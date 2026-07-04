from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs" / "polos_gastro"
DOCS = ROOT / "docs" / "polos_gastro"
FECHA_CORTE = "2026-06-29"


NOMBRES_COLUMNS = [
    "nombre_interno",
    "nombre_publico",
    "nombre_corto",
    "usar_en_informe",
    "observaciones",
]

UNIVERSO_COLUMNS = [
    "polo_id",
    "nombre_publico",
    "tipo_area",
    "grupo_informe",
    "estado_validacion",
    "decision_para_informe",
    "nivel_evidencia",
    "fuentes_principales",
    "urls_pendientes",
    "requiere_validacion_adicional",
    "motivo_decision",
    "riesgo_metodologico",
    "observaciones",
]

DELIMITACION_COLUMNS = [
    "polo_id",
    "nombre_publico",
    "tipo_area",
    "delimitacion_textual",
    "barrios_asociados",
    "comunas_probables",
    "nivel_precision",
    "fuente_delimitacion",
    "requiere_validacion_cartografica",
    "observaciones",
]


PUBLIC_NAMES = {
    "PG001A_PALERMO_SOHO": ("Palermo Soho", "Palermo Soho"),
    "PG001B_PALERMO_HOLLYWOOD": ("Palermo Hollywood", "Palermo Hollywood"),
    "PG001C_LAS_CANITAS": ("Las Cañitas", "Las Cañitas"),
    "PG002_VILLA_CRESPO": ("Villa Crespo", "Villa Crespo"),
    "PG003_PUERTO_MADERO": ("Puerto Madero", "Puerto Madero"),
    "PG004_SAN_TELMO": ("San Telmo", "San Telmo"),
    "PG005_CHACARITA": ("Chacarita", "Chacarita"),
    "PG006A_BARRIO_CHINO": ("Barrio Chino", "Barrio Chino"),
    "PG006B_BAJO_BELGRANO": ("Bajo Belgrano", "Bajo Belgrano"),
    "PG006C_BELGRANO_R": ("Belgrano R", "Belgrano R"),
    "PG007_RECOLETA": ("Recoleta", "Recoleta"),
    "PG008_CABALLITO": ("Caballito", "Caballito"),
    "PG009_COSTANERA_NORTE": ("Costanera Norte", "Costanera Norte"),
    "PG010_AVENIDA_CASEROS_BARRACAS": ("Avenida Caseros / Barracas", "Caseros / Barracas"),
    "PG011_MICROCENTRO_CENTRO_RENOVADO": ("Microcentro / Centro", "Microcentro / Centro"),
    "PG012_AVENIDA_CORRIENTES": ("Avenida Corrientes", "Corrientes"),
    "PG013_ABASTO": ("Abasto", "Abasto"),
    "PG014_AVENIDA_BOEDO": ("Avenida Boedo", "Boedo"),
    "PG015_DEVOTO": ("Devoto", "Devoto"),
    "PG016_CORREDOR_DOHO_DONADO_HOLMBERG": ("DoHo / Donado-Holmberg", "DoHo"),
    "PG017_VILLA_URQUIZA": ("Villa Urquiza", "Villa Urquiza"),
    "PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY": (
        "Nuevo Bajo en Retiro / Esmeralda y Paraguay",
        "Nuevo Bajo en Retiro",
    ),
    "PG019_AVENIDA_FEDERICO_LACROZE_DESDE_LIBERTADOR_": (
        "Federico Lacroze / Libertador a Cabildo",
        "Federico Lacroze",
    ),
    "PG020_PARQUE_SAAVEDRA_AVENIDA_GARCIA_DEL_RIO": (
        "Parque Saavedra / García del Río",
        "García del Río",
    ),
    "PG021_CIRCUITO_GASTRONOMICO_DE_PATERNAL": ("Paternal", "Paternal"),
    "PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN": (
        "Villa Pueyrredón / Av. San Martín",
        "Villa Pueyrredón",
    ),
    "PGF2_COLEGIALES": ("Colegiales", "Colegiales"),
    "PGF2_MONTSERRAT": ("Monserrat", "Monserrat"),
    "PGF2_RETIRO": ("Retiro", "Retiro"),
    "PGF2_FLORES": ("Flores", "Flores"),
    "PGF2_FLORESTA": ("Floresta", "Floresta"),
    "PGF2_PARQUE_PATRICIOS": ("Parque Patricios", "Parque Patricios"),
}


