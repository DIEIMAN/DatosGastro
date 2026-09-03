# -*- coding: utf-8 -*-
"""Piloto Google Places + microzonas — Etapa 5: tabla de revisión editorial.

EXPERIMENTAL. Derivado de solo lectura: NO modifica los outputs base del piloto.
Lee POLIGONOS_MICROZONAS_PILOTO.geojson + MICROCLUSTERS_PILOTO.geojson y produce una
tabla por microzona para decisión editorial (DGDGAS), con clasificación por reglas:

- APROBAR: núcleo discreto (sin subdivisión), mixto entre fuentes, con respaldo KDE.
- APROBAR CON OBSERVACIONES: núcleo discreto con alguna debilidad (KDE bajo, chico,
  fuente desbalanceada).
- REVISAR CORTE: pieza generada por subdivisión KMeans (límites geométricos, no reales).
- REVISAR UNIVERSO: núcleo sostenido casi solo por una fuente (>=70 % Places o >=95 %
  F01+F02 en zona donde Places aportó mucho).
- DESCARTAR / FUSIONAR: núcleo muy chico pegado (<80 m) a otro mayor.

La columna `referencia_orientativa` usa hitos urbanos conocidos con coordenadas
APROXIMADAS: es orientación editorial, siempre verificar sobre el mapa.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/historico/experimentos/google_places_microzonas_piloto/revision_editorial_microzonas.py
"""
from __future__ import annotations

import math
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
SALIDA = ROOT / "outputs" / "polos_gastro" / "historico" / "experimentos" / "google_places_microzonas_piloto"
POLIGONOS = SALIDA / "POLIGONOS_MICROZONAS_PILOTO.geojson"
PUNTOS = SALIDA / "MICROCLUSTERS_PILOTO.geojson"
OUT_DIR = SALIDA / "revision"
OUT_CSV = OUT_DIR / "tabla_revision_editorial_microzonas.csv"

CRS_METRICO = "EPSG:5347"
FUSION_DIST_M = 80.0

# Hitos urbanos de referencia (coordenadas APROXIMADAS, solo orientación editorial).
LANDMARKS = {
    "palermo_soho_hollywood": [
        ("Plaza Serrano (aprox.)", -34.5886, -58.4303),
        ("eje Honduras/Armenia (aprox.)", -34.5905, -58.4265),
        ("eje Fitz Roy - Hollywood (aprox.)", -34.5820, -58.4365),
        ("Dorrego/Cordoba - Hollywood este (aprox.)", -34.5855, -58.4295),
    ],
    "corrientes_microcentro": [
        ("Abasto (aprox.)", -34.6037, -58.4106),
        ("Corrientes y Callao (aprox.)", -34.6044, -58.3917),
        ("Obelisco / Corrientes y 9 de Julio (aprox.)", -34.6037, -58.3816),
        ("peatonal Lavalle/Florida (aprox.)", -34.6021, -58.3746),
        ("Reconquista / bajo (aprox.)", -34.5990, -58.3710),
    ],
    "belgrano": [
        ("Barrio Chino - Arribenos/Juramento (aprox.)", -34.5600, -58.4475),
        ("Cabildo y Juramento (aprox.)", -34.5622, -58.4560),
        ("corredor Libertador norte (aprox.)", -34.5560, -58.4420),
        ("Cabildo sur / limite Colegiales (aprox.)", -34.5700, -58.4515),
    ],
    "san_telmo": [
        ("Plaza Dorrego (aprox.)", -34.6205, -58.3717),
        ("Mercado de San Telmo (aprox.)", -34.6184, -58.3719),
        ("Parque Lezama norte (aprox.)", -34.6250, -58.3705),
    ],
}


def dist_m(lat1, lon1, lat2, lon2) -> float:
    """Distancia aproximada en metros (suficiente para referencias orientativas)."""
    dy = (lat1 - lat2) * 111_320.0
    dx = (lon1 - lon2) * 111_320.0 * math.cos(math.radians(lat1))
    return math.hypot(dx, dy)


def referencia(zona: str, lat: float, lon: float) -> str:
    mejor, dmin = "", 1e9
    for nombre, la, lo in LANDMARKS.get(zona, []):
        d = dist_m(lat, lon, la, lo)
        if d < dmin:
            mejor, dmin = nombre, d
    if dmin <= 350:
        return mejor
    if dmin <= 700:
        return f"cerca de {mejor}"
    return ""


def confianza(row) -> str:
    if row["ronda"] > 0 or row["frac_kde"] < 0.25 or row["cantidad_entidades"] < 8:
        return "baja"
    if (row["frac_kde"] >= 0.5 and row["cantidad_entidades"] >= 15
            and 15 <= row["porcentaje_places"] <= 75):
        return "alta"
    return "media"


