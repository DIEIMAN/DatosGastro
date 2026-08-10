"""Genera las tres salidas mecánicas de la ronda 14 de Codex.

Sólo lee insumos existentes. Escribe exclusivamente en esta carpeta. No llama APIs.
"""
from __future__ import annotations

import io
import re
import sys
import unittest
import unicodedata
from collections import Counter
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parents[3]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts" / "barrido_ciudad"
sys.path.insert(0, str(SCRIPTS))

from callejero_canonico import cargar as cargar_callejero_canonico  # noqa: E402
from callejero_canonico import familias as familias_callejero  # noqa: E402
from normalizar_calles import clave_calle, resolutor_desde  # noqa: E402
from polos_seis_vias import continuidad  # noqa: E402
from polos_soporte import CALLEJERO, CRS_METRICO, barrios, puntos_base, sin_tildes  # noqa: E402
from ronda_7_geometria_ampliaciones import marco_de, tramo_por_altura  # noqa: E402


UNIVERSO_ESPERADO = 23_981
CONTROLES_ESPERADOS = {"R01": 1358, "P091": 772, "P078": 595, "P065": 361}
UMBRALES_M = (20, 40, 60, 80, 120)
BUFFER_CORREDOR_M = 150
AREA_MINIMA_INTERSECCION_M2 = 0.01

AFECTADOS_CALLES = {
    "P001", "P015", "P022", "P028", "P047", "P048", "P050", "P071", "P072-1"
}

# Estas equivalencias son las nueve observaciones declaradas en el pedido. La agrupación general
# la hacen los módulos existentes; estas claves sólo resuelven los residuos S/N, inicial y
# CAP/CAPITAN que el callejero no puede decidir mirando únicamente el texto.
ALIAS_CALLES = {
    "COSTANERA RAFAEL OBLIGADO": "Costanera Rafael Obligado",
    "COSTANERA RAFAEL OBLIGADO S N": "Costanera Rafael Obligado",
    "BARCO CENTENERA": "Del Barco Centenera",
    "BARCO DEL CENTENERA": "Del Barco Centenera",
    "DEL BARCO CENTENERA": "Del Barco Centenera",
    "MOSCONI": "Mosconi",
    "E MOSCONI": "Mosconi",
    "RICARDO BALBIN": "Ricardo Balbin",
    "DOCTOR RICARDO BALBIN": "Ricardo Balbin",
    "HONORIO PUEYRREDON": "Honorio Pueyrredon",
    "DOCTOR HONORIO PUEYRREDON": "Honorio Pueyrredon",
    "JUAN F ARANGUREN": "Juan F Aranguren",
    "DOCTOR JUAN F ARANGUREN": "Juan F Aranguren",
    "CAP RAMON FREIRE": "Capitan Ramon Freire",
    "CAPITAN RAMON FREIRE": "Capitan Ramon Freire",
    "JUANA AZURDUY": "Juana Azurduy",
    "AZURDUY JUANA": "Juana Azurduy",
}


def clave_simple(texto: str) -> str:
    limpio = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9]+", " ", limpio.upper())).strip()


def sin_vacios(tabla: pd.DataFrame, nombre: str) -> pd.DataFrame:
    salida = tabla.copy()
    salida = salida.replace([np.inf, -np.inf], np.nan)
    salida = salida.fillna("FALTA: valor nulo no producido por el instrumento")
    for columna in salida.columns:
        vacias = salida[columna].astype(str).str.strip().eq("")
        if vacias.any():
            salida.loc[vacias, columna] = f"FALTA: {columna} vacío en el insumo"
    if salida.astype(str).apply(lambda s: s.str.strip().eq("")).any().any():
        raise RuntimeError(f"{nombre}: quedaron celdas vacías")
    return salida


def escribir_csv(tabla: pd.DataFrame, nombre: str) -> None:
    sin_vacios(tabla, nombre).to_csv(OUT / nombre, index=False, encoding="utf-8-sig")


