"""Control de regresion del lector compartido de fuentes locales (F01/F02).

El defecto que estas pruebas impiden repetir: un lector escrito contra un solo esquema
de F02 lee un archivo y devuelve cero para los otros siete, y el estudio de rubro que lo
usa mide un piso artificialmente bajo sin que nada falle.

Las pruebas sobre archivos reales solo abren el encabezado y las primeras filas, para no
recorrer las 391.000 filas del conjunto en cada corrida de tests.
"""
from pathlib import Path
import itertools
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.shared.fuentes_locales import (  # noqa: E402
    detectar_dialecto,
    iter_f01,
    iter_f02,
    listar_archivos_f02,
    normalizar,
    reparar_mojibake,
)
from scripts.shared.fuentes_locales.f02 import COLUMNAS_PROHIBIDAS  # noqa: E402

RAW = ROOT / "data" / "raw"
F01 = RAW / "f01_oferta_establecimientos_gastronomicos.csv"


class TextoTest(unittest.TestCase):
    def test_normaliza_acentos(self):
        self.assertEqual(normalizar("PANADERÍA"), "panaderia")
        self.assertEqual(normalizar("Elaboración de Productos"), "elaboracion de productos")

    def test_repara_doble_codificacion(self):
        # Caso real del archivo 2022: UTF-8 releido como latin-1 y grabado asi.
        roto = "PANADERÍA".encode("utf-8").decode("latin-1")
        self.assertNotEqual(roto, "PANADERÍA")
        self.assertEqual(reparar_mojibake(roto), "PANADERÍA")
        self.assertEqual(normalizar(roto), "panaderia")

    def test_no_toca_texto_sano(self):
        for texto in ["PANADERÍA", "CAFE BAR", "Ñandú", ""]:
            self.assertEqual(reparar_mojibake(texto), texto)


@unittest.skipUnless(listar_archivos_f02(), "no hay archivos F02 en data/raw")
class DialectoF02Test(unittest.TestCase):
    def test_cada_archivo_declara_su_dialecto(self):
        for ruta in listar_archivos_f02():
            with self.subTest(archivo=ruta.name):
                dial = detectar_dialecto(ruta)
                self.assertIn(dial.delimitador, (";", ","))
                self.assertIn(dial.esquema, ("legacy", "moderno"))
                self.assertIn(dial.codificacion, ("utf-8-sig", "cp1252"))

    def test_ningun_archivo_queda_en_una_sola_columna(self):
        """El sintoma exacto del lector roto: delimitador equivocado -> una columna."""
        for ruta in listar_archivos_f02():
            with self.subTest(archivo=ruta.name):
                primera = next(iter(iter_f02([ruta], incluir_crudo=True)), None)
                self.assertIsNotNone(primera, f"{ruta.name} no devolvio ninguna fila")
                self.assertGreater(len(primera.crudo), 3, "el archivo se leyo como una sola columna")

    def test_todos_los_archivos_traen_rubro(self):
        for ruta in listar_archivos_f02():
            with self.subTest(archivo=ruta.name):
                muestra = list(itertools.islice(iter_f02([ruta]), 200))
                self.assertTrue(muestra, f"{ruta.name} no devolvio filas")
                con_rubro = sum(1 for r in muestra if r.rubro_completo)
                self.assertGreater(con_rubro, len(muestra) * 0.9,
                                   f"{ruta.name}: el rubro llega vacio en la muestra")

    def test_no_expone_datos_personales(self):
        """Guardrail 7: titulares, cuits y telefonos no salen del lector."""
        for ruta in listar_archivos_f02():
            with self.subTest(archivo=ruta.name):
                for reg in itertools.islice(iter_f02([ruta], incluir_crudo=True), 50):
                    self.assertFalse(COLUMNAS_PROHIBIDAS & set(reg.crudo))

    def test_anio_de_habilitacion_es_de_cuatro_digitos(self):
        for ruta in listar_archivos_f02():
            with self.subTest(archivo=ruta.name):
                for reg in itertools.islice(iter_f02([ruta]), 200):
                    if reg.anio_habilitacion:
                        self.assertRegex(reg.anio_habilitacion, r"^(19|20)\d{2}$")

    def test_perfil_detecta_periodo_enganoso(self):
        from scripts.shared.fuentes_locales import perfilar_f02
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "f02_habilitaciones_aprobadas_2025.csv"
            ruta.write_text(
                "razon_social,rubro,domicilio,nropartidamatriz,disposicion\n"
                "Prueba,FABRICA DE PASTAS,CALLE 123,1,DI-2018-AGC\n",
                encoding="utf-8-sig",
            )
            perfil = perfilar_f02(tmp)[0]
        self.assertFalse(perfil["periodo_coherente"])
        self.assertEqual(perfil["anio_max"], 2018)


