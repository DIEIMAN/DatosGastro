# Informe final — Prototipo V1 del pipeline de microzonas gastronómicas

**Fecha:** 2026-07-08 · **Carácter:** experimental. Nada de lo aquí descripto modifica la
Fase 25, los mapas oficiales ni el pipeline F01–F05. Sin commits (pedido explícito).
Objetivo de la etapa: **construir evidencia** para decidir si el enfoque diseñado el
2026-07-08 produce mejores microzonas gastronómicas que las tandas DBSCAN anteriores.

**Respuesta corta: sí, el enfoque funciona y el salto de calidad es medible.** Con el
universo V1 (9.739 entidades, 92× la semilla), HDBSCAN intra-macrozona detecta 83 núcleos
de diámetro acotado (≤ 1,3 km) donde el mejor DBSCAN de las tandas anteriores colapsaba
todo en un cluster por macrozona. El 92,8 % de los polígonos híbridos pasa los gates de QA
sin intervención. Los problemas restantes son de datos (semilla con sedes mal geocodificadas,
F02-2025 defectuoso, recencia) y de dos ajustes metodológicos identificados, no del método.

## 1. Qué se implementó (las 7 etapas pedidas)

Scripts en `scripts/polos_gastro/experimentos/pipeline_microzonas_v1/` (config + s01–s05),
salidas en `outputs/polos_gastro/experimentos/pipeline_microzonas_v1/`, docs en
`docs/polos_gastro/experimentos/pipeline_microzonas_v1/`. Todo parámetro está registrado
con justificación en `parametros_pipeline_v1.json` (regla "sin parámetros mágicos").

1. **Universo V1 (Etapa 1):** tabla maestra de 9.739 entidades desde F01+F02 con
   resolución de entidades espacial+textual, linaje completo a filas fuente y reglas
   documentadas en `REGLAS_UNIVERSO_V1.md`. Volumen dentro del rango previsto (8.000–9.500).
2. **Perfilado (Etapa 2):** `universo/perfil_universo_v1.md` — 100 % geocodificado,
   distribución por comuna/barrio (point-in-polygon), densidades por km², composición de
   evidencia y advertencia de recencia (evidencia fechada concentrada en 2016–2018).
3. **Clustering por macrozona (Etapa 3):** contenedores construidos como hull de la semilla
   depurada + buffer 500 m (capa de trabajo aproximada, no límite oficial); 4.615 entidades
   asignadas a 12 macrozonas; HDBSCAN por macrozona (83 clusters en 11; Costanera Norte
   declarada `evidencia_insuficiente` con justificación automática del fallback); KDE de
   control por macrozona; DBSCAN de continuidad y local para comparación.
4. **Poligonización (Etapa 4):** 419 polígonos alternativos por 6 métodos (convex, concave
   0.3/0.5, buffer-unión, contorno KDE, cápsula PCA solo en los 4 corredores detectados),
   con mapas comparativos por macrozona (`poligonos/mapas/comparativa_*.png`). Sin ganador
   declarado, como se pidió.
5. **Métricas objetivas (Etapa 5):** `metricas/metricas_microzonas.csv` — 502 filas con
   n locales, superficie, densidad, cobertura, excluidos, contención, elongación,
   compacidad, distancia media al vecino y gates/banderas de QA por polígono.
6. **Comparación (Etapa 6):** `COMPARACION_DBSCAN_HDBSCAN_HIBRIDO.md` — los tres enfoques
   sobre el mismo universo, con ventajas/desventajas respaldadas por números.
7. **Recomendaciones (Etapa 7):** §4 de este informe.

## 2. Hallazgos que exceden lo esperado

- **La semilla de Fase 13 tiene un 22 % de sedes mal geocodificadas** (21 de 95 puntos a
  más de 2,3 km del centro de su polo; Belgrano tiene sedes a 14 y 8 km). Deforman
  cualquier contenedor construido sobre ellas. La lista queda implícita en
  `macrozonas/macrozonas_contenedores.geojson` (`n_semilla_apartados`) y conviene
  volcarla a la cola de revisión de Fase 11.
- **El recurso F02-2025 está roto en origen o en el mapeo:** 25.289 filas → 877 direcciones
  únicas (filas idénticas repetidas hasta 360 veces) y sin fecha de habilitación. Aporta
  poco y obliga a bandera propia. Confirma la revisión de mapeo que el diseño dejó pendiente.
- **5.123 entidades (53 %) quedan fuera de toda macrozona editorial.** No es un error: los
  12 polos editoriales cubren una fracción de la ciudad. Esa capa diagnóstica
  (`entidades_fuera_de_macrozona.csv`) es la materia prima para detectar **zonas
  emergentes** no contempladas por el mapa editorial (p. ej. corredores de Villa Urquiza,
  Devoto, Flores, visibles en el perfil por barrio).
- **Los núcleos "todo el barrio es denso":** 6 de 83 clusters superan el gate de 35 ha
  (Microcentro C0: 432 locales / 92 ha; Palermo Soho C2: 244 / 87 ha). HDBSCAN describe
  bien la realidad (densidad continua), pero la microzona útil requiere subdividir esos
  casos (ver §4.1).

## 3. Limitaciones encontradas

