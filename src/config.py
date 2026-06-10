
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / 'data' / 'raw'
DATA_PROCESSED = ROOT / 'data' / 'processed'
DATA_ANALYTICS = ROOT / 'data' / 'analytics'
SOURCES = {
    'F01': 'https://cdn.buenosaires.gob.ar/datosabiertos/datasets/ente-de-turismo/oferta-establecimientos-gastronomicos/establecimientos_gastronomicos.csv',
    'F02': 'https://data.buenosaires.gob.ar/dataset/habilitaciones-aprobadas',
    'F03': 'https://data.buenosaires.gob.ar/dataset/ferias-mercados',
}
