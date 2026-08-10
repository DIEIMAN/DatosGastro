# -*- coding: utf-8 -*-
"""Los establecimientos con reconocimiento que quedan fuera de todo borde, con la geometría de ahora.

QUÉ REHACE Y POR QUÉ
--------------------
La medición anterior se hizo contra la instantánea anterior de bordes y encontró 60 fuera de todo
polo, de los cuales 41 a 250 m o menos. Después de eso se movieron cuatro bordes, así que las
distancias cambiaron y el cálculo hay que rehacerlo.

**El corte de 250 m es una prioridad de inspección, no una prueba de que el borde esté
incompleto.** Eso no cambia. Lo que esta corrida agrega es la distinción que decide si un caso es
para revisar o para dejar como está: para cada uno se mide si el borde más cercano lo dejaría
adentro **extendiendo sobre una calle que su perímetro escrito ya nombra**, o si haría falta
inventar una línea que el texto no dice.

CÓMO SE DECIDE ESA COLUMNA · dos pruebas, las dos publicadas
------------------------------------------------------------
  1. **¿La nombra el texto?** La calle de la puerta, resuelta contra el callejero oficial, contra
     el perímetro escrito de la página, normalizado sin tildes. Es una prueba de texto y se dice
     que lo es.
  2. **¿Toca el borde?** El eje de esa calle contra el polígono del polo. Una calle que el texto
     nombra pero que no llega hasta el borde tampoco resuelve: la extensión quedaría suelta.

Sólo cuando las dos dan que sí el caso es «extender sobre una calle que el perímetro ya nombra».
En los demás se dice cuál de las dos falló. Y para todos se mide lo que costaría igual —hectáreas
y locales— porque el costo es la mitad de la decisión.

Se mide en EPSG:5347. Cero requests. Nada se adopta.
"""

import csv
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import nearest_points, unary_union

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
sys.path.insert(0, str(SALIDA))
sys.path.insert(0, str(BARRIDO / "ronda_18"))
sys.path.insert(0, str(BARRIDO / "ronda_17"))
import geometria_vigente_19 as gv  # noqa: E402
from anclas_dentro_y_fuera import Direcciones  # noqa: E402
from cierre_geometrico import Callejero  # noqa: E402
from cinco_sin_ancla_adentro import extender, piezas, tramo_hasta  # noqa: E402
from geometria_vigente_19 import limpia  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()
HITOS = BARRIDO / "hitos" / "hitos_capa_2026.geojson"
FICHAS = BARRIDO / "ronda_17_codex" / "fichas_corpus_polos.csv"
BARRIOS = BARRIDO / "insumos" / "caba_barrios.geojson"
ANTERIOR = BARRIDO / "ronda_18_codex" / "hitos_fuera_de_todo_polo.csv"

# Los mismos dos cortes de la medición anterior, para que las dos sean comparables.
TOLERANCIA_BORDE_M = 3.0
CORTE_M = 250.0
# Palabras que no distinguen una calle de otra: si el perímetro escrito dice «avenida», eso no
# prueba que nombre a ESTA avenida.
VACIAS = {"av", "avda", "avenida", "calle", "pje", "pasaje", "diag", "diagonal", "dr", "gral",
          "cnel", "coronel", "general", "presidente", "pres", "tte", "teniente", "de", "del",
          "la", "el", "los", "las", "y", "san", "santa", "alte", "almirante", "capitan", "cap",
          "ing", "ingeniero", "int", "intendente", "doctor", "profesor", "prof"}


def sin_tildes(t):
    return unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower()


def significativas(nombre):
    """Las palabras de un nombre de calle que sirven para reconocerla en un texto."""
    return {w for w in re.split(r"[^a-z0-9]+", sin_tildes(nombre))
            if len(w) > 2 and w not in VACIAS}


