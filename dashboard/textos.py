from __future__ import annotations


CRITICAL_WARNINGS = [
    "No sumar F01 + F02: F01 son registros de oferta; F02 son habilitaciones aprobadas.",
    "F02 no representa locales activos ni locales unicos; tampoco informa bajas.",
    "F02 2025 tiene esquema distinto y contiene disposiciones de varios anios; se muestra aparte y no como flujo anual comparable.",
    "F04 y F05 son relevamientos manuales trazables y parciales; no representan universos completos ni impacto.",
]

SOURCE_CAPTIONS = {
    "f01": "Fuente: Buenos Aires Data / ENTUR. F01 no confirma vigencia actual por registro.",
    "f02": "Fuente: Buenos Aires Data / AGC. Habilitaciones aprobadas; clasificacion gastronomica inferida por rubro.",
    "f03": "Fuente: Buenos Aires Data / Min. Espacio Publico. F03 separa espacios reales de puestos/personas.",
    "f04": "Fuente: relevamiento manual trazable F04. Solo aptos para metricas fuertes cuando apto_dashboard=si.",
    "f05": "Fuente: relevamiento manual trazable F05. Catalogo de instrumentos, no serie de impacto.",
    "mapa": "Fuente: Buenos Aires Data (ENTUR / Min. Espacio Publico). Coordenadas provistas por la fuente; no se geocodifico. No se mapean F02, puestos, eventos ni programas.",
    "mapa_oportunidades": "Fuente: analytics_mapa_oportunidades.csv. Universos separados a nivel comuna; no es un score compuesto.",
    "resumen": "Fuente: analytics_resumen_ejecutivo.csv, fecha de consulta declarada en cada salida.",
}

TAB_INTROS = {
    "panorama": "Lectura ejecutiva de oferta registrada, habilitaciones, espacios publicos/ferias y eventos aptos.",
    "territorio": "Distribucion territorial con capas mapeables oficiales y rankings por barrio/comuna.",
    "dinamismo": "Evolucion F02 solo para anios comparables; periodos no comparables se separan.",
    "ecosistema": "Espacios F03, eventos F04 y programas F05 como ecosistema publico trazable.",
    "metodologia": "Criterios de lectura, trazabilidad, aptitud de datos y limites del tablero.",
}

WHAT_IT_DOES_NOT_ANSWER = [
    "Cantidad de locales gastronomicos activos.",
    "Bajas, cierres o supervivencia de establecimientos.",
    "Impacto economico, ventas, empleo o facturacion.",
    "Cobertura completa de eventos privados o programas no publicados.",
]


def source_caption(key: str, date_text: str = "") -> str:
    caption = SOURCE_CAPTIONS.get(key, "Fuente: procesamiento propio sobre archivos trazables.")
    if date_text and date_text != "No disponible":
        return f"{caption} Fecha de consulta: {date_text}."
    return caption

