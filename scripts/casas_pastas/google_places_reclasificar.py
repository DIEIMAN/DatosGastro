"""Reprocesa (SIN nuevos requests) la corrida ampliada de Google Places con un criterio
de clasificación ajustado para casas/fábricas/locales de venta de pastas en CABA.

Lee lo ya descargado:
  outputs/casas_pastas_google_places/google_places_deduplicado.csv
(y valida contra raw/candidatos), y genera:
  google_places_deduplicado_reclasificado.csv
  google_places_resumen_reclasificado.csv
  google_places_cambios_clasificacion.csv

NO llama a Google. NO usa API key. NO integra AGC/OSM. NO genera PDF. NO commitea.

Criterio ajustado (lo aprendido)
--------------------------------
- El universo NO es solo "fábrica de pastas" estricta: incluye casas de pastas, pastas
  frescas, pastificios, fábricas y locales de VENTA de ravioles/sorrentinos/ñoquis/
  tallarines/fideos frescos (tipo "Master Pastas"), aunque Google les ponga algún tipo
  gastronómico.
- NO descartar automáticamente por tener 'restaurant' en types.
- A: nombre claro de pastas + algún tipo de VENTA (food_store/store/manufacturer/noodle_shop...).
- B: nombre de pastas pero Google solo lo tipa como gastronómico (restaurant/meal_*),
  sin tipo de venta -> dudoso, requiere revisión manual.
- C: claramente restaurante / trattoria / bar de pasta / pasta bar / pizzería /
  gastronómico general, o sin término de pastas en el nombre.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_places_clasificador import A, B, C, RANK, clasificar, conf_integrada  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "casas_pastas_google_places"
DEDUP_IN = OUT / "google_places_deduplicado.csv"
CAND_IN = OUT / "google_places_candidatos_ampliado.csv"
RAW_IN = OUT / "google_places_raw_ampliado.json"

DEDUP_OUT = OUT / "google_places_deduplicado_reclasificado.csv"
RESUMEN_OUT = OUT / "google_places_resumen_reclasificado.csv"
CAMBIOS_OUT = OUT / "google_places_cambios_clasificacion.csv"

def main() -> int:
    if not DEDUP_IN.exists():
        print(f"ABORTADO: no existe {DEDUP_IN}. Corré primero la ampliación.")
        return 2

    # Validación de insumos (sin requests).
    raw_n = len(json.load(RAW_IN.open(encoding="utf-8"))) if RAW_IN.exists() else None
    cand_n = sum(1 for _ in csv.DictReader(CAND_IN.open(encoding="utf-8-sig"))) if CAND_IN.exists() else None
    rows = list(csv.DictReader(DEDUP_IN.open(encoding="utf-8-sig")))
    print(f"Insumos (sin requests): raw_places={raw_n} · candidatos={cand_n} · dedup_unicos={len(rows)}")

    nuevas, cambios = [], []
    for r in rows:
        anterior = r["match_casas_pastas"]
        nq = int(r.get("cantidad_queries_detectado") or 1)
        nueva, conf, motivo, rev = clasificar(r["nombre"], r["types"])
        out = dict(r)
        out["match_casas_pastas"] = nueva
        out["confianza_integrada_google"] = conf_integrada(nueva, nq)
        out["requiere_revision_manual"] = "si" if rev else "no"
        out["motivo_clasificacion"] = motivo
        nuevas.append(out)
        if nueva != anterior:
            cambios.append({
                "place_id": r["place_id"],
                "nombre": r["nombre"],
                "clasificacion_anterior": anterior,
                "clasificacion_nueva": nueva,
                "motivo_del_cambio": motivo,
                "requiere_revision_manual": "si" if rev else "no",
            })

    nuevas.sort(key=lambda x: (-RANK[x["match_casas_pastas"]], -int(x.get("cantidad_queries_detectado") or 1)))

    # Escribir reclasificado (mismas columnas que el deduplicado).
    cols = list(rows[0].keys())
    with DEDUP_OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(nuevas)

    with CAMBIOS_OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["place_id", "nombre", "clasificacion_anterior",
                                           "clasificacion_nueva", "motivo_del_cambio",
                                           "requiere_revision_manual"])
        w.writeheader()
        w.writerows(cambios)

    def cuenta(rows_, cls):
        return sum(1 for x in rows_ if x["match_casas_pastas"] == cls)

    a_new, b_new, c_new = cuenta(nuevas, A), cuenta(nuevas, B), cuenta(nuevas, C)
    a_old, b_old, c_old = cuenta(rows, A), cuenta(rows, B), cuenta(rows, C)
    b_to_a = sum(1 for x in cambios if x["clasificacion_anterior"] == B and x["clasificacion_nueva"] == A)
    b_to_c = sum(1 for x in cambios if x["clasificacion_anterior"] == B and x["clasificacion_nueva"] == C)
    b_revision = sum(1 for x in nuevas if x["match_casas_pastas"] == B)

    with RESUMEN_OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["indicador", "valor"])
        w.writerow(["fecha", dt.date.today().isoformat()])
        w.writerow(["fuente", "Google Places API (New) - AMPLIADO reclasificado (sin nuevos requests)"])
        w.writerow(["establecimientos_unicos", len(nuevas)])
        w.writerow(["A_anterior", a_old]); w.writerow(["A_nuevo", a_new])
        w.writerow(["B_anterior", b_old]); w.writerow(["B_nuevo", b_new])
        w.writerow(["C_anterior", c_old]); w.writerow(["C_nuevo", c_new])
        w.writerow(["cambios_totales", len(cambios)])
        w.writerow(["B_a_A", b_to_a])
        w.writerow(["B_a_C", b_to_c])
        w.writerow(["B_quedan_revision_manual", b_revision])

    print(f"A: {a_old} -> {a_new} | B: {b_old} -> {b_new} | C: {c_old} -> {c_new}")
    print(f"Cambios: {len(cambios)} (B->A: {b_to_a}, B->C: {b_to_c}) | B en revisión: {b_revision}")
    print(f"Archivos: {DEDUP_OUT.name}, {RESUMEN_OUT.name}, {CAMBIOS_OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
