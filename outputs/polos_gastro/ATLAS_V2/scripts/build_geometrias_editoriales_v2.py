#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bloque B2 — Envolvente editorial unica para las 22 referencias (Atlas V2).

Deriva una capa geometrica editorial homogenea a partir de las fuentes vectoriales
CERRADAS del corpus R01-R22. No recalcula ninguna cifra, universo, cota, proporcion,
saturacion ni decision territorial: solo cambia la forma en que se dibuja lo ya decidido.

Reglas duras:
- Todas las fuentes se abren en SOLO LECTURA y se registra su SHA-256.
- Se escribe exclusivamente dentro de outputs/polos_gastro/ATLAS_V2/.
- Sin red, sin API, sin geocodificacion nueva, sin credenciales.
- Sin datos personales: las capas de puntos solo aportan lat/lon agregadas y nunca
  se exportan filas individuales.

Dos registros visuales (AG-1):
- observado  -> envolvente derivada de puntos observados      -> borde continuo
- editorial  -> geometria editorial cerrada, sin puntos       -> borde continuo
- declarado  -> area de consulta declarada, sin puntos        -> borde PUNTEADO

Uso:
    .venv/Scripts/python.exe -B outputs/polos_gastro/ATLAS_V2/scripts/build_geometrias_editoriales_v2.py
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
import re
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.dont_write_bytecode = True

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
import shapely.affinity
from shapely.geometry import (
    GeometryCollection,
    LineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
    box,
)
from shapely.ops import unary_union

# --------------------------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------------------------

SCRIPT = Path(__file__).resolve()
OUT = SCRIPT.parent.parent                      # outputs/polos_gastro/ATLAS_V2


def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("No se encontro la raiz del repositorio")


REPO = repo_root(SCRIPT)
IF = REPO / "outputs/polos_gastro/INFORMEFINAL"
PG = REPO / "outputs/polos_gastro"

CAPAS = OUT / "capas"
QA = OUT / "qa"

CRS_METRICO = "EPSG:5347"
CRS_GEO = "EPSG:4326"

# Fuentes de solo lectura ---------------------------------------------------------------

SRC = {
    "fase24": REPO / "scripts/polos_gastro/build_fase24_fase22_corregida_oficina.py",
    "v31_belgrano": PG / "correcciones_cartograficas_post_qa_v3_1/capas/BELGRANO_PRESENTACION_V3_1.geojson",
    "v31_recoleta": PG / "correcciones_cartograficas_post_qa_v3_1/capas/RECOLETA_PRESENTACION_V3_1.geojson",
    "v31_costanera": PG / "correcciones_cartograficas_post_qa_v3_1/capas/COSTANERA_NORTE_PRESENTACION_V3_1.geojson",
    "t1_puntos": IF / "codex/tanda1_saturaciones_v4_4/outputs/universos/UNIVERSO_DEDUP_CONSERVADOR_TANDA1_V4_4.csv",
    "t1_subunidades": IF / "codex/tanda1_saturaciones_v4_4/outputs/SUBUNIDADES_CORREGIDAS_V4_4.geojson",
    "t2_puntos": IF / "codex/tanda2_ejecucion_v1/outputs/UNIVERSO_DEDUP_CONSERVADOR_TANDA2_V1.csv",
    "t2_areas": IF / "codex/tanda2_ejecucion_v1/config/AREAS_TANDA2_ANALISIS_REPARADAS.geojson",
    "grupo_a": IF / "codex/preflight_tecnico_grupo_a_v1/areas/AREAS_PROVISIONALES_GRUPO_A.geojson",
    "grupo_b": IF / "codex/preflight_tecnico_grupo_b_reparado_v1/areas/AREAS_PROVISIONALES_GRUPO_B.geojson",
    "grupo_c": IF / "codex/preflight_tecnico_grupo_c_v1/areas/AREAS_PROVISIONALES_GRUPO_C.geojson",
    "r20_producto": IF / "codex/preflight_tecnico_grupo_c_correccion_v1/areas/R20_PRODUCTO_CORREGIDO.geojson",
    "comunas": REPO / "data/raw/geo_comunas.geojson",
    "barrios": REPO / "data/raw/geo_barrios.geojson",
    # D-01 (V2.1): mascara de los diques 1 a 4 de Puerto Madero. OpenStreetMap via
    # Overpass (relaciones 2364286, 2364166, 2364163, 2364162), ODbL 1.0, acceso
    # 2026-08-03, contrastada contra la capa oficial `cuerpos_de_agua_mapa_base_v2`
    # del WMS de IDECABA con 97,113% de coincidencia raster. Cierra BLOQUEADO-01.
    "r04_agua": PG / ("INVESTIGACION_DESBLOQUEOS_V21/paquete/r04_puerto_madero/"
                      "geometrias/r04_mascara_agua_propuesta.geojson"),
}

# --------------------------------------------------------------------------------------
# Familias tipologicas (D-4) y colores
# --------------------------------------------------------------------------------------

FAMILIAS = {
    "polo": ("Polo", "#1F3B57"),
    "multiparte": ("Polo con subzonas / multiparte", "#2C7FB8"),
    "eje": ("Eje o corredor", "#C0762B"),
    "segmentada": ("Area segmentada", "#2D7A68"),
    "dispersa": ("Referencia dispersa", "#7353A6"),
}

# --------------------------------------------------------------------------------------
# Especificacion por referencia
#
#   registro : observado | editorial | declarado   (AG-1)
#   buffer_m : expansion aplicada SOLO cuando el origen son puntos observados
#   cierre_m : cierre morfologico buffer(+d).buffer(-d)
#   suavizado: iteraciones de Chaikin (0 = sin suavizar)
# --------------------------------------------------------------------------------------

