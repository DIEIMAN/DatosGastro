# Mercados gastronómicos CABA — Ajuste conservador de estado operativo (V2.2)

> Decisión metodológica explícita. **El conteo activo se ajusta de 15 a 12** por criterio
> conservador de estado operativo. Fecha: 2026-06-24.

## 1. La decisión

> **El conteo de mercados gastronómicos activos para conteo pasa de 15 (V2) a 12 (V2.2).**

Tres casos se retiran del conteo activo **por prudencia**, ante señales de estado operativo no
concluyentes:

- **Mercado Soho** (MG-0005)
- **Mercat Caballito** (MG-0014)
- **El Galpón** (MG-0009)

**No se eliminan del universo.** Quedan como **casos gastronómicos relevantes en revisión**
(`en_revision_no_contabilizado_por_prudencia`), en
`mercados_gastronomicos_en_revision_v2_2.csv`. **No son "fuera de alcance".**

## 2. Justificación por caso

- **Mercado Soho:** Google Places lo marca **`CLOSED_PERMANENTLY`** y no hay evidencia reciente
  suficiente que lo contradiga (el documental aporta perfil por Turismo BA, pero dirección/horario
  solo por prensa, sin sitio oficial recuperado). → retirar del conteo hasta validar.
- **Mercat Caballito:** Google Places lo marca **`CLOSED_PERMANENTLY`**; la fuente oficial
  recuperada es solo una **mención en agenda/evento**, sin ficha propia con dirección/horario. →
  requiere validación externa antes de contar.
- **El Galpón:** el **match de Google fue inconsistente** (devolvió un teatro/`event_venue`
  homónimo) y hay señales de situación no clara / posible cierre temporal. → desambiguar el predio
  y validar estado antes de contar.

## 3. Por qué es conservador (y por qué es una fortaleza)

- Una señal de cierre en una sola fuente (Google) **no alcanza** para afirmar que un mercado
  cerró, pero **sí** alcanza para **dejar de afirmar que está activo** sin validar.
- Es preferible **subreportar con transparencia** (12 confirmados + 3 en revisión) que
  **sobrereportar** (15) con casos dudosos.
- La decisión es **reversible y trazable**: si la validación territorial/documental confirma
  actividad, los casos vuelven al conteo.

## 4. Qué NO cambia

- El universo total en alcance sigue siendo **16**.
- Cerrados (1), distritos (2), abastos no gastronómicos (3) y fuera de alcance (2) se mantienen
  diferenciados, sin mezclarse.
- Los posibles omitidos (Google/documental) **no** se suman al conteo.

## 5. Nuevo cuadro de conteo

| Categoría | V2 | V2.2 |
|---|---|---|
| Activos para conteo | 15 | **12** |
| En revisión (no contabilizados por prudencia) | 0 | **3** |
| Cerrados documentados | 1 | 1 |
| Pendientes metodológicos | 0 | 0 |
| Distritos gastronómicos (no mercado) | 2 | 2 |
| Abasto barrial no gastronómico | 3 | 3 |
| Fuera de alcance | 2 | 2 |

## 6. Condición para revertir

Cada caso vuelve a "activo para conteo" con **al menos una** de estas evidencias:
sitio oficial vigente con operación, verificación territorial, o fuente oficial GCBA/Turismo BA
actualizada que confirme estado operativo. Se documenta en la ficha y en el resumen.


---

> **Nota V2.3 (2026-06-24):** Se incorporó una tanda V2.3 de URLs visibles de Perplexity para reforzar trazabilidad documental. No modifica conteos (siguen 12 activos confirmados y 3 en revisión); las fuentes con URL truncada quedan pendientes de verificación. Ver `23_integracion_urls_perplexity_v2_3.md`.
