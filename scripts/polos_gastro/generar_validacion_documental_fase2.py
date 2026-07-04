from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs" / "polos_gastro"
DOCS = ROOT / "docs" / "polos_gastro"
FUENTES_DOCS = DOCS / "fuentes_externas"
FICHAS = DOCS / "fichas_polos"
CONSULTA = "2026-06-29"


PERPLEXITY_COLUMNS = [
    "polo",
    "tipo_area_sugerido_perplexity",
    "nivel_consolidacion_sugerido_perplexity",
    "fuente_principal_perplexity",
    "link_fuente_principal_perplexity",
    "fuente_secundaria_perplexity",
    "link_fuente_secundaria_perplexity",
    "evidencia_que_aporta_perplexity",
    "delimitacion_o_zona_mencionada_perplexity",
    "locales_o_referencias_mencionadas_perplexity",
    "confiabilidad_perplexity",
    "decision_sugerida_perplexity",
    "observaciones_perplexity",
    "requiere_verificacion_url",
    "requiere_busqueda_complementaria",
]

FUENTES_COLUMNS = [
    "fuente_id",
    "polo_id",
    "nombre_polo",
    "tipo_fuente",
    "nombre_fuente",
    "titulo_o_referencia",
    "url",
    "fecha_publicacion",
    "fecha_consulta",
    "evidencia_que_aporta",
    "delimitacion_mencionada",
    "locales_mencionados",
    "confiabilidad",
    "uso_recomendado",
    "limitaciones",
    "requiere_revision_manual",
]

VALIDACION_COLUMNS = [
    "polo_id",
    "nombre_polo",
    "tipo_area_fase1",
    "tipo_area_revisado",
    "nivel_consolidacion_fase1",
    "nivel_consolidacion_revisado",
    "cantidad_fuentes_total",
    "cantidad_fuentes_alta",
    "cantidad_fuentes_media",
    "cantidad_fuentes_baja",
    "cantidad_fuentes_requiere_revision",
    "hay_fuente_oficial",
    "hay_fuente_periodistica",
    "hay_fuente_datos_abiertos",
    "hay_fuente_turistica",
    "hay_fuente_academica",
    "hay_delimitacion_explicita",
    "hay_locales_mencionados",
    "url_pendiente",
    "estado_validacion",
    "decision_para_informe",
    "observaciones",
]


SEED_SOURCES = {
    "url_semilla_turismo_polos": {
        "seed_id": "SEM001",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo": "Polos gastronomicos",
        "url": "https://turismo.buenosaires.gob.ar/es/article/polos-gastron%C3%B3micos",
        "tipo_fuente": "turismo",
        "confiabilidad": "alta",
        "uso": "validar_existencia_polo",
        "descripcion": "Validar existencia y relato turistico/institucional de polos gastronomicos. Revisar paginacion cuando el contenido aparece distribuido.",
        "estado_url": "verificada",
    },
    "url_semilla_gastronomia_ba": {
        "seed_id": "SEM002",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo": "Gastronomia en Buenos Aires",
        "url": "https://turismo.buenosaires.gob.ar/es/article/gastronom%C3%ADa-en-buenos-aires",
        "tipo_fuente": "turismo",
        "confiabilidad": "alta",
        "uso": "contexto_turistico",
        "descripcion": "Fuente oficial para menciones generales de Palermo, Puerto Madero, Las Canitas, Recoleta y San Telmo como zonas gastronomicas de la ciudad.",
        "estado_url": "verificada",
    },
    "url_semilla_popular_areas": {
        "seed_id": "SEM003",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo": "Popular areas for eating out",
        "url": "https://turismo.buenosaires.gob.ar/en/article/popular-areas-eating-out",
        "tipo_fuente": "turismo",
        "confiabilidad": "alta",
        "uso": "contexto_turistico",
        "descripcion": "Fuente turistica oficial en ingles para Las Canitas, Palermo Hollywood y otras zonas mencionadas como areas populares para comer.",
        "estado_url": "verificada",
    },
    "url_semilla_badata_oferta": {
        "seed_id": "SEM004",
        "nombre_fuente": "Buenos Aires Data",
        "titulo": "Oferta y Establecimientos gastronomicos",
        "url": "https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos",
        "tipo_fuente": "datos_abiertos",
        "confiabilidad": "media",
        "uso": "evidencia_cuantitativa",
        "descripcion": "Base abierta para medir oferta gastronomica por barrio o zona. No valida por si sola un polo institucional.",
        "estado_url": "verificada",
    },
    "url_semilla_badata_recurso": {
        "seed_id": "SEM005",
        "nombre_fuente": "Buenos Aires Data",
        "titulo": "Recurso Oferta gastronomica",
        "url": "https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos/resource/e66613ef-aaf4-44aa-b89c-638c431fef0e",
        "tipo_fuente": "datos_abiertos",
        "confiabilidad": "media",
        "uso": "evidencia_cuantitativa",
        "descripcion": "Recurso con campos de establecimientos gastronomicos. Util para futura etapa cuantitativa, no para afirmar delimitaciones sin analisis.",
        "estado_url": "verificada",
    },
    "url_semilla_lanacion_concentracion": {
        "seed_id": "SEM006",
        "nombre_fuente": "La Nacion",
        "titulo": "Casi el 60% de los locales gastronomicos se concentran en siete barrios portenos",
        "url": "https://www.lanacion.com.ar/buenos-aires/casi-el-60-de-los-locales-gastronomicos-se-concentran-en-siete-barrios-portenos-nid2095107/",
        "tipo_fuente": "periodistica",
        "confiabilidad": "media",
        "uso": "evidencia_cuantitativa",
        "descripcion": "Fuente periodistica para densidad y concentracion barrial. No alcanza sola para delimitar polos.",
        "estado_url": "verificada",
    },
    "url_semilla_guia_reuniones": {
        "seed_id": "SEM007",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo": "Guia de Turismo de Reuniones 2015",
        "url": "https://turismo.buenosaires.gob.ar/sites/turismo/files/guia_turismo_de_reuniones_2015ES.pdf",
        "tipo_fuente": "turismo",
        "confiabilidad": "media",
        "uso": "contexto_turistico",
        "descripcion": "Fuente turistica/institucional para contexto de polos, especialmente Puerto Madero, Palermo Viejo, Palermo Hollywood y Las Canitas.",
        "estado_url": "verificada",
    },
    "url_semilla_plan_turistico_2023": {
        "seed_id": "SEM008",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo": "Plan de desarrollo / gestion estrategica de la oferta turistica 2023",
        "url": "https://turismo.buenosaires.gob.ar/sites/turismo/files/plan-desarrollo-gestion-estrategica-oferta-turistica-2023.pdf",
        "tipo_fuente": "turismo",
        "confiabilidad": "media",
        "uso": "contexto_turistico",
        "descripcion": "Fuente estrategica/turistica para revisar menciones a productos turisticos y oferta gastronomica. Citar solo si el texto menciona efectivamente el polo.",
        "estado_url": "verificada",
    },
}


