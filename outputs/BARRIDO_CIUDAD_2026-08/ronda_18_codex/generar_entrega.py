# -*- coding: utf-8 -*-
"""Genera las salidas espaciales y normaliza la capa de reconocimientos.

Lectura fijada antes de correr:

* El universo de locales es el mismo que construyó las concentraciones:
  ``anillo == nucleo`` y ``apto_geometria == True`` de ``base/local.csv``.
* Todas las áreas y distancias se calculan en EPSG:5347.
* La continuidad conserva la definición que produjo la curva ya publicada de
  Villa Pueyrredón: porcentaje de locales incluido en la componente conexa
  mayor a cada distancia. No equivale al porcentaje con algún vecino cercano.
* Mataderos, Núñez, Retiro y Villa Santa Rita se miden sobre el polígono
  administrativo del barrio. Ningún otro soporte queda administrativo.
* La tabla de hitos exteriores reproduce el universo de 60 detectado con la
  capa que usa hoy el atlas. Un contacto a hasta 3 m se trata como tolerancia
  cartográfica y se enumera aparte. La lectura territorial usa 250 m como
  convención y publica sensibilidad a 100, 250 y 500 m.

No consulta APIs, no modifica fuentes de locales ni geometrías y no exporta
teléfonos, correos o identificadores de plataformas.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import deque
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


OUT = Path(__file__).resolve().parent
BASE = OUT.parent
HITOS = BASE / "hitos" / "hitos_capa_2026.geojson"
LOCALES = BASE / "base" / "local.csv"
SOPORTES_BASE = BASE / "ronda_16_codex" / "geometria" / "soportes_41.geojson"
CIERRE = BASE / "ronda_17" / "geometria" / "perimetros_cierre.geojson"
BARRIOS = BASE / "insumos" / "caba_barrios.geojson"
ZONAS_R7 = BASE / "geometria_r7" / "zonas_r7.geojson"
CRS_METRICO = "EPSG:5347"
DISTANCIAS = (20, 40, 60, 80, 120)
TOLERANCIA_BORDE_M = 3.0
CORTE_REVISION_BORDE_M = 250.0
ADMINISTRATIVOS = {
    "Z27": "VILLA SANTA RITA",
    "Z33": "MATADEROS",
    "Z41": "NUÑEZ",
    "Z46": "RETIRO",
}
NOMBRES_CANONICOS = {
    "R16": "Donado–Holmberg",
    "R20": "García del Río",
    "Z41": "Núñez",
    "Z44": "Villa Ortúzar",
    "Z54": "Nueva Pompeya · eje Av. Sáenz",
}
REEMPLAZOS_R17 = {"Z35", "Z37", "Z39", "Z40", "Z44", "Z53", "Z54"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def escribir_csv(df: pd.DataFrame, nombre: str) -> None:
    df.to_csv(OUT / nombre, index=False, encoding="utf-8-sig", lineterminator="\r\n")


def cargar_locales() -> gpd.GeoDataFrame:
    columnas = ["local_id", "lon", "lat", "anillo", "apto_geometria"]
    df = pd.read_csv(LOCALES, usecols=columnas, low_memory=False)
    df = df[
        df["anillo"].eq("nucleo")
        & df["apto_geometria"].astype(str).str.casefold().eq("true")
    ].copy()
    return gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326",
    ).to_crs(CRS_METRICO)


def construir_soportes() -> gpd.GeoDataFrame:
    soportes = gpd.read_file(SOPORTES_BASE).to_crs(CRS_METRICO).set_index("polo_id")
    cierre = gpd.read_file(CIERRE).to_crs(CRS_METRICO)
    cierre = cierre[cierre["pieza"].eq("la zona entera, como se adopta")].set_index("zona_id")
    barrios = gpd.read_file(BARRIOS).to_crs(CRS_METRICO).set_index("BARRIO")

    for pid in REEMPLAZOS_R17:
        if pid not in cierre.index:
            raise RuntimeError(f"{pid}: falta el perímetro entero de cierre")
        fila = cierre.loc[pid]
        soportes.at[pid, "geometry"] = fila.geometry
        soportes.at[pid, "soporte_es_real"] = True
        soportes.at[pid, "estado_soporte"] = "BORDE_PROPIO_VIGENTE"
        soportes.at[pid, "fuente_geometria"] = (
            f"geometria/perimetros_cierre.geojson#{pid}:zona_entera"
        )

    for pid, barrio in ADMINISTRATIVOS.items():
        if barrio not in barrios.index:
            raise RuntimeError(f"{pid}: no se encontró el barrio {barrio}")
        soportes.at[pid, "geometry"] = barrios.loc[barrio].geometry
        soportes.at[pid, "soporte_es_real"] = False
        soportes.at[pid, "estado_soporte"] = "POLIGONO_ADMINISTRATIVO_DE_BARRIO"
        soportes.at[pid, "fuente_geometria"] = f"insumos/caba_barrios.geojson#{barrio}"

    for pid, nombre in NOMBRES_CANONICOS.items():
        soportes.at[pid, "polo_nombre"] = nombre

    soportes["superficie_soporte_m2"] = soportes.geometry.area
    if len(soportes) != 41 or soportes.index.duplicated().any():
        raise RuntimeError("los soportes no tienen 41 identificadores únicos")
    if set(soportes.index[~soportes["soporte_es_real"].astype(bool)]) != set(ADMINISTRATIVOS):
        raise RuntimeError("quedaron soportes administrativos fuera de los cuatro declarados")
    return soportes.reset_index()


def tamano_componente_mayor(xy: np.ndarray, distancia: float) -> int:
    if len(xy) == 0:
        return 0
    pares = cKDTree(xy).query_pairs(distancia, output_type="ndarray")
    vecinos: list[list[int]] = [[] for _ in range(len(xy))]
    for a, b in pares:
        vecinos[int(a)].append(int(b))
        vecinos[int(b)].append(int(a))
    vistos = np.zeros(len(xy), dtype=bool)
    mayor = 0
    for origen in range(len(xy)):
        if vistos[origen]:
            continue
        vistos[origen] = True
        cola = deque([origen])
        n = 0
        while cola:
            actual = cola.popleft()
            n += 1
            for vecino in vecinos[actual]:
                if not vistos[vecino]:
                    vistos[vecino] = True
                    cola.append(vecino)
        mayor = max(mayor, n)
    return mayor


def curva_para(locales: gpd.GeoDataFrame, poligono) -> tuple[int, list[float]]:
    adentro = locales[locales.geometry.covered_by(poligono)]
    xy = np.column_stack((adentro.geometry.x, adentro.geometry.y))
    n = len(adentro)
    curva = [round(100 * tamano_componente_mayor(xy, d) / n, 1) if n else 0.0 for d in DISTANCIAS]
    return n, curva


def validar_modelo_villa_pueyrredon(locales: gpd.GeoDataFrame) -> None:
    zonas = gpd.read_file(ZONAS_R7).to_crs(CRS_METRICO)
    poligono = zonas.loc[zonas["zona_id"].eq("R22"), "geometry"].iloc[0]
    n, curva = curva_para(locales, poligono)
    esperado = [2.5, 5.6, 11.6, 15.7, 31.3]
    if n != 198 or curva != esperado:
        raise RuntimeError(f"el control de Villa Pueyrredón divergió: n={n}, curva={curva}")


def densidad_y_continuidad(soportes: gpd.GeoDataFrame, locales: gpd.GeoDataFrame) -> None:
    filas = []
    for _, s in soportes.sort_values("polo_id").iterrows():
        n, curva = curva_para(locales, s.geometry)
        ha = float(s.geometry.area / 10_000)
        fila = {
            "polo_id": s.polo_id,
            "polo": s.polo_nombre,
            "tipo_de_borde": (
                "poligono_de_barrio" if s.polo_id in ADMINISTRATIVOS else "borde_propio"
            ),
            "barrio_usado": ADMINISTRATIVOS.get(s.polo_id, ""),
            "fuente_geometria": s.fuente_geometria,
            "n_locales": n,
            "superficie_ha": round(ha, 2),
            "locales_por_ha": round(n / ha, 2),
            "definicion_continuidad": "porcentaje de locales en la componente conexa mayor",
        }
        for d, valor in zip(DISTANCIAS, curva):
            fila[f"continuidad_pct_{d}m"] = valor
        filas.append(fila)
    escribir_csv(pd.DataFrame(filas), "densidad_y_continuidad_41.csv")


PARTICULAS = {"de", "del", "la", "las", "los", "y", "e", "en", "el", "al"}


def titulo_sobrio(texto: str) -> str:
    palabras = texto.casefold().split()
    salida = []
    for i, palabra in enumerate(palabras):
        salida.append(palabra if i and palabra in PARTICULAS else palabra[:1].upper() + palabra[1:])
    return " ".join(salida)


DIRECCIONES_CANONICAS = {
    "CORRIENTES AV. 6735": "Av. Corrientes 6735",
    "YRIGOYEN, HIPOLITO 1201": "Hipólito Yrigoyen 1201",
    "BOEDO 136": "Boedo 136",
    "LUJAN 2101": "Luján 2101",
    "CALLAO AV. 248": "Av. Callao 248",
    "MOREAU DE JUSTO, ALICIA AV. 1840": "Av. Alicia Moreau de Justo 1840",
    "OBLIGADO RAFAEL, AV.COSTANERA 7030": "Av. Costanera Rafael Obligado 7030",
    "RODRIGUEZ, MARTIN 517": "Martín Rodríguez 517",
    "ESTADOS UNIDOS 465": "Estados Unidos 465",
    "LAVALLE 941": "Lavalle 941",
    "MOREAU DE JUSTO, ALICIA AV. 1140": "Av. Alicia Moreau de Justo 1140",
    "SAN JUAN AV. 1999": "Av. San Juan 1999",
    "BERUTI 2602": "Beruti 2602",
    "MOREAU DE JUSTO, ALICIA AV. 420": "Av. Alicia Moreau de Justo 420",
    "PARAGUAY 645": "Paraguay 645",
    "LIBERTAD 431": "Libertad 431",
}


CONFLICTOS = {
    "DIR-002": (
        "resuelto_con_fuente_publica_archivada",
        "Se adopta Av. Álvarez Jonte 5299 esquina Av. Lope de Vega; la ficha pública confirma la esquina.",
        "Av. Álvarez Jonte 5299 esquina Av. Lope de Vega",
    ),
    "DIR-009": (
        "declarado_fuentes_publicas_discrepan",
        "Se conserva Av. Álvarez Thomas 1321; otra ficha pública consigna 1311. Requiere decisión canónica.",
        None,
    ),
    "DIR-010": (
        "resuelto_dos_numeraciones_misma_esquina",
        "Se conserva Suárez 396 y se declara Av. Almirante Brown 1220 como numeración alternativa de la misma esquina.",
        None,
    ),
    "DIR-015": (
        "declarado_referencia_de_esquina_imprecisa",
        "Se conserva Av. Rivadavia 4548; la referencia periodística a Av. La Plata no se usa como altura.",
        None,
    ),
    "DIR-024": (
        "declarado_fuentes_publicas_discrepan",
        "Se conserva Av. San Juan 2809; existen menciones a 2816 y la sede fundacional de 2727 ya no opera.",
        None,
    ),
}


def normalizar_hitos() -> None:
    contenido = json.loads(HITOS.read_text(encoding="utf-8"))
    for feature in contenido["features"]:
        p = feature["properties"]
        nombre_original = str(
            p["nombre_original"] if "nombre_original" in p else (p.get("nombre") or "")
        )
        direccion_original = str(
            p["direccion_original"] if "direccion_original" in p else (p.get("direccion") or "")
        )
        conflicto_original = str(
            p["conflicto_direccion_original"]
            if "conflicto_direccion_original" in p
            else (p.get("conflicto_direccion") or "")
        )
        p["nombre_original"] = nombre_original
        p["direccion_original"] = direccion_original
        p["conflicto_direccion_original"] = conflicto_original
        if nombre_original and any(c.isalpha() for c in nombre_original) and not any(
            c.islower() for c in nombre_original
        ):
            p["nombre"] = titulo_sobrio(nombre_original)
        if direccion_original in DIRECCIONES_CANONICAS:
            p["direccion"] = DIRECCIONES_CANONICAS[direccion_original]
        estado, resolucion, direccion = CONFLICTOS.get(
            p["hito_id"], ("sin_conflicto_declarado", "", None)
        )
        p["conflicto_direccion_estado"] = estado
        p["conflicto_direccion_resolucion"] = resolucion
        if direccion:
            p["direccion"] = direccion
        p["conflicto_direccion"] = "" if estado.startswith("resuelto") else conflicto_original
    encabezado = [
        "{",
        f'"type": {json.dumps(contenido["type"], ensure_ascii=False)},',
        f'"name": {json.dumps(contenido.get("name", "hitos_capa_2026"), ensure_ascii=False)},',
        f'"crs": {json.dumps(contenido.get("crs"), ensure_ascii=False)},',
        '"features": [',
    ]
    features = [
        json.dumps(feature, ensure_ascii=False, separators=(", ", ": "))
        + ("," if i < len(contenido["features"]) - 1 else "")
        for i, feature in enumerate(contenido["features"])
    ]
    HITOS.write_text("\n".join(encabezado + features + ["]", "}", ""]), encoding="utf-8")


def hitos_fuera() -> None:
    capa = gpd.read_file(HITOS).to_crs(CRS_METRICO)
    soportes = gpd.read_file(SOPORTES_BASE).to_crs(CRS_METRICO)
    barrios = gpd.read_file(BARRIOS).to_crs(CRS_METRICO)
    filas = []
    tolerados = []
    for _, hito in capa.sort_values("hito_id").iterrows():
        distancias = soportes.geometry.distance(hito.geometry)
        distancia_min = float(distancias.min())
        if 1e-7 < distancia_min <= TOLERANCIA_BORDE_M:
            i = distancias.idxmin()
            tolerados.append(
                {
                    "hito_id": hito.hito_id,
                    "nombre": hito.nombre,
                    "polo_mas_cercano_id": soportes.loc[i, "polo_id"],
                    "distancia_m": round(distancia_min, 1),
                    "decision": "tratar como contacto de borde; no integrar los 60 exteriores",
                }
            )
        if distancia_min <= TOLERANCIA_BORDE_M:
            continue
        i = distancias.idxmin()
        cercano = soportes.loc[i]
        bmask = barrios.geometry.covers(hito.geometry)
        barrio = str(barrios.loc[bmask, "BARRIO"].iloc[0]) if bmask.any() else "NO_ASIGNADO"
        lectura = (
            "posible_borde_incompleto"
            if distancia_min <= CORTE_REVISION_BORDE_M
            else "esperable_zona_sin_polo"
        )
        filas.append(
            {
                "hito_id": hito.hito_id,
                "nombre": hito.nombre,
                "tipo": hito.tipo,
                "direccion": hito.direccion,
                "barrio": barrio.title(),
                "polo_mas_cercano_id": cercano.polo_id,
                "polo_mas_cercano": cercano.polo_nombre,
                "distancia_m": round(distancia_min, 1),
                "lectura": lectura,
                "criterio_lectura": (
                    f"distancia al borde menor o igual a {CORTE_REVISION_BORDE_M:.0f} m"
                    if distancia_min <= CORTE_REVISION_BORDE_M
                    else f"distancia al borde mayor a {CORTE_REVISION_BORDE_M:.0f} m"
                ),
            }
        )
    fuera = pd.DataFrame(filas)
    escribir_csv(fuera, "hitos_fuera_de_todo_polo.csv")
    escribir_csv(pd.DataFrame(tolerados), "hitos_contacto_borde_tolerancia.csv")
    sensibilidad = []
    for corte in (100, 250, 500):
        n_revisar = int(fuera["distancia_m"].le(corte).sum())
        sensibilidad.append(
            {
                "corte_m": corte,
                "posible_borde_incompleto": n_revisar,
                "esperable_zona_sin_polo": int(len(fuera) - n_revisar),
                "universo": int(len(fuera)),
            }
        )
    escribir_csv(pd.DataFrame(sensibilidad), "hitos_fuera_sensibilidad.csv")


def exportar_conflictos() -> None:
    capa = gpd.read_file(HITOS)
    columnas = [
        "hito_id",
        "nombre",
        "direccion_original",
        "direccion",
        "conflicto_direccion_estado",
        "conflicto_direccion_resolucion",
        "fuente_primaria",
    ]
    df = capa[capa["conflicto_direccion_original"].fillna("").astype(str).str.strip().ne("")][columnas]
    contrastes = {
        "DIR-002": "https://godiamo.com.ar/restaurantes/el-fortin/",
        "DIR-009": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/la-mezzetta | https://visitbue.com/guias/GUIA_GASTRONOMICA_BUE_portugues.pdf",
        "DIR-010": "https://turismo.buenosaires.gob.ar/es/gastronomico/banchero",
        "DIR-015": "https://cuisine.com.ar/wp-content/uploads/2025/10/Guia-CV-4_baja.pdf",
        "DIR-024": "https://buenosaires.gob.ar/sites/default/files/media/document/2014/07/09/f2bcdf150e993967c85852f1a5ed84a435d851ea.pdf | https://www.boletinoficial.gob.ar/pdf/linkQR/VXNEVEVBZ24xQTkreFpJZ1U0d1UwZz09",
    }
    df["fuente_contraste"] = df["hito_id"].map(contrastes)
    df["fecha_revision"] = "2026-08-10"
    marte = pd.DataFrame(
        [
            {
                "hito_id": "NO_CARGADO_MARTE",
                "nombre": "Marte",
                "direccion_original": "Crisólogo Larralde 277 o 2772",
                "direccion": "Crisólogo Larralde 2772",
                "conflicto_direccion_estado": "resuelto_fuera_de_la_capa",
                "conflicto_direccion_resolucion": (
                    "No integra la capa de 215 reconocimientos. Se adopta 2772 por una pieza "
                    "periodística individual fechada en 2026 que describe el establecimiento."
                ),
                "fuente_primaria": "",
                "fuente_contraste": "https://www.lanacion.com.ar/sabado/el-polo-gourmet-que-crece-en-la-frontera-norte-de-la-ciudad-nid29052026/",
                "fecha_revision": "2026-08-10",
            }
        ]
    )
    escribir_csv(pd.concat([df, marte], ignore_index=True), "conflictos_direccion.csv")


def main() -> None:
    hashes_antes = {str(p): sha256(p) for p in (LOCALES, SOPORTES_BASE, CIERRE, BARRIOS)}
    locales = cargar_locales()
    validar_modelo_villa_pueyrredon(locales)
    soportes = construir_soportes()
    densidad_y_continuidad(soportes, locales)
    soportes.to_crs("EPSG:4326").to_file(OUT / "soportes_41_usados.geojson", driver="GeoJSON")
    normalizar_hitos()
    hitos_fuera()
    exportar_conflictos()
    hashes_despues = {str(p): sha256(p) for p in (LOCALES, SOPORTES_BASE, CIERRE, BARRIOS)}
    if hashes_antes != hashes_despues:
        raise RuntimeError("un insumo de sólo lectura cambió durante la ejecución")
    print("Salidas espaciales y capa normalizada generadas")


if __name__ == "__main__":
    main()
