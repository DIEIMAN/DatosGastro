# Pendientes y limitaciones

## Pendientes operativos

- Refrescar periodicamente las URLs directas oficiales para F01, F02 y F03 en `src/config.py`.
- Descargar nuevamente fuentes reales en `data/raw/` cuando BA Data publique actualizaciones.
- Mantener seeds/manuales solo en `data/seeds/`.
- Revisar `docs/perfilado_fuentes.md` despues de cada descarga.
- Revisar `docs/AUDITORIA_DATOS_REALES.md` antes de construir un dashboard.
- Ajustar mapeos de columnas si BA Data cambia nombres o formatos.
- Geocodificar direcciones con USIG en una etapa futura con internet.
- Validar vigencia de F01 contra fuentes oficiales complementarias si se necesita hablar de establecimientos activos.
- Mantener curado F04 con fuente por fila; si aparece dataset oficial estructurado de eventos, integrarlo como nueva fuente.
- Mantener curado F05 con fuente por fila; si aparece dataset oficial estructurado de programas/politicas, integrarlo como nueva fuente.

## Limitaciones actuales

- Los seeds son fallback de desarrollo y no son aptos para dashboard real.
- F01 es oferta/establecimientos registrados, pero no confirma vigencia actual por registro.
- F02 son habilitaciones aprobadas AGC; no representan establecimientos activos unicos.
- La clasificacion gastronomica de F02 es inferida desde descripcion de rubro y requiere cautela en casos ambiguos.
- F03 incluye recursos con cobertura desigual; `f03_mercados.csv` quedo marcado como sospechoso por tamano menor a 1 KB.
- Eventos con sedes multiples o no determinadas usan `U00000`.
- F04 no representa el universo completo de eventos gastronomicos de CABA.
- F05 no es serie temporal de impacto; no se publicaron o no se estructuraron metricas de impacto para varios programas.
- Montos historicos de F05 no deben usarse como vigentes sin validar normativa/tarifaria actual.
- Analytics deben interpretarse segun `estado_datos`, `apto_dashboard`, metodologia y limitaciones.

## No hacer sin evidencia

- No inventar URLs de descarga.
- No inventar registros de establecimientos, ferias, eventos o programas.
- No inferir barrio definitivo si el texto es ambiguo.
- No reemplazar seeds por datos reales sin conservar trazabilidad de fuente.
- No publicar graficos si `apto_dashboard` no es `si`.
- No sumar F01 y F02 como "establecimientos gastronomicos".
- No llamar establecimientos a las habilitaciones F02.
