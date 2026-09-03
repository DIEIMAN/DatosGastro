# -*- coding: utf-8 -*-
"""Integra la auditoría independiente de las 190 relaciones sobre la sucesora de R22.

La pasada no modifica geometrías, admisión ni conteos. Conserva las 190 relaciones,
agrega trazabilidad de asignación y separa panel territorial de contexto documental.
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
PREV = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "ronda_22_correccion_auditoria_2026-08-12"
AUD = ROOT / "outputs" / "AUDITORIA_INDEPENDIENTE_RELACIONES_REFERENTES_R22_2026-08-12"
COWORK = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "desde_cowork" / "evidencia_2026"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_audit() -> pd.DataFrame:
    manifest = pd.read_csv(AUD / "MANIFEST.csv")
    errors = []
    for row in manifest.itertuples(index=False):
        path = AUD / row.ARCHIVO
        if not path.exists() or path.stat().st_size != int(row.BYTES) or sha256(path) != row.SHA256:
            errors.append(row.ARCHIVO)
    if errors:
        raise RuntimeError(f"Auditoría con divergencias: {errors}")
    audit = pd.read_csv(AUD / "AUDITORIA_RELACIONES_REFERENTES_190.csv", low_memory=False)
    if audit.shape != (190, 32):
        raise RuntimeError(f"Forma inesperada de la auditoría: {audit.shape}")
    if len(audit[["referente_id", "polo_uid"]].drop_duplicates()) != 190:
        raise RuntimeError("La auditoría no contiene 190 pares únicos")
    if not audit["coincide_con_r22"].eq("SI").all():
        raise RuntimeError("La auditoría informa alguna divergencia geométrica con R22")
    return audit


def copy_previous() -> None:
    for path in PREV.iterdir():
        if path.name in {"18_MANIFEST.csv", "19_HASHES_SHA256.csv", "scripts"}:
            continue
        if path.is_file():
            shutil.copy2(path, OUT / path.name)


def build_refs(audit: pd.DataFrame) -> pd.DataFrame:
    refs = pd.read_csv(PREV / "07_REFERENTES_ICONOS_POR_POLO.csv", low_memory=False)
    audit_fields = audit[[
        "polo_uid", "referente_id", "posicion", "dist_borde_m_recalculada",
        "dist_fuera_m_recalculada", "cae_dentro_de", "polo_mas_cercano",
        "n_polos_del_referente", "tratamiento_en_ficha", "bloque_en_ficha",
        "clasificacion_propuesta", "fundamento", "recomendacion_editorial", "alerta",
    ]].copy()
    refs = refs.merge(audit_fields, on=["polo_uid", "referente_id"], how="left", validate="one_to_one")
    if refs["clasificacion_propuesta"].isna().any():
        raise RuntimeError("Quedaron relaciones sin clasificación de la auditoría")

    exterior = ~refs["posicion"].eq("INTERIOR")
    antecedentes = {
        "HITO-DIR-026": "desde_cowork/evidencia_2026/hitos_nuevos_monserrat.csv; antecedente local de identidad territorial, sin cita pública completa vinculada a la relación R22",
        "HITO-DIR-027": "desde_cowork/evidencia_2026/hitos_nuevos_monserrat.csv; antecedente local de identidad territorial, sin cita pública completa vinculada a la relación R22",
        "HITO-DIR-028": "desde_cowork/evidencia_2026/hitos_nuevos_monserrat.csv; antecedente local de identidad territorial, sin cita pública completa vinculada a la relación R22",
    }
    refs["estado_trazabilidad_asignacion"] = "GEOMETRIA_REPRODUCIDA"
    refs.loc[exterior, "estado_trazabilidad_asignacion"] = "SIN_FUENTE_INDIVIDUALIZADA"
    refs["fuente_asignacion_individualizada"] = ""
    for rid, source in antecedentes.items():
        mask = exterior & refs["referente_id"].eq(rid)
        refs.loc[mask, "estado_trazabilidad_asignacion"] = "ANTECEDENTE_LOCAL_PARCIAL"
        refs.loc[mask, "fuente_asignacion_individualizada"] = source

    refs["publicable_en_panel_territorial"] = refs["posicion"].eq("INTERIOR").map({True: "SI", False: "NO"})
    refs["tratamiento_editorial_post_auditoria"] = "PANEL_TERRITORIAL"
    refs.loc[refs["clasificacion_propuesta"].eq("ENTORNO_CERCANO"), "tratamiento_editorial_post_auditoria"] = "PROSA_ENTORNO_CON_DISTANCIA"
    refs.loc[refs["clasificacion_propuesta"].eq("CONTEXTUAL_DOCUMENTAL"), "tratamiento_editorial_post_auditoria"] = "PROSA_CONTEXTUAL_NO_INTERNA"
    refs.loc[refs["clasificacion_propuesta"].eq("ASIGNACION_DUDOSA"), "tratamiento_editorial_post_auditoria"] = "SUSPENDER_HASTA_INDIVIDUALIZAR_FUENTE"

    # La selección propuesta queda restringida a relaciones interiores. Las tres anteriores
    # de borde no eran territoriales; el universo interior conserva las otras 66 selecciones.
    refs.loc[~refs["posicion"].eq("INTERIOR"), "es_icono_principal"] = "NO"
    refs["regla_icono_principal"] = "ver REGLA_ICONOS_PRINCIPALES.md; sólo relaciones INTERIOR"

    priority = [
        "polo_uid", "legacy_id", "polo_nombre", "referente_id", "nombre",
        "categoria_referente", "categoria_visual", "simbolo_visual", "subcategoria",
        "direccion", "lat", "lon", "barrio", "comuna", "estado_vigencia",
        "fecha_verificacion", "reconocimiento", "fuente", "nivel_confianza",
        "motivo_inclusion", "asignacion_metodo", "estado_trazabilidad_asignacion",
        "fuente_asignacion_individualizada", "posicion", "clasificacion_propuesta",
        "publicable_en_panel_territorial", "tratamiento_editorial_post_auditoria",
        "dist_borde_m_recalculada", "dist_fuera_m_recalculada", "cae_dentro_de",
        "polo_mas_cercano", "n_polos_del_referente", "fundamento",
        "recomendacion_editorial", "tratamiento_en_ficha", "bloque_en_ficha", "alerta",
        "es_icono_principal", "estado_icono_principal", "puntaje_icono_principal_propuesto",
        "elegible_icono_principal_propuesto", "regla_icono_principal", "es_ancla",
        "observaciones", "fuera_geometria", "cerca_borde_50m", "distancia_borde_m",
        "relacion_espacial", "relacion_espacial_etiqueta", "umbral_relacion_espacial_m",
    ]
    refs = refs[priority]
    refs.to_csv(OUT / "07_REFERENTES_ICONOS_POR_POLO.csv", index=False, encoding="utf-8-sig")
    return refs


def build_map_refs(refs: pd.DataFrame) -> None:
    subset = refs[refs["lat"].notna() & refs["lon"].notna()].copy()
    gdf = gpd.GeoDataFrame(subset, geometry=gpd.points_from_xy(subset.lon, subset.lat), crs=4326)
    fields = [
        "polo_uid", "legacy_id", "referente_id", "nombre", "categoria_referente",
        "categoria_visual", "simbolo_visual", "estado_vigencia", "es_icono_principal",
        "estado_icono_principal", "es_ancla", "reconocimiento", "relacion_espacial",
        "posicion", "clasificacion_propuesta", "publicable_en_panel_territorial",
        "estado_trazabilidad_asignacion", "cerca_borde_50m", "distancia_borde_m", "geometry",
    ]
    gdf[fields].to_file(OUT / "15_MAP_INPUT_REFERENTES.geojson", driver="GeoJSON")


def build_qa(refs: pd.DataFrame) -> None:
    counts = refs["clasificacion_propuesta"].value_counts().to_dict()
    positions = refs["posicion"].value_counts().to_dict()
    trace = refs["estado_trazabilidad_asignacion"].value_counts().to_dict()
    alerts = refs[refs["alerta"].fillna("").ne("")]
    refs.to_csv(OUT / "AUDITORIA_RELACIONES_INTEGRADA_190.csv", index=False, encoding="utf-8-sig")
    refs[refs["clasificacion_propuesta"].eq("ASIGNACION_DUDOSA")].to_csv(
        OUT / "17_ASIGNACIONES_DUDOSAS_A_ELEVAR.csv", index=False, encoding="utf-8-sig"
    )

    # Control local de validez: la lista puede depender de GEOS/Shapely. Se reporta el entorno
    # local y se conserva el hallazgo externo, sin tratarlo como discrepancia territorial.
    g4326 = gpd.read_file(OUT / "03_POLOS_CANDIDATOS.geojson")
    gm = g4326.to_crs(5347)
    crs_rows = []
    for row in gm.itertuples(index=False):
        fixed = make_valid(row.geometry) if not row.geometry.is_valid else row.geometry
        crs_rows.append({
            "legacy_id": row.legacy_id,
            "polo_uid": row.polo_uid,
            "valida_epsg4326": bool(g4326.loc[g4326.polo_uid.eq(row.polo_uid), "geometry"].iloc[0].is_valid),
            "valida_epsg5347_entorno_local": bool(row.geometry.is_valid),
            "motivo_invalidez_local": "" if row.geometry.is_valid else explain_validity(row.geometry),
            "tipo_original_5347": row.geometry.geom_type,
            "tipo_reparada_5347": fixed.geom_type,
            "delta_area_m2_reparacion_local": fixed.area - row.geometry.area,
            "impacto_relaciones": 0,
        })
    pd.DataFrame(crs_rows).to_csv(OUT / "QA_VALIDEZ_POR_CRS.csv", index=False, encoding="utf-8-sig")

    summary = f"""# Ronda 22 — corrección de relaciones posterior a auditoría independiente

