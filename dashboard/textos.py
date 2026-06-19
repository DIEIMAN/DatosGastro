from __future__ import annotations


# ----------------------------------------------------------------------------
# Textos del dashboard: unica fuente de verdad de la narrativa.
# Principio editorial: concepto primero, codigo de fuente (F01-F05) al final y
# entre parentesis. Una sola regla de lectura global; el detalle metodologico
# completo vive en la pestana Metodologia.
# ----------------------------------------------------------------------------

TITULO = "DataGastro"
BAJADA = (
    "Una radiografia del ecosistema gastronomico de Buenos Aires construida sobre "
    "datos abiertos del GCBA y relevamientos trazables: que oferta existe, donde se "
    "habilita actividad nueva, que espacios publicos funcionan y que sostiene la Ciudad."
)

REGLA_DE_ORO = (
    "Como leer este tablero: cada seccion responde una pregunta distinta con una fuente "
    "distinta. Los numeros no se suman entre si — una habilitacion no es un local activo, "
    "y un local registrado no garantiza que siga abierto. El detalle completo esta en Metodologia."
)

TABS = [
    "Panorama",
    "Donde esta la gastronomia",
    "Cuanto se abre por anio",
    "Que pone la Ciudad",
    "Metodologia",
]

KPI_LABELS = {
    "f01": "Oferta registrada en guia oficial",
    "f02": "Habilitaciones aprobadas (2015-2025)",
    "f03": "Espacios de ferias, mercados y FIAB",
    "f04": "Eventos gastronomicos verificados",
}

KPI_HELP = {
    "f01": "Fuente 1: guia de oferta gastronomica de Buenos Aires Data / Ente de Turismo del GCBA. No confirma que cada local siga abierto.",
    "f02": "Fuente 2: habilitaciones aprobadas por la Agencia Gubernamental de Control (AGC), clasificadas como gastronomia de servicio. No equivalen a locales activos. La serie anual comparable es 2019-2024.",
    "f03": "Fuente 3: espacios reales de ferias, mercados y Ferias Itinerantes de Abastecimiento Barrial (FIAB). No cuenta puestos individuales.",
    "f04": "Fuente 4: eventos vinculados a la politica gastronomica, relevados manualmente con fuente por fila. Solo los verificados entran en metricas.",
}

HALLAZGO_DENSIDAD = (
    "**Hallazgo clave:** en volumen absoluto, Palermo lidera la oferta registrada. "
    "Pero por densidad (registros por km2), San Nicolas concentra entre 6 y 7 veces "
    "mas actividad gastronomica. El nucleo real por intensidad es el microcentro y "
    "el casco historico (San Nicolas, Monserrat, San Telmo), no Palermo. Esta "
    "diferencia importa para planificacion de uso del suelo y permisos de espacio publico."
)

GLOSARIO = {
    "AGC": "Agencia Gubernamental de Control: organismo del GCBA que aprueba habilitaciones comerciales.",
    "GCBA": "Gobierno de la Ciudad de Buenos Aires.",
    "USIG": "Sistema de Informacion Geografica del GCBA: servicio oficial para normalizar y ubicar direcciones en el mapa.",
    "FIAB": "Ferias Itinerantes de Abastecimiento Barrial: ferias de productos frescos que rotan por barrios.",
    "F01": "Fuente 1: oferta gastronomica registrada en la guia oficial del Ente de Turismo del GCBA.",
    "F02": "Fuente 2: habilitaciones gastronomicas aprobadas por la Agencia Gubernamental de Control.",
    "F03": "Fuente 3: espacios de ferias, mercados y FIAB de la Direccion General de Ferias del GCBA.",
    "F04": "Fuente 4: eventos gastronomicos relevados manualmente con fuente anotada por fila.",
    "F05": "Fuente 5: programas y politicas gastronomicas relevados manualmente con normativa de referencia.",
    "Geocodificacion": "Proceso de convertir una direccion de texto en coordenadas geograficas para mostrarla en el mapa.",
    "Habilitacion": "Autorizacion formal del GCBA para operar un rubro comercial en una direccion.",
    "Padron vivo": "Registro actualizado de locales activos con altas y bajas. DataGastro no tiene esta fuente todavia.",
}

