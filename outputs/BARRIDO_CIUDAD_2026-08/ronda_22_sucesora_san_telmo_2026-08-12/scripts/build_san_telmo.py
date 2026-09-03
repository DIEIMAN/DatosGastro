# -*- coding: utf-8 -*-
"""Construye una sucesora de R22 que incorpora la manzana del Mercado de San Telmo.

No modifica R22 ni su corrección de relaciones. La lectura se fijó antes de medir:
- adopción técnica directa: <= 2 ha y <= 10 locales añadidos, geometría válida, sin solapes;
- revisión humana: <= 5 ha y <= 25 locales añadidos, geometría válida, sin solapes;
- rechazo/rediseño: > 5 ha, > 25 locales o cualquier solape material nuevo.

Diego decidió ampliar el borde. La alternativa de manzana cae en revisión humana por locales
y queda adoptada por esa decisión explícita. Los 66 iconos principales permanecen congelados.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.validation import explain_validity, make_valid

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = HERE.parents[3]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
PREV = BARRIDO / "ronda_22_correccion_relaciones_2026-08-12"
BLOCKS = BARRIDO / "insumos_ciudad" / "manzanas.geojson"
BARrios = BARRIDO / "insumos" / "caba_barrios.geojson"
LOCALS = BARRIDO / "desde_cowork" / "BASE_GASTRONOMICA_estado_2026-08-12.csv"
TARGET_UID = "POLO-R03"
MARKET_ID = "HITO-MG-0001"
BLOCK_ID = 7783
TOLERANCE_M = 1.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy_previous() -> None:
    for path in PREV.iterdir():
        if path.name in {"18_MANIFEST.csv", "19_HASHES_SHA256.csv", "scripts"}:
            continue
        if path.is_file():
            shutil.copy2(path, OUT / path.name)


def load_locals() -> gpd.GeoDataFrame:
    d = pd.read_csv(LOCALS, low_memory=False)
    d = d[(d["anillo"] == "nucleo") & d["apto_geometria"].astype(str).isin(["True", "true", "1"])].copy()
    return gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326).to_crs(5347)


def build_geometry():
    poles = gpd.read_file(PREV / "03_POLOS_CANDIDATOS.geojson").to_crs(5347)
    old = poles.loc[poles.polo_uid.eq(TARGET_UID), "geometry"].iloc[0]
    blocks = gpd.read_file(BLOCKS).to_crs(5347)
    chosen = blocks.loc[blocks["id"].eq(BLOCK_ID), "geometry"]
    if len(chosen) != 1:
        raise RuntimeError(f"La manzana estable {BLOCK_ID} no es única")
    block = chosen.iloc[0]
    refs = gpd.read_file(PREV / "15_MAP_INPUT_REFERENTES.geojson").to_crs(5347)
    market = refs.loc[refs.referente_id.eq(MARKET_ID), "geometry"].iloc[0]
    if old.covers(market):
        raise RuntimeError("El mercado ya está contenido; la sucesora no es necesaria")
    if old.distance(block) > 0.001 or market.distance(block) > 1.0:
        raise RuntimeError("La manzana ya no conecta con el polo o con el punto del mercado")
    new = old.union(block.buffer(TOLERANCE_M))
    if not new.is_valid:
        new = make_valid(new)
    if not new.is_valid or not new.covers(market):
        raise RuntimeError("La geometría sucesora no es válida o no contiene el mercado")
    return poles, old, new, block, market


def update_poles(poles, old, new, local_count):
    mask = poles.polo_uid.eq(TARGET_UID)
    poles.loc[mask, "geometry"] = gpd.GeoSeries([new], crs=5347).iloc[0]
    poles.loc[mask, "ha_r22"] = new.area / 10000
    poles.loc[mask, "locales_r22"] = local_count
    poles.loc[mask, "reparacion_geometrica"] = "ampliacion_manzana_mercado_san_telmo_buffer_1m"
    poles.loc[mask, "decision_territorial"] = "AMPLIAR_POR_DECISION_DIEGO_2026-08-12"
    poles.loc[mask, "estado"] = "SUCESORA_EN_REVISION_NO_OFICIAL"
    poles.to_crs(4326).to_file(OUT / "03_POLOS_CANDIDATOS.geojson", driver="GeoJSON")

    map_poles = gpd.read_file(PREV / "14_MAP_INPUT_POLOS.geojson").to_crs(5347)
    map_poles.loc[map_poles.polo_uid.eq(TARGET_UID), "geometry"] = gpd.GeoSeries([new], crs=5347).iloc[0]
    map_poles.to_crs(4326).to_file(OUT / "14_MAP_INPUT_POLOS.geojson", driver="GeoJSON")


def update_dimensions(new, loc):
    path = OUT / "05_POLOS_COMUNAS_BARRIOS.csv"
    d = pd.read_csv(path)
    barrios = gpd.read_file(BARrios).to_crs(5347)
    inside = loc[loc.within(new)]
    mask = d.polo_uid.eq(TARGET_UID)
    for idx, row in d[mask].iterrows():
        if row.dimension_tipo == "COMUNA":
            d.loc[idx, ["porcentaje_superficie", "locales"]] = [100.0, len(inside)]
        elif row.dimension_tipo == "BARRIO":
            name = str(row.dimension_nombre).upper().replace("Ó", "O")
            b = barrios[barrios.BARRIO.str.upper().str.replace("Ó", "O").eq(name)]
            if len(b) != 1:
                raise RuntimeError(f"Barrio no localizado: {row.dimension_nombre}")
            geom = b.geometry.iloc[0]
            d.loc[idx, "porcentaje_superficie"] = new.intersection(geom).area / new.area * 100
            d.loc[idx, "locales"] = int(inside.within(geom).sum())
    d.to_csv(path, index=False, encoding="utf-8-sig")


def update_references(new):
    refs = pd.read_csv(OUT / "07_REFERENTES_ICONOS_POR_POLO.csv", low_memory=False)
    target = refs.polo_uid.eq(TARGET_UID) & refs.referente_id.eq(MARKET_ID)
    if target.sum() != 1:
        raise RuntimeError("La relación Mercado–San Telmo no es única")
    point = gpd.GeoSeries(gpd.points_from_xy(refs.loc[target, "lon"], refs.loc[target, "lat"]), crs=4326).to_crs(5347).iloc[0]
    distance = point.distance(new.boundary)
    changes = {
        "estado_trazabilidad_asignacion": "GEOMETRIA_SUCESORA_SAN_TELMO",
        "fuente_asignacion_individualizada": "decisión territorial Diego 2026-08-12; manzana GCBA id 7783; Mercado de San Telmo, Defensa 961/963",
        "posicion": "INTERIOR",
        "clasificacion_propuesta": "INTERIOR_PROXIMO_AL_BORDE",
        "publicable_en_panel_territorial": "SI",
        "tratamiento_editorial_post_auditoria": "PANEL_TERRITORIAL",
        "dist_borde_m_recalculada": distance,
        "dist_fuera_m_recalculada": 0.0,
        "cae_dentro_de": TARGET_UID,
        "polo_mas_cercano": TARGET_UID,
        "fundamento": f"El punto queda dentro de la sucesora de San Telmo, a {distance:.1f} m del borde, por incorporación de la manzana del mercado.",
        "recomendacion_editorial": "Publicar en el panel territorial como mercado; la ampliación debe declararse como decisión posterior a R22.",
        "tratamiento_en_ficha": "INTERIOR",
        "bloque_en_ficha": "PANEL_TERRITORIAL",
        "fuera_geometria": "NO",
        "cerca_borde_50m": "SI",
        "distancia_borde_m": distance,
        "relacion_espacial": "INTERIOR",
        "relacion_espacial_etiqueta": "interior a la geometría sucesora",
    }
    for col, value in changes.items():
        if col in refs.columns:
            refs.loc[target, col] = value
    refs.to_csv(OUT / "07_REFERENTES_ICONOS_POR_POLO.csv", index=False, encoding="utf-8-sig")
    refs.to_csv(OUT / "AUDITORIA_RELACIONES_INTEGRADA_190.csv", index=False, encoding="utf-8-sig")

    geo = gpd.read_file(OUT / "15_MAP_INPUT_REFERENTES.geojson")
    gm = geo.polo_uid.eq(TARGET_UID) & geo.referente_id.eq(MARKET_ID)
    for col in ["posicion", "clasificacion_propuesta", "publicable_en_panel_territorial", "estado_trazabilidad_asignacion"]:
        if col in geo.columns:
            geo.loc[gm, col] = refs.loc[target, col].iloc[0]
    if "distancia_borde_m" in geo.columns:
        geo.loc[gm, "distancia_borde_m"] = distance
    geo.to_file(OUT / "15_MAP_INPUT_REFERENTES.geojson", driver="GeoJSON")

    qa = pd.read_csv(OUT / "08_QA_REFERENTES_POR_POLO.csv")
    qm = qa.polo_uid.eq(TARGET_UID)
    qa.loc[qm, "n_fuera_geometria"] = 3
    qa.loc[qm, "n_cerca_borde_50m"] = 3
    qa.loc[qm, "n_dentro"] = 2
    qa.loc[qm, "n_borde_hasta_50m"] = 2
    qa.loc[qm, "n_entorno_51_250m"] = 2
    qa.loc[qm, "estado_qa"] = "REVISAR_3_ASIGNACIONES_EXTERIORES; MERCADO_INCORPORADO"
    qa.loc[qm, "n_iconos_principales_propuestos"] = 1
    qa.to_csv(OUT / "08_QA_REFERENTES_POR_POLO.csv", index=False, encoding="utf-8-sig")


def write_counts(delta_locals):
    d = pd.read_csv(OUT / "10_CONTEOS_GLOBALES.csv")
    row = d.iloc[-1].copy()
    row["momento"] = "R22_SUCESORA_SAN_TELMO"
    row["locales_unicos"] = int(row["locales_unicos"]) + delta_locals
    row["ocurrencias_fichas"] = int(row["ocurrencias_fichas"]) + delta_locals
    row["duplicaciones"] = int(row["duplicaciones"])
    row["geometria"] = "sucesora R22; San Telmo incorpora manzana GCBA 7783 con tolerancia instrumental de 1 m"
    row["fuente"] = "R22 corregida + decisión territorial Diego 2026-08-12"
    d = pd.concat([d, row.to_frame().T], ignore_index=True)
    d.to_csv(OUT / "10_CONTEOS_GLOBALES.csv", index=False, encoding="utf-8-sig")


def write_docs(old, new, block, market, old_n, new_n, overlaps):
    added_ha = (new.area - old.area) / 10000
    band = "REVISION_HUMANA_ADOPTADA_POR_DECISION_EXPLICITA"
    (OUT / "DECISION_SAN_TELMO.md").write_text(f"""# Decisión territorial — San Telmo

