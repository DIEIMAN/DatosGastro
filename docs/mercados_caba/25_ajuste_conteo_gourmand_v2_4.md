# Mercados gastronómicos CABA — Ajuste de conteo por Gourmand Food Hall (V2.4)

> Ajuste acotado del conteo activo. **Solo** incorpora Gourmand Food Hall. No modifica los 3 casos
> en revisión, el cerrado, los distritos, los abastos ni los fuera de alcance. Fecha: 2026-06-24.

## Decisión

> **El conteo se ajusta de 12 a 13 activos confirmados por incorporación de Gourmand Food Hall como
> food hall privado activo, luego de validación documental.**

Gourmand Food Hall cumplió los **5 criterios de inclusión** (ver
`24_validacion_gourmand_food_hall_v2_4.md` y `validacion_gourmand_food_hall_v2_4.csv`): identidad
propia de food hall, operación actual verificable (Google `OPERATIONAL`, 2.125 reseñas), 10+
propuestas gastronómicas, respaldo multifuente (sitio oficial + prensa) y no es un patio de comidas
común.

## Clasificación incorporada

| id | nombre | tipo | gestión | barrio | comuna | estado | activo_para_conteo |
|---|---|---|---|---|---|---|---|
| MG-0017 | Gourmand Food Hall | food_hall | privada | Retiro | 1 | activo | sí |

## Nuevo cuadro de conteo

| Categoría | V2.2 | V2.4 |
|---|---|---|
| Activos para conteo | 12 | **13** |
| — sede fija | 10 | 11 |
| — itinerantes | 2 | 2 |
| En revisión (no contabilizados) | 3 | 3 |
| Cerrados documentados | 1 | 1 |
| Pendientes metodológicos | 0 | 0 |
| Distritos gastronómicos (no mercado) | 2 | 2 |
| Abasto barrial no gastronómico | 3 | 3 |
| Fuera de alcance | 2 | 2 |

**Gestión de los 13 activos:** 3 públicos · **5 privados** · 5 mixtos.

## Qué NO cambia

- **Mercado Soho, Mercat Caballito y El Galpón** siguen **en revisión** (no contabilizados).
- **Mercado de los Carruajes** sigue **cerrado documentado**.
- Distritos, abastos no gastronómicos y fuera de alcance se mantienen igual.
- La lectura conservadora V2.2 sigue vigente; este ajuste es **aditivo y documentado**, no un
  cambio de criterio.

## Trazabilidad

- Padrón activo V2.4: `mercados_gastronomicos_activos_v2_4.csv` (13 filas).
- Resumen V2.4: `resumen_relevamiento_mercados_v2_4.csv`.
- Validación: `validacion_gourmand_food_hall_v2_4.csv` y `24_validacion_gourmand_food_hall_v2_4.md`.
- Gourmand sale de `posibles_omitidos` (queda como activo); los demás posibles omitidos siguen
  pendientes.
