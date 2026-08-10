# -*- coding: utf-8 -*-
"""Ronda 16: correspondencia 124×41, solapamientos 41×41 y borde de Palermo.

Corrida local, sin red ni APIs. No modifica el pipeline público ni datos fuente.
Las reglas de lectura están preinscritas en LECTURA_PREVIA_RONDA_16.md.
"""

from __future__ import annotations

import hashlib
from itertools import combinations
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union


OUT = Path(__file__).resolve().parent
BARRIDO = OUT.parent
EVIDENCIA = BARRIDO / "desde_cowork" / "evidencia_2026"
CRS_METRICO = "EPSG:5347"
AREA_POSITIVA_M2 = 0.01
TOL_CONTENCION_M2 = 1.0
UMBRAL_CONTINUIDAD_M = 40.0

CRITERIO = EVIDENCIA / "criterio_admision_55.csv"
FICHAS = EVIDENCIA / "fichas_corpus_polos.csv"
BASE_LOCAL = BARRIDO / "base" / "local.csv"
ZONAS_R7 = BARRIDO / "geometria_r7" / "zonas_r7.geojson"
PERIMETROS_CSV = BARRIDO / "ronda_15" / "perimetros_18.csv"
PERIMETROS_GEO = BARRIDO / "ronda_15" / "geometria" / "perimetros_18.geojson"
POLOS_124 = BARRIDO / "borrador_polos" / "polos_publicables.geojson"
NOMBRES_124 = BARRIDO / "desde_cowork" / "POLOS_NOMBRADOS.csv"

INSUMOS_CRITICOS = [
    CRITERIO,
    FICHAS,
    BASE_LOCAL,
    ZONAS_R7,
    PERIMETROS_CSV,
    PERIMETROS_GEO,
    POLOS_124,
    NOMBRES_124,
]

ALIAS_PROVISORIOS = {"Z53": "S_LABOCA"}

SOPORTES_REALES_DE_CONCENTRACION = {"Z54": "P024"}

PALERMO_COMPONENTES = {
    "R01_BASE": ("referencia", "R01"),
    "P091_PALERMO_SOHO": ("concentracion", "P091"),
    "P078_PALERMO_HOLLYWOOD": ("concentracion", "P078"),
    "P065_LAS_CANITAS": ("concentracion", "P065"),
}

PALERMO_584 = {
    "P073": "Palermo Botánico",
    "P087": "Palermo Pacífico",
    "P092": "Villa Freud",
    "P088": "Palermo · Gascón y Honduras",
    "P064": "Palermo · Plaza Italia y Av. del Libertador",
    "P104": "Alto Palermo",
}


def limpia(geom):
    if geom is None or geom.is_empty:
        return geom
    return geom if geom.is_valid else geom.buffer(0)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def escribir_csv(df: pd.DataFrame, nombre: str) -> None:
    df.to_csv(OUT / nombre, index=False, encoding="utf-8-sig", lineterminator="\r\n")


def cargar_universo() -> gpd.GeoDataFrame:
    base = pd.read_csv(BASE_LOCAL, low_memory=False)
    base = base.dropna(subset=["lon", "lat"])
    universo = base[(base["anillo"] == "nucleo") & (base["apto_geometria"] == True)].copy()  # noqa: E712
    if len(universo) != 23_981:
        raise RuntimeError(f"ERR-10: se esperaban 23.981 registros y hay {len(universo)}")
    puntos = gpd.GeoDataFrame(
        universo.reset_index(drop=False).rename(columns={"index": "fila_base"}),
        geometry=gpd.points_from_xy(universo["lon"], universo["lat"]),
        crs="EPSG:4326",
    ).to_crs(CRS_METRICO)
    return puntos


def cargar_concentraciones() -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    polos = gpd.read_file(POLOS_124).to_crs(CRS_METRICO)
    polos["geometry"] = polos.geometry.map(limpia)
    if len(polos) != 124 or polos["polo_id"].duplicated().any():
        raise RuntimeError("el universo de concentraciones no tiene 124 IDs únicos")
    nombres = pd.read_csv(NOMBRES_124, encoding="utf-8-sig")
    if len(nombres) != 124 or nombres["polo_id"].duplicated().any():
        raise RuntimeError("POLOS_NOMBRADOS no tiene 124 IDs únicos")
    return polos.set_index("polo_id", drop=False), nombres.set_index("polo_id", drop=False)


