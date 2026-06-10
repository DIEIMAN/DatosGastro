from __future__ import annotations

from dataclasses import dataclass

from clean_text import normalize_text, strip_accents


TAXONOMY = [
    ("C001", "Restaurante", "Restaurante"),
    ("C002", "Bar", "Bar"),
    ("C003", "Cafe", "Cafe"),
    ("C004", "Bar notable", "Bar notable"),
    ("C005", "Heladeria", "Heladeria"),
    ("C006", "Pizzeria", "Pizzeria"),
    ("C007", "Parrilla", "Parrilla"),
    ("C008", "Panaderia", "Panaderia"),
    ("C009", "Pasteleria", "Pasteleria"),
    ("C010", "Mercado", "Mercado"),
    ("C011", "Feria", "Feria"),
    ("C012", "Foodtruck", "Foodtruck"),
    ("C013", "Catering", "Catering"),
    ("C014", "Comida al paso", "Comida al paso"),
    ("C015", "Otro gastronomico", "Otro gastronomico"),
    ("C016", "No gastronomico", "No gastronomico"),
    ("C017", "Requiere validacion", "Requiere validacion"),
]

CATEGORY_BY_NAME = {name: category_id for category_id, name, _ in TAXONOMY}

KEYWORDS = [
    ("Bar notable", ("bar notable", "bares notables", "cafe notable", "café notable"), 0.95),
    ("Heladeria", ("helader", "helado"), 0.9),
    ("Pizzeria", ("pizzer", "pizza", "empanada"), 0.9),
    ("Parrilla", ("parrilla", "asador", "asado"), 0.9),
    ("Panaderia", ("panader", "panificacion"), 0.9),
    ("Pasteleria", ("pasteler", "confiter", "repost"), 0.85),
    ("Cafe", ("cafe", "cafeter", "café"), 0.85),
    ("Foodtruck", ("food truck", "foodtruck", "puesto movil", "puesto móvil"), 0.85),
    ("Catering", ("catering", "servicio de lunch", "lunch"), 0.85),
    ("Feria", ("feria", "fiab", "ba market"), 0.85),
    ("Mercado", ("mercado", "mercado gastronomico", "mercado gastronómico"), 0.85),
    ("Comida al paso", ("rotiser", "casa de comidas", "comida al paso", "take away", "sandwich"), 0.8),
    ("Bar", ("bar", "cervecer", "pub", "vinoteca", "bodegon", "bodegón"), 0.8),
    ("Restaurante", ("restaurante", "restaurant", "restoran", "resto", "cantina"), 0.8),
]

NON_GASTRO_KEYWORDS = (
    "farmacia",
    "kiosco",
    "libreria",
    "peluqueria",
    "indumentaria",
    "oficina",
    "estacionamiento",
    "gimnasio",
)


@dataclass(frozen=True)
class CategoryResult:
    es_gastronomico: str
    categoria_gastronomica_inferida: str
    confianza_categoria: float
    motivo_categoria: str
    id_categoria: str


def _search_text(*values) -> str:
    return " ".join(strip_accents(normalize_text(value, case="lower")) for value in values if value is not None)


def classify_gastronomic_category(*values) -> CategoryResult:
    text = _search_text(*values)
    if not text:
        return CategoryResult("requiere_validacion", "Requiere validacion", 0.0, "Sin texto para clasificar", "C017")

    for keyword in NON_GASTRO_KEYWORDS:
        if keyword in text:
            return CategoryResult("no", "No gastronomico", 0.9, f"Keyword no gastronomica: {keyword}", "C016")

    for category, keywords, confidence in KEYWORDS:
        for keyword in keywords:
            if strip_accents(keyword).lower() in text:
                return CategoryResult("si", category, confidence, f"Keyword gastronomica: {keyword}", CATEGORY_BY_NAME[category])

    return CategoryResult(
        "requiere_validacion",
        "Requiere validacion",
        0.35,
        "No se encontraron keywords gastronomicas trazables",
        "C017",
    )


def normalize_category(value):
    result = classify_gastronomic_category(value)
    return result.categoria_gastronomica_inferida, result.id_categoria


def taxonomy_dataframe_rows():
    rows = []
    for category_id, category, subcategory in TAXONOMY:
        rows.append(
            {
                "id_categoria": category_id,
                "categoria_general": category,
                "subcategoria": subcategory,
                "descripcion": f"Categoria normalizada V2: {category}",
                "ejemplos": "",
            }
        )
    return rows