SALTO = chr(10)


class FilasCorridas2021Test(unittest.TestCase):
    """El archivo 2021 escribe campos con ";" adentro y sin comillas: la fila se corre."""

    ENCABEZADO = ("Solicitud;TipoTramite;Superficie;FechaHabilitacion;CodigoRubro;"
                  "DescripcionRubro;CodigoSubRubro;DescripcionSubRubro;UnidadFuncional;"
                  "Seccion;Manzana;Parcela;Partida_Matriz;PartidaHorizontal;Calles;"
                  "Titulares;Cuits") + SALTO

    def _leer(self, linea):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "f02_habilitaciones_aprobadas_2021.csv"
            ruta.write_text(self.ENCABEZADO + linea + SALTO, encoding="utf-8")
            return next(iter(iter_f02([ruta])))

    def test_calle_con_apellido_y_nombre_se_recompone(self):
        # "SALGUERO; JERONIMO 188" parte la direccion y corre las columnas una posicion.
        reg = self._leer("1;Habilitacion;72;2021-03-18;501487;Impresion;;;;17;087B;35;"
                         "170415;;SALGUERO; JERONIMO 188;IMPRENTA 24 S.R.L.;30714356360")
        self.assertEqual(reg.domicilio, "SALGUERO JERONIMO 188")

    def test_rubro_de_pizzeria_corre_la_fila_siete_lugares(self):
        # El rubro real trae siete ";" adentro; la direccion termina fuera del encabezado.
        reg = self._leer("2;Habilitacion;194;2021-03-10;1.5;Alimentacion;18;"
                         "Com. min. elab. y vta. Pizza; fuga-zza; faina; empanadas; postres;"
                         " flanes; churros; grill;1;65;9;005B;137866;1323508;GAONA AV. 3756;"
                         "GAONA AV. 3758;Correa; Ruben;20169094781")
        self.assertEqual(reg.domicilio, "GAONA AV. 3756")
        self.assertEqual(reg.id_registro, "")  # la partida recibio basura: no es un id

    def test_no_toma_nombres_de_persona_como_direccion(self):
        reg = self._leer("3;Habilitacion;50;2021-05-01;1.5;Panaderia;;;;1;1;1;"
                         "123456;;CALLE SIN ALTURA;Perez Juan Carlos;20304050607")
        self.assertEqual(reg.domicilio, "CALLE SIN ALTURA")

    def test_partida_sobre_dos_parcelas_toma_la_primera(self):
        reg = self._leer("4;Habilitacion;50;2021-05-01;1.5;Panaderia;;;;1;1;1;"
                         "291211;291212;;RIVADAVIA AV. 100;;")
        self.assertEqual(reg.id_registro, "291211")


