# Plan de corridas territoriales — Expansión V4

**Fecha:** 2026-07-12  
**Ejecución:** futura (Codex) — este documento es preflight

## Secuencia

1. **Preparar universo** de la tanda (F01/F02 + Places reutilizados + brechas autorizadas).
2. **Asignar puntos** a áreas de consulta por geometría (no por campo barrio del CSV).
3. **Aplicar método principal** según tipología (ver matriz).
4. **Métodos de control** obligatorios (KDE, ablación por fuente, continuidad).
5. **Contraste post hoc** con evidencia documental Grok (solo ABIERTA_Y_LEIDA para límites narrativos).
6. **Clasificar resultado** en taxonomía permitida (incluye EVIDENCIA_INSUFICIENTE).
7. **No adoptar** sin decisión humana.

## Métodos por tipología

| Tipología | Método principal | Controles |
|---|---|---|
| CORREDOR_LINEAL | densidad longitudinal + tramos | vacíos >300 m cortan; buffers variables |
| NUCLEO_COMPACTO / MICROCENTRALIDAD | HDBSCAN radio pequeño | mínimo puntos; estabilidad bootstrap |
| MULTIPARTE | clustering + componentes | no fusionar a priori |
| UNIDAD_BARRIAL | HDBSCAN + grafo | ratio núcleo/fondo; multiparte |
| RED_DE_NODOS | comunidades de grafo | no forzar corredor |

## Hipótesis nula de fragmentación

Caballito (Z03), Villa Urquiza (Z10), Paternal (Z14), Centro (Z05):  
**partir de múltiples piezas o ninguna**, no de un solo polígono.

## Cero clusters es válido

Boedo, Lacroze completa, Villa Pueyrredón: salida esperable `EVIDENCIA_INSUFICIENTE` / `OFERTA_DISPERSA`.
