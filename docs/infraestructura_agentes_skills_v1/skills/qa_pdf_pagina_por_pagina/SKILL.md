---
name: qa_pdf_pagina_por_pagina
description: QA visual obligatorio de PDFs DataGastro/DGDGAS. Renderizar páginas a PNG, inspeccionar cada una y no dar por terminado un PDF solo porque el generador corrió sin error.
version: 1
---

# qa_pdf_pagina_por_pagina

**Política:** `POLITICA_OPERATIVA_DATAGASTRO.md` §8.  
**Reglas:** R-PDF-01, R-MAR-01.  
**Producto existente (Claude):** `.claude/skills/datagastro-qa-pdf` y `scripts/qa/pdf_check.py` — esta skill V1 es la versión canónica de procedimiento para todas las plataformas.

## Propósito

Garantizar que un PDF sea legible y mostrable (o honestamente marcado como borrador interno) mediante revisión visual página a página.

## Cuándo usarla

- Tras generar o regenerar cualquier PDF (informe, mapas en PDF, pack).  
- Antes de reportar “PDF listo”.

## Cuándo no usarla

- Sobre PDFs fuente de terceros que no se regeneran (solo lectura/citar).  
- Como reemplazo de validación de KPIs (complementa `validar_metricas_y_kpis`).

## Insumos requeridos

- Ruta del PDF.  
- Python del venv.  
- Criterio de marca: publicable DGDGAS vs interno.

## Rutas permitidas

- Lectura del PDF.  
- Escritura de PNG de QA junto al PDF o en `qa_png_<nombre>/` (rutas ya cubiertas por `.gitignore` típico).

## Rutas prohibidas

- Sobrescribir PDF oficial de otra fase.  
- Commitear PNG de QA internos sin pedido.

## Procedimiento

1. `.venv/Scripts/python.exe scripts/qa/pdf_check.py <ruta.pdf>`  
   - Opciones: `--pages`, `--dpi 150` si texto chico.  
2. Leer **cada** PNG con herramienta de imagen/visión.  
3. Buscar: solapes, desbordes, páginas en blanco/`[SIN TEXTO]`, marca incorrecta, portada con “borrador/fecha/versión” si el estándar del informe lo prohíbe, leyendas de mapa ilegibles.  
4. Si falla: corregir generador → regenerar → volver a 1.  
5. Si hay `kpis_lock.json`: encadenar skill de KPIs.  
6. Reportar: N páginas revisadas, defectos, correcciones, rutas absolutas.

## Criterios de aceptación

- [ ] Todas las páginas renderizadas e inspeccionadas.  
- [ ] Sin defectos bloqueantes abiertos (o listados y aceptados por humano).  
- [ ] Marca DGDGAS en publicables.  
- [ ] No se declaró listo solo por exit code 0 del generador.

## Outputs obligatorios

- Carpeta PNG de QA.  
- Resumen en respuesta y/o sección en `QA_FINAL`.

## Errores frecuentes

- Revisar solo la portada.  
- Usar `pdftoppm`/dependencias nuevas.  
- Dejar “DataGastro” en pieza pública.

## Checklist de QA

- Portada y pie.  
- Índice vs secciones.  
- Tablas y mapas.  
- Texto cortado / bajo contraste.

## Formato del handoff

```markdown
## Handoff — QA PDF
- PDF:
- Páginas:
- DPI:
- PNG:
- Defectos bloqueantes:
- Defectos menores:
- Regeneraciones:
```

## Formato de respuesta final

“Revisé N/N páginas. Bloqueantes: … Menores: … PDF: `ruta`. PNG: `ruta`.”

## Ejemplo breve

Tras `build_fase25_…py`, correr `pdf_check` sobre el PDF de oficina, mirar 11 PNG, corregir leyenda p.3, regenerar, re-chequear.

## Reglas de seguridad

Política §2, §5, §8. No instalar PyMuPDF si ya está en venv.

## Autorización humana

- Entregar PDF con defectos conocidos “menores” sin señalarlos.  
- Reemplazar PDF oficial de fase cerrada.
