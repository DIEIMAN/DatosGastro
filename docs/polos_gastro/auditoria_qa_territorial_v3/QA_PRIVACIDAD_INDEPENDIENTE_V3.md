# QA de privacidad independiente V3

## Alcance

Revisión de GeoJSON, CSV, JSON, SVG, manifest y ZIP de la corrida territorial V3. No se inspeccionaron ni exportaron valores identificables de fuentes crudas.

## Resultado

| Control | Resultado |
| --- | --- |
| Nombres comerciales en GeoJSON editorial | NO DETECTADOS |
| Domicilios, email, teléfono, CUIT/DNI | NO DETECTADOS |
| `place_id` / API keys / links privados | NO DETECTADOS |
| CSV de asignación | SANITIZADO; referencias `Pxxxxx`, sin coordenadas |
| GeoJSON territoriales | SIN PII; geometrías agregadas |
| SVG/metadata | SIN PII o secretos detectados |
| Puntos técnicos | 1.536 coordenadas exactas con referencias sanitizadas |

## Hallazgo de separación

`PUNTOS_ASOCIADOS_SANITIZADOS_V3.geojson` no contiene nombres ni domicilios, pero sí coordenadas puntuales exactas. Debe declararse **INTERNO_TECNICO_NO_PUBLICABLE** y quedar fuera de cualquier paquete institucional/publicable. Las capas territoriales y los mapas institucionales no necesitan distribuir esas coordenadas.

Los mapas actuales muestran puntos sin rótulos individuales. El riesgo es menor que distribuir el GeoJSON puntual, pero la versión institucional debería omitirlos para evitar reidentificación por cruce espacial y para cumplir el contrato editorial.

## Dictamen

Privacidad de las capas territoriales: **APTA**. Separación entre insumo técnico y entregable público: **REQUIERE AJUSTE**. No se detectó un bloqueo por exposición directa de datos personales.
