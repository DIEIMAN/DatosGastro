# HANDOFF · Ronda 7 · la vía B cambia de escala, y la geometría se toca por primera vez · 2026-08-08

Continúa `HANDOFF_POLOS_RONDA_6_2026_08_07.md`. Rama `mercados-gastronomicos-v2`.
**Google Places: 0 requests.** USIG: normalizador sobre cinco direcciones nuevas y `/datos_utiles`
sobre un punto, todo cacheado. Diego resolvió las veinte decisiones pendientes y con eso se
descongela la fase 2. La geometría se descongeló **sólo** para las tareas 3 y 4; fichas y
cartografía siguen congeladas.

**Tres scripts nuevos**, en este orden de dependencia:

1. `scripts/barrido_ciudad/ronda_7_hitos_y_decisiones.py` → `hitos_capa_2026_r7.csv` (225 hitos,
   36 columnas), `cambios_ronda_7.csv` (201 cambios), `RONDA_7_HITOS.txt`,
   `monserrat_hitos_r7.csv`, `nucleo_de_salta_r7.csv`, `san_cristobal_densidad_r7.csv`,
   `veredictos_no_aplicados_r7.csv`
2. `scripts/barrido_ciudad/ronda_7_geometria_ampliaciones.py` → `geometria_r7/referencias_r7.geojson`,
   `ampliaciones_r7.csv`, `ampliaciones_sensibilidad_buffer_r7.csv`, `solapes_r7.csv`,
   `AMPLIACIONES_R7.txt`
3. `scripts/barrido_ciudad/ronda_7_familias_de_vias.py` → `zonas_via_B_via_D_r7.csv`,
   `seis_vias_94_filas_r7.csv`, `vista_unida_94_filas_r7.csv`, `requiere_cruce_resuelto_r7.csv`,
   `reparto_de_las_48_sin_hitos_r7.csv`, `via_C_contra_padron_fiab_r7.csv`,
   `geometria_r7/zonas_r7.geojson`, `FAMILIAS_DE_VIAS_R7.txt`

Más `scripts/barrido_ciudad/places_vigencia_hitos.py`, que **no se ejecutó** (ver abajo).

---

## El número que la ronda venía a buscar

Con la misma capa de hitos y las mismas 94 filas, cambiando sólo a qué objeto se le pregunta:

| vía B | ronda 4 (capa r3) | por contención (capa r7) | **por zona (capa r7)** |
|---|---|---|---|
| abre | 7 | 16 | **33** |
| pendiente | 37 | 27 | 37 |
| no abre | 48 | 51 | **24** |

**Las dos columnas de la derecha son la comparación válida**: misma capa, mismas filas. La
primera está para ver de dónde venimos y no para restarle a las otras. El 7 de la ronda 4 se
midió sobre `hitos_capa_2026_r3.csv`; de 7 a 16 es lo que aportaron los veredictos de las rondas
5 a 7, y de 16 a 33 es el cambio de escala.

### Cómo se reparten las que no tienen hitos en su propio polígono

Son **51**, no 48: la ronda 4 contó sobre la capa r3 y tres filas cambiaron de lado cuando las
rondas 5–7 corrigieron direcciones (`PG006B_BAJO_BELGRANO`, `PG006C_BELGRANO_R`, `PGR_P004`). La
reconciliación está fila por fila en el informe.

| | filas |
|---|---|
| **la zona SÍ tiene hitos, el fragmento no** | **27** |
| la zona tampoco tiene hitos | 23 |
| la fila no tiene zona resuelta | 1 |

**Ésas 27 y las 23 se contaban igual hasta ayer**, y son dos cosas distintas: una es «acá no hay
trayectoria» y la otra es «el clustering no acertó a caer encima de un bar». `PGR_P083 · Almagro`
—5,67 ha, zona con 8 hitos de vía B, soporte `activo`— es el caso que originó el criterio y sigue
ahí, ahora con nombre y con la distinción escrita.

### Cómo queda guardado

