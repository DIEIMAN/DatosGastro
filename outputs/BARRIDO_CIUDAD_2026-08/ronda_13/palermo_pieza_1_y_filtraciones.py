# -*- coding: utf-8 -*-
"""Nombre y perimetro declarado para la pieza 1 del residuo de Palermo, y que hacer con las
piezas que se filtran a Villa Crespo, Colegiales y Chacarita.

Insumo: la pieza 1 y las 8 piezas se reconstruyen igual que en palermo_seis_subzonas.py, con el
mismo filtro de universo (anillo=nucleo & apto_geometria), que es el unico que reproduce los
1358 de R01 y los 188 del residuo.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
from collections import Counter
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

BASE = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"
LAS_TRES_MEDIDAS = ["P091", "P078", "P065"]


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def main():
    polos = gpd.read_file(BASE / "borrador_polos" / "polos_publicables.geojson").to_crs(CRS_METRICO)
    refs = gpd.read_file(BASE / "geometria_r8" / "referencias_r8.geojson").to_crs(CRS_METRICO)
    polos["geometry"] = polos.geometry.map(limpia)
    refs["geometry"] = refs.geometry.map(limpia)

    loc = pd.read_csv(BASE / "base" / "local.csv", low_memory=False).dropna(subset=["lon", "lat"])
    loc = loc[(loc["anillo"] == "nucleo") & (loc["apto_geometria"])]
    pts = gpd.GeoDataFrame(
        loc, geometry=gpd.points_from_xy(loc["lon"], loc["lat"]), crs="EPSG:4326"
    ).to_crs(CRS_METRICO)

    g_r01 = limpia(refs[refs["referencia_id"] == "R01"].geometry.iloc[0])
    union_tres = limpia(unary_union(
        [limpia(unary_union(polos[polos["polo_id"] == p].geometry.values)) for p in LAS_TRES_MEDIDAS]
    ))
    residuo = limpia(g_r01.difference(union_tres))
    piezas = sorted(
        [limpia(p) for p in getattr(residuo, "geoms", [residuo]) if p.area / 10_000 >= 0.1],
        key=lambda p: p.area, reverse=True,
    )

    filas = []

    # ---- La pieza 1: de que calles esta hecha -------------------------------------------
    print("=" * 78)
    print("PIEZA 1 - de que esta hecha")
    print("=" * 78)
    p1 = piezas[0]
    dentro = pts[pts.within(p1)]
    print(f"  {p1.area / 10_000:.2f} ha - {len(dentro)} locales\n")

    def calle(direccion):
        if not isinstance(direccion, str) or not direccion.strip():
            return None
        # "Thames 1234" -> "Thames": se corta en el primer bloque numerico.
        partes = direccion.split()
        out = []
        for t in partes:
            if t.isdigit():
                break
            out.append(t)
        return " ".join(out).strip().title() or None

    calles = Counter(c for c in dentro["direccion_norm"].map(calle) if c)
    con_dir = sum(1 for d in dentro["direccion_norm"] if isinstance(d, str) and d.strip())
    print(f"  locales con direccion: {con_dir} de {len(dentro)} "
          f"({con_dir / len(dentro) * 100:.1f} %)")
    print("  calles dominantes:")
    for nombre, n in calles.most_common(12):
        print(f"     {nombre:<32} {n:3d}")
        filas.append(dict(bloque="pieza 1 - calles", clave=nombre, valor=n, nota=""))

    minx, miny, maxx, maxy = p1.bounds
    p1_wgs = gpd.GeoSeries([p1], crs=CRS_METRICO).to_crs("EPSG:4326").iloc[0]
    wminx, wminy, wmaxx, wmaxy = p1_wgs.bounds
    print(f"\n  extension: {(maxx - minx):.0f} m E-O x {(maxy - miny):.0f} m N-S")
    print(f"  bbox WGS84: lon {wminx:.5f} a {wmaxx:.5f} - lat {wminy:.5f} a {wmaxy:.5f}")
    filas.append(dict(bloque="pieza 1 - forma", clave="extension_EO_m", valor=round(maxx - minx),
                      nota=""))
    filas.append(dict(bloque="pieza 1 - forma", clave="extension_NS_m", valor=round(maxy - miny),
                      nota=""))
    filas.append(dict(bloque="pieza 1 - forma", clave="bbox_wgs84",
                      valor=f"{wminx:.5f},{wminy:.5f},{wmaxx:.5f},{wmaxy:.5f}", nota=""))

    # Cuanto de la pieza 1 explica P090+P089, el unico polo del borrador que cae adentro.
    g90 = limpia(unary_union(polos[polos["polo_id"] == "P090+P089"].geometry.values))
    inter = limpia(p1.intersection(g90))
    n_in = int(pts.within(inter).sum())
    print(f"\n  P090+P089 'Palermo - eje Av. Santa Fe' cubre {inter.area / 10_000:.2f} ha "
          f"({inter.area / p1.area * 100:.1f} % de la pieza) y {n_in} de sus {len(dentro)} locales "
          f"({n_in / len(dentro) * 100:.1f} %)")
    resto = limpia(p1.difference(g90))
    print(f"  lo que NO cubre: {resto.area / 10_000:.2f} ha y "
          f"{int(pts.within(resto).sum())} locales")
    filas.append(dict(bloque="pieza 1 - nucleo", clave="P090+P089_ha_dentro",
                      valor=round(inter.area / 10_000, 2),
                      nota=f"{inter.area / p1.area * 100:.1f} % de la pieza"))
    filas.append(dict(bloque="pieza 1 - nucleo", clave="P090+P089_locales_dentro", valor=n_in,
                      nota=f"{n_in / len(dentro) * 100:.1f} % de los locales de la pieza"))

    # ---- Las piezas que se filtran a otros barrios ---------------------------------------
    print()
    print("=" * 78)
    print("LAS PIEZAS QUE SE FILTRAN - contra que referencia vecina caen")
    print("=" * 78)
    vecinas = {
        "R08": "Villa Crespo",
        "R09R19_CHACAGIALES": "Chacagiales (Chacarita + Lacroze + Colegiales)",
        "R21": "La Paternal",
    }
    for i, pieza in enumerate(piezas, start=1):
        dentro_p = pts[pts.within(pieza)]
        if len(dentro_p) == 0 and pieza.area / 10_000 < 1:
            continue
        barrios = Counter(dentro_p["barrio"].dropna())
        dom = barrios.most_common(1)[0] if barrios else ("sin locales", 0)
        if dom[0] == "Palermo":
            continue
        print(f"\n  pieza {i}: {pieza.area / 10_000:.2f} ha - {len(dentro_p)} locales - "
              f"dominante {dom[0]} ({dom[1]}/{len(dentro_p)})")
        for rid, nombre in vecinas.items():
            fila_ref = refs[refs["referencia_id"] == rid]
            if fila_ref.empty:
                continue
            g_v = limpia(fila_ref.geometry.iloc[0])
            inter_v = limpia(pieza.intersection(g_v))
            ha_v = inter_v.area / 10_000
            d = pieza.distance(g_v)
            marca = "SOLAPA" if ha_v > 0.001 else f"no solapa - a {d:.0f} m"
            print(f"     vs {rid:<22} {nombre:<46} {marca}"
                  + (f" ({ha_v:.2f} ha, {int(pts.within(inter_v).sum())} loc)" if ha_v > 0.001 else ""))
            filas.append(dict(
                bloque=f"pieza {i} - filtracion", clave=rid,
                valor=round(ha_v, 2) if ha_v > 0.001 else 0,
                nota=f"{nombre} - " + (f"solapa {ha_v:.2f} ha" if ha_v > 0.001
                                       else f"no solapa, a {d:.0f} m"),
            ))

    destino = SALIDA / "palermo_pieza_1_y_filtraciones.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["bloque", "clave", "valor", "nota"])
        w.writeheader()
        w.writerows(filas)
    print(f"\nEscrito: {destino.name} ({len(filas)} filas)")


if __name__ == "__main__":
    main()
