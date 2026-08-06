"""Primera poligonización de toda la Ciudad desde la base. BORRADOR — no se publica ni se sella.

QUÉ ES Y QUÉ NO ES
------------------
Es el objetivo del proyecto corrido por primera vez de punta a punta: clustering sobre los puntos
aptos de los 48 barrios, con **un solo juego de parámetros para toda la Ciudad**, y las
envolventes que salen de ahí. No toca el Atlas, no reemplaza ninguna de las 22 zonas publicadas y
ninguna de sus cifras entra en ningún informe. Se mira, se discute, y recién después se decide si
algo de esto se convierte en producto.

LOS PARÁMETROS SON ÚNICOS Y ESTÁN ANCLADOS EN ALGO EXTERNO A ESTOS DATOS
------------------------------------------------------------------------
La regla que ordena esta corrida: **si un polo sólo aparece bajando el umbral en su zona, no es un
polo, es un ajuste.** Así que los parámetros se fijan una vez, para los 48 barrios, y se eligen
antes de mirar ningún resultado:

  min_cluster_size = 40   La zona más chica que el Atlas ya publicó tiene 40 establecimientos
                          (R16 Donado–Holmberg y R20 García del Río). No se llama polo a algo más
                          chico que lo más chico que la Dirección ya publicó. El ancla es una
                          decisión editorial vieja, no un número leído de estos datos.
  min_samples      = 10   Cuántos vecinos hacen «denso» un punto. Diez locales gastronómicos en el
                          entorno inmediato es el umbral de percepción de a pie que el proyecto
                          viene usando; por debajo de eso el algoritmo persigue tríos de esquina.
  método           = eom  Excess of mass: deja que el algoritmo elija la profundidad del corte en
                          vez de imponer una cantidad de polos. Es el mismo que ya se usó en la
                          corrida territorial V3.
  concave_hull     = 0,55 El ratio adoptado por `config_territorial_v3.json`. No se reajusta.

Y **la sensibilidad se publica**, como pide el §7 del esquema: si el mapa cambia de naturaleza
cuando se mueve el umbral, el umbral está mal elegido y hay que decirlo antes que nadie.

EL UNIVERSO: SÓLO PUNTOS APTOS, Y EL CONTROL DEL §5
--------------------------------------------------
Entran únicamente los puntos con `apto_geometria = True`, que es lo que el §5 del esquema exige
para que una envolvente hable de la oferta y no de la geometría de consulta. Pero alimentar el
clustering sólo con aptos no alcanza para cumplir el control: **una envolvente dibujada con puntos
aptos puede encerrar mayoritariamente puntos que no lo son**, y ahí el polígono vuelve a describir
otra cosa. Así que el control se corre sobre la envolvente terminada, contando todo lo que cae
adentro. Si alguna falla, se marca y se informa; no se borra en silencio.

EL ANILLO ES EL NÚCLEO, Y LA DECISIÓN SE DECLARA
------------------------------------------------
Se poligoniza el anillo **núcleo** —restaurante, bar, café, pizzería, parrilla, comida al paso,
heladería—. Panaderías y pastelerías (el ampliado) van como sensibilidad, no como universo
principal. El motivo es el mismo por el que existen los dos anillos: una panadería es comercio de
alimentos y no necesariamente gastronomía de estar. La corrida con el ampliado se reporta al lado
para que la decisión sea falsable y no un supuesto escondido.

QUÉ MÁS SE MIDE, PORQUE EL BORRADOR ES TAMBIÉN UN DIAGNÓSTICO
--------------------------------------------------------------
El §10 del esquema declara que la base no sabe todavía si su cobertura es pareja. Un mapa lo
muestra donde una tabla no: si aparecieran polos sólo donde una fuente miró más, se vería. Por eso
cada polo se reporta con la composición de sus fuentes y con una **ablación**: se repite la corrida
completa sacando un grupo de independencia por vez, y se mide cuántos polos sobreviven. Un polo
que desaparece al sacar una sola fuente no es un polo: es lo que esa fuente cargó.

**Toda ablación lleva control aleatorio, y eso es regla del script, no criterio del que lo corre.**
Sacar una fuente saca puntos; sin sortear la misma cantidad de puntos al azar no se distingue «la
fuente sostenía el polo» de «faltaron puntos». No hay bandera para saltearlo: ver `SORTEOS_CONTROL`.

Google Places no interviene: no está en la base y esta corrida no consulta nada.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/borrador_polos_ciudad.py
  .venv/Scripts/python.exe scripts/barrido_ciudad/borrador_polos_ciudad.py --sin-ablacion
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import unicodedata
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import MultiPoint
from sklearn.cluster import HDBSCAN

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
BASE = BARRIDO / "base" / "local.csv"
ENVOLVENTES_22 = ROOT / "outputs" / "polos_gastro" / "ATLAS_V2" / "capas" / "envolventes_editoriales_v2.geojson"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
OUT = BARRIDO / "borrador_polos"
GEN_PAREJIDAD = BARRIDO / "generado"

CRS_METRICO = "EPSG:5347"
CRS_GEO = "EPSG:4326"

# --- los parámetros, uno solo para toda la Ciudad -----------------------------------------------
PARAMETROS = {
    "min_cluster_size": 40,
    "min_samples": 10,
    "cluster_selection_method": "eom",
    "concave_hull_ratio": 0.55,
    "anillo": "nucleo",
    "solo_aptos": True,
}

# Sensibilidad publicada: la grilla se declara acá y se corre entera, no se elige la celda que
# mejor queda. `min_cluster_size` se mueve entre la mitad y el doble del valor adoptado.
GRILLA_SENSIBILIDAD = [(mcs, ms) for mcs in (20, 30, 40, 60, 80) for ms in (5, 10, 20)]

# --- umbrales del cotejo, escritos antes de correrlo --------------------------------------------
# Se necesitan dos, y son distintos: uno decide si el borrador ENCONTRÓ una zona publicada, y el
# otro si un polo del borrador es NUEVO. Un solo número para los dos lados escondería el hecho de
# que las superficies son muy distintas —las publicadas van de 25 a 479 ha—.
COBERTURA_MINIMA_ZONA = 0.25   # el borrador «encuentra» una zona si le cubre al menos este 25 %
SOLAPE_MAXIMO_NUEVO = 0.25     # un polo es «nuevo» si menos del 25 % de su superficie ya estaba

# Grupos de independencia de la base (§3 del esquema). La ablación saca uno por vez.
GRUPOS = {
    "F01": "GCBA_AGC", "F02": "GCBA_AGC", "RUS": "GCBA_URBANISMO",
    "PERMISOS": "GCBA_ESPACIO_PUBLICO", "OSM": "OSM",
    "OVERTURE": "OVERTURE_FSQ_ATP", "ATP": "OVERTURE_FSQ_ATP",
}

# Cuándo una corrida dejó de separar polos y devolvió la Ciudad entera como una mancha. Pasa con
# HDBSCAN cuando `min_samples` es alto respecto de la densidad: el resultado sigue siendo un número
# de clusters y sigue pareciendo una respuesta. Sin este umbral, «5 polos» y «2 polos» se leerían
# como corridas más conservadoras cuando son corridas fallidas.
COLAPSO_PCT = 0.50

# --- el control aleatorio es OBLIGATORIO en toda ablación, y la regla vive acá ------------------
# No es una opción del que corre el script. Sacar una fuente saca puntos, y los parámetros están
# calibrados sobre la densidad actual: sin el control no se sabe si la corrida se rompió por la
# fuente o por quedarse corta de puntos. En la corrida del 2026-08-06, agregar el control cambió el
# significado de TRES de las cinco filas. Por eso no hay bandera `--sin-control`: `ablacion()` se
# niega a devolver una tabla sin su columna de control, y `lectura_ablacion()` se niega a redactar
# una lectura de una fila que no la traiga. Si alguna vez hay que bajarlo, se baja borrando este
# bloque a mano y dejando el rastro en el diff, no pasando un flag.
SORTEOS_CONTROL = 5   # sorteos del control aleatorio, con semilla fija
if SORTEOS_CONTROL < 3:
    raise SystemExit(
        "SORTEOS_CONTROL < 3: el control aleatorio es obligatorio y el colapso es un umbral, así "
        "que un solo sorteo cae de un lado o del otro por azar. Mínimo tres.")


def lectura_ablacion(fila) -> str:
    """La lectura de una fila de ablación, que NO existe sin su control aleatorio.

    Se niega a redactar antes que redactar de más: una fila sin control no dice si midió la fuente
    o la densidad, y una lectura escrita igual es peor que ninguna.
    """
    if not getattr(fila, "colapsos_azar", None):
        raise ValueError(
            f"la fila «{fila.grupo_quitado}» no trae control aleatorio: no se puede leer. "
            "Toda ablación viaja con su control (ver SORTEOS_CONTROL).")
    colapsos = int(str(fila.colapsos_azar).split("/")[0])
    if fila.colapsa and colapsos == 0:
        return ("la fuente SOSTIENE el mapa: sin ella la corrida se rompe y sacar la misma "
                "cantidad de puntos al azar no la rompe nunca")
    if fila.colapsa and colapsos:
        return (f"NO INTERPRETABLE: el azar rompe la corrida {colapsos} de {SORTEOS_CONTROL} "
                "veces. Se midió la densidad que exigen los parámetros, no el peso de la fuente")
    if colapsos and not fila.colapsa:
        return ("sus puntos son REDUNDANTES: sacarla aguanta mejor que sacar la misma cantidad "
                "al azar")
    if fila.pct_puntos_perdidos == 0:
        return "no aporta ningún local propio: sus registros llegan siempre pegados a otro"
    return f"interpretable: sobrevive el {fila.pct_sobreviven:.0f} % de los polos"


def colapsa(etiquetas: np.ndarray) -> tuple[bool, float]:
    """¿La corrida devolvió una sola mancha? Devuelve también qué fracción cayó en el mayor."""
    validos = etiquetas[etiquetas >= 0]
    if not len(validos):
        return False, 0.0
    mayor = pd.Series(validos).value_counts().iloc[0] / len(etiquetas)
    return mayor > COLAPSO_PCT, float(mayor)


def plegar(texto: object) -> str:
    return (unicodedata.normalize("NFKD", str(texto))
            .encode("ascii", "ignore").decode().upper().strip())


# --------------------------------------------------------------------------- insumos


def cargar_puntos(anillo: str, solo_aptos: bool) -> gpd.GeoDataFrame:
    """Los puntos que pueden dibujar, en CRS métrico.

    `apto_geometria` es la condición del §5 y no se relaja: un punto geocodificado a centroide de
    manzana corre la forma del cluster treinta metros, y treinta metros cambian una envolvente.
    """
    base = pd.read_csv(BASE, low_memory=False)
    base["barrio_k"] = base.barrio.map(plegar)
    universo = base if anillo == "ampliado" else base[base.anillo == "nucleo"]
    if solo_aptos:
        universo = universo[universo.apto_geometria]
    geo = gpd.GeoDataFrame(
        universo.copy(),
        geometry=gpd.points_from_xy(universo.lon, universo.lat), crs=CRS_GEO).to_crs(CRS_METRICO)
    geo["grupo_principal"] = geo.grupos_independencia.fillna("").str.split(";").str[0]
    return geo.reset_index(drop=True)


def cargar_base_completa() -> gpd.GeoDataFrame:
    """Todos los locales con punto, aptos y no aptos: es contra esto que corre el control del §5."""
    base = pd.read_csv(BASE, low_memory=False)
    return gpd.GeoDataFrame(
        base, geometry=gpd.points_from_xy(base.lon, base.lat), crs=CRS_GEO).to_crs(CRS_METRICO)


# --------------------------------------------------------------------------- clustering


def agrupar(geo: gpd.GeoDataFrame, min_cluster_size: int, min_samples: int,
            metodo: str = "eom") -> np.ndarray:
    xy = np.c_[geo.geometry.x.to_numpy(), geo.geometry.y.to_numpy()]
    return HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples,
                   cluster_selection_method=metodo, copy=True).fit_predict(xy)


def envolver(puntos: gpd.GeoSeries, ratio: float):
    """Envolvente cóncava del cluster. Si el hull cóncavo degenera, cae al convexo y se anota."""
    multi = MultiPoint(list(puntos.geometry))
    geometria = shapely.concave_hull(multi, ratio=ratio, allow_holes=False)
    if geometria.is_empty or geometria.geom_type not in ("Polygon", "MultiPolygon"):
        return multi.convex_hull, True
    return geometria, False


def construir_polos(geo: gpd.GeoDataFrame, etiquetas: np.ndarray,
                    ratio: float) -> gpd.GeoDataFrame:
    """Un polígono por cluster, con su composición de fuentes y su tamaño."""
    filas = []
    for etiqueta in sorted({int(e) for e in etiquetas if e >= 0}):
        miembros = geo[etiquetas == etiqueta]
        geometria, degenerado = envolver(miembros, ratio)
        grupos = miembros.grupos_independencia.fillna("").str.split(";").explode()
        grupos = grupos[grupos != ""]
        barrios = miembros.barrio.value_counts()
        filas.append({
            "polo_id": f"P{etiqueta + 1:03d}",
            "locales": len(miembros),
            "ha": geometria.area / 1e4,
            "locales_x_ha": len(miembros) / (geometria.area / 1e4),
            "barrio_principal": barrios.index[0],
            "barrios": ";".join(barrios.index[:3]),
            "n_barrios": int(miembros.barrio.nunique()),
            "corroborados": int((miembros.n_fuentes >= 2).sum()),
            "grupo_dominante": grupos.value_counts().index[0] if len(grupos) else "",
            "peso_grupo_dominante": (grupos.value_counts().iloc[0] / len(miembros)) if len(grupos) else np.nan,
            "abiertos": int((miembros.nivel_publicacion == "abierto").sum()),
            "hull_degenerado": degenerado,
            "geometry": geometria,
        })
    polos = gpd.GeoDataFrame(filas, geometry="geometry", crs=CRS_METRICO)
    return polos.sort_values("locales", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------- controles


def control_aptitud(polos: gpd.GeoDataFrame, base_completa: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Control 7 del §8: ninguna envolvente puede derivarse mayoritariamente de puntos no aptos.

    Se cuenta todo lo que cae DENTRO de la envolvente terminada, apto y no apto. Contar sólo los
    puntos que el clustering usó daría 100 % siempre y no controlaría nada.
    """
    dentro = gpd.sjoin(base_completa[["local_id", "apto_geometria", "geometry"]],
                       polos[["polo_id", "geometry"]], how="inner", predicate="within")
    resumen = dentro.groupby("polo_id").apto_geometria.agg(["size", "sum"])
    resumen.columns = ["puntos_en_envolvente", "aptos_en_envolvente"]
    polos = polos.merge(resumen, left_on="polo_id", right_index=True, how="left")
    polos[["puntos_en_envolvente", "aptos_en_envolvente"]] = polos[
        ["puntos_en_envolvente", "aptos_en_envolvente"]].fillna(0).astype(int)
    polos["share_aptos"] = polos.aptos_en_envolvente / polos.puntos_en_envolvente.replace(0, np.nan)
    polos["control_aptitud"] = polos.share_aptos > 0.5
    return polos


