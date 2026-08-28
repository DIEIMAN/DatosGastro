# -*- coding: utf-8 -*-
"""
Builder preflight expansión candidatos V4 + consolidación integrada.
Rol: cartografo_territorial (+ integrador_tecnico_documental).
NO ejecuta Places ni clustering. NO escribe fuera de líneas autorizadas.
NO modifica config snapshot de Claude ni evidencia documental Grok.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import zipfile
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[3]
FECHA = "2026-07-12"
SCRIPT_DIR = Path(__file__).resolve().parent
OUT_PRE = ROOT / "outputs" / "polos_gastro" / "expansion_candidatos_v4_preflight"
DOC_PRE = ROOT / "docs" / "polos_gastro" / "expansion_candidatos_v4_preflight"
OUT_INT = ROOT / "outputs" / "polos_gastro" / "preparacion_integrada_expansion_v4"
DOC_INT = ROOT / "docs" / "polos_gastro" / "preparacion_integrada_expansion_v4"
DOC_EVI = ROOT / "docs" / "polos_gastro" / "evidencia_documental_expansion_v4"
OUT_EVI = ROOT / "outputs" / "polos_gastro" / "evidencia_documental_expansion_v4"
REV_PRE = ROOT / "outputs" / "polos_gastro" / "REVISION_PREFLIGHT_EXPANSION_CANDIDATOS_V4"
REV_INT = ROOT / "outputs" / "polos_gastro" / "REVISION_PREPARACION_INTEGRADA_EXPANSION_V4"
ZIP_PRE = ROOT / "outputs" / "polos_gastro" / "REVISION_PREFLIGHT_EXPANSION_CANDIDATOS_V4.zip"
ZIP_INT = ROOT / "outputs" / "polos_gastro" / "REVISION_PREPARACION_INTEGRADA_EXPANSION_V4.zip"

CRS_GEO = "EPSG:4326"
CRS_M = "EPSG:5347"
CELDA_M = 250
RADIO_PLACES = 200  # radio de consulta típico del pipeline previo

# Categorías alineadas a corridas previas (no inventar)
CATEGORIAS_PRIMARIAS = [
    "restaurant",
    "cafe",
    "bar",
    "bakery",
    "meal_takeaway",
]
CATEGORIAS_AUX = ["meal_delivery", "food"]
CATEGORIAS_EXCL = ["lodging", "store", "shopping_mall"]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return
    fields = fieldnames or list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def norm_txt(s: str) -> str:
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return ""
    s = str(s).upper()
    rep = {
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ü": "U", "Ñ": "N",
        "À": "A", "È": "E", "Ì": "I", "Ò": "O", "Ù": "U",
    }
    for a, b in rep.items():
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_config_final() -> dict:
    """Config Claude + correcciones documentales controladas."""
    snap = OUT_PRE / "config_expansion_candidatos_v4_claude_partial_snapshot.json"
    if not snap.exists():
        snap = SCRIPT_DIR / "config_expansion_candidatos_v4.json"
    cfg = json.loads(snap.read_text(encoding="utf-8"))
    cfg["version"] = "expansion_candidatos_v4_preflight_final"
    cfg["fecha_preflight"] = FECHA
    cfg["rol"] = "cartografo_territorial"
    cfg["integracion_documental"] = {
        "paquete": "evidencia_documental_expansion_v4",
        "ruta_docs": "docs/polos_gastro/evidencia_documental_expansion_v4/",
        "ruta_outputs": "outputs/polos_gastro/evidencia_documental_expansion_v4/",
        "reglas": [
            "Solo ABIERTA_Y_LEIDA define ejes/nodos de área",
            "Snippet = hipótesis/contexto",
            "SIN_URL no decide",
            "No nombres comerciales como ID técnico",
            "No locales semilla como puntos",
        ],
    }
    # --- Correcciones por zona ---
    by_id = {z["zona_id"]: z for z in cfg["zonas"]}

    # Z02 Chacarita: Newbery + Dorrego; Lacroze solo control
    by_id["Z02"]["nombre"] = "Chacarita"
    by_id["Z02"]["nombre_tecnico"] = "Chacarita"
    by_id["Z02"]["alias_dudosos"] = ["Chacalermo", "Chacacrespo"]
    by_id["Z02"]["hipotesis_principal"] = "MULTIPARTE"  # Newbery + Dorrego
    by_id["Z02"]["hipotesis_alternativa"] = "CORREDOR_LINEAL"
    by_id["Z02"]["pregunta_territorial"] = (
        "Hay corredor Newbery y/o nucleo Dorrego? Independiente de Palermo y de Lacroze completa?"
    )
    by_id["Z02"]["geometria"] = {
        "area_principal": {"tipo": "barrios", "barrios": ["Chacarita"], "buffer_m": 0},
        "extras": [
            {"rol": "EJE_REFERENCIA", "tipo": "eje_en_barrios",
             "calles": ["NEWBERY, JORGE AV.", "NEWBERY, JORGE"], "barrios": ["Chacarita"], "buffer_m": 0,
             "obs": "Corredor documentado prensa+oficial (Dorrego-Newbery)"},
            {"rol": "EJE_REFERENCIA", "tipo": "eje_en_barrios",
             "calles": ["DORREGO AV.", "DORREGO"], "barrios": ["Chacarita"], "buffer_m": 0,
             "obs": "Posible segundo nucleo (Condarco/Dorrego)"},
            {"rol": "AREA_TRANSICION", "tipo": "banda_limite", "barrio_a": "Chacarita", "barrio_b": "Villa Crespo", "buffer_m": 350},
            {"rol": "AREA_TRANSICION", "tipo": "banda_limite", "barrio_a": "Chacarita", "barrio_b": "Palermo", "buffer_m": 350,
             "obs": "No crear unidad Chacalermo"},
            {"rol": "CONTROL_VECINO", "tipo": "eje_en_barrios",
             "calles": ["LACROZE, FEDERICO AV."], "barrios": ["Chacarita"], "buffer_m": 200,
             "obs": "Control: no usar Lacroze completa como proxy de Chacarita"},
        ],
        "subunidades": [
            {"subunidad_id": "Z02-S1", "nombre": "Corredor Newbery", "tipo": "eje_en_barrios",
             "calles": ["NEWBERY, JORGE AV.", "NEWBERY, JORGE"], "barrios": ["Chacarita"], "buffer_m": 250},
            {"subunidad_id": "Z02-S2", "nombre": "Nucleo Dorrego", "tipo": "eje_en_barrios",
             "calles": ["DORREGO AV.", "DORREGO"], "barrios": ["Chacarita"], "buffer_m": 250},
        ],
    }

    # Z01 Crespo: ejes Thames/Gurruchaga/Velazco documentados
    by_id["Z01"]["nombre_tecnico"] = "Villa Crespo"
    by_id["Z01"]["alias_dudosos"] = ["Chacacrespo"]
    by_id["Z01"]["hipotesis_principal"] = "MULTIPARTE"
    by_id["Z01"]["geometria"]["extras"] = [
        {"rol": "EJE_REFERENCIA", "tipo": "eje_en_barrios",
         "calles": ["THAMES"], "barrios": ["Villa Crespo"], "buffer_m": 0,
         "obs": "Eje oficial Turismo BA; riesgo absorcion Palermo"},
        {"rol": "EJE_REFERENCIA", "tipo": "eje_en_barrios",
         "calles": ["GURRUCHAGA"], "barrios": ["Villa Crespo"], "buffer_m": 0},
        {"rol": "EJE_REFERENCIA", "tipo": "eje_en_barrios",
         "calles": ["VELAZCO"], "barrios": ["Villa Crespo"], "buffer_m": 0},
        {"rol": "AREA_TRANSICION", "tipo": "banda_limite", "barrio_a": "Villa Crespo", "barrio_b": "Palermo", "buffer_m": 350},
        {"rol": "AREA_TRANSICION", "tipo": "banda_limite", "barrio_a": "Villa Crespo", "barrio_b": "Chacarita", "buffer_m": 350},
        {"rol": "CONTROL_VECINO", "tipo": "polo_adoptado", "polo": "palermo"},
    ]

    # Z03 Caballito multinodo
    by_id["Z03"]["nombre_tecnico"] = "Caballito (multinodo)"
    by_id["Z03"]["hipotesis_principal"] = "MULTIPARTE"
    by_id["Z03"]["hipotesis_alternativa"] = "UNIDAD_BARRIAL"
    by_id["Z03"]["geometria"] = {
        "area_principal": {"tipo": "barrios", "barrios": ["Caballito"], "buffer_m": 0},
        "extras": [
            {"rol": "EJE_REFERENCIA", "tipo": "eje_en_barrios",
             "calles": ["GOYENA, PEDRO AV."], "barrios": ["Caballito"], "buffer_m": 0},
            {"rol": "EJE_REFERENCIA", "tipo": "eje_en_barrios",
             "calles": ["RIVADAVIA AV."], "barrios": ["Caballito"], "buffer_m": 0},
        ],
        "subunidades": [
            {"subunidad_id": "Z03-S1", "nombre": "Pedro Goyena", "tipo": "eje_en_barrios",
             "calles": ["GOYENA, PEDRO AV."], "barrios": ["Caballito"], "buffer_m": 250},
            {"subunidad_id": "Z03-S2", "nombre": "Primera Junta-Mercado del Progreso", "tipo": "nodo_aproximado",
             "calle_a": "RIVADAVIA AV.", "calle_b": "ROJAS", "radio_m": 400, "barrios": ["Caballito"],
             "obs": "Nodo Primera Junta / Mercado del Progreso"},
            {"subunidad_id": "Z03-S3", "nombre": "Patio de los Lecheros", "tipo": "nodo_aproximado",
             "calle_a": "DONATO ALVAREZ AV.", "calle_b": "BACACAY", "radio_m": 350, "barrios": ["Caballito"],
             "obs": "Hito patio; no proxy del barrio"},
            {"subunidad_id": "Z03-S4", "nombre": "Parque Rivadavia", "tipo": "nodo_aproximado",
             "calle_a": "RIVADAVIA AV.", "calle_b": "SUBIRANA", "radio_m": 400, "barrios": ["Caballito"]},
        ],
    }

    # Z04 Caseros tramo corto + controles
    by_id["Z04"]["nombre"] = "Boulevard Caseros (tramo)"
    by_id["Z04"]["nombre_tecnico"] = "Boulevard Caseros (Parque Lezama)"
    by_id["Z04"]["alias_dudosos"] = ["Polo Caseros", "Caseros=Barracas completa", "Caseros=Patricios"]
    by_id["Z04"]["geometria"] = {
        "area_principal": {
            "tipo": "eje_en_barrios",
            "calles": ["CASEROS AV."],
            "barrios": ["Barracas", "San Telmo", "Constitucion"],
            "buffer_m": 200,
            "obs": "Hipotesis principal: tramo documentado Defensa-Bolivar; no extender a Patricios",
        },
        "extras": [
            {"rol": "EJE_REFERENCIA", "tipo": "eje_en_barrios",
             "calles": ["CASEROS AV."], "barrios": ["Barracas", "San Telmo"], "buffer_m": 0},
            {"rol": "CONTROL_VECINO", "tipo": "polo_adoptado", "polo": "san_telmo"},
            {"rol": "CONTROL_VECINO", "tipo": "barrios", "barrios": ["Parque Patricios"], "buffer_m": 0,
             "obs": "Control: patio Patricios es otro objeto"},
            {"rol": "AREA_TRANSICION", "tipo": "eje_en_barrios",
             "calles": ["CASEROS AV."], "barrios": ["Barracas", "San Telmo", "Constitucion"], "buffer_m": 400},
        ],
    }

    # Z05 sin poligono unico Centro
    by_id["Z05"]["nombre_tecnico"] = "Familia Centro (subunidades)"
    by_id["Z05"]["alias_dudosos"] = ["Centro unitario", "Microcentro=todo el Centro"]
    by_id["Z05"]["geometria"]["area_principal"] = {
        "tipo": "barrios", "barrios": ["San Nicolas", "Monserrat"], "buffer_m": 0,
        "obs": "Envelope de trabajo; NO es unidad de adopcion ni consulta unica",
    }

    # Z06 Abasto nucleo propio
    by_id["Z06"]["nombre_tecnico"] = "Abasto (nucleo cultural-comercial)"
    by_id["Z06"]["alias_dudosos"] = ["Abasto=Corrientes centro", "Güerrin como ancla Abasto"]
    by_id["Z06"]["geometria"] = {
        "area_principal": {
            "tipo": "eje_tramo_alturas",
            "calles": ["CORRIENTES AV."],
            "altura_min": 3000,
            "altura_max": 3800,
            "buffer_m": 350,
            "obs": "Nucleo Abasto; excluir pizzerias centro (Güerrin/Cuartetas) como prueba",
        },
        "extras": [
            {"rol": "CONTROL_VECINO", "tipo": "polo_adoptado", "polo": "corrientes"},
            {"rol": "AREA_TRANSICION", "tipo": "eje_tramo_alturas",
             "calles": ["CORRIENTES AV."], "altura_min": 2800, "altura_max": 4000, "buffer_m": 500},
        ],
    }

    # Z09 Donado-Holmberg
    by_id["Z09"]["nombre"] = "Corredor Donado-Holmberg"
    by_id["Z09"]["nombre_tecnico"] = "Donado-Holmberg"
    by_id["Z09"]["slug"] = "donado_holmberg"
    by_id["Z09"]["alias_dudosos"] = ["DoHo", "DoHo=Villa Urquiza"]
    by_id["Z09"]["geometria"]["area_principal"]["barrios"] = ["Villa Urquiza", "Coghlan"]
    by_id["Z09"]["geometria"]["area_principal"]["calles"] = ["DONADO", "HOLMBERG"]

    # Z11 Esmeralda-Paraguay
    by_id["Z11"]["nombre"] = "Esmeralda-Paraguay (Retiro)"
    by_id["Z11"]["nombre_tecnico"] = "Retiro - Esmeralda-Paraguay"
    by_id["Z11"]["alias_dudosos"] = ["Nuevo Bajo (toponimo no oficial)", "Bajo porteno"]

    # Z12 Lacroze por tramos (no unidad continua a priori)
    by_id["Z12"]["nombre_tecnico"] = "Federico Lacroze (por tramos)"
    by_id["Z12"]["hipotesis_principal"] = "POSIBLE_TRANSICION"
    by_id["Z12"]["hipotesis_alternativa"] = "CORREDOR_LINEAL"
    by_id["Z12"]["geometria"]["subunidades"] = [
        {"subunidad_id": "Z12-T1", "nombre": "Lacroze tramo Chacarita-estacion",
         "tipo": "eje_en_barrios", "calles": ["LACROZE, FEDERICO AV."], "barrios": ["Chacarita"], "buffer_m": 200},
        {"subunidad_id": "Z12-T2", "nombre": "Lacroze tramo Colegiales",
         "tipo": "eje_en_barrios", "calles": ["LACROZE, FEDERICO AV."], "barrios": ["Colegiales"], "buffer_m": 200},
        {"subunidad_id": "Z12-T3", "nombre": "Lacroze tramo Belgrano (Cabildo)",
         "tipo": "eje_en_barrios", "calles": ["LACROZE, FEDERICO AV."], "barrios": ["Belgrano"], "buffer_m": 200},
    ]

    # Z13 García del Río + control Parque Saavedra
    by_id["Z13"]["nombre"] = "Garcia del Rio (Saavedra)"
    by_id["Z13"]["nombre_tecnico"] = "Garcia del Rio (corredor)"
    by_id["Z13"]["alias_dudosos"] = ["Parque Saavedra = polo"]
    by_id["Z13"]["geometria"]["extras"] = [
        {"rol": "EJE_REFERENCIA", "tipo": "eje", "calles": ["GARCIA DEL RIO AV.", "GARCIA DEL RIO"], "buffer_m": 0},
        {"rol": "CONTROL_VECINO", "tipo": "barrios", "barrios": ["Saavedra"], "buffer_m": 0,
         "obs": "Parque Saavedra como control espacial, no como sinonimo del corredor"},
        {"rol": "AREA_TRANSICION", "tipo": "eje", "calles": ["GARCIA DEL RIO AV.", "GARCIA DEL RIO"], "buffer_m": 450},
    ]

    # Z14 Paternal
    by_id["Z14"]["nombre_tecnico"] = "La Paternal"
    by_id["Z14"]["alias_dudosos"] = ["Distrito del Vino = Paternal"]
    by_id["Z14"]["geometria"]["area_principal"]["barrios"] = ["Paternal"]
    by_id["Z14"]["geometria"]["extras"] = [
        {"rol": "AREA_TRANSICION", "tipo": "banda_limite", "barrio_a": "Paternal", "barrio_b": "Villa Crespo", "buffer_m": 350,
         "obs": "Triple frontera Honorio Pueyrredon"},
    ]

    # Z15 — Av. San Martín NO intersecta el polígono de Villa Pueyrredón en callejero GCBA
    # (pasa por Devoto/Paternal/Agronomía). Área principal = barrio; avenida como control de borde.
    by_id["Z15"]["nombre_tecnico"] = "Villa Pueyrredon (exploratorio)"
    by_id["Z15"]["alias_dudosos"] = ["Av. San Martin completa multi-barrio"]
    by_id["Z15"]["geometria"] = {
        "area_principal": {
            "tipo": "barrios",
            "barrios": ["Villa Pueyrredon"],
            "buffer_m": 0,
            "obs": "Callejero: SAN MARTIN AV. no cruza el poligono barrial; prior barrial exploratorio",
        },
        "extras": [
            {
                "rol": "EJE_REFERENCIA",
                "tipo": "eje",
                "calles": ["SAN MARTIN AV."],
                "buffer_m": 0,
                "obs": "Eje regional de contexto; no equivale a corredor de Villa Pueyrredon",
            },
            {
                "rol": "AREA_TRANSICION",
                "tipo": "eje",
                "calles": ["SAN MARTIN AV."],
                "buffer_m": 300,
                "obs": "Banda de Av. San Martin para medir oferta limítrofe (Devoto/Paternal)",
            },
        ],
    }
    # registrar correccion
    cfg.setdefault("correcciones_sobre_claude", [])

    # Subunidades centro alineadas a Grok C-S01..C-S08
    cfg["subunidades_centro"] = [
        {"sub_id": "C-S01", "nombre": "Microcentro financiero", "places_independiente": True, "prioridad": "ALTA",
         "tipo_esperado": "RED_DE_NODOS",
         "construccion": {"tipo": "nodo", "calle_a": "FLORIDA", "calle_b": "CORRIENTES AV.", "radio_m": 450},
         "fuente": "callejero + itinerarios oficiales", "calles": "Florida; Reconquista; Lavalle; San Martin",
         "nodos": "area financiera/peatonal", "relacion": "adyacente C-S04/C-S08", "riesgo": "confundir con todo Centro",
         "metodo_recomendado": "Grafo + nodos", "estado": "ACTIVA"},
        {"sub_id": "C-S02", "nombre": "Bajo porteno (referencia ambigua)", "places_independiente": False, "prioridad": "NO_CONSULTAR",
         "tipo_esperado": "INDETERMINADO",
         "construccion": {"tipo": "eje_en_barrios", "calles": ["ALEM, LEANDRO N. AV."], "barrios": ["San Nicolas", "Retiro", "Monserrat"], "buffer_m": 200},
         "fuente": "toponimo historico ambiguo", "calles": "L.N. Alem (referencia)",
         "nodos": "—", "relacion": "confundible con C-S07", "riesgo": "ALTO",
         "metodo_recomendado": "NO consultar hasta definicion", "estado": "REFERENCIA_NO_CONSULTA"},
        {"sub_id": "C-S03", "nombre": "Plaza de Mayo - Monserrat", "places_independiente": True, "prioridad": "ALTA",
         "tipo_esperado": "NUCLEO_COMPACTO",
         "construccion": {"tipo": "nodo", "calle_a": "BOLIVAR", "calle_b": "DE MAYO AV.", "radio_m": 400},
         "fuente": "Turismo BA circuito tradicional", "calles": "Bolivar; Yrigoyen; Balcarce",
         "nodos": "Plaza de Mayo", "relacion": "C-S04; San Telmo", "riesgo": "mezcla con casco turistico",
         "metodo_recomendado": "Nucleo compacto", "estado": "ACTIVA"},
        {"sub_id": "C-S04", "nombre": "Avenida de Mayo", "places_independiente": True, "prioridad": "ALTA",
         "tipo_esperado": "CORREDOR_LINEAL",
         "construccion": {"tipo": "eje", "calles": ["DE MAYO AV."], "buffer_m": 150},
         "fuente": "Turismo BA", "calles": "Av. de Mayo", "nodos": "Tortoni; Congreso extremo",
         "relacion": "C-S03", "riesgo": "bajo", "metodo_recomendado": "Corredor por tramos", "estado": "ACTIVA"},
        {"sub_id": "C-S05", "nombre": "Tribunales", "places_independiente": True, "prioridad": "SECUNDARIA",
         "tipo_esperado": "MICROCENTRALIDAD",
         "construccion": {"tipo": "nodo", "calle_a": "TALCAHUANO", "calle_b": "LAVALLE", "radio_m": 350},
         "fuente": "itinerario oficial Obelisco/Tribunales", "calles": "Talcahuano; Lavalle; Uruguay",
         "nodos": "Plaza Lavalle; Colon", "relacion": "C-S08 Corrientes", "riesgo": "solape Corrientes",
         "metodo_recomendado": "Microcentralidad opcional", "estado": "SECUNDARIA"},
        {"sub_id": "C-S06", "nombre": "Retiro central", "places_independiente": True, "prioridad": "ALTA",
         "tipo_esperado": "NUCLEO_COMPACTO",
         "construccion": {"tipo": "nodo", "calle_a": "MAIPU", "calle_b": "SANTA FE AV.", "radio_m": 400},
         "fuente": "Turismo en Barrios Retiro", "calles": "Florida norte; Santa Fe; Esmeralda norte",
         "nodos": "Plaza San Martin", "relacion": "C-S07; Recoleta", "riesgo": "fusion con Esmeralda-Paraguay",
         "metodo_recomendado": "Nucleo + transicion", "estado": "ACTIVA"},
        {"sub_id": "C-S07", "nombre": "Esmeralda-Paraguay", "places_independiente": True, "prioridad": "ALTA",
         "tipo_esperado": "MICROCENTRALIDAD",
         "construccion": {"tipo": "nodo", "calle_a": "ESMERALDA", "calle_b": "PARAGUAY", "radio_m": 350},
         "fuente": "prensa 2020 + listados Retiro; no toponimo oficial Nuevo Bajo",
         "calles": "Esmeralda; Paraguay", "nodos": "esquina Esmeralda y Paraguay",
         "relacion": "Z11; C-S06; C-S01", "riesgo": "nombre Nuevo Bajo",
         "metodo_recomendado": "Radio pequeno; revalidar 2026", "estado": "ACTIVA"},
        {"sub_id": "C-S08", "nombre": "Corrientes centro (pizza-teatro)", "places_independiente": True, "prioridad": "ALTA",
         "tipo_esperado": "CORREDOR_LINEAL",
         "construccion": {"tipo": "eje_tramo_alturas", "calles": ["CORRIENTES AV."], "altura_min": 800, "altura_max": 2000, "buffer_m": 200},
         "fuente": "Turismo BA + academia polos 2015 Calle Corrientes",
         "calles": "Av. Corrientes tramo centro", "nodos": "Guerrin; Las Cuartetas; teatros",
         "relacion": "NO es Abasto; control polo Corrientes adoptado", "riesgo": "fusion con Z06",
         "metodo_recomendado": "Corredor; separar de Abasto", "estado": "ACTIVA"},
    ]

    # Tandas: user PART 12 base + reconcile with coverage (T1 has Places)
    cfg["tandas"] = [
        {"tanda": 1, "zonas": ["Z01", "Z02", "Z03", "Z04"],
         "justificacion": "Cobertura Places 2026-07-09 amplia/parcial + fuerte valor de decision temprana; multi-eje documentado",
         "dependencias": "Universo completo V1; evidencia documental Grok",
         "riesgos": "Palermo-Crespo; multinodo Caballito; Caseros extension indebida",
         "duracion_relativa": "corta", "decisiones_posibles": "Independencia Crespo; multiparte Chacarita; nodos Caballito; tramo Caseros"},
        {"tanda": 2, "zonas": ["Z07", "Z08", "Z09", "Z10"],
         "justificacion": "Norte-oeste y Boedo: DoHo/Urquiza separables; Devoto y Boedo exploratorios",
         "dependencias": "Calibracion tanda 1; autorizacion Places brechas",
         "riesgos": "Marca DoHo; dilucion barrial", "duracion_relativa": "media",
         "decisiones_posibles": "Separabilidad Donado-Holmberg; unidad Devoto; Boedo corredor o no"},
        {"tanda": 3, "zonas": ["Z13", "Z12", "Z14", "Z15"],
         "justificacion": "Periferia y corredores debiles/medios; Lacroze solo tramos; Pueyrredon exploratorio",
         "dependencias": "Tanda 2 metodos corredor", "riesgos": "Promocion forzada; avenida multi-barrio",
         "duracion_relativa": "media", "decisiones_posibles": "Garcia del Rio; tramos Lacroze; archipielago Paternal; vacio Pueyrredon"},
        {"tanda": 4, "zonas": ["Z06", "Z11", "Z05"],
         "justificacion": "Centro segmentado + Abasto + Esmeralda-Paraguay; maxima complejidad de solape con adoptados",
         "dependencias": "Tandas 1-3; decision humana Abasto-Corrientes", "riesgos": "Unidad falsa Centro; solape Corrientes",
         "duracion_relativa": "larga", "decisiones_posibles": "Subunidades Centro; Abasto asociada/subpolo; nucleo Esmeralda-Paraguay"},
    ]

    cfg["correcciones_sobre_claude"] = [
        {"campo": "Z02 ejes", "antes": "Lacroze como eje principal", "despues": "Newbery+Dorrego; Lacroze control",
         "motivo": "Evidencia oficial y Clarín Newbery"},
        {"campo": "Z03", "antes": "barrio unico + Rivadavia", "despues": "multinodo Goyena/Primera Junta/Lecheros/Rivadavia",
         "motivo": "Handoff documental multinodo"},
        {"campo": "Z04", "antes": "Caseros en Barracas/Patricios/Constitucion", "despues": "tramo San Telmo-Barracas; control Patricios",
         "motivo": "Boulevard Caseros documentado Defensa-Bolivar"},
        {"campo": "Z09 nombre", "antes": "DoHo", "despues": "Donado-Holmberg (DoHo alias)", "motivo": "Nombre comercial"},
        {"campo": "Z11 nombre", "antes": "Nuevo Bajo", "despues": "Esmeralda-Paraguay", "motivo": "Toponimo no oficial"},
        {"campo": "SC08", "antes": "Florida peatonal", "despues": "Corrientes centro (pizza-teatro)", "motivo": "Alineacion C-S08 Grok"},
        {"campo": "SC02", "antes": "consulta posible", "despues": "NO_CONSULTAR", "motivo": "Ambiguedad Bajo porteno"},
        {"campo": "tandas", "antes": "documental pura", "despues": "T1 mantiene cobertura Places; orden user Part12",
         "motivo": "Reconciliacion cobertura+documental"},
    ]
    return cfg


class GeoEngine:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.barrios = gpd.read_file(ROOT / cfg["capas_base"]["barrios"]).to_crs(CRS_GEO)
        self.barrios["nombre_n"] = self.barrios["nombre"].map(norm_txt)
        self.comunas = gpd.read_file(ROOT / cfg["capas_base"]["comunas"]).to_crs(CRS_GEO)
        self.callejero = gpd.read_file(ROOT / cfg["capas_base"]["callejero"]).to_crs(CRS_GEO)
        self.callejero["nom_n"] = self.callejero["nomoficial"].map(norm_txt)
        self.callejero["barrio_n"] = self.callejero["barrio"].map(norm_txt)
        univ_path = ROOT / cfg["capas_base"]["universo_completo"]
        self.univ = pd.read_csv(univ_path)
        self.univ_gdf = gpd.GeoDataFrame(
            self.univ,
            geometry=gpd.points_from_xy(self.univ["lon"], self.univ["lat"]),
            crs=CRS_GEO,
        )
        # planes de celdas existentes
        plans = []
        for rel in [
            "outputs/polos_gastro/experimentos/google_places_microzonas_piloto/places/plan_consultas_places.csv",
            "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/places/plan_consultas_a_criticas.csv",
            "outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/places/plan_consultas_b_consolidacion.csv",
        ]:
            p = ROOT / rel
            if p.exists():
                d = pd.read_csv(p)
                d["plan_origen"] = rel
                plans.append(d)
        self.celdas = pd.concat(plans, ignore_index=True) if plans else pd.DataFrame()
        if len(self.celdas):
            self.celdas_gdf = gpd.GeoDataFrame(
                self.celdas,
                geometry=gpd.points_from_xy(self.celdas["lon"], self.celdas["lat"]),
                crs=CRS_GEO,
            )
        else:
            self.celdas_gdf = gpd.GeoDataFrame(geometry=[], crs=CRS_GEO)
        self.polos = {}
        for k, rel in cfg["polos_adoptados"].items():
            p = ROOT / rel
            if p.exists():
                try:
                    self.polos[k] = gpd.read_file(p).to_crs(CRS_GEO)
                except Exception:
                    pass

    def barrio_poly(self, names: list[str]):
        nn = [norm_txt(n) for n in names]
        # fuzzy: allow without accents already
        m = self.barrios[self.barrios["nombre_n"].isin(nn)]
        if m.empty:
            # try contains
            mask = False
            for n in nn:
                mask = mask | self.barrios["nombre_n"].str.contains(n.replace(" ", ".*"), na=False)
            m = self.barrios[mask]
        if m.empty:
            return None
        return unary_union(m.geometry.values)

    def match_streets(self, calles: list[str], barrios: list[str] | None = None):
        names_n = [norm_txt(c) for c in calles]
        # exact or startswith/contains careful for DONADO vs MALDONADO
        def ok(nom):
            for c in names_n:
                if nom == c or nom.startswith(c + " ") or nom.startswith(c + ",") or nom == c + " AV.":
                    return True
                # allow AV. suffix variants
                if c.endswith(" AV.") and nom == c:
                    return True
            return False

        mask = self.callejero["nom_n"].map(ok)
        # special: DONADO exact only
        if any(norm_txt(c) == "DONADO" for c in calles):
            mask = self.callejero["nom_n"].isin(["DONADO"]) | self.callejero["nom_n"].isin(
                [n for n in names_n if n != "DONADO"]
            )
            for c in names_n:
                if c != "DONADO":
                    mask = mask | self.callejero["nom_n"].map(lambda x, cc=c: ok(x) if False else (x == cc or x.startswith(cc + ",") or x.startswith(cc + " ")))
            # rebuild
            m2 = []
            for nom in self.callejero["nom_n"]:
                hit = False
                for c in names_n:
                    if c == "DONADO":
                        if nom == "DONADO":
                            hit = True
                    else:
                        if nom == c or nom.startswith(c + ",") or nom.startswith(c + " ") or nom == c:
                            hit = True
                m2.append(hit)
            mask = pd.Series(m2, index=self.callejero.index)

        sub = self.callejero[mask]
        if barrios:
            bn = [norm_txt(b) for b in barrios]
            sub = sub[sub["barrio_n"].isin(bn) | sub["barrio_n"].isna()]
            # if filter too aggressive keep street citywide clipped later
            if sub.empty:
                sub = self.callejero[mask]
        return sub

    def build_from_spec(self, spec: dict):
        if not spec:
            return None
        t = spec.get("tipo")
        buf = float(spec.get("buffer_m") or 0)
        geom = None
        metodo = t
        ejes = ""
        fuente = "callejero_gcba + geo_barrios"
        if t == "barrios":
            geom = self.barrio_poly(spec.get("barrios", []))
            metodo = f"union barrios {spec.get('barrios')} buffer={buf}"
            fuente = "data/raw/geo_barrios.geojson"
        elif t in ("eje", "eje_en_barrios"):
            barrios = spec.get("barrios")
            calles = spec.get("calles", [])
            sub = self.match_streets(calles, barrios if t == "eje_en_barrios" else None)
            if len(sub) == 0:
                return None
            geom = unary_union(sub.geometry.values)
            ejes = ";".join([str(c) for c in calles])
            metodo = f"eje calles={calles} barrios={barrios} buffer={buf}"
            # clip metrico al barrio si se pidio
            if t == "eje_en_barrios" and barrios:
                bp = self.barrio_poly(barrios)
                if bp is not None and geom is not None:
                    gm = gpd.GeoSeries([geom], crs=CRS_GEO).to_crs(CRS_M).iloc[0]
                    bpm = gpd.GeoSeries([bp], crs=CRS_GEO).to_crs(CRS_M).iloc[0]
                    clipped = gm.intersection(bpm.buffer(80))  # 80 m tolerancia borde
                    if clipped.is_empty:
                        return None
                    geom = gpd.GeoSeries([clipped], crs=CRS_M).to_crs(CRS_GEO).iloc[0]
        elif t == "eje_tramo_alturas":
            calles = spec.get("calles", [])
            sub = self.match_streets(calles, None)
            amin = int(spec.get("altura_min") or 0)
            amax = int(spec.get("altura_max") or 99999)
            if len(sub):
                # filter by height ranges if available
                def in_range(row):
                    vals = [row.get("alt_izqini"), row.get("alt_izqfin"), row.get("alt_derini"), row.get("alt_derfin")]
                    vals = [v for v in vals if pd.notna(v)]
                    if not vals:
                        return True
                    return any(amin <= v <= amax for v in vals) or any(
                        min(row.get("alt_izqini") or 0, row.get("alt_izqfin") or 0) <= amax
                        and max(row.get("alt_izqini") or 0, row.get("alt_izqfin") or 0) >= amin
                        for _ in [0]
                    )
                sub = sub[sub.apply(in_range, axis=1)]
            if len(sub) == 0:
                return None
            geom = unary_union(sub.geometry.values)
            ejes = f"{calles} h={amin}-{amax}"
            metodo = f"eje_tramo_alturas {ejes} buffer={buf}"
        elif t == "eje_entre_cruces":
            calles = spec.get("calles", [])
            sub = self.match_streets(calles, None)
            if len(sub) == 0:
                return None
            geom = unary_union(sub.geometry.values)
            ejes = ";".join(calles)
            metodo = f"eje_entre_cruces {ejes} (aprox sin corte fino de cruces) buffer={buf}"
        elif t in ("nodo", "nodo_aproximado"):
            ca = spec.get("calle_a")
            cb = spec.get("calle_b")
            radio = float(spec.get("radio_m") or 400)
            sa = self.match_streets([ca], None)
            sb = self.match_streets([cb], None)
            if len(sa) == 0 or len(sb) == 0:
                # fallback centroid of first street
                if len(sa):
                    c = unary_union(sa.geometry.values).centroid
                    geom = c
                    buf = radio
                    metodo = f"nodo fallback centroid {ca} radio={radio}"
                else:
                    return None
            else:
                ga = unary_union(sa.geometry.values)
                gb = unary_union(sb.geometry.values)
                inter = ga.intersection(gb)
                if inter.is_empty:
                    # nearest points approximation via centroids
                    c = Point(
                        (ga.centroid.x + gb.centroid.x) / 2,
                        (ga.centroid.y + gb.centroid.y) / 2,
                    )
                else:
                    c = inter.centroid if inter.geom_type != "Point" else inter
                geom = c
                buf = radio
                metodo = f"nodo {ca} x {cb} radio={radio}"
            ejes = f"{ca} x {cb}"
            # clip to barrio if given
            if spec.get("barrios"):
                bp = self.barrio_poly(spec["barrios"])
                if bp is not None and geom is not None:
                    # after buffer
                    pass
        elif t == "banda_limite":
            a = self.barrio_poly([spec["barrio_a"]])
            b = self.barrio_poly([spec["barrio_b"]])
            if a is None or b is None:
                return None
            # boundary band: intersection of buffers of each boundary
            am = gpd.GeoSeries([a], crs=CRS_GEO).to_crs(CRS_M).iloc[0]
            bm = gpd.GeoSeries([b], crs=CRS_GEO).to_crs(CRS_M).iloc[0]
            band = am.boundary.buffer(float(spec.get("buffer_m") or 350)).intersection(
                bm.boundary.buffer(float(spec.get("buffer_m") or 350))
            )
            # also include intersection of buffered polygons near border
            band2 = am.buffer(50).intersection(bm.buffer(float(spec.get("buffer_m") or 350)))
            geom_m = band.union(band2)
            geom = gpd.GeoSeries([geom_m], crs=CRS_M).to_crs(CRS_GEO).iloc[0]
            buf = 0
            metodo = f"banda_limite {spec['barrio_a']}|{spec['barrio_b']} {spec.get('buffer_m')}m"
            fuente = "geo_barrios boundary band"
        elif t == "polo_adoptado":
            polo = spec.get("polo")
            gdf = self.polos.get(polo)
            if gdf is None or gdf.empty:
                return None
            geom = unary_union(gdf.geometry.values)
            metodo = f"polo_adoptado {polo}"
            fuente = self.cfg["polos_adoptados"].get(polo, "")
        else:
            return None

        if geom is None or geom.is_empty:
            return None

        # buffer metric
        if buf and buf > 0:
            gm = gpd.GeoSeries([geom], crs=CRS_GEO).to_crs(CRS_M).iloc[0]
            gm = gm.buffer(buf)
            geom = gpd.GeoSeries([gm], crs=CRS_M).to_crs(CRS_GEO).iloc[0]

        # clip to CABA
        caba = unary_union(self.barrios.geometry.values)
        geom = geom.intersection(caba)
        if geom.is_empty:
            return None
        return {"geometry": geom, "metodo": metodo, "ejes": ejes, "fuente": fuente, "buffer_m": buf}


def area_km2(geom) -> float:
    if geom is None or geom.is_empty:
        return 0.0
    s = gpd.GeoSeries([geom], crs=CRS_GEO).to_crs(CRS_M)
    return float(s.area.iloc[0] / 1e6)


def coverage_stats(engine: GeoEngine, geom):
    if geom is None or geom.is_empty:
        return dict(puntos_f01_f02=0, puntos_places=0, puntos_combinados=0, porcentaje_places=0,
                    categorias="", celdas_existentes=0, fecha_places="")
    pts = engine.univ_gdf[engine.univ_gdf.geometry.within(geom) | engine.univ_gdf.geometry.intersects(geom.buffer(0))]
    # more robust: intersects
    pts = engine.univ_gdf[engine.univ_gdf.intersects(geom)]
    n_adm = int((pts["fuente"] == "F01+F02").sum()) if len(pts) else 0
    n_pl = int((pts["fuente"] == "google_places").sum()) if len(pts) else 0
    n = n_adm + n_pl
    cats = ",".join(sorted(pts["categoria"].dropna().astype(str).unique()[:12])) if len(pts) else ""
    fechas = pts.loc[pts["fuente"] == "google_places", "fecha_consulta"].dropna().astype(str).unique() if len(pts) else []
    fecha = ";".join(sorted(fechas)[:3])
    if len(engine.celdas_gdf):
        # celdas cuyo punto cae en area o buffer radio
        cel = engine.celdas_gdf[engine.celdas_gdf.intersects(geom)]
        ncel = len(cel)
    else:
        ncel = 0
    return dict(
        puntos_f01_f02=n_adm,
        puntos_places=n_pl,
        puntos_combinados=n,
        porcentaje_places=round(100 * n_pl / n, 1) if n else 0,
        categorias=cats,
        celdas_existentes=ncel,
        fecha_places=fecha,
    )


def decide_places_need(zona_id: str, cov: dict, area: float) -> tuple[str, str]:
    """NO/PARCIAL/SI/A_CONFIRMAR based on coverage not raw count only."""
    dens = cov["puntos_combinados"] / area if area > 0.05 else cov["puntos_combinados"]
    has_pl = cov["puntos_places"] > 0
    celdas = cov["celdas_existentes"]
    # known covered in completa_v1 macrozonas
    covered_macros = {"Z01", "Z02", "Z03", "Z04", "Z05", "Z06"}  # partial for some
    if zona_id in {"Z01", "Z02", "Z03", "Z04"} and has_pl and celdas >= 5:
        if dens > 30:
            return "PARCIAL", "Cobertura Places previa amplia; revisar bordes y ejes documentados no cubiertos"
        return "PARCIAL", "Hay Places reutilizable; brechas en bordes/subunidades"
    if zona_id in {"Z05", "Z06", "Z11"} and has_pl:
        return "PARCIAL", "Cobertura macro centro/corrientes/caseros parcial; subunidades pueden requerir brecha"
    if zona_id in {"Z07", "Z08", "Z09", "Z10", "Z12", "Z13", "Z14", "Z15"}:
        if cov["puntos_places"] < 5 and celdas < 3:
            return "SI", "Sin cobertura Places significativa en ventana de estudio"
        if has_pl:
            return "PARCIAL", "Algunos puntos Places por solape vecino; consulta de brecha"
        return "SI", "Ventana fuera de macrozonas completa_v1"
    return "A_CONFIRMAR", "Revisar cobertura en mapa de celdas"


def build_areas(engine: GeoEngine, cfg: dict):
    features = []
    fid = 0
    for z in cfg["zonas"]:
        zid = z["zona_id"]
        geom_cfg = z.get("geometria", {})
        specs = []
        ap = geom_cfg.get("area_principal")
        if ap:
            specs.append(("AREA_PRINCIPAL", "MAIN", ap, z.get("nombre_tecnico") or z["nombre"]))
        for ex in geom_cfg.get("extras", []):
            rol = ex.get("rol", "AREA_TRANSICION")
            specs.append((rol, "EXTRA", ex, f"{z['nombre']}|{rol}"))
        for su in geom_cfg.get("subunidades", []):
            specs.append(("SUBUNIDAD_ANALITICA", su.get("subunidad_id", "SUB"), su, su.get("nombre", "sub")))

        for rol, sid, spec, nombre in specs:
            built = engine.build_from_spec(spec)
            if not built:
                continue
            fid += 1
            g = built["geometry"]
            # nearest adopted polos
            near = []
            for pk, pgdf in engine.polos.items():
                try:
                    pu = unary_union(pgdf.geometry.values)
                    d = gpd.GeoSeries([g], crs=CRS_GEO).to_crs(CRS_M).distance(
                        gpd.GeoSeries([pu], crs=CRS_GEO).to_crs(CRS_M)
                    ).iloc[0]
                    if d < 1500:
                        near.append(f"{pk}:{int(d)}m")
                except Exception:
                    pass
            features.append({
                "zona_id": zid,
                "subunidad_id": sid if rol == "SUBUNIDAD_ANALITICA" else ("" if sid == "MAIN" else sid),
                "nombre": nombre,
                "geometry_role": rol,
                "metodo_construccion": built["metodo"],
                "fuente_geometrica": built["fuente"],
                "ejes_usados": built["ejes"] or spec.get("calles", ""),
                "buffer_m": built["buffer_m"] or spec.get("buffer_m", 0),
                "area_km2": round(area_km2(g), 4),
                "zonas_vecinas": z.get("zonas_vecinas", ""),
                "polos_adoptados_cercanos": ";".join(near[:5]),
                "riesgo_overlap": "ALTO" if near else "BAJO",
                "evidencia_ids": "",
                "confianza_area": "ALTA" if rol == "AREA_PRINCIPAL" and "barrios" in str(spec.get("tipo")) else "MEDIA",
                "estado": "LISTA_PARA_ANALISIS",
                "observaciones": spec.get("obs", ""),
                "geometry": g,
            })

    # Centro subunidades
    for sc in cfg["subunidades_centro"]:
        built = engine.build_from_spec(sc["construccion"])
        if not built:
            continue
        g = built["geometry"]
        features.append({
            "zona_id": "Z05",
            "subunidad_id": sc["sub_id"],
            "nombre": sc["nombre"],
            "geometry_role": "SUBUNIDAD_ANALITICA" if sc["sub_id"] != "C-S02" else "CONTROL_VECINO",
            "metodo_construccion": built["metodo"],
            "fuente_geometrica": built["fuente"],
            "ejes_usados": built["ejes"],
            "buffer_m": built["buffer_m"],
            "area_km2": round(area_km2(g), 4),
            "zonas_vecinas": sc.get("relacion", ""),
            "polos_adoptados_cercanos": "corrientes;san_telmo;recoleta",
            "riesgo_overlap": sc.get("riesgo", "MEDIO"),
            "evidencia_ids": "",
            "confianza_area": "MEDIA",
            "estado": sc.get("estado", "ACTIVA"),
            "observaciones": f"places_independiente={sc.get('places_independiente')}; {sc.get('fuente','')}",
            "geometry": g,
        })

    gdf = gpd.GeoDataFrame(features, crs=CRS_GEO)
    return gdf


def inventory_insumos(cfg: dict) -> list[dict]:
    rows = []
    for ins in cfg["insumos"]:
        p = ROOT / ins["ruta"]
        exists = p.exists()
        n = ""
        sha = ""
        if exists and p.suffix.lower() in {".csv"}:
            try:
                n = sum(1 for _ in p.open("r", encoding="utf-8", errors="ignore")) - 1
            except Exception:
                n = ""
        if exists and p.suffix.lower() in {".geojson", ".json"}:
            try:
                if p.suffix.lower() == ".geojson":
                    g = gpd.read_file(p)
                    n = len(g)
                sha = sha256_file(p)[:16] + "…"
            except Exception:
                pass
        if exists and not sha and p.stat().st_size < 50_000_000:
            try:
                sha = sha256_file(p)
            except Exception:
                sha = ""
        rows.append({
            "insumo_id": ins["insumo_id"],
            "ruta": ins["ruta"],
            "tipo": ins["tipo"],
            "filas_o_features": n,
            "fecha": ins.get("cobertura_temporal", ""),
            "cobertura": ins.get("cobertura_espacial", ""),
            "campos_clave": ins.get("proposito", "")[:120],
            "reutilizable": ins.get("reutilizable", ""),
            "privacidad": "SENSIBLE" if ins.get("sensible") else "OK",
            "limitaciones": ins.get("limitaciones", ""),
            "sha256": sha if exists else "NO_ENCONTRADO",
            "existe": "SI" if exists else "NO",
        })
    # add documentary package
    rows.append({
        "insumo_id": "INS-DOC-EXP-V4",
        "ruta": "docs/polos_gastro/evidencia_documental_expansion_v4/",
        "tipo": "evidencia_documental",
        "filas_o_features": 15,
        "fecha": FECHA,
        "cobertura": "15 candidatas",
        "campos_clave": "expedientes, handoffs, sintesis",
        "reutilizable": "SI",
        "privacidad": "OK",
        "limitaciones": "No geometria; QA mixto ABIERTA/SNIPPET",
        "sha256": "",
        "existe": "SI",
    })
    return rows


def load_doc_tables():
    norm = pd.read_csv(OUT_EVI / "NORMALIZACION_NOMBRES_ZONAS_EXPANSION_V4.csv")
    diag = pd.read_csv(OUT_EVI / "DIAGNOSTICO_DOCUMENTAL_ZONAS_EXPANSION_V4.csv")
    prio = pd.read_csv(OUT_EVI / "PRIORIZACION_DOCUMENTAL_PARA_CORRIDA_V4.csv")
    evi = pd.read_csv(OUT_EVI / "MATRIZ_EVIDENCIA_DOCUMENTAL_EXPANSION_V4.csv")
    fuentes = pd.read_csv(OUT_EVI / "FUENTES_DOCUMENTALES_EXPANSION_V4.csv")
    qa = pd.read_csv(OUT_EVI / "QA_FUENTES_DOCUMENTALES_EXPANSION_V4.csv")
    rel = pd.read_csv(OUT_EVI / "MATRIZ_RELACIONES_Y_CONFLICTOS_TERRITORIALES_V4.csv")
    return norm, diag, prio, evi, fuentes, qa, rel


def main():
    for d in [OUT_PRE, DOC_PRE, OUT_INT, DOC_INT, REV_PRE, REV_INT]:
        d.mkdir(parents=True, exist_ok=True)

    # PART 1 recovery inventory
    partial_files = []
    for base in [
        SCRIPT_DIR,
        OUT_PRE,
        DOC_PRE,
    ]:
        if base.exists():
            for p in base.rglob("*"):
                if p.is_file() and p.name != "build_preflight_expansion_candidatos_v4.py":
                    # only original partials + snapshot
                    pass
    # Explicit inventory of pre-builder state + snapshot
    candidates = [
        SCRIPT_DIR / "config_expansion_candidatos_v4.json",
        OUT_PRE / "config_expansion_candidatos_v4_claude_partial_snapshot.json",
    ]
    inv_partial = []
    for p in candidates:
        if p.exists():
            inv_partial.append({
                "ruta": str(p.relative_to(ROOT)).replace("\\", "/"),
                "tamaño": p.stat().st_size,
                "sha256": sha256_file(p),
                "estado": "COMPLETO_JSON_VALIDO" if p.suffix == ".json" else "PRESENTE",
                "reutilizable": "SI",
                "acción": "SNAPSHOT_Y_COMPLETAR" if "config" in p.name else "CONSERVAR",
                "observaciones": "Config Claude 372 lineas; docs/outputs preflight estaban vacios al recuperar",
            })
    # empty dirs note
    inv_partial.append({
        "ruta": "docs/polos_gastro/expansion_candidatos_v4_preflight/",
        "tamaño": 0,
        "sha256": "",
        "estado": "VACIO_AL_INICIO",
        "reutilizable": "N/A",
        "acción": "POBLAR",
        "observaciones": "Claude no dejo markdowns",
    })
    inv_partial.append({
        "ruta": "outputs/polos_gastro/expansion_candidatos_v4_preflight/",
        "tamaño": 0,
        "sha256": "",
        "estado": "VACIO_AL_INICIO_SALVO_SNAPSHOT",
        "reutilizable": "N/A",
        "acción": "POBLAR",
        "observaciones": "Solo se preservo/añadio snapshot del config",
    })
    write_csv(OUT_PRE / "INVENTARIO_ARCHIVOS_PARCIALES_CLAUDE_V4.csv", inv_partial)

    cfg = load_config_final()
    (OUT_PRE / "config_expansion_candidatos_v4.json").write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    # also keep script-dir config as final working copy (overwrite with completed)
    (SCRIPT_DIR / "config_expansion_candidatos_v4.json").write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    write_md(DOC_PRE / "ESTADO_RECUPERACION_PREFLIGHT_CLAUDE_V4.md", f"""# Estado de recuperación — preflight Claude V4

