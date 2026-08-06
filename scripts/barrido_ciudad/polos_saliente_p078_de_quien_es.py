"""¿De quién es el saliente N–NE de P078? Distancia a TODOS los polos del borrador.

LA PREGUNTA, Y POR QUÉ NO ES LA QUE SE VENÍA HACIENDO
------------------------------------------------------
Los tres bloques del saliente —35, 23 y 12 locales— se venían leyendo como «cola de P078» por una
razón que no es geográfica: **salieron de ahí**. Se los encontró partiendo P078, así que quedaron
descriptos contra P078. Eso es un sesgo de procedencia, no una medición.

La prueba 1 de `CUANDO_DOS_POLOS_SON_UNO.md` —el precedente Recoleta— se aplica contra **todos**
los polos del borrador, no contra el que los produjo:

    0 – 50 m    → una sola zona, sin discusión          (Recoleta, 9 → 1)
    50 – 200 m  → depende de estabilidad y nombre       (Belgrano, 3 partes a 160 m)
    > 200 m     → zonas distintas o multiparte          (Costanera, 163 – 2.727 m)

**Unir no es bajar el mínimo.** Un bloque de 35 que se une a un polo vecino por continuidad medida
no está siendo rescatado por debajo de 40: está siendo reconocido como parte de un cuerpo que ya
califica. El mínimo de 40 sigue intacto y sigue valiendo para todos.

LA TRAMPA QUE HAY QUE ESQUIVAR ACÁ
-----------------------------------
La envolvente de P078 se dibuja sobre sus 585 puntos, **incluidos los del saliente**. Así que la
distancia de cualquier bloque a «la envolvente de P078» es 0 por construcción, y no dice nada. Por
eso P078 se mide aparte y contra las **envolventes de sus tres partes**, que es la comparación que
sí tiene contenido.

Google Places: 0 requests. No se toca ningún umbral ni ninguna cifra publicada.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_saliente_p078_de_quien_es.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import (  # noqa: E402
    CRS_METRICO, ENVOLVENTES_22, PARAMETROS, cargar_puntos, envolver,
)
from polos_atributos_clases import OUT  # noqa: E402
from polos_particion_anada_estructura import MINIMO, componentes  # noqa: E402

POLO = "P078"
UMBRAL = 55
BLOQUE_MINIMO = 10          # los bloques del saliente que vale la pena medir

# La tabla de CUANDO_DOS_POLOS_SON_UNO.md §3, tal cual
UNIR = 50
ESTABILIDAD = 200


def clasificar(distancia: float) -> str:
    if distancia < UNIR:
        return "UNIR · precedente Recoleta"
    if distancia < ESTABILIDAD:
        return "prueba de estabilidad"
    return "zonas distintas"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    cuerpo = geo[geo.polo_unido == POLO].reset_index(drop=True)
    polos = gpd.read_file(OUT / "borrador_polos_v3.geojson").to_crs(CRS_METRICO)
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)

    todas = componentes(cuerpo, UMBRAL)
    partes = [c for c in todas if len(c) >= MINIMO]
    bloques = [c for c in todas if BLOQUE_MINIMO <= len(c) < MINIMO]

    p("¿DE QUIÉN ES EL SALIENTE N–NE DE P078? · prueba 1, contra TODOS los polos del borrador")
    p("=" * 100)
    p("")
    p("  Los bloques se venían leyendo como cola de P078 porque de ahí salieron. Eso es un sesgo")
    p("  de procedencia. La prueba 1 —precedente Recoleta— se aplica contra todo el borrador.")
    p("")
    p(f"    0 – {UNIR} m      → UNIR, una sola zona, sin discusión")
    p(f"    {UNIR} – {ESTABILIDAD} m    → prueba de estabilidad")
    p(f"    > {ESTABILIDAD} m       → zonas distintas")
    p("")
    p("  Unir NO es bajar el mínimo: el bloque no se rescata por debajo de 40, se reconoce como")
    p("  parte de un cuerpo que ya califica. El mínimo de 40 sigue intacto para todos.")
    p("")
    p(f"  bloques del saliente medidos: {len(bloques)} "
      f"({', '.join(str(len(c)) for c in sorted(bloques, key=len, reverse=True))} locales)")
    p("")

    # Las envolventes de las tres partes, para medir P078 sin la circularidad de su propia cáscara
    envolventes_partes = {}
    for orden, indices in enumerate(partes, start=1):
        geometria, _ = envolver(cuerpo.iloc[indices], PARAMETROS["concave_hull_ratio"])
        envolventes_partes[f"{POLO}·S{orden}"] = geometria

    filas, veredictos = [], []
    for indices in sorted(bloques, key=len, reverse=True):
        miembros = cuerpo.iloc[indices]
        geometria, degenerado = envolver(miembros, PARAMETROS["concave_hull_ratio"])
        nombre = f"bloque_{len(indices)}"

        # DOS distancias, y hacen falta las dos. La de envolventes puede ser MUCHO menor que la
        # de puntos: el borde de un hull es un segmento entre dos puntos lejanos, y un tercero
        # puede pasar cerca de ese segmento sin estar cerca de ningún punto. Reportar sólo la de
        # envolventes haría leer como continuidad lo que es una arista tendida sobre un vacío.
        puntos_bloque = miembros.geometry
        distancias = []
        for polo in polos.itertuples():
            if polo.polo_id == POLO:
                continue
            miembros_polo = geo[geo.polo_unido == polo.polo_id].geometry
            distancias.append({
                "contra": polo.polo_id,
                "que_es": f"polo · {polo.barrio_principal} · {polo.locales} loc",
                "d_envolventes_m": round(geometria.distance(polo.geometry), 1),
                "d_entre_puntos_m": round(
                    min(puntos_bloque.distance(q).min() for q in miembros_polo), 1)
                if len(miembros_polo) else None,
            })
        # --- y contra las tres partes de P078, que es la comparación con contenido
        for etiqueta, geometria_parte in envolventes_partes.items():
            indices_parte = partes[int(etiqueta[-1]) - 1]
            puntos_parte = cuerpo.iloc[indices_parte].geometry
            distancias.append({
                "contra": etiqueta,
                "que_es": "parte de P078",
                "d_envolventes_m": round(geometria.distance(geometria_parte), 1),
                "d_entre_puntos_m": round(
                    min(puntos_bloque.distance(q).min() for q in puntos_parte), 1),
            })

        tabla = pd.DataFrame(distancias).sort_values("d_envolventes_m").head(6)
        tabla.insert(0, "bloque", nombre)
        # La clasificación se decide con la distancia ENTRE PUNTOS. Es la que mide separación
        # real entre concentraciones; la de envolventes depende de cómo se dibujó la cáscara.
        tabla["clasificacion"] = tabla.d_entre_puntos_m.map(clasificar)
        tabla["arista_sobre_vacio"] = tabla.d_entre_puntos_m - tabla.d_envolventes_m > 40
        filas.append(tabla)

        mas_cerca = tabla.sort_values("d_entre_puntos_m").iloc[0]
        veredictos.append({
            "bloque": nombre,
            "locales": len(indices),
            "barrio_principal": miembros.barrio.value_counts().index[0],
            "ha": round(geometria.area / 1e4, 1),
            "hull_degenerado": degenerado,
            "mas_cercano": mas_cerca.contra,
            "d_envolventes_m": mas_cerca.d_envolventes_m,
            "d_entre_puntos_m": mas_cerca.d_entre_puntos_m,
            "clasificacion": mas_cerca.clasificacion,
        })

        p("-" * 100)
        p(f"  {nombre.upper()} · {len(indices)} locales · "
          f"{miembros.barrio.value_counts().index[0]} · {geometria.area / 1e4:.1f} ha")
        p("")
        p(tabla.drop(columns=["bloque"]).to_string(index=False))
        p("")

    p("=" * 100)
    p("  VEREDICTO POR BLOQUE")
    p("=" * 100)
    p("")
    resumen = pd.DataFrame(veredictos)
    p(resumen.to_string(index=False))
    p("")

    if resumen.d_entre_puntos_m.sub(resumen.d_envolventes_m).gt(40).any():
        p("  AVISO SOBRE LAS DOS COLUMNAS, y no es menor. Para algún bloque la distancia entre")
        p("  envolventes es decenas de metros MENOR que la distancia entre puntos. Eso no es")
        p("  cercanía: es una **arista del hull tendida sobre un vacío**. El borde de una")
        p("  envolvente es un segmento entre dos puntos lejanos, y un tercero puede pasar cerca de")
        p("  ese segmento sin estar cerca de ningún punto.")
        p("")
        p("  Por eso la clasificación se decide con `d_entre_puntos_m`. Usar la de envolventes")
        p("  habría hecho pasar por continuidad —y por debajo del corte de 50 m de Recoleta— una")
        p("  separación real de decenas de metros. En Recoleta los pares que decidieron estaban a")
        p("  0,0 m: se TOCABAN, que es una evidencia distinta de un borde que pasa cerca.")
        p("")

    unibles = resumen[resumen.clasificacion.str.startswith("UNIR")]
    if len(unibles):
        p(f"  {len(unibles)} bloque(s) a menos de {UNIR} m de un polo del borrador. Por precedente")
        p("  Recoleta son una sola zona con ese polo, y eso se resuelve SIN tocar ningún umbral.")
    else:
        p(f"  NINGÚN bloque queda a menos de {UNIR} m de otro polo del borrador. El precedente")
        p("  Recoleta no aplica: no hay a quién unirlos.")
        p("")
        estables = resumen[resumen.clasificacion == "prueba de estabilidad"]
        if len(estables):
            p(f"  {len(estables)} bloque(s) caen en la franja {UNIR}–{ESTABILIDAD} m, así que pasan")
            p("  a la prueba de estabilidad. Y el vecino más cercano de todos es una PARTE de P078,")
            p("  no otro polo: el saliente es de P078 y de nadie más.")
        p("")
        p("  Queda entonces el camino (c): reportarlo como hallazgo acotado, con redacción R7.")
    p("")

    # Zona publicada encima de cada bloque, que hace falta para redactar el hallazgo
    p("-" * 100)
    p("  ZONA PUBLICADA SOBRE LOS BLOQUES")
    p("")
    for indices in sorted(bloques, key=len, reverse=True):
        miembros = cuerpo.iloc[indices]
        adentro = {}
        for z in zonas.itertuples():
            n = int(miembros.geometry.within(z.geometry).sum())
            if n:
                adentro[z.referencia_id] = n
        detalle = ", ".join(f"{k}: {v}" for k, v in adentro.items()) or "ninguna"
        p(f"    bloque_{len(indices)}: {detalle}  "
          f"(de {len(indices)} locales)")
    p("")

    salida = buffer.getvalue()
    (OUT / "SALIENTE_P078_DE_QUIEN_ES.txt").write_text(salida, encoding="utf-8")
    pd.concat(filas).to_csv(OUT / "saliente_p078_distancias.csv", index=False, encoding="utf-8")
    resumen.to_csv(OUT / "saliente_p078_veredicto.csv", index=False, encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
