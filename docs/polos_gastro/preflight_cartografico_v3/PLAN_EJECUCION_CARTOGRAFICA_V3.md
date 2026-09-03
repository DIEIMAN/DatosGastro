# Plan de ejecución cartográfica V3

**Estado:** DISEÑADO, NO EJECUTADO  
**Marca:** EXPERIMENTAL / NO OFICIAL  
**Gate documental:** cumplido durante la sesión; compatibilidad evaluada.  
**Gate de ejecución:** bloqueado hasta instrucción posterior explícita.

## Condiciones de arranque de la futura corrida

1. Usar las dos copias idénticas de `HANDOFF_DOCUMENTAL_CARTOGRAFO_V1.md` como el mismo entregable final del `investigador_documental`.
2. Conservar la evaluación de compatibilidad y sus observaciones antes de cualquier diseño ejecutable.
3. Informar contradicciones sin corregirlas en silencio.
4. Recibir una instrucción posterior explícita para ejecutar; este requisito sigue pendiente.
5. Crear una línea de resultados nueva; nunca escribir dentro de v2.1, Fase 25, Fase 26 ni cartografías v2–v4.2.
6. Congelar hashes de universo, capas analíticas y superficies protegidas antes de cualquier cálculo.

## Evaluación de compatibilidad documental prevista

El handoff permite preparar una matriz `afirmación_documental ↔ sector ↔ fuente ↔ fecha ↔ confianza ↔ componente_técnico ↔ compatibilidad`. En la futura corrida se controlará:

- que la evidencia sea documental y no se presente como delimitación;
- que los nombres coincidan con decisiones humanas o queden como etiquetas de trabajo;
- que no haya afirmaciones sobre actividad, habilitación, formalidad o informalidad;
- que la relación Recoleta–Retiro quede como diagnóstico no supervisado: el handoff respalda Callao–9 de Julio y Bellas Artes como referencias/transiciones, pero no aporta una instrucción específica para absorber Retiro;
- que `CN_C01–CN_C04`, en especial `CN_C02`, puedan vincularse con evidencia sin rellenar discontinuidades;
- que cualquier contradicción con DEC-12 o DEC-13 quede escalada a decisión humana.

## Secuencia técnica común posterior

1. Validar hashes y esquemas de entradas.
2. Cargar el universo sanitizado y filtrar exclusivamente por `macrozona_id`.
3. Separar F01/F02 de la señal externa ya almacenada; no sumarlas como universos equivalentes sin mostrar composición.
4. Proyectar a `EPSG:5347` para distancias y áreas.
5. Reproducir primero métricas existentes sin escribir sobre baselines.
6. Construir alternativas en una carpeta nueva, con capa analítica separada de presentación.
7. Medir cobertura, componentes, vacíos, área, dependencia de fuente, sensibilidad al contenedor y estabilidad.
8. Vincular evidencia documental solo post hoc.
9. Exportar, si se autoriza, GeoJSON en `EPSG:4326` y mapas rotulados EXPERIMENTAL / NO OFICIAL.
10. Ejecutar QA geométrico, privacidad, hashes pre/post y Git; dejar handoff cartográfico para revisión humana independiente.

## Belgrano

### Pregunta de diseño

Representar una unidad macro del Polo Belgrano con centralidades internas, evitando tanto convertir cada núcleo técnico en una unidad autónoma como construir una envolvente gigante que rellene vacíos o abarque áreas sin soporte.

### Alternativas a comparar

- **B-A — Unidad macro + centralidades:** un contenedor de comunicación general y centralidades internas derivadas de soporte estable, sin límites internos rígidos.
- **B-B — Red multiparte conectada conceptualmente:** componentes separados que pertenecen a una misma lectura territorial, con continuidad evaluada por proximidad y soporte, sin bandas artificiales.
- **B-C — Superficie continua restringida:** representación de densidad/continuidad recortada por soporte y vacíos, con penalización explícita a área no respaldada.
- **B-D — Máximo de subzonas prudentes:** agrupación de candidatos solo si continuidad, composición y evidencia documental convergen; el número no se fija por anticipado.

### Ejes de lectura a contrastar post handoff

- Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría.
- Cabildo–Juramento.
- Bajo Belgrano.
- Belgrano R.

Estos nombres no ingresarán al algoritmo ni se convertirán automáticamente en nombres de núcleos. Se usarán para correspondencia post hoc, pendiente de revisión humana conforme DEC-12.

### Controles y métricas

