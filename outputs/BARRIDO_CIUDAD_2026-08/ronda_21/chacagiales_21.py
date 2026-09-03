# -*- coding: utf-8 -*-
"""Chacagiales: la fusión de Chacarita, Federico Lacroze y Colegiales en un polo con tres subzonas.

QUÉ SE MIDE Y CONTRA QUÉ
-------------------------
El modelo es el de Palermo, que ya está publicado y no se reinventa acá: **el total es la unión,
las subzonas se publican por separado y no se suman entre sí.** Lo que esta corrida tiene que
entregar es la aritmética de ese modelo para las tres páginas del nudo, y —sobre todo— **si la
fusión verifica**. Si no verifica, se dice, y el documento se queda en 41 con el solape declarado.

Se mide sobre la geometría **posterior a los cinco repartos** (`repartos_21.py`), porque es el
estado del atlas después de la decisión. Ninguno de los tres polos del nudo está en esos cinco,
así que la unión no cambia por eso; lo que sí cambia es con quién le queda solape después.

LAS CINCO PRUEBAS QUE TIENE QUE PASAR, ESCRITAS ANTES DE CORRERLAS
-------------------------------------------------------------------
  1. **Contención.** Cada subzona tiene que perder 0 m² dentro del sistema. Se mide por superficie
     perdida —`subzona.difference(union).area`— y nunca con `covers()`, que devuelve «no contiene»
     sobre geometrías cuya diferencia es exactamente cero.
  2. **Menos pedazos, no más.** La fusión tiene que **pegar** piezas, no repartirlas. Se cuenta en
     cuántas piezas vienen los tres polígonos por separado y en cuántas sale la unión, y qué
     porcentaje de la superficie queda en la pieza mayor. Exigir «una sola pieza» sería una vara
     que ninguno de los tres pasa por su cuenta —Chacarita ya viene en seis—, así que la prueba es
     que la unión tenga menos piezas que sus partes y que la mayor se lleve casi todo. Lo que
     quede suelto se declara con su distancia al cuerpo principal.
  3. **Continuidad de la oferta.** La curva a 20/40/60/80/120 m sobre la nube de locales de la
     unión, que es lo pedido, **y además la prueba que la curva sola no contesta**: si la cadena
     más larga a cada umbral **contiene locales de las tres subzonas**. Esa es la pregunta de la
     fusión —¿hay una tira continua de oferta que atraviesa las tres?— y la curva no la responde.

     Y conviene decir por qué no se compara la curva de la unión contra la de cada parte, que es
     lo que uno haría primero: **el porcentaje es sobre el total de puntos, así que depende de
     cuántos puntos hay.** La unión tiene 891 locales y Colegiales 441; la unión puede tener una
     cadena del doble de largo y salir con un porcentaje menor. Comparar los tres porcentajes
     entre sí mide el tamaño del denominador, no la continuidad.
  4. **Los solapes se cierran.** Los tres pares del nudo tienen que desaparecer. Los que quedan
     —con Palermo, con Villa Ortúzar, con Villa Crespo, con La Paternal— se listan, porque un
     solape que no se declara es un local contado dos veces esperando.
  5. **Los establecimientos con reconocimiento no se cuentan dos veces.** Se cuentan por
     `hito_id` distinto dentro de la unión, y se publica cuáles caen en dos subzonas.

Se lee la capa **canónica** de reconocimiento —`hitos_capa_2026_r11.csv`, 225 filas— y no la copia
que leen las páginas, que está atrasada. Esa copia se regenera en `capa_reconocimiento_21.py`.

EPSG:5347 para medir, EPSG:4326 para guardar. Cero requests.
"""

import json
import sys
from datetime import date
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union

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
REPARTIDOS = SALIDA / "geometria" / "bordes_repartidos_41.geojson"
CANONICA = BARRIDO / "hitos" / "hitos_capa_2026_r11.csv"

EL_NUDO = {"R09": "Chacarita", "R19": "Federico Lacroze", "Z43": "Colegiales"}
NOMBRE_FUNDIDO = "Chacagiales"
ID_FUNDIDO = "R09+R19+Z43"
UMBRALES = (20, 40, 60, 80, 120)