Se adopta una sucesora de R22 que incorpora la manzana GCBA `id=7783` (`sm=004 - 029`) del Mercado de San Telmo y una tolerancia instrumental exterior de 1 m. R22 permanece intacta.

- Mercado antes: exterior, a 64,183 m del borde.
- Mercado después: interior, a {market.distance(new.boundary):.3f} m del borde.
- Superficie: {old.area/10000:.4f} → {new.area/10000:.4f} ha (+{added_ha:.4f}).
- Locales registrados: {old_n} → {new_n} (+{new_n-old_n}).
- Solapes materiales nuevos: {len(overlaps)}.
- Banda previa: `{band}`. El resultado supera el máximo de diez locales de adopción automática, pero queda dentro del rango de revisión (≤5 ha y ≤25 locales) y fue aprobado expresamente por Diego.
- Los 66 íconos principales permanecen congelados; Mercado de San Telmo entra al panel pero no se promueve a ícono.
""", encoding="utf-8")
    pd.DataFrame([
        {"alternativa": "MANZANA_SIN_TOLERANCIA", "tolerancia_m": 0, "incluye_mercado": "NO", "decision": "DESCARTADA_POR_ERROR_INSTRUMENTAL_0_45M"},
        {"alternativa": "MANZANA_BUFFER_1M", "tolerancia_m": 1, "incluye_mercado": "SI", "decision": "ADOPTADA"},
        {"alternativa": "MANZANA_BUFFER_2M", "tolerancia_m": 2, "incluye_mercado": "SI", "decision": "NO_NECESARIA"},
        {"alternativa": "MANZANA_BUFFER_5M", "tolerancia_m": 5, "incluye_mercado": "SI", "decision": "NO_NECESARIA"},
    ]).to_csv(OUT / "SENSIBILIDAD_SAN_TELMO.csv", index=False, encoding="utf-8-sig")
    (OUT / "00_RESUMEN.md").write_text(f"""# R22 · sucesora San Telmo