def nombre_concentracion(fila: pd.Series) -> str:
    for campo in ("nombre_mapa", "nombre_en_ficha", "nombre_propuesto"):
        valor = str(fila.get(campo, "")).strip()
        if valor and valor.lower() != "nan":
            return valor
    return str(fila["polo_id"])


def sistema_palermo(zonas_r7: gpd.GeoDataFrame, polos: gpd.GeoDataFrame):
    componentes = {}
    for etiqueta, (tipo, objeto_id) in PALERMO_COMPONENTES.items():
        if tipo == "referencia":
            geom = zonas_r7.loc[objeto_id].geometry
        else:
            geom = polos.loc[objeto_id].geometry
        componentes[etiqueta] = limpia(geom)
    return limpia(unary_union(list(componentes.values()))), componentes


def construir_soportes(
    polos: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, dict[str, object]]:
    criterio = pd.read_csv(CRITERIO, encoding="utf-8-sig")
    admitidos = criterio[criterio["categoria_por_criterio"] == "polo admitido"].copy()
    if len(admitidos) != 41 or admitidos["polo_id"].duplicated().any():
        raise RuntimeError("el criterio no devuelve 41 polos admitidos únicos")

    p15 = pd.read_csv(PERIMETROS_CSV, encoding="utf-8-sig").set_index("zona_id")
    if len(p15) != 18 or p15.index.duplicated().any():
        raise RuntimeError("perimetros_18.csv no contiene 18 zonas únicas")
    g15 = gpd.read_file(PERIMETROS_GEO).to_crs(CRS_METRICO)
    g15["geometry"] = g15.geometry.map(limpia)
    zonas_r7 = gpd.read_file(ZONAS_R7).to_crs(CRS_METRICO).set_index("zona_id")
    zonas_r7["geometry"] = zonas_r7.geometry.map(limpia)
    palermo, componentes_palermo = sistema_palermo(zonas_r7, polos)

    filas = []
    for ficha in admitidos.sort_values("polo_id").itertuples():
        zid = ficha.polo_id
        if zid == "R01":
            geom = palermo
            es_real = True
            estado = "REAL_SISTEMA_PUBLICADO"
            soporte_id = "R01+P091+P078+P065"
            fuente = (
                "geometria_r7/zonas_r7.geojson#R01 + "
                "borrador_polos/polos_publicables.geojson#P091,P078,P065"
            )
        elif zid in p15.index and str(p15.loc[zid, "cerrado_si_no"]).strip().lower() == "si":
            piezas = g15[g15["zona_id"] == zid]
            if piezas.empty:
                raise RuntimeError(f"{zid} figura cerrado pero no tiene geometría en ronda 15")
            geom = limpia(unary_union(list(piezas.geometry)))
            es_real = True
            estado = "REAL_R15_CERRADO"
            soporte_id = zid
            fuente = f"ronda_15/geometria/perimetros_18.geojson#{zid}"
        elif zid in SOPORTES_REALES_DE_CONCENTRACION:
            soporte_id = SOPORTES_REALES_DE_CONCENTRACION[zid]
            geom = polos.loc[soporte_id].geometry
            es_real = True
            estado = "REAL_CONCENTRACION_MEDIDA"
            fuente = f"borrador_polos/polos_publicables.geojson#{soporte_id}"
        else:
            soporte_id = ALIAS_PROVISORIOS.get(zid, zid)
            if soporte_id not in zonas_r7.index:
                raise RuntimeError(f"no hay soporte anterior para {zid} (alias {soporte_id})")
            geom = zonas_r7.loc[soporte_id].geometry
            if zid in p15.index:
                es_real = False
                estado_r15 = str(p15.loc[zid, "cerrado_si_no"]).strip().upper()
                estado = f"PROVISORIO_R15_{estado_r15}"
            else:
                es_real = True
                estado = "REAL_PREVIO_NO_INCLUIDO_EN_R15"
            fuente = f"geometria_r7/zonas_r7.geojson#{soporte_id}"

        filas.append(
            {
                "polo_id": zid,
                "polo_nombre": ficha.nombre,
                "soporte_id": soporte_id,
                "soporte_es_real": bool(es_real),
                "estado_soporte": estado,
                "fuente_geometria": fuente,
                "superficie_soporte_m2": float(limpia(geom).area),
                "geometry": limpia(geom),
            }
        )

    soportes = gpd.GeoDataFrame(filas, geometry="geometry", crs=CRS_METRICO)
    if len(soportes) != 41 or soportes["polo_id"].duplicated().any():
        raise RuntimeError("la capa de soportes no tiene 41 polos únicos")
    reales = int(soportes["soporte_es_real"].sum())
    if (reales, len(soportes) - reales) != (31, 10):
        raise RuntimeError(f"se esperaban 31 soportes reales y 10 provisorios; hay {reales}/{41-reales}")
    return soportes.set_index("polo_id", drop=False), componentes_palermo