def cargar_universo() -> gpd.GeoDataFrame:
    base = pd.read_csv(BARRIDO / "base" / "local.csv", low_memory=False)
    universo = base[(base.anillo == "nucleo") & (base.apto_geometria == True)].copy()  # noqa: E712
    if len(universo) != UNIVERSO_ESPERADO:
        raise RuntimeError(f"universo incorrecto: {len(universo)} != {UNIVERSO_ESPERADO}")
    return gpd.GeoDataFrame(
        universo,
        geometry=gpd.points_from_xy(universo.lon, universo.lat),
        crs="EPSG:4326",
    ).to_crs(CRS_METRICO).reset_index(drop=True)


def construir_montes_de_oca(callejero: gpd.GeoDataFrame) -> tuple[object, str]:
    marco = marco_de(barrios(), ["Barracas"])
    eje, n_segmentos = tramo_por_altura(
        callejero, "MONTES DE OCA, MANUEL AV.", 280, 1702, marco
    )
    if eje is None or eje.is_empty:
        raise RuntimeError("no se pudo construir Av. Montes de Oca 280-1702")
    geometria = eje.buffer(BUFFER_CORREDOR_M)
    detalle = (
        f"callejero GCBA; {n_segmentos} segmentos que solapan alturas 280-1702; "
        f"buffer convencional {BUFFER_CORREDOR_M} m"
    )
    return geometria, detalle


def validar_controles(universo: gpd.GeoDataFrame, polos: gpd.GeoDataFrame,
                      zonas: gpd.GeoDataFrame) -> dict[str, int]:
    p = polos.set_index("polo_id")
    z = zonas.set_index("zona_id")
    obtenidos = {
        "R01": int(universo.within(z.loc["R01"].geometry).sum()),
        "P091": int(universo.within(p.loc["P091"].geometry).sum()),
        "P078": int(universo.within(p.loc["P078"].geometry).sum()),
        "P065": int(universo.within(p.loc["P065"].geometry).sum()),
    }
    if obtenidos != CONTROLES_ESPERADOS:
        raise RuntimeError(f"falló el gate del universo: {obtenidos}")
    return obtenidos


def nombre_p(row: pd.Series) -> str:
    for columna in ("nombre_mapa", "nombre_en_ficha", "nombre_propuesto"):
        valor = str(row.get(columna, "")).strip()
        if valor and valor.lower() != "nan":
            return valor
    return f"FALTA: POLOS_NOMBRADOS.csv no trae nombre para {row['polo_id']}"


def preparar_zonas(callejero: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, str]:
    fichas = pd.read_csv(
        BARRIDO / "desde_cowork" / "evidencia_2026" / "fichas_corpus_polos.csv",
        encoding="utf-8-sig",
    )
    admitidas = fichas[~fichas.estado.astype(str).str.startswith("NO ENTRA")].copy()
    if len(admitidas) != 41:
        raise RuntimeError(f"se esperaban 41 fichas no rechazadas y hay {len(admitidas)}")
    geometrias = gpd.read_file(BARRIDO / "geometria_r7" / "zonas_r7.geojson").to_crs(
        CRS_METRICO
    ).set_index("zona_id")
    faltan = sorted(set(admitidas.polo_id) - set(geometrias.index))
    if faltan:
        raise RuntimeError(f"faltan geometrías para fichas: {faltan}")

    filas = []
    for ficha in admitidas.itertuples():
        geom = geometrias.loc[ficha.polo_id].geometry
        filas.append({
            "rz_id": ficha.polo_id,
            "rz_nombre": ficha.nombre_ficha,
            "estado_ficha": ficha.estado,
            "fuente_geometria": "outputs/BARRIDO_CIUDAD_2026-08/geometria_r7/zonas_r7.geojson",
            "geometry": geom,
        })
    montes, detalle = construir_montes_de_oca(callejero)
    filas.append({
        "rz_id": "MDO280_1702",
        "rz_nombre": "Av. Montes de Oca 280-1702",
        "estado_ficha": "ADICION_PEDIDA_RONDA_14",
        "fuente_geometria": detalle,
        "geometry": montes,
    })
    zonas = gpd.GeoDataFrame(filas, geometry="geometry", crs=CRS_METRICO)
    if len(zonas) != 42 or zonas.rz_id.duplicated().any():
        raise RuntimeError("el segundo universo no quedó en 42 geometrías únicas")
    return zonas, detalle