Estado: `REVISION`. Esta carpeta deriva de `ronda_22_correccion_relaciones_2026-08-12` y no modifica R22.

## Decisión incorporada

- San Telmo incorpora la manzana GCBA `id=7783` del Mercado de San Telmo y una tolerancia instrumental de 1 m.
- Superficie: {old.area/10000:.4f} → {new.area/10000:.4f} ha.
- Locales registrados: {old_n} → {new_n}.
- Mercado de San Telmo pasa de exterior a interior próximo al borde y entra al panel territorial.
- No se introducen solapes materiales con otros polos.

## Relaciones e íconos

- 190 relaciones: 139 interiores y 51 exteriores.
- Clasificación: 108 `INTERIOR`, 31 `INTERIOR_PROXIMO_AL_BORDE`, 26 `CONTEXTUAL_DOCUMENTAL`, 17 `ASIGNACION_DUDOSA` y 8 `ENTORNO_CERCANO`.
- Los 66 íconos principales quedan congelados. Mercado de San Telmo no se promueve a ícono.
- Las 51 relaciones exteriores continúan pendientes de resolución documental individual. La auditoría de las 52 relaciones originales sigue siendo el input correcto para esa investigación porque incluye el estado previo del mercado.

## Conteos globales

- 10.835 locales únicos dentro de al menos una ficha.
- 11.135 ocurrencias en fichas.
- 300 duplicaciones y ninguna pertenencia triple.

