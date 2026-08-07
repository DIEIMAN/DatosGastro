"""Los tres conteos de Bares Notables, cerrados: se fusionan los homónimos y manda el Boletín.

QUÉ CIERRA Y QUÉ NO
-------------------
`hitos_cruzar_bares_notables.py` cruzó las tres listas y **no decidió cuál manda**, porque para
decidir hacía falta saber a qué fecha está cada una y contra qué acto administrativo. Diego lo
decidió el 2026-08-07, y esta corrida lo aplica:

  a) los pares de homónimos con la **misma altura** son el mismo bar y se fusionan;
  b) manda la lista del **BOLETÍN OFICIAL**, que es la declaratoria;
  c) lo que queda fuera del canon **no se descarta**: se anota aparte, con su origen.

LO QUE ESTA CORRIDA AVISA ANTES DE CORRER, Y ESTÁ EN `LECTURA_PREVIA.md` §6
----------------------------------------------------------------------------
El enunciado predice que «en las tres listas» pasa de 70 a 74. Mirando el cruce ya escrito, eso
**no puede dar 74**: los «4 pares» impresos son **3 bares** —Café Palacio sale en dos líneas
porque la entidad ya fusionada tiene dos nombres— y de los tres sólo Café Palacio queda en las
tres listas. Bar Bidou junta Wikidata + Boletín y El Preferido de Palermo junta GCBA + Wikidata:
dos listas cada uno. La corrida mide y reporta lo que salga, bar por bar. Si el número no es el
predicho, el número manda.

LA REGLA DE FUSIÓN, DECLARADA
------------------------------
Pasada 2b, nueva: **mismo nombre plegado + misma altura, aunque la calle no matchee**. Es la que
Diego autorizó, y no es un descubrimiento de esta corrida: los cuatro pares ya estaban impresos y
revisados uno por uno. Cada fusión imprime **la equivalencia de calles que implica**, porque son
justo el residuo abierto de `normalizar_calles.py` —las iniciales— más un sinónimo de verdad
(Roque Sáenz Peña = Diagonal Norte, que son la misma calle con dos nombres).

EL CANON NECESITA COORDENADAS Y NO TODAS ESTÁN
-----------------------------------------------
El Boletín trae dirección, no punto. Los que ya están en el catálogo del GCBA heredan su
coordenada —ya geocodificada con USIG— y el resto se geocodifica con USIG, que es el
geocodificador oficial, gratuito y sin credenciales. **Google Places: 0 requests.**

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/hitos_cerrar_bares_notables.py
"""
from __future__ import annotations

import io
import json
import re
import sys
import unicodedata
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset_bares_notables import CACHE, consultar, limpiar  # noqa: E402
from hitos_cruzar_bares_notables import (  # noqa: E402
    cargar,
    clave_domicilio,
    plegar_nombre,
)

# Vive dentro del `main()` del cruce y no se puede importar. Se repite con su valor y su motivo:
# «36 Billares» está en Av. de Mayo 1262 y 1265 según quién lo cargó. Si allá cambia, acá también.
TOLERANCIA_ALTURA = 50

