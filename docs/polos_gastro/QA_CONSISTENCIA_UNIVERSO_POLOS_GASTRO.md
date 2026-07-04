# QA de consistencia del universo PolosGastro

Fecha de corte: 2026-06-29.

Verificación cruzada de los cinco archivos del universo, hecha por lectura programática de los
CSV (sin modificar datos salvo correcciones menores explícitas, que se documentan al final).

Archivos revisados:
- `outputs/polos_gastro/universo_informe_polos_gastro.csv`
- `outputs/polos_gastro/matriz_validacion_polos_gastro.csv`
- `outputs/polos_gastro/base_delimitacion_preliminar_polos_gastro.csv`
- `outputs/polos_gastro/base_mapa_conceptual_polos_gastro.csv`
- `outputs/polos_gastro/fuentes_por_familia_territorial.csv`

---

## 1. Los 32 polos están representados donde corresponde — ✅

Los cinco archivos tienen exactamente **32 filas** con el mismo conjunto de `polo_id`. No hay
polos faltantes, sobrantes ni `polo_id` duplicados. Los 32 incluyen los 5 casos
`no_incluir_por_ahora` (que figuran en universo/matriz/delimitación/mapa/familias pero quedan
fuera del mapa conceptual visible).

## 2. `grupo_informe` consistente — ✅

Cruce por `polo_id` entre universo, delimitación, mapa conceptual y familias:
**0 discrepancias**. El mismo polo tiene el mismo grupo en los cuatro archivos.

Distribución (32): núcleo principal 6 · zona relevante 5 · emergente/candidato 9 · anexo 7 ·
no incluir por ahora 5.

## 3. Nombres públicos con tildes correctas — ✅ (con 1 nota)

El campo `nombre_publico` está correcto en universo, delimitación, mapa conceptual, familias y
en `nombres_publicos_polos_gastro.csv`: **Las Cañitas, García del Río, Villa Pueyrredón,
Microcentro / Centro, Monserrat, Av. San Martín**, etc.

**Nota documentada (no es error funcional):** el archivo `matriz_validacion_polos_gastro.csv`
conserva en su campo **interno** `nombre_polo` versiones sin tilde:
- "Las Canitas" (vs. Las Cañitas)
- "Garcia del Rio" / "Parque Saavedra / Garcia del Rio" (vs. García del Río)
- "Villa Pueyrredon / Av. San Martin" (vs. Villa Pueyrredón / Av. San Martín)
- "Microcentro y Centro" (vs. Microcentro / Centro)

Esto es un campo de trabajo de la matriz, no el nombre público. El nombre público canónico
vive en `nombres_publicos_polos_gastro.csv` y en `universo_informe_polos_gastro.csv`.
**Recomendación:** no copiar los strings de `matriz_validacion` al informe; usar siempre
`nombre_publico`. No se corrige la matriz aquí porque regenerarla implica re-ejecutar el
script de Fase 2 y podría alterar la trazabilidad; se deja como recomendación de no-uso.

## 4. Palermo Soho / Hollywood / Las Cañitas como subpolos — ✅

Los tres (`PG001A/B/C`) tienen `tipo_area = subpolo`, `familia_territorial = palermo_y_subpolos`
y `grupo_informe = nucleo_principal`. Las observaciones del universo indican explícitamente
"tratar junto con Palermo… como familia Palermo" y "no tratar como barrio independiente".
Coherente en los cinco archivos.

## 5. Barrio Chino como subzona de Belgrano — ✅

`PG006A_BARRIO_CHINO`: `tipo_area = subpolo`, `familia_territorial = belgrano_y_norte`,
`barrios_asociados = Belgrano`, observación "Presentar siempre dentro de Belgrano" /
"Subzona comercial-cultural; no barrio independiente". Coherente.

## 6. Familia de zona central (Microcentro/Centro, Monserrat, Retiro) — ✅

