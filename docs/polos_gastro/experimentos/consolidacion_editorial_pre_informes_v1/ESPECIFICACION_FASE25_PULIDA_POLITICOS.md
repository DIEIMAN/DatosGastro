# Especificación — Fase 25 pulida para presentación política

Estado: ESPECIFICACIÓN EDITORIAL EXPERIMENTAL — **no es un informe final** y no autoriza
por sí misma la regeneración de la pieza. Fecha: 2026-07-11.
Basada en `AUDITORIA_EDITORIAL_FASE25_PARA_POLITICOS.md` y `MATRIZ_AJUSTES_FASE25.csv`
(misma carpeta) y en el `REGISTRO_DECISIONES_APROBADAS_DIEGO.md` (DEC-01…DEC-09).

## 1. Objetivo

Convertir la Fase 25 (pieza interna prudente, entregada a la oficina) en una versión
apta para decisores políticos, que responda en el cuerpo cuatro preguntas:

1. ¿Dónde se concentra la actividad gastronómica de la Ciudad?
2. ¿Qué zonas están consolidadas?
3. ¿Qué ejes tienen relevancia?
4. ¿Qué zonas merecen seguimiento?

Sin comunicar en el cuerpo: algoritmos, parámetros, problemas técnicos, vocabulario de
trabajo interno.

## 2. Audiencia

Primaria: jefatura política de la DGDGAS y funcionarios del Gobierno de la Ciudad sin
formación técnica. Secundaria: equipos de otras áreas que reciban la pieza como
referencia. Tiempo de lectura esperado: 5–10 minutos; lectura probable: solo mapas,
títulos y cajas.

## 3. Extensión recomendada

**9–10 páginas** (contra las 11 actuales): se ganan dos páginas fusionando resumen y
alcance y eliminando la página 6 duplicada; se agregan "Próximos pasos" y nota
metodológica final. Formato y marca: los actuales de Fase 25 (paleta, tipografía, pies
de página DGDGAS).

## 4. Estructura página por página

| # | Página | Contenido | Origen |
| --- | --- | --- | --- |
| 1 | Portada | Título actual + subtítulo con contenido ("Lectura territorial de la actividad gastronómica") | Ajuste de texto |
| 2 | Resumen ejecutivo | 3–4 afirmaciones territoriales en positivo + 1 línea de alcance al pie | Reescritura (fusiona pp. 3+4 actuales) |
| 3 | Mapa general | Mapa a página casi completa con jerarquía visual en tres niveles: polos consolidados / ejes relevantes / zonas en observación. Caja "Lectura" con hallazgo real | Rediseño del asset actual |
| 4 | Detalle: Palermo / Las Cañitas | Estructura actual con leyendas y tags simplificados | Ajuste |
| 5 | Detalle: Puerto Madero | Ídem; sin microajustes de fondo hasta resolver DH-06 | Ajuste mínimo |
| 6 | Detalle: San Telmo | Ídem; etiqueta principal con nombre editorial propio | Ajuste |
| 7 | Detalle: Corrientes | Título "Corrientes" (Abasto como área asociada en el propio mapa y texto, por DEC-01/02) | Ajuste de título + texto |
| 8 | Detalle: Belgrano | Un solo sistema de rótulo para las tres subzonas, declaradas lectura editorial (DEC-04) | Ajuste |
| 9 | Próximos pasos | Qué zonas se profundizan, qué se sigue observando, cuándo habrá actualización | Página nueva |
| 10 | Nota metodológica | Fuentes, criterio de lectura, convención de representación (DEC-09), aclaración de referencias | Página nueva (absorbe descargos) |

El índice se elimina (pieza de 10 páginas no lo necesita). Si jefatura lo exige, se
reincorpora y la pieza pasa a 11.

## 5. Mapas

**Se conservan (con ajuste de leyenda/tags, sin tocar geometrías):**

- `assets/mapa_fase25_palermo_las_canitas.*` — mejor lámina actual; plantilla del resto.
- `assets/mapa_fase25_san_telmo.*` — conservar hasta que DH-01 se resuelva.
- `assets/mapa_fase25_corrientes_abasto.*` — la banda continua ya cumple DEC-01.
- `assets/mapa_fase25_belgrano.*` — conservar con rótulos unificados (DEC-04).

**Deben regenerarse:**

- **Mapa global** (`assets/global_mapa_fase25.png`): a página completa, con jerarquía
  visual de tres niveles y leyenda sin "aproximado". Es la regeneración de mayor valor
  político y puede hacerse ya (criterio editorial declarado, sin datos nuevos).
- **Puerto Madero:** tras la repetición técnica (resultados de Codex, DH-06); no antes.
- **San Telmo:** solo si DH-01 se firma con eje Defensa respaldado.
- **Costanera Norte en el mapa global:** representación multiparte discontinua rotulada
  exploratoria (DEC-05/06), cuando haya decisión de representación tomada.

Regla general: ningún mapa nuevo introduce categorías técnicas en leyenda; toda
convención se declara una vez en la nota metodológica.

## 6. Textos que deben reducirse

