"""Construye el PADRÓN CANDIDATO INTEGRADO de casas/fábricas/locales de venta de pastas
en CABA, cruzando tres fuentes SIN hacer requests:

  1. AGC / F02  -> registro administrativo oficial estricto (NO implica local activo).
  2. OpenStreetMap -> relevamiento abierto auxiliar (no oficial).
  3. Google Places API -> padrón candidato operativo no oficial.

Regla central: NO filtrar solo por cadenas. Se preservan explícitamente locales
independientes y casas de barrio. Cadenas y casas chicas son parte del mismo universo.

Salidas en outputs/casas_pastas_integrado/. El padrón con nombres/direcciones es
SENSIBLE (datos de terceros / razón social AGC) -> carpeta gitignored.
NO genera PDF. NO commitea. NO toca el pipeline principal.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import math
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from shapely.geometry import Point, shape
from shapely.strtree import STRtree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_places_clasificador import MARCAS_ESPERADAS, norm_nombre, strip_acc  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GP = ROOT / "outputs" / "casas_pastas_google_places"
CP = ROOT / "outputs" / "casas_pastas"            # crudo AGC/OSM (gitignored)
GEO = ROOT / "data" / "raw"
OUT = ROOT / "outputs" / "casas_pastas_integrado"

GOOGLE_DEDUP = GP / "google_places_consolidado_plus_deduplicado.csv"
GOOGLE_CALIDAD = GP / "google_places_consolidado_plus_calidad_queries.csv"
GOOGLE_C_SIGNAL = GP / "revision_cobertura_google" / "revision_C_con_senal_pastas.csv"
OSM = CP / "osm_casas_pastas_candidatos.csv"
AGC = CP / "casas_pastas_maestro.csv"


def haversine_m(lat1, lon1, lat2, lon2) -> float:
    try:
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    except (TypeError, ValueError):
        return 1e9
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---------------- Geometría: asignación de comuna/barrio ----------------
def cargar_geo():
    gc = json.load((GEO / "geo_comunas.geojson").open(encoding="utf-8"))
    gb = json.load((GEO / "geo_barrios.geojson").open(encoding="utf-8"))
    com_geoms, com_meta = [], []
    for f in gc["features"]:
        com_geoms.append(shape(f["geometry"]))
        com_meta.append({"comuna": str(f["properties"]["comuna"]),
                         "area_km2": round(f["properties"]["area"] / 1e6, 4)})
    bar_geoms, bar_meta = [], []
    for f in gb["features"]:
        bar_geoms.append(shape(f["geometry"]))
        bar_meta.append({"barrio": f["properties"]["nombre"].title(),
                         "comuna": str(f["properties"]["comuna"]),
                         "area_km2": round(f["properties"]["area_metro"] / 1e6, 4)})
    return (STRtree(com_geoms), com_geoms, com_meta,
            STRtree(bar_geoms), bar_geoms, bar_meta)


def asignar(tree, geoms, meta, lat, lon):
    la, lo = fnum(lat), fnum(lon)
    if la is None or lo is None:
        return None
    pt = Point(lo, la)
    for idx in tree.query(pt):
        if geoms[idx].contains(pt):
            return meta[idx]
    return None


# ---------------- Carga de fuentes a registros comunes ----------------
def cargar_google():
    c_signal = set()
    if GOOGLE_C_SIGNAL.exists():
        for r in csv.DictReader(GOOGLE_C_SIGNAL.open(encoding="utf-8-sig")):
            if r.get("decision_revision") == "posible_faltante_buscar":
                c_signal.add(r["place_id"])
    regs = []
    for r in csv.DictReader(GOOGLE_DEDUP.open(encoding="utf-8-sig")):
        cls = r["match_casas_pastas"]
        if cls.startswith("A_"):
            capa = "Google_A_probable"
        elif cls.startswith("B_"):
            capa = "Google_B_revision"
        elif r["place_id"] in c_signal:
            capa = "Google_C_posible_faltante"
        else:
            capa = "Google_C_descartado"
        regs.append({
            "fuente": "google", "id_origen": r["place_id"], "nombre": r["nombre"],
            "direccion": r["direccion"], "lat": r["lat"], "lon": r["lon"],
            "tipo_google": r.get("types", ""), "capa_origen": capa,
            "es_A": capa == "Google_A_probable",
            "es_B": capa in ("Google_B_revision", "Google_C_posible_faltante"),
            "queries": r.get("queries_detectado", ""),
        })
    return regs


def cargar_osm():
    regs = []
    for r in csv.DictReader(OSM.open(encoding="utf-8-sig")):
        niv = (r.get("nivel_universo") or "").upper()
        if niv == "A":
            capa, esA, esB = "OSM_A_auxiliar", True, False
        elif niv == "B":
            capa, esA, esB = "OSM_B_revision", False, True
        else:
            capa, esA, esB = "OSM_C_descartado", False, False
        regs.append({
            "fuente": "osm", "id_origen": f"{r.get('osm_type','')}/{r.get('osm_id','')}",
            "nombre": r.get("nombre_original", ""), "direccion": r.get("addr", ""),
            "lat": r.get("lat", ""), "lon": r.get("lon", ""),
            "tipo_google": "", "capa_origen": capa, "es_A": esA, "es_B": esB, "queries": "",
        })
    return regs


def cargar_agc():
    regs = []
    for r in csv.DictReader(AGC.open(encoding="utf-8-sig")):
        # AGC maestro: universo A estricto, oficial. nombre = razón social (sensible).
        regs.append({
            "fuente": "agc", "id_origen": r.get("id_registro_original", ""),
            "nombre": r.get("nombre_original", ""), "direccion": r.get("direccion_original", ""),
            "lat": r.get("lat", ""), "lon": r.get("lon", ""), "tipo_google": "",
            "capa_origen": "AGC_A_oficial_estricto", "es_A": True, "es_B": False, "queries": "",
            "comuna_pre": r.get("comuna_efectiva", ""), "barrio_pre": r.get("barrio_efectivo", ""),
        })
    return regs


# ---------------- Dedup multifuente ----------------
def es_duplicado(a, b) -> bool:
    na, nb = norm_nombre(a["nombre"]), norm_nombre(b["nombre"])
    if not na or not nb:
        return False
    d = haversine_m(a["lat"], a["lon"], b["lat"], b["lon"])
    rt = ratio(na, nb)
    if d < 40 and rt >= 0.5:
        return True
    if d < 150 and rt >= 0.8:
        return True
    if d < 250 and na == nb:
        return True
    return False


def integrar():
    regs = cargar_google() + cargar_osm() + cargar_agc()

    # Dedup: une por place_id (google) y luego cross-source por nombre+distancia.
    grupos: list[list[dict]] = []
    for r in regs:
        puesto = False
        for g in grupos:
            if any(es_duplicado(r, x) for x in g[-3:]):  # comparar con últimos del grupo
                g.append(r)
                puesto = True
                break
        if not puesto:
            grupos.append([r])

    # Segunda pasada: fusiona grupos cercanos (por si quedaron separados).
    fusion = True
    while fusion:
        fusion = False
        for i in range(len(grupos)):
            for j in range(i + 1, len(grupos)):
                if any(es_duplicado(x, y) for x in grupos[i][:4] for y in grupos[j][:4]):
                    grupos[i].extend(grupos[j])
                    grupos.pop(j)
                    fusion = True
                    break
            if fusion:
                break
    return grupos


PRIOR = {"agc": 3, "google": 2, "osm": 1}


def clasificar_grupo(g):
    fuentes = sorted({m["fuente"] for m in g}, key=lambda f: -PRIOR[f])
    a_sources = {m["fuente"] for m in g if m["es_A"]}
    b_any = any(m["es_B"] for m in g)
    n_fuentes = len(fuentes)

    if len(a_sources) >= 2:
        clase, conf = "A_integrado_multifuente", "alta"
    elif "agc" in a_sources:
        clase, conf = "A_agc_oficial_estricto", "alta"
    elif "google" in a_sources:
        clase, conf = "A_google_probable", "media-alta" if n_fuentes >= 2 else "media"
    elif "osm" in a_sources:
        clase, conf = "A_osm_auxiliar", "media"
    elif b_any:
        clase, conf = "B_revision_manual", "media-baja"
    else:
        clase, conf = "C_descartado", "baja"

    # Revisión prioritaria: B y C-posible-faltante (capa B). Los A de una sola fuente
    # quedan como candidatos operativos válidos, no como prioridad de revisión.
    rev = "si" if clase == "B_revision_manual" else "no"
    cap = sorted({m["capa_origen"] for m in g})
    motivo = f"fuentes={'+'.join(fuentes)}; capas={','.join(cap)}"
    return clase, conf, rev, fuentes, motivo


def elegir_repr(g):
    """Elige el registro 'representante' (mejor nombre/dirección) del grupo."""
    # Preferir AGC (oficial) > google (suele tener dirección formateada) > osm
    g2 = sorted(g, key=lambda m: (-PRIOR[m["fuente"]], -len(m.get("direccion", ""))))
    return g2[0]


def main() -> int:
    for p in (GOOGLE_DEDUP, OSM, AGC):
        if not p.exists():
            print(f"ABORTADO: falta insumo {p}")
            return 2
    OUT.mkdir(parents=True, exist_ok=True)
    com_tree, com_g, com_m, bar_tree, bar_g, bar_m = cargar_geo()

    grupos = integrar()
    print(f"Registros totales (3 fuentes): {sum(len(g) for g in grupos)} -> grupos únicos: {len(grupos)}")

    # Construir filas del padrón.
    filas = []
    for g in grupos:
        clase, conf, rev, fuentes, motivo = clasificar_grupo(g)
        rep = elegir_repr(g)
        lat, lon = rep["lat"], rep["lon"]
        # comuna/barrio: usar AGC pre-asignado si está, si no PIP.
        comuna = barrio = area_com = area_bar = None
        agc_rec = next((m for m in g if m["fuente"] == "agc"), None)
        if agc_rec and agc_rec.get("comuna_pre"):
            comuna = agc_rec["comuna_pre"]
            barrio = agc_rec.get("barrio_pre") or None
        cm = asignar(com_tree, com_g, com_m, lat, lon)
        bm = asignar(bar_tree, bar_g, bar_m, lat, lon)
        if cm and not comuna:
            comuna = cm["comuna"]
        if bm and not barrio:
            barrio = bm["barrio"]
        area_com = cm["area_km2"] if cm else None
        area_bar = bm["area_km2"] if bm else None

        queries = ";".join(sorted({q for m in g for q in m.get("queries", "").split(";") if q}))
        filas.append({
            "id_integrado": "",  # se asigna abajo
            "nombre": rep["nombre"], "direccion": rep["direccion"],
            "lat": lat, "lon": lon, "comuna": comuna or "", "barrio": barrio or "",
            "clase_integrada": clase, "confianza_integrada": conf,
            "fuentes_detectan": "+".join(fuentes), "cantidad_fuentes": len(fuentes),
            "fuente_principal": fuentes[0], "requiere_revision_manual": rev,
            "motivo_clasificacion": motivo, "tipo_establecimiento_google": rep.get("tipo_google", ""),
            "queries_detectado": queries,
            "_area_com": area_com, "_area_bar": area_bar,
            "_norm": norm_nombre(rep["nombre"]),
        })

    # ----- Cadenas vs independientes -----
    # clave de cadena: marca conocida canónica, si no, nombre normalizado exacto.
    def marca_de(nrm):
        for marca, claves in MARCAS_ESPERADAS.items():
            if any(k in nrm for k in claves):
                return marca
        return None

    cand = [f for f in filas if f["clase_integrada"] != "C_descartado"]
    cadena_key = {}
    for f in cand:
        mk = marca_de(f["_norm"])
        cadena_key[id(f)] = mk if mk else f["_norm"]
    cnt_key = Counter(cadena_key[id(f)] for f in cand)
    for f in filas:
        if f["clase_integrada"] == "C_descartado":
            f["es_cadena_detectada"], f["cadena_detectada"] = "no", ""
            f["cantidad_sucursales_cadena"], f["tipo_establecimiento"] = 0, "indeterminado"
            continue
        key = cadena_key[id(f)]
        mk = marca_de(f["_norm"])
        n = cnt_key.get(key, 1)
        if mk or n >= 2:
            f["es_cadena_detectada"], f["cadena_detectada"] = "si", (mk or key)
            f["cantidad_sucursales_cadena"], f["tipo_establecimiento"] = n, "cadena"
        else:
            f["es_cadena_detectada"], f["cadena_detectada"] = "no", ""
            f["cantidad_sucursales_cadena"], f["tipo_establecimiento"] = 1, "independiente"

    # id estable
    for i, f in enumerate(sorted(filas, key=lambda x: (x["clase_integrada"], x["nombre"])), 1):
        f["id_integrado"] = f"INT{i:04d}"

    escribir(filas, com_m, bar_m)
    return 0


def escribir(filas, com_m, bar_m):
    cols = ["id_integrado", "nombre", "direccion", "lat", "lon", "comuna", "barrio",
            "clase_integrada", "confianza_integrada", "fuentes_detectan", "cantidad_fuentes",
            "fuente_principal", "es_cadena_detectada", "cadena_detectada",
            "cantidad_sucursales_cadena", "tipo_establecimiento", "tipo_establecimiento_google",
            "requiere_revision_manual", "motivo_clasificacion", "queries_detectado"]

    candidatos = [f for f in filas if f["clase_integrada"] != "C_descartado"]
    descartados = [f for f in filas if f["clase_integrada"] == "C_descartado"]

    # padron candidato (sensible)
    _wr(OUT / "padron_candidato_integrado.csv", cols, candidatos)
    # geojson
    feats = []
    for f in candidatos:
        la, lo = fnum(f["lat"]), fnum(f["lon"])
        if la is None or lo is None:
            continue
        props = {k: f[k] for k in cols}
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lo, la]},
                      "properties": props})
    (OUT / "padron_candidato_integrado.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    # trazabilidad / dedup (incluye descartados: nada desaparece)
    _wr(OUT / "deduplicacion_fuentes.csv", cols, filas)

    # revisión manual prioritaria
    revm = [f for f in filas if f["requiere_revision_manual"] == "si"]
    _wr(OUT / "revision_manual_prioritaria.csv", cols, revm)

    # ----- agregados (seguros) -----
    por_fuente = Counter(f["fuentes_detectan"] for f in candidatos)
    _wr2(OUT / "integrado_por_fuente.csv", ["combinacion_fuentes", "cantidad"],
         [{"combinacion_fuentes": k, "cantidad": v} for k, v in sorted(por_fuente.items(), key=lambda x: -x[1])])

    def agg(campo, area_lookup):
        d = defaultdict(lambda: {"cantidad": 0})
        for f in candidatos:
            key = f[campo] or "(sin asignar)"
            d[key]["cantidad"] += 1
        out = []
        for k, v in d.items():
            area = area_lookup.get(k)
            dens = round(v["cantidad"] / area, 4) if area else ""
            out.append({campo: k, "cantidad": v["cantidad"], "area_km2": area or "",
                        "densidad_por_km2": dens})
        out.sort(key=lambda x: -x["cantidad"])
        return out

    area_com = {m["comuna"]: m["area_km2"] for m in com_m}
    area_bar = {m["barrio"]: m["area_km2"] for m in bar_m}
    por_comuna = agg("comuna", area_com)
    por_barrio = agg("barrio", area_bar)
    _wr2(OUT / "integrado_por_comuna.csv", ["comuna", "cantidad", "area_km2", "densidad_por_km2"], por_comuna)
    _wr2(OUT / "integrado_por_barrio.csv", ["barrio", "cantidad", "area_km2", "densidad_por_km2"], por_barrio)
    _wr2(OUT / "densidad_integrado_por_comuna.csv", ["comuna", "cantidad", "area_km2", "densidad_por_km2"],
         sorted([r for r in por_comuna if r["area_km2"]], key=lambda x: -(x["densidad_por_km2"] or 0)))
    _wr2(OUT / "densidad_integrado_por_barrio.csv", ["barrio", "cantidad", "area_km2", "densidad_por_km2"],
         sorted([r for r in por_barrio if r["area_km2"]], key=lambda x: -(x["densidad_por_km2"] or 0)))

    # cobertura cadenas vs independientes
    cad = defaultdict(lambda: {"sucursales": 0})
    for f in candidatos:
        if f["es_cadena_detectada"] == "si":
            cad[f["cadena_detectada"]]["sucursales"] += 1
    _wr2(OUT / "cobertura_cadenas_e_independientes.csv", ["cadena", "sucursales"],
         sorted([{"cadena": k, "sucursales": v["sucursales"]} for k, v in cad.items()],
                key=lambda x: -x["sucursales"]))

    # calidad google queries (copia derivada, segura)
    if GOOGLE_CALIDAD.exists():
        rows = list(csv.DictReader(GOOGLE_CALIDAD.open(encoding="utf-8-sig")))
        if rows:
            _wr(OUT / "calidad_google_queries.csv", list(rows[0].keys()), rows)

    # ----- resumen -----
    n_cad = sum(1 for f in candidatos if f["tipo_establecimiento"] == "cadena")
    n_ind = sum(1 for f in candidatos if f["tipo_establecimiento"] == "independiente")
    clases = Counter(f["clase_integrada"] for f in candidatos)
    fuente_solo = Counter()
    for f in candidatos:
        fuente_solo[f["fuentes_detectan"]] += 1
    multif = sum(1 for f in candidatos if f["cantidad_fuentes"] >= 2)
    g_a = sum(1 for f in candidatos if "google" in f["fuentes_detectan"])
    o_a = sum(1 for f in candidatos if "osm" in f["fuentes_detectan"])
    a_a = sum(1 for f in candidatos if "agc" in f["fuentes_detectan"])
    baja_com = [r["comuna"] for r in por_comuna if r["cantidad"] <= 2 and r["comuna"] != "(sin asignar)"]

    resumen = [
        ("fecha", dt.date.today().isoformat()),
        ("nota", "Padrón CANDIDATO (no oficial). AGC=oficial estricto/no implica local activo; OSM=auxiliar; Google=operativo no oficial."),
        ("candidatos_unicos", len(candidatos)),
        ("descartados", len(descartados)),
        ("clase_A_integrado_multifuente", clases.get("A_integrado_multifuente", 0)),
        ("clase_A_google_probable", clases.get("A_google_probable", 0)),
        ("clase_A_osm_auxiliar", clases.get("A_osm_auxiliar", 0)),
        ("clase_A_agc_oficial_estricto", clases.get("A_agc_oficial_estricto", 0)),
        ("clase_B_revision_manual", clases.get("B_revision_manual", 0)),
        ("con_google", g_a), ("con_osm", o_a), ("con_agc", a_a),
        ("multifuente", multif),
        ("cadenas", n_cad), ("independientes", n_ind),
        ("revision_manual_prioritaria", len([f for f in filas if f["requiere_revision_manual"] == "si"])),
        ("comunas_baja_cobertura", "; ".join(sorted(baja_com)) or "(ninguna)"),
    ]
    _wr2(OUT / "resumen_integrado.csv", ["indicador", "valor"],
         [{"indicador": k, "valor": v} for k, v in resumen])

    print(f"Candidatos únicos: {len(candidatos)} | descartados: {len(descartados)}")
    print(f"  multifuente={multif} con_google={g_a} con_osm={o_a} con_agc={a_a}")
    print(f"  cadenas={n_cad} independientes={n_ind} revision_manual={len([f for f in filas if f['requiere_revision_manual']=='si'])}")
    print("  clases:", dict(clases))
    print("  top comunas:", [(r["comuna"], r["cantidad"]) for r in por_comuna[:5]])
    print("  top barrios:", [(r["barrio"], r["cantidad"]) for r in por_barrio[:5]])
    print(f"Salidas en: {OUT.relative_to(ROOT)}")


def _wr(path, cols, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _wr2(path, cols, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