Los tres comparten `familia_territorial = zona_central` (etiquetada "Zona central y Recoleta"),
junto con Recoleta y Nuevo Bajo en Retiro. Microcentro/Centro y Monserrat/Retiro se manejan como
sublecturas de la misma familia, no como polos aislados. Las observaciones piden no duplicar
lectura entre Microcentro y Monserrat, y separar Retiro del subeje Nuevo Bajo. Coherente.

## 7. Corrientes y Abasto no fusionados sin justificación — ✅

`PG012_AVENIDA_CORRIENTES` (avenida, emergente) y `PG013_ABASTO` (barrio, anexo) son filas
separadas, ambas en la familia `cultura_avenidas_y_noches`. Las observaciones dicen
explícitamente "Analizar junto a Abasto, pero no fusionar todavía" y "Trabajar junto a
Corrientes en fase futura". Comparten familia (justificado), pero **no** están fusionados.
Coherente.

## 8. Los «no incluir por ahora» no aparecen como mapeados — ✅

Los 5 casos `no_incluir_por_ahora` (Bajo Belgrano, Avenida Boedo, Federico Lacroze / Libertador
a Cabildo, Parque Saavedra / García del Río, Villa Pueyrredón / Av. San Martín) tienen
`mostrar_en_mapa_conceptual = no` y `representacion_sugerida = no_mapear` en
`base_mapa_conceptual`. No aparecen como puntos/áreas en los mapas conceptuales (sí en la caja
"No mapeados en esta fase"). Coherente con la regla de no mapear casos descartados.

> Verificación cruzada: hay 5 filas con `mostrar_en_mapa_conceptual = no` y son exactamente
> esos 5 polos.

## 9. Precisión de delimitación coincide con el riesgo metodológico — ✅

Distribución: alta 3 · media 11 · baja 16 · sin delimitación 2.

- Los 2 `sin_delimitacion` (Federico Lacroze, García del Río) son `no_incluir_por_ahora` y
  `no_mapear`. Coherente: sin fuente → sin geometría.
- Los 3 de precisión `alta` (Palermo Soho, Palermo Hollywood, DoHo/Donado-Holmberg) tienen
  delimitación textual por avenidas/calles citada de fuente turística oficial; el riesgo
  metodológico aclara que "no equivalen a polígono oficial". Coherente.
- Los 16 de precisión `baja` reciben representación conservadora (punto conceptual o familia
  sin geometría) y su riesgo advierte contra polígonos cerrados. Coherente.

El gráfico `precision_delimitacion_polos.png` reproduce exactamente estos conteos (3/11/16/2).

---

## Resumen QA

| Verificación | Resultado |
| --- | --- |
| 32 polos representados en los 5 archivos | ✅ |
| `grupo_informe` consistente | ✅ (0 discrepancias) |
| `familia_territorial` consistente | ✅ (0 discrepancias) |
| Tildes en `nombre_publico` | ✅ (nota sobre campo interno de la matriz) |
| Subpolos de Palermo | ✅ |
| Barrio Chino dentro de Belgrano | ✅ |
| Familia zona central | ✅ |
| Corrientes / Abasto no fusionados | ✅ |
| «No incluir» no mapeados | ✅ |
| Precisión vs. riesgo | ✅ |

## Correcciones menores realizadas

**Ninguna.** Todos los hallazgos son consistentes o son notas de documentación (campo interno
de la matriz sin tilde). No se modificó ningún CSV: la única observación accionable
(nombres sin tilde en `matriz_validacion`) requiere regenerar el script de Fase 2 y se deja
como recomendación de no-uso, no como edición, para no alterar la trazabilidad.

## Recomendaciones (sin aplicar)

1. Para el informe, tomar nombres **siempre** de `nombre_publico`, nunca del campo
   `nombre_polo` de `matriz_validacion`.
2. Si en una fase futura se regenera la matriz, alinear `nombre_polo` con `nombre_publico`
   (tildes) para evitar confusión.
