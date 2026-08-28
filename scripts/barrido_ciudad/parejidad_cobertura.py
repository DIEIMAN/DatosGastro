"""Dos indicadores de parejidad de cobertura de la base, sin esperar el tabulado del INDEC.

El §10 del esquema declara el límite más importante de la base: **no sabe todavía si su cobertura
es pareja**. La solución prevista es el tabulado del Censo Económico por comuna, que Diego está
gestionando. Estos dos indicadores no lo reemplazan: responden la misma pregunta con menos
precisión, con fuentes que ya están disponibles.

  A · Locales de la base sobre parcelas comerciales totales, por barrio.
      El Relevamiento de Usos del Suelo trae `TIPO1` para TODAS las parcelas, no sólo las
      gastronómicas. Las parcelas `UNICOMERCIAL` activas son el denominador: es el universo del
      comercio a la calle, medido caminando, parcela por parcela, en los 48 barrios.

  B · Locales de la base cada mil habitantes, por comuna y por barrio.
      Población en viviendas particulares del Censo Nacional 2022 (INDEC, CC BY 4.0).

QUÉ MIDE CADA UNO, DECLARADO ANTES DE MIRAR EL NÚMERO
-----------------------------------------------------
Ninguno de los dos mide completitud. Los dos miden **variación entre barrios de una razón que,
si la cobertura fuera pareja, debería variar poco por razones de cobertura**. Y los dos mezclan
dos cosas distintas en un solo número:

    locales de la base ÷ parcelas comerciales
        = (locales de la base ÷ parcelas gastronómicas del Relevamiento)   ← cobertura
        × (parcelas gastronómicas del Relevamiento ÷ parcelas comerciales) ← composición real

El segundo factor no es un defecto de la base: es un hecho del territorio. Palermo tiene más
gastronomía por comercio que Villa Riachuelo, y eso no es un sesgo de medición. Por eso el
informe reporta **la descomposición** y no sólo la razón pedida: el factor que habla de cobertura
es el primero.

El primer factor tiene una propiedad que conviene entender antes de leerlo:

  * El Relevamiento **está adentro de la base** (aporta 10.890 de sus 42.342 registros). Así que
    la razón base ÷ Relevamiento es ≥ 1 por construcción, y lo que mide es **cuánto agregan las
    otras seis fuentes por encima del piso que puso el Relevamiento**. Esa es la pregunta de
    cobertura que importa: el Relevamiento solo ya es parejo, porque caminó los 48 barrios.
  * El Relevamiento es **rotativo**: 11 barrios relevados en 2022, 19 en 2023, 18 en 2024. No hay
    foto simultánea de la Ciudad. La tabla reporta el año de cada barrio y el informe controla si
    la razón se ordena por año, que sería un artefacto y no cobertura.

EXPECTATIVA ESCRITA ANTES DE CORRER
-----------------------------------
Se declara para que el resultado sea falsable y no se acomode la explicación después. La banda no
es un veredicto: es lo que se esperaba, y queda escrita gane o pierda.

  A · cobertura (base ÷ Relevamiento gastronómico): si la cobertura fuera pareja, el coeficiente
      de variación entre barrios estaría por debajo de 0,25 y el cociente p90/p10 por debajo de 2.
  B · locales cada mil habitantes: se espera dispersión ALTA y NO se interpreta como sesgo. La
      gastronomía se concentra donde hay oficinas y turismo, no donde hay camas: San Nicolás y
      Puerto Madero tienen que dar altísimo por razones reales. El indicador B sirve para
      presentar y para detectar el caso extremo, no para diagnosticar cobertura.

LO QUE NINGUNO DE LOS DOS PUEDE HACER
-------------------------------------
Distinguir un barrio con poca gastronomía de un barrio poco cubierto **en términos absolutos**.
Para eso hace falta un conteo externo del mismo universo, y eso sigue siendo el tabulado del
Censo Económico. Lo que sí hacen es mostrar si la base se aparta de una medición homogénea del
territorio de manera desigual entre barrios.

FUENTES
-------
  Relevamiento de Usos del Suelo 2022-2024 · GCBA · CC-BY-2.5-AR
      data/fuentes_externas/usos_suelo/rus_2022_2024.csv   (ver perfilar_usos_suelo.py)
  Censo Nacional de Población, Hogares y Viviendas 2022 · INDEC · CC BY 4.0
      radios censales 2022 con POB_TOT_P, y la tabla de personas por radio como control cruzado
      (ver bajar_censo_2022.py)

Uso:
  .venv/Scripts/python.exe scripts/barrido_ciudad/parejidad_cobertura.py
"""
from __future__ import annotations

