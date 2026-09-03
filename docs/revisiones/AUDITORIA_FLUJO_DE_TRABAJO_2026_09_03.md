# Auditoría de flujo de trabajo — 2026-09-03

Pedido de Diego: auditar exhaustivamente el repositorio, de lo global a las skills, hooks y MCPs,
y decir qué **secar**, qué **mejorar** y qué **sumar** para mejorar el flujo de trabajo.

Método: cuatro auditorías de solo lectura en paralelo (skills y superficies de agentes; docs y
navegación; código, tests y tooling; outputs, datos, raíz y git), más verificación propia de las
dudas que dejaron. **Nada fue borrado, movido ni commiteado.** Toda ruta citada fue verificada.

Antecedente: `AUDITORIA_REPO_COMPLETA_2026_08_28.md` (estructura y limpieza). Ésta la da por
base y agrega lo que aquélla no miraba: git, código, skills, hooks, plugins, MCPs y memoria.

---

## 0. Resumen ejecutivo: los diez hallazgos que cambian el flujo

1. **Lo canónico del último mes no está en git.** `scripts/shared/fuentes_locales/` (el lector
   F02 que CLAUDE.md declara obligatorio), `scripts/panaderias/`, `tests/test_fuentes_locales.py`,
   `tests/test_casas_pastas_dedup.py`, `docs/estudios_de_rubro/`, `docs/panaderias/`, 20 de los
   34 handoffs y `DECISIONES_CERRADAS_Y_PENDIENTES.md` figuran como `??`. Un `git stash` o un
   clon los pierde. Es el riesgo más alto del repo.
2. **La fase F3 de la reorganización (Polos VIGENTE/historico) sí se ejecutó en disco el
   2026-08-28, pero nunca se commiteó ni documentó.** `outputs/polos_gastro` pasó de 44 a 5
   entradas, 71 scripts tienen las rutas parcheadas en el working tree, y ningún handoff ni
   `ESTADO_GENERAL_INFORMEFINAL.md` lo dice. Un `git checkout .` rompe 71 scripts.
3. **82 % de los 646 archivos "modificados" son solo fin de línea.** El `.gitattributes` del
   08-10 pide correr `git add --renormalize .` una vez; nunca se corrió. Quedan 117 archivos con
   cambios reales (Atlas V3, F3, `src/config.py`, CLAUDE.md, skills) mezclados con 529 falsos.
4. **50 commits sin push y la rama principal se llama `mercados-gastronomicos-v2`.** `main`
   está congelada desde el 2026-06-19; todo julio y agosto vive en la otra rama, que puede
   hacer fast-forward a `main` (`main..v2` = 83, `v2..main` = 0). Sin push, no hay respaldo.
5. **Los hooks de graphify no funcionan y CLAUDE.md pide consultar un archivo que no existe.**
   `python3` no está en Git Bash (el hook falla en silencio), el matcher no cubre PowerShell,
   `.graphify/graph.json` no existe y el reporte es del 08-07, 13 commits atrás.
6. **La misma regla vive en seis lugares.** Privacidad está en CLAUDE.md, AGENTS.md, la skill,
   `docs/skills_claude/03`, `agent_skills/README.md` y `agent_skills/shared/…qa_privacidad.md`.
   Hay cuatro superficies de skills; una de ellas (`agent_skills/claude_imported`) contradice
   al guardrail 6 vigente ("NO scraping" contra "recolección controlada").
7. **`kpis_lock.json` es una convención declarada en tres lugares y adoptada en cero informes.**
   La regla de CLAUDE.md nunca se activa.
8. **Sesenta lectores de F02 propios, doce clientes de Google Places y diecinueve copias de
   `plegar`.** El módulo compartido existe pero solo lo usan panaderías y pastas nuevas.
9. **`requirements.txt` no permite correr el 40 % de los scripts.** Faltan numpy, scipy, pillow,
   scikit-learn, pymupdf, pypdf, networkx; no hay pyproject, ruff, pytest ni CI.
10. **3,2 GB secables con riesgo nulo o bajo** (cuarentena F0 de 228 MB con seis días, dump ATP de
    2,8 GB, `tmp/` de 113 MB, `.agent-tools/` de 367 MB regenerable) y `.git` con 497 MiB de
    objetos sueltos porque nunca se corrió `git gc`.

---

## 1. Estado de la reorganización del 08-28

