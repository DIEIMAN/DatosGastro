# DataGastro V2 — Mapa de cobertura por rubro

> Etapa 2. Lectura de `config/v2/cobertura_fuente_rubro_v2.csv` y
> `config/v2/rubros_universo_gastronomico_v2.csv`: qué rubros tendrán buena cobertura oficial y
> cuáles dependerán de fuentes externas o de revisión manual. Sin requests, sin datos nuevos.

## 1. Cómo leer este mapa

Para cada rubro se evalúa la **mejor cobertura oficial disponible** (F0x), si necesita Google
Places (E01) u OSM (E02), y el riesgo de confusión (sobre todo consumo vs producción vs venta).
La fuente de verdad es la matriz CSV; este documento la resume.

## 2. Rubros con buena ancla oficial

Cobertura oficial **media-alta**; lo oficial alcanza para una base sólida (a validar siempre).

| Rubro | Ancla oficial | Nota |
|---|---|---|
| mercados_gastronomicos | F03 (alta) | espacios reales, separar de puestos |
| ferias_gastronomicas | F03 (alta) | buena cobertura de ferias relevadas |
| bar_notable | F07 (alta) | registro oficial de notables |
| panaderias | F02 (alta) | rubro de elaboración/venta bien habilitado |
| restaurantes | F02 (alta) + F01 | amplio; habilitación ≠ activo |
| bares | F02 (alta) + F07 | amplio + ancla notable |

## 3. Rubros con ancla parcial

Cobertura oficial **media**; sirve de base pero necesita complemento externo y desambiguación.

| Rubro | Ancla | Complemento necesario |
|---|---|---|
| cafeterias | F01/F02/F07 | Google/OSM para distinguir de especialidad |
| pizzerias | F01/F02 | Google/documental; separar de italianos |
| parrillas | F01/F02/F06 | Google |
| pastelerias | F02 | desambiguar de panaderías/confiterías |
| confiterias | F02/F07 | documental; solapa con cafeterías |
| heladerias | F01/F02 | Google/OSM (bajo riesgo) |
| rotiserias | F02 | Google; solapa con restaurantes |
| casas_de_pastas | F02 | Google/OSM/documental (piloto V1) |
| eventos_gastronomicos | F04/F05 | I03 contexto; nunca universo completo |

## 4. Rubros donde Google/OSM serán centrales

Cobertura oficial **baja o nula**; el universo real vendrá sobre todo de fuentes externas.

| Rubro | Por qué | Fuente central |
|---|---|---|
| cafeterias_de_especialidad | el rubro administrativo no marca especialidad | Google + documental |
| cervecerias | rubro reciente, poco en datasets | Google + OSM |
| chocolaterias | rubro de nicho | Google + documental |
| vinotecas | se mezcla con comercio de bebidas | Google + OSM |
| queserias | nicho, sin rubro propio claro | documental + Google |
| charcuterias | nicho | documental + Google |
| dieteticas_gourmet | confusión con suplementos | Google + OSM |
| almacenes_gastronomicos | curaduría difícil de delimitar | documental + Google |
| empanadas | rara vez rubro propio | Google + revisión |

## 5. Rubros con alto riesgo de confusión

Requieren reglas de exclusión y desambiguación cuidadosas (ver `config/v2/reglas_exclusion_v2.csv`).

| Rubro | Confusión típica |
|---|---|
| casas_de_pastas / fabricas_de_pastas | restaurante italiano vs venta vs fábrica |
| obradores / fabricas_con_venta | producción sin venta vs con venta minorista |
| cafeterias vs cafeterias_de_especialidad | especialidad no declarada |
| bodegones | restaurante de autor vs bodegón tradicional |
| dieteticas_gourmet | dietética de suplementos / farmacia |
| vinotecas vs bares | venta envasada vs consumo en local |

Regla transversal: cuando coexisten señales de consumo y producción sin resolver →
`C1 revision_manual`, nunca se fuerza la clasificación.

## 6. Rubros que requieren validación manual fuerte

`requiere_revision_manual = si` con `riesgo alto`: producción gastronómica (obradores, fábricas,
tostadores), venta de nicho (queserías, charcuterías, almacenes, dietéticas gourmet), cafeterías
de especialidad, bodegones, casos emblemáticos y todo lo marcado
`pendiente_revision_taxonomica`.

## 7. Resumen ejecutivo de cobertura

- **Mejor cubiertos por lo oficial:** ferias, mercados, bares/cafés notables, panaderías,
  restaurantes y bares (con la advertencia "habilitación ≠ local activo").
- **Peor cubiertos por lo oficial:** cafeterías de especialidad, producción/obradores y venta de
  nicho (queserías, charcuterías, chocolaterías, almacenes, dietéticas gourmet), cervecerías.
- **Dependencia de Google/OSM:** alta en los rubros emergentes y de nicho; media en consumo
  general; baja en ferias/mercados.
- **Carga de revisión manual:** concentrada en producción, venta de nicho y desambiguación
  consumo/producción/venta.

> Todas las cifras de cobertura son **expectativas de diseño** (orden de magnitud), no
> mediciones. Se confirmarán recién al ejecutar el barrido (Etapas A–I del documento 12) y la
> validación territorial posterior.
