"""Padrón analítico de casas/fábricas de pastas en CABA (Partes 1-7 y 10).

Fuentes locales/públicas del proyecto: F02 (habilitaciones AGC raw, todos los años), F01 (oferta
gastronómica raw), geo_cache/dim_ubicacion (geocodificación ya existente), geo_comunas/geo_barrios
(geometrías oficiales). NO usa Drive, ni fuentes internas, ni scraping, ni APIs pagas.

Recordatorio: F02 son HABILITACIONES/registros administrativos, no "locales activos".

Salidas en outputs/casas_pastas/ (ver INFORME_CASAS_PASTAS.md).
"""
from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))
from pastas_patterns import classify, norm  # noqa: E402
from scripts.shared.fuentes_locales import iter_f01, iter_f02  # noqa: E402
from scripts.shared.fuentes_locales.geo import cargar_cache  # noqa: E402

RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUT = ROOT / "outputs" / "casas_pastas"
FIG = OUT / "figuras"

F01 = RAW / "f01_oferta_establecimientos_gastronomicos.csv"
GEO_COMUNAS = RAW / "geo_comunas.geojson"
GEO_BARRIOS = RAW / "geo_barrios.geojson"
GEO_CACHE = PROC / "geo_cache.csv"
DIM_UBIC = PROC / "dim_ubicacion.csv"
DIM_TERR = PROC / "dim_territorio.csv"

TRACE_COLS = [
    "fuente", "archivo_origen", "id_registro_original", "nombre_original", "rubro_original",
    "descripcion_original", "patron_detectado", "categoria_pastas", "confianza_categoria",
    "motivo_categoria", "direccion_original", "comuna_original", "barrio_original",
    "lat", "lon", "calidad_geo", "fecha_habilitacion", "observaciones",
]
PRODUCT_PATTERNS = {"ravioles", "sorrentinos", "noquis", "fideos_frescos", "tallarines_frescos"}


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def to_float(value: str):
    try:
        v = float(str(value).replace(",", "."))
        return v
    except (ValueError, TypeError):
        return None


# --------------------------------------------------------------------------------------
# Parte 2 y 3 — candidatos F02 y F01
#
# La lectura de los archivos crudos vive en scripts/shared/fuentes_locales. El lector
# anterior abría los ocho archivos F02 con delimitador coma y utf-8: los siete archivos
# 2015-2024 usan ";" y caían como una sola columna, de modo que este estudio venía
# midiendo únicamente el archivo 2025. El módulo compartido detecta delimitador,
# codificación y nombres de columna por archivo, y no expone titulares, cuits ni
# teléfonos (guardrail 7): las filas legacy vienen sin nombre de establecimiento.
# --------------------------------------------------------------------------------------
def extract_f02() -> list[dict]:
    cands = []
    for reg in iter_f02():
        c = classify(reg.rubro_completo, reg.nombre, reg.descripcion)
        if c["nivel"] == "C" and c["patron_detectado"] == "":
            continue  # sin ninguna señal de pasta: no es candidato
        if reg.esquema == "moderno":
            obs = f"esquema=moderno; archivo={reg.periodo}; disposicion={reg.disposicion.strip()[:24]}"
        else:
            obs = (f"esquema=legacy; archivo={reg.periodo}; "
                   "sin nombre: titulares no se leen (dato personal)")
        cands.append({
            "fuente": "F02",
            "archivo_origen": reg.archivo_origen,
            "id_registro_original": reg.id_registro,
            "nombre_original": reg.nombre,
            "rubro_original": reg.rubro_completo,
            "descripcion_original": reg.descripcion[:200],
            "patron_detectado": c["patron_detectado"],
            "categoria_pastas": c["categoria_pastas"],
            "confianza_categoria": c["confianza_categoria"],
            "motivo_categoria": c["motivo_categoria"],
            "direccion_original": reg.domicilio,
            "comuna_original": reg.comuna,
            "barrio_original": "",
            "lat": "", "lon": "", "calidad_geo": "",
            "fecha_habilitacion": reg.anio_habilitacion,
            "observaciones": obs,
            "_nivel": c["nivel"], "_anio": reg.anio_habilitacion, "_esquema": reg.esquema,
        })
    return cands