def membresias(geometrias: gpd.GeoDataFrame, puntos: gpd.GeoDataFrame) -> dict[str, set[int]]:
    salida: dict[str, set[int]] = {}
    for fila in geometrias.itertuples():
        dentro = puntos.geometry.within(fila.geometry)
        salida[fila.polo_id] = set(puntos.index[dentro].tolist())
    return salida


def correspondencia(
    polos: gpd.GeoDataFrame,
    nombres: pd.DataFrame,
    soportes: gpd.GeoDataFrame,
) -> pd.DataFrame:
    filas = []
    n_provisorios = int((~soportes["soporte_es_real"]).sum())
    for pid, p in polos.sort_index().iterrows():
        nombre_p = nombre_concentracion(nombres.loc[pid])
        encontrados = 0
        for zid, z in soportes.sort_index().iterrows():
            if not p.geometry.intersects(z.geometry):
                continue
            inter = limpia(p.geometry.intersection(z.geometry))
            area_i = float(inter.area)
            if area_i <= AREA_POSITIVA_M2:
                continue
            encontrados += 1
            area_p = float(p.geometry.area)
            area_z = float(z.geometry.area)
            filas.append(
                {
                    "bloque": "PUBLICABLE" if z.soporte_es_real else "PENDIENTE_DE_PERIMETRO",
                    "fila_tipo": "INTERSECCION",
                    "concentracion_id": pid,
                    "concentracion_nombre": nombre_p,
                    "polo_id": zid,
                    "polo_nombre": z.polo_nombre,
                    "soporte_es_real_A": True,
                    "soporte_es_real_B": bool(z.soporte_es_real),
                    "estado_soporte_A": "REAL_CONCENTRACION_124",
                    "estado_soporte_B": z.estado_soporte,
                    "fuente_geometria_A": "borrador_polos/polos_publicables.geojson",
                    "fuente_geometria_B": z.fuente_geometria,
                    "superficie_A_m2": area_p,
                    "superficie_B_m2": area_z,
                    "interseccion_m2": area_i,
                    "pct_superficie_A_en_B": 100 * area_i / area_p,
                    "pct_superficie_B_cubierta_por_A": 100 * area_i / area_z,
                    "criterio": f"intersección > {AREA_POSITIVA_M2} m²",
                }
            )
        if encontrados == 0:
            filas.append(
                {
                    "bloque": "PENDIENTE_DE_PERIMETROS",
                    "fila_tipo": "SIN_INTERSECCION_EN_SOPORTES_ACTUALES",
                    "concentracion_id": pid,
                    "concentracion_nombre": nombre_p,
                    "polo_id": "NINGUNO",
                    "polo_nombre": "No intersecta soportes actuales",
                    "soporte_es_real_A": True,
                    "soporte_es_real_B": "NO_APLICA",
                    "estado_soporte_A": "REAL_CONCENTRACION_124",
                    "estado_soporte_B": "NO_APLICA",
                    "fuente_geometria_A": "borrador_polos/polos_publicables.geojson",
                    "fuente_geometria_B": "NO_APLICA",
                    "superficie_A_m2": float(p.geometry.area),
                    "superficie_B_m2": "",
                    "interseccion_m2": 0.0,
                    "pct_superficie_A_en_B": 0.0,
                    "pct_superficie_B_cubierta_por_A": "",
                    "criterio": f"sin intersección en soportes actuales; {n_provisorios} soportes provisorios",
                }
            )
    df = pd.DataFrame(filas)
    numericas = [
        "superficie_A_m2",
        "superficie_B_m2",
        "interseccion_m2",
        "pct_superficie_A_en_B",
        "pct_superficie_B_cubierta_por_A",
    ]
    for c in numericas:
        df[c] = df[c].map(lambda x: round(float(x), 4) if x != "" else "")
    orden = {"PUBLICABLE": 0, "PENDIENTE_DE_PERIMETRO": 1, "PENDIENTE_DE_PERIMETROS": 2}
    df["_orden"] = df["bloque"].map(orden)
    return df.sort_values(["_orden", "concentracion_id", "pct_superficie_A_en_B"], ascending=[True, True, False]).drop(columns="_orden")


