# Diagnóstico editorial del PDF mostrable actual

**Proyecto:** PolosGastro — DGDGAS (Dirección General de Desarrollo Gastronómico)
**Fecha de diagnóstico:** 3 de julio de 2026
**Pieza revisada:** `outputs/polos_gastro/fase19_pdf_mostrable_ale/INFORME_POLOS_GASTRO_DGDGAS_MOSTRABLE_ALE.pdf`
**Base editorial revisada:** `docs/polos_gastro/fase19_pdf_mostrable_ale/INFORME_POLOS_GASTRO_DGDGAS_PDF_BASE_MOSTRABLE_ALE.md`

Este diagnóstico identifica todo lo que hace que la pieza actual siga leyéndose como
documento interno de trabajo y no como pieza mostrable en oficina. No se ejecuta código,
no se genera PDF, no se generan mapas, no se tocan datos fuente.

---

## 1. Resumen del problema

La pieza de fase19 es metodológicamente correcta y visualmente aceptable, pero conserva
lenguaje y estructura de documento interno. El PDF se rasteriza en **18 páginas** (según
el QA de fase19), mientras que la versión realmente mostrable debería quedar en **11
páginas** cerradas, sin ninguna sección de trabajo posterior ni referencias a validación
interna con una persona.

El problema no es el contenido territorial: es el **envoltorio editorial**. Hay que quitar
todo lo que suene a borrador, pendiente, validación con terceros o instrucción interna.

---

## 2. Menciones a "Ale" y validación interna

Detectadas en la base editorial de fase19:

| Ubicación en la base | Texto problemático | Acción |
|---|---|---|
| Párrafo introductorio (línea 9) | "…la version PDF mostrable **para Ale**." | Eliminar la referencia; el documento no se dirige a una persona. |
| Sección 1 — Resumen ejecutivo (línea 15) | "…para conversacion institucional, **validacion interna** y priorizacion de proximos pasos." | Reemplazar por resumen sin lenguaje de validación interna (ver Tarea 3). |
| Sección 1 — Resumen ejecutivo (líneas 21-25) | Bloque completo **"Para validar con Ale:"** con cuatro viñetas. | Eliminar el bloque completo. |
| Sección 7 — Decisiones pendientes (línea 89) | "Validar **con Ale** el recorte de Corrientes y Abasto." | Eliminar la sección completa. |
| Sección 9 — Próximos pasos (línea 103) | "Revisar **con Ale** delimitaciones, sedes y criterios…" | Eliminar la sección completa. |

Además, el archivo `NOTA_PARA_PRESENTAR_A_ALE.md` es un documento acompañante interno; **no
forma parte del PDF** y no debe convertirse en página. Su título y su bloque "Decisiones a
validar con Ale" son exclusivamente internos.

**Regla para el PDF limpio:** cero apariciones de "Ale", "validar con Ale", "validación
interna" o cualquier destinatario nominal.

---

## 3. Frases de validación / borrador / documento interno

Textos que suenan a borrador, pendiente o instrucción interna y que deben salir del PDF:

- "Este documento es la **base editorial de la version PDF mostrable para Ale**." (intro).
- "**version mostrable, no final**" (concepto que atraviesa la nota y el QA; no debe aparecer
  como texto visible del PDF).
- "que decisiones conviene cerrar **antes de avanzar hacia una version final o de uso
  operativo**" (resumen ejecutivo, línea 19).
- Toda la sección **7. Decisiones pendientes** (líneas 87-92): es agenda interna.
- Toda la sección **8. Recomendaciones prudentes** (líneas 94-99): lenguaje de recomendación
  operativa que no corresponde a una pieza de lectura.
- Toda la sección **9. Próximos pasos** (líneas 101-106): hoja de ruta interna.
- "A validar o tratar como hito" repetido en cada zona de la sección 5: la etiqueta "a
  validar" es de trabajo. En el PDF limpio las menciones deben presentarse sin la marca "a
  validar" (ver Especificación); la prudencia se mantiene con "subzona a reforzar" / "área a
  reforzar", que sí son admisibles.

---

## 4. Páginas que no conviene mostrar (12 en adelante)

Según el QA de fase19, el PDF tiene 18 páginas rasterizadas. Las páginas visibles útiles son
la portada, el resumen, el alcance, el mapa global, la lectura general y los cinco detalles
territoriales. Todo lo que cae **de la página 12 en adelante** corresponde a secciones de
trabajo y debe eliminarse por completo:

