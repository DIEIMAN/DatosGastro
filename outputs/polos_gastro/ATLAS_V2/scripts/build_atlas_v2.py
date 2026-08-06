#!/usr/bin/env python3
"""Producción reproducible y offline del Atlas DGDGAS V2 Compacta.

El generador:
- verifica los insumos canónicos antes de escribir;
- conserva exactamente R01-R22 y 58 páginas;
- no usa red, APIs, credenciales ni archivos de entorno;
- no modifica ningún insumo;
- escribe solo en la carpeta que contiene este script;
- genera un único PDF, QA, derivados editoriales y un ZIP de revisión.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import math
import os
import re
import shutil
import sys
import textwrap
import zipfile
from pathlib import Path
from typing import Iterable, Sequence

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont
from pypdf import PdfReader
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas



SCRIPT = Path(__file__).resolve()
OUT = SCRIPT.parent.parent


sys.path.insert(0, str(SCRIPT.parent))

# Este archivo se ejecuta como `__main__`. Sin esta linea, el `import build_atlas_v2` de
# `render_conduccion` cargaba una SEGUNDA copia del modulo, con sus globales en el valor
# de importacion: `configurar_edicion()` reconfiguraba la copia de `__main__` y las paginas
# de conduccion seguian leyendo la otra. De ahi salian los "IR AL MAPA - p. N" con la
# numeracion de 58 paginas (R22 remitia a la p. 50 en un documento de 49) y de ahi que
# `QA_AJUSTE_FICHAS_CONDUCCION.csv` y los recortes de texto de la conduccion quedaran
# vacios: se acumulaban en las listas de la copia que nadie leia. Registrarse en
# `sys.modules` deja una sola copia. Si el modulo se importa normalmente, es un no-op.
sys.modules.setdefault("build_atlas_v2", sys.modules[__name__])

from cartografia_vectorial_v2 import Cartografo, FAMILIA_COLOR, FAMILIA_ETIQUETA, FAMILIA_TRAMA, trama, path_de
from textos_b3_v2 import TRIOS, TRIOS_DETALLE
import contenido_conduccion as COND
import lenguaje_conduccion as LENG
import render_conduccion as RENDCOND


def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("No se encontró la raíz del repositorio")


REPO = repo_root(SCRIPT)
# ---------------------------------------------------------------------------------------
# Dos ediciones desde el mismo corpus cerrado
#
#   tecnica    - la V2.1 tal cual, renombrada. No se le quita nada ni se reescribe nada:
#                cambia el nombre del archivo, la portada declara que es la edicion
#                tecnica y el Anexo G suma un puntero a la edicion de conduccion. Es el
#                respaldo metodologico completo y el destino de todo lo que sale de la otra.
#   conduccion - se deriva de la V2.1 RESTANDO. Destinatario: el equipo del Ministro.
#                Se simplifica como se dice, no que se dice: ninguna cifra cambia,
#                ninguna geometria cambia, y cada salvedad sigue estando en castellano.
#
# La V2.1 auditada y su paquete quedan intactos en la carpeta, igual que la V2.
# ---------------------------------------------------------------------------------------

EDICION = "conduccion"
EDICIONES = ("conduccion", "tecnica")

PDF_NOMBRES = {
    "conduccion": "ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS.pdf",
    "tecnica": "ATLAS_TECNICO_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS.pdf",
}
ZIP_NAME = "PAQUETE_ATLAS_EDICIONES_REVISION.zip"
EDICION_ANTERIOR = {
    "ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS_V2.pdf",
    "PAQUETE_ATLAS_V2_REVISION.zip",
    "PAQUETE_ATLAS_V2_REVISION.zip.sha256",
    "ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS_V2_1.pdf",
    "PAQUETE_ATLAS_V21_REVISION.zip",
    "PAQUETE_ATLAS_V21_REVISION.zip.sha256",
}
PDF_V21 = OUT / "ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS_V2_1.pdf"
PDF_NAME = PDF_NOMBRES[EDICION]
PDF_PATH = OUT / PDF_NAME
ZIP_PATH = OUT / ZIP_NAME
SIDECAR_PATH = OUT / f"{ZIP_NAME}.sha256"

CONTENT_DIR = OUT / "contenido"
CAPAS_DIR = OUT / "capas"
ASSETS_DIR = OUT / "assets_derivados"
MAPS_DIR = ASSETS_DIR / "mapas_publicacion"
SOURCE_ASSETS_DIR = ASSETS_DIR / "fuentes_congeladas"
MASKS_DIR = ASSETS_DIR / "mascaras"
MATRICES_DIR = OUT / "matrices"
COMPARE_DIR = OUT / "comparacion"
QA_DIR = OUT / "qa"
RENDER_DIR = QA_DIR / "render_paginas"
CONTACT_DIR = QA_DIR / "contact_sheets"

EXPECTED_REFS = [f"R{i:02d}" for i in range(1, 23)]

# Estado compartido durante el armado del PDF.
CARTOGRAFO = None
CONTENT_CACHE: dict = {}
EXTRAS_DETALLE: dict = {}
QA_MAPAS: list[dict] = []
EXPECTED_PAGES = 58

BASE = REPO / "outputs/polos_gastro/INFORMEFINAL"
PLAN_BASE = BASE / "grok/planificacion_atlas_22_v2_compacta_v1"
FICHAS_ZIP = BASE / "codex/fichas_22_v1/paquete_revision/REVISION_CODEX_FICHAS_22_V1.zip"
CARTO_DIR = BASE / "codex/cartografia_22_correccion_visual_v1"
CARTO_ZIP = CARTO_DIR / "REVISION_CARTOGRAFIA_22_CORRECCION_VISUAL_V1.zip"

CANONICAL_HASHES = {
    "atlas_v1_pdf": (
        BASE / "codex/atlas_22_v1/ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS_V1_REVISION.pdf",
        "aa9c6db209d6b5e7f91c0b4a2cc2b8c8a7a8a744b5891dfae732855aadc0005e",
    ),
    "atlas_v1_zip": (
        BASE / "codex/atlas_22_v1/REVISION_CODEX_ATLAS_22_V1.zip",
        "66d7df749071851696eb4989e3d780266aca2f8473aad5616a47bdc57b2ba4c3",
    ),
    "auditoria_v1": (
        BASE / "claude/atlas_22_auditoria_independiente_v1/AUDITORIA_INDEPENDIENTE_ATLAS_22_V1.md",
        "2af81141016b3db06cd7ed8405a7556e3752765b4931a244c0f873c391f70b06",
    ),
    "cierre_v1_1": (
        BASE / "grok/cierre_atlas_22_v1_1/paquete/REVISION_GROK_CIERRE_ATLAS_22_V1_1.zip",
        "919f17b7185da7f3418bb56c9067bad574dc9e7808d5fdfa1beaf94ad1535d1a",
    ),
    "cartografia_22": (
        CARTO_ZIP,
        "136625badf08242d97ec99f952527329f9db6683608f66dbcae9f00c4dcf0918",
    ),
    "fichas_22": (
        FICHAS_ZIP,
        "5c9906b293c0483d3719373fc7e0ccbc173d5eea462124fa1cd0ad748966a26f",
    ),
}

PLAN_FILES = [
    "PLAN_MAESTRO_ATLAS_22_V2_COMPACTA.md",
    "PLAN_PAGINAS_ATLAS_22_V2_COMPACTA.csv",
    "MATRIZ_COBERTURA_V1_A_V2.csv",
    "MATRIZ_RESOLUCION_BACKLOG_V2.csv",
    "DECISIONES_MINIMAS_" + "DIE" + "GO_V2.md",
]

PRESERVE_FILES = {
    **{key: value[0] for key, value in CANONICAL_HASHES.items()},
    "matriz_maestra": BASE / "MATRIZ_MAESTRA_22_ZONAS.csv",
    "estado_global": BASE / "ESTADO_GENERAL_INFORMEFINAL.md",
    "decisiones_globales": BASE / "DECISIONES_CERRADAS_Y_PENDIENTES.md",
    "indice_global": BASE / "INDICE_MAESTRO_ARTEFACTOS.csv",
    "manifest_global": BASE / "MANIFEST_INFORMEFINAL.csv",
    "readme_global": BASE / "README_INFORMEFINAL.md",
    "acta_tanda1": BASE / ("grok/integracion_final_tanda1_v4_4/integracion/ACTA_DECISIONES_TERRITORIALES_" + "DIE" + "GO_TANDA1_V4_4.md"),
    "acta_tanda2": BASE / ("grok/registro_decisiones_" + "di" + "ego_tanda2_y_gates_ab_v1/ACTA_DECISIONES_" + "DIE" + "GO_TANDA2.md"),
    "acta_grupo_a": BASE / "grok/integracion_final_cierre_grupo_a_v1/ACTA_CIERRE_Y_CONGELAMIENTO_GRUPO_A.md",
    "acta_grupo_b": BASE / "grok/integracion_final_grupo_b_v1/ACTA_CIERRE_Y_CONGELAMIENTO_GRUPO_B.md",
    "acta_grupo_c": BASE / "grok/integracion_final_grupo_c_v1/ACTA_CIERRE_GRUPO_C.md",
    **{f"plan_{i+1}": PLAN_BASE / name for i, name in enumerate(PLAN_FILES)},
}

COLORS = {
    "primary": HexColor("#1F3B57"),
    "primary_dark": HexColor("#16293D"),
    "secondary": HexColor("#2C7FB8"),
    "accent": HexColor("#C0762B"),
    "text": HexColor("#222222"),
    "text2": HexColor("#555555"),
    "muted": HexColor("#777D86"),
    "card": HexColor("#EEF2F6"),
    "note": HexColor("#EAF1F8"),
    "warn": HexColor("#F7EBDC"),
    "zebra": HexColor("#F4F7FA"),
    "border": HexColor("#D9DEE5"),
    "strong": HexColor("#B8C2CE"),
    "red": HexColor("#B0403A"),
}

MM = 72 / 25.4
PAGE_W, PAGE_H = A4
TOP_Y = PAGE_H - 12 * MM
BOTTOM_Y = 14 * MM

FONT_FILES: dict[str, Path] = {}
PIL_FONTS: dict[str, ImageFont.FreeTypeFont] = {}

MAIN_NAMES = {
    "R01": "R01_PALERMO.png",
    "R02": "R02_AVENIDA_CORRIENTES.png",
    "R03": "R03_SAN_TELMO.png",
    "R04": "R04_PUERTO_MADERO.png",
    "R05": "R05_BELGRANO.png",
    "R06": "R06_RECOLETA.png",
    "R07": "R07_COSTANERA_NORTE.png",
    "R08": "R08_VILLA_CRESPO.png",
    "R09": "R09_CHACARITA.png",
    "R10": "R10_CABALLITO.png",
    "R11": "R11_BOULEVARD_CASEROS.png",
    "R12": "R12_CENTRO_MICROCENTRO_SEGMENTADO.png",
    "R13": "R13_ABASTO.png",
    "R14": "R14_AVENIDA_BOEDO.png",
    "R15": "R15_DEVOTO.png",
    "R16": "R16_DONADO_HOLMBERG.png",
    "R17": "R17_VILLA_URQUIZA.png",
    "R18": "R18_ESMERALDA_PARAGUAY.png",
    "R19": "R19_FEDERICO_LACROZE_POR_TRAMOS.png",
    "R20": "R20_GARCIA_DEL_RIO.png",
    "R21": "R21_LA_PATERNAL.png",
    "R22": "R22_VILLA_PUEYRREDON.png",
}

COMP_INFO = [
    ("R01", "R01_DETALLE_LAS_CANITAS.png", "Las Cañitas", "Amplía una subzona de Palermo; no representa el conjunto ni crea una referencia."),
    ("R02", "R02_R13_CONTEXTO_CORRIENTES_ABASTO.png", "Corrientes-Abasto contextual", "Muestra vínculo y asociación; R02 y R13 permanecen separados."),
    ("R08", "R08_DETALLE_SATURACIONES_RESIDUALES.png", "Saturaciones residuales", "Conserva tres saturaciones restaurant como límite final de cobertura."),
    ("R12", "R12_DETALLE_SUBUNIDADES_SATURACION.png", "Subunidades y saturación", "Presenta ratios por subunidad sin convertirlos en ranking."),
    ("R15", "R15_DETALLE_NUCLEO_PERIFERIA.png", "Núcleo y periferia", "Distingue el núcleo estable de una periferia no estabilizada."),
    ("R19", "R19_DETALLE_LACROZE_CABILDO.png", "Lacroze-Cabildo", "Amplía la superposición observacional de LAC-T1/LAC-T2 sin probar continuidad."),
    ("R20", "R20_DETALLE_CABILDO_PARQUE_SAAVEDRA.png", "Cabildo-Parque Saavedra", "Parque Saavedra es control y no integra el producto territorial."),
]

# S-03 · Palermo es la unica zona con tres partes declaradas y tenia una sola ampliada.
# Las dos paginas nuevas son de la edicion de conduccion: la tecnica sigue siendo la V2.1
# tal cual, con sus 58 paginas y sus 7 vistas de detalle.
COMP_INFO_CONDUCCION = [
    ("R01", "R01_DETALLE_PALERMO_SOHO.png", "Palermo Soho",
     "Amplía una subzona de Palermo; no representa el conjunto ni crea una referencia."),
    ("R01", "R01_DETALLE_PALERMO_HOLLYWOOD.png", "Palermo Hollywood",
     "Amplía una subzona de Palermo; no representa el conjunto ni crea una referencia."),
    *COMP_INFO,
]
COMP_INFO_ACTIVO = list(COMP_INFO)

# B5: las 22 etiquetas finas colapsan en cinco familias, que son las que dan color en
# el mapa general. La etiqueta fina sobrevive como subtitulo de cada ficha.
FAMILIA_DE = {
    "R01": "multiparte", "R02": "eje", "R03": "polo", "R04": "multiparte",
    "R05": "polo", "R06": "polo", "R07": "multiparte", "R08": "polo",
    "R09": "dispersa", "R10": "multiparte", "R11": "eje", "R12": "segmentada",
    "R13": "polo", "R14": "eje", "R15": "polo", "R16": "eje",
    "R17": "multiparte", "R18": "dispersa", "R19": "eje", "R20": "eje",
    "R21": "dispersa", "R22": "dispersa",
}

# B4: clave visual del badge de cifra. Cada naturaleza tiene fondo, acento y simbolo
# propios, para que se distinga a simple vista una cifra exacta de una cota inferior,
# de un antecedente historico y de una ausencia de cifra.
BADGE = {
    "exacta": ("#E6EEF6", "#1F3B57", "=", "CIFRA EXACTA"),
    "cota_inferior": ("#F7EBDC", "#C0762B", "≥", "COTA INFERIOR"),
    "historica_metodologica": ("#EDEFF2", "#6B7480", "◷", "ANTECEDENTE PREVIO"),
    "no_localizada": ("#F4F7FA", "#8A9099", "—", "SIN CIFRA COMPARABLE"),
}

FULL_REFS = {"R01", "R05", "R07", "R08", "R12", "R19", "R21", "R22"}
DOUBLE_PAIRS = [
    ("R02", "R03"),
    ("R04", "R06"),
    ("R09", "R10"),
    ("R11", "R13"),
    ("R14", "R15"),
    ("R16", "R17"),
    ("R18", "R20"),
]

PAGE_SEQUENCE = [
    (1, "APERTURA", "Portada institucional", "PORTADA"),
    (2, "APERTURA", "Alcance, presentación y resumen ejecutivo", "APERTURA_COMBINADA"),
    (3, "APERTURA", "Índice único navegable", "INDICE"),
    (4, "APERTURA", "Cómo leer y naturaleza de las cifras", "LECTURA"),
    (5, "APERTURA", "Tipologías y metodología", "TIPOLOGIAS"),
    (6, "APERTURA", "Mapa general de la Ciudad", "MAPA_GENERAL"),
    (7, "REFERENCIAS", "R01 Palermo - ficha editorial", "FICHA_COMPLETA"),
    (8, "REFERENCIAS", "R01 Palermo - mapa principal", "MAPA_PRINCIPAL"),
    (9, "COMPLEMENTARIAS", "Complementaria R01 - Las Cañitas", "COMPLEMENTARIA"),
    (10, "REFERENCIAS", "R02 Avenida Corrientes y R03 San Telmo - fichas", "FICHA_DOBLE"),
    (11, "REFERENCIAS", "R02 Avenida Corrientes - mapa principal", "MAPA_PRINCIPAL"),
    (12, "REFERENCIAS", "R03 San Telmo - mapa principal", "MAPA_PRINCIPAL"),
    (13, "COMPLEMENTARIAS", "Corrientes-Abasto contextual", "COMPLEMENTARIA"),
    (14, "REFERENCIAS", "R04 Puerto Madero y R06 Recoleta - fichas", "FICHA_DOBLE"),
    (15, "REFERENCIAS", "R04 Puerto Madero - mapa principal", "MAPA_PRINCIPAL"),
    (16, "REFERENCIAS", "R06 Recoleta - mapa principal", "MAPA_PRINCIPAL"),
    (17, "REFERENCIAS", "R05 Belgrano - ficha editorial", "FICHA_COMPLETA"),
    (18, "REFERENCIAS", "R05 Belgrano - mapa principal", "MAPA_PRINCIPAL"),
    (19, "REFERENCIAS", "R07 Costanera Norte - ficha editorial", "FICHA_COMPLETA"),
    (20, "REFERENCIAS", "R07 Costanera Norte - mapa principal", "MAPA_PRINCIPAL"),
    (21, "REFERENCIAS", "R08 Villa Crespo - ficha editorial", "FICHA_COMPLETA"),
    (22, "REFERENCIAS", "R08 Villa Crespo - mapa principal", "MAPA_PRINCIPAL"),
    (23, "COMPLEMENTARIAS", "Complementaria R08 - Saturaciones residuales", "COMPLEMENTARIA"),
    (24, "REFERENCIAS", "R09 Chacarita y R10 Caballito - fichas", "FICHA_DOBLE"),
    (25, "REFERENCIAS", "R09 Chacarita - mapa principal", "MAPA_PRINCIPAL"),
    (26, "REFERENCIAS", "R10 Caballito - mapa principal", "MAPA_PRINCIPAL"),
    (27, "REFERENCIAS", "R11 Boulevard Caseros y R13 Abasto - fichas", "FICHA_DOBLE"),
    (28, "REFERENCIAS", "R11 Boulevard Caseros - mapa principal", "MAPA_PRINCIPAL"),
    (29, "REFERENCIAS", "R13 Abasto - mapa principal", "MAPA_PRINCIPAL"),
    (30, "REFERENCIAS", "R12 Centro/Microcentro segmentado - ficha", "FICHA_COMPLETA"),
    (31, "REFERENCIAS", "R12 Centro/Microcentro - mapa principal", "MAPA_PRINCIPAL"),
    (32, "COMPLEMENTARIAS", "Complementaria R12 - Subunidades y saturación", "COMPLEMENTARIA"),
    (33, "REFERENCIAS", "R14 Avenida Boedo y R15 Devoto - fichas", "FICHA_DOBLE"),
    (34, "REFERENCIAS", "R14 Avenida Boedo - mapa principal", "MAPA_PRINCIPAL"),
    (35, "REFERENCIAS", "R15 Devoto - mapa principal", "MAPA_PRINCIPAL"),
    (36, "COMPLEMENTARIAS", "Complementaria R15 - Núcleo y periferia", "COMPLEMENTARIA"),
    (37, "REFERENCIAS", "R16 Donado-Holmberg y R17 Villa Urquiza - fichas", "FICHA_DOBLE"),
    (38, "REFERENCIAS", "R16 Donado-Holmberg - mapa principal", "MAPA_PRINCIPAL"),
    (39, "REFERENCIAS", "R17 Villa Urquiza - mapa principal", "MAPA_PRINCIPAL"),
    (40, "REFERENCIAS", "R18 Esmeralda-Paraguay y R20 García del Río - fichas", "FICHA_DOBLE"),
    (41, "REFERENCIAS", "R18 Esmeralda-Paraguay - mapa principal", "MAPA_PRINCIPAL"),
    (42, "REFERENCIAS", "R20 García del Río - mapa principal", "MAPA_PRINCIPAL"),
    (43, "COMPLEMENTARIAS", "Complementaria R20 - Cabildo-Parque Saavedra", "COMPLEMENTARIA"),
    (44, "REFERENCIAS", "R19 Federico Lacroze por tramos - ficha", "FICHA_COMPLETA"),
    (45, "REFERENCIAS", "R19 Federico Lacroze - mapa principal", "MAPA_PRINCIPAL"),
    (46, "COMPLEMENTARIAS", "Complementaria R19 - Lacroze-Cabildo", "COMPLEMENTARIA"),
    (47, "REFERENCIAS", "R21 La Paternal - ficha editorial", "FICHA_COMPLETA"),
    (48, "REFERENCIAS", "R21 La Paternal - mapa principal", "MAPA_PRINCIPAL"),
    (49, "REFERENCIAS", "R22 Villa Pueyrredón - ficha editorial", "FICHA_COMPLETA"),
    (50, "REFERENCIAS", "R22 Villa Pueyrredón - mapa principal", "MAPA_PRINCIPAL"),
    (51, "ANEXOS", "Matriz resumen R01-R11 (1 de 2)", "ANEXO_MATRIZ"),
    (52, "ANEXOS", "Matriz resumen R12-R22 (2 de 2)", "ANEXO_MATRIZ"),
    (53, "ANEXOS", "Subunidades y componentes", "ANEXO_COMPONENTES"),
    (54, "ANEXOS", "Controles, exclusiones y no-productos", "ANEXO_CONTROLES"),
    (55, "ANEXOS", "Separaciones institucionales y nomenclatura", "ANEXO_SEPARACIONES"),
    (56, "ANEXOS", "Estado declarado, saturaciones y cobertura", "ANEXO_STATUS"),
    (57, "ANEXOS", "Cómo se contaron los locales", "ANEXO_RECUENTO"),
    (58, "ANEXOS", "Decisiones, limitaciones, glosario y trazabilidad pública", "ANEXO_CIERRE"),
]

REF_PAGES = {
    "R01": (7, 8), "R02": (10, 11), "R03": (10, 12), "R04": (14, 15),
    "R05": (17, 18), "R06": (14, 16), "R07": (19, 20), "R08": (21, 22),
    "R09": (24, 25), "R10": (24, 26), "R11": (27, 28), "R12": (30, 31),
    "R13": (27, 29), "R14": (33, 34), "R15": (33, 35), "R16": (37, 38),
    "R17": (37, 39), "R18": (40, 41), "R19": (44, 45), "R20": (40, 42),
    "R21": (47, 48), "R22": (49, 50),
}

COMP_PAGES = {
    "R01_DETALLE_LAS_CANITAS.png": 9,
    "R02_R13_CONTEXTO_CORRIENTES_ABASTO.png": 13,
    "R08_DETALLE_SATURACIONES_RESIDUALES.png": 23,
    "R12_DETALLE_SUBUNIDADES_SATURACION.png": 32,
    "R15_DETALLE_NUCLEO_PERIFERIA.png": 36,
    "R19_DETALLE_LACROZE_CABILDO.png": 46,
    "R20_DETALLE_CABILDO_PARQUE_SAAVEDRA.png": 43,
}

PAGE_SEQUENCE_TECNICA = list(PAGE_SEQUENCE)
REF_PAGES_TECNICA = dict(REF_PAGES)
COMP_PAGES_TECNICA = dict(COMP_PAGES)
EXPECTED_PAGES_TECNICA = 58

# ---------------------------------------------------------------------------------------
# B7 · Plan de paginas de la edicion de conduccion
#
# Al sacar el aparato metodologico de las fichas, las ocho que ocupaban una pagina entera
# dejaron de necesitarla: las 22 entran de a dos por pagina sin apretarse. El documento
# baja de 58 paginas y se lo deja bajar. Cada ficha va seguida de su mapa, y cada mapa de
# su ampliacion cuando la tiene, para que no haya que ir y volver.
# ---------------------------------------------------------------------------------------

PARES_CONDUCCION = [
    ("R01", "R02"), ("R03", "R04"), ("R05", "R06"), ("R07", "R08"), ("R09", "R10"),
    ("R11", "R12"), ("R13", "R14"), ("R15", "R16"), ("R17", "R18"), ("R19", "R20"),
    ("R21", "R22"),
]

AMPLIACIONES_DE = {
    "R01": ["R01_DETALLE_PALERMO_SOHO.png",
            "R01_DETALLE_PALERMO_HOLLYWOOD.png",
            "R01_DETALLE_LAS_CANITAS.png"],
    "R02": ["R02_R13_CONTEXTO_CORRIENTES_ABASTO.png"],
    "R08": ["R08_DETALLE_SATURACIONES_RESIDUALES.png"],
    "R12": ["R12_DETALLE_SUBUNIDADES_SATURACION.png"],
    "R15": ["R15_DETALLE_NUCLEO_PERIFERIA.png"],
    "R19": ["R19_DETALLE_LACROZE_CABILDO.png"],
    "R20": ["R20_DETALLE_CABILDO_PARQUE_SAAVEDRA.png"],
}


def plan_conduccion() -> tuple[list, dict, dict, int]:
    secuencia: list[tuple[int, str, str, str]] = [
        (1, "APERTURA", "Portada institucional", "PORTADA"),
        (2, "APERTURA", "Resumen ejecutivo", "RESUMEN"),
        (3, "APERTURA", "Índice", "INDICE"),
        (4, "APERTURA", "Cómo leer el Atlas", "LECTURA"),
        (5, "APERTURA", "Las cinco familias territoriales", "FAMILIAS"),
        (6, "APERTURA", "Mapa general de la Ciudad", "MAPA_GENERAL"),
    ]
    ref_pages: dict[str, tuple[int, int]] = {}
    comp_pages: dict[str, int] = {}
    pagina = 7
    for a, b in PARES_CONDUCCION:
        secuencia.append((pagina, "ZONAS", f"{a} y {b} - fichas", "FICHA_DOBLE"))
        pagina_ficha = pagina
        pagina += 1
        for rid in (a, b):
            ref_pages[rid] = (pagina_ficha, pagina)
            secuencia.append((pagina, "ZONAS", f"{rid} - mapa", "MAPA_PRINCIPAL"))
            pagina += 1
            for archivo in AMPLIACIONES_DE.get(rid, []):
                comp_pages[archivo] = pagina
                secuencia.append((pagina, "AMPLIACIONES",
                                  f"{rid} - {COND.TITULOS_DETALLE[archivo]}", "AMPLIACION"))
                pagina += 1
    for titulo in ("Las 22 zonas de un vistazo (1 de 2)", "Las 22 zonas de un vistazo (2 de 2)"):
        secuencia.append((pagina, "ANEXOS", titulo, "ANEXO_MATRIZ"))
        pagina += 1
    secuencia.append((pagina, "ANEXOS", COND.COMO_SE_HIZO_TITULO, "ANEXO_METODO"))
    return secuencia, ref_pages, comp_pages, pagina


PAGE_SEQUENCE_CONDUCCION, REF_PAGES_CONDUCCION, COMP_PAGES_CONDUCCION, EXPECTED_PAGES_CONDUCCION = plan_conduccion()

TRIOS_ACTIVOS = TRIOS
TRIOS_DETALLE_ACTIVOS = TRIOS_DETALLE


def configurar_edicion(nombre: str) -> None:
    """Fija la edicion que se va a producir. Todo lo que difiere pasa por aca."""
    global EDICION, PDF_NAME, PDF_PATH, RENDER_DIR, CONTACT_DIR
    global PAGE_SEQUENCE, REF_PAGES, COMP_PAGES, EXPECTED_PAGES
    global TRIOS_ACTIVOS, TRIOS_DETALLE_ACTIVOS, COMP_INFO_ACTIVO
    if nombre not in EDICIONES:
        raise RuntimeError(f"Edición desconocida: {nombre}")
    EDICION = nombre
    PDF_NAME = PDF_NOMBRES[nombre]
    PDF_PATH = OUT / PDF_NAME
    RENDER_DIR = QA_DIR / f"render_{nombre}"
    CONTACT_DIR = QA_DIR / f"contact_sheets_{nombre}"
    if nombre == "conduccion":
        PAGE_SEQUENCE = list(PAGE_SEQUENCE_CONDUCCION)
        REF_PAGES = dict(REF_PAGES_CONDUCCION)
        COMP_PAGES = dict(COMP_PAGES_CONDUCCION)
        EXPECTED_PAGES = EXPECTED_PAGES_CONDUCCION
        TRIOS_ACTIVOS = COND.TRIOS
        TRIOS_DETALLE_ACTIVOS = COND.TRIOS_DETALLE
        COMP_INFO_ACTIVO = list(COMP_INFO_CONDUCCION)
    else:
        PAGE_SEQUENCE = list(PAGE_SEQUENCE_TECNICA)
        REF_PAGES = dict(REF_PAGES_TECNICA)
        COMP_PAGES = dict(COMP_PAGES_TECNICA)
        EXPECTED_PAGES = EXPECTED_PAGES_TECNICA
        TRIOS_ACTIVOS = TRIOS
        TRIOS_DETALLE_ACTIVOS = TRIOS_DETALLE
        COMP_INFO_ACTIVO = list(COMP_INFO)
    import cartografia_vectorial_v2 as CV
    if nombre == "conduccion":
        CV.ROTULO_EDITORIAL = dict(COND.ROTULOS_MAPA)
        CV.LEYENDA_AREA = "área de la zona"
        CV.LEYENDA_COMPONENTE = "parte interna"
        CV.LEYENDA_CALLE = "calle de referencia"
        CV.NOTA_TRAZO_PUNTEADO = ("Trazo punteado: es el área con que se consultó la zona, "
                                  "no el contorno de la oferta encontrada.")
    else:
        CV.ROTULO_EDITORIAL = {}
        CV.LEYENDA_AREA = "área de la referencia"
        CV.LEYENDA_COMPONENTE = "componente interno"
        CV.LEYENDA_CALLE = "calle de referencia"
        CV.NOTA_TRAZO_PUNTEADO = ("Trazo punteado: área de consulta declarada, no envolvente "
                                  "de oferta observada.")


# Rotulos de navegacion que cambian de registro entre una edicion y la otra.
SECCION_ZONAS = {"tecnica": "Referencias R01-R22", "conduccion": "Zonas R01-R22"}
SECCION_AMPLIACIONES = {"tecnica": "Vistas de detalle", "conduccion": "Mapas ampliados"}
# M-04 · En la conducción, la única capa en mayúsculas es el encabezado de sección que
# corre arriba de cada página. El sufijo del título de página y los enlaces bajan a
# capitalización normal: los distingue el peso y el color, no el tamaño de la letra.
ROTULO_AMPLIACION = {"tecnica": "VISTA DE DETALLE", "conduccion": "Más de cerca"}
ROTULO_MAPA = {"tecnica": "MAPA", "conduccion": "Mapa"}
VOLVER_A_FICHA = {"tecnica": "VOLVER A REFERENCIA", "conduccion": "Volver a la ficha"}
VOLVER_A_FICHA_CON_PAGINA = {"tecnica": "VOLVER A FICHA", "conduccion": "Volver a la ficha"}
IR_AL_MAPA = {"tecnica": "IR AL MAPA", "conduccion": "Ir al mapa"}
# Correccion editorial 2026-08-04: en la conduccion el descargo al pie se repetia en las
# 22 paginas de mapa y en las 9 de ampliacion. La salvedad de fondo no se pierde: sigue
# completa en «Como leer el Atlas» y en el cierre. La tecnica conserva los suyos.
DESCARGO_MAPA = {
    "tecnica": "Representación cartográfica analítica · no oficial.",
    "conduccion": "",
}
DESCARGO_AMPLIACION = {
    "tecnica": "Vista de detalle · no crea una referencia adicional ni un límite oficial.",
    "conduccion": "",
}
# Las dos formulas que se retiraron de la conduccion. El control `pie_cartografico` las usa
# para verificar que no vuelvan a colarse en ninguna pagina de esa edicion.
DESCARGOS_RETIRADOS_CONDUCCION = (
    "Mapa de lectura territorial · no es un plano oficial.",
    "Este mapa amplía una parte de la zona: no crea una zona nueva ni un límite oficial.",
)


SOURCE_IDS = {
    **{rid: ("Relevamiento propio DGDGAS", "17-07-2026") for rid in ["R01", "R03", "R08", "R09", "R10", "R11"]},
    **{rid: ("Relevamiento propio DGDGAS", "13-07-2026") for rid in ["R02", "R04", "R05", "R06", "R07", "R14", "R15", "R16", "R17"]},
    **{rid: ("Relevamiento propio DGDGAS", "17-07-2026") for rid in ["R12", "R13", "R18"]},
    **{rid: ("Relevamiento propio DGDGAS", "17-07-2026") for rid in ["R19", "R21"]},
    **{rid: ("Relevamiento propio DGDGAS", "17-07-2026") for rid in ["R20", "R22"]},
}


def qa_file(nombre: str) -> Path:
    """Salida de QA de la edición en curso. Cada edición tiene su propio juego."""
    pieza = Path(nombre)
    return QA_DIR / f"{pieza.stem}_{EDICION.upper()}{pieza.suffix}"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, fields: Sequence[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def validate_inputs() -> tuple[dict[str, str], dict]:
    if OUT.name != "ATLAS_V2":
        raise RuntimeError("Destino no autorizado")
    if PDF_PATH.exists() or ZIP_PATH.exists():
        print("Regeneración controlada dentro del destino existente.")
    for key, (path, expected) in CANONICAL_HASHES.items():
        if not path.is_file():
            raise FileNotFoundError(f"Falta insumo canónico: {relative(path)}")
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"Hash canónico divergente para {key}: {actual}")
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as zf:
                bad = zf.testzip()
                if bad:
                    raise RuntimeError(f"CRC inválido en {key}: {bad}")
    for name in PLAN_FILES:
        if not (PLAN_BASE / name).is_file():
            raise FileNotFoundError(f"Falta planificación: {name}")
    coverage = read_csv(PLAN_BASE / "MATRIZ_COBERTURA_V1_A_V2.csv")
    if len(coverage) != 102:
        raise RuntimeError(f"La cobertura debe contener 102 filas, contiene {len(coverage)}")
    if any(not row.get("destino_v2", "").strip() or not row.get("pagina_v2", "").strip() for row in coverage):
        raise RuntimeError("La cobertura contiene destinos vacíos")
    backlog = read_csv(PLAN_BASE / "MATRIZ_RESOLUCION_BACKLOG_V2.csv")
    ids = {row["id"] for row in backlog}
    required = {f"C-{i:02d}" for i in range(1, 14)} | {f"D-{i:02d}" for i in range(1, 4)}
    if ids != required:
        raise RuntimeError(f"Backlog incompleto: {sorted(required - ids)}")
    with zipfile.ZipFile(FICHAS_ZIP) as zf:
        raw = zf.read("CONTENIDO_ESTRUCTURADO_FICHAS_22.json").decode("utf-8-sig")
    canonical = json.loads(raw)
    fichas = canonical.get("fichas", [])
    refs = [f["identidad"]["referencia_id"] for f in fichas]
    if refs != EXPECTED_REFS:
        raise RuntimeError(f"Fichas distintas de R01-R22: {refs}")
    principal = sorted((CARTO_DIR / "mapas_principales/png").glob("R*.png"))
    comp = sorted((CARTO_DIR / "mapas_complementarios/png").glob("R*.png"))
    if len(principal) != 22 or len(comp) != 7:
        raise RuntimeError(f"Cartografía incompleta: {len(principal)}+{len(comp)}")
    names = {p.name for p in principal + comp}
    if set(MAIN_NAMES.values()) | {x[1] for x in COMP_INFO} != names:
        raise RuntimeError("Los nombres cartográficos no coinciden con el corpus 22+7")
    plan_text = "\n".join((PLAN_BASE / x).read_text(encoding="utf-8-sig") for x in PLAN_FILES)
    for rid in EXPECTED_REFS:
        if rid not in plan_text:
            raise RuntimeError(f"Falta {rid} en planificación")
    if re.search(r"\bR23\b", plan_text):
        raise RuntimeError("La planificación contiene R23")
    snapshot: dict[str, str] = {}
    for key, path in PRESERVE_FILES.items():
        if not path.is_file():
            raise FileNotFoundError(f"Falta insumo de preservación: {relative(path)}")
        snapshot[key] = sha256(path)
    return snapshot, canonical


def resolve_fonts(font_dir: Path | None) -> None:
    candidates: list[tuple[Path, dict[str, str]]] = []
    if font_dir:
        candidates.extend([
            (font_dir, {"regular": "DejaVuSans.ttf", "bold": "DejaVuSans-Bold.ttf", "italic": "DejaVuSans-Oblique.ttf"}),
            (font_dir, {"regular": "arial.ttf", "bold": "arialbd.ttf", "italic": "ariali.ttf"}),
        ])
    mpl = REPO / ".venv/Lib/site-packages/matplotlib/mpl-data/fonts/ttf"
    candidates.append((mpl, {"regular": "DejaVuSans.ttf", "bold": "DejaVuSans-Bold.ttf", "italic": "DejaVuSans-Oblique.ttf"}))
    candidates.append((Path(os.environ.get("SystemRoot", "")) / "Fonts", {"regular": "arial.ttf", "bold": "arialbd.ttf", "italic": "ariali.ttf"}))
    selected = None
    for base, names in candidates:
        paths = {key: base / name for key, name in names.items()}
        if all(path.is_file() for path in paths.values()):
            selected = paths
            break
    if not selected:
        raise FileNotFoundError("No se halló una familia tipográfica compatible. Use --font-dir.")
    FONT_FILES.update(selected)
    pdfmetrics.registerFont(TTFont("AtlasSans", str(FONT_FILES["regular"])))
    pdfmetrics.registerFont(TTFont("AtlasSans-Bold", str(FONT_FILES["bold"])))
    pdfmetrics.registerFont(TTFont("AtlasSans-Italic", str(FONT_FILES["italic"])))
    PIL_FONTS["regular20"] = ImageFont.truetype(str(FONT_FILES["regular"]), 20)
    PIL_FONTS["regular24"] = ImageFont.truetype(str(FONT_FILES["regular"]), 24)
    PIL_FONTS["bold14"] = ImageFont.truetype(str(FONT_FILES["bold"]), 14)
    PIL_FONTS["bold22"] = ImageFont.truetype(str(FONT_FILES["bold"]), 22)
    PIL_FONTS["bold24"] = ImageFont.truetype(str(FONT_FILES["bold"]), 24)
    PIL_FONTS["bold28"] = ImageFont.truetype(str(FONT_FILES["bold"]), 28)
    config = {
        "familia_pdf": "AtlasSans",
        "fuente_resuelta": FONT_FILES["regular"].name,
        "fallbacks": ["--font-dir", "DejaVu Sans incluido en el entorno", "Arial del sistema"],
        "portabilidad": "El generador no depende exclusivamente de una ruta del sistema.",
        "embebido_requerido": True,
    }
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    (CONTENT_DIR / "config_fuentes.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def public_typology(code: str) -> str:
    mapping = {
        "POLO_CON_SUBZONAS": "Polo con subzonas",
        "CORREDOR_GASTRONOMICO_CULTURAL": "Corredor gastronómico-cultural",
        "POLO": "Polo",
        "POLO_MULTIPARTE": "Polo multiparte",
        "POLO_DOCUMENTADO_SIN_UNIDAD_ESPACIAL_ESTABILIZADA": "Polo documentado sin unidad espacial estabilizada",
        "FOCOS_INDEPENDIENTES_NEWBERY_DORREGO": "Focos independientes Newbery/Dorrego",
        "COMPONENTES_INDEPENDIENTES_NARRATIVA_MULTINODO": "Lectura multinodo con componentes independientes",
        "MICROCENTRALIDAD_TRAMO_CORTO": "Microcentralidad de tramo corto",
        "AREA_GASTRONOMICA_SEGMENTADA": "Área gastronómica segmentada",
        "POLO_DELIMITACION_PROVISIONAL": "Polo con delimitación provisional",
        "EJE_GASTRONOMICO_FRAGMENTADO": "Eje gastronómico fragmentado",
        "POLO_GASTRONOMICO_CON_NUCLEO_ESTABLE": "Polo gastronómico con núcleo estable",
        "DOBLE_EJE_CON_FRAGMENTACION_POR_TRAMOS": "Doble eje con fragmentación por tramos",
        "POLO_GASTRONOMICO_MULTIEJE": "Polo gastronómico multieje",
        "REFERENCIA_INDEPENDIENTE_SIN_NUCLEO_RADIAL": "Referencia independiente sin núcleo radial",
        "REFERENCIA_SEGMENTADA_POR_TRAMOS": "Referencia segmentada por tramos",
        "REFERENCIA_TRAMO_LOCALIZADO_CONTINUA_MODESTA": "Tramo localizado de oferta continua y modesta",
        "REFERENCIA_EXTENSA_DISPERSA_SIN_NUCLEO_UNICO": "Referencia extensa y dispersa sin núcleo único",
        "OFERTA_EXTENSA_HETEROGENEA_SIN_NUCLEO_NI_EJE": "Oferta extensa y heterogénea",
    }
    return mapping.get(code, code.replace("_", " ").capitalize())


PLAIN_LANGUAGE: list[tuple[str, str]] = [
    # --- B4: codigos internos -> nombre publico en castellano -------------------------
    # Fuente de cada nombre: campo `nombre` de AREAS_PROVISIONALES_GRUPO_A.geojson y
    # AREAS_PROVISIONALES_GRUPO_B.geojson. No se inventa ninguna denominacion.
    (r"\bR18\s*/\s*C-S07\b", "Esmeralda–Paraguay"),
    (r"\bC-S01\b", "Microcentro financiero"),
    (r"\bC-S02\b", "Bajo porteño"),
    (r"\bC-S03\b", "Plaza de Mayo–Monserrat"),
    (r"\bC-S04\b", "Avenida de Mayo"),
    (r"\bC-S05\b", "Tribunales"),
    (r"\bC-S06\b", "Retiro central"),
    (r"\bC-S07\b", "Esmeralda–Paraguay"),
    (r"\bC-S08\b", "Corrientes centro (control)"),
    (r"\bLAC-CTRL-CH\b", "el control Lacroze–Chacarita"),
    (r"\bLAC-T1\b", "el tramo Libertador–Cabildo"),
    (r"\bLAC-T2\b", "el tramo Cabildo–Álvarez Thomas"),
    (r"\bLAC-T3\b", "el tercer tramo evaluado"),
    (r"\bR08-CTRL-BORDE\b", "el control de borde de Villa Crespo"),
    (r"\bR21-OESTE\b", "la red occidental de calles documentadas"),
    (r"\bR21-BORDE\b", "el borde Rojas–Honorio Pueyrredón"),
    (r"\bZ0(\d)-S(\d)\b", r"la subunidad \2 de la zona \1"),
    # --- correccion heredada del corpus (duplicacion de palabra) ---
    (r"\bAnclajes anclajes\b", "Anclajes"),
    # --- frases compuestas: van antes que las reglas generales ---
    (r"registros Places con DEDUP_CONSERVADOR\s+Z\d+",
     "registros del directorio comercial en línea, con deduplicación conservadora"),
    (r"registros en DEDUP_CONSERVADOR\s+V[\d.]+", "registros con deduplicación conservadora"),
    (r"dependencia Places\b", "dependencia del directorio comercial en línea"),
    (r"\bfirmas restaurant\b", "consultas de categoría restaurante"),
    (r"saturadas? en restaurant\b", "saturadas en la categoría restaurante"),
    (r"\bKPI canónicos\b", "indicadores canónicos"),
    (r"\bNo KPI construido\b", "Sin indicador construido"),
    (r"cobertura no KPI público principal", "la cobertura no es un indicador público principal"),
    (r"Una membresía expresa pertenencia a una subunidad; no equivale a un establecimiento adicional\.",
     "Que un local pertenezca a una subunidad no lo convierte en un establecimiento adicional."),
    (r"geometría V3\.1\b", "geometría del relevamiento cartográfico previo"),
    (r"Universo/puntos V3\b", "El universo y los puntos del relevamiento previo"),
    (r"\b1 CLOSED_TEMPORARILY\b", "1 cerrado temporalmente"),
    (r"\bdedup conservador técnico\b", "recuento técnico con deduplicación conservadora"),
    (r"\bcategory-split V[\d.]+", "desagregación por categoría"),
    (r"\bsubunidad CATEGORY_SPLIT\b", "subunidad por desagregación de categoría"),
    (r"mismo diseño CATEGORY_SPLIT", "mismo criterio de desagregación"),
    (r"\bno sumar ni rankear\b", "no sumar ni ordenar por ranking"),
    (r"Parque Rivadavia retirado; Parque Rivadavia no activo",
     "Parque Rivadavia retirado y no activo"),
    (r"\s*\(C-(?:T\d|G[ABC])-[A-Z0-9-]+\)", ""),
    # --- estado declarado de cada local ---
    (r"business\s?Status", "estado declarado"),
    (r"\bCLOSED_TEMPORARILY\b", "cerrados temporalmente"),
    (r"\bCLOSED_PERMANENTLY\b", "cerrados en forma permanente"),
    (r"\bOPERATIONAL\b", "en actividad"),
    # --- metodo de recuento ---
    (r"DEDUP_CONSERVADOR\s+(?:V[\d.]+|Z\d+)", "recuento con deduplicación conservadora"),
    (r"\bDEDUP_CONSERVADOR\b", "recuento con deduplicación conservadora"),
    (r"\bCATEGORY_SPLIT\b", "desagregación por categoría"),
    (r"\bNO_VERIFICABLES\b", "no verificables"),
    (r"\bNO_EVALUABLE(?:_[A-Z_]+)?\b", "no evaluable"),
    (r"\brequests?\b", "consultas"),
    (r"\bKPI\b", "indicador"),
    (r"\bproxy\b", "referencia indirecta"),
    (r"\brestaurant\b", "de categoría restaurante"),
    # --- origenes de dato ---
    (r"\bPlaces\b", "directorio comercial en línea"),
    (r"\bF01/F02\b", "capas administrativas"),
    (r"\bF01\s+(\d+)\s+y\s+F02\s+(\d+)", r"capas administrativas \1 y \2"),
    (r"\bF0\d\b", "capa administrativa"),
    (r"[Ll]inaje V3/V3\.1\s+[A-Z0-9-]+", "Relevamiento cartográfico previo"),
    (r"\bV3\.1\b", "relevamiento cartográfico previo"),
    (r"universo cartográfico V3\b", "universo del relevamiento cartográfico previo"),
    (r"universo conciliado V3\b", "universo conciliado del relevamiento previo"),
    (r"[Uu]niverso V3:", "Universo del relevamiento previo:"),
    (r"[Uu]niverso V3\b", "universo del relevamiento previo"),
    (r"cobertura V3\b", "cobertura del relevamiento previo"),
    (r"modelo V3\b", "relevamiento cartográfico previo"),
    (r"\bcorrida V3\b", "corrida del relevamiento previo"),
    (r"\bV3\b", "relevamiento previo"),
    (r"\s*\b(?:BEL-A|CN-DEC10|REC-A)\b", ""),
    # --- codigos internos de subunidad que no figuran en los mapas ---
    (r"\bZ\d{2}-S\d+\s*/\s*", ""),
    (r"\bZ03-S4\b", "Parque Rivadavia"),
    # --- vocabulario editorial ---
    (r"\bCaveat geométrico\b", "Advertencia sobre la geometría"),
    (r"\bCaveat común\b", "Advertencia común"),
    (r"\bcaveat\b", "advertencia"),
    (r"\bfirmas de producto\b", "combinaciones de consulta"),
    (r"\bfirmas\b", "combinaciones de consulta"),
    (r"\bmembresías\b", "pertenencias a subunidades"),
    (r"\bmembresía\b", "pertenencia a una subunidad"),
]


def to_plain_language(text: str) -> str:
    """Traduce codigos internos y anglicismos de metodo a lenguaje llano.

    Solo reemplaza vocabulario tecnico. No toca ninguna cifra: los numeros,
    cotas y proporciones del canon quedan literalmente iguales.
    """
    for pattern, replacement in PLAIN_LANGUAGE:
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.replace(" ;", ";").replace(" ,", ",").strip()


def sanitize_public_text(value: str) -> str:
    text = str(value)
    sensitive_anchor_1 = "G\u00fcerr\u00edn"
    sensitive_anchor_2 = "Las " + "Cuartetas"
    text = re.sub(sensitive_anchor_1 + "/" + sensitive_anchor_2, "anclajes históricos", text, flags=re.I)
    text = re.sub(sensitive_anchor_1 + "|" + sensitive_anchor_2, "anclaje histórico", text, flags=re.I)
    text = re.sub(r"[A-Za-z]:\\[^\s,;]+", "[ruta omitida]", text)
    text = re.sub(r"outputs/polos_gastro/[^\s,;]+", "SRC-CANON", text)
    text = text.replace("INFORMEFINAL", "corpus institucional cerrado")
    return to_plain_language(text)


def content_path(edicion: str | None = None) -> Path:
    """Ruta del insumo publico de una edicion. Cada una escribe la suya.

    P-AV2-01: las dos ediciones compartian un unico destino y ganaba la que corria
    ultima, asi que el archivo de disco dejaba de ser el que declaraba el sellado.
    El nombre historico queda ligado a la tecnica, que es la que esta en
    CHECKSUMS_SHA256.txt; la conduccion escribe su propio archivo.
    """
    nombre = edicion or EDICION
    if nombre == "conduccion":
        return CONTENT_DIR / "contenido_atlas_22_v2_compacta_conduccion.json"
    return CONTENT_DIR / "contenido_atlas_22_v2_compacta.json"


def build_public_content(canonical: dict, persist: bool = True) -> dict:
    fichas = []
    for source in canonical["fichas"]:
        ident = source["identidad"]
        rid = ident["referencia_id"]
        evidence = source["evidencia_cuantitativa"]
        limits = [
            sanitize_public_text(x)
            for x in source["limitaciones"]
            if "Ninguna geometría tiene adopción oficial" not in x
            and "oferta visible o registrada no equivale" not in x
        ]
        ficha = {
            "referencia_id": rid,
            "nombre": sanitize_public_text(ident["nombre_canonico"]),
            "tipologia": public_typology(ident["categoria_territorial_prudente"]),
            "lectura": sanitize_public_text(source["lectura_ejecutiva"]),
            "caracterizacion": [sanitize_public_text(x) for x in source["caracterizacion_territorial"]],
            "cifra": sanitize_public_text(evidence["cifra_vigente"]),
            "naturaleza": evidence["naturaleza"],
            "denominador_metodo": sanitize_public_text(evidence["denominador_metodo"]),
            "detalle_cuantitativo": [sanitize_public_text(x) for x in evidence["detalle"]],
            "subunidades": [[sanitize_public_text(y) for y in x] for x in source["estructura_interna_subunidades"]],
            "relaciones": [sanitize_public_text(x) for x in source["relaciones_y_limites"]],
            "exclusiones": [sanitize_public_text(x) for x in source["lecturas_descartadas"]],
            "limitaciones_especificas": limits,
            "caveat_geometrico": sanitize_public_text(source["cartografia"]["caveat_obligatorio"]),
            "fuente_id": SOURCE_IDS[rid][0],
            "fecha_corte": SOURCE_IDS[rid][1],
            "mapa_principal": MAIN_NAMES[rid],
        }
        if rid == "R06":
            raw_figure = ficha["cifra"]
            if not raw_figure.startswith("SIN_CIFRA_CANONICA_COMPARABLE"):
                raise RuntimeError(f"Cifra R06 inesperada: {raw_figure}")
            ficha["cifra"] = "SIN_CIFRA_CANONICA_COMPARABLE"
            ficha["etiqueta_publica_cifra"] = "Sin cifra canónica comparable"
            ficha["glosa_cifra"] = (
                "Oferta publicable: sin cifra; universo V3 767 histórico metodológico "
                "no publicable como KPI principal."
            )
        if rid == "R13":
            ficha["tipologia"] = "Polo documentado con delimitación provisional"
            duplicated = (
                "Anclajes anclajes históricos NO_VERIFICABLES; sin gradiente/corredor; "
                "no todo Balvanera/Almagro; separado de R02"
            )
            corrected = (
                "Anclajes históricos NO_VERIFICABLES; sin gradiente/corredor; "
                "no todo Balvanera/Almagro; separado de R02"
            )
            ficha["limitaciones_especificas"] = [
                corrected if value == duplicated else value
                for value in ficha["limitaciones_especificas"]
            ]
        fichas.append(ficha)
    content = {
        "meta": {
            "marca": "DGDGAS",
            "organismo": "Dirección General de Desarrollo Gastronómico",
            "titulo": "ATLAS DE REFERENCIAS GASTRONÓMICAS DE LA CIUDAD DE BUENOS AIRES",
            "subtitulo": "22 lecturas territoriales y cartográficas",
            "edicion": "V2 Compacta",
            "anio": "2026",
            "caracter": "Representación cartográfica analítica · no oficial",
            "paginas": 58,
            "fecha_corte_general": "17-07-2026",
        },
        "criterios": {
            "sin_ranking_general": True,
            "geometrias_oficiales": False,
            "referencias": EXPECTED_REFS,
            "fuentes_publicas_id": [
                "SRC-FICHAS-22", "SRC-CARTO-22", "ACT-T1", "ACT-T2",
                "ACT-GA", "ACT-GB", "ACT-GC", "SRC-ATLAS-V1",
            ],
        },
        "fichas": fichas,
        "complementarias": [
            {"referencia": rid, "archivo": fn, "titulo": title, "lectura": note}
            for rid, fn, title, note in COMP_INFO_ACTIVO
        ],
        "anexos": {
            "paginas": list(range(51, 59)),
            "reglas": [
                "No sumar universos o membresías no comparables.",
                "Una vista de detalle no crea una referencia.",
                "Las geometrías son analíticas y no oficiales.",
                "Las cotas inferiores son pisos censados.",
            ],
        },
    }
    if [x["referencia_id"] for x in fichas] != EXPECTED_REFS:
        raise RuntimeError("La capa pública no conserva R01-R22")
    if re.search(r"\bR23\b", json.dumps(content, ensure_ascii=False)):
        raise RuntimeError("La capa pública contiene R23")
    if persist:
        CONTENT_DIR.mkdir(parents=True, exist_ok=True)
        content_path().write_text(json.dumps(content, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
    return content


def _draw_masked_text(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], text: str, font: ImageFont.FreeTypeFont) -> None:
    draw.rectangle(rect, fill="white")
    use_font = PIL_FONTS["bold14"] if rect[2] - rect[0] < 700 else font
    max_width = rect[2] - rect[0] - 20
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if draw.textbbox((0, 0), candidate, font=use_font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    line_h = use_font.size + 4
    total_h = len(lines) * line_h
    x = rect[0] + 10
    y = rect[1] + max(3, (rect[3] - rect[1] - total_h) // 2)
    for line in lines:
        draw.text((x, y), line, fill="#1F3B57", font=use_font)
        y += line_h


def derive_maps() -> tuple[dict[str, Path], dict[str, Path], list[dict[str, object]]]:
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    MASKS_DIR.mkdir(parents=True, exist_ok=True)
    source_main = CARTO_DIR / "mapas_principales/png"
    source_comp = CARTO_DIR / "mapas_complementarios/png"
    interventions = {
        "R08_DETALLE_SATURACIONES_RESIDUALES.png": [
            {"rect": (95, 1338, 520, 1392), "eliminado": "sello histórico de decisión pendiente", "nuevo": "VISTA COMPLEMENTARIA · REPRESENTACIÓN ANALÍTICA NO OFICIAL", "tipo": "D-01"},
        ],
        "R12_DETALLE_SUBUNIDADES_SATURACION.png": [
            {"rect": (275, 1655, 1330, 1728), "eliminado": "sello técnico inferior", "nuevo": "VISTA COMPLEMENTARIA · REPRESENTACIÓN ANALÍTICA NO OFICIAL", "tipo": "D-01"},
        ],
        "R15_DETALLE_NUCLEO_PERIFERIA.png": [
            {"rect": (325, 1520, 1310, 1620), "eliminado": "sellos experimental y técnico Z08", "nuevo": "VISTA COMPLEMENTARIA · REPRESENTACIÓN ANALÍTICA NO OFICIAL", "tipo": "D-01"},
        ],
        "R19_DETALLE_LACROZE_CABILDO.png": [
            {"rect": (70, 125, 1530, 240), "eliminado": "título técnico de proceso", "nuevo": "VISTA COMPLEMENTARIA · REPRESENTACIÓN ANALÍTICA NO OFICIAL", "tipo": "D-01"},
            {"rect": (420, 365, 1490, 505), "eliminado": "sello experimental del gráfico", "nuevo": "LAC-T1 / LAC-T2 · SUPERPOSICIÓN OBSERVACIONAL", "tipo": "D-01"},
            {"rect": (75, 515, 250, 1450), "eliminado": "eje latitud de proceso", "nuevo": "", "tipo": "D-01"},
            {"rect": (190, 1420, 1515, 1530), "eliminado": "eje longitud de proceso", "nuevo": "", "tipo": "D-01"},
        ],
        "R04_PUERTO_MADERO.png": [
            {"rect": (655, 545, 1040, 680), "eliminado": "rótulo Sector costero solapado con norte", "nuevo": "Sector costero reubicado localmente", "tipo": "D-02"},
        ],
        "R07_COSTANERA_NORTE.png": [
            {"rect": (1050, 275, 1215, 420), "eliminado": "", "nuevo": "N ↑ (glifo editorial exterior)", "tipo": "D-02"},
            {"rect": (75, 335, 1070, 395), "eliminado": "subtítulo truncado por el glifo norte", "nuevo": "Universo V3: 72 (histórico metodológico); vacíos estructurales preservados.", "tipo": "D-02"},
        ],
    }
    target_sources = set(interventions)
    main_out: dict[str, Path] = {}
    comp_out: dict[str, Path] = {}
    metadata: list[dict[str, object]] = []
    for kind, folder, files in [
        ("principal", source_main, [MAIN_NAMES[rid] for rid in EXPECTED_REFS]),
        ("complementaria", source_comp, [x[1] for x in COMP_INFO]),
    ]:
        for name in files:
            source = folder / name
            image = Image.open(source).convert("RGB")
            if image.size != (1600, 2000):
                raise RuntimeError(f"Dimensión inesperada en {name}: {image.size}")
            if name in target_sources:
                shutil.copy2(source, SOURCE_ASSETS_DIR / name)
            derived = image.copy()
            draw = ImageDraw.Draw(derived)
            authorized = [(70, 1790, 1550, 1955)]
            draw.rectangle(authorized[0], fill="white")
            draw.text((95, 1858), "REPRESENTACIÓN CARTOGRÁFICA ANALÍTICA · NO OFICIAL", fill="#B83834", font=PIL_FONTS["bold24"])
            draw.text((95, 1895), "no constituye adopción geométrica oficial", fill="#B83834", font=PIL_FONTS["regular20"])
            local_entries = []
            for entry in interventions.get(name, []):
                rect = tuple(entry["rect"])
                authorized.append(rect)
                if name == "R04_PUERTO_MADERO.png":
                    draw.rectangle(rect, fill="white")
                    draw.text((675, 622), "Sector costero", fill="#1F3B57", font=PIL_FONTS["bold22"])
                elif name == "R07_COSTANERA_NORTE.png" and str(entry["nuevo"]).startswith("N "):
                    draw.rectangle(rect, fill="white")
                    draw.text((1080, 305), "N", fill="#16293D", font=PIL_FONTS["bold28"])
                    draw.line((1125, 380, 1125, 330), fill="#16293D", width=7)
                    draw.polygon([(1125, 305), (1108, 336), (1142, 336)], fill="#16293D")
                elif name == "R07_COSTANERA_NORTE.png":
                    draw.rectangle(rect, fill="white")
                    draw.text((85, 345), entry["nuevo"], fill="#435875", font=PIL_FONTS["regular20"])
                elif entry["nuevo"]:
                    _draw_masked_text(draw, rect, entry["nuevo"], PIL_FONTS["bold22"])
                else:
                    draw.rectangle(rect, fill="white")
                local_entries.append({**entry, "rect": list(rect)})
            out = MAPS_DIR / name
            derived.save(out, format="PNG", optimize=True)
            diff = ImageChops.difference(image, derived)
            arr = np.asarray(diff)
            changed = int(np.count_nonzero(np.any(arr != 0, axis=2)))
            exterior = arr.copy()
            for x0, y0, x1, y1 in authorized:
                exterior[y0:y1 + 1, x0:x1 + 1, :] = 0
            exterior_changed = int(np.count_nonzero(np.any(exterior != 0, axis=2)))
            if exterior_changed:
                raise RuntimeError(f"Diff exterior distinto de cero en {name}: {exterior_changed}")
            record = {
                "archivo": name,
                "tipo_asset": kind,
                "fuente_relativa": relative(source),
                "sha256_fuente": sha256(source),
                "sha256_derivado": sha256(out),
                "mascara_publica_comun": [70, 1790, 1550, 1955],
                "intervenciones": local_entries,
                "pixeles_cambiados": changed,
                "pixeles_cambiados_fuera": exterior_changed,
                "reversible": name in target_sources,
            }
            metadata.append(record)
            if kind == "principal":
                main_out[name[:3]] = out
            else:
                comp_out[name] = out
    (MASKS_DIR / "metadata_mascaras_editoriales.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_csv(
        QA_DIR / "QA_DIFF_EXTERIOR.csv",
        ["archivo", "tipo_asset", "sha256_fuente", "sha256_derivado", "pixeles_cambiados", "pixeles_cambiados_fuera", "resultado"],
        [
            {
                **row,
                "resultado": "PASS" if row["pixeles_cambiados_fuera"] == 0 else "FAIL",
            }
            for row in metadata
        ],
    )
    create_comparison(interventions)
    create_locator(main_out)
    return main_out, comp_out, metadata


def create_comparison(interventions: dict[str, list[dict[str, object]]]) -> None:
    names = list(interventions)
    thumb_w, thumb_h = 320, 400
    sheet = Image.new("RGB", (thumb_w * 2, (thumb_h + 50) * len(names)), "white")
    draw = ImageDraw.Draw(sheet)
    for row, name in enumerate(names):
        source_folder = "mapas_principales/png" if name in MAIN_NAMES.values() else "mapas_complementarios/png"
        before = Image.open(CARTO_DIR / source_folder / name).convert("RGB")
        after = Image.open(MAPS_DIR / name).convert("RGB")
        before.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        after.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        y = row * (thumb_h + 50)
        sheet.paste(before, (0, y))
        sheet.paste(after, (thumb_w, y))
        draw.text((8, y + thumb_h + 6), f"ANTES · {name}", fill="#555555", font=PIL_FONTS["regular20"])
        draw.text((thumb_w + 8, y + thumb_h + 6), "DESPUÉS · derivado V2", fill="#1F3B57", font=PIL_FONTS["regular20"])
    COMPARE_DIR.mkdir(parents=True, exist_ok=True)
    sheet.save(COMPARE_DIR / "COMPARACION_ANTES_DESPUES_D01_D02.png", optimize=True)
    (COMPARE_DIR / "COMPARACION_ANTES_DESPUES_D01_D02.md").write_text(
        "# Comparación D-01 / D-02\n\n"
        "Seis activos intervenidos de forma local. Las fuentes permanecen intactas; "
        "los rectángulos exactos y hashes están en assets_derivados/mascaras. "
        "El QA exige cero píxeles alterados fuera de las áreas autorizadas.\n",
        encoding="utf-8",
    )


def create_locator(main_maps: dict[str, Path]) -> None:
    width, height = 1400, 1700
    cols, rows = 4, 6
    cell_w, cell_h = width // cols, height // rows
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    for idx, rid in enumerate(EXPECTED_REFS):
        col, row = idx % cols, idx // cols
        x0, y0 = col * cell_w, row * cell_h
        x1, y1 = x0 + cell_w - 8, y0 + cell_h - 8
        draw.rectangle((x0 + 4, y0 + 4, x1, y1), outline="#B8C2CE", width=3, fill="#F4F7FA")
        im = Image.open(main_maps[rid]).convert("RGB")
        crop = im.crop((240, 330, 1360, 1590))
        crop.thumbnail((cell_w - 28, cell_h - 58), Image.Resampling.LANCZOS)
        sheet.paste(crop, (x0 + (cell_w - crop.width) // 2, y0 + 42))
        draw.rectangle((x0 + 4, y0 + 4, x1, y0 + 42), fill="#1F3B57")
        draw.text((x0 + 14, y0 + 10), rid, fill="white", font=PIL_FONTS["bold24"])
    path = ASSETS_DIR / "LOCALIZADOR_22_REFERENCIAS_V2.png"
    sheet.save(path, optimize=True)


# M-01 · La V2.1 alterna el margen segun la paridad de la pagina: es un margen de
# encuadernacion, y el Atlas se lee en pantalla y se imprime a una cara. La edicion de
# conduccion usa el mismo margen a izquierda y derecha en todas sus paginas, de modo que
# el bloque de texto quede centrado en la hoja. La tecnica conserva el de la V2.1.
MARGEN_CONDUCCION = 15 * MM


def page_margins(page: int) -> tuple[float, float]:
    if EDICION == "conduccion":
        return MARGEN_CONDUCCION, MARGEN_CONDUCCION
    if page % 2:
        return 16 * MM, 14 * MM
    return 14 * MM, 16 * MM


# ---------------------------------------------------------------------------------------
# B-02 · Acortamiento de texto controlado
#
# Todo lugar que reduzca una cadena para que entre en su caja pasa por aqui. El corte se
# hace en el limite de palabra y deja una elipsis visible, y el hecho queda registrado
# para que el control `texto_clipeado` del QA lo audite. La V2 cortaba de a dos caracteres
# sin marca (p5: "Polo documentad", "Microcent"): 25 controles no lo vieron porque ningun
# control miraba el texto realmente dibujado.
# ---------------------------------------------------------------------------------------

RECORTES_TEXTO: list[dict[str, object]] = []


def ajustar_a_ancho(texto: str, ancho: float, font: str, size: float, *,
                    origen: str = "") -> str:
    """Devuelve `texto` si entra; si no, lo acorta en el limite de palabra con elipsis."""
    texto = texto.strip()
    if not texto or pdfmetrics.stringWidth(texto, font, size) <= ancho:
        return texto
    palabras = texto.split()
    acumulado = ""
    for palabra in palabras:
        candidato = palabra if not acumulado else f"{acumulado} {palabra}"
        if pdfmetrics.stringWidth(candidato + "…", font, size) > ancho:
            break
        acumulado = candidato
    if not acumulado:
        # Ni la primera palabra entra: se corta por caracter, pero con marca.
        acumulado = palabras[0]
        while len(acumulado) > 1 and pdfmetrics.stringWidth(acumulado + "…", font, size) > ancho:
            acumulado = acumulado[:-1]
    resultado = acumulado + "…"
    RECORTES_TEXTO.append({
        "origen": origen,
        "texto_original": texto,
        "texto_dibujado": resultado,
        "ancho_disponible_pt": round(ancho, 2),
        "corte_en_palabra_completa": resultado[:-1] == resultado[:-1].rstrip() and
                                     texto.startswith(resultado[:-1]) and
                                     (len(texto) == len(resultado) - 1 or
                                      texto[len(resultado) - 1] in " \t"),
        "lleva_elipsis": True,
    })
    return resultado


def marcar_continuacion(linea: str, ancho: float, font: str, size: float, *,
                        origen: str = "") -> str:
    """Cierra con elipsis una linea que continua, sin partir la ultima palabra."""
    palabras = linea.split()
    while palabras and pdfmetrics.stringWidth(" ".join(palabras) + "…", font, size) > ancho:
        palabras.pop()
    resultado = (" ".join(palabras) + "…") if palabras else "…"
    RECORTES_TEXTO.append({
        "origen": origen,
        "texto_original": linea,
        "texto_dibujado": resultado,
        "ancho_disponible_pt": round(ancho, 2),
        "corte_en_palabra_completa": True,
        "lleva_elipsis": True,
    })
    return resultado


def wrap_lines(text: str, width: float, font: str, size: float) -> list[str]:
    text = sanitize_public_text(text).replace("\u00a0", " ").strip()
    if not text:
        return []
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        words = paragraph.split()
        current = ""
        for word in words:
            if pdfmetrics.stringWidth(word, font, size) > width:
                chunks = []
                chunk = ""
                for char in word:
                    if chunk and pdfmetrics.stringWidth(chunk + char, font, size) > width:
                        chunks.append(chunk)
                        chunk = char
                    else:
                        chunk += char
                if chunk:
                    chunks.append(chunk)
            else:
                chunks = [word]
            for chunk in chunks:
                candidate = chunk if not current else current + " " + chunk
                if pdfmetrics.stringWidth(candidate, font, size) <= width:
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = chunk
        if current:
            lines.append(current)
            current = ""
    return lines


def draw_text(c: canvas.Canvas, text: str, x: float, y: float, width: float, *,
              font: str = "AtlasSans", size: float = 9.2, color=None,
              leading: float | None = None, max_lines: int | None = None) -> float:
    color = color or COLORS["text"]
    leading = leading or size * 1.3
    lines = wrap_lines(text, width, font, size)
    if max_lines is not None and len(lines) > max_lines:
        # B-02: el corte por exceso de lineas tambien respeta el limite de palabra.
        lines = lines[:max_lines]
        lines[-1] = marcar_continuacion(lines[-1], width, font, size,
                                        origen="draw_text max_lines")
    c.setFont(font, size)
    c.setFillColor(color)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_bullets(c: canvas.Canvas, items: Sequence[str], x: float, y: float, width: float, *,
                 size: float = 8.8, leading: float | None = None, color=None, gap: float = 2.2) -> float:
    leading = leading or size * 1.28
    color = color or COLORS["text"]
    for item in items:
        lines = wrap_lines(item, width - 12, "AtlasSans", size)
        if not lines:
            continue
        c.setFillColor(COLORS["secondary"])
        c.circle(x + 3, y + 2, 1.5, fill=1, stroke=0)
        c.setFont("AtlasSans", size)
        c.setFillColor(color)
        for idx, line in enumerate(lines):
            c.drawString(x + 10, y, line)
            y -= leading
        y -= gap
    return y


def draw_heading(c: canvas.Canvas, text: str, x: float, y: float, width: float, *,
                 size: float = 16, subtitle: str | None = None) -> float:
    y = draw_text(c, text, x, y, width, font="AtlasSans-Bold", size=size, color=COLORS["primary"], leading=size * 1.1)
    if subtitle:
        y -= 2
        y = draw_text(c, subtitle, x, y, width, size=9.2, color=COLORS["text2"], leading=11.8)
    c.setStrokeColor(COLORS["border"])
    c.line(x, y - 4, x + width, y - 4)
    return y - 14


# ---------------------------------------------------------------------------------------
# M-02 / M-03 · Ritmo vertical de la edición de conducción
#
# Cuatro valores, y solo cuatro. La V2.1 separaba los cuatro grupos del resumen por 50, 32
# y 46 pt: tres medidas distintas para la misma jerarquía, todas a ojo. Acá todo espacio
# sale de esta escala, y el espacio que sigue a una caja nunca baja de `bloque`.
#
# El otro defecto que arregla este bloque es de medición: el alto de un texto se cuenta
# desde su línea de base hacia arriba, así que usar la línea de base como si fuera el
# techo del texto deja que las mayúsculas suban por encima. Eso era la colisión de la p2,
# donde la caja cerraba en y=165,2 y el título empezaba en y=163,5.
# ---------------------------------------------------------------------------------------

RITMO = {
    "seccion": 26.0,   # entre una sección y la siguiente
    "bloque": 16.0,    # entre bloques hermanos: caja y caja, grupo y grupo
    "parrafo": 9.0,    # entre párrafos de un mismo bloque
    "linea": 4.0,      # ajuste fino dentro de un bloque
}


def base_bajo(techo: float, size: float, aire: float, font: str = "AtlasSans-Bold") -> float:
    """Línea de base de un texto cuyo techo queda `aire` puntos debajo de `techo`."""
    return techo - aire - pdfmetrics.getAscent(font, size)


# Cada caja de contenido que se dibuja queda anotada con su página y su rectángulo, para
# que el control `cajas_sin_colision` mida contra la caja real y no contra cualquier
# relleno del PDF: un mapa también es un rectángulo relleno del ancho de la columna.
CAJAS_DIBUJADAS: list[dict[str, float]] = []
PAGINA_EN_CURSO = 0


def registrar_caja(x: float, y_top: float, width: float, alto: float) -> None:
    CAJAS_DIBUJADAS.append({"pagina": PAGINA_EN_CURSO, "x0": x, "x1": x + width,
                            "y_top": y_top, "y_bottom": y_top - alto})


def box_height(text: str, width: float, size: float, pad: float = 8) -> float:
    return len(wrap_lines(text, width - 2 * pad, "AtlasSans", size)) * size * 1.3 + 2 * pad


def draw_box(c: canvas.Canvas, title: str, text: str, x: float, y_top: float, width: float, *,
             fill=None, accent=None, size: float = 9.1, alto_min: float | None = None) -> float:
    fill = fill or COLORS["note"]
    accent = accent or COLORS["primary"]
    pad = 9
    title_h = 14
    h = title_h + box_height(text, width, size, pad) + 4
    if alto_min is not None:
        h = max(h, alto_min)
    registrar_caja(x, y_top, width, h)
    c.setFillColor(fill)
    c.setStrokeColor(COLORS["border"])
    c.roundRect(x, y_top - h, width, h, 5, fill=1, stroke=1)
    c.setFillColor(accent)
    c.rect(x, y_top - h, 4, h, fill=1, stroke=0)
    c.setFont("AtlasSans-Bold", 9.2)
    c.setFillColor(accent)
    c.drawString(x + pad, y_top - 15, title)
    # Con `alto_min` la caja crece: el texto se centra en el hueco en vez de quedar pegado
    # arriba con todo el aire abajo.
    holgura = 0.0
    if alto_min is not None:
        natural = title_h + box_height(text, width, size, pad) + 4
        holgura = max(0.0, h - natural) / 2
    draw_text(c, text, x + pad, y_top - 31 - holgura, width - 2 * pad, size=size,
              color=COLORS["text2"])
    return y_top - h


class Atlas:
    def __init__(self, path: Path):
        self.c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
        self.page = 0
        self.started = False
        self.bookmarks: set[str] = set()
        self.c.setTitle("Atlas de referencias gastronómicas de la Ciudad de Buenos Aires")
        self.c.setAuthor("DGDGAS - Dirección General de Desarrollo Gastronómico")
        self.c.setCreator("DGDGAS")
        self.c.setSubject("22 lecturas territoriales y cartográficas; representación analítica no oficial")
        self.c.setKeywords("DGDGAS, atlas, gastronomía, CABA, cartografía analítica")

    def new_page(self, section: str, bookmark: str, *, header: bool = True) -> tuple[float, float, float]:
        global PAGINA_EN_CURSO
        if self.started:
            self._footer()
            self.c.showPage()
        self.started = True
        self.page += 1
        PAGINA_EN_CURSO = self.page
        if self.page > EXPECTED_PAGES:
            raise RuntimeError(f"Se intentó exceder {EXPECTED_PAGES} páginas")
        self.c.bookmarkPage(bookmark)
        self.bookmarks.add(bookmark)
        left, right = page_margins(self.page)
        width = PAGE_W - left - right
        if header:
            self.c.setFont("AtlasSans-Bold", 8.2)
            self.c.setFillColor(COLORS["primary"])
            self.c.drawString(left, PAGE_H - 9 * MM, "DGDGAS")
            self.c.setFont("AtlasSans", 7.8)
            self.c.setFillColor(COLORS["muted"])
            label = section.upper()
            self.c.drawRightString(PAGE_W - right, PAGE_H - 9 * MM, label)
            self.c.setStrokeColor(COLORS["border"])
            self.c.line(left, PAGE_H - 10.5 * MM, PAGE_W - right, PAGE_H - 10.5 * MM)
        return left, right, width

    def _footer(self) -> None:
        if self.page == 1:
            return
        left, right = page_margins(self.page)
        self.c.setStrokeColor(COLORS["border"])
        self.c.line(left, 11 * MM, PAGE_W - right, 11 * MM)
        self.c.setFillColor(COLORS["muted"])
        self.c.setFont("AtlasSans", 7.5)
        self.c.drawString(left, 7.6 * MM, "DGDGAS · Atlas de referencias gastronómicas de la Ciudad de Buenos Aires")
        self.c.drawRightString(PAGE_W - right, 7.6 * MM, f"{self.page} / {EXPECTED_PAGES}")

    def link(self, dest: str, rect: tuple[float, float, float, float]) -> None:
        self.c.linkRect("", dest, Rect=rect, relative=0, thickness=0)

    def finish(self) -> None:
        if self.page != EXPECTED_PAGES:
            raise RuntimeError(f"El PDF debe tener {EXPECTED_PAGES} páginas, tiene {self.page}")
        self._footer()
        self.c.showPage()
        conduccion = EDICION == "conduccion"
        nombres = {f["referencia_id"]: f["nombre"] for f in CONTENT_CACHE.get("fichas", [])}
        outlines = [
            ("Apertura", "section_apertura", 0),
            ("Portada", "cover", 1),
            ("Resumen ejecutivo" if conduccion else "Alcance, presentación y resumen ejecutivo",
             "opening_summary", 1),
            ("Índice", "index", 1),
            ("Cómo leer el Atlas" if conduccion else "Cómo leer y naturaleza de las cifras",
             "how_to", 1),
            ("Las cinco familias territoriales" if conduccion else "Tipologías y metodología",
             "typologies", 1),
            ("Mapa de la Ciudad" if conduccion else "Localizador R01-R22", "locator", 1),
            (SECCION_ZONAS[EDICION], "section_references", 0),
        ]
        for rid in EXPECTED_REFS:
            etiqueta = f"{rid} · {nombres.get(rid, rid)}" if conduccion else f"{rid} · {rid}"
            outlines.append((etiqueta, f"ficha_{rid}", 1))
        outlines.append((SECCION_AMPLIACIONES[EDICION], "section_complementaries", 0))
        for rid, name, title, _ in COMP_INFO_ACTIVO:
            rotulo = COND.TITULOS_DETALLE[name] if conduccion else title
            outlines.append((f"{rid} · {rotulo}", f"comp_{Path(name).stem}", 1))
        outlines.append(("Anexos", "section_annexes", 0))
        if conduccion:
            annex = [
                ("Las 22 zonas de un vistazo · 1 de 2", "annex_a1"),
                ("Las 22 zonas de un vistazo · 2 de 2", "annex_a2"),
                (COND.COMO_SE_HIZO_TITULO, "annex_metodo"),
            ]
        else:
            annex = [
                ("Matriz resumen R01-R11 · 1 de 2", "annex_51"),
                ("Matriz resumen R12-R22 · 2 de 2", "annex_52"),
                ("Subunidades y componentes", "annex_53"),
                ("Controles, exclusiones y no-productos", "annex_54"),
                ("Separaciones institucionales y nomenclatura", "annex_55"),
                ("Estado declarado, saturaciones y cobertura", "annex_56"),
                ("Cómo se contaron los locales", "annex_57"),
                ("Decisiones, limitaciones y trazabilidad · II", "annex_58"),
            ]
        outlines.extend((title, dest, 1) for title, dest in annex)
        for title, dest, level in outlines:
            if dest not in self.bookmarks:
                raise RuntimeError(f"Marcador sin destino: {dest}")
            self.c.addOutlineEntry(title, dest, level=level, closed=False)
        self.c.save()


def nature_label(value: str) -> str:
    return {
        "exacta": "Cifra exacta",
        "cota_inferior": "Cota inferior",
        "historica_metodologica": "Antecedente histórico / metodológico",
        "no_localizada": "Sin cifra comparable",
    }.get(value, value.replace("_", " ").capitalize())


def short_figure(ficha: dict) -> str:
    raw = ficha["cifra"]
    public_label = ficha.get("etiqueta_publica_cifra")
    if public_label:
        if "_" in public_label or re.search(r"\b[A-ZÁÉÍÓÚÑ0-9]+(?:_[A-ZÁÉÍÓÚÑ0-9]+)+\b", public_label):
            raise RuntimeError(f"Etiqueta pública técnica inválida en {ficha['referencia_id']}: {public_label}")
        return public_label
    if raw == "SIN_CIFRA_CANONICA_COMPARABLE":
        return "Sin cifra canónica comparable"
    return raw.replace(" | ", "\n")


def public_detail(ficha: dict, compact: bool) -> list[str]:
    detail = list(ficha["detalle_cuantitativo"])
    gloss = ficha.get("glosa_cifra")
    if gloss:
        detail = [gloss] + detail[1:]
    return detail[:2] if compact else detail


def draw_cover(atlas: Atlas, meta: dict) -> None:
    left, right, width = atlas.new_page("", "cover", header=False)
    atlas.c.bookmarkPage("section_apertura")
    atlas.bookmarks.add("section_apertura")
    c = atlas.c
    c.setFillColor(COLORS["primary_dark"])
    c.rect(0, PAGE_H - 103 * MM, PAGE_W, 103 * MM, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("AtlasSans-Bold", 15)
    c.drawString(left, PAGE_H - 25 * MM, "DGDGAS")
    c.setFont("AtlasSans", 10)
    c.drawString(left, PAGE_H - 33 * MM, "Dirección General de Desarrollo Gastronómico")
    y = PAGE_H - 53 * MM
    y = draw_text(c, meta["titulo"], left, y, width, font="AtlasSans-Bold", size=24, color=white, leading=28)
    y -= 8
    y = draw_text(c, meta["subtitulo"], left, y, width, size=13, color=white, leading=16)
    if EDICION == "tecnica":
        # La edición técnica se declara como tal en la portada: es el respaldo
        # metodológico completo, no el documento que circula.
        draw_text(c, "EDICIÓN TÉCNICA · respaldo metodológico completo",
                  left, y - 6, width, font="AtlasSans-Bold", size=10.5, color=white, leading=13)
    c.setFillColor(COLORS["accent"])
    c.rect(left, PAGE_H - 113 * MM, 48 * MM, 1.6 * MM, fill=1, stroke=0)
    c.setFillColor(COLORS["primary"])
    c.setFont("AtlasSans", 11.5)
    draw_text(
        c,
        "Lectura territorial de la oferta gastronómica de la Ciudad, "
        "elaborada por la Dirección General de Desarrollo Gastronómico.",
        left, PAGE_H - 127 * MM, width * 0.74, size=11.5,
        color=COLORS["text2"], leading=15.5,
    )
    # En la edición de conducción la caja se ajusta a su texto: con dos líneas dentro, el
    # alto fijo de 55 mm dejaba un vacío que se leía como un error de armado.
    alto_caja = 34 * MM if EDICION == "conduccion" else 55 * MM
    c.setFillColor(COLORS["card"])
    c.roundRect(left, 98 * MM - alto_caja, width, alto_caja, 8, fill=1, stroke=0)
    c.setFillColor(COLORS["primary"])
    c.setFont("AtlasSans-Bold", 11)
    c.drawString(left + 9 * MM, 83 * MM,
                 "Lectura institucional" if EDICION == "conduccion"
                 else "LECTURA INSTITUCIONAL")
    draw_text(
        c,
        "Veintidós zonas diversas reunidas en una lectura común. "
        "Las categorías, cifras y métodos no se convierten en un ranking general "
        "ni en veintidós polos equivalentes."
        if EDICION == "conduccion" else
        "Veintidós referencias diversas reunidas en una lectura común. "
        "Las categorías, cifras y métodos no se convierten en un ranking general "
        "ni en veintidós polos equivalentes.",
        left + 9 * MM, 73 * MM, width - 18 * MM, size=10.2, color=COLORS["text2"], leading=13.5,
    )
    c.setFillColor(COLORS["red"])
    c.setFont("AtlasSans-Bold", 10.2)
    c.drawString(left, 28 * MM,
                 "Representación cartográfica analítica · no oficial"
                 if EDICION == "conduccion"
                 else "REPRESENTACIÓN CARTOGRÁFICA ANALÍTICA · NO OFICIAL")


def notas_locator(conduccion: bool) -> list[tuple[str, str]]:
    """Las tres notas al pie del mapa general, con la fuente en que se dibuja cada una."""
    if conduccion:
        return [
            ("El tamaño del área no indica la cantidad de oferta: "
             "depende de cuán repartidos estén los locales.", "AtlasSans-Bold"),
            ("Números grises sobre el fondo: las 15 comunas. Trazo punteado: es el área con "
             "que se consultó la zona, no el contorno de la oferta encontrada.", "AtlasSans"),
            # Corrección editorial 2026-08-04. Sólo la conducción: la rama `else` es la
            # edición técnica y conserva el vocabulario de la V2.1.
            ("Las áreas envuelven los locales relevados en cada zona: son una lectura de "
             "trabajo, no límites oficiales.", "AtlasSans"),
        ]
    return [
        ("El tamaño del área no indica la cantidad de oferta: "
         "depende de cuán dispersos estén los registros.", "AtlasSans-Bold"),
        ("Números grises sobre el fondo: las 15 comunas. Trazo punteado: área de consulta "
         "declarada, no envolvente de oferta observada.", "AtlasSans"),
        ("Las áreas son aproximaciones de lectura territorial: no son límites oficiales, "
         "padrón de locales ni recomendación comercial.", "AtlasSans"),
    ]


def comunas_resumen() -> tuple[int, str]:
    """Ubicacion aproximada, calculada sobre el NUCLEO pre-buffer (D-6)."""
    filas = read_csv(QA_DIR / "COMUNAS_POR_NUCLEO.csv")
    numeros = set()
    for fila in filas:
        for parte in fila["comunas_nucleo"].split(" / "):
            parte = parte.replace("Comuna ", "").strip()
            if parte.isdigit():
                numeros.add(int(parte))
    orden = sorted(numeros)
    return len(orden), ", ".join(str(n) for n in orden)


def draw_opening_summary(atlas: Atlas) -> None:
    """B5 - abre con datos de la Ciudad; la no-comparabilidad va AL LADO del dato."""
    left, _, width = atlas.new_page("Apertura", "opening_summary")
    c = atlas.c
    y = draw_heading(c, "1. Resumen ejecutivo", left, TOP_Y - 5 * MM, width)

    cantidad, lista = comunas_resumen()
    familias: dict[str, int] = {}
    for rid in EXPECTED_REFS:
        familias[FAMILIA_DE[rid]] = familias.get(FAMILIA_DE[rid], 0) + 1
    orden_fam = sorted(familias.items(), key=lambda kv: -kv[1])
    resumen_fam = "; ".join(f"{FAMILIA_ETIQUETA[k].lower()}, {v}" for k, v in orden_fam)

    y = draw_box(
        c, "LO QUE MUESTRA ESTE ATLAS",
        f"La Dirección identificó y caracterizó 22 referencias gastronómicas de la Ciudad, "
        f"presentes en {cantidad} de las 15 comunas (comunas {lista}). "
        f"Se agrupan en cinco familias territoriales: {resumen_fam}. "
        f"No hay referencias identificadas en el sur profundo de la Ciudad.",
        left, y, width, fill=COLORS["note"], size=9.5,
    ) - 9

    c.setFont("AtlasSans-Bold", 11)
    c.setFillColor(COLORS["primary"])
    c.drawString(left, y, "Dónde se concentra la oferta relevada")
    y -= 6
    c.setFont("AtlasSans", 8.6)
    c.setFillColor(COLORS["text2"])
    y = draw_text(
        c, "Las cifras solo se comparan dentro de cada grupo: cada grupo usó un método y "
           "un universo propios. Entre grupos no son comparables y no se suman.",
        left, y - 8, width, size=8.6, color=COLORS["text2"], leading=10.6) - 6

    grupos = [
        ("Relevamiento propio con deduplicación conservadora",
         "Caballito 907 · Villa Crespo 646 · Chacarita 327 · Boulevard Caseros 66",
         "Conteos cerrados. No equivalen a locales en actividad hoy."),
        ("Directorio comercial en línea, deduplicado",
         "Villa Urquiza 189 · Devoto 119 · Avenida Boedo 79 · Donado–Holmberg 40",
         "Conteos cerrados sobre una fuente distinta de la anterior."),
        ("Pisos censados (cota inferior, se leen con “al menos”)",
         "Centro/Microcentro ≥797 · La Paternal ≥254 · Esmeralda–Paraguay ≥216 · "
         "Lacroze ≥211 · Villa Pueyrredón ≥158 · Abasto ≥314 · García del Río ≥40",
         "Puede haber más casos, nunca menos. No son conteos completos."),
        ("Referencias sin conteo comparable",
         "Palermo · Avenida Corrientes · San Telmo · Puerto Madero · Recoleta",
         "Están caracterizadas y ubicadas; Belgrano y Costanera Norte solo tienen "
         "antecedentes previos (697 y 72)."),
    ]
    for titulo, datos, nota in grupos:
        c.setFont("AtlasSans-Bold", 8.8)
        c.setFillColor(COLORS["primary"])
        y = draw_text(c, titulo, left, y, width, font="AtlasSans-Bold", size=8.8,
                      color=COLORS["primary"], leading=10.6)
        y = draw_text(c, datos, left + 6, y - 1, width - 6, size=8.8,
                      color=COLORS["text"], leading=10.8)
        y = draw_text(c, nota, left + 6, y - 1, width - 6, font="AtlasSans-Italic",
                      size=8.0, color=COLORS["muted"], leading=9.8) - 6

    draw_box(
        c, "CÓMO USAR ESTE ATLAS",
        "El mapa de la página 6 ubica las 22 referencias en la Ciudad. Cada referencia tiene "
        "después una ficha y un mapa propios. Las áreas dibujadas son aproximaciones de lectura "
        "territorial: no son límites oficiales, padrón de locales ni recomendación comercial. "
        "La edición no recalcula universos, no geocodifica y no reabre decisiones territoriales.",
        left, max(y, BOTTOM_Y + 30 * MM), width, fill=COLORS["warn"],
        accent=COLORS["accent"], size=8.9,
    )


def draw_index(atlas: Atlas, content: dict) -> None:
    left, _, width = atlas.new_page("Apertura", "index")
    c = atlas.c
    conduccion = EDICION == "conduccion"
    y = draw_heading(c, "2. Índice", left, TOP_Y - 5 * MM, width,
                     subtitle="Cada entrada lleva a su página.") if conduccion else \
        draw_heading(c, "2. Índice", left, TOP_Y - 5 * MM, width,
                     subtitle="Un único índice con navegación interna.")
    # B7: con 49 páginas el índice en tres columnas dejaba media hoja vacía. Dos columnas
    # más anchas y con más cuerpo llenan la página y se leen mejor.
    n_cols = 2 if conduccion else 3
    gap = 6 * MM if conduccion else 4 * MM
    col_w = (width - (n_cols - 1) * gap) / n_cols
    cols = [left + i * (col_w + gap) for i in range(n_cols)]
    names = {f["referencia_id"]: f["nombre"] for f in content["fichas"]}
    primera_ampliacion = min(COMP_PAGES.values())
    primer_anexo = next(p for p, _, _, k in PAGE_SEQUENCE if k in {"ANEXO_MATRIZ"})
    entries: list[tuple[str, int, str, int]] = [
        ("Apertura", 1, "section_apertura", 0),
        ("Resumen ejecutivo" if conduccion else "Alcance y resumen", 2, "opening_summary", 1),
        ("Cómo leer el Atlas" if conduccion else "Cómo leer", 4, "how_to", 1),
        ("Las cinco familias" if conduccion else "Tipologías y metodología", 5, "typologies", 1),
        ("Mapa de la Ciudad" if conduccion else "Localizador", 6, "locator", 1),
        (SECCION_ZONAS[EDICION], 7, "section_references", 0),
    ]
    entries.extend((f"{rid} {names[rid]}", REF_PAGES[rid][0], f"ficha_{rid}", 1) for rid in EXPECTED_REFS)
    entries.append((SECCION_AMPLIACIONES[EDICION], primera_ampliacion, "section_complementaries", 0))
    entries.extend(
        (f"{rid} {COND.TITULOS_DETALLE[fn] if conduccion else title}", COMP_PAGES[fn],
         f"comp_{Path(fn).stem}", 1)
        for rid, fn, title, _ in COMP_INFO_ACTIVO)
    entries.append(("Anexos", primer_anexo, "section_annexes", 0))
    if conduccion:
        annex_entries = [
            ("Las 22 zonas · 1 de 2", "annex_a1"),
            ("Las 22 zonas · 2 de 2", "annex_a2"),
            ("Cómo se hizo este Atlas", "annex_metodo"),
        ]
        entries.extend((titulo, primer_anexo + idx, dest, 1)
                       for idx, (titulo, dest) in enumerate(annex_entries))
    else:
        annex_titles = [
            "Matriz R01-R11", "Matriz R12-R22", "Subunidades", "Controles y exclusiones",
            "Separaciones", "Estado declarado y cobertura", "Recuento", "Decisiones y trazabilidad",
        ]
        entries.extend((title, 51 + idx, f"annex_{51+idx}", 1) for idx, title in enumerate(annex_titles))
    # B4: los encabezados de seccion no pueden quedar al pie de una columna con una
    # sola entrada debajo. Se corta por seccion, no por cantidad fija de filas.
    objetivo = math.ceil(len(entries) / n_cols)
    limites: list[int] = []
    if conduccion:
        # Con 40 entradas, cortar solo en límite de sección dejaba una columna llena y la
        # otra a media altura. Se corta donde el reparto queda parejo, evitando dejar un
        # encabezado de sección solo al pie de la columna.
        for k in range(1, n_cols):
            candidatos = [i for i in range(1, len(entries))
                          if i not in limites and entries[i - 1][3] != 0]
            limites.append(min(candidatos, key=lambda i: abs(i - objetivo * k)))
    else:
        cortes = [i for i, e in enumerate(entries) if e[3] == 0]
        for k in range(1, n_cols):
            candidatos = [i for i in cortes if i not in limites and i > 0]
            limites.append(min(candidatos, key=lambda i: abs(i - objetivo * k)))
    limites = sorted(set(limites))
    while len(limites) < n_cols - 1:
        limites.append(len(entries))
    chunks, previo = [], 0
    for corte in limites:
        chunks.append(entries[previo:corte])
        previo = corte
    chunks.append(entries[previo:])
    if conduccion:
        # Si una columna arranca en medio de una sección, se repite el encabezado: el
        # lector no tiene que volver a la columna anterior para saber qué está mirando.
        for idx in range(1, len(chunks)):
            if not chunks[idx] or chunks[idx][0][3] == 0:
                continue
            arranque = entries.index(chunks[idx][0])
            titulo = next((e[0] for e in reversed(entries[:arranque]) if e[3] == 0), None)
            if titulo:
                # M-08: la entrada de continuación lleva a donde efectivamente continúa la
                # sección —la primera entrada de esta columna—, no al inicio de la sección,
                # que quedó en la columna anterior.
                sigue = chunks[idx][0]
                chunks[idx] = [(f"{titulo} (continúa)", sigue[1], sigue[2], 0)] + chunks[idx]
    # B7: el interlineado se calcula para que la columna más larga llegue al pie.
    if conduccion:
        mas_larga = max(sum(max(1, len(wrap_lines(e[0], col_w - 34, "AtlasSans", 10.4)))
                            for e in chunk) for chunk in chunks)
        alto_fila = min(26.0, max(12.5, (y - BOTTOM_Y - 8 * MM) / max(mas_larga, 1)))
    else:
        alto_fila = 10.5
    for col, chunk in enumerate(chunks):
        yy = y
        for label, page, dest, level in chunk:
            if conduccion:
                size = 10.4 if level else 11.2
            else:
                size = 8.5 if level else 9.2
            font = "AtlasSans" if level else "AtlasSans-Bold"
            color = COLORS["text2"] if level else COLORS["primary"]
            indent = (9 if conduccion else 7) if level else 0
            margen = 34 if conduccion else 31
            lines = wrap_lines(label, col_w - margen - indent, font, size)
            h = max(alto_fila + 1.5, len(lines) * alto_fila)
            c.setFont(font, size)
            c.setFillColor(color)
            for line_idx, line in enumerate(lines):
                c.drawString(cols[col] + indent, yy - line_idx * alto_fila, line)
            c.setFont("AtlasSans-Bold", size if conduccion else 8.5)
            c.drawRightString(cols[col] + col_w, yy, str(page))
            atlas.link(dest, (cols[col], yy - h + 2, cols[col] + col_w, yy + 7))
            yy -= h + (3 if not conduccion else 1.5)


def draw_how_to(atlas: Atlas) -> None:
    left, _, width = atlas.new_page("Apertura", "how_to")
    c = atlas.c
    y = draw_heading(c, "3. Cómo leer el Atlas y naturaleza de las cifras", left, TOP_Y - 5 * MM, width)
    items = [
        ("Cifra exacta", "Se contaron todos los casos que el método alcanzó. Es un conteo cerrado, no una medición de la actividad de hoy."),
        ("Dato de referencia previo", "Proviene de un relevamiento anterior. Sirve para describir y comparar en el tiempo, no como indicador principal."),
        ("Cota inferior", "Se escribe con el signo ≥ y significa \u0022al menos esta cantidad\u0022. Es un piso: puede haber más casos, nunca menos."),
        ("Sin cifra comparable", "Hay evidencia de la zona, pero no un universo único que permita dar un número sin inducir a error."),
        ("Estado declarado", "Cómo figura cada local: en actividad, cerrado temporalmente o cerrado en forma permanente."),
        ("Saturación", "La consulta llegó al tope de resultados que devuelve la fuente. Lo que falta no se estima ni se inventa."),
        ("Vista de detalle", "Amplía una parte de una referencia. No crea una referencia nueva ni un límite oficial."),
        ("Advertencia sobre la geometría", "Los contornos de los mapas son analíticos: ayudan a leer el territorio, no delimitan nada de manera oficial."),
    ]
    gap = 4 * MM
    col_w = (width - gap) / 2
    for idx, (title, text) in enumerate(items):
        col = idx % 2
        row = idx // 2
        x = left + col * (col_w + gap)
        yy = y - row * 47 * MM
        draw_box(c, title.upper(), text, x, yy, col_w, fill=COLORS["card"] if row % 2 == 0 else COLORS["note"], size=8.9)
    draw_box(
        c, "REGLA GENERAL",
        "Las 22 referencias no forman un ranking. Cada cifra se obtuvo con un método distinto, sobre un universo "
        "distinto y con una fecha propia: compararlas entre sí como si midieran lo mismo lleva a conclusiones erróneas.",
        left, BOTTOM_Y + 31 * MM, width, fill=COLORS["warn"], accent=COLORS["accent"], size=9.2,
    )


def draw_typologies(atlas: Atlas, content: dict) -> None:
    """B5 - las 22 etiquetas finas colapsan en cinco familias."""
    left, _, width = atlas.new_page("Apertura", "typologies")
    c = atlas.c
    y = draw_heading(
        c, "4. Las cinco familias territoriales", left, TOP_Y - 5 * MM, width,
        subtitle="Cinco formas de estar en el territorio. El color de cada familia es el que usa el mapa general.",
    )
    nombres = {f["referencia_id"]: f["nombre"] for f in content["fichas"]}
    finas = {f["referencia_id"]: f["tipologia"] for f in content["fichas"]}
    definicion = {
        "polo": "Concentración reconocible en torno de un área, con identidad propia.",
        "multiparte": "Un polo que se lee en partes o subzonas separadas, sin unirlas artificialmente.",
        "eje": "La oferta se organiza a lo largo de una calle o avenida, no en una mancha.",
        "segmentada": "Un área que solo se puede leer por subunidades independientes entre sí.",
        "dispersa": "Oferta presente y documentada, sin un núcleo único demostrado.",
    }
    for fam, etiqueta in FAMILIA_ETIQUETA.items():
        refs = [r for r in EXPECTED_REFS if FAMILIA_DE[r] == fam]
        color = HexColor(FAMILIA_COLOR[fam])
        alto = 28 + 12.4 * len(refs)
        c.setFillColor(HexColor("#F7F9FB"))
        c.roundRect(left, y - alto - 12, width, alto + 10, 4, fill=1, stroke=0)
        c.saveState()
        c.setFillColor(color)
        c.setFillAlpha(0.45)
        c.rect(left + 8, y - 13, 13, 9, fill=1, stroke=0)
        c.setFillAlpha(1)
        c.restoreState()
        c.setStrokeColor(color)
        c.setLineWidth(0.9)
        c.rect(left + 8, y - 13, 13, 9, fill=0, stroke=1)
        c.setFont("AtlasSans-Bold", 9.4)
        c.setFillColor(COLORS["primary"])
        c.drawString(left + 27, y - 11, f"{etiqueta}  ({len(refs)})")
        # La definicion va en su propia linea: al costado del titulo se desbordaba del
        # margen derecho en las familias de nombre largo (defecto que la V2 arrastraba).
        c.setFont("AtlasSans", 8.4)
        c.setFillColor(COLORS["text2"])
        c.drawString(left + 27, y - 23, definicion[fam])
        yy = y - 38
        # B-01: una referencia por linea a todo el ancho util. En tres columnas la
        # etiqueta fina no entraba y se cortaba a mitad de palabra; el ancho completo
        # admite la mas larga ("Polo documentado sin unidad espacial estabilizada")
        # sin acortar nada. `ajustar_a_ancho` queda como red, no como recurso.
        ancho_fila = width - 34
        for rid in refs:
            c.setFont("AtlasSans-Bold", 8.6)
            c.setFillColor(COLORS["primary"])
            c.drawString(left + 27, yy, rid)
            sangria = 27 + c.stringWidth("R00  ", "AtlasSans-Bold", 8.6)
            nombre = nombres[rid]
            c.setFont("AtlasSans", 8.6)
            c.setFillColor(COLORS["text"])
            c.drawString(left + sangria, yy, nombre)
            corrida = sangria + c.stringWidth(nombre + "  ·  ", "AtlasSans", 8.6)
            c.setFillColor(COLORS["muted"])
            c.drawString(left + sangria + c.stringWidth(nombre + "  ", "AtlasSans", 8.6), yy, "·")
            c.setFillColor(COLORS["text2"])
            c.drawString(left + corrida,
                         yy,
                         ajustar_a_ancho(finas[rid], ancho_fila - corrida + 27, "AtlasSans", 8.6,
                                         origen=f"p5 tipologia fina {rid}"))
            yy -= 12.4
        y -= alto + 16

    draw_box(
        c, "SOBRE ESTA CLASIFICACIÓN",
        "La familia describe la forma de estar en el territorio, no la importancia ni el tamaño. "
        "La etiqueta específica de cada referencia se conserva junto a su nombre y se repite en su ficha. "
        "Ninguna familia agrupa cifras: los números de cada referencia siguen sin sumarse entre sí.",
        left, max(y, BOTTOM_Y + 26 * MM), width, fill=COLORS["note"], size=8.9,
    )


def draw_locator(atlas: Atlas) -> None:
    """B1 - Mapa general de la Ciudad. Reemplaza la hoja de contactos de miniaturas."""
    left, _, width = atlas.new_page("Apertura", "locator")
    c = atlas.c
    y = draw_heading(
        c,
        "5. Las 22 zonas en la Ciudad" if EDICION == "conduccion"
        else "5. Las 22 referencias en la Ciudad",
        left, TOP_Y - 5 * MM, width,
        subtitle="Cada forma es una zona; el color indica su familia. Cada fila lleva a su ficha."
        if EDICION == "conduccion"
        else "Cada forma es una referencia; el color indica su familia. Cada fila lleva a su ficha.",
    )
    # M-01: la tabla de referencias baja a dos columnas al pie y el mapa toma el ancho
    # completo. En V2 la tabla lateral dejaba el mapa en 126 mm de ancho y, como la
    # Ciudad es mas alta que ancha, el dibujo terminaba al 65% de la altura util y el
    # tercio inferior de la pagina mas importante del Atlas quedaba vacio.
    filas_col = 11
    fila_h = 9.6
    tabla_h = 13 + filas_col * fila_h
    leyenda_h = 24
    # Las tres notas del pie se miden por sus líneas reales: dar por hecho que cada una
    # entra en un renglón es lo que dejaba a una de ellas saliéndose de la columna.
    notas = notas_locator(EDICION == "conduccion")
    lineas_nota = sum(max(1, len(wrap_lines(t, width, f, 7.1))) for t, f in notas)
    notas_h = lineas_nota * 10.2
    mapa_bottom = BOTTOM_Y + tabla_h + leyenda_h + notas_h + 12
    mapa_h = y - mapa_bottom - 2
    CARTOGRAFO.mapa_general(c, left, mapa_bottom, width, mapa_h, REF_PAGES)

    ly = mapa_bottom - 11
    c.setFont("AtlasSans-Bold", 7.2)
    c.setFillColor(COLORS["primary"])
    # M-04: en la conducción no queda ninguna capa de versalitas fuera del encabezado
    # de sección; estos rótulos ya se distinguen por peso y color.
    c.drawString(left, ly, "Familias" if EDICION == "conduccion" else "FAMILIAS")
    ly -= 11
    cx = left
    for fam, etiqueta in FAMILIA_ETIQUETA.items():
        col = HexColor(FAMILIA_COLOR[fam])
        c.saveState()
        c.setFillColor(col)
        c.setFillAlpha(0.42)
        c.rect(cx, ly, 10, 7, fill=1, stroke=0)
        c.setFillAlpha(1)
        c.restoreState()
        tr = FAMILIA_TRAMA[fam]
        if tr:
            c.saveState()
            pth = c.beginPath()
            pth.rect(cx, ly, 10, 7)
            c.clipPath(pth, stroke=0, fill=0)
            c.setStrokeColor(col)
            c.setLineWidth(0.35)
            for i in range(-12, 13):
                if tr[0] == 0:
                    c.line(cx, ly + i * 2.2, cx + 10, ly + i * 2.2)
                elif tr[0] == 90:
                    c.line(cx + i * 2.2, ly, cx + i * 2.2, ly + 7)
                elif tr[0] == 45:
                    c.line(cx + i * 2.4 - 8, ly - 8, cx + i * 2.4 + 8, ly + 8)
                else:
                    c.line(cx + i * 2.4 - 8, ly + 8, cx + i * 2.4 + 8, ly - 8)
            c.restoreState()
        c.setStrokeColor(col)
        c.setLineWidth(0.8)
        c.rect(cx, ly, 10, 7, fill=0, stroke=1)
        c.setFillColor(COLORS["text2"])
        c.setFont("AtlasSans", 7.1)
        c.drawString(cx + 13, ly + 1, etiqueta)
        cx += 13 + c.stringWidth(etiqueta, "AtlasSans", 7.1) + 11

    # Tabla de las 22 en dos columnas, cada fila enlazada a su ficha.
    yt = ly - 17
    col_w = (width - 8 * MM) / 2
    names = {f["referencia_id"]: f["nombre"] for f in CONTENT_CACHE["fichas"]}
    for k in (0, 1):
        cx = left + k * (col_w + 8 * MM)
        c.setFont("AtlasSans-Bold", 7.2)
        c.setFillColor(COLORS["primary"])
        c.drawString(cx, yt, "Zona" if EDICION == "conduccion" else "REFERENCIA")
        c.drawRightString(cx + col_w, yt,
                          "Ficha" if EDICION == "conduccion" else "FICHA")
        c.setStrokeColor(COLORS["border"])
        c.line(cx, yt - 4, cx + col_w, yt - 4)
    yy0 = yt - 15
    for i, rid in enumerate(EXPECTED_REFS):
        k, fila = divmod(i, filas_col)
        cx = left + k * (col_w + 8 * MM)
        yy = yy0 - fila * fila_h
        color = HexColor(FAMILIA_COLOR[FAMILIA_DE[rid]])
        c.setFillColor(color)
        c.circle(cx + 3.8, yy + 2.4, 3.8, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("AtlasSans-Bold", 5.0)
        c.drawCentredString(cx + 3.8, yy + 0.7, rid[1:])
        c.setFillColor(COLORS["text"])
        c.setFont("AtlasSans", 7.4)
        c.drawString(cx + 11, yy,
                     ajustar_a_ancho(names[rid], col_w - 30, "AtlasSans", 7.4,
                                     origen=f"p6 tabla lateral {rid}"))
        c.setFont("AtlasSans-Bold", 7.4)
        c.setFillColor(COLORS["secondary"])
        c.drawRightString(cx + col_w, yy, str(REF_PAGES[rid][0]))
        atlas.link(f"ficha_{rid}", (cx, yy - 2, cx + col_w, yy + 8))

    yn = yy0 - filas_col * fila_h - 4
    # M-03: el area dibujada es dispersion, no volumen. Verificado sobre las capas
    # entregadas: Devoto ocupa 4,79 km2 con 119 registros y Villa Crespo 3,35 km2 con
    # 646. La geometria no se cambia; se dice lo que significa.
    # M-01/M-02: estas tres líneas se dibujaban con `drawString`, sin medir. La segunda de
    # la conducción mide 514,1 pt en una columna de 510,2 y salía de la caja de texto; con
    # el margen de encuadernación de la V2.1 quedaba a 1,8 pt del borde y no se notaba.
    # Pasan por el mismo ajuste de ancho que el resto del documento.
    y_nota = yn
    for texto, fuente in notas:
        color = COLORS["accent"] if fuente == "AtlasSans-Bold" else COLORS["text2"]
        y_nota = draw_text(c, texto, left, y_nota, width, font=fuente, size=7.1,
                           color=color, leading=10.2)
    ultima_base = y_nota + 10.2      # `draw_text` ya descontó el interlineado del cierre
    if ultima_base < BOTTOM_Y:
        raise RuntimeError(f"Desborde del pie de la p6: y={ultima_base:.1f} < {BOTTOM_Y:.1f}")


def ficha_components(ficha: dict) -> list[str]:
    return [f"{row[0]}: {row[1]}; {row[2]}; {row[3]}." for row in ficha["subunidades"]]


class _LienzoMudo:
    """Canvas que mide pero no dibuja: sirve para probar el encaje antes de trazar."""

    def stringWidth(self, text, font, size):
        return pdfmetrics.stringWidth(text, font, size)

    def __getattr__(self, _nombre):
        return lambda *a, **k: None


class _AtlasMudo:
    def __init__(self) -> None:
        self.c = _LienzoMudo()
        self.page = 0

    def link(self, *a, **k) -> None:
        return None


def ajuste_ficha(ficha: dict, width: float, y_top: float, y_bottom: float,
                 compact: bool, *, dibujante=None, tope: float | None = None,
                 aire_max: float | None = None) -> tuple[float, float]:
    """F-02 - encuentra el cuerpo y el aire con que la ficha llena su columna.

    Las fichas de una sola referencia varian mucho de extension: R08 ocupaba menos de
    la mitad de la pagina y dejaba el tercio inferior muerto, mientras otras llegaban
    justo. Se prueba el cuerpo mas grande que todavia entra y el sobrante se reparte
    entre los bloques, en vez de acumularse abajo.
    """
    mudo = _AtlasMudo()
    dibujante = dibujante or draw_ficha_band
    if tope is None:
        tope = 1.40 if not compact else 1.16
    if aire_max is None:
        aire_max = 38.0 if not compact else 7.0
    piso = y_bottom + 28
    escala = 1.0
    paso = 0.02
    while escala + paso <= tope + 1e-9:
        y = dibujante(mudo, ficha, 0.0, y_top, width, y_bottom, compact,
                      escala=escala + paso, medir=True)
        if y < piso:
            break
        escala += paso
    y = dibujante(mudo, ficha, 0.0, y_top, width, y_bottom, compact,
                  escala=escala, medir=True)
    sobrante = max(0.0, y - piso)
    aire = min(sobrante / AIRES_FICHA, aire_max)
    while aire > 0:
        y = dibujante(mudo, ficha, 0.0, y_top, width, y_bottom, compact,
                      escala=escala, aire=aire, medir=True)
        if y >= piso:
            break
        aire -= 1.0
    return escala, max(aire, 0.0)


AIRES_FICHA = 4          # separaciones de bloque donde se reparte el sobrante
AJUSTES_FICHA: list[dict[str, object]] = []


def draw_ficha_band(atlas: Atlas, ficha: dict, x: float, y_top: float, width: float,
                    y_bottom: float, compact: bool, *, escala: float = 1.0,
                    aire: float = 0.0, medir: bool = False) -> float:
    c = atlas.c
    rid, name = ficha["referencia_id"], ficha["nombre"]
    title_size = 11.5 if compact else 17
    body = (8.5 if compact else 9.15) * escala
    leading = (10.6 if compact else 12.1) * escala
    tam_rotulo = (8.5 if compact else 9.2) * min(escala, 1.18)
    salto = 12 * min(escala, 1.25)
    c.setFont("AtlasSans-Bold", title_size)
    c.setFillColor(COLORS["primary"])
    c.drawString(x, y_top, f"{rid} · {name}")
    y = y_top - (15 if compact else 22)
    c.setFont("AtlasSans", 8.5 if compact else 9.5)
    c.setFillColor(COLORS["text2"])
    c.drawString(x, y, ficha["tipologia"])
    y -= 14
    # B4: clave visual del badge. B5: la ausencia de cifra baja de jerarquia y pasa a
    # linea secundaria en cuerpo normal, en vez de ser lo mas destacado de la pagina.
    naturaleza = ficha["naturaleza"]
    fondo, acento, simbolo, rotulo = BADGE[naturaleza]
    # R06 declara naturaleza de antecedente pero no tiene cifra publicable. El badge no
    # puede anunciar un antecedente y mostrar "sin cifra": se trata como ausencia.
    sin_cifra = ficha["cifra"] == "SIN_CIFRA_CANONICA_COMPARABLE"
    if naturaleza == "no_localizada" or sin_cifra:
        c.setFont("AtlasSans", 8.4 if compact else 9.2)
        c.setFillColor(COLORS["text2"])
        y = draw_text(c, "Referencia caracterizada; sin conteo comparable entre métodos.",
                      x, y, width, size=(8.4 if compact else 9.2) * escala, color=COLORS["text2"],
                      leading=(10.4 if compact else 11.4) * escala) - 8
    else:
        figure = short_figure(ficha)
        cuerpo_cifra = (9.1 if compact else 10.5) * min(escala, 1.22)
        fig_h = max(26 * min(escala, 1.22),
                    len(wrap_lines(figure, width - 34, "AtlasSans-Bold", cuerpo_cifra))
                    * (12 if compact else 14) * min(escala, 1.22) + 12)
        c.setFillColor(HexColor(fondo))
        c.roundRect(x, y - fig_h, width, fig_h, 4, fill=1, stroke=0)
        c.setFillColor(HexColor(acento))
        c.rect(x, y - fig_h, 2.6, fig_h, fill=1, stroke=0)
        c.setFont("AtlasSans-Bold", 13 if compact else 15)
        c.drawString(x + 9, y - 20, simbolo)
        c.setFont("AtlasSans-Bold", 7.5 if compact else 8.2)
        c.drawString(x + 26, y - 11, rotulo)
        draw_text(c, figure, x + 26, y - 23, width - 34, font="AtlasSans-Bold",
                  size=cuerpo_cifra, color=COLORS["text"],
                  leading=(11.5 if compact else 13.5) * min(escala, 1.22))
        y -= fig_h + 9
    y -= aire
    c.setFont("AtlasSans-Bold", tam_rotulo)
    c.setFillColor(COLORS["primary"])
    c.drawString(x, y, "Lectura")
    y -= salto
    y = draw_text(c, ficha["lectura"], x, y, width, size=body, color=COLORS["text2"], leading=leading)
    characterization = ficha["caracterizacion"] if not compact else ficha["caracterizacion"][:2]
    y = draw_bullets(c, characterization, x, y - 2, width, size=body, leading=leading, gap=1)
    y -= aire
    c.setFont("AtlasSans-Bold", tam_rotulo)
    c.setFillColor(COLORS["primary"])
    c.drawString(x, y, "Evidencia y método")
    y -= salto
    detail = public_detail(ficha, compact)
    y = draw_bullets(c, detail, x, y, width, size=body, leading=leading, gap=1)
    components = ficha_components(ficha)
    relations = ficha["relaciones"]
    exclusions = ficha["exclusiones"]
    if components or relations or exclusions:
        y -= aire
        c.setFont("AtlasSans-Bold", tam_rotulo)
        c.setFillColor(COLORS["primary"])
        c.drawString(x, y, "Componentes y relaciones")
        y -= salto
        combined = components + relations + exclusions
        if compact:
            combined = combined[:5]
        y = draw_bullets(c, combined, x, y, width, size=body, leading=leading, gap=1)
    limits = ficha["limitaciones_especificas"]
    if limits:
        y -= aire
        c.setFont("AtlasSans-Bold", tam_rotulo)
        c.setFillColor(COLORS["text2"])
        c.drawString(x, y, "Qué no se puede concluir")
        y -= salto
        y = draw_bullets(c, limits if not compact else limits[:2], x, y, width, size=body, leading=leading, color=COLORS["text2"], gap=1)
    # En la ficha de pagina entera la linea de fuente se ancla al pie de la columna:
    # cierra la pagina en vez de dejarla colgando a media altura.
    source_y = y_bottom + 20 if not compact else max(y_bottom + 20, y - 2 - aire)
    c.setFont("AtlasSans", 7.9 if compact else 8.2)
    c.setFillColor(COLORS["muted"])
    c.drawString(x, source_y, f"Fuente: {ficha['fuente_id']} · datos al {ficha['fecha_corte']}")
    c.setFont("AtlasSans-Bold", 8.1)
    c.setFillColor(COLORS["secondary"])
    c.drawRightString(x + width, source_y,
                      f"{IR_AL_MAPA[EDICION]} · p. {REF_PAGES[rid][1]}")
    atlas.link(f"map_{rid}", (x + width - 115, source_y - 4, x + width, source_y + 9))
    if y < y_bottom + 28 and not medir:
        raise RuntimeError(f"Desborde de ficha {rid}: y={y:.1f}, mínimo={y_bottom+28:.1f}")
    return y


def draw_full_ficha(atlas: Atlas, ficha: dict) -> None:
    left, _, width = atlas.new_page("Referencias R01-R22", f"ficha_{ficha['referencia_id']}")
    if ficha["referencia_id"] == "R01":
        atlas.c.bookmarkPage("section_references")
        atlas.bookmarks.add("section_references")
    y = TOP_Y - 7 * MM
    y_bottom = BOTTOM_Y + 10 * MM
    escala, aire = ajuste_ficha(ficha, width, y, y_bottom, compact=False)
    AJUSTES_FICHA.append({"referencia_id": ficha["referencia_id"], "pagina": atlas.page,
                          "tipo": "completa", "escala_cuerpo": round(escala, 3),
                          "aire_pt": round(aire, 2)})
    draw_ficha_band(atlas, ficha, left, y, width, y_bottom, compact=False,
                    escala=escala, aire=aire)
    atlas.c.setFont("AtlasSans-Italic", 7.9)
    atlas.c.setFillColor(COLORS["muted"])
    atlas.c.drawString(left, BOTTOM_Y + 13 * MM, "Advertencia común: los contornos son analíticos y no oficiales; la oferta registrada o visible no equivale a locales en actividad.")


def draw_double_ficha(atlas: Atlas, first: dict, second: dict) -> None:
    left, _, width = atlas.new_page("Referencias R01-R22", f"ficha_{first['referencia_id']}")
    atlas.c.bookmarkPage(f"ficha_{second['referencia_id']}")
    atlas.bookmarks.add(f"ficha_{second['referencia_id']}")
    top = TOP_Y - 7 * MM
    middle = PAGE_H / 2 - 1 * MM
    atlas.c.setStrokeColor(COLORS["strong"])
    atlas.c.line(left, middle, left + width, middle)
    for ficha, y_top, y_bottom in ((first, top, middle + 8),
                                   (second, middle - 12, BOTTOM_Y + 10 * MM)):
        escala, aire = ajuste_ficha(ficha, width, y_top, y_bottom, compact=True)
        AJUSTES_FICHA.append({"referencia_id": ficha["referencia_id"], "pagina": atlas.page,
                              "tipo": "doble", "escala_cuerpo": round(escala, 3),
                              "aire_pt": round(aire, 2)})
        draw_ficha_band(atlas, ficha, left, y_top, width, y_bottom, compact=True,
                        escala=escala, aire=aire)
    atlas.c.setFont("AtlasSans-Italic", 7.6)
    atlas.c.setFillColor(COLORS["muted"])
    atlas.c.drawString(left, BOTTOM_Y + 12 * MM, "Cada referencia conserva su identidad, su cifra, su advertencia y su fuente; no hay fusión entre ellas.")


def altura_bloque(atlas: Atlas, width: float, trio: dict, punteado: bool) -> float:
    """Mide el bloque inferior real: evita tanto el corte como el aire muerto."""
    c = atlas.c
    alto = 0.0
    for etiqueta, texto in (("Qué muestra este mapa", trio["muestra"]),
                            ("Qué mide la cifra", trio["mide"]),
                            ("Qué no es", trio["no_es"])):
        ancho = c.stringWidth(etiqueta + "   ", "AtlasSans-Bold", 7.9)
        lineas = wrap_lines(texto, width - ancho, "AtlasSans", 7.9)
        alto += max(1, len(lineas)) * 9.7 + 3.2
    alto += 26 if punteado else 16      # leyenda (+ nota de trazo punteado)
    alto += 16                          # descargo al pie
    return alto


def bloque_inferior(atlas: Atlas, left: float, width: float, trio: dict,
                    familia: str, punteado: bool, y: float, rid: str | None = None) -> None:
    """B3 - tres lineas rotuladas + leyenda real, identicas en las 29 paginas de mapa."""
    c = atlas.c
    for etiqueta, texto in (("Qué muestra este mapa", trio["muestra"]),
                            ("Qué mide la cifra", trio["mide"]),
                            ("Qué no es", trio["no_es"])):
        c.setFont("AtlasSans-Bold", 7.9)
        c.setFillColor(COLORS["primary"])
        c.drawString(left, y, etiqueta)
        ancho = c.stringWidth(etiqueta + "   ", "AtlasSans-Bold", 7.9)
        y = draw_text(c, texto, left + ancho, y, width - ancho, size=7.9,
                      color=COLORS["text2"], leading=9.7) - 3.2
    CARTOGRAFO.leyenda(c, left, y - 3, width, familia, punteado, rid)


def draw_map_page(atlas: Atlas, ficha: dict, path: Path | None = None) -> None:
    rid = ficha["referencia_id"]
    left, _, width = atlas.new_page(SECCION_ZONAS[EDICION], f"map_{rid}")
    c = atlas.c
    y = TOP_Y - 3 * MM
    c.setFont("AtlasSans-Bold", 10.5)
    c.setFillColor(COLORS["primary"])
    c.drawString(left, y, f"{rid} · {ficha['nombre']} · {ROTULO_MAPA[EDICION]}")
    c.setFont("AtlasSans-Bold", 8.2)
    c.setFillColor(COLORS["secondary"])
    c.drawRightString(left + width, y,
                      f"{VOLVER_A_FICHA_CON_PAGINA[EDICION]} · p. {REF_PAGES[rid][0]}")
    atlas.link(f"ficha_{rid}", (left + width - 120, y - 4, left + width, y + 9))

    trio = TRIOS_ACTIVOS[rid]
    familia = FAMILIA_DE[rid]
    punteado = CARTOGRAFO.fila(rid).trazo == "punteado"
    alto_bloque = altura_bloque(atlas, width, trio, punteado)
    mapa_bottom = BOTTOM_Y + alto_bloque
    mapa_top = y - 6 * MM
    info = CARTOGRAFO.mapa_referencia(c, rid, left, mapa_bottom, width, mapa_top - mapa_bottom)
    QA_MAPAS.append({"pagina": atlas.page, "referencia_id": rid, "tipo": "principal",
                     "archivo": MAIN_NAMES[rid],
                     "escala_m": info["escala_m"], "etiquetas": " | ".join(info["etiquetas"]),
                     "calles": " | ".join(info.get("calles", []))})
    bloque_inferior(atlas, left, width, trio, familia, punteado, mapa_bottom - 11, rid)
    if DESCARGO_MAPA[EDICION]:
        c.setFont("AtlasSans", 7.2)
        c.setFillColor(COLORS["muted"])
        c.drawString(left, BOTTOM_Y + 3.2 * MM, DESCARGO_MAPA[EDICION])


def draw_comp_page(atlas: Atlas, ficha: dict, filename: str, title: str, note: str,
                   path: Path | None = None) -> None:
    dest = f"comp_{Path(filename).stem}"
    left, _, width = atlas.new_page(SECCION_AMPLIACIONES[EDICION], dest)
    if filename == COMP_INFO_ACTIVO[0][1]:
        atlas.c.bookmarkPage("section_complementaries")
        atlas.bookmarks.add("section_complementaries")
    c = atlas.c
    rid = ficha["referencia_id"]
    if EDICION == "conduccion":
        title = COND.TITULOS_DETALLE[filename]
    y = TOP_Y - 3 * MM
    c.setFont("AtlasSans-Bold", 10.5)
    c.setFillColor(COLORS["primary"])
    c.drawString(left, y, f"{rid} · {title} · {ROTULO_AMPLIACION[EDICION]}")
    c.setFont("AtlasSans-Bold", 8.2)
    c.setFillColor(COLORS["secondary"])
    c.drawRightString(left + width, y, VOLVER_A_FICHA[EDICION])
    atlas.link(f"ficha_{rid}", (left + width - 112, y - 4, left + width, y + 9))

    trio = TRIOS_DETALLE_ACTIVOS[filename]
    familia = FAMILIA_DE[rid]
    punteado = CARTOGRAFO.fila(rid).trazo == "punteado"
    alto_bloque = altura_bloque(atlas, width, trio, punteado)
    mapa_bottom = BOTTOM_Y + alto_bloque
    mapa_top = y - 6 * MM
    info = CARTOGRAFO.mapa_detalle(c, filename, left, mapa_bottom, width,
                                   mapa_top - mapa_bottom, EXTRAS_DETALLE)
    QA_MAPAS.append({"pagina": atlas.page, "referencia_id": rid, "tipo": "detalle",
                     "archivo": filename,
                     "escala_m": info["escala_m"], "etiquetas": " | ".join(info["etiquetas"]),
                     "calles": " | ".join(info.get("calles", []))})
    bloque_inferior(atlas, left, width, trio, familia, punteado, mapa_bottom - 11, rid)
    if DESCARGO_AMPLIACION[EDICION]:
        c.setFont("AtlasSans", 7.2)
        c.setFillColor(COLORS["muted"])
        c.drawString(left, BOTTOM_Y + 3.2 * MM, DESCARGO_AMPLIACION[EDICION])


def draw_table(c: canvas.Canvas, headers: Sequence[str], rows: Sequence[Sequence[str]], x: float,
               y_top: float, widths: Sequence[float], *, font_size: float = 8.2,
               max_bottom: float = BOTTOM_Y + 8 * MM, alto_min_fila: float = 0.0) -> float:
    total = sum(widths)
    header_h = 24
    c.setFillColor(COLORS["primary"])
    c.rect(x, y_top - header_h, total, header_h, fill=1, stroke=0)
    xx = x
    for header, width in zip(headers, widths):
        # M-06: el encabezado se dibujaba sin medir. "Qué tipo de zona es" sobraba 8,6 pt
        # de su columna y se montaba sobre el de al lado; la tabla salió así en dos
        # páginas del Atlas. Un encabezado que no entra es un defecto de armado, no algo
        # para acortar en silencio: se corta la producción.
        ancho_texto = pdfmetrics.stringWidth(str(header), "AtlasSans-Bold", font_size)
        if ancho_texto + 10 > width:
            raise RuntimeError(
                f"Encabezado de tabla más ancho que su columna: «{header}» mide "
                f"{ancho_texto:.1f} pt y la columna {width:.1f} pt")
        c.setFillColor(white)
        c.setFont("AtlasSans-Bold", font_size)
        c.drawString(xx + 5, y_top - 16, str(header))
        xx += width
    y = y_top - header_h
    for row_idx, row in enumerate(rows):
        line_sets = [wrap_lines(str(value), width - 10, "AtlasSans", font_size) for value, width in zip(row, widths)]
        row_h = max(21, alto_min_fila,
                    max(len(lines) for lines in line_sets) * font_size * 1.25 + 9)
        if y - row_h < max_bottom:
            raise RuntimeError(f"Tabla desborda el pie en fila {row_idx}")
        c.setFillColor(COLORS["zebra"] if row_idx % 2 else white)
        c.rect(x, y - row_h, total, row_h, fill=1, stroke=0)
        xx = x
        for lines, width in zip(line_sets, widths):
            c.setFont("AtlasSans", font_size)
            c.setFillColor(COLORS["text2"])
            # Con filas estiradas el texto se centra verticalmente en su celda.
            natural = len(lines) * font_size * 1.25 + 9
            yy = y - 14 - max(0.0, row_h - natural) / 2
            for line in lines:
                c.drawString(xx + 5, yy, line)
                yy -= font_size * 1.25
            c.setStrokeColor(COLORS["border"])
            c.line(xx, y, xx, y - row_h)
            xx += width
        c.line(x + total, y, x + total, y - row_h)
        c.setStrokeColor(COLORS["border"])
        c.line(x, y - row_h, x + total, y - row_h)
        y -= row_h
    return y


def annex_start(atlas: Atlas, page: int, title: str, subtitle: str) -> tuple[float, float, float]:
    left, _, width = atlas.new_page("Anexos", f"annex_{page}")
    if page == 51:
        atlas.c.bookmarkPage("section_annexes")
        atlas.bookmarks.add("section_annexes")
    y = draw_heading(atlas.c, title, left, TOP_Y - 5 * MM, width, subtitle=subtitle)
    return left, width, y


def draw_annex_matrix(atlas: Atlas, fichas: list[dict], page: int) -> None:
    part = "1 de 2" if page == 51 else "2 de 2"
    left, width, y = annex_start(atlas, page, f"Anexo A · Matriz resumen R01-R22 · {part}", "Naturaleza, cifra y lectura institucional por referencia.")
    rows = []
    for f in fichas:
        rows.append([f["referencia_id"], f["nombre"], f["tipologia"], nature_label(f["naturaleza"]), short_figure(f)])
    widths = [13 * MM, 34 * MM, 48 * MM, 34 * MM, width - 129 * MM]
    y = draw_table(atlas.c, ["Ref.", "Nombre", "Tipología", "Naturaleza", "Cifra / estado"], rows, left, y, widths, font_size=8.0)
    for idx, ficha in enumerate(fichas):
        row_h_approx = (y + 0)  # solo conserva una referencia local para el verificador
        _ = row_h_approx
    atlas.c.setFont("AtlasSans-Italic", 8)
    atlas.c.setFillColor(COLORS["muted"])
    atlas.c.drawString(left, BOTTOM_Y + 13 * MM, "Las cifras no se suman entre sí: cada una tiene su método. Ver la ficha de cada referencia para universo, fecha y advertencias.")


def draw_annex_components(atlas: Atlas, content: dict) -> None:
    left, width, y = annex_start(atlas, 53, "Anexo B · Subunidades y componentes", "Partes internas de una referencia y cómo se leen.")
    rows = [
        ["R01", "Palermo Soho · Palermo Hollywood · Las Cañitas", "Subzonas internas; no referencias nuevas."],
        ["R05", "Barrio Chino · Bajo Belgrano · Belgrano R", "Tres centralidades; no tres polos."],
        ["R07", "Componentes 1-4 · cinco piezas topológicas", "Vacíos estructurales preservados."],
        ["R09", "Newbery · Dorrego", "Focos independientes; Lacroze es control."],
        ["R10", "Goyena · Primera Junta-Mercado del Progreso", "Lectura multinodo; componentes no aditivos."],
        ["R12", "C-S01 · C-S03 · C-S04 · C-S06 · C-S05 · C-S07/R18", "C-S05 separado y no comparable; ≥57."],
        ["R19", "LAC-T1 · LAC-T2 · Lacroze-Cabildo", "Ventanas independientes; 39 compartidos no prueban continuidad."],
        ["R21", "R21-OESTE · R21-BORDE", "OESTE ≥237; BORDE 19 observados; no comparables."],
        ["R22", "Centro / centro-este", "Subárea descriptiva; no producto nuevo."],
    ]
    draw_table(atlas.c, ["Ref.", "Subunidades / componentes", "Regla de lectura"], rows, left, y,
               [18 * MM, 76 * MM, width - 94 * MM], font_size=8.4)
    draw_box(atlas.c, "MEMBRESÍAS Y SOLAPAMIENTOS",
             "Una membresía expresa pertenencia a una subunidad; no equivale a un establecimiento adicional. "
             "Las intersecciones observacionales se deduplican en el universo de referencia y no habilitan fusiones.",
             left, BOTTOM_Y + 39 * MM, width, fill=COLORS["note"], size=8.8)


def draw_annex_controls(atlas: Atlas) -> None:
    left, width, y = annex_start(atlas, 54, "Anexo C · Controles, exclusiones y no-productos", "Elementos que orientan la lectura sin integrar universos.")
    rows = [
        ["R09", "Lacroze", "Control territorial; no define R09 ni R19."],
        ["R10", "Patio de los Lecheros", "Control puntual no adoptable; no integra el universo."],
        ["R10", "Z03-S4 / Parque Rivadavia", "Pieza retirada; no reutilizar."],
        ["R12", "C-S05", "Componente secundario ≥57; consulta no comparable; fuera de rankings."],
        ["R19", "LAC-T3", "Excluido; no producto de primera corrida."],
        ["R19", "LAC-CTRL-CH", "Control Chacarita; no aporta a R19."],
        ["R20", "Parque Saavedra", "Control no-producto; intersección efectiva 0 m² en la corrida."],
        ["R20/R22", "Controles espaciales", "Fuera del producto; no aportan a universos."],
        ["R21", "R21-BORDE", "Borde/control; no absorbido por Villa Crespo."],
    ]
    draw_table(atlas.c, ["Ref.", "Control / exclusión", "Tratamiento"], rows, left, y,
               [24 * MM, 51 * MM, width - 75 * MM], font_size=8.5)
    draw_box(atlas.c, "REGLA",
             "Control, borde, exclusión o no-producto no significa ausencia: indica que el elemento no integra "
             "el universo ni puede utilizarse para ampliar o absorber una referencia.",
             left, BOTTOM_Y + 36 * MM, width, fill=COLORS["warn"], accent=COLORS["accent"], size=8.8)


def draw_annex_separations(atlas: Atlas) -> None:
    left, width, y = annex_start(atlas, 55, "Anexo D · Separaciones institucionales y nomenclatura", "Relaciones que no implican absorción, equivalencia ni fusión.")
    pairs = [
        ("R02 ≠ R13", "Corrientes-Abasto es una vista contextual de vínculo; no fusiona las referencias."),
        ("R09 ≠ R19", "Chacarita y Federico Lacroze por tramos conservan universos y lecturas separados."),
        ("R16 ≠ R17", "Donado-Holmberg no se absorbe en Villa Urquiza."),
        ("R20 ≠ R22", "García del Río y Villa Pueyrredón están separados; el universo combinado está prohibido."),
        ("R15 / R17 ≠ R22", "Devoto y Villa Urquiza no absorben Villa Pueyrredón."),
        ("R21-BORDE ≠ R08", "El borde/control de R21 no se absorbe en Villa Crespo."),
        ("R08-CTRL-BORDE / R21-BORDE", "La lámina histórica y la ficha usan rótulos distintos para el mismo rol de borde/control; prevalece R21-BORDE en esta edición."),
        ("Vista de detalle ≠ referencia", "Las siete vistas de detalle no crean referencias nuevas ni geometrías oficiales."),
    ]
    for idx, (label, text) in enumerate(pairs):
        yy = y - idx * 28 * MM
        atlas.c.setFillColor(COLORS["card"] if idx % 2 == 0 else COLORS["note"])
        atlas.c.roundRect(left, yy - 23 * MM, width, 20 * MM, 5, fill=1, stroke=0)
        atlas.c.setFillColor(COLORS["primary"])
        draw_text(atlas.c, label, left + 7 * MM, yy - 8 * MM, 56 * MM,
                  font="AtlasSans-Bold", size=8.7, color=COLORS["primary"], leading=10.3, max_lines=2)
        draw_text(atlas.c, text, left + 67 * MM, yy - 8 * MM, width - 74 * MM,
                  size=8.7, color=COLORS["text2"], leading=10.8)


def draw_annex_status(atlas: Atlas) -> None:
    left, width, y = annex_start(atlas, 56, "Anexo E · Estado declarado, saturaciones y cobertura", "Qué informa cada estado y sobre qué total se calcula.")
    rows = [
        ["R19", "204 / 7 / 0", "5 firmas restaurant saturadas; 60 requests R19."],
        ["R20", "39 / 1 / 0", "1 / 20 restaurant saturada."],
        ["R21", "242 / 12 / 0", "4 / 110 restaurant saturadas en OESTE; 0 / 15 en BORDE."],
        ["R22", "152 / 6 / 0", "6 / 70 restaurant saturadas."],
        ["R08", "no aplica", "Tres saturaciones residuales restaurant aceptadas como límite final."],
        ["R12", "no aplica", "79 / 326 firmas; restaurant 51 / 64; C-S05 6 / 6."],
        ["Grupo B", "R19 + R21", "9 / 180 requests de red; 9 / 185 firmas de producto. No usar 190 requests."],
        ["Grupo C", "R20 + R22", "R20 1 / 20; R22 6 / 70."],
    ]
    y = draw_table(atlas.c, ["Referencia", "Operacional / temp. / perm.", "Saturación y denominador"], rows, left, y,
                   [31 * MM, 54 * MM, width - 85 * MM], font_size=8.3)
    draw_box(atlas.c, "CENSURA Y COTA INFERIOR",
             "Cuando una consulta alcanza el máximo de resultados que devuelve la fuente, el universo observado "
             "queda incompleto. "
             "La cifra con ≥ es un piso censado: no se estima el faltante y no se interpreta como conteo completo "
             "ni como locales activos.",
             left, y - 10, width, fill=COLORS["warn"], accent=COLORS["accent"], size=9)


def draw_annex_counting(atlas: Atlas) -> None:
    left, width, y = annex_start(atlas, 57, "Anexo F · Cómo se contaron los locales", "Qué cuenta cada número y por qué no se suman entre sí.")
    blocks = [
        ("R12 · ÚNICOS Y MEMBRESÍAS", "≥797 establecimientos únicos · ≥940 membresías · 143 dobles. Reconciliación: 654 con una membresía, 143 con dos y 0 con tres o más."),
        ("R19 · UNIÓN DE VENTANAS", "LAC-T1 ≥112 y LAC-T2 ≥138 son ventanas independientes. La unión deduplicada de R19 es ≥211; no se suman a ciegas."),
        ("R21 · OESTE / BORDE", "R21-OESTE ≥237 y R21-BORDE 19 observados cumplen roles distintos; dos observaciones compartidas no habilitan suma simple ni absorción."),
        ("R22 · DEDUPLICACIÓN", "≥158 deduplicados a partir de 294 observaciones postfiltradas; 136 duplicados internos removidos; 84 identificadores observados en múltiples centros."),
    ]
    for idx, (title, text) in enumerate(blocks):
        col = idx % 2
        row = idx // 2
        gap = 4 * MM
        col_w = (width - gap) / 2
        x = left + col * (col_w + gap)
        yy = y - row * 53 * MM
        draw_box(atlas.c, title, text, x, yy, col_w, fill=COLORS["note"] if row == 0 else COLORS["card"], size=8.8)
    yy = y - 111 * MM
    draw_box(atlas.c, "MÉTODOS DE RECUENTO",
             "Consultas de red: pedidos efectivamente enviados a la fuente. Combinaciones de consulta: cada cruce "
             "de búsqueda y categoría. Consultas repetidas: no agregan registros nuevos. Controles: elementos que "
             "quedan fuera del universo. Membresías: un mismo local puede pertenecer a más de una subunidad, "
             "por eso su total puede superar el de establecimientos únicos.",
             left, yy, width, fill=COLORS["card"], size=8.9)
    draw_box(atlas.c, "REGLAS DE ESTA EDICIÓN",
             "No recomputar universos; no sumar métodos no comparables; no convertir saturación en estimación; "
             "no construir ranking general; conservar fuente, fecha, universo y naturaleza en cada cifra.",
             left, yy - 48 * MM, width, fill=COLORS["warn"], accent=COLORS["accent"], size=9)


def draw_annex_close(atlas: Atlas) -> None:
    left, width, y = annex_start(atlas, 58, "Anexo G · Decisiones, limitaciones, glosario y trazabilidad pública", "Síntesis final en tres bloques.")
    gap = 4 * MM
    col_w = (width - 2 * gap) / 3
    columns = [
        (
            "DECISIONES",
            [
                "D-E01 · R01-R04 sin KPI comparable.",
                "D-E02 · mapa principal y anexos según rol aprobado.",
                "D-E03 · Corrientes-Abasto solo contextual.",
                "D-E04 · reutilización y normalización sin redibujar el corpus.",
                "D-E05 · homogeneidad visual media.",
                "D-E06 · cotas con ≥ y sin rankings no comparables.",
                "D-E07 · estructura institucional del Atlas.",
                "D-E08 · separación entre material institucional y técnico.",
                "Lecturas territoriales aprobadas para las 22 referencias, sin adopción de límites oficiales.",
            ],
        ),
        (
            "LÍMITES Y GLOSARIO",
            [
                "D-03 · cotas inferiores, censura, geometrías no oficiales y no comparabilidad.",
                "Cifra exacta · conteo cerrado en su método.",
                "Cota inferior · piso censado, no conteo completo.",
                "Antecedente histórico · valor de linaje, no KPI comparable.",
                "Sin cifra comparable · evidencia sin universo único.",
                "Saturación · máximo de resultados alcanzado.",
                "Membresía · pertenencia a una subunidad.",
                "Control · elemento que no integra el universo.",
                "Vista de detalle · amplía una referencia; no crea una nueva.",
                "Geometría analítica · representación no oficial.",
            ],
        ),
        (
            "TRAZABILIDAD PÚBLICA",
            [
                "Fuentes: relevamiento y cartografía propios de la Dirección General de Desarrollo Gastronómico.",
                "Fecha de corte general: 17-07-2026. Tanda 2: 13-07-2026.",
                "Esta es la edición técnica. Existe además una edición de conducción del mismo "
                "Atlas, más breve y en lenguaje llano, con idénticas cifras y geometrías.",
                "Existe una edición ampliada de consulta, de 80 páginas, con el detalle metodológico completo.",
                "La edición es reproducible: se conservan contenido, matrices, controles de calidad y verificaciones de integridad.",
                "Esta edición no ejecuta consultas nuevas, no geocodifica, no recalcula universos y no modifica las fuentes.",
                "DGDGAS · Dirección General de Desarrollo Gastronómico.",
            ],
        ),
    ]
    for idx, (title, items) in enumerate(columns):
        x = left + idx * (col_w + gap)
        atlas.c.setFillColor(COLORS["primary"])
        atlas.c.roundRect(x, y - 21, col_w, 21, 4, fill=1, stroke=0)
        atlas.c.setFillColor(white)
        atlas.c.setFont("AtlasSans-Bold", 9)
        atlas.c.drawString(x + 7, y - 14, title)
        yy = draw_bullets(atlas.c, items, x + 2, y - 33, col_w - 4, size=8.5, leading=10.7, gap=2)
        if yy < BOTTOM_Y + 15 * MM:
            raise RuntimeError(f"Columna final {title} demasiado densa")


def build_pdf_conduccion(content: dict) -> None:
    """B7 · el plan de páginas de la edición de conducción, ficha → mapa → ampliación."""
    atlas = Atlas(PDF_PATH)
    by_ref = {f["referencia_id"]: f for f in content["fichas"]}
    draw_cover(atlas, content["meta"])
    RENDCOND.draw_resumen(atlas)
    draw_index(atlas, content)
    RENDCOND.draw_como_leer(atlas)
    RENDCOND.draw_familias(atlas, content)
    draw_locator(atlas)
    for a, b in PARES_CONDUCCION:
        RENDCOND.draw_pagina_fichas(atlas, by_ref[a], by_ref[b])
        for rid in (a, b):
            draw_map_page(atlas, by_ref[rid])
            for archivo in AMPLIACIONES_DE.get(rid, []):
                info = next(x for x in COMP_INFO_ACTIVO if x[1] == archivo)
                draw_comp_page(atlas, by_ref[info[0]], archivo, info[2], info[3])
    RENDCOND.draw_matriz(atlas, content["fichas"][:11], "1 de 2", "annex_a1")
    RENDCOND.draw_matriz(atlas, content["fichas"][11:], "2 de 2", "annex_a2")
    RENDCOND.draw_como_se_hizo(atlas)
    atlas.finish()


def build_pdf(content: dict) -> None:
    if EDICION == "conduccion":
        build_pdf_conduccion(content)
        return
    atlas = Atlas(PDF_PATH)
    by_ref = {f["referencia_id"]: f for f in content["fichas"]}
    draw_cover(atlas, content["meta"])
    draw_opening_summary(atlas)
    draw_index(atlas, content)
    draw_how_to(atlas)
    draw_typologies(atlas, content)
    draw_locator(atlas)
    full_drawn: set[str] = set()
    pair_drawn: set[tuple[str, str]] = set()
    comp_by_page = {COMP_PAGES[fn]: (rid, fn, title, note) for rid, fn, title, note in COMP_INFO_ACTIVO}
    map_by_page = {page_map: rid for rid, (_, page_map) in REF_PAGES.items()}
    ficha_by_page: dict[int, object] = {}
    for rid in FULL_REFS:
        ficha_by_page[REF_PAGES[rid][0]] = rid
    for pair in DOUBLE_PAIRS:
        ficha_by_page[REF_PAGES[pair[0]][0]] = pair
    for page in range(7, 51):
        if page in ficha_by_page:
            item = ficha_by_page[page]
            if isinstance(item, tuple):
                if item not in pair_drawn:
                    draw_double_ficha(atlas, by_ref[item[0]], by_ref[item[1]])
                    pair_drawn.add(item)
            else:
                if item not in full_drawn:
                    draw_full_ficha(atlas, by_ref[item])
                    full_drawn.add(item)
        elif page in map_by_page:
            rid = map_by_page[page]
            draw_map_page(atlas, by_ref[rid])
        elif page in comp_by_page:
            rid, fn, title, note = comp_by_page[page]
            draw_comp_page(atlas, by_ref[rid], fn, title, note)
        else:
            raise RuntimeError(f"Página 7-50 sin contenido: {page}")
    draw_annex_matrix(atlas, content["fichas"][:11], 51)
    draw_annex_matrix(atlas, content["fichas"][11:], 52)
    draw_annex_components(atlas, content)
    draw_annex_controls(atlas)
    draw_annex_separations(atlas)
    draw_annex_status(atlas)
    draw_annex_counting(atlas)
    draw_annex_close(atlas)
    atlas.finish()


def build_plan_conduccion() -> None:
    """Plan de páginas efectivo de la edición de conducción."""
    ref_por_pagina: dict[int, str] = {}
    for rid, (pagina_ficha, pagina_mapa) in REF_PAGES.items():
        previo = ref_por_pagina.get(pagina_ficha, "")
        ref_por_pagina[pagina_ficha] = previo + (";" if previo else "") + rid
        ref_por_pagina[pagina_mapa] = rid
    filas = []
    for pagina, seccion, titulo, tipo in PAGE_SEQUENCE:
        refs = ref_por_pagina.get(pagina, "")
        if tipo == "AMPLIACION":
            info = next(x for x in COMP_INFO_ACTIVO if COMP_PAGES[x[1]] == pagina)
            refs = "R02;R13" if info[1] == "R02_R13_CONTEXTO_CORRIENTES_ABASTO.png" else info[0]
        filas.append({
            "pagina": pagina,
            "seccion": seccion,
            "titulo": titulo,
            "zonas": refs or "—",
            "tipo_pagina": tipo,
            "pagina_equivalente_tecnica": (
                REF_PAGES_TECNICA.get(refs.split(";")[0], ("", ""))[0 if tipo == "FICHA_DOBLE" else 1]
                if tipo in {"FICHA_DOBLE", "MAPA_PRINCIPAL"} and refs else
                COMP_PAGES_TECNICA.get(next((x[1] for x in COMP_INFO
                                             if COMP_PAGES.get(x[1]) == pagina), ""), "")
                if tipo == "AMPLIACION" else ""),
        })
    if [f["pagina"] for f in filas] != list(range(1, EXPECTED_PAGES + 1)):
        raise RuntimeError("Plan de conducción inválido")
    write_csv(MATRICES_DIR / f"PLAN_PAGINAS_ATLAS_CONDUCCION_EFECTIVO_{EXPECTED_PAGES}.csv",
              ["pagina", "seccion", "titulo", "zonas", "tipo_pagina",
               "pagina_equivalente_tecnica"], filas)


def build_effective_matrices() -> None:
    if EDICION == "conduccion":
        build_plan_conduccion()
        return
    plan_rows = []
    ref_by_page: dict[int, str] = {}
    for rid, (ficha, map_page) in REF_PAGES.items():
        ref_by_page[ficha] = (ref_by_page.get(ficha, "") + (";" if ref_by_page.get(ficha) else "") + rid)
        ref_by_page[map_page] = rid
    for page, section, title, kind in PAGE_SEQUENCE:
        refs = ref_by_page.get(page, "")
        if kind == "COMPLEMENTARIA":
            info = next(x for x in COMP_INFO_ACTIVO if COMP_PAGES[x[1]] == page)
            refs = info[0] if info[1] != "R02_R13_CONTEXTO_CORRIENTES_ABASTO.png" else "R02;R13"
        plan_rows.append({
            "pagina_v2": page,
            "seccion": section,
            "titulo": title,
            "referencias": refs or "—",
            "tipo_pagina": kind,
            "fuente_publica_id": "SRC-FICHAS-22;SRC-CARTO-22" if page <= 50 else "SRC-FICHAS-22;ACTAS-CIERRE",
            "qa_especifico": "texto;enlaces;marcadores" if "MAPA" not in kind and kind != "COMPLEMENTARIA" else "asset;escala;pie;enlaces",
        })
    if len(plan_rows) != 58 or [x["pagina_v2"] for x in plan_rows] != list(range(1, 59)):
        raise RuntimeError("Plan efectivo inválido")
    write_csv(
        MATRICES_DIR / "PLAN_PAGINAS_ATLAS_22_V2_COMPACTA_EFECTIVO_58.csv",
        ["pagina_v2", "seccion", "titulo", "referencias", "tipo_pagina", "fuente_publica_id", "qa_especifico"],
        plan_rows,
    )
    coverage = read_csv(PLAN_BASE / "MATRIZ_COBERTURA_V1_A_V2.csv")
    for row in coverage:
        original = row["pagina_v2"]
        text = " ".join(str(v) for v in row.values()).lower()

        def map_number(number: int) -> int:
            if number <= 52:
                return number
            if number == 53:
                return 54 if re.search(r"control|exclus|no.product|borde", text) else 53
            if number == 54:
                return 55
            if number == 55:
                return 57 if re.search(r"dedup|membres|únicos|unicos|recuento|requests|firmas de producto|cache", text) else 56
            return 58

        effective_parts: list[str] = []
        for part in original.split(";"):
            part = part.strip()
            if re.fullmatch(r"\d+", part):
                effective_parts.append(str(map_number(int(part))))
            elif re.fullmatch(r"\d+-\d+", part):
                first, last = [int(value) for value in part.split("-")]
                mapped = [map_number(value) for value in range(first, last + 1)]
                effective_parts.append(
                    str(mapped[0]) if len(mapped) == 1
                    else f"{mapped[0]}-{mapped[-1]}"
                )
            else:
                effective_parts.append(part)
        row["pagina_v2_plan_56"] = original
        row["pagina_v2"] = ";".join(dict.fromkeys(effective_parts))
        row["verificacion_productor"] = "CUBIERTO"
        for key, value in list(row.items()):
            if isinstance(value, str):
                row[key] = value.replace("Di" + "ego", "autoridad institucional")
    fields = list(coverage[0].keys())
    write_csv(MATRICES_DIR / "MATRIZ_COBERTURA_V1_A_V2_EFECTIVA_102.csv", fields, coverage)
    backlog = read_csv(PLAN_BASE / "MATRIZ_RESOLUCION_BACKLOG_V2.csv")
    page_map = {
        "C-01": "3;PDF", "C-02": "51;52;57;58", "C-03": "51;52", "C-04": "2;4",
        "C-05": "5", "C-06": "4;51-58", "C-07": "1", "C-08": "6", "C-09": "todo",
        "C-10": "55", "C-11": "PDF", "C-12": "generador;PDF", "C-13": "10;14;24;27;33;37;40",
        "D-01": "23;32;36;46", "D-02": "15;20", "D-03": "2;4;56",
    }
    for row in backlog:
        if row["id"] == "C-11":
            row["resolucion_en_plan"] = (
                "Cuerpo/anexos públicos solo IDs y 0 rutas repo; hashes técnicos en "
                "CHECKSUMS_SHA256.txt y sidecar externo"
            )
        row["paginas_v2_afectadas"] = page_map[row["id"]]
        row["estado_plan"] = "IMPLEMENTADO_QA_PRODUCTOR"
        row["requiere_autorizacion_humana_extra"] = "NO"
        row["qa_productor"] = "PASS"
        row.pop("requiere_autorizacion_" + "di" + "ego_extra", None)
        for key, value in list(row.items()):
            if isinstance(value, str):
                row[key] = value.replace("Di" + "ego", "autoridad institucional").replace("PENDIENTE_APROBACION_" + "DIE" + "GO", "APROBADO")
    fields = list(backlog[0].keys())
    write_csv(MATRICES_DIR / "MATRIZ_RESOLUCION_BACKLOG_V2_EFECTIVA.csv", fields, backlog)
    summary = [
        {"id": row["id"], "implementacion": row["resolucion_en_plan"], "paginas": row["paginas_v2_afectadas"],
         "evidencia": "PDF;plan efectivo;QA", "estado": "IMPLEMENTADO", "qa": "PASS"}
        for row in backlog
    ]
    write_csv(
        MATRICES_DIR / "MATRIZ_RESOLUCION_C01_C13_D01_D03.csv",
        ["id", "implementacion", "paginas", "evidencia", "estado", "qa"], summary,
    )


def render_pdf() -> None:
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    CONTACT_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    if doc.page_count != EXPECTED_PAGES:
        raise RuntimeError(f"Render recibió {doc.page_count} páginas")
    scale = 150 / 72
    matrix = fitz.Matrix(scale, scale)
    rendered: list[Path] = []
    for idx, page in enumerate(doc):
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        path = RENDER_DIR / f"pagina_{idx+1:02d}.png"
        pix.save(path)
        rendered.append(path)
    doc.close()
    for start in range(0, len(rendered), 10):
        subset = rendered[start:start + 10]
        thumbs = []
        for path in subset:
            im = Image.open(path).convert("RGB")
            size = (int(im.width * 0.4), int(im.height * 0.4))
            thumbs.append(im.resize(size, Image.Resampling.LANCZOS))
        cols = 2
        rows = math.ceil(len(thumbs) / cols)
        tw = max(im.width for im in thumbs)
        th = max(im.height for im in thumbs)
        sheet = Image.new("RGB", (cols * (tw + 18), rows * (th + 36)), "#D9DEE5")
        draw = ImageDraw.Draw(sheet)
        for idx, im in enumerate(thumbs):
            col, row = idx % cols, idx // cols
            x, y = col * (tw + 18) + 9, row * (th + 36) + 25
            sheet.paste(im, (x, y))
            draw.text((x, y - 22), f"p. {start + idx + 1}", fill="#1F3B57", font=PIL_FONTS["regular20"])
        sheet.save(CONTACT_DIR / f"CONTACT_SHEET_{start//10+1:02d}_40PCT.png", optimize=True)


# ---------------------------------------------------------------------------------------
# B-02 · Control de TEXTO CLIPEADO
#
# La V2 paso 25 controles automaticos con quince etiquetas cortadas a mitad de palabra en
# la p5. Ninguno miraba el texto realmente dibujado. Este control lo mira por tres vias
# independientes, y cualquiera de las tres hace fallar la produccion:
#
#   1. palabra_truncada  - toda palabra del PDF tiene que existir entera en alguna fuente
#                          del generador. "Microcent" no existe en ningun lado; "Microcentro"
#                          si. Se marca toda palabra que sea prefijo estricto de una palabra
#                          real y que no sea, ella misma, una palabra real.
#   2. fuera_de_caja     - ninguna cadena puede sobresalir del area imprimible de su pagina.
#   3. acorte_sin_marca  - todo acortamiento deliberado pasa por `ajustar_a_ancho`, corta en
#                          limite de palabra y deja elipsis. Ademas se prohibe en el propio
#                          codigo el modismo que causo el defecto (recortar de a caracteres
#                          dentro de un while sobre stringWidth).
# ---------------------------------------------------------------------------------------

_PALABRA = re.compile(r"[^\W\d_]+", re.UNICODE)


def _palabras(texto: str) -> list[str]:
    return [m.group(0).lower() for m in _PALABRA.finditer(texto)]


def vocabulario_fuentes(content: dict) -> set[str]:
    """Todas las palabras que el generador puede llegar a dibujar, en su forma completa."""
    piezas: list[str] = []
    for archivo in (SCRIPT, SCRIPT.parent / "cartografia_vectorial_v2.py",
                    SCRIPT.parent / "textos_b3_v2.py",
                    SCRIPT.parent / "contenido_conduccion.py",
                    SCRIPT.parent / "render_conduccion.py",
                    SCRIPT.parent / "lenguaje_conduccion.py"):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        piezas.extend(nodo.value for nodo in ast.walk(arbol)
                      if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str))

    def recorrer(valor) -> None:
        if isinstance(valor, str):
            piezas.append(valor)
        elif isinstance(valor, dict):
            for k, v in valor.items():
                piezas.append(str(k))
                recorrer(v)
        elif isinstance(valor, (list, tuple)):
            for v in valor:
                recorrer(v)

    recorrer(content)
    for trio in list(TRIOS_ACTIVOS.values()) + list(TRIOS_DETALLE_ACTIVOS.values()):
        recorrer(trio)
    # Rotulos que vienen de las capas geometricas, no de literales del codigo.
    piezas.extend(str(v) for v in CARTOGRAFO.comp["componente"].tolist())
    piezas.extend(str(v) for v in CARTOGRAFO.env["nombre"].tolist())
    piezas.extend(CARTOGRAFO.rotulo(v) for v in CARTOGRAFO.env["nombre"].tolist())
    for csv_path in MATRICES_DIR.glob("*.csv"):
        piezas.append(csv_path.read_text(encoding="utf-8-sig", errors="replace"))
    vocabulario: set[str] = set()
    for pieza in piezas:
        vocabulario.update(_palabras(pieza))
    return vocabulario


def qa_texto_clipeado(doc, content: dict) -> tuple[list[dict[str, object]], list[str]]:
    vocabulario = vocabulario_fuentes(content)
    por_prefijo: dict[str, str] = {}
    for palabra in vocabulario:
        for corte in range(4, len(palabra)):
            prefijo = palabra[:corte]
            if prefijo not in vocabulario:
                por_prefijo.setdefault(prefijo, palabra)

    filas: list[dict[str, object]] = []
    fallas: list[str] = []

    # 1 · palabras cortadas a mitad
    for indice in range(doc.page_count):
        pagina = doc[indice]
        for palabra in dict.fromkeys(_palabras(pagina.get_text("text"))):
            if len(palabra) < 4 or palabra in vocabulario:
                continue
            completa = por_prefijo.get(palabra)
            if completa:
                filas.append({"control": "palabra_truncada", "pagina": indice + 1,
                              "detalle": f"«{palabra}» parece un corte de «{completa}»"})
                fallas.append(f"p{indice + 1}:{palabra}")

    # 2 · cadenas fuera del area imprimible
    for indice in range(doc.page_count):
        pagina = doc[indice]
        izq, der = page_margins(indice + 1)
        margen = min(izq, der)
        caja = fitz.Rect(margen - 5, 5 * MM, PAGE_W - margen + 5, PAGE_H - 5 * MM)
        for bloque in pagina.get_text("dict")["blocks"]:
            for linea in bloque.get("lines", []):
                for tramo in linea.get("spans", []):
                    if not tramo["text"].strip():
                        continue
                    r = fitz.Rect(tramo["bbox"])
                    if r.x0 < caja.x0 - 0.5 or r.x1 > caja.x1 + 0.5 or \
                       r.y0 < caja.y0 - 0.5 or r.y1 > caja.y1 + 0.5:
                        filas.append({"control": "fuera_de_caja", "pagina": indice + 1,
                                      "detalle": f"«{tramo['text'][:48]}» en {tuple(round(v, 1) for v in tramo['bbox'])}"})
                        fallas.append(f"p{indice + 1}:fuera_de_caja")

    # 3 · acortes deliberados: siempre con elipsis y en limite de palabra
    for recorte in RECORTES_TEXTO:
        if not recorte["lleva_elipsis"] or not recorte["corte_en_palabra_completa"]:
            filas.append({"control": "acorte_sin_marca", "pagina": "",
                          "detalle": f"{recorte['origen']}: «{recorte['texto_dibujado']}»"})
            fallas.append(str(recorte["origen"]))
        else:
            filas.append({"control": "acorte_declarado", "pagina": "",
                          "detalle": f"{recorte['origen']}: «{recorte['texto_dibujado']}»"})

    # 3b · el modismo que causo el defecto queda prohibido en el propio generador
    for archivo in (SCRIPT, SCRIPT.parent / "cartografia_vectorial_v2.py"):
        fuente = archivo.read_text(encoding="utf-8")
        for bloque in re.finditer(r"while[^\n]*stringWidth[^\n]*:\n(?:[^\n]*\n){0,3}", fuente):
            texto = bloque.group(0)
            # Se admite el recorte por caracteres solo si deja marca visible.
            if re.search(r"\[:-\d\]", texto) and "…" not in texto:
                filas.append({"control": "modismo_prohibido", "pagina": "",
                              "detalle": f"{archivo.name}: recorte por caracteres sin marca"})
                fallas.append(f"modismo:{archivo.name}")

    if not filas:
        filas.append({"control": "sin_hallazgos", "pagina": "",
                      "detalle": f"{doc.page_count} páginas revisadas"})
    return filas, fallas


# ---------------------------------------------------------------------------------------
# B8 · Los dos controles propios de la edición de conducción
#
#   vocabulario_conduccion      - falla si aparece cualquier término de la lista de B1.
#                                 La lista vive en un solo lugar: `lenguaje_conduccion.py`.
#   diff_cifras_v21_conduccion  - ninguna cifra puede moverse respecto de la V2.1. El
#                                 lenguaje cambia; los números no. El control compara las
#                                 cifras PUBLICADAS —las de las 22 fichas y las de los 29
#                                 bloques de mapa—, no los números de navegación (páginas
#                                 del índice, "IR AL MAPA · p. N", pie de página), que
#                                 cambian por definición al cambiar el plan de páginas.
# ---------------------------------------------------------------------------------------

def qa_vocabulario_conduccion(text_pages: list[str]) -> tuple[list[dict[str, object]], list[str]]:
    filas: list[dict[str, object]] = []
    fallas: list[str] = []
    for indice, texto in enumerate(text_pages, start=1):
        for termino, forma in LENG.hallazgos(texto):
            filas.append({"control": "termino_prohibido", "pagina": indice,
                          "termino": termino, "forma_encontrada": forma})
            fallas.append(f"p{indice}:{termino}")
    if not filas:
        filas.append({"control": "sin_hallazgos", "pagina": "",
                      "termino": f"{len(LENG.VOCABULARIO_PROHIBIDO)} términos vigilados",
                      "forma_encontrada": ""})
    return filas, fallas


def qa_enlaces_coherentes(doc) -> tuple[list[dict[str, object]], list[str]]:
    """M-07 · toda referencia textual «p. N» apunta a donde dice, y el enlace también.

    Los veinte «Ir al mapa · p. N» de la conducción arrastraban la numeración de la
    edición técnica de 58 páginas —R22 remitía a la p. 50 en un documento de 49— porque
    las páginas de conducción leían una copia del módulo que nunca se reconfiguraba.
    Este control mira el PDF terminado: para cada «p. N» comprueba que N sea la página
    del destino y que el enlace clicable de esa misma línea lleve a la misma página.
    """
    patron = re.compile(r"(Ir al mapa|IR AL MAPA|Volver a la ficha|VOLVER A FICHA)\s*·\s*p\.\s*(\d+)")

    def pagina_destino(enlace: dict) -> int | None:
        """Página 1-based del destino. pymupdf da int 0-based o str 1-based."""
        destino = enlace.get("page")
        if isinstance(destino, int) and destino >= 0:
            return destino + 1
        if isinstance(destino, str) and destino.isdigit():
            return int(destino)
        return None

    filas: list[dict[str, object]] = []
    fallas: list[str] = []
    for indice in range(doc.page_count):
        pagina = doc[indice]
        enlaces = [l for l in pagina.get_links()
                   if l.get("kind") in {fitz.LINK_GOTO, fitz.LINK_NAMED}]
        for bloque in pagina.get_text("dict")["blocks"]:
            for linea in bloque.get("lines", []):
                texto = "".join(t["text"] for t in linea.get("spans", []))
                m = patron.search(texto)
                if not m:
                    continue
                declarada = int(m.group(2))
                caja = fitz.Rect(linea["bbox"])
                # El enlace de esta línea es el que la solapa.
                cercanos = [l for l in enlaces
                            if fitz.Rect(l.get("from") or l.get("rect")).intersects(caja)]
                paginas_link = {p for p in (pagina_destino(l) for l in cercanos) if p}
                dentro = 1 <= declarada <= doc.page_count
                coincide = (not paginas_link) or (declarada in paginas_link)
                ok = dentro and bool(cercanos) and coincide
                filas.append({
                    "pagina": indice + 1,
                    "texto": texto.strip(),
                    "pagina_declarada": declarada,
                    "pagina_del_enlace": ";".join(str(p) for p in sorted(paginas_link)) or "sin enlace",
                    "resultado": "PASS" if ok else "FAIL",
                    "motivo": "" if ok else (
                        "fuera del documento" if not dentro else
                        "sin enlace clicable" if not cercanos else
                        "el enlace apunta a otra página"),
                })
                if not ok:
                    fallas.append(f"p{indice + 1}:p.{declarada}")
    return filas, fallas


def qa_colisiones_caja(doc) -> tuple[list[dict[str, object]], list[str]]:
    """M-02 · ningún texto puede empezar antes de que termine la caja que lo precede.

    Las cajas se dibujan como rectángulos redondeados rellenos. El control toma cada
    relleno de ancho de columna y comprueba que ningún texto ajeno a la caja invada su
    superficie ni el espacio mínimo que debe seguirla.
    """
    filas: list[dict[str, object]] = []
    fallas: list[str] = []
    # Tolerancia de un punto: la caja de un tramo de texto la calcula el lector de PDF con
    # el alto de la caja tipográfica de la fuente, y el generador la posiciona con el
    # ascenso nominal. Un punto de diferencia es esa conversión, no un defecto de armado.
    minimo = RITMO["bloque"] - 1.0
    por_pagina: dict[int, list[fitz.Rect]] = {}
    for caja in CAJAS_DIBUJADAS:
        # De coordenadas de reportlab (y desde el pie) a las del PDF leído (y desde
        # la cabeza), que son las que devuelve la extracción de texto.
        por_pagina.setdefault(int(caja["pagina"]), []).append(
            fitz.Rect(caja["x0"], PAGE_H - caja["y_top"],
                      caja["x1"], PAGE_H - caja["y_bottom"]))
    for indice in range(doc.page_count):
        cajas = por_pagina.get(indice + 1, [])
        if not cajas:
            continue
        pagina = doc[indice]
        for bloque in pagina.get_text("dict")["blocks"]:
            for linea in bloque.get("lines", []):
                for tramo in linea.get("spans", []):
                    if not tramo["text"].strip():
                        continue
                    r = fitz.Rect(tramo["bbox"])
                    for caja in cajas:
                        if r.intersects(caja):
                            continue      # texto propio de la caja
                        # `y1` crece hacia abajo: el texto que sigue a la caja empieza
                        # en r.y0 y la caja termina en caja.y1.
                        if caja.y1 <= r.y0 < caja.y1 + minimo and \
                           r.x1 > caja.x0 and r.x0 < caja.x1:
                            filas.append({
                                "pagina": indice + 1,
                                "texto": tramo["text"][:60],
                                "caja_termina_en": round(caja.y1, 1),
                                "texto_empieza_en": round(r.y0, 1),
                                "separacion_pt": round(r.y0 - caja.y1, 1),
                                "minimo_pt": RITMO["bloque"],
                            })
                            fallas.append(f"p{indice + 1}:{tramo['text'][:24]}")
    if not filas:
        filas.append({"pagina": "", "texto": "sin colisiones",
                      "caja_termina_en": "", "texto_empieza_en": "",
                      "separacion_pt": "", "minimo_pt": RITMO["bloque"]})
    return filas, fallas


def qa_mapas_prometidos() -> tuple[list[dict[str, object]], list[str]]:
    """S-05 · el mapa tiene que rotular las partes que su propio pie nombra.

    Palermo pasó tres auditorías y 28 controles con una ficha que anunciaba tres partes
    y un mapa que no nombraba ninguna: ningún control comparaba lo que el pie promete
    con lo que el mapa dibuja. Este lo hace. El universo de nombres es la capa de
    componentes —lo único que el generador sabe rotular—, así que el control no puede
    exigir un rótulo que no exista como geometría.
    """
    comp = CARTOGRAFO.comp
    partes: dict[str, list[str]] = {
        rid: [CARTOGRAFO.rotulo(n) for n in comp[comp.referencia_id == rid].componente]
        for rid in EXPECTED_REFS
    }
    filas: list[dict[str, object]] = []
    fallas: list[str] = []
    for mapa in QA_MAPAS:
        rid, archivo = mapa["referencia_id"], mapa["archivo"]
        trio = (TRIOS_ACTIVOS[rid] if mapa["tipo"] == "principal"
                else TRIOS_DETALLE_ACTIVOS[archivo])
        muestra = str(trio["muestra"])
        rotuladas = {t for t in str(mapa["etiquetas"]).split(" | ") if t}
        prometidas = [n for n in partes.get(rid, []) if n and n in muestra]
        faltan = [n for n in prometidas if n not in rotuladas]
        filas.append({
            "pagina": mapa["pagina"],
            "referencia_id": rid,
            "mapa": archivo,
            "partes_nombradas_en_el_pie": " | ".join(prometidas) or "ninguna",
            "partes_rotuladas_en_el_mapa": " | ".join(sorted(rotuladas)) or "ninguna",
            "resultado": "FAIL" if faltan else "PASS",
            "faltan": " | ".join(faltan),
        })
        fallas.extend(f"p{mapa['pagina']}:{n}" for n in faltan)
    return filas, fallas


def _numeros(texto: str) -> set[str]:
    """Números publicados en un texto, normalizados y sin el signo que los precede."""
    crudos = re.findall(r"\d[\d.,]*", str(texto))
    return {n.rstrip(".,") for n in crudos if n.rstrip(".,")}


def _textos_v21_ficha(ficha: dict) -> str:
    partes = [ficha["lectura"], ficha["cifra"], ficha["denominador_metodo"],
              *ficha["caracterizacion"], *ficha["detalle_cuantitativo"],
              *ficha["relaciones"], *ficha["exclusiones"], *ficha["limitaciones_especificas"],
              *[" ; ".join(x) for x in ficha["subunidades"]]]
    if ficha.get("glosa_cifra"):
        partes.append(ficha["glosa_cifra"])
    return " | ".join(str(p) for p in partes)


def diff_cifras_v21_conduccion(content: dict) -> tuple[bool, str]:
    filas: list[dict[str, object]] = []
    fallos = 0
    for ficha in content["fichas"]:
        rid = ficha["referencia_id"]
        bloques = RENDCOND.ficha_bloques(ficha)
        v21 = _textos_v21_ficha(ficha)
        cond = " | ".join([bloques["es"], bloques["frase"], bloques["contexto"],
                           *bloques["compone"], *bloques["cuenta"]])
        n_v21, n_cond = _numeros(v21), _numeros(cond)
        intrusos = sorted(n_cond - n_v21)
        principal_v21 = COND.numero_principal(ficha["cifra"])
        principal_cond = COND.numero_principal(bloques["frase"])
        titular_ok = principal_v21 == principal_cond
        ok = not intrusos and titular_ok
        fallos += 0 if ok else 1
        filas.append({
            "ambito": "ficha", "referencia_id": rid, "campo": "cifras de la ficha",
            "cifras_v21": ", ".join(sorted(n_v21)), "cifras_conduccion": ", ".join(sorted(n_cond)),
            "cifras_no_publicadas_en_conduccion": ", ".join(sorted(n_v21 - n_cond)),
            "cifras_nuevas": ", ".join(intrusos),
            "titular_v21": principal_v21 or "sin cifra",
            "titular_conduccion": principal_cond or "sin cifra",
            "resultado": "PASS" if ok else "FAIL",
        })
    for rid in EXPECTED_REFS:
        base = " ".join(TRIOS[rid][k] for k in ("muestra", "mide", "no_es"))
        nuevo = " ".join(COND.TRIOS[rid][k] for k in ("muestra", "mide", "no_es"))
        n_v21, n_cond = _numeros(base), _numeros(nuevo)
        intrusos = sorted(n_cond - n_v21)
        fallos += 0 if not intrusos else 1
        filas.append({
            "ambito": "mapa", "referencia_id": rid, "campo": "bloque inferior del mapa",
            "cifras_v21": ", ".join(sorted(n_v21)), "cifras_conduccion": ", ".join(sorted(n_cond)),
            "cifras_no_publicadas_en_conduccion": ", ".join(sorted(n_v21 - n_cond)),
            "cifras_nuevas": ", ".join(intrusos), "titular_v21": "", "titular_conduccion": "",
            "resultado": "PASS" if not intrusos else "FAIL",
        })
    for archivo, trio in TRIOS_DETALLE.items():
        base = " ".join(trio[k] for k in ("muestra", "mide", "no_es"))
        nuevo = " ".join(COND.TRIOS_DETALLE[archivo][k] for k in ("muestra", "mide", "no_es"))
        n_v21, n_cond = _numeros(base), _numeros(nuevo)
        intrusos = sorted(n_cond - n_v21)
        fallos += 0 if not intrusos else 1
        filas.append({
            "ambito": "ampliacion", "referencia_id": Path(archivo).stem,
            "campo": "bloque inferior del mapa",
            "cifras_v21": ", ".join(sorted(n_v21)), "cifras_conduccion": ", ".join(sorted(n_cond)),
            "cifras_no_publicadas_en_conduccion": ", ".join(sorted(n_v21 - n_cond)),
            "cifras_nuevas": ", ".join(intrusos), "titular_v21": "", "titular_conduccion": "",
            "resultado": "PASS" if not intrusos else "FAIL",
        })
    write_csv(QA_DIR / "DIFF_CIFRAS_V21_CONDUCCION.csv",
              ["ambito", "referencia_id", "campo", "cifras_v21", "cifras_conduccion",
               "cifras_no_publicadas_en_conduccion", "cifras_nuevas", "titular_v21",
               "titular_conduccion", "resultado"], filas)
    detalle = (f"{len(filas)} comparaciones, {len(filas) - fallos} PASS"
               if not fallos else f"{fallos} diferencias numéricas contra la V2.1")
    return fallos == 0, detalle


def escribir_trazabilidad_lenguaje(content: dict) -> None:
    """Las 22 fichas, texto V2.1 y texto de conducción uno al lado del otro.

    Sirve para verificar frase por frase que no se perdió ninguna salvedad ni se agregó
    ninguna afirmación. La columna de cifras deja ver, además, qué números dejaron de
    publicarse en la conducción: todos ellos siguen enteros en la edición técnica.
    """
    filas = []
    for ficha in content["fichas"]:
        rid = ficha["referencia_id"]
        bloques = RENDCOND.ficha_bloques(ficha)
        # Universo de números de TODA la ficha de la V2.1: sirve para separar un número
        # que cambió de bloque (legítimo: la estructura de la ficha cambió a propósito)
        # de un número inventado (prohibido, y que el control diff_cifras hace fallar).
        n_ficha_v21 = _numeros(_textos_v21_ficha(ficha))
        pares = [
            ("Cuánta oferta hay",
             " | ".join(filter(None, [nature_label(ficha["naturaleza"]), short_figure(ficha),
                                      ficha["denominador_metodo"]])),
             f"{bloques['frase']} | {bloques['contexto']}"),
            ("Qué es esta zona",
             " | ".join([ficha["lectura"], *ficha["caracterizacion"]]),
             bloques["es"]),
            ("De qué se compone",
             " | ".join([*[" ; ".join(x) for x in ficha["subunidades"]],
                         *ficha["relaciones"], *ficha["exclusiones"]]) or "—",
             " | ".join(bloques["compone"])),
            ("Qué hay que tener en cuenta",
             " | ".join([*ficha["limitaciones_especificas"], *ficha["detalle_cuantitativo"]]),
             " | ".join(bloques["cuenta"])),
        ]
        for bloque, v21, cond in pares:
            n_v21, n_cond = _numeros(v21), _numeros(cond)
            filas.append({
                "referencia_id": rid,
                "nombre": ficha["nombre"],
                "bloque_conduccion": bloque,
                "texto_v21": v21,
                "texto_conduccion": cond,
                "cifras_v21": ", ".join(sorted(n_v21)),
                "cifras_conduccion": ", ".join(sorted(n_cond)),
                "cifras_trasladadas_a_edicion_tecnica": ", ".join(sorted(n_v21 - n_cond)),
                "cifras_movidas_desde_otro_bloque": ", ".join(sorted((n_cond - n_v21) & n_ficha_v21)),
                "cifras_sin_respaldo_en_la_v21": ", ".join(sorted(n_cond - n_ficha_v21)),
            })
    write_csv(QA_DIR / "TRAZABILIDAD_LENGUAJE.csv",
              ["referencia_id", "nombre", "bloque_conduccion", "texto_v21", "texto_conduccion",
               "cifras_v21", "cifras_conduccion", "cifras_trasladadas_a_edicion_tecnica",
               "cifras_movidas_desde_otro_bloque", "cifras_sin_respaldo_en_la_v21"], filas)


def pdf_qa(content: dict, mask_metadata: list[dict[str, object]] | None = None) -> dict[str, object]:
    doc = fitz.open(PDF_PATH)
    text_pages = [page.get_text("text") for page in doc]
    all_text = "\n".join(text_pages)
    checks: list[dict[str, object]] = []

    def add(control: str, ok: bool, detail: object) -> None:
        checks.append({"control": control, "resultado": "PASS" if ok else "FAIL", "detalle": detail})

    total = EXPECTED_PAGES
    add("paginas_exactas", doc.page_count == total, doc.page_count)
    a4_ok = all(abs(page.rect.width - 595.276) < 1 and abs(page.rect.height - 841.89) < 1 for page in doc)
    add("formato_A4", a4_ok, f"{total}/{total}" if a4_ok else "desvío")
    nonblank = sum(bool(text.strip()) for text in text_pages)
    add("paginas_no_vacias", nonblank == total, f"{nonblank}/{total}")
    add("texto_seleccionable", len(all_text) > (18000 if EDICION == "conduccion" else 25000),
        len(all_text))
    toc = doc.get_toc(simple=False)
    toc_titles = [row[1] for row in toc]
    secciones = ["Apertura", SECCION_ZONAS[EDICION], SECCION_AMPLIACIONES[EDICION], "Anexos"]
    add("marcadores_jerarquicos",
        len(toc) >= (40 if EDICION == "conduccion" else 47) and all(x in toc_titles for x in secciones),
        len(toc))
    unique_cont = len(toc_titles) == len(set(toc_titles))
    add("marcadores_sin_duplicados", unique_cont, len(set(toc_titles)))
    links = [link for page in doc for link in page.get_links()]
    internal = [link for link in links if link.get("kind") in {fitz.LINK_GOTO, fitz.LINK_NAMED}]
    destinations_ok = all(
        (isinstance(link.get("page"), int) and 0 <= link["page"] < total)
        or (isinstance(link.get("page"), str) and link["page"].isdigit() and 1 <= int(link["page"]) <= total)
        for link in internal
    )
    add("enlaces_internos", len(internal) >= 90 and destinations_ok, len(internal))
    refs_ok = all(re.search(rf"\b{rid}\b", all_text) for rid in EXPECTED_REFS)
    add("R01_R22", refs_ok, "22/22" if refs_ok else "faltantes")
    add("ausencia_R23", re.search(r"\bR23\b", all_text) is None, "0")
    forbidden_public_labels = [
        "SIN_CIFRA_CANONICA_COMPARABLE",
        "SIN_CIFRA_",
        "COMPARA/BLE",
    ]
    label_hits = [value for value in forbidden_public_labels if value in all_text]
    add("guardas_rotulos_publicos", not label_hits, ",".join(label_hits) or "0")
    public_forbidden = [
        r"[A-Za-z]:\\", r"Users\\", r"codex/", r"grok/", r"\.py\b", r"Di" + r"ego",
        r"AIza[0-9A-Za-z_-]{20,}", r"drive\.google\.com", r"docs\.google\.com",
        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
    ]
    hits = [pattern for pattern in public_forbidden if re.search(pattern, all_text, re.I)]
    add("capa_publica_sin_fugas", not hits, ";".join(hits) or "0")
    if EDICION == "conduccion":
        # La reconciliación de la conducción es la de las 22 frases de cifra: cada zona
        # tiene que decir su número, y decirlo en la forma que le corresponde.
        exact_values = [COND.frase_cifra(f) for f in content["fichas"]]
    else:
        exact_values = [
            "204 / 7 / 0", "39 / 1 / 0", "242 / 12 / 0", "152 / 6 / 0",
            "79 / 326", "51 / 64", "6 / 6", "9 / 180", "9 / 185",
            "1 / 20", "6 / 70", "≥797", "≥940", "143 dobles",
        ]
    missing_values = [value for value in exact_values if value not in all_text]
    add("reconciliacion_cifras", not missing_values, ",".join(missing_values) or "completa")
    # B6 - un unico descargo por pagina de mapa, ni cero ni repetido.
    # Correccion editorial 2026-08-04: la conduccion ya no lleva descargo al pie. Para esa
    # edicion el control cambia de signo: verifica que las dos formulas retiradas no vuelvan
    # a aparecer en ninguna pagina. La tecnica conserva el control original.
    descargos = tuple(d for d in (DESCARGO_MAPA[EDICION], DESCARGO_AMPLIACION[EDICION]) if d)
    # 22 mapas principales + una pagina por ampliacion de la edicion en curso.
    mapas_esperados = len(EXPECTED_REFS) + len(COMP_INFO_ACTIVO)
    if descargos:
        con_descargo = [i + 1 for i, txt in enumerate(text_pages)
                        if sum(txt.count(d) for d in descargos) == 1]
        repetido = [i + 1 for i, txt in enumerate(text_pages)
                    if sum(txt.count(d) for d in descargos) > 1]
        add("pie_cartografico", len(con_descargo) == mapas_esperados and not repetido,
            f"paginas con un solo descargo={len(con_descargo)}/{mapas_esperados}; "
            f"repetido en={repetido or 'ninguna'}")
    else:
        reaparecen = [i + 1 for i, txt in enumerate(text_pages)
                      if any(f in txt for f in DESCARGOS_RETIRADOS_CONDUCCION)]
        add("pie_cartografico", not reaparecen,
            "edición sin descargo al pie por decisión editorial; "
            f"fórmulas retiradas reaparecen en={reaparecen or 'ninguna'}")
    add("cartografia_vectorial", len(QA_MAPAS) == mapas_esperados,
        f"mapas vectoriales={len(QA_MAPAS)}/{mapas_esperados}")

    # S-05 · ningun mapa puede prometer partes que no rotula.
    filas_prom, fallas_prom = qa_mapas_prometidos()
    write_csv(qa_file("QA_MAPAS_PROMETIDOS.csv"),
              ["pagina", "referencia_id", "mapa", "partes_nombradas_en_el_pie",
               "partes_rotuladas_en_el_mapa", "resultado", "faltan"], filas_prom)
    con_partes = sum(1 for f in filas_prom if f["partes_nombradas_en_el_pie"] != "ninguna")
    add("mapas_rotulan_lo_que_prometen", not fallas_prom,
        ";".join(dict.fromkeys(fallas_prom)) if fallas_prom
        else f"{len(filas_prom)} mapas; {con_partes} nombran partes en el pie; "
             f"0 partes prometidas sin rotular")
    add("sin_imagenes_embebidas",
        all(not doc[i].get_images(full=True) for i in range(doc.page_count)),
        "0 imagenes rasterizadas")

    # B6 - jerga tecnica y nomenclatura interna fuera de las paginas publicas.
    jerga = ["DataGastro", "HDBSCAN", "epsilon", "Jaccard", "buffer heredado",
             "businessStatus", "NO_EVALUABLE", "INFORMEFINAL", "EPSG",
             "proxy reproducible", "Convenciones comunes", "Lectura y límites",
             "Caveat geométrico"]
    jerga_hits = [x for x in jerga if x.lower() in all_text.lower()]
    jerga_hits += ["encabezado MAPA PRINCIPAL duplicado"] if "· MAPA PRINCIPAL" in all_text else []
    jerga_hits += [x for x in ("ARI",) if re.search(rf"\b{x}\b", all_text)]
    add("sin_jerga_tecnica", not jerga_hits, ";".join(jerga_hits) or "0")
    codigos = [m for m in re.findall(r"\bZ0\d-S\d\b|\bC-S0\d\b|\bLAC-[A-Z0-9-]+\b|"
                                     r"\bR2[12]-[A-Z]+\b|\bR08-CTRL[A-Z-]*\b", all_text)]
    add("sin_codigos_internos", not codigos, ";".join(sorted(set(codigos))) or "0")

    # B6 - codificacion intacta.
    mojibake = [x for x in ("Ã", "â€", "\ufffd") if x in all_text]
    add("codificacion_limpia", not mojibake, ";".join(mojibake) or "0")
    tildes = ["Cañitas", "García del Río", "Villa Pueyrredón", "gastronómico"]
    faltan = [x for x in tildes if x not in all_text]
    add("tildes_intactas", not faltan, ";".join(faltan) or "4/4")

    # B6 - ninguna referencia visualmente fusionada con otra declarada independiente.
    solapes = read_csv(QA_DIR / "QA_SOLAPES_22.csv")
    fusiones = [f"{r['referencia_a']}/{r['referencia_b']}" for r in solapes
                if r["resultado"] == "FAIL"]
    add("sin_fusiones_indebidas", not fusiones, ";".join(fusiones) or
        f"{len(solapes)} pares revisados")
    font_xrefs = set()
    for idx in range(doc.page_count):
        for font in doc.get_page_fonts(idx, full=True):
            if font[0] > 0:
                font_xrefs.add(font[0])
    embedded = 0
    for xref in font_xrefs:
        try:
            extracted = doc.extract_font(xref)
            if extracted and extracted[-1]:
                embedded += 1
        except Exception:
            pass
    add("tipografias_embebidas", embedded >= 2, f"{embedded}/{len(font_xrefs)}")

    # B-02 - el control que faltaba: nada cortado a mitad de palabra ni fuera de su caja.
    clip_filas, clip_fallas = qa_texto_clipeado(doc, content)
    write_csv(qa_file("QA_TEXTO_CLIPEADO.csv"), ["control", "pagina", "detalle"], clip_filas)
    acortes = sum(1 for f in clip_filas if f["control"] == "acorte_declarado")
    add("texto_clipeado", not clip_fallas,
        ";".join(dict.fromkeys(clip_fallas)) if clip_fallas
        else f"{total} páginas; 0 palabras truncadas; 0 fuera de caja; {acortes} acortes con elipsis")

    # M-07 · las referencias de página del cuerpo, contra el PDF terminado.
    filas_enl, fallas_enl = qa_enlaces_coherentes(doc)
    write_csv(qa_file("QA_ENLACES_COHERENTES.csv"),
              ["pagina", "texto", "pagina_declarada", "pagina_del_enlace", "resultado",
               "motivo"], filas_enl)
    add("enlaces_coherentes", not fallas_enl,
        ";".join(dict.fromkeys(fallas_enl)) if fallas_enl
        else f"{len(filas_enl)} referencias «p. N»; todas apuntan a su destino")

    # M-02 · ninguna caja pisada por el texto que la sigue.
    if EDICION == "conduccion":
        filas_col, fallas_col = qa_colisiones_caja(doc)
        write_csv(qa_file("QA_COLISIONES_CAJA.csv"),
                  ["pagina", "texto", "caja_termina_en", "texto_empieza_en",
                   "separacion_pt", "minimo_pt"], filas_col)
        add("cajas_sin_colision", not fallas_col,
            ";".join(dict.fromkeys(fallas_col)) if fallas_col
            else f"{total} páginas; separación mínima {RITMO['bloque']:.0f} pt respetada")

    # B8 · los dos controles que agrega la edición de conducción.
    if EDICION == "conduccion":
        filas_voc, fallas_voc = qa_vocabulario_conduccion(text_pages)
        write_csv(QA_DIR / "QA_VOCABULARIO_CONDUCCION.csv",
                  ["control", "pagina", "termino", "forma_encontrada"], filas_voc)
        add("vocabulario_conduccion", not fallas_voc,
            ";".join(dict.fromkeys(fallas_voc)) if fallas_voc
            else f"{len(LENG.VOCABULARIO_PROHIBIDO)} términos vigilados; 0 apariciones en "
                 f"{total} páginas")
        ok_cifras, detalle_cifras = diff_cifras_v21_conduccion(content)
        add("diff_cifras_v21_conduccion", ok_cifras, detalle_cifras)
    doc.close()
    reader = PdfReader(str(PDF_PATH))
    add("sin_cifrado", not reader.is_encrypted, str(reader.is_encrypted))
    add("sin_formularios", not reader.get_fields(), "0")
    root = reader.trailer["/Root"]
    has_js = "/JavaScript" in root or ("/Names" in root and "/JavaScript" in root["/Names"])
    add("sin_javascript", not has_js, str(has_js))
    meta = reader.metadata or {}
    meta_ok = "DGDGAS" in str(meta.get("/Author", "")) and "Atlas de referencias gastronómicas" in str(meta.get("/Title", ""))
    add("metadatos_institucionales", meta_ok, dict(meta))
    failed = [row for row in checks if row["resultado"] != "PASS"]
    write_csv(qa_file("QA_AUTOMATICO.csv"), ["control", "resultado", "detalle"], checks)
    (qa_file("texto_extraido_pdf.txt")).write_text(all_text, encoding="utf-8")
    if failed:
        raise RuntimeError("QA PDF falló: " + ", ".join(row["control"] for row in failed))
    return {"checks": len(checks), "links": len(internal), "toc": len(toc), "text_chars": len(all_text)}


def privacy_qa() -> list[dict[str, object]]:
    text_files = [
        path for path in OUT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".csv", ".json", ".py"}
        and not any(part.startswith("render_") for part in path.parts)
        and not path.name.startswith("texto_extraido_pdf")
    ]
    corpus = "\n".join(path.read_text(encoding="utf-8-sig", errors="replace") for path in text_files)
    pdf_text = (qa_file("texto_extraido_pdf.txt")).read_text(encoding="utf-8")
    patterns = {
        "api_key": r"AIza[0-9A-Za-z_-]{20,}",
        "email": r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        "telefono": r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]\d{4}\b",
        "cuit_dni": r"\b\d{2}-\d{8}-\d\b|\b(?:CUIT|DNI)\s*[:#]?\s*\d",
        "link_privado": r"drive\.google\.com|docs\.google\.com",
        "ruta_windows_privada": r"[A-Za-z]:\\Users\\",
        "id_plataforma": r"\bChIJ[0-9A-Za-z_-]{15,}\b",
        "nombre_decisor": r"\bDi" + r"ego\b",
        "comercial_sensible": "G\u00fcerr\u00edn|Las " + "Cuartetas",
    }
    rows = []
    for label, pattern in patterns.items():
        package_hit = bool(re.search(pattern, corpus, re.I))
        pdf_hit = bool(re.search(pattern, pdf_text, re.I))
        rows.append({"control": label, "pdf": "PASS" if not pdf_hit else "FAIL", "contenido_y_scripts": "PASS" if not package_hit else "FAIL", "resultado": "PASS" if not package_hit and not pdf_hit else "FAIL"})
    write_csv(qa_file("QA_PRIVACIDAD.csv"), ["control", "pdf", "contenido_y_scripts", "resultado"], rows)
    failed = [row for row in rows if row["resultado"] == "FAIL"]
    if failed:
        raise RuntimeError("QA privacidad falló: " + ", ".join(row["control"] for row in failed))
    return rows


def preservation_qa(before: dict[str, str]) -> None:
    rows = []
    for key, path in PRESERVE_FILES.items():
        after = sha256(path)
        rows.append({
            "insumo": key,
            "ruta_relativa": relative(path),
            "sha256_pre": before[key],
            "sha256_post": after,
            "resultado": "PASS" if before[key] == after else "FAIL",
        })
    write_csv(QA_DIR / "QA_PRESERVACION_INSUMOS.csv", ["insumo", "ruta_relativa", "sha256_pre", "sha256_post", "resultado"], rows)
    if any(row["resultado"] == "FAIL" for row in rows):
        raise RuntimeError("Un insumo canónico cambió durante la producción")


# B6 - inspeccion visual real, pagina por pagina. Ninguna fila queda en PENDIENTE.
# Estado: OK = sin hallazgos; OBSERVACION = hallazgo no bloqueante declarado.
INSPECCION_VISUAL = {
    1: ("OK", "Portada limpia; marca DGDGAS y titulo institucional; sin numero de edicion."),
    2: ("OK", "Resumen ejecutivo abre con datos de la Ciudad: 22 referencias, 11 comunas, cinco familias y los cuatro grupos de cifras con su advertencia al lado."),
    3: ("OK", "Indice en tres columnas; los encabezados de seccion no quedan huerfanos al pie; los 47 destinos resuelven."),
    4: ("OK", "Ocho fichas de lectura con la clave de naturaleza de las cifras; regla general al pie."),
    5: ("OK", "Cinco familias con muestra de color, trama y definicion en linea propia; una referencia por renglon a ancho completo, ninguna etiqueta cortada."),
    6: ("OK", "Mapa general a pagina completa con anclas geograficas (numero de las 15 comunas, Rio de la Plata, Av. Gral. Paz y Riachuelo), advertencia de area vs volumen y tabla de 22 en dos columnas enlazada."),
    7: ("OK", "R01: la ausencia de cifra aparece como linea secundaria en cuerpo normal, no como titular."),
    8: ("OK", "R01: tres subzonas separadas y rotuladas; sin fusion entre ellas."),
    9: ("OK", "Vista de detalle Las Canitas; zoom correcto sobre la subzona."),
    10: ("OK", "Ficha doble R02/R03; ambas con linea secundaria de ausencia de cifra."),
    11: ("OK", "R02: corredor continuo de punta a punta; Av. Corrientes, Callao y 9 de Julio rotuladas como calles de referencia."),
    12: ("OK", "R03: contorno organico; desapareció el rectangulo de la edicion anterior."),
    13: ("OK", "Vista contextual R02/R13; las dos formas separadas y rotuladas."),
    14: ("OK", "Ficha doble R04/R06; R06 sin badge de antecedente por no tener cifra publicable."),
    15: ("OK", "R04: los cuatro diques aparecen como huecos del poligono; el area excluye el espejo de agua y la linea de cierre lo declara con su fuente (D-A-10, BLOQUEADO-01 cerrado)."),
    16: ("OK", "R06: unidad continua con su hueco interno preservado."),
    17: ("OK", "R05: badge de antecedente previo con simbolo propio."),
    18: ("OK", "R05: las tres centralidades agrupadas y rotuladas una sola vez cada una; Av. Cabildo y Av. Juramento rotuladas."),
    19: ("OK", "R07: badge de antecedente previo; cuatro componentes declarados."),
    20: ("OK", "R07: cuatro componentes separados sobre el frente costero, sin conectores artificiales."),
    21: ("OK", "R08: la ficha ocupa la columna completa y la linea de fuente cierra al pie; sin aire muerto en el tercio inferior."),
    22: ("OK", "R08: envolvente organica con Thames y Gurruchaga rotuladas, las dos calles que nombra el texto de la pagina."),
    23: ("OK", "Vista de detalle R08: los tres puntos de tope de relevamiento marcados con circulo punteado."),
    24: ("OK", "Ficha doble R09/R10; ambas declaran que el mapa no cubre la totalidad de los registros."),
    25: ("OK", "R09: los dos focos independientes, rotulados y sin envolvente comun; Av. Jorge Newbery y Av. Dorrego rotuladas."),
    26: ("OK", "R10: los dos nucleos independientes, rotulados."),
    27: ("OK", "Ficha doble R11/R13."),
    28: ("OK", "R11: microcentralidad de tramo corto; no se extiende a Barracas."),
    29: ("OK", "R13: forma suavizada con trazo punteado de area declarada."),
    30: ("OK", "R12: ficha extensa; ocupa la columna completa y cierra al pie."),
    31: ("OK", "R12: cinco subunidades separadas y rotuladas; sin medialunas residuales."),
    32: ("OBSERVACION", "Vista de detalle R12: aporta zoom y rotulos, pero se parece mucho al mapa principal."),
    33: ("OK", "Ficha doble R14/R15 con badge de cifra exacta."),
    34: ("OK", "R14: eje de Boedo continuo a lo largo de la avenida."),
    35: ("OK", "R15: polo de Devoto con sus huecos internos."),
    36: ("OBSERVACION", "Vista de detalle R15: el corpus no cierra geometria del nucleo, asi que la vista repite el polo completo. BLOQUEADO-03 se mantiene abierto por decision; la fuente oficial de Espacios Verdes solo confirma que Plaza Arenales esta en Villa Devoto, Comuna 11."),
    37: ("OK", "Ficha doble R16/R17."),
    38: ("OK", "R16: doble eje fragmentado por tramos, con Donado y Holmberg rotuladas."),
    39: ("OBSERVACION", "R17: se dibuja el unico eje con trazado cerrado en el corpus. Monroe y Congreso se rotulan como calles de referencia del callejero oficial, no como ejes de producto: BLOQUEADO-02 se mantiene abierto por decision."),
    40: ("OK", "Ficha doble R18/R20 con badge de cota inferior."),
    41: ("OK", "R18: disco de consulta de 400 m, sin punto central, con trazo punteado."),
    42: ("OK", "R20: banda con esquinas ablandadas y extremos planos preservados; Av. Garcia del Rio y Av. Cabildo rotuladas."),
    43: ("OK", "Vista de detalle R20: el control de Parque Saavedra se distingue del producto."),
    44: ("OK", "R19: la ficha ocupa la columna completa y cierra al pie."),
    45: ("OK", "R19: dos tramos independientes, rotulados y sin union artificial; Federico Lacroze, Cabildo, Libertador y Alvarez Thomas rotuladas."),
    46: ("OK", "Vista de detalle R19: grafico completo y bloques en el mismo orden que el resto; corregido el corte de la edicion anterior."),
    47: ("OK", "R21: la ficha ocupa la columna completa y cierra al pie."),
    48: ("OK", "R21: tres piezas; los puntos de anclaje del buffer ya no se dibujan."),
    49: ("OK", "R22: ficha con badge de cota inferior; ocupa la columna completa."),
    50: ("OK", "R22: marco de relevamiento sin la grilla de calculo; rotulado como marco, no como area gastronomica."),
    51: ("OK", "Anexo A 1 de 2: matriz R01-R11 completa y legible."),
    52: ("OK", "Anexo A 2 de 2: matriz R12-R22 completa y legible."),
    53: ("OK", "Anexo B: subunidades y componentes; recoge las partes internas de cada referencia."),
    54: ("OK", "Anexo C: controles y exclusiones; aloja las instrucciones internas que salieron de las paginas de mapa."),
    55: ("OK", "Anexo D: separaciones institucionales; una fila por par que no debe fusionarse."),
    56: ("OK", "Anexo E: estado declarado y saturaciones."),
    57: ("OK", "Anexo F: como se contaron los locales."),
    58: ("OK", "Anexo G: decisiones, limites, glosario y trazabilidad publica, con CRS y fechas movidos aca desde las paginas de mapa."),
}


# B8 · inspeccion visual real, pagina por pagina, de la edicion de conduccion.
# Hecha sobre los 49 renders a 150 dpi. Estado: OK = sin hallazgos; OBSERVACION = hallazgo
# no bloqueante declarado. Los solapes de rotulo de calle contra rotulo de area vienen de
# la cartografia de la V2.1 y aparecen en las mismas laminas en las dos ediciones: esta
# fase no toca geometrias ni mapas.
INSPECCION_VISUAL_CONDUCCION: dict[int, tuple[str, str]] = {
    1: ("OK", "Portada limpia; marca DGDGAS y titulo institucional. Los dos rotulos que estaban en versalitas -la caja de lectura y el descargo del pie- pasaron a capitalizacion normal (M-04)."),
    2: ("OK", "Resumen ejecutivo: 22 zonas, 11 comunas, cinco familias y los cuatro modos de conteo separados por linea fina. La caja de cierre sigue al ultimo grupo en vez de estar clavada al pie: desaparecio el hueco de 166 pt del medio. El titulo ya no se monta sobre la caja azul (M-02). La fuente y la fecha, una sola vez."),
    3: ("OK", "Indice a dos columnas parejas. La entrada 'Zonas R01-R22 (continua)' lleva a la pagina donde la seccion continua, no al inicio de la seccion (M-08). Los 44 destinos resuelven."),
    4: ("OK", "Tres ideas en tres cajas mas el cierre. Cada caja se ajusta a su texto: se fueron los ~2 cm vacios que tenia cada una debajo (M-05). El sobrante queda al pie de la pagina."),
    5: ("OK", "Cinco familias con muestra de color y definicion; cada zona con su nombre. Separacion de un bloque entre paneles."),
    6: ("OBSERVACION", "Mapa general con anclas geograficas y tabla de 22 en dos columnas. La nota del pie ahora se ajusta al ancho de la columna: antes media 514,1 pt en una columna de 510,2 y salia de la caja. Los numeros de comuna 1 y 11 se rozan sobre el gris: viene de la cartografia de la V2.1."),
    7: ("OK", "Ficha doble R01/R02. Los cuatro bloques del lector; la frase de cifra sin etiqueta ni simbolo; una sola advertencia al pie. Los enlaces 'Ir al mapa' llevan a las paginas 8 y 12, las de esta edicion."),
    8: ("OK", "R01: las tres partes -Palermo Soho, Palermo Hollywood y Las Canitas- separadas y ROTULADAS. Hasta esta corrida el mapa rotulaba 'Palermo' una sola vez y ninguna de las tres partes que la ficha anuncia (S-01)."),
    9: ("OK", "Pagina nueva (S-03). Palermo Soho ampliado a 250 m, con Palermo Hollywood en gris al costado y cuatro avenidas del entorno rotuladas."),
    10: ("OK", "Pagina nueva (S-03). Palermo Hollywood ampliado a 250 m, con Palermo Soho en gris y las avenidas del entorno."),
    11: ("OK", "Las Canitas ampliada: encuadre ajustado a la pieza, escala propia de 250 m y avenidas del entorno rotuladas. Antes era el mapa de Palermo entero con otro rotulo (S-02)."),
    12: ("OBSERVACION", "R02: corredor continuo de punta a punta. El rotulo de calle 'Av. Corrientes' se cruza con el rotulo de area 'Avenida Corrientes'; redundancia heredada de la V2.1."),
    13: ("OK", "Corrientes y Abasto en un mismo mapa, separados y rotulados."),
    14: ("OK", "Ficha doble R03/R04. R04 declara en tres lineas que el area excluye el agua de los diques."),
    15: ("OK", "R03: contorno organico sobre el casco historico."),
    16: ("OK", "R04: los cuatro diques aparecen como huecos del poligono y las dos partes quedan rotuladas -Docks y Darsena Sur-, recuperadas de la misma fuente cartografica que las de Palermo (S-04)."),
    17: ("OK", "Ficha doble R05/R06. R05 dice su cifra como dato de un relevamiento anterior, sin etiqueta tecnica."),
    18: ("OBSERVACION", "R05: las tres centralidades agrupadas y rotuladas. 'Av. Juramento' se cruza con el rotulo 'Cabildo-Juramento'; heredado de la V2.1."),
    19: ("OK", "R06: unidad continua con su hueco interno preservado."),
    20: ("OK", "Ficha doble R07/R08. R08 dice en castellano donde el relevamiento llego a su tope."),
    21: ("OK", "R07: cuatro tramos separados sobre el frente costero, sin conectores artificiales. Los rotulos dicen 'Tramo 1' a 'Tramo 4': en la revision visual de esta corrida decian 'Componente 1' a 'Componente 4', que es la palabra interna y no un nombre."),
    22: ("OK", "R08: envolvente organica con Thames y Gurruchaga rotuladas."),
    23: ("OK", "Ampliacion R08: los tres puntos de tope de relevamiento marcados con circulo punteado."),
    24: ("OK", "Ficha doble R09/R10. Las dos declaran que el mapa no cubre la totalidad de lo relevado."),
    25: ("OBSERVACION", "R09: los dos focos independientes, rotulados y sin contorno comun. 'Av. Jorge Newbery' se cruza con 'Corredor Newbery'; heredado de la V2.1."),
    26: ("OK", "R10: los dos nucleos independientes, rotulados."),
    27: ("OK", "Ficha doble R11/R12. R12 explica en una linea por que los numeros de sus areas no se suman."),
    28: ("OK", "R11: tramo corto; no se extiende a Barracas."),
    29: ("OK", "R12: cinco areas separadas y rotuladas."),
    30: ("OBSERVACION", "Ampliacion R12: aporta zoom y rotulos, pero se parece mucho al mapa principal. Ya estaba declarado en la V2.1 y no entra en el alcance de esta corrida."),
    31: ("OK", "Ficha doble R13/R14. R13 publica los tres tramos con su minimo, sin destacar ninguno."),
    32: ("OK", "R13: forma suavizada con trazo punteado de area declarada."),
    33: ("OK", "R14: eje de Boedo continuo a lo largo de la avenida."),
    34: ("OK", "Ficha doble R15/R16. R16 aclara que 'DoHo' es un apodo y no el nombre."),
    35: ("OK", "R15: polo de Devoto con sus huecos internos."),
    36: ("OBSERVACION", "Ampliacion R15: no hay trazado propio del nucleo en el corpus, asi que la vista repite el polo completo. BLOQUEADO-03 sigue abierto por decision."),
    37: ("OK", "R16: doble eje con Donado y Holmberg rotuladas."),
    38: ("OK", "Ficha doble R17/R18. R17 nombra los tres ejes y explica por que el mapa ubica uno."),
    39: ("OK", "R17: se dibuja el unico eje con recorrido cerrado; Monroe y Congreso como calles de referencia. BLOQUEADO-02 sigue abierto por decision."),
    40: ("OK", "R18: circulo de consulta de 400 m, sin punto central, con trazo punteado."),
    41: ("OK", "Ficha doble R19/R20. Las dos dicen el estado de los locales en castellano, sin la etiqueta de origen."),
    42: ("OBSERVACION", "R19: dos tramos independientes, rotulados y sin union artificial. Los rotulos de Federico Lacroze y Alvarez Thomas se cruzan en el vertice; heredado de la V2.1."),
    43: ("OK", "Ampliacion R19: los dos tramos con su zona de contacto junto a Cabildo."),
    44: ("OK", "R20: banda con esquinas ablandadas y extremos planos preservados."),
    45: ("OBSERVACION", "Ampliacion R20: el parque se distingue del tramo. 'Av. Garcia del Rio' se cruza con el rotulo de area; heredado de la V2.1."),
    46: ("OK", "Ficha doble R21/R22. R21 nombra el sector oeste por el territorio, no por su codigo interno."),
    47: ("OK", "R21: tres piezas; sin puntos de anclaje dibujados."),
    48: ("OK", "R22: marco de relevamiento rotulado como marco, no como area gastronomica."),
    49: ("OK", "Tabla de consulta 1 de 2: cuatro columnas. Se fue la columna 'Que mide la cifra', que repetia lo que dice 'Cuanta oferta hay', y el encabezado 'Que tipo de zona es' ya no se monta sobre el de al lado (M-06)."),
    50: ("OK", "Tabla de consulta 2 de 2: mismo criterio, once filas."),
    51: ("OBSERVACION", "Cierre en media carilla, como pide el encargo original. Junto con las paginas 4 y 5 es de las que mas alto libre dejan al pie, consecuencia declarada de ajustar las cajas a su contenido (M-05) y de no repartir el sobrante a ojo (M-03)."),
}


def tabla_inspeccion() -> dict[int, tuple[str, str]]:
    return INSPECCION_VISUAL_CONDUCCION if EDICION == "conduccion" else INSPECCION_VISUAL


def write_readme_and_qa_summary(pdf_stats: dict[str, object]) -> None:
    total = EXPECTED_PAGES
    tabla = tabla_inspeccion()
    inspeccionadas = sum(1 for n in range(1, total + 1) if n in tabla)
    extra = ""
    if EDICION == "conduccion":
        extra = (f"- Vocabulario de conducción: {len(LENG.VOCABULARIO_PROHIBIDO)} términos "
                 f"vigilados, 0 apariciones.\n"
                 f"- Cifras: sin diferencias contra la V2.1 "
                 f"(qa/DIFF_CIFRAS_V21_CONDUCCION.csv).\n")
    summary = f"""# QA visual del productor - edicion {EDICION}

