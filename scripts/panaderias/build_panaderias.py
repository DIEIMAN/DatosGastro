"""Padron analitico de panaderias en CABA.

Alcance decidido por Diego el 2026-08-27: nucleo (elaboracion o despacho de pan) mas
punto de coccion (masa ya elaborada / masas y pasteleria). Confiteria, despacho de masas
sin elaboracion, pizza/empanadas, galletitas y churros quedan FUERA, pero trazados en C
con etiqueta propia para poder recuperarlos si la decision cambia.

Fuentes locales/publicas del proyecto: F02 (habilitaciones AGC raw, todos los anios),
F01 (oferta gastronomica raw), geo_cache/dim_ubicacion (geocodificacion ya existente),
geo_comunas/geo_barrios (geometrias oficiales). NO usa Drive, ni fuentes internas, ni
scraping, ni APIs pagas.

Recordatorio: F02 son HABILITACIONES/registros administrativos, no "locales activos".

Salidas en outputs/panaderias/.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))
from panaderias_patterns import classify, norm  # noqa: E402
from scripts.shared.fuentes_locales import iter_f01, iter_f02  # noqa: E402
from scripts.shared.fuentes_locales.geo import cargar_cache  # noqa: E402

RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUT = ROOT / "outputs" / "panaderias"
FIG = OUT / "figuras"

F01 = RAW / "f01_oferta_establecimientos_gastronomicos.csv"
GEO_COMUNAS = RAW / "geo_comunas.geojson"
GEO_BARRIOS = RAW / "geo_barrios.geojson"
GEO_CACHE = PROC / "geo_cache.csv"
DIM_UBIC = PROC / "dim_ubicacion.csv"
DIM_TERR = PROC / "dim_territorio.csv"

TRACE_COLS = [
    "fuente", "archivo_origen", "id_registro_original", "clave_habilitacion",
    "nombre_original", "rubro_original",
    "descripcion_original", "patron_detectado", "categoria_panaderia", "confianza_categoria",
    "motivo_categoria", "direccion_original", "comuna_original", "barrio_original",
    "lat", "lon", "calidad_geo", "fecha_habilitacion", "observaciones",
]
# Patrones que, aun siendo A, conviene mirar a mano: la industrial puede no atender publico.
REVISAR_AUNQUE_A = {"elaboracion_industrial_panaderia", "panificadora", "fabrica_de_pan"}


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def to_float(value: str):
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return None


# --------------------------------------------------------------------------------------
# Candidatos F02 y F01
#
# La lectura de los archivos crudos vive en scripts/shared/fuentes_locales: alli se
# resuelven de una vez el delimitador, la codificacion y los nombres de columna, que
# cambian archivo por archivo. Antes cada estudio de rubro tenia su propio lector y el
# heredado entendia un solo esquema, con lo que siete de los ocho archivos F02 aportaban
# cero filas. El modulo compartido tampoco expone titulares, cuits ni telefonos
# (guardrail 7), asi que las filas legacy siguen viniendo sin nombre de establecimiento.
# --------------------------------------------------------------------------------------
def extract_f02() -> list[dict]:
    cands = []
    for reg in iter_f02():
        c = classify(reg.rubro_completo, reg.nombre, reg.descripcion)
        if c["nivel"] == "C" and c["patron_detectado"] == "":
            continue  # ninguna senial de pan ni rubro limitrofe: no es candidato
        if reg.esquema == "moderno":
            obs = ("esquema=moderno; archivo=" + reg.periodo
                   + "; disposicion=" + reg.disposicion.strip()[:24])
        else:
            obs = ("esquema=legacy; archivo=" + reg.periodo
                   + "; sin nombre: titulares no se leen (dato personal)")
        cands.append({
            "fuente": "F02",
            "archivo_origen": reg.archivo_origen,
            "id_registro_original": reg.id_registro,
            "clave_habilitacion": reg.clave_habilitacion,
            "nombre_original": reg.nombre,
            "rubro_original": reg.rubro_completo,
            "descripcion_original": reg.descripcion[:200],
            "patron_detectado": c["patron_detectado"],
            "categoria_panaderia": c["categoria_panaderia"],
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
            "clave_habilitacion": "",  # F01 no es un registro de habilitacion
            "nombre_original": reg.nombre,
            "rubro_original": reg.rubro_completo,
            "descripcion_original": reg.ambientacion[:200],
            "patron_detectado": c["patron_detectado"],
            "categoria_panaderia": c["categoria_panaderia"],
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
# Geocodificacion desde cache local (sin servicios externos)
# --------------------------------------------------------------------------------------
def load_geocache() -> dict:
    """Cache del pipeline (solo lectura) mas la cache compartida de los estudios de rubro.

    La segunda se llena con `python -m scripts.shared.fuentes_locales.geo` y vive fuera de
    data/processed, que es superficie protegida.
    """
    return cargar_cache()


def geocode(cands: list[dict], lookup: dict) -> None:
    for c in cands:
        if c["lat"]:
            continue
        hit = lookup.get(norm(c["direccion_original"]))
        if hit:
            c["lat"], c["lon"], c["calidad_geo"] = hit[0], hit[1], "cache_" + str(hit[2])
        else:
            c["calidad_geo"] = "sin_geo"


# --------------------------------------------------------------------------------------
# Dedup -> maestro
# --------------------------------------------------------------------------------------
def street_base(direccion: str) -> str:
    """Calle sin altura: Larrazabal 3543 -> larrazabal. Une variantes de altura/esquina."""
    n = norm(direccion)
    n = re.sub(r"\b\d+\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def establecimiento_key(c: dict) -> str:
    """Clave de establecimiento, en orden de preferencia.

    F02 esta desnormalizado: un mismo local aparece decenas o cientos de veces (una fila
    por rubro x domicilio x tramite). Lo que hay que agrupar es el LOCAL.

      1. solicitud + unidad funcional. Una solicitud es una habilitacion, que es lo mas
         cerca de un local que publica la fuente. Se usa tal cual, sin sumarle el
         archivo: 379 solicitudes aparecen en dos archivos distintos porque los anios se
         solapan, y las 379 traen el mismo domicilio, o sea que son la misma habilitacion
         publicada dos veces. Agrupar por solicitud las une, que es lo correcto.
      2. partida matriz + nombre. Para el archivo moderno (2025), que no publica la
         solicitud pero si la razon social. La partida sola identifica el INMUEBLE, y el
         51 % de los inmuebles del universo aloja mas de una habilitacion: sin el nombre,
         los locales distintos de un mismo edificio se fusionan.
      3. nombre + calle sin altura, y en ultimo lugar el domicilio completo. Las filas
         legacy no tienen nombre (el titular no se lee, guardrail 7), asi que ahi se
         conserva la altura para no fusionar toda una calle en un solo establecimiento.

    El cambio de (2) a (1) como clave principal recupera los locales que la partida
    fusionaba. Contrapartida conocida: dos habilitaciones sucesivas del mismo local
    (renovacion, cambio de titular) son dos solicitudes y pasan a contarse dos veces; se
    mide aparte en `d9_renovaciones_candidatas.csv`.
    """
    habilitacion = str(c.get("clave_habilitacion", "")).strip()
    if habilitacion:
        return "H:" + habilitacion
    partida = str(c.get("id_registro_original", "")).strip()
    nombre = norm(c["nombre_original"])
    if partida:
        return "P:" + partida + "|" + nombre
    if nombre:
        return "N:" + nombre + "|" + street_base(c["direccion_original"])
    return "D:" + norm(c["direccion_original"])


def fusionar_entre_esquemas(groups: dict) -> dict:
    """Une el mismo tramite cuando aparece en el archivo legacy y en el moderno.

    El padron 2025 vuelve a publicar habilitaciones viejas: sobre el universo A hay 59
    casos con la misma partida, el mismo domicilio, el mismo anio y el mismo patron de
    rubro en los dos archivos. Como el legacy se identifica por `solicitud` y el moderno
    por `disposicion`, las claves viven en espacios distintos y el mismo local se cuenta
    dos veces.

    La regla une solo lo inequivoco: una tripla (partida, domicilio, anio) que del lado
    legacy tenga exactamente un grupo y del lado moderno exactamente uno. Si de un lado
    hay dos, no se sabe cual va con cual y se dejan separados; el caso queda visible en
    `d9_renovaciones_candidatas.csv`, que es lista para mirar a ojo.
    """
    def esquema(items): return items[0].get("_esquema", "")

    # Las triplas se arman sobre TODAS las filas del grupo, no sobre la primera: una
    # habilitacion en ochava trae dos domicilios y cada archivo los lista en otro orden.
    triples = defaultdict(lambda: defaultdict(set))
    for key, items in groups.items():
        esq = esquema(items)
        if esq not in ("legacy", "moderno"):
            continue
        for c in items:
            partida = str(c.get("id_registro_original", "")).strip()
            domicilio = norm(c["direccion_original"])
            anio = str(c.get("_anio", ""))
            if partida and domicilio and anio:
                triples[(partida, domicilio, anio)][esq].add(key)

    fusionados = dict(groups)
    for (_, _, _), lados in triples.items():
        if len(lados.get("legacy", ())) != 1 or len(lados.get("moderno", ())) != 1:
            continue
        destino, origen = next(iter(lados["legacy"])), next(iter(lados["moderno"]))
        if destino == origen or origen not in fusionados:
            continue
        fusionados[destino] = fusionados[destino] + fusionados.pop(origen)
    return fusionados


def dedup(cands_ab: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for c in cands_ab:
        groups[establecimiento_key(c)].append(c)
    groups = fusionar_entre_esquemas(groups)

    maestro = []
    for gid, (key, items) in enumerate(groups.items(), 1):
        items.sort(key=lambda c: (c["_nivel"] != "A", not bool(c["lat"]),
                                  -float(c["confianza_categoria"] or 0)))
        rep = dict(items[0])
        # El representante se elige por nivel, geo y confianza, y puede ser una fila legacy,
        # que no trae nombre ni comuna declarada. Si otra fila del grupo -tipicamente la
        # del padron 2025, que si publica la razon social- tiene el campo, se completa: son
        # el mismo tramite, y perder el nombre al fusionar seria perder lo unico que la
        # fuente publica sobre la identidad del local.
        for campo in ("nombre_original", "comuna_original", "barrio_original",
                      "descripcion_original", "fecha_habilitacion"):
            if not str(rep.get(campo, "")).strip():
                for c in items[1:]:
                    if str(c.get(campo, "")).strip():
                        rep[campo] = c[campo]
                        break
        fuentes = sorted({c["fuente"] for c in items})
        rep["fuentes_que_lo_detectan"] = ",".join(fuentes)
        rep["cantidad_fuentes"] = len(fuentes)
        rep["es_duplicado_probable"] = "si" if len(items) > 1 else "no"
        rep["grupo_duplicado"] = "G%04d" % gid
        rep["confianza_match"] = "alta" if len(fuentes) > 1 else ("media" if len(items) > 1 else "unica")
        rev = (rep["_nivel"] == "B") or (rep["patron_detectado"] in REVISAR_AUNQUE_A) or (not rep["lat"])
        rep["requiere_revision_manual"] = "si" if rev else "no"
        rep["registros_agrupados"] = len(items)
        maestro.append(rep)
    return maestro


# --------------------------------------------------------------------------------------
# Comuna / barrio / densidad
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


def build_territorial_tables(universo: list[dict], comunas, barrios):
    area_com = {int(r.comuna): r.area_km2 for r in comunas.itertuples()}
    area_bar = {str(r.nombre): r.area_km2 for r in barrios.itertuples()}
    comuna_de_barrio = {str(r.nombre): int(r.comuna) for r in barrios.itertuples()}

    cnt_com, cnt_com_geo, cnt_bar = Counter(), Counter(), Counter()
    for c in universo:
        ce = c.get("comuna_efectiva", "")
        if ce:
            cnt_com[ce] += 1
            if c["lat"]:
                cnt_com_geo[ce] += 1
        be = c.get("barrio_efectivo", "")
        if be and c["lat"]:
            cnt_bar[be] += 1

    por_comuna = []
    for cm in sorted(area_com):
        n = cnt_com.get(str(cm), 0)
        a = area_com[cm]
        por_comuna.append({
            "comuna": cm, "cantidad": n, "cantidad_geolocalizada": cnt_com_geo.get(str(cm), 0),
            "area_km2": round(a, 3), "densidad_por_km2": round(n / a, 4) if a else "",
            "panaderias_por_10000_hab": "",  # poblacion no disponible localmente
        })
    por_barrio = []
    for bn in sorted(area_bar):
        n = cnt_bar.get(bn, 0)
        a = area_bar[bn]
        por_barrio.append({
            "barrio": bn, "comuna": comuna_de_barrio.get(bn, ""), "cantidad": n,
            "area_km2": round(a, 3), "densidad_por_km2": round(n / a, 4) if a else "",
            "panaderias_por_10000_hab": "",
        })
    return por_comuna, por_barrio


# --------------------------------------------------------------------------------------
# Figuras
# --------------------------------------------------------------------------------------
def make_figures(universo_A, universo_B, comunas, por_comuna, por_barrio):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)

    geo_a = [c for c in universo_A if c["lat"] and c["lon"]]
    geo_b = [c for c in universo_B if c["lat"] and c["lon"]]
    fig, ax = plt.subplots(figsize=(8, 9))
    comunas.boundary.plot(ax=ax, color="#888", linewidth=0.6)
    if geo_b:
        ax.scatter([float(c["lon"]) for c in geo_b], [float(c["lat"]) for c in geo_b],
                   s=14, color="#f0a04b", alpha=0.65, edgecolor="white", linewidth=0.2,
                   label="B punto de coccion (n=%d)" % len(geo_b))
    if geo_a:
        ax.scatter([float(c["lon"]) for c in geo_a], [float(c["lat"]) for c in geo_a],
                   s=20, color="#8c3d1e", alpha=0.85, edgecolor="white", linewidth=0.3,
                   label="A nucleo (n=%d)" % len(geo_a))
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    ax.set_title("Panaderias geolocalizadas - CABA (habilitaciones AGC, no locales activos)")
    ax.set_axis_off()
    fig.tight_layout(); fig.savefig(FIG / "mapa_nodos_panaderias.png", dpi=140); plt.close(fig)

    pc = sorted([r for r in por_comuna if r["cantidad"] > 0], key=lambda r: r["cantidad"])
    if pc:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(["Comuna %s" % r["comuna"] for r in pc], [r["cantidad"] for r in pc], color="#2c7fb8")
        ax.set_title("Panaderias por comuna (universo A)"); ax.set_xlabel("cantidad")
        fig.tight_layout(); fig.savefig(FIG / "ranking_por_comuna.png", dpi=140); plt.close(fig)

    dc = sorted([r for r in por_comuna if r["densidad_por_km2"] not in ("", 0)],
                key=lambda r: r["densidad_por_km2"])
    if dc:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(["Comuna %s" % r["comuna"] for r in dc], [r["densidad_por_km2"] for r in dc],
                color="#31a354")
        ax.set_title("Densidad por km2 por comuna (universo A)"); ax.set_xlabel("panaderias/km2")
        fig.tight_layout(); fig.savefig(FIG / "densidad_por_comuna.png", dpi=140); plt.close(fig)

    pb = sorted([r for r in por_barrio if r["cantidad"] > 0], key=lambda r: r["cantidad"])[-15:]
    if pb:
        fig, ax = plt.subplots(figsize=(8, 7))
        ax.barh([r["barrio"] for r in pb], [r["cantidad"] for r in pb], color="#756bb1")
        ax.set_title("Panaderias por barrio (A, top 15 geolocalizados)"); ax.set_xlabel("cantidad")
        fig.tight_layout(); fig.savefig(FIG / "ranking_por_barrio.png", dpi=140); plt.close(fig)

    db = sorted([r for r in por_barrio if r["densidad_por_km2"] not in ("", 0)],
                key=lambda r: r["densidad_por_km2"])[-15:]
    if db:
        fig, ax = plt.subplots(figsize=(8, 7))
        ax.barh([r["barrio"] for r in db], [r["densidad_por_km2"] for r in db], color="#dd8452")
        ax.set_title("Densidad por km2 por barrio (A, top 15 geolocalizados)")
        ax.set_xlabel("panaderias/km2")
        fig.tight_layout(); fig.savefig(FIG / "densidad_por_barrio.png", dpi=140); plt.close(fig)


def write_geojson(rows: list[dict], fname: str) -> int:
    feats = []
    for c in rows:
        if not (c["lat"] and c["lon"]):
            continue
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(c["lon"]), float(c["lat"])]},
            "properties": {k: c.get(k, "") for k in [
                "nombre_original", "fuente", "categoria_panaderia", "patron_detectado",
                "comuna_efectiva", "barrio_efectivo", "calidad_geo", "confianza_categoria",
                "nivel_universo"]},
        })
    (OUT / fname).write_text(json.dumps({"type": "FeatureCollection", "features": feats},
                                        ensure_ascii=False), encoding="utf-8")
    return len(feats)


# --------------------------------------------------------------------------------------
# Inventario de fuentes
# --------------------------------------------------------------------------------------
def inventario(f02_n, f01_n):
    rows = [
        {"fuente": "F02 habilitaciones AGC (raw, todos los anios)",
         "path": "data/raw/f02_habilitaciones_aprobadas_*.csv", "existe": "si",
         "columnas_relevantes": "descripcion_rubro/DescripcionRubro (+SubRubro), calles, partida_matriz, fecha_habilitacion (legacy 2015-2024); razon_social, rubro, domicilio, comuna, nropartidamatriz, comentarios (moderno 2025)",
         "cantidad_filas": f02_n, "utilidad": "alta (fuente principal de panaderias)",
         "observaciones": "8 archivos con dialectos distintos, leidos por scripts/shared/fuentes_locales; son habilitaciones/registros administrativos, no locales activos; titulares y cuits no se leen"},
        {"fuente": "F01 oferta gastronomica (raw)",
         "path": "data/raw/f01_oferta_establecimientos_gastronomicos.csv", "existe": "si",
         "columnas_relevantes": "nombre, categoria, cocina, lat, long, barrio, comuna",
         "cantidad_filas": f01_n,
         "utilidad": "baja (no tiene categoria panaderia; solo aporta por nombre)",
         "observaciones": "cp1252, delimitado por ;. Su categoria mas cercana es confiteria, fuera del alcance"},
        {"fuente": "geo_comunas", "path": "data/raw/geo_comunas.geojson",
         "existe": "si" if GEO_COMUNAS.exists() else "no",
         "columnas_relevantes": "comuna, area (m2), geometry", "cantidad_filas": 15,
         "utilidad": "alta (asignacion y densidad por comuna)", "observaciones": "oficial GCBA"},
        {"fuente": "geo_barrios", "path": "data/raw/geo_barrios.geojson",
         "existe": "si" if GEO_BARRIOS.exists() else "no",
         "columnas_relevantes": "nombre, comuna, area_metro, geometry", "cantidad_filas": 48,
         "utilidad": "alta (asignacion y densidad por barrio)", "observaciones": "oficial GCBA"},
        {"fuente": "geo_cache (geocodificacion existente)", "path": "data/processed/geo_cache.csv",
         "existe": "si" if GEO_CACHE.exists() else "no",
         "columnas_relevantes": "direccion_original, latitud, longitud, calidad_geo",
         "cantidad_filas": "", "utilidad": "media (lat/lon por direccion ya geocodificada)",
         "observaciones": "no geocodifica direcciones nuevas; sin servicios externos"},
        {"fuente": "dim_ubicacion", "path": "data/processed/dim_ubicacion.csv",
         "existe": "si" if DIM_UBIC.exists() else "no",
         "columnas_relevantes": "direccion_original, latitud, longitud, calidad_geo",
         "cantidad_filas": "", "utilidad": "media (lat/lon secundaria)", "observaciones": ""},
        {"fuente": "dim_territorio", "path": "data/processed/dim_territorio.csv",
         "existe": "si" if DIM_TERR.exists() else "no",
         "columnas_relevantes": "barrio, comuna, centroide", "cantidad_filas": "",
         "utilidad": "baja (mapeo barrio-comuna; sin poblacion ni area)",
         "observaciones": "no hay poblacion local -> per capita pendiente"},
    ]
    write_csv(OUT / "inventario_fuentes_usadas.csv", rows,
              ["fuente", "path", "existe", "columnas_relevantes", "cantidad_filas",
               "utilidad", "observaciones"])


def split_write(prefix: str, cands: list[dict]):
    for nivel, suf in [("A", "nucleo"), ("B", "punto_coccion_y_probables"), ("C", "fuera_de_alcance")]:
        sub = [c for c in cands if c["_nivel"] == nivel]
        write_csv(OUT / ("candidatos_" + prefix + "_" + suf + ".csv"), sub, TRACE_COLS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    f02 = extract_f02()
    f01 = extract_f01()
    inventario(f02_n=str(len(f02)) + " filas candidatas (rubro de pan o limitrofe)",
               f01_n=str(len(f01)) + " filas candidatas (rubro de pan o limitrofe)")

    split_write("f02", f02)
    split_write("f01", f01)

    lookup = load_geocache()
    geocode(f02 + f01, lookup)

    cands_ab = [c for c in (f02 + f01) if c["_nivel"] in ("A", "B")]
    maestro = dedup(cands_ab)

    comunas, barrios = territorial(maestro)
    for c in maestro:
        c["nivel_universo"] = c["_nivel"]

    maestro_cols = list(TRACE_COLS) + [
        "fuentes_que_lo_detectan", "cantidad_fuentes", "es_duplicado_probable",
        "grupo_duplicado", "confianza_match", "requiere_revision_manual", "registros_agrupados",
        "comuna_efectiva", "barrio_efectivo", "nivel_universo"]
    write_csv(OUT / "panaderias_maestro.csv", maestro, maestro_cols)

    maestro_A = [c for c in maestro if c["_nivel"] == "A"]
    maestro_B = [c for c in maestro if c["_nivel"] == "B"]

    n_geo_a = write_geojson(maestro_A, "panaderias_maestro_A.geojson")
    n_geo_ab = write_geojson(maestro, "panaderias_maestro_AB.geojson")

    # Tablas territoriales: el universo A es el que se publica; AB queda como cota superior.
    por_comuna, por_barrio = build_territorial_tables(maestro_A, comunas, barrios)
    por_comuna_ab, por_barrio_ab = build_territorial_tables(maestro, comunas, barrios)

    tcols_com = ["comuna", "cantidad", "cantidad_geolocalizada", "area_km2",
                 "densidad_por_km2", "panaderias_por_10000_hab"]
    tcols_bar = ["barrio", "comuna", "cantidad", "area_km2", "densidad_por_km2",
                 "panaderias_por_10000_hab"]
    write_csv(OUT / "panaderias_por_comuna.csv", por_comuna, tcols_com)
    write_csv(OUT / "panaderias_por_barrio.csv", por_barrio, tcols_bar)
    write_csv(OUT / "panaderias_por_comuna_AB.csv", por_comuna_ab, tcols_com)
    write_csv(OUT / "panaderias_por_barrio_AB.csv", por_barrio_ab, tcols_bar)
    write_csv(OUT / "panaderias_densidad_comuna.csv",
              sorted(por_comuna, key=lambda r: (r["densidad_por_km2"] == "",
                                                -(r["densidad_por_km2"] or 0))),
              ["comuna", "cantidad", "area_km2", "densidad_por_km2"])
    write_csv(OUT / "panaderias_densidad_barrio.csv",
              sorted([r for r in por_barrio if r["cantidad"] > 0],
                     key=lambda r: -(r["densidad_por_km2"] or 0)),
              ["barrio", "comuna", "cantidad", "area_km2", "densidad_por_km2"])

    # Habilitaciones por anio (F02), universo A y B por separado
    anio_rows = []
    for nivel, etiqueta in [("A", "nucleo"), ("B", "punto_coccion")]:
        anios, seen = Counter(), set()
        for c in [x for x in f02 if x["_nivel"] == nivel]:
            key = establecimiento_key(c) + "|" + c["_anio"]
            if key in seen or not c["_anio"]:
                continue
            seen.add(key)
            anios[c["_anio"]] += 1
        for k, v in sorted(anios.items()):
            anio_rows.append({
                "periodo_habilitacion": k, "universo": etiqueta,
                "cantidad_establecimientos": v,
                "nota": "habilitaciones AGC; NO aperturas netas ni locales activos"})
    write_csv(OUT / "panaderias_habilitaciones_por_anio.csv", anio_rows,
              ["periodo_habilitacion", "universo", "cantidad_establecimientos", "nota"])

    # Que quedo afuera y con que etiqueta (para poder recuperarlo si cambia el alcance)
    fuera = Counter((c["patron_detectado"], c["categoria_panaderia"])
                    for c in (f02 + f01) if c["_nivel"] == "C")
    write_csv(OUT / "panaderias_excluidos_por_motivo.csv",
              [{"patron_detectado": p, "categoria": cat, "filas": n,
                "nota": "fuera del alcance decidido 2026-08-27; recuperable moviendo el patron"}
               for (p, cat), n in fuera.most_common()],
              ["patron_detectado", "categoria", "filas", "nota"])

    try:
        make_figures(maestro_A, maestro_B, comunas, por_comuna, por_barrio)
        figs_ok = True
    except Exception as exc:  # noqa: BLE001
        figs_ok = False
        print("AVISO figuras:", exc)

    resumen = {
        "alcance": "nucleo (A) + punto de coccion (B); confiteria/masas sin elaboracion/pizza fuera",
        "universo_A": len(maestro_A),
        "universo_B": len(maestro_B),
        "maestro_total_AB": len(maestro),
        "geolocalizados_A": n_geo_a,
        "sin_geo_A": len(maestro_A) - n_geo_a,
        "geolocalizados_AB": n_geo_ab,
        "requieren_revision_manual": sum(1 for c in maestro if c["requiere_revision_manual"] == "si"),
        "candidatos_f02_A": len([c for c in f02 if c["_nivel"] == "A"]),
        "candidatos_f02_B": len([c for c in f02 if c["_nivel"] == "B"]),
        "candidatos_f02_C": len([c for c in f02 if c["_nivel"] == "C"]),
        "candidatos_f01_A": len([c for c in f01 if c["_nivel"] == "A"]),
        "candidatos_f01_B": len([c for c in f01 if c["_nivel"] == "B"]),
        "candidatos_f01_C": len([c for c in f01 if c["_nivel"] == "C"]),
        "figuras_generadas": figs_ok,
        "top_comuna_cantidad": sorted([r for r in por_comuna if r["cantidad"]],
                                      key=lambda r: -r["cantidad"])[:10],
        "top_barrio_cantidad": sorted([r for r in por_barrio if r["cantidad"]],
                                      key=lambda r: -r["cantidad"])[:10],
        "top_comuna_densidad": sorted([r for r in por_comuna if r["densidad_por_km2"] not in ("", 0)],
                                      key=lambda r: -r["densidad_por_km2"])[:10],
        "top_barrio_densidad": sorted([r for r in por_barrio if r["densidad_por_km2"] not in ("", 0)],
                                      key=lambda r: -r["densidad_por_km2"])[:10],
    }
    (OUT / "_resumen_build.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2),
                                             encoding="utf-8")
    print(json.dumps({k: v for k, v in resumen.items() if not k.startswith("top_")},
                     ensure_ascii=False, indent=2))
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
