# -*- coding: utf-8 -*-
"""Etapa Infra-6 — QA automatico de la capa editorial de macrozonas.

EXPERIMENTAL. Controles pedidos explicitamente, en dos niveles (mismo criterio que el QA
del prototipo de clustering: gates duros que rechazan vs. banderas que piden revision):

GATES DUROS (bloquean una version, no se publica si fallan):
  G1 poligonos invalidos (autointersecciones, anillos mal formados)
  G2 atributos obligatorios faltantes o vacios (id, nombre, nivel, tipo_geometria,
     estado_revision, nivel_confianza, version_capa)
  G3 'id' duplicado
  G4 valores fuera de vocabulario controlado (nivel, tipo_geometria, estado_revision,
     nivel_confianza)
  G5 'subzona' con polo_id vacio o apuntando a un id que no existe en la capa

BANDERAS (no bloquean, quedan para revision humana):
  B1 poligonos con huecos (anillos interiores) — puede ser intencional (excluir una
     plaza), pero se marca siempre
  B2 superposicion entre macrozonas del MISMO nivel que no son padre/hijo (dos polos o
     dos subzonas de polos distintos no deberian solaparse)
  B3 cobertura de CABA: se documenta el % cubierto por poligonos de nivel 'polo' y se
     deja la geometria de lo NO cubierto como capa diagnostica (no es un error: son zonas
     sin macrozona editorial todavia, igual que 'entidades_fuera_de_macrozona' en el
     prototipo V1)
  B4 features con estado_revision != 'aprobado_editorial' (recordatorio: no deberian
     alimentar un informe institucional todavia)

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/qa_capa_editorial.py <capa.geojson>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
from shapely.validation import explain_validity

REPO = Path(__file__).resolve().parents[4]
COMUNAS = REPO / "PolosGastro/cartografia/comunas_caba.geojson"
CRS_METRICO = "EPSG:5347"

CAMPOS_OBLIGATORIOS = [
    "id", "nombre", "nivel", "tipo_geometria", "estado_revision", "nivel_confianza",
    "version_capa",
]
VALORES_VALIDOS = {
    "nivel": {"polo", "subzona"},
    "tipo_geometria": {"poligono_real", "poligono_aproximado", "elipse_editorial", "pendiente"},
    "estado_revision": {"borrador", "revisado", "aprobado_editorial"},
    "nivel_confianza": {"alta", "media", "baja", "sin_evidencia"},
}


def gates_duros(gdf: gpd.GeoDataFrame) -> list[str]:
    errores = []

    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in gdf.columns:
            errores.append(f"G2: falta la columna obligatoria '{campo}' en toda la capa")
            continue
        vacios = gdf[gdf[campo].isna() | (gdf[campo].astype(str).str.strip() == "")]
        for id_ in vacios.get("id", vacios.index):
            errores.append(f"G2: '{campo}' vacio en feature id={id_}")

    if "id" in gdf.columns:
        dup = gdf["id"][gdf["id"].duplicated(keep=False)]
        for id_ in sorted(set(dup)):
            errores.append(f"G3: id duplicado '{id_}'")

    for campo, validos in VALORES_VALIDOS.items():
        if campo not in gdf.columns:
            continue
        malos = gdf[~gdf[campo].isin(validos) & gdf[campo].notna()]
        for _, fila in malos.iterrows():
            errores.append(
                f"G4: '{campo}'={fila[campo]!r} fuera de vocabulario en id={fila.get('id')} "
                f"(validos: {sorted(validos)})"
            )

    if "nivel" in gdf.columns and "polo_id" in gdf.columns and "id" in gdf.columns:
        ids_existentes = set(gdf["id"])
        subzonas = gdf[gdf["nivel"] == "subzona"]
        for _, fila in subzonas.iterrows():
            polo_id = fila.get("polo_id")
            if polo_id is None or (isinstance(polo_id, float)) or str(polo_id).strip() == "":
                errores.append(f"G5: subzona id={fila['id']} sin polo_id")
            elif polo_id not in ids_existentes:
                errores.append(
                    f"G5: subzona id={fila['id']} referencia polo_id={polo_id!r} inexistente"
                )

    for _, fila in gdf.iterrows():
        geom = fila.geometry
        if geom is None:
            continue
        if not geom.is_valid:
            errores.append(f"G1: geometria invalida en id={fila.get('id')}: "
                           f"{explain_validity(geom)}")

    return errores


def banderas(gdf: gpd.GeoDataFrame) -> list[str]:
    avisos = []
    gdf_m = gdf.to_crs(CRS_METRICO)

    for _, fila in gdf_m.iterrows():
        geom = fila.geometry
        if geom is not None and geom.geom_type == "Polygon" and len(geom.interiors) > 0:
            avisos.append(f"B1: id={fila.get('id')} tiene {len(geom.interiors)} hueco(s) interior(es)")
        elif geom is not None and geom.geom_type == "MultiPolygon":
            n_huecos = sum(len(p.interiors) for p in geom.geoms)
            if n_huecos:
                avisos.append(f"B1: id={fila.get('id')} (multipolygon) tiene {n_huecos} hueco(s)")

    if "nivel" in gdf_m.columns and "polo_id" in gdf_m.columns:
        for nivel in ("polo", "subzona"):
            capa = gdf_m[gdf_m["nivel"] == nivel]
            if nivel == "subzona":
                grupos = capa.groupby("polo_id")
            else:
                grupos = [(None, capa)]
            for _, grupo in grupos:
                ids = grupo["id"].tolist()
                geoms = grupo.geometry.tolist()
                for i in range(len(ids)):
                    for j in range(i + 1, len(ids)):
                        inter = geoms[i].intersection(geoms[j]).area
                        area_min = min(geoms[i].area, geoms[j].area)
                        if area_min > 0 and inter / area_min > 0.02:
                            pct = round(100.0 * inter / area_min, 1)
                            avisos.append(
                                f"B2: solapamiento {pct}% (del area menor) entre "
                                f"{ids[i]} y {ids[j]} (mismo nivel '{nivel}')"
                            )

    if "nivel" in gdf_m.columns:
        polos = gdf_m[gdf_m["nivel"] == "polo"]
        if len(polos):
            comunas = gpd.read_file(COMUNAS).to_crs(CRS_METRICO)
            caba = comunas.union_all()
            cubierto = polos.geometry.union_all()
            area_caba = caba.area
            area_cubierta = cubierto.intersection(caba).area
            pct = round(100.0 * area_cubierta / area_caba, 2)
            avisos.append(
                f"B3: cobertura de CABA por macrozonas nivel 'polo': {pct}% "
                f"({len(polos)} polos con geometria)"
            )
        else:
            avisos.append("B3: no hay features nivel='polo' con geometria; cobertura = 0%")

    if "estado_revision" in gdf_m.columns:
        no_aprobados = gdf_m[gdf_m["estado_revision"] != "aprobado_editorial"]
        if len(no_aprobados):
            avisos.append(
                f"B4: {len(no_aprobados)} de {len(gdf_m)} features NO estan "
                "'aprobado_editorial' (no deberian usarse en un informe institucional): "
                + ", ".join(no_aprobados['id'].astype(str))
            )

    return avisos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capa", help="Ruta al GeoJSON de la capa editorial a validar")
    args = parser.parse_args()

    gdf = gpd.read_file(args.capa)
    errores = gates_duros(gdf)
    avisos = banderas(gdf)

    print(f"QA de {args.capa} — {len(gdf)} features")
    print("=" * 70)
    print(f"\nGATES DUROS: {len(errores)} error(es)")
    for e in errores:
        print(f"  [X] {e}")
    print(f"\nBANDERAS: {len(avisos)} aviso(s)")
    for a in avisos:
        print(f"  [!] {a}")

    print("\n" + "=" * 70)
    if errores:
        print(f"RESULTADO: NO PUBLICABLE — {len(errores)} gate(s) duro(s) sin resolver.")
        sys.exit(1)
    print("RESULTADO: pasa los gates duros. Revisar banderas antes de aprobar version.")


if __name__ == "__main__":
    main()
