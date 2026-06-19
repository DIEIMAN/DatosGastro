# DataGastro — Informe de análisis

> **Prototipo de base analítica del ecosistema gastronómico de la Ciudad de Buenos Aires**
> Informe de análisis · Junio de 2026
>
> Construido sobre datos abiertos del Gobierno de la Ciudad de Buenos Aires (GCBA) y relevamientos trazables.
> Cada número informa su fuente, su fecha y sus límites.

Este archivo es la **versión editable en texto** del informe. La pieza que se genera y distribuye es el PDF, producido por el script `scripts/generar_informe_pdf.py` (ReportLab). Si se edita este texto, hay que reflejar los cambios en el script para que el PDF quede sincronizado. Las cifras provienen de los outputs del proyecto (`data/analytics/` y `data/processed/`); no se inventan ni se recalculan.

---

## Resumen ejecutivo

DataGastro es un prototipo de base analítica que integra, en un único modelo ordenado y trazable, la información pública dispersa sobre el sector gastronómico de la Ciudad de Buenos Aires. Reúne cinco registros oficiales y relevamientos propios, y los mantiene separados porque cada uno mide una dimensión distinta del mismo fenómeno.

**Hallazgos principales**

- **El sector formal está documentado a gran escala:** 2.823 locales en la guía oficial de oferta y 44.169 habilitaciones gastronómicas aprobadas integradas en la base, con serie comparable 2019–2024 y períodos no comparables (2015–2018 y 2025) identificados por separado.
- **Por primera vez se puede observar, calle por calle, dónde se aprueba actividad gastronómica formal:** el 97% de las habilitaciones (42.741) fue ubicado en el mapa con el sistema de geolocalización oficial del Gobierno de la Ciudad, con una tasa exacta de geocodificación cercana al 99% y un control de consistencia territorial por comuna.
- **Volumen y concentración no coinciden:** si se mide densidad de oferta registrada, San Nicolás y el centro histórico aparecen como el núcleo de mayor intensidad territorial, mientras Palermo lidera en cantidad absoluta. Esta lectura surge de la oferta registrada, no de locales activos.
- **La Ciudad gestiona 259 espacios públicos de abastecimiento:** 6 mercados, 69 ferias y 184 puntos de ferias itinerantes de abastecimiento barrial, distribuidos territorialmente en las comunas de la Ciudad.
- **Todo el trabajo es trazable y validado:** cada número informa su fuente, su fecha y sus límites; el proceso pasa 62 controles de calidad automáticos sin errores y 22 tests automáticos ejecutados correctamente.

> **Lectura.** La fortaleza del prototipo es metodológica: no inventa un número único del sector, sino que ordena la evidencia disponible y deja explícito qué se puede afirmar y qué no. Eso lo hace confiable como insumo de gestión.

---

## 1. Qué es DataGastro y para qué sirve

La Ciudad tiene un sector gastronómico muy activo, pero la información sobre ese sector vive dispersa en registros que nunca se habían integrado: una guía de oferta, un registro de habilitaciones, padrones de ferias y mercados, noticias de eventos, documentos de programas. Cada uno describe algo diferente.

DataGastro es un prototipo construido para resolver ese problema. No para producir un número único que sume todo, sino para:

- Integrar las fuentes disponibles en un modelo de datos único, reproducible y trazable.
- Separar correctamente los universos, de manera que cada cifra tenga una definición clara y defendible.
- Convertir la información en insumos útiles para conversación pública, planificación territorial y diseño de políticas.
- Dejar en claro qué se sabe, qué no se sabe y con qué fuente se sostiene cada afirmación.

**Preguntas que guiaron el trabajo**

1. ¿Dónde se concentra la oferta gastronómica registrada?
2. ¿Qué tipos de gastronomía predominan?
3. ¿Cómo evolucionó la actividad formal año a año?
4. ¿Dónde, en términos de calles y barrios, se aprueba actividad gastronómica formal?
5. ¿Qué espacios públicos de abastecimiento existen y cómo se distribuyen?
6. ¿Qué eventos y programas impulsa la Ciudad?
7. ¿Hay diferencia entre dónde hay muchos locales y dónde están más concentrados?
8. ¿Qué no se puede responder con estos datos y por qué?

