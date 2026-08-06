---
name: crear_paquete_revision_sanitizado
description: Armar carpeta y/o ZIP de revisión humana sin crudos, secretos ni PII. Incluye selección de archivos, escaneo de privacidad, integridad ZIP y metadata.
version: 1
---

# crear_paquete_revision_sanitizado

**Política:** §§5, 6, 11.  
**Reglas:** R-ZIP-01, R-PRIV-01, R-PAR-01.  
**Referencia:** `agent_skills/shared/datagastro_qa_privacidad.md`; patrones `armar_paquete_revision.py` en experimentos Polos.

## Propósito

Producir un paquete compartible para revisión interna (humano u otro agente) **sin** datos sensibles ni insumos crudos prohibidos.

## Cuándo usarla

- Cierre de auditoría o experimento para enviar a Diego / otro rol.  
- Export de evidencia documental o matrices sanitizadas.

## Cuándo no usarla

- Para archivar crudos Places o formularios con PII (van a internal/gitignore).  
- Como backup completo del monorepo.

## Insumos requeridos

- Lista blanca de archivos a incluir.  
- Directorio destino bajo `outputs/.../<paquete>/`.  
- Resultado de escaneo de privacidad.

## Rutas permitidas

- Escritura solo en `outputs/<proyecto>/.../<paquete>/` o `outputs/infraestructura_agentes_skills_v1/`.  
- Lectura de docs/outputs del experimento (no de secretos).

## Rutas prohibidas

- Incluir `.env`, `**/interno/`, `place_id` crudos, XLSX de respuestas con PII, API keys.  
- Escribir en Drive.  
- Pisar packs oficiales cerrados.

## Procedimiento

1. Definir lista blanca (MD de síntesis, CSV agregados, mapas no sensibles, QA_FINAL, MANIFEST).  
2. Excluir: raw Places, filas individuales identificables, logs con keys.  
3. Copiar a carpeta `REVISION_*/` con rutas relativas limpias.  
4. Escaneo privacidad (patrones de `datagastro_qa_privacidad.md`).  
5. Generar ZIP; `ZipFile.testzip()` o equivalente.  
6. Metadata JSON opcional: conteo archivos, bytes, sha256 del ZIP, restricciones.  
7. Documentar en MANIFEST qué se excluyó y por qué.

## Criterios de aceptación

- [ ] 0 hallazgos automáticos de privacidad en el pack (o hallazgos justificados como falsos positivos).  
- [ ] ZIP íntegro.  
- [ ] Sin duplicados confusos de rutas.  
- [ ] README del pack con orden de lectura.

## Outputs obligatorios

- Carpeta de revisión.  
- ZIP (si se pidió).  
- Metadata o sección en MANIFEST.  
- Nota de exclusiones.

## Errores frecuentes

- Incluir “por si acaso” el CSV crudo.  
- Rutas absolutas de usuario dentro del ZIP.  
- Olvidar README de lectura.

## Checklist de QA

- Privacidad.  
- Integridad ZIP.  
- Tamaño razonable.  
- Sin secretos.

## Formato del handoff

```markdown
## Handoff — paquete revisión
- Carpeta:
- ZIP:
- SHA-256 ZIP:
- Archivos N:
- Exclusiones:
- Privacidad:
```

## Formato de respuesta final

Rutas absolutas + SHA-256 + “apto para revisión humana / no”.

## Ejemplo breve

Pack GPT-56: 26 archivos, sin JSON crudo Places, SHA-256 del ZIP documentado en QA_FINAL.

## Reglas de seguridad

Política §§1, 5, 14. No `git add` del ZIP sin autorización (muchos ZIP están en gitignore).

## Autorización humana

- Incluir material marcado interno.  
- Publicar fuera del área.
