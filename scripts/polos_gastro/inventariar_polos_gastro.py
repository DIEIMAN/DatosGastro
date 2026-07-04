# -*- coding: utf-8 -*-
"""
Fase 1 PolosGastro.

Lee el PDF semilla de polos gastronomicos, registra el archivo detectado y
genera una base candidata reproducible. La normalizacion es controlada dentro
del script porque el PDF no trae tablas estructuradas: los registros de polos y
locales se transcriben del PDF y se marcan como insumo semilla no validado.
"""

from __future__ import annotations

import csv
import re
import shutil
import subprocess
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs" / "polos_gastro"
SCRIPT_DIR = ROOT / "scripts" / "polos_gastro"
OUTPUT_DIR = ROOT / "outputs" / "polos_gastro"
GRAFICOS_DIR = OUTPUT_DIR / "graficos"
TABLAS_DIR = OUTPUT_DIR / "tablas"

SOURCE_LABEL = "PDF Polos gastronómicos (insumo semilla no validado)"
PROCESS_DATE = date.today().isoformat()


def _norm(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return ascii_value.lower()


def slug(value: str) -> str:
    value = _norm(value)
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value


@dataclass(frozen=True)
class PdfCandidate:
    path: Path
    score: int
    motivo: str


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def iter_project_pdfs() -> list[Path]:
    skip_parts = {".git", ".venv", ".pytest_cache", "tmp_pdf_preview"}
    pdfs: list[Path] = []
    for pdf in ROOT.rglob("*.pdf"):
        if any(part in skip_parts for part in pdf.parts):
            continue
        pdfs.append(pdf)
    return sorted(set(pdfs))


def score_pdf(path: Path) -> PdfCandidate | None:
    name = _norm(path.name)
    parent = _norm(path.parent.name)
    score = 0
    reasons: list[str] = []
    if "polo" in name:
        score += 5
        reasons.append("nombre contiene 'polo'")
    if "gastronom" in name:
        score += 4
        reasons.append("nombre contiene 'gastronom'")
    if parent == "polosgastro":
        score += 3
        reasons.append("ubicado en PolosGastro")
    if score == 0:
        return None
    return PdfCandidate(path=path, score=score, motivo="; ".join(reasons))


def find_source_pdf() -> tuple[Path, list[PdfCandidate]]:
    candidates = [candidate for pdf in iter_project_pdfs() if (candidate := score_pdf(pdf))]
    candidates.sort(key=lambda item: (-item.score, len(item.path.parts), relative(item.path)))
    if not candidates:
        raise FileNotFoundError("No se encontro un PDF candidato para PolosGastro.")
    return candidates[0].path, candidates


def run_tool(args: list[str]) -> str:
    completed = subprocess.run(
        args,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def get_page_count(pdf_path: Path, extracted_text: str) -> int:
    if shutil.which("pdfinfo"):
        info = run_tool(["pdfinfo", str(pdf_path)])
        for line in info.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())
    if extracted_text:
        return extracted_text.count("\f") + 1
    return 0


def extract_pdf_text(pdf_path: Path) -> str:
    if not shutil.which("pdftotext"):
        return ""
    return run_tool(["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), "-"])


def polo(
    index: int,
    nombre_polo: str,
    tipo_area: str,
    barrio_o_zona_principal: str,
    subzonas: str,
    comuna_probable: str,
    estado_candidato: str,
    nivel_consolidacion: str,
    descripcion_breve: str,
    pagina_fuente: str,
    observaciones: str,
) -> dict[str, str]:
    return {
        "polo_id": f"PG{index:03d}_{slug(nombre_polo)[:42].upper()}",
        "nombre_polo": nombre_polo,
        "nombre_normalizado": slug(nombre_polo),
        "tipo_area": tipo_area,
        "barrio_o_zona_principal": barrio_o_zona_principal,
        "subzonas": subzonas,
        "comuna_probable": comuna_probable,
        "estado_candidato": estado_candidato,
        "nivel_consolidacion": nivel_consolidacion,
        "descripcion_breve": descripcion_breve,
        "fuente_inicial": SOURCE_LABEL,
        "pagina_fuente": pagina_fuente,
        "requiere_validacion": "sí",
        "observaciones": observaciones,
    }


POLOS_CANDIDATOS = [
    polo(
        1,
        "Palermo (Soho, Hollywood y Las Cañitas)",
        "barrio",
        "Palermo",
        "Soho; Hollywood; Las Cañitas",
        "Comuna 14 (probable, inferida por barrio; no validada)",
        "normalizado",
        "consolidado",
        "Polo amplio con subzonas internas y listado de locales destacados en el PDF.",
        "1; 2",
        "La delimitación entre Soho, Hollywood y Las Cañitas requiere validación territorial.",
    ),
    polo(
        2,
        "Villa Crespo",
        "barrio",
        "Villa Crespo",
        "",
        "Comuna 15 (probable, inferida por barrio; no validada)",
        "normalizado",
        "consolidado",
        "Barrio mencionado con sección propia y locales destacados.",
        "1; 3",
        "Algunos locales pueden ubicarse en zona límite con Palermo/Chacarita; validar.",
    ),
    polo(
        3,
        "Puerto Madero",
        "barrio",
        "Puerto Madero",
        "",
        "Comuna 1 (probable, inferida por barrio; no validada)",
        "normalizado",
        "consolidado",
        "Barrio mencionado con sección propia y locales destacados.",
        "1; 3",
        "No se valida vigencia ni delimitación por diques.",
    ),
    polo(
        4,
        "San Telmo",
        "barrio",
        "San Telmo",
        "",
        "Comuna 1 (probable, inferida por barrio; no validada)",
        "normalizado",
        "consolidado",
        "Barrio mencionado con sección propia y locales destacados.",
        "1; 4",
        "El Mercado de San Telmo aparece como mención colectiva; requiere tratamiento propio.",
    ),
    polo(
        5,
        "Chacarita",
        "barrio",
        "Chacarita",
        "",
        "Comuna 15 (probable, inferida por barrio; no validada)",
        "normalizado",
        "relevante",
        "Barrio mencionado con sección propia y locales destacados.",
        "1; 4",
        "Puede solaparse con Villa Crespo/Colegiales en algunas menciones; validar límites.",
    ),
    polo(
        6,
        "Belgrano (Barrio Chino + Bajo Belgrano + Belgrano R)",
        "barrio",
        "Belgrano",
        "Barrio Chino; Bajo Belgrano; Belgrano R",
        "Comuna 13 (probable, inferida por barrio; no validada)",
        "ambiguo",
        "consolidado",
        "Belgrano aparece como polo con subzonas; el detalle del PDF lista Barrio Chino y Bajo Belgrano.",
        "1; 5",
        "Belgrano R aparece en el listado inicial, pero no en la sección detallada de locales.",
    ),
    polo(
        7,
        "Recoleta",
        "barrio",
        "Recoleta",
        "",
        "Comuna 2 (probable, inferida por barrio; no validada)",
        "normalizado",
        "consolidado",
        "Barrio mencionado con sección propia y locales destacados.",
        "1; 5-6",
        "La sección de locales continúa entre páginas; validar alcance territorial.",
    ),
    polo(
        8,
        "Caballito",
        "barrio",
        "Caballito",
        "",
        "Comuna 6 (probable, inferida por barrio; no validada)",
        "normalizado",
        "relevante",
        "Barrio mencionado con sección propia y locales destacados.",
        "1; 6",
        "Requiere validación para distinguir polo barrial de puntos aislados.",
    ),
    polo(
        9,
        "Costanera Norte",
        "zona_costera",
        "Costanera Norte",
        "",
        "Requiere validación territorial",
        "requiere_validacion",
        "relevante",
        "Zona costera mencionada con sección propia y locales destacados.",
        "1; 6",
        "No se infiere comuna porque el corredor costero puede atravesar más de una referencia territorial.",
    ),
    polo(
        10,
        "Avenida Caseros (Barracas)",
        "avenida",
        "Barracas",
        "Avenida Caseros",
        "Comuna 4 (probable, inferida por barrio; no validada)",
        "normalizado",
        "relevante",
        "Corredor de avenida asociado a Barracas con sección propia y locales destacados.",
        "1; 7",
        "Requiere delimitar tramo exacto y relación con Parque Patricios/San Telmo.",
    ),
    polo(
        11,
        "Microcentro / Centro Renovado",
        "zona_central",
        "Microcentro / Centro",
        "",
        "Comuna 1 (probable; no validada)",
        "normalizado",
        "relevante",
        "Zona central mencionada con sección propia y locales destacados.",
        "1; 7",
        "El PDF alterna 'Microcentro y centro' y 'Microcentro / Centro Renovado'.",
    ),
    polo(
        12,
        "Avenida Corrientes",
        "avenida",
        "Avenida Corrientes",
        "",
        "Requiere validación territorial",
        "ambiguo",
        "requiere_revision",
        "Avenida mencionada como elemento separado en el listado inicial.",
        "1",
        "El detalle posterior agrupa Abasto - Av. Corrientes; no se fusiona sin validación.",
    ),
    polo(
        13,
        "Abasto",
        "subpolo",
        "Abasto",
        "",
        "Comuna 3 (probable, inferida por zona Balvanera; no validada)",
        "ambiguo",
        "requiere_revision",
        "Zona mencionada como elemento separado en el listado inicial.",
        "1",
        "El detalle posterior agrupa Abasto - Av. Corrientes; no se fusiona sin validación.",
    ),
    polo(
        14,
        "Avenida Boedo",
        "avenida",
        "Boedo",
        "Avenida Boedo",
        "Comuna 5 (probable, inferida por barrio; no validada)",
        "base_pdf",
        "candidato",
        "Avenida/corredor mencionado en el listado inicial, sin sección de locales destacados.",
        "1",
        "Requiere validar tramo, centralidad gastronómica y fuentes complementarias.",
    ),
    polo(
        15,
        "Devoto",
        "barrio",
        "Villa Devoto",
        "",
        "Comuna 11 (probable, inferida por barrio; no validada)",
        "base_pdf",
        "incipiente",
        "Barrio mencionado en una línea que usa la palabra 'Incipientes'.",
        "1",
        "El PDF no aporta sección de locales; clasificación incipiente queda como lectura del texto fuente.",
    ),
    polo(
        16,
        "Corredor DoHo / Donado-Holmberg",
        "corredor",
        "Donado-Holmberg",
        "DoHo",
        "Requiere validación territorial",
        "base_pdf",
        "incipiente",
        "Corredor mencionado por nombre específico, sin sección de locales destacados.",
        "1",
        "Debe validarse si se considera corredor urbano, subpolo o denominación comercial.",
    ),
    polo(
        17,
        "Villa Urquiza",
        "barrio",
        "Villa Urquiza",
        "",
        "Comuna 12 (probable, inferida por barrio; no validada)",
        "base_pdf",
        "candidato",
        "Barrio mencionado en el listado inicial, sin sección de locales destacados.",
        "1",
        "Requiere fuentes complementarias para delimitar concentración gastronómica.",
    ),
    polo(
        18,
        "Nuevo Bajo en Retiro (Esmeralda y Paraguay)",
        "zona_central",
        "Retiro",
        "Alrededores de Esmeralda y Paraguay",
        "Comuna 1 (probable, inferida por barrio; no validada)",
        "base_pdf",
        "incipiente",
        "Zona emergente definida por entorno de esquina, sin sección de locales destacados.",
        "1",
        "No hay polígono ni tramo; requiere validación territorial y documental.",
    ),
    polo(
        19,
        "Avenida Federico Lacroze desde Libertador hasta Cabildo",
        "avenida",
        "Avenida Federico Lacroze",
        "Desde Libertador hasta Cabildo",
        "Requiere validación territorial",
        "base_pdf",
        "candidato",
        "Tramo de avenida mencionado en el listado inicial, sin locales destacados.",
        "1",
        "El tramo propuesto debe verificarse con cartografía y fuentes territoriales.",
    ),
    polo(
        20,
        "Parque Saavedra / Avenida García del Río",
        "subpolo",
        "Saavedra",
        "Parque Saavedra; Avenida García del Río",
        "Comuna 12 (probable, inferida por barrio; no validada)",
        "base_pdf",
        "candidato",
        "Zona barrial/parque y avenida mencionadas como circuito potencial.",
        "1",
        "Requiere diferenciar entorno de parque, avenida y oferta gastronómica efectiva.",
    ),
    polo(
        21,
        "Circuito gastronómico de Paternal",
        "barrio",
        "La Paternal",
        "Circuito gastronómico",
        "Comuna 15 (probable, inferida por barrio; no validada)",
        "base_pdf",
        "candidato",
        "Circuito mencionado en el listado inicial, sin sección de locales destacados.",
        "1",
        "La noción de circuito requiere delimitación y fuente complementaria.",
    ),
    polo(
        22,
        "Villa Pueyrredón / Avenida San Martín",
        "barrio",
        "Villa Pueyrredón",
        "Avenida San Martín",
        "Comuna 12 (probable, inferida por barrio; no validada)",
        "base_pdf",
        "candidato",
        "Barrio/corredor mencionado en el listado inicial, sin sección de locales destacados.",
        "1",
        "Requiere delimitar el tramo de Avenida San Martín y validar concentración.",
    ),
    polo(
        23,
        "Abasto - Avenida Corrientes",
        "corredor",
        "Abasto / Avenida Corrientes",
        "Abasto; Avenida Corrientes",
        "Requiere validación territorial",
        "ambiguo",
        "relevante",
        "Agrupación que aparece en la sección de locales destacados del PDF.",
        "7-8",
        "Se conserva como fila ambigua para alojar locales mencionados sin fusionar las filas separadas de Abasto y Avenida Corrientes.",
    ),
]


def local(
    polo_id: str,
    nombre_polo: str,
    nombre_local: str,
    subzona: str,
    pagina_fuente: str,
    observaciones: str = "No se valida vigencia, dirección ni condición de operación.",
) -> dict[str, str]:
    return {
        "polo_id": polo_id,
        "nombre_polo": nombre_polo,
        "nombre_local": nombre_local,
        "subzona": subzona,
        "tipo_mencion": "local destacado mencionado en PDF",
        "fuente_inicial": SOURCE_LABEL,
        "pagina_fuente": pagina_fuente,
        "requiere_validacion": "sí",
        "observaciones": observaciones,
    }


def build_locales() -> list[dict[str, str]]:
    by_name = {row["nombre_polo"]: row["polo_id"] for row in POLOS_CANDIDATOS}
    data: list[dict[str, str]] = []

    def add(nombre_polo: str, names: list[str], subzona: str, pagina: str) -> None:
        for name in names:
            data.append(local(by_name[nombre_polo], nombre_polo, name, subzona, pagina))

    add(
        "Palermo (Soho, Hollywood y Las Cañitas)",
        [
            "Don Julio",
            "La Cabrera",
            "Niño Gordo",
            "Gran Dabbang",
            "Mishiguene",
            "Osaka",
            "La Mar",
            "Aldo’s (Palermo)",
            "Cosi Mi Piace",
            "Oporto",
            "Las Pizarras Bistro",
            "Pa’ Pastar",
            "Café Registrado",
            "Francisca del Fuego (Distrito Arcos)",
        ],
        "Palermo",
        "2",
    )
    add(
        "Palermo (Soho, Hollywood y Las Cañitas)",
        ["Campo Bravo", "Novecento", "Morelia", "Kansas", "SushiClub"],
        "Las Cañitas",
        "2",
    )
    add(
        "Villa Crespo",
        [
            "878 Bar",
            "La Fuerza",
            "Julia",
            "Apu Nudo",
            "La Crespo",
            "Sarkis",
            "Malcriada",
            "Picarón",
            "Niño Gordo (zona límite)",
        ],
        "Villa Crespo",
        "3",
    )
    add(
        "Puerto Madero",
        [
            "Cabaña Las Lilas",
            "Sottovoce",
            "Chila",
            "Happening",
            "El Mercado (Faena)",
            "Patagonia Sur",
            "La Parolaccia Casa Tua",
            "Le Grill",
            "Red Resto & Lounge",
        ],
        "Puerto Madero",
        "3",
    )
    add(
        "San Telmo",
        [
            "El Preferido de San Telmo",
            "Café San Juan",
            "Hierbabuena",
            "La Brigada",
            "El Hornero",
            "Napoles",
            "Pulpería Quilapán",
            "Mercado de San Telmo (puestos varios)",
        ],
        "San Telmo",
        "4",
    )
    add(
        "Chacarita",
        [
            "Anafe",
            "Bar Chacabuco",
            "La Fuerza (sucursal Chacarita)",
            "Cantina Urondo",
            "Bar Roma",
            "Niño Gordo Burger House",
            "La Alacena Trattoria",
        ],
        "Chacarita",
        "4",
    )
    add(
        "Belgrano (Barrio Chino + Bajo Belgrano + Belgrano R)",
        ["Hong Kong Style", "China Rose", "Ichisou", "Ramen Neko", "Ichiban", "BAO Kitchen"],
        "Barrio Chino",
        "5",
    )
    add(
        "Belgrano (Barrio Chino + Bajo Belgrano + Belgrano R)",
        ["Tori Tori", "Alo’s Café", "La Mar (referencia de la zona)", "Casa China", "Anafe (original)"],
        "Bajo Belgrano",
        "5",
    )
    add(
        "Recoleta",
        [
            "La Pecora Nera",
            "La Biela",
            "Fervor",
            "El Sanjuanino",
            "Sottovoce Recoleta",
            "Piegari",
            "Roux",
            "Aramburu",
        ],
        "Recoleta",
        "5-6",
    )
    add(
        "Caballito",
        ["Patio de los Lecheros", "La Vaca Atada", "La Casona del Nonno", "Tierra de Nadie", "Café de la Plaza"],
        "Caballito",
        "6",
    )
    add(
        "Costanera Norte",
        ["Rodizio", "Gardiner", "Tequila (bar)", "Puerto Cristal (sobre la zona)", "El Muelle", "Lo de Jesús (sucursal Costanera)"],
        "Costanera Norte",
        "6",
    )
    add(
        "Avenida Caseros (Barracas)",
        ["Hierbabuena (segunda sede)", "Napoles Caseros", "Caseros 3039", "La Popular", "Café Registrado (sucursal)"],
        "Avenida Caseros / Barracas",
        "7",
    )
    add(
        "Microcentro / Centro Renovado",
        ["Tanta", "Los Galgos", "La Puerto Rico", "Santos Manjares", "La Continental (histórica)", "La Embajada", "El Foro"],
        "Microcentro / Centro",
        "7",
    )
    add(
        "Abasto - Avenida Corrientes",
        ["Güerrín", "Las Cuartetas", "El Palacio de la Pizza", "Pertutti", "La Reina Kunti", "Moulin Bleu"],
        "Abasto - Avenida Corrientes",
        "7-8",
    )

    for index, row in enumerate(data, start=1):
        row["local_id"] = f"LG{index:03d}_{slug(row['nombre_local'])[:42].upper()}"

    ordered_fields = [
        "local_id",
        "polo_id",
        "nombre_polo",
        "nombre_local",
        "subzona",
        "tipo_mencion",
        "fuente_inicial",
        "pagina_fuente",
        "requiere_validacion",
        "observaciones",
    ]
    return [{field: row[field] for field in ordered_fields} for row in data]


AMBIGUEDADES = [
    "Avenida Corrientes y Abasto aparecen separados en el listado inicial, pero la sección de locales los agrupa como Abasto - Av. Corrientes.",
    "Belgrano R aparece en el listado inicial, aunque la sección detallada solo desarrolla Barrio Chino y Bajo Belgrano.",
    "Palermo se presenta como polo amplio y Las Cañitas aparece como subpolo interno.",
    "La línea 'Incipientes Devoto' sugiere condición emergente, pero no define alcance ni evidencia complementaria.",
    "Varios casos son corredores o avenidas sin polígono: DoHo, Federico Lacroze, Avenida Boedo, Avenida Caseros y Avenida San Martín.",
    "Nuevo Bajo en Retiro se define por el entorno Esmeralda-Paraguay, no por un límite territorial formal.",
    "Costanera Norte no permite inferir comuna única sin una delimitación geográfica previa.",
]


def ensure_dirs() -> None:
    for directory in [DOCS_DIR, SCRIPT_DIR, OUTPUT_DIR, GRAFICOS_DIR, TABLAS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"No hay filas para escribir en {path}.")
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_summary_rows(polos: list[dict[str, str]], locales: list[dict[str, str]]) -> list[dict[str, str]]:
    tipo_counts = Counter(row["tipo_area"] for row in polos)
    nivel_counts = Counter(row["nivel_consolidacion"] for row in polos)
    polos_con_locales = {row["polo_id"] for row in locales}

    rows = [
        {
            "indicador": "cantidad_polos_candidatos",
            "categoria": "total",
            "valor": str(len(polos)),
            "fuente": SOURCE_LABEL,
            "observaciones": "Base candidata; todos los registros requieren validación.",
        },
        {
            "indicador": "cantidad_polos_con_locales_destacados",
            "categoria": "total",
            "valor": str(len(polos_con_locales)),
            "fuente": SOURCE_LABEL,
            "observaciones": "Locales destacados mencionados en el PDF, no padrón oficial.",
        },
        {
            "indicador": "cantidad_polos_requieren_validacion",
            "categoria": "total",
            "valor": str(sum(1 for row in polos if row["requiere_validacion"] == "sí")),
            "fuente": SOURCE_LABEL,
            "observaciones": "Incluye comunas probables y delimitaciones no validadas.",
        },
        {
            "indicador": "cantidad_locales_destacados_seed",
            "categoria": "total",
            "valor": str(len(locales)),
            "fuente": SOURCE_LABEL,
            "observaciones": "Menciones cualitativas; no se valida vigencia, dirección ni apertura.",
        },
    ]

    for tipo, count in sorted(tipo_counts.items()):
        rows.append(
            {
                "indicador": "cantidad_por_tipo_area",
                "categoria": tipo,
                "valor": str(count),
                "fuente": SOURCE_LABEL,
                "observaciones": "Clasificación normalizada por lectura del PDF; requiere validación.",
            }
        )
    for nivel, count in sorted(nivel_counts.items()):
        rows.append(
            {
                "indicador": "cantidad_por_nivel_consolidacion",
                "categoria": nivel,
                "valor": str(count),
                "fuente": SOURCE_LABEL,
                "observaciones": "Clasificación orientativa para Fase 1.",
            }
        )
    return rows


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    def clean(value: str) -> str:
        return value.replace("\n", " ").replace("|", "/")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(clean(str(value)) for value in row) + " |")
    return "\n".join(lines)


def grouped_locales(locales: list[dict[str, str]]) -> list[list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    pages: dict[str, set[str]] = defaultdict(set)
    for row in locales:
        grouped[row["nombre_polo"]].append(row["nombre_local"])
        pages[row["nombre_polo"]].add(row["pagina_fuente"])
    return [
        [polo_name, "; ".join(names), "; ".join(sorted(pages[polo_name]))]
        for polo_name, names in grouped.items()
    ]


def write_inventory(
    pdf_path: Path,
    candidates: list[PdfCandidate],
    page_count: int,
    polos: list[dict[str, str]],
    locales: list[dict[str, str]],
) -> None:
    candidate_rows = [
        [relative(item.path), str(item.score), item.motivo, "usado" if item.path == pdf_path else "no usado"]
        for item in candidates
    ]
    polo_rows = [
        [
            row["polo_id"],
            row["nombre_polo"],
            row["tipo_area"],
            row["nivel_consolidacion"],
            row["estado_candidato"],
            row["pagina_fuente"],
        ]
        for row in polos
    ]

    content = f"""# Inventario inicial PolosGastro

## Advertencia metodológica

Este inventario corresponde a una Fase 1. El PDF se trata como insumo semilla no validado, no como fuente oficial ni como verdad cerrada. La base resultante es candidata y requiere validación con fuentes complementarias antes de usarla como insumo de gestión, mapa o informe institucional.

## Archivo fuente detectado

- Archivo usado: `{relative(pdf_path)}`
- Cantidad de páginas: {page_count}
- Fecha de procesamiento local: {PROCESS_DATE}
- Extracción: lectura de texto con `pdftotext` y normalización controlada en `scripts/polos_gastro/inventariar_polos_gastro.py`.
- Copia de trabajo: no se realizó. El PDF original no fue movido ni modificado.

## PDFs considerados

{md_table(["archivo", "score", "motivo", "uso"], candidate_rows)}

## Polos detectados

{md_table(["polo_id", "polo", "tipo_area", "nivel", "estado", "página"], polo_rows)}

## Locales destacados detectados

El listado de locales destacados requiere validación. No se asume que los locales sigan abiertos, no se asume dirección y no se los trata como padrón oficial.

{md_table(["polo/sección", "locales mencionados", "página"], grouped_locales(locales))}

## Ambigüedades iniciales

{chr(10).join(f"- {item}" for item in AMBIGUEDADES)}

## Próximos pasos sugeridos

- Validar si el PDF tiene origen oficial, interno o documental y asignar una ficha de fuente.
- Contrastar los polos con barrios, comunas y cartografía oficial antes de delimitar polígonos.
- Separar polos consolidados, corredores, avenidas, subpolos y zonas turísticas con criterios explícitos.
- Validar locales destacados con fuentes complementarias antes de usarlos como evidencia territorial.
- Definir si en una fase posterior corresponde conectar esta base con habilitaciones, oferta registrada u otras capas de DataGastro, sin tocar el pipeline general hasta aprobación explícita.
"""
    (DOCS_DIR / "INVENTARIO_INICIAL_POLOS_GASTRO.md").write_text(content, encoding="utf-8")


def write_diagnostic(polos: list[dict[str, str]], locales: list[dict[str, str]]) -> None:
    detailed_polos = sorted({row["nombre_polo"] for row in locales})
    candidate_only = [row["nombre_polo"] for row in polos if row["nombre_polo"] not in detailed_polos]

    content = f"""# Diagnóstico inicial PolosGastro

## Qué contiene el PDF

El PDF contiene un listado inicial de zonas, barrios, avenidas, corredores y subpolos gastronómicos de CABA. También incluye secciones de locales destacados para algunos polos. En esta Fase 1 se extrajeron {len(polos)} polos o agrupaciones candidatas y {len(locales)} menciones de locales destacados.

## Qué tipo de fuente es

Por ahora debe tratarse como una fuente documental semilla. No se verificó origen oficial, fecha de elaboración, metodología, universo ni criterio de selección de locales. Por lo tanto:

- Base candidata, no padrón oficial.
- El listado de locales destacados requiere validación.
- La existencia de un local destacado no prueba por sí sola la delimitación de un polo.
- La delimitación territorial de cada polo debe validarse con fuentes complementarias.

## Qué permite hacer

- Construir un primer inventario de zonas candidatas.
- Identificar casos que el documento presenta con mayor desarrollo interno.
- Separar tipos de área: barrio, corredor, avenida, subpolo, zona costera y zona central.
- Preparar una agenda de validación territorial y documental.

## Qué NO permite afirmar

- No permite afirmar que los polos sean oficiales.
- No permite afirmar que los locales mencionados sigan abiertos o funcionen actualmente.
- No permite afirmar direcciones, coordenadas ni comunas definitivas.
- No permite medir densidad, volumen de oferta ni actividad económica.
- No permite integrar la fuente al pipeline general sin ficha, contrato y aprobación.

## Polos con mayor evidencia interna en el PDF

Estos casos tienen sección propia o listado de locales destacados dentro del PDF:

{chr(10).join(f"- {name}" for name in detailed_polos)}

## Candidatos, corredores o zonas sin detalle de locales

Estos casos aparecen en el listado inicial, pero no tienen sección de locales destacados en el PDF:

{chr(10).join(f"- {name}" for name in candidate_only)}

## Diferencias conceptuales para normalización

| Tipo | Criterio de uso en Fase 1 | Riesgo si se fuerza |
| --- | --- | --- |
| Barrio | Unidad territorial reconocible por nombre barrial. | Confundir barrio completo con concentración gastronómica real. |
| Corredor | Eje o circuito que conecta tramos o zonas. | Usarlo como polígono sin límites definidos. |
| Avenida | Tramo lineal asociado a oferta gastronómica. | No definir altura inicial/final o incluir zonas heterogéneas. |
| Subpolo | Zona menor dentro de un barrio o polo amplio. | Duplicar conteos con el polo principal. |
| Zona turística/gastronómica | Área de referencia urbana o turística. | Tomarla como delimitación administrativa oficial. |

## Ambigüedades detectadas

{chr(10).join(f"- {item}" for item in AMBIGUEDADES)}

## Recomendación para próximas fases

La próxima fase debería validar la naturaleza del PDF, construir una ficha de fuente y contrastar cada polo con cartografía oficial, notas institucionales y capas públicas ya existentes. Recién después conviene definir delimitaciones operativas, criterios de consolidación y posibles cruces con DataGastro general.
"""
    (DOCS_DIR / "DIAGNOSTICO_INICIAL_POLOS_GASTRO.md").write_text(content, encoding="utf-8")


def write_sources(pdf_path: Path, page_count: int) -> None:
    content = f"""# Fuentes y trazabilidad PolosGastro

## Fuente inicial

- Fuente inicial: `PDF Polos gastronómicos`.
- Archivo usado: `{relative(pdf_path)}`
- Páginas procesadas: {page_count}
- Estado: insumo semilla no validado.
- Uso en Fase 1: inventario, normalización inicial y base candidata.

## Cómo se extrajo

El script `scripts/polos_gastro/inventariar_polos_gastro.py` localiza el PDF candidato dentro del proyecto, extrae texto con `pdftotext` cuando está disponible y registra la cantidad de páginas con `pdfinfo`. Dado que el PDF no tiene tablas estructuradas, la normalización de polos y locales se realiza mediante una carga controlada dentro del script, transcripta desde el texto del PDF.

## Cómo se normalizó

- Se asignó un `polo_id` estable para cada polo o agrupación candidata.
- Se normalizó el tipo de área usando categorías simples: barrio, subpolo, corredor, avenida, zona_costera, zona_central u otro.
- Se conservaron subzonas cuando el PDF las menciona.
- Se separaron filas ambiguas para no fusionar ni dividir sin documentación.
- Se marcó todo como `requiere_validacion = sí`.

## Campos inferidos

- `nombre_normalizado`
- `tipo_area`
- `barrio_o_zona_principal`
- `subzonas`
- `comuna_probable`
- `estado_candidato`
- `nivel_consolidacion`
- `descripcion_breve`
- `observaciones`

Estos campos son lecturas metodológicas de Fase 1. No constituyen validación oficial.

## Campos que requieren validación

- Comunas probables.
- Límites territoriales de cada polo.
- Tramos de avenidas y corredores.
- Vigencia de locales destacados.
- Naturaleza oficial, interna o documental del PDF.
- Criterio de consolidación de cada polo.

## Fuentes complementarias sugeridas para próximas fases

- Datos abiertos del GCBA.
- BA Capital Gastronómica.
- Ente de Turismo.
- Notas institucionales.
- Mapas de barrios y comunas.
- OpenStreetMap / Google Places solo si se define una fase de geocodificación y respetando reglas de uso; no scraping.
- Registros de habilitaciones gastronómicas ya disponibles en DataGastro, si corresponde, sin tocar el pipeline general todavía.

## Trazabilidad por fila

Los CSV generados incluyen `fuente_inicial`, `pagina_fuente`, `requiere_validacion` y `observaciones`. La página de fuente indica el lugar del PDF usado para sostener cada registro, pero no reemplaza una validación territorial o documental.
"""
    (DOCS_DIR / "FUENTES_Y_TRAZABILIDAD_POLOS_GASTRO.md").write_text(content, encoding="utf-8")


def write_reading(polos: list[dict[str, str]], locales: list[dict[str, str]]) -> None:
    local_counts = Counter(row["nombre_polo"] for row in locales)
    top_with_locals = [name for name, _ in local_counts.most_common()]
    incipient = [row["nombre_polo"] for row in polos if row["nivel_consolidacion"] in {"incipiente", "candidato", "requiere_revision"}]

    content = f"""# Lectura inicial PolosGastro

## Lectura ejecutiva breve

La Fase 1 permite construir una primera base candidata de polos gastronómicos de CABA a partir de un PDF semilla. Se identificaron {len(polos)} polos o agrupaciones candidatas y {len(locales)} menciones de locales destacados. La lectura es exploratoria y no habilita todavía un informe final ni un mapa operativo.

## Polos que aparecen más consolidados en el insumo

Los polos con mayor desarrollo interno son aquellos que tienen sección de locales destacados. Entre ellos aparecen:

{chr(10).join(f"- {name}" for name in top_with_locals)}

## Corredores o zonas que aparecen como incipientes o candidatos

Estos casos deberían tratarse como candidatos a validar, no como polos cerrados:

{chr(10).join(f"- {name}" for name in incipient)}

## Zonas con interés para un informe futuro

- Palermo y Belgrano, por presencia de subzonas internas.
- Abasto / Avenida Corrientes, por la ambigüedad entre listado separado y sección agrupada.
- Corredores como DoHo, Federico Lacroze, Avenida Caseros y Avenida Boedo, por requerir delimitación de tramo.
- Zonas emergentes como Nuevo Bajo en Retiro, Devoto y Parque Saavedra / Avenida García del Río.

## Qué falta validar

- Origen y metodología del PDF.
- Delimitaciones territoriales de cada polo.
- Comunas probables y barrios asociados.
- Vigencia de locales destacados.
- Criterio para distinguir consolidado, relevante, incipiente y candidato.
- Cruce eventual con fuentes públicas o internas, sin integrar todavía al pipeline general.

## Cómo podría conectarse con DataGastro

PolosGastro puede funcionar como una capa candidata de lectura territorial. En una fase posterior podría contrastarse con oferta registrada, habilitaciones aprobadas, eventos, ferias y fuentes institucionales. Ese cruce debe hacerse con ficha de fuente, contrato, reglas de privacidad y aprobación explícita antes de tocar el pipeline general de DataGastro.
"""
    (DOCS_DIR / "LECTURA_INICIAL_POLOS_GASTRO.md").write_text(content, encoding="utf-8")


def write_outline() -> None:
    content = """# Esqueleto futuro de informe PolosGastro

Este documento es una base de estructura para una fase posterior. No es un informe final PDF, no contiene conclusiones institucionales cerradas y no debe presentarse como producto terminado.

## 1. Portada

Título tentativo, fecha de corte, área responsable y advertencia de alcance.

## 2. Resumen ejecutivo

Síntesis de objetivo, fuente inicial, hallazgos validados y próximos pasos.

## 3. Qué es un polo gastronómico

Definición operativa: barrio, corredor, avenida, subpolo y zona turística/gastronómica.

## 4. Mapa conceptual de zonas/corredores

Visual futuro, sujeto a validación cartográfica. No generar mapa final hasta definir polígonos o tramos.

## 5. Polos consolidados

Casos con evidencia documental y validación complementaria.

## 6. Polos emergentes

Casos candidatos o incipientes con necesidad de relevamiento adicional.

## 7. Locales destacados como evidencia cualitativa

Uso prudente de menciones de locales. Aclarar que no son padrón oficial, no prueban vigencia y no delimitan por sí solos un polo.

## 8. Oportunidades de gestión

Posibles usos: agenda territorial, promoción, circuitos, diagnóstico de cobertura y articulación con turismo/cultura/desarrollo económico.

## 9. Limitaciones metodológicas

Fuente semilla, ausencia de delimitación formal, vigencia no validada, sesgos territoriales y necesidad de fuentes complementarias.

## 10. Próximos pasos

Validar fuente, construir ficha, definir criterios, contrastar con datos públicos y evaluar integración futura con DataGastro.
"""
    (DOCS_DIR / "ESQUELETO_INFORME_POLOS_GASTRO.md").write_text(content, encoding="utf-8")


def generate() -> dict[str, str]:
    ensure_dirs()
    pdf_path, candidates = find_source_pdf()
    extracted_text = extract_pdf_text(pdf_path)
    page_count = get_page_count(pdf_path, extracted_text)
    locales = build_locales()
    summary_rows = build_summary_rows(POLOS_CANDIDATOS, locales)

    write_csv(OUTPUT_DIR / "polos_gastronomicos_base_candidata.csv", POLOS_CANDIDATOS)
    write_csv(OUTPUT_DIR / "locales_destacados_por_polo_seed.csv", locales)
    write_csv(OUTPUT_DIR / "resumen_polos_inicial.csv", summary_rows)

    write_inventory(pdf_path, candidates, page_count, POLOS_CANDIDATOS, locales)
    write_diagnostic(POLOS_CANDIDATOS, locales)
    write_sources(pdf_path, page_count)
    write_reading(POLOS_CANDIDATOS, locales)
    write_outline()

    return {
        "archivo_fuente": relative(pdf_path),
        "paginas": str(page_count),
        "polos": str(len(POLOS_CANDIDATOS)),
        "locales": str(len(locales)),
        "candidatos_pdf": str(len(candidates)),
    }


def main() -> None:
    result = generate()
    print("PolosGastro Fase 1 generada")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
