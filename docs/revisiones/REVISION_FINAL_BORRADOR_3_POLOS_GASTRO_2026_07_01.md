# Revision final - Borrador 3 PolosGastro

Fecha de revision: 2026-07-01. Documento interno de revision metodologica e institucional.
Revisor: auditoria asistida (Claude Code). No es informe final. No modifica el Borrador 3.

Alcance de la revision: los seis documentos de `docs/polos_gastro/fase9_borrador_3/`, la tabla
consolidada `outputs/polos_gastro/fase9_borrador_3/tablas/tabla_polos_para_informe_borrador_3.csv`
y, como contraste, la lectura comparada y la tabla de la Fase 8 fuerte. Todo en solo lectura.

---

## 1. Diagnostico general

El Borrador 3 esta metodologicamente cerrado y es consistente entre sus piezas. Cumple los
controles centrales de la auditoria:

| Control | Resultado | Evidencia |
| --- | --- | --- |
| Universo de 32 registros | Cumple | La tabla consolidada tiene 32 filas de datos; el informe lo declara en secciones 4 y 16. |
| 4 areas nucleo | Cumple | Palermo (agrupando Soho, Hollywood y Las Canitas), Recoleta, San Telmo y Puerto Madero (secciones 6 y 7). |
| Palermo como area nucleo con subpolos | Cumple | Los 3 registros base se conservan; la senal alta del barrio se advierte explicitamente como no validante de cada subpolo. |
| Puerto Madero nucleo con documentacion media | Cumple | Seccion 7: se sostiene por reconocimiento urbano e institucional, con delimitacion fina pendiente y senal objetiva baja bien contextualizada. |
| Belgrano como macroarea de revision | Cumple | Seccion 8: Barrio Chino subzona fuerte; Bajo Belgrano y Belgrano R con tratamiento diferenciado; la senal barrial declarada como no distintiva de subzonas. |
| Abasto en anexo | Cumple | Seccion 10 y fila 24 de la tabla: "anexo / caso a validar", con senal media aproximada por Balvanera y advertencia de que no separa Abasto de Corrientes. No aparece como zona relevante. |
| Paternal y Bajo Belgrano no subidos automaticamente | Cumple | Ambos con "podria... no se aplica" en el cuerpo y movimiento sugerido solo en `NOTAS_REVISION_HUMANA_BORRADOR_3.md`. |
| Capa objetiva como contexto, no ranking | Cumple | La tabla conserva el orden del Borrador 2; el nivel es cualitativo; el indice numerico no aparece en el Borrador 3. |
| El indice no viaja solo | Cumple | El indice numerico quedo en la Fase 8 fuerte; el Borrador 3 solo usa niveles cualitativos acompanados siempre de lectura prudente y limitacion territorial. |
| Sin confusion oferta registrada / habilitaciones / locales activos | Cumple | Notas metodologicas 7 y 8, anexo tecnico 7 y seccion 14 del informe lo separan de forma explicita y repetida. |
| Sin afirmaciones de densidad real ni vigencia | Cumple | Formulas consistentes: "no mide", "no confirma", "no valida vigencia operativa". |
| Sin lenguaje publico de descarte ("dejar afuera") | Cumple | Se usa "en espera de evidencia" y la seccion 11 explica que la denominacion es deliberada y no descarta valor potencial. |
| Tono DGDGAS prudente | Cumple | Condicionales ("podria", "permitiria"), separacion hallazgos/limites, sin superlativos ni lenguaje de IA. |

**Control de riesgo destacado:** el cuadrante "evidencia debil o pendiente + senal objetiva alta"
quedo vacio y el documento deja constancia explicita de ello (seccion 13 del informe y seccion 6
del anexo tecnico). Es el control mas importante contra la conclusion indebida y esta bien resuelto.

---

## 2. Fortalezas

1. **Separacion de capas sostenida en todos los documentos.** Capa documental (decide el grupo),
   validacion liviana (sugiere) y capa objetiva (contextualiza) nunca se mezclan como un mismo
   universo probatorio.
2. **Ningun cambio de clasificacion aplicado automaticamente.** Todas las recomendaciones de Fase 8
   liviana estan marcadas "no aplicar ahora" y consolidadas en una tabla de decisiones humanas
   pendientes.
3. **Advertencias territoriales caso por caso.** Cada fila de la tabla tiene lectura prudente y
   limitacion territorial propia (Palermo no valida subpolos; Balvanera no separa Abasto de
   Corrientes; Belgrano no distingue Barrio Chino, Bajo Belgrano ni Belgrano R).
4. **Tratamiento correcto de los no calculables.** Los corredores sin delimitacion no reciben senal
   de barrio, con justificacion metodologica (notas, seccion 5).
5. **Trazabilidad.** Fechas de corte declaradas (base 2026-06-30, incorporaciones 2026-07-01),
   fuentes F01/F02 con universos explicitos (2823 y 44169 registros) y limite conocido de F02
   (44099 registros sin barrio util, solo lectura comunal).
6. **Higiene de la tarea.** El cierre documenta que no hubo Google Places, ni datos fuente tocados,
   ni Borrador 2 modificado, ni commit/push/staging.

---

## 3. Problemas detectados

Ninguno bloquea el cierre metodologico. En orden de relevancia:

