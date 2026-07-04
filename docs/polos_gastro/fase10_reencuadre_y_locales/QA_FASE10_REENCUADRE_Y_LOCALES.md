# QA Fase 10 - Reencuadre y locales semilla

Fecha de cierre: 2026-07-02.

## 1. Archivos creados

Documentacion:

- `docs/polos_gastro/fase10_reencuadre_y_locales/REENCUADRE_METODOLOGICO_POLOS_GASTRO_FASE10.md`
- `docs/polos_gastro/fase10_reencuadre_y_locales/VOCABULARIO_Y_CAMBIOS_BORRADOR_4.md`
- `docs/polos_gastro/fase10_reencuadre_y_locales/LECTURA_UNIVERSO_SEMILLA_FASE10.md`
- `docs/polos_gastro/fase10_reencuadre_y_locales/RESUMEN_LOCALES_SEMILLA_FASE10.md`
- `docs/polos_gastro/fase10_reencuadre_y_locales/ESQUEMA_GOOGLE_PLACES_POLOS_FASE10.md`
- `docs/polos_gastro/fase10_reencuadre_y_locales/PLAN_INVESTIGACION_COMPLEMENTARIA_POLOS_FASE10.md`
- `docs/polos_gastro/fase10_reencuadre_y_locales/ESTRUCTURA_PROPUESTA_BORRADOR_4_REENCUADRADO.md`
- `docs/polos_gastro/fase10_reencuadre_y_locales/QA_FASE10_REENCUADRE_Y_LOCALES.md`

Tablas:

- `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/universo_polos_semilla_fase10.csv`
- `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/locales_semilla_polos_fase10.csv`
- `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/schema_locales_google_places_fase10.csv`

## 2. Archivos modificados

No se modificaron archivos preexistentes. Solo se crearon carpetas y archivos nuevos de Fase 10.

## 3. Tablas creadas

- Universo de polos semilla: 22 polos o areas de trabajo.
- Locales semilla: 106 menciones local-polo.
- Esquema Google Places: 20 campos propuestos.

## 4. Alcance verificado

| Control | Resultado |
| --- | --- |
| Cantidad de polos procesados | 22 |
| Cantidad de menciones local-polo extraidas | 106 |
| Se llamo a Google Places | No |
| Se uso API key | No |
| Se imprimio API key | No |
| Se genero raw de Google Places | No |
| Se tocaron datos fuente originales | No |
| Se toco Borrador 3 | No |
| Se toco Borrador 2 | No |
| Se tocaron Cafecito, Mercados o Casas de Pastas | No |
| Se genero PDF | No |
| Se genero DOCX | No |
| Se generaron mapas finales | No |
| Se aplico Design System | No |
| Se hizo commit | No |
| Se hizo push | No |
| Se hizo staging o git add | No |

## 5. Riesgos pendientes

- Los locales semilla son menciones preliminares y no prueban vigencia operativa.
- Varios polos no tienen locales explicitos en el documento semilla y requieren busqueda
  complementaria.
- Belgrano necesita tratamiento diferenciado por subzonas.
- Corrientes y Abasto comparten un mismo bloque de referencias y requieren nota cruzada.
- Corredores como Costanera Norte, DoHo, Avenida Caseros, Avenida Boedo, Federico Lacroze y Villa
  Pueyrredon / Avenida San Martin necesitan recorte textual antes de mapas.
- Si se autoriza Google Places, deben mantenerse separados campos internos y publicables.

## 6. Control de privacidad

Se revisaron los archivos creados bajo `docs/polos_gastro/fase10_reencuadre_y_locales/` y
`outputs/polos_gastro/fase10_reencuadre_y_locales/`.

Resultado:

- API keys de Google: sin hallazgos.
- Emails: sin hallazgos.
- Telefonos: sin hallazgos.
- DNI: sin hallazgos.
- Links privados de Drive/Docs: sin hallazgos.
- CUIT: los hits del patron amplio corresponden a falsos positivos por la palabra "circuito".
- `place_id`: aparece solo como campo interno esperado (`google_place_id_interno`) y como
  advertencia de no publicacion.

## 7. Proximos pasos recomendados

1. Revision humana del reencuadre metodologico.
2. Validar el mapeo editorial propuesto para Borrador 4.
3. Revisar nombres de locales, sucursales y subzonas ambiguas.
4. Preparar queries de geolocalizacion sin ejecutar API hasta autorizacion explicita.
5. Ejecutar investigacion complementaria por polos con prioridad alta.
6. Redactar Borrador 4 solo como copia nueva, sin modificar Borrador 3.
