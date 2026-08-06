"""La tabla con la que una persona le pone nombre a cada uno de los 124 polos del borrador.

PARA QUÉ EXISTE
---------------
Los nombres no salen del clustering —§5 de `CRITERIOS_LECTURA_POLIGONIZACION`: «cómo se llaman»
es una de las cuatro cosas que el algoritmo explícitamente NO decide—. Lo que sí se puede hacer es
juntar, en una sola fila por polo, todo lo que hace falta para nombrarlo sin abrir el mapa: dónde
cae, sobre qué calles, qué tamaño tiene, si ya hay una zona publicada encima y cuál es su vecino.

No calcula nada nuevo ni mueve ninguna decisión: **relee lo ya decidido y lo ordena.**

TRES COSAS QUE ESTA TABLA DICE CON CUIDADO, PORQUE SE PUEDEN LEER MAL
-----------------------------------------------------------------------
1. **`calles_dominantes` no es un recuento de oferta por calle.** Es dónde caen los locales de
   este polo QUE TIENEN DIRECCIÓN, y esa fracción va al lado en `pct_locales_con_direccion`
   justamente para que no se lea como censo. Un polo con 30 % de direcciones nombra sus calles
   sobre un tercio de sus locales.
2. **`distancia_al_corte` mide distancia a una convención, no a una frontera.** El corte de
   4,58 loc/ha se eligió; no hay hueco en la distribución que lo sostenga (§1 de
   `POLOS_ATRIBUTOS_Y_PRUEBAS`). Un polo a 0,05 del corte no está «al borde de ser otra cosa»:
   está al borde de una raya que dibujamos nosotros. Por eso la columna existe — para que quien
   nombre vea cuáles son los casos donde la clase no significa nada.
3. **`d_al_vecino_entre_puntos_m` es entre PUNTOS y no entre envolventes**, y es la única
   distancia que se publica acá. La distancia entre envolventes puede ser varias veces menor que
   la distancia entre puntos —11,3 m contra 55,8 m en el saliente de P078— porque el borde de un
   hull es un segmento tendido entre dos puntos lejanos y un tercero puede pasar cerca de ese
   segmento sin estar cerca de ningún punto. Toda decisión de unir se toma entre puntos.

Y `zonas_publicadas_encima` va con los DOS porcentajes, porque la relación no es uno a uno en
ninguna de las dos direcciones: el 47,7 % de los locales de P078 cae fuera de R01, y sólo 306 de
los 1.358 locales que hay dentro de R01 son de P078.

Google Places: 0 requests. No se toca ninguna cifra publicada ni ninguna geometría.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_para_nombrar.py
"""
from __future__ import annotations

import io
import json
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

from borrador_polos_ciudad import (  # noqa: E402
    CRS_METRICO, ENVOLVENTES_22, PARAMETROS, cargar_puntos,
)
from polos_atributos_clases import OUT  # noqa: E402
from polos_foco_menor import calle  # noqa: E402

CALLES_TOP = 6
SOLAPE_MINIMO = 0.02      # por debajo de esto la zona publicada apenas roza el polo y no se lista


