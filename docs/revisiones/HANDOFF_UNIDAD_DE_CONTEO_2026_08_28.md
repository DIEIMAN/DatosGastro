# Handoff — la unidad de conteo (F1 de panaderías), 2026-08-28

Continúa `HANDOFF_LECTOR_FUENTES_LOCALES_2026_08_27.md`. Aquel arregló **cómo se leen** los
archivos de F02; éste arregla **qué se cuenta como un establecimiento**.

## Qué se hizo

El padrón agrupaba por partida matriz, que identifica la parcela y no el local: el 51 % de
los inmuebles del universo aloja más de una habilitación. Ahora agrupa por habilitación
—`solicitud` más unidad funcional en los siete archivos viejos, `disposicion` en el de
2025— con partida + nombre de respaldo.

| | antes | después |
|---|---|---|
| Panaderías, universo A | 1.176 | **1.219** |
| Panaderías, A + B | 1.647 | 1.732 |
| Registros con nombre | 119 | 117 |
| Marcados para revisión manual | 533 | 559 |

## Lo que apareció al hacerlo, y que la medición previa no veía

**No dio 1.280.** El diagnóstico anticipaba 1.214 legacy + 66 modernos, tratándolos como
universos disjuntos. No lo son: **el padrón 2025 republica trámites viejos**. Como el
archivo legacy se identifica por `solicitud` y el moderno por `disposicion`, el mismo local
entraba dos veces con dos claves de espacios distintos. Son **59 casos del universo A**,
que se unen cuando coinciden partida, domicilio y año y hay exactamente un grupo de cada
lado. Quedan 2 ambiguos sin unir, a propósito.

Del mismo tipo, del lado legacy: **379 solicitudes aparecen en dos archivos** por el solape
de años, siempre con el mismo domicilio. Agrupar por solicitud las une, que es lo correcto,
y ése es el dato que autoriza a usar la solicitud sola como clave global.

**El nombre se perdía al fusionar.** Si el representante del grupo es una fila vieja —que
por privacidad no trae nombre— y el trámite gemelo del padrón 2025 sí lo tiene, el nombre
desaparecía: la cobertura caía de 119 a 38 y `Día Argentina S.A.` pasaba de 17 bocas a 2.
Ahora los campos vacíos del representante se completan con los del resto del grupo.

**El grupo de 362 filas no es una fusión indebida.** Son 900 filas crudas de una sola
disposición: el padrón 2025 publica cada trámite multiplicado por rubro × domicilio ×
comentario. El criterio de cierre del plan —"el grupo más grande baja de 360"— estaba mal
formulado: lo que importa es que ningún grupo mezcle locales distintos, y no lo hace. De
1.732 grupos, 40 contienen más de un domicilio y los 14 que cruzan dos calles son ochavas
(Cabildo 1690 / José Hernández 2412; Entre Ríos 1098 / Humberto 1º 1799).

## El precio, medido

Un local habilitado dos veces —renovación, cambio de titular— son dos habilitaciones y
entra dos veces. Cota superior: **83 establecimientos, el 6,8 % del universo A** (81
domicilios con dos registros del mismo patrón de rubro, 80 de ellos con una sola partida).
La cifra vive entre **1.136 y 1.219**.

No se resuelve con una regla: dos panaderías pegadas son igual de compatibles con la
evidencia que una sola habilitada dos veces. La lista corta está en
`outputs/panaderias/analisis/d9_renovaciones_candidatas.csv` y es trabajo de F4.

## Archivos tocados

Módulo compartido (sirve a todos los rubros):
- `scripts/shared/fuentes_locales/f02.py` — expone `solicitud`, `unidad_funcional`,
  `partida_horizontal` y la propiedad `clave_habilitacion`; normaliza los códigos de UF
  (`0001`, `1;1`, `0002;0001` → `1`, `1`, `1;2`) y descarta el texto de rubro que el
  corrimiento de 2021 mete en esa columna.
- `tests/test_fuentes_locales.py` — 6 pruebas nuevas (clase `UnidadDeConteoTest`).

Panaderías:
- `scripts/panaderias/build_panaderias.py` — nueva `establecimiento_key`,
  `fusionar_entre_esquemas()`, y el completado de campos del representante.
- `scripts/panaderias/diagnostico_panaderias.py` — D9 nuevo, `--maestro RUTA`, y D4
  describiendo la clave real.
- `outputs/panaderias/` regenerado, con `analisis/d9_renovaciones_candidatas.csv`.

Documentación: `docs/panaderias/{README_PANADERIAS,NOTAS_METODOLOGICAS,PLAN_DE_TRABAJO}.md`,
`docs/estudios_de_rubro/{LECTOR_FUENTES_LOCALES,ACCIONES_PARA_DIEGO,COMPARACION_PANADERIAS_CASAS_DE_PASTAS}.md`,
`outputs/panaderias/analisis/HALLAZGOS_DIAGNOSTICO.md`, `CLAUDE.md`.

**No tocado a propósito:** `outputs/casas_pastas/` y la clave de `build_casas_pastas.py`.
El build de pastas se corrió a una carpeta aparte y reproduce 159 exacto, o sea que el
cambio del lector no lo movió; adoptar la clave nueva ahí sí va a mover el número, y es
decisión de Diego junto con la de regenerar el entregable.

## Estado de verificación

- `python -m unittest discover tests` → 91 tests OK (eran 85).
- `python -m scripts.shared.fuentes_locales.f02` → los ocho archivos con filas y rubro.
- Los dos builds corren de punta a punta; pastas reproduce su cifra vigente.

## Lo que sigue

1. **F2** — separar el pan que es negocio del pan que es góndola. Ya no depende de nada:
   el maestro trae `clave_habilitacion`. Necesita que Diego revise una vez la lista de
   giros ajenos (`p2_contaminacion_multirubro.csv`).
2. **F3** — decidir qué cifra se publica. Bloquea cualquier informe.
3. El resto sigue igual en `docs/estudios_de_rubro/ACCIONES_PARA_DIEGO.md`; lo urgente de
   ahí no cambió: no hay ninguna habilitación posterior a 2024 en el proyecto.
