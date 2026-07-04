# Fuentes y trazabilidad PolosGastro

## Fuente inicial

- Fuente inicial: `PDF Polos gastronómicos`.
- Archivo usado: `PolosGastro/Polos gastronómicos.pdf`
- Páginas procesadas: 8
- Estado: insumo semilla no validado.
- Uso en Fase 1: inventario, normalización inicial y base candidata.

## Cómo se extrajo

El script `scripts/polos_gastro/inventariar_polos_gastro.py` localiza el PDF candidato dentro del proyecto, extrae texto con `pdftotext` cuando está disponible y registra la cantidad de páginas con `pdfinfo`. Dado que el PDF no tiene tablas estructuradas, la normalización de polos y locales se realiza mediante una carga controlada dentro del script, transcripta desde el texto del PDF.

## Cómo se normalizó

- Se asignó un `polo_id` estable para cada polo o agrupación candidata.
- Se normalizó el tipo de área usando categorías simples: barrio, subpolo, corredor, avenida, zona_costera, zona_central u otro.
- Se conservaron subzonas cuando el PDF las menciona.
- Se separaron filas ambiguas para no fusionar ni dividir sin documentación.
- Se marcó todo como `requiere_validacion = sí`.

## Campos inferidos

- `nombre_normalizado`
- `tipo_area`
- `barrio_o_zona_principal`
- `subzonas`
- `comuna_probable`
- `estado_candidato`
- `nivel_consolidacion`
- `descripcion_breve`
- `observaciones`

Estos campos son lecturas metodológicas de Fase 1. No constituyen validación oficial.

## Campos que requieren validación

- Comunas probables.
- Límites territoriales de cada polo.
- Tramos de avenidas y corredores.
- Vigencia de locales destacados.
- Naturaleza oficial, interna o documental del PDF.
- Criterio de consolidación de cada polo.

## Fuentes complementarias sugeridas para próximas fases

- Datos abiertos del GCBA.
- BA Capital Gastronómica.
- Ente de Turismo.
- Notas institucionales.
- Mapas de barrios y comunas.
- OpenStreetMap / Google Places solo si se define una fase de geocodificación y respetando reglas de uso; no scraping.
- Registros de habilitaciones gastronómicas ya disponibles en DataGastro, si corresponde, sin tocar el pipeline general todavía.

## Trazabilidad por fila

Los CSV generados incluyen `fuente_inicial`, `pagina_fuente`, `requiere_validacion` y `observaciones`. La página de fuente indica el lugar del PDF usado para sostener cada registro, pero no reemplaza una validación territorial o documental.

<!-- FASE2_VALIDACION_DOCUMENTAL_START -->
## Validacion documental Fase 2

Fecha de consulta documental: 2026-06-29.

- Fuentes semilla verificadas: 8.
- Filas normalizadas desde matriz Perplexity: 32.
- Filas de fuentes externas por polo: 80.
- Fuentes complementarias encontradas: 16.
- URLs pendientes unicas: 1.

### Criterios de confiabilidad

- `alta`: fuente oficial/turistica directamente vinculada al polo o fuente semilla central ya verificada.
- `media`: fuente periodistica, datos abiertos o hito turistico que aporta contexto o evidencia parcial.
- `baja`: fuente debil o poco pertinente; no se uso en esta fase.
- `requiere_revision`: mencion sin URL, fuente pendiente o evidencia insuficiente.

### Criterios de decision

- `incluir_como_polo_consolidado`: respaldo fuerte y uso posible en cuerpo principal con cautela metodologica.
- `incluir_como_polo_relevante`: respaldo documental suficiente, pero con redaccion prudente.
- `incluir_como_polo_emergente`: evidencia de oferta/identidad, pendiente de delimitacion y medicion.
- `incluir_como_corredor_candidato`: eje o corredor plausible, sin cierre territorial.
- `mencionar_en_anexo`: caso util para contexto o exploracion, no para argumento central.
- `no_incluir_aun`: evidencia insuficiente para una version ejecutiva.

### Diferencia entre tipos de fuente

- Oficial/GCBA: aporta marco institucional o datos publicos, pero puede estar orientada a gestion o turismo.
- Turistica: ayuda a identificar relato, identidad y atractivos; no debe usarse sola para cerrar delimitaciones.
- Periodistica: orienta concentracion, evolucion o agenda publica; requiere contraste.
- Datos abiertos: permite medicion futura, no valida por si solo la existencia institucional de un polo.
- Comercial: puede describir oferta privada; usar con cautela por sesgo promocional.
- Academica: no se encontro una fuente academica cargada en esta fase.

### Limitaciones

La matriz sigue siendo exploratoria. No se geocodificaron locales, no se genero mapa final, no se modifico pipeline y no se reemplazo la base candidata Fase 1.
<!-- FASE2_VALIDACION_DOCUMENTAL_END -->
