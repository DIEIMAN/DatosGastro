# QA visual de visuales regenerados — Fase 4A

Fecha: 2026-06-29.

Revisión visual de cada PNG nuevo en `outputs/polos_gastro/graficos/fase4a/`. Clasificación:
`apto_informe` · `apto_con_ajustes` · `solo_interno` · `descartar`.

---

## 1. `universo_polos_por_grupo_v2.png`

- Legibilidad: alta. Títulos: ok. Nota: "jerarquía metodológica, no intensidad" (separada del footer).
- Etiquetas/superposición/saturación: sin problemas.
- **Clasificación: `apto_informe`.**

## 2. `precision_delimitacion_polos_v2.png`

- Legibilidad: alta. Escala azul ordinal (oscuro→claro) refuerza que es una escala; rojo para
  "sin delimitación". Nota separada del footer.
- Sin superposición ni saturación.
- **Clasificación: `apto_informe`.**

## 3. `familias_territoriales_polos_v2.png`

- Rediseño a **barras agrupadas** (antes apiladas): mucho más comparable.
- Solape de nota/footer **corregido** (separados).
- Legibilidad: alta. Densidad de barras moderada pero clara.
- **Clasificación: `apto_informe`.**

## 4. `mapa_conceptual_polos_gastro_resumido_v2.png`

- Muestra núcleo + relevantes + candidatos. Sin anexos ni `no_incluir`.
- **Solape de etiquetas resuelto** (spread vertical por celda). Sin caja que tape.
- Nota roja visible: "Esquema conceptual preliminar. No representa delimitaciones oficiales."
- **Clasificación: `apto_informe`.**

## 5. `mapa_conceptual_polos_gastro_completo_v2.png`

- Muestra todo el universo salvo `no_incluir`. Sin solapes (mejora clara vs. v1).
- Más denso por diseño; legible.
- **Clasificación: `apto_con_ajustes`** (apto para anexo del informe; o `solo_interno` si se
  prefiere mantener el cuerpo del informe con el resumido).

## 6. `mapa_estatico_caba_polos_gastro_v1.png`

- Mapa real de CABA con barrios oficiales; resalta barrios asociados por grupo (núcleo,
  relevante, candidato). Etiquetas combinadas por barrio compartido (Palermo
  Soho/Hollywood/Cañitas; Villa Urquiza/DoHo; Recoleta/Costanera Norte; Microcentro/Centro/
  Avenida Corrientes) → **sin texto encimado**.
- Nota roja visible y atribución Buenos Aires Data en el pie.
- Densidad alta en el norte/centro pero legible.
- **Clasificación: `apto_informe`** (es el mapa territorial principal). Nota: las etiquetas
  combinadas son honestas (barrio de referencia compartido), no afirman delimitación.

## 7. `mapa_estatico_caba_polos_gastro_nucleo_v1.png`

- Versión con solo núcleo + zonas relevantes: más limpia, ideal para el cuerpo del informe.
- Misma corrección de etiquetas; nota y atribución presentes.
- **Clasificación: `apto_informe`.**

---

## Síntesis

| PNG | Clasificación |
| --- | --- |
| universo_polos_por_grupo_v2 | apto_informe |
| precision_delimitacion_polos_v2 | apto_informe |
| familias_territoriales_polos_v2 | apto_informe |
| mapa_conceptual_resumido_v2 | apto_informe |
| mapa_conceptual_completo_v2 | apto_con_ajustes (anexo / interno) |
| mapa_estatico_caba_v1 | apto_informe |
| mapa_estatico_caba_nucleo_v1 | apto_informe |

**Descartados: ninguno.** Todos los problemas de la auditoría previa (solape de etiquetas,
caja que tapaba, apilado denso, falta de mapa territorial) quedaron resueltos.

## Correcciones aplicadas en esta fase

- Familias: apilado → barras agrupadas; nota/footer separados.
- Mapas conceptuales: spread vertical por celda; sin caja superpuesta; nota roja visible.
- Mapa estático: etiqueta combinada por barrio compartido (resuelve el encimado de Palermo y
  Villa Urquiza/DoHo).

## Pendiente menor (no bloqueante)

- En el mapa estático completo, algunos barrios concentran varios polos en una etiqueta larga.
  Si se quiere, en una fase futura se puede mover esas etiquetas a un recuadro lateral. No es
  necesario para el informe.