import io
import sys
import unicodedata
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

BASE_LOCAL = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "base" / "local.csv"
RUS_CSV = ROOT / "data" / "fuentes_externas" / "usos_suelo" / "rus_2022_2024.csv"
CENSO_DIR = ROOT / "data" / "fuentes_externas" / "censo"
RADIOS_ZIP = CENSO_DIR / "radios-censales-2022.zip"
PERSONAS_ZIP = CENSO_DIR / "02-caba-2022.zip"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
GEN = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "generado"

CRS_METRICO = "EPSG:5347"

# Las tres comunas del sur, que son las que el §0 del esquema señala como el riesgo: si la
# cobertura se desploma en algún lado, es acá. Se declara antes de mirar, no después.
COMUNAS_SUR = [4, 8, 9]

# Población total en viviendas particulares de CABA, Censo 2022. Control cruzado entre los dos
# archivos del INDEC: el campo POB_TOT_P del shapefile de radios y la tabla de personas por radio
# tienen que dar exactamente lo mismo.
POBLACION_CABA_2022 = 3_095_454


def plegar(texto: object) -> str:
    """Nombre de barrio comparable entre fuentes: sin acentos, mayúsculas, sin espacios sobrantes."""
    return (unicodedata.normalize("NFKD", str(texto))
            .encode("ascii", "ignore").decode().upper().strip())


class InsumoFaltante(RuntimeError):
    """Falta un archivo que este script no descarga."""


# ---------------------------------------------------------------------------- insumos


def cargar_base() -> pd.DataFrame:
    """La base gastronómica, con barrio asignado por geometría en su construcción."""
    base = pd.read_csv(BASE_LOCAL, low_memory=False)
    base["barrio_k"] = base.barrio.map(plegar)
    return base


def cargar_rus() -> pd.DataFrame:
    """Relevamiento completo, con la reparación de codificación de `perfilar_usos_suelo`."""
    if not RUS_CSV.exists():
        raise InsumoFaltante(
            f"falta {RUS_CSV.relative_to(ROOT)} — la URL de descarga está en el docstring de "
            "scripts/barrido_ciudad/perfilar_usos_suelo.py")
    from perfilar_usos_suelo import cargar
    rus = cargar()
    rus["barrio_k"] = rus.BARRIO.map(plegar)
    return rus


def cargar_poblacion_por_radio() -> gpd.GeoDataFrame:
    """Radios censales 2022 de CABA con población en viviendas particulares.

    Control cruzado obligatorio: el total del shapefile tiene que coincidir con el de la tabla de
    personas por radio. Son dos archivos distintos del mismo organismo; si no coinciden, uno de
    los dos no es lo que dice ser y la corrida corta.
    """
    if not RADIOS_ZIP.exists():
        raise InsumoFaltante(
            f"falta {RADIOS_ZIP.relative_to(ROOT)} — correr scripts/barrido_ciudad/bajar_censo_2022.py")
    radios = gpd.read_file(f"zip://{RADIOS_ZIP.as_posix()}!radios-censales-2022.shp",
                           where="cod_prov = '02'")
    radios["comuna"] = radios.cod_dep.astype(int) // 7

    total_shp = int(radios.POB_TOT_P.sum())
    total_tabla = _total_personas_de_la_tabla()
    if total_tabla is not None and total_shp != total_tabla:
        raise InsumoFaltante(
            f"los dos archivos del Censo 2022 no coinciden: shapefile {total_shp:,} vs tabla de "
            f"personas {total_tabla:,}. No se sigue hasta entender la diferencia.")
    if total_shp != POBLACION_CABA_2022:
        raise InsumoFaltante(
            f"la población de CABA cambió respecto de la declarada: {total_shp:,} vs "
            f"{POBLACION_CABA_2022:,}. Revisar si el INDEC republicó la base.")
    return radios


