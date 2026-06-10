from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_ANALYTICS = ROOT / "data" / "analytics"
OUTPUTS = ROOT / "outputs"
PROFILE_OUTPUTS = OUTPUTS / "tablas_resumen"
DOCS = ROOT / "docs"

PENDING_URL = "PENDIENTE_URL_DIRECTA"

SOURCE_CONFIG = {
    "F01": {
        "name": "Oferta y Establecimientos Gastronomicos",
        "description": "Registro de oferta y establecimientos gastronomicos publicado por BA Data / GCBA.",
        "url": None,
        "target_filename": "f01_oferta_establecimientos_gastronomicos.csv",
        "seed_glob": "raw_establecimientos_gastronomicos.csv",
        "portal_url": "https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos",
    },
    "F02": {
        "name": "Habilitaciones Aprobadas AGC",
        "description": "Habilitaciones aprobadas por anio publicadas por BA Data / AGC.",
        "url": None,
        "target_filename": "f02_habilitaciones_aprobadas.csv",
        "seed_glob": "raw_habilitaciones_aprobadas*.csv",
        "portal_url": "https://data.buenosaires.gob.ar/dataset/habilitaciones-aprobadas",
    },
    "F03": {
        "name": "Ferias y Mercados",
        "description": "Ferias, mercados y espacios afines publicados por BA Data / GCBA.",
        "url": None,
        "target_filename": "f03_ferias_mercados.csv",
        "seed_glob": "raw_ferias_mercados.csv",
        "portal_url": "https://data.buenosaires.gob.ar/dataset/ferias-mercados",
    },
}

# Backwards-compatible alias used by earlier scripts.
SOURCES = {key: item["url"] for key, item in SOURCE_CONFIG.items()}

BARRIO_COMUNA = {
    "Agronomia": "15",
    "Almagro": "5",
    "Balvanera": "3",
    "Barracas": "4",
    "Belgrano": "13",
    "Boedo": "5",
    "Caballito": "6",
    "Chacarita": "15",
    "Coghlan": "12",
    "Colegiales": "13",
    "Constitucion": "1",
    "Flores": "7",
    "Floresta": "10",
    "La Boca": "4",
    "La Paternal": "15",
    "Liniers": "9",
    "Mataderos": "9",
    "Monte Castro": "10",
    "Monserrat": "1",
    "Nueva Pompeya": "4",
    "Nunez": "13",
    "Palermo": "14",
    "Parque Avellaneda": "9",
    "Parque Chacabuco": "7",
    "Parque Chas": "15",
    "Parque Patricios": "4",
    "Puerto Madero": "1",
    "Recoleta": "2",
    "Retiro": "1",
    "Saavedra": "12",
    "San Cristobal": "3",
    "San Nicolas": "1",
    "San Telmo": "1",
    "Velez Sarsfield": "10",
    "Versalles": "10",
    "Villa Crespo": "15",
    "Villa del Parque": "11",
    "Villa Devoto": "11",
    "Villa General Mitre": "11",
    "Villa Lugano": "8",
    "Villa Luro": "10",
    "Villa Ortuzar": "15",
    "Villa Pueyrredon": "12",
    "Villa Real": "10",
    "Villa Riachuelo": "8",
    "Villa Santa Rita": "11",
    "Villa Soldati": "8",
    "Villa Urquiza": "12",
}

SOURCE_STATUS_VALUES = {
    "seed": "datos seed",
    "partial": "datos reales parciales",
    "complete": "datos reales completos",
    "pending": "datos pendientes de validacion",
}