| Fase | Plan | Estado verificado |
|---|---|---|
| F0 | Basura técnica a cuarentena | Hecha y commiteada (`d781389`). `_delete_candidates/2026-08-28/` = 3,0 GB, de los que 2,8 GB es el dump ATP y ~228 MB son las siete filas de "riesgo nulo". |
| F1 | Raíz consolidada | Hecha (`d781389`). `configs/` fusionada, `_docs_reorganizacion` archivada. |
| F2 | `outputs/fuentes_externas` → `data/fuentes_externas` | Hecha (`6852595`). Cero referencias rotas en docs, scripts, skills. |
| F3 | Polos VIGENTE/historico | **Hecha en disco, sin commit.** 5 entradas en `outputs/polos_gastro`, `historico/` con 55 entradas y 1,5 GB, 1 rename staged, 71 scripts parcheados en working tree. No se creó `VIGENTE/`; las carpetas vigentes quedaron nombradas. |
| F4 | Rubros | Pendiente. Siguen 6 carpetas `outputs/casas_pastas*`, 2 `outputs/mercados*`, `exports/`, `deliverables/`, `fuentes_internas_mercados_caba/`. Pesa ~6 MB: es orden, no disco. |
| F5 | Docs | Pendiente en su totalidad. No existe `docs/general/`; 22 archivos sueltos en `docs/`; pares duplicados intactos. |

Decisiones B del 08-07 que siguen sin respuesta: dump ATP, `DataMercados.zip`, espejos de raíz.

---

## 2. Git y disco

### Hallazgos

- `git status`: 646 `M`, 219 `??`, 1 `R`. Con `-uall`: 8.797 archivos y 2,67 GB sin trackear
  (7.467 archivos en `outputs/polos_gastro`, 292 en `docs/polos_gastro`, 303 `.py`).
- `git diff --numstat` +71.675/−71.456; con `-w` quedan 117 archivos, +1.635/−1.416.
- `.git` = 957 MB: 497 MiB de objetos sueltos, 435 MiB en pack, 5 `tmp_obj_*` huérfanos.
- Trackeados: 2.056 archivos, 254 MB. Dos copias del `Atlas_V3_agosto_2026.docx` (25 MB).
- Ramas: `main` 2026-06-19; `casas-pastas-integrado` ya mergeada en v2; `mercados-gastronomicos-v2`
  a 50 commits de su remoto.
- Commits: convención `feat/docs/chore/fix/reorg(scope)` consistente desde julio; ráfagas
  (44 en la semana del 08-06) y silencios (nada del 08-11 al 08-27 ni del 08-29 al 09-03 pese a
  Atlas 39, recuperación nominal, panaderías y exploración Roma). Un commit de 697 archivos
  (`7acb3ff`) mezcló CRLF parcial con contenido.
- `.gitignore`: 11 reglas redundantes (dos `.env`, dos `casas_pastas_google_places`, seis
  `*.zip` locales tapadas por el `*.zip` global, tres `*.pdf` locales). Faltan `tmp/`, `cache/`,
  `.playwright-mcp/`, `deliverables/`, `PolosGastro/`. Política de pastas invertida: la build
  canónica `outputs/casas_pastas/` está ignorada y las cinco superadas parcialmente trackeadas.
- Zips: 137, 3,65 GB, cero trackeados. Único redundante claro: `rus_2022_2024_shp.zip` (84 MB,
  ya extraído en `shp/`). Los sellados de INFORMEFINAL (~165 MB) no se tocan.
- `tmp/` (113 MB, mtime 09-01): `pydeps_duckdb/` (pip-target regenerable), CSV y PDF de Roma
  SUAP/ATECO que ningún script ni doc reclama.

### Secar

| Ítem | Peso | Riesgo |
|---|---|---|
| Cuarentena F0 (todo salvo el ATP) | ~228 MB | nulo, ya clasificado el 08-28 |
| Dump ATP `output_2026-08-01-13-32-15.zip` | 2,8 GB | bajo, anotando procedencia, fecha y hash en `data/fuentes_externas/all_the_places/`; el derivado `atp_caba.csv` ya existe |
| `tmp/` | 113 MB | nulo; si Roma vale, nace en `data/fuentes_externas/roma_suap/` con ficha |
| `.agent-tools/` | 367 MB | nulo, venv regenerable; solo pesa en disco y backup |
| `git gc` | recupera 100–300 MB | nulo |
| `cache/`, `.playwright-mcp/`, `.codex/` (vacía) | < 100 KB | nulo, ruido de raíz |
| `rus_2022_2024_shp.zip` | 84 MB | nulo |
| `lo_profile_*` dentro de Atlas 39 | 862 KB | nulo; hoy rompe `find` y `git status` por MAX_PATH |

