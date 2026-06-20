# Casas y fábricas de pastas en CABA — Padrón candidato integrado

**Estado: PADRÓN CANDIDATO (no oficial). Requiere revisión manual antes de presentarse como definitivo.**

Documento de diagnóstico que cruza tres fuentes para maximizar la cobertura de casas/
fábricas/locales de venta de pastas en la Ciudad de Buenos Aires, **incluyendo
explícitamente casas de barrio y locales independientes**, no solo cadenas.

## Fuentes y su naturaleza (no se mezclan sin aclarar)

- **AGC / F02 — registro administrativo oficial estricto.** Habilitaciones aprobadas bajo
  rubro de elaboración de pastas. Es oficial, pero **administrativo y estricto**: una
  habilitación **no implica un local activo hoy**.
- **OpenStreetMap — relevamiento abierto auxiliar.** Colaborativo, no oficial, no verificado.
- **Google Places API — padrón candidato operativo no oficial.** Refleja oferta operativa,
  pero no es un registro oficial.

El cruce es un **padrón candidato**, no un padrón oficial.

## Resultado integrado

| Métrica | Valor |
|---|---|
| **Candidatos únicos** | **264** |
| Descartados (restaurantes/bares/pizzerías, preservados aparte) | 57 |
| Detectados por Google | 152 |
| Detectados por OSM | 153 |
| Detectados por AGC | 11 |
| **Multifuente (≥2 fuentes)** | 52 |
| Cadenas | 90 |
| **Independientes** | **174** |
| En revisión manual prioritaria | 45 |

### Clasificación integrada

| Clase | Cantidad | Lectura |
|---|---|---|
| `A_integrado_multifuente` | 36 | Confirmado por ≥2 fuentes (mayor confianza). |
| `A_google_probable` | 70 | Candidato operativo (solo Google A). |
| `A_osm_auxiliar` | 102 | Auxiliar (solo OSM). |
| `A_agc_oficial_estricto` | 11 | Oficial administrativo (no implica local activo). |
| `B_revision_manual` | 45 | Dudosos / posibles faltantes: **no se descartan**. |

## Distribución territorial

**Top comunas (cantidad):** Comuna 14 (34), Comuna 13 (34), Comuna 6 (25), Comuna 12 (24), Comuna 2 (23).

**Top barrios (cantidad):** Palermo (34), Caballito (25), Recoleta (23), Belgrano (23), Villa Urquiza (19).

**Mayor densidad por km² — comunas:** Comuna 6 (3.65), Comuna 2 (3.58), Comuna 5 (3.00), Comuna 13 (2.29), Comuna 14 (2.14).

**Mayor densidad por km² — barrios:** Almagro (4.20), Caballito (3.65), Recoleta (3.58), Colegiales (3.49), Villa Urquiza (3.49).

Densidad = candidatos / área oficial km² (geometrías GCBA). No se calcula densidad por
habitante (falta dataset de población en el proyecto). Comunas con baja cobertura (≤2): Comuna 8.

## Cadenas e independientes

El padrón **no prioriza franquicias**. Las cadenas (90 sucursales) sirven para control de
cobertura; el núcleo del análisis son las **174 casas independientes / de barrio**.
Principales cadenas detectadas (control de cobertura): La Juvenil, Multipasta, Caprizzi,
Master Pastas, Pastas Mazzeo, Milena Pastas Artesanales.

> Nota: el conteo de sucursales por cadena puede estar **sobreestimado** cuando una misma
> sucursal aparece en dos fuentes con direcciones algo distintas y no se fusionó, o
> **subestimado** si dos sucursales reales quedaron muy cerca. Es parte de lo que exige la
> revisión manual.

## Límites (leer antes de usar)

- Es un **padrón candidato no oficial**; el número final exige **revisión manual**.
- AGC mide **habilitaciones**, no locales activos.
- OSM y Google **no son padrones oficiales**.
- La deduplicación entre fuentes es heurística (nombre + distancia + similitud); puede
  dejar duplicados o separar sucursales. Ver `deduplicacion_fuentes` y `revision_manual_prioritaria`.
- Los `B_revision_manual` y los C marcados como *posible faltante* **se conservan** para revisión;
  no desaparecen del análisis.

## Próximos pasos sugeridos

1. Revisión manual de los 45 `B_revision_manual` y de los C *posible faltante*.
2. Validar fusiones dudosas de cadenas (especialmente La Juvenil).
3. Sumar población por comuna/barrio para densidad por habitante.
4. Recién con el padrón validado, evaluar (con aprobación) el PDF final y/o el cruce con el pipeline.
