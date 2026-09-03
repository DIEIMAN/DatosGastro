# Arquitectura del nuevo informe de polos con pipeline híbrido

Estado: PROPUESTA EDITORIAL EXPERIMENTAL — **no es el informe final ni autoriza su
redacción**. Fecha: 2026-07-11.
Respeta `REGISTRO_DECISIONES_APROBADAS_DIEGO.md` (DEC-01…DEC-09). Depende de resultados
técnicos pendientes (repeticiones de Belgrano y Puerto Madero, soporte del eje Defensa;
carpetas de Codex) y de decisiones abiertas (DH-01, DH-05, DH-06, DH-10, DH-11).

## 1. Propósito

Presentar la lectura territorial de polos gastronómicos **con la evidencia ampliada del
pipeline híbrido** (universo F01/F02 + señales externas sanitizadas; representaciones por
tipo territorial), como pieza complementaria de la lectura general vigente (DEC-07). Es
el primer informe donde las zonas se muestran con la forma que su territorio pide (núcleo,
corredor, red, frente, señal) en lugar de una única convención gráfica.

## 2. Audiencia y variantes

Se preparan **dos variantes del mismo esqueleto**, que comparten mapas base y difieren en
capas de detalle y anexos:

- **Variante A — ministro/política:** decisores; 12–14 páginas; cero metodología en
  cuerpo; sin cifras de cobertura en láminas (van a nota); lenguaje de la guía.
- **Variante B — interna/técnica:** equipo DGDGAS y revisión; 20–25 páginas; mismas
  láminas + fichas por zona con métricas (cobertura, estabilidad, mezcla de fuentes) +
  anexos completos.

## 3. Relación con Fase 25

Por DEC-07, este informe **complementa** la Fase 25 (o su versión pulida): no la
sustituye ni la contradice. Regla editorial: donde el híbrido y Fase 25 difieren en
representación (p. ej. Puerto Madero banda vs. frente), el informe lo presenta como
"lectura profundizada", nunca como corrección. El mapa principal sigue la decisión DH-10
(pendiente; recomendación vigente: lectura general como mapa principal y estructuras
híbridas como láminas de detalle).

## 4. Estructura tentativa (variante A; B agrega fichas y anexos)

| # | Página | Contenido |
| --- | --- | --- |
| 1 | Portada | Título institucional + subtítulo ("Lectura territorial en profundidad") |
| 2 | Resumen | Hallazgos en positivo: dónde se concentra, qué se consolida, qué se observa |
| 3 | Mapa general | Lectura de conjunto (según DH-10) con jerarquía de madurez (§8) |
| 4 | Cómo leer este informe | Los cinco tipos territoriales explicados en lenguaje llano, con miniaturas |
| 5 | San Telmo — núcleo compacto | Núcleo + (si DH-01 c) eje Defensa contextual |
| 6 | Corrientes — corredor | Corredor único continuo (DEC-01), subtramos como etiquetas narrativas (DEC-02), capa de contexto (DEC-08) |
| 7 | Belgrano — red multinuclear | Núcleos estables de la repetición, sin nombres si DH-05 sigue abierta (códigos visuales neutros) |
| 8 | Puerto Madero — frente | Frente según DH-06 firmada (hipótesis: doble margen de diques) |
| 9 | Palermo (Soho / Hollywood / Cañitas) | Núcleo + red, si el escalado llega a tiempo; si no, lectura editorial rotulada |
| 10 | Zonas en observación | Microcentro, Recoleta, Caballito, Villa Crespo/Chacarita, Caseros/Barracas en un pliego comparativo sobrio |
| 11 | Costanera — lectura exploratoria | Unidad editorial multiparte discontinua (DEC-05/06), espacios explicados por condiciones físicas |
| 12 | Próximos pasos | Profundizaciones previstas, actualización de evidencia |
| 13 | Nota metodológica | Fuentes, tipos de representación, convención de franjas (DEC-09), tratamiento de la oferta dispersa (DEC-08), línea de alcance |
| (14) | Reserva | Página de holgura para una zona adicional madura |

## 5. Mapas

- **Mapa general:** uno, a página completa, con las estructuras maduras y las zonas en
  observación diferenciadas por jerarquía visual (§8). Sin geometrías experimentales no
  firmadas.
