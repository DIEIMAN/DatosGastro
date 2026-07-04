# QA - Capa objetiva Fase 8 fuerte

Fecha de consulta: 2026-07-01.

## Fuentes usadas

- F01 oferta y establecimientos gastronomicos: 2823 filas leidas.
- F02 habilitaciones gastronomicas procesadas: 44169 filas leidas.
- Dimension ubicacion: apoyo para comuna de F02.
- Borrador 2 y universo Fase 5: solo lectura para cruce metodologico.

## Filas procesadas

| archivo | filas |
| --- | --- |
| oferta_gastronomica_por_barrio_fase8_fuerte.csv | 47 |
| oferta_gastronomica_por_comuna_fase8_fuerte.csv | 15 |
| habilitaciones_gastronomicas_por_comuna_fase8_fuerte.csv | 16 |
| indice_senal_objetiva_por_barrio_fase8_fuerte.csv | 47 |
| indice_senal_objetiva_por_comuna_fase8_fuerte.csv | 15 |
| polos_vs_capa_objetiva_fase8_fuerte.csv | 32 |
| insumo_mapa_contexto_objetivo_fase8_fuerte.csv | 47 |

## Privacidad

Se generaron solo agregados por barrio/comuna y tablas metodologicas. No se exportaron nombres de
establecimientos, direcciones individuales, telefonos, correos, identificadores fiscales/personales
ni identificadores tecnicos de plataformas privadas.

Archivo de QA automatico:

- `outputs/polos_gastro/fase8_fuerte/qa/qa_privacidad_fase8_fuerte.csv`

Resultado automatico: 0 alertas.

## Confirmaciones

- [x] No se uso Google Places.
- [x] No se llamaron APIs privadas.
- [x] No se tocaron datos fuente.
- [x] No se modifico `data/`.
- [x] No se modifico Borrador 2.
- [x] No se modificaron tablas de Fase 7.
- [x] No se modifico la validacion de Fase 8 liviana.
- [x] No se genero PDF.
- [x] No se genero DOCX.
- [x] No se generaron mapas.
- [x] No se generaron graficos.
- [x] No se generaron dashboards.
- [x] No hubo commit, push ni staging.

## Nota

La ausencia de alertas automaticas no reemplaza revision humana antes de publicar. Esta fase queda
como insumo interno.
