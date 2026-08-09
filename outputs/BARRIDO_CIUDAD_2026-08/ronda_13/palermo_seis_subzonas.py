# -*- coding: utf-8 -*-
"""Palermo contra las SEIS subzonas que nombra la ficha, no contra las tres que se midieron.

Las rondas 9 y 10 cruzaron R01 contra P091 Soho, P078 Hollywood y P065 Las Canitas. La ficha de
R01 en fichas_corpus_polos.csv nombra tres mas -P073 Palermo Botanico, P087 Palermo Pacifico y
P092 Villa Freud- que nunca entraron a ninguna interseccion. Esto las mide, y mide cada una
contra las 8 piezas del residuo de la ronda 10.

Predicciones escritas antes de correr: ver LECTURA_PREVIA_RONDA_13.md.

Trampas de shapely/GEOS que la ronda 7 dejo anotadas y que aca se respetan:
  - medir area en metros, nunca en grados: se proyecta a EPSG:5347 (POSGAR 2007 / Argentina 5).
  - no usar covers()/contains() como predicado: se mide superficie perdida, que es R12.
  - buffer(0) antes de cada operacion booleana: los poligonos del borrador tienen
    autointersecciones y GEOS falla en silencio, devolviendo areas de cero sin avisar.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

BASE = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).resolve().parent

# POSGAR 2007 / Argentina faja 5: es la proyeccion metrica de CABA que usan las rondas previas.
CRS_METRICO = "EPSG:5347"

SUBZONAS = {
    "P091": "Palermo Soho",
    "P078": "Palermo Hollywood",
    "P065": "Las Canitas",
    "P073": "Palermo Botanico",
    "P087": "Palermo Pacifico",
    "P092": "Villa Freud",
}
LAS_TRES_MEDIDAS = ["P091", "P078", "P065"]
LAS_TRES_NUEVAS = ["P073", "P087", "P092"]


def limpia(geom):
    """buffer(0) repara autointersecciones. Sin esto GEOS devuelve areas de cero sin avisar."""
    return geom if geom.is_valid else geom.buffer(0)


def main():
    polos = gpd.read_file(BASE / "borrador_polos" / "polos_publicables.geojson").to_crs(CRS_METRICO)
    refs = gpd.read_file(BASE / "geometria_r8" / "referencias_r8.geojson").to_crs(CRS_METRICO)
    polos["geometry"] = polos.geometry.map(limpia)
    refs["geometry"] = refs.geometry.map(limpia)

    r01 = refs[refs["referencia_id"] == "R01"]
    assert len(r01) == 1, "R01 no es unica en referencias_r8"
    g_r01 = limpia(r01.geometry.iloc[0])
    ha_r01 = g_r01.area / 10_000

    # Locales de la base gastronomica, para contar por pieza igual que la ronda 10.
    #
    # EL FILTRO IMPORTA Y NO ESTABA ESCRITO EN NINGUN LADO. La base trae 27.727 locales; contar
    # los 27.727 da R01 = 1454 y no los 1358 que publicaron las rondas 9 y 10. El universo de
    # esas rondas es `anillo == nucleo` Y `apto_geometria == True`, que reproduce 1358 exacto.
    # Sin el filtro los conteos salen ~7 % altos y las areas igual coinciden, que es lo que lo
    # vuelve peligroso: la corrida parece validar y esta contando otro universo.
    locales = pd.read_csv(BASE / "base" / "local.csv", low_memory=False)
    locales = locales.dropna(subset=["lon", "lat"])
    n_bruto = len(locales)
    locales = locales[(locales["anillo"] == "nucleo") & (locales["apto_geometria"])]
    print(f"base: {n_bruto} locales con punto -> {len(locales)} tras el filtro "
          f"anillo=nucleo & apto_geometria (universo de las rondas 9 y 10)")
    pts = gpd.GeoDataFrame(
        locales,
        geometry=gpd.points_from_xy(locales["lon"], locales["lat"]),
        crs="EPSG:4326",
    ).to_crs(CRS_METRICO)

    def cuenta(geom):
        return int(pts.within(geom).sum())

    print(f"R01 Palermo: {ha_r01:,.2f} ha - {cuenta(g_r01)} locales\n")

    filas = []

    # ---- Parte 1: R01 contra cada una de las seis subzonas -------------------------------
    print("=" * 78)
    print("PARTE 1 - R01 contra las SEIS subzonas de la ficha")
    print("=" * 78)
    geoms = {}
    for pid, nombre in SUBZONAS.items():
        sub = polos[polos["polo_id"] == pid]
        if sub.empty:
            print(f"  {pid} {nombre}: NO ESTA en polos_publicables.geojson")
            filas.append(
                dict(
                    bloque="R01 x subzona", pid=pid, nombre=nombre, ha_subzona="",
                    locales_subzona="", ha_interseccion="", pct_de_la_subzona="",
                    pct_de_R01="", locales_en_la_interseccion="",
                    medida_en_ronda_9_10="si" if pid in LAS_TRES_MEDIDAS else "no",
                    observacion="ausente de la capa publicable",
                )
            )
            continue
        g = limpia(unary_union(sub.geometry.values))
        geoms[pid] = g
        inter = limpia(g_r01.intersection(g))
        ha_g, ha_i = g.area / 10_000, inter.area / 10_000
        n_g = cuenta(g)
        n_i = cuenta(inter) if not inter.is_empty else 0
        marca = "  <-- NUNCA MEDIDA" if pid in LAS_TRES_NUEVAS else ""
        print(
            f"  {pid} {nombre:<20} {ha_g:7.2f} ha {n_g:5d} loc | "
            f"R01 n {ha_i:7.2f} ha ({ha_i / ha_g * 100 if ha_g else 0:5.1f} % de la subzona, "
            f"{ha_i / ha_r01 * 100:4.1f} % de R01) {n_i:5d} loc{marca}"
        )
        filas.append(
            dict(
                bloque="R01 x subzona", pid=pid, nombre=nombre,
                ha_subzona=round(ha_g, 2), locales_subzona=n_g,
                ha_interseccion=round(ha_i, 2),
                pct_de_la_subzona=round(ha_i / ha_g * 100, 1) if ha_g else 0,
                pct_de_R01=round(ha_i / ha_r01 * 100, 1),
                locales_en_la_interseccion=n_i,
                medida_en_ronda_9_10="si" if pid in LAS_TRES_MEDIDAS else "no",
                observacion="",
            )
        )

    # ---- Parte 2: reconstruir las 8 piezas del residuo -----------------------------------
    print()
    print("=" * 78)
    print("PARTE 2 - las 8 piezas del residuo, y cada una contra las tres nuevas")
    print("=" * 78)
    union_tres = limpia(unary_union([geoms[p] for p in LAS_TRES_MEDIDAS if p in geoms]))
    residuo = limpia(g_r01.difference(union_tres))
    piezas = sorted(
        [limpia(p) for p in getattr(residuo, "geoms", [residuo]) if p.area / 10_000 >= 0.1],
        key=lambda p: p.area,
        reverse=True,
    )
    print(f"  residuo total: {residuo.area / 10_000:,.2f} ha - {cuenta(residuo)} locales - "
          f"{len(piezas)} piezas de mas de 0,1 ha\n")

    for i, pieza in enumerate(piezas, start=1):
        ha_p, n_p = pieza.area / 10_000, cuenta(pieza)
        toques = []
        for pid in LAS_TRES_NUEVAS:
            if pid not in geoms:
                continue
            inter = limpia(pieza.intersection(geoms[pid]))
            ha_i = inter.area / 10_000
            if ha_i > 0.001:
                toques.append(f"{pid} {SUBZONAS[pid]} {ha_i:.2f} ha ({ha_i / ha_p * 100:.1f} %)")
            filas.append(
                dict(
                    bloque="pieza x subzona nueva", pid=pid, nombre=SUBZONAS[pid],
                    ha_subzona=round(geoms[pid].area / 10_000, 2),
                    locales_subzona=cuenta(geoms[pid]),
                    ha_interseccion=round(ha_i, 4),
                    pct_de_la_subzona=round(ha_i / (geoms[pid].area / 10_000) * 100, 2),
                    pct_de_R01="", locales_en_la_interseccion=cuenta(inter) if ha_i > 0 else 0,
                    medida_en_ronda_9_10="no",
                    observacion=f"pieza {i} del residuo ({ha_p:.2f} ha, {n_p} locales)",
                )
            )
        print(f"  pieza {i}: {ha_p:6.2f} ha {n_p:4d} loc  ->  "
              + ("; ".join(toques) if toques else "NO TOCA NINGUNA DE LAS TRES"))

    # ---- Parte 3: quien SI esta adentro de la pieza 1 -------------------------------------
    print()
    print("=" * 78)
    print("PARTE 3 - la pieza 1: que polos del borrador caen adentro")
    print("=" * 78)
    p1 = piezas[0]
    ha_p1 = p1.area / 10_000
    print(f"  pieza 1: {ha_p1:.2f} ha - {cuenta(p1)} locales\n")
    candidatos = []
    for _, fila in polos.iterrows():
        g = limpia(fila.geometry)
        inter = limpia(p1.intersection(g))
        ha_i = inter.area / 10_000
        if ha_i > 0.05:
            candidatos.append((fila["polo_id"], g.area / 10_000, ha_i, ha_i / (g.area / 10_000) * 100,
                               ha_i / ha_p1 * 100, cuenta(inter)))
    candidatos.sort(key=lambda t: t[2], reverse=True)
    for pid, ha_g, ha_i, pct_polo, pct_pieza, n_i in candidatos:
        print(f"    {pid:<10} polo {ha_g:6.2f} ha | dentro de la pieza 1: {ha_i:6.2f} ha "
              f"({pct_polo:5.1f} % del polo, {pct_pieza:5.1f} % de la pieza) {n_i:4d} loc")
        filas.append(
            dict(
                bloque="pieza 1 x polo del borrador", pid=pid, nombre="",
                ha_subzona=round(ha_g, 2), locales_subzona=cuenta(limpia(
                    polos[polos["polo_id"] == pid].geometry.iloc[0])),
                ha_interseccion=round(ha_i, 2), pct_de_la_subzona=round(pct_polo, 1),
                pct_de_R01=round(pct_pieza, 1), locales_en_la_interseccion=n_i,
                medida_en_ronda_9_10="no", observacion="cae dentro de la pieza 1 del residuo",
            )
        )
    if not candidatos:
        print("    ningun polo del borrador cae dentro de la pieza 1")

    destino = SALIDA / "palermo_seis_subzonas.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"\nEscrito: {destino.relative_to(BASE.parent.parent)} ({len(filas)} filas)")


if __name__ == "__main__":
    main()
