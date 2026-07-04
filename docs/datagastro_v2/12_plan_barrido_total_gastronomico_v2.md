# DataGastro V2 — Plan de barrido total gastronómico

> Etapa 2. Diseño del camino hacia el **universo gastronómico general** de CABA. No se ejecuta
> nada: es la hoja de ruta para pasar de pilotos a un padrón candidato amplio de todos los
> rubros, sin mezclar consumo, producción y venta.

## 1. Qué significa "todos los gastronómicos"

**Padrón candidato amplio, no censo definitivo.** "Todos" = el universo operativo probable más
completo y defendible que se pueda construir cruzando fuentes, con trazabilidad por fila y
nivel de confianza explícito. **Nunca** se afirma completitud ni "locales activos confirmados".

Los rubros piloto (`config/v2/rubros_piloto_v2.csv`) **calibran** el método; la arquitectura
apunta al universo total (`config/v2/rubros_universo_gastronomico_v2.csv`).

## 2. Principio rector: no mezclar funciones

El barrido mantiene separadas las tres funciones del ecosistema en todo momento:

```text
CONSUMO en local      restaurantes, bares, cafeterías, pizzerías, parrillas, bodegones...
PRODUCCIÓN            obradores, fábricas de pastas, tostadores, fábricas con venta...
VENTA especializada   panaderías, pastelerías, casas de pastas, chocolaterías, vinotecas...
+ FERIAS/MERCADOS/EVENTOS  y etiquetas transversales (cadena, independiente, emblemático)
```

Un mismo establecimiento puede tener función doble (panadería que también es cafetería): se
admite `categoria_secundaria`, pero **nunca** se colapsan consumo, producción y venta en un
único cubo de conteo.

## 3. Etapas del barrido

### Etapa A — Anclas oficiales
- Poblar `fact_deteccion_fuente` leyendo salidas públicas existentes (F01, F02, F03, F04, F05)
  **sin regenerarlas**. Candidatos con nivel C4 `oficial_estricto`.
- Sumar F06–F10 cuando se aprueben sus descargas (con ficha de fuente).
- Salida: padrón candidato base, solo oficial, por comuna/rubro.

### Etapa B — OSM (fuente abierta auxiliar)
- Mapear tags OSM → taxonomía v2 (`config/v2/osm_tags_v2.csv`). Cobertura auxiliar y geometría.
- Deduplicar contra el padrón oficial. Coincidencias suben a C5 multifuente.

### Etapa C — Google Places (señal operativa, BLOQUEADA por costo)
- Plan en `04_plan_integracion_google_places.md`. Requiere aprobación + presupuesto + topes.
- Aporta cobertura amplia, `businessStatus`, detección de cadenas. Es el motor de cobertura de
  los rubros mal anclados en lo oficial.

### Etapa D — Documental / web (localizador)
- Perplexity/web **solo como localizador** (`07_...md`). Sostiene `historico_emblematico` y
  rubros de nicho. Sin URL verificable, no entra.

### Etapa E — Revisión manual
- Resolver casos B/C1 (`fact_validacion_manual`). Separar producción de consumo de venta
  cuando las señales son mixtas.

### Etapa F — Resolución de entidad (deduplicación)
- Unificar detecciones de todas las fuentes en `dim_establecimiento_candidato`
  (1 fila = 1 entidad), con heurística conservadora (nombre+dirección normalizados + distancia
  + similitud), reutilizando el enfoque validado en el piloto V1.

### Etapa G — Clasificación por rubro
- Asignar `id_rubro_principal` (+ secundario) según taxonomía v2, etiquetas transversales
  (cadena/independiente/emblemático) y `nivel_confianza`.

### Etapa H — Salidas generales
- Agregados sanitizados: mapa general, por rubro, rankings por comuna/barrio, densidad,
  cadenas vs independientes, cobertura por zona (`09_...md`).

### Etapa I — Informes específicos por rubro
- Una vez clasificado el universo, se "filtra" por rubro para informes profundos (ver §5).

## 4. Diagrama del flujo

```text
A oficiales ─┐
B OSM        ├─► F resolución de entidad ─► G clasificación por rubro ─► H salidas generales
C Places(💰) ┤                                                            └─► I informes por rubro
D documental ┤
E revisión ──┘
            (cada fuente conserva su detección en fact_deteccion_fuente)
```

## 5. Informes específicos por rubro (cómo se derivan)

Cada informe es un **corte del universo clasificado**, con su propia nota metodológica de
cobertura (qué fuente lo ancla, cuánto depende de externas):

| Informe | Rubros | Ancla principal | Dependencia externa |
|---|---|---|---|
| Cafés de especialidad | cafeterias_de_especialidad | baja (oficial) | **alta** (Google + documental) |
| Heladerías artesanales | heladerias | media (F01/F02) | media (Google/OSM) |
| Panaderías y pastelerías | panaderias, pastelerias | **media-alta** (F02) | media (Google/OSM) |
| Casas de pastas | casas_de_pastas, fabricas_de_pastas | media (F02) | alta (Google/OSM/documental) — piloto V1 |
| Mercados y ferias | mercados_gastronomicos, ferias_gastronomicas | **alta** (F03) | baja |
| Productores / obradores | obradores, fabricas_*, productores_proveedores | baja (F02 parcial) | **alta** (documental + revisión) |

## 6. Orden recomendado de ejecución

1. **A (oficiales)** y **B (OSM)** primero: sin costo, construyen base y prueban deduplicación.
2. **D (documental)** en paralelo para emblemáticos.
3. **C (Google)** como piloto topeado cuando haya aprobación y presupuesto.
4. **E→F→G** para consolidar; **H→I** para salidas.

Cada transición es un **gate de aprobación de Diego**. Esta Etapa 2 deja solo el diseño y la
matriz de cobertura; no inicia A.

## 7. Lo que esta etapa NO hace

- No descarga ni lee datos para poblar candidatos.
- No ejecuta requests, ni Google, ni OSM, ni Perplexity.
- No crea `dim_establecimiento_candidato` ni `fact_deteccion_fuente` con datos.
- No toca V1 ni casas de pastas.
