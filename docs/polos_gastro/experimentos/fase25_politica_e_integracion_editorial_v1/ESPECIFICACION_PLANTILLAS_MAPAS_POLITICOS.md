# Especificación de plantillas para mapas políticos

Estado: **EXPERIMENTAL / NO OFICIAL**. No integra capas v2.1.  
Fecha: 2026-07-11.

## Reglas comunes

- Formato A4 vertical, área cartográfica dominante y una caja de lectura breve.
- Paleta, tipografías, márgenes y pies del sistema visual DGDGAS; no se crea una marca nueva.
- El tipo territorial define la geometría. La madurez define únicamente énfasis y distintivo.
- Sin nombres comerciales, puntos individuales, coordenadas, códigos técnicos ni métricas sin contexto.
- Toda franja es una convención orientativa; no constituye límite oficial.
- Placeholder obligatorio hasta la integración: `MAPA PENDIENTE - CAPA DE PRESENTACIÓN V2.1`.

## 1. Mapa general

- Propósito: lectura de conjunto de las 22 zonas de referencia.
- Capas requeridas: base CABA simplificada, zonas consolidadas, zonas con seguimiento y zonas en observación.
- Leyenda: tipo territorial y madurez en dos bloques separados.
- Requisito v2.1: jerarquía tipo/madurez, Costanera multiparte y metadatos de versión.
- No mostrar: polígonos técnicos, puntos individuales ni ranking.

## 2. Núcleo compacto

- Caso de referencia: San Telmo.
- Símbolo: contorno continuo y relleno pleno de baja opacidad.
- Elemento contextual: eje Defensa con trazo más fino y sin franja protagónica.
- Requisito v2.1: núcleo simplificado y eje contextual validado.

## 3. Corredor

- Caso de referencia: Avenida Corrientes.
- Símbolo: banda continua sobre el eje, sin cortes internos.
- Abasto: área asociada fuera de la geometría del corredor, con trama diferenciada.
- Nota: `Franja orientativa de representación; no constituye un límite oficial.`
- Requisito v2.1: corredor continuo y área asociada separada.

## 4. Red multinuclear

- Caso de referencia: Belgrano, solo después de decisión humana sobre la shortlist.
- Símbolo: núcleos con tratamiento idéntico, sin jerarquías ni contenedor duro.
- Madurez: `lectura en consolidación` mientras siga experimental.
- No mostrar: cantidad de polos como hallazgo, códigos de núcleos o nombres no firmados.
- Requisito v2.1: shortlist estricta y correspondencia post hoc revisada.

## 5. Frente doble

- Caso de referencia: Puerto Madero.
- Símbolo: dos bandas simplificadas sobre ambos márgenes de los diques.
- No mostrar: segmentos analíticos, subdivisiones técnicas ni referencias comerciales.
- Requisito v2.1: geometría de presentación simplificada y validación territorial.

## 6. Unidad multiparte

- Caso de referencia: Costanera Norte.
- Símbolo: tres piezas separadas bajo una etiqueta común; vacíos preservados.
- Contexto secundario: solo si se aprueba su ubicación editorial; nunca como cuarta componente.
- Madurez: `lectura exploratoria` y sin conectores entre piezas.
- Requisito v2.1: capas de los tres componentes y decisión sobre el contexto secundario.

## 7. Zonas en observación

- Propósito: mostrar señales que justifican seguimiento sin proponer geometría.
- Símbolo: mención textual o densidad difusa sin borde.
- No mostrar: polígonos, marcadores que parezcan locales o jerarquías de relevancia.
- Placeholder: listado editorial vigente hasta que cada escalado alcance una decisión registrada.

## Entrega esperada de cada asset futuro

- PNG de presentación y, si existe, versión vectorial.
- Dimensiones, sistema de referencia y fecha de generación.
- Hash SHA-256, versión de capa y decisión editorial asociada.
- Confirmación de ausencia de nombres comerciales, identificadores técnicos y coordenadas individuales.

