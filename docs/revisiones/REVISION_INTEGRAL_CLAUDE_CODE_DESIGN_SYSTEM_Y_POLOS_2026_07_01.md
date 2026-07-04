# Revisión integral Claude Code — Design System y PolosGastro

Fecha de revisión: 2026-07-01.
Autor de la revisión: Claude Code (auditoría de solo lectura, sin aplicar cambios).
Alcance: revisión del trabajo dejado por Codex en dos líneas — Design System DGDGAS
(export de Claude Design + mapeo experimental) y PolosGastro (Fase 7 / Borrador 2,
Fase 8 liviana y Fase 8 fuerte / capa objetiva).

Esta revisión **no aplica cambios**. No modifica tokens canónicos, scripts productivos,
Borrador 2, datos fuente ni informes. No genera PDF, DOCX, mapas ni dashboards.

---

## 1. Resumen ejecutivo

- **Estado del Design System.** El trabajo de importación, comparación y mapeo está
  **bien hecho y es prudente**. El JSON experimental es válido, se autodeclara
  `do_not_use_as_canonical: true` y no toca los tokens canónicos. El mapeo distingue
  correctamente qué adoptar, qué adaptar y qué dejar para después. **No está listo para
  volverse canónico**, pero sí para ser validado. Falta una preview visual controlada
  antes de tocar `style_tokens_dgdgas.py` o los tokens canónicos.

- **Estado de PolosGastro.** Las tres fases son metodológicamente consistentes y
  conservadoras. Fase 7 / Borrador 2 es un checkpoint interno coherente. Fase 8 liviana
  dejó recomendaciones razonables, todas marcadas `Aplicar ahora = NO`. Fase 8 fuerte
  agrega una capa objetiva **bien tratada como contexto y no como ranking**: el cruce
  `polos_vs_capa_objetiva` incluye la columna de decisión `usar_en_borrador_3_si_no`,
  marca los corredores como "no calculable" y **deja vacío** el cuadrante peligroso
  (evidencia débil/pendiente con señal objetiva alta). QA de privacidad: 0 alertas.

- **¿Listos para aplicar diseño?** **No todavía.** Ninguna de las dos líneas requiere
  aplicar diseño ahora. El Design System necesita una preview mínima antes de canonizar;
  PolosGastro necesita revisión humana de las recomendaciones antes de Borrador 3. Aplicar
  el Design System a informes de PolosGastro en este momento sería prematuro y acumularía
  dos riesgos no resueltos a la vez.

- **Próximo paso recomendado.** Validación humana del mapeo de tokens (Etapa 1, sin tocar
  canónicos) y, en paralelo, revisión humana del cruce `polos_vs_capa_objetiva` para
  decidir qué entra al Borrador 3. La aplicación de diseño queda para después de ambas.

---

## 2. Revisión del Design System

### Diagnóstico general

Codex ejecutó un ciclo completo y ordenado: importó el export de Claude Design a
`claude_design_export_v1/` como insumo auditable, produjo una revisión comparativa
(`REVISION_EXPORT_CLAUDE_DESIGN_V1.md`), un mapeo token por token
(`MAPEO_TOKENS_CLAUDE_DESIGN_A_BASE_LOCAL.md`), un JSON experimental mapeado, un CSV de
diff legible y una propuesta de ampliación de componentes, todo cerrado con un plan de
actualización por etapas. El criterio transversal es correcto: **adoptar el criterio
visual/metodológico del export mediante un mapeo controlado, no por reemplazo directo.**

### Estado de tokens

- El JSON experimental `design_tokens_dgdgas_claude_design_mapped_v1.json` **es válido**
  (carga sin error) y **conserva la estructura local** (`color.*` como strings HEX,
  `typography.scale.*`, `box.*`, `content_states.*`), guardando lo nuevo del export bajo
  `experimental_claude_design.*`. Esto es exactamente lo que corresponde para no romper el
  consumidor actual.
