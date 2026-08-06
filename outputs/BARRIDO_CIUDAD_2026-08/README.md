# Barrido de la Ciudad · agosto 2026

Etapa que sigue al cierre del Atlas V2. Objetivo: extender el relevamiento a los 48 barrios y
hacer comparables los métodos con que se contaron las 22 zonas publicadas.

> **El objetivo cambió el 5/8, y hacia arriba.** Ya no es extender un relevamiento: es construir
> una **base de la gastronomía de la Ciudad** apoyada en todas las bases que existen, para que se
> pueda trabajar mejor desde la Dirección y desde afuera. **El Atlas pasa a ser un producto
> derivado de esa base**, no algo paralelo. Y el entregable final sigue siendo el mapa de polos
> poligonizados de toda la Ciudad.
>
> Entrada para eso: **`README_BASE_GASTRONOMICA.md`** (cómo se usa la base y qué no hace) y
> **`ESQUEMA_BASE_GASTRONOMICA.md`** (el modelo de datos). El estado del día está en
> `docs/revisiones/HANDOFF_BASE_GASTRONOMICA_2026_08_05.md`.

Esta carpeta la escriben dos manos —la sesión de Cowork y la sesión del repositorio—, así que
lo primero es saber qué archivo manda. **Leé esta tabla antes de tomar cualquier número.**

---

## Qué manda

| archivo | rol | quién lo escribe |
|---|---|---|
| `generado/capa_homogenea_48_barrios.csv` | **vigente** | `scripts/barrido_ciudad/build_capa_homogenea.py` |
| `generado/capa_homogenea_22_zonas.csv` | **vigente** | idem |
| `generado/factor_captura_22_zonas.csv` | **vigente** | idem |
| `capa_homogenea_*.csv` y `factor_captura_*.csv` en la raíz | **referencia congelada** del 5/8, contra la que corre `--check`. No se actualizan. No se leen como dato. | Cowork, una sola vez |
| `insumos/cifras_publicadas_atlas_22.csv` | cifras del Atlas, declaradas. **No se recalculan.** | congelado |
| `insumos/` en general | entradas al cálculo | ambas |
| `generado/` en general | salidas derivadas, reproducibles | el generador |

Si la referencia congelada y lo vigente difieren, **no es un error automáticamente**: a partir
de las decisiones del 5/8 tienen que diferir. `--check` deja de ser un control de regresión el
día que se aplican; a partir de ahí el control es el propio `--check` contra una referencia
nueva, que hay que volver a congelar.

---

## Documentos de método

| archivo | qué fija |
|---|---|
| `METODO_COMPARABILIDAD_2026-08.md` | las cinco reglas de conteo y el factor de captura de las 22 zonas |
| `DISENO_CUATRO_FUENTES.md` | por qué son cuatro fuentes y qué aporta cada una |
| `FUENTES_NUEVAS_2026-08.md` | las fuentes verificadas, con URL |
| `SPEC_PLACES_BARRIDO.md` | tipos de Places, grilla, presupuesto de llamadas, guardarraíles |
| `CONTROLES_FUENTES_NUEVAS_2026-08.md` | los dos controles sobre el Relevamiento de Usos del Suelo |
| `crosswalk_zona_barrio.csv` | % de cada zona en cada barrio — para la mezcla de añadas |
| `grilla_places_48_barrios.csv` | celdas por barrio y universo estimado. **Intacto y con aviso**: se dimensionó para contar |
| `AVISO_GRILLA_48_BARRIOS.md` | por qué esa grilla ya no responde al criterio correcto, y cuál es el criterio nuevo |
| `generado/CRUCE_PLACES_PADRON_R08.txt` | qué trae Places que la base documental no tiene, en la zona mejor calibrada |
| `generado/UNIVERSO_POR_CAPTURA_17_ZONAS.txt` | el estimador padrón × Places puesto a prueba en 17 zonas — **falla, y queda cerrado** |
| `generado/PREPARACION_CAMPO_NUNEZ_LA_BOCA.md` | piso documental, perímetro tentativo y control de resultado para los dos barrios que se relevan a pie |
| `comparabilidad_atlas.html` | el tablero para mirar y mostrar |
| `DICCIONARIO_COLUMNAS.md` | **va con cualquier CSV que se entregue.** Lleva el aviso de que `habilitaciones` cuenta trámites y no oferta |
| `consulta_agc/` | la consulta técnica a la AGC y su anexo. **La manda Diego, no el repositorio** |

