"""Aplica la revisión manual de Diego sobre los 42 casos en revisión y depura el padrón.

SIN requests, sin API key, sin tocar datos crudos. Genera:
  Internos (gitignored, con nombres):
    .../anexos_internos/revision_manual_diego/decisiones_revision_manual_diego.csv
    .../anexos_internos/revision_manual_diego/confirmados_revision_manual_diego.csv
    .../anexos_internos/revision_manual_diego/descartados_revision_manual_diego.csv
    .../anexos_internos/revision_manual_diego/resumen_revision_manual_diego.csv
  Padrón depurado (gitignored):
    outputs/casas_pastas_integrado/padron_candidato_integrado_v3_depurado.csv
    outputs/casas_pastas_integrado/resumen_integrado_v3_depurado.csv
  Agregados sanitizados (publicables, sin datos individuales):
    outputs/casas_pastas_reporte/integrado_sanitizado/*_v3_depurado.csv / .geojson

Regla: confirmar_A_manual -> clase A_validado_manual; descartar_C_manual -> fuera del padrón
(se conservan en anexo). No se inventan fuentes.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

from shapely.geometry import Point, shape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_places_clasificador import clasificar_cadena, norm_nombre  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
REP = ROOT / "outputs" / "casas_pastas_reporte"
SAN = REP / "integrado_sanitizado"
GEO = ROOT / "data" / "raw"
DIEGO = REP / "anexos_internos" / "revision_manual_diego"
PADRON = INT / "padron_candidato_integrado_v2.csv"
AUDIT = INT / "auditoria_calidad" / "auditoria_revision_manual_prioritaria_ordenada.csv"
GEO_DECIMALS = 3

# (nombre, comuna, motivo) — revisión manual de Diego.
CONFIRMAR = [
    ("B&L", "5", "venden pastas como el resto de la cadena B&L"),
    ("La Gran Avenida", "11", "sigue existiendo; caso a conservar"),
    ("La Torinesa", "7", "fábrica de pastas; muy buenas reseñas; candidata a investigación histórica"),
    ("Que Sabor...!", "12", "existe y vende pastas"),
    ("12 de Octubre", "11", "existe y vende pastas"),
    ("Al Puro Huevo - Buenos Aires", "2", "existe y vende pastas"),
    ("Doña Fábrica", "5", "existe y vende pastas"),
    ("El Gran Sabor", "5", "existe y vende pastas"),
    ("Familia Aufieri", "6", "existe y vende pastas"),
    ("Felipe Il Nonno", "12", "existe y vende pastas"),
    ("Imperial", "12", "existe y vende pastas"),
    ("La Buenos Aires de Paco", "12", "existe y vende pastas"),
    ("La Delfina", "12", "existe y vende pastas"),
    ("La Genovesa", "14", "existe y vende pastas"),
    ("La Juvenil de Almagro", "5", "sucursal de LA JUVENIL"),
    ("La Luisita", "14", "existe y vende pastas"),
    ("La Luisita", "5", "existe y vende pastas"),
    ("La abuela amasa", "7", "existe y vende pastas"),
    ("Las Delicias de Gascón", "14", "existe y vende pastas"),
    ("Pastas Artesanales", "3", "existe y vende pastas"),
    ("Pastas Artesanales Casa Vázquez", "7", "existe y vende pastas"),
    ("Pastas Savori", "6", "probablemente Pastas Sívori; existe y vende pastas (corregir nombre, mantener trazabilidad)"),
    ("Piatto Rosso", "6", "existe y vende pastas"),
    ("Puerta del Sol", "14", "existe y vende pastas"),
    ("Rochino Villa Urquiza", "12", "existe y vende pastas"),
    ("San Jose", "11", "existe y vende pastas"),
    ("¡QUIERO MAS..!", "2", "existe y vende pastas"),
]
DESCARTAR = [
    ("El Pastificio de Pablos", "11", "no es casa de pastas"),
    ("La Abuela Amasa Caballito", "6", "vende pastas cocinadas; no es casa de pastas/pastificio"),
    ("La Parolaccia Casa Tua Palermo", "14", "trattoria/restaurante italiano"),
    ("Pablos", "11", "restaurante; no casa de pastas"),
    ("Fábrica de Pasta", "4", "no existe / no verificable"),
    ("Fábrica de Pasta", "9", "no existe / no verificable"),
    ("Jardín de Infantes Común 02/07° Prof. Marina Margarita Ravioli", "6", "no es lugar gastronómico"),
    ("La Leonesa 3", "6", "posible cierre; no contar por prudencia"),
    ("La Parolaccia Barrio Norte", "2", "trattoria/restaurante italiano"),
    ("La Pasta Frola", "1", "confitería; no vende pastas"),
    ("Otra Pasta", "1", "restaurante; no contar"),
    ("PASTIFICIO", "14", "cerrado o restaurante; no contar"),
    ("Pasta", "14", "no contar"),
    ("Pastas Al Paso y Algo Más", "10", "cerrado"),
    ("Terra di pasta Shopping Devoto", "11", "restaurante/fast food de pastas; no contar"),
]


def _wr(path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main() -> int:
    pad = list(csv.DictReader(PADRON.open(encoding="utf-8-sig")))
    prio = {}
    if AUDIT.exists():
        for r in csv.DictReader(AUDIT.open(encoding="utf-8-sig")):
            prio[norm_nombre(r["nombre"])] = r.get("prioridad_revision", "3")

    # Índice de decisiones por (nombre normalizado, comuna)
    dec = {}
    for nombre, com, mot in CONFIRMAR:
        dec[(norm_nombre(nombre), com)] = ("confirmar_A_manual", mot)
    for nombre, com, mot in DESCARTAR:
        dec[(norm_nombre(nombre), com)] = ("descartar_C_manual", mot)

    B = [r for r in pad if r["clase_integrada"] == "B_revision_manual"]
    decisiones, confirmados, descartados, sin_match = [], [], [], []
    confirmar_ids, descartar_ids = set(), set()
    for r in B:
        key = (norm_nombre(r["nombre"]), r["comuna"])
        if key not in dec:
            sin_match.append(r); continue
        d, mot = dec[key]
        obs = "validado manualmente por Diego (revisión de escritorio)"
        if "Savori" in r["nombre"]:
            obs = "posible nombre real: Pastas Sívori (trazabilidad: nombre original 'Pastas Savori')"
        fila = {
            "nombre": r["nombre"], "barrio": r["barrio"], "comuna": r["comuna"],
            "prioridad": prio.get(norm_nombre(r["nombre"]), "3"),
            "decision_diego": d, "motivo_diego": mot,
            "accion_final_sugerida": "A_validado_manual" if d == "confirmar_A_manual" else "excluir_del_padron",
            "observaciones": obs,
        }
        decisiones.append(fila)
        if d == "confirmar_A_manual":
            confirmar_ids.add(r["id_integrado"]); confirmados.append(fila)
        else:
            descartar_ids.add(r["id_integrado"]); descartados.append(fila)

    if sin_match:
        print(f"AVISO: {len(sin_match)} casos B sin decisión de Diego (quedan en revisión):")
        for r in sin_match:
            print(f"   - c{r['comuna']} {r['nombre']}")

    # ---- Padrón v3 depurado ----
    v3 = []
    for r in pad:
        if r["id_integrado"] in descartar_ids:
            continue  # fuera del padrón principal (se conserva en anexo)
        row = dict(r)
        if r["id_integrado"] in confirmar_ids:
            row["clase_integrada"] = "A_validado_manual"
            row["confianza_integrada"] = "validado_manual"
            row["requiere_revision_manual"] = "no"
            row["motivo_clasificacion"] = "confirmado en revisión manual (Diego)"
        v3.append(row)

    # ---- Incorporación documental (fuente fuerte, fuera del cruce automático) ----
    # Sin dirección ni coordenadas (no se inventan): entra con comuna/barrio conocidos y
    # estado "requiere geocodificación". Clase propia A_documental_validado_manual.
    DOCUMENTALES = [
        {"nombre": "Pastas Amelia", "comuna": "5", "barrio": "Boedo",
         "motivo": "incorporado por revisión documental (La Nación; fábrica desde 1948, Boedo)"},
    ]
    base_cols = {c: "" for c in pad[0].keys()}
    incorporados_doc = 0
    for k, dde in enumerate(DOCUMENTALES, 1):
        if any(norm_nombre(r["nombre"]) == norm_nombre(dde["nombre"]) and r["comuna"] == dde["comuna"]
               for r in v3):
            continue  # ya presente, no duplicar
        row = dict(base_cols)
        row.update({
            "id_integrado": f"INTDOC{k:02d}", "nombre": dde["nombre"], "direccion": "",
            "lat": "", "lon": "", "comuna": dde["comuna"], "barrio": dde["barrio"],
            "clase_integrada": "A_documental_validado_manual", "confianza_integrada": "documental",
            "fuentes_detectan": "documental", "cantidad_fuentes": "1", "fuente_principal": "documental",
            "requiere_revision_manual": "geocodificacion_pendiente",
            "motivo_clasificacion": dde["motivo"], "queries_detectado": "",
        })
        v3.append(row); incorporados_doc += 1

    # ---- Incorporación por RECALL Google (aprobados en revisión manual) ----
    # Los 7 casos validados como casa de pastas/fábrica/venta. Se geocodifican desde los brutos
    # del recall (coordenadas), clase A_google_recall_validado_manual. NO se suman a mano.
    # Además se ENRIQUECE Pastas Amelia (documental) con coordenadas si están disponibles.
    RECALL_BRUTO = ROOT / "outputs" / "casas_pastas_recall" / "google_api_complementaria" / "bruto"
    APROBADOS = {  # clave normalizada -> etiqueta de display
        "franccesca": "Franccesca - Pastas Artesanales",
        "civitavecchia": "Fábrica de pastas Civitavecchia Pastas Frescas",
        "via reggio": "Via Reggio - Pastas Artesanales",
        "senora pasta": "Señora Pasta",
        "laurimar": "Fábrica de Pastas Laurimar",
        "buon giorno": "Fábrica de Pastas Frescas Buon Giorno Artesanales",
        "emporio de las pastas": "El Emporio de las Pastas",
    }
    incorporados_recall = 0
    amelia_geocodificada = False
    if RECALL_BRUTO.exists():
        gc = json.load((ROOT / "data" / "raw" / "geo_comunas.geojson").open(encoding="utf-8"))
        gb = json.load((ROOT / "data" / "raw" / "geo_barrios.geojson").open(encoding="utf-8"))
        com_shapes = [(shape(f["geometry"]), str(f["properties"]["comuna"])) for f in gc["features"]]
        bar_shapes = [(shape(f["geometry"]), f["properties"]["nombre"].title()) for f in gb["features"]]

        def geocode(lat, lon):
            try:
                pt = Point(float(lon), float(lat))
            except (TypeError, ValueError):
                return "", ""
            com = next((c for s, c in com_shapes if s.contains(pt)), "")
            bar = next((b for s, b in bar_shapes if s.contains(pt)), "")
            return com, bar

        # Indexar mejor coincidencia por clave aprobada y por Amelia desde los brutos
        hallados = {}
        for jf in sorted(RECALL_BRUTO.glob("*.json")):
            try:
                places = json.load(jf.open(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            for p in places:
                nm = norm_nombre((p.get("displayName") or {}).get("text", ""))
                loc = p.get("location") or {}
                claves = list(APROBADOS.keys()) + ["fabrica de pastas amelia"]
                for clave in claves:
                    if clave in nm and clave not in hallados and loc.get("latitude") is not None:
                        hallados[clave] = {"lat": loc.get("latitude"), "lon": loc.get("longitude"),
                                           "direccion": p.get("formattedAddress", ""),
                                           "types": ";".join(p.get("types") or [])}

        for k, clave in enumerate(APROBADOS, 1):
            if any(norm_nombre(r["nombre"]) == norm_nombre(APROBADOS[clave]) for r in v3):
                continue  # ya presente
            h = hallados.get(clave)
            if not h:
                continue  # sin dato en bruto, no inventar
            com, bar = geocode(h["lat"], h["lon"])
            row = dict(base_cols)
            row.update({
                "id_integrado": f"INTREC{k:02d}", "nombre": APROBADOS[clave], "direccion": h["direccion"],
                "lat": str(h["lat"]), "lon": str(h["lon"]), "comuna": com, "barrio": bar,
                "clase_integrada": "A_google_recall_validado_manual",
                "confianza_integrada": "recall_validado_manual",
                "fuentes_detectan": "google_recall", "cantidad_fuentes": "1",
                "fuente_principal": "google_recall", "requiere_revision_manual": "no",
                "motivo_clasificacion": "detectado por recall complementario Google y validado manualmente",
                "queries_detectado": "",
            })
            v3.append(row); incorporados_recall += 1

        # Enriquecer Pastas Amelia con coordenadas (no la suma como nueva)
        am = hallados.get("fabrica de pastas amelia")
        if am:
            for r in v3:
                if r["id_integrado"].startswith("INTDOC") and "amelia" in norm_nombre(r["nombre"]):
                    if not r.get("lat"):
                        com, bar = geocode(am["lat"], am["lon"])
                        r["lat"] = str(am["lat"]); r["lon"] = str(am["lon"])
                        r["comuna"] = r["comuna"] or com
                        r["barrio"] = r["barrio"] or bar
                        r["requiere_revision_manual"] = "no"
                        r["motivo_clasificacion"] = (r.get("motivo_clasificacion", "") +
                                                     " | geocodificado vía recall Google")
                        amelia_geocodificada = True
                    break

    # Recalcular cadena/independiente sobre el universo depurado
    cnt_nrm = Counter(norm_nombre(r["nombre"]) for r in v3)
    for r in v3:
        tipo, cadena = clasificar_cadena(norm_nombre(r["nombre"]), cnt_nrm[norm_nombre(r["nombre"])])
        r["tipo_establecimiento"] = tipo
        r["es_cadena_detectada"] = "si" if tipo == "cadena" else "no"
        r["cadena_detectada"] = cadena
    cad_cnt = Counter(r["cadena_detectada"] for r in v3 if r["es_cadena_detectada"] == "si" and r["cadena_detectada"])
    for r in v3:
        r["cantidad_sucursales_cadena"] = cad_cnt[r["cadena_detectada"]] if r["es_cadena_detectada"] == "si" else 1

    cols = list(pad[0].keys())
    _wr(INT / "padron_candidato_integrado_v3_depurado.csv", cols, v3)

    # ---- Métricas ----
    clases = Counter(r["clase_integrada"] for r in v3)
    n_tot = len(v3)
    con = lambda f: sum(1 for r in v3 if f in r["fuentes_detectan"])
    multif = sum(1 for r in v3 if int(r["cantidad_fuentes"]) >= 2)
    n_cad = sum(1 for r in v3 if r["tipo_establecimiento"] == "cadena")
    n_ind = sum(1 for r in v3 if r["tipo_establecimiento"] == "independiente")
    georref = sum(1 for r in v3 if fnum(r["lat"]) is not None and fnum(r["lon"]) is not None)
    combos = Counter(r["fuentes_detectan"] for r in v3)

    resumen = [
        ("nota", "Padrón candidato DEPURADO (no oficial) tras revisión manual de escritorio."),
        ("candidatos_unicos", n_tot),
        ("candidatos_unicos_v2", len(pad)),
        ("confirmados_revision_manual", len(confirmados)),
        ("descartados_revision_manual", len(descartados)),
        ("incorporados_documentales", incorporados_doc),
        ("incorporados_recall_google", incorporados_recall),
        ("amelia_geocodificada", "si" if amelia_geocodificada else "no"),
        ("casos_aun_en_revision", len(sin_match)),
        ("clase_A_integrado_multifuente", clases.get("A_integrado_multifuente", 0)),
        ("clase_A_validado_manual", clases.get("A_validado_manual", 0)),
        ("clase_A_documental_validado_manual", clases.get("A_documental_validado_manual", 0)),
        ("clase_A_google_recall_validado_manual", clases.get("A_google_recall_validado_manual", 0)),
        ("clase_A_google_probable", clases.get("A_google_probable", 0)),
        ("clase_A_osm_auxiliar", clases.get("A_osm_auxiliar", 0)),
        ("clase_A_agc_oficial_estricto", clases.get("A_agc_oficial_estricto", 0)),
        ("con_google", con("google")), ("con_osm", con("osm")), ("con_agc", con("agc")),
        ("multifuente", multif), ("cadenas", n_cad), ("independientes", n_ind),
        ("georreferenciados", georref),
    ]
    rrows = [{"indicador": k, "valor": v} for k, v in resumen]
    _wr(INT / "resumen_integrado_v3_depurado.csv", ["indicador", "valor"], rrows)
    _wr(SAN / "resumen_integrado_v3_depurado.csv", ["indicador", "valor"], rrows)

    # ---- Internos (con nombres) ----
    _wr(DIEGO / "decisiones_revision_manual_diego.csv",
        ["nombre", "barrio", "comuna", "prioridad", "decision_diego", "motivo_diego",
         "accion_final_sugerida", "observaciones"], decisiones)
    _wr(DIEGO / "confirmados_revision_manual_diego.csv",
        ["nombre", "barrio", "comuna", "prioridad", "decision_diego", "motivo_diego",
         "accion_final_sugerida", "observaciones"], confirmados)
    _wr(DIEGO / "descartados_revision_manual_diego.csv",
        ["nombre", "barrio", "comuna", "prioridad", "decision_diego", "motivo_diego",
         "accion_final_sugerida", "observaciones"], descartados)
    _wr(DIEGO / "resumen_revision_manual_diego.csv", ["indicador", "valor"], [
        {"indicador": "casos_revisados", "valor": len(B)},
        {"indicador": "confirmados", "valor": len(confirmados)},
        {"indicador": "descartados", "valor": len(descartados)},
        {"indicador": "sin_decision", "valor": len(sin_match)},
    ])

    # ---- Agregados sanitizados depurados ----
    gc = json.load((GEO / "geo_comunas.geojson").open(encoding="utf-8"))
    gb = json.load((GEO / "geo_barrios.geojson").open(encoding="utf-8"))
    acom = {str(f["properties"]["comuna"]): f["properties"]["area"] / 1e6 for f in gc["features"]}
    abar = {f["properties"]["nombre"].title(): f["properties"]["area_metro"] / 1e6 for f in gb["features"]}
    com = Counter(r["comuna"] for r in v3 if r["comuna"])
    bar = Counter(r["barrio"] for r in v3 if r["barrio"])

    etq = {
        "osm": "solo OSM",
        "google": "solo Google",
        "google+osm": "Google + OSM",
        "agc": "solo AGC",
        "google_recall": "Recall complementario",
        "documental": "Documental (revisión)",
    }
    _wr(SAN / "integrado_por_fuente_v3_depurado.csv", ["combinacion_fuentes", "cantidad"],
        [{"combinacion_fuentes": etq.get(k, k), "cantidad": combos.get(k, 0)}
         for k in ("osm", "google", "google+osm", "agc", "google_recall", "documental")]
        + [{"combinacion_fuentes": "total", "cantidad": n_tot}, {"combinacion_fuentes": "multifuente", "cantidad": multif}])

    def agg(counter, area):
        out = []
        for k, n in sorted(counter.items(), key=lambda x: -x[1]):
            a = area.get(k)
            out.append({"clave": k, "cantidad": n, "area_km2": round(a, 4) if a else "",
                        "densidad_por_km2": round(n / a, 4) if a else ""})
        return out

    ca = agg(com, acom); ba = agg(bar, abar)
    _wr(SAN / "integrado_por_comuna_v3_depurado.csv", ["comuna", "cantidad", "area_km2", "densidad_por_km2"],
        [{"comuna": r["clave"], **{k: r[k] for k in ("cantidad", "area_km2", "densidad_por_km2")}} for r in ca])
    _wr(SAN / "integrado_por_barrio_v3_depurado.csv", ["barrio", "cantidad", "area_km2", "densidad_por_km2"],
        [{"barrio": r["clave"], **{k: r[k] for k in ("cantidad", "area_km2", "densidad_por_km2")}} for r in ba])
    _wr(SAN / "densidad_integrado_por_comuna_v3_depurado.csv", ["comuna", "cantidad", "area_km2", "densidad_por_km2"],
        sorted([{"comuna": r["clave"], "cantidad": r["cantidad"], "area_km2": r["area_km2"],
                 "densidad_por_km2": r["densidad_por_km2"]} for r in ca if r["area_km2"]],
               key=lambda x: -(x["densidad_por_km2"] or 0)))
    _wr(SAN / "densidad_integrado_por_barrio_v3_depurado.csv", ["barrio", "cantidad", "area_km2", "densidad_por_km2"],
        sorted([{"barrio": r["clave"], "cantidad": r["cantidad"], "area_km2": r["area_km2"],
                 "densidad_por_km2": r["densidad_por_km2"]} for r in ba if r["area_km2"]],
               key=lambda x: -(x["densidad_por_km2"] or 0)))

    # GeoJSON depurado reducido (sin datos individuales)
    feats = []
    for i, r in enumerate(v3, 1):
        la, lo = fnum(r["lat"]), fnum(r["lon"])
        if la is None or lo is None:
            continue
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [round(lo, GEO_DECIMALS), round(la, GEO_DECIMALS)]},
                      "properties": {"id_anonimo": f"PT{i:04d}", "clasificacion_integrada": r["clase_integrada"],
                                     "es_cadena_detectada": r["es_cadena_detectada"], "comuna": r["comuna"],
                                     "barrio": r["barrio"]}})
    (SAN / "mapa_puntos_sanitizado_v3_depurado.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"DEPURADO: v2={len(pad)} -> v3={n_tot} | confirmados={len(confirmados)} descartados={len(descartados)} "
          f"sin_decision={len(sin_match)}")
    print(f"  clases: {dict(clases)}")
    print(f"  indep={n_ind} cadenas={n_cad} multifuente={multif} georref={georref}")
    print(f"  con_google={con('google')} con_osm={con('osm')} con_agc={con('agc')}")
    print(f"  geojson: {len(feats)} puntos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
