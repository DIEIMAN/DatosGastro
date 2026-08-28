# Auditoría completa del repositorio — 2026-08-28

Pedido de Diego: el repo quedó ilegible (mil versiones de informes, zips, restos) y quiere
una separación clara: **lo general que usan todos los subproyectos** por un lado, y
**Polos Gastro / Cafecito / Panaderías / Casas de Pastas / Mercados / etc.** cada uno en su lugar.

**Nada fue borrado ni movido.** Este documento es el diagnóstico + la propuesta. Cada bloque
se ejecuta sólo con confirmación explícita (guardrail 9, skill `datagastro-limpieza`).

Antecedente directo: `docs/PLAN_LIMPIEZA_REPO_2026_08_07.md` (auditoría de borrado de hace 3
semanas, ejecutada parcialmente). Esta auditoría lo actualiza y agrega la dimensión que aquella
no tenía: la **reorganización por subproyecto**.

---

## 1. Números generales

| Métrica | Valor |
|---|---|
| Tamaño total (sin `.git`, `.venv`, `node_modules`) | **~9,4 GB** |
| `outputs/` | **8,4 GB** (13.424 archivos) — el 89 % del repo |
| Archivos trackeados por git | 1.966 (de ellos 1.081 en `outputs/`, 486 en `docs/`) |
| Archivos físicos totales en outputs | 13.424 → **el 92 % de outputs NO está en git** (datos crudos, PNG, zips) |
| Zips | **137 zips, 3,74 GB** (2,8 GB es uno solo: el dump de All The Places) |
| Directorios de primer nivel | **42** (deberían ser ~15) |
| Estado git al momento de auditar | 567 modificados + 233 sin trackear (branch `mercados-gastronomicos-v2`) |

### Los cinco pesos pesados de `outputs/` (7,6 GB de los 8,4)

| Carpeta | Peso | Qué es |
|---|---|---|
| `data/fuentes_externas/` | 3,6 GB | Fuentes descargadas (ATP 2,8 GB + RUS + censo + OSM + Overture). **No es un output: es insumo.** |
| `outputs/ATLAS_INFORMATIVO_39_2026-08-13/` | 1,5 GB | Línea Atlas vigente (39 polos) |
| `outputs/polos_gastro/` | 1,5 GB | Todo el ciclo histórico de Polos (fases 5–29, INFORMEFINAL, ATLAS_V2, experimentos) |
| `outputs/BARRIDO_CIUDAD_2026-08/` | 422 MB | Barrido Places de la Ciudad |
| `ATLAS_GASTRONOMICO_*_2026-08-12/` (4 carpetas) | 909 MB | **Cuatro iteraciones sucesivas del mismo documento** de un solo día |

---

## 2. Diagnóstico: por qué no se entiende nada

### 2.1 La raíz tiene 42 directorios y mezcla cinco épocas

En la raíz conviven:

- **Núcleo vigente**: `src/`, `scripts/`, `data/`, `docs/`, `outputs/`, `tests/`, `sql/`, `schemas/`, `dashboard/`, `notebooks/`.
- **Carpetas espejo pre-reorganización de junio**: `Cafesito/`, `CasasDePastas/`, `MercadosGastro/`, `PolosGastro/` (copias "para abrir rápido", documentadas en `.gitignore`; `CasasDePastas` y `MercadosGastro` tienen 2 archivos cada una).
- **Restos administrativos**: `_to_delete/` (125 MB que nunca se borraron), `_archive_historico/`, `_docs_reorganizacion/` (docs de la reorg de junio), `Algunas Cosas de Drive/` (copias manuales de Drive + stubs .gdoc de 0 bytes), `%SystemDrive%/` (**artefacto de un comando mal escapado** — contiene un `ProgramData` fantasma).
- **Duplicación de convención**: `config/` **y** `configs/` (una trae fuentes_externas+v2, la otra encuestas); `cache/` suelto en la raíz (2 JSON); `exports/` y `deliverables/` que son en realidad outputs de entrega.
- **Obsoletos declarados**: `graphify-out/` (39 MB, el propio CLAUDE.md dice "stale — do not use"), `tmp/` (35 MB), `tmp_pdf_preview/` (22 MB), `PROMPT_CLAUDE_CODE_CORREDORES.md` suelto en la raíz.

### 2.2 `outputs/` mezcla tres cosas de naturaleza distinta

1. **Insumos** disfrazados de outputs: `data/fuentes_externas/` (3,6 GB de fuentes descargadas). Debería vivir bajo `data/`.
2. **Outputs por subproyecto** (lo correcto): `outputs/cafecito/`, `outputs/panaderias/`, `outputs/mercados_caba/`…
3. **Outputs por evento/fecha en la raíz de outputs**: 15 carpetas MAYÚSCULAS con fecha (`ATLAS_GASTRONOMICO_*_2026-08-12` ×4, `AUDITORIA_INDEPENDIENTE_*` ×3, `CORRECCION*` ×2, `ENTREGA_REUNION_2026-08-18`, `HALLAZGOS_*`, `DECISIONES_EDITORIALES_*`, `UNIFICACION_*`, `FICHAS_REFERENTES_*`, `PAQUETE_CONTEXTO_2026-08`). **Todas son del ciclo Atlas/Polos** pero viven sueltas al lado de los subproyectos, y son la principal causa de que "no se entienda nada".

