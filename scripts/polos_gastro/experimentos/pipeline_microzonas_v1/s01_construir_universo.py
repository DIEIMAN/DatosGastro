# -*- coding: utf-8 -*-
"""Etapa 1 — Universo gastronomico V1 (entidades, no registros administrativos).

EXPERIMENTAL. Lee `data/processed/` (solo lectura) y escribe en
`outputs/polos_gastro/historico/experimentos/pipeline_microzonas_v1/universo/`.

Construye la tabla maestra de ENTIDADES gastronomicas a partir de F01 (oferta
registrada) y F02 (habilitaciones historicas), con resolucion de entidades
espacial + textual (doc 03 s5). Semantica honesta: el universo mide oferta
gastronomica registrada / con evidencia documental, JAMAS "locales activos".

Reglas aplicadas (todas registradas en `log_reglas_universo_v1.json` y
documentadas en docs/polos_gastro/historico/experimentos/pipeline_microzonas_v1/):

  R1  F01: filas `es_gastronomico = si`, join a dim_ubicacion.
  R2  F02: filas `es_gastronomico = si`, excluyendo Catering/Mercado/Feria
      (no son locales gastronomicos a la calle).
  R3  F02 se colapsa a UNA entidad por id_ubicacion (5,6 filas/ubicacion en
      promedio; el recurso 2025 llega a 28,8). Limitacion: sin nombre comercial
      en F02, varios locales legitimos en una misma direccion (galerias)
      quedan como una sola entidad.
  R4  Dedup interna F01: mismo nombre normalizado + misma id_ubicacion, o
      mismo nombre normalizado a <= 40 m (mismo local geocodificado por
      cadenas de direccion distintas).
  R5  Dedup cruzada F01<-F02 (sin nombres en F02, solo ubicacion/espacio):
      a) misma id_ubicacion  -> fusion;
      b) misma direccion_normalizada -> fusion;
      c) distancia <= 15 m y categoria compatible -> fusion;
      d) distancia <= 30 m y categoria compatible -> NO fusiona, marca
         `posible_duplicado_cercano` (cola de revision humana).
  R6  Supervivencia: nombre y categoria de F01; mejor coordenada disponible;
      evidencia = union (banderas en_f01/en_f02, fechas min/max).

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/pipeline_microzonas_v1/s01_construir_universo.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from datetime import date
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402


# ---------------------------------------------------------------------------
# Normalizacion
# ---------------------------------------------------------------------------

def plegar(texto: str) -> str:
    """Mayusculas, sin acentos, sin puntuacion, espacios colapsados."""
    if not isinstance(texto, str):
        return ""
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = "".join(c if c.isalnum() or c.isspace() else " " for c in t.upper())
    return " ".join(t.split())


def categoria_canonica(cat: str) -> str:
    return plegar(cat).lower() or "sin_categoria"


# Pares de categorias que pueden describir el mismo local segun la fuente
# (F02 trae rubros administrativos; F01 categorias inferidas). Simetricos.
CATEGORIAS_COMPATIBLES = {
    frozenset(p)
    for p in [
        ("cafe", "pasteleria"),
        ("cafe", "panaderia"),
        ("cafe", "bar"),
        ("panaderia", "pasteleria"),
        ("restaurante", "parrilla"),
        ("restaurante", "pizzeria"),
        ("restaurante", "bar"),
        ("restaurante", "comida al paso"),
        ("pizzeria", "comida al paso"),
    ]
}


def compatibles(cat_a: str, cat_b: str) -> bool:
    if cat_a == cat_b:
        return True
    return frozenset((cat_a, cat_b)) in CATEGORIAS_COMPATIBLES


def id_entidad(direccion: str, nombre: str, categoria: str) -> str:
    base = f"{direccion}|{nombre}|{categoria}".encode("utf-8")
    return "E" + hashlib.sha1(base).hexdigest()[:10].upper()


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

def cargar_dim_ubicacion() -> pd.DataFrame:
    ub = pd.read_csv(config.PROCESSED / "dim_ubicacion.csv", dtype=str)
    ub["latitud"] = pd.to_numeric(ub["latitud"], errors="coerce")
    ub["longitud"] = pd.to_numeric(ub["longitud"], errors="coerce")
    return ub[
        ["id_ubicacion", "direccion_normalizada", "barrio", "comuna",
         "latitud", "longitud", "calidad_geo"]
    ]


def cargar_f01(ub: pd.DataFrame, log: dict) -> pd.DataFrame:
    fact = pd.read_csv(config.PROCESSED / "fact_establecimiento.csv", dtype=str)
    log["f01_filas_totales"] = len(fact)
    f01 = fact[fact["es_gastronomico"] == "si"].copy()
    log["f01_filas_gastronomicas"] = len(f01)
    f01 = f01.merge(ub, on="id_ubicacion", how="left")
    f01["nombre_norm"] = f01["nombre"].map(plegar)
    f01["cat_canon"] = f01["categoria_gastronomica_inferida"].map(categoria_canonica)
    f01["anio_evidencia"] = pd.to_numeric(f01["anio_fuente"], errors="coerce")
    return f01


def cargar_f02(ub: pd.DataFrame, log: dict) -> pd.DataFrame:
    fact = pd.read_csv(config.PROCESSED / "fact_habilitacion_gastronomica.csv", dtype=str)
    log["f02_filas_totales"] = len(fact)
    f02 = fact[fact["es_gastronomico"] == "si"].copy()
    log["f02_filas_gastronomicas"] = len(f02)

    excluidas = config.PARAMETROS["universo"]["categorias_f02_excluidas"]["valor"]
    mask_exc = f02["categoria_gastronomica_inferida"].isin(excluidas)
    log["f02_filas_excluidas_por_categoria"] = {
        cat: int((f02.loc[mask_exc, "categoria_gastronomica_inferida"] == cat).sum())
        for cat in excluidas
    }
    f02 = f02[~mask_exc].copy()
    log["f02_filas_tras_filtro_categorias"] = len(f02)

    f02["cat_canon"] = f02["categoria_gastronomica_inferida"].map(categoria_canonica)
    f02["fecha_hab"] = pd.to_datetime(f02["fecha_habilitacion"], errors="coerce")
    f02["es_recurso_2025"] = f02["anio_fuente"].eq("2025")
    f02 = f02.merge(ub, on="id_ubicacion", how="left", suffixes=("_f02", ""))
    return f02


# ---------------------------------------------------------------------------
# Entidades F01 (dedup interna, R4)
# ---------------------------------------------------------------------------

class UnionFind:
    def __init__(self, n: int):
        self.padre = list(range(n))

    def raiz(self, i: int) -> int:
        while self.padre[i] != i:
            self.padre[i] = self.padre[self.padre[i]]
            i = self.padre[i]
        return i

    def unir(self, a: int, b: int) -> None:
        ra, rb = self.raiz(a), self.raiz(b)
        if ra != rb:
            self.padre[rb] = ra


def entidades_f01(f01: pd.DataFrame, log: dict) -> pd.DataFrame:
    dist_max = config.PARAMETROS["universo"]["dedup_f01_nombre_igual_dist_m"]["valor"]
    f01 = f01.reset_index(drop=True)
    uf = UnionFind(len(f01))

    # R4a: mismo nombre normalizado + misma id_ubicacion
    for _, idx in f01.groupby(["nombre_norm", "id_ubicacion"]).groups.items():
        idx = list(idx)
        for j in idx[1:]:
            uf.unir(idx[0], j)

    # R4b: mismo nombre normalizado a <= 40 m (requiere coordenadas)
    gdf = gpd.GeoDataFrame(
        f01, geometry=gpd.points_from_xy(f01["longitud"], f01["latitud"]),
        crs=config.CRS_GEO,
    )
    con_geo = gdf["latitud"].notna() & gdf["longitud"].notna() & gdf["nombre_norm"].ne("")
    metrico = gdf.loc[con_geo].to_crs(config.CRS_METRICO)
    fusiones_espaciales = 0
    for _, idx in metrico.groupby("nombre_norm").groups.items():
        idx = list(idx)
        if len(idx) < 2:
            continue
        sub = metrico.loc[idx]
        xy = np.column_stack([sub.geometry.x, sub.geometry.y])
        arbol = cKDTree(xy)
        for a, b in arbol.query_pairs(dist_max):
            uf.unir(idx[a], idx[b])
            fusiones_espaciales += 1

    f01["grupo_f01"] = [uf.raiz(i) for i in range(len(f01))]
    n_grupos = f01["grupo_f01"].nunique()
    log["f01_fusiones_mismo_nombre_misma_ubicacion"] = int(
        len(f01) - f01.groupby(["nombre_norm", "id_ubicacion"]).ngroups
    )
    log["f01_pares_fusionados_nombre_40m"] = fusiones_espaciales
    log["f01_entidades"] = int(n_grupos)

    filas = []
    for gid, sub in f01.groupby("grupo_f01"):
        mejor = sub.sort_values("calidad_geo").iloc[0]  # fuente_oficial < usig_exacta alfabetico: elegir con coords
        con_coord = sub.dropna(subset=["latitud", "longitud"])
        ref = con_coord.iloc[0] if len(con_coord) else mejor
        filas.append(
            {
                "nombre_canonico": sub["nombre"].iloc[0],
                "nombre_norm": sub["nombre_norm"].iloc[0],
                "direccion_normalizada": ref["direccion_normalizada"],
                "id_ubicacion": ref["id_ubicacion"],
                "lat": ref["latitud"],
                "lon": ref["longitud"],
                "calidad_geo": ref["calidad_geo"],
                "categoria_canonica": sub["cat_canon"].mode().iloc[0],
                "n_registros_f01": len(sub),
                "anio_evidencia_f01": (
                    int(sub["anio_evidencia"].max()) if sub["anio_evidencia"].notna().any() else None
                ),
                "ids_origen_f01": ";".join(sub["id_establecimiento"].astype(str)),
                "estado_resolucion": "unica" if len(sub) == 1 else "fusion_f01_interna",
            }
        )
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# Entidades F02 (colapso por ubicacion, R3)
# ---------------------------------------------------------------------------

def entidades_f02(f02: pd.DataFrame, log: dict) -> pd.DataFrame:
    filas = []
    for uid, sub in f02.groupby("id_ubicacion"):
        cats = sub["cat_canon"].value_counts()
        fechas = sub["fecha_hab"].dropna()
        filas.append(
            {
                "id_ubicacion": uid,
                "direccion_normalizada": sub["direccion_normalizada"].iloc[0],
                "lat": sub["latitud"].iloc[0],
                "lon": sub["longitud"].iloc[0],
                "calidad_geo": sub["calidad_geo"].iloc[0],
                "categoria_canonica": cats.index[0],
                "categorias_f02": ";".join(f"{c}:{n}" for c, n in cats.items()),
                "n_registros_f02": len(sub),
                "n_rubros_f02": int(sub["descripcion_rubro_normalizada"].nunique()),
                "evidencia_min_fecha": fechas.min().date().isoformat() if len(fechas) else None,
                "evidencia_max_fecha": fechas.max().date().isoformat() if len(fechas) else None,
                "solo_evidencia_2025_sin_fecha": bool(sub["es_recurso_2025"].all()),
                "ids_origen_f02": ";".join(sub["id_habilitacion"].astype(str)),
            }
        )
    ent = pd.DataFrame(filas)
    log["f02_entidades_por_ubicacion"] = len(ent)
    log["f02_entidades_solo_recurso_2025"] = int(ent["solo_evidencia_2025_sin_fecha"].sum())
    return ent


# ---------------------------------------------------------------------------
# Dedup cruzada (R5) y tabla maestra (R6)
# ---------------------------------------------------------------------------

def fusionar(e1: pd.DataFrame, e2: pd.DataFrame, log: dict):
    dist_fusion = config.PARAMETROS["universo"]["dedup_cruzada_dist_m"]["valor"]
    dist_flag = config.PARAMETROS["universo"]["dedup_cruzada_flag_dist_m"]["valor"]

    e1 = e1.reset_index(drop=True)
    e2 = e2.reset_index(drop=True)
    e2["fusionada_en"] = -1  # indice de la entidad F01 receptora
    e2["regla_fusion"] = ""
    e2["flag_duplicado"] = ""

    # R5a: misma id_ubicacion. R5b: misma direccion_normalizada.
    por_ubicacion: dict[str, list[int]] = {}
    por_direccion: dict[str, list[int]] = {}
    for i, fila in e1.iterrows():
        if pd.notna(fila["id_ubicacion"]):
            por_ubicacion.setdefault(fila["id_ubicacion"], []).append(i)
        if pd.notna(fila["direccion_normalizada"]):
            por_direccion.setdefault(fila["direccion_normalizada"], []).append(i)

    def elegir_receptora(candidatos: list[int], cat: str) -> int:
        """Si hay varias entidades F01 en la misma direccion (galeria), recibe
        la de categoria compatible; si ninguna lo es, la de mas registros."""
        compat = [i for i in candidatos if compatibles(e1.at[i, "categoria_canonica"], cat)]
        pool = compat or candidatos
        return max(pool, key=lambda i: e1.at[i, "n_registros_f01"])

    n_a = n_b = n_c = n_flag = 0
    for j, fila in e2.iterrows():
        cat = fila["categoria_canonica"]
        cands = por_ubicacion.get(fila["id_ubicacion"], [])
        if cands:
            e2.at[j, "fusionada_en"] = elegir_receptora(cands, cat)
            e2.at[j, "regla_fusion"] = "R5a_misma_id_ubicacion"
            n_a += 1
            continue
        cands = por_direccion.get(fila["direccion_normalizada"], [])
        if cands:
            e2.at[j, "fusionada_en"] = elegir_receptora(cands, cat)
            e2.at[j, "regla_fusion"] = "R5b_misma_direccion_normalizada"
            n_b += 1

    # R5c/R5d: espacial sobre las F02 aun no fusionadas.
    g1 = gpd.GeoDataFrame(
        e1, geometry=gpd.points_from_xy(e1["lon"], e1["lat"]), crs=config.CRS_GEO
    )
    con1 = g1["lat"].notna() & g1["lon"].notna()
    m1 = g1.loc[con1].to_crs(config.CRS_METRICO)
    xy1 = np.column_stack([m1.geometry.x, m1.geometry.y])
    idx1 = m1.index.to_numpy()
    arbol = cKDTree(xy1)

    pendientes = e2[(e2["fusionada_en"] < 0) & e2["lat"].notna() & e2["lon"].notna()]
    g2 = gpd.GeoDataFrame(
        pendientes, geometry=gpd.points_from_xy(pendientes["lon"], pendientes["lat"]),
        crs=config.CRS_GEO,
    ).to_crs(config.CRS_METRICO)
    for j, punto in zip(g2.index, g2.geometry):
        vecinos = arbol.query_ball_point([punto.x, punto.y], dist_flag)
        if not vecinos:
            continue
        cat = e2.at[j, "categoria_canonica"]
        mejores = sorted(
            vecinos,
            key=lambda k: (punto.x - xy1[k][0]) ** 2 + (punto.y - xy1[k][1]) ** 2,
        )
        for k in mejores:
            i = int(idx1[k])
            d = float(np.hypot(punto.x - xy1[k][0], punto.y - xy1[k][1]))
            if not compatibles(e1.at[i, "categoria_canonica"], cat):
                continue
            if d <= dist_fusion:
                e2.at[j, "fusionada_en"] = i
                e2.at[j, "regla_fusion"] = "R5c_espacial_15m_categoria_compatible"
                n_c += 1
            else:
                e2.at[j, "flag_duplicado"] = "posible_duplicado_cercano_30m"
                n_flag += 1
            break

    log["fusiones_R5a_misma_id_ubicacion"] = n_a
    log["fusiones_R5b_misma_direccion"] = n_b
    log["fusiones_R5c_espacial_15m"] = n_c
    log["flags_posible_duplicado_30m"] = n_flag
    log["f02_entidades_fusionadas_en_f01"] = int((e2["fusionada_en"] >= 0).sum())
    log["f02_entidades_independientes"] = int((e2["fusionada_en"] < 0).sum())
    return e1, e2


def tabla_maestra(e1: pd.DataFrame, e2: pd.DataFrame) -> pd.DataFrame:
    maestra = e1.copy()
    maestra["en_f01"] = True
    maestra["en_f02"] = False
    maestra["n_registros_f02"] = 0
    maestra["n_rubros_f02"] = 0
    maestra["categorias_f02"] = ""
    maestra["evidencia_min_fecha"] = None
    maestra["evidencia_max_fecha"] = None
    maestra["solo_evidencia_2025_sin_fecha"] = False
    maestra["ids_origen_f02"] = ""
    maestra["regla_fusion"] = ""
    maestra["flag_duplicado"] = ""

    for j, fila in e2.iterrows():
        i = fila["fusionada_en"]
        if i >= 0:
            maestra.at[i, "en_f02"] = True
            maestra.at[i, "n_registros_f02"] += fila["n_registros_f02"]
            maestra.at[i, "n_rubros_f02"] += fila["n_rubros_f02"]
            maestra.at[i, "categorias_f02"] = fila["categorias_f02"]
            maestra.at[i, "evidencia_min_fecha"] = fila["evidencia_min_fecha"]
            maestra.at[i, "evidencia_max_fecha"] = fila["evidencia_max_fecha"]
            maestra.at[i, "ids_origen_f02"] = fila["ids_origen_f02"]
            maestra.at[i, "regla_fusion"] = fila["regla_fusion"]
            maestra.at[i, "estado_resolucion"] = "fusion_cruzada"

    indep = e2[e2["fusionada_en"] < 0].copy()
    indep["nombre_canonico"] = ""
    indep["nombre_norm"] = ""
    indep["en_f01"] = False
    indep["en_f02"] = True
    indep["n_registros_f01"] = 0
    indep["anio_evidencia_f01"] = None
    indep["ids_origen_f01"] = ""
    indep["estado_resolucion"] = "unica"
    indep = indep.drop(columns=["fusionada_en"])

    columnas = [
        "nombre_canonico", "nombre_norm", "direccion_normalizada", "id_ubicacion",
        "lat", "lon", "calidad_geo", "categoria_canonica",
        "en_f01", "en_f02", "n_registros_f01", "n_registros_f02", "n_rubros_f02",
        "categorias_f02", "anio_evidencia_f01", "evidencia_min_fecha",
        "evidencia_max_fecha", "solo_evidencia_2025_sin_fecha",
        "estado_resolucion", "regla_fusion", "flag_duplicado",
        "ids_origen_f01", "ids_origen_f02",
    ]
    todas = pd.concat([maestra[columnas], indep[columnas]], ignore_index=True)
    todas["id_entidad"] = [
        id_entidad(str(d), str(n), str(c))
        for d, n, c in zip(
            todas["direccion_normalizada"], todas["nombre_norm"], todas["categoria_canonica"]
        )
    ]
    # Colisiones de hash (mismas claves) se desambiguan con sufijo posicional.
    dup = todas["id_entidad"].duplicated(keep=False)
    if dup.any():
        todas.loc[dup, "id_entidad"] = (
            todas.loc[dup, "id_entidad"]
            + "_"
            + todas.loc[dup].groupby("id_entidad").cumcount().astype(str)
        )
    return todas[["id_entidad"] + columnas]


def marcar_aptitud(maestra: pd.DataFrame, log: dict) -> pd.DataFrame:
    """Marca que entidades entran al clustering y por que se descartan otras."""
    bbox = config.PARAMETROS["universo"]["bbox_caba"]["valor"]
    caba = gpd.read_file(config.COMUNAS_GEOJSON).to_crs(config.CRS_GEO).union_all()

    motivo = pd.Series("", index=maestra.index)
    sin_coord = maestra["lat"].isna() | maestra["lon"].isna()
    motivo[sin_coord] = "sin_coordenadas"

    lat = maestra["lat"].astype(float)
    lon = maestra["lon"].astype(float)
    fuera_bbox = ~sin_coord & ~(
        lat.between(*bbox["lat"]) & lon.between(*bbox["lon"])
    )
    motivo[fuera_bbox] = "fuera_bbox_caba"

    resto = ~sin_coord & ~fuera_bbox
    puntos = gpd.GeoSeries(
        gpd.points_from_xy(lon[resto], lat[resto]), index=maestra.index[resto],
        crs=config.CRS_GEO,
    )
    fuera_caba = ~puntos.within(caba)
    motivo[fuera_caba.index[fuera_caba]] = "fuera_limite_caba"

    maestra["apta_clustering"] = motivo.eq("")
    maestra["motivo_descarte"] = motivo
    log["entidades_totales"] = len(maestra)
    log["entidades_aptas_clustering"] = int(maestra["apta_clustering"].sum())
    log["descartes"] = motivo[motivo != ""].value_counts().to_dict()
    return maestra


def correspondencia(f01: pd.DataFrame, f02: pd.DataFrame, maestra: pd.DataFrame) -> pd.DataFrame:
    """Tabla fila fuente -> id_entidad (linaje completo, doc 03 s4)."""
    mapa = {}
    for _, fila in maestra.iterrows():
        for rid in str(fila["ids_origen_f01"]).split(";"):
            if rid:
                mapa[("F01", rid)] = fila["id_entidad"]
        for rid in str(fila["ids_origen_f02"]).split(";"):
            if rid:
                mapa[("F02", rid)] = fila["id_entidad"]
    filas = [
        {"fuente": f, "id_registro_fuente": r, "id_entidad": e}
        for (f, r), e in mapa.items()
    ]
    return pd.DataFrame(filas)


def main() -> None:
    config.asegurar_salidas("universo")
    log: dict = {"fecha_corrida": date.today().isoformat()}

    ub = cargar_dim_ubicacion()
    f01 = cargar_f01(ub, log)
    f02 = cargar_f02(ub, log)

    e1 = entidades_f01(f01, log)
    e2 = entidades_f02(f02, log)
    e1, e2 = fusionar(e1, e2, log)
    maestra = tabla_maestra(e1, e2)
    maestra = marcar_aptitud(maestra, log)

    dupl_potenciales = log["f01_filas_gastronomicas"] + log["f02_filas_tras_filtro_categorias"]
    log["reduccion_total"] = {
        "filas_fuente_gastronomicas": dupl_potenciales,
        "entidades_finales": len(maestra),
        "porcentaje_colapso": round(100.0 * (1 - len(maestra) / dupl_potenciales), 1),
    }

    salida = config.SALIDA / "universo"
    maestra.to_csv(salida / "universo_entidades_v1.csv", index=False, encoding="utf-8")
    corr = correspondencia(f01, f02, maestra)
    corr.to_csv(salida / "correspondencia_filas_fuente.csv", index=False, encoding="utf-8")
    with open(salida / "log_reglas_universo_v1.json", "w", encoding="utf-8") as fh:
        json.dump(log, fh, ensure_ascii=False, indent=2)
    config.exportar_parametros()

    print("=" * 70)
    print("UNIVERSO GASTRONOMICO V1 (experimental; oferta registrada, no activos)")
    print("=" * 70)
    for k, v in log.items():
        print(f"{k}: {v}")
    print(f"\nSalidas en {salida}")


if __name__ == "__main__":
    main()
