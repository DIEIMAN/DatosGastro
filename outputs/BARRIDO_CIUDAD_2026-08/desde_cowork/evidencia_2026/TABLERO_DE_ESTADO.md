# Tablero de estado · Atlas V3

**9 de agosto de 2026 · construido leyendo el disco, no la memoria**

> **Este archivo reemplaza a `HANDOFF_ATLAS_V3_CONTEXTO.md`.** Aquél se escribió sin leer el repositorio y quedó atrás de dos rondas el mismo día que se escribió. **Si los dos dicen cosas distintas, manda éste.**
>
> **Y una regla para que esto no vuelva a pasar: este archivo se actualiza antes de reportar cualquier trabajo, no después.** Un hallazgo que no está acá no existe para la próxima sesión.

---

# 0 · Por qué se repitió trabajo, y cómo se corta

**El diagnóstico, sin vueltas:** hay tres actores escribiendo —Cowork, el repositorio y Diego— y **ningún lugar único que diga qué está resuelto**. Todo lo que se produjo hasta hoy es *narrativa de un momento*: un handoff, una auditoría, una ronda N. Ninguno es un **tablero**. Entonces cada actor nuevo vuelve a deducir lo que ya estaba deducido.

**Los cuatro casos concretos de trabajo rehecho, para que se vea el patrón:**

| se rehizo | ya estaba resuelto en |
|---|---|
| el conteo de Monserrat | ronda 7, medido por geometría — la ronda 9 lo contradijo con otro método y nadie lo notó hasta la ronda 10 |
| «qué son los 407 de Palermo» | ronda 9 y ronda 10 — el handoff los etiquetó mal y con eso bloqueó diez fichas |
| los 76,1 m y los 1.100 m² de la lámina 5 | ronda 7, tarea 5e — se pidieron como «que falta verificar» |
| la tabla de numeración de secciones | estaba en la cabecera del propio archivo que la auditoría citaba |

**Las tres reglas que lo cortan:**

1. **Nada se trabaja si no está en la sección 3 de este tablero.** Si aparece algo nuevo, primero se agrega acá.
2. **Antes de abrir una pregunta, se busca en la sección 2.** Si está ahí, está cerrada y no se reabre sin evidencia nueva.
3. **Quien produce, actualiza el tablero en el mismo movimiento.** No al final del día.

**Y hay una cuarta que es de esta situación puntual, y es la más urgente:**

> **Hay dos sesiones de Cowork escribiendo sobre la misma carpeta.** Ésta y la nueva. La nueva tiene lectura directa del repositorio, corrió la auditoría del 09/08 y está al día; **ésta está dos rondas atrás.**
>
> **Recomendación: seguir con la nueva y cerrar ésta.** Dos Cowork sobre el mismo repositorio es una máquina de duplicar exactamente lo que este tablero viene a evitar. Este archivo es mi entrega final; no debería producir contenido nuevo después de esto.

---

# 1 · El reparto, sin ambigüedad

| | **Diego** | **Cowork** | **El repositorio (Claude Code)** |
|---|---|---|---|
| **qué hace** | decide, verifica en la calle y en redes, valida el tono | investiga fuentes, fija criterio, redacta, audita | mide, corre, cruza geometría, versiona |
| **qué NO hace** | no escribe el documento | **no mide geometría ni corre nada** | no decide criterio ni redacta el documento |
| **lo único que sólo él puede** | Instagram/Facebook/TikTok, la calle, la firma | leer prensa y fuentes públicas, y escribir | tocar el dato y git |

**Reglas de frontera que ya costaron caro:**

- **Cowork no afirma el contenido de un archivo que no leyó.** Tiene lectura directa del repositorio por el puente: **se lee, no se recuerda.** Cinco errores salieron de saltarse esto.
- **Cowork no publica sobre una fuente provisoria si ya pidió la definitiva** (R16). Las láminas 14 y 15 se escribieron sobre un PDF el mismo día que el repositorio ya tenía la planilla.
- **El repositorio no toma decisiones de criterio**, y hace bien: cuando el Patio Costanera Norte quedó entre la letra y el espíritu, lo devolvió en vez de elegir.
- **Diego no verifica lo que ya está verificado.** Ver la sección 2 antes de salir a caminar.

---

# 2 · CERRADO · no volver a abrir

Cada línea tiene su archivo. **Si alguien vuelve a preguntar esto, la respuesta es «está cerrado, mirá tal archivo».**

