# QA de la preparación del re-piloto — Tanda 1 Fase 11 (Google Places)

Fecha: 2026-07-02. Cierre de control de la preparación del re-piloto. Documento interno.

## Ejecución real Tanda 1

Cuarta iteración: se ejecutó la **única corrida real autorizada**. Detalle completo en
`QA_REPILOTO_TANDA1_REAL_GOOGLE_PLACES.md` y decisión en `DECISION_POST_REPILOTO_TANDA1.md`.

- **API ejecutada**: sí (una sola vez, comando `--execute --confirm-real-api`).
- **Cantidad de consultas**: 10 (hard cap respetado). Matches 10, errores 0, cuota/billing/permiso
  sin problemas.
- **Outputs generados**: `resultados_repiloto_tanda1_interno.csv`,
  `resultados_repiloto_tanda1_revision_visual.csv`, `resultados_repiloto_tanda1_publicable.csv`.
- **Seguridad de API**: key reportada solo como "presente"; nunca impresa ni guardada; `.env` no
  copiado; sin API key en outputs; sin raw JSON en outputs.
- **Sanitización**: revisión visual con lat/lon sin campos sensibles (0 columnas prohibidas);
  publicable con lat/lon vacíos (aceptado_para_mapa=no) y sin campos sensibles (0 columnas
  prohibidas); interno conserva el dato técnico.
- **Corrección post-corrida**: bug de clasificación (`store`⊂`food_store`) que marcaba mal a Cosi
  Mi Piace; corregido a match por token exacto + set gastronómico; clasificación **reprocesada
  desde el interno guardado, sin nueva llamada API**. Dry-run vuelto a correr OK.
- **Decisión posterior**: recomendado preparar Tanda 2; corregir solo queries de Osaka/Aldo's
  (cerrados) y Oporto (Colegiales).
- **Confirmaciones**: no PDF/DOCX/mapas; no datos fuente ni otros proyectos tocados; no
  commit/push/staging.

## Actualización — output de revisión visual agregado

Tercera iteración: se agregó un **output intermedio de revisión visual** a la rama real. No se
ejecutó API.

- **Output de revisión visual agregado**: `resultados_repiloto_tanda1_revision_visual.csv`
  (esquema en `schema_resultados_repiloto_tanda1_revision_visual.csv`). Trae `lat`/`lon`
  **siempre** (aunque `aceptado_para_mapa='no'`), con `decision_automatica`, `motivo_decision` y
  `accion_recomendada`, para inspección manual antes de aceptar/rechazar.
- **No contiene** `google_place_id`/`place_id`, `rating`, `user_ratings_total`, raw JSON, API key,
  dirección exacta con altura, `nota_interna` ni campos técnicos sensibles. Verificado con prueba
  offline de `build_revision_row` (0 campos prohibidos presentes).
- **Publicable final mantiene lógica prudente**: `lat`/`lon` vacíos mientras
  `aceptado_para_mapa='no'` (verificado offline: `pub['lat']` vacío).
- **Tres roles claros**: interno (todo técnico) · revisión visual (lat/lon sin campos sensibles) ·
  publicable (solo puntos aceptados). La revisión visual **no** va al PDF público ni circula como
  publicable final.
- **Dry-run sigue funcionando** tras los cambios (10 filas, sin API). Sintaxis validada.
- **Hard cap 10 intacto.** No API ejecutada; no llamadas a Google Places; API key no impresa;
  `.env` no copiado; no PDF/DOCX/mapas; no datos fuente ni otros proyectos tocados;
  no commit/push/staging.

## Actualización — rama real implementada con doble confirmación

Segunda iteración: se implementó la **rama real de ejecución API**, dejándola **bloqueada detrás
de doble confirmación**. No se ejecutó API.

- **Rama real implementada** en `places_repiloto_fase11.py` (`do_execute`, `call_places`,
  `clasificar`, `build_interno_row`, `build_publicable_row`).
- **Doble confirmación requerida**: la API real solo se llama con `--execute --confirm-real-api`.
  - `--execute` sola → frena con error controlado (exit 2), sin API. Verificado.
  - `--confirm-real-api` sola → dry-run con aviso (exit 0), sin API. Verificado.
  - (sin banderas) → dry-run (exit 0). Verificado.
  - `--execute --confirm-real-api` → **NO ejecutado** (regla estricta); llamaría API solo con key
    válida, si no frena con exit 3.
- **Hard cap 10 intacto**: `MAX_LOCALES_HARD_CAP = 10` sin cambios; la rama real corta a 10 y avisa.
- **Dry-run re-ejecutado** tras los cambios: 10 filas, input de Fase 11, queries limpias, criterios
  presentes, sin API.
