# -*- coding: utf-8 -*-
"""Perfila las fuentes candidatas al universo gastronomico definitivo (solo lectura).

Linea experimental de diseno del pipeline de microzonas (PolosGastro).
Objetivo: respaldar con numeros reales los documentos metodologicos de
`docs/polos_gastro/experimentos/diseno_pipeline_definitivo/`.

Que hace:
- Perfila F01 (oferta registrada) y F02 (habilitaciones gastronomicas) desde
  `data/processed/` (solo lectura; el pipeline NO se regenera ni se modifica).
- Mide cobertura geografica (coordenadas, barrio/comuna determinados) por fuente.
- Estima solapamiento F01/F02 via `id_ubicacion` compartido en `dim_ubicacion`
  (indicador de la magnitud del problema de deduplicacion).
- Asigna comuna real por punto (point-in-polygon con `comunas_caba.geojson`)
  para medir sesgo territorial de cada fuente.
- Perfila el universo semilla de PolosGastro (106 locales, Fase 13) como referencia.

Salidas (experimentales, no institucionales):
- outputs/polos_gastro/experimentos/diseno_pipeline_definitivo/perfil_fuentes_universo.md
- outputs/polos_gastro/experimentos/diseno_pipeline_definitivo/cobertura_por_comuna.csv

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/perfilar_fuentes_universo_definitivo.py
"""

from __future__ import annotations

import os
from datetime import date

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PROCESSED = os.path.join(RAIZ, "data", "processed")
SALIDA = os.path.join(
    RAIZ, "outputs", "polos_gastro", "experimentos", "diseno_pipeline_definitivo"
)
COMUNAS_GEOJSON = os.path.join(RAIZ, "PolosGastro", "cartografia", "comunas_caba.geojson")
SEMILLA_CSV = os.path.join(
    RAIZ, "outputs", "polos_gastro", "fase13_mapas", "tablas", "locales_para_mapa_revision.csv"
)

# Bounding box amplio de CABA para descartar coordenadas claramente erroneas.
LAT_MIN, LAT_MAX = -34.75, -34.50
LON_MIN, LON_MAX = -58.60, -58.30


def pct(parte: int, total: int) -> str:
    if total == 0:
        return "s/d"
    return f"{100.0 * parte / total:.1f} %"


def cargar_comunas() -> gpd.GeoDataFrame:
    comunas = gpd.read_file(COMUNAS_GEOJSON)
    col_nombre = None
    for candidata in ("COMUNAS", "comuna", "COMUNA", "nombre", "NOMBRE"):
        if candidata in comunas.columns:
            col_nombre = candidata
            break
    if col_nombre is None:
        col_nombre = [c for c in comunas.columns if c != "geometry"][0]
    comunas = comunas[[col_nombre, "geometry"]].rename(columns={col_nombre: "comuna_geo"})
    comunas["comuna_geo"] = comunas["comuna_geo"].astype(str)
    return comunas


def asignar_comuna(df: pd.DataFrame, comunas: gpd.GeoDataFrame) -> pd.Series:
    """Asigna comuna por point-in-polygon a filas con lat/lon validas."""
    validas = df.dropna(subset=["latitud", "longitud"])
    puntos = gpd.GeoDataFrame(
        validas[[]],
        geometry=[Point(xy) for xy in zip(validas["longitud"], validas["latitud"])],
        crs=comunas.crs,
    )
    join = gpd.sjoin(puntos, comunas, how="left", predicate="within")
    # sjoin puede duplicar por bordes; conservar primera asignacion por indice
    join = join[~join.index.duplicated(keep="first")]
    return join["comuna_geo"].reindex(df.index)


def perfil_f01(dim_ubi: pd.DataFrame, comunas: gpd.GeoDataFrame):
    fact = pd.read_csv(os.path.join(PROCESSED, "fact_establecimiento.csv"), dtype=str)
    n_total = len(fact)
    gastro = fact[fact["es_gastronomico"] == "si"].copy()
    n_gastro = len(gastro)

    gastro = gastro.merge(
        dim_ubi[["id_ubicacion", "latitud", "longitud", "barrio", "calidad_geo"]],
        on="id_ubicacion",
        how="left",
    )
    gastro["latitud"] = pd.to_numeric(gastro["latitud"], errors="coerce")
    gastro["longitud"] = pd.to_numeric(gastro["longitud"], errors="coerce")
    con_coord = gastro.dropna(subset=["latitud", "longitud"])
    en_caba = con_coord[
        con_coord["latitud"].between(LAT_MIN, LAT_MAX)
        & con_coord["longitud"].between(LON_MIN, LON_MAX)
    ]
    barrio_ok = gastro[~gastro["barrio"].isin(["No determinado", "", None])].dropna(
        subset=["barrio"]
    )

    gastro["comuna_geo"] = asignar_comuna(gastro, comunas)
    por_comuna = (
        gastro.dropna(subset=["comuna_geo"]).groupby("comuna_geo").size().rename("f01_oferta")
    )
    top_cat = gastro["categoria_gastronomica_inferida"].value_counts().head(8)

    resumen = {
        "filas_totales": n_total,
        "gastronomicos_si": n_gastro,
        "con_coordenadas": len(con_coord),
        "coords_en_bbox_caba": len(en_caba),
        "barrio_determinado": len(barrio_ok),
        "ubicaciones_unicas": gastro["id_ubicacion"].nunique(),
        "top_categorias": top_cat,
    }
    return gastro, por_comuna, resumen