REFS = [
    dict(id="R01", nombre="Palermo", familia="multiparte", registro="editorial",
         origen="fase24:palermo", buffer_m=0, cierre_m=80, suavizado=2, multiparte=True),
    dict(id="R02", nombre="Avenida Corrientes", familia="eje", registro="declarado",
         origen="fase24:corrientes:line", buffer_m=200, cierre_m=80, suavizado=2, multiparte=False),
    dict(id="R03", nombre="San Telmo", familia="polo", registro="editorial",
         origen="fase24:san_telmo", buffer_m=0, cierre_m=100, suavizado=3, multiparte=False),
    dict(id="R04", nombre="Puerto Madero", familia="multiparte", registro="editorial",
         origen="fase24:puerto", buffer_m=0, cierre_m=80, suavizado=2, multiparte=True),
    dict(id="R05", nombre="Belgrano", familia="polo", registro="editorial",
         origen="v31:belgrano", buffer_m=0, cierre_m=90, suavizado=2, multiparte=True),
    dict(id="R06", nombre="Recoleta", familia="polo", registro="editorial",
         origen="v31:recoleta", buffer_m=0, cierre_m=90, suavizado=2, multiparte=False),
    dict(id="R07", nombre="Costanera Norte", familia="multiparte", registro="editorial",
         origen="v31:costanera", buffer_m=0, cierre_m=70, suavizado=2, multiparte=True),
    dict(id="R08", nombre="Villa Crespo", familia="polo", registro="observado",
         origen="t1:Z01", buffer_m=200, cierre_m=140, suavizado=2, multiparte=False),
    dict(id="R09", nombre="Chacarita", familia="dispersa", registro="observado",
         origen="t1sub:Z02", buffer_m=200, cierre_m=120, suavizado=2, multiparte=True,
         subunidades=["Z02-S1", "Z02-S2"]),
    dict(id="R10", nombre="Caballito", familia="multiparte", registro="observado",
         origen="t1sub:Z03", buffer_m=150, cierre_m=110, suavizado=2, multiparte=True,
         subunidades=["Z03-S1", "Z03-S2"]),
    dict(id="R11", nombre="Boulevard Caseros", familia="eje", registro="observado",
         origen="t1:Z04", buffer_m=120, cierre_m=80, suavizado=2, multiparte=False),
    dict(id="R12", nombre="Centro / Microcentro segmentado", familia="segmentada", registro="declarado",
         origen="grupo_a:R12", buffer_m=0, cierre_m=60, suavizado=2, multiparte=True),
    dict(id="R13", nombre="Abasto", familia="polo", registro="declarado",
         origen="grupo_a:R13", buffer_m=0, cierre_m=60, suavizado=2, multiparte=False),
    dict(id="R14", nombre="Avenida Boedo", familia="eje", registro="observado",
         origen="t2:Z07", buffer_m=200, cierre_m=120, suavizado=2, multiparte=False),
    dict(id="R15", nombre="Devoto", familia="polo", registro="observado",
         origen="t2:Z08", buffer_m=200, cierre_m=130, suavizado=2, multiparte=False),
    dict(id="R16", nombre="Donado-Holmberg", familia="eje", registro="observado",
         origen="t2:Z09", buffer_m=200, cierre_m=110, suavizado=2, multiparte=True),
    dict(id="R17", nombre="Villa Urquiza", familia="multiparte", registro="observado",
         origen="t2:Z10", buffer_m=200, cierre_m=130, suavizado=2, multiparte=True),
    dict(id="R18", nombre="Esmeralda-Paraguay", familia="dispersa", registro="declarado",
         origen="grupo_a:R18", buffer_m=0, cierre_m=0, suavizado=0, multiparte=False),
    dict(id="R19", nombre="Federico Lacroze por tramos", familia="eje", registro="declarado",
         origen="grupo_b:R19", buffer_m=0, cierre_m=60, suavizado=2, multiparte=True),
    dict(id="R20", nombre="Garcia del Rio", familia="eje", registro="declarado",
         origen="grupo_c:R20", buffer_m=0, cierre_m=40, suavizado=2, multiparte=False),
    dict(id="R21", nombre="La Paternal", familia="dispersa", registro="declarado",
         origen="grupo_b:R21", buffer_m=0, cierre_m=80, suavizado=2, multiparte=True),
    dict(id="R22", nombre="Villa Pueyrredon", familia="dispersa", registro="declarado",
         origen="grupo_c:R22", buffer_m=0, cierre_m=0, suavizado=0, multiparte=False),
]

# Exenciones de recorte mutuo. La exencion es por DECLARACION DEL CORPUS, nunca por
# registro geometrico: que una sea eje y la otra area no alcanza. Cada par lleva su motivo
# y se publica en QA_SOLAPES_22.csv.
EXENCIONES_RECORTE = {
    ("R12", "R18"): (
        "geometria compartida declarada: el corpus define una sola geometria (C-S07) con "
        "dos productos separados, R18 y R12"),
    ("R02", "R12"): (
        "eje que atraviesa un area; el corpus no declara discontinuidad del corredor de "
        "Av. Corrientes y registra la co-localizacion en GA-R12-CS08-CONTROL (R12;R02)"),
}
PARES_COMPARTIDOS_DECLARADOS = set(EXENCIONES_RECORTE)

# Orden de dibujo. Solo se aparta del default (0) donde una exencion produce superposicion
# y hay que decidir cual queda arriba.
Z_ORDEN = {"R02": 2, "R18": 2}

GAP_M = 6.0             # erosion por lado en las costuras -> separacion visible de 12 m
SIMPLIFY_M = 12.0       # tolerancia de simplificacion topologica
ASTILLA_MIN_M2 = 8000   # piso absoluto de visibilidad de una pieza en pagina
ASTILLA_FRACCION = 0.02 # y ademas 2% de la pieza mayor de la referencia