- **Es usable como insumo de evaluación, no como canónico.** Se autodeclara
  `do_not_use_as_canonical: true`. Además, `style_tokens_dgdgas.py` tiene hardcodeada la
  ruta a `design_tokens_dgdgas.json`, así que el experimental no entra al pipeline por
  accidente. Bien.
- **Conviene adoptar (coincidencias / mejoras claras):** marca (`#1F3B57`, `#2C7FB8`,
  `#C0762B`), página A4 / márgenes, `shadow.print = none` como regla de QA, el vocabulario
  de estados metodológicos (`en_espera`, `contexto`, `validacion`, `no_delimita`) y —muy
  importante— `"En espera de evidencia"` como lenguaje público en lugar de "Dejar afuera".
- **Conviene mantener local:** el esquema semántico simple de tokens, la paleta de charts,
  el `footer.*`, los `box.*`, `radius.lg/pill` y la escala tipográfica actual **hasta ver
  una preview**. El export sube body de 9.5 a 10.5 pt y ensancha espaciado (md 12→16,
  lg 16→24), lo que **cambia el paginado** de cualquier informe. No adoptar a ciegas.

### Estado de componentes

- La propuesta de ampliación (`COMPONENTES_PROPUESTA_AMPLIACION_CLAUDE_DESIGN_V1.md`) es
  documental, no toca scripts, y prioriza bien.
- **Adoptar primero:** `RequiereValidacion` + vocabulario de `EstadoDocumentacion`,
  `FuenteEvidencia` y `AlcanceAdvertencia`. Son bloques de prudencia editorial que
  refuerzan los guardrails (separar hallazgo de límite) y no dependen de render nuevo.
- **Dejar para después:** chips visuales completos, halos de mapa y sombras de pantalla —
  requieren backend de render real y QA visual, y los halos tienen riesgo territorial
  (parecer delimitación oficial).

### Compatibilidad con la base local

- `style_tokens_dgdgas.py` resuelve referencias vía un índice de color aplanado y
  `_REF_ROOTS` que incluye `status.`. Los estados nuevos del JSON experimental
  (`status.validation`, `status.waiting`, `status.context`, etc.) **resolverían sin
  romper** si algún día se cargara ese JSON. Los `box.*` del experimental referencian
  claves que existen (`surface.warm`, `status.validation`), así que `box_style()` no
  fallaría. El punto de fricción real no es el JSON, sino el esquema crudo del export
  original (objetos `{value, use}`, claves con `$`, unidades mixtas), que Codex **ya
  neutralizó** al mapear a la forma local.
- **Los scripts están cerca, no lejos**, de poder consumir tokens mapeados: el consumidor
  actual funcionaría con el JSON experimental casi sin cambios. Lo que falta es una
  decisión humana sobre valores (tipografía/espaciado) y una preview.

### Riesgos (Design System)

- **Reemplazo directo de tokens canónicos:** rompería `style_tokens_dgdgas.py` si se usara
  el export crudo. Mitigado mientras se use solo el JSON mapeado y no se toque el canónico.
- **Cambio de paginado:** subir body y espaciado altera saltos de página en informes ya
  revisados. Requiere preview.
- **Tipografías no instaladas** (Libre Franklin, Source Sans 3, IBM Plex Mono): en
  Word/Google Docs o render sin fuentes, los fallbacks deben ser obligatorios. El JSON
  experimental **ya incluye la cadena de fallback**, lo cual es correcto.
- **Cambio de estados sin migración:** templates que esperen `principal/secundario` no
  deben recibir `fuerte/media` sin tabla de equivalencia.
- **Riesgo territorial en mapas** (halos como área de influencia) y **marca**: no exponer
  "DataGastro" como marca pública. Ambos están advertidos en la doc de Codex.

### Recomendación (Design System)

