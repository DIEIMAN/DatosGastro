# -*- coding: utf-8 -*-
"""Los cuatro que publican el polígono de su barrio: cuánto más chico es el polo que el barrio.

QUIÉNES SON LOS CUATRO
----------------------
Tres están declarados hace tandas —Núñez, Retiro y Villa Santa Rita— y el cuarto lo declara esta:
**Colegiales**. La capa lo trae como borde propio y su propia página ya dice que «el contorno que
esta página usa coincide con el polígono del barrio, y todavía no está dibujado el recorte más
chico de adentro». Acá se mide cuánto coincide, y después cuánto más chico sería el recorte.

**No se adopta ninguno.** La decisión la firma quien escribe. Esto deja la cifra.

LA REGLA DEL RECORTE, ESCRITA ANTES DE MEDIR
---------------------------------------------
El recorte más chico de adentro que contiene la concentración real de locales, con el mismo método
con el que se trazó todo lo demás:

  1. **La concentración** son las concentraciones detectadas por densidad con más de la mitad de su
     superficie dentro del contorno publicado. Es el mismo criterio con el que ya se publica
     «cuánta gastronomía hay concentrada dentro del barrio».
  2. **Los locales** son los del universo `anillo=nucleo & apto_geometria` que caen dentro de esas
     concentraciones y dentro del contorno.
  3. **La cuadra de cada local** es el segmento del callejero oficial más cercano a su punto.
  4. **El recorte** son las manzanas frentistas de esas cuadras, con el mismo frente mínimo de 20 m
     de siempre.

**Y una advertencia sobre ese frente mínimo, porque la primera versión de esta corrida publicaba
una sensibilidad que no dice nada.** A 10, 20 y 40 m el recorte da exactamente la misma superficie
en los cuatro, y eso no es robustez: es que el umbral **no llega a morder**. Las cuadras son
segmentos enteros del callejero, así que la manzana que da frente a una cuadra le da la cuadra
entera: el frente más chico que aparece en los cuatro casos es de 43 m, el doble del umbral. Lo
que se publica entonces es **el frente más chico medido**, que es el dato que dice cuán lejos está
el umbral de importar. Tres cifras iguales presentadas como sensibilidad habrían leído como una
comprobación que nadie hizo.

No se elige un contorno suave ni se rellenan huecos: el recorte es exactamente las manzanas que dan
frente a las cuadras donde están los locales. Por eso puede salir en varias piezas, y **cuántas
son se publica**: una figura en ocho pedazos no es un perímetro, y esconderlo detrás de una cifra
de superficie sería el error de siempre.

**Y se mide cuántos locales de la concentración quedan adentro del recorte.** No está garantizado
por construcción —un local retirado de la línea municipal puede caer fuera de la manzana frentista—
y un recorte que no contiene lo que fue a buscar no sirve, aunque su superficie sea creíble.

Se mide en EPSG:5347 y se guarda en EPSG:4326. Cero requests.
"""

import csv
import json
import sys
import unicodedata
import re
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
sys.path.insert(0, str(SALIDA))
sys.path.insert(0, str(BARRIDO / "ronda_17"))
import geometria_vigente_20 as gv  # noqa: E402
from geometria_vigente_20 import limpia  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()
BASE = BARRIDO / "base" / "local.csv"
PUBLICABLES = BARRIDO / "borrador_polos" / "polos_publicables.geojson"
BARRIOS = BARRIDO / "insumos" / "caba_barrios.geojson"

# Los cuatro, y el barrio contra el que se compara cada uno.
LOS_CUATRO = [("Z41", "Núñez", "NUÑEZ"), ("Z46", "Retiro", "RETIRO"),
              ("Z27", "Villa Santa Rita", "VILLA SANTA RITA"),
              ("Z43", "Colegiales", "COLEGIALES")]
DECLARADOS = {"Z41", "Z46", "Z27"}   # los tres que el documento ya cuenta como sin borde propio
FRENTE = 20.0
SENSIBILIDAD = (10.0, 40.0)