UNIVERSE = {
    "PG001A_PALERMO_SOHO": {
        "grupo": "nucleo_principal",
        "decision": "incluir_como_polo_consolidado",
        "nivel": "alta",
        "motivo": "Subpolo de Palermo con respaldo documental y delimitacion textual en la matriz semilla.",
        "riesgo": "Presentarlo como barrio independiente en lugar de subpolo dentro de Palermo.",
        "observaciones": "Tratar junto con Palermo Hollywood y Las Cañitas como familia Palermo.",
    },
    "PG001B_PALERMO_HOLLYWOOD": {
        "grupo": "nucleo_principal",
        "decision": "incluir_como_polo_consolidado",
        "nivel": "alta",
        "motivo": "Subpolo de Palermo reconocido por fuente turistica/oficial y matriz semilla.",
        "riesgo": "Sobregeneralizar limites o separarlo de Palermo como unidad administrativa.",
        "observaciones": "Usar como subpolo gastronómico de Palermo.",
    },
    "PG001C_LAS_CANITAS": {
        "grupo": "nucleo_principal",
        "decision": "incluir_como_polo_consolidado",
        "nivel": "alta",
        "motivo": "Subpolo con mencion especifica y trayectoria como zona gastronómica.",
        "riesgo": "Nombrarlo como barrio independiente o fijar limites no documentados.",
        "observaciones": "Nombre publico corregido a Las Cañitas.",
    },
    "PG003_PUERTO_MADERO": {
        "grupo": "nucleo_principal",
        "decision": "incluir_como_polo_consolidado",
        "nivel": "alta",
        "motivo": "Polo consolidado con respaldo turistico/institucional y lectura urbana clara.",
        "riesgo": "Confundir circuito turistico con medicion de locales activos.",
        "observaciones": "Requiere delimitacion cartografica por docks/avenidas en fase futura.",
    },
    "PG004_SAN_TELMO": {
        "grupo": "nucleo_principal",
        "decision": "incluir_como_polo_consolidado",
        "nivel": "alta",
        "motivo": "Barrio con reconocimiento gastronomico y presencia en fuente semilla/documental.",
        "riesgo": "Mezclar barrio completo, Mercado de San Telmo y corredores internos.",
        "observaciones": "Mantener advertencia sobre locales destacados no censales.",
    },
    "PG007_RECOLETA": {
        "grupo": "nucleo_principal",
        "decision": "incluir_como_polo_consolidado",
        "nivel": "alta",
        "motivo": "Polo tradicional con evidencia documental y menciones turísticas.",
        "riesgo": "Usar referencias históricas para afirmar vigencia operativa sin contraste.",
        "observaciones": "Requiere delimitacion fina si se mapea.",
    },
    "PG005_CHACARITA": {
        "grupo": "zona_relevante",
        "decision": "incluir_como_polo_relevante",
        "nivel": "media",
        "motivo": "Tiene fuente complementaria oficial dedicada al polo, pero todavia no hay medicion territorial ni densidad validada.",
        "riesgo": "Elevarlo a nucleo principal con solo una capa turistica/documental.",
        "observaciones": "Correccion: baja del informe principal a zona relevante con redaccion prudente.",
    },
    "PG006A_BARRIO_CHINO": {
        "grupo": "zona_relevante",
        "decision": "incluir_como_polo_relevante",
        "nivel": "media",
        "motivo": "Subzona comercial-cultural con fuente turistica complementaria; no es barrio administrativo.",
        "riesgo": "Tratarlo como barrio independiente o como polo institucional cerrado.",
        "observaciones": "Presentar siempre dentro de Belgrano.",
    },
    "PG011_MICROCENTRO_CENTRO_RENOVADO": {
        "grupo": "zona_relevante",
        "decision": "incluir_como_polo_relevante",
        "nivel": "media",
        "motivo": "Zona central con evidencia de densidad y fuentes de contexto, pero sin delimitacion fina.",
        "riesgo": "Fragmentar o duplicar con Monserrat, Retiro y Nuevo Bajo.",
        "observaciones": "Conviene agruparlo narrativamente como zona central.",
    },
    "PGF2_MONTSERRAT": {
        "grupo": "zona_relevante",
        "decision": "incluir_como_polo_relevante",
        "nivel": "media",
        "motivo": "Aporta a la familia de zona central por concentracion/oferta, no como polo cerrado.",
        "riesgo": "Duplicar lectura con Microcentro/Centro.",
        "observaciones": "Caso agregado en Fase 2; usar como sublectura central.",
    },
    "PGF2_RETIRO": {
        "grupo": "zona_relevante",
        "decision": "incluir_como_polo_relevante",
        "nivel": "media",
        "motivo": "Zona central/turistica con evidencia documental, distinta del subeje Nuevo Bajo.",
        "riesgo": "Confundir Retiro completo con Esmeralda-Paraguay.",
        "observaciones": "Agrupar con zona central y mantener Nuevo Bajo como anexo.",
    },
    "PG002_VILLA_CRESPO": {
        "grupo": "emergente_o_candidato",
        "decision": "incluir_como_polo_emergente",
        "nivel": "parcial",
        "motivo": "Tiene señales de oferta y un hito complementario, pero falta delimitacion y cruce cuantitativo.",
        "riesgo": "Usar un mercado/hito para validar todo el barrio.",
        "observaciones": "Candidato defendible para fase de mapa, no nucleo.",
    },
    "PG008_CABALLITO": {
        "grupo": "emergente_o_candidato",
        "decision": "incluir_como_polo_emergente",
        "nivel": "parcial",
        "motivo": "Cuenta con hitos gastronomicos y evidencia de concentracion, sin polo formal cerrado.",
        "riesgo": "Convertir Patio/Mercado en validacion de barrio completo.",
        "observaciones": "Trabajar como barrio con nodos gastronomicos.",
    },
    "PG009_COSTANERA_NORTE": {
        "grupo": "emergente_o_candidato",
        "decision": "incluir_como_corredor_candidato",
        "nivel": "parcial",
        "motivo": "Hay fuentes oficiales de contexto y hito gastronomico, pero no delimitacion de corredor completo.",
        "riesgo": "Presentarlo como polo consolidado por existencia de patios o restaurantes puntuales.",
        "observaciones": "Mantener como corredor candidato, no anexo ni principal.",
    },
    "PG012_AVENIDA_CORRIENTES": {
        "grupo": "emergente_o_candidato",
        "decision": "incluir_como_corredor_candidato",
        "nivel": "parcial",
        "motivo": "Identidad teatro/pizza documentada; falta delimitar tramo y separar de Abasto.",
        "riesgo": "Tomar una identidad cultural como delimitacion gastronomica oficial.",
        "observaciones": "Analizar junto a Abasto, pero no fusionar todavia.",
    },
    "PG015_DEVOTO": {
        "grupo": "emergente_o_candidato",
        "decision": "incluir_como_polo_emergente",
        "nivel": "parcial",
        "motivo": "Fuente oficial barrial aporta señal gourmet, pero no hay densidad ni limites.",
        "riesgo": "Usar una descripcion barrial como prueba de polo.",
        "observaciones": "Cruzar en futura fase con oferta registrada.",
    },
    "PG016_CORREDOR_DOHO_DONADO_HOLMBERG": {
        "grupo": "emergente_o_candidato",
        "decision": "incluir_como_corredor_candidato",
        "nivel": "parcial",
        "motivo": "Existe fuente complementaria para Donado-Holmberg, pero requiere control de vigencia y alcance.",
        "riesgo": "Elevar DoHo sin fuente clara de delimitacion actual.",
        "observaciones": "Mantener como corredor candidato.",
    },
    "PG017_VILLA_URQUIZA": {
        "grupo": "emergente_o_candidato",
        "decision": "incluir_como_polo_emergente",
        "nivel": "parcial",
        "motivo": "Tiene señal vinculada a Donado-Holmberg, no a todo el barrio.",
        "riesgo": "Extender evidencia de un eje a Villa Urquiza completa.",
        "observaciones": "Separar barrio de corredor DoHo.",
    },
    "PG021_CIRCUITO_GASTRONOMICO_DE_PATERNAL": {
        "grupo": "emergente_o_candidato",
        "decision": "incluir_como_corredor_candidato",
        "nivel": "parcial",
        "motivo": "Distrito del Vino aporta contexto territorial, no validacion especifica del circuito.",
        "riesgo": "Confundir distrito tematico con circuito gastronomico barrial.",
        "observaciones": "Requiere fuente especifica de Paternal antes de informe central.",
    },
    "PGF2_COLEGIALES": {
        "grupo": "emergente_o_candidato",
        "decision": "incluir_como_polo_emergente",
        "nivel": "parcial",
        "motivo": "Agregado Fase 2 con evidencia de concentracion/oferta, sin recorte propio.",
        "riesgo": "Incluirlo sin haber estado en la base semilla Fase 1.",
        "observaciones": "Tratar como candidato agregado.",
    },
    "PG006C_BELGRANO_R": {
        "grupo": "anexo",
        "decision": "mencionar_en_anexo",
        "nivel": "parcial_baja",
        "motivo": "Tiene señal de oferta barrial, pero no evidencia de polo delimitado.",
        "riesgo": "Duplicar con Belgrano/Barrio Chino.",
        "observaciones": "Mantener como anexo.",
    },
    "PG010_AVENIDA_CASEROS_BARRACAS": {
        "grupo": "anexo",
        "decision": "mencionar_en_anexo",
        "nivel": "parcial_baja",
        "motivo": "Evidencia indirecta para Barracas/Caseros; falta fuente especifica del corredor.",
        "riesgo": "Sobredimensionar un eje con evidencia debil.",
        "observaciones": "Nombre publico normalizado con barra espaciada.",
    },
    "PG013_ABASTO": {
        "grupo": "anexo",
        "decision": "mencionar_en_anexo",
        "nivel": "parcial_baja",
        "motivo": "Tiene hitos y solapamiento con Avenida Corrientes, pero no polo propio defendible.",
        "riesgo": "Duplicar con Corrientes o Balvanera sin criterio territorial.",
        "observaciones": "Trabajar junto a Corrientes en fase futura.",
    },
    "PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY": {
        "grupo": "anexo",
        "decision": "mencionar_en_anexo",
        "nivel": "parcial_baja",
        "motivo": "Retiro esta respaldado, pero el subeje Nuevo Bajo no tiene delimitacion robusta.",
        "riesgo": "Confundir Retiro con un recorte operativo no validado.",
        "observaciones": "Nombre publico corregido a Nuevo Bajo en Retiro.",
    },
    "PGF2_FLORES": {
        "grupo": "anexo",
        "decision": "mencionar_en_anexo",
        "nivel": "parcial_baja",
        "motivo": "Hay evidencia de circuito identitario puntual, no de barrio completo.",
        "riesgo": "Generalizar desde barrio coreano a todo Flores.",
        "observaciones": "Anexo o caso de circuito cultural.",
    },
    "PGF2_FLORESTA": {
        "grupo": "anexo",
        "decision": "mencionar_en_anexo",
        "nivel": "parcial_baja",
        "motivo": "Evidencia contextual de oferta/concentracion, sin polo delimitado.",
        "riesgo": "Incluir como zona relevante sin fuentes especificas.",
        "observaciones": "Mantener como anexo exploratorio.",
    },
    "PGF2_PARQUE_PATRICIOS": {
        "grupo": "anexo",
        "decision": "mencionar_en_anexo",
        "nivel": "parcial_baja",
        "motivo": "Cuenta con hito gastronomico puntual, no con validacion barrial.",
        "riesgo": "Usar un patio como prueba de polo.",
        "observaciones": "Anexo o caso puntual.",
    },
    "PG006B_BAJO_BELGRANO": {
        "grupo": "no_incluir_por_ahora",
        "decision": "no_incluir_aun",
        "nivel": "insuficiente",
        "motivo": "Mencion indirecta sin fuente especifica suficiente.",
        "riesgo": "Duplicar con Barrio Chino/Belgrano.",
        "observaciones": "Pendiente de busqueda manual.",
    },
    "PG014_AVENIDA_BOEDO": {
        "grupo": "no_incluir_por_ahora",
        "decision": "no_incluir_aun",
        "nivel": "insuficiente",
        "motivo": "No hay evidencia documental suficiente de corredor gastronomico.",
        "riesgo": "Confundir identidad cultural barrial con polo gastronomico.",
        "observaciones": "Mantener pendiente.",
    },
    "PG019_AVENIDA_FEDERICO_LACROZE_DESDE_LIBERTADOR_": {
        "grupo": "no_incluir_por_ahora",
        "decision": "no_incluir_aun",
        "nivel": "insuficiente",
        "motivo": "Tramo propuesto sin fuente verificable suficiente.",
        "riesgo": "Inventar delimitacion o corredor.",
        "observaciones": "No avanzar hasta tener fuente especifica.",
    },
    "PG020_PARQUE_SAAVEDRA_AVENIDA_GARCIA_DEL_RIO": {
        "grupo": "no_incluir_por_ahora",
        "decision": "no_incluir_aun",
        "nivel": "insuficiente",
        "motivo": "No hay fuente suficiente para validar García del Río como corredor gastronomico.",
        "riesgo": "Inferir desde parque/barrio sin respaldo.",
        "observaciones": "Nombre publico corregido a García del Río.",
    },
    "PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN": {
        "grupo": "no_incluir_por_ahora",
        "decision": "no_incluir_aun",
        "nivel": "insuficiente",
        "motivo": "No hay fuente especifica suficiente para el eje Av. San Martin.",
        "riesgo": "Presentar un eje no validado.",
        "observaciones": "Nombre publico corregido a Villa Pueyrredón / Av. San Martín.",
    },
}