1. **Contenedores derivados de la semilla:** el hull de 3–18 puntos + buffer es una
   aproximación gruesa del polígono editorial; la sensibilidad al buffer es material
   (300 m → 3.726 entidades asignadas; 500 m → 4.615; 700 m → 5.307). Para el pipeline
   oficial hace falta digitalizar los contornos editoriales una única vez.
2. **F02 sin nombre comercial** limita la deduplicación cruzada (solo 814 fusiones F01↔F02)
   y puede tanto subcontar (galerías) como sobrefusionar (vecinos de igual categoría a
   ≤ 15 m). Umbrales sin calibrar contra un conjunto etiquetado a mano.
3. **Recencia:** la evidencia fechada es 2015–2023 con pico 2016–2018. Las microzonas
   reflejan concentración histórica de oferta registrada; sin ponderación temporal pueden
   sobrevivir núcleos que decayeron después de 2019.
4. **Cápsula de corredor sobre eje PCA**, no sobre el eje vial real (contención 80 %):
   depende de la base callejera GCBA ya identificada como pendiente en el plan de mapas V3.
5. **Sin validaciones de estabilidad** (Jaccard bajo ±25 % de `min_cluster_size` y bootstrap
   80 %) ni test contra el universo semilla como conjunto de control: quedaron fuera de esta
   tanda por alcance.
6. **KDE con umbral relativo por macrozona** cumple como control, pero en macrozonas de
   densidad muy pareja produce contornos chicos alrededor del máximo (subestima núcleos
   secundarios): el umbral merece sensibilización en el piloto.

## 4. Recomendaciones metodológicas (Etapa 7 del pedido)

### 4.1 Segunda pasada para núcleos gigantes (nueva, la más importante)
Para los 6 clusters > 35 ha: re-correr HDBSCAN solo sobre los puntos del cluster con
`min_cluster_size` mayor y `cluster_selection_method="leaf"` (extrae las hojas de la
jerarquía = sub-núcleos), o usar los contornos KDE internos como separadores. Es la brecha
principal entre lo detectado y la microzona editorialmente útil.

### 4.2 Ponderar locales por importancia
Con F01+F02 no hay rating ni reseñas. Pesos disponibles HOY, en orden de honestidad:
(a) recencia de evidencia (habilitación 2019+ pesa más que 2015), (b) multiplicidad de
evidencia (`en_f01` y `en_f02` a la vez, nº de registros), (c) calidad geo. Un KDE
ponderado por esos pesos es inmediato. Rating/reseñas de Google Places solo podrían entrar
como **evidencia complementaria por muestreo** (ver 4.4), nunca como peso masivo: el TOS
limita retención y el costo es renovable.

### 4.3 Detectar corredores además de núcleos
La detección actual (elongación PCA > 3 y largo > 600 m sobre clusters ya formados)
encontró 4 corredores reales pero fragmenta los largos (Av. Corrientes quedó en 3–4
núcleos consecutivos: C5-C6-C7). Propuesta: paso dedicado que proyecte entidades sobre
los ejes viales GCBA y detecte secuencias densas 1-D (ventana deslizante sobre la
progresiva de la avenida), fusionando núcleos consecutivos en un corredor único. Depende
de la misma base callejera pendiente.

### 4.4 Google Places como evidencia complementaria (nunca principal)
Rol correcto, alineado con el diseño y la skill 06: (a) validación de vigencia por
muestreo dirigido sobre microzonas ya detectadas (decenas de consultas autorizadas, no
censo), (b) desempate de duplicados de la banda 15–30 m (497 casos), (c) rating medio
del núcleo como atributo descriptivo agregado. Cada corrida con presupuesto explícito
aprobado por Diego.

### 4.5 Ajustes menores detectados
- Recuperar la banda de revisión R5d (497 posibles duplicados) con nombres de F01 contra
  razón social del recurso F02-2025 crudo (el dato existe en origen, no en el mapeo).
- Documentar el contenedor degradado de Avenida Caseros / Barracas (quedó con 1 punto
  semilla tras depurar 2) — es el candidato obvio a redigitalización manual temprana.
- El punto U+FFFD de "Las Cañitas" sigue en el CSV de Fase 13 (defecto de origen conocido).

## 5. Siguiente paso recomendado (antes de pensar en el flujo oficial)

**No** incorporar nada todavía. El orden propuesto:

1. **Revisión humana del piloto:** Diego mira los mapas de Etapas 3–4 en las tres
   macrozonas canónicas (Palermo, San Telmo, Corrientes) y valida contra terreno el caso
   de prueba del diseño (¿emerge Fitz Roy–Honduras–Gorriti y no todo Palermo?). Sin ese
   juicio editorial, ninguna métrica alcanza (doc 02 §4.5).
2. **Digitalizar contornos editoriales de los 12 polos** (una vez, capa de trabajo): elimina
   la dependencia del hull de semilla, el principal supuesto frágil del prototipo.
3. **Implementar la segunda pasada de núcleos > 35 ha** (§4.1) y las validaciones de
   estabilidad (±25 % de parámetros, bootstrap), que ya están especificadas en el diseño.
4. Recién entonces, corrida completa versionada (`universo_v202607` + microzonas candidatas)
   con tabla de decisiones humanas — la Fase D del plan de adopción.

Los pasos 2 y 3 son trabajo de horas, no de semanas; el bloqueo real es la decisión
editorial del paso 1.
