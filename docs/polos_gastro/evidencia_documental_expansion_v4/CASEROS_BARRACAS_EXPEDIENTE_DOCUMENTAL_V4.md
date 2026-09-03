# Expediente documental — Avenida Caseros — Barracas

**zona_id:** Z04  
**Fecha de consulta:** 2026-07-12  
**Rol:** investigador_documental_externo (+ red_team_documental)  
**Línea:** evidencia_documental_expansion_v4  
**Regla:** la evidencia interpreta y contextualiza; **no** supervisa clustering ni decide polígonos.

## 1. Resumen ejecutivo

El objeto documentado es el **Boulevard Caseros** (tramo corto Defensa–Bolívar junto a Parque Lezama), denominado polo por Turismo BA y por prensa desde 2017. La etiqueta semilla 'Barracas' es **demasiado amplia**; el oficial lo asocia a San Telmo.

- **Estado documental provisional:** `CORREDOR_DOCUMENTADO`
- **Forma sugerida (documental, no geométrica):** Corredor corto Defensa–Bolívar (Boulevard Caseros)
- **Principal evidencia:** Turismo BA Circuito Tradicional
- **Principal debilidad:** Nombre semilla 'Barracas' demasiado amplio

## 2. Nombres y alcance

| Campo | Valor |
|---|---|
| nombre_canonico_propuesto | Boulevard / Avenida Caseros (tramo San Telmo–Barracas) |
| nombres_alternativos | Boulevard Caseros; Av. Caseros; Polo Caseros |
| nombres_comerciales | Boulevard Caseros; polo gastronómico Caseros |
| nombres_historicos | Avenida Caseros |
| barrios_involucrados | Barracas; San Telmo (límite); no equivale a Parque Patricios |
| comunas | Comuna 4 (Barracas); Comuna 1 (San Telmo en el tramo documentado) |
| calles_referencia | Av. Caseros entre Defensa y Bolívar (tramo oficial Turismo BA); posible extensión a lo largo del boulevard |
| nodos_referencia | Parque Lezama; Museo Histórico Nacional; cruce Defensa/Bolívar |
| ambiguedades | Nombre semilla 'Caseros/Barracas' puede sugerir todo Barracas o Parque Patricios; evidencia fuerte es tramo acotado |
| nombre_recomendado_para_analisis | Boulevard Caseros (tramo Parque Lezama) |
| nombre_recomendado_para_comunicacion | Boulevard Caseros |

*Observaciones de normalización:* Turismo BA lo asocia a San Telmo (Defensa–Bolívar). No usar 'Polo Caseros' como sinónimo de barrio completo.

## 3. Antecedentes

La zona forma parte del universo semilla de polos candidatos del proyecto Polos Gastro (PDF semilla / fases 1–5). No está entre los polos con corrida territorial V3 adoptada (Belgrano, Recoleta, Costanera Norte). Esta expansión V4 la trata como **candidata documental**, no adoptada.

## 4. Evidencia oficial

Ver matriz de evidencia y fuentes con nivel OFICIAL_PRIMARIA asociadas a esta zona.