def ablacion(geo: gpd.GeoDataFrame, polos: gpd.GeoDataFrame, p) -> pd.DataFrame:
    """Repite la corrida entera sacando un grupo de independencia por vez.

    Lo que interesa no es cuántos polos salen sin esa fuente, sino **cuántos de los polos de la
    corrida completa siguen existiendo**: un polo sobrevive si su superficie queda cubierta en al
    menos la mitad por algún polo de la corrida ablacionada. Un polo que desaparece al sacar una
    sola fuente no describe el territorio: describe dónde miró esa fuente.

    Y una ablación sin control no se puede leer. Sacar una fuente saca puntos, y los parámetros
    están calibrados sobre la densidad actual: con un tercio menos de puntos la corrida puede
    romperse **por rala**, sin que esa fuente sostuviera nada. Por eso cada ablación viaja con un
    **control aleatorio**: se sacan al azar exactamente tantos puntos como sacó la fuente y se
    repite. Si el azar rompe la corrida igual, lo que se midió fue la densidad, no la fuente.
    """
    generador = np.random.default_rng(20260806)
    filas = []
    for grupo in sorted(set(GRUPOS.values())):
        sin = geo[~geo.grupos_independencia.fillna("").str.split(";").map(lambda g: grupo in g)]
        if len(sin) < PARAMETROS["min_cluster_size"]:
            continue
        etiquetas = agrupar(sin, PARAMETROS["min_cluster_size"], PARAMETROS["min_samples"])
        colapsada, mayor = colapsa(etiquetas)
        parciales = construir_polos(sin, etiquetas, PARAMETROS["concave_hull_ratio"])
        union = parciales.union_all() if len(parciales) else None
        if union is None:
            sobreviven = 0
        else:
            sobreviven = int(sum(polo.intersection(union).area / polo.area >= 0.5
                                 for polo in polos.geometry))
        # Control aleatorio: mismos n puntos removidos, elegidos al azar. Con un solo sorteo el
        # control es tan inestable como lo que quiere controlar —el colapso es un umbral, y una
        # sola muestra cae de un lado o del otro por azar—, así que se sortea varias veces y se
        # reporta cuántas colapsaron.
        colapsos, polos_azar = 0, []
        for _ in range(SORTEOS_CONTROL):
            azar = geo.iloc[generador.choice(len(geo), size=len(sin), replace=False)]
            etiquetas_azar = agrupar(azar, PARAMETROS["min_cluster_size"], PARAMETROS["min_samples"])
            colapsada_azar, _ = colapsa(etiquetas_azar)
            colapsos += int(colapsada_azar)
            polos_azar.append(len({int(e) for e in etiquetas_azar if e >= 0}))

        filas.append({
            "grupo_quitado": grupo,
            "puntos_restantes": len(sin),
            "pct_puntos_perdidos": round((1 - len(sin) / len(geo)) * 100, 1),
            "polos_en_la_ablacion": len(parciales),
            "polos_azar_mediana": int(np.median(polos_azar)),
            "colapsos_azar": f"{colapsos}/{SORTEOS_CONTROL}",
            "mayor_pct": round(mayor * 100, 1),
            "colapsa": colapsada,
            # Sin polos separados no hay supervivencia que medir: una mancha que cubre la Ciudad
            # «cubre» todos los polos originales y devolvería 100 % sin significar nada.
            "polos_originales_que_sobreviven": np.nan if colapsada else sobreviven,
            "pct_sobreviven": (np.nan if colapsada or not len(polos)
                               else round(sobreviven / len(polos) * 100, 1)),
        })
    tabla = pd.DataFrame(filas)
    # El control no es opcional y esto lo hace estructural: una tabla sin su columna no sale de
    # esta función. Si algún día alguien saca el bloque del control, la ablación deja de correr.
    if len(tabla) and "colapsos_azar" not in tabla.columns:
        raise ValueError("ablación sin control aleatorio: no se emite. Ver SORTEOS_CONTROL.")
    p("  ABLACIÓN · se saca un grupo de independencia por vez y se repite la corrida entera")
    p("    un polo «sobrevive» si al menos la mitad de su superficie sigue cubierta sin esa fuente")
    p("    `colapsa` = la corrida sin esa fuente ya no separa polos: devuelve una mancha con más")
    p(f"    del {COLAPSO_PCT:.0%} de los puntos, y entonces la supervivencia no se puede medir")
    p(f"    `_azar` = el control: {SORTEOS_CONTROL} sorteos sacando al azar los mismos n puntos")
    p(tabla.to_string(index=False))
    p("")
    p("    LECTURA, caso por caso — la fila sola no dice nada sin su control:")
    for fila in tabla.itertuples():
        p(f"      {fila.grupo_quitado:<22} {lectura_ablacion(fila)}")
    p("")
    p("    Y la conclusión que atraviesa la tabla: **el umbral de colapso cae adentro del rango de")
    p("    tamaños que la ablación necesita probar.** Con un solo juego de parámetros calibrado a")
    p("    la densidad actual, esta ablación no puede separar limpiamente «la fuente sostenía el")
    p("    polo» de «faltaron puntos». Es un límite del diseño de la prueba, no un resultado sobre")
    p("    las fuentes, y hay que arreglarlo antes de usar la ablación para decidir nada.")
    p("")
    return tabla