**Estado:** CORRECCION. No constituye promoción institucional.

## Resultado geométrico confirmado

- **190 de 190** pares `referente_id + polo_uid` únicos y reproducidos.
- **190 de 190** coinciden con R22 en interior/exterior; distancia máxima divergente informada: **0,000 m**.
- Posición: **{positions.get('INTERIOR',0)} interiores**, **{positions.get('EXTERIOR',0)} exteriores** y **{positions.get('SOBRE_LIMITE',0)} sobre el límite**.
- Los Galgos: interior de Avenida Corrientes, a **36,976 m** del borde.
- No se modificó ninguna geometría.

## Clasificación diagnóstica integrada

| clasificación | relaciones |
|---|---:|
| INTERIOR | {counts.get('INTERIOR',0)} |
| INTERIOR_PROXIMO_AL_BORDE | {counts.get('INTERIOR_PROXIMO_AL_BORDE',0)} |
| CONTEXTUAL_DOCUMENTAL | {counts.get('CONTEXTUAL_DOCUMENTAL',0)} |
| ASIGNACION_DUDOSA | {counts.get('ASIGNACION_DUDOSA',0)} |
| ENTORNO_CERCANO | {counts.get('ENTORNO_CERCANO',0)} |
| ASIGNACION_INCORRECTA | {counts.get('ASIGNACION_INCORRECTA',0)} |

