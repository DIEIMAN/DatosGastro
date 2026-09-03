# -*- coding: utf-8 -*-
"""Etapa 2 — Perfilado del universo gastronomico V1.

EXPERIMENTAL. Lee la salida de s01 y la cartografia de referencia; escribe el
informe de calidad del universo ANTES de clusterizar:

- registros por fuente y entidades tras deduplicar (con % de colapso),
- distribucion por comuna y por barrio (point-in-polygon, no el campo interno),
- densidad aproximada por km2 por comuna,
- % geocodificado, % descartado y por que,
- composicion de la evidencia (solo F01 / solo F02 / ambas; fechada / sin fecha).

Salidas:
- outputs/.../pipeline_microzonas_v1/universo/perfil_universo_v1.md
- outputs/.../pipeline_microzonas_v1/universo/perfil_por_comuna.csv
- outputs/.../pipeline_microzonas_v1/universo/perfil_por_barrio.csv

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/pipeline_microzonas_v1/s02_perfilar_universo.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402


def pct(parte, total) -> str:
    return f"{100.0 * parte / total:.1f} %" if total else "s/d"


def capa_nombre(path, candidatas):
    capa = gpd.read_file(path)
    col = next((c for c in candidatas if c in capa.columns), None)
    if col is None:
        col = [c for c in capa.columns if c != "geometry"][0]
    capa = capa[[col, "geometry"]].rename(columns={col: "nombre"})
    capa["nombre"] = capa["nombre"].astype(str)
    return capa


def asignar(gdf_puntos, capa):
    join = gpd.sjoin(gdf_puntos, capa, how="left", predicate="within")
    join = join[~join.index.duplicated(keep="first")]
    return join["nombre"]


def main() -> None:
    salida = config.SALIDA / "universo"
    ent = pd.read_csv(salida / "universo_entidades_v1.csv", dtype={"id_ubicacion": str})
    with open(salida / "log_reglas_universo_v1.json", encoding="utf-8") as fh:
        log = json.load(fh)

    comunas = capa_nombre(config.COMUNAS_GEOJSON, ("COMUNAS", "comuna", "COMUNA"))
    barrios = capa_nombre(config.BARRIOS_GEOJSON, ("BARRIO", "barrio", "nombre"))

    aptas = ent[ent["apta_clustering"]].copy()
    puntos = gpd.GeoDataFrame(
        aptas[[]], geometry=gpd.points_from_xy(aptas["lon"], aptas["lat"]),
        crs=config.CRS_GEO,
    )
    aptas["comuna_geo"] = asignar(puntos, comunas).values
    aptas["barrio_geo"] = asignar(puntos, barrios).values

    # Densidad por comuna: entidades / km2 de superficie oficial de la comuna.
    com_m = comunas.to_crs(config.CRS_METRICO)
    com_m["km2"] = com_m.geometry.area / 1e6
    por_comuna = (
        aptas.groupby("comuna_geo").size().rename("entidades").reset_index()
        .merge(com_m[["nombre", "km2"]], left_on="comuna_geo", right_on="nombre")
        .drop(columns="nombre")
    )
    por_comuna["densidad_km2"] = (por_comuna["entidades"] / por_comuna["km2"]).round(1)
    por_comuna["participacion"] = (
        100.0 * por_comuna["entidades"] / por_comuna["entidades"].sum()
    ).round(1)
    por_comuna = por_comuna.sort_values("entidades", ascending=False)
    por_comuna.to_csv(salida / "perfil_por_comuna.csv", index=False)

    bar_m = barrios.to_crs(config.CRS_METRICO)
    bar_m["km2"] = bar_m.geometry.area / 1e6
    por_barrio = (
        aptas.groupby("barrio_geo").size().rename("entidades").reset_index()
        .merge(bar_m[["nombre", "km2"]], left_on="barrio_geo", right_on="nombre")
        .drop(columns="nombre")
    )
    por_barrio["densidad_km2"] = (por_barrio["entidades"] / por_barrio["km2"]).round(1)
    por_barrio = por_barrio.sort_values("entidades", ascending=False)
    por_barrio.to_csv(salida / "perfil_por_barrio.csv", index=False)

    # Evidencia
    solo_f01 = int((ent["en_f01"] & ~ent["en_f02"]).sum())
    solo_f02 = int((~ent["en_f01"] & ent["en_f02"]).sum())
    ambas = int((ent["en_f01"] & ent["en_f02"]).sum())
    sin_fecha_2025 = int(ent["solo_evidencia_2025_sin_fecha"].fillna(False).sum())
    con_fecha_f02 = int(ent["evidencia_max_fecha"].notna().sum())
    flags = int(ent["flag_duplicado"].fillna("").ne("").sum())

    anio_max = pd.to_datetime(ent["evidencia_max_fecha"], errors="coerce").dt.year
    por_anio = anio_max.value_counts().sort_index()

    cats = ent["categoria_canonica"].value_counts().head(12)
    geocodificadas = int(ent["lat"].notna().sum())

    filas_fuente = log["reduccion_total"]["filas_fuente_gastronomicas"]

    w = []
    a = w.append
    a("# Perfil del universo gastronomico V1 (experimental)")
    a("")
    a(f"**Fecha de corrida:** {date.today().isoformat()} · **Universo:** F01 + F02 "
      "(decision 2026-07-08)")
    a("")
    a(config.NOTA_EXPERIMENTAL)
    a("")
    a("## 1. Volumen y deduplicacion")
    a("")
    a("| Indicador | Valor |")
    a("|---|---|")
    a(f"| Filas F01 gastronomicas | {log['f01_filas_gastronomicas']:,} |")
    a(f"| Filas F02 gastronomicas | {log['f02_filas_gastronomicas']:,} |")
    a(f"| Filas F02 excluidas por categoria (catering, mercado, feria) | "
      f"{sum(log['f02_filas_excluidas_por_categoria'].values()):,} |")
    a(f"| Filas fuente que entraron a resolucion | {filas_fuente:,} |")
    a(f"| **Entidades tras deduplicar** | **{len(ent):,}** |")
    a(f"| Colapso filas -> entidades | {log['reduccion_total']['porcentaje_colapso']} % |")
    a(f"| Entidades F01 tras dedup interna | {log['f01_entidades']:,} "
      f"(de {log['f01_filas_gastronomicas']:,} filas) |")
    a(f"| Ubicaciones F02 tras colapso por direccion | {log['f02_entidades_por_ubicacion']:,} "
      f"(de {log['f02_filas_tras_filtro_categorias']:,} filas; "
      f"{log['f02_filas_tras_filtro_categorias'] / log['f02_entidades_por_ubicacion']:.1f} filas/ubicacion) |")
    a(f"| Fusiones F01<-F02 | {log['f02_entidades_fusionadas_en_f01']:,} "
      f"(R5a {log['fusiones_R5a_misma_id_ubicacion']}, R5b {log['fusiones_R5b_misma_direccion']}, "
      f"R5c {log['fusiones_R5c_espacial_15m']}) |")
    a(f"| Posibles duplicados no fusionados (15-30 m, a revision) | {flags:,} |")
    a("")
    a("Lectura: el 'porcentaje de duplicados' relevante no es uno solo. Dentro de F02, "
      f"{log['f02_filas_tras_filtro_categorias']:,} filas colapsan a "
      f"{log['f02_entidades_por_ubicacion']:,} ubicaciones "
      f"({pct(log['f02_filas_tras_filtro_categorias'] - log['f02_entidades_por_ubicacion'], log['f02_filas_tras_filtro_categorias'])} "
      "de redundancia interna). Entre fuentes, solo "
      f"{log['f02_entidades_fusionadas_en_f01']:,} ubicaciones F02 "
      f"({pct(log['f02_entidades_fusionadas_en_f01'], log['f02_entidades_por_ubicacion'])}) "
      "matchean con una entidad F01: los universos casi no se superponen, como anticipo "
      "el perfilado de diseno.")
    a("")
    a("## 2. Evidencia por fuente")
    a("")
    a("| Evidencia | Entidades | % |")
    a("|---|---|---|")
    a(f"| Solo F01 (oferta registrada) | {solo_f01:,} | {pct(solo_f01, len(ent))} |")
    a(f"| Solo F02 (habilitaciones historicas) | {solo_f02:,} | {pct(solo_f02, len(ent))} |")
    a(f"| Ambas fuentes | {ambas:,} | {pct(ambas, len(ent))} |")
    a(f"| Con alguna fecha de habilitacion | {con_fecha_f02:,} | {pct(con_fecha_f02, len(ent))} |")
    a(f"| Solo recurso F02-2025 sin fecha | {sin_fecha_2025:,} | {pct(sin_fecha_2025, len(ent))} |")
    a("")
    a("Anio de la evidencia F02 mas reciente por entidad (cuando existe fecha):")
    a("")
    for anio, n in por_anio.items():
        a(f"- {int(anio)}: {n:,}")
    a("")
    a("**Advertencia de recencia:** la evidencia fechada se concentra en 2016-2018; casi no "
      "hay altas fechadas post-2019 en lo integrado. Las microzonas descriptas con este "
      "universo reflejan concentracion de oferta registrada/habilitada historica, no el "
      "paisaje gastronomico actual. Toda comunicacion debe declararlo.")
    a("")
    a("## 3. Calidad de geocodificacion y descartes")
    a("")
    a("| Indicador | Valor |")
    a("|---|---|")
    a(f"| Entidades geocodificadas | {geocodificadas:,} ({pct(geocodificadas, len(ent))}) |")
    a(f"| Aptas para clustering | {log['entidades_aptas_clustering']:,} "
      f"({pct(log['entidades_aptas_clustering'], len(ent))}) |")
    for motivo, n in log["descartes"].items():
        a(f"| Descartadas: {motivo} | {n:,} |")
    calidad = ent["calidad_geo"].value_counts(dropna=False)
    for cal, n in calidad.items():
        a(f"| Calidad geo `{cal}` | {n:,} ({pct(n, len(ent))}) |")
    a("")
    a("## 4. Categorias canonicas (top 12)")
    a("")
    for cat, n in cats.items():
        a(f"- {cat}: {n:,}")
    a("")
    a("## 5. Distribucion territorial (point-in-polygon)")
    a("")
    a("Por comuna (completo en `perfil_por_comuna.csv`):")
    a("")
    a("| Comuna | Entidades | % | km2 | Entidades/km2 |")
    a("|---|---|---|---|---|")
    for _, r in por_comuna.iterrows():
        a(f"| {r['comuna_geo']} | {int(r['entidades']):,} | {r['participacion']} % | "
          f"{r['km2']:.1f} | {r['densidad_km2']} |")
    a("")
    a("Top 15 barrios (completo en `perfil_por_barrio.csv`):")
    a("")
    a("| Barrio | Entidades | Entidades/km2 |")
    a("|---|---|---|")
    for _, r in por_barrio.head(15).iterrows():
        a(f"| {r['barrio_geo']} | {int(r['entidades']):,} | {r['densidad_km2']} |")
    a("")
    a("## 6. Limitaciones conocidas de este universo")
    a("")
    a("1. F02 no trae nombre comercial: una direccion con varios locales legitimos "
      "(galerias, patios) cuenta como UNA entidad; y la fusion F01<-F02 a <=15 m puede "
      "unir vecinos distintos de la misma categoria (riesgo acotado, documentado).")
    a("2. El recurso F02-2025 llego con filas duplicadas masivamente (28,8 filas por "
      "direccion) y sin fecha de habilitacion: aporta solo ~900 ubicaciones y su mapeo "
      "sigue pendiente de revision (ya senalado en el diseno).")
    a("3. La evidencia no acredita actividad actual (guardrail 5): 'entidad' = lugar con "
      "evidencia documental gastronomica en alguna fuente publica integrada.")
    a("4. El sesgo territorial de F01 (49 % en Comunas 1+14) se mitiga pero no desaparece: "
      "las comunas del sur dependen casi solo de F02.")
    a("")

    ruta = salida / "perfil_universo_v1.md"
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write("\n".join(w))
    print(f"Perfil escrito en {ruta}")
    print(f"Comunas: {len(por_comuna)} | Barrios: {len(por_barrio)}")
    print(f"Entidades: {len(ent):,} | aptas clustering: {log['entidades_aptas_clustering']:,}")


if __name__ == "__main__":
    main()
