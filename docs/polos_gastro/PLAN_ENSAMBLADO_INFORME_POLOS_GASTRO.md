# Plan de ensamblado del informe PolosGastro

Fecha: 2026-06-29.

Plan de armado del futuro informe. **No es el informe ni el PDF.** No se redacta contenido final
todavía. Sirve para definir qué insumos alimentan cada parte antes de escribir el primer borrador
(Fase 5).

---

## 1. Documentos que ya alimentan el informe

| Insumo | Aporta a |
| --- | --- |
| `UNIVERSO_DEFENDIBLE_INFORME_POLOS_GASTRO.md` | Definición del universo y criterios. |
| `LECTURA_UNIVERSO_INFORME_POLOS_GASTRO.md` | Lectura por grupo. |
| `FUENTES_Y_TRAZABILIDAD_POLOS_GASTRO.md` | Trazabilidad de fuentes. |
| `DELIMITACION_TEXTUAL_PRELIMINAR_POLOS_GASTRO.md` | Delimitación textual y límites. |
| `LECTURA_MAPA_CONCEPTUAL_POLOS_GASTRO.md` | Lectura del esquema conceptual. |
| `cartografia/fase4a/CARTOGRAFIA_USADA_FASE4A.md` | Nota de fuente cartográfica + atribución. |
| `fuentes_externas/ESTADO_FUENTES_POST_BUSQUEDA_MANUAL_CHATGPT.md` | Estado de evidencia por polo. |
| Fichas `fichas_polos/*.md` | Detalle por polo. |

## 2. CSVs que alimentan tablas

| CSV | Tabla del informe |
| --- | --- |
| `universo_informe_polos_gastro.csv` | Tabla maestra (polo, grupo, evidencia, decisión). |
| `base_delimitacion_preliminar_polos_gastro.csv` | Delimitación textual + precisión + comunas. |
| `base_cartografica_visual_polos_gastro.csv` | Qué se muestra en el mapa y cómo. |
| `fuentes_por_familia_territorial.csv` | Agrupación por familia. |
| `fuentes_externas_polos_gastro.csv` (92) | Anexo de fuentes con trazabilidad. |
| `matriz_validacion_polos_gastro.csv` | Validación documental (anexo metodológico). |

## 3. Visuales que entran (cuerpo)

- `graficos/fase4a/universo_polos_por_grupo_v2.png`
- `graficos/fase4a/precision_delimitacion_polos_v2.png`
- `graficos/fase4a/familias_territoriales_polos_v2.png`
- `graficos/fase4a/mapa_conceptual_polos_gastro_resumido_v2.png`
- `graficos/fase4a/mapa_estatico_caba_polos_gastro_nucleo_v1.png`

## 4. Visuales que quedan internos / anexo

- `graficos/fase4a/mapa_estatico_caba_polos_gastro_v1.png` (completo → anexo).
- `graficos/fase4a/mapa_conceptual_polos_gastro_completo_v2.png` (anexo / interno).
- PNG de la fase anterior (`graficos/*.png` sin sufijo): histórico interno.

## 5. Estructura página por página (tentativa)

1. **Portada** — título, fecha de corte, área, advertencia de alcance.
2. **Resumen ejecutivo** — objetivo, universo (32), hallazgos validados, límites.
3. **Qué es un polo gastronómico** — definición operativa (barrio/corredor/avenida/subpolo/zona).
4. **Cómo se construyó el universo** — fuentes (semilla, oficial, periodística, datos abiertos),
   criterios de grupo y evidencia.
5. **Mapa territorial** — `mapa_estatico_caba_nucleo_v1` + nota metodológica.
6. **Esquema conceptual** — `mapa_conceptual_resumido_v2`.
7. **Universo por grupo y precisión** — gráficos `universo_v2` y `precision_v2`.
8. **Familias territoriales** — `familias_v2` + lectura por familia.
9. **Polos consolidados (núcleo)** — 6 casos.
10. **Zonas relevantes** — 5 casos.
11. **Emergentes / candidatos** — 9 casos.
12. **Anexos** — anexo de barrios/casos (8), locales destacados (cualitativo), mapa completo.
13. **Limitaciones metodológicas**.
14. **Próximos pasos**.
15. **Anexo de fuentes** — tabla de trazabilidad.

## 6. Qué falta redactar

- Texto de todas las secciones (hoy son esqueleto + insumos).
- Resumen ejecutivo definitivo.
- Lectura narrativa por familia y por polo del núcleo.
- Redacción de límites y advertencias para jefatura (tono DataGastro).

## 7. Qué falta validar

- Las 5 URLs con `requiere_revision_url` (clarin.com / GCBA) — verificación manual.
- Revisión manual de los 3 matches de baja confianza del piloto Google Places.
- Confirmar tratamiento final de García del Río (anexo) y de los casos `no_incluir`.

## 8. Riesgos metodológicos a mencionar en el informe

- Universo defendible ≠ padrón de locales activos.
- Barrios/comunas = referencia territorial, no delimitación de polos.
- 16 polos de precisión baja + 2 sin delimitación → sin polígonos de polos.
- Fuentes turísticas/periodísticas validan identidad, no delimitación oficial.
- Google Places: experimental, sesgo comercial, no usado en el mapa.

## 9. Recomendación para Fase 5

- Redactar un **primer borrador en Markdown** siguiendo la estructura de la sección 5, con los
  visuales `fase4a/` ya insertados como referencias.
- Mantenerlo en `docs/polos_gastro/` (no PDF) hasta revisión de Diego.
- No generar PDF ni publicar hasta cerrar validaciones pendientes (sección 7).
