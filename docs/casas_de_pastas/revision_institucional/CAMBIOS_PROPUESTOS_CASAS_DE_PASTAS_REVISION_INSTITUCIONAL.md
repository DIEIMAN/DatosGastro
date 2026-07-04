# Cambios propuestos — Revisión institucional Casas de Pastas

Comparación entre el informe actual (`outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.md`) y la nueva versión institucional (`INFORME_CASAS_DE_PASTAS_REVISION_INSTITUCIONAL.md`). No se eliminó información relevante; se reordenó la arquitectura, se concentró la metodología y se movió el contenido técnico a anexos.

| Parte del informe actual | Problema detectado | Cambio propuesto | Motivo |
| --- | --- | --- | --- |
| Título `# DataGastro — Diagnóstico territorial gastronómico` | Usa DataGastro como marca pública | Reemplazado por `# Casas de Pastas / Mercados de Pastas — Informe` con firma **DGDGAS — Dirección General de Gastronomía · Gobierno de la Ciudad de Buenos Aires` | Guardrail: no usar DataGastro como marca pública; usar DGDGAS como marca visible |
| Firma `Análisis y desarrollo: Diego Aleman` | Crédito personal en un informe institucional | Retirado del cuerpo público (autoría no se expone como marca; queda en la trazabilidad interna) | Pieza institucional, no personal |
| Sin índice | Documento sin navegación | Se agregó **Índice** con secciones numeradas y anclas | Requisito de la revisión; facilita lectura de autoridad |
| Secciones en formato pregunta ("¿Qué universo…?", "¿Por qué…?", "¿Dónde…?") | Arquitectura de expediente/FAQ, no institucional | Reescritas como secciones numeradas temáticas (2 a 9) | Mejorar títulos y estructura; tono sobrio |
| Bloque "Indicadores" al inicio, sin resumen ejecutivo | Faltaba una síntesis de una página | Se agregó **1. Resumen ejecutivo** (qué analiza, por qué importa, hallazgos, qué permite, oportunidades, límites) | Requisito; pirámide invertida |
| Metodología dispersa (notas técnicas repetidas en varias secciones: "no oficial", "no es censo", tabla de fuentes, revisión manual) | Repetición de aclaraciones metodológicas sección por sección | Metodología concentrada en **3. Metodología y fuentes**; detalle técnico movido a **Anexo A** | Concentrar metodología; no repetir notas técnicas |
| Tabla de fuentes (§2 actual) | Correcta, pero mezclada con lectura | Se mantiene íntegra en la sección 3 (metodología) | No perder información; ubicarla donde corresponde |
| §3 y §4 (concentración y densidad) con rankings top-5 | Información válida pero sin lectura institucional ni tablas completas | Resultados agrupados en bloques **dato / lectura / implicancia** (5.1 y 5.2); tablas completas por comuna y barrio movidas al **Anexo B** | Requisito de bloques; anexar tablas largas |
| §5 "¿Qué barrios son polos?" | Solapaba con concentración | Reordenado como 5.3, diferenciando polos por cantidad | Evitar repetición, mantener el dato |
| §6 y §7 (cadenas y listado de cadenas) | Listado largo en el cuerpo | Bloque 5.4 con la lectura + **Anexo D** con el detalle completo de cadenas | Cuerpo liviano; detalle en anexo |
| §8 "Núcleo de mayor respaldo cruzado" | Dato clave enterrado al final | Elevado en el cuerpo (5.5) y citado en el resumen ejecutivo | Jerarquizar el hallazgo más sólido |
| §9 "¿Qué aportó la revisión manual?" | Correcto | Mantenido como 5.6 en formato dato/lectura/implicancia | Conservar información |
| §10 "¿Qué aporta esta metodología?" (replicabilidad) | Mezclaba metodología con lectura de gestión | Llevado a **7. Lectura institucional** con lenguaje prudente ("podría", "convendría") | No prometer acciones no decididas |
| "Casos con respaldo documental" | Contenido de respaldo en el cuerpo | Movido a **Anexo C** íntegro | Aligerar cuerpo sin perder los casos |
| "¿Para qué sirve este diagnóstico?" | Buen contenido, título coloquial | Integrado en **1. Resumen ejecutivo** y **7. Lectura institucional** | Mejor arquitectura |
| "Limitaciones" (párrafo único) | Límites correctos pero en bloque denso | **8. Aspectos a considerar** (lista priorizada) + **Anexo E** (tabla L1–L7) | Priorizar y ordenar los límites |
| Sin sección de próximos pasos explícita | Próximos pasos dispersos en §10 y limitaciones | **9. Próximos pasos** como lista de opciones (validación, fuentes, actualización, visualizaciones, cruces) | Requisito; sin comprometer ejecución |
| Datos territoriales solo como top-5 | El detalle completo por comuna/barrio no estaba en el informe público | Tablas completas (15 comunas, 42 barrios) sumadas al **Anexo B** desde los agregados sanitizados v3 depurados | Sumar información disponible sin recortar |

## Criterios aplicados

- No se eliminó información relevante; se reubicó (tablas y metodología a anexos).
- Se eliminó repetición de aclaraciones metodológicas.
- Se mejoró arquitectura: índice, secciones numeradas, resumen ejecutivo, anexos al final.
- No se inventaron datos, porcentajes ni conclusiones: todas las cifras provienen del informe V4 y de los agregados sanitizados existentes.
- No se mostraron rutas locales, scripts, hashes ni nombres internos en el informe principal.
