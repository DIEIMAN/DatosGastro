"""Auditoría de cobertura (SIN nuevos requests) sobre el consolidado de Google Places.

Objetivo: antes de integrar AGC+OSM+Google, validar que no estemos perdiendo casas/
fábricas/locales de venta de pastas relevantes (cadenas y marcas conocidas), sin meter
restaurantes puros.

Lee:
  google_places_consolidado_deduplicado.csv (+ resumen + calidad)
Genera en revision_cobertura_google/:
  revision_B_google.csv
  revision_C_con_senal_pastas.csv
  revision_marcas_conocidas.csv
  revision_sucursales_detectadas.csv
  revision_posibles_faltantes_por_barrio.csv
  resumen_revision_cobertura.csv

NO llama a Google. NO usa API key. NO integra AGC/OSM. NO genera PDF. NO commitea.
"""
from __future__ import annotations

import csv
import datetime as dt
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_places_clasificador import (  # noqa: E402
    A, B, C, MARCAS_ESPERADAS, PRODUCTO, RETAIL_TYPES, es_restaurante_puro,
    norm_nombre, strip_acc,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "casas_pastas_google_places"
REV = OUT / "revision_cobertura_google"
CONS = OUT / "google_places_consolidado_deduplicado.csv"

# Tipos de "venta" que distinguen un local de un restaurante puro.
VENTA_TYPES = RETAIL_TYPES  # food_store, store, manufacturer, noodle_shop, deli, etc.


def na(s: str) -> str:
    return norm_nombre(s)


def tiene_producto(nombre: str) -> bool:
    n = na(nombre)
    return any(strip_acc(k) in n for k in PRODUCTO)


def tipos_set(types_str: str) -> set[str]:
    return {t.strip().lower() for t in (types_str or "").split(";") if t.strip()}


def w(path: Path, cols: list[str], rows: list[dict]) -> None:
    REV.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(rows)


def main() -> int:
    if not CONS.exists():
        print(f"ABORTADO: no existe {CONS}. Corré primero la consolidación.")
        return 2
    rows = list(csv.DictReader(CONS.open(encoding="utf-8-sig")))
    print(f"Consolidado leído: {len(rows)} establecimientos únicos (sin requests).")

    # ---------- 1. Todos los B ----------
    b_rows = []
    for r in rows:
        if r["match_casas_pastas"] != B:
            continue
        tset = tipos_set(r["types"])
        venta = bool(tset & VENTA_TYPES)
        decision = "mantener_B_revision_manual"
        motivo = ("nombre de pastas pero Google solo lo tipa como gastronómico/no-venta; "
                  "verificar manualmente si es local de venta o restaurante")
        b_rows.append({
            "place_id": r["place_id"], "nombre": r["nombre"], "direccion": r["direccion"],
            "types": r["types"], "tiene_tipo_venta": "si" if venta else "no",
            "decision_revision": decision, "motivo_revision": motivo,
        })

    # ---------- 2. C con señal de posible casa de pastas (nombre o tipo de venta) ----------
    c_signal = []
    for r in rows:
        if r["match_casas_pastas"] != C:
            continue
        n = na(r["nombre"])
        tset = tipos_set(r["types"])
        prod = tiene_producto(r["nombre"])
        venta = bool(tset & VENTA_TYPES)
        resto = es_restaurante_puro(n)
        if not (prod or venta):
            continue  # sin señal real (query_origen se ignora: todas eran de pastas)
        if resto:
            decision, motivo = "mantener_C", "el nombre delata restaurante/bar/trattoria/pizzería"
        elif venta and not prod:
            decision = "posible_faltante_buscar"
            motivo = ("local de alimentos (tipo de venta) sin término de pastas en el nombre; "
                      "podría ser casa de pastas con nombre genérico: verificar")
        elif prod and venta:
            decision, motivo = "posible_faltante_buscar", "producto de pastas + tipo de venta; revisar por qué quedó C"
        else:
            decision, motivo = "mantener_C", "señal débil; sin tipo de venta"
        c_signal.append({
            "place_id": r["place_id"], "nombre": r["nombre"], "direccion": r["direccion"],
            "types": r["types"], "producto_en_nombre": "si" if prod else "no",
            "tipo_venta": "si" if venta else "no", "parece_restaurante": "si" if resto else "no",
            "decision_revision": decision, "motivo_revision": motivo,
        })

    # ---------- 3. Marcas conocidas (filas que matchean) ----------
    marcas_rows = []
    for r in rows:
        n = na(r["nombre"])
        for marca, claves in MARCAS_ESPERADAS.items():
            if any(k in n for k in claves):
                cls = r["match_casas_pastas"]
                if cls == A:
                    dec, mot = "mantener_A", "marca conocida ya clasificada como probable casa de pastas"
                elif cls == B:
                    dec, mot = "mantener_B_revision_manual", "marca conocida en B: revisar para promover"
                else:
                    dec, mot = "posible_faltante_buscar", "marca conocida quedó en C: revisar/buscar dirigido"
                marcas_rows.append({
                    "marca": marca, "place_id": r["place_id"], "nombre": r["nombre"],
                    "direccion": r["direccion"], "match_casas_pastas": cls,
                    "decision_revision": dec, "motivo_revision": mot,
                })
                break

    # ---------- 4/5. Sucursales por cadena (marcas + nombres repetidos) ----------
    suc_rows = []
    # marcas conocidas
    for marca, claves in MARCAS_ESPERADAS.items():
        hits = [r for r in rows if any(k in na(r["nombre"]) for k in claves)]
        if hits:
            cc = Counter(h["match_casas_pastas"][0] for h in hits)
            suc_rows.append({
                "cadena": marca, "tipo": "marca_conocida", "sucursales": len(hits),
                "A": cc.get("A", 0), "B": cc.get("B", 0), "C": cc.get("C", 0),
                "ejemplos": " | ".join(sorted({h["nombre"] for h in hits})[:5]),
            })
    # nombres repetidos (cadenas no listadas), solo A/B
    by_name = defaultdict(list)
    for r in rows:
        if r["match_casas_pastas"] == C:
            continue
        by_name[na(r["nombre"])].append(r)
    listadas = {k for cl in MARCAS_ESPERADAS.values() for k in cl}
    for nm, hits in by_name.items():
        if len(hits) >= 2 and not any(k in nm for k in listadas):
            cc = Counter(h["match_casas_pastas"][0] for h in hits)
            suc_rows.append({
                "cadena": nm, "tipo": "nombre_repetido", "sucursales": len(hits),
                "A": cc.get("A", 0), "B": cc.get("B", 0), "C": cc.get("C", 0),
                "ejemplos": " | ".join(sorted({h["nombre"] for h in hits})[:5]),
            })
    suc_rows.sort(key=lambda x: -x["sucursales"])

    # ---------- 6. Marcas esperadas: presente / subrepresentada / ausente ----------
    faltantes_marca = []
    for marca, claves in MARCAS_ESPERADAS.items():
        hits = [r for r in rows if any(k in na(r["nombre"]) for k in claves)]
        n_a = sum(1 for h in hits if h["match_casas_pastas"] == A)
        if not hits:
            status, dec = "ausente", "posible_faltante_buscar"
        elif n_a <= 1:
            status, dec = "subrepresentada", "posible_faltante_buscar"
        else:
            status, dec = "presente", "mantener_A"
        faltantes_marca.append({
            "marca": marca, "sucursales": len(hits), "sucursales_A": n_a,
            "status": status, "decision_revision": dec,
        })

    # ---------- Cobertura por barrio (queries 'casa de pastas <barrio>') ----------
    barrio_cnt: dict[str, int] = defaultdict(int)
    for r in rows:
        if r["match_casas_pastas"] != A:
            continue
        for q in r["queries_detectado"].split(";"):
            qn = q.strip().lower()
            m = re.match(r"casa de pastas (.+)", qn)
            if m:
                barrio_cnt[m.group(1).strip().title()] += 1
    barrio_rows = []
    for barrio, n in sorted(barrio_cnt.items(), key=lambda x: x[1]):
        dec = "posible_faltante_buscar" if n <= 2 else "ok"
        barrio_rows.append({
            "barrio": barrio, "casas_pastas_A_detectadas": n,
            "cobertura": "baja" if n <= 2 else "media/alta",
            "decision_revision": dec,
        })

    # ---------- Escritura ----------
    w(REV / "revision_B_google.csv",
      ["place_id", "nombre", "direccion", "types", "tiene_tipo_venta",
       "decision_revision", "motivo_revision"], b_rows)
    w(REV / "revision_C_con_senal_pastas.csv",
      ["place_id", "nombre", "direccion", "types", "producto_en_nombre", "tipo_venta",
       "parece_restaurante", "decision_revision", "motivo_revision"], c_signal)
    w(REV / "revision_marcas_conocidas.csv",
      ["marca", "place_id", "nombre", "direccion", "match_casas_pastas",
       "decision_revision", "motivo_revision"], marcas_rows)
    w(REV / "revision_sucursales_detectadas.csv",
      ["cadena", "tipo", "sucursales", "A", "B", "C", "ejemplos"], suc_rows)
    w(REV / "revision_posibles_faltantes_por_barrio.csv",
      ["barrio", "casas_pastas_A_detectadas", "cobertura", "decision_revision"], barrio_rows)

    c_promover = sum(1 for x in c_signal if x["decision_revision"] == "posible_faltante_buscar")
    ausentes = [m["marca"] for m in faltantes_marca if m["status"] == "ausente"]
    subrep = [m["marca"] for m in faltantes_marca if m["status"] == "subrepresentada"]
    resumen = [
        {"indicador": "fecha", "valor": dt.date.today().isoformat()},
        {"indicador": "establecimientos_unicos", "valor": len(rows)},
        {"indicador": "B_a_revisar", "valor": len(b_rows)},
        {"indicador": "C_con_senal_pastas", "valor": len(c_signal)},
        {"indicador": "C_posible_faltante_buscar", "valor": c_promover},
        {"indicador": "marcas_esperadas_total", "valor": len(MARCAS_ESPERADAS)},
        {"indicador": "marcas_ausentes", "valor": "; ".join(ausentes) or "(ninguna)"},
        {"indicador": "marcas_subrepresentadas", "valor": "; ".join(subrep) or "(ninguna)"},
        {"indicador": "cadenas_detectadas", "valor": len(suc_rows)},
        {"indicador": "barrios_cobertura_baja",
         "valor": "; ".join(b["barrio"] for b in barrio_rows if b["cobertura"] == "baja") or "(ninguno)"},
    ]
    w(REV / "resumen_revision_cobertura.csv", ["indicador", "valor"], resumen)
    # marcas detalle como archivo extra dentro de la misma carpeta
    w(REV / "revision_marcas_esperadas_status.csv",
      ["marca", "sucursales", "sucursales_A", "status", "decision_revision"], faltantes_marca)

    print(f"B a revisar: {len(b_rows)} | C con señal: {len(c_signal)} (posible_faltante: {c_promover})")
    print(f"Marcas ausentes: {ausentes or '(ninguna)'}")
    print(f"Marcas subrepresentadas: {subrep or '(ninguna)'}")
    print(f"Cadenas detectadas: {len(suc_rows)} | barrios cobertura baja: "
          f"{[b['barrio'] for b in barrio_rows if b['cobertura'] == 'baja']}")
    print(f"Salidas en: {REV.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
