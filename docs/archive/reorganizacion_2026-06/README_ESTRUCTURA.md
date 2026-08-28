# README_ESTRUCTURA — Cómo está organizado DataGastro

**Última actualización:** 2026-06-29 (reorganización segura — ver MANIFEST_REORG.md)

Este repo contiene **tres líneas de trabajo** que comparten un mismo pipeline base.
Esta guía explica dónde vive cada cosa y cómo seguir trabajando.

---

## 1. DataGastro general (pipeline público F01–F05)

Es el núcleo del proyecto. **Quedó intacto en su lugar** (mover esto rompe imports y rutas).

| Qué | Dónde |
|---|---|
| Modelado / analytics / validación | `src/build_model.py`, `src/build_analytics.py`, `src/validate_model.py` |
| Contratos / auditoría / geocodificación | `src/source_contracts.py`, `src/audit_real_data.py`, `src/geocode_usig.py` |
| SQL | `sql/01_…`…`sql/05_views_dashboard.sql` |
| Datos modelados | `data/processed/`, `data/raw/`, `data/seeds/` |
| Dashboard | `dashboard/` |
| Notebooks generales | `notebooks/` |
| Configs / fuentes externas | `config/` |
| Docs generales | `docs/` (raíz): diccionario de datos, fuentes y trazabilidad, changelog, guías |
| Tablas resumen generales | `outputs/tablas_resumen/` |

Comandos del pipeline (sin cambios):
```powershell
python src\build_model.py --strict-real
python src\build_analytics.py --strict-real
python src\validate_model.py --strict-real
python -m unittest discover tests
```

### DataGastro V2 (etapa 1) — también intacto, NO mezclar
`config/v2/`, `data/v2/`, `docs/datagastro_v2/`, `outputs/v2/`, `schemas/`, `src/v2/`.
Es una línea aparte; **no se tocó ni se fusionó** con Pastas/Mercados.

---

## 2. Casas de Pastas

| Qué | Dónde |
|---|---|
| **Informe final vigente** | `CasasDePastas/final/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` (+ `.md`) — copia |
| Fuente de verdad del final | `outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` |
| **Generador vigente** | `scripts/casas_pastas/build_pdf_integrado_v4.py` |
| Pipeline de padrón (Google/OSM/AGC) | `scripts/casas_pastas/` (varios `google_places_*`, `build_casas_pastas.py`, …) |
| Datos crudos / padrón (sensible) | `outputs/casas_pastas_integrado/`, `outputs/casas_pastas/`, … (gitignored, intactos) |
| Agregados del informe | `outputs/casas_pastas_reporte/*.csv`, mapas, geojson |
| Docs metodológicos | `docs/casas_pastas/` (NOTAS_METODOLOGICAS*, PLAN_PDF, GOOGLE_PLACES_PILOTO) |

Regenerar:
```powershell
python scripts\casas_pastas\build_pdf_integrado_v4.py
```

---

## 3. Mercados Gastronómicos CABA

| Qué | Dónde |
|---|---|
| **PDF final vigente** | `MercadosGastro/final/MercadosGastroCABA_FINAL.pdf` (+ Resumen) — copia |
| Fuente de verdad del final | `outputs/mercados_caba/sanitized/MercadosGastroCABA_con_horarios.pdf` |
| **Generador vigente (cadena)** | `src/mercados_caba/build_pdf_final_con_horarios.py` |
| Gráficos vigentes (v5) | `src/mercados_caba/build_visuals_v5.py` → `outputs/mercados_caba/sanitized/*_v5.png` |
| QA vigente | `src/mercados_caba/validate_mercados_final_con_horarios.py` |
| Insumos del informe | `docs/mercados_caba/` (anexos V4_1, master, oportunidad V4_1) + CSVs v4/v4_1/vfinal |
| Bitácora metodológica | `docs/mercados_caba/00_…` … `26_…` |
| Crudos / internas (sensible) | `outputs/mercados_caba/internal/`, `outputs/mercados_caba/raw/`, `fuentes_internas_mercados_caba/` (intactos) |

La cadena de generación encadena (no es un solo script):
`build_pdf_final_con_horarios.py` → `build_pdf_final_entrega.py` →
`build_pdf_final_v4_1_from_v3.py` → `build_pdf_from_markdown_master.py`.

Regenerar:
```powershell
python src\mercados_caba\build_visuals_v5.py            # si hace falta refrescar gráficos
python src\mercados_caba\build_pdf_final_con_horarios.py
python src\mercados_caba\validate_mercados_final_con_horarios.py
```

---

## 4. Carpetas de la reorganización

- **`_archive_historico/`** — Archivo histórico (64 archivos): bitácora de versiones de Mercados,
  informes/packs históricos de Casas de Pastas, checkpoints, y los 11 CSV intermedios referenciados
  por scripts secundarios (en `mercados_gastro/csv_intermedios_referenciados/`, con `README.md` de
  metadata). Separado por familia, conservando la subcarpeta de origen. Gitignored.
- **`_delete_candidates/`** — **Ya no existe.** Tras el cierre del 2026-06-29 quedó vacío: los 224
  SAFE se eliminaron y los 64 KEEP/REVIEW se movieron a `_archive_historico/`. No hay nada pendiente.
  Ver `AUDIT_REORG_FINAL.md` §11–§12 y `AUDIT_DELETE_CANDIDATES.csv`.
- **`MercadosGastro/` y `CasasDePastas/`** — Carpetas espejo con `final/` (copia del entregable
  vigente) y `archive_review/` (vacía). Punto navegable de "esto es lo final".
- **`_docs_reorganizacion/`** — Esta documentación: MANIFEST, DELETE_CANDIDATES, PATH_CHANGES,
  README_ESTRUCTURA, y la auditoría (AUDIT_REORG_FINAL, AUDIT_DELETE_CANDIDATES `.md`/`.csv`).

---

## 5. Dónde están los "finales" (resumen rápido)

| Línea | Final navegable | Fuente de verdad (regenerable) |
|---|---|---|
| Mercados | `MercadosGastro/final/MercadosGastroCABA_FINAL.pdf` | `outputs/mercados_caba/sanitized/MercadosGastroCABA_con_horarios.pdf` |
| Pastas | `CasasDePastas/final/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` | `outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` |

---

## 6. Reglas para seguir trabajando (recordatorio)

- **No mezclar** las tres líneas ni V2.
- **No commitear datos sensibles** (todo lo crudo/interno está gitignored; ver `.gitignore`).
- Antes de borrar la cuarentena, **revisar `DELETE_CANDIDATES.md`** y confirmar.
- El pipeline F01–F05 y V2 **no se tocan sin permiso explícito**.
- Drive es **solo lectura**.
