---
name: gestionar_decisiones_humanas
description: Registrar, respetar y escalar decisiones humanas (DEC/DH) separadas de hallazgos técnicos. Evitar reabrir lo firmado y documentar contradicciones.
version: 1
---

# gestionar_decisiones_humanas

**Política:** §§9, 12.  
**Reglas:** R-DEC-01, R-MET-03, R-EVI-01.  
**Referencia:** `REGISTRO_DECISIONES_APROBADAS_DIEGO.md`; matrices DH/DEC Polos; handoff evidencia Belgrano/Recoleta/Costanera.

## Propósito

Mantener el límite entre lo que el análisis sugiere y lo que la institución decide.

## Cuándo usarla

- Al redactar informes o mapas con nombres/jerarquías.  
- Al integrar resultados técnicos que podrían chocar con una DEC.  
- Al proponer reaperturas.

## Cuándo no usarla

- Para “decidir por Diego” nombres o inclusiones.  
- Para convertir estabilidad de cluster en decisión institucional automática.

## Insumos requeridos

- Registro o matriz de decisiones del paquete.  
- Resultado técnico relevante (opcional).  
- Estado: firmada / abierta / sujeta a prueba.

## Rutas permitidas

- Lectura de registros existentes.  
- Escritura en línea paralela o actualización **autorizada** del registro del paquete experimental:  
  `REGISTRO_DECISIONES_*.md`, `MATRIZ_DECISIONES_*.md`.

## Rutas prohibidas

- Alterar decisiones en informes oficiales cerrados.  
- Borrar el historial de una DEC.

## Procedimiento

1. Clasificar cada ítem: evidencia | inferencia técnica | decisión humana.  
2. Listar decisiones **firmadas** que el trabajo debe respetar.  
3. Listar abiertas y qué insumo las cierra.  
4. Si hay contradicción técnica: una nota estructurada (no reescritura dispersa).  
5. Proponer opciones con recomendación prudente; no auto-firmar.  
6. Actualizar matriz solo con estados honestos (“sujeto a prueba”, “firmada”, etc.).

## Criterios de aceptación

- [ ] Separación evidencia/inferencia/decisión visible.  
- [ ] Firmadas no reabiertas en silencio.  
- [ ] Reaperturas explícitas y únicas.  
- [ ] Dueño de la firma = humano.

## Outputs obligatorios

- Matriz o registro actualizado (paquete experimental).  
- Notas de contradicción si aplica.

## Errores frecuentes

- Tratar Turismo BA o nota periodística como decisión de límite.  
- Reabrir Belgrano/Recoleta/Costanera en cada párrafo.  
- Mezclar “recomendación del modelo” con “aprobado”.

## Checklist de QA

- IDs DEC/DH estables.  
- Fecha y autor de firma.  
- Dependencias a pipeline técnico.

## Formato del handoff

```markdown
## Handoff — decisiones humanas
- Firmadas a respetar:
- Abiertas:
- Contradicciones nuevas:
- Esperando a Diego:
```

## Formato de respuesta final

Tabla DEC/DH + acciones permitidas sin espera vs bloqueadas.

## Ejemplo breve

DEC-05 Costanera multiparte firmada a nivel representación; repetición técnica inestable → no revertir DEC; ajustar texto de provisoriedad.

## Reglas de seguridad

Política §9 y §12.

## Autorización humana

- Firmar o revertir cualquier DEC/DH.  
- Publicar nombres nuevos como oficiales.
