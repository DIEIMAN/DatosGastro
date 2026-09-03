# QA automático de la capa editorial (Etapa Infra-6)

**Fecha:** 2026-07-08 · **Carácter:** propuesta de controles + implementación
experimental (`qa_capa_editorial.py`), ya probada contra datos reales de esta sesión.

## Diseño: gates duros vs. banderas (mismo criterio que el QA de clustering del prototipo V1)

| Gate/bandera | Qué revisa | Bloquea publicación |
|---|---|---|
| G1 | Geometrías inválidas (autointersecciones, anillos mal formados) vía `shapely.is_valid` | Sí |
| G2 | Campos obligatorios ausentes o vacíos (`id`, `nombre`, `nivel`, `tipo_geometria`, `estado_revision`, `nivel_confianza`, `version_capa`) | Sí |
| G3 | `id` duplicado | Sí |
| G4 | Valores fuera de vocabulario controlado (`nivel`, `tipo_geometria`, `estado_revision`, `nivel_confianza`) | Sí |
| G5 | Subzona con `polo_id` vacío o apuntando a un `id` que no existe en la capa | Sí |
| B1 | Polígonos con huecos (anillos interiores) — puede ser intencional, se marca siempre | No |
| B2 | Superposición entre macrozonas del **mismo nivel** que no son padre/hijo (umbral: intersección > 2 % del área menor) | No |
| B3 | % de cobertura de CABA por macrozonas nivel `polo`, contra `comunas_caba.geojson` — la parte no cubierta se documenta, no se oculta (mismo espíritu que la capa `entidades_fuera_de_macrozona` del prototipo V1) | No |
| B4 | Features con `estado_revision != "aprobado_editorial"` — recordatorio de que no deben alimentar un informe institucional todavía | No |

## Prueba real: corrida contra el borrador de Palermo Soho/Hollywood (Etapa Infra-4)

```
.venv/Scripts/python.exe scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/qa_capa_editorial.py outputs/polos_gastro/experimentos/infraestructura_cartografica_v1/macrozonas_editorial_v1_borrador.geojson
```

**Resultado: NO PUBLICABLE, 2 gates duros.** El QA detectó, correctamente, que las dos
subzonas (`MZ_PALERMO_SOHO`, `MZ_PALERMO_HOLLYWOOD`) declaran `polo_id = MZ_PALERMO`, pero
ese polígono de nivel `polo` **no existe** en el archivo — porque en la Etapa Infra-4 solo
se trazaron las dos subzonas, nunca el contorno del polo "Palermo" completo (que incluiría
también Las Cañitas, Palermo Chico y Palermo Nuevo/Botánico, no construidos en esta
sesión). Es un hallazgo genuino, no un bug del QA: confirma que el gate G5 funciona
(detecta jerarquías rotas) y documenta honestamente que el trabajo de Infra-4 es parcial
por diseño (un caso de prueba, no la capa completa). También reportó correctamente B3
(0 % de cobertura, porque no hay ningún polígono de nivel `polo` todavía) y B4 (ambas
features en estado `borrador`, como corresponde).

Esta es exactamente la función que debe cumplir el QA: **nadie necesita revisar a mano si
la jerarquía está completa o si algo quedó en borrador** — el script lo dice.

## Qué falta para un QA "de producción" (fuera de esta etapa)

- Verificar la lista de `contiene_semilla_ids` contra la geometría real (¿el polígono
  contiene efectivamente esos puntos semilla de Fase 13?) — el campo existe en el esquema
  (Infra-2) pero su verificación automática no se implementó aquí porque hoy no hay
  ninguna capa con ese campo completado.
- Umbral de B2 (2 % del área menor) es un valor inicial razonable, no calibrado contra
  casos reales de solapamiento intencional (p. ej. una subzona "de contexto" que se
  superpone a propósito, como Palermo Chico en fase16) — a ajustar en el piloto.
- El chequeo de cobertura (B3) hoy compara contra el 100% de CABA; cuando se decida qué
  macrozonas están "fuera de alcance por diseño" (Etapa Infra-7), convendría documentarlas
  explícitamente en vez de que el QA reporte siempre un porcentaje bajo sin contexto.
