# Revisión crítica de los cinco prototipos híbridos

Estado: EXPERIMENTAL / NO OFICIAL. Fecha de corte: 2026-07-10.
Insumo: `outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/` y
`docs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/` (paquete
`REVISION_PROTOTIPOS_HIBRIDOS_V1.zip`). Todos los números citados fueron verificados
directamente contra los CSV, GeoJSON y mapas del experimento; no se aceptó ningún
resumen previo sin contraste.

Ninguna geometría de este documento constituye delimitación institucional. Las fuentes
miden oferta registrada (F01/F02) y oferta visible en Google Places (fuente externa
auxiliar); en ningún caso "locales activos".

## 0. Verificación de resúmenes previos: matices detectados

La lectura directa de los archivos confirma el veredicto general
(`PIPELINE_HIBRIDO_POR_TIPO_TERRITORIAL`, recomendación `ESCALAR_CON_AJUSTES`) pero
obliga a precisar varios puntos que los resúmenes comprimen de más:

1. **El "corredor único" de Corrientes son 5 componentes geométricos**, no un trazo
   continuo: 31 segmentos de soporte disueltos en 5 piezas, 3.444 m acumulados
   (`corrientes_eje_candidato.geojson`, `metadata_pipeline_hibrido_v1.json`).
2. **El corredor de Corrientes cubre 375 de 1.255 puntos del universo de la macrozona
   (29,9 %)** (`mezcla_fuentes_representaciones_v1.csv`). Reemplaza a los 23 tiles como
   representación, pero no representa a la macrozona completa.
3. **El "núcleo único" de San Telmo depende del consenso**: KDE con umbral relativo 0,5 y
   bandwidth 80/100 produce 2 componentes (`san_telmo_comparacion_metodos.csv`); el
   consenso KDE∩HDBSCAN estable lo reduce a 1. La pregunta "uno o dos núcleos" tiene
   base empírica real, no es solo editorial.
4. **Belgrano retiene 6 de 28 comunidades**: a umbral 80 m el grafo produce 28
   comunidades con 17,9 % de ruido (`belgrano_comparacion_comunidades.csv`); los 6
   núcleos publicados son las comunidades que superan el filtro de tamaño. Además hay
   una discrepancia menor de conteo entre `mezcla_fuentes_representaciones_v1.csv`
   (BEL_N03=18, BEL_N05=36) y `belgrano_nucleos_candidatos.geojson` (17 y 35): dos
   puntos de diferencia en total, a corregir en la repetición (conteo por membresía de
   comunidad vs. conteo por contención en el hull).
5. **La robustez media esconde colas**: San Telmo promedia 0,57 pero el percentil 10 del
   ARI por bloques es negativo (−0,032 a 200 m; −0,031 a 300 m): en el peor decil de
   repeticiones la partición no se parece en nada a la base
   (`robustez_bootstrap_bloques_v1.csv`). Puerto Madero es la única zona con colas
   sanas (p10 = 0,81/0,83).
6. **El contenedor de Belgrano es una unión de corredores de 250 m** sobre Juramento,
   Libertador y Cabildo, y su propia ficha registra 53 entidades conocidas que quedan
   fuera de toda macrozona (`macrozonas_editoriales_candidatas_v1.geojson`,
   observaciones de MZ_BELGRANO). Esto es evidencia directa de que el contenedor puede
   estar cortando la estructura multinuclear.
7. **La sensibilidad epsilon quedó sin evaluar en varias zonas** por un `TypeError`
   reproducible de scikit-learn 1.9 con `cluster_selection_epsilon` positivo; los
   fallback quedaron registrados y no se imputó estabilidad
   (`metricas_estabilidad_desagregadas_v1.csv`, `FE_DE_ERRATAS_AUDITORIA_GPT56.md`).

## 1. Cuatro cosas que no deben confundirse

Toda la lectura siguiente separa explícitamente:

- **Robustez de una estructura**: qué tan parecida vuelve a salir la partición al
  perturbar los datos (ARI por bloques, perturbaciones locales).
- **Cobertura de esa estructura**: qué fracción de la evidencia queda dentro de la
  representación. Una estructura puede ser muy robusta y cubrir poco (Puerto Madero).
