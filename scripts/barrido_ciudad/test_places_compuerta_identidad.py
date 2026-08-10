"""Test de la compuerta de identidad, contra los casos REALES que ya se pagaron.

Los cuatro de la escalera de la ronda 9 son el banco de pruebas, porque de los cuatro sabemos la
respuesta correcta por evidencia documental independiente:

    Papa Frita      Places devolvió el establecimiento preguntado   → ACEPTAR
    Carruajes       devolvió el preguntado, en otra calle           → ACEPTAR (misma sede)
    Castelar        «EX Hotel Castelar.» + OPERATIONAL              → RECHAZAR (contradicción)
    Perla del Once  devolvió «La Americana»                         → RECHAZAR (otro negocio)

**El que decide es el cuarto.** Una compuerta que lo acepte no sirve para nada: es exactamente el
error que invalidó la ronda 8.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from places_compuerta_identidad import (  # noqa: E402
    CAMPOS_MINIMOS,
    compuerta,
    contradiccion,
    parecido_de_nombre,
    validar_mascara,
)


def _c(nombre, direccion, estado):
    return {"displayName": {"text": nombre}, "formattedAddress": direccion,
            "businessStatus": estado}


class LaMascara(unittest.TestCase):
    def test_la_mascara_minima_pasa(self):
        validar_mascara(CAMPOS_MINIMOS)

    def test_la_mascara_de_la_ronda_8_es_rechazada(self):
        """Es la que invalidó 71 requests. Ahora corta antes de gastar el primero."""
        with self.assertRaises(ValueError):
            validar_mascara(["places.businessStatus", "places.formattedAddress",
                             "places.regularOpeningHours"])


class LosCuatroCasosReales(unittest.TestCase):
    def test_papa_frita_se_acepta(self):
        r = compuerta("El Palacio de la Papa Frita", "Av. Corrientes 1612",
                      [_c("El Palacio de la Papa Frita",
                          "Av. Corrientes 1612, C1042 AAP, Cdad. Autónoma de Buenos Aires",
                          "OPERATIONAL")])
        self.assertEqual(r["veredicto"], "aceptado")
        self.assertEqual(r["business_status"], "OPERATIONAL")

    def test_la_perla_del_once_se_RECHAZA(self):
        """EL TEST QUE DECIDE. Places devolvió el comercio que ocupa hoy el local."""
        r = compuerta("La Perla del Once", "Av. Rivadavia 2800",
                      [_c("La Americana, La Reina de las Empanadas",
                          "Av. Rivadavia 2800, C1083ACT Cdad. Autónoma de Buenos Aires",
                          "OPERATIONAL")])
        self.assertEqual(r["veredicto"], "RECHAZADO")
        self.assertEqual(r["business_status"], "", "un rechazado NO puede dejar estado")

    def test_castelar_se_RECHAZA_por_contradiccion(self):
        """(d) el nombre dice EX y el estado dice OPERATIONAL: no hay dato."""
        r = compuerta("Confitería del Hotel Castelar", "Av. de Mayo 1152",
                      [_c("EX Hotel Castelar.",
                          "Av. de Mayo 1150, C1085ABO, Cdad. Autónoma de Buenos Aires",
                          "OPERATIONAL")])
        self.assertEqual(r["veredicto"], "RECHAZADO")
        self.assertIn("contradicción", r["motivo"])

    def test_carruajes_se_acepta_por_nombre_pese_a_la_calle(self):
        """Devolvió el establecimiento preguntado con su propio nombre y su propio cierre."""
        r = compuerta("Mercado de los Carruajes", "Av. Leandro N. Alem 852",
                      [_c("Mercado de los Carruajes",
                          "Av. Leandro N. Alem 852, C1001AAQ, Cdad. Autónoma de Buenos Aires",
                          "CLOSED_PERMANENTLY")])
        self.assertEqual(r["veredicto"], "aceptado")
        self.assertEqual(r["business_status"], "CLOSED_PERMANENTLY")


class LosCasosDeLaRonda8QueFuncionaban(unittest.TestCase):
    """La compuerta no puede romper las diez coincidencias buenas que el control ya resolvía."""

    def test_misma_cuadra_se_acepta(self):
        r = compuerta("El Tokio", "Av. Alvarez Jonte 3550",
                      [_c("El Tokio", "Av. Álvarez Jonte 3548, Cdad. Autónoma de Buenos Aires",
                          "OPERATIONAL")])
        self.assertEqual(r["veredicto"], "aceptado")

    def test_parentesis_aclaratorio_no_rompe_el_nombre(self):
        r = compuerta("Los Galgos (Callao 501)", "Av. Callao 501",
                      [_c("Los Galgos", "Av. Callao 501, Cdad. Autónoma de Buenos Aires",
                          "OPERATIONAL")])
        self.assertEqual(r["veredicto"], "aceptado")

    def test_crizia_la_unica_falla_real_se_RECHAZA(self):
        """De 71 dejó una sola alarma verdadera. Tiene que seguir siendo rechazo."""
        r = compuerta("Crizia", "Gorriti 5143",
                      [_c("Crizia", "Fitz Roy 1819, Cdad. Autónoma de Buenos Aires",
                          "OPERATIONAL")])
        self.assertEqual(r["veredicto"], "RECHAZADO")


class LaDesambiguacionEntreCandidatos(unittest.TestCase):
    """(c) se piden varios y se elige. Con uno solo esto no se podía hacer."""

    def test_elige_al_establecimiento_entre_varios(self):
        r = compuerta("La Perla", "Av. Don Pedro de Mendoza 1899",
                      [_c("La Americana", "Av. Rivadavia 2800, Cdad. Autónoma de Buenos Aires",
                          "OPERATIONAL"),
                       _c("La Perla", "Av. Don Pedro de Mendoza 1895, Cdad. Autónoma de Buenos "
                          "Aires", "OPERATIONAL")])
        self.assertEqual(r["veredicto"], "aceptado")
        self.assertEqual(r["nombre_devuelto"], "La Perla")

    def test_dos_igual_de_buenos_con_estados_distintos_se_RECHAZA(self):
        r = compuerta("La Perla", "Av. Don Pedro de Mendoza 1899",
                      [_c("La Perla", "Av. Don Pedro de Mendoza 1899, CABA", "OPERATIONAL"),
                       _c("La Perla", "Av. Don Pedro de Mendoza 1895, CABA",
                          "CLOSED_PERMANENTLY")])
        self.assertEqual(r["veredicto"], "RECHAZADO")
        self.assertIn("reproducible", r["motivo"])


class LasPiezasSueltas(unittest.TestCase):
    def test_parecido_distingue_los_dos_casos_que_importan(self):
        self.assertGreater(parecido_de_nombre("Los Galgos (Callao 501)", "Los Galgos"), 0.34)
        self.assertLess(parecido_de_nombre("La Perla del Once",
                                           "La Americana, La Reina de las Empanadas"), 0.34)

    def test_la_contradiccion_se_detecta(self):
        self.assertIsNotNone(contradiccion("EX Hotel Castelar.", "OPERATIONAL"))
        self.assertIsNone(contradiccion("Hotel Castelar", "OPERATIONAL"))
        self.assertIsNone(contradiccion("EX Hotel Castelar.", "CLOSED_PERMANENTLY"))

    def test_sin_candidatos_es_rechazo_no_dato_vacio(self):
        r = compuerta("Lo Que Sea", "Calle Falsa 123", [])
        self.assertEqual(r["veredicto"], "RECHAZADO")


if __name__ == "__main__":
    unittest.main(verbosity=2)
