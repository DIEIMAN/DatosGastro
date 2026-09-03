# Subproyecto Panaderías — CABA

Abierto el 2026-08-27. Sigue la misma línea de trabajo que Casas de Pastas: partir de las
fuentes públicas locales del proyecto, armar un padrón candidato con trazabilidad fila a
fila, y recién después evaluar fuentes externas para completar lo que las públicas no ven.

## Estado

Fase 1 corrida: padrón base sobre F01 + F02, con clasificación A/B/C, deduplicación,
geocodificación desde caché local, tablas territoriales y figuras. Sin API paga, sin
scraping, sin Drive.

| | |
|---|---|
| Universo A (núcleo) | **1.219** establecimientos |
| Universo B (punto de cocción) | **513** |
| Total A+B | **1.732** |
| Geolocalizados (A) | 1.203 de 1.219 (98,7 %) |
| Requieren revisión manual | 559 |

Cifras del 2026-08-28, contando por habilitación (fase F1 cerrada). El 27 decían
1.176 / 471 / 1.647, agrupando por partida matriz, que es el inmueble; y antes de arreglar
el lector de F02, 569 / 77 / 646, con siete de los ocho archivos leídos mal (ver
`docs/estudios_de_rubro/IMPACTO_LECTOR_2026_08_27.md`).

Recordatorio permanente: **F02 son habilitaciones**, registros administrativos. No son
locales activos ni aperturas netas.

## Documentos

- `ALCANCE_Y_DEFINICION.md` — qué es y qué no es una panadería en este subproyecto.
  Decisión de Diego del 2026-08-27.
- `NOTAS_METODOLOGICAS.md` — cómo se construyó el padrón, qué se encontró y qué límites
  tiene. **Leer antes de citar cualquier número.**
- `PLAN_DE_TRABAJO.md` — las fases pendientes en orden de dependencia y lo que depende de
  Diego. **Es el archivo que se actualiza cuando algo avanza.**
- `outputs/panaderias/analisis/HALLAZGOS_DIAGNOSTICO.md` — los seis hallazgos medidos sobre
  el padrón vigente, con los CSV que los respaldan.
- `docs/estudios_de_rubro/COMPARACION_PANADERIAS_CASAS_DE_PASTAS.md` — los dos rubros lado
  a lado, y qué de panaderías le sirve a pastas.

## Código y salidas

- `scripts/panaderias/panaderias_patterns.py` — clasificador A/B/C. Trae su propio banco
  de pruebas: `.venv/Scripts/python.exe scripts/panaderias/panaderias_patterns.py`
  (13/13 al 2026-08-27).
- `scripts/panaderias/build_panaderias.py` — build del padrón.
  `.venv/Scripts/python.exe scripts/panaderias/build_panaderias.py`
- `scripts/panaderias/diagnostico_panaderias.py` — nueve controles sobre el maestro ya
  construido (sesgo de geo, elaboración vs despacho, agrupamiento, firmas, barrios vacíos,
  solape con pastas, QA de la geocodificación, renovaciones candidatas). Acepta
  `--pastas RUTA` para el solape y `--maestro RUTA` para diagnosticar una corrida de
  prueba sin pisar las salidas publicadas.
- `scripts/panaderias/diagnostico_unidad_de_conteo.py` — relee F02 para medir el
  sub-conteo por partida matriz y la contaminación por multi-rubro.
- `outputs/panaderias/` — padrón maestro, candidatos por fuente y nivel, tablas por
  comuna y barrio, densidades, habilitaciones por año, excluidos por motivo, figuras.
- `outputs/panaderias/analisis/` — salidas de los dos diagnósticos y el documento de
  hallazgos.

## Qué sigue

El detalle, con criterios de cierre y dependencias, está en `PLAN_DE_TRABAJO.md`. En corto:

1. **F2 — pan que es negocio vs pan en góndola.** El 23,4 % de las habilitaciones del
   universo declaran además otro giro, sobre todo supermercado. Es lo que sigue.
2. **F3 — decidir la cifra.** Del mismo padrón salen 1.219 y, descontando el pan que está
   dentro de otro giro, una cifra menor que F2 va a fijar. Se elige, no se promedia. Es
   firma de Diego y bloquea todo lo que se publique.
3. **F4 — revisión humana** de los casos de frontera, después de F2. Incluye los 81
   domicilios de `d9_renovaciones_candidatas.csv`, que son el precio de contar por
   habilitación.
4. **F5 — fuentes externas** para nombre, vigencia y actualidad, que ninguna corrección
   interna puede dar. OSM y Overture primero; Places sólo si hace falta y con autorización.
5. **F6 — per cápita**, que necesita el censo 2022 y no depende de nada de lo anterior.

Cerrado: el lector de F02, el alcance, el clasificador, la geocodificación (98,7 %, con
control propio y 0 puntos fuera de CABA) y **F1, la unidad de conteo**.
