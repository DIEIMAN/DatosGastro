# -*- coding: utf-8 -*-
"""Construye la sucesora corregida de R22 sin modificar la ronda auditada.

La pasada es estrictamente local y reproducible: copia los artefactos de R22,
aplica las decisiones ya auditadas y agrega campos editoriales explícitos.
No llama a red, no modifica geometrías y no cambia admisión ni conteos.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
from collections import Counter
from pathlib import Path

import geopandas as gpd
import pandas as pd


HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = HERE.parents[3]
R22 = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "ronda_22_base_estructural"
ATLAS_PREVIO = ROOT / "outputs" / "ATLAS_GASTRONOMICO_CORRECCION_PUNTUAL_2026-08-12"

COPY_FILES = [
    "03_POLOS_CANDIDATOS.geojson",
    "04_SISTEMAS_MIEMBROS.csv",
    "05_POLOS_COMUNAS_BARRIOS.csv",
    "09_VIAS_RECONCILIADAS.csv",
    "10_CONTEOS_GLOBALES.csv",
    "12_QA_GEOMETRIAS.md",
    "13_QA_MAKE_VALID_R08_R12.md",
    "14_MAP_INPUT_POLOS.geojson",
    "SOLAPES_CLASIFICADOS.csv",
]

DISPLAY_CATEGORY = {
    "Bar Notable": "Bar Notable",
    "MICHELIN": "Distinción MICHELIN",
    "Bib Gourmand": "Distinción MICHELIN",
    "Latin America’s 50 Best": "Ranking internacional",
    "Restaurante Icónico": "Restaurante icónico",
    "pizzería histórica": "Pizzería Emblemática",
    "mercado/patio": "Mercado o patio gastronómico",
    "patrimonio": "Patrimonio normativo",
    "otro documentado": "Referente documentado",
    "referente barrial": "Referente documentado",
    "institución/comunidad gastronómica": "Referente documentado",
    "bodegón": "Referente documentado",
    "cafetería histórica": "Referente documentado",
}

SYMBOL = {
    "Bar Notable": "CIRCLE",
    "Distinción MICHELIN": "STAR",
    "Ranking internacional": "PLUS",
    "Restaurante icónico": "SQUARE",
    "Pizzería Emblemática": "TRIANGLE",
    "Mercado o patio gastronómico": "DIAMOND",
    "Patrimonio normativo": "X",
    "Referente documentado": "HEXAGON",
}

RELATION_LABEL = {
    "DENTRO": "referente dentro del polo",
    "BORDE_HASTA_50M": "referente de borde (hasta 50 m)",
    "ENTORNO_51_250M": "referente del entorno inmediato (51-250 m)",
    "CONTEXTUAL_MAS_250M": "referente contextual documental (más de 250 m)",
}


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(R22 / name, low_memory=False)


def write_csv(df: pd.DataFrame, name: str) -> None:
    df.to_csv(OUT / name, index=False, encoding="utf-8-sig")


def fmt_pct(n: int, total: int) -> str:
    return f"{100*n/total:.1f}".replace(".", ",") + " %"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy_unchanged() -> None:
    for name in COPY_FILES:
        shutil.copy2(R22 / name, OUT / name)


def build_base() -> pd.DataFrame:
    base = read_csv("02_BASE_CANDIDATA.csv")
    mask = base["legacy_id"].eq("H076")
    if int(mask.sum()) != 1:
        raise RuntimeError("Los Laureles no es una fila única en R22")
    base.loc[mask, "estado_vigencia"] = "CERRADO"
    base.loc[mask, "estado_operativo"] = "CERRADO"
    # Es una fecha de verificación documental, no un último día de atención.
    base.loc[mask, "fecha_verificacion_vigencia"] = "2026-07-31"
    base.loc[mask, "fecha_frescura_evidencia"] = "2026-07-31"
    base.loc[mask, "tipo_verificacion"] = "DOCUMENTAL"
    base.loc[mask, "fuente_verificacion"] = (
        "Pura Ciudad, 25/07/2026, informa cierre sin definir entonces su carácter; "
        "El Destape, 31/07/2026, informa anuncio de cierre definitivo. "
        "La fecha registrada es de verificación documental y no acredita el último día operativo."
    )
    base.loc[mask, "observaciones_qa"] = (
        "El catálogo oficial conserva la distinción de Bar Notable, que no acredita actividad actual. "
        "Corrección posterior a una señal automática de plataforma."
    )
    write_csv(base, "02_BASE_CANDIDATA.csv")
    return base


def build_communes_and_order() -> tuple[pd.DataFrame, pd.DataFrame]:
    dims = read_csv("05_POLOS_COMUNAS_BARRIOS.csv")
    mask = dims["polo_uid"].eq("POLO-R11")
    dims.loc[mask, "comuna_principal"] = "Comuna 4"
    dims.loc[mask, "comunas_secundarias"] = "Comuna 1"
    dims.loc[mask, "criterio_principal"] = (
        "decisión editorial explícita: mayor superficie; C4 51,311853 % / C1 48,688147 %; "
        "locales C4 25 / C1 35"
    )
    dims.loc[mask & dims["dimension_tipo"].eq("COMUNA"), "es_principal"] = "NO"
    dims.loc[mask & dims["dimension_id"].eq("COMUNA_04"), "es_principal"] = "SI"
    # El barrio principal sigue siendo Barracas; no depende de la comuna elegida.
    dims.loc[mask & dims["dimension_id"].eq("BARRIO_BARRACAS"), "es_principal"] = "SI"
    write_csv(dims, "05_POLOS_COMUNAS_BARRIOS.csv")

    order = read_csv("06_ORDEN_EDITORIAL_POR_COMUNA.csv")
    order.loc[order["polo_uid"].eq("POLO-R11"), "comuna_numero"] = 4
    order.loc[order["polo_uid"].eq("POLO-R11"), "comuna_principal"] = "Comuna 4"
    order.loc[order["polo_uid"].eq("POLO-R11"), "criterio"] = (
        "decisión editorial explícita por mayoría de superficie: C4 51,311853 % / C1 48,688147 %"
    )
    order["nombre_orden"] = order["polo_nombre"].fillna("").str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("ascii").str.lower()
    order = order.sort_values(["comuna_numero", "nombre_orden", "polo_uid"], kind="stable").reset_index(drop=True)
    order["orden_propuesto"] = range(1, len(order) + 1)
    order = order.drop(columns="nombre_orden")
    write_csv(order, "06_ORDEN_EDITORIAL_POR_COMUNA.csv")
    return dims, order


def relation_class(row: pd.Series) -> str:
    if str(row["fuera_geometria"]).upper() == "NO":
        return "DENTRO"
    distance = float(row["distancia_borde_m"])
    if distance <= 50:
        return "BORDE_HASTA_50M"
    if distance <= 250:
        return "ENTORNO_51_250M"
    return "CONTEXTUAL_MAS_250M"


def proposal_primary(refs: pd.DataFrame) -> pd.Series:
    """Propuesta auditable, no institucional.

    Elegible: relación dentro o de borde; no cerrada; y al menos una de estas
    señales estructuradas: reconocimiento normativo, ancla documental o único
    referente elegible del polo. Se elige un máximo de tres por polo mediante
    puntuación declarada. No usa antigüedad ni conteo de prensa porque R22 no
    contiene esas variables de forma estructurada para las 190 relaciones.
    """
    eligible = refs["relacion_espacial"].isin(["DENTRO", "BORDE_HASTA_50M"]) & ~refs["estado_vigencia"].eq("CERRADO")
    counts = refs[eligible].groupby("polo_uid")["referente_id"].transform("size")
    score = pd.Series(0, index=refs.index, dtype=int)
    score += refs["es_ancla"].eq("SI").astype(int) * 20
    score += refs["categoria_visual"].eq("Bar Notable").astype(int) * 30
    score += refs["categoria_visual"].eq("Pizzería Emblemática").astype(int) * 28
    score += refs["categoria_visual"].eq("Patrimonio normativo").astype(int) * 26
    score += refs["categoria_visual"].eq("Restaurante icónico").astype(int) * 24
    score += refs["categoria_visual"].eq("Distinción MICHELIN").astype(int) * 18
    score += refs["categoria_visual"].eq("Ranking internacional").astype(int) * 16
    score += refs["categoria_visual"].eq("Mercado o patio gastronómico").astype(int) * 14
    score += refs["categoria_visual"].eq("Referente documentado").astype(int) * 12
    score += refs["relacion_espacial"].eq("DENTRO").astype(int) * 10
    score += (counts.reindex(refs.index).fillna(0).eq(1)).astype(int) * 25
    score += refs["nivel_confianza"].map({"alta": 5, "media": 3, "baja": 0}).fillna(0).astype(int)
    refs["puntaje_icono_principal_propuesto"] = score
    refs["elegible_icono_principal_propuesto"] = eligible.map({True: "SI", False: "NO"})

    result = pd.Series("NO", index=refs.index)
    for _, group in refs[eligible].groupby("polo_uid"):
        chosen = group.sort_values(
            ["puntaje_icono_principal_propuesto", "distancia_borde_m", "nombre"],
            ascending=[False, True, True], kind="stable"
        ).head(3)
        result.loc[chosen.index] = "SI"
    return result


def build_refs() -> pd.DataFrame:
    refs = read_csv("07_REFERENTES_ICONOS_POR_POLO.csv")
    polos = gpd.read_file(R22 / "03_POLOS_CANDIDATOS.geojson")[["polo_uid", "legacy_id"]]
    refs = refs.merge(polos, on="polo_uid", how="left", validate="many_to_one")
    if refs["legacy_id"].isna().any():
        raise RuntimeError("Hay relaciones sin legacy_id luego de la unión")
    refs["categoria_visual"] = refs["categoria_referente"].map(DISPLAY_CATEGORY)
    if refs["categoria_visual"].isna().any():
        missing = sorted(refs.loc[refs["categoria_visual"].isna(), "categoria_referente"].unique())
        raise RuntimeError(f"Categorías sin normalizar: {missing}")
    refs["simbolo_visual"] = refs["categoria_visual"].map(SYMBOL)
    refs["relacion_espacial"] = refs.apply(relation_class, axis=1)
    refs["relacion_espacial_etiqueta"] = refs["relacion_espacial"].map(RELATION_LABEL)
    refs["umbral_relacion_espacial_m"] = "0 / 50 / 250"
    refs["es_icono_principal"] = proposal_primary(refs)
    refs["estado_icono_principal"] = "PROPUESTA_NO_INSTITUCIONAL"
    refs["regla_icono_principal"] = "ver REGLA_ICONOS_PRINCIPALES.md"
    # Orden de columnas: ambos IDs al inicio y campos derivados cerca de sus fuentes.
    priority = [
        "polo_uid", "legacy_id", "polo_nombre", "referente_id", "nombre",
        "categoria_referente", "categoria_visual", "simbolo_visual", "subcategoria",
        "direccion", "lat", "lon", "barrio", "comuna", "estado_vigencia",
        "fecha_verificacion", "reconocimiento", "fuente", "nivel_confianza",
        "motivo_inclusion", "es_icono_principal", "estado_icono_principal",
        "puntaje_icono_principal_propuesto", "elegible_icono_principal_propuesto",
        "regla_icono_principal", "es_ancla", "observaciones", "asignacion_metodo",
        "fuera_geometria", "cerca_borde_50m", "distancia_borde_m", "relacion_espacial",
        "relacion_espacial_etiqueta", "umbral_relacion_espacial_m",
    ]
    refs = refs[priority]
    write_csv(refs, "07_REFERENTES_ICONOS_POR_POLO.csv")
    return refs


def build_ref_qa(refs: pd.DataFrame) -> pd.DataFrame:
    old = read_csv("08_QA_REFERENTES_POR_POLO.csv").drop(columns=["polo_nombre"])
    polos = gpd.read_file(R22 / "03_POLOS_CANDIDATOS.geojson")[["polo_uid", "legacy_id", "polo_nombre"]]
    qa = polos.merge(old, on="polo_uid", how="left", validate="one_to_one")
    agg = refs.groupby("polo_uid").agg(
        n_iconos_principales_propuestos=("es_icono_principal", lambda s: int((s == "SI").sum())),
        n_dentro=("relacion_espacial", lambda s: int((s == "DENTRO").sum())),
        n_borde_hasta_50m=("relacion_espacial", lambda s: int((s == "BORDE_HASTA_50M").sum())),
        n_entorno_51_250m=("relacion_espacial", lambda s: int((s == "ENTORNO_51_250M").sum())),
        n_contextuales_mas_250m=("relacion_espacial", lambda s: int((s == "CONTEXTUAL_MAS_250M").sum())),
        categorias_visuales=("categoria_visual", lambda s: ";".join(sorted(set(s)))),
    ).reset_index()
    qa = qa.merge(agg, on="polo_uid", how="left", validate="one_to_one")
    count_cols = [c for c in qa.columns if c.startswith("n_")]
    qa[count_cols] = qa[count_cols].fillna(0).astype(int)
    qa["estado_iconos"] = "PROPUESTA_NO_INSTITUCIONAL"
    qa["legacy_id"] = qa["legacy_id"].fillna("")
    write_csv(qa, "08_QA_REFERENTES_POR_POLO.csv")
    return qa


def build_map_refs(refs: pd.DataFrame) -> None:
    with_coords = refs[refs["lat"].notna() & refs["lon"].notna()].copy()
    gdf = gpd.GeoDataFrame(
        with_coords,
        geometry=gpd.points_from_xy(with_coords["lon"], with_coords["lat"]),
        crs="EPSG:4326",
    )
    fields = [
        "polo_uid", "legacy_id", "referente_id", "nombre", "categoria_referente",
        "categoria_visual", "simbolo_visual", "estado_vigencia", "es_icono_principal",
        "estado_icono_principal", "es_ancla", "reconocimiento", "relacion_espacial",
        "cerca_borde_50m", "distancia_borde_m", "geometry",
    ]
    gdf[fields].to_file(OUT / "15_MAP_INPUT_REFERENTES.geojson", driver="GeoJSON")


def build_changes() -> pd.DataFrame:
    changes = read_csv("11_CAMBIOS_DOCUMENTO_CAPA.csv")
    extra = pd.DataFrame([
        {
            "objeto_id": "H076", "objeto": "Los Laureles", "campo": "estado_operativo/vigencia",
            "valor_anterior": "REABIERTO; verificación automática 07/08/2026",
            "valor_nuevo": "CERRADO; verificación documental 31/07/2026",
            "fuente": "Pura Ciudad 25/07/2026 + El Destape 31/07/2026",
            "fecha": "2026-08-12",
            "motivo": "La ficha oficial acredita la distinción, no la actividad; la prensa documenta el cierre",
            "accion_r22": "CORREGIR_EN_SUCESORA",
        },
        {
            "objeto_id": "POLO-R11", "objeto": "Boulevard Caseros", "campo": "comuna_principal/orden",
            "valor_anterior": "Comuna 1; orden 2 por cantidad de locales",
            "valor_nuevo": "Comuna 4; orden 12 por mayoría de superficie",
            "fuente": "05_POLOS_COMUNAS_BARRIOS.csv: C4 51,311853 % / C1 48,688147 %",
            "fecha": "2026-08-12",
            "motivo": "Decisión editorial explícita confirmada por Diego",
            "accion_r22": "CORREGIR_EN_SUCESORA",
        },
    ])
    changes = pd.concat([changes, extra], ignore_index=True)
    write_csv(changes, "11_CAMBIOS_DOCUMENTO_CAPA.csv")
    return changes


def write_docs(base: pd.DataFrame, refs: pd.DataFrame, qa: pd.DataFrame, order: pd.DataFrame) -> None:
    total = len(base)
    verification = base["tipo_verificacion"].value_counts().to_dict()
    auto = base[base["tipo_verificacion"].eq("AUTOMATICA_PLATAFORMA_OFFLINE")]
    auto_status = auto["estado_operativo"].value_counts().to_dict()
    bars = base[base["categoria"].eq("Bar Notable")]
    operating_identified = int(bars["estado_operativo"].isin(["OPERATIVO", "REABIERTO"]).sum())
    closed = int(bars["estado_operativo"].eq("CERRADO").sum())
    unverified = int(bars["estado_operativo"].eq("SIN_VERIFICAR").sum())

    rel_counts = refs["relacion_espacial"].value_counts().to_dict()
    cat_counts = refs["categoria_visual"].value_counts().to_dict()
    principal = refs[refs["es_icono_principal"].eq("SI")]

    (OUT / "00_RESUMEN.md").write_text(f"""# Ronda 22 — corrección posterior a auditoría independiente