PERPLEXITY_ROWS = [
    {
        "polo": "Palermo Soho",
        "tipo": "subpolo",
        "nivel": "consolidado",
        "fuente_principal": "Turismo Buenos Aires - Polos gastronomicos",
        "link_principal": "url_semilla_turismo_polos",
        "fuente_secundaria": "Turismo Buenos Aires - Gastronomia en Buenos Aires",
        "link_secundaria": "url_semilla_gastronomia_ba",
        "evidencia": "Lo identifica como subzona de Palermo con oferta gastronomica; fuente oficial descriptiva.",
        "delimitacion": "Scalabrini Ortiz, Cordoba, Juan B. Justo y Santa Fe.",
        "locales": "No enumera locales especificos.",
        "confiabilidad": "alta",
        "decision": "incluir_como_polo_consolidado",
        "observaciones": "Buen respaldo institucional; util para validar existencia y aproximacion territorial.",
        "requiere_busqueda": "no",
    },
    {
        "polo": "Palermo Hollywood",
        "tipo": "subpolo",
        "nivel": "consolidado",
        "fuente_principal": "Turismo Buenos Aires - Polos gastronomicos",
        "link_principal": "url_semilla_turismo_polos",
        "fuente_secundaria": "Turismo Buenos Aires - Popular areas for eating out",
        "link_secundaria": "url_semilla_popular_areas",
        "evidencia": "Lo presenta como polo activo dentro de Palermo, con foco gastronomico.",
        "delimitacion": "Juan B. Justo, Dorrego, Santa Fe y Cordoba.",
        "locales": "No enumera locales especificos.",
        "confiabilidad": "alta",
        "decision": "incluir_como_polo_consolidado",
        "observaciones": "Muy solido como subpolo reconocido por turismo oficial.",
        "requiere_busqueda": "no",
    },
    {
        "polo": "Las Canitas",
        "tipo": "subpolo",
        "nivel": "consolidado",
        "fuente_principal": "Turismo Buenos Aires - Polos gastronomicos",
        "link_principal": "url_semilla_turismo_polos",
        "fuente_secundaria": "Turismo Buenos Aires - Popular areas for eating out",
        "link_secundaria": "url_semilla_popular_areas",
        "evidencia": "Lo describe como polo gastronomico nacido en calle Baez y alrededores.",
        "delimitacion": "Baez y calles aledanas, en Palermo.",
        "locales": "Serie de restaurantes, sin listado.",
        "confiabilidad": "alta",
        "decision": "incluir_como_polo_consolidado",
        "observaciones": "Fuerte como subzona gastronomica; no presentarlo como barrio independiente.",
        "requiere_busqueda": "no",
    },
    {
        "polo": "Villa Crespo",
        "tipo": "barrio",
        "nivel": "emergente",
        "fuente_principal": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_principal": "url_semilla_badata_oferta",
        "fuente_secundaria": "Buenos Aires Data - descarga dataset",
        "link_secundaria": "url_semilla_badata_recurso",
        "evidencia": "Permite verificar locales georreferenciados; evidencia de presencia de establecimientos, no de polo formal.",
        "delimitacion": "Barrio Villa Crespo.",
        "locales": "Ejemplo de dataset mencionado por Perplexity.",
        "confiabilidad": "media",
        "decision": "mencionar_en_anexo",
        "observaciones": "Requiere cruce cuantitativo para probar concentracion.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Puerto Madero",
        "tipo": "zona_costera",
        "nivel": "consolidado",
        "fuente_principal": "Turismo Buenos Aires - Gastronomia en Buenos Aires",
        "link_principal": "url_semilla_gastronomia_ba",
        "fuente_secundaria": "Guia Turismo de Reuniones",
        "link_secundaria": "url_semilla_guia_reuniones",
        "evidencia": "Lo describe como polo gastronomico importante y centro residencial/gastronomico regenerado.",
        "delimitacion": "Antiguos docks; Av. Alicia Moreau de Justo.",
        "locales": "No enumera locales especificos.",
        "confiabilidad": "alta",
        "decision": "incluir_como_polo_consolidado",
        "observaciones": "Muy solido; valor turistico y urbanistico.",
        "requiere_busqueda": "no",
    },
    {
        "polo": "San Telmo",
        "tipo": "barrio",
        "nivel": "consolidado",
        "fuente_principal": "Turismo Buenos Aires - Gastronomia en Buenos Aires",
        "link_principal": "url_semilla_gastronomia_ba",
        "fuente_secundaria": "Turismo Buenos Aires - Polos gastronomicos",
        "link_secundaria": "url_semilla_turismo_polos",
        "evidencia": "Lo nombra como polo gastronomico y menciona recuperacion/boom inmobiliario y oferta amplia.",
        "delimitacion": "Barrio San Telmo.",
        "locales": "Mencion a unos 150 restaurantes segun Perplexity.",
        "confiabilidad": "alta",
        "decision": "incluir_como_polo_consolidado",
        "observaciones": "Buen caso para informe principal.",
        "requiere_busqueda": "no",
    },
    {
        "polo": "Chacarita",
        "tipo": "barrio",
        "nivel": "requiere_validacion",
        "fuente_principal": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_principal": "url_semilla_badata_oferta",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "Hay potencial para mapear oferta, pero no aparecio respaldo directo como polo en fuentes recuperadas por Perplexity.",
        "delimitacion": "Barrio Chacarita.",
        "locales": "No hay referencias especificas.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Buscar notas periodisticas especificas o mapas de corredores.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Barrio Chino",
        "tipo": "subpolo",
        "nivel": "relevante",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "Turismo Buenos Aires - Gastronomia en Buenos Aires",
        "link_secundaria": "url_semilla_gastronomia_ba",
        "evidencia": "Aparece como referencia dentro de Belgrano, pero no como delimitacion oficial independiente.",
        "delimitacion": "Belgrano.",
        "locales": "No lista locales del corredor.",
        "confiabilidad": "media",
        "decision": "mencionar_en_anexo",
        "observaciones": "Tratar como subzona comercial/cultural, no como barrio.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Bajo Belgrano",
        "tipo": "subpolo",
        "nivel": "requiere_validacion",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "Mencion indirecta dentro de Belgrano; falta evidencia especifica.",
        "delimitacion": "Bajo Belgrano.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Necesita busqueda manual por corredor/locales.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Belgrano R",
        "tipo": "barrio",
        "nivel": "emergente",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "Aparece en datos de concentracion por barrio, pero no como polo gastronomico explicito.",
        "delimitacion": "Belgrano R.",
        "locales": "No hay.",
        "confiabilidad": "media",
        "decision": "mencionar_en_anexo",
        "observaciones": "Util como barrio con presencia gastronomica, no como polo probado.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Recoleta",
        "tipo": "barrio",
        "nivel": "consolidado",
        "fuente_principal": "Turismo Buenos Aires - Gastronomia en Buenos Aires",
        "link_principal": "url_semilla_gastronomia_ba",
        "fuente_secundaria": "Turismo Buenos Aires - Polos gastronomicos",
        "link_secundaria": "url_semilla_turismo_polos",
        "evidencia": "Polo historico y uno de los mas antiguos; mencion a La Biela.",
        "delimitacion": "Barrio Recoleta.",
        "locales": "La Biela.",
        "confiabilidad": "alta",
        "decision": "incluir_como_polo_consolidado",
        "observaciones": "Muy fuerte para informe institucional.",
        "requiere_busqueda": "no",
    },
    {
        "polo": "Caballito",
        "tipo": "barrio",
        "nivel": "relevante",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_secundaria": "url_semilla_badata_oferta",
        "evidencia": "Alta concentracion de locales; faltan fuentes que lo definan como polo especifico.",
        "delimitacion": "Barrio Caballito.",
        "locales": "No hay listado.",
        "confiabilidad": "media",
        "decision": "mencionar_en_anexo",
        "observaciones": "Mejor como barrio con fuerte densidad gastronomica.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Costanera Norte",
        "tipo": "zona_costera",
        "nivel": "requiere_validacion",
        "fuente_principal": "sin_fuente",
        "link_principal": "url_pendiente",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "No se recupero evidencia suficiente.",
        "delimitacion": "No definida.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Requiere busqueda manual especifica por Costanera Norte y locales.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Avenida Caseros / Barracas",
        "tipo": "avenida",
        "nivel": "emergente",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_secundaria": "url_semilla_badata_oferta",
        "evidencia": "Contexto de Barracas/Constitucion como areas con menor concentracion; no prueba corredor.",
        "delimitacion": "Barracas / eje Caseros.",
        "locales": "No hay.",
        "confiabilidad": "media",
        "decision": "mencionar_en_anexo",
        "observaciones": "No sobredimensionar como polo consolidado.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Microcentro y Centro",
        "tipo": "zona_central",
        "nivel": "relevante",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_secundaria": "url_semilla_badata_oferta",
        "evidencia": "Retiro/Microcentro entre barrios con alta concentracion; util para zona central.",
        "delimitacion": "Retiro y area central, sin delimitacion fina.",
        "locales": "Sin listado especifico.",
        "confiabilidad": "media",
        "decision": "incluir_como_polo_relevante",
        "observaciones": "Tratar como zona central con densidad gastronomica.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Avenida Corrientes",
        "tipo": "avenida",
        "nivel": "requiere_validacion",
        "fuente_principal": "sin_fuente",
        "link_principal": "url_pendiente",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "No se recupero evidencia especifica suficiente.",
        "delimitacion": "No definida.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Puede ser relevante culturalmente, falta prueba gastronomica.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Abasto",
        "tipo": "barrio",
        "nivel": "requiere_validacion",
        "fuente_principal": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_principal": "url_semilla_badata_oferta",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "Hay base de oferta abierta, no evidencia directa de polo consolidado.",
        "delimitacion": "Abasto.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Requiere notas especificas o analisis de densidad.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Avenida Boedo",
        "tipo": "avenida",
        "nivel": "requiere_validacion",
        "fuente_principal": "sin_fuente",
        "link_principal": "url_pendiente",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "Sin evidencia suficiente recuperada.",
        "delimitacion": "No definida.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Buscar manualmente con foco cultural y bares tradicionales.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Devoto",
        "tipo": "barrio",
        "nivel": "requiere_validacion",
        "fuente_principal": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_principal": "url_semilla_badata_oferta",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "Potencial de relevamiento por dataset, sin prueba de polo.",
        "delimitacion": "Barrio Devoto.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Necesita evidencia externa adicional.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "DoHo / Donado-Holmberg",
        "tipo": "corredor",
        "nivel": "requiere_validacion",
        "fuente_principal": "sin_fuente",
        "link_principal": "url_pendiente",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "No se recupero fuente verificable especifica.",
        "delimitacion": "Donado-Holmberg.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Corredor plausible, pero no probado.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Villa Urquiza",
        "tipo": "barrio",
        "nivel": "emergente",
        "fuente_principal": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_principal": "url_semilla_badata_oferta",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "Base de oferta georreferenciada; faltan fuentes que lo nombren como polo.",
        "delimitacion": "Villa Urquiza.",
        "locales": "No hay.",
        "confiabilidad": "media",
        "decision": "mencionar_en_anexo",
        "observaciones": "Util como zona con oferta, no como polo cerrado.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Nuevo Bajo en Retiro / Esmeralda y Paraguay",
        "tipo": "subpolo",
        "nivel": "requiere_validacion",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "Turismo Buenos Aires - Gastronomia en Buenos Aires",
        "link_secundaria": "url_semilla_gastronomia_ba",
        "evidencia": "Retiro aparece como barrio con bares destacados, pero no hay delimitacion de este subeje.",
        "delimitacion": "Retiro; no tramo Esmeralda/Paraguay.",
        "locales": "No hay.",
        "confiabilidad": "media",
        "decision": "mencionar_en_anexo",
        "observaciones": "Zonificacion exacta pendiente.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Federico Lacroze / Libertador a Cabildo",
        "tipo": "avenida",
        "nivel": "requiere_validacion",
        "fuente_principal": "sin_fuente",
        "link_principal": "url_pendiente",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "No se verifico evidencia suficiente.",
        "delimitacion": "Tramo propuesto.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Requiere busqueda manual especifica.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Parque Saavedra / Garcia del Rio",
        "tipo": "barrio",
        "nivel": "requiere_validacion",
        "fuente_principal": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_principal": "url_semilla_badata_oferta",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "Dataset permite explorar oferta, pero no prueba polo.",
        "delimitacion": "Saavedra.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Validar si es corredor emergente o concentracion barrial.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Paternal",
        "tipo": "circuito",
        "nivel": "requiere_validacion",
        "fuente_principal": "sin_fuente",
        "link_principal": "url_pendiente",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "No se recupero evidencia suficiente para circuito gastronomico.",
        "delimitacion": "Paternal.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Pendiente de validacion.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Villa Pueyrredon / Av. San Martin",
        "tipo": "avenida",
        "nivel": "requiere_validacion",
        "fuente_principal": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_principal": "url_semilla_badata_oferta",
        "fuente_secundaria": "sin_fuente",
        "link_secundaria": "url_pendiente",
        "evidencia": "Solo base de oferta abierta, sin polo probado.",
        "delimitacion": "Villa Pueyrredon / Av. San Martin.",
        "locales": "No hay.",
        "confiabilidad": "requiere_revision",
        "decision": "no_incluir_aun",
        "observaciones": "Falta evidencia externa de corredor.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Colegiales",
        "tipo": "barrio",
        "nivel": "relevante",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_secundaria": "url_semilla_badata_oferta",
        "evidencia": "Aparece como barrio con alta concentracion de locales.",
        "delimitacion": "Colegiales.",
        "locales": "Sin listado especifico.",
        "confiabilidad": "media",
        "decision": "incluir_como_polo_relevante",
        "observaciones": "Mejor como barrio relevante, no necesariamente polo formal.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Monserrat",
        "tipo": "barrio",
        "nivel": "relevante",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_secundaria": "url_semilla_badata_oferta",
        "evidencia": "Figura entre barrios con elevada concentracion de locales.",
        "delimitacion": "Monserrat.",
        "locales": "Sin listado especifico.",
        "confiabilidad": "media",
        "decision": "incluir_como_polo_relevante",
        "observaciones": "Util como barrio central con densidad gastronomica.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Retiro",
        "tipo": "barrio",
        "nivel": "relevante",
        "fuente_principal": "Turismo Buenos Aires - Gastronomia en Buenos Aires",
        "link_principal": "url_semilla_gastronomia_ba",
        "fuente_secundaria": "La Nacion - concentracion de locales",
        "link_secundaria": "url_semilla_lanacion_concentracion",
        "evidencia": "Turismo oficial lo menciona entre zonas de bares destacados; prensa lo incluye en concentracion.",
        "delimitacion": "Retiro.",
        "locales": "Sin listado especifico.",
        "confiabilidad": "alta",
        "decision": "incluir_como_polo_relevante",
        "observaciones": "Puede ir como zona central relevante, no necesariamente polo consolidado.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Flores",
        "tipo": "barrio",
        "nivel": "relevante",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_secundaria": "url_semilla_badata_oferta",
        "evidencia": "Aparece en grupo de alta concentracion de locales.",
        "delimitacion": "Flores.",
        "locales": "Sin listado especifico.",
        "confiabilidad": "media",
        "decision": "mencionar_en_anexo",
        "observaciones": "Relevante como barrio de oferta, no como polo probado.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Floresta",
        "tipo": "barrio",
        "nivel": "relevante",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_secundaria": "url_semilla_badata_oferta",
        "evidencia": "Se menciona entre barrios con concentracion importante.",
        "delimitacion": "Floresta.",
        "locales": "Sin listado especifico.",
        "confiabilidad": "media",
        "decision": "mencionar_en_anexo",
        "observaciones": "Mejor como evidencia contextual.",
        "requiere_busqueda": "si",
    },
    {
        "polo": "Parque Patricios",
        "tipo": "barrio",
        "nivel": "relevante",
        "fuente_principal": "La Nacion - concentracion de locales",
        "link_principal": "url_semilla_lanacion_concentracion",
        "fuente_secundaria": "Buenos Aires Data - Oferta y Establecimientos gastronomicos",
        "link_secundaria": "url_semilla_badata_oferta",
        "evidencia": "Aparece en mapa de oferta/concentracion, pero no como polo principal.",
        "delimitacion": "Parque Patricios.",
        "locales": "Sin listado especifico.",
        "confiabilidad": "media",
        "decision": "mencionar_en_anexo",
        "observaciones": "Util para contexto, no para polo principal.",
        "requiere_busqueda": "si",
    },
]


