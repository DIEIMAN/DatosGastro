# Componentes — DGDGAS Informes Design System v1

Inventario de componentes reutilizables. Cada informe se arma combinando estos bloques; el layout no se rehace por proyecto. Los valores de estilo referencian `tokens.json`.

**Marca pública:** DGDGAS — Dirección General de Desarrollo Gastronómico · **Nombre interno:** DataGastro (no público).
**Regla transversal:** no inventar datos, no generar rankings, mapas = referencia territorial (no delimitación oficial), no usar Google Places como fuente pública.

Convención de campos: `token` = marcador de dato que completa cada proyecto (p. ej. `{ig_pct}`); el sistema no fija cifras.

---

## 1. Portada

- **Propósito.** Apertura institucional del informe.
- **Campos esperados.** `kickerMarca` (fijo: "DGDGAS – Dirección General de Desarrollo Gastronómico"), `kickerTipo` (p. ej. "Informe de resultados" / "Relevamiento territorial"), `titulo`, `subtitulo`, `descripcion`, `piePresenta`, `fecha`.
- **Estilos.** Banda superior `brand.primary`; kicker en `mono` `brand.accent`; título `type.h1`; regla de 34×2px `brand.accent`; bajada `ink.muted`.
- **Cuándo usarlo.** Siempre, como primera página.
- **Cuándo no.** Nunca con marca DataGastro; nunca con foto de comida ni estética de folleto.

## 2. Índice

- **Propósito.** Mapa de secciones con números de página.
- **Campos.** `entradas[]` = `{ num, texto, pagina, sub? }`.
- **Estilos.** Título `type.h2`; entradas `type.body`; subsecciones indentadas y atenuadas (`ink.faint`); número de página en `mono`.
- **Cuándo.** En todo informe de 3+ secciones.
- **Cuándo no.** En resumen ejecutivo de una carilla.

## 3. FichaRelevamiento (Datos generales)

- **Propósito.** Ficha técnica del relevamiento: modalidad, lugar, fechas, volumen.
- **Campos.** `modalidad`, `lugar`, `fechas`, `universo`/`base`, `distribucion?` (por día/franja).
- **Estilos.** Tabla de dos columnas etiqueta/valor (`table` cell); etiquetas en `mono` uppercase `ink.faint`.
- **Cuándo.** Sección 1 de informes con encuesta o relevamiento.
- **Cuándo no.** Como reemplazo de la metodología completa (esa va al AnexoMetodologico).

## 4. PreguntaAnalizada

- **Propósito.** Mostrar la pregunta **antes** del resultado y su tipo.
- **Campos.** `pregunta`, `tipo` (cerrada | abierta | multi-respuesta | consentimiento), `observa?`.
- **Estilos.** Borde izquierdo 3px `brand.secondary`; label `mono` uppercase `state.media.text`; pregunta `type.h3`; chip de tipo.
- **Cuándo.** En cada bloque de resultados de encuesta.
- **Cuándo no.** Para variables no provenientes de una pregunta; no fusionar dos preguntas distintas en una sola caja.

## 5. LecturaResultados

- **Propósito.** Lectura descriptiva y prudente del dato ya mostrado.
- **Campos.** `texto` (prosa, oraciones completas).
- **Estilos.** Fondo `surface.base`; label `mono` uppercase `ink.muted`; cuerpo `type.body`.
- **Cuándo.** Después de una tabla, gráfico o mapa.
- **Cuándo no.** Para afirmar representatividad que el relevamiento no tiene; sin conclusiones fuertes.

## 6. NotaMetodologica

- **Propósito.** Aclaración breve de método en el cuerpo (p. ej. menciones en multi-respuesta).
- **Campos.** `texto` (breve).
- **Estilos.** Borde izquierdo 3px `brand.accent`; fondo `surface.warm`; label `mono` `state.debil.text`; texto `type.small`.
- **Cuándo.** Junto al resultado que necesita la aclaración (multi-respuesta → "la suma puede superar 100%").
- **Cuándo no.** Para notas largas; esas van al AnexoMetodologico.

## 7. TablaInstitucional

- **Propósito.** Tabla ejecutiva/legible de resultados o comparaciones.
- **Campos.** `columnas[]`, `filas[]`; valores numéricos alineados a la derecha; `caption` (universo/base/fuente).
- **Estilos.** Header `table.header` (azul); filas alternadas `table.rowAlt`; divisores `table.rowDivider`.
- **Cuándo.** Cuando la tabla explica mejor que un gráfico; en informes ejecutivos.
- **Cuándo no.** Con aspecto de planilla cruda; sin caption de base/fuente.

