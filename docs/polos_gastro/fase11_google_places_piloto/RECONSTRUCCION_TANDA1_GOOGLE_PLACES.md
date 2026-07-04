# Reconstrucción de la Tanda 1 real — Google Places (PolosGastro, Fase 11)

Fecha de auditoría: 2026-07-02. Documento interno. Reconstruye qué ejecutó Copilot en la
primera tanda real de Google Places, sin ejecutar nuevas llamadas ni tocar la API.

> Esta reconstrucción se hace **por lectura de artefactos** (scripts y CSV ya generados). No se
> corrió ningún comando, no se llamó a la API, no se leyó ninguna API key ni `.env`.

## 1. Qué script se ejecutó

`scripts/polos_gastro/google_places/places_piloto_locales.py --execute`

Es un experimento **aislado**, fuera del pipeline F01–F05. El propio encabezado del script y su
README lo marcan como no productivo. Confirmado por el QA de Copilot
(`QA_TANDA_1_GOOGLE_PLACES.md`, línea 8).

## 2. Desde qué carpeta e insumo tomó los datos (hallazgo importante)

El script **no** leyó los insumos de Fase 10 ni de Fase 11 preparación. Su constante interna es:

```
SEED = ROOT / "outputs" / "polos_gastro" / "locales_destacados_por_polo_seed.csv"
```

Es decir, tomó los locales desde **`outputs/polos_gastro/locales_destacados_por_polo_seed.csv`**,
filtró por `NUCLEO_NOMBRES` (Palermo, Puerto Madero, San Telmo, Recoleta) y cortó en los primeros
`limit` = 10 registros. Como el seed empieza por Palermo, los 10 consultados fueron LG001–LG010
(todos de Palermo).

Consecuencia: la tanda **no** usó la tabla preparada de Fase 11
(`locales_semilla_preparados_para_google_places.csv`), que tiene queries mejores con hints de
barrio y estrategia de match. Usó queries crudas del tipo
`"<nombre>, Palermo (Soho, Hollywood y Las Cañitas), CABA, Argentina"`.

Los 10 locales **sí** son trazables al documento semilla: los 10 existen en el seed y en la tabla
preparada de Fase 11. **Ninguno está fuera de semilla.** (Ver `auditoria_origen_tanda1.csv`.)

## 3. Inputs efectivos

- Fuente de locales: `outputs/polos_gastro/locales_destacados_por_polo_seed.csv` (10 primeras filas
  de Palermo).
- API key: leída de entorno o `.env` (el script nunca la imprime; solo reporta "presente/ausente").
- Endpoint: Places API (New) Text Search, `maxResultCount: 1`, FieldMask mínimo **sin** location
  (por eso no hay lat/lon).

## 4. Outputs generados

| Archivo | Ubicación | Contenido |
|---|---|---|
| Resultados crudos experimento | `outputs/polos_gastro/experimentos_google_places/locales_places_piloto_resultados.csv` | 10 filas con `place_id`, nombre Google, dirección, tipos, business_status |
| Queries (dry-run refresco) | `outputs/polos_gastro/experimentos_google_places/locales_places_piloto_queries.csv` | 10 queries, sin datos Google |
| Legacy dry-run | `outputs/polos_gastro/experimentos_google_places/locales_places_piloto.csv` | 10 queries dry-run |
| Interno Fase 11 | `outputs/polos_gastro/fase11_google_places_piloto/tablas/locales_places_piloto_resultados_interno.csv` | 10 filas con `google_place_id_interno`, columnas rating/user_ratings_total (vacías), lat/lon (vacías) |
| Sanitizado (publicable) | `outputs/polos_gastro/fase11_google_places_piloto/tablas/locales_places_piloto_resultados_sanitizado.csv` | 10 filas sin place_id/rating/user_ratings_total |

Los archivos interno y sanitizado de Fase 11 **no los genera el script** (el script solo escribe en
`experimentos_google_places/`). Fueron derivados por Copilot en un paso manual/aparte no
documentado en el script.

## 5. Cuántas consultas reales hizo

10 consultas reales (una por local, `maxResultCount: 1`). 10 matches, 0 errores, 0 sin
coincidencia. Consistente con el QA de Copilot.

## 6. ¿Respetó el hard cap?

Sí. `MAX_LOCALES_HARD_CAP = 10` sin modificar. Se consultaron exactamente 10 locales. El cap no fue
tocado (confirmado por lectura del script actual).

## 7. Señales de ruta/comando raro

- **Insumo equivocado**: usó el seed del experimento aislado, no la tabla preparada de Fase 11. No
  es "ruta rara" en sentido de path fuera del repo, pero **sí** es un desalineamiento de pipeline:
  la Fase 11 preparación quedó sin usar.
- **Queries pobres**: la query incluye el nombre largo del polo dentro del textQuery
  (`"Osaka, Palermo (Soho, Hollywood y Las Cañitas), CABA, Argentina"`), lo que degrada el match
  (Google devolvió "Osaki Sushi", "Artemisia", "Somos OP").
- **Encoding en consola/QA**: "Ni�o Gordo" / "Ni o Gordo" es mojibake de salida por consola sin
  UTF-8; **el dato en los CSV está correcto** ("Niño Gordo").

## 8. ¿Outputs en la carpeta esperada o dispersos?

**Dispersos.** Conviven dos ubicaciones:
- `outputs/polos_gastro/experimentos_google_places/` (lo que escribe el script).
- `outputs/polos_gastro/fase11_google_places_piloto/tablas/` (derivados interno/sanitizado).

El resultado crudo con `place_id` vive en `experimentos_google_places/`, fuera de la carpeta de
Fase 11 piloto. Recomendable consolidar y dejar claro cuál es la fuente de verdad.

## 9. ¿Archivos duplicados o inconsistentes?

- **Duplicación de queries**: `locales_places_piloto_queries.csv` y `locales_places_piloto.csv`
  (legacy) tienen el mismo contenido dry-run.
- **Inconsistencia de nombres de local**: el seed usa `Aldo’s (Palermo)` y `Oporto`; el QA de
  Copilot los renombró erróneamente como `LG008_ARTEMISIA` y `LG010_SOmos_OP` tomando el
  **nombre que devolvió Google** como si fuera el local consultado. Es un error de documentación
  del QA, no de los datos.
- **Contradicción aceptado vs revisión**: el QA dice "Matches aceptados (10): 10", pero en el CSV
  sanitizado las 10 filas tienen `aceptado_para_mapa = no`. "10 matches" no equivale a "10
  aceptados para mapa". Ninguno quedó aceptado para mapa.

## 10. Conclusión de la reconstrucción

La tanda 1 se ejecutó de forma segura (cap respetado, sin exponer key, sin lat/lon en publicable),
pero **metodológicamente desalineada**: usó el insumo del experimento aislado en vez de la tabla
preparada de Fase 11, con queries pobres que produjeron 3 matches erróneos (Osaka→Osaki,
Aldo's→Artemisia, Oporto→Somos OP). El QA de Copilot documentó mal el origen (confundió
nombre-Google con nombre-semilla) y sobrevendió el resultado ("10 aceptados").

Ver decisión en `DECISION_TANDA2_GOOGLE_PLACES.md`.