---

## 2. Las cinco fuentes: qué mide cada una

El principal riesgo al trabajar con estos datos es mezclar universos y comunicar conclusiones que los datos no sostienen. El ejemplo más común sería sumar la oferta registrada con las habilitaciones aprobadas y hablar de "X establecimientos gastronómicos": ese número no existe, porque cada fuente describe algo distinto.

| Fuente | Organismo de origen | Qué mide | Qué NO dice |
|---|---|---|---|
| Oferta gastronómica registrada (F01) | Ente de Turismo del GCBA | Establecimientos publicados en la guía oficial de gastronomía | No confirma si cada local sigue abierto hoy |
| Habilitaciones aprobadas (F02) | Agencia Gubernamental de Control (AGC) | Trámites de habilitación aprobados por rubro gastronómico (recursos 2015–2025) | No son locales activos ni registran cierres |
| Ferias, mercados y FIAB (F03) | Dirección General de Ferias del GCBA | Espacios reales de abastecimiento público | No cuenta puestos ni personas, solo espacios |
| Eventos relevados (F04) | Relevamiento propio con fuente por fila | Inventario trazable de eventos del sector | No es el universo completo de eventos |
| Programas y políticas (F05) | Relevamiento propio con fuente por fila | Catálogo institucional de programas vigentes | No mide impacto, empleo ni presupuesto |

**Una aclaración técnica importante.** La cifra de habilitaciones surgió de un trabajo de depuración cuidadoso. Una primera versión del clasificador inflaba el total a 87.934 porque asignaba rubros gastronómicos a actividades como talabartería o venta de productos envasados, que contienen palabras parecidas pero no son gastronomía de servicio. El clasificador definitivo, por coincidencia exacta de términos, llega a 44.169 habilitaciones genuinamente gastronómicas, integradas desde los recursos anuales de la Agencia Gubernamental de Control.

---

## 3. Los números principales, separados

*Datos: resumen analítico del proyecto sobre los registros oficiales del GCBA.*

*(Figura: `outputs/informe/figures/01_kpis.png` — barras horizontales de los cinco indicadores.)*

> **Lectura.** Las habilitaciones tienen un volumen mucho mayor porque acumulan trámites desde 2015. La oferta registrada es una guía estática. Los espacios públicos son pocos pero geográficamente relevantes. Eventos y programas son catálogos documentados, no estadísticas. Por eso ninguno se suma con otro.

---

## 4. El mapa del ecosistema

Las coordenadas de la oferta registrada y de los espacios públicos vienen directamente de las fuentes oficiales. Las de las habilitaciones se obtuvieron con el sistema de geolocalización del Gobierno de la Ciudad. Solo se muestran puntos con ubicación validada.

*(Figura: `outputs/informe/figures/02_mapa.png` — izquierda: oferta registrada y espacios públicos; derecha: sumando las habilitaciones aprobadas geolocalizadas.)*

> **Lectura.** La actividad se concentra con fuerza en el corredor norte (Palermo, Recoleta, Belgrano) y el centro histórico (San Nicolás, Monserrat, San Telmo), y se afina hacia el sur. La capa de habilitaciones geolocalizadas es la única que permite observar, calle por calle, dónde se aprueba actividad formal. Son habilitaciones aprobadas, no locales activos.

---

## 5. ¿Dónde se concentra? Volumen frente a densidad

Hay un matiz que cambia la lectura sobre dónde está el núcleo de mayor intensidad. En cantidad absoluta, Palermo lidera; pero Palermo es muy extenso. Si se mide la densidad —locales por kilómetro cuadrado— San Nicolás y el centro histórico aparecen como las zonas de mayor concentración. Esta lectura corresponde a la oferta registrada, no a locales activos.

*(Figura: `outputs/informe/figures/03_densidad.png` — la misma fuente en cantidad absoluta y en densidad por km².)*

