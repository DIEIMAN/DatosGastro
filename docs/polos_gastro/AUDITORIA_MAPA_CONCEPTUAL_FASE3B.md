# Auditoría para mapa conceptual - Fase 3B

Fecha de corte documental: 2026-06-29.

Esta auditoría revisa los insumos locales ya generados para PolosGastro y define un criterio visual prudente. No se usó geocodificación, no se descargó geodata y no se modificaron fuentes.

## Insumos revisados

- `outputs/polos_gastro/universo_informe_polos_gastro.csv`
- `outputs/polos_gastro/base_delimitacion_preliminar_polos_gastro.csv`
- `outputs/polos_gastro/fuentes_por_familia_territorial.csv`

## Polos que pueden mapearse con seguridad conceptual

Pueden aparecer como etiquetas, puntos conceptuales o líneas conceptuales, siempre con nota metodológica visible:

- Palermo Soho
- Palermo Hollywood
- Las Cañitas
- Puerto Madero
- San Telmo
- Chacarita
- Barrio Chino
- Recoleta
- Costanera Norte
- Avenida Corrientes
- Devoto
- DoHo / Donado-Holmberg
- Monserrat
- Retiro

## Polos que solo pueden aparecer como etiqueta, punto aproximado o familia sin geometría

Estos casos pueden ayudar a pensar el informe, pero no deben leerse como zonas cerradas ni como delimitaciones institucionales:

- Villa Crespo
- Belgrano R
- Caballito
- Avenida Caseros / Barracas
- Microcentro / Centro
- Abasto
- Villa Urquiza
- Nuevo Bajo en Retiro / Esmeralda y Paraguay
- Paternal
- Colegiales
- Flores
- Floresta
- Parque Patricios

## Polos que no deberían mapearse todavía

Estos casos quedan fuera del mapa conceptual principal por estar en `no_incluir_por_ahora` o por no tener delimitación suficiente:

- Bajo Belgrano
- Avenida Boedo
- Federico Lacroze / Libertador a Cabildo
- Parque Saavedra / García del Río
- Villa Pueyrredón / Av. San Martín

## Familias mejor respaldadas

- Palermo y subpolos
- Zona costera y turística
- Zona central y Recoleta

## Familias débiles o mixtas

- Sur histórico y tradicional
- Belgrano y norte
- Oeste y barrios con oferta
- Corredores emergentes norte-oeste
- Cultura, avenidas y noches

## Riesgos visuales

- Confundir un diagrama conceptual con un mapa oficial.
- Convertir barrios amplios en polígonos cerrados sin fuente territorial.
- Dar la misma jerarquía visual a núcleos consolidados, candidatos y anexos.
- Representar casos de baja precisión como áreas completas.
- Leer familias territoriales como límites administrativos.
- Interpretar fuentes documentales como padrón de locales activos.

## Criterio de cierre de esta fase

La Fase 3B habilita gráficos de apoyo y un diagrama territorial esquemático. No habilita mapa institucional final, geocodificación de locales, shapefiles, geojson definitivos ni polígonos cerrados.