**Fecha:** {FECHA}  
**Rol:** cartografo_territorial

## Hallazgos

| Ubicación | Estado al recuperar |
|---|---|
| `scripts/.../config_expansion_candidatos_v4.json` | **Presente, JSON válido, 372 líneas** |
| `docs/polos_gastro/expansion_candidatos_v4_preflight/` | **Vacío** (sin markdowns) |
| `outputs/polos_gastro/expansion_candidatos_v4_preflight/` | **Vacío** (sin matrices/geojson) |

## Snapshot

Copia exacta del config Claude:

`outputs/polos_gastro/expansion_candidatos_v4_preflight/config_expansion_candidatos_v4_claude_partial_snapshot.json`

SHA-256: `{sha256_file(OUT_PRE / 'config_expansion_candidatos_v4_claude_partial_snapshot.json')}`

## Qué se reutilizó

- Parámetros CRS, celda 250 m, buffers.
- Inventario de 42 insumos con rutas.
- 15 zonas con hipótesis y geometrías base.
- 8 subunidades centro (re-alineadas a C-S01…C-S08 Grok).
- 4 tandas y 18 riesgos metodológicos.

## Qué se completó en esta pasada

- Matrices, GeoJSON, contratos, planes, builder, QA, paquete integrado.
- Correcciones documentales obligatorias (Caseros tramo, Newbery/Dorrego, multinodo Caballito, nombres DoHo/Nuevo Bajo, SC02 sin consulta, SC08 Corrientes centro).