> **Lectura.** Palermo lidera en volumen, pero por su tamaño la oferta queda diluida. Si se mide densidad de oferta registrada, San Nicolás y el centro histórico aparecen como el núcleo de mayor intensidad territorial. La diferencia tiene implicancias concretas para uso del suelo, gestión del tránsito y evaluación de permisos de espacio público.

---

## 6. ¿Cuánto se habilita por año?

*Datos: Agencia Gubernamental de Control (AGC), registros publicados en datos abiertos.*

Una habilitación aprobada es la autorización formal para operar un rubro en un domicilio: marca dónde el sector formal está invirtiendo. El gráfico muestra solo los años comparables entre sí (2019–2024).

*(Figura: `outputs/informe/figures/04_serie.png` — habilitaciones aprobadas por año, serie comparable.)*

> **Lectura.** La serie comparable permite observar la dinámica anual del sector formal, con el impacto visible de la pandemia en 2020 y la recuperación posterior. Los períodos 2015–2018 (consolidado en un solo archivo) y 2025 (esquema distinto, con disposiciones de varios años) se informan por separado para no falsear la comparación, y por eso no se incluyen en este gráfico.

---

## 7. ¿Qué tipo de gastronomía se habilita?

*Datos: Agencia Gubernamental de Control (AGC); categoría inferida del rubro declarado.*

*(Figura: `outputs/informe/figures/05_categorias.png` — habilitaciones por tipo de gastronomía.)*

> **Lectura.** La distribución por categoría muestra qué rubros concentran la mayor actividad formal sobre el total integrado de la base. La venta de alimentos sin servicio de mesa se separó del conteo gastronómico porque no representa el mismo tipo de actividad.

---

## 8. Los espacios públicos de la Ciudad

*Datos: Dirección General de Ferias del GCBA y archivo oficial georreferenciado de ferias itinerantes.*

Este es el componente público y territorial del ecosistema: los espacios que la Ciudad gestiona directamente para la comercialización de alimentos. Se cuentan espacios reales (la feria como unidad), no los puestos individuales.

*(Figura: `outputs/informe/figures/06_espacios.png` — espacios públicos de abastecimiento por tipo.)*

> **Lectura.** Los 259 espacios se reparten en mercados municipales (permanentes), ferias especializadas y 184 puntos de ferias itinerantes de abastecimiento barrial, que rotan por los barrios con productos frescos y básicos. Es la red de abastecimiento de proximidad de la Ciudad, presente en las 15 comunas y distribuida de forma más equilibrada que la oferta privada.

---

## 9. Eventos y programas que impulsa la Ciudad

*Datos: relevamiento propio sobre comunicaciones oficiales del GCBA y normativa, con fuente por registro.*

La dimensión institucional del ecosistema: las acciones que el Gobierno de la Ciudad impulsa para el sector. Se documentaron 13 eventos verificados (festivales, ciclos de mercado, concursos, jornadas de descuentos) y 4 programas vigentes:

- **BA Capital Gastronómica** — programa marco de promoción del sector.
- **Distrito del Vino** — incentivos territoriales en la Comuna 11.
- **Bares Notables** — protección patrimonial de establecimientos históricos.
- **Permisos de área gastronómica** — régimen de mesas y sillas en la vía pública.

Sobre el régimen de permisos de área gastronómica: está identificado en el catálogo de programas, pero su dataset operativo (los permisos efectivamente otorgados y vigentes) todavía no está integrado como fuente analítica del proyecto. Su incorporación figura en la hoja de ruta.

> **Lectura.** La Ciudad tiene una agenda gastronómica activa y diversa. Este es un inventario documentado y trazable —cada registro tiene su fuente anotada— pero no un universo estadísticamente completo.

---

## 10. Qué responde el análisis

