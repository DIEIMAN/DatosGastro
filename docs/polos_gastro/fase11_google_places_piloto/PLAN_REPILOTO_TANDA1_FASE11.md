# Plan del re-piloto — Tanda 1 corregida (Google Places, Fase 11)

Fecha: 2026-07-02. Documento interno. Preparación **sin ejecutar API**. Experimento controlado,
fuera del pipeline público F01–F05.

## 1. Por qué se rehace la Tanda 1

La auditoría (`QA_AUDITORIA_TANDA1_GOOGLE_PLACES.md`,
`RECONSTRUCCION_TANDA1_GOOGLE_PLACES.md`, `DECISION_TANDA2_GOOGLE_PLACES.md`) concluyó que la
Tanda 1 **no es confiable** para mapa ni para avanzar a Tanda 2:

- Usó el insumo equivocado (seed de experimento aislado) en vez de la tabla preparada de Fase 11.
- Queries pobres (nombre largo del polo embebido en el `textQuery`) que produjeron 3 matches
  erróneos.
- El QA de Copilot contó "matches devueltos" como "aceptados"; los aceptados para mapa fueron 0.
- FieldMask sin `location`: no hay lat/lon, así que no sirve para mapa.

## 2. Qué errores se corrigieron

| Problema Tanda 1 | Corrección en el re-piloto |
|---|---|
| Insumo = seed experimental | Fuente única = tabla preparada de Fase 11 (o su subconjunto `muestra_repiloto_tanda1_fase11.csv`) |
| Query cruda con polo largo | Query limpia `nombre + zona + Buenos Aires` (ver `queries_repiloto_tanda1_fase11.csv`) |
| Osaka→Osaki, Aldo's→Artemisia, Oporto→Somos OP aceptados | Sustitutos prohibidos explícitos; esos 3 quedan como casos de prueba con query más específica y rechazo documentado |
| FieldMask sin location | FieldMask con `location` (lat/lon) |
| "10 aceptados" engañoso | Diseño: `aceptado_para_mapa` solo tras revisión manual; el conteo separa "matches" de "aceptados" |
| Sanitizado con dirección exacta y `nota_interna` | Esquema publicable sin dirección exacta, sin place_id/rating/user_ratings_total, sin nota_interna |
| Mojibake "Ni�o Gordo" | Era solo de consola/QA; los CSV usan UTF-8 y "Niño Gordo" correcto |

## 3. Qué input correcto se usará

- Fuente válida única: `outputs/polos_gastro/fase11_google_places_preparacion/tablas/locales_semilla_preparados_para_google_places.csv`.
- Muestra operativa de 10 (Palermo): `outputs/polos_gastro/fase11_google_places_piloto/tablas/muestra_repiloto_tanda1_fase11.csv`.
- Queries: `outputs/polos_gastro/fase11_google_places_piloto/tablas/queries_repiloto_tanda1_fase11.csv`.
- Criterios de aceptación/rechazo: `CRITERIOS_MATCH_GOOGLE_PLACES_FASE11.md`.

## 4. Por qué NO se usa el seed experimental

`locales_destacados_por_polo_seed.csv` es el insumo del experimento aislado anterior. No lleva las
columnas de query preparada, hints de barrio ni estrategia de match de Fase 11, y fue precisamente
la causa de las queries pobres. El re-piloto lo excluye por diseño: el script
`places_repiloto_fase11.py` **solo** lee la tabla preparada de Fase 11 (o su muestra), nunca el
seed.

## 5. Por qué `location` es obligatorio

El objetivo final del piloto es alimentar un mapa. Sin `location` (lat/lon) no hay puntos que
mapear. La Tanda 1 no lo pedía, por eso quedó inservible para mapa. El FieldMask del re-piloto
incluye `places.location`. **lat/lon son campo interno de QA**; al mapa/publicable solo viajan tras
revisión manual y con la leyenda prudente prevista.

## 6. Cómo se separan los tres outputs

La ejecución real produce **tres** archivos con roles distintos:

1. **Interno** (`resultados_repiloto_tanda1_interno.csv`, esquema en
   `schema_resultados_repiloto_tanda1_interno.csv`): todo para QA — incluye `direccion_google`,
   `lat`, `lon`, `rating_interno`, `user_ratings_total_interno`, `google_place_id_interno`,
   `confidence_match`, `nota_interna`, `business_status`, `fecha_consulta`. **Uso**: control
   técnico y trazabilidad. No circula.