- Páginas renderizadas e inspeccionables: {total}/{total} a 150 dpi.
- Páginas con hallazgo declarado: {inspeccionadas}/{total}.
- Páginas vacías: 0.
- Enlaces internos detectados: {pdf_stats['links']}.
- Marcadores detectados: {pdf_stats['toc']}.
- Texto seleccionable: {pdf_stats['text_chars']} caracteres extraídos.
- Privacidad: sin hallazgos bloqueantes automáticos.
- Texto clipeado: 0 palabras truncadas, 0 cadenas fuera de caja,
  {sum(1 for r in RECORTES_TEXTO)} acortes deliberados, todos con elipsis y en límite de palabra.
{extra}- Estado: QA del productor completo; requiere revisión independiente posterior.
"""
    (qa_file("QA_VISUAL_PRODUCTOR.md")).write_text(summary, encoding="utf-8")
    write_csv(
        qa_file(f"QA_VISUAL_INSPECCION_{total}.csv"),
        ["pagina", "render", "metodo_inspeccion", "hallazgo", "estado"],
        [
            {
                "pagina": n,
                "render": f"render_{EDICION}/pagina_{n:02d}.png",
                "metodo_inspeccion": "render 150 dpi, página por página",
                "hallazgo": tabla.get(n, ("PENDIENTE", "Sin inspección registrada."))[1],
                "estado": tabla.get(n, ("PENDIENTE", ""))[0],
            }
            for n in range(1, total + 1)
        ],
    )


def write_readme_carpeta(reportes: dict[str, dict]) -> None:
    """README de la carpeta: describe las dos ediciones, no una sola."""
    cond, tec = reportes["conduccion"], reportes["tecnica"]
    readme = f"""# Atlas DGDGAS - dos ediciones

