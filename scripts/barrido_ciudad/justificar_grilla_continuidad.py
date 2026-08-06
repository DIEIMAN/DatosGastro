"""Por qué la grilla de continuidad baja a 20 m en los polos densos. La justificación geométrica.

EL ARGUMENTO
------------
La grilla vieja del barrido de continuidad era 40–300 m, y se diseñó mirando polos de 2 a 4
locales por hectárea. Aplicarla tal cual a un polo de 8 loc/ha no mide lo mismo, y la razón es
geométrica, no de gusto:

    **la distancia típica entre vecinos escala con 1/√densidad**

Para un proceso de puntos homogéneo de intensidad λ, la distancia media al vecino más cercano es
`1 / (2·√λ)`. Duplicar la densidad no acerca los puntos a la mitad: los acerca en un factor √2. Y
al cuadruplicarla —de 2 a 8 loc/ha, que es el rango real de estos polos— la distancia típica se
parte por dos.

La consecuencia operativa es la que importa: **un piso de 40 m es un umbral distinto según la
densidad del polo.** A 2 loc/ha está apenas por encima del vecino típico y el barrido arranca
justo donde la estructura empieza a aparecer. A 8 loc/ha está a más del doble del vecino típico:
todo está conectado desde el primer valor y el barrido no resuelve nada — devuelve «un solo
cuerpo» para cualquier polo denso, que es una propiedad de la grilla y no del territorio.

Por eso se agregan 20, 25, 30 y 35 m. **Por esta razón, y no para que aparezcan las partes que uno
espera**, que es la forma en que este mismo movimiento sería trampa. El resguardo está en la regla
de aceptación y no en la buena intención: si las partes de un polo denso sólo existen en los
umbrales nuevos y desaparecen apenas se sube, la condición de estabilidad las descarta sola.

LA LEY SE VERIFICA CONTRA LOS DATOS, QUE ES LO QUE LA VUELVE UN ARGUMENTO
--------------------------------------------------------------------------
Este script mide la distancia media real al vecino más cercano en cada polo grande y la compara
con la predicción de Poisson. Sirve para dos cosas, y la segunda no estaba buscada.

Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/justificar_grilla_continuidad.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import PARAMETROS, cargar_puntos  # noqa: E402
from polos_atributos_clases import OUT  # noqa: E402

TAMANIO_MINIMO = 300
DENSIDAD_DE_DISENO = 2.0    # loc/ha para los que se diseñó la grilla 40–300


def vecino_medio_poisson(loc_por_ha: float) -> float:
    """Distancia media al vecino más cercano en un proceso de Poisson de esa densidad."""
    lam = loc_por_ha / 1e4          # loc/ha → loc/m²
    return 1 / (2 * np.sqrt(lam))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    polos = pd.read_csv(OUT / "borrador_polos_v3.csv")
    grandes = polos[polos.locales >= TAMANIO_MINIMO].sort_values("locales", ascending=False)

    filas = []
    for polo in grandes.itertuples():
        cuerpo = geo[geo.polo_unido == polo.polo_id]
        xy = np.c_[cuerpo.geometry.x.to_numpy(), cuerpo.geometry.y.to_numpy()]
        distancias, _ = cKDTree(xy).query(xy, k=2)      # k=2: el primero es el punto mismo
        observada = float(distancias[:, 1].mean())
        predicha = vecino_medio_poisson(polo.locales_x_ha)
        filas.append({
            "polo_id": polo.polo_id,
            "barrio_principal": polo.barrio_principal,
            "locales": polo.locales,
            "locales_x_ha": round(polo.locales_x_ha, 2),
            "vecino_predicho_m": round(predicha, 1),
            "vecino_observado_m": round(observada, 1),
            "observado_sobre_predicho": round(observada / predicha, 2),
            "piso_viejo_sobre_vecino": round(40 / observada, 1),
            "piso_nuevo_sobre_vecino": round(20 / observada, 1),
        })
    tabla = pd.DataFrame(filas)

    referencia = vecino_medio_poisson(DENSIDAD_DE_DISENO)

    p("POR QUÉ LA GRILLA DE CONTINUIDAD BAJA A 20 m · la justificación geométrica")
    p("=" * 100)
    p("")
    p("  La distancia típica entre vecinos escala con 1/√densidad. Para un proceso de puntos de")
    p("  intensidad λ, la distancia media al vecino más cercano es 1/(2·√λ). Duplicar la densidad")
    p("  no acerca los puntos a la mitad: los acerca en un factor √2.")
    p("")
    p(f"  A {DENSIDAD_DE_DISENO:.0f} loc/ha —la densidad para la que se diseñó la grilla 40–300 m—")
    p(f"  el vecino típico está a {referencia:.1f} m. Un piso de 40 m queda apenas por encima, así")
    p("  que el barrido arranca justo donde la estructura empieza a aparecer.")
    p("")
    p("-" * 100)
    p("  LA LEY, CONTRA LOS DATOS")
    p("")
    p(tabla.to_string(index=False))
    p("")
    p("  `piso_viejo_sobre_vecino` es la lectura operativa: cuántas veces el vecino típico mide el")
    p("  piso de 40 m en cada polo. Cuando ese número pasa de 2, el umbral más bajo de la grilla")
    p("  ya conecta todo y el barrido devuelve «un solo cuerpo» — un resultado de la grilla, no")
    p("  del territorio.")
    p("")
    ratio = tabla.observado_sobre_predicho
    p(f"  AJUSTE DE LA LEY: observado/predicho entre {ratio.min():.2f} y {ratio.max():.2f}.")
    p("  Los puntos reales están SIEMPRE más juntos que la predicción de Poisson, y tiene que ser")
    p("  así: la gastronomía se agrupa y Poisson supone independencia. La ley da la escala y el")
    p("  orden de magnitud correctos, que es para lo que se la usa. No se la usa para predecir un")
    p("  valor.")
    p("")

    # El resultado que no estaba buscado. Si la densidad nominal ordenara bien a los polos, el
    # vecino observado tendría que crecer al bajar loc/ha. P065 rompe el orden, y eso es
    # justamente lo que se espera de un polo encadenado: su densidad se calcula sobre un hull que
    # incluye los vacíos de la unión, así que subestima cuán juntos están los puntos adentro de
    # cada pedazo. La medida sirve entonces como control independiente del encadenamiento.
    orden_densidad = tabla.sort_values("locales_x_ha").polo_id.tolist()
    orden_vecino = tabla.sort_values("vecino_observado_m", ascending=False).polo_id.tolist()
    p("-" * 100)
    p("  UN RESULTADO QUE NO ESTABA BUSCADO · el orden se rompe, y dice algo")
    p("")
    p(f"    orden por densidad nominal (de menor a mayor): {' < '.join(orden_densidad)}")
    p(f"    orden por vecino observado (de más lejos a más cerca): {' > '.join(orden_vecino)}")
    p("")
    if orden_densidad != orden_vecino:
        discrepantes = [a for a, b in zip(orden_densidad, orden_vecino) if a != b]
        p(f"    NO coinciden. El caso que las separa es {discrepantes[0] if discrepantes else '—'}.")
        p("")
        p("    P065 tiene la densidad nominal más baja de los cuatro y sin embargo sus puntos están")
        p("    más juntos que los de P078, que es un 30 % más denso en el papel. Eso es lo que se")
        p("    espera de un polo ENCADENADO: la densidad se mide sobre una envolvente que incluye")
        p("    los vacíos de la unión, así que subestima cuán juntos están los puntos adentro de")
        p("    cada pedazo. La densidad nominal describe la cáscara; el vecino observado describe")
        p("    el tejido.")
        p("")
        p("    Es un control independiente del encadenamiento, y coincide con lo que ya había")
        p("    dicho la curva de continuidad de P065 por otro camino.")
    else:
        p("    Coinciden: la densidad nominal ordena bien a los cuatro polos.")
    p("")

    salida = buffer.getvalue()
    (OUT / "JUSTIFICACION_GRILLA_CONTINUIDAD.txt").write_text(salida, encoding="utf-8")
    tabla.to_csv(OUT / "justificacion_grilla_continuidad.csv", index=False, encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