### Mejorar (orden sugerido, un commit por paso)

1. `git add` de lo canónico sin trackear: `scripts/shared/fuentes_locales`, `scripts/panaderias`,
   los dos tests, `docs/estudios_de_rubro`, `docs/panaderias`, handoffs, `DECISIONES_*`.
2. Commit de contenido real (Atlas V3, `src/config.py`, docs de fuentes externas, CLAUDE.md,
   AGENTS.md, skills), separado de F3.
3. Commit `reorg(F3)`: rename staged + 71 parcheos + `.gitignore`; después `unittest` y una
   línea en `ESTADO_GENERAL_INFORMEFINAL.md`.
4. `git add --renormalize .` + commit propio; considerar `core.autocrlf=false` en el repo.
5. `git push`; merge fast-forward de `mercados-gastronomicos-v2` a `main`; borrar
   `casas-pastas-integrado`. Trabajar en `main` o en ramas por tema con nombre real.
6. Limpiar `.gitignore` (11 redundantes, 5 faltantes, política de pastas).
7. Sacar del índice las dos copias del `.docx` de 12–13 MB; los pesados van con `.sha256` al lado.

### Sumar

- `scripts/qa/estado_repo.py` (solo lectura): tamaño por dir, `M/??` con partición "solo EOL vs
  real", untracked por dir, commits sin push, días desde el último commit, edad de `.graphify`.
  Engancharlo al SessionStart junto al aviso de handoff.
- Regla de cuarentena con vencimiento: `_delete_candidates/<fecha>/` se borra a los 14 días.
- Regla "todo dataset descargado nace en `data/fuentes_externas/<fuente>/` con `FICHA.md`,
  nunca en `tmp/`".
- Cierre de sesión larga = commit + push + handoff.

---

## 3. Raíz, outputs y datos

### Hallazgos

- Raíz: 33 directorios (objetivo ~15). Fuera de la estructura objetivo: `_delete_candidates`,
  `.agent-tools`, `fuentes_internas_mercados_caba` (255 MB, con `DataMercados.zip` de 124 MB),
  `tmp`, `exports`, `deliverables`, `cache`, `.playwright-mcp`, `.codex`, los cuatro espejos.
- `outputs/` 4,8 GB en 29 entradas. Polos 4,0 GB: `historico` 1,5 GB, `ATLAS_INFORMATIVO_39`
  1,5 GB, `INFORMEFINAL` 795 MB, `ATLAS_V2` 211 MB. 4.603 PNG = 1,77 GB (44 % del subproyecto
  son renders y QA). 17 `.docx` de 34 MB = 574 MB: cada versión v5.1, v6.0…v6.4 guarda dos o
  tres copias (`_PRE_SANITIZAR`, `_GOOGLE_DOCS`, `_TITULO_SANITIZADO`).
- `data/` 975 MB, pipeline F01–F05 intacto (último commit de `processed`/`analytics` 06-18).
  `fuentes_externas` 804 MB, de los que el `.dbf` del RUS pesa 360 MB.

### Secar

- Copias intermedias `.docx` de Atlas 39 superadas por v6.4 (~8 versiones): verificar hash por
  pares y respetar manifiestos sellados. Riesgo medio: confirmar con Diego.
- `DataMercados.zip`: decisión B; no se puede afirmar redundancia sin abrirlo.

### Mejorar

- Ejecutar F4 (pastas 6→1, mercados 2→1, `exports/`+`deliverables/` → `outputs/entregas/`,
  `fuentes_internas_mercados_caba/` → `data/fuentes_internas/mercados/`). Son ~6 MB y un
  parcheo de rutas acotado (verificar con grep antes de cada movimiento).
- Espejos de raíz (`Cafesito/`, `CasasDePastas/`, `MercadosGastro/`, `PolosGastro/`): decisión
  pendiente desde el 08-07; `PolosGastro/` ni siquiera está ignorada.

### Sumar

- Política escrita de outputs por subproyecto: carpetas vigentes nombradas + `historico/` +
  `README_ESTADO.md`; una versión nueva reemplaza a la anterior y la manda a `historico/` en el
  mismo commit. Polos ya la cumple de hecho; falta escribirla y aplicarla a pastas, mercados y
  cafecito.
- Regla para binarios pesados: PNG de QA y `.docx` no se trackean; van con `.sha256`.

---

## 4. Documentación y navegación

### Hallazgos

