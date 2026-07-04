# Auditoría visual de gráficos PolosGastro

Fecha de corte: 2026-06-29.

Evaluación de los 6 PNG en `outputs/polos_gastro/graficos/`, generados por
`scripts/polos_gastro/generar_mapa_conceptual_polos_gastro.py`. No se rediseñó ningún gráfico
en esta fase; esto es solo diagnóstico previo a la propuesta visual.

Paleta institucional usada (consistente en todos): núcleo `#275DAD` (azul), zona relevante
`#2A9D8F` (verde), emergente `#E9B44C` (amarillo), anexo `#7D8597` (gris), no incluir
`#C44536` (rojo). Todos los gráficos llevan pie con base (32 polos), fuente y fecha de corte.

---

## 1. `universo_polos_por_grupo.png`

Barras horizontales: 6 / 5 / 9 / 7 / 5 por grupo.

- **Sirve para informe:** sí.
- **Solo metodología interna:** no, es presentable.
- **Visualmente claro:** sí. Orden lógico, etiquetas de valor visibles, sin saturación.
- **Saturado:** no.
- **Problemas de lectura:** ninguno relevante.
- **Requiere rediseño:** no. Ajuste menor opcional: paleta secuencial por jerarquía en lugar
  de colores categóricos, y subtítulo aclarando "jerarquía metodológica, no intensidad".
- **Conservar:** sí.
- **Versión más estética futura:** opcional (branding DataGastro), no urgente.

## 2. `precision_delimitacion_polos.png`

Barras verticales: alta 3 · media 11 · baja 16 · sin delimitación 2.

- **Sirve para informe:** sí — es el gráfico que justifica por qué no hay polígonos cerrados.
- **Solo metodología interna:** no, es muy útil para el lector ejecutivo.
- **Visualmente claro:** sí.
- **Saturado:** no.
- **Problemas de lectura:** ninguno.
- **Requiere rediseño:** no. Mejora opcional: usar gradiente de un solo color (de alta a baja)
  para reforzar que es una escala ordinal, no categorías independientes.
- **Conservar:** sí.
- **Versión más estética futura:** opcional.

## 3. `familias_territoriales_polos.png`

Barras horizontales apiladas por grupo, 8 familias.

- **Sirve para informe:** sí, con cuidado.
- **Solo metodología interna:** parcialmente — es denso para un lector no técnico.
- **Visualmente claro:** mayormente. La leyenda de 5 colores ayuda.
- **Saturado:** moderado. Las barras apiladas con totales bajos (2–7) y 5 segmentos posibles
  hacen que algunos segmentos sean muy finos.
- **Problemas de lectura:** el apilado dificulta comparar un mismo grupo entre familias.
  La etiqueta "Corredores emergentes norte-oeste" se parte en dos líneas.
- **Requiere rediseño:** leve. Alternativa recomendada: barras agrupadas o un pequeño heatmap
  familia × grupo, más fácil de leer que el apilado.
- **Conservar:** sí (sirve de insumo aunque se rediseñe).
- **Versión más estética futura:** sí, recomendable.

## 4. `mapa_conceptual_polos_gastro.png` (alias del resumido)

Diagrama esquemático: eje X = grupo, eje Y = familia. Muestra solo núcleo + zona relevante +
corredores conceptuales (~13 casos visibles).

- **Sirve para informe:** sí, como diagrama de orientación (no como mapa real).
- **Solo metodología interna:** puede ir al informe con la advertencia roja que ya trae.
- **Visualmente claro:** sí, está aireado.
- **Saturado:** no.
- **Problemas de lectura:** la caja "No mapeados en esta fase" (esquina inferior derecha)
  **se solapa** con la etiqueta "Avenida Corrientes". Hay que reubicar la caja.
- **Requiere rediseño:** menor (mover la caja de no-mapeados).
- **Conservar:** sí.
- **Nota de redundancia:** es **idéntico** a `mapa_conceptual_polos_gastro_resumido.png`
  (el script genera ambos con `complete=False`). Uno es alias del otro.
- **Versión más estética futura:** sí (ver propuesta visual).

## 5. `mapa_conceptual_polos_gastro_resumido.png`

Idéntico al anterior (mismo contenido). Mismas observaciones.

- **Requiere rediseño:** mismo solapamiento de la caja.
- **Conservar:** sí, pero evaluar consolidar con el alias en fase futura para no duplicar.

## 6. `mapa_conceptual_polos_gastro_completo.png`

Diagrama esquemático con los 27 casos visibles (todo menos los 5 "no incluir").

- **Sirve para informe:** **no en su forma actual** — es de trabajo interno.
- **Solo metodología interna:** sí.
- **Visualmente claro:** parcialmente.
- **Saturado:** sí, en zonas concretas.
- **Problemas de lectura:**
  - En el cuadrante "Emergente/candidato" × familia "Corredores emergentes norte-oeste" se
    amontonan DoHo, Villa Crespo, Villa Urquiza, Paternal y Colegiales; las etiquetas chocan.
  - La caja "No mapeados" tapa la etiqueta "Abasto".
  - Mezcla 27 casos de muy distinta jerarquía con el mismo peso visual.
- **Requiere rediseño:** sí, claramente (separación de etiquetas, jitter mayor, o paginar por
  familia / por grupo).
- **Conservar:** sí, como insumo de revisión interna; no publicar.
- **Versión más estética futura:** sí, prioritaria si se quiere una versión completa legible.

---

## Síntesis

| Gráfico | ¿Informe? | ¿Claro? | ¿Saturado? | ¿Rediseño? | Conservar |
| --- | --- | --- | --- | --- | --- |
| universo_por_grupo | Sí | Sí | No | No (opcional) | Sí |
| precision_delimitacion | Sí | Sí | No | No (opcional) | Sí |
| familias_territoriales | Sí (con cuidado) | Casi | Moderado | Leve | Sí |
| mapa_conceptual (alias) | Sí | Sí | No | Menor (caja) | Sí |
| mapa_conceptual_resumido | Sí | Sí | No | Menor (caja) | Sí |
| mapa_conceptual_completo | No (interno) | Parcial | Sí | Sí | Sí (interno) |

**Listos para informe (con ajustes menores):** universo_por_grupo, precision_delimitacion,
mapa_conceptual resumido.
**Rediseñar antes de publicar:** familias_territoriales (leve), mapa_conceptual_completo (mayor).
**Correcciones menores muy seguras pendientes (no aplicadas aún):** reubicar la caja
"No mapeados" para que no tape etiquetas. Se deja para la fase de rediseño visual junto con la
decisión de simbología, para no regenerar los PNG de forma aislada.

> Ningún gráfico es un mapa cartográfico real. Todos son diagramas conceptuales o de barras.
