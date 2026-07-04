# Plan de mejora cartográfica V3 — PolosGastro DGDGAS

Marca pública: **DGDGAS — Dirección General de Gastronomía**.
Documento de planificación para que Codex rehaga los mapas de detalle con base callejera.
No ejecuta API, no genera PDF, no genera mapas, no toca datos fuente. No commit / no push / no staging.

Referencia de partida: PDF V2 de 18 páginas
`outputs/polos_gastro/fase14_pdf_institucional_revision_visual/INFORME_POLOS_GASTRO_DGDGAS_PRELIMINAR_V2.pdf`.

---

## 1. Diagnóstico visual del V2

El V2 mejoró de forma clara respecto al V1: conserva el mapa global, agrega cajas de menciones
destacadas por polo/subzona, mejora la lectura institucional y no contiene campos sensibles
(barrido de QA V2: 0 emails, teléfonos, DNI, CUIT, `place_id`, `rating`, `user_ratings_total`,
raw JSON, rutas locales ni marca interna).

Lo que funciona y **debe conservarse**:

- El **mapa global** de los 22 polos/ejes. Es la lectura principal del universo y no se rediseña.
- Las **cajas de menciones destacadas** por polo/subzona. Sirven y deben mantenerse.
- El tono institucional sobrio y la estructura de 18 páginas.

Lo que **no alcanza**:

- Los **mapas de detalle (páginas 7–11)** siguen siendo demasiado esquemáticos: puntos y símbolos
  sobre un fondo casi vacío. Sin calles ni referencias urbanas no se entiende el territorio.
- Para las páginas de zoom territorial hace falta **base callejera** (avenidas, calles de
  referencia, hitos urbanos) que permita ubicar los polos en la trama real de la ciudad.

Diego detectó correctamente este punto: el detalle territorial no se lee.

---

## 2. Objetivo de los mapas V3

- Mapas de detalle con **calles, avenidas y referencias urbanas** legibles.
- **No deben parecer salidas técnicas** (ni output de SIG ni de librería de mapas crudo).
- Deben verse **institucionales y aptos para PDF DGDGAS**, en línea con el resto del informe.
- Deben **complementar** las cajas de menciones destacadas, no reemplazarlas ni competir con ellas.

---

## 3. Mapas a rehacer

Sólo las cinco páginas de detalle territorial (7 a 11 del V2). El mapa global no se toca.

1. Palermo / Las Cañitas (pág. 7).
2. Puerto Madero (pág. 8).
3. San Telmo (pág. 9).
4. Corrientes / Abasto (pág. 10).
5. Belgrano y subzonas (pág. 11).

---

## 4. Requisitos cartográficos (transversales a todas las zonas)

- Usar una **base callejera limpia**, no un fondo satelital ni un mapa técnico recargado.
- Mostrar **avenidas principales** siempre.
- Mostrar **calles relevantes** sólo si no sobrecargan la lectura.
- Mantener los **puntos como apoyo**, no como protagonista; sirven para ubicar, no para contar.
- **No mostrar cerrados como activos.**
- **No mostrar duplicados ni queries a corregir** en el mapa.
- **No usar nombres de locales sobre el mapa**, salvo 2 o 3 hitos muy claros por zona.
- Mantener los **nombres destacados en las cajas laterales** (como en el V2).
- Incluir siempre la nota: **"lectura territorial preliminar, no delimitación oficial"**.

---

## 5. Requisitos por zona

### Palermo / Las Cañitas
- Diferenciar **Palermo Soho / Palermo Hollywood** y **Las Cañitas** como subzonas distintas.
- Usar referencias urbanas y avenidas para separarlas (ejes viales, no líneas inventadas).
- Mantener las menciones destacadas en caja lateral: **Don Julio, La Cabrera, Niño Gordo,
  Gran Dabbang, Mishiguene, La Mar, Cosi Mi Piace, Campo Bravo, Kansas, SushiClub.**
  (Café Registrado se mantiene con cautela, como en el V2.)

### Puerto Madero
- Mostrar los **docks / corredor costero** como estructura reconocible de la zona.
- Ubicar **hitos y sedes a validar** sin darles el mismo peso que las menciones con más respaldo.
- **No sobredimensionar casos dudosos** (Cabaña Las Lilas, La Parolaccia Casa Tua, Red Resto &
  Lounge, Patagonia Sur siguen como "a validar").