POLO_META = {
    "Palermo Soho": {
        "polo_id": "PG001A_PALERMO_SOHO",
        "fase1_parent": "PG001_PALERMO_SOHO_HOLLYWOOD_Y_LAS_CANITAS",
        "estado": "validado_fuerte",
        "decision": "incluir_como_polo_consolidado",
        "observacion": "Subpolo desagregado de Palermo Fase 1; no reemplaza la base original.",
    },
    "Palermo Hollywood": {
        "polo_id": "PG001B_PALERMO_HOLLYWOOD",
        "fase1_parent": "PG001_PALERMO_SOHO_HOLLYWOOD_Y_LAS_CANITAS",
        "estado": "validado_fuerte",
        "decision": "incluir_como_polo_consolidado",
        "observacion": "Subpolo desagregado de Palermo Fase 1; mantener advertencia de escala.",
    },
    "Las Canitas": {
        "polo_id": "PG001C_LAS_CANITAS",
        "fase1_parent": "PG001_PALERMO_SOHO_HOLLYWOOD_Y_LAS_CANITAS",
        "estado": "validado_fuerte",
        "decision": "incluir_como_polo_consolidado",
        "observacion": "Subpolo de Palermo; no tratar como barrio independiente.",
    },
    "Villa Crespo": {
        "polo_id": "PG002_VILLA_CRESPO",
        "fase1_parent": "PG002_VILLA_CRESPO",
        "estado": "candidato_con_evidencia",
        "decision": "incluir_como_polo_emergente",
        "observacion": "Tiene evidencia de oferta y fuente complementaria puntual; falta delimitacion.",
    },
    "Puerto Madero": {
        "polo_id": "PG003_PUERTO_MADERO",
        "fase1_parent": "PG003_PUERTO_MADERO",
        "estado": "validado_fuerte",
        "decision": "incluir_como_polo_consolidado",
        "observacion": "Polo consolidado con respaldo turistico institucional.",
    },
    "San Telmo": {
        "polo_id": "PG004_SAN_TELMO",
        "fase1_parent": "PG004_SAN_TELMO",
        "estado": "validado_fuerte",
        "decision": "incluir_como_polo_consolidado",
        "observacion": "Polo consolidado; requiere cuidar diferencia entre barrio y circuitos internos.",
    },
    "Chacarita": {
        "polo_id": "PG005_CHACARITA",
        "fase1_parent": "PG005_CHACARITA",
        "estado": "validado_medio",
        "decision": "incluir_como_polo_relevante",
        "observacion": "La busqueda complementaria encontro una pagina oficial de Turismo BA dedicada al polo.",
    },
    "Barrio Chino": {
        "polo_id": "PG006A_BARRIO_CHINO",
        "fase1_parent": "PG006_BELGRANO_BARRIO_CHINO_BAJO_BELGRANO_BELGRA",
        "estado": "validado_medio",
        "decision": "incluir_como_polo_relevante",
        "observacion": "Subzona comercial y turistica de Belgrano; no tratar como barrio administrativo.",
    },
    "Bajo Belgrano": {
        "polo_id": "PG006B_BAJO_BELGRANO",
        "fase1_parent": "PG006_BELGRANO_BARRIO_CHINO_BAJO_BELGRANO_BELGRA",
        "estado": "requiere_validacion",
        "decision": "no_incluir_aun",
        "observacion": "Hay fuentes de entorno costero y Belgrano, pero no un recorte documental del subpolo.",
    },
    "Belgrano R": {
        "polo_id": "PG006C_BELGRANO_R",
        "fase1_parent": "PG006_BELGRANO_BARRIO_CHINO_BAJO_BELGRANO_BELGRA",
        "estado": "candidato_con_evidencia",
        "decision": "mencionar_en_anexo",
        "observacion": "Evidencia de barrio con oferta, sin delimitacion de polo gastronomico.",
    },
    "Recoleta": {
        "polo_id": "PG007_RECOLETA",
        "fase1_parent": "PG007_RECOLETA",
        "estado": "validado_fuerte",
        "decision": "incluir_como_polo_consolidado",
        "observacion": "Polo tradicional con respaldo de fuentes turisticas.",
    },
    "Caballito": {
        "polo_id": "PG008_CABALLITO",
        "fase1_parent": "PG008_CABALLITO",
        "estado": "candidato_con_evidencia",
        "decision": "incluir_como_polo_emergente",
        "observacion": "Fuentes puntuales de mercados/patios y evidencia de concentracion; no cerrar como polo formal.",
    },
    "Costanera Norte": {
        "polo_id": "PG009_COSTANERA_NORTE",
        "fase1_parent": "PG009_COSTANERA_NORTE",
        "estado": "candidato_con_evidencia",
        "decision": "incluir_como_corredor_candidato",
        "observacion": "Fuentes oficiales describen atractivos/patios costeros; falta delimitar corredor gastronomico.",
    },
    "Avenida Caseros / Barracas": {
        "polo_id": "PG010_AVENIDA_CASEROS_BARRACAS",
        "fase1_parent": "PG010_AVENIDA_CASEROS_BARRACAS",
        "estado": "requiere_validacion",
        "decision": "mencionar_en_anexo",
        "observacion": "La evidencia sigue siendo indirecta; requiere busqueda especifica del corredor Caseros.",
    },
    "Microcentro y Centro": {
        "polo_id": "PG011_MICROCENTRO_CENTRO_RENOVADO",
        "fase1_parent": "PG011_MICROCENTRO_CENTRO_RENOVADO",
        "estado": "validado_medio",
        "decision": "incluir_como_polo_relevante",
        "observacion": "Zona central con evidencia de densidad; no tiene delimitacion fina unica.",
    },
    "Avenida Corrientes": {
        "polo_id": "PG012_AVENIDA_CORRIENTES",
        "fase1_parent": "PG012_AVENIDA_CORRIENTES",
        "estado": "candidato_con_evidencia",
        "decision": "incluir_como_corredor_candidato",
        "observacion": "Fuente turistica respalda identidad de teatro y pizza; falta delimitar como corredor gastronomico.",
    },
    "Abasto": {
        "polo_id": "PG013_ABASTO",
        "fase1_parent": "PG013_ABASTO",
        "estado": "candidato_con_evidencia",
        "decision": "mencionar_en_anexo",
        "observacion": "Tiene hitos turisticos/gastronomicos, pero se solapa con Corrientes y Balvanera.",
    },
    "Avenida Boedo": {
        "polo_id": "PG014_AVENIDA_BOEDO",
        "fase1_parent": "PG014_AVENIDA_BOEDO",
        "estado": "requiere_validacion",
        "decision": "no_incluir_aun",
        "observacion": "La busqueda dejo referencias culturales, pero no una fuente suficiente de corredor gastronomico.",
    },
    "Devoto": {
        "polo_id": "PG015_DEVOTO",
        "fase1_parent": "PG015_DEVOTO",
        "estado": "candidato_con_evidencia",
        "decision": "incluir_como_polo_emergente",
        "observacion": "Fuente oficial barrial menciona circuito gourmet; requiere apoyo cuantitativo.",
    },
    "DoHo / Donado-Holmberg": {
        "polo_id": "PG016_CORREDOR_DOHO_DONADO_HOLMBERG",
        "fase1_parent": "PG016_CORREDOR_DOHO_DONADO_HOLMBERG",
        "estado": "candidato_con_evidencia",
        "decision": "incluir_como_corredor_candidato",
        "observacion": "Fuente oficial de circuito gastronomico en Donado-Holmberg; requiere validacion de vigencia.",
    },
    "Villa Urquiza": {
        "polo_id": "PG017_VILLA_URQUIZA",
        "fase1_parent": "PG017_VILLA_URQUIZA",
        "estado": "candidato_con_evidencia",
        "decision": "incluir_como_polo_emergente",
        "observacion": "La evidencia complementaria se apoya en Donado-Holmberg y Villa Urquiza; falta cuantificar barrio.",
    },
    "Nuevo Bajo en Retiro / Esmeralda y Paraguay": {
        "polo_id": "PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY",
        "fase1_parent": "PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY",
        "estado": "requiere_validacion",
        "decision": "mencionar_en_anexo",
        "observacion": "Retiro esta respaldado, pero no el subeje Esmeralda-Paraguay.",
    },
    "Federico Lacroze / Libertador a Cabildo": {
        "polo_id": "PG019_AVENIDA_FEDERICO_LACROZE_DESDE_LIBERTADOR_",
        "fase1_parent": "PG019_AVENIDA_FEDERICO_LACROZE_DESDE_LIBERTADOR_",
        "estado": "requiere_validacion",
        "decision": "no_incluir_aun",
        "observacion": "Hay referencias puntuales cercanas, no evidencia del tramo como corredor gastronomico.",
    },
    "Parque Saavedra / Garcia del Rio": {
        "polo_id": "PG020_PARQUE_SAAVEDRA_AVENIDA_GARCIA_DEL_RIO",
        "fase1_parent": "PG020_PARQUE_SAAVEDRA_AVENIDA_GARCIA_DEL_RIO",
        "estado": "requiere_validacion",
        "decision": "no_incluir_aun",
        "observacion": "No se encontro fuente suficiente de corredor Garcia del Rio.",
    },
    "Paternal": {
        "polo_id": "PG021_CIRCUITO_GASTRONOMICO_DE_PATERNAL",
        "fase1_parent": "PG021_CIRCUITO_GASTRONOMICO_DE_PATERNAL",
        "estado": "candidato_con_evidencia",
        "decision": "incluir_como_corredor_candidato",
        "observacion": "Distrito del Vino aporta contexto territorial, pero no valida por si solo circuito gastronomico.",
    },
    "Villa Pueyrredon / Av. San Martin": {
        "polo_id": "PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN",
        "fase1_parent": "PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN",
        "estado": "requiere_validacion",
        "decision": "no_incluir_aun",
        "observacion": "No hay fuente especifica suficiente para el eje Av. San Martin en esta etapa.",
    },
    "Colegiales": {
        "polo_id": "PGF2_COLEGIALES",
        "fase1_parent": "",
        "estado": "candidato_con_evidencia",
        "decision": "incluir_como_polo_emergente",
        "observacion": "Aporte de Perplexity como candidato contextual fuera de la base Fase 1.",
    },
    "Monserrat": {
        "polo_id": "PGF2_MONTSERRAT",
        "fase1_parent": "",
        "estado": "validado_medio",
        "decision": "incluir_como_polo_relevante",
        "observacion": "Zona central con evidencia periodistica y datos abiertos; requiere recorte territorial.",
    },
    "Retiro": {
        "polo_id": "PGF2_RETIRO",
        "fase1_parent": "",
        "estado": "validado_medio",
        "decision": "incluir_como_polo_relevante",
        "observacion": "Zona central relevante; no confundir con el subeje Nuevo Bajo.",
    },
    "Flores": {
        "polo_id": "PGF2_FLORES",
        "fase1_parent": "",
        "estado": "candidato_con_evidencia",
        "decision": "mencionar_en_anexo",
        "observacion": "Evidencia de barrio con oferta; falta definicion de polo.",
    },
    "Floresta": {
        "polo_id": "PGF2_FLORESTA",
        "fase1_parent": "",
        "estado": "candidato_con_evidencia",
        "decision": "mencionar_en_anexo",
        "observacion": "Evidencia contextual de concentracion; falta fuente de polo.",
    },
    "Parque Patricios": {
        "polo_id": "PGF2_PARQUE_PATRICIOS",
        "fase1_parent": "",
        "estado": "candidato_con_evidencia",
        "decision": "mencionar_en_anexo",
        "observacion": "Fuente de patio gastronomico ayuda como candidato, no como barrio consolidado.",
    },
}


