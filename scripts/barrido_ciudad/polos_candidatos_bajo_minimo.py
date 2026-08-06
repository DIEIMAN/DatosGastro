"""Registro de conglomerados que NO llegaron al mínimo de 40. El antídoto del error del sur.

PARA QUÉ EXISTE ESTE ARCHIVO
-----------------------------
El Atlas publicó «No se identificaron zonas en el extremo sur de la Ciudad». Era literalmente
cierto y se leyó como si no hubiera nada; el barrido posterior encontró diez polos con mil locales
ahí. La frase no era falsa: era una afirmación sobre dónde habíamos mirado, escrita como una
afirmación sobre el territorio (R7).

Este registro es el antídoto exacto. **Lista lo que había y no calificó**, para que la frase «no
se identificaron polos en X» venga con la evidencia de qué se descartó y por qué. Un lector puede
discutir el mínimo; lo que no puede es no enterarse.

**No publica nada y no rescata nada.** El mínimo de 40 no se toca: está anclado en la zona
publicada más chica del Atlas y se fijó para todo el universo antes de mirar qué sobrevivía (R3).

EL INSTRUMENTO, Y EN QUÉ SE DIFERENCIA DEL QUE HIZO LOS POLOS
---------------------------------------------------------------
Los 118 polos salieron de HDBSCAN. Este registro usa **contigüidad** —componentes conexas a un
umbral declarado— sobre los puntos que quedaron afuera de todo polo. **No es el mismo instrumento**
y hay que decirlo: un conglomerado de acá no es «un polo rechazado», es «un grupo de locales
contiguos que no llega al mínimo». Se elige contigüidad porque es transparente y reproducible sin
re-correr el clustering, que movería la pertenencia de los polos ya decididos.

Como el resultado depende del umbral, va la sensibilidad a 40, 55 y 70 m (R4).

DOS ORÍGENES, Y NO SE MEZCLAN
-------------------------------
  `fuera_de_todo_polo`  · contiguos entre los puntos que ningún polo se llevó. Son los que
                          responden «¿qué había en X que no calificó?».
  `bloque_interno`      · bloques adentro de un polo que no llegan al mínimo de parte, como los
                          35 / 23 / 12 del saliente de P078. NO son «no se identificó nada ahí»:
                          están adentro de una zona que sí califica.

Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_candidatos_bajo_minimo.py
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

from borrador_polos_ciudad import (  # noqa: E402
    CRS_METRICO, ENVOLVENTES_22, PARAMETROS, cargar_puntos, envolver,
)
from polos_atributos_clases import OUT  # noqa: E402
from polos_particion_anada_estructura import MINIMO, componentes  # noqa: E402

UMBRAL = 55                  # declarado; la sensibilidad va abajo
SENSIBILIDAD = (40, 55, 70)
BANDA = (25, MINIMO - 1)     # 25–39 locales: lo que quedó cerca y no llegó


def inventario(puntos: gpd.GeoDataFrame, umbral: int) -> list[list[int]]:
    """Los conglomerados contiguos que caen en la banda."""
    return [c for c in componentes(puntos, umbral) if BANDA[0] <= len(c) <= BANDA[1]]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    # `comuna` ya viene en la base; traerla otra vez del padrón de pertenencia la duplicaría en
    # comuna_x/comuna_y y el script fallaría más adelante con un nombre que no existe.
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    polos = gpd.read_file(OUT / "borrador_polos_v3.geojson").to_crs(CRS_METRICO)
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)
    nombres_zona = dict(zip(zonas.referencia_id, zonas.nombre))

    sueltos = geo[geo.polo_unido == ""].reset_index(drop=True)
    asignados = geo[geo.polo_unido != ""].reset_index(drop=True)

    # Árbol sobre los puntos YA asignados: da de una el polo más cercano y su distancia real.
    xy_asignados = np.c_[asignados.geometry.x.to_numpy(), asignados.geometry.y.to_numpy()]
    arbol = cKDTree(xy_asignados)

    p("CANDIDATOS BAJO EL MÍNIMO · lo que había y no calificó")
    p("=" * 100)
    p("")
    p("  El Atlas escribió «no se identificaron zonas en el extremo sur» y se leyó como que no")
    p("  había nada. Este registro es el antídoto: lista lo que se descartó, para que la frase")
    p("  venga con su evidencia. NO publica ni rescata nada — el mínimo de 40 no se toca.")
    p("")
    p(f"  banda: {BANDA[0]}–{BANDA[1]} locales · umbral de contigüidad: {UMBRAL} m")
    p(f"  puntos fuera de todo polo: {len(sueltos)} de {len(geo)}")
    p("")
    p("  INSTRUMENTO: contigüidad, NO el HDBSCAN que hizo los 118. Un conglomerado de acá no es")
    p("  «un polo rechazado»: es un grupo de locales contiguos que no llega al mínimo.")
    p("")

    filas = []

    # --- origen 1: conglomerados fuera de todo polo
    for orden, indices in enumerate(inventario(sueltos, UMBRAL), start=1):
        miembros = sueltos.iloc[indices]
        geometria, degenerado = envolver(miembros, PARAMETROS["concave_hull_ratio"])
        xy = np.c_[miembros.geometry.x.to_numpy(), miembros.geometry.y.to_numpy()]
        distancias, vecinos = arbol.query(xy)
        i_mas_cerca = int(np.argmin(distancias))
        polo_cercano = asignados.iloc[int(vecinos[i_mas_cerca])].polo_unido
        envolvente_cercana = polos[polos.polo_id == polo_cercano]
        adentro = {}
        for z in zonas.itertuples():
            n = int(miembros.geometry.within(z.geometry).sum())
            if n:
                adentro[z.referencia_id] = n
        ha = geometria.area / 1e4
        filas.append({
            "candidato_id": f"C{orden:03d}",
            "origen": "fuera_de_todo_polo",
            "n_locales": len(indices),
            "ha": round(ha, 2),
            "locales_x_ha": round(len(indices) / ha, 2) if ha > 0 else None,
            "barrios": "; ".join(f"{b} ({n})" for b, n in
                                 miembros.barrio.value_counts().head(3).items()),
            "comuna": "; ".join(str(int(c)) for c in
                                sorted(miembros.comuna.dropna().unique())),
            "polo_mas_cercano": polo_cercano,
            "d_al_polo_entre_puntos_m": round(float(distancias.min()), 1),
            "d_al_polo_envolventes_m": round(
                geometria.distance(envolvente_cercana.geometry.iloc[0]), 1)
            if len(envolvente_cercana) else None,
            "en_zona_publicada": "; ".join(
                f"{nombres_zona.get(k, k)} ({k}): {v}" for k, v in adentro.items()) or "no",
            "hull_degenerado": degenerado,
        })

    # --- origen 2: bloques adentro de un polo que no llegan al mínimo de parte
    orden = 0
    for polo_id in sorted(geo[geo.polo_unido != ""].polo_unido.unique()):
        cuerpo = geo[geo.polo_unido == polo_id].reset_index(drop=True)
        todas = componentes(cuerpo, UMBRAL)
        if len([c for c in todas if len(c) >= MINIMO]) < 2:
            continue          # sin partes, no hay «bloque interno» que reportar
        for indices in todas:
            if not (BANDA[0] <= len(indices) <= BANDA[1]):
                continue
            orden += 1
            miembros = cuerpo.iloc[indices]
            geometria, degenerado = envolver(miembros, PARAMETROS["concave_hull_ratio"])
            adentro = {}
            for z in zonas.itertuples():
                n = int(miembros.geometry.within(z.geometry).sum())
                if n:
                    adentro[z.referencia_id] = n
            ha = geometria.area / 1e4
            filas.append({
                "candidato_id": f"B{orden:03d}",
                "origen": "bloque_interno",
                "n_locales": len(indices),
                "ha": round(ha, 2),
                "locales_x_ha": round(len(indices) / ha, 2) if ha > 0 else None,
                "barrios": "; ".join(f"{b} ({n})" for b, n in
                                     miembros.barrio.value_counts().head(3).items()),
                "comuna": "; ".join(str(int(c)) for c in
                                    sorted(miembros.comuna.dropna().unique())),
                "polo_mas_cercano": polo_id,
                "d_al_polo_entre_puntos_m": 0.0,      # está adentro del polo
                "d_al_polo_envolventes_m": 0.0,
                "en_zona_publicada": "; ".join(
                    f"{nombres_zona.get(k, k)} ({k}): {v}" for k, v in adentro.items()) or "no",
                "hull_degenerado": degenerado,
            })

    tabla = pd.DataFrame(filas).sort_values(
        ["origen", "n_locales"], ascending=[True, False]).reset_index(drop=True)

    p("-" * 100)
    p("  EL REGISTRO")
    p("")
    for origen, grupo in tabla.groupby("origen"):
        p(f"  · {origen}: {len(grupo)} conglomerados, {int(grupo.n_locales.sum())} locales")
    p("")
    columnas = ["candidato_id", "origen", "n_locales", "locales_x_ha", "comuna",
                "polo_mas_cercano", "d_al_polo_entre_puntos_m", "en_zona_publicada"]
    p(tabla[columnas].to_string(index=False))
    p("")

    fuera = tabla[tabla.origen == "fuera_de_todo_polo"]
    if len(fuera):
        p("-" * 100)
        p("  DÓNDE ESTÁN LOS QUE QUEDARON FUERA DE TODO POLO")
        p("")
        por_comuna = fuera.comuna.value_counts().sort_index()
        for comuna, n in por_comuna.items():
            locales = int(fuera[fuera.comuna == comuna].n_locales.sum())
            p(f"    comuna {comuna:<8} {n} conglomerado(s) · {locales} locales")
        p("")
        sin_zona = fuera[fuera.en_zona_publicada == "no"]
        p(f"    fuera de toda zona publicada: {len(sin_zona)} de {len(fuera)} conglomerados "
          f"({int(sin_zona.n_locales.sum())} locales)")
        p("")

    # --- sensibilidad al umbral, que es de donde depende todo esto
    p("-" * 100)
    p("  SENSIBILIDAD AL UMBRAL DE CONTIGÜIDAD")
    p("")
    sens = []
    for umbral in SENSIBILIDAD:
        grupos = inventario(sueltos, umbral)
        sens.append({
            "umbral_m": umbral,
            "conglomerados_en_banda": len(grupos),
            "locales_en_banda": sum(len(c) for c in grupos),
            "el_mas_grande": max((len(c) for c in grupos), default=0),
        })
    p(pd.DataFrame(sens).to_string(index=False))
    p("")
    p("    **La dependencia del umbral es FUERTE y hay que leerla antes que la tabla**: de 1")
    p("    conglomerado a 40 m se pasa a 14 a 55 m y a 18 a 70 m. Este registro NO es una")
    p("    propiedad del territorio: es lo que se ve con un umbral de contigüidad de 55 m, y con")
    p("    otro se ve otra cosa. Se publica con el umbral al lado, siempre, y quien lo use para")
    p("    respaldar una frase tiene que citar el umbral en la misma frase.")
    p("")
    p("    La razón del salto es la del §geométrico: a 40 m el umbral queda por debajo del vecino")
    p("    típico de un tejido denso y casi nada se conecta. No hay un valor «correcto»; hay uno")
    p("    declarado.")
    p("")

    # ¿Y el sur, que es el caso que motivó todo esto?
    p("-" * 100)
    p("  QUÉ DICE ESTE REGISTRO SOBRE EL SUR")
    p("")
    comunas_sur = {"4", "8", "9"}
    en_sur = fuera[fuera.comuna.apply(
        lambda c: bool(comunas_sur & set(str(c).replace(" ", "").split(";"))))]
    if len(en_sur):
        p(f"    {len(en_sur)} conglomerado(s) en las comunas 4, 8 o 9.")
        p(en_sur[["candidato_id", "n_locales", "barrios", "comuna"]].to_string(index=False))
    else:
        p("    Con este umbral no aparecen conglomerados de 25–39 locales en las comunas 4, 8 ni 9.")
        p("")
        p("    Y esto se escribe con cuidado, porque es exactamente el lugar donde el Atlas se")
        p("    equivocó: **no significa que no haya actividad en el sur.** Significa que ahí la")
        p("    oferta que la base registra ya quedó adentro de polos que sí califican —el barrido")
        p("    encontró diez— o está más dispersa que 55 m entre locales. El registro dice dónde")
        p("    hubo conglomerados que no llegaron al mínimo, no dónde hay o no hay gastronomía.")
    p("")

    p("=" * 100)
    p(f"  {len(tabla)} candidatos registrados · {int(tabla.n_locales.sum())} locales en total")
    p("=" * 100)
    p("")
    p("  CÓMO SE USA: al lado de cualquier frase del tipo «no se identificaron polos en X».")
    p("  Y CÓMO NO: ninguno de estos es un polo, ninguno se publica, y el mínimo sigue en 40.")
    p("")

    salida = buffer.getvalue()
    (OUT / "CANDIDATOS_BAJO_MINIMO.txt").write_text(salida, encoding="utf-8")
    tabla.to_csv(OUT / "CANDIDATOS_BAJO_MINIMO.csv", index=False, encoding="utf-8")
    pd.DataFrame(sens).to_csv(OUT / "candidatos_bajo_minimo_sensibilidad.csv", index=False,
                              encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
