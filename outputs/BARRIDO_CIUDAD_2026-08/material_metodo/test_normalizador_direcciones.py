"""Regresión de la limpieza de direcciones que se manda a USIG.

POR QUÉ ESTE TEST EXISTE
------------------------
El caso «Esquiu 1393» es el motivo. La limpieza convertía `esq.` y `esquina` en « y » con una
expresión regular sin límite de palabra, así que **`esq` matcheaba adentro de «Esquiu»** y la
dirección salía como « y iu 1393». USIG no la resolvía, la fila aparecía «sin resolver», y la
falla parecía del servicio externo.

Es la clase de bug más cara de encontrar: no rompe nada, no tira excepción, y produce un resultado
que se explica solo con una hipótesis equivocada («el normalizador no la tiene»). Por eso queda
como test y no como comentario.

Los otros dos casos son los que aparecieron en la misma corrida y subieron el resuelto del 93,7 %
al 96,8 %: los rangos de altura con barras y las colas de país sin punto separador.

Y un caso NEGATIVO que también importa: «Ciudad de la Paz» es una calle de Belgrano. Cortar por
«Ciudad» a secas la decapitaría, así que el corte es por «Ciudad Autónoma».

  .venv/Scripts/python.exe -m unittest tests.test_normalizador_direcciones -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))

from dataset_bares_notables import limpiar  # noqa: E402
from polos_foco_menor import calle  # noqa: E402


class LimpiezaDeDirecciones(unittest.TestCase):

    def test_esq_no_matchea_adentro_de_una_calle(self):
        """El bug original: `esq` adentro de «Esquiu» la convertía en « y iu»."""
        self.assertEqual(limpiar("Esquiu 1393"), "Esquiu 1393")

    def test_otras_calles_que_empiezan_como_esquina(self):
        """La familia entera del mismo bug, no sólo el caso que apareció."""
        for direccion in ("Esquiu 1393", "Esquiú 1393", "Esquina 500"):
            with self.subTest(direccion=direccion):
                self.assertNotIn(" y ", limpiar(direccion))

    def test_esquina_de_verdad_si_se_convierte(self):
        """Y el reemplazo tiene que seguir funcionando cuando SÍ es una esquina."""
        self.assertEqual(limpiar("Corrientes esq. Callao"), "Corrientes y Callao")
        self.assertEqual(limpiar("Corrientes esquina Callao"), "Corrientes y Callao")

    def test_rango_de_alturas_con_barras(self):
        """«1148/50/52» → «1148»: USIG no entiende el rango y se queda con la primera."""
        self.assertEqual(limpiar("Av. de Mayo 1148/50/52"), "Av. de Mayo 1148")

    def test_cola_de_pais_con_y_sin_punto(self):
        """La cola llega de las dos formas y las dos hay que cortarlas."""
        self.assertEqual(
            limpiar("Avenida de Mayo 825. Ciudad Autónoma de Buenos Aires. Argentina"),
            "Avenida de Mayo 825")
        self.assertEqual(
            limpiar("Avenida de Mayo 599 Ciudad Autónoma de Buenos Aires Argentina"),
            "Avenida de Mayo 599")

    def test_no_se_corta_por_la_palabra_ciudad_sola(self):
        """Caso negativo: «Ciudad de la Paz» es una calle de Belgrano y no se puede decapitar."""
        self.assertEqual(limpiar("Ciudad de la Paz 2400"), "Ciudad de la Paz 2400")

    def test_direccion_vacia_no_rompe(self):
        self.assertEqual(limpiar(None), "")
        self.assertEqual(limpiar(""), "")


class ClaveDeCalle(unittest.TestCase):
    """La clave con la que se agrupan calles para describir un foco.

    Apareció midiendo el foco menor de P103: el mismo campo trae «INDEPENDENCIA AV.» y «Avenida
    Independencia», y sin plegar las dos convenciones una calle se cuenta como dos. No rompe nada
    —de nuevo—: devuelve dos filas plausibles donde hay una, y el ranking de calles sale mal.
    """

    def test_las_tres_convenciones_pliegan_a_la_misma_clave(self):
        for variante in ("INDEPENDENCIA AV. 821", "Avenida Independencia 734",
                         "Av. Independencia 691", "independencia 700"):
            with self.subTest(variante=variante):
                self.assertEqual(calle(variante), "INDEPENDENCIA")

    def test_apellido_invertido_con_coma(self):
        """«CALVO, CARLOS 819» y «Carlos Calvo 819» son la misma calle."""
        self.assertEqual(calle("CALVO, CARLOS 819"), calle("Carlos Calvo 819"))
        self.assertEqual(calle("CALVO, CARLOS 819"), "CARLOS CALVO")

    def test_el_marcador_no_matchea_adentro_de_una_calle(self):
        """El caso negativo, que es de la familia de «Esquiu».

        «Avellaneda» empieza con «Av» y no es una avenida abreviada. Un prefijo sin límite de
        palabra la dejaría en «ELLANEDA», que es exactamente el bug original con otra ropa.
        """
        self.assertEqual(calle("AVELLANEDA 1200"), "AVELLANEDA")
        self.assertEqual(calle("Avda. Avellaneda 1200"), "AVELLANEDA")

    def test_tildes_y_tratamientos_pliegan(self):
        """Aparecieron midiendo P078: «Arévalo»/«Arevalo» y cuatro grafías de Niceto Vega."""
        self.assertEqual(calle("Arévalo 1500"), calle("Arevalo 1500"))
        self.assertEqual(calle("Cnel. Niceto Vega 5100"), calle("Coronel Niceto Vega 5100"))
        self.assertEqual(calle("Coronel Niceto Vega 5100"), "NICETO VEGA")

    def test_inversion_con_mas_de_una_coma(self):
        """El caso real que rompía el conteo de P078.

        «VEGA, NICETO, Cnel. AV.» es Avenida Coronel Niceto Vega. Con un solo `split(",", 1)` la
        calle quedaba como «NICETO, CNEL. VEGA» y se contaba aparte de «Niceto Vega»: la misma
        calle en dos filas, cada una con la mitad de los locales.
        """
        for variante in ("VEGA, NICETO, Cnel. AV. 5534", "Avenida Coronel Niceto Vega 5702",
                         "Niceto Vega 5572", "NICETO VEGA AV. 5600"):
            with self.subTest(variante=variante):
                self.assertEqual(calle(variante), "NICETO VEGA")

    def test_el_tratamiento_no_matachea_adentro_de_una_calle(self):
        """Caso negativo del mismo tipo: «General Paz» sí lleva tratamiento, «Genoveva» no."""
        self.assertEqual(calle("Genoveva 100"), "GENOVEVA")
        self.assertEqual(calle("Drago 700"), "DRAGO")

    def test_se_queda_con_la_primera_de_una_direccion_doble(self):
        """El padrón asienta frentes de esquina en un solo campo: «CHILE 700;CHACABUCO 706»."""
        self.assertEqual(calle("CHILE 700;CHACABUCO 706"), "CHILE")


if __name__ == "__main__":
    unittest.main()
