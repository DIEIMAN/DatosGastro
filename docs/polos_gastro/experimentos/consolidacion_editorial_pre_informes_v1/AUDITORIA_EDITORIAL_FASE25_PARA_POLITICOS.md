# Auditoría editorial de Fase 25 para presentación política

Estado: DOCUMENTACIÓN EDITORIAL EXPERIMENTAL. Fecha: 2026-07-11.
Pieza auditada: `outputs/polos_gastro/fase25_microajustes_finales_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_FASE25.pdf`
(11 páginas, generado por `scripts/polos_gastro/build_fase25_microajustes_finales_oficina.py`,
que hereda de fase24 → fase22).

Método: inspección visual directa de las 11 páginas rasterizadas
(`raster_pages/page-01..11.png`, misma fecha que el PDF), del texto extraído
(`pdf_text_extract.txt`), de los assets de mapas (`assets/*.png|svg`) y del generador.
**No se modificó nada.** Las acciones concretas están en `MATRIZ_AJUSTES_FASE25.csv`.

## Veredicto general

Fase 25 es una pieza honesta, sobria y de marca consistente, pero está calibrada para un
lector interno prudente, no para un decisor político. Sus tres problemas dominantes:

1. **Se define por lo que no es.** El resumen ejecutivo y una página entera (p. 4)
   están dedicados a advertencias. Un decisor lee "aproximado", "semilla", "no oficial"
   siete veces antes de encontrar un hallazgo.
2. **Jerga interna en superficie.** "Universo semilla" (aparece en 7 de 11 páginas),
   "área de lectura", "eje aprox.", "subzona aprox." son vocabulario de trabajo que en
   una lámina política transmite provisoriedad.
3. **Subutilización del espacio.** Páginas 3, 4 y 6 tienen entre un tercio y dos tercios
   de página vacíos; el mapa global (p. 5) ocupa menos de la mitad de su página. La pieza
   podría decir más con las mismas 11 páginas o decir lo mismo en 8–9.

Lo que **sí funciona** y debe conservarse: paleta y marca DGDGAS uniformes (nombre
institucional correcto en las 11 páginas), estructura repetida de las láminas de detalle
(mapa + dos cajas), mapas limpios sin saturación de puntos, pies de página consistentes,
y la decisión de fondo de no dibujar límites duros.

## Auditoría página por página

### Página 1 — Portada

