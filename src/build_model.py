
from pathlib import Path
import pandas as pd
from config import DATA_RAW, DATA_PROCESSED

if __name__ == '__main__':
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    print('Modelo seed ya incluido. Próxima iteración: leer full CSVs descargados y reconstruir processed.')
    for csv in DATA_RAW.glob('*.csv'):
        try:
            df = pd.read_csv(csv)
            print(csv.name, df.shape)
        except Exception as exc:
            print(csv.name, 'ERROR', exc)
