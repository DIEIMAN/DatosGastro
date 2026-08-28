# -*- coding: utf-8 -*-
"""Etapa Cal-5 — Ensamblado de `macrozonas_editoriales_candidatas_v1.geojson`.

EXPERIMENTAL, NO OFICIAL. Combina las 10 macrozonas sin cambios de
`macrozonas_v1_experimental.geojson` con las 4 corregidas en la Etapa Cal-2/3
(Microcentro, Belgrano, Costanera Norte, Chacarita), actualizando atributos de
trazabilidad (version_capa, fecha_actualizacion, nivel_confianza, observaciones) sin
perder el historial de por que cambio cada una.

Sigue siendo "candidata": estado_revision se mantiene en "borrador" para las 4
corregidas (recien se pasa a "revisado" u "aprobado_editorial" cuando alguien de DGDGAS
lo decida, Etapa Cal-6). Las 10 sin cambios mantienen su version_capa original
("v1_experimental") para dejar explicito que no fueron tocadas en esta ronda.

Uso:
    .venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/ensamblar_macrozonas_candidatas_v1.py
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import geopandas as gpd

REPO = Path(__file__).resolve().parents[4]
SALIDA = REPO / "outputs/polos_gastro/experimentos/infraestructura_cartografica_v1"
CORRECCIONES_DIR = SALIDA / "correcciones_bloqueantes"

ACTUALIZACIONES = {
    "MZ_MICROCENTRO_Y_CENTRO": {
        "nivel_confianza": "media",
        "metodo_construccion": (
            "barrio oficial San Nicolas MENOS el corredor real de Avenida Corrientes "
            "(resuelve el solapamiento del 49.2% detectado en macrozonas_v1_experimental)"
        ),
        "fuente": "barrio_oficial:San Nicolas; corredor:MZ_AVENIDA_CORRIENTES (recorte)",
        "observaciones": (
            "Corregida en la Etapa Cal-2/3 para eliminar el solapamiento con Avenida "
            "Corrientes (era el bloqueante #1). 406 entidades que antes se contaban en "
            "ambas macrozonas ahora quedan solo en Corrientes. QA (Cal-4): 0 entidades "
            "duplicadas, 0 huerfanas. Antes/despues: 229.0->116.3 ha, 763->357 entidades. "
            "Ver CORRECCIONES_BLOQUEANTES_ANTES_DESPUES.md."
        ),
    },
    "MZ_BELGRANO": {
        "nivel_confianza": "media",
        "metodo_construccion": (
            "corredores reales sobre Av. Juramento, Av. del Libertador y Av. Cabildo "
            "(semiancho 250 m), interseccion con barrio oficial Belgrano — reemplaza la "
            "union de elipses editoriales heredadas de fase16"
        ),
        "fuente": "callejero_gcba: Juramento Av., Del Libertador Av., Cabildo Av.; barrio_oficial:Belgrano",
        "observaciones": (
            "Corregida en la Etapa Cal-2/3: sube de confianza baja a media porque ahora "
            "se apoya en calles reales documentadas (fase16 ya las citaba como "
            "referencia geografica de cada subzona), no en elipses dibujadas a mano. "
            "ADVERTENCIA (QA Cal-4): la correccion gana 84 entidades pero pierde 53 que "
            "quedan sin ninguna macrozona (el semiancho de 250 m no llega a cubrir zonas "
            "que las elipses viejas si cubrian). Revisar esas 53 entidades antes de "
            "aprobar. Sigue siendo UN solo poligono de polo, no subdividido en Barrio "
            "Chino/Bajo Belgrano/Belgrano R (pendiente de una sesion futura). "
            "Antes/despues: 202.0->232.5 ha, 273->304 entidades."
        ),
    },
    "MZ_COSTANERA_NORTE": {
        "nivel_confianza": "baja",
        "metodo_construccion": (
            "corredor real sobre Av. Costanera Rafael Obligado, semiancho reducido de "
            "350 a 250 m, bbox acotado al tramo con evidencia real (antes cubria casi el "
            "doble del tramo con entidades)"
        ),
        "fuente": "callejero_gcba: Av. Costanera Rafael Obligado",
        "observaciones": (
            "Corregida en la Etapa Cal-2/3: reduccion de superficie (225.1->150.8 ha, "
            "-33%) sin perder ninguna de las 5 entidades. Confianza se mantiene BAJA "
            "deliberadamente: la correccion la hace mas honesta, no le agrega evidencia "
            "que no existe (0.03 entidades/ha, la mas baja de las 12). Candidata a "
            "marcarse 'evidencia insuficiente' en vez de aprobarse como esta."
        ),
    },
    "MZ_CHACARITA": {
        "nivel_confianza": "media",
        "metodo_construccion": (
            "barrio oficial Chacarita interseccion con buffer 400 m alrededor de las "
            "116 entidades reales del universo V1 (F01+F02) ya contenidas — reemplaza "
            "el barrio completo sin recorte"
        ),
        "fuente": "barrio_oficial:Chacarita; universo_v1:entidades_contenidas",
        "observaciones": (
            "Corregida en la Etapa Cal-2/3: mejora modesta (311.7->262.0 ha, -16%), "
            "mismas 116 entidades preservadas (0 huerfanas). El diagnostico inicial "
            "(ficha tecnica Cal-1) sugeria que las entidades estaban concentradas en "
            "~2x2 km; al graficar el rango completo se confirmo que en realidad cubren "
            "casi todo el barrio, por eso la mejora fue modesta y no dramatica. Se "
            "documenta la correccion del diagnostico para no repetir el error de lectura."
        ),
    },
}


def main() -> None:
    base = gpd.read_file(SALIDA / "macrozonas_v1_experimental.geojson")
    correcciones = gpd.read_file(CORRECCIONES_DIR / "geometrias_corregidas.geojson")
    hoy = date.today().isoformat()

    base = base.set_index("id", drop=False)
    correcciones = correcciones.set_index("id")

    for id_, attrs in ACTUALIZACIONES.items():
        base.loc[id_, "geometry"] = correcciones.loc[id_, "geometry"]
        for campo, valor in attrs.items():
            base.loc[id_, campo] = valor
        base.loc[id_, "version_capa"] = "candidatas_v1"
        base.loc[id_, "fecha_actualizacion"] = hoy
        base.loc[id_, "autor"] = "Claude (asistido) - correccion de bloqueante, pendiente revision Diego"
        # estado_revision se mantiene 'borrador': recien pasa a revisado/aprobado en Cal-6

    base = base.reset_index(drop=True)
    ruta = SALIDA / "macrozonas_editoriales_candidatas_v1.geojson"
    base.to_file(ruta, driver="GeoJSON")

    resumen = base.copy()
    resumen["area_ha"] = (resumen.to_crs("EPSG:5347").geometry.area / 10_000.0).round(1)
    print(f"{len(base)} features -> {ruta}")
    print(resumen[["id", "nombre", "nivel_confianza", "version_capa", "area_ha"]].to_string(index=False))
    print(f"\nModificadas en esta ronda: {len(ACTUALIZACIONES)} de {len(base)}")
    print(f"Sin cambios (version_capa='v1_experimental'): {len(base) - len(ACTUALIZACIONES)}")


if __name__ == "__main__":
    main()
