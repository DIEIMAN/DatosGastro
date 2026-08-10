# -*- coding: utf-8 -*-
import csv
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
EVIDENCIA = BARRIDO / "desde_cowork" / "evidencia_2026"
OUT = BARRIDO / "ronda_15_codex"


class Ronda15Tests(unittest.TestCase):
    def test_err17_corpus_y_conteo_institucional(self):
        corpus = pd.read_csv(EVIDENCIA / "fichas_corpus_polos.csv", encoding="utf-8-sig")
        self.assertEqual(len(corpus), 53)
        self.assertFalse(corpus["polo_id"].duplicated().any())
        self.assertTrue({"Z50", "Z51", "Z52", "Z53", "Z54"}.issubset(set(corpus["polo_id"])))
        criterio = pd.read_csv(EVIDENCIA / "criterio_admision_55.csv", encoding="utf-8-sig")
        self.assertEqual((criterio["categoria_por_criterio"] == "polo admitido").sum(), 41)

    def test_err18(self):
        corpus = pd.read_csv(EVIDENCIA / "fichas_corpus_polos.csv", encoding="utf-8-sig")
        esperados = {"R02": 4, "R04": 4, "R05": 5, "R19": 4, "Z37": 5,
                     "Z50": 4, "Z51": 3, "Z52": 2, "Z53": 2, "Z54": 2}
        obtenidos = corpus.set_index("polo_id").loc[list(esperados), "n_vias"].astype(int).to_dict()
        self.assertEqual(obtenidos, esperados)

    def test_err19(self):
        with (EVIDENCIA / "via_E_22_referencias.csv").open(encoding="utf-8-sig", newline="") as fh:
            filas = list(csv.reader(fh))
        self.assertEqual({len(f) for f in filas}, {10})
        r03 = next(f for f in filas if f[0] == "R03")
        self.assertEqual(r03[8:], ["6", "2026-08-07"])

    def test_reparto_mueve_solo_el_contrafactico(self):
        reparto = pd.read_csv(OUT / "reparto_sur.csv", encoding="utf-8-sig")
        n_fusiones = reparto.loc[reparto["clase_reparto"] == "CONTENIDA", "zona_id"].nunique()
        esperado = 41 - n_fusiones
        self.assertTrue((reparto["conteo_polos_admitidos_vigente"] == 41).all())
        self.assertTrue((reparto["conteo_si_Diego_firma_recomendaciones"] == esperado).all())
        informe = (OUT / "RONDA_15_CODEX.md").read_text(encoding="utf-8")
        self.assertIn("continúa en **41 polos admitidos**", informe)
        self.assertIn(f"contrafáctico pasa a **{esperado}**", informe)

    def test_z55_no_cambia_mapa_con_una_sola_via(self):
        criterio = pd.read_csv(EVIDENCIA / "criterio_admision_55.csv", encoding="utf-8-sig")
        z55 = criterio.loc[criterio["polo_id"] == "Z55"].iloc[0]
        self.assertEqual(z55["C1_umbral"], "NO CUMPLE")
        self.assertNotEqual(z55["categoria_por_criterio"], "polo admitido")
        fuentes = pd.read_csv(OUT / "z55_fuentes_publicas.csv", encoding="utf-8-sig")
        self.assertEqual(fuentes["coincidencias_Mariano_Acosta_Janer"].sum(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
