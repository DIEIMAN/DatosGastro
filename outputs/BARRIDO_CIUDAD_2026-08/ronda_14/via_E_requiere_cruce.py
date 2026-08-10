# -*- coding: utf-8 -*-
"""Los 10 `requiere_cruce` de la via E, resueltos por cruce espacial.

QUE SON LOS 10
--------------
La via E se mide por ZONA y las filas la heredan. Diez de las 94 no pueden heredar porque su
soporte cae en un barrio que tiene mas de una zona y las zonas no coinciden en el veredicto:

    7 en Flores     Z23 casco historico (no abre) · Z24 Avellaneda-Ruperto Godoy (abre, 6 grupos)
                    · Z39 Parque Avellaneda / Flores sur, incluye Baek-ku (abre, 2)
    3 en Balvanera  Z35 Once (no abre) · Z36 Congreso (abre, 2)

No es investigacion: la zona ya tiene veredicto. Lo unico que falta es decir en cual de ellas cae
cada poligono.

LA REGLA, ESCRITA ANTES DE CORRER
----------------------------------
    1. Se mide la fraccion del AREA del poligono del polo dentro de cada zona candidata.
    2. Si una zona con veredicto propio de via E se lleva >= 50 %, la fila hereda ese veredicto.
       El 50 % es la convencion "mas de la mitad, pertenece" que ya usa la via A.
    3. Si la unica que la contiene es Z23, la herencia se marca aparte. **Z23 no es una
       delimitacion: es un residuo** —"el barrio de Flores menos Z24 y Z39b"— y por lo tanto se
       traga Bajo Flores, cuya via E la ronda 2 le atribuyo a Z39. Heredar de un residuo es
       heredar de "lo que sobro", que no es lo mismo que pertenecer a una zona.
    4. Si ninguna llega al 50 %, la fila NO se resuelve y se dice por que. No se reparte.

Y una prediccion, escrita antes: **las tres de Balvanera no se pueden cerrar por cruce.** Z36
Congreso no tiene poligono —la ronda 8 la fusiono en Z47 Monserrat + Congreso, y el poligono de
Z47 es el barrio de Monserrat—, asi que dentro de Balvanera no hay nada contra que cruzar. Si eso
se confirma, la via E sube por las 7 de Flores y no por las 10.

LAS DOS REGLAS QUE SE AGREGARON DESPUES DE LA PRIMERA PASADA, Y POR QUE
------------------------------------------------------------------------
La primera pasada, con las reglas 1 a 4, cerro 9 de 10. **Dos de esas nueve estaban mal, y las dos
por la misma causa: el poligono de la zona candidata no era una delimitacion.**

    5. Una zona cuyo poligono ES EL BARRIO ENTERO no puede resolver una ambiguedad DENTRO de ese
       barrio. Z35 "Balvanera · Once" mide 434,43 ha, que es exactamente el barrio de Balvanera.
       Decir que un polo de Balvanera "cae en Z35" es decir que cae en Balvanera: no discrimina
       nada frente a Z36 Congreso, que es la otra mitad de la pregunta. La primera pasada le dio
       Z35 a P107 y a P055 con 82,5 % y 100 % de contencion, y los dos numeros son ciertos y no
       significan nada.

    6. Un soporte que CONTIENE a varias zonas candidatas no hereda de ninguna. PGF2_FLORES es el
       barrio de Flores entero: adentro tiene a Z23, a Z24 y a Z39b. Heredar la via E de Z23
       porque se lleva el 94 % del area seria atribuirle al todo lo de una parte — que es
       literalmente la regla "la herencia no vale hacia arriba" de
       `CRITERIO_ESCALA_DE_LAS_VIAS.md`, leida al reves.

Las dos reglas se escriben aca en vez de corregir el resultado en silencio.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"

VIA_E_94 = BASE / "desde_cowork" / "evidencia_2026" / "via_E_94_filas.csv"
SEIS_VIAS_ZONAS = BASE / "desde_cowork" / "evidencia_2026" / "seis_vias_ronda_2.csv"
ZONAS = BASE / "geometria_r7" / "zonas_r8.geojson"

PERTENENCIA_MIN = 0.50
CANDIDATAS = {
    "Flores": ["Z23", "Z24", "Z39", "Z39b"],
    "Balvanera": ["Z35", "Z47"],
}
RESIDUOS = {"Z23"}
# Regla 5: zonas cuyo poligono es el barrio entero. No discriminan dentro de su propio barrio.
POLIGONO_ES_EL_BARRIO = {"Z35": "Balvanera", "Z39": "Parque Avellaneda", "Z47": "Monserrat"}


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
    from polos_soporte import soportes_94  # noqa: E402

    via_e = pd.read_csv(VIA_E_94)
    pendientes = via_e[via_e["modo"] == "requiere_cruce"].copy()
    zonas = gpd.read_file(ZONAS).to_crs(CRS_METRICO).set_index("zona_id")
    zonas["geometry"] = zonas.geometry.map(limpia)
    veredictos = pd.read_csv(SEIS_VIAS_ZONAS).set_index("zona_id")

    print("=" * 100)
    print("LOS 10 requiere_cruce DE LA VIA E · cruce espacial")
    print("=" * 100)
    print(f"\nEl veredicto de via E de cada zona candidata, tal como lo dejo la ronda 2:\n")
    for zid in sorted({z for lista in CANDIDATAS.values() for z in lista}):
        if zid in veredictos.index:
            fila = veredictos.loc[zid]
            print(f"  {zid:<7}{str(fila['zona'])[:44]:<46}via E: {fila['via_E']}")
        else:
            print(f"  {zid:<7}{'(no esta en seis_vias_ronda_2.csv)':<46}"
                  f"{'no tiene veredicto propio de via E'}")

    soportes = soportes_94().set_index("polo_id")
    filas = []
    print("\n" + "-" * 100)
    print("Cada fila contra sus zonas candidatas (fraccion del AREA del poligono):")
    print("-" * 100)
    for fila in pendientes.itertuples():
        geom = soportes.geometry.get(fila.polo_id)
        barrio = "Flores" if "Flores" in str(fila.nombre_polo) else "Balvanera"
        if geom is None or geom.is_empty:
            print(f"\n{fila.polo_id:<14}SIN SOPORTE GEOMETRICO: no se cruza")
            filas.append(dict(polo_id=fila.polo_id, nombre=fila.nombre_polo, barrio=barrio,
                              zona_asignada="", fraccion="", via_E_heredada="",
                              modo_nuevo="sigue requiere_cruce", detalle="sin soporte geometrico"))
            continue
        geom = limpia(geom)
        reparto = []
        for zid in CANDIDATAS[barrio]:
            if zid not in zonas.index:
                continue
            frac = limpia(geom.intersection(zonas.geometry.loc[zid])).area / geom.area
            if frac > 0.001:
                reparto.append((zid, frac))
        reparto.sort(key=lambda t: -t[1])
        detalle = " · ".join(f"{z} {f:.1%}" for z, f in reparto) or "no cae en ninguna candidata"
        print(f"\n{fila.polo_id:<14}{str(fila.nombre_polo)[:26]:<28}{geom.area / 10_000:>8,.1f} ha"
              f"   {detalle}")

        # regla 6 · el soporte contiene a otras candidatas: no hereda de ninguna.
        # Se mide por fraccion cubierta y no con `contains()`: Z24 se sale del barrio de Flores
        # —su delimitacion toca el borde de Floresta— y el predicado estricto la deja pasar.
        contenidas = []
        for z in CANDIDATAS[barrio]:
            if z in zonas.index and z != "Z23":
                g_z = zonas.geometry.loc[z]
                # el mismo 50 % de la regla 2, leido al reves: si el soporte se lleva mas de la
                # mitad de la zona, la zona es una PARTE del soporte y no al reves.
                if limpia(geom.intersection(g_z)).area / g_z.area >= PERTENENCIA_MIN:
                    contenidas.append(z)
        gana = reparto[0] if reparto and reparto[0][1] >= PERTENENCIA_MIN else None
        if contenidas:
            print(f"{'':<14}-> NO SE RESUELVE (regla 6): el soporte CONTIENE a "
                  f"{', '.join(contenidas)}. La herencia no vale hacia arriba.")
            filas.append(dict(
                polo_id=fila.polo_id, nombre=fila.nombre_polo, barrio=barrio, zona_asignada="",
                fraccion="", via_E_heredada="", modo_nuevo="sigue requiere_cruce",
                detalle=f"{detalle} · el soporte contiene a {', '.join(contenidas)}: "
                        f"heredar seria atribuirle al todo lo de una parte"))
            continue
        # regla 5 · la ganadora es una zona cuyo poligono es el barrio entero, y la competencia
        # esta dentro de ese mismo barrio: la contencion no discrimina
        if gana and gana[0] in POLIGONO_ES_EL_BARRIO and POLIGONO_ES_EL_BARRIO[gana[0]] == barrio:
            print(f"{'':<14}-> NO SE RESUELVE (regla 5): {gana[0]} se lleva {gana[1]:.1%}, pero su "
                  f"poligono ES el barrio de {barrio}.")
            print(f"{'':<14}   'Cae en {gana[0]}' y 'cae en {barrio}' son la misma frase: no "
                  f"discrimina contra la otra zona del barrio.")
            filas.append(dict(
                polo_id=fila.polo_id, nombre=fila.nombre_polo, barrio=barrio, zona_asignada="",
                fraccion=f"{gana[1]:.1%}", via_E_heredada="",
                modo_nuevo="sigue requiere_cruce",
                detalle=f"{detalle} · el poligono de {gana[0]} es el barrio entero: la contencion "
                        f"no distingue {gana[0]} de la otra zona del barrio, que no tiene poligono"))
            continue
        if gana is None:
            modo, zona_ok, heredado = "sigue requiere_cruce", "", ""
            print(f"{'':<14}-> NO SE RESUELVE: ninguna candidata llega al "
                  f"{PERTENENCIA_MIN:.0%}")
        else:
            zona_ok, frac = gana
            heredado = (veredictos.loc[zona_ok, "via_E"] if zona_ok in veredictos.index
                        else "la zona no tiene veredicto propio de via E")
            if zona_ok in RESIDUOS:
                modo = "heredada_de_residuo"
                print(f"{'':<14}-> hereda de {zona_ok} ({frac:.1%}) · via E: {heredado}")
                print(f"{'':<14}   PERO {zona_ok} es un RESIDUO —el barrio menos Z24 y Z39b—, "
                      f"y ahi adentro esta Bajo Flores,")
                print(f"{'':<14}   que la ronda 2 le atribuyo a Z39. La herencia queda marcada.")
            elif zona_ok not in veredictos.index:
                modo = "sigue requiere_cruce"
                print(f"{'':<14}-> cae en {zona_ok} ({frac:.1%}) pero {zona_ok} NO tiene "
                      f"veredicto propio de via E: no hay de que heredar")
            else:
                modo = "heredada"
                print(f"{'':<14}-> HEREDA de {zona_ok} ({frac:.1%}) · via E: {heredado}")
        filas.append(dict(
            polo_id=fila.polo_id, nombre=fila.nombre_polo, barrio=barrio,
            zona_asignada=zona_ok, fraccion=f"{gana[1]:.1%}" if gana else "",
            via_E_heredada=heredado, modo_nuevo=modo, detalle=detalle))

    # ---- el recuento ---------------------------------------------------------------------
    resueltas = [f for f in filas if f["modo_nuevo"] in ("heredada", "heredada_de_residuo")]
    firmes = [f for f in resueltas if f["modo_nuevo"] == "heredada"]
    print("\n" + "=" * 100)
    print(f"RESUELTAS: {len(resueltas)} de 10   ({len(firmes)} sin salvedad, "
          f"{len(resueltas) - len(firmes)} heredando de un residuo)")
    # El denominador del tablero: 84 % son las filas con veredicto si/no. Las otras 15 son los 10
    # requiere_cruce, 4 PENDIENTE y 1 REVISAR. Se reconcilia aca para no publicar otro porcentaje.
    total_antes = int(via_e["via_E_abierta"].isin(["si", "no"]).sum())
    print(f"  base: {total_antes}/94 ({total_antes / 94:.0%}) filas con veredicto si/no "
          f"—es el 84 % del tablero—, mas 10 requiere_cruce, 4 PENDIENTE y 1 REVISAR")
    print(f"  con este cruce: {total_antes + len(resueltas)}/94 "
          f"({(total_antes + len(resueltas)) / 94:.0%})")
    print(f"  si el cierre de los 10 hubiera salido completo habria dado 89/94 (95 %)")
    sin_cerrar = [f for f in filas if f["modo_nuevo"] == "sigue requiere_cruce"]
    if sin_cerrar:
        print(f"\n  Las {len(sin_cerrar)} que no cierran, y por que:")
        for f in sin_cerrar:
            print(f"    {f['polo_id']:<14}{f['detalle']}")
    print("=" * 100)

    destino = SALIDA / "via_E_requiere_cruce.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["polo_id", "nombre", "barrio", "zona_asignada",
                                           "fraccion", "via_E_heredada", "modo_nuevo", "detalle"])
        w.writeheader()
        w.writerows(filas)
    print(f"\nEscrito: {destino.name} ({len(filas)} filas)")


if __name__ == "__main__":
    main()