- `docs/`: 852 archivos, 780 `.md`, 21 carpetas; **352 sin trackear** (ninguno por regla de
  ignore). 58 % de los archivos están en `docs/polos_gastro` (495), y **189 de ellos son copias
  byte a byte de archivos que ya están en `outputs/polos_gastro/`**.
- 22 archivos sueltos en la raíz de `docs/`, 20 de junio (época V3); 14 sin ninguna referencia.
- No existe `docs/README.md`. `docs/ESTRUCTURA_PROYECTO.md` (06-10) describe 9 carpetas y nada
  de scripts, outputs por subproyecto, skills ni revisiones.
- 34 handoffs en `docs/revisiones/` (380 KB) más 4 en `docs/cafecito/` y ~45 dentro de fases
  cerradas de Polos. El hook SessionStart elige por `mtime` con `ls -t`: funciona hoy por
  casualidad; un checkout, clon, stash o renormalización iguala los mtime y elige al azar. No
  distingue subproyecto.
- Pares duplicados: `docs/casas_pastas` (V4 de junio, superada) + `docs/casas_de_pastas`
  (revisión institucional cerrada 07-04); `docs/mercados` (revisión 07-04) + `docs/mercados_caba`
  (vigente: tres scripts de `src/` la leen). 28 duplicados exactos internos (plantillas v1 = v1.1,
  design_system = claude_design_export_v1).
- Enlaces rotos en navegación: `README.md` cita `notebooks/05_informe_ejecutivo_datagastro.ipynb`
  (no existe, dos veces); `docs/skills_claude/08` cita `outputs/tmp/` (hoy es `tmp/`).
- `README.md` raíz: 150 líneas, último commit 06-17, título "DatosGastro", solo describe el
  pipeline V3, cifras de junio sin fecha de corte, no menciona ningún subproyecto ni CLAUDE.md.
- Estado vigente: `ESTADO_GENERAL_INFORMEFINAL.md` dice "Actualizado 2026-08-04" y hay un mes de
  Atlas posterior. Ningún `ESTADO*.md` para panaderías, pastas, cafecito ni mercados;
  `README_POLOS_GASTRO.md` (06-29) dice "sin informe final aún". El buen modelo es
  `docs/panaderias/README_PANADERIAS.md` (sección Estado con cifras, unidad de conteo y fecha).
- CLAUDE.md: 140 líneas, 9,9 KB. El bloque "Estudios de rubro" (25 líneas de detalle F02) repite
  lo que ya está en `docs/estudios_de_rubro/`; el índice "Infraestructura V1.1" (18 líneas) está
  duplicado casi literal en AGENTS.md; la nota sobre `graphify-out/` ya no aplica (F0 lo borró).
- AGENTS.md y CLAUDE.md difieren en 225 líneas y dicen cosas distintas sobre datos personales
  (uso interno con minimización vs "no exportar filas").

### Secar

- `docs/polos_gastro/`: quitar los 189 duplicados de outputs; fases cerradas de junio–julio a
  `docs/polos_gastro/historico/`. Dejar README reescrito, `PROTECTED_SURFACES.yaml`,
  `PEDIDOS_EXTERNOS_*`, fichas vivas.
- Raíz de `docs/`: los 7 referenciados (`contratos_fuentes`, `perfilado_fuentes`,
  `diccionario_de_datos`, `fuentes_y_trazabilidad`, `GUIA_*`, `CHANGELOG`) → `docs/general/`;
  los 14 sin referencia → `docs/archive/v3_2026-06/`; `PLAN_LIMPIEZA_*` y `NOTA_LIMPIEZA_*` →
  `docs/revisiones/`.
- Fusionar `casas_pastas` + `casas_de_pastas` (nombre `casas_pastas`, coincide con outputs) y
  `mercados` dentro de `mercados_caba`; `fichas_v0/` y `fichas_v1/` (32 archivos) a `historico/`.
- `infraestructura_agentes_skills_v1_1_1_hotfix` (docs 51 KB + scripts 32 KB, sin trackear desde
  julio) → fusionar README en `_v1_1` y archivar; `_v1` y `_v1_1` quedan (las citan CLAUDE.md,
  AGENTS.md y 4 scripts) pero salen del índice de CLAUDE.md.
- `docs/ESTRUCTURA_PROYECTO.md` → reemplazado por `docs/README.md`.

### Mejorar

