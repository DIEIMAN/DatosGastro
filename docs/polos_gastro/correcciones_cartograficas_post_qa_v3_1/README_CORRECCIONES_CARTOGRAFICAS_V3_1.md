# Correcciones cartográficas post-QA V3.1

## Alcance

Línea derivada de presentación creada por `cartografo_territorial`. No recalcula modelos ni modifica capas V3. Modelos cerrados: Belgrano `BEL-A`, Recoleta `REC-A`, Costanera Norte `CN-DEC10`.

## Auditorías rectoras

| informe | SHA-256 |
| --- | --- |
| `docs/polos_gastro/auditoria_qa_territorial_v3/INFORME_AUDITORIA_QA_TERRITORIAL_V3.md` | `4cea66f8dc70a9cc60c5ac314e7edbc5f080748e56fc44e078796d26803b49b5` |
| `docs/polos_gastro/auditoria_externa_red_team_v3/INFORME_RED_TEAM_TERRITORIAL_V3.md` | `662fdd4e18bad5b5339b009992d681ec5fa5cc2b68835dfd1f031a02d88dc9e3` |

## Separación de superficies

- Editorial institucional: `capas/`, `mapas/` y metadatos publicables de esta línea.
- Interno técnico no publicable: `PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson`, tablas punto→unidad, métricas completas y alternativas. No se copiaron al paquete.

## Regeneración

Desde la raíz del repositorio:

`.venv/Scripts/python.exe scripts/polos_gastro/correcciones_cartograficas_post_qa_v3_1/generar_correcciones_cartograficas_v3_1.py`

El script usa únicamente archivos locales. No usa red, APIs ni Places.
