# Plan de limpieza del repo — 2026-08-07

Relevamiento de duplicados, zips de entrega y archivos sin uso. **Nada fue borrado ni movido**:
este documento es el plan previo que exige la skill `datagastro-limpieza`; cada bloque se ejecuta
solo con confirmación de Diego. Cuarentena disponible: `_delete_candidates/` (ya en `.gitignore`).

Contexto de tamaño: `outputs/` pesa 5,4 GB. Un solo archivo (el dump global de All The Places,
2,9 GB) es más de la mitad. Los duplicados exactos por hash (>100 KB, fuera de `.git`/`.venv`/
`node_modules`) suman **696 grupos y ~420 MB de espacio repetido**, el 95 % dentro de
`outputs/polos_gastro/`. Ningún `.zip` está versionado en git (`*.zip` está en `.gitignore`),
así que todo lo listado es solo disco local: borrar no afecta el historial.

---

# SEGUNDA RONDA — auditoría ampliada (2026-08-07, tarde)

Diego pidió no borrar el dump de All The Places por ahora, y buscar otras cosas realmente
inservibles: versiones viejas de informes, restos de entorno, lo que sea. Se escaneó el repo
completo (11.981 archivos, 6,06 GB fuera de `.git`/`.venv`/`node_modules`).

## S1. Basura técnica — borrado sin ninguna repercusión (~82 MB)

Nada de esto es insumo, entregable ni evidencia. Todo se regenera o ya está declarado obsoleto.

| Ítem | Peso | Por qué no tiene repercusión |
|---|---|---|
| `graphify-out/` | 42 MB | El propio `CLAUDE.md` lo declara *"stale copy from a previous version — do not use it"*. El grafo vigente es `.graphify/` (regenerado hoy 15:59). |
| `tmp_pdf_preview/` | 23 MB | Renders PNG de QA de PDFs de junio–julio. Regenerables con `scripts/qa/pdf_check.py`. |
| `tmp/` | 12 MB | 5 logs casi idénticos de análisis tanda2 (`tanda2_analysis*.log`), PNG de QA sueltos, inspecciones de PDFs de diman, y `tmp/tanda2_zip_audit/` = extracción temporal de `REVISION_CODEX_TANDA2_EJECUCION_V1.zip`, que sigue existiendo intacto con su `.sha256`. |
| `__pycache__/` fuera de `.venv` | ~5,6 MB / 80 dirs | Bytecode. Precedente autorizado el 2026-07-13 (`docs/NOTA_LIMPIEZA_PYC_TANDA2.md`). |
| `scripts/outputs/` | 74 KB | Artefacto de un script corrido con directorio equivocado: contiene `mercados/INFORME_MERCADOS_DGDGAS.pdf` del 2026-07-02 (73 KB), versión previa y distinta del vigente `outputs/mercados/...` del 07-04 (302 KB). El resto son carpetas vacías. |
| 22 carpetas vacías | 0 | Incluye `.codex/`, `outputs/graficos`, `outputs/mapas`, `outputs/notebooks`, `data/internal_raw`, `data/v2/raw`, `CasasDePastas/archive_review`, `MercadosGastro/archive_review`, y 5 subcarpetas de `INFORMEFINAL/claude/fable_preflight_tecnico_tanda2_v1/`. |
| 11 stubs de 0 bytes | 0 | Los `.gdoc`/`.gsheet` de `Algunas Cosas de Drive/`: punteros de Drive sin contenido. |

**Excepción a respetar:** no tocar `data/v2/analytics/.gitkeep` ni `outputs/v2/sanitized/.gitkeep`
(archivos vacíos a propósito, sostienen carpetas versionadas).

## S2. Copias de espejo y versiones intermedias — borrado seguro pero con criterio (~7 MB)

- **`Cafesito/final/`**: 14 de sus 15 archivos son duplicados exactos de `outputs/cafecito/`
  (4,1 MB). El único propio es `INFORME_CAFECITO_DGDGAS_REVISION_4_EDITABLE.docx`. La carpeta
  está en `.gitignore` (línea 85) como espejo, igual que las de Mercados y Casas de Pastas.
  Si el espejo se usa para abrir cosas rápido, dejarlo; si no, borrar los 14 duplicados.
- **Versiones intermedias del informe Cafecito** (~2,6 MB): en `outputs/cafecito/` conviven 15
  PDFs de la misma pieza — `V2, V3, V4, V5, V6, V6_1, FINAL, FINAL_EDITABLE_TEST, REVISION_1,
  REVISION_2, REVISION_2_FORMATO, REVISION_3, REVISION_4`. La vigente es **REVISION_4**
  (2026-07-04). Las 10 anteriores a `REVISION_2` son iteraciones de un mismo día (29–30 de junio)
  que ya nadie va a abrir. Recomendación: conservar `REVISION_4`, `REVISION_3` y el
  `_EDITABLE`; borrar el resto.