def extract_f01() -> list[dict]:
    cands = []
    for reg in iter_f01():
        c = classify(reg.nombre, reg.categoria, reg.cocina)
        if c["nivel"] == "C" and c["patron_detectado"] == "":
            continue
        cands.append({
            "fuente": "F01",
            "archivo_origen": reg.archivo_origen,
            "id_registro_original": reg.id_registro,
            "nombre_original": reg.nombre,
            "rubro_original": reg.rubro_completo,
            "descripcion_original": reg.ambientacion[:200],
            "patron_detectado": c["patron_detectado"],
            "categoria_pastas": c["categoria_pastas"],
            "confianza_categoria": c["confianza_categoria"],
            "motivo_categoria": c["motivo_categoria"],
            "direccion_original": reg.direccion,
            "comuna_original": reg.comuna,
            "barrio_original": reg.barrio,
            "lat": reg.lat or "",
            "lon": reg.lon or "",
            "calidad_geo": "f01_fuente" if reg.lat else "sin_geo",
            "fecha_habilitacion": "",
            "observaciones": "",
            "_nivel": c["nivel"], "_anio": "",
        })
    return cands


# --------------------------------------------------------------------------------------
# Parte 5 — geocodificación desde cache local (sin servicios externos)
# --------------------------------------------------------------------------------------
def load_geocache() -> dict:
    """Cache del pipeline (solo lectura) mas la cache compartida de los estudios de rubro.

    La segunda se llena con `python -m scripts.shared.fuentes_locales.geo` y vive fuera de
    data/processed, que es superficie protegida.
    """
    return cargar_cache()


def geocode_f02(cands: list[dict], lookup: dict) -> None:
    for c in cands:
        if c["fuente"] != "F02" or c["lat"]:
            continue
        hit = lookup.get(norm(c["direccion_original"]))
        if hit:
            c["lat"], c["lon"], c["calidad_geo"] = hit[0], hit[1], f"cache_{hit[2]}"
        else:
            c["calidad_geo"] = "sin_geo"


# --------------------------------------------------------------------------------------
# Parte 4 — dedup -> maestro
# --------------------------------------------------------------------------------------
def establecimiento_key(c: dict) -> str:
    """Clave conservadora segun la naturaleza de la fuente.

    F02 es una serie de habilitaciones: la copia mal rotulada como 2025 reedita parte de
    2015-2020 y agrega razon social. Para no contarla como otro establecimiento, F02 se
    agrupa por partida + domicilio exacto y el nombre queda como enriquecimiento. F01 se
    agrupa por nombre + domicilio. En ningun caso se quita la altura: puertas cercanas o
    alternativas quedan para revision, no se fusionan automaticamente.
    """
    nombre = norm(c["nombre_original"])
    domicilio = norm(c["direccion_original"])
    identificador = norm(c.get("id_registro_original", ""))
    if c.get("fuente") == "F02" and domicilio:
        return "f02|" + identificador + "|" + domicilio
    if domicilio:
        return c.get("fuente", "") + "|" + nombre + "|" + domicilio
    # Sin domicilio, solo se agrupan repeticiones del mismo registro fuente. Si tampoco
    # hay identificador, se conserva el rubro para no colapsar filas no contrastables.
    return "sin_domicilio|" + "|".join([
        c.get("fuente", ""), identificador, nombre,
        norm(c.get("rubro_original", "")),
    ])