# --------------------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------------------

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def chaikin_ring(coords: list[tuple[float, float]], iterations: int) -> list[tuple[float, float]]:
    """Corner-cutting de Chaikin sobre un anillo cerrado."""
    if iterations <= 0 or len(coords) < 4:
        return coords
    ring = list(coords)
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    for _ in range(iterations):
        nuevo: list[tuple[float, float]] = []
        for i in range(len(ring) - 1):
            p, q = ring[i], ring[i + 1]
            nuevo.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            nuevo.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
        nuevo.append(nuevo[0])
        ring = nuevo
    return ring


def suavizar(geom, iterations: int):
    """Aplica Chaikin a exteriores e interiores preservando la topologia multiparte."""
    if iterations <= 0 or geom.is_empty:
        return geom
    piezas = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    salida = []
    for pieza in piezas:
        ext = chaikin_ring(list(pieza.exterior.coords), iterations)
        ints = [chaikin_ring(list(r.coords), iterations) for r in pieza.interiors]
        try:
            nuevo = Polygon(ext, ints)
            if not nuevo.is_valid:
                nuevo = nuevo.buffer(0)
            if not nuevo.is_empty:
                salida.append(nuevo)
        except Exception:
            salida.append(pieza)
    if not salida:
        return geom
    return salida[0] if len(salida) == 1 else MultiPolygon(salida)


def envolvente(geom, buffer_m: float, cierre_m: float, suave: int):
    """Buffer opcional -> cierre morfologico -> simplificacion -> suavizado."""
    g = geom
    if buffer_m > 0:
        g = g.buffer(buffer_m)
    g = unary_union(g)
    if cierre_m > 0:
        g = g.buffer(cierre_m).buffer(-cierre_m)
    if g.is_empty:
        return g
    g = g.simplify(SIMPLIFY_M, preserve_topology=True)
    g = suavizar(g, suave)
    if not g.is_valid:
        g = g.buffer(0)
    return g


def ablandar_esquinas(geom, radio: float):
    """Redondea las esquinas conservando los lados rectos.

    D-5c (R20): la fuente es una banda recta derivada de la traza vial, con extremos
    planos deliberados ("no prolonga el eje antes de Cabildo ni dentro del parque").
    No hay lados curvos que suavizar: aplicar Chaikin la deformaria en un huso y
    movería los extremos. Se ablanda solo el angulo vivo de las esquinas.
    """
    suave = geom.buffer(-radio, join_style=1).buffer(radio, join_style=1)
    suave = solo_poligonos(suave)
    return suave if not suave.is_empty else geom


def componer_multiparte(piezas: list):
    """Une piezas de una misma referencia SIN fusionarlas.

    El corpus exige que R01, R04, R05, R07, R09, R10, R12, R16, R17, R19 y R21
    conserven sus componentes visibles. Si dos piezas se tocan, se separan por la
    misma costura que se usa entre referencias en vez de convertirse en un poligono
    unico.
    """
    piezas = [p for p in piezas if p is not None and not p.is_empty]
    if len(piezas) <= 1:
        return unary_union(piezas) if piezas else Polygon()
    salida = []
    for i, p in enumerate(piezas):
        otros = unary_union([q for j, q in enumerate(piezas) if j != i])
        recorte = solo_poligonos(p.difference(otros.buffer(GAP_M)))
        salida.append(recorte if not recorte.is_empty else p)
    return unary_union(salida)


def solo_poligonos(geom):
    if geom.is_empty:
        return geom
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    piezas = [g for g in getattr(geom, "geoms", []) if g.geom_type in ("Polygon", "MultiPolygon")]
    if not piezas:
        return Polygon()
    return unary_union(piezas)


# --------------------------------------------------------------------------------------
# Carga de fuentes (solo lectura)
# --------------------------------------------------------------------------------------

def cargar_fase24() -> dict[str, list[dict]]:
    """Extrae GEOMETRIES por AST, sin ejecutar el modulo (cero efectos secundarios)."""
    texto = SRC["fase24"].read_text(encoding="utf-8")
    m = re.search(r"^GEOMETRIES\s*=\s*(\[.*?^\])", texto, re.S | re.M)
    if not m:
        raise RuntimeError("No se encontro GEOMETRIES en el script fase24")
    bloque = re.sub(r'("color":\s*)([A-Z_][A-Z_0-9]*)', r'\1"\2"', m.group(1))
    entradas = ast.literal_eval(bloque)
    por_key: dict[str, list[dict]] = {}
    for e in entradas:
        por_key.setdefault(e["key"], []).append(e)
    return por_key


def geom_fase24(entrada: dict):
    coords = entrada["coords"]
    if entrada["shape"] == "polygon":
        return Polygon(coords)
    if entrada["shape"] == "line":
        return LineString(coords)
    return Point(coords[0])


def puntos_tanda1() -> gpd.GeoDataFrame:
    df = pd.read_csv(SRC["t1_puntos"], dtype=str, keep_default_na=False)
    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)
    g = gpd.GeoDataFrame(
        df[["zona_id"]],
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs=CRS_GEO,
    )
    return g.to_crs(CRS_METRICO)


def puntos_tanda2() -> gpd.GeoDataFrame:
    """Solo la porcion E-PLACES: es la que corresponde a las cifras de R14-R17."""
    df = pd.read_csv(SRC["t2_puntos"], dtype=str, keep_default_na=False)
    df = df[df["fuente"] == "E-PLACES"].copy()
    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)
    g = gpd.GeoDataFrame(
        df[["zonas"]],
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs=CRS_GEO,
    )
    return g.to_crs(CRS_METRICO)


def leer_capa(clave: str) -> gpd.GeoDataFrame:
    return gpd.read_file(SRC[clave]).to_crs(CRS_METRICO)


# --------------------------------------------------------------------------------------
# Construccion de nucleos y envolventes
# --------------------------------------------------------------------------------------