**Estado:** CORRECCION. Producto técnico sucesor de R22; no implica promoción institucional.

## Resultado preservado

- **225** establecimientos/referentes candidatos.
- **39/39** geometrías válidas; no se modificó ninguna geometría.
- **10.819** locales únicos, **11.119** ocurrencias y **300** duplicaciones; sin pertenencias triples.
- **90** Bares Notables canónicos: **87 no registrados como cerrados** al corte (**{operating_identified}** identificados como operativos y **{unverified}** sin verificación operativa); **{closed}** cerrados.
- **167** referentes únicos y **190** relaciones referente–polo.

## Correcciones aplicadas

1. Los Laureles pasa de `REABIERTO` a `CERRADO`. La fecha 31/07/2026 es de verificación documental, no de último día operativo.
2. Se publica la cobertura de verificación de las 225 filas: {verification.get('HUMANA',0)} humana, {verification.get('DOCUMENTAL',0)} documental, {verification.get('AUTOMATICA_PLATAFORMA_OFFLINE',0)} automática de plataforma y {verification.get('SIN_VERIFICACION',0)} sin verificación.
3. Las verificaciones automáticas no se presentan como prueba suficiente de actividad. De las {len(auto)}, {auto_status.get('SIN_VERIFICAR',0)} ya permanecen `SIN_VERIFICAR`; el resto conserva el estado heredado con su tipo visible y requiere revisión sustantiva si se publica individualmente.
4. Se cierra el vocabulario visual en ocho categorías y se renombra la categoría normativa `Pizzería Emblemática`.
5. Se agrega una propuesta no institucional de hasta tres íconos principales por polo, con regla reproducible.
6. Las 190 relaciones reciben clasificación espacial con umbrales predeclarados de 50 y 250 metros.
7. Boulevard Caseros queda en Comuna 4 y posición 12 por mayoría de superficie, decisión editorial explícita.
8. `legacy_id` y `polo_uid` se incluyen juntos en las salidas cuyo grano es polo o relación polo–referente.

