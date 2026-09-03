# Ronda 21 · Verificación de vigencia

**Fecha de consulta:** 10 de agosto de 2026  
**Corte del atlas:** 1 de agosto de 2026  
**Regla de cierre aplicada:** si no hay prueba pública suficiente, el establecimiento queda **EN DUDA**. «No localizado» nunca se traduce como «cerrado».

## Resultado ejecutivo

El universo se congeló y publicó antes de iniciar la búsqueda en `UNIVERSO_PREBUSQUEDA.md`: 9 «probablemente abierto», 7 «sin verificación individual», 3 «en conflicto entre dos fuentes» y 3 «dudoso». La suma reproduce los 22 estados declarados por el atlas, aunque el texto fuente presenta inconsistencias de rotulado que se conservaron como observaciones de integridad.

De esos 22 casos, **9 obtuvieron una pieza pública v2 fechada en 2026** que individualiza nombre y número de calle: Bárbaro, San Antonio, Alcanfor, Horta, Julia, Trescha, Fico, Han y El Cedrón. La formulación correcta es «actividad acreditada a la fecha de la fuente»; ninguno queda afirmado como abierto al corte sólo por eso. Los otros **13 quedan EN DUDA**. Este conteo es descriptivo sobre el universo congelado, no una estimación ni un ranking.

Las señales de agregadores y plataformas se mantuvieron en columnas separadas. No aportan ningún punto, nombre o identificador publicable para el atlas y no fueron usadas para declarar una apertura o un cierre.

## Los tres históricos

### Bar del Alvear Palace Hotel

El hallazgo principal es negativo y concluyente sobre el contenido del acto: la [Resolución 1225/2026 y su anexo](https://documentosboletinoficial.buenosaires.gob.ar/publico/PE-RES-MCGC-MCGC-1225-26-ANX.pdf) incorporan **«BAR DEL ALVEAR PALACE HOTEL, Av. Alvear 1891»** y no dicen si se trata de L'Orangerie, Lobby Bar, Alvear Roof Bar, Alvear Grill, Alvear Café o Alvear Sushi Bar. El antecedente de 2019 repite la denominación genérica. Por lo tanto, **el acto normativo no desambigua**.

El [sitio del hotel](https://alvearpalace.com/restaurantes-bares/lobby-bar/) atribuye la condición de Bar Notable al **Lobby Bar**. Es una corroboración fuerte y permite registrar «probable correspondencia con Lobby Bar», pero no se debe presentar como si el acto hubiera hecho esa identificación. Además, la página no tiene fecha editorial, por lo que no es v2 de vigencia.

### Petit Colón y El Coleccionista

Las fichas oficiales de turismo individualizan [Petit Colón](https://turismo.buenosaires.gob.ar/es/gastronomico/petit-col%C3%B3n?page=1) y [El Coleccionista](https://turismo.buenosaires.gob.ar/es/gastronomico/el-coleccionista?page=6), pero no tienen fecha editorial. Las señales recientes recuperadas son de plataformas y quedaron fuera de la evidencia publicable. Ambos permanecen **EN DUDA; sin señal de cierre, verificación pendiente**.

## Los nueve kosher de Flores

Se buscaron, uno por uno, American Kosher, Kosher City, Amltí/Amit, Azulay, Hamra, Behar Almacén, Soultani, Productos Cohen y Nacca por una ruta distinta de la prensa generalista: organismos de certificación, sitios comunitarios y prensa kosher.

La lista de Jabad Recoleta individualiza Amit y Azulay, y el archivo de Jabad individualiza Soultani, pero ninguna página aporta una fecha editorial que feche ese dato. El comunicado comunitario de 2023 sobre Hamra refiere a otras sedes y no se extrapoló a Aranguren 3192. Para los demás no apareció una lista fechada posterior al [registro oficial de 2015](https://turismo.buenosaires.gob.ar/sites/turismo/files/establecimientos_KOSHER_2015_0.pdf) que una nombre y altura.

**La ruta de certificadores y prensa comunitaria también cierra; queda declarada como puerta cerrada.** Esto describe la ruta de búsqueda, no el estado comercial de los nueve establecimientos. Los nueve quedan **EN DUDA**.

## Los dieciséis pedidos página por página

El detalle completo está en `PEDIDOS_16_PAGINAS.csv`. Se resolvieron documentalmente, a fecha de fuente, San Antonio, Mercado del Progreso, MN Santa Inés, Bárbaro, La Orquídea, Simona y Suculentas. En los bloques con varios nombres, el resultado es individual: no se trasladó la prueba de un local a sus vecinos.

Quedaron para recorrido o constatación directa los establecimientos que sólo devolvieron fichas sin fecha, plataformas o anuncios sin confirmación posterior. Los pedidos de Federico Lacroze y Monte Castro no son verificaciones de establecimiento: el primero requiere validación GIS del contorno y el segundo un recorrido territorial o conteo actualizado.

## Controles de integridad del universo

- El Puentecito aparece en la prosa del atlas como «probablemente abierto», pero queda fuera del conteo declarado de nueve. La búsqueda sólo encontró señal actual de plataforma; permanece EN DUDA.
- Cimino R, Donado 1919, tiene un antecedente periodístico de 2022 y listados sectoriales cuya fecha de dato no pudo acreditarse como 2026. No se lo suma al universo de 22 y permanece EN DUDA como fila de control.
- El Bohemio conserva una pieza v2 de diciembre de 2024, pero no una prueba 2026. La categoría «probablemente abierto» del atlas no se sostuvo como conclusión de esta ronda.

## Método y límites

- Fuentes públicas y gratuitas únicamente. No se usaron APIs pagas, llamadas, correos, credenciales ni fuentes internas o privadas.
- Cada resultado conserva su consulta exacta, URL y fecha en los CSV. «Sin fecha editorial verificable» se escribe literalmente cuando corresponde.
- Un catálogo patrimonial es v1: acredita pertenencia e identidad, no actividad.
- Una ficha oficial o propia sin fecha es v4: orienta, pero no fecha vigencia.
- Una pieza v2 acredita actividad a la fecha de la fuente, no al corte.
- Una marca de plataforma «cerrado» o «puede estar cerrado» no se publica como cierre.
- No se modificó el atlas ni ninguna fuente original. Esta ronda produce sólo documentos nuevos dentro de `ronda_21_codex`.

## Archivos de entrega

- `UNIVERSO_PREBUSQUEDA.md`: universo publicado antes de buscar.
- `RESULTADOS_22_ESTADOS.csv`: los 22 casos, con evidencia publicable y señal no publicable separadas.
- `HISTORICOS_TRES.csv`: Alvear, Petit Colón y El Coleccionista.
- `KOSHER_RUTA_NUEVA.csv`: nueve búsquedas de certificadores/comunidad.
- `PEDIDOS_16_PAGINAS.csv`: resolución página por página.
