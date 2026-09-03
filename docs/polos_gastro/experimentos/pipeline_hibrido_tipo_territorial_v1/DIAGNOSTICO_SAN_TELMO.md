# Diagnóstico San Telmo

**Resultado:** prototipo útil con ajustes. El universo tiene 320 puntos y 46.6 % Places. Emergen 1 núcleos candidatos al exigir presencia estable en perturbaciones locales y coincidencia con KDE.

HDBSCAN eom/leaf y KDE se informan por separado en `san_telmo_comparacion_metodos.csv`. La estabilidad media por bloques fue 0.57. La evidencia permite núcleo compacto; no resuelve automáticamente si Mercado, Defensa y casco histórico deben ser una o dos unidades. `DEFENSA` se usa sólo como calle local de referencia.

**Recomendación:** conservar núcleo(s) estable(s) y someter a decisión humana la combinación núcleo + eje Defensa. No usar KMeans.
