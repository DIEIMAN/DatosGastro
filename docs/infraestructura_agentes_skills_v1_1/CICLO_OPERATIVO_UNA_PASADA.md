# Ciclo operativo de una pasada — DataGastro / DGDGAS

**ID:** `CICLO_OPERATIVO_UNA_PASADA`
**Fecha:** 2026-07-14
**Precedencia:** debajo de guardrails y de la política V1.1 (§0); por encima de agentes, skills y
tareas puntuales. Complementa la política, no la reemplaza.
**Definido por:** Diego (principio operativo); redacción técnica de esta versión: Claude.

## 1. El ciclo (regla central)

> **una producción → una auditoría independiente → una corrección puntual → decisión → cierre**

- Un entregable tiene **un productor** y **un revisor independiente**. Nada más.
- El QA automático del productor (self-checks, scripts, render propio) es parte de la
  producción. **No cuenta como auditoría independiente** y no genera paquete propio.
- Después de la auditoría hay **como máximo una corrección puntual**, verificada solo sobre lo
  corregido. No se re-audita todo el entregable ni se audita la auditoría.
- Luego decide Diego (o queda registrado como pendiente humano) y la pieza pasa a CERRADO.
- **Prohibido:** auditorías de auditorías, consolidaciones de consolidaciones, preflights en
  cadena para un mismo paso, contratos nuevos para cambios chicos.

## 2. Estados canónicos

`PREPARACION → LISTO_PARA_AUTORIZACION → EJECUCION → REVISION → CORRECCION → DECISION → CERRADO`

- Cada pieza declara su estado con uno de estos términos, sin porcentajes subjetivos de avance:
  un gate verificable (archivo existe, QA emitido, decisión registrada) es lo único que mueve el
  estado.
- **Regla de dos errores:** si una pieza acumula dos errores materiales después de corregida, no
  se parcha una tercera vez: se **reconstruye desde el último input congelado**. No se
  reconstruye el proyecto entero por un error localizado.

## 3. Fuente vigente única

- Por etapa/subproyecto hay **una sola fuente de estado vigente**. Para Polos INFORMEFINAL:
  `outputs/polos_gastro/INFORMEFINAL/ESTADO_GENERAL_INFORMEFINAL.md` +
  `DECISIONES_CERRADAS_Y_PENDIENTES.md` (raíz de INFORMEFINAL).
- **Ningún mapa, ficha técnica o artefacto histórico es fuente de estatus institucional.** Si un
  artefacto técnico dice "decisión pendiente / no adoptar" y el registro de decisiones dice otra
  cosa, gana el registro; el artefacto se cita solo como evidencia predecisión.
- Todo artefacto no vigente se rotula al citarlo: `HISTORICO`, `EVIDENCIA_TECNICA_PREDECISION` o
  `SUPERSEDIDO`. No se borra ni se reescribe in-place.
- Al iniciar cualquier tarea de Polos: leer primero esas dos fuentes; no reconstruir el estado
  desde el historial del chat.

## 4. Roles (un rol por agente, sin superposición)

| Agente | Hace | No hace |
| --- | --- | --- |
| **Codex** | Producción técnica: scripts, API autorizada, deduplicación, análisis espacial, clustering, mapas. QA automático propio (parte de la producción). | Auditoría independiente de su propio producto; decisiones territoriales. |
| **Claude/Fable** | UNA auditoría independiente (metodológica o visual) del producto terminado; hallazgos priorizados con bloqueantes primero; integración editorial cuando se le asigne. | Repetir el trabajo del productor; re-auditar lo ya auditado; abrir paquetes de reparación en cadena. |
| **Grok** | Investigación documental; registro de decisiones; integración final; actualización de la fuente vigente (una vez por cierre). | Volver a auditar lo auditado; generar consolidaciones intermedias múltiples. |
| **Diego** | Decisiones territoriales e institucionales; autorización de API, gastos, Git y cambios de alcance. | — |
| **ChatGPT** | Coordinación: elegir el siguiente paso, revisar paquetes, redactar prompts breves, cortar ciclos burocráticos. | Producir o auditar contenido él mismo. |

- No usar agentes en paralelo salvo tareas realmente independientes con rutas de escritura
  exclusivas (política §12).
- Cada agente **se detiene al alcanzar su criterio de terminación**. No inventa tareas
  adicionales, no "aprovecha" para mejorar cosas no pedidas, no abre paquetes nuevos por
  iniciativa propia.

## 5. Prompts operativos (formato obligatorio)

Todo prompt operativo entre agentes usa **cinco bloques** y nada más:

1. **Objetivo** — una frase.
2. **Inputs canónicos** — rutas exactas; incluye la fuente vigente de estado.
3. **Acciones** — lista imperativa y acotada.
4. **Prohibiciones** — qué no tocar (protegidas, cerradas, decisiones firmadas).
5. **Criterio de aceptación** — gate verificable que termina la tarea.

Plantilla lista para copiar:
`outputs/polos_gastro/INFORMEFINAL/claude/auditoria_sistema_agentes_skills_v1/PLANTILLA_TAREA_CORTA.md`

## 6. Paquetes y reportes (anti-burocracia)

- Un cambio de ≤5 archivos sobre una pieza existente **se anexa a la carpeta de esa pieza** con
  nota de versión; no se crea paquete nuevo, ni manifest nuevo, ni preflight nuevo.
- Un ciclo completo (producción + auditoría + corrección + cierre) genera **como máximo**:
  1 carpeta de producción, 1 informe de auditoría, 1 nota de corrección, 1 actualización de la
  fuente vigente. Manifest/checksums solo en el cierre, no en cada paso intermedio.
- Los reportes de agentes distinguen siempre **"verificado directamente"** (lo abrí/rendericé/
  ejecuté) de **"según el reporte de X"** (lo afirma otro agente). Nunca presentar lo segundo
  como lo primero.
- Ante archivo faltante o insumo dudoso: detenerse y reportar la ruta exacta; no sustituir con
  memoria del chat ni con archivos "parecidos".

## 7. Qué sigue requiriendo autorización de Diego

Sin cambios respecto de política V1.1 §15: commit/push, APIs pagas (Places), modificar
superficies protegidas o cerradas, reabrir decisiones firmadas, promover a oficial, gastos.