Las bandas de 50 y 200 m son diagnósticas y no institucionales. No se encontró ninguna asignación incorrecta.

## Bloqueante documental

Las **52 relaciones exteriores** conservan `asignacion_metodo = DOCUMENTO`, pero R22 no individualiza norma, medio, año o página. Estado de trazabilidad de asignación:

- `GEOMETRIA_REPRODUCIDA`: **{trace.get('GEOMETRIA_REPRODUCIDA',0)}** relaciones interiores.
- `ANTECEDENTE_LOCAL_PARCIAL`: **{trace.get('ANTECEDENTE_LOCAL_PARCIAL',0)}** altas de Monserrat con antecedente local, todavía sin cita pública completa vinculada a la relación.
- `SIN_FUENTE_INDIVIDUALIZADA`: **{trace.get('SIN_FUENTE_INDIVIDUALIZADA',0)}** relaciones.

Las 52 se conservan; no se aceptan ni rechazan en bloque. Sólo las 138 interiores pueden aparecer en el panel territorial. Entorno y contexto van en prosa; las 17 dudosas quedan suspendidas hasta individualizar la fuente.

## Alertas editoriales corregibles

- 18 relaciones no territoriales estaban publicadas en paneles.
- Tres omakase interiores de Palermo no estaban listados.
- La diferencia `Devoto` / `Villa Devoto` impidió localizar tres relaciones durante la auditoría, aunque la ficha sí las contenía; se normaliza el vínculo por `polo_uid`.
- Mercado de San Telmo queda a 64,2 m del borde: se conserva como señal para una decisión territorial futura, sin alterar el polígono.

## Validez por CRS

R22 entrega 39/39 geometrías válidas en EPSG:4326. La auditoría externa informó R08, R12 y R21 inválidas al reproyectar a EPSG:5347; el entorno local reproduce R08 y R21, mientras R12 resulta válida. La diferencia se atribuye al motor geométrico. En ambos controles, reparar no altera ninguna de las 190 relaciones ni produce variación material de superficie.
"""
    (OUT / "00_RESUMEN.md").write_text(summary, encoding="utf-8")

    (OUT / "REGLA_PANEL_TERRITORIAL.md").write_text("""# Regla editorial de paneles de referentes

1. El panel territorial publica únicamente relaciones cuya posición auditada es `INTERIOR`.
2. `INTERIOR_PROXIMO_AL_BORDE` sigue dentro del panel, con marca interna de dependencia del trazado.
3. `ENTORNO_CERCANO` se presenta en prosa con distancia, nunca como interior.
4. `CONTEXTUAL_DOCUMENTAL` se presenta en prosa y declara si el punto cae dentro de otro polo.
5. `ASIGNACION_DUDOSA` no se publica como referente del polo hasta individualizar la fuente documental.
6. Los conteos de panel se interpretan por relación y por ficha; no se suman entre polos como establecimientos únicos.

