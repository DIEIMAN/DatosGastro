"""Mide dos defectos estructurales del padron de panaderias, sobre las fuentes crudas.

A diferencia de `diagnostico_panaderias.py`, que trabaja sobre el maestro ya construido,
este relee F02 porque las preguntas son sobre columnas que el maestro no guarda.

  P1  Unidad de conteo. Hoy el maestro agrupa por partida matriz, que identifica el
      INMUEBLE, no el local. Los siete archivos legacy traen ademas `solicitud` (una
      habilitacion) y `unidad_funcional`. Cuanto cambia el universo segun con cual se
      cuente, y cuantos inmuebles del universo tienen mas de una habilitacion adentro.

  P2  Contaminacion por multi-rubro. Una habilitacion declara varios rubros a la vez
      (mediana 5). Basta que uno sea de pan para que el establecimiento entre al universo,
      aunque su giro sea supermercado, farmacia o kiosco. Cuantos son y de que giro.

No escribe nada fuera de outputs/panaderias/analisis/ y no consulta nada externo. El
archivo 2025 (esquema moderno) no tiene `solicitud`, asi que queda fuera de esta medicion:
aporta 66 establecimientos del universo A y se cuenta aparte.

Uso:
  .venv/Scripts/python.exe scripts/panaderias/diagnostico_unidad_de_conteo.py
"""
from __future__ import annotations

import csv
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))
from panaderias_patterns import classify  # noqa: E402
from scripts.shared.fuentes_locales.f02 import (  # noqa: E402
    _fila_canonica, _tomar, detectar_dialecto, listar_archivos_f02)

ANA = ROOT / "outputs" / "panaderias" / "analisis"

# Giros que, conviviendo en la misma habilitacion, indican que el pan es accesorio.
OTRO_GIRO = re.compile(
    r"supermercado|autoservicio|hipermercado|farmacia|estacion de servicio|"
    r"golosinas envasadas|kiosco|gimnasio|cerrajeria|ferreteria|libreria|papeleria|"
    r"juguet|mueble|iluminacion|bazar|deposito|lavadero|peluqueria|veterinaria|"
    r"indumentaria|calzado|joyeria|optica|inmobiliaria|oficina comercial")


def norm(v: object) -> str:
    t = unicodedata.normalize("NFKD", str(v or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t)).strip()


def write_csv(name: str, rows: list[dict], cols: list[str]) -> None:
    ANA.mkdir(parents=True, exist_ok=True)
    with (ANA / name).open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def leer_legacy() -> list[dict]:
    filas = []
    for p in listar_archivos_f02():
        d = detectar_dialecto(p)
        if d.esquema != "legacy":
            continue
        with open(p, encoding=d.codificacion, errors="replace", newline="") as fh:
            for fila in csv.DictReader(fh, delimiter=d.delimitador):
                can = _fila_canonica(fila)
                rubro = (_tomar(can, "descripcion_rubro") + " "
                         + _tomar(can, "descripcion_sub_rubro")).strip()
                if not rubro:
                    continue
                filas.append({
                    "solicitud": _tomar(can, "solicitud"),
                    "partida": _tomar(can, "partida_matriz"),
                    "unidad": _tomar(can, "unidad_funcional", "partida_horizontal"),
                    "domicilio": _tomar(can, "calles").split(";")[0],
                    "rubro": rubro,
                    "nivel": classify(rubro)["nivel"],
                    "patron": classify(rubro)["patron_detectado"],
                    "periodo": d.periodo,
                })
    return filas


