# Auditoría visual — Informe Cafecito DGDGAS · REVISIÓN 3

Revisión página por página del PDF `INFORME_CAFECITO_DGDGAS_REVISION_3.pdf`
(14 páginas). Cada página se inspeccionó renderizándola como imagen.

Archivos de esta revisión:

- PDF: `INFORME_CAFECITO_DGDGAS_REVISION_3.pdf`
  (en `outputs/cafecito/` y `Cafesito/final/`).
- Textos: `contenido_editable_informe_cafecito_revision_3.yaml`.
- Generador: `generar_informe_cafecito_revision_3.py`.

## Qué se aplicó en esta revisión

1. **Numeración de secciones** (1 a 12) en todos los títulos, coherente con el
   índice. Subsecciones simples donde aporta: 1.1 Ficha del relevamiento, 1.2
   Respuestas por día y franja, 4.1 Residencia agregada, 4.2 Barrios y
   localidades más mencionados.
2. **Top 5 de barrios/localidades** en la página de residencia, agregado y con
   normalización mínima (mayúsculas/tildes). Las menciones únicas se agrupan en
   «Otras respuestas». No se publican respuestas individuales.
3. **Explicación de multi-respuesta** en frase completa, junto al gráfico, en
   canales e intereses; etiquetas con menciones ("57% (45)"); base clara
   ("Base: 79 respuestas · pregunta multi-respuesta: se muestran menciones por
   opción").
4. **Bases siempre fuera de las cajas de lectura**, debajo del gráfico.

## Tabla de auditoría

| Página | Problema revisado | Corrección aplicada | Estado final |
| ------ | ----------------- | ------------------- | ------------ |
| 1 · Portada | Marca, datos duplicados, "Entrada libre". | Sin cambios: marca DGDGAS, datos una sola vez, sin "Entrada libre". | OK |
| 2 · Índice | Numeración de secciones y subsecciones; páginas reales. | Índice con números 1–12 y subsecciones 1.1, 1.2, 4.1, 4.2 indentadas; páginas correctas. | OK |
| 3 · Datos generales | Numeración de sección y subsecciones; tabla. | Título "1.", subsecciones "1.1 Ficha del relevamiento" y "1.2 Respuestas por día y franja horaria". Tabla legible. | OK |
| 4 · Preguntas del formulario | Página cargada; legibilidad. | Interlineado y alturas de fila más holgados; las 9 preguntas en una sola página, prolijas, sin cortes; nota al pie cabe sin comprimir. | OK |
| 5 · Perfil | Numeración; cajas de pregunta; títulos de gráfico. | Título "3."; cajas sin desbordar; "Género declarado" separado; bases fuera de cajas. | OK |
| 6 · Lugar de residencia | Sumar top 5 de barrios; numeración; subsecciones. | Título "4."; "4.1 Por zona (CABA/GBA/PBA)" + "4.2 Barrios y localidades más mencionados" (top 5: Belgrano, Caballito, Núñez, Saavedra, Palermo + «Otras respuestas»); nota de privacidad; base fuera de cajas. | OK |
| 7 · Vínculo previo | Numeración; preguntas largas; bases. | Título "5."; preguntas contenidas en sus cajas; donut y barra apilada legibles; base fuera de cajas. | OK |
| 8 · Canales de llegada | Multi-respuesta confusa; base pisada. | Título "6."; explicación completa de multi-respuesta; etiquetas "57% (45)"; base clara fuera de la caja de lectura. | OK |
| 9 · Acompañamiento | Numeración; gráfico holgado. | Título "7."; gráfico centrado y holgado; base fuera de cajas. | OK |
| 10 · Motivaciones | Numeración; gráfico holgado. | Título "8."; gráfico holgado; base fuera de cajas. | OK |
| 11 · Intereses futuros | Multi-respuesta confusa; base pisaba la caja de lectura. | Título "9."; explicación completa de multi-respuesta; etiquetas "35% (28)"; base separada, fuera de la caja de lectura. | OK |
| 12 · Síntesis | Espaciado, viñetas. | Título "10."; viñetas completas, buen espaciado. | OK |
| 13 · Aspectos a considerar | Recomendaciones en potencial; espaciado. | Título "11."; recomendaciones en potencial; sin desbordes. | OK |
| 14 · Anexo red de cafeterías | Mapas; nota prudente; marca. | Título "12."; mapas legibles; nota prudente visible; marca DGDGAS. | OK |

## Top 5 de barrios/localidades (resultado)

Sí se pudo agregar. Base: 79 respuestas con dato declarado.

| Barrio/localidad | % | Menciones |
| --- | --- | --- |
| Belgrano | 24% | 19 |
| Caballito | 6% | 5 |
| Núñez | 6% | 5 |
| Saavedra | 5% | 4 |
| Palermo | 5% | 4 |
| Otras respuestas | 53% | 42 |

La frecuencia mínima del top 5 es 4 (agregado, no expone individuos). Las 20
respuestas con una sola mención quedan dentro de «Otras respuestas». No se
publican valores individuales.

## QA textual final

**No aparece** (0 ocurrencias): `DataGastro`, `Entrada libre y gratuita`, la nota
de horario extendido, `.py`, `.csv`, `.yaml`, `outputs/`, `scripts/`, rutas de
Windows, hashes, `QA`, emails, `EDITABLE_TEST`, `REVISION_1/2/3`, "procedencia",
marcadores sin reemplazar.

**Sí aparece**: `DGDGAS`, `Dirección General de Desarrollo Gastronómico`, índice con números
de página, secciones numeradas, subsecciones, lugar, fechas, horarios, preguntas
del formulario, resultados en porcentajes, explicación de multi-respuesta,
menciones por opción, top de barrios, bases fuera de cajas de lectura.

Verificación específica: **ninguna línea de "Base:" aparece pegada a "Lectura de
resultados"** en ninguna página.

## Confirmaciones

- No se sobrescribió el FINAL, ni las revisiones 1, 2 o 2·formato (hashes intactos).
- No se modificó el XLSX original ni los datos fuente.
- No se cambiaron cálculos salvo el nuevo agregado pedido (top de barrios).
- No se reintrodujo DataGastro.
