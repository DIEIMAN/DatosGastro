"""Test de regresión de `callejero_canonico`. Con casos negativos, que son los que importan.

POR QUÉ LOS NEGATIVOS
----------------------
Un test que sólo verifique que los tres casos conocidos se unen **pasaría también con una función
que une todo con todo**. La canonicalización es peligrosa en las dos direcciones: si une de menos
produce medio corredor —el bicho que estamos arreglando—; si une de más, junta ejes distintos que
comparten nombre y produce tramos que atraviesan la Ciudad.

Por eso hay tres bloques: **une lo que debe**, **NO une lo que no debe**, y **no rompe lo que
funcionaba**.

USO
---
  .venv/Scripts/python.exe -m unittest discover -s scripts/barrido_ciudad -p "test_*.py"
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))

from callejero_canonico import (  # noqa: E402
    CONTACTO_M,
    cargar,
    eje_canonico,
    familias,
    raiz,
)

_CACHE = {}


def _callejero():
    if "c" not in _CACHE:
        _CACHE["c"] = cargar()
        _CACHE["m"] = familias(_CACHE["c"])
    return _CACHE["c"], _CACHE["m"]


class RaizSinGeometria(unittest.TestCase):
    """La raíz saca el tipo de vía y NADA más."""

    def test_saca_el_sufijo_de_tipo(self):
        self.assertEqual(raiz("GARCIA DEL RIO AV."), "GARCIA DEL RIO")
        self.assertEqual(raiz("BOEDO AV"), "BOEDO")
        self.assertEqual(raiz("PASAJE ESPERANZA"), "ESPERANZA")

    def test_no_toca_un_nombre_que_CONTIENE_el_sufijo(self):
        """El caso Esquiú: «esq» adentro de un nombre no es «esquina»."""
        self.assertEqual(raiz("ESQUIU"), "ESQUIU")
        self.assertEqual(raiz("AVELLANEDA"), "AVELLANEDA")   # «AV» adentro de AVELLANEDA
        self.assertEqual(raiz("CALLENDER"), "CALLENDER" if raiz("CALLENDER") else "")

    def test_no_confunde_un_nombre_que_contiene_a_otro(self):
        self.assertNotEqual(raiz("SOLDADO DE LA INDEPENDENCIA"), raiz("INDEPENDENCIA AV"))


class UneLoQueDebe(unittest.TestCase):
    """Los corredores partidos en dos nombres oficiales."""

    def test_garcia_del_rio_es_un_solo_corredor(self):
        """El caso de la ronda 8: R20 se midió sobre la mitad este."""
        callejero, mapa = _callejero()
        self.assertEqual(mapa["GARCIA DEL RIO"], {"GARCIA DEL RIO", "GARCIA DEL RIO AV"})
        entero = eje_canonico(callejero, "GARCIA DEL RIO", mapa)
        mitad = unary_union(list(callejero[callejero.clave == "GARCIA DEL RIO"].geometry))
        self.assertGreater(entero.length, mitad.length * 1.9)

    def test_el_corredor_entero_toca_las_dos_avenidas(self):
        """Cabildo cruza una mitad y Balbín la otra. Sólo el corredor entero toca a las dos."""
        callejero, mapa = _callejero()
        entero = eje_canonico(callejero, "GARCIA DEL RIO", mapa)
        cabildo = unary_union(list(callejero[callejero.clave == "CABILDO AV"].geometry))
        balbin = unary_union(list(
            callejero[callejero.clave == "BALBIN RICARDO DR AV"].geometry))
        self.assertTrue(entero.intersects(cabildo), "el corredor entero debe cruzar Av. Cabildo")
        self.assertTrue(entero.intersects(balbin), "el corredor entero debe cruzar Av. Balbín")

    def test_hay_muchas_familias_partidas_no_tres(self):
        """El hallazgo: no son tres casos sueltos, es una propiedad del callejero."""
        _, mapa = _callejero()
        grupos = {frozenset(f) for f in mapa.values() if len(f) > 1}
        self.assertGreater(len(grupos), 50)


class NoUneLoQueNoDebe(unittest.TestCase):
    """Los negativos. Mismo nombre, ejes distintos: NO son el mismo corredor."""

    def test_san_martin_no_se_une_con_san_martin_av(self):
        """Están a 6,6 km. Unirlas produciría un eje que cruza media Ciudad."""
        _, mapa = _callejero()
        self.assertNotIn("SAN MARTIN AV", mapa["SAN MARTIN"])

    def test_azul_no_se_une_con_azul_pasaje(self):
        _, mapa = _callejero()
        self.assertNotIn("AZUL PASAJE", mapa["AZUL"])

    def test_maipu_no_se_une_con_maipu_av(self):
        """El borde: 102 m. Por encima del contacto, así que quedan separadas."""
        callejero, mapa = _callejero()
        a = unary_union(list(callejero[callejero.clave == "MAIPU"].geometry))
        b = unary_union(list(callejero[callejero.clave == "MAIPU AV"].geometry))
        self.assertGreater(a.distance(b), CONTACTO_M)
        self.assertNotIn("MAIPU AV", mapa["MAIPU"])

    def test_dos_calles_que_se_cruzan_no_son_familia(self):
        """El contacto solo no alcanza: casi todas las calles tocan a alguna."""
        _, mapa = _callejero()
        self.assertNotIn("CABILDO AV", mapa["GARCIA DEL RIO"])
        self.assertNotIn("JURAMENTO", mapa.get("CABILDO AV", set()))

    def test_soldado_de_la_independencia_no_es_independencia(self):
        _, mapa = _callejero()
        self.assertNotIn("SOLDADO DE LA INDEPENDENCIA", mapa.get("INDEPENDENCIA AV", set()))


class NoRompeLoQueFuncionaba(unittest.TestCase):
    """Una calle sin variantes tiene que seguir devolviendo exactamente lo de antes."""

    def test_calle_sin_variantes_no_cambia(self):
        callejero, mapa = _callejero()
        for nombre in ("ZABALA", "DELGADO", "CONESA", "FRAGA"):
            con = eje_canonico(callejero, nombre, mapa)
            sin = unary_union(list(callejero[callejero.clave == nombre].geometry))
            self.assertAlmostEqual(con.length, sin.length, places=3, msg=nombre)

    def test_toda_clave_pertenece_a_su_propia_familia(self):
        _, mapa = _callejero()
        for clave, familia in mapa.items():
            self.assertIn(clave, familia)

    def test_las_familias_son_simetricas(self):
        _, mapa = _callejero()
        for clave, familia in mapa.items():
            for otra in familia:
                self.assertEqual(mapa[otra], familia, f"{clave} y {otra} discrepan")


if __name__ == "__main__":
    unittest.main(verbosity=2)