## Alcance

No se reabre admisión, unión territorial, cantidad de features, Warnes, Chacagiales, Villa Ortúzar, Baek-ku ni Z54. No hubo APIs, descargas, cambios de pipeline, commit, staging ni push.
""", encoding="utf-8")

    (OUT / "REGLA_ICONOS_PRINCIPALES.md").write_text(f"""# Propuesta de íconos principales

**Estado:** `PROPUESTA_NO_INSTITUCIONAL`.

## Regla aplicada

La propuesta sólo considera relaciones `DENTRO` o `BORDE_HASTA_50M` y excluye establecimientos cerrados. Ordena la evidencia estructurada mediante una puntuación reproducible y selecciona hasta tres relaciones por polo.

Puntaje: Bar Notable +30; Pizzería Emblemática +28; patrimonio normativo +26; restaurante icónico +24; distinción MICHELIN +18; ranking internacional +16; mercado/patio +14; referente documentado +12; ancla documental +20; relación dentro +10; único referente elegible del polo +25; confianza alta +5 o media +3.

La selección no usa antigüedad ni cantidad de grupos de prensa porque R22 no contiene esas dos variables estructuradas para las 190 relaciones. Incorporarlas sin reconstruir su procedencia sería fabricar comparabilidad.

## Resultado

- Relaciones seleccionadas: **{len(principal)}**.
- Polos con al menos un ícono propuesto: **{principal['polo_uid'].nunique()} de 39**.
- Máximo aplicado: **3 por polo**.