- **Validez institucional**: si la representación puede afirmarse ante terceros con las
  fuentes disponibles. Depende de la mezcla F01/F02 vs. Places, no de la geometría.
- **Legibilidad visual**: si el mapa se entiende. Mejorar la legibilidad (menos piezas)
  no agrega evidencia.

## 2. San Telmo — núcleo compacto

| Dimensión | Valor verificado | Fuente |
| --- | --- | --- |
| Universo | 320 puntos; 46,6 % Places | `robustez_ablacion_fuentes_v1.csv` |
| Representación | 1 núcleo (ST_N01), 177 puntos | `san_telmo_nucleo_candidato.geojson` |
| Cobertura | 177/320 = 55,3 % del universo | ídem |
| Places dentro | 70/177 = 39,6 % | `mezcla_fuentes_representaciones_v1.csv` |
| Estabilidad local | MEDIA (0,776); membresía media del núcleo 0,92 | `metricas_estabilidad_desagregadas_v1.csv`; geojson |
| Robustez bloques | 0,57 (0,633 @200 m; 0,499 @300 m); **p10 negativo** | `robustez_bootstrap_bloques_v1.csv` |
| Sensibilidad global | mínima 0,652 (eom=leaf: 1,0) | `metricas_estabilidad_desagregadas_v1.csv` |
| Borde | 21,9 % de puntos a ≤100 m del borde | `robustez_bordes_v1.csv` |

- **Qué demuestra:** que existe un núcleo compacto de consenso (KDE bw 80/100/140,
  umbral 0,5, restringido a soporte HDBSCAN estable) que concentra el 55 % de la
  evidencia con mezcla de fuentes más sana que el promedio de la zona (39,6 % Places
  dentro vs. 46,6 % en el universo), y que 8 polígonos previos eran fragmentación
  artificial.
- **Qué no demuestra:** que el núcleo sea único (KDE a umbral 0,5 con bw 80/100 da 2
  componentes); que el borde exacto del hull signifique algo (concave hull ratio 0,4 +
  buffer 35 m son convenciones de dibujo); la relación con el eje Defensa (no se
  construyó soporte vial en esta zona); qué son los 143 puntos restantes.
- **Dependencia de Places:** media (46,6 % del universo); el núcleo la baja a 39,6 %.
- **Dependencia del contenedor:** baja-media (21,9 % de puntos cerca del borde; el
  contenedor reducido sube el número de clusters de 8 a 10).
- **Mejora principal frente a KMeans:** elimina la partición en 8 polígonos sin
  significado; una unidad respaldada por densidad en lugar de tiles.
- **Riesgo de falsa precisión:** MEDIO. El contorno dibujado invita a leerlo como
  límite; el p10 negativo del bootstrap indica que la partición fina no es estable,
  aunque el núcleo central sí (membresía 0,92).
- **Decisión técnica posible ya:** adoptar el patrón "núcleo de consenso HDBSCAN+KDE"
  como generador de candidatos para zonas tipo núcleo compacto.
- **Decisión humana pendiente:** uno o dos núcleos; papel del eje Defensa (DH-01).
- **¿Puede escalarse ahora?** El patrón sí (con los gates de la matriz de escalado); la
  versión final de San Telmo espera la decisión DH-01.

## 3. Corrientes — corredor lineal

| Dimensión | Valor verificado | Fuente |
| --- | --- | --- |
| Universo | 1.255 puntos; 39,9 % Places | `robustez_ablacion_fuentes_v1.csv` |
| Representación | eje `CORRIENTES AV.`: 31 segmentos → 5 componentes, 3.444 m; buffer 60/90/120 m | geojson eje/buffer; metadata |
| Cobertura | 375/1.255 = 29,9 % del universo | `mezcla_fuentes_representaciones_v1.csv` |
| Places dentro | 149/375 = 39,7 % | ídem |
| Estabilidad local | ALTA (0,930) | `metricas_estabilidad_desagregadas_v1.csv` |
| Robustez bloques | 0,65 (0,678 @200 m; 0,628 @300 m); p10 0,38/0,23 | `robustez_bootstrap_bloques_v1.csv` |
| Sensibilidad global | ALTA (leaf/eom 0,572) | `metricas_estabilidad_desagregadas_v1.csv` |
| Perfil longitudinal | 22 bins de 200 m, 0 huecos; densidad 105–525 pts/km | `corrientes_perfil_longitudinal.csv` |
| Borde | 30,4 % de puntos a ≤100 m del borde | `robustez_bordes_v1.csv` |

