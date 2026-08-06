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

    def test_el_marcador_en_el_MEDIO_que_dejo_la_desinversion(self):
        """El bicho que encontró el inventario, y es la continuación directa de Niceto Vega.

        «CALVO, CARLOS AV.» trae el marcador al final del último segmento. Al dar vuelta los
        segmentos queda «CARLOS AV. CALVO» —con el «AV.» en el MEDIO—, donde ninguna regla de
        extremos lo alcanza. El inventario lo encontró en 23 avenidas, siempre partiendo la calle
        en dos filas de tamaño parecido, que es la forma más difícil de notar a ojo.
        """
        for variante in ("CALVO, CARLOS AV. 819", "Av. Carlos Calvo 819", "Carlos Calvo 819"):
            with self.subTest(variante=variante):
                self.assertEqual(calle(variante), "CARLOS CALVO")
        self.assertEqual(calle("ALBERDI, JUAN BAUTISTA AV. 1200"), "JUAN BAUTISTA ALBERDI")
        self.assertEqual(calle("Avenida Juan Bautista Alberdi 1200"), "JUAN BAUTISTA ALBERDI")

    def test_el_marcador_pegado_al_punto_sin_espacio(self):
        """«AV.SAN MARTIN» viene sin espacio detrás del punto: el punto separa igual que el espacio."""
        self.assertEqual(calle("AV.SAN MARTIN 2500"), "SAN MARTIN")
        self.assertEqual(calle(".FRANCISCO BEIRO 3400"), "FRANCISCO BEIRO")

    def test_tratamientos_abreviados_y_largos_pliegan(self):
        """«TTE. GRAL.» y «Teniente General» son lo mismo, y el campo trae las cuatro grafías."""
        for variante in ("TTE. GENERAL JUAN DOMINGO PERON 1500",
                         "Teniente General Juan Domingo Perón 1500",
                         "TTE. GRAL. JUAN DOMINGO PERON 1500"):
            with self.subTest(variante=variante):
                self.assertEqual(calle(variante), "JUAN DOMINGO PERON")
        self.assertEqual(calle("MCAL. ANTONIO JOSE DE SUCRE 2200"),
                         calle("Mariscal Antonio José de Sucre 2200"))

    def test_el_token_entero_impide_que_vuelva_el_bug_de_esquiu(self):
        """El caso negativo del cambio de posición libre, y es el que lo vuelve seguro.

        Sacar marcadores de cualquier posición sería exactamente el bug de «Esquiu» si la
        comparación fuera por prefijo. Es por token entero contra un conjunto, así que no puede.
        """
        self.assertEqual(calle("AVELLANEDA 1200"), "AVELLANEDA")
        self.assertEqual(calle("Presidencia 100"), "PRESIDENCIA")
        self.assertEqual(calle("General Paz 200"), "PAZ")          # sí es tratamiento
        self.assertEqual(calle("Generala 200"), "GENERALA")        # no lo es

    def test_mojibake_de_dos_vueltas(self):
        """«Arribeños» pasada dos veces por la conversión equivocada, y el caso negativo."""
        self.assertEqual(calle("ARRIBEÃâOS 2290"), "ARRIBENOS")
        self.assertEqual(calle("Arribeños 2290"), "ARRIBENOS")
        # NEGATIVO: un texto sano vuelve intacto porque no decodifica como UTF-8.
        self.assertEqual(calle("Cañitas 100"), "CANITAS")
        self.assertEqual(calle("Peña 2400"), "PENA")

    def test_codigo_postal_pegado_al_nombre(self):
        """«BARTOLOME MITRE C1201AAX» trae el CPA donde iría la altura."""
        self.assertEqual(calle("BARTOLOME MITRE C1201AAX"), "BARTOLOME MITRE")
        self.assertEqual(calle("JULIAN ALVAREZ C1414DRJ"), "JULIAN ALVAREZ")

    def test_conector_colgando_en_la_cola(self):
        """«11 de Septiembre de 1888» pierde el año junto con la altura y termina en «DE»."""
        self.assertEqual(calle("11 de Septiembre de 1888 2200"), "11 DE SEPTIEMBRE")
        self.assertEqual(calle("11 de Septiembre 2200"), "11 DE SEPTIEMBRE")

    def test_no_se_recorta_el_conector_de_adelante(self):
        """Caso negativo del anterior: «De los Constituyentes» empieza así de verdad."""
        self.assertEqual(calle("De los Constituyentes 3200"), "DE LOS CONSTITUYENTES")
        self.assertEqual(calle("Del Libertador 4500"), "DEL LIBERTADOR")

    def test_las_iniciales_NO_se_tocan_y_es_una_decision(self):
        """El residuo declarado. No es un olvido: es que no se puede resolver sin callejero.

        «RAMON L. FALCON» y «RAMON FALCON» son la misma calle y siguen contándose aparte. Tirar
        las letras sueltas los uniría — y rompería «S. MARTIN», que es *San* Martín y no la
        inicial de un nombre. Las dos formas son indistinguibles sin una fuente canónica.
        """
        self.assertEqual(calle("RAMON L. FALCON 2400"), "RAMON L FALCON")
        self.assertEqual(calle("S. MARTIN 1200"), "S MARTIN")


if __name__ == "__main__":
    unittest.main()
