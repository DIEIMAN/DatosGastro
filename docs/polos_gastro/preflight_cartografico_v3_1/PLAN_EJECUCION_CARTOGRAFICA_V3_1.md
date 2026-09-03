# Plan de ejecución cartográfica V3.1

**Estado:** LISTO PARA EJECUCIÓN POSTERIOR  
**Ejecución en esta tanda:** NO  
**Entrada documental vigente:** `docs/polos_gastro/evidencia_documental_integrada_v1_1/HANDOFF_DOCUMENTAL_CARTOGRAFO_V1_1.md`.

## Base reutilizada

Este plan complementa, sin reescribir, el inventario de `docs/polos_gastro/preflight_cartografico_v3/` y la matriz de 24 insumos en `outputs/polos_gastro/preflight_cartografico_v3/MATRIZ_INSUMOS_Y_DEPENDENCIAS.csv`.

Validación previa V3.1:

- 24/24 rutas existen y conservan sus SHA-256;
- scripts v1, v2 y v2.1 reutilizables sin modificación in-place;
- universos vigentes: Belgrano 697, Recoleta 767, Costanera Norte 72;
- cálculo métrico en `EPSG:5347`; exportación GeoJSON en `EPSG:4326`/CRS84;
- V1.1 documental agregado como entrada normativa, no como feature espacial;
- baselines y superficies protegidas en solo lectura.

## Gate de inicio de la futura corrida

1. Recibir instrucción explícita de ejecutar.
2. Crear una línea experimental nueva de resultados, distinta de preflight V3/V3.1 y de v2.1.
3. Congelar hashes de los 24 insumos, bundle documental V1.1, Fase 25, Fase 26 y v2.1.
4. Cargar el universo sanitizado; filtrar por `macrozona_id`; separar F01/F02 de la señal externa ya almacenada.
5. No llamar APIs, no descargar datos y no instalar dependencias.

## Secuencia común

1. Reproducir controles de esquema y universos sin escribir sobre baselines.
2. Proyectar a `EPSG:5347` antes de distancias, áreas o buffers.
3. Ejecutar alternativas sin nombres documentales ni cantidades esperadas de clusters como restricciones.
4. Medir cobertura, componentes, huecos, área, estabilidad, sensibilidad al contenedor y composición de fuentes.
5. Generar capas analíticas nuevas.
6. Aplicar decisiones territoriales/editoriales a una capa de presentación separada.
7. Ejecutar correspondencia documental post hoc.
8. Registrar desacuerdos en una copia nueva del esquema de `CONTRADICCIONES_Y_VACIOS_DOCUMENTALES.md`; no modificar la evidencia original.
9. Ejecutar QA geométrico, privacidad, hashes pre/post y Git.

## Belgrano

### Alternativas

- Unidad macro con centralidades internas.
- Red multiparte bajo una identidad única, preservando separaciones reales.
- Superficie continua restringida por soporte y vacíos.
- Agrupación prudente de candidatos sin fijar un número de subzonas por anticipado.

### Ajustes V3.1

- Se confirma que las cuatro referencias documentales son hipótesis post hoc, no cuatro clusters esperados.
- La centralidad Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría se evalúa como una centralidad con nodos.
- Cabildo–Juramento comienza como eje interno descriptivo.
- Bajo Belgrano se contrasta como centralidad diferenciada.
- Belgrano R se contrasta como sector secundario; una eventual promoción queda para decisión humana.
- Se mantiene el control contra fragmentación excesiva y contra hull gigante con área sin soporte.

### Salida esperada

Comparación técnica de alternativas, continuidad entre estructuras y correspondencia post hoc, sin número oficial de polos ni nombres técnicos promovidos automáticamente.

## Recoleta

### Alternativas

- R-A: unidad general con centralidades internas.
- R-B: unidad general con un máximo de dos subzonas.

### Ajustes V3.1

- Junín–Vicente López–entorno del Cementerio y Alvear–Posadas son las referencias principales para el contraste post hoc.
- Callao–9 de Julio y Bellas Artes se evalúan inicialmente como nodos/transiciones.
- La relación hacia Retiro se analiza como corredor o transición, nunca como fusión automática de barrios.
- Los nueve núcleos analíticos v2.1 se conservan como baseline; no se hereda su cantidad en presentación.
- Se mantiene el control de vacíos y superficie incorporada sin soporte.

### Salida esperada

Comparación R-A/R-B con métricas de cobertura, vacíos, robustez, composición de fuentes y recomendación técnica sujeta a decisión humana.

## Costanera Norte

### Cambio obligatorio V3.1

DEC-10 reemplaza el tratamiento exploratorio del plan V3. Costanera Norte debe producirse como un polo adoptado de cuatro componentes discontinuos, apto para cuerpo y cartografía principal. `CN_C02` es componente pleno: no contextual, no anexo, no pendiente de confirmación.

### Proceso previsto

1. Conservar `CN_C01–CN_C04` en la evaluación y en las capas derivadas autorizadas.
2. No usar los nombres documentales ni la cantidad cuatro para supervisar el clustering.
3. Conservar discontinuidades y vacíos; prohibir conectores artificiales.
4. Conciliar el universo técnico 72 = 71 asignados + 1 registro de borde sin alterar v2/v2.1.
5. Crear capa analítica nueva que preserve los cuatro componentes adoptados y sus métricas de fuente.
6. Crear capa de presentación nueva con los cuatro componentes y jerarquía de cartografía principal.
7. Ejecutar la correspondencia documental espacial post hoc.
8. Documentar una vez la dependencia global de Places y la composición de `CN_C02`; no usarla para degradar jerarquía.

### Tabla futura de correspondencia

| componente_geométrico | componente_documental | estado_correspondencia | evidencia | observaciones |
| --- | --- | --- | --- | --- |
| `CN_C01` | pendiente | `EMPAREJADA/PARCIAL/SIN_CORRESPONDENCIA_DIRECTA` | pendiente | |
| `CN_C02` | pendiente | `EMPAREJADA/PARCIAL/SIN_CORRESPONDENCIA_DIRECTA` | pendiente | componente adoptado |
| `CN_C03` | pendiente | `EMPAREJADA/PARCIAL/SIN_CORRESPONDENCIA_DIRECTA` | pendiente | |
| `CN_C04` | pendiente | `EMPAREJADA/PARCIAL/SIN_CORRESPONDENCIA_DIRECTA` | pendiente | |

La falta de correspondencia documental directa no autoriza a eliminar un componente.

### Salida esperada

Capa analítica y capa de presentación separadas, ambas con cuatro componentes discontinuos; correspondencia documental; métricas; nota metodológica; cartografía preparada para el cuerpo principal. Ninguna salida afirmará estatus regulatorio de establecimientos concretos.

## Criterios de cierre de la futura corrida

- 24 insumos y evidencia V1.1 con hashes pre/post intactos.
- Cero cambios en v2.1, Fase 25, Fase 26, fuentes e infraestructura.
- Belgrano sin fragmentación forzada ni hull gigante.
- Recoleta como unidad general, con máximo dos subzonas.
- Costanera Norte con cuatro componentes, incluido `CN_C02`, y vacíos preservados.
- Correspondencia documental post hoc y desacuerdos explícitos.
- Dependencias de fuente y límites metodológicos documentados sin reducir decisiones adoptadas.
- Sin staging, commit ni push salvo autorización posterior.

