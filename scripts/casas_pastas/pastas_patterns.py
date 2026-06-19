"""Clasificador estricto de casas/fábricas de pastas (universos A / B / C).

Objetivo: separar SOLO casas de pastas, fábricas de pastas, elaboración/venta de pastas
frescas o secas y pastificios. NO incluir restaurantes italianos, trattorias, pizzerías,
bares ni gastronómicos generales (esos van a C / descartados).

Niveles:
  A — estricto confirmado: rubro/nombre/descripción indica claramente casa/fábrica/elaboración/
      venta de pastas.
  B — probable: indicios fuertes (nombre con "pastas" pero rubro genérico, "pastas caseras/
      artesanales") no totalmente concluyentes.
  C — dudoso/descartado: mención ambigua de pasta, o restaurante/italiano/pizzería/bar.

Devuelve un dict con: nivel, categoria_pastas, patron_detectado, confianza_categoria,
motivo_categoria. No tiene dependencias externas.
"""
from __future__ import annotations

import re
import unicodedata


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text)).strip()


# --- Patrones ESTRICTOS (universo A): rubro/elaboración/fábrica/venta de pastas ---
# Cada patrón: (regex sobre texto normalizado, categoria_pastas, etiqueta)
STRICT_PATTERNS = [
    (r"elaboracion de pastas alimenticias frescas", "pastas_frescas", "elaboracion_pastas_frescas"),
    (r"elaboracion de pastas alimenticias secas", "pastas_secas", "elaboracion_pastas_secas"),
    (r"elaboracion de pastas( frescas)?", "elaboracion_pastas", "elaboracion_pastas"),
    (r"fabrica de pastas( alimenticias)?( frescas)?", "fabrica_pastas", "fabrica_pastas"),
    (r"pastas alimenticias", "pastas_alimenticias", "pastas_alimenticias"),
    (r"casas? de pastas", "casa_pastas", "casa_de_pastas"),
    (r"pastificio", "pastificio", "pastificio"),
    (r"venta de pastas frescas", "venta_pastas_frescas", "venta_pastas_frescas"),
    (r"pastas frescas", "pastas_frescas", "pastas_frescas"),
    (r"\bravioles?\b", "producto_pastas", "ravioles"),
    (r"\bsorrentinos?\b", "producto_pastas", "sorrentinos"),
    (r"\bnoquis?\b", "producto_pastas", "noquis"),
    (r"fideos frescos", "producto_pastas", "fideos_frescos"),
    (r"tallarines frescos", "producto_pastas", "tallarines_frescos"),
]

# --- Términos de PASTA genéricos (para B) ---
PASTA_HINT = re.compile(r"\bpastas?\b|raviol|sorrentino|noqui|fideo|tallarin|pastific|canelon|capelet|agnolot")
# Contexto de producción/venta que refuerza B
PROD_CONTEXT = re.compile(r"fabrica|elaborac|artesanal|casera|caseras|venta|pastas caseras|pastas artesanales|rotiseria")

# --- Exclusiones (empujan a C salvo que haya match estricto) ---
EXCLUDE = re.compile(
    r"restaurant|trattoria|ristorante|pizz|parrilla|\bbar\b|cerveceria|cafe|cafeteria|"
    r"heladeria|panaderia|confiteria|cocina italiana|pasta bar|comida italiana|resto"
)


def classify(*texts: str) -> dict:
    """Clasifica un registro a partir de uno o más campos textuales (rubro, nombre, etc.).

    Devuelve siempre un dict; nivel 'C' si no hay señal clara de casa/fábrica de pastas.
    """
    blob = " ".join(norm(t) for t in texts if t)

    # 1) match estricto -> A (aunque haya palabras de restaurante, el rubro manda)
    for pattern, categoria, etiqueta in STRICT_PATTERNS:
        if re.search(pattern, blob):
            return {
                "nivel": "A",
                "categoria_pastas": categoria,
                "patron_detectado": etiqueta,
                "confianza_categoria": 0.9,
                "motivo_categoria": f"Patron estricto: {etiqueta}",
            }

    tiene_pasta = bool(PASTA_HINT.search(blob))
    tiene_exclusion = bool(EXCLUDE.search(blob))

    # 2) indicio de pasta + contexto de producción/venta, sin exclusión clara -> B
    if tiene_pasta and PROD_CONTEXT.search(blob) and not tiene_exclusion:
        return {
            "nivel": "B",
            "categoria_pastas": "probable_pastas_produccion_venta",
            "patron_detectado": "pasta+contexto_produccion",
            "confianza_categoria": 0.6,
            "motivo_categoria": "Mencion de pastas con contexto de fabrica/elaboracion/venta, rubro no concluyente",
        }

    # 3) nombre/menciona pasta pero sin contexto ni exclusión -> B débil
    if tiene_pasta and not tiene_exclusion:
        return {
            "nivel": "B",
            "categoria_pastas": "probable_nombre_pastas",
            "patron_detectado": "pasta_en_texto",
            "confianza_categoria": 0.5,
            "motivo_categoria": "Texto menciona pastas sin rubro concluyente y sin senial de restaurante",
        }

    # 4) menciona pasta pero hay señal de restaurante/italiano/pizzería -> C
    if tiene_pasta and tiene_exclusion:
        return {
            "nivel": "C",
            "categoria_pastas": "ambiguo_gastronomico",
            "patron_detectado": "pasta+restaurante",
            "confianza_categoria": 0.3,
            "motivo_categoria": "Mencion de pasta en contexto de restaurante/italiano/pizzeria: no es casa/fabrica de pastas",
        }

    # 5) sin señal de pasta -> C (no debería entrar al universo)
    return {
        "nivel": "C",
        "categoria_pastas": "sin_senial_pastas",
        "patron_detectado": "",
        "confianza_categoria": 0.0,
        "motivo_categoria": "Sin patron de pastas",
    }


if __name__ == "__main__":
    pruebas = [
        ("Elaboración de pastas alimenticias frescas", ""),
        ("Elaboración de pastas alimenticias secas", ""),
        ("COM.MIN. DE PRODUCTOS ALIMENTICIOS", "Farfalla Pastas S.R.L"),
        ("RESTAURANTE", "La Pasta"),
        ("RESTAURANTE", "Trattoria Da Mario - pastas caseras"),
        ("Pastificio Don Luigi", ""),
        ("Casa de Pastas La Nonna", ""),
        ("VENTA DE ROPA", "Boutique Sorrentino"),
    ]
    for t in pruebas:
        print(t, "->", classify(*t))