def _total_personas_de_la_tabla() -> int | None:
    """Suma de `PERSONA_P02` (sexo al nacer) sobre todos los radios: aplica a toda la población."""
    if not PERSONAS_ZIP.exists():
        return None
    with zipfile.ZipFile(PERSONAS_ZIP) as z, z.open("02-caba-2022-persona.csv") as fh:
        personas = pd.read_csv(fh, usecols=["cod_variable", "cantidad"])
    return int(personas.loc[personas.cod_variable == "PERSONA_P02", "cantidad"].sum())


def cargar_barrios() -> gpd.GeoDataFrame:
    barrios = gpd.read_file(BARRIOS)[["nombre", "comuna", "geometry"]]
    barrios["barrio_k"] = barrios.nombre.map(plegar)
    return barrios


# ------------------------------------------------------------------- indicador A


def locales_con_rus(base: pd.DataFrame) -> pd.Series:
    """Cuántos locales de la base tienen al Relevamiento entre sus fuentes, por barrio.

    Hace visible la parte mecánica de la razón base ÷ Relevamiento. Como el Relevamiento está
    adentro de la base, esa razón nunca puede bajar de 1, y una razón estable podría ser sólo el
    reflejo de que el piso es el mismo en todos lados. La razón que **no** tiene piso mecánico es
    `sin_rus ÷ rus_gastro`: cuánto agregan las otras seis fuentes por cada parcela que el
    Relevamiento encontró caminando. Si esa también es estable, la parejidad no es un artefacto.
    """
    fuentes = base.fuentes.fillna("").str.split(";")
    tiene = fuentes.map(lambda fs: "RUS" in fs)
    return base[tiene].groupby("barrio_k").local_id.count()


def indicador_a(base: pd.DataFrame, rus: pd.DataFrame) -> pd.DataFrame:
    """Locales de la base sobre parcelas comerciales del Relevamiento, por barrio.

    Denominador: parcelas `UNICOMERCIAL` con `ESTADO = ACTIVO`, contadas por SMP distinto. Es el
    universo donde vive el comercio a la calle y donde el propio Relevamiento ubica el 100 % de
    sus registros gastronómicos: el control 1 de `perfilar_usos_suelo` verificó que todos los
    valores de TIPO2 gastronómicos caen bajo `TIPO1 = UNICOMERCIAL`. Contar filas en vez de
    parcelas daría de más, porque una parcela con dos usos aparece dos veces.

    Numerador del Relevamiento: el mismo filtro que usa `build_base_gastronomica.cargar_rus_base`,
    para que la razón base ÷ Relevamiento no mezcle dos definiciones.
    """
    from perfilar_usos_suelo import anillos
    nucleo_tipos, ampliado_tipos = anillos()

    activo = rus[(rus.ESTADO == "ACTIVO")]
    unicomercial = activo[activo.TIPO1 == "UNICOMERCIAL"]
    multicomercial = activo[activo.TIPO1.isin(["UNICOMERCIAL", "MULTICOMERCIAL"])]

    tabla = pd.DataFrame({
        "comercial": unicomercial.groupby("barrio_k").SMP.nunique(),
        "comercial_con_multi": multicomercial.groupby("barrio_k").SMP.nunique(),
        "rus_gastro": unicomercial[unicomercial.TIPO2.isin(ampliado_tipos)].groupby("barrio_k").SMP.nunique(),
        "rus_nucleo": unicomercial[unicomercial.TIPO2.isin(nucleo_tipos)].groupby("barrio_k").SMP.nunique(),
        "anio_relevamiento": rus.groupby("barrio_k").ANIO.max(),
    })

    de_la_base = pd.DataFrame({
        "base_total": base.groupby("barrio_k").local_id.count(),
        "base_nucleo": base[base.anillo == "nucleo"].groupby("barrio_k").local_id.count(),
        "base_aptos": base[base.apto_geometria].groupby("barrio_k").local_id.count(),
        "base_con_rus": locales_con_rus(base),
    })
    tabla = tabla.join(de_la_base).fillna(0)
    tabla["base_sin_rus"] = tabla.base_total - tabla.base_con_rus

    # Las tres razones. La pedida es `base_sobre_comercial`; las otras dos son su descomposición,
    # y son las que dicen cuál de los dos factores mueve el número.
    tabla["base_sobre_comercial"] = tabla.base_total / tabla.comercial * 1000
    tabla["rus_sobre_comercial"] = tabla.rus_gastro / tabla.comercial * 1000
    tabla["cobertura"] = tabla.base_total / tabla.rus_gastro
    # La misma razón sin el piso mecánico: cuánto agregan las otras seis fuentes por cada parcela
    # que el Relevamiento encontró caminando. Ver `locales_con_rus`.
    tabla["aporte_otras_fuentes"] = tabla.base_sin_rus / tabla.rus_gastro
    return tabla.sort_values("cobertura", ascending=False)


