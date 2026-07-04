# Auditoría integral PolosGastro — pre-informe

Fecha de corte: 2026-06-29.

Esta auditoría revisa el estado completo del subproyecto PolosGastro antes de iniciar
cualquier borrador de informe. **No modifica ni borra archivos** (salvo correcciones menores
de consistencia documentadas en `QA_CONSISTENCIA_UNIVERSO_POLOS_GASTRO.md`, si las hubiera).
No genera PDF, mapas finales, geocodificación ni shapefiles. No toca otros subproyectos
(Cafecito, MercadosGastro, CasasDePastas) ni el pipeline general F01–F05.

Estado en Git: **todo el subproyecto está untracked** (`PolosGastro/`, `docs/polos_gastro/`,
`outputs/polos_gastro/`, `scripts/polos_gastro/`). No hay nada commiteado ni stageado.

---

## 1. Inventario de archivos existentes

### Fuente semilla
- `PolosGastro/Polos gastronómicos.pdf` — PDF inicial (100 KB). Base candidata, no oficial.

### Scripts (`scripts/polos_gastro/`)
- `inventariar_polos_gastro.py` — Fase 1.
- `definir_universo_informe_polos_gastro.py` — universo defendible + nombres públicos.
- `generar_validacion_documental_fase2.py` — Fase 2 (matriz, fichas, fuentes).
- `fase3a_urls_y_delimitacion_textual.py` — Fase 3A (URLs + delimitación textual).
- `generar_mapa_conceptual_polos_gastro.py` — Fase 3B (base mapa conceptual + gráficos).
- `__pycache__/` — caché de Python (no tocar).

### Documentos metodológicos (`docs/polos_gastro/`)
- `DIAGNOSTICO_INICIAL_POLOS_GASTRO.md`
- `INVENTARIO_INICIAL_POLOS_GASTRO.md`
- `LECTURA_INICIAL_POLOS_GASTRO.md`
- `UNIVERSO_DEFENDIBLE_INFORME_POLOS_GASTRO.md`
- `LECTURA_UNIVERSO_INFORME_POLOS_GASTRO.md`
- `FUENTES_Y_TRAZABILIDAD_POLOS_GASTRO.md`
- `AUDITORIA_FASE2_VALIDACION_DOCUMENTAL.md`
- `LECTURA_VALIDACION_DOCUMENTAL_POLOS_GASTRO.md`
- `DELIMITACION_TEXTUAL_PRELIMINAR_POLOS_GASTRO.md`
- `AUDITORIA_MAPA_CONCEPTUAL_FASE3B.md`
- `LECTURA_MAPA_CONCEPTUAL_POLOS_GASTRO.md`
- `ESQUELETO_INFORME_POLOS_GASTRO.md`
- `fuentes_externas/` — 5 documentos (semilla, complementarias, pendientes, reporte 3A, Perplexity).
- `fichas_polos/` — 32 fichas individuales (una por polo).

### Outputs de datos (`outputs/polos_gastro/`)
- 13 CSV (detalle en sección 3).
- `graficos/` — 6 PNG (detalle en `AUDITORIA_VISUAL_GRAFICOS_POLOS_GASTRO.md`).

---

## 2. Qué hace cada script

| Script | Rol | Entradas | Salidas principales |
| --- | --- | --- | --- |
| `inventariar_polos_gastro.py` | Fase 1: lee el PDF semilla, transcribe polos y locales (el PDF no trae tablas estructuradas), marca todo como insumo semilla no validado. | `PolosGastro/*.pdf` | `polos_gastronomicos_base_candidata.csv`, `locales_destacados_por_polo_seed.csv`, `resumen_polos_inicial.csv`, docs de diagnóstico/inventario/lectura inicial. |
| `definir_universo_informe_polos_gastro.py` | Construye el universo defendible y los nombres públicos corregidos. | base candidata + insumos Fase 2 | `universo_informe_polos_gastro.csv`, `nombres_publicos_polos_gastro.csv`, `fuentes_por_familia_territorial.csv`, docs de universo. |
| `generar_validacion_documental_fase2.py` | Fase 2: matriz de validación documental, 32 fichas, normaliza fuentes externas. | matriz Perplexity seed + fuentes | `matriz_validacion_polos_gastro.csv`, `fuentes_externas_polos_gastro.csv`, `resumen_validacion_documental_fase2.csv`, `fichas_polos/*.md`. |
| `fase3a_urls_y_delimitacion_textual.py` | Fase 3A: resuelve URLs pendientes y arma delimitación textual preliminar. | fuentes externas | `base_delimitacion_preliminar_polos_gastro.csv`, doc delimitación, reporte URLs 3A. |
| `generar_mapa_conceptual_polos_gastro.py` | Fase 3B: deriva representación visual sugerida por polo y genera los 6 gráficos. | universo + delimitación + familias | `base_mapa_conceptual_polos_gastro.csv`, `graficos/*.png`, auditoría y lectura del mapa conceptual. |

