from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs" / "polos_gastro"
DOCS = ROOT / "docs" / "polos_gastro"
FUENTES_DOCS = DOCS / "fuentes_externas"
FECHA_CORTE = "2026-06-29"


FUENTES_COLUMNS = [
    "fuente_id",
    "polo_id",
    "nombre_polo",
    "tipo_fuente",
    "nombre_fuente",
    "titulo_o_referencia",
    "url",
    "fecha_publicacion",
    "fecha_consulta",
    "evidencia_que_aporta",
    "delimitacion_mencionada",
    "locales_mencionados",
    "confiabilidad",
    "uso_recomendado",
    "limitaciones",
    "requiere_revision_manual",
]

UNIVERSO_COLUMNS = [
    "polo_id",
    "nombre_publico",
    "tipo_area",
    "grupo_informe",
    "estado_validacion",
    "decision_para_informe",
    "nivel_evidencia",
    "fuentes_principales",
    "urls_pendientes",
    "requiere_validacion_adicional",
    "motivo_decision",
    "riesgo_metodologico",
    "observaciones",
]

FAMILIAS_COLUMNS = [
    "familia_id",
    "familia_nombre",
    "polo_id",
    "nombre_publico",
    "grupo_informe",
    "estado_validacion",
    "fuentes_principales",
    "urls_pendientes",
    "observaciones",
]

DELIMITACION_COLUMNS = [
    "polo_id",
    "nombre_publico",
    "familia_territorial",
    "tipo_area",
    "grupo_informe",
    "delimitacion_textual",
    "barrios_asociados",
    "comunas_probables",
    "nivel_precision",
    "fuente_delimitacion",
    "url_fuente_delimitacion",
    "requiere_validacion_cartografica",
    "observaciones",
]

INITIAL_PENDING_IDS = [
    "PX007B",
    "PX009B",
    "PX010B",
    "PX013A",
    "PX013B",
    "PX016A",
    "PX016B",
    "PX017B",
    "PX018A",
    "PX018B",
    "PX019B",
    "PX020A",
    "PX020B",
    "PX021B",
    "PX023A",
    "PX023B",
    "PX024B",
    "PX025A",
    "PX025B",
    "PX026B",
]

