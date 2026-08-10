from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


class EntregaTest(unittest.TestCase):
    def test_archivos_requeridos(self) -> None:
        expected = {
            "vigencia_historicos_ronda_19.csv", "verificacion_locales_ronda_19.csv",
            "ejes_comerciales_control.csv", "INFORME.md",
        }
        self.assertTrue(expected.issubset({p.name for p in OUT.iterdir()}))

    def test_historicos(self) -> None:
        data = rows("vigencia_historicos_ronda_19.csv")
        self.assertEqual(len(data), 54)
        self.assertEqual(len({r["nombre"] for r in data}), 54)
        self.assertEqual(sum(r["es_de_los_42"] == "si" for r in data), 12)
        self.assertTrue(all(r["es_de_los_42"] == "si" for r in data[:12]))
        self.assertTrue(all(r["es_de_los_42"] == "no" for r in data[12:]))
        self.assertEqual(sum(r["nivel_resultante"] == "v2" for r in data), 48)
        self.assertEqual(sum(r["nivel_resultante"] == "v1" for r in data), 6)
        self.assertFalse(any(r["resultado"] == "cerrado_a_fecha_fuente" for r in data))
        self.assertTrue(all(r["fecha_nueva"] and r["fuente_nueva"].startswith("https://")
                            for r in data if r["nivel_resultante"] == "v2"))

    def test_locales(self) -> None:
        data = rows("verificacion_locales_ronda_19.csv")
        self.assertEqual(len(data), 19)
        improved = {r["nombre"] for r in data if r["estado"] == "abierto_a_fecha_fuente"}
        self.assertEqual(improved, {"Brest Patisserie", "Bulmat", "Ichiban", "Matok"})
        self.assertFalse(any("cerrad" in r["estado"].lower() for r in data))
        self.assertEqual(sum(r["estado"] == "vigencia_no_verificada" for r in data), 15)

    def test_conflictos(self) -> None:
        data = {r["establecimiento"]: r for r in rows("conflictos_direccion_ronda_19.csv")}
        self.assertEqual(set(data), {"La Mezzetta", "San Carlos", "Saverio"})
        self.assertTrue(data["La Mezzetta"]["direccion_adoptada"].endswith("1321"))
        self.assertTrue(data["San Carlos"]["direccion_adoptada"].endswith("4548"))
        self.assertTrue(data["Saverio"]["direccion_adoptada"].endswith("2809"))
        self.assertIn("pendiente", data["Saverio"]["estado_resolucion"])

    def test_ejes(self) -> None:
        data = rows("ejes_comerciales_control.csv")
        self.assertEqual(list(data[0]), [
            "pagina", "eje_citado", "eje_en_la_fuente", "valor_citado",
            "valor_en_la_fuente", "anio", "coincide", "superlativo_citado",
            "superlativo_correcto",
        ])
        self.assertEqual(len(data), 90)
        self.assertEqual(sum("no en unidad" in r["coincide"] for r in data), 11)
        wrong = {(r["pagina"], r["eje_citado"]) for r in data
                 if r["superlativo_correcto"].startswith("no:")}
        self.assertEqual(wrong, {
            ("R09 · Federico Lacroze", "Colegiales"),
            ("Z43 · Colegiales", "Colegiales"),
            ("Z42 · La Paternal", "Warnes"),
        })
        liniers = next(r for r in data if r["eje_en_la_fuente"] == "Liniers"
                       and r["valor_citado"].startswith("variacion_interanual="))
        self.assertIn("0.039463", liniers["valor_en_la_fuente"])
        warnes = next(r for r in data if r["eje_en_la_fuente"] == "Warnes"
                      and r["valor_citado"].startswith("variacion_interanual="))
        self.assertIn("-6.830396", warnes["valor_en_la_fuente"])

    def test_prosa_y_privacidad(self) -> None:
        targets = [
            "vigencia_historicos_ronda_19.csv", "verificacion_locales_ronda_19.csv",
            "conflictos_direccion_ronda_19.csv", "ejes_comerciales_control.csv", "INFORME.md",
        ]
        content = "\n".join((OUT / name).read_text(encoding="utf-8-sig") for name in targets)
        self.assertIsNone(re.search(r"\b(?:barrido|ronda)\b", content, re.I))
        self.assertIsNone(re.search(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", content))
        self.assertIsNone(re.search(r"(?i)(api[_-]?key|secret[_-]?key|bearer\s+[a-z0-9._-]{12,})", content))
        self.assertNotIn("file://", content.lower())
        self.assertNotIn("C:\\", content)
        report = (OUT / "INFORME.md").read_text(encoding="utf-8")
        self.assertTrue(report.startswith("# Valores que cambiaron"))
        self.assertIn("## Pendientes explícitos", report)
        self.assertIn("No se modificaron fuentes originales", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
