from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from geocode_usig import (
    GeocodeResult,
    consistency_report,
    generate_f02_address_candidates,
    normalize_f02_address,
    parse_usig_payload,
    pending_addresses,
    read_cache,
    select_geocode_result,
    write_cache,
)


class GeocodeUsigTest(unittest.TestCase):
    def test_normalize_f02_address_handles_inverted_agc_streets(self):
        cases = {
            "FERNANDEZ DE LA CRUZ, F., GRAL. AV. 4602": "FERNANDEZ DE LA CRUZ 4602",
            "LAFERRERE, GREGORIO de 1383;LAFERRERE, GREGORIO de 1387": "LAFERRERE 1383",
            "NICARAGUA 6048": "NICARAGUA 6048",
            "LARRAZABAL AV. 705": "LARRAZABAL 705",
        }

        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_f02_address(raw), expected)

    def test_generate_f02_address_candidates_preserves_inverted_street_parts(self):
        cases = {
            "SUAREZ, JOSE LEON 52": ["JOSE LEON SUAREZ 52"],
            "DIAZ, CNEL. AV. 1944": ["CORONEL DIAZ 1944", "AV CORONEL DIAZ 1944"],
            "ALVEAR, MARCELO T. De 499": ["MARCELO T DE ALVEAR 499"],
            "MORENO, JOSE MARIA AV. 100": ["AV JOSE MARIA MORENO 100"],
            "MITRE, EMILIO 433": ["EMILIO MITRE 433"],
            "SAENZ, MANUELA 343": ["MANUELA SAENZ 343"],
            "DE MAYO AV. 852": ["AV DE MAYO 852"],
            "AV. DEL LIBERTADOR SIN N\u00daMERO OFICIAL 3805": ["AV DEL LIBERTADOR 3805"],
        }

        for raw, expected_values in cases.items():
            with self.subTest(raw=raw):
                candidates = generate_f02_address_candidates(raw)
                for expected in expected_values:
                    self.assertIn(expected, candidates)

    def test_generate_f02_address_candidates_keeps_clean_addresses(self):
        cases = {
            "NICARAGUA 6048": ["NICARAGUA 6048"],
            "SALTA 380": ["SALTA 380"],
            "CORRIENTES AV. 4646": ["CORRIENTES 4646", "AV CORRIENTES 4646"],
        }

        for raw, expected_values in cases.items():
            with self.subTest(raw=raw):
                candidates = generate_f02_address_candidates(raw)
                for expected in expected_values:
                    self.assertIn(expected, candidates)

    def test_generate_f02_address_candidates_processes_multiple_addresses(self):
        candidates = generate_f02_address_candidates("MORENO, JOSE MARIA AV. 100;ROSARIO 495")

        self.assertIn("AV JOSE MARIA MORENO 100", candidates)
        self.assertIn("ROSARIO 495", candidates)

    def test_select_geocode_result_prefers_exact_source_commune_match(self):
        results = [
            GeocodeResult("DIAZ, CNEL. AV. 1944", "DIAZ 1944", "DIAZ 1944", "-34.63", "-58.43", "", "7", "calle_altura", "exacta", "2026-06-18"),
            GeocodeResult("DIAZ, CNEL. AV. 1944", "AV CORONEL DIAZ 1944", "AV CORONEL DIAZ 1944", "-34.58", "-58.41", "", "14", "calle_altura", "exacta", "2026-06-18"),
        ]

        selected = select_geocode_result(
            "DIAZ, CNEL. AV. 1944",
            ["DIAZ 1944", "CORONEL DIAZ 1944", "AV CORONEL DIAZ 1944"],
            results,
            comuna_fuente="14",
        )

        self.assertEqual(selected.direccion_consulta, "AV CORONEL DIAZ 1944")
        self.assertEqual(selected.criterio_seleccion, "exacta_comuna_coincidente")
        self.assertEqual(selected.coincide_comuna, "si")

    def test_select_geocode_result_marks_unmatched_exact_commune_as_inconsistent(self):
        result = GeocodeResult("MITRE, EMILIO 381", "MITRE 381", "MITRE 381", "-34.60", "-58.38", "", "1", "calle_altura", "exacta", "2026-06-18")

        selected = select_geocode_result("MITRE, EMILIO 381", ["MITRE 381"], [result], comuna_fuente="6")

        self.assertEqual(selected.estado, "usig_comuna_inconsistente")
        self.assertEqual(selected.latitud, "")
        self.assertEqual(selected.coincide_comuna, "no")

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

    def test_consistency_report_compares_source_commune_with_exact_usig(self):
        habilitaciones = pd.DataFrame(
            [
                {"direccion_original": "RIVADAVIA 3102", "comuna": "3"},
                {"direccion_original": "CORRIENTES 1000", "comuna": "1"},
                {"direccion_original": "SIN COMUNA 1", "comuna": "No determinada"},
            ]
        )
        cache = pd.DataFrame(
            [
                {"direccion_original": "RIVADAVIA 3102", "comuna_usig": "3", "estado": "exacta"},
                {"direccion_original": "CORRIENTES 1000", "comuna_usig": "2", "estado": "exacta"},
                {"direccion_original": "SIN COMUNA 1", "comuna_usig": "4", "estado": "exacta"},
                {"direccion_original": "NO ENTRA 1", "comuna_usig": "1", "estado": "aproximada"},
            ]
        )

        report, discrepancies = consistency_report(habilitaciones, cache)

        self.assertEqual(report["total"], 2)
        self.assertEqual(report["coincidencias"], 1)
        self.assertEqual(report["discrepancias"], 1)
        self.assertEqual(report["porcentaje_coincidencia"], 50.0)
        self.assertEqual(discrepancies.iloc[0]["direccion_original"], "CORRIENTES 1000")
        self.assertEqual(discrepancies.iloc[0]["comuna_fuente"], "1")
        self.assertEqual(discrepancies.iloc[0]["comuna_usig"], "2")


if __name__ == "__main__":
    unittest.main()