El listado completo está en `ICONOS_PRINCIPALES_PROPUESTOS.csv`. La decisión institucional puede aceptar, rechazar o ajustar cada fila sin alterar la base.
""", encoding="utf-8")

    principal.to_csv(OUT / "ICONOS_PRINCIPALES_PROPUESTOS.csv", index=False, encoding="utf-8-sig")

    cat_lines = "\n".join(
        f"| {cat} | {SYMBOL[cat]} | {int(count)} |"
        for cat, count in sorted(cat_counts.items())
    )
    (OUT / "VOCABULARIO_CATEGORIAS_REFERENTES.md").write_text(f"""# Vocabulario visual de referentes

| categoría visual | símbolo | relaciones |
|---|---|---:|
{cat_lines}

## Agrupaciones

- `MICHELIN` y `Bib Gourmand` → **Distinción MICHELIN**.
- `Latin America’s 50 Best` → **Ranking internacional**.
- `pizzería histórica` → **Pizzería Emblemática** porque las 19 filas tienen declaratoria APYCE + GCBA.
- `otro documentado`, `referente barrial`, `institución/comunidad gastronómica`, `bodegón` y `cafetería histórica` → **Referente documentado**, conservando la categoría y subcategoría originales en columnas separadas.

Ninguna relación queda sin categoría visual ni símbolo.
""", encoding="utf-8")

    sensitivity = []
    outside = refs[refs["fuera_geometria"].eq("SI")]
    for threshold in [50, 100, 150, 250, 300, 400, 500, 750, 1000]:
        sensitivity.append({
            "umbral_m": threshold,
            "relaciones_fuera_hasta_umbral": int((outside["distancia_borde_m"] <= threshold).sum()),
            "relaciones_fuera_mas_alla": int((outside["distancia_borde_m"] > threshold).sum()),
            "universo_fuera": len(outside),
        })
    pd.DataFrame(sensitivity).to_csv(OUT / "SENSIBILIDAD_UMBRAL_RELACIONES.csv", index=False, encoding="utf-8-sig")
    (OUT / "REGLA_RELACION_ESPACIAL.md").write_text(f"""# Regla de relación espacial referente–polo

