# Handoff a Codex — Mapas y PDF del Borrador 4 PolosGastro

DGDGAS — Dirección General de Gastronomía. Documento interno de traspaso. Fecha: 2026-07-02.
Este documento explica todo lo necesario para que Codex retome PolosGastro y avance hacia los
**mapas** y la **pieza PDF institucional**, sin volver a revisar el proceso desde cero.

---

## 1. Estado actual del proyecto

- Universo semilla cerrado: **22 polos/ejes** gastronómicos de la Ciudad.
- **106 menciones** de locales relevadas del documento semilla.
- **Cobertura completa** de la capa auxiliar de geolocalización: 106/106 ubicados (todos en la
  Ciudad), como **capa auxiliar**, no como padrón ni validador oficial.
- **Borrador 4 redactado** y orientado a pieza institucional publicable DGDGAS.
- **Decisiones editoriales de Diego incorporadas**.
- **Plan de mapas creado** (aún no se generaron mapas).
- El proyecto está en **punto de decisión y producción visual**, no de nuevo relevamiento.

## 2. Qué ya está cerrado

- El **universo semilla** (22 polos/ejes) y su lectura territorial.
- La **capa auxiliar** de geolocalización de los 106 locales, con su clasificación prudente
  (59 razonables/fuertes; 8 vigencia no confirmada; 11 duplicados probables; 25 zona/sucursal a
  revisar; 3 búsquedas a corregir).
- La **redacción del Borrador 4** (informe, resumen ejecutivo, decisiones, plan de mapas, notas).
- Los **criterios editoriales** de Diego (ver punto 4).
- La **orientación institucional** de la pieza (marca DGDGAS, posible destino Vicejefatura).

## 3. Qué archivos son la fuente de verdad

Documentos (Markdown):

- `docs/polos_gastro/fase12_borrador_4/INFORME_POLOS_GASTRO_BORRADOR_4.md` — informe base.
- `docs/polos_gastro/fase12_borrador_4/RESUMEN_EJECUTIVO_POLOS_GASTRO_BORRADOR_4.md` — resumen.
- `docs/polos_gastro/fase12_borrador_4/DECISIONES_EDITORIALES_DIEGO_BORRADOR_4.md` — acta de Diego.
- `docs/polos_gastro/fase12_borrador_4/PLAN_MAPAS_BORRADOR_4.md` — plan de mapas.
- `docs/polos_gastro/fase12_borrador_4/NOTAS_REVISION_HUMANA_BORRADOR_4.md` — puntos abiertos.

Tablas de respaldo (insumo interno, **no** exponer nombres de archivo en el PDF público):