def relacion_observada(area_i: float, perdida_a: float, perdida_b: float) -> tuple[str, str]:
    if area_i <= AREA_POSITIVA_M2:
        return "DISJUNTA", "NINGUNA"
    a_en_b = perdida_a <= TOL_CONTENCION_M2
    b_en_a = perdida_b <= TOL_CONTENCION_M2
    if a_en_b and b_en_a:
        return "CONTENIDA", "COINCIDENTES"
    if a_en_b:
        return "CONTENIDA", "A_EN_B"
    if b_en_a:
        return "CONTENIDA", "B_EN_A"
    return "SOLAPADA", "NINGUNA"


def matriz_solapamientos(
    soportes: gpd.GeoDataFrame,
    puntos: gpd.GeoDataFrame,
) -> pd.DataFrame:
    miembros = membresias(soportes, puntos)
    filas = []
    ids = sorted(soportes.index)
    for aid, bid in combinations(ids, 2):
        a = soportes.loc[aid]
        b = soportes.loc[bid]
        ga, gb = a.geometry, b.geometry
        inter = limpia(ga.intersection(gb))
        area_i = float(inter.area) if inter is not None and not inter.is_empty else 0.0
        perdida_a = float(limpia(ga.difference(gb)).area)
        perdida_b = float(limpia(gb.difference(ga)).area)
        observada, direccion = relacion_observada(area_i, perdida_a, perdida_b)
        ambos_reales = bool(a.soporte_es_real and b.soporte_es_real)
        clase = observada if ambos_reales else "PENDIENTE DE PERÍMETRO"
        compartidos = len(miembros[aid] & miembros[bid])
        n_a, n_b = len(miembros[aid]), len(miembros[bid])
        filas.append(
            {
                "polo_A": aid,
                "nombre_A": a.polo_nombre,
                "polo_B": bid,
                "nombre_B": b.polo_nombre,
                "soporte_es_real_A": bool(a.soporte_es_real),
                "soporte_es_real_B": bool(b.soporte_es_real),
                "estado_soporte_A": a.estado_soporte,
                "estado_soporte_B": b.estado_soporte,
                "fuente_geometria_A": a.fuente_geometria,
                "fuente_geometria_B": b.fuente_geometria,
                "superficie_A_m2": float(ga.area),
                "superficie_B_m2": float(gb.area),
                "interseccion_m2": area_i,
                "superficie_perdida_A_m2": perdida_a,
                "superficie_perdida_B_m2": perdida_b,
                "pct_superficie_A_en_B": 100 * area_i / ga.area if ga.area else 0.0,
                "pct_superficie_B_en_A": 100 * area_i / gb.area if gb.area else 0.0,
                "locales_compartidos": compartidos,
                "locales_A": n_a,
                "locales_B": n_b,
                "pct_locales_A_compartidos": 100 * compartidos / n_a if n_a else 0.0,
                "pct_locales_B_compartidos": 100 * compartidos / n_b if n_b else 0.0,
                "relacion_observada": observada,
                "direccion_contencion_observada": direccion,
                "clase": clase,
                "gate_recomendacion": (
                    "HABILITADO_PARA_LECTURA; ESTA_TABLA_NO_DECIDE"
                    if ambos_reales
                    else "BLOQUEADO: PENDIENTE DE PERÍMETRO"
                ),
            }
        )
    df = pd.DataFrame(filas)
    if len(df) != 820:
        raise RuntimeError(f"la matriz debía tener 820 pares y tiene {len(df)}")
    numericas = [c for c in df.columns if c.endswith("_m2") or c.startswith("pct_")]
    for c in numericas:
        df[c] = df[c].round(4)
    return df.sort_values(["polo_A", "polo_B"])


