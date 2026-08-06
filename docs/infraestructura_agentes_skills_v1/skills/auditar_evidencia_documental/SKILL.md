---
name: auditar_evidencia_documental
description: Auditar matrices y textos de evidencia documental (citas, fechas, URLs, contradicciones) sin convertir periodismo en verdad territorial ni modificar informes oficiales.
version: 1
---

# auditar_evidencia_documental

**Política:** §§7, 9, 12.  
**Reglas:** R-EVI-01, R-MET-01, R-MET-02.  
**Referencia:** `docs/polos_gastro/evidencia_documental/` (matrices, handoff Codex/Claude, bibliografía).

## Propósito

Asegurar que la evidencia documental sea verificable, bien clasificada y usable para contraste con capas espaciales — no como sustituto de geometría ni de decisión.

## Cuándo usarla

- Tras armar o ampliar matrices de evidencia.  
- Antes de que cartografía o editorial usen topónimos documentales.  
- En handoffs documentales cross-tool.

## Cuándo no usarla

- Para dibujar polígonos.  
- Para validar KPIs de densidades (eso es metodológico/espacial).  
- Para scraping masivo de sitios con ToS dudoso.

## Insumos requeridos

- Matriz CSV/MD de evidencia.  
- Textos por polo o tema.  
- Criterio de IDs (BEL-E01, REC-R01, etc. si existen).

## Rutas permitidas

- Lectura/escritura en paquete documental experimental:  
  `docs/.../evidencia_documental/` o línea paralela nueva.  
- Outputs sanitizados asociados.

## Rutas prohibidas

- Informes oficiales PDF.  
- Cambiar GeoJSON.  
- Inventar URLs o fechas no vistas.

## Procedimiento

1. Revisar cada fila: afirmación, fuente, fecha, URL o localización de la fuente, nivel de evidencia.  
2. Marcar: alta / media / baja / rechazada (ej. cifra de “150 restaurantes” mal atribuida).  
3. Separar: hecho documental citado | inferencia del analista | decisión institucional.  
4. Detectar contradicciones entre fuentes y con decisiones firmadas.  
5. Corregir “link” genérico sin URL; no fabricar enlaces.  
6. Actualizar bibliografía verificada.  
7. Emitir handoff para cartógrafo/editor: qué se puede usar para nombrar y qué no.

## Criterios de aceptación

- [ ] Sin URLs inventadas.  
- [ ] Fechas inconsistentes corregidas o marcadas.  
- [ ] Rechazos explícitos documentados.  
- [ ] Ninguna nota periodística promovida a “límite oficial”.

## Outputs obligatorios

- Matriz actualizada o informe de auditoría.  
- Lista de contradicciones.  
- Handoff documental.

## Errores frecuentes

- Paywall citado como verificado al detalle sin acceso.  
- Confundir San Telmo y Recoleta en la misma frase de fuente.  
- Usar evidencia de un polo para bautizar otro.

## Checklist de QA

- IDs únicos.  
- Campos mínimos por fila.  
- Privacidad (no datos personales de terceros no públicos).  
- Estado por polo.

## Formato del handoff

```markdown
## Handoff — evidencia documental
- Polos/temas:
- Matriz:
- Listos para contraste espacial:
- No usar para nombrar:
- Rechazados:
- Contradicciones:
```

## Formato de respuesta final

Resumen por polo + rutas + “apto para contraste: sí/no”.

## Ejemplo breve

Corregir REC-R02 (cifra de 150 no es de Recoleta) y dejar constancia en matriz y handoff.

## Reglas de seguridad

No inventar fuentes. Política §1 y §12. Sin APIs no autorizadas.

## Autorización humana

- Tratar una fuente débil como decisión de límite.  
- Publicar bibliografía con material no verificable como “oficial”.
