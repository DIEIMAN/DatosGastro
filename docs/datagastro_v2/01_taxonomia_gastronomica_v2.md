# DataGastro V2 — Taxonomía gastronómica

> Propuesta de taxonomía. No se aplica todavía a ningún dato. Sirve para clasificar el padrón
> candidato de forma consistente y defendible.

## 1. Estructura

Dos niveles + atributos metodológicos:

```text
categoria_principal   (función / rol en el ecosistema)
subcategoria          (rubro concreto)
incluye               (qué entra)
excluye               (qué NO entra, para evitar inflar el universo)
fuentes_sugeridas     (dónde se detecta mejor)
riesgo_metodologico   (sesgo o confusión típica)
criterio_de_validacion (cómo confirmar territorialmente)
```

Un establecimiento candidato puede tener **más de una** subcategoría (ej.: panadería que
también es cafetería). Se admite `categoria_secundaria` en el modelo de datos. Si un rubro es
dudoso, se marca `pendiente_revision_taxonomica` y **no** se excluye.

## 2. Categorías principales

```text
consumo_en_local
takeaway_delivery
produccion_gastronomica
venta_especializada
ferias_mercados_eventos
historico_emblematico       (etiqueta transversal, no excluyente)
cadena_marca                (atributo de organización, no de rubro)
independiente_barrial       (atributo de organización, no de rubro)
```

`historico_emblematico`, `cadena_marca` e `independiente_barrial` son **etiquetas
transversales**: describen la entidad, no su rubro. Conviven con la categoría funcional
(ej.: una pizzería puede ser `consumo_en_local` + `historico_emblematico`).

## 3. Tabla de taxonomía (subcategorías)

Leyenda riesgo: **B** bajo · **M** medio · **A** alto.