COMPLEMENTARY_SOURCES = [
    {
        "fuente_id": "COMP001",
        "polo": "Chacarita",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Polo gastronomico Chacarita",
        "url": "https://turismo.buenosaires.gob.ar/es/article/polo-gastron%C3%B3mico-chacarita",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Pagina oficial dedicada al polo gastronomico Chacarita; permite mejorar el respaldo documental del caso.",
        "delimitacion_mencionada": "Chacarita; sin limites administrativos cerrados en esta matriz.",
        "locales_mencionados": "Menciones de locales en pagina turistica; no se cargan como padron.",
        "confiabilidad": "alta",
        "uso_recomendado": "validar_existencia_polo",
        "limitaciones": "Fuente turistica; no define por si sola densidad ni delimitacion operativa.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP002",
        "polo": "Barrio Chino",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Barrio Chino / Pasaje Echeverria",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/barrio-chino",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Reconoce la zona como atractivo con oferta gastronomica/comercial y mejora la trazabilidad del subpolo.",
        "delimitacion_mencionada": "Belgrano; entorno Arribenos, Olazabal, Juramento y Pasaje Echeverria segun paginas turisticas.",
        "locales_mencionados": "Sin cargar locales como padron.",
        "confiabilidad": "alta",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "Subzona comercial-cultural; no barrio administrativo ni delimitacion gastronomica cerrada.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP003",
        "polo": "Caballito",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Patio de los Lecheros",
        "url": "https://turismo.buenosaires.gob.ar/es/gastronomico/patio-de-los-lecheros",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Aporta un hito gastronomico reconocido en Caballito.",
        "delimitacion_mencionada": "Caballito; unidad puntual, no corredor.",
        "locales_mencionados": "Puestos gastronomicos no individualizados en esta matriz.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "Valida un hito, no todo el barrio como polo.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP004",
        "polo": "Caballito",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Mercado del Progreso",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/mercado-del-progreso",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Aporta otro hito de oferta gastronomica/comercial en Caballito.",
        "delimitacion_mencionada": "Caballito; mercado historico.",
        "locales_mencionados": "Puestos y rubros del mercado; no se cargan como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "No delimita un polo barrial.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP005",
        "polo": "Costanera Norte",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Patio Costanera Norte",
        "url": "https://turismo.buenosaires.gob.ar/es/gastronomico/patio-costanera-norte",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Reconoce oferta gastronomica en Costanera Norte como hito puntual.",
        "delimitacion_mencionada": "Costanera Norte; unidad puntual.",
        "locales_mencionados": "Oferta del patio; no se desagrega como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "Hito especifico; no valida por si solo el corredor completo.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP006",
        "polo": "Costanera Norte",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Costanera Norte",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/costanera-norte",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Fuente de contexto territorial para el corredor costero.",
        "delimitacion_mencionada": "Ribera norte de la ciudad; no recorte gastronomico cerrado.",
        "locales_mencionados": "Sin listado de locales cargado.",
        "confiabilidad": "media",
        "uso_recomendado": "contexto_turistico",
        "limitaciones": "Contexto espacial, no prueba suficiente de polo gastronomico.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP007",
        "polo": "Parque Patricios",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Smart Plaza Patio Parque Patricios",
        "url": "https://turismo.buenosaires.gob.ar/es/gastronomico/smart-plaza-patio-parque-patricios",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Hito gastronomico puntual para Parque Patricios.",
        "delimitacion_mencionada": "Parque Patricios; unidad puntual.",
        "locales_mencionados": "Puestos/operadores no cargados como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "No valida al barrio como polo completo.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP008",
        "polo": "DoHo / Donado-Holmberg",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Circuito Sin Pausa",
        "url": "https://turismo.buenosaires.gob.ar/es/article/circuito-sin-pausa",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Fuente oficial que describe gastronomia en Donado-Holmberg y Villa Urquiza.",
        "delimitacion_mencionada": "Donado y Holmberg; Villa Urquiza.",
        "locales_mencionados": "Menciones de oferta; no se cargan como padron.",
        "confiabilidad": "alta",
        "uso_recomendado": "delimitar_zona",
        "limitaciones": "Requiere revisar vigencia y densidad actual antes de informe final.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP009",
        "polo": "Villa Urquiza",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Circuito Sin Pausa",
        "url": "https://turismo.buenosaires.gob.ar/es/article/circuito-sin-pausa",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Aporta respaldo documental para Villa Urquiza vinculado al eje Donado-Holmberg.",
        "delimitacion_mencionada": "Donado y Holmberg; Villa Urquiza.",
        "locales_mencionados": "Menciones de oferta; no se cargan como padron.",
        "confiabilidad": "alta",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "No cubre todo el barrio Villa Urquiza.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP010",
        "polo": "Avenida Corrientes",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "A night of theatre and pizza",
        "url": "https://turismo.buenosaires.gob.ar/en/atractivo/800pm-night-theatre-and-pizza",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Reconoce la asociacion entre Avenida Corrientes, teatros y pizzerias como identidad gastronomica.",
        "delimitacion_mencionada": "Avenida Corrientes; no tramo operativo cerrado.",
        "locales_mencionados": "Pizzerias tradicionales mencionadas en la pagina; no se cargan como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "Identidad cultural/gastronomica; no equivale a polo institucional.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP011",
        "polo": "Abasto",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Abasto Shopping",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/abasto-shopping",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Hito turistico/comercial del Abasto con oferta de consumo; ayuda a caracterizar zona.",
        "delimitacion_mencionada": "Abasto/Balvanera; hito puntual.",
        "locales_mencionados": "No se cargan locales como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "contexto_turistico",
        "limitaciones": "Centro comercial; no valida un polo barrial.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP012",
        "polo": "Devoto",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Barrio Villa Devoto",
        "url": "https://turismo.buenosaires.gob.ar/es/turismo-en-barrios/barrio-villa-devoto",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Fuente oficial barrial que menciona atractivo gourmet/circuito de consumo local.",
        "delimitacion_mencionada": "Villa Devoto; sin corredor gastronomico delimitado.",
        "locales_mencionados": "Sin cargar locales como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "Contexto barrial; requiere validacion cuantitativa.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP013",
        "polo": "Paternal",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Distrito del Vino",
        "url": "https://turismo.buenosaires.gob.ar/es/article/distrito-del-vino",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Ubica a Paternal dentro de un distrito tematico con agenda de consumo y enoturismo.",
        "delimitacion_mencionada": "Villa Devoto, Villa del Parque y Paternal; no circuito gastronomico de Paternal.",
        "locales_mencionados": "Bodegas, vinotecas y espacios asociados; no se cargan como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "contexto_turistico",
        "limitaciones": "Valida distrito tematico, no por si solo un polo gastronomico de Paternal.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP014",
        "polo": "Villa Crespo",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Mercat Villa Crespo",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/mercat-villa-crespo",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Hito gastronomico de Villa Crespo; aporta evidencia puntual de oferta.",
        "delimitacion_mencionada": "Villa Crespo; unidad puntual.",
        "locales_mencionados": "Puestos/espacios del mercado; no se cargan como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "Hito puntual; no prueba concentracion barrial.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP015",
        "polo": "Flores",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Almuerzo coreano",
        "url": "https://turismo.buenosaires.gob.ar/es/atractivo/almuerzo-coreano",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Aporta evidencia de oferta gastronomica identitaria en el barrio coreano.",
        "delimitacion_mencionada": "Flores/Barrio coreano; no polo barrial completo.",
        "locales_mencionados": "Restaurantes del circuito no cargados como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "Circuito cultural especifico; requiere separarlo de Flores como barrio completo.",
        "requiere_revision_manual": "no",
    },
    {
        "fuente_id": "COMP016",
        "polo": "Microcentro y Centro",
        "tipo_fuente": "turismo",
        "nombre_fuente": "Turismo Buenos Aires",
        "titulo_o_referencia": "Mercado San Nicolas",
        "url": "https://turismo.buenosaires.gob.ar/es/otros-establecimientos/mercado-san-nicol%C3%A1s",
        "fecha_publicacion": "sin_fecha",
        "evidencia_que_aporta": "Hito de oferta gastronomica/comercial en el area central.",
        "delimitacion_mencionada": "San Nicolas / Centro; unidad puntual.",
        "locales_mencionados": "Puestos y rubros; no se cargan como padron.",
        "confiabilidad": "media",
        "uso_recomendado": "caracterizar_identidad",
        "limitaciones": "No delimita la zona central como polo.",
        "requiere_revision_manual": "no",
    },
]