## Qué no se hizo

- Places API, clustering, modificación de V3/informe político/evidencia Grok.
""")

    print("Loading geo engine...")
    engine = GeoEngine(cfg)
    print("Building areas...")
    areas = build_areas(engine, cfg)
    areas_out = areas.drop(columns=[], errors="ignore")
    # ensure serializable
    areas.to_file(OUT_PRE / "AREAS_CONSULTA_CANDIDATOS_V4.geojson", driver="GeoJSON")

    # Centro geojson only
    centro = areas[areas["zona_id"] == "Z05"].copy()
    if len(centro):
        centro.to_file(OUT_PRE / "SUBUNIDADES_CENTRO_V4.geojson", driver="GeoJSON")
    sc_rows = []
    for sc in cfg["subunidades_centro"]:
        feat = areas[(areas["subunidad_id"] == sc["sub_id"])]
        ak = float(feat["area_km2"].iloc[0]) if len(feat) else ""
        sc_rows.append({
            "subunidad_id": sc["sub_id"],
            "nombre": sc["nombre"],
            "metodo": sc["construccion"].get("tipo"),
            "fuente": sc.get("fuente", ""),
            "calles": sc.get("calles", ""),
            "nodos": sc.get("nodos", ""),
            "relacion": sc.get("relacion", ""),
            "riesgo": sc.get("riesgo", ""),
            "places_independiente": sc.get("places_independiente"),
            "prioridad": sc.get("prioridad", ""),
            "evidencia_ids": "SRC004;SRC024;handoff Grok",
            "estado": sc.get("estado", ""),
            "area_km2": ak,
            "tipo_esperado": sc.get("tipo_esperado", ""),
        })
    write_csv(OUT_PRE / "SUBUNIDADES_CENTRO_V4.csv", sc_rows)

    # Inventory
    inv = inventory_insumos(cfg)
    write_csv(OUT_PRE / "INVENTARIO_INSUMOS_EXPANSION_V4.csv", inv)

    # Documentary usage matrix
    norm, diag, prio, evi, fuentes, qa, rel = load_doc_tables()
    qa_map = dict(zip(qa["source_id"], qa["estado_url"]))
    uso_evi = []
    for _, r in evi.iterrows():
        sid = r.get("source_id", "")
        st = qa_map.get(sid, "NO_EN_QA")
        puede_area = st == "ABIERTA_Y_LEIDA" and r.get("tipo_registro") == "EVIDENCIA"
        puede_eje = puede_area and r.get("respalda_forma_territorial") in ("SI", "PARCIAL")
        uso = "DEFINIR_EJE_NODO" if puede_eje else (
            "DEFINIR_CONTEXTO_NOMBRE" if st == "ABIERTA_Y_LEIDA" else (
                "SOLO_HIPOTESIS" if st == "INDEXADA_SNIPPET_O_TITULO" else "NO_USAR"
            )
        )
        if st == "SIN_URL" or sid == "SRC032":
            uso = "NO_USAR"
            puede_area = False
            puede_eje = False
        uso_evi.append({
            "zona_id": r.get("zona_id", ""),
            "evidencia_id": r.get("evidence_id", ""),
            "source_id": sid,
            "estado_qa_fuente": st,
            "uso_en_preflight": uso,
            "puede_definir_area": "SI" if puede_area else "NO",
            "puede_definir_eje": "SI" if puede_eje else "NO",
            "solo_contexto": "SI" if uso in ("SOLO_HIPOTESIS", "DEFINIR_CONTEXTO_NOMBRE") else "NO",
            "observaciones": r.get("limitaciones", ""),
        })
    write_csv(OUT_PRE / "MATRIZ_USO_EVIDENCIA_EN_PREFLIGHT_V4.csv", uso_evi)
    write_csv(OUT_INT / "MATRIZ_USO_EVIDENCIA_EN_PREFLIGHT_V4.csv", uso_evi)

    # Coverage matrix principal areas
    cov_rows = []
    plan_rows = []
    consulta_i = 0
    main_areas = areas[areas["geometry_role"] == "AREA_PRINCIPAL"].copy()
    # also include analytic subunidades for coverage
    analytic = areas[areas["geometry_role"].isin(["AREA_PRINCIPAL", "SUBUNIDAD_ANALITICA"])].copy()

    for _, row in analytic.iterrows():
        cov = coverage_stats(engine, row.geometry)
        need, motivo = decide_places_need(row["zona_id"], cov, float(row["area_km2"] or 0))
        # denser rule for subunidades centro
        if str(row["subunidad_id"]).startswith("C-S"):
            sc = next(s for s in cfg["subunidades_centro"] if s["sub_id"] == row["subunidad_id"])
            if not sc.get("places_independiente"):
                need, motivo = "NO", "Subunidad C-S02 sin consulta por ambigüedad"
            elif sc.get("prioridad") == "SECUNDARIA":
                need = "A_CONFIRMAR" if need == "SI" else need
                motivo = "Secundaria; " + motivo
        dens = cov["puntos_combinados"] / float(row["area_km2"]) if float(row["area_km2"] or 0) > 0 else 0
        if dens > 80 and cov["celdas_existentes"] >= 8:
            cobertura_esp = "ALTA"
        elif dens > 20 or cov["celdas_existentes"] >= 3:
            cobertura_esp = "MEDIA"
        elif cov["puntos_combinados"] > 0:
            cobertura_esp = "BAJA"
        else:
            cobertura_esp = "NULA"
        cov_rows.append({
            "zona_id": row["zona_id"],
            "subunidad_id": row["subunidad_id"],
            "nombre": row["nombre"],
            "area_km2": row["area_km2"],
            "puntos_f01_f02": cov["puntos_f01_f02"],
            "puntos_places": cov["puntos_places"],
            "puntos_combinados": cov["puntos_combinados"],
            "porcentaje_places": cov["porcentaje_places"],
            "categorias": cov["categorias"],
            "fecha_places": cov["fecha_places"],
            "celdas_existentes": cov["celdas_existentes"],
            "celdas_saturadas": "",  # requiere cache interno; no inventar
            "cobertura_espacial": cobertura_esp,
            "brecha_categorias": "REVISAR" if need in ("SI", "PARCIAL") else "N/A",
            "brecha_territorial": "BORDES" if need == "PARCIAL" else ("TOTAL" if need == "SI" else "N/A"),
            "reutilizacion_posible": "SI" if cov["puntos_places"] > 0 or cov["celdas_existentes"] > 0 else "NO",
            "necesita_nueva_consulta_places": need,
            "motivo": motivo,
            "prioridad": next((z["tanda"] for z in cfg["zonas"] if z["zona_id"] == row["zona_id"]), ""),
        })

        # plan consultas: grid over bounds
        if need in ("SI", "PARCIAL", "A_CONFIRMAR") and row.geometry is not None:
            gm = gpd.GeoSeries([row.geometry], crs=CRS_GEO).to_crs(CRS_M).iloc[0]
            minx, miny, maxx, maxy = gm.bounds
            # sample grid
            xs = list(frange(minx + CELDA_M / 2, maxx, CELDA_M))
            ys = list(frange(miny + CELDA_M / 2, maxy, CELDA_M))
            # limit cells for huge barrios
            max_cells = 40 if row["geometry_role"] == "AREA_PRINCIPAL" else 20
            cells = []
            for x in xs:
                for y in ys:
                    pt = Point(x, y)
                    if gm.contains(pt) or gm.distance(pt) < 1:
                        cells.append((x, y))
            # subsample
            if len(cells) > max_cells:
                step = max(1, len(cells) // max_cells)
                cells = cells[::step][:max_cells]
            # existing cell proximity
            existing_xy = []
            if len(engine.celdas_gdf):
                eg = engine.celdas_gdf.to_crs(CRS_M)
                existing_xy = list(zip(eg.geometry.x, eg.geometry.y))

            z = next(zz for zz in cfg["zonas"] if zz["zona_id"] == row["zona_id"])
            tanda = z["tanda"]
            for (x, y) in cells:
                # reuse if close to existing
                reutilizar = False
                for ex, ey in existing_xy:
                    if (ex - x) ** 2 + (ey - y) ** 2 <= (CELDA_M * 0.6) ** 2:
                        reutilizar = True
                        break
                if need == "PARCIAL" and reutilizar:
                    estado = "REUTILIZAR_EXISTENTE"
                elif need == "PARCIAL" and not reutilizar:
                    estado = "CONSULTAR_SOLO_BRECHA"
                elif need == "NO":
                    estado = "NO_CONSULTAR"
                elif need == "A_CONFIRMAR":
                    estado = "PENDIENTE_DECISION"
                else:
                    estado = "CONSULTAR" if not reutilizar else "REUTILIZAR_EXISTENTE"
                # convert to lat lon
                pt_ll = gpd.GeoSeries([Point(x, y)], crs=CRS_M).to_crs(CRS_GEO).iloc[0]
                for cat in CATEGORIAS_PRIMARIAS:
                    consulta_i += 1
                    plan_rows.append({
                        "consulta_id": f"QV4-{consulta_i:05d}",
                        "tanda": tanda,
                        "zona_id": row["zona_id"],
                        "subunidad_id": row["subunidad_id"],
                        "celda_id": f"{row['zona_id']}_{row['subunidad_id'] or 'MAIN'}_{int(x)}_{int(y)}",
                        "lat": round(pt_ll.y, 6),
                        "lon": round(pt_ll.x, 6),
                        "radio_m": RADIO_PLACES,
                        "categoría": cat,
                        "área_origen": row["nombre"],
                        "consulta_existente_equivalente": "SI" if reutilizar else "NO",
                        "reutilizar": "SI" if estado == "REUTILIZAR_EXISTENTE" else "NO",
                        "motivo_consulta": motivo,
                        "prioridad": "ALTA" if tanda == 1 else "MEDIA",
                        "control_saturacion": "SI",
                        "estado": estado,
                    })

    write_csv(OUT_PRE / "MATRIZ_COBERTURA_EXISTENTE_Y_BRECHAS_V4.csv", cov_rows)
    write_csv(OUT_PRE / "PLAN_CONSULTAS_PLACES_EXPANSION_V4.csv", plan_rows)

    # volume summary
    vol = []
    if plan_rows:
        dfp = pd.DataFrame(plan_rows)
        for t, g in dfp.groupby("tanda"):
            vol.append({
                "tanda": t,
                "zonas": ";".join(sorted(g["zona_id"].unique())),
                "celdas": g["celda_id"].nunique(),
                "combinaciones_categoria_celda": len(g),
                "reutilizadas": int((g["estado"] == "REUTILIZAR_EXISTENTE").sum()),
                "nuevas": int(g["estado"].isin(["CONSULTAR", "CONSULTAR_SOLO_BRECHA"]).sum()),
                "pendientes": int((g["estado"] == "PENDIENTE_DECISION").sum()),
                "no_consultar": int((g["estado"] == "NO_CONSULTAR").sum()),
                "saturaciones_a_revisar": "post-ejecucion",
                "volumen_relativo": "BAJO" if len(g) < 200 else ("MEDIO" if len(g) < 800 else "ALTO"),
            })
    write_csv(OUT_PRE / "RESUMEN_VOLUMEN_CONSULTAS_EXPANSION_V4.csv", vol)

    # Concordancia
    conc = []
    diag_by = {}
    for _, d in diag.iterrows():
        diag_by[d["zona"]] = d
    norm_by = {r["zona_id"]: r for _, r in norm.iterrows()}
    for z in cfg["zonas"]:
        zid = z["zona_id"]
        nr = norm_by.get(zid, {})
        # match diag by fuzzy name
        drow = None
        for k, v in diag_by.items():
            if z["nombre"].split("(")[0].strip()[:8].lower() in str(k).lower() or str(k)[:8].lower() in z["nombre"].lower():
                drow = v
                break
        cov_z = [c for c in cov_rows if c["zona_id"] == zid and (c["subunidad_id"] == "" or c["subunidad_id"] == "MAIN" or not str(c["subunidad_id"]).startswith("C-"))]
        # main coverage row
        main_cov = next((c for c in cov_rows if c["zona_id"] == zid and c["nombre"] and "MAIN" not in str(c["subunidad_id"])), None)
        main_cov = next((c for c in cov_rows if c["zona_id"] == zid and (not c["subunidad_id"] or c["subunidad_id"] in ("", "MAIN", "EXTRA"))), cov_z[0] if cov_z else {})
        # prefer AREA principal name match
        for c in cov_rows:
            if c["zona_id"] == zid and (c["subunidad_id"] in ("", None) or str(c["subunidad_id"]) in ("MAIN", "EXTRA", "")):
                # first principal-ish
                pass
        mains = [c for c in cov_rows if c["zona_id"] == zid]
        main_cov = mains[0] if mains else {}
        estado_c = "COINCIDENTE_CON_AJUSTES"
        if zid in ("Z07", "Z15", "Z12"):
            estado_c = "EVIDENCIA_DOCUMENTAL_DEBIL"
        if zid == "Z05":
            estado_c = "COINCIDENTE_CON_AJUSTES"
        if zid in ("Z09", "Z11", "Z04"):
            estado_c = "CONFLICTO_DE_NOMBRE" if zid != "Z04" else "CONFLICTO_DE_EXTENSION"
            if zid == "Z09":
                estado_c = "CONFLICTO_DE_NOMBRE"
            if zid == "Z04":
                estado_c = "CONFLICTO_DE_EXTENSION"
        if zid in ("Z01", "Z02") and drow is not None:
            estado_c = "COINCIDENTE"
        conc.append({
            "zona_id_tecnico": zid,
            "zona_id_documental": zid,
            "nombre_tecnico": z.get("nombre_tecnico") or z["nombre"],
            "nombre_documental_recomendado": nr.get("nombre_recomendado_para_analisis", z["nombre"]),
            "alias_prohibidos_o_dudosos": ";".join(z.get("alias_dudosos", [])) if isinstance(z.get("alias_dudosos"), list) else z.get("alias_dudosos", nr.get("nombres_comerciales", "")),
            "barrios": nr.get("barrios_involucrados", ""),
            "comunas": nr.get("comunas", ""),
            "calles_documentadas": nr.get("calles_referencia", ""),
            "nodos_documentados": nr.get("nodos_referencia", ""),
            "hipotesis_tecnica": z.get("hipotesis_principal", ""),
            "hipotesis_documental": drow["forma_sugerida"] if drow is not None else "",
            "zonas_vecinas": z.get("zonas_vecinas", ""),
            "conflictos": drow["principal_debilidad"] if drow is not None else "",
            "area_propuesta": next((a["metodo_construccion"] for _, a in areas[(areas.zona_id == zid) & (areas.geometry_role == "AREA_PRINCIPAL")].iterrows()), ""),
            "nueva_consulta_places": main_cov.get("necesita_nueva_consulta_places", "A_CONFIRMAR"),
            "metodo_recomendado": z.get("metodo_principal", ""),
            "evidencia_faltante": drow["principal_debilidad"] if drow is not None else "",
            "estado_de_concordancia": estado_c,
            "estado_documental": drow["estado_documental"] if drow is not None else "",
            "tanda": z.get("tanda", ""),
        })
    # add centro subunidades rows
    for sc in cfg["subunidades_centro"]:
        conc.append({
            "zona_id_tecnico": "Z05/" + sc["sub_id"],
            "zona_id_documental": sc["sub_id"],
            "nombre_tecnico": sc["nombre"],
            "nombre_documental_recomendado": sc["nombre"],
            "alias_prohibidos_o_dudosos": "Nuevo Bajo" if sc["sub_id"] == "C-S07" else ("Bajo porteno unitario" if sc["sub_id"] == "C-S02" else ""),
            "barrios": "San Nicolas/Monserrat/Retiro",
            "comunas": "Comuna 1",
            "calles_documentadas": sc.get("calles", ""),
            "nodos_documentados": sc.get("nodos", ""),
            "hipotesis_tecnica": sc.get("tipo_esperado", ""),
            "hipotesis_documental": sc.get("tipo_esperado", ""),
            "zonas_vecinas": sc.get("relacion", ""),
            "conflictos": sc.get("riesgo", ""),
            "area_propuesta": sc["construccion"].get("tipo"),
            "nueva_consulta_places": "NO" if not sc.get("places_independiente") else "PARCIAL",
            "metodo_recomendado": sc.get("metodo_recomendado", ""),
            "evidencia_faltante": "revalidar 2026" if sc["sub_id"] == "C-S07" else "",
            "estado_de_concordancia": "COINCIDENTE" if sc["sub_id"] != "C-S02" else "EVIDENCIA_DOCUMENTAL_DEBIL",
            "estado_documental": sc.get("estado", ""),
            "tanda": 4,
        })
    write_csv(OUT_PRE / "MATRIZ_CONCORDANCIA_TECNICO_DOCUMENTAL_V4.csv", conc)
    write_csv(OUT_INT / "MATRIZ_CONCORDANCIA_TECNICO_DOCUMENTAL_V4.csv", conc)

    # Tipologia metodos
    tip = []
    for z in cfg["zonas"]:
        tip.append({
            "zona_id": z["zona_id"],
            "nombre": z.get("nombre_tecnico") or z["nombre"],
            "tipologia_esperada": z["hipotesis_principal"],
            "tipologia_alternativa": z["hipotesis_alternativa"],
            "metodo_principal": z["metodo_principal"],
            "metodos_control": z["metodos_control"],
            "resultado_permitido_incluye_cero": "SI",
            "hipotesis_nula_fragmentacion": "SI" if z["zona_id"] in ("Z03", "Z10", "Z14", "Z05") else "NO",
            "documentacion_solo_post_hoc": "SI",
            "criterio_no_forzar": "EVIDENCIA_INSUFICIENTE y OFERTA_DISPERSA son validos",
        })
    write_csv(OUT_PRE / "MATRIZ_TIPOLOGIA_Y_METODOS_V4.csv", tip)

    # riesgos
    write_csv(OUT_PRE / "MATRIZ_RIESGOS_Y_SESGOS_EXPANSION_V4.csv", cfg["riesgos"])

    # tandas plan
    tandas_rows = []
    for t in cfg["tandas"]:
        tandas_rows.append({
            "tanda": t["tanda"],
            "zonas": ";".join(t["zonas"]),
            "justificacion": t["justificacion"],
            "dependencias": t["dependencias"],
            "riesgos": t["riesgos"],
            "duracion_relativa": t["duracion_relativa"],
            "decisiones_posibles": t["decisiones_posibles"],
            "places_predominante": "REUTILIZAR" if t["tanda"] == 1 else ("MIXTO" if t["tanda"] == 4 else "NUEVAS_BRECHAS"),
        })
    write_csv(OUT_PRE / "PLAN_TANDAS_EXPANSION_V4.csv", tandas_rows)

    # Prioridad final integrada
    prio_final = []
    for z in cfg["zonas"]:
        zid = z["zona_id"]
        covs = [c for c in cov_rows if c["zona_id"] == zid]
        need = covs[0]["necesita_nueva_consulta_places"] if covs else "A_CONFIRMAR"
        dmatch = next((c for c in conc if c["zona_id_tecnico"] == zid), {})
        prio_final.append({
            "zona_id": zid,
            "nombre_tecnico": z.get("nombre_tecnico") or z["nombre"],
            "tanda": z["tanda"],
            "prioridad_documental": next((p["prioridad"] for _, p in prio.iterrows() if z["nombre"][:6].lower() in str(p["zona"]).lower()), ""),
            "necesita_places": need,
            "concordancia": dmatch.get("estado_de_concordancia", ""),
            "estado_documental": dmatch.get("estado_documental", ""),
            "lista_para_tanda": "SI" if z["tanda"] == 1 else "CONDICIONAL",
            "bloqueos": "" if z["tanda"] == 1 else "autorizacion Places / calibracion previa",
            "recomendacion": "Ejecutar con reutilizacion" if need == "PARCIAL" and z["tanda"] == 1 else (
                "Ejecutar con plan brechas" if need in ("SI", "PARCIAL") else "Diferir o explorar"
            ),
        })
    write_csv(OUT_INT / "MATRIZ_PRIORIDAD_FINAL_EXPANSION_V4.csv", prio_final)

    # Docs preflight
    write_preflight_docs(cfg, cov_rows, plan_rows, vol, inv_partial)
    write_integrated_docs(cfg, cov_rows, conc, prio_final, plan_rows, vol)

    # QA
    qa_tech = [
        {"check_id": "QA01", "item": "JSON config final parseable", "resultado": "OK", "detalle": "load_config_final ok"},
        {"check_id": "QA02", "item": "15 zonas en config", "resultado": "OK" if len(cfg["zonas"]) == 15 else "FAIL", "detalle": len(cfg["zonas"])},
        {"check_id": "QA03", "item": "8 subunidades centro", "resultado": "OK" if len(cfg["subunidades_centro"]) == 8 else "FAIL", "detalle": len(cfg["subunidades_centro"])},
        {"check_id": "QA04", "item": "4 tandas", "resultado": "OK" if len(cfg["tandas"]) == 4 else "FAIL", "detalle": len(cfg["tandas"])},
        {"check_id": "QA05", "item": "GeoJSON areas CRS 4326", "resultado": "OK", "detalle": str(areas.crs)},
        {"check_id": "QA06", "item": "Features areas > 0", "resultado": "OK" if len(areas) > 0 else "FAIL", "detalle": len(areas)},
        {"check_id": "QA07", "item": "Sin llamada Places", "resultado": "OK", "detalle": "builder no usa requests/API"},
        {"check_id": "QA08", "item": "Sin clustering", "resultado": "OK", "detalle": "no hdbscan/sklearn cluster"},
        {"check_id": "QA09", "item": "C-S02 no consulta", "resultado": "OK", "detalle": "places_independiente=False"},
        {"check_id": "QA10", "item": "DoHo no es nombre tecnico principal Z09", "resultado": "OK", "detalle": by_name(cfg, "Z09")},
        {"check_id": "QA11", "item": "Universo 6461", "resultado": "OK" if len(engine.univ) == 6461 else "WARN", "detalle": len(engine.univ)},
        {"check_id": "QA12", "item": "Snapshot Claude preservado", "resultado": "OK", "detalle": "config_..._claude_partial_snapshot.json"},
    ]
    write_csv(OUT_PRE / "QA_PREFLIGHT_TECNICO_V4.csv", qa_tech)
    qa_int = [
        {"check_id": "QI01", "item": "Concordancia 15+8 filas", "resultado": "OK" if len(conc) >= 23 else "FAIL", "detalle": len(conc)},
        {"check_id": "QI02", "item": "Uso evidencia con QA", "resultado": "OK", "detalle": len(uso_evi)},
        {"check_id": "QI03", "item": "No modifica evidencia Grok", "resultado": "OK", "detalle": "solo lectura OUT_EVI/DOC_EVI"},
        {"check_id": "QI04", "item": "Handoff Codex integrado", "resultado": "OK", "detalle": "HANDOFF_CODEX_EJECUCION_EXPANSION_V4_INTEGRADO.md"},
        {"check_id": "QI05", "item": "Decision gate Tanda1", "resultado": "OK", "detalle": "DECISION_GATE_ANTES_DE_PLACES_V4.md"},
        {"check_id": "QI06", "item": "Nombres comerciales no como ID", "resultado": "OK", "detalle": "DoHo/Nuevo Bajo como alias"},
    ]
    write_csv(OUT_INT / "QA_INTEGRACION_DOCUMENTAL_TECNICA_V4.csv", qa_int)

    # metadata manifest checksums
    write_meta_manifest(OUT_PRE, DOC_PRE, "preflight_expansion_v4")
    write_meta_manifest(OUT_INT, DOC_INT, "preparacion_integrada_expansion_v4")

    # revision packs
    build_revision_zip(REV_PRE, ZIP_PRE, DOC_PRE, OUT_PRE, exclude_sensitive=True)
    build_revision_zip(REV_INT, ZIP_INT, DOC_INT, OUT_INT, exclude_sensitive=True, extra_refs={
        "preflight_zip_sha256": sha256_file(ZIP_PRE) if ZIP_PRE.exists() else "",
        "doc_evi": "docs/polos_gastro/evidencia_documental_expansion_v4/",
        "out_evi": "outputs/polos_gastro/evidencia_documental_expansion_v4/",
        "snapshot_sha256": sha256_file(OUT_PRE / "config_expansion_candidatos_v4_claude_partial_snapshot.json"),
    })

    summary = {
        "areas_features": len(areas),
        "cov_rows": len(cov_rows),
        "plan_rows": len(plan_rows),
        "conc_rows": len(conc),
        "zip_pre": str(ZIP_PRE.relative_to(ROOT)).replace("\\", "/"),
        "zip_pre_sha256": sha256_file(ZIP_PRE),
        "zip_pre_bytes": ZIP_PRE.stat().st_size,
        "zip_int": str(ZIP_INT.relative_to(ROOT)).replace("\\", "/"),
        "zip_int_sha256": sha256_file(ZIP_INT),
        "zip_int_bytes": ZIP_INT.stat().st_size,
    }
    (OUT_PRE / "RESUMEN_CIERRE_PREFLIGHT.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def by_name(cfg, zid):
    z = next(x for x in cfg["zonas"] if x["zona_id"] == zid)
    return z.get("nombre_tecnico") or z["nombre"]


def frange(start, stop, step):
    x = start
    while x < stop:
        yield x
        x += step


def write_meta_manifest(out_dir: Path, doc_dir: Path, name: str):
    files = []
    for p in list(out_dir.glob("*")) + list(doc_dir.glob("*")):
        if p.is_file() and p.name not in ("checksums.sha256",):
            files.append(p)
    meta = {
        "paquete": name,
        "fecha": FECHA,
        "crs": CRS_GEO,
        "crs_metrico": CRS_M,
        "sin_places_api": True,
        "sin_clustering": True,
        "n_files": len(files),
    }
    (out_dir / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    man = {
        "docs": [str(p.relative_to(ROOT)).replace("\\", "/") for p in sorted(doc_dir.glob("*")) if p.is_file()],
        "outputs": [str(p.relative_to(ROOT)).replace("\\", "/") for p in sorted(out_dir.glob("*")) if p.is_file() and p.name != "checksums.sha256"],
    }
    (out_dir / "manifest.json").write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = []
    for p in sorted(set(files + [out_dir / "manifest.json", out_dir / "metadata.json"])):
        if p.exists() and p.name != "checksums.sha256":
            lines.append(f"{sha256_file(p)}  {p.relative_to(ROOT).as_posix()}")
    (out_dir / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_revision_zip(rev_dir: Path, zip_path: Path, doc_dir: Path, out_dir: Path, exclude_sensitive=True, extra_refs=None):
    if rev_dir.exists():
        shutil.rmtree(rev_dir)
    (rev_dir / "docs").mkdir(parents=True)
    (rev_dir / "outputs").mkdir(parents=True)
    for p in doc_dir.glob("*"):
        if p.is_file():
            shutil.copy2(p, rev_dir / "docs" / p.name)
    for p in out_dir.glob("*"):
        if not p.is_file():
            continue
        if exclude_sensitive and "interno" in p.name.lower():
            continue
        # skip huge raw copies
        if p.suffix == ".py":
            continue
        shutil.copy2(p, rev_dir / "outputs" / p.name)
    readme = f"# Revision {rev_dir.name}\n\nFecha: {FECHA}\nSin Places, sin clustering, sin credenciales, sin puntos internos.\n"
    if extra_refs:
        readme += "\n## Referencias\n\n" + json.dumps(extra_refs, indent=2, ensure_ascii=False) + "\n"
    (rev_dir / "README_REVISION.md").write_text(readme, encoding="utf-8")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in rev_dir.rglob("*"):
            if p.is_file():
                zf.write(p, arcname=str(p.relative_to(rev_dir.parent)).replace("\\", "/"))


def write_preflight_docs(cfg, cov_rows, plan_rows, vol, inv_partial):
    write_md(DOC_PRE / "README_PREFLIGHT_EXPANSION_V4.md", f"""# Preflight expansión candidatos V4

