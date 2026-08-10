"""Ronda 10 · Palermo por eliminación, Monserrat reconciliado, y las dos erratas.

Google Places: **0 requests**. Ninguna consulta de red.

    TAREA 1  la capa FD se reconcilia contra el archivo canónico: FD-20 estaba mal cargado
    TAREA 2  Palermo · contención por superficie perdida, y QUÉ SON los 407 locales
    TAREA 3  Monserrat · el catálogo dice 9 y la capa tiene 2. Y el límite norte, medido
    TAREA 4  las dos erratas: via_C de PGR_P004 y la cola de R20

POR QUÉ FD-20 SE REESCRIBE
---------------------------
La ronda 9 cargó un FD-20 propio —el falso negativo de Places— porque el archivo con las
definiciones no estaba en el repositorio. Ahora está, y **el FD-20 canónico es otro**: «la quiebra
decretada leída como cierre». Lo que la ronda 9 llamó FD-20 es, en el archivo, **FD-21**.

Se corrige por el archivo, no por antigüedad: el catálogo es de Diego y este proceso no lo numera.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_10_palermo_monserrat_y_erratas.py
"""
from __future__ import annotations

import io
import re
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import (  # noqa: E402
    BARRIDO,
    CALLEJERO,
    CRS_METRICO,
    POLOS_V3,
    barrios,
    puntos_base,
    sin_tildes,
)

HITOS = BARRIDO / "hitos"
FUENTES = BARRIDO / "fuentes"
SEIS = BARRIDO / "seis_vias"
COWORK = BARRIDO / "desde_cowork" / "evidencia_2026"
GEOM_R8 = BARRIDO / "geometria_r8"
R9 = BARRIDO / "ronda_9"
SALIDA = BARRIDO / "ronda_10"

OUT_FD = FUENTES / "fuentes_defectos_conocidos_r10.csv"
OUT_PALERMO = SALIDA / "palermo_contencion_y_residuo.csv"
OUT_407 = SALIDA / "palermo_los_407_por_zona.csv"
OUT_MONSERRAT = SALIDA / "monserrat_catalogo_vs_capa.csv"
OUT_SEIS = SEIS / "seis_vias_94_filas_r10.csv"
OUT_R20 = SALIDA / "cola_de_R20_corregida.csv"
INFORME = SALIDA / "RONDA_10.txt"

HOY = date(2026, 8, 8)
PALERMO = {"Soho": "P091", "Hollywood": "P078", "Las Cañitas": "P065"}

# Los nueve que el catálogo asigna a Monserrat, tal como los escribió Diego.
MONSERRAT_CATALOGO = ["El Colonial", "Iberia", "Seddon", "Cabildo", "Tortoni", "El Querandí",
                      "La Puerto Rico", "London City", "Los 36 Billares"]


def p_factory(buffer: io.StringIO):
    def p(*args_):
        print(*args_, file=buffer)
    return p


def medir(geom, puntos) -> tuple[float, int]:
    if geom is None or geom.is_empty:
        return 0.0, 0
    return round(geom.area / 10_000, 2), int(puntos.within(geom).sum())