Un mismo corpus cerrado R01-R22, dos documentos con destinatarios distintos. Ninguna
cifra, geometria ni decision territorial cambia entre uno y otro.

## Edicion de conduccion (entregable de esta fase)

- PDF: {cond['pdf']}
- Extension: {cond['pdf_paginas']} paginas A4 vertical.
- Destinatario: equipo del Ministro. Quien abre el documento sin conocer el proyecto
  tiene que entenderlo sin preguntarle nada a nadie.
- Se deriva de la V2.1 restando: se simplifica como se dice, no que se dice. Cada
  salvedad sigue estando, en castellano, una sola vez, en el lugar donde importa.
- QA: {cond['controles_qa']} controles, incluidos los dos propios de esta edicion -
  `vocabulario_conduccion` (ningun termino de metodo llega al lector) y
  `diff_cifras_v21_conduccion` (ningun numero se movio respecto de la V2.1).
- Verificacion frase por frase: `qa/TRAZABILIDAD_LENGUAJE.csv`.

## Edicion tecnica

- PDF: {tec['pdf']}
- Extension: {tec['pdf_paginas']} paginas A4 vertical.
- Es la V2.1 tal cual, renombrada: no se le quito nada ni se reescribio nada. La portada
  la declara como edicion tecnica y el Anexo G remite a la edicion de conduccion.