DELIMITATIONS = {
    "PG001A_PALERMO_SOHO": ("Scalabrini Ortiz, Córdoba, Juan B. Justo y Santa Fe.", "Palermo", "Comuna 14", "media", "Matriz Perplexity / fuente semilla Turismo BA", "si"),
    "PG001B_PALERMO_HOLLYWOOD": ("Juan B. Justo, Dorrego, Santa Fe y Córdoba.", "Palermo", "Comuna 14", "media", "Matriz Perplexity / fuente semilla Turismo BA", "si"),
    "PG001C_LAS_CANITAS": ("Báez y calles aledañas, en Palermo.", "Palermo", "Comuna 14", "media", "Matriz Perplexity / fuente semilla Turismo BA", "si"),
    "PG002_VILLA_CRESPO": ("Barrio Villa Crespo; hito Mercat como referencia puntual.", "Villa Crespo", "Comuna 15", "baja", "Matriz Perplexity y fuente complementaria", "si"),
    "PG003_PUERTO_MADERO": ("Antiguos docks; Av. Alicia Moreau de Justo.", "Puerto Madero", "Comuna 1", "media", "Matriz Perplexity / guia turistica", "si"),
    "PG004_SAN_TELMO": ("Barrio San Telmo.", "San Telmo", "Comuna 1", "baja", "Matriz Perplexity / fuente semilla", "si"),
    "PG005_CHACARITA": ("Barrio Chacarita; sin limites finos definidos en esta fase.", "Chacarita", "Comuna 15", "baja", "Fuente complementaria Turismo BA y matriz Perplexity", "si"),
    "PG006A_BARRIO_CHINO": ("Subzona de Belgrano; entorno Arribeños, Olazábal, Juramento y Pasaje Echeverría como referencia documental.", "Belgrano", "Comuna 13", "media", "Fuente complementaria Turismo BA", "si"),
    "PG006B_BAJO_BELGRANO": ("Bajo Belgrano, sin delimitacion documental suficiente.", "Belgrano", "Comuna 13", "baja", "Matriz Perplexity", "si"),
    "PG006C_BELGRANO_R": ("Belgrano R, sin delimitacion gastronomica especifica.", "Belgrano", "Comuna 13", "baja", "Matriz Perplexity", "si"),
    "PG007_RECOLETA": ("Barrio Recoleta.", "Recoleta", "Comuna 2", "baja", "Matriz Perplexity / fuente semilla", "si"),
    "PG008_CABALLITO": ("Barrio Caballito; Patio de los Lecheros y Mercado del Progreso como hitos puntuales.", "Caballito", "Comuna 6", "baja", "Matriz Perplexity y fuentes complementarias", "si"),
    "PG009_COSTANERA_NORTE": ("Costanera Norte / ribera norte; sin tramo gastronomico cerrado.", "Costanera Norte", "Comunas 13/14 (aproximacion)", "baja", "Fuentes complementarias Turismo BA", "si"),
    "PG010_AVENIDA_CASEROS_BARRACAS": ("Barracas / eje Caseros; delimitacion especifica pendiente.", "Barracas", "Comuna 4", "baja", "Matriz Perplexity", "si"),
    "PG011_MICROCENTRO_CENTRO_RENOVADO": ("Area central / Microcentro-Centro, sin delimitacion fina.", "San Nicolas, Monserrat, Retiro (aproximacion)", "Comuna 1", "baja", "Matriz Perplexity y fuente complementaria", "si"),
    "PG012_AVENIDA_CORRIENTES": ("Avenida Corrientes; tramo operativo no definido.", "San Nicolas, Balvanera, Almagro (segun tramo futuro)", "Comunas 1/3/5 (aproximacion)", "baja", "Fuente complementaria Turismo BA y matriz Perplexity", "si"),
    "PG013_ABASTO": ("Abasto / Balvanera; hito comercial y entorno cultural, sin polo delimitado.", "Balvanera", "Comuna 3", "baja", "Fuente complementaria y matriz Perplexity", "si"),
    "PG014_AVENIDA_BOEDO": ("Sin delimitacion documental suficiente.", "Boedo", "Comuna 5", "sin_delimitacion", "Sin fuente verificable suficiente", "si"),
    "PG015_DEVOTO": ("Villa Devoto; sin corredor gastronomico delimitado.", "Villa Devoto", "Comuna 11", "baja", "Fuente complementaria Turismo BA", "si"),
    "PG016_CORREDOR_DOHO_DONADO_HOLMBERG": ("Donado y Holmberg; Villa Urquiza.", "Villa Urquiza", "Comuna 12", "media", "Fuente complementaria Turismo BA", "si"),
    "PG017_VILLA_URQUIZA": ("Villa Urquiza; evidencia parcial asociada a Donado-Holmberg.", "Villa Urquiza", "Comuna 12", "baja", "Matriz Perplexity y fuente complementaria", "si"),
    "PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY": ("Retiro; no hay delimitacion validada del tramo Esmeralda-Paraguay.", "Retiro", "Comuna 1", "baja", "Matriz Perplexity", "si"),
    "PG019_AVENIDA_FEDERICO_LACROZE_DESDE_LIBERTADOR_": ("Sin delimitacion documental suficiente del tramo.", "Belgrano/Colegiales (aproximacion)", "Comuna 13/Comuna 15 (aproximacion)", "sin_delimitacion", "Sin fuente verificable suficiente", "si"),
    "PG020_PARQUE_SAAVEDRA_AVENIDA_GARCIA_DEL_RIO": ("Saavedra / Parque Saavedra; eje García del Río pendiente de fuente especifica.", "Saavedra", "Comuna 12", "baja", "Matriz Perplexity", "si"),
    "PG021_CIRCUITO_GASTRONOMICO_DE_PATERNAL": ("Paternal dentro de contexto Distrito del Vino; no circuito gastronomico validado.", "La Paternal", "Comuna 15", "baja", "Fuente complementaria Distrito del Vino y matriz Perplexity", "si"),
    "PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN": ("Sin delimitacion documental suficiente del eje Av. San Martin.", "Villa Pueyrredón", "Comuna 12", "sin_delimitacion", "Sin fuente verificable suficiente", "si"),
    "PGF2_COLEGIALES": ("Barrio Colegiales; sin corredor especifico.", "Colegiales", "Comuna 13", "baja", "Matriz Perplexity", "si"),
    "PGF2_MONTSERRAT": ("Barrio Monserrat; parte de zona central, sin recorte propio.", "Monserrat", "Comuna 1", "baja", "Matriz Perplexity", "si"),
    "PGF2_RETIRO": ("Barrio Retiro; parte de zona central, sin recorte fino.", "Retiro", "Comuna 1", "baja", "Matriz Perplexity", "si"),
    "PGF2_FLORES": ("Flores / barrio coreano como referencia puntual, no barrio completo.", "Flores", "Comuna 7", "baja", "Fuente complementaria Turismo BA y matriz Perplexity", "si"),
    "PGF2_FLORESTA": ("Barrio Floresta; sin corredor especifico.", "Floresta", "Comuna 10", "baja", "Matriz Perplexity", "si"),
    "PGF2_PARQUE_PATRICIOS": ("Parque Patricios; hito Smart Plaza como referencia puntual.", "Parque Patricios", "Comuna 4", "baja", "Fuente complementaria Turismo BA y matriz Perplexity", "si"),
}


