# Auditoria Fase 2 - Validacion documental PolosGastro

Fecha de control: 2026-06-29.

Esta auditoria revisa la Fase 2 documental antes de avanzar a mapas o informe final. No modifica fuentes originales ni convierte la base en taxonomia oficial.

## Archivos revisados

- outputs/polos_gastro/perplexity_matriz_evidencia_seed.csv
- outputs/polos_gastro/fuentes_externas_polos_gastro.csv
- outputs/polos_gastro/matriz_validacion_polos_gastro.csv
- docs/polos_gastro/LECTURA_VALIDACION_DOCUMENTAL_POLOS_GASTRO.md
- docs/polos_gastro/FUENTES_Y_TRAZABILIDAD_POLOS_GASTRO.md
- docs/polos_gastro/DIAGNOSTICO_INICIAL_POLOS_GASTRO.md
- docs/polos_gastro/fichas_polos/

## Consistencia de conteos

| indicador | valor |
| --- | --- |
| Filas matriz Perplexity | 32 |
| Filas fuentes externas | 80 |
| Filas matriz validacion | 32 |
| Fichas Markdown | 32 |
| URLs pendientes en fuentes | 20 |
| Fuentes requiere_revision | 20 |

Los conteos principales declarados en Fase 2 son consistentes con los CSV reales: 32 filas Perplexity, 80 fuentes externas, 32 polos en matriz de validacion y 32 fichas.

## Polos duplicados, agregados o solapados

### Desagregaciones y agregados

- PG001 Palermo se desagrego en Palermo Soho, Palermo Hollywood y Las Cañitas.
- PG006 Belgrano se desagrego en Barrio Chino, Bajo Belgrano y Belgrano R.
- PG023 Abasto - Avenida Corrientes no se arrastro como fila propia: quedo representado por Abasto y Avenida Corrientes.

- Polos agregados en Fase 2 que no estaban como filas Fase 1: PGF2_COLEGIALES, PGF2_MONTSERRAT, PGF2_RETIRO, PGF2_FLORES, PGF2_FLORESTA, PGF2_PARQUE_PATRICIOS.
- Fila Fase 1 no trasladada literalmente a Fase 2: PG001_PALERMO_SOHO_HOLLYWOOD_Y_LAS_CANITAS, PG006_BELGRANO_BARRIO_CHINO_BAJO_BELGRANO_BELGRA, PG023_ABASTO_AVENIDA_CORRIENTES.

### Solapamientos territoriales relevantes

- Palermo Soho, Palermo Hollywood y Las Cañitas son subpolos de Palermo; no deben presentarse como barrios independientes.
- Barrio Chino, Bajo Belgrano y Belgrano R provienen de una base Fase 1 agregada de Belgrano; Barrio Chino debe tratarse como subzona comercial-cultural.
- Microcentro / Centro, Monserrat, Retiro y Nuevo Bajo en Retiro componen una familia de zona central; conviene agruparlos narrativamente y separar el subeje Nuevo Bajo.
- Avenida Corrientes y Abasto se solapan territorial y narrativamente; se recomienda analizarlos vinculados, sin fusionarlos todavia.
- DoHo / Donado-Holmberg y Villa Urquiza se solapan: el eje Donado-Holmberg no representa automaticamente todo el barrio.
- Paternal y Distrito del Vino no son equivalentes: el distrito tematico aporta contexto, no valida por si solo un circuito gastronomico.

## Fuentes sin URL o con URL pendiente

| polo | registros_url_pendiente |
| --- | --- |
| Abasto | 1 |
| Avenida Boedo | 2 |
| Avenida Corrientes | 2 |
| Bajo Belgrano | 1 |
| Belgrano R | 1 |
| Chacarita | 1 |
| Costanera Norte | 2 |
| Devoto | 1 |
| DoHo / Donado-Holmberg | 2 |
| Federico Lacroze / Libertador a Cabildo | 2 |
| Parque Saavedra / García del Río | 1 |
| Paternal | 2 |
| Villa Pueyrredón / Av. San Martín | 1 |
| Villa Urquiza | 1 |

Las URLs pendientes no impiden usar todos los casos como insumo exploratorio, pero si bloquean decisiones fuertes para informe principal o delimitacion cartografica.

## Fuentes potencialmente debiles

- Datos abiertos: sirven para una futura medicion de oferta, pero no validan por si solos la existencia institucional de un polo.
- Fuentes turisticas: ayudan a describir identidad, atractivos o relato, pero no cierran delimitaciones ni densidad.
- Hitos puntuales: patios, mercados o centros comerciales no validan por si solos un barrio completo.
- Perplexity: se mantiene como insumo de organizacion, no como fuente primaria para conclusiones finales.

## Decisiones demasiado agresivas detectadas

- Chacarita: pasa de informe principal a zona relevante por evidencia turistica directa pero todavia parcial.
- Barrio Chino: pasa de informe principal a zona relevante; es subzona comercial-cultural de Belgrano.
- Microcentro / Centro, Monserrat y Retiro: se mantienen como zona relevante agrupada, no como nucleos separados.
- Costanera Norte, Avenida Corrientes, DoHo / Donado-Holmberg y Paternal: quedan como emergentes/candidatos.

## Problemas de nombres publicos

- `Las Canitas` se normaliza como `Las Cañitas`.
- `Garcia del Rio` se normaliza como `García del Río`.
- `Villa Pueyrredon` se normaliza como `Villa Pueyrredón`.
- `Donado Holmberg` se usa como `Donado-Holmberg`.
- `Avenida Caseros/Barracas` se usa como `Avenida Caseros / Barracas`.
- `Microcentro/Centro` se usa como `Microcentro / Centro`.
- `Nuevo Bajo Retiro` se usa como `Nuevo Bajo en Retiro`.

## Resultado de la depuracion

| grupo_informe | cantidad |
| --- | --- |
| nucleo_principal | 6 |
| zona_relevante | 5 |
| emergente_o_candidato | 9 |
| anexo | 7 |
| no_incluir_por_ahora | 5 |

La depuracion no borra ni reemplaza la Fase 2: crea un universo defendible para una futura etapa de mapas e informe.
