# Expediente documental — Parque Saavedra — Avenida García del Río

**zona_id:** Z13  
**Fecha de consulta:** 2026-07-12  
**Rol:** investigador_documental_externo (+ red_team_documental)  
**Línea:** evidencia_documental_expansion_v4  
**Regla:** la evidencia interpreta y contextualiza; **no** supervisa clustering ni decide polígonos.

## 1. Resumen ejecutivo

García del Río (Saavedra) es un **corredor periodísticamente bien documentado** (2024) entre Cabildo y Parque Saavedra, con obras de espacio público en 2026. Falta denominación oficial 'polo', pero la forma de tramo es clara.

- **Estado documental provisional:** `CORREDOR_DOCUMENTADO`
- **Forma sugerida (documental, no geométrica):** Corredor bulevar García del Río
- **Principal evidencia:** Clarín 2024
- **Principal debilidad:** Poca fuente oficial que diga 'polo'

## 2. Nombres y alcance

| Campo | Valor |
|---|---|
| nombre_canonico_propuesto | Bulevar / Avenida García del Río (Saavedra) |
| nombres_alternativos | Parque Saavedra; Bulevar García del Río; García del Río |
| nombres_comerciales | polo gastronómico García del Río (prensa) |
| nombres_historicos | Av. García del Río (sobre arroyo Medrano entubado) |
| barrios_involucrados | Saavedra; borde Núñez / Villa Urquiza / Coghlan |
| comunas | Comuna 12 |
| calles_referencia | Av. García del Río entre Cabildo y Parque Saavedra; cruces Crámer, Conesa, Vidal, Moldes, Zapiola |
| nodos_referencia | Parque Saavedra; bulevar verde de García del Río |
| ambiguedades | Parque Saavedra (espacio verde) ≠ corredor gastronómico; no fusionar con DoHo ni todo Urquiza |
| nombre_recomendado_para_analisis | García del Río (Saavedra) |
| nombre_recomendado_para_comunicacion | Bulevar García del Río (Saavedra) |

*Observaciones de normalización:* Clarín 2024 documenta corredor/polo periodístico. Obras de repavimentación 2026 en prensa barrial.

## 3. Antecedentes

La zona forma parte del universo semilla de polos candidatos del proyecto Polos Gastro (PDF semilla / fases 1–5). No está entre los polos con corrida territorial V3 adoptada (Belgrano, Recoleta, Costanera Norte). Esta expansión V4 la trata como **candidata documental**, no adoptada.

## 4. Evidencia oficial

Ver matriz de evidencia y fuentes con nivel OFICIAL_PRIMARIA asociadas a esta zona.

- **SRC009** — Oferta y Establecimientos Gastronómicos (BA Data / GCBA). https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos

## 5. Evidencia institucional / sectorial / académica

Se priorizaron fuentes oficiales y periodísticas confiables. La referencia académica SRC024 (Troncoso 2020) aporta marco: la folletería GCBA 2015 listaba seis polos clásicos; las candidatas de expansión no estaban en esa lista corta.

## 6. Evidencia periodística

Ver fuentes PERIODISTICA_CONFIABLE en la matriz de fuentes.
- **SRC016** — Bulevar García del Río: bares y restaurantes del polo gastronómico que renovó Saavedra (2024-06-01). https://www.clarin.com/gourmet/bulevar-garcia-rio-bares-restaurantes-polo-gastronomico-renovo-barrio-saavedra_0_ZMgU1ouriY.html
- **SRC026** — Comienza la repavimentación del bulevar García del Río (2026-01-09). https://www.saavedraonline.com.ar/comienza-la-repavimentacion-de-garcia-del-rio-entre-cabildo-y-el-parque-saavedra/

## 7. Calles y nodos mencionados

- Calles: Av. García del Río entre Cabildo y Parque Saavedra; cruces Crámer, Conesa, Vidal, Moldes, Zapiola
- Nodos: Parque Saavedra; bulevar verde de García del Río

## 8. Hipótesis de forma territorial

**Hipótesis (no decisión):** Corredor bulevar García del Río. Debe contrastarse con evidencia espacial; no dibujar polígono desde este expediente.

## 9. Relación con zonas vecinas

- **Villa Urquiza ↔ Parque Saavedra / García del Río** (vecindad; severidad MEDIA): Barrios vecinos con formas distintas (multieje vs corredor). → Analizar juntas bordes; no un solo nombre.

## 10. Evidencia a favor

- [ALTA] Clarín 2024 documenta el bulevar García del Río (Cabildo–Parque Saavedra) como polo/corredor gastronómico de Saavedra. (`EV-Z13-001`, SRC016)

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

- ¿La densidad sigue el bulevar de forma lineal?
- ¿Hay spillover a calles transversales?
- ¿Se solapa espacialmente con DoHo? (no debería por distancia, verificar bordes)

## 15. Recomendación documental provisional

**Correr corredor lineal; separar de DoHo.**

Prioridad Places: `ALTA` · Prioridad clustering: `ALTA`

No declarar zona adoptada. Separar: (1) evidencia documental, (2) inferencia, (3) hipótesis territorial, (4) decisión institucional futura.

## 16. Fuentes

- `SRC009` | OFICIAL_PRIMARIA | Oferta y Establecimientos Gastronómicos | https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- `SRC016` | PERIODISTICA_CONFIABLE | Bulevar García del Río: bares y restaurantes del polo gastronómico que renovó Saavedra | https://www.clarin.com/gourmet/bulevar-garcia-rio-bares-restaurantes-polo-gastronomico-renovo-barrio-saavedra_0_ZMgU1ouriY.html
- `SRC024` | ACADEMICA | Geografía del consumo gastronómico en Buenos Aires | https://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1852-42652020000200005
- `SRC026` | PERIODISTICA_CONFIABLE | Comienza la repavimentación del bulevar García del Río | https://www.saavedraonline.com.ar/comienza-la-repavimentacion-de-garcia-del-rio-entre-cabildo-y-el-parque-saavedra/

---

*Paquete: docs/polos_gastro/evidencia_documental_expansion_v4/*
