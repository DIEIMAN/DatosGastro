# HANDOFF · Ronda 6 · dos verificados, un falso positivo probado, y un barrio que no era · 2026-08-07

Continúa `HANDOFF_POLOS_RONDA_5_2026_08_07.md` (misma fecha). Rama `mercados-gastronomicos-v2`.
**Google Places: 0 requests.** USIG: 2 consultas de `/datos_utiles` sobre puntos ya normalizados,
cacheadas. Dos verificaciones humanas de Diego, y las consecuencias que traen —medidas, no
heredadas. Geometría de polos, agrupamientos, fichas y cartografía: **no tocados.**

**Script nuevo: `scripts/barrido_ciudad/ronda_6_vigencia_villa_luro_almagro.py`.** Salidas:
`hitos_capa_2026_r6.csv` (221 filas, 32 columnas), `cambios_ronda_6.csv` (11 cambios),
`RONDA_6.txt`, `donde_caen_los_dos_hitos_r6.csv`, `almagro_cinco_notables_r6.csv`.

---

## Lo que cargó Diego

| hito | establecimiento | dirección | antes | ahora |
|---|---|---|---|---|
| H028 | Café Olimpo | Irigoyen 1491 | `estado_operativo_pendiente` | `si` · v2 |
| H045 | 12 de octubre (El Boliche de Roberto) | Bulnes 331 | `sin_verificar` | `si` · v2 |

`verificado_abierto` es el vocabulario de la tanda; en la capa el estado abierto se escribe `si`
desde siempre, y el nivel va aparte en `vigencia_nivel`.

**La de Café Olimpo cierra el último `estado_operativo_pendiente` de la capa** — el estado que la
ronda 5 había creado para él, y el caso que el documento de Places citaba como «el que por sí solo
justifica correr Places». Se resolvió con una verificación humana y 0 requests. La estimación de
costo sigue en pie para las otras 28 fichas de las tandas A+B, pero **ya no tiene su caso testigo**.

---

## Lo primero, porque contradice lo que veníamos escribiendo

**Café Olimpo no está en Villa Luro. Está en Monte Castro.**

El anexo de la Res. 1225/26 lo asienta en Villa Luro, Comuna 10, y de ahí venía la frase «es el
único Bar Notable de Villa Luro; si cerró, Villa Luro desaparece entera del Atlas». La dirección es
correcta y el establecimiento existe. El barrio no.

El callejero oficial del GCBA reparte la calle Irigoyen **por altura**, y la calle atraviesa cuatro
barrios:

| altura (impar) | lado impar | lado par |
|---|---|---|
| 1–499 | Villa Luro | Villa Luro |
| 501–1299 | Villa Luro | Versalles |
| **1301–1799** | **Monte Castro** | Versalles |
| 1801–1899 | Villa Real | Versalles |
| 1901–2599 | Villa Real | Villa Real |

**Villa Luro se termina en el 1299.** El 1491 cae dos cuadras más allá. Y no es un problema del
punto: la esquina que cita la ficha —Irigoyen y Arregui, resuelta por intersección de ejes del
callejero— está a 16 m de donde USIG había geocodificado la dirección, sobre el límite Monte Castro
/ Versalles, a **262 m de Villa Luro**. USIG `/datos_utiles` sobre el punto responde **Monte Castro,
Comuna 10**.

**Por qué no se veía:** Villa Luro, Monte Castro y Versalles son las tres Comuna 10. La comuna del
anexo era correcta, así que cualquier control por comuna lo daba por bueno. El defecto es de barrio
y sólo se ve a escala de barrio.

Es la **tercera instancia de FD-02** (La Academia, Roma del Abasto, Café Olimpo) y cierra el
pendiente 3 de la ronda 5: el campo territorial del catálogo falla en las tres, siempre por lo
mismo —se llenó por nombre de calle o zona aproximada, nunca por altura.

`barrio_declarado` de H028 pasa de vacío a **Monte Castro**, con la marca FD-02 registrada.

---

## Las dos consecuencias, medidas

La carga venía con dos afirmaciones. Ninguna se copió: las dos se comprobaron contra geometría.

### «Villa Luro conserva su vía B» — no, y por dos motivos independientes

El hito no está en Villa Luro (arriba). Y aunque lo estuviera, **no entra a la fila**: Café Olimpo
queda a **1.532 m** del polígono de `PGR_P020 · P020 · Villa Luro` (25,1 ha), afuera de las 94 filas
de la matriz y afuera de las 22 envolventes.

### «Almagro recupera los cinco notables» — cierto a escala de barrio, todavía no en la capa

El polígono administrativo de Almagro contiene exactamente cinco Bares Notables. Pero en la capa,
hoy, sólo uno está verificado:

| hito | nombre | dirección | estado en la capa | a `PGR_P083` |
|---|---|---|---|---|
| H063 | La Orquídea | Av. Corrientes 4101 | `sin_verificar` | 74 m |
| H045 | 12 de octubre | Bulnes 331 | **`si` · v2** | 469 m |
| H054 | El Símbolo | Av. Corrientes 3787 | `sin_verificar` | 518 m |
| H071 | Las Violetas | Av. Rivadavia 3899 | `sin_verificar` | 666 m |
| H044 | El Banderín | Guardia Vieja 3601 | `sin_verificar` | 747 m |

Los otros cuatro **sí** tienen veredicto —Las Violetas y El Banderín v3, El Símbolo v2 por Diego,
La Orquídea v5— pero ese veredicto vive en `desde_cowork/evidencia_2026/`, que es insumo producido
afuera y **no se aplicó a la capa**. Esta ronda cargó sólo las dos verificaciones pedidas. Mientras
no se apliquen, «Almagro recupera los cinco» es cierto en el registro de la tanda y falso en la capa.