def construir(fuentes: dict) -> tuple[dict, dict, list[dict]]:
    f24 = fuentes["f24"]
    p1, p2 = fuentes["p1"], fuentes["p2"]
    ga, gb, gc = fuentes["ga"], fuentes["gb"], fuentes["gc"]
    r20 = fuentes["r20"]
    t2a = fuentes["t2a"]

    nucleos: dict[str, object] = {}
    envolventes: dict[str, object] = {}
    trazas: list[dict] = []
    componentes: list[dict] = []
    tierra = unary_union(list(fuentes["barrios"].geometry))
    subunidades_t1 = fuentes["sub1"]

    def componente(rid, nombre, rol, geom):
        if geom is None or geom.is_empty:
            return
        componentes.append({"referencia_id": rid, "componente": nombre, "rol": rol,
                            "geometry": geom})

    def registrar(ref, nucleo, env, soporte, detalle):
        nucleos[ref["id"]] = nucleo
        envolventes[ref["id"]] = env
        trazas.append({
            "referencia_id": ref["id"],
            "nombre": ref["nombre"],
            "familia": ref["familia"],
            "registro": ref["registro"],
            "origen": ref["origen"],
            "buffer_m": ref["buffer_m"],
            "cierre_m": ref["cierre_m"],
            "suavizado_chaikin": ref["suavizado"],
            "soporte": soporte,
            "detalle_construccion": detalle,
        })

    for ref in REFS:
        rid, origen = ref["id"], ref["origen"]

        # ---- fase24 (R01-R04) -----------------------------------------------------
        if origen.startswith("fase24:"):
            partes = origen.split(":")
            key = partes[1]
            entradas = f24[key]
            if len(partes) > 2 and partes[2] == "line":
                usadas = [e for e in entradas if e["shape"] == "line"]
                soporte = f"{len(usadas)} eje(s) declarado(s)"
            else:
                usadas = [e for e in entradas if e["shape"] == "polygon"]
                soporte = f"{len(usadas)} poligono(s) editorial(es) cerrados"
            base = [geom_fase24(e) for e in usadas]
            # Cada pieza conserva el nombre con que la fuente la declara. Sin esto, las
            # partes nombradas de R01 y R04 se perdian al componer la envolvente y el mapa
            # solo podia rotular la referencia entera.
            nombres = [str(e.get("label") or e.get("subzona") or rid) for e in usadas]
            gs = gpd.GeoSeries(base, crs=CRS_GEO).to_crs(CRS_METRICO)
            if rid == "R04":
                # D-A-05: se sustrae la superficie que cae fuera de todo poligono barrial
                # oficial, es decir sobre el Rio de la Plata. Solo agua, nunca parques.
                gs = gpd.GeoSeries([solo_poligonos(g.intersection(tierra)) for g in gs],
                                   crs=CRS_METRICO)
                gs = gs[~gs.is_empty]
                soporte += " recortados contra tierra barrial oficial"
            nucleo = unary_union(list(gs))
            if ref["multiparte"]:
                piezas = {i: envolvente(gs.loc[i], ref["buffer_m"], ref["cierre_m"],
                                        ref["suavizado"]) for i in gs.index}
                env = componer_multiparte(list(piezas.values()))
                # La envolvente no cambia: las partes son las MISMAS piezas con las que ya
                # se componia, registradas ademas con su nombre para poder rotularlas.
                for i, pieza in piezas.items():
                    componente(rid, nombres[i], "PARTE_DECLARADA_FASE24", pieza)
            else:
                env = envolvente(nucleo, ref["buffer_m"], ref["cierre_m"], ref["suavizado"])
            registrar(ref, nucleo, solo_poligonos(env), soporte,
                      f"fase24 key={key}")

        # ---- V3.1 (R05-R07) --------------------------------------------------------
        elif origen.startswith("v31:"):
            capa = leer_capa("v31_" + origen.split(":")[1])
            nucleo = unary_union(list(capa.geometry))
            if ref["multiparte"]:
                env = componer_multiparte([
                    envolvente(g, 0, ref["cierre_m"], ref["suavizado"]) for g in capa.geometry
                ])
            else:
                env = envolvente(nucleo, 0, ref["cierre_m"], ref["suavizado"])
            etiqueta = ("nombre_publico" if "nombre_publico" in capa.columns
                        else "componente_publico" if "componente_publico" in capa.columns
                        else None)
            for _, f in capa.iterrows():
                componente(rid, str(f[etiqueta]) if etiqueta else rid,
                           str(f.get("categoria_publica", "componente")),
                           envolvente(f.geometry, 0, ref["cierre_m"], ref["suavizado"]))
            registrar(ref, nucleo, solo_poligonos(env),
                      f"{len(capa)} centralidad(es)/componente(s) de presentacion V3.1",
                      "capa de presentacion institucional cerrada V3.1; "
                      "las piezas se agrupan por centralidad, sin alterar la geometria")

        # ---- Tanda 1 por SUBUNIDAD declarada (R09, R10) ----------------------------
        # Los focos que el corpus declara independientes no se fusionan en una mancha:
        # cada subunidad envuelve solo los puntos que caen dentro de ella.
        elif origen.startswith("t1sub:"):
            zona = origen.split(":")[1]
            pts = p1[p1["zona_id"] == zona]
            sel = subunidades_t1[subunidades_t1["subunidad_id"].isin(ref["subunidades"])]
            piezas, detalles, cubiertos = [], [], 0
            for _, sub in sel.iterrows():
                dentro = pts[pts.within(sub.geometry)]
                if dentro.empty:
                    continue
                cubiertos += len(dentro)
                pieza = envolvente(MultiPoint(list(dentro.geometry)), ref["buffer_m"],
                                   ref["cierre_m"], ref["suavizado"])
                piezas.append(pieza)
                detalles.append(f"{sub['nombre']} ({len(dentro)} puntos)")
                componente(rid, str(sub["nombre"]), "subunidad declarada", pieza)
            nucleo = MultiPoint(list(pts[pts.within(unary_union(list(sel.geometry)))].geometry))
            env = componer_multiparte(piezas)
            registrar(ref, nucleo, solo_poligonos(env),
                      f"{cubiertos} de {len(pts)} puntos observados, dentro de "
                      f"{len(piezas)} subunidad(es) declarada(s) ({zona})",
                      "envolvente por subunidad declarada: " + " · ".join(detalles))

        # ---- Tanda 1 por puntos (R08-R11) -----------------------------------------
        elif origen.startswith("t1:"):
            zona = origen.split(":")[1]
            pts = p1[p1["zona_id"] == zona]
            nucleo = MultiPoint(list(pts.geometry))
            env = envolvente(nucleo, ref["buffer_m"], ref["cierre_m"], ref["suavizado"])
            registrar(ref, nucleo, solo_poligonos(env),
                      f"{len(pts)} puntos observados ({zona})",
                      f"buffer {ref['buffer_m']} m sobre puntos del universo deduplicado")

        # ---- Tanda 2 por puntos E-PLACES (R14-R17) ---------------------------------
        elif origen.startswith("t2:"):
            zona = origen.split(":")[1]
            mask = p2["zonas"].apply(lambda z: zona in str(z).split("|"))
            pts = p2[mask]
            nucleo = MultiPoint(list(pts.geometry))
            env = envolvente(nucleo, ref["buffer_m"], ref["cierre_m"], ref["suavizado"])
            # D-5d: recortar contra la geometria de producto ya cerrada.
            area = t2a[(t2a["zona_id"] == zona) & (t2a["geometry_role"] == "AREA_PRINCIPAL")]
            recorte_nota = "sin recorte"
            if not area.empty:
                producto = unary_union(list(area.geometry)).buffer(ref["buffer_m"])
                recortado = env.intersection(producto)
                if not recortado.is_empty:
                    env = recortado
                    recorte_nota = "recortado al area de producto cerrada (D-5d)"
            registrar(ref, nucleo, solo_poligonos(env),
                      f"{len(pts)} puntos observados E-PLACES ({zona})",
                      f"buffer {ref['buffer_m']} m sobre puntos; {recorte_nota}")

        # ---- Grupo A (R12, R13, R18) ----------------------------------------------
        elif origen.startswith("grupo_a:"):
            objetivo = origen.split(":")[1]
            if objetivo == "R12":
                sel = ga[ga["id"].isin(
                    ["GA-R12-CS01", "GA-R12-CS03", "GA-R12-CS04", "GA-R12-CS05", "GA-R12-CS06"]
                )]
                detalle = "5 subunidades operativas; C-S02 sin geometria, C-S08 es control (excluido); C-S07 se comparte con R18"
            elif objetivo == "R13":
                sel = ga[ga["id"] == "GA-R13"]
                detalle = "tramo declarado Corrientes 3000 a 3800, buffer 350 m"
            else:
                sel = ga[ga["id"] == "GA-R18-CS07-COMPARTIDA"]
                detalle = "disco de consulta de 400 m en torno a Esmeralda y Paraguay (D-5a: sin suavizar, sin punto central)"
            sel = sel[sel.geometry.notna()]
            for _, f in sel.iterrows():
                componente(rid, str(f["nombre"]), str(f["subunidad_id"]),
                           envolvente(f.geometry, 0, ref["cierre_m"], ref["suavizado"]))
            nucleo = unary_union(list(sel.geometry))
            if ref["multiparte"]:
                env = componer_multiparte([
                    envolvente(g, 0, ref["cierre_m"], ref["suavizado"]) for g in sel.geometry
                ])
            else:
                env = envolvente(nucleo, 0, ref["cierre_m"], ref["suavizado"])
            registrar(ref, nucleo, solo_poligonos(env),
                      f"{len(sel)} area(s) de consulta declarada(s)", detalle)

        # ---- Grupo B (R19, R21) ----------------------------------------------------
        elif origen.startswith("grupo_b:"):
            objetivo = origen.split(":")[1]
            sel = gb[(gb["referencia_id"] == objetivo) & (gb["funcion"] != "CONTROL_NO_PRODUCTO")]
            for _, f in sel.iterrows():
                componente(rid, str(f["nombre"]), str(f["subunidad"]),
                           envolvente(f.geometry, 0, ref["cierre_m"], ref["suavizado"]))
            nucleo = unary_union(list(sel.geometry))
            env = componer_multiparte([
                envolvente(g, 0, ref["cierre_m"], ref["suavizado"]) for g in sel.geometry
            ])
            registrar(ref, nucleo, solo_poligonos(env),
                      f"{len(sel)} tramo(s)/area(s) declarada(s)",
                      "controles CONTROL_NO_PRODUCTO excluidos del producto")

        # ---- Grupo C (R20, R22) ----------------------------------------------------
        else:
            objetivo = origen.split(":")[1]
            if objetivo == "R20":
                sel = r20
                nucleo = unary_union(list(sel.geometry))
                env = ablandar_esquinas(nucleo, 30.0)
                detalle = "banda plana de 180 m; esquinas ablandadas 30 m y extremos planos preservados (D-5c)"
                soporte = "1 banda declarada corregida"
            else:
                sel = gc[gc["referencia_id"] == "R22"]
                nucleo = unary_union(list(sel.geometry))
                env = nucleo                      # D-5b: sin suavizar
                detalle = "marco de relevamiento barrial; sin suavizar y sin grilla interna (D-5b)"
                soporte = "1 marco de muestreo declarado"
            registrar(ref, nucleo, solo_poligonos(env), soporte, detalle)

    return nucleos, envolventes, trazas, componentes