## S3. Lo que parecía candidato pero NO se puede borrar

Verificado uno por uno; se documenta para no volver a proponerlo:

- **`data/fuentes_externas/usos_suelo/shp/` (540 MB).** Parecía extracción redundante del zip
  de 87 MB, pero **5 scripts del barrido lo leen en vivo** por glob (`build_base_gastronomica.py`,
  `capa_rus_por_zona.py`, `cruzar_places_padron.py`, `preparar_campo_barrio.py`). Es insumo activo.
  *Lo que sí sobra es el zip `rus_2022_2024_shp.zip` (87 MB)*, ya que su contenido está extraído
  y en uso — mismo caso que ATP: fuente pública, queda a criterio de Diego.
- **`INVESTIGACION_DESBLOQUEOS_V21/_fuente_zip_solo_lectura/` (16 MB).** Solo 22 de 48 archivos
  coinciden con `ATLAS_V2/`: es la versión V2 **previa** a la corrección V2.1, conservada como
  referencia congelada de la investigación. No es copia: es evidencia.
- **`outputs/polos_gastro/FASE5-29/` (192 MB) y los históricos de INFORMEFINAL.** Son 14 PDFs de
  fases superadas por ATLAS_V2, pero `ESTADO_GENERAL_INFORMEFINAL.md` conserva los históricos
  **deliberadamente**: "Atlas V1 completa — CERRADO_Y_CONGELADO: respaldo institucional completo
  y auditable, *no invalidado por V2*". Borrarlos rompería la trazabilidad del ciclo una-pasada.
- **`node_modules/` (21 MB).** Regenerable con `npm install`, pero el experimento que lo usa
  (`scripts/polos_gastro/cartografia_experimentos/usig_mapa_interactivo_minimo/`) sigue en el
  repo y está citado en 10 documentos de cartografía. Borrar solo si el experimento se declara
  cerrado.
- **Contact sheets de QA en paquetes sellados** (~70 MB entre ATLAS_V2 y atlas_22/cartografía_22).
  Son renders regenerables, pero viven dentro de paquetes con `CHECKSUMS_SHA256.txt` y sellado
  "157/157". Tocarlos invalidaría el sellado.
- **20 MB de duplicados exactos en archivos chicos** (1.013 grupos, 1–100 KB). Están casi todos
  *dentro* de paquetes de revisión sellados, donde la repetición es intencional (cada paquete se
  arma autocontenido). No se toca.

---

## A. Seguro borrar (regenerable o copia exacta; ~340 MB)

**A1. Carpetas extraídas junto a su propio zip (~265 MB, 33 pares).**
Patrón dominante: cada paquete de revisión existe como `REVISION_X.zip` **y** como carpeta
`REVISION_X/` al lado, con contenido idéntico. Propuesta: **conservar el zip (entregable sellado)
y borrar la carpeta extraída**, que se regenera descomprimiendo. Los pares grandes:

- `outputs/polos_gastro/INFORMEFINAL/codex/tanda1_saturaciones_v4_4/paquete_revision/REVISION_TANDA1_SATURACIONES_V4_4/` (42 MB) y `..._CIERRE_POST_ADDENDUM/` (42 MB)
- `outputs/polos_gastro/FASE5-29/fase28.../REVISION_INFORME_POLITICO_INTEGRADO_V2_1/` (18 MB), `fase29.../..._V2_2/` (16 MB), `fase27.../..._V2/` (10 MB)
- `outputs/polos_gastro/corrida_territorial_v3/REVISION_CORRIDA_TERRITORIAL_V3/` (16 MB) **más** `REVISION_CORRIDA_TERRITORIAL_V3_EXTRACCION_QA/` (16 MB, extracción de la extracción)
- `outputs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/`: `REVISION_CLAUDE_PRE_FASE26_V4/` (16 MB), `REVISION_HUMANA_COMPLETA_V1/` (11 MB), `REVISION_CARTOGRAFIA_EDITORIAL_V2/` (10 MB), `REVISION_DESIGN_PRE_FASE26_V4_2/` (9 MB), `REVISION_CLAUDE_PRE_FASE26_V4_1/` (9 MB)
- `outputs/polos_gastro/INFORMEFINAL/codex/tanda2_auditoria_metodologica_v1_1/paquete_revision/REVISION_CODEX_TANDA2_AUDITORIA_METODOLOGICA_V1_1/` (11 MB)
- `correcciones_cartograficas_post_qa_v3_1/REVISION_...` (7 MB), `expansion_candidatos_v4_tanda1/REVISION_...` (6 MB), prototipos híbridos (5+4+4 MB), `PAQUETE_DECISIONES_DIEGO/` (4 MB)
- 13 pares menores de ~1–2 MB (evidencia documental, infraestructura v1/v1.1/hotfix, preflights, casas de pastas `PACK_REVISION_EXTERNA_254_V4/`)

