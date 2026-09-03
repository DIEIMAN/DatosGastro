# Construcción del universo gastronómico definitivo — Análisis metodológico

**Fecha:** 2026-07-08 · **Carácter:** análisis metodológico experimental. No integra ninguna
fuente ni modifica el pipeline F01–F05. Toda cifra citada proviene del perfilado de solo
lectura `outputs/polos_gastro/experimentos/diseno_pipeline_definitivo/perfil_fuentes_universo.md`
(corrida 2026-07-08) o de los contratos de fuentes vigentes.

## 1. Qué es (y qué no es) el universo buscado

El insumo que el pipeline de microzonas necesita es una **tabla maestra de entidades
gastronómicas georreferenciadas de toda la Ciudad**: una fila por local (entidad resuelta),
con la mejor coordenada disponible, categoría canónica y **evidencia por fuente** con fechas.

Semántica honesta y no negociable (guardrails 3 y 5): este universo mide **oferta
gastronómica registrada / con evidencia documental**, no "locales activos". Ninguna fuente
disponible —ni la suma de todas— acredita actividad actual. La palabra que corresponde en
informes es "oferta registrada" o "locales con evidencia [fuente/año]".

**Anti-patrón a evitar:** concatenar fuentes y clusterizar el resultado. Sin resolución de
entidades, un mismo local presente en F01 y F02 cuenta doble y la "densidad" resultante mide
redundancia administrativa, no concentración gastronómica. Peor con F02 crudo: 44.169 filas
gastronómicas colapsan en solo 7.908 ubicaciones únicas — clusterizar filas en vez de
entidades multiplicaría cada dirección por ~5,6 en promedio.

## 2. Fichas de fuentes candidatas

### 2.1 F01 — Oferta de establecimientos gastronómicos (BA Data) · pública, en pipeline

| Aspecto | Detalle |
|---|---|
| Qué mide | oferta gastronómica **registrada** en el dataset oficial (directorio) |
| Qué NO mide | actividad actual; altas/bajas desde la publicación del dataset |
| Volumen útil | 2.704 gastronómicos confirmados; 2.703 con coordenadas (100 %); 2.628 ubicaciones únicas |
| Calidad geo | excelente: coordenadas de origen + barrio determinado en 98 % |
| Categorías | ricas y consistentes (Restaurante 1.754, Café 414, Bar 368, …) + campos extra sin explotar: `cocina`, `ambientacion`, `horario` |
| Sesgo territorial | fuerte concentración en corredor central: Comuna 1 = 853 (32 %), Comuna 14 = 459 (17 %); Comuna 8 = 18 (0,7 %) |
| Actualización | snapshot; sin periodicidad garantizada — la fecha de corte hay que declararla siempre |
| Rol propuesto | **columna vertebral del universo v1**: nombres reales + coordenadas confiables |

### 2.2 F02 — Habilitaciones gastronómicas aprobadas (AGC) · pública, en pipeline

| Aspecto | Detalle |
|---|---|
| Qué mide | **trámites de habilitación aprobados**, históricos (guardrail 5: jamás "locales activos") |
| Qué NO mide | si el local abrió, sigue abierto o cerró; un local puede tener varias habilitaciones y una dirección varios locales sucesivos |
| Volumen útil | 44.169 filas gastronómicas → **7.908 ubicaciones únicas**; 97 % con coordenadas (vía USIG) |
| Composición temporal | 2015–2023 con fecha (concentrado 2016–2019; solo 19 filas en 2023) **+ 25.289 filas del recurso 2025 sin fecha de habilitación en el mapeo actual** (trae rubro, domicilio, comuna y razón social; es el componente más voluminoso y más reciente) |
| Calidad geo | buena pero indirecta (geocodificación de dirección, no coordenada de origen); `barrio/comuna` internos casi siempre "No determinado" — la asignación territorial confiable es point-in-polygon |
| Sesgo | mide formalización administrativa; sobrerrepresenta períodos de alta actividad de trámites (2016–2019); categorías administrativas (Catering 5.860, Comida al paso 7.719) que no siempre son locales a la calle |
| Riesgo específico | **duplicación interna masiva** (5,6 filas por ubicación); rubros no gastronómicos a la calle (catering, elaboración) que inflarían núcleos si no se filtran |
| Rol propuesto | **ampliación de cobertura** (7.908 ubicaciones vs. 2.628 de F01, y mejor distribución territorial), colapsada a una entidad por ubicación+rubro con ventana de recencia; el recurso 2025 merece revisión propia de mapeo (hoy entra sin fecha) |