Validar el mapeo con revisión humana y una **preview mínima controlada** antes de tocar
nada canónico. No adoptar valores de tipografía/espaciado sin ver el efecto en A4. Adoptar
primero el vocabulario de estados y el lenguaje público ("En espera de evidencia") a nivel
documentación, que es lo de menor riesgo y mayor valor.

---

## 3. Revisión de PolosGastro

### Fase 7 / Borrador 2

Metodológicamente **consistente**. Es explícitamente un checkpoint interno: no público,
no PDF/DOCX, no delimitación oficial. Cambios sensatos: Palermo como área núcleo única con
subpolos; 4 áreas núcleo en la lectura ejecutiva; sustitución de "No incluir" por "En
espera de evidencia"; incorporación del documento semilla como insumo interno orientador,
no como fuente pública. Deja pendientes claros para Fase 8. No convierte habilitaciones en
"locales activos". Sin objeciones.

### Fase 8 liviana

**Recomendaciones razonables y conservadoras.** Validación documental acotada de 10 casos
débiles/pendientes. Todas las filas de
`recomendaciones_cambio_clasificacion_fase8.csv` llevan `Aplicar ahora = NO`. Los límites
están bien declarados: no se saltaron paywalls, no se usó Google Places, notas
periodísticas no prueban densidad ni padrón, fuentes antiguas no prueban vigencia. Es
exactamente el tono prudente que corresponde. Sin objeciones.

### Fase 8 fuerte / capa objetiva

**Suma, no mete ruido** — siempre que se respete su encuadre. La capa se construye desde
fuentes locales del pipeline (F01 oferta registrada, F02 habilitaciones históricas) en
**solo lectura**, sin descargas nuevas y sin Google Places. El script escribe únicamente
en `outputs/polos_gastro/fase8_fuerte/` y en su carpeta de docs, e incluye un **escáner de
privacidad propio** (email, teléfono, identificador fiscal, DNI, api key, identificadores
privados de Google, enlaces Drive) que dio **0 alertas**.

El `indice_senal_objetiva` está bien definido como indicador interno 0–100 de "presencia
relativa en las fuentes disponibles", con la aclaración explícita de que **no** significa
densidad real, vigencia, calidad ni delimitación.

### Capa objetiva: ¿bien tratada como contexto y no como ranking?

**Sí.** Puntos que lo confirman:

- El cruce `polos_vs_capa_objetiva_fase8_fuerte.csv` no ordena por puntaje: incluye
  columnas de gobierno (`lectura_prudente`, `limitacion_territorial`,
  `recomendacion_metodologica`, `usar_en_borrador_3_si_no`) y la observación fija "No
  aplicar cambios de clasificación automáticamente" en todas las filas.
- Los **corredores y áreas costeras** (Corrientes, Costanera Norte, DoHo, Caseros/Barracas,
  Boedo, Federico Lacroze, Villa Pueyrredón) se marcan `no calculable` y
  `usar_en_borrador_3 = NO`, evitando comparaciones falsas por falta de delimitación.
- En `LECTURA_COMPARADA`, el cuadrante **"evidencia débil/pendiente con señal objetiva
  alta" está vacío ("Sin registros")**. Ese es precisamente el cuadrante donde la señal
  objetiva podría inducir a subir un caso débil de categoría; que esté vacío reduce mucho
  el riesgo de conclusión indebida.

### Casos donde la señal objetiva podría inducir conclusiones indebidas (a vigilar)

- **Aproximación por barrio en subpolos:** Palermo Soho/Hollywood/Las Cañitas y Barrio
  Chino heredan la señal del barrio contenedor (Palermo=100, Belgrano=15.2). La tabla lo
  advierte ("Palermo como barrio no valida el subpolo"), pero en un informe hay que evitar
  que el 100 se lea como validación del subpolo.
- **Abasto (46.04, "medio") y Microcentro (50.82, "medio"):** señal intermedia sobre
  áreas multibarriales/solapadas. El riesgo es citar el número sin la limitación
  territorial que lo acompaña.
