# Fase 5 — Criterio de uso de visuales (PolosGastro)

Fecha: 2026-06-30.

Decisión de Diego (2026-06-30): **dejar de priorizar gráficos decorativos.** Los mapas
conceptuales y los gráficos de barras no convencen visualmente. **No se borran**: pasan a
material experimental/interno y **no se usan como base principal del informe**, salvo que aparezca
una forma mucho mejor de representar esa información.

Este documento **solo clasifica**. No modifica ni borra ningún archivo de visuales.

---

## A. Usar o mantener como base (informe)

Mapas territoriales reales sobre CABA, con barrios/comunas oficiales:

| Archivo | Ubicación | Por qué se mantiene |
| --- | --- | --- |
| `mapa_estatico_caba_polos_gastro_nucleo_v1.png` | `outputs/polos_gastro/graficos/fase4a/` | Mapa territorial real (barrios oficiales). Versión limpia: núcleo + zonas relevantes. Legible. **Candidato fuerte para el cuerpo del informe.** |
| `mapa_estatico_caba_polos_gastro_v1.png` | `outputs/polos_gastro/graficos/fase4a/` | Mapa territorial real con núcleo + relevantes + candidatos. Útil como panorama general, revisando que no quede sobrecargado. |

**Insumos para mejorarlos / generar nuevos (Fase 5, Tarea 6):**
- `PolosGastro/cartografia/barrios_caba.geojson` (48 barrios, Buenos Aires Data).
- `PolosGastro/cartografia/comunas_caba.geojson` (15 comunas).
- `outputs/polos_gastro/base_delimitacion_preliminar_polos_gastro.csv` (barrio/comuna por polo).
- Script base: `scripts/polos_gastro/cartografia/generar_visuales_polos_gastro_fase4a.py`.

**Criterio de calidad para “usar”:** que el mapa ayude a entender **ubicación real** sobre CABA,
con barrios/comunas como referencia, nota metodológica visible (barrio ≠ polo) y sin inventar
delimitaciones oficiales.

---

## B. Dejar como experimento interno / no usar en informe

No borrar. Quedan disponibles como material de trabajo, **fuera** de la base principal del informe.

### Mapas conceptuales (tipo diagrama/red, no geográficos)

| Archivo | Ubicación | Motivo |
| --- | --- | --- |
| `mapa_conceptual_polos_gastro.png` | `outputs/polos_gastro/graficos/` | Diagrama esquemático, no territorial. No convence visualmente. |
| `mapa_conceptual_polos_gastro_resumido.png` | `outputs/polos_gastro/graficos/` | Versión previa del resumido. Reemplazada por el mapa territorial. |
| `mapa_conceptual_polos_gastro_completo.png` | `outputs/polos_gastro/graficos/` | Denso, etiquetas apretadas. Solo interno. |
| `mapa_conceptual_polos_gastro_resumido_v2.png` | `outputs/polos_gastro/graficos/fase4a/` | Mejor resuelto que v1, pero sigue siendo diagrama conceptual. No es base principal. |
| `mapa_conceptual_polos_gastro_completo_v2.png` | `outputs/polos_gastro/graficos/fase4a/` | Denso. Solo interno/anexo. |

### Gráficos de barras / resumen estadístico

| Archivo | Ubicación | Motivo |
| --- | --- | --- |
| `universo_polos_por_grupo.png` | `outputs/polos_gastro/graficos/` | Barras simples (conteo por grupo). Aporta poco; se reemplaza por tabla. |
| `universo_polos_por_grupo_v2.png` | `outputs/polos_gastro/graficos/fase4a/` | Rediseño del anterior; sigue siendo decorativo para el informe. |
| `precision_delimitacion_polos.png` | `outputs/polos_gastro/graficos/` | Barras de precisión; mejor explicado en texto/tabla. |
| `precision_delimitacion_polos_v2.png` | `outputs/polos_gastro/graficos/fase4a/` | Rediseño; idem. |
| `familias_territoriales_polos.png` | `outputs/polos_gastro/graficos/` | Barras apiladas poco claras. |
| `familias_territoriales_polos_v2.png` | `outputs/polos_gastro/graficos/fase4a/` | Barras agrupadas; mejor que v1 pero no aporta lectura territorial. |

---

## C. Reemplazos sugeridos (en vez de los gráficos descartados)

La información de los gráficos de barras se transmite mejor con **tablas limpias** (ya presentes
en la auditoría y en el universo consolidado) y con los **mapas territoriales**:

- "Universo por grupo" → tabla de distribución (6/5/9/8/4) en el informe. No hace falta gráfico.
- "Precisión de delimitación" → columna en la tabla del universo + nota metodológica que explica
  por qué no se dibujan polígonos cerrados.
- "Familias territoriales" → una sección por familia con su mini-tabla de polos (estructura del
  `PLAN_ENSAMBLADO_INFORME_POLOS_GASTRO.md`), apoyada en los mapas por grupo de la Tarea 6.

---

## D. Reglas para visuales nuevos (Fase 5)

- Mapas territoriales sobrios sobre cartografía oficial (barrios/comunas).
- Puntos/centroides aproximados **siempre aclarados** como aproximación.
- Barrios/comunas como **referencia**, no delimitación de polos.
- **No** mapas conceptuales tipo red.
- **No** gráficos de barras salvo que estén claramente justificados y bien resueltos.
- **No** Google Places como base pública; **no** coordenadas Google en mapas públicos.
- Si un polo no tiene geometría suficiente, marcarlo **pendiente** y no inventar.

> Resumen: el informe se apoya en **mapas territoriales reales + tablas claras**, no en diagramas
> conceptuales ni barras decorativas.
