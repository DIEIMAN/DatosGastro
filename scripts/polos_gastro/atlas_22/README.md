# Scripts portables del Atlas 22 V2 Compacta

## Propósito y alcance

Esta carpeta conserva el generador y el QA de la corrección local B-01...B-04 del Atlas 22 V2
Compacta. Las copias curadas permiten verificar o regenerar el producto en un directorio nuevo,
sin escribir sobre el Atlas institucional vigente.

No son scripts standalone. Requieren un checkout de DataGastro con `.git/` y el árbol local
completo de `outputs/polos_gastro/INFORMEFINAL/`. Ese árbol aporta Atlas V1/V2, fichas,
cartografía, planificación, actas y globales cerrados. Los PDF, ZIP y demás binarios
institucionales no se versionan junto con estos scripts.

## Dependencias y operación offline

- Windows y `.venv/Scripts/python.exe` con las dependencias ya instaladas en el proyecto.
- PyMuPDF, Pillow, NumPy, pypdf y ReportLab.
- Fuentes DejaVu Sans del entorno virtual o Arial del sistema; puede indicarse `--font-dir`.
- Sin red, APIs, `.env`, credenciales ni escritura en datos fuente.
- Los insumos se abren en modo lectura y sus hashes institucionales se verifican antes de crear
  el primer archivo de salida.

## Separación de rutas

- `--source-package`: raíz completa y de solo lectura de
  `outputs/polos_gastro/INFORMEFINAL/`.
- `--output-dir`: destino nuevo. En operación normal debe quedar bajo
  `outputs/polos_gastro/_work/atlas_22/`.
- Área temporal de pruebas: `%TEMP%/datagastro_atlas_22_tests/`, habilitada únicamente mediante
  `--allow-temp-output`.
- `--font-dir`: directorio opcional que contiene DejaVu Sans o Arial.

El build rechaza source igual a output, output dentro del source, superficies declaradas
`puede_modificar: false`, destinos fuera de la raíz autorizada y destinos existentes no vacíos.
No hay modo de sobrescritura.

## Invocación offline

Desde la raíz del repositorio:

```powershell
$source = 'outputs/polos_gastro/INFORMEFINAL'
$output = 'outputs/polos_gastro/_work/atlas_22/regeneracion_YYYYMMDD_HHMM'

.venv/Scripts/python.exe -B scripts/polos_gastro/atlas_22/build_atlas_22_v2_compacta.py `
  --source-package $source `
  --output-dir $output

.venv/Scripts/python.exe -B scripts/polos_gastro/atlas_22/qa_correccion_local_b01_b04.py `
  --source-package $source `
  --output-dir $output
```

Preflight sin escritura:

```powershell
.venv/Scripts/python.exe -B scripts/polos_gastro/atlas_22/build_atlas_22_v2_compacta.py `
  --source-package $source --output-dir $output --check-inputs

.venv/Scripts/python.exe -B scripts/polos_gastro/atlas_22/qa_correccion_local_b01_b04.py `
  --source-package $source --output-dir $output --check-only
```

`--finalize-visual` sólo debe usarse después de revisar las 58 páginas. El QA calcula y registra
el hash de la versión curada actual del build, pero no exige un hash histórico rígido del script.

## Outputs

La regeneración produce un PDF de 58 páginas, contenido estructurado, activos derivados,
matrices, renders, QA, manifest, checksums, ZIP y sidecar SHA-256 dentro de `--output-dir`.
El QA compatible trabaja sobre ese mismo destino nuevo.

## Superficies prohibidas y no sobrescritura

Está prohibido usar como destino, o sobrescribir directa o indirectamente:

- `atlas_22_v1/`;
- `atlas_22_v2_compacta_v1/`;
- `atlas_22_v2_compacta_correccion_local_v1/`;
- `cartografia_22_v1/`;
- `cartografia_22_correccion_visual_v1/`;
- `fichas_22_v1/`;
- cualquier ruta declarada no modificable en `docs/polos_gastro/PROTECTED_SURFACES.yaml`.

## QA, privacidad y preservación

El flujo verifica hashes de insumos, CRC de ZIP, 58 páginas A4, texto seleccionable, marcadores,
enlaces internos, tipografías, cobertura, preservación de páginas y activos, y patrones de datos
personales o secretos. Una ejecución exitosa no reemplaza la inspección visual página por página
ni una auditoría independiente.

Las fuentes originales protegidas permanecen en modo lectura:

- `outputs/polos_gastro/INFORMEFINAL/codex/atlas_22_v2_compacta_correccion_local_v1/scripts/build_atlas_22_v2_compacta.py`
- `outputs/polos_gastro/INFORMEFINAL/codex/atlas_22_v2_compacta_correccion_local_v1/scripts/qa_correccion_local_b01_b04.py`

## Reproducibilidad y hashes de referencia

Un clon limpio no alcanza: Git no contiene los binarios ni todo el corpus institucional. Se
necesita custodiar localmente el árbol completo de `INFORMEFINAL` y verificarlo antes de
regenerar. Los siguientes hashes identifican los artefactos vigentes al momento de esta
curación; son referencias de verificación y no implican versionar los binarios:

- PDF vigente: `586d794df3abced527aa648a5e2065d37626c0507c7f60ea0d4de8a67c48faee`.
- ZIP vigente: `2e4835933b8501a8e48144b14960d357a6cc7719e172d9c93c6c092a266af519`.

El hash de una regeneración puede variar por metadatos de PDF/ZIP aunque el contenido material
sea equivalente. En ese caso deben compararse páginas, texto, estructura, marcadores, enlaces y
diferencias visuales antes de atribuir una divergencia sustantiva.