## Delimitación y geometría

| pregunta | respuesta | dónde |
|---|---|---|
| ¿Qué son los 407 de Palermo? | **Son los locales de Soho ∪ Hollywood que caen FUERA de R01.** No son de R01. Los de R01 que no están en las subzonas son 398 contra dos y **188 contra las tres**, en 8 piezas | `ronda_9/`, `ronda_10/palermo_residuo_por_zona.csv` |
| ¿Palermo opción A o B? | **A.** La B perdería locales publicados. Contención verificada por superficie perdida **0,0 m²** — `covers()` da False y por eso no se usa (R12) | ronda 10 |
| ¿La pieza 1 es una de las subzonas sin medir? | **No.** La hipótesis se corrió y se cayó. Sigue sin nombre | `ronda_13/palermo_seis_subzonas.csv` |
| ¿La pieza 3 se solapa con R08? | **No. R08 está a 6 m y no se tocan.** Es artefacto de borde, no filtración. No hay nada que repartir | ronda 13 |
| Soho: ¿728 o 772 locales? | **772 manda para cualquier cosa cartográfica**, porque es el del polígono. 728 es el clúster | ronda 13 |
| ¿Cuántos Notables tiene Monserrat? | **9**, medido por geometría. El «2» salía de filtrar por `barrio_declarado`, que es texto de la fuente (R13). **La lámina 7 se destraba** | ronda 7, reconciliado ronda 10 |
| ¿La vía C de Almagro abre? | **NO ABRE.** No hay ningún mercado dentro de su polígono; lo único cerca es una feria itinerante. **La lámina 4 dice cinco vías, no seis** | `ronda_13/via_C_almagro.csv` |
| ¿Cuántas filas abren vía C? | **2 filas de 94** (PG001B, PG008) y **3 zonas de 22** (Bonpland, Belgrano, del Progreso). El arrastre de `PGR_P004` lo cerró la ronda 10 | ronda 13, control de arrastre |
| ¿La cola de R20? | **47 % de la superficie y 30 % de los locales** — 28,63 ha, 31 locales. Se conserva, y se declara | ronda 12 |

## Vigencia y referentes

| pregunta | respuesta | dónde |
|---|---|---|
| ¿Estado del catálogo de Notables? | **90 de 90 verificados. 86 abiertos · 1 en quiebra operando · 1 en riesgo · 2 cerrados. Operan 88** | `catalogo_90_estado_final.csv` |
| ¿Cuáles son los 2 cerrados? | **Plaza Bar** (Florida 1005, desde abril de 2017 — nueve años) y **La Buena Medida** (Suárez 101, desde octubre de 2025) | ídem |
| ¿The New Brighton está cerrado? | **No.** Quiebra decretada y **sigue atendiendo**. Un acto jurídico no es un hecho operativo (FD-20) | ídem |
| ¿El Palacio de la Papa Frita cerró? | **No: se mudó** de Av. Corrientes 1612 a Paraná 350. Lo que se perdió es la dirección distinguida | errata 08/08 |
| ¿Sirve la corrida de Places de la ronda 8? | **No. Se da por perdida entera.** Sin `displayName`, ninguno de los 71 resultados tiene referente conocido — incluido el único `CLOSED_PERMANENTLY` | ronda 9 |
| ¿Se pueden citar los 54 que verificó Diego? | **Resuelven filas, no se citan solos.** 32 citables con fecha propia, 58 no | `hitos_capa_2026_r11.csv`, campo `citable_en_documento` |

## Fuentes y láminas