# --------------------------------------------------------------------------------------
# Recorte mutuo por linea media (Voronoi)
# --------------------------------------------------------------------------------------

def semillas(geom, paso: float = 60.0) -> list[Point]:
    """Puntos de siembra: los propios puntos, o el contorno densificado de la geometria."""
    if geom.is_empty:
        return []
    if geom.geom_type == "Point":
        return [geom]
    if geom.geom_type == "MultiPoint":
        return list(geom.geoms)
    pts: list[Point] = []
    for pieza in (geom.geoms if geom.geom_type.startswith("Multi") else [geom]):
        if pieza.geom_type in ("LineString", "LinearRing"):
            linea = shapely.segmentize(pieza, paso)
            pts.extend(Point(c) for c in linea.coords)
            continue
        borde = shapely.segmentize(pieza.boundary, paso)
        for linea in (borde.geoms if borde.geom_type.startswith("Multi") else [borde]):
            pts.extend(Point(c) for c in linea.coords)
        pts.append(pieza.representative_point())
    return pts


def pulir_corte(geom, apertura: float = 25.0):
    """Apertura morfologica del borde cortado + suavizado leve.

    El recorte por linea media deja filamentos donde dos formas se rozan. La apertura
    los elimina y el Chaikin evita que la costura quede como un borde dentado.
    """
    if geom.is_empty:
        return geom
    abierto = geom.buffer(-apertura).buffer(apertura)
    abierto = solo_poligonos(abierto)
    if abierto.is_empty:
        return geom
    return suavizar(abierto.simplify(SIMPLIFY_M, preserve_topology=True), 1)


