# QA de geometrías

- CRS de entrega: EPSG:4326. Cálculos métricos: EPSG:5347.
- Features válidas: 39/39. Vacías: 0.
- Conteo máximo de pertenencias por local: 2. No hay duplicación triple.
- Solapes clasificados: 14 pares.

| polo_a_id | polo_b_id | solape_ha | locales_doble_conteo | clase |
|---|---|---|---|---|
| R01 | R08 | 12.549172 | 77 | SOLAPE_TERRITORIAL_REAL |
| R01 | R09+R19+Z43 | 33.15053 | 111 | SOLAPE_TERRITORIAL_REAL |
| R04 | Z46 | 23.16541 | 4 | SOLAPE_TERRITORIAL_REAL |
| R05 | Z41 | 0.058019 | 0 | SLIVER |
| R08 | R09+R19+Z43 | 6.356782 | 1 | SOLAPE_TERRITORIAL_REAL |
| R09+R19+Z43 | R21 | 4.807454 | 4 | SOLAPE_TERRITORIAL_REAL |
| R09+R19+Z43 | Z44 | 15.928442 | 25 | SOLAPE_TERRITORIAL_REAL |
| R11 | Z50 | 1.548684 | 3 | SOLAPE_TERRITORIAL_REAL |
| R12 | Z47 | 0.0 | 0 | SLIVER |
| R13 | Z35 | 3.908406 | 15 | SOLAPE_TERRITORIAL_REAL |
| R13 | Z37 | 0.0 | 0 | SLIVER |
| R20 | Z41 | 2.328601 | 6 | SOLAPE_TERRITORIAL_REAL |
| Z24 | Z27 | 0.534667 | 2 | SOLAPE_TERRITORIAL_REAL |
| Z40 | Z54 | 39.385541 | 52 | PIEZA_ANIDADA |

La clasificación no reparte puntos por centro de masa. Para el total global cada `local_id` cuenta una vez; para las fichas puede aparecer en ambas geometrías cuando el solape es territorialmente real. Z54/Z40 se trata como pieza anidada, no como solape accidental.
