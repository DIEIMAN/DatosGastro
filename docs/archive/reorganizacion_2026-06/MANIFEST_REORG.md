# MANIFEST_REORG — Reorganización DataGastro

**Fecha:** 2026-06-29
**Rama:** `mercados-gastronomicos-v2`
**Modo aplicado:** "Solo mover lo SEGURO" (decisión de Diego).
**Commit / push:** NO se hizo commit ni push. No se usó `git add`.

> **Auditoría posterior (2026-06-29):** los 288 candidatos fueron auditados archivo por archivo.
> Ver `AUDIT_REORG_FINAL.md`, `AUDIT_DELETE_CANDIDATES.md` y `.csv`. Resultado: 164 SAFE,
> 42 KEEP_AS_ARCHIVE, 82 REVIEW_REQUIRED, 0 DO_NOT_DELETE. Prueba fuerte de dependencia: las
> cadenas de Mercados, Casas y DataGastro general regeneran/validan con la cuarentena desactivada.
> **Hallazgo:** `validate_mercados_setup.py` espera 62 archivos hoy en cuarentena (no es la cadena
> del PDF final, pero falla si se borran) → esos quedaron en REVIEW_REQUIRED.

---

## 1. Resumen de cambios

Se separaron y ordenaron tres líneas de trabajo **sin tocar el pipeline público F01–F05
ni los datos sensibles**, y sin borrar nada en forma definitiva.

- Las **versiones viejas, drafts, generadores legacy y QA antiguos** de Mercados y Casas de
  Pastas se movieron a `_delete_candidates/` (cuarentena), agrupados por tipo.
- Los **entregables vigentes** (PDF + insumos de su cadena de generación) se conservaron en
  su ubicación original (`outputs/.../sanitized/`, `docs/...`, `src/...`, `scripts/...`),
  porque los generadores los leen por ruta relativa y moverlos rompería la reproducibilidad.
- Se crearon carpetas espejo `MercadosGastro/` y `CasasDePastas/` con una subcarpeta
  `final/` que contiene una **copia** del entregable vigente, para tener un punto único y
  navegable de "esto es lo final". Los originales siguen en `outputs/` (fuente de verdad).
- **El pipeline general DataGastro (src raíz, data/, sql/, dashboard/, notebooks/, config/)
  quedó INTACTO.** Mover esos archivos rompía imports planos (`from config`, `from clean_text`),
  rutas SQL, dashboard y tests, y violaba el Guardrail 2 (no tocar el pipeline sin permiso).
- **DataGastro V2 (`config/v2/`, `data/v2/`, `docs/datagastro_v2/`, `outputs/v2/`,
  `schemas/`, `src/v2/`) quedó INTACTO** donde está. No se mezcló con Pastas ni Mercados.

### Reproducibilidad verificada (QA ejecutado)

- ✅ Se ejecutó la cadena vigente de **Mercados**
  (`src/mercados_caba/build_pdf_final_con_horarios.py`) end-to-end: regeneró el PDF, el
  resumen y el pack sin errores.
- ✅ Se ejecutó la cadena vigente de **Casas de Pastas**
  (`scripts/casas_pastas/build_pdf_integrado_v4.py`): regeneró el PDF (23 páginas) y el MD
  sin errores.
- ✅ Todos los sensibles/intocables verificados intactos (ver §5).

### Conteos

- Archivos movidos a cuarentena (`_delete_candidates/`): **288**
  - Mercados: **259** · Casas de Pastas: **29** · General: 0 · Unclear: 0
- Copias de entregables vigentes en `final/`: **4** (2 Mercados, 2 Pastas).
- `.gitignore`: se agregaron reglas defensivas para las carpetas nuevas (ver PATH_CHANGES).

---

## 2. Versión vigente fijada (confirmada por Diego)

| Línea | Entregable vigente | Generador vigente |
|---|---|---|
| **Mercados** | `outputs/mercados_caba/sanitized/MercadosGastroCABA_con_horarios.pdf` | cadena `build_pdf_final_con_horarios.py` |
| **Casas de Pastas** | `outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` | `scripts/casas_pastas/build_pdf_integrado_v4.py` |

> La cadena de Mercados NO es un solo script. Encadena dinámicamente:
> `build_pdf_final_con_horarios.py` → `build_pdf_final_entrega.py` →
> `build_pdf_final_v4_1_from_v3.py` → `build_pdf_from_markdown_master.py`,
> y consume visuales generados por `build_visuals_v5.py`. Por eso el "vigente" mezcla
> insumos V4_1 (docs/CSV) y V5 (gráficos). Todos esos eslabones se conservaron in situ.

---

## 3. Árbol final (resumido)

```
DataGastro/
├── src/                      # PIPELINE GENERAL — INTACTO (build_model, build_analytics, ...)
│   ├── mercados_caba/        # Solo cadena vigente Mercados (4 builders + visuals_v5 + validate)
│   └── v2/                   # INTACTO
├── data/                     # INTACTO (processed, raw, seeds, v2, internal_*)
├── sql/                      # INTACTO
├── dashboard/                # INTACTO
├── notebooks/                # INTACTO
├── config/                   # INTACTO (incl. config/v2)
├── schemas/                  # INTACTO (V2)
├── docs/
│   ├── (docs generales)      # INTACTO
│   ├── casas_pastas/         # Solo metodología + plan vigentes
│   ├── mercados_caba/        # Bitácora 00–26 + docs de la cadena vigente
│   └── datagastro_v2/        # INTACTO
├── outputs/
│   ├── casas_pastas_reporte/ # Solo V4 + insumos agregados (resto en cuarentena)
│   ├── casas_pastas*/        # Crudos sensibles — INTACTOS (gitignored)
│   └── mercados_caba/sanitized/  # Solo entregable vigente + insumos cadena + QA vigente
│
├── MercadosGastro/
│   ├── final/                # Copia: MercadosGastroCABA_FINAL.pdf + ResumenEjecutivo_FINAL.pdf
│   └── archive_review/       # (vacío — material dudoso iría aquí)
├── CasasDePastas/
│   ├── final/                # Copia: INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf + .md
│   └── archive_review/       # (vacío)
│
├── _delete_candidates/       # CUARENTENA — 288 archivos, NO borrados aún
│   ├── mercados_gastro/      # 259
│   ├── casas_de_pastas/      # 29
│   ├── datagastro_general/   # 0
│   └── unclear/              # 0
└── _docs_reorganizacion/     # Esta documentación
```

