# Atlas de Referencias Gastronómicas de la Ciudad de Buenos Aires · control de tablas y vigencia

Estado: **entrega técnica reproducible, con salvedades explícitas**. Fecha de corte: **10/08/2026**.

## Qué cambió de valor

- Cinco conteos quedaron derivados de sus seis columnas: R02 **3 → 4**, R04 **3 → 4**, R05 **4 → 5**, R19 **3 → 4** y Z37 **6 → 5**. Las cinco filas conservan la categoría `polo admitido`; el control se ejecutó el 10/08/2026 sobre el corpus y el criterio de admisión archivados.
- Los diez casos sin cruce quedaron cerrados: **3 abren y 7 no abren** por la vía E. La fila del barrio Flores abre por medición propia del barrio, no por herencia desde una parte. Fuentes: capa oficial pública de barrios y domicilios del Directorio de Unidades Económicas, procesados el 10/08/2026; corpus de prensa pública con corte 07/08/2026.
- El catálogo consolidado reconcilia **90 entradas: 86 abiertas, 1 abierta en quiebra, 1 en riesgo y 2 cerradas**; son 88 que el catálogo trata como operativas y dos cierres con evidencia positiva. Fuente: catálogo consolidado del 03/08/2026 y auditoría pública cerrada el 08/08/2026.
- **Plaza Bar**, Florida 1005, continúa en el catálogo oficial vigente aunque cerró el **29/04/2017**. La reapertura está anunciada para 2028, por lo que corresponde `cerrado con reapertura anunciada`, no extinción. Fuentes: Clarín/Viva, 15/02/2025; Tango y Milonga, 02/01/2025; catálogo oficial consolidado, 03/08/2026.
- La alerta de **El Puentecito** no acreditaba un cierre: la pieza perdida era Los Laureles. El resultado prudente es `probablemente_abierto`, nivel v2, no `verificado_abierto`. Fuente principal: La Nación, 07/07/2026; corroboraciones: reseña pública de servicio del 04/05/2026 y ficha oficial editada el 20/02/2026.

## 1. Correspondencia entre 124 concentraciones y 41 polos

La ejecución sobre los soportes vigentes produjo **143 intersecciones materiales: 95 publicables y 48 en espera de borde**. Otras 29 concentraciones no tienen una intersección material con los soportes disponibles. Cada fila declara `TRAZADO` o `PROVISORIO_DE_BARRIO`; estas últimas llevan `atribuible=NO`. Fuente: capas locales derivadas de datos públicos, ejecución del 10/08/2026.

El umbral está publicado: se exige una intersección mayor a **0,01 m²**. No hay tope de filas ni truncamiento. En esta ejecución hubo **cero contactos excluidos por el umbral**; aun así se genera una tabla separada con encabezado estable para que cualquier exclusión futura quede enumerada. El programa acepta una nueva capa mediante `--soportes`, exige 41 identificadores únicos y falla si no puede distinguir bordes trazados de provisorios.

La capa nueva de perímetros todavía no fue adoptada en esta ejecución. Por eso estos conteos describen la geometría vigente anterior y deben regenerarse con el mismo comando cuando el archivo nuevo quede cerrado.

## 2. Arreglos de consistencia

### Conteo de vías

`n_vias` se recalcula únicamente desde `via_A` a `via_F`. Ninguna de las cinco correcciones atraviesa el umbral de tres vías y los otros criterios no se editaron; el programa se detiene si detecta un cambio de categoría. Fuente: corpus y criterio de admisión, consulta local del 10/08/2026.

### Ancho de CSV

La fila R03 se volvió a serializar con comillas mediante un escritor CSV. Sus campos `via_E_advertencia`, `via_E_rutas_n` y `fecha_relevamiento` permanecen separados. El control previo encontró **72 archivos y cero filas con ancho divergente** en el directorio de evidencia; el test automatizado repite el chequeo sobre todas las tablas de esa carpeta y sobre esta entrega. Fecha del control: 10/08/2026.

### Normalización de calles

Se corrigieron exactamente nueve concentraciones: **dos** por altura fuera de rango, **cuatro** por una calle registrada con dos nombres y **tres** por abreviaturas no contempladas. En todos los casos se conserva la suma de ocurrencias y se documentan el valor anterior, el canónico y el caso de prueba. Fuente: tabla de 124 concentraciones, procesada el 10/08/2026.

