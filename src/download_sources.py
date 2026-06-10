
import requests
from pathlib import Path
from config import DATA_RAW, SOURCES


def download_file(url: str, out_path: Path):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    print(f'Descargado: {out_path} ({len(r.content)} bytes)')

if __name__ == '__main__':
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    # F01 tiene URL directa conocida.
    download_file(SOURCES['F01'], DATA_RAW / 'establecimientos_gastronomicos_full.csv')
    print('F02 y F03: revisar portales BA Data para recursos anuales/GeoJSON y agregar URLs directas al config.')
