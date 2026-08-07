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
from normalizar_calles import (  # noqa: E402
    MARCADORES, MARCADORES_PAREADOS, ResolutorDeCalles, calle, clave_calle,
)


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


class ClaveInsensibleAlOrden(unittest.TestCase):
    """El CUARTO bicho de la serie R8: la misma calle escrita en otro orden.

    La desinversión se dispara con la coma, y el inventario mostró que la coma **no siempre
    está**: `ROOSEVELT FRANKLIN D.` viene invertido y sin coma, y `URIBURU JOSE E., Pres.` tiene
    la coma separando el tratamiento y no el apellido. Es la misma causa que Niceto Vega —una
    regla apoyada en una marca que falta— y produce el mismo daño: la calle en dos filas, con la
    mitad de los locales cada una, y sin avisar.

    El arreglo no adivina el orden: la clave es el CONJUNTO de tokens, así que las dos escrituras
    caen juntas sin que nadie declare cuál está bien.
    """

    def test_invertido_sin_coma_cae_en_la_misma_clave(self):
        """Los casos medidos del inventario, los seis."""
        pares = [
            ("ROOSEVELT FRANKLIN D. 2200", "Franklin D. Roosevelt 2200"),
            ("MANSO JUANA 1500", "Juana Manso 1500"),
            ("URIBURU JOSE E., Pres. 700", "Presidente José E. Uriburu 700"),
            ("LINIERS VIRREY 1400", "Virrey Liniers 1400"),
            ("AZURDUY JUANA 100", "Juana Azurduy 100"),
            ("OBLIGADO RAFAEL, Av.Costanera 7010", "Avenida Costanera Rafael Obligado 7010"),
        ]
        for invertida, natural in pares:
            with self.subTest(invertida=invertida):
                self.assertEqual(clave_calle(invertida), clave_calle(natural))

    def test_el_articulo_corrido_al_final_tambien_pliega(self):
        """`BARCO CENTENERA del` es «Avenida del Barco Centenera» con el artículo al final.

        Es el caso que el CONJUNTO resuelve y el multiconjunto no: el recorte de cola se comía ese
        «del» —existe porque «11 de Septiembre de 1888» pierde el año con la altura— y lo dejaba
        en `BARCO CENTENERA`, separado de las otras dos formas. Con conjunto, el token está o no
        está y da igual dónde.
        """
        for variante in ("BARCO CENTENERA del 1300", "Av. del Barco Centenera 1300",
                         "Barco del Centenera 1300"):
            with self.subTest(variante=variante):
                self.assertEqual(clave_calle(variante), clave_calle("Del Barco Centenera 1300"))
        # Y con el artículo al final Y el tratamiento después de la coma, que es como viene:
        self.assertEqual(clave_calle("VALLE IBERLUCEA del, Dr. 1271"),
                         clave_calle("Doctor del Valle Iberlucea 938"))
        self.assertEqual(clave_calle("ARTIGAS MANUEL de 5125"),
                         clave_calle("Manuel de Artigas 5125"))

    def test_el_conector_colgando_sigue_plegando(self):
        """Lo que hacía el recorte de cola lo hace ahora el conjunto, sin regla aparte."""
        self.assertEqual(clave_calle("11 de Septiembre de 1888 2200"),
                         clave_calle("11 de Septiembre 2200"))

    # ------------------------------------------------------------------ CASOS NEGATIVOS
    # Todo lo que el conjunto NO tiene que plegar. Sin esto, «insensible al orden» se convierte en
    # «insensible a todo» y el arreglo pasa de sub-plegar a sobre-plegar, que es peor: sub-plegar
    # parte una calle en dos y se nota; sobre-plegar junta dos calles y no se nota nunca.

    def test_NEGATIVO_los_numeros_distinguen_calles(self):
        """«3 de Febrero» y «4 de Febrero» son dos calles y comparten todo menos el número.

        La clave agresiva del inventario las juntaba porque tiraba los tokens de un carácter. Ésta
        no tira nada, y por eso el caso queda acá: es el falso positivo que el detector tenía y el
        arreglo no puede heredar.
        """
        self.assertNotEqual(clave_calle("3 de Febrero 1200"), clave_calle("4 de Febrero 1200"))
        self.assertNotEqual(clave_calle("5 de Julio 100"), clave_calle("9 de Julio 100"))

    def test_NEGATIVO_las_iniciales_siguen_sin_plegarse(self):
        """El residuo declarado no se cuela por la puerta de atrás.

        Plegar `RAMON L FALCON` con `RAMON FALCON` haría lo mismo con `S MARTIN` y `SAN MARTIN`, y
        ahí la inicial no es inicial: es *San*. Sigue esperando callejero.
        """
        self.assertNotEqual(clave_calle("RAMON L. FALCON 2400"), clave_calle("Ramón Falcón 2400"))
        self.assertNotEqual(clave_calle("S. MARTIN 1200"), clave_calle("San Martín 1200"))
        self.assertNotEqual(clave_calle("E. MOSCONI 100"), clave_calle("Mosconi 100"))

    def test_NEGATIVO_los_sufijos_de_rumbo_distinguen_calles(self):
        """«Traful N.» y «Traful S.» son dos calles distintas y difieren en una sola letra."""
        self.assertNotEqual(clave_calle("Traful N. 100"), clave_calle("Traful S. 100"))

    def test_NEGATIVO_el_articulo_de_cabeza_no_se_recorta(self):
        """La otra mitad del residuo: acá la forma larga es el nombre real y la corta un recorte.

        `LA PAMPA` no es `PAMPA` ni `DE LOS CONSTITUYENTES` es `CONSTITUYENTES`. El conjunto no
        los pliega porque el artículo es un token, y está bien que no lo haga: decidir que sí
        sería sobre-plegar por comodidad.
        """
        self.assertNotEqual(clave_calle("La Pampa 1200"), clave_calle("Pampa 1200"))
        self.assertNotEqual(clave_calle("De los Constituyentes 3200"),
                            clave_calle("Constituyentes 3200"))
        self.assertNotEqual(clave_calle("Humberto I 800"), clave_calle("Humberto 800"))

    def test_NEGATIVO_dos_calles_distintas_no_caen_juntas(self):
        """Control grueso: calles sin relación siguen separadas."""
        self.assertNotEqual(clave_calle("Carlos Calvo 800"), clave_calle("Chacabuco 800"))
        self.assertNotEqual(clave_calle("Juana Manso 100"), clave_calle("Juana Azurduy 100"))

    def test_la_clave_no_es_publicable_y_la_etiqueta_si(self):
        """La clave sale ilegible a propósito; lo que se publica es la etiqueta."""
        self.assertEqual(clave_calle("Del Barco Centenera 1300"), "BARCO CENTENERA DEL")


