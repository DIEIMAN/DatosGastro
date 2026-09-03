"""Regresiones de deduplicacion del constructor de Casas de Pastas."""
import unittest

from scripts.casas_pastas.build_casas_pastas import establecimiento_key


def fila(nombre="", direccion="", identificador="1", rubro="FABRICA DE PASTAS"):
    return {
        "nombre_original": nombre,
        "direccion_original": direccion,
        "fuente": "F02",
        "id_registro_original": identificador,
        "rubro_original": rubro,
    }


class DeduplicacionCasasPastasTest(unittest.TestCase):
    def test_no_fusiona_anonimos_de_distintas_alturas(self):
        a = fila(direccion="ENTRE RIOS AV. 629", identificador="10")
        b = fila(direccion="ENTRE RIOS AV. 2186", identificador="20")
        self.assertNotEqual(establecimiento_key(a), establecimiento_key(b))

    def test_no_fusiona_sucursales_de_una_marca_en_la_misma_calle(self):
        a = fila(nombre="La Juvenil", direccion="AV. CORRIENTES 5064")
        b = fila(nombre="La Juvenil", direccion="AV. CORRIENTES 5590")
        self.assertNotEqual(establecimiento_key(a), establecimiento_key(b))

    def test_si_fusiona_mismo_nombre_y_domicilio_normalizados(self):
        a = fila(nombre="Gusmar Hnos.", direccion="CIUDAD DE LA PAZ 896")
        b = fila(nombre="GUSMAR HNOS", direccion="Ciudad de la Paz 896")
        self.assertEqual(establecimiento_key(a), establecimiento_key(b))

    def test_f02_usa_reedicion_como_enriquecimiento_del_mismo_registro(self):
        legacy = fila(nombre="", direccion="CIUDAD DE LA PAZ 896", identificador="123")
        reedicion = fila(nombre="Gusmar Hnos.", direccion="Ciudad de la Paz 896",
                         identificador="123")
        self.assertEqual(establecimiento_key(legacy), establecimiento_key(reedicion))

    def test_f02_no_fusiona_partidas_distintas_en_una_misma_puerta(self):
        a = fila(direccion="CALLE 123", identificador="10")
        b = fila(direccion="CALLE 123", identificador="20")
        self.assertNotEqual(establecimiento_key(a), establecimiento_key(b))

    def test_sin_domicilio_no_colapsa_ids_distintos(self):
        self.assertNotEqual(
            establecimiento_key(fila(identificador="10")),
            establecimiento_key(fila(identificador="20")),
        )


if __name__ == "__main__":
    unittest.main()