SEARCHES = {
    "Chacarita": [
        '"Chacarita polo gastronomico Buenos Aires"',
        '"Chacarita restaurantes circuito gastronomico"',
        '"Barrios a la Carta Chacarita BA Capital Gastronomica"',
        "site:buenosaires.gob.ar Chacarita gastronomia",
    ],
    "Costanera Norte": [
        '"Costanera Norte polo gastronomico Buenos Aires"',
        '"Costanera Norte restaurantes Buenos Aires"',
        'site:buenosaires.gob.ar "Costanera Norte" gastronomia',
        '"Rodizio Gardiner Tequila Costanera Norte polo gastronomico"',
    ],
    "Avenida Caseros / Barracas": [
        '"Avenida Caseros polo gastronomico Barracas"',
        '"Avenida Caseros restaurantes Barracas"',
        '"Barracas polo gastronomico Avenida Caseros"',
        'site:buenosaires.gob.ar "Avenida Caseros" gastronomia',
    ],
    "Avenida Corrientes / Abasto": [
        '"Avenida Corrientes polo gastronomico pizzerias Buenos Aires"',
        '"Abasto polo gastronomico Buenos Aires"',
        '"Abasto restaurantes circuito gastronomico"',
        "site:buenosaires.gob.ar Abasto gastronomia",
    ],
    "Boedo": [
        '"Avenida Boedo gastronomia bares restaurantes"',
        '"Boedo polo gastronomico Buenos Aires"',
        '"Boedo circuito gastronomico"',
        "site:buenosaires.gob.ar Boedo gastronomia",
    ],
    "Devoto": [
        '"Devoto polo gastronomico Buenos Aires"',
        '"Villa Devoto restaurantes circuito gastronomico"',
        "site:buenosaires.gob.ar Devoto gastronomia",
    ],
    "DoHo / Donado-Holmberg": [
        '"DoHo Donado Holmberg polo gastronomico"',
        '"Donado Holmberg restaurantes Buenos Aires"',
        '"Distrito Donado Holmberg gastronomia"',
        "site:buenosaires.gob.ar Donado Holmberg",
    ],
    "Villa Urquiza": [
        '"Villa Urquiza polo gastronomico"',
        '"Villa Urquiza restaurantes circuito gastronomico"',
        'site:buenosaires.gob.ar "Villa Urquiza" gastronomia',
    ],
    "Nuevo Bajo Retiro / Esmeralda y Paraguay": [
        '"Nuevo Bajo Retiro restaurantes"',
        '"Esmeralda y Paraguay gastronomia"',
        '"Retiro polo gastronomico Esmeralda Paraguay"',
        "site:buenosaires.gob.ar Retiro gastronomia",
    ],
    "Federico Lacroze": [
        '"Federico Lacroze restaurantes Belgrano Colegiales"',
        '"Avenida Federico Lacroze polo gastronomico"',
        'site:buenosaires.gob.ar "Federico Lacroze" gastronomia',
    ],
    "Parque Saavedra / Garcia del Rio": [
        '"Garcia del Rio polo gastronomico Saavedra"',
        '"Parque Saavedra restaurantes Garcia del Rio"',
        "site:buenosaires.gob.ar Saavedra gastronomia",
    ],
    "Paternal": [
        '"Paternal circuito gastronomico"',
        '"La Paternal restaurantes Buenos Aires"',
        "site:buenosaires.gob.ar Paternal gastronomia",
    ],
    "Villa Pueyrredon / Av. San Martin": [
        '"Villa Pueyrredon Avenida San Martin restaurantes"',
        '"Villa Pueyrredon polo gastronomico"',
        'site:buenosaires.gob.ar "Villa Pueyrredon" gastronomia',
    ],
    "Belgrano desagregado": [
        '"Barrio Chino Belgrano gastronomia Buenos Aires"',
        '"Bajo Belgrano restaurantes circuito gastronomico"',
        '"Belgrano R restaurantes Buenos Aires"',
        'site:buenosaires.gob.ar "Barrio Chino" gastronomia',
    ],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value or "sin_nombre"


def yes_no(value: bool) -> str:
    return "si" if value else "no"


def resolve_url(token: str) -> str:
    if token == "url_pendiente":
        return "url_pendiente"
    if token in SEED_SOURCES:
        return SEED_SOURCES[token]["url"]
    return token


def is_pending_url(value: str) -> bool:
    return not value or value == "url_pendiente" or value.startswith("url_")


def source_meta_for_name(name: str, url_token: str) -> dict[str, str]:
    if name == "sin_fuente":
        return {
            "tipo_fuente": "otra",
            "nombre_fuente": "sin_fuente",
            "titulo": "url_pendiente",
            "confiabilidad": "requiere_revision",
            "uso": "solo_insumo_exploratorio",
            "limitaciones": "Perplexity no aporto fuente verificable para este campo.",
        }
    seed = SEED_SOURCES.get(url_token)
    if seed:
        return {
            "tipo_fuente": seed["tipo_fuente"],
            "nombre_fuente": seed["nombre_fuente"],
            "titulo": seed["titulo"],
            "confiabilidad": seed["confiabilidad"],
            "uso": seed["uso"],
            "limitaciones": "Fuente semilla verificada; su uso depende de no sobregeneralizar la evidencia.",
        }
    if "La Nacion" in name:
        return {
            "tipo_fuente": "periodistica",
            "nombre_fuente": "La Nacion",
            "titulo": name,
            "confiabilidad": "media",
            "uso": "evidencia_cuantitativa",
            "limitaciones": "Fuente periodistica; no delimita polos por si sola.",
        }
    if "Buenos Aires Data" in name:
        return {
            "tipo_fuente": "datos_abiertos",
            "nombre_fuente": "Buenos Aires Data",
            "titulo": name,
            "confiabilidad": "media",
            "uso": "evidencia_cuantitativa",
            "limitaciones": "Datos de oferta; requieren cruce territorial para inferir concentracion.",
        }
    if "Turismo Buenos Aires" in name or "Guia Turismo" in name:
        return {
            "tipo_fuente": "turismo",
            "nombre_fuente": "Turismo Buenos Aires",
            "titulo": name,
            "confiabilidad": "media",
            "uso": "contexto_turistico",
            "limitaciones": "Fuente turistica descriptiva; no cerrar delimitacion sin apoyo complementario.",
        }
    return {
        "tipo_fuente": "otra",
        "nombre_fuente": name,
        "titulo": name,
        "confiabilidad": "requiere_revision",
        "uso": "solo_insumo_exploratorio",
        "limitaciones": "Clasificacion automatica pendiente de revision.",
    }


def upsert_section(path: Path, marker: str, section_text: str) -> None:
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    start = f"<!-- {marker}_START -->"
    end = f"<!-- {marker}_END -->"
    block = f"{start}\n{section_text.rstrip()}\n{end}\n"
    if start in original and end in original:
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        updated = pattern.sub(block.rstrip(), original)
    else:
        updated = original.rstrip() + "\n\n" + block
    write_text(path, updated)


def build_perplexity_rows() -> list[dict[str, str]]:
    rows = []
    for item in PERPLEXITY_ROWS:
        principal_url = resolve_url(item["link_principal"])
        secundaria_url = resolve_url(item["link_secundaria"])
        rows.append(
            {
                "polo": item["polo"],
                "tipo_area_sugerido_perplexity": item["tipo"],
                "nivel_consolidacion_sugerido_perplexity": item["nivel"],
                "fuente_principal_perplexity": item["fuente_principal"],
                "link_fuente_principal_perplexity": principal_url,
                "fuente_secundaria_perplexity": item["fuente_secundaria"],
                "link_fuente_secundaria_perplexity": secundaria_url,
                "evidencia_que_aporta_perplexity": item["evidencia"],
                "delimitacion_o_zona_mencionada_perplexity": item["delimitacion"],
                "locales_o_referencias_mencionadas_perplexity": item["locales"],
                "confiabilidad_perplexity": item["confiabilidad"],
                "decision_sugerida_perplexity": item["decision"],
                "observaciones_perplexity": item["observaciones"],
                "requiere_verificacion_url": yes_no(
                    is_pending_url(principal_url) or is_pending_url(secundaria_url)
                ),
                "requiere_busqueda_complementaria": item["requiere_busqueda"],
            }
        )
    return rows


def build_fuentes_rows(perplexity_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seq = 1
    for item, normalized in zip(PERPLEXITY_ROWS, perplexity_rows):
        meta = POLO_META[item["polo"]]
        for suffix, source_name, url_token in (
            ("A", item["fuente_principal"], item["link_principal"]),
            ("B", item["fuente_secundaria"], item["link_secundaria"]),
        ):
            url = resolve_url(url_token)
            source_meta = source_meta_for_name(source_name, url_token)
            pending = is_pending_url(url)
            rows.append(
                {
                    "fuente_id": f"PX{seq:03d}{suffix}",
                    "polo_id": meta["polo_id"],
                    "nombre_polo": item["polo"],
                    "tipo_fuente": source_meta["tipo_fuente"],
                    "nombre_fuente": source_meta["nombre_fuente"],
                    "titulo_o_referencia": source_meta["titulo"],
                    "url": url,
                    "fecha_publicacion": "sin_fecha",
                    "fecha_consulta": CONSULTA,
                    "evidencia_que_aporta": normalized["evidencia_que_aporta_perplexity"],
                    "delimitacion_mencionada": normalized["delimitacion_o_zona_mencionada_perplexity"],
                    "locales_mencionados": normalized["locales_o_referencias_mencionadas_perplexity"],
                    "confiabilidad": "requiere_revision" if pending else source_meta["confiabilidad"],
                    "uso_recomendado": source_meta["uso"],
                    "limitaciones": source_meta["limitaciones"],
                    "requiere_revision_manual": yes_no(pending or item["requiere_busqueda"] == "si"),
                }
            )
        seq += 1

    for source in COMPLEMENTARY_SOURCES:
        meta = POLO_META[source["polo"]]
        rows.append(
            {
                "fuente_id": source["fuente_id"],
                "polo_id": meta["polo_id"],
                "nombre_polo": source["polo"],
                "tipo_fuente": source["tipo_fuente"],
                "nombre_fuente": source["nombre_fuente"],
                "titulo_o_referencia": source["titulo_o_referencia"],
                "url": source["url"],
                "fecha_publicacion": source["fecha_publicacion"],
                "fecha_consulta": CONSULTA,
                "evidencia_que_aporta": source["evidencia_que_aporta"],
                "delimitacion_mencionada": source["delimitacion_mencionada"],
                "locales_mencionados": source["locales_mencionados"],
                "confiabilidad": source["confiabilidad"],
                "uso_recomendado": source["uso_recomendado"],
                "limitaciones": source["limitaciones"],
                "requiere_revision_manual": source["requiere_revision_manual"],
            }
        )
    return rows


def phase1_indexes() -> tuple[dict[str, dict[str, str]], dict[str, list[str]]]:
    polos = {row["polo_id"]: row for row in read_csv(OUTPUTS / "polos_gastronomicos_base_candidata.csv")}
    locales: dict[str, list[str]] = defaultdict(list)
    for row in read_csv(OUTPUTS / "locales_destacados_por_polo_seed.csv"):
        nombre = row.get("nombre_local", "").strip()
        if nombre:
            locales[row["polo_id"]].append(nombre)
    return polos, locales


def has_explicit_delim(value: str) -> bool:
    normalized = value.lower()
    negatives = ["no definida", "sin delimitacion", "sin limites", "no tramo", "no hay"]
    return bool(value.strip()) and not any(negative in normalized for negative in negatives)


def build_validation_rows(fuentes_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    phase1, locales = phase1_indexes()
    by_polo: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in fuentes_rows:
        by_polo[row["polo_id"]].append(row)

    validation = []
    for item in PERPLEXITY_ROWS:
        meta = POLO_META[item["polo"]]
        source_rows = by_polo[meta["polo_id"]]
        parent = phase1.get(meta.get("fase1_parent", ""), {})
        counts = Counter(row["confiabilidad"] for row in source_rows)
        tipos = {row["tipo_fuente"] for row in source_rows}
        local_list = locales.get(meta.get("fase1_parent", ""), [])
        pending = any(is_pending_url(row["url"]) for row in source_rows)
        validation.append(
            {
                "polo_id": meta["polo_id"],
                "nombre_polo": item["polo"],
                "tipo_area_fase1": parent.get("tipo_area", "no_aplica_fase1"),
                "tipo_area_revisado": item["tipo"],
                "nivel_consolidacion_fase1": parent.get("nivel_consolidacion", "no_aplica_fase1"),
                "nivel_consolidacion_revisado": item["nivel"],
                "cantidad_fuentes_total": str(len(source_rows)),
                "cantidad_fuentes_alta": str(counts["alta"]),
                "cantidad_fuentes_media": str(counts["media"]),
                "cantidad_fuentes_baja": str(counts["baja"]),
                "cantidad_fuentes_requiere_revision": str(counts["requiere_revision"]),
                "hay_fuente_oficial": yes_no(bool(tipos & {"oficial_gcba", "turismo", "datos_abiertos"})),
                "hay_fuente_periodistica": yes_no("periodistica" in tipos),
                "hay_fuente_datos_abiertos": yes_no("datos_abiertos" in tipos),
                "hay_fuente_turistica": yes_no("turismo" in tipos),
                "hay_fuente_academica": yes_no("academica" in tipos),
                "hay_delimitacion_explicita": yes_no(any(has_explicit_delim(row["delimitacion_mencionada"]) for row in source_rows)),
                "hay_locales_mencionados": yes_no(bool(local_list) or any("no hay" not in row["locales_mencionados"].lower() and "sin listado" not in row["locales_mencionados"].lower() for row in source_rows)),
                "url_pendiente": yes_no(pending),
                "estado_validacion": meta["estado"],
                "decision_para_informe": meta["decision"],
                "observaciones": meta["observacion"],
            }
        )
    return validation


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(column, "")).replace("\n", " ") for column in columns) + " |")
    return "\n".join([header, sep, *body])