# ------------------------------------------------------------------- indicador B


def poblacion_por_barrio(radios: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame,
                         p) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Reparte la población de cada radio censal entre los barrios que toca, por área.

    Los radios del INDEC y los barrios del GCBA son dos trazados distintos y no encajan. En vez de
    suponer que sí, se reparte la población de cada radio en proporción al área que aporta a cada
    barrio, y se reporta cuánta población quedó en radios partidos: si esa fracción fuera grande,
    la cifra por barrio sería un reparto y no una medición, y habría que decirlo en el informe.

    El reparto por área supone densidad uniforme dentro del radio. Es falso en radios con plazas o
    playas ferroviarias, y por eso la comuna —donde no hay reparto ninguno— es la unidad de
    referencia y el barrio es la lectura auxiliar.
    """
    radios_m = radios.to_crs(CRS_METRICO)
    barrios_m = barrios.to_crs(CRS_METRICO)
    radios_m["area_radio"] = radios_m.area

    piezas = gpd.overlay(radios_m[["codigo", "POB_TOT_P", "area_radio", "geometry"]],
                         barrios_m[["barrio_k", "geometry"]], how="intersection")
    piezas["area_pieza"] = piezas.area
    piezas["peso"] = piezas.area_pieza / piezas.groupby("codigo").area_pieza.transform("sum")
    piezas["poblacion"] = piezas.POB_TOT_P * piezas.peso

    partidos = piezas.groupby("codigo").barrio_k.nunique()
    pob_partida = piezas[piezas.codigo.isin(partidos[partidos > 1].index)].POB_TOT_P.groupby(
        piezas.codigo).first().sum()

    p("  reparto de radios censales entre barrios")
    p(f"    radios de CABA: {len(radios_m):,} | radios que tocan más de un barrio: "
      f"{int((partidos > 1).sum()):,} ({(partidos > 1).mean() * 100:.1f} %)")
    p(f"    población en radios partidos: {int(pob_partida):,} "
      f"({pob_partida / radios_m.POB_TOT_P.sum() * 100:.1f} % del total)")
    repartida, total = piezas.poblacion.sum(), radios_m.POB_TOT_P.sum()
    p(f"    población repartida: {repartida:,.0f} de {total:,} "
      f"(perdida contra el borde de la Ciudad: {total - repartida:,.0f})")
    p("")

    por_barrio = piezas.groupby("barrio_k").poblacion.sum().round().astype(int).to_frame("poblacion")
    por_comuna = radios.groupby("comuna").POB_TOT_P.sum().to_frame("poblacion")
    return por_barrio, por_comuna


def indicador_b(base: pd.DataFrame, pob_barrio: pd.DataFrame, pob_comuna: pd.DataFrame,
                barrios: gpd.GeoDataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Locales de la base cada mil habitantes, por barrio y por comuna."""
    por_barrio = pd.DataFrame({
        "base_total": base.groupby("barrio_k").local_id.count(),
        "base_nucleo": base[base.anillo == "nucleo"].groupby("barrio_k").local_id.count(),
    }).join(pob_barrio, how="outer").fillna(0)
    por_barrio = por_barrio.join(barrios.set_index("barrio_k")[["comuna"]])
    por_barrio["locales_x_mil"] = (por_barrio.base_total / por_barrio.poblacion * 1000).round(2)
    por_barrio["nucleo_x_mil"] = (por_barrio.base_nucleo / por_barrio.poblacion * 1000).round(2)

    base_com = base.dropna(subset=["comuna"]).copy()
    base_com["comuna"] = base_com.comuna.astype(int)
    por_comuna = pd.DataFrame({
        "base_total": base_com.groupby("comuna").local_id.count(),
        "base_nucleo": base_com[base_com.anillo == "nucleo"].groupby("comuna").local_id.count(),
    }).join(pob_comuna, how="outer").fillna(0)
    por_comuna["locales_x_mil"] = (por_comuna.base_total / por_comuna.poblacion * 1000).round(2)
    por_comuna["nucleo_x_mil"] = (por_comuna.base_nucleo / por_comuna.poblacion * 1000).round(2)
    return por_barrio.sort_values("locales_x_mil", ascending=False), por_comuna


