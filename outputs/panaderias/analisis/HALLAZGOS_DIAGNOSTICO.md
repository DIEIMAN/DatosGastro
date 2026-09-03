# Panaderías — hallazgos del diagnóstico

Corrida del 2026-08-27, tarde, sobre el padrón vigente (A = 1.178, B = 472, A+B = 1.650)
y sobre F02 leído con `scripts/shared/fuentes_locales`.

Reproducible con:

```
.venv/Scripts/python.exe scripts/panaderias/diagnostico_panaderias.py --pastas <maestro_pastas>
.venv/Scripts/python.exe scripts/panaderias/diagnostico_unidad_de_conteo.py
```

El primero trabaja sobre el maestro ya construido; el segundo relee F02 porque pregunta por
columnas que el maestro no guarda. Ninguno consulta nada externo ni escribe fuera de esta
carpeta.

---

## 1. La partida matriz es el inmueble, no el local (P1)

El maestro agrupa por partida matriz. Una partida identifica una **parcela**, y bajo una
misma parcela conviven habilitaciones distintas: un gimnasio, una cerrajería y una
panadería pueden compartir partida.

| Unidad de conteo | Universo A (archivos legacy) |
|---|---|
| Partida matriz — lo que se usa hoy | 1.112 |
| Solicitud (una habilitación = un local) | **1.214** |
| Solicitud + unidad funcional | 1.217 |

Son **102 establecimientos de sub-conteo, un 9,2 %**. Y el 51 % de los inmuebles del
universo (567 de 1.112) alojan más de una habilitación, que es lo que produce los grupos
absurdos: el más grande fusiona 360 registros bajo una sola fila.

Los siete archivos legacy traen `solicitud`, `unidad_funcional` y `partida_horizontal`. El
archivo 2025 (esquema moderno) no trae ninguno: aporta 66 establecimientos del universo A
que seguirían contándose por partida.

Detalle: `p1_unidad_de_conteo.csv`, `p1_inmuebles_con_varias_habilitaciones.csv`,
`d4_grupos_mas_grandes.csv`.

## 2. Casi un cuarto del universo es pan dentro de otro negocio (P2)

Una habilitación declara varios rubros a la vez — **mediana de 5, máximo 15**. Basta que
uno sea de pan para que el establecimiento entre al universo.

| | Habilitaciones | Con un giro ajeno en la misma habilitación |
|---|---|---|
| Declaran elaboración | 786 | **235 (29,9 %)** |
| Sólo despacho | 428 | 49 (11,4 %) |
| **Total** | **1.214** | **284 (23,4 %)** |

Giros detectados: supermercado 321, bazar 39, golosinas envasadas (kiosco) 22, depósito 3.

**Lo contraintuitivo:** la contaminación es *mayor* en el grupo que declara elaborar
(29,9 %) que en el que sólo despacha (11,4 %). No es un error: son los supermercados con
horno propio. La panadería de barrio y el sector de panadería de un Coto están hoy en la
misma cifra, y la distinción no la resuelve el rubro de pan sino los otros rubros de la
misma habilitación.

Esto se ve también en el padrón: `Día Argentina S.A.` aparece con 18 bocas y
`Farmacia Orien S.A.` con 2.

Detalle: `p2_contaminacion_multirubro.csv`, `d5_firmas_con_varias_bocas.csv`.

## 3. La geocodificación quedó bien y pasa el control (D8)

Después de la corrida de USIG, el universo A pasó de 65,4 % a **97,8 %** geolocalizado
(1.152 de 1.178). Los puntos vienen marcados `sin_control_comuna`, así que se controlaron
aparte:

- **0 puntos fuera del polígono de CABA** sobre 1.602 geolocalizados.
- De los 118 casos donde hay comuna declarada en la fuente y comuna geocodificada,
  **116 coinciden y 2 discrepan**. Las dos están en `d8_qa_geocodificacion.csv`; una
  (`MARTINEZ, ENRIQUE, GRAL. 683`, declarada 13 y geocodificada 9) tiene la firma de una
  calle homónima y conviene mirarla a mano.
- 88 coordenadas son compartidas por 2 establecimientos cada una. Es esperable: dos
  habilitaciones en el mismo domicilio.

Quedan 48 registros sin coordenadas, que son 34 direcciones únicas. **29 no tienen altura**
(esquinas, S/N): USIG no las resuelve solas y necesitan criterio humano. Sólo 4 son
direccionables. El problema de cobertura geográfica está prácticamente cerrado.

