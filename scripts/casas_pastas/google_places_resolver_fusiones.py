"""Resuelve los casos `revisar_fusion` del padrón candidato integrado (SIN requests).

Reglas deterministas sobre cada candidato B cercano a un A con nombre compatible de pastas:
  - dist al A más cercano < 30 m            -> fusionar_con_A (duplicado real entre fuentes)
  - nombre con señal de restaurante/bodegón -> descartar_C (gastronómico general)
  - resto                                   -> mantener_B_revision (no es duplicado; revisar en campo)

Genera:
  outputs/casas_pastas_integrado/auditoria_calidad/revision_4_fusiones_decision.csv
Y si cambian conteos:
  outputs/casas_pastas_integrado/padron_candidato_integrado_v2.csv
  outputs/casas_pastas_integrado/resumen_integrado_v2.csv
  outputs/casas_pastas_reporte/integrado_sanitizado/resumen_integrado_v2.csv

No borra datos crudos. No commitea. No toca el pipeline principal.
"""
from __future__ import annotations

import csv
import datetime as dt
import math
import sys
import unicodedata
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
AUD = INT / "auditoria_calidad"
REP = ROOT / "outputs" / "casas_pastas_reporte" / "integrado_sanitizado"
PADRON = INT / "padron_candidato_integrado.csv"

DECISION = AUD / "revision_4_fusiones_decision.csv"
PADRON_V2 = INT / "padron_candidato_integrado_v2.csv"
RESUMEN_V2 = INT / "resumen_integrado_v2.csv"
RESUMEN_V2_PUB = REP / "resumen_integrado_v2.csv"

FUSION_M = 30
COMPAT = ("pasta", "raviol", "sorrentin", "noqui", "gnocchi", "tallarin", "fideo", "pastificio")
RESTO_WORDS = ("bodegon", "restaurant", "restaurante", "trattoria", "ristorante",
               "pizzeria", "pizza", "pasta bar", "bar de pasta", "cantina", "osteria")


def na(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def hav(a, b, c, d):
    try:
        a, b, c, d = map(float, (a, b, c, d))
    except (TypeError, ValueError):
        return 9e9
    R = 6371000
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = math.radians(c - a), math.radians(d - b)
    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))


