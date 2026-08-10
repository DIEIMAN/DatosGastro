# -*- coding: utf-8 -*-
"""Cruza 124 concentraciones con 41 soportes, sin modificar geometrías fuente.

Por defecto usa la capa vigente de soportes de la entrega anterior. Cuando esté
disponible una nueva capa, se pasa con ``--soportes RUTA``. La capa debe declarar
``soporte_es_real`` y un estado/fuente; el programa falla si no puede distinguir
un borde trazado de un soporte provisorio.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


OUT = Path(__file__).resolve().parent
BASE = OUT.parent
POLOS = BASE / "borrador_polos" / "polos_publicables.geojson"
NOMBRES = BASE / "desde_cowork" / "POLOS_NOMBRADOS.csv"
SOPORTES_VIGENTES = BASE / "ronda_16_codex" / "geometria" / "soportes_41.geojson"
CRS_METRICO = "EPSG:5347"
UMBRAL_M2 = 0.01


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def bool_estricto(valor: object) -> bool:
    if isinstance(valor, bool):
        return valor
    texto = str(valor).strip().casefold()
    if texto in {"true", "1", "si", "sí"}:
        return True
    if texto in {"false", "0", "no"}:
        return False
    raise ValueError(f"soporte_es_real no es booleano: {valor!r}")


def nombre_concentracion(fila: pd.Series) -> str:
    for campo in ("nombre_mapa", "nombre_en_ficha", "nombre_propuesto"):
        valor = str(fila.get(campo, "")).strip()
        if valor and valor.casefold() != "nan":
            return valor
    return str(fila["polo_id"])


def cargar(soportes_path: Path):
    polos = gpd.read_file(POLOS).to_crs(CRS_METRICO)
    nombres = pd.read_csv(NOMBRES, encoding="utf-8-sig").set_index("polo_id")
    soportes = gpd.read_file(soportes_path).to_crs(CRS_METRICO)
    obligatorias = {"polo_id", "soporte_es_real", "estado_soporte", "fuente_geometria"}
    faltan = obligatorias - set(soportes.columns)
    if faltan:
        raise RuntimeError(f"la capa de soportes no declara {sorted(faltan)}")
    soportes["soporte_es_real"] = soportes["soporte_es_real"].map(bool_estricto)
    if len(polos) != 124 or polos["polo_id"].duplicated().any():
        raise RuntimeError("la capa de concentraciones no tiene 124 IDs únicos")
    if len(soportes) != 41 or soportes["polo_id"].duplicated().any():
        raise RuntimeError("la capa de soportes no tiene 41 IDs únicos")
    if len(nombres) != 124 or nombres.index.duplicated().any():
        raise RuntimeError("la tabla de nombres no tiene 124 IDs únicos")
    return polos.set_index("polo_id"), nombres, soportes.set_index("polo_id")


def cruzar(polos, nombres, soportes) -> tuple[pd.DataFrame, pd.DataFrame]:
    filas = []
    excluidos = []
    for pid, concentracion in polos.sort_index().iterrows():
        cruces = 0
        for zid, soporte in soportes.sort_index().iterrows():
            if not concentracion.geometry.intersects(soporte.geometry):
                continue
            inter = concentracion.geometry.intersection(soporte.geometry)
            area = float(inter.area)
            if area <= UMBRAL_M2:
                excluidos.append(
                    {
                        "concentracion_id": pid,
                        "polo_id": zid,
                        "interseccion_m2": round(area, 8),
                        "umbral_m2": UMBRAL_M2,
                        "motivo": "contacto sin área material; excluido de la correspondencia",
                    }
                )
                continue
            cruces += 1
            real = bool(soporte.soporte_es_real)
            filas.append(
                {
                    "bloque": "PUBLICABLE" if real else "ESPERA_BORDE",
                    "fila_tipo": "INTERSECCION",
                    "concentracion_id": pid,
                    "concentracion_nombre": nombre_concentracion(nombres.loc[pid]),
                    "polo_id": zid,
                    "polo_nombre": str(soporte.get("polo_nombre", zid)),
                    "borde_polo": "TRAZADO" if real else "PROVISORIO_DE_BARRIO",
                    "atribuible": "SI" if real else "NO",
                    "estado_soporte": soporte.estado_soporte,
                    "fuente_geometria": soporte.fuente_geometria,
                    "superficie_concentracion_m2": round(float(concentracion.geometry.area), 4),
                    "superficie_soporte_m2": round(float(soporte.geometry.area), 4),
                    "interseccion_m2": round(area, 4),
                    "pct_concentracion_en_soporte": round(
                        100 * area / concentracion.geometry.area, 4
                    ),
                    "pct_soporte_cubierto": round(100 * area / soporte.geometry.area, 4),
                    "criterio": f"intersección > {UMBRAL_M2} m²; sin tope de filas",
                }
            )
        if cruces == 0:
            filas.append(
                {
                    "bloque": "ESPERA_BORDE",
                    "fila_tipo": "SIN_INTERSECCION_EN_SOPORTES_ACTUALES",
                    "concentracion_id": pid,
                    "concentracion_nombre": nombre_concentracion(nombres.loc[pid]),
                    "polo_id": "NINGUNO",
                    "polo_nombre": "Sin cruce material en los soportes disponibles",
                    "borde_polo": "NO_APLICA",
                    "atribuible": "NO",
                    "estado_soporte": "SIN_CRUCE",
                    "fuente_geometria": "NO_APLICA",
                    "superficie_concentracion_m2": round(float(concentracion.geometry.area), 4),
                    "superficie_soporte_m2": "",
                    "interseccion_m2": 0.0,
                    "pct_concentracion_en_soporte": 0.0,
                    "pct_soporte_cubierto": "",
                    "criterio": f"sin intersección > {UMBRAL_M2} m²; sin tope de filas",
                }
            )
    orden = {"PUBLICABLE": 0, "ESPERA_BORDE": 1}
    df = pd.DataFrame(filas)
    df["_orden"] = df["bloque"].map(orden)
    resultado = df.sort_values(
        ["_orden", "concentracion_id", "polo_id"], kind="mergesort"
    ).drop(columns="_orden")
    descartes = pd.DataFrame(
        excluidos,
        columns=["concentracion_id", "polo_id", "interseccion_m2", "umbral_m2", "motivo"],
    ).sort_values(["concentracion_id", "polo_id"], kind="mergesort")
    return resultado, descartes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--soportes", type=Path, default=SOPORTES_VIGENTES)
    parser.add_argument("--salida", type=Path, default=OUT / "correspondencia_124_x_41.csv")
    args = parser.parse_args()
    soportes_path = args.soportes.resolve()
    hashes_antes = {str(p): sha256(p) for p in (POLOS, NOMBRES, soportes_path)}
    polos, nombres, soportes = cargar(soportes_path)
    resultado, excluidos = cruzar(polos, nombres, soportes)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(args.salida, index=False, encoding="utf-8-sig", lineterminator="\r\n")
    excluidos.to_csv(
        OUT / "contactos_excluidos_umbral.csv",
        index=False,
        encoding="utf-8-sig",
        lineterminator="\r\n",
    )
    inter = resultado[resultado["fila_tipo"] == "INTERSECCION"]
    resumen = {
        "concentraciones": 124,
        "polos": 41,
        "cruces_materiales": int(len(inter)),
        "cruces_publicables": int(inter["bloque"].eq("PUBLICABLE").sum()),
        "cruces_esperando_borde": int(inter["bloque"].eq("ESPERA_BORDE").sum()),
        "concentraciones_sin_cruce_material": int(
            resultado["fila_tipo"].eq("SIN_INTERSECCION_EN_SOPORTES_ACTUALES").sum()
        ),
        "umbral_interseccion_m2": UMBRAL_M2,
        "contactos_excluidos_por_umbral": int(len(excluidos)),
        "detalle_exclusiones": "contactos_excluidos_umbral.csv",
        "tope_de_filas": None,
        "geometria_soportes": str(soportes_path),
        "sha256_insumos": hashes_antes,
    }
    (OUT / "correspondencia_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    hashes_despues = {str(p): sha256(p) for p in (POLOS, NOMBRES, soportes_path)}
    if hashes_antes != hashes_despues:
        raise RuntimeError("un insumo cambió durante la ejecución")
    print(json.dumps(resumen, ensure_ascii=False))


if __name__ == "__main__":
    main()