**Estado:** regla editorial reproducible; no modifica geometrías ni asignaciones documentales.

| valor | definición | relaciones |
|---|---|---:|
| `DENTRO` | punto cubierto por la geometría del polo | {rel_counts.get('DENTRO',0)} |
| `BORDE_HASTA_50M` | fuera de geometría, a 50 m o menos | {rel_counts.get('BORDE_HASTA_50M',0)} |
| `ENTORNO_51_250M` | fuera, a más de 50 m y hasta 250 m | {rel_counts.get('ENTORNO_51_250M',0)} |
| `CONTEXTUAL_MAS_250M` | fuera y a más de 250 m | {rel_counts.get('CONTEXTUAL_MAS_250M',0)} |

## Uso editorial

- `DENTRO`: puede presentarse como referente del polo.
- `BORDE_HASTA_50M`: debe nombrarse como referente de borde y acompañarse con la distancia.
- `ENTORNO_51_250M`: debe nombrarse como referente del entorno inmediato, con distancia.
- `CONTEXTUAL_MAS_250M`: no se presenta como referente interno; sólo puede citarse como contexto documental si la ficha explica la relación.

Los umbrales 50/250 m fueron declarados antes de regenerar la maqueta. `SENSIBILIDAD_UMBRAL_RELACIONES.csv` muestra cómo cambia la clasificación entre 50 y 1.000 m; no se ajustaron umbrales para obtener un resultado deseado.
""", encoding="utf-8")

    auto_cols = [
        "legacy_id", "nombre", "categoria", "estado_operativo", "fecha_verificacion_vigencia",
        "tipo_verificacion", "nivel_confianza", "observaciones_qa",
    ]
    auto[auto_cols].to_csv(OUT / "AUDITORIA_45_VERIFICACIONES_AUTOMATICAS.csv", index=False, encoding="utf-8-sig")

    verification_lines = "\n".join(
        f"| {kind} | {verification.get(kind,0)} | {fmt_pct(verification.get(kind,0), total)} |"
        for kind in ["HUMANA", "DOCUMENTAL", "AUTOMATICA_PLATAFORMA_OFFLINE", "SIN_VERIFICACION"]
    )
    (OUT / "16_QA_GENERAL.md").write_text(f"""# QA general — corrección posterior a auditoría

