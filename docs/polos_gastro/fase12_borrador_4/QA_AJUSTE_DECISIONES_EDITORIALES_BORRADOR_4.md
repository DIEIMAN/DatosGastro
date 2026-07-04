# QA — Ajuste por decisiones editoriales, Borrador 4 PolosGastro

DGDGAS — Dirección General de Desarrollo Gastronómico. Documento interno. Fecha: 2026-07-02.

## Entregables

- **Creado**: `DECISIONES_EDITORIALES_DIEGO_BORRADOR_4.md` (8 criterios registrados).
- **Creado**: `PLAN_MAPAS_BORRADOR_4.md` (mapa global + puntos internos + 5 mapas de detalle +
  criterios de exclusión).
- **Creado**: este QA.
- **Modificado**: `INFORME_POLOS_GASTRO_BORRADOR_4.md` (ajustes puntuales, sin reescritura).
- **Modificado**: `NOTAS_REVISION_HUMANA_BORRADOR_4.md` (reducidas a lo que queda abierto).

## Decisiones editoriales incorporadas al informe

- **Cerrados/vigencia no confirmada (8)**: no como activos, fuera de mapa público y cuerpo; se
  conservan internamente (secciones 5, 6, 8).
- **Avenida Corrientes**: eje teatral-gastronómico, tramo **9 de Julio–Callao** (secciones 4, 6, 7,
  8).
- **Abasto**: área alrededor del shopping, **radio ~5 cuadras**; eje vinculado a Corrientes con
  delimitación distinta, sin fusión ni doble conteo (secciones 4, 6, 7, 8).
- **Polos sin locales explícitos (9)**: integran el universo y se **marcan en el mapa global**
  (secciones 4, 5, 7, 8).
- **Mapa global** de los 22 polos/ejes (áreas/ejes), locales en **mapas de detalle** (secciones 5,
  10; plan de mapas).
- **Publicabilidad institucional** con marca DGDGAS; tono publicable, no experimental (encabezado,
  secciones 9, 10).

## Notas de revisión humana

Reducidas: se retiraron los puntos ya decididos por Diego. Quedan para Ale: delimitación
Corrientes/Abasto, tipo de mapa, nombres en mapas de detalle, recomendaciones en cuerpo o anexos,
formato PDF/DOCX, y polos a destacar. Puntos técnicos menores: Belgrano/subzonas y sedes de
duplicados/cadenas.

## Confirmaciones

- **Decisiones editoriales registradas.** **Borrador 4 ajustado** (puntual, sin reescribir).
  **Notas reducidas.** **Plan de mapas creado.**
- **No se ejecutó API.** **No se generó PDF, DOCX ni mapas.**
- **No se tocaron datos fuente**, ni Cafecito, Mercados o Casas de Pastas. No se borró nada.
- **No commit / push / staging.** No se usó `git add`.
- **No se usó "DataGastro"** como marca pública; marca visible: **DGDGAS — Dirección General de
  Gastronomía**.
- Documentos **sin** place_id, rating, user_ratings_total, API key ni raw JSON (verificado por
  búsqueda: 0 coincidencias en el contenido del informe/notas/plan/decisiones).

## Observación menor para la maquetación

El informe conserva, en sus anexos, referencias a nombres de tablas de respaldo (CSV). No son rutas
absolutas ni datos técnicos sensibles, pero al producir la **pieza PDF institucional** conviene
omitir esas referencias de archivo del texto visible, dejándolas solo como respaldo interno.
