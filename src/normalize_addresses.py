
import requests

USIG_URL = 'https://servicios.usig.buenosaires.gob.ar/normalizar/'


def normalize_address(address: str):
    """Prepara normalización con USIG. Requiere internet.
    Devuelve dict con campos mínimos; si falla, marca sin_geo.
    """
    if not address:
        return {'direccion_normalizada': 'No disponible', 'calidad_geo': 'sin_geo'}
    try:
        r = requests.get(USIG_URL, params={'direccion': address}, timeout=15)
        r.raise_for_status()
        data = r.json()
        return {'direccion_normalizada': data.get('direccion', address), 'raw_usig': data, 'calidad_geo': 'exacta'}
    except Exception as exc:
        return {'direccion_normalizada': 'Pendiente USIG', 'calidad_geo': 'sin_geo', 'error': str(exc)}