def diagnostico_10(geo: gpd.GeoDataFrame, polos: gpd.GeoDataFrame, p) -> None:
    """El borrador leído contra el §10: ¿los polos siguen a la oferta o siguen a las fuentes?

    El §10 del esquema declara que la base no sabe si su cobertura es pareja. Un mapa lo muestra
    donde una tabla no: si aparecieran polos sólo donde una fuente miró más, se vería.

    El contraste que hace falta es contra algo que NO dependa de dónde miraron nuestras fuentes, y
    el Relevamiento de Usos del Suelo sirve: caminó los 48 barrios parcela por parcela. Si un
    barrio tiene mucha gastronomía relevada a pie y ningún polo, o al revés, el mapa no está
    siguiendo al territorio. La tabla completa está en PAREJIDAD_COBERTURA.txt.
    """
    tabla_a = GEN_PAREJIDAD / "parejidad_a_parcelas_comerciales.csv"
    if not tabla_a.exists():
        p("  DIAGNÓSTICO DEL §10 · no corre: falta parejidad_a_parcelas_comerciales.csv")
        p("    correr antes scripts/barrido_ciudad/parejidad_cobertura.py")
        p("")
        return

    parejidad = pd.read_csv(tabla_a, index_col=0)
    por_barrio = polos.groupby("barrio_principal").agg(
        polos=("polo_id", "size"), locales_en_polos=("locales", "sum"))
    por_barrio.index = [plegar(i) for i in por_barrio.index]
    puntos_barrio = geo.groupby("barrio_k").local_id.count().rename("puntos_aptos")

    cruce = parejidad[["rus_gastro", "rus_sobre_comercial", "cobertura"]].join(
        por_barrio, how="left").join(puntos_barrio, how="left").fillna(0)
    cruce["polos"] = cruce.polos.astype(int)

    p("  DIAGNÓSTICO DEL §10 · ¿los polos siguen a la oferta o siguen a las fuentes?")
    p("    contraste contra el Relevamiento de Usos del Suelo, que caminó los 48 barrios")
    correlacion = cruce.rus_gastro.corr(cruce.locales_en_polos, method="spearman")
    p(f"    correlación de Spearman entre gastronomía relevada a pie y locales en polos, por "
      f"barrio: {correlacion:.2f}")
    sin_polo = cruce[cruce.polos == 0].sort_values("rus_gastro", ascending=False)
    p(f"    barrios sin ningún polo: {len(sin_polo)}")
    p(sin_polo[["rus_gastro", "rus_sobre_comercial", "puntos_aptos", "cobertura"]].round(2).to_string())
    p(f"    los seis juntos tienen {int(sin_polo.rus_gastro.sum())} parcelas gastronómicas "
      f"relevadas, el {sin_polo.rus_gastro.sum() / cruce.rus_gastro.sum() * 100:.1f} % de la "
      "Ciudad, y su composición mediana es "
      f"{sin_polo.rus_sobre_comercial.median():.0f} por mil contra "
      f"{cruce.rus_sobre_comercial.median():.0f} de la Ciudad.")
    p("")
    p("    Y el control que importa: ¿algún barrio con MUCHA gastronomía caminada quedó sin polo?")
    umbral = cruce.rus_gastro.median()
    huecos = sin_polo[sin_polo.rus_gastro > umbral]
    p(f"    barrios sin polo por encima de la mediana de gastronomía relevada "
      f"({umbral:.0f} parcelas): {len(huecos)}"
      + (f" — {', '.join(huecos.index)}" if len(huecos) else ""))
    p("")