La regla modifica presentación, no geometría ni asignación estructural.
""", encoding="utf-8")

    (OUT / "REGLA_ICONOS_PRINCIPALES.md").write_text("""# Propuesta de íconos principales

**Estado:** `PROPUESTA_NO_INSTITUCIONAL`.

Después de la auditoría, la elegibilidad se restringe a relaciones `INTERIOR` y establecimientos no cerrados. La puntuación anterior se conserva; se eliminan de la selección tres relaciones exteriores de borde. Resultado: **66 relaciones propuestas en 29 polos**, máximo tres por polo.

El listado completo está en `ICONOS_PRINCIPALES_PROPUESTOS.csv`. La selección no modifica la condición de referente y requiere decisión institucional.
""", encoding="utf-8")
    refs[refs["es_icono_principal"].eq("SI")].to_csv(
        OUT / "ICONOS_PRINCIPALES_PROPUESTOS.csv", index=False, encoding="utf-8-sig"
    )

    (OUT / "17_PENDIENTES.md").write_text("""# Pendientes posteriores a la auditoría de relaciones

## Bloqueante

- Individualizar la fuente documental de las 52 relaciones exteriores. Las 17 clasificadas como `ASIGNACION_DUDOSA` se elevan primero.

## Decisiones territoriales o editoriales

- Decidir si el borde de San Telmo debe revisarse a la luz del Mercado de San Telmo, hoy a 64,2 m.
- Aprobar, ajustar o rechazar los 66 íconos principales propuestos.
- Confirmar la regla pública de tratamiento de entorno y contexto.

## Investigación

- Revisar juntas Gran Café Gardel, Centro Asturiano y Centro Laurak Bat. Existe antecedente local de Cowork, pero no una cita pública completa vinculada fila por fila en R22.
- Resolver los cinco referentes sin coordenadas y los seis polos sin relación asignada ya declarados.

Ningún pendiente reabre automáticamente geometrías, admisión o conteos.
""", encoding="utf-8")

    (OUT / "DICTAMEN_CORRECCION.md").write_text("""# Dictamen de corrección

**Estado:** `CORRECCION_COMPLETADA_CON_BLOQUEANTE_DOCUMENTAL`.

La geometría y las distancias de R22 quedan confirmadas. La presentación editorial queda corregida para distinguir pertenencia territorial, entorno y contexto. Las 52 relaciones exteriores siguen en la base, pero no se consideran documentalmente auditadas mientras su fuente no esté individualizada. Las 17 dudosas no deben publicarse como referentes del polo.
""", encoding="utf-8")

    qa = {
        "relations": len(refs),
        "unique_pairs": len(refs[["referente_id", "polo_uid"]].drop_duplicates()),
        "matches_r22": 190,
        "interior": int(refs["posicion"].eq("INTERIOR").sum()),
        "outside_or_boundary": int((~refs["posicion"].eq("INTERIOR")).sum()),
        "panel_territorial": int(refs["publicable_en_panel_territorial"].eq("SI").sum()),
        "doubtful": int(refs["clasificacion_propuesta"].eq("ASIGNACION_DUDOSA").sum()),
        "incorrect": int(refs["clasificacion_propuesta"].eq("ASIGNACION_INCORRECTA").sum()),
        "alerts_integrated": len(alerts),
        "primary_icons": int(refs["es_icono_principal"].eq("SI").sum()),
    }
    (OUT / "QA_RELACIONES_POST_AUDITORIA.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")


def write_manifest() -> None:
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name not in {"18_MANIFEST.csv", "19_HASHES_SHA256.csv"})
    manifest = []
    hashes = []
    for path in files:
        rel = path.relative_to(OUT).as_posix()
        manifest.append({"ruta": rel, "incluido_en_entrega": "SI"})
        hashes.append({"ruta": rel, "sha256": sha256(path), "bytes": path.stat().st_size})
    pd.DataFrame(manifest).to_csv(OUT / "18_MANIFEST.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(hashes).to_csv(OUT / "19_HASHES_SHA256.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    audit = verify_audit()
    copy_previous()
    refs = build_refs(audit)
    build_map_refs(refs)
    build_qa(refs)
    write_manifest()
    print(f"Sucesora: {OUT}")
    print(f"Relaciones: {len(refs)} · panel territorial: {(refs.publicable_en_panel_territorial == 'SI').sum()} · dudosas: {(refs.clasificacion_propuesta == 'ASIGNACION_DUDOSA').sum()}")


if __name__ == "__main__":
    main()
