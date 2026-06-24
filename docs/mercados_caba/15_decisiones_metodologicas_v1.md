# Mercados gastronómicos CABA — Decisiones metodológicas V1

> Criterios aplicados en la consolidación V1. Objetivo: conteos honestos y categorías que no
> mezclen cosas distintas.

## 1. Por qué el Mercado de los Carruajes no se cuenta como activo

Fuentes oficiales (GCBA) y prensa (La Nación) confirman que **cerró definitivamente en abril
2025** y se reconvierte en espacio de eventos. Se conserva como **antecedente documentado**
(ex cochera presidencial reconvertida en paseo gourmet, 43 puestos), con
`estado_operativo = cerrado` y `activo_para_conteo = no`. Contarlo como activo sobreestimaría el
universo vigente. Vive en `mercados_gastronomicos_cerrados_o_no_activos_v1.csv`.

## 2. Cómo se trataron los Centros de Abastecimiento Municipal (CAM)

Los CAM son **mercados municipales de abasto**. Se evaluó caso por caso el **foco gastronómico**:

- **CAM Nº 72 (Av. Córdoba 1750) = Mercado San Nicolás** y **CAM Nº 128 (Av. Juramento 2527) =
  Mercado de Belgrano**: están renovados, con plaza de comidas y oferta gastronómica → **se
  incluyen en alcance** (ya figuran como MG-0013 y MG-0002). Se documenta la equivalencia para
  evitar doble conteo.
- **CAM Nº 27 (Mercado Pompeya, Av. Sáenz 790)** y **CAM Nº 116 (Villa Pueyrredón, Ezeiza y
  Nazca)**: son abasto barrial activo, pero **no se confirmó** que la gastronomía sea eje central
  → quedan como `mercado_barrial_alimentario` en **pendientes** (`mantener_pendiente`), **no** se
  cuentan como mercados gastronómicos activos y **no** se mezclan con food halls.
- **Mercado Comunitario Primera Junta**: posible solapamiento con el Mercado del Progreso y oferta
  no confirmada → pendiente.

Regla: un CAM entra solo con evidencia de oferta gastronómica/de comida; si es abasto puro, queda
`mercado_barrial_alimentario` pendiente, separado de los food halls.

## 3. Cómo se trató Barrio Chino

**Barrio Chino (Belgrano)** tiene oferta gastronómica y comercios alimentarios orientales, pero
es un **distrito comercial**, no un mercado único con administración común. Se clasifica como
`distrito_gastronomico_no_mercado`: se documenta por su relevancia gastronómica, pero **no** se
cuenta como un mercado del padrón. Igual criterio para **Los Arcos del Rosedal / "Patio de los
Arcos"**, que es un **polo de restaurantes independientes** bajo viaducto (distinto del
**Distrito Arcos**, un outlet que queda fuera de alcance).

## 4. Cómo se trataron patios y food halls

- **Food hall**: espacio techado y curado con varios puestos gastronómicos bajo una administración
  (Mercat Villa Crespo, Soho, Mercat Caballito; Carruajes cuando operaba). Cuenta como mercado
  gastronómico.
- **Patio gastronómico / espacio tipo mercado**: predio (a veces al aire libre) con varios puestos
  gestionado, frecuentemente por GCBA (Lecheros, Smart Plaza, Costanera Norte, Rodrigo Bueno).
  Cuenta como mercado gastronómico (categoría `espacio_tipo_mercado_gastronomico`).
- Ambos se distinguen de un **patio de comidas de shopping** o un **restaurante individual**, que
  no entran.

## 5. Diferencias entre las categorías clave

| Categoría | Qué es | Cuenta como mercado | Ejemplos |
|---|---|---|---|
| **mercado gastronómico** (público/privado/mixto, food hall, barrial alimentario, identidad histórica) | predio con administración común y varios puestos donde la gastronomía/los alimentos son eje | **sí** | San Telmo, Belgrano, Soho, Mercat VC |
| **feria gastronómica** | evento periódico/itinerante con puestos gastronómicos y de productores | **sí** (marca itinerante) | Buenos Aires Market |
| **mercado de productores** | venta directa de productores de alimentos | **sí** | Bonpland, El Galpón, Sabe la Tierra |
| **food hall** | patio gastronómico curado techado | **sí** (subtipo) | Mercat Caballito, Carruajes |
| **distrito gastronómico** | zona/polo con muchos locales independientes, sin administración única | **no** (se documenta aparte) | Barrio Chino, Los Arcos del Rosedal |

## 6. Conteo (regla de oro)

`mercados_activos_para_conteo` = mercados en alcance con `estado_operativo` activo o itinerante y
`activo_para_conteo = si`. **No** suman: cerrados, distritos, pendientes ni fuera de alcance. Esto
mantiene separados los universos y evita inflar la cifra.
