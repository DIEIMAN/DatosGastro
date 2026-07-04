# Prompt para Codex — generar PDF limpio de 11 páginas

**Proyecto:** PolosGastro — DGDGAS
**Fecha:** 3 de julio de 2026

Copiar y pegar el bloque de abajo en Codex. No ejecutar nada desde este documento.

---

## Prompt (listo para pegar)

```
Contexto: repositorio C:\proyectos\Gastronomia\DataGastro, proyecto PolosGastro de la
DGDGAS (Dirección General de Desarrollo Gastronómico). Ya existe una pieza en fase19:
- Base editorial: docs/polos_gastro/fase19_pdf_mostrable_ale/INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_MOSTRABLE_ALE.md
- PDF actual: outputs/polos_gastro/fase19_pdf_mostrable_ale/INFORME_POLOS_GASTRO_DGDGAS_MOSTRABLE_ALE.pdf

Tarea: generar una versión PDF LIMPIA de EXACTAMENTE 11 páginas, mostrable en oficina,
partiendo de fase19 y aplicando la especificación de fase20:
- docs/polos_gastro/fase20_limpieza_mostrable_oficina/ESPECIFICACION_PDF_11_PAGINAS_OFICINA.md
- docs/polos_gastro/fase20_limpieza_mostrable_oficina/PROPUESTA_RESUMEN_EJECUTIVO_PAGINA_3.md

Estructura fija de 11 páginas:
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

Debes:
- Eliminar por completo todas las páginas 12 en adelante (criterio de menciones, hallazgos de
  capa auxiliar, fuente cartográfica y geometrías, decisiones pendientes, recomendaciones
  prudentes, próximos pasos y anexos). El PDF cierra en la página 11.
- Eliminar TODA mención a "Ale".
- Eliminar TODA mención a "validar con Ale", "validación interna" y "versión mostrable".
- Eliminar el bloque "Para validar con Ale" del resumen ejecutivo.
- Reemplazar el resumen ejecutivo (página 3) por el texto de PROPUESTA_RESUMEN_EJECUTIVO_PAGINA_3.md.
- Limpiar el índice para que tenga solo las 11 entradas de la estructura.
- Corregir la numeración de pie a formato "N / 11" (1/11 … 11/11); no dejar totales heredados
  como "/18".
- Usar como marca visible únicamente "DGDGAS — Dirección General de Desarrollo Gastronómico" (nunca
  "DataGastro"), y pie institucional "DGDGAS — Dirección General de Desarrollo Gastronómico" con raya larga
  si el sistema de render lo permite.
- Mantener los mapas actuales de fase19 tal como están si no hay tiempo para rediseñarlos.
- Mantener lenguaje prudente ("subzona aproximada", "área de lectura", "eje aproximado", "área
  a reforzar"); no presentar subzonas como límites oficiales.
- Quitar la etiqueta "A validar o tratar como hito" de las cajas de menciones; lo pendiente se
  expresa solo a nivel de subzona con "subzona a reforzar" / "área a reforzar".

Prohibido:
- No tocar datos fuente (data/, XLSX, pipeline F01-F05).
- No ejecutar APIs ni llamadas a Google Places. No scraping. No capturas de Google Maps.
- No incluir place_id, rating, user_ratings_total, API key, raw JSON, rutas locales, nombres de
  scripts, QA técnico ni nombres de CSV internos en el PDF.
- No hacer commit, no hacer push, no hacer staging, no usar git add.
- No tocar Cafecito, Mercados, Casas de Pastas, Borrador 2 ni Borrador 3.

Salida final:
- El PDF debe llamarse:
  outputs/polos_gastro/fase20_limpieza_mostrable_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA.pdf

Al terminar, hacer un barrido textual del PDF confirmando: 11 páginas, sin "Ale", sin
"DataGastro", sin campos sensibles/técnicos, numeración "N / 11", índice de 11 entradas.
```

---

## Notas de control (no pegar, para seguimiento humano)

- La ruta del PDF de salida es fija; no cambiarla.
- Si Codex propone rediseñar mapas, recordar que el pedido es mantener los actuales salvo que
  haya tiempo explícito para rehacerlos.
- Tras la corrida, verificar contra el checklist de
  `ESPECIFICACION_PDF_11_PAGINAS_OFICINA.md` y `QA_FASE20_LIMPIEZA_EDITORIAL.md`.