def tarea_correspondencia(polos: gpd.GeoDataFrame, nombres: pd.DataFrame,
                          zonas42: gpd.GeoDataFrame) -> tuple[int, list[str], list[str]]:
    nombres = nombres.set_index("polo_id")
    pares: list[dict] = []
    for p in polos.sort_values("polo_id").itertuples():
        for z in zonas42.sort_values("rz_id").itertuples():
            if not p.geometry.intersects(z.geometry):
                continue
            comun = p.geometry.intersection(z.geometry).area
            if comun <= AREA_MINIMA_INTERSECCION_M2:
                continue
            nombre = nombre_p(nombres.loc[p.polo_id])
            pares.append({
                "p_id": p.polo_id,
                "p_nombre": nombre,
                "rz_id": z.rz_id,
                "rz_nombre": z.rz_nombre,
                "area_p_m2": p.geometry.area,
                "area_rz_m2": z.geometry.area,
                "area_interseccion_m2": comun,
                "pct_superficie_p_en_rz": 100 * comun / p.geometry.area,
                "pct_superficie_rz_cubierta_por_p": 100 * comun / z.geometry.area,
                "fuente_rz": z.fuente_geometria,
            })

    p_con = {r["p_id"] for r in pares}
    z_con = {r["rz_id"] for r in pares}
    p_sin = sorted(set(polos.polo_id) - p_con)
    z_sin = sorted(set(zonas42.rz_id) - z_con)
    filas: list[dict] = []

    for r in sorted(pares, key=lambda x: (x["p_id"], -x["pct_superficie_p_en_rz"], x["rz_id"])):
        base = {
            "area_interseccion_m2": round(r["area_interseccion_m2"], 2),
            "pct_superficie_p": round(r["pct_superficie_p_en_rz"], 4),
            "pct_superficie_rz": round(r["pct_superficie_rz_cubierta_por_p"], 4),
            "criterio": f"intersección de superficie > {AREA_MINIMA_INTERSECCION_M2} m²",
        }
        filas.append({
            "seccion": "P_A_RZ",
            "origen_id": r["p_id"], "origen_nombre": r["p_nombre"],
            "destino_id": r["rz_id"], "destino_nombre": r["rz_nombre"],
            "pct_superficie_origen": round(r["pct_superficie_p_en_rz"], 4),
            "denominador_pct_origen": "superficie del P",
            "fuente_geometria_origen": "borrador_polos/polos_publicables.geojson",
            "fuente_geometria_destino": r["fuente_rz"], **base,
        })
    for r in sorted(pares, key=lambda x: (x["rz_id"], -x["pct_superficie_rz_cubierta_por_p"], x["p_id"])):
        base = {
            "area_interseccion_m2": round(r["area_interseccion_m2"], 2),
            "pct_superficie_p": round(r["pct_superficie_p_en_rz"], 4),
            "pct_superficie_rz": round(r["pct_superficie_rz_cubierta_por_p"], 4),
            "criterio": f"intersección de superficie > {AREA_MINIMA_INTERSECCION_M2} m²",
        }
        filas.append({
            "seccion": "RZ_A_P",
            "origen_id": r["rz_id"], "origen_nombre": r["rz_nombre"],
            "destino_id": r["p_id"], "destino_nombre": r["p_nombre"],
            "pct_superficie_origen": round(r["pct_superficie_rz_cubierta_por_p"], 4),
            "denominador_pct_origen": "superficie del R/Z",
            "fuente_geometria_origen": r["fuente_rz"],
            "fuente_geometria_destino": "borrador_polos/polos_publicables.geojson", **base,
        })

    for pid in p_sin:
        filas.append({
            "seccion": "P_SIN_RZ", "origen_id": pid,
            "origen_nombre": nombre_p(nombres.loc[pid]),
            "destino_id": "NINGUNO", "destino_nombre": "No intersecta ningún R/Z del universo",
            "area_interseccion_m2": "NO_APLICA: no hubo intersección",
            "pct_superficie_origen": 0.0, "denominador_pct_origen": "superficie del P",
            "pct_superficie_p": 0.0, "pct_superficie_rz": "NO_APLICA: no hubo R/Z",
            "criterio": f"sin intersección de superficie > {AREA_MINIMA_INTERSECCION_M2} m²",
            "fuente_geometria_origen": "borrador_polos/polos_publicables.geojson",
            "fuente_geometria_destino": "NO_APLICA: no hubo R/Z",
        })
    zonas_idx = zonas42.set_index("rz_id")
    for zid in z_sin:
        z = zonas_idx.loc[zid]
        filas.append({
            "seccion": "RZ_SIN_P", "origen_id": zid, "origen_nombre": z.rz_nombre,
            "destino_id": "NINGUNO", "destino_nombre": "No contiene ningún P del universo",
            "area_interseccion_m2": "NO_APLICA: no hubo intersección",
            "pct_superficie_origen": 0.0, "denominador_pct_origen": "superficie del R/Z",
            "pct_superficie_p": "NO_APLICA: no hubo P", "pct_superficie_rz": 0.0,
            "criterio": f"sin intersección de superficie > {AREA_MINIMA_INTERSECCION_M2} m²",
            "fuente_geometria_origen": z.fuente_geometria,
            "fuente_geometria_destino": "NO_APLICA: no hubo P",
        })
    escribir_csv(pd.DataFrame(filas), "correspondencia_124_x_42.csv")
    return len(pares), p_sin, z_sin