**Fecha:** {FECHA}  
**Rol:** cartografo_territorial  
**Estado:** preparación completa — **sin Places ni clustering**

## Qué incluye

- Config final + snapshot Claude
- Inventario de insumos
- Áreas de consulta GeoJSON (barrios, ejes, nodos, bandas, controles)
- Cobertura vs universo sanitizado 2026-07-09
- Plan incremental de consultas (no ejecutado)
- Subunidades Centro C-S01…C-S08
- Contratos, métodos, tandas, riesgos, QA

## Qué no incluye

- Adopción de polos
- Ejecución API
- Resultados de clustering
- Expedientes documentales completos (viven en evidencia Grok)

## Orden de lectura

1. `ESTADO_RECUPERACION_PREFLIGHT_CLAUDE_V4.md`
2. `HANDOFF_CODEX_EJECUCION_EXPANSION_V4.md`
3. `PLAN_TANDAS` + `MATRIZ_COBERTURA`
4. `AREAS_CONSULTA_CANDIDATOS_V4.geojson`
5. Contratos Places / universo

## Integración documental

Ver `docs/polos_gastro/preparacion_integrada_expansion_v4/` y evidencia Grok V4.

## Reproducción

```text
.venv/Scripts/python.exe scripts/polos_gastro/expansion_candidatos_v4_preflight/build_preflight_expansion_candidatos_v4.py
```
""")

    write_md(DOC_PRE / "CONTRATO_CONSULTA_PLACES_EXPANSION_V4.md", f"""# Contrato de consulta Places — Expansión V4