- **Regla general:** la columna `indice_senal_objetiva` **no debería viajar sola** a
  ningún informe; siempre con `lectura_prudente` y `limitacion_territorial`.

### Principales riesgos metodológicos (PolosGastro)

- Que un lector externo lea el índice como ranking o densidad real.
- Que la señal de barrio se use para validar subpolos/corredores no delimitados.
- Confundir habilitaciones (F02) u oferta registrada (F01) con "locales activos".
- Presentar como corredor algo sin tramo definido.

Todos están advertidos en la documentación de Codex; el riesgo es de **uso posterior**,
no del artefacto en sí.

### ¿Conviene avanzar a Borrador 3?

**Casi, pero primero una revisión humana acotada.** El material está listo para
alimentar un Borrador 3, pero antes conviene: (1) revisar humanamente el cruce
`polos_vs_capa_objetiva` y confirmar qué tablas van a cuerpo y cuáles a anexo técnico;
(2) resolver los casos que la propia doc marca (Palermo subpolos, Belgrano, Corrientes/
Abasto, Caseros, DoHo, Costanera). Con eso resuelto, Borrador 3 puede arrancar.

---

## 4. Revisión de integración

### ¿Conviene aplicar el Design System a PolosGastro ahora?

**No.** Acumularía dos incertidumbres a la vez: tokens sin preview validada + Borrador 3
sin revisión humana. Además, el propio plan de Codex y el cierre de Fase 7 dicen
explícitamente "no aplicar design system". Primero conviene una **demo mínima aislada**,
no sobre un informe real.

### Qué componentes serían prioritarios (cuando se integre)

Para un informe territorial como PolosGastro, los de mayor valor y menor riesgo:

1. `EstadoDocumentacion` con el vocabulario nuevo (fuerte/media/débil/en_espera/contexto).
2. `AlcanceAdvertencia` (disclaimer de alcance, límites metodológicos visibles).
3. `FuenteEvidencia` (fuentes públicas por bloque, sin datos privados).
4. `TablaPolos` con estados mapeados — **sin ordenar por puntaje ni color**.
5. `MapaContexto` **sin halos**, con disclaimer y fuente cartográfica obligatorios.

### Qué páginas podrían usarse para una demo

Una demo mínima de 2–3 páginas, con datos ya validados y no sensibles:

- **Página de portada + nota metodológica** (marca, tipografía, footer).
- **Una tabla de polos** derivada de `tabla_polos_para_informe_borrador_2.csv`
  (estados y columnas, sin ranking).
- **Una página de "capa objetiva como contexto"** con la tabla comparada + disclaimer,
  para probar `AlcanceAdvertencia` y `EstadoDocumentacion` en un caso real de riesgo.

### Qué NO debería aplicarse todavía

- Chips visuales complejos, halos de mapa, sombras.
- Cambios de tipografía/espaciado sin preview (rompen paginado).
- Cualquier aplicación sobre Borrador 2 o sobre informes finales.
- Mapas de polígonos o de ranking.

---

## 5. Plan recomendado

### Etapa 1 — Validar mapeo de tokens
- Revisión humana de `MAPEO_TOKENS_*.md`, del JSON experimental y del CSV de diff.
- Decidir valores discutibles: tipografía (body 9.5 vs 10.5), espaciado, radios, estados.
- **No tocar tokens canónicos. No tocar scripts.**

### Etapa 2 — Preview mínima controlada
- Construir una preview estática de 2–3 páginas demo (portada+nota, tabla de polos,
  página de capa objetiva como contexto), con datos ya validados.
- **No tocar informes finales. No aplicar a Borrador 2.**

### Etapa 3 — Canonizar (solo si la preview funciona)
- Actualizar `design_tokens_dgdgas.yaml`/`.json` con versión nueva y tabla de equivalencia
  de estados.