# ------------------------------------------------------------------- dispersión


def dispersion(serie: pd.Series) -> dict:
    """Las tres medidas que se declararon en la expectativa, sin elegirlas después de ver el dato."""
    s = serie.replace([np.inf, -np.inf], np.nan).dropna()
    p10, p90 = s.quantile(0.10), s.quantile(0.90)
    return {
        "n": int(len(s)),
        "mediana": float(s.median()),
        "cv": float(s.std(ddof=1) / s.mean()),
        "p10": float(p10),
        "p90": float(p90),
        "p90_sobre_p10": float(p90 / p10) if p10 else float("nan"),
        "min": float(s.min()), "max": float(s.max()),
        "barrio_min": str(s.idxmin()), "barrio_max": str(s.idxmax()),
    }


def linea_dispersion(nombre: str, d: dict, banda_cv: float | None, banda_p90p10: float | None) -> str:
    veredicto = ""
    if banda_cv is not None:
        ok_cv = d["cv"] < banda_cv
        ok_r = d["p90_sobre_p10"] < banda_p90p10
        veredicto = f"  [{'dentro' if ok_cv and ok_r else 'FUERA'} de la banda escrita]"
    return (f"    {nombre:<34} mediana {d['mediana']:>7.2f} | CV {d['cv']:.2f} | "
            f"p90/p10 {d['p90_sobre_p10']:.2f} | rango {d['min']:.2f}–{d['max']:.2f}"
            f" ({d['barrio_min']} … {d['barrio_max']}){veredicto}")


# ------------------------------------------------------------------- informe


