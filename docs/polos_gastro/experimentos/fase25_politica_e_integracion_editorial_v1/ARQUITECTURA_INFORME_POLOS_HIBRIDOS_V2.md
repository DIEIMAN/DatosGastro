# Arquitectura del informe de polos híbridos - V2

Estado: **PROPUESTA EDITORIAL EXPERIMENTAL / NO OFICIAL**.  
Fecha: 2026-07-11.

Esta versión continúa la arquitectura previa y aplica DEC-10 a DEC-20. No autoriza la integración del handoff v2.1 ni reemplaza la Fase 25 oficial.

## Principio editorial

El informe presenta dos dimensiones independientes: tipo territorial y madurez de evidencia. El tipo explica la forma; la madurez explica cuánto respaldo tiene hoy la lectura. Las capas híbridas profundizan la lectura general y no se presentan como una corrección de la Fase 25.

## Variante A - política, 12 a 14 páginas

| Página | Contenido |
| --- | --- |
| 1 | Portada institucional. |
| 2 | Síntesis ejecutiva sin tecnicismos. |
| 3 | Mapa general con leyendas separadas de tipo y madurez. |
| 4 | Cómo leer: núcleo, corredor, red, frente, identidad en tramos y señal exploratoria. |
| 5 | San Telmo: núcleo compacto y eje contextual. |
| 6 | Corrientes: corredor continuo; Abasto como área asociada. |
| 7 | Puerto Madero: frente doble, condicionado a asset v2.1. |
| 8 | Belgrano: red en estudio, sin cantidad ni nombres no firmados. |
| 9 | Palermo: lectura editorial o escalado aprobado. |
| 10 | Zonas en observación. |
| 11 | Costanera Norte: unidad multiparte exploratoria. |
| 12 | Próximos pasos. |
| 13 | Nota metodológica y alcance. |
| 14 | Reserva editorial, solo si una zona adicional alcanza madurez suficiente. |

Reglas: sin métricas técnicas en láminas; sin nombres comerciales; sin algoritmos; sin fuentes privadas nombradas; sin polígonos experimentales no firmados.

## Variante B - interna, 20 a 25 páginas

Comparte las páginas 1 a 13 y agrega:

- ficha técnica por zona con universo, cobertura, estabilidad, mezcla de fuentes y advertencias;
- tabla de no asignados en categorías agregadas;
- decisiones aplicadas y pendientes;
- convenciones cartográficas;
- trazabilidad de capas, hashes y fechas;
- comparativas de representación cuando estén validadas;
- anexo de límites metodológicos y reproducibilidad.

Las cifras internas no pasan a la variante política por defecto. Cada una debe estar en el KPI lock con fuente, campo, fecha y advertencia.

## Dependencias de cierre

1. Handoff v2.1 recibido e inventariado, sin integrarlo automáticamente.
2. Capas de presentación aprobadas para Puerto Madero, Corrientes, San Telmo y Costanera.
3. Shortlist de Belgrano revisada y decisión humana registrada.
4. Metadatos y hashes disponibles.
5. KPI lock actualizado y validado contra archivos de origen.
6. QA visual, metodológico y de privacidad de ambas variantes.