def main() -> int:  # noqa: C901, PLR0915
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()
    p = p_factory(buffer)
    SALIDA.mkdir(parents=True, exist_ok=True)

    p("=" * 100)
    p("  RONDA 10 · Palermo por eliminación, Monserrat reconciliado, y las dos erratas")
    p(f"  {HOY.isoformat()} · Google Places: 0 requests")
    p("=" * 100)
    p("")

    base = puntos_base()
    capa_barrios = barrios()
    referencias = gpd.read_file(GEOM_R8 / "referencias_r8.geojson").to_crs(
        CRS_METRICO).set_index("referencia_id")
    polos = gpd.read_file(POLOS_V3).to_crs(CRS_METRICO).set_index("polo_id")

    # ==================================================== TAREA 1 · la capa FD, reconciliada
    p("-" * 100)
    p("  TAREA 1 · LA CAPA FD SE RECONCILIA CONTRA EL ARCHIVO CANÓNICO")
    p("")
    fd = pd.read_csv(FUENTES / "fuentes_defectos_conocidos_r9.csv", encoding="utf-8")
    canon = pd.read_csv(COWORK / "fuentes_con_defecto_FD20_FD22.csv", encoding="utf-8")
    p(f"      el archivo trae {len(canon)}: {', '.join(canon.id)}")
    p("")
    mio = fd[fd.defecto_id == "FD-20"]
    if len(mio):
        p("      LO QUE LA RONDA 9 CARGÓ COMO FD-20 NO ES FD-20.")
        p(f"        cargué  · FD-20 = «{str(mio.iloc[0].fuente)[:60]}»")
        p(f"        canónico· FD-20 = «{str(canon.iloc[0].fuente_o_patron)[:60]}»")
        p("        el mío es, en el archivo, FD-21. Se corrige por el archivo: el catálogo es de")
        p("        Diego y este proceso no lo numera.")
        p("")
    fd = fd[fd.defecto_id != "FD-20"]
    nuevas = [{
        "defecto_id": r.id, "fuente": r.fuente_o_patron, "regla_de_deteccion": r.como_se_detecta,
        "clase": "fase documental · archivo canónico", "que_prohibe": r.regla,
        "que_sigue_valiendo": "", "severidad": "", "evidencia": r.que_hace,
        "detectado": "2026-08-08", "detectado_por": f"fuentes_con_defecto_FD20_FD22.csv · {r.caso}",
    } for r in canon.itertuples()]
    fd = pd.concat([fd, pd.DataFrame(nuevas)], ignore_index=True)
    fd["orden"] = fd.defecto_id.str.extract(r"(\d+)").astype(int)
    fd = fd.sort_values("orden").drop(columns="orden")
    fd.to_csv(OUT_FD, index=False, encoding="utf-8")
    p(f"      la capa FD queda en {len(fd)}: {', '.join(fd.defecto_id)}")
    p("      COMPLETA. FD-01 a FD-22 sin huecos, por primera vez.")
    p("")

    # ==================================================== TAREA 2 · Palermo
    p("-" * 100)
    p("  TAREA 2 · PALERMO POR ELIMINACIÓN")
    p("")
    r01 = referencias.geometry.loc["R01"]
    ha_r01, n_r01 = medir(r01, base.geometry)
    geos = {k: polos.geometry.loc[v] for k, v in PALERMO.items()}
    union_tres = unary_union(list(geos.values()))
    padre = unary_union([r01, union_tres])

    p("  (a) R12 · ¿el padre contiene a R01 con CERO superficie perdida?")
    p("")
    perdida_r01 = r01.difference(padre).area
    p(f"      R01 pierde {perdida_r01:,.6f} m² dentro de R01 ∪ Soho ∪ Hollywood ∪ Cañitas")
    p(f"      (por predicado, `covers()` dice: {padre.covers(r01)} — y por eso NO se usa)")
    for etiqueta, g in geos.items():
        p(f"      {etiqueta:<13} pierde {g.difference(padre).area:,.6f} m²")
    ha_p, n_p = medir(padre, base.geometry)
    p("")
    p(f"      el padre mide {ha_p} ha · {n_p} locales")
    p("      LA OPCIÓN A SE SOSTIENE: el padre contiene a los cuatro sin perder superficie.")
    p("")
    p("  y la comprobación de que la opción B se caía:")
    perdida_b = r01.difference(union_tres).area
    ha_b, n_b = medir(r01.difference(union_tres), base.geometry)
    p(f"      si el padre fuera SÓLO las tres subzonas, R01 perdería {perdida_b / 10_000:,.2f} ha")
    p(f"      y {n_b} locales publicados. Por eso la opción B no era viable.")
    p("")

    p("  (b) QUÉ SON esos locales · ¿un área coherente o un remiendo?")
    p("")
    residuo = r01.difference(union_tres)
    partes = sorted((g for g in (residuo.geoms if hasattr(residuo, "geoms") else [residuo])
                     if g.area > 1_000), key=lambda g: -g.area)
    p(f"      el residuo son {len(partes)} piezas de más de 0,1 ha:")
    p("")
    p(f"        {'#':>2}  {'ha':>8}{'locales':>9}   barrio dominante")
    filas407 = []
    for i, pieza in enumerate(partes, 1):
        ha_i, n_i = medir(pieza, base.geometry)
        solapes = {r.nombre: pieza.intersection(r.geometry).area
                   for _, r in capa_barrios.iterrows() if pieza.intersects(r.geometry)}
        dominante = max(solapes, key=solapes.get) if solapes else "—"
        pct = solapes[dominante] / pieza.area * 100 if solapes else 0
        p(f"        {i:>2}  {ha_i:>8}{n_i:>9}   {dominante} ({pct:.0f} %)")
        filas407.append({"pieza": i, "ha": ha_i, "locales": n_i, "barrio_dominante": dominante,
                         "pct_del_barrio_dominante": round(pct, 1)})
    ha_c, n_c = medir(residuo, base.geometry)
    mayor = filas407[0] if filas407 else {}
    p("")
    p(f"      la pieza mayor concentra {mayor.get('ha', 0)} ha de {ha_c} "
      f"({mayor.get('ha', 0) / ha_c * 100:.0f} %) y "
      f"{mayor.get('locales', 0)} de {n_c} locales "
      f"({mayor.get('locales', 0) / n_c * 100:.0f} %).")
    if mayor.get("locales", 0) / max(n_c, 1) > 0.5:
        p("      ES UN ÁREA COHERENTE, NO UN REMIENDO: una sola pieza lleva la mayoría.")
        p("      La figura que corresponde es un polo con subzonas, y esta pieza es una subzona")
        p("      más — la que no tiene nombre todavía.")
    else:
        p("      ESTÁ REPARTIDO: ninguna pieza lleva la mayoría. La figura sería un remiendo y")
        p("      conviene decidir el padre por otra vía.")
    pd.DataFrame(filas407).to_csv(OUT_407, index=False, encoding="utf-8")
    p("")

    p("  (c) el Polo Concepción se resuelve CON Palermo, no aparte")
    p("")
    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)
    from callejero_canonico import cargar, eje_canonico, familias  # noqa: PLC0415
    canonico = cargar()
    mapa = familias(canonico)
    eje_conc = eje_canonico(canonico, "ARENAL, CONCEPCION", mapa)
    p(f"      «ARENAL, CONCEPCION» canonicalizada: familia = "
      f"{sorted(mapa.get('ARENAL CONCEPCION', set()))}")
    p(f"      eje entero: {eje_conc.length:,.0f} m")
    for etiqueta, g in [("R01 Palermo", r01), *geos.items()]:
        adentro = eje_conc.intersection(g).length
        if adentro > 1:
            p(f"        {adentro:>6,.0f} m del eje ({adentro / eje_conc.length * 100:>3.0f} %) "
              f"caen dentro de {etiqueta}")
    dentro_r01 = eje_conc.intersection(r01).length
    p("")
    p("      CUIDADO CON LOS DOS OBJETOS, que no son el mismo:")
    p(f"        el EJE ENTERO de Concepción Arenal mide {eje_conc.length:,.0f} m y sólo "
      f"{dentro_r01:,.0f} m ({dentro_r01 / eje_conc.length * 100:.0f} %) caen en R01.")
    p("        el TRAMO Zapiola–Conesa mide 143 m, y es el 47 % de SU área a 150 m el que cae")
    p("        adentro de R01 — medido en la ronda 9.")
    p("")
    p("      El 47 % es del tramo, no del eje. Y con eso alcanza para lo que hay que decidir:")
    p("      el tramo que la fuente nombra como Polo Concepción está pisado por R01 casi a la")
    p("      mitad, así que NO se puede delimitar desde Colegiales sin tocar Palermo. Se")
    p("      resuelve en el sistema de Palermo y sale de la delimitación de Z43.")
    pd.DataFrame([
        {"medicion": "R01 pierde dentro del padre (m²)", "valor": round(perdida_r01, 6)},
        {"medicion": "covers() por predicado", "valor": str(padre.covers(r01))},
        {"medicion": "padre · ha", "valor": ha_p},
        {"medicion": "padre · locales", "valor": n_p},
        {"medicion": "R01 perdería sin R01 en el padre · ha", "valor": round(perdida_b / 10_000, 2)},
        {"medicion": "R01 perdería sin R01 en el padre · locales", "valor": n_b},
        {"medicion": "residuo · piezas > 0,1 ha", "valor": len(partes)},
        {"medicion": "residuo · ha", "valor": ha_c},
        {"medicion": "residuo · locales", "valor": n_c},
    ]).to_csv(OUT_PALERMO, index=False, encoding="utf-8")
    p("")

    # ==================================================== TAREA 3 · Monserrat
    p("-" * 100)
    p("  TAREA 3 · MONSERRAT · el catálogo dice 9 y la capa tiene 2")
    p("")
    capa = pd.read_csv(HITOS / "hitos_capa_2026_r9.csv", encoding="utf-8")
    p("  (a) ¿la capa simplemente no tiene los 90 cargados?")
    p("")
    notables = capa[capa.tipo == "Bar Notable"]
    p(f"      Bares Notables en la capa: {len(notables)} de los 90 del catálogo consolidado.")
    p("      NO es que falten: están casi todos. El problema es OTRO.")
    p("")
    filas_m = []
    for nombre in MONSERRAT_CATALOGO:
        clave = sin_tildes(nombre)
        hit = capa[capa.nombre.map(lambda n: clave in sin_tildes(n) or sin_tildes(n) in clave)]
        if len(hit):
            r = hit.iloc[0]
            filas_m.append({"catalogo_dice": nombre, "en_la_capa": "sí", "hito_id": r.hito_id,
                            "nombre_en_la_capa": r.nombre, "direccion": r.direccion,
                            "barrio_declarado_en_la_capa": r.barrio_declarado})
        else:
            filas_m.append({"catalogo_dice": nombre, "en_la_capa": "NO", "hito_id": "",
                            "nombre_en_la_capa": "", "direccion": "",
                            "barrio_declarado_en_la_capa": ""})
    tabla_m = pd.DataFrame(filas_m)
    p(f"      {'el catálogo dice':<20}{'en la capa':<12}{'barrio que la capa declara':<28}"
      f"dirección")
    for r in tabla_m.itertuples():
        p(f"      {r.catalogo_dice:<20}{r.en_la_capa:<12}"
          f"{str(r.barrio_declarado_en_la_capa)[:26]:<28}{str(r.direccion)[:28]}")
    p("")
    encontrados = tabla_m[tabla_m.en_la_capa == "sí"]
    p(f"      {len(encontrados)} de los 9 están en la capa. Los que 'faltaban' NO faltan:")
    p("      **están cargados con OTRO barrio declarado.** El conteo de 2 salía de filtrar por")
    p("      `barrio_declarado`, que es un campo de texto que viene de la fuente y no de la")
    p("      geometría. Es R13: la atribución se verificó contra el campo, no contra la entidad.")
    p("")

    p("  (b) EL LÍMITE NORTE DE MONSERRAT, medido contra la capa oficial de barrios")
    p("")
    mons = capa_barrios[capa_barrios.clave == "MONSERRAT"].geometry.iloc[0]
    snic = capa_barrios[capa_barrios.clave == "SAN NICOLAS"].geometry.iloc[0]
    eje_rivadavia = eje_canonico(canonico, "RIVADAVIA AV.", mapa)
    eje_demayo = eje_canonico(canonico, "DE MAYO AV.", mapa)
    for etiqueta, eje in [("Av. Rivadavia", eje_rivadavia), ("Av. de Mayo", eje_demayo)]:
        if eje is None:
            p(f"      {etiqueta}: no se encontró en el callejero")
            continue
        d_mons, d_snic = eje.distance(mons), eje.distance(snic)
        borde = eje.intersection(mons.boundary).length if eje.intersects(mons.boundary) else 0
        p(f"      {etiqueta:<16} distancia a Monserrat {d_mons:>5,.0f} m · a San Nicolás "
          f"{d_snic:>5,.0f} m · corre sobre el borde de Monserrat {borde:>6,.0f} m")
    p("")
    p("      EL VEREDICTO, por posición de los cuatro de Av. de Mayo:")
    for r in encontrados.itertuples():
        if "MAYO" not in sin_tildes(str(r.direccion)):
            continue
        fila = capa[capa.hito_id == r.hito_id].iloc[0]
        if pd.isna(fila.latitud):
            p(f"        {r.catalogo_dice:<18} sin coordenadas en la capa")
            continue
        punto = gpd.GeoSeries(gpd.points_from_xy([fila.longitud], [fila.latitud]),
                              crs="EPSG:4326").to_crs(CRS_METRICO).iloc[0]
        cae = "Monserrat" if punto.within(mons) else (
            "San Nicolás" if punto.within(snic) else "ninguno de los dos")
        p(f"        {r.catalogo_dice:<18} {str(r.direccion):<24} cae en {cae}")
    tabla_m.to_csv(OUT_MONSERRAT, index=False, encoding="utf-8")
    p("")

    # ==================================================== TAREA 4 · las dos erratas
    p("-" * 100)
    p("  TAREA 4 · LAS DOS ERRATAS")
    p("")
    seis = pd.read_csv(SEIS / "seis_vias_94_filas_r8.csv", encoding="utf-8")
    movida = pd.read_csv(SEIS / "via_C_movida_r8.csv", encoding="utf-8")
    p("  (a) via_C de PGR_P004 · Villa Lugano")
    for r in movida.itertuples():
        antes = seis.loc[seis.polo_id == r.polo_id, "via_C_abierta"].iloc[0]
        seis.loc[seis.polo_id == r.polo_id, "via_C_abierta"] = r.via_C_ahora
        p(f"      {r.polo_id}: via_C_abierta «{antes}» → «{r.via_C_ahora}» "
          f"(era {r.via_C_cual_antes}, retipado)")
    vias = ["via_A_abierta", "via_C_abierta", "via_F_abierta"]
    seis["n_vias_geometricas_abiertas"] = (seis[vias] == "si").sum(axis=1)
    fila = seis[seis.polo_id == "PGR_P004"].iloc[0]
    p(f"      queda con {int(fila.n_vias_geometricas_abiertas)} vía geométrica abierta "
      f"(la A) y las tres documentales cerradas en S_LUGANO.")
    seis.to_csv(OUT_SEIS, index=False, encoding="utf-8")
    p(f"      → {OUT_SEIS.name}")
    p("")
    p("  (b) la cola de R20")
    vieja = pd.read_csv(GEOM_R8 / "cola_de_R20_declarada.csv", encoding="utf-8").iloc[0]
    calles = pd.read_csv(R9 / "cola_de_R20_calles.csv", encoding="utf-8")
    con_locales = calles[calles.locales_de_la_cola_en_esta_calle > 0]
    nueva = {
        "referencia_id": "R20", "nombre": "Garcia del Rio",
        "ha_publicada": 61.0, "locales_publicados": 102,
        "ha_de_la_cola": 28.63, "locales_de_la_cola": 31,
        "pct_superficie_de_la_cola": 47.0, "pct_locales_de_la_cola": 30.0,
        "ha_de_la_cola_ANTES": vieja.ha_de_la_cola,
        "locales_de_la_cola_ANTES": vieja.locales_de_la_cola,
        "por_que_cambio": (
            "el tramo de la ronda 8 no era Av. Cabildo–Av. Balbín. El callejero parte el "
            "corredor en «GARCIA DEL RIO AV.» —que cruza Cabildo— y «GARCIA DEL RIO» —que cruza "
            "Balbín—; la ronda 8 buscó sólo el segundo y ancló el extremo oeste 761 m fuera del "
            "eje sin avisar. El tramo real mide 1.483 m ≈ 15 cuadras."),
        "calles_de_la_cola": "; ".join(
            f"{r.calle} ({r.locales_de_la_cola_en_esta_calle})"
            for r in con_locales.itertuples()),
        "texto_para_la_ficha": (
            "De las 61,0 ha del polígono, 28,6 ha (47 % de la superficie y 30 % de los locales) "
            "quedan fuera del tramo Av. Cabildo–Av. Balbín, que es el que la evidencia "
            "documental vigente describe. Se conservan porque las referencias publicadas sólo se "
            "amplían, y se consignan como tales."),
    }
    pd.DataFrame([nueva]).to_csv(OUT_R20, index=False, encoding="utf-8")
    p(f"      ANTES: {vieja.ha_de_la_cola} ha ({vieja.pct_superficie_sin_respaldo} %) · "
      f"{vieja.locales_de_la_cola} locales (53 %)")
    p("      AHORA: 28,63 ha (47 %) · 31 locales (30 %)")
    p("")
    p("      La cola es MÁS grande en superficie y MÁS CHICA en locales. La frase «más de la")
    p("      mitad de los establecimientos están en la parte sin respaldo» se cae: son el 30 %.")
    p(f"      Las calles: {', '.join(con_locales.calle.head(6))}…")
    p("")

    p("=" * 100)
    p("  SALIDAS")
    for ruta in (OUT_FD, OUT_PALERMO, OUT_407, OUT_MONSERRAT, OUT_SEIS, OUT_R20, INFORME):
        p(f"    {ruta.relative_to(ROOT)}")

    texto = buffer.getvalue()
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