RESOLUTIONS = {
    "PX007B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Con quien quieras - Pizzerías en Chacarita",
        "url": "https://turismo.buenosaires.gob.ar/es/ba-todos-bolsillos/con-quien-quieras",
        "evidencia_que_aporta": "Fuente oficial/turistica que identifica pizzerias reconocidas en Chacarita y ubica la referencia en Av. Corrientes y Federico Lacroze.",
        "delimitacion_mencionada": "Av. Corrientes y Federico Lacroze, Chacarita.",
        "locales_mencionados": "El Imperio de la Pizza; Santa Maria; La Mezzetta.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "Resuelve una referencia gastronomica puntual; no delimita todo Chacarita como polo institucional.",
        "requiere_revision_manual": "si",
    },
    "PX009B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Belgrano - Circuito 2",
        "url": "https://turismo.buenosaires.gob.ar/es/turismo-en-barrios/barrio-belgrano-circuito-2",
        "evidencia_que_aporta": "Fuente oficial/turistica que menciona el circuito de Bajo Belgrano, Barrio Chino y gastronomia.",
        "delimitacion_mencionada": "Bajo Belgrano / Barrio Chino dentro de Belgrano.",
        "locales_mencionados": "No lista locales como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "No convierte Bajo Belgrano en polo independiente ni da poligono.",
        "requiere_revision_manual": "si",
    },
    "PX010B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Circuito Sin Pausa - Gastronomia en Villa Urquiza",
        "url": "https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa",
        "evidencia_que_aporta": "Fuente oficial/turistica que vincula Donado-Holmberg con el limite de Villa Urquiza y Belgrano R.",
        "delimitacion_mencionada": "Echeverria, Holmberg, Av. Donado y Virrey del Pino.",
        "locales_mencionados": "Cafeterias, restaurantes y helados de autor; sin padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "Apoya un borde/circuito, no valida Belgrano R como polo gastronomico completo.",
        "requiere_revision_manual": "si",
    },
    "PX013A": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Costanera Norte",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/costanera-norte",
        "evidencia_que_aporta": "Fuente oficial/turistica que describe Costanera Norte como corredor ribereno y menciona oferta gastronomica tradicional y carritos.",
        "delimitacion_mencionada": "Corredor paralelo al Rio de la Plata, de Recoleta a Ciudad Universitaria, pasando por Palermo.",
        "locales_mencionados": "Restaurantes clasicos y carritos de la costanera; sin padron.",
        "confiabilidad": "media",
        "uso_recomendado": "contexto_turistico",
        "limitaciones": "Describe corredor y oferta, pero no cierra un poligono gastronomico.",
        "requiere_revision_manual": "si",
    },
    "PX013B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Costanera Norte",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/costanera-norte",
        "evidencia_que_aporta": "Fuente oficial/turistica que refuerza el caracter ribereno y recreativo de la Costanera Norte.",
        "delimitacion_mencionada": "Costanera Norte / ribera norte de CABA.",
        "locales_mencionados": "No lista locales como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "delimitar_zona",
        "limitaciones": "No debe usarse para afirmar limites gastronomicos finos.",
        "requiere_revision_manual": "si",
    },
    "PX016A": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Con quien quieras - Gastronomia en Av. Corrientes",
        "url": "https://turismo.buenosaires.gob.ar/es/ba-todos-bolsillos/con-quien-quieras",
        "evidencia_que_aporta": "Fuente oficial/turistica que caracteriza Av. Corrientes por teatros, cafes y pizza portena.",
        "delimitacion_mencionada": "Av. Corrientes y 9 de Julio, San Nicolas.",
        "locales_mencionados": "Las Cuartetas; Guerrin; La Americana; El Palacio de la Pizza.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "Valida identidad cultural-gastronomica puntual, no todo el corredor.",
        "requiere_revision_manual": "si",
    },
    "PX016B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "A night of theatre and pizza",
        "url": "https://turismo.buenosaires.gob.ar/en/atractivo/800pm-night-theatre-and-pizza",
        "evidencia_que_aporta": "Fuente turistica oficial que asocia Avenida Corrientes con teatro y pizza.",
        "delimitacion_mencionada": "Avenida Corrientes, sin tramo integral cerrado.",
        "locales_mencionados": "Pizzerias tradicionales; no se carga como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "No reemplaza una delimitacion cartografica del corredor.",
        "requiere_revision_manual": "si",
    },
    "PX017B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Abasto Shopping",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/abasto-shopping",
        "evidencia_que_aporta": "Fuente turistica oficial de hito comercial/turistico del Abasto.",
        "delimitacion_mencionada": "Abasto / Balvanera; hito puntual.",
        "locales_mencionados": "No se carga listado de locales.",
        "confiabilidad": "media",
        "uso_recomendado": "contexto_turistico",
        "limitaciones": "Centro comercial; no valida el barrio como polo cerrado.",
        "requiere_revision_manual": "si",
    },
    "PX018A": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "20 h - Avenida Boedo",
        "url": "https://turismo.buenosaires.gob.ar/es/atractivo/20-h-avenida-boedo",
        "evidencia_que_aporta": "Fuente oficial/turistica con referencias culturales y bares tradicionales sobre Avenida Boedo.",
        "delimitacion_mencionada": "Avenida Boedo; referencias a Av. San Juan y Av. Boedo y Av. Boedo 857.",
        "locales_mencionados": "Esquina Homero Manzi; Cafe Margot.",
        "confiabilidad": "media",
        "uso_recomendado": "contexto_historico",
        "limitaciones": "Apoya identidad cultural y bares puntuales, no valida corredor gastronomico.",
        "requiere_revision_manual": "si",
    },
    "PX018B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "La ruta del fileteado porteño",
        "url": "https://turismo.buenosaires.gob.ar/es/recorrido/la-ruta-del-fileteado-porte%C3%B1o",
        "evidencia_que_aporta": "Fuente oficial/turistica que incluye Avenida Boedo dentro de un recorrido cultural.",
        "delimitacion_mencionada": "Avenida Boedo como parada de recorrido cultural.",
        "locales_mencionados": "Referencias a bares tradicionales, sin padron.",
        "confiabilidad": "media",
        "uso_recomendado": "contexto_historico",
        "limitaciones": "Fuente cultural; no sostiene por si sola un polo gastronomico.",
        "requiere_revision_manual": "si",
    },
    "PX019B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Villa Devoto",
        "url": "https://turismo.buenosaires.gob.ar/es/turismo-en-barrios/barrio-villa-devoto",
        "evidencia_que_aporta": "Fuente oficial/turistica que describe Villa Devoto y menciona circuito gourmet.",
        "delimitacion_mencionada": "Villa Devoto.",
        "locales_mencionados": "Sin listado de locales como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "No delimita un corredor ni cuantifica oferta.",
        "requiere_revision_manual": "si",
    },
    "PX020A": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Circuito Sin Pausa - Gastronomia en Villa Urquiza",
        "url": "https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa",
        "evidencia_que_aporta": "Fuente oficial/turistica que identifica un circuito gastronomico sobre Donado-Holmberg.",
        "delimitacion_mencionada": "Echeverria, Holmberg, Av. Donado y Virrey del Pino.",
        "locales_mencionados": "Cafeterias, restaurantes y helados de autor; sin padron.",
        "confiabilidad": "alta",
        "uso_recomendado": "delimitar_zona",
        "limitaciones": "Requiere control de vigencia y no representa todo Villa Urquiza.",
        "requiere_revision_manual": "si",
    },
    "PX020B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Circuito Sin Pausa",
        "url": "https://turismo.buenosaires.gob.ar/es/article/circuito-sin-pausa",
        "evidencia_que_aporta": "Fuente complementaria ya identificada para Donado-Holmberg y Villa Urquiza.",
        "delimitacion_mencionada": "Donado-Holmberg / Villa Urquiza.",
        "locales_mencionados": "Menciones de oferta; no padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "No valida por si sola todo el barrio ni su densidad actual.",
        "requiere_revision_manual": "si",
    },
    "PX021B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Circuito Sin Pausa - Gastronomia en Villa Urquiza",
        "url": "https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa",
        "evidencia_que_aporta": "Fuente oficial/turistica que ubica oferta gastronomica en Villa Urquiza vinculada a Donado-Holmberg.",
        "delimitacion_mencionada": "Echeverria, Holmberg, Av. Donado y Virrey del Pino.",
        "locales_mencionados": "Cafeterias, restaurantes y helados de autor; sin padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "No cubre todo Villa Urquiza como barrio.",
        "requiere_revision_manual": "si",
    },
    "PX025B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Plan de desarrollo / gestion estrategica de la oferta turistica 2023",
        "url": "https://turismo.buenosaires.gob.ar/sites/turismo/files/plan-desarrollo-gestion-estrategica-oferta-turistica-2023.pdf",
        "evidencia_que_aporta": "Documento turistico estrategico que ubica La Paternal dentro de C15 y del producto/discusion de sabores y Distrito del Vino.",
        "delimitacion_mencionada": "C15: Chacarita, Villa Crespo, La Paternal, Villa Ortuzar, Agronomia y Parque Chas.",
        "locales_mencionados": "Referencias a Distrito del Vino; no padron.",
        "confiabilidad": "media",
        "uso_recomendado": "contexto_turistico",
        "limitaciones": "No valida un circuito gastronomico especifico de Paternal.",
        "requiere_revision_manual": "si",
    },
    "PX026B": {
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "La Nueva Andaluza",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/la-nueva-andaluza",
        "evidencia_que_aporta": "Fuente oficial/turistica de hito puntual con referencia a Avenida San Martin en Villa Pueyrredon.",
        "delimitacion_mencionada": "Avenida San Martin; hito puntual, no corredor.",
        "locales_mencionados": "La Nueva Andaluza.",
        "confiabilidad": "media",
        "uso_recomendado": "contexto_historico",
        "limitaciones": "No valida Villa Pueyrredon / Av. San Martin como polo o corredor.",
        "requiere_revision_manual": "si",
    },
}

