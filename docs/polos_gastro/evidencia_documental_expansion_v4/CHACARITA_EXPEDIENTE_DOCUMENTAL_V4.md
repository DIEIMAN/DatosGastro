# Expediente documental — Chacarita

**zona_id:** Z02  
**Fecha de consulta:** 2026-07-12  
**Rol:** investigador_documental_externo (+ red_team_documental)  
**Línea:** evidencia_documental_expansion_v4  
**Regla:** la evidencia interpreta y contextualiza; **no** supervisa clustering ni decide polígonos.

## 1. Resumen ejecutivo

Chacarita tiene **página oficial de polo** y prensa 2024 que describe el corredor Jorge Newbery (≈6 cuadras, >20 propuestas) y al menos un segundo foco en Dorrego. Riesgos: **Chacalermo** y confusión con **Federico Lacroze**.

- **Estado documental provisional:** `IDENTIDAD_DOCUMENTAL_FUERTE`
- **Forma sugerida (documental, no geométrica):** Corredor Newbery + posible segundo núcleo Dorrego
- **Principal evidencia:** Turismo BA + Clarín Newbery
- **Principal debilidad:** Nombres de frontera; no fusionar con Lacroze completa

## 2. Nombres y alcance

| Campo | Valor |
|---|---|
| nombre_canonico_propuesto | Chacarita |
| nombres_alternativos | Chaca; barrio Chacarita |
| nombres_comerciales | Chacalermo (prensa, frontera Palermo-Chacarita); polo gastronómico Chacarita (Turismo BA) |
| nombres_historicos | Chacarita |
| barrios_involucrados | Chacarita; bordes Colegiales y Palermo |
| comunas | Comuna 15 |
| calles_referencia | Av. Jorge Newbery; Av. Dorrego; Charlone; Guevara; Maure; Fraga; Condarco |
| nodos_referencia | Cementerio de la Chacarita; Estación Federico Lacroze (borde); Movistar Arena (borde) |
| ambiguedades | Chacalermo confunde con Palermo; Federico Lacroze no es sinónimo de todo Chacarita |
| nombre_recomendado_para_analisis | Chacarita |
| nombre_recomendado_para_comunicacion | Chacarita |

*Observaciones de normalización:* Turismo BA delimita concentración entre Dorrego y Newbery. Prensa describe corredor Newbery (Corrientes–Córdoba).

## 3. Antecedentes

La zona forma parte del universo semilla de polos candidatos del proyecto Polos Gastro (PDF semilla / fases 1–5). No está entre los polos con corrida territorial V3 adoptada (Belgrano, Recoleta, Costanera Norte). Esta expansión V4 la trata como **candidata documental**, no adoptada.

## 4. Evidencia oficial

Turismo BA: mayoría de propuestas entre Dorrego y Newbery; narrativa de reconversión de talleres a gastronomía innovadora.