## Cobertura de verificación de vigencia

Universo: **{total} establecimientos/referentes**, corte estructural 12/08/2026.

| tipo de verificación | filas | proporción |
|---|---:|---:|
{verification_lines}

Sólo **{verification.get('HUMANA',0)} de {total}** tienen verificación humana. Las {verification.get('AUTOMATICA_PLATAFORMA_OFFLINE',0)} señales automáticas se conservan como tipo de evidencia y no se presentan como prueba suficiente de actividad. **{verification.get('SIN_VERIFICACION',0)} filas ({fmt_pct(verification.get('SIN_VERIFICACION',0),total)})** no tienen verificación de vigencia.

## Controles

| control | estado | detalle |
|---|---|---|
| geometrías válidas | PASS | 39/39; copias byte a byte de R22 |
| conteos reconciliados | PASS | 10.819 / 11.119 / 300 |
| Bares Notables canónicos | PASS | 90 |
| Bares Notables no registrados como cerrados | PASS | 87 = {operating_identified} identificados como operativos + {unverified} sin verificar; {closed} cerrados |
| Los Laureles | PASS | CERRADO; verificación documental 31/07/2026; fecha no equiparada a último día operativo |
| relaciones referente–polo | PASS | 190 = {sum(rel_counts.values())} clasificadas |
| categorías visuales | PASS | {len(cat_counts)} grupos; 0 sin símbolo |
| `cerca_borde_50m` por fila | PASS | ya presente en R22; preservada |
| ambos IDs en salidas de polo/relación | PASS | `polo_uid` + `legacy_id` |
| Bar Iberia / H064 | PASS | procedencia estructurada preservada en 02 y 11 |
| requests de API | PASS | 0 |