Todos los scripts son reproducibles, usan `pathlib`, leen/escriben con `utf-8-sig`/`utf-8`,
fijan `FECHA_CORTE = "2026-06-29"` y no dependen de datos privados ni de red.

---

## 3. CSVs existentes y rol de cada uno

| CSV | Filas (sin header) | Rol |
| --- | --- | --- |
| `polos_gastronomicos_base_candidata.csv` | 23 | Base candidata Fase 1 (transcripción del PDF). |
| `locales_destacados_por_polo_seed.csv` | 100 | Locales destacados semilla (cualitativos, no padrón). |
| `resumen_polos_inicial.csv` | 15 | Indicadores resumen Fase 1. |
| `perplexity_matriz_evidencia_seed.csv` | 32 | Matriz semilla Perplexity (sugerencias por polo). |
| `nombres_publicos_polos_gastro.csv` | 32 | Mapeo nombre interno → nombre público corregido. |
| `universo_informe_polos_gastro.csv` | 32 | **Universo defendible**: grupo, evidencia, decisión, riesgo por polo. |
| `matriz_validacion_polos_gastro.csv` | 32 | Validación documental Fase 2 (tipos de fuente, flags). |
| `resumen_validacion_documental_fase2.csv` | 4 | Indicadores resumen Fase 2. |
| `fuentes_externas_polos_gastro.csv` | 80 | **80 fuentes externas** normalizadas con trazabilidad. |
| `base_delimitacion_preliminar_polos_gastro.csv` | 32 | Delimitación textual + precisión + familia. |
| `fuentes_por_familia_territorial.csv` | 32 | Cruce polo → familia territorial (8 familias). |
| `base_mapa_conceptual_polos_gastro.csv` | 32 | Base para visualización conceptual (representación sugerida). |

El universo trabaja siempre con **32 polos** (filas). La base candidata tiene 23 porque los
subpolos de Palermo (Soho, Hollywood, Las Cañitas) y los agregados de Fase 2 (PGF2_*) se
desagregaron después.

---

## 4. Documentos metodológicos existentes

Cubren toda la cadena: diagnóstico e inventario inicial (Fase 1), universo defendible y
trazabilidad de fuentes, validación documental y lectura (Fase 2), delimitación textual y
reporte de URLs (Fase 3A), auditoría y lectura del mapa conceptual (Fase 3B), y el esqueleto
de informe futuro. La carpeta `fuentes_externas/` documenta fuentes semilla verificadas,
complementarias encontradas, búsquedas complementarias pendientes y el reporte de URLs 3A.

---

## 5. Gráficos existentes

6 PNG en `outputs/polos_gastro/graficos/` (evaluación detallada en
`AUDITORIA_VISUAL_GRAFICOS_POLOS_GASTRO.md`):

- `universo_polos_por_grupo.png`
- `precision_delimitacion_polos.png`
- `familias_territoriales_polos.png`
- `mapa_conceptual_polos_gastro.png`
- `mapa_conceptual_polos_gastro_resumido.png`
- `mapa_conceptual_polos_gastro_completo.png`

---

## 6. Conteos principales

| Indicador | Valor |
| --- | --- |
| Polos candidatos (base Fase 1) | 23 |
| Polos en universo defendible | 32 |
| Locales destacados (semilla) | 100 |
| Fuentes externas | 80 |
| Fichas de polos | 32 (una por polo del universo, incluyendo los 4 «no incluir») |

**Universo por grupo de informe** (32):
- núcleo principal: 6
- zona relevante: 5
- emergente/candidato: 9
- anexo: 7
- no incluir por ahora: 5

**Nivel de evidencia**: alta 6 · media 5 · parcial 9 · parcial_baja 7 · insuficiente 5.

**Precisión de delimitación** (32):
- alta: 3
- media: 11
- baja: 16
- sin delimitación: 2

**Familias territoriales** (8):
- corredores_emergentes_norte_oeste: 7
- zona_central (y Recoleta): 5
- oeste_y_barrios_con_oferta: 5
- belgrano_y_norte: 4
- palermo_y_subpolos: 3
- sur_historico_y_tradicional: 3
- cultura_avenidas_y_noches: 3
- zona_costera_y_turistica: 2

---

## 7. Problemas detectados

1. **Redundancia de archivo de gráfico**: `mapa_conceptual_polos_gastro.png` y
   `mapa_conceptual_polos_gastro_resumido.png` son el mismo gráfico (el script genera ambos
   con `complete=False`). El primero es un alias del segundo. No es un error, pero genera
   duplicación. **No borrar**: documentar. Decisión recomendada en sección 10.
2. **Solapamiento de etiquetas en el mapa conceptual completo**: en el cuadrante
   "Emergente/candidato", familia "Corredores emergentes norte-oeste", se amontonan DoHo,
   Villa Crespo, Villa Urquiza, Paternal y Colegiales; las etiquetas chocan entre sí.
   Afecta legibilidad. Es un caso de rediseño para fase futura, no de corrección menor.