UNRESOLVED = {
    "PX023A": "No se encontro URL verificable que respalde el tramo Federico Lacroze / Libertador a Cabildo como corredor gastronomico.",
    "PX023B": "No se encontro segunda fuente verificable para el tramo Federico Lacroze / Libertador a Cabildo.",
    "PX024B": "No se encontro URL verificable que respalde Parque Saavedra / Garcia del Rio como corredor gastronomico.",
    "PX025A": "No se encontro URL verificable especifica para un circuito gastronomico de Paternal; solo fuentes de contexto de Distrito del Vino/C15.",
}

FAMILIES = {
    "palermo_y_subpolos": {
        "nombre": "Palermo y subpolos",
        "polos": ["PG001A_PALERMO_SOHO", "PG001B_PALERMO_HOLLYWOOD", "PG001C_LAS_CANITAS"],
        "observacion": "Familia con subpolos internos de Palermo; no barrios independientes.",
    },
    "zona_costera_y_turistica": {
        "nombre": "Zona costera y turistica",
        "polos": ["PG003_PUERTO_MADERO", "PG009_COSTANERA_NORTE"],
        "observacion": "Agrupa ribera y centralidad turistica; requiere diferenciar docks, corredor ribereño e hitos.",
    },
    "sur_historico_y_tradicional": {
        "nombre": "Sur historico y tradicional",
        "polos": ["PG004_SAN_TELMO", "PG010_AVENIDA_CASEROS_BARRACAS", "PGF2_PARQUE_PATRICIOS"],
        "observacion": "Familia historica/tradicional con distinta fuerza documental por caso.",
    },
    "zona_central": {
        "nombre": "Zona central y Recoleta",
        "polos": [
            "PG007_RECOLETA",
            "PG011_MICROCENTRO_CENTRO_RENOVADO",
            "PGF2_MONTSERRAT",
            "PGF2_RETIRO",
            "PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY",
        ],
        "observacion": "Conviene agrupar centralidades turisticas y separar subejes no validados.",
    },
    "belgrano_y_norte": {
        "nombre": "Belgrano y norte",
        "polos": [
            "PG006A_BARRIO_CHINO",
            "PG006C_BELGRANO_R",
            "PG006B_BAJO_BELGRANO",
            "PG019_AVENIDA_FEDERICO_LACROZE_DESDE_LIBERTADOR_",
        ],
        "observacion": "Barrio Chino es subzona comercial-cultural; Belgrano R y Bajo Belgrano quedan prudentes.",
    },
    "oeste_y_barrios_con_oferta": {
        "nombre": "Oeste y barrios con oferta",
        "polos": [
            "PG008_CABALLITO",
            "PGF2_FLORES",
            "PGF2_FLORESTA",
            "PG015_DEVOTO",
            "PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN",
        ],
        "observacion": "Agrupa barrios e hitos de oferta; no implica equivalencia territorial.",
    },
    "corredores_emergentes_norte_oeste": {
        "nombre": "Corredores emergentes norte-oeste",
        "polos": [
            "PG005_CHACARITA",
            "PG002_VILLA_CRESPO",
            "PGF2_COLEGIALES",
            "PG017_VILLA_URQUIZA",
            "PG016_CORREDOR_DOHO_DONADO_HOLMBERG",
            "PG021_CIRCUITO_GASTRONOMICO_DE_PATERNAL",
            "PG020_PARQUE_SAAVEDRA_AVENIDA_GARCIA_DEL_RIO",
        ],
        "observacion": "Familia de candidatos y corredores; requiere validar tramos antes de mapear.",
    },
    "cultura_avenidas_y_noches": {
        "nombre": "Cultura, avenidas y noches",
        "polos": ["PG012_AVENIDA_CORRIENTES", "PG013_ABASTO", "PG014_AVENIDA_BOEDO"],
        "observacion": "Agrupa identidad cultural/nocturna; no se debe convertir automaticamente en poligonos gastronomicos.",
    },
}

PENDING_ORDER = ["url_pendiente", "requiere_revision_url"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def upsert_section(path: Path, marker: str, section: str) -> None:
    original = path.read_text(encoding="utf-8")
    start = f"<!-- {marker}_START -->"
    end = f"<!-- {marker}_END -->"
    block = f"{start}\n{section.rstrip()}\n{end}"
    if start in original and end in original:
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        updated = pattern.sub(block, original)
    else:
        updated = original.rstrip() + "\n\n" + block + "\n"
    write_text(path, updated)


def is_pending_url(url: str) -> bool:
    return not url or url in PENDING_ORDER or url.startswith("url_semilla_")


def join(items: list[str], fallback: str = "sin datos") -> str:
    clean = [item for item in items if item]
    return "; ".join(clean) if clean else fallback


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("\n", " ") for column in columns) + " |")
    return "\n".join(lines)