- **Mapas por tipo territorial** (uno por lámina de detalle):
  - **Núcleo compacto (San Telmo, Palermo Soho):** contorno de densidad suavizado con
    relleno pleno; sin isolíneas múltiples; etiqueta editorial con nombre.
  - **Corredor (Corrientes):** banda continua sobre el eje vial con franja orientativa
    (nota DEC-09); etiquetas narrativas de subtramos sin cortes geométricos; capa de
    contexto de oferta cercana en símbolo menor.
  - **Red multinuclear (Belgrano, Palermo Hollywood):** núcleos separados con el mismo
    tratamiento visual entre sí (ninguna jerarquía implícita mientras DH-05 esté
    abierta); sin polígono contenedor duro; halo sutil de macroárea.
  - **Frente gastronómico (Puerto Madero):** banda(s) sobre el/los márgenes firmados en
    DH-06, con hitos discretos; sin segmentación norte/centro/sur salvo firma explícita.
  - **Señal exploratoria (Costanera):** componentes discontinuas bajo una sola etiqueta,
    densidad difusa (sin bordes), rótulo "lectura exploratoria" en la propia lámina,
    texto que explica los vacíos por condiciones físicas y geográficas (DEC-05).

## 6. Qué va al cuerpo y qué al anexo

**Cuerpo (ambas variantes):** mapas, lecturas territoriales en lenguaje editorial,
hallazgos, próximos pasos, nota metodológica sobria.

**Anexo (variante B; en A se omite o se reduce a la nota):**

- fichas técnicas por zona: cobertura de la representación, estabilidad, mezcla de
  fuentes, decisiones aplicadas (con IDs DEC/DH);
- taxonomía completa de puntos no asignados con conteos por categoría (DEC-08);
- tabla de convenciones (franjas por tipo, umbrales usados como convención);
- trazabilidad de insumos (hashes, versiones de capas);
- registro de decisiones editoriales aplicadas.

**No aparece en ninguna variante:** nombres de algoritmos en el cuerpo (HDBSCAN, KDE,
KMeans), parámetros (epsilon, bandwidth, umbrales), incidencias técnicas (solapes
corregidos, artefactos de contenedor), nombres de plataformas externas en láminas
(la fuente externa se menciona genéricamente en nota metodológica como "servicios de
localización de terceros bajo convenio de uso permitido", solo en variante B con su
peso por zona).

## 7. Cobertura, no asignados y franjas

- **Cobertura:** regla mínima de DEC-08: ninguna lámina de detalle sin nota de
  cobertura. Formulación variante A (cualitativa): "la estructura representa la mayor
  parte de la oferta relevada en la zona / una parte de la oferta relevada; el resto se
  muestra como contexto". Formulación variante B (cuantitativa): "X % de los puntos del
  universo experimental".
- **Puntos no asignados:** clasificación interna por la taxonomía de seis categorías
  (DEC-08). Comunicación pública: solo dos rótulos visuales — "oferta gastronómica de
  contexto" (categorías 2–3, símbolo menor en el mapa) y silencio gráfico para el resto
  (documentado en anexo B). Nunca la palabra "ruido" en ninguna variante.
- **Franjas (buffers):** siempre con la nota estándar de convención (DEC-09): en A
  cualitativa ("franja orientativa de representación"), en B con anchos numéricos en la
  tabla de convenciones del anexo.

## 8. Jerarquía de madurez (rotulado transversal)

Cuatro estados, definidos una vez en la página "Cómo leer este informe" y aplicados en
cada lámina con un distintivo discreto (color del rótulo o pictograma, no texto largo):

| Estado | Criterio | Zonas esperadas (a hoy) |
| --- | --- | --- |
| **Consolidado** | Representación estable, decisión firmada, fuentes mixtas sanas | Corrientes; San Telmo (post DH-01) |
| **Con observaciones** | Representación estable con condiciones (p. ej. dependencia de fuente externa declarada) | Puerto Madero (post repetición) |
| **Experimental** | Repetición corrida, pendiente de firma o de nombres | Belgrano; Palermo Hollywood |
| **Exploratorio** | Sin medición defendible; solo lectura | Costanera (DEC-05/06); zonas del pliego de observación |

Regla: una zona solo puede subir de estado por decisión firmada registrada en el
REGISTRO; el informe nunca sube estados por su cuenta.

## 9. Dependencias para producción

No se redacta hasta que: (a) Codex entregue las repeticiones (Belgrano, Puerto Madero,
soporte Defensa); (b) se firmen DH-01, DH-06 y DH-10; (c) DH-11 (etiquetado de
deduplicación) tenga al menos la cota rápida de 50 casos; (d) Diego apruebe esta
arquitectura. El orden de producción está en
`PLAN_INTEGRACION_RESULTADOS_CODEX_FABLE.md`.
