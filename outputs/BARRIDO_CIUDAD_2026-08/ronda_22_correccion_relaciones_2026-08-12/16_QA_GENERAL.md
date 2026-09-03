# QA general — corrección posterior a auditoría

## Cobertura de verificación de vigencia

Universo: **225 establecimientos/referentes**, corte estructural 12/08/2026.

| tipo de verificación | filas | proporción |
|---|---:|---:|
| HUMANA | 59 | 26,2 % |
| DOCUMENTAL | 25 | 11,1 % |
| AUTOMATICA_PLATAFORMA_OFFLINE | 44 | 19,6 % |
| SIN_VERIFICACION | 97 | 43,1 % |

Sólo **59 de 225** tienen verificación humana. Las 44 señales automáticas se conservan como tipo de evidencia y no se presentan como prueba suficiente de actividad. **97 filas (43,1 %)** no tienen verificación de vigencia.

## Controles

| control | estado | detalle |
|---|---|---|
| geometrías válidas | PASS | 39/39; copias byte a byte de R22 |
| conteos reconciliados | PASS | 10.819 / 11.119 / 300 |
| Bares Notables canónicos | PASS | 90 |
| Bares Notables no registrados como cerrados | PASS | 87 = 86 identificados como operativos + 1 sin verificar; 3 cerrados |
| Los Laureles | PASS | CERRADO; verificación documental 31/07/2026; fecha no equiparada a último día operativo |
| relaciones referente–polo | PASS | 190 = 190 clasificadas |
| categorías visuales | PASS | 8 grupos; 0 sin símbolo |
| `cerca_borde_50m` por fila | PASS | ya presente en R22; preservada |
| ambos IDs en salidas de polo/relación | PASS | `polo_uid` + `legacy_id` |
| Bar Iberia / H064 | PASS | procedencia estructurada preservada en 02 y 11 |
| requests de API | PASS | 0 |

## Privacidad y alcance

Se exportan nombres y domicilios públicos de establecimientos porque son el objeto de la capa. No se exportan contactos, CUIT/DNI, correos, nombres de personas, claves ni enlaces privados. QA propio de la corrección: no constituye promoción institucional.