- **CLAUDE.md a ~80 líneas**: guardrails intactos; entorno sin la frase de `graphify-out`;
  continuidad = 3 líneas apuntando a `HANDOFF_ACTUAL.md`; alcance = los 6 bullets; "Estudios de
  rubro" = 3 líneas (leer la receta, leer por `fuentes_locales`, agrupar por
  `clave_habilitacion`), el resto ya vive en docs; "Infraestructura V1.1" = 2 líneas
  (precedencia y fuente vigente de Polos); sección nueva de 5 líneas "Mapa del repo" →
  `docs/README.md`.
- **AGENTS.md**: solo lo específico de Codex (reporting standard, no `git add .`) y remitir a
  CLAUDE.md para guardrails e infraestructura. Unificar la regla de datos personales.
- **README.md**: DataGastro/DGDGAS, cifras fechadas o fuera, notebook corregida, bloque
  "Subproyectos" con un renglón y puntero por rubro, y "Cómo se trabaja acá" (CLAUDE.md →
  handoff actual → docs/README).
- **Handoff robusto**: `docs/revisiones/HANDOFF_ACTUAL.md` (tabla de hilos abiertos: polos,
  panaderías, pastas, cafecito, pet-friendly, con ruta y fecha) + hook que parsea la fecha del
  nombre en vez de `mtime`. Convención `HANDOFF_<SUBPROYECTO>_<TEMA>_<fecha>.md` formalizada.
- Actualizar `ESTADO_GENERAL_INFORMEFINAL.md` o anteponerle una nota fechada al estado real.

### Sumar

- `docs/README.md` (40 líneas): qué hay en cada carpeta, vigente vs histórico, qué leer según tarea.
- `docs/<subproyecto>/ESTADO.md` homogéneo (esqueleto de `README_PANADERIAS.md`): fecha de
  corte, cifras canónicas con unidad de conteo, cerrado/abierto, entregable vigente, handoff
  más reciente, decisiones que esperan a Diego. Faltan polos, pastas, cafecito, mercados, barrido.
- `docs/general/` (propuesto el 08-28, aún sin crear).
- `scripts/qa/check_docs_links.py`: verifica las rutas citadas en CLAUDE.md, AGENTS.md, README,
  `docs/README.md` y `docs/skills_claude`; correr tras cada reorganización.

---

## 5. Código, tests y tooling Python

### Hallazgos

- 295 `.py`, ~132 k líneas: `scripts/` 263 archivos (barrido 94, polos 90, cafecito 26, pastas
  22), `src/` 32, `tests/` 7. **117 de 295 archivos llevan versión en el nombre** (`_vN`,
  `faseN`, `tandaN`, `ronda_N`); `scripts/cafecito/` tiene 23 generadores de informe casi
  idénticos de 1.100–1.260 líneas, sin tocar desde el 07-04.
- **Tests: 91 pasan en 10 s.** Cubren 7 módulos. Sin test: `panaderias/build_panaderias.py` (la
  fusión de los 59 republicados), `pastas_patterns`, `panaderias_patterns`, `validate_kpis.py`,
  `pdf_check.py`, `barrido_ciudad/polos_soporte.py` (importado por 29 scripts, es el shared de
  facto del barrido), `reporting_dgdgas` (4 módulos), `build_analytics`, `validate_model`,
  `src/v2`, `src/mercados_caba`. Los tests usan `sys.path.insert` en cuatro variantes. No hay CI.
- Duplicación: 60 lectores de F02 propios (28 barrido, 24 polos, 3 pastas, 5 polos raíz); 54
  funciones de normalización en 25 archivos (`plegar` ×19, nueve byte a byte idénticas;
  `limpiar_texto` ×5; `normalizar` ×5); `write_csv` ×23, `read_csv` ×15, `build_pdf` ×11;
  12 clientes de Google Places implementados a mano (las lecciones de la memoria sobre
  `displayName`, `circle` y paginación viven dispersas en esos 12); 5 scripts del barrido pegan a
  la URL de USIG directo aunque `src/geocode_usig.py` tiene 11 tests y cache.
- `requirements.txt`: 12 paquetes sin versión. Importados y ausentes: numpy (55 archivos), scipy
  (24), pillow (21), scikit-learn (14), pymupdf (5), networkx (5), pypdf. `.venv` tiene 105
  paquetes; `.venv-tools` 245 sin requirements propio. No hay `pyproject.toml`, ruff, pytest,
  pre-commit, Makefile ni `tasks.py`. `matplotlib` es el import más frecuente (261 archivos): el
  proyecto es cartográfico-editorial.
- `scripts/compat/`: dos shims de 10 líneas, 85 días sin uso. `sql/`: sin referencias desde
  código desde junio. `node_modules/` (21 MB) sirve a un solo experimento HTML de cartografía.
  `notebooks/` congelado desde el 06-19. `__pycache__` ×501 fuera de `.venv` (cero trackeados).