- **Qué se entiende:** título claro, emisor claro, fecha clara. Correcta.
- **Qué sobra / falta:** el subtítulo "Informe" es genérico; no orienta sobre el tipo de
  pieza. Un decisor agradecería un subtítulo con contenido ("Lectura territorial de la
  actividad gastronómica").
- **Marca:** correcta (DGDGAS — Dirección General de Desarrollo Gastronómico).
- **Riesgo:** ninguno.

### Página 2 — Índice

- **Qué se entiende:** todo; las líneas guía ya no pisan el texto (corregido en F25).
- **Qué sobra:** en una pieza de 11 páginas el índice es prescindible para un público
  político; es media página de valor informativo bajo. Oportunidad de síntesis: fusionar
  con la portada o eliminar si la versión política queda en ≤10 páginas.
- **Riesgo:** ninguno.

### Página 3 — Resumen ejecutivo

- **Qué se entiende:** que la pieza ordena 22 polos y ejes y que no es un padrón. El
  mensaje sustantivo ("dónde se concentra la actividad") no está.
- **Demasiado técnico:** "universo semilla de 22 polos" (dos veces en la página);
  "insumo para la discusión institucional".
- **Qué no aporta a un decisor:** el segundo párrafo entero es negativo ("no constituyen
  límites oficiales, padrón de locales ni ranking gastronómico") — necesario, pero no
  como centro del resumen; se traslada condensado a una nota al pie de lámina o a la
  página de alcance.
- **Jerarquía visual:** enorme espacio vacío entre los párrafos y la caja "Lectura
  institucional" al pie; la página parece inacabada.
- **Sobrepromesa:** ninguna; el problema es el inverso (infrapromesa: la pieza vale más
  de lo que su resumen transmite).
- **Acción principal:** reescribir el resumen en positivo: 3–4 afirmaciones territoriales
  (concentración en el corredor norte, ejes tradicionales, zonas en observación) + 1
  línea de alcance.

### Página 4 — Alcance y criterio de lectura

- **Qué se entiende:** que todo es aproximado. Ese es el problema: una página completa
  de disclaimers (tres cajas: "Aclaración metodológica", "Universo semilla", "Subzonas")
  hace que la pieza entera parezca preliminar.
- **Demasiado técnico:** "capas auxiliares de geolocalización"; "universo semilla" como
  título de caja; "polígonos normativos".
- **Elementos que parecen preliminares:** la página entera funciona como descargo. Dos
  tercios inferiores vacíos refuerzan la sensación de borrador.
- **Acción principal:** condensar las tres cajas en una sola nota de alcance de 3–4
  líneas, en lenguaje institucional ("las áreas representadas son referencias de lectura
  territorial, no límites oficiales"), y liberar la página para contenido con valor
  (cifras clave, criterio de selección de las cinco zonas). Los tres párrafos completos
  van a la nota metodológica final.
- **Cómo mantener honestidad sin llenar de advertencias:** una sola nota bien escrita +
  rotulado consistente en leyendas cumple la misma función que tres cajas.

### Página 5 — Mapa general de polos y ejes gastronómicos

- **Qué se entiende:** dónde están las 22 zonas nombradas. Buen punto de partida.
- **Mapas saturados / imágenes con demasiado texto:** el mapa no está saturado, pero
  tiene 22 etiquetas del mismo peso visual: un decisor no distingue lo consolidado de lo
  exploratorio. Falta jerarquía (el requisito político central: "qué zonas están
  consolidadas, cuáles merecen seguimiento").
- **Tamaño:** el mapa ocupa ~45 % de la página; hay margen superior e inferior
  desaprovechado. Debería ser el elemento héroe de la pieza, a página casi completa.
- **Leyenda:** "Área aproximada" y "Eje / corredor aproximado" — la palabra "aproximado"
  en leyenda contradice DEC-09 (la convención se declara una vez, no se estampa en cada
  ítem). "Macroárea con subzonas" es jerga tolerable pero mejorable.
- **Caja "Lectura":** texto de relleno ("El mapa global ordena una mirada general de la
  Ciudad…") — no dice nada que el mapa no muestre. Reemplazar por un hallazgo real (p.
  ej., la concentración del arco norte + ejes históricos del centro-sur).
- **Costanera Norte:** aparece como eje lineal continuo; tras DEC-05/06 la
  representación futura deberá ser multiparte discontinua y rotulada exploratoria
  (requiere nuevo mapa, depende del pipeline híbrido).
- **Inconsistencia con DEC-01:** Corrientes y Abasto figuran como dos etiquetas de igual
  peso; la versión política debe presentar Corrientes como corredor único con Abasto como
  lectura asociada.

### Página 6 — Lectura territorial general

- **Qué se entiende:** cómo están agrupadas las páginas siguientes. Es una página
  "meta": habla del informe, no del territorio.
- **Qué no aporta a un decisor:** las tres cajas repiten casi literalmente los textos de
  las páginas 7–11 ("Corrientes y Abasto se presentan como áreas vinculadas pero
  diferenciadas" aparece idéntico en p. 6 y p. 10). Los tres bullets del pie repiten la
  p. 3 ("las menciones laterales funcionan como referencias del universo semilla").
- **Jerarquía visual:** hueco grande entre las cajas y los bullets.
- **Acción principal:** eliminar la página en la versión política o convertirla en la
  verdadera página de hallazgos ("qué muestra la lectura: concentración, ejes,
  seguimiento"), dejando de duplicar contenido.

### Páginas 7–11 — Láminas de detalle (estructura común)

Evaluación común a las cinco láminas (Palermo/Las Cañitas, Puerto Madero, San Telmo,
Corrientes/Abasto, Belgrano):

- **Qué se entiende:** la estructura mapa + "Referencias del universo semilla" +
  "Lectura territorial" es clara y repetible. Los mapas son limpios y elegantes.
- **Demasiado técnico (transversal):**
  - Tags bajo cada etiqueta de mapa: "SUBZONA APROX.", "ÁREA DE LECTURA", "EJE APROX.",
    "HITO", "NODO", "SUBZONA DE REFERENCIA". Seis vocabularios distintos de tag en cinco
    mapas; en Belgrano conviven tres en la misma lámina. Para un político son ruido y
    transmiten inseguridad. Acción: unificar en un solo sistema discreto (o quitar los
    tags y declarar la convención una vez en la leyenda).
  - Leyenda repetida "subzona aproximada / área de lectura / avenidas de referencia":
    "área de lectura" es jerga interna; "aproximada" otra vez.
  - Título de caja "Referencias del universo semilla": jerga; además el listado de
    locales con nombre propio (Don Julio, La Cabrera, Kansas…) en una pieza política
    roza el aval comercial aunque el descargo diga lo contrario. Acción: en la versión
    política, quitar los nombres de locales o llevarlos a anexo como "referencias
    ilustrativas"; si se conservan, retitular ("Referencias de la zona").
- **Duplicación título/mapa:** cada página repite el nombre de la zona tres veces
  (encabezado "Detalle: X", título del mapa "X", etiquetas internas). El título del mapa
  puede absorberse en el encabezado.
- **Elementos que parecen preliminares:** los rectángulos gris punteado ("área de
  lectura") de Abasto (p. 10), Bajo Belgrano y Belgrano R (p. 11) se ven como
  placeholders: cajas grises vacías con borde punteado. Riesgo alto de que un decisor
  pregunte "¿esto está sin terminar?".
- **Espacio:** en las cinco láminas el mapa ocupa ~40 % de la página y las cajas ~25 %;
  hay bandas vacías arriba y abajo del mapa. Mapas más grandes = más autoridad visual.

Observaciones específicas:

- **P. 7 Palermo:** la mejor lámina; tres subzonas con color diferenciado. "SUBZONA
  APROX." bajo cada nombre tres veces. La caja de lectura es sustantiva. Conservar como
  plantilla.
- **P. 8 Puerto Madero:** los rótulos ya se descargaron en F25 pero conviven cuatro
  categorías ("ÁREA DE LECTURA" ×2, "EJE APROX.", "HITO") en un mapa angosto; el eje
  naranja "Sector costero" y la banda azul "Docks" se superponen conceptualmente (dos
  representaciones del mismo frente). Tras la repetición técnica (Codex) este mapa
  probablemente se regenere (DH-06 abierto): no invertir en microajustes ahora.
- **P. 9 San Telmo:** etiqueta "Área gastronómica" + tag "ÁREA DE LECTURA" es
  redundante (área/área) y genérica: es la única zona cuyo polígono no tiene nombre
  propio. El rombo del Mercado es desproporcionado respecto de la trama. DH-01 sigue
  abierta: posible regeneración con eje Defensa respaldado.
- **P. 10 Corrientes/Abasto:** el corredor se dibuja correctamente como banda continua
  (compatible con DEC-01). El rótulo "Corrientes (9 de Julio – Callao)" fija extremos
  con precisión de calle: mantener solo si se declara convención. La caja gris punteada
  de Abasto parece placeholder (ver arriba). El título de página "Corrientes / Abasto"
  con barra sugiere paridad; DEC-01 pide comunicar Corrientes como corredor único con
  Abasto asociado: retitular ("Corrientes, con Abasto como área asociada" o similar).
- **P. 11 Belgrano:** tres tags distintos ("SUBZONA APROX.", "ÁREA DE LECTURA",
  "SUBZONA DE REFERENCIA") para tres subzonas — el lector no puede reconstruir la
  diferencia semántica. En la caja de referencias, "Belgrano R: subzona de referencia
  dentro de la macroárea" está listado entre locales: error de categoría. DEC-04: la
  lámina puede mantenerse como lectura editorial mientras se rotule como tal; los
  nombres no deben presentarse como jerarquía validada.

## Expresiones problemáticas: destino propuesto

| Expresión | Dónde aparece | Destino |
| --- | --- | --- |
| "universo semilla" | pp. 3, 4, 6, 7–11 (título de caja) | **Eliminar** de láminas; explicar una vez en nota metodológica como "relevamiento inicial de referencias" |
| "aproximada/o", "APROX." | leyendas y tags de todos los mapas | **Simplificar:** declarar una vez ("las áreas son referencias de lectura, no límites"); quitar de tags |
| "área de lectura" | leyendas pp. 7–11, tags | **Trasladar** a nota metodológica; en lámina usar "área de referencia" |
| "insumo para la discusión institucional" | p. 3 | **Simplificar** ("apoyo para el ordenamiento territorial") |
| "capas auxiliares de geolocalización" | p. 4 | **Trasladar** a nota metodológica |
| "no constituyen límites oficiales…" (triple negación) | pp. 3, 4 | **Simplificar** a una sola frase estándar, una vez |
| "macroárea con subzonas" | p. 5 leyenda, p. 11 | **Mantener** (comprensible) pero considerar "zona con sectores internos" |
| "hito colectivo" / "hito de lectura" | pp. 8, 9 | **Simplificar** a "hito" o "referencia" |
| "menciones laterales" | p. 6 | **Eliminar** (jerga de maquetación) |
| "zona aproximada", "candidato", "evidencia media", "polígono candidato" | no aparecen en Fase 25 (vocabulario de los experimentos) | **Prevención:** la guía de lenguaje debe impedir que entren en informes futuros |

## Riesgo de sobrepromesa

Bajo en el texto (la pieza peca de lo contrario). Dos riesgos puntuales:

1. Los nombres de locales pueden leerse como recomendación oficial pese al descargo.
2. El rótulo "Corrientes (9 de Julio – Callao)" y las avenidas nombradas fijan extremos
   con una precisión que la metodología no defiende; tolerable como convención declarada.

## Oportunidades de síntesis

1. Fusionar pp. 3+4 (resumen con una línea de alcance) → libera una página.
2. Eliminar o reconvertir p. 6 (duplicada) → libera otra página.
3. Con las dos páginas liberadas: mapa global a página completa con jerarquía visual
   (consolidado / eje / en observación) + una página final "Próximos pasos" que hoy no
   existe y es lo primero que pide un decisor.
4. Índice prescindible si la pieza queda en ≤10 páginas.

## Dependencias

- Cambios de texto, layout, leyendas, tags y estructura: **ejecutables ya** (no dependen
  de Codex ni del pipeline híbrido).
- Regeneración de mapas de Puerto Madero (DH-06), San Telmo (DH-01) y cualquier
  incorporación de jerarquía basada en evidencia nueva: **esperan resultados de Codex**.
- Mapa global con jerarquía visual: puede hacerse ya con criterio editorial declarado
  (Fase 25 no necesita el híbrido para distinguir zonas consolidadas de exploratorias),
  pero conviene sincronizarlo con DEC-05/06 para Costanera.

El detalle accionable, elemento por elemento, está en `MATRIZ_AJUSTES_FASE25.csv`
(misma carpeta).
