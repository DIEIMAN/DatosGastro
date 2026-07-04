# Fase 5 — Polos a documentar (PolosGastro)

Fecha: 2026-06-30.

Polos con evidencia débil, fuentes flojas, dudas de clasificación o documentación pendiente, con
**qué falta** y **qué hacer** usando solo las fuentes ya disponibles en el repo. **No se inventan
fuentes, citas ni evidencia.** Las búsquedas web son **sugerencias**; no se ejecutan en esta fase
(requieren autorización explícita de Diego y salir del repo).

Base: `FASE_5_UNIVERSO_CONSOLIDADO_POLOS.md` (estado de documentación + prioridad) y
`fuentes_externas/BUSQUEDAS_COMPLEMENTARIAS_PENDIENTES.md` (búsquedas ya listadas).

---

## 1. Tabla de polos a reforzar

Ordenados por prioridad de revisión.

| Polo | Grupo actual | Problema | Qué evidencia falta | Fuentes existentes | Recomendación |
| --- | --- | --- | --- | --- | --- |
| **Paternal** | emergente | URL pendiente (PX025A); solo contexto del Distrito del Vino, sin fuente específica del circuito gastronómico | Fuente que documente el circuito/oferta gastronómica de Paternal, no el distrito temático del vino | Distrito del Vino (turismo); Plan oferta turística 2023 (turismo); TimeOut genérica (CM012, `requiere_revision_url`) | Mantener como **candidato débil**. No elevar. Cerrar PX025A o asumir pendiente |
| **García del Río** | anexo | URL pendiente (PX024B); fuente periodística (Clarín, Bulevar García del Río) no verificable | Verificar la nota de Clarín o hallar fuente alternativa del Bulevar García del Río | Oferta gastronómica BA Data (datos_abiertos); Clarín Bulevar García del Río (CM011, `requiere_revision_url`) | Mantener en **anexo** con prudencia. No mapear como área cerrada |
| **Federico Lacroze** | no incluir | URLs pendientes (PX023A/B); sin fuente verificable del tramo | Cualquier fuente específica del corredor Federico Lacroze (Libertador→Cabildo) | Sin fuente verificable; Clarín antigua (CM010, `requiere_revision_url`) | Mantener **fuera**. No avanzar hasta tener fuente |
| **Av. Boedo** | no incluir | Solo fuentes culturales/históricas; sin corredor gastronómico documentado | Fuente que valide oferta/circuito gastronómico (no identidad cultural barrial) | 20 h Avenida Boedo (turismo); La ruta del fileteado (turismo); ambas `requiere_revision` | Mantener **fuera**. Es identidad cultural, no polo gastronómico |
| **Bajo Belgrano** | no incluir | Mención indirecta dentro de Belgrano; sin fuente propia | Fuente específica que distinga Bajo Belgrano del Barrio Chino / Belgrano | La Nación 60% (periodística); Belgrano Circuito 2 (turismo, `requiere_revision`) | Mantener **fuera**. Riesgo de duplicar con Barrio Chino |
| **Villa Pueyrredón / Av. San Martín** | no incluir | Hito puntual (La Nueva Andaluza); sin corredor validado | Fuente de corredor gastronómico sobre Av. San Martín | Oferta BA Data (datos_abiertos); La Nueva Andaluza (turismo) | Mantener **fuera**. Hito ≠ corredor |
| **Av. Corrientes** | emergente | 1 fuente media + 2 `requiere_revision_url` (clarín no abrió) | Verificar las fuentes oficiales (Calle Corrientes / pizzerías) y separar tramo de Abasto | A night of theatre and pizza (turismo); Con quien quieras (turismo); Calle Corrientes + pizzerías CM003/CM004 (oficiales) | **Incluir secundario** (eje cultural-gastronómico). Verificar CM003/CM004 antes de citar |
| **Belgrano R** | anexo | Señal barrial, sin polo delimitado | Fuente que documente oferta gastronómica concreta de Belgrano R | La Nación 60% (periodística); Circuito Sin Pausa (turismo) | Mantener **anexo**. No elevar |

---

## 2. Qué se pudo completar con fuentes del repo (sin web)

Revisando `fuentes_externas_polos_gastro.csv` y los docs de estado de fuentes, **no hay fuentes
sin usar** que cambien la clasificación de estos polos. El trabajo manual de ChatGPT
(CM001–CM012) y Perplexity ya se incorporó:

- **Av. Corrientes** — ya tiene las fuentes oficiales CM003 (Calle Corrientes) y CM004 (pizzerías
  de Corrientes), verificadas. Refuerzan el eje cultural-gastronómico. El problema restante es
  solo de redacción (separar tramo de Abasto), no de falta de fuente. → su debilidad es
  parcialmente formal; con CM003/CM004 podría considerarse **media**, pero se deja **débil** por
  prudencia hasta validar el recorte territorial.
- **García del Río / Federico Lacroze / Paternal** — las fuentes nuevas (clarín, TimeOut) quedaron
  como `requiere_revision_url` porque clarin.com no abre por WebFetch. **No** se pueden cerrar sin
  verificación manual o web autorizada.

> Conclusión: con los recursos actuales del repo, **no se puede cerrar más evidencia** sin
> búsqueda web autorizada o verificación manual de URLs. La documentación queda en su estado
> actual, trazada.

---

## 3. Búsquedas web sugeridas (NO ejecutadas)

Ya existe un listado por polo en
[`fuentes_externas/BUSQUEDAS_COMPLEMENTARIAS_PENDIENTES.md`](fuentes_externas/BUSQUEDAS_COMPLEMENTARIAS_PENDIENTES.md).
Prioridad para esta fase (polos de prioridad alta/media):

- **Paternal**: `"La Paternal circuito gastronómico"`, `"Paternal restaurantes Buenos Aires"`,
  `site:buenosaires.gob.ar Paternal gastronomia`.
- **García del Río / Saavedra**: `"García del Río polo gastronómico Saavedra"`,
  `"Bulevar García del Río restaurantes"`, `site:buenosaires.gob.ar Saavedra gastronomia`.
- **Federico Lacroze**: `"Avenida Federico Lacroze polo gastronómico"`,
  `"Federico Lacroze restaurantes Belgrano Colegiales"`.
- **Av. Corrientes / Abasto**: verificar `"Calle Corrientes" gastronomía site:buenosaires.gob.ar`
  y delimitación del tramo respecto de Abasto.
- **Av. Boedo / Bajo Belgrano / Villa Pueyrredón**: ver el listado completo en el doc citado.

> Verificación manual pendiente (sin web): las URLs de **clarin.com** (CM006, CM010, CM011) que no
> abren por WebFetch. Abrirlas a mano confirmaría García del Río y reforzaría Chacarita / Federico
> Lacroze.

---

## 4. Reglas aplicadas

- No se inventaron fuentes ni citas.
- No se ejecutó búsqueda web (requiere autorización explícita).
- No se cambió ninguna clasificación de polo en esta fase.
- Lo que falta queda marcado como **pendiente**, no completado a la fuerza.
