# Metodología de la corrida territorial V3

**Estado:** EXPERIMENTAL / NO OFICIAL  
**Fecha de corte:** 2026-07-11  
**Rol:** `cartografo_territorial`  
**CRS de cálculo:** `EPSG:5347` · **GeoJSON:** `EPSG:4326` / CRS84

## Principio central

La documentación no supervisó clustering, asignaciones ni geometrías. Primero se calcularon
continuidad, componentes, distancias, cobertura, densidad y estabilidad; después se aplicaron
nombres y contraste documental. Se separan capa analítica, interpretación documental, decisión
institucional y capa de presentación.

## Métodos ejecutados

- Belgrano: comunidades de grafo sobre los 17 candidatos v2, distancias entre polígonos,
  sensibilidad a umbrales 80–300 m, estabilidad bootstrap ya congelada, respaldo KDE y ablación
  por fuente del baseline; unión restringida por componente, sin hull común.
- Recoleta: continuidad de los nueve núcleos v2.1, distancias y vacíos, unión topológica con cierre
  morfológico de 35 m, alternativa de dos grupos mediante corte del mayor arco del árbol de
  expansión mínima, KDE multiancho, bootstrap por bloques y ablaciones congeladas en v2.1.
- Costanera Norte: reproducción HDBSCAN (`min_cluster_size=8`, `min_samples=5`, `eom`), concave
  hull ratio 0,55 y buffer analítico 55 m recortado al contenedor; cuatro componentes conservados,
  sin bandas ni conectores. DEC-10 se aplica después del cálculo como decisión institucional.

Los buffers y cierres son convenciones cartográficas orientativas. No representan ancho real ni
límites administrativos oficiales. La señal externa ya almacenada se analiza como fuente separada;
no se realizaron consultas externas.

## Reproducibilidad

Configuración: `scripts/polos_gastro/corrida_territorial_v3/config_territorial_v3.json`. Script:
`scripts/polos_gastro/corrida_territorial_v3/ejecutar_corrida_territorial_v3.py`. Los 27
insumos registrados tuvieron hash coincidente antes de ejecutar.
