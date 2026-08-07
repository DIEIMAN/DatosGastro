"""Ronda 3 · la vía B por soporte y la vía D con cuatro estados, sobre las 94 filas y las 22 zonas.

QUÉ HACE
--------
Recomputa **sólo las dos vías cuyas reglas cambiaron**. Las vías A, C y F se leen tal cual de la
corrida de la ronda 2: sus insumos no se movieron, y volver a calcularlas sería fabricar la
oportunidad de que cambien por otra cosa.

    B · trayectoria    ahora con `via_B_soporte` de cinco valores y una vía que puede quedar
                       PENDIENTE, que no es ni abierta ni cerrada
    D · comunidades    ahora con `via_D_estado` de cuatro valores (más el quinto que trae el CSV)
                       y con siete enclaves cruzables en vez de cuatro

EL ORDEN DE PRECEDENCIA, DECLARADO EN `LECTURA_PREVIA_RONDA_3.md` §2 Y NO MOVIDO DESPUÉS
-----------------------------------------------------------------------------------------
    activo / mixto  >  en_disputa  >  sin_verificar  >  extinguido

`extinguido` sólo cuando **todos** los hitos de la fila están verificados cerrados. Una fila con un
cerrado y un sin verificar no es extinguida: el sin verificar puede estar abierto y nadie miró. Es
la asimetría que Los Laureles obliga a respetar.

LO QUE ESTE SCRIPT VA A HACER Y CONVIENE SABER DE ANTEMANO
-----------------------------------------------------------
**La vía B se desploma.** No porque se haya perdido evidencia, sino porque la que había nunca
existió: en 220 fichas de hitos hay 8 verificadas abiertas. El 43 de 94 de la ronda 2 contaba como
«abre» todo lo que no estuviera verificado cerrado, que es afirmar 212 cosas que nadie comprobó.

Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_seis_vias_r3.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import (  # noqa: E402
    BARRIDO,
    CRS_GEOGRAFICO,
    CRS_METRICO,
    envolventes_22,
    soportes_94,
)

OUT = BARRIDO / "seis_vias"
HITOS = BARRIDO / "hitos"
CAPA_R3 = HITOS / "hitos_capa_2026_r3.csv"
ENCLAVES_R3 = OUT / "enclaves_comunitarios_r3.geojson"

TIPOS_VIA_B = {
    "Bar Notable": "bar_notable",
    "Restaurante Icónico": "restaurante_iconico",
    "Pizzería emblemática": "pizzeria_emblematica",
    "Heladería histórica": "heladeria_historica",
    "MICHELIN": "michelin",
    "Ranking internacional": "50best",
}

# `dudosa` se pliega a `sin_verificar`: significa «nadie miró y además hay motivo para dudar»,
# que no es una disputa entre fuentes. El conteo de dudosos sigue viajando en su columna.
PLIEGUE = {"si": "si", "no": "no", "en_disputa": "en_disputa",
           "dudosa": "sin_verificar", "sin_verificar": "sin_verificar"}


def soporte_de(estados: list[str]) -> tuple[str, str]:
    """(`via_B_soporte`, `via_B_abierta`) para una fila, con la precedencia declarada."""
    if not estados:
        return "sin_hitos", "no"
    plegados = [PLIEGUE.get(e, "sin_verificar") for e in estados]
    abiertos = plegados.count("si")
    cerrados = plegados.count("no")
    if abiertos and cerrados:
        return "mixto", "si"
    if abiertos:
        return "activo", "si"
    if "en_disputa" in plegados:
        return "en_disputa", "pendiente"
    if "sin_verificar" in plegados:
        return "sin_verificar", "pendiente"
    return "extinguido", "no"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    if not CAPA_R3.exists():
        raise SystemExit("falta hitos_capa_2026_r3.csv — correr hitos_ronda_3_vigencia.py")
    if not ENCLAVES_R3.exists():
        raise SystemExit("falta enclaves_comunitarios_r3.geojson — correr enclaves_ronda_3.py")

    capa = pd.read_csv(CAPA_R3)
    con_punto = capa[capa.latitud.notna() & capa.longitud.notna()].copy()
    hitos = gpd.GeoDataFrame(
        con_punto, geometry=gpd.points_from_xy(con_punto.longitud, con_punto.latitud),
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO).reset_index(drop=True)
    enclaves = gpd.read_file(ENCLAVES_R3).to_crs(CRS_METRICO)
    cruzables = enclaves[enclaves.computa_via_D == "si"]
    mercados = hitos[hitos.tipo == "Mercado/patio"]

    p("RONDA 3 · LA VÍA B POR SOPORTE Y LA VÍA D CON CUATRO ESTADOS")
    p("=" * 100)
    p("")
    p(f"  hitos con punto: {len(hitos)} · enclaves con geometría: {len(enclaves)} · "
      f"cruzables: {len(cruzables)}")
    p("  Vías A, C y F: se leen de la ronda 2 sin recalcular. Sus insumos no se movieron.")
    p("  Google Places: 0 requests.")
    p("")
    p("  El estado de los hitos que entra al cómputo:")
    for estado, cuantos in capa.vigencia_verificada.value_counts().items():
        p(f"      {estado:<16}{cuantos:>5}")
    p("")

    def medir(capa_soporte: gpd.GeoDataFrame, clave: str) -> pd.DataFrame:
        hitos_dentro = gpd.sjoin(hitos, capa_soporte[[clave, "geometry"]],
                                 predicate="within", how="inner")
        mercados_dentro = gpd.sjoin(mercados, capa_soporte[[clave, "geometry"]],
                                    predicate="within", how="inner")
        filas = []
        for fila in capa_soporte.itertuples():
            identificador = getattr(fila, clave)
            registro = {clave: identificador}
            if fila.geometry is None or fila.geometry.is_empty:
                registro["soporte_ausente"] = "si"
                filas.append(registro)
                continue
            registro["soporte_ausente"] = "no"

            propios = hitos_dentro[hitos_dentro[clave] == identificador]
            for tipo, columna in TIPOS_VIA_B.items():
                registro[f"via_B_{columna}"] = int((propios.tipo == tipo).sum())
            registro["via_B_total"] = len(propios)
            registro["via_B_patrimonio_normativo"] = int(propios.es_patrimonio_normativo.sum())
            for estado in ("si", "no", "en_disputa", "dudosa", "sin_verificar"):
                registro[f"via_B_{estado}"] = int((propios.vigencia_verificada == estado).sum())
            soporte, abierta = soporte_de(list(propios.vigencia_verificada.astype(str)))
            registro["via_B_soporte"] = soporte
            registro["via_B_abierta"] = abierta
            registro["via_B_nombres"] = "; ".join(sorted(propios.nombre.astype(str))[:12])
            registro["via_B_abiertos_cuales"] = "; ".join(
                sorted(propios[propios.vigencia_verificada == "si"].nombre.astype(str)))
            registro["via_B_cerrados_cuales"] = "; ".join(
                sorted(propios[propios.vigencia_verificada == "no"].nombre.astype(str)))
            registro["via_B_en_disputa_cuales"] = "; ".join(
                sorted(propios[propios.vigencia_verificada == "en_disputa"].nombre.astype(str)))

            suyos = mercados_dentro[mercados_dentro[clave] == identificador]
            registro["via_C_cual_r3"] = "; ".join(sorted(suyos.nombre.astype(str)))

            # Vía D. Por defecto NO_MEDIDA, que es lo que la ronda 2 escribía como `no`.
            tocados = cruzables[cruzables.intersects(fila.geometry)]
            sin_computo = enclaves[(enclaves.computa_via_D == "no") &
                                   enclaves.geometry.notna() &
                                   enclaves.intersects(fila.geometry)]
            if len(tocados):
                registro["via_D_estado"] = "abierta"
                registro["via_D_abierta"] = "si"
            else:
                registro["via_D_estado"] = "no_medida"
                registro["via_D_abierta"] = "pendiente"
            registro["via_D_enclave"] = "; ".join(sorted(tocados.enclave_id))
            registro["via_D_enclave_sin_computo"] = "; ".join(sorted(sin_computo.enclave_id))
            filas.append(registro)
        return pd.DataFrame(filas)

    # ------------------------------------------------------------------ las 94
    soportes = soportes_94()
    ronda2 = pd.read_csv(OUT / "seis_vias_94_filas.csv")
    medidas = medir(soportes, "polo_id")
    columnas_acf = [c for c in ronda2.columns
                    if c.startswith(("via_A", "via_C", "via_F", "n_locales", "ha", "locales_x_ha",
                                     "cont_pct", "vecino"))] + ["polo_id", "nombre_polo",
                                                                "soporte_clase", "soporte_detalle"]
    tabla = ronda2[columnas_acf].merge(
        medidas.drop(columns=[c for c in ("via_C_cual_r3",) if c in medidas]),
        on="polo_id", how="left")
    tabla.to_csv(OUT / "seis_vias_94_filas_r3.csv", index=False, encoding="utf-8")

    # ------------------------------------------------------------------ el delta de vía B
    p("-" * 100)
    p("  TAREA 1 · LA VÍA B, RECONTADA CON `via_B_soporte`")
    p("")
    reparto = tabla[tabla.soporte_ausente == "no"].via_B_soporte.value_counts()
    p(f"      {'via_B_soporte':<18}{'filas':>7}   abre")
    for valor in ("activo", "mixto", "en_disputa", "sin_verificar", "extinguido", "sin_hitos"):
        cuantas = int(reparto.get(valor, 0))
        abre = {"activo": "sí", "mixto": "sí", "extinguido": "no",
                "en_disputa": "pendiente", "sin_verificar": "pendiente",
                "sin_hitos": "no"}[valor]
        p(f"      {valor:<18}{cuantas:>7}   {abre}")
    p(f"      {'TOTAL':<18}{int(reparto.sum()):>7}   (sobre las 92 con soporte)")
    p("")
    abre_r3 = int((tabla.via_B_abierta == "si").sum())
    pendientes = int((tabla.via_B_abierta == "pendiente").sum())
    cierra = int((tabla.via_B_abierta == "no").sum())
    p(f"      EL DELTA CONTRA LA RONDA 2:  43 de 94  →  {abre_r3} de 94")
    p(f"      y {pendientes} filas quedan PENDIENTES, que no es ni abre ni no abre. "
      f"{cierra} no abren.")
    p("")
    p("      Esas 43 no se perdieron: nunca existieron. La ronda 2 contaba como «abre» todo hito")
    p("      que no estuviera verificado cerrado, es decir 212 hitos que nadie miró. Con 8")
    p("      verificados abiertos en 220 fichas, el número honesto es éste.")
    p("")
    p("      Las filas que SÍ abren, con el hito que las abre:")
    for fila in tabla[tabla.via_B_abierta == "si"].itertuples():
        p(f"            {str(fila.polo_id):<24}{str(fila.nombre_polo)[:26]:<28}"
          f"{fila.via_B_soporte:<10}{fila.via_B_abiertos_cuales[:44]}")
    p("")
    extinguidas = tabla[tabla.via_B_soporte == "extinguido"]
    p(f"      Las filas EXTINGUIDAS —hubo hitos, todos verificados cerrados—: {len(extinguidas)}")
    for fila in extinguidas.itertuples():
        p(f"            {str(fila.polo_id):<24}{str(fila.nombre_polo)[:26]:<28}"
          f"{fila.via_B_cerrados_cuales[:44]}")
    p("      Se publican igual, como capa histórica: la trayectoria es un hecho del pasado que no")
    p("      se revierte. Lo que no hacen es abrir la vía.")
    p("")
    en_disputa = tabla[tabla.via_B_soporte == "en_disputa"]
    p(f"      Las filas EN DISPUTA: {len(en_disputa)}")
    for fila in en_disputa.itertuples():
        p(f"            {str(fila.polo_id):<24}{str(fila.nombre_polo)[:26]:<28}"
          f"{fila.via_B_en_disputa_cuales[:44]}")
    p("")
    p008 = tabla[tabla.polo_id.astype(str).str.contains("P008", na=False)]
    if len(p008):
        for fila in p008.itertuples():
            p(f"      LA REVERSIÓN · {fila.polo_id} {fila.nombre_polo}: "
              f"soporte = {fila.via_B_soporte}, vía B = {fila.via_B_abierta}")
            p(f"            hitos adentro: {fila.via_B_total} · «{fila.via_B_nombres}»")
        p("      La ronda 2 la había cerrado. No está cerrada: está pendiente, que es distinto.")
    p("")

    # ------------------------------------------------------------------ vía D
    p("-" * 100)
    p("  TAREA 2-3 · LA VÍA D, CON CUATRO ESTADOS Y SIETE ENCLAVES CRUZABLES")
    p("")
    for estado, cuantas in tabla[tabla.soporte_ausente == "no"].via_D_estado.value_counts(
    ).items():
        p(f"      {estado:<24}{cuantas:>5} de 92 con soporte")
    p("")
    p(f"      EL DELTA CONTRA LA RONDA 2:  7 abiertas de 94  →  "
      f"{int((tabla.via_D_estado == 'abierta').sum())} de 94")
    p("      Y las que antes decían `no` ahora dicen `no_medida`, que es lo que son: 87 filas")
    p("      escritas como cerradas cuando lo que pasaba era que no las habíamos medido.")
    p("")
    p("      Las que abren vía D:")
    for fila in tabla[tabla.via_D_estado == "abierta"].itertuples():
        p(f"            {str(fila.polo_id):<24}{str(fila.nombre_polo)[:28]:<30}"
          f"{fila.via_D_enclave}")
    p("")
    con_sin_computo = tabla[tabla.via_D_enclave_sin_computo.astype(str).str.len() > 0]
    p(f"      Filas que tocan un enclave que NO computa (se ve, no cuenta): {len(con_sin_computo)}")
    for fila in con_sin_computo.itertuples():
        p(f"            {str(fila.polo_id):<24}{str(fila.nombre_polo)[:28]:<30}"
          f"{fila.via_D_enclave_sin_computo}")
    p("")

    # ------------------------------------------------------------------ el recuento de vías
    def abre(columna: pd.Series) -> pd.Series:
        return (columna == "si").astype(int)

    tabla["n_vias_medibles"] = (
        abre(tabla.via_A_abierta) + abre(tabla.via_B_abierta) + abre(tabla.via_C_abierta)
        + abre(tabla.via_D_abierta) + abre(tabla.via_F_abierta))
    tabla["n_vias_pendientes"] = ((tabla.via_B_abierta == "pendiente").astype(int)
                                  + (tabla.via_D_abierta == "pendiente").astype(int))
    tabla.loc[tabla.soporte_ausente != "no", ["n_vias_medibles", "n_vias_pendientes"]] = np.nan
    tabla.to_csv(OUT / "seis_vias_94_filas_r3.csv", index=False, encoding="utf-8")

    p("-" * 100)
    p("  LAS 94 FILAS · cuántas abren cada vía, con la regla nueva")
    p("")
    for via, columna in [("A · densidad", "via_A_abierta"), ("B · trayectoria", "via_B_abierta"),
                         ("C · mercados", "via_C_abierta"), ("D · comunidades", "via_D_abierta"),
                         ("F · corredor", "via_F_abierta")]:
        cuantas = int((tabla[columna] == "si").sum())
        pend = int((tabla[columna] == "pendiente").sum())
        cola = f"   ({pend} pendientes)" if pend else ""
        p(f"      {via:<20}{cuantas:>4} de 94{cola}")
    p(f"      {'E · reconocimiento':<20}{'—':>4}   la llena Diego; el cruce contra el ENTUR va aparte")
    p("")
    con_soporte = tabla[tabla.soporte_ausente == "no"]
    for cuantas, n in con_soporte.n_vias_medibles.value_counts().sort_index().items():
        p(f"            {int(cuantas)} vía(s) abiertas: {n} filas")
    ninguna = con_soporte[con_soporte.n_vias_medibles == 0]
    p("")
    p(f"      filas con CERO vías abiertas: {len(ninguna)} "
      f"(de las cuales {int((ninguna.n_vias_pendientes > 0).sum())} tienen alguna PENDIENTE)")
    p("")

    # ------------------------------------------------------------------ las 22
    envolventes = envolventes_22()
    medidas22 = medir(envolventes, "referencia_id")
    ronda2_22 = pd.read_csv(OUT / "seis_vias_22_zonas.csv")
    columnas22 = [c for c in ronda2_22.columns
                  if c.startswith(("via_A", "via_C", "via_F", "n_locales", "ha"))] + \
        ["referencia_id", "nombre"]
    tabla22 = ronda2_22[columnas22].merge(
        medidas22.drop(columns=[c for c in ("via_C_cual_r3",) if c in medidas22]),
        on="referencia_id", how="left")
    tabla22["n_vias_medibles"] = (
        abre(tabla22.via_A_abierta) + abre(tabla22.via_B_abierta) + abre(tabla22.via_C_abierta)
        + abre(tabla22.via_D_abierta) + abre(tabla22.via_F_abierta))
    tabla22["n_vias_pendientes"] = ((tabla22.via_B_abierta == "pendiente").astype(int)
                                    + (tabla22.via_D_abierta == "pendiente").astype(int))
    tabla22 = tabla22.sort_values("referencia_id").reset_index(drop=True)
    tabla22.to_csv(OUT / "seis_vias_22_zonas_r3.csv", index=False, encoding="utf-8")

    p("=" * 100)
    p("  EL CONTROL · las 22 publicadas, con la regla nueva")
    p("=" * 100)
    p("")
    p(f"  {'id':<5}{'zona':<30}{'A':>3}{'B':>3}{'C':>3}{'D':>3}{'F':>3}{'abren':>7}"
      f"{'pend':>6}   soporte B / estado D")
    for fila in tabla22.itertuples():
        marcas = ""
        for via in "ABCDF":
            valor = getattr(fila, f"via_{via}_abierta")
            marcas += f"{'X' if valor == 'si' else '?' if valor == 'pendiente' else '·':>3}"
        p(f"  {fila.referencia_id:<5}{fila.nombre[:29]:<30}{marcas}"
          f"{fila.n_vias_medibles:>7}{fila.n_vias_pendientes:>6}   "
          f"{fila.via_B_soporte} / {fila.via_D_estado}")
    p("")
    sin_ninguna = tabla22[tabla22.n_vias_medibles == 0]
    p(f"      zonas con al menos una vía ABIERTA: {int((tabla22.n_vias_medibles > 0).sum())} de 22")
    p(f"      zonas con cero abiertas:            {len(sin_ninguna)}")
    for fila in sin_ninguna.itertuples():
        p(f"            {fila.referencia_id} {fila.nombre}: "
          f"{fila.n_vias_pendientes} vía(s) pendiente(s) · B = {fila.via_B_soporte}")
    p("")
    p("      La ronda 2 decía «las 22 abren al menos una vía medible» y era cierto con su regla.")
    p("      Con la regla de presencia, la afirmación que se sostiene es la de las vías A, C y F,")
    p("      que no dependen de vigencia. La vía B de las 22 está casi entera PENDIENTE, y eso no")
    p("      es un resultado sobre el territorio: es el estado de nuestra verificación.")
    p("")

    p("=" * 100)
    p(f"  94 filas y 22 zonas · vía B {abre_r3} abren / {pendientes} pendientes · "
      f"vía D {int((tabla.via_D_estado == 'abierta').sum())} abiertas · Places: 0 requests")
    p("=" * 100)
    p("")

    (OUT / "SEIS_VIAS_R3.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
