# Pendientes y limitaciones

## Pendientes operativos

- Completar URLs directas oficiales para F01, F02 y F03 en `src/config.py`.
- Descargar fuentes reales en `data/raw/`.
- Mantener seeds/manuales solo en `data/seeds/`.
- Revisar `docs/perfilado_fuentes.md` despues de cada descarga.
- Revisar `docs/AUDITORIA_DATOS_REALES.md` antes de construir un dashboard.
- Ajustar mapeos de columnas si BA Data cambia nombres o formatos.
- Geocodificar direcciones con USIG en una etapa futura con internet.
- Validar vigencia de establecimientos seed contra habilitaciones AGC.

## Limitaciones de la V2

- Los archivos `raw_*` actuales son seed/manuales, no padrones completos.
- Los seeds son fallback de desarrollo y no son aptos para dashboard real.
- F02 no tiene registros seed cargados.
- Eventos con sedes multiples o no determinadas usan `U00000`.
- No se publicaron o no se estructuraron metricas de impacto para varios programas.
- Analytics deben interpretarse como prueba de pipeline mientras el estado sea `datos seed`.

## No hacer sin evidencia

- No inventar URLs de descarga.
- No inventar registros de establecimientos, ferias, eventos o programas.
- No inferir barrio definitivo si el texto es ambiguo.
- No reemplazar seeds por datos reales sin conservar trazabilidad de fuente.
- No publicar graficos si `apto_dashboard` no es `si`.