### 2.3 Casas de Pastas está repartida en 6 carpetas de outputs + 2 de docs

`outputs/casas_pastas/` (build vigente 2026-08), `casas_de_pastas/` (1 PDF), `casas_pastas_reporte/`, `casas_pastas_integrado/`, `casas_pastas_google_places/`, `casas_pastas_recall/` — más `exports/casas_pastas_subproyecto/` y `_archive_historico/casas_de_pastas/`. En docs: `docs/casas_pastas/` **y** `docs/casas_de_pastas/`. Ocho lugares para un rubro.

### 2.4 Mercados: cuatro nombres

`outputs/mercados/`, `outputs/mercados_caba/`, `docs/mercados/`, `docs/mercados_caba/`, `MercadosGastro/`, `fuentes_internas_mercados_caba/` (254 MB en la raíz, con `DataMercados.zip` de 124 MB probablemente ya extraído al lado).

### 2.5 Polos/Atlas: la historia entera está viva y desplegada

`outputs/polos_gastro/` tiene 44 entradas mezclando: línea vigente (`INFORMEFINAL/`, `ATLAS_V2/`, `REFERENTES_2026/`), 20+ carpetas de revisiones/fases superadas (`REVISION_*`, `FASE5-29/`, `evidencia_documental_*` v1/v1.1/v4/v4.1…), CSVs seed de la etapa inicial, y un zip huérfano con "(2)" en el nombre. Además la línea Atlas más nueva vive **fuera** (`outputs/ATLAS_INFORMATIVO_39_2026-08-13/` + las 15 carpetas fechadas de §2.2). Hoy, para saber qué es lo vigente hay que leer `ESTADO_GENERAL_INFORMEFINAL.md` — la estructura no lo dice.

### 2.6 Infraestructura de agentes triplicada en tres superficies

