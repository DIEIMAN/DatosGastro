# Delimitacion textual preliminar - PolosGastro

Fecha de corte documental: 2026-06-29.

## 1. Por que delimitacion textual antes de mapas

La Fase 3A trabaja con texto porque todavia no hay poligonos ni criterios cartograficos cerrados. Antes de dibujar mapas conviene saber si cada caso corresponde a barrio, subpolo, avenida, corredor o zona central.

La delimitación textual no equivale a polígono oficial.
Las comunas probables no constituyen validación cartográfica.
Las zonas sin fuente clara no deben mapearse como polígonos cerrados.
Los mapas futuros deben diferenciar polos consolidados, zonas relevantes y candidatos.

## 2. Diferencia entre tipos territoriales

- Barrio: unidad reconocible de CABA; puede servir para agrupacion, pero no prueba concentracion gastronomica.
- Subpolo: recorte dentro de un barrio, como Palermo Soho o Barrio Chino.
- Avenida: eje lineal que requiere tramo inicial/final para mapearse.
- Corredor: conjunto de calles o tramo con oferta; necesita fuente de delimitacion.
- Zona central: familia territorial amplia que puede contener varios barrios y subejes.

## 3. Familias territoriales propuestas

| familia_id | familia_nombre | polos |
| --- | --- | --- |
| palermo_y_subpolos | Palermo y subpolos | Palermo Soho, Palermo Hollywood, Las Cañitas |
| zona_costera_y_turistica | Zona costera y turistica | Puerto Madero, Costanera Norte |
| sur_historico_y_tradicional | Sur historico y tradicional | San Telmo, Avenida Caseros / Barracas, Parque Patricios |
| zona_central | Zona central y Recoleta | Recoleta, Microcentro / Centro, Nuevo Bajo en Retiro / Esmeralda y Paraguay, Monserrat, Retiro |
| belgrano_y_norte | Belgrano y norte | Barrio Chino, Bajo Belgrano, Belgrano R, Federico Lacroze / Libertador a Cabildo |
| oeste_y_barrios_con_oferta | Oeste y barrios con oferta | Caballito, Devoto, Villa Pueyrredón / Av. San Martín, Flores, Floresta |
| corredores_emergentes_norte_oeste | Corredores emergentes norte-oeste | Villa Crespo, Chacarita, DoHo / Donado-Holmberg, Villa Urquiza, Parque Saavedra / García del Río, Paternal, Colegiales |
| cultura_avenidas_y_noches | Cultura, avenidas y noches | Avenida Corrientes, Abasto, Avenida Boedo |

## 4. Delimitaciones con mayor precision

- Alta: Palermo Soho, Palermo Hollywood, DoHo / Donado-Holmberg.
- Media: Las Cañitas, Puerto Madero, San Telmo, Chacarita, Barrio Chino, Recoleta, Costanera Norte, Avenida Corrientes, Devoto, Monserrat, Retiro.

## 5. Delimitaciones debiles o pendientes

- Baja: Villa Crespo, Bajo Belgrano, Belgrano R, Caballito, Avenida Caseros / Barracas, Microcentro / Centro, Abasto, Avenida Boedo, Villa Urquiza, Nuevo Bajo en Retiro / Esmeralda y Paraguay, Paternal, Villa Pueyrredón / Av. San Martín, Colegiales, Flores, Floresta, Parque Patricios.
- Sin delimitacion: Federico Lacroze / Libertador a Cabildo, Parque Saavedra / García del Río.

## 6. Riesgos metodologicos

- Usar comunas probables como si fueran validacion cartografica.
- Dibujar poligonos cerrados para avenidas o corredores sin tramo documentado.
- Sobregeneralizar barrios enteros desde un hito gastronomico puntual.
- Fusionar casos solapados sin justificar escala.

## 7. Que falta antes de dibujar mapas

- Resolver o documentar URLs pendientes restantes.
- Definir si el mapa conceptual usara familias, etiquetas, puntos o lineas antes que poligonos.
- Separar nucleo principal, zonas relevantes y candidatos con simbolizacion distinta.
- Revisar manualmente las delimitaciones de baja precision.

## 8. Recomendacion para Fase 3B

Preparar un mapa conceptual no final por familias territoriales, preferentemente con etiquetas y lineas/corredores preliminares. No avanzar a poligonos cerrados hasta tener una fuente territorial o un criterio documentado por cada caso.

## Conteo por precision

| nivel_precision | cantidad |
| --- | --- |
| alta | 3 |
| media | 11 |
| baja | 16 |
| sin_delimitacion | 2 |

<!-- FASE3B_LECTURA_VISUAL_START -->
## Lectura visual preliminar

En Fase 3B se generaron visualizaciones conceptuales para ordenar el universo PolosGastro antes de un informe final:

- `outputs/polos_gastro/graficos/universo_polos_por_grupo.png`
- `outputs/polos_gastro/graficos/precision_delimitacion_polos.png`
- `outputs/polos_gastro/graficos/familias_territoriales_polos.png`
- `outputs/polos_gastro/graficos/mapa_conceptual_polos_gastro.png`
- `outputs/polos_gastro/graficos/mapa_conceptual_polos_gastro_completo.png`

Son visualizaciones conceptuales porque no usan geocodificación, no incorporan una base cartográfica definitiva y no convierten delimitaciones textuales en polígonos. Sirven para lectura interna, priorización y diseño del informe futuro.

Riesgos de interpretación:

- Leer el diagrama como mapa oficial.
- Convertir candidatos en zonas validadas.
- Interpretar familias como límites administrativos.
- Usar casos de baja precisión como áreas cerradas.
- Confundir fuentes documentales con padrón de locales activos.

Casos no mapeados en el mapa conceptual principal: Bajo Belgrano, Avenida Boedo, Federico Lacroze / Libertador a Cabildo, Parque Saavedra / García del Río, Villa Pueyrredón / Av. San Martín.

Próximos pasos para un mapa final: cerrar fuentes pendientes, validar geometrías con un criterio cartográfico documentado, decidir simbología institucional y separar puntos, líneas y áreas según nivel de evidencia.
<!-- FASE3B_LECTURA_VISUAL_END -->
