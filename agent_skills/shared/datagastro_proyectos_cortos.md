# Guía para proyectos cortos DataGastro

Aplica a proyectos chicos con formularios, encuestas, relevamientos exploratorios, eventos o
entregables puntuales: Cafecito, pilotos barriales, validaciones rápidas y futuros informes de
formulario.

## Flujo recomendado

1. Inventariar fuentes disponibles: XLSX/CSV, PDF del formulario, documentos de contexto,
   imágenes/gráficos exportados, textos operativos.
2. Leer la metodología o justificación del formulario antes de analizar datos.
3. Crear o actualizar un diccionario de preguntas.
4. Analizar el XLSX/CSV en modo solo lectura.
5. No modificar la fuente original.
6. Excluir datos personales o potencialmente identificables de outputs públicos.
7. Generar resúmenes por pregunta.
8. Generar gráficos simples.
9. Tratar cruces como exploratorios.
10. Redactar informe Markdown.
11. Si se pide, generar DOCX/PDF con gráficos y lecturas breves.
12. Cerrar con QA de privacidad, cantidad de respuestas y regenerabilidad.

## Lectura de fuentes

- PDF/metodología: identificar objetivo del relevamiento, destinatarios, uso esperado y límites.
- XLSX/CSV: identificar columnas, tipos de pregunta, faltantes y campos sensibles.
- DOCX o gráficos exportados: usar como contraste y contexto, no como reemplazo del dato fuente.
- TXT o notas: usar solo para contexto del evento; no inventar datos ausentes.

## Diccionario de preguntas

Debe incluir:

- Columna original.
- Pregunta visible.
- Objetivo.
- Tipo de variable.
- Cómo se analiza.
- Si es sensible o publicable.
- Limitaciones.

## Limpieza

- No modificar el archivo fuente.
- Normalizar espacios y categorías solo cuando sea necesario y documentado.
- No imputar faltantes.
- No corregir texto libre de forma que altere el sentido.
- Documentar decisiones de limpieza.

## Preguntas multi-respuesta

- Identificar separador real usado por el formulario.
- Proteger opciones canónicas que tengan coma interna.
- Reportar base de respondentes y aclarar que la suma puede superar 100%.
- No partir categorías como "Por amigos, familia o conocidos" si son una opción única.
- No convertir respuestas múltiples en ranking excluyente.

## Respuestas abiertas

- No publicar respuestas abiertas que puedan identificar personas.
- Resumir por temas o menciones agregadas.
- Si hay cola de menciones únicas, redactarla con prudencia o no publicarla si hay riesgo.
- No sobreinterpretar frases aisladas.

## Privacidad

Nunca publicar:

- Correos.
- Teléfonos.
- Nombres.
- DNI/CUIT/CUIL.
- Marcas temporales individuales.
- Barrios/localidades libres si la combinación puede identificar a alguien.
- Links privados, IDs técnicos o API keys.

Trabajar con agregados y notas metodológicas visibles.

## Informe Markdown

Estructura mínima:

1. Objetivo del relevamiento.
2. Alcance y limitaciones.
3. Perfil general.
4. Resultados por pregunta.
5. Canales o motivaciones, si aplica.
6. Cruces exploratorios, si aplica.
7. Conclusiones prudentes.
8. Recomendaciones para próximos relevamientos.
9. Fuentes usadas y outputs generados.

## DOCX con gráficos

Debe incluir:

- Portada simple.
- Cantidad de respuestas/registros.
- Nota metodológica breve.
- Cada gráfico generado.
- Lectura corta debajo de cada gráfico.
- Conclusiones finales.
- Recomendaciones.
- Sin datos personales ni respuestas abiertas identificables.

## QA final

- Ejecutar script de análisis.
- Verificar que el XLSX/CSV fuente no cambió, idealmente con hash antes/después.
- Verificar cantidad de respuestas reportada.
- Verificar que outputs públicos no contienen `@`, emails, teléfonos ni identificadores.
- Verificar que gráficos existen.
- Verificar que informe Markdown existe.
- Verificar que DOCX/PDF existe si se pidió.
- Verificar categorías multi-respuesta críticas.
- Verificar que no se tocaron proyectos o pipelines fuera de alcance.
- Confirmar que no hubo commit, push ni `git add .`.