**A2. Carpetas temporales de QA (35 MB).**
- `tmp_pdf_preview/` (23 MB): renders PNG de QA de PDFs de junio–julio, todos regenerables con `scripts/qa/pdf_check.py`.
- `tmp/` (12 MB): logs de análisis tanda2 (5 copias casi iguales), PNG de QA sueltos, `tmp/tanda2_zip_audit/` (2,9 MB duplicado exacto), inspecciones de PDFs de diman. Todo de julio, ciclos ya cerrados.

**A3. `graphify-out/` (42 MB).** Copia obsoleta de una versión anterior del grafo; el CLAUDE.md ya
la declara "stale — do not use". El grafo vigente vive en `.graphify/`.

**A4. `deliverables/diman_reporting_bridge/` (parcial, ~1,5 MB).**
- `datagastro_diman_reporting_bridge_v1_final.zip` y `..._v1_final_clean.zip` son **idénticos**
  (mismo hash MD5 `c57216a8...`). Borrar uno (sugerido: conservar `_final_clean`).
- Las tres extracciones de QA `_qa_clean_extract_v1/`, `_qa_clean_extract_final_v1/` y
  `_qa_clean_extract_final_v1_clean/` son restos del control del paquete; el zip queda como registro.

**A5. `__pycache__/` fuera de `.venv` (~80 directorios).** Bytecode regenerable en `scripts/`,
`src/`, `dashboard/`, `tests/`, `deliverables/` y outputs de codex/grok. Precedente: Diego ya
autorizó este tipo de borrado el 2026-07-13 (`docs/NOTA_LIMPIEZA_PYC_TANDA2.md`), aunque acotado
a una superficie puntual; este bloque amplía esa superficie y por eso se vuelve a pedir OK.
**Excepción:** no tocar los `__pycache__` dentro de paquetes congelados de INFORMEFINAL si algún
manifiesto de hashes los inventaría (verificar antes de ejecutar).

**A6. Archivos stub de 0 bytes en `Algunas Cosas de Drive/`** (`*.gdoc`, `*.gsheet`, 10 archivos):
son accesos directos de Google Drive copiados a disco, no contienen datos.

**A7. `_to_delete/`** (44 KB, un solo archivo `_cotejo_docx_texto.txt`): ya estaba marcado para borrar.

## B. Revisar con Diego antes de decidir

**B1. `data/fuentes_externas/all_the_places/output_2026-08-01-13-32-15.zip` (2,9 GB).**
La mayor ganancia posible. Es el dump global crudo de All The Places; el recorte CABA ya está
extraído al lado (`atp_caba.csv`, 422 KB, con `atp_recorte_meta.json` que documenta la corrida:
44,7 M de líneas → 6.682 candidatas). Es fuente pública re-descargable, por eso no entra en
"seguro" (guardrail: datos fuente públicos no se borran sin permiso). Opciones: (a) borrar y
anotar la URL de origen en el meta, (b) mover a disco externo, (c) dejar. Recomendación: (a),
dejando registrada versión/fecha del dump en el meta.

**B2. Zips de revisión de ciclos cerrados (julio, ~250 MB en total).**
Los ~90 zips `REVISION_*`/`PAQUETE_*` de codex/grok/claude son el registro sellado del ciclo de
auditorías de Polos (tandas 1–2, grupos A–C, atlas 22). No son basura: son evidencia del ciclo
una-pasada. Propuesta conservadora: conservarlos donde están, o moverlos en bloque a
`_archive_historico/polos_revision_packs_2026-07/` si molestan en `outputs/`. Decisión de Diego.

**B3. Duplicaciones docs/ vs outputs/.**
- `docs/polos_gastro/preintegracion_editorial_v3.zip` (20 KB) vs `outputs/polos_gastro/preintegracion_editorial_v3.zip` (21 KB): tamaños distintos — determinar cuál es el vigente y borrar el otro.
- `docs/datagastro_v2.zip` (29 KB, junio): parece un paquete viejo de docs; confirmar si algo lo referencia.