- `kpis_lock.json`: cero trackeados; tres en disco, todos de prueba.

### Secar

- Hooks y reglas de graphify (ver §6) o regenerar el grafo en cada cambio.
- `scripts/compat/` (verificar que ningún doc lo cite).
- `__pycache__` ×501 (solo disco); línea 119 redundante del `.gitignore`.
- `sql/` → `sql/archive/` o nota en README de que es histórico. No borrar.
- `node_modules/` local si el experimento no se retoma (regenerable con `npm install`).
- `scripts/cafecito/`: congelar 20 generadores en `archive/` dejando `v6_1`, `revision_4`,
  `belgrano_tanda8` con un README de qué PDF salió de cuál. No borrar: son trazabilidad.
- Regla `kpis_lock.json` en CLAUDE.md, salvo que se adopte (ver §6).

### Mejorar

- Cerrar la migración al lector compartido: primero los 3 de pastas y los 5 de polos raíz; los
  18 de `experimentos/` quedan congelados con nota.
- Cerrar la fuga de USIG (5 scripts del barrido → `geocode_usig`/`fuentes_locales/geo.py`).
- `requirements.txt` completo y pinneado + `requirements.lock` con `pip freeze`;
  `requirements-tools.txt` para `.venv-tools`.

### Sumar

- `pyproject.toml` mínimo: `[tool.ruff]` (E, F, I), `[tool.pytest.ini_options] pythonpath`,
  `requires-python`. Cero cambios en el pipeline. Elimina los `sys.path.insert`.
- Orquestador (`Makefile`, que Git Bash ya corre, o `tasks.py` con invoke): `test`,
  `perfil-f02`, `rubro RUBRO=… OUT=…`, `pdf-check FILE=…`, `lint`, `clean-pycache`, siempre con
  `.venv/Scripts/python.exe`. Resuelve de raíz el Python de Store.
- `scripts/shared/places_client.py`: un cliente único de Places (New) con `displayName`
  obligatorio en el field mask, `locationRestriction` rectangular, paginación con checkpoint,
  presupuesto por corrida y log de costo.
- `scripts/shared/texto.py` como único normalizador (ya existe `fuentes_locales/texto.py`):
  mover `plegar`, `strip_accents`, `slug`, `norm_nombre`, `norm_dir`; el reemplazo de las 19
  copias es mecánico y verificable con los 42 tests de direcciones.
- `scripts/shared/io_csv.py` (o ampliar `polos_soporte`) y un test para `polos_soporte`.
- Tests con mayor retorno: `build_panaderias` (fusión de republicados, `clave_habilitacion`),
  `pastas_patterns`/`panaderias_patterns` (tabla nombre engañoso vs rubro), `validate_kpis` con
  lock de juguete, `reporting_dgdgas` smoke (PDF de una página abierto por `pdf_check`).
- CI mínima (`.github/workflows/tests.yml`): install + unittest en Ubuntu.

---

## 6. Skills, hooks, plugins, MCPs y memoria

### Hallazgos

- **Cuatro superficies de skills**: `.claude/skills/` (19: 10 datagastro + 9 técnicas),
  `.agents/skills/` (10 punteros + `recoleccion-polos`, la única con scripts reales),
  `agent_skills/claude_imported/` (9 punteros), `docs/skills_claude/` (8 docs largos). Los
  punteros funcionan, pero `agent_skills/claude_imported/datagastro-fuentes-externas` conserva
  "NO scraping", contradiciendo al guardrail 6 vigente. Las 9 skills técnicas, `recoleccion-polos`
  y los punteros de qa-pdf están sin commitear desde el 14–16 de agosto.
- Redundancia: `datagastro-guardrails` reformula los 9 guardrails que ya carga CLAUDE.md;
  `-limpieza` repite el 9; `-privacidad` el 7; `-pipeline` el 2. Las 9 técnicas repiten al pie
  los guardrails 2/3/5/7/8. `guardrails` y `limpieza` se disparan ambas "SIEMPRE antes de borrar".
  Las más valiosas son `datagastro-informes` (defaults DGDGAS que no están en CLAUDE.md) y
  `datagastro-qa-pdf` (procedimiento de 6 pasos).
- Errores de hecho en skills: `chromadb-rag` dice "instalado en `.venv-tools`" y no está (vive en
  `.agent-tools/chromadb/.venv`, chromadb 1.5.9); `duckdb-sql` y `folium-mapas` mandan a
  `.venv-tools` cuando ambos paquetes están en `.venv`.