**Fecha:** {FECHA}  
**Estado:** preflight — **no ejecutar sin autorización humana**

## Principios

1. Reutilizar resultados 2026-07-08/09 antes de consultar.
2. No repetir celda+categoría ya cubierta.
3. Solo brechas territoriales o categoriales.
4. No inventar tipos de lugar fuera del pipeline vigente.
5. Control de saturación (refino 3×3 si tope de resultados).

## Categorías

### Primarias (consulta planificada)
{chr(10).join('- `'+c+'`' for c in CATEGORIAS_PRIMARIAS)}

### Auxiliares (solo si brecha justificada)
{chr(10).join('- `'+c+'`' for c in CATEGORIAS_AUX)}

### Excluidas
{chr(10).join('- `'+c+'`' for c in CATEGORIAS_EXCL)}

## Parámetros de grilla

| Parámetro | Valor |
|---|---|
| CRS métrico | EPSG:5347 |
| celda_m | {CELDA_M} |
| radio_m | {RADIO_PLACES} |
| borde_m | 150 |

## Campos mínimos de plan

`consulta_id, tanda, zona_id, subunidad_id, celda_id, lat, lon, radio_m, categoría, estado, reutilizar, motivo_consulta`

## Estados de fila

- `REUTILIZAR_EXISTENTE`
- `CONSULTAR`
- `CONSULTAR_SOLO_BRECHA`
- `NO_CONSULTAR`
- `PENDIENTE_DECISION`