| pregunta | respuesta | dónde |
|---|---|---|
| ¿Cuántos ejes tiene el IDECBA? | **48 vigentes. La serie manda, el PDF no** (FD-23). **«Microcentro» no existe entre los 48** | `ronda_12/idecba_48_autoridad.csv` |
| ¿«Los polos consagrados son los que más pierden»? | **Refutado.** −1,69 contra −1,30, 21 y 21: no hay brecha | ronda 12 |
| ¿«La brecha no es norte-sur»? | **Refutado, y es al revés:** Norte 0 de 9 suben, Sur 7 de 13 | ronda 12 |
| ¿Los 76 m y los 1.100 m² de la lámina 5? | **Ya medidos.** Máxima 76,1 m (Plaza Asturias–El Imparcial); envolvente 0,110 ha | ronda 7, tarea 5e |
| ¿Hay que cargar Plaza Asturias y El Globo como hitos? | **No, y es decisión de la ronda 7**: no tienen registro oficial. **Cargarlos sería lo incorrecto.** Lo que sí falta es su vigencia | ronda 7 |
| ¿La lámina 7 está en suspenso? | **No.** Se destrabó con la reconciliación de Monserrat. **La v2.1 todavía dice que sí y hay que corregirlo** | ronda 10 |
| ¿Falta escribir la Nota metodológica? | **No: está escrita y completa.** Lo que falta es decidir qué número lleva | `ATLAS_V3_SECCIONES_V_VI.md` |
| ¿Hay dos numeraciones del documento? | **No son dos numeraciones: son dos proyectos de documento.** El de las 124 fichas (06/08) y el de las 41 (08/08). Cada uno coherente por dentro | `DOS_PROYECTOS_DE_FICHA.md`, `correspondencia_fase_documental.csv` |
| ¿Está todo bajo git? | **Sí, desde la ronda 13.** Y `git status` desde el puente miente por CRLF: usar `git -c core.autocrlf=true` | ronda 13 |

---

# 3 · ABIERTO · con dueño y con qué destraba

## Espera decisión de Diego · nada avanza sin esto

| # | qué hay que decidir | qué destraba |
|---|---|---|
| **D1** | **¿Cuál de los dos proyectos de ficha es el cuerpo del documento** — las 41 en prosa o las 124? | **Es más grande que todo lo demás junto.** Define qué se escribe y qué se anexa |
| **D2** | **Nombre y perímetro declarado de la pieza 1 de Palermo.** Propuesta en mesa: «Palermo — eje Av. Santa Fe», que explica 75 de sus 134 locales en un tercio de la superficie | cierra Palermo y con él ~4 fichas |
| **D3** | **Las 8,09 ha y 7 locales de doble conteo** entre R01 y Chacagiales (piezas 5 y 7) | cierra el nudo de Chacagiales |
| **D4** | **Dónde va la Nota metodológica**, que está escrita y no tiene número | cierra la estructura del documento |
| **D5** | **ERR-08 y ERR-09** — esperan firma. Ninguna cambia un veredicto de admisión | limpieza |
| **D6** | **Los pares `_sin_contacto`**: hay `PARA_CHEQUEAR_DIEGO.csv` y `PARA_CHEQUEAR_DIEGO_sin_contacto.csv` conviviendo. **Si quedan los dos, alguien va a citar el que tiene teléfono** | seguridad de datos |
| **D7** | **¿Se corta la dependencia de Palermo?** Publicar las fichas bloqueadas con perímetro en revisión y sin cifra agregada. **No se resigna nada** —hoy tampoco se puede afirmar cuántos locales tiene Palermo— y destraba el resto | **es la palanca que más acorta el proyecto** |

## Le toca al repositorio

- **La vía C de Z40 Nueva Pompeya** — mismo defecto que Almagro: abre sin nombrar el objeto. Señalado en la ronda 13 y no resuelto.
- **El perímetro de Colegiales sobre la cuña real** — Zabala 254 m y Virrey Avilés 344 m son los únicos cruces con tramo verificable. **Tres cuadras, no diez.** Álvarez Thomas y Forest se tocan a 0 m.
- **R08 ∩ R21** — 49,7 ha entre Villa Crespo y La Paternal.
- **Los 10 `requiere_cruce` de la vía E** — es un cruce espacial, no investigación. Llevaría la vía E de 84 % a ~95 %.
- **La vía B recorrida contra el catálogo cargado** — cero requests, y los pendientes eran mayormente `sin_verificar`.
- **Las 5 zonas pendientes de límites.**

## Le toca a Cowork

- **30 de las 41 fichas** (11 escritas). Depende de D1.
- **La sección VIII**, lo que se midió y no alcanzó.
- **Consolidar la edición técnica** con las rondas 8 a 13.
- **Corregir la cabecera de la v2.1**, que sigue diciendo que la lámina 7 está en suspenso.
- **Los niveles de nombre de los 41**, que el cruce automático no resuelve.

## Le toca a Diego

- **Las tres caminatas** — Montes de Oca 280–1702 (es la lámina 12 y nadie midió la continuidad), Av. Rivadavia en Flores (y qué proporción del eje es gastronomía), Las Cañitas (361 nuestros contra 97 de La Nación).
- **La vigencia de Plaza Asturias y El Globo** — es lo único que le falta a la lámina 5.
- **Las siete decisiones de arriba.**

