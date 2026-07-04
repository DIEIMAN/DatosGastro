# DataGastro V2 — Plan de integración Google Places API

> **Plan, no ejecución.** Este documento diseña cómo se usaría Google Places API en V2. **No**
> se ejecutan requests, **no** se usa API key, **no** se llama a la API en esta etapa. Recoge y
> generaliza el piloto V1 (`docs/casas_pastas/GOOGLE_PLACES_PILOTO.md`).

## 1. Encuadre metodológico

- Google Places es **señal operativa no oficial** (E01). No es registro administrativo.
- Sólo **API oficial** de Places. **Prohibido** scraping de Google Maps.
- Sirve para **cobertura amplia**, detección de **actividad** (`businessStatus`) y de **cadenas**
  (repetición de marca). No para afirmar legitimidad oficial.

## 2. Guardrails de seguridad (obligatorios, heredados del piloto)

```text
- API key sólo desde variable de entorno (p. ej. GOOGLE_MAPS_API_KEY). Nunca se imprime,
  loguea, guarda ni commitea. No se escribe en .env.
- Modo por defecto = dry-run. Sin --run no hay request real.
- Topes duros configurables (--max-queries, --max-results) que abortan si se exceden.
- Pausa entre requests (--pause).
- Toda salida cruda va a carpeta GITIGNORED (p. ej. outputs/v2_google_places/).
- Nada se pushea hasta autorización explícita de Diego.
```

## 3. Cómo buscar por rubro

Usar **Text Search** (`places:searchText`) con queries por subcategoría de la taxonomía v2.
Cada subcategoría tiene un set de términos fuertes y términos ambiguos (a vigilar):

```text
casas_de_pastas      "casa de pastas", "pastas frescas", "pastificio", "ravioles"     [evitar: "restaurante italiano"]
panaderías           "panadería", "factura", "pan artesanal"
heladerías           "heladería artesanal", "helado"
cafeterías_especial. "café de especialidad", "specialty coffee", "tostador"
parrillas            "parrilla", "asador"
pizzerías            "pizzería", "pizza a la piedra"
chocolaterías        "chocolatería", "bombones artesanales"
vinotecas            "vinoteca", "wine store"
queserías            "quesería", "quesos artesanales"
...                  (un bloque por subcategoría)
```

Cada query lleva sufijo territorial (CABA / barrio / comuna). El **mapeo término→subcategoría**
se versiona en un archivo de configuración (no sensible).

## 4. Cómo buscar por barrio / comuna

- **Grilla territorial:** combinar cada término de rubro con cada barrio/comuna (48 barrios /
  15 comunas) para mejorar cobertura y reducir el sesgo de "todo en el centro".
- Se planifica como CSV de plan (gitignored), igual que el piloto
  (`google_places_plan_*.csv`), y **se ejecuta por lotes topeados**, no de una sola vez.
- Alternativa de mayor costo/precisión: `searchNearby` con centro+radio por comuna. Decisión
  según presupuesto (ver §11).

## 5. Cómo evitar duplicados

Deduplicación en dos momentos:

1. **Intra-Google:** por `place_id` (clave estable de Google). Un `place_id` = una entidad.
2. **Inter-fuente:** misma heurística conservadora del piloto integrado:
   - nombre normalizado (minúsculas, sin acentos/puntuación);
   - dirección normalizada (sin "CABA/Buenos Aires/Argentina");
   - distancia haversine;
   - similitud de nombre (ratio de secuencias).
   - Reglas: `dist<40 m y sim≥0.5` · `dist<150 m y sim≥0.8` · `nombre idéntico y dist<250 m`.

Se conserva trazabilidad: `fuentes_detectan`, `cantidad_fuentes`, `motivo_fusion`.

## 6. Cómo clasificar candidatos

Clasificación determinística y conservadora (generaliza A/B/C del piloto):

```text
A_operativo_probable   nombre/types con término fuerte del rubro y sin señal de otro rubro
B_dudoso               término ambiguo o señales mixtas → requiere_revision_manual = si
C_descartado           sin término del rubro objetivo  → se conserva aparte con motivo
```

Insumos de clasificación (campos mínimos, primera pasada): `id`, `displayName`,
`formattedAddress`, `location`, `businessStatus`, `types`. El clasificador de rubro se
**reutiliza/extiende** desde `scripts/casas_pastas/google_places_clasificador.py`.

## 7. Cómo detectar cadenas

- **Marca conocida:** lista curada de marcas (no sensible). Coincidencia de nombre normalizado.
- **Repetición:** mismo nombre normalizado en ≥2 `place_id`/sedes ⇒ `es_cadena_detectada = si`.
- Campos: `es_cadena_detectada`, `cadena_detectada`, `cantidad_sucursales_cadena`,
  `tipo_establecimiento` (`cadena` / `independiente` / `indeterminado`).
- Una aparición única sin marca conocida ⇒ `independiente`. **Los independientes son centrales,
  no ruido.**

## 8. Cómo separar consumo de producción / comercio especializado

Es el riesgo metodológico más alto: Google etiqueta grueso (`restaurant`, `store`,
`food`). Estrategia:

```text
1. types de Google como señal débil (ej.: noodle_shop, bakery, store, manufacturer).
2. términos del nombre como señal fuerte (ej.: "fábrica", "obrador", "elaboración").
3. cruce con AGC (rubro administrativo) cuando exista coincidencia.
4. si la señal de consumo y producción coexisten sin resolver → B_dudoso (revisión manual).
```

Nunca se afirma "fábrica/obrador" sólo por `types`; se requiere término en nombre o ancla
oficial/documental.

## 9. Brutos: dónde y cómo se guardan

```text
outputs/v2_google_places/            (GITIGNORED, completo)
  raw/<subcategoria>/<fecha>.json    respuesta cruda SOLO con campos mínimos pedidos (sin API key)
  candidatos.csv                     normalizados + clasificados
  resumen.csv                        conteos A/B/C, requests, errores
  log.txt                            ejecución sin API key
```

Los brutos contienen `place_id`, dirección y, en una eventual segunda pasada, teléfono/web:
**son sensibles** y nunca salen de la carpeta gitignored.

## 10. Outputs sanitizados (entregables)

Lo que sí puede publicarse son **agregados** que **no** exponen filas individuales sensibles:

```text
- conteos por subcategoría × comuna/barrio
- densidad territorial (por km² con geometrías GCBA)
- cadenas vs independientes (conteos)
- distribución por nivel de confianza
```

Reglas de sanitización para entregables externos:

```text
- NO exponer place_id, API key, teléfonos, emails ni direcciones individuales.
- NO exportar filas individuales con nombre comercial + dirección a entregables externos.
- Publicar sólo agregados, perfiles de columnas y diagnósticos.
```

## 11. Costo y control

- Estimación de **orden de magnitud** (a confirmar contra pricing vigente de Google y crédito
  gratuito de la cuenta **antes** de cualquier ejecución; **no** es precio oficial).
- Text Search con campos básicos es más barato que pedir `rating`, `reviews`, `openingHours`,
  `websiteUri`, `phone` (segunda etapa, sólo si se justifica).
- Ejecución **siempre topeada y por lotes**; nunca una corrida masiva sin límites.

## 12. Estado y aprobaciones

- Diseño: versionable (este documento no contiene API key ni datos sensibles).
- Ejecución: **bloqueada** hasta aprobación explícita de Diego, presupuesto confirmado y topes
  acordados.