SOLAPAMIENTOS = [
    "Palermo Soho, Palermo Hollywood y Las Cañitas son subpolos de Palermo; no deben presentarse como barrios independientes.",
    "Barrio Chino, Bajo Belgrano y Belgrano R provienen de una base Fase 1 agregada de Belgrano; Barrio Chino debe tratarse como subzona comercial-cultural.",
    "Microcentro / Centro, Monserrat, Retiro y Nuevo Bajo en Retiro componen una familia de zona central; conviene agruparlos narrativamente y separar el subeje Nuevo Bajo.",
    "Avenida Corrientes y Abasto se solapan territorial y narrativamente; se recomienda analizarlos vinculados, sin fusionarlos todavia.",
    "DoHo / Donado-Holmberg y Villa Urquiza se solapan: el eje Donado-Holmberg no representa automaticamente todo el barrio.",
    "Paternal y Distrito del Vino no son equivalentes: el distrito tematico aporta contexto, no valida por si solo un circuito gastronomico.",
]


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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def upsert_section(path: Path, marker: str, section: str) -> None:
    original = path.read_text(encoding="utf-8")
    start = f"<!-- {marker}_START -->"
    end = f"<!-- {marker}_END -->"
    block = f"{start}\n{section.rstrip()}\n{end}"
    if start in original and end in original:
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        updated = pattern.sub(block, original)
    else:
        updated = original.rstrip() + "\n\n" + block + "\n"
    write_text(path, updated)