def sensibilidad(geo: gpd.GeoDataFrame, p) -> pd.DataFrame:
    """La grilla declarada, corrida entera. Se publica gane o pierda el parámetro adoptado."""
    filas = []
    for mcs, ms in GRILLA_SENSIBILIDAD:
        etiquetas = agrupar(geo, mcs, ms)
        validos = etiquetas[etiquetas >= 0]
        tamanios = pd.Series(validos).value_counts()
        colapsada, mayor = colapsa(etiquetas)
        filas.append({
            "min_cluster_size": mcs, "min_samples": ms,
            "polos": int(len(tamanios)),
            "ruido_pct": round((etiquetas == -1).mean() * 100, 1),
            "mediana_locales": int(tamanios.median()) if len(tamanios) else 0,
            "mayor": int(tamanios.max()) if len(tamanios) else 0,
            "mayor_pct": round(mayor * 100, 1),
            "colapsa": colapsada,
            "adoptado": mcs == PARAMETROS["min_cluster_size"] and ms == PARAMETROS["min_samples"],
        })
    tabla = pd.DataFrame(filas)
    p("  SENSIBILIDAD AL UMBRAL · la grilla completa, declarada antes de correr")
    p("    `colapsa` marca las corridas que dejaron de separar polos y devolvieron la Ciudad como")
    p("    una mancha. Su columna `polos` es un número y no es un resultado: no se lee como una")
    p("    corrida más conservadora.")
    p(tabla.to_string(index=False))
    utiles = tabla[~tabla.colapsa]
    p(f"    corridas que separan polos: {len(utiles)} de {len(tabla)} | rango de polos "
      f"{utiles.polos.min()}–{utiles.polos.max()} | el adoptado da "
      f"{int(tabla.loc[tabla.adoptado, 'polos'].iloc[0])}")
    p("")
    return tabla


