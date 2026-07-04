# Skill operativa: QA privacidad de entregables

Guía corta para revisar que outputs públicos o compartibles de DataGastro no expongan datos
sensibles. Debe aplicarse antes de cerrar informes, packs, DOCX, PDF, CSV, Markdown o gráficos.

## Qué buscar

- Emails.
- Teléfonos.
- CUIT/DNI.
- Nombres propios si no son públicos/institucionales.
- `place_id`.
- API keys.
- Links privados de Drive/Docs.
- Timestamps individuales.
- Respuestas abiertas identificables.
- IDs técnicos que permitan reconstruir una persona, comercio o trámite sensible.

## Comandos sugeridos PowerShell

Estos comandos deben correrse sobre outputs públicos o entregables, no necesariamente sobre
fuentes privadas/crudas. Ajustar `$path` al directorio del entregable.

```powershell
$path = "outputs/cafecito"
```

Buscar `@`:

```powershell
Get-ChildItem -Path $path -Recurse -File | Select-String -Pattern "@" -SimpleMatch
```

Buscar emails:

```powershell
Get-ChildItem -Path $path -Recurse -File | Select-String -Pattern "[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"
```

Buscar patrones de teléfono:

```powershell
Get-ChildItem -Path $path -Recurse -File | Select-String -Pattern "\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b"
```

Buscar CUIT:

```powershell
Get-ChildItem -Path $path -Recurse -File | Select-String -Pattern "CUIT|C\.U\.I\.T\.|\b\d{2}-\d{8}-\d\b"
```

Buscar DNI:

```powershell
Get-ChildItem -Path $path -Recurse -File | Select-String -Pattern "DNI|D\.N\.I\.|\b\d{7,8}\b"
```

Buscar `place_id`:

```powershell
Get-ChildItem -Path $path -Recurse -File | Select-String -Pattern "place_id" -SimpleMatch
```

Buscar API keys de Google:

```powershell
Get-ChildItem -Path $path -Recurse -File | Select-String -Pattern "AIza[0-9A-Za-z_\-]{20,}"
```

Buscar links privados de Drive/Docs:

```powershell
Get-ChildItem -Path $path -Recurse -File | Select-String -Pattern "drive\.google\.com|docs\.google\.com"
```

## Reglas

- Si aparece dato sensible en outputs públicos, no borrar fuente; corregir script/output.
- No modificar XLSX/CSV original.
- No publicar identificadores individuales.
- Agregar a `.gitignore` carpetas internas/crudas.
- Documentar qué se excluyó.
- Mantener separadas fuentes privadas/crudas y outputs publicables.
- Si hay duda sobre una respuesta abierta, no publicarla o resumirla de forma agregada.

## QA para DOCX

Un DOCX es un ZIP. Conviene revisar el XML interno con Python/zipfile o extraer temporalmente en
una carpeta descartable.

Ejemplo con Python:

```powershell
@'
from pathlib import Path
import re
import zipfile

docx = Path("outputs/cafecito/INFORME_CAFECITO_GRAFICOS.docx")
patterns = {
    "@": re.compile(r"@"),
    "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    "telefono": re.compile(r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b"),
    "drive_docs": re.compile(r"drive\.google\.com|docs\.google\.com", re.I),
    "api_key": re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
}
with zipfile.ZipFile(docx) as zf:
    xml = "\n".join(
        zf.read(name).decode("utf-8", errors="replace")
        for name in zf.namelist()
        if name.endswith(".xml")
    )
for label, pattern in patterns.items():
    print(label, "HIT" if pattern.search(xml) else "OK")
'@ | python -
```

## QA para PDF

La búsqueda textual en PDF puede ser imperfecta porque el texto puede estar comprimido,
fragmentado o convertido a imagen. Si hay riesgo:

- Revisar la fuente Markdown/DOCX usada para generar el PDF.
- Extraer texto del PDF con una herramienta local si está disponible.
- Revisar manualmente páginas donde podrían aparecer tablas, anexos o respuestas abiertas.
- No confiar solo en que una búsqueda sin resultados prueba ausencia total de datos sensibles.
