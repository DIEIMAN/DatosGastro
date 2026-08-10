# -*- coding: utf-8 -*-
"""Av. Montes de Oca medida con las seis vias, como cualquier zona nueva.

POR QUE
-------
Diego la incorporo el 09/08 como la referencia 42 y su ficha ya esta escrita, apoyada en
trayectoria, anclaje normativo (Res. 65/SSADMIN/2017) y reconocimiento externo. La propia ficha
declara lo que falta: *"queda pendiente medirla con las seis vias como a cualquier otra zona: lo
que esta escrito aca se apoya en [...] documentos, no en un conteo propio"*. Esto es ese conteo.

EL SOPORTE, Y EL LIO DE IDENTIFICADORES
----------------------------------------
En la capa de las 124 este corredor es **P066 · "Av. Montes de Oca"**, 65 locales en 18,02 ha,
Barracas. **No es P008.** El id P008 designa dos cosas segun que archivo se abra —"Distrito de
Diseño (Barracas)" en `POLOS_NOMBRADOS.csv` y "Barracas · Av. Montes de Oca" en el modelo de
ficha—, y esa colision es ERR-11, que sale del mapeo 124 x 42. Aca no se resuelve: se usa P066 y
se deja dicho por que.

Y no es un detalle: los dos son de Barracas, los dos son plausibles, y **P008 tiene 49 locales en
otras calles** —Vieytes, Iriarte, San Antonio, California—. Medir P008 creyendo que es este
corredor devolveria numeros perfectamente formados de otro objeto.

LAS DOS FAMILIAS DE VIAS
-------------------------
`CRITERIO_ESCALA_DE_LAS_VIAS.md` (07/08): A, C y F se miden sobre el poligono; B, D y E sobre la
zona, y las filas las heredan. Aca se reportan las dos escalas —el poligono P066 y el barrio de
Barracas— porque para una referencia que se publica como corredor la diferencia entre las dos
escalas ES el resultado: si un hito abre la via a escala de barrio pero cae a 800 m del corredor,
eso hay que verlo.

LO QUE ESTA CORRIDA NO HACE
----------------------------
**No mide la continuidad de la oferta sobre la avenida entre el 280 y el 1702.** Esa es la curva de
continuidad que reemplaza a la caminata, y la esta haciendo Codex en paralelo. La columna de
continuidad que si aparece aca es la de la via A —componente conexa de la nube de puntos DENTRO del
poligono, a 60 m—, que es otra cosa y se llama distinto a proposito.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import math
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"

POLO = "P066"
BARRIO_ZONA = "Barracas"
HITOS = BASE / "hitos" / "hitos_capa_2026_r11.csv"
PUBLICABLES = BASE / "borrador_polos" / "polos_publicables.geojson"

# Los cortes de LECTURA_PREVIA.md, fijados en la ronda 2 y no se tocan.
CONTINUIDAD_M = 60
CURVA_CONTINUIDAD_M = (20, 40, 60, 80, 120)
BANDA_M = 100
CURVA_BANDA_M = (50, 75, 100, 150, 200)
PERTENENCIA_MIN = 0.50
CURVA_PERTENENCIA = (0.25, 0.50, 0.75, 1.00)
MUESTRA_MINIMA = 20
CORTE_ELONGACION = 2.0


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def componente_mayor(coords, umbral):
    """% de puntos en la componente conexa mayor, uniendo lo que este a <= umbral."""
    n = len(coords)
    if n == 0:
        return float("nan")
    vistos, mayor = set(), 0
    for i in range(n):
        if i in vistos:
            continue
        pila, grupo = [i], set()
        while pila:
            k = pila.pop()
            if k in grupo:
                continue
            grupo.add(k)
            vistos.add(k)
            xk, yk = coords[k]
            for j in range(n):
                if j in grupo:
                    continue
                dx, dy = coords[j][0] - xk, coords[j][1] - yk
                if dx * dx + dy * dy <= umbral * umbral:
                    pila.append(j)
        mayor = max(mayor, len(grupo))
    return mayor / n * 100


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
    from polos_soporte import (puntos_base, barrios, construir_enclaves, sin_tildes,  # noqa: E402
                               PERTENENCIA)

    puntos = puntos_base()
    polos = gpd.read_file(PUBLICABLES).to_crs(CRS_METRICO).set_index("polo_id")
    soporte = limpia(polos.geometry.loc[POLO])
    capa_barrios = barrios().set_index("clave")
    zona = limpia(capa_barrios.geometry.loc[sin_tildes(BARRIO_ZONA)])

    filas = []

    def anota(via, escala, medida, valor, abre="", nota=""):
        filas.append(dict(via=via, escala=escala, medida=medida, valor=valor, abre=abre, nota=nota))

    print("=" * 92)
    print(f"AV. MONTES DE OCA · las seis vias · soporte {POLO} de la capa de las 124")
    print("=" * 92)
    ha = soporte.area / 10_000
    dentro = puntos[puntos.within(soporte)]
    print(f"\nsoporte: {ha:,.2f} ha · {len(dentro)} locales · {len(dentro) / ha:,.2f} loc/ha")
    print(f"zona de herencia: barrio de {BARRIO_ZONA}, "
          f"{zona.area / 10_000:,.2f} ha · {int(puntos.within(zona).sum())} locales")
    anota("—", "poligono", "hectareas", round(ha, 2), "", f"{POLO}, no P008 (ver ERR-11)")
    anota("—", "poligono", "locales", len(dentro))
    anota("—", "zona", "hectareas del barrio", round(zona.area / 10_000, 2))
    anota("—", "zona", "locales del barrio", int(puntos.within(zona).sum()))

    # ---- via A · densidad y continuidad ---------------------------------------------------
    print("\n" + "-" * 92)
    print("VIA A · densidad y continuidad · se mide sobre el poligono")
    print("-" * 92)
    coords = [(p.x, p.y) for p in dentro.geometry]
    print(f"  locales por hectarea: {len(dentro) / ha:,.2f}")
    print(f"  continuidad de la NUBE DE PUNTOS (no del corredor sobre la avenida):")
    for umbral in CURVA_CONTINUIDAD_M:
        marca = "  <<< el declarado" if umbral == CONTINUIDAD_M else ""
        pct = componente_mayor(coords, umbral)
        print(f"     a {umbral:>4} m: {pct:5.1f} % en la componente mayor{marca}")
        anota("A", "poligono", f"componente mayor a {umbral} m", f"{pct:.1f} %", "",
              "curva declarada en LECTURA_PREVIA; NO es la continuidad del corredor")

    pert = pd.read_csv(PERTENENCIA)
    col_polo = "polo_id" if "polo_id" in pert.columns else pert.columns[1]
    puntos_ix = puntos.reset_index(drop=True)
    dentro_ix = set(puntos_ix.index[puntos_ix.within(soporte)])
    print(f"\n  regla de apertura: algun polo del borrador con >= "
          f"{PERTENENCIA_MIN:.0%} de sus locales dentro del soporte")
    abre_a, detalle_a = False, []
    if "local_id" in pert.columns and "local_id" in puntos_ix.columns:
        idx_por_local = {lid: i for i, lid in enumerate(puntos_ix["local_id"])}
        for pid, grupo in pert.groupby(col_polo):
            ids = [idx_por_local.get(x) for x in grupo["local_id"]]
            ids = [i for i in ids if i is not None]
            if not ids:
                continue
            frac = sum(1 for i in ids if i in dentro_ix) / len(ids)
            if frac >= 0.25:
                detalle_a.append((pid, len(ids), frac))
        detalle_a.sort(key=lambda t: -t[2])
        for pid, n, frac in detalle_a[:5]:
            print(f"     {pid:<12}{n:>5} locales · {frac:6.1%} dentro")
        abre_a = any(f >= PERTENENCIA_MIN for _, _, f in detalle_a)
        for corte in CURVA_PERTENENCIA:
            cuantos = sum(1 for _, _, f in detalle_a if f >= corte)
            anota("A", "poligono", f"polos con >= {corte:.0%} de pertenencia", cuantos)
    else:
        print("     no se pudo cruzar la pertenencia: faltan columnas de union")
    veredicto_a = "ABRE" if abre_a else "no abre"
    print(f"  -> via A: {veredicto_a}")
    print("     SALVEDAD: el soporte ES un polo del borrador, asi que la regla se cumple sola.")
    print("     Lo que informa de verdad son la densidad y la continuidad de arriba.")
    anota("A", "poligono", "veredicto", veredicto_a, veredicto_a,
          "tautologico: el soporte es un polo del borrador y contiene el 100 % de sus locales")

    # ---- via B · trayectoria · las dos escalas ---------------------------------------------
    print("\n" + "-" * 92)
    print("VIA B · trayectoria e instituciones · se mide sobre la ZONA y la fila la hereda")
    print("-" * 92)
    hitos = pd.read_csv(HITOS)
    con_punto = hitos.dropna(subset=["latitud", "longitud"]).copy()
    geo_hitos = gpd.GeoDataFrame(
        con_punto, geometry=gpd.points_from_xy(con_punto.longitud, con_punto.latitud),
        crs="EPSG:4326").to_crs(CRS_METRICO)
    print(f"  capa de hitos: {len(hitos)} filas, {len(geo_hitos)} con punto "
          f"({len(hitos) - len(geo_hitos)} sin coordenada: no se ubican en el centroide de nada)")
    en_zona = geo_hitos[geo_hitos.within(zona)]
    en_poligono = geo_hitos[geo_hitos.within(soporte)]
    print(f"\n  hitos en el barrio de {BARRIO_ZONA}: {len(en_zona)} · "
          f"dentro del poligono: {len(en_poligono)}\n")
    print(f"  {'hito':<34}{'tipo':<22}{'dentro de P066':>16}{'distancia':>11}")
    for h in en_zona.itertuples():
        d = soporte.distance(h.geometry)
        print(f"  {str(h.nombre)[:33]:<34}{str(h.tipo)[:21]:<22}"
              f"{('SI' if d == 0 else 'no'):>16}{d:>9,.0f} m")
        anota("B", "zona", f"hito · {h.nombre}", h.tipo, "SI" if d == 0 else "no",
              f"a {d:,.0f} m del poligono; direccion: {h.direccion}")
    abre_b = len(en_zona) >= 1
    print(f"\n  -> via B: {'ABRE' if abre_b else 'no abre'} a escala de zona · "
          f"{'ABRE' if len(en_poligono) else 'no abre'} por contencion en el poligono")
    anota("B", "zona", "veredicto", "ABRE" if abre_b else "no abre",
          "ABRE" if abre_b else "no abre",
          f"{len(en_zona)} hitos en el barrio, {len(en_poligono)} dentro del poligono")

    # ---- via C · mercados y centralidades ----------------------------------------------------
    print("\n" + "-" * 92)
    print("VIA C · mercados, patios y galerias EN ACTIVIDAD · se mide sobre el poligono")
    print("-" * 92)
    mercados = geo_hitos[geo_hitos.tipo.astype(str).str.contains("Mercado|patio", case=False,
                                                                 na=False)]
    sin_punto = hitos[hitos.tipo.astype(str).str.contains("Mercado|patio", case=False, na=False)]
    print(f"  la capa tiene {len(sin_punto)} de tipo Mercado/patio y {len(mercados)} con punto")
    adentro = mercados[mercados.within(soporte)]
    if len(adentro):
        for m in adentro.itertuples():
            print(f"     DENTRO: {m.nombre} ({m.direccion})")
    else:
        cercanos = sorted(((soporte.distance(m.geometry), m.nombre, m.direccion)
                           for m in mercados.itertuples()))[:3]
        print("     ninguno cae dentro del poligono. Los mas cercanos:")
        for d, nombre, direccion in cercanos:
            print(f"       {nombre} ({direccion}) a {d:,.0f} m")
            anota("C", "poligono", f"mercado mas cercano · {nombre}", f"{d:,.0f} m", "",
                  str(direccion))
    abre_c = len(adentro) >= 1
    print(f"  -> via C: {'ABRE' if abre_c else 'NO ABRE'}")
    anota("C", "poligono", "veredicto", "ABRE" if abre_c else "no abre",
          "ABRE" if abre_c else "no abre",
          "la decision 1 del 07/08 exige mercado, patio o galeria EN ACTIVIDAD y nombrado")

    # ---- via D · comunidades y especializacion ------------------------------------------------
    print("\n" + "-" * 92)
    print("VIA D · comunidades y especializacion · enclaves con delimitacion documentada")
    print("-" * 92)
    enclaves, _ = construir_enclaves()
    abre_d = False
    for e in enclaves.itertuples():
        d = soporte.distance(e.geometry)
        toca = d == 0
        abre_d = abre_d or toca
        print(f"  {e.enclave:<38}{'INTERSECTA' if toca else 'no toca':>12}{d:>10,.0f} m")
        anota("D", "poligono", f"enclave · {e.enclave}", "intersecta" if toca else "no toca",
              "", f"a {d:,.0f} m")
    print(f"  -> via D: {'ABRE' if abre_d else 'NO ABRE'}")
    anota("D", "poligono", "veredicto", "ABRE" if abre_d else "no abre",
          "ABRE" if abre_d else "no abre", "los cuatro enclaves de la ronda 3, buffer 150 m")

    # ---- via E · reconocimiento externo -------------------------------------------------------
    print("\n" + "-" * 92)
    print("VIA E · reconocimiento externo · NO se mide desde el repositorio")
    print("-" * 92)
    print("  La via E la llena el trabajo documental: no se estima, no se infiere, no se rellena")
    print("  con proxies. La ficha ya la declara abierta con prensa nacional y el sitio oficial de")
    print("  turismo tratando el corredor como circuito. Esta corrida NO la vuelve a juzgar.")
    anota("E", "zona", "veredicto", "declarada ABRE en la ficha", "ABRE (documental)",
          "prensa nacional + sitio oficial de turismo; el repositorio no mide esta via")

    # ---- via F · corredor ----------------------------------------------------------------------
    print("\n" + "-" * 92)
    print("VIA F · corredor · elongacion de la nube de puntos, corte declarado 2,0")
    print("-" * 92)
    if len(dentro) < MUESTRA_MINIMA:
        print(f"  menos de {MUESTRA_MINIMA} puntos: el eje principal seria ruido. NA declarado.")
        abre_f, elong = False, float("nan")
    else:
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        sxx = sum((x - mx) ** 2 for x in xs) / len(xs)
        syy = sum((y - my) ** 2 for y in ys) / len(ys)
        sxy = sum((x - mx) * (y - my) for x, y in coords) / len(coords)
        traza, det = sxx + syy, sxx * syy - sxy * sxy
        raiz = math.sqrt(max(traza * traza / 4 - det, 0))
        l1, l2 = traza / 2 + raiz, traza / 2 - raiz
        elong = math.sqrt(l1) / math.sqrt(l2) if l2 > 0 else float("inf")
        # el eje principal, para la banda y el largo
        ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
        ux, uy = math.cos(ang), math.sin(ang)
        sobre = [((x - mx) * ux + (y - my) * uy) for x, y in coords]
        perp = [abs(-(x - mx) * uy + (y - my) * ux) for x, y in coords]
        perp_ord = sorted(perp)
        largo = max(sobre) - min(sobre)
        p5 = sorted(sobre)[int(0.05 * (len(sobre) - 1))]
        p95 = sorted(sobre)[int(0.95 * (len(sobre) - 1))]
        ancho_p80 = perp_ord[int(0.80 * (len(perp_ord) - 1))]
        rect = soporte.minimum_rotated_rectangle
        lados = [rect.exterior.coords[i] for i in range(5)]
        largos = sorted(
            math.dist(lados[i], lados[i + 1]) for i in range(4))
        elong_rect = largos[-1] / largos[0] if largos[0] else float("inf")
        print(f"  elongacion de los puntos (sigma1/sigma2): {elong:,.2f}   "
              f"corte declarado {CORTE_ELONGACION}")
        print(f"  elongacion del rectangulo rotado minimo:  {elong_rect:,.2f}")
        print(f"  largo p5-p95: {p95 - p5:,.0f} m · largo total {largo:,.0f} m · "
              f"ancho p80 {ancho_p80:,.0f} m")
        print("  fraccion de puntos dentro de la banda del eje:")
        for banda in CURVA_BANDA_M:
            frac = sum(1 for p in perp if p <= banda) / len(perp)
            marca = "  <<< el declarado" if banda == BANDA_M else ""
            print(f"     a {banda:>4} m: {frac:5.1%}{marca}")
            anota("F", "poligono", f"fraccion en banda de {banda} m", f"{frac:.1%}")
        abre_f = elong >= CORTE_ELONGACION
        for clave, valor in [("elongacion de los puntos", round(elong, 2)),
                             ("elongacion del rectangulo", round(elong_rect, 2)),
                             ("largo p5-p95 (m)", round(p95 - p5)),
                             ("ancho p80 (m)", round(ancho_p80))]:
            anota("F", "poligono", clave, valor)
    print(f"  -> via F: {'ABRE' if abre_f else 'NO ABRE'}")
    anota("F", "poligono", "veredicto", "ABRE" if abre_f else "no abre",
          "ABRE" if abre_f else "no abre", f"corte declarado {CORTE_ELONGACION}, no se mueve")

    # ---- que tramo de la avenida cubre el poligono -------------------------------------------
    #
    # La ficha publica "oferta documentada entre el 280 y el 1702". Eso NO se comprueba aca —la
    # continuidad de la oferta es la curva que esta haciendo Codex—, pero si se puede contestar
    # una pregunta distinta y previa: **que alturas de la avenida cubre el poligono que se publica
    # como este corredor.** Si el poligono cubriera 400 metros y la ficha anunciara 1.400, el
    # problema no seria de continuidad sino de que estan describiendo objetos de distinto largo.
    print("\n" + "-" * 92)
    print("EL TRAMO DE LA AVENIDA QUE EL POLIGONO CUBRE · contra el 280-1702 que anuncia la ficha")
    print("-" * 92)
    from callejero_canonico import cargar, familias  # noqa: E402
    calles = cargar()
    mapa = familias(calles)
    # El callejero la escribe «MONTES DE OCA, MANUEL AV.» — con el nombre de pila en el medio—, y
    # buscarla como «Montes de Oca Av.» devuelve VACIO sin tirar ningun error. Es el mismo bicho de
    # orden de tokens que ya esta registrado como R8 y que la ronda 9 encontro con «ARENAL,
    # CONCEPCION». Aparece tambien, y publicado, en las calles dominantes de P066 en
    # POLOS_NOMBRADOS.csv: «Montes De Oca (9); Manuel Montes De Oca (2)» son la misma avenida
    # contada dos veces — el bug del normalizador que la ronda 12 dejo anotado en 9 de los 124.
    claves = mapa.get("MONTES DE OCA MANUEL AV", {"MONTES DE OCA MANUEL AV"})
    eje = calles[calles.clave.isin(claves)]
    if eje.empty:
        raise SystemExit("la avenida no aparece en el callejero con esa clave: se declara y se para")
    print(f"  la avenida en el callejero: {' + '.join(sorted(claves))} · "
          f"{len(eje)} cuadras · {limpia(unary_union(list(eje.geometry))).length:,.0f} m")
    tocadas = eje[eje.geometry.intersects(soporte)]
    if len(tocadas):
        alturas = [a for a in list(tocadas.alt_derini) + list(tocadas.alt_derfin) if a > 0]
        print(f"  cuadras que el poligono toca: {len(tocadas)} · "
              f"alturas {min(alturas):.0f} a {max(alturas):.0f}")
        dentro_m = limpia(unary_union(list(tocadas.geometry))).intersection(soporte).length
        print(f"  metros de avenida DENTRO del poligono: {dentro_m:,.0f} m")
        anota("—", "poligono", "tramo de Av. Montes de Oca cubierto",
              f"{min(alturas):.0f}-{max(alturas):.0f}", "",
              f"{dentro_m:,.0f} m de avenida dentro del poligono; la ficha anuncia 280-1702")
        # a que distancia quedan los dos extremos que anuncia la ficha
        for altura in (280, 1702):
            cuadra = eje[((eje.alt_derini <= altura) & (eje.alt_derfin >= altura)) |
                         ((eje.alt_izqini <= altura) & (eje.alt_izqfin >= altura))]
            if len(cuadra):
                g = limpia(unary_union(list(cuadra.geometry)))
                d = soporte.distance(g)
                print(f"  la cuadra del {altura} esta a {d:,.0f} m del poligono "
                      f"({'dentro' if d == 0 else 'FUERA'})")
                anota("—", "poligono", f"extremo declarado por la ficha · altura {altura}",
                      f"{d:,.0f} m", "", "dentro" if d == 0 else "fuera del poligono publicado")
            else:
                print(f"  la altura {altura} no cae en ninguna cuadra del callejero")

    # ---- el resumen ------------------------------------------------------------------------
    print("\n" + "=" * 92)
    veredictos = {"A": abre_a, "B": abre_b, "C": abre_c, "D": abre_d, "F": abre_f}
    abiertas = [v for v, ok in veredictos.items() if ok]
    print(f"AV. MONTES DE OCA abre {len(abiertas)} de las 5 vias medibles: "
          f"{', '.join(abiertas) if abiertas else 'ninguna'}")
    print(f"  mas la via E, declarada abierta por la ficha y no medida aca.")
    print("=" * 92)
    anota("—", "resumen", "vias medibles abiertas", f"{len(abiertas)} de 5",
          ", ".join(abiertas), "la via E es documental y no la mide el repositorio")

    destino = SALIDA / "montes_de_oca_seis_vias.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["via", "escala", "medida", "valor", "abre", "nota"])
        w.writeheader()
        w.writerows(filas)
    print(f"\nEscrito: {destino.name} ({len(filas)} filas)")


if __name__ == "__main__":
    main()
