# Especificación de PDF limpio de 11 páginas — Oficina

**Proyecto:** PolosGastro — DGDGAS (Dirección General de Gastronomía)
**Fecha:** 3 de julio de 2026
**Base de partida:** fase19 (`INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_MOSTRABLE_ALE.md` y su PDF).
**Salida final esperada:** `outputs/polos_gastro/fase20_limpieza_mostrable_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA.pdf`

Documento de especificación editorial. **No ejecuta código, no genera PDF, no genera mapas,
no toca datos fuente.** Define exactamente cómo debe quedar la pieza de 11 páginas.

---

## 1. Reglas transversales (aplican a todas las páginas)

- **Marca visible única:** "DGDGAS — Dirección General de Gastronomía". Nunca "DataGastro".
- **Pie institucional:** "DGDGAS — Dirección General de Gastronomía" con raya larga (em dash
  `—`) si el sistema de render lo permite; si no, guion largo simple.
- **Numeración de pie:** formato "N / 11" en las once páginas (1/11 … 11/11). Sin totales
  heredados de fase19 ("/18").
- **Cero apariciones** de: "Ale", "validar con Ale", "validación interna", "versión mostrable",
  "versión final", "borrador", "preliminar", "prueba", "documento interno", "uso operativo".
- **Sin campos sensibles ni técnicos:** sin `place_id`, `rating`, `user_ratings_total`, API
  key, raw JSON, rutas locales, nombres de scripts, QA técnico ni nombres de CSV internos.
- **Sin capturas de Google Maps.** Los mapas son los editoriales ya existentes en fase19.
- **Lenguaje prudente obligatorio:** "subzona aproximada", "área de lectura", "eje aproximado",
  "área a reforzar". Las subzonas **no** se presentan como límites oficiales.
- **Acentuación cuidada** en portada, índice, títulos y resumen ejecutivo.

---

## 2. Estructura fija de 11 páginas

| Pág. | Contenido | Origen fase19 |
|---|---|---|
| 1 | Portada | Portada / intro (depurada). |
| 2 | Índice | Nuevo, 11 entradas. |
| 3 | Resumen ejecutivo | Reescrito (Tarea 3). |
| 4 | Alcance y criterio de lectura | Sección 2. |
| 5 | Mapa global de 22 polos/ejes | Sección 3. |
| 6 | Lectura territorial general | Sección 4. |
| 7 | Detalle: Palermo / Las Cañitas | Sección 5 (zona 1). |
| 8 | Detalle: Puerto Madero | Sección 5 (zona 2). |
| 9 | Detalle: San Telmo | Sección 5 (zona 3). |
| 10 | Detalle: Corrientes / Abasto | Sección 5 (zona 4). |
| 11 | Detalle: Belgrano | Sección 5 (zona 5). |

**No existe página 12 ni posterior.**

---

## 3. Contenido por página

### Página 1 — Portada
- Título: "Polos gastronómicos de la Ciudad de Buenos Aires".
- Subtítulo: "Informe".
- Marca: "DGDGAS — Dirección General de Gastronomía".
- Organismo: "Gobierno de la Ciudad de Buenos Aires".
- Fecha: "Julio de 2026".
- **Quitar** cualquier frase de "base editorial", "mostrable", "para Ale".

### Página 2 — Índice
Once entradas, exactamente:
1. Portada
2. Índice
3. Resumen ejecutivo
4. Alcance y criterio de lectura
5. Mapa global de 22 polos/ejes
6. Lectura territorial general
7. Detalle: Palermo / Las Cañitas
8. Detalle: Puerto Madero
9. Detalle: San Telmo
10. Detalle: Corrientes / Abasto
11. Detalle: Belgrano

**No listar:** criterio de menciones, hallazgos de capa auxiliar, fuente cartográfica,
decisiones pendientes, recomendaciones prudentes, próximos pasos ni anexos.

### Página 3 — Resumen ejecutivo
- Usar el texto propuesto en `PROPUESTA_RESUMEN_EJECUTIVO_PAGINA_3.md`.
- **Sin** bloque "Para validar con Ale". **Sin** KPIs ni tarjetas numéricas tipo tablero.

### Página 4 — Alcance y criterio de lectura
Conservar el contenido de la sección 2 de fase19:
- El universo semilla es un insumo de trabajo.
- Las menciones destacadas no son ranking, no son recomendación comercial ni padrón de
  locales activos.