def calle_de(direccion):
    """«Av. Callao 83» -> «Av. Callao». Devuelve None si no hay nada antes del número.

    El recorte del número **exige un espacio antes**. Sin esa exigencia, la parte opcional del
    «nº» se comía la última letra del nombre de la calle: «Pinzon 102» daba «Pinzo», «Tucuman
    1700» daba «Tucuma» y «Av. San Juan 1999» daba «Av. San Jua». Doce direcciones de ochenta
    salieron como «no resuelve contra el callejero» sin que nada fallara.
    """
    t = str(direccion).strip(" .,")
    t = re.sub(r"\s*,?\s*(local|locales|piso|pb|of\.?|oficina|depto\.?|dpto\.?)\b.*$", "",
               t, flags=re.I)
    t = re.sub(r"\s+(?:n[°º]\s*)?\d{1,5}(?:\s*bis)?\s*$", "", t)
    t = re.sub(r"\s+(esq\.?|esquina|y)\s+.*$", "", t, flags=re.I).strip(" .,")
    return t or None


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 98)
    print("ESTABLECIMIENTOS CON RECONOCIMIENTO FUERA DE TODO BORDE · con la geometría de ahora")
    print("=" * 98 + "\n")

    cj = Callejero()
    dirs = Direcciones(cj)
    bordes, procedencia, soportes = gv.cargar()
    nombres = {pid: str(soportes.polo_nombre.loc[pid]) for pid in bordes}
    fichas = pd.read_csv(FICHAS).set_index("polo_id")
    barrios = gpd.read_file(BARRIOS).to_crs(CRS_M)

    perimetro_texto = {}
    for pid in bordes:
        txt = ""
        if pid in fichas.index:
            for col in ("perimetro_textual", "nota_de_delimitacion"):
                v = fichas.loc[pid, col]
                if isinstance(v, str) and v.strip() and v.strip().lower() != "nan":
                    txt += " " + v
        perimetro_texto[pid] = sin_tildes(txt)

    capa = gpd.read_file(HITOS).to_crs(CRS_M)
    print(f"capa de reconocimiento: {len(capa)} establecimientos con punto")
    print(f"geometría vigente: {len(bordes)} bordes\n")

    ids = sorted(bordes)
    geoms = [bordes[p] for p in ids]

    # Dos filas de la capa con el MISMO punto son un establecimiento contado dos veces. No se
    # descartan acá —la capa no es de esta corrida— pero la columna tiene que estar, porque si
    # no el conteo de «cuántos quedan cerca del borde» sale inflado y nadie lo ve.
    por_punto = {}
    for _, h in capa.iterrows():
        por_punto.setdefault(h.geometry.wkt, []).append(str(h.hito_id))
    duplicado_de = {i: [x for x in v if x != i]
                    for v in por_punto.values() if len(v) > 1 for i in v}
    if duplicado_de:
        print(f"puntos repetidos en la capa: {len(duplicado_de)} filas comparten coordenada con "
              f"otra")
        for i, otros in sorted(duplicado_de.items()):
            nom = capa.loc[capa.hito_id == i, "nombre"].iloc[0]
            dirc = capa.loc[capa.hito_id == i, "direccion"].iloc[0]
            print(f"    {i:<10} {str(nom)[:26]:<28} {str(dirc)[:28]:<30} = {', '.join(otros)}")
        print("")

    fuera, contacto = [], []
    for _, h in capa.sort_values("hito_id").iterrows():
        d = [g.distance(h.geometry) for g in geoms]
        dmin = min(d)
        i = d.index(dmin)
        if 1e-7 < dmin <= TOLERANCIA_BORDE_M:
            contacto.append(dict(hito_id=h.hito_id, nombre=h.nombre, polo_id=ids[i],
                                 polo=nombres[ids[i]], distancia_m=round(dmin, 1),
                                 decision="contacto de borde; se publica aparte"))
        if dmin <= TOLERANCIA_BORDE_M:
            continue
        fuera.append((h, ids[i], dmin))

    print(f"fuera de todo borde (más de {TOLERANCIA_BORDE_M:.0f} m de los 41): {len(fuera)}")
    print(f"en contacto de borde (entre 0 y {TOLERANCIA_BORDE_M:.0f} m): {len(contacto)}\n")

    filas = []
    for h, pid, dmin in sorted(fuera, key=lambda x: x[2]):
        borde = bordes[pid]
        ha0, loc0 = cj.ha(borde), cj.locales(borde)
        texto_calle = calle_de(h.direccion)
        calle = dirs.calle(texto_calle) if texto_calle else None

        la_nombra = toca = None
        ha1 = loc1 = tramo_m = ""
        piezas1 = ""
        if calle is not None:
            palabras = significativas(calle)
            la_nombra = bool(palabras) and all(w in perimetro_texto[pid] for w in palabras)
            eje = unary_union(list(cj.segmentos(calle).geometry))
            toca = eje.distance(borde) <= 1.0
            if dmin <= CORTE_M:
                tramo, largo = tramo_hasta(cj, calle, borde, h.geometry)
                ext = extender(cj, borde, [tramo])
                ha1, loc1, tramo_m = round(cj.ha(ext), 2), cj.locales(ext), round(largo)
                piezas1 = piezas(ext)

        if calle is None:
            veredicto = "no se puede decidir: la dirección no resuelve contra el callejero"
        elif la_nombra and toca:
            veredicto = "extender sobre una calle que el perímetro escrito ya nombra"
        elif la_nombra and not toca:
            veredicto = ("el perímetro nombra la calle pero la calle no llega al borde: la "
                         "extensión quedaría suelta")
        elif toca:
            veredicto = "haría falta una calle que el perímetro escrito no nombra"
        else:
            veredicto = ("haría falta una calle que el perímetro escrito no nombra, y que "
                         "además no toca el borde")

        bmask = barrios.geometry.covers(h.geometry)
        barrio = str(barrios.loc[bmask, "BARRIO"].iloc[0]).title() if bmask.any() else "sin asignar"

        filas.append(dict(
            hito_id=h.hito_id, nombre=h.nombre, tipo=h.tipo, direccion=h.direccion,
            barrio=barrio, polo_mas_cercano_id=pid, polo_mas_cercano=nombres[pid],
            distancia_m=round(dmin, 1),
            prioridad_de_inspeccion=("a 250 m o menos" if dmin <= CORTE_M
                                     else "más de 250 m"),
            calle_de_la_puerta=calle or "",
            la_nombra_el_perimetro_escrito=("" if la_nombra is None
                                            else ("si" if la_nombra else "no")),
            la_calle_toca_el_borde="" if toca is None else ("si" if toca else "no"),
            que_haria_falta=veredicto,
            tramo_a_agregar_m=tramo_m,
            ha_del_borde_actual=round(ha0, 2), locales_del_borde_actual=loc0,
            ha_si_se_extiende=ha1, locales_si_se_extiende=loc1,
            delta_ha=round(ha1 - ha0, 2) if ha1 != "" else "",
            delta_locales=(loc1 - loc0) if loc1 != "" else "",
            piezas_del_borde_actual=piezas(borde),
            piezas_si_se_extiende=piezas1,
            mismo_punto_que=" ".join(duplicado_de.get(str(h.hito_id), [])),
            borde_transitorio="si" if pid in gv.TRANSITORIOS else "no",
            borde_es_propio="no" if pid in gv.SIN_BORDE_PROPIO else "si",
            perimetro_escrito_de_la_pagina=(
                str(fichas.loc[pid, "perimetro_textual"])[:220]
                if pid in fichas.index and isinstance(fichas.loc[pid, "perimetro_textual"], str)
                else "la página no escribe perímetro")))

    d = pd.DataFrame(filas)
    cerca = d[d.distancia_m <= CORTE_M]

    print("=" * 98)
    print(f"LOS QUE QUEDAN A {CORTE_M:.0f} M O MENOS DE UN BORDE · {len(cerca)}, "
          f"por distancia")
    print("=" * 98)
    print(f"  {'establecimiento':<32} {'tipo':<22} {'polo más cercano':<26} {'m':>6}  qué haría falta")
    for r in cerca.itertuples():
        print(f"  {str(r.nombre)[:30]:<32} {str(r.tipo)[:20]:<22} "
              f"{str(r.polo_mas_cercano)[:24]:<26} {r.distancia_m:>6,.1f}  {r.que_haria_falta[:58]}")

    ya_nombrada = cerca[cerca.la_nombra_el_perimetro_escrito == "si"]
    print(f"\n  de los {len(cerca)}:")
    print(f"    la calle de su puerta ya está en el perímetro escrito y toca el borde : "
          f"{(cerca.que_haria_falta == 'extender sobre una calle que el perímetro escrito ya nombra').sum():>3}")
    print(f"    el perímetro la nombra pero la calle no llega al borde                : "
          f"{(cerca.que_haria_falta.str.startswith('el perímetro nombra')).sum():>3}")
    print(f"    haría falta una calle que el perímetro escrito no nombra              : "
          f"{(cerca.que_haria_falta.str.startswith('haría falta')).sum():>3}")
    print(f"    la dirección no resuelve contra el callejero                          : "
          f"{(cerca.calle_de_la_puerta == '').sum():>3}")

    if len(ya_nombrada):
        print(f"\n  los que se resolverían sobre una calle que el texto ya nombra:")
        for r in ya_nombrada.sort_values("distancia_m").itertuples():
            print(f"      {str(r.nombre)[:30]:<32} {str(r.direccion)[:28]:<30} "
                  f"{r.polo_mas_cercano_id} a {r.distancia_m:>5,.1f} m · "
                  f"{r.ha_del_borde_actual:,.2f} -> {r.ha_si_se_extiende:,.2f} ha · "
                  f"{r.locales_del_borde_actual} -> {r.locales_si_se_extiende} locales "
                  f"({r.piezas_si_se_extiende} pieza/s)")

    # sensibilidad, con los mismos tres cortes de la medición anterior
    print(f"\n  sensibilidad al corte (el corte es una convención, no un hallazgo):")
    sens = []
    for corte in (100, 250, 500):
        n = int((d.distancia_m <= corte).sum())
        sens.append(dict(corte_m=corte, a_revisar=n, esperables=len(d) - n, universo=len(d)))
        print(f"      a {corte:>3} m: {n:>3} a revisar · {len(d) - n:>3} esperables "
              f"de {len(d)}")

    # contra la medición anterior
    print(f"\n  contra la medición anterior, que se hizo con los bordes de antes:")
    if ANTERIOR.exists():
        ant = pd.read_csv(ANTERIOR)
        ant_cerca = ant[ant.distancia_m <= CORTE_M]
        print(f"      antes: {len(ant)} fuera de todo polo, {len(ant_cerca)} a 250 m o menos")
        print(f"      ahora: {len(d)} fuera de todo borde, {len(cerca)} a 250 m o menos")
        antes_ids = set(ant.hito_id)
        ahora_ids = set(d.hito_id)
        entraron = sorted(antes_ids - ahora_ids)
        salieron = sorted(ahora_ids - antes_ids)
        print(f"      dejaron de estar afuera (los recoge un borde nuevo): "
              f"{len(entraron)}{': ' + ', '.join(entraron) if entraron else ''}")
        print(f"      pasaron a estar afuera: {len(salieron)}")
        # De dónde salieron: el soporte provisorio que los contenía y qué pasó con ese polo. Sin
        # esto, «pasaron a estar afuera 20» se lee como si hubieran aparecido establecimientos
        # nuevos, y lo que pasó es que el perímetro trazado es más chico que el soporte que
        # reemplazó.
        sop_m = soportes.to_crs(CRS_M)
        cuenta = {}
        for hid in salieron:
            g = capa.loc[capa.hito_id == hid, "geometry"].iloc[0]
            dentro = [pid for pid, gg in sop_m.geometry.items() if limpia(gg).covers(g)]
            for pid in dentro:
                cuenta.setdefault(pid, []).append(hid)
        for pid, lista in sorted(cuenta.items(), key=lambda x: -len(x[1])):
            print(f"          los contenía el soporte {pid} ({nombres.get(pid, '')}), que ahora "
                  f"publica su borde de «{procedencia.get(pid, '')}»: {len(lista)}")
        sin_soporte = [h for h in salieron
                       if not any(h in v for v in cuenta.values())]
        if sin_soporte:
            print(f"          no estaban dentro de ningún soporte: {', '.join(sin_soporte)}")
        comunes = antes_ids & ahora_ids
        ant_i = ant.set_index("hito_id").distancia_m
        aho_i = d.set_index("hito_id").distancia_m
        movidos = [(k, float(ant_i[k]), float(aho_i[k])) for k in sorted(comunes)
                   if abs(float(ant_i[k]) - float(aho_i[k])) > 0.5]
        print(f"      cambiaron de distancia: {len(movidos)}")
        for k, a, b in sorted(movidos, key=lambda x: x[2])[:12]:
            nom = str(d.set_index("hito_id").nombre[k])[:28]
            print(f"          {k} {nom:<30} {a:>7,.1f} m -> {b:>7,.1f} m")

    campos = list(filas[0].keys())
    with (SALIDA / "hitos_cerca_del_borde.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(sorted(filas, key=lambda f: f["distancia_m"]))
    if contacto:
        with (SALIDA / "hitos_contacto_de_borde.csv").open("w", encoding="utf-8",
                                                           newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(contacto[0].keys()))
            w.writeheader()
            w.writerows(sorted(contacto, key=lambda f: f["distancia_m"]))

    (SALIDA / "hitos_cerca_resumen.json").write_text(json.dumps(dict(
        fecha=HOY, universo=len(capa), fuera_de_todo_borde=len(d),
        a_250_m_o_menos=len(cerca), en_contacto_de_borde=len(contacto),
        sobre_calle_ya_nombrada=int(
            (cerca.que_haria_falta ==
             "extender sobre una calle que el perímetro escrito ya nombra").sum()),
        sensibilidad=sens), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nEscrito: hitos_cerca_del_borde.csv ({len(filas)} filas) · "
          f"hitos_contacto_de_borde.csv ({len(contacto)} filas) · hitos_cerca_resumen.json")


if __name__ == "__main__":
    main()