def clasificar(row) -> tuple[str, str, str]:
    """(clasificacion, problema_detectado, accion_recomendada)."""
    if row["vecino_mas_cercano_m"] is not None and row["vecino_mas_cercano_m"] < FUSION_DIST_M \
            and row["cantidad_entidades"] < 10:
        return ("DESCARTAR / FUSIONAR",
                f"nucleo chico ({row['cantidad_entidades']} ent.) pegado a otro poligono "
                f"(a {row['vecino_mas_cercano_m']:.0f} m)",
                "fusionar con la microzona vecina o descartar")
    if row["ronda"] > 0:
        return ("REVISAR CORTE",
                "pieza de subdivision KMeans: el limite con las piezas vecinas es "
                "geometrico, no una frontera real",
                "redibujar el corte a mano (calles/hitos) o fusionar piezas vecinas")
    if row["porcentaje_places"] >= 70:
        return ("REVISAR UNIVERSO",
                f"{row['porcentaje_places']:.0f} % de los puntos son Google Places: "
                "nucleo casi invisible para F01+F02",
                "verificar contra registro/campo antes de aprobar (posible oferta nueva "
                "o sesgo de prominencia de Places)")
    if confianza(row) == "alta":
        return ("APROBAR",
                "",
                "aprobar como microzona candidata")
    obs = []
    if row["frac_kde"] < 0.5:
        obs.append(f"respaldo KDE parcial ({row['frac_kde']:.0%})")
    if row["cantidad_entidades"] < 15:
        obs.append(f"pocas entidades ({row['cantidad_entidades']})")
    if row["porcentaje_places"] < 15:
        obs.append("casi sin señal Places")
    if row["porcentaje_places"] > 75:
        obs.append("dominada por Places")
    return ("APROBAR CON OBSERVACIONES",
            "; ".join(obs) or "debilidad menor",
            "aprobar dejando la observacion anotada")


def lectura(row, clasif: str) -> str:
    ref = row["referencia_orientativa"]
    mezcla = (f"{row['porcentaje_f01_f02']:.0f} % F01+F02 / "
              f"{row['porcentaje_places']:.0f} % Places")
    if clasif == "REVISAR CORTE":
        base = "Parte de un corredor denso continuo; la pieza en si es real, el corte no"
    elif clasif == "REVISAR UNIVERSO":
        base = "Nucleo detectado principalmente por Places"
    elif clasif == "DESCARTAR / FUSIONAR":
        base = "Fragmento menor adosado a un nucleo mayor"
    elif clasif == "APROBAR":
        base = "Nucleo discreto y mixto, consistente entre fuentes"
    else:
        base = "Nucleo discreto con debilidad menor"
    partes = [base, mezcla]
    if ref:
        partes.append(ref)
    return " | ".join(partes)


def main() -> int:
    poli = gpd.read_file(POLIGONOS)
    pts = gpd.read_file(PUNTOS)

    fuentes = (pts[pts["cluster_final"] != "ruido"]
               .groupby(["cluster_final", "fuente"]).size().unstack(fill_value=0))
    for col in ("F01+F02", "google_places"):
        if col not in fuentes.columns:
            fuentes[col] = 0

    poli_m = poli.to_crs(CRS_METRICO)
    vecino = []
    for i, geom in enumerate(poli_m.geometry):
        misma_mz = poli_m[poli_m["macrozona_id"] == poli_m.iloc[i]["macrozona_id"]]
        dists = [geom.distance(g) for j, g in zip(misma_mz.index, misma_mz.geometry)
                 if j != poli_m.index[i]]
        vecino.append(round(min(dists), 1) if dists else None)

    cent = poli.geometry.centroid  # WGS84: suficiente para referencia orientativa

    filas = []
    for i, (_, p) in enumerate(poli.iterrows()):
        cid = p["cluster_id"]
        f = fuentes.loc[cid] if cid in fuentes.index else {"F01+F02": 0, "google_places": 0}
        n = int(f["F01+F02"] + f["google_places"])
        fila = {
            "macrozona": p["macrozona_id"],
            "zona_piloto": p["zona_piloto"],
            "microzona_id": cid,
            "cantidad_entidades": n,
            "porcentaje_places": round(100 * f["google_places"] / max(n, 1), 1),
            "porcentaje_f01_f02": round(100 * f["F01+F02"] / max(n, 1), 1),
            "superficie_ha": p["area_ha"],
            "densidad_entidades_ha": p["densidad_ha"],
            "diametro_m": p["diametro_m"],
            "ronda": int(p["ronda"]),
            "frac_kde": p["frac_en_nucleo_kde"] if p["frac_en_nucleo_kde"] is not None else 0.0,
            "vecino_mas_cercano_m": vecino[i],
            "referencia_orientativa": referencia(p["zona_piloto"], cent.iloc[i].y, cent.iloc[i].x),
        }
        fila["confianza_algoritmica"] = confianza(fila)
        clasif, problema, accion = clasificar(fila)
        fila["clasificacion"] = clasif
        fila["problema_detectado"] = problema
        fila["accion_recomendada"] = accion
        fila["lectura_editorial_sugerida"] = lectura(fila, clasif)
        filas.append(fila)

    df = pd.DataFrame(filas).sort_values(["zona_piloto", "macrozona", "microzona_id"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")

    print(f"[revision] {len(df)} microzonas -> {OUT_CSV}\n")
    print("Clasificacion por macrozona:")
    print(df.groupby(["macrozona", "clasificacion"]).size().unstack(fill_value=0).to_string())
    print("\nResumen global:")
    print(df["clasificacion"].value_counts().to_string())
    print("\nMezcla de fuentes (microzonas con 20-80 % Places = 'mixtas'):")
    mixtas = ((df["porcentaje_places"] >= 20) & (df["porcentaje_places"] <= 80)).sum()
    print(f"  mixtas: {mixtas}/{len(df)} ({100 * mixtas / len(df):.0f} %)")
    print("\nConfianza algoritmica:")
    print(df["confianza_algoritmica"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