def main() -> int:
    if not PADRON.exists():
        print(f"ABORTADO: falta {PADRON}")
        return 2
    pad = list(csv.DictReader(PADRON.open(encoding="utf-8-sig")))
    A = [r for r in pad if r["clase_integrada"].startswith("A_")]
    Bs = [r for r in pad if r["clase_integrada"] == "B_revision_manual"]

    def nearest_A(r):
        best = None
        for a in A:
            d = hav(r["lat"], r["lon"], a["lat"], a["lon"])
            if best is None or d < best[0]:
                best = (d, a)
        if not best:
            return None, None, None
        d, a = best
        sim = SequenceMatcher(None, na(r["nombre"]), na(a["nombre"])).ratio()
        return d, sim, a

    # casos revisar_fusion: B compatible con pastas y a < 150 m de un A
    casos = []
    for r in Bs:
        n = na(r["nombre"])
        if not any(t in n for t in COMPAT):
            continue
        d, sim, a = nearest_A(r)
        if d is None or d >= 150:
            continue
        casos.append((r, d, sim, a))

    decisiones = []
    fusionar = {}   # id_B -> id_A target
    descartar = set()
    for r, d, sim, a in casos:
        n = na(r["nombre"])
        addr_eq = na(r["direccion"]) and na(r["direccion"]) == na(a["direccion"])
        if d < FUSION_M or addr_eq:
            decision = "fusionar_con_A"
            motivo = (f"a {d:.0f} m del A '{a['nombre']}'"
                      + (" y misma dirección" if addr_eq else "")
                      + "; duplicado real entre fuentes")
            impacto = "-1 (deja de contarse como candidato separado)"
            accion = f"fusionar en {a['id_integrado']}"
            fusionar[r["id_integrado"]] = a
        elif any(w in n for w in RESTO_WORDS):
            decision = "descartar_C"
            motivo = "nombre con señal de bodegón/restaurante: gastronómico general, no casa de pastas"
            impacto = "-1 (pasa a descartado)"
            accion = "mover a descartados (C)"
            descartar.add(r["id_integrado"])
        else:
            decision = "mantener_B_revision"
            motivo = (f"no es duplicado (A más cercano '{a['nombre']}' a {d:.0f} m, distinto); "
                      "nombre compatible pero solo tipo gastronómico: validar en campo")
            impacto = "0 (sin cambio)"
            accion = "validar_manual en campo"
        decisiones.append({
            "caso": r["nombre"], "fuente": r["fuentes_detectan"],
            "clasificacion_actual": r["clase_integrada"],
            "candidato_A_cercano": a["nombre"], "distancia_metros": round(d),
            "similitud_nombre": round(sim, 2), "decision": decision, "motivo": motivo,
            "impacto_en_conteo": impacto, "accion_sugerida": accion,
        })

    AUD.mkdir(parents=True, exist_ok=True)
    cols = ["caso", "fuente", "clasificacion_actual", "candidato_A_cercano", "distancia_metros",
            "similitud_nombre", "decision", "motivo", "impacto_en_conteo", "accion_sugerida"]
    _wr(DECISION, cols, decisiones)

    cambia = bool(fusionar or descartar)
    if not cambia:
        print("Sin cambios de conteo: el padrón candidato integrado ORIGINAL se mantiene.")
        print(f"Decisión escrita en: {DECISION.relative_to(ROOT)}")
        return 0

    # ----- construir padrón v2 -----
    v2 = []
    fused_targets = {a["id_integrado"]: src for src, a in
                     [(pad_b, fusionar[idb]) for idb in fusionar for pad_b in [next(x for x in pad if x["id_integrado"] == idb)]]}
    # mapa target_id -> lista de fuentes absorbidas
    absorb = {}
    for idb, a in fusionar.items():
        b = next(x for x in pad if x["id_integrado"] == idb)
        absorb.setdefault(a["id_integrado"], set()).update(b["fuentes_detectan"].split("+"))

    for r in pad:
        if r["id_integrado"] in fusionar:
            continue  # B fusionado: desaparece como fila propia
        if r["id_integrado"] in descartar:
            continue  # B descartado: sale del padrón candidato
        row = dict(r)
        if r["id_integrado"] in absorb:
            fset = set(row["fuentes_detectan"].split("+")) | absorb[r["id_integrado"]]
            order = {"agc": 3, "google": 2, "osm": 1}
            fl = sorted(fset, key=lambda f: -order.get(f, 0))
            row["fuentes_detectan"] = "+".join(fl)
            row["cantidad_fuentes"] = len(fl)
            if row["clase_integrada"] == "A_google_probable" and len(fl) >= 2:
                row["confianza_integrada"] = "media-alta"
            row["motivo_clasificacion"] = (row.get("motivo_clasificacion", "")
                                           + " | absorbe duplicado OSM/Google por fusión revisada")
        v2.append(row)

    pad_cols = list(pad[0].keys())
    _wr(PADRON_V2, pad_cols, v2)

    # resumen v2
    clases = Counter(r["clase_integrada"] for r in v2)
    n_cad = sum(1 for r in v2 if r["tipo_establecimiento"] == "cadena")
    n_ind = sum(1 for r in v2 if r["tipo_establecimiento"] == "independiente")
    multif = sum(1 for r in v2 if int(r["cantidad_fuentes"]) >= 2)
    rev = sum(1 for r in v2 if r["clase_integrada"] == "B_revision_manual")
    con = lambda f: sum(1 for r in v2 if f in r["fuentes_detectan"])
    resumen = [
        ("fecha", dt.date.today().isoformat()),
        ("version", "v2 (tras resolución de casos revisar_fusion)"),
        ("nota", "Padrón CANDIDATO no oficial. AGC oficial estricto (no implica local activo); OSM auxiliar; Google operativo."),
        ("candidatos_unicos", len(v2)),
        ("candidatos_unicos_v1", len(pad)),
        ("fusionados_con_A", len(fusionar)),
        ("descartados_nuevos", len(descartar)),
        ("clase_A_integrado_multifuente", clases.get("A_integrado_multifuente", 0)),
        ("clase_A_google_probable", clases.get("A_google_probable", 0)),
        ("clase_A_osm_auxiliar", clases.get("A_osm_auxiliar", 0)),
        ("clase_A_agc_oficial_estricto", clases.get("A_agc_oficial_estricto", 0)),
        ("clase_B_revision_manual", rev),
        ("con_google", con("google")), ("con_osm", con("osm")), ("con_agc", con("agc")),
        ("multifuente", multif),
        ("cadenas", n_cad), ("independientes", n_ind),
        ("revision_manual_prioritaria", rev),
    ]
    _wr(RESUMEN_V2, ["indicador", "valor"], [{"indicador": k, "valor": v} for k, v in resumen])
    REP.mkdir(parents=True, exist_ok=True)
    _wr(RESUMEN_V2_PUB, ["indicador", "valor"], [{"indicador": k, "valor": v} for k, v in resumen])

    print(f"Casos resueltos: {len(decisiones)} | fusiones={len(fusionar)} descartes={len(descartar)} "
          f"mantener_B={sum(1 for d in decisiones if d['decision']=='mantener_B_revision')}")
    print(f"Candidatos: {len(pad)} -> {len(v2)} | revisión manual: {rev}")
    for d in decisiones:
        print(f"  - {d['caso'][:34]:34s} d={d['distancia_metros']}m -> {d['decision']}")
    print(f"Archivos: {DECISION.name}, {PADRON_V2.name}, {RESUMEN_V2.name}, (pub) {RESUMEN_V2_PUB.name}")
    return 0


def _wr(path, cols, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
