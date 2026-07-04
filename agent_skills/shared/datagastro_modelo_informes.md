# Modelo común para informes DataGastro

Este estándar aplica a informes de Cafecito, Mercados, Casas de Pastas y futuros proyectos
DataGastro. El objetivo es producir entregables útiles para gestión pública, trazables,
reproducibles y seguros desde el punto de vista de privacidad.

## Principios generales

- No inventar datos, métricas, URLs, fuentes, fechas ni conclusiones.
- Diferenciar dato oficial, dato relevado, señal documental, señal operativa e inferencia.
- Usar lenguaje prudente: "muestra exploratoria", "base candidata", "lectura orientativa" o
  "insumo para gestión", según corresponda.
- No afirmar representatividad si no hay diseño muestral.
- No exponer datos personales.
- No publicar correos, teléfonos, nombres, CUIT, DNI, IDs técnicos, links privados ni API keys.
- Separar outputs públicos de fuentes internas/crudas.
- Documentar limitaciones, fecha de corte, universo, fuente y método de generación.
- No convertir habilitaciones, permisos, registros documentales o señales en "locales activos" si
  la fuente no mide actividad actual.
- No mezclar universos de fuentes como si fueran un total único.

## Estructura base de informe

1. Portada / título
2. Resumen ejecutivo
3. Objetivo del relevamiento
4. Alcance y metodología
5. Limitaciones
6. Perfil general de los datos
7. Resultados principales
8. Gráficos y lectura
9. Cruces exploratorios, si aplica
10. Hallazgos cualitativos, si aplica
11. Conclusiones
12. Recomendaciones para gestión
13. Próximos pasos
14. Anexo metodológico / diccionario de variables

## Estilo narrativo

- Institucional, claro y sobrio.
- No sonar a informe académico pesado.
- No sonar a publicidad.
- Priorizar utilidad para decisión pública.
- Explicar "qué nos dicen los datos" y "qué decisión habilitan".
- Separar hallazgos de límites metodológicos.
- Cuando la muestra sea chica, usar frases prudentes.
- Evitar lenguaje de IA, superlativos vacíos y conclusiones más fuertes que la evidencia.

Frases útiles:

- "Los resultados deben leerse como una primera aproximación exploratoria."
- "La muestra no permite inferencias representativas sobre la totalidad del público."
- "El relevamiento permite identificar señales iniciales para orientar futuras acciones."
- "Estos resultados sirven como insumo para mejorar próximos relevamientos."
- "La lectura es orientativa y debe complementarse con nuevas mediciones."

## Estándar de gráficos

- Gráficos simples y legibles.
- Priorizar barras horizontales o verticales.
- No usar gráficos complejos si no aportan a una decisión.
- Incluir siempre base `n`, fuente y nota de alcance.
- No mostrar datos personales ni identificadores.
- No graficar categorías de identificación individual si pueden exponer personas.
- Cada gráfico debe tener una lectura corta debajo.
- Si una pregunta es multi-respuesta, aclarar que los porcentajes pueden sumar más de 100%.
- Evitar paletas decorativas: priorizar contraste, lectura y sobriedad institucional.

## Estándar de QA

Antes de cerrar un informe:

- Validar que los datos fuente no fueron modificados.
- Verificar que no haya correos ni datos sensibles en outputs.
- Verificar que los gráficos existen y fueron regenerados desde la fuente correcta.
- Verificar que el informe referencia solo archivos existentes.
- Verificar que las cantidades reportadas coinciden con los datos.
- Verificar que no hay afirmaciones exageradas o representatividad no justificada.
- Documentar scripts y cómo regenerar outputs.
- Confirmar qué archivos fueron creados/modificados.
- Confirmar que no hubo commit, push ni `git add .`, salvo pedido explícito.

## Checklist de cierre

- Fuentes usadas.
- Cantidad de registros/respuestas y fecha de corte.
- Outputs generados.
- Gráficos generados.
- Ruta del informe principal.
- Principales hallazgos.
- Limitaciones.
- Recomendaciones.
- QA de privacidad.
- Confirmación de alcance: qué no se tocó.
