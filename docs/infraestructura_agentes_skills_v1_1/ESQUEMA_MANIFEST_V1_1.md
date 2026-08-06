# Esquema de manifest V1.1 (sin autorreferencia)

## Problema V1

`MANIFEST_ARCHIVOS.csv` se incluía a sí mismo; tamaño/hash dejaban de coincidir tras el append.

## Solución V1.1

| Archivo | Contenido |
| --- | --- |
| `MANIFEST_CONTENIDO.csv` | Una fila por archivo del pack **excepto** este CSV. Columnas: `ruta_relativa,bytes,sha256` |
| `CHECKSUMS_SHA256.txt` | Líneas `sha256  ruta` para: `MANIFEST_CONTENIDO.csv`, `metadata_*.json`, `QA_FINAL_*.md` (si aplica), y el **ZIP** (hash del ZIP se escribe *después* de crearlo, en un segundo paso o en archivo junto al ZIP) |
| `metadata_*.json` | Metadatos del paquete (no lista todos los hashes de contenido) |

### Flujo de empaquetado correcto

1. Armar carpeta de revisión con todos los artefactos (sin ZIP aún).  
2. Generar `MANIFEST_CONTENIDO.csv` sobre esa carpeta (excluyendo el propio CSV y excluyendo `CHECKSUMS_SHA256.txt` si se genera después, o regenerar checksums al final).  
3. Escribir `metadata_*.json` y `QA_FINAL_*.md`.  
4. Regenerar `MANIFEST_CONTENIDO.csv` incluyendo metadata y QA (aún sin autorreferencia).  
5. Escribir `CHECKSUMS_SHA256.txt` con hashes de manifest, metadata, QA.  
6. Crear ZIP de la carpeta.  
7. Añadir al `CHECKSUMS_SHA256.txt` **junto al ZIP** (fuera o dentro con nombre `CHECKSUMS_SHA256.txt` que incluya hash del zip calculado post-creación — si va **dentro** del ZIP, el hash del ZIP no puede estar dentro del mismo ZIP de forma coherente).  

**Regla práctica adoptada:**

- Dentro del pack/ZIP: `MANIFEST_CONTENIDO.csv` + `CHECKSUMS_INTERNO.txt` (manifest + metadata + QA + demás archivos listados sin el checksums interno si se genera al final en un solo paso: mejor listar solo manifest+metadata+QA en CHECKSUMS_INTERNO).  
- Junto al ZIP (fuera): `CHECKSUMS_SHA256.txt` con hash del ZIP + hash del manifest + metadata.

Implementación en `scripts/infraestructura_agentes_skills_v1_1/empaquetar_revision_v1_1.py`.