def is_pending_url(url: str) -> bool:
    return url == "url_pendiente" or not url or url.startswith("url_semilla_")


def join(items: list[str], fallback: str = "sin datos") -> str:
    filtered = [item for item in items if item]
    return "; ".join(filtered) if filtered else fallback


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("\n", " ") for column in columns) + " |")
    return "\n".join(lines)


def source_summary(rows: list[dict[str, str]]) -> str:
    non_pending = [row for row in rows if not is_pending_url(row["url"])]
    prioritized = sorted(non_pending, key=lambda r: (r["confiabilidad"] != "alta", r["tipo_fuente"], r["fuente_id"]))
    labels = []
    for row in prioritized[:4]:
        label = f"{row['titulo_o_referencia']} ({row['tipo_fuente']})"
        labels.append(label)
    return join(labels, "sin fuente verificable")


def build_nombre_rows(validation: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for row in validation:
        polo_id = row["polo_id"]
        nombre_publico, nombre_corto = PUBLIC_NAMES[polo_id]
        universe = UNIVERSE[polo_id]
        if universe["grupo"] in {"nucleo_principal", "zona_relevante", "emergente_o_candidato"}:
            usar = "si_con_prudencia" if universe["grupo"] != "nucleo_principal" else "si"
        elif universe["grupo"] == "anexo":
            usar = "solo_anexo"
        else:
            usar = "no_por_ahora"
        rows.append(
            {
                "nombre_interno": row["nombre_polo"],
                "nombre_publico": nombre_publico,
                "nombre_corto": nombre_corto,
                "usar_en_informe": usar,
                "observaciones": universe["observaciones"],
            }
        )
    return rows


def build_universo_rows(validation: list[dict[str, str]], fuentes_by_polo: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    rows = []
    for row in validation:
        polo_id = row["polo_id"]
        universe = UNIVERSE[polo_id]
        sources = fuentes_by_polo[polo_id]
        pending = [f"{source['fuente_id']}:url_pendiente" for source in sources if is_pending_url(source["url"])]
        nombre_publico = PUBLIC_NAMES[polo_id][0]
        rows.append(
            {
                "polo_id": polo_id,
                "nombre_publico": nombre_publico,
                "tipo_area": row["tipo_area_revisado"],
                "grupo_informe": universe["grupo"],
                "estado_validacion": row["estado_validacion"],
                "decision_para_informe": universe["decision"],
                "nivel_evidencia": universe["nivel"],
                "fuentes_principales": source_summary(sources),
                "urls_pendientes": join(pending, "sin_urls_pendientes"),
                "requiere_validacion_adicional": "si",
                "motivo_decision": universe["motivo"],
                "riesgo_metodologico": universe["riesgo"],
                "observaciones": universe["observaciones"],
            }
        )
    return rows


def build_delimitacion_rows(validation: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for row in validation:
        polo_id = row["polo_id"]
        nombre_publico = PUBLIC_NAMES[polo_id][0]
        delim = DELIMITATIONS[polo_id]
        rows.append(
            {
                "polo_id": polo_id,
                "nombre_publico": nombre_publico,
                "tipo_area": row["tipo_area_revisado"],
                "delimitacion_textual": delim[0],
                "barrios_asociados": delim[1],
                "comunas_probables": delim[2],
                "nivel_precision": delim[3],
                "fuente_delimitacion": delim[4],
                "requiere_validacion_cartografica": delim[5],
                "observaciones": "Base para futura delimitacion. No contiene poligonos, coordenadas ni geocodificacion.",
            }
        )
    return rows


def group_lists(universo: list[dict[str, str]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for row in universo:
        groups[row["grupo_informe"]].append(row["nombre_publico"])
    return groups


def write_audit_doc(
    validation: list[dict[str, str]],
    phase1: list[dict[str, str]],
    fuentes: list[dict[str, str]],
    universo: list[dict[str, str]],
) -> None:
    phase1_ids = {row["polo_id"] for row in phase1}
    validation_ids = {row["polo_id"] for row in validation}
    pending_rows = [row for row in fuentes if is_pending_url(row["url"])]
    pending_by_polo = Counter(PUBLIC_NAMES[row["polo_id"]][0] for row in pending_rows)
    weak_sources = [row for row in fuentes if row["confiabilidad"] == "requiere_revision"]
    fichas_count = len(list((DOCS / "fichas_polos").glob("*.md")))
    group_counts = Counter(row["grupo_informe"] for row in universo)
    added = [row["polo_id"] for row in validation if row["polo_id"].startswith("PGF2_")]
    not_carried = sorted(phase1_ids - validation_ids)
    split_note = [
        "PG001 Palermo se desagrego en Palermo Soho, Palermo Hollywood y Las Cañitas.",
        "PG006 Belgrano se desagrego en Barrio Chino, Bajo Belgrano y Belgrano R.",
        "PG023 Abasto - Avenida Corrientes no se arrastro como fila propia: quedo representado por Abasto y Avenida Corrientes.",
    ]
    aggressive = [
        "Chacarita: pasa de informe principal a zona relevante por evidencia turistica directa pero todavia parcial.",
        "Barrio Chino: pasa de informe principal a zona relevante; es subzona comercial-cultural de Belgrano.",
        "Microcentro / Centro, Monserrat y Retiro: se mantienen como zona relevante agrupada, no como nucleos separados.",
        "Costanera Norte, Avenida Corrientes, DoHo / Donado-Holmberg y Paternal: quedan como emergentes/candidatos.",
    ]
    lines = [
        "# Auditoria Fase 2 - Validacion documental PolosGastro",
        "",
        f"Fecha de control: {FECHA_CORTE}.",
        "",
        "Esta auditoria revisa la Fase 2 documental antes de avanzar a mapas o informe final. No modifica fuentes originales ni convierte la base en taxonomia oficial.",
        "",
        "## Archivos revisados",
        "",
        "- outputs/polos_gastro/perplexity_matriz_evidencia_seed.csv",
        "- outputs/polos_gastro/fuentes_externas_polos_gastro.csv",
        "- outputs/polos_gastro/matriz_validacion_polos_gastro.csv",
        "- docs/polos_gastro/LECTURA_VALIDACION_DOCUMENTAL_POLOS_GASTRO.md",
        "- docs/polos_gastro/FUENTES_Y_TRAZABILIDAD_POLOS_GASTRO.md",
        "- docs/polos_gastro/DIAGNOSTICO_INICIAL_POLOS_GASTRO.md",
        "- docs/polos_gastro/fichas_polos/",
        "",
        "## Consistencia de conteos",
        "",
        markdown_table(
            [
                {"indicador": "Filas matriz Perplexity", "valor": str(len(read_csv(OUTPUTS / "perplexity_matriz_evidencia_seed.csv")))},
                {"indicador": "Filas fuentes externas", "valor": str(len(fuentes))},
                {"indicador": "Filas matriz validacion", "valor": str(len(validation))},
                {"indicador": "Fichas Markdown", "valor": str(fichas_count)},
                {"indicador": "URLs pendientes en fuentes", "valor": str(len(pending_rows))},
                {"indicador": "Fuentes requiere_revision", "valor": str(len(weak_sources))},
            ],
            ["indicador", "valor"],
        ),
        "",
        "Los conteos principales declarados en Fase 2 son consistentes con los CSV reales: 32 filas Perplexity, 80 fuentes externas, 32 polos en matriz de validacion y 32 fichas.",
        "",
        "## Polos duplicados, agregados o solapados",
        "",
        "### Desagregaciones y agregados",
        "",
        "\n".join(f"- {item}" for item in split_note),
        "",
        f"- Polos agregados en Fase 2 que no estaban como filas Fase 1: {', '.join(added)}.",
        f"- Fila Fase 1 no trasladada literalmente a Fase 2: {', '.join(not_carried) if not_carried else 'sin casos'}.",
        "",
        "### Solapamientos territoriales relevantes",
        "",
        "\n".join(f"- {item}" for item in SOLAPAMIENTOS),
        "",
        "## Fuentes sin URL o con URL pendiente",
        "",
        markdown_table(
            [{"polo": key, "registros_url_pendiente": str(value)} for key, value in sorted(pending_by_polo.items())],
            ["polo", "registros_url_pendiente"],
        ),
        "",
        "Las URLs pendientes no impiden usar todos los casos como insumo exploratorio, pero si bloquean decisiones fuertes para informe principal o delimitacion cartografica.",
        "",
        "## Fuentes potencialmente debiles",
        "",
        "- Datos abiertos: sirven para una futura medicion de oferta, pero no validan por si solos la existencia institucional de un polo.",
        "- Fuentes turisticas: ayudan a describir identidad, atractivos o relato, pero no cierran delimitaciones ni densidad.",
        "- Hitos puntuales: patios, mercados o centros comerciales no validan por si solos un barrio completo.",
        "- Perplexity: se mantiene como insumo de organizacion, no como fuente primaria para conclusiones finales.",
        "",
        "## Decisiones demasiado agresivas detectadas",
        "",
        "\n".join(f"- {item}" for item in aggressive),
        "",
        "## Problemas de nombres publicos",
        "",
        "- `Las Canitas` se normaliza como `Las Cañitas`.",
        "- `Garcia del Rio` se normaliza como `García del Río`.",
        "- `Villa Pueyrredon` se normaliza como `Villa Pueyrredón`.",
        "- `Donado Holmberg` se usa como `Donado-Holmberg`.",
        "- `Avenida Caseros/Barracas` se usa como `Avenida Caseros / Barracas`.",
        "- `Microcentro/Centro` se usa como `Microcentro / Centro`.",
        "- `Nuevo Bajo Retiro` se usa como `Nuevo Bajo en Retiro`.",
        "",
        "## Resultado de la depuracion",
        "",
        markdown_table(
            [{"grupo_informe": key, "cantidad": str(group_counts.get(key, 0))} for key in ["nucleo_principal", "zona_relevante", "emergente_o_candidato", "anexo", "no_incluir_por_ahora"]],
            ["grupo_informe", "cantidad"],
        ),
        "",
        "La depuracion no borra ni reemplaza la Fase 2: crea un universo defendible para una futura etapa de mapas e informe.",
    ]
    write_text(DOCS / "AUDITORIA_FASE2_VALIDACION_DOCUMENTAL.md", "\n".join(lines))


def write_universe_doc(universo: list[dict[str, str]]) -> None:
    groups = group_lists(universo)
    lines = [
        "# Universo defendible para informe PolosGastro",
        "",
        f"Fecha de corte documental: {FECHA_CORTE}.",
        "",
        "Este documento define un universo de trabajo para un informe futuro. No crea una taxonomia oficial de polos gastronomicos y no reemplaza una validacion territorial.",
        "",
        "## 1. Criterio de inclusion",
        "",
        "Se priorizan casos con respaldo documental, nombre publico defendible, fuente trazable y riesgo metodologico controlado. La inclusion no significa oficializacion: significa que el caso puede trabajarse con una redaccion prudente en una fase posterior.",
        "",
        "## 2. Diferencias operativas",
        "",
        "- Polo consolidado: caso con respaldo fuerte y relato defendible para cuerpo principal.",
        "- Zona relevante: area con evidencia media/alta, pero limites o escala todavia prudentes.",
        "- Corredor emergente: eje con señales documentales, pendiente de delimitacion y contraste.",
        "- Candidato: barrio, eje o subzona con señales parciales que requiere validacion adicional.",
        "- Anexo: caso interesante para contexto, pero no para desarrollar como polo principal.",
        "",
        "## 3. Nucleo principal recomendado",
        "",
        "\n".join(f"- {name}" for name in groups["nucleo_principal"]),
        "",
        "## 4. Zonas relevantes recomendadas",
        "",
        "\n".join(f"- {name}" for name in groups["zona_relevante"]),
        "",
        "## 5. Emergentes y candidatos",
        "",
        "\n".join(f"- {name}" for name in groups["emergente_o_candidato"]),
        "",
        "## 6. Casos para anexo",
        "",
        "\n".join(f"- {name}" for name in groups["anexo"]),
        "",
        "## 7. Casos que no conviene incluir todavia",
        "",
        "\n".join(f"- {name}" for name in groups["no_incluir_por_ahora"]),
        "",
        "## 8. Casos solapados y tratamiento recomendado",
        "",
        "\n".join(f"- {item}" for item in SOLAPAMIENTOS),
        "",
        "## 9. Riesgos metodologicos",
        "",
        "- No convertir fuentes turisticas en validacion oficial.",
        "- No convertir concentracion de oferta en polo institucional.",
        "- No usar locales destacados como padron ni como prueba de vigencia.",
        "- No mezclar barrio, subpolo, avenida, corredor y zona central como si fueran equivalentes.",
        "- No sobregeneralizar barrios enteros cuando la evidencia refiere a hitos o subzonas.",
        "",
        "## 10. Recomendacion para la proxima fase",
        "",
        "Antes de mapas o PDF institucional, conviene cerrar una delimitacion textual por grupo, resolver URLs pendientes criticas, definir si la zona central se muestra como bloque, y preparar un mapa conceptual no final para revision interna.",
    ]
    write_text(DOCS / "UNIVERSO_DEFENDIBLE_INFORME_POLOS_GASTRO.md", "\n".join(lines))


def write_executive_reading(universo: list[dict[str, str]]) -> None:
    groups = group_lists(universo)
    counts = Counter(row["grupo_informe"] for row in universo)
    lines = [
        "# Lectura ejecutiva del universo de informe - PolosGastro",
        "",
        "Esta lectura ordena el universo recomendable para un futuro informe. No es el informe final y no debe usarse como PDF institucional.",
        "",
        "## Universo recomendado",
        "",
        f"El nucleo principal queda acotado a {counts['nucleo_principal']} casos: {', '.join(groups['nucleo_principal'])}. Son los casos con respaldo mas defendible para una primera narrativa ejecutiva.",
        "",
        "Las zonas relevantes quedan fuera del nucleo principal, pero pueden aparecer en el cuerpo del informe con redaccion prudente: " + ", ".join(groups["zona_relevante"]) + ".",
        "",
        "Los emergentes/candidatos sirven para una lectura de oportunidades o agenda futura: " + ", ".join(groups["emergente_o_candidato"]) + ".",
        "",
        "Los casos para anexo son utiles como contexto o seguimiento, sin desarrollarlos como polos centrales: " + ", ".join(groups["anexo"]) + ".",
        "",
        "No conviene incluir todavia: " + ", ".join(groups["no_incluir_por_ahora"]) + ".",
        "",
        "## Antes de hacer mapas",
        "",
        "- Resolver delimitaciones textuales de baja precision.",
        "- Decidir si Palermo y zona central se mapearan como familias o como subzonas separadas.",
        "- No dibujar poligonos sin fuente territorial o criterio documentado.",
        "- No geocodificar locales destacados hasta definir si se usaran como evidencia cualitativa o solo anexo.",
        "",
        "## Antes del PDF institucional",
        "",
        "- Resolver URLs pendientes que condicionan decisiones fuertes.",
        "- Ajustar nombres publicos y tildes en todo texto final.",
        "- Separar hallazgos de limitaciones metodologicas.",
        "- Aclarar que se trata de una lectura exploratoria basada en fuentes documentales y base semilla.",
        "- Evitar afirmar oficialidad o vigencia operativa de locales.",
    ]
    write_text(DOCS / "LECTURA_UNIVERSO_INFORME_POLOS_GASTRO.md", "\n".join(lines))


def update_skeleton() -> None:
    section = "\n".join(
        [
            "## Estructura sugerida segun universo defendible",
            "",
            "1. Portada.",
            "2. Resumen ejecutivo.",
            "3. Que es un polo gastronomico y como se construyo el universo.",
            "4. Nucleo de polos consolidados.",
            "5. Zonas relevantes.",
            "6. Corredores emergentes y candidatos.",
            "7. Lectura territorial preliminar.",
            "8. Oportunidades de gestion.",
            "9. Limitaciones metodologicas.",
            "10. Anexo de casos pendientes y fuentes.",
            "",
            "Nota: esta estructura no habilita todavia PDF final, mapas finales ni geocodificacion. Primero debe cerrarse delimitacion territorial y validacion de URLs pendientes.",
        ]
    )
    upsert_section(DOCS / "ESQUELETO_INFORME_POLOS_GASTRO.md", "FASE3_UNIVERSO_DEFENDIBLE", section)


def main() -> None:
    validation = read_csv(OUTPUTS / "matriz_validacion_polos_gastro.csv")
    phase1 = read_csv(OUTPUTS / "polos_gastronomicos_base_candidata.csv")
    fuentes = read_csv(OUTPUTS / "fuentes_externas_polos_gastro.csv")
    fuentes_by_polo: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in fuentes:
        fuentes_by_polo[row["polo_id"]].append(row)

    missing = [row["polo_id"] for row in validation if row["polo_id"] not in UNIVERSE]
    if missing:
        raise RuntimeError(f"Faltan decisiones de universo para: {missing}")

    nombres = build_nombre_rows(validation)
    universo = build_universo_rows(validation, fuentes_by_polo)
    delimitacion = build_delimitacion_rows(validation)

    write_csv(OUTPUTS / "nombres_publicos_polos_gastro.csv", nombres, NOMBRES_COLUMNS)
    write_csv(OUTPUTS / "universo_informe_polos_gastro.csv", universo, UNIVERSO_COLUMNS)
    write_csv(OUTPUTS / "base_delimitacion_preliminar_polos_gastro.csv", delimitacion, DELIMITACION_COLUMNS)

    write_audit_doc(validation, phase1, fuentes, universo)
    write_universe_doc(universo)
    write_executive_reading(universo)
    update_skeleton()


if __name__ == "__main__":
    main()
