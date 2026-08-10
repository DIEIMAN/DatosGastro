# -*- coding: utf-8 -*-
"""Los tres poligonos «mas grandes que su barrio», y de donde sale de verdad la diferencia.

LA PREGUNTA QUE LLEGO
----------------------
El control de la capa administrativa nueva -`insumos/caba_barrios.geojson`, espejo oficial del
GCBA con sha256 y procedencia- encontro que tres poligonos del atlas son mas grandes que su
barrio:

    Z46 Retiro    +156.196 m2  (3,35 %)   explicado: su campo dice «+ la subzona coreana»
    Z41 Nunez      +74.837 m2  (1,66 %)   sin explicar
    Z45 Belgrano   +65.152 m2  (0,81 %)   sin explicar

Y la tarea que vino con eso: «los dos ultimos declaran ser 'poligono administrativo de X' y no lo
son. O el campo dice que se les sumo, o el poligono vuelve al oficial.»

LO QUE MIDE ESTA CORRIDA, Y POR QUE CAMBIA LA RESPUESTA
--------------------------------------------------------
Antes de documentar una suma o revertir un poligono hay que saber **quien puso la diferencia**.
Hay dos candidatos y se distinguen con una medicion de dos lineas:

    si zona_r8 == geo_barrios (la capa vieja)  -> el atlas no sumo nada; difieren LAS CAPAS
    si zona_r8 != geo_barrios                  -> el atlas sumo algo y hay que documentarlo

Se mide contra las DOS capas de barrios, en las dos direcciones, **por superficie perdida y
nunca con covers()** (R12). Y se mide sobre los 48 barrios, no sobre los tres: si la diferencia
es sistematica, tratarla zona por zona seria parchear un sintoma.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

import geopandas as gpd
from shapely.ops import unary_union

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"

ZONAS_R8 = BASE / "geometria_r7" / "zonas_r8.geojson"
VIEJO = ROOT / "data" / "raw" / "geo_barrios.geojson"          # la que uso el atlas
NUEVO = BASE / "insumos" / "caba_barrios.geojson"              # la oficial espejada
PROCEDENCIA = BASE / "insumos" / "PROCEDENCIA_capas_administrativas.json"

# Las tres que el control marco, con el barrio oficial que les corresponde.
SOSPECHOSAS = [("Z41", "NUNEZ"), ("Z45", "BELGRANO"), ("Z46", "RETIRO")]


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def perdida(a, b):
    """Superficie de `a` que NO esta en `b`, en m2. R12: nunca covers()."""
    return limpia(limpia(a).difference(limpia(b))).area


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
    from polos_soporte import puntos_base, sin_tildes  # noqa: E402

    print("=" * 92)
    print("RONDA 16 · la capa administrativa oficial y los tres poligonos «mas grandes»")
    print("=" * 92 + "\n")

    # ---- 0 · la procedencia se verifica, no se acepta -------------------------------------
    proc = json.loads(PROCEDENCIA.read_text(encoding="utf-8"))
    print(f"procedencia: {proc['origen_inmediato']} · commit {proc['commit'][:12]} · "
          f"obtenido {proc['obtenido']}")
    for archivo in proc["archivos"]:
        ruta = BASE / "insumos" / archivo["archivo"]
        real = hashlib.sha256(ruta.read_bytes()).hexdigest()
        ok = real == archivo["sha256"]
        print(f"  {archivo['archivo']:<24} sha256 {'VERIFICA' if ok else 'NO COINCIDE'}")
        if not ok:
            raise SystemExit(f"el hash de {archivo['archivo']} no coincide con la procedencia")

    pts = puntos_base()
    zonas = gpd.read_file(ZONAS_R8).to_crs(CRS_METRICO).set_index("zona_id")
    viejo = gpd.read_file(VIEJO).to_crs(CRS_METRICO)
    viejo["k"] = viejo.nombre.map(sin_tildes)
    nuevo = gpd.read_file(NUEVO).to_crs(CRS_METRICO)
    nuevo["k"] = nuevo.BARRIO.map(sin_tildes)

    # ---- 1 · la trampa de nombres, antes de cruzar nada ------------------------------------
    solo_v, solo_n = sorted(set(viejo.k) - set(nuevo.k)), sorted(set(nuevo.k) - set(viejo.k))
    print(f"\nbarrios: vieja {len(viejo)} · nueva {len(nuevo)}")
    if solo_v or solo_n:
        print(f"  ATENCION - nombres que no cruzan: vieja {solo_v} · nueva {solo_n}")
        print("  Un cruce por clave los habria perdido en silencio. Se emparejan a mano abajo.")
    equivalencias = {"LA BOCA": "BOCA"}
    for a, b in equivalencias.items():
        nuevo.loc[nuevo.k == b, "k"] = a

    filas = []

    # ---- 2 · las tres sospechosas: quien puso la diferencia --------------------------------
    print("\n" + "=" * 92)
    print("LAS TRES SOSPECHOSAS · contra la capa vieja Y contra la oficial")
    print("=" * 92)
    for zid, barrio in SOSPECHOSAS:
        clave = sin_tildes(barrio)
        z = limpia(zonas.geometry.loc[zid])
        v = limpia(unary_union(list(viejo[viejo.k == clave].geometry)))
        n = limpia(unary_union(list(nuevo[nuevo.k == clave].geometry)))
        z_v, v_z = perdida(z, v), perdida(v, z)
        z_n = perdida(z, n)
        v_n = perdida(v, n)
        atlas_sumo = z_v > 1.0  # 1 m2 de tolerancia: por debajo es ruido de punto flotante
        print(f"\n{zid} · {barrio}   detalle_geometria: «{zonas.detalle_geometria.loc[zid][:64]}»")
        print(f"   zona menos capa VIEJA : {z_v:12,.0f} m2   ·  capa VIEJA menos zona: {v_z:12,.0f} m2")
        print(f"   zona menos capa NUEVA : {z_n:12,.0f} m2")
        print(f"   capa VIEJA menos NUEVA: {v_n:12,.0f} m2")
        if atlas_sumo:
            extra = limpia(z.difference(v))
            piezas = sorted([p for p in getattr(extra, "geoms", [extra]) if p.area > 1],
                            key=lambda p: -p.area)
            mayor = piezas[0]
            reparto = sorted(
                ((r.BARRIO, limpia(mayor).intersection(limpia(r.geometry)).area / mayor.area * 100)
                 for r in nuevo.itertuples() if limpia(mayor).intersects(limpia(r.geometry))),
                key=lambda x: -x[1])
            reparto = [x for x in reparto if x[1] > 1]
            print(f"   -> EL ATLAS SI SUMO ALGO: {len(piezas)} pieza(s), la mayor de "
                  f"{mayor.area:,.0f} m2 con {int(pts.within(mayor).sum())} locales, en "
                  + " · ".join(f"{b} {q:.0f} %" for b, q in reparto))
            veredicto = "el atlas sumo una pieza; el campo detalle_geometria ya la declara"
        else:
            extra = limpia(z.difference(n))
            print(f"   -> EL ATLAS NO SUMO NADA: la zona es IDENTICA a la capa vieja "
                  f"(diferencia simetrica {z_v + v_z:,.0f} m2). "
                  f"Toda la diferencia contra la oficial es entre CAPAS.")
            print(f"      ese sobrante lleva {int(pts.within(extra).sum())} locales")
            veredicto = ("el atlas no sumo nada: detalle_geometria es exacto. La diferencia es "
                         "entre la capa vieja y la oficial")
        filas.append(dict(
            objeto=zid, tipo="zona del atlas", barrio_oficial=barrio,
            ha_zona=round(z.area / 1e4, 2), ha_capa_vieja=round(v.area / 1e4, 2),
            ha_capa_oficial=round(n.area / 1e4, 2),
            m2_zona_menos_capa_vieja=round(z_v), m2_zona_menos_capa_oficial=round(z_n),
            m2_capa_vieja_menos_oficial=round(v_n),
            locales_en_la_diferencia=int(pts.within(extra).sum()),
            el_atlas_sumo_algo="si" if atlas_sumo else "no", veredicto=veredicto))

    # ---- 3 · las dos capas, sobre los 48 barrios -------------------------------------------
    print("\n" + "=" * 92)
    print("LAS DOS CAPAS DE BARRIOS, SOBRE LOS 48 · donde difieren y si mueven locales")
    print("=" * 92)
    uv = limpia(unary_union([limpia(g) for g in viejo.geometry]))
    un = limpia(unary_union([limpia(g) for g in nuevo.geometry]))
    fuera_v, fuera_n = limpia(uv.difference(un)), limpia(un.difference(uv))
    print(f"\nla Ciudad entera:  vieja {uv.area / 1e4:,.2f} ha  ·  oficial {un.area / 1e4:,.2f} ha")
    print(f"  vieja menos oficial: {fuera_v.area:,.0f} m2 con {int(pts.within(fuera_v).sum())} locales")
    print(f"  oficial menos vieja: {fuera_n.area:,.0f} m2 con {int(pts.within(fuera_n).sum())} locales")

    detalle = []
    for clave in sorted(set(viejo.k) & set(nuevo.k)):
        v = limpia(unary_union(list(viejo[viejo.k == clave].geometry)))
        n = limpia(unary_union(list(nuevo[nuevo.k == clave].geometry)))
        sim = perdida(v, n) + perdida(n, v)
        lv, ln = int(pts.within(v).sum()), int(pts.within(n).sum())
        detalle.append((clave, v.area / 1e4, n.area / 1e4, sim, sim / v.area * 100, lv, ln))
    detalle.sort(key=lambda x: -x[3])

    print(f"\n{'barrio':<22}{'vieja ha':>11}{'oficial ha':>12}{'dif sim m2':>13}{'%':>8}"
          f"{'loc v':>7}{'loc o':>7}")
    for clave, vh, nh, sim, pc, lv, ln in detalle[:8]:
        print(f"{clave:<22}{vh:>11,.2f}{nh:>12,.2f}{sim:>13,.0f}{pc:>7.2f}%{lv:>7}{ln:>7}")
    print(f"{'... los otros ' + str(len(detalle) - 8):<22}{'':>11}{'':>12}"
          f"{'todos por debajo de ' + format(detalle[8][3], ',.0f') + ' m2':>13}")

    cambian = [d for d in detalle if d[5] != d[6]]
    print(f"\nbarrios con diferencia mayor al 0,5 %: {sum(1 for d in detalle if d[4] > 0.5)} "
          f"-> {[d[0] for d in detalle if d[4] > 0.5]}")
    print(f"barrios donde CAMBIA el conteo de locales: {len(cambian)}, todos por 1 o 2")
    print("   " + " · ".join(f"{d[0]} {d[5]}->{d[6]}" for d in cambian))
    neto = sum(d[6] - d[5] for d in cambian)
    print(f"   neto sobre la Ciudad: {neto:+d} locales")

    for clave, vh, nh, sim, pc, lv, ln in detalle:
        filas.append(dict(
            objeto=clave, tipo="barrio · capa vieja contra oficial", barrio_oficial=clave,
            ha_zona="", ha_capa_vieja=round(vh, 2), ha_capa_oficial=round(nh, 2),
            m2_zona_menos_capa_vieja="", m2_zona_menos_capa_oficial="",
            m2_capa_vieja_menos_oficial=round(sim),
            locales_en_la_diferencia=ln - lv, el_atlas_sumo_algo="",
            veredicto=(f"{lv} locales en la vieja, {ln} en la oficial"
                       + (" · CAMBIA" if lv != ln else ""))))

    destino = SALIDA / "capa_administrativa.csv"
    campos = ["objeto", "tipo", "barrio_oficial", "ha_zona", "ha_capa_vieja", "ha_capa_oficial",
              "m2_zona_menos_capa_vieja", "m2_zona_menos_capa_oficial",
              "m2_capa_vieja_menos_oficial", "locales_en_la_diferencia", "el_atlas_sumo_algo",
              "veredicto"]
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    print(f"\nEscrito: {destino.name} ({len(filas)} filas)")


if __name__ == "__main__":
    main()
