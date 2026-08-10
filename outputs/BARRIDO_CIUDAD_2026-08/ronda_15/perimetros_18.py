# -*- coding: utf-8 -*-
"""Los dieciocho polos sin perimetro propio, trazados sobre lo que sus fichas ya tienen escrito.

DE DONDE SALE
-------------
`MAGNITUD_DE_LOS_18.md` mide, para cada uno de los 18 polos admitidos sin perimetro, que
proporcion del barrio contenedor esta dentro de una concentracion detectada. Cuando esa
proporcion es baja, el poligono administrativo del barrio -que es lo que hoy tienen como
geometria en `geometria_r7/zonas_r8.geojson`- esta mintiendo mucho. Nunez da 2,8 %.

El perimetro de cada uno **ya esta escrito** en calles y alturas, en
`SECCION_VII_ZONAS_INCORPORADAS.md`, `FICHAS_SUR_NUEVAS.md` y el campo `perimetro_textual` de
`fichas_corpus_polos.csv`. Aca no se averigua nada: se poligoniza lo escrito.

EL INSTRUMENTO NUEVO, Y ES LO QUE DESTRABA EL PASO
---------------------------------------------------
`polos_poligonizar.py` §5 declaro una carencia: *"Recortar a manzana necesita una capa de
manzanas o parcelas, y en el repositorio no hay ninguna -solo barrios y comunas-"*. Por eso los
124 poligonos del borrador tienen bordes libres, y por eso un corredor solo se podia cerrar con
un buffer.

**Esa capa se construye desde el callejero, que si esta.** `polygonize()` sobre la union nodada
de los 31.961 segmentos devuelve **15.032 caras cerradas de mediana 1,05 ha**: son las manzanas.
Con eso, "Av. Alvarez Jonte entre el 4400 y el 5299" deja de necesitar un ancho inventado: el
poligono son **las manzanas con frente sobre ese tramo**, y su borde corre sobre calles por
construccion.

Es la misma tecnica que la ronda 14 uso para la cuña de Colegiales, aplicada a la Ciudad entera
en vez de a tres bordes elegidos a mano.

LA REGLA QUE DECIDE SI UNA FICHA CIERRA O NO, ESCRITA ANTES DE CORRER
----------------------------------------------------------------------
Una pieza cierra **solo si el texto de la ficha le da extension medible sobre el callejero**:

    un rango de alturas          "Av. Alvarez Jonte entre el 4400 y el 5299"
    dos calles de corte          "Jose Leon Suarez entre Ramon Falcon y Ventura Bosch"
    calles que encierran cara    cuatro calles que `polygonize` cierra

Y **no cierra** cuando el texto nombra un eje sin extremos, una esquina sin extension, o puntos
que el mismo texto llama dispersos. En ese caso **no se inventa el borde**: queda el provisorio
del barrio y la salida declara que dato falta. Un ancho puesto por buffer seria una propiedad del
instrumento y no del territorio, y este proyecto ya tiene esa leccion escrita cuatro veces.

`cerrado_si_no` toma tres valores y no dos, porque la mitad de estas zonas son **sistemas de
subpolos** y el texto cierra unas piezas y otras no:

    si       cerraron todas las piezas que el texto nombra -> la ficha puede publicar cifra
    parcial  cerro alguna y falta otra -> **la ficha NO publica cifra de zona**; lo trazado
             viaja como pieza medida y `que_falta` dice cual falta
    no       no cerro ninguna -> queda el provisorio del barrio

TRAMPAS DE SHAPELY/GEOS QUE LAS RONDAS 7 Y 13 DEJARON ANOTADAS, Y QUE ACA SE RESPETAN
--------------------------------------------------------------------------------------
  - area en metros, nunca en grados: todo se proyecta a EPSG:5347 (POSGAR 2007 / Argentina 5).
  - **R12**: la contencion se verifica por **superficie perdida**, no por predicado. `covers()`
    devuelve False en casos que si contienen. Cada perimetro nuevo se mide contra el provisorio
    midiendo cuanta superficie suya queda afuera.
  - `buffer(0)` antes de cada operacion booleana.
  - el frente de una manzana sobre el tramo se mide por **interseccion exacta** de borde contra
    eje, no por proximidad: las caras salen de la union nodada de esas mismas lineas, asi que
    comparten coordenadas y la longitud compartida es exacta.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import polygonize, unary_union

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"
CRS_SALIDA = "EPSG:4326"  # el de zonas_r8 y referencias_r8, que es lo que consumen los mapas

ZONAS_R8 = BASE / "geometria_r7" / "zonas_r8.geojson"
REFERENCIAS_R8 = BASE / "geometria_r8" / "referencias_r8.geojson"
MAGNITUDES = BASE / "desde_cowork" / "evidencia_2026" / "magnitudes_sin_perimetro.csv"
HITOS = BASE / "hitos" / "hitos_capa_2026_r11.csv"  # la ultima con punto: 225 filas, 220 con lat/lon

# Frente minimo para que una manzana cuente como frentista del tramo. Declarado, no elegido a
# ojo: una manzana que solo toca el tramo en la ochava comparte unos pocos metros; 20 m es menos
# de la mitad de una fila de parcelas y no llega a un frente de manzana. La sensibilidad a 10 y
# 40 m se reporta al final de la corrida.
FRENTE_MIN_M = 20.0
FRENTE_SENSIBILIDAD = (10.0, 20.0, 40.0)


def limpia(g):
    return g if g.is_valid else g.buffer(0)


# --------------------------------------------------------------------------- recetas
#
# Una receta por zona. `piezas` lleva las que el texto cierra; `sin_cerrar` las que nombra y no
# alcanzan a cerrar, con el dato que falta. El orden es el de prioridad de MAGNITUD_DE_LOS_18:
# de menor a mayor proporcion del barrio concentrada, que es donde el provisorio miente mas.
RECETAS = [
    dict(
        zona="Z41", nombre="Nunez", pct=2.8,
        fuente=("Tres piezas: el corredor de Crisologo Larralde entre Av. del Libertador y Av. "
                "Cabildo, el corredor bajo el viaducto Mitre, y un nucleo disperso de bistros en "
                "Campos Salles, O'Higgins y Grecia."),
        piezas=[dict(nombre="corredor Crisologo Larralde", tipo="eje_entre",
                     calle="LARRALDE, CRISOLOGO AV.", corte_a="DEL LIBERTADOR AV.",
                     corte_b="CABILDO AV.")],
        sin_cerrar=[
            ("corredor bajo el viaducto Mitre",
             "el texto no nombra ninguna calle ni los dos extremos del tramo, y la propia ficha "
             "deja abierto el reparto: el extremo sur toca R19 Federico Lacroze y el tramo entre "
             "Blanco Encalada y Monroe cae en Belgrano"),
            ("nucleo de bistros en Campos Salles, O'Higgins y Grecia",
             "tres calles sin extension, y el texto las llama dispersas"),
        ],
    ),
    dict(
        zona="Z46", nombre="Retiro", pct=3.9,
        fuente=("Tres piezas: el nucleo institucional de Plaza San Martin y Florida; el corredor "
                "Arroyo, de Juncal y Esmeralda a Plaza Carlos Pellegrini; y un cluster coreano y "
                "asiatico sobre Maipu, Esmeralda, Paraguay y M. T. de Alvear, alturas 800 a 990, "
                "entre Plaza San Martin y Av. Cordoba."),
        piezas=[
            dict(nombre="cluster coreano y asiatico", tipo="ejes_por_altura",
                 calles=["MAIPU", "ESMERALDA", "PARAGUAY", "ALVEAR, MARCELO T. DE"],
                 desde=800, hasta=990),
            dict(nombre="corredor Arroyo", tipo="eje_entre", calle="ARROYO",
                 corte_a="JUNCAL", corte_b="PELLEGRINI, CARLOS"),
        ],
        sin_cerrar=[("nucleo institucional de Plaza San Martin y Florida",
                     "una plaza y una calle sin rango de alturas ni calles de corte: Florida "
                     "entera mide mas de un kilometro y el texto no dice que tramo")],
        contra=["Z46_SUBZONA_CLUSTER_COREANO"],
    ),
    dict(
        zona="Z27", nombre="Villa Santa Rita", pct=4.9,
        fuente=("Puntos dispersos con anclaje en Av. Alvarez Jonte, que es el limite sur y oeste "
                "del barrio y no su columna interior."),
        piezas=[],
        sin_cerrar=[("el conjunto",
                     "el texto dice 'puntos dispersos' y no da extension sobre Av. Alvarez Jonte; "
                     "la propia ficha declara que la via de densidad no abre porque son seis "
                     "locales dispersos en diez cuadras. Falta el tramo de Av. Alvarez Jonte, en "
                     "alturas o entre calles de corte")],
    ),
    dict(
        zona="Z50", nombre="Barracas - Av. Montes de Oca", pct=5.2,
        fuente=("El corredor documentado va de Av. Montes de Oca 280 a 1702. El poligono medido "
                "es otra cosa y es mas chico: 18,02 hectareas y 62 locales, sobre el tramo 301 a "
                "999."),
        piezas=[dict(nombre="corredor documentado 280-1702", tipo="eje_por_altura",
                     calle="MONTES DE OCA, MANUEL AV.", desde=280, hasta=1702)],
        sin_cerrar=[],
        lecturas=[dict(nombre="el poligono medido, tramo 301-999", tipo="eje_por_altura",
                       calle="MONTES DE OCA, MANUEL AV.", desde=301, hasta=999),
                  dict(nombre="el eje que releva la Ciudad, 501-1199", tipo="eje_por_altura",
                       calle="MONTES DE OCA, MANUEL AV.", desde=501, hasta=1199)],
        que_falta_extra=("decidir cual de los tres objetos es el polo: el corredor documentado "
                         "280-1702, el poligono medido 301-999 o el eje relevado 501-1199. La "
                         "ficha declara la decision abierta y las tres cifras estan en esta salida"),
    ),
    dict(
        zona="Z51", nombre="Barracas - Iriarte, California y Vieytes", pct=5.2,
        fuente=("Racimo documentado sobre Av. Iriarte 2100-2300, con extension a Vieytes y "
                "California."),
        piezas=[dict(nombre="racimo Av. Iriarte 2100-2300", tipo="eje_por_altura",
                     calle="IRIARTE, GRAL. AV.", desde=2100, hasta=2300)],
        sin_cerrar=[],
        cruces=[("VIEYTES", "la transversal que el texto nombra"),
                ("CALIFORNIA", "la otra transversal que el texto nombra")],
        que_falta_extra=("la 'extension a California' no tiene extension escrita: California no "
                         "cruza el tramo 2100-2300. Si esa extension entra, hay que decir hasta "
                         "que altura"),
    ),
    dict(
        zona="Z39", nombre="Parque Avellaneda", pct=5.2,
        fuente="El anillo del Parque Avellaneda, sobre Av. Olivera y Av. Lacarra.",
        piezas=[],
        sin_cerrar=[("el anillo del parque",
                     "un anillo necesita cerrar y el texto nombra dos avenidas que se CRUZAN "
                     "-distancia 0 m-, o sea dos lados de una esquina, no cuatro de un anillo. "
                     "Faltan las otras dos calles del anillo, o el poligono del parque")],
        lecturas=[dict(nombre="lectura B - por las alturas de los tres referentes",
                       tipo="ejes_por_altura", calles=["LACARRA AV."], desde=836, hasta=1500),
                  dict(nombre="lectura B - Av. Olivera al 1557",
                       tipo="ejes_por_altura", calles=["OLIVERA AV."], desde=1500, hasta=1600)],
        que_falta_extra=("las dos calles que faltan para cerrar el anillo. La lectura B esta "
                         "medida y NO se adopta: delimita por donde estan los tres referentes "
                         "-La Barra del Parque (Lacarra 836), De Flores Cafe (Lacarra 1500) y "
                         "Viejo Mercado (Olivera 1557)- y no por el perimetro escrito, y los tres "
                         "estan dudosos"),
    ),
    dict(
        zona="Z28", nombre="Monte Castro", pct=5.7,
        fuente=("Av. Alvarez Jonte, aproximadamente entre el 4400 y el 5299, con nodo en el cruce "
                "con Av. Lope de Vega."),
        piezas=[dict(nombre="corredor Av. Alvarez Jonte 4400-5299", tipo="eje_por_altura",
                     calle="ALVAREZ JONTE AV.", desde=4400, hasta=5299)],
        sin_cerrar=[],
        cruces=[("LOPE DE VEGA AV.", "el nodo que el texto nombra")],
    ),
    dict(
        zona="Z52", nombre="La Boca - Almirante Brown y Necochea", pct=7.5,
        fuente=("El tramo de la calle Necochea y sus intersecciones con la avenida Suarez y la "
                "calle Olavarria, aproximadamente 340 metros lineales, desde la avenida Suarez y "
                "la calle Olavarria, extendiendose hasta la avenida Almirante Brown."),
        piezas=[dict(nombre="tramo Necochea, de Suarez a Alte. Brown", tipo="eje_entre",
                     calle="NECOCHEA", corte_a="SUAREZ AV.", corte_b="BROWN, ALTE. AV.")],
        sin_cerrar=[],
        largo_declarado_m=340,
    ),
    dict(
        zona="Z53", nombre="La Boca - Caminito y Vuelta de Rocha", pct=7.5,
        fuente="Entorno de Caminito y la Vuelta de Rocha, sobre Av. Don Pedro de Mendoza.",
        piezas=[],
        sin_cerrar=[("el entorno de Caminito y la Vuelta de Rocha",
                     "'entorno' no es una extension, y **la Vuelta de Rocha no esta en el "
                     "callejero**: es un recodo del Riachuelo, no una calle. Falta el tramo de "
                     "Av. Don Pedro de Mendoza, en alturas o entre calles de corte")],
    ),
    dict(
        zona="Z33", nombre="Mataderos", pct=9.7,
        fuente=("Dos piezas separadas por mas de un kilometro: la Feria y el Mercado de Hacienda, "
                "en Av. Lisandro de la Torre y Av. de los Corrales, y un conjunto de referentes "
                "dispersos. El eje comercial que releva la Ciudad es Av. Alberdi 5501-6299."),
        piezas=[],
        sin_cerrar=[("la Feria y el Mercado de Hacienda",
                     "el texto da una esquina -el cruce de dos avenidas- y ninguna extension"),
                    ("el conjunto de referentes dispersos",
                     "el texto los llama dispersos y estan a mas de un kilometro de la Feria")],
        lecturas=[dict(nombre="lectura B - el eje comercial que releva la Ciudad, Alberdi 5501-6299",
                       tipo="ejes_por_altura", calles=["ALBERDI, JUAN BAUTISTA AV."],
                       desde=5501, hasta=6299)],
        que_falta_extra=("la extension de la pieza de la Feria. La lectura B esta medida y NO se "
                         "adopta: **ese tramo es el eje del IDECBA, no el perimetro del polo**, y "
                         "tomarlo seria atribuirle al polo el objeto de otra fuente"),
    ),
    dict(
        zona="Z31", nombre="Villa Luro", pct=9.8,
        fuente=("Bulevar Ramon L. Falcon 5400-5800, entre Albariños y Escalada, mas Av. Rivadavia "
                "10100-10400."),
        piezas=[dict(nombre="Bulevar Ramon L. Falcon 5400-5800", tipo="eje_por_altura",
                     calle="FALCON, RAMON L.,CNEL. AV.", desde=5400, hasta=5800),
                dict(nombre="Av. Rivadavia 10100-10400", tipo="eje_por_altura",
                     calle="RIVADAVIA AV.", desde=10100, hasta=10400)],
        sin_cerrar=[],
        # El texto da la misma pieza dos veces: por altura y por calles de corte. Se miden las
        # dos y se comparan: es una verificacion R12 que la ficha regala y nadie habia usado.
        # «Albariños» en la ficha; el callejero lo escribe ALBARINO, en singular. La primera
        # corrida no lo encontro y el control **no fallo: se salteo en silencio**. Por eso ahora
        # cada nombre de calle de una receta se resuelve contra el callejero antes de usarse.
        control_doble=dict(nombre="Falcon entre Albarino y Escalada", calle="FALCON, RAMON L.,CNEL. AV.",
                           corte_a="ALBARINO", corte_b="ESCALADA AV.", contra="Bulevar Ramon L. Falcon 5400-5800"),
    ),
    dict(
        zona="Z35", nombre="Balvanera - Once", pct=19.2,
        fuente="En revision. La ficha no escribe ningun perimetro.",
        piezas=[],
        sin_cerrar=[("la zona entera",
                     "la ficha declara el perimetro 'en revision' y **no escribe ninguna calle**. "
                     "No hay nada que poligonizar. Lo que falta es el perimetro, y la propia "
                     "ficha dice cual es el insumo: documentar la densidad actual")],
    ),
    dict(
        zona="Z40", nombre="Nueva Pompeya y Parque Patricios", pct=19.8,
        fuente=("Tres piezas: Av. Caseros y el Distrito Tecnologico, Av. Saenz y el Mercado de "
                "Pompeya, y el Barrio Charrua."),
        piezas=[],
        sin_cerrar=[("Av. Caseros y el Distrito Tecnologico", "eje sin extremos ni alturas"),
                    ("Av. Saenz y el Mercado de Pompeya", "eje sin extremos ni alturas"),
                    ("Barrio Charrua",
                     "la nota de delimitacion le da tres bordes -Av. Bonorino, Av. Fernandez de "
                     "la Cruz y las vias del Belgrano Sur- pero **las vias del Belgrano Sur no "
                     "son una linea del callejero**: solo hay segmentos de calle marcados con "
                     "cruce ferroviario. Con dos bordes de tres no cierra una cara")],
        aviso=("y aunque cerrara, el Barrio Charrua abre la via D por comunidad y practica "
               "cultural, no por establecimientos: sumarlo agregaria superficie sin oferta y "
               "bajaria la densidad publicada de la zona"),
    ),
    dict(
        zona="Z54", nombre="Nueva Pompeya - eje Av. Saenz", pct=19.8,
        fuente="Eje Av. Saenz, con nucleo en el Mercado de Pompeya, Av. Saenz 790.",
        piezas=[],
        sin_cerrar=[("el eje Av. Saenz",
                     "una sola altura -el 790, que es el mercado- no es una extension. Falta el "
                     "tramo, y ademas el reparto con Z40, que la ficha declara pendiente")],
    ),
    dict(
        zona="Z47", nombre="Monserrat y Congreso", pct=23.7,
        fuente=("El eje Av. de Mayo-Callao: Av. de Mayo de Peru/Bolivar a Lima/Salta, alturas 500 "
                "a 1300, ambas aceras, con frentes sobre H. Yrigoyen 1199-1201. Remates en Alsina "
                "420, Peru 86 y 302, Av. Belgrano 599 y 1144, Defensa 695, Solis 475, la ochava "
                "de Entre Rios e Independencia, y Av. Callao 248 y 368."),
        piezas=[dict(nombre="eje Av. de Mayo 500-1300, ambas aceras", tipo="eje_por_altura",
                     calle="DE MAYO AV.", desde=500, hasta=1300)],
        sin_cerrar=[],
        remates=[("ALSINA, ADOLFO", 420), ("PERU", 86), ("PERU", 302),
                 ("BELGRANO AV.", 599), ("BELGRANO AV.", 1144), ("DEFENSA", 695),
                 ("SOLIS", 475), ("CALLAO AV.", 248), ("CALLAO AV.", 368),
                 ("YRIGOYEN, HIPOLITO", 1199), ("YRIGOYEN, HIPOLITO", 1201)],
        contra=["R12"],
        que_falta_extra=("decidir si los remates entran al poligono. Estan medidos abajo: son "
                         "direcciones sueltas, no bordes, y meterlos exigiria decir por que "
                         "calles se llega hasta cada uno"),
    ),
    dict(
        zona="Z37", nombre="Almagro", pct=29.1,
        fuente=("Tres piezas: el nucleo de Guardia Vieja y Bulnes, el corredor de Av. Corrientes "
                "entre el 3500 y el 4200, y el nodo de Rivadavia y Medrano."),
        piezas=[dict(nombre="corredor Av. Corrientes 3500-4200", tipo="eje_por_altura",
                     calle="CORRIENTES AV.", desde=3500, hasta=4200)],
        sin_cerrar=[("nucleo de Guardia Vieja y Bulnes",
                     "el texto dice 'cuatro locales en tres cuadras' y nombra dos alturas -3601 y "
                     "3602-, pero no dice cuales son las tres cuadras: falta el rango"),
                    ("nodo de Rivadavia y Medrano",
                     "una esquina sin extension")],
        contra=["R13"],
    ),
    dict(
        zona="Z32", nombre="Liniers - Mercado Andino", pct=33.7,
        fuente=("El eje de Jose Leon Suarez entre Ramon Falcon y Ventura Bosch, 285 metros "
                "medidos, con transversales sobre Ramon Falcon, Ibarrola y Ventura Bosch. No es "
                "un cuadrante: es un eje con transversales."),
        piezas=[dict(nombre="eje Jose Leon Suarez, de Ramon Falcon a Ventura Bosch",
                     tipo="eje_entre", calle="SUAREZ, JOSE LEON",
                     corte_a="FALCON, RAMON L.,CNEL. AV.", corte_b="BOSCH, VENTURA")],
        sin_cerrar=[],
        largo_declarado_m=285,
        cruces=[("IBARROLA", "la transversal donde esta la gastronomia")],
    ),
    dict(
        zona="Z44", nombre="Villa Ortuzar", pct=34.2,
        fuente=("Av. Alvarez Thomas, tramo 600-1700, con nucleo secundario en Plaza 25 de Agosto "
                "-Giribone, 14 de Julio, Charlone y Bauness."),
        piezas=[dict(nombre="corredor Av. Alvarez Thomas 600-1700", tipo="eje_por_altura",
                     calle="ALVAREZ THOMAS AV.", desde=600, hasta=1700)],
        sin_cerrar=[("nucleo secundario de Plaza 25 de Agosto",
                     "las cuatro calles NO encierran ninguna cara: Bauness queda a 184 m de "
                     "Giribone y a 249 m de 14 de Julio, y con las otras tres tampoco cierra. "
                     "Falta decir por donde va el cuarto lado")],
        contra=["R09R19_CHACAGIALES"],
    ),
]


# --------------------------------------------------------------------------- maquinaria


class Callejero:
    """El callejero canonico, su capa de manzanas y las operaciones que necesitan las recetas."""

    def __init__(self):
        sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
        from callejero_canonico import cargar, familias, eje_canonico  # noqa: E402
        from polos_soporte import (barrios, puntos_base, sin_tildes,  # noqa: E402
                                   _punto_de_cruce, _tramo_entre)

        self._eje_canonico, self._sin_tildes = eje_canonico, sin_tildes
        self._punto_de_cruce, self._tramo_entre = _punto_de_cruce, _tramo_entre
        self.calles = cargar()
        self.familias = familias(self.calles)
        self.puntos = puntos_base()
        self.barrios = barrios().set_index("nombre")
        hitos = pd.read_csv(HITOS).dropna(subset=["latitud", "longitud"])
        # ERRATA DE LA CAPA DE HITOS, encontrada al contar: **siete establecimientos estan
        # cargados mas de una vez con el mismo punto y distinto `tipo`** -una vez como MICHELIN
        # y otra como «Ranking internacional»; Don Julio, tres veces-, o sea **ocho filas de
        # mas**. Sin deduplicar, Nunez contaba «2 hitos adentro» cuando adentro hay uno solo,
        # que es Ness. Se deduplica por nombre y punto y el defecto queda declarado: no se
        # corrige la capa desde aca.
        antes = len(hitos)
        hitos = hitos.drop_duplicates(subset=["nombre", "latitud", "longitud"])
        if antes != len(hitos):
            print(f"hitos: {antes} filas con punto -> {len(hitos)} tras deduplicar por nombre y "
                  f"punto ({antes - len(hitos)} filas repetidas en hitos_capa_2026_r11.csv)")
        self.hitos = gpd.GeoDataFrame(
            hitos, geometry=gpd.points_from_xy(hitos.longitud, hitos.latitud),
            crs="EPSG:4326").to_crs(CRS_METRICO).reset_index(drop=True)
        red = unary_union(list(self.calles.geometry))
        caras = [limpia(p) for p in polygonize(red)]
        self.manzanas = gpd.GeoSeries(caras, crs=CRS_METRICO)
        self._sidx = self.manzanas.sindex
        print(f"callejero: {len(self.calles):,} segmentos -> "
              f"{len(self.manzanas):,} caras cerradas (manzanas), "
              f"mediana {self.manzanas.area.median() / 10_000:,.2f} ha, "
              f"total {self.manzanas.area.sum() / 10_000:,.0f} ha")
        print(f"base: {len(self.puntos):,} locales del universo anillo=nucleo & apto_geometria\n")

    def segmentos(self, nombre):
        """Los segmentos de la familia de esa calle. **Falla fuerte si el nombre no existe.**

        La primera corrida escribio «ALBARIÑOS» y el callejero lo tiene como ALBARINO, en
        singular. `segmentos` devolvio vacio, `tramo_entre` devolvio None y el control R12 de
        Villa Luro **se salteo sin imprimir nada**. Es la misma familia de falla silenciosa que
        este proyecto ya tiene contada cinco veces, asi que un nombre que no resuelve corta la
        corrida en vez de producir un numero de menos.
        """
        clave = self._sin_tildes(nombre)
        sub = self.calles[self.calles.clave.isin(self.familias.get(clave, {clave}))]
        if sub.empty:
            raise SystemExit(f"«{nombre}» ({clave}) no esta en el callejero: la receta lo nombra "
                             f"y no se puede resolver. No se sigue con un tramo de menos.")
        return sub

    def reparto_por_barrio(self, geom, minimo=0.01):
        """Que barrios se reparten el poligono, por superficie. Ordenado de mayor a menor."""
        salida = []
        for nombre, g in self.barrios.geometry.items():
            inter = limpia(geom.intersection(limpia(g)))
            if inter.is_empty:
                continue
            fraccion = inter.area / geom.area
            if fraccion >= minimo:
                salida.append((nombre, fraccion * 100, inter.area / 10_000))
        return sorted(salida, key=lambda x: -x[1])

    def eje(self, nombre):
        return self._eje_canonico(self.calles, nombre, self.familias)

    def tramo_por_altura(self, nombre, desde, hasta):
        """Los segmentos cuyo rango de alturas SOLAPA el pedido, con desigualdad estricta.

        La estricta no es un detalle: el segmento 4301-4400 de Alvarez Jonte comparte con el
        rango 4400-5299 un unico numero, el extremo, y con `>=` entraba entero y agregaba 120 m
        de eje y una manzana que la ficha no nombra.
        """
        elegidos = []
        for r in self.segmentos(nombre).itertuples():
            alturas = [v for v in (r.alt_izqini, r.alt_izqfin, r.alt_derini, r.alt_derfin)
                       if v and v > 0]
            if not alturas:
                continue
            if max(alturas) > desde and min(alturas) < hasta:
                elegidos.append(r.geometry)
        return unary_union(elegidos) if elegidos else None

    def tramo_entre(self, nombre, corte_a, corte_b):
        segmentos = self.segmentos(nombre)
        a, b = self.segmentos(corte_a), self.segmentos(corte_b)
        if segmentos.empty or a.empty or b.empty:
            return None
        pa = self._punto_de_cruce(segmentos, a)
        pb = self._punto_de_cruce(segmentos, b)
        return self._tramo_entre(segmentos, pa, pb)

    def frentistas(self, tramo, frente_min=FRENTE_MIN_M):
        """Las manzanas con frente sobre el tramo. Interseccion EXACTA, no proximidad."""
        salida = []
        for i in self._sidx.query(tramo.buffer(2)):
            cara = self.manzanas.iloc[i]
            largo = cara.boundary.intersection(tramo).length
            if largo >= frente_min:
                salida.append((i, largo, cara))
        return salida

    def punto_de_altura(self, calle, altura):
        """El centro de la cuadra que contiene esa altura. Devuelve None si no hay cuadra."""
        for r in self.segmentos(calle).itertuples():
            pares = [(r.alt_izqini, r.alt_izqfin), (r.alt_derini, r.alt_derfin)]
            for ini, fin in pares:
                if ini and fin and min(ini, fin) <= altura <= max(ini, fin):
                    return r.geometry.interpolate(0.5, normalized=True)
        return None

    def locales(self, geom):
        return int(self.puntos.within(geom).sum())

    def hitos_en(self, geom):
        """Los hitos con punto que caen adentro. Devuelve la lista de nombres.

        **Esta es la prueba que decide si el trazado describe al polo o al algoritmo**, y no la
        invento aca: es la leccion de Almagro, escrita en su propia ficha. El fragmento que el
        agrupamiento automatico detecto ahi mide 5,7 ha y **no contiene ninguno de los cinco
        Bares Notables** de la zona. Un poligono que no contiene los hitos sobre los que su ficha
        se apoya no es el poligono de esa ficha, por prolijo que sea su borde.
        """
        return sorted(self.hitos[self.hitos.within(geom)].nombre.astype(str))

    def hitos_cerca(self, geom, marco, tope=8):
        """Los hitos del marco que quedan FUERA de `geom`, con su distancia al borde.

        Sin la distancia, «0 de 9 adentro» se lee como una refutacion y puede ser lo contrario:
        un hito en la esquina de enfrente esta a 20 m y uno de otro barrio a 700 m, y los dos
        cuentan igual en un conteo de adentro/afuera. La distancia es la que separa «el perimetro
        no describe al polo» de «el perimetro no llega a la ochava».
        """
        fuera = self.hitos[~self.hitos.within(geom)]
        fuera = fuera[fuera.within(marco)]
        pares = sorted(((str(r.nombre), geom.distance(r.geometry)) for r in fuera.itertuples()),
                       key=lambda x: x[1])
        return pares[:tope]


def resolver_pieza(cj, pieza):
    """Devuelve (tramo, poligono, detalle) o (None, None, motivo)."""
    tipo = pieza["tipo"]
    if tipo == "eje_por_altura":
        tramo = cj.tramo_por_altura(pieza["calle"], pieza["desde"], pieza["hasta"])
        detalle = f"{pieza['calle']} {pieza['desde']}-{pieza['hasta']}"
    elif tipo == "ejes_por_altura":
        piezas = [cj.tramo_por_altura(n, pieza["desde"], pieza["hasta"]) for n in pieza["calles"]]
        faltan = [n for n, t in zip(pieza["calles"], piezas) if t is None]
        if faltan:
            return None, None, f"sin tramo en el callejero: {faltan}"
        tramo = unary_union(piezas)
        detalle = (", ".join(pieza["calles"]) + f" {pieza['desde']}-{pieza['hasta']}")
    elif tipo == "eje_entre":
        tramo = cj.tramo_entre(pieza["calle"], pieza["corte_a"], pieza["corte_b"])
        detalle = f"{pieza['calle']} entre {pieza['corte_a']} y {pieza['corte_b']}"
    else:
        raise SystemExit(f"tipo de pieza desconocido: {tipo}")
    if tramo is None or tramo.is_empty:
        return None, None, f"el tramo salio vacio: {detalle}"
    frentistas = cj.frentistas(tramo)
    if not frentistas:
        return tramo, None, f"ninguna manzana con frente >= {FRENTE_MIN_M:.0f} m sobre {detalle}"
    poligono = limpia(unary_union([c for _, _, c in frentistas]))
    return tramo, poligono, detalle


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 96)
    print("RONDA 15 - los dieciocho perimetros, trazados sobre lo que las fichas ya tienen escrito")
    print("=" * 96 + "\n")

    cj = Callejero()

    zonas = gpd.read_file(ZONAS_R8).to_crs(CRS_METRICO).set_index("zona_id")
    refs = gpd.read_file(REFERENCIAS_R8).to_crs(CRS_METRICO).set_index("referencia_id")
    magnitudes = pd.read_csv(MAGNITUDES).set_index("polo_id")

    filas, capa = [], []

    for receta in RECETAS:
        zona = receta["zona"]
        contenedor = magnitudes.contenedor.get(zona)
        provisorio = limpia(zonas.geometry.loc[contenedor])
        ha_prov = provisorio.area / 10_000
        loc_prov = cj.locales(provisorio)

        print("=" * 96)
        print(f"{zona} - {receta['nombre']}   ({receta['pct']} % del barrio concentrado; "
              f"provisorio = {contenedor}, {ha_prov:,.2f} ha, {loc_prov} locales)")
        print("=" * 96)
        print(f"  perimetro escrito: {receta['fuente']}\n")

        cerradas, notas = [], []
        for pieza in receta["piezas"]:
            tramo, poligono, detalle = resolver_pieza(cj, pieza)
            if poligono is None:
                print(f"  [NO CIERRA] {pieza['nombre']}: {detalle}")
                notas.append(f"{pieza['nombre']}: {detalle}")
                continue
            n_mz = len(cj.frentistas(tramo))
            print(f"  [CIERRA]  {pieza['nombre']}")
            print(f"            eje {tramo.length:,.0f} m -> {n_mz} manzanas frentistas -> "
                  f"{poligono.area / 10_000:,.2f} ha, {cj.locales(poligono)} locales")
            cerradas.append((pieza["nombre"], detalle, tramo, poligono))

        for nombre, motivo in receta.get("sin_cerrar", []):
            print(f"  [NO CIERRA] {nombre}: {motivo}")

        # ---- verificaciones que el propio texto de la ficha regala ----------------------
        if receta.get("largo_declarado_m") and cerradas:
            declarado = receta["largo_declarado_m"]
            medido = cerradas[0][2].length
            print(f"\n  R12 - largo declarado por la fuente {declarado} m contra el medido "
                  f"{medido:,.0f} m: {medido - declarado:+,.0f} m "
                  f"({abs(medido - declarado) / declarado * 100:.1f} %)")
            notas.append(f"largo declarado {declarado} m, medido {medido:,.0f} m")

        if receta.get("control_doble") and cerradas:
            cd = receta["control_doble"]
            otro = cj.tramo_entre(cd["calle"], cd["corte_a"], cd["corte_b"])
            base = next((t for n, _, t, _ in cerradas if n == cd["contra"]), None)
            if otro is not None and base is not None:
                print(f"\n  R12 - la misma pieza escrita dos veces. Por alturas: {base.length:,.0f} m. "
                      f"Por calles de corte ({cd['nombre']}): {otro.length:,.0f} m. "
                      f"Diferencia {otro.length - base.length:+,.0f} m")
                notas.append(f"la ficha da la misma pieza por alturas ({base.length:,.0f} m) y "
                             f"por calles de corte ({otro.length:,.0f} m)")

        for calle, que_es in receta.get("cruces", []):
            eje = cj.eje(calle)
            if eje is None or not cerradas:
                continue
            d = min(t.distance(eje) for _, _, t, _ in cerradas)
            print(f"  control - {calle} ({que_es}): a {d:,.0f} m del tramo trazado "
                  f"-> {'cruza' if d < 1 else 'NO cruza'}")
            if d >= 1:
                notas.append(f"{calle} no cruza el tramo trazado: queda a {d:,.0f} m")

        union = limpia(unary_union([p for _, _, _, p in cerradas])) if cerradas else None

        if receta.get("remates") and union is not None:
            adentro = afuera = 0
            lejos = []
            for calle, altura in receta["remates"]:
                punto = cj.punto_de_altura(calle, altura)
                if punto is None:
                    continue
                if union.contains(punto):
                    adentro += 1
                else:
                    afuera += 1
                    lejos.append((f"{calle} {altura}", union.distance(punto)))
            print(f"\n  los remates que nombra la ficha: {adentro} adentro del poligono, "
                  f"{afuera} afuera")
            for etiqueta, d in sorted(lejos, key=lambda x: -x[1])[:5]:
                print(f"      {etiqueta:<28} a {d:,.0f} m")
            if afuera:
                notas.append(f"{afuera} de {adentro + afuera} remates caen fuera del poligono "
                             f"(el mas lejano a {max(d for _, d in lejos):,.0f} m)")

        # ---- R12: contencion por SUPERFICIE PERDIDA, no por predicado -------------------
        ha_nuevo = loc_nuevo = fuera_ha = 0.0
        hitos_dentro = hitos_barrio = 0
        if union is not None:
            ha_nuevo = union.area / 10_000
            loc_nuevo = cj.locales(union)
            dentro = limpia(union.intersection(provisorio))
            # El maximo con cero no es cosmetico: la resta de dos areas casi iguales sale
            # negativa por punto flotante y «-0,00 ha fuera» se lee como un dato, no como ruido.
            fuera_ha = max(0.0, ha_nuevo - dentro.area / 10_000)
            print(f"\n  el poligono trazado: {ha_nuevo:,.2f} ha - {loc_nuevo} locales")
            print(f"  contra el provisorio ({contenedor}): "
                  f"{ha_nuevo - ha_prov:+,.2f} ha - {loc_nuevo - loc_prov:+d} locales "
                  f"({ha_nuevo / ha_prov * 100:.1f} % de la superficie del barrio, "
                  f"{loc_nuevo / loc_prov * 100:.1f} % de sus locales)")
            print(f"  R12 - superficie del trazado que queda FUERA del provisorio: "
                  f"{fuera_ha:,.2f} ha ({fuera_ha / ha_nuevo * 100:.1f} %) -> "
                  f"{'contenido' if fuera_ha < 0.01 else 'NO contenido: se sale del barrio'}")
            if fuera_ha >= 0.01:
                reparto = cj.reparto_por_barrio(union)
                detalle = " · ".join(f"{n} {p:.0f} %" for n, p, _ in reparto)
                print(f"       se reparte entre: {detalle}")
                notas.append(f"el trazado se sale del barrio contenedor: {fuera_ha:,.2f} ha "
                             f"({fuera_ha / ha_nuevo * 100:.0f} %); reparto por barrio: {detalle}")

            # ---- la prueba de Almagro: contiene el trazado los hitos de su propia ficha ----
            en_barrio = cj.hitos_en(provisorio)
            en_trazado = cj.hitos_en(union)
            print(f"  hitos con punto: {len(en_trazado)} de los {len(en_barrio)} del provisorio "
                  f"caen dentro del trazado")
            if en_trazado:
                print(f"      adentro: {', '.join(en_trazado)}")
            afuera = cj.hitos_cerca(union, provisorio)
            if afuera:
                print("      afuera, con la distancia al borde: "
                      + " · ".join(f"{n} {d:,.0f} m" for n, d in afuera))
            hitos_dentro, hitos_barrio = len(en_trazado), len(en_barrio)
            if hitos_barrio and not hitos_dentro:
                cerca = afuera[0] if afuera else None
                notas.append(
                    f"PRUEBA DE ALMAGRO: el trazado no contiene NINGUNO de los {hitos_barrio} "
                    f"hitos del barrio"
                    + (f"; el mas cercano es {cerca[0]} a {cerca[1]:,.0f} m" if cerca else ""))

            for otra in receta.get("contra", []):
                g = limpia(refs.geometry.loc[otra]) if otra in refs.index else None
                if g is None:
                    continue
                inter = limpia(union.intersection(g))
                print(f"  contra {otra}: comparten {inter.area / 10_000:,.2f} ha "
                      f"({inter.area / union.area * 100:.1f} % del trazado, "
                      f"{inter.area / g.area * 100:.1f} % de {otra}) y "
                      f"{cj.locales(inter)} locales")
                if inter.area > 0:
                    notas.append(f"se pisa con {otra}: {inter.area / 10_000:,.2f} ha y "
                                 f"{cj.locales(inter)} locales, sin repartir")

            for i, (nombre, detalle, _, poligono) in enumerate(cerradas):
                capa.append(dict(
                    zona_id=zona, nombre=receta["nombre"], pieza=nombre,
                    fuente_del_perimetro=receta["fuente"],
                    metodo=f"manzanas frentistas del callejero sobre {detalle} "
                           f"(frente minimo {FRENTE_MIN_M:.0f} m)",
                    ha=round(poligono.area / 10_000, 2), n_locales=cj.locales(poligono),
                    geometry=poligono))

        # ---- lecturas declaradas y NO adoptadas -----------------------------------------
        for lectura in receta.get("lecturas", []):
            _, poligono, detalle = resolver_pieza(cj, lectura)
            if poligono is None:
                print(f"  lectura declarada - {lectura['nombre']}: no resuelve ({detalle})")
                continue
            print(f"  lectura declarada, NO adoptada - {lectura['nombre']}: "
                  f"{poligono.area / 10_000:,.2f} ha, {cj.locales(poligono)} locales")

        # ---- veredicto -------------------------------------------------------------------
        n_piezas = len(receta["piezas"]) + len(receta.get("sin_cerrar", []))
        if cerradas and not receta.get("sin_cerrar"):
            cerrado = "si"
        elif cerradas:
            cerrado = "parcial"
        else:
            cerrado = "no"
        que_falta = "; ".join(f"{n}: {m}" for n, m in receta.get("sin_cerrar", []))
        if receta.get("que_falta_extra"):
            que_falta = "; ".join(x for x in (que_falta, receta["que_falta_extra"]) if x)
        if receta.get("aviso"):
            que_falta += f" - {receta['aviso']}"
        if not que_falta:
            que_falta = "nada: el texto cerro todas las piezas que nombra"

        print(f"\n  VEREDICTO: cerrado = {cerrado.upper()}  "
              f"({len(cerradas)} de {n_piezas} piezas)")
        if cerrado == "parcial":
            print("             la ficha NO publica cifra de zona: lo trazado es una pieza, "
                  "no el polo")
        print()

        filas.append(dict(
            zona_id=zona, nombre=receta["nombre"],
            pct_del_barrio_concentrado=receta["pct"],
            ha=round(ha_nuevo, 2) if union is not None else "",
            n_locales=loc_nuevo if union is not None else "",
            ha_del_provisorio=round(ha_prov, 2),
            n_locales_del_provisorio=loc_prov,
            delta_ha=round(ha_nuevo - ha_prov, 2) if union is not None else "",
            delta_locales=(loc_nuevo - loc_prov) if union is not None else "",
            ha_fuera_del_provisorio=round(fuera_ha, 2) if union is not None else "",
            hitos_en_el_trazado=hitos_dentro if union is not None else "",
            hitos_en_el_provisorio=cj.hitos_en(provisorio).__len__(),
            piezas_cerradas=len(cerradas), piezas_del_texto=n_piezas,
            cerrado_si_no=cerrado,
            que_falta=que_falta,
            provisorio=contenedor,
            fuente_del_perimetro=receta["fuente"],
            metodo=("manzanas frentistas del callejero; borde sobre calles por construccion"
                    if cerradas else "sin trazado: se mantiene el poligono administrativo"),
            notas="; ".join(notas),
        ))

    # ---- sensibilidad al unico parametro del metodo -------------------------------------
    print("=" * 96)
    print("SENSIBILIDAD AL FRENTE MINIMO - el unico parametro que este metodo tiene")
    print("=" * 96)
    print(f"{'zona':<8}" + "".join(f"{f'{f:.0f} m':>14}" for f in FRENTE_SENSIBILIDAD))
    for receta in RECETAS:
        if not receta["piezas"]:
            continue
        linea = f"{receta['zona']:<8}"
        for frente in FRENTE_SENSIBILIDAD:
            piezas = []
            for pieza in receta["piezas"]:
                tramo, _, _ = resolver_pieza(cj, pieza)
                if tramo is None:
                    continue
                fr = cj.frentistas(tramo, frente_min=frente)
                if fr:
                    piezas.append(unary_union([c for _, _, c in fr]))
            ha = limpia(unary_union(piezas)).area / 10_000 if piezas else 0
            linea += f"{ha:>11,.2f} ha"
        print(linea)

    # ---- salidas -------------------------------------------------------------------------
    campos = ["zona_id", "nombre", "pct_del_barrio_concentrado", "ha", "n_locales",
              "ha_del_provisorio", "n_locales_del_provisorio", "delta_ha", "delta_locales",
              "ha_fuera_del_provisorio", "hitos_en_el_trazado", "hitos_en_el_provisorio",
              "piezas_cerradas", "piezas_del_texto", "cerrado_si_no",
              "que_falta", "provisorio", "fuente_del_perimetro", "metodo", "notas"]
    destino = SALIDA / "perimetros_18.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)

    geo = SALIDA / "geometria" / "perimetros_18.geojson"
    geo.parent.mkdir(exist_ok=True)
    gpd.GeoDataFrame(capa, geometry="geometry", crs=CRS_METRICO).to_crs(CRS_SALIDA).to_file(
        geo, driver="GeoJSON")

    cerrados = [f for f in filas if f["cerrado_si_no"] == "si"]
    parciales = [f for f in filas if f["cerrado_si_no"] == "parcial"]
    print(f"\nEscrito: {destino.name} ({len(filas)} filas) y geometria/{geo.name} "
          f"({len(capa)} piezas, {CRS_SALIDA})")
    print(f"  cerradas: {len(cerrados)}  ·  parciales: {len(parciales)}  ·  "
          f"sin trazar: {len(filas) - len(cerrados) - len(parciales)}")


if __name__ == "__main__":
    main()