def write_seed_doc() -> None:
    lines = [
        "# Fuentes semilla verificadas - PolosGastro",
        "",
        f"Fecha de consulta: {CONSULTA}.",
        "",
        "Estas fuentes se cargan como punto de partida documental. Que una URL abra no implica que valide por si sola un polo gastronomico ni su delimitacion.",
        "",
    ]
    for seed in SEED_SOURCES.values():
        lines.extend(
            [
                f"## {seed['seed_id']} - {seed['titulo']}",
                "",
                f"- Fuente: {seed['nombre_fuente']}",
                f"- Tipo: {seed['tipo_fuente']}",
                f"- URL: {seed['url']}",
                f"- Estado URL: {seed['estado_url']}",
                f"- Uso: {seed['descripcion']}",
                f"- Cautela: uso recomendado `{seed['uso']}`, confiabilidad `{seed['confiabilidad']}`.",
                "",
            ]
        )
    write_text(FUENTES_DOCS / "FUENTES_SEMILLA_VERIFICADAS.md", "\n".join(lines))


def write_pending_searches() -> None:
    lines = [
        "# Busquedas complementarias pendientes - PolosGastro",
        "",
        "Listado de consultas sugeridas para cerrar evidencia debil o ambigua. No todas deben convertirse en fuentes del informe: primero hay que verificar URL, contenido, fecha, pertinencia y sesgo.",
        "",
    ]
    for polo, searches in SEARCHES.items():
        lines.append(f"## {polo}")
        lines.append("")
        for query in searches:
            lines.append(f"- {query}")
        lines.append("")
    write_text(FUENTES_DOCS / "BUSQUEDAS_COMPLEMENTARIAS_PENDIENTES.md", "\n".join(lines))