def dedup(cands_ab: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for c in cands_ab:
        groups[establecimiento_key(c)].append(c)

    maestro = []
    for gid, (key, items) in enumerate(groups.items(), 1):
        # Preferir nivel A, luego el registro que aporta nombre, geo y mayor confianza.
        items.sort(key=lambda c: (c["_nivel"] != "A", not bool(c["nombre_original"]),
                                  not bool(c["lat"]), -float(c["confianza_categoria"] or 0)))
        rep = dict(items[0])
        # La reedicion historica puede aportar nombre donde el legacy aporta geometria.
        # Se completa cada campo sin sumar una fuente independiente ni una fila.
        if not rep["nombre_original"]:
            rep["nombre_original"] = next((c["nombre_original"] for c in items
                                             if c["nombre_original"]), "")
        if not rep["lat"]:
            geo = next((c for c in items if c["lat"] and c["lon"]), None)
            if geo:
                rep["lat"], rep["lon"], rep["calidad_geo"] = (
                    geo["lat"], geo["lon"], geo["calidad_geo"])
        fuentes = sorted({c["fuente"] for c in items})
        rep["fuentes_que_lo_detectan"] = ",".join(fuentes)
        rep["cantidad_fuentes"] = len(fuentes)
        rep["es_duplicado_probable"] = "si" if len(items) > 1 else "no"
        rep["grupo_duplicado"] = f"G{gid:04d}"
        rep["confianza_match"] = "alta" if len(fuentes) > 1 else ("media" if len(items) > 1 else "unica")
        rev = (rep["_nivel"] == "B") or (rep["patron_detectado"] in PRODUCT_PATTERNS) or (not rep["lat"])
        rep["requiere_revision_manual"] = "si" if rev else "no"
        rep["registros_agrupados"] = len(items)
        maestro.append(rep)
    return maestro


# --------------------------------------------------------------------------------------
# Parte 6 — comuna/barrio/densidad con geopandas
# --------------------------------------------------------------------------------------
def territorial(maestro: list[dict]):
    import geopandas as gpd
    from shapely.geometry import Point

    comunas = gpd.read_file(GEO_COMUNAS).to_crs(4326)
    barrios = gpd.read_file(GEO_BARRIOS).to_crs(4326)
    comunas["comuna"] = comunas["comuna"].astype(int)
    comunas["area_km2"] = comunas["area"] / 1e6
    barrios["area_km2"] = barrios["area_metro"] / 1e6

    geo_pts = [c for c in maestro if c["lat"] and c["lon"]]
    if geo_pts:
        gdf = gpd.GeoDataFrame(
            geo_pts, geometry=[Point(float(c["lon"]), float(c["lat"])) for c in geo_pts], crs=4326)
        j_com = gpd.sjoin(gdf, comunas[["comuna", "geometry"]], how="left", predicate="within")
        j_bar = gpd.sjoin(gdf, barrios[["nombre", "comuna", "geometry"]], how="left", predicate="within")
        for i, c in zip(gdf.index, geo_pts):
            cm = j_com.loc[i, "comuna"] if i in j_com.index else None
            if hasattr(cm, "iloc"):
                cm = cm.iloc[0]
            c["comuna_geo"] = "" if cm is None or (isinstance(cm, float) and cm != cm) else str(int(cm))
            bn = j_bar.loc[i, "nombre"] if i in j_bar.index else None
            if hasattr(bn, "iloc"):
                bn = bn.iloc[0]
            c["barrio_geo"] = "" if bn is None or (isinstance(bn, float) and bn != bn) else str(bn)

    # comuna efectiva: geo si existe, si no comuna_original (de F01/F02)
    def comuna_efectiva(c):
        g = c.get("comuna_geo", "")
        if g:
            return g
        co = re.sub(r"[^0-9]", "", c.get("comuna_original", ""))
        return co if co else ""

    for c in maestro:
        c["comuna_efectiva"] = comuna_efectiva(c)
        c["barrio_efectivo"] = c.get("barrio_geo", "") or c.get("barrio_original", "")
    return comunas, barrios


def build_territorial_tables(maestro_A: list[dict], comunas, barrios):
    area_com = {int(r.comuna): r.area_km2 for r in comunas.itertuples()}
    area_bar = {str(r.nombre): r.area_km2 for r in barrios.itertuples()}
    comuna_de_barrio = {str(r.nombre): int(r.comuna) for r in barrios.itertuples()}

    cnt_com = Counter()
    cnt_com_geo = Counter()
    cnt_bar = Counter()
    for c in maestro_A:
        ce = c.get("comuna_efectiva", "")
        if ce:
            cnt_com[ce] += 1
            if c["lat"]:
                cnt_com_geo[ce] += 1
        be = c.get("barrio_efectivo", "")
        if be and c["lat"]:
            cnt_bar[be] += 1

    por_comuna = []
    for cm in sorted(area_com, key=lambda x: x):
        n = cnt_com.get(str(cm), 0)
        a = area_com[cm]
        por_comuna.append({
            "comuna": cm, "cantidad": n, "cantidad_geolocalizada": cnt_com_geo.get(str(cm), 0),
            "area_km2": round(a, 3), "densidad_por_km2": round(n / a, 4) if a else "",
            "casas_por_10000_hab": "",  # poblacion no disponible localmente
        })
    por_barrio = []
    for bn in sorted(area_bar):
        n = cnt_bar.get(bn, 0)
        a = area_bar[bn]
        por_barrio.append({
            "barrio": bn, "comuna": comuna_de_barrio.get(bn, ""), "cantidad": n,
            "area_km2": round(a, 3), "densidad_por_km2": round(n / a, 4) if a else "",
            "casas_por_10000_hab": "",
        })
    return por_comuna, por_barrio


# --------------------------------------------------------------------------------------
# Parte 10 — figuras
# --------------------------------------------------------------------------------------
def make_figures(maestro_A, comunas, barrios, por_comuna, por_barrio):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)

    # mapa de nodos
    geo = [c for c in maestro_A if c["lat"] and c["lon"]]
    fig, ax = plt.subplots(figsize=(8, 9))
    comunas.boundary.plot(ax=ax, color="#888", linewidth=0.6)
    if geo:
        ax.scatter([float(c["lon"]) for c in geo], [float(c["lat"]) for c in geo],
                   s=22, color="#c0392b", alpha=0.8, edgecolor="white", linewidth=0.3)
    ax.set_title(f"Casas/fábricas de pastas (A) geolocalizadas — CABA (n={len(geo)})")
    ax.set_axis_off()
    fig.tight_layout(); fig.savefig(FIG / "mapa_nodos_casas_pastas.png", dpi=140); plt.close(fig)

    # ranking comuna
    pc = sorted([r for r in por_comuna if r["cantidad"] > 0], key=lambda r: r["cantidad"])
    if pc:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh([f"Comuna {r['comuna']}" for r in pc], [r["cantidad"] for r in pc], color="#2c7fb8")
        ax.set_title("Casas/fábricas de pastas por comuna (A)"); ax.set_xlabel("cantidad")
        fig.tight_layout(); fig.savefig(FIG / "ranking_por_comuna.png", dpi=140); plt.close(fig)

    # densidad comuna
    dc = sorted([r for r in por_comuna if r["densidad_por_km2"] not in ("", 0)], key=lambda r: r["densidad_por_km2"])
    if dc:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh([f"Comuna {r['comuna']}" for r in dc], [r["densidad_por_km2"] for r in dc], color="#31a354")
        ax.set_title("Densidad por km² por comuna (A)"); ax.set_xlabel("casas/km²")
        fig.tight_layout(); fig.savefig(FIG / "densidad_por_comuna.png", dpi=140); plt.close(fig)

    # ranking barrio top 15
    pb = sorted([r for r in por_barrio if r["cantidad"] > 0], key=lambda r: r["cantidad"])[-15:]
    if pb:
        fig, ax = plt.subplots(figsize=(8, 7))
        ax.barh([r["barrio"] for r in pb], [r["cantidad"] for r in pb], color="#756bb1")
        ax.set_title("Casas/fábricas de pastas por barrio (A, top 15 geolocalizados)"); ax.set_xlabel("cantidad")
        fig.tight_layout(); fig.savefig(FIG / "ranking_por_barrio.png", dpi=140); plt.close(fig)

    # densidad barrio top 15
    db = sorted([r for r in por_barrio if r["densidad_por_km2"] not in ("", 0)], key=lambda r: r["densidad_por_km2"])[-15:]
    if db:
        fig, ax = plt.subplots(figsize=(8, 7))
        ax.barh([r["barrio"] for r in db], [r["densidad_por_km2"] for r in db], color="#dd8452")
        ax.set_title("Densidad por km² por barrio (A, top 15 geolocalizados)"); ax.set_xlabel("casas/km²")
        fig.tight_layout(); fig.savefig(FIG / "densidad_por_barrio.png", dpi=140); plt.close(fig)


