# Evaluación agentes y skills V1

**Fecha:** 2026-07-11  
**Método:** casos de prueba A–D sobre packs existentes (solo lectura de orígenes) + revisión de definiciones.  
**Criterio:** no declarar “listo para producción” solo porque existan archivos.

Escala: **APTO** | **APTO_CON_AJUSTES** | **NO_APTO**

---

## Resumen ejecutivo de aptitud

| Elemento | Aptitud | Motivo breve |
| --- | --- | --- |
| Política operativa | APTO | Corta, usable, alineada a guardrails |
| Matriz de reglas | APTO | Trazable a fuentes del repo |
| Arquitectura | APTO_CON_AJUSTES | Falta script de paridad y prueba runtime Claude agents |
| Skill auditar_entregable_experimental | APTO | Encaja con QA_FINAL reales |
| Skill qa_pdf_pagina_por_pagina | APTO | Caso B ejecutado con pdf_check + visión muestral |
| Skill crear_paquete_revision_sanitizado | APTO_CON_AJUSTES | No re-empaquetó en esta tanda; patrón validado en packs origen |
| Skill auditar_git_y_archivos_protegidos | APTO_CON_AJUSTES | Procedimentalmente clara; no se midieron 386 hashes aquí |
| Skill crear_manifest_hashes_metadata | APTO_CON_AJUSTES | Plantilla + packs origen; script utilitario aún no en scripts/infra |
| Skill integrar_handoffs | APTO | Casos A/C |
| Skill validar_metricas_y_kpis | APTO_CON_AJUSTES | No se corrió validate_kpis sobre F25 en esta tanda |
| Skill transformar_cartografia_a_presentacion | APTO | Caso D checklist sin regenerar |
| Skill gestionar_decisiones_humanas | APTO | Matriz v2.1 y handoffs |
| Skill auditar_evidencia_documental | APTO | Caso A REC-R02 |
| investigador_documental | APTO | Caso A |
| auditor_metodologico | APTO_CON_AJUSTES | Sin caso de ablación dedicado en esta tanda |
| cartografo_territorial | APTO | Caso D |
| editor_institucional | APTO_CON_AJUSTES | Definido; no reescribió informe en prueba |
| integrador_tecnico_editorial | APTO | Caso C plan |
| auditor_qa | APTO | Caso B solo lectura |
| coordinador | APTO_CON_AJUSTES | Necesario en multiagente; mantener delgado |

**Veredicto de infraestructura V1:** **APTO_CON_AJUSTES** para uso controlado en pruebas y prompts. **No APTO aún** como única fuente productiva que reemplace `.claude/skills` / `AGENTS.md` sin el párrafo de puntero aprobado.

---

## Skills (detalle)

### auditar_entregable_experimental

| Campo | Valor |
| --- | --- |
| prueba | Revisión cruzada con QA_FINAL F25 y v2.1 |
| resultado | Procedimiento alineado |
| obedecidas | experimental, no auto-aprobar |
| omitidas | ejecución completa de checklist en un pack nuevo de infra |
| contexto | medio |
| duplicaciones | solapa con INFORME_QA (aceptable: skill vs plantilla) |
| errores | ninguno bloqueante |
| riesgo | bajo |
| correcciones | añadir ejemplo relleno en plantilla |
| aptitud | **APTO** |

### qa_pdf_pagina_por_pagina

| Campo | Valor |
| --- | --- |
| prueba | Caso B: 10 páginas renderizadas; p.1 y p.3 inspeccionadas |
| resultado | PASS |
| obedecidas | venv, no editar PDF, PNG en carpeta infra |
| omitidas | inspección exhaustiva de las 10 PNG al máximo detalle (muestra 2 + metadata de las 10) |
| contexto | medio-alto (imágenes) |
| duplicaciones | con skill Claude datagastro-qa-pdf |
| errores | ninguno |
| riesgo | divergencia Claude vs Codex si no se exporta |
| correcciones | sincronizar a agent_skills en promoción |
| aptitud | **APTO** |

### crear_paquete_revision_sanitizado

| Campo | Valor |
| --- | --- |
| prueba | Lectura de packs REVISION_* existentes |
| resultado | Patrón validado; no se creó ZIP nuevo de producto Polos |
| aptitud | **APTO_CON_AJUSTES** |

