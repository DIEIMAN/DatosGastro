# Ronda 22 — corrección posterior a auditoría independiente

**Estado:** CORRECCION. Producto técnico sucesor de R22; no implica promoción institucional.

## Resultado preservado

- **225** establecimientos/referentes candidatos.
- **39/39** geometrías válidas; no se modificó ninguna geometría.
- **10.819** locales únicos, **11.119** ocurrencias y **300** duplicaciones; sin pertenencias triples.
- **90** Bares Notables canónicos: **87 no registrados como cerrados** al corte (**86** identificados como operativos y **1** sin verificación operativa); **3** cerrados.
- **167** referentes únicos y **190** relaciones referente–polo.

## Correcciones aplicadas

1. Los Laureles pasa de `REABIERTO` a `CERRADO`. La fecha 31/07/2026 es de verificación documental, no de último día operativo.
2. Se publica la cobertura de verificación de las 225 filas: 59 humana, 25 documental, 44 automática de plataforma y 97 sin verificación.
3. Las verificaciones automáticas no se presentan como prueba suficiente de actividad. De las 44, 34 ya permanecen `SIN_VERIFICAR`; el resto conserva el estado heredado con su tipo visible y requiere revisión sustantiva si se publica individualmente.
4. Se cierra el vocabulario visual en ocho categorías y se renombra la categoría normativa `Pizzería Emblemática`.
5. Se agrega una propuesta no institucional de hasta tres íconos principales por polo, con regla reproducible.
6. Las 190 relaciones reciben clasificación espacial con umbrales predeclarados de 50 y 250 metros.
7. Boulevard Caseros queda en Comuna 4 y posición 12 por mayoría de superficie, decisión editorial explícita.
8. `legacy_id` y `polo_uid` se incluyen juntos en las salidas cuyo grano es polo o relación polo–referente.

## Alcance

No se reabre admisión, unión territorial, cantidad de features, Warnes, Chacagiales, Villa Ortúzar, Baek-ku ni Z54. No hubo APIs, descargas, cambios de pipeline, commit, staging ni push.