Detalle: `d1_sesgo_geocodificacion.csv`, `d3_direcciones_sin_geocodificar.csv`,
`d8_qa_geocodificacion.csv`.

## 4. Elaborar o sólo despachar no tiene patrón territorial (D2)

La proporción que declara elaboración va de **54,7 % (Comuna 10)** a **72,9 % (Comuna 15)**.
Quince comunas dentro de un rango de 18 puntos, sin agrupamiento geográfico reconocible: no
hay una zona de la Ciudad que sólo despache pan.

Es un resultado negativo y conviene tenerlo escrito, porque cierra una hipótesis que
aparece sola al mirar el mapa.

Detalle: `d2_elaboracion_vs_despacho_por_comuna.csv`.

## 5. Los 48 barrios tienen al menos una panadería (D6)

Ninguno de los 48 barrios queda en cero. No hay desierto de pan en el padrón, y con la
cobertura geográfica ahora en 97,8 % la afirmación se sostiene.

## 6. Un quinto de las casas de pastas comparte domicilio con una panadería (D7)

29 domicilios —y las mismas 29 partidas— aparecen en los dos universos. Sobre un padrón de
pastas de 161 establecimientos, es el 18 %.

No es un error de clasificación: son habilitaciones que declaran los dos rubros. Pero
significa que **los universos de rubro no son disjuntos**, y que sumar estudios de rubro
para estimar un total de comercios de alimentos contaría esos locales dos veces.

Detalle: `d7_solape_con_casas_de_pastas.csv`.

---

## 7. La unidad de conteo, aplicada: 1.219, no 1.280 (F1, 2026-08-28)

El cambio de partida matriz a habilitación se aplicó. El universo A pasa de 1.176 a
**1.219** y el A+B de 1.647 a 1.732.

**No dio 1.280.** Ese cálculo sumaba 1.214 legacy + 66 modernos como si fueran universos
disjuntos, y no lo son: el padrón 2025 vuelve a publicar trámites viejos. Como el archivo
legacy se identifica por `solicitud` y el moderno por `disposicion`, el mismo local entraba
dos veces con dos claves distintas. Son **59 casos del universo A** —misma partida, mismo
domicilio, mismo año, mismo patrón de rubro— y ahora se unen. Quedan 2 sin unir, donde la
correspondencia es ambigua y unir a ciegas sería inventar.

Otro efecto del mismo tipo, del lado legacy: **379 solicitudes aparecen en dos archivos**
por el solape de años, siempre con el mismo domicilio. Agrupar por solicitud las une.

**El precio, que es el riesgo que el plan anticipaba.** Un local habilitado dos veces
—renovación, cambio de titular— son dos habilitaciones. La cota superior del doble conteo
es **83 establecimientos, el 6,8 % del universo A**: 81 domicilios donde conviven dos
registros con el mismo patrón de rubro, 80 de ellos con una sola partida. Con eso, la cifra
vive entre **1.136 y 1.219**, y la lista se resuelve mirándola: dos panaderías pegadas son
igual de compatibles con la evidencia que una sola habilitada dos veces.

Detalle: `d9_renovaciones_candidatas.csv`.

**Un efecto lateral que casi pasa inadvertido.** Al fusionar, el representante del grupo
suele ser una fila vieja, que no trae nombre. La cobertura de nombres caía de 119 a 38 y
`Día Argentina S.A.` pasaba de 17 bocas a 2. Ahora los campos vacíos del representante se
completan con los de las otras filas del mismo trámite.

---

## Lo que estos hallazgos cambian

1. El conteo publicable no es 1.178 ni 1.280: contando por habilitación y sin doble
   publicación es **1.219**, con una cota inferior de 1.136 si todas las renovaciones
   candidatas fueran el mismo local. Falta descontar el pan que está dentro de otro giro
   (F2), que sobre la medición previa sacaba 284 de 1.280. Los números salen del mismo
   padrón y miden cosas distintas: hay que elegir cuál se publica y decirlo; no promediarlos.
2. El eje editorial pendiente ya no es sólo *elaboración vs despacho*: es
   **negocio de pan vs pan dentro de otro negocio**, que corta distinto y afecta más al
   grupo que parecía más limpio.
3. La geocodificación y la unidad de conteo dejan de ser el cuello de botella. El cuello
   pasa a ser **F2 y la decisión de qué cifra se publica**, que es trabajo de criterio, no
   de código.
