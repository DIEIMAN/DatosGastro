# -*- coding: utf-8 -*-
"""Los cinco repartos contenidos: qué queda de cada página después de repartir el solape.

QUÉ SE REPARTE Y QUÉ NO
------------------------
Cinco de los seis solapes que se decidieron. El sexto —Chacarita, Federico Lacroze y Colegiales—
no se reparte: se funde, y eso se mide aparte en `chacagiales_21.py` porque cambia el conteo de
polos y esta corrida no debe depender de que aquella verifique.

Tres de los cinco son **enteros**: todo el solape se le atribuye a una de las dos páginas y la
otra lo pierde. Dos son **cortes**: el solape se parte por un eje y cada mitad va a una página.

LA ORIENTACIÓN DE LOS DOS CORTES NO SE ASUME
---------------------------------------------
El pedido lo dice y tiene razón en decirlo: «al oeste es Almagro, al este es Abasto» es una
afirmación sobre el territorio y hay que verificarla antes de cortar, no después. Acá se verifica
con tres cosas distintas, y las tres se publican:

  1. **El rumbo del eje** medido sobre el tramo que efectivamente cruza el solape, no sobre la
     avenida entera. Una avenida que gira cambia de rumbo, y el rumbo que importa es el del tramo
     que corta.
  2. **Lo que el nomenclador oficial dice de cada vereda.** El callejero trae `barrio_par` y
     `barrio_imp` por segmento: es la atribución de barrio de cada acera, escrita por la fuente.
     Y además se mide **cuánto del borde compartido entre los dos barrios corre sobre el eje**:
     si un eje se presenta como «el límite entre A y B», ese número tiene que ser grande, y si
     da cinco metros la frase es falsa aunque el corte igual se pueda hacer.
  3. **De qué lado cae la masa propia de cada polo** —la parte de cada uno que NO está en el
     solape—. Esa es la que decide el reparto, porque es la única que habla de los polos y no de
     los barrios. Las dos primeras confirman o contradicen, y si contradicen se dice.

Y la tercera se corre **a cinco radios alrededor del solape**, no una vez. El eje hay que
prolongarlo para que corte de lado a lado, y una prolongación de ocho kilómetros parte barrios
enteros que están mucho más allá de donde la avenida existe: medir la masa de un polo contra esa
prolongación puede dar el lado de una geometría que la avenida nunca tocó. Si la respuesta no es
la misma a 200, 400, 800 y 1.600 metros y sin recorte, el reparto depende del radio y hay que
decirlo en vez de publicar el número de un radio elegido a dedo.

Se publica también **en qué barrio cae cada mitad repartida**, porque es la comprobación que
avisa cuando un corte, siendo correcto, deja a una página con superficie adentro del barrio de la
otra.

Y la convención `par` = acera izquierda del sentido de digitalización **también se verifica**, no
se hereda de la documentación: se toma un segmento donde las dos aceras tienen barrios distintos,
se desplaza un punto a cada lado y se mira en qué barrio de la capa oficial cae.

CÓMO SE MIDE
------------
  - EPSG:5347 para medir, EPSG:4326 para guardar.
  - El corte se hace poligonizando el borde del solape junto con el eje prolongado, y no con
    `split()`: si el eje no atraviesa la figura de lado a lado, `split()` devuelve la figura
    entera sin avisar.
  - Los locales se cuentan por punto adentro del polígono, universo `anillo=nucleo &
    apto_geometria`, el mismo de todo lo demás.
  - La contención se verifica por superficie perdida, nunca con `covers()`.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import json
import math
import sys
from datetime import date
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, polygonize, unary_union

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
ROOT = BARRIDO.parents[1]
sys.path.insert(0, str(BARRIDO / "ronda_20"))
sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))

import geometria_vigente_20 as gv  # noqa: E402
from geometria_vigente_20 import limpia  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()
BASE = BARRIDO / "base" / "local.csv"
BARRIOS = BARRIDO / "insumos" / "caba_barrios.geojson"

# --------------------------------------------------------------------------------------------
# LOS CINCO REPARTOS, como los decidió Diego.
#
#   modo "entero"  todo el solape es de `gana`; `pierde` publica su figura menos el solape.
#   modo "corte"   el solape se parte por `eje`; cada mitad va a la página cuya masa propia está
#                  de ese lado. Qué lado es cuál NO se declara acá: se mide.
# --------------------------------------------------------------------------------------------
REPARTOS = [
    dict(clave="A1", a="Z46", b="R12", modo="entero", gana="R12", pierde="Z46",
         motivo=("Retiro no tiene borde propio —publica el polígono de su barrio— y el solape "
                 "entero es del Microcentro hasta que Retiro tenga borde dibujado")),
    dict(clave="A2", a="R02", b="R12", modo="entero", gana="R02", pierde="R12",
         motivo=("corredor contra núcleo: la franja sobre Av. Corrientes es del corredor, que "
                 "existe por esa avenida; el núcleo la contiene de paso")),
    dict(clave="A3", a="Z47", b="R12", modo="entero", gana="Z47", pierde="R12",
         motivo=("el eje de Av. de Mayo con sus nueve Bares Notables es de Monserrat: es el 63 % "
                 "de Monserrat y el 4,7 % del Microcentro")),
    dict(clave="A4", a="R13", b="Z37", modo="corte", eje="MEDRANO AV.",
         barrios={"R13": None, "Z37": "ALMAGRO"},
         motivo="se corta en Av. Medrano, que la página de Almagro nombra en su perímetro escrito"),
    dict(clave="A5", a="R08", b="R21", modo="corte", eje="WARNES AV.",
         barrios={"R08": "VILLA CRESPO", "R21": "PATERNAL"},
         motivo="se corta por Av. Warnes, con la que la matriz define a La Paternal"),
]

# A qué radio alrededor del solape se vuelve a preguntar de qué lado está la masa de cada polo.
RADIOS = (200.0, 400.0, 800.0, 1600.0, None)


# --------------------------------------------------------------------------------------------
# herramientas
# --------------------------------------------------------------------------------------------
def rumbo(dx, dy):
    """Azimut 0–180 desde el norte. Un eje no tiene sentido, así que 10° y 190° son el mismo."""
    a = math.degrees(math.atan2(dx, dy)) % 180.0
    return a


def nombre_del_rumbo(az):
    for lim, etq in ((11.25, "N–S"), (33.75, "NNE–SSO"), (56.25, "NE–SO"), (78.75, "ENE–OSO"),
                     (101.25, "E–O"), (123.75, "ESE–ONO"), (146.25, "SE–NO"),
                     (168.75, "SSE–NNO"), (180.01, "N–S")):
        if az < lim:
            return etq
    return "N–S"


def nombre_del_lado(dx, dy):
    """El rumbo del desplazamiento medio de una pieza respecto del eje, en palabras."""
    if dx == 0 and dy == 0:
        return "sobre el eje"
    az = math.degrees(math.atan2(dx, dy)) % 360.0
    puntos = ["norte", "nornoreste", "noreste", "estenoreste", "este", "estesudeste",
              "sudeste", "sudsudeste", "sur", "sudsudoeste", "sudoeste", "oestesudoeste",
              "oeste", "oestenoroeste", "noroeste", "nornoroeste"]
    return puntos[int((az + 11.25) % 360 // 22.5)]


def prolongar(linea, metros=8000.0):
    """La misma línea con los dos extremos estirados por su tangente, para que corte de lado a
    lado. Un eje que se queda corto parte la figura en una sola pieza y la corrida seguiría."""
    xs, ys = list(linea.coords), None
    p0, p1 = xs[0], xs[1]
    q0, q1 = xs[-2], xs[-1]
    d0 = math.hypot(p0[0] - p1[0], p0[1] - p1[1]) or 1.0
    d1 = math.hypot(q1[0] - q0[0], q1[1] - q0[1]) or 1.0
    ini = (p0[0] + (p0[0] - p1[0]) / d0 * metros, p0[1] + (p0[1] - p1[1]) / d0 * metros)
    fin = (q1[0] + (q1[0] - q0[0]) / d1 * metros, q1[1] + (q1[1] - q0[1]) / d1 * metros)
    ys = [ini] + xs + [fin]
    return LineString(ys)


def eje_unico(calles, familias, nombre, cerca_de):
    """El eje canónico de una calle, reducido a UNA polilínea continua: la que pasa por el solape.

    Se exige una sola porque el signo del lado se calcula contra una polilínea, y calcularlo
    contra un manojo de pedazos sueltos daría un signo por pedazo sin que nadie lo note.
    """
    from callejero_canonico import eje_canonico  # noqa: E402
    bruto = eje_canonico(calles, nombre, familias)
    unido = linemerge(bruto)
    piezas = list(unido.geoms) if unido.geom_type == "MultiLineString" else [unido]
    tocan = [p for p in piezas if p.intersects(cerca_de.buffer(60))]
    if not tocan:
        raise SystemExit(f"«{nombre}» no toca el solape que tiene que cortar. No se corta.")
    tocan.sort(key=lambda p: -p.length)
    if len(tocan) > 1:
        largos = ", ".join(f"{p.length:,.0f} m" for p in tocan)
        print(f"    aviso: el eje de {nombre} llega al solape en {len(tocan)} piezas ({largos}); "
              f"se corta con la más larga y se declara")
    return tocan[0]


def lado_de(linea, punto):
    """+1 / −1 según de qué lado de la polilínea cae el punto. 0 si cae encima."""
    d = linea.project(punto)
    a = linea.interpolate(max(0.0, d - 8.0))
    b = linea.interpolate(min(linea.length, d + 8.0))
    cruz = (b.x - a.x) * (punto.y - a.y) - (b.y - a.y) * (punto.x - a.x)
    return 0 if abs(cruz) < 1e-9 else (1 if cruz > 0 else -1)


def partir(poligono, corte):
    """Las piezas de `poligono` a los dos lados de `corte`, sin usar split()."""
    red = unary_union([poligono.boundary, corte])
    caras = [limpia(c) for c in polygonize(red)]
    return [c for c in caras if c.representative_point().within(poligono) and c.area > 1.0]


def desplazamiento_medio(linea, geom):
    """(dx, dy) del centroide de una pieza respecto de su punto más cercano sobre el eje."""
    p = geom.representative_point()
    q = linea.interpolate(linea.project(p))
    return p.x - q.x, p.y - q.y


def poligono_barrio(barrios, nombre):
    sub = barrios[barrios.BARRIO.astype(str).str.upper().str.strip() == nombre.upper().strip()]
    if sub.empty:
        raise SystemExit(f"«{nombre}» no está en la capa oficial de barrios. No se sigue con un "
                         f"polígono vacío, que mediría 0,00 ha y se leería como un dato.")
    return limpia(unary_union(list(sub.geometry)))


def composicion_por_barrio(barrios, geom, minimo=1.0):
    """[(barrio, % de la figura)] ordenado de mayor a menor, para ver dónde cae una mitad."""
    salida = []
    for r in barrios.itertuples():
        if not geom.intersects(r.geometry):
            continue
        pct = limpia(geom.intersection(r.geometry)).area / geom.area * 100
        if pct >= minimo:
            salida.append((str(r.BARRIO), pct))
    return sorted(salida, key=lambda t: -t[1])


# --------------------------------------------------------------------------------------------
def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from callejero_canonico import cargar, familias  # noqa: E402

    print("=" * 98)
    print("LOS CINCO REPARTOS CONTENIDOS · qué queda de cada página después de repartir el solape")
    print("=" * 98 + "\n")

    bordes, procedencia, soportes = gv.cargar()
    nombres = {pid: str(soportes.polo_nombre.loc[pid]) for pid in bordes}
    calles = cargar()
    fams = familias(calles)
    barrios = gpd.read_file(BARRIOS).to_crs(CRS_M)
    print(f"geometría vigente: {len(bordes)} polos · callejero: {len(calles):,} segmentos\n")

    base = pd.read_csv(BASE)
    base = base[(base.anillo == "nucleo") & (base.apto_geometria.astype(str).str.lower()
                                             .isin(["true", "1", "si", "sí"]))]
    pts = gpd.GeoDataFrame(
        base[["local_id", "nombre", "direccion_norm", "barrio", "comuna"]].copy(),
        geometry=gpd.GeoSeries([Point(x, y) for x, y in zip(base.lon, base.lat)],
                               crs=CRS_G).to_crs(CRS_M).values, crs=CRS_M)
    sidx = pts.sindex
    print(f"base: {len(pts):,} locales del universo anillo=nucleo & apto_geometria\n")

    def locales_en(g):
        cand = pts.iloc[list(sidx.query(g))]
        return cand[cand.geometry.within(g)]

    def ha(g):
        return g.area / 10_000

    antes = {pid: (ha(g), len(locales_en(g))) for pid, g in bordes.items()}
    nuevos = dict(bordes)
    # El Microcentro entra en tres de los cinco repartos, así que hay que distinguir la cifra
    # publicada del valor con el que llega a cada reparto. Mezclarlas hace que el tercero parezca
    # llevarse lo que en realidad se llevaron los tres, y esa es la cifra con la que se escribe.
    previo = {pid: v for pid, v in antes.items()}
    filas_reparto, cambian, orientaciones = [], [], []

    # ---------------------------------------------------------------- la convención par/impar
    print("-" * 98)
    print("0 · LA CONVENCIÓN DEL NOMENCLADOR, VERIFICADA Y NO HEREDADA")
    print("-" * 98)
    testigo = calles[(calles.barrio_par.notna()) & (calles.barrio_imp.notna())
                     & (calles.barrio_par != calles.barrio_imp)].iloc[0]
    seg = testigo.geometry
    medio = seg.interpolate(0.5, normalized=True)
    c = list(seg.coords)
    dx, dy = c[-1][0] - c[0][0], c[-1][1] - c[0][1]
    n = math.hypot(dx, dy) or 1.0
    izq = Point(medio.x - dy / n * 25, medio.y + dx / n * 25)
    der = Point(medio.x + dy / n * 25, medio.y - dx / n * 25)

    def barrio_de(p):
        s = barrios[barrios.geometry.contains(p)]
        return str(s.iloc[0].BARRIO) if len(s) else "(fuera de la capa)"

    b_izq, b_der = barrio_de(izq), barrio_de(der)
    par_es_izq = str(testigo.barrio_par).strip().lower() in b_izq.strip().lower()
    print(f"    segmento testigo: {testigo.nomoficial} · par={testigo.barrio_par} · "
          f"impar={testigo.barrio_imp}")
    print(f"    a 25 m a la izquierda del sentido de digitalización cae en {b_izq}")
    print(f"    a 25 m a la derecha                                   cae en {b_der}")
    print(f"    → «par» es la acera {'IZQUIERDA' if par_es_izq else 'DERECHA'} del sentido de "
          f"digitalización. Verificado, no supuesto.\n")

    # ---------------------------------------------------------------- los cinco
    for rep in REPARTOS:
        a, b = rep["a"], rep["b"]
        ga, gb = nuevos[a], nuevos[b]
        inter = limpia(ga.intersection(gb))
        loc_inter = locales_en(inter)
        print("=" * 98)
        print(f"{rep['clave']} · {nombres[a]} ({a})  y  {nombres[b]} ({b})")
        print("=" * 98)
        print(f"    el solape mide {ha(inter):,.2f} ha y tiene {len(loc_inter)} locales")
        print(f"    motivo: {rep['motivo']}\n")

        if rep["modo"] == "entero":
            gana, pierde = rep["gana"], rep["pierde"]
            resto = limpia(nuevos[pierde].difference(inter))
            perdida = ha(nuevos[pierde]) - ha(resto) - ha(inter)
            if abs(perdida) > 0.01:
                raise SystemExit(f"restar el solape a {pierde} no cierra por {perdida:.4f} ha. "
                                 f"No se sigue con una resta que no da.")
            nuevos[pierde] = resto
            reparto_por_polo = {gana: inter, pierde: None}
            for r in loc_inter.itertuples():
                cambian.append(dict(reparto=rep["clave"], local_id=r.local_id,
                                    nombre=str(r.nombre), direccion=str(r.direccion_norm),
                                    barrio=r.barrio, comuna=r.comuna,
                                    deja_de_contarlo=f"{pierde} · {nombres[pierde]}",
                                    lo_sigue_contando=f"{gana} · {nombres[gana]}",
                                    lado=""))
        else:
            eje = eje_unico(calles, fams, rep["eje"], inter)
            corte = prolongar(eje)

            # --- 1 · el rumbo del tramo que cruza, no el de la avenida entera
            tramo = eje.intersection(inter.buffer(120))
            tramo = linemerge(tramo) if tramo.geom_type == "MultiLineString" else tramo
            piezas_t = list(tramo.geoms) if tramo.geom_type == "MultiLineString" else [tramo]
            piezas_t.sort(key=lambda p: -p.length)
            ct = list(piezas_t[0].coords)
            az = rumbo(ct[-1][0] - ct[0][0], ct[-1][1] - ct[0][1])
            print(f"    1 · el eje de {rep['eje']} cruza el solape a lo largo de "
                  f"{eje.intersection(inter).length:,.0f} m")
            print(f"        rumbo del tramo que cruza: {az:.1f}° · o sea {nombre_del_rumbo(az)}")

            # --- 2 · lo que el nomenclador dice de cada vereda
            clave_eje = next(k for k in fams
                             if k.replace(".", "").replace(" ", "")
                             == rep["eje"].replace(".", "").replace(" ", ""))
            sub = calles[calles.clave.isin(fams[clave_eje])]
            sub = sub[sub.geometry.intersects(inter.buffer(30))]
            pares = sorted({(str(r.barrio_par), str(r.barrio_imp)) for r in sub.itertuples()})
            print(f"    2 · el nomenclador, en los {len(sub)} segmentos que tocan el solape:")
            for pp, ii in pares:
                cuantos = sum(1 for r in sub.itertuples()
                              if (str(r.barrio_par), str(r.barrio_imp)) == (pp, ii))
                print(f"        acera par «{pp}» · acera impar «{ii}»   ({cuantos} segmentos)")
            nomenclador_separa = any(pp != ii for pp, ii in pares)
            print(f"        → el nomenclador {'SÍ' if nomenclador_separa else 'NO'} pone dos "
                  f"barrios distintos a los lados de este eje en este tramo")

            # ¿cuánto del borde compartido entre los dos barrios corre sobre este eje?
            bn = rep.get("barrios", {})
            b_a, b_b = bn.get(a), bn.get(b)
            borde_compartido = sobre_el_eje = None
            if b_a and b_b:
                ga_b = poligono_barrio(barrios, b_a)
                gb_b = poligono_barrio(barrios, b_b)
                comp = ga_b.boundary.intersection(gb_b.boundary)
                borde_compartido = comp.length
                sobre_el_eje = comp.intersection(eje.buffer(5.0)).length
                pct = (sobre_el_eje / borde_compartido * 100) if borde_compartido else 0.0
                print(f"        el borde compartido entre {b_a} y {b_b} mide "
                      f"{borde_compartido:,.1f} m, y {sobre_el_eje:,.1f} m de ese borde "
                      f"({pct:.1f} %) corren sobre este eje")
                if pct < 50:
                    print(f"        → ATENCIÓN: este eje NO es el límite entre los dos barrios. "
                          f"El corte se puede hacer igual, pero la frase «es el límite» es falsa")
            else:
                falta = a if not b_a else b
                print(f"        el borde compartido no se puede medir: {falta} "
                      f"({nombres[falta]}) no es un barrio de la capa oficial")

            # --- 3 · de qué lado cae la masa propia de cada polo, a cinco radios
            solo = {a: limpia(ga.difference(gb)), b: limpia(gb.difference(ga))}
            print(f"    3 · masa propia de cada polo a cada lado del eje, por radio alrededor "
                  f"del solape:")
            print(f"        {'radio':>8}  {a:>6} lado A / lado B   {b:>6} lado A / lado B    "
                  f"queda lado A / lado B")
            veredictos, masa = [], None
            for radio in RADIOS:
                campo = inter.buffer(radio) if radio else None
                acum = {}
                for pid in (a, b):
                    propio = solo[pid] if campo is None else limpia(solo[pid].intersection(campo))
                    ac = {1: 0.0, -1: 0.0, 0: 0.0}
                    for pieza in (partir(propio, corte) or [propio]):
                        ac[lado_de(corte, pieza.representative_point())] += pieza.area
                    acum[pid] = ac
                dd = {s: (a if acum[a][s] >= acum[b][s] else b) for s in (1, -1)}
                veredictos.append((dd[1], dd[-1]))
                if radio is None:
                    masa = acum
                etq = f"{radio:,.0f} m" if radio else "sin recorte"
                print(f"        {etq:>8}  {acum[a][1] / 1e4:>7,.2f} / {acum[a][-1] / 1e4:>7,.2f}   "
                      f"{acum[b][1] / 1e4:>7,.2f} / {acum[b][-1] / 1e4:>7,.2f}     "
                      f"{dd[1]:>6} / {dd[-1]:<6}")
            if len(set(veredictos)) != 1:
                raise SystemExit(f"el reparto de {rep['clave']} depende del radio: "
                                 f"{sorted(set(veredictos))}. Un corte que cambia de dueño según "
                                 f"cuánto contexto se mire no es un corte. No se sigue.")
            print(f"        → el mismo reparto a los cinco radios. No depende de cuánto se mire")

            duenio = {s: veredictos[0][0 if s == 1 else 1] for s in (1, -1)}
            if duenio[1] == duenio[-1]:
                raise SystemExit(
                    f"los dos lados del eje le tocarían a {duenio[1]}: la masa propia de "
                    f"{a} y {b} está del mismo lado y el corte no reparte nada. "
                    f"Esto hay que decidirlo, no resolverlo con una regla. No se corta.")

            piezas = partir(inter, corte)
            if len(piezas) < 2:
                raise SystemExit(f"el eje de {rep['eje']} parte el solape en {len(piezas)} pieza(s). "
                                 f"No corta: no se sigue.")
            reparto_por_polo = {a: [], b: []}
            lados_desc = {}
            for pieza in piezas:
                s = lado_de(corte, pieza.representative_point())
                if s == 0:
                    raise SystemExit("una pieza cae exactamente sobre el eje. No se sigue.")
                reparto_por_polo[duenio[s]].append(pieza)
                dx, dy = desplazamiento_medio(corte, pieza)
                lados_desc.setdefault(duenio[s], []).append((dx, dy, pieza.area))
            reparto_por_polo = {k: limpia(unary_union(v)) for k, v in reparto_por_polo.items()}

            print()
            for pid in (a, b):
                vs = lados_desc.get(pid, [])
                if vs:
                    sx = sum(dx * w for dx, _, w in vs) / sum(w for *_, w in vs)
                    sy = sum(dy * w for _, dy, w in vs) / sum(w for *_, w in vs)
                    donde = nombre_del_lado(sx, sy)
                else:
                    donde = "(sin pieza)"
                g = reparto_por_polo[pid]
                comp = composicion_por_barrio(barrios, g)
                print(f"        → al {donde} del eje: {ha(g):,.2f} ha · "
                      f"{len(locales_en(g))} locales  →  {pid} · {nombres[pid]}")
                print(f"          esa mitad cae en: "
                      + " · ".join(f"{nb} {pc:.0f} %" for nb, pc in comp))
                orientaciones.append(dict(
                    reparto=rep["clave"], eje=rep["eje"], rumbo_grados=round(az, 1),
                    rumbo=nombre_del_rumbo(az), polo=pid, polo_nombre=nombres[pid],
                    lado=donde, ha=round(ha(g), 2), locales=len(locales_en(g)),
                    barrios_de_esa_mitad="; ".join(f"{nb} {pc:.0f}%" for nb, pc in comp),
                    nomenclador_separa_barrios="si" if nomenclador_separa else "no",
                    nomenclador_par="; ".join(sorted({p for p, _ in pares})),
                    nomenclador_impar="; ".join(sorted({i for _, i in pares})),
                    borde_compartido_de_los_dos_barrios_m=(round(borde_compartido, 1)
                                                           if borde_compartido else ""),
                    de_ese_borde_sobre_el_eje_m=(round(sobre_el_eje, 1)
                                                 if sobre_el_eje is not None else "")))

            # La variante espejo, medida y no adoptada. Va porque «al este» y «al oeste» sólo
            # nombran los flancos de un eje que corre norte-sur, y si el eje corre de otro modo
            # la frase de la decisión admite dos lecturas opuestas. Publicar las dos cifras
            # cuesta seis líneas y ahorra una ronda entera.
            print("\n        la variante espejo, medida y NO adoptada:")
            for pid, otro in ((a, b), (b, a)):
                g_espejo = reparto_por_polo[pid]      # se queda el flanco del otro
                h_esp = ha(nuevos[pid]) - ha(reparto_por_polo[otro]) + 0.0
                queda = limpia(nuevos[pid].difference(g_espejo))
                print(f"          si {pid} · {nombres[pid]:<22} se quedara el otro flanco: "
                      f"{ha(queda):,.2f} ha · {len(locales_en(queda))} locales")
                del h_esp
            print()

            for pid, otro in ((a, b), (b, a)):
                cede = reparto_por_polo[otro]
                nuevos[pid] = limpia(nuevos[pid].difference(cede))
                for r in locales_en(cede).itertuples():
                    cambian.append(dict(
                        reparto=rep["clave"], local_id=r.local_id, nombre=str(r.nombre),
                        direccion=str(r.direccion_norm), barrio=r.barrio, comuna=r.comuna,
                        deja_de_contarlo=f"{pid} · {nombres[pid]}",
                        lo_sigue_contando=f"{otro} · {nombres[otro]}",
                        lado=nombre_del_lado(*desplazamiento_medio(corte, cede)[:2])))

        # --- el después de las dos páginas
        print()
        for pid in (a, b):
            hp, lp = antes[pid]                       # lo que la página publica hoy
            h0, l0 = previo[pid]                      # con lo que llega a este reparto
            h1, l1 = ha(nuevos[pid]), len(locales_en(nuevos[pid]))
            previo[pid] = (h1, l1)
            extra = ("" if abs(h0 - hp) < 0.01 else
                     f"   [publica {hp:,.2f} ha · {lp} locales; llega a este reparto ya repartido]")
            print(f"    {pid} · {nombres[pid]:<28} {h0:>9,.2f} ha → {h1:>9,.2f} ha   "
                  f"({h1 - h0:+.2f})     {l0:>5} → {l1:>5} locales ({l1 - l0:+d}){extra}")
            filas_reparto.append(dict(
                reparto=rep["clave"], polo=pid, polo_nombre=nombres[pid],
                rol=("gana el solape" if rep["modo"] == "entero" and pid == rep.get("gana")
                     else "pierde el solape" if rep["modo"] == "entero" else "se parte el solape"),
                ha_publicada_hoy=round(hp, 2), locales_publicados_hoy=lp,
                ha_antes_de_este_reparto=round(h0, 2), ha_despues_de_este_reparto=round(h1, 2),
                ha_delta_de_este_reparto=round(h1 - h0, 2),
                locales_antes_de_este_reparto=l0, locales_despues_de_este_reparto=l1,
                locales_delta_de_este_reparto=l1 - l0,
                solape_ha=round(ha(inter), 2), solape_locales=len(loc_inter),
                motivo=rep["motivo"]))
        print()

    print("=" * 98)
    print("LAS CIFRAS FINALES DE LAS OCHO PÁGINAS QUE TOCAN LOS CINCO REPARTOS")
    print("=" * 98)
    print(f"    {'polo':<6} {'página':<30}{'publica hoy':>22}{'después de repartir':>26}")
    tocadas = sorted({p for r in REPARTOS for p in (r["a"], r["b"])})
    filas_finales = []
    for pid in tocadas:
        hp, lp = antes[pid]
        h1, l1 = ha(nuevos[pid]), len(locales_en(nuevos[pid]))
        print(f"    {pid:<6} {nombres[pid][:28]:<30}{hp:>11,.2f} ha {lp:>6,} loc"
              f"{h1:>13,.2f} ha {l1:>6,} loc   ({h1 - hp:+,.2f} ha · {l1 - lp:+,} loc)")
        filas_finales.append(dict(polo=pid, polo_nombre=nombres[pid],
                                  ha_publicada_hoy=round(hp, 2), locales_publicados_hoy=lp,
                                  ha_final=round(h1, 2), locales_finales=l1,
                                  ha_delta=round(h1 - hp, 2), locales_delta=l1 - lp))
    print()

    # ---------------------------------------------------------------- la unión, de nuevo
    print("=" * 98)
    print("LA UNIÓN DE LOS 41, DESPUÉS DE LOS CINCO REPARTOS")
    print("=" * 98)

    def conjunto(bs):
        u = limpia(unary_union([limpia(g) for g in bs.values()]))
        suma_ha = sum(g.area for g in bs.values()) / 10_000
        suma_loc = sum(len(locales_en(g)) for g in bs.values())
        ids = set()
        pares = 0
        for x, y in combinations(sorted(bs), 2):
            gx, gy = bs[x], bs[y]
            if not gx.intersects(gy):
                continue
            it = limpia(gx.intersection(gy))
            if it.area < 1.0:
                continue
            pares += 1
            ids |= set(locales_en(it).local_id.astype(str))
        return dict(suma_ha=suma_ha, suma_locales=suma_loc, union_ha=u.area / 10_000,
                    union_locales=len(locales_en(u)), pares=pares, en_dos_o_mas=len(ids))

    c0, c1 = conjunto(bordes), conjunto(nuevos)
    campos = [("suma de los 41 por separado, ha", "suma_ha", "{:,.2f}"),
              ("unión de los 41, ha", "union_ha", "{:,.2f}"),
              ("suma de los 41 por separado, locales", "suma_locales", "{:,}"),
              ("unión de los 41, locales", "union_locales", "{:,}"),
              ("se cuentan de más, veces", None, "{:,}"),
              ("locales distintos en dos o más polos", "en_dos_o_mas", "{:,}"),
              ("pares de polos que comparten superficie", "pares", "{:,}")]
    print(f"  {'cifra':<44}{'antes':>14}{'ahora':>14}")
    for etq, clave, fmt in campos:
        if clave is None:
            v0 = c0["suma_locales"] - c0["union_locales"]
            v1 = c1["suma_locales"] - c1["union_locales"]
        else:
            v0, v1 = c0[clave], c1[clave]
        marca = "   <-- cambia" if abs(v1 - v0) > 1e-9 else ""
        print(f"  {etq:<44}{fmt.format(v0):>14}{fmt.format(v1):>14}{marca}")

    print(f"\n  se cuentan de más {c1['suma_locales'] - c1['union_locales']:,} veces sobre "
          f"{c1['en_dos_o_mas']:,} locales distintos.")

    # ---------------------------------------------------------------- salidas
    gpd.GeoDataFrame(
        [dict(polo_id=pid, polo_nombre=nombres[pid], caracter=gv.caracter(pid),
              ha=round(ha(g), 2), locales=len(locales_en(g)),
              reparto=next((r["clave"] for r in REPARTOS if pid in (r["a"], r["b"])), ""),
              geometry=g) for pid, g in sorted(nuevos.items())],
        geometry="geometry", crs=CRS_M).to_crs(CRS_G).to_file(
        SALIDA / "geometria" / "bordes_repartidos_41.geojson", driver="GeoJSON")

    pd.DataFrame(filas_reparto).to_csv(SALIDA / "repartos_cifras.csv", index=False,
                                       encoding="utf-8")
    pd.DataFrame(filas_finales).to_csv(SALIDA / "repartos_cifras_finales.csv", index=False,
                                       encoding="utf-8")
    pd.DataFrame(cambian).to_csv(SALIDA / "repartos_locales_que_cambian.csv", index=False,
                                 encoding="utf-8")
    pd.DataFrame(orientaciones).to_csv(SALIDA / "repartos_orientacion_de_los_cortes.csv",
                                       index=False, encoding="utf-8")
    (SALIDA / "repartos_resumen.json").write_text(json.dumps(
        dict(fecha=HOY, antes=c0, ahora=c1,
             locales_que_cambian_de_pagina=len(cambian),
             par_es_acera_izquierda=bool(par_es_izq)),
        ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nEscrito: repartos_cifras.csv ({len(filas_reparto)} filas) · "
          f"repartos_locales_que_cambian.csv ({len(cambian)}) · "
          f"repartos_orientacion_de_los_cortes.csv ({len(orientaciones)}) · "
          f"repartos_resumen.json · geometria/bordes_repartidos_41.geojson")


if __name__ == "__main__":
    main()