---

## 4. Archivos movidos por categoría

Detalle archivo-por-archivo (ruta original → nueva) en **`DELETE_CANDIDATES.md`**.
Resumen por grupo:

### Mercados → `_delete_candidates/mercados_gastro/`
- `pdfs_informes/` (11): PDFs de informe V3/V4/V5/V5_1/FINAL*/legacy `MercadosGastroCABA.pdf` y `con_horarios_v2`.
- `pdfs_resumenes/` (11): resúmenes ejecutivos PDF de las mismas versiones viejas.
- `packs_zip/` (19): packs entregables/documentales V0…V5_1 (menos el pack del vigente).
- `visuales_png/` (13): gráficos y mapas v3/v4 (los v5 vigentes quedaron in situ).
- `csv_intermedios/` (61): CSVs de relevamiento/candidatos/activos v0…v3 y duplicados.
- `docs_versiones_viejas/` (24): informes, anexos, auditorías y READMEs de versiones superadas.
- `generadores_legacy/` (7): builders viejos (informe_final v4/v5/v5_1, visuals v3/v4, con_horarios_v2, v4_from_v3).
- `validadores_legacy/` (9): validadores de versiones superadas.
- `qa_png/` (86): carpetas QA PNG de versiones viejas (la QA del vigente quedó in situ).
- `subcarpetas_intermedias/` (18): `compartible_v2_2/`, `documental_v2_1/`, `tablas_informe_v1_2/`.

### Casas de Pastas → `_delete_candidates/casas_de_pastas/`
- `informes_viejos/` (7): INFORME_CASAS_PASTAS y INTEGRADO / V2 / V3 (PDF+MD).
- `generadores_pdf_viejos/` (4): build_pdf_casas_pastas, integrado, _v2, _v3.
- `packs_revision/` (14): PACK_REVISION_EXTERNA_254 (sin sufijo) — el V4 quedó in situ.
- `docs_viejos/` (2): INFORME_CASAS_PASTAS.md e INTEGRADO.md superados.
- `checkpoints_txt/` (2): notas de trabajo TXT (DOMINGO_REVISION, SABADOALANOCHE_RECALL).

---

## 5. Archivos NO tocados por seguridad (intocables verificados)

Verificados presentes e intactos tras la reorganización:

- `.env`, `Algunas Cosas de Drive/`, `PROYECTOSGASTROAPARTENOREVISAR/` (+ `.zip`).
- `fuentes_internas_mercados_caba/`.
- `data/internal_raw/`, `data/internal_processed/`, `data/processed/`, `data/raw/`, `data/seeds/`.
- `outputs/casas_pastas/`, `outputs/casas_pastas_integrado/`, `outputs/casas_pastas_google_places/`,
  `outputs/casas_pastas_recall/`, `outputs/casas_pastas_reporte/anexos_internos/`.
- `outputs/mercados_caba/internal/`, `outputs/mercados_caba/raw/`.
- `outputs/analisis_interno/`, `outputs/inventario_drive/`, `exports/`.
- DataGastro V2: `config/v2/`, `data/v2/` (raw, processed, analytics), `docs/datagastro_v2/`,
  `outputs/v2/`, `schemas/`, `src/v2/`.
- Pipeline core: `src/build_model.py`, `src/build_analytics.py`, `src/validate_model.py`,
  `src/source_contracts.py`, `src/geocode_usig.py`, `sql/*`, `dashboard/`, `notebooks/`.

No se tocó Google Drive en ningún momento.

---

## 6. Dudas / ambigüedades (requieren revisión humana)

1. **`docs/mercados_caba/RESUMEN_EJECUTIVO_MERCADOS_GASTRONOMICOS_CABA_V4.md`** quedó in situ.
   La cadena vigente no lo referencia explícitamente, pero es el resumen .md más reciente.
   No se mandó a cuarentena para no perder un texto potencialmente útil. **Revisar si sigue vigente.**
2. **`docs/datagastro_v2.zip`** y **`docs/datagastro_v2/`**: hay un .zip y una carpeta del mismo
   nombre. El .zip parece un backup. No se movió (V2 es intocable por decisión). **Confirmar si el
   .zip es descartable.**
3. **Packs de revisión externa**: el `PACK_REVISION_EXTERNA_254` (sin sufijo) se mandó a cuarentena
   y el `_V4` quedó in situ. Contienen agregados sanitizados (no filas individuales), pero conviene
   que un humano confirme antes de borrar.
4. **`MercadosGastro/archive_review/` y `CasasDePastas/archive_review/` quedaron vacías.** Todo lo
   viejo se consolidó en `_delete_candidates/`. Si Diego prefiere distinguir "archivo histórico a
   conservar" de "candidato a borrar", se puede repartir en una segunda pasada.

---

## 7. Próximo paso

**Nada se borró.** Tras la revisión de `DELETE_CANDIDATES.md` por Diego y su confirmación
explícita, recién ahí se elimina `_delete_candidates/`.