def write_geojson(maestro_A: list[dict]) -> int:
    feats = []
    for c in maestro_A:
        if not (c["lat"] and c["lon"]):
            continue
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(c["lon"]), float(c["lat"])]},
            "properties": {k: c.get(k, "") for k in [
                "nombre_original", "fuente", "categoria_pastas", "patron_detectado",
                "comuna_efectiva", "barrio_efectivo", "calidad_geo", "confianza_categoria"]},
        })
    gj = {"type": "FeatureCollection", "features": feats}
    (OUT / "casas_pastas_maestro.geojson").write_text(json.dumps(gj, ensure_ascii=False), encoding="utf-8")
    return len(feats)


# --------------------------------------------------------------------------------------
# Parte 1 — inventario de fuentes
# --------------------------------------------------------------------------------------
def inventario(f02_n, f01_n):
    def cols_of(path, enc, delim=","):
        try:
            with open(path, encoding=enc, errors="replace", newline="") as fh:
                return next(csv.reader(fh, delimiter=delim))
        except Exception:
            return []
    rows = [
        {"fuente": "F02 habilitaciones AGC (raw, todos los años)", "path": "data/raw/f02_habilitaciones_aprobadas_*.csv",
         "existe": "si", "columnas_relevantes": "descripcion_rubro/DescripcionRubro (+SubRubro), calles, partida_matriz, fecha_habilitacion (legacy 2015-2024); razon_social, rubro, domicilio, comuna, nropartidamatriz, comentarios (moderno 2025)",
         "cantidad_filas": f02_n, "utilidad": "alta (fuente principal de casas/fabricas de pastas)",
         "observaciones": "8 archivos con dialectos distintos, leidos por scripts/shared/fuentes_locales; son habilitaciones/registros administrativos, no locales activos; titulares y cuits no se leen"},
        {"fuente": "F01 oferta gastronomica (raw)", "path": "data/raw/f01_oferta_establecimientos_gastronomicos.csv",
         "existe": "si", "columnas_relevantes": "nombre, categoria, cocina, lat, long, barrio, comuna",
         "cantidad_filas": f01_n, "utilidad": "baja (orientada a restaurantes; casi sin casas de pastas)",
         "observaciones": "cp1252, delimitado por ;"},
        {"fuente": "geo_comunas", "path": "data/raw/geo_comunas.geojson", "existe": "si" if GEO_COMUNAS.exists() else "no",
         "columnas_relevantes": "comuna, area (m2), geometry", "cantidad_filas": 15,
         "utilidad": "alta (asignacion y densidad por comuna)", "observaciones": "oficial GCBA"},
        {"fuente": "geo_barrios", "path": "data/raw/geo_barrios.geojson", "existe": "si" if GEO_BARRIOS.exists() else "no",
         "columnas_relevantes": "nombre, comuna, area_metro, geometry", "cantidad_filas": 48,
         "utilidad": "alta (asignacion y densidad por barrio)", "observaciones": "oficial GCBA"},
        {"fuente": "geo_cache (geocodificacion existente)", "path": "data/processed/geo_cache.csv",
         "existe": "si" if GEO_CACHE.exists() else "no", "columnas_relevantes": "direccion_original, latitud, longitud, calidad_geo",
         "cantidad_filas": "", "utilidad": "media (lat/lon por direccion ya geocodificada)",
         "observaciones": "no geocodifica direcciones nuevas; sin servicios externos"},
        {"fuente": "dim_ubicacion", "path": "data/processed/dim_ubicacion.csv",
         "existe": "si" if DIM_UBIC.exists() else "no", "columnas_relevantes": "direccion_original, latitud, longitud, calidad_geo",
         "cantidad_filas": "", "utilidad": "media (lat/lon secundaria)", "observaciones": ""},
        {"fuente": "dim_territorio", "path": "data/processed/dim_territorio.csv",
         "existe": "si" if DIM_TERR.exists() else "no", "columnas_relevantes": "barrio, comuna, centroide",
         "cantidad_filas": "", "utilidad": "baja (mapeo barrio-comuna; sin poblacion ni area)",
         "observaciones": "no hay poblacion local -> per capita pendiente"},
    ]
    write_csv(OUT / "inventario_fuentes_usadas.csv", rows,
              ["fuente", "path", "existe", "columnas_relevantes", "cantidad_filas", "utilidad", "observaciones"])


