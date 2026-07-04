# Auditoría visual — Informe Cafecito DGDGAS · REVISIÓN 2

Revisión visual página por página del PDF `INFORME_CAFECITO_DGDGAS_REVISION_2.pdf`
(14 páginas tras la corrección; 13 en la versión auditada). Cada página se
inspeccionó renderizándola como imagen, no solo extrayendo texto.

Las correcciones se aplicaron en una versión nueva, **sin sobrescribir** la
revisión 2:

- PDF corregido: `INFORME_CAFECITO_DGDGAS_REVISION_2_FORMATO.pdf`
  (en `outputs/cafecito/` y `Cafesito/final/`).
- Textos: `contenido_editable_informe_cafecito_revision_2_formato.yaml`.
- Generador: `generar_informe_cafecito_revision_2_formato.py`.

## Resumen de cambios de formato

1. **Cajas de pregunta que desbordaban** (perfil, vínculo, acompañamiento): el
   texto de la pregunta se salía del borde derecho en las columnas angostas. Se
   recalibró el ancho de ajuste de línea al ancho real de la caja menos su
   margen interno; ahora el texto se reparte en más líneas y queda contenido.
2. **Nota de "Base" pisada por la caja de lectura** (canales, intereses): la
   base del gráfico se dibujaba dentro del área del gráfico y caía sobre la caja
   inferior. Se reposicionó debajo del gráfico, con espacio reservado.
3. **Gráficos apretados con labels montados sobre las barras**
   (acompañamiento y motivaciones, que iban juntos en una sola página): se
   **dividió en dos páginas**, una por gráfico, con más ancho y aire.
4. **Cajas de "Lectura de resultados" con exceso de vacío**: pasaron a tener
   altura ajustada al texto.

El informe pasó de 13 a **14 páginas** por la división de acompañamiento /
motivaciones, y el índice se recalculó.

## Tabla de auditoría

| Página | Estado | Problema detectado | Corrección aplicada | Estado final |
| ------ | ------ | ------------------ | ------------------- | ------------ |
| 1 · Portada | OK | Sin problemas. Marca DGDGAS, sin DataGastro, sin "Presenta" duplicado, sin "Entrada libre y gratuita". | Sin cambios de fondo. | OK |
| 2 · Índice | A corregir | Los números de página debían recalcularse al pasar a 14 páginas. | Índice actualizado con división acompañamiento (9) / motivaciones (10) y corrimiento del resto. | OK |
| 3 · Datos generales | OK | Tabla legible, sin la nota de horario extendido, sin texto fuera de caja. | Sin cambios (se mantuvo la corrección de la revisión 2). | OK |
| 4 · Preguntas del formulario | OK | Las 9 preguntas con tipo y objetivo entran en una sola página, sin texto cortado ni cajas desbordadas. | Sin cambios. | OK |
| 5 · Perfil | A corregir | La pregunta "¿Con qué género te identificás?" rozaba/desbordaba el borde derecho de su caja. | Wrap recalibrado: la pregunta se reparte en dos líneas dentro de la caja. Título "Género declarado" separado del bloque. | OK |
| 6 · Lugar de residencia | A corregir (menor) | Barras y labels correctos; caja de lectura con exceso de espacio vacío. | Caja de lectura con altura ajustada al texto. Labels con más ancho de ajuste. | OK |
| 7 · Vínculo previo | A corregir | La pregunta "¿Aceptás recibir información sobre próximos eventos…?" desbordaba el borde derecho (palabra fuera de la caja). | Wrap recalibrado: la pregunta queda contenida. Donut y barra apilada legibles. | OK |
| 8 · Canales de llegada | A corregir | La nota de "Base · multi-respuesta" quedaba pisada por la caja de lectura. | Base reposicionada debajo del gráfico, visible. Labels con más ancho. | OK |
| 9 · Acompañamiento | A corregir (importante) | En una sola página con motivaciones: gráfico angosto con labels montados sobre las barras; pregunta desbordada; bases pegadas a la caja. | **Dividido en página propia** ("acompañamiento en el evento") con gráfico holgado y centrado. | OK |
| 10 · Motivaciones | Nueva | Antes compartía página con acompañamiento (apretado). | **Página propia** ("motivaciones e intereses del momento") con el gráfico de "qué interesó" holgado, labels sin montarse. | OK |
| 11 · Intereses futuros | A corregir | Pregunta larga (2 líneas) + 8 barras + lectura: la base del gráfico se solapaba con el título de la caja de lectura. | Caja de lectura anclada abajo y gráfico apoyado encima con margen para la base; sin solapamiento. | OK |
| 12 · Síntesis | OK | Viñetas completas, buen espaciado, sin cortes. | Sin cambios. | OK |
| 13 · Aspectos a considerar | OK | Recomendaciones en potencial, buen espaciado, sin desbordes. | Sin cambios. | OK |
| 14 · Anexo red de cafeterías | OK | Mapas legibles, títulos no se pisan, nota prudente visible, sin DataGastro. | Sin cambios (marca DGDGAS verificada). | OK |

## QA textual final (PDF corregido)

**No aparece** (verificado, 0 ocurrencias): `DataGastro`, `Entrada libre y
gratuita`, la nota de horario extendido, rutas locales, `.py`, `.csv`, `.yaml`,
`outputs/`, `scripts/`, rutas de Windows, hashes, `QA`, emails, `EDITABLE_TEST`,
fracciones tipo `x/79`, "procedencia", marcadores sin reemplazar.

**Sí aparece**: `DGDGAS`, `Dirección General de Desarrollo Gastronómico`, `Cafecito BA en tu
barrio`, índice con números de página, lugar, fechas, horarios, preguntas del
formulario, resultados en porcentajes.

## Confirmaciones

- No se sobrescribió el FINAL, la REVISIÓN 1 ni la REVISIÓN 2 (hashes intactos).
- No se modificó el XLSX original ni los datos fuente.
- No se cambiaron cálculos ni se agregaron conclusiones nuevas.
- No se reintrodujo DataGastro.
