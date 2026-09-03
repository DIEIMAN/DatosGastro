# HANDOFF — Experimento polígonos exploratorios por clustering (PolosGastro)

**Fecha:** 2026-07-07 · **Rama:** `mercados-gastronomicos-v2` (todo untracked, sin commit).
**Estado:** EXPERIMENTO GENERADO CON OBSERVACIONES — pendiente de revisión visual humana.

Experimento paralelo y auxiliar. **No** reemplaza el informe vigente de PolosGastro, **no**
toca Fase 25 ni PDFs finales ni mapas actuales, **no** define límites oficiales. Todos los
outputs dicen "experimental/exploratorio/estimado".

## Qué se creó

- Script: `scripts/polos_gastro/experimentos/generar_poligonos_clustering.py`
- Docs (`docs/polos_gastro/experimentos_clustering/`): `INVENTARIO_PUNTOS_DISPONIBLES.md`,
  `METODOLOGIA_POLIGONOS_CLUSTERING.md`, `QA_POLIGONOS_CLUSTERING.md`,
  `COMPARACION_CLUSTERS_ZONAS_ACTUALES.md`, este handoff.
- Outputs (`outputs/polos_gastro/experimentos_clustering/`): puntos y polígonos GeoJSON,
  `resumen_clusters.csv`, `parametros_probados.csv`, 2 mapas PNG con QA visual hecho.

## Cómo se corre

```
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/generar_poligonos_clustering.py
```
Opcionales: `--input CSV`, `--outdir DIR`, `--eps METROS --min-samples N` (fuerza parámetros;
si no, elige por criterio documentado en la metodología §7).

## Decisiones clave

- **Input elegido:** `outputs/polos_gastro/fase13_mapas/tablas/locales_para_mapa_revision.csv`
  (106 locales semilla con lat/lon, polo y subzona; único archivo del repo con el universo
  completo geolocalizado). Se descartaron 11 `duplicado_probable` y 2 puntos fuera de CABA →
  **93 puntos válidos**.
- **Algoritmo:** DBSCAN (scikit-learn 1.9.0) en EPSG:5347, peso uniforme 1 (el input no trae
  rating/reviews; los archivos `_interno` de Fase 11 se excluyeron a propósito).
- **scikit-learn se instaló en `.venv` en esta sesión con autorización explícita de Diego**
  (no estaba; trajo scipy/joblib/threadpoolctl, sin pisar paquetes).
- **Parámetros:** grilla 6×4 (eps 150–500 × min_samples 3–6) → elegido **eps=400 m,
  min_samples=3** (12 clusters, 44 ruido = 47.3 %, cluster máx 8 pts). Alternativa candidata:
  500/3 (10 clusters, 43 % ruido). Criterio de elección relajado a ruido ≤ 55 % porque ninguna
  configuración baja del 43 % con esta densidad (documentado).
- **Polígonos:** concave_hull(0.5) o convex hull + buffer 40 m; áreas 0.66–21.2 ha.

## Hallazgos para revisar visualmente

1. `mapa_poligonos_experimental.png`: si la escala de los polígonos (manchas chicas) sirve
   como contraste frente a las subzonas editoriales punteadas.
2. Clusters mixtos (C0, C1, C6): son **sedes geocodificadas fuera de su polo** — insumo
   directo para la revisión pendiente de Fase 11 (`zona_sucursal_a_revisar`).
3. Microcentro 7/7 en ruido y Corrientes cortada en C9/C11: DBSCAN no captura corredores.
4. C11 integra el punto de Abasto con Corrientes — consistente con Abasto como subzona.
5. Punto de Puerto Madero excluido por caer fuera del polígono de comunas (borde costero).

## Limitaciones

Universo semilla curado (~7 pts/polo), no censo; ruido intrínseco alto; comparación editorial
solo visual; una sola configuración final. Detalle en metodología §9.

## Próximos pasos sugeridos

1. Revisión humana de mapas + `resumen_clusters.csv`.
2. Eventual re-corrida con `--eps 500 --min-samples 3` para comparar.
3. Si el enfoque convence: corrida separada sobre universo público F01–F05 (sin mezclar
   universos) y/o variantes para corredores (densidad kernel).

## Confirmaciones

Sin push, sin commit, sin staging (`git add` no se usó). Sin APIs externas ni Places nuevo
(único acceso a red: pip install autorizado). Datos fuente y pipeline intactos. Informe
vigente, Fase 25, PDFs y mapas actuales de PolosGastro intactos. Cafecito/Mercados/Casas de
Pastas no se tocaron.
