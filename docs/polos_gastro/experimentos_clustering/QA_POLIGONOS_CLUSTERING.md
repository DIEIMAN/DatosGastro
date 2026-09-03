# QA técnico — Polígonos exploratorios por clustering (PolosGastro)

**Fecha:** 2026-07-07 · Corrida:
`.venv/Scripts/python.exe scripts/polos_gastro/experimentos/generar_poligonos_clustering.py`

## 1–3. Puntos

| Métrica | Valor |
|---|---|
| Puntos cargados | 106 |
| Puntos válidos usados | **93** |
| Descartados: `estado_consolidado = duplicado_probable` | 11 (no doble-contar densidad) |
| Descartados: fuera del polígono de comunas de CABA | 2 |

Detalle de los 2 puntos fuera de CABA:
- Belgrano · lat −34.47960, lon −58.57073 → geolocalizado en provincia (sede errónea,
  estado `vigencia_no_confirmada`).
- Puerto Madero · lat −34.63340, lon −58.34329 → sobre el borde costero/dársenas, fuera del
  polígono de comunas; revisar si es un problema de precisión del límite o de la sede.

## 4–6. Configuración

| Ítem | Valor |
|---|---|
| CRS métrico | EPSG:5347 (POSGAR 2007 / Argentina faja 5) |
| Algoritmo | DBSCAN (scikit-learn 1.9.0), distancia euclidiana en metros, peso uniforme = 1 |
| Grilla probada | eps ∈ {150, 200, 250, 300, 400, 500} × min_samples ∈ {3, 4, 5, 6} (24 combinaciones) |
| Parámetros finales | **eps = 400 m, min_samples = 3** (elección automática según criterio documentado; alternativa viable: 500/3) |

## 7–9. Resultados

| Métrica | Valor |
|---|---|
| Clusters | 12 |
| Ruido / outliers | 44 puntos (47.3 %) |
| Área de polígonos | mín 0.66 ha · mediana 3.71 ha · máx 21.17 ha |

## 10–12. Observaciones de tamaño y mezcla

- **Clusters chicos:** 8 de 12 clusters tienen el mínimo posible (3 puntos). Con este
  universo es esperable; tratarlos como señales, no como áreas robustas.
- **Clusters grandes:** C7 (8 pts, San Telmo, 13.5 ha) y C1 (7 pts, Villa Crespo, 21.2 ha)
  son los más consistentes. Ninguno supera el 9 % de los puntos: no hay fusión de media
  Ciudad.
- **Clusters que mezclan zonas (detectado):**
  - C0 (Palermo 3 + "San Telmo" 1 + "Chacarita" 1) y C1 (Villa Crespo 5 + "Palermo" 1 +
    "Costanera Norte" 1): los puntos con polo lejano son sedes geocodificadas fuera de su
    polo — coincide con los estados `zona_sucursal_a_revisar` de Fase 11.
  - C6 (Recoleta 3 + "Puerto Madero" 1), C9 (Av. Corrientes 2 + Caballito 1),
    C11 (Av. Corrientes 2 + Abasto 1 — coherente con Abasto como subzona de Corrientes),
    C3 (Palermo 2 + Belgrano 1), C7 (San Telmo 7 + Caseros/Barracas 1, limítrofe).
- **Ruido alto localizado:** Microcentro y Centro quedó 7/7 en ruido (corredor disperso).

## 13. Archivos generados

En `outputs/polos_gastro/experimentos_clustering/`:
- `puntos_clustering_experimental.geojson` (93 puntos con `cluster_id` y nota exploratoria)
- `poligonos_clustering_experimental.geojson` (12 polígonos con atributos completos)
- `resumen_clusters.csv` · `parametros_probados.csv`
- `mapa_clusters_experimental.png` · `mapa_poligonos_experimental.png`

En `docs/polos_gastro/experimentos_clustering/`: inventario, metodología, comparación, este QA
y el handoff. Script: `scripts/polos_gastro/experimentos/generar_poligonos_clustering.py`.

## 14. Verificación de términos prudentes

- Ambos PNG llevan título con "EXPERIMENTAL" y la nota visible "Capa auxiliar exploratoria.
  No constituye límite oficial. Requiere revisión territorial." — verificado renderizando y
  mirando las imágenes (QA visual, dos iteraciones: se corrigió solapamiento de etiquetas y
  visibilidad de polígonos).
- Cada feature/fila de polígono lleva `nota = "Polígono exploratorio auxiliar. No constituye
  límite oficial."`.
- Grep de términos vedados ("ranking", "mejores locales", "recomendaciones", "zonas
  definitivas", "límite oficial" en afirmativo) sobre los outputs y docs del experimento:
  sin ocurrencias afirmativas; "límite oficial" aparece solo negado.

## 15–18. Confirmaciones de guardrails

| # | Confirmación |
|---|---|
| 15 | **Sin API externa:** no se ejecutó Google Places ni ningún request externo de datos. Único acceso a red: `pip install scikit-learn` desde PyPI, autorizado explícitamente por Diego en esta sesión. |
| 16 | **PDFs y outputs finales de PolosGastro intactos:** no se modificó Fase 25, ni PDFs, ni mapas vigentes; la capa editorial V4 se usó solo en lectura. |
| 17 | **Datos fuente intactos:** `data/`, `PolosGastro/cartografia/` y todos los inputs se abrieron solo en lectura. Todo lo escrito está en las 3 carpetas experimentales nuevas. |
| 18 | **Sin push, sin commit, sin staging:** no se ejecutó ningún comando `git add`/`commit`/`push`; verificado con `git status --short` (solo archivos nuevos untracked). |