La fila guarda **`zona_via_B` y `via_B_modo`, y nada más**. El valor vive en
`zonas_via_B_via_D_r7.csv`. Si mañana se vuelve a correr el clustering, las filas quedan
apuntando a una zona que puede no existir y **rompen visiblemente**, en vez de quedarse con un
`si` huérfano. `vista_unida_94_filas_r7.csv` es la vista con el valor pegado: es derivada y se
puede tirar.

Modos: **69 heredada · 20 propia · 5 requiere_cruce**, sobre 47 zonas distintas.

**La salvedad va en la ficha:** la herencia no vale hacia arriba. Que Almagro tenga cinco Bares
Notables no convierte a `PGR_P083` en un polo notable — lo convierte en un fragmento de una zona
que tiene cinco.

---

## La geometría, por primera vez

Las cuatro decisiones aplicadas, con la regla de que **el polígono nuevo tiene que contener al
viejo**. Verificado por superficie perdida, no por predicado: `covers()` de GEOS devuelve `False`
en R19 y R21 sobre geometrías cuya diferencia mide **exactamente 0,0 m²**. Es una falla de
robustez de `relate` con vértices casi colineales, no un polígono que se achicó; manda la
superposición y queda anotado en el CSV (`predicado_covers_geos`).

| | antes | después | delta locales | contención |
|---|---|---|---|---|
| **R19** Federico Lacroze | 89,5 ha · 185 | 303,3 ha · 532 | **+347 (+187,6 %)** | 0,0 m² perdidos |
| **R21** La Paternal | 321,0 ha · 208 | 385,3 ha · 307 | +99 (+47,6 %) | 0,0 m² perdidos |
| **R20** García del Río | 28,4 ha · 61 | 61,0 ha · 102 | +41 (+67,2 %) | 0,0 m² perdidos |
| **R18** → subzona de Z46 | 48,4 ha · 318 | 51,2 ha · 330 | +12 | 0,0 m² perdidos |

Buffer de 150 m, la convención declarada en la ronda 3 (una cuadra a cada lado). La sensibilidad
a 100 y 200 m está en `ampliaciones_sensibilidad_buffer_r7.csv`.

**R19 casi cuadruplica y conviene mirarlo antes de firmarlo.** A 100 m de buffer serían +243 en
vez de +347.

### Dos cosas que la ampliación deja a la vista y no se resuelven acá

**1. Seis solapes que antes no existían.** El más grande es **R09 ∩ R19 = 60,4 ha**, que es el
64 % de toda R09 Chacarita. También R08 ∩ R21 = 49,7 ha. Las 22 tienen regla de precedencia por
solape para contar sin duplicar, así que esto cambia conteos si no se decide. Está medido en
`solapes_r7.csv` y **no se tocó**: la precedencia es decisión editorial, no ajuste de geometría.

**2. R20 · «se revisa el corte» podía recortar, y recortaba.** El tramo Cabildo → Balbín mide
974 m (el 60 % de García del Río dentro de Saavedra) y **24,7 ha de la envolvente publicada
quedan fuera de él**. La regla de contención las conserva, así que se adopta la unión. Si en
algún momento se decide que la envolvente estaba mal cortada, ése es el número a discutir, y es
una decisión sobre lo publicado.

### Marco de la ampliación de R21

Con el marco en La Paternal sola, **tres de los siete ejes dan cero metros** —Beláustegui,
Remedios de Escalada y Rojas no pasan por el barrio— y la ampliación sería de 9 locales. Villa
Crespo entra al marco porque la decisión 8 lo dice («hacia el límite con Villa Crespo»). Villa
Gral. Mitre **no** entra: la decisión no lo nombra y sumaría otros 93 locales sin respaldo en el
texto.

---

## Lo que contradijo al insumo

### Cinco de los «cinco que no estaban en la capa» ya estaban

`hitos_nuevos_monserrat.csv` da por ausentes a nueve de diez establecimientos. Se comprobó uno
por uno antes de dar de alta nada:

