# Mercados gastronómicos CABA — estado

**Fecha de corte:** 2026-09-03. **Alcance:** mercados gastronómicos específicamente; no mercados
generales ni minoristas (`CLAUDE.md`).

## Entregables

| Entregable | Dónde | Estado |
|---|---|---|
| Informe final V4.1 (markdown master → PDF) | `docs/mercados_caba/INFORME_FINAL_*_MARKDOWN_MASTER.md`; generador `src/mercados_caba/build_pdf_from_markdown_master.py`; regenerar según `docs/mercados_caba/README_REGENERAR_INFORME_FINAL_V4_1.md` | Cerrado (julio 2026). |
| Fichas | `docs/mercados_caba/fichas_v1_2/` | Vigente; `fichas_v0/` y `fichas_v1/` superadas. |
| Revisión DGDGAS | `docs/mercados_caba/revision_dgdgas_2026-07/` (antes `docs/mercados/`) y `outputs/mercados_caba/revision_dgdgas_2026-07/INFORME_MERCADOS_DGDGAS.pdf` (antes `outputs/mercados/`); generador `scripts/mercados/build_pdf_dgdgas_mercados.py` | Cerrado (2026-07-04). |
| Agregados publicables | `outputs/mercados_caba/sanitized/` | Vigente. |
| Fuentes internas | `fuentes_internas_mercados_caba/` (ignorado; incluye `DataMercados.zip` de 124 MB); inventario con `src/mercados_caba/build_inventario_fuentes_internas_mercados.py` | Sin cambios. |

Cifras canónicas del informe cerrado, según el registro de sesiones de julio: 254 depurados,
173 independientes, 81 cadenas. Verificar contra el markdown master antes de citar.

## Decisiones que esperan a Diego

- `fuentes_internas_mercados_caba/` → `data/fuentes_internas/mercados/` (plan del 2026-08-28):
  requiere tocar tres scripts de `src/mercados_caba/`, que es superficie protegida.
- `DataMercados.zip`: borrar si los 114 archivos sueltos al lado son su contenido extraído.
