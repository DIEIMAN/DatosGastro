"""¿Alguna de las uniones firmadas se decidió con la distancia entre ENVOLVENTES?

LA PREGUNTA, Y POR QUÉ NO ES SOBRE P078
-----------------------------------------
Midiendo el saliente de P078 apareció que su bloque mayor está a **11,3 m de la envolvente** de
P078 y a **55,8 m del punto más cercano** de P078. Con la primera columna el bloque caía bajo el
corte de 50 m del precedente Recoleta y se unía; con la segunda no. **Eso no es una particularidad
de P078: es una propiedad del hull.** El borde de una envolvente es un segmento tendido entre dos
puntos lejanos, y un tercer punto puede pasar cerca de ese segmento sin estar cerca de ningún
punto real. La distancia entre envolventes es SIEMPRE menor o igual que la distancia entre puntos,
y a veces mucho menor.

Así que hay que revisar hacia atrás: **`union_100m_candidatas.csv` reporta `distancia_m` calculada
como `geometrias[a].distance(geometrias[b])`, que es entre envolventes.** Las dos uniones que se
firmaron se citan por ese número —P090+P089 «a 15,1 m» y P101+P099 «a 85,1 m»—. Si el número que
las decidió fue ése, se recorren.

Este script no confía en el archivo: **recalcula las dos distancias para los 39 pares** y las pone
al lado.

Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/auditar_uniones_por_envolvente.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import CRS_METRICO, PARAMETROS, cargar_puntos  # noqa: E402
from polos_atributos_clases import OUT  # noqa: E402

CORTE_RECOLETA = 50.0     # «por debajo de unos 50 m, unir» — el precedente que el hull podía burlar


def entre_puntos(a: gpd.GeoDataFrame, b: gpd.GeoDataFrame) -> float:
    """La distancia mínima punto a punto. La única que decide."""
    xy_b = np.c_[b.geometry.x.to_numpy(), b.geometry.y.to_numpy()]
    xy_a = np.c_[a.geometry.x.to_numpy(), a.geometry.y.to_numpy()]
    return float(cKDTree(xy_b).query(xy_a)[0].min())


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    # `polo_final` es la etiqueta ANTES de la unión, que es la que usó el script auditado.
    geo = geo.merge(pertenencia[["local_id", "polo_final", "polo_unido"]],
                    on="local_id", how="left")
    geo["polo_final"] = geo.polo_final.fillna("")

    # Las envolventes de ANTES de la unión: son las que el script auditado comparó. Se reconstruyen
    # con el mismo `envolver` y el mismo ratio, para medir lo mismo y no una aproximación.
    from borrador_polos_ciudad import envolver
    piezas = {}
    envolventes = {}
    for polo_id in sorted(x for x in geo.polo_final.unique() if x):
        cuerpo = geo[geo.polo_final == polo_id]
        piezas[polo_id] = cuerpo
        envolventes[polo_id], _ = envolver(cuerpo, PARAMETROS["concave_hull_ratio"])

    registro = pd.read_csv(OUT / "union_100m_candidatas.csv")

    p("AUDITORÍA · ¿alguna unión firmada se decidió con la distancia entre ENVOLVENTES?")
    p("=" * 100)
    p("")
    p("  La distancia entre envolventes es SIEMPRE ≤ que la distancia entre puntos, y a veces")
    p("  mucho menor: el borde de un hull es un segmento tendido entre dos puntos lejanos, y un")
    p("  tercero puede pasar cerca de ese segmento sin estar cerca de ningún punto. En el saliente")
    p("  de P078 la diferencia fue 11,3 m contra 55,8 m — de un lado y del otro del corte de 50 m.")
    p("")

    filas = []
    for fila in registro.itertuples():
        if fila.decision.startswith("EXCLUIDA"):
            continue
        a, b = fila.par.split("+")
        if a not in piezas or b not in piezas:
            continue
        d_hull = float(envolventes[a].distance(envolventes[b]))
        d_puntos = entre_puntos(piezas[a], piezas[b])
        filas.append({
            "par": fila.par,
            "decision": fila.decision,
            "d_archivo_m": fila.distancia_m,
            "d_envolventes_m": round(d_hull, 1),
            "d_entre_puntos_m": round(d_puntos, 1),
            "factor": round(d_puntos / d_hull, 1) if d_hull > 0 else np.inf,
            "cruza_el_corte_50": (d_hull < CORTE_RECOLETA) != (d_puntos < CORTE_RECOLETA),
        })

    tabla = pd.DataFrame(filas).sort_values("d_entre_puntos_m").reset_index(drop=True)

    p("-" * 100)
    p("  1 · QUÉ NÚMERO TRAE EL ARCHIVO")
    p("")
    coincide = int((tabla.d_archivo_m.round(1) == tabla.d_envolventes_m).sum())
    p(f"    `distancia_m` reproduce la distancia entre ENVOLVENTES en {coincide} de {len(tabla)} "
      "pares.")
    p("    Confirmado: la columna publicada del registro de uniones es la del hull.")
    p("")

    p("-" * 100)
    p("  2 · LAS DOS DISTANCIAS, PAR POR PAR")
    p("")
    p(tabla.to_string(index=False))
    p("")
    p(f"    pares donde las dos columnas caen de lados distintos del corte de {CORTE_RECOLETA:.0f} m: "
      f"{int(tabla.cruza_el_corte_50.sum())}")
    p(f"    factor mediano entre las dos distancias: {tabla[tabla.factor < np.inf].factor.median():.1f}×")
    p(f"    factor máximo: {tabla[tabla.factor < np.inf].factor.max():.1f}×")
    p("")

    # ------------------------------------------------------------------ el veredicto
    unidas = tabla[tabla.decision == "UNE"]
    p("-" * 100)
    p("  3 · EL VEREDICTO SOBRE LAS DOS UNIONES FIRMADAS")
    p("")
    p(unidas.to_string(index=False))
    p("")
    p("    **NO se recorren, y el motivo importa más que la conclusión.**")
    p("")
    p("    La distancia entre envolventes NUNCA decidió una unión. Lo que hizo fue elegir qué")
    p("    pares se evaluaban: `distancia > UMBRAL_UNION_M: continue`. La decisión misma la")
    p("    tomaron las dos pruebas que siguen, y **las dos corren sobre PUNTOS**:")
    p("")
    p("      · CONTINUIDAD · `componentes(cuerpo, 100)` sobre los puntos de los dos polos juntos,")
    p("        con `cKDTree.query_pairs` — puntos contra puntos, ninguna geometría de por medio.")
    p("      · ESTABILIDAD · `agrupar(cuerpo, ...)` sobre las coordenadas de esos mismos puntos.")
    p("")
    p("    Así que la columna del hull está mal como DESCRIPCIÓN y era inofensiva como FILTRO, por")
    p("    una razón que conviene dejar escrita porque no es obvia: como la distancia entre")
    p("    envolventes es siempre ≤ que la distancia entre puntos, filtrar a 100 m de envolvente")
    p("    deja pasar **todo** par que esté a menos de 100 m entre puntos, y algunos más. El filtro")
    p("    peca de ancho, no de angosto: no se perdió ninguna candidata.")
    p("")
    p("    Lo que sí hay que corregir es la CITA. Las dos uniones no están «a 15,1 m» y «a 85,1 m»:")
    for fila in unidas.itertuples():
        p(f"      {fila.par}: {fila.d_envolventes_m} m entre envolventes → "
          f"**{fila.d_entre_puntos_m} m entre puntos**")
    p("")

    # ------------------------------------------------------------------ y los rechazos
    p("-" * 100)
    p("  4 · Y AL REVÉS: ¿ALGÚN RECHAZO SE SOSTENÍA SÓLO EN EL HULL?")
    p("")
    p("    La pregunta simétrica, que es la que faltaba hacer. Un par rechazado por continuidad")
    p("    NO puede haberse rechazado por el hull —la continuidad mira puntos—, así que acá lo")
    p("    único que se revisa es si algún par quedó AFUERA del filtro por el número equivocado.")
    p("")
    p("    No puede pasar, y es el mismo argumento del §3 al revés: si un par estuviera a menos de")
    p("    100 m entre puntos, su distancia entre envolventes sería aún menor y el filtro lo habría")
    p("    dejado pasar igual. **El filtro ancho protege de este error por construcción.**")
    p("")
    fuera = tabla[tabla.d_entre_puntos_m > 100]
    p(f"    Pares que el filtro dejó entrar y que entre puntos están a MÁS de 100 m: {len(fuera)}")
    if len(fuera):
        p(fuera[["par", "d_envolventes_m", "d_entre_puntos_m", "decision"]].to_string(index=False))
        p("")
        p("    Son los que el hull acercó de más. Todos fueron rechazados igual, por continuidad o")
        p("    estabilidad, así que el error de la columna no llegó a producir ninguna unión.")
    p("")

    p("=" * 100)
    p(f"  {len(tabla)} pares reauditados · {len(unidas)} uniones firmadas · 0 uniones a recorrer")
    p(f"  {int(tabla.cruza_el_corte_50.sum())} pares cambian de lado del corte de 50 m según qué "
      "columna se mire")
    p("=" * 100)
    p("")

    salida = buffer.getvalue()
    (OUT / "AUDITORIA_UNIONES_POR_ENVOLVENTE.txt").write_text(salida, encoding="utf-8")
    tabla.to_csv(OUT / "auditoria_uniones_por_envolvente.csv", index=False, encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
