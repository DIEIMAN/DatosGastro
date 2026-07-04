# Skill operativa: reporte con formulario

Guía corta para informes DataGastro basados en formularios, encuestas o relevamientos
exploratorios de eventos y acciones gastronómicas.

## Cuándo usarla

Cuando haya un formulario, encuesta o relevamiento exploratorio de un evento o acción
gastronómica, especialmente si proviene de Google Forms, una planilla de respuestas o un
operativo de captación en territorio.

## Entradas típicas

- XLSX/CSV de respuestas.
- PDF/DOCX con preguntas o justificación del formulario.
- Documento de contexto del evento o acción.
- Gráficos exportados del formulario, si existen.

## Flujo recomendado

1. Inventariar archivos.
2. Identificar datos personales.
3. Leer preguntas y objetivo de cada una.
4. Construir diccionario de preguntas.
5. Limpiar sin modificar fuente.
6. Separar preguntas cerradas, multi-respuesta y abiertas.
7. Generar resúmenes por pregunta.
8. Generar gráficos simples.
9. Hacer cruces prudentes.
10. Redactar informe exploratorio.
11. Crear DOCX/PDF con gráficos si se pide.
12. Ejecutar QA de privacidad.

## Reglas de interpretación

- No afirmar representatividad si no hay muestra diseñada.
- Usar "muestra exploratoria" cuando corresponda.
- Reportar siempre base `n`.
- No forzar cruces con celdas chicas.
- Separar hallazgos cuantitativos de lecturas cualitativas.
- No mostrar respuestas abiertas si pueden identificar personas.
- No convertir respuestas de encuesta en verdad general sobre todo el evento.
- En multi-respuesta, aclarar que los porcentajes pueden sumar más de 100%.

## Outputs esperados

- Script reproducible.
- Resumen de variables.
- Resumen de respuestas cerradas.
- Resumen de respuestas abiertas.
- Gráficos.
- Informe Markdown.
- DOCX con gráficos si corresponde.
- README de regeneración.

## QA mínimo

- Ejecutar el script de análisis desde cero.
- Verificar que el XLSX/CSV original no se modificó, idealmente con hash antes/después.
- Verificar cantidad total de respuestas/registros.
- Verificar que las bases `n` reportadas coinciden con los datos.
- Verificar que preguntas multi-respuesta no parten opciones canónicas con coma interna.
- Verificar que no se publican correos, teléfonos, nombres, DNI, CUIT, timestamps individuales,
  links privados, IDs técnicos ni API keys.
- Verificar que no aparece `@` en outputs públicos.
- Verificar que los gráficos existen.
- Verificar que el informe Markdown existe.
- Verificar que el DOCX/PDF existe si fue pedido.
- Verificar que el README explica cómo regenerar outputs.
- Verificar que no se tocaron datos fuente, pipelines ni proyectos fuera de alcance.
- Confirmar que no hubo commit, push ni `git add .`.