def update_sources(fuentes: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    resolved = []
    unresolved = []
    for row in fuentes:
        fuente_id = row["fuente_id"]
        if fuente_id in RESOLUTIONS:
            row.update(RESOLUTIONS[fuente_id])
            row["fecha_consulta"] = FECHA_CORTE
            resolved.append(
                {
                    "fuente_id": fuente_id,
                    "polo": row["nombre_polo"],
                    "url": row["url"],
                    "estado": "resuelta_con_fuente_parcial",
                    "nota": row["limitaciones"],
                }
            )
        elif fuente_id in UNRESOLVED:
            row["requiere_revision_manual"] = "si"
            row["limitaciones"] = UNRESOLVED[fuente_id]
            unresolved.append(
                {
                    "fuente_id": fuente_id,
                    "polo": row["nombre_polo"],
                    "motivo": UNRESOLVED[fuente_id],
                }
            )
    initial = [
        {"fuente_id": row["fuente_id"], "polo": row["nombre_polo"], "url_inicial": "url_pendiente"}
        for row in fuentes
        if row["fuente_id"] in INITIAL_PENDING_IDS
    ]
    return fuentes, resolved, unresolved


def source_summary(rows: list[dict[str, str]]) -> str:
    not_pending = [row for row in rows if not is_pending_url(row["url"])]
    prioritized = sorted(not_pending, key=lambda row: (row["confiabilidad"] != "alta", row["tipo_fuente"], row["fuente_id"]))
    return join([f"{row['titulo_o_referencia']} ({row['tipo_fuente']})" for row in prioritized[:4]], "sin fuente verificable")


def recompute_universe(universo: list[dict[str, str]], fuentes_by_polo: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    updated = []
    for row in universo:
        sources = fuentes_by_polo[row["polo_id"]]
        pending = [f"{source['fuente_id']}:url_pendiente" for source in sources if is_pending_url(source["url"])]
        row["fuentes_principales"] = source_summary(sources)
        row["urls_pendientes"] = join(pending, "sin_urls_pendientes")
        row["requiere_validacion_adicional"] = "si"
        updated.append(row)
    return updated


def family_lookup() -> dict[str, tuple[str, str, str]]:
    lookup = {}
    for family_id, data in FAMILIES.items():
        for polo_id in data["polos"]:
            lookup[polo_id] = (family_id, data["nombre"], data["observacion"])
    return lookup


def build_family_rows(universo: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = family_lookup()
    rows = []
    for row in universo:
        family_id, family_name, observation = lookup[row["polo_id"]]
        rows.append(
            {
                "familia_id": family_id,
                "familia_nombre": family_name,
                "polo_id": row["polo_id"],
                "nombre_publico": row["nombre_publico"],
                "grupo_informe": row["grupo_informe"],
                "estado_validacion": row["estado_validacion"],
                "fuentes_principales": row["fuentes_principales"],
                "urls_pendientes": row["urls_pendientes"],
                "observaciones": observation,
            }
        )
    return rows


DELIMITATIONS = {
    "PG001A_PALERMO_SOHO": {
        "texto": "Delimitado por las avenidas Scalabrini Ortiz, Cordoba, Juan B. Justo y Santa Fe.",
        "barrios": "Palermo",
        "comunas": "Comuna 14",
        "precision": "alta",
        "fuente": "Turismo Buenos Aires - Polos gastronomicos",
        "url": "https://turismo.buenosaires.gob.ar/es/article/polos-gastron%C3%B3micos",
        "obs": "Limites textuales de fuente oficial/turistica; no equivalen a poligono oficial.",
    },
    "PG001B_PALERMO_HOLLYWOOD": {
        "texto": "Delimitado por Av. Juan B. Justo, Dorrego, Av. Santa Fe y Av. Cordoba.",
        "barrios": "Palermo",
        "comunas": "Comuna 14",
        "precision": "alta",
        "fuente": "Turismo Buenos Aires - Polos gastronomicos",
        "url": "https://turismo.buenosaires.gob.ar/es/article/polos-gastron%C3%B3micos",
        "obs": "Limites textuales de fuente oficial/turistica; no equivalen a poligono oficial.",
    },
    "PG001C_LAS_CANITAS": {
        "texto": "Calle Baez y calles aledañas, en Palermo.",
        "barrios": "Palermo",
        "comunas": "Comuna 14",
        "precision": "media",
        "fuente": "Turismo Buenos Aires - Polos gastronomicos",
        "url": "https://turismo.buenosaires.gob.ar/es/article/polos-gastron%C3%B3micos",
        "obs": "Fuente menciona eje y alrededores, no limites cerrados.",
    },
    "PG002_VILLA_CRESPO": {
        "texto": "Barrio Villa Crespo; Mercat Villa Crespo como hito puntual.",
        "barrios": "Villa Crespo",
        "comunas": "Comuna 15",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires - Mercat Villa Crespo",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/mercat-villa-crespo",
        "obs": "Hito puntual; falta delimitar concentracion barrial.",
    },
    "PG003_PUERTO_MADERO": {
        "texto": "Antiguos docks del puerto; centro residencial y gastronomico asociado a Puerto Madero.",
        "barrios": "Puerto Madero",
        "comunas": "Comuna 1",
        "precision": "media",
        "fuente": "Turismo Buenos Aires - Polos gastronomicos",
        "url": "https://turismo.buenosaires.gob.ar/es/article/polos-gastron%C3%B3micos",
        "obs": "Zona clara, pero requiere poligono operativo futuro.",
    },
    "PG004_SAN_TELMO": {
        "texto": "Barrio San Telmo.",
        "barrios": "San Telmo",
        "comunas": "Comuna 1",
        "precision": "media",
        "fuente": "Turismo Buenos Aires - Polos gastronomicos",
        "url": "https://turismo.buenosaires.gob.ar/es/article/polos-gastron%C3%B3micos",
        "obs": "Barrio reconocido; faltan limites finos para subcircuitos.",
    },
    "PG005_CHACARITA": {
        "texto": "Barrio Chacarita; referencias gastronomicas en Av. Corrientes y Federico Lacroze.",
        "barrios": "Chacarita",
        "comunas": "Comuna 15",
        "precision": "media",
        "fuente": "Turismo Buenos Aires - Con quien quieras / Polo gastronomico Chacarita",
        "url": "https://turismo.buenosaires.gob.ar/es/ba-todos-bolsillos/con-quien-quieras",
        "obs": "Redaccion prudente: fuente de identidad/hitos, no limites oficiales.",
    },
    "PG006A_BARRIO_CHINO": {
        "texto": "Subzona de Belgrano vinculada a Barrio Chino y Bajo Belgrano.",
        "barrios": "Belgrano",
        "comunas": "Comuna 13",
        "precision": "media",
        "fuente": "Turismo Buenos Aires - Belgrano Circuito 2",
        "url": "https://turismo.buenosaires.gob.ar/es/turismo-en-barrios/barrio-belgrano-circuito-2",
        "obs": "Subzona comercial-cultural; no barrio independiente.",
    },
    "PG006B_BAJO_BELGRANO": {
        "texto": "Bajo Belgrano dentro de Belgrano Circuito 2.",
        "barrios": "Belgrano",
        "comunas": "Comuna 13",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires - Belgrano Circuito 2",
        "url": "https://turismo.buenosaires.gob.ar/es/turismo-en-barrios/barrio-belgrano-circuito-2",
        "obs": "No incluir como polo cerrado; solo referencia contextual.",
    },
    "PG006C_BELGRANO_R": {
        "texto": "Belgrano R como referencia contextual vinculada al borde Donado-Holmberg.",
        "barrios": "Belgrano",
        "comunas": "Comuna 13",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires - Circuito Sin Pausa",
        "url": "https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa",
        "obs": "No valida Belgrano R como polo gastronomico independiente.",
    },
    "PG007_RECOLETA": {
        "texto": "Barrio Recoleta.",
        "barrios": "Recoleta",
        "comunas": "Comuna 2",
        "precision": "media",
        "fuente": "Turismo Buenos Aires - Polos gastronomicos",
        "url": "https://turismo.buenosaires.gob.ar/es/article/polos-gastron%C3%B3micos",
        "obs": "Barrio reconocido, sin subdelimitacion operativa.",
    },
    "PG008_CABALLITO": {
        "texto": "Barrio Caballito; Patio de los Lecheros y Mercado del Progreso como hitos.",
        "barrios": "Caballito",
        "comunas": "Comuna 6",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires - Patio de los Lecheros / Mercado del Progreso",
        "url": "https://turismo.buenosaires.gob.ar/es/gastronomico/patio-de-los-lecheros",
        "obs": "Hitos puntuales; no poligono barrial.",
    },
    "PG009_COSTANERA_NORTE": {
        "texto": "Corredor paralelo al Rio de la Plata, de Recoleta a Ciudad Universitaria, pasando por Palermo.",
        "barrios": "Recoleta; Palermo; Nunez/Belgrano entorno Ciudad Universitaria",
        "comunas": "Comunas 2, 13 y 14 (aproximacion)",
        "precision": "media",
        "fuente": "Turismo Buenos Aires - Costanera Norte",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/costanera-norte",
        "obs": "Corredor ribereño amplio; no delimita oferta gastronomica fina.",
    },
    "PG010_AVENIDA_CASEROS_BARRACAS": {
        "texto": "Barracas / eje Caseros; delimitacion especifica pendiente.",
        "barrios": "Barracas",
        "comunas": "Comuna 4",
        "precision": "baja",
        "fuente": "Matriz Perplexity / La Nacion / BA Data",
        "url": "https://www.lanacion.com.ar/buenos-aires/casi-el-60-de-los-locales-gastronomicos-se-concentran-en-siete-barrios-portenos-nid2095107/",
        "obs": "Evidencia indirecta; anexo.",
    },
    "PG011_MICROCENTRO_CENTRO_RENOVADO": {
        "texto": "Zona central integrada por San Nicolas, Monserrat y Retiro como aproximacion narrativa.",
        "barrios": "San Nicolas; Monserrat; Retiro",
        "comunas": "Comuna 1",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires / La Nacion / Buenos Aires Data",
        "url": "https://turismo.buenosaires.gob.ar/es/article/gastronom%C3%ADa-en-buenos-aires",
        "obs": "No dibujar como poligono cerrado sin criterio adicional.",
    },
    "PG012_AVENIDA_CORRIENTES": {
        "texto": "Av. Corrientes y 9 de Julio, San Nicolas, como referencia de identidad teatro/pizza; tramo integral pendiente.",
        "barrios": "San Nicolas; Balvanera; Almagro (segun tramo futuro)",
        "comunas": "Comunas 1, 3 y 5 (aproximacion)",
        "precision": "media",
        "fuente": "Turismo Buenos Aires - Con quien quieras",
        "url": "https://turismo.buenosaires.gob.ar/es/ba-todos-bolsillos/con-quien-quieras",
        "obs": "Identidad cultural-gastronomica, no corredor completo.",
    },
    "PG013_ABASTO": {
        "texto": "Abasto / Balvanera; hito comercial y entorno cultural, sin polo delimitado.",
        "barrios": "Balvanera",
        "comunas": "Comuna 3",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires - Abasto Shopping",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/abasto-shopping",
        "obs": "Anexo; analizar con Av. Corrientes.",
    },
    "PG014_AVENIDA_BOEDO": {
        "texto": "Avenida Boedo con referencias a Av. San Juan y Av. Boedo y Av. Boedo 857.",
        "barrios": "Boedo",
        "comunas": "Comuna 5",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires - 20 h Avenida Boedo",
        "url": "https://turismo.buenosaires.gob.ar/es/atractivo/20-h-avenida-boedo",
        "obs": "Fuente cultural/historica; no alcanza para mapear polo gastronomico cerrado.",
    },
    "PG015_DEVOTO": {
        "texto": "Villa Devoto; zona barrial con circuito gourmet mencionado por fuente oficial/turistica.",
        "barrios": "Villa Devoto",
        "comunas": "Comuna 11",
        "precision": "media",
        "fuente": "Turismo Buenos Aires - Villa Devoto",
        "url": "https://turismo.buenosaires.gob.ar/es/turismo-en-barrios/barrio-villa-devoto",
        "obs": "No delimita corredor; candidato.",
    },
    "PG016_CORREDOR_DOHO_DONADO_HOLMBERG": {
        "texto": "Calles Echeverria, Holmberg, Av. Donado y Virrey del Pino; eje Donado-Holmberg.",
        "barrios": "Villa Urquiza; borde Belgrano R",
        "comunas": "Comunas 12 y 13 (borde aproximado)",
        "precision": "alta",
        "fuente": "Turismo Buenos Aires - Circuito Sin Pausa",
        "url": "https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa",
        "obs": "Preciso como eje/circuito, no como barrio completo.",
    },
    "PG017_VILLA_URQUIZA": {
        "texto": "Villa Urquiza con evidencia parcial asociada a Donado-Holmberg.",
        "barrios": "Villa Urquiza",
        "comunas": "Comuna 12",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires - Circuito Sin Pausa",
        "url": "https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa",
        "obs": "Evidencia del eje, no de todo el barrio.",
    },
    "PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY": {
        "texto": "Retiro; no hay delimitacion validada del tramo Esmeralda-Paraguay.",
        "barrios": "Retiro",
        "comunas": "Comuna 1",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires / La Nacion como contexto de Retiro",
        "url": "https://turismo.buenosaires.gob.ar/es/article/gastronom%C3%ADa-en-buenos-aires",
        "obs": "Anexo; no mapear como poligono cerrado.",
    },
    "PG019_AVENIDA_FEDERICO_LACROZE_DESDE_LIBERTADOR_": {
        "texto": "Sin delimitacion documental suficiente del tramo Federico Lacroze / Libertador a Cabildo.",
        "barrios": "Belgrano/Colegiales (aproximacion)",
        "comunas": "Comunas 13 y 15 (aproximacion)",
        "precision": "sin_delimitacion",
        "fuente": "Sin fuente verificable suficiente",
        "url": "url_pendiente",
        "obs": "No mapear como area cerrada.",
    },
    "PG020_PARQUE_SAAVEDRA_AVENIDA_GARCIA_DEL_RIO": {
        "texto": "Sin fuente suficiente para validar Garcia del Rio como corredor gastronomico.",
        "barrios": "Saavedra",
        "comunas": "Comuna 12",
        "precision": "sin_delimitacion",
        "fuente": "Sin fuente verificable suficiente",
        "url": "url_pendiente",
        "obs": "No mapear como area cerrada.",
    },
    "PG021_CIRCUITO_GASTRONOMICO_DE_PATERNAL": {
        "texto": "La Paternal dentro de C15 y contexto Distrito del Vino; no circuito gastronomico especifico.",
        "barrios": "La Paternal",
        "comunas": "Comuna 15",
        "precision": "baja",
        "fuente": "Plan de desarrollo / gestion estrategica de la oferta turistica 2023",
        "url": "https://turismo.buenosaires.gob.ar/sites/turismo/files/plan-desarrollo-gestion-estrategica-oferta-turistica-2023.pdf",
        "obs": "Contexto territorial, no polo/circuito validado.",
    },
    "PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN": {
        "texto": "Avenida San Martin con hito puntual La Nueva Andaluza; sin corredor validado.",
        "barrios": "Villa Pueyrredon",
        "comunas": "Comuna 12",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires - La Nueva Andaluza",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/la-nueva-andaluza",
        "obs": "No mapear como corredor cerrado.",
    },
    "PGF2_COLEGIALES": {
        "texto": "Barrio Colegiales; sin corredor gastronomico especifico.",
        "barrios": "Colegiales",
        "comunas": "Comuna 13",
        "precision": "baja",
        "fuente": "La Nacion / Buenos Aires Data",
        "url": "https://www.lanacion.com.ar/buenos-aires/casi-el-60-de-los-locales-gastronomicos-se-concentran-en-siete-barrios-portenos-nid2095107/",
        "obs": "Candidato agregado; requiere fuente especifica.",
    },
    "PGF2_MONTSERRAT": {
        "texto": "Barrio Monserrat como parte de zona central.",
        "barrios": "Monserrat",
        "comunas": "Comuna 1",
        "precision": "media",
        "fuente": "La Nacion / Buenos Aires Data",
        "url": "https://www.lanacion.com.ar/buenos-aires/casi-el-60-de-los-locales-gastronomicos-se-concentran-en-siete-barrios-portenos-nid2095107/",
        "obs": "Mapear dentro de familia zona central, no como polo aislado.",
    },
    "PGF2_RETIRO": {
        "texto": "Barrio Retiro como parte de zona central.",
        "barrios": "Retiro",
        "comunas": "Comuna 1",
        "precision": "media",
        "fuente": "Turismo Buenos Aires / La Nacion",
        "url": "https://turismo.buenosaires.gob.ar/es/article/gastronom%C3%ADa-en-buenos-aires",
        "obs": "Separar de Nuevo Bajo en Retiro.",
    },
    "PGF2_FLORES": {
        "texto": "Flores / barrio coreano como referencia puntual; no barrio completo.",
        "barrios": "Flores",
        "comunas": "Comuna 7",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires - Almuerzo coreano",
        "url": "https://turismo.buenosaires.gob.ar/es/atractivo/almuerzo-coreano",
        "obs": "Circuito cultural especifico, no polo barrial.",
    },
    "PGF2_FLORESTA": {
        "texto": "Barrio Floresta; sin corredor gastronomico especifico.",
        "barrios": "Floresta",
        "comunas": "Comuna 10",
        "precision": "baja",
        "fuente": "La Nacion / Buenos Aires Data",
        "url": "https://www.lanacion.com.ar/buenos-aires/casi-el-60-de-los-locales-gastronomicos-se-concentran-en-siete-barrios-portenos-nid2095107/",
        "obs": "Anexo exploratorio.",
    },
    "PGF2_PARQUE_PATRICIOS": {
        "texto": "Parque Patricios con hito Smart Plaza Patio; no barrio completo.",
        "barrios": "Parque Patricios",
        "comunas": "Comuna 4",
        "precision": "baja",
        "fuente": "Turismo Buenos Aires - Smart Plaza Patio Parque Patricios",
        "url": "https://turismo.buenosaires.gob.ar/es/gastronomico/smart-plaza-patio-parque-patricios",
        "obs": "Hito puntual; anexo.",
    },
}


def build_delimitacion(universo: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = family_lookup()
    rows = []
    for row in universo:
        polo_id = row["polo_id"]
        family_id = lookup[polo_id][0]
        delim = DELIMITATIONS[polo_id]
        rows.append(
            {
                "polo_id": polo_id,
                "nombre_publico": row["nombre_publico"],
                "familia_territorial": family_id,
                "tipo_area": row["tipo_area"],
                "grupo_informe": row["grupo_informe"],
                "delimitacion_textual": delim["texto"],
                "barrios_asociados": delim["barrios"],
                "comunas_probables": delim["comunas"],
                "nivel_precision": delim["precision"],
                "fuente_delimitacion": delim["fuente"],
                "url_fuente_delimitacion": delim["url"],
                "requiere_validacion_cartografica": "si",
                "observaciones": delim["obs"],
            }
        )
    return rows


def write_url_report(resolved: list[dict[str, str]], unresolved: list[dict[str, str]], fuentes: list[dict[str, str]], universo: list[dict[str, str]]) -> None:
    initial = [row for row in fuentes if row["fuente_id"] in INITIAL_PENDING_IDS]
    still_pending = [row for row in fuentes if row["fuente_id"] in INITIAL_PENDING_IDS and is_pending_url(row["url"])]
    universe_by_polo = {row["polo_id"]: row for row in universo}
    impact_rows = []
    for row in still_pending:
        urow = universe_by_polo.get(row["polo_id"], {})
        impact_rows.append(
            {
                "polo": urow.get("nombre_publico", row["nombre_polo"]),
                "grupo": urow.get("grupo_informe", ""),
                "impacto": "bloquea delimitacion fuerte o inclusion central" if urow.get("grupo_informe") != "no_incluir_por_ahora" else "refuerza decision de no incluir por ahora",
            }
        )

    lines = [
        "# Reporte de URLs pendientes - Fase 3A",
        "",
        f"Fecha de consulta: {FECHA_CORTE}.",
        "",
        "La revision se limito a fuentes abiertas y verificables, priorizando Turismo Buenos Aires, BA Data y fuentes periodisticas ya identificadas. No se uso scraping ni APIs privadas.",
        "",
        "## URLs pendientes al inicio",
        "",
        f"- Registros `url_pendiente` iniciales: {len(INITIAL_PENDING_IDS)}.",
        f"- Polos afectados al inicio: {len(set(row['polo_id'] for row in initial))}.",
        "",
        "## URLs resueltas",
        "",
        markdown_table(resolved, ["fuente_id", "polo", "url", "estado", "nota"]) if resolved else "Sin URLs resueltas.",
        "",
        "## URLs que siguen pendientes",
        "",
        markdown_table(unresolved, ["fuente_id", "polo", "motivo"]) if unresolved else "No quedaron URLs pendientes de la lista inicial.",
        "",
        "## Fuentes descartadas o no usadas",
        "",
        "- Resultados que solo mencionaban atractivos generales, buscadores o locales sueltos no se usaron para cerrar delimitaciones.",
        "- Fuentes con menciones de un hito puntual se cargaron como evidencia parcial, no como validacion de polo.",
        "- No se uso ningun resultado de plataformas privadas ni listados comerciales no institucionales.",
        "",
        "## Impacto sobre el universo del informe",
        "",
        "No se modifico la clasificacion del universo. Las URLs resueltas reducen incertidumbre documental, pero no elevan casos debiles a nucleo principal.",
        "",
        markdown_table(impact_rows, ["polo", "grupo", "impacto"]) if impact_rows else "Las URLs pendientes restantes no modifican el universo.",
    ]
    write_text(FUENTES_DOCS / "REPORTE_URLS_PENDIENTES_FASE3A.md", "\n".join(lines))


def write_delim_doc(delimitacion: list[dict[str, str]], family_rows: list[dict[str, str]]) -> None:
    counts = Counter(row["nivel_precision"] for row in delimitacion)
    by_precision = defaultdict(list)
    for row in delimitacion:
        by_precision[row["nivel_precision"]].append(row["nombre_publico"])

    lines = [
        "# Delimitacion textual preliminar - PolosGastro",
        "",
        f"Fecha de corte documental: {FECHA_CORTE}.",
        "",
        "## 1. Por que delimitacion textual antes de mapas",
        "",
        "La Fase 3A trabaja con texto porque todavia no hay poligonos ni criterios cartograficos cerrados. Antes de dibujar mapas conviene saber si cada caso corresponde a barrio, subpolo, avenida, corredor o zona central.",
        "",
        "La delimitación textual no equivale a polígono oficial.",
        "Las comunas probables no constituyen validación cartográfica.",
        "Las zonas sin fuente clara no deben mapearse como polígonos cerrados.",
        "Los mapas futuros deben diferenciar polos consolidados, zonas relevantes y candidatos.",
        "",
        "## 2. Diferencia entre tipos territoriales",
        "",
        "- Barrio: unidad reconocible de CABA; puede servir para agrupacion, pero no prueba concentracion gastronomica.",
        "- Subpolo: recorte dentro de un barrio, como Palermo Soho o Barrio Chino.",
        "- Avenida: eje lineal que requiere tramo inicial/final para mapearse.",
        "- Corredor: conjunto de calles o tramo con oferta; necesita fuente de delimitacion.",
        "- Zona central: familia territorial amplia que puede contener varios barrios y subejes.",
        "",
        "## 3. Familias territoriales propuestas",
        "",
        markdown_table(
            [
                {"familia_id": fid, "familia_nombre": data["nombre"], "polos": ", ".join(row["nombre_publico"] for row in family_rows if row["familia_id"] == fid)}
                for fid, data in FAMILIES.items()
            ],
            ["familia_id", "familia_nombre", "polos"],
        ),
        "",
        "## 4. Delimitaciones con mayor precision",
        "",
        f"- Alta: {', '.join(by_precision['alta']) if by_precision['alta'] else 'sin casos'}.",
        f"- Media: {', '.join(by_precision['media']) if by_precision['media'] else 'sin casos'}.",
        "",
        "## 5. Delimitaciones debiles o pendientes",
        "",
        f"- Baja: {', '.join(by_precision['baja']) if by_precision['baja'] else 'sin casos'}.",
        f"- Sin delimitacion: {', '.join(by_precision['sin_delimitacion']) if by_precision['sin_delimitacion'] else 'sin casos'}.",
        "",
        "## 6. Riesgos metodologicos",
        "",
        "- Usar comunas probables como si fueran validacion cartografica.",
        "- Dibujar poligonos cerrados para avenidas o corredores sin tramo documentado.",
        "- Sobregeneralizar barrios enteros desde un hito gastronomico puntual.",
        "- Fusionar casos solapados sin justificar escala.",
        "",
        "## 7. Que falta antes de dibujar mapas",
        "",
        "- Resolver o documentar URLs pendientes restantes.",
        "- Definir si el mapa conceptual usara familias, etiquetas, puntos o lineas antes que poligonos.",
        "- Separar nucleo principal, zonas relevantes y candidatos con simbolizacion distinta.",
        "- Revisar manualmente las delimitaciones de baja precision.",
        "",
        "## 8. Recomendacion para Fase 3B",
        "",
        "Preparar un mapa conceptual no final por familias territoriales, preferentemente con etiquetas y lineas/corredores preliminares. No avanzar a poligonos cerrados hasta tener una fuente territorial o un criterio documentado por cada caso.",
        "",
        "## Conteo por precision",
        "",
        markdown_table(
            [{"nivel_precision": key, "cantidad": str(counts.get(key, 0))} for key in ["alta", "media", "baja", "sin_delimitacion"]],
            ["nivel_precision", "cantidad"],
        ),
    ]
    write_text(DOCS / "DELIMITACION_TEXTUAL_PRELIMINAR_POLOS_GASTRO.md", "\n".join(lines))


def update_reading(universo: list[dict[str, str]], delimitacion: list[dict[str, str]], unresolved: list[dict[str, str]]) -> None:
    precision = Counter(row["nivel_precision"] for row in delimitacion)
    families = ", ".join(data["nombre"] for data in FAMILIES.values())
    no_closed = [row["nombre_publico"] for row in delimitacion if row["nivel_precision"] in {"baja", "sin_delimitacion"}]
    section = "\n".join(
        [
            "## Actualizacion Fase 3A - URLs y delimitacion textual",
            "",
            f"- URLs pendientes iniciales: {len(INITIAL_PENDING_IDS)}.",
            f"- URLs resueltas en Fase 3A: {len(RESOLUTIONS)}.",
            f"- URLs que siguen pendientes: {len(UNRESOLVED)}.",
            f"- Familias territoriales definidas: {families}.",
            f"- Delimitaciones `alta`: {precision.get('alta', 0)}; `media`: {precision.get('media', 0)}; `baja`: {precision.get('baja', 0)}; `sin_delimitacion`: {precision.get('sin_delimitacion', 0)}.",
            "",
            "Los casos con delimitacion textual razonable para un mapa conceptual son los de precision alta o media. Los casos de baja precision pueden figurar como etiquetas o familias, pero no deberian dibujarse como areas cerradas.",
            "",
            f"No deberian mapearse aun como area cerrada: {', '.join(no_closed)}.",
            "",
            "Recomendacion: la proxima fase deberia producir un mapa conceptual por familias, con simbologia diferente para nucleo principal, zonas relevantes y candidatos, evitando poligonos falsamente precisos.",
        ]
    )
    upsert_section(DOCS / "LECTURA_UNIVERSO_INFORME_POLOS_GASTRO.md", "FASE3A_URLS_DELIMITACION", section)


def update_skeleton(unresolved: list[dict[str, str]]) -> None:
    unresolved_ids = ", ".join(row["fuente_id"] for row in unresolved) if unresolved else "sin pendientes"
    section = "\n".join(
        [
            "## Pendientes para mapa conceptual",
            "",
            f"- URLs pendientes criticas o especificas: {unresolved_ids}.",
            "- Delimitaciones sin fuente: Federico Lacroze / Libertador a Cabildo; Parque Saavedra / Garcia del Rio.",
            "- Diferenciar barrios, subpolos, avenidas, corredores y zona central antes de diseñar simbolos.",
            "- Evitar mapas con poligonos falsamente precisos.",
            "- Evaluar un mapa por puntos, etiquetas o familias antes que poligonos cerrados.",
            "- Separar visualmente polos consolidados, zonas relevantes, emergentes/candidatos, anexo y no incluir por ahora.",
        ]
    )
    upsert_section(DOCS / "ESQUELETO_INFORME_POLOS_GASTRO.md", "FASE3A_PENDIENTES_MAPA_CONCEPTUAL", section)


def main() -> None:
    fuentes = read_csv(OUTPUTS / "fuentes_externas_polos_gastro.csv")
    universo = read_csv(OUTPUTS / "universo_informe_polos_gastro.csv")

    fuentes, resolved, unresolved = update_sources(fuentes)
    write_csv(OUTPUTS / "fuentes_externas_polos_gastro.csv", fuentes, FUENTES_COLUMNS)

    fuentes_by_polo: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in fuentes:
        fuentes_by_polo[row["polo_id"]].append(row)

    universo = recompute_universe(universo, fuentes_by_polo)
    write_csv(OUTPUTS / "universo_informe_polos_gastro.csv", universo, UNIVERSO_COLUMNS)

    family_rows = build_family_rows(universo)
    write_csv(OUTPUTS / "fuentes_por_familia_territorial.csv", family_rows, FAMILIAS_COLUMNS)

    delimitacion = build_delimitacion(universo)
    write_csv(OUTPUTS / "base_delimitacion_preliminar_polos_gastro.csv", delimitacion, DELIMITACION_COLUMNS)

    write_url_report(resolved, unresolved, fuentes, universo)
    write_delim_doc(delimitacion, family_rows)
    update_reading(universo, delimitacion, unresolved)
    update_skeleton(unresolved)


if __name__ == "__main__":
    main()