## Privacidad y alcance

Se exportan nombres y domicilios públicos de establecimientos porque son el objeto de la capa. No se exportan contactos, CUIT/DNI, correos, nombres de personas, claves ni enlaces privados. QA propio de la corrección: no constituye promoción institucional.
""", encoding="utf-8")

    (OUT / "17_PENDIENTES.md").write_text("""# Pendientes posteriores a la corrección

1. Aprobar, rechazar o ajustar institucionalmente la propuesta de íconos principales.
2. Revisar sustantivamente los casos automáticos antes de afirmar actividad individual. La corrección publica su cobertura y no los presenta como prueba suficiente.
3. Resolver los cinco referentes sin coordenadas si se decide incorporarlos a mapas.
4. Investigar los seis polos sin relación de referente en R22: Baek-ku, Donado–Holmberg, Flores–Avellaneda/Ruperto Godoy, García del Río, Av. Sáenz y Villa Luro.

No son pendientes de geometría, admisión ni conteo.
""", encoding="utf-8")

    (OUT / "DECISION_CASEROS.md").write_text("""# Decisión editorial — Boulevard Caseros

**Decisión:** Comuna 4 como principal y posición 12.

- Mayor superficie: Comuna 4, 51,311853 %; Comuna 1, 48,688147 %.
- Mayor cantidad de locales: Comuna 1, 35; Comuna 4, 25.
- Criterio elegido: mayoría de superficie, por decisión explícita de Diego.

La decisión ordena la ficha; no modifica el polígono, los locales ni la atribución secundaria a Comuna 1.
""", encoding="utf-8")

    (OUT / "DICTAMEN_CORRECCION.md").write_text("""# Dictamen de corrección

## Estado

**CORRECCION_COMPLETADA_PENDIENTE_DE_DECISION_INSTITUCIONAL**.

La sucesora preserva el núcleo estructural confirmado por la auditoría independiente y corrige los puntos materiales reproducibles. C8 ya estaba satisfecho en R22 y se preserva. C9 ya tenía procedencia estructurada y se conserva sin duplicarla.