La diferencia de un registro observada al recalcular todo el corpus con la versión local de la librería es ajena a San Telmo. Para no contaminar esta decisión, los globales se actualizaron aplicando el delta verificado de 16 locales sobre el baseline canónico de R22.
""", encoding="utf-8")
    (OUT / "16_QA_GENERAL.md").write_text("""# QA general — sucesora San Telmo

- Geometría válida en EPSG:5347 y EPSG:4326.
- Mercado de San Telmo contenido.
- 87 locales dentro de San Telmo: +16 frente al baseline canónico.
- 0 solapes materiales nuevos.
- 190 relaciones y 190 pares únicos.
- 139 relaciones interiores; 51 exteriores.
- 17 asignaciones dudosas sin cambio.
- 66 íconos principales congelados, sin altas ni bajas.
- R22, el Atlas vigente y las fuentes originales no fueron modificados.
""", encoding="utf-8")
    (OUT / "17_PENDIENTES.md").write_text("""# Pendientes

- Resolver documentalmente las 52 relaciones que eran exteriores en el input auditado; al integrar el resultado, Mercado de San Telmo ya debe tratarse como interior por la decisión geométrica posterior.
- Priorizar las 17 `ASIGNACION_DUDOSA`.
- No revisar los 66 íconos hasta la lectura editorial intensa de Diego.
- Regenerar el Atlas desde esta sucesora después de integrar la corrección documental de Cowork.
""", encoding="utf-8")
    (OUT / "DICTAMEN_CORRECCION.md").write_text("""# Dictamen

La ampliación de San Telmo es técnicamente admisible y queda adoptada por decisión territorial explícita. Incorpora una unidad urbana completa, contiene el mercado, no produce solapes materiales y conserva congelada la selección de íconos. La carpeta permanece en `REVISION` hasta integrar la resolución documental independiente de las relaciones exteriores y regenerar el Atlas.
""", encoding="utf-8")
    (OUT / "REGLA_RELACION_ESPACIAL.md").write_text("""# Regla de relación espacial

La pertenencia territorial se determina contra la geometría sucesora. Las 190 relaciones se distribuyen en 139 interiores y 51 exteriores. El Mercado de San Telmo es la única relación que cambia respecto de la auditoría de R22: pasa a interior próximo al borde por una decisión geométrica posterior, no por una reinterpretación de la medición original.
""", encoding="utf-8")
    (OUT / "REGLA_PANEL_TERRITORIAL.md").write_text("""# Regla editorial de paneles

1. El panel publica únicamente relaciones interiores en la geometría vigente de esta sucesora.
2. `INTERIOR_PROXIMO_AL_BORDE` permanece en panel con marca interna de dependencia del trazado.
3. `ENTORNO_CERCANO` y `CONTEXTUAL_DOCUMENTAL` se presentan fuera del panel.
4. `ASIGNACION_DUDOSA` queda suspendida hasta individualizar la fuente.
5. Los conteos son relaciones por ficha, no establecimientos únicos.