def clave_barrio(x):
    x = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", x)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from cierre_geometrico import Callejero  # noqa: E402

    print("=" * 98)
    print("EL RECORTE DE ADENTRO DE LOS CUATRO QUE PUBLICAN EL POLÍGONO DE SU BARRIO")
    print("=" * 98 + "\n")

    cj = Callejero()
    bordes, procedencia, soportes = gv.cargar()
    barrios = gpd.read_file(BARRIOS).to_crs(CRS_M)
    conc = gpd.read_file(PUBLICABLES).to_crs(CRS_M)

    base = pd.read_csv(BASE)
    base = base[(base.anillo == "nucleo") & (base.apto_geometria.astype(str).str.lower()
                                             .isin(["true", "1", "si", "sí"]))]
    pts = gpd.GeoDataFrame(
        base[["local_id"]].copy(),
        geometry=gpd.GeoSeries([Point(x, y) for x, y in zip(base.lon, base.lat)],
                               crs=CRS_G).to_crs(CRS_M).values, crs=CRS_M)
    sidx_pts = pts.sindex
    seg = cj.calles
    sidx_seg = seg.sindex

    def locales_en(g):
        cand = pts.iloc[list(sidx_pts.query(g))]
        return cand[cand.geometry.within(g)]

    def cuadra_de(punto):
        """El segmento del callejero más cercano al punto. Se busca en un entorno creciente para
        no recorrer 32.000 segmentos por local, y si el entorno queda vacío se agranda: devolver
        None por un radio corto sería perder un local en silencio."""
        for radio in (60, 150, 400, 1200):
            idx = list(sidx_seg.query(punto.buffer(radio)))
            if idx:
                sub = seg.iloc[idx]
                return sub.geometry.iloc[sub.geometry.distance(punto).values.argmin()]
        return None

    filas, capa = [], []
    for pid, nombre, barrio_nombre in LOS_CUATRO:
        borde = limpia(bordes[pid])
        sub = barrios[barrios.BARRIO.map(clave_barrio) == clave_barrio(barrio_nombre)]
        if sub.empty:
            raise SystemExit(f"«{barrio_nombre}» no está en la capa oficial de barrios.")
        gb = limpia(unary_union(list(sub.geometry)))

        ha_borde, loc_borde = cj.ha(borde), len(locales_en(borde))
        fuera = borde.difference(gb).area
        adentro_no = gb.difference(borde).area
        coincidencia = 100 * (1 - (fuera + adentro_no) / (borde.area + gb.area))

        # --- la concentración
        usadas = []
        for r in conc.itertuples():
            g = limpia(r.geometry)
            if not g.intersects(borde):
                continue
            if g.intersection(borde).area / g.area > 0.5:
                usadas.append((str(r.polo_id), g))
        if not usadas:
            raise SystemExit(f"{pid} no tiene ninguna concentración mayormente adentro. El "
                             f"recorte no tendría de qué salir y una cifra de 0 ha se leería "
                             f"como un dato. No se sigue.")
        gconc = limpia(unary_union([g for _, g in usadas]))
        de_la_conc = locales_en(limpia(gconc.intersection(borde)))

        # --- el recorte
        cuadras = []
        for p in de_la_conc.geometry:
            c = cuadra_de(p)
            if c is None:
                raise SystemExit(f"un local de {pid} no tiene ninguna cuadra a menos de 1.200 m. "
                                 f"Eso no es un dato del territorio, es un punto mal puesto.")
            cuadras.append(c)
        eje = unary_union(cuadras)

        def recorte_con(frente):
            frent = cj.frentistas(eje, frente_min=frente)
            if not frent:
                return None
            return limpia(unary_union([c for _, _, c in frent]))

        recorte = recorte_con(FRENTE)
        if recorte is None:
            raise SystemExit(f"{pid}: ninguna manzana da {FRENTE:.0f} m de frente a las cuadras "
                             f"de sus locales. No se sigue.")
        recorte = limpia(recorte.intersection(borde))   # el recorte es de ADENTRO
        ha_rec, loc_rec = cj.ha(recorte), len(locales_en(recorte))
        contenidos = int(de_la_conc.geometry.within(recorte).sum())
        n_piezas = 1 if recorte.geom_type == "Polygon" else len(recorte.geoms)
        frentes = sorted(l for _, l, _ in cj.frentistas(eje, frente_min=0.1))
        frente_min_medido = frentes[0] if frentes else 0.0
        # cuántas manzanas quedarían fuera si el umbral fuera el de mayor exigencia del juego
        muerden = sum(1 for x in frentes if x < max(SENSIBILIDAD))
        # el conteo que publica la capa de concentraciones, que es otro universo
        n_capa = sum(int(conc.loc[conc.polo_id == p, "n_locales"].iloc[0]) for p, _ in usadas)

        print("-" * 98)
        print(f"{pid} · {nombre}"
              + ("" if pid in DECLARADOS else "   (se declara en esta tanda)"))
        print("-" * 98)
        print(f"    el contorno publicado      {ha_borde:>9,.2f} ha · {loc_borde:>5} locales")
        print(f"    el barrio administrativo   {gb.area / 1e4:>9,.2f} ha")
        print(f"        del contorno, fuera del barrio: {fuera:>12,.1f} m²   "
              f"del barrio, fuera del contorno: {adentro_no:>12,.1f} m²   "
              f"({coincidencia:.2f} % de coincidencia)")
        print(f"    la concentración adentro   {len(usadas)} pieza(s) "
              f"({', '.join(p for p, _ in usadas)}) · {len(de_la_conc)} locales medidos en el "
              f"universo del atlas")
        print(f"        la capa de concentraciones publica {n_capa} para esas mismas piezas: es "
              f"otro universo y otro recorte, y por eso no coinciden")
        print(f"    el recorte de adentro      {ha_rec:>9,.2f} ha · {loc_rec:>5} locales · "
              f"{n_piezas} pieza(s)")
        print(f"        contiene {contenidos} de los {len(de_la_conc)} locales de la "
              f"concentración")
        print(f"        el polo sería {ha_borde / ha_rec:,.1f} veces más chico que el barrio en "
              f"superficie, y se quedaría con el "
              f"{100 * loc_rec / loc_borde:,.1f} % de sus locales")
        print(f"        el frente más chico de una manzana sobre una cuadra es de "
              f"{frente_min_medido:,.0f} m, así que el umbral de {FRENTE:.0f} m no muerde: "
              f"{muerden} manzanas quedarían fuera aun exigiendo "
              f"{max(SENSIBILIDAD):.0f} m")

        filas.append(dict(
            polo=f"{pid} · {nombre}", polo_id=pid,
            ya_estaba_declarado="si" if pid in DECLARADOS else "no, se declara en esta tanda",
            ha_del_contorno_publicado=round(ha_borde, 2),
            locales_del_contorno_publicado=loc_borde,
            ha_del_recorte_de_adentro=round(ha_rec, 2),
            locales_del_recorte_de_adentro=loc_rec,
            veces_mas_chico_en_superficie=round(ha_borde / ha_rec, 1),
            pct_de_los_locales_que_conserva=round(100 * loc_rec / loc_borde, 1),
            ha_del_barrio_administrativo=round(gb.area / 1e4, 2),
            m2_del_contorno_fuera_del_barrio=round(fuera, 1),
            m2_del_barrio_fuera_del_contorno=round(adentro_no, 1),
            pct_de_coincidencia_con_el_barrio=round(coincidencia, 2),
            concentraciones_usadas=" ".join(p for p, _ in usadas),
            locales_de_la_concentracion=len(de_la_conc),
            locales_que_publica_la_capa_de_concentraciones=n_capa,
            locales_de_la_concentracion_dentro_del_recorte=contenidos,
            piezas_del_recorte=n_piezas,
            frente_mas_chico_medido_m=round(frente_min_medido, 1),
            manzanas_que_perderia_exigiendo_40m=muerden,
        ))
        capa.append(dict(zona_id=pid, nombre=nombre, que_es="recorte de adentro, medido y no "
                                                            "adoptado",
                         ha=round(ha_rec, 2), n_locales=loc_rec, geometry=recorte))

    campos = list(filas[0].keys())
    with (SALIDA / "recorte_de_los_cuatro.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    (SALIDA / "geometria").mkdir(exist_ok=True)
    gpd.GeoDataFrame(capa, geometry="geometry", crs=CRS_M).to_crs(CRS_G).to_file(
        SALIDA / "geometria" / "recorte_de_los_cuatro.geojson", driver="GeoJSON")
    (SALIDA / "recorte_resumen.json").write_text(
        json.dumps(dict(fecha=HOY, frente_minimo_m=FRENTE, filas=filas), ensure_ascii=False,
                   indent=2), encoding="utf-8")

    print("\n" + "=" * 98)
    print("EL CUADRO")
    print("=" * 98)
    print(f"  {'polo':<26}{'contorno ha':>12}{'loc':>6}   {'recorte ha':>11}{'loc':>6}"
          f"{'×':>7}{'% loc':>8}{'piezas':>8}")
    for f in filas:
        print(f"  {f['polo'][:24]:<26}{f['ha_del_contorno_publicado']:>12,.2f}"
              f"{f['locales_del_contorno_publicado']:>6}   "
              f"{f['ha_del_recorte_de_adentro']:>11,.2f}"
              f"{f['locales_del_recorte_de_adentro']:>6}"
              f"{f['veces_mas_chico_en_superficie']:>7,.1f}"
              f"{f['pct_de_los_locales_que_conserva']:>7,.1f} %{f['piezas_del_recorte']:>8}")
    print(f"\nEscrito: recorte_de_los_cuatro.csv ({len(filas)} filas) · "
          f"geometria/recorte_de_los_cuatro.geojson · recorte_resumen.json")


if __name__ == "__main__":
    main()