- **Qué demuestra:** que el eje vial real con buffer variable es una representación
  continua en densidad (ningún bin vacío en 4,4 km de perfil) y reemplaza con ventaja a
  23 tiles KMeans. La densidad varía de 105 a 525 pts/km con picos en el tramo oeste
  (bins 3 y 8) y en 1.200–1.600 m (bins 17–18), y un valle relativo en 400–800 m: hay
  base empírica para subtramos narrativos sin partir la geometría.
- **Qué no demuestra:** que el corredor sea la macrozona (cubre 29,9 % del universo; la
  MZ de 350 m de semiancho incluye oferta a varias cuadras del eje); que el eje sea un
  trazo continuo (son 5 componentes geométricos); dónde termina el polo frente a
  Microcentro (el contenedor de Microcentro se construyó restando este corredor).
- **Dependencia de Places:** baja (39,9 % universo; 39,7 % dentro del corredor).
- **Dependencia del contenedor:** media (30,4 % de puntos cerca de borde), pero la
  representación depende menos de la partición del detector: se apoya en el soporte
  vial.
- **Mejora principal frente a KMeans:** reemplazo integral de 23 tiles arbitrarios por
  un objeto urbano legible y trazable.
- **Riesgo de falsa precisión:** BAJO en la forma (el eje existe); MEDIO si el buffer
  60/90/120 se lee como medición de ancho real en lugar de convención de
  representación.
- **Decisión técnica posible ya:** reemplazar tiles por corredor; adoptar el patrón
  "eje respaldado + buffer variable + perfil longitudinal" para zonas tipo corredor.
- **Decisión humana pendiente:** corredor único vs. subtramos narrativos (DH-02);
  frontera con Microcentro (DH-03); estatus del ancho orientativo (DH-12).
- **¿Puede escalarse ahora?** Sí, el patrón corredor es el más maduro de los cinco.

## 4. Belgrano — red multinuclear

| Dimensión | Valor verificado | Fuente |
| --- | --- | --- |
| Universo | 697 puntos; 56,4 % Places | `robustez_ablacion_fuentes_v1.csv` |
| Representación | 6 núcleos sin nombre (de 28 comunidades a umbral 80 m) | geojson; `belgrano_comparacion_comunidades.csv` |
| Cobertura | 150/697 = 21,5 % (geojson; el CSV dice 152) | geojson; `mezcla_fuentes_representaciones_v1.csv` |
| Places dentro | 38,9–65,7 % según núcleo | geojson |
| Estabilidad local | BAJA (0,301); bootstrap de puntos 0,168 | `metricas_estabilidad_desagregadas_v1.csv` |
| Robustez bloques | 0,39 (0,336 @200 m; 0,446 @300 m); p10 ≈ 0,10 | `robustez_bootstrap_bloques_v1.csv` |
| Concordancia entre métodos | ARI grafo vs. HDBSCAN eom = **0,07**; eom vs. leaf = 0,16 | `belgrano_comparacion_comunidades.csv` |
| Ablación | F01/F02 solos: 2 clusters; F01 solo: 0 clusters (100 % ruido) | `robustez_ablacion_fuentes_v1.csv` |
| Borde | 32,7 % de puntos a ≤100 m; contenedor reducido duplica el ruido (12,8→26,0 %) | `robustez_bordes_v1.csv` |

- **Qué demuestra:** que la lectura multinuclear es visual y conceptualmente mejor que
  17 polígonos o una macroárea, y que se puede derivar un umbral de grafo de los datos
  (80 m = p75 de la distancia al 5º vecino) en lugar de imponer una cantidad de núcleos.
- **Qué no demuestra:** que estos 6 núcleos concretos existan de forma reproducible.
  La evidencia en contra es consistente: grafo y HDBSCAN casi no coinciden (ARI 0,07),
  eom y leaf tampoco (0,16), el bootstrap de puntos da 0,17, los bloques dan 0,39, y
  los 6 núcleos son una selección por tamaño entre 28 comunidades. Tampoco demuestra
  correspondencia con Barrio Chino, Cabildo/Juramento, Bajo Belgrano o
  Libertador/Barrancas: eso no se testeó y no debe afirmarse.
