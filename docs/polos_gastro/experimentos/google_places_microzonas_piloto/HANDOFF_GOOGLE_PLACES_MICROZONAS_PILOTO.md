# HANDOFF — piloto Google Places + microzonas (2026-07-09)

## Qué se pidió

Piloto operativo de microzonas gastronómicas: macrozonas candidatas V1 como
contenedores + universo F01+F02 + Google Places como enriquecimiento acotado por zona +
HDBSCAN/KDE + **polígonos chicos** (que los clusters NO ocupen macrozonas enteras).
Zonas piloto: Palermo Soho/Hollywood, Corrientes/Microcentro, Belgrano, San Telmo.
Restricciones: sin Fase 25, sin commits/add/push, sin tocar datos fuente, todo en
`experimentos/`, Places solo con presupuesto explícito, sin place_id/raw JSON/key en
outputs publicables.

## Estado: PILOTO EJECUTADO (2026-07-09)

- **Google Places: EJECUTADO con autorización explícita de Diego** (confirmada en
  sesión): 379 consultas `searchNearby` (cap 450, ≤ USD 13,27), **0 errores**, 3.511
  puntos únicos → 626 fuera de macrozona (descartados) → 1.234 duplicados de F01+F02 →
  **1.651 puntos nuevos** (universo +76 %: 2.172 → 3.823).
- **Clustering + polígonos: EJECUTADO** dos veces (solo F01+F02 y enriquecido). Versión
  final: **78 microzonas, máx. 12,1 ha, 0 descartes por gates, 0 gigantes**. Mapas de
  las 4 zonas con QA visual hecho (incluye una corrección real detectada por QA: puntos
  Places fuera de macrozona que entraban al universo — se agregó contención estricta).

## Dónde está todo

- Scripts: `scripts/polos_gastro/experimentos/google_places_microzonas_piloto/`
  (orden: `preparar_consultas_places_piloto.py` → `construir_universo_piloto.py` →
  `detectar_microzonas_piloto.py` → `generar_mapas_piloto.py`; siempre con
  `.venv/Scripts/python.exe`).
- Docs: `docs/polos_gastro/experimentos/google_places_microzonas_piloto/`
  (PLAN_API, QA_PRIVACIDAD, INFORME_RESULTADOS, este handoff).
- Outputs: `outputs/polos_gastro/experimentos/google_places_microzonas_piloto/`
  (UNIVERSO_PILOTO_SANITIZADO.csv, MICROCLUSTERS_PILOTO.geojson,
  POLIGONOS_MICROZONAS_PILOTO.geojson, 4 mapas PNG, 2 QA json, places/plan+sanitizado;
  `interno/` con place_id **gitignoreado** — verificado con `git check-ignore`).

## Decisiones tomadas en esta tanda

- Places como **enriquecimiento** con dedup contra F01+F02 (15 m parcela / 40 m +
  nombre compatible), nunca fuente principal; columna `fuente` en todos los outputs.
- Contención estricta: puntos Places fuera de la macrozona se descartan (la grilla de
  consulta se extiende ~175 m más allá del borde).
- Control de tamaño: subdividir (KMeans) si área > 18 ha o diámetro > 1.000 m no
  corredor; piezas objetivo ~10 ha; los cortes internos son geométricos (limitación
  editorial documentada en el informe).
- Bug sklearn 1.9 con `cluster_selection_epsilon`: fallback a epsilon 0 documentado
  (en la corrida final solo afectó a Palermo Soho).
- `.gitignore`: agregada la carpeta `interno/` del piloto.

## Pendientes

1. Revisión editorial de los cortes de subdivisión (Corrientes K01/K03, Belgrano).
2. Extender a las 8 macrozonas restantes (dry-run del mismo script estima consultas;
   requiere NUEVA autorización de presupuesto).
3. Resolver el bug de epsilon (fijar versión de sklearn o merge post-hoc a 50 m).
4. Definir refresco/rol institucional del dato Places (hoy: foto del 2026-07-09).
5. Este piloto NO actualiza la revisión DGDGAS de macrozonas (proceso paralelo en
   `infraestructura_cartografica_v1/REVISION_DGDGAS_MACROZONAS_CANDIDATAS_V1.md`).

## Restricciones confirmadas

Sin commits/add/push (`.gitignore` modificado en working tree, sin stagear). Fase 25,
informes oficiales y datos fuente intactos. Key nunca impresa ni guardada; sin raw JSON;
place_id solo en `interno/` gitignoreado. Todo bajo `experimentos/`.