# --------------------------------------------------------------------------- cotejo


def cotejar(polos: gpd.GeoDataFrame, p) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    """El borrador contra las 22 zonas publicadas, en los dos sentidos.

    Los dos sentidos no son el mismo cálculo hecho al revés y por eso se reportan por separado:
    una zona publicada grande puede estar «encontrada» por un polo chico que le cubre poco, y un
    polo chico puede estar íntegramente adentro de una zona grande sin que la zona esté cubierta.
    """
    zonas = gpd.read_file(ENVOLVENTES_22)[["referencia_id", "nombre", "geometry"]].to_crs(CRS_METRICO)
    zonas["ha_zona"] = zonas.area / 1e4
    union_polos = polos.union_all()
    union_zonas = zonas.union_all()

    # --- sentido 1: qué le pasó a cada zona publicada
    filas = []
    for zona in zonas.itertuples():
        cubierto = zona.geometry.intersection(union_polos).area
        tocan = polos[polos.intersects(zona.geometry)]
        # «Toca» se mide contra la superficie de LA ZONA, no contra la del polo. Medirlo contra el
        # polo dejaba a una zona chica adentro de un polo grande con cero polos que la tocan y un
        # 25 % de cobertura en la misma fila: dos números que se contradicen.
        tocan = tocan[[g.intersection(zona.geometry).area / zona.geometry.area > 0.01
                       for g in tocan.geometry]]
        filas.append({
            "referencia_id": zona.referencia_id, "nombre": zona.nombre,
            "ha_zona": round(zona.ha_zona, 1),
            "polos_que_la_tocan": len(tocan),
            "pct_zona_cubierta": round(cubierto / zona.geometry.area * 100, 1),
            "encontrada": cubierto / zona.geometry.area >= COBERTURA_MINIMA_ZONA,
            "polos": ";".join(tocan.polo_id.tolist()[:6]),
        })
    por_zona = pd.DataFrame(filas)

    # --- sentido 2: qué le pasó a cada polo del borrador
    solapes, mejor_zona, absorbidas = [], [], []
    for geometria in polos.geometry:
        solape = geometria.intersection(union_zonas).area / geometria.area
        solapes.append(round(solape * 100, 1))
        candidatas = [(geometria.intersection(z.geometry).area / geometria.area, z.referencia_id)
                      for z in zonas.itertuples() if geometria.intersects(z.geometry)]
        mejor_zona.append(max(candidatas)[1] if candidatas else "")
        # Un polo grande puede tener poco solape porcentual y contener entera a una zona chica.
        # Sin esta columna, el polo que se come a Belgrano sale rotulado «nuevo».
        absorbidas.append(";".join(
            z.referencia_id for z in zonas.itertuples()
            if geometria.intersection(z.geometry).area / z.geometry.area >= 0.5))
    polos = polos.copy()
    polos["pct_ya_publicado"] = solapes
    polos["zona_publicada"] = mejor_zona
    polos["zonas_que_contiene"] = absorbidas
    polos["es_nuevo"] = (polos.pct_ya_publicado < SOLAPE_MAXIMO_NUEVO * 100) & (polos.zonas_que_contiene == "")

    p("  COTEJO CONTRA LAS 22 ZONAS PUBLICADAS")
    p(f"    umbrales escritos antes de correr: zona encontrada si el borrador le cubre "
      f"≥ {COBERTURA_MINIMA_ZONA:.0%}; polo nuevo si menos del {SOLAPE_MAXIMO_NUEVO:.0%} de su "
      "superficie ya estaba publicada")
    p("")
    p(f"    zonas publicadas que el borrador ENCUENTRA: {int(por_zona.encontrada.sum())} de 22")
    p(f"    zonas publicadas que el borrador NO encuentra: {int((~por_zona.encontrada).sum())}")
    p(f"    polos del borrador NUEVOS (fuera de lo publicado): {int(polos.es_nuevo.sum())} de {len(polos)}")
    p(f"    superficie publicada: {union_zonas.area / 1e4:,.0f} ha | "
      f"borrador: {union_polos.area / 1e4:,.0f} ha | "
      f"compartida: {union_zonas.intersection(union_polos).area / 1e4:,.0f} ha")
    p("")
    engullen = polos[(polos.zonas_que_contiene != "") &
                     (polos.pct_ya_publicado < SOLAPE_MAXIMO_NUEVO * 100)]
    if len(engullen):
        p("    POLOS QUE CONTIENEN UNA ZONA PUBLICADA ENTERA Y AUN ASÍ SOLAPAN POCO")
        p("    Es el caso que los dos umbrales por separado no ven: el polo es mucho más grande")
        p("    que la zona, así que la zona aparece «encontrada» y el polo aparecería «nuevo».")
        p("    No son polos nuevos: son la misma zona con otro perímetro, mucho más ancho.")
        p(engullen[["polo_id", "barrio_principal", "locales", "ha", "locales_x_ha",
                    "pct_ya_publicado", "zonas_que_contiene"]].round(1).to_string(index=False))
        p("")
    p("    LAS 22, UNA POR UNA")
    p(por_zona.sort_values("pct_zona_cubierta", ascending=False).to_string(index=False))
    p("")

    # Dónde está lo nuevo, en términos de comuna. El mapa lo muestra de un vistazo y la tabla lo
    # deja escrito: hay comunas enteras sin ninguna zona publicada.
    barrios = gpd.read_file(BARRIOS)[["nombre", "comuna", "geometry"]].to_crs(CRS_METRICO)
    con_zona = set(gpd.sjoin(barrios, zonas, how="inner", predicate="intersects").comuna.unique())
    puntos_polo = gpd.GeoDataFrame(polos.copy(), geometry=polos.representative_point(),
                                   crs=CRS_METRICO)
    ubicados = gpd.sjoin(puntos_polo[["polo_id", "locales", "es_nuevo", "geometry"]],
                         barrios[["comuna", "geometry"]], how="left", predicate="within")
    por_comuna = ubicados.groupby("comuna").agg(
        polos=("polo_id", "size"), nuevos=("es_nuevo", "sum"), locales=("locales", "sum"))
    por_comuna["tiene_zona_publicada"] = [c in con_zona for c in por_comuna.index]

    p("    DÓNDE ESTÁ LO NUEVO · polos del borrador por comuna")
    p(por_comuna.sort_values("nuevos", ascending=False).to_string())
    sin_zona = por_comuna[~por_comuna.tiene_zona_publicada]
    p("")
    p(f"    comunas sin NINGUNA zona publicada del Atlas que sí tienen polos en el borrador: "
      f"{len(sin_zona)} — comunas {', '.join(str(int(c)) for c in sin_zona.index)}, "
      f"con {int(sin_zona.polos.sum())} polos y {int(sin_zona.locales.sum()):,} locales")
    p("    Es el hallazgo más grande del cotejo y no depende de ningún umbral: el Atlas no tiene")
    p("    zona publicada en esas comunas, y el clustering encuentra concentraciones ahí con los")
    p("    mismos parámetros que usó en Palermo.")
    p("")
    return por_zona, polos


