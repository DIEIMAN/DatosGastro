# Versionado de la capa editorial (Etapa Infra-5)

**Fecha:** 2026-07-08 · **Carácter:** propuesta de diseño experimental.

## Principio: snapshots inmutables, nunca edición en el lugar

Igual que el "universo semilla" y el "universo_vYYYYMM" ya usados en el diseño del
pipeline de microzonas (`docs/polos_gastro/experimentos/diseno_pipeline_definitivo/
03_CONSTRUCCION_UNIVERSO_GASTRONOMICO.md §6`), la capa editorial se versiona por
**snapshots inmutables**: una vez publicada una versión, sus archivos no se vuelven a
tocar. Un cambio, por chico que sea, genera una versión nueva.

## Convención de nombres

```
data/editorial/macrozonas/
├── macrozonas_editorial_v1_20260710.geojson      ← snapshot inmutable
├── macrozonas_editorial_v2_20260915.geojson      ← snapshot inmutable
├── CHANGELOG.md                                   ← que cambio y por que, version a version
└── VERSION_VIGENTE.md                             ← 1 linea: "la version vigente es v2"
```

(Ruta final a decidir con Diego cuando se apruebe salir de `experimentos/`; hoy todo vive
en `outputs/polos_gastro/experimentos/infraestructura_cartografica_v1/`.)

- **`vN`**: entero secuencial, nunca se reutiliza ni se salta hacia atrás.
- **`_YYYYMMDD`**: fecha de publicación (no de inicio de edición) — mismo criterio que
  `fecha_corte_por_fuente` del universo gastronómico, para que un informe pueda citar
  "macrozonas v2 (2026-09-15)" sin ambigüedad.
- El atributo `version_capa` de cada feature (esquema Infra-2) lleva el mismo valor
  `vN_YYYYMMDD` — permite saber la versión de un polígono aunque se lo mire suelto, fuera
  del archivo.

## Qué dispara una versión nueva

No cualquier ajuste amerita subir de v1 a v2 — hay dos escalas de cambio:

1. **Ajuste de vértices dentro de una versión (no publica versión nueva):** mientras un
   polígono está en `estado_revision = "borrador"` o `"revisado"`, se puede iterar
   libremente en el kit de edición (Infra-3) sin versionar cada intento — el versionado
   protege snapshots **publicados**, no el trabajo en curso.
2. **Publicación de versión nueva (sí incrementa `vN`):** cuando uno o más polígonos
   pasan a `estado_revision = "aprobado_editorial"` y quedan disponibles para que el
   pipeline de clustering los use. Dispara versión nueva:
   - alta de una macrozona/subzona que no existía,
   - baja o fusión de una macrozona/subzona,
   - cambio de geometría de una macrozona ya aprobada (aunque sea un ajuste de borde),
   - cambio de `nivel` (p. ej. una subzona que pasa a tratarse como polo propio).
   **No** dispara versión nueva: corregir una errata en `observaciones` o `autor` (se
   parchea con nota en el changelog, sin nuevo snapshot geométrico).

## `CHANGELOG.md` — formato de entrada

```markdown
## v2 — 2026-09-15

**Aprobado por:** Diego · **Reemplaza:** v1 (2026-07-10)

### Agregadas
- MZ_CHACARITA (nivel=polo): primer contorno real, trazado sobre callejero
  (calles X, Y). Antes sin geometria (fase16 no la cubria).

### Modificadas
- MZ_PALERMO_SOHO: ajuste de borde sur (paso de Scalabrini Ortiz a Malabia tras revision
  de terreno). `reemplaza_a: MZ_PALERMO_SOHO` (v1). Motivo: 8 locales quedaban fuera del
  poligono v1 pese a estar documentados en la ficha PG001A.

### Sin cambios
- Las 10 macrozonas restantes de v1 continuan vigentes en v2 (no se re-listan sus
  geometrias; ver v1 para el detalle).

### Impacto esperado en el pipeline
- Recalcular microzonas de Chacarita (antes usaba contenedor hull-de-semilla) y de
  Palermo Soho (cambio de borde). El resto de las macrozonas no requiere re-clusterizar.
```

El changelog es lo que responde, dentro de un año, "qué cambió" sin tener que diffear
GeoJSON a mano — pero el diff automático (siguiente sección) es la fuente de verdad; el
changelog es la versión legible para humanos de ese diff.

## Diff automático entre versiones

Herramienta de apoyo (no reemplaza el changelog humano, lo verifica):
`comparar_versiones_editorial.py` — dado `vN` y `vN+1`, reporta por `id`:

- **agregadas**: `id` presente en vN+1, ausente en vN.
- **eliminadas**: `id` presente en vN, ausente en vN+1.
- **geometría modificada**: mismo `id`, `symmetric_difference` de área > 1 % del área
  original (evita marcar como "cambiada" una geometría idéntica con precisión de punto
  flotante distinta).
- **atributos modificados**: mismo `id`, misma geometría, algún campo del esquema
  distinto (típicamente `estado_revision` pasando de `revisado` a `aprobado_editorial`).

Este reporte es el que debería coincidir con lo que el `CHANGELOG.md` dice a mano — si no
coincide, alguien olvidó documentar un cambio.

## Trazabilidad hacia el pipeline de clustering

Cada corrida de microzonas (`s01`…`s05` del prototipo, o su sucesor) debe registrar en su
propio log qué `version_capa` de la capa editorial usó (ya existe el hábito de registrar
parámetros en `parametros_pipeline_v1.json`; se agrega `version_capa_editorial` al mismo
archivo). Así, un informe que cite "microzonas calculadas el 2026-09-20" es reproducible:
universo vX + editorial vY + parámetros de clustering, los tres versionados por separado
pero citados juntos.
