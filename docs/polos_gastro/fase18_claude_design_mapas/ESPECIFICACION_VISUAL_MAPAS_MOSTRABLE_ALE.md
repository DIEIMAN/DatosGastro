# Especificación visual — Mapas de detalle, versión mostrable para Ale

**DGDGAS — Dirección General de Gastronomía**
Fase 18 — Especificación derivada de la referencia de Claude Design.
Documento de criterio, no de ejecución. No ejecuta API, no genera PDF, no genera mapas, no toca datos
fuente. No commit / no push / no staging.

Esta especificación define **cómo deben verse** los mapas de la versión mostrable (V5). Se apoya en el
sistema visual de la referencia `inputs/DGDGAS_mapas_detalle_claude_design_v1.html` y en las geometrías y
datos ya trabajados en V3/V4. **No introduce datos nuevos.**

Lenguaje obligatorio en todos los mapas: **"subzona aproximada"**, **"área de lectura"**, **"eje
aproximado"**. Nota fija por página: **"Referencia territorial — no delimita oficialmente polos"**.

---

## 0. Sistema visual común a los cinco mapas

Un mismo lenguaje para todas las páginas de detalle.

**Jerarquía visual (del fondo al frente):**
1. Fondo `#FAFBFC` + grilla de calles **tenue, rotada al ángulo del barrio** (da sensación de trama real).
2. Agua y avenidas nombradas — soporte, **nunca** protagonistas.
3. Áreas de subzona coloreadas — **protagonistas**.
4. Etiquetas grandes de subzona + tag "aproximada".
5. Hitos (rombo navy) — al final, máximo 2–3 por mapa, siempre con etiqueta.

**Estado codificado por el borde:**
- Borde **sólido** (~1.9 px) → subzona **consolidada**.
- Borde **discontinuo** (~1.5 px, dash 4 3) → **a reforzar / a validar**.
- **Punteado tenue**, sin relleno → **contexto** (no protagonista).

**Colores y opacidades (paleta institucional DGDGAS):**
- Navy marca / hito: `#1F3B57`. Verde: `#2F6E5B`. Azul: `#2C7FB8`. Cobre (ejes): `#C0762B`.
  Slate (a reforzar): `#5E6B78`.
- Relleno consolidada: color @ **15–20%**. Relleno a reforzar: color @ **8–10%**.
- Grilla / avenidas / agua: `#E8EDF1` / `#D3DAE0` / `#E6EDF3`.

**Tipografía (tamaños sobre lienzo de referencia 720×560; escalar proporcionalmente):**
- Subzona principal: 20–23 px, peso 600.
- Subzona menor / a reforzar: 17–19 px, peso 500–600.
- Tag "aproximada": 8.5–9 px, mono.
- Hito: 12–13.5 px, peso 500–600.
- Avenida: 10–10.5 px, mono.

**Reglas de etiqueta:**
- Etiqueta dentro del área si el ancho lo permite; si no, colgar afuera con línea guía que termina en un
  punto sobre el área.
- Separación mínima entre etiquetas; dos etiquetas nunca se tocan.
- **Nunca puntos de locales sobre el mapa.** Los nombres van en la caja lateral. Sólo hitos urbanos como
  rombo.

**Decisiones de forma:**
- Fenómeno que sigue una avenida (Corrientes) o el río/diques (Puerto Madero): **banda longitudinal**, no
  polígono compacto.
- Documentación débil o sin recorte (Belgrano R, Bajo Belgrano, Abasto): **borde discontinuo, relleno
  suave, nunca borde sólido**.
- Contexto no protagonista: sólo contorno punteado tenue y etiqueta gris, sin relleno.
- **No usar elipses genéricas cuando se pueda usar polígono por calles/avenidas.** Si no hay precisión,
  usar área aproximada con nota clara.