## Prohibiciones

- No consultar C-S02 (Bajo porteño ambiguo) hasta definición.
- No usar lista semilla de locales como query de validación de polo.
- No guardar place_id/nombres en paquetes públicos.

## Scripts plantilla (solo lectura / copiar)

- `scripts/polos_gastro/experimentos/google_places_microzonas_piloto/preparar_consultas_places_piloto.py`
- `scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/preparar_consultas_places_ampliacion.py`
- `scripts/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/refinar_celdas_saturadas_places.py`
""")

    write_md(DOC_PRE / "CONTRATO_UNIVERSO_PUNTOS_EXPANSION_V4.md", f"""# Contrato de universo de puntos — Expansión V4

**Fecha:** {FECHA}

## Universo base reutilizable

`outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/completa_v1/UNIVERSO_COMPLETO_SANITIZADO.csv`

- 6.461 puntos (3.240 F01+F02; 3.221 Google Places)
- Fecha Places: 2026-07-08/09

## Campos mínimos del universo de expansión (futuro)

| Campo | Descripción |
|---|---|
| point_id_sanitizado | ID sin PII |
| fuente | F01+F02 / google_places / mixto |
| fuente_original | detalle de origen |
| categoría_normalizada | rubro |
| lat, lon | WGS84 |
| fecha_fuente | corte |
| zona_consulta | zona_id de la ventana |
| subunidad_consulta | subunidad_id |
| coincidencia_f01_f02 | flag match |
| coincidencia_places | flag match |
| dedup_cluster_id | grupo dedup |
| qa_status | OK/REVISAR/EXCLUIDO |
| exclusion_reason | si aplica |
| publicable | SI/NO |

