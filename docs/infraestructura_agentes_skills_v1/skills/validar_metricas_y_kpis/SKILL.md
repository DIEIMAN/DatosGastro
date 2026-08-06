---
name: validar_metricas_y_kpis
description: Validar que las cifras de un informe o paquete coinciden con fuentes/tablas y, si existe, con kpis_lock.json. Evitar drift y universos mezclados.
version: 1
---

# validar_metricas_y_kpis

**Política:** §§6–7, 12.  
**Reglas:** R-KPI-01, R-UNI-01, R-MET-01.  
**Herramienta:** `.venv/Scripts/python.exe scripts/qa/validate_kpis.py <lock> <entregable…>`.

## Propósito

Asegurar que los números publicados son trazables y estables entre regeneraciones.

## Cuándo usarla

- Antes de cerrar informe con KPIs.  
- Tras regenerar PDF/MD desde generador.  
- En auditorías metodológicas de conteos (polígonos, puntos, respuestas de formulario).

## Cuándo no usarla

- Para “mejorar” un número sin fuente.  
- Para sumar F01+F02 como total de locales.

## Insumos requeridos

- Entregable(s) texto/PDF/MD.  
- Tablas fuente o analytics del paquete.  
- `kpis_lock.json` si el informe lo define.

## Rutas permitidas

- Lectura de tablas del paquete y lock.  
- Escritura de reporte de validación en el paquete (MD/CSV de discrepancias).

## Rutas prohibidas

- Alterar datos fuente para que el KPI “pase”.  
- Editar el lock sin avisar (los canónicos no cambian sin autorización).

## Procedimiento

1. Extraer cifras afirmadas en el entregable.  
2. Clasificar cada una: universo F/I/E, fuente, fecha.  
3. Si hay lock: correr `validate_kpis.py`.  
4. Recomputar conteos clave desde tablas del paquete (no desde memoria).  
5. Listar: verificado / no verificable / discrepante.  
6. Prohibir lenguaje de “locales activos” si la métrica no lo es.

## Criterios de aceptación

- [ ] Lock OK o inexistente justificado.  
- [ ] Discrepancias abiertas = bloqueantes.  
- [ ] Universos no sumados indebidamente.  
- [ ] “No verificable” explícito cuando falte insumo.

## Outputs obligatorios

- Resultado validate_kpis (si aplica).  
- Tabla de cifras en QA o anexo.

## Errores frecuentes

- Validar solo la portada.  
- Confundir v2 “55 grupos” con “41 retenidos”.  
- Actualizar el texto y no el lock (o al revés).

## Checklist de QA

- n y denominadores.  
- Unidades (archivos, puntos, polígonos, respuestas).  
- Captions de gráficos.

## Formato del handoff

```markdown
## Handoff — KPIs
- Lock:
- validate_kpis:
- Discrepancias:
- No verificables:
```

## Formato de respuesta final

OK/FAIL + lista de faltantes + rutas.

## Ejemplo breve

Informe Cafecito o Polos con lock de candidatos: el PDF debe contener exactamente los strings del lock.

## Reglas de seguridad

No inventar el valor “correcto”. Política §12.

## Autorización humana

- Cambiar valores del `kpis_lock.json`.  
- Publicar con discrepancias conocidas.
