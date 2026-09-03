# Handoff · Places, los dos polos cortos — 2026-08-21

**Estado: terminado.** No queda trabajo técnico pendiente. Lo que sigue son tres decisiones de
coordinación y, si se toman, aplicarlas en el generador.

## Dónde está todo

- Guion: `scripts/barrido_ciudad/places_completar_dos_polos.py` (sin commitear).
- Entregables y caché: `outputs/analisis_interno/places_dos_polos_2026-08-21/` — Git la ignora.
  - `PLACES_BARRACAS_IRIARTE.csv` · `PLACES_LA_BOCA_ALMIRANTE_BROWN.csv`
  - `BITACORA_PLACES.md` — autorización, SKU, consumo, y los tres defectos de criterio corregidos.
  - `CONTROL_ACEPTACION_39_POLOS.csv` — el conteo polo por polo.

## Lo que se gastó

16 consultas efectivas (17 llamadas HTTP: la primera fue un HTTP 400 que cortó la corrida y no
ejecutó búsqueda). SKU **Pro** en las dos, 5.000 gratis/mes cada uno. **La verificación previa en la
consola de Google Cloud no se hizo** — Diego decidió ejecutar igual. Costo máximo si el cupo
estuviera agotado: USD 0,51.

## Resultado

- **Barracas Z51:** 2 domicilios completados (Rotisería Candela → Vieytes 1387; Parrilla La Familia
  → Av. Iriarte 2101). Piedra Libre: Places no devolvió nada en 50 m. El Amanecer: devolvió
  «El Nuevo Amanecer» en otra calle — **no se adoptó**.
- **La Boca Z52:** 2 nombres adoptados — **Los 3 Amigos** (`LOC001411`, calle y altura exactas,
  3,4 m) y **Pizzeria & Resttaurante Juana** (`LOC021898`, candidato único, 29,1 m).
- Los otros tres nombres que devolvió Places en La Boca —Café Roma, Banchero, La Buena Medida— son
  **las tres referencias que la ficha ya publica**. No son hallazgos.

## Control de aceptación · medido, con los tres escenarios

`CONTROL_ACEPTACION_39_POLOS.csv` · candidatos en `CANDIDATOS_POLOS_CORTOS.csv`

| escenario | llegan a 5 | quedan cortos |
|---|---|---|
| **Hoy** | 35 / 39 | Barracas (2), Nueva Pompeya eje Sáenz (0), Baek-ku (3), Parque Avellaneda (1) |
| **Generando la lista que falta, con el criterio vigente** | 36 / 39 | Barracas (2), Baek-ku (3), Parque Avellaneda (1) |
| **Admitiendo además una sola fuente propia** | **39 / 39** | — |

**Corrección a la primera versión de este handoff.** Dije que Nueva Pompeya · eje Av. Sáenz «no
tiene de dónde sacar lista». Es falso: tiene **8 candidatos con dos o más fuentes**. Muestra 0 por
un motivo administrativo —la lista ratificada de 173 entradas cubrió 37 de los 39 polos y a éste no
lo alcanzó— y el panel de la V7.0 lo resuelve solo, **sin Places y sin decisión**.

Los tres que quedan dependen de **una sola decisión, la misma para los tres**: si un
establecimiento con **una sola fuente propia** puede entrar a la lista. La evidencia de Places no
cuenta como segunda fuente y no mueve el conteo en ningún polo.

## Las decisiones

1. **¿Se listan establecimientos con una sola fuente propia?** Es la que cierra Barracas, Baek-ku y
   Parque Avellaneda de una vez. Si la respuesta es sí, van dos advertencias:
   - **Parque Avellaneda** necesita 4 de sus 5 candidatos, y hay uno de cadena (**Grido**) y dos que
     parecen ventas domiciliarias de Overture (**Amarelloavellaneda**, **bimboatucasa**).
   - **Barracas** además exige listar **Piedra Libre** y **El Amanecer** *sin altura*: Places no
     pudo completarlas, y sobre El Amanecer hay discrepancia de nombre registrada.
2. **¿Se adopta «Pizzeria & Resttaurante Juana»?** 29,1 de 30 m es el borde del criterio, no tiene
   domicilio que verifique, y el nombre trae la errata de Places.

## Para retomar