- **SRC002** — Polo gastronómico Chacarita (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/article/polo-gastron%C3%B3mico-chacarita
- **SRC003** — Turismo en Barrios | Circuitos al aire libre (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/turismo-en-barrios
- **SRC009** — Oferta y Establecimientos Gastronómicos (BA Data / GCBA). https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos

## 5. Evidencia institucional / sectorial / académica

Se priorizaron fuentes oficiales y periodísticas confiables. La referencia académica SRC024 (Troncoso 2020) aporta marco: la folletería GCBA 2015 listaba seis polos clásicos; las candidatas de expansión no estaban en esa lista corta.

## 6. Evidencia periodística

Clarín Gourmet 2024 es la fuente periodística más detallada del corredor Newbery y su antigüedad aproximada (~7 años). Infobae 2023 documenta el nombre Chacalermo en la frontera con Palermo.
- **SRC012** — En Chacarita, los mejores y los más nuevos restaurantes de avenida de Newbery (2024-09-26). https://www.clarin.com/gourmet/chacarita-mejores-nuevos-restaurantes-avenida-newbery-polo-personalidad-buenos-precios_0_GjmBjylej0.html
- **SRC013** — Chacalermo, cómo es el nuevo epicentro gastronómico de moda en Buenos Aires (2023-08-19). https://www.infobae.com/tendencias/2023/08/19/chacalermo-como-es-el-nuevo-epicentro-gastronomico-de-moda-en-buenos-aires/

## 7. Calles y nodos mencionados

- Calles: Av. Jorge Newbery; Av. Dorrego; Charlone; Guevara; Maure; Fraga; Condarco
- Nodos: Cementerio de la Chacarita; Estación Federico Lacroze (borde); Movistar Arena (borde)

## 8. Hipótesis de forma territorial

**Hipótesis:** corredor Newbery (Corrientes–Córdoba) + posible segundo núcleo Dorrego; no un único polígono barrial ni Lacroze completa.

## 9. Relación con zonas vecinas

- **Villa Crespo ↔ Chacarita** (borde_y_nodo_compartido; severidad MEDIA): Arena y etiquetas Chacacrespo; frontera porosa. → Correr juntas con IDs distintos; no fusionar nombres.
- **Chacarita ↔ Palermo** (nombre_frontera; severidad ALTA): Chacalermo es etiqueta mediática de frontera. → No crear zona Chacalermo; analizar superposición.
- **Chacarita ↔ Federico Lacroze** (posible_borde_no_sinonimo; severidad MEDIA): Polo Chacarita oficial no se centra en Lacroze. → No usar Lacroze completa como proxy de Chacarita.
- **Chacarita ↔ Colegiales** (borde; severidad BAJA): Proximidad; no fusión automática. → Revisar spillover en bordes.

## 10. Evidencia a favor

- [ALTA] Turismo BA denomina polo gastronómico Chacarita y ubica la mayoría de propuestas entre Dorrego y Newbery. (`EV-Z02-001`, SRC002)
- [ALTA] Clarín 2024 documenta corredor Newbery de ~6 cuadras (Corrientes–Córdoba) con >20 propuestas y ~7 años de formación. (`EV-Z02-002`, SRC012)
- [MEDIA] Prensa usa 'Chacalermo' para frontera Chacarita–Palermo (Córdoba–Dorrego–Corrientes). (`EV-Z02-003`, SRC013)

## 11. Contraindicadores

- Ver objeciones y red team; ausencia de contraindicio explícito no implica ausencia de riesgo.

## 12. Vacíos documentales

- Polígono o tramos oficiales con medidas.
- Serie temporal de oferta.
- Fuentes de Comuna / juntas comunales específicas.
- Validación 2026 de locales citados en notas antiguas.

## 13. Riesgos de sobreinterpretación

- Convertir 'polo' de turismo o prensa en límite municipal.
- Usar un patio/mercado o un local famoso como proxy de zona.
- Adoptar nombres comerciales (DoHo, Chacalermo, Nuevo Bajo) sin glosa.
- Supervisar el clustering con esta narrativa.

## 14. Preguntas para la corrida espacial

- ¿Un o dos clusters principales (Newbery vs Dorrego)?
- ¿Hay continuidad hacia Palermo que justifique etiqueta de frontera?
- ¿La estación Lacroze aporta densidad o es ruido de borde?
- ¿Persisten los locales citados en 2024?

## 15. Recomendación documental provisional

**Correr Newbery y Dorrego; evaluar multiparte.**

Prioridad Places: `MUY_ALTA` · Prioridad clustering: `MUY_ALTA`

No declarar zona adoptada. Separar: (1) evidencia documental, (2) inferencia, (3) hipótesis territorial, (4) decisión institucional futura.

## 16. Fuentes

- `SRC002` | OFICIAL_PRIMARIA | Polo gastronómico Chacarita | https://turismo.buenosaires.gob.ar/es/article/polo-gastron%C3%B3mico-chacarita
- `SRC003` | OFICIAL_PRIMARIA | Turismo en Barrios | Circuitos al aire libre | https://turismo.buenosaires.gob.ar/es/turismo-en-barrios
- `SRC009` | OFICIAL_PRIMARIA | Oferta y Establecimientos Gastronómicos | https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- `SRC012` | PERIODISTICA_CONFIABLE | En Chacarita, los mejores y los más nuevos restaurantes de avenida de Newbery | https://www.clarin.com/gourmet/chacarita-mejores-nuevos-restaurantes-avenida-newbery-polo-personalidad-buenos-precios_0_GjmBjylej0.html
- `SRC013` | PERIODISTICA_CONFIABLE | Chacalermo, cómo es el nuevo epicentro gastronómico de moda en Buenos Aires | https://www.infobae.com/tendencias/2023/08/19/chacalermo-como-es-el-nuevo-epicentro-gastronomico-de-moda-en-buenos-aires/
- `SRC024` | ACADEMICA | Geografía del consumo gastronómico en Buenos Aires | https://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1852-42652020000200005

---

*Paquete: docs/polos_gastro/evidencia_documental_expansion_v4/*
