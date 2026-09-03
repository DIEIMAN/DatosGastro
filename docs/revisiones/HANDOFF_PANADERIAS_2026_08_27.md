# Handoff — Panaderías (2026-08-27)

## Estado

Padrón vigente: **A = 1.178, B = 472, A+B = 1.650**. Geolocalizados 1.152 de 1.178
(97,8 %). 534 marcados para revisión manual.

Cerrado: lector de F02 (ahora en `scripts/shared/fuentes_locales`), alcance, clasificador
con banco de pruebas, geocodificación USIG y su control de calidad.

Abierto y **medido**: unidad de conteo y contaminación por multi-rubro.

## Lo que se hizo en la segunda vuelta

Diagnóstico sobre el dato que ya existe, sin pedir nada externo. Dos scripts nuevos,
reproducibles, que escriben en `outputs/panaderias/analisis/`:

- `scripts/panaderias/diagnostico_panaderias.py` — ocho controles sobre el maestro.
- `scripts/panaderias/diagnostico_unidad_de_conteo.py` — relee F02 para las preguntas que
  el maestro no puede contestar.

Hallazgos en `outputs/panaderias/analisis/HALLAZGOS_DIAGNOSTICO.md`. Los dos que importan:

1. **La partida matriz es el inmueble, no el local.** Contar por `solicitud` da 1.214 en
   vez de 1.112: 9,2 % de sub-conteo. El 51 % de los inmuebles del universo alojan más de
   una habilitación, y el grupo más grande del maestro fusiona 360 registros.
2. **El 23,4 % de las habilitaciones del universo declaran otro giro** (supermercado en
   321 casos). Y pega más fuerte en el grupo que parecía limpio: 29,9 % de las que declaran
   elaboración contra 11,4 % de las que sólo despachan. Son supermercados con horno.

Del mismo padrón salen tres cifras: **1.178** (hoy), **1.280** (corregida la unidad de
conteo), **996** (además, sin el pan dentro de otro giro).

También: la geocodificación pasó el control (0 puntos fuera de CABA, 116 de 118 comunas
coinciden); ningún barrio queda en cero; elaborar o sólo despachar no tiene patrón
territorial; y 29 domicilios están a la vez en panaderías y en casas de pastas.

## Documentos nuevos

- `docs/panaderias/PLAN_DE_TRABAJO.md` — F1 a F6 en orden de dependencia, con criterios de
  cierre y lo que depende de Diego. **Es el archivo que se actualiza cuando algo avanza.**
- `docs/estudios_de_rubro/COMPARACION_PANADERIAS_CASAS_DE_PASTAS.md` — los dos rubros lado
  a lado.
- `outputs/panaderias/analisis/HALLAZGOS_DIAGNOSTICO.md`.
- Dos párrafos agregados a `COMO_ABRIR_UN_RUBRO_NUEVO.md`: medir la zona gris y mirar la
  unidad de conteo antes de escribir el clasificador.

## Cuidado al retomar

- **Diego estuvo editando en paralelo.** `scripts/shared/fuentes_locales/f02.py` cambió
  a las 15:33 y el maestro de panaderías se había generado a las 15:30. Panaderías se
  verificó estable contra el lector nuevo (1.178/472/1.650, corriendo con `--out` a una
  carpeta de prueba), pero conviene regenerar antes de publicar.
- **Las cifras de pastas de la comparación son de una corrida de prueba**, no de
  `outputs/casas_pastas/`, que sigue publicando 10. Con el lector actual da 159.
- El número de pastas se movió de 139 a 159 entre dos corridas de esta misma tarde, por
  los cambios en el lector. Cualquier cifra de pastas hay que volver a sacarla.

## Lo primero que conviene hacer

F1 del plan: exponer `solicitud` y `unidad_funcional` en `RegistroF02` y cambiar
`establecimiento_key`. Vive en el módulo compartido, así que **pastas lo hereda** — y
conviene medirlo ahí antes de regenerar su entregable, para no rehacer el informe dos veces.