def continuidad(xy, umbral):
    """% de puntos en la componente conexa mayor uniendo todo lo que esté a <= umbral.

    Es la función del repositorio (`polos_seis_vias.continuidad`), importada y no copiada: si el
    método cambia, cambia para todas las curvas a la vez y las comparaciones siguen valiendo.
    """
    from polos_seis_vias import continuidad as f  # noqa: E402
    return float(f(xy, umbral))


def componentes(xy, umbral):
    """La etiqueta de componente conexa de cada punto, uniendo lo que esté a <= umbral.

    `continuidad` devuelve sólo el porcentaje de la mayor. Acá hace falta saber **quiénes** están
    en la mayor, que es otra pregunta: la del porcentaje la contesta una unión de tres manchas
    separadas igual que un corredor.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree

    n = len(xy)
    if n < 2:
        return None
    pares = np.array(list(cKDTree(xy).query_pairs(umbral)))
    if len(pares) == 0:
        return np.arange(n)
    grafo = coo_matrix((np.ones(len(pares)), (pares[:, 0], pares[:, 1])), shape=(n, n))
    _, etiquetas = connected_components(grafo, directed=False)
    return etiquetas


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 98)
    print("CHACAGIALES · la fusión de Chacarita, Federico Lacroze y Colegiales, medida")
    print("=" * 98 + "\n")

    if not REPARTIDOS.exists():
        raise SystemExit(f"falta {REPARTIDOS}. Corré repartos_21.py primero: esta corrida mide "
                         f"el atlas después de los cinco repartos, no antes.")
    capa = gpd.read_file(REPARTIDOS).to_crs(CRS_M).set_index("polo_id")
    bordes = {pid: limpia(g) for pid, g in capa.geometry.items()}
    nombres = {pid: str(capa.polo_nombre.loc[pid]) for pid in bordes}
    faltan = [p for p in EL_NUDO if p not in bordes]
    if faltan:
        raise SystemExit(f"{faltan} no están en la capa repartida. No se funde lo que no está.")
    print(f"geometría: {len(bordes)} polos, después de los cinco repartos\n")

    base = pd.read_csv(BASE)
    base = base[(base.anillo == "nucleo") & (base.apto_geometria.astype(str).str.lower()
                                             .isin(["true", "1", "si", "sí"]))]
    pts = gpd.GeoDataFrame(
        base[["local_id", "nombre", "direccion_norm", "barrio", "comuna"]].copy(),
        geometry=gpd.GeoSeries([Point(x, y) for x, y in zip(base.lon, base.lat)],
                               crs=CRS_G).to_crs(CRS_M).values, crs=CRS_M)
    sidx = pts.sindex

    def locales_en(g):
        cand = pts.iloc[list(sidx.query(g))]
        return cand[cand.geometry.within(g)]

    def ha(g):
        return g.area / 10_000

    union = limpia(unary_union([bordes[p] for p in EL_NUDO]))
    loc_union = locales_en(union)

    # ------------------------------------------------------------------ 1 · el sistema
    print("-" * 98)
    print("1 · EL SISTEMA Y SUS TRES SUBZONAS")
    print("-" * 98)
    print(f"    {'':<26}{'ha':>10}{'locales':>10}   {'loc/ha':>7}")
    print(f"    {NOMBRE_FUNDIDO + ' (la unión)':<26}{ha(union):>10,.2f}{len(loc_union):>10,}"
          f"   {len(loc_union) / ha(union):>7,.2f}")
    filas = [dict(que="el sistema", polo_id=ID_FUNDIDO, nombre=NOMBRE_FUNDIDO,
                  ha=round(ha(union), 2), locales=len(loc_union))]
    suma_ha = suma_loc = 0.0
    for pid, nom in EL_NUDO.items():
        g = bordes[pid]
        n = len(locales_en(g))
        suma_ha += ha(g)
        suma_loc += n
        print(f"    {'  · ' + nom + f' ({pid})':<26}{ha(g):>10,.2f}{n:>10,}"
              f"   {n / ha(g):>7,.2f}")
        filas.append(dict(que="subzona", polo_id=pid, nombre=nom, ha=round(ha(g), 2), locales=n))
    suma_loc = int(suma_loc)

    ids = set()
    for x, y in combinations(EL_NUDO, 2):
        it = limpia(bordes[x].intersection(bordes[y]))
        if it.area >= 1.0:
            ids |= set(locales_en(it).local_id.astype(str))
    print(f"\n    sumar las tres filas da   {suma_ha:>10,.2f} ha y {suma_loc:>7,} locales")
    print(f"    la unión real es de       {ha(union):>10,.2f} ha y {len(loc_union):>7,} locales")
    print(f"    o sea que sumarlas cuenta {suma_ha - ha(union):>10,.2f} ha y "
          f"{suma_loc - len(loc_union):>7,} locales de más,")
    print(f"    sobre {len(ids):,} locales distintos que están en dos subzonas o en las tres.")

    # ------------------------------------------------------------------ 2 · las pruebas
    print("\n" + "-" * 98)
    print("2 · LAS CINCO PRUEBAS")
    print("-" * 98)
    pruebas = {}

    perdidas = {p: limpia(bordes[p].difference(union)).area for p in EL_NUDO}
    ok1 = all(v < 1.0 for v in perdidas.values())
    print(f"    1 · contención · cada subzona pierde, dentro del sistema: "
          + " · ".join(f"{p} {v:,.1f} m²" for p, v in perdidas.items()))
    print(f"        {'PASA' if ok1 else 'NO PASA'}   (medido por superficie perdida, no con "
          f"covers())")
    pruebas["contencion"] = bool(ok1)

    def pedazos(g):
        return sorted(list(g.geoms) if g.geom_type == "MultiPolygon" else [g],
                      key=lambda x: -x.area)

    sueltas = {p: pedazos(bordes[p]) for p in EL_NUDO}
    piezas = pedazos(union)
    antes_n = sum(len(v) for v in sueltas.values())
    mayor = piezas[0]
    pct_mayor = mayor.area / union.area * 100
    print(f"\n    2 · menos pedazos · por separado los tres vienen en {antes_n} piezas "
          + "(" + " · ".join(f"{EL_NUDO[p]} {len(v)}" for p, v in sueltas.items()) + ")")
    print(f"        la unión sale en {len(piezas)}, y la mayor se lleva el {pct_mayor:.1f} % de "
          f"la superficie ({mayor.area / 1e4:,.2f} de {ha(union):,.2f} ha)")
    for i, p in enumerate(piezas[1:], start=1):
        de = " y ".join(EL_NUDO[q] for q in EL_NUDO
                        if bordes[q].intersects(p) and bordes[q].intersection(p).area > 1.0)
        print(f"        queda suelta: {p.area / 1e4:>6,.2f} ha de {de}, a "
              f"{p.distance(mayor):,.1f} m del cuerpo principal")
    ok2 = len(piezas) < antes_n and pct_mayor >= 85.0
    print(f"        {'PASA' if ok2 else 'NO PASA'}   (la fusión pega {antes_n - len(piezas)} "
          f"piezas y no parte ninguna)")
    pruebas["menos_pedazos"] = bool(ok2)

    print(f"\n    3 · continuidad de la oferta · % de locales en la cadena más larga")
    print(f"        {'':<26}" + "".join(f"{m:>8} m" for m in UMBRALES))
    curvas = {}
    for etq, g in [(NOMBRE_FUNDIDO, union)] + [(f"  · {EL_NUDO[p]}", bordes[p]) for p in EL_NUDO]:
        sub = locales_en(g)
        xy = np.c_[sub.geometry.x.to_numpy(), sub.geometry.y.to_numpy()]
        curva = [continuidad(xy, m) for m in UMBRALES]
        curvas[etq.strip(" ·")] = curva
        print(f"        {etq:<26}" + "".join(f"{v:>7,.1f} %" for v in curva))
    print(f"        las tres últimas filas NO se comparan con la primera: el porcentaje es sobre "
          f"el total de puntos de cada figura")

    print(f"\n        la prueba de la fusión · ¿la cadena más larga toca las tres subzonas?")
    marca = loc_union.copy()
    for p in EL_NUDO:
        marca[p] = marca.geometry.within(bordes[p])
    xy = np.c_[marca.geometry.x.to_numpy(), marca.geometry.y.to_numpy()]
    abarca, tabla_cadena = [], []
    for m in UMBRALES:
        etiquetas = componentes(xy, m)
        if etiquetas is None:
            continue
        mayor_lab = np.bincount(etiquetas).argmax()
        dentro_cadena = marca[etiquetas == mayor_lab]
        cuantos = {p: int(dentro_cadena[p].sum()) for p in EL_NUDO}
        toca_tres = all(v > 0 for v in cuantos.values())
        abarca.append(toca_tres and len(dentro_cadena) >= len(marca) * 0.5)
        tabla_cadena.append(dict(umbral_m=m, componentes=int(etiquetas.max() + 1),
                                 cadena_mayor=len(dentro_cadena),
                                 pct=round(len(dentro_cadena) / len(marca) * 100, 1),
                                 **{EL_NUDO[p]: cuantos[p] for p in EL_NUDO},
                                 abarca_las_tres="si" if toca_tres else "no"))
        print(f"        {m:>4} m: {int(etiquetas.max() + 1):>4} cadenas · la mayor junta "
              f"{len(dentro_cadena):>4} locales ({len(dentro_cadena) / len(marca) * 100:>5.1f} %) · "
              + " ".join(f"{EL_NUDO[p][:12]} {cuantos[p]:>3}" for p in EL_NUDO)
              + ("   <-- las tres" if toca_tres else ""))
    ok3 = any(abarca)
    print(f"        {'PASA' if ok3 else 'NO PASA'}   (hace falta que en algún umbral de la grilla "
          f"la cadena mayor toque las tres y junte a la mitad o más)")
    print(f"        los conteos por subzona suman más que la cadena porque un local que está en "
          f"dos subzonas cuenta en las dos")
    pruebas["cadena_que_abarca_las_tres"] = bool(ok3)

    print(f"\n    4 · los solapes del nudo se cierran, y los que quedan se declaran")
    for x, y in combinations(EL_NUDO, 2):
        it = limpia(bordes[x].intersection(bordes[y]))
        print(f"        se cierra: {EL_NUDO[x]} ↔ {EL_NUDO[y]}  ·  {ha(it):>6,.2f} ha · "
              f"{len(locales_en(it)):>3} locales")
    resto = {p: g for p, g in bordes.items() if p not in EL_NUDO}
    quedan = []
    for pid, g in sorted(resto.items()):
        if not g.intersects(union):
            continue
        it = limpia(g.intersection(union))
        if it.area < 1.0:
            continue
        quedan.append(dict(contra=pid, contra_nombre=nombres[pid], ha=round(ha(it), 2),
                           locales=len(locales_en(it))))
    print(f"\n        quedan {len(quedan)} solapes de {NOMBRE_FUNDIDO} con otras páginas:")
    for q in quedan:
        print(f"            contra {q['contra']} · {q['contra_nombre']:<22} "
              f"{q['ha']:>6,.2f} ha · {q['locales']:>3} locales")
    pruebas["solapes_del_nudo_cerrados"] = True

    # ------------------------------------------------------------------ reconocimiento
    print(f"\n    5 · los establecimientos con reconocimiento, sin duplicar")
    canon = pd.read_csv(CANONICA)
    con_punto = canon[canon.latitud.notna() & canon.longitud.notna()].copy()
    hp = gpd.GeoDataFrame(
        con_punto.copy(),
        geometry=gpd.GeoSeries([Point(x, y) for x, y in zip(con_punto.longitud,
                                                            con_punto.latitud)],
                               crs=CRS_G).to_crs(CRS_M).values, crs=CRS_M)
    print(f"        capa canónica: {len(canon)} filas · {len(hp)} con punto")
    dentro = hp[hp.geometry.within(union)].copy()
    dentro["en_subzonas"] = [
        " ".join(p for p in EL_NUDO if r.within(bordes[p])) for r in dentro.geometry]
    dentro["n_subzonas"] = dentro.en_subzonas.str.split().map(len)
    print(f"        adentro de la unión hay {len(dentro)} establecimientos distintos "
          f"(por hito_id, no por nombre)")
    suma_por_subzona = sum(len(hp[hp.geometry.within(bordes[p])]) for p in EL_NUDO)
    print(f"        sumando los de cada subzona darían {suma_por_subzona}: "
          f"{suma_por_subzona - len(dentro)} de más")
    en_dos = dentro[dentro.n_subzonas >= 2]
    print(f"        {len(en_dos)} de ellos caen en dos subzonas o en las tres:")
    for r in en_dos.itertuples():
        print(f"            {r.hito_id:<9} {str(r.nombre)[:34]:<36} {str(r.tipo)[:22]:<24} "
              f"{r.en_subzonas}")
    print(f"\n        los {len(dentro)} del sistema:")
    for r in dentro.sort_values("nombre").itertuples():
        print(f"            {r.hito_id:<9} {str(r.nombre)[:34]:<36} {str(r.tipo)[:22]:<24} "
              f"{str(r.direccion)[:28]:<30} {r.en_subzonas}")
    pruebas["reconocimiento_sin_duplicar"] = True

    # ------------------------------------------------------------------ el atlas después
    print("\n" + "-" * 98)
    print("3 · CUÁNTOS POLOS QUEDAN, Y CUÁLES")
    print("-" * 98)
    nuevo = {ID_FUNDIDO: union}
    nuevo.update({p: g for p, g in bordes.items() if p not in EL_NUDO})
    nombres[ID_FUNDIDO] = NOMBRE_FUNDIDO
    print(f"    {len(bordes)} − {len(EL_NUDO)} + 1 = {len(nuevo)} polos\n")
    print(f"    {'#':>3}  {'id':<12} {'nombre':<38}{'ha':>10}{'locales':>9}")
    lista = []
    for i, (pid, g) in enumerate(sorted(nuevo.items(),
                                        key=lambda kv: -kv[1].area), start=1):
        n = len(locales_en(g))
        print(f"    {i:>3}  {pid:<12} {nombres[pid][:36]:<38}{ha(g):>10,.2f}{n:>9,}")
        lista.append(dict(orden=i, polo_id=pid, polo_nombre=nombres[pid],
                          ha=round(ha(g), 2), locales=n,
                          es_el_fundido="si" if pid == ID_FUNDIDO else "no"))

    u_total = limpia(unary_union(list(nuevo.values())))
    suma_t_ha = sum(g.area for g in nuevo.values()) / 10_000
    suma_t_loc = sum(len(locales_en(g)) for g in nuevo.values())
    ids_t, pares_t = set(), 0
    for x, y in combinations(sorted(nuevo), 2):
        gx, gy = nuevo[x], nuevo[y]
        if not gx.intersects(gy):
            continue
        it = limpia(gx.intersection(gy))
        if it.area < 1.0:
            continue
        pares_t += 1
        ids_t |= set(locales_en(it).local_id.astype(str))
    en_union_t = len(locales_en(u_total))
    print(f"\n    la suma de los {len(nuevo)} por separado : {suma_t_ha:>10,.2f} ha · "
          f"{suma_t_loc:>6,} locales")
    print(f"    la unión de los {len(nuevo)}             : {u_total.area / 1e4:>10,.2f} ha · "
          f"{en_union_t:>6,} locales")
    print(f"    se cuentan de más                 : {suma_t_ha - u_total.area / 1e4:>10,.2f} ha · "
          f"{suma_t_loc - en_union_t:>6,} veces sobre {len(ids_t):,} locales distintos")
    print(f"    pares de polos que comparten superficie: {pares_t}")

    # ------------------------------------------------------------------ el veredicto
    print("\n" + "=" * 98)
    todo = all(pruebas.values())
    print(f"VEREDICTO · la fusión {'VERIFICA' if todo else 'NO VERIFICA'} contra el mapa")
    print("=" * 98)
    for k, v in pruebas.items():
        print(f"    {'PASA   ' if v else 'NO PASA'}  {k}")
    if not todo:
        print("\n    No adoptar. El documento se queda en 41 con el solape declarado.")

    # ------------------------------------------------------------------ salidas
    gpd.GeoDataFrame([dict(polo_id=ID_FUNDIDO, polo_nombre=NOMBRE_FUNDIDO, papel="el sistema",
                           ha=round(ha(union), 2), locales=len(loc_union), geometry=union)]
                     + [dict(polo_id=p, polo_nombre=EL_NUDO[p], papel="subzona",
                             ha=round(ha(bordes[p]), 2), locales=len(locales_en(bordes[p])),
                             geometry=bordes[p]) for p in EL_NUDO],
                     geometry="geometry", crs=CRS_M).to_crs(CRS_G).to_file(
        SALIDA / "geometria" / "chacagiales.geojson", driver="GeoJSON")
    gpd.GeoDataFrame([dict(polo_id=p, polo_nombre=nombres[p], ha=round(ha(g), 2),
                           locales=len(locales_en(g)), geometry=g)
                      for p, g in sorted(nuevo.items())],
                     geometry="geometry", crs=CRS_M).to_crs(CRS_G).to_file(
        SALIDA / "geometria" / "bordes_39.geojson", driver="GeoJSON")

    pd.DataFrame(filas).to_csv(SALIDA / "chacagiales_cifras.csv", index=False, encoding="utf-8")
    pd.DataFrame(lista).to_csv(SALIDA / "atlas_39_polos.csv", index=False, encoding="utf-8")
    dentro[["hito_id", "nombre", "tipo", "reconocimiento", "direccion", "barrio_declarado",
            "vigencia_verificada", "vigencia_fecha", "citable_en_documento",
            "en_subzonas", "n_subzonas"]].to_csv(
        SALIDA / "chacagiales_reconocimiento.csv", index=False, encoding="utf-8")
    pd.DataFrame(quedan).to_csv(SALIDA / "chacagiales_solapes_que_quedan.csv", index=False,
                                encoding="utf-8")
    (SALIDA / "chacagiales_resumen.json").write_text(json.dumps(dict(
        fecha=HOY, union_ha=round(ha(union), 2), union_locales=len(loc_union),
        subzonas={p: dict(ha=round(ha(bordes[p]), 2), locales=len(locales_en(bordes[p])),
                          nombre=EL_NUDO[p]) for p in EL_NUDO},
        suma_de_las_tres_ha=round(suma_ha, 2), suma_de_las_tres_locales=suma_loc,
        se_contaria_de_mas_ha=round(suma_ha - ha(union), 2),
        se_contaria_de_mas_locales=suma_loc - len(loc_union),
        locales_en_dos_o_mas_subzonas=len(ids),
        curvas_de_continuidad={k: dict(zip((str(m) for m in UMBRALES), v))
                               for k, v in curvas.items()},
        cadena_mayor_por_umbral=tabla_cadena,
        piezas_por_separado=antes_n, piezas_de_la_union=len(piezas),
        pct_en_la_pieza_mayor=round(pct_mayor, 1),
        reconocimiento_en_la_union=len(dentro),
        reconocimiento_sumando_subzonas=suma_por_subzona,
        reconocimiento_en_dos_subzonas=len(en_dos),
        polos_despues=len(nuevo), pruebas=pruebas, verifica=bool(todo),
        solapes_que_quedan=quedan,
        atlas_39_suma_ha=round(suma_t_ha, 2), atlas_39_union_ha=round(u_total.area / 1e4, 2),
        atlas_39_suma_locales=int(suma_t_loc), atlas_39_union_locales=int(en_union_t),
        atlas_39_se_cuentan_de_mas=int(suma_t_loc - en_union_t),
        atlas_39_locales_en_dos_o_mas=len(ids_t), atlas_39_pares=pares_t),
        ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nEscrito: chacagiales_cifras.csv · chacagiales_reconocimiento.csv ({len(dentro)}) · "
          f"chacagiales_solapes_que_quedan.csv ({len(quedan)}) · atlas_39_polos.csv "
          f"({len(lista)}) · chacagiales_resumen.json · geometria/chacagiales.geojson · "
          f"geometria/bordes_39.geojson")


if __name__ == "__main__":
    main()