### 2.3 Universo semilla PolosGastro (106 locales, Fase 13) · editorial

Curado a mano, 100 % geolocalizado, con estados de validación (32 match fuerte, 11 duplicados
probables, 8 vigencia no confirmada). **No aporta volumen** (106 puntos) pero es el único
conjunto con validación editorial: su rol correcto es **conjunto de control** — toda microzona
que el pipeline detecte en una macrozona debería contener a los locales semilla validados de
esa macrozona. Si no los contiene, algo está mal (en el pipeline o en la sede del local).
No se mezcla como fuente de puntos: se usa a posteriori como test.

### 2.4 Fuentes internas (I01–I99) · internas de gestión

Eventos internos, seguimiento operativo, bases de contacto. **No son padrón de locales** y
arrastran datos sensibles (contactos, CUIT — guardrail 7). Quedan **fuera** del universo de
clustering. Único uso legítimo futuro: validación cualitativa puntual (p. ej., confirmar que
un núcleo detectado coincide con la zona de un programa), siempre agregada.

### 2.5 F03 — Ferias y mercados · pública, en pipeline

4.352 puestos + 30 ferias + 6 mercados. Los **puestos no son locales gastronómicos a la
calle** y las ferias son eventos periódicos, no oferta fija. Incluirlos crearía falsos
núcleos en predios feriales. Quedan fuera del universo base; los mercados gastronómicos ya
tienen su propio subproyecto (no se toca). A lo sumo, capa de contexto en mapas.

### 2.6 OpenStreetMap (candidata F06+) · pública nueva

| Aspecto | Detalle |
|---|---|
| Qué mide | POIs gastronómicos **visibles para la comunidad OSM** (`amenity=restaurant/cafe/bar/fast_food`) |
| Ventajas | abierta (ODbL, con atribución), gratuita, script exploratorio ya permitido por skill 06, trae nombre + coordenada + a veces horario; útil como **tercera evidencia** para desempatar dudas F01/F02 |
| Limitaciones | cobertura heterogénea y no auditada; sesgo fuerte hacia zonas turísticas/céntricas (el mismo sesgo que F01, con lo cual **no corrige**, refuerza); vandalismo/desactualización posibles |
| Rol propuesto | fuente de **contraste y enriquecimiento** (matching de nombres, detección de cierres aparentes), no columna vertebral; entra solo con ficha F06+ y aprobación |

### 2.7 Google Places (candidata E01) · externa privada, condicional

| Aspecto | Detalle |
|---|---|
| Qué mide | oferta **visible en Google**, con `business_status`, rating y reseñas — lo más cercano a "actividad actual" disponible |
| Ventajas | frescura inigualable; nombres comerciales reales; el piloto de Fase 11 ya probó el mecanismo controlado (106 consultas, sin scraping) |
| Limitaciones/TOS | API paga (cada corrida requiere autorización presupuestaria explícita de Diego — skill 06); TOS restringe almacenamiento: `place_id` es almacenable, coordenadas y atributos tienen límites de caché/retención → el universo **no puede depender** de retener masivamente datos de Places; separación estricta de outputs internos vs. publicables (ya practicada en Fase 11) |
| Lecciones de Fase 11 | el matching nombre→lugar produce errores de sede (sucursales equivocadas), duplicados y vigencias no confirmadas: 25/106 quedaron "a revisar" — a escala de miles, esa tasa exige QA automático + muestreo humano, no revisión total |
| Costo estimado | cubrir CABA entera por grilla (Nearby Search) son miles de llamadas pagas y renovables; no es un costo único |
| Rol propuesto | **capa de validación de vigencia por muestreo** sobre núcleos ya detectados (decenas de consultas dirigidas, no censo), y solo si se autoriza presupuesto. No como fuente masiva del universo v1 |