- `outputs/polos_gastro/fase12_borrador_4/tablas/tabla_polos_borrador_4.csv` — 22 polos.
- `outputs/polos_gastro/fase12_borrador_4/tablas/casos_criticos_borrador_4.csv` — 51 casos.
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/consolidado_tandas_google_places.csv`
  — 106 locales (base auxiliar de revisión).

Ante conflicto entre documentos, mandan las **decisiones editoriales de Diego** y luego el
**informe**.

## 4. Decisiones editoriales de Diego ya tomadas

- **Cerrados / vigencia no confirmada:** no se incluyen en el mapa público ni en el cuerpo
  principal como activos; se conservan internamente como referencia semilla.
- **Avenida Corrientes:** eje teatral-gastronómico, tramo **9 de Julio–Callao**.
- **Abasto:** área alrededor del Abasto, entorno del shopping como centro, **radio ~5 cuadras**.
  Corrientes y Abasto son **ejes vinculados con delimitación distinta**, no un mismo polo (evitar
  doble conteo).
- **Polos sin locales explícitos (9):** se **marcan igual en el mapa global** como parte del
  universo semilla; no se descartan.
- **Mapas:** el mapa global muestra los **22 polos/ejes** (áreas/ejes), no solo los locales
  geolocalizados; la capa de locales es auxiliar y va a **mapas de detalle**; cerrados/dudosos
  fuera de mapas públicos.
- **Publicabilidad:** el informe será **publicable institucionalmente** (marca DGDGAS), con posible
  circulación hacia **Vicejefatura de Gobierno**.
- **Estilo:** cercano a **Casas de Pastas y Mercados** (limpio, institucional, visual, prudente,
  apto para conducción); evitar lenguaje técnico/experimental/interno.

## 5. Qué queda para Ale

- Validar la **delimitación** de Abasto (radio ~5 cuadras del shopping) y Corrientes
  (9 de Julio–Callao).
- Definir el **tipo de mapa**: por polos, por zonas o por locales.
- Definir si se muestran **nombres de locales** en los mapas de detalle.
- Definir si las **recomendaciones** van en el cuerpo o en anexos.
- Definir el **formato de salida**: PDF final, DOCX editable o ambos.
- Señalar **polos a destacar** por interés de gestión.
- Puntos técnicos menores: **Belgrano** (subzonas con respaldo diferenciado, Belgrano R más débil)
  y sede a mapear en **duplicados/cadenas**.

## 6. Qué mapas hay que generar

1. **Mapa global** de los **22 polos/ejes**, incluidos los que **no** tienen locales explícitos.
2. **Mapa de puntos internos**: los 59 locales con correspondencia razonable/fuerte (uso interno,
   no público).
3. **Mapas de detalle** por zonas prioritarias: Palermo / Las Cañitas, Puerto Madero, San Telmo,
   Corrientes / Abasto, Belgrano.

## 7. Qué criterios seguir para mapas

- El **mapa global** representa los 22 polos/ejes como **áreas o ejes**, no como puntos de locales.
  Corrientes se dibuja como **eje/línea** en el tramo **9 de Julio–Callao**; Abasto como **área**
  alrededor del shopping (radio ~5 cuadras).
- Los **polos sin locales explícitos** se representan como área/eje según su tipo territorial,
  **nunca** como punto de local; se rotulan con nota de refuerzo documental pendiente.
- **Cerrados / vigencia no confirmada:** fuera de todo mapa público.
- **Duplicados:** una sola sede por punto; el resto no se repite.
- **Zona/sucursal a revisar y búsquedas a corregir:** no entran a mapa público hasta confirmación.
- **Hitos colectivos** (Mercado de San Telmo, Patio de los Lecheros, El Mercado / Faena): como
  referencia colectiva, no como punto de restaurante.
- La **capa de locales** es auxiliar; acompaña, no reemplaza el universo semilla.

## 8. Qué NO debe mostrarse en el PDF público

- Nombres de archivos internos (CSV, scripts) ni rutas locales.
- Referencias a la herramienta de geolocalización como validador; solo como **señal auxiliar**.
- Lenguaje experimental o de proceso ("capa experimental", jerga de la herramienta, detalles de
  ejecución, tandas, corridas).
- Locales cerrados / dudosos presentados como activos.
- La palabra **DataGastro** como marca pública (marca visible: **DGDGAS**).
- Etiquetas de estado del documento ("prueba", "borrador", "documento interno") si se entrega como
  pieza final.

## 9. Qué datos sensibles no deben aparecer

- `place_id`, `rating`, `user_ratings_total`.
- API key, raw JSON de la herramienta.
- Rutas de archivos locales, nombres de scripts.
- Cualquier dato personal (CUIT, DNI, emails, teléfonos, contactos, transacciones individuales).
- Filas individuales sensibles: trabajar con agregados y conteos.

## 10. Qué estilo visual se espera

- Línea de **Casas de Pastas y Mercados DGDGAS**: sobrio, institucional, visual, prudente.
- Portada DGDGAS y pie institucional.
- Cajas de lectura/advertencia/método claras; tono apto para conducción política.
- Mapas legibles a nivel conducción, con disclaimer de que la geolocalización acompaña y no valida.
- Sin apariencia experimental ni de expediente técnico.

## 11. Qué pasos debe hacer Codex después

1. Esperar/confirmar las **decisiones de Ale** (punto 5), sobre todo delimitaciones, tipo de mapa y
   formato de salida.
2. **Generar los mapas** según los puntos 6 y 7 (global primero, luego detalle).
3. **Maquetar la pieza PDF institucional** con estilo DGDGAS, aplicando la checklist de cierre
   (`CHECKLIST_CIERRE_PDF_POLOS_GASTRO_DGDGAS.md`).
4. Verificar contra la checklist que no aparezcan marca DataGastro, rutas, CSV internos, campos
   sensibles ni cerrados como activos.
5. Recién entonces preparar la **versión final** (PDF y/o DOCX según decisión) para eventual
   circulación hacia Vicejefatura.

> Nota operativa: no ejecutar API, no tocar datos fuente ni scripts productivos, no otros proyectos
> (Cafecito, Mercados, Casas de Pastas), y no commit/push/staging sin permiso explícito de Diego.