- **Dependencia de Places:** media-alta (56,4 % del universo; F01/F02 solos casi no
  tienen estructura: 2 clusters, y F01 solo es 100 % ruido). Parte de la
  multinuclearidad puede ser un artefacto de dónde mira Places.
- **Dependencia del contenedor:** ALTA. El contenedor es una unión de corredores de
  250 m (Juramento/Libertador/Cabildo) que ya deja 53 entidades conocidas fuera de toda
  macrozona; un tercio de los puntos está a ≤100 m del borde y encoger el contenedor
  100 m duplica el ruido. Es la hipótesis principal a testear en la repetición.
- **Mejora principal frente a KMeans:** deja de fabricar 17 piezas; propone unidades
  potencialmente reales y sin nombres impuestos.
- **Riesgo de falsa precisión:** ALTO si se publican los 6 hulls; los contornos parecen
  firmes y la evidencia dice que no lo son.
- **Decisión técnica posible ya:** repetir con protocolo formal
  (`ESPECIFICACION_REPETICION_BELGRANO.md`); no publicar los 6 núcleos; no nombrar.
- **Decisión humana pendiente:** aprobar el protocolo y el contenedor de contraste
  (DH-04); nombres y jerarquía recién después de la repetición (DH-05).
- **¿Puede escalarse ahora?** No. Bloquea también a las demás zonas de tipo
  multinuclear (Palermo Hollywood, Villa Crespo, Chacarita, Caballito).

## 5. Puerto Madero — frente gastronómico

| Dimensión | Valor verificado | Fuente |
| --- | --- | --- |
| Universo | 294 puntos; 71,1 % Places | `robustez_ablacion_fuentes_v1.csv` |
| Representación | PM_FRENTE_01 sobre `MOREAU DE JUSTO, ALICIA AV.`: 31 segmentos → 18 componentes, 3.527 m | geojson; metadata |
| Cobertura | 102/294 = 34,7 % (≤180 m del frente); 192 puntos fuera | metadata; `mezcla_fuentes_representaciones_v1.csv` |
| Places dentro | 63/102 = 61,8 %; densidad 28,9 pts/km | `mezcla_fuentes_representaciones_v1.csv` |
| Estabilidad local | ALTA (0,944) | `metricas_estabilidad_desagregadas_v1.csv` |
| Robustez bloques | 0,86 (0,847 @200 m; 0,875 @300 m); p10 0,81/0,83 — colas sanas | `robustez_bootstrap_bloques_v1.csv` |
| Sensibilidad global | MEDIA (mínima 0,767) | `metricas_estabilidad_desagregadas_v1.csv` |
| Borde | **71,8 % de puntos a ≤100 m del borde**; contenedor reducido: 11→5 clusters | `robustez_bordes_v1.csv` |
| Perfil | los 294 puntos proyectados; bin 750–1.000 m: 46 puntos, 40 Places (87 %) | `puerto_madero_perfil_frente.csv` |

- **Qué demuestra:** que la estructura de puntos de la zona es la más estable de las
  cinco (única con colas de bootstrap sanas) y que la forma "frente" es más honesta que
  11 manchas. La robustez 0,86 es real, pero es robustez del patrón de puntos, no
  validez del frente dibujado.
- **Qué no demuestra:** cobertura. El frente asigna un tercio de la evidencia; el
  soporte usado (una sola calle, Alicia Moreau de Justo, lado oeste de los diques)
  quedó disuelto en 18 componentes fragmentadas. El inventario del callejero local
  (`inventario_ejes_viales_puerto_madero.csv`, nuevo) confirma que existen ejes
  paralelos del lado este (Juana Manso 3.876 m, Pierina Dealessi 2.873 m, Olga
  Cossettini 1.650 m) que el prototipo no consideró: el soporte territorial estaba
  incompleto, como se sospechaba.
- **Dependencia de Places:** ALTA (71,1 % del universo; 61,8 % dentro del frente; el
  tramo norte del perfil es 87 % Places; F02 solo es 100 % ruido). Ninguna geometría
  debe presentarse como evidencia independiente de esa dependencia.
