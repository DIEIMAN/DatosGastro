# -*- coding: utf-8 -*-
"""Que dato exacto le falta a cada pieza que no cerro, calle por calle, para que alguien lo busque.

DE DONDE SALE
-------------
La ronda 15 cerro 7 de los 18, dejo 4 en «parcial» y 7 sin trazar, y dijo que a cinco de los siete
les faltaban «cuatro palabras: un rango de alturas». Esto convierte esa frase en una lista
accionable: **una fila por pieza que no cerro**, con el dato que falta, la frase de la ficha donde
esta el hueco, y quien puede conseguirlo.

Incluye tambien las piezas sin cerrar de las cuatro zonas «parcial», porque son las que impiden
que esas fichas publiquen cifra. La columna `estado_de_la_zona` las distingue.

LO QUE ESTA CORRIDA MIDE, Y LO QUE NO
--------------------------------------
**Mide** los candidatos: cuando el atlas ya tiene en disco una altura o un tramo que podria llenar
el hueco, se mide que daria. **No los adopta.** Un candidato medido es material para que Diego
decida, no una delimitacion: varios vienen del eje del IDECBA o de las direcciones de los
referentes, y las dos cosas describen otro objeto que el perimetro del polo.

La unica excepcion declarada es Z35 Balvanera, que **no tiene ningun perimetro escrito**: ahi la
tarea pedia redactar uno desde la evidencia de su propia ficha, y lo redactado va en la columna
`propuesta_de_redaccion`, medido y **sin adoptar**.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import sys
from pathlib import Path

import geopandas as gpd
from shapely.ops import polygonize, unary_union

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"
FRENTE_MIN_M = 20.0

FICHA_VII = "desde_cowork/evidencia_2026/SECCION_VII_ZONAS_INCORPORADAS.md"
FICHA_SUR = "desde_cowork/evidencia_2026/FICHAS_SUR_NUEVAS.md"
CORPUS = "desde_cowork/evidencia_2026/fichas_corpus_polos.csv · campo perimetro_textual"


def limpia(g):
    return g if g.is_valid else g.buffer(0)


# --------------------------------------------------------------------------- las filas
#
# `medir` es opcional y siempre es un CANDIDATO, nunca una adopcion.
FILAS = [
    # ---------------------------------------------------------------- los siete sin trazar
    dict(zona="Z27", nombre="Villa Santa Rita", estado="no", pieza="el conjunto",
         falta="Un rango de alturas sobre Av. Alvarez Jonte, o dos calles de corte.",
         frase="«Puntos dispersos con anclaje en Av. Alvarez Jonte, que es el limite sur y oeste "
               "del barrio y no su columna interior.»",
         donde=CORPUS, quien="Diego / relevamiento",
         medir=None,
         nota="La ficha declara que la via de densidad NO abre -«seis locales dispersos en diez "
              "cuadras es un conjunto, no una densidad»-, asi que el hueco no es de redaccion: "
              "es que la zona todavia no tiene una concentracion que delimitar."),
    dict(zona="Z39", nombre="Parque Avellaneda", estado="no", pieza="el anillo del parque",
         falta="O el rango de alturas sobre cada avenida -si es un corredor en L-, o cambiar la "
               "avenida: medido, Av. Olivera NO bordea el parque.",
         frase="«El anillo del Parque Avellaneda, sobre Av. Olivera y Av. Lacarra.»",
         donde=FICHA_VII, quien="Diego (decision de lectura); el callejero ya dio la medicion",
         medir=dict(tipo="parque"),
         nota="RELECTURA DE LA FUENTE: Time Out habla de bodegones SOBRE Olivera y Lacarra, que "
              "es un corredor; «anillo» es palabra del atlas. Y las dos avenidas se cruzan en un "
              "punto: son dos lados de una esquina."),
    dict(zona="Z53", nombre="La Boca · Caminito y Vuelta de Rocha", estado="no",
         pieza="el entorno de Caminito y la Vuelta de Rocha",
         falta="El tramo de Av. Don Pedro de Mendoza, en alturas o entre calles de corte.",
         frase="«Entorno de Caminito y la Vuelta de Rocha, sobre Av. Don Pedro de Mendoza.»",
         donde=FICHA_SUR, quien="Diego da el tramo; el callejero cierra el resto",
         medir=dict(tipo="caminito"),
         nota="PROPUESTA PARA LA CARA DEL SUR: la Vuelta de Rocha no esta en el callejero porque "
              "es un recodo del Riachuelo, pero el objeto que cierra esa cara SI existe y es "
              "auditable: el limite oficial del barrio de La Boca sobre el Riachuelo, de "
              "caba_barrios.geojson, con sha256 y procedencia. Y Caminito SI esta en el callejero."),
    dict(zona="Z33", nombre="Mataderos", estado="no", pieza="la Feria y el Mercado de Hacienda",
         falta="Una extension. El texto da el cruce de dos avenidas y nada mas.",
         frase="«la Feria y el Mercado de Hacienda, en Av. Lisandro de la Torre y Av. de los "
               "Corrales»",
         donde=FICHA_VII, quien="fuente publica: la Feria tiene perimetro de ocupacion declarado",
         medir=None,
         nota="La Feria ocupa calles cortadas los fines de semana: su perimetro es un dato "
              "administrativo que existe fuera del atlas."),
    dict(zona="Z33", nombre="Mataderos", estado="no", pieza="el conjunto de referentes dispersos",
         falta="Una extension, y antes que eso la decision de si es una pieza o no.",
         frase="«y un conjunto de referentes dispersos» · «sus dos piezas estan a mas de un "
               "kilometro»",
         donde=FICHA_VII, quien="Diego",
         medir=None,
         nota="La propia ficha dice que «una densidad promedio sobre el conjunto no describe "
              "ninguna de las dos»."),
    dict(zona="Z35", nombre="Balvanera · Once", estado="no", pieza="la zona entera",
         falta="TODO el perimetro: la ficha no nombra ninguna calle.",
         frase="«Perimetro. En revision. Hay trayectoria e identidad de colectividad reales, y la "
               "densidad actual no esta documentada.»",
         donde=FICHA_VII, quien="quien escribe la ficha, sobre la propuesta medida de al lado",
         medir=dict(tipo="balvanera"),
         propuesta="Eje Tucuman entre el 2379 y el 2755, ambas aceras, con transversal sobre Paso "
                   "al 700.",
         nota="REDACTADA desde las puertas que la propia ficha ya lista, todas del padron oficial "
              "de 2015: Sucat David (Tucuman 2379), El Jaial (2620), Al Galope (2633), Lalo "
              "Helueni (2755) y Yaffo Kosher (Paso 747). Las cinco resuelven en el callejero y "
              "Paso cruza el tramo. NO ADOPTADA: es una propuesta de redaccion, no una "
              "delimitacion, y el padron es de 2015."),
    dict(zona="Z40", nombre="Nueva Pompeya y Parque Patricios", estado="no",
         pieza="Av. Caseros y el Distrito Tecnologico",
         falta="Un rango de alturas sobre Av. Caseros.",
         frase="«Tres piezas: Av. Caseros y el Distrito Tecnologico, ...»",
         donde=FICHA_VII, quien="Diego; o fuente publica: la Ley 2972 fija el perimetro del "
                                "Distrito Tecnologico, que el repositorio NO tiene",
         medir=dict(tipo="eje", calle="CASEROS AV.", desde=2601, hasta=3199),
         nota="Los dos unicos numeros que el atlas ya tiene para esta pieza son el eje del IDECBA "
              "-Av. Caseros 2601-2999- y El Globito en el 3159. El candidato medido usa 2601-3199, "
              "y adoptarlo seria decidir que el polo coincide con el eje relevado: exactamente lo "
              "que Mataderos no dejo hacer."),
    dict(zona="Z40", nombre="Nueva Pompeya y Parque Patricios", estado="no",
         pieza="Av. Saenz y el Mercado de Pompeya",
         falta="Un rango de alturas sobre Av. Saenz.",
         frase="«..., Av. Saenz y el Mercado de Pompeya, ...»",
         donde=FICHA_VII, quien="Diego",
         medir=dict(tipo="eje", calle="SAENZ AV.", desde=790, hasta=1399),
         nota="ES LA MISMA PIEZA QUE Z54. Candidatos en disco: el Mercado de Pompeya en Av. Saenz "
              "790 y el eje del IDECBA 801-1399."),
    dict(zona="Z40", nombre="Nueva Pompeya y Parque Patricios", estado="no",
         pieza="Barrio Charrua",
         falta="El cuarto borde, o el perimetro del Barrio General San Martin.",
         frase="«tiene el mejor perimetro fisico del Atlas: Av. Bonorino, Av. Fernandez de la Cruz "
               "y las vias del Belgrano Sur»",
         donde=CORPUS, quien="fuente publica: el perimetro del Barrio General San Martin",
         medir=dict(tipo="charrua"),
         nota="MEDIDO Y NO CIERRA, por dos motivos: las vias del Belgrano Sur no son una linea del "
              "callejero -solo hay segmentos con marca de cruce-, y las dos avenidas SE CRUZAN. "
              "Con el borde del barrio como tercer lado la cara que sale es Nueva Pompeya entera. "
              "Y la ficha declara que ahi no hay oferta comercial documentada: sumarlo agregaria "
              "superficie sin locales."),
    dict(zona="Z54", nombre="Nueva Pompeya · eje Av. Saenz", estado="no", pieza="el eje Av. Saenz",
         falta="La extension del eje. Una sola altura -el 790, que es el mercado- no es un tramo.",
         frase="«Eje Av. Saenz, con nucleo en el Mercado de Pompeya, Av. Saenz 790.»",
         donde=FICHA_SUR, quien="Diego",
         medir=None,
         nota="LA FUSION CON Z40 NO NECESITA GEOMETRIA PARA DECIDIRSE: el perimetro escrito de Z40 "
              "ya lista «Av. Saenz y el Mercado de Pompeya» como su segunda pieza, y Z54 es «eje "
              "Av. Saenz, con nucleo en el Mercado de Pompeya». Son el mismo eje y el mismo "
              "objeto, a la misma direccion. Lo que espera al perimetro de Z40 es la CIFRA, no la "
              "decision."),
    # ---------------------------------------------- las piezas sin cerrar de las «parcial»
    dict(zona="Z41", nombre="Nunez", estado="parcial", pieza="corredor bajo el viaducto Mitre",
         falta="Los dos extremos del tramo, y antes el reparto con las otras dos zonas que lo "
               "comparten.",
         frase="«el corredor bajo el viaducto Mitre» · «el extremo sur del viaducto toca la "
               "referencia de Federico Lacroze y el tramo entre Blanco Encalada y Monroe cae en "
               "Belgrano»",
         donde=FICHA_VII, quien="Diego (el reparto); el callejero no tiene la traza del viaducto",
         medir=dict(tipo="viaducto"),
         nota="YA SE DIBUJO UNA VEZ, y por eso no cuenta: seis_vias/nunez_corredor_viaducto.geojson "
              "es «aprox. recta entre cabeceras» con buffer de 150 m. Ese borde es una propiedad "
              "del instrumento, que es justo lo que esta ronda no admite."),
    dict(zona="Z41", nombre="Nunez", estado="parcial",
         pieza="nucleo de bistros en Campos Salles, O'Higgins y Grecia",
         falta="Un rango de alturas o calles de corte para cada una de las tres.",
         frase="«y un nucleo disperso de bistros en Campos Salles, O'Higgins y Grecia»",
         donde=FICHA_VII, quien="Diego / relevamiento", medir=None,
         nota="El texto lo llama disperso. Ness (Grecia 3691) y Evelia (Campos Salles 1712) dan "
              "dos alturas, pero delimitar por los referentes no es delimitar por el perimetro."),
    dict(zona="Z46", nombre="Retiro", estado="parcial",
         pieza="nucleo institucional de Plaza San Martin y Florida",
         falta="El tramo de Florida. La calle entera mide mas de un kilometro.",
         frase="«el nucleo institucional de Plaza San Martin y Florida»",
         donde=FICHA_VII, quien="Diego", medir=dict(tipo="eje", calle="FLORIDA", desde=800, hasta=1005),
         nota="Es la pieza mas barata de las once: dos de sus hitos quedaron a 5 m y a 59 m del "
              "trazado actual -Florida Garden (Florida 899) y Plaza Bar (Florida 1005)-, asi que "
              "las alturas que la acotan ya estan en la propia ficha."),
    dict(zona="Z37", nombre="Almagro", estado="parcial", pieza="nucleo de Guardia Vieja y Bulnes",
         falta="Cuales son las tres cuadras.",
         frase="«En Guardia Vieja hay cuatro locales en tres cuadras, dos de ellos enfrentados en "
               "la misma esquina - el 3601 y el 3602.»",
         donde=FICHA_VII, quien="Diego / relevamiento",
         medir=dict(tipo="eje", calle="GUARDIA VIEJA", desde=3500, hasta=3800),
         nota="El texto da dos alturas de la MISMA cuadra y dice que son tres cuadras, sin decir "
              "cuales. El candidato medido supone 3500-3800 y es una suposicion, no la ficha."),
    dict(zona="Z37", nombre="Almagro", estado="parcial", pieza="nodo de Rivadavia y Medrano",
         falta="Una extension. El texto da una esquina.",
         frase="«y el nodo de Rivadavia y Medrano»",
         donde=FICHA_VII, quien="Diego", medir=None,
         nota="Las Violetas (Av. Rivadavia 3899) es el hito de esta pieza y quedo a 697 m del "
              "trazado actual."),
    dict(zona="Z44", nombre="Villa Ortuzar", estado="parcial",
         pieza="nucleo secundario de Plaza 25 de Agosto",
         falta="Por donde va el cuarto lado.",
         frase="«con nucleo secundario en Plaza 25 de Agosto - Giribone, 14 de Julio, Charlone y "
               "Bauness»",
         donde=FICHA_VII, quien="Diego / callejero",
         medir=dict(tipo="plaza"),
         nota="MEDIDO Y NO CIERRA: las cuatro calles no encierran ninguna cara. Bauness queda a "
              "184 m de Giribone y a 249 m de 14 de Julio; ni siquiera las otras tres cierran."),
]


class Medidor:
    def __init__(self):
        sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
        from callejero_canonico import cargar, eje_canonico, familias  # noqa: E402
        from polos_soporte import puntos_base, sin_tildes  # noqa: E402
        self._eje_canonico, self._sin_tildes = eje_canonico, sin_tildes
        self.calles = cargar()
        self.familias = familias(self.calles)
        self.puntos = puntos_base()
        red = unary_union(list(self.calles.geometry))
        self.manzanas = gpd.GeoSeries([limpia(p) for p in polygonize(red)], crs=CRS_METRICO)
        self._sidx = self.manzanas.sindex

    def segmentos(self, nombre):
        clave = self._sin_tildes(nombre)
        sub = self.calles[self.calles.clave.isin(self.familias.get(clave, {clave}))]
        if sub.empty:
            raise SystemExit(f"«{nombre}» no esta en el callejero")
        return sub

    def eje(self, nombre):
        return self._eje_canonico(self.calles, nombre, self.familias)

    def tramo(self, nombre, desde, hasta):
        elegidos = []
        for r in self.segmentos(nombre).itertuples():
            alturas = [v for v in (r.alt_izqini, r.alt_izqfin, r.alt_derini, r.alt_derfin)
                       if v and v > 0]
            if alturas and max(alturas) > desde and min(alturas) < hasta:
                elegidos.append(r.geometry)
        return unary_union(elegidos) if elegidos else None

    def frentistas(self, tramo):
        return [self.manzanas.iloc[i] for i in self._sidx.query(tramo.buffer(2))
                if self.manzanas.iloc[i].boundary.intersection(tramo).length >= FRENTE_MIN_M]

    def corredor(self, calle, desde, hasta):
        t = self.tramo(calle, desde, hasta)
        if t is None:
            return None, f"{calle} {desde}-{hasta}: sin tramo en el callejero"
        piezas = self.frentistas(t)
        if not piezas:
            return None, f"{calle} {desde}-{hasta}: sin manzanas frentistas"
        g = limpia(unary_union(piezas))
        return g, (f"{calle} {desde}-{hasta}: eje {t.length:,.0f} m -> {len(piezas)} manzanas -> "
                   f"{g.area / 1e4:,.2f} ha, {int(self.puntos.within(g).sum())} locales")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 92)
    print("RONDA 16 · que dato le falta a cada pieza que no cerro")
    print("=" * 92 + "\n")
    m = Medidor()
    barrios = gpd.read_file(BASE / "insumos" / "caba_barrios.geojson").to_crs(CRS_METRICO)

    filas = []
    for fila in FILAS:
        candidato = ""
        receta = fila.get("medir")
        if receta:
            tipo = receta["tipo"]
            if tipo == "eje":
                _, candidato = m.corredor(receta["calle"], receta["desde"], receta["hasta"])
            elif tipo == "parque":
                ol, la = m.eje("OLIVERA AV."), m.eje("LACARRA AV.")
                di = m.eje("DIRECTORIO AV.")
                cand = [(self_g.boundary.intersection(la).length, self_g)
                        for self_g in (m.manzanas.iloc[i] for i in m._sidx.query(la.buffer(5)))
                        if self_g.area / 1e4 > 20]
                parque = max(cand, key=lambda x: x[0])[1]
                candidato = (f"la cara del parque mide {parque.area / 1e4:,.2f} ha con "
                             f"{int(m.puntos.within(parque).sum())} locales; frente sobre "
                             f"Av. Lacarra {parque.boundary.intersection(la).length:,.0f} m y "
                             f"sobre Av. Directorio {parque.boundary.intersection(di).length:,.0f} m; "
                             f"sobre Av. Olivera {parque.boundary.intersection(ol).length:,.0f} m "
                             f"-> Av. Olivera la toca en un punto y NO la bordea")
            elif tipo == "caminito":
                dpm, cam = m.eje("DON PEDRO DE MENDOZA AV."), m.eje("CAMINITO")
                boca = limpia(unary_union(
                    [limpia(g) for g in barrios[barrios.BARRIO.astype(str).str.upper()
                                                .str.contains("BOCA")].geometry]))
                caras = [p for p in polygonize(unary_union([dpm, boca.boundary])) if p.area > 1000]
                candidato = (f"Caminito SI esta en el callejero ({cam.length:,.0f} m) y toca "
                             f"Av. Don Pedro de Mendoza a {cam.distance(dpm):.0f} m; la avenida "
                             f"({dpm.length:,.0f} m) con el limite oficial del barrio cierra "
                             f"{len(caras)} cara(s): el objeto del sur existe, falta la extension")
            elif tipo == "balvanera":
                g1, d1 = m.corredor("TUCUMAN", 2379, 2755)
                g2, d2 = m.corredor("PASO", 700, 799)
                u = limpia(unary_union([g for g in (g1, g2) if g is not None]))
                candidato = (f"{d1} | {d2} | union de las dos: {u.area / 1e4:,.2f} ha, "
                             f"{int(m.puntos.within(u).sum())} locales")
            elif tipo == "charrua":
                bon = m.eje("BONORINO, ESTEBAN, CNEL. AV.")
                fdc = m.eje("FERNANDEZ DE LA CRUZ, F., GRAL. AV.")
                pom = limpia(unary_union(
                    [limpia(g) for g in barrios[barrios.BARRIO.astype(str).str.upper()
                                                == "NUEVA POMPEYA"].geometry]))
                caras = sorted([limpia(p) for p in polygonize(unary_union([bon, fdc, pom.boundary]))
                                if p.area > 1000], key=lambda p: -p.area)
                candidato = (f"Av. Bonorino y Av. Fernandez de la Cruz SE CRUZAN "
                             f"({bon.distance(fdc):.0f} m); con el borde del barrio la cara mayor "
                             f"es {caras[0].area / 1e4:,.2f} ha, o sea Nueva Pompeya entera "
                             f"({pom.area / 1e4:,.2f} ha). No cierra el enclave.")
            elif tipo == "plaza":
                ejes = {n: m.eje(n) for n in ["GIRIBONE", "14 DE JULIO", "CHARLONE", "BAUNESS"]}
                caras = [p for p in polygonize(unary_union(list(ejes.values()))) if p.area > 1000]
                pares = [(a, b, ejes[a].distance(ejes[b]))
                         for i, a in enumerate(ejes) for b in list(ejes)[i + 1:]]
                lejos = max(pares, key=lambda x: x[2])
                candidato = (f"las cuatro calles cierran {len(caras)} caras; el par mas separado es "
                             f"{lejos[0]} y {lejos[1]} a {lejos[2]:,.0f} m")
            elif tipo == "viaducto":
                ruta = BASE / "seis_vias" / "nunez_corredor_viaducto.geojson"
                capa = gpd.read_file(ruta).to_crs(CRS_METRICO)
                r = capa.iloc[0]
                candidato = (f"existe {ruta.name}: «{r.que_es}», buffer {r.buffer_m:.0f} m, "
                             f"{capa.geometry.iloc[0].area / 1e4:,.2f} ha. El borde lo pone el "
                             f"buffer, no la evidencia: no cuenta como perimetro")
        if candidato:
            print(f"{fila['zona']} · {fila['pieza']}\n    {candidato}\n")
        filas.append(dict(
            zona_id=fila["zona"], nombre=fila["nombre"], estado_de_la_zona=fila["estado"],
            pieza=fila["pieza"], dato_que_falta=fila["falta"],
            frase_de_la_ficha_con_el_hueco=fila["frase"], donde_esta_esa_frase=fila["donde"],
            quien_lo_puede_conseguir=fila["quien"],
            propuesta_de_redaccion=fila.get("propuesta", ""),
            candidato_medido_NO_adoptado=candidato, nota=fila["nota"]))

    destino = SALIDA / "que_falta_por_zona.csv"
    campos = ["zona_id", "nombre", "estado_de_la_zona", "pieza", "dato_que_falta",
              "frase_de_la_ficha_con_el_hueco", "donde_esta_esa_frase", "quien_lo_puede_conseguir",
              "propuesta_de_redaccion", "candidato_medido_NO_adoptado", "nota"]
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)

    sin_trazar = sum(1 for f in filas if f["estado_de_la_zona"] == "no")
    print("=" * 92)
    print(f"Escrito: {destino.name} · {len(filas)} piezas "
          f"({sin_trazar} de zonas sin trazar, {len(filas) - sin_trazar} de zonas parciales)")
    print(f"  zonas distintas: {len(set(f['zona_id'] for f in filas))}")
    cuantos = sum(1 for f in filas if "rango de alturas" in f["dato_que_falta"].lower()
                  or "tramo" in f["dato_que_falta"].lower())
    print(f"  piezas a las que les falta SOLO un tramo o rango de alturas: {cuantos}")


if __name__ == "__main__":
    main()
