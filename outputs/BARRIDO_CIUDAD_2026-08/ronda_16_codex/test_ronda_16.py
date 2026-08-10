# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

import pandas as pd


OUT = Path(__file__).resolve().parent
BARRIDO = OUT.parent
EVIDENCIA = BARRIDO / "desde_cowork" / "evidencia_2026"


class Ronda16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.soportes = pd.read_csv(OUT / "soportes_41.csv")
        cls.corr = pd.read_csv(OUT / "correspondencia_124_x_41.csv")
        cls.matriz = pd.read_csv(OUT / "matriz_solapamiento_41x41.csv")
        cls.positivos = pd.read_csv(OUT / "solapamientos_positivos_41.csv")
        cls.palermo = pd.read_csv(OUT / "palermo_584_contra_perimetro.csv")
        cls.informe = (OUT / "RONDA_16_CODEX.md").read_text(encoding="utf-8")

    def test_universo_y_soportes(self):
        criterio = pd.read_csv(EVIDENCIA / "criterio_admision_55.csv")
        self.assertEqual((criterio.categoria_por_criterio == "polo admitido").sum(), 41)
        self.assertEqual(len(self.soportes), 41)
        self.assertFalse(self.soportes.polo_id.duplicated().any())
        self.assertEqual(self.soportes.soporte_es_real.value_counts().to_dict(), {True: 31, False: 10})
        z54 = self.soportes.set_index("polo_id").loc["Z54"]
        z40 = self.soportes.set_index("polo_id").loc["Z40"]
        self.assertTrue(z54.soporte_es_real)
        self.assertEqual(z54.soporte_id, "P024")
        self.assertFalse(z40.soporte_es_real)

    def test_correspondencia_124_x_41(self):
        self.assertEqual(self.corr.concentracion_id.nunique(), 124)
        inter = self.corr[self.corr.fila_tipo == "INTERSECCION"]
        self.assertEqual(len(inter), 143)
        self.assertEqual((inter.bloque == "PUBLICABLE").sum(), 95)
        self.assertEqual((inter.bloque == "PENDIENTE_DE_PERIMETRO").sum(), 48)
        self.assertTrue(inter.soporte_es_real_A.eq(True).all())
        self.assertTrue(
            inter.loc[inter.bloque == "PUBLICABLE", "soporte_es_real_B"].astype(bool).all()
        )

    def test_matriz_completa_y_gate_provisorio(self):
        self.assertEqual(len(self.matriz), 820)
        self.assertFalse(self.matriz[["polo_A", "polo_B"]].duplicated().any())
        provisorio = ~(self.matriz.soporte_es_real_A & self.matriz.soporte_es_real_B)
        self.assertTrue(self.matriz.loc[provisorio, "clase"].eq("PENDIENTE DE PERÍMETRO").all())
        self.assertTrue(
            self.matriz.loc[provisorio, "gate_recomendacion"]
            .eq("BLOQUEADO: PENDIENTE DE PERÍMETRO")
            .all()
        )
        reales = ~provisorio
        self.assertFalse(self.matriz.loc[reales, "clase"].eq("PENDIENTE DE PERÍMETRO").any())
        esperado = self.matriz[self.matriz.interseccion_m2 > 0.01].reset_index(drop=True)
        pd.testing.assert_frame_equal(self.positivos, esperado, check_dtype=False)

    def test_z54_bloqueada_y_z51_disjunta(self):
        def par(a, b):
            x = self.matriz[
                ((self.matriz.polo_A == a) & (self.matriz.polo_B == b))
                | ((self.matriz.polo_A == b) & (self.matriz.polo_B == a))
            ]
            self.assertEqual(len(x), 1)
            return x.iloc[0]

        z54 = par("Z40", "Z54")
        self.assertAlmostEqual(z54.interseccion_m2, 504_234.5331, places=2)
        self.assertEqual(z54.relacion_observada, "CONTENIDA")
        self.assertEqual(z54.clase, "PENDIENTE DE PERÍMETRO")
        self.assertEqual(z54.locales_compartidos, 95)

        for candidato in ("Z50", "R11"):
            z51 = par("Z51", candidato)
            self.assertEqual(z51.clase, "DISJUNTA")
            self.assertEqual(z51.interseccion_m2, 0)
            self.assertEqual(z51.locales_compartidos, 0)

    def test_palermo_584_y_continuidad(self):
        self.assertEqual(set(self.palermo.concentracion_id), {"P073", "P087", "P092", "P088", "P064", "P104"})
        self.assertEqual(self.palermo.locales_capa_124.sum(), 584)
        self.assertEqual(self.palermo.locales_ERR10_en_geometria.sum(), 582)
        self.assertTrue(self.palermo.interseccion_con_sistema_m2.eq(0).all())
        continuas = set(self.palermo.loc[self.palermo.continuidad_40m, "concentracion_id"])
        self.assertEqual(continuas, {"P088", "P092"})
        self.assertTrue(
            self.palermo.decision_delimitacion.eq(
                "PENDIENTE_DIEGO; SIN_PROPUESTA_DE_AMPLIACION"
            ).all()
        )

    def test_documento_se_deriva_de_las_tablas(self):
        inter_corr = self.corr[self.corr.fila_tipo == "INTERSECCION"]
        positivos = self.matriz[self.matriz.interseccion_m2 > 0.01]
        positivos_reales = positivos[
            positivos.soporte_es_real_A & positivos.soporte_es_real_B
        ]
        pendientes = self.matriz[self.matriz.clase == "PENDIENTE DE PERÍMETRO"]
        controles = [
            f"**{len(inter_corr)} pares**",
            f"**{(inter_corr.bloque == 'PUBLICABLE').sum()} publicables**",
            f"**{(inter_corr.bloque == 'PENDIENTE_DE_PERIMETRO').sum()} pendientes de perímetro**",
            f"**{len(positivos)}** pares con intersección",
            f"**{len(positivos_reales)}** tienen ambos soportes reales",
            f"**{len(pendientes)}** pares quedan clasificados",
        ]
        for texto in controles:
            self.assertIn(texto, self.informe)
        self.assertIn("No se emite recomendación", self.informe)

    def test_anexo_b_cierra_nota_y_fuentes_intactas(self):
        anexo = (EVIDENCIA / "ANEXO_B_LAS_124_CONCENTRACIONES.md").read_text(encoding="utf-8")
        self.assertIn("correspondencia_124_x_41.csv", anexo)
        self.assertNotIn("están pendientes de recalcularse", anexo)
        hashes = pd.read_csv(OUT / "insumos_sha256.csv")
        self.assertTrue(hashes.sin_cambios.all())
        self.assertTrue((hashes.sha256_antes == hashes.sha256_despues).all())


if __name__ == "__main__":
    unittest.main()