- Ninguna skill del proyecto menciona los MCPs `ckan`, `openstreetmap`, `duckdb`, `tavily`
  instalados el 09-01. La única guía es la user-level `gastronomia-research`, que no cita USIG ni
  la separación F/I/E y compite con `datagastro-geodatos`, `fuentes-externas`, `duckdb-sql` y
  `osmnx` en la auto-invocación. `claude-design` falla la conexión (403) en cada sesión.
- **Hooks**: los dos PreToolUse de graphify usan `python3` (no existe en Git Bash → fallan en
  silencio con `|| true`), matcher `Bash` sin PowerShell, y el grafo tiene 13 commits de atraso
  sin `graph.json`. Lanzan dos procesos por cada Bash/Read/Glob para nada. El SessionStart del
  handoff sí funciona.
- `settings.local.json`: `"Bash(git reset *)"` en `allow` (choca con el guardrail 9); 40
  entradas, varias de un solo uso con rutas absolutas del scratchpad.
- **Plugins**: `frontend-design` 0 menciones, `atomic-agents` 0 uso, `code-review` y
  `skill-creator` plausibles. Ningún `.claude/agents/`.
- **Infraestructura agentes V1/V1.1/hotfix**: 323 archivos, ~2,8 MB, en 9 carpetas (docs,
  scripts, outputs), 69 trackeados. Catálogo de julio: 7 agentes, ninguno promovido en 7 semanas;
  `docs/…_v1_1/agents/` vacío. Lo vigente (ciclo una pasada, fuente única, PROTECTED_SURFACES) ya
  está resumido en CLAUDE.md. El único rol con valor distinto a un `Agent` genérico es
  `auditor_qa` (solo lectura, escribe solo QA).
- **Memoria persistente**: 77 archivos, 215 KB, `MEMORY.md` de 12,9 KB cargado en cada sesión.
  75 son tipo `project`, 1 `feedback`, 0 `user`. Unas 45 son crónica de rondas de Polos y
  versiones del Atlas (V5.1, V6.1…V6.4, rondas 1–21) que los handoffs del repo ya registran.

### Secar

- Los dos hooks PreToolUse de graphify y la sección graphify de CLAUDE.md (o arreglarlos, abajo).
- `agent_skills/claude_imported/` (réplica de `.agents/skills/` con un puntero divergente):
  dejar `.agents/skills/` como única capa para no-Claude; retocar dos líneas en AGENTS.md y
  `agent_skills/codex/README.md`.
- `outputs/infraestructura_agentes_skills_*` (235 archivos, ~2,3 MB, cero trackeados,
  regenerables) → cuarentena.
- Plugins `frontend-design` y `atomic-agents`.
- `.codex/` vacía; `"Bash(git reset *)"` del allow; entradas de un solo uso del
  `settings.local.json`.
- Fusionar `datagastro-limpieza` dentro de `datagastro-guardrails`.
- Memoria: consolidar las ~45 crónicas de Polos/Atlas en 3–4 memorias de "estado vigente" y
  dejar `MEMORY.md` en ~40 líneas; agregar memorias tipo `user` y `feedback` (hoy casi no hay).

### Mejorar

- Commitear el bloque coherente del guardrail 6 (CLAUDE.md, AGENTS.md, dos skills, dos docs, 9
  técnicas, `recoleccion-polos`, punteros) y actualizar `REPORTE_PARIDAD_SKILLS.md`.
- Corregir `chromadb-rag`, `duckdb-sql`, `folium-mapas` (intérprete correcto).
- Desduplicar: CLAUDE.md única fuente de los 9 guardrails; las skills datagastro son checklists
  cortos que remiten; las técnicas dejan solo lo específico de la herramienta (Folium expone
  atributos en el HTML, HDBSCAN no es "misma vara", Nominatim 1 req/s).
- Mover `recoleccion-polos` a `.claude/skills/`: sus wrappers con `--allow-host` son el guardrail
  6 hecho código y hoy solo los ve Codex.
- Si graphify se conserva: `python3` → `.venv/Scripts/python.exe`, matcher `Bash|PowerShell`, y
  un PostToolUse en `Edit|Write` sobre `scripts/**/*.py` y `src/**/*.py` que corra
  `graphify update .`.
- `kpis_lock.json`: crearlo para los 2–3 informes vivos (Atlas, panaderías, pastas) o sacar la
  regla de CLAUDE.md, `informes` y `qa-pdf`.