### La base y las fuentes abiertas (5/8, segunda mitad)

| archivo | qué fija |
|---|---|
| `ESQUEMA_BASE_GASTRONOMICA.md` | el modelo de datos: dos tablas, identificador, vigencia, aptitud geométrica y publicación |
| `README_BASE_GASTRONOMICA.md` | cómo se usa la base, qué no hace y **la advertencia de licencias** |
| `generado/BASE_GASTRONOMICA.txt` | el informe de la corrida: qué entró, cómo se agrupó y los ocho controles |
| `generado/base_48_barrios.csv` | el agregado versionable por barrio |
| `base_referencia_agregada.csv` | **referencia congelada** del `--check` de la base |
| `generado/OVERTURE_GASTRO_CIUDAD.txt` | Overture: 11.921 POI núcleo, 1,74× el padrón, redistribuible |
| `generado/OSM_GASTRO_CIUDAD.txt` | OSM: 6.427 POI núcleo, y su sesgo de cobertura medido por barrio |
| `generado/ATP_GASTRO_CIUDAD.txt` | All The Places: 282, sólo cadenas |
| `generado/CRUCE_FUENTES_ABIERTAS.txt` | **el número que decide el barrido**: Overture rescata el 90 % de lo que Places descubre |
| `generado/FUENTES_GCBA_NUEVAS.txt` | los seis datasets nuevos, con el aviso de que la ficha de CKAN no coincide con el archivo |
| `generado/BADATA_CATALOGO.txt` | el barrido de los 453 datasets del portal, ordenado por utilidad |
| `generado/COTEJO_22_ZONAS_BASE.txt` | las 22 zonas recalculadas desde la base, con las bandas escritas antes de correr |

El handoff operativo vive donde manda la convención del repo:
`docs/revisiones/HANDOFF_BARRIDO_CIUDAD_2026_08_05.md`.

---

## Las cinco reglas de conteo

Valen para toda fuente que entre a esta etapa. El detalle está en `METODO_COMPARABILIDAD`.

1. La unidad es la **dirección normalizada** (o la parcela), nunca la habilitación.
2. **Dos anillos de rubro**, núcleo y ampliado, y se informan los dos.
3. Las direcciones **anómalas se marcan, no se borran**. Umbral: más de 20 habilitaciones.
4. Asignación **por geometría**, no por el campo de texto.
5. La ventana **no registra bajas**. El número nunca es «locales abiertos hoy».

---

## Decisiones tomadas el 5/8

- **CERVECERIA y SUSHI al núcleo; CONFITERIA al ampliado.** Por simetría con el mapeo de
  habilitaciones, donde `confiteria` cae en Pastelería. Que ese mapeo sea discutible queda
  anotado: se corrige en las dos bases a la vez o en ninguna.
- **El oeste entra en esta tanda.** Ficha documental sin factor de captura, y añada declarada.
- **La base del control de captura son las habilitaciones**, no el Relevamiento. El
  Relevamiento es mejor fuente pero peor control: es rotativo, y 19 de las 22 zonas cruzan más
  de un barrio, así que casi toda zona mezcla 2022, 2023 y 2024.
- **El Relevamiento de Usos del Suelo es fuente primaria** del piso documental; el padrón de
  habilitaciones queda como segunda columna.

## Decisiones tomadas el 5/8 (segunda tanda)

- **Places: autorizado el control completo de las 17 zonas con cifra publicada**, no la versión
  reducida a cuatro. Con cuatro puntos no se separa señal de ruido; con 17 repartidos en las
  familias de método sale una curva de calibración.