### auditar_git_y_archivos_protegidos

| Campo | Valor |
| --- | --- |
| prueba | git status de esta tanda; no se recalcularon árboles F25 de 27 archivos |
| resultado | Reglas claras; verificación parcial |
| aptitud | **APTO_CON_AJUSTES** |

### crear_manifest_hashes_metadata

| Campo | Valor |
| --- | --- |
| prueba | Manifests origen + packing de esta infra (script) |
| aptitud | **APTO_CON_AJUSTES** |

### integrar_handoffs

| Campo | Valor |
| --- | --- |
| prueba | Casos A y C + plantillas |
| aptitud | **APTO** |

### validar_metricas_y_kpis

| Campo | Valor |
| --- | --- |
| prueba | Lectura de kpis_lock_preliminar (existencia); no validate_kpis.py end-to-end |
| aptitud | **APTO_CON_AJUSTES** |

### transformar_cartografia_a_presentacion

| Campo | Valor |
| --- | --- |
| prueba | Caso D PM analítica vs presentación |
| aptitud | **APTO** |

### gestionar_decisiones_humanas

| Campo | Valor |
| --- | --- |
| prueba | Matriz v2.1 + DECISIONES_Y_ADVERTENCIAS HANDOFF_FABLE |
| aptitud | **APTO** |

### auditar_evidencia_documental

| Campo | Valor |
| --- | --- |
| prueba | Caso A REC-R02 + inventario URLs del pack |
| aptitud | **APTO** |

---

## Agentes (detalle)

### investigador_documental

- Prueba: Caso A. Resultado PASS.  
- Obedecidas: no geometría, REC-R02, handoff.  
- Aptitud: **APTO**

### auditor_metodologico

- Prueba: solo revisión de definición + lectura de advertencias v2.1 (“estabilidad ≠ elegibilidad”).  
- Sin corrida de sensibilidad nueva.  
- Aptitud: **APTO_CON_AJUSTES**

### cartografo_territorial

- Prueba: Caso D. PASS sin regenerar mapas.  
- Aptitud: **APTO**

### editor_institucional

- Prueba: definición 1.1 + hallazgo de portada Caso B (feedback al editor, no reescritura).  
- Aptitud: **APTO_CON_AJUSTES** (falta prueba de regeneración de informe en línea paralela)

### integrador_tecnico_editorial

- Prueba: Caso C plan. PASS.  
- Aptitud: **APTO**

### auditor_qa

- Prueba: Caso B. Solo lectura + informe. PASS.  
- Aptitud: **APTO**

### coordinador

- Evaluación: necesario si ≥2 roles; no en mono-tarea.  
- Riesgo: inflar el rol.  
- Aptitud: **APTO_CON_AJUSTES**

---

## Consumo de contexto (cualitativo)

| Artefacto | Tokens relativos |
| --- | --- |
| Política | bajo |
| Una skill | bajo-medio |
| Un agente + 2 skills + política | medio |
| AGENTS.md completo + Cowork | alto (problema preexistente) |
| 10 skills de una vez | alto — **no cargar todas** |

---

## Duplicaciones detectadas

1. QA PDF: skill V1 vs `.claude/skills/datagastro-qa-pdf`.  
2. Informes: skill Claude ampliada vs copias agents.  
3. Plantilla INFORME_QA vs skill auditar_entregable (complementarias).

---

## Correcciones necesarias antes de “producción”

1. Aprobar y aplicar **solo** párrafos de puntero en AGENTS.md / CLAUDE.md.  
2. Script `check_skills_parity.py` entre copias productivas.  
3. Exportar qa-pdf + plantilla DGDGAS a capa Codex (`agent_skills`).  
4. Caso extra: `validate_kpis` sobre un lock real.  
5. No crear `.claude/agents/` hasta schema verificado y permisos acotados.  
6. Resolver working tree `M .claude/settings.json` (ya existía; no es de este paquete) con auditoría aparte.

---

## Conclusión

La V1 **funciona como capa documental controlada** y superó los cuatro casos de prueba sin tocar finales.  
**No** sustituye aún la disciplina operativa diaria de Claude/Codex sin los punteros y la paridad de skills productivas.
