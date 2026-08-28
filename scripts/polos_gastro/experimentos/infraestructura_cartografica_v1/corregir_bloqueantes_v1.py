# -*- coding: utf-8 -*-
"""Etapa Cal-2/3 — Correccion de los 4 bloqueantes de macrozonas_v1_experimental.

EXPERIMENTAL. NO reemplaza macrozonas_v1_experimental.geojson en el lugar: genera
geometrias ANTES/DESPUES por separado, con metricas y justificacion, para revision
humana (Etapa Cal-3 del pedido). El ensamblado final en una capa candidata es un paso
posterior y explicito (Etapa Cal-5).

Los 4 bloqueantes y su correccion:

1. AVENIDA CORRIENTES x MICROCENTRO (solapamiento 49,2%, 406 entidades compartidas)
   Corrientes se deja intacta (la prueba de pipeline anterior ya mostro que funciona
   bien: 0 clusters sobredimensionados). Se recorta MICROCENTRO restandole la franja
   que ya cubre el corredor de Corrientes (San Nicolas MENOS el corredor real).

2. BELGRANO (confianza baja, aproximacion heredada de fase16 sin verificar)
   Se reemplaza la union de elipses por corredores reales sobre las 3 calles que la
   propia documentacion de fase16 ya usaba como referencia geografica (Juramento para
   Barrio Chino, Libertador para Bajo Belgrano, Cabildo para Belgrano R), recortados al
   barrio oficial.

3. COSTANERA NORTE (corredor sobredimensionado respecto de la evidencia: 225 ha para 5
   entidades concentradas en un tramo de ~2,2 km de los ~4,4 km del corredor actual)
   Se acota el corredor al tramo con evidencia real y se reduce el semiancho de 350 a
   250 m (mas honesto dado lo escaso de la evidencia).

4. CHACARITA (barrio completo, 311,7 ha, para 116 entidades concentradas en ~2x2 km)
   Se reemplaza el barrio completo por barrio ∩ buffer(entidades reales del universo V1
   que ya caen ahi, no la semilla -que esta mal geocodificada para este polo-), radio
   400 m.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/corregir_bloqueantes_v1.py
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from shapely.geometry import box
from shapely.ops import unary_union

REPO = Path(__file__).resolve().parents[4]
SALIDA = REPO / "outputs/polos_gastro/experimentos/infraestructura_cartografica_v1"
CORRECCIONES_DIR = SALIDA / "correcciones_bloqueantes"
CALLEJERO_PATH = REPO / "outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson"
BARRIOS_PATH = REPO / "PolosGastro/cartografia/barrios_caba.geojson"
COMUNAS_PATH = REPO / "PolosGastro/cartografia/comunas_caba.geojson"
PROTOTIPO = REPO / "outputs/polos_gastro/experimentos/pipeline_microzonas_v1"

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"


def limpiar_geometria(geom):
    if geom.geom_type == "GeometryCollection":
        partes = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
        geom = unary_union(partes) if partes else geom
    if not geom.is_valid:
        geom = geom.buffer(0)
    return geom


def cargar_universo() -> gpd.GeoDataFrame:
    ent = pd.read_csv(
        PROTOTIPO / "universo" / "universo_entidades_v1.csv", dtype={"id_ubicacion": str}
    )
    ent = ent[ent["apta_clustering"]].copy()
    return gpd.GeoDataFrame(
        ent, geometry=gpd.points_from_xy(ent["lon"], ent["lat"]), crs=CRS_GEO
    ).to_crs(CRS_METRICO)


def metricas(nombre, geom_m, universo_m):
    dentro = universo_m[universo_m.within(geom_m)]
    area_ha = geom_m.area / 10_000.0
    return {
        "nombre": nombre, "area_ha": round(area_ha, 1), "n_entidades": len(dentro),
        "densidad_ha": round(len(dentro) / area_ha, 2) if area_ha else 0,
    }


def mapa_antes_despues(nombre, geom_antes_m, geom_despues_m, universo_m, path_png,
                       extra_geom=None, extra_color="#7a5c99", extra_label=None):
    fig, axes = plt.subplots(1, 2, figsize=(14, 8))
    bounds_union = unary_union([geom_antes_m, geom_despues_m]).buffer(300).bounds
    for ax, geom, etiqueta in [(axes[0], geom_antes_m, "ANTES"), (axes[1], geom_despues_m, "DESPUES")]:
        ax.set_aspect("equal")
        ax.set_axis_off()
        gpd.GeoSeries([geom], crs=CRS_METRICO).plot(
            ax=ax, color="#2a78d6", alpha=0.35, edgecolor="#2a78d6", linewidth=1.5
        )
        if extra_geom is not None:
            gpd.GeoSeries([extra_geom], crs=CRS_METRICO).boundary.plot(
                ax=ax, color=extra_color, linewidth=1.3, linestyle=(0, (5, 3))
            )
        dentro = universo_m[universo_m.within(geom)]
        ax.scatter(dentro.geometry.x, dentro.geometry.y, c="#1c5cab", s=10, zorder=4)
        ax.set_xlim(bounds_union[0], bounds_union[2])
        ax.set_ylim(bounds_union[1], bounds_union[3])
        area_ha = geom.area / 10_000.0
        ax.set_title(f"{etiqueta}: {len(dentro)} entidades, {area_ha:.1f} ha", fontsize=11.5)
    leyenda = [Line2D([], [], marker="o", linestyle="", markerfacecolor="#1c5cab",
                      markersize=7, label="Entidad del universo V1")]
    if extra_label:
        leyenda.append(Line2D([], [], color=extra_color, linewidth=1.3, linestyle=(0, (5, 3)),
                              label=extra_label))
    axes[0].legend(handles=leyenda, loc="upper left", fontsize=8, frameon=True)
    fig.suptitle(f"EXPERIMENTAL - Correccion de bloqueante: {nombre}", fontsize=13)
    fig.text(0.5, 0.02, "Candidato experimental, pendiente de aprobacion editorial.",
            ha="center", fontsize=8.5, color="#52514e")
    fig.savefig(path_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def corregir_belgrano(barrios_m, callejero_m):
    barrio = barrios_m[barrios_m["nombre"] == "Belgrano"].geometry.iloc[0]
    # Semiancho 250 m (no 400): las 3 avenidas son ejes de referencia documentados
    # (fase16 criterio_geografico), no se busca cubrir todo el barrio con ellas.
    calles = {
        "JURAMENTO AV.": 250, "DEL LIBERTADOR AV.": 250, "CABILDO AV.": 250,
    }
    tramos = []
    for nom, semiancho in calles.items():
        sel = callejero_m[callejero_m["nomoficial"] == nom]
        sel = sel[sel.intersects(barrio.buffer(1000))]
        if len(sel):
            tramos.append(unary_union(sel.geometry).buffer(semiancho))
    corredor = unary_union(tramos)
    return limpiar_geometria(corredor.intersection(barrio))


def corregir_costanera_norte(callejero_m, caba_m):
    # bbox acotado al tramo con evidencia real (las 5 entidades caen entre
    # lat -34.567 y -34.546 aprox.); semiancho reducido de 350 a 250 m: mas
    # honesto dado lo escaso de la evidencia.
    bbox_nuevo = (-58.435, -34.572, -58.400, -34.542)
    bbox_geo = box(*bbox_nuevo)
    bbox_m = gpd.GeoSeries([bbox_geo], crs=CRS_GEO).to_crs(CRS_METRICO).iloc[0]
    tramo = callejero_m[
        (callejero_m["nomoficial"] == "OBLIGADO RAFAEL, AV.COSTANERA")
        & callejero_m.geometry.intersects(bbox_m)
    ]
    eje = unary_union(tramo.geometry)
    corredor = eje.buffer(250).intersection(bbox_m).intersection(caba_m)
    return limpiar_geometria(corredor)


def corregir_chacarita(barrios_m, universo_m, geom_antes_m):
    barrio = barrios_m[barrios_m["nombre"] == "Chacarita"].geometry.iloc[0]
    dentro = universo_m[universo_m.within(geom_antes_m)]
    buffer_entidades = unary_union(dentro.buffer(400))
    return limpiar_geometria(buffer_entidades.intersection(barrio))


def corregir_microcentro(gdf_m):
    san_nicolas = gdf_m[gdf_m["id"] == "MZ_MICROCENTRO_Y_CENTRO"].geometry.iloc[0]
    corrientes = gdf_m[gdf_m["id"] == "MZ_AVENIDA_CORRIENTES"].geometry.iloc[0]
    return limpiar_geometria(san_nicolas.difference(corrientes))


def main() -> None:
    CORRECCIONES_DIR.mkdir(parents=True, exist_ok=True)
    gdf = gpd.read_file(SALIDA / "macrozonas_v1_experimental.geojson")
    gdf_m = gdf.to_crs(CRS_METRICO)
    barrios_m = gpd.read_file(BARRIOS_PATH).to_crs(CRS_METRICO)
    callejero_m = gpd.read_file(CALLEJERO_PATH).to_crs(CRS_METRICO)
    comunas_m = gpd.read_file(COMUNAS_PATH).to_crs(CRS_METRICO)
    caba_m = comunas_m.union_all()
    universo_m = cargar_universo()

    resultados = []

    # --- 1. Microcentro (Corrientes queda igual) ---
    antes = gdf_m[gdf_m["id"] == "MZ_MICROCENTRO_Y_CENTRO"].geometry.iloc[0]
    despues = corregir_microcentro(gdf_m)
    corrientes_geom = gdf_m[gdf_m["id"] == "MZ_AVENIDA_CORRIENTES"].geometry.iloc[0]
    mapa_antes_despues(
        "Microcentro y Centro (recortado por Avenida Corrientes)", antes, despues,
        universo_m, CORRECCIONES_DIR / "antes_despues_microcentro.png",
        extra_geom=corrientes_geom, extra_label="Contorno de Avenida Corrientes (sin cambios)",
    )
    m_antes, m_despues = metricas("Microcentro ANTES", antes, universo_m), metricas("Microcentro DESPUES", despues, universo_m)
    resultados.append((m_antes, m_despues))
    print(f"Microcentro: {m_antes} -> {m_despues}")

    # --- 2. Belgrano ---
    antes = gdf_m[gdf_m["id"] == "MZ_BELGRANO"].geometry.iloc[0]
    despues = corregir_belgrano(barrios_m, callejero_m)
    mapa_antes_despues(
        "Belgrano (corredores reales Juramento/Libertador/Cabildo)", antes, despues,
        universo_m, CORRECCIONES_DIR / "antes_despues_belgrano.png",
    )
    m_antes, m_despues = metricas("Belgrano ANTES", antes, universo_m), metricas("Belgrano DESPUES", despues, universo_m)
    resultados.append((m_antes, m_despues))
    print(f"Belgrano: {m_antes} -> {m_despues}")

    # --- 3. Costanera Norte ---
    antes = gdf_m[gdf_m["id"] == "MZ_COSTANERA_NORTE"].geometry.iloc[0]
    despues = corregir_costanera_norte(callejero_m, caba_m)
    mapa_antes_despues(
        "Costanera Norte (corredor acotado a la evidencia real)", antes, despues,
        universo_m, CORRECCIONES_DIR / "antes_despues_costanera_norte.png",
    )
    m_antes, m_despues = metricas("Costanera Norte ANTES", antes, universo_m), metricas("Costanera Norte DESPUES", despues, universo_m)
    resultados.append((m_antes, m_despues))
    print(f"Costanera Norte: {m_antes} -> {m_despues}")

    # --- 4. Chacarita ---
    antes = gdf_m[gdf_m["id"] == "MZ_CHACARITA"].geometry.iloc[0]
    despues = corregir_chacarita(barrios_m, universo_m, antes)
    mapa_antes_despues(
        "Chacarita (recorte por densidad real de entidades)", antes, despues,
        universo_m, CORRECCIONES_DIR / "antes_despues_chacarita.png",
    )
    m_antes, m_despues = metricas("Chacarita ANTES", antes, universo_m), metricas("Chacarita DESPUES", despues, universo_m)
    resultados.append((m_antes, m_despues))
    print(f"Chacarita: {m_antes} -> {m_despues}")

    # Guardar geometrias corregidas (en EPSG:4326) para ensamblar despues
    correcciones = {
        "MZ_MICROCENTRO_Y_CENTRO": corregir_microcentro(gdf_m),
        "MZ_BELGRANO": corregir_belgrano(barrios_m, callejero_m),
        "MZ_COSTANERA_NORTE": corregir_costanera_norte(callejero_m, caba_m),
        "MZ_CHACARITA": corregir_chacarita(
            barrios_m, universo_m, gdf_m[gdf_m["id"] == "MZ_CHACARITA"].geometry.iloc[0]
        ),
    }
    filas = []
    for id_, geom_m in correcciones.items():
        geom_geo = gpd.GeoSeries([geom_m], crs=CRS_METRICO).to_crs(CRS_GEO).iloc[0]
        geom_geo = limpiar_geometria(geom_geo)
        filas.append({"id": id_, "geometry": geom_geo})
    gdf_correcciones = gpd.GeoDataFrame(filas, crs=CRS_GEO)
    gdf_correcciones.to_file(CORRECCIONES_DIR / "geometrias_corregidas.geojson", driver="GeoJSON")

    tabla = pd.DataFrame(
        [m for par in resultados for m in par]
    )
    tabla.to_csv(CORRECCIONES_DIR / "metricas_antes_despues.csv", index=False)
    print(f"\nGeometrias corregidas -> {CORRECCIONES_DIR / 'geometrias_corregidas.geojson'}")
    print(f"Metricas -> {CORRECCIONES_DIR / 'metricas_antes_despues.csv'}")


if __name__ == "__main__":
    main()
