# Cómo abrir un estudio de rubro nuevo

Receta para el próximo rubro (pizzerías, heladerías, parrillas, lo que venga), escrita a
partir de lo que costó panaderías y casas de pastas.

## 1. Escribir el alcance antes que el código

Un archivo `docs/<rubro>/ALCANCE_Y_DEFINICION.md` que diga qué entra, qué no, y por qué.
Sin eso, la clasificación se discute contra el resultado y no contra la definición.

La regla que ya está probada: **manda el rubro habilitado, no el nombre de fantasía.**
Un local llamado "Panadería" con rubro de confitería es confitería.

Tres universos, siempre:

- **A — núcleo:** el rubro es inequívoco.
- **B — frontera:** el caso que la gente llamaría del rubro pero que la definición separa
  (en panaderías: el punto de cocción que no elabora la masa). Se cuenta aparte para poder
  publicar con y sin él.
- **C — fuera, etiquetado:** lo descartado, pero con la etiqueta del motivo, para poder
  recuperarlo si la definición cambia. C no se tira.

**Medir la zona gris antes de escribir el clasificador.** Contar cuántas filas de F02 caen
en los rubros de frontera decide cuánta discusión merece la definición. En casas de pastas
el universo B tiene 2 casos y la decisión es irrelevante; en panaderías tiene 471, un 29 %
del total, y mueve la cifra publicable un 40 %. Si la zona gris es grande, la definición se
acuerda con Diego **antes** de codificar, no contra el resultado.

**Y mirar la unidad de conteo desde el principio.** La partida matriz identifica el
inmueble, no el local: en panaderías eso resultó ser un 9,2 % de sub-conteo y grupos de 360
registros. Los siete archivos legacy traen `solicitud` y `unidad_funcional`, que sí
identifican la habilitación.

## 2. Escribir el clasificador aparte del builder

`scripts/<rubro>/<rubro>_patterns.py` con una función `classify(...)` que devuelva
`nivel`, `patron_detectado`, `confianza_categoria` y `motivo_categoria`. Todo patrón corre
sobre texto normalizado (`normalizar` del módulo compartido). Que el motivo viaje con la
fila es lo que después permite auditar sin volver a correr nada.

## 3. Leer las fuentes con el módulo compartido — nunca copiar un lector

```python
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.shared.fuentes_locales import iter_f01, iter_f02

for reg in iter_f02():
    c = classify(reg.rubro_completo, reg.nombre, reg.descripcion)
```

Ver `LECTOR_FUENTES_LOCALES.md`. Copiar el lector del estudio anterior es exactamente lo
que produjo el defecto que este módulo resuelve; si hace falta algo que el módulo no da,
se agrega **ahí** y se corren `tests/test_fuentes_locales.py`.

Antes de empezar, correr el perfil y mirar que ningún archivo esté en cero:

```
.venv/Scripts/python.exe -m scripts.shared.fuentes_locales.f02
```

## 4. Lo que hay que decir del dato, sí o sí

- F02 son **habilitaciones**, no locales activos (guardrail 5). La serie por año es de
  habilitaciones otorgadas, no de aperturas netas ni de stock.
- Las filas legacy (2015-2024) **no tienen nombre** de establecimiento: titulares y CUIT no
  se leen por guardrail 7. Se identifican por partida matriz y domicilio.
- El archivo llamado `2025` no contiene habilitaciones de 2025: sus disposiciones son de
  2015-2018 (ver acciones pendientes en `IMPACTO_LECTOR_2026_08_27.md`).
- El archivo `2023` trae 5.063 filas contra 12.000-30.000 de los años vecinos: el año está
  subrepresentado en la fuente, no en el rubro.

## 5. Deduplicar y dejar la traza

F02 está desnormalizado: un mismo local aparece muchas veces. El maestro sale de agrupar
por domicilio normalizado y rubro, guardando `registros_agrupados`, `cantidad_fuentes` y
`requiere_revision_manual`. Los dos builders existentes ya hacen esto y sirven de modelo:
`scripts/panaderias/build_panaderias.py` y `scripts/casas_pastas/build_casas_pastas.py`.

## 6. Correr sin pisar lo publicado

Los dos builders aceptan `--out DIR`. Para medir el efecto de un cambio antes de decidir
si se regenera lo oficial:

```
.venv/Scripts/python.exe scripts/<rubro>/build_<rubro>.py --out <carpeta_de_prueba>
```

y recién después, con los números comparados, se corre sobre `outputs/<rubro>/`.

## 7. Antes de dar por cerrado

- `.venv/Scripts/python.exe -m unittest discover tests`
- El perfil de F02 sin archivos en cero.
- El conteo por año que cubra todo el período disponible (si aparecen años vacíos en el
  medio, es el lector, no el rubro).
- Si sale PDF: QA visual con `scripts/qa/pdf_check.py`, mirando las páginas.
