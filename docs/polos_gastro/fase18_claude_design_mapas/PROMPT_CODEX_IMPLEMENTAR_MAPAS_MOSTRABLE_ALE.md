# Prompt para Codex — Implementar mapas y PDF V5 mostrable

Este archivo contiene un prompt **listo para pegar en Codex**. Todo lo que está debajo de la línea es el
prompt.

---

Retomás **PolosGastro** en el repo `C:\proyectos\Gastronomia\DataGastro`, rama
`mercados-gastronomicos-v2`. Marca pública visible: **DGDGAS — Dirección General de Desarrollo Gastronómico** (nunca
"DataGastro").

## Contexto

El PDF V4 (fase 16) tiene mapas de detalle que todavía se ven generados por script: subzonas como
elipses/manchas, etiquetas que no jerarquizan. Se hizo una **Fase 18 de interpretación de diseño** a partir
de una referencia visual generada en Claude Design. Tu tarea es **implementar una versión V5 mostrable**
del PDF aplicando esa especificación.

## Leé primero (obligatorio, en este orden)

1. `docs/polos_gastro/fase18_claude_design_mapas/DIAGNOSTICO_CLAUDE_DESIGN_VS_V4.md`
2. `docs/polos_gastro/fase18_claude_design_mapas/ESPECIFICACION_VISUAL_MAPAS_MOSTRABLE_ALE.md` ← **criterio
   central; es tu fuente de verdad visual.**
3. `docs/polos_gastro/fase18_claude_design_mapas/ESTRATEGIA_VERSION_MOSTRABLE_ALE.md`
4. Referencia visual (solo como inspiración, **no** se exporta ni se copia tal cual):
   `docs/polos_gastro/fase18_claude_design_mapas/inputs/DGDGAS_mapas_detalle_claude_design_v1.html`
5. Base editorial y datos: `docs/polos_gastro/fase16_mapas_editoriales_v4/INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_V4.md`
6. Base callejera ya descargada (GCBA, CC-BY-2.5-AR):
   `outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson`

Ante conflicto: manda la **especificación visual** de fase 18; luego el Markdown base V4.

## Qué tenés que hacer

1. **Generar mapas V5** de las cinco zonas de detalle (Palermo/Las Cañitas, Puerto Madero, San Telmo,
   Corrientes/Abasto, Belgrano) aplicando el **sistema visual** de la especificación (sección 0) y los
   **criterios por zona** (secciones 3–7):
   - Fondo `#FAFBFC` + grilla de calles tenue **rotada al ángulo del barrio**.
   - Callejero GCBA como **soporte suave**; avenidas nombradas de referencia.
   - Subzonas coloreadas **protagonistas**, con **polígonos angulares anclados a las avenidas** de la
     especificación — **no elipses genéricas**. Corrientes y Puerto Madero como **bandas longitudinales**.
   - **Estado por borde:** sólido = consolidada; discontinuo = a reforzar/validar; punteado tenue = contexto.
   - Rellenos a baja opacidad (15–20% consolidada / 8–10% a reforzar). Paleta y tamaños de la
     especificación (lienzo de referencia 720×560, escalar proporcional).
   - Etiquetas grandes dentro del área + tag "aproximada" mono chica; separación mínima; línea guía si no
     cabe. **Sin superposición.**
   - Hitos como rombo navy (máx. 2–3 por mapa, con etiqueta). **Nunca puntos de locales sobre el mapa.**
   - Nota fija por mapa: **"Referencia territorial — no delimita oficialmente polos"**.
2. **Generar el PDF V5 mostrable:**
   - **Conservar el mapa global** (pág. 5) y la **estructura de 18 páginas** si alcanza.
   - **Reemplazar solo** las páginas de detalle (7–11) por los mapas V5.
   - Conservar las **cajas laterales de menciones** con las mismas listas del Markdown base V4 (sub-bloque
     "a validar" separado con su nota). **No** agregar ni quitar nombres.
   - Pie institucional **"DGDGAS — Dirección General de Desarrollo Gastronómico"**.
   - Fuentes **locales / fallback** (Arial/Calibri). **No** llamar Google Fonts por red.
3. **Rasterizar y QA:** rasterizar las 18 páginas y generar hoja de contacto para control visual.
4. **Guardar todo en** `outputs/polos_gastro/fase19_pdf_mostrable_ale/` (mapas, PDF, assets) y las notas
   de QA/documentos en `docs/polos_gastro/fase19_pdf_mostrable_ale/`. Rasterizados temporales en
   `tmp_pdf_preview/polos_fase19_pdf_v5/`.

## Restricciones (obligatorias)

- **No inventar datos nuevos.** Usar el universo semilla, las menciones y las geometrías ya existentes.
- **No ejecutar API** ni llamadas Google Places / plataformas privadas.
- **No tocar datos fuente** ni el pipeline F01–F05. No modificar `data/`.
- **No tocar otros proyectos:** Cafecito, Mercados, Casas de Pastas, Design System, Borrador 2, Borrador 3.
- **No borrar nada.**
- **No commit / no push / no staging.** No `git add`.
- **No presentar subzonas como límites oficiales.** Mantener lenguaje "subzona aproximada / área de lectura
  / eje aproximado".
- **Sin campos sensibles ni técnicos visibles:** `place_id`, `rating`, `user_ratings_total`, API key, raw
  JSON, rutas locales, nombres de scripts, CSV internos, QA técnico. Sin capturas de Google Maps.
- **Sin marca DataGastro.** Sin "prueba", "borrador", "V5", "preliminar", "documento interno" en el PDF
  visible.
- Cerrados / vigencia no confirmada **fuera** del mapa público; duplicados una sola sede.

## Verificá antes de cerrar (checklist)

- [ ] Los cinco mapas usan el sistema visual (grilla rotada, subzonas protagonistas, estado por borde).
- [ ] **Ninguna elipse genérica** donde se puede trazar polígono por avenidas; Corrientes y Puerto Madero
      longitudinales.
- [ ] Etiquetas grandes, sin superposición, con tag "aproximada" y nota "no delimita oficialmente polos".
- [ ] Corrientes y Abasto **diferenciados** ("vínculo — no continuidad"); Belgrano R y Bajo Belgrano con
      borde discontinuo; Barrio Chino sólido.
- [ ] Mapa global y 18 páginas conservados; solo se reemplazaron 7–11.
- [ ] Cajas laterales con las mismas menciones que V4; sub-bloque "a validar" con nota.
- [ ] Barrido de campos sensibles = 0; sin marca DataGastro; sin etiquetas de proceso.
- [ ] Archivos en `fase19_pdf_mostrable_ale`; hoja de contacto generada.

## Cómo responder

Al terminar, devolvé:
- Lista de archivos generados (mapas, PDF, hoja de contacto) con sus rutas.
- **Problemas visuales** que hayan quedado (etiquetas ajustadas a mano, zonas difíciles, saturación).
- **Pendientes** que requieren decisión de Ale (recorte de Abasto/Corrientes, destino de Belgrano R, si
  Abasto necesita página propia, densidad de color/etiquetas).
- Confirmación explícita de: **no API, no datos fuente tocados, no otros proyectos, no commit/push/staging,
  sin campos sensibles.**
