# Reencuadre metodologico PolosGastro - Fase 10

Fecha de trabajo: 2026-07-02. Documento interno de preparacion. No es Borrador 4, no es informe
final, no es PDF, no es DOCX y no aplica diseno institucional.

## 1. Cambio de criterio

La Fase 10 modifica el criterio de trabajo usado en fases anteriores. El documento semilla del area
pasa a ser el punto de partida del universo valido de polos gastronomicos. Si un polo aparece en ese
documento, se considera parte del universo de trabajo.

La tarea deja de ser decidir si un polo "existe" o "no existe". A partir de esta fase, el trabajo
consiste en complementar, documentar, enriquecer, jerarquizar editorialmente, sumar fuentes y
preparar una capa de puntos gastronomicos por polo.

Este cambio no convierte el documento semilla en fuente publica validada, padron oficial, ranking ni
delimitacion territorial. Lo convierte en el universo operativo definido por el area para ordenar el
trabajo.

## 2. Rol de la investigacion complementaria

La investigacion complementaria no valida la existencia de los polos del universo semilla. Su funcion
es fortalecer la descripcion, la documentacion disponible, la lectura territorial y la
jerarquizacion editorial de cada caso.

Por lo tanto, cuando un polo tiene poca informacion publica, no se descarta. Se lo describe con una
de estas lecturas:

- documentacion publica a reforzar;
- informacion complementaria pendiente;
- relevancia territorial acotada;
- requiere ampliacion documental.

El informe futuro debe hablar de relevancia, documentacion disponible, oportunidades de gestion y
necesidades de profundizacion. No debe usar un esquema de "entra/no entra".

## 3. Universo semilla y documentos previos

La base de esta fase es `docs/polos_gastro/fase7/DOCUMENTO_SEMILLA_POLOS_Y_LOCALES.md`. La tabla de
Borrador 3 se usa como insumo de contexto para recuperar grupo anterior, tipo territorial y nivel de
documentacion.

Cuando el documento semilla agrupa una macroarea y Borrador 3 la desagrega, se conserva la lectura
semilla como unidad de trabajo y se deja trazada la desagregacion existente. El caso mas claro es
Palermo, que el documento semilla presenta como un polo con subzonas, mientras Borrador 3 conserva
tres registros base: Palermo Soho, Palermo Hollywood y Las Canitas.

## 4. Reinterpretacion de la capa objetiva de Fase 8

La capa objetiva de Fase 8 fuerte se reinterpreta como contexto territorial, no como filtro de
entrada. Su funcion es aportar senales de presencia relativa en fuentes locales disponibles y
advertir limitaciones por barrio, comuna, subpolo o corredor.

No debe usarse para:

- excluir polos del universo semilla;
- ordenar polos como ranking;
- afirmar densidad real;
- validar vigencia operativa de locales;
- cerrar delimitaciones oficiales;
- convertir una senal barrial en prueba de un subpolo o corredor.

Su uso recomendado para Borrador 4 es cualitativo y metodologico: senal territorial de contexto,
siempre acompanada por la limitacion territorial correspondiente.

## 5. Capa de locales gastronomicos

Los locales mencionados en el documento semilla son obligatorios para la futura capa de puntos. Si
un local aparece en el documento semilla, debe figurar en la tabla de locales semilla, con origen
`documento_semilla` y prioridad `obligatorio`.

Esta incorporacion no afirma que el local este activo hoy, no constituye recomendacion oficial y no
equivale a padron. Es una capa de trabajo para geolocalizacion, fichas internas y revision manual.

Locales adicionales podran sumarse en fases posteriores si son claramente relevantes, tienen fuente
trazable y pasan revision manual. Esos locales complementarios no deben mezclarse con los locales
obligatorios del documento semilla sin una columna de origen.

## 6. Uso previsto de Google Places

Google Places se propone como capa complementaria de puntos gastronomicos, no como padron oficial.
No debe usarse para decidir si un polo existe, ni para reemplazar fuentes publicas, documentacion
del area o revision humana.

El orden metodologico recomendado es:

1. geolocalizar primero los locales del documento semilla;
2. revisar manualmente coincidencias, nombres y direcciones;
3. sumar, si se autoriza, locales complementarios relevantes por polo;
4. mantener identificadores, ratings y volumenes de resenas como campos internos;
5. publicar solo campos autorizados y revisados.

No se debe publicar raw de Google Places, `place_id`, API keys, ratings ni cantidades de resenas en
informes publicos salvo decision institucional explicita.

## 7. Lineamientos para Borrador 4

Borrador 4 deberia redactarse como un relevamiento territorial y gastronomico del universo definido
por el area. La pregunta editorial no es que polos se incluyen o excluyen, sino como se presenta la
relevancia de cada polo y que nivel de documentacion lo acompana.

El cuerpo del documento puede distinguir polos principales, polos relevantes, emergentes,
corredores/subzonas y polos con documentacion publica a reforzar. Las fichas por polo pueden
incorporar locales semilla como referencias preliminares, siempre con advertencia de que no son
padron ni ranking.

El Borrador 4 no debe parecer:

- ranking oficial de polos;
- delimitacion oficial de areas gastronomicas;
- padron de locales activos;
- guia comercial de recomendacion;
- validacion automatica por Google Places o por la capa objetiva.

## 8. Limites de esta fase

En esta fase no se genera Borrador 4 completo, PDF, DOCX, mapas finales ni llamadas a Google
Places. No se tocan datos fuente originales, Borrador 3, Cafecito, Mercados, Casas de Pastas,
pipeline general, tokens canonicos ni scripts productivos.

