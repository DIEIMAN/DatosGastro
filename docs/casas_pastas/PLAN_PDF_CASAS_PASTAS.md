# Plan del PDF — Casas y fábricas de pastas en CABA

Estructura sugerida (6–10 páginas) para el informe institucional. Usa **solo** la versión
sanitizada (`outputs/casas_pastas_reporte/`). Tono institucional, sobrio, sin lenguaje de IA;
separar hallazgos de límites; no decir "locales activos"; no presentar OSM como padrón oficial.

| Pág. | Sección | Contenido | Insumo (sanitizado) |
| --- | --- | --- | --- |
| 1 | **Portada** | Título, área, fecha, "documento de diagnóstico — datos públicos AGC + OSM auxiliar" | — |
| 2 | **Resumen ejecutivo** | 5–8 bullets: 10 establecimientos en registro AGC estricto; OSM auxiliar sugiere ~138; diferencia = fuente/definición, no error; principales límites | `tabla_resumen_general.csv` |
| 3 | **Metodología y fuentes** | Definición estricta (A/B/C); fuentes (AGC/F02 oficial, OSM auxiliar, geometrías GCBA); qué se excluyó (restaurantes/italianos) | `comparacion_agc_osm.csv` |
| 4 | **Mapa de nodos** | Mapa agregado sin etiquetas; aclarar AGC oficial vs OSM aparte | `mapa_nodos_agregado.png` |
| 5 | **Distribución por comuna** | Tabla + barras; aclarar que son habilitaciones, no locales activos | `top_comunas_cantidad.csv` |
| 6 | **Distribución por barrio** | Tabla + barras (geolocalizados) | `top_barrios_cantidad.csv` |
| 7 | **Densidad por km²** | Comuna y barrio; explicar denominador (área oficial) y sensibilidad por N chico | `top_comunas_densidad.csv`, `top_barrios_densidad.csv` |
| 8 | **Comparación AGC vs OSM** | Los tres planos: registro oficial / relevamiento abierto auxiliar / pendiente de validación | `comparacion_agc_osm.csv` |
| 9 | **Limitaciones** | L1–L7; foco en "habilitaciones ≠ locales activos" y rubro angosto | `limitaciones_metodologicas.csv` |
| 10 | **Próximos pasos** | Google Places API oficial (plan), validación manual de B/OSM, sumar población para per cápita | INFORME §10 |

## Reglas de armado

- **Fuente de datos**: solo `outputs/casas_pastas_reporte/` (sanitizada). Nunca la carpeta cruda.
- **Nada de**: razón social, nombres de personas, direcciones individuales, teléfonos, mails, CUIT.
- **Etiquetas**: "registro administrativo oficial" (AGC), "relevamiento abierto auxiliar" (OSM),
  "pendiente de validación".
- **Lenguaje**: habilitaciones AGC, oferta registrada, puntos OSM — **no** "locales activos".

## Generación técnica (cuando se apruebe)

- El proyecto ya ignora `outputs/*.pdf` y `outputs/*.html` en Git (no se versionan PDFs).
- Opción simple: componer el PDF desde este plan + las figuras/tablas sanitizadas (p. ej. con
  un notebook o un script de armado dedicado). Confirmar antes de generarlo.
- No incluir el GeoJSON de puntos si hay cualquier duda; basta el `mapa_nodos_agregado.png`.