- Resumen ejecutivo: de 3 párrafos + caja a 4 frases sustantivas + 1 línea de alcance.
- Página de alcance (actual p. 4): desaparece como página; queda 1 nota de 3–4 líneas.
- Caja "Lectura" del mapa global: de texto de relleno a hallazgo territorial.
- Cajas "Referencias del universo semilla": retituladas "Referencias de la zona";
  en la versión política los nombres de locales se retiran o van a anexo como
  referencias ilustrativas (decisión final de Diego).
- Bullets meta de la p. 6 actual: desaparecen.

## 7. Nivel de detalle metodológico

- **Cuerpo (pp. 1–9):** cero metodología. Ni fuentes, ni métodos, ni advertencias más
  allá de la línea estándar de alcance.
- **Nota metodológica (p. 10):** qué se relevó (fuentes abiertas y referencias
  territoriales), qué significa cada representación (área de referencia, corredor,
  sector), la convención cartográfica de las franjas (DEC-09, formulación cualitativa),
  y la aclaración de que las referencias de locales no son ranking ni acreditación.
  Máximo una página, tono sobrio, sin cifras de parámetros.
- **Nunca en esta pieza:** clustering, Places, buffers en metros, estabilidad,
  cobertura porcentual, nombres de algoritmos.

## 8. Lenguaje recomendado

(Detalle completo en `GUIA_LENGUAJE_INFORMES_POLOS.md`.)

- "polo gastronómico consolidado", "eje gastronómico", "área de referencia", "sector",
  "zona en observación", "lectura territorial", "presencia gastronómica destacada".
- Afirmaciones en positivo con el hedging concentrado en una sola nota.
- Verbos institucionales: "se concentra", "se consolida", "se observa", "merece
  seguimiento".

## 9. Lenguaje prohibido o inconveniente

- Prohibido en cuerpo y leyendas: "universo semilla", "área de lectura", "APROX.",
  "candidato", "cluster", "buffer", "KDE", "HDBSCAN", "KMeans", "Places", "ruido",
  "evidencia media/baja", "no oficial", "preliminar", "borrador".
- Inconveniente (usar solo si jefatura lo pide): números de locales por zona (la pieza
  no es un padrón), extremos de calles con precisión ("9 de Julio – Callao") sin
  declarar convención.

## 10. Disclaimer adecuado

Una sola formulación estándar, dos apariciones como máximo (pie del resumen y nota
metodológica):

> "Las áreas y ejes representados son referencias de lectura territorial elaboradas por
> la DGDGAS; no constituyen límites oficiales ni un registro de establecimientos."

## 11. Cómo evitar que parezca preliminar

1. Eliminar la página-descargo y los tags "APROX." (la señal #1 de provisoriedad).
2. Rectángulos punteados grises (Abasto, Bajo Belgrano, Belgrano R) → tramas sutiles
   con etiqueta, mismas en todas las láminas.
3. Un solo sistema de rótulos en los cinco mapas.
4. Mapa global dominante y con jerarquía: una pieza que afirma algo no parece borrador.
5. Página de próximos pasos: transforma "esto es aproximado" en "esto continúa así".
6. Mantener la fecha y una versión visible discreta (p. ej. "Julio 2026") sin numerar
   fases internas: "Fase 25" no aparece en la pieza.

## 12. Cómo mantener honestidad sin llenar de advertencias

- Toda la honestidad se concentra en dos dispositivos: la línea estándar de alcance
  (§10) y la nota metodológica final (§7). El resto de la pieza afirma con lenguaje
  calibrado ("referencia", "lectura", "en observación") que ya lleva la incertidumbre
  incorporada sin declararla en cada elemento.
- La jerarquía de tres niveles del mapa global es en sí misma un acto de honestidad:
  distingue lo consolidado de lo que está en observación sin necesidad de disclaimers.
- Las zonas cuyo detalle depende de trabajo técnico pendiente (Puerto Madero, San
  Telmo si cambia) no se prometen: la página de próximos pasos dice "profundización en
  curso" sin exponer el problema técnico.

## 13. Qué comunica y qué no

**Comunica:** dónde se concentra la actividad gastronómica; qué zonas están
consolidadas (arco norte, ejes históricos); qué ejes tienen relevancia (Corrientes como
corredor único con Abasto asociado); qué zonas merecen seguimiento (Costanera como
lectura exploratoria, zonas en observación del mapa global).

**No comunica:** algoritmos, parámetros, fuentes externas por nombre, coberturas
porcentuales, problemas técnicos, decisiones internas pendientes, jerga de trabajo.

## 14. Condiciones de producción

- Los ajustes de texto/leyenda/estructura no requieren datos nuevos ni resultados de
  Codex: pueden implementarse apenas Diego apruebe esta especificación.
- La implementación se hará como **fase nueva** (heredando del generador de Fase 25,
  como Fase 25 heredó de 24) — Fase 25 final permanece intacta (guardrail).
- QA obligatorio: `scripts/qa/pdf_check.py` + inspección visual de todas las páginas
  antes de dar por terminada la pieza.