El control canónico de Café Olimpo resuelve primero calle y altura: **Irigoyen 1491 → Monte Castro, Comuna 10**. No se hereda el barrio asignado a otro tramo de la misma calle. Resultado del test: `OK`, 10/08/2026.

## 3. Diez cruces pendientes

Los diez registros indican la pregunta territorial, la fuente pública, el sector resultante y el veredicto. No se usaron habilitaciones por parcela: se declaran **puerta cerrada** por no ser públicas. El sustituto combina la capa oficial pública de barrios con domicilios públicos y ejes dominantes, y luego aplica el reconocimiento público ya fechado al 07/08/2026.

Resultados que abren: Flores como medición propia de barrio, P014 en Flores sur y P085 en Congreso. Resultados que no abren: P107 y P055 en Once; P061, P059, P058, P060 y P036 en el casco de Flores. Ninguno queda pendiente. La tabla conserva la justificación individual y evita atribuir al barrio entero el resultado de una única subzona.

## 4. Vigencia de 90 establecimientos históricos

La escala publicada en esta entrega queda así:

- `v0`: constatación en el lugar, fecha cero y baja auditabilidad; sólo es admisible junto con búsqueda de evidencia negativa.
- `v1`: mención o consulta sin pieza individual fechada; no acredita apertura.
- `v2`: hecho fechado de una fuente secundaria; acredita el hecho descripto, no necesariamente atención actual.
- `v3`: evidencia pública fechada de servicio real, ficha oficial editada activamente o participación operativa fechada.

No se asignó v0 porque las fuentes archivadas no documentan una constatación presencial susceptible de aplicar esa regla. La distribución es **61 v1, 14 v2 y 15 v3**. Hay **10 verificaciones con más de 90 días** y **66 acciones de revisión** al sumar evidencia vencida y registros v1 sin pieza individual auditable. Fuente: capa consolidada y auditoría pública con corte 08/08/2026; antigüedad calculada al 10/08/2026.

El Buzón adopta **Esquiú 1393**, dirección del catálogo consolidado, y conserva como alternativas declaradas **Esquiú y Centenera** y **Esquiú y Tabaré**. Fuente: tres registros oficiales reconciliados el 08/08/2026.

Los cierres quedan separados de las interrupciones recuperadas. `cerrados.csv` contiene Plaza Bar y La Buena Medida. `interrumpidos_recuperados.csv` contiene El Obrero: interrupción de ocho meses durante la pandemia, reapertura en 2021 y evidencia pública de actividad archivada el 07/08/2026. Un cierre temporal no se leyó como extinción.

El estado abierto de un agregador no se utilizó como verificación. No se exportaron puntos, nombres vinculados a consultas, identificadores ni estados individuales de plataformas.

## 5. El Puentecito

La Nación lo describió en funcionamiento en Vieytes 1895 el **07/07/2026**, dentro de su selección de 16 restaurantes icónicos. Una reseña pública del **04/05/2026** describe servicio real, pero queda cinco días fuera de la ventana de 90 días. La ficha oficial fue modificada el **20/02/2026**, aunque una edición reciente no equivale por sí sola a una visita.

La conclusión publicable es: **no hay evidencia pública archivada que sostenga el cierre y hay evidencia secundaria reciente compatible con actividad; probablemente abierto, v2**. No se afirma `verificado_abierto`. La frase que originó la alerta estaba mal atribuida y se refería a Los Laureles.

## Pendientes y límites finales

- Falta ejecutar la correspondencia con la nueva capa de perímetros cuando quede disponible; la presente salida usa los soportes vigentes anteriores.
- No hubo consulta web en vivo porque el conector de investigación no estuvo disponible. Se trabajó sólo con evidencia pública ya archivada; por eso El Puentecito no se eleva por encima de `probablemente_abierto`.
- Sesenta y tres entradas de nivel v1 requieren una pieza individual fechada antes de citarse como vigencia. Diez registros superan 90 días y están marcados para revisión.
- La fuente de habilitaciones por parcela permanece cerrada por no ser pública. Ninguna conclusión depende de ella.

Las fuentes originales, la geometría en elaboración y el pipeline general no fueron modificados. Todas las salidas se generaron sin contactos, correos, identificadores de plataforma ni claves.