- **¿Dónde se concentra la oferta registrada?** En el corredor norte (Palermo, Recoleta, Belgrano) y el centro histórico (San Nicolás, Monserrat, San Telmo). Palermo tiene el mayor número absoluto.
- **¿Qué tipos de gastronomía predominan?** Restaurantes, bares y confiterías, y locales de comida rápida concentran el grueso de las habilitaciones.
- **¿Cómo evolucionó la actividad formal?** La serie comparable 2019–2024 muestra la dinámica anual, con la caída de 2020 por la pandemia y la recuperación posterior. Los períodos 2015–2018 y 2025 se informan aparte por no ser comparables.
- **¿Dónde se aprueba actividad formal, calle por calle?** El 97% de las habilitaciones fue geolocalizado con el sistema oficial del GCBA, con tasa exacta cercana al 99% y consistencia territorial por comuna. Las comunas del centro y el corredor norte concentran la mayor densidad.
- **¿Qué espacios públicos existen y cómo se distribuyen?** 259 espacios: 6 mercados, 69 ferias y 184 puntos de abastecimiento barrial, distribuidos territorialmente en las 15 comunas con criterio de proximidad.
- **¿Qué impulsa la Ciudad en el sector?** 13 eventos verificados y 4 programas vigentes de promoción, incentivos territoriales, patrimonio y uso del espacio público.
- **¿Hay diferencia entre cantidad y concentración?** Sí. Si se mide densidad de oferta registrada, San Nicolás y el centro histórico aparecen como el núcleo de mayor intensidad territorial, mientras Palermo lidera en cantidad absoluta.

**¿Qué NO se puede responder todavía, y por qué?**

- Cuántos locales están **activos hoy**: no existe un padrón con bajas actualizado.
- Cuántos **abrieron o cerraron** en términos netos: las habilitaciones no registran bajas.
- El **impacto económico** del sector: empleo, ventas o facturación.
- Si un barrio está **saturado o subatendido**: falta un denominador de demanda.
- El **impacto de eventos o programas**: no hay métricas de resultado publicadas.

> **Lectura.** Esta honestidad sobre los límites es lo que hace confiable la base: cada afirmación está respaldada, y las que no tienen respaldo no se hacen.

---

## 11. Qué falta y cómo se podría mejorar

Un prototipo honesto también deja en claro qué no puede responder todavía y cómo avanzar.

| Brecha | Por qué importa | Acción posible |
|---|---|---|
| Sin padrón de locales activos | No se sabe cuántos establecimientos siguen abiertos | Incorporar el dataset operativo de permisos de área gastronómica (mesas y sillas): un permiso vigente puede funcionar como señal parcial de actividad actual en calle |
| Las habilitaciones no registran cierres | No representan aperturas netas del sector | Solicitar el registro de bajas a la AGC |
| Sin datos de empleo o facturación | No se puede medir impacto económico | Ministerio de Trabajo, AFIP, encuestas sectoriales |
| Agenda de eventos sin estructura | El inventario de eventos es parcial | Colaboración con Turismo y Cultura para un dataset actualizable |
| Sin denominador de demanda | No se puede saber si un barrio está saturado | Flujo peatonal, turismo y población por zona |

**Próximos pasos en orden de prioridad**

- **Incorporar el dataset operativo de permisos de área gastronómica** como señal parcial de actividad en calle: cubre la brecha más importante, la ausencia de un padrón de locales activos. No todos los locales tienen permiso de mesas y sillas, por lo que no sería un padrón completo, sino una señal parcial.
- **Profundizar el análisis territorial** con herramientas de análisis de redes sobre los puntos geolocalizados, para detectar polos y corredores. Sería un módulo exploratorio, no un indicador oficial.
- **Mantener la base actualizada** reejecutando el proceso cuando las fuentes publiquen nuevos datos.

**Estado actual del trabajo.** El prototipo tiene hoy un proceso de datos completo y validado, de extremo a extremo: integración de fuentes, limpieza, normalización, geolocalización y controles de calidad. Pasa 62 controles de calidad automáticos sin errores ni advertencias y 22 tests automáticos ejecutados correctamente, e incluye una herramienta interactiva de exploración además de este informe. El proceso es reproducible: cuando las fuentes se actualicen, la base se reconstruye con la misma metodología.

---

*DataGastro · Datos abiertos del Gobierno de la Ciudad de Buenos Aires y relevamientos trazables. Cada número informa su fuente, su fecha y sus límites.*
