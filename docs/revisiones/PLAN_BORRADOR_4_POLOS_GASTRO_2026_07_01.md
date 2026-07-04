# Plan Borrador 4 - PolosGastro (version presentable interna)

Fecha: 2026-07-01. Documento interno de planificacion. Define que deberia ser el Borrador 4 y en
que orden producirlo. No ejecuta nada: cada paso requiere decision humana previa.

Insumos: Borrador 3 con ajustes menores post-auditoria, revision final del 2026-07-01, propuesta
de decisiones humanas (`PROPUESTA_DECISIONES_HUMANAS_BORRADOR_4.md`), preview v2 y sus dos
evaluaciones (accesibilidad y tabla de 32 filas).

## 1. Objetivo de Borrador 4

Producir la **version presentable interna** del informe de polos gastronomicos: un documento que
jefatura pueda leer completo sin conocer el expediente metodologico, con las decisiones humanas ya
aplicadas y trazadas. **No es un documento publico** y no se genera como PDF/DOCX final hasta
revisar diseno y contenido. Sigue sin medir densidad, vigencia ni delimitar polos.

## 2. Que deberia incorporar

- Las decisiones humanas cerradas (seccion 4), aplicadas con trazabilidad: cada cambio de grupo
  cita la decision que lo autorizo.
- La estructura ejecutiva del Borrador 3 (resumen ejecutivo -> hallazgos -> limites -> proximos
  pasos -> anexos), con redaccion pulida para lectura de jefatura.
- La tabla ejecutiva breve (6-8 casos) en el cuerpo, segun el formato validado en la preview.
- La lectura comparada documental + senal cualitativa, sin indice numerico.
- Las advertencias obligatorias del anexo tecnico, trasladadas a donde corresponda del cuerpo.
- Una seccion explicita de "que habilita / que no habilita" (ya existe en Borrador 3; se conserva).
- Marca DGDGAS como unica marca visible; DataGastro solo si el documento circula como interno
  tecnico.

## 3. Que deberia dejar en anexo

- La tabla completa de 32 registros, en 3 bloques con cortes por grupo (formato validado en la
  preview v2), con 6 columnas y lectura prudente obligatoria.
- La metodologia de la capa objetiva y sus advertencias (esquema del Borrador 3 sin cambios).
- El detalle de fuentes por caso (solo tras QA editorial de que fuentes se nombran).
- Las decisiones humanas registradas (acta breve) como anexo de trazabilidad.
- Las referencias del documento semilla **no** entran ni al cuerpo ni al anexo publico: quedan
  como insumo interno; a lo sumo, conteos agregados (recomendacion conservadora 8).

## 4. Decisiones humanas a cerrar antes de redactar

En orden de impacto (detalle y recomendacion conservadora en la propuesta de decisiones):

1. Paternal: sube o no a documentacion media.
2. Bajo Belgrano: pasa o no a anexo a validar.
3. Corrientes / Abasto: tratamiento cruzado.
4. Caseros / Barracas: denominacion y recorte.
5. DoHo y Costanera Norte: recortes textuales.
6. Parque Saavedra: verificacion o degradacion de la fuente Clarin.
7. Referencias del documento semilla: insumo interno vs conteos agregados.
8. Capa objetiva: confirmacion del esquema cuerpo-cualitativo / anexo-sin-indice.
9. Columna "senal (contexto)" en la tabla del anexo: se mantiene o va solo en fichas.

Formato sugerido: acta breve (una linea por decision: aprobada / rechazada / pospuesta + quien y
cuando). Sin acta, el Borrador 4 no deberia redactarse.

## 5. Que diseno se podria aplicar

Sobre **copia controlada** (nunca sobre los archivos de fase9), lo validado por las previews:

- Tokens experimentales mapeados + los ajustes de contraste AA de la evaluacion de accesibilidad
  (captions con text.secondary, eyebrow #2C6E9E, variantes de texto para accent y validation).
- Los `state_details` completos (incluidos los tres propuestos: contexto, no_delimita, anexo).
- Componentes: portada DGDGAS, cinta de estado del documento (obligatoria), tabla ejecutiva,
  tabla completa con cortes por grupo, chips con etiqueta textual, cajas de lectura / advertencia /
  nota metodologica, placeholder de mapa con disclaimer.
- Footer con patron `DGDGAS - {proyecto} - {tipo}` y folio.

## 6. Que diseno NO aplicar todavia

- Actualizacion de tokens canonicos (`design_tokens_dgdgas.json/.yaml`): requiere aprobacion
  explicita y su propia etapa.
- Cambios a `style_tokens_dgdgas.py` o `scripts/shared/`: scripts productivos, requieren permiso.
- Halos de mapa, coropleticos o cualquier mapa real.
- Sombras en salida imprimible, chips complejos dependientes de render PDF/DOCX.
- Cualquier orden o color derivado del nivel de senal (regla dura anti-ranking).
- Webfonts o instalacion de tipografias (decision tipografica pendiente).

## 7. Que mapas podrian venir despues

Solo despues del Borrador 4 aprobado y con autorizacion especifica:

- **Mapa de contexto por barrio/comuna** (unico tipo recomendado): base cartografica oficial
  (Buenos Aires Data - Barrios CABA), marcadores o sombreado tenue de referencia, disclaimer y
  fuente visibles, sin poligonos de polos, sin halos, sin escala de color que reproduzca la senal
  como ranking.
- Nunca: mapas de delimitacion de polos, subpolos o corredores; mapas con datos de plataformas
  privadas o Google Places.

## 8. Orden de salidas recomendado

1. **Markdown presentable** (Borrador 4 propiamente dicho): primera salida. Todo el contenido y
   las decisiones, sin diseno. Es lo que se revisa metodologicamente.
2. **HTML preview de la copia controlada con diseno aplicado**: segunda salida. Valida el diseno
   sobre el contenido real completo (no sobre extractos como las previews v1/v2).
3. **PDF de prueba**: tercera salida, solo si 1 y 2 pasan revision, con permiso para tocar los
   scripts de render si hiciera falta, y marcado "prueba - no publicable".
4. **DOCX de prueba**: despues del PDF (el render DOCX es el mas fragil para chips/tablas), solo
   si se necesita circuito de comentarios en Word.

**Recomendacion central:** el Borrador 4 debe ser una version presentable **interna, no publica**,
y no debe generarse como PDF/DOCX final hasta que diseno y contenido pasen revision humana. El
PDF/DOCX "final" es una decision separada, posterior, de jefatura.

## 9. Criterio de cierre del Borrador 4

- Acta de decisiones completa y aplicada sin excepciones silenciosas.
- QA de lenguaje: sin "locales activos", sin ranking, sin descarte, sin densidad/vigencia
  afirmadas, marca DGDGAS.
- QA de privacidad: sin fuentes internas no publicables, sin listados del documento semilla, sin
  rutas ni credenciales.
- Checklist de la revision final del Borrador 3 re-pasado sobre el nuevo texto.
- Registro de que quedo fuera (mapas, indice numerico, referencias semilla) y por que.
