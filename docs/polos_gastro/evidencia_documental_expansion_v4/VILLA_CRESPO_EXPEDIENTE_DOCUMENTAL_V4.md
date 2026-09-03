# Expediente documental — Villa Crespo

**zona_id:** Z01  
**Fecha de consulta:** 2026-07-12  
**Rol:** investigador_documental_externo (+ red_team_documental)  
**Línea:** evidencia_documental_expansion_v4  
**Regla:** la evidencia interpreta y contextualiza; **no** supervisa clustering ni decide polígonos.

## 1. Resumen ejecutivo

Villa Crespo cuenta con **denominación oficial** de 'Polo gastronómico' en Turismo BA, con ejes Thames, Gurruchaga y Velazco, y con cobertura periodística reciente (2025) que la presenta como destino turístico-gastronómico. El principal riesgo es la **absorción narrativa por Palermo** vía Thames y etiquetas de frontera.

- **Estado documental provisional:** `IDENTIDAD_DOCUMENTAL_FUERTE`
- **Forma sugerida (documental, no geométrica):** Multi-eje / núcleos (Thames, Gurruchaga, Velazco, Mercat)
- **Principal evidencia:** Turismo BA 'Polo gastronómico Villa Crespo'
- **Principal debilidad:** Riesgo de absorción por Palermo; sin polígono

## 2. Nombres y alcance

| Campo | Valor |
|---|---|
| nombre_canonico_propuesto | Villa Crespo |
| nombres_alternativos | VC; barrio Villa Crespo |
| nombres_comerciales | Chacacrespo (prensa/barrial, frontera con Chacarita); polo gastronómico Villa Crespo (Turismo BA) |
| nombres_historicos | Villa Crespo (barrio desde fines s. XIX) |
| barrios_involucrados | Villa Crespo; borde con Palermo y Chacarita |
| comunas | Comuna 15 |
| calles_referencia | Thames; Gurruchaga; Velazco; Castillo; Aguirre; Murillo; Serrano (borde Palermo) |
| nodos_referencia | Mercat Villa Crespo (Thames 747); Plaza Gurruchaga; Convento San José; Movistar Arena (borde) |
| ambiguedades | Riesgo de absorción narrativa por Palermo vía calle Thames; Chacacrespo es etiqueta no institucional |
| nombre_recomendado_para_analisis | Villa Crespo |
| nombre_recomendado_para_comunicacion | Villa Crespo |

*Observaciones de normalización:* Turismo BA usa 'Polo gastronómico Villa Crespo'. No adoptar Chacacrespo como nombre institucional.

## 3. Antecedentes

La zona forma parte del universo semilla de polos candidatos del proyecto Polos Gastro (PDF semilla / fases 1–5). No está entre los polos con corrida territorial V3 adoptada (Belgrano, Recoleta, Costanera Norte). Esta expansión V4 la trata como **candidata documental**, no adoptada.

## 4. Evidencia oficial

La página 'Polo gastronómico Villa Crespo' es la evidencia oficial más directa de la expansión V4 junto con Chacarita. No define polígono; lista locales y calles. Mercat Villa Crespo aparece como establecimiento. Circuitos de barrios y Bus Turístico (prensa) refuerzan centralidad de Thames.

