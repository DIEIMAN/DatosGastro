# QA del output publicable — Tanda 1 Google Places (Fase 11)

Fecha: 2026-07-02. Revisión de campos sensibles/técnicos en los outputs destinados a ser
publicables. No se ejecutó API. No se leyó API key ni `.env`.

## Archivo revisado

`outputs/polos_gastro/fase11_google_places_piloto/tablas/locales_places_piloto_resultados_sanitizado.csv`

## Campos presentes

```
id_local_semilla, polo, subzona, nombre_lugar_original, query_google_places, status_busqueda,
nombre_google, direccion_google, barrio_o_zona_inferida, categoria_google, business_status,
confidence_match, requiere_revision_manual, aceptado_para_mapa, mostrar_nombre_en_mapa,
mostrar_en_ficha, nota_publica, nota_interna, fecha_consulta
```

## Checklist de campos prohibidos

| Campo prohibido | ¿Presente en el sanitizado? |
|---|---|
| `google_place_id` / `place_id` | NO ✔ |
| `rating` | NO ✔ |
| `user_ratings_total` | NO ✔ |
| `raw JSON` | NO ✔ |
| `API key` | NO ✔ |

El sanitizado **no** contiene identificadores de Google Places, ratings ni conteos de reseñas, ni
JSON crudo ni credenciales. En ese sentido, cumple la regla de no publicar `place_id`, `rating` ni
`user_ratings_total`.

## Observaciones adicionales (no bloqueantes, pero a decidir antes de publicar)

1. **`direccion_google` con altura exacta**: el sanitizado incluye la dirección completa devuelta
   por Google (p. ej. "Guatemala 4699"). No es un dato personal sensible (es un comercio), pero
   conviene decidir si un output "publicable" debe llevar dirección exacta o solo barrio/zona. Para
   una pieza institucional, `barrio_o_zona_inferida` suele alcanzar.
2. **`business_status` y `categoria_google`**: son campos técnicos de Google. No están prohibidos
   por las reglas dadas, pero son "campos técnicos internos" en el sentido amplio. Evaluar si viajan
   al output publicable final o quedan solo en el interno.
3. **`nombre_google` con matches erróneos**: el sanitizado muestra "Somos OP" (aseguradora),
   "Artemisia" y "Osaki Sushi Palermo" como `nombre_google`. Publicar esto tal cual asociaría a
   locales semilla (Oporto, Aldo's, Osaka) con nombres que no les corresponden. **No publicar** hasta
   corregir los matches.
4. **`nota_interna` dentro del "sanitizado"**: el archivo llamado sanitizado incluye una columna
   `nota_interna`. Si "sanitizado" = "publicable", una columna con la palabra *interna* no debería
   viajar. Menor, pero conviene depurar.

## ¿Hace falta una versión corregida ahora?

**No se generó** una versión corregida del sanitizado en esta auditoría, y **es lo correcto**: el
sanitizado no viola las reglas duras (no hay place_id/rating/user_ratings_total/JSON/key). Las
observaciones 1–4 son decisiones de diseño editorial, no incumplimientos. Además, el contenido de
esta tanda **no debe publicarse** por los matches erróneos (Osaka, Aldo's, Oporto). Corregir el
sanitizado antes de resolver esos matches sería trabajo perdido.

Recomendación: dejar el sanitizado como está (no publicable todavía) y, cuando se rehaga el piloto
con queries corregidas, generar el publicable definitivo decidiendo antes los puntos 1–2.

## Confirmaciones

- No se ejecutó ninguna llamada a Google Places en esta QA.
- No se imprimió ni leyó API key.
- No se copió `.env`.
- No se creó ni modificó ningún output de datos en esta tarea (solo este documento QA).