Reprocesar sin gastar un solo request:

    .venv/Scripts/python.exe scripts/barrido_ciudad/places_completar_dos_polos.py --ejecutar --tope 0

Quedan 3 puntos de La Boca sin consultar (`LOC021889`, `LOC021890`, `LOC021892`), listados como
`NO_CONSULTADO`. Caen a metros de puntos ya consultados: lo previsible es que devuelvan Banchero y
Café Roma otra vez. Consultarlos requiere autorización nueva.

---

# Continuación · 21/08/2026, tarde · auditoría, corrección 01 y preparación ampliada

**Estado: la corrección del piloto está cerrada; la ampliación está preparada y BLOQUEADA.**

## Lo que cambió respecto de arriba

La auditoría independiente (`outputs/analisis_interno/places_dos_polos_2026-08-21/claude_cowork/
auditoria_v1/`) dictaminó **APTO_CON_CORRECCION**. Se aplicó **una corrección puntual**, en
`.../claude_code/correccion_01/`:

- **El «36 / 39» de este handoff está mal y pasa a 35 / 39.** Contaba a «Pizzeria & Resttaurante
  Juana», con una sola fuente propia, dentro de un escenario definido por la exigencia de dos.
  La Boca · Almirante Brown queda en **4**, no en 5.
- **`limite_declarado` de LOC001411** decía «UNA sola fuente propia (F02;PERMISOS)»: son **dos**.
- **El reproceso desde caché ya no exige credencial.** `--ejecutar --tope 0` corre sin clave, y
  `Corrida.pedir()` corta sin credencial aunque el tope lo permitiera.

Verificado con la red bloqueada a nivel de socket: **0 requests, caché intacta, una sola celda
cambiada en los dos CSV**. Detalle en `NOTA_CORRECCION_01.md` y `QA_CORRECCION_01.json`.

**Dos decisiones humanas registradas** en `DECISIONES_HUMANAS_POST_AUDITORIA.csv`, **sin aplicar**:
Los 3 Amigos (LOC001411) es **integrable**; «Pizzería Juana» (LOC021898) se conserva como **señal
externa provisional**, sin publicarse como nombre y sin afirmar vigencia.

## La ampliación, preparada y sin ejecutar

`outputs/analisis_interno/recuperacion_nominal_places_2026-08-21/claude_code/preparacion_v1/`

Cola de los **5.092 SIN_NOMBRE** de la capa post-tandas 03-04: 866 con domicilio completo (Text
Search Pro) y 4.226 sin (Nearby Search Pro), menos **8 reutilizables de la caché del piloto** →
**5.084 consultas nuevas**. Cuatro fases: F1 473 (nominación con domicilio), F2 1.098 (nominación
sin domicilio), F3 1.946 (posibles fusiones), F4 1.575 (ambiguos).

| | fases | consultas | costo máximo |
|---|---|---:|---:|
| piso | F1 | 473 | USD 15,14 |
| estimación | F1 + F2 | 1.569 | USD 50,21 |
| techo | las cuatro | 5.084 | USD 162,69 |

**La ejecución está bloqueada por diseño.** `ejecutar_recuperacion_nominal.py` devuelve 2 mientras
no exista `VERIFICACION_GOOGLE_CLOUD.json` con el saldo del tramo gratuito **de cada SKU** leído en
la consola, con fecha (del día o de los siete anteriores), quién lo leyó y quién autoriza. Los
topes son **duros y separados por SKU**: un SKU agotado no consume el cupo del otro. Probado en
`DRY_RUN.md`, seis casos escalonados, 0 requests.

## Para retomar

1. Leer en la consola el saldo de **Text Search Pro** y **Nearby Search Pro** y cargarlo en
   `VERIFICACION_GOOGLE_CLOUD.json`. Sin eso no se consulta nada.
2. Decidir el alcance: F1 sola, F1+F2, o la cola entera.
3. Pendiente de fondo, sin resolver: **si un nombre cuyo único origen es Places puede publicarse**.
   Hoy el Atlas afirma que ninguna plataforma privada aportó al inventario.

El reparto entre Text y Nearby de las ~306 llamadas Pro anteriores del repositorio **no está
registrado**, y por eso no se puede afirmar que la cola entre en el tramo gratuito.
