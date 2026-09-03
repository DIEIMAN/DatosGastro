# Expediente documental — Microcentro y Centro

**zona_id:** Z05  
**Fecha de consulta:** 2026-07-12  
**Rol:** investigador_documental_externo (+ red_team_documental)  
**Línea:** evidencia_documental_expansion_v4  
**Regla:** la evidencia interpreta y contextualiza; **no** supervisa clustering ni decide polígonos.

## 1. Resumen ejecutivo

El Centro/Microcentro **no debe tratarse como una sola zona gastronómica**. La evidencia oficial desagrega nodos (Plaza de Mayo, Av. de Mayo, Obelisco/Tribunales, Corrientes pizza-teatro, Retiro). Ver `SUBUNIDADES_DOCUMENTALES_CENTRO_V4.csv`.

- **Estado documental provisional:** `EVIDENCIA_CONTRADICTORIA`
- **Forma sugerida (documental, no geométrica):** Familia de subunidades (ver CSV subunidades)
- **Principal evidencia:** Itinerarios oficiales desagregados + academia 2015
- **Principal debilidad:** Tratar Centro como una unidad

## 2. Nombres y alcance

| Campo | Valor |
|---|---|
| nombre_canonico_propuesto | Centro / Microcentro (familia de subunidades) |
| nombres_alternativos | Microcentro; Centro porteño; San Nicolás; área central |
| nombres_comerciales | Microcentro renovado; Centro Renovado (semilla) |
| nombres_historicos | Microcentro financiero; Casco histórico adyacente |
| barrios_involucrados | San Nicolás; Monserrat; Retiro (parcial); límites difusos |
| comunas | Comuna 1 (principal) |
| calles_referencia | Florida; Lavalle; Reconquista; Diagonal Norte; Av. de Mayo; Corrientes (tramo centro); 9 de Julio |
| nodos_referencia | Plaza de Mayo; Obelisco; Tribunales/Plaza Lavalle; Galerías Pacífico; Avenida de Mayo |
| ambiguedades | Centro ≠ Microcentro ≠ Bajo porteño ≠ Nuevo Bajo; no tratar como una sola unidad gastronómica |
| nombre_recomendado_para_analisis | Familia Centro (subunidades) |
| nombre_recomendado_para_comunicacion | Centro y Microcentro (con subunidades) |

*Observaciones de normalización:* Investigación profunda en SUBUNIDADES_DOCUMENTALES_CENTRO_V4.csv. Evitar etiqueta única.

## 3. Antecedentes

La zona forma parte del universo semilla de polos candidatos del proyecto Polos Gastro (PDF semilla / fases 1–5). No está entre los polos con corrida territorial V3 adoptada (Belgrano, Recoleta, Costanera Norte). Esta expansión V4 la trata como **candidata documental**, no adoptada.

## 4. Evidencia oficial

Ver matriz de evidencia y fuentes con nivel OFICIAL_PRIMARIA asociadas a esta zona.

