# Handoff red team → integrador V3

**De:** `auditor_externo_red_team`  
**Para:** `integrador_tecnico_editorial` (y editor del informe político)  
**Fecha:** 2026-07-11  
**Veredicto:** `APTO_CON_AJUSTES_EDITORIALES`  
**Corrida auditada:** `outputs/polos_gastro/corrida_territorial_v3/` (sin modificaciones)

---

## 1. Qué puede darse por cerrado

| Tema | Estado |
|---|---|
| Polo único Belgrano + BEL-A | Cerrado |
| Tres centralidades; Belgrano R secundario | Cerrado (no promover) |
| Polo único Recoleta + REC-A | Cerrado |
| Nueve núcleos solo analíticos | Cerrado |
| Polo Costanera + 4 componentes + CN_C02 + DEC-10 | Cerrado |
| Evidencia documental V1.1 como base de contraste | Cerrado |
| REC-R02 no publicable | Cerrado |
| Hashes / QA técnico de corrida | Fuera de alcance de este red team; no objetado por contradicción territorial |

---

## 2. Qué debe hacer el integrador (orden sugerido)

1. Leer `VEREDICTO_AUDITORIA_EXTERNA_V3.md` y `RECOMENDACIONES_EDITORIALES_EXTERNAS_V3.md`.  
2. Inventariar assets V3 contra `CONTRATO_OUTPUTS_CARTOGRAFICOS_PARA_INTEGRACION_V3.md` (preintegración).  
3. Aplicar matriz TO-* de textos obsoletos del PDF político heredado (Costanera exploratoria, Recoleta en observación, etc.).  
4. Seleccionar mapas según tabla §3.  
5. Completar KPI lock editorial con cifras del `KPI_LOCK_CARTOGRAFICO_V3.csv` **sin recalcular**.  
6. Insertar **una** nota metodológica (fuentes + no límite oficial + dependencia Costanera).  
7. Regenerar PDF en **línea paralela** (no tocar Fase 25 cerrada / superficies protegidas).  
8. QA visual de PDF (`scripts/qa/pdf_check.py`) — fuera de este handoff, a cargo del flujo de informe.

---

## 3. Selección de mapas (contrato de uso)

| Página / ficha | Asset preferido | Condición |
|---|---|---|
| Belgrano | `mapas/belgrano_02_mapa_presentacion.png` (+ SVG si compone) | Tras ajuste de rótulos / subtítulo |
| Recoleta | `mapas/recoleta_02_mapa_presentacion.png` | Ajuste menor de pie/leyenda |
| Costanera | `mapas/costanera_norte_02_mapa_presentacion.png` | Solo si se leen 4 componentes |
| Apoyo vacíos Costanera | `mapas/costanera_norte_05_vacios_continuidad.png` | Caja metodológica o mitad inferior p.8 |
| Método Recoleta (opcional) | `mapas/recoleta_03_comparativo_modelos.png` | Anexo / no ficha |
| **Prohibidos en cuerpo** | `belgrano_03`, `costanera_norte_03`, `*_04_puntos_cobertura` | Hasta regeneración o leyenda |

Detalle de hallazgos: `QA_VISUAL_EXTERNO_MAPAS_V3.csv`.

---

## 4. Textos mínimos por ficha (listos para adaptar)

### Belgrano

**Título:** Polo Gastronómico Belgrano  

**Bajada:** Unidad con tres centralidades densas de oferta registrada o visible. Belgrano R se mantiene como sector secundario.  

**Pie de mapa:** Delimitación de trabajo del estudio; no es el límite del barrio ni un límite administrativo oficial.  

**No decir:** que el 35 % “demuestra debilidad del polo” sin el marco de centralidades vs. barrio.

### Recoleta

**Título:** Polo Gastronómico Recoleta  

**Bajada:** Un solo polo de fuerte reconocimiento institucional. La geometría refleja la oferta densa y deja huecos en predios no gastronómicos.  

**Pie:** No representa el perímetro barrial ni nueve polos internos.  

**No decir:** cifra de ~150 restaurantes; “nueve polos”.

### Costanera Norte

**Título:** Polo Gastronómico Costanera Norte  

**Bajada:** Estructura multiparte de cuatro componentes discontinuos. Los vacíos son parte de la lógica territorial del frente ribereño.  

**Pie:** Delimitación adoptada por el estudio, actualizable con nueva evidencia; no es límite administrativo oficial.  

**No decir:** informal / ilegal / solo exploratorio / tres sectores principales.

---

## 5. Objeciones que el integrador debe poder responder

Ver filas de alta fuerza en `MATRIZ_OBJECIONES_Y_RESPUESTAS_V3.csv`:

- OBJ-BEL-T01 / OBJ-BEL-P01 (cobertura y listado Turismo BA)  
- OBJ-REC-T01 / OBJ-REC-P02 (envolvente y nueve núcleos)  
- OBJ-CN-T01 / OBJ-CN-P01 / OBJ-CN-P02 (Places, informalidad, mapa multiparte)

---

## 6. Decisiones que siguen en Diego (no resueltas por red team)

1. Arquitectura de páginas para incorporar Recoleta (Opción A/B/C del plan de preintegración).  
2. Firma DH-05 de nombres públicos de centralidades de Belgrano.  
3. Promoción de Belgrano R (recomendación red team y cartógrafo: **no**).  
4. Chip de estado / tipo-madurez de Costanera en el sistema visual del PDF.  
5. Si la regeneración V3 arrastra también assets v2.1 pendientes de otros polos.

---

## 7. Superficies protegidas (recordatorio)

No modificar in-place:

- `docs/polos_gastro/fase25_microajustes_finales_oficina/**`  
- `outputs/polos_gastro/fase25_microajustes_finales_oficina/**`  
- generador Fase 25 y baselines cartográficas cerradas listadas en `PROTECTED_SURFACES.yaml`  
- `PolosGastro/**` (semilla)  
- pipeline general `src/build_*.py`

Trabajar en **línea paralela** V3.

---

## 8. Entregables de esta auditoría

Ruta canónica:

`docs/polos_gastro/auditoria_externa_red_team_v3/`

Espejo:

`outputs/polos_gastro/auditoria_externa_red_team_v3/`

Archivos:

1. `INFORME_RED_TEAM_TERRITORIAL_V3.md`  
2. `MATRIZ_OBJECIONES_Y_RESPUESTAS_V3.csv`  
3. `QA_VISUAL_EXTERNO_MAPAS_V3.csv`  
4. `RECOMENDACIONES_EDITORIALES_EXTERNAS_V3.md`  
5. `VEREDICTO_AUDITORIA_EXTERNA_V3.md`  
6. `HANDOFF_RED_TEAM_INTEGRADOR_V3.md` (este archivo)

---

## 9. Mensaje de cierre para el integrador

La corrida territorial V3 **puede integrarse** al informe político experimental con trabajo editorial y de composición de mapas.  
No reabrir Belgrano / Recoleta / Costanera en lo territorial.  
El cuello de botella es **claridad pública y legibilidad**, no la existencia de los tres polos ni la validez de BEL-A, REC-A y CN-DEC10.
