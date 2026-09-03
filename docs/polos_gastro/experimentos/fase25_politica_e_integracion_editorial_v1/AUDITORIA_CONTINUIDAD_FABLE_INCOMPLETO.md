# Auditoría de continuidad del trabajo editorial incompleto

Estado: **EXPERIMENTAL / NO OFICIAL**  
Fecha de auditoría: 2026-07-11  
Alcance: tanda `fase25_politica_e_integracion_editorial_v1`.

## Conclusión de continuidad

El trabajo existente constituye una base editorial avanzada y no debe rehacerse. Están completos el registro de decisiones, el sistema que separa tipo territorial y madurez, sus matrices operativas, el banco de textos, el contenido editable y la primera versión funcional del generador. El PDF existente tiene 10 páginas y texto extraíble, pero no puede considerarse validado porque el generador fue modificado después de producirlo.

La carpeta completa está actualmente sin seguimiento en Git. Por ese motivo no existe un diff histórico que permita atribuir el último cambio a una línea mediante Git. La evidencia disponible es inequívoca en cuanto al orden:

- PDF generado: 2026-07-11 11:00:13;
- generador modificado: 2026-07-11 11:01:09.

La versión no validada es, por lo tanto, la versión actual del generador. La comprobación operativa pendiente consiste en ejecutarla, renderizar nuevamente sus 10 páginas y comparar el resultado con las imágenes de QA previas. El efecto observado de esa regeneración se incorporará al cierre de esta auditoría.

### Verificación posterior

La versión actual se ejecutó sin cambios previos y produjo nuevamente 10 páginas. El PDF pasó de 2.140.167 bytes a 2.123.582 bytes, confirmando que la salida anterior no correspondía exactamente al último estado guardado del generador. Después del QA visual se incorporó una corrección reproducible de rótulos únicamente sobre las copias experimentales; el PDF final quedó en 1.990.167 bytes. La falta de historial Git impide atribuir el guardado de las 11:01:09 a una línea anterior concreta, pero el cambio incompleto quedó operacionalmente verificado y su salida actual fue validada completa.

## Estado por componente

| Componente | Estado inicial | Evidencia | Acción de continuidad |
| --- | --- | --- | --- |
| `REGISTRO_DECISIONES_EDITORIALES_V2.md` | COMPLETO | Registra DEC-01 a DEC-20, pendientes v2.1 y decisiones abiertas. | Conservar como fuente de decisiones. |
| `SISTEMA_TIPO_Y_MADUREZ_TERRITORIAL.md` | COMPLETO | Define dos dimensiones independientes y reglas visuales. | Conservar y aplicar. |
| `MATRIZ_TIPO_MADUREZ.csv` | COMPLETO | Asignación operativa por zona, tipo, madurez y pendiente. | Incluir en el paquete. |
| `BANCO_TEXTOS_POLITICOS_V1.md` | COMPLETO | Banco canónico TXT-01 a TXT-20. | Conservar; corregir solo si el QA detecta una contradicción editorial. |
| `contenido_fase25_politica_experimental_v1.yaml` | COMPLETO | Contenido de las 10 páginas; compatible con parser restringido. | Mantener el mecanismo existente, sin PyYAML obligatorio. |
| `MATRIZ_ASSETS_PENDIENTES_CODEX.csv` | COMPLETO | Identifica placeholders y reemplazos futuros v2.1. | Incluir sin integrar capas. |
| `generar_fase25_politica_experimental_v1.py` | COMPLETO_REQUIERE_QA | Generador funcional de 454 líneas; su mtime es posterior al PDF. | Ejecutar y validar su versión actual. |
| `INFORME_POLOS_GASTRO_FASE25_POLITICA_EXPERIMENTAL_V1.pdf` | COMPLETO_REQUIERE_QA | PDF A4, 10 páginas, texto extraíble, generado antes del último cambio del script. | Regenerar y validar. |
| `qa_png_INFORME_POLOS_GASTRO_FASE25_POLITICA_EXPERIMENTAL_V1/` | COMPLETO_REQUIERE_QA | Hay 10 PNG, uno por página, todos de 910 x 1287 px. | Volver a renderizar y revisar página por página. |
| `ESPECIFICACION_PLANTILLAS_MAPAS_POLITICOS.md` | NO_INICIADO | No existía al iniciar esta continuidad. | Crear con placeholders y requisitos. |
| `ARQUITECTURA_INFORME_POLOS_HIBRIDOS_V2.md` | NO_INICIADO | No existía en esta tanda. | Crear con variantes política e interna. |
| `MATRIZ_DEPENDENCIAS_INFORME_HIBRIDO.csv` | NO_INICIADO | No existía en esta tanda. | Crear. |
| `BORRADOR_INFORME_EVOLUCION_METODOLOGICA_ACTOS_I_III.md` | NO_INICIADO | No existía en esta tanda. | Redactar Actos I a III; no cerrar Acto IV. |
| `kpis_lock_preliminar.json` | NO_INICIADO | No existía en esta tanda. | Crear sin inventar valores ni cerrar pendientes v2.1. |
| `PLAN_INTEGRACION_HANDOFF_CODEX_V21.md` | NO_INICIADO | No existía en esta tanda. | Documentar integración futura sin ejecutarla. |
| QA final, manifest, metadata y paquete | NO_INICIADO | No existían. | Crear al finalizar el QA. |

## Superficies protegidas al inicio

Se registró una línea base mediante conteo y hash de árbol para:

- Fase 25 oficial: `outputs/polos_gastro/fase25_microajustes_finales_oficina/`;
- documentación, outputs y scripts de `pipeline_hibrido_integracion_v21/`;
- Fase 26 comparativa, localizada fuera de esta tanda.

Estas superficies se mantuvieron en modo solo lectura. Los hashes se recalcularon en el QA final y coincidieron con la línea base.

## Límites de la tanda

- No se integra el handoff técnico v2.1.
- No se ejecutan algoritmos territoriales ni clustering.
- No se realizan llamadas externas, descargas ni instalaciones.
- No se modifican datos fuente, Fase 25 oficial, Fase 26 ni outputs técnicos.
- No se realiza staging, commit ni push.
