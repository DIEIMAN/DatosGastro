# DataGastro V2 — Integración segura y minimizada de I10 (DGDGAS)

> Etapa 3. Integración **local, minimizada y sin exposición de PII** de la fuente interna I10.
> **No** se hicieron requests, **no** se usó API key, **no** se modificó/movió/borró el Excel
> original, **no** se construyó el padrón final, **no** se dedupló contra Google/OSM. Pipeline
> V1 y casas de pastas intactos.

## 1. Qué es I10

- `I10_directorio_gastronomico_dgdgas`: directorio interno de **locales gastronómicos por
  rubro** (planilla `Copia de Base de datos DGDGAS EVENTOS.xlsx`, carpeta interna gitignored).
- **No es padrón oficial ni censo.** Se trata como **fuente interna de validación / catálogo
  candidato**. No implica local activo confirmado y **no reemplaza** AGC ni fuentes oficiales.
- Aporta detecciones internas por rubro y cobertura territorial, con trazabilidad.

## 2. Qué se leyó

- Solo el `.xlsx` **local**, en modo lectura por `zipfile` (no se usó `openpyxl`, no disponible).
  Nunca se abrieron los punteros `.gsheet` ni links de Drive.
- 15 hojas leídas. **12 hojas de rubro** se trataron como establecimientos; **3 se excluyeron**
  (`BASE` resumen, `Organizadores` con nombres de personas, `Comunas` con teléfono/mail).

## 3. Qué se excluyó (minimización de PII)

Columnas PII descartadas **siempre** (no se escriben ni en el staging interno):
`CELULAR`, `MAIL`, `REFERENTE`, `INSTAGRAM`, `CARGO` (y, en hojas excluidas, `Nombre`,
`Teléfono`). Total de **valores PII descartados: 8.350**. **No se eliminó ningún
establecimiento**: solo se quitaron los campos personales.

## 4. Qué quedó (y dónde)

| Salida | Contenido | Sensibilidad | Ubicación |
|---|---|---|---|
| `i10_dgdgas_perfil_columnas.csv` | perfil de columnas por hoja | media | `outputs/v2/internal/` **(gitignored)** |
| `i10_dgdgas_establecimientos_minimizados.csv` | establecimientos con `nombre_local` + `barrio` + `direccion` | **alta** | `outputs/v2/internal/` **(gitignored)** |
| `i10_dgdgas_agregado_por_hoja.csv` | conteos por hoja/rubro | baja | `outputs/v2/sanitized/` (versionable) |
| `i10_dgdgas_agregado_por_rubro_v2.csv` | conteos por subcategoría v2 | baja | `outputs/v2/sanitized/` |
| `i10_dgdgas_agregado_por_barrio.csv` | conteos por barrio | baja | `outputs/v2/sanitized/` |
| `i10_dgdgas_resumen_integracion.csv` | métricas de integración | baja | `outputs/v2/sanitized/` |

`nombre_local` y `direccion` son **sensibles operativos**: viven **solo** en
`outputs/v2/internal/` (gitignored). **Nunca** se escriben en `outputs/v2/sanitized/`. No se
geocodificó, no se generó GeoJSON, no se publicaron direcciones.

## 5. Resultados (orden de magnitud)

- **Total establecimientos minimizados (interno): 2.480.**
- Con barrio: 1.525 · con dirección (solo interno): 1.617.
- En hojas mixtas (a desagregar): 978 · pendiente revisión taxonómica: 278.

Distribución por subcategoría v2 sugerida:

| subcategoria_v2_sugerida | registros | hojas que aportan |
|---|---|---|
| restaurantes | 698 | 3 (Restaurantes, Cocina internacional, Restaurantes de autor) |
| bares | 269 | 1 |
| bodegones | 97 | 1 |
| parrillas | 95 | 1 |
| heladerias | 65 | 1 |
| pendiente_desagregar_hoja_mixta | 978 | 2 (Café y dulce, Pizza/empanadas/pasta) |
| pendiente_revision_taxonomica | 278 | 3 (Hamburguesería, Foodtrucks, Emprendimientos) |

## 6. Rubros que I10 cubre fuerte

`restaurantes`, `bares`, `bodegones`, `parrillas`, `heladerias`. Destacan **`bodegones`** y
**`heladerias`**, rubros con ancla **oficial débil** (ver `13_mapa_cobertura_por_rubro_v2.md`):
ahí el directorio interno suma cobertura real como **validación**.

## 7. Rubros / hojas que requieren desagregación

- **Hojas mixtas** (`pendiente_desagregar_hoja_mixta`):
  - `Café y dulce` (702) → cafeterías / pastelerías / confiterías.
  - `Pizza, empanadas y pasta` (276) → pizzerías / empanadas / casas de pastas.
- **Rubro no estable en la taxonomía** (`pendiente_revision_taxonomica`):
  - `Hamburguesería` (131), `Foodtrucks` (82), `Emprendimientos` (65).

No se resolvieron a la fuerza: se conservan con su etiqueta de pendiente.

## 8. Limitaciones

- **PII en origen:** la fuente cruda contiene contacto; solo se usa minimizada.
- **Sin fecha de actualización:** no asumir vigencia; contacto ≠ establecimiento activo.
- **`barrio` es texto libre** y sin normalizar: aparecen ~230 valores distintos (CABA tiene 48
  barrios), con celdas que listan varios barrios o variantes de tipeo. Requiere normalización
  antes de cualquier análisis territorial fino. No hay comuna en las hojas de rubro.
- **Posibles duplicados** intra-fuente (no se deduplicó) y solapamiento entre hojas.
- I10 es **una sola fuente**: su confianza sube solo al cruzarse con otras (multifuente).

## 9. Qué queda pendiente antes de usar I10 en el padrón general

1. Confirmar con DGDGAS propietario, fecha de corte, grano y reglas de actualización.
2. **Desagregar** hojas mixtas a subcategorías v2 y resolver `Hamburguesería`/`Foodtrucks`/
   `Emprendimientos` en la revisión taxonómica.
3. **Normalizar barrio** y, si se consigue, asignar comuna (sin geocodificar direcciones aquí).
4. **Deduplicar** intra-I10 y, en etapa posterior, contra F01/F02/OSM/Google (multifuente).
5. Definir el contrato interno y mantener I10 como **universo interno separado** (no mezclar
   con F0x ni E0x).

## 10. Reproducibilidad

```bash
python src/v2/build_i10_dgdgas_staging.py   # offline; regenera staging interno + agregados
python src/v2/validate_v2_setup.py          # valida setup + escaneo de privacidad
```

No hace requests, no usa API key, no toca el Excel original ni el pipeline V1.
