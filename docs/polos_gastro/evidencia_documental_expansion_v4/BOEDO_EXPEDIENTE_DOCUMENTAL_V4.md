# Expediente documental — Avenida Boedo

**zona_id:** Z07  
**Fecha de consulta:** 2026-07-12  
**Rol:** investigador_documental_externo (+ red_team_documental)  
**Línea:** evidencia_documental_expansion_v4  
**Regla:** la evidencia interpreta y contextualiza; **no** supervisa clustering ni decide polígonos.

## 1. Resumen ejecutivo

Boedo muestra **identidad cultural** (tango, bares, avenida histórica) pero **evidencia débil** de polo o corredor gastronómico contemporáneo en fuentes oficiales abiertas localizadas en esta pasada.

- **Estado documental provisional:** `IDENTIDAD_DOCUMENTAL_DEBIL`
- **Forma sugerida (documental, no geométrica):** Eje de avenida / cafés (a testear)
- **Principal evidencia:** Identidad barrial/cafés
- **Principal debilidad:** Falta evidencia de concentración contemporánea

## 2. Nombres y alcance

| Campo | Valor |
|---|---|
| nombre_canonico_propuesto | Avenida Boedo / Boedo |
| nombres_alternativos | Boedo; eje Boedo |
| nombres_comerciales | — |
| nombres_historicos | Boedo literario/tango; cafés históricos |
| barrios_involucrados | Boedo; bordes San Cristóbal y Almagro |
| comunas | Comuna 5 |
| calles_referencia | Av. Boedo; Pasaje San Ignacio; entorno San Juan / Independencia |
| nodos_referencia | Café Margot (Av. Boedo); ejes culturales de Boedo |
| ambiguedades | Identidad cultural/barrial ≠ concentración gastronómica contemporánea documentada como polo |
| nombre_recomendado_para_analisis | Avenida Boedo |
| nombre_recomendado_para_comunicacion | Boedo / Avenida Boedo |

*Observaciones de normalización:* Fuentes oficiales de Turismo BA resaltan tango, bares y circuitos barriales; evidencia de 'polo gastronómico' débil.

## 3. Antecedentes

La zona forma parte del universo semilla de polos candidatos del proyecto Polos Gastro (PDF semilla / fases 1–5). No está entre los polos con corrida territorial V3 adoptada (Belgrano, Recoleta, Costanera Norte). Esta expansión V4 la trata como **candidata documental**, no adoptada.

## 4. Evidencia oficial

Ver matriz de evidencia y fuentes con nivel OFICIAL_PRIMARIA asociadas a esta zona.

- **SRC009** — Oferta y Establecimientos Gastronómicos (BA Data / GCBA). https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- **SRC030** — Turismo en Barrios — Almagro / Boedo (contexto cultural) (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/turismo-en-barrios

## 5. Evidencia institucional / sectorial / académica

Se priorizaron fuentes oficiales y periodísticas confiables. La referencia académica SRC024 (Troncoso 2020) aporta marco: la folletería GCBA 2015 listaba seis polos clásicos; las candidatas de expansión no estaban en esa lista corta.

## 6. Evidencia periodística

Ver fuentes PERIODISTICA_CONFIABLE en la matriz de fuentes.

## 7. Calles y nodos mencionados

- Calles: Av. Boedo; Pasaje San Ignacio; entorno San Juan / Independencia
- Nodos: Café Margot (Av. Boedo); ejes culturales de Boedo

## 8. Hipótesis de forma territorial

**Hipótesis (no decisión):** Eje de avenida / cafés (a testear). Debe contrastarse con evidencia espacial; no dibujar polígono desde este expediente.

## 9. Relación con zonas vecinas

- Ver `MATRIZ_RELACIONES_Y_CONFLICTOS_TERRITORIALES_V4.csv`.

## 10. Evidencia a favor


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

- ¿Existe cluster a lo largo de Av. Boedo?
- ¿Solo hitos de cafés notables sin continuidad?

## 15. Recomendación documental provisional

**Exploratorio; no promover como polo sin spatial proof.**

Prioridad Places: `MEDIA` · Prioridad clustering: `MEDIA`

No declarar zona adoptada. Separar: (1) evidencia documental, (2) inferencia, (3) hipótesis territorial, (4) decisión institucional futura.

## 16. Fuentes

- `SRC009` | OFICIAL_PRIMARIA | Oferta y Establecimientos Gastronómicos | https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- `SRC024` | ACADEMICA | Geografía del consumo gastronómico en Buenos Aires | https://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1852-42652020000200005
- `SRC030` | OFICIAL_PRIMARIA | Turismo en Barrios — Almagro / Boedo (contexto cultural) | https://turismo.buenosaires.gob.ar/es/turismo-en-barrios

---

*Paquete: docs/polos_gastro/evidencia_documental_expansion_v4/*