- Incorporar `EstadoDocumentacion`, `AlcanceAdvertencia`, `FuenteEvidencia` al catálogo.
- Adaptar `style_tokens_dgdgas.py` con pruebas/smoke checks, manteniendo compatibilidad.

### Etapa 4 — Preparar Borrador 3 de PolosGastro
- Revisión humana del cruce `polos_vs_capa_objetiva`; definir tablas a cuerpo vs anexo.
- Resolver casos señalados (Palermo subpolos, Belgrano, Corrientes/Abasto, Caseros, DoHo,
  Costanera). Redactar Borrador 3 con la capa objetiva **como contexto en anexo técnico**.

### Etapa 5 — Aplicar diseño sobre copia controlada
- Recién aquí aplicar el Design System, sobre una **copia** del Borrador 3, no sobre el
  original. QA público antes de cualquier salida. Sin PDF/DOCX/mapas hasta autorización.

---

## 6. Riesgos

**Técnicos**
- Reemplazo directo de tokens rompería el consumidor actual (mitigado si se usa solo el
  JSON mapeado).
- Cambio de tipografía/espaciado altera paginado de informes existentes.
- Tipografías no instaladas → obligatorio fallback (ya previsto en el JSON mapeado).
- DOCX real requeriría `python-docx` (no instalar sin autorización).

**Metodológicos**
- Lectura del `indice_senal_objetiva` como ranking o densidad real.
- Señal de barrio usada para validar subpolos/corredores no delimitados.
- Confundir habilitaciones/oferta registrada con "locales activos".
- Que el índice viaje sin sus columnas de límite.

**Institucionales**
- Exponer "DataGastro" como marca pública (debe ser DGDGAS).
- Publicar como oficial una capa que es solo contexto interno.
- Lenguaje de descarte ("Dejar afuera") en vez de "En espera de evidencia".
- Circular Borrador 2/3 como informe final sin revisión humana ni QA.

---

## 7. QA

Confirmaciones de esta revisión (auditoría de solo lectura):

- [x] **No commit.**
- [x] **No push.**
- [x] **No staging** — `git diff --cached --name-only` sin resultados.
- [x] **No datos fuente tocados** — `data/` y `src/` no modificados; solo lectura.
- [x] **No Borrador 2 modificado** — solo lectura.
- [x] **No PDF/DOCX generado.**
- [x] **No mapas generados.**
- [x] **No dashboards ni gráficos generados.**
- [x] **No diseño aplicado a informes.**
- [x] **No tokens canónicos modificados** — `design_tokens_dgdgas.json/.yaml` intactos.
- [x] **No scripts productivos modificados.**
- [x] **No Google Places / API keys leídas ni impresas.**
- [x] **No .env, credenciales, place_id ni raw Google Places en este output.**
- [x] Único archivo creado por esta tarea: este informe (más la carpeta `docs/revisiones/`).

---

## Resumen de cierre

- **Archivo creado:** `docs/revisiones/REVISION_INTEGRAL_CLAUDE_CODE_DESIGN_SYSTEM_Y_POLOS_2026_07_01.md`
  (y la carpeta `docs/revisiones/`, que no existía).
- **Archivos modificados:** ninguno.
- **Hallazgo más importante:** el trabajo de Codex es sólido y prudente en ambas líneas;
  el JSON de tokens es válido y no-canónico, y la capa objetiva de PolosGastro está bien
  tratada como contexto (cruce con columna de decisión y cuadrante de riesgo vacío). Nada
  está listo para canonizar ni para aplicar diseño sin una preview y una revisión humana
  previas.
- **Próximo paso recomendado:** validación humana del mapeo de tokens (Etapa 1, sin tocar
  canónicos) y, en paralelo, revisión humana del cruce `polos_vs_capa_objetiva` para
  habilitar el Borrador 3. La aplicación de diseño queda para después de ambas.
- **Confirmación:** no se hizo commit, push ni staging; no se modificó ningún archivo
  fuera del informe nuevo.