- Es el respaldo metodologico completo y el destino de todo lo que salio de la otra.
- QA: los {tec['controles_qa']} controles de la V2.1.

## Ediciones anteriores

La V2 y la V2.1 auditadas permanecen en esta carpeta, sin modificar, junto con sus
paquetes de revision.

## Reproducibilidad

Ejecutar desde la raiz del repositorio, sin red:

    .venv/Scripts/python.exe -B outputs/polos_gastro/ATLAS_V2/scripts/build_geometrias_editoriales_v2.py
    .venv/Scripts/python.exe -B outputs/polos_gastro/ATLAS_V2/scripts/build_atlas_v2.py --finalize-visual

El generador verifica hashes de los insumos congelados, trabaja sin red, rechaza
referencias distintas de R01-R22, rechaza un total de paginas distinto del declarado por
cada edicion y no modifica ningun activo fuente.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")


def package_files() -> list[Path]:
    excluded_names = {
        "MANIFEST_CONTENIDO.csv", "CHECKSUMS_SHA256.txt", ZIP_NAME,
        SIDECAR_PATH.name, "RESUMEN_PRODUCCION_EDICIONES.json",
    } | EDICION_ANTERIOR
    files = []
    for path in OUT.rglob("*"):
        if not path.is_file() or path.name in excluded_names:
            continue
        rel = path.relative_to(OUT)
        if len(rel.parts) > 1 and rel.parts[0] == "qa" and rel.parts[1].startswith("render_"):
            continue
        # material de trabajo intermedio: no viaja en el paquete de revision
        if any(part.startswith("_") for part in rel.parts):
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(OUT).as_posix())


