from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from build_model import enrich_locations_with_geo_cache


class GeoCacheBuildModelTest(unittest.TestCase):
    def test_enriches_non_official_location_and_preserves_official_coordinates(self):
        dim = pd.DataFrame(
            [
                {
                    "id_ubicacion": "U001",
                    "direccion_original": "RIVADAVIA 3102",
                    "direccion_normalizada": "Pendiente USIG",
                    "barrio": "Balvanera",
                    "comuna": "3",
                    "latitud": "No disponible",
                    "longitud": "No disponible",
                    "calidad_geo": "sin_geo",
                    "requiere_validacion": "si",
                    "motivo_validacion": "Geocodificacion pendiente con USIG",
                },
                {
                    "id_ubicacion": "U002",
                    "direccion_original": "RIVADAVIA 3102",
                    "direccion_normalizada": "RIVADAVIA 3102",
                    "barrio": "Balvanera",
                    "comuna": "3",
                    "latitud": "-34.60",
                    "longitud": "-58.40",
                    "calidad_geo": "fuente_oficial",
                    "requiere_validacion": "no",
                    "motivo_validacion": "Coordenadas provistas por fuente oficial",
                },
            ]
        )
        cache = pd.DataFrame(
            [
                {
                    "direccion_original": "RIVADAVIA 3102",
                    "direccion_normalizada": "RIVADAVIA AV. 3102",
                    "latitud": "-34.61052573",
                    "longitud": "-58.41050581",
                    "barrio_usig": "Balvanera",
                    "comuna_usig": "3",
                    "precision": "calle_altura",
                    "estado": "exacta",
                    "fecha_consulta": "2026-06-12",
                }
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "geo_cache.csv"
            cache.to_csv(cache_path, index=False)
            enriched = enrich_locations_with_geo_cache(dim, cache_path)

        self.assertEqual(enriched.loc[0, "calidad_geo"], "usig_exacta")
        self.assertEqual(enriched.loc[0, "latitud"], "-34.61052573")
        self.assertEqual(enriched.loc[1, "calidad_geo"], "fuente_oficial")
        self.assertEqual(enriched.loc[1, "latitud"], "-34.60")


if __name__ == "__main__":
    unittest.main()