3. **Caja "No mapeados" se solapa con casos**: en ambos mapas conceptuales la caja de la
   esquina inferior derecha tapa "Avenida Corrientes" (resumido) y "Abasto" (completo).
4. **Cabecera BOM (`utf-8-sig`)** en la mayoría de los CSV. Es esperado y los scripts lo
   manejan, pero conviene tenerlo presente si un consumidor externo lee los CSV.

---

## 8. Inconsistencias detectadas

Cruce de los 4 archivos de universo por `polo_id`:

- `grupo_informe`: **100% consistente** entre universo, delimitación, mapa conceptual y
  familias (0 discrepancias).
- `familia_territorial`: **100% consistente** entre delimitación, mapa conceptual y familias.
- **Nombres con tilde en `nombre_publico`**: correctos en universo, delimitación, mapa
  conceptual, familias y nombres públicos (Las Cañitas, García del Río, Villa Pueyrredón,
  Microcentro / Centro, etc.).
- **Nombres sin tilde en `matriz_validacion_polos_gastro.csv` (campo `nombre_polo`)**: la
  matriz conserva versiones internas sin tilde ("Las Canitas", "Garcia del Rio",
  "Villa Pueyrredon / Av. San Martin", "Microcentro y Centro", "Parque Saavedra / Garcia del
  Rio"). Es un **campo interno de trabajo**, no el nombre público; no se usa para el informe.
  No es un error funcional, pero conviene documentarlo para no copiar esos strings al informe.
  Ver QA de consistencia.

No se detectaron polos faltantes, duplicados de `polo_id`, ni grupos mal asignados.

---

## 9. Archivos duplicados o redundantes

- `mapa_conceptual_polos_gastro.png` ≡ `mapa_conceptual_polos_gastro_resumido.png`
  (mismo contenido; el primero es alias). **Conservar ambos por ahora**, son output del script.

No hay CSV ni documentos duplicados.

---

## 10. Archivos que conviene conservar

Todos. En particular:
- Los 12 CSV de datos (cadena de trazabilidad completa Fase 1 → 3B).
- Las 32 fichas de polos.
- Los 5 documentos de `fuentes_externas/` (incluyen las búsquedas pendientes, clave para
  la próxima fase de fuentes).
- El `ESQUELETO_INFORME_POLOS_GASTRO.md` (estructura del futuro informe).
- Los 5 scripts (reproducibilidad).

---

## 11. Archivos que NO conviene tocar

- `PolosGastro/Polos gastronómicos.pdf` — fuente semilla. No modificar.
- `scripts/polos_gastro/__pycache__/` — caché. No borrar.
- Los CSV de universo ya validados, salvo correcciones menores documentadas en el QA.
- Cualquier archivo fuera de `*/polos_gastro/` y `PolosGastro/` (otros subproyectos / pipeline).

---

## 12. Riesgos antes de informe

1. **Confundir el universo con un padrón**: los 32 polos son universo defendible de lectura,
   no locales activos. Los 100 locales son menciones cualitativas, no censo.
2. **Falsa precisión cartográfica**: con 16 polos de precisión baja y 2 sin delimitación, no
   se pueden dibujar polígonos cerrados para todo el universo.
3. **4 URLs pendientes** (PX023A, PX023B, PX024B, PX025A) bloquean delimitación fuerte de
   Federico Lacroze / Libertador a Cabildo, Parque Saavedra / García del Río y Paternal.
4. **Subpolos y subzonas**: Palermo Soho/Hollywood/Las Cañitas deben presentarse como
   subpolos de Palermo; Barrio Chino como subzona dentro de Belgrano. Riesgo de tratarlos
   como barrios independientes.
5. **Familias ≠ límites administrativos**: las 8 familias ordenan la lectura, no son
   polígonos ni comunas.

---

## 13. Qué falta antes de escribir el borrador

1. **Decidir la capa cartográfica**: si el informe usará mapa real (USIG/Leaflet, GeoPandas)
   o se mantiene en diagrama conceptual. Ver `cartografia/`.
2. **Definir simbología institucional** (paleta DataGastro, marcadores por nivel de evidencia).
3. **Cerrar — o asumir como definitivamente pendientes — las 4 URLs**.
4. **Rediseñar el mapa conceptual completo** para resolver el solapamiento de etiquetas.
5. **Decidir tratamiento de locales destacados** (anexo cualitativo con advertencia).
6. **Fuentes adicionales** para polos débiles (ver `PEDIDOS_EXTERNOS_PARA_MEJORAR_POLOS_GASTRO.md`).
7. **Definir alcance del informe** (núcleo + relevantes + emergentes; anexos al final).

> **No iniciar el informe final** hasta cerrar las decisiones de cartografía, estilo visual y
> fuentes adicionales.