def perfil_f02(dim_ubi: pd.DataFrame, comunas: gpd.GeoDataFrame):
    fact = pd.read_csv(os.path.join(PROCESSED, "fact_habilitacion_gastronomica.csv"), dtype=str)
    n_total = len(fact)
    gastro = fact[fact["es_gastronomico"] == "si"].copy()
    n_gastro = len(gastro)

    gastro = gastro.merge(
        dim_ubi[["id_ubicacion", "latitud", "longitud"]].rename(
            columns={"latitud": "lat_ubi", "longitud": "lon_ubi"}
        ),
        on="id_ubicacion",
        how="left",
    )
    gastro["latitud"] = pd.to_numeric(gastro["lat_ubi"], errors="coerce")
    gastro["longitud"] = pd.to_numeric(gastro["lon_ubi"], errors="coerce")
    con_coord = gastro.dropna(subset=["latitud", "longitud"])

    anios = pd.to_datetime(gastro["fecha_habilitacion"], errors="coerce").dt.year
    rango = (
        f"{int(anios.min())}-{int(anios.max())}" if anios.notna().any() else "sin fechas parseables"
    )
    por_anio = anios.value_counts().sort_index()

    dir_unicas = gastro["direccion_original"].str.strip().str.upper().nunique()
    ubi_unicas = gastro["id_ubicacion"].nunique()

    gastro["comuna_geo"] = asignar_comuna(gastro, comunas)
    por_comuna = (
        gastro.dropna(subset=["comuna_geo"])
        .groupby("comuna_geo")
        .size()
        .rename("f02_habilitaciones")
    )
    top_rubros = gastro["categoria_gastronomica_inferida"].value_counts().head(8)

    resumen = {
        "filas_totales": n_total,
        "gastronomicos_si": n_gastro,
        "con_coordenadas": len(con_coord),
        "direcciones_unicas": dir_unicas,
        "ubicaciones_unicas": ubi_unicas,
        "rango_fechas": rango,
        "habilitaciones_por_anio": por_anio,
        "top_categorias": top_rubros,
    }
    return gastro, por_comuna, resumen


def perfil_semilla() -> dict:
    semilla = pd.read_csv(SEMILLA_CSV)
    con_coord = semilla.dropna(subset=["lat", "lon"])
    return {
        "filas": len(semilla),
        "con_coordenadas": len(con_coord),
        "polos": semilla["polo"].nunique(),
        "subzonas": semilla["subzona"].nunique(),
        "duplicados_probables": int((semilla["estado_consolidado"] == "duplicado_probable").sum()),
    }


