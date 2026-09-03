# Reglas del universo gastronómico V1 — registro completo

**Fecha:** 2026-07-08 · **Carácter:** experimental. Documenta TODAS las reglas usadas por
`scripts/polos_gastro/experimentos/pipeline_microzonas_v1/s01_construir_universo.py`.
Los conteos provienen de la corrida 2026-07-08 (`universo/log_reglas_universo_v1.json`).

**Semántica (guardrails 3 y 5):** una *entidad* es un lugar con evidencia documental
gastronómica en alguna fuente pública integrada (oferta registrada F01 y/o habilitaciones
históricas F02). El universo NO mide "locales activos" y ninguna salida puede describirlo así.

## Fuentes y filtros de entrada

| Regla | Detalle | Efecto en la corrida |
|---|---|---|
| R1 | F01 = `fact_establecimiento` con `es_gastronomico = si`, join a `dim_ubicacion` | 2.704 filas de 2.823 |
| R2 | F02 = `fact_habilitacion_gastronomica` con `es_gastronomico = si`, excluyendo categorías que no son locales a la calle: Catering (5.860), Mercado (2), Feria (1) | 38.306 filas de 44.169 |

## Colapso y deduplicación

| Regla | Detalle | Efecto |
|---|---|---|
| R3 | F02 se colapsa a **una entidad por `id_ubicacion`** (dirección normalizada USIG). Atributos conservados: categorías con conteo, nº de filas, nº de rubros, ventana de fechas, bandera `solo_evidencia_2025_sin_fecha` | 38.306 filas → 7.866 ubicaciones (79,5 % de redundancia interna; el recurso 2025 aporta solo 867 ubicaciones) |
| R4a | Dedup interna F01: mismo nombre normalizado + misma `id_ubicacion` | 12 fusiones |
| R4b | Dedup interna F01: mismo nombre normalizado a ≤ 40 m (mismo local geocodificado por cadenas de dirección distintas; a más de 40 m se asume sucursal) | 17 pares fusionados → F01 queda en 2.687 entidades |
| R5a | Cruzada F02→F01: misma `id_ubicacion` | 21 fusiones (coincide con el perfilado de diseño) |
| R5b | Cruzada: misma `direccion_normalizada` textual | 80 fusiones |
| R5c | Cruzada: distancia ≤ 15 m **y** categoría compatible (tabla de compatibilidad explícita en `s01`, p. ej. café≈pastelería, restaurante≈parrilla; USIG geocodifica a parcela: 15 m ≈ misma parcela o lindera) | 713 fusiones |
| R5d | Banda de revisión: 15–30 m con categoría compatible NO fusiona; marca `posible_duplicado_cercano_30m` | 497 entidades marcadas |
| R6 | Supervivencia: nombre y categoría de F01 (F02 no trae nombre comercial); mejor coordenada disponible; evidencia = unión con banderas `en_f01`/`en_f02` y fechas mín/máx | — |

**Normalización textual:** mayúsculas, sin acentos, sin puntuación, espacios colapsados.
**Identidad:** `id_entidad` = hash SHA-1 (10 hex) de dirección normalizada + nombre + categoría.
**Linaje:** `correspondencia_filas_fuente.csv` mapea cada fila fuente a su entidad (regenerable).

## Resultado

| Indicador | Valor |
|---|---|
| Filas fuente gastronómicas que entraron a resolución | 41.010 |
| **Entidades finales** | **9.739** (colapso del 76,3 %) |
| Solo F01 / solo F02 / ambas | 2.126 / 7.052 / 561 |
| Aptas para clustering (con coordenadas dentro de CABA) | 9.738 |

Dentro del rango 8.000–9.500 previsto por el diseño (doc 03 §7), apenas por encima porque
la fusión cruzada sin nombres en F02 es deliberadamente conservadora.

## Limitaciones asumidas (no defectos ocultos)

1. **F02 sin nombre comercial:** en una dirección con varios locales legítimos (galerías,
   patios) F02 aporta UNA entidad; y la fusión a ≤ 15 m puede unir vecinos de la misma
   categoría. Ambos errores son acotados y de signo conocido.
2. **Recurso F02-2025 defectuoso:** 25.289 filas → solo 877 direcciones únicas (28,8
   filas/dirección, duplicación masiva de origen) y sin fecha de habilitación en el mapeo
   actual. Entra colapsado y con bandera propia; su revisión de mapeo sigue pendiente.
3. **Recencia:** la evidencia fechada se concentra en 2016–2018. El universo describe
   concentración histórica de oferta registrada, no el paisaje actual.
4. **Umbrales no calibrados contra verdad de campo:** 40 m (R4b), 15 m (R5c) y 30 m (R5d)
   están justificados por escala urbana, no validados contra un conjunto etiquetado a mano
   (el diseño prevé calibrarlos con ~100–200 pares etiquetados; pendiente).