OUT = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "hitos"
REFERENTES = ROOT / "outputs" / "polos_gastro" / "REFERENTES_2026" / "matriz_referentes_final_2026.csv"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    listas = cargar()
    for nombre, tabla in listas.items():
        tabla["clave_dom"] = tabla.direccion.map(clave_domicilio)
        tabla["clave_nom"] = tabla.nombre.map(plegar_nombre)
        tabla["lista"] = nombre

    todas = pd.concat(listas.values(), ignore_index=True).reset_index(drop=True)
    padre = list(range(len(todas)))

    def raiz(i):
        while padre[i] != i:
            padre[i] = padre[padre[i]]
            i = padre[i]
        return i

    motivos: dict[int, set[str]] = {}

    def unir(a, b, motivo):
        ra, rb = raiz(a), raiz(b)
        if ra == rb:
            return False
        padre[rb] = ra
        motivos.setdefault(ra, set()).add(motivo)
        motivos[ra] |= motivos.pop(rb, set())
        return True

    def calle_y_altura(indice):
        calle, alt = todas.clave_dom[indice].split("|")
        return frozenset(calle.split()), int(alt)

    def misma_calle(i, j):
        a, b = calle_y_altura(i)[0], calle_y_altura(j)[0]
        return bool(a) and bool(b) and (a <= b or b <= a)

    con_domicilio = [i for i in range(len(todas)) if todas.clave_dom[i]]

    # 1 · misma calle (por contención) y misma altura.
    for a in range(len(con_domicilio)):
        for b in range(a + 1, len(con_domicilio)):
            i, j = con_domicilio[a], con_domicilio[b]
            if raiz(i) != raiz(j) and calle_y_altura(i)[1] == calle_y_altura(j)[1] \
                    and misma_calle(i, j):
                unir(i, j, "domicilio")

    # 2 · mismo nombre plegado, misma calle, altura a menos de TOLERANCIA_ALTURA.
    con_nombre: dict[str, list[int]] = {}
    for i in con_domicilio:
        if todas.clave_nom[i]:
            con_nombre.setdefault(todas.clave_nom[i], []).append(i)
    for indices in con_nombre.values():
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                i, j = indices[a], indices[b]
                if raiz(i) != raiz(j) and misma_calle(i, j) and abs(
                        calle_y_altura(i)[1] - calle_y_altura(j)[1]) <= TOLERANCIA_ALTURA:
                    unir(i, j, "nombre+calle")

    # 2b · LA PASADA NUEVA · mismo nombre plegado y MISMA altura con la calle escrita distinto.
    #      Autorizada caso por caso: los cuatro pares estaban impresos y revisados.
    fusiones_nuevas = []
    equivalencias = []
    for indices in con_nombre.values():
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                i, j = indices[a], indices[b]
                if raiz(i) == raiz(j) or misma_calle(i, j):
                    continue
                if calle_y_altura(i)[1] != calle_y_altura(j)[1]:
                    continue
                antes_i = {m for m in todas.lista[[k for k in range(len(todas))
                                                   if raiz(k) == raiz(i)]]}
                antes_j = {m for m in todas.lista[[k for k in range(len(todas))
                                                   if raiz(k) == raiz(j)]]}
                if unir(i, j, "nombre+altura (homonimo cerrado)"):
                    fusiones_nuevas.append({
                        "bar": str(todas.nombre[i]),
                        "a": f"{todas.nombre[i]} ({todas.direccion[i]})",
                        "b": f"{todas.nombre[j]} ({todas.direccion[j]})",
                        "listas_antes_a": "+".join(sorted(antes_i)),
                        "listas_antes_b": "+".join(sorted(antes_j)),
                        "listas_despues": "+".join(sorted(antes_i | antes_j)),
                    })
                    equivalencias.append((
                        " ".join(sorted(calle_y_altura(i)[0])),
                        " ".join(sorted(calle_y_altura(j)[0]))))

    # 3 · sin domicilio utilizable: sólo queda el nombre.
    primero_con_nombre = {}
    for i, fila in todas.iterrows():
        if fila.clave_dom and fila.clave_nom:
            primero_con_nombre.setdefault(fila.clave_nom, i)
    for i, fila in todas.iterrows():
        if fila.clave_dom or not fila.clave_nom:
            continue
        destino = primero_con_nombre.get(fila.clave_nom)
        if destino is not None:
            unir(destino, i, "solo nombre")

    grupos: dict[int, list] = {}
    for i in range(len(todas)):
        grupos.setdefault(raiz(i), []).append(todas.iloc[i])

    filas = []
    for indice, miembros in grupos.items():
        presentes = {m.lista for m in miembros}
        por_lista = {m.lista: m for m in miembros}
        filas.append({
            "bar": sorted({m.nombre for m in miembros}, key=len)[0],
            "nombres_vistos": " | ".join(sorted({str(m.nombre) for m in miembros})),
            "direcciones_vistas": " | ".join(
                sorted({str(m.direccion) for m in miembros if pd.notna(m.direccion)})),
            "direccion_boletin": str(por_lista["BOLETIN_90"].direccion)
            if "BOLETIN_90" in por_lista else "",
            "id_boletin": str(por_lista["BOLETIN_90"].id) if "BOLETIN_90" in por_lista else "",
            "nombre_gcba": str(por_lista["GCBA_84"].nombre) if "GCBA_84" in por_lista else "",
            "direccion_gcba": str(por_lista["GCBA_84"].direccion) if "GCBA_84" in por_lista else "",
            "en_GCBA_84": "si" if "GCBA_84" in presentes else "no",
            "en_WIKIDATA_95": "si" if "WIKIDATA_95" in presentes else "no",
            "en_BOLETIN_90": "si" if "BOLETIN_90" in presentes else "no",
            "n_listas": len(presentes),
            "emparejado_por": "+".join(sorted(motivos.get(indice, {"unico"}))) or "unico",
        })
    cruce = pd.DataFrame(filas).sort_values(
        ["n_listas", "bar"], ascending=[False, True]).reset_index(drop=True)

    previo = pd.read_csv(OUT / "cruce_bares_notables.csv")
    tres_antes = int((previo.n_listas == 3).sum())
    tres_ahora = int((cruce.n_listas == 3).sum())

    p("BARES NOTABLES · los homónimos cerrados y el Boletín como declaratoria")
    p("=" * 100)
    p("")
    p("-" * 100)
    p("  a · LAS FUSIONES NUEVAS · mismo nombre, misma altura, calle escrita distinto")
    p("")
    p(f"      pares fusionados: {len(fusiones_nuevas)}   (el enunciado hablaba de 4 líneas)")
    p("")
    for f in fusiones_nuevas:
        p(f"      {f['a']}")
        p(f"          +  {f['b']}")
        p(f"          {f['listas_antes_a']}  +  {f['listas_antes_b']}  →  {f['listas_despues']}")
        p("")
    p("      LA EQUIVALENCIA DE CALLES QUE CADA FUSIÓN IMPLICA, que es dato para el normalizador:")
    for a, b in sorted(set(equivalencias)):
        p(f"          «{a}»  =  «{b}»")
    p("")
    p("      Las de iniciales —F LACROZE / FEDERICO LACROZE, J L BORGES / JORGE LUIS BORGES— son")
    p("      el residuo que `normalizar_calles.py` declara abierto y que espera callejero. La de")
    p("      Roque Sáenz Peña / Diagonal Norte NO es residuo: son dos nombres oficiales de la")
    p("      misma calle, y ninguna regla de tokens la va a cerrar nunca. Es tabla, no regla.")
    p("")
    p("-" * 100)
    p("  EL NÚMERO, CONTRA EL PREDICHO")
    p("")
    p(f"      bares distintos         {len(previo)}  →  {len(cruce)}")
    p(f"      en las TRES listas      {tres_antes}  →  {tres_ahora}      (el enunciado predecía 74)")
    p("")
    if tres_ahora != 74:
        p("      NO da 74, y el motivo estaba escrito antes de correr. De los tres bares")
        p("      fusionados sólo uno queda en las tres listas; los otros dos juntan dos listas")
        p("      cada uno. Las cuatro líneas impresas eran tres bares.")
    else:
        p("      Da 74, como predecía el enunciado.")
    p("")

    combinaciones = cruce.groupby(
        ["en_GCBA_84", "en_WIKIDATA_95", "en_BOLETIN_90"]).size().sort_values(ascending=False)
    p("      GCBA  WIKI  BOLETIN   bares")
    for (g, w, b), n in combinaciones.items():
        marca = "  ← en las tres" if g == w == b == "si" else ""
        p(f"      {g:<5} {w:<5} {b:<9} {n:>3}{marca}")
    p("")

    # ------------------------------------------------------------------ b · el canon
    canon = cruce[cruce.en_BOLETIN_90 == "si"].copy().reset_index(drop=True)
    fuera = cruce[cruce.en_BOLETIN_90 == "no"].copy().reset_index(drop=True)

    p("-" * 100)
    p("  b · EL CANON · manda el BOLETÍN OFICIAL, que es la declaratoria")
    p("")
    p(f"      en el canon:   {len(canon)}")
    p(f"      fuera:         {len(fuera)}   — NO se descartan; van anotados con su origen")
    p("")
    solo_wiki = fuera[(fuera.en_WIKIDATA_95 == "si") & (fuera.en_GCBA_84 == "no")]
    solo_gcba = fuera[(fuera.en_GCBA_84 == "si") & (fuera.en_WIKIDATA_95 == "no")]
    ambas = fuera[(fuera.en_GCBA_84 == "si") & (fuera.en_WIKIDATA_95 == "si")]
    p(f"      · sólo Wikidata      {len(solo_wiki):>2}   (eran 11 antes de las fusiones)")
    for fila in solo_wiki.itertuples():
        p(f"            {fila.bar}  —  {fila.direcciones_vistas or 'sin dirección'}")
    p("")
    p(f"      · sólo GCBA          {len(solo_gcba):>2}   el enunciado no los nombra, y también")
    p("                              quedan fuera del canon: el catálogo del GCBA es oficial")
    p("                              pero no es la declaratoria")
    for fila in solo_gcba.itertuples():
        p(f"            {fila.bar}  —  {fila.direcciones_vistas or 'sin dirección'}")
    p("")
    p(f"      · GCBA + Wikidata    {len(ambas):>2}   dos fuentes coinciden y el Boletín no los tiene:")
    p("                              son los que más merecen que alguien mire el acto")
    for fila in ambas.itertuples():
        p(f"            {fila.bar}  —  {fila.direcciones_vistas or 'sin dirección'}")
    p("")

    # ------------------------------------------------------------------ coordenadas del canon
    referentes = pd.read_csv(REFERENTES, comment="#")
    referentes = referentes[referentes.tipo == "Bar Notable"]
    coord_gcba = {}
    for fila in referentes.itertuples():
        coord_gcba[str(fila.nombre)] = (fila.latitud, fila.longitud)

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    heredadas = geocodificadas = sin_punto = 0
    latitudes, longitudes, origen_punto = [], [], []
    fallidas = []
    for fila in canon.itertuples():
        lat = lon = None
        origen = ""
        if fila.nombre_gcba and fila.nombre_gcba in coord_gcba:
            lat, lon = coord_gcba[fila.nombre_gcba]
            if pd.notna(lat) and pd.notna(lon):
                origen = "REFERENTES_2026 (GCBA, ya geocodificado)"
                heredadas += 1
            else:
                lat = lon = None
        if lat is None and fila.direccion_boletin and fila.direccion_boletin != "nan":
            candidato = consultar(limpiar(fila.direccion_boletin), cache)
            if candidato and candidato.get("coordenadas"):
                lat = float(candidato["coordenadas"]["y"])
                lon = float(candidato["coordenadas"]["x"])
                origen = "USIG sobre la dirección del Boletín"
                geocodificadas += 1
            else:
                fallidas.append(f"{fila.bar} — {fila.direccion_boletin}")
        if lat is None:
            sin_punto += 1
            origen = origen or "sin coordenada"
        latitudes.append(lat)
        longitudes.append(lon)
        origen_punto.append(origen)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

    canon["latitud"] = latitudes
    canon["longitud"] = longitudes
    canon["origen_punto"] = origen_punto

    p("-" * 100)
    p("  LAS COORDENADAS DEL CANON · USIG, cero requests pagos")
    p("")
    p(f"      heredadas del catálogo del GCBA   {heredadas:>3}")
    p(f"      geocodificadas con USIG           {geocodificadas:>3}")
    p(f"      sin coordenada                    {sin_punto:>3}")
    for texto in fallidas:
        p(f"            no resolvió: {texto}")
    p("")
    if canon.latitud.notna().sum() == 0:
        p("      CORTE R8: la columna `latitud` llegó vacía en el 100 % de las filas.")
        p("      No se reporta ningún resultado sobre ella.")
        (OUT / "CIERRE_BARES_NOTABLES.txt").write_text(buffer.getvalue(), encoding="utf-8")
        print(buffer.getvalue())
        return 1

    canon.to_csv(OUT / "bares_notables_canon_boletin.csv", index=False, encoding="utf-8")
    fuera.to_csv(OUT / "bares_notables_fuera_del_canon.csv", index=False, encoding="utf-8")
    cruce.to_csv(OUT / "cruce_bares_notables_cerrado.csv", index=False, encoding="utf-8")
    pd.DataFrame(fusiones_nuevas).to_csv(
        OUT / "fusiones_homonimos_misma_altura.csv", index=False, encoding="utf-8")

    p("=" * 100)
    p(f"  canon {len(canon)} bares ({int(canon.latitud.notna().sum())} con punto) · "
      f"fuera del canon {len(fuera)} anotados · en las tres {tres_ahora} · Places: 0 requests")
    p("=" * 100)
    p("")

    (OUT / "CIERRE_BARES_NOTABLES.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