- **SRC001** — Polo gastronómico Villa Crespo (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/article/polo-gastron%C3%B3mico-villa-crespo
- **SRC003** — Turismo en Barrios | Circuitos al aire libre (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/turismo-en-barrios
- **SRC004** — Circuito Tradicional | 24, 48 y 72 horas (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/24-48-72/tradicional
- **SRC005** — Mercat Villa Crespo (Turismo Buenos Aires / GCBA). https://turismo.buenosaires.gob.ar/es/otros-establecimientos/mercat-villa-crespo
- **SRC009** — Oferta y Establecimientos Gastronómicos (BA Data / GCBA). https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos

## 5. Evidencia institucional / sectorial / académica

Se priorizaron fuentes oficiales y periodísticas confiables. La referencia académica SRC024 (Troncoso 2020) aporta marco: la folletería GCBA 2015 listaba seis polos clásicos; las candidatas de expansión no estaban en esa lista corta.

## 6. Evidencia periodística

LA NACION 2025 consolida el relato de polo turístico-gastronómico, Mercat, parada de bus en Thames y Movistar Arena en el borde. Notas auxiliares describen Thames como corredor Palermo–Crespo.
- **SRC011** — El mapa de Villa Crespo: el barrio que se transformó en el nuevo polo turístico y gastronómico (2025-04-15/22). https://www.lanacion.com.ar/que-sale/el-mapa-de-villa-crespo-el-barrio-que-se-transformo-en-el-nuevo-polo-turistico-y-gastronomico-nid15042025/
- **SRC013** — Chacalermo, cómo es el nuevo epicentro gastronómico de moda en Buenos Aires (2023-08-19). https://www.infobae.com/tendencias/2023/08/19/chacalermo-como-es-el-nuevo-epicentro-gastronomico-de-moda-en-buenos-aires/

## 7. Calles y nodos mencionados

- Calles: Thames; Gurruchaga; Velazco; Castillo; Aguirre; Murillo; Serrano (borde Palermo)
- Nodos: Mercat Villa Crespo (Thames 747); Plaza Gurruchaga; Convento San José; Movistar Arena (borde)

## 8. Hipótesis de forma territorial

**Hipótesis:** multi-eje / multi-núcleo (Thames + Gurruchaga/Velazco + Mercat), con borde poroso hacia Palermo. No asumir un rectángulo de barrio.

## 9. Relación con zonas vecinas

- **Villa Crespo ↔ Palermo** (borde_competencia_narrativa; severidad ALTA): Thames documentada como corredor que conecta Palermo y Villa Crespo; riesgo de absorción por Palermo. → No unir clusters Palermo-Crespo sin justificación; reportar borde.
- **Villa Crespo ↔ Chacarita** (borde_y_nodo_compartido; severidad MEDIA): Arena y etiquetas Chacacrespo; frontera porosa. → Correr juntas con IDs distintos; no fusionar nombres.
- **Paternal ↔ Villa Crespo** (borde_micro_polo; severidad MEDIA): Prensa describe micro-polo de borde. → Evaluar si el borde es propio o spillover de Crespo.

## 10. Evidencia a favor

- [ALTA] Turismo BA denomina 'Polo gastronómico Villa Crespo' y describe mezcla de tradicional y vanguardia. (`EV-Z01-001`, SRC001)
- [ALTA] Thames es destacada (Time Out) y se mencionan Gurruchaga y Velazco como ejes de propuestas. (`EV-Z01-002`, SRC001)
- [MEDIA] Prensa 2025 presenta Villa Crespo como polo turístico-gastronómico consolidado, con Mercat y parada de Bus Turístico en Thames. (`EV-Z01-003`, SRC011)
- [MEDIA] Fuentes auxiliares describen Thames como corredor que conecta Palermo y Villa Crespo. (`EV-Z01-004`, SRC023)

## 11. Contraindicadores

- Ver objeciones y red team; ausencia de contraindicio explícito no implica ausencia de riesgo.

## 12. Vacíos documentales

- Documento de planeamiento o Comuna 15 que delimite el polo.
- Fecha de inicio institucional del uso 'polo' en Turismo BA.
- Conteos de oferta por eje.

## 13. Riesgos de sobreinterpretación

- Convertir 'polo' de turismo o prensa en límite municipal.
- Usar un patio/mercado o un local famoso como proxy de zona.
- Adoptar nombres comerciales (DoHo, Chacalermo, Nuevo Bajo) sin glosa.
- Supervisar el clustering con esta narrativa.

## 14. Preguntas para la corrida espacial

- ¿Thames se comporta como corredor continuo hacia Palermo o se interrumpe?
- ¿Gurruchaga y Velazco forman núcleos distintos del de Thames?
- ¿Mercat es un outlier puntual o ancla de un cluster?
- ¿Qué densidad hay lejos de estos ejes (falso positivo de 'todo el barrio')?

## 15. Recomendación documental provisional

**Correr con buffer que distinga Palermo Soho/Hollywood; no imponer un solo polígono.**

Prioridad Places: `MUY_ALTA` · Prioridad clustering: `MUY_ALTA`

No declarar zona adoptada. Separar: (1) evidencia documental, (2) inferencia, (3) hipótesis territorial, (4) decisión institucional futura.

## 16. Fuentes

- `SRC001` | OFICIAL_PRIMARIA | Polo gastronómico Villa Crespo | https://turismo.buenosaires.gob.ar/es/article/polo-gastron%C3%B3mico-villa-crespo
- `SRC003` | OFICIAL_PRIMARIA | Turismo en Barrios | Circuitos al aire libre | https://turismo.buenosaires.gob.ar/es/turismo-en-barrios
- `SRC004` | OFICIAL_PRIMARIA | Circuito Tradicional | 24, 48 y 72 horas | https://turismo.buenosaires.gob.ar/es/24-48-72/tradicional
- `SRC005` | OFICIAL_PRIMARIA | Mercat Villa Crespo | https://turismo.buenosaires.gob.ar/es/otros-establecimientos/mercat-villa-crespo
- `SRC009` | OFICIAL_PRIMARIA | Oferta y Establecimientos Gastronómicos | https://data.buenosaires.gob.ar/dataset/oferta-establecimientos-gastronomicos
- `SRC011` | PERIODISTICA_CONFIABLE | El mapa de Villa Crespo: el barrio que se transformó en el nuevo polo turístico y gastronómico | https://www.lanacion.com.ar/que-sale/el-mapa-de-villa-crespo-el-barrio-que-se-transformo-en-el-nuevo-polo-turistico-y-gastronomico-nid15042025/
- `SRC013` | PERIODISTICA_CONFIABLE | Chacalermo, cómo es el nuevo epicentro gastronómico de moda en Buenos Aires | https://www.infobae.com/tendencias/2023/08/19/chacalermo-como-es-el-nuevo-epicentro-gastronomico-de-moda-en-buenos-aires/
- `SRC023` | AUXILIAR | Thames: el corredor gastronómico que reinventa Palermo y Villa Crespo | https://agroempresario.com/publicacion/99906/thames-el-corredor-gastronomico-que-reinventa-palermo-y-villa-crespo/
- `SRC024` | ACADEMICA | Geografía del consumo gastronómico en Buenos Aires | https://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1852-42652020000200005
- `SRC028` | AUXILIAR | Mercat Villa Crespo (sitio propio) | https://mercatmercado.com/

---

*Paquete: docs/polos_gastro/evidencia_documental_expansion_v4/*
