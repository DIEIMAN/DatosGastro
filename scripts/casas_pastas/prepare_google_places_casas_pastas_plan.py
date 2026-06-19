"""Plan de integración Google Places para casas/fábricas de pastas. NO llama a la API.

Genera un CSV de plan de consultas (text search + grilla por comuna) y la lista de campos
deseados si en el futuro se usa la API oficial con autorización y presupuesto. No hace scraping,
no usa ni guarda API key, no ejecuta llamadas pagas.

Ver docs/skills_claude/06_fuentes_externas_privadas.md.

Salida: outputs/casas_pastas/google_places_plan_casas_pastas.csv
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "casas_pastas" / "google_places_plan_casas_pastas.csv"

QUERIES = [
    "casa de pastas CABA", "casa de pastas Buenos Aires", "pastas frescas CABA",
    "fábrica de pastas CABA", "fabrica de pastas Buenos Aires", "pastificio Buenos Aires",
    "ravioles CABA", "sorrentinos CABA", "fideos frescos CABA",
]
# Campos deseados si en el futuro se usa Places API (New) oficial
CAMPOS_DESEADOS = [
    "place_id", "display_name", "formatted_address", "location", "business_status", "types",
    "rating", "user_rating_count", "price_level", "regular_opening_hours", "website_uri",
    "national_phone_number",
]
COMUNAS = list(range(1, 16))


def main():
    rows = []
    # 1) búsquedas por texto a nivel ciudad
    for q in QUERIES:
        rows.append({
            "tipo_busqueda": "text_search_ciudad", "query": q, "comuna": "", "zona": "CABA",
            "metodo_sugerido": "Places Text Search (New)", "filtro_post": "aplicar criterio estricto A/B/C",
            "campos_deseados": ";".join(CAMPOS_DESEADOS),
            "nota": "NO ejecutar sin API key + autorizacion + presupuesto. No scraping.",
        })
    # 2) grilla por comuna (texto + comuna) para mejorar cobertura territorial
    for cm in COMUNAS:
        for q in ["casa de pastas", "fabrica de pastas", "pastas frescas", "pastificio"]:
            rows.append({
                "tipo_busqueda": "text_search_por_comuna", "query": f"{q} comuna {cm} CABA",
                "comuna": cm, "zona": f"Comuna {cm}",
                "metodo_sugerido": "Places Text Search (New) o Nearby con centro de comuna",
                "filtro_post": "aplicar criterio estricto A/B/C; descartar restaurantes/italianos",
                "campos_deseados": ";".join(CAMPOS_DESEADOS),
                "nota": "NO ejecutar sin API key + autorizacion + presupuesto. No scraping.",
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["tipo_busqueda", "query", "comuna", "zona",
                                           "metodo_sugerido", "filtro_post", "campos_deseados", "nota"])
        w.writeheader(); w.writerows(rows)
    print(f"Plan generado (sin llamadas a API): {OUT}")
    print(f"Consultas propuestas: {len(rows)} ({len(QUERIES)} a nivel ciudad + grilla por comuna)")
    print("Recordatorio: este script nunca llama a Google ni usa API keys. No scraping.")


if __name__ == "__main__":
    main()
