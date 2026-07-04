# Diagnóstico inicial PolosGastro

## Qué contiene el PDF

El PDF contiene un listado inicial de zonas, barrios, avenidas, corredores y subpolos gastronómicos de CABA. También incluye secciones de locales destacados para algunos polos. En esta Fase 1 se extrajeron 23 polos o agrupaciones candidatas y 100 menciones de locales destacados.

## Qué tipo de fuente es

Por ahora debe tratarse como una fuente documental semilla. No se verificó origen oficial, fecha de elaboración, metodología, universo ni criterio de selección de locales. Por lo tanto:

- Base candidata, no padrón oficial.
- El listado de locales destacados requiere validación.
- La existencia de un local destacado no prueba por sí sola la delimitación de un polo.
- La delimitación territorial de cada polo debe validarse con fuentes complementarias.

## Qué permite hacer

- Construir un primer inventario de zonas candidatas.
- Identificar casos que el documento presenta con mayor desarrollo interno.
- Separar tipos de área: barrio, corredor, avenida, subpolo, zona costera y zona central.
- Preparar una agenda de validación territorial y documental.

## Qué NO permite afirmar

- No permite afirmar que los polos sean oficiales.
- No permite afirmar que los locales mencionados sigan abiertos o funcionen actualmente.
- No permite afirmar direcciones, coordenadas ni comunas definitivas.
- No permite medir densidad, volumen de oferta ni actividad económica.
- No permite integrar la fuente al pipeline general sin ficha, contrato y aprobación.

## Polos con mayor evidencia interna en el PDF

Estos casos tienen sección propia o listado de locales destacados dentro del PDF:

- Abasto - Avenida Corrientes
- Avenida Caseros (Barracas)
- Belgrano (Barrio Chino + Bajo Belgrano + Belgrano R)
- Caballito
- Chacarita
- Costanera Norte
- Microcentro / Centro Renovado
- Palermo (Soho, Hollywood y Las Cañitas)
- Puerto Madero
- Recoleta
- San Telmo
- Villa Crespo

## Candidatos, corredores o zonas sin detalle de locales

Estos casos aparecen en el listado inicial, pero no tienen sección de locales destacados en el PDF:

- Avenida Corrientes
- Abasto
- Avenida Boedo
- Devoto
- Corredor DoHo / Donado-Holmberg
- Villa Urquiza
- Nuevo Bajo en Retiro (Esmeralda y Paraguay)
- Avenida Federico Lacroze desde Libertador hasta Cabildo
- Parque Saavedra / Avenida García del Río
- Circuito gastronómico de Paternal
- Villa Pueyrredón / Avenida San Martín

## Diferencias conceptuales para normalización

| Tipo | Criterio de uso en Fase 1 | Riesgo si se fuerza |
| --- | --- | --- |
| Barrio | Unidad territorial reconocible por nombre barrial. | Confundir barrio completo con concentración gastronómica real. |
| Corredor | Eje o circuito que conecta tramos o zonas. | Usarlo como polígono sin límites definidos. |
| Avenida | Tramo lineal asociado a oferta gastronómica. | No definir altura inicial/final o incluir zonas heterogéneas. |
| Subpolo | Zona menor dentro de un barrio o polo amplio. | Duplicar conteos con el polo principal. |
| Zona turística/gastronómica | Área de referencia urbana o turística. | Tomarla como delimitación administrativa oficial. |

## Ambigüedades detectadas

- Avenida Corrientes y Abasto aparecen separados en el listado inicial, pero la sección de locales los agrupa como Abasto - Av. Corrientes.
- Belgrano R aparece en el listado inicial, aunque la sección detallada solo desarrolla Barrio Chino y Bajo Belgrano.
- Palermo se presenta como polo amplio y Las Cañitas aparece como subpolo interno.
- La línea 'Incipientes Devoto' sugiere condición emergente, pero no define alcance ni evidencia complementaria.
- Varios casos son corredores o avenidas sin polígono: DoHo, Federico Lacroze, Avenida Boedo, Avenida Caseros y Avenida San Martín.
- Nuevo Bajo en Retiro se define por el entorno Esmeralda-Paraguay, no por un límite territorial formal.
- Costanera Norte no permite inferir comuna única sin una delimitación geográfica previa.

## Recomendación para próximas fases

La próxima fase debería validar la naturaleza del PDF, construir una ficha de fuente y contrastar cada polo con cartografía oficial, notas institucionales y capas públicas ya existentes. Recién después conviene definir delimitaciones operativas, criterios de consolidación y posibles cruces con DataGastro general.

<!-- FASE2_VALIDACION_DOCUMENTAL_START -->
## Validación documental preliminar

La Fase 2 tomo la respuesta de Perplexity como insumo inicial, no como verdad cerrada, y la cruzo con fuentes semilla verificadas, fuentes complementarias oficiales/turisticas y la base candidata de Fase 1.

- Filas Perplexity normalizadas: 32.
- Fuentes semilla verificadas: 8.
- Polos `validado_fuerte`: 6.
- Polos `validado_medio`: 5.
- Polos `candidato_con_evidencia`: 14.
- Polos `requiere_validacion`: 7.
- Polos `ambiguo`: 0.
- Polos `descartar_por_ahora`: 0.

Principales ambiguedades: varios casos mezclan barrio, subpolo, avenida, corredor, hito gastronomico y distrito tematico. Por eso la clasificacion revisada separa polos consolidados, zonas relevantes, candidatos y casos que requieren validacion.

Falta validar delimitaciones, vigencia de menciones, densidad territorial y eventuales cruces con datos abiertos antes de un informe final.

Base candidata, no padrón oficial.

Los locales destacados no constituyen un censo ni un registro de establecimientos.

La delimitación territorial requiere validación complementaria.

La evidencia documental se usa para orientar una lectura exploratoria, no para cerrar una taxonomía oficial.
<!-- FASE2_VALIDACION_DOCUMENTAL_END -->
