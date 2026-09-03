# -*- coding: utf-8 -*-
"""Las calles que bordean el contorno de las 23 páginas que no escriben un perímetro reconstruible.

QUÉ RESUELVE
------------
La tanda anterior midió que once de las cuarenta y una páginas tienen un perímetro escrito del que
se reconstruye el borde, siete lo dan a medias y **veintitrés no lo dan**. Para esas veintitrés la
salida no era geométrica: el borde está dibujado, lo que falta es el texto. Esto lo da hecho:
recorre el contorno dibujado de cada una y devuelve, **en orden de recorrido**, las calles del
callejero oficial sobre las que corre, con las alturas de los extremos de cada tramo.

No escribe el texto de la página. Devuelve las calles y las alturas.

CÓMO SE RECORRE
---------------
  1. El contorno se **densifica cada 4 metros**. Se recorre punto por punto y a cada punto se le
     busca el segmento del callejero más cercano dentro de 15 m.
  2. Los puntos consecutivos que caen sobre la misma calle —comparada **por familia del callejero
     y no por cadena**, que es la lección de la tanda anterior— se juntan en un tramo.
  3. La secuencia se **despecula** antes de comprimir: una muestra suelta que difiere de sus dos
     vecinas se corrige a la de las vecinas. Sin eso, cada ochava que el contorno roza parte en
     dos un tramo que es uno solo, y la lista sale con la misma calle nombrada cuatro veces.
  4. Un tramo de menos de 30 m no se publica: es ruido de una esquina o de una ochava, y una lista
     de perímetro con cuarenta entradas de doce metros no sirve para escribir nada. Lo que se
     descarta se cuenta y se declara. Y **dos tramos de la misma calle separados sólo por tramos
     descartados se juntan en uno**, que es lo que pasa cuando el contorno vuelve a la misma
     calle después de doblar en una esquina.
  4. De cada tramo se dan **las alturas del segmento donde empieza y del segmento donde termina**,
     como rango de la cuadra y no como un número exacto: el callejero da alturas por cuadra, y
     escribir «Defensa 1043» donde la fuente dice «1001-1099» sería una precisión que no existe.

Y se publica **cuánto del contorno corre sobre alguna calle**. Es el número que dice si la página
se puede escribir: un contorno que va por calles el 90 % del recorrido se escribe de corrido; uno
que va el 15 % no es una figura de calles y hay que decirlo en vez de forzar la frase.

EPSG:5347. Cero requests.
"""

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
ROOT = BARRIDO.parents[1]
sys.path.insert(0, str(BARRIDO / "ronda_20"))
sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))

import geometria_vigente_20 as gv  # noqa: E402
from geometria_vigente_20 import limpia  # noqa: E402

CRS_M = "EPSG:5347"
HOY = date.today().isoformat()
PERIMETRO_41 = BARRIDO / "ronda_20" / "perimetro_escrito_41.csv"
REPARTIDOS = SALIDA / "geometria" / "bordes_repartidos_41.geojson"
FUNDIDOS = SALIDA / "geometria" / "bordes_39.geojson"

PASO = 4.0          # cada cuántos metros se muestrea el contorno
TOLERANCIA = 15.0   # a qué distancia una calle cuenta como «el contorno va por ahí»
MINIMO = 30.0       # tramos más cortos que esto no se publican


def rango(fila):
    """El rango de alturas de una cuadra, como lo trae el callejero: «702-800 / 701-799»."""
    par = [v for v in (fila.alt_izqini, fila.alt_izqfin) if v and v > 0]
    imp = [v for v in (fila.alt_derini, fila.alt_derfin) if v and v > 0]
    p = f"{min(par):.0f}-{max(par):.0f}" if par else "s/n"
    i = f"{min(imp):.0f}-{max(imp):.0f}" if imp else "s/n"
    return f"{p} / {i}"


def anillos(geom):
    piezas = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    piezas.sort(key=lambda g: -g.area)
    salida = []
    for i, p in enumerate(piezas):
        salida.append((i, "contorno exterior", p.exterior))
        for j, hueco in enumerate(p.interiors):
            salida.append((i, f"hueco {j + 1}", hueco))
    return salida


