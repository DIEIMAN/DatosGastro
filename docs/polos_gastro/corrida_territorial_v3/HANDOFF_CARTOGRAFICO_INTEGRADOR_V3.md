# Handoff cartográfico al integrador V3

## Propósito y decisiones

Entregar capas, métricas y mapas regenerables para integración técnico-editorial. Modelos
recomendados: BEL-A, REC-A y CN-DEC10. Respaldos: BEL-C y REC-B.

## KPI lock cartográfico

Usar `KPI_LOCK_CARTOGRAFICO_V3.csv` sin recalcular ni redondear de otro modo. No alterar
geometrías analíticas; cualquier ajuste de presentación debe derivarse por script y mantener una
capa separada.

## Nombres autorizados

Polo Gastronómico Belgrano; Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría; Cabildo–Juramento;
Bajo Belgrano; Belgrano R · Polo Gastronómico Recoleta; centralidad patrimonial-comercial;
corredor patrimonial-hotelero · Polo Gastronómico Costanera Norte; corredor de concesiones
ribereñas; franja de puestos y carritos de parrilla; patio gastronómico de puestos en containers;
predios de eventos y usos mixtos Costa Salguero–Punta Carrasco.

## Pies de mapa sugeridos

- “Geometría experimental derivada de oferta registrada/visible. No constituye límite administrativo oficial.”
- “Los vacíos se preservan y los nombres se aplican post hoc; los buffers son convenciones cartográficas.”
- Costanera: “Unidad multiparte adoptada por el estudio, con cuatro componentes discontinuos.”

## Archivos

- Analítica: `*_ANALITICA_V3.geojson`.
- Presentación: `*_PRESENTACION_V3.geojson`.
- Puntos: `PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson` y `ASIGNACION_PUNTOS_TERRITORIAL_V3.csv`.
- Métricas: `METRICAS_MODELOS_TERRITORIALES_V3.csv`, matriz de decisión y KPI lock.
- Mapas: `mapas/`, PNG y SVG.
- Hashes: `CHECKSUMS_SHA256.txt` y manifest del paquete.

## Contrato editorial concurrente

Estado: **INCORPORADO**. Ruta prevista: `docs/polos_gastro/preintegracion_editorial_v3/CONTRATO_OUTPUTS_CARTOGRAFICOS_PARA_INTEGRACION_V3.md`. SHA-256:
`9da6ca5e87112cdfc18a4d4cb93cdf8241abc6c17f20eb924a91df0abadd3630`. Al no existir contrato específico, dimensiones y nombres siguen el
contrato mínimo de esta corrida; podrían requerir adaptación editorial posterior sin alterar la
capa analítica.

## Limitaciones y pendientes

La dependencia de señal externa almacenada se declara como límite de fuente, no como criterio de
exclusión. Belgrano R queda como sector secundario; su promoción es la única firma humana potencial.