**Fuentes:** usar fuentes locales o fallbacks ya validados (Arial/Calibri). **No** llamar Google Fonts por
red. **No** dejar visible ningún texto de proceso ("borrador de diseño", "reglas para Codex", "fecha de
corte", nombres de archivo, etc.).

---

## 1. Mapa global (página 5)

- **Conservar** el mapa global de los 22 polos/ejes. Es la lectura principal del universo.
- **No rehacerlo.** Sólo ajustes menores de coherencia cromática con la paleta anterior si hiciera falta
  (misma navy, mismos grises).
- Mantiene su nota de lectura territorial y su rol de mapa institucional del universo semilla.

---

## 2. Mapas de detalle — criterio general

- Estilo editorial inspirado en Claude Design (sección 0).
- **Zonas coloreadas como protagonistas; callejero suave como soporte.**
- Etiquetas grandes y limpias.
- Puntos de locales **secundarios o directamente omitidos**; menciones destacadas en **caja lateral**.
- **No elipses genéricas** cuando haya avenidas para trazar el polígono. Sin precisión → área aproximada
  con nota.
- Caja lateral con sub-bloque separado **"a validar"** y su nota de confirmación documental.

Menciones por zona: exactamente las ya definidas en el Markdown base V4 (`INFORME_..._PDF_BASE_V4.md`,
sección 5). No agregar ni quitar nombres.

---

## 3. Palermo / Las Cañitas

**Etiquetas principales (borde sólido, protagonistas):** Palermo Soho, Palermo Hollywood, Las Cañitas.

**Delimitaciones aproximadas de trabajo (para trazar polígonos por avenidas, no elipses):**
- **Palermo Soho:** Av. Santa Fe, Av. Scalabrini Ortiz, Av. Córdoba, Av. Juan B. Justo.
- **Palermo Hollywood:** Av. Juan B. Justo, Av. Santa Fe, Av. Dorrego, Av. Córdoba.
- **Las Cañitas:** área aproximada Báez / Luis María Campos / Libertador / Ortega y Gasset o Chenaut
  (bolsón propio).

**Avenidas nombradas de soporte:** Av. Juan B. Justo (separa Soho de Hollywood), Av. Santa Fe, Av. del
Libertador.

**Contexto (punteado tenue, sin relleno, o se omite si ensucia):** Palermo Chico, Palermo Botánico/Nuevo.
**No sobrecargar** con estas si compiten con las tres subzonas principales.

**Caja lateral (menciones):** Don Julio, La Cabrera, Niño Gordo, Gran Dabbang, Mishiguene, La Mar, Cosi Mi
Piace; Las Cañitas: Campo Bravo, Kansas, SushiClub. Café Registrado con cautela como en V4.

**No** poner menciones en el mapa; van en la caja lateral.

---

## 4. Puerto Madero

- **Lectura longitudinal, no de manchas.** Eje costero de norte a sur pegado a los diques y al río.
- **Formas longitudinales** (banda), no manchas redondas.
- Elementos de soporte: **Río de la Plata**, **diques/basins**, **Av. A. Moreau de Justo** (spine).
- **Eje costero — Diques**: sector aproximado (subzona longitudinal).
- **Faena / El Mercado**: como **hito** (rombo) o área acotada, no como punto de restaurante.
- **Dársena Sur**: **área a validar** (borde discontinuo).
- **Caja lateral:** Happening, Sottovoce, El Mercado / Faena, Le Grill; sub-bloque a validar: Cabaña Las
  Lilas, La Parolaccia Casa Tua, Red Resto & Lounge, Patagonia Sur (requieren confirmación de vigencia).

---

## 5. San Telmo

- Lectura **patrimonial y barrial**.
- **Calle Defensa** como columna (eje) del casco.
- **Mercado de San Telmo** como **hito colectivo** (rombo), no restaurante puntual.
- **Plaza Dorrego** como hito.
- **Casco histórico / entorno Defensa** como **área de lectura** aproximada.
- **Entorno gastronómico próximo** como área cercana aproximada.
- Soporte: Av. San Juan, Av. Paseo Colón.
- **Evitar círculos genéricos**; usar áreas apoyadas en Defensa y el casco.
- **Caja lateral:** La Brigada, Café San Juan, Hierbabuena; sub-bloque hitos y a validar: Mercado de San
  Telmo, El Preferido de San Telmo, Pulpería Quilapán, Napoles.

---

## 6. Corrientes / Abasto

Dos lecturas distintas, **vinculadas pero no fusionadas**. Evitar doble conteo.

**Corrientes:**
- **Eje lineal** teatral-gastronómico entre **9 de Julio y Callao** (banda longitudinal, no polígono
  compacto).
- Soporte: banda 9 de Julio, Av. Callao (cross).
- Hito: **Obelisco / teatros** (nodo).
- Etiqueta: "Eje teatral-gastronómico — aprox.".

**Abasto:**
- **Área separada** a reforzar en torno al shopping, **radio aproximado ~5 cuadras**.
- Borde **discontinuo** ("Área a reforzar").
- Hito: Abasto Shopping.
- **No fusionar con Corrientes.** Indicar explícitamente **"vínculo — no continuidad"**.

**Etiquetas claras y separadas** para cada uno.

**Caja lateral:** Corrientes: Las Cuartetas, El Palacio de la Pizza, Pertutti; a validar/hito: Güerrín,
Moulin Bleu. Nota de Abasto: área a reforzar documentalmente, mostrada separada del eje Corrientes;
conviene validar su recorte antes de tratarla como polo propio.

---

## 7. Belgrano

Jerarquía visible entre subzonas de respaldo desigual.

- **Barrio Chino:** subzona con **identidad más clara** → borde **sólido**. Hito: Arco del Barrio Chino.
  Etiqueta "Identidad clara — aprox.". **Es la subzona más fuerte.**
- **Belgrano R:** **subzona a reforzar** → borde **discontinuo**. **No sobredimensionar**; sin evidencia
  de polo consolidado, se muestra a reforzar hasta contar con más documentación.
- **Bajo Belgrano:** **área a revisar** → borde **discontinuo**.
- Soporte: Av. Cabildo, Av. Juramento, FFCC Mitre.
- **Caja lateral:** Barrio Chino: Hong Kong Style, China Rose; a validar: Ichisou, Ramen Neko, Ichiban,
  BAO Kitchen, Tori Tori.

---

## 8. Cautelas que deben quedar visibles (todas las páginas)

- Nota fija: **"Referencia territorial — no delimita oficialmente polos"**.
- Lenguaje **"subzona aproximada / área de lectura / eje aproximado"** en etiquetas y bajadas.
- Menciones = universo semilla, **no ranking ni padrón operativo**; "no constituye ranking ni listado
  exhaustivo".
- Cerrados / vigencia no confirmada: **fuera** del mapa público.
- Duplicados: una sola sede; **no** repetir.
- **Sin** campos técnicos ni sensibles (place_id, rating, user_ratings_total, API key, raw JSON, rutas,
  scripts, CSV internos) en ninguna parte visible. **Sin** marca DataGastro. Sin capturas de Google Maps.

---

## 9. Resumen de qué cambia respecto de V4

| Zona | Cambio principal |
|---|---|
| Global | Se conserva; ajustes menores de coherencia cromática. |
| Palermo | Elipses → polígonos por avenidas; contexto tenue o omitido; 3 etiquetas fuertes. |
| Puerto Madero | Manchas → banda longitudinal de diques; Faena como hito; Dársena Sur a validar. |
| San Telmo | Círculos → área sobre eje Defensa; Mercado y Plaza Dorrego como hitos. |
| Corrientes/Abasto | Corrientes banda lineal; Abasto área discontinua separada; "vínculo, no continuidad". |
| Belgrano | Jerarquía por borde: Barrio Chino sólido, Belgrano R y Bajo Belgrano discontinuos. |

Todo lo demás (mapa global, cajas laterales, callejero GCBA, estructura de 18 páginas, pie institucional)
**se conserva**.
