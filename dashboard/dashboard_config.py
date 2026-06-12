from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYTICS = ROOT / "data" / "analytics"
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"

TRACE_COLUMNS = [
    "estado_datos",
    "fuentes_utilizadas",
    "urls_fuentes",
    "fecha_consulta_min",
    "fecha_consulta_max",
    "nota_metodologica",
    "limitaciones",
    "apto_dashboard",
]

F02_SERIE_ORDER = ["2019", "2020", "2021", "2022", "2023", "2024"]

CATEGORY_COLORS = {
    "Restaurante": [43, 108, 176, 170],
    "Bar": [214, 94, 96, 170],
    "Cafe": [136, 86, 167, 170],
    "Bar notable": [188, 189, 34, 170],
    "Heladeria": [23, 190, 207, 170],
    "Pizzeria": [255, 127, 14, 170],
    "Parrilla": [140, 86, 75, 170],
    "Panaderia": [44, 160, 44, 170],
    "Pasteleria": [227, 119, 194, 170],
    "Mercado": [31, 119, 180, 170],
    "Feria": [148, 103, 189, 170],
    "Foodtruck": [127, 127, 127, 170],
    "Catering": [188, 127, 14, 170],
    "Comida al paso": [102, 166, 30, 170],
}

DEFAULT_POINT_COLOR = [80, 80, 80, 150]
FIAB_POINT_COLOR = [40, 150, 95, 220]

