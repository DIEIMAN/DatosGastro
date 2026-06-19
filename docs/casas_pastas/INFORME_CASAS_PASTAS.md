# Casas y fábricas de pastas en CABA — Informe

Análisis territorial de **casas/fábricas de pastas** (elaboración y venta de pastas frescas/secas,
pastificios), separado del análisis general de gastronomía. Bloque independiente del proyecto.

> Universo bajo análisis: comercios cuyo **rubro principal** es producción o venta de pastas.
> **No** incluye restaurantes italianos, trattorias, pizzerías, bares ni gastronómicos generales.

## 1. Objetivo

Construir el padrón analítico más completo posible de casas/fábricas de pastas en la Ciudad,
con geolocalización, comuna, barrio, densidad y distribución territorial, usando primero fuentes
ya presentes en el proyecto y fuentes públicas abiertas.

## 2. Definición estricta (universos A / B / C)

- **A — estricto confirmado**: rubro/nombre indica claramente casa/fábrica/elaboración/venta de
  pastas (p. ej. rubro AGC "Elaboración de pastas alimenticias frescas/secas", "pastificio",
  "casa de pastas").
- **B — probable**: indicios fuertes no concluyentes (nombre con "pastas" pero rubro genérico).
- **C — dudoso/descartado**: mención ambigua de pasta, o restaurante/italiano/pizzería/bar.

El análisis principal usa **A**. A+B solo se muestra por separado, nunca mezclado.

## 3. Fuentes usadas

| Fuente | Rol | Detalle |
| --- | --- | --- |
| **F02 — Habilitaciones aprobadas AGC** (raw, 2015–2025) | **Principal** | Rubro oficial de elaboración de pastas. Son habilitaciones/registros administrativos, **no** locales activos. |
| F01 — Oferta gastronómica (raw) | Secundaria | Orientada a restaurantes; aporta ~0 casas de pastas (filtro estricto). |
| geo_comunas / geo_barrios (GCBA) | Geometrías | Asignación territorial y área km². |
| geo_cache / dim_ubicacion | Geocodificación | lat/lon ya existentes en el proyecto; sin servicios externos pagos. |
| OpenStreetMap / Overpass | **Auxiliar** | Contraste abierto; colaborativo e incompleto. No es padrón oficial. |
| Google Places | Solo **plan** | Sin ejecutar API (ver Parte 9). |

Trazabilidad por registro en `outputs/casas_pastas/casas_pastas_maestro.csv` (fuente, archivo,
id original, rubro, patrón detectado, calidad geo, etc.).

## 4. Resultados — universo A (oficial)

- **Universo A (AGC, deduplicado): 10 establecimientos** distintos de casas/fábricas de pastas.
- Geolocalizados: **9 de 10**.
- Provienen de **152 filas** de habilitación AGC (108 "pastas frescas" + 44 "pastas secas"),
  que tras deduplicar por establecimiento (nombre + calle) dan 10 establecimientos.
- **Universo B (probable): 1** ("Farfalla Pastas", rubro genérico de comercio minorista).
- F01 aportó 0 a A (solo 1 registro ambiguo "La Pasta", restaurante → C).

> El número es bajo y es un **hallazgo en sí mismo**: el rubro AGC "elaboración de pastas
> alimenticias" es angosto y muchas casas de pastas operan bajo rubros genéricos de comercio
> minorista o no figuran con ese rubro. Ver contraste con OSM (sección 7) y límites (sección 9).

## 5. Distribución territorial (universo A)

### Por comuna (cantidad)
Comuna 13 = 2; comunas 2, 4, 5, 7, 8, 9, 10, 11 = 1 cada una. Resto = 0.
(`casas_pastas_por_comuna.csv`)

### Por barrio (cantidad, geolocalizados)
1 establecimiento en cada uno de: Barracas, Belgrano, Colegiales, Floresta, Mataderos,
Parque Chacabuco, Recoleta, Villa Devoto, Villa Lugano. (`casas_pastas_por_barrio.csv`)

### Densidad por km²
- **Comuna**: Comuna 2 (0.155), Comuna 5 (0.150), Comuna 13 (0.135) encabezan.
  (`casas_pastas_densidad_comuna.csv`)
- **Barrio** (geolocalizados): Colegiales (0.437), Floresta (0.431), Parque Chacabuco (0.261).
  (`casas_pastas_densidad_barrio.csv`)

> Densidad = establecimientos / área km² (área oficial GCBA). Con N tan chico, los rankings de
> densidad son **muy sensibles** a cada caso y deben leerse como indicativos, no concluyentes.