### Y lo que ninguna de las dos mueve

**La vía B medida no cambia.** Desde la ronda 3 la vía B se mide por presencia dentro del polígono
de la fila, y **ninguno de los dos hitos está adentro de ninguna de las 94 filas ni de ninguna de
las 22 envolventes**. `PGR_P020` y `PGR_P083` siguen en `sin_hitos`.

Lo que la carga salva es la lectura de **escala de barrio** (Z31, Z37) —la unidad que usa la
asignación heredada de vía E—, que no es la fila de la matriz. La diferencia de tamaño lo explica
solo: Almagro barrio son 405,3 ha y `PGR_P083` son **5,7 ha**; ninguno de los cinco Notables del
barrio está adentro, y el más cercano queda a 74 m.

**Esto no es un detalle de contabilidad.** Es la brecha entre las dos escalas con las que venimos
trabajando, y esta ronda es la primera vez que se ve con nombres propios en las dos puntas.

---

## FD-12 pasa a la capa canónica, con caso probado

La marca de Yelp «EL BOLICHE DE ROBERTO - CLOSED - Updated July 2026» **era falsa**. Diego verificó
el establecimiento abierto el 07/08/2026.

FD-12 estaba identificada en el material producido afuera como «visible e inauditable» —el dominio
bloquea por `robots.txt` y no se puede abrir la ficha para saber de cuándo es la marca ni de dónde
salió—. Ahora entra a `fuentes/fuentes_defectos_conocidos.csv` (que pasa de 4 a 5 defectos) con la
evidencia que la prueba, más la marca aplicada sobre H045 en `fuentes_marcas_aplicadas.csv`.

**La regla no cambia** —se registra, nunca se convierte en veredicto— pero deja de ser una
precaución y pasa a ser un hecho medido.

**Y rompe el patrón de las otras cuatro, que conviene no disimular.** FD-01 a FD-04 son errores del
documento sobre sí mismo: una fecha de actualización, un campo de barrio, un número de resolución.
FD-12 es una **afirmación sobre el establecimiento**, del tipo que normalmente sí acreditaría, y en
el sentido que más cuesta ignorar: nadie duda de un «cerrado». Quedó escrito en la sección de la
edición técnica.

---

## Archivos tocados esta ronda

- `outputs/BARRIDO_CIUDAD_2026-08/hitos/hitos_capa_2026_r6.csv` (nuevo, 221 filas, 32 columnas)
- `outputs/BARRIDO_CIUDAD_2026-08/hitos/cambios_ronda_6.csv` (nuevo, 11 cambios)
- `outputs/BARRIDO_CIUDAD_2026-08/hitos/RONDA_6.txt` (nuevo)
- `outputs/BARRIDO_CIUDAD_2026-08/hitos/almagro_cinco_notables_r6.csv` (nuevo)
- `outputs/BARRIDO_CIUDAD_2026-08/seis_vias/donde_caen_los_dos_hitos_r6.csv` (nuevo)
- `outputs/BARRIDO_CIUDAD_2026-08/fuentes/fuentes_defectos_conocidos.csv` (+FD-12)
- `outputs/BARRIDO_CIUDAD_2026-08/fuentes/fuentes_marcas_aplicadas.csv` (+2 marcas: FD-12/H045, FD-02/H028)
- `outputs/BARRIDO_CIUDAD_2026-08/fuentes/SECCION_EDICION_TECNICA_FUENTES_CON_DEFECTOS.md` (FD-12, tercera instancia de FD-02, criterio general corregido)
- `outputs/BARRIDO_CIUDAD_2026-08/seis_vias/_cache_usig_datos_utiles.json` (+2 consultas)
- `scripts/barrido_ciudad/ronda_6_vigencia_villa_luro_almagro.py` (nuevo)

---

## Lo que espera decisión

1. **Aplicar el resto del registro del día a la capa.** `vigencia_cierre_del_dia.csv` y
   `vigencia_tanda_B_almagro_norte.csv` traen once veredictos más con evidencia y verificador —entre
   ellos los cuatro Notables de Almagro que faltan—. Tres cosas a resolver antes de aplicarlos en
   bloque: (a) `probablemente_abierto` no existe en el enum de la capa y hay que decidir si entra o
   si mapea a `dudosa` con `vigencia_sentido_duda`; (b) El Símbolo tiene dos niveles distintos entre
   los dos archivos (v4 `probablemente_abierto` en tanda B, v2 `verificado_abierto` en cierre del
   día); (c) **El Cedrón (DIR-011) está `si` en la capa y `dudoso` en el registro de la tanda** — eso
   es una contradicción, no un dato faltante.
2. **Villa Luro se queda sin Bar Notable.** Con Café Olimpo en Monte Castro, el barrio no tiene
   ninguno: hay que revisar cualquier texto que sostenga la vía B de Villa Luro en ese hito. El
   único que lo dice hoy es material de cowork (`PARA_CHEQUEAR_DIEGO.csv`), no salidas del
   repositorio; ninguna afirmación repo-side quedó pendiente de corregir.
3. **Monte Castro suma su segundo hito** (Café Olimpo, junto a El Fortín / DIR-002, que también se
   verificó abierto el 07/08). No se recalculó nada de Z28 con esto.
4. **La estimación de Places sigue vigente pero perdió su caso testigo.** Decidir si se corre igual
   el subconjunto de 28 restantes o si la verificación humana lo reemplaza.
5. Siguen de antes: los cinco pendientes abiertos de la ronda 5 (derivados de `hitos_capa_2026_r3`
   que puedan citar la fila vieja «Café Roma / San Luis 3101», El Sol de Galicia con la dirección
   vieja en archivos de vía B, El Greco y Josephina's Café sin resolver) y los puntos abiertos de
   las rondas 3 y 4.