### 2.8 Otras (delivery, pagos, reservas)

Solo por convenio y en formato agregado por zona (skill 06): no aportan padrón de puntos y
quedan fuera de este universo. Un futuro convenio agregado serviría para **ponderar demanda**
de microzonas ya detectadas, no para detectarlas.

## 3. Cobertura comparada y sesgos (evidencia del perfilado)

Participación por comuna (point-in-polygon, puntos con coordenadas):

- **F01** concentra el 49 % de su oferta en Comunas 1+14; Comuna 8 casi no existe (18 puntos).
- **F02** distribuye mejor: Comuna 1 = 23 %, y las comunas del sur y oeste (8, 9, 10) tienen
  volumen real (385 / 2.676 / 1.155 ubicaciones-trámite).

Implicancias de diseño:

1. Ninguna fuente sola alcanza: F01 tiene calidad pero cobertura céntrica; F02 tiene
   cobertura pero semántica administrativa y duplicación interna.
2. El sesgo no se "promedia" mezclando: se **documenta por fuente** y se mitiga en el
   pipeline con densidad relativa por macrozona (doc 01 §1) y con la bandera de QA
   `dependiente_de_fuente_X` (doc 01 §6).
3. En macrozonas periféricas, las microzonas saldrán con confianza más baja por escasez de
   evidencia — eso se declara, no se disimula con umbrales laxos.

## 4. Diseño de la tabla maestra

Una fila por **entidad**, nunca por fila de fuente:

| Campo | Contenido |
|---|---|
| `id_entidad` | estable entre versiones (hash de dirección normalizada + nombre canónico) |
| `nombre_canonico` | mejor nombre disponible (prioridad: semilla > F01 > OSM > F02 razón social) |
| `direccion_normalizada`, `id_ubicacion` | vía USIG, reutilizando el criterio del pipeline |
| `lat`, `lon`, `calidad_geo`, `fuente_geo` | mejor coordenada disponible (origen > geocodificada exacta > aproximada) |
| `categoria_canonica`, `confianza_categoria` | diccionario único |
| `en_f01`, `en_f02`, `en_semilla`, `en_osm`, … | banderas de evidencia por fuente |
| `evidencia_max_fecha`, `evidencia_min_fecha` | ventana temporal de la evidencia |
| `n_registros_origen`, `ids_origen` | linaje completo hacia las filas fuente |
| `estado_resolucion` | `unica` / `fusion_automatica` / `fusion_revisada` / `en_revision` |
| `version_universo`, `fecha_corte_por_fuente` | versionado |

Las filas fuente nunca se borran ni se editan: la resolución vive en una **tabla de
correspondencia** (fila fuente → entidad) regenerable y auditable.

## 5. Estrategia de deduplicación (resolución de entidades)

Hallazgo empírico que ordena todo el diseño: **la conciliación por ID compartido es casi
nula** — solo 21 ubicaciones comunes entre F01 (2.628) y F02 (7.908) pese a que ambas pasan
por `dim_ubicacion`. Las cadenas de dirección de cada fuente se normalizan por caminos
distintos y producen IDs distintos para el mismo lugar físico. Conclusión: la deduplicación
debe ser **espacial + textual**, en cuatro pasos:

1. **Bloqueo (blocking):** solo se comparan pares candidatos cercanos — misma celda de grilla
   de ~50 m (o cuadra normalizada calle+altura±25). Evita el producto cartesiano
   (2.628 × 7.908 pares es inviable y innecesario).
