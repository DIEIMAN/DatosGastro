# QA — Corrida ampliada Google Places (PolosGastro, Fase 11)

DGDGAS — Dirección General de Gastronomía. Documento interno. Fecha: 2026-07-02.

## Ejecución

- Comando (una vez): `python scripts/polos_gastro/google_places/places_repiloto_fase11.py --tanda corrida_ampliada --batch --execute --confirm-real-api`.
- Modo: **batch** en bloques internos de `MAX_LOCALES_HARD_CAP` (10). Cap **no modificado**.
- Guardado incremental tras cada bloque; reanudable (omite ids ya en el interno).

## Conteos

- Locales candidatos (restantes tras Tanda 1+2): **86**.
- Efectivamente consultados: **86** (9 bloques: 8 de 10 + 1 de 6).
- Excluidos por ya consultados en Tanda 1/2: **20**.
- Matches: **86**. Errores de API: **0**. Problemas de cuota/billing/permiso: **0**.
- Aceptados para mapa automáticamente: **0** (diseño prudente).

## Hallazgos por criterio (corrida ampliada)

- **Cerrados**: 3 en esta corrida (La Reina Kunti ×2 permanente por duplicación Corrientes/Abasto;
  Alo's Café temporal). Total acumulado de cerrados: **8**.
- **Fuera de CABA**: **0**.
- **Rubros no gastronómicos / categoría dudosa**: 1 (**Chila** → `tourist_attraction`; revisar, es
  alta cocina). Hitos colectivos (mercado/patio/food_court) detectados y marcados para no tratarse
  como local individual.
- **Zonas/sucursales dudosas**: 25 casos de confianza baja quedaron en `zona_sucursal_a_revisar`.
- **Duplicados probables**: **11** (mismo place_id en dos polos). Incluye los **6 de Abasto = Av.
  Corrientes**.
- **Queries a corregir**: casos puntuales (Chila por categoría; se suman a Pa' Pastar y Oporto de
  tandas previas → 3 en total).

## Consolidado total

- Registros consolidados: **106** (Tanda 1: 10 + Tanda 2: 10 + ampliada: 86). Cobertura completa de
  la tabla preparada de Fase 11.
- Consultas reales acumuladas: **106**.

Distribución consolidada:

| Estado | Casos |
|---|---|
| match_fuerte | 32 |
| match_razonable_revisar_sede | 27 |
| zona_sucursal_a_revisar | 25 |
| duplicado_probable | 11 |
| vigencia_no_confirmada | 8 |
| query_a_corregir | 3 |

## Seguridad de API

- API key leída solo de entorno/`.env`; reportada como "presente"; **nunca impresa ni guardada**.
- `.env` no copiado ni mostrado; **sin API key en outputs**; **sin raw JSON** en outputs.

## Sanitización de publicables

- Interno (86 filas): con `google_place_id_interno`, `rating_interno`, `user_ratings_total_interno`,
  `direccion_google` (archivo técnico).
- Revisión visual (86): lat/lon en las 86 filas; **0 columnas prohibidas**.
- Publicable (86): lat/lon vacíos (todos `aceptado_para_mapa=no`); **0 columnas prohibidas**.

## Confirmaciones

- No se procesó más de 10 por bloque; `MAX_LOCALES_HARD_CAP=10` sin modificar.
- Input solo desde la tabla preparada de Fase 11; **sin seeds experimentales**.
- No se reconsultaron los 20 ya consultados (exclusión documentada por id).
- **No PDF/DOCX/mapas.** No se tocaron datos fuente, Borrador 2/3, Cafecito, Mercados ni Casas de
  Pastas. No se borró nada. **No commit/push/staging.**
- Marca: **DGDGAS — Dirección General de Gastronomía**.
