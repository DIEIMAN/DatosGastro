# Plan futuro de integración del handoff Codex v2.1

Estado: **PLAN EXPERIMENTAL / NO EJECUTADO**.  
Fecha: 2026-07-11.

## Condición de inicio

La integración comienza solo con autorización explícita y después de recibir un handoff inventariado. Esta tanda no lee ni copia sus capas técnicas dentro del informe.

## Secuencia propuesta

1. **Inventario**: registrar archivos, versiones, tamaños, hashes, sistema de referencia y fecha.
2. **Validación de alcance**: comprobar que las capas corresponden a presentación y no contienen puntos individuales, nombres comerciales ni identificadores técnicos.
3. **Capas de presentación**: contrastar cada asset con `ESPECIFICACION_PLANTILLAS_MAPAS_POLITICOS.md`.
4. **Mapas**: reemplazar placeholders uno por uno, sin alterar textos ni páginas no dependientes.
5. **Métricas**: actualizar `kpis_lock_preliminar.json` solo desde campos verificados; mantener métricas técnicas fuera de la variante política.
6. **Decisiones**: registrar cualquier contradicción o reapertura en un sucesor del registro V2; no resolverla dentro del generador.
7. **Reemplazo de placeholders**: actualizar `MATRIZ_ASSETS_PENDIENTES_CODEX.csv` con estado, hash y fecha de cada sustitución.
8. **PDF**: regenerar primero una versión paralela experimental; no sobrescribir Fase 25 oficial.
9. **Validación cruzada**: comparar texto, mapa, tipo, madurez, decisión y KPI para cada zona.
10. **QA**: render visual completo, extracción textual, privacidad, integridad de ZIP y verificación Git.

## Gates por zona

- San Telmo: núcleo principal y eje Defensa secundario.
- Corrientes: corredor único, Abasto fuera de la traza.
- Puerto Madero: frente doble simplificado, sin segmentos analíticos.
- Belgrano: no integrar núcleos antes de la decisión humana sobre shortlist y nombres.
- Costanera: tres componentes principales, vacíos preservados y contexto secundario sujeto a decisión.

## Criterio de cierre

La integración se considera completa únicamente si cada placeholder tiene reemplazo trazable, cada KPI está validado, las decisiones pendientes están registradas y ambas variantes superan QA visual, metodológico y de privacidad.