def grilla_interior(geom, paso: float = 50.0) -> list[Point]:
    """Siembra el interior con una grilla GLOBALMENTE ALINEADA.

    La alineacion comun es deliberada: donde dos envolventes se superponen, ambas
    reclaman exactamente las mismas coordenadas, esas semillas se descartan y la
    frontera queda decidida por la linea media de las semillas no compartidas.
    """
    minx, miny, maxx, maxy = geom.bounds
    xs = np.arange(np.floor(minx / paso) * paso, maxx + paso, paso)
    ys = np.arange(np.floor(miny / paso) * paso, maxy + paso, paso)
    if xs.size * ys.size > 400_000:
        return []
    malla = np.array(np.meshgrid(xs, ys)).T.reshape(-1, 2)
    dentro = shapely.contains_xy(geom, malla[:, 0], malla[:, 1])
    return [Point(x, y) for x, y in malla[dentro]]


def recorte_voronoi(nucleos: dict, envolventes: dict) -> tuple[dict, dict]:
    # Siembra: nucleo + contorno + interior de la propia envolvente, para que la
    # linea media caiga entre las formas efectivamente dibujadas y ninguna
    # referencia deje su interior sin reclamar.
    # Deliberadamente NO se siembra con los puntos observados uno a uno: donde dos
    # nubes se interpenetran, sus celdas se alternan y el recorte deshilacha la forma.
    # La linea media se decide entre las formas dibujadas, no entre observaciones.
    reclamos: dict[tuple[int, int], set[str]] = {}
    for rid in nucleos:
        env = envolventes[rid]
        for p in semillas(env.boundary, paso=60.0) + grilla_interior(env):
            reclamos.setdefault((round(p.x), round(p.y)), set()).add(rid)

    # Una coordenada reclamada por dos referencias (p. ej. los 36 puntos que R16 y R17
    # comparten) no discrimina: se descarta de la siembra, no de la envolvente.
    pts, dueno, compartidas = [], [], 0
    for (x, y), duenos in reclamos.items():
        if len(duenos) != 1:
            compartidas += 1
            continue
        pts.append(Point(x, y))
        dueno.append(next(iter(duenos)))
    if compartidas:
        print(f"  semillas descartadas por reclamo multiple: {compartidas}")

    extent = box(*gpd.GeoSeries(list(envolventes.values()), crs=CRS_METRICO).total_bounds).buffer(5000)
    celdas = shapely.voronoi_polygons(MultiPoint(pts), extend_to=extent, ordered=True)
    lista = list(celdas.geoms)
    if len(lista) != len(pts):
        raise RuntimeError(f"Voronoi devolvio {len(lista)} celdas para {len(pts)} semillas")

    regiones: dict[str, list] = {}
    for celda, rid in zip(lista, dueno):
        regiones.setdefault(rid, []).append(celda)
    regiones = {rid: unary_union(cs) for rid, cs in regiones.items()}

    # Los pares exentos comparten region en vez de disputarsela. Se resuelve ANTES de
    # recortar: unir geometrias ya pulidas dejaba huecos y cunas dentro de la forma.
    efectivas = {}
    for rid in envolventes:
        propias = [regiones[rid]]
        for a, b in EXENCIONES_RECORTE:
            if rid == a and b in regiones:
                propias.append(regiones[b])
            elif rid == b and a in regiones:
                propias.append(regiones[a])
        efectivas[rid] = unary_union(propias)

    recortadas = {}
    for rid, env in envolventes.items():
        r = solo_poligonos(env.intersection(efectivas[rid]))
        recortadas[rid] = pulir_corte(r) if not r.is_empty else env
    return recortadas, regiones


