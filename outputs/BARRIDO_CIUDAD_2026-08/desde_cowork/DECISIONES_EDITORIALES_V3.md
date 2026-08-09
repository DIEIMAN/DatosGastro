# Decisiones editoriales del Atlas V3

**Tomadas por Diego el 6 de agosto de 2026.** Quedan cerradas: no se reabren salvo que aparezca
un impedimento concreto, y si aparece se anota acá con su motivo.

---

## 1 · Los 74 polos sin nombre propio → **«Nombre propuesto», dicho UNA vez**

Se acepta la clasificación en cuatro niveles, **pero no va una leyenda debajo de cada ficha.** Se
declara **una sola vez**, al abrir la sección V, y las fichas quedan limpias.

Cómo se implementa, que es lo mínimo que funciona:

- Al abrir la sección V va un párrafo: *«De las 124 concentraciones, 50 llevan un nombre
  reconocido o de uso corriente. Las 74 restantes están marcadas con ° y llevan un nombre
  propuesto: no se identificó para ellas una denominación de uso corriente, y la definitiva la
  define el programa de identidad y marca.»*
- En la ficha, el nombre lleva un **°** y nada más. Sin línea, sin nota al pie, sin repetir.
- El nivel completo (1 a 4) y su fuente quedan **en la capa de datos**, para quien quiera el
  detalle.

**Por qué el símbolo y no nada.** Sin ninguna marca, el lector no puede saber cuáles son los 74, y
la declaración única se vuelve decorativa. Un carácter, explicado una vez, alcanza — y no ensucia
124 fichas.

**Y no es irreversible.** Cuando el programa de marca bautice una zona, se le saca el ° y se le
carga el nombre. La capa de datos ya está preparada para eso.

## 2 · La capa de datos → **se publica completa**

Polígonos en GeoJSON y tabla de los 124 con sus atributos.

**Lo que esto obliga a resolver antes de publicar**, y es trabajo real:

- **Licencia campo por campo.** Los tres niveles ya están definidos: `abierto`, `punto`,
  `agregado`. Ningún punto de Google Places ni de fuente no redistribuible sale del repositorio.
- **Los atributos agregados por polo sí salen** —conteo, superficie, densidad, clase, ejes,
  hitos— porque son agregados y no reconstruyen ninguna base de origen.
- **Falta decidir el formato de publicación**: si va por BA Data, como anexo del documento, o
  ambos. Eso es institucional, no técnico.

## 3 · Cartografía → **mapa general + uno por comuna**

El general es el que va a la lámina 11 del Plan y el que se va a fotografiar. Los quince de
comuna abren cada capítulo de la sección V.

**Orden de producción:** primero el general, porque es el que tiene fecha; los quince después.

## 4 · Fotos en las fichas → **no van**

124 fotos es mucho trabajo, y sobre todo: **cualquier criterio de qué se fotografía privilegia lo
pintoresco**, y el sur vuelve a quedar mal parado en un atlas que vino a corregir exactamente eso.

Si en algún momento se quiere ilustrar, la vía que no rompe la comparabilidad es un croquis de las
calles principales, igual para los 124.

## 5 · Numeración → **desde cero**

Consecuencia de que el documento se sostiene solo y no se compara con nada anterior. Los `polo_id`
del borrador se conservan en la capa de datos como trazabilidad interna, no en el documento.

---

## 6 · Autorías → resuelto por defecto

**La edición técnica es un documento interno.** No lleva firma personal: va como producto de la
Dirección General de Desarrollo Gastronómico, para uso interno y para quien tenga que auditar el
método.

**El Atlas lo firma la Dirección.** Si más adelante alguien quiere autorías nominales, se agregan
sin tocar nada del contenido.

## 7 · Dónde se publica la capa → **anexo del documento, y BA Data si se autoriza**

No hay una decisión institucional tomada sobre esto, así que se adopta la que no bloquea nada:

- **La capa sale como anexo del Atlas**, bajo control de la Dirección. Eso no requiere permiso de
  nadie más y cumple el objetivo de que el trabajo sea utilizable por terceros.
- **BA Data queda como destino natural** si alguien lo autoriza. El formato ya va a ser el
  correcto —GeoJSON y CSV con licencia declarada por campo—, así que publicarlo ahí después es
  trámite, no trabajo.

Si esta decisión resulta equivocada, el costo de corregirla es cero: es el mismo archivo en otro
lugar.

---

## Lo único que sigue abierto

**El nombre del enclave boliviano de Liniers** (P021). Circulan cinco: «microcentro boliviano»,
«la Pequeña Bolivia», «el altiplano de Liniers», «el Bolishopping», «la feria boliviana». Es el
único caso del mapa donde el problema es que **sobran** nombres, y tiene peso simbólico.

Mientras no se decida, va con ° como los otros 74 — que es exactamente para lo que sirve el
símbolo.
