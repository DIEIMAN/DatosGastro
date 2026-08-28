# -*- coding: utf-8 -*-
"""Revision editorial de poligonos completos v1.

EXPERIMENTAL / no oficial. No llama APIs y no modifica outputs base de
`completa_v1`; crea derivados en `revision_editorial_v1`.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import geopandas as gpd
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
BASE = (ROOT / "outputs" / "polos_gastro" / "experimentos"
        / "google_places_microzonas_ampliacion_v1" / "completa_v1")
DOCS = (ROOT / "docs" / "polos_gastro" / "experimentos"
        / "google_places_microzonas_ampliacion_v1")
OUT = BASE / "revision_editorial_v1"

POLIGONOS = BASE / "POLIGONOS_MICROZONAS_COMPLETA_V1.geojson"
PUNTOS = BASE / "MICROCLUSTERS_COMPLETA_V1.geojson"
QA_INTEGRACION = BASE / "qa_integracion_completa_v1.json"
QA_CLUSTERS = BASE / "qa_clusters_completa_v1.json"
MAPAS = BASE / "mapas"

OUT_TABLA = OUT / "tabla_revision_editorial_poligonos_completa_v1.csv"
OUT_RESUMEN_JSON = OUT / "resumen_revision_editorial_poligonos_completa_v1.json"
OUT_CONTACT = OUT / "contact_sheet_mapas_completa_v1.png"
OUT_RESUMEN_MD = DOCS / "RESUMEN_EJECUTIVO_REVISION_COMPLETA_V1.md"
OUT_HANDOFF_MD = DOCS / "HANDOFF_REVISION_POLIGONOS_COMPLETA_V1.md"

CRS_METRICO = "EPSG:5347"

TITULOS_ZONA = {
    "corrientes_microcentro": "Corrientes / Microcentro",
    "belgrano": "Belgrano",
    "palermo_soho_hollywood": "Palermo Soho / Hollywood",
    "san_telmo": "San Telmo",
    "chacarita": "Chacarita",
    "villa_crespo": "Villa Crespo",
    "recoleta": "Recoleta",
    "caballito": "Caballito",
    "puerto_madero": "Puerto Madero",
    "costanera_norte": "Costanera Norte",
    "caseros_barracas": "Av. Caseros / Barracas",
}

LECTURAS_ZONA = {
    "MZ_AVENIDA_CORRIENTES": "Eje Corrientes / Once-Abasto-Centro; revisar continuidad lineal y cortes transversales.",
    "MZ_MICROCENTRO_Y_CENTRO": "Centro historico-administrativo; microzonas de alta densidad y cortes finos por manzana.",
    "MZ_BELGRANO": "Belgrano: posibles piezas Cabildo, Juramento, Barrio Chino y Bajo Belgrano.",
    "MZ_PALERMO_SOHO": "Palermo Soho: entorno Plaza Serrano, Armenia, Honduras y Gorriti.",
    "MZ_PALERMO_HOLLYWOOD": "Palermo Hollywood: entorno Fitz Roy, Humboldt, Nicaragua y corredores nocturnos.",
    "MZ_SAN_TELMO": "San Telmo: Defensa, Plaza Dorrego, Mercado y borde sur.",
    "MZ_CHACARITA": "Chacarita: eje Dorrego / Corrientes / cementerio; revisar saturacion inicial.",
    "MZ_VILLA_CRESPO": "Villa Crespo: continuidad con Palermo y Corrientes; revisar fusiones de corredor.",
    "MZ_RECOLETA": "Recoleta: tejido denso con posible exceso de particion interna.",
    "MZ_CABALLITO": "Caballito: Av. Rivadavia, Primera Junta y Pedro Goyena; riesgo de corredores partidos.",
    "MZ_PUERTO_MADERO": "Puerto Madero: diques y frentes costeros; controlar baja densidad y piezas aisladas.",
    "MZ_COSTANERA_NORTE": "Costanera Norte: oferta visible muy dependiente de Places; confianza institucional baja.",
    "MZ_AVENIDA_CASEROS_BARRACAS": "Av. Caseros / Barracas: eje emergente con evidencia acotada.",
}

ZONAS_DEBILES = {"MZ_COSTANERA_NORTE", "MZ_AVENIDA_CASEROS_BARRACAS"}


def shape_compactness(geom) -> float:
    area = geom.area
    perim = geom.length
    if perim <= 0:
        return 0.0
    return 4 * math.pi * area / (perim * perim)


def tile_like(row, compactness: float) -> bool:
    return (
        int(row["ronda"]) > 0
        and float(row["area_ha"]) >= 7.0
        and float(row["elongacion"]) < 1.8
        and compactness >= 0.25
    )


def lectura_orientativa(row, f01, places, pct_places) -> str:
    base = LECTURAS_ZONA.get(row["macrozona_id"], "Lectura urbana pendiente de revision manual.")
    add = []
    if row["es_corredor"]:
        add.append("forma de corredor")
    if pct_places >= 80:
        add.append("alta dependencia de Places")
    if f01 < 5:
        add.append("bajo respaldo F01+F02")
    if float(row["area_ha"]) < 2.0 and int(row["n_puntos"]) >= 12:
        add.append("pieza chica pero densa")
    if add:
        return base + " Senales: " + ", ".join(add) + "."
    return base


def clasificar(row, f01: int, places: int, pct_places: float, compactness: float) -> tuple[str, str, str, str]:
    problemas = []
    acciones = []

    n = int(row["n_puntos"])
    area = float(row["area_ha"])
    dens = float(row["densidad_ha"])
    elong = float(row["elongacion"])
    ronda = int(row["ronda"])
    macro = row["macrozona_id"]

    if macro in ZONAS_DEBILES:
        problemas.append("macrozona_debil_o_emergente")
    if ronda > 0:
        problemas.append("corte_por_subdivision_kmeans")
        acciones.append("validar_si_el_corte_es_defendible")
    if tile_like(row, compactness):
        problemas.append("poligono_tipo_tile")
        acciones.append("revisar_corte_manual")
    if row["es_corredor"] and elong >= 3.0:
        problemas.append("corredor_lineal")
        acciones.append("revisar_continuidad_o_fusion")
    if pct_places >= 80:
        problemas.append("exceso_places_poco_respaldo_f01f02")
        acciones.append("mantener_como_senal_no_oficial")
    if f01 < 5:
        problemas.append("bajo_respaldo_f01f02")
    if dens < 4:
        problemas.append("baja_densidad")
    if area > 15:
        problemas.append("poligono_grande")
        acciones.append("revisar_subdivision_o_limite")
    if n < 8:
        problemas.append("pocos_puntos")
    if float(row["diametro_m"]) > 950 and not row["es_corredor"]:
        problemas.append("diametro_alto_no_corredor")

    # Confianzas
    conf_alg = "ALTA"
    if ronda > 0 or tile_like(row, compactness) or n < 10:
        conf_alg = "MEDIA"
    if dens < 3 or n < 6:
        conf_alg = "BAJA"

    conf_ed = "ALTA"
    if macro in ZONAS_DEBILES or pct_places >= 75 or f01 < 5:
        conf_ed = "MEDIA"
    if (macro in ZONAS_DEBILES and pct_places >= 75) or dens < 3:
        conf_ed = "BAJA"

    # Accion editorial prudente
    if dens < 2.5 or n < 5:
        accion = "DESCARTAR"
    elif macro in ZONAS_DEBILES and (pct_places >= 70 or f01 < 5):
        accion = "REVISAR UNIVERSO"
    elif tile_like(row, compactness) or (ronda > 0 and area >= 7):
        accion = "REVISAR CORTE"
    elif row["es_corredor"] and elong >= 3.0:
        accion = "REVISAR FUSION"
    elif pct_places >= 80 and f01 < 8:
        accion = "REVISAR UNIVERSO"
    elif problemas:
        accion = "APROBAR CON OBSERVACIONES"
    else:
        accion = "APROBAR"

    if not acciones:
        acciones.append({
            "APROBAR": "conservar_como_microzona_candidata",
            "APROBAR CON OBSERVACIONES": "conservar_con_nota_metodologica",
            "REVISAR CORTE": "revisar_limite_y_posible_redibujo",
            "REVISAR FUSION": "evaluar_fusion_con_poligonos_contiguos",
            "REVISAR UNIVERSO": "validar_con_fuentes_no_places_y_revision_humana",
            "DESCARTAR": "descartar_de_capa_editorial",
        }[accion])

    return accion, conf_alg, conf_ed, "; ".join(sorted(set(problemas))) or "sin_problema_relevante", "; ".join(sorted(set(acciones)))


def crear_contact_sheet() -> None:
    maps = sorted(MAPAS.glob("*.png"))
    thumbs = []
    for p in maps:
        im = Image.open(p).convert("RGB")
        im.thumbnail((520, 420))
        thumbs.append((p, im.copy()))
    cols = 2
    pad = 24
    title_h = 44
    cell_w = 560
    cell_h = 500
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * cell_w + pad, rows * cell_h + pad), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    for i, (path, im) in enumerate(thumbs):
        r, c = divmod(i, cols)
        x = pad + c * cell_w
        y = pad + r * cell_h
        label = path.stem.replace("mapa_completa_v1_", "")
        draw.text((x, y), label, fill=(20, 20, 20), font=font)
        sheet.paste(im, (x, y + title_h))
        draw.text((x, y + title_h + im.height + 8), path.name, fill=(80, 80, 80),
                  font=font_small)
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_CONTACT)


def resumenes_markdown(tabla: pd.DataFrame, resumen: dict) -> tuple[str, str]:
    conteo = tabla["accion_recomendada"].value_counts().to_dict()
    mejores = tabla[tabla["accion_recomendada"].isin(["APROBAR", "APROBAR CON OBSERVACIONES"])].copy()
    mejores = mejores.sort_values(["confianza_editorial", "densidad_entidades_ha", "cantidad_entidades"],
                                  ascending=[True, False, False]).head(12)
    problematicas = tabla[tabla["accion_recomendada"].isin(["REVISAR CORTE", "REVISAR FUSION", "REVISAR UNIVERSO", "DESCARTAR"])]
    prob_zonas = problematicas.groupby("macrozona").size().sort_values(ascending=False).head(8)

    resumen_md = [
        "# Resumen ejecutivo - revision editorial poligonos completa v1",
        "",
        "Estado: EXPERIMENTAL / no oficial. No define limites oficiales ni acredita locales activos.",
        "",
        "## Hallazgos robustos",
        "",
        f"- Se revisaron {len(tabla)} poligonos experimentales generados sobre el universo completo sanitizado.",
        f"- La clasificacion preliminar deja {conteo.get('APROBAR', 0)} poligonos en aprobar y {conteo.get('APROBAR CON OBSERVACIONES', 0)} en aprobar con observaciones.",
        "- Las zonas con mejor lectura preliminar combinan densidad, continuidad territorial y respaldo F01+F02: Corrientes/Microcentro, Belgrano, Palermo, San Telmo y sectores de Caballito.",
        "- La capa completa permite pasar a una revision humana de cortes sin requerir nuevas llamadas a Google Places.",
        "- Las piezas pequenas y densas tienden a ser mas defendibles que los recortes grandes o subdivididos por KMeans.",
        "",
        "## Pendientes editoriales",
        "",
        f"- {conteo.get('REVISAR CORTE', 0)} poligonos requieren revisar corte; varios provienen de subdivisiones de clusters grandes.",
        f"- {conteo.get('REVISAR FUSION', 0)} poligonos requieren evaluar fusion o continuidad de corredor.",
        f"- {conteo.get('REVISAR UNIVERSO', 0)} poligonos dependen demasiado de Places o tienen bajo respaldo F01+F02.",
        "- Recoleta, Villa Crespo y Caballito muestran saturacion previa relevante; no conviene resolver eso con mas API sin criterio editorial previo.",
        "- Costanera Norte y Caseros/Barracas siguen siendo macrozonas debiles: pueden servir como senal exploratoria, no como delimitacion defendible.",
        "",
        "## Conteo por categoria",
        "",
    ]
    for k in ["APROBAR", "APROBAR CON OBSERVACIONES", "REVISAR CORTE", "REVISAR FUSION", "REVISAR UNIVERSO", "DESCARTAR"]:
        resumen_md.append(f"- {k}: {conteo.get(k, 0)}")
    resumen_md += [
        "",
        "## Limites",
        "",
        "- Google Places es una senal auxiliar no oficial de oferta visible.",
        "- F01+F02 y Google Places no deben leerse como un padron de locales activos.",
        "- La clasificacion es una priorizacion editorial reproducible; requiere revision humana antes de version institucional.",
        "",
    ]

    handoff = [
        "# Handoff - revision poligonos completa v1",
        "",
        "## Poligonos aprobables",
        "",
        "Candidatos iniciales a conservar o revisar con observaciones:",
        "",
    ]
    for _, r in mejores.iterrows():
        handoff.append(f"- {r['microzona_id']} ({r['macrozona']}): {r['accion_recomendada']}; {r['cantidad_entidades']} puntos; {r['densidad_entidades_ha']} puntos/ha.")
    handoff += [
        "",
        "## Zonas con mas revision pendiente",
        "",
    ]
    for z, n in prob_zonas.items():
        handoff.append(f"- {z}: {int(n)} poligonos con accion de revision o descarte.")
    handoff += [
        "",
        "## Reglas para la proxima tanda",
        "",
        "- No usar mas API por defecto.",
        "- Redibujar manualmente antes de pedir mas datos.",
        "- Priorizar continuidad urbana reconocible sobre recortes geometricos.",
        "- Mantener separados F01+F02 y Google Places en todo entregable.",
        "- Para pasar a version institucional: revision humana de mapas, ajuste de nombres, validacion de limites con criterio urbano y anexo metodologico.",
        "",
        "## Archivos",
        "",
        f"- Tabla: `{OUT_TABLA}`",
        f"- Contact sheet: `{OUT_CONTACT}`",
        f"- Resumen JSON: `{OUT_RESUMEN_JSON}`",
    ]
    return "\n".join(resumen_md) + "\n", "\n".join(handoff) + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    pol = gpd.read_file(POLIGONOS).to_crs(CRS_METRICO)
    pts = gpd.read_file(PUNTOS).to_crs(CRS_METRICO)
    qa_integracion = json.loads(QA_INTEGRACION.read_text(encoding="utf-8"))
    qa_clusters = json.loads(QA_CLUSTERS.read_text(encoding="utf-8"))

    filas = []
    for _, r in pol.iterrows():
        cluster_id = r["cluster_id"]
        sub = pts[pts["cluster_final"] == cluster_id]
        f01 = int((sub["fuente"] == "F01+F02").sum())
        places = int((sub["fuente"] == "google_places").sum())
        n = int(len(sub))
        pct_places = round(100 * places / n, 1) if n else 0.0
        compact = round(shape_compactness(r.geometry), 3)
        accion, conf_alg, conf_ed, problemas, acciones = clasificar(r, f01, places, pct_places, compact)
        filas.append({
            "macrozona": r["macrozona_id"],
            "zona_piloto": r["zona_piloto"],
            "microzona_id": cluster_id,
            "cantidad_entidades": n,
            "cantidad_f01_f02": f01,
            "cantidad_places": places,
            "porcentaje_places": pct_places,
            "superficie_ha": round(float(r["area_ha"]), 2),
            "densidad_entidades_ha": round(float(r["densidad_ha"]), 2),
            "geometria_tipo": r.geometry.geom_type,
            "es_corredor": bool(r["es_corredor"]),
            "ronda_subdivision": int(r["ronda"]),
            "elongacion": round(float(r["elongacion"]), 2),
            "diametro_m": round(float(r["diametro_m"]), 1),
            "compactacion": compact,
            "lectura_urbana_orientativa": lectura_orientativa(r, f01, places, pct_places),
            "confianza_algoritmica": conf_alg,
            "confianza_editorial": conf_ed,
            "problema_detectado": problemas,
            "accion_recomendada": accion,
            "observaciones": acciones,
        })
    tabla = pd.DataFrame(filas).sort_values(["macrozona", "microzona_id"])
    tabla.to_csv(OUT_TABLA, index=False, encoding="utf-8")
    crear_contact_sheet()

    resumen = {
        "poligonos_revisados": int(len(tabla)),
        "conteo_por_categoria": tabla["accion_recomendada"].value_counts().to_dict(),
        "conteo_por_macrozona": tabla.groupby("macrozona").size().to_dict(),
        "conteo_revision_por_macrozona": (
            tabla[tabla["accion_recomendada"].str.startswith("REVISAR")]
            .groupby("macrozona").size().to_dict()
        ),
        "qa_integracion": {
            "universo_completo_total": qa_integracion.get("universo_completo_total"),
            "places_nuevos_incorporados": qa_integracion.get("places_nuevos_incorporados"),
        },
        "qa_clusters_zonas": qa_clusters.get("zonas", {}),
    }
    OUT_RESUMEN_JSON.write_text(json.dumps(resumen, ensure_ascii=False, indent=2),
                                encoding="utf-8")
    resumen_md, handoff_md = resumenes_markdown(tabla, resumen)
    OUT_RESUMEN_MD.write_text(resumen_md, encoding="utf-8")
    OUT_HANDOFF_MD.write_text(handoff_md, encoding="utf-8")
    print(f"[revision] tabla -> {OUT_TABLA}")
    print(f"[revision] resumen -> {OUT_RESUMEN_MD}")
    print(f"[revision] handoff -> {OUT_HANDOFF_MD}")
    print(f"[revision] contact sheet -> {OUT_CONTACT}")
    print(json.dumps(resumen["conteo_por_categoria"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