### Sumar

- **Hook PreToolUse de guardrails duros** (`Bash|PowerShell`, `exit 2`): escrituras en
  `G:\My Drive` o `G:\.shortcut-targets-by-id`; `rm`/`Remove-Item`/`git rm`/`git reset --hard`
  sobre `data/processed`, `data/analytics`, `src/build_*`, `dashboard`, `notebooks`. Los
  guardrails 1, 2 y 9 hoy dependen solo de prosa.
- **Hook PreToolUse** que avise o bloquee `python `, `python3 `, `pip ` a secas y exija
  `.venv/Scripts/python.exe`. Es la fricción más repetida en las memorias.
- **Hook Stop** que avise si en la sesión se generó un PDF sin `qa_png_*` hermano. El QA visual
  hoy es voluntario y la memoria lo registra como "treadmill".
- **Hook SessionStart ampliado**: handoff actual + `estado_repo.py` (modificados, sin trackear,
  sin push, edad del grafo).
- **Skill `datagastro-abrir-rubro`**: la receta y el precheck ya existen
  (`COMO_ABRIR_UN_RUBRO_NUEVO.md`, `python -m scripts.shared.fuentes_locales.f02`); dos rubros
  abiertos en agosto y tres memorias de errores del lector justifican una skill, no 25 líneas de
  CLAUDE.md.
- **Skill `datagastro-mcps`** (o portar `gastronomia-research` al proyecto): orden USIG → CKAN →
  OSM → Tavily → DuckDB, códigos F/I/E, qué MCP no está configurado.
- **Un solo agente nativo, `auditor-qa`** (read-only del producto, escribe solo `INFORME_QA*`):
  el ciclo "una pasada" lo exige y un `Agent` genérico no lo garantiza. El adaptador ya está
  escrito en `docs/infraestructura_agentes_skills_v1_1/adaptadores/claude_propuestos/auditor_qa.md`.
  Requiere pedido explícito de Diego (CLAUDE.md prohíbe crear `.claude/agents/` sin pedido).

---

## 7. Plan priorizado

### Bloque A — hoy, sin decisión de Diego, riesgo nulo (asegurar lo hecho)

1. `git add` de lo canónico sin trackear (§2, paso 1) y commit.
2. Commit de contenido real separado; commit `reorg(F3)`; nota en `ESTADO_GENERAL_INFORMEFINAL.md`.
3. `git add --renormalize .` y commit propio.
4. `git push`; `git gc`.
5. Quitar los hooks rotos de graphify; quitar `git reset` del allow; corregir las tres skills
   con intérprete equivocado; commitear el bloque del guardrail 6.
6. `.gitignore`: 5 faltantes, 11 redundantes.

### Bloque B — esta semana (orden y reglas)

7. CLAUDE.md a ~80 líneas; AGENTS.md remite; README.md actualizado; `docs/README.md` nuevo.
8. `HANDOFF_ACTUAL.md` + hook por fecha del nombre + `estado_repo.py` en SessionStart.
9. Hooks de guardrails duros y de Python del venv.
10. `pyproject.toml` + `requirements.txt` completo + `Makefile`/`tasks.py`.
11. F4 y F5 con `git mv` y grep previo de rutas.
12. Skills: fusionar limpieza en guardrails, sacar los pies repetidos, mover `recoleccion-polos`,
    crear `datagastro-abrir-rubro` y `datagastro-mcps`; deshabilitar dos plugins.
13. Consolidar la memoria persistente.

### Bloque C — decisiones de Diego

- Borrar la cuarentena F0 (228 MB). Destino del dump ATP (2,8 GB). `DataMercados.zip`. Espejos
  de raíz. Copias `.docx` intermedias del Atlas 39 (574 MB). Merge a `main` y renombre o cierre
  de `mercados-gastronomicos-v2`. Adoptar o retirar `kpis_lock.json`. Agente nativo `auditor-qa`.
  `scripts/cafecito/` a archivo. Cerrar la migración al lector F02 en pastas y polos (mueve
  números publicados: decisión junto con regenerar entregables).

### Bloque D — inversión de fondo (cuando haya un rubro nuevo por delante)

- `places_client.py`, `texto.py` único, `io_csv.py`, tests de `build_panaderias` y patrones,
  CI mínima, política de outputs por subproyecto aplicada a todos los rubros.

---

**Estado: DIAGNÓSTICO ENTREGADO.** Nada ejecutado. El Bloque A no requiere decisiones y
elimina los dos riesgos de pérdida (canónico sin trackear, F3 sin commit).
