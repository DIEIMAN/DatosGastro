# Plan de escalado del pipeline híbrido

## Recomendación

**ESCALAR_CON_AJUSTES.**

Funcionaron para su propósito: corredor vial en Corrientes; señal sin polígono en Costanera; núcleo de consenso HDBSCAN+KDE en San Telmo. Belgrano mejora visualmente a núcleos sin nombre, pero debe repetirse por baja robustez de bloques. Puerto Madero es parcial: mejora la forma, pero el soporte vial no cubre todos los puntos y la dependencia Places sigue alta.

## Otras ocho zonas

- Palermo Soho: núcleo HDBSCAN+KDE, con sensibilidad global explícita.
- Palermo Hollywood: red multinuclear, comunidades + KDE.
- Microcentro: núcleos/peatonales y posible eje, evitando solape con Corrientes.
- Caballito: grafo/comunidades; nunca 33 tiles.
- Recoleta: KDE/heatmap y núcleos separados.
- Villa Crespo y Chacarita: grafo + KDE; gate fuerte por dependencia Places.
- Caseros/Barracas: corredor sobre `CASEROS AV.` si el tramo local queda respaldado.

No volver a usar KMeans, Voronoi ni cantidad objetivo de unidades. Callejero es necesario para corredores/frentes. Se automatizan detección, estabilidad, perfiles y QA; nombres, jerarquía, inclusión, buffer orientativo y relación con Fase 25 permanecen manuales.

Bloquean el nuevo informe: repetir Belgrano y Puerto Madero, revisión humana de los cinco casos, deduplicación etiquetada, tratamiento de solapes y selección del mapa principal.
