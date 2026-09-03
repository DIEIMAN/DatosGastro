# Expediente documental — Abasto

**zona_id:** Z06  
**Fecha de consulta:** 2026-07-12  
**Rol:** investigador_documental_externo (+ red_team_documental)  
**Línea:** evidencia_documental_expansion_v4  
**Regla:** la evidencia interpreta y contextualiza; **no** supervisa clustering ni decide polígonos.

## 1. Resumen ejecutivo

Abasto tiene **identidad cultural-comercial fuerte** (Gardel, Mercado/Shopping, Balvanera) y relación compleja con **Av. Corrientes**. La semilla mezcla pizzerías del tramo céntrico (Güerrín, Las Cuartetas) que la evidencia oficial ubica más al centro.

- **Estado documental provisional:** `ZONA_RECONOCIDA_SIN_FORMA_CLARA`
- **Forma sugerida (documental, no geométrica):** Núcleo Abasto + relación con tramo Corrientes (no fusión automática)
- **Principal evidencia:** Identidad Abasto/Gardel + pizza Corrientes histórica
- **Principal debilidad:** Semilla mezcla pizzerías céntricas con Abasto

## 2. Nombres y alcance

| Campo | Valor |
|---|---|
| nombre_canonico_propuesto | Abasto |
| nombres_alternativos | Barrio del Abasto; Abasto–Corrientes |
| nombres_comerciales | Abasto Shopping / Mercado de Abasto |
| nombres_historicos | Mercado de Abasto; barrio del tango / Gardel |
| barrios_involucrados | Balvanera (Abasto); borde Almagro |
| comunas | Comuna 3 (principal); borde Comuna 5 |
| calles_referencia | Av. Corrientes (tramo Abasto); Agüero; Anchorena; Carlos Gardel |
| nodos_referencia | Mercado/Shopping Abasto; Museo Casa Carlos Gardel; pizzerías de Corrientes |
| ambiguedades | Confusión Abasto cultural vs. corredor pizza de Corrientes vs. shopping; no es sinónimo de toda Av. Corrientes |
| nombre_recomendado_para_analisis | Abasto (núcleo cultural-comercial) |
| nombre_recomendado_para_comunicacion | Abasto |

*Observaciones de normalización:* Tratar como área asociada a Corrientes, no fusión automática. Identidad cultural fuerte; forma gastronómica a contrastar espacialmente.

## 3. Antecedentes

La zona forma parte del universo semilla de polos candidatos del proyecto Polos Gastro (PDF semilla / fases 1–5). No está entre los polos con corrida territorial V3 adoptada (Belgrano, Recoleta, Costanera Norte). Esta expansión V4 la trata como **candidata documental**, no adoptada.

## 4. Evidencia oficial

Ver matriz de evidencia y fuentes con nivel OFICIAL_PRIMARIA asociadas a esta zona.

- **SRC003** — Turismo en Barrios | Circuitos al aire libre (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/turismo-en-barrios
- **SRC004** — Circuito Tradicional | 24, 48 y 72 horas (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/24-48-72/tradicional
- **SRC009** — Oferta y Establecimientos Gastronómicos (BA Data / GCBA). https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- **SRC027** — Calle Corrientes / pizza y teatro (itinerario) (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/24-48-72/tradicional
- **SRC034** — Balvanera (Turismo en Barrios) — Gardel y Abasto (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/turismo-en-barrios

## 5. Evidencia institucional / sectorial / académica

Se priorizaron fuentes oficiales y periodísticas confiables. La referencia académica SRC024 (Troncoso 2020) aporta marco: la folletería GCBA 2015 listaba seis polos clásicos; las candidatas de expansión no estaban en esa lista corta.

## 6. Evidencia periodística

Ver fuentes PERIODISTICA_CONFIABLE en la matriz de fuentes.

## 7. Calles y nodos mencionados

- Calles: Av. Corrientes (tramo Abasto); Agüero; Anchorena; Carlos Gardel
- Nodos: Mercado/Shopping Abasto; Museo Casa Carlos Gardel; pizzerías de Corrientes

## 8. Hipótesis de forma territorial

**Hipótesis (no decisión):** Núcleo Abasto + relación con tramo Corrientes (no fusión automática). Debe contrastarse con evidencia espacial; no dibujar polígono desde este expediente.

## 9. Relación con zonas vecinas

- **Abasto ↔ Avenida Corrientes** (solapamiento_narrativo; severidad ALTA): Semilla mezcla pizzerías céntricas con Abasto. → Cortes territoriales explícitos.
- **Abasto ↔ Balvanera/Almagro** (pertenencia_administrativa; severidad MEDIA): Abasto no es barrio oficial único; es subzona. → Usar buffer funcional, no solo barrio.

## 10. Evidencia a favor

- [MEDIA] Turismo BA asocia Balvanera/Abasto a Gardel, historia y movida comercial, no a un 'polo gastronómico Abasto' explícito en la misma fórmula que Crespo/Chacarita. (`EV-Z06-001`, SRC034)
- [MEDIA] Pizzerías de Corrientes (Güerrín, Las Cuartetas) se documentan en tramo más céntrico; semilla las agrupa con Abasto. (`EV-Z06-002`, SRC027)
- [MEDIA] Calle Corrientes figura históricamente como polo en folletería 2015; Abasto no aparece como polo separado en esa lista. (`EV-Z06-003`, SRC024)

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

- ¿Hay núcleo denso alrededor del Mercado de Abasto?
- ¿Dónde corta la densidad de Corrientes respecto del tramo centro?
- ¿Almagro aporta spillover?

## 15. Recomendación documental provisional

**Separar consulta Abasto de tramo pizza Corrientes centro.**

Prioridad Places: `ALTA` · Prioridad clustering: `ALTA`

No declarar zona adoptada. Separar: (1) evidencia documental, (2) inferencia, (3) hipótesis territorial, (4) decisión institucional futura.

## 16. Fuentes

- `SRC003` | OFICIAL_PRIMARIA | Turismo en Barrios | Circuitos al aire libre | https://turismo.buenosaires.gob.ar/es/turismo-en-barrios
- `SRC004` | OFICIAL_PRIMARIA | Circuito Tradicional | 24, 48 y 72 horas | https://turismo.buenosaires.gob.ar/es/24-48-72/tradicional
- `SRC009` | OFICIAL_PRIMARIA | Oferta y Establecimientos Gastronómicos | https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- `SRC024` | ACADEMICA | Geografía del consumo gastronómico en Buenos Aires | https://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1852-42652020000200005
- `SRC027` | OFICIAL_PRIMARIA | Calle Corrientes / pizza y teatro (itinerario) | https://turismo.buenosaires.gob.ar/es/24-48-72/tradicional
- `SRC034` | OFICIAL_PRIMARIA | Balvanera (Turismo en Barrios) — Gardel y Abasto | https://turismo.buenosaires.gob.ar/es/turismo-en-barrios

---

*Paquete: docs/polos_gastro/evidencia_documental_expansion_v4/*