def sustraer_agua_r04(finales: dict, trazas: list[dict]) -> tuple[dict, dict]:
    """D-01 (V2.1) - descuenta los espejos de agua de los cuatro diques de Puerto Madero.

    Se aplica al final, sobre la geometria ya recortada y pulida, para que el area
    resultante sea exactamente la que la auditoria independiente verifico contra el WMS
    oficial de IDECABA. Solo se resta la INTERSECCION de la mascara con R04: la mascara
    OSM excede la envolvente y esa parte no se toca. Ninguna otra referencia se modifica
    y ningun parque ni plaza entra en la sustraccion.
    """
    mascara = gpd.read_file(SRC["r04_agua"]).to_crs(CRS_METRICO)
    agua = unary_union(list(mascara.geometry))
    antes = finales["R04"]
    quitado = antes.intersection(agua)
    despues = solo_poligonos(antes.difference(agua))
    if despues.is_empty:
        raise RuntimeError("La sustraccion de agua vacio R04")
    for otro, geom in finales.items():
        if otro != "R04" and geom.intersects(agua) and geom.intersection(agua).area > 1.0:
            raise RuntimeError(f"La mascara de agua toca {otro}: solo puede afectar a R04")
    finales["R04"] = despues
    for t in trazas:
        if t["referencia_id"] == "R04":
            t["soporte"] += " y sin los espejos de agua de los diques 1 a 4"
            t["detalle_construccion"] += (
                "; agua de los diques sustraida con mascara OpenStreetMap/Overpass "
                "(ODbL 1.0, acceso 2026-08-03) validada contra el WMS oficial de IDECABA")
    reporte = {
        "area_antes_km2": round(antes.area / 1e6, 6),
        "area_agua_sustraida_km2": round(quitado.area / 1e6, 6),
        "area_despues_km2": round(despues.area / 1e6, 6),
        "mascara_total_km2": round(agua.area / 1e6, 6),
        "fuente": "OpenStreetMap/Overpass ODbL 1.0; validada contra IDECABA WMS "
                  "cuerpos_de_agua_mapa_base_v2 (97,113% de coincidencia raster)",
        "alcance": "solo R04; ninguna otra referencia intersecta la mascara",
    }
    print(f"  R04 sin agua: {reporte['area_antes_km2']} -> {reporte['area_despues_km2']} km2 "
          f"(-{reporte['area_agua_sustraida_km2']})")
    return finales, reporte


def separar_costuras(recortadas: dict) -> dict:
    """Erosiona GAP_M por lado solo donde dos referencias se tocan."""
    def compartido(a: str, b: str) -> bool:
        return (a, b) in PARES_COMPARTIDOS_DECLARADOS or (b, a) in PARES_COMPARTIDOS_DECLARADOS

    salida = {}
    for rid, geom in recortadas.items():
        otros = [g for k, g in recortadas.items()
                 if k != rid and not compartido(rid, k) and g.distance(geom) < 1.0]
        if not otros:
            salida[rid] = geom
            continue
        recorte = geom.difference(unary_union(otros).buffer(GAP_M))
        recorte = solo_poligonos(recorte)
        salida[rid] = recorte if not recorte.is_empty else geom
    return salida


def limpiar_astillas(geoms: dict) -> tuple[dict, list[dict]]:
    """Descarta esquirlas cartograficas del recorte.

    Solo elimina fragmentos irrelevantes a escala de lectura (por debajo del umbral
    de visibilidad en pagina). No altera cifras: la superficie es un recurso de
    dibujo, nunca un dato publicado.
    """
    salida, reporte = {}, []
    for rid, geom in geoms.items():
        piezas = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        if not piezas:
            salida[rid] = geom
            continue
        mayor = max(p.area for p in piezas)
        umbral = max(ASTILLA_MIN_M2, mayor * ASTILLA_FRACCION)
        conservadas = [p for p in piezas if p.area >= umbral]
        if not conservadas:
            conservadas = [max(piezas, key=lambda p: p.area)]
        descartadas = len(piezas) - len(conservadas)
        area_desc = sum(p.area for p in piezas) - sum(p.area for p in conservadas)
        salida[rid] = conservadas[0] if len(conservadas) == 1 else MultiPolygon(conservadas)
        reporte.append({
            "referencia_id": rid,
            "piezas_antes": len(piezas),
            "piezas_despues": len(conservadas),
            "astillas_descartadas": descartadas,
            "area_descartada_m2": round(area_desc, 1),
            "porcentaje_area_descartada": round(100 * area_desc / geom.area, 3) if geom.area else 0.0,
            "umbral_m2": round(umbral, 1),
        })
    return salida, reporte


# --------------------------------------------------------------------------------------
# QA de solapes
# --------------------------------------------------------------------------------------

def motivo_exencion(a: str, b: str) -> str:
    return EXENCIONES_RECORTE.get((a, b)) or EXENCIONES_RECORTE.get((b, a)) or ""


def qa_solapes(previas: dict, finales: dict) -> list[dict]:
    filas = []
    ids = [r["id"] for r in REFS]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            antes = previas[a].intersection(previas[b]).area
            despues = finales[a].intersection(finales[b]).area
            declarado = (a, b) in PARES_COMPARTIDOS_DECLARADOS or (b, a) in PARES_COMPARTIDOS_DECLARADOS
            if antes < 1 and despues < 1 and not declarado:
                continue
            if declarado:
                resultado = "EXENTO_DECLARADO"
            elif despues < 1.0:
                resultado = "PASS"
            else:
                resultado = "FAIL"
            filas.append({
                "referencia_a": a,
                "referencia_b": b,
                "solape_m2_sin_recorte": round(antes, 1),
                "solape_m2_final": round(despues, 1),
                "relacion_declarada": "CO-LOCALIZADA_DECLARADA" if declarado else "INDEPENDIENTE",
                "resultado": resultado,
                "motivo_exencion": motivo_exencion(a, b),
            })
    return filas


# --------------------------------------------------------------------------------------
# Salidas
# --------------------------------------------------------------------------------------