class MarcadoresPareados(unittest.TestCase):
    """Una abreviatura sin su forma larga parte la calle en dos, y eso ya pasó.

    La tabla tenía `DR` y no `DOCTOR`: «VALLE IBERLUCEA del, Dr.» perdía el tratamiento y
    «Doctor del Valle Iberlucea» lo conservaba, así que la misma calle quedaba en dos claves. El
    par explícito convierte el olvido en algo que se ve.
    """

    def test_toda_abreviatura_tiene_su_forma_larga_en_la_tabla(self):
        """La invariante, y no un caso: si falta un lado, el test lo dice antes que el inventario."""
        for corta, larga in MARCADORES_PAREADOS.items():
            with self.subTest(marcador=corta):
                self.assertIn(corta, MARCADORES)
                self.assertIn(larga, MARCADORES)

    def test_doctor_abreviado_y_largo_pliegan(self):
        """El caso que destapó el faltante, con la forma cruda tal como viene del padrón."""
        self.assertEqual(clave_calle("VALLE IBERLUCEA del, Dr. 1271"),
                         clave_calle("Doctor del Valle Iberlucea 938"))
        self.assertEqual(calle("Doctor Ricardo Rojas 400"), calle("Dr. Ricardo Rojas 400"))

    def test_NEGATIVO_una_calle_que_empieza_como_el_tratamiento_no_se_toca(self):
        """La familia de «Esquiu» otra vez: es token entero, así que el prefijo no alcanza."""
        self.assertEqual(calle("Doctores 100"), "DOCTORES")
        self.assertEqual(calle("Ingeniero 100"), "")          # sólo el tratamiento: no hay calle
        self.assertEqual(calle("Ingenieros 100"), "INGENIEROS")
        self.assertEqual(calle("Presidencia 100"), "PRESIDENCIA")