def main() -> None:
    os.makedirs(SALIDA, exist_ok=True)
    comunas = cargar_comunas()

    dim_ubi = pd.read_csv(os.path.join(PROCESSED, "dim_ubicacion.csv"), dtype=str)

    f01, f01_comuna, r01 = perfil_f01(dim_ubi, comunas)
    f02, f02_comuna, r02 = perfil_f02(dim_ubi, comunas)
    rs = perfil_semilla()

    # Solapamiento F01/F02 por id_ubicacion compartido (misma direccion normalizada USIG).
    ubi_f01 = set(f01["id_ubicacion"].dropna())
    ubi_f02 = set(f02["id_ubicacion"].dropna())
    inter = ubi_f01 & ubi_f02

    cobertura = (
        pd.concat([f01_comuna, f02_comuna], axis=1).fillna(0).astype(int).sort_index()
    )
    cobertura.index.name = "comuna"
    cobertura.to_csv(os.path.join(SALIDA, "cobertura_por_comuna.csv"))

    lineas = []
    w = lineas.append
    w("# Perfil de fuentes candidatas — universo gastronomico definitivo")
    w("")
    w(f"**Fecha de corrida:** {date.today().isoformat()}")
    w("**Caracter:** salida experimental de solo lectura. No modifica el pipeline F01-F05.")
    w("Los conteos describen registros administrativos y oferta registrada, **no** locales")
    w("activos (guardrail 5).")
    w("")
    w("## F01 — Oferta de establecimientos gastronomicos (registrada)")
    w("")
    w(f"- Filas en `fact_establecimiento`: {r01['filas_totales']:,}")
    w(f"- Con `es_gastronomico = si`: {r01['gastronomicos_si']:,} "
      f"({pct(r01['gastronomicos_si'], r01['filas_totales'])})")
    w(f"- Gastronomicos con coordenadas: {r01['con_coordenadas']:,} "
      f"({pct(r01['con_coordenadas'], r01['gastronomicos_si'])})")
    w(f"- Coordenadas dentro de bbox CABA: {r01['coords_en_bbox_caba']:,}")
    w(f"- Con barrio determinado en `dim_ubicacion`: {r01['barrio_determinado']:,} "
      f"({pct(r01['barrio_determinado'], r01['gastronomicos_si'])})")
    w(f"- Ubicaciones unicas (`id_ubicacion`): {r01['ubicaciones_unicas']:,}")
    w("")
    w("Top categorias inferidas:")
    w("")
    for cat, n in r01["top_categorias"].items():
        w(f"- {cat}: {n:,}")
    w("")
    w("## F02 — Habilitaciones gastronomicas aprobadas (historicas)")
    w("")
    w(f"- Filas en `fact_habilitacion_gastronomica`: {r02['filas_totales']:,}")
    w(f"- Con `es_gastronomico = si`: {r02['gastronomicos_si']:,} "
      f"({pct(r02['gastronomicos_si'], r02['filas_totales'])})")
    w(f"- Gastronomicas con coordenadas: {r02['con_coordenadas']:,} "
      f"({pct(r02['con_coordenadas'], r02['gastronomicos_si'])})")
    w(f"- Direcciones unicas (texto): {r02['direcciones_unicas']:,}")
    w(f"- Ubicaciones unicas (`id_ubicacion`): {r02['ubicaciones_unicas']:,}")
    w(f"- Rango de fechas de habilitacion: {r02['rango_fechas']}")
    w("")
    w("Habilitaciones gastronomicas por anio (parseables):")
    w("")
    for anio, n in r02["habilitaciones_por_anio"].items():
        w(f"- {int(anio)}: {n:,}")
    w("")
    w("Top categorias inferidas:")
    w("")
    for cat, n in r02["top_categorias"].items():
        w(f"- {cat}: {n:,}")
    w("")
    w("## Solapamiento F01 / F02 (indicador de deduplicacion)")
    w("")
    w("Ambas fuentes comparten `dim_ubicacion` (direccion normalizada USIG), por lo que el")
    w("`id_ubicacion` compartido es un proxy de 'misma direccion en ambas fuentes'. No implica")
    w("que sea el mismo negocio ni que este activo.")
    w("")
    w(f"- Ubicaciones gastronomicas F01: {len(ubi_f01):,}")
    w(f"- Ubicaciones gastronomicas F02: {len(ubi_f02):,}")
    w(f"- Ubicaciones presentes en ambas: {len(inter):,} "
      f"({pct(len(inter), len(ubi_f01))} de F01; {pct(len(inter), len(ubi_f02))} de F02)")
    w("")
    w("## Universo semilla PolosGastro (referencia, Fase 13)")
    w("")
    w(f"- Locales semilla: {rs['filas']} (con coordenadas: {rs['con_coordenadas']})")
    w(f"- Polos: {rs['polos']} — Subzonas: {rs['subzonas']}")
    w(f"- Marcados `duplicado_probable`: {rs['duplicados_probables']}")
    w("")
    w("## Cobertura por comuna (point-in-polygon)")
    w("")
    w("Ver `cobertura_por_comuna.csv`. Conteos por comuna asignada geometricamente a los puntos")
    w("con coordenadas; sirve para leer el sesgo territorial de cada fuente antes de clusterizar.")
    w("")
    tabla = cobertura.reset_index()
    w("| Comuna | F01 oferta | F02 habilitaciones |")
    w("|---|---|---|")
    for _, fila in tabla.iterrows():
        w(f"| {fila['comuna']} | {fila['f01_oferta']:,} | {fila['f02_habilitaciones']:,} |")
    w("")

    ruta_md = os.path.join(SALIDA, "perfil_fuentes_universo.md")
    with open(ruta_md, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lineas))
    print(f"Perfil escrito en: {ruta_md}")
    print(f"Cobertura por comuna: {os.path.join(SALIDA, 'cobertura_por_comuna.csv')}")


if __name__ == "__main__":
    main()
