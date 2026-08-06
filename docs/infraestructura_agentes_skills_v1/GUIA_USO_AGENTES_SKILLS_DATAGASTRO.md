# Guía de uso — agentes y skills DataGastro V1

**Paquete:** `docs/infraestructura_agentes_skills_v1/`  
**Política obligatoria:** `POLITICA_OPERATIVA_DATAGASTRO.md`

---

## 1. Cómo elegir agente

| Si la tarea es… | Agente |
| --- | --- |
| Buscar/citar fuentes, matrices, REC-R02 | `investigador_documental` |
| Robustez, cobertura, sobrelectura | `auditor_metodologico` |
| GeoJSON, mapas, analítica vs presentación | `cartografo_territorial` |
| Informe DGDGAS, lenguaje, YAML editable | `editor_institucional` |
| Unir handoffs, placeholders, plan versión nueva | `integrador_tecnico_editorial` |
| Cierre independiente, PDF, hashes, ZIP, git | `auditor_qa` |
| Varios roles / paralelo / rutas exclusivas | `coordinador` (liviano) |
| Una sola skill clara | No hace falta agente: invocá la skill |

---

## 2. Cómo invocar una skill

1. Abrir `skills/<nombre>/SKILL.md`.  
2. Cumplir insumos y rutas permitidas.  
3. Ejecutar el procedimiento.  
4. Entregar outputs obligatorios + handoff si aplica.

En Claude Code (skills productivas): además pueden activarse por descripción las de `.claude/skills/`. Las V1 se invocan **por ruta** hasta promoción.

---

## 3. Trabajo en paralelo

1. Coordinador (o el humano) asigna **carpetas exclusivas** por agente.  
2. Nadie escribe en la carpeta del otro.  
3. Se intercambia solo entregable con QA o handoff.  
4. Integrador consolida en **línea nueva**.

---

## 4. Evitar que agentes se pisen

- Nombres de paquete con sufijo de agente o fecha.  
- Lista PROTECTED al inicio.  
- Prohibido `git add .`.  
- Integrador no “arregla” el origen.

---

## 5. Cuándo pedir QA independiente

- Siempre que haya PDF, ZIP de revisión o cifras canónicas.  
- Siempre antes de mostrar a jefatura.  
- El productor **no** se auto-aprueba en definitivo.

---

## 6. Cuándo escalar a decisión humana

- Reabrir DEC/DH.  
- Cambiar `kpis_lock` canónico.  
- Promover experimental → oficial.  
- Places/API, commit, borrar archivos, tocar pipeline F01–F05.  
- Contradicción técnica vs decisión firmada.

---

## 7. Cómo entregar un handoff

Usar plantillas en `plantillas/`:

- documental / metodológico / cartográfico / editorial / integración  
- cierre: `INFORME_QA.md`

Completar: origen, destino, archivos, cifras, prohibiciones, hashes, git.

---

## 8. Incorporar un agente nuevo

1. Redactar `agents/<rol>.md` con misión, skills, puede/no puede, rutas.  
2. Mapear reglas en la matriz.  
3. Probar con un caso en `outputs/infraestructura_agentes_skills_v1/casos_prueba/`.  
4. Evaluar en `EVALUACION_...` antes de usarlo en serio.  
5. **No** copiar a `.claude/agents/` sin propuesta de permisos.

---

## 9. Actualizar una skill

1. Editar canónico en `skills/<nombre>/SKILL.md` (V1) o `docs/skills_claude/` (legacy).  
2. Subir `version`.  
3. Si hay copias productivas: actualizar **todas** o ninguna (paridad).  
4. Sin symlinks en Windows.

---

## 10. Desactivar la infraestructura

- No borrar: dejar de citar el paquete en prompts.  
- No aplicar las propuestas a AGENTS.md/CLAUDE.md.  
- Seguir usando solo guardrails + `.claude/skills` + `agent_skills` como antes.  
- Los archivos V1 pueden permanecer como docs.

---

## 11. Claude Code

```text
Leé docs/infraestructura_agentes_skills_v1/POLITICA_OPERATIVA_DATAGASTRO.md
y agents/auditor_qa.md.
Aplicá skills/qa_pdf_pagina_por_pagina y auditar_entregable_experimental
sobre <ruta>. Solo lectura del entregable. Escribí INFORME_QA en
outputs/infraestructura_agentes_skills_v1/...
```

---

## 12. Codex

```text
Seguí AGENTS.md y
docs/infraestructura_agentes_skills_v1/POLITICA_OPERATIVA_DATAGASTRO.md.
Rol: agents/integrador_tecnico_editorial.md.
Skill: integrar_handoffs.
Insumo solo lectura: <pack>.
Salida solo en outputs/infraestructura_agentes_skills_v1/...
No git add, no commit, no modificar el pack origen.
```

---

## 13. Prompts cortos (reemplazan prompts largos)

### A. Evidencia

```text
Rol investigador_documental. Política V1. Pack: REVISION_EVIDENCIA_DOCUMENTAL_POLOS_V1.
Inventariá correcciones críticas (incl. REC-R02). Handoff plantilla documental.
No editar el pack.
```

### B. QA PDF

```text
Rol auditor_qa. Skill qa_pdf_pagina_por_pagina.
PDF: <ruta>. PNG a outputs/infraestructura_agentes_skills_v1/tmp_qa/.
No editar el PDF. INFORME_QA con pendientes de integración.
```

### C. Integración

```text
Rol integrador_tecnico_editorial. Leé HANDOFF_FABLE v2.1 y matriz decisiones.
Plan de integración en línea nueva (solo plan). No modificar v2.1 ni F25.
```

### D. Cartografía

```text
Rol cartografo_territorial. Compará capa analítica vs presentación PM v2.1.
Checklist de transformación. No regenerar mapas.
```

### E. Editorial

```text
Rol editor_institucional. Política + decisiones firmadas.
Línea paralela solo. No alterar métricas ni geometrías. QA PDF al final vía auditor_qa.
```

---

## 14. Orden típico multiagente

1. Coordinador (si aplica)  
2. Especialistas en paralelo (carpetas exclusivas)  
3. Integrador (línea nueva)  
4. Editor (si falta relato)  
5. Auditor QA  
6. Diego  

---

*Fin de la guía V1.*
