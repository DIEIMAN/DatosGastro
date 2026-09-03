# HANDOFF — Experimento polígonos exploratorios v2 (PolosGastro)

**Fecha:** 2026-07-07 · **Rama:** `mercados-gastronomicos-v2` (todo untracked, sin commit).
**Estado:** EXPERIMENTO V2 GENERADO CON OBSERVACIONES — pendiente de revisión visual humana.

Segunda tanda del experimento auxiliar. **No** reemplaza el informe vigente, **no** toca
Fase 25 ni PDFs ni mapas actuales, **no** define límites oficiales. La tanda 1
(`experimentos_clustering/`) quedó intacta; todo lo nuevo está en carpetas `*_v2`.

## Qué se hizo

1. **Diagnóstico del ruido de la tanda 1** (47.3 %): causa principal, universo semilla ralo
   (~7 pts/polo); ver `DIAGNOSTICO_RUIDO_DBSCAN.md`.
2. **DBSCAN recalibrado:** grilla ampliada de 45 combinaciones (eps 150–1000, ms 2–6) con
   métricas de fusión/fragmentación, y **3 candidatas** en vez de una:
   estricta (500/4, 57 % ruido), equilibrada (400/3, 47.3 %, = tanda 1) e
   **inclusiva (650/4, 29 % ruido, sin fusión de zonas — el hallazgo de la grilla)**.
   ms=2 descartado (pares como clusters); eps ≥ 800 descartado (fusiona zonas aunque baje ruido).
3. **Poligonización asistida por polo/subzona** (estrategia nueva): 14 grupos con hull
   prudente, depuración de sedes apartadas (10 excluidas), confianza por cantidad de puntos
   (11 alta / 2 media / 1 baja) y bandera `extension_a_revisar` en 3 grupos dispersos
   (Chacarita, Caseros/Barracas, Costanera Norte).
4. **Comparación y recomendación:** el asistido cubre todas las zonas y es la salida más
   defendible para revisión del informe; DBSCAN queda como diagnóstico de concentraciones
   emergentes. Detalle en `COMPARACION_DBSCAN_VS_ASISTIDO.md` y
   `RECOMENDACION_METODOLOGICA_POLIGONOS.md`.

## Diferencia entre las dos salidas (en una línea)

DBSCAN **descubre** concentraciones sin usar etiquetas (pero deja ruido y zonas vacías);
el asistido **representa** las zonas editoriales existentes con polígonos trazables y
atributos de calidad (pero no puede descubrir nada nuevo).

**Cuál parece mejor:** la asistida por subzona como referencia técnica para el informe,
con depuración manual previa de los 3 grupos dispersos; DBSCAN inclusivo (650/4) como anexo
diagnóstico.

## Cómo correr

```
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/generar_poligonos_clustering_v2.py
```
Opcionales: `--input CSV`, `--outdir DIR`, `--solo-grilla` (solo tabla de grilla).
Las candidatas están definidas en `CANDIDATAS_DBSCAN` dentro del script, con su justificación.

## Qué revisar visualmente

1. `mapa_poligonos_asistidos_subzona_experimental.png` — la salida principal: colores =
   confianza, borde rojo punteado = extensión a revisar, cruces grises = apartados excluidos.
2. `comparativo_dbscan_vs_asistido.png` — azul (DBSCAN equilibrado) vs naranja (asistido);
   los dispersos van en trazo tenue.
3. Los 3 mapas DBSCAN candidatos, en especial el inclusivo (650/4).
4. La lista de **10 puntos apartados** (QA v2 §7) — insumo directo para la revisión de sedes
   pendiente de Fase 11.
5. Choques menores de etiquetas en el centro del mapa asistido: leer con
   `resumen_poligonos_asistidos_subzona.csv`.

## Próximos pasos sugeridos

1. Revisión humana de mapas y del resumen CSV; decidir si el asistido pasa a insumo de
   trabajo del informe (siempre como capa auxiliar).
2. Depurar manualmente Chacarita / Caseros-Barracas / Costanera Norte y regenerar.
3. Evaluar cápsulas sobre eje vial para corredores (Corrientes, Caseros) — no implementado.
4. Etapa futura: experimento separado con universo público F01–F05 (10.847 ubicaciones),
   sin mezclar universos (riesgos en `RECOMENDACION_METODOLOGICA_POLIGONOS.md` §5).

## Confirmaciones

Sin push, sin commit, sin staging. Sin API externa ni Places nuevo ni scraping ni requests
externos. Datos fuente y pipeline intactos (el CSV de Fase 13 conserva incluso su defecto de
encoding). Informe vigente, Fase 25, PDFs y mapas actuales intactos. Tanda 1 del experimento
sin pisar. Cafecito / Mercados / Casas de Pastas no se tocaron.
