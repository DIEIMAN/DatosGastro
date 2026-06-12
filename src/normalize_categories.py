from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

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
    ("C018", "Comercio alimenticio minorista", "Comercio alimenticio minorista"),
]

CATEGORY_BY_NAME = {name: category_id for category_id, name, _ in TAXONOMY}

KEYWORDS = [
    ("Bar notable", ("bar notable", "bares notables", "cafe notable"), 0.95),
    ("Heladeria", ("helader", "helado"), 0.9),
    ("Pizzeria", ("pizz", "empanada"), 0.9),
    ("Parrilla", ("parrill", "asador", "asado"), 0.9),
    ("Panaderia", ("panader", "panificacion"), 0.9),
    ("Pasteleria", ("pasteler", "confiter", "repost"), 0.85),
    ("Cafe", ("cafe", "cafeter"), 0.85),
    ("Foodtruck", ("food truck", "foodtruck", "puesto movil"), 0.85),
    ("Catering", ("catering", "servicio de lunch", "lunch"), 0.85),
    ("Feria", ("feria", "fiab", "ba market"), 0.85),
    ("Mercado", ("mercado", "mercado gastronomico"), 0.85),
    ("Comida al paso", ("rotiser", "casa de comidas", "comida al paso", "take away", "sandwich"), 0.8),
    ("Bar", ("bar", "cervecer", "pub", "vinotec", "bodegon"), 0.8),
    ("Restaurante", ("restaurante", "restaurant", "restoran", "resto", "cantina"), 0.8),
]

PREFIX_KEYWORDS = {
    "helader",
    "panader",
    "confiter",
    "rotiser",
    "cervecer",
    "pizz",
    "pizzer",
    "parrill",
    "pasteler",
    "cafeter",
    "sandwich",
    "vinotec",
}

EXACT_PLURAL_PATTERNS = {
    "bar": r"\bbar(?:es)?\b",
    "pub": r"\bpubs?\b",
    "cafe": r"\bcafes?\b",
    "pizza": r"\bpizzas?\b",
    "empanada": r"\bempanadas?\b",
    "helado": r"\bhelados?\b",
    "asado": r"\basados?\b",
    "bodegon": r"\bbodegon(?:es)?\b",
    "cantina": r"\bcantinas?\b",
    "restoran": r"\brestoran(?:es)?\b",
    "feria": r"\bferias?\b",
    "mercado": r"\bmercados?\b",
}

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

EXCLUSION_PATTERNS = (
    (r"\bexcluid[oa]s?\b[^\)]*", "Texto de exclusion normativa"),
    (r"\benvasad\w*\b", "Producto envasado sin servicio gastronomico"),
    (r"\bpublicidad\b", "Publicidad no gastronomica"),
    (r"\bpublicacion(?:es)?\b", "Publicaciones no gastronomicas"),
    (r"\btalabarteria\b", "Talabarteria no gastronomica"),
    (r"\bmarroquineria\b", "Marroquineria no gastronomica"),
    (r"\bguardabarros\b", "Guardabarros no gastronomico"),
    (r"\bembarcacion(?:es)?\b", "Embarcaciones no gastronomicas"),
    (r"\bbarniz(?:es)?\b", "Barnices no gastronomicos"),
    (r"\ben\s+barras\b", "Frase 'en barras' no equivale a bar"),
)

COMERCIO_ALIMENTICIO_PATTERNS = (
    r"\bproductos\s+alimenticios\b",
    r"\bproducto\s+alimenticio\b",
    r"\bventa\s+de\s+alimentos\b",
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


@lru_cache(maxsize=None)
def _keyword_pattern(keyword: str) -> re.Pattern:
    normalized = strip_accents(keyword).lower()
    words = re.findall(r"\w+", normalized)
    if not words:
        return re.compile(r"a^")
    if len(words) == 1:
        word = words[0]
        if word in PREFIX_KEYWORDS:
            return re.compile(rf"\b{re.escape(word)}\w*")
        if word in EXACT_PLURAL_PATTERNS:
            return re.compile(EXACT_PLURAL_PATTERNS[word])
        return re.compile(rf"\b{re.escape(word)}\b")
    return re.compile(r"\b" + r"\s+".join(re.escape(word) for word in words) + r"\b")


def _match_keyword(text: str, keyword: str) -> bool:
    return bool(_keyword_pattern(keyword).search(text))


def _mask_exclusions(text: str) -> tuple[str, list[str]]:
    result = text
    reasons = []
    for pattern, reason in EXCLUSION_PATTERNS:
        if re.search(pattern, result):
            reasons.append(reason)
            result = re.sub(pattern, " ", result)
    result = re.sub(r"\s+", " ", result).strip()
    return result, reasons


def _matches_comercio_alimenticio(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in COMERCIO_ALIMENTICIO_PATTERNS)


def classify_gastronomic_category(*values) -> CategoryResult:
    """Clasifica rubros como gastronomia de servicio, comercio alimenticio o no gastronomicos.

    El matching de rubros gastronomicos usa limites de palabra sobre texto
    normalizado sin acentos. Las raices documentadas como prefijos se evaluan
    solo al inicio de palabra. Los rubros de venta minorista de productos
    alimenticios sin evidencia de servicio gastronomico se separan como
    "Comercio alimenticio minorista" y no alimentan la fact table F02
    gastronomica.
    """
    text = _search_text(*values)
    if not text:
        return CategoryResult("requiere_validacion", "Requiere validacion", 0.0, "Sin texto para clasificar", "C017")

    for keyword in NON_GASTRO_KEYWORDS:
        if _match_keyword(text, keyword):
            return CategoryResult("no", "No gastronomico", 0.9, f"Keyword no gastronomica: {keyword}", "C016")

    match_text, exclusion_reasons = _mask_exclusions(text)

    for category, keywords, confidence in KEYWORDS:
        for keyword in keywords:
            if _match_keyword(match_text, keyword):
                return CategoryResult("si", category, confidence, f"Keyword gastronomica: {keyword}", CATEGORY_BY_NAME[category])

    if _matches_comercio_alimenticio(match_text):
        return CategoryResult(
            "no",
            "Comercio alimenticio minorista",
            0.85,
            "Venta minorista de productos alimenticios sin servicio gastronomico",
            CATEGORY_BY_NAME["Comercio alimenticio minorista"],
        )

    if exclusion_reasons:
        return CategoryResult(
            "no",
            "No gastronomico",
            0.8,
            "; ".join(exclusion_reasons),
            "C016",
        )

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