- **Grilla adaptativa, no fija.** Se corre a 1 km y se vuelve a partir en 500 m cualquier celda
  que devuelva 50 resultados o más. Bajar la grilla a ciegas gasta de más donde no hace falta;
  no bajarla nunca pierde locales en silencio justo donde la estimación es menos confiable.
  Cuántas celdas hubo que repartir **se informa aparte**: dice dónde el factor de captura
  estimado se queda corto.
- **La consulta a la AGC va**, como consulta técnica y no como hallazgo, con partida y dirección
  solamente.
- **El hallazgo de los lotes quedó probado contra el catastro** (`generado/PRUEBA_SMP_LOTES.txt`).

## Decisiones tomadas el 5/8 (tercera tanda · después de correr Places)

- **El frente de Places se cierra.** Recupera del orden del 12 % de una cifra contada a pie y es
  techo estructural, no de esa barrida: una corrida entera de la misma consulta agregó un solo
  local (N̂ ≈ 77 sobre 646). No sustituye al campo y no se insiste.
- **Núñez y La Boca se relevan a pie**, al nivel de Caballito y Villa Crespo. No salen como fichas
  documentales. Su paquete de preparación —piso, perímetro tentativo, control de resultado— está
  en `generado/PREPARACION_CAMPO_NUNEZ_LA_BOCA.md`.
- **Las 20 fichas documentales del oeste y del sur salen**, con la salvedad y la añada declaradas.
- **El aporte de Places es descubrimiento, no vigencia.** Corrige la formulación anterior: confirma
  abiertas 26 de las 233 direcciones núcleo del padrón en Villa Crespo (11,2 %), demasiado poco
  para sostener una tabla de vigencia; en cambio la mayor parte de lo que trae son direcciones que
  el padrón no tiene, en 11 de las 14 zonas con muestra suficiente.

## Decisiones tomadas el 5/8 (cuarta tanda · las fuentes abiertas y la base)

- **El objetivo de la etapa es la base**, y el Atlas se deriva de ella. Ver el aviso de arriba.
- **Entraron tres fuentes de POI abiertas y redistribuibles**: Overture Maps, OpenStreetMap y All
  The Places. Overture es la primera fuente que supera al padrón (1,74×) y viene con nombre y
  dirección publicables.
- **Foursquare queda afuera**, no por decisión sino porque cerró el acceso anónimo. Cuesta poco:
  aporta el 3,3 % de Overture y ya viaja adentro.
- **La columna vertebral dejó de ser Places, y está medido.** Overture sola empareja 73 de los 81
  puntos que Places trajo de Villa Crespo; sólo 4 quedarían sin identidad publicable.
- **La base no se corre con Places hasta haber cargado todo lo abierto** y dimensionado qué agrega.

## Abierto

- El mapeo `confiteria → Pastelería`, pendiente de criterio de la Dirección.
- **Correr o no una primera tanda de Places, y de qué tamaño.** La recomendación cambió con la
  medición del rescate y está en `HANDOFF_BASE_GASTRONOMICA_2026_08_05.md`.
- **La cláusula de compartir-igual de la ODbL de OSM**, que tiene que revisar el área legal antes
  de publicar cualquier capa abierta. Está detallada en `README_BASE_GASTRONOMICA.md`.
- La vigencia **sigue sin fuente completa**, pero ya no es un agujero entero: los permisos de
  espacio público aportan **fecha de vencimiento**, que es la única afirmación con fecha por
  delante de todo el conjunto. Alcanza a 332 locales de la base.
- «Cómo se construyeron las zonas», del Atlas, sigue pendiente de confirmación de la Dirección.
- Regenerar o no los PDF del Atlas con la reescritura editorial ya aplicada al generador.

---

## Antes de tocar nada

Rigen `AGENTS.md` y la política de `docs/infraestructura_agentes_skills_v1_1/`. En particular:
no se commitea sin pedido explícito, no se usa `git add .`, y no se tocan `data/`, `src/`,
`dashboard/` ni las superficies protegidas de `docs/polos_gastro/PROTECTED_SURFACES.yaml`.
Las descargas crudas de fuentes externas están fuera de Git (`.gitignore`, línea 123).