# --------------------------------------------------------------------------------------
def split_write(prefix: str, cands: list[dict]):
    for nivel, suf in [("A", "estrictos"), ("B", "probables"), ("C", "dudosos_descartados")]:
        sub = [c for c in cands if c["_nivel"] == nivel]
        write_csv(OUT / f"candidatos_{prefix}_{suf}.csv", sub, TRACE_COLS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    f02 = extract_f02()
    f01 = extract_f01()
    inventario(f02_n=f"{len(f02)} filas candidatas (con termino pasta)",
               f01_n=f"{len(f01)} filas candidatas (con termino pasta)")

    split_write("f02", f02)
    split_write("f01", f01)

    lookup = load_geocache()
    geocode_f02(f02 + f01, lookup)

    cands_ab = [c for c in (f02 + f01) if c["_nivel"] in ("A", "B")]
    maestro = dedup(cands_ab)
    maestro_cols = TRACE_COLS + [
        "_nivel", "fuentes_que_lo_detectan", "cantidad_fuentes", "es_duplicado_probable",
        "grupo_duplicado", "confianza_match", "requiere_revision_manual", "registros_agrupados"]

    comunas, barrios = territorial(maestro)
    maestro_cols += ["comuna_efectiva", "barrio_efectivo"]
    # renombrar _nivel -> nivel_universo en salida
    for c in maestro:
        c["nivel_universo"] = c["_nivel"]
    write_csv(OUT / "casas_pastas_maestro.csv", maestro,
              [col for col in maestro_cols if col != "_nivel"] + ["nivel_universo"])

    maestro_A = [c for c in maestro if c["_nivel"] == "A"]
    maestro_AB = maestro

    n_geo = write_geojson(maestro_A)

    por_comuna, por_barrio = build_territorial_tables(maestro_A, comunas, barrios)
    write_csv(OUT / "casas_pastas_por_comuna.csv", por_comuna,
              ["comuna", "cantidad", "cantidad_geolocalizada", "area_km2", "densidad_por_km2", "casas_por_10000_hab"])
    write_csv(OUT / "casas_pastas_por_barrio.csv", por_barrio,
              ["barrio", "comuna", "cantidad", "area_km2", "densidad_por_km2", "casas_por_10000_hab"])
    write_csv(OUT / "casas_pastas_densidad_comuna.csv",
              sorted(por_comuna, key=lambda r: (r["densidad_por_km2"] == "", -(r["densidad_por_km2"] or 0))),
              ["comuna", "cantidad", "area_km2", "densidad_por_km2"])
    write_csv(OUT / "casas_pastas_densidad_barrio.csv",
              sorted([r for r in por_barrio if r["cantidad"] > 0], key=lambda r: -(r["densidad_por_km2"] or 0)),
              ["barrio", "comuna", "cantidad", "area_km2", "densidad_por_km2"])

    # Parte 7 — habilitaciones por año (F02), universo A
    anios = Counter()
    seen = set()
    for c in [x for x in f02 if x["_nivel"] == "A"]:
        key = establecimiento_key(c) + "|" + c["_anio"]
        if key in seen:
            continue
        seen.add(key)
        if c["_anio"]:
            anios[c["_anio"]] += 1
    anio_rows = [{"periodo_habilitacion": k, "cantidad_establecimientos_pastas": v,
                  "nota": "habilitaciones AGC vinculadas a casas/fabricas de pastas (A); NO aperturas netas ni locales activos"}
                 for k, v in sorted(anios.items())]
    write_csv(OUT / "casas_pastas_habilitaciones_por_anio.csv", anio_rows,
              ["periodo_habilitacion", "cantidad_establecimientos_pastas", "nota"])

    try:
        make_figures(maestro_A, comunas, barrios, por_comuna, por_barrio)
        figs_ok = True
    except Exception as exc:  # noqa: BLE001
        figs_ok = False
        print("AVISO figuras:", exc)

    # resumen a stdout + json para el informe
    resumen = {
        "universo_A": len(maestro_A),
        "universo_B": len([c for c in maestro_AB if c["_nivel"] == "B"]),
        "maestro_total_AB": len(maestro_AB),
        "geolocalizados_A": n_geo,
        "sin_geo_A": len(maestro_A) - n_geo,
        "candidatos_f02_A": len([c for c in f02 if c["_nivel"] == "A"]),
        "candidatos_f02_B": len([c for c in f02 if c["_nivel"] == "B"]),
        "candidatos_f02_C": len([c for c in f02 if c["_nivel"] == "C"]),
        "candidatos_f01_A": len([c for c in f01 if c["_nivel"] == "A"]),
        "candidatos_f01_B": len([c for c in f01 if c["_nivel"] == "B"]),
        "candidatos_f01_C": len([c for c in f01 if c["_nivel"] == "C"]),
        "figuras_generadas": figs_ok,
        "top_comuna_cantidad": sorted([r for r in por_comuna if r["cantidad"]], key=lambda r: -r["cantidad"])[:10],
        "top_barrio_cantidad": sorted([r for r in por_barrio if r["cantidad"]], key=lambda r: -r["cantidad"])[:10],
        "top_comuna_densidad": sorted([r for r in por_comuna if r["densidad_por_km2"] not in ("", 0)], key=lambda r: -r["densidad_por_km2"])[:10],
        "top_barrio_densidad": sorted([r for r in por_barrio if r["densidad_por_km2"] not in ("", 0)], key=lambda r: -r["densidad_por_km2"])[:10],
    }
    (OUT / "_resumen_build.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in resumen.items() if not k.startswith("top_")}, ensure_ascii=False, indent=2))
    print("TOP comuna (cant):", [(r["comuna"], r["cantidad"]) for r in resumen["top_comuna_cantidad"]])
    print("TOP barrio (cant):", [(r["barrio"], r["cantidad"]) for r in resumen["top_barrio_cantidad"]])
    print("TOP comuna (dens):", [(r["comuna"], r["densidad_por_km2"]) for r in resumen["top_comuna_densidad"]])


def _cli_out(argv=None):
    """--out DIR redirige TODA la salida a otra carpeta.

    Sirve para correr el build sin pisar entregables ya publicados: se produce en una
    carpeta aparte y se comparan los numeros antes de decidir si se regenera lo oficial.
    """
    import argparse
    global OUT, FIG
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None, help="carpeta de salida (por defecto, la del proyecto)")
    args = ap.parse_args(argv)
    if args.out:
        OUT = Path(args.out).resolve()
        FIG = OUT / "figuras"


if __name__ == "__main__":
    _cli_out()
    main()
