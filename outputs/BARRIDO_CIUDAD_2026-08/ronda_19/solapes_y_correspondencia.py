# -*- coding: utf-8 -*-
"""La tabla de solapes, la correspondencia con las 124 concentraciones y la unión de los 41.

QUÉ RESUELVE
------------
  1. **`solapes_declarados.csv`** · todo par de polos que comparte superficie, con las hectáreas,
     los locales compartidos y la lista de cuáles son. Es la tabla que impide que el día que se
     sumen los polos se cuenten dos veces los mismos locales. Va **todo par**, no sólo el de
     Villa Ortúzar: un solape que no está declarado es un local contado dos veces esperando.
  2. **La correspondencia 124 × 41**, contra los bordes de ahora.
  3. **La unión de los 41**: superficie total y locales totales con el solape descontado una sola
     vez. Es la única cifra con la que se puede totalizar el conjunto.

CÓMO SE MIDE
------------
  - En EPSG:5347; lo que se guarda, en EPSG:4326.
  - La contención de un polígono dentro de otro se verifica por **superficie perdida**
    —`A.difference(B).area`— y nunca con `covers()`. La columna `ha_de_la_concentracion_fuera`
    es esa medida, y es la que decide si una concentración está dentro de un polo.
  - Los locales se cuentan por punto dentro del polígono, sobre el universo `anillo=nucleo &
    apto_geometria`, que es el mismo con el que se midió todo lo demás.
  - El detalle de qué locales son sale por `local_id`, barrio y comuna. Nombre y dirección están
    en `base/local.csv` por ese identificador y no se copian acá.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import json
import sys
from datetime import date
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
sys.path.insert(0, str(SALIDA))
import geometria_vigente_19 as gv  # noqa: E402
from geometria_vigente_19 import limpia  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()
BASE = BARRIDO / "base" / "local.csv"
PUBLICABLES = BARRIDO / "borrador_polos" / "polos_publicables.geojson"
ANEXO_B = BARRIDO / "desde_cowork" / "evidencia_2026" / "anexo_B_124_concentraciones.csv"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 98)
    print("SOLAPES · CORRESPONDENCIA · UNIÓN DE LOS 41   ·   contra la geometría vigente")
    print("=" * 98 + "\n")

    bordes, procedencia, soportes = gv.cargar()
    nombres = {pid: str(soportes.polo_nombre.loc[pid]) for pid in bordes}
    print(f"geometría vigente: {len(bordes)} polos")
    for etq in ("soporte previo", "cierre geométrico", "última tanda de bordes"):
        cuales = sorted(k for k, v in procedencia.items() if v == etq)
        print(f"  de {etq:<24} {len(cuales):>2}: {', '.join(cuales)}")
    print(f"  borde transitorio        : {', '.join(sorted(gv.TRANSITORIOS))}")
    print(f"  sin borde propio         : {', '.join(sorted(gv.SIN_BORDE_PROPIO))}\n")

    (SALIDA / "geometria").mkdir(exist_ok=True)
    gpd.GeoDataFrame(
        [dict(polo_id=pid, polo_nombre=nombres[pid], de_donde_sale=procedencia[pid],
              caracter=gv.caracter(pid),
              borde_transitorio="si" if pid in gv.TRANSITORIOS else "no",
              borde_es_propio="no" if pid in gv.SIN_BORDE_PROPIO else "si",
              ha=round(g.area / 10_000, 2), geometry=g)
         for pid, g in sorted(bordes.items())],
        geometry="geometry", crs=CRS_M).to_crs(CRS_G).to_file(
        SALIDA / "geometria" / "bordes_vigentes_41.geojson", driver="GeoJSON")

    base = pd.read_csv(BASE)
    base = base[(base.anillo == "nucleo") & (base.apto_geometria.astype(str).str.lower()
                                             .isin(["true", "1", "si", "sí"]))]
    pts = gpd.GeoDataFrame(
        base[["local_id", "barrio", "comuna"]].copy(),
        geometry=gpd.GeoSeries([Point(x, y) for x, y in zip(base.lon, base.lat)],
                               crs=CRS_G).to_crs(CRS_M).values,
        crs=CRS_M)
    sidx = pts.sindex
    print(f"base: {len(pts):,} locales del universo anillo=nucleo & apto_geometria\n")

    def locales_en(geom):
        cand = pts.iloc[list(sidx.query(geom))]
        return cand[cand.geometry.within(geom)]

    # ------------------------------------------------------------------ 1 · solapes
    print("=" * 98)
    print("1 · TODOS LOS PARES DE POLOS QUE COMPARTEN SUPERFICIE")
    print("=" * 98)
    filas, detalle = [], []
    for a, b in combinations(sorted(bordes), 2):
        ga, gb = bordes[a], bordes[b]
        if not ga.intersects(gb):
            continue
        inter = limpia(ga.intersection(gb))
        if inter.area < 1.0:
            continue
        compartidos = locales_en(inter)
        filas.append(dict(
            polo_a=a, nombre_a=nombres[a], polo_b=b, nombre_b=nombres[b],
            ha_compartidas=round(inter.area / 10_000, 2),
            locales_compartidos=len(compartidos),
            ha_de_a=round(ga.area / 10_000, 2), ha_de_b=round(gb.area / 10_000, 2),
            pct_de_a_compartido=round(inter.area / ga.area * 100, 1),
            pct_de_b_compartido=round(inter.area / gb.area * 100, 1),
            ha_de_a_fuera_de_b=round(ga.difference(gb).area / 10_000, 2),
            ha_de_b_fuera_de_a=round(gb.difference(ga).area / 10_000, 2),
            alguno_es_transitorio="si" if {a, b} & gv.TRANSITORIOS else "no",
            alguno_publica_su_barrio="si" if {a, b} & gv.DE_BARRIO else "no",
            locales_compartidos_ids=" ".join(sorted(compartidos.local_id.astype(str))),
        ))
        for r in compartidos.itertuples():
            detalle.append(dict(polo_a=a, nombre_a=nombres[a], polo_b=b, nombre_b=nombres[b],
                                local_id=r.local_id, barrio=r.barrio, comuna=r.comuna))

    filas.sort(key=lambda f: -f["locales_compartidos"])
    print(f"\n{len(filas)} pares de polos comparten superficie.\n")
    print(f"  {'par':<18} {'ha':>8} {'locales':>8}   {'% de A':>7} {'% de B':>7}  aviso")
    for f in filas:
        aviso = []
        if f["alguno_es_transitorio"] == "si":
            aviso.append("uno tiene borde transitorio")
        if f["alguno_publica_su_barrio"] == "si":
            aviso.append("uno publica el polígono de su barrio")
        print(f"  {f['polo_a']}+{f['polo_b']:<13} {f['ha_compartidas']:>8,.2f} "
              f"{f['locales_compartidos']:>8} {f['pct_de_a_compartido']:>6.1f} % "
              f"{f['pct_de_b_compartido']:>6.1f} %  {'; '.join(aviso)}")

    ids_unicos = {d["local_id"] for d in detalle}
    u = gv.union(bordes)
    suma_indiv = sum(len(locales_en(g)) for g in bordes.values())
    ha_indiv = sum(g.area for g in bordes.values()) / 10_000
    en_union = len(locales_en(u))
    ha_union = u.area / 10_000

    campos = ["polo_a", "nombre_a", "polo_b", "nombre_b", "ha_compartidas",
              "locales_compartidos", "ha_de_a", "ha_de_b", "pct_de_a_compartido",
              "pct_de_b_compartido", "ha_de_a_fuera_de_b", "ha_de_b_fuera_de_a",
              "alguno_es_transitorio", "alguno_publica_su_barrio", "locales_compartidos_ids"]
    with (SALIDA / "solapes_declarados.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    with (SALIDA / "solapes_locales_detalle.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["polo_a", "nombre_a", "polo_b", "nombre_b",
                                           "local_id", "barrio", "comuna"])
        w.writeheader()
        w.writerows(detalle)

    # el caso conocido, verificado contra la geometría vigente
    print("\n  el caso conocido · Villa Ortúzar contra Chacarita, Colegiales y Federico Lacroze:")
    z44 = bordes["Z44"]
    vecinos = {k: bordes[k] for k in ("R09", "R19", "Z43") if k in bordes}
    for k, g in vecinos.items():
        inter = limpia(z44.intersection(g))
        print(f"      contra {k} ({nombres[k]}): {inter.area / 10_000:>6,.2f} ha · "
              f"{len(locales_en(inter)):>3} locales")
    juntos = limpia(unary_union(list(vecinos.values())))
    inter3 = limpia(z44.intersection(juntos))
    loc3 = locales_en(inter3)
    coincide = abs(inter3.area / 10_000 - 15.93) < 0.05 and len(loc3) == 25
    print(f"      contra los tres juntos, sin contar dos veces lo que se pisan entre ellos:")
    print(f"          {inter3.area / 10_000:,.2f} ha · {len(loc3)} locales")
    print(f"      la cifra adoptada es 15,93 ha y 25 locales: "
          f"{'COINCIDE' if coincide else 'NO COINCIDE'}")

    # ------------------------------------------------------------------ 2 · la unión de los 41
    print("\n" + "=" * 98)
    print("2 · LA UNIÓN DE LOS 41 · el solape descontado una sola vez")
    print("=" * 98)
    print(f"  la suma de los 41 por separado : {ha_indiv:>10,.2f} ha · {suma_indiv:>6,} locales")
    print(f"  la unión de los 41             : {ha_union:>10,.2f} ha · {en_union:>6,} locales")
    print(f"  o sea que se cuentan de más    : {ha_indiv - ha_union:>10,.2f} ha · "
          f"{suma_indiv - en_union:>6,} locales")
    print(f"  locales distintos que están en dos o más polos: {len(ids_unicos):,}")
    print(f"  (la suma de la columna locales_compartidos da "
          f"{sum(f['locales_compartidos'] for f in filas):,}, y es mayor porque un local que")
    print(f"   está en tres polos aparece en los tres pares)")

    # ------------------------------------------------------------------ 3 · las 124
    print("\n" + "=" * 98)
    print("3 · LAS 124 CONCENTRACIONES CONTRA LOS BORDES DE AHORA")
    print("=" * 98)
    conc = gpd.read_file(PUBLICABLES).to_crs(CRS_M)
    nombres_conc = {}
    if ANEXO_B.exists():
        ax = pd.read_csv(ANEXO_B)
        col_id = next((c for c in ax.columns if c.lower() in ("polo_id", "concentracion_id",
                                                              "id")), None)
        col_nom = next((c for c in ax.columns if "nombre" in c.lower()), None)
        if col_id and col_nom:
            nombres_conc = dict(zip(ax[col_id].astype(str), ax[col_nom].astype(str)))

    filas_c = []
    for r in conc.itertuples():
        g = limpia(r.geometry)
        loc_g = locales_en(g)
        toques = []
        for pid, borde in bordes.items():
            if not g.intersects(borde):
                continue
            inter = limpia(g.intersection(borde))
            if inter.area < 1.0:
                continue
            toques.append((pid, inter.area, g.difference(borde).area))
        toques.sort(key=lambda x: -x[1])
        if toques:
            pid, area_i, fuera = toques[0]
            pct_dentro = 100 - fuera / g.area * 100
            estado = ("contenida" if fuera < g.area * 0.01 else
                      ("mayormente dentro" if pct_dentro >= 50 else "toca el borde"))
        else:
            pid, area_i, fuera, pct_dentro, estado = None, 0.0, g.area, 0.0, "fuera de todo polo"
        filas_c.append(dict(
            concentracion_id=r.polo_id,
            concentracion_nombre=nombres_conc.get(str(r.polo_id), ""),
            ha=round(g.area / 10_000, 2), n_locales_medidos=len(loc_g),
            n_locales_de_la_capa=int(r.n_locales),
            polo=pid or "", polo_nombre=nombres.get(pid, "") if pid else "",
            estado=estado,
            pct_de_la_concentracion_dentro=round(pct_dentro, 1),
            ha_de_la_concentracion_fuera=round(fuera / 10_000, 2),
            polos_que_toca=" ".join(t[0] for t in toques),
            n_polos_que_toca=len(toques),
            polo_es_transitorio="si" if pid in gv.TRANSITORIOS else "no"))

    d = pd.DataFrame(filas_c)
    dentro = d[d.estado.isin(["contenida", "mayormente dentro"])]
    tocan = d[d.estado == "toca el borde"]
    fuera_de_todo = d[d.estado == "fuera de todo polo"]
    print(f"\n  de las {len(d)} concentraciones:")
    print(f"    contenidas o mayormente dentro de un polo : {len(dentro):>3}  ·  "
          f"{dentro.n_locales_medidos.sum():>6,} locales  ·  {dentro.ha.sum():>9,.2f} ha")
    print(f"    tocan un borde sin quedar mayormente dentro: {len(tocan):>3}  ·  "
          f"{tocan.n_locales_medidos.sum():>6,} locales  ·  {tocan.ha.sum():>9,.2f} ha")
    print(f"    fuera de todo polo                        : {len(fuera_de_todo):>3}  ·  "
          f"{fuera_de_todo.n_locales_medidos.sum():>6,} locales  ·  "
          f"{fuera_de_todo.ha.sum():>9,.2f} ha")
    fuera_total = int(d[~d.index.isin(dentro.index)].n_locales_medidos.sum())
    print(f"\n  la cifra publicable: {len(dentro)} de las {len(d)} concentraciones caen dentro de")
    print(f"  algún polo y {len(d) - len(dentro)} no. Las que no suman {fuera_total:,} locales.")

    print(f"\n  las más grandes de las {len(fuera_de_todo)} que quedan fuera de todo polo:")
    for r in fuera_de_todo.sort_values("n_locales_medidos", ascending=False).head(10).itertuples():
        print(f"      {r.concentracion_id:<6} {str(r.concentracion_nombre)[:38]:<40} "
              f"{r.n_locales_medidos:>4} locales · {r.ha:>7,.2f} ha")

    d.to_csv(SALIDA / "correspondencia_124_x_41.csv", index=False, encoding="utf-8")

    resumen = dict(
        fecha=HOY, pares_con_solape=len(filas),
        locales_en_dos_o_mas_polos=len(ids_unicos),
        suma_de_los_41_locales=int(suma_indiv), union_de_los_41_locales=int(en_union),
        se_cuentan_de_mas_locales=int(suma_indiv - en_union),
        suma_de_los_41_ha=round(ha_indiv, 2), union_de_los_41_ha=round(ha_union, 2),
        se_cuentan_de_mas_ha=round(ha_indiv - ha_union, 2),
        concentraciones=len(d), concentraciones_dentro_de_un_polo=len(dentro),
        concentraciones_fuera=int(len(d) - len(dentro)),
        locales_de_las_que_estan_dentro=int(dentro.n_locales_medidos.sum()),
        locales_de_las_que_no=fuera_total,
        concentraciones_fuera_de_todo_polo=len(fuera_de_todo),
        villa_ortuzar_solape_ha=round(inter3.area / 10_000, 2),
        villa_ortuzar_solape_locales=len(loc3),
        villa_ortuzar_coincide_con_lo_adoptado=bool(coincide))
    (SALIDA / "solapes_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nEscrito: solapes_declarados.csv ({len(filas)} pares) · "
          f"solapes_locales_detalle.csv ({len(detalle)} filas) · "
          f"correspondencia_124_x_41.csv ({len(d)} filas) · solapes_resumen.json")


if __name__ == "__main__":
    main()