---

# 4 · Lo que no se toca

El criterio de admisión, las escalas de evidencia, las 16 reglas y los 23 defectos de fuente **están cerrados y documentados**. Viven en `EDICION_TECNICA_METODO.md`, `EDICION_TECNICA_FASE_DOCUMENTAL.md` y `agent_skills/shared/datagastro_metodo_experimental.md`.

**Lo mínimo que hay que tener presente al producir:**

**Las seis vías** — se entra por cualquiera. **A, C y F se miden sobre el polígono; B, D y E sobre la zona**, y las filas las heredan por referencia. **La herencia no vale hacia arriba.**

**Vía C** — se abre por **centralidad**, no por concentración de oferta bajo un techo. La prueba: *¿el objeto organiza su entorno, o fue puesto en él?*

**Vigencia** — v1 a v5 con veredictos. **Un acto jurídico no es un hecho operativo. La evidencia negativa se busca. Toda verificación vence y lleva su fecha pegada al texto.**

**Los números que se pueden sumar** — los 124 polígonos son disjuntos (solape 0,0 %) y dan **12.688 locales en 3.128,5 ha = el 53 % de la gastronomía en el 15 % de la superficie**. **La matriz de 94 filas NO se suma nunca.**

**La pregunta cero, antes de afirmar cualquier cosa:** *¿esto es una propiedad del territorio o de mi instrumento?* Ya falló seis veces y siempre en la misma dirección: la lectura territorial es la más noticiosa.

**Y las restricciones de Diego:** el bloque para el repositorio va último · no se piden fuentes internas · nunca «Atlas V2» en el documento · las 22 referencias sólo se amplían · nada se descarta sin detallar qué sería.

---

# 5 · Dónde está cada cosa · verificado en disco el 09/08

```
outputs\BARRIDO_CIUDAD_2026-08\
├── desde_cowork\                    ← EDICION_TECNICA_METODO.md
│   │                                  ATLAS_V3_SECCIONES_I_IV_VII.md
│   │                                  ATLAS_V3_SECCIONES_V_VI.md  (nota metodológica)
│   │                                  DOS_PROYECTOS_DE_FICHA.md · POLOS_NOMBRADOS.csv
│   └── evidencia_2026\              ← todo lo demás de Cowork (99 archivos)
│                                      INDICE.csv · correspondencia_fase_documental.csv
│                                      INDICE_DE_VERSIONES.md
│                                      AUDITORIA_DE_ESTADO_2026-08-09.md
│                                      catalogo_90_estado_final.csv
│                                      LAMINAS_v2_2026-08-08.md  (v2.1)
│                                      FICHAS_SECCION_VII_TANDA_1.md  (11 de 41)
├── hitos\hitos_capa_2026_r11.csv    ← 225 × 46 · la capa vigente
├── seis_vias\seis_vias_94_filas_r12.csv y _22_zonas_r12.csv
├── ronda_9..13\                     ← las narrativas y sus CSV
└── idecba\                          ← crudos · la serie de 48 manda
```

**Ojo:** `hitos/`, `seis_vias/`, `ronda_*/` e `idecba/` **cuelgan de `BARRIDO_CIUDAD_2026-08`, no de `evidencia_2026`.** El handoff los ubicaba mal.

---

# 6 · Los porcentajes, al 09/08

| frente | estado |
|---|---|
| criterio de admisión | **100 %** |
| cobertura geográfica | **100 %** — 15 comunas |
| **vigencia del catálogo** | **100 %** — 90 de 90 |
| vía E medida | **84 %** — 79/94, con 10 `requiere_cruce` que son un cruce |
| vía B medida | **67 %** — 63/94, y **sube solo** al recorrerla contra el catálogo |
| delimitación de polos | **~85 %** — Palermo casi cerrado, Colegiales y R08∩R21 abiertos |
| **documento** | **el cuerpo está en 11 de 41 fichas** — y depende de D1 |
| edición técnica | **~90 %**, con las rondas 8 a 13 por incorporar |
| presentación | **v2.1**, con la lámina 4 a cinco vías y la cabecera de la 7 por corregir |

**El cuello de botella ya no es el dato: es el documento, y está esperando una decisión —D1— que no la puede tomar ninguno de los dos Claude.**
