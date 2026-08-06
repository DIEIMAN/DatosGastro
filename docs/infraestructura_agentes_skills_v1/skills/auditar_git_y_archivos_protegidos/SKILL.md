---
name: auditar_git_y_archivos_protegidos
description: Verificar higiene Git (sin add masivo, sin commit/push no autorizados) y que superficies protegidas (finales, F25/26, fuentes, baselines) no cambiaron vía comparación de hashes.
version: 1
---

# auditar_git_y_archivos_protegidos

**Política:** §§2, 4, 6.  
**Reglas:** R-FIN-01, R-SRC-01, R-GIT-01, R-GIT-02, R-HASH-01.  
**Referencia código:** listas `PROTECTED` en  
`scripts/polos_gastro/experimentos/pipeline_hibrido_repeticiones_v2/ejecutar_repeticiones_hibridas_v2.py` y  
`.../pipeline_hibrido_integracion_v21/construir_integracion_v21.py`.

## Propósito

Demostrar que el trabajo no alteró baselines protegidas ni violó reglas Git del proyecto.

## Cuándo usarla

- Antes y después de corridas experimentales.  
- En todo `QA_FINAL`.  
- Tras trabajo de otro agente en paralelo.

## Cuándo no usarla

- Para hacer commit “en nombre del usuario”.  
- Para borrar cambios ajenos sin confirmación.

## Insumos requeridos

- Lista `PROTECTED` del contexto (rutas de fase/paquete).  
- Opcional: snapshot de hashes previos.  
- Alcance del working tree a inspeccionar (`git status` solo lectura).

## Rutas permitidas

- Lectura de cualquier ruta protegida.  
- Escritura de reportes solo en el paquete de trabajo:  
  `verificacion_hashes_*.csv`, sección en QA_FINAL.

## Rutas prohibidas

- Modificar lo protegido “para que el hash calce”.  
- `git add .`, commit, push, reset --hard, clean -fd.

## Procedimiento

1. Fijar lista protegida (Fase 25, 26, v2.1, fuentes, PDFs finales del contexto).  
2. Calcular SHA-256 de cada archivo (árbol recursivo si es directorio).  
3. Comparar con baseline al inicio de la tarea (si no hay baseline, generar al inicio y al final).  
4. `git status` / `git diff --stat` en solo lectura: reportar staged=0 y que no hubo commit.  
5. Verificar que no se usó `git add .` en la sesión.  
6. Documentar N archivos comparados y diferencias (debe ser 0 en protegidos).

## Criterios de aceptación

- [ ] 0 cambios en protegidos (o lista explícita de cambios **autorizados**).  
- [ ] Staging limpio respecto de la tarea (o solo archivos del paquete si el humano lo pidió).  
- [ ] Sin commit/push ejecutados por el agente.

## Outputs obligatorios

- Tabla o CSV de verificación de hashes.  
- Párrafo Git en QA_FINAL.

## Errores frecuentes

- Proteger solo el PDF y olvidar el script generador.  
- Comparar con baseline vieja de otra rama sin decirlo.  
- “Arreglar” un protegido al detectar drift.

## Checklist de QA

- Lista PROTECTED explícita.  
- N hashes.  
- git status interpretado.  
- Fuentes no tocadas.

## Formato del handoff

```markdown
## Handoff — git y protegidos
- Baseline:
- Protegidos N / cambios:
- Staged:
- Commit/push:
- CSV hashes:
```

## Formato de respuesta final

“Protegidos: N archivos, 0 cambios. Git: sin commit/push; staged=0. Detalle: `ruta`.”

## Ejemplo breve

v2.1: 386 archivos protegidos, 0 cambios; script no ejecuta git add.

## Reglas de seguridad

Política §4 y §14.

## Autorización humana

- Cualquier modificación a un archivo protegido.  
- Commit/push.  
- Force-push / reset destructivo (en general prohibidos).
