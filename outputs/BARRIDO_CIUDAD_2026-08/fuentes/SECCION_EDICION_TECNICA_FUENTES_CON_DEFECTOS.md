# Fuentes con defectos conocidos

*Sección para la edición técnica · redactada el 7 de agosto de 2026 · datos en
`outputs/BARRIDO_CIUDAD_2026-08/fuentes/fuentes_defectos_conocidos.csv` y
`fuentes_marcas_aplicadas.csv`*

Un dato mal cargado se corrige en su fila. Lo que esta sección registra es distinto: fuentes donde
el defecto **es una propiedad del artefacto** y afecta a todo lo que salga de él, hoy y en cada
consulta futura. Sin un registro explícito, cada corrección se paga de nuevo cada vez que alguien
vuelve a citar la misma fuente.

Van cuatro. Cada una tiene tres campos que hacen falta juntos: **cómo se detecta** —una regla que un
script puede evaluar, no una impresión—, **qué prohíbe afirmar** y **qué sigue valiendo**. Una regla
sin consecuencia declarada se convierte en una etiqueta decorativa; una consecuencia sin regla no se
puede aplicar sola.

---

## FD-01 · El Cronista con fecha de actualización 24/09/2025

**Se detecta:** dominio `cronista.com` **y** `fecha_actualizacion = 2025-09-24`.

**Qué pasó.** Al menos tres notas con años de origen distintos llevan exactamente la misma fecha de
actualización: la del Mercado de los Carruajes, «5 lugares para comer bien y barato en el barrio
chino» (original de agosto de 2021) y la de Ultramarinos (original de septiembre de 2024). Tres
notas, tres años de origen, una sola fecha. Eso no es una nota desactualizada: es un **re-sellado
masivo del archivo**.

**La prueba está en la de los Carruajes:** actualizada el 24/09/2025, seguía recomendando dos
restaurantes adentro de un mercado que había cerrado cinco meses antes. La fecha de actualización no
acompañó ninguna revisión del contenido.

**Prohíbe:** leer esa fecha de actualización como fecha de verificación del dato.
**Sigue valiendo:** el contenido, con la añada de su fecha de **origen**.

**Dos precisiones que evitan aplicarla de más.** La marca es **dominio más fecha**, no fecha sola:
una nota de otro medio publicada el mismo día no está afectada. Y no alcanza el medio: la nota de El
Cronista sobre Los Laureles del 05/08/2026 se publicó 12:33 y se actualizó 12:34 — un minuto es una
corrección de redacción, no un re-sellado, y esa nota cuenta.

**Y una asimetría que hay que respetar.** Seis hitos de la capa salen de cronista.com y no tienen
fecha de actualización registrada por nosotros. **No encontrar la fecha no es haberla verificado
distinta**: quedan `pendiente_de_comprobacion`, que es un tercer estado y no un descarte encubierto.

---

## FD-02 · El catálogo consolidado de Bares Notables, en su campo territorial

**Se detecta:** cualquier uso del campo `barrio` o `comuna` del catálogo.

**Qué pasó.** El catálogo ubica La Academia en la Comuna 5. El normalizador del GCBA la pone en
Balvanera, Comuna 3. El error es verificable contra una fuente oficial del mismo Estado que publica
el catálogo.

**Prohíbe:** usar el barrio o la comuna del catálogo como dato territorial sin cotejarlo con USIG.
**Sigue valiendo:** la declaratoria, el nombre y la dirección postal.

Esto importa porque la matriz asigna hitos a filas por **punto**, y el punto sale de la dirección,
no del barrio declarado. Una fila que se arme por nombre de barrio hereda el error entero.

---

## FD-03 · El PDF del catálogo servido bajo la URL de la Res. MCGC 3758/24

**Se detecta:** cualquier cita del catálogo que no venga con SHA-256 y fecha de descarga.

**Qué pasó.** Bajo la misma URL y el mismo número de resolución circulan contenidos distintos: el
que está en disco desde el 03/08/2026 trae **90 entradas** y una hoja de firmas del **26/02/2026**
(GEDO IF-2026-10314379-GCABA-DGPMYCH); la URL sirve hoy uno de **88**. A eso se suman las listas
independientes del GCBA (84) y de Wikidata (95).

**Prohíbe:** citar «el catálogo» sin decir cuál de los contenidos.
**Sigue valiendo:** cada contenido, citado por su hash y su identificador interno.

La consecuencia excede la cita. Si un documento firmado en febrero ya lista las doce altas, «alta del
3 de agosto» no describe el acto declaratorio. La resolución de las altas sigue sin localizarse, y
por eso las doce viajan con `declaratoria_localizada = "no · sólo prensa"`.

---

## FD-04 · Time Out Buenos Aires, en su campo de barrio

**Se detecta:** el barrio que declara una nota de Time Out.

**Qué pasó.** Tres direcciones mal asignadas, verificadas contra USIG en el control de bordes: Corte
Comedor —Time Out dice Núñez, USIG dice Belgrano—, Vereda Adentro y el tercer caso del mismo control.

**Prohíbe:** usar el barrio que declara Time Out como dato territorial.
**Sigue valiendo:** la distinción editorial y la dirección de puerta.

---

## Cómo se usa esta sección

1. Antes de incorporar un dato, buscar su fuente acá. Si tiene marca, aplicar lo que la marca
   prohíbe **y** conservar lo que sigue valiendo: la marca no borra la fuente.
2. Cuando una marca se aplique a un registro concreto, dejarlo en `fuentes_marcas_aplicadas.csv` con
   el campo afectado y la consecuencia. Sin ese rastro, la marca vuelve a discutirse cada ronda.
3. Cuando una detección resulte falso positivo, **registrarla igual, marcada como tal**. La lista de
   lo que se decidió no marcar vale tanto como la de lo marcado: es lo que impide que la próxima
   ronda la vuelva a levantar.
4. Un defecto nuevo entra con los tres campos completos —regla, prohibición, evidencia—. Si no se
   puede escribir la regla, todavía no es un defecto de fuente: es un dato mal cargado.

**Y el criterio general, que es el que ordena todo lo anterior:** una fecha de actualización, un
campo de barrio o un número de resolución son **metadatos del artefacto**, no observaciones del
territorio. Ninguno de los cuatro defectos es un error sobre un restaurante: los cuatro son errores
sobre cómo el documento se describe a sí mismo. Que sean todos del mismo tipo es el hallazgo, no la
coincidencia.
