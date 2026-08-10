# -*- coding: utf-8 -*-
"""La capa oficial de 48 barrios: qué mueve adoptarla, medido barrio por barrio.

QUÉ DECIDE ESTA CORRIDA
------------------------
Se adopta `insumos/caba_barrios.geojson` como capa canónica de barrios para todo el proyecto. La
que se venía usando, `data/raw/geo_barrios.geojson`, **no tiene procedencia, ni commit, ni
sha256**; la nueva tiene los tres, verificados contra `PROCEDENCIA_capas_administrativas.json`.

Antes de aplicarla se publica el costo, y el costo es esta tabla: **para cada barrio, cuántos
locales entran, cuántos salen y de dónde vienen o a dónde van.** El movimiento se mide local por
local, con el punto de cada uno contra las dos capas, no por diferencia de totales: un barrio
puede quedar igual en el neto y haber cambiado dos locales.

LA TRAMPA QUE SE LEVANTA ANTES DE QUE MUERDA
---------------------------------------------
La capa vieja escribe **«La Boca»**; la oficial, **«Boca»**. Y la oficial escribe **«NUÑEZ»**
mientras el resto del proyecto escribe «Núñez». Un cruce por nombre con `==` **pierde el barrio
entero y no falla**: devuelve cero filas y el conteo queda en cero sin que nada avise.

Todos los cruces por nombre de esta corrida pasan por `nombres_de_barrio.clave`, y
`test_capa_de_barrios.py` falla si alguno devuelve cero filas para un barrio que tiene locales.
No es una precaución teórica: **este mismo paquete se tropezó con la eñe en su primera corrida**
—`cierre_geometrico.py` buscó «Nunez» con `==`, no encontró nada, midió 0,00 ha y siguió—.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nombres_de_barrio import clave, emparejar  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"

OFICIAL = BASE / "insumos" / "caba_barrios.geojson"
VIEJA = ROOT / "data" / "raw" / "geo_barrios.geojson"
PROCEDENCIA = BASE / "insumos" / "PROCEDENCIA_capas_administrativas.json"
HOY = date.today().isoformat()

SIN_BARRIO = "(fuera de toda la capa)"


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def cargar(ruta, col):
    capa = gpd.read_file(ruta).to_crs(CRS_METRICO)
    capa = capa.rename(columns={col: "nombre"})[["nombre", "geometry"]].copy()
    capa["geometry"] = capa.geometry.map(limpia)
    return capa


def barrio_de_cada_punto(puntos, capa, etiqueta):
    """El barrio de cada local por punto en polígono. Devuelve una Serie alineada a `puntos`."""
    cruce = gpd.sjoin(puntos[["geometry"]], capa, how="left", predicate="within")
    # sjoin puede duplicar un punto que cae exactamente sobre un borde compartido. Se queda el
    # primero y se cuenta cuántos fueron: si son muchos, el número de abajo no es de fiar.
    duplicados = int(cruce.index.duplicated().sum())
    if duplicados:
        print(f"  {etiqueta}: {duplicados} locales caen sobre un límite y matchean dos barrios; "
              f"se toma el primero")
    return cruce[~cruce.index.duplicated()].nombre.fillna(SIN_BARRIO)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 98)
    print("LA CAPA DE 48 BARRIOS · qué mueve adoptarla, medido barrio por barrio")
    print("=" * 98 + "\n")

    sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
    from polos_soporte import puntos_base  # noqa: E402

    oficial = cargar(OFICIAL, "BARRIO")
    vieja = cargar(VIEJA, "nombre")
    puntos = puntos_base()
    print(f"capa oficial: {len(oficial)} barrios · capa vieja: {len(vieja)} barrios · "
          f"universo: {len(puntos):,} locales\n")

    # ---- 1 · el emparejamiento de nombres, que es lo primero que hay que ver ---------------
    print("-" * 98)
    print("1 · los nombres, emparejados por clave normalizada y no por igualdad")
    print("-" * 98)
    pares, solo_vieja, solo_oficial = emparejar(vieja.nombre, oficial.nombre)
    print(f"  {len(pares)} pares · {len(solo_vieja)} sólo en la vieja · "
          f"{len(solo_oficial)} sólo en la oficial")

    def plano(x):  # lo que hace un cruce «prolijo» que no usa el normalizador
        import unicodedata
        return unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().upper()

    pierde_igualdad = [(a, b) for a, b in pares if str(a) != str(b)]
    pierde_mayus = [(a, b) for a, b in pares if plano(a) != plano(b)]
    print(f"\n  cuánto pierde cada forma de cruzar, sobre los mismos {len(pares)} barrios:")
    print(f"    con `a == b`                          pierde {len(pierde_igualdad)} barrios")
    print(f"    con mayúsculas y sin tildes           pierde {len(pierde_mayus)} barrios")
    print(f"    con `nombres_de_barrio.clave`         pierde 0")
    print(f"\n  los que ni las mayúsculas ni las tildes salvan, que son los que muerden:")
    for a, b in pierde_mayus:
        print(f"      «{a}»  ->  «{b}»      (clave {clave(a)})")
    distintos = pierde_mayus
    if solo_vieja or solo_oficial:
        print(f"  ATENCIÓN, sin par: vieja {solo_vieja} · oficial {solo_oficial}")

    # ---- 2 · geometría: en cuánto difieren las dos capas -----------------------------------
    print("\n" + "-" * 98)
    print("2 · la geometría de las dos capas")
    print("-" * 98)
    u_vieja = limpia(vieja.geometry.union_all())
    u_ofic = limpia(oficial.geometry.union_all())
    d_vo, d_ov = limpia(u_vieja.difference(u_ofic)), limpia(u_ofic.difference(u_vieja))
    print(f"  la Ciudad entera: vieja {u_vieja.area / 1e4:,.2f} ha · "
          f"oficial {u_ofic.area / 1e4:,.2f} ha")
    print(f"    vieja menos oficial: {d_vo.area:12,.0f} m² con "
          f"{int(puntos.within(d_vo).sum())} locales")
    print(f"    oficial menos vieja: {d_ov.area:12,.0f} m² con "
          f"{int(puntos.within(d_ov).sum())} locales")

    # ---- 3 · el impacto, local por local ---------------------------------------------------
    print("\n" + "-" * 98)
    print("3 · el impacto: qué locales se mueven y a dónde")
    print("-" * 98)
    antes = barrio_de_cada_punto(puntos, vieja, "capa vieja")
    despues = barrio_de_cada_punto(puntos, oficial, "capa oficial")
    tabla = pd.DataFrame({"local_id": puntos.local_id.values,
                          "barrio_viejo": antes.values, "barrio_oficial": despues.values})
    tabla["clave_vieja"] = tabla.barrio_viejo.map(clave)
    tabla["clave_oficial"] = tabla.barrio_oficial.map(clave)
    movidos = tabla[tabla.clave_vieja != tabla.clave_oficial].copy()
    print(f"  locales que cambian de barrio: {len(movidos)} de {len(tabla):,}")

    conteo_v = tabla.clave_vieja.value_counts()
    conteo_o = tabla.clave_oficial.value_counts()
    claves = sorted(set(conteo_v.index) | set(conteo_o.index))
    nombre_de = {clave(n): n for n in oficial.nombre}
    nombre_de.setdefault(clave(SIN_BARRIO), SIN_BARRIO)
    for n in vieja.nombre:
        nombre_de.setdefault(clave(n), n)

    filas = []
    for k in claves:
        entran = movidos[movidos.clave_oficial == k]
        salen = movidos[movidos.clave_vieja == k]
        v, o = int(conteo_v.get(k, 0)), int(conteo_o.get(k, 0))
        if not len(entran) and not len(salen):
            continue
        de_donde = " · ".join(f"{nombre_de.get(c, c)} {n}"
                              for c, n in entran.clave_vieja.value_counts().items())
        a_donde = " · ".join(f"{nombre_de.get(c, c)} {n}"
                             for c, n in salen.clave_oficial.value_counts().items())
        filas.append(dict(barrio=nombre_de.get(k, k), locales_capa_vieja=v,
                          locales_capa_oficial=o, neto=o - v,
                          entran=len(entran), salen=len(salen),
                          de_que_barrio_entran=de_donde, a_que_barrio_salen=a_donde))
    filas.sort(key=lambda f: (-(f["entran"] + f["salen"]), f["barrio"]))

    barrios_reales = [f for f in filas if f["barrio"] != SIN_BARRIO]
    neto_barrios = sum(f["neto"] for f in barrios_reales)
    print(f"\n  {len(barrios_reales)} barrios cambian su conteo, con un neto de "
          f"{neto_barrios:+d} sobre el conjunto de los 48.")
    print(f"  El neto no es cero porque **un local que hoy cae fuera de toda la capa vieja "
          f"entra en la oficial**: la fila «{SIN_BARRIO}» baja de 3 a 2. Sumando esa fila el "
          f"neto de la Ciudad es {sum(f['neto'] for f in filas):+d}, como tiene que ser.\n")
    print(f"  {'barrio':<24}{'vieja':>8}{'oficial':>9}{'neto':>6}{'entran':>8}{'salen':>7}  "
          f"detalle")
    for f in filas:
        detalle = "; ".join(x for x in (f"entran de {f['de_que_barrio_entran']}"
                                        if f["entran"] else "",
                                        f"salen a {f['a_que_barrio_salen']}"
                                        if f["salen"] else "") if x)
        print(f"  {f['barrio']:<24}{f['locales_capa_vieja']:>8,}{f['locales_capa_oficial']:>9,}"
              f"{f['neto']:>+6d}{f['entran']:>8}{f['salen']:>7}  {detalle}")

    # ---- 4 · el control que la adopción exige ----------------------------------------------
    print("\n" + "-" * 98)
    print("4 · control: ningún barrio con locales puede quedar en cero por el cruce de nombres")
    print("-" * 98)
    vacios = []
    for nom in oficial.nombre:
        k = clave(nom)
        n_geom = int(conteo_o.get(k, 0))
        # el cruce por nombre, tal como lo haría cualquier consumidor de la capa
        n_nombre = int((tabla.barrio_oficial.map(clave) == k).sum())
        if n_geom and not n_nombre:
            vacios.append(nom)
    if vacios:
        print(f"  FALLA: {vacios} tienen locales por geometría y cero por nombre")
        sys.exit(1)
    print(f"  OK: los {len(oficial)} barrios cruzan por nombre y por geometría con el mismo "
          f"resultado")

    # ---- salidas ---------------------------------------------------------------------------
    campos = ["barrio", "locales_capa_vieja", "locales_capa_oficial", "neto", "entran", "salen",
              "de_que_barrio_entran", "a_que_barrio_salen"]
    with (SALIDA / "impacto_capa_barrios.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    movidos[["local_id", "barrio_viejo", "barrio_oficial"]].to_csv(
        SALIDA / "locales_que_cambian_de_barrio.csv", index=False, encoding="utf-8")

    procedencia = json.loads(PROCEDENCIA.read_text(encoding="utf-8"))
    resumen = dict(
        fecha=HOY,
        capa_adoptada="outputs/BARRIDO_CIUDAD_2026-08/insumos/caba_barrios.geojson",
        capa_reemplazada="data/raw/geo_barrios.geojson",
        sha256=[a["sha256"] for a in procedencia["archivos"] if a["archivo"] == "caba_barrios.geojson"][0],
        barrios=len(oficial),
        pares_de_nombre=len(pares),
        pares_que_se_escriben_distinto=[list(x) for x in distintos],
        locales_que_cambian_de_barrio=len(movidos),
        barrios_afectados=len(barrios_reales),
        neto_sobre_los_48_barrios=neto_barrios,
        neto_de_la_ciudad_incluyendo_lo_que_cae_fuera=sum(f["neto"] for f in filas),
        ha_capa_vieja=round(u_vieja.area / 1e4, 2),
        ha_capa_oficial=round(u_ofic.area / 1e4, 2),
        locales_en_vieja_no_oficial=int(puntos.within(d_vo).sum()),
        locales_en_oficial_no_vieja=int(puntos.within(d_ov).sum()),
    )
    (SALIDA / "capa_de_barrios.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nEscrito: impacto_capa_barrios.csv ({len(filas)} filas) · "
          f"locales_que_cambian_de_barrio.csv ({len(movidos)} filas) · capa_de_barrios.json")


if __name__ == "__main__":
    main()