def canonizar_alias(etiqueta: str) -> str:
    return ALIAS_CALLES.get(clave_simple(etiqueta), etiqueta)


def ranking_canonico(cuerpo: pd.DataFrame, resolutor) -> str:
    conteos: Counter[str] = Counter()
    orden_aparicion: dict[str, int] = {}
    for direccion in cuerpo.direccion_norm.dropna():
        etiqueta = resolutor.etiqueta(direccion)
        etiqueta = canonizar_alias(etiqueta)
        if len(etiqueta.strip()) > 2 and any(c.isalpha() for c in etiqueta):
            orden_aparicion.setdefault(etiqueta, len(orden_aparicion))
            conteos[etiqueta] += 1
    top = sorted(conteos.items(), key=lambda kv: (-kv[1], orden_aparicion[kv[0]]))[:6]
    return "; ".join(f"{calle.title()} ({n})" for calle, n in top)


def correr_tests_callejero() -> int:
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName("test_callejero_canonico")
    resultado = unittest.TextTestRunner(stream=stream, verbosity=0).run(suite)
    if not resultado.wasSuccessful() or resultado.testsRun != 14:
        raise RuntimeError(f"tests callejero fallaron:\n{stream.getvalue()}")
    return resultado.testsRun


def tarea_calles(universo: gpd.GeoDataFrame) -> tuple[int, int]:
    # Se carga y agrupa el callejero con el módulo pedido. La tabla de familias se usa como gate:
    # debe conservar el control negativo de las 14 pruebas y producir múltiples familias reales.
    callejero_canonico = cargar_callejero_canonico()
    familias = familias_callejero(callejero_canonico)
    if len({frozenset(v) for v in familias.values() if len(v) > 1}) <= 50:
        raise RuntimeError("el callejero canónico no produjo las familias esperadas")
    # Verificación adicional: las etiquetas que sí tienen forma oficial deben resolver contra el
    # callejero. Los residuos explícitos quedan cubiertos por ALIAS_CALLES.
    claves_oficiales = {clave_calle(n) for n in callejero_canonico.nomoficial}
    if clave_calle("Doctor Ricardo Balbin") not in claves_oficiales:
        raise RuntimeError("Ricardo Balbín no resolvió contra el callejero oficial")

    pertenencia = pd.read_csv(BARRIDO / "borrador_polos" / "pertenencia_local_polo_v3.csv")
    geo = universo.drop(columns="geometry").merge(
        pertenencia[["local_id", "polo_unido"]], on="local_id", how="left"
    )
    resolutor = resolutor_desde(geo)
    polos = pd.read_csv(
        BARRIDO / "desde_cowork" / "POLOS_NOMBRADOS.csv", encoding="utf-8-sig", dtype=str
    )
    filas = []
    for fila in polos.itertuples():
        antes = fila.calles_dominantes
        if fila.polo_id in AFECTADOS_CALLES:
            cuerpo = geo[geo.polo_unido == fila.polo_id]
            despues = ranking_canonico(cuerpo, resolutor)
        else:
            despues = antes
        cambio = antes != despues
        filas.append({
            "polo_id": fila.polo_id,
            "calles_dominantes_antes": antes,
            "calles_dominantes_despues": despues,
            "cambio": "SI" if cambio else "NO",
            "diff": f"ANTES: {antes} | DESPUES: {despues}" if cambio else "SIN_CAMBIO",
            "metodo": "normalizar_calles + callejero_canonico + aliases declarados en el pedido",
        })
    tabla = pd.DataFrame(filas)
    cambiaron = set(tabla.loc[tabla.cambio == "SI", "polo_id"])
    if cambiaron != AFECTADOS_CALLES:
        raise RuntimeError(f"el diff no quedó en las nueve filas pedidas: {sorted(cambiaron)}")
    escribir_csv(tabla, "calles_dominantes_canonicas.csv")
    return len(cambiaron), correr_tests_callejero()


