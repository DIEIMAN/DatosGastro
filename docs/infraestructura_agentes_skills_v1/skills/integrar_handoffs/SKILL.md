---
name: integrar_handoffs
description: Redactar, fusionar y consumir handoffs entre agentes/sesiones/herramientas sin pisar carpetas ajenas ni reabrir decisiones firmadas por accidente.
version: 1
---

# integrar_handoffs

**Política:** §§10–12.  
**Reglas:** R-HO-01, R-MA-01, R-MET-03.  
**Referencia:** `docs/revisiones/HANDOFF_*.md`;  
`docs/polos_gastro/experimentos/consolidacion_editorial_pre_informes_v1/PLAN_INTEGRACION_RESULTADOS_CODEX_FABLE.md`.

## Propósito

Preservar continuidad y reglas de higiene cuando el trabajo cruza Claude, Codex, Grok u otro rol.

## Cuándo usarla

- Al iniciar tarea que continúa trabajo previo.  
- Al cortar sesión.  
- Al integrar resultados de un agente técnico en capa editorial (o viceversa).

## Cuándo no usarla

- Para reescribir la historia de un paquete cerrado sin nota de versión.  
- Para “integrar” corridas a medio terminar.

## Insumos requeridos

- Handoffs existentes relevantes.  
- Rutas exclusivas de cada productor.  
- Registro de decisiones humanas si aplica.

## Rutas permitidas

- Lectura de handoffs y entregables finales con QA.  
- Escritura:  
  - `docs/revisiones/HANDOFF_*.md` (continuidad global), y/o  
  - `docs/.../<paquete>/HANDOFF_*.md`.

## Rutas prohibidas

- Escribir en la carpeta de trabajo activa de otro agente.  
- Modificar Fase 25/finales “al integrar”.

## Procedimiento

1. Leer handoff más reciente del tema + política.  
2. Inventariar entregables del productor: solo los con QA_FINAL o equivalentes.  
3. Mapear qué documento del consumidor se actualiza (tabla de integración).  
4. Detectar contradicciones con decisiones firmadas → nota, no auto-revert.  
5. Actualizar o crear HANDOFF con: hecho / no hecho / rutas / pendientes / prohibiciones.  
6. Dejar explícito el dueño de la siguiente acción.

## Criterios de aceptación

- [ ] Un lector nuevo puede retomar en ≤10 minutos.  
- [ ] Rutas absolutas o repo-relativas verificables.  
- [ ] Sin pisar carpetas ajenas.  
- [ ] Decisiones firmadas intactas o escaladas.

## Outputs obligatorios

- Archivo `HANDOFF_*.md`.  
- Si integración editorial: nota de qué docs se tocarán tras aprobación.

## Errores frecuentes

- Handoff solo narrativo sin rutas.  
- Integrar números sin validar KPIs.  
- Reabrir DH/DEC en el mismo párrafo de “continuidad”.

## Checklist de QA

- Estado.  
- Rutas.  
- Pendientes humanos vs técnicos.  
- Qué no se tocó.

## Formato del handoff

```markdown
# HANDOFF — <tema> — <fecha>
## Contexto
## Hecho
## No hecho / fuera de alcance
## Rutas
## Decisiones firmadas a respetar
## Contradicciones (si hay)
## Próximo dueño
## Prohibiciones
```

## Formato de respuesta final

Enlace al handoff + 5 viñetas de estado + próximo dueño.

## Ejemplo breve

Codex termina repeticiones v2 → Fable actualiza plan de integración y handoff en `docs/revisiones/` sin tocar carpeta `pipeline_hibrido_repeticiones_v2/` de scripts de Codex.

## Reglas de seguridad

Política §§10–12, 14.

## Autorización humana

- Ejecutar la integración que reabre una DEC firmada.  
- Borrar handoffs previos.