| | insumo | capa |
|---|---|---|
| Bar El Colonial · Av. Belgrano 599 | NO estaba | **H008, con punto** |
| Bar Seddon · Defensa 695 | NO estaba | **H015, con punto** |
| Cabildo de Buenos Aires · Perú 86 | NO estaba | **H020, con punto** |
| El Querandí · Perú 302 | NO estaba | **H053, con punto** |
| London City · Av. de Mayo 599 | NO estaba | **H073, con punto** |

Entraron con el canon del Boletín y con la Res. 1225/26 de la ronda 5. **No se dieron de alta:**
duplicarlos habría inflado exactamente la vía B que esta ronda venía a medir bien.

**Las altas que sí lo son son cuatro:** Gran Café Gardel (DIR-026), Centro Asturiano (DIR-027),
Centro Laurak Bat / Restaurante Haritz (DIR-028) y Casal de Catalunya (DIR-029). Los tres últimos
abren la vía D, no la B. Gran Café Gardel **no computa para la vía B**: no está en el anexo ni
entre los 16 Icónicos, así que es trayectoria sin registro oficial. Su dirección es una ochava sin
altura y se geocodificó por cruce de ejes del callejero.

**El Globo y Plaza Asturias no entran a la capa de hitos**: no tienen ningún registro oficial. El
Globo está explícitamente fuera del anexo y de los 16.

### «Nueve de los noventa», confirmado

Contado contra el polígono administrativo: **9 Bares Notables dentro de Monserrat**, de 91 con
punto en la capa. El insumo tenía razón.

### Av. Boyacá y Av. Carabobo son la misma avenida

La delimitación de Z23 Flores casco histórico dice «Av. Rivadavia, Boyacá-Carabobo». No se puede
construir: **las dos tocan al eje de Rivadavia dentro de Flores en un único punto, idéntico para
las dos.** Boyacá corre al norte de Rivadavia y Carabobo al sur; cambia de nombre al cruzar.
«Entre Boyacá y Carabobo» mide cero cuadras.

Z23 ya estaba PENDIENTE de redelimitación por otro motivo (su único hito cae ocho cuadras al sur).
Esto agrega el motivo geométrico. Mientras tanto recibe **por residuo** lo que no cae en Z24 ni en
Z39b, marcado `residuo (no contención)`, que no es una asignación medida.

### La decisión 1 no mueve ninguna fila de las 94

Comprobado contra el padrón de FIAB del GCBA (184 ferias): **0 de los 8 mercados/patios con punto
de la capa está a menos de 50 m de una FIAB**. La más cercana está a 202 m. Donde la decisión sí
mueve es a nivel de zona, y ahí el dato viene de la delimitación textual de cowork —Z23, Z25, Z28,
Z44, Z47—: se registra su procedencia, no se lo vuelve a derivar.

**Y un hallazgo del mismo criterio, que no es de la decisión 1:** `H199 · Yiyo el Zeneize`
(Av. Eva Perón 4402) está tipado `Mercado/patio` pero su reconocimiento es «Patrimonio histórico y
cultural inmaterial (Ley CABA 6.533)». Es la única vía C de las 94 que no se apoya en un mercado
de la lista oficial, y abre `PGR_P004 · Villa Lugano`. **No se tocó**: esta ronda tiene el mandato
de no mover A, C ni F.

---

## Las mediciones que Diego pidió

### El núcleo de Salta

| | Bar Iberia | Plaza Asturias | El Globo | El Imparcial |
|---|---|---|---|---|
| **Bar Iberia** | — | 17,2 | 51,6 | 61,6 |
| **Plaza Asturias** | 17,2 | — | 68,7 | 76,1 |
| **El Globo** | 51,6 | 68,7 | — | 30,4 |
| **El Imparcial** | 61,6 | 76,1 | 30,4 | — |

Metros, sobre puntos normalizados con USIG. **La distancia máxima entre dos de los cuatro es
76,1 m** y los cuatro caben en una envolvente convexa de **0,110 ha**. No es una lista: es un
núcleo de una ochava.

### San Cristóbal · el conteo de la decisión 11

| tramo | eje | locales | por 100 m |
|---|---|---|---|
| Av. San Juan 1900-2100 | 357 m | 32 | 9,0 |
| Av. Independencia 2300-2500 | 319 m | 22 | 6,9 |
| **los dos, sin doble conteo** | | **54** en 13,7 ha | **3,95 locales/ha** |