- **Seguridad**: la key se lee solo de entorno/`.env`, nunca se imprime ni guarda; el `.env` nunca
  se muestra (solo "presente/ausente"); no se guarda raw JSON; outputs interno/publicable separados;
  publicable sin place_id/rating/user_ratings_total/dirección exacta/nota_interna.
- **Clasificación prudente** implementada: rechazo de sustitutos (Osaki/Artemisia/Somos OP), rubros
  no gastronómicos y fuera de CABA; `confidence_match` alta/media/baja; `aceptado_para_mapa` nunca
  en `si` automáticamente (se habilita a mano tras revisión).
- **No commit/push/staging**; no se tocaron datos fuente ni otros proyectos; no PDF/DOCX/mapas.

## Confirmaciones de seguridad y alcance

- **No se ejecutó API.** Solo se corrió el dry-run (sin llamadas de red).
- **No hubo llamadas a Google Places.**
- **No se imprimió ninguna API key** ni se leyó su valor.
- **No se leyó ni mostró el contenido de `.env`**; no se copió `.env`.
- **No se modificó `MAX_LOCALES_HARD_CAP`** (sigue en 10 en el script nuevo).
- **No se guardó ninguna API key en outputs.**
- **No se generó PDF, DOCX ni mapas.**
- **No se tocaron datos fuente**, ni Borrador 2/3, ni Cafecito, Mercados o Casas de Pastas.
- **No se borró ningún archivo.**
- **No hubo commit, push ni staging.** No se usó `git add`.
- No se usó "DataGastro" como marca pública.

## Confirmaciones de la tarea

- **Wrapper/script corregido preparado**: `scripts/polos_gastro/google_places/places_repiloto_fase11.py`.
  - Lee exclusivamente la tabla preparada de Fase 11 (o la muestra derivada de ella).
  - Dry-run por defecto; rama real detrás de doble confirmación `--execute --confirm-real-api`.
  - Hard cap de 10 respetado.
  - No imprime API key; no guarda raw JSON en publicable; separa interno de publicable; registra
    `fecha_consulta` en el esquema interno.
  - No usa seeds experimentales.
- **Muestra corregida de 10 creada**: `muestra_repiloto_tanda1_fase11.csv` (10 locales de Palermo
  tomados de Fase 11).
- **Queries limpias generadas**: `queries_repiloto_tanda1_fase11.csv` (con `criterio_aceptacion` y
  `criterio_rechazo`, incluidos los rechazos de Osaki/Artemisia/Somos OP).
- **Dry-run hecho**: `dryrun_repiloto_tanda1_fase11.csv` (10 filas, sin API).
- **No se usaron seeds experimentales como input principal.** El script apunta a Fase 11.
- **Esquemas interno y publicable preparados** (solo cabeceras, sin resultados reales):
  `schema_resultados_repiloto_tanda1_interno.csv`, `schema_resultados_repiloto_tanda1_publicable.csv`.
- **El publicable futuro NO incluye** `google_place_id`/`place_id`, `rating`, `user_ratings_total`,
  dirección exacta con altura ni `nota_interna` (verificado contra las columnas del esquema).

## Verificación del FieldMask (para ejecución futura)

El `FIELD_MASK` incluye: `id`, `displayName`, `formattedAddress`, `location`, `types`,
`primaryType`, `businessStatus`, `rating`, `userRatingCount`.

- `location` presente (lat/lon imprescindible para mapa).
- `rating`, `userRatingCount`, `id` marcados como internos (no viajan al publicable).

## Verificación de rechazos explícitos

En el script (`SUSTITUTOS_PROHIBIDOS`, `CATEGORIAS_NO_GASTRONOMICAS`) y en las queries:

- No aceptar "Osaki" como "Osaka".
- No aceptar "Artemisia" como "Aldo's".
- No aceptar "Somos OP" como "Oporto".
- No aceptar rubros no gastronómicos (insurance_agency, etc.).
- No aceptar resultados fuera de CABA.
- No aceptar sucursal de otro polo sin revisión.

## Archivos creados por esta preparación

- `scripts/polos_gastro/google_places/places_repiloto_fase11.py`
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/muestra_repiloto_tanda1_fase11.csv`
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/queries_repiloto_tanda1_fase11.csv`
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/dryrun_repiloto_tanda1_fase11.csv`
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/schema_resultados_repiloto_tanda1_interno.csv`
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/schema_resultados_repiloto_tanda1_publicable.csv`
- `docs/polos_gastro/fase11_google_places_piloto/PLAN_REPILOTO_TANDA1_FASE11.md`
- `docs/polos_gastro/fase11_google_places_piloto/QA_PREPARACION_REPILOTO_TANDA1_FASE11.md` (este)