def recorrer(anillo, calles, sidx, familias):
    """[(clave de familia, nombre, largo, fila del segmento inicial, fila del final)] en orden."""
    n = max(int(anillo.length // PASO), 8)
    muestras = []
    for k in range(n):
        p = anillo.interpolate(k / n, normalized=True)
        cerca = list(sidx.query(p.buffer(TOLERANCIA)))
        if not cerca:
            muestras.append((None, None))
            continue
        sub = calles.iloc[cerca]
        d = sub.geometry.distance(p)
        fila = sub.loc[d.idxmin()]
        muestras.append((fila.clave, fila))
    # tramos: corridas consecutivas de la misma familia, cerrando el anillo
    def fam(c):
        return frozenset(familias.get(c, {c})) if c else None

    # despecular: una muestra suelta entre dos iguales es la ochava de una esquina, no otra calle
    for _ in range(2):
        for i in range(len(muestras)):
            a = fam(muestras[(i - 1) % len(muestras)][0])
            b = fam(muestras[i][0])
            c = fam(muestras[(i + 1) % len(muestras)][0])
            if a is not None and a == c and b != a:
                muestras[i] = muestras[(i - 1) % len(muestras)]

    tramos, actual = [], None
    for clave, fila in muestras + [(None, None)]:
        f = fam(clave)
        if actual and actual["fam"] == f and f is not None:
            actual["filas"].append(fila)
            continue
        if actual:
            tramos.append(actual)
        actual = None if f is None else dict(fam=f, clave=clave, filas=[fila])
    if actual:
        tramos.append(actual)
    # el anillo es cíclico: si el primero y el último son la misma calle, son un tramo
    if len(tramos) > 1 and tramos[0]["fam"] == tramos[-1]["fam"]:
        tramos[0]["filas"] = tramos[-1]["filas"] + tramos[0]["filas"]
        tramos.pop()
    salida = []
    for t in tramos:
        largo = len(t["filas"]) * (anillo.length / n)
        nombre = Counter(f.nomoficial for f in t["filas"]).most_common(1)[0][0]
        salida.append(dict(clave=t["clave"], nombre=nombre, largo=largo,
                           primero=t["filas"][0], ultimo=t["filas"][-1],
                           n_muestras=len(t["filas"])))
    return salida, sum(1 for c, _ in muestras if c is not None), len(muestras)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from callejero_canonico import cargar, familias  # noqa: E402

    print("=" * 98)
    print("LAS CALLES QUE BORDEAN EL CONTORNO · las 23 páginas sin perímetro reconstruible")
    print("=" * 98 + "\n")

    calles = cargar()
    fams = familias(calles)
    sidx = calles.sindex
    print(f"callejero: {len(calles):,} segmentos\n")

    esc = pd.read_csv(PERIMETRO_41)
    los_23 = [str(r.polo_id) for r in esc.itertuples()
              if str(r.reconstruible_desde_el_texto).strip() == "no"]
    if len(los_23) != 23:
        raise SystemExit(f"salieron {len(los_23)} páginas con «no» y se esperaban 23. La "
                         f"clasificación cambió: no se sigue con otra lista sin decirlo.")

    publicados, _, soportes = gv.cargar()
    nombres = {pid: str(soportes.polo_nombre.loc[pid]) for pid in publicados}

    capas = [("el borde publicado hoy", publicados, nombres)]
    if REPARTIDOS.exists() and FUNDIDOS.exists():
        d39 = gpd.read_file(FUNDIDOS).to_crs(CRS_M).set_index("polo_id")
        b39 = {pid: limpia(g) for pid, g in d39.geometry.items()}
        n39 = {pid: str(d39.polo_nombre.loc[pid]) for pid in b39}
        cambian = [p for p in los_23
                   if p in b39 and abs(b39[p].area - publicados[p].area) > 100.0]
        cambian += ["R09+R19+Z43"]
        capas.append(("el borde después de las decisiones",
                      {p: b39[p] for p in cambian}, n39))

    filas, resumen = [], []
    for etiqueta, bordes, nom in capas:
        cuales = [p for p in los_23 if p in bordes] if etiqueta.endswith("hoy") \
            else list(bordes)
        if not cuales:
            continue
        print("#" * 98)
        print(f"# {etiqueta.upper()}  ·  {len(cuales)} página(s)")
        print("#" * 98)
        for pid in cuales:
            g = bordes[pid]
            print("\n" + "=" * 98)
            print(f"{pid} · {nom[pid]}   ·   {g.area / 1e4:,.2f} ha")
            print("=" * 98)
            total_l = sobre_calle = 0.0
            for pieza, que, anillo in anillos(g):
                tramos, con, tot = recorrer(anillo, calles, sidx, fams)
                cortos = [t for t in tramos if t["largo"] < MINIMO]
                largos = []
                for t in (x for x in tramos if x["largo"] >= MINIMO):
                    if largos and largos[-1]["clave"] == t["clave"]:
                        largos[-1]["largo"] += t["largo"]
                        largos[-1]["ultimo"] = t["ultimo"]
                        largos[-1]["veces"] = largos[-1].get("veces", 1) + 1
                        continue
                    largos.append(dict(t))
                total_l += anillo.length
                sobre_calle += anillo.length * (con / max(tot, 1))
                print(f"\n  pieza {pieza + 1} · {que} · {anillo.length:,.0f} m · "
                      f"{con / max(tot, 1) * 100:.0f} % del recorrido va por alguna calle")
                if not largos:
                    print(f"      ningún tramo llega a {MINIMO:.0f} m: este contorno no corre "
                          f"por calles y no hay perímetro que escribir desde acá")
                for k, t in enumerate(largos, start=1):
                    juntado = (f"  (une {t['veces']} tramos separados por esquinas)"
                               if t.get("veces") else "")
                    print(f"      {k:>2}. {t['nombre']:<32} {t['largo']:>7,.0f} m   "
                          f"de {rango(t['primero']):<20} a {rango(t['ultimo'])}{juntado}")
                    filas.append(dict(
                        capa=etiqueta, polo=pid, polo_nombre=nom[pid], pieza=pieza + 1,
                        que=que, orden=k, calle=t["nombre"], clave_callejero=t["clave"],
                        largo_m=round(t["largo"], 1),
                        altura_desde=rango(t["primero"]), altura_hasta=rango(t["ultimo"]),
                        tramos_unidos=t.get("veces", 1)))
                if cortos:
                    print(f"      (se descartan {len(cortos)} tramos de menos de "
                          f"{MINIMO:.0f} m, que suman {sum(t['largo'] for t in cortos):,.0f} m: "
                          f"esquinas y ochavas)")
            pct = sobre_calle / total_l * 100 if total_l else 0.0
            print(f"\n  el contorno mide {total_l:,.0f} m y {pct:.0f} % corre sobre alguna calle")
            if pct < 50:
                print(f"  ATENCIÓN: menos de la mitad del contorno va por calles. Esta página no "
                      f"tiene un perímetro de calles que escribir; tiene una mancha")
            resumen.append(dict(capa=etiqueta, polo=pid, polo_nombre=nom[pid],
                                contorno_m=round(total_l), pct_sobre_calle=round(pct, 1),
                                tramos=sum(1 for f in filas
                                           if f["polo"] == pid and f["capa"] == etiqueta)))
        print()

    pd.DataFrame(filas).to_csv(SALIDA / "calles_de_los_23.csv", index=False, encoding="utf-8")
    pd.DataFrame(resumen).to_csv(SALIDA / "calles_de_los_23_resumen.csv", index=False,
                                 encoding="utf-8")
    (SALIDA / "calles_de_los_23_resumen.json").write_text(json.dumps(dict(
        fecha=HOY, paso_m=PASO, tolerancia_m=TOLERANCIA, tramo_minimo_m=MINIMO,
        paginas=len(los_23), tramos=len(filas),
        menos_de_la_mitad_por_calles=[r["polo"] for r in resumen
                                      if r["pct_sobre_calle"] < 50]),
        ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 98)
    print("RESUMEN · cuánto del contorno de cada página corre sobre calles")
    print("=" * 98)
    print(f"    {'polo':<12} {'página':<40}{'contorno':>10}{'% calles':>10}{'tramos':>8}")
    for r in sorted(resumen, key=lambda x: x["pct_sobre_calle"]):
        if not r["capa"].endswith("hoy"):
            continue
        print(f"    {r['polo']:<12} {r['polo_nombre'][:38]:<40}{r['contorno_m']:>9,} m"
              f"{r['pct_sobre_calle']:>9,.0f} %{r['tramos']:>8}")
    print(f"\nEscrito: calles_de_los_23.csv ({len(filas)} tramos) · "
          f"calles_de_los_23_resumen.csv · calles_de_los_23_resumen.json")


if __name__ == "__main__":
    main()
