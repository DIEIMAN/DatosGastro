# -*- coding: utf-8 -*-
"""Los cuatro sin borde propio: qué borde sale de las calles que su propia página nombra.

QUIÉNES SON Y POR QUÉ ESTÁN JUNTOS
-----------------------------------
Retiro, Núñez y Villa Santa Rita publican el polígono de su barrio. Colegiales lo publica también
—su contorno y el del barrio coinciden en el 99,93 %— y desde esta ronda es **subzona de
Chacagiales**, así que su borde importa igual, pero como subzona.

LA REGLA, ESCRITA ANTES DE MEDIR
---------------------------------
El borde se arma **solamente con las calles que el bloque «Dónde está» de esa página nombra**,
leídas de `SECCION_VII_ZONAS_INCORPORADAS.md`. Nada más entra: ni el borde del barrio, ni una
transversal razonable, ni la calle que cualquiera pondría. Si con lo que la página escribe no se
cierra una figura, **la salida es decir qué calle falta nombrar**, no dibujarla.

Eso vuelve al control útil de verdad: lo que devuelve no es un mapa, es una lista de qué tiene
que escribir cada página para que su borde se pueda trazar sin que nadie invente nada.

Un nombre se resuelve contra el callejero oficial o corta la corrida. Los nombres propios de
plazas, mercados, viaductos y enclaves **no son calles** y se declaran aparte: son la mitad de la
razón por la que estas cuatro páginas no cierran.

CÓMO SE ARMA CADA PIEZA
------------------------
  - **corredor** · la página da una calle y sus dos extremos (otras dos calles, o dos alturas).
    El borde son las manzanas frentistas del tramo, con el frente mínimo de 20 m de siempre, que
    es la regla con la que se trazó todo lo demás del atlas.
  - **recinto** · la página da calles que se cruzan entre sí y encierran una cara. El borde es
    esa cara.
  - **no cierra** · todo lo demás, con el motivo y la calle que falta.

EPSG:5347 para medir, EPSG:4326 para guardar. Cero requests.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import polygonize, unary_union

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
ROOT = BARRIDO.parents[1]
sys.path.insert(0, str(BARRIDO / "ronda_17"))
sys.path.insert(0, str(BARRIDO / "ronda_20"))
sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))

import geometria_vigente_20 as gv  # noqa: E402
from geometria_vigente_20 import limpia  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()
SECCION = BARRIDO / "desde_cowork" / "evidencia_2026" / "SECCION_VII_ZONAS_INCORPORADAS.md"
FRENTE = 20.0

# --------------------------------------------------------------------------------------------
# LAS CUATRO PÁGINAS.
#
#   `nombra`      lo que la página escribe, tal cual, con su clave en el callejero oficial.
#                 clave None = el nombre no es una calle (plaza, mercado, viaducto, enclave).
#   `piezas`      lo que se puede armar, y con qué.
#   `no_cierran`  lo que la página describe y no cierra, con qué calle le falta.
# --------------------------------------------------------------------------------------------
PAGINAS = [
    dict(
        polo="Z46", pagina="Retiro",
        nombra=[("Florida", "FLORIDA"), ("Juncal", "JUNCAL"), ("Esmeralda", "ESMERALDA"),
                ("Maipú", "MAIPU"), ("Paraguay", "PARAGUAY"),
                ("M. T. de Alvear", "ALVEAR MARCELO T DE"), ("Av. Córdoba", "CORDOBA AV"),
                ("Arroyo", "ARROYO"),
                ("Plaza San Martín", None), ("Plaza Carlos Pellegrini", None)],
        piezas=[
            dict(nombre="el núcleo coreano y asiático", tipo="recinto",
                 calles=["MAIPU", "ESMERALDA", "PARAGUAY", "ALVEAR MARCELO T DE"],
                 de_donde=("«sobre Maipú, Esmeralda, Paraguay y M. T. de Alvear, alturas 800 a "
                           "990». Las cuatro se cruzan de a pares y encierran una cara: es la "
                           "única pieza de las cuatro páginas que cierra sin agregar nada"),
                 comprobar_alturas=(800, 990)),
            dict(nombre="el corredor Arroyo", tipo="corredor",
                 calle="ARROYO", desde="ESMERALDA", hasta="PELLEGRINI CARLOS",
                 de_donde=("«el corredor Arroyo, de Juncal y Esmeralda a Plaza Carlos "
                           "Pellegrini». El extremo norte se resuelve con la CALLE Carlos "
                           "Pellegrini, que la página no nombra: nombra la plaza. Es la única "
                           "libertad que se toma en toda la corrida y va declarada acá"),
                 declarar=("la página escribe «Plaza Carlos Pellegrini» y el borde usa la calle "
                           "Carlos Pellegrini, que Arroyo sí cruza")),
        ],
        no_cierran=[
            ("el núcleo institucional de Plaza San Martín y Florida",
             "la página nombra una sola calle —Florida— y una plaza. Una calle sola no encierra "
             "nada, y con la regla de manzanas frentistas tampoco alcanza: falta hasta dónde",
             "las dos transversales que acotan el tramo de Florida (la página tendría que "
             "escribir «Florida entre X e Y»)"),
        ]),
    dict(
        polo="Z41", pagina="Núñez",
        nombra=[("Crisólogo Larralde", "LARRALDE CRISOLOGO AV"),
                ("Av. del Libertador", "DEL LIBERTADOR AV"), ("Av. Cabildo", "CABILDO AV"),
                ("Campos Salles", "CAMPOS SALLES"), ("O'Higgins", "O HIGGINS"),
                ("Grecia", "GRECIA"), ("Av. Congreso", "CONGRESO AV"),
                ("viaducto Mitre", None)],
        piezas=[
            dict(nombre="el corredor de Crisólogo Larralde", tipo="corredor",
                 calle="LARRALDE CRISOLOGO AV", desde="DEL LIBERTADOR AV", hasta="CABILDO AV",
                 de_donde=("«el corredor de Crisólogo Larralde entre Av. del Libertador y Av. "
                           "Cabildo». Los dos extremos son calles nombradas y Larralde cruza a "
                           "las dos: cierra")),
        ],
        no_cierran=[
            ("el corredor bajo el viaducto Mitre",
             "la página no nombra ninguna calle para esta pieza: nombra el viaducto, que es una "
             "traza ferroviaria y no una línea del callejero",
             "las dos calles que flanquean el viaducto en el tramo que la página quiere decir"),
            ("el núcleo disperso de bistrós en Campos Salles, O'Higgins y Grecia",
             "O'Higgins y Grecia son paralelas —corren a 34 m y no se cruzan— y Campos Salles "
             "las cruza a las dos: las tres forman una U abierta, no una figura cerrada",
             "la transversal que cierra el paño del otro lado de Campos Salles"),
        ]),
    dict(
        polo="Z27", pagina="Villa Santa Rita",
        nombra=[("Av. Álvarez Jonte", "ALVAREZ JONTE AV")],
        piezas=[],
        no_cierran=[
            ("los puntos dispersos con anclaje en Av. Álvarez Jonte",
             "la página nombra una sola calle en todo el bloque, y además dice que es el límite "
             "sur y oeste del barrio y no su columna interior. Una calle sola no encierra nada, "
             "y ésta encima está en el borde: aunque se le aplicaran las manzanas frentistas, "
             "la mitad de ellas caería fuera del barrio",
             "al menos dos transversales que acoten el tramo, y una calle interior paralela que "
             "le dé fondo a la figura"),
        ]),
    dict(
        polo="Z43", pagina="Colegiales",
        nombra=[("Concepción Arenal", "ARENAL CONCEPCION"), ("Zapiola", "ZAPIOLA"),
                ("Polo Concepción", None), ("Mercado de Pulgas", None)],
        piezas=[],
        no_cierran=[
            ("el eje Concepción Arenal–Zapiola",
             "las dos calles se cruzan, así que lo que la página da es una esquina y no una "
             "figura, y el bloque no escribe hasta dónde llega el eje por ninguna de las dos",
             "las dos transversales que acotan el eje (o las alturas entre las que corre)"),
            ("el Polo Concepción y el Mercado de Pulgas",
             "son dos enclaves nombrados por su nombre propio, no por calles. El Mercado de "
             "Pulgas tiene dirección conocida —Gral. E. Martínez 50— pero esa calle no está "
             "escrita en el bloque",
             "las calles que delimitan cada enclave; para el Mercado de Pulgas alcanzaría con "
             "escribir la dirección que ya se conoce"),
        ]),
]


def bloque_donde_esta(texto, titulo):
    partes = re.split(r"^# (.+)$", texto, flags=re.M)
    for i in range(1, len(partes), 2):
        if partes[i].strip() == titulo:
            m = re.search(r"\*\*Dónde está\.\*\*(.*?)(?=\n\*\*[^*\n]{2,60}?\.\*\*|\Z)",
                          partes[i + 1], flags=re.S)
            if not m:
                raise SystemExit(f"la página «{titulo}» no tiene bloque «Dónde está». Si de "
                                 f"verdad no lo tiene es un hallazgo y hay que declararlo.")
            return re.sub(r"\s+", " ", m.group(1)).strip()
    raise SystemExit(f"la página «{titulo}» no está en {SECCION.name}. No se propone un borde "
                     f"para una página que no se encontró.")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from cierre_geometrico import Callejero  # noqa: E402

    print("=" * 98)
    print("LOS CUATRO SIN BORDE PROPIO · el borde que sale de las calles que su página nombra")
    print("=" * 98 + "\n")

    cj = Callejero()
    bordes, _, soportes = gv.cargar()
    texto = SECCION.read_text(encoding="utf-8")

    filas, filas_calles, geoms = [], [], []
    for pag in PAGINAS:
        pid, titulo = pag["polo"], pag["pagina"]
        bloque = bloque_donde_esta(texto, titulo)
        print("=" * 98)
        print(f"{pid} · {titulo}   ·   publica hoy "
              f"{bordes[pid].area / 1e4:,.2f} ha y {cj.locales(bordes[pid])} locales")
        print("=" * 98)
        print(f"    lo que escribe: «{bloque[:400]}{'…' if len(bloque) > 400 else ''}»\n")

        calles = [(n, k) for n, k in pag["nombra"] if k]
        no_calles = [n for n, k in pag["nombra"] if not k]
        print(f"    nombra {len(calles)} calles y {len(no_calles)} cosas que no son calles")
        for n, k in calles:
            eje = cj.eje(k)
            print(f"        calle  «{n}» → {k} · {eje.length:,.0f} m en el callejero")
            filas_calles.append(dict(polo=pid, pagina=titulo, escribe=n, callejero=k,
                                     es_calle="si", largo_m=round(eje.length, 1)))
        for n in no_calles:
            print(f"        NO es calle  «{n}»")
            filas_calles.append(dict(polo=pid, pagina=titulo, escribe=n, callejero="",
                                     es_calle="no", largo_m=""))

        total = []
        print()
        for pieza in pag["piezas"]:
            if pieza["tipo"] == "corredor":
                tramo = cj.tramo_entre(pieza["calle"], pieza["desde"], pieza["hasta"])
                if tramo is None or tramo.is_empty:
                    raise SystemExit(f"el tramo de {pieza['calle']} entre {pieza['desde']} y "
                                     f"{pieza['hasta']} sale vacío. No se sigue con 0,00 ha.")
                caras = cj.frentistas(tramo, FRENTE)
                if not caras:
                    raise SystemExit(f"ninguna manzana da frente al tramo de {pieza['calle']}. "
                                     f"No se sigue.")
                g = limpia(unary_union([c for _, _, c in caras]))
                detalle = (f"tramo de {tramo.length:,.0f} m · {len(caras)} manzanas frentistas · "
                           f"frente más chico {min(l for _, l, _ in caras):,.0f} m")
            elif pieza["tipo"] == "recinto":
                ejes = [cj.eje(k) for k in pieza["calles"]]
                caras = [limpia(c) for c in polygonize(unary_union(ejes))]
                cerradas = [c for c in caras
                            if all(c.boundary.intersection(e).length >= FRENTE for e in ejes)]
                if not cerradas:
                    raise SystemExit(f"las calles {pieza['calles']} no encierran ninguna cara con "
                                     f"frente sobre las cuatro. Si no cierran, va en no_cierran.")
                g = limpia(unary_union(cerradas))
                detalle = (f"{len(cerradas)} cara(s) con frente sobre las "
                           f"{len(ejes)} calles a la vez")
            else:
                raise SystemExit(f"tipo de pieza desconocido: {pieza['tipo']}")

            n = cj.locales(g)
            print(f"    CIERRA · {pieza['nombre']}")
            print(f"             {g.area / 1e4:,.2f} ha · {n} locales · {detalle}")
            print(f"             de dónde sale: {pieza['de_donde']}")
            if pieza.get("declarar"):
                print(f"             se declara: {pieza['declarar']}")
            if pieza.get("comprobar_alturas"):
                d, h = pieza["comprobar_alturas"]
                dentro = [k for k in pieza["calles"]
                          if (cj.tramo_por_altura(k, d, h) is not None
                              and not cj.tramo_por_altura(k, d, h).is_empty
                              and cj.tramo_por_altura(k, d, h).intersects(g))]
                print(f"             control de alturas {d}–{h}: la cara cae sobre ese tramo en "
                      f"{len(dentro)} de las {len(pieza['calles'])} calles")
            total.append(g)
            filas.append(dict(polo=pid, pagina=titulo, pieza=pieza["nombre"],
                              estado="cierra", tipo=pieza["tipo"],
                              ha=round(g.area / 1e4, 2), locales=n, detalle=detalle,
                              de_donde=pieza["de_donde"], falta=""))
            geoms.append(dict(polo=pid, pagina=titulo, pieza=pieza["nombre"],
                              ha=round(g.area / 1e4, 2), locales=n, geometry=g))
            print()

        for nombre, motivo, falta in pag["no_cierran"]:
            print(f"    NO CIERRA · {nombre}")
            print(f"                por qué: {motivo}")
            print(f"                falta nombrar: {falta}")
            filas.append(dict(polo=pid, pagina=titulo, pieza=nombre, estado="no cierra",
                              tipo="", ha="", locales="", detalle=motivo, de_donde="",
                              falta=falta))
            print()

        if total:
            g = limpia(unary_union(total))
            n = cj.locales(g)
            hoy_ha = bordes[pid].area / 1e4
            print(f"    lo que la página cierra hoy, junto: {g.area / 1e4:,.2f} ha · {n} locales")
            print(f"    contra las {hoy_ha:,.2f} ha que publica: es "
                  f"{hoy_ha / (g.area / 1e4):,.1f} veces más chico y conserva el "
                  f"{n / max(cj.locales(bordes[pid]), 1) * 100:,.1f} % de los locales")
            fuera = limpia(g.difference(bordes[pid])).area
            print(f"    y cae dentro del contorno publicado: {fuera:,.0f} m² quedan fuera "
                  f"(medido por superficie perdida, no con covers())")
        else:
            print(f"    la página no cierra ninguna pieza. No hay borde que proponer, y lo que "
                  f"falta está escrito arriba.")
        print()

    gpd.GeoDataFrame(geoms, geometry="geometry", crs=CRS_M).to_crs(CRS_G).to_file(
        SALIDA / "geometria" / "bordes_de_los_cuatro.geojson", driver="GeoJSON")
    pd.DataFrame(filas).to_csv(SALIDA / "bordes_de_los_cuatro.csv", index=False, encoding="utf-8")
    pd.DataFrame(filas_calles).to_csv(SALIDA / "bordes_de_los_cuatro_calles.csv", index=False,
                                      encoding="utf-8")
    cierran = sum(1 for f in filas if f["estado"] == "cierra")
    (SALIDA / "bordes_de_los_cuatro_resumen.json").write_text(json.dumps(
        dict(fecha=HOY, piezas_que_cierran=cierran,
             piezas_que_no=sum(1 for f in filas if f["estado"] == "no cierra"),
             por_pagina={p["pagina"]: dict(
                 cierran=sum(1 for f in filas
                             if f["pagina"] == p["pagina"] and f["estado"] == "cierra"),
                 no_cierran=len(p["no_cierran"])) for p in PAGINAS}),
        ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 98)
    print(f"RESUMEN · cierran {cierran} piezas de las "
          f"{len(filas)} que las cuatro páginas describen")
    print("=" * 98)
    for p in PAGINAS:
        c = sum(1 for f in filas if f["pagina"] == p["pagina"] and f["estado"] == "cierra")
        print(f"    {p['pagina']:<20} {c} de {c + len(p['no_cierran'])} piezas")
    print(f"\nEscrito: bordes_de_los_cuatro.csv ({len(filas)}) · "
          f"bordes_de_los_cuatro_calles.csv ({len(filas_calles)}) · "
          f"bordes_de_los_cuatro_resumen.json · geometria/bordes_de_los_cuatro.geojson")


if __name__ == "__main__":
    main()