| categoria_principal | subcategoria | incluye | excluye | fuentes_sugeridas | riesgo | criterio_de_validacion |
|---|---|---|---|---|---|---|
| consumo_en_local | restaurantes | servicio de mesa, cocina al plato | rotiserías sin salón, dark kitchens | AGC, Places, Ente Turismo, OSM | M | salón habilitado + actividad observable |
| consumo_en_local | bares | bar, bar notable, pub | venta de bebidas envasadas (vinoteca) | AGC, Ente Turismo, Places | M | barra/salón + horario nocturno típico |
| consumo_en_local | cafeterías | café tradicional, confitería con salón | cafeterías de especialidad (subcat. propia) | AGC, Places, OSM | M | salón + carta de café/infusiones |
| consumo_en_local | cafeterías_de_especialidad | tostado propio o de terceros, métodos filtrados | cadenas de café masivo si no aplica | Places, documentales, OSM | A | señal de especialidad (método, origen) verificada |
| consumo_en_local | pizzerías | pizza al molde/media masa, a la piedra | restaurantes italianos genéricos | AGC, Places, documentales | M | producto principal = pizza |
| consumo_en_local | parrillas | parrilla, asador | bodegón sin parrilla | AGC, Places, Ente Turismo | M | parrilla a la vista / carta de carnes |
| consumo_en_local | bodegones | cocina porteña tradicional de salón | restaurantes de autor | documentales, Ente Turismo, Places | A | reconocimiento documental + carta tradicional |
| consumo_en_local | cervecerías | cervecería, brewpub, bar de cerveza | distribuidoras sin consumo | Places, OSM, documentales | M | consumo en local + oferta de cerveza |
| takeaway_delivery | rotiserías | comida lista para llevar | restaurantes con salón principal | AGC, Places | M | mostrador de venta para llevar |
| takeaway_delivery | empanadas | locales de empanadas | restaurantes que sólo las ofrecen en carta | AGC, Places | M | producto principal = empanadas |
| takeaway_delivery | heladerías | heladería artesanal/industrial con venta | fábricas sin venta al público | AGC, Places, OSM | B | mostrador de venta de helado |
| produccion_gastronomica | fábricas_de_pastas | elaboración de pastas frescas | casas de pastas sólo reventa | AGC, Places, documentales | A | obrador/elaboración declarada o visible |
| produccion_gastronomica | obradores | obrador de pastelería/panadería/catering | punto de venta sin elaboración | AGC, BA Data, documentales | A | habilitación de elaboración / obrador |
| produccion_gastronomica | tostadores_de_café | tostado de café para venta/abastecimiento | cafeterías que sólo sirven | documentales, Places, web oficial | A | proceso de tostado declarado |
| produccion_gastronomica | fábricas_con_venta_al_público | elaboración + local de venta | fábricas sin venta minorista | AGC, BA Data, Places | M | elaboración + venta minorista verificada |
| venta_especializada | panaderías | pan y factura con elaboración o venta | grandes superficies con sección panadería | AGC, Places, OSM | B | local especializado en panificados |
| venta_especializada | pastelerías | pastelería, repostería | panaderías genéricas | AGC, Places | M | oferta principal de pastelería |
| venta_especializada | confiterías | confitería tradicional (venta) | confitería con salón (=cafetería) | AGC, documentales | M | foco en venta de confitería |
| venta_especializada | casas_de_pastas | venta de pastas frescas (reventa/elaboración) | restaurantes italianos | AGC, Places, OSM, documentales | A | mostrador de pastas frescas (ver piloto V1) |
| venta_especializada | chocolaterías | chocolate artesanal/industrial, bombonería | kioscos con chocolates | Places, documentales | M | producto principal = chocolate |
| venta_especializada | vinotecas | venta de vino y bebidas | bares (consumo en local) | Places, OSM, documentales | M | venta de vino envasado predominante |
| venta_especializada | queserías | venta especializada de quesos | almacenes genéricos | documentales, Places | M | foco en quesos |
| venta_especializada | charcuterías | fiambres y embutidos especializados | supermercados | documentales, Places | M | foco en charcutería |
| venta_especializada | dietéticas_gourmet | dietética con foco gastronómico/gourmet | farmacias, dietéticas de suplementos | Places, OSM | A | oferta gastronómica gourmet verificable |
| venta_especializada | almacenes_gastronómicos | almacén/delicatessen especializado | autoservicios genéricos | documentales, Places | A | curaduría de producto gastronómico |
| ferias_mercados_eventos | mercados_gastronómicos | mercados de abasto/gastronómicos | shoppings genéricos | BA Data, F03, Ente Turismo | M | espacio físico con puestos gastronómicos |
| ferias_mercados_eventos | ferias_gastronómicas | ferias itinerantes/permanentes | ferias no gastronómicas | BA Data, F03, F04 | M | feria con oferta gastronómica declarada |
| ferias_mercados_eventos | eventos_gastronómicos | festivales, activaciones, ediciones | eventos sin componente gastronómico | F04, Ente Turismo, documentales | M | edición datada con fuente |
| historico_emblematico | bar_notable | registro Bares Notables GCBA | bares comunes | BA Data (Bares Notables), documentales | B | inclusión en registro oficial Notables |
| historico_emblematico | caso_emblematico | caso histórico/identitario documentado | apertura reciente sin trayectoria | documentales, prensa | A | ≥2 referencias documentales independientes |

> La fila `casas_de_pastas` y `fábricas_de_pastas` recoge directamente la experiencia del
> piloto V1 (clasificación A/B/C, "venta ≠ restaurante italiano").

## 4. Reglas de clasificación

1. **No excluir por duda.** Rubro ambiguo → `pendiente_revision_taxonomica`. Se conserva.
2. **Doble función permitida.** `categoria_principal` + `categoria_secundaria` cuando aplica.
3. **Etiquetas transversales aparte.** `historico_emblematico`, `cadena_marca`,
   `independiente_barrial` no compiten con la categoría funcional.
4. **Producción vs venta vs consumo.** Distinguir obrador/fábrica (produce) de comercio
   especializado (vende) de local de consumo (sirve). Es el eje conceptual de V2 y el de mayor
   riesgo metodológico (Places suele etiquetar todo como `restaurant`/`store`).
5. **Riesgo alto = más validación.** Subcategorías con riesgo **A** requieren al menos una
   señal documental o territorial antes de pasar de candidato a confirmado.

## 5. Mapa a la taxonomía V1

V2 **no** rompe la taxonomía de V1 (`dim_categoria_gastronomica`). Se propone una tabla puente
`puente_taxonomia_v1_v2` que mapee cada categoría V1 a la nueva subcategoría, para no perder
trazabilidad con el pipeline público existente.
