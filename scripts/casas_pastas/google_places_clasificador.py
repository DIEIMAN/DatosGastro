"""Clasificador compartido de candidatos de Google Places (casas/fábricas/venta de pastas).

Criterio ajustado (lo aprendido en el piloto ampliado):
- El universo NO es solo "fábrica de pastas" estricta: incluye casas de pastas, pastas
  frescas, pastificios, fábricas y locales de VENTA de ravioles/sorrentinos/ñoquis/
  tallarines/fideos frescos (tipo "Master Pastas"), aunque Google les ponga algún tipo
  gastronómico.
- NO descartar automáticamente por tener 'restaurant' en types.
- A: nombre claro de pastas + algún tipo de VENTA (food_store/store/manufacturer/noodle_shop...).
- B: nombre de pastas pero Google solo lo tipa como gastronómico (sin tipo de venta) -> revisar.
- C: claramente restaurante/trattoria/bar de pasta/pasta bar/pizzería/gastronómico general,
  o sin término de pastas en el nombre.

Usado por google_places_ampliado.py, google_places_reclasificar.py y google_places_consolidar.py
para garantizar el MISMO criterio en todas las corridas. No hace requests ni usa API key.
"""
from __future__ import annotations

import re
import unicodedata

A = "A_google_probable_casa_pastas"
B = "B_google_dudoso"
C = "C_google_descartado"
RANK = {A: 3, B: 2, C: 1}

# Marcas/cadenas esperadas (clave normalizada, sin acentos). Compartido por la auditoría
# de cobertura y la consolidación, para medir presencia/ausencia con un único criterio.
MARCAS_ESPERADAS = {
    "la juvenil": ["la juvenil"],
    "master pastas / pastas master": ["master pastas", "pastas master"],
    "multipasta": ["multipasta"],
    "biasatti": ["biasatti"],
    "caprizzi": ["caprizzi"],
    "raviolon": ["raviolon"],
    "pastas mazzeo": ["mazzeo"],
    "la salteña (venta directa)": ["la saltena"],
    "el buen gusto": ["el buen gusto"],
    "las malvinas": ["las malvinas"],
}

STRONG_SHOP = [
    "pastificio", "fabrica de pasta", "fabrica de fideos", "pastas frescas",
    "pastas caseras", "pastas artesanales", "casa de pasta", "master pastas",
]
PRODUCTO = [
    "pasta", "pastas", "raviol", "sorrentin", "noqui", "gnocchi", "tallarin",
    "fideos", "canelon", "agnolotti", "capeletti", "capelletti", "fettuccine",
]
RETAIL_TYPES = {
    "food_store", "store", "manufacturer", "grocery_store", "noodle_shop",
    "wholesaler", "deli", "delicatessen", "supermarket", "convenience_store", "market",
}
PREPARED_TYPES = {
    "restaurant", "italian_restaurant", "meal_takeaway", "meal_delivery",
    "dessert_restaurant", "cafe", "cafeteria", "brunch_restaurant", "food_delivery",
    "bar", "fast_food_restaurant", "fine_dining_restaurant", "pizza_restaurant",
    "coffee_shop",
}


def strip_acc(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def norm_nombre(s: str) -> str:
    s = strip_acc((s or "").lower())
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def es_restaurante_puro(n: str) -> bool:
    """n: nombre normalizado. True si el NOMBRE delata restaurante/bar/pizzería."""
    if "bar de pasta" in n or "pasta bar" in n:
        return True
    palabras = ["trattoria", "ristorante", "restaurante", "restaurant", "pizzeria",
                "pizza", "osteria", "cantina", "cucina", "parrilla", "bodegon",
                "rotiseria", "cafeteria", "comedor"]
    if any(w in n for w in palabras):
        return True
    if re.search(r"\bbar\b", n):   # 'bar' como palabra suelta (no 'barilla')
        return True
    if re.search(r"\bcafe\b", n):
        return True
    return False


def clasificar(nombre: str, types_str: str) -> tuple[str, str, str, bool]:
    """(match, confianza, motivo, requiere_revision_manual). types_str: 'a;b;c'."""
    n = norm_nombre(nombre)
    tset = {t.strip().lower() for t in (types_str or "").split(";") if t.strip()}

    if es_restaurante_puro(n):
        return (C, "baja", "señal de restaurante/bar/pizzería/trattoria en el nombre", False)

    strong = any(strip_acc(k) in n for k in STRONG_SHOP)
    prod = any(strip_acc(k) in n for k in PRODUCTO)
    if not (strong or prod):
        return (C, "baja", "sin término de pastas en el nombre", False)

    retail = bool(tset & RETAIL_TYPES)
    prepared = bool(tset & PREPARED_TYPES)

    if retail:
        if strong and not prepared:
            return (A, "alta", "nombre de casa/fábrica/pastas + tipo de venta, sin tipo gastronómico", False)
        if strong and prepared:
            return (A, "media-alta",
                    "nombre fuerte de pastas + tipo de venta (también tipos gastronómicos: revisar)", True)
        return (A, "media",
                "producto de pastas en el nombre + tipo de venta" +
                (" (con tipos gastronómicos: revisar)" if prepared else ""), bool(prepared))

    return (B, "media",
            "nombre de pastas pero Google solo lo tipa como gastronómico (sin tipo de venta): revisar",
            True)


# Nombres genéricos de categoría (NO son marcas/cadenas aunque se repitan): varios locales
# independientes distintos pueden llamarse así. No deben contarse como sucursales de una cadena.
NOMBRES_GENERICOS = {
    "pasta", "pastas", "pastas frescas", "pastas caseras", "pastas artesanales",
    "pastificio", "fabrica de pasta", "fabrica de pastas", "casa de pasta", "casa de pastas",
    "pastas frescas caseras", "pasta fresca", "fabrica de fideos",
}


def clasificar_cadena(nombre_norm: str, conteo_nombre: int) -> tuple[str, str]:
    """Devuelve (tipo_establecimiento, cadena_detectada).

    cadena si: coincide con una marca conocida, o el nombre normalizado se repite (>=2)
    y NO es un nombre genérico de categoría. En otro caso, independiente.
    """
    for marca, claves in MARCAS_ESPERADAS.items():
        if any(k in nombre_norm for k in claves):
            return "cadena", marca
    if conteo_nombre >= 2 and nombre_norm not in NOMBRES_GENERICOS:
        return "cadena", nombre_norm
    return "independiente", ""


def conf_integrada(match: str, n_queries: int) -> str:
    if match == A:
        return "alta" if n_queries >= 2 else "media-alta"
    if match == B:
        return "media"
    return "baja"