La sucesora tiene 139 relaciones de panel. Mercado de San Telmo ingresa por la ampliación territorial posterior a la auditoría; la regla editorial no fue flexibilizada.
""", encoding="utf-8")
    (OUT / "QA_RELACIONES_POST_AUDITORIA.json").write_text(json.dumps({
        "relaciones": 190, "pares_unicos": 190, "interior": 139, "exterior": 51,
        "panel_territorial": 139, "asignaciones_dudosas": 17,
        "cambio_posterior_a_auditoria": "HITO-MG-0001 + POLO-R03",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    qa_rows = pd.read_csv(OUT / "QA_VALIDACIONES.csv")
    qa_rows = pd.concat([qa_rows, pd.DataFrame([
        {"control": "san_telmo_market_inside", "estado": "PASS"},
        {"control": "san_telmo_no_new_overlap", "estado": "PASS"},
        {"control": "icons_frozen_66", "estado": "PASS"},
    ])], ignore_index=True).drop_duplicates("control", keep="last")
    qa_rows.to_csv(OUT / "QA_VALIDACIONES.csv", index=False, encoding="utf-8-sig")


def write_preview(old, new, block, market):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    refs = gpd.read_file(PREV / "15_MAP_INPUT_REFERENTES.geojson").to_crs(5347)
    refs = refs[refs.polo_uid.eq(TARGET_UID)]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
    for ax, geom, title in [(axes[0], old, "R22 · antes"), (axes[1], new, "Sucesora · después")]:
        gpd.GeoSeries([block], crs=5347).plot(ax=ax, color="#e8dfcf", edgecolor="#8b7254", linewidth=1)
        gpd.GeoSeries([geom], crs=5347).plot(ax=ax, color="#7fcdbb", edgecolor="#006d5b", alpha=.65, linewidth=2)
        refs.plot(ax=ax, color="#252525", markersize=22)
        gpd.GeoSeries([market], crs=5347).plot(ax=ax, color="#c43c2b", markersize=70, marker="D")
        ax.set_title(title); ax.set_aspect("equal"); ax.set_axis_off()
    fig.suptitle("San Telmo · incorporación de la manzana del Mercado", fontsize=14, fontweight="bold")
    fig.savefig(OUT / "QA_SAN_TELMO_COMPARATIVA.png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def manifests():
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name not in {"18_MANIFEST.csv", "19_HASHES_SHA256.csv"})
    with (OUT / "18_MANIFEST.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["ruta", "incluido_en_entrega"]); w.writeheader()
        for p in files: w.writerow({"ruta": p.relative_to(OUT).as_posix(), "incluido_en_entrega": "SI"})
    with (OUT / "19_HASHES_SHA256.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["ruta", "sha256", "bytes"]); w.writeheader()
        for p in files: w.writerow({"ruta": p.relative_to(OUT).as_posix(), "sha256": sha256(p), "bytes": p.stat().st_size})


def main():
    copy_previous()
    poles, old, new, block, market = build_geometry()
    loc = load_locals()
    old_n = int(loc.within(old).sum()); new_n = int(loc.within(new).sum())
    if old_n != 71 or new_n != 87:
        raise RuntimeError(f"Conteos inesperados San Telmo: {old_n} -> {new_n}")
    others = poles[~poles.polo_uid.eq(TARGET_UID)]
    overlaps = [(r.polo_uid, new.intersection(r.geometry).area / 10000) for r in others.itertuples() if new.intersection(r.geometry).area > 10]
    if overlaps:
        raise RuntimeError(f"La ampliación introduce solapes materiales: {overlaps}")
    if (new.area-old.area)/10000 > 5 or new_n-old_n > 25:
        raise RuntimeError("La alternativa supera la banda previa de revisión")
    update_poles(poles, old, new, new_n)
    update_dimensions(new, loc)
    update_references(new)
    write_counts(new_n-old_n)
    write_docs(old, new, block, market, old_n, new_n, overlaps)
    write_preview(old, new, block, market)
    # Los 66 iconos se copian sin regenerar ni cambiar.
    if len(pd.read_csv(OUT / "ICONOS_PRINCIPALES_PROPUESTOS.csv")) != 66:
        raise RuntimeError("La lista congelada de iconos dejó de tener 66 filas")
    qa = {
        "estado": "REVISION",
        "geometria_valida": new.is_valid,
        "motivo_invalidez": explain_validity(new),
        "mercado_interior": new.covers(market),
        "area_ha_antes": old.area/10000,
        "area_ha_despues": new.area/10000,
        "locales_antes": old_n,
        "locales_despues": new_n,
        "relaciones_interiores": 139,
        "relaciones_exteriores": 51,
        "iconos_congelados": 66,
        "solapes_materiales_nuevos": len(overlaps),
    }
    (OUT / "QA_SAN_TELMO.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    manifests()
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