- **Criterio de menciones / capa auxiliar** — hallazgos de la capa objetiva; material interno.
- **Sección 6 — Fuente cartográfica y geometrías** (líneas 81-85): menciona base callejera,
  licencia, fecha de portal y "descarga local ya disponible en el proyecto". Es ficha técnica
  interna; no va al PDF mostrable.
- **Sección 7 — Decisiones pendientes** — eliminar.
- **Sección 8 — Recomendaciones prudentes** — eliminar.
- **Sección 9 — Próximos pasos** — eliminar.
- **Anexos** (líneas 108-110): "La tabla de menciones destacadas y la tabla de geometrias
  quedan como respaldo en los outputs de esta fase." Referencia a outputs internos; eliminar.

**Regla:** el PDF limpio cierra en la página 11. No existe página 12 ni posterior.

---

## 5. Índice desactualizado

El índice actual (implícito en la estructura de 9 secciones + anexos) sigue listando
secciones 6 a 9 y anexos, que corresponden a páginas 12-18. Un índice mostrable debe:

- listar **solo 11 entradas**, alineadas con la estructura de la Especificación;
- no incluir "Decisiones pendientes", "Recomendaciones prudentes", "Próximos pasos",
  "Fuente cartográfica y geometrías" ni "Anexos";
- no referenciar números de página superiores a 11.

---

## 6. Numeración desactualizada

La numeración de pie de página puede seguir diciendo "**/18**" (o el total que arrastre el
flujo de render de fase19), aunque la versión visible deba quedar en 11 páginas. Debe
corregirse a formato **"N / 11"** en las once páginas (1/11 … 11/11), sin saltos ni totales
heredados.

---

## 7. Contenido que debilita la presentación

- **Sección 6 (ficha cartográfica):** expone base callejera, licencia CC-BY, fecha de portal
  y "descarga local ya disponible en el proyecto". En una pieza de oficina esto suena a nota
  técnica de trabajo y menciona rutas/insumos internos. Fuera del cuerpo mostrable.
- **Etiquetas "A validar o tratar como hito":** en cada zona conviven menciones sólidas con
  ítems "a validar". Mezclar ambas categorías dentro de una caja de "menciones destacadas"
  debilita la lectura. En el PDF limpio, las menciones destacadas deben ser las sólidas; lo
  "a reforzar" se expresa solo a nivel de subzona con lenguaje prudente.
- **Simplificación de tildes** (según QA): algunos textos secundarios pierden tildes por
  compatibilidad del render. No es bloqueante para mostrar, pero conviene señalarlo para que
  el generador cuide acentuación en portada, índice, títulos y resumen ejecutivo.
- **Pie institucional:** debe unificarse a "DGDGAS — Dirección General de Desarrollo Gastronómico" con
  raya larga (em dash) si el sistema de render lo permite; si no, guion largo simple.

---

## 8. Inventario de secciones fase19 → decisión fase20

| # | Sección fase19 | Decisión fase20 |
|---|---|---|
| Intro | Párrafo "base editorial mostrable para Ale" | **Eliminar** (reemplaza portada + subtítulo institucional). |
| 1 | Resumen ejecutivo (con bloque "Para validar con Ale") | **Reescribir** sin bloque interno (Tarea 3). |
| 2 | Alcance y criterio de lectura | **Conservar**, revisado. |
| 3 | Mapa global de 22 polos/ejes | **Conservar**. |
| 4 | Lectura territorial general | **Conservar**, revisado. |
| 5 | Detalles territoriales (5 zonas) | **Conservar** como 5 páginas de detalle, sin "a validar". |
| 6 | Fuente cartográfica y geometrías | **Eliminar** del PDF. |
| 7 | Decisiones pendientes | **Eliminar**. |
| 8 | Recomendaciones prudentes | **Eliminar**. |
| 9 | Próximos pasos | **Eliminar**. |
| — | Anexos | **Eliminar** del PDF. |

---

## 9. Conclusión del diagnóstico

La pieza de fase19 es una buena base de contenido, pero editorialmente sigue siendo un
documento de trabajo. Para una versión mostrable en oficina hay que:

1. eliminar toda referencia nominal ("Ale") y de validación interna;
2. eliminar las secciones 6 a 9 y los anexos (páginas 12 en adelante);
3. reescribir el resumen ejecutivo sin bloque interno;
4. reconstruir índice y numeración a 11 páginas;
5. unificar el pie institucional a "DGDGAS — Dirección General de Desarrollo Gastronómico";
6. mantener el lenguaje prudente ("subzona aproximada", "área de lectura", "eje aproximado",
   "área a reforzar") sin presentar subzonas como límites oficiales.

La especificación operativa de estas correcciones está en
`ESPECIFICACION_PDF_11_PAGINAS_OFICINA.md`.
