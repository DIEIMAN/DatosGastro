---
name: auditar_entregable_experimental
description: Cerrar y auditar un paquete experimental DataGastro (no oficial). Verificar política, limitaciones, no auto-aprobación y checklist de entrega. Usar al finalizar experimentos Polos/Cafecito/Mercados o packs de revisión.
version: 1
---

# auditar_entregable_experimental

**Política:** aplicar siempre `docs/infraestructura_agentes_skills_v1/POLITICA_OPERATIVA_DATAGASTRO.md`.  
**Reglas:** R-PAR-01, R-LIM-01, R-MET-02, R-MA-02 (ver `MATRIZ_REGLAS_REUTILIZABLES.md`).

## Propósito

Emitir un veredicto de cierre sobre un entregable **experimental**: completitud, trazabilidad, limitaciones, separación de capas y cumplimiento de política — sin promoverlo a oficial.

## Cuándo usarla

- Fin de un experimento o tanda (híbrido, clustering, consolidación editorial, etc.).
- Antes de armar ZIP de revisión humana.
- Cuando un especialista declara “listo para QA”.

## Cuándo no usarla

- Para aprobar PDFs oficiales o Fase 25/26 como oficiales.
- Como sustituto de `qa_pdf_pagina_por_pagina` (la invoca o la exige, no la reemplaza).
- Para reabrir decisiones humanas firmadas.

## Insumos requeridos

- Rutas del paquete: `docs/…`, `outputs/…`, opcional `scripts/…`.
- Declaración de estado: EXPERIMENTAL / NO OFICIAL (o equivalente).
- Lista de superficies protegidas del contexto (si aplica).
- Handoff del productor (si existe).

## Rutas permitidas

- Lectura: paquete bajo auditoría + insumos referenciados en solo lectura.
- Escritura: solo dentro del paquete de QA/cierre, p. ej.  
  `docs/.../<paquete>/QA_FINAL_*.md`,  
  `outputs/.../<paquete>/` (reportes de auditoría).

## Rutas prohibidas

- Datos fuente, pipeline F01–F05, fases oficiales, PDFs finales, `.env`.
- Carpetas de otro agente en curso.
- Google Drive en escritura.

## Procedimiento

1. Leer política y handoff del productor.  
2. Inventariar archivos del paquete (cruzar con manifest si existe; si no, exigir skill de manifest).  
3. Verificar etiqueta experimental y limitaciones documentadas.  
4. Verificar separación analítica vs presentación (si hay mapas/geometrías).  
5. Confirmar que cifras citadas tienen fuente o están marcadas no verificables.  
6. Exigir evidencia de: git/protegidos, privacidad, PDF (si hay), KPIs (si hay).  
7. Confirmar que el productor **no** es quien firma la aprobación definitiva.  
8. Redactar `QA_FINAL_*.md` con veredicto: APTO PARA REVISIÓN HUMANA / OBSERVACIONES / NO APTO.

## Criterios de aceptación

- [ ] Política citada y controles duros OK o fallas listadas.  
- [ ] Limitaciones e incertidumbre declaradas.  
- [ ] No se modificaron finales ni fuentes.  
- [ ] Veredicto no es “oficial” salvo decisión humana previa documentada.  
- [ ] Rol auditor ≠ productor principal (o queda explícito que aprueba Diego).

## Outputs obligatorios

- `QA_FINAL_<paquete>.md` (o actualización del existente).  
- Lista de hallazgos (bloqueantes / menores).  
- Rutas absolutas revisadas.

## Errores frecuentes

- Marcar “OK” sin mirar PDF.  
- Tratar experimento como oficial.  
- Aprobar el propio trabajo.  
- Omitir “qué no se verificó”.

## Checklist de QA

- Controles de política (API, Places, installs, git, fuentes).  
- Manifest presente o justificación.  
- Privacidad publicable.  
- Handoff actualizado.

## Formato del handoff

```markdown
## Handoff — auditoría entregable experimental
- Paquete:
- Veredicto:
- Bloqueantes:
- Menores:
- Pendiente humano:
- Rutas:
```

## Formato de respuesta final

1. Veredicto en una línea.  
2. Tabla controles OK/FAIL.  
3. Hallazgos.  
4. Rutas.  
5. Qué no se tocó.

## Ejemplo breve

Auditar `docs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/` tras construir v2.1: emitir QA_FINAL con “386 protegidos OK”, sin API, sin commit.

## Reglas de seguridad

Ver política §§1–5, 8, 14.

## Autorización humana

- Promover a oficial.  
- Ignorar bloqueantes de privacidad.  
- Commit del paquete.