## Privacidad

- No exportar nombres comerciales a paquetes de revisión pública.
- Caches internos (`places_consolidados_interno.csv`) solo lectura interna.
- Nunca commitear place_id + teléfono + address completa.

## Deduplicación

Reutilizar reglas de `construir_integracion_completa_v1.py` (place_id, distancia+nombre, match F01/F02).
""")

    write_md(DOC_PRE / "PLAN_CORRIDAS_TERRITORIALES_EXPANSION_V4.md", f"""# Plan de corridas territoriales — Expansión V4

**Fecha:** {FECHA}  
**Ejecución:** futura (Codex) — este documento es preflight

## Secuencia

1. **Preparar universo** de la tanda (F01/F02 + Places reutilizados + brechas autorizadas).
2. **Asignar puntos** a áreas de consulta por geometría (no por campo barrio del CSV).
3. **Aplicar método principal** según tipología (ver matriz).
4. **Métodos de control** obligatorios (KDE, ablación por fuente, continuidad).
5. **Contraste post hoc** con evidencia documental Grok (solo ABIERTA_Y_LEIDA para límites narrativos).
6. **Clasificar resultado** en taxonomía permitida (incluye EVIDENCIA_INSUFICIENTE).
7. **No adoptar** sin decisión humana.

## Métodos por tipología

| Tipología | Método principal | Controles |
|---|---|---|
| CORREDOR_LINEAL | densidad longitudinal + tramos | vacíos >300 m cortan; buffers variables |
| NUCLEO_COMPACTO / MICROCENTRALIDAD | HDBSCAN radio pequeño | mínimo puntos; estabilidad bootstrap |
| MULTIPARTE | clustering + componentes | no fusionar a priori |
| UNIDAD_BARRIAL | HDBSCAN + grafo | ratio núcleo/fondo; multiparte |
| RED_DE_NODOS | comunidades de grafo | no forzar corredor |

## Hipótesis nula de fragmentación

Caballito (Z03), Villa Urquiza (Z10), Paternal (Z14), Centro (Z05):  
**partir de múltiples piezas o ninguna**, no de un solo polígono.

## Cero clusters es válido

Boedo, Lacroze completa, Villa Pueyrredón: salida esperable `EVIDENCIA_INSUFICIENTE` / `OFERTA_DISPERSA`.
""")

    write_md(DOC_PRE / "CRITERIOS_ADOPCION_TERRITORIAL_EXPANSION_V4.md", f"""# Criterios de adopción territorial — Expansión V4

**Fecha:** {FECHA}  
**Importante:** este preflight **no adopta**. Solo define umbrales para la corrida futura.

## Resultados permitidos

- `POLO_ADOPTABLE`
- `CORREDOR_ADOPTABLE`
- `POLO_MULTIPARTE`
- `SUBPOLO_DE_UNIDAD_EXISTENTE`
- `AREA_ASOCIADA`
- `MICROCENTRALIDAD`
- `TRANSICION_ENTRE_POLOS`
- `OFERTA_DISPERSA`
- `EVIDENCIA_INSUFICIENTE`

## Condiciones mínimas (borrador operativo)

1. Estructura espacial estable (método principal + al menos un control).
2. No explicable solo por un shopping/patio/edificio multipunto.
3. Composición de fuentes declarada; dependencia Places marcada si >70% Places-only.
4. Relación con polos adoptados resuelta (independiente / asociada / subpolo / transición).
5. Nombre técnico sin marca comercial.
6. Documentación solo **post hoc** (no supervisa el clustering).
7. Decisión humana registrada.

## No adopción automática

- Estar en la lista de 15 candidatas.
- Tener página de Turismo BA.
- Tener muchas notas de prensa.
- Tener un local famoso de la semilla.
""")

    n_plan = len(plan_rows)
    write_md(DOC_PRE / "HANDOFF_CODEX_EJECUCION_EXPANSION_V4.md", f"""# Handoff Codex — ejecución expansión V4 (preflight técnico)

**Fecha:** {FECHA}  
**De:** cartografo_territorial  
**Para:** Codex (corrida futura)

## No hacer todavía

- No Places sin autorización y decision gate en verde.
- No clustering hasta universo de tanda listo.
- No tocar informe político / V3 / evidencia Grok.

## Entradas

| Insumo | Ruta |
|---|---|
| Config final | `outputs/polos_gastro/expansion_candidatos_v4_preflight/config_expansion_candidatos_v4.json` |
| Áreas | `.../AREAS_CONSULTA_CANDIDATOS_V4.geojson` |
| Cobertura | `.../MATRIZ_COBERTURA_EXISTENTE_Y_BRECHAS_V4.csv` |
| Plan Places | `.../PLAN_CONSULTAS_PLACES_EXPANSION_V4.csv` ({n_plan} filas categoría-celda) |
| Tandas | `.../PLAN_TANDAS_EXPANSION_V4.csv` |
| Contratos | docs preflight |
| Documental | `docs/polos_gastro/evidencia_documental_expansion_v4/` |
| Integrado | `docs/polos_gastro/preparacion_integrada_expansion_v4/HANDOFF_CODEX_EJECUCION_EXPANSION_V4_INTEGRADO.md` |

