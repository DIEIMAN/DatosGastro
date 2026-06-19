# Skill 05 — Geodatos y territorio

Cómo tratar direcciones, ubicación y análisis territorial sin sacar conclusiones falsas.

> Regla central, repetida a propósito: **geocodificar una dirección NO prueba que el local exista
> ni que esté activo hoy.** Solo ubica un punto declarado en el espacio.

## 1. Jerarquía territorial CABA

- **Comuna** (1–15): unidad administrativa. Útil para agregados estables.
- **Barrio**: 48 barrios oficiales. Más granular, más ruido en los límites.
- **Dirección**: calle + altura. Insumo para geocodificar; puede estar mal escrita, incompleta o
  desactualizada.
- **lat/lon**: par de coordenadas. Resultado de geocodificar o de la fuente.

## 2. Fuentes de geocodificación y su rol

| Fuente | Rol | Cuidado |
| --- | --- | --- |
| **USIG** (GCBA) | Normalización oficial de direcciones CABA, comuna/barrio | Fuente preferente para CABA; ver `src/geocode_usig.py`, `src/normalize_addresses.py` |
| **OSM / Overpass** | POIs abiertos de contraste | Cobertura heterogénea, depende de la comunidad; no es padrón oficial |
| **Google Places** | Oferta visible, coordenadas, estado del negocio | API paga, restricciones de TOS/almacenamiento; **no scraping**; no confirma habilitación |

- Preferir **USIG** para normalizar y asignar comuna/barrio dentro de CABA.
- OSM y Google se usan como **contraste/validación externa**, nunca como verdad de padrón.
- Registrar siempre: fuente de la coordenada, fecha de consulta y método (exacta/aproximada).

## 3. Densidad vs. volumen

- **Volumen**: cantidad absoluta de puntos en una zona. Sesgado por tamaño del área y por
  intensidad de relevamiento.
- **Densidad**: puntos por unidad de superficie o por habitante. Permite comparar zonas, pero
  amplifica errores en áreas chicas.
- No comparar volumen de una fuente con densidad de otra. Declarar siempre el denominador.

## 4. Sesgos territoriales a vigilar

- **Sesgo de cobertura**: OSM y reviews sobrerrepresentan zonas turísticas/mediáticas (Palermo,
  Recoleta, San Telmo) y subrepresentan barrios periféricos.
- **Sesgo de geocodificación**: direcciones ambiguas caen al centroide de calle/comuna y generan
  falsos clusters.
- **Sesgo de fuente**: un directorio de delivery no cubre locales sin delivery; un padrón de
  permisos no cubre locales sin permiso.
- **Sesgo temporal**: coordenadas viejas reflejan locales que pudieron cerrar.

## 5. Qué se puede afirmar y qué no

| Se puede afirmar | NO se puede afirmar |
| --- | --- |
| "X direcciones geocodificadas en la comuna N" | "Hay X locales activos en la comuna N" |
| "Y POIs gastronómicos visibles en OSM/Google" | "Y restaurantes habilitados y abiertos" |
| "Densidad de oferta **registrada/visible** por comuna" | "Densidad de locales **operando** hoy" |
| "Z habilitaciones aprobadas históricas con coordenada" | "Z negocios funcionando" |

Usar siempre el sustantivo que corresponde a lo que la fuente mide (ver skills 01 y 02):
oferta registrada, oferta visible, habilitaciones aprobadas, permisos, POIs — **no** "locales
activos".

## 6. Privacidad geográfica

- Una coordenada exacta + nombre + datos económicos puede reidentificar a un comercio.
- Para outputs sensibles, agregar a comuna/barrio y respetar umbral mínimo por celda (skill 03).
