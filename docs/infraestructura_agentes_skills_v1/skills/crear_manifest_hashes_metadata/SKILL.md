---
name: crear_manifest_hashes_metadata
description: Generar MANIFEST_ARCHIVOS con rutas, tamaños, hashes y metadata de paquete para trazabilidad y revisión.
version: 1
---

# crear_manifest_hashes_metadata

**Política:** §6.  
**Reglas:** R-MAN-01, R-HASH-01.  
**Referencia:** `MANIFEST_ARCHIVOS.md` en experimentos Polos (`pipeline_hibrido_*`, consolidación editorial).

## Propósito

Dejar inventario reproducible de lo entregado en un paquete.

## Cuándo usarla

- Cierre de cualquier paquete experimental o de revisión.  
- Antes del ZIP sanitizado.

## Cuándo no usarla

- Sobre árboles enormes de `node_modules` o `.venv`.  
- Como inventario de todo el monorepo.

## Insumos requeridos

- Raíz del paquete (docs y/o outputs).  
- Alcance de archivos a incluir.

## Rutas permitidas

- Escritura: `docs/.../<paquete>/MANIFEST_ARCHIVOS.md` y/o  
  `outputs/.../<paquete>/metadata_*.json`.

## Rutas prohibidas

- Hashear e incluir secretos o crudos en manifests **publicables**.  
- Escribir manifest dentro de fases oficiales cerradas.

## Procedimiento

1. Listar archivos del paquete (relativos al root del repo).  
2. Para cada uno: tamaño bytes + SHA-256.  
3. Redactar `MANIFEST_ARCHIVOS.md` (tabla ruta | bytes | hash).  
4. Opcional: JSON metadata (fecha, estado experimental, restricciones, script generador).  
5. Si hay ZIP posterior, añadir fila del ZIP al final o en addendum.

## Criterios de aceptación

- [ ] Toda ruta del pack de revisión aparece o se justifica la exclusión.  
- [ ] Hashes calculados con herramienta del entorno (Python venv o Get-FileHash).  
- [ ] Encoding UTF-8 del MD.

## Outputs obligatorios

- `MANIFEST_ARCHIVOS.md`  
- Metadata JSON si el paquete es ZIP de revisión.

## Errores frecuentes

- Rutas absolutas de una sola máquina como única clave.  
- Olvidar scripts del paquete.  
- Hashes de archivos que luego se regeneran sin actualizar manifest.

## Checklist de QA

- Conteo archivos vs disco.  
- Hash del manifest no es requisito; hash de insumos sí.

## Formato del handoff

```markdown
## Handoff — manifest
- MANIFEST:
- Metadata:
- Archivos N:
- Notas:
```

## Formato de respuesta final

Ruta del manifest + N archivos + advertencias.

## Ejemplo breve

Manifest v2.1 con decenas de entradas docs/outputs/scripts del paquete.

## Reglas de seguridad

No copiar contenido sensible al manifest (solo rutas/hashes/tamaños).

## Autorización humana

Ninguna para generar manifest de paquete experimental propio; sí para publicar el manifest fuera del área si contiene rutas internas sensibles.
