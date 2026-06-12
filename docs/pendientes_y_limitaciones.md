# Pendientes y limitaciones

## Pendientes operativos

- Refrescar periodicamente las URLs directas oficiales para F01, F02 y F03 en `src/config.py`.
- Descargar nuevamente fuentes reales en `data/raw/` cuando BA Data publique actualizaciones.
- Mantener seeds/manuales solo en `data/seeds/`.
- Revisar `docs/perfilado_fuentes.md` despues de cada descarga.
- Revisar `docs/AUDITORIA_DATOS_REALES.md` antes de construir un dashboard.
- Ajustar mapeos de columnas si BA Data cambia nombres o formatos.
- Geocodificar direcciones F02 con `src/geocode_usig.py` por tandas y cache persistente en `data/processed/geo_cache.csv`; no promover puntos si la tasa exacta queda por debajo de 90%.
- Incorporar permisos de area gastronomica F06 solo como nueva fuente separada en una etapa posterior.
- Validar vigencia de F01 contra fuentes oficiales complementarias si se necesita hablar de establecimientos activos.
- Mantener curado F04 con fuente por fila; si aparece dataset oficial estructurado de eventos, integrarlo como nueva fuente.
- Mantener curado F05 con fuente por fila; si aparece dataset oficial estructurado de programas/politicas, integrarlo como nueva fuente.

## Limitaciones actuales

- Los seeds son fallback de desarrollo y no son aptos para dashboard real.
- F01 es oferta/establecimientos registrados, pero no confirma vigencia actual por registro.
- F02 son habilitaciones aprobadas AGC; no representan establecimientos activos unicos.
- La clasificacion gastronomica de F02 es inferida desde descripcion de rubro y requiere cautela en casos ambiguos. La venta minorista de productos alimenticios sin evidencia de servicio gastronomico se clasifica aparte como `Comercio alimenticio minorista` y no se cuenta como habilitacion gastronomica de servicio.
- F02 2025 tiene esquema distinto y contiene disposiciones de varios anios; queda con `requiere_validacion = si` y no debe usarse como flujo anual comparable. El periodo 2015-2018 tambien es agregado.
- F03 contiene recursos con distintos niveles de grano. Los puestos individuales no deben interpretarse como ferias o mercados. Los indicadores principales usan espacios reales; los registros de puestos, si se conservan, quedan solo como insumo tecnico y no se exponen en dashboard.
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
- No implementar scores de oportunidad, metricas de impacto ni geocodificacion masiva F02 sin cache, rate limit y validacion de calidad.