- **Dependencia del contenedor:** alta en apariencia (71,8 % cerca del borde), pero es
  en parte geometría inherente: el barrio es una península angosta. Distinguir "borde
  administrativo corta estructura" de "la zona es angosta" es parte de la repetición.
- **Mejora principal frente a KMeans:** forma urbana legible en lugar de 11 manchas.
- **Riesgo de falsa precisión:** MEDIO-ALTO si se publica el frente actual: robustez
  0,86 leída como "validado" cuando cubre el 34,7 %.
- **Decisión técnica posible ya:** repetir con inventario completo de soportes
  (`ESPECIFICACION_REPETICION_PUERTO_MADERO.md`); no publicar PM_FRENTE_01 solo.
- **Decisión humana pendiente:** frente único vs. doble vs. segmentos, y tratamiento de
  los 192 puntos (DH-06); nombres norte/centro/sur si aparecieran (no imponerlos).
- **¿Puede escalarse ahora?** No. Es además el único caso del tipo "frente": no hay a
  qué escalarlo todavía.

## 6. Costanera Norte — señal exploratoria

| Dimensión | Valor verificado | Fuente |
| --- | --- | --- |
| Universo | 72 puntos; 93,1 % Places; **F01/F02 = 5 puntos** | `robustez_ablacion_fuentes_v1.csv` |
| Representación | 4 marcadores de concentración + KDE, sin polígono | `costanera_concentraciones_exploratorias.geojson` |
| Cobertura | 71/72 puntos en las 4 concentraciones (10+29+11+21) | ídem |
| Places por concentración | 80 %, 96,6 %, 100 %, 90,5 % | ídem |
| Estabilidad local | ALTA (0,990) | `metricas_estabilidad_desagregadas_v1.csv` |
| Robustez bloques | 0,77 (0,759/0,778) | `robustez_bootstrap_bloques_v1.csv` |
| Borde | 87,5 % de puntos a ≤100 m del borde (franja costera angosta) | `robustez_bordes_v1.csv` |

- **Qué demuestra:** que hay concentraciones detectables y estables **de oferta visible
  en Places**, y que la decisión de no dibujar polígono es correcta.
- **Qué no demuestra:** existencia de un polo respaldado por fuentes públicas: con 5
  registros F01/F02 (0 clusters, 100 % ruido en la ablación), no hay universo público
  que delimitar. La robustez 0,77 es robustez del detector sobre una fuente única: es
  el caso de manual de "estructura robusta sin validez institucional".
- **Dependencia de Places:** extrema (93,1 %; CN_C03 es 100 % Places).
- **Dependencia del contenedor:** alta pero inherente (corredor costero de 250 m).
- **Mejora principal frente a KMeans:** elimina 4 polígonos que fabricaban falsa
  precisión sobre una fuente auxiliar.
- **Riesgo de falsa precisión:** BAJO con el tratamiento actual (puntos/KDE en anexo);
  ALTO ante cualquier intento de promoverla a polo firme.
- **Decisión técnica posible ya:** mantener como señal exploratoria; no repetir (no hay
  qué mejorar sin cambiar el universo de fuentes).
- **Decisión humana pendiente:** anexo vs. exclusión, y forma del anexo (DH-07).
- **¿Puede escalarse ahora?** El *tratamiento* sí: "señal exploratoria sin polígono" es
  el patrón por defecto para cualquier zona con dependencia Places extrema.

## 7. Síntesis

| Zona | Robustez bloques | Cobertura de la representación | Dependencia Places (universo) | ¿Escalable ya? |
| --- | --- | --- | --- | --- |
| San Telmo | 0,57 (p10 < 0) | 55,3 % | 46,6 % | patrón sí; zona espera DH-01 |
| Corrientes | 0,65 | 29,9 % | 39,9 % | sí (patrón corredor) |
| Belgrano | 0,39 | 21,5 % | 56,4 % | no — repetir |
| Puerto Madero | 0,86 | 34,7 % | 71,1 % | no — repetir soporte |
| Costanera Norte | 0,77 | n/a (sin polígono) | 93,1 % | solo como anexo |

KMeans queda descartado como generador de unidades territoriales; esta revisión no
encontró ningún elemento que reabra esa discusión.
