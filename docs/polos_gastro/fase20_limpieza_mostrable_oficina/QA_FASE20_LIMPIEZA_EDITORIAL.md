# QA — Fase 20: limpieza editorial mostrable oficina

**Proyecto:** PolosGastro — DGDGAS (Dirección General de Gastronomía)
**Fecha de control:** 3 de julio de 2026

Control de la fase editorial (solo documentos). **No se ejecutó código, no se generó PDF, no
se generaron mapas, no se tocaron datos fuente.**

---

## 1. Documentos creados

- [x] `DIAGNOSTICO_PDF_MOSTRABLE_ACTUAL.md` — diagnóstico editorial del PDF/base actual.
- [x] `ESPECIFICACION_PDF_11_PAGINAS_OFICINA.md` — especificación de la pieza de 11 páginas.
- [x] `PROPUESTA_RESUMEN_EJECUTIVO_PAGINA_3.md` — propuesta de resumen ejecutivo (página 3).
- [x] `HERRAMIENTAS_MAPAS_PROXIMA_ITERACION.md` — análisis de herramientas de mapas a futuro.
- [x] `PROMPT_CODEX_GENERAR_PDF_11_PAGINAS.md` — prompt listo para pegar en Codex.
- [x] `QA_FASE20_LIMPIEZA_EDITORIAL.md` — este documento.

Todos en `docs/polos_gastro/fase20_limpieza_mostrable_oficina/`.

---

## 2. Confirmaciones de tareas

- [x] Diagnóstico creado.
- [x] Especificación creada.
- [x] Propuesta de resumen ejecutivo creada.
- [x] Documento de herramientas creado.
- [x] Prompt Codex creado.

---

## 3. Confirmaciones de alcance (no ejecución)

- [x] No se generó PDF.
- [x] No se generaron mapas.
- [x] No se ejecutaron APIs.
- [x] No se hicieron llamadas a Google Places.
- [x] No se usó scraping.
- [x] No se usaron capturas de Google Maps.
- [x] No se tocaron datos fuente (`data/`, XLSX, pipeline F01-F05).
- [x] No se tocaron scripts productivos.

---

## 4. Confirmaciones de aislamiento (otros proyectos)

- [x] No se tocó Cafecito.
- [x] No se tocó Mercados.
- [x] No se tocó Casas de Pastas.
- [x] No se tocó Borrador 2.
- [x] No se tocó Borrador 3.
- [x] No se tocó la fase19 (solo se leyó como base).

---

## 5. Confirmaciones de git

- [x] No se hizo commit.
- [x] No se hizo push.
- [x] No se hizo staging.
- [x] No se usó `git add .`.

---

## 6. Confirmaciones de contenido sensible/marca

- [x] Los documentos no incluyen `place_id`, `rating`, `user_ratings_total`, API key ni raw JSON
  como contenido público de la pieza.
- [x] La especificación prohíbe explícitamente esos campos en el PDF.
- [x] Marca pública: "DGDGAS — Dirección General de Gastronomía"; sin "DataGastro" como marca
  pública.
- [x] Lenguaje prudente exigido; subzonas no presentadas como límites oficiales.
- [x] Referencias internas a rutas, scripts y CSV aparecen solo en documentos de trabajo de
  fase20 (diagnóstico/especificación/prompt), no en el contenido destinado al PDF.

> Nota: los documentos de fase20 son documentos internos de trabajo; citan rutas de fase19 y el
> nombre del PDF de salida para poder operar. Eso es correcto para trabajo interno. El PDF
> mostrable final, en cambio, no debe contener ninguna de esas referencias (así lo exige la
> Especificación y lo verifica el barrido textual pedido en el prompt de Codex).

---

## 7. Pendiente (fuera de esta fase)

- Generación del PDF de 11 páginas por Codex, siguiendo
  `PROMPT_CODEX_GENERAR_PDF_11_PAGINAS.md`.
- Salida esperada:
  `outputs/polos_gastro/fase20_limpieza_mostrable_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA.pdf`.
- Verificación posterior contra el checklist de la Especificación.
