# PATH_CHANGES — Cambios de rutas y reproducibilidad

**Fecha:** 2026-06-29

---

## 1. Filosofía aplicada

Se priorizó **no romper reproducibilidad**. Los generadores vigentes leen y escriben por
**ruta relativa** dentro de `outputs/`, `docs/`, `src/`, `scripts/`. Por eso **NO se movieron
los insumos ni los entregables vigentes** de su ubicación original: solo se sacaron de en
medio las versiones viejas.

**Consecuencia:** los comandos de regeneración **NO cambiaron**. Siguen siendo los de antes.

---

## 2. Scripts NO modificados (no hizo falta tocar imports/paths)

No se editó ningún `.py` de las cadenas de generación. Quedaron intactas en su carpeta original:

- Mercados: `src/mercados_caba/build_pdf_final_con_horarios.py` (+ los 3 builders que encadena
  + `build_visuals_v5.py` + `validate_mercados_final_con_horarios.py`).
- Casas de Pastas: `scripts/casas_pastas/build_pdf_integrado_v4.py`.

Ambas cadenas se **ejecutaron tras la reorganización y funcionaron** (ver MANIFEST §1).

> **Edición posterior (rev.2, 2026-06-29):** se actualizó **`src/mercados_caba/validate_mercados_setup.py`**
> para validar SOLO la cadena vigente (antes exigía 62 archivos históricos hoy en cuarentena, y fallaba
> con 68 errores tras la reorganización). El validador actualizado verifica: builders de la cadena,
> insumos docs/CSV/PNG vigentes, salida final + copia en `MercadosGastro/final/`, y sobre el PDF final
> 14 páginas, footer, anclas p7/p11/p14 y ausencia de 'V4_1'. Conserva los guardrails de privacidad,
> gitignore y `.env`. **No cambió ninguna ruta de generación.** Resultado: EXIT 0, 0 errores.

---

## 3. Comandos para regenerar los informes vigentes

Sin cambios respecto de antes. Desde la raíz del repo, con el venv activo:

### Mercados Gastronómicos CABA (vigente)
```powershell
python src\mercados_caba\build_pdf_final_con_horarios.py
python src\mercados_caba\validate_mercados_final_con_horarios.py   # QA
```
Salida: `outputs\mercados_caba\sanitized\MercadosGastroCABA_con_horarios.pdf`
(+ `ResumenEjecutivo_...` + `PACK_MercadosGastroCABA_con_horarios.zip`).

> Si se necesita regenerar los gráficos v5 primero:
> ```powershell
> python src\mercados_caba\build_visuals_v5.py
> ```

### Casas de Pastas (vigente)
```powershell
python scripts\casas_pastas\build_pdf_integrado_v4.py
```
Salida: `outputs\casas_pastas_reporte\INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` (+ `.md`).
Lee el padrón depurado desde `outputs\casas_pastas_integrado\` (sensible, gitignored, intacto).

---

## 4. Cambios de ruta efectivos (solo carpetas nuevas)

| Qué | Dónde está la fuente de verdad | Copia/espejo nuevo |
|---|---|---|
| PDF final Mercados | `outputs/mercados_caba/sanitized/MercadosGastroCABA_con_horarios.pdf` | `MercadosGastro/final/MercadosGastroCABA_FINAL.pdf` |
| Resumen final Mercados | `outputs/mercados_caba/sanitized/ResumenEjecutivo_MercadosGastroCABA_con_horarios.pdf` | `MercadosGastro/final/ResumenEjecutivo_MercadosGastroCABA_FINAL.pdf` |
| Informe final Pastas | `outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` | `CasasDePastas/final/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` |

> Las copias en `final/` son **snapshots de conveniencia**. Si se regenera el informe, la copia
> NO se actualiza sola: re-copiar manualmente desde `outputs/` si se quiere refrescar.

**Cierre de limpieza (2026-06-29):** se eliminaron los 224 SAFE y se movieron los 53 KEEP a
`_archive_historico/`. Quedan 11 CSV REVIEW_REQUIRED en `_delete_candidates/mercados_gastro/csv_intermedios/`.
`.gitignore` ahora también cubre `_archive_historico/`. Nada de esto afecta rutas de generación.

Las versiones viejas se movieron a `_delete_candidates/` (ver DELETE_CANDIDATES.md). Como eran
PDF/zip/QA gitignorados o untracked, esos movimientos no afectan a ningún script.

---

## 5. Cambio en `.gitignore`

Se agregaron reglas defensivas para que las carpetas nuevas **no se commiteen por accidente**
(Guardrail 8 — no commitear datos internos):

```
_delete_candidates/
MercadosGastro/final/
MercadosGastro/archive_review/
CasasDePastas/final/
CasasDePastas/archive_review/
```

---

## 6. Riesgos / cosas a vigilar

- **Archivos `.md` trackeados movidos a cuarentena** (p. ej. informes V3/V4 de Mercados que
  estaban versionados): git los verá como `deleted` en el working tree. **No se hizo commit**,
  así que el historial está intacto; si se quiere revertir, basta restaurarlos desde
  `_delete_candidates/` o con `git restore`.
- **Las copias en `final/` se desincronizan** si se regenera el informe (ver §4).
- **No se tocó el pipeline F01–F05 ni V2.** Cualquier reorganización física de esos módulos
  requeriría reescribir imports planos y rutas, y permiso explícito de Diego.