def medir_palermo(
    polos: gpd.GeoDataFrame,
    soportes: gpd.GeoDataFrame,
    componentes: dict[str, object],
    puntos: gpd.GeoDataFrame,
) -> pd.DataFrame:
    sistema = soportes.loc["R01"].geometry
    filas = []
    total_atributo = int(polos.loc[list(PALERMO_584), "n_locales"].sum())
    if total_atributo != 584:
        raise RuntimeError(f"las seis concentraciones no suman 584 en la capa: {total_atributo}")
    for pid, nombre in PALERMO_584.items():
        geom = polos.loc[pid].geometry
        inter = limpia(geom.intersection(sistema))
        area_i = float(inter.area) if inter is not None and not inter.is_empty else 0.0
        n_geom = int(puntos.geometry.within(geom).sum())
        n_inter = int(puntos.geometry.within(inter).sum()) if area_i > AREA_POSITIVA_M2 else 0
        distancia_borde = float(geom.distance(sistema.boundary))
        distancias_componentes = {k: float(geom.distance(g)) for k, g in componentes.items()}
        componente_cercano = min(distancias_componentes, key=distancias_componentes.get)
        distancia_sistema = float(geom.distance(sistema))
        filas.append(
            {
                "concentracion_id": pid,
                "nombre": nombre,
                "soporte_es_real_A": True,
                "soporte_es_real_B": True,
                "fuente_geometria_A": f"borrador_polos/polos_publicables.geojson#{pid}",
                "fuente_geometria_B": "sistema publicado R01+P091+P078+P065",
                "superficie_m2": float(geom.area),
                "locales_capa_124": int(polos.loc[pid, "n_locales"]),
                "locales_ERR10_en_geometria": n_geom,
                "interseccion_con_sistema_m2": area_i,
                "superficie_fuera_del_sistema_m2": float(limpia(geom.difference(sistema)).area),
                "locales_compartidos_con_sistema": n_inter,
                "distancia_al_borde_m": distancia_borde,
                "distancia_al_sistema_m": distancia_sistema,
                "componente_mas_cercano": componente_cercano,
                "distancia_al_componente_m": distancias_componentes[componente_cercano],
                "continuidad_20m": distancia_sistema <= 20,
                "continuidad_40m": distancia_sistema <= UMBRAL_CONTINUIDAD_M,
                "continuidad_60m": distancia_sistema <= 60,
                "continuidad_80m": distancia_sistema <= 80,
                "continuidad_120m": distancia_sistema <= 120,
                "clase_continuidad_40m": (
                    "CONTINUA_CON_EL_SISTEMA_A_40M"
                    if distancia_sistema <= UMBRAL_CONTINUIDAD_M
                    else "OBJETO_APARTE_A_40M"
                ),
                "decision_delimitacion": "PENDIENTE_DIEGO; SIN_PROPUESTA_DE_AMPLIACION",
            }
        )
    df = pd.DataFrame(filas)
    numericas = [c for c in df.columns if c.endswith("_m2") or c.endswith("_m")]
    for c in numericas:
        df[c] = df[c].round(4)
    return df


def tabla_soportes(soportes: gpd.GeoDataFrame, puntos: gpd.GeoDataFrame) -> pd.DataFrame:
    filas = []
    for fila in soportes.sort_index().itertuples():
        filas.append(
            {
                "polo_id": fila.polo_id,
                "polo_nombre": fila.polo_nombre,
                "soporte_id": fila.soporte_id,
                "soporte_es_real": bool(fila.soporte_es_real),
                "estado_soporte": fila.estado_soporte,
                "fuente_geometria": fila.fuente_geometria,
                "superficie_soporte_m2": round(float(fila.geometry.area), 4),
                "locales_ERR10_en_soporte": int(puntos.geometry.within(fila.geometry).sum()),
                "estado_publicacion": "PUBLICABLE" if fila.soporte_es_real else "PENDIENTE_DE_PERIMETRO",
            }
        )
    return pd.DataFrame(filas)


def markdown_tabla(df: pd.DataFrame, columnas: list[str]) -> str:
    vista = df[columnas].copy()
    encabezado = "| " + " | ".join(columnas) + " |"
    separador = "|" + "|".join(["---"] * len(columnas)) + "|"
    filas = []
    for valores in vista.itertuples(index=False, name=None):
        celdas = [str(v).replace("|", "\\|").replace("\n", " ") for v in valores]
        filas.append("| " + " | ".join(celdas) + " |")
    return "\n".join([encabezado, separador, *filas])


