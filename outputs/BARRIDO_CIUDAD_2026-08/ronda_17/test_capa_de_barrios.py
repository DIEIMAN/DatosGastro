# -*- coding: utf-8 -*-
"""El test que falla cuando un cruce por nombre de barrio pierde un barrio en silencio.

POR QUÉ ESTE TEST Y NO OTRO
----------------------------
Un cruce por nombre que no encuentra nada **no lanza ninguna excepción**: devuelve cero filas, y
cero filas se lee como «ese barrio no tiene locales». La capa vieja escribe «La Boca» y la
oficial «Boca»; la oficial escribe «NUÑEZ» y el resto del proyecto «Núñez». Las dos son
suficientes para borrar un barrio entero de un agregado sin que nada avise.

El test corre el cruce **como lo haría un consumidor de la capa** y falla si algún barrio que
tiene locales por geometría devuelve cero por nombre.

    .venv/Scripts/python.exe -m unittest discover -s outputs/BARRIDO_CIUDAD_2026-08/ronda_17

Cero requests.
"""

import sys
import unittest
from pathlib import Path

import geopandas as gpd

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parents[0]          # outputs/BARRIDO_CIUDAD_2026-08
ROOT = AQUI.parents[2]          # la raíz del repositorio
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))

from nombres_de_barrio import clave, emparejar, igual  # noqa: E402

CRS_METRICO = "EPSG:5347"
OFICIAL = BASE / "insumos" / "caba_barrios.geojson"
VIEJA = ROOT / "data" / "raw" / "geo_barrios.geojson"


def _limpia(g):
    return g if g.is_valid else g.buffer(0)


class TestNormalizador(unittest.TestCase):
    """Los casos concretos que costaron plata, escritos uno por uno."""

    def test_la_boca_y_boca_son_el_mismo_barrio(self):
        self.assertTrue(igual("La Boca", "Boca"))
        self.assertTrue(igual("LA BOCA", "BOCA"))

    def test_nunez_con_ene_y_sin_ene(self):
        self.assertTrue(igual("Núñez", "NUÑEZ"))
        self.assertTrue(igual("Nuñez", "NUNEZ"))

    def test_villa_ortuzar_con_y_sin_tilde(self):
        self.assertTrue(igual("Villa Ortúzar", "VILLA ORTUZAR"))

    def test_villa_gral_mitre_con_y_sin_punto(self):
        self.assertTrue(igual("Villa Gral. Mitre", "VILLA GRAL MITRE"))

    def test_no_empareja_barrios_distintos(self):
        self.assertFalse(igual("Villa Luro", "Villa Lugano"))
        self.assertFalse(igual("Flores", "Floresta"))
        self.assertFalse(igual("Parque Chacabuco", "Parque Chas"))

    def test_el_articulo_interior_no_se_saca(self):
        # «Villa del Parque» tiene un artículo adentro y es parte del nombre.
        self.assertEqual(clave("Villa Del Parque"), "VILLA DEL PARQUE")

    def test_vacio_no_empareja_con_vacio(self):
        self.assertFalse(igual("", ""))
        self.assertFalse(igual(None, None))

    def test_emparejar_levanta_ambiguedad_en_vez_de_elegir(self):
        with self.assertRaises(ValueError):
            emparejar(["La Boca", "Boca"], ["Boca"])


class TestCruceDeCapas(unittest.TestCase):
    """El test que da nombre al archivo: ningún barrio con locales puede dar cero por nombre."""

    @classmethod
    def setUpClass(cls):
        from polos_soporte import puntos_base
        cls.oficial = gpd.read_file(OFICIAL).to_crs(CRS_METRICO).rename(
            columns={"BARRIO": "nombre"})[["nombre", "geometry"]]
        cls.oficial["geometry"] = cls.oficial.geometry.map(_limpia)
        cls.vieja = gpd.read_file(VIEJA).to_crs(CRS_METRICO)[["nombre", "geometry"]]
        cls.vieja["geometry"] = cls.vieja.geometry.map(_limpia)
        cls.puntos = puntos_base()

    def test_las_dos_capas_tienen_los_mismos_48_barrios(self):
        pares, solo_v, solo_o = emparejar(self.vieja.nombre, self.oficial.nombre)
        self.assertEqual(len(pares), 48, "las dos capas deberían emparejar 48 barrios")
        self.assertEqual(solo_v, [], f"barrios sólo en la capa vieja: {solo_v}")
        self.assertEqual(solo_o, [], f"barrios sólo en la capa oficial: {solo_o}")

    def test_ningun_barrio_con_locales_da_cero_al_cruzar_por_nombre(self):
        """El corazón del asunto, y se prueba contra las DOS capas.

        Se cuenta cada barrio por geometría —punto en polígono, que no puede fallar por un
        nombre— y después por nombre. Un barrio que tiene locales por geometría y cero por
        nombre es un cruce roto, y el test lo nombra en vez de dejarlo pasar.
        """
        for etiqueta, capa in (("oficial", self.oficial), ("vieja", self.vieja)):
            with self.subTest(capa=etiqueta):
                cruce = gpd.sjoin(self.puntos[["geometry"]], capa, how="left",
                                  predicate="within")
                cruce = cruce[~cruce.index.duplicated()]
                por_geometria = cruce.nombre.dropna().map(clave).value_counts()
                rotos = []
                for nombre in capa.nombre:
                    k = clave(nombre)
                    if not por_geometria.get(k, 0):
                        continue
                    por_nombre = int((cruce.nombre.map(clave) == k).sum())
                    if por_nombre == 0:
                        rotos.append((nombre, int(por_geometria[k])))
                self.assertEqual(rotos, [],
                                 f"barrios con locales que el cruce por nombre pierde: {rotos}")

    def test_el_cruce_ingenuo_efectivamente_perderia_la_boca(self):
        """Prueba que la trampa es real y no una precaución teórica.

        Si este test dejara de fallar en su parte «ingenua», sería porque alguien alineó los
        nombres de las dos capas, y entonces el normalizador se puede simplificar. Hasta
        entonces, esto documenta el costo exacto de no usarlo.
        """
        nombres_oficial = set(self.oficial.nombre)
        boca_vieja = [n for n in self.vieja.nombre if clave(n) == "BOCA"][0]
        self.assertNotIn(boca_vieja, nombres_oficial,
                         "«La Boca» no debería existir tal cual en la capa oficial")
        self.assertTrue(any(igual(boca_vieja, n) for n in nombres_oficial),
                        "y el normalizador sí tiene que encontrarlo")

    def test_todo_local_del_universo_cae_en_algun_barrio_de_la_capa_oficial(self):
        """No es un test de nombres: es la cota superior de lo que el cruce puede perder.

        Al 10/08/2026 quedan 2 locales fuera de la capa oficial, contra 3 de la vieja. Si ese
        número crece, algo se rompió en la geometría o en los puntos, y conviene enterarse acá.
        """
        cruce = gpd.sjoin(self.puntos[["geometry"]], self.oficial, how="left", predicate="within")
        cruce = cruce[~cruce.index.duplicated()]
        fuera = int(cruce.nombre.isna().sum())
        self.assertLessEqual(fuera, 2,
                             f"{fuera} locales del universo no caen en ningún barrio oficial")


if __name__ == "__main__":
    unittest.main(verbosity=2)
