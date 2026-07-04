# QA consolidado — Tandas reales Google Places (PolosGastro, Fase 11)

Fecha: 2026-07-02. Documento interno. Cierre de control de las corridas reales ejecutadas.

## Tandas ejecutadas

| Tanda | Comando | Consultas | Matches | Errores | Cap 10 | Detalle |
|---|---|---|---|---|---|---|
| Tanda 1 (re-piloto) | `--execute --confirm-real-api` | 10 | 10 | 0 | respetado | `QA_REPILOTO_TANDA1_REAL_GOOGLE_PLACES.md` |
| Tanda 2 | `--tanda tanda2 --execute --confirm-real-api` | 10 | 10 | 0 | respetado | `QA_TANDA2_REAL_GOOGLE_PLACES.md` |

- **Total de consultas reales acumuladas: 20** (10 + 10). No se ejecutaron los 106.
- Cada tanda usó su propia muestra/queries/outputs de Fase 11; **no se mezclaron ni pisaron**.

## Outputs generados

Tanda 1: `resultados_repiloto_tanda1_{interno,revision_visual,publicable}.csv`.
Tanda 2: `resultados_tanda2_{interno,revision_visual,publicable}.csv`.

## Seguridad de API

- API key leída solo de entorno/`.env`; reportada únicamente como "presente"; **nunca impresa ni
  guardada** en las dos corridas.
- `.env` **no** copiado ni mostrado en claro.
- **Sin API key en ningún output.**
- **Sin raw JSON** en ningún output (FieldMask mínimo; no se persiste la respuesta cruda).

## Sanitización

- **Interno**: contiene `google_place_id_interno`, `rating_interno`, `user_ratings_total_interno`,
  `direccion_google` (archivo técnico; correcto).
- **Revisión visual** (ambas tandas): lat/lon en las 10 filas aunque `aceptado_para_mapa=no`; **0
  columnas prohibidas** (sin place_id, rating, user_ratings_total, dirección exacta, nota_interna).
- **Publicable** (ambas tandas): lat/lon vacíos (todos `aceptado_para_mapa=no`); **0 columnas
  prohibidas**. Prudente: nada al mapa sin revisión humana.

## Confirmaciones globales

- No se ejecutó más de 10 consultas por tanda; `MAX_LOCALES_HARD_CAP=10` **sin modificar**.
- No se usaron seeds experimentales; input siempre desde la tabla preparada de Fase 11.
- No se usó "DataGastro" como marca pública en los entregables.
- **No PDF/DOCX/mapas finales.**
- **No se tocaron** datos fuente, Borrador 2, Borrador 3, Cafecito, Mercados ni Casas de Pastas.
- **No se borró nada.**
- **No commit / push / staging.** No se usó `git add`.

## Decisiones humanas abiertas (para Borrador 4)

- Locales cerrados en Google (Osaka, Aldo's — Tanda 1; Las Pizarras, Francisca del Fuego, Morelia —
  Tanda 2): mantener en semilla como "vigencia no confirmada / no mapeable hasta validar".
- Oporto (Colegiales) y las cadenas de Tanda 2: revisión de zona/sede.
- Pa' Pastar → "Pastasole": definir corrección de query o no-match.
- Niño Gordo LG028: posible duplicado de la sede Palermo (LG003).

Ver `DECISIONES_HUMANAS_POST_TANDA1.md`, `DECISION_POST_REPILOTO_TANDA1.md` y
`DECISION_POST_TANDA2.md`.
