# Anexo - Horarios documentados de mercados gastronómicos CABA

## Metodología

Los horarios se presentan como información documental de referencia. Pueden variar por temporada, operador, sede o actualización de canales públicos, por lo que requieren validación antes de su uso operativo o comunicación al público.

La tabla consolida únicamente información ya presente en archivos sanitizados del proyecto, especialmente `horarios_mercados_gastronomicos_v3.csv`, `mercados_gastronomicos_activos_v4.csv` y fichas documentales V1/V1.2. No se hicieron requests, no se usaron API keys y no se inventaron horarios.

Los itinerantes se mantienen sin horario fijo único: su funcionamiento depende de sede, fecha y programación.

## Tabla de horarios documentados

| Mercado | Sede | Frecuencia de apertura | Horario documentado | Observación | Nivel de confianza | Fuente de respaldo |
| --- | --- | --- | --- | --- | --- | --- |
| Mercado de San Telmo | sede fija | Lunes a domingo | 9 a 22 (a confirmar) | Fuentes documentales divergentes; no usar como horario operativo definitivo. | parcial_fuentes_divergentes | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; GCBA/Turismo BA/sitio propio |
| Mercado de Belgrano | sede fija | Lunes a domingo | frescos 8:30-20; gastronomía 11-24 | Diferencia entre rubro de frescos y oferta gastronómica. | alto_documental | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2 |
| Mercado San Nicolás | sede fija | Lunes a sábado | mercado 8-18; gastronomía 11-24 | Permite lectura de almuerzo laboral y franja post-laboral. | alto_documental | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; respaldo documental multifuente |
| Mercado del Progreso | sede fija | Lunes a sábado | Lun-Vie 7:30-13 y 17-20; Sáb hasta 14 y 17-20 | Horario documental con posible divergencia entre fuentes; validar antes de publicar. | alto_documental_con_divergencia_a_validar | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; sitio propio |
| Mercat Villa Crespo | sede fija | Martes a domingo | 12 a 23 (Vie-Sáb hasta 01) | Útil para lectura de almuerzo, tarde-noche y salida corta. | alto_documental | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; Turismo BA |
| Gourmand Food Hall | sede fija | Todos los días | Dom-Jue 10-23; Vie-Sáb 10-1 | Horario documental de food hall; validar vigencia antes de comunicar. | alto_documental | horarios_mercados_gastronomicos_v3.csv; sitio propio y validación documental multifuente |
| Patio de los Lecheros | sede fija | Todos los días | 9 a 24 (Vie-Sáb hasta 3) | Operación extendida; gastronomía documentada desde las 13 en fichas previas. | alto_documental | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; GCBA |
| Smart Plaza Parque Patricios | sede fija | Todos los días | 11 a 24 (Vie-Sáb hasta 1) | Permite lectura de almuerzo, tarde y salida post-laboral. | alto_documental | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; GCBA |
| Patio Costanera Norte | sede fija | Miércoles a domingo | Mié 12-19; Jue-Sáb 12-24; Dom 12-21 | Horario incorporado como documental; validar antes de programación operativa. | alto_documental | horarios_mercados_gastronomicos_v3.csv; ficha V1.2 sanitizada |
| Patio Gastronómico Rodrigo Bueno | sede fija | Viernes a domingo | 11 a 23 | Horario de fin de semana; validar por operador antes de publicar. | alto_documental | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; GCBA |
| Mercado Bonpland | sede fija | Martes, miércoles, viernes y sábado | 10 a 19/20 | Mercado de productores y economía social; días específicos. | alto_documental | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; Turismo BA |
| Sabe la Tierra | itinerante | Fines de semana | depende de sede/programación; sin horario fijo único consolidado | No asignar horario fijo único; requiere calendario de edición y sede. | por_sede_no_consolidado | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; sitio propio |
| Buenos Aires Market | itinerante | Fines de semana | depende de sede/programación; sin horario fijo único consolidado | No asignar horario fijo único; requiere calendario de edición y sede. | por_sede_no_consolidado | horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; sitio propio |

## Recomendación de uso

Usar esta capa como referencia interna para orientar programación, priorización de validaciones y comunicación institucional. Antes de publicar horarios al público o programar acciones operativas, corresponde validarlos con el operador, la sede vigente o el canal oficial actualizado.