class UnidadDeConteoTest(unittest.TestCase):
    """La clave de agrupamiento es la habilitacion (solicitud + UF), no el inmueble.

    La partida matriz identifica la parcela: agrupar por ella fusiona locales distintos
    de un mismo edificio. Estos casos fijan como se lee la unidad funcional, que es lo
    que desagrega la parcela, y que el corrimiento de 2021 no la ensucie.
    """

    ENCABEZADO = FilasCorridas2021Test.ENCABEZADO

    def _leer(self, linea, periodo="2022"):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / ("f02_habilitaciones_aprobadas_%s.csv" % periodo)
            ruta.write_text(self.ENCABEZADO + linea + SALTO, encoding="utf-8")
            return next(iter(iter_f02([ruta])))

    def test_unidad_funcional_pierde_los_ceros_a_la_izquierda(self):
        # "0001" en un anio y "1" en otro son la misma UF: si no, el mismo local se
        # contaria dos veces al unir archivos.
        reg = self._leer("10;Habilitacion;50;2022-05-01;1.5;Panaderia;;;0001;1;1;1;"
                         "123456;7654321;RIVADAVIA AV. 100;Titular;20304050607")
        self.assertEqual(reg.unidad_funcional, "1")
        self.assertEqual(reg.partida_horizontal, "7654321")
        self.assertEqual(reg.clave_habilitacion, "10/1")

    def test_uf_repetida_por_parcela_no_multiplica_la_clave(self):
        # El archivo repite el codigo una vez por parcela de la habilitacion: "1;1".
        reg = self._leer('11;Habilitacion;50;2022-05-01;1.5;Panaderia;;;"1;1";1;1;1;'
                         '123456;;RIVADAVIA AV. 100;Titular;20304050607')
        self.assertEqual(reg.unidad_funcional, "1")

    def test_tramite_sobre_dos_uf_conserva_las_dos_ordenadas(self):
        reg = self._leer('12;Habilitacion;50;2022-05-01;1.5;Panaderia;;;"0002;0001";1;1;1;'
                         '123456;;RIVADAVIA AV. 100;Titular;20304050607')
        self.assertEqual(reg.unidad_funcional, "1;2")

    def test_texto_de_rubro_caido_en_la_columna_no_es_unidad_funcional(self):
        # 2021: el corrimiento mete "BOTONERIA" o "churros" en UnidadFuncional.
        reg = self._leer("13;Habilitacion;50;2021-05-01;1.5;Panaderia;;;BOTONERIA;1;1;1;"
                         "123456;;RIVADAVIA AV. 100;Titular;20304050607", periodo="2021")
        self.assertEqual(reg.unidad_funcional, "")
        self.assertEqual(reg.clave_habilitacion, "13")

    def _leer_moderno(self, linea):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "f02_habilitaciones_aprobadas_2025.csv"
            ruta.write_text(
                "razon_social,rubro,domicilio,comuna,nro_partida_matriz,disposicion"
                + SALTO + linea + SALTO, encoding="utf-8")
            return next(iter(iter_f02([ruta])))

    def test_el_esquema_moderno_agrupa_por_disposicion(self):
        # 2025 no publica la solicitud, pero la disposicion es el mismo acto: una
        # habilitacion. Sin ella la clave seria la partida, que es el inmueble.
        reg = self._leer_moderno("PANIFICADORA SA,Panaderia,RIVADAVIA AV. 100,1,123456,"
                                 "DI-2016-1-AGC")
        self.assertEqual(reg.esquema, "moderno")
        self.assertEqual(reg.clave_habilitacion, "DI-2016-1-AGC")
        self.assertEqual(reg.id_registro, "123456")

    def test_fila_moderna_sin_disposicion_no_tiene_clave(self):
        # El 4,7 % de 2025 viene sin disposicion: tiene que caer a partida + nombre.
        reg = self._leer_moderno("PANIFICADORA SA,Panaderia,RIVADAVIA AV. 100,1,123456,")
        self.assertEqual(reg.clave_habilitacion, "")


@unittest.skipUnless(F01.exists(), "no esta f01 en data/raw")
class F01Test(unittest.TestCase):
    def test_lee_campos_y_coordenadas(self):
        muestra = list(itertools.islice(iter_f01(), 100))
        self.assertTrue(muestra)
        self.assertTrue(all(r.nombre for r in muestra))
        con_geo = [r for r in muestra if r.lat is not None]
        self.assertTrue(con_geo)
        for reg in con_geo:
            self.assertTrue(-35.0 < reg.lat < -34.0, reg.lat)
            self.assertTrue(-59.0 < reg.lon < -58.0, reg.lon)

    def test_no_expone_telefono_ni_mail(self):
        for reg in itertools.islice(iter_f01(incluir_crudo=True), 50):
            self.assertNotIn("telefono", reg.crudo)
            self.assertNotIn("mail", reg.crudo)


if __name__ == "__main__":
    unittest.main()