`infraestructura_agentes_skills_v1`, `_v1_1`, `_v1_1_1_hotfix` existen **en docs/, en scripts/ y en outputs/** (9 carpetas). Más `agent_skills/`, `.agents/`, `.claude/skills/`, `docs/skills_claude/`. Es historia de versiones desplegada como si todo estuviera vigente.

### 2.7 Pendientes del plan del 08-07 que siguen sin ejecutar

Del plan anterior quedó autorizado y hecho el borrado de 35 zips redundantes (~196 MB). Sigue todo lo demás: `tmp/` + `tmp_pdf_preview/` (57 MB), `graphify-out/` (39 MB), `__pycache__` (~80 dirs), stubs de Drive, `_to_delete/` (que en vez de vaciarse **creció a 125 MB**), y las decisiones B (dump ATP 2,8 GB, DataMercados.zip, node_modules, planillas de Drive).

---

## 3. Propuesta de estructura objetivo

Principio: **primer nivel = general vs subproyecto**, y dentro de cada subproyecto la misma
tríada `docs / scripts / outputs` (los datos fuente quedan centralizados en `data/` porque los
universos F/I/E son transversales — guardrail 3).

```
DataGastro/
├── CLAUDE.md, AGENTS.md, README.md, requirements.txt
├── src/                      # pipeline F01–F05 — INTACTO (guardrail 2)
├── data/                     # fuentes: raw, processed, analytics, geo, seeds — INTACTO
│   └── fuentes_externas/     # ← data/fuentes_externas (ATP, RUS, censo, OSM, Overture)
├── dashboard/  notebooks/  sql/  schemas/  tests/   # INTACTOS
├── config/                   # ← fusiona configs/ (encuestas) dentro de config/
├── scripts/
│   ├── shared/  qa/  compat/           # lo transversal
│   └── <subproyecto>/                  # ya está así — se mantiene
├── docs/
│   ├── general/              # diccionario, contratos, guías, changelog (hoy sueltos en docs/)
│   ├── skills_claude/  revisiones/  estudios_de_rubro/
│   ├── <subproyecto>/        # un solo dir por subproyecto (fusionar casas_*, mercados*)
│   └── archive/              # infraestructura v1/v1.1/hotfix, legacy, reorg de junio
├── outputs/
│   ├── polos_gastro/
│   │   ├── VIGENTE/          # INFORMEFINAL, ATLAS_V2, REFERENTES_2026, atlas 39 + fechadas 08-12/08-13
│   │   └── historico/        # FASE5-29, REVISION_*, evidencias v1–v4, experimentos cerrados
│   ├── barrido_ciudad/       # ← BARRIDO_CIUDAD_2026-08
│   ├── cafecito/  panaderias/  mercados/  casas_pastas/   # un dir por rubro, con historico/ adentro
│   ├── analisis_interno/     # (ignorado por git, como hoy)
│   ├── entregas/             # ← exports/ + deliverables/ + ENTREGA_REUNION_*
│   └── tablas_resumen/
└── _archive_historico/       # + espejos Cafesito/CasasDePastas/MercadosGastro/PolosGastro si se conservan
```

Notas de diseño:

- **Los paquetes sellados de Polos no se abren ni se renombran por dentro** (checksums SHA256):
  se mueven carpetas enteras, nunca su contenido.
- La partición VIGENTE/historico de Polos replica exactamente lo que ya declara
  `ESTADO_GENERAL_INFORMEFINAL.md`; la estructura pasa a decir lo que hoy sólo dice ese doc.
- Las 4 carpetas `ATLAS_GASTRONOMICO_*_2026-08-12` son iteraciones del mismo día: la última en
  la cadena queda en VIGENTE, las 3 previas en historico (909 MB → ~640 MB a historico).
- `casas_pastas`: `outputs/casas_pastas/` (build 2026-08 vigente) queda como canónica; reporte,
  integrado, google_places y recall pasan a `casas_pastas/historico/` (son la línea V4 de julio,
  superada por el build por habilitación).
- Mercados: unificar bajo `mercados/`; `fuentes_internas_mercados_caba/` → `data/fuentes_internas/mercados/`.

## 4. Qué se borra (no sólo se mueve) — requiere confirmación aparte

| Ítem | Peso | Riesgo |
|---|---|---|
| `_to_delete/` completo | 125 MB | Nulo: ya estaba marcado; los zips `repo_0X` del candidato editorial tienen su fuente en outputs |
| `graphify-out/` | 39 MB | Nulo: declarado stale en CLAUDE.md |
| `tmp/`, `tmp_pdf_preview/` | 57 MB | Nulo: QA regenerable (plan 08-07, bloque A2) |
| `%SystemDrive%/` | ~1 MB | Nulo: artefacto de comando mal escapado |
| `__pycache__` fuera de .venv | ~6 MB | Nulo (verificando manifiestos de paquetes sellados) |
| Stubs .gdoc/.gsheet 0 bytes | 0 | Nulo |
| `outputs/polos_gastro/REVISION_EVIDENCIA_DOCUMENTAL_EXPANSION_V4 (2).zip` | — | Duplicado con "(2)": verificar hash contra la carpeta y borrar |
| **Decisiones B heredadas**: dump ATP (2,8 GB), `DataMercados.zip` (124 MB), `node_modules` (21 MB), planillas Drive | ~3 GB | Cada una es una decisión tuya; el plan 08-07 detalla opciones |

## 5. Riesgos y salvaguardas del movimiento

1. **Rutas hardcodeadas**: 179 scripts trackeados leen/escriben rutas de outputs. Antes de mover
   cada carpeta hay que grepear su ruta en `scripts/`, `src/`, `docs/` y parchear o dejar la
   carpeta donde está. Los movimientos se hacen con `git mv` para preservar historia.
2. **Pipeline intacto**: `src/`, `data/processed`, `data/analytics`, `dashboard/`, `notebooks/`
   no se tocan (guardrail 2). `data/fuentes_externas/` es carpeta **nueva** bajo data, no toca lo existente.
3. **Paquetes sellados**: mover sólo el contenedor; correr después una verificación de checksums
   de 2–3 paquetes al azar.
4. **Ejecución por fases con commit por fase**, para poder revertir cualquier paso:
   - **F0** — borrado de basura técnica (§4 filas 1–7).
   - **F1** — raíz: fusionar config/configs, mover cache, archivar `_docs_reorganizacion`, `Algunas Cosas de Drive`, prompt suelto.
   - **F2** — `data/fuentes_externas` → `data/fuentes_externas` + parcheo de rutas (la más delicada: 5+ scripts del barrido leen el RUS en vivo).
   - **F3** — consolidación Polos/Atlas (VIGENTE vs historico + las 15 carpetas fechadas).
   - **F4** — consolidación por rubro (casas_pastas ×6, mercados ×4, entregas).
   - **F5** — docs: general/, fusiones, archive de infraestructura v1/v1.1/hotfix.
   - Tras cada fase: `python -m unittest discover tests` + `graphify update .` + smoke de los scripts afectados.

---

**Estado: DIAGNÓSTICO ENTREGADO — a la espera de decisiones de Diego.**

Decisiones que necesito de vos:
1. ¿Apruebo la estructura objetivo de §3 (con VIGENTE/historico en Polos)?
2. ¿F0 (borrado de basura técnica, ~230 MB) se ejecuta directo o querés cuarentena en `_delete_candidates/`?
3. Las decisiones B heredadas (~3 GB): ¿dump ATP se borra anotando procedencia, se mueve a disco externo, o queda?
4. ¿Los espejos de la raíz (`Cafesito/` etc.) se conservan como espejo o se archivan?
