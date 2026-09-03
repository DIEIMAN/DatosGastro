# Casas de pastas — estado

**Fecha de corte:** 2026-09-03. **Alcance:** solo casas y fábricas de pastas; no restaurantes ni
restaurantes italianos (`CLAUDE.md`).

## Dos líneas, una vigente

| Línea | Dónde | Unidad de conteo | Estado |
|---|---|---|---|
| Build por habilitación (agosto 2026) | `outputs/casas_pastas/` (ignorado por Git: trae razón social y direcciones individuales); scripts en `scripts/casas_pastas/build_casas_pastas.py` | Grupos por domicilio normalizado y rubro con el lector compartido; reproduce 159 exacto tras el arreglo del lector (2026-08-28) | **Vigente.** |
| Integrado V4 (junio–julio 2026) | `outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf`, `PACK_REVISION_EXTERNA_254_V4`, `outputs/casas_pastas_integrado/`, `_google_places/`, `_recall/`; docs en `docs/casas_pastas/historico_v4_2026-06/` y `revision_institucional_2026-07/` | Padrón integrado AGC + OSM + Google (254 depurados) | Superada por el build por habilitación. Los PDF entregados se conservan. |

## Decisiones que esperan a Diego

- Adoptar la clave `clave_habilitacion` (la de panaderías) en `build_casas_pastas.py`: mueve el
  159 publicado y obliga a regenerar el entregable. Ver
  `docs/revisiones/HANDOFF_UNIDAD_DE_CONTEO_2026_08_28.md`, sección "No tocado a propósito".
- Consolidar las cinco carpetas históricas de `outputs/casas_pastas_*` bajo una sola. No se hizo
  el 2026-09-03 porque la build canónica está en una carpeta ignorada por Git y meter las
  históricas (parcialmente trackeadas) adentro las sacaría del índice; hace falta elegir un
  nombre para la canónica versionable.

## Dónde seguir

- `docs/estudios_de_rubro/COMPARACION_PANADERIAS_CASAS_DE_PASTAS.md`.
- Auditoría de la base 238 (domicilios sin altura, 2026-08-28) y la nota «254 vs 11» en los
  handoffs del 2026-08-27/28.
