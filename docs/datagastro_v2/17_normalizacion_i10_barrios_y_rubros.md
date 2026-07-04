# DataGastro V2 — Normalización interna de I10 (barrios y rubros)

> Etapa 3.5. Mejora de **calidad interna** de I10 antes de cualquier padrón. **No** se hicieron
> requests, **no** se usó API key, **no** se descargó nada, **no** se modificó el Excel original,
> **no** se dedupló contra fuentes externas, **no** se geocodificó, **no** se creó el padrón
> final. Pipeline V1 y casas de pastas intactos.

## 1. Qué se normalizó

Sobre los **2.480** registros minimizados de I10 (Etapa 3) se aplicó:

1. **Normalización de barrios** contra el catálogo oficial de CABA (48 barrios), tomado de la
   fuente local `data/raw/geo_barrios.geojson` (solo lectura). Se mapearon aliases, se detectaron
   valores genéricos, múltiples y de fuera de CABA.
2. **Clasificación tentativa de rubro** para hojas mixtas, vía reglas por nombre del local
   (uso interno; el nombre **no** se publica).

Configs creados (versionables, no sensibles):
- `config/v2/barrios_caba_aliases_v2.csv` (48 oficiales + 22 aliases + genéricos + fuera de CABA).
- `config/v2/reglas_desagregacion_i10_v2.csv` (reglas tentativas por hoja mixta).

## 2. Resultado de barrios

| estado_barrio | registros | % |
|---|---|---|
| normalizado | 1.380 | 55,6 |
| sin_barrio | 955 | 38,5 |
| pendiente_revision | 62 | 2,5 |
| ambiguo (CABA/Buenos Aires genérico) | 42 | 1,7 |
| fuera_caba_probable (GBA u otra) | 29 | 1,2 |
| multiple_barrio (varios en una celda) | 12 | 0,5 |

- **1.380 registros (55,6%)** quedaron mapeados a uno de los **48 barrios oficiales** (todos
  representados). Mejora sobre Etapa 3: aliases como *Palermo Hollywood*, *Las Cañitas*, *Boca*,
  *Devoto*, *Montserrat* o *La Paternal* se consolidan en su barrio oficial (p. ej. Palermo pasó
  de ~227 a 244).
- De los 1.525 registros que traían barrio en Etapa 3: 1.380 normalizados + 145 no resueltos
  (ambiguo/múltiple/fuera/pendiente).

## 3. Qué NO se pudo normalizar (barrios)

- **sin_barrio (955):** la celda venía vacía en origen.
- **ambiguo (42):** referencias genéricas a la ciudad ("CABA", "Buenos Aires") o no-barrios
  ("Todas las sucursales", "Tienda online").
- **fuera_caba_probable (29):** localidades del GBA u otras (Quilmes, Olivos, Ramos Mejía, etc.).
- **multiple_barrio (12):** una celda con varios barrios ("Palermo - San Telmo",
  "Colegiales/Palermo/Recoleta").
- **pendiente_revision (62):** texto que no mapeó (nombres de calles, siglas, tipeos varios).

`barrio` es **texto libre** sin normalizar en origen; el catálogo de aliases cubre los casos
frecuentes pero no la cola larga de ruido.

## 4. Resultado de rubros

| estado_rubro | registros |
|---|---|
| directo_hoja (hoja de rubro clara) | 1.224 |
| desagregado_tentativo (hoja mixta, match por nombre) | 391 |
| pendiente_desagregar (hoja mixta, sin match) | 587 |
| pendiente_taxonomica (Hamburguesería/Foodtrucks/Emprendimientos) | 278 |

### 4.1 Desagregación de hojas mixtas (clasificación tentativa)
- **Café y dulce:** cafeterías 216, pastelerías 30, cafeterías de especialidad 22,
  chocolaterías 11, confiterías 9, panaderías 8; **406 sin match** (quedan pendientes).
- **Pizza, empanadas y pasta:** pizzerías 50, casas de pastas 19, empanadas 19, rotiserías 7;
  **181 sin match** (quedan pendientes).

La clasificación es **tentativa** (confianza media/baja): se basa en términos del nombre del
local, no en verificación. Si no hay match claro, **no se fuerza**: queda pendiente.

## 5. Cómo se trataron las hojas no resolubles

`Hamburguesería` (131), `Foodtrucks` (82) y `Emprendimientos` (65) → **278** registros marcados
`pendiente_revision_taxonomica`. **No se excluyen**: esperan una decisión taxonómica (crear
subcategoría nueva, p. ej. hamburgueserías; tratar foodtrucks como formato itinerante
transversal; clasificar emprendimientos caso por caso).

## 6. Limitaciones

- **Una sola fuente (I10):** la confianza sube solo al cruzarse con otras (multifuente).
- **Sin verificación:** la desagregación por nombre es heurística; puede haber falsos positivos.
- **Sin comuna para no-normalizados:** solo los barrios oficiales traen comuna.
- **38,5% sin barrio:** limita el análisis territorial de I10 por sí solo.
- **Posibles duplicados** intra-I10 (aún no deduplicado).

## 7. Por qué esto sigue sin ser padrón final

No se construyó `dim_establecimiento_candidato`. No se dedupló (ni intra-I10 ni contra
F01/F02/OSM/Google). No se geocodificó. I10 sigue siendo **fuente interna de validación /
catálogo candidato**, no padrón ni prueba de local activo.

## 8. Próximos pasos

1. Afinar reglas de desagregación y/o revisión manual de los 587 pendientes mixtos.
2. Resolver taxonómicamente Hamburguesería/Foodtrucks/Emprendimientos (278).
3. Ampliar aliases de barrio para reducir los 62 pendientes; decidir exclusión de los 29 fuera
   de CABA.
4. Confirmar con DGDGAS propietario, fecha de corte y grano antes de integrar.
5. Recién entonces: deduplicación intra-I10 y, en etapa posterior, resolución de entidad
   multifuente hacia el padrón candidato.

## 9. Reproducibilidad

```bash
python src/v2/build_i10_dgdgas_staging.py    # staging interno minimizado (Etapa 3)
python src/v2/normalize_i10_dgdgas.py        # normalizacion interna (Etapa 3.5)
python src/v2/validate_v2_setup.py           # valida setup, columnas y privacidad
```

Todo offline. Nombres y direcciones permanecen solo en `outputs/v2/internal/` (gitignored).