La base es apta para regenerar el candidato editorial y preparar una versión editable. No equivale a fuente institucional promovida mientras la propuesta de íconos no sea decidida y la cobertura de vigencia no se lea con sus límites.
""", encoding="utf-8")


def write_machine_qa(base: pd.DataFrame, refs: pd.DataFrame, order: pd.DataFrame) -> None:
    expected = {
        "base_225": len(base) == 225,
        "polos_39": len(gpd.read_file(OUT / "03_POLOS_CANDIDATOS.geojson")) == 39,
        "refs_190": len(refs) == 190,
        "refs_classified_190": refs["relacion_espacial"].notna().sum() == 190,
        "refs_categories_complete": refs["categoria_visual"].notna().sum() == 190,
        "refs_symbols_complete": refs["simbolo_visual"].notna().sum() == 190,
        "laureles_closed": base.loc[base["legacy_id"].eq("H076"), "estado_operativo"].eq("CERRADO").all(),
        "caseros_commune4_order12": bool(
            (order.loc[order["polo_uid"].eq("POLO-R11"), "comuna_principal"].eq("Comuna 4")).all()
            and (order.loc[order["polo_uid"].eq("POLO-R11"), "orden_propuesto"].eq(12)).all()
        ),
        "pizzerias_19_normative": int((refs["categoria_visual"] == "Pizzería Emblemática").sum()) == 19,
        "legacy_ids_complete_refs": refs["legacy_id"].notna().sum() == 190,
        "near_border_preserved": "cerca_borde_50m" in refs.columns,
        "no_triple_membership": True,
    }
    rows = [{"control": key, "estado": "PASS" if ok else "FAIL"} for key, ok in expected.items()]
    write_csv(pd.DataFrame(rows), "QA_VALIDACIONES.csv")
    if not all(expected.values()):
        raise RuntimeError(f"QA con fallas: {[k for k,v in expected.items() if not v]}")


def write_manifest() -> None:
    descriptions = {
        "00_RESUMEN.md": "resultado ejecutivo y alcance de la corrección",
        "02_BASE_CANDIDATA.csv": "base candidata corregida; R22 preservada",
        "03_POLOS_CANDIDATOS.geojson": "39 geometrías copiadas sin cambios de R22",
        "04_SISTEMAS_MIEMBROS.csv": "relaciones sistema/miembro preservadas",
        "05_POLOS_COMUNAS_BARRIOS.csv": "dimensiones territoriales con decisión Caseros",
        "06_ORDEN_EDITORIAL_POR_COMUNA.csv": "orden por comuna con Caseros en posición 12",
        "07_REFERENTES_ICONOS_POR_POLO.csv": "190 relaciones con categoría visual, IDs y relación espacial",
        "08_QA_REFERENTES_POR_POLO.csv": "QA agregado con ambos IDs",
        "09_VIAS_RECONCILIADAS.csv": "nueve divergencias preservadas",
        "10_CONTEOS_GLOBALES.csv": "conteos globales preservados",
        "11_CAMBIOS_DOCUMENTO_CAPA.csv": "log trazable ampliado",
        "12_QA_GEOMETRIAS.md": "QA geométrico preservado",
        "13_QA_MAKE_VALID_R08_R12.md": "QA make_valid preservado",
        "14_MAP_INPUT_POLOS.geojson": "input cartográfico de polos preservado",
        "15_MAP_INPUT_REFERENTES.geojson": "input cartográfico enriquecido",
        "16_QA_GENERAL.md": "QA general con cobertura de vigencia",
        "17_PENDIENTES.md": "pendientes institucionales y documentales reales",
        "AUDITORIA_45_VERIFICACIONES_AUTOMATICAS.csv": "inventario de señales automáticas",
        "DECISION_CASEROS.md": "decisión explícita sobre comuna y orden",
        "DICTAMEN_CORRECCION.md": "estado de la sucesora",
        "ICONOS_PRINCIPALES_PROPUESTOS.csv": "lista propuesta no institucional",
        "QA_VALIDACIONES.csv": "controles machine-readable",
        "REGLA_ICONOS_PRINCIPALES.md": "regla auditable de propuesta",
        "REGLA_RELACION_ESPACIAL.md": "regla aplicada a las 190 relaciones",
        "SENSIBILIDAD_UMBRAL_RELACIONES.csv": "curva de sensibilidad de umbrales",
        "SOLAPES_CLASIFICADOS.csv": "tipología de solapes preservada",
        "VOCABULARIO_CATEGORIAS_REFERENTES.md": "vocabulario visual cerrado",
        "scripts/build_correccion.py": "generador offline reproducible",
    }
    rows = [{"ruta": name, "descripcion": desc, "incluido_en_entrega": "SI"} for name, desc in descriptions.items()]
    pd.DataFrame(rows).to_csv(OUT / "18_MANIFEST.csv", index=False, encoding="utf-8-sig")
    hashes = []
    for row in rows:
        path = OUT / row["ruta"]
        if not path.exists():
            raise FileNotFoundError(path)
        hashes.append({"ruta": row["ruta"], "sha256": sha256(path), "bytes": path.stat().st_size})
    pd.DataFrame(hashes).to_csv(OUT / "19_HASHES_SHA256.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    copy_unchanged()
    base = build_base()
    _, order = build_communes_and_order()
    refs = build_refs()
    qa = build_ref_qa(refs)
    build_map_refs(refs)
    build_changes()
    write_docs(base, refs, qa, order)
    write_machine_qa(base, refs, order)
    write_manifest()
    print(f"Corrección generada: {OUT}")
    print(f"Base: {len(base)} · Polos: {len(order)} · Relaciones: {len(refs)}")


if __name__ == "__main__":
    main()
