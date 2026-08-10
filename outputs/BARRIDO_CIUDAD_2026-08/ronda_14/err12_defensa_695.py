# -*- coding: utf-8 -*-
"""ERR-12 · una direccion asignada a dos establecimientos: Defensa 695.

EL CONFLICTO
------------
  catalogo_90_estado_final.csv   fila 17   BAR SEDDON      Defensa 695     Monserrat
  ronda_13/verificaciones_...    fila R11  BAR BRITANICO   "Defensa 695 esq. Brasil 399"

Dos establecimientos no comparten una puerta. Y la segunda direccion ademas es internamente
inconsistente: dice una altura y una esquina que no pueden ser la misma.

COMO SE RESUELVE, Y POR QUE ASI
-------------------------------
No se resuelve por memoria ni por busqueda: se resuelve con las dos fuentes que el proyecto ya
tiene en disco y que son las que corresponden.

  1. `bares_notables_caba.geojson` — Wikidata (CC0) con geocodificacion USIG del GCBA. Trae la
     direccion declarada, la direccion NORMALIZADA POR USIG y el punto. Es la fuente que el
     proyecto ya usa como catalogo de Notables.
  2. `callejero_gcba_2026_06_02.geojson` — el callejero oficial, cuadra por cuadra, con los rangos
     de altura par e impar de cada cuadra. Es lo que permite preguntarle a la Ciudad, sin salir del
     disco, DONDE cae la altura 695 de Defensa y en que altura de Defensa cruza Brasil.

La prueba de la esquina no se toma de ninguna descripcion: se calcula. Para cada cuadra de Defensa
se buscan las calles del callejero que tocan sus dos extremos —esas son sus esquinas—, y se mira
en que cuadra de Defensa cae la altura declarada.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import sys
from pathlib import Path

import geopandas as gpd
from shapely.ops import unary_union

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"

NOTABLES = BASE / "dataset_bares_notables" / "bares_notables_caba.geojson"
REFERENCIAS = BASE / "geometria_r8" / "referencias_r8.geojson"
ZONAS = BASE / "geometria_r7" / "zonas_r8.geojson"

# Radio para decidir que una calle "toca" el extremo de una cuadra. Una esquina real es un vertice
# compartido; 25 m es el ancho de una avenida y es el mismo umbral de contacto que ya usa
# callejero_canonico.CONTACTO_M.
ESQUINA_M = 25.0


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def cuadras_de(callejero, raiz_calle, raiz_fn):
    return callejero[callejero["_canon"] == raiz_calle].copy()


def esquinas_de(cuadra, callejero, raiz_calle):
    """Los nombres de las calles que tocan los extremos de esta cuadra."""
    coords = list(cuadra.geometry.coords)
    from shapely.geometry import Point
    extremos = [Point(coords[0]), Point(coords[-1])]
    salida = []
    for punto in extremos:
        cerca = callejero[callejero.geometry.distance(punto) <= ESQUINA_M]
        nombres = sorted({n for n in cerca["_canon"] if n and n != raiz_calle})
        salida.append(nombres)
    return salida


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
    from callejero_canonico import raiz  # noqa: E402
    from polos_soporte import CALLEJERO  # noqa: E402

    print("=" * 84)
    print("ERR-12 · Defensa 695 · quien esta en esa puerta")
    print("=" * 84)

    # ---- 1 · lo que dice el catalogo con geocodificacion USIG ----------------------------
    notables = gpd.read_file(NOTABLES)
    pares = {}
    for clave, patron in [("Britanico", "Brit"), ("Seddon", "Seddon")]:
        fila = notables[notables["nombre"].str.contains(patron, case=False, na=False)]
        if len(fila) != 1:
            raise SystemExit(f"{clave}: {len(fila)} filas en el catalogo de Notables")
        pares[clave] = fila.iloc[0]

    print("\nLo que dice Wikidata + normalizador USIG del GCBA:\n")
    print(f"{'establecimiento':<16}{'declarada':<16}{'USIG normalizada':<26}{'barrio':<12}comuna")
    for clave, f in pares.items():
        print(f"{f['nombre'][:15]:<16}{str(f['direccion_declarada'])[:15]:<16}"
              f"{str(f['direccion_normalizada'])[:25]:<26}{str(f['barrio'])[:11]:<12}"
              f"{f['comuna']:.0f}")

    puntos = gpd.GeoDataFrame(
        {"clave": list(pares)}, geometry=[pares[k].geometry for k in pares],
        crs="EPSG:4326").to_crs(CRS_METRICO)
    d = puntos.geometry.iloc[0].distance(puntos.geometry.iloc[1])
    print(f"\nDistancia entre los dos puntos USIG: {d:,.0f} m")

    # ---- 2 · el callejero oficial, cuadra por cuadra -------------------------------------
    calles = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    calles["_canon"] = calles["nomoficial"].map(lambda n: raiz(n) if isinstance(n, str) else "")
    defensa = cuadras_de(calles, "DEFENSA", raiz).sort_values("alt_derini")
    print(f"\nDefensa en el callejero oficial: {len(defensa)} cuadras\n")

    g_brasil = limpia(unary_union(list(calles[calles["_canon"] == "BRASIL"].geometry)))
    filas = []
    print(f"{'cuadra (impar)':<18}{'barrio':<12}{'esquinas':<46}{'a Brasil'}")
    for cuadra in defensa.itertuples():
        esq = esquinas_de(cuadra, calles, "DEFENSA")
        etiqueta = " / ".join(" + ".join(e) if e else "(sin cruce)" for e in esq)
        dist_brasil = cuadra.geometry.distance(g_brasil)
        rango = f"{cuadra.alt_derini:.0f}-{cuadra.alt_derfin:.0f}"
        marca = ""
        if cuadra.alt_derini <= 695 <= cuadra.alt_derfin:
            marca = "  <<< la altura 695"
        if dist_brasil <= ESQUINA_M:
            marca += "  <<< aca cruza BRASIL"
        print(f"{rango:<18}{str(cuadra.barrio)[:11]:<12}{etiqueta[:45]:<46}"
              f"{dist_brasil:>7,.0f} m{marca}")
        filas.append(dict(
            objeto=f"Defensa {rango}", barrio=cuadra.barrio, esquinas=etiqueta,
            distancia_a_brasil_m=round(dist_brasil), contiene_695=marca.startswith("  <<< la"),
            cruza_brasil=dist_brasil <= ESQUINA_M))

    la_695 = [f for f in filas if f["contiene_695"]]
    la_brasil = [f for f in filas if f["cruza_brasil"]]
    print()
    for etiqueta, grupo in [("La altura 695 de Defensa cae en", la_695),
                            ("Brasil cruza Defensa en", la_brasil)]:
        for f in grupo:
            print(f"{etiqueta}: {f['objeto']}, {f['barrio']}, esquina {f['esquinas']}")

    # ---- 2b · a que cuadra de Defensa esta pegado cada punto -----------------------------
    #
    # No alcanza con saber donde cruza Brasil: hay que ver si el punto que USIG geocodifico esta
    # efectivamente ahi. Si el Britanico estuviera en la altura 695 su punto caeria pegado a la
    # cuadra 601-695, y no lo esta.
    print("\nDistancia de cada punto a cada cuadra de Defensa (las mas cercanas):\n")
    for clave, punto in zip(puntos["clave"], puntos.geometry):
        cercanas = sorted(
            ((cuadra.geometry.distance(punto), f"{cuadra.alt_derini:.0f}-{cuadra.alt_derfin:.0f}")
             for cuadra in defensa.itertuples()), key=lambda t: t[0])[:3]
        detalle = " · ".join(f"Defensa {rango}: {dist:,.0f} m" for dist, rango in cercanas)
        print(f"  {clave:<12} {detalle}")
        filas.append(dict(
            objeto=f"[cuadra mas cercana] {clave}", barrio="", esquinas=detalle,
            distancia_a_brasil_m=round(punto.distance(g_brasil)), contiene_695="",
            cruza_brasil=""))

    # ---- 3 · donde cae cada punto, contra la geometria publicada -------------------------
    refs = gpd.read_file(REFERENCIAS).to_crs(CRS_METRICO)
    zonas = gpd.read_file(ZONAS).to_crs(CRS_METRICO)
    refs["geometry"] = refs.geometry.map(limpia)
    zonas["geometry"] = zonas.geometry.map(limpia)
    print("\nDonde cae cada punto en la geometria publicada:\n")
    for clave, punto in zip(puntos["clave"], puntos.geometry):
        dentro_r = refs[refs.geometry.contains(punto)]["referencia_id"].tolist()
        dentro_z = zonas[zonas.geometry.contains(punto)]["zona_id"].tolist()
        r11 = limpia(refs[refs.referencia_id == "R11"].geometry.iloc[0])
        print(f"  {clave:<12} referencias: {dentro_r or '(ninguna)'}   "
              f"zonas: {dentro_z or '(ninguna)'}   distancia a R11: {punto.distance(r11):,.0f} m")
        filas.append(dict(
            objeto=f"[punto USIG] {clave}", barrio="",
            esquinas=f"referencias {dentro_r or 'ninguna'} · zonas {dentro_z or 'ninguna'}",
            distancia_a_brasil_m=round(punto.distance(r11)), contiene_695="",
            cruza_brasil="distancia a R11 en la columna de metros"))

    destino = SALIDA / "err12_defensa_695.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["objeto", "barrio", "esquinas",
                                           "distancia_a_brasil_m", "contiene_695", "cruza_brasil"])
        w.writeheader()
        w.writerows(filas)
    print(f"\nEscrito: {destino.name} ({len(filas)} filas)")


if __name__ == "__main__":
    main()
