# -*- coding: utf-8 -*-
"""El perimetro EN CALLES de la pieza 1 del residuo de Palermo.

Diego dejo la firma del nombre condicionada a esto: "NO se pide la firma hasta que el repositorio
mida el perimetro en calles sobre la caja -58.43404,-34.59232 a -58.42101,-34.58240. Proponer
perimetros sin medir ya fallo dos veces."

Los dos fallos que cita, para no repetirlos:
  - la propuesta de perimetro de Colegiales resulto imposible: Av. Alvarez Thomas y Av. Forest se
    tocan a 0 m, asi que no podian ser dos lados de nada.
  - los ejes de Mataderos y Liniers que se citaban estaban mal, y el enclave de Liniers estaba
    900 numeros al oeste.

El metodo, entonces, no propone calles: las MIDE. Para cada calle del callejero que toca la pieza,
se calcula cuanto de esa calle cae adentro y a que distancia corre del borde. Una calle solo puede
ser lado del perimetro si corre POR el borde, no si lo cruza.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

BASE = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"
LAS_TRES = ["P091", "P078", "P065"]


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def main():
    polos = gpd.read_file(BASE / "borrador_polos" / "polos_publicables.geojson").to_crs(CRS_METRICO)
    refs = gpd.read_file(BASE / "geometria_r8" / "referencias_r8.geojson").to_crs(CRS_METRICO)
    polos["geometry"] = polos.geometry.map(limpia)
    refs["geometry"] = refs.geometry.map(limpia)

    g_r01 = limpia(refs[refs["referencia_id"] == "R01"].geometry.iloc[0])
    union = limpia(unary_union(
        [limpia(unary_union(polos[polos["polo_id"] == p].geometry.values)) for p in LAS_TRES]))
    residuo = limpia(g_r01.difference(union))
    piezas = sorted([limpia(p) for p in getattr(residuo, "geoms", [residuo])
                     if p.area / 10_000 >= 0.1], key=lambda p: p.area, reverse=True)
    p1 = piezas[0]
    borde = p1.boundary
    print(f"pieza 1: {p1.area / 10_000:.2f} ha - perimetro {borde.length:,.0f} m")

    # Se usa el callejero del proyecto y su nombre canonico, no una capa propia. `nomoficial`
    # parte la misma calle en varios registros a lo largo del eje -es lo que produjo los tres
    # bichos que documenta callejero_canonico.py-, asi que se agrupa por la raiz de esa funcion.
    import sys

    sys.path.insert(0, str(BASE.parents[1] / "scripts" / "barrido_ciudad"))
    from callejero_canonico import raiz  # noqa: E402
    from polos_soporte import CALLEJERO  # noqa: E402

    print(f"callejero: {CALLEJERO.name}")
    calles = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    calles["_canon"] = calles["nomoficial"].map(lambda n: raiz(n) if isinstance(n, str) else "")
    col = "_canon"
    print(f"   {len(calles)} tramos, agrupados por raiz canonica")

    cerca = calles[calles.geometry.intersects(p1.buffer(60))].copy()
    print(f"   {len(cerca)} tramos a menos de 60 m de la pieza\n")

    filas = []
    for nombre, grupo in cerca.groupby(col):
        geom = limpia(unary_union(grupo.geometry.values))
        dentro = geom.intersection(p1)
        m_dentro = dentro.length
        # Cuanto de la calle corre pegado al borde (a menos de 15 m): eso es ser un LADO.
        sobre_borde = geom.intersection(borde.buffer(15)).length
        if m_dentro < 20 and sobre_borde < 20:
            continue
        cruza = m_dentro > 60 and sobre_borde < m_dentro * 0.4
        filas.append(dict(
            calle=nombre,
            metros_dentro_de_la_pieza=round(m_dentro),
            metros_sobre_el_borde=round(sobre_borde),
            rol=("LADO DEL PERIMETRO" if sobre_borde >= 80 and not cruza
                 else "cruza la pieza" if cruza else "toca"),
        ))
    filas.sort(key=lambda f: -f["metros_sobre_el_borde"])

    print(f"{'calle':<38}{'m dentro':>10}{'m sobre el borde':>18}   rol")
    for f in filas[:28]:
        print(f"{str(f['calle'])[:37]:<38}{f['metros_dentro_de_la_pieza']:>10}"
              f"{f['metros_sobre_el_borde']:>18}   {f['rol']}")

    lados = [f for f in filas if f["rol"] == "LADO DEL PERIMETRO"]
    print(f"\nCALLES QUE PUEDEN SER LADO DEL PERIMETRO: {len(lados)}")
    for f in lados:
        print(f"   {f['calle']} - {f['metros_sobre_el_borde']} m sobre el borde")

    # ---- La prueba directa del nombre propuesto ------------------------------------------
    #
    # El nombre en danza es "Palermo - eje Av. Santa Fe", heredado de P090+P089. Antes de firmarlo
    # hay que preguntarle a la geometria si la pieza 1 tiene algo que ver con Av. Santa Fe.
    print()
    print("=" * 78)
    print("PRUEBA DEL NOMBRE PROPUESTO - la pieza 1 contra Av. Santa Fe")
    print("=" * 78)
    sf = calles[calles["_canon"] == "SANTA FE"]
    g_sf = limpia(unary_union(sf.geometry.values))
    g90 = limpia(unary_union(polos[polos["polo_id"] == "P090+P089"].geometry.values))
    d_p1 = p1.distance(g_sf)
    m_p1 = g_sf.intersection(p1).length
    m_90 = g_sf.intersection(g90).length
    print(f"   Av. Santa Fe DENTRO de la pieza 1 : {m_p1:,.0f} m")
    print(f"   distancia de la pieza 1 a Santa Fe: {d_p1:,.0f} m")
    print(f"   Av. Santa Fe dentro de P090+P089  : {m_90:,.0f} m  (distancia 0 m)")
    for clave, valor, nota in [
        ("perimetro_total_m", round(borde.length), "de la pieza 1"),
        ("m_de_perimetro_sobre_alguna_calle", sum(f["metros_sobre_el_borde"] for f in lados),
         f"{sum(f['metros_sobre_el_borde'] for f in lados) / borde.length * 100:.0f} % del total"),
        ("santa_fe_dentro_de_la_pieza_1_m", round(m_p1), "cero"),
        ("distancia_pieza_1_a_santa_fe_m", round(d_p1), "no la toca"),
        ("santa_fe_dentro_de_P090_P089_m", round(m_90), "el nombre viene de aca"),
    ]:
        filas.append(dict(calle=f"[{clave}]", metros_dentro_de_la_pieza=valor,
                          metros_sobre_el_borde="", rol=nota))

    destino = SALIDA / "palermo_pieza_1_perimetro.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["calle", "metros_dentro_de_la_pieza",
                                           "metros_sobre_el_borde", "rol"])
        w.writeheader()
        w.writerows(filas)
    print(f"\nEscrito: {destino.name} ({len(filas)} filas)")


if __name__ == "__main__":
    main()