2. **Revisión visual** (`resultados_repiloto_tanda1_revision_visual.csv`, esquema en
   `schema_resultados_repiloto_tanda1_revision_visual.csv`): sanitizado pero con **lat/lon
   siempre presentes** (aunque `aceptado_para_mapa='no'`), más `decision_automatica`,
   `motivo_decision` y `accion_recomendada`. **Uso**: inspeccionar los puntos en un visor antes de
   aceptar/rechazar a mano. **No** lleva `google_place_id`/`place_id`, `rating`,
   `user_ratings_total`, raw JSON, API key, dirección exacta con altura, `nota_interna` ni campos
   técnicos sensibles. **No es publicable final**: no debe ir al PDF público ni circular como pieza
   institucional.

3. **Publicable** (`resultados_repiloto_tanda1_publicable.csv`, esquema en
   `schema_resultados_repiloto_tanda1_publicable.csv`): solo `polo`, `subzona`, `nombre_lugar`,
   `tipo_gastronomico_estimado`, `lat`, `lon`, `barrio_o_zona`, `fuente_geolocalizacion`, `origen`,
   `mostrar_en_mapa`, `mostrar_en_ficha`, `nota_publica`. **Prudente**: `lat`/`lon` salen vacíos
   mientras `aceptado_para_mapa='no'`; solo se llenan para puntos aceptados. **Uso**: pieza final,
   se construye **después de la revisión humana** (marcar a mano los aceptados).

- **No viajan al publicable ni a la revisión visual**: dirección exacta con altura,
  `google_place_id`/`place_id`, `rating`, `user_ratings_total`, raw JSON, API key, `nota_interna`,
  campos técnicos.
- **Diferencia clave**: el interno tiene todo; la revisión visual tiene lat/lon sin campos
  sensibles para control manual; el publicable solo tiene puntos ya aceptados para mapa.

## 7. Doble confirmación de la rama real

La rama real de ejecución **ya está implementada** en el script, pero **bloqueada detrás de doble
confirmación**. Comportamiento:

| Invocación | Qué hace |
|---|---|
| (sin banderas) | Dry-run. No llama API. |
| `--confirm-real-api` (sola) | Dry-run con aviso. No llama API. |
| `--execute` (sola) | **Frena** con error controlado: "Para ejecutar llamadas reales a Google Places usar también --confirm-real-api". No llama API (exit 2). |
| `--execute --confirm-real-api` | Rama real. Llama API **solo** si además hay API key válida; si no, frena e informa qué falta (exit 3). |

Seguridad de la rama real: lee la key solo de entorno/`.env`, **nunca** la imprime ni la guarda,
nunca muestra el `.env`, solo reporta "presente/ausente". FieldMask mínimo con `location`. No
guarda raw JSON. Separa interno/publicable. Hard cap 10 (si la muestra tuviera más, corta a 10 y lo
avisa por stderr).

## 8. Condiciones antes de correr `--execute --confirm-real-api`

Deben cumplirse **todas**:

1. Aprobación explícita de Diego para gastar en Places API.
2. API key de Google Maps Platform con **billing y tope de gasto** configurados, provista por
   entorno o `.env` local (nunca commiteada, nunca impresa).
3. Revisión de los Términos de Google Maps Platform (cache, mezcla con otros mapas).
4. Confirmación de que se usa la muestra de Fase 11 (cap 10 intacto) y no un seed.

## 9. Riesgos

- **Costo**: cada request de Places API (New) es pago. El cap de 10 acota el gasto de esta tanda.
- **Matches erróneos**: Osaka/Aldo's/Oporto son casos de riesgo alto (ver
  `queries_repiloto_tanda1_fase11.csv`). El script rechaza automáticamente los sustitutos conocidos
  (Osaki, Artemisia, Somos OP), rubros no gastronómicos y resultados fuera de CABA, pero igual
  requieren revisión manual.
- **Publicable prematuro**: por diseño, `aceptado_para_mapa` sale en `no` incluso con confianza
  alta; se habilita a mano tras revisión. No publicar sin ese paso.

## 10. Qué revisar después de ejecutar (cuando corresponda)

- `resultados_repiloto_tanda1_interno.csv`: revisar `confidence_match`, `business_status`, y las
  filas con `nota_interna` de rechazo (sustituto/rubro/fuera de CABA).
- Confirmar manualmente los 3 casos de riesgo alto (Osaka, Aldo's, Oporto) antes de aceptarlos.
- `resultados_repiloto_tanda1_publicable.csv`: verificar que no aparezcan dirección exacta,
  place_id, rating, user_ratings_total ni nota_interna.
- Recién tras revisión, marcar a mano `aceptado_para_mapa=si` en los que correspondan.

## 11. Comandos (referencia — NO ejecutar la rama real todavía)

```
# Dry-run (ya ejecutado, sin API):
python scripts/polos_gastro/google_places/places_repiloto_fase11.py

# Ejecución real FUTURA (doble confirmación), solo tras cumplir la sección 8:
# python scripts/polos_gastro/google_places/places_repiloto_fase11.py --execute --confirm-real-api
```