class AbreviaturasQueSeEstiran(unittest.TestCase):
    """«STA FE» es Santa Fe: acá la palabra es parte del nombre y se estira, no se tira."""

    def test_santa_y_santo_abreviados(self):
        self.assertEqual(calle("STA FE AV. 1200"), calle("Avenida Santa Fe 1200"))
        self.assertEqual(calle("STO DOMINGO 500"), calle("Santo Domingo 500"))
        self.assertEqual(calle("FRAY JUSTO STA MARIA DE ORO 2400"),
                         calle("Fray Justo Santa María de Oro 2400"))

    def test_NEGATIVO_la_S_sola_no_se_estira_y_es_el_residuo_declarado(self):
        """`S. MARTIN` es *San* Martín, pero `S` también es una inicial y no se distinguen.

        Estirarla uniría `S MARTIN` con `SAN MARTIN` —correcto— y también `E MOSCONI` con
        cualquier cosa que empiece con E. Espera callejero, como las demás iniciales.
        """
        self.assertEqual(calle("S. MARTIN 1200"), "S MARTIN")
        self.assertNotEqual(clave_calle("S. MARTIN 1200"), clave_calle("San Martín 1200"))


class EtiquetaElegidaPorLaFuente(unittest.TestCase):
    """Cuál de las dos escrituras se publica. La decide la fuente, no la frecuencia.

    El padrón (F01/F02/RUS/PERMISOS) asienta la calle invertida; OSM, Overture y ATP la escriben
    en orden natural. Elegir por mayoría simple da mal: `ROOSEVELT FRANKLIN D` le gana 19 a 7 a
    `FRANKLIN D ROOSEVELT` y está al revés. Sobre los 12 grupos del corpus la regla de la fuente
    acierta 12 de 12, y en 5 corrige a la mayoría.
    """

    def test_gana_la_forma_de_la_fuente_que_no_invierte_aunque_sea_minoria(self):
        direcciones = ["ROOSEVELT FRANKLIN D. 2200"] * 19 + ["Franklin D. Roosevelt 2200"] * 7
        fuentes = ["F02"] * 19 + ["OVERTURE"] * 7
        resolutor = ResolutorDeCalles(direcciones, fuentes)
        self.assertEqual(resolutor.etiqueta("ROOSEVELT FRANKLIN D. 2200"), "FRANKLIN D ROOSEVELT")
        self.assertEqual(resolutor.etiqueta("Franklin D. Roosevelt 2200"), "FRANKLIN D ROOSEVELT")

    def test_una_fuente_mixta_no_cuenta_como_orden_natural(self):
        """`F02;OVERTURE` no sirve para decidir: no se sabe de cuál de las dos salió el domicilio.

        Sólo votan las filas cuyas fuentes son TODAS de las que no invierten. Acá eso deja al
        grupo sin votos y se cae a la moda, que es lo declarado para ese caso.
        """
        resolutor = ResolutorDeCalles(
            ["MANSO JUANA 1500"] * 3 + ["Juana Manso 1500"],
            ["F02", "F02;OVERTURE", "RUS", "F01;OVERTURE"])
        self.assertEqual(resolutor.etiqueta("MANSO JUANA 1500"), "MANSO JUANA")
        self.assertEqual(resolutor.base_de_la_etiqueta[clave_calle("MANSO JUANA 1500")][0],
                         "solo_padron_moda")

    def test_sin_fuente_que_no_invierta_cae_a_la_moda_y_lo_declara(self):
        resolutor = ResolutorDeCalles(["MANSO JUANA 1500"] * 5, ["F02"] * 5)
        clave = clave_calle("MANSO JUANA 1500")
        self.assertEqual(resolutor.etiquetas[clave], "MANSO JUANA")
        self.assertEqual(resolutor.base_de_la_etiqueta[clave], ("solo_padron_moda", 5))

    def test_la_etiqueta_no_depende_del_orden_en_que_se_leyo_la_base(self):
        """Dos formas empatadas no pueden dar etiquetas distintas según cómo vino ordenado el CSV."""
        a = ResolutorDeCalles(["MANSO JUANA 1500", "Juana Manso 1500"], ["OSM", "OVERTURE"])
        b = ResolutorDeCalles(["Juana Manso 1500", "MANSO JUANA 1500"], ["OVERTURE", "OSM"])
        self.assertEqual(a.etiqueta("Juana Manso 1500"), b.etiqueta("Juana Manso 1500"))

    def test_una_calle_que_no_esta_en_el_corpus_devuelve_su_forma_legible(self):
        resolutor = ResolutorDeCalles(["Chacabuco 800"], ["OSM"])
        self.assertEqual(resolutor.etiqueta("Gorriti 4800"), "GORRITI")


if __name__ == "__main__":
    unittest.main()
