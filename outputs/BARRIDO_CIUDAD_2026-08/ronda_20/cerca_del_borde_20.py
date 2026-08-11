# -*- coding: utf-8 -*-
"""Los que quedan fuera de todo borde, con la geometría de ahora y contra el perímetro que se lee.

QUÉ CAMBIA CONTRA LA MEDICIÓN ANTERIOR · tres cosas, y las tres importan
------------------------------------------------------------------------
1. **La geometría.** La Boca · Almirante Brown y Necochea pasa a 16,17 ha, así que los tres
   establecimientos que ese borde fue extendido a contener dejan de estar afuera.

2. **La capa de reconocimiento.** La medición anterior leyó `hitos_capa_2026.geojson`, que es una
   foto de la capa anterior a la ronda 5 y trae el Café Roma dos veces. Acá se lee la capa
   canónica, `hitos_capa_2026_r11.csv`: sin el duplicado y con los diez establecimientos que la
   foto no tiene.

3. **Contra qué texto se corre la prueba de «¿lo nombra el perímetro escrito?».** La medición
   anterior la corría contra las columnas de la ficha de trabajo, buscando palabras. Acá se corre
   contra **el bloque «Dónde está» de la página publicada**, con las calles ya resueltas contra el
   callejero oficial en `perimetro_escrito_41.py`. Es el texto que el criterio adoptado nombra
   —«una calle que el perímetro escrito ya nombra»— y es el que lee quien recibe el documento.

   El cambio no es cosmético. Por buscar palabras en otro texto, la medición anterior daba que el
   perímetro de Balvanera no nombraba Av. Rivadavia; la página **la nombra, y con alturas**.

Las dos pruebas siguen siendo las mismas y siguen publicándose por separado: que el texto nombre
la calle, y que la calle llegue hasta el borde. El corte de 250 m sigue siendo una prioridad de
inspección y no una prueba de que el borde esté incompleto.

Se mide en EPSG:5347. Cero requests. Nada se adopta.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
sys.path.insert(0, str(SALIDA))
sys.path.insert(0, str(BARRIDO / "ronda_19"))
sys.path.insert(0, str(BARRIDO / "ronda_18"))
sys.path.insert(0, str(BARRIDO / "ronda_17"))
import geometria_vigente_20 as gv  # noqa: E402
from anclas_dentro_y_fuera import Direcciones  # noqa: E402
from cierre_geometrico import Callejero  # noqa: E402
from cinco_sin_ancla_adentro import extender, piezas, tramo_hasta  # noqa: E402
from hitos_cerca_del_borde import calle_de  # noqa: E402
from perimetro_escrito_41 import D as DECLARACION  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()
CAPA = BARRIDO / "hitos" / "hitos_capa_2026_r11.csv"
BARRIOS = BARRIDO / "insumos" / "caba_barrios.geojson"
ANTERIOR = BARRIDO / "ronda_19" / "hitos_cerca_del_borde.csv"

TOLERANCIA_BORDE_M = 3.0
CORTE_M = 250.0


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 98)
    print("FUERA DE TODO BORDE · geometría de ahora, capa canónica, perímetro de la página")
    print("=" * 98 + "\n")

    cj = Callejero()
    dirs = Direcciones(cj)
    bordes, procedencia, soportes = gv.cargar()
    nombres = {pid: str(soportes.polo_nombre.loc[pid]) for pid in bordes}
    barrios = gpd.read_file(BARRIOS).to_crs(CRS_M)

    # El perímetro escrito de cada página: la lista de calles del control de esta tanda, guardada
    # **por familia del callejero y no por cadena**.
    #
    # Comparar los nombres como texto da falsos negativos, y no en un caso raro: la puerta del
    # Café de los Angelitos resuelve como «RIVADAVIA» y la página escribe «Av. Rivadavia», que
    # resuelve como «RIVADAVIA AV.». Son la misma avenida —el callejero las tiene en la misma
    # familia— y la comparación de cadenas decía que la página no la nombraba. Se compara por
    # familia, que es la pregunta real: ¿son la misma calle?
    #
    # Y no todo par que se parece es la misma: «CALLAO» y «CALLAO AV.» son familias distintas, así
    # que esto no afloja la prueba, la hace correcta.
    def familia(nombre):
        cj.segmentos(nombre)          # corta si el nombre no resuelve
        clave = cj._sin_tildes(nombre)
        return frozenset(cj.familias.get(clave, {clave}))

    nombradas = {d["pid"]: {familia(c) for c in d["calles"]} for d in DECLARACION}
    if set(nombradas) != set(bordes):
        raise SystemExit("el control del perímetro escrito y la geometría no cubren los mismos "
                         "polos. No se corre la prueba con una página de menos.")

    capa = pd.read_csv(CAPA)
    con_punto = capa[capa.latitud.notna() & capa.longitud.notna()].copy()
    sin_punto = len(capa) - len(con_punto)
    geo = gpd.GeoDataFrame(
        con_punto, geometry=gpd.GeoSeries(
            [Point(x, y) for x, y in zip(con_punto.longitud, con_punto.latitud)],
            crs=CRS_G).to_crs(CRS_M).values, crs=CRS_M)
    print(f"capa canónica: {len(capa)} establecimientos, {len(geo)} con punto "
          f"({sin_punto} sin geocodificar, y se dice)")

    por_punto = {}
    for _, h in geo.iterrows():
        por_punto.setdefault(h.geometry.wkt, []).append(str(h.hito_id))
    repetidos = {i: [x for x in v if x != i]
                 for v in por_punto.values() if len(v) > 1 for i in v}
    print(f"puntos repetidos en la capa: {len(repetidos)} filas comparten coordenada con otra")
    for i, otros in sorted(repetidos.items()):
        f = geo.loc[geo.hito_id == i].iloc[0]
        print(f"    {i:<10} {str(f['nombre'])[:26]:<28} {str(f.direccion)[:26]:<28} "
              f"= {', '.join(otros)}")
    print("")

    ids = sorted(bordes)
    geoms = [bordes[p] for p in ids]

    fuera, contacto, adentro = [], [], []
    for _, h in geo.sort_values("hito_id").iterrows():
        d = [g.distance(h.geometry) for g in geoms]
        dmin = min(d)
        i = d.index(dmin)
        if dmin <= 1e-7:
            adentro.append((h, ids[i]))
            continue
        if dmin <= TOLERANCIA_BORDE_M:
            contacto.append(dict(hito_id=h.hito_id, nombre=h["nombre"], polo_id=ids[i],
                                 polo=nombres[ids[i]], distancia_m=round(dmin, 1),
                                 decision="contacto de borde; se publica aparte"))
            continue
        fuera.append((h, ids[i], dmin))

    print(f"adentro de algún borde                 : {len(adentro)}")
    print(f"en contacto de borde (0 a {TOLERANCIA_BORDE_M:.0f} m)        : {len(contacto)}")
    print(f"fuera de todo borde (más de {TOLERANCIA_BORDE_M:.0f} m)      : {len(fuera)}\n")

    filas = []
    for h, pid, dmin in sorted(fuera, key=lambda x: x[2]):
        borde = bordes[pid]
        ha0, loc0 = cj.ha(borde), cj.locales(borde)
        texto_calle = calle_de(h.direccion) if pd.notna(h.direccion) else None
        calle = dirs.calle(texto_calle) if texto_calle else None

        la_nombra = toca = None
        ha1 = loc1 = tramo_m = piezas1 = ""
        if calle is not None:
            la_nombra = familia(calle) in nombradas[pid]
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
            hito_id=h.hito_id, nombre=h["nombre"], tipo=h.tipo, direccion=h.direccion,
            barrio=barrio, polo_mas_cercano_id=pid, polo_mas_cercano=nombres[pid],
            distancia_m=round(dmin, 1),
            a_250_m_o_menos="si" if dmin <= CORTE_M else "no",
            calle_de_la_puerta=calle or "",
            la_nombra_el_perimetro_escrito=("" if calle is None else
                                            ("si" if la_nombra else "no")),
            la_calle_toca_el_borde="" if calle is None else ("si" if toca else "no"),
            que_haria_falta=veredicto,
            ha_del_borde_ahora=round(ha0, 2), locales_del_borde_ahora=loc0,
            ha_si_se_extiende=ha1, locales_si_se_extiende=loc1,
            tramo_a_agregar_m=tramo_m, piezas_si_se_extiende=piezas1,
            categoria_del_perimetro=next(d["categoria"] for d in DECLARACION
                                         if d["pid"] == pid),
        ))

    df = pd.DataFrame(filas)
    cerca = df[df.a_250_m_o_menos == "si"]
    resuelven = cerca[cerca.que_haria_falta ==
                      "extender sobre una calle que el perímetro escrito ya nombra"]

    print("=" * 98)
    print("EL CUADRO")
    print("=" * 98)
    print(f"  fuera de todo borde                        : {len(df)}")
    for corte in (100, 250, 500):
        print(f"  de ésos, a {corte:>3} m o menos                   : "
              f"{int((df.distancia_m <= corte).sum())}")
    print(f"\n  de los {len(cerca)} que están a {CORTE_M:.0f} m o menos:")
    for v, sub in cerca.groupby("que_haria_falta"):
        print(f"      {len(sub):>3}  {v}")

    print(f"\n  los que se resolverían sin inventar una línea: {len(resuelven)}")
    print(f"  {'establecimiento':<30} {'dirección':<26} {'polo':<28} {'m':>7}  el borde pasaría a")
    for r in resuelven.sort_values("distancia_m").itertuples():
        print(f"  {str(r.nombre)[:28]:<30} {str(r.direccion)[:24]:<26} "
              f"{str(r.polo_mas_cercano)[:26]:<28} {r.distancia_m:>7,.1f}  "
              f"{r.ha_si_se_extiende:>8,.2f} ha · {r.locales_si_se_extiende:>4} locales")

    print(f"\n  por categoría del perímetro escrito de la página más cercana:")
    for cat, sub in cerca.groupby("categoria_del_perimetro"):
        n = int((sub.que_haria_falta ==
                 "extender sobre una calle que el perímetro escrito ya nombra").sum())
        print(f"      {cat:<42} {len(sub):>3} cerca · {n} sobre calle ya nombrada")

    campos = list(filas[0].keys())
    with (SALIDA / "cerca_del_borde_20.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    if contacto:
        with (SALIDA / "contacto_de_borde_20.csv").open("w", encoding="utf-8",
                                                        newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(contacto[0].keys()))
            w.writeheader()
            w.writerows(contacto)

    # --------------------------------------------------- qué cambió contra la medición anterior
    print("\n" + "=" * 98)
    print("QUÉ CAMBIÓ CONTRA LA MEDICIÓN ANTERIOR")
    print("=" * 98)
    ant = pd.read_csv(ANTERIOR)
    # la tanda anterior guardó el corte como `prioridad_de_inspeccion` y no como una columna
    # «si/no»; se recalcula desde la distancia, que es el dato y no la etiqueta
    ant_cerca = ant[ant.distancia_m <= CORTE_M]
    ant_res = ant_cerca[ant_cerca.que_haria_falta ==
                        "extender sobre una calle que el perímetro escrito ya nombra"]
    print(f"  {'':<44}{'antes':>8}{'ahora':>8}")
    print(f"  {'fuera de todo borde':<44}{len(ant):>8}{len(df):>8}")
    print(f"  {'a 250 m o menos':<44}{len(ant_cerca):>8}{len(cerca):>8}")
    print(f"  {'sobre calle que el perímetro ya nombra':<44}{len(ant_res):>8}{len(resuelven):>8}")

    salieron = sorted(set(ant.hito_id) - set(df.hito_id))
    entraron = sorted(set(df.hito_id) - set(ant.hito_id))
    print(f"\n  dejaron de estar afuera: {len(salieron)}")
    for hid in salieron:
        f = ant[ant.hito_id == hid].iloc[0]
        print(f"      {hid:<9} {str(f['nombre'])[:30]:<32} estaba a {f.distancia_m:>6,.1f} m de "
              f"{f.polo_mas_cercano}")
    print(f"  empezaron a estar afuera: {len(entraron)}")
    for hid in entraron:
        f = df[df.hito_id == hid].iloc[0]
        print(f"      {hid:<9} {str(f['nombre'])[:30]:<32} a {f.distancia_m:>7,.1f} m de "
              f"{f.polo_mas_cercano}")

    comunes = set(ant.hito_id) & set(df.hito_id)
    a = ant.set_index("hito_id").loc[sorted(comunes)]
    b = df.set_index("hito_id").loc[sorted(comunes)]
    cambio = [i for i in sorted(comunes)
              if str(a.loc[i, "que_haria_falta"]) != str(b.loc[i, "que_haria_falta"])]
    print(f"\n  cambiaron de veredicto sin moverse: {len(cambio)}   "
          f"(la prueba se corre contra otro texto)")
    for i in cambio:
        print(f"      {i:<9} {str(b.loc[i, 'nombre'])[:28]:<30} "
              f"{str(b.loc[i, 'polo_mas_cercano'])[:22]:<24}")
        print(f"      {'':<9} antes: {a.loc[i, 'que_haria_falta']}")
        print(f"      {'':<9} ahora: {b.loc[i, 'que_haria_falta']}")

    (SALIDA / "cerca_del_borde_resumen.json").write_text(json.dumps(dict(
        fecha=HOY, fuera_de_todo_borde=len(df), a_250_m_o_menos=len(cerca),
        a_100_m_o_menos=int((df.distancia_m <= 100).sum()),
        a_500_m_o_menos=int((df.distancia_m <= 500).sum()),
        sobre_calle_ya_nombrada=len(resuelven),
        exigen_una_calle_que_el_texto_no_nombra=int(len(cerca) - len(resuelven)),
        en_contacto_de_borde=len(contacto),
        dejaron_de_estar_afuera=salieron, empezaron_a_estar_afuera=entraron,
        cambiaron_de_veredicto=cambio,
    ), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nEscrito: cerca_del_borde_20.csv ({len(filas)} filas) · "
          f"contacto_de_borde_20.csv ({len(contacto)} filas) · cerca_del_borde_resumen.json")


if __name__ == "__main__":
    main()
