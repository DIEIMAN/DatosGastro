"""Segunda pasada LOCAL sobre fuentes oficiales/abiertas ya disponibles en el proyecto
(sin descargar nada, sin requests) para detectar indicios de casas de pastas que podrían
faltar en el padrón depurado.

NO modifica el padrón. NO llama a los registros "locales activos": son registros
administrativos o indicios según la fuente.

Salidas (gitignored):
  outputs/casas_pastas_recall/oficiales_recheck/candidatos_oficiales_extra_a_validar.csv
  outputs/casas_pastas_recall/oficiales_recheck/resumen_recheck_oficial.csv
"""
from __future__ import annotations

import csv
import datetime as dt
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[2]
CP = ROOT / "outputs" / "casas_pastas"
PADRON = ROOT / "outputs" / "casas_pastas_integrado" / "padron_candidato_integrado_v3_depurado.csv"
OUT = ROOT / "outputs" / "casas_pastas_recall" / "oficiales_recheck"

TERMINOS = ["pasta", "pastas", "pastificio", "fabrica de pastas", "pastas frescas", "raviol",
            "sorrentin", "noqui", "gnocchi", "fideos", "tallarin", "agnolotti"]
# Fuentes locales disponibles (registros administrativos / relevamiento abierto).
FUENTES = [
    ("candidatos_f02_probables.csv", "AGC/F02 (probables)", "registro administrativo"),
    ("candidatos_f02_dudosos_descartados.csv", "AGC/F02 (dudosos)", "registro administrativo"),
    ("osm_casas_pastas_candidatos.csv", "OpenStreetMap", "relevamiento abierto"),
]


def na(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def main() -> int:
    padron = set()
    if PADRON.exists():
        padron = {na(r["nombre"]) for r in csv.DictReader(PADRON.open(encoding="utf-8-sig"))}

    filas = []
    for archivo, fuente, tipo_reg in FUENTES:
        p = CP / archivo
        if not p.exists():
            continue
        for r in csv.DictReader(p.open(encoding="utf-8-sig")):
            nombre = r.get("nombre_original", "") or r.get("nombre", "")
            blob = na(" ".join([nombre, r.get("rubro_original", ""), r.get("descripcion_original", ""),
                                r.get("shop", ""), r.get("categoria_pastas", "")]))
            term = next((t for t in TERMINOS if t in blob), None)
            if not term:
                continue
            nrm = na(nombre)
            if not nrm:
                continue
            presente = nrm in padron
            zona = r.get("comuna_efectiva", "") or r.get("comuna_original", "") or r.get("addr", "")
            filas.append({
                "nombre": nombre, "fuente": fuente, "tipo_registro": tipo_reg,
                "barrio_o_comuna": str(zona)[:40], "termino_detectado": term,
                "estado_en_padron": "presente_en_padron" if presente else "indicio_a_validar",
                "accion_sugerida": "ya representado" if presente else
                                   "validar (registro/indicio, no implica local activo)",
            })

    # dedup por (nombre normalizado, fuente)
    vistos, dedup = set(), []
    for f in filas:
        k = (na(f["nombre"]), f["fuente"])
        if k in vistos:
            continue
        vistos.add(k); dedup.append(f)

    OUT.mkdir(parents=True, exist_ok=True)
    cols = ["nombre", "fuente", "tipo_registro", "barrio_o_comuna", "termino_detectado",
            "estado_en_padron", "accion_sugerida"]
    with (OUT / "candidatos_oficiales_extra_a_validar.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(dedup)

    est = Counter(f["estado_en_padron"] for f in dedup)
    porf = Counter(f["fuente"] for f in dedup)
    with (OUT / "resumen_recheck_oficial.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh); w.writerow(["indicador", "valor"])
        w.writerow(["fecha", dt.date.today().isoformat()])
        w.writerow(["registros_con_termino_pastas", len(dedup)])
        for k, v in est.items():
            w.writerow([k, v])
        for k, v in porf.items():
            w.writerow([f"fuente:{k}", v])
        w.writerow(["nota", "registros administrativos / indicios; NO equivalen a locales activos"])

    print(f"Recheck oficial: {len(dedup)} registros con término de pastas · {dict(est)}")
    print(f"  por fuente: {dict(porf)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