- **SRC003** — Turismo en Barrios | Circuitos al aire libre (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/turismo-en-barrios
- **SRC004** — Circuito Tradicional | 24, 48 y 72 horas (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/24-48-72/tradicional
- **SRC009** — Oferta y Establecimientos Gastronómicos (BA Data / GCBA). https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- **SRC033** — Retiro | Circuitos 1 y 2 (Turismo en Barrios) (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/turismo-en-barrios

## 5. Evidencia institucional / sectorial / académica

Se priorizaron fuentes oficiales y periodísticas confiables. La referencia académica SRC024 (Troncoso 2020) aporta marco: la folletería GCBA 2015 listaba seis polos clásicos; las candidatas de expansión no estaban en esa lista corta.

## 6. Evidencia periodística

Ver fuentes PERIODISTICA_CONFIABLE en la matriz de fuentes.
- **SRC022** — Jorge Ferrari: 'El Microcentro está más lindo que nunca' (2023-05-30). https://elplanetaurbano.com/2023/05/jorge-ferrari-empresario-gastronomico-el-microcentro-esta-mas-lindo-que-nunca/
- **SRC025** — Casi el 60% de los locales gastronómicos se concentran en siete barrios porteños (s/f (nid2095107)). https://www.lanacion.com.ar/buenos-aires/casi-el-60-de-los-locales-gastronomicos-se-concentran-en-siete-barrios-portenos-nid2095107/

## 7. Calles y nodos mencionados

- Calles: Florida; Lavalle; Reconquista; Diagonal Norte; Av. de Mayo; Corrientes (tramo centro); 9 de Julio
- Nodos: Plaza de Mayo; Obelisco; Tribunales/Plaza Lavalle; Galerías Pacífico; Avenida de Mayo

## 8. Hipótesis de forma territorial

**Hipótesis (no decisión):** Familia de subunidades (ver CSV subunidades). Debe contrastarse con evidencia espacial; no dibujar polígono desde este expediente.

## 9. Relación con zonas vecinas

- Ver `MATRIZ_RELACIONES_Y_CONFLICTOS_TERRITORIALES_V4.csv`.

## 10. Evidencia a favor

- [ALTA] Turismo BA documenta subnodos del centro: Plaza de Mayo, Av. de Mayo, Obelisco/Tribunales, Corrientes pizza-teatro, no un único 'polo Centro'. (`EV-Z05-001`, SRC004)
- [ALTA] Academia 2020: folletería GCBA 2015 distinguía seis polos; Calle Corrientes aparece, no 'Microcentro' como polo único. (`EV-Z05-002`, SRC024)

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

- ¿Qué subunidades muestran estructura espacial propia?
- ¿Microcentro financiero tiene oferta distinta de Av. de Mayo?
- ¿Cómo se separa Corrientes centro de Abasto?
- ¿Qué bbox evitar para no mezclar todo Comuna 1?

## 15. Recomendación documental provisional

**Correr subunidades; nunca un solo bbox de Centro.**

Prioridad Places: `MUY_ALTA (por subunidad)` · Prioridad clustering: `MUY_ALTA (separado)`

No declarar zona adoptada. Separar: (1) evidencia documental, (2) inferencia, (3) hipótesis territorial, (4) decisión institucional futura.

## 16. Fuentes

- `SRC003` | OFICIAL_PRIMARIA | Turismo en Barrios | Circuitos al aire libre | https://turismo.buenosaires.gob.ar/es/turismo-en-barrios
- `SRC004` | OFICIAL_PRIMARIA | Circuito Tradicional | 24, 48 y 72 horas | https://turismo.buenosaires.gob.ar/es/24-48-72/tradicional
- `SRC009` | OFICIAL_PRIMARIA | Oferta y Establecimientos Gastronómicos | https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- `SRC022` | PERIODISTICA_CONFIABLE | Jorge Ferrari: 'El Microcentro está más lindo que nunca' | https://elplanetaurbano.com/2023/05/jorge-ferrari-empresario-gastronomico-el-microcentro-esta-mas-lindo-que-nunca/
- `SRC024` | ACADEMICA | Geografía del consumo gastronómico en Buenos Aires | https://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1852-42652020000200005
- `SRC025` | PERIODISTICA_CONFIABLE | Casi el 60% de los locales gastronómicos se concentran en siete barrios porteños | https://www.lanacion.com.ar/buenos-aires/casi-el-60-de-los-locales-gastronomicos-se-concentran-en-siete-barrios-portenos-nid2095107/
- `SRC033` | OFICIAL_PRIMARIA | Retiro | Circuitos 1 y 2 (Turismo en Barrios) | https://turismo.buenosaires.gob.ar/es/turismo-en-barrios

---

*Paquete: docs/polos_gastro/evidencia_documental_expansion_v4/*
