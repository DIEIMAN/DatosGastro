"""Corrige la clasificación cadena/independiente en el padrón v2 (SIN requests).

Motivo: nombres genéricos de categoría ('pastas frescas', 'pastificio', 'fábrica de pasta',
'pasta') quedaban marcados como cadena por repetición de nombre, cuando son locales
independientes distintos. Además recuenta sucursales en el conjunto v2 real.

Actualiza:
  outputs/casas_pastas_integrado/padron_candidato_integrado_v2.csv  (flags de cadena)
  outputs/casas_pastas_integrado/resumen_integrado_v2.csv           (cadenas/independientes)
  outputs/casas_pastas_integrado/cobertura_cadenas_e_independientes.csv
  outputs/casas_pastas_reporte/integrado_sanitizado/resumen_integrado_v2.csv
  outputs/casas_pastas_reporte/integrado_sanitizado/cobertura_cadenas_e_independientes.csv

No cambia el total (261) ni las clases A/B. No commitea.
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_places_clasificador import clasificar_cadena, norm_nombre  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
SAN = ROOT / "outputs" / "casas_pastas_reporte" / "integrado_sanitizado"
PADRON = INT / "padron_candidato_integrado_v2.csv"
RESUMEN = INT / "resumen_integrado_v2.csv"
COBERTURA = INT / "cobertura_cadenas_e_independientes.csv"


def _wr(path, cols, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    pad = list(csv.DictReader(PADRON.open(encoding="utf-8-sig")))
    cols = list(pad[0].keys())
    cnt = Counter(norm_nombre(r["nombre"]) for r in pad)

    old = Counter(r["tipo_establecimiento"] for r in pad)
    cambios = 0
    for r in pad:
        nrm = norm_nombre(r["nombre"])
        tipo, cadena = clasificar_cadena(nrm, cnt[nrm])
        if tipo != r["tipo_establecimiento"]:
            cambios += 1
        r["tipo_establecimiento"] = tipo
        r["es_cadena_detectada"] = "si" if tipo == "cadena" else "no"
        r["cadena_detectada"] = cadena
        # recuento de sucursales por cadena en el set v2
        r["cantidad_sucursales_cadena"] = ""  # se completa abajo
    # recuento por cadena
    cad_cnt = Counter(r["cadena_detectada"] for r in pad if r["es_cadena_detectada"] == "si" and r["cadena_detectada"])
    for r in pad:
        if r["es_cadena_detectada"] == "si":
            r["cantidad_sucursales_cadena"] = cad_cnt[r["cadena_detectada"]]
        else:
            r["cantidad_sucursales_cadena"] = 1
    _wr(PADRON, cols, pad)

    new = Counter(r["tipo_establecimiento"] for r in pad)
    n_cad, n_ind = new["cadena"], new["independiente"]

    # cobertura (excluye genéricos por construcción)
    cob = sorted([{"cadena": k, "sucursales": v} for k, v in cad_cnt.items()],
                 key=lambda x: -x["sucursales"])
    _wr(COBERTURA, ["cadena", "sucursales"], cob)
    SAN.mkdir(parents=True, exist_ok=True)
    _wr(SAN / "cobertura_cadenas_e_independientes.csv", ["cadena", "sucursales"], cob)

    # resumen v2: actualizar solo cadenas/independientes, preservar el resto
    for rpath in (RESUMEN, SAN / "resumen_integrado_v2.csv"):
        if not rpath.exists():
            continue
        rows = list(csv.DictReader(rpath.open(encoding="utf-8-sig")))
        for row in rows:
            if row["indicador"] == "cadenas":
                row["valor"] = n_cad
            elif row["indicador"] == "independientes":
                row["valor"] = n_ind
        _wr(rpath, ["indicador", "valor"], rows)

    print(f"Reclasificados cadena->independiente: {cambios}")
    print(f"ANTES: cadena={old['cadena']} independiente={old['independiente']}")
    print(f"AHORA: cadena={n_cad} independiente={n_ind} (total {n_cad + n_ind})")
    print("Cadenas reales (top):", [(c["cadena"], c["sucursales"]) for c in cob[:6]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