def write_complementary_doc() -> None:
    lines = [
        "# Fuentes complementarias encontradas - PolosGastro",
        "",
        f"Fecha de consulta: {CONSULTA}.",
        "",
        "La busqueda complementaria priorizo fuentes oficiales/turisticas del GCBA y se cargo con criterio conservador. Estas fuentes mejoran trazabilidad, pero no cierran mapas, censos ni taxonomias finales.",
        "",
    ]
    for source in COMPLEMENTARY_SOURCES:
        lines.extend(
            [
                f"## {source['fuente_id']} - {source['polo']}",
                "",
                f"- Fuente: {source['nombre_fuente']}",
                f"- Referencia: {source['titulo_o_referencia']}",
                f"- URL: {source['url']}",
                f"- Tipo: {source['tipo_fuente']}",
                f"- Confiabilidad: {source['confiabilidad']}",
                f"- Evidencia: {source['evidencia_que_aporta']}",
                f"- Delimitacion mencionada: {source['delimitacion_mencionada']}",
                f"- Limitaciones: {source['limitaciones']}",
                "",
            ]
        )
    write_text(FUENTES_DOCS / "FUENTES_COMPLEMENTARIAS_ENCONTRADAS.md", "\n".join(lines))


def write_reading_doc(validation_rows: list[dict[str, str]], fuentes_rows: list[dict[str, str]]) -> None:
    counts = Counter(row["estado_validacion"] for row in validation_rows)
    principal = [row["nombre_polo"] for row in validation_rows if row["decision_para_informe"] in {"incluir_como_polo_consolidado", "incluir_como_polo_relevante"}]
    anexo = [row["nombre_polo"] for row in validation_rows if row["decision_para_informe"] == "mencionar_en_anexo"]
    no_incluir = [row["nombre_polo"] for row in validation_rows if row["decision_para_informe"] == "no_incluir_aun"]
    complementary_names = sorted({row["nombre_polo"] for row in fuentes_rows if row["fuente_id"].startswith("COMP")})
    lines = [
        "# Lectura de validacion documental - PolosGastro",
        "",
        "Esta lectura no es el informe final. Ordena evidencia documental para decidir que polos pueden avanzar a una futura fase de delimitacion territorial, mapas y redaccion ejecutiva.",
        "",
        "## Fuentes cargadas",
        "",
        f"- Fuentes semilla verificadas: {len(SEED_SOURCES)}.",
        f"- Filas normalizadas desde la matriz Perplexity: {len(PERPLEXITY_ROWS)}.",
        f"- Fuentes externas cargadas por polo: {len(fuentes_rows)} filas.",
        f"- Fuentes complementarias encontradas y cargadas: {len(COMPLEMENTARY_SOURCES)} filas.",
        "",
        "## Polos mejor respaldados",
        "",
        "El nucleo fuerte inicial queda compuesto por Palermo Soho, Palermo Hollywood, Las Canitas, Puerto Madero, San Telmo y Recoleta. Son casos con menciones institucionales/turisticas y una identidad gastronomica reconocible. Chacarita, Retiro, Microcentro/Centro, Monserrat y Barrio Chino quedan en validacion media: tienen respaldo documental, pero requieren redaccion prudente y control de escala.",
        "",
        "## Clasificacion documental",
        "",
        markdown_table(
            [{"estado": key, "cantidad": str(counts.get(key, 0))} for key in ["validado_fuerte", "validado_medio", "candidato_con_evidencia", "requiere_validacion", "ambiguo", "descartar_por_ahora"]],
            ["estado", "cantidad"],
        ),
        "",
        "## Recomendacion preliminar",
        "",
        f"- Informe principal: {', '.join(principal)}.",
        f"- Anexo o lectura secundaria: {', '.join(anexo) if anexo else 'sin casos'}.",
        f"- No incluir todavia: {', '.join(no_incluir) if no_incluir else 'sin casos'}.",
        "",
        "## Corredores candidatos y zonas prudentes",
        "",
        "Avenida Corrientes, Costanera Norte, DoHo / Donado-Holmberg y Paternal mejoran respecto de la matriz semilla porque aparecen fuentes complementarias, pero siguen siendo candidatos. En estos casos conviene hablar de corredor, hito o distrito cuando corresponda, no de polo consolidado.",
        "",
        "## Informacion faltante antes del informe final",
        "",
        "- Delimitacion territorial por polo o subpolo.",
        "- Validacion de URLs pendientes y de menciones sin link de Perplexity.",
        "- Cruce cuantitativo con Buenos Aires Data y, si se habilita en una fase futura, con habilitaciones gastronomicas.",
        "- Reglas para no duplicar barrios, subpolos, avenidas y corredores.",
        "- Control de vigencia de locales destacados, sin convertirlos en padron oficial.",
        "",
        "## Conexion con DataGastro",
        "",
        "PolosGastro queda como subproyecto documental exploratorio. Puede alimentar una futura lectura DataGastro sobre territorialidad gastronomica, pero aun no modifica pipelines, modelos, dashboards ni fuentes de datos generales.",
        "",
        "## Cuidado metodologico",
        "",
        "No se debe mezclar barrio, subpolo, avenida y corredor como si fueran equivalentes. Una fuente turistica puede validar relato e identidad, una fuente de datos abiertos puede medir oferta, una nota periodistica puede orientar concentracion, pero ninguna de esas capas por separado cierra una taxonomia oficial.",
        "",
        "## Fuentes complementarias usadas",
        "",
        f"- {', '.join(complementary_names)}.",
    ]
    write_text(DOCS / "LECTURA_VALIDACION_DOCUMENTAL_POLOS_GASTRO.md", "\n".join(lines))


def write_fichas(validation_rows: list[dict[str, str]], fuentes_rows: list[dict[str, str]]) -> None:
    phase1, locales = phase1_indexes()
    by_polo: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in fuentes_rows:
        by_polo[row["polo_id"]].append(row)
    validation_by_id = {row["polo_id"]: row for row in validation_rows}

    for item in PERPLEXITY_ROWS:
        meta = POLO_META[item["polo"]]
        polo_id = meta["polo_id"]
        validation = validation_by_id[polo_id]
        parent = phase1.get(meta.get("fase1_parent", ""), {})
        local_list = locales.get(meta.get("fase1_parent", ""), [])
        source_rows = by_polo[polo_id]
        verified_links = [row["url"] for row in source_rows if not is_pending_url(row["url"])]
        pending_links = [row["url"] for row in source_rows if is_pending_url(row["url"])]
        searches = SEARCHES.get(item["polo"], SEARCHES.get("Belgrano desagregado" if "Belgrano" in item["polo"] or item["polo"] == "Barrio Chino" else item["polo"], []))
        source_lines = [f"- {row['fuente_id']}: {row['titulo_o_referencia']} ({row['tipo_fuente']}, {row['confiabilidad']}) - {row['url']}" for row in source_rows]
        lines = [
            f"# {item['polo']}",
            "",
            f"## 1. Nombre del polo",
            "",
            item["polo"],
            "",
            "## 2. Tipo de area",
            "",
            item["tipo"],
            "",
            "## 3. Nivel de consolidacion sugerido",
            "",
            f"Perplexity: {item['nivel']}. Validacion documental revisada: {validation['estado_validacion']}.",
            "",
            "## 4. Decision preliminar para informe",
            "",
            validation["decision_para_informe"],
            "",
            "## 5. Descripcion breve",
            "",
            parent.get("descripcion_breve", "Polo agregado en Fase 2 como candidato contextual fuera de la base Fase 1."),
            "",
            "## 6. Evidencia disponible",
            "",
            item["evidencia"],
            "",
            "## 7. Fuentes principales",
            "",
            "\n".join(source_lines[:2]) if source_lines else "- Sin fuentes principales verificables.",
            "",
            "## 8. Fuentes secundarias",
            "",
            "\n".join(source_lines[2:]) if len(source_lines) > 2 else "- Sin fuentes secundarias adicionales.",
            "",
            "## 9. Links verificados",
            "",
            "\n".join(f"- {url}" for url in sorted(set(verified_links))) if verified_links else "- Sin links verificados.",
            "",
            "## 10. URLs pendientes",
            "",
            "\n".join(f"- {url}" for url in pending_links) if pending_links else "- Sin URLs pendientes en las fuentes cargadas.",
            "",
            "## 11. Locales destacados mencionados en Fase 1",
            "",
            "\n".join(f"- {name}" for name in local_list) if local_list else "- Sin locales destacados en Fase 1 para este recorte.",
            "",
            "Nota: los locales destacados provienen del PDF semilla de Fase 1. No constituyen padron, censo ni prueba de vigencia.",
            "",
            "## 12. Delimitacion territorial preliminar si existe",
            "",
            item["delimitacion"],
            "",
            "## 13. Ambiguedades",
            "",
            meta["observacion"],
            "",
            "## 14. Riesgos metodologicos",
            "",
            "- No confundir concentracion de oferta con validacion institucional.",
            "- No convertir fuentes turisticas en delimitaciones oficiales.",
            "- No usar locales destacados como registro de establecimientos.",
            "",
            "## 15. Busquedas complementarias sugeridas",
            "",
            "\n".join(f"- {query}" for query in searches) if searches else "- Sin busquedas especificas predefinidas; revisar fuentes oficiales, periodisticas y barriales.",
            "",
            "## 16. Recomendacion para el informe",
            "",
            f"{validation['decision_para_informe']}. {validation['observaciones']}",
        ]
        filename = FICHAS / f"{polo_id}_{slugify(item['polo'])}.md"
        write_text(filename, "\n".join(lines))