- **SRC003** — Turismo en Barrios | Circuitos al aire libre (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/turismo-en-barrios
- **SRC004** — Circuito Tradicional | 24, 48 y 72 horas (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/24-48-72/tradicional
- **SRC009** — Oferta y Establecimientos Gastronómicos (BA Data / GCBA). https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- **SRC031** — Smart Plaza Patio Parque Patricios (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/otros-establecimientos/smart-plaza-patio-parque-patricios

## 5. Evidencia institucional / sectorial / académica

Se priorizaron fuentes oficiales y periodísticas confiables. La referencia académica SRC024 (Troncoso 2020) aporta marco: la folletería GCBA 2015 listaba seis polos clásicos; las candidatas de expansión no estaban en esa lista corta.

## 6. Evidencia periodística

Ver fuentes PERIODISTICA_CONFIABLE en la matriz de fuentes.
- **SRC014** — Boulevard Caseros: 15 restaurantes y cafés para conocer en el límite de San Telmo y Barracas (2022-09-08). https://www.clarin.com/gourmet/boulevard-caseros-15-restaurantes-cafes-conocer-limite-san-telmo-barracas_0_cySLDukUbr.html
- **SRC015** — Avenida Caseros: los mejores restaurantes del nuevo polo gastronómico porteño (2017-01-12). https://www.lanacion.com.ar/sociedad/avenida-caseros-los-mejores-restaurantes-del-nuevo-polo-gastronomico-porteno-nid1974368/

## 7. Calles y nodos mencionados

- Calles: Av. Caseros entre Defensa y Bolívar (tramo oficial Turismo BA); posible extensión a lo largo del boulevard
- Nodos: Parque Lezama; Museo Histórico Nacional; cruce Defensa/Bolívar

## 8. Hipótesis de forma territorial

**Hipótesis (no decisión):** Corredor corto Defensa–Bolívar (Boulevard Caseros). Debe contrastarse con evidencia espacial; no dibujar polígono desde este expediente.

## 9. Relación con zonas vecinas

- Ver `MATRIZ_RELACIONES_Y_CONFLICTOS_TERRITORIALES_V4.csv`.

## 10. Evidencia a favor

- [ALTA] Turismo BA identifica Boulevard Caseros como tramo de Av. Caseros transformado en polo gastronómico entre Defensa y Bolívar. (`EV-Z04-001`, SRC004)
- [MEDIA] Desde 2017 la prensa ya hablaba de 'nuevo polo' en una sola cuadra Caseros entre Defensa y Bolívar. (`EV-Z04-002`, SRC015)

## 11. Contraindicadores

- Smart Plaza Patio Parque Patricios es un patio gastronómico distinto, no evidencia del corredor Caseros–Barracas. (`EV-Z04-003`)

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

- ¿El cluster se limita a 1–3 cuadras del tramo Defensa–Bolívar?
- ¿Hay extensión medible del boulevard más allá del tramo oficial?
- ¿Hay confusión de puntos con Parque Patricios o San Telmo casco?

## 15. Recomendación documental provisional

**Acotar consulta al tramo documentado; revalidar extensión.**

Prioridad Places: `ALTA` · Prioridad clustering: `ALTA`

No declarar zona adoptada. Separar: (1) evidencia documental, (2) inferencia, (3) hipótesis territorial, (4) decisión institucional futura.

## 16. Fuentes

- `SRC003` | OFICIAL_PRIMARIA | Turismo en Barrios | Circuitos al aire libre | https://turismo.buenosaires.gob.ar/es/turismo-en-barrios
- `SRC004` | OFICIAL_PRIMARIA | Circuito Tradicional | 24, 48 y 72 horas | https://turismo.buenosaires.gob.ar/es/24-48-72/tradicional
- `SRC009` | OFICIAL_PRIMARIA | Oferta y Establecimientos Gastronómicos | https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- `SRC014` | PERIODISTICA_CONFIABLE | Boulevard Caseros: 15 restaurantes y cafés para conocer en el límite de San Telmo y Barracas | https://www.clarin.com/gourmet/boulevard-caseros-15-restaurantes-cafes-conocer-limite-san-telmo-barracas_0_cySLDukUbr.html
- `SRC015` | PERIODISTICA_CONFIABLE | Avenida Caseros: los mejores restaurantes del nuevo polo gastronómico porteño | https://www.lanacion.com.ar/sociedad/avenida-caseros-los-mejores-restaurantes-del-nuevo-polo-gastronomico-porteno-nid1974368/
- `SRC024` | ACADEMICA | Geografía del consumo gastronómico en Buenos Aires | https://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1852-42652020000200005
- `SRC031` | OFICIAL_PRIMARIA | Smart Plaza Patio Parque Patricios | https://turismo.buenosaires.gob.ar/es/otros-establecimientos/smart-plaza-patio-parque-patricios

---

*Paquete: docs/polos_gastro/evidencia_documental_expansion_v4/*