def curva_para(universo: gpd.GeoDataFrame, geometria) -> tuple[int, float, list[float]]:
    miembros = universo[universo.within(geometria)]
    xy = np.c_[miembros.geometry.x.to_numpy(), miembros.geometry.y.to_numpy()]
    return len(miembros), geometria.area / 10_000, [float(continuidad(xy, m)) for m in UMBRALES_M]


def tarea_curvas(universo: gpd.GeoDataFrame, zonas_r7: gpd.GeoDataFrame,
                 montes_geom, montes_detalle: str) -> tuple[pd.DataFrame, list[float]]:
    zonas = zonas_r7.set_index("zona_id")
    n_r22, _, control = curva_para(universo, zonas.loc["R22"].geometry)
    if n_r22 != 198 or control != [2.5, 5.6, 11.6, 15.7, 31.3]:
        raise RuntimeError(f"no se reprodujo la curva control R22: n={n_r22}, curva={control}")
    objetivos = [
        ("MDO280_1702", "Av. Montes de Oca 280-1702", montes_geom, montes_detalle),
        ("R11", "Boulevard Caseros", zonas.loc["R11"].geometry,
         "outputs/BARRIDO_CIUDAD_2026-08/geometria_r7/zonas_r7.geojson"),
        ("Z28", "Monte Castro · Álvarez Jonte 4400-5300", zonas.loc["Z28"].geometry,
         "outputs/BARRIDO_CIUDAD_2026-08/geometria_r7/zonas_r7.geojson"),
        ("Z42", "Coghlan", zonas.loc["Z42"].geometry,
         "outputs/BARRIDO_CIUDAD_2026-08/geometria_r7/zonas_r7.geojson"),
    ]
    filas = []
    for zona_id, nombre, geom, fuente in objetivos:
        n, ha, curva = curva_para(universo, geom)
        filas.append({
            "zona_id": zona_id, "zona": nombre,
            "n_locales_universo": n, "superficie_soporte_ha": round(ha, 4),
            "continuidad_pct_20m": curva[0], "continuidad_pct_40m": curva[1],
            "continuidad_pct_60m": curva[2], "continuidad_pct_80m": curva[3],
            "continuidad_pct_120m": curva[4], "umbral_conjunto_m": 40,
            "continuidad_pct_umbral_conjunto": curva[1],
            "definicion": "porcentaje de puntos en la mayor componente conexa",
            "universo": "anillo == nucleo AND apto_geometria == True (n=23981)",
            "fuente_geometria": fuente,
        })
    tabla = pd.DataFrame(filas)
    escribir_csv(tabla, "curvas_continuidad_r14.csv")
    return tabla, control


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    universo = cargar_universo()
    polos = gpd.read_file(BARRIDO / "borrador_polos" / "polos_publicables.geojson").to_crs(
        CRS_METRICO
    )
    if len(polos) != 124 or polos.polo_id.duplicated().any():
        raise RuntimeError("el universo P no tiene 124 geometrías únicas")
    zonas_r7 = gpd.read_file(BARRIDO / "geometria_r7" / "zonas_r7.geojson").to_crs(CRS_METRICO)
    controles = validar_controles(universo, polos, zonas_r7)

    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)
    zonas42, montes_detalle = preparar_zonas(callejero)
    montes_geom = zonas42.loc[zonas42.rz_id == "MDO280_1702", "geometry"].iloc[0]
    nombres = pd.read_csv(
        BARRIDO / "desde_cowork" / "POLOS_NOMBRADOS.csv", encoding="utf-8-sig", dtype=str
    )
    n_pares, p_sin, z_sin = tarea_correspondencia(polos, nombres, zonas42)
    n_cambios, n_tests = tarea_calles(universo)
    curvas, control_r22 = tarea_curvas(universo, zonas_r7, montes_geom, montes_detalle)

    valores40 = "; ".join(
        f"{r.zona_id} {r.continuidad_pct_40m:.1f}%".replace(".", ",")
        for r in curvas.itertuples()
    )
    control_r22_texto = " / ".join(f"{v:.1f}".replace(".", ",") for v in control_r22)
    n_universo_texto = f"{len(universo):,}".replace(",", ".")
    controles_texto = {k: f"{v:,}".replace(",", ".") for k, v in controles.items()}
    md = f"""# Ronda 14 · Codex

Estado: **EXPERIMENTAL / NO OFICIAL**. Cero requests a APIs.

## 1. Correspondencia 124 × 42

Se cruzaron 124 polígonos P con 41 fichas no rechazadas y el corredor Av. Montes de Oca 280–1702. Se obtuvieron **{n_pares} pares con intersección de superficie**. La tabla incluye ambos sentidos y ambos denominadores. Quedaron **{len(p_sin)} P sin R/Z** y **{len(z_sin)} R/Z sin P**; las listas están en las secciones `P_SIN_RZ` y `RZ_SIN_P` del CSV.

## 2. Calles dominantes

Se regeneró el ranking de las nueve filas señaladas y se conservaron las otras 115. El diff quedó en **{n_cambios} filas**. `test_callejero_canonico.py`: **{n_tests}/{n_tests} pruebas aprobadas**, incluido el control negativo San Martín.

## 3. Curvas de continuidad

Con el universo `anillo == nucleo AND apto_geometria == True` (**{n_universo_texto} registros**), al umbral común de 40 m se obtuvo: **{valores40}**. La curva control R22 reprodujo **{control_r22_texto} %**.

## Controles y faltantes

Gate reproducido: R01={controles_texto['R01']}; Soho={controles_texto['P091']}; Hollywood={controles_texto['P078']}; Cañitas={controles_texto['P065']}. No quedó ninguna celda vacía ni medición pendiente. La continuidad es una propiedad del instrumento: porcentaje de puntos en la mayor componente conexa, no porcentaje de superficie urbana. Montes de Oca usa los segmentos del callejero que solapan 280–1702 y el buffer territorial convencional de 150 m; no usa el eje IDECBA 501–1199.

Esta corrida no escribió en fuentes ni en las carpetas `ronda_14/` y `desde_cowork/`.
"""
    (OUT / "RONDA_14_CODEX.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
