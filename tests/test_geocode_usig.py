from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from geocode_usig import parse_usig_payload, pending_addresses, read_cache, write_cache


class GeocodeUsigTest(unittest.TestCase):
    def test_parse_exact_result_inside_caba(self):
        payload = {
            "direccionesNormalizadas": [
                {
                    "direccion": "RIVADAVIA AV. 3102",
                    "tipo": "calle_altura",
                    "coordenadas": {"x": -58.41050581, "y": -34.61052573},
                    "barrio": "Balvanera",
                    "comuna": "3",
                }
            ]
        }

        result = parse_usig_payload("RIVADAVIA 3102", payload, fecha_consulta="2026-06-12")

        self.assertEqual(result.estado, "exacta")
        self.assertEqual(result.latitud, "-34.61052573")
        self.assertEqual(result.longitud, "-58.41050581")
        self.assertEqual(result.fecha_consulta, "2026-06-12")

    def test_parse_out_of_bounds_result_is_suspicious(self):
        payload = {
            "direccionesNormalizadas": [
                {
                    "direccion": "FUERA DE CABA 1",
                    "tipo": "calle_altura",
                    "coordenadas": {"x": -57.0, "y": -34.0},
                }
            ]
        }

        result = parse_usig_payload("FUERA DE CABA 1", payload, fecha_consulta="2026-06-12")

        self.assertEqual(result.estado, "sospechosa")

    def test_pending_addresses_skips_cached_entries(self):
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

        self.assertEqual(pending_addresses(["rivadavia 3102", "Corrientes 1000"], cache), ["Corrientes 1000"])

    def test_cache_roundtrip_keeps_required_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "geo_cache.csv"
            write_cache(pd.DataFrame([{"direccion_original": "Corrientes 1000", "estado": "sin_match"}]), path)
            cache = read_cache(path)

        self.assertIn("fecha_consulta", cache.columns)
        self.assertIn("direccion_normalizada", cache.columns)


if __name__ == "__main__":
    unittest.main()
