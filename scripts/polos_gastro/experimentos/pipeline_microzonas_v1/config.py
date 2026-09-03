# -*- coding: utf-8 -*-
"""Configuracion compartida del prototipo V1 del pipeline de microzonas.

EXPERIMENTAL. No toca Fase 25, mapas oficiales ni el pipeline F01-F05.
Lee `data/processed/` en modo solo lectura; escribe unicamente en
`outputs/polos_gastro/historico/experimentos/pipeline_microzonas_v1/`.

Todos los parametros del prototipo viven aca, con su justificacion, y se
exportan a `parametros_pipeline_v1.json` en cada corrida (regla: sin
parametros magicos; todo queda registrado).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]

PROCESSED = REPO / "data" / "processed"
SALIDA = REPO / "outputs" / "polos_gastro" / "historico" / "experimentos" / "pipeline_microzonas_v1"
DOCS = REPO / "docs" / "polos_gastro" / "historico" / "experimentos" / "pipeline_microzonas_v1"

COMUNAS_GEOJSON = REPO / "PolosGastro" / "cartografia" / "comunas_caba.geojson"
BARRIOS_GEOJSON = REPO / "PolosGastro" / "cartografia" / "barrios_caba.geojson"
SEMILLA_CSV = (
    REPO / "outputs" / "polos_gastro" / "fase13_mapas" / "tablas"
    / "locales_para_mapa_revision.csv"
)

CRS_GEO = "EPSG:4326"
CRS_METRICO = "EPSG:5347"  # POSGAR 2007 faja 5: distancias en metros para CABA

NOTA_EXPERIMENTAL = (
    "Salida experimental del prototipo V1 de microzonas. No constituye limite oficial, "
    "no mide 'locales activos' (mide oferta gastronomica registrada / habilitaciones "
    "historicas) y requiere revision humana antes de cualquier uso institucional."
)

# ---------------------------------------------------------------------------
# Registro de parametros: valor + justificacion. Nada de numeros sueltos.
# ---------------------------------------------------------------------------

PARAMETROS = {
    "universo": {
        "fuentes": {
            "valor": ["F01", "F02"],
            "justificacion": "Decision de Diego 2026-07-08: universo v1 solo con fuentes "
            "publicas ya integradas; Google Places nunca como fuente principal.",
        },
        "categorias_f02_excluidas": {
            "valor": ["Catering", "Mercado", "Feria"],
            "justificacion": "Catering no es local gastronomico a la calle e inflaria "
            "nucleos (doc 03 s2.2); Mercado/Feria pertenecen al universo F03 y al "
            "subproyecto Mercados (3 filas en total).",
        },
        "colapso_f02": {
            "valor": "una entidad por id_ubicacion",
            "justificacion": "F02 tiene 5,6 filas por ubicacion (y el recurso 2025 llega "
            "a 28,8): clusterizar filas mediria redundancia administrativa. Sin nombre "
            "comercial en F02 no es posible separar locales distintos en una misma "
            "direccion (galerias): limitacion documentada.",
        },
        "dedup_f01_nombre_igual_dist_m": {
            "valor": 40,
            "justificacion": "Dos filas F01 con el mismo nombre normalizado a menos de "
            "40 m (un frente de manzana) se consideran el mismo local geocodificado por "
            "cadenas de direccion distintas. A mas de 40 m pueden ser sucursales.",
        },
        "dedup_cruzada_dist_m": {
            "valor": 15,
            "justificacion": "USIG geocodifica a parcela; 15 m cubre la misma parcela y "
            "la de al lado. Sin nombres en F02, fusionar mas lejos con solo la categoria "
            "arriesga fusionar locales vecinos distintos.",
        },
        "dedup_cruzada_flag_dist_m": {
            "valor": 30,
            "justificacion": "Entre 15 y 30 m con categoria compatible no se fusiona pero "
            "se marca `posible_duplicado_cercano` para cola de revision humana (banda "
            "media del doc 03 s5).",
        },
        "bbox_caba": {
            "valor": {"lat": [-34.75, -34.50], "lon": [-58.60, -58.30]},
            "justificacion": "Descarta coordenadas claramente fuera de CABA antes del "
            "point-in-polygon (mismo criterio que el perfilado de diseno).",
        },
    },
    "macrozonas": {
        "fuente_contenedores": {
            "valor": "hull convexo de puntos semilla por polo (Fase 13) + buffer",
            "justificacion": "No existe capa poligonal editorial de los 13 polos (las "
            "subzonas V4 cubren solo 5 mapas). El doc 01 s4.4 preve digitalizar un "
            "contorno aproximado una unica vez como capa de trabajo experimental; el "
            "hull de la semilla es esa digitalizacion, automatica y reproducible. "
            "NO es un limite oficial.",
        },
        "abasto_en_corrientes": {
            "valor": True,
            "justificacion": "Decision editorial vigente (no se re-litiga): Abasto es "
            "subzona del polo Corrientes.",
        },
        "buffer_contenedor_m": {
            "valor": 500,
            "justificacion": "La semilla es rala (5-19 puntos por polo) y su hull "
            "subestima la macrozona editorial; 500 m (~4-5 cuadras) da margen para que "
            "los nucleos emerjan de los datos y no del recorte. Sensibilidad con 300 y "
            "700 m registrada en el perfil de asignacion.",
        },
        "buffers_sensibilidad_m": {"valor": [300, 700], "justificacion": "Control de "
            "cuanto depende la asignacion del buffer elegido."},
        "radio_max_semilla_m": {
            "valor": 2300,
            "justificacion": "Una macrozona editorial es de escala barrio/corredor: el "
            "caso mas extendido legitimo es el eje Corrientes completo (~2,2 km desde el "
            "centro del polo, incluida la subzona Abasto). Puntos semilla mas lejos del "
            "centro mediano de su polo son sedes mal geocodificadas (hallazgo Tanda 2: "
            "Belgrano con sedes a 14 km, Recoleta a 6 km) y no deben deformar el "
            "contenedor. La regla relativa de Tanda 2 (3 x mediana) no alcanzaba: con "
            "varias sedes malas la mediana tambien se corre.",
        },
        "min_semilla_contenedor": {
            "valor": 3,
            "justificacion": "Con menos de 3 puntos semilla depurados el hull degenera "
            "(punto o segmento); el contenedor se construye igual (buffer del hull "
            "degenerado) pero queda marcado `contenedor_degradado` para lectura con "
            "cautela.",
        },
        "asignacion_multiple": {
            "valor": "menor distancia al hull base; empate -> contenedor de menor area",
            "justificacion": "Doc 01 s4.4: un punto pertenece a una sola macrozona. Si "
            "un punto cae dentro de dos hulls base (distancia 0 a ambos), gana la "
            "macrozona mas especifica (hull menor): un contenedor grande no debe "
            "tragarse a uno chico vecino.",
        },
    },
    "clustering": {
        "hdbscan_min_cluster_size": {
            "valor": "max(8, 3% de los puntos de la macrozona)",
            "justificacion": "Doc 02 s2.2: 8 locales como minimo interpretable de un "
            "nucleo; el 3% relativiza en macrozonas muy pobladas.",
        },
        "hdbscan_min_samples": {"valor": 5, "justificacion": "Doc 02 s2.2 (propuesta "
            "inicial a calibrar en piloto)."},
        "hdbscan_cluster_selection_epsilon_m": {
            "valor": 50,
            "justificacion": "Evita fragmentar nucleos separados por una calle (~30 m de "
            "eje a eje + veredas).",
        },
        "hdbscan_cluster_selection_method": {
            "valor": "eom",
            "justificacion": "Se fija explicitamente porque cambia resultados (doc 02 "
            "s2.1); eom prioriza clusters estables.",
        },
        "minimo_puntos_macrozona": {
            "valor": 30,
            "justificacion": "Doc 02 s2.1: con <30 puntos HDBSCAN fragmenta o no "
            "encuentra estructura. Bajo ese umbral se corre DBSCAN(eps=150, ms=4) como "
            "alternativa declarada y la macrozona queda marcada evidencia_insuficiente.",
        },
        "dbscan_fallback": {
            "valor": {"eps_m": 150, "min_samples": 4},
            "justificacion": "Escala de 1-2 cuadras, exigencia minima de 4 locales: para "
            "macrozonas con poca evidencia solo se aceptan nucleos chicos y densos.",
        },
        "dbscan_continuidad": {
            "valor": {"eps_m": 650, "min_samples": 4},
            "justificacion": "Candidata 'inclusiva' de la Tanda 2: unica corrida DBSCAN "
            "comparable con lo ya hecho.",
        },
        "kde_bandwidth_m": {
            "valor": 100,
            "justificacion": "Una cuadra portena (~110 m); doc 02 s2.2 propone 80-120 m.",
        },
        "kde_grilla_m": {"valor": 20, "justificacion": "Doc 02 s2.2."},
        "kde_umbral_relativo": {
            "valor": 0.4,
            "justificacion": "Nucleo KDE = celdas >= 40% del maximo DE LA macrozona "
            "(umbral relativo: inmune al sesgo de registro entre comunas).",
        },
    },
    "poligonizacion": {
        "metodos": {
            "valor": [
                "convex_hull_buffer",
                "concave_hull_r03_buffer",
                "concave_hull_r05_buffer",
                "buffer_union_r70",
                "kde_contorno_40pct",
                "capsula_pca",
            ],
            "justificacion": "Etapa 4 del pedido: generar alternativas comparables sin "
            "decidir todavia cual gana. alphashape no esta en .venv; el concave_hull de "
            "shapely con dos ratios cubre el mismo espacio de formas (doc 02 s3).",
        },
        "buffer_frente_m": {
            "valor": 35,
            "justificacion": "Los puntos son puertas de local: el poligono debe cubrir "
            "el frente edificado, no pasar por el eje de la calzada (doc 02 s3).",
        },
        "buffer_union_r_m": {
            "valor": 70,
            "justificacion": "Radio de influencia de un local (doc 02 s3, 60-80 m); "
            "cierre morfologico buffer(+70)->union->buffer(-35).",
        },
        "capsula_semiancho_m": {
            "valor": 60,
            "justificacion": "Doc 02 s3: corredores como capsula sobre el eje principal "
            "(PCA hasta disponer de ejes viales GCBA), semiancho 50-70 m.",
        },
        "corredor_elongacion_min": {"valor": 3.0, "justificacion": "Doc 01 s4.6."},
        "corredor_largo_min_m": {"valor": 600, "justificacion": "Doc 01 s4.6."},
    },
    "qa_gates": {
        "superficie_max_ha": {"valor": 35, "justificacion": "Doc 01 s6 (gate duro)."},
        "superficie_flag_ha": {"valor": 20, "justificacion": "Doc 01 s6 (bandera)."},
        "min_locales": {"valor": 5, "justificacion": "Doc 01 s6 (gate duro)."},
        "densidad_min_ha": {"valor": 1.0, "justificacion": "Doc 01 s6 (gate duro)."},
        "diametro_max_no_corredor_m": {"valor": 1200, "justificacion": "Doc 01 s6."},
    },
}


def parametros_planos() -> dict:
    """Version {grupo.nombre: valor} para registrar en salidas."""
    planos = {}
    for grupo, params in PARAMETROS.items():
        for nombre, det in params.items():
            planos[f"{grupo}.{nombre}"] = det["valor"]
    return planos


def exportar_parametros(destino: Path | None = None) -> Path:
    destino = destino or (SALIDA / "parametros_pipeline_v1.json")
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(PARAMETROS, fh, ensure_ascii=False, indent=2)
    return destino


def asegurar_salidas(*subdirs: str) -> None:
    for sub in subdirs:
        (SALIDA / sub).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ruta = exportar_parametros()
    print(f"Parametros exportados a {ruta}")