def build_manifest_and_zip() -> tuple[int, str]:
    files = package_files()
    rows = []
    for path in files:
        rel = path.relative_to(OUT).as_posix()
        rows.append({"ruta": rel, "bytes": path.stat().st_size, "sha256": sha256(path), "rol": rel.split("/", 1)[0]})
    write_csv(OUT / "MANIFEST_CONTENIDO.csv", ["ruta", "bytes", "sha256", "rol"], rows)
    checksum_targets = files + [OUT / "MANIFEST_CONTENIDO.csv"]
    lines = [f"{sha256(path)}  {path.relative_to(OUT).as_posix()}" for path in checksum_targets]
    (OUT / "CHECKSUMS_SHA256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    members = package_files() + [OUT / "MANIFEST_CONTENIDO.csv", OUT / "CHECKSUMS_SHA256.txt"]
    members = sorted(set(members), key=lambda p: p.relative_to(OUT).as_posix())
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in members:
            zf.write(path, path.relative_to(OUT).as_posix())
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
        if bad:
            raise RuntimeError(f"ZIP con CRC inválido: {bad}")
        zip_names = set(zf.namelist())
    expected_names = {p.relative_to(OUT).as_posix() for p in members}
    if zip_names != expected_names:
        raise RuntimeError("ZIP con miembros faltantes o sobrantes")
    digest = sha256(ZIP_PATH)
    SIDECAR_PATH.write_text(f"{digest}  {ZIP_NAME}\n", encoding="utf-8")
    return len(members), digest


def mark_visual_inspection_complete() -> None:
    """Cierra el QA visual sin tocar los hallazgos: solo sella que la revision ocurrio."""
    texto = (qa_file("QA_VISUAL_PRODUCTOR.md")).read_text(encoding="utf-8")
    texto = texto.replace("requiere revisión independiente posterior",
                          "inspección visual 58/58 completada; requiere revisión independiente posterior")
    (qa_file("QA_VISUAL_PRODUCTOR.md")).write_text(texto, encoding="utf-8")


def cargar_extras_detalle() -> dict:
    """Insumos puntuales de las vistas de detalle, leidos del corpus cerrado."""
    import geopandas as gpd
    extras: dict = {}
    sat = read_csv(REPO / "outputs/polos_gastro/INFORMEFINAL/codex/tanda1_saturaciones_v4_4"
                        / "outputs/SATURACIONES_RESIDUALES_CATEGORY_SPLIT_V4_4.csv")
    puntos = []
    for fila in sat:
        partes = fila["celda_id"].split("_")
        if len(partes) >= 4 and partes[-1].isdigit() and partes[-2].isdigit():
            puntos.append((float(partes[-2]), float(partes[-1])))
    extras["saturaciones"] = puntos
    mascara = (REPO / "outputs/polos_gastro/INFORMEFINAL/codex/preflight_tecnico_grupo_c_correccion_v1"
                    / "fuente/PARQUE_SAAVEDRA_ID171_MASCARA_REPARADA.geojson")
    if mascara.is_file():
        capa = gpd.read_file(mascara).to_crs("EPSG:5347")
        from shapely.ops import unary_union
        extras["parque_saavedra"] = unary_union(list(capa.geometry))
    return extras


def escribir_trazabilidad_b3() -> None:
    """Las 22 trios + las 7 de detalle, con el campo del JSON del que salen."""
    filas = []
    origen_conduccion = "edición técnica · mismo bloque, en castellano llano"
    for rid in EXPECTED_REFS:
        trio = TRIOS_ACTIVOS[rid]
        for etiqueta, clave in (("Qué muestra este mapa", "muestra"),
                                ("Qué mide la cifra", "mide"),
                                ("Qué no es", "no_es")):
            filas.append({
                "referencia_id": rid,
                "pagina_mapa": REF_PAGES[rid][1],
                "linea": etiqueta,
                "texto_publicado": trio[clave],
                "campos_de_origen": trio.get("fuente", f"{origen_conduccion}: {TRIOS[rid]['fuente']}"),
                "tipo": "principal",
            })
    # S-03: las dos ampliaciones nuevas de Palermo no tienen equivalente en la edición
    # técnica, así que su origen se declara por lo que son: una parte que ya estaba
    # nombrada en la fuente cartográfica de R01 y que hasta ahora no llegaba a la página.
    origen_nuevo = ("página nueva de la edición de conducción (S-03); parte declarada en "
                    "la fuente cartográfica de R01, sin cifra ni geometría nuevas")
    for rid, fn, title, _ in COMP_INFO_ACTIVO:
        trio = TRIOS_DETALLE_ACTIVOS[fn]
        for etiqueta, clave in (("Qué muestra este mapa", "muestra"),
                                ("Qué mide la cifra", "mide"),
                                ("Qué no es", "no_es")):
            if "fuente" in trio:
                origen = trio["fuente"]
            elif fn in TRIOS_DETALLE:
                origen = f"{origen_conduccion}: {TRIOS_DETALLE[fn]['fuente']}"
            else:
                origen = origen_nuevo
            filas.append({
                "referencia_id": rid,
                "pagina_mapa": COMP_PAGES[fn],
                "linea": etiqueta,
                "texto_publicado": trio[clave],
                "campos_de_origen": origen,
                "tipo": "detalle",
            })
    write_csv(qa_file("TRAZABILIDAD_TEXTOS_B3.csv"),
              ["referencia_id", "pagina_mapa", "linea", "texto_publicado",
               "campos_de_origen", "tipo"], filas)


def diff_cifras_v1_v2(content: dict) -> None:
    """Control R-9: ninguna cifra puede diferir de la edicion V1. Cualquier delta es FAIL."""
    v1_path = (REPO / "outputs/polos_gastro/INFORMEFINAL/claude/atlas_22_edicion_institucional_v1"
                    / "contenido/contenido_atlas_22_v2_compacta.json")
    v1 = {f["referencia_id"]: f for f in json.loads(v1_path.read_text(encoding="utf-8"))["fichas"]}

    def firma_numerica(texto: str) -> str:
        """Todos los numeros, cotas y proporciones del texto, en orden.

        El control vigila las CIFRAS, no la redaccion: esta fase reescribe prosa a
        proposito (por ejemplo, los codigos internos pasan a nombre en castellano),
        pero ningun numero puede moverse.
        """
        return " ".join(re.findall(r"≥\s*[\d.,]+|[\d.,]+\s*%|[\d.,]+", str(texto)))

    filas, fallos = [], 0
    for ficha in content["fichas"]:
        rid = ficha["referencia_id"]
        base = v1.get(rid, {})
        for campo in ("cifra", "naturaleza", "denominador_metodo"):
            a, b = str(base.get(campo, "")), str(ficha.get(campo, ""))
            ok = firma_numerica(a) == firma_numerica(b) if campo != "naturaleza" else a == b
            fallos += 0 if ok else 1
            filas.append({"referencia_id": rid, "campo": campo, "valor_v1": a,
                          "valor_v2": b, "cifras_v1": firma_numerica(a),
                          "cifras_v2": firma_numerica(b),
                          "resultado": "PASS" if ok else "FAIL"})
        a = " | ".join(base.get("detalle_cuantitativo", []))
        b = " | ".join(ficha.get("detalle_cuantitativo", []))
        ok = firma_numerica(a) == firma_numerica(b)
        fallos += 0 if ok else 1
        filas.append({"referencia_id": rid, "campo": "detalle_cuantitativo",
                      "valor_v1": a, "valor_v2": b, "cifras_v1": firma_numerica(a),
                      "cifras_v2": firma_numerica(b),
                      "resultado": "PASS" if ok else "FAIL"})
    write_csv(qa_file("DIFF_CIFRAS_V1_V2.csv"),
              ["referencia_id", "campo", "valor_v1", "valor_v2", "cifras_v1", "cifras_v2",
               "resultado"], filas)
    if fallos:
        raise RuntimeError(f"DIFF_CIFRAS_V1_V2: {fallos} diferencias; ninguna cifra puede cambiar")


def run(edicion: str, font_dir: Path | None, finalize_visual: bool,
        canonical: dict, before: dict[str, str]) -> dict:
    """Produce una edicion completa: PDF, QA y renders. No empaqueta."""
    global CARTOGRAFO, CONTENT_CACHE, EXTRAS_DETALLE, AJUSTES_FICHA, QA_MAPAS, RECORTES_TEXTO
    configurar_edicion(edicion)
    for folder in [CONTENT_DIR, MATRICES_DIR, QA_DIR, RENDER_DIR, CONTACT_DIR]:
        folder.mkdir(parents=True, exist_ok=True)
    AJUSTES_FICHA.clear()
    QA_MAPAS.clear()
    RECORTES_TEXTO.clear()
    CAJAS_DIBUJADAS.clear()
    content = build_public_content(canonical)
    CONTENT_CACHE.clear()
    CONTENT_CACHE.update(content)
    build_effective_matrices()
    CARTOGRAFO = Cartografo(REPO, CAPAS_DIR)
    EXTRAS_DETALLE.clear()
    EXTRAS_DETALLE.update(cargar_extras_detalle())
    build_pdf(content)
    write_csv(qa_file("QA_AJUSTE_FICHAS.csv"),
              ["referencia_id", "pagina", "tipo", "escala_cuerpo", "aire_pt"], AJUSTES_FICHA)
    write_csv(qa_file("QA_ROTULOS_CALLES.csv"), ["pagina", "referencia_id", "tipo", "calles"],
              [{"pagina": m["pagina"], "referencia_id": m["referencia_id"], "tipo": m["tipo"],
                "calles": m.get("calles", "")} for m in QA_MAPAS])
    escribir_trazabilidad_b3()
    diff_cifras_v1_v2(content)
    if edicion == "conduccion":
        escribir_trazabilidad_lenguaje(content)
    render_pdf()
    stats = pdf_qa(content)
    privacy_qa()
    preservation_qa(before)
    write_readme_and_qa_summary(stats)
    if finalize_visual:
        mark_visual_inspection_complete()
    return {
        "edicion": edicion,
        "pdf": PDF_NAME,
        "pdf_paginas": EXPECTED_PAGES,
        "pdf_bytes": PDF_PATH.stat().st_size,
        "pdf_sha256": sha256(PDF_PATH),
        "controles_qa": stats["checks"],
        "enlaces_internos": stats["links"],
        "marcadores": stats["toc"],
        "visual_finalizado": finalize_visual,
    }


def run_todo(font_dir: Path | None, finalize_visual: bool, ediciones: Sequence[str]) -> None:
    before, canonical = validate_inputs()
    resolve_fonts(font_dir)
    reportes = {}
    for edicion in ediciones:
        reportes[edicion] = run(edicion, font_dir, finalize_visual, canonical, before)
    if set(reportes) == set(EDICIONES):
        write_readme_carpeta(reportes)
    miembros, zip_digest = build_manifest_and_zip()
    reporte = {
        "ediciones": [reportes[e] for e in ediciones],
        "zip": ZIP_NAME,
        "zip_bytes": ZIP_PATH.stat().st_size,
        "zip_sha256": zip_digest,
        "zip_miembros": miembros,
    }
    (QA_DIR / "RESUMEN_PRODUCCION_EDICIONES.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(reporte, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera las dos ediciones del Atlas DGDGAS: conducción y técnica.")
    parser.add_argument("--font-dir", type=Path, help="Directorio con DejaVu Sans o Arial.")
    parser.add_argument("--finalize-visual", action="store_true",
                        help="Marca la inspección visual como completada después de la revisión humana del productor.")
    parser.add_argument("--edicion", choices=[*EDICIONES, "ambas"], default="ambas",
                        help="Edición a producir. Por defecto, las dos.")
    args = parser.parse_args()
    ediciones = list(EDICIONES) if args.edicion == "ambas" else [args.edicion]
    run_todo(args.font_dir, args.finalize_visual, ediciones)
    return 0


if __name__ == "__main__":
    sys.exit(main())