## 8. TablaPolos

- **Propósito.** Clasificación territorial larga con estado por fila.
- **Campos.** `polo`, `estadoDoc` (chip), `tipoTerritorial`, `barriosComunas`, `recomendacion`, `observaciones?`.
- **Estilos.** `TablaInstitucional` + chip de `EstadoDocumentacion` en celda (`chip.dotSmall`).
- **Cuándo.** Universo de polos o casos territoriales.
- **Cuándo no.** Como ranking; el orden es por grupo, no por puntaje. Recomendaciones en tono prudente ("En espera de evidencia", no "Dejar afuera").

## 9. FichaPolo

- **Propósito.** Ficha estándar por polo, media o página completa.
- **Campos.** `nombre`, `grupo`, `tipoTerritorial`, `estadoDoc` (chip), `evidencia`, `referenciasPreliminares?`, `limitesMetodologicos`, `queFaltaValidar`, `recomendacionPrudente`.
- **Estilos.** Cabecera `surface.base` con chip de estado; grilla etiqueta/valor; pie con `NotaMetodologica`/recomendación (borde `brand.accent`).
- **Cuándo.** Para desarrollar núcleos y casos relevantes.
- **Cuándo no.** Sin separar evidencia de límites; sin recomendación prudente.

## 10. MapaContexto

- **Propósito.** Ubicación territorial de referencia, no delimitación.
- **Campos.** `barrios` (capa tenue), `marcadores[]` = `{ grupo, halo|dot }`, `leyenda`, `disclaimer`, `fuenteCartografica`.
- **Estilos.** `map.*`: barrios tenues, halos por grupo, disclaimer `map.disclaimer`, fuente al pie.
- **Cuándo.** Cuando el territorio ayuda a leer el dato.
- **Cuándo no.** Con polígonos de polos, bordes que parezcan oficiales, mapas de red, o geometría de plataformas privadas.

## 11. RequiereValidacion

- **Propósito.** Marcar evidencia parcial que aún no habilita conclusiones.
- **Campos.** `texto`.
- **Estilos.** Fondo `state.validacion.bg`, borde `state.validacion.border`, punto `state.validacion.dot`.
- **Cuándo.** Casos de documentación débil o URLs sin verificar.
- **Cuándo no.** Como alarma; no usar rojo.

## 12. EstadoDocumentacion (EstadoChip)

- **Propósito.** Calificar la evidencia de un dato/polo de un vistazo.
- **Campos.** `estado` (fuerte | media | debil | pendiente | enEspera | contexto | anexo | interno), `nota?`.
- **Estilos.** `chip` + color de `state[estado]`. El texto siempre nombra el estado.
- **Cuándo.** En tablas, fichas y junto a datos.
- **Cuándo no.** Con rojo (reservado a `state.alerta`); sin etiqueta textual.

## 13. QueHabilita

- **Propósito.** Explicitar qué decisiones/mejoras habilita el relevamiento y qué NO.
- **Campos.** `texto`.
- **Estilos.** Fondo `state.media.bg`, borde `state.media.border`, label `mono` `state.media.text`.
- **Cuándo.** Al cierre de una sección de resultados o del informe.
- **Cuándo no.** Para prometer alcances no sostenidos ("no constituye padrón de locales activos").

## 14. AnexoMetodologico

- **Propósito.** Fuentes, criterios de clasificación, límites y material secundario.
- **Campos.** `fuentes[]`, `criterios`, `advertenciaMapas`, `queFaltaValidar`, `visualesDescartados?`.
- **Estilos.** Etiqueta de página `ANEXO` (`state.debil`); cuerpo `type.body`/`type.small`; listas con viñeta `brand.accent`.
- **Cuándo.** Al final, para todo lo que no va al cuerpo principal.
- **Cuándo no.** Para material que debería estar en el cuerpo; no exponer fuentes privadas, URLs internas ni datos personales.

---

## Bloques auxiliares

- **FuenteEvidencia** — lista breve de fuentes de un bloque (viñetas `brand.accent`).
- **AlcanceAdvertencia** — disclaimer de alcance neutro (borde `line.strong`, sin rojo salvo advertencia real).
- **SeccionHeader** — número `mono` `brand.accent` + título `type.h2` + regla.
- **ResultadoBarras** — barras horizontales de menciones/%, valores como `{token}`, base declarada.

## QA público (antes de exportar)

Sin rutas locales · sin scripts/hashes · sin emails/teléfonos · sin CUIT/DNI · sin API keys ni links privados · marca DGDGAS (no DataGastro) · sin respuestas individuales identificables.