2. **Score por par candidato:**
   - distancia espacial (métrica; < 30 m alto, 30–80 m medio, > 80 m descarta salvo match
     textual perfecto),
   - similitud de nombre (token-based, p. ej. `token_set_ratio`; F02-2025 aporta
     `razon_social`, que difiere del nombre de fantasía → umbral más laxo y peso menor),
   - compatibilidad de categoría (café ≈ cafetería; catering ≉ restaurante),
   - coincidencia exacta de dirección normalizada (peso fuerte cuando existe).
3. **Tres bandas de decisión:** fusión automática (score alto) / **cola de revisión humana**
   (banda media) / entidades distintas (score bajo). Los umbrales se calibran contra un
   conjunto etiquetado a mano (~100–200 pares), construible a partir del universo semilla y
   sus 11 `duplicado_probable` ya identificados en Fase 11.
4. **Supervivencia (survivorship):** la entidad fusionada toma la mejor coordenada
   (origen > geocodificada), el nombre según prioridad de fuente, y la unión de la evidencia.

Casos límite documentados de antemano: galerías y patios gastronómicos (varios locales
legítimos en una misma dirección → la dirección igual NO implica duplicado; el nombre
decide); sucursales de cadena (mismo nombre, direcciones distintas → la distancia decide);
recambio comercial (misma dirección, años distintos, nombres distintos → entidades distintas
con nota de sucesión).

## 6. Estrategia de actualización

1. **Fecha de corte por fuente, siempre declarada.** El universo es un snapshot compuesto;
   su metadato mínimo es la lista fuente → fecha de corte.
2. **Snapshots versionados e inmutables** (`universo_vYYYYMM`): las microzonas citan la
   versión exacta; dos corridas sobre la misma versión son reproducibles.
3. **Actualización incremental, no reconstrucción:** al refrescar una fuente, solo las filas
   nuevas/cambiadas pasan por resolución; los `id_entidad` estables permiten comparar
   universos entre versiones (altas, bajas de evidencia).
4. **Recencia como atributo, no como filtro destructivo:** la evidencia vieja no se borra;
   el pipeline de microzonas decide qué ventana usa (p. ej. ponderar habilitaciones según
   antigüedad, o exigir evidencia ≥ año X para contar en densidad). Recomendación inicial:
   ventana dura de 10 años + peso decreciente por antigüedad, a sensibilizar en el piloto.
5. **Ciclo de mejora datos ↔ clustering:** los outliers de HDBSCAN y los puntos apartados de
   cada corrida vuelven como cola de revisión de sedes del universo (así se resolvieron los
   "10 apartados" de Tanda 2).
6. **Ritmo realista:** F01/F02 se refrescan cuando BA Data publique (verificar, no asumir);
   el universo se reversiona a lo sumo con cada tanda de microzonas, no en continuo.

## 7. Recomendación para el universo v1

- **Entran:** F01 (columna vertebral) + F02 colapsado a entidades con su semántica declarada.
  Costo cero, todo público, sin decisiones externas pendientes. Volumen esperado del orden de
  **8.000–9.500 entidades** tras resolución (2.628 ∪ 7.908 con fusiones), ~80× el universo
  semilla actual.
- **Control de calidad:** universo semilla como conjunto de test (§2.3).
- **Decisión de Diego requerida antes de la Fase B:** (a) confirmar F01+F02 como v1;
  (b) revisar el mapeo del recurso F02-2025 (hoy sin fecha) porque es la evidencia más
  reciente y voluminosa; (c) OSM sí/no como tercera evidencia (ficha F06+ previa);
  (d) Google Places queda para validación por muestreo con presupuesto explícito, nunca
  censo.
- **No entran:** F03 (puestos/ferias), fuentes internas I (sensibles, no-padrón), cualquier
  plataforma sin convenio.