- Retención de los 17 candidatos y de la shortlist v2.1 como referencias, no como resultado predeterminado.
- Cobertura del universo de 697 registros y composición 304 F01/F02 + 393 señales externas.
- Supervivencia por bloques 150/200/300/400 m, respaldo KDE, Jaccard sin señal externa y distancia al borde.
- Cantidad de componentes, distancia entre ellos, vacíos preservados y porcentaje de área del contenedor cubierto.
- Penalización de fragmentación excesiva y de superficie sin soporte.
- Comparación con barrio oficial Belgrano completo como contraste de contenedor.

### Gate humano

No publicar cantidad de polos, nombres de núcleos ni jerarquías. La futura salida será una comparación técnica para decisión, no una delimitación.

## Recoleta

### Pregunta de diseño

Reducir la fragmentación de nueve núcleos técnicos y comunicar una unidad general de Recoleta, comparando una solución única con centralidades frente a una solución de máximo dos subzonas.

### Alternativas a comparar

- **R-A — Unidad única con centralidades:** una identidad general con gradientes o marcadores internos no delimitantes.
- **R-B — Unidad general con máximo dos subzonas:** solo si la separación está respaldada simultáneamente por vacíos, estabilidad, composición y evidencia documental.

### Reglas

- Los nueve núcleos analíticos permanecen intactos como baseline.
- Los cinco candidatos de presentación v2.1 son referencia, no obligación.
- Ninguna alternativa puede crear más de dos subzonas de presentación.
- Control explícito de vacíos: no disolver a través de parques, infraestructuras o sectores sin soporte sin dejarlo visible.
- Evaluar la relación con Retiro sin absorberlo ni renombrarlo automáticamente.
- Tratar Callao–9 de Julio como transición inicial a verificar, no como frontera aprobada.

### Controles y métricas

- Cobertura sobre 767 registros; composición 404 F01/F02 + 363 señales externas.
- Robustez media, p10, sensibilidad al contenedor y ablación de fuentes.
- Área, compacidad, huecos, número de componentes y pérdida/ganancia de cobertura respecto de los nueve núcleos.
- Continuidad entre núcleos y proporción de superficie sin soporte incorporada por cada alternativa.
- Compatibilidad documental de la transición hacia Retiro y del eje Callao–9 de Julio.

### Gate humano

La elección entre R-A y R-B y cualquier nombre de subzona requieren decisión explícita. El resultado no se promueve automáticamente a mapa principal.

## Costanera Norte

### Pregunta de diseño

Preservar una identidad única multiparte y discontinua, evaluar los cuatro componentes técnicos y vincularlos posteriormente con evidencia documental sin transformar la señal exploratoria en una delimitación firme.

### Tratamiento de componentes

- `CN_C01`, `CN_C03` y `CN_C04`: componentes principales vigentes de la presentación v2.1.
- `CN_C02`: inclusión obligatoria en la evaluación, en la representación comparativa y en la matriz de correspondencia documental. La conciliación de precedencia es: cuatro componentes visibles/evaluados, con `CN_C02` conservado como contexto secundario conforme DEC-13; no se fuerza como resultado del cálculo ni se lo convierte en principal sin decisión humana.
- Registro no asignado 72/71: conservar su clasificación v2.1 como dependencia del contenedor; no incorporarlo automáticamente a una geometría.

### Reglas

- No construir hull único, conectores ni buffers que rellenen espacios entre componentes.
- Preservar discontinuidades físicas y geográficas.
- Comparar geometrías con evidencia documental solo post hoc.
- Mantener la lectura exploratoria y la alta dependencia de señal externa visible.
- No afirmar ni sugerir informalidad, falta de habilitación, actividad actual o irregularidad.
- No asignar nombres propios a los componentes sin decisión humana.

### Controles y métricas

- Conciliación exacta del universo 72 = 71 asignados + 1 no asignado localizado.
- Cobertura y composición por `CN_C01–CN_C04`.
- Distancias entre componentes y preservación de vacíos.
- Correspondencia documental con niveles `compatible`, `parcial`, `sin evidencia` o `contradictoria`.
- Sensibilidad a fuente y contenedor; ninguna mejora visual puede ocultar la dependencia externa.

### Gate humano

La ubicación editorial de `CN_C02` y cualquier cambio en su jerarquía siguen pendientes de decisión. Costanera Norte permanece exploratoria.

## Criterio de cierre de la futura corrida

Una futura corrida solo podrá declararse lista para revisión si entrega capas nuevas en línea paralela, hashes pre/post sin cambios en protegidos, parámetros completos, comparación de alternativas, limitaciones, matriz de correspondencia documental y QA independiente. No se autoproclamará oficial.