INTROS = {
    "panorama": (
        "Resumen ejecutivo en una pantalla: el tamano de cada universo, el mapa con la "
        "oferta registrada y los espacios publicos, y las lecturas principales."
    ),
    "territorio": (
        "Donde esta la actividad. Los puntos principales salen de coordenadas oficiales. "
        "La capa opcional USIG de F02 muestra donde se aprueba actividad gastronomica "
        "formal, no donde hay locales activos, y se dibuja separada de la oferta registrada "
        "y de los espacios publicos."
    ),
    "dinamismo": (
        "Una habilitacion aprobada es la autorizacion formal para operar un rubro en un "
        "domicilio: marca donde el sector formal esta invirtiendo. Aca se ve cuantas "
        "habilitaciones gastronomicas se aprobaron por anio y de que tipo."
    ),
    "ecosistema": (
        "La pata publica del ecosistema: la red de mercados y ferias de abastecimiento, "
        "el calendario de eventos que la Ciudad impulsa o acompana, y los programas e "
        "instrumentos vigentes."
    ),
    "metodologia": (
        "Todas las reglas de lectura, advertencias, fuentes y limites del tablero. "
        "Si un numero de las otras pestanas genera dudas, la respuesta esta aca."
    ),
}

# Advertencias completas: se muestran SOLO en Metodologia. En el resto del
# tablero cada grafico lleva su caption de fuente con la advertencia minima.
ADVERTENCIAS_COMPLETAS = [
    "No sumar F01 + F02: F01 son registros de oferta publicados; F02 son habilitaciones aprobadas. Universos distintos.",
    "F02 no representa locales activos ni locales unicos, y no informa bajas ni cierres.",
    "La clasificacion gastronomica de F02 se infiere del texto del rubro con matching por palabra completa y exclusiones trazables; sigue siendo una inferencia.",
    "El recurso F02 2025 tiene esquema distinto y contiene disposiciones de varios anios: se muestra aparte y nunca como flujo anual.",
    "F02 no publica barrio; la comuna se conoce solo en parte de los registros. Las vistas territoriales de F02 declaran su cobertura.",
    "F03 cuenta espacios (mercados, ferias, paradas FIAB), no puestos. El padron de puestos se agrega por feria y los datos personales se descartan.",
    "Cada parada FIAB es un punto semanal: la misma feria itinerante aparece en varias ubicaciones.",
    "F04 y F05 son relevamientos manuales trazables y parciales; no representan universos completos ni miden impacto.",
    "Solo se mapean coordenadas provistas por fuentes oficiales o geocodificaciones F02 validadas. F02 USIG solo puede sumarse como capa opcional si el cache supera 95% de exactas y se excluyen discrepancias de comuna contra la fuente.",
]

NO_RESPONDE = [
    "Cuantos locales gastronomicos estan activos hoy (no existe padron vivo con bajas).",
    "Cuantos locales cerraron o cuanto sobreviven (no hay datos de bajas).",
    "Que impacto economico tuvo un programa o evento (no hay metricas publicadas estructuradas).",
    "Si un barrio esta saturado o vacio en terminos reales (falta denominador poblacional y vigencia de la oferta).",
    "Cuanto empleo genera el sector (sin fuente estructurada integrada).",
]

CAPTIONS = {
    "f01": "Fuente: Buenos Aires Data / Ente de Turismo (F01). Registro publicado; no confirma vigencia por local.",
    "f02": "Fuente: Buenos Aires Data / AGC, recursos 2015-2025 (F02). Habilitaciones aprobadas, no locales activos; categoria inferida por rubro.",
    "f02_serie": "Fuente: Buenos Aires Data / AGC (F02). Serie solo con recursos comparables como flujo anual (2019-2024).",
    "f02_comuna": "Fuente: Buenos Aires Data / AGC (F02). Solo registros con comuna informada por la fuente.",
    "f03": "Fuente: Buenos Aires Data / Min. Espacio Publico (F03). Espacios reales; sin puestos ni datos personales.",
    "f04": "Fuente: relevamiento manual trazable sobre comunicaciones oficiales GCBA y Boletin Oficial (F04). Inventario parcial, no universo.",
    "f05": "Fuente: relevamiento manual trazable (F05). Catalogo de instrumentos vigentes; no mide impacto.",
    "mapa": "Mapa: F01 y F03 usan coordenadas de fuentes oficiales. F02 USIG es una capa opcional apagada por default; eventos y programas no se mapean como puntos.",
    "f02_usig": "Geocodificado con USIG sobre direccion normalizada; se excluyen puntos cuya comuna no coincide con la fuente. No son locales activos: son habilitaciones aprobadas.",
    "coropleta": "Coropleta: GeoJSON oficial de comunas (BA Data) + habilitaciones F02 con comuna informada. Intensidad = cantidad de habilitaciones, no locales activos.",
    "territorio_tabla": "Tabla por comuna con universos separados; las columnas no se suman entre si.",
    "resumen": "Fuente: salidas analiticas del pipeline con trazabilidad por archivo (ver Metodologia).",
}


def caption_con_fecha(key: str, date_text: str = "") -> str:
    caption = CAPTIONS.get(key, "Fuente: procesamiento propio sobre archivos trazables.")
    if date_text and date_text != "No disponible":
        return f"{caption} Consulta: {date_text}."
    return caption