- Las subzonas son aproximaciones editoriales de lectura territorial; no son límites oficiales,
  polígonos normativos ni delimitaciones cerradas.

### Página 5 — Mapa global de 22 polos/ejes
- Mapa global de fase19 como pieza principal.
- Texto breve: representa áreas, ejes y zonas de lectura territorial del universo semilla, sin
  definir límites oficiales.

### Página 6 — Lectura territorial general
Conservar el párrafo de la sección 4 de fase19 (Palermo concentra volumen; Puerto Madero como
banda de docks/eje costero; San Telmo desde el Mercado y el casco histórico; Corrientes y
Abasto vinculados pero diferenciados; Belgrano como macroárea con subzonas de respaldo desigual).

### Páginas 7 a 11 — Detalles territoriales
Una zona por página, cada una con su mapa editorial de fase19, una caja de menciones destacadas
(solo las sólidas) y un párrafo de lectura prudente. **Quitar la etiqueta "A validar o tratar
como hito"**; lo pendiente se expresa a nivel de subzona con "subzona a reforzar" / "área a
reforzar".

- **Pág. 7 — Palermo / Las Cañitas:** menciones Palermo/Las Cañitas (Don Julio, La Cabrera,
  Niño Gordo, Gran Dabbang, Mishiguene, La Mar, Cosi Mi Piace; Campo Bravo, Kansas, SushiClub).
  Lectura: Palermo Soho, Palermo Hollywood y Las Cañitas como subzonas aproximadas.
- **Pág. 8 — Puerto Madero:** menciones zona costera/docks (Happening, Sottovoce, El Mercado /
  Faena, Le Grill). Lectura: docks, eje costero, Faena / El Mercado como hito; Dársena Sur como
  área a reforzar.
- **Pág. 9 — San Telmo:** menciones (La Brigada, Café San Juan, Hierbabuena). Lectura: Mercado
  de San Telmo como hito colectivo; casco histórico y eje Defensa como ordenadores.
- **Pág. 10 — Corrientes / Abasto:** menciones Corrientes (Las Cuartetas, El Palacio de la
  Pizza, Pertutti). Lectura: Corrientes como eje teatral-gastronómico aproximado (9 de Julio–
  Callao); Abasto como área a reforzar en torno al shopping, sin fusionarse con Corrientes.
- **Pág. 11 — Belgrano:** menciones Barrio Chino (Hong Kong Style, China Rose). Lectura: Barrio
  Chino con identidad gastronómica clara; Bajo Belgrano con sedes a reforzar; Belgrano R como
  subzona a reforzar.

---

## 4. Eliminar por completo (no aparece en ninguna página)

- Página / sección de **criterio de menciones**.
- **Hallazgos de capa auxiliar** (capa objetiva).
- **Fuente cartográfica y geometrías** (sección 6 de fase19).
- **Decisiones pendientes** (sección 7).
- **Recomendaciones prudentes** (sección 8).
- **Próximos pasos** (sección 9).
- **Anexos**.
- Todo texto "Para validar con Ale".
- Toda mención a "versión mostrable" / "validación con Ale".
- Todo texto que suene a instrucción interna.

---

## 5. Ajustes de índice, numeración y resumen

- **Índice:** solo 11 páginas (ver arriba).
- **Numeración visible:** 1 / 11, 2 / 11, …, 11 / 11.
- **Resumen ejecutivo:** sin bloque "Para validar con Ale" (texto en su documento propio).
- **Pie institucional:** "DGDGAS — Dirección General de Gastronomía" con raya larga si el
  sistema lo permite.

---

## 6. Checklist de conformidad de la pieza final

- [ ] 11 páginas exactas; sin página 12+.
- [ ] Índice con 11 entradas alineadas a la estructura.
- [ ] Numeración "N / 11" en todas las páginas.
- [ ] Cero "Ale" / "validar con Ale" / "validación interna".
- [ ] Resumen ejecutivo sin bloque interno ni KPIs.
- [ ] Marca "DGDGAS — Dirección General de Gastronomía"; sin "DataGastro".
- [ ] Sin campos sensibles/técnicos; sin capturas de Google Maps.
- [ ] Lenguaje prudente; subzonas no presentadas como límites oficiales.