## 6. Evolución temporal (habilitaciones AGC, universo A)

Por año de disposición de habilitación: **2015 = 3, 2016 = 6, 2017 = 1**.
(`casas_pastas_habilitaciones_por_anio.csv`)

> Mide **habilitaciones AGC** vinculadas a casas/fábricas de pastas, **no** aperturas netas ni
> locales activos. No hay registros bajo este rubro estricto después de 2017 en la fuente.

## 7. Mapa y visualizaciones

En `outputs/casas_pastas/figuras/`:
`mapa_nodos_casas_pastas.png`, `ranking_por_comuna.png`, `ranking_por_barrio.png`,
`densidad_por_comuna.png`, `densidad_por_barrio.png`.
Capa de puntos: `outputs/casas_pastas/casas_pastas_maestro.geojson`.

## 8. Marco de lectura institucional (AGC vs OSM)

Para un informe institucional, los números deben leerse en **tres planos distintos**, sin
mezclarlos:

| Plano | Fuente | Qué es | Cantidad (A) |
| --- | --- | --- | --- |
| **Registro administrativo oficial** | AGC / F02 | Habilitaciones vinculadas a elaboración de pastas. **No** son locales activos. | **10** |
| **Relevamiento abierto auxiliar** | OpenStreetMap | Puntos mapeados por la comunidad con `shop=pasta` y equivalentes. **No** es padrón oficial ni está verificado. | **138** |
| **Pendiente de validación** | AGC B + OSM A/B | Indicios fuertes que requieren confirmación manual o API oficial antes de contarse. | 1 (B AGC) + OSM |

OSM clasifica **138 A** (132 con tag explícito `shop=pasta`), 15 B y 6 C en CABA
(`outputs/casas_pastas/osm_casas_pastas_candidatos.csv`).

> **La diferencia AGC (10) vs OSM (138) no debe leerse como un error**, sino como una **diferencia
> de fuente y de definición**: la habilitación AGC bajo el rubro estricto de pastas captura solo a
> quienes se habilitaron exactamente con ese rubro, mientras OSM refleja un universo operativo más
> amplio pero no oficial. Ambos son válidos en su plano. El número oficial es 10; el universo real
> probable es mayor y queda **pendiente de validación**.

## 8.b Versión publicable

La carpeta cruda `outputs/casas_pastas/` contiene razón social, direcciones e IDs individuales y
está **excluida de Git** (`.gitignore`). Para informe/PDF usar la versión **sanitizada** (solo
agregados, sin datos personales) en `outputs/casas_pastas_reporte/`:
`tabla_resumen_general.csv`, `top_comunas_cantidad.csv`, `top_barrios_cantidad.csv`,
`top_comunas_densidad.csv`, `top_barrios_densidad.csv`, `comparacion_agc_osm.csv`,
`limitaciones_metodologicas.csv`, `mapa_nodos_agregado.png`, `mapa_nodos_puntos.geojson`
(solo AGC, sin nombres).

## 9. Limitaciones

1. **AGC mide habilitaciones, no locales activos.** Un registro puede estar cerrado hoy.
2. **Rubro estricto angosto**: solo captura quienes se habilitaron exactamente como "elaboración
   de pastas alimenticias". Casas de pastas bajo rubros genéricos quedan fuera de A (algunas en B).
3. **Geocodificación**: se usó solo la caché local del proyecto; no se geocodificó con servicios
   externos pagos. 1 de 10 quedó sin punto (se contabiliza por comuna del registro).
4. **Sin población local**: no se pudo calcular "por 10.000 habitantes" (falta dataset de
   población por comuna/barrio en el proyecto). Queda pendiente.
5. **OSM** es incompleto y colaborativo; no reemplaza un padrón.
6. **N pequeño en A** → rankings sensibles; tomar como diagnóstico inicial, no como censo.

## 10. Próximos pasos

1. **Google Places API oficial** (plan en `google_places_plan_casas_pastas.csv`): ejecutar con
   autorización y presupuesto para ampliar cobertura (no scraping).
2. **Validación manual** del universo B y de los candidatos OSM A para promover a A confirmados.
3. Sumar **dataset de población** por comuna/barrio para densidad per cápita.
4. Revisar rubros AGC adicionales (comercio minorista de productos alimenticios con nombre de
   pastas) para recuperar casas de pastas registradas bajo rubros genéricos.
5. Recién con A validado y ampliado, evaluar (con aprobación) un cruce hacia el pipeline.

Ver `NOTAS_METODOLOGICAS.md` para el detalle de criterios, patrones y trazabilidad.