def main():
    filas = leer_legacy()
    print("filas legacy con rubro:", len(filas))

    por_sol, por_part, por_su = defaultdict(list), defaultdict(list), defaultdict(list)
    for f in filas:
        if f["solicitud"]:
            por_sol[f["solicitud"]].append(f)
            por_su[(f["solicitud"], f["unidad"])].append(f)
        if f["partida"]:
            por_part[f["partida"]].append(f)

    def universo(g):
        return {k: v for k, v in g.items() if any(x["nivel"] == "A" for x in v)}

    u_sol, u_part, u_su = universo(por_sol), universo(por_part), universo(por_su)

    # --- P1 -----------------------------------------------------------------------
    multi = {p: len({x["solicitud"] for x in v if x["solicitud"]}) for p, v in u_part.items()}
    con_varias = sum(1 for c in multi.values() if c > 1)
    print()
    print("P1 - unidad de conteo (archivos legacy, universo A)")
    print("   por partida matriz (lo que usa el maestro hoy) : %d" % len(u_part))
    print("   por solicitud (una habilitacion = un local)    : %d" % len(u_sol))
    print("   por solicitud + unidad funcional               : %d" % len(u_su))
    print("   inmuebles del universo con mas de una habilitacion adentro: %d de %d (%.1f %%)"
          % (con_varias, len(u_part), 100.0 * con_varias / max(1, len(u_part))))

    write_csv("p1_unidad_de_conteo.csv", [
        {"unidad_de_conteo": "partida matriz (actual)", "establecimientos": len(u_part),
         "nota": "identifica el inmueble; fusiona locales distintos del mismo edificio"},
        {"unidad_de_conteo": "solicitud", "establecimientos": len(u_sol),
         "nota": "una habilitacion = un local; disponible solo en los 7 archivos legacy"},
        {"unidad_de_conteo": "solicitud + unidad funcional", "establecimientos": len(u_su),
         "nota": "maxima desagregacion disponible"},
    ], ["unidad_de_conteo", "establecimientos", "nota"])

    write_csv("p1_inmuebles_con_varias_habilitaciones.csv",
              [{"partida_matriz": p, "habilitaciones_distintas": c,
                "domicilio": u_part[p][0]["domicilio"]}
               for p, c in sorted(multi.items(), key=lambda kv: -kv[1]) if c > 1],
              ["partida_matriz", "habilitaciones_distintas", "domicilio"])

    # --- P2 -----------------------------------------------------------------------
    detalle, conteo_giro = [], Counter()
    for sol, v in u_sol.items():
        patrones = {x["patron"] for x in v if x["nivel"] == "A"}
        grupo = "elaboracion" if any(p != "despacho_de_pan" for p in patrones) else "solo_despacho"
        otros = sorted({x["rubro"] for x in v if OTRO_GIRO.search(norm(x["rubro"]))})
        if otros:
            for o in otros:
                conteo_giro[OTRO_GIRO.search(norm(o)).group(0)] += 1
        detalle.append({
            "solicitud": sol, "domicilio": v[0]["domicilio"], "partida_matriz": v[0]["partida"],
            "grupo_pan": grupo, "rubros_en_la_habilitacion": len({x["rubro"] for x in v}),
            "giro_ajeno": "si" if otros else "no",
            "giro_ajeno_detectado": otros[0][:80] if otros else "",
        })

    cont = [d for d in detalle if d["giro_ajeno"] == "si"]
    print()
    print("P2 - contaminacion por multi-rubro (universo A por solicitud, n=%d)" % len(u_sol))
    print("   con un giro ajeno en la misma habilitacion: %d (%.1f %%)"
          % (len(cont), 100.0 * len(cont) / max(1, len(u_sol))))
    for grupo in ("elaboracion", "solo_despacho"):
        sub = [d for d in detalle if d["grupo_pan"] == grupo]
        c = sum(1 for d in sub if d["giro_ajeno"] == "si")
        print("     %-14s total %4d | con giro ajeno %4d (%.1f %%)"
              % (grupo, len(sub), c, 100.0 * c / max(1, len(sub))))
    print("   giros detectados:")
    for g, c in conteo_giro.most_common(10):
        print("     %-24s %4d" % (g, c))
    tam = sorted(d["rubros_en_la_habilitacion"] for d in detalle)
    print("   rubros distintos por habilitacion: mediana %d | max %d"
          % (tam[len(tam) // 2], tam[-1]))

    write_csv("p2_contaminacion_multirubro.csv",
              sorted(detalle, key=lambda d: (d["giro_ajeno"] != "si", d["grupo_pan"])),
              ["solicitud", "domicilio", "partida_matriz", "grupo_pan",
               "rubros_en_la_habilitacion", "giro_ajeno", "giro_ajeno_detectado"])

    print()
    print("CSV en", ANA)


if __name__ == "__main__":
    main()
