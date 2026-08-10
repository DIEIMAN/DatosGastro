# -*- coding: utf-8 -*-
"""Los solapes entre polos y la correspondencia con las 124 concentraciones, con los bordes nuevos.

QUÉ RESUELVE
------------
  1. **`solapes_declarados.csv`** es la tabla que impide que el día que se sumen los polos se
     cuenten dos veces los mismos locales. Va **todo par de polos que se toca**, no sólo el de
     Villa Ortúzar: un solape que no está declarado es un local contado dos veces esperando.
  2. **La correspondencia 124 × 41**, rehecha. La salida vigente se calculó contra la geometría
     anterior y ya no describe el conjunto; hoy el documento no publica la relación justamente
     por eso.

CÓMO SE MIDE
------------
  - En EPSG:5347, y se guarda lo que se guarda en EPSG:4326.
  - La contención de un polígono dentro de otro se verifica por **superficie perdida**
    —`A.difference(B).area`— y nunca con `covers()`. La columna `ha_de_A_fuera_de_B` es esa
    medida, y es la que hay que mirar para decir «esta concentración está adentro de este polo».
  - Los locales compartidos se cuentan por punto dentro del polígono, sobre la misma base de
    23.981 locales del universo `anillo=nucleo & apto_geometria` con la que se midió todo lo
    demás.
  - El detalle de qué locales son sale por `local_id`, barrio y comuna. Nombre y dirección de
    cada uno están en `base/local.csv` por `local_id` y no se copian acá: para no contar dos
    veces alcanza con el identificador, y una lista de filas individuales no hace falta.

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
import geometria_vigente  # noqa: E402
from geometria_vigente import limpia  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()
BASE = BARRIDO / "base" / "local.csv"
PUBLICABLES = BARRIDO / "borrador_polos" / "polos_publicables.geojson"
ANEXO_B = BARRIDO / "desde_cowork" / "evidencia_2026" / "anexo_B_124_concentraciones.csv"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 98)
    print("SOLAPES ENTRE POLOS · y la correspondencia con las 124 concentraciones")
    print("=" * 98 + "\n")

    bordes, procedencia, soportes = geometria_vigente.cargar()
    nombres = {pid: str(soportes.polo_nombre.loc[pid]) for pid in bordes}

    # La capa vigente completa, en un archivo. Sin esto, cada tanda vuelve a armarla leyendo tres
    # geojson en el orden correcto, y basta con que uno se saltee una adopción para que mida otra
    # cosa. Es la misma que usan el control de anclas y las dos tablas de acá.
    (SALIDA / "geometria").mkdir(exist_ok=True)
    gpd.GeoDataFrame(
        [dict(polo_id=pid, polo_nombre=nombres[pid], de_donde_sale=procedencia[pid],
              borde_tentativo="si" if pid in geometria_vigente.TENTATIVOS else "no",
              borde_es_propio="no" if pid in geometria_vigente.SIN_BORDE_PROPIO else "si",
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
    print("TODOS LOS PARES DE POLOS QUE SE TOCAN")
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
            ha_de_solape=round(inter.area / 10_000, 2), locales_de_solape=len(compartidos),
            ha_de_a=round(ga.area / 10_000, 2), ha_de_b=round(gb.area / 10_000, 2),
            pct_de_a_en_b=round(inter.area / ga.area * 100, 1),
            pct_de_b_en_a=round(inter.area / gb.area * 100, 1),
            ha_de_a_fuera_de_b=round(ga.difference(gb).area / 10_000, 2),
            ha_de_b_fuera_de_a=round(gb.difference(ga).area / 10_000, 2),
            alguno_es_tentativo="si" if {a, b} & geometria_vigente.TENTATIVOS else "no",
            alguno_es_de_barrio="si" if {a, b} & geometria_vigente.SIN_BORDE_PROPIO else "no",
            locales_compartidos_ids=" ".join(sorted(compartidos.local_id.astype(str))),
        ))
        for r in compartidos.itertuples():
            detalle.append(dict(polo_a=a, polo_b=b, local_id=r.local_id,
                                barrio=r.barrio, comuna=r.comuna))

    filas.sort(key=lambda f: -f["locales_de_solape"])
    print(f"{len(filas)} pares de polos comparten superficie.\n")
    print(f"  {'par':<16} {'ha':>8} {'locales':>8}   {'% de A':>7} {'% de B':>7}  aviso")
    for f in filas:
        aviso = []
        if f["alguno_es_tentativo"] == "si":
            aviso.append("uno es tentativo")
        if f["alguno_es_de_barrio"] == "si":
            aviso.append("uno publica el polígono de su barrio")
        print(f"  {f['polo_a']}+{f['polo_b']:<11} {f['ha_de_solape']:>8,.2f} "
              f"{f['locales_de_solape']:>8} {f['pct_de_a_en_b']:>6.1f} % "
              f"{f['pct_de_b_en_a']:>6.1f} %  {'; '.join(aviso)}")

    total_solape = sum(f["locales_de_solape"] for f in filas)
    ids_unicos = {d["local_id"] for d in detalle}
    u = geometria_vigente.union(bordes)
    suma_indiv = sum(len(locales_en(g)) for g in bordes.values())
    en_union = len(locales_en(u))
    print(f"\n  la suma de los 41 por separado da   : {suma_indiv:,} locales")
    print(f"  la unión de los 41 mide             : {en_union:,} locales")
    print(f"  o sea que se cuentan de más         : {suma_indiv - en_union:,} locales")
    print(f"  locales distintos que están en 2 o más polos: {len(ids_unicos):,}")
    print(f"  (la suma de la columna locales_de_solape da {total_solape:,}, y es mayor porque un")
    print(f"   local que está en tres polos aparece en los tres pares)")
    print(f"  superficie de la unión: {u.area / 10_000:,.2f} ha · "
          f"suma de las 41 por separado: {sum(g.area for g in bordes.values()) / 10_000:,.2f} ha")

    # Villa Ortúzar, que es el que la decisión pedía verificar
    print("\n  el caso que la decisión pedía verificar · Villa Ortúzar contra Chacarita,")
    print("  Colegiales y Federico Lacroze:")
    z44 = bordes["Z44"]
    vecinos = {k: bordes[k] for k in ("R09", "R19", "Z43") if k in bordes}
    for k, g in vecinos.items():
        inter = limpia(z44.intersection(g))
        print(f"      contra {k} ({nombres[k]}): {inter.area / 10_000:>6,.2f} ha · "
              f"{len(locales_en(inter)):>3} locales")
    juntos = limpia(unary_union(list(vecinos.values())))
    inter3 = limpia(z44.intersection(juntos))
    loc3 = locales_en(inter3)
    print(f"      contra los tres juntos, sin contar dos veces lo que se pisa entre ellos:")
    print(f"          {inter3.area / 10_000:,.2f} ha · {len(loc3)} locales")
    print(f"      la cifra que la decisión trae es 15,93 ha y 25 locales: "
          f"{'coincide' if abs(inter3.area / 10_000 - 15.93) < 0.05 and len(loc3) == 25 else 'NO coincide'}")

    campos = ["polo_a", "nombre_a", "polo_b", "nombre_b", "ha_de_solape", "locales_de_solape",
              "ha_de_a", "ha_de_b", "pct_de_a_en_b", "pct_de_b_en_a", "ha_de_a_fuera_de_b",
              "ha_de_b_fuera_de_a", "alguno_es_tentativo", "alguno_es_de_barrio",
              "locales_compartidos_ids"]
    with (SALIDA / "solapes_declarados.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    with (SALIDA / "solapes_locales_detalle.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["polo_a", "polo_b", "local_id", "barrio", "comuna"])
        w.writeheader()
        w.writerows(detalle)

    # ------------------------------------------------------------------ 2 · las 124
    print("\n" + "=" * 98)
    print("LAS 124 CONCENTRACIONES CONTRA LOS BORDES NUEVOS")
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
            pct_de_la_concentracion_dentro_del_polo=round(pct_dentro, 1),
            ha_de_la_concentracion_fuera_del_polo=round(fuera / 10_000, 2),
            polos_que_toca=" ".join(t[0] for t in toques),
            n_polos_que_toca=len(toques),
            polo_es_tentativo="si" if pid in geometria_vigente.TENTATIVOS else "no"))

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
    print(f"\n  la cifra publicable: {len(dentro)} de las {len(d)} concentraciones caen dentro de")
    print(f"  algún polo y {len(d) - len(dentro)} no. Las que no suman "
          f"{d[~d.index.isin(dentro.index)].n_locales_medidos.sum():,} locales.")

    print(f"\n  las {len(fuera_de_todo)} que quedan fuera de todo polo, por tamaño:")
    for r in fuera_de_todo.sort_values("n_locales_medidos", ascending=False).itertuples():
        print(f"      {r.concentracion_id:<6} {str(r.concentracion_nombre)[:38]:<40} "
              f"{r.n_locales_medidos:>4} locales · {r.ha:>7,.2f} ha")

    d.to_csv(SALIDA / "correspondencia_124_x_41.csv", index=False, encoding="utf-8")

    resumen = dict(
        fecha=HOY, pares_con_solape=len(filas),
        locales_en_dos_o_mas_polos=len(ids_unicos),
        suma_de_los_41=int(suma_indiv), union_de_los_41=int(en_union),
        se_cuentan_de_mas=int(suma_indiv - en_union),
        ha_de_la_union=round(u.area / 10_000, 2),
        concentraciones=len(d), concentraciones_dentro_de_un_polo=len(dentro),
        concentraciones_fuera=int(len(d) - len(dentro)),
        locales_de_las_que_estan_dentro=int(dentro.n_locales_medidos.sum()),
        locales_de_las_que_no=int(d[~d.index.isin(dentro.index)].n_locales_medidos.sum()),
        villa_ortuzar_solape_ha=round(inter3.area / 10_000, 2),
        villa_ortuzar_solape_locales=len(loc3))
    (SALIDA / "solapes_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nEscrito: solapes_declarados.csv ({len(filas)} pares) · "
          f"solapes_locales_detalle.csv ({len(detalle)} filas) · "
          f"correspondencia_124_x_41.csv ({len(d)} filas) · solapes_resumen.json")


if __name__ == "__main__":
    main()
