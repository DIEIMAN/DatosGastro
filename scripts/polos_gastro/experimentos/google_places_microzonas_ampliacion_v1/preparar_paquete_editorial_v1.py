# -*- coding: utf-8 -*-
"""Paquete editorial de decision para microzonas completas v1.

EXPERIMENTAL / no oficial. No llama APIs, no modifica geometrias base y no
sobrescribe `completa_v1`; crea derivados en `paquete_editorial_v1`.
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[4]
BASE = (ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos"
        / "google_places_microzonas_ampliacion_v1" / "completa_v1")
OUT = BASE / "paquete_editorial_v1"
MAPAS = OUT / "mapas_revision"

POLIGONOS = BASE / "POLIGONOS_MICROZONAS_COMPLETA_V1.geojson"
PUNTOS = BASE / "MICROCLUSTERS_COMPLETA_V1.geojson"
UNIVERSO = BASE / "UNIVERSO_COMPLETO_SANITIZADO.csv"
REVISION = BASE / "revision_editorial_v1" / "tabla_revision_editorial_poligonos_completa_v1.csv"
HANDOFF_PREVIO = (ROOT / "docs" / "polos_gastro" / "historico" / "experimentos"
                  / "google_places_microzonas_ampliacion_v1"
                  / "HANDOFF_REVISION_POLIGONOS_COMPLETA_V1.md")

CRS_METRICO = "EPSG:5347"

MAP_ACCION = {
    "APROBAR": "PASA_A_BORRADOR",
    "APROBAR CON OBSERVACIONES": "PASA_A_BORRADOR_CON_NOTA",
    "REVISAR CORTE": "REDIBUJAR_CORTE",
    "REVISAR FUSION": "EVALUAR_FUSION",
    "REVISAR UNIVERSO": "VERIFICAR_UNIVERSO",
    "DESCARTAR": "EXCLUIR_POR_AHORA",
}

PROXIMA_ACCION = {
    "PASA_A_BORRADOR": "incluir_en_borrador_editorial_y_nominar_microzona",
    "PASA_A_BORRADOR_CON_NOTA": "incluir_en_borrador_con_observacion_metodologica",
    "REDIBUJAR_CORTE": "abrir_en_qgis_y_redibujar_limite_con_criterio_urbano",
    "EVALUAR_FUSION": "comparar_con_poligonos_contiguos_y_definir_si_unificar",
    "VERIFICAR_UNIVERSO": "validar_con_fuentes_f01_f02_osm_y_revision_humana",
    "EXCLUIR_POR_AHORA": "dejar_fuera_de_capa_editorial_hasta_nueva_evidencia",
}

COLORES = {
    "APROBAR": "#2f7d32",
    "APROBAR CON OBSERVACIONES": "#8bbf3d",
    "REVISAR CORTE": "#f39c12",
    "REVISAR FUSION": "#8e44ad",
    "REVISAR UNIVERSO": "#c0392b",
    "DESCARTAR": "#7f8c8d",
}

ZONAS_PROBLEMATICAS = {
    "corrientes_microcentro": ["MZ_AVENIDA_CORRIENTES", "MZ_MICROCENTRO_Y_CENTRO"],
    "belgrano": ["MZ_BELGRANO"],
    "caballito": ["MZ_CABALLITO"],
    "puerto_madero": ["MZ_PUERTO_MADERO"],
    "costanera_norte": ["MZ_COSTANERA_NORTE"],
    "caseros_barracas": ["MZ_AVENIDA_CASEROS_BARRACAS"],
}

MACROZONAS_DEBILES = {"MZ_COSTANERA_NORTE", "MZ_AVENIDA_CASEROS_BARRACAS"}


def prioridad(row: pd.Series) -> str:
    macro = row.get("macrozona") or row.get("macrozona_id")
    accion = row["accion_editorial"]
    problema = str(row["problema_detectado"])
    pct_places = float(row["porcentaje_places"])
    f01 = int(row.get("cantidad_f01_f02", 0))
    ronda = int(row.get("ronda_subdivision", 0))

    if accion in {"EXCLUIR_POR_AHORA", "VERIFICAR_UNIVERSO"}:
        return "ALTA"
    if macro in {"MZ_AVENIDA_CORRIENTES", "MZ_MICROCENTRO_Y_CENTRO"} and accion in {
        "REDIBUJAR_CORTE", "EVALUAR_FUSION"
    }:
        return "ALTA"
    if macro == "MZ_BELGRANO" and (ronda > 0 or accion == "REDIBUJAR_CORTE"):
        return "ALTA"
    if macro == "MZ_CABALLITO" and accion in {"REDIBUJAR_CORTE", "EVALUAR_FUSION"}:
        return "ALTA"
    if macro in MACROZONAS_DEBILES and accion != "PASA_A_BORRADOR":
        return "ALTA"
    if pct_places >= 75 and f01 < 8:
        return "ALTA"
    if "poligono_tipo_tile" in problema or "corte_por_subdivision_kmeans" in problema:
        return "MEDIA"
    if accion in {"REDIBUJAR_CORTE", "EVALUAR_FUSION"}:
        return "MEDIA"
    if accion == "PASA_A_BORRADOR_CON_NOTA":
        return "MEDIA"
    return "BAJA"


def motivo(row: pd.Series) -> str:
    parts = []
    if row["problema_detectado"] and row["problema_detectado"] != "sin_problema_relevante":
        parts.append(str(row["problema_detectado"]))
    macro = row.get("macrozona") or row.get("macrozona_id")
    if macro in MACROZONAS_DEBILES:
        parts.append("macrozona_debil_para_decision_institucional")
    if macro in {"MZ_AVENIDA_CORRIENTES", "MZ_MICROCENTRO_Y_CENTRO"}:
        parts.append("controlar_continuidad_corrientes_microcentro")
    if macro == "MZ_CABALLITO":
        parts.append("controlar_sobreparticion_de_corredores")
    if macro == "MZ_BELGRANO":
        parts.append("controlar_cortes_barrio_chino_cabildo_juramento")
    return "; ".join(dict.fromkeys(parts)) or "sin_alerta_especifica"


def cargar() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, pd.DataFrame, pd.DataFrame]:
    pol = gpd.read_file(POLIGONOS).to_crs(CRS_METRICO)
    pts = gpd.read_file(PUNTOS).to_crs(CRS_METRICO)
    universo = pd.read_csv(UNIVERSO)
    rev = pd.read_csv(REVISION)
    if len(pol) != len(rev):
        raise SystemExit(f"Conteo incompatible: poligonos={len(pol)} revision={len(rev)}")
    return pol, pts, universo, rev


def preparar_capas(pol: gpd.GeoDataFrame, rev: pd.DataFrame) -> gpd.GeoDataFrame:
    keep = [
        "microzona_id", "accion_recomendada", "confianza_editorial",
        "problema_detectado", "observaciones", "cantidad_entidades",
        "cantidad_f01_f02", "cantidad_places", "porcentaje_places",
        "superficie_ha", "densidad_entidades_ha", "ronda_subdivision",
    ]
    attrs = rev[keep].copy()
    g = pol.merge(attrs, left_on="cluster_id", right_on="microzona_id", how="left")
    if g["accion_recomendada"].isna().any():
        raise SystemExit("Hay poligonos sin clasificacion editorial.")
    g["categoria_revision"] = g["accion_recomendada"]
    g["accion_editorial"] = g["categoria_revision"].map(MAP_ACCION)
    g["prioridad_revision"] = g.apply(prioridad, axis=1)
    g["motivo"] = g.apply(motivo, axis=1)
    g["proxima_accion"] = g["accion_editorial"].map(PROXIMA_ACCION)
    g["nota_paquete"] = (
        "EXPERIMENTAL / no oficial. Capa de decision editorial; no usar como limite final."
    )
    return g


def exportar_capas(g: gpd.GeoDataFrame) -> dict[str, int]:
    OUT.mkdir(parents=True, exist_ok=True)
    capas = {
        "poligonos_aprobables_v1.geojson": ["APROBAR", "APROBAR CON OBSERVACIONES"],
        "poligonos_revisar_corte_v1.geojson": ["REVISAR CORTE"],
        "poligonos_revisar_fusion_v1.geojson": ["REVISAR FUSION"],
        "poligonos_revisar_universo_v1.geojson": ["REVISAR UNIVERSO"],
        "poligonos_descartar_v1.geojson": ["DESCARTAR"],
    }
    counts = {}
    g.to_crs("EPSG:4326").to_file(OUT / "poligonos_todos_con_revision_v1.geojson",
                                  driver="GeoJSON")
    counts["poligonos_todos_con_revision_v1.geojson"] = int(len(g))
    for fname, cats in capas.items():
        sub = g[g["categoria_revision"].isin(cats)].copy()
        sub.to_crs("EPSG:4326").to_file(OUT / fname, driver="GeoJSON")
        counts[fname] = int(len(sub))
    return counts


def tabla_decision(g: gpd.GeoDataFrame) -> pd.DataFrame:
    cols = [
        "macrozona_id", "cluster_id", "categoria_revision", "accion_editorial",
        "prioridad_revision", "motivo", "cantidad_entidades", "porcentaje_places",
        "superficie_ha", "densidad_entidades_ha", "confianza_editorial",
        "problema_detectado", "proxima_accion",
    ]
    out = g[cols].copy()
    out = out.rename(columns={
        "macrozona_id": "macrozona",
        "cluster_id": "microzona_id",
        "cantidad_entidades": "entidades_total",
    })
    out = out.sort_values(["prioridad_revision", "macrozona", "microzona_id"],
                          key=lambda s: s.map({"ALTA": 0, "MEDIA": 1, "BAJA": 2}).fillna(s)
                          if s.name == "prioridad_revision" else s)
    out.to_csv(OUT / "tabla_decision_editorial_microzonas_v1.csv", index=False,
               encoding="utf-8")
    return out


def plot_mapa(g: gpd.GeoDataFrame, pts: gpd.GeoDataFrame, path: Path, title: str,
              mz_ids: list[str] | None = None) -> None:
    MAPAS.mkdir(parents=True, exist_ok=True)
    sub = g[g["macrozona_id"].isin(mz_ids)].copy() if mz_ids else g.copy()
    sub_pts = pts[pts["macrozona_id"].isin(mz_ids)].copy() if mz_ids else pts.copy()
    fig, ax = plt.subplots(figsize=(12, 10))
    if len(sub_pts):
        sub_pts.plot(ax=ax, color="#d7d7d7", markersize=2, alpha=0.35)
    for cat, color in COLORES.items():
        layer = sub[sub["categoria_revision"] == cat]
        if len(layer):
            layer.plot(ax=ax, color=color, edgecolor="#222222", linewidth=0.5,
                       alpha=0.45)
    sub.boundary.plot(ax=ax, color="#222222", linewidth=0.4, alpha=0.65)
    handles = [Patch(facecolor=color, edgecolor="#222222", label=cat, alpha=0.55)
               for cat, color in COLORES.items() if (sub["categoria_revision"] == cat).any()]
    ax.legend(handles=handles, loc="upper right", fontsize=8, framealpha=0.92)
    ax.set_title(title, fontsize=13)
    ax.set_axis_off()
    ax.set_aspect("equal")
    fig.text(0.5, 0.015,
             "EXPERIMENTAL / no oficial. Capa de decision editorial; no usar como limite final.",
             ha="center", fontsize=8, color="#555555")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def generar_mapas(g: gpd.GeoDataFrame, pts: gpd.GeoDataFrame) -> list[str]:
    paths = []
    general = MAPAS / "mapa_general_categorias_editoriales_v1.png"
    plot_mapa(g, pts, general, "Paquete editorial v1 - categorias de revision")
    paths.append(str(general))
    for nombre, mz_ids in ZONAS_PROBLEMATICAS.items():
        path = MAPAS / f"mapa_revision_{nombre}_v1.png"
        plot_mapa(g, pts, path, f"Revision editorial v1 - {nombre}", mz_ids)
        paths.append(str(path))
    return paths


def resumen_md(tabla: pd.DataFrame, g: gpd.GeoDataFrame, layer_counts: dict[str, int],
               mapas: list[str]) -> str:
    by_accion = tabla["accion_editorial"].value_counts().to_dict()
    by_prioridad = tabla["prioridad_revision"].value_counts().to_dict()
    borrador = by_accion.get("PASA_A_BORRADOR", 0) + by_accion.get("PASA_A_BORRADOR_CON_NOTA", 0)
    redibujo = by_accion.get("REDIBUJAR_CORTE", 0) + by_accion.get("EVALUAR_FUSION", 0)
    debiles = tabla[tabla["macrozona"].isin(MACROZONAS_DEBILES)]["macrozona"].value_counts().to_dict()
    solidas = (tabla[tabla["accion_editorial"].isin(["PASA_A_BORRADOR", "PASA_A_BORRADOR_CON_NOTA"])]
               .groupby("macrozona").size().sort_values(ascending=False).head(6).to_dict())
    lines = [
        "# Resumen paquete editorial v1",
        "",
        "Estado: EXPERIMENTAL / no oficial. Este paquete organiza decision editorial; no redibuja geometrias.",
        "",
        "## Sintesis",
        "",
        f"- Poligonos procesados: {len(tabla)}.",
        f"- Pasan a borrador editorial: {borrador} ({by_accion.get('PASA_A_BORRADOR', 0)} directos y {by_accion.get('PASA_A_BORRADOR_CON_NOTA', 0)} con nota).",
        f"- Requieren redibujo o evaluacion de fusion: {redibujo}.",
        f"- Requieren verificar universo: {by_accion.get('VERIFICAR_UNIVERSO', 0)}.",
        f"- Quedan excluidos por ahora: {by_accion.get('EXCLUIR_POR_AHORA', 0)}.",
        "",
        "## Macrozonas mas solidas",
        "",
    ]
    for macro, n in solidas.items():
        lines.append(f"- {macro}: {int(n)} poligonos pasan a borrador o borrador con nota.")
    lines += [
        "",
        "## Macrozonas debiles o con mayor cuidado",
        "",
    ]
    for macro, n in debiles.items():
        lines.append(f"- {macro}: {int(n)} poligonos en macrozona debil o emergente.")
    lines += [
        "- Corrientes/Microcentro, Belgrano y Caballito requieren decision humana por cortes internos y continuidad territorial.",
        "- Costanera Norte y Caseros/Barracas no deberian consolidarse como limites institucionales sin revision externa a Places.",
        "",
        "## Que no conviene volver a consultar con API",
        "",
        "- No conviene reconsultar macrozonas completas.",
        "- No conviene resolver la saturacion de Recoleta, Villa Crespo o Caballito con mas API antes de definir cortes urbanos.",
        "- La siguiente mejora debe ser redibujo editorial, no mas puntos.",
        "",
        "## Prioridad de revision",
        "",
    ]
    for k in ["ALTA", "MEDIA", "BAJA"]:
        lines.append(f"- {k}: {by_prioridad.get(k, 0)} poligonos.")
    lines += [
        "",
        "## Capas generadas",
        "",
    ]
    for name, n in layer_counts.items():
        lines.append(f"- `{name}`: {n} poligonos.")
    lines += [
        "",
        "## Mapas de revision",
        "",
    ]
    for path in mapas:
        lines.append(f"- `{Path(path).name}`")
    return "\n".join(lines) + "\n"


def handoff_md(tabla: pd.DataFrame, mapas: list[str]) -> str:
    alta = tabla[tabla["prioridad_revision"] == "ALTA"]
    lines = [
        "# Handoff paquete editorial v1",
        "",
        "## Archivos para revision manual",
        "",
        "- `tabla_decision_editorial_microzonas_v1.csv`: tablero principal de decision.",
        "- `poligonos_todos_con_revision_v1.geojson`: abrir en QGIS para ver todos los poligonos con atributos editoriales.",
        "- `poligonos_aprobables_v1.geojson`: candidatos a borrador, no version final.",
        "- `poligonos_revisar_corte_v1.geojson`: insumo prioritario para redibujo manual.",
        "- `poligonos_revisar_fusion_v1.geojson`: revisar continuidad y union con poligonos vecinos.",
        "- `poligonos_revisar_universo_v1.geojson`: validar con fuentes externas a Places y lectura humana.",
        "- `poligonos_descartar_v1.geojson`: mantener fuera de la capa editorial por ahora.",
        "",
        "## Capas a abrir en QGIS",
        "",
        "1. `poligonos_todos_con_revision_v1.geojson`",
        "2. `poligonos_revisar_corte_v1.geojson`",
        "3. `poligonos_revisar_fusion_v1.geojson`",
        "4. `poligonos_aprobables_v1.geojson`",
        "",
        "Simbolizar por `accion_editorial` o `prioridad_revision`.",
        "",
        "## Capa que NO debe usarse como final",
        "",
        "Ninguna capa de este paquete debe usarse como limite institucional final. Son capas de decision y revision.",
        "",
        "## Prioridad alta",
        "",
    ]
    for _, r in alta.head(25).iterrows():
        lines.append(f"- {r['microzona_id']} ({r['macrozona']}): {r['accion_editorial']} - {r['motivo']}")
    lines += [
        "",
        "## Pasos faltantes para version institucional",
        "",
        "- Revision humana en QGIS de cortes de prioridad alta.",
        "- Redibujo manual de limites segun continuidad urbana reconocible.",
        "- Nominacion editorial de microzonas defendibles.",
        "- Validacion con fuentes oficiales/administrativas y criterio de gestion.",
        "- Anexo metodologico que declare que Google Places es senal auxiliar no oficial.",
        "- Nueva capa versionada, separada de este paquete experimental.",
        "",
        "## Mapas generados",
        "",
    ]
    for path in mapas:
        lines.append(f"- `{Path(path).name}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    MAPAS.mkdir(parents=True, exist_ok=True)
    pol, pts, universo, rev = cargar()
    g = preparar_capas(pol, rev)
    layer_counts = exportar_capas(g)
    tabla = tabla_decision(g)
    mapas = generar_mapas(g, pts)

    resumen = resumen_md(tabla, g, layer_counts, mapas)
    handoff = handoff_md(tabla, mapas)
    (OUT / "RESUMEN_PAQUETE_EDITORIAL_V1.md").write_text(resumen, encoding="utf-8")
    (OUT / "HANDOFF_PAQUETE_EDITORIAL_V1.md").write_text(handoff, encoding="utf-8")
    metadata = {
        "estado": "EXPERIMENTAL / no oficial",
        "poligonos_procesados": int(len(tabla)),
        "conteo_por_capa": layer_counts,
        "conteo_accion_editorial": tabla["accion_editorial"].value_counts().to_dict(),
        "conteo_prioridad": tabla["prioridad_revision"].value_counts().to_dict(),
        "universo_rows_leido": int(len(universo)),
        "mapas": [str(Path(p).relative_to(OUT)) for p in mapas],
        "nota": "No se redibujaron geometrias; solo se incorporaron atributos editoriales.",
    }
    (OUT / "metadata_paquete_editorial_v1.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
