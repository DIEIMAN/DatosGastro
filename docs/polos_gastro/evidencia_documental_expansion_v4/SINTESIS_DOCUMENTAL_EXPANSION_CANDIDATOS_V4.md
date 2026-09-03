# Síntesis documental — candidatos expansión V4

**Fecha:** 2026-07-12  
**Ámbito:** 15 zonas candidatas · sin adopción institucional

## 1. Panorama general

La expansión documental V4 encuentra un gradiente claro:

1. **Identidad oficial explícita de "polo gastronómico"** en Turismo BA: **Villa Crespo** y **Chacarita**.
2. **Corredores bien descritos** (oficial y/o prensa): **Boulevard Caseros** (tramo corto), **Donado–Holmberg (DoHo)**, **García del Río**.
3. **Zonas reconocidas sin forma única**: **Caballito**, **Villa Urquiza**, **Abasto**, **Devoto**.
4. **Familia centro** que **no** es una unidad: **Microcentro/Centro** + **Nuevo Bajo (Esmeralda–Paraguay)**.
5. **Evidencia débil o insuficiente**: **Boedo**, **Federico Lacroze** (como avenida completa), **Villa Pueyrredón**.
6. **Media con forma archipiélago**: **La Paternal** (prensa fuerte, oficial débil).

La folletería histórica de polos (academia sobre materiales GCBA 2015) listaba Palermo, Las Cañitas, Puerto Madero, Recoleta, San Telmo y Calle Corrientes. Las 15 candidatas **no** estaban en esa lista corta; su elevación requiere contraste espacial y decisión humana.

## 2. Ranking de fuerza documental (provisional)

| Rango | Zona | Estado |
|---|---|---|
| 1 | Villa Crespo | IDENTIDAD_DOCUMENTAL_FUERTE |
| 2 | Chacarita | IDENTIDAD_DOCUMENTAL_FUERTE |
| 3 | Boulevard Caseros (tramo) | CORREDOR_DOCUMENTADO |
| 4 | García del Río / Saavedra | CORREDOR_DOCUMENTADO |
| 5 | DoHo / Donado–Holmberg | CORREDOR_DOCUMENTADO |
| 6 | Caballito | ZONA_RECONOCIDA_SIN_FORMA_CLARA |
| 7 | Villa Urquiza | ZONA_RECONOCIDA_SIN_FORMA_CLARA |
| 8 | Abasto | ZONA_RECONOCIDA_SIN_FORMA_CLARA |
| 9 | Nuevo Bajo (Esmeralda–Paraguay) | NUCLEO_DOCUMENTADO |
| 10 | Centro/Microcentro (familia) | EVIDENCIA_CONTRADICTORIA (como unidad) |
| 11 | Villa Devoto | IDENTIDAD_DOCUMENTAL_MEDIA |
| 12 | La Paternal | IDENTIDAD_DOCUMENTAL_MEDIA |
| 13 | Avenida Boedo | IDENTIDAD_DOCUMENTAL_DEBIL |
| 14 | Federico Lacroze (avenida completa) | EVIDENCIA_INSUFICIENTE |
| 15 | Villa Pueyrredón / Av. San Martín | EVIDENCIA_INSUFICIENTE |

## 3. Zonas con respaldo fuerte

- **Villa Crespo** y **Chacarita**: páginas oficiales de polo + prensa reciente.
- **Boulevard Caseros (tramo Defensa–Bolívar)**: oficial en itinerario + prensa histórica convergente en el tramo.

## 4. Zonas con respaldo medio

- **García del Río**, **DoHo**, **Caballito**, **Urquiza**, **Abasto**, **Devoto**, **Paternal**, **núcleo Esmeralda–Paraguay**.

## 5. Zonas débiles

- **Boedo**, **Lacroze completa**, **Villa Pueyrredón**.
- **Centro como unidad única** (débil/contradictorio); subunidades pueden ser fuertes por separado.

## 6. Corredores mejor documentados

1. Jorge Newbery (Chacarita)  
2. Thames / multi-eje Villa Crespo  
3. Boulevard Caseros (corto)  
4. García del Río (Cabildo–Parque Saavedra)  
5. Donado–Holmberg  

## 7. Nombres problemáticos

| Nombre | Problema | Uso recomendado |
|---|---|---|
| DoHo | Marca comercial/inmobiliaria | Alias; preferir Donado–Holmberg |
| Chacalermo / Chacacrespo | Etiquetas de frontera | No institucionales |
| Nuevo Bajo | No oficial en circuitos | Esmeralda–Paraguay / Retiro |
| Bajo porteño | Ambiguo histórico | Evitar sin definición |
| Polo Caseros / Barracas | Infla el tramo y el barrio | Boulevard Caseros (tramo) |
| Microcentro = Centro | Falsa unidad | Subunidades |
| Parque Saavedra = García del Río | Parque ≠ corredor | Distinguir |

## 8. Conflictos territoriales principales

- Crespo ↔ Palermo (Thames)  
- Chacarita ↔ Palermo (Chacalermo)  
- Chacarita ↔ Lacroze  
- Caballito multinodo  
- Caseros ↔ San Telmo vs Barracas vs Patricios  
- Abasto ↔ Corrientes centro  
- DoHo ↔ Urquiza ↔ García del Río  
- Nuevo Bajo ↔ Microcentro ↔ Retiro  
- Paternal ↔ Crespo (triple frontera) / ≠ Distrito del Vino  

## 9. Prioridades

Ver `PRIORIZACION_DOCUMENTAL_PARA_CORRIDA_V4.csv`.

**Tanda 1 sugerida (documental):** Villa Crespo, Chacarita.  
**Tanda 2:** Caballito (por nodos), Caseros, DoHo+Urquiza, García del Río.  
**Tanda 3:** Subunidades Centro + Nuevo Bajo + Abasto.  
**Tanda 4–5:** Devoto, Paternal, Boedo, Lacroze tramos, Pueyrredón.

## 10. Recomendaciones Places

- Áreas de consulta ancladas en **calles/nodos documentados**, no en barrios enteros por defecto.
- Subunidades del Centro con bboxes separados.
- No usar lista semilla de locales como queries de validación de polo.

## 11. Recomendaciones clustering

- Hipótesis nula de **fragmentación** en Caballito, Urquiza, Paternal, Centro.
- Permitir **0 clusters** (Lacroze completa, Pueyrredón, Boedo).
- No etiquetar clusters con DoHo/Chacalermo/Nuevo Bajo sin decisión editorial.

## 12. Decisiones humanas futuras

1. ¿Adoptar nombre comunicacional "Villa Crespo" / "Chacarita" si el spatial confirma?  
2. ¿Cómo nombrar Caseros sin decir Barracas completa?  
3. ¿Qué subunidades del Centro entran a informe?  
4. ¿DoHo se comunica o solo Donado–Holmberg?  
5. ¿Paternal se presenta como circuito emergente o se archiva?  

**Ninguna de estas decisiones se toma en este paquete.**