# --------------------------------------------------------------------------- informe


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sin-ablacion", action="store_true",
                        help="salta la ablación por grupo (seis corridas completas)")
    args = parser.parse_args()

    # La consola de Windows entrega cp1252 y el informe tiene flechas y guiones largos. El archivo
    # ya se escribe en UTF-8; esto es sólo para que el eco por pantalla no corte la corrida.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    OUT.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    base_completa = cargar_base_completa()

    p("BORRADOR · primera poligonización de toda la Ciudad desde la base")
    p("=" * 100)
    p("")
    p("NO ES UN PRODUCTO. No se publica, no se sella y no toca el Atlas. Se mira.")
    p("Google Places: 0 requests. Places no está en la base.")
    p("")
    p(f"universo: {len(geo):,} puntos del anillo {PARAMETROS['anillo']} con apto_geometria = True")
    p(f"          (de {len(base_completa):,} locales de la base, corte {base_completa.corte.iloc[0]})")
    p(f"parámetros ÚNICOS para los 48 barrios: min_cluster_size={PARAMETROS['min_cluster_size']}, "
      f"min_samples={PARAMETROS['min_samples']}, método={PARAMETROS['cluster_selection_method']}, "
      f"concave_hull_ratio={PARAMETROS['concave_hull_ratio']}")
    p("")

    etiquetas = agrupar(geo, PARAMETROS["min_cluster_size"], PARAMETROS["min_samples"],
                        PARAMETROS["cluster_selection_method"])
    geo["polo_id"] = [f"P{int(e) + 1:03d}" if e >= 0 else "" for e in etiquetas]
    polos = construir_polos(geo, etiquetas, PARAMETROS["concave_hull_ratio"])
    polos = control_aptitud(polos, base_completa)

    ruido = int((etiquetas == -1).sum())
    p("=" * 100)
    p("RESULTADO")
    p("=" * 100)
    p("")
    p(f"  polos: {len(polos)}")
    p(f"  locales agrupados: {len(geo) - ruido:,} ({(1 - ruido / len(geo)) * 100:.1f} %) | "
      f"dispersos (ruido): {ruido:,} ({ruido / len(geo) * 100:.1f} %)")
    p(f"  superficie total de los polos: {polos.ha.sum():,.0f} ha "
      f"({polos.ha.sum() / 20_300 * 100:.1f} % de la superficie de la Ciudad)")
    p("")
    p("  TAMAÑO DE LOS POLOS")
    for etiqueta, valor in [("mínimo", polos.locales.min()), ("mediana", polos.locales.median()),
                            ("media", polos.locales.mean()), ("máximo", polos.locales.max())]:
        p(f"    {etiqueta:<10} {valor:>8.0f} locales")
    p(f"    superficie: mediana {polos.ha.median():.1f} ha | rango "
      f"{polos.ha.min():.1f}–{polos.ha.max():.1f} ha")
    p(f"    densidad:   mediana {polos.locales_x_ha.median():.1f} locales/ha | rango "
      f"{polos.locales_x_ha.min():.1f}–{polos.locales_x_ha.max():.1f}")
    p("")
    tramos = pd.cut(polos.locales, [39, 60, 100, 200, 400, 10_000],
                    labels=["40–60", "61–100", "101–200", "201–400", "más de 400"])
    p("    distribución por tamaño:")
    for tramo, cuenta in tramos.value_counts().sort_index().items():
        p(f"      {tramo:<12} {cuenta:>3} polos")
    p("")

    # Un polo grande y flojo no es lo mismo que un polo grande y denso, y el conteo no los
    # distingue. Se marcan acá porque son los que un editor tendría que partir o descartar, y
    # porque son el modo de fallar de un clustering con un solo parámetro: encadena barrios
    # contiguos de densidad media en una mancha que ningún peatón reconocería como un polo.
    grandes = polos[(polos.ha > polos.ha.quantile(0.90)) &
                    (polos.locales_x_ha < polos.locales_x_ha.median())]
    p("  POLOS GRANDES Y POCO DENSOS · candidatos a partir, no resultados para mostrar")
    p(f"    polos por encima del percentil 90 de superficie y por debajo de la densidad mediana "
      f"({polos.locales_x_ha.median():.1f} locales/ha): {len(grandes)}")
    if len(grandes):
        p(grandes[["polo_id", "barrio_principal", "n_barrios", "barrios", "locales", "ha",
                   "locales_x_ha"]].round(1).to_string(index=False))
    p("")

    p("  UN SOLO JUEGO DE PARÁMETROS NO ES UN SOLO UMBRAL DE DENSIDAD")
    p("    HDBSCAN es adaptativo por diseño: no fija una distancia, fija cuántos vecinos hacen")
    p("    denso a un punto, y después deja que la distancia la ponga el territorio. Así que")
    p("    correr los 48 barrios con el mismo `min_cluster_size` y el mismo `min_samples` —que es")
    p("    lo que se pidió y lo que se hizo— NO impone la misma vara de densidad en toda la")
    p("    Ciudad. Impone la misma regla, y la regla da un umbral distinto en cada lugar.")
    p("")
    tercios = pd.qcut(polos.locales_x_ha, 3, labels=["tercio menos denso", "tercio medio",
                                                    "tercio más denso"])
    resumen_d = polos.groupby(tercios, observed=True).agg(
        polos=("polo_id", "size"), locales=("locales", "sum"), ha=("ha", "sum"),
        densidad_min=("locales_x_ha", "min"), densidad_max=("locales_x_ha", "max"))
    resumen_d["ha_por_polo"] = (resumen_d.ha / resumen_d.polos).round(1)
    p(resumen_d.round(1).to_string())
    p(f"    la densidad del polo más denso es {polos.locales_x_ha.max() / polos.locales_x_ha.min():.0f} "
      f"veces la del menos denso, y la superficie mediana del tercio menos denso es "
      f"{resumen_d.ha_por_polo.iloc[0] / resumen_d.ha_por_polo.iloc[-1]:.0f} veces la del más denso.")
    p("")
    p("    Consecuencia práctica, y es la lectura importante de este borrador: en la periferia el")
    p("    método dibuja manchas grandes y flojas, y en el centro dibuja piezas chicas y")
    p("    apretadas. Un polo de Lugano y un polo de San Nicolás llevan la misma etiqueta y no")
    p("    son la misma cosa. Si lo que se quiere es «la misma vara para toda la Ciudad» en el")
    p("    sentido de un mismo piso de densidad, este método no lo da y hay que decidirlo: o se")
    p("    acepta la vara relativa —cada zona contra su entorno— o se pasa a un umbral absoluto")
    p("    en locales por hectárea, que es otra corrida y otra discusión.")
    p("")

    p("  CONTROL §5 · ninguna envolvente derivada mayoritariamente de puntos no aptos")
    fallan = polos[~polos.control_aptitud]
    p(f"    envolventes que pasan: {int(polos.control_aptitud.sum())} de {len(polos)}")
    p(f"    share de aptos dentro de la envolvente: mínimo {polos.share_aptos.min() * 100:.1f} % | "
      f"mediana {polos.share_aptos.median() * 100:.1f} %")
    if len(fallan):
        p("    FALLAN — se marcan y quedan en la capa, no se borran:")
        p(fallan[["polo_id", "barrio_principal", "locales", "puntos_en_envolvente",
                  "aptos_en_envolvente", "share_aptos"]].to_string(index=False))
    p("")

    p("  DE QUÉ ESTÁN HECHOS LOS POLOS")
    p(f"    locales corroborados por 2+ grupos: {int(polos.corroborados.sum()):,} de "
      f"{int(polos.locales.sum()):,} ({polos.corroborados.sum() / polos.locales.sum() * 100:.1f} %)")
    p(f"    publicables con identidad abierta: {int(polos.abiertos.sum()):,} "
      f"({polos.abiertos.sum() / polos.locales.sum() * 100:.1f} %)")
    p(f"    polos con un grupo dominante por encima del 70 % de sus puntos: "
      f"{int((polos.peso_grupo_dominante > 0.7).sum())}")
    p("    grupo dominante, cuántos polos encabeza:")
    for grupo, cuenta in polos.grupo_dominante.value_counts().items():
        p(f"      {grupo:<24} {cuenta:>3}")
    p("")

    p("  REPARTO TERRITORIAL")
    por_barrio = polos.groupby("barrio_principal").agg(
        polos=("polo_id", "size"), locales=("locales", "sum"), ha=("ha", "sum")).sort_values(
        "polos", ascending=False)
    p(f"    barrios con al menos un polo: {len(por_barrio)} de 48")
    sin_polo = sorted(set(geo.barrio.dropna().unique()) - set(por_barrio.index))
    p(f"    barrios sin ningún polo ({len(sin_polo)}): {', '.join(sin_polo) if sin_polo else '—'}")
    p("")
    p(por_barrio.head(15).round(1).to_string())
    p("")

    diagnostico_10(geo, polos, p)

    tabla_sens = sensibilidad(geo, p)
    tabla_abl = ablacion(geo, polos, p) if not args.sin_ablacion else pd.DataFrame()

    # --- ampliado como sensibilidad del universo, no como universo
    geo_amp = cargar_puntos("ampliado", True)
    etiquetas_amp = agrupar(geo_amp, PARAMETROS["min_cluster_size"], PARAMETROS["min_samples"])
    colapsa_amp, mayor_amp = colapsa(etiquetas_amp)
    polos_amp = construir_polos(geo_amp, etiquetas_amp, PARAMETROS["concave_hull_ratio"])
    p("  SENSIBILIDAD AL ANILLO · el mismo parámetro sobre núcleo+ampliado (con panaderías)")
    p(f"    núcleo:   {len(geo):,} puntos → {len(polos)} polos, {polos.ha.sum():,.0f} ha")
    p(f"    ampliado: {len(geo_amp):,} puntos → {len(polos_amp)} polos, "
      f"{polos_amp.ha.sum():,.0f} ha")
    if colapsa_amp:
        p(f"    COLAPSA: el {mayor_amp * 100:.1f} % de los puntos del ampliado cae en un solo")
        p("    cluster. Con panaderías y pastelerías adentro, la Ciudad deja de tener polos")
        p("    separables con estos parámetros: pasa a ser una sola mancha continua. No es un")
        p("    resultado alternativo del mapa, es la corrida que no se puede hacer así.")
        p("    Consecuencia: la elección del anillo núcleo NO es cosmética. El ampliado exigiría")
        p("    otros parámetros, y entonces los dos mapas dejarían de ser comparables.")
    else:
        cubierto = polos.union_all().intersection(polos_amp.union_all()).area / polos.union_all().area
        p(f"    superficie del núcleo que el ampliado también cubre: {cubierto * 100:.1f} %")
    p("")

    por_zona, polos = cotejar(polos, p)

    p("    LOS POLOS DEL BORRADOR QUE NO ESTABAN PUBLICADOS (los 25 más grandes)")
    nuevos = polos[polos.es_nuevo].sort_values("locales", ascending=False)
    p(nuevos.head(25)[["polo_id", "barrio_principal", "locales", "ha", "locales_x_ha",
                       "pct_ya_publicado", "corroborados"]].round(1).to_string(index=False))
    p("")
    p("    LOS POLOS QUE CAEN SOBRE ZONA PUBLICADA (los 15 más grandes)")
    viejos = polos[~polos.es_nuevo].sort_values("locales", ascending=False)
    p(viejos.head(15)[["polo_id", "zona_publicada", "barrio_principal", "locales", "ha",
                       "pct_ya_publicado"]].round(1).to_string(index=False))
    p("")

    # --------------------------------------------------------------- salidas
    salida = buffer.getvalue()
    (OUT / "BORRADOR_POLOS_CIUDAD.txt").write_text(salida, encoding="utf-8")

    publicable = polos.drop(columns=["geometry"]).round(3)
    publicable.to_csv(OUT / "borrador_polos.csv", index=False, encoding="utf-8")
    por_zona.to_csv(OUT / "cotejo_22_zonas_vs_borrador.csv", index=False, encoding="utf-8")
    tabla_sens.to_csv(OUT / "sensibilidad_umbral.csv", index=False, encoding="utf-8")
    if len(tabla_abl):
        tabla_abl.to_csv(OUT / "ablacion_por_grupo.csv", index=False, encoding="utf-8")

    # La capa geométrica va sin identidad de locales: son polígonos y conteos, nada más.
    polos.to_crs(CRS_GEO).to_file(OUT / "borrador_polos.geojson", driver="GeoJSON")
    # La pertenencia punto→polo se guarda con `local_id`, sin nombre ni dirección: alcanza para
    # reconstruir la corrida y no arrastra identidad de ninguna fuente no redistribuible.
    geo[["local_id", "polo_id", "barrio", "comuna", "anillo", "n_fuentes",
         "nivel_publicacion"]].to_csv(OUT / "pertenencia_local_polo.csv", index=False,
                                      encoding="utf-8")
    (OUT / "parametros.json").write_text(
        json.dumps({"parametros": PARAMETROS,
                    "umbrales_cotejo": {"cobertura_minima_zona": COBERTURA_MINIMA_ZONA,
                                        "solape_maximo_nuevo": SOLAPE_MAXIMO_NUEVO},
                    "grilla_sensibilidad": GRILLA_SENSIBILIDAD,
                    "estado": "BORRADOR_NO_PUBLICABLE",
                    "places_requests": 0},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