def update_traceability_doc(validation_rows: list[dict[str, str]], fuentes_rows: list[dict[str, str]]) -> None:
    pending_count = len({row["url"] for row in fuentes_rows if is_pending_url(row["url"])})
    section = "\n".join(
        [
            "## Validacion documental Fase 2",
            "",
            f"Fecha de consulta documental: {CONSULTA}.",
            "",
            f"- Fuentes semilla verificadas: {len(SEED_SOURCES)}.",
            f"- Filas normalizadas desde matriz Perplexity: {len(PERPLEXITY_ROWS)}.",
            f"- Filas de fuentes externas por polo: {len(fuentes_rows)}.",
            f"- Fuentes complementarias encontradas: {len(COMPLEMENTARY_SOURCES)}.",
            f"- URLs pendientes unicas: {pending_count}.",
            "",
            "### Criterios de confiabilidad",
            "",
            "- `alta`: fuente oficial/turistica directamente vinculada al polo o fuente semilla central ya verificada.",
            "- `media`: fuente periodistica, datos abiertos o hito turistico que aporta contexto o evidencia parcial.",
            "- `baja`: fuente debil o poco pertinente; no se uso en esta fase.",
            "- `requiere_revision`: mencion sin URL, fuente pendiente o evidencia insuficiente.",
            "",
            "### Criterios de decision",
            "",
            "- `incluir_como_polo_consolidado`: respaldo fuerte y uso posible en cuerpo principal con cautela metodologica.",
            "- `incluir_como_polo_relevante`: respaldo documental suficiente, pero con redaccion prudente.",
            "- `incluir_como_polo_emergente`: evidencia de oferta/identidad, pendiente de delimitacion y medicion.",
            "- `incluir_como_corredor_candidato`: eje o corredor plausible, sin cierre territorial.",
            "- `mencionar_en_anexo`: caso util para contexto o exploracion, no para argumento central.",
            "- `no_incluir_aun`: evidencia insuficiente para una version ejecutiva.",
            "",
            "### Diferencia entre tipos de fuente",
            "",
            "- Oficial/GCBA: aporta marco institucional o datos publicos, pero puede estar orientada a gestion o turismo.",
            "- Turistica: ayuda a identificar relato, identidad y atractivos; no debe usarse sola para cerrar delimitaciones.",
            "- Periodistica: orienta concentracion, evolucion o agenda publica; requiere contraste.",
            "- Datos abiertos: permite medicion futura, no valida por si solo la existencia institucional de un polo.",
            "- Comercial: puede describir oferta privada; usar con cautela por sesgo promocional.",
            "- Academica: no se encontro una fuente academica cargada en esta fase.",
            "",
            "### Limitaciones",
            "",
            "La matriz sigue siendo exploratoria. No se geocodificaron locales, no se genero mapa final, no se modifico pipeline y no se reemplazo la base candidata Fase 1.",
        ]
    )
    upsert_section(DOCS / "FUENTES_Y_TRAZABILIDAD_POLOS_GASTRO.md", "FASE2_VALIDACION_DOCUMENTAL", section)


def update_diagnostic_doc(validation_rows: list[dict[str, str]]) -> None:
    counts = Counter(row["estado_validacion"] for row in validation_rows)
    section = "\n".join(
        [
            "## Validación documental preliminar",
            "",
            "La Fase 2 tomo la respuesta de Perplexity como insumo inicial, no como verdad cerrada, y la cruzo con fuentes semilla verificadas, fuentes complementarias oficiales/turisticas y la base candidata de Fase 1.",
            "",
            f"- Filas Perplexity normalizadas: {len(PERPLEXITY_ROWS)}.",
            f"- Fuentes semilla verificadas: {len(SEED_SOURCES)}.",
            f"- Polos `validado_fuerte`: {counts.get('validado_fuerte', 0)}.",
            f"- Polos `validado_medio`: {counts.get('validado_medio', 0)}.",
            f"- Polos `candidato_con_evidencia`: {counts.get('candidato_con_evidencia', 0)}.",
            f"- Polos `requiere_validacion`: {counts.get('requiere_validacion', 0)}.",
            f"- Polos `ambiguo`: {counts.get('ambiguo', 0)}.",
            f"- Polos `descartar_por_ahora`: {counts.get('descartar_por_ahora', 0)}.",
            "",
            "Principales ambiguedades: varios casos mezclan barrio, subpolo, avenida, corredor, hito gastronomico y distrito tematico. Por eso la clasificacion revisada separa polos consolidados, zonas relevantes, candidatos y casos que requieren validacion.",
            "",
            "Falta validar delimitaciones, vigencia de menciones, densidad territorial y eventuales cruces con datos abiertos antes de un informe final.",
            "",
            "Base candidata, no padrón oficial.",
            "",
            "Los locales destacados no constituyen un censo ni un registro de establecimientos.",
            "",
            "La delimitación territorial requiere validación complementaria.",
            "",
            "La evidencia documental se usa para orientar una lectura exploratoria, no para cerrar una taxonomía oficial.",
        ]
    )
    upsert_section(DOCS / "DIAGNOSTICO_INICIAL_POLOS_GASTRO.md", "FASE2_VALIDACION_DOCUMENTAL", section)


def update_skeleton_doc() -> None:
    section = "\n".join(
        [
            "## Pendientes antes del informe final",
            "",
            "- Validacion de URLs pendientes.",
            "- Busqueda de fuentes complementarias para casos debiles o ambiguos.",
            "- Delimitacion territorial por polo, subpolo, avenida o corredor.",
            "- Mapa conceptual por comunas, barrios y corredores.",
            "- Clasificacion final de polos consolidados, relevantes, emergentes y candidatos.",
            "- Cruce futuro con Buenos Aires Data.",
            "- Posible cruce futuro con habilitaciones gastronomicas si se habilita metodologicamente.",
            "- Posible geocodificacion futura de locales destacados.",
            "- Cuidado metodologico para no convertir fuentes turisticas, datos abiertos o locales destacados en padron oficial.",
        ]
    )
    upsert_section(DOCS / "ESQUELETO_INFORME_POLOS_GASTRO.md", "FASE2_PENDIENTES_INFORME_FINAL", section)


def ensure_perplexity_doc() -> None:
    path = FUENTES_DOCS / "perplexity_fuentes_polos_gastro.md"
    if not path.exists():
        write_text(
            path,
            "\n".join(
                [
                    "# Perplexity - fuentes PolosGastro",
                    "",
                    "PEGAR_AQUI_RESPUESTA_PERPLEXITY",
                    "",
                    "Nota: archivo creado porque no se encontro una respuesta completa existente.",
                ]
            ),
        )


def main() -> None:
    FUENTES_DOCS.mkdir(parents=True, exist_ok=True)
    FICHAS.mkdir(parents=True, exist_ok=True)
    ensure_perplexity_doc()

    perplexity_rows = build_perplexity_rows()
    write_csv(OUTPUTS / "perplexity_matriz_evidencia_seed.csv", perplexity_rows, PERPLEXITY_COLUMNS)

    fuentes_rows = build_fuentes_rows(perplexity_rows)
    write_csv(OUTPUTS / "fuentes_externas_polos_gastro.csv", fuentes_rows, FUENTES_COLUMNS)

    validation_rows = build_validation_rows(fuentes_rows)
    write_csv(OUTPUTS / "matriz_validacion_polos_gastro.csv", validation_rows, VALIDACION_COLUMNS)

    write_seed_doc()
    write_pending_searches()
    write_complementary_doc()
    write_reading_doc(validation_rows, fuentes_rows)
    write_fichas(validation_rows, fuentes_rows)
    update_traceability_doc(validation_rows, fuentes_rows)
    update_diagnostic_doc(validation_rows)
    update_skeleton_doc()

    summary_rows = [
        {"indicador": "filas_perplexity", "valor": str(len(perplexity_rows))},
        {"indicador": "fuentes_semilla", "valor": str(len(SEED_SOURCES))},
        {"indicador": "fuentes_externas_filas", "valor": str(len(fuentes_rows))},
        {"indicador": "fichas_polos", "valor": str(len(PERPLEXITY_ROWS))},
    ]
    write_csv(OUTPUTS / "resumen_validacion_documental_fase2.csv", summary_rows, ["indicador", "valor"])


if __name__ == "__main__":
    main()
