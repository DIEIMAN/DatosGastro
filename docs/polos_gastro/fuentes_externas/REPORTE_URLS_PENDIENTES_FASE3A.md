# Reporte de URLs pendientes - Fase 3A

Fecha de consulta: 2026-06-29.

La revision se limito a fuentes abiertas y verificables, priorizando Turismo Buenos Aires, BA Data y fuentes periodisticas ya identificadas. No se uso scraping ni APIs privadas.

## URLs pendientes al inicio

- Registros `url_pendiente` iniciales: 20.
- Polos afectados al inicio: 14.

## URLs resueltas

| fuente_id | polo | url | estado | nota |
| --- | --- | --- | --- | --- |
| PX007B | Chacarita | https://turismo.buenosaires.gob.ar/es/ba-todos-bolsillos/con-quien-quieras | resuelta_con_fuente_parcial | Resuelve una referencia gastronomica puntual; no delimita todo Chacarita como polo institucional. |
| PX009B | Bajo Belgrano | https://turismo.buenosaires.gob.ar/es/turismo-en-barrios/barrio-belgrano-circuito-2 | resuelta_con_fuente_parcial | No convierte Bajo Belgrano en polo independiente ni da poligono. |
| PX010B | Belgrano R | https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa | resuelta_con_fuente_parcial | Apoya un borde/circuito, no valida Belgrano R como polo gastronomico completo. |
| PX013A | Costanera Norte | https://turismo.buenosaires.gob.ar/es/otros-establecimientos/costanera-norte | resuelta_con_fuente_parcial | Describe corredor y oferta, pero no cierra un poligono gastronomico. |
| PX013B | Costanera Norte | https://turismo.buenosaires.gob.ar/es/otros-establecimientos/costanera-norte | resuelta_con_fuente_parcial | No debe usarse para afirmar limites gastronomicos finos. |
| PX016A | Avenida Corrientes | https://turismo.buenosaires.gob.ar/es/ba-todos-bolsillos/con-quien-quieras | resuelta_con_fuente_parcial | Valida identidad cultural-gastronomica puntual, no todo el corredor. |
| PX016B | Avenida Corrientes | https://turismo.buenosaires.gob.ar/en/atractivo/800pm-night-theatre-and-pizza | resuelta_con_fuente_parcial | No reemplaza una delimitacion cartografica del corredor. |
| PX017B | Abasto | https://turismo.buenosaires.gob.ar/es/otros-establecimientos/abasto-shopping | resuelta_con_fuente_parcial | Centro comercial; no valida el barrio como polo cerrado. |
| PX018A | Avenida Boedo | https://turismo.buenosaires.gob.ar/es/atractivo/20-h-avenida-boedo | resuelta_con_fuente_parcial | Apoya identidad cultural y bares puntuales, no valida corredor gastronomico. |
| PX018B | Avenida Boedo | https://turismo.buenosaires.gob.ar/es/recorrido/la-ruta-del-fileteado-porte%C3%B1o | resuelta_con_fuente_parcial | Fuente cultural; no sostiene por si sola un polo gastronomico. |
| PX019B | Devoto | https://turismo.buenosaires.gob.ar/es/turismo-en-barrios/barrio-villa-devoto | resuelta_con_fuente_parcial | No delimita un corredor ni cuantifica oferta. |
| PX020A | DoHo / Donado-Holmberg | https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa | resuelta_con_fuente_parcial | Requiere control de vigencia y no representa todo Villa Urquiza. |
| PX020B | DoHo / Donado-Holmberg | https://turismo.buenosaires.gob.ar/es/article/circuito-sin-pausa | resuelta_con_fuente_parcial | No valida por si sola todo el barrio ni su densidad actual. |
| PX021B | Villa Urquiza | https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa | resuelta_con_fuente_parcial | No cubre todo Villa Urquiza como barrio. |
| PX025B | Paternal | https://turismo.buenosaires.gob.ar/sites/turismo/files/plan-desarrollo-gestion-estrategica-oferta-turistica-2023.pdf | resuelta_con_fuente_parcial | No valida un circuito gastronomico especifico de Paternal. |
| PX026B | Villa Pueyrredon / Av. San Martin | https://turismo.buenosaires.gob.ar/es/otros-establecimientos/la-nueva-andaluza | resuelta_con_fuente_parcial | No valida Villa Pueyrredon / Av. San Martin como polo o corredor. |

## URLs que siguen pendientes

| fuente_id | polo | motivo |
| --- | --- | --- |
| PX023A | Federico Lacroze / Libertador a Cabildo | No se encontro URL verificable que respalde el tramo Federico Lacroze / Libertador a Cabildo como corredor gastronomico. |
| PX023B | Federico Lacroze / Libertador a Cabildo | No se encontro segunda fuente verificable para el tramo Federico Lacroze / Libertador a Cabildo. |
| PX024B | Parque Saavedra / Garcia del Rio | No se encontro URL verificable que respalde Parque Saavedra / Garcia del Rio como corredor gastronomico. |
| PX025A | Paternal | No se encontro URL verificable especifica para un circuito gastronomico de Paternal; solo fuentes de contexto de Distrito del Vino/C15. |

## Fuentes descartadas o no usadas

- Resultados que solo mencionaban atractivos generales, buscadores o locales sueltos no se usaron para cerrar delimitaciones.
- Fuentes con menciones de un hito puntual se cargaron como evidencia parcial, no como validacion de polo.
- No se uso ningun resultado de plataformas privadas ni listados comerciales no institucionales.

## Impacto sobre el universo del informe

No se modifico la clasificacion del universo. Las URLs resueltas reducen incertidumbre documental, pero no elevan casos debiles a nucleo principal.

| polo | grupo | impacto |
| --- | --- | --- |
| Federico Lacroze / Libertador a Cabildo | no_incluir_por_ahora | refuerza decision de no incluir por ahora |
| Federico Lacroze / Libertador a Cabildo | no_incluir_por_ahora | refuerza decision de no incluir por ahora |
| Parque Saavedra / García del Río | no_incluir_por_ahora | refuerza decision de no incluir por ahora |
| Paternal | emergente_o_candidato | bloquea delimitacion fuerte o inclusion central |