**B4. Copias de planillas internas.**
`Algunas Cosas de Drive/Copia de Base de datos DGDGAS EVENTOS.xlsx` es duplicado exacto del que
está en `fuentes_internas_mercados_caba/`. Las otras dos (`ADE I SEGUIMIENTO`, `Recap eventos`)
solo existen ahí. Propuesta: consolidar todo en `fuentes_internas_mercados_caba/` (ya ignorada
por git) y vaciar `Algunas Cosas de Drive/`. Son datos internos: no borrar sin confirmar que la
copia canónica queda.

**B5. `node_modules/` + `package.json` (21 MB).** Solo lo usa el experimento
`scripts/polos_gastro/cartografia_experimentos/usig_mapa_interactivo_minimo/`. Regenerable con
`npm install`. Si el experimento sigue vivo, dejar; si quedó superado por la cartografía actual,
borrar `node_modules/` y conservar el código.

**B6. Duplicados de informes finales entre carpetas espejo** (~7 MB): `MercadosGastroCABA_FINAL.pdf`
y `INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` existen en 3 lugares cada uno (carpeta espejo del
subproyecto, `outputs/`, y `outputs/datagastro_design_system/claude_design_pack/referencias/`).
Las carpetas espejo (`MercadosGastro/final/`, `CasasDePastas/final/`) están documentadas en el
`.gitignore` como copias intencionales — probablemente dejar como está; se lista por completitud.

**B7. `fuentes_internas_mercados_caba/DataMercados.zip` (130 MB).** El contenido parece ya
extraído en la misma carpeta (decenas de PDFs/docx internos). Si la extracción está completa, el
zip es redundante — pero es fuente interna original: confirmar antes.

## C. No borrar (aunque parezcan candidatos)

- Outputs finales y congelados: `outputs/polos_gastro/INFORMEFINAL/` (salvo extracciones A1),
  `ATLAS_V2/` (PDFs, qa/, scripts), `REFERENTES_2026/`, informes de cafecito/mercados/pastas.
- `data/processed/`, `data/analytics/`, `src/`, `dashboard/`, `notebooks/` (guardrail 2).
- Fuentes: `data/fuentes_externas/` (censo, RUS, radios censales — zips fuente),
  `fuentes_internas_mercados_caba/` (salvo B7), `exports/` (packs de entrega de pastas).
- `_archive_historico/` (KEEP_AS_ARCHIVE explícito en `.gitignore`).
- `.graphify/` (grafo vigente), `.venv/`, `scripts/`, `docs/`, `tests/`, `configs/`, `kpis_lock`.

---

## Registro de ejecución — 2026-08-07 (autorizado por Diego)

Diego autorizó borrar los zips con carpeta extraída existente y los duplicados exactos. Ejecutado:

- **35 zips borrados (~176 MB)**: todos los `REVISION_*`/`PAQUETE_*` (y `docs/datagastro_v2.zip`,
  ambos `preintegracion_editorial_v3.zip`) cuya carpeta extraída existía al lado. Cada zip se
  verificó archivo por archivo contra su carpeta (nombre + tamaño, 100 % presente) antes de borrar.
  La carpeta queda como registro del paquete.
- **Duplicados exactos borrados (~20 MB)**: `REVISION_CORRIDA_TERRITORIAL_V3_EXTRACCION_QA/`
  (idéntica por `diff -r` a la carpeta que queda), y en `deliverables/diman_reporting_bridge/`:
  `..._v1_final.zip` (MD5 idéntico a `..._v1_final_clean.zip`, que queda), las tres carpetas
  `_qa_clean_extract*` y las dos `_final_staging*` (idénticas salvo bytecode `.pyc`; el contenido
  sellado vive en `..._v1_final_clean.zip`).
- **NO borrados**: `outputs/casas_pastas_reporte/PACK_REVISION_EXTERNA_254_V4.zip` (2 archivos
  difieren de la carpeta → el zip no es redundante) y el pack en `_archive_historico/`
  (KEEP_AS_ARCHIVE). Los ~73 zips de revisión restantes no tienen carpeta extraída: son el único
  registro sellado y quedan.
- Siguen pendientes de autorización: A2 (tmp), A3 (graphify-out), A5 (pycache), A6 (stubs), A7,
  y todo el bloque B.

## Ejecución propuesta (cuando Diego confirme)

1. Bloque A completo → mover a `_delete_candidates/2026-08-07/` (cuarentena) o borrado directo,
   a elección. Con cuarentena, purga definitiva a los ~30 días.
2. Bloque B → decidir ítem por ítem; B1 solo tras anotar procedencia del dump en el meta.
3. Verificación posterior: `python -m unittest discover tests` + `graphify update .` no deberían
   verse afectados (nada del bloque A toca código ni datos fuente).