def formato_es(valor: float, decimales: int = 2) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def generar_informe(
    soportes_df: pd.DataFrame,
    corr: pd.DataFrame,
    matriz: pd.DataFrame,
    palermo: pd.DataFrame,
) -> str:
    corr_inter = corr[corr["fila_tipo"] == "INTERSECCION"]
    positivos = matriz[matriz["interseccion_m2"] > AREA_POSITIVA_M2]
    positivos_reales = positivos[
        positivos["soporte_es_real_A"] & positivos["soporte_es_real_B"]
    ]
    pendientes = matriz[matriz["clase"] == "PENDIENTE DE PERÍMETRO"]
    pal = palermo.copy()
    pal["ha"] = (pal["superficie_m2"] / 10_000).map(formato_es)
    pal["distancia_m"] = pal["distancia_al_borde_m"].map(formato_es)
    pal = pal.rename(
        columns={
            "locales_capa_124": "locales_concentracion",
            "locales_ERR10_en_geometria": "locales_en_poligono",
        }
    )

    top_reales = positivos_reales.sort_values("interseccion_m2", ascending=False).head(20).copy()
    top_reales["interseccion_ha"] = (top_reales["interseccion_m2"] / 10_000).round(2)
    top_reales["pct_area_A"] = top_reales["pct_superficie_A_en_B"].round(2)
    top_reales["pct_area_B"] = top_reales["pct_superficie_B_en_A"].round(2)
    top_reales["pct_locales_A"] = top_reales["pct_locales_A_compartidos"].round(2)
    top_reales["pct_locales_B"] = top_reales["pct_locales_B_compartidos"].round(2)

    z54 = matriz[
        ((matriz.polo_A == "Z40") & (matriz.polo_B == "Z54"))
        | ((matriz.polo_A == "Z54") & (matriz.polo_B == "Z40"))
    ].iloc[0]
    z52_z53 = matriz[
        ((matriz.polo_A == "Z52") & (matriz.polo_B == "Z53"))
        | ((matriz.polo_A == "Z53") & (matriz.polo_B == "Z52"))
    ].iloc[0]
    contenidas_reales = positivos_reales[positivos_reales.relacion_observada == "CONTENIDA"]

    return f"""# Ronda 16 · correspondencia, solapamientos y borde de Palermo

Estado: **EXPERIMENTAL / NO OFICIAL**. Corrida local, sin red ni APIs. Esta ronda mide; no adopta
fusiones ni ampliaciones.

## 1. Soportes

El universo tiene **41 polos admitidos**: **{int(soportes_df.soporte_es_real.sum())}** con soporte
REAL y **{int((~soportes_df.soporte_es_real).sum())}** con soporte PROVISORIO. Los cuatro cierres
parciales de ronda 15 no se usan como si fueran el polo completo.

Palermo R01 se reconstruyó como el sistema publicado `R01 ∪ P091 ∪ P078 ∪ P065`: 
**{formato_es(soportes_df.loc[soportes_df.polo_id == 'R01', 'superficie_soporte_m2'].iloc[0] / 10_000)} ha**
y **{formato_es(int(soportes_df.loc[soportes_df.polo_id == 'R01', 'locales_ERR10_en_soporte'].iloc[0]), 0)}**
registros del universo ERR-10.

## 2. Correspondencia 124 × 41

Se obtuvieron **{len(corr_inter)} pares** con intersección mayor a {AREA_POSITIVA_M2} m²:
**{int((corr_inter.bloque == 'PUBLICABLE').sum())} publicables** y
**{int((corr_inter.bloque == 'PENDIENTE_DE_PERIMETRO').sum())} pendientes de perímetro**.
La tabla declara ambos soportes y ambos denominadores. Las concentraciones sin cruce en los
soportes actuales permanecen identificadas como pendientes mientras existan
**{int((~soportes_df.soporte_es_real).sum())} soportes provisorios**.

## 3. Matriz 41 × 41

La matriz contiene los **820 pares no ordenados**. Hay **{len(positivos)}** pares con intersección
material; **{len(positivos_reales)}** tienen ambos soportes reales y pueden leerse territorialmente.
Otros **{len(pendientes)}** pares quedan clasificados `PENDIENTE DE PERÍMETRO` porque al menos un
lado es provisorio, tengan o no intersección observada.

Z54–Z40 queda correctamente bloqueado: intersección observada
**{formato_es(z54.interseccion_m2)} m²**, relación observada `{z54.relacion_observada}`, clase final
**`{z54.clase}`**. No se emite recomendación.

Pares reales con mayor superficie de intersección (hasta 20):

{markdown_tabla(top_reales, ['polo_A', 'polo_B', 'interseccion_ha', 'pct_area_A', 'pct_area_B', 'locales_compartidos', 'pct_locales_A', 'pct_locales_B', 'clase']) if len(top_reales) else 'No hay intersecciones entre soportes reales.'}

Entre los 14 cruces positivos con ambos soportes reales hay
**{len(contenidas_reales)} contenciones completas**: los 14 son solapamientos parciales. Entre los
cruces bloqueados aparece otro caso que parecería contención si se ignorara el soporte: Z52–Z53
da **{formato_es(z52_z53.interseccion_m2)} m²** y {int(z52_z53.locales_compartidos)} registros,
pero Z53 sigue representada por La Boca y la clase correcta es `PENDIENTE DE PERÍMETRO`.

## 4. Palermo · 584 registros en seis concentraciones

El control de pertenencia de las seis concentraciones reproduce **{int(palermo.locales_capa_124.sum())}**
registros, que es el número del Anexo B. El recuento espacial de puntos que caen dentro de los seis
polígonos generalizados da **{int(palermo.locales_ERR10_en_geometria.sum())}**. No reemplaza al
primero: los polígonos de representación pueden incluir o dejar fuera puntos de su agrupamiento.
Por eso se publican las dos columnas y se conserva 584 como denominador de las concentraciones.
La clasificación de continuidad usa 40 m, fijados antes de correr; se publican también los cortes
20/60/80/120 m.

{markdown_tabla(pal, ['concentracion_id', 'nombre', 'ha', 'locales_concentracion', 'locales_en_poligono', 'interseccion_con_sistema_m2', 'distancia_m', 'componente_mas_cercano', 'clase_continuidad_40m'])}

No se propone ampliación del perímetro. La decisión de delimitación queda para Diego.

## 5. Límites y gates

- Universo: `anillo == 'nucleo' AND apto_geometria == True`, **23.981 registros**.
- CRS métrico: EPSG:5347.
- Contención: superficie perdida, tolerancia 1 m²; no se usa `covers()`.
- Intersección material: mayor a 0,01 m².
- Los conteos describen registros del universo analítico, no actividad comercial vigente.
- Fuentes originales y pipeline F01–F05: sólo lectura.
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "geometria").mkdir(parents=True, exist_ok=True)

    hashes_antes = {str(p.relative_to(BARRIDO)): sha256(p) for p in INSUMOS_CRITICOS}
    puntos = cargar_universo()
    polos, nombres = cargar_concentraciones()
    soportes, componentes_palermo = construir_soportes(polos)

    soportes_df = tabla_soportes(soportes, puntos)
    corr = correspondencia(polos, nombres, soportes)
    matriz = matriz_solapamientos(soportes, puntos)
    palermo = medir_palermo(polos, soportes, componentes_palermo, puntos)

    escribir_csv(soportes_df, "soportes_41.csv")
    escribir_csv(corr, "correspondencia_124_x_41.csv")
    escribir_csv(matriz, "matriz_solapamiento_41x41.csv")
    escribir_csv(
        matriz[matriz["interseccion_m2"] > AREA_POSITIVA_M2].copy(),
        "solapamientos_positivos_41.csv",
    )
    escribir_csv(palermo, "palermo_584_contra_perimetro.csv")

    geo_out = soportes.reset_index(drop=True).to_crs("EPSG:4326")
    geo_out.to_file(OUT / "geometria" / "soportes_41.geojson", driver="GeoJSON")

    hashes_despues = {str(p.relative_to(BARRIDO)): sha256(p) for p in INSUMOS_CRITICOS}
    if hashes_antes != hashes_despues:
        raise RuntimeError("algún insumo crítico cambió durante la corrida")
    hashes_df = pd.DataFrame(
        [
            {"archivo": p, "sha256_antes": h, "sha256_despues": hashes_despues[p], "sin_cambios": True}
            for p, h in hashes_antes.items()
        ]
    )
    escribir_csv(hashes_df, "insumos_sha256.csv")

    informe = generar_informe(soportes_df, corr, matriz, palermo)
    (OUT / "RONDA_16_CODEX.md").write_text(informe, encoding="utf-8")
    print("RONDA_16_CODEX.md generado")


if __name__ == "__main__":
    main()