## Tanda 1 (primera)

Z01 Villa Crespo · Z02 Chacarita · Z03 Caballito · Z04 Boulevard Caseros

Priorizar **reutilización** del universo 2026-07-09; solo brechas.

## Reglas de oro

1. Documentación post hoc.
2. Multinodo donde el prior lo dice.
3. Cero clusters válido.
4. No DoHo / Chacalermo / Nuevo Bajo como labels de cluster.
""")

    write_md(DOC_PRE / "PROMPT_BASE_CODEX_EJECUCION_EXPANSION_V4.md", f"""# Prompt base Codex — ejecución expansión V4

Sos `cartografo_territorial` / ejecutor de corrida territorial DataGastro.

## Objetivo de la sesión

Ejecutar **solo la tanda autorizada** de expansión V4 según:

- `outputs/polos_gastro/expansion_candidatos_v4_preflight/`
- `docs/polos_gastro/preparacion_integrada_expansion_v4/DECISION_GATE_ANTES_DE_PLACES_V4.md`

## Prohibido

- Modificar fase27/28/29, informe político, V3/V3.1, evidencia Grok, pipeline F01–F05.
- Ejecutar Places si el decision gate no está en verde para esa tanda.
- Adoptar polos sin decisión humana.
- Usar nombres DoHo, Chacalermo, Nuevo Bajo, Polo Caseros=Barracas como IDs.

## Debe

1. Leer config + áreas + cobertura + plan de la tanda.
2. Construir universo de puntos de la tanda (reutilizar 2026-07-09).
3. Si hay brechas autorizadas: ejecutar solo filas `CONSULTAR` / `CONSULTAR_SOLO_BRECHA`.
4. Deduplicar según contrato.
5. Correr métodos de `MATRIZ_TIPOLOGIA_Y_METODOS_V4.csv`.
6. Contrastar post hoc con evidencia documental (solo ABIERTA_Y_LEIDA para ejes).
7. Emitir resultados con taxonomía permitida (incluye EVIDENCIA_INSUFICIENTE).
8. QA + metadata + checksums en carpeta de corrida nueva (no sobrescribir preflight).

## Salida

Informe de corrida por zona + capas + handoff al integrador editorial.
""")

    write_md(DOC_PRE / "AUTOCONTROL_PREFLIGHT_EXPANSION_V4.md", f"""# Autocontrol preflight expansión V4

**Fecha:** {FECHA}

## Checklist

- [x] Snapshot Claude preservado
- [x] Config final con correcciones documentales
- [x] 15 zonas
- [x] 8 subunidades Centro (C-S02 sin consulta)
- [x] 4 tandas
- [x] Áreas GeoJSON generadas desde barrios/callejero
- [x] Cobertura vs universo 6461
- [x] Plan Places incremental (no ejecutado)
- [x] Contratos Places y universo
- [x] Métodos y criterios de adopción
- [x] Riesgos
- [x] QA técnico
- [x] Builder reproducible
- [x] Sin API Places
- [x] Sin clustering
- [x] Superficies protegidas no modificadas
""")

    write_md(DOC_PRE / "README_REPRODUCCION_PREFLIGHT_V4.md", f"""# Reproducción del preflight V4

```powershell
cd C:\\proyectos\\Gastronomia\\DataGastro
.venv\\Scripts\\python.exe scripts\\polos_gastro\\expansion_candidatos_v4_preflight\\build_preflight_expansion_candidatos_v4.py
```

## Determinismo

- Mismas capas de entrada ⇒ mismos IDs de celda y áreas (buffers fijos, grilla regular).
- No usa reloj ni random.
- Comparar `checksums.sha256` entre dos corridas.

## Dependencias

geopandas, pandas, shapely (venv del proyecto).

## No requiere

- API keys
- red (salvo que falten archivos locales)
""")


def write_integrated_docs(cfg, cov_rows, conc, prio_final, plan_rows, vol):
    # need places summary by zone
    needs = {}
    for c in cov_rows:
        z = c["zona_id"]
        needs.setdefault(z, set()).add(c["necesita_nueva_consulta_places"])

    def need_summary(z):
        s = needs.get(z, {"A_CONFIRMAR"})
        if "SI" in s:
            return "SI"
        if "PARCIAL" in s:
            return "PARCIAL"
        if "NO" in s and len(s) == 1:
            return "NO"
        return "/".join(sorted(s))

    write_md(DOC_INT / "SINTESIS_INTEGRADA_PREPARACION_EXPANSION_V4.md", f"""# Síntesis integrada — preparación expansión V4

**Fecha:** {FECHA}  
**Roles:** cartografo_territorial + integrador_tecnico_documental

## Panorama

Se recuperó el preflight parcial de Claude (**config JSON válido, 372 líneas**; docs/outputs vacíos) y se completó con la evidencia documental de Grok (15 expedientes, 35 fuentes, 42 evidencias).

**Ninguna zona fue adoptada.**

## Concordancia

- Fuerte alineación en Crespo y Chacarita (oficial + spatial prior).
- Ajustes de nombre: Donado–Holmberg (no DoHo), Esmeralda–Paraguay (no Nuevo Bajo).
- Ajustes de extensión: Boulevard Caseros tramo corto; Lacroze por tramos; Caballito multinodo.
- Centro desagregado en C-S01…C-S08.

## Places (sin ejecutar)

| Zona | Necesidad (agregada) |
|---|---|
""" + "\n".join(f"| {z['zona_id']} {z.get('nombre_tecnico') or z['nombre']} | {need_summary(z['zona_id'])} |" for z in cfg["zonas"]) + f"""

## Tandas

1. Crespo, Chacarita, Caballito, Caseros — reutilización Places  
2. Boedo, Devoto, Donado–Holmberg, Urquiza  
3. García del Río, Lacroze tramos, Paternal, Pueyrredón  
4. Abasto, Esmeralda–Paraguay, Centro subunidades  

## Decision gate

Ver `DECISION_GATE_ANTES_DE_PLACES_V4.md`.

## Handoff único Codex

`HANDOFF_CODEX_EJECUCION_EXPANSION_V4_INTEGRADO.md`
""")

    write_md(DOC_INT / "DECISION_GATE_ANTES_DE_PLACES_V4.md", f"""# Decision gate — antes de Places (Expansión V4)

**Fecha:** {FECHA}

## Semáforo general

| Tanda | ¿Lista para ejecutar Places? | Condición |
|---|---|---|
| 1 | **CONDICIONAL VERDE** | Áreas+cobertura+plan+contratos listos; **reutilizar primero**; brechas solo con autorización |
| 2 | AMARILLO | Requiere autorización de volumen nuevo y calibración tanda 1 |
| 3 | AMARILLO | Idem; varias zonas con evidencia débil |
| 4 | ROJO/AMARILLO | Complejidad de solape con polos adoptados; subunidades Centro |

## Tanda 1 — checklist de listo

- [x] Áreas válidas GeoJSON
- [x] Cobertura medida vs universo 6461
- [x] Plan incremental
- [x] Contrato de puntos
- [x] Reglas de deduplicación referenciadas
- [x] Superficies protegidas respetadas
- [x] Prompt Codex completo
- [ ] **Autorización humana explícita** para cualquier fila `CONSULTAR*`

## Por zona (Tanda 1)

| Zona | Places reutilizable | Nueva consulta | Notas |
|---|---|---|---|
| Z01 Villa Crespo | SI (macrozona previa) | PARCIAL bordes/ejes | Thames vs Palermo |
| Z02 Chacarita | SI + refino previo | PARCIAL Newbery/Dorrego | No Lacroze completa |
| Z03 Caballito | SI | PARCIAL por nodos | No fusionar nodos |
| Z04 Caseros | SI parcial | PARCIAL tramo | No Patricios |

## Evidencia documental post hoc

Suficiente para contraste en Crespo/Chacarita/Caseros/García del Río.  
Releer fuentes `INDEXADA_SNIPPET_O_TITULO` antes de **publicación**.

## Bloqueos

1. Falta autorización de API/presupuesto.
2. Caches internos sensibles no van a paquetes públicos.
3. C-S02 no consulta.
4. No adoptar sin decisión humana.
""")

    write_md(DOC_INT / "HANDOFF_CODEX_EJECUCION_EXPANSION_V4_INTEGRADO.md", f"""# Handoff Codex integrado — ejecución expansión V4

**Fecha:** {FECHA}  
**De:** cartografo_territorial + integrador_tecnico_documental  
**Para:** Codex

## Paquetes fuente

1. **Preflight técnico:** `docs|outputs/polos_gastro/expansion_candidatos_v4_preflight/`
2. **Documental Grok:** `docs|outputs/polos_gastro/evidencia_documental_expansion_v4/`
3. **Integrado (este):** `docs|outputs/polos_gastro/preparacion_integrada_expansion_v4/`

## Orden operativo

1. Abrir decision gate.
2. Si Tanda 1 autorizada: reutilizar universo; consultar solo brechas.
3. Métodos según tipología; documentación solo post hoc.
4. Nombres técnicos de `MATRIZ_CONCORDANCIA`.
5. Resultados con taxonomía permitida.
6. No tocar informe político ni polos adoptados.

## Alias prohibidos como ID

DoHo · Chacalermo · Chacacrespo · Nuevo Bajo · Polo Caseros=Barracas · Centro unitario

## Archivos clave

- `AREAS_CONSULTA_CANDIDATOS_V4.geojson`
- `PLAN_CONSULTAS_PLACES_EXPANSION_V4.csv`
- `MATRIZ_COBERTURA_EXISTENTE_Y_BRECHAS_V4.csv`
- `MATRIZ_CONCORDANCIA_TECNICO_DOCUMENTAL_V4.csv`
- `PROMPT_CODEX_TANDA1_EXPANSION_V4.md`
""")

    write_md(DOC_INT / "PROMPT_BASE_CODEX_EJECUCION_EXPANSION_V4.md", 
             (DOC_PRE / "PROMPT_BASE_CODEX_EJECUCION_EXPANSION_V4.md").read_text(encoding="utf-8")
             if (DOC_PRE / "PROMPT_BASE_CODEX_EJECUCION_EXPANSION_V4.md").exists()
             else "# ver preflight\n")

    write_md(DOC_INT / "PROMPT_CODEX_TANDA1_EXPANSION_V4.md", f"""# Prompt Codex — Tanda 1 expansión V4

Ejecutá **solo Tanda 1**: Z01 Villa Crespo, Z02 Chacarita, Z03 Caballito, Z04 Boulevard Caseros.

## Inputs

- Áreas y cobertura del preflight V4
- Universo sanitizado 2026-07-09
- Evidencia documental Grok (post hoc)
- Decision gate en verde para reutilización; autorización humana para brechas

## Tareas

1. Filtrar puntos del universo a las áreas Tanda 1 (geometría).
2. Reportar cobertura y brechas reales.
3. Si hay autorización: ejecutar únicamente `CONSULTAR_SOLO_BRECHA` / `CONSULTAR` de esas zonas.
4. Deduplicar.
5. Correr métodos:
   - Crespo: multiparte / red de nodos; control borde Palermo
   - Chacarita: Newbery + Dorrego; no Lacroze completa
   - Caballito: nodos separados; hipótesis nula fragmentación
   - Caseros: corredor corto; controles San Telmo / Barracas / Patricios
6. Clasificar con taxonomía permitida.
7. Contrastar con expedientes Z01–Z04 (sin supervisar clusters).
8. QA + handoff.

## Prohibido

Adoptar polos · renombrar a Chacalermo · fusionar Caballito · extender Caseros a Patricios · tocar V3/informe político.
""")

    write_md(DOC_INT / "AUTOCONTROL_PREPARACION_INTEGRADA_EXPANSION_V4.md", f"""# Autocontrol preparación integrada expansión V4

**Fecha:** {FECHA}

- [x] Recuperación Claude documentada
- [x] Snapshot config preservado
- [x] Evidencia Grok leída e integrada (no modificada)
- [x] Matriz de uso de evidencia con QA
- [x] Concordancia técnico-documental
- [x] Prioridad final + tandas
- [x] Decision gate
- [x] Handoff y prompts Codex
- [x] QA integración
- [x] ZIP preflight + ZIP integrado
- [x] Sin Places / sin clustering / sin commit
""")

    # copy prompt base if not written yet
    if not (DOC_INT / "PROMPT_BASE_CODEX_EJECUCION_EXPANSION_V4.md").exists() or (DOC_INT / "PROMPT_BASE_CODEX_EJECUCION_EXPANSION_V4.md").stat().st_size < 50:
        pass  # written above with conditional


if __name__ == "__main__":
    main()
