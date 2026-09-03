# Expediente documental — Villa Urquiza

**zona_id:** Z10  
**Fecha de consulta:** 2026-07-12  
**Rol:** investigador_documental_externo (+ red_team_documental)  
**Línea:** evidencia_documental_expansion_v4  
**Regla:** la evidencia interpreta y contextualiza; **no** supervisa clustering ni decide polígonos.

## 1. Resumen ejecutivo

Villa Urquiza es **barrio con oferta** y mención oficial de gastronomía en un set de calles que se solapa con DoHo. Debe analizarse como **multieje**, no como un solo corredor ni como la marca DoHo.

- **Estado documental provisional:** `ZONA_RECONOCIDA_SIN_FORMA_CLARA`
- **Forma sugerida (documental, no geométrica):** Multieje (Triunvirato/Congreso + Donado–Holmberg)
- **Principal evidencia:** Gastronomía Urquiza en circuitos oficiales
- **Principal debilidad:** Riesgo de colapsar en DoHo

## 2. Nombres y alcance

| Campo | Valor |
|---|---|
| nombre_canonico_propuesto | Villa Urquiza |
| nombres_alternativos | Urquiza |
| nombres_comerciales | polo gastronómico de Villa Urquiza (prensa) |
| nombres_historicos | Villa Urquiza |
| barrios_involucrados | Villa Urquiza |
| comunas | Comuna 12 |
| calles_referencia | Av. Triunvirato; Av. Congreso; Donado–Holmberg (subzona); posibles otros ejes |
| nodos_referencia | Plaza; estaciones de subte/tren del barrio; corredor DoHo como componente |
| ambiguedades | Barrio ≠ corredor DoHo; fragmentación probable entre ejes |
| nombre_recomendado_para_analisis | Villa Urquiza (multieje) |
| nombre_recomendado_para_comunicacion | Villa Urquiza |

*Observaciones de normalización:* Separar de DoHo y de García del Río/Saavedra en análisis y comunicación.

## 3. Antecedentes

La zona forma parte del universo semilla de polos candidatos del proyecto Polos Gastro (PDF semilla / fases 1–5). No está entre los polos con corrida territorial V3 adoptada (Belgrano, Recoleta, Costanera Norte). Esta expansión V4 la trata como **candidata documental**, no adoptada.

## 4. Evidencia oficial

Ver matriz de evidencia y fuentes con nivel OFICIAL_PRIMARIA asociadas a esta zona.

- **SRC008** — Circuito Sin Pausa | Gastronomía en Villa Urquiza (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa
- **SRC009** — Oferta y Establecimientos Gastronómicos (BA Data / GCBA). https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos

## 5. Evidencia institucional / sectorial / académica

Se priorizaron fuentes oficiales y periodísticas confiables. La referencia académica SRC024 (Troncoso 2020) aporta marco: la folletería GCBA 2015 listaba seis polos clásicos; las candidatas de expansión no estaban en esa lista corta.

## 6. Evidencia periodística

Ver fuentes PERIODISTICA_CONFIABLE en la matriz de fuentes.
- **SRC019** — El barrio porteño que más crece en 2025 y ya es furor (circuito gourmet) (2025-06-26). https://www.clarin.com/informacion-general/barrio-porteno-crece-2025-furor-treintaneros-circuito-gourmet_0_DtD7d8uTnJ.html

## 7. Calles y nodos mencionados

- Calles: Av. Triunvirato; Av. Congreso; Donado–Holmberg (subzona); posibles otros ejes
- Nodos: Plaza; estaciones de subte/tren del barrio; corredor DoHo como componente

## 8. Hipótesis de forma territorial

**Hipótesis (no decisión):** Multieje (Triunvirato/Congreso + Donado–Holmberg). Debe contrastarse con evidencia espacial; no dibujar polígono desde este expediente.

## 9. Relación con zonas vecinas

- **DoHo ↔ Villa Urquiza** (parte_todo; severidad ALTA): DoHo es corredor dentro de Urquiza, no el barrio. → IDs separados; no etiquetar todo Urquiza como DoHo.
- **Villa Urquiza ↔ Parque Saavedra / García del Río** (vecindad; severidad MEDIA): Barrios vecinos con formas distintas (multieje vs corredor). → Analizar juntas bordes; no un solo nombre.

## 10. Evidencia a favor

- [MEDIA] Existe mención oficial de gastronomía en Villa Urquiza asociada a un conjunto de calles, no a un único nombre de polo. (`EV-Z10-001`, SRC008)
- [BAJA] Prensa 2025 habla de crecimiento y circuito gourmet en el barrio (Villa Urquiza en el relato mediático). (`EV-Z10-002`, SRC019)

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

- Además de Donado–Holmberg, ¿Triunvirato/Congreso u otros ejes forman clusters?
- ¿El barrio es un solo cluster o varios?

## 15. Recomendación documental provisional

**Correr barrio y corredor DoHo con IDs distintos.**

Prioridad Places: `ALTA` · Prioridad clustering: `ALTA`

No declarar zona adoptada. Separar: (1) evidencia documental, (2) inferencia, (3) hipótesis territorial, (4) decisión institucional futura.

## 16. Fuentes

- `SRC008` | OFICIAL_PRIMARIA | Circuito Sin Pausa | Gastronomía en Villa Urquiza | https://turismo.buenosaires.gob.ar/es/24-48-72/sinpausa
- `SRC009` | OFICIAL_PRIMARIA | Oferta y Establecimientos Gastronómicos | https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- `SRC019` | PERIODISTICA_CONFIABLE | El barrio porteño que más crece en 2025 y ya es furor (circuito gourmet) | https://www.clarin.com/informacion-general/barrio-porteno-crece-2025-furor-treintaneros-circuito-gourmet_0_DtD7d8uTnJ.html
- `SRC024` | ACADEMICA | Geografía del consumo gastronómico en Buenos Aires | https://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1852-42652020000200005

---

*Paquete: docs/polos_gastro/evidencia_documental_expansion_v4/*