### San Telmo
- Mostrar el entorno del **Mercado de San Telmo** y las calles de referencia del casco.
- Tratar el **Mercado de San Telmo como hito colectivo**, no como restaurante puntual.

### Corrientes / Abasto
- Mostrar la **Av. Corrientes entre 9 de Julio y Callao** como eje.
- Mostrar el **área Abasto alrededor del shopping**, con radio aproximado de cinco cuadras.
- Dejar claro que Corrientes y Abasto son **ejes vinculados, no el mismo polo**.
- **Evitar el doble conteo** (una mención no puede sumar en los dos).

### Belgrano
- Separar **Barrio Chino, Bajo Belgrano y Belgrano R** como subzonas.
- **Belgrano R** debe verse como **subzona a reforzar, no como polo consolidado.**

---

## 6. Fuentes posibles para la base callejera (opciones para Codex)

Ordenadas de menor a mayor fricción. **No descargar nada sin dejar documentado origen, fecha y
licencia.** Regla del repo: sólo APIs oficiales, datos agregados o cartografía pública; nada de
scraping ni plataformas privadas.

1. **Capas locales ya disponibles en el proyecto.** Hay polígonos de barrios y comunas:
   - `data/raw/geo_barrios.geojson`
   - `data/raw/geo_comunas.geojson`
   Sirven para el **contorno de barrio/subzona** pero **no traen calles**. Útiles como marco, no
   como base callejera.
2. **Cartografía pública GCBA (BA Data / USIG).** Si el proyecto ya tiene descargada una capa de
   calles/ejes de circulación del GCBA, usarla como base callejera oficial (origen institucional,
   preferible para una pieza DGDGAS). Verificar si existe antes de descargar; si no está, dejar
   registrado qué capa se necesita.
3. **OpenStreetMap / callejero** como base de referencia, **si el proyecto lo permite** y sólo
   como capa de contexto visual (no como fuente de datos de locales). Documentar atribución y
   licencia ODbL. No mezclar con el universo semilla de polos.

Criterio: preferir GCBA por institucionalidad; OSM como alternativa de contexto. En ambos casos
registrar **origen, fecha de descarga y licencia** en el anexo cartográfico del PDF.

---

## 7. Criterios para el PDF V3

- **Conservar la estructura de 18 páginas** si alcanza.
- Mantener el **mapa global** (pág. 5) sin cambios.
- **Reemplazar las páginas 7–11** por los nuevos mapas callejeros de detalle.
- Mantener las **cajas de menciones destacadas** en cada página de detalle.
- Corregir el pie institucional a **"DGDGAS — Dirección General de Gastronomía"** si en algún lugar
  aparece con guion simple u otra variante.
- **No usar lenguaje técnico ni experimental** en el cuerpo visible.

---

## 8. Checklist para Codex

- [ ] Localizar la fuente callejera (capa local → GCBA descargada → OSM), con origen/fecha/licencia.
- [ ] Generar los mapas por zona (Palermo/Las Cañitas, Puerto Madero, San Telmo, Corrientes/Abasto, Belgrano).
- [ ] Revisar legibilidad de cada mapa (avenidas visibles, calles sin sobrecargar, puntos como apoyo).
- [ ] Insertar los mapas en el PDF V3 reemplazando las páginas 7–11.
- [ ] Rasterizar las páginas para control visual (hoja de contacto).
- [ ] Verificar campos sensibles: 0 `place_id`, `rating`, `user_ratings_total`, API key, raw JSON, rutas locales, emails/teléfonos/DNI/CUIT.
- [ ] Verificar que **no diga DataGastro** en ningún lado visible.
- [ ] Verificar que no diga **prueba / borrador / revisión institucional / documento interno** en el cuerpo visible.
- [ ] Verificar que los **cerrados no aparezcan como activos**, y que duplicados y queries a corregir no figuren como destacados.
- [ ] Confirmar que la nota "lectura territorial preliminar, no delimitación oficial" está en cada mapa de detalle.

---

## 9. Restricciones de ejecución

- No ejecutar API ni llamadas Google Places / plataformas privadas.
- No tocar datos fuente ni el pipeline F01–F05.
- No borrar archivos. No tocar otros proyectos (Cafecito, Mercados, Casas de Pastas, Design System).
- No commit / no push / no staging.
