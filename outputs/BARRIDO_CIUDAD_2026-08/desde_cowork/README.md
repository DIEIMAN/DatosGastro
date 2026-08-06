# Producido afuera del repositorio · Cowork

**6 de agosto de 2026.** Lo que se hizo del lado que tiene red y criterio, mientras el
repositorio corría datos y geometría. Todo lo de acá es **insumo**: nada de esto se generó
corriendo código sobre los datos.

---

## Qué hay

| archivo | qué es | estado |
|---|---|---|
| `EDICION_TECNICA_METODO.md` | **La edición técnica.** Diez partes y un anexo: de dónde sale cada número del Atlas y del barrido, con las curvas, los controles y los que fallaron | completo |
| `ATLAS_V3_SECCIONES_I_IV_VII.md` | El **texto del Atlas V3**: presentación, qué es un polo, de dónde salen los datos, cómo se leyó el territorio, y qué no dice este atlas | completo · no depende de las fichas |
| `FICHA_Y_ESTRUCTURA_V3.md` | La **plantilla de las 124 fichas** y el esqueleto del documento, con las 5 decisiones editoriales pendientes | completo |
| `NOMBRAR_LOS_POLOS.md` | La regla para nombrar los 124, la respuesta a **dónde está Soho**, y el hallazgo sobre el sur | completo · espera `POLOS_PARA_NOMBRAR.csv` para aplicarse |
| `diccionario_nombres_uso_corriente.csv` | **72 nombres** de áreas gastronómicas de CABA en 4 niveles, con límites de calles y fuente | completo |
| `hitos_documentales_caba.csv` | **199 distinciones sobre 189 establecimientos**, 6 capas, con fuente y licencia por fila | falta geocodificar |
| `HITOS_DOCUMENTALES_LEEME.md` | Cómo usar el anterior y sus 9 advertencias | completo |
| `DECISION_P078_Y_SALIENTE.md` | El razonamiento de por qué la excepción de P078 no se firmaba | cerrado — el repo lo resolvió por estabilidad |

---

## Lo primero que hay que hacer con esto

### 1 · Reconciliar los bares notables · NO duplicar

Este repositorio **ya tiene** `dataset_bares_notables/` con **95 filas desde Wikidata (CC0),
geocodificadas con USIG**. Eso es mejor que lo que trae `hitos_documentales_caba.csv` en ese
rubro, por dos razones: la licencia es redistribuible y los puntos ya existen.

**El dataset de Wikidata manda.** De las 90 filas `bar_notable` de `hitos_documentales_caba.csv`
—que vienen del catálogo consolidado del Boletín Oficial— sólo hay que incorporar **las que
Wikidata no tenga**, cotejando por nombre normalizado y dirección. Las dos listas no coinciden
exactamente y ninguna es superconjunto de la otra:

- Wikidata declara explícitamente ser un **listado NO exhaustivo**.
- El catálogo del Boletín Oficial es el registro administrativo, pero **no publica el año de
  declaratoria** (falta en 88 de 90) y tiene inconsistencias propias de comuna, anotadas fila por
  fila en la columna `nota`.

**Las otras 109 filas no se solapan con nada:** 58 Michelin 2026, 16 rankings 50 Best, 20
pizzerías emblemáticas, 5 heladerías y 10 mercados y patrimonio. Ésas entran enteras.

### 2 · La regla de licencia, que no cambia

Ninguna de las fuentes nuevas es CC-BY. **No se redistribuye nada.** Entra el **hecho** —este
local tiene esta distinción— con la cita de la fuente. No entra texto descriptivo de Michelin ni
de 50 Best. Es el mismo criterio del nivel `agregado` que se usó con Places.

### 3 · Al geocodificar

- **27 filas no tienen dirección** (pizzerías y heladerías): geocodificar por nombre + barrio. Si
  no resuelve a un local único, **se descarta la fila**. No se elige la más probable. Reportar
  cuántas cayeron.
- **Un conflicto de dirección real:** Crizia figura en Fitz Roy 1819 (ViaMichelin) y en Gorriti
  5143 (50 Best). Resolver contra la base; si son dos locales, son dos filas.
- `clave_dedup` agrupa el mismo local con varias distinciones. **9 lo tienen**, y ésos van primero
  en la ficha.

---

## Los tres hallazgos que cambian el producto

**1 · La nomenclatura oficial tampoco llega al sur.** Turismo BA nombra cinco polos
gastronómicos —Soho/Hollywood, Cañitas, Puerto Madero, Recoleta y San Telmo—: ninguno en el oeste
y sólo San Telmo en el sur. La literatura académica de referencia llega a la misma lista. **El
vacío del Atlas V2 no fue un error de relevamiento: fue heredar un vocabulario sin palabras para
el sur.** Está escrito así en la sección I del Atlas V3.

**2 · Hay anclaje normativo para nombrar el sur.** El **Distrito del Deporte (Ley 5235/2014)** es
el único instrumento con perímetro publicado que nombra territorio en las comunas 8 y 9. Con el
Tecnológico (Ley 2972), el de las Artes (Ley 4353) y el de Diseño (Ley 4761) se cubre buena parte
del sur con nombres de nivel 1.

**3 · R18 se llama «Esmeralda-Paraguay» y nadie usa ese nombre.** No aparece como microzona
gastronómica en ninguna fuente. La concentración existe —es la clase A más densa de las 22— pero
el nombre es descriptivo porque no había uno. Conviene declararlo así en la V3.

---

## Y una confirmación por otro camino

La prueba 3 midió que P078 no tiene ninguna calle de Soho. La documentación coincide: **Av. Juan
B. Justo divide Palermo Viejo, y Humboldt, Fitz Roy y Bonpland caen del lado de Hollywood.**
Medición y documento llegan al mismo lugar sin haberse consultado.

Con una trampa para la Tarea 2: **Honduras, Gorriti, Costa Rica, Nicaragua, El Salvador, Cabrera
y Guatemala cruzan Juan B. Justo y tienen tramos de los dos lados.** Son neutrales. Hace falta
calle + altura. Es la misma familia de error que los tres bugs del normalizador.

Punto de control: **Don Julio está en Guatemala 4699, en Soho.** El polo que lo contenga es Soho,
salvo que el clustering lo haya partido.

---

## Qué falta de este lado

- Aplicar el diccionario a los 124 → espera `POLOS_PARA_NOMBRAR.csv`
- Las 124 fichas → esperan nombres y polígonos
- Secciones V, VI y VIII del Atlas → esperan las fichas
- La edición técnica a `.docx` con formato de la Dirección
