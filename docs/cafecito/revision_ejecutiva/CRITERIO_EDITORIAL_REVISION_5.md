# Criterio editorial - Revision 5 de Cafecito

Fecha: 2026-07-02. Documento interno. Explica las decisiones editoriales de
`INFORME_CAFECITO_REVISION_5_EDITORIAL.md`, que propone una arquitectura intermedia entre la
Revision 4 (completa pero repetitiva) y la version ejecutiva simplificada (clara pero demasiado
corta para reemplazar al informe).

## 1. Por que no se usa la version ultra resumida como reemplazo total

La version ejecutiva simplificada (~4 paginas) resolvio la lectura de autoridad, pero recorto
cosas que el informe principal debe conservar:

- **El analisis por pregunta.** El formulario es el activo del relevamiento; el informe principal
  debe rendir cuentas de cada pregunta, no solo de bloques tematicos. La fusion de preguntas en
  bloques (por ejemplo, primera vez + contacto) servia para el resumen, pero borraba la
  correspondencia uno a uno con el formulario.
- **Datos completos pedidos en su momento:** acompanamiento, distincion explicita entre la
  pregunta cerrada de zona y la abierta de barrio, y el detalle de intereses mas alla del top 5.
- **La funcion de expediente:** la Revision 4 documenta el relevamiento ante cualquier consulta
  posterior; una pieza de 4 paginas no cumple ese rol.

La version ejecutiva queda como pieza de lectura rapida (y el resumen de una pagina para mail);
la Revision 5 es la candidata a informe principal.

## 2. Que se recupera de la Revision 4

- El analisis pregunta por pregunta (las 10 preguntas, en el orden del formulario).
- La distincion entre la pregunta cerrada de residencia y la abierta de barrio/localidad, ahora
  como dos preguntas consecutivas (3 y 4) con una nota de una linea.
- El acompanamiento (pregunta 8), que la version ejecutiva habia sacado del cuerpo.
- El inventario de preguntas del formulario, reubicado como Anexo 2 en formato lista simple.
- La nota sobre correo electronico y pregunta cultural, reducida a una linea del Anexo 2.
- El anexo de red de cafeterias con sus tres datos y su nota prudente.
- Toda la prudencia de lenguaje: menciones (no preferencias), muestra acotada, potencial
  ("podria", "convendria"), sin promesas.

## 3. Que se toma de la version ejecutiva

- La piramide invertida: resumen ejecutivo fuerte al inicio (era la seccion 10 de la Revision 4,
  al final).
- La estructura dato -> lectura -> implicancia, ahora aplicada por pregunta.
- La ficha compacta de datos generales.
- La aclaracion de multi-respuesta dicha una sola vez en el cuerpo (intro de la seccion 3) y una
  vez en el anexo metodologico.
- La lectura institucional como seccion propia (confirma / abre / observar / mejorar).
- El anexo metodologico breve unificado.
- Las fechas correctas y verificadas (sabado 27, 10:00-18:30; domingo 28, 10:00-18:00).

## 4. Que se elimina por repetitivo

- La pagina de "Preguntas del formulario" del cuerpo (pagina 4 de la Revision 4): duplicaba lo que
  las secciones tematicas repetian; sobrevive como lista simple en el Anexo 2.
- El andamiaje "Pregunta analizada / Tipo / Que permite observar" repetido 9 veces: se reemplaza
  por una linea "Que se pregunto" por pregunta; el tipo de cada pregunta queda solo en el Anexo 2.
- La nota de multi-respuesta duplicada (identica en secciones 6 y 9 de la Revision 4).
- Las notas de fuente por subseccion ("Fuente: pregunta cerrada...", "Pregunta abierta...").
- La sintesis final (seccion 10 de la Revision 4): su contenido se movio al resumen ejecutivo; no
  se dice dos veces.
- El indice: con la nueva extension (~7-8 paginas maquetadas) es prescindible; si al maquetar se
  decide mantenerlo, es una fila de decision de diseno, no editorial.

## 5. Que pasa al anexo

- **Anexo 1:** toda la metodologia comun (base, agregacion, multi-respuesta, privacidad, limites),
  dicha una sola vez.
- **Anexo 2:** la lista de preguntas del formulario con su tipo, mas la aclaracion de correo y
  pregunta cultural.
- **Anexo 3:** la red de cafeterias (14 marcas, 39 sedes, 2 pendientes) con nota prudente; mapas y
  rankings quedan como respaldo fuera del documento.
- **Anexo 4:** informacion operativa: desglose por dia/franja (con marcador a confirmar),
  acompanamiento completo, menciones menores de intereses, y la aclaracion de que los cruces
  exploratorios son material interno.

## 6. Por que esta version es mas equilibrada

- **Conserva todo el contenido pedido** (10 preguntas, acompanamiento, residencia en dos
  preguntas, red de cafeterias) sin perder ningun dato de la Revision 4 que tenga valor de
  lectura; lo operativo baja al Anexo 4 en vez de desaparecer.
- **Elimina solo repeticion**, no informacion: cada aclaracion metodologica existe exactamente una
  vez en el cuerpo o una vez en el anexo.
- **Ordena para dos lectores a la vez:** la autoridad lee el resumen (pagina 1) y puede parar; el
  equipo lee las 10 preguntas y los anexos.
- **Prepara la maquetacion:** los comentarios `<!-- Página sugerida -->` proponen pares de
  preguntas por hoja (1-2, 3-4, 5-6, 7-8, 9-10), con pares tematicamente coherentes (perfil,
  territorio, vinculo, llegada y compania, motivaciones e intereses), estimando ~7-8 paginas
  finales contra ~14 de la Revision 4.
- **No toca nada existente:** la Revision 4, su YAML y la version ejecutiva quedan intactos; la
  Revision 5 es una propuesta paralela a decision humana.

## 7. Pendientes de decision humana

- Validar el recorte (en especial la eliminacion de la pagina de preguntas del cuerpo y de la
  sintesis final).
- Confirmar el desglose por dia/franja desde la Revision 4 (marcador
  `{dato_a_confirmar_desglose_por_dia_y_franja}`).
- Decidir si la Revision 5 pasa a ser el contenido de una futura regeneracion del PDF (via YAML
  editable + script de revision, con permiso) o queda como pieza Markdown.
- Decidir si se mantiene un indice al maquetar.
