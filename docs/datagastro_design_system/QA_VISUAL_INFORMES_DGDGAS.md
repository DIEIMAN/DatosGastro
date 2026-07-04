# QA visual — DGDGAS Informes v1

Checklist para revisar un informe (o plantilla pública) antes de publicarlo.
Combina QA **visual**, QA **editorial** y QA **público** (privacidad / no fuga
de material técnico). Un informe no se considera cerrado hasta pasar todo.

Marcar cada ítem: `[ ]` pendiente · `[x]` verificado · `[n/a]` no aplica.

---

## A. Marca y portada

- [ ] Marca pública = `DGDGAS – Dirección General de Desarrollo Gastronómico`.
- [ ] **No** aparece `DataGastro` como marca pública (solo interno, si aplica).
- [ ] La Dirección es más visible que el nombre interno del proyecto.
- [ ] Portada institucional, limpia, sin decoración marketinera.
- [ ] «Presenta: DGDGAS – Dirección General de Desarrollo Gastronómico».

## B. Estructura y editorial

- [ ] Índice con **números de página** reales.
- [ ] Secciones **numeradas**.
- [ ] **Datos duros primero**, interpretación después.
- [ ] En encuestas, la **pregunta se muestra antes** del resultado.
- [ ] Tipo de pregunta indicado (cerrada / abierta / multi-respuesta /
      consentimiento).
- [ ] En multi-respuesta: se muestran **menciones** y se aclara que la suma
      **puede superar 100 %**.
- [ ] Notas metodológicas **breves** en el cuerpo; lo extenso está en anexo.
- [ ] Oraciones completas; tono descriptivo y prudente.
- [ ] Recomendaciones en **potencial** («podría», «sería conveniente»…).
- [ ] Hallazgos y límites están **separados**; no se afirma representatividad
      inexistente.

## C. Gráficos

- [ ] Gráficos legibles; se priorizan barras/tablas sobre circulares.
- [ ] Cada gráfico tiene **título**, **base/universo**, **fuente** y **lectura
      breve**.
- [ ] Sin gráficos decorativos que no aporten a una lectura o decisión.
- [ ] Colores dentro de la secuencia de tokens (`chart.sequence`).

## D. Tablas

- [ ] Encabezados claros; números alineados a la derecha.
- [ ] Sin columnas técnicas en informe ejecutivo.
- [ ] Filas legibles (zebra) y bordes sobrios.
- [ ] Resultados principales separados de anexos.
- [ ] En tablas de revisión: estado / prioridad / decisión sugerida visibles.

## E. Mapas / cartografía

- [ ] Mapa **útil**, no decorativo.
- [ ] **No** representa límites oficiales inexistentes.
- [ ] Usa barrios / comunas como referencia territorial.
- [ ] Nota de **alcance** presente si el mapa es conceptual / preliminar / de
      trabajo.
- [ ] Estilo sobrio; **no** mapa tipo red.
- [ ] **No** usa coordenadas ni geometría de plataformas privadas como base.
- [ ] **No** usa Google Places como fuente pública principal.

## F. Consistencia visual (tokens)

- [ ] Colores del informe corresponden a los tokens (`brand.*`, `text.*`,
      `surface.*`, `status.*`).
- [ ] Tipografías y escala de títulos según tokens.
- [ ] Márgenes y espaciados consistentes (A4).
- [ ] Cajas usan el relleno/acento correcto por tipo (pregunta / lectura /
      nota / advertencia / validación).
- [ ] Footer con patrón `DGDGAS - {proyecto} - {tipo}` y número de página.

## G. QA público (privacidad y no fuga técnica)

- [ ] **No** rutas locales.
- [ ] **No** nombres de scripts ni archivos técnicos.
- [ ] **No** hashes, IDs internos ni QA técnico.
- [ ] **No** emails, teléfonos ni datos de contacto.
- [ ] **No** datos personales, CUIT ni DNI.
- [ ] **No** API keys ni credenciales.
- [ ] **No** links privados.
- [ ] **No** respuestas individuales identificables (todo agregado).
- [ ] **No** se convierten habilitaciones / registros / menciones en «locales
      activos».
- [ ] Marcas de estado interno (borrador / uso interno) removidas del público.

## H. Datos y fuentes

- [ ] No hay datos, métricas, URLs ni conclusiones inventadas.
- [ ] Cada bloque cita su fuente / relevamiento.
- [ ] Universos de fuentes no se mezclan indebidamente (públicas / internas /
      externas).

---

## Salida esperada del QA

Al terminar, dejar constancia (en el pedido, no en el PDF público) de:

1. Ítems verificados / pendientes / n/a.
2. Correcciones aplicadas.
3. Confirmación de que no quedó material sensible ni técnico en la salida
   pública.