def formato_conteo(serie: pd.Series, tope: int | None = None) -> str:
    """«Palermo (210); Villa Crespo (44)». Separador « ; » y no coma: hay nombres con coma."""
    conteos = serie.value_counts()
    if tope is not None:
        conteos = conteos.head(tope)
    return "; ".join(f"{k} ({v})" for k, v in conteos.items())


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")

    polos = gpd.read_file(OUT / "borrador_polos_v3.geojson").to_crs(CRS_METRICO)
    atributos = pd.read_csv(OUT / "borrador_polos_v3.csv")
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)
    corte = json.loads((OUT / "parametros_v2.json").read_text(
        encoding="utf-8"))["clases_densidad"]["cortes_locales_x_ha"][0]

    asignados = geo[geo.polo_unido != ""].reset_index(drop=True)
    xy = np.c_[asignados.geometry.x.to_numpy(), asignados.geometry.y.to_numpy()]
    etiqueta = asignados.polo_unido.to_numpy()

    p("POLOS PARA NOMBRAR · una fila por polo, con todo lo que hace falta para ponerle nombre")
    p("=" * 100)
    p("")
    p(f"  {len(polos)} polos · {len(asignados)} locales asignados · borrador v3")
    p("")
    p("  El nombre NO sale de acá. Sale de una persona que lee esta fila. El §5 de")
    p("  CRITERIOS_LECTURA lista «cómo se llaman» entre las cosas que el algoritmo no decide.")
    p("")
    p("  TRES COLUMNAS QUE SE PUEDEN LEER MAL, Y CÓMO SE LEEN:")
    p("")
    p("   · calles_dominantes    — dónde caen los locales CON DIRECCIÓN, no un censo por calle.")
    p("                            La base va al lado en pct_locales_con_direccion.")
    p(f"   · distancia_al_corte   — distancia a una convención elegida ({corte:.2f} loc/ha), no a una")
    p("                            frontera del territorio: no hay hueco en la distribución.")
    p("   · d_al_vecino...       — ENTRE PUNTOS. La distancia entre envolventes no se publica acá")
    p("                            porque puede ser varias veces menor y llevar a unir de más.")
    p("")

    filas = []
    for polo in polos.itertuples():
        cuerpo = asignados[asignados.polo_unido == polo.polo_id]
        fila_atributos = atributos[atributos.polo_id == polo.polo_id].iloc[0]

        con_direccion = cuerpo.direccion_norm.dropna()
        calles = con_direccion.map(calle)
        calles = calles[calles.str.len() > 2].value_counts().head(CALLES_TOP)

        # --- zonas publicadas encima, con los dos porcentajes
        solapes = []
        for zona in zonas.itertuples():
            if not polo.geometry.intersects(zona.geometry):
                continue
            comun = polo.geometry.intersection(zona.geometry).area
            del_polo = comun / polo.geometry.area
            if del_polo < SOLAPE_MINIMO:
                continue
            solapes.append((del_polo, f"{zona.referencia_id} {zona.nombre} "
                                      f"({del_polo:.0%} del polo, {comun / zona.geometry.area:.0%} "
                                      f"de la zona)"))
        solapes.sort(reverse=True)

        # --- vecino más cercano, ENTRE PUNTOS
        propios = etiqueta == polo.polo_id
        ajenos = ~propios
        arbol = cKDTree(xy[ajenos])
        distancias, vecinos = arbol.query(xy[propios])
        i = int(np.argmin(distancias))
        vecino = etiqueta[ajenos][int(vecinos[i])]

        filas.append({
            "polo_id": polo.polo_id,
            "n_locales": len(cuerpo),
            "ha": round(fila_atributos.ha, 2),
            "locales_x_ha": round(fila_atributos.locales_x_ha, 3),
            "clase_densidad": fila_atributos.clase_densidad,
            "distancia_al_corte": round(fila_atributos.locales_x_ha - corte, 3),
            "barrios": formato_conteo(cuerpo.barrio),
            "comunas": "; ".join(str(int(c)) for c in sorted(cuerpo.comuna.dropna().unique())),
            "calles_dominantes": "; ".join(f"{c.title()} ({n})" for c, n in calles.items()),
            "pct_locales_con_direccion": round(len(con_direccion) / len(cuerpo) * 100, 1),
            "zonas_publicadas_encima": " · ".join(t for _, t in solapes) or "ninguna",
            "polo_mas_cercano": vecino,
            "d_al_vecino_entre_puntos_m": round(float(distancias.min()), 1),
        })

    tabla = pd.DataFrame(filas).sort_values("n_locales", ascending=False).reset_index(drop=True)

    p("-" * 100)
    p("  LA TABLA, resumida. El CSV lleva las columnas largas enteras.")
    p("")
    columnas = ["polo_id", "n_locales", "ha", "locales_x_ha", "clase_densidad",
                "distancia_al_corte", "pct_locales_con_direccion",
                "polo_mas_cercano", "d_al_vecino_entre_puntos_m"]
    p(tabla[columnas].to_string(index=False))
    p("")

    p("-" * 100)
    p("  LO QUE CONVIENE MIRAR ANTES DE NOMBRAR")
    p("")
    sin_zona = tabla[tabla.zonas_publicadas_encima == "ninguna"]
    p(f"  · polos sin ninguna zona publicada encima: {len(sin_zona)} de {len(tabla)} "
      f"({int(sin_zona.n_locales.sum())} locales). Son los que hay que nombrar desde cero.")
    con_zona = tabla[tabla.zonas_publicadas_encima != "ninguna"]
    p(f"  · polos con al menos una zona publicada encima: {len(con_zona)}. El nombre publicado es")
    p("    el candidato natural, pero el solape va en los dos sentidos y hay que mirarlo: un polo")
    p("    que cubre el 20 % de una zona no es esa zona.")
    p("")

    flojos = tabla[tabla.pct_locales_con_direccion < 50].sort_values("pct_locales_con_direccion")
    p(f"  · polos donde MENOS de la mitad de los locales tiene dirección: {len(flojos)}.")
    p("    En ésos las calles dominantes se apoyan en poca evidencia y no alcanzan solas.")
    if len(flojos):
        p(flojos[["polo_id", "n_locales", "pct_locales_con_direccion",
                  "calles_dominantes"]].head(15).to_string(index=False))
    p("")

    ambiguos = tabla[tabla.distancia_al_corte.abs() < 0.5].sort_values("distancia_al_corte")
    p(f"  · polos a menos de 0,5 loc/ha del corte de clase: {len(ambiguos)}. En éstos la clase")
    p("    NO significa nada — el corte es una convención y no hay hueco que lo sostenga—, así")
    p("    que la clase no debería entrar en el nombre ni en la redacción de la ficha.")
    if len(ambiguos):
        p(ambiguos[["polo_id", "n_locales", "locales_x_ha", "clase_densidad",
                    "distancia_al_corte"]].to_string(index=False))
    p("")

    pegados = tabla[tabla.d_al_vecino_entre_puntos_m < 50].sort_values(
        "d_al_vecino_entre_puntos_m")
    p(f"  · polos a menos de 50 m de otro MEDIDO ENTRE PUNTOS: {len(pegados)}. Es el rango del")
    p("    precedente Recoleta —«por debajo de unos 50 m, unir»—, así que estos pares son los")
    p("    que hay que mirar antes de darles dos nombres distintos.")
    if len(pegados):
        p(pegados[["polo_id", "n_locales", "polo_mas_cercano",
                   "d_al_vecino_entre_puntos_m"]].to_string(index=False))
    p("")

    p("=" * 100)
    p(f"  {len(tabla)} polos · {int(tabla.n_locales.sum())} locales · "
      f"{tabla.ha.sum():.0f} ha · Google Places: 0 requests")
    p("=" * 100)
    p("")

    salida = buffer.getvalue()
    (OUT / "POLOS_PARA_NOMBRAR.txt").write_text(salida, encoding="utf-8")
    tabla.to_csv(OUT / "POLOS_PARA_NOMBRAR.csv", index=False, encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
