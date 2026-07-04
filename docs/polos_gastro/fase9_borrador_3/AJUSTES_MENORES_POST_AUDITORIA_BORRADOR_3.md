# Ajustes menores post-auditoria - Borrador 3

Fecha: 2026-07-01. Documento interno. Registra los dos unicos ajustes aplicados al Borrador 3
despues de la revision final (`docs/revisiones/REVISION_FINAL_BORRADOR_3_POLOS_GASTRO_2026_07_01.md`).
No hay cambios de grupo ni de clasificacion. No es informe final.

## 1. Que se reviso

- `INFORME_POLOS_GASTRO_BORRADOR_3.md` (busqueda de formulaciones concluyentes; unica ocurrencia
  de "validan" en sentido asertivo: seccion 9, Avenida Corrientes).
- `tabla_polos_para_informe_borrador_3.csv` (fila Paternal, hallazgo de consistencia de la
  auditoria).
- Vocabulario de tipos territoriales de la seccion 5 del informe y regla de corredores no
  calculables de las notas metodologicas (seccion 5).

## 2. Que se toco

**Informe (1 linea, seccion 9, Avenida Corrientes).** Se suavizo el verbo:

- Antes: "Fuentes oficiales validan identidad de teatro/pizza, pero no un corredor gastronomico
  cerrado."
- Ahora: "Fuentes oficiales respaldan la identidad de teatro/pizza, pero no un corredor
  gastronomico cerrado."

No se toco ninguna otra linea del informe. La ocurrencia de "se validan" en
`NOTAS_REVISION_HUMANA_BORRADOR_3.md` (seccion 6) se dejo como esta: describe una accion futura
condicional, no una afirmacion de evidencia.

**Tabla (1 fila, Paternal, 2 celdas).**

- `tipo_territorial`: antes `corredor`; ahora `area de revision (barrio-circuito a validar)`.
- `limitacion_territorial_capa_objetiva`: antes "Paternal como barrio aporta contexto; no valida
  el corredor gastronomico."; ahora "La senal proviene del barrio de referencia Paternal y aporta
  contexto; no valida el circuito gastronomico propuesto ni implica un corredor delimitado."

No se modifico ninguna otra celda de la fila ni ninguna otra fila. El grupo de Paternal sigue
siendo `candidato a validar - documentacion debil`; la senal sigue siendo `bajo`; las
recomendaciones de Fase 8 liviana siguen marcadas sin aplicar.

## 3. Decision tomada sobre Paternal (hallazgo 1)

**Problema.** La fila asignaba tipo `corredor` con senal objetiva barrial `bajo`, mientras la regla
metodologica establece que los corredores sin delimitacion son "no calculables". Los otros siete
corredores del universo cumplen la regla.

**Opciones evaluadas.**

- (a) Pasar la senal de Paternal a "no calculable" por corredor: descartada, porque contradiria el
  cuerpo del informe (seccion 9: "la senal objetiva del barrio Paternal es baja y solo aporta
  contexto") y porque la evidencia de Fase 8 fuerte si calculo una senal barrial directa para el
  barrio Paternal.
- (b) Ajustar el tipo visible para que el caso no parezca un corredor delimitado: **elegida**. El
  tipo pasa a `area de revision (barrio-circuito a validar)`, que usa el vocabulario existente de
  la seccion 5 del informe ("area de revision") y describe la situacion real: un barrio con un
  circuito gastronomico propuesto, todavia a validar.

**Consistencia resultante.** La regla "corredor sin delimitacion = no calculable" queda sin
excepciones: los siete casos tipificados como corredor son no calculables, y Paternal, que tiene
senal barrial directa, ya no esta tipificado como corredor. La limitacion territorial de la fila
aclara de forma explicita que la senal proviene del barrio de referencia y no valida el circuito.

**Que no se hizo.** No se cambio el grupo, no se subio la documentacion a media (sigue siendo
recomendacion de Fase 8 liviana "sin aplicar"), no se toco la senal ni la lectura prudente.

## 4. Frase suavizada sobre Corrientes (hallazgo 2)

Ver seccion 2. Unico cambio: "validan identidad" -> "respaldan la identidad". El resto de la
oracion (que niega el corredor gastronomico cerrado) quedo intacto.

## 5. Que queda pendiente para decision humana

Ninguno de estos ajustes cierra las decisiones de `NOTAS_REVISION_HUMANA_BORRADOR_3.md`, que
siguen abiertas y ahora estan desarrolladas con recomendacion conservadora en
`PROPUESTA_DECISIONES_HUMANAS_BORRADOR_4.md`:

- Si Paternal sube a candidato con documentacion media (la recomendacion de Fase 8 liviana sigue
  sin aplicar).
- Si Bajo Belgrano pasa a anexo a validar.
- El tratamiento conjunto de Avenida Corrientes y Abasto.
- Los recortes territoriales de Caseros/Barracas, DoHo y Costanera Norte.
- El tratamiento editorial de las referencias del documento semilla.
- Que tablas de capa objetiva entran al anexo de una version presentable.

## 6. Trazabilidad

- Hallazgos de origen: secciones 3 y 4 de la revision final del 2026-07-01.
- Archivos modificados: `INFORME_POLOS_GASTRO_BORRADOR_3.md` (1 linea) y
  `tabla_polos_para_informe_borrador_3.csv` (1 fila, 2 celdas).
- Archivos NO modificados: resumen ejecutivo, notas metodologicas, anexo tecnico, notas de
  revision humana, cierre, y todo lo anterior a Fase 9 (Borrador 2, Fase 7, Fase 8).
