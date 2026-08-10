# -*- coding: utf-8 -*-
"""Atribuir dos ejes del IDECBA que el cruce oficial marca como que no estan en el Atlas.

LOS DOS CASOS
-------------
`ronda_12/idecba_48_autoridad.csv` da los dos como "NO — candidato a evaluar con las seis vias":

    Triunvirato   Av. Triunvirato 3601-4699 · Monroe 4801-5399
                  559 relevados · 92,1 % de ocupacion · -1,3 pp · 16,44 locales por cuadra
    Avellaneda    Avellaneda 2701-3799 · Bogota 2901-3499 · Aranguren 2901-3499
                  1.073 relevados · 94,6 % · -0,2 pp · **23,33 locales por cuadra, el eje MAS
                  DENSO de los 48**

Y los dos tienen una referencia del Atlas encima:

    R17 Villa Urquiza  su perimetro declarado es "Av. Triunvirato, Av. Monroe y Plaza Echeverria"
    Z24 Flores         "el corredor de Av. Avellaneda entre Nazca y Cuenca/Bahia Blanca"

La ficha de R17 ya lo dice con todas las letras: *"Es una atribucion faltante, no un dato
faltante"*, y deja el pendiente escrito como "un cruce espacial y no una investigacion".

POR QUE NO ALCANZA CON CRUZAR NOMBRES DE CALLE
-----------------------------------------------
La ronda 13 cruzo las CALLES de los locales de cada referencia contra las calles de los tramos, y
dejo dicho el limite de ese metodo: para 12 de los 48 ejes el nombre no normaliza igual y la sonda
matchea cero locales **antes de tocar geometria**. Un negativo de un instrumento ciego no es un
negativo.

Aca los tramos se construyen como GEOMETRIA, que es lo que la ronda 13 dejo como pendiente 4: para
cada tramo se toman las cuadras del callejero oficial cuyo rango de alturas se solapa con el rango
del tramo, y se mide cuanto de esa geometria cae dentro del poligono de la referencia. **Un tramo
que no se puede construir se declara y no se cuenta**, en vez de salir como negativo.

LA REGLA, ESCRITA ANTES
------------------------
    - se atribuye si >= 50 % de los metros del eje relevado caen dentro del poligono
    - entre el 10 % y el 50 % se atribuye como PARCIAL, con el porcentaje al lado
    - por debajo del 10 % no se atribuye
    - y en los tres casos se reporta tambien el reverso: que fraccion del poligono toca el eje,
      porque un eje adentro de un poligono diez veces mas grande no lo describe

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"

AUTORIDAD = BASE / "ronda_12" / "idecba_48_autoridad.csv"
ZONAS = BASE / "geometria_r7" / "zonas_r8.geojson"

CORTE_ATRIBUIR = 0.50
CORTE_PARCIAL = 0.10

# (eje del IDECBA, referencia del Atlas, soporte, tramos como (clave canonica, desde, hasta))
CASOS = [
    {
        "eje": "Triunvirato",
        "referencia": "R17",
        "nombre_referencia": "Villa Urquiza",
        "tramos": [("TRIUNVIRATO AV", 3601, 4699), ("MONROE AV", 4801, 5399)],
    },
    {
        "eje": "Avellaneda",
        "referencia": "Z24",
        "nombre_referencia": "Flores · Avellaneda y Ruperto Godoy",
        "tramos": [("AVELLANEDA AV", 2701, 3799), ("BOGOTA", 2901, 3499),
                   ("ARANGUREN JUAN F DR", 2901, 3499)],
    },
]


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def cuadras_del_tramo(calles, clave, desde, hasta):
    """Las cuadras cuyo rango de alturas se solapa con [desde, hasta], por cualquiera de las manos.

    Se usa el solape y no la contencion: el tramo del IDECBA arranca en el 3601 y la cuadra del
    callejero puede ir del 3600 al 3698. Exigir contencion perderia las dos cuadras de las puntas.
    """
    sel = calles[calles.clave == clave]
    if sel.empty:
        return sel, "la calle NO esta en el callejero con esa clave"
    solapa = (((sel.alt_derini <= hasta) & (sel.alt_derfin >= desde) & (sel.alt_derfin > 0)) |
              ((sel.alt_izqini <= hasta) & (sel.alt_izqfin >= desde) & (sel.alt_izqfin > 0)))
    return sel[solapa], ""


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
    from polos_soporte import envolventes_22, puntos_base  # noqa: E402
    from callejero_canonico import cargar, familias  # noqa: E402

    calles = cargar()
    mapa = familias(calles)
    env = envolventes_22().set_index("referencia_id")
    zonas = gpd.read_file(ZONAS).to_crs(CRS_METRICO).set_index("zona_id")
    puntos = puntos_base()
    autoridad = pd.read_csv(AUTORIDAD)

    print("=" * 100)
    print("IDECBA · atribuir Triunvirato y Avellaneda, construyendo los tramos como geometria")
    print("=" * 100)

    filas, cambios = [], {}
    for caso in CASOS:
        rid = caso["referencia"]
        if rid in env.index:
            soporte, procedencia = limpia(env.geometry.loc[rid]), "envolvente editorial del Atlas"
        elif rid in zonas.index:
            soporte, procedencia = limpia(zonas.geometry.loc[rid]), zonas.detalle_geometria.loc[rid]
        else:
            raise SystemExit(f"{rid} no esta en ninguna capa de geometria")

        print("\n" + "-" * 100)
        print(f"EJE «{caso['eje']}»  contra  {rid} · {caso['nombre_referencia']}")
        print(f"  soporte: {soporte.area / 10_000:,.2f} ha · "
              f"{int(puntos.within(soporte).sum())} locales · {procedencia}")
        print("-" * 100)
        print(f"\n{'tramo':<34}{'cuadras':>9}{'metros':>10}{'dentro':>10}{'%':>7}"
              f"{'distancia':>12}")

        piezas, total_m, dentro_m, notas = [], 0.0, 0.0, []
        for clave, desde, hasta in caso["tramos"]:
            familia = mapa.get(clave, {clave})
            sel_familia = calles[calles.clave.isin(familia)]
            cuadras, problema = cuadras_del_tramo(sel_familia, clave, desde, hasta)
            if problema or cuadras.empty:
                # se prueba la familia entera antes de declarar el tramo irreconstruible
                cuadras = sel_familia[
                    (((sel_familia.alt_derini <= hasta) & (sel_familia.alt_derfin >= desde) &
                      (sel_familia.alt_derfin > 0)) |
                     ((sel_familia.alt_izqini <= hasta) & (sel_familia.alt_izqfin >= desde) &
                      (sel_familia.alt_izqfin > 0)))]
            etiqueta = f"{clave} {desde}-{hasta}"
            if cuadras.empty:
                print(f"{etiqueta:<34}{'NO SE PUDO CONSTRUIR — se declara y no se cuenta':>48}")
                notas.append(f"{etiqueta}: no se pudo construir")
                filas.append(dict(eje=caso["eje"], referencia=rid, tramo=etiqueta, cuadras=0,
                                  metros=0, metros_dentro=0, porcentaje="",
                                  distancia_m="", nota="tramo no construible desde el callejero"))
                continue
            geom = limpia(unary_union(list(cuadras.geometry)))
            piezas.append(geom)
            adentro = geom.intersection(soporte).length
            total_m += geom.length
            dentro_m += adentro
            d = soporte.distance(geom)
            print(f"{etiqueta:<34}{len(cuadras):>9}{geom.length:>10,.0f}{adentro:>10,.0f}"
                  f"{adentro / geom.length * 100:>6.0f}%{d:>10,.0f} m")
            filas.append(dict(
                eje=caso["eje"], referencia=rid, tramo=etiqueta, cuadras=len(cuadras),
                metros=round(geom.length), metros_dentro=round(adentro),
                porcentaje=f"{adentro / geom.length * 100:.0f}%", distancia_m=round(d),
                nota="; ".join(sorted(familia)) if len(familia) > 1 else ""))

        if not piezas:
            print("\n  el eje entero no se pudo construir: no se atribuye nada")
            continue
        eje_geom = limpia(unary_union(piezas))
        frac = dentro_m / total_m
        veredicto = ("SI" if frac >= CORTE_ATRIBUIR
                     else "parcial" if frac >= CORTE_PARCIAL else "no")
        print(f"\n  EL EJE ENTERO: {total_m:,.0f} m · {dentro_m:,.0f} m dentro · {frac:.0%}"
              f"   ->  atribucion: {veredicto}")

        # el reverso: cuanto del poligono describe el eje
        banda = eje_geom.buffer(150)
        cubre = limpia(banda.intersection(soporte)).area / soporte.area
        loc_banda = int(puntos.within(limpia(banda.intersection(soporte))).sum())
        print(f"  EL REVERSO: la banda de 150 m del eje cubre el {cubre:.0%} del poligono "
              f"({loc_banda} de {int(puntos.within(soporte).sum())} locales)")
        filas.append(dict(
            eje=caso["eje"], referencia=rid, tramo="[EL EJE ENTERO]", cuadras="",
            metros=round(total_m), metros_dentro=round(dentro_m), porcentaje=f"{frac:.0%}",
            distancia_m=round(soporte.distance(eje_geom)),
            nota=f"atribucion {veredicto}; la banda de 150 m del eje cubre el {cubre:.0%} del "
                 f"poligono y {loc_banda} de {int(puntos.within(soporte).sum())} locales"
                 + ("; " + " · ".join(notas) if notas else "")))
        if veredicto != "no":
            cambios[caso["eje"]] = (rid, caso["nombre_referencia"], veredicto, frac, cubre,
                                    loc_banda)

    # ---- se escribe en el archivo que se lee ------------------------------------------------
    #
    # La ronda 12 y la 13 dejaron escrito el mismo modo de falla dos veces: registrar el defecto no
    # lo corrige si no llega al archivo que se lee. Asi que la atribucion se aplica aca.
    print("\n" + "=" * 100)
    if not cambios:
        print("Ninguna atribucion supera el corte: el archivo no se toca.")
        return
    for eje, (rid, nombre, veredicto, frac, cubre, loc) in cambios.items():
        mascara = autoridad.eje == eje
        antes = autoridad.loc[mascara, "esta_en_el_atlas"].iloc[0]
        # el archivo ya usa «SI — ...», «parcial — R21» y «NO — ...»: se respeta esa forma
        nuevo = (f"SI — {rid} {nombre}" if veredicto == "SI"
                 else f"parcial — {rid} {nombre}")
        autoridad.loc[mascara, "esta_en_el_atlas"] = nuevo
        viejo_que = autoridad.loc[mascara, "que_es_en_el_atlas"].iloc[0]
        detalle = (f"atribuido por geometria en la ronda 14: el {frac:.0%} de los metros del eje "
                   f"cae dentro del poligono de {rid}, y la banda de 150 m del eje cubre el "
                   f"{cubre:.0%} de ese poligono")
        autoridad.loc[mascara, "que_es_en_el_atlas"] = (
            f"{viejo_que} · {detalle}" if isinstance(viejo_que, str) and viejo_que.strip()
            else detalle)
        print(f"  {eje:<14}«{antes}»")
        print(f"  {'':<14} -> «{nuevo}»")
    autoridad.to_csv(AUTORIDAD, index=False, encoding="utf-8")
    print(f"\nActualizado: {AUTORIDAD.name} ({len(cambios)} filas)")
    print("=" * 100)

    destino = SALIDA / "idecba_atribucion_triunvirato_avellaneda.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["eje", "referencia", "tramo", "cuadras", "metros",
                                           "metros_dentro", "porcentaje", "distancia_m", "nota"])
        w.writeheader()
        w.writerows(filas)
    print(f"Escrito: {destino.name} ({len(filas)} filas)")


if __name__ == "__main__":
    main()
