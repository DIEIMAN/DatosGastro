from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from normalize_categories import classify_gastronomic_category


class ClassifyGastronomicCategoryTest(unittest.TestCase):
    def test_talabarteria_marroquineria_is_not_bar(self):
        result = classify_gastronomic_category(
            "COM.MIN.DE CALZADOS EN GRAL., ART.DE CUERO. TALABARTERIA, MARROQUINERIA"
        )

        self.assertEqual(result.es_gastronomico, "no")
        self.assertEqual(result.categoria_gastronomica_inferida, "No gastronomico")

    def test_envasados_is_comercio_alimenticio_not_parrilla(self):
        result = classify_gastronomic_category("com.min. de productos alimenticios envasados")

        self.assertEqual(result.es_gastronomico, "no")
        self.assertEqual(result.categoria_gastronomica_inferida, "Comercio alimenticio minorista")
        self.assertNotEqual(result.categoria_gastronomica_inferida, "Parrilla")

    def test_publicidad_is_not_pub(self):
        result = classify_gastronomic_category("empresa de publicidad")

        self.assertEqual(result.es_gastronomico, "no")
        self.assertEqual(result.categoria_gastronomica_inferida, "No gastronomico")

    def test_excluded_feria_mercado_is_comercio_alimenticio_not_feria(self):
        result = classify_gastronomic_category(
            "local de venta de productos alimenticios y/o bebidas (excluido feria, mercado...)"
        )

        self.assertEqual(result.es_gastronomico, "no")
        self.assertEqual(result.categoria_gastronomica_inferida, "Comercio alimenticio minorista")
        self.assertNotEqual(result.categoria_gastronomica_inferida, "Feria")

    def test_bar_cafe_is_service_gastronomy(self):
        result = classify_gastronomic_category("bar cafe")

        self.assertEqual(result.es_gastronomico, "si")
        self.assertIn(result.categoria_gastronomica_inferida, {"Bar", "Cafe"})

    def test_restaurante_cantina_is_restaurante(self):
        result = classify_gastronomic_category("restaurante cantina")

        self.assertEqual(result.es_gastronomico, "si")
        self.assertEqual(result.categoria_gastronomica_inferida, "Restaurante")


if __name__ == "__main__":
    unittest.main()