1. **Paternal: tipo territorial "corredor" con senal barrial calculada (menor, unico hallazgo de
   consistencia).** La regla de las notas metodologicas (seccion 5) establece que los corredores sin
   delimitacion son "no calculables"; sin embargo, la tabla consolidada asigna a Paternal
   `tipo_territorial = corredor` y `nivel_senal_objetiva = bajo` (senal del barrio Paternal). Los
   otros siete corredores del universo quedaron correctamente como no calculables. El texto mitiga
   el riesgo ("Paternal como barrio aporta contexto; no valida el corredor gastronomico"), pero la
   tabla queda formalmente inconsistente con la regla.
2. **Verbo "validan" en la seccion 9 del informe (estilistico).** "Fuentes oficiales validan
   identidad de teatro/pizza" es la formulacion mas asertiva del documento. Esta acotada a identidad
   (no a polo, densidad ni vigencia), por lo que es defendible; aun asi, "respaldan" o "documentan"
   seria mas homogeneo con el resto del tono.
3. **Duplicacion menor en la lectura comparada de Fase 8 fuerte (fuera del Borrador 3).** Costanera
   Norte, DoHo y Avenida Caseros aparecen tanto en la tabla de "senal no concluyente" como en la de
   "no calculables". Es un documento de Fase 8 cerrada y no debe modificarse ahora; solo se deja
   constancia para una eventual version futura.

---

## 4. Frases o secciones a ajustar (si se decide ajustar)

Ninguna correccion se considera inevitable; el Borrador 3 no se modifico. Si la revision humana
quiere pulir antes de una version presentable:

| Ubicacion | Texto actual | Ajuste sugerido | Prioridad |
| --- | --- | --- | --- |
| Informe, seccion 9, Avenida Corrientes | "Fuentes oficiales validan identidad de teatro/pizza" | "Fuentes oficiales respaldan la identidad de teatro/pizza" | Baja |
| Tabla consolidada, fila Paternal | `tipo_territorial = corredor` + `nivel_senal_objetiva = bajo` | Decidir en revision humana: (a) tratar la senal como no calculable por corredor, o (b) reclasificar el tipo visible como "barrio con corredor propuesto" manteniendo la senal barrial como contexto. Documentar la opcion elegida en las notas metodologicas. | Media |

---

## 5. Riesgos metodologicos

1. **Lectura de ranking por terceros.** Aunque el Borrador 3 lo evita, cualquier reordenamiento
   futuro de la tabla por nivel de senal (por ejemplo al aplicar diseno o exportar) reconstruiria un
   ranking. El orden del Borrador 2 debe tratarse como invariante.
2. **Senal de Palermo leida como validacion de subpolos.** El 100 relativo del barrio es el valor
   mas citable del trabajo y el mas propenso a sobreinterpretacion. Las advertencias existen; el
   riesgo es que se pierdan al resumir o diagramar.
3. **Recomendaciones de Fase 8 liviana aplicadas sin revision.** Paternal y Bajo Belgrano tienen
   movimientos sugeridos documentados; si un lector apurado los toma como aplicados, la estructura
   ejecutiva cambiaria sin decision humana.
4. **Fuentes pendientes de verificacion.** Parque Saavedra depende de una fuente Clarin no revisada
   completa; Federico Lacroze de una fuente antigua. No deben endurecerse esos casos hasta cerrar la
   verificacion.
5. **Erosion de advertencias en derivados.** Resumenes, laminas o versiones disenadas tienden a
   recortar las limitaciones territoriales. La regla "el indice/nivel nunca viaja solo" debe
   trasladarse a cualquier derivado visual.

---

## 6. Que esta listo para una version presentable

- La estructura ejecutiva completa (4 areas nucleo, zonas relevantes, emergentes, candidatos,
  anexo, en espera de evidencia) y su justificacion caso por caso.
- El aparato metodologico: notas, anexo tecnico, advertencias obligatorias y control de cuadrante
  vacio.
- La tabla consolidada de 32 registros con columnas de contexto.
- El lenguaje institucional: prudente, sin descarte, sin densidad ni vigencia afirmadas.
- La trazabilidad de fuentes y fechas de corte.

## 7. Que falta antes de publicar

1. Cerrar las decisiones humanas listadas en `NOTAS_REVISION_HUMANA_BORRADOR_3.md` (Paternal,
   Bajo Belgrano, Corrientes/Abasto, recortes de Caseros y DoHo, tratamiento de Costanera Norte).
2. Resolver la inconsistencia formal de Paternal (seccion 4 de esta revision).
3. Completar la verificacion de las fuentes pendientes (Clarin de Parque Saavedra) o degradar su
   mencion.
4. Decidir el tratamiento editorial de las referencias del documento semilla.
5. Definir la politica de marca en salida (DGDGAS publica; DataGastro solo interno) y aplicar QA
   publico de privacidad.
6. Revision humana formal de jefatura sobre el alcance de un Borrador 4 o version presentable.
7. Recien despues: mapas de contexto autorizados y aplicacion de diseno sobre copia controlada.

---

## 8. Recomendacion

**Avanzar con condiciones.** El Borrador 3 esta en condiciones de pasar a revision humana y de
servir como base de una version presentable. Las condiciones son: (a) cerrar las decisiones humanas
pendientes antes de cualquier cambio de clasificacion; (b) resolver el caso Paternal en la tabla;
(c) mantener el orden del Borrador 2 como invariante en todo derivado; (d) trasladar las
advertencias obligatorias del anexo tecnico a cualquier pieza visual o resumida que se genere.

No se recomienda publicar el Borrador 3 tal cual (es un documento interno por diseno) ni iniciar
la aplicacion productiva de diseno antes de validar la preview controlada del Design System.