def main() -> int:
    GEN.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args):
        print(*args, file=buffer)

    base = cargar_base()
    rus = cargar_rus()
    barrios = cargar_barrios()
    radios = cargar_poblacion_por_radio()

    p("Parejidad de la cobertura de la base · dos indicadores disponibles hoy")
    p("=" * 88)
    p("")
    p("Ninguno de los dos es el denominador del Censo Económico. Los dos responden la misma")
    p("pregunta con menor precisión: si la base se aparta de una medición homogénea del")
    p("territorio de manera desigual entre barrios.")
    p("")
    p(f"base: {len(base):,} locales, corte {base.corte.iloc[0]}")
    p(f"Relevamiento de Usos del Suelo: {rus.SMP.nunique():,} parcelas, relevamiento rotativo 2022-2024")
    p(f"Censo 2022: {int(radios.POB_TOT_P.sum()):,} personas en viviendas particulares, "
      f"{len(radios):,} radios")
    p("")

    # ------------------------------------------------------------------ A
    p("=" * 88)
    p("INDICADOR A · locales de la base sobre parcelas comerciales, por barrio")
    p("=" * 88)
    p("")
    a = indicador_a(base, rus)
    p(f"  CABA: {int(a.base_total.sum()):,} locales de la base | "
      f"{int(a.rus_gastro.sum()):,} parcelas gastronómicas del Relevamiento | "
      f"{int(a.comercial.sum()):,} parcelas comerciales activas")
    p(f"  razón pedida (locales cada 1.000 parcelas comerciales), Ciudad: "
      f"{a.base_total.sum() / a.comercial.sum() * 1000:.1f}")
    p(f"  descomposición, Ciudad: cobertura {a.base_total.sum() / a.rus_gastro.sum():.2f} × "
      f"composición {a.rus_gastro.sum() / a.comercial.sum() * 1000:.1f} por mil")
    p("")
    p("  DISPERSIÓN ENTRE LOS 48 BARRIOS")
    p(linea_dispersion("razón pedida (base/comercial)", dispersion(a.base_sobre_comercial), None, None))
    p(linea_dispersion("composición (RUS/comercial)", dispersion(a.rus_sobre_comercial), None, None))
    p(linea_dispersion("COBERTURA (base/RUS gastro)", dispersion(a.cobertura), 0.25, 2.0))
    p(linea_dispersion("  ídem, sin el piso mecánico", dispersion(a.aporte_otras_fuentes), 0.25, 2.0))
    p("")
    p("  El primero mezcla los otros dos. El que habla de la base es el tercero, y el cuarto es")
    p("  el mismo sin la parte que no puede bajar de 1 porque el Relevamiento está adentro.")
    p("")
    p("  QUIÉN ROMPE LA BANDA DEL CV, mirado después de ver el número y rotulado como tal:")
    fuera = a[a.cobertura > a.cobertura.quantile(0.90)][["comercial", "rus_gastro", "base_total", "cobertura"]]
    p(fuera.to_string())
    recortada = a[(a.cobertura >= a.cobertura.quantile(0.05)) & (a.cobertura <= a.cobertura.quantile(0.95))]
    p(f"    sin el 5 % de cada cola: CV {recortada.cobertura.std(ddof=1) / recortada.cobertura.mean():.2f} "
      f"| rango {recortada.cobertura.min():.2f}–{recortada.cobertura.max():.2f} "
      f"({len(recortada)} barrios)")
    p("    Este recorte NO estaba declarado antes de correr. Se informa como diagnóstico de qué")
    p("    mueve el CV, no como veredicto que reemplace al de la banda escrita.")
    p("")

    p("  ¿la cobertura se ordena por el año del relevamiento? (sería artefacto, no cobertura)")
    for anio, grupo in a.groupby("anio_relevamiento"):
        p(f"    {int(anio)}: {len(grupo):>2} barrios | cobertura mediana {grupo.cobertura.median():.2f} "
          f"| composición mediana {grupo.rus_sobre_comercial.median():.1f} por mil")
    p("")

    p("  ¿la cobertura cae en el sur? (comunas 4, 8 y 9 — el riesgo declarado en el §0)")
    a_com = a.join(barrios.set_index("barrio_k")[["comuna"]])
    sur = a_com[a_com.comuna.isin(COMUNAS_SUR)]
    resto = a_com[~a_com.comuna.isin(COMUNAS_SUR)]
    p(f"    sur   ({len(sur)} barrios): cobertura mediana {sur.cobertura.median():.2f} | "
      f"composición mediana {sur.rus_sobre_comercial.median():.1f} por mil | "
      f"razón pedida {sur.base_sobre_comercial.median():.1f}")
    p(f"    resto ({len(resto)} barrios): cobertura mediana {resto.cobertura.median():.2f} | "
      f"composición mediana {resto.rus_sobre_comercial.median():.1f} por mil | "
      f"razón pedida {resto.base_sobre_comercial.median():.1f}")
    p("")

    # Control: el denominador usa el campo BARRIO del Relevamiento (la parcela sabe en qué barrio
    # está) y el numerador usa el barrio que la base asigna por geometría. Son dos atribuciones
    # distintas y si discreparan mucho, la razón por barrio estaría comparando dos recortes.
    p("  CONTROL · las dos atribuciones de barrio, la del Relevamiento y la geométrica de la base")
    desvio = (a.base_con_rus - a.rus_gastro).abs()
    p(f"    locales de la base con fuente RUS: {int(a.base_con_rus.sum()):,} | "
      f"parcelas gastronómicas del Relevamiento: {int(a.rus_gastro.sum()):,}")
    p(f"    desvío absoluto por barrio: mediana {desvio.median():.0f} | máximo {desvio.max():.0f} "
      f"({desvio.idxmax()}) | suma {int(desvio.sum()):,} "
      f"({desvio.sum() / a.rus_gastro.sum() * 100:.1f} % del universo)")
    p("")

    cols = ["comercial", "rus_gastro", "base_total", "base_sin_rus", "base_sobre_comercial",
            "rus_sobre_comercial", "cobertura", "aporte_otras_fuentes", "anio_relevamiento"]
    vista = a[cols].copy()
    for columna in ("base_sobre_comercial", "rus_sobre_comercial"):
        vista[columna] = vista[columna].round(1)
    for columna in ("cobertura", "aporte_otras_fuentes"):
        vista[columna] = vista[columna].round(2)
    p("  los 10 barrios donde la base más se despega del Relevamiento:")
    p(vista.head(10).to_string())
    p("")
    p("  los 10 donde menos:")
    p(vista.tail(10).to_string())
    p("")

    # ------------------------------------------------------------------ B
    p("=" * 88)
    p("INDICADOR B · locales de la base cada mil habitantes")
    p("=" * 88)
    p("")
    pob_barrio, pob_comuna = poblacion_por_barrio(radios, barrios, p)
    b_barrio, b_comuna = indicador_b(base, pob_barrio, pob_comuna, barrios)

    p(f"  CABA: {int(b_comuna.base_total.sum()):,} locales / "
      f"{int(b_comuna.poblacion.sum()):,} habitantes = "
      f"{b_comuna.base_total.sum() / b_comuna.poblacion.sum() * 1000:.2f} locales cada mil")
    p("")
    p("  POR COMUNA (unidad exacta: la comuna es el departamento censal, sin reparto)")
    p(b_comuna[["base_total", "base_nucleo", "poblacion", "locales_x_mil", "nucleo_x_mil"]]
      .sort_values("locales_x_mil", ascending=False).to_string())
    p("")
    p(linea_dispersion("locales cada mil (comuna)", dispersion(b_comuna.locales_x_mil), None, None))
    p(linea_dispersion("locales cada mil (barrio)", dispersion(b_barrio.locales_x_mil), None, None))
    p("")
    p("  Se esperaba dispersión alta y se obtuvo dispersión alta: NO es un diagnóstico de")
    p("  cobertura. La gastronomía se ubica donde hay oficinas y turismo, no donde hay camas.")
    p("")
    p("  los 10 barrios con más locales por habitante:")
    p(b_barrio.head(10)[["base_total", "poblacion", "locales_x_mil", "comuna"]].to_string())
    p("")
    p("  los 10 con menos:")
    p(b_barrio.tail(10)[["base_total", "poblacion", "locales_x_mil", "comuna"]].to_string())
    p("")
    sur_b = b_comuna.loc[b_comuna.index.isin(COMUNAS_SUR)]
    resto_b = b_comuna.loc[~b_comuna.index.isin(COMUNAS_SUR)]
    p(f"  sur (comunas 4, 8, 9): {sur_b.locales_x_mil.median():.2f} locales cada mil | "
      f"resto: {resto_b.locales_x_mil.median():.2f}")
    p("")

    salida = buffer.getvalue()
    (GEN / "PAREJIDAD_COBERTURA.txt").write_text(salida, encoding="utf-8")
    a.to_csv(GEN / "parejidad_a_parcelas_comerciales.csv", encoding="utf-8")
    b_barrio.to_csv(GEN / "parejidad_b_por_barrio.csv", encoding="utf-8")
    b_comuna.to_csv(GEN / "parejidad_b_por_comuna.csv", encoding="utf-8")

    print(salida)
    print(f"escrito en {GEN.relative_to(ROOT)}: PAREJIDAD_COBERTURA.txt, "
          "parejidad_a_parcelas_comerciales.csv, parejidad_b_por_barrio.csv, "
          "parejidad_b_por_comuna.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