def escribir_capas(finales: dict, nucleos: dict, trazas: list[dict]) -> gpd.GeoDataFrame:
    CAPAS.mkdir(parents=True, exist_ok=True)
    por_id = {t["referencia_id"]: t for t in trazas}
    filas = []
    for rid, geom in finales.items():
        t = por_id[rid]
        filas.append({
            "referencia_id": rid,
            "nombre": t["nombre"],
            "familia": t["familia"],
            "familia_etiqueta": FAMILIAS[t["familia"]][0],
            "color": FAMILIAS[t["familia"]][1],
            "registro": t["registro"],
            "trazo": "punteado" if t["registro"] == "declarado" else "continuo",
            "piezas": len(geom.geoms) if geom.geom_type == "MultiPolygon" else 1,
            "z_orden": Z_ORDEN.get(rid, 0),
            "area_km2": round(geom.area / 1e6, 4),
            "soporte": t["soporte"],
            "geometry": geom,
        })
    env = gpd.GeoDataFrame(filas, crs=CRS_METRICO)
    env.to_crs(CRS_GEO).to_file(CAPAS / "envolventes_editoriales_v2.geojson", driver="GeoJSON")

    nuc = gpd.GeoDataFrame(
        [{"referencia_id": rid, "tipo": nucleos[rid].geom_type} for rid in nucleos],
        geometry=[nucleos[rid] for rid in nucleos], crs=CRS_METRICO,
    )
    nuc.to_crs(CRS_GEO).to_file(CAPAS / "nucleos_prebuffer_v2.geojson", driver="GeoJSON")
    return env


def recortar_componentes(componentes: list[dict], finales: dict,
                         roles: set[str]) -> list[dict]:
    """Ajusta a la envolvente final las partes que se van a rotular sobre el mapa.

    La envolvente se recorta contra las referencias vecinas DESPUES de componerse, asi
    que una parte declarada puede sobrar por el borde. El rotulo se ancla en el punto
    representativo de la parte: si la parte sobresale, el rotulo cae fuera de la tinta
    que el mapa dibuja. Se recorta solo lo indicado por `roles` para no mover los
    rotulos ya publicados de las nueve referencias que hoy tienen partes.
    """
    salida = []
    for comp in componentes:
        if comp["rol"] not in roles:
            salida.append(comp)
            continue
        env = finales.get(comp["referencia_id"])
        recortado = solo_poligonos(comp["geometry"].intersection(env)) if env is not None else None
        if recortado is None or recortado.is_empty:
            continue
        salida.append({**comp, "geometry": recortado})
    return salida


def escribir_componentes(componentes: list[dict]) -> None:
    """Componentes internos rotulables (subunidades, centralidades, tramos)."""
    if not componentes:
        return
    gdf = gpd.GeoDataFrame(componentes, crs=CRS_METRICO)
    gdf["area_km2"] = (gdf.geometry.area / 1e6).round(4)
    gdf.to_crs(CRS_GEO).to_file(CAPAS / "componentes_editoriales_v2.geojson", driver="GeoJSON")


def escribir_csv(path: Path, filas: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)


def comunas_por_nucleo(nucleos: dict) -> list[dict]:
    """D-6: cruce sobre el NUCLEO (pre-buffer), nunca sobre la envolvente."""
    com = leer_capa("comunas")
    filas = []
    for ref in REFS:
        nucleo = nucleos[ref["id"]]
        hit = com[com.intersects(nucleo)]
        nombres = sorted({f"Comuna {int(float(c))}" for c in hit["comuna"]})
        filas.append({
            "referencia_id": ref["id"],
            "nombre": ref["nombre"],
            "comunas_nucleo": " / ".join(nombres) if nombres else "sin interseccion",
            "cantidad": len(nombres),
            "nota": "ubicacion aproximada sobre el nucleo pre-buffer; no es cobertura",
        })
    return filas


def main() -> int:
    QA.mkdir(parents=True, exist_ok=True)

    faltan = [k for k, p in SRC.items() if not p.exists()]
    if faltan:
        raise RuntimeError(f"Faltan fuentes: {faltan}")

    fuentes = {
        "f24": cargar_fase24(),
        "p1": puntos_tanda1(),
        "p2": puntos_tanda2(),
        "ga": leer_capa("grupo_a"),
        "gb": leer_capa("grupo_b"),
        "gc": leer_capa("grupo_c"),
        "r20": leer_capa("r20_producto"),
        "t2a": leer_capa("t2_areas"),
        "sub1": leer_capa("t1_subunidades"),
        "barrios": leer_capa("barrios"),
    }

    nucleos, envolventes, trazas, componentes = construir(fuentes)
    recortadas, _ = recorte_voronoi(nucleos, envolventes)
    separadas = separar_costuras(recortadas)
    finales, reporte_astillas = limpiar_astillas(separadas)
    finales, agua_r04 = sustraer_agua_r04(finales, trazas)

    componentes = recortar_componentes(componentes, finales, {"PARTE_DECLARADA_FASE24"})

    env_gdf = escribir_capas(finales, nucleos, trazas)
    escribir_componentes(componentes)
    escribir_csv(QA / "QA_SOLAPES_22.csv", qa_solapes(envolventes, finales))
    escribir_csv(QA / "QA_ASTILLAS_RECORTE.csv", reporte_astillas)
    escribir_csv(QA / "QA_SUSTRACCION_AGUA_R04.csv",
                 [{"metrica": k, "valor": v} for k, v in agua_r04.items()])
    escribir_csv(QA / "TRAZABILIDAD_GEOMETRIAS_B2.csv", trazas)
    escribir_csv(QA / "COMUNAS_POR_NUCLEO.csv", comunas_por_nucleo(nucleos))
    escribir_csv(QA / "FUENTES_B2_SHA256.csv", [
        {"clave": k, "ruta": rel(p), "bytes": p.stat().st_size, "sha256": sha256(p)}
        for k, p in SRC.items()
    ])

    resumen = {
        "referencias": len(finales),
        "buffer_default_m": 200,
        "gap_costura_m": GAP_M * 2,
        "registros": {
            r: sum(1 for t in trazas if t["registro"] == r)
            for r in ("observado", "editorial", "declarado")
        },
        "area_total_km2": round(sum(g.area for g in finales.values()) / 1e6, 3),
    }
    (QA / "RESUMEN_B2.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    for _, r in env_gdf.sort_values("referencia_id").iterrows():
        print(f"  {r.referencia_id}  {r.nombre[:30]:32} {r.registro:10} "
              f"piezas={r.piezas:2}  {r.area_km2:7.3f} km2  {r.soporte}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