Buffer de 75 m, media cuadra a cada lado. **No es un veredicto de vía A**: el recorte por eje es
más ajustado que un polígono de polo y la densidad sale más alta por construcción. Es el insumo
que la decisión pidió antes de decidir.

### Bar Seddon, resuelto por punto

USIG `/datos_utiles` sobre el punto responde **Monserrat**. El polígono GCBA lo confirma: dentro
de Monserrat, a **8 m** del borde de San Telmo. **El catálogo tiene razón y la CPPHC no**, aunque
por 8 metros. Cuarta vez que un campo territorial se resuelve contra el punto.

---

## Las diez filas trabadas · 8 de 10 resueltas

| resueltas por contención | por residuo | sin resolver |
|---|---|---|
| — | P055, P085, P107 → **Z35** · P036, P058, P059, P060, P061 → **Z23** | PGF2_FLORES, PGR_P014 |

**Ninguna se resolvió por contención**: ningún fragmento cae dentro de Z24, Z39b ni Z47. En
Balvanera el residuo no es debilidad —la decisión 13 se llevó Congreso a Monserrat, así que lo que
queda de Balvanera fuera del eje Av. de Mayo–Callao es, por construcción, Once—. En Flores sí lo
es, por lo de Boyacá/Carabobo.

**PGF2_FLORES (859 ha) y PGR_P014 (45,6 ha) quedan sin resolver a propósito.** Sus soportes cubren
más de la mitad del barrio: no pertenecen a una zona, la abarcan. Forzarles una sería inventar una
pertenencia, y la más cara de detectar después, porque quedaría escrita como si se hubiera medido.

---

## Decisión 4 · Places autorizado y NO ejecutado

`places_vigencia_hitos.py` deja la pasada lista: **220 hitos con dirección utilizable** —el número
exacto de la decisión—, campos `business_status`, `formatted_address` y `opening_hours`, nivel
v2b, `vigencia_fecha_consulta` escrita en cada fila porque **Places no trae la fecha del dato**.

**No se gastó nada.** La decisión pide confirmar el precio contra la consola antes de gastar, y
este proceso no puede leer la consola de facturación de Diego; la tarifa que circula en la
estimación está anotada como no confirmada en el propio repositorio. El guion exige las dos
banderas juntas —`--precio-confirmado <USD_por_1000>` y `--ejecutar`— y sin ellas sale en seco
con 0 requests. La clave se lee de `GOOGLE_MAPS_API_KEY`; no se guarda ninguna credencial.

La asimetría queda codificada: `CLOSED_PERMANENTLY` acredita cerrado con fuerza, `OPERATIONAL` no
mueve el estado de nadie.

---

## Lo que espera decisión

1. **La precedencia de los seis solapes nuevos**, empezando por R09 ∩ R19 (60,4 ha, el 64 % de
   Chacarita). Es editorial y cambia conteos.
2. **R19 a 150 m de buffer casi cuadruplica** (+187,6 %). Confirmar el buffer o bajarlo.
3. **Las 24,7 ha de R20** que quedan fuera del tramo que la decisión describe.
4. **`H199 · Yiyo el Zeneize`**: si no es un mercado en actividad, la vía C de `PGR_P004` se cae.
5. **Los cinco veredictos de `vigencia_tanda_A_centro.csv` sin aplicar** —Bar El Federal, Los 36
   Billares, Café Tortoni, Café de los Angelitos, Varela Varelita—. Nunca estuvieron bloqueados
   por el enum y ninguna decisión los nombra, así que quedaron fuera; están listados en
   `veredictos_no_aplicados_r7.csv`. **Dos de ellos son de Monserrat** y su vía B se está midiendo
   con ellos en `sin_verificar`.
6. **Correr Places** con el precio confirmado, o no.
7. **Z23 necesita redelimitación**, ahora con dos motivos y no uno.
8. Siguen de antes los pendientes abiertos de las rondas 3 a 6.
