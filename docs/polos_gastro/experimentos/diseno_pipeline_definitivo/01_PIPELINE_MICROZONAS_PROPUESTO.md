# Pipeline definitivo propuesto — Microzonas gastronómicas dentro de macrozonas

**Fecha:** 2026-07-08 · **Carácter:** propuesta metodológica experimental, sujeta a decisión
humana. No modifica el pipeline F01–F05, la Fase 25 ni ningún informe vigente. Nada de lo aquí
descripto define límites oficiales.

**Documentos hermanos:** `02_COMPARACION_ALGORITMOS_Y_POLIGONIZACION.md` (elección de métodos)
y `03_CONSTRUCCION_UNIVERSO_GASTRONOMICO.md` (insumo de datos). Evidencia empírica de respaldo:
`outputs/polos_gastro/experimentos/diseno_pipeline_definitivo/perfil_fuentes_universo.md`.

## 1. Objetivo y encuadre

Las **macrozonas** (Palermo Soho, Palermo Hollywood, San Telmo, Corrientes, etc.) siguen
siendo las unidades territoriales del informe de PolosGastro. El pipeline propuesto **no las
redefine**: las toma como marco fijo y detecta, dentro de cada una, los **núcleos
gastronómicos reales** (p. ej. Fitz Roy–Honduras–Gorriti dentro de Palermo Hollywood),
generando polígonos chicos y precisos — **microzonas** — subordinados a la macrozona.

Esto invierte el planteo de las Tandas 1 y 2: allí el clustering era global y se comparaba
contra las zonas editoriales; aquí el clustering corre **por macrozona**, con la macrozona
como restricción de contorno. Consecuencias de diseño:

- Un cluster nunca puede cruzar macrozonas: el problema de "DBSCAN mezcla etiquetas de polos
  lejanos" (Tanda 2) desaparece por construcción.
- La densidad se evalúa **relativa a cada macrozona**, no a toda la Ciudad: evita que el
  sesgo de registro entre comunas (F01: 32 % de la oferta registrada cae en la Comuna 1)
  decida qué macrozonas "merecen" microzonas.
- Los puntos fuera de toda macrozona no se descartan: van a una capa diagnóstica separada
  (posibles zonas emergentes), que solo se incorpora por decisión editorial.

## 2. Principios no negociables

1. **Universos separados** (guardrail 3): el universo de entrada es uno solo, construido con
   resolución de entidades documentada (doc 03); nunca una concatenación automática de fuentes.
2. **Semántica honesta** (guardrail 5): las microzonas describen concentración de **oferta
   gastronómica registrada/con evidencia**, no de "locales activos". Cada salida lo declara.
3. **Revisión humana obligatoria**: ningún polígono llega a un informe sin aprobación
   explícita; el QA automático filtra, no aprueba.
4. **Trazabilidad completa**: cada microzona debe poder rastrearse a macrozona → cluster →
   puntos → fuentes → fecha de corte.
5. **Versionado**: cada corrida produce un snapshot inmutable (universo + parámetros +
   polígonos + decisiones humanas). Los informes citan una versión, no "la última".

## 3. Flujo propuesto

```
(0) Fuentes crudas (F01, F02, semilla PolosGastro, [OSM], [Google Places])
        │  fichas por fuente, fecha de corte, universo propio
        ▼
(1) UNIVERSO GASTRONÓMICO CONSOLIDADO          ← doc 03
        │  tabla maestra de entidades con evidencia por fuente
        ▼
(2) NORMALIZACIÓN
        │  direcciones USIG · categorías canónicas · CRS métrico
        ▼
(3) DEDUPLICACIÓN / RESOLUCIÓN DE ENTIDADES    ← doc 03 §5
        │  bloqueo espacial + similitud de nombre + compatibilidad de rubro
        ▼
(4) ASIGNACIÓN A MACROZONA
        │  point-in-polygon contra capa editorial (+ buffer de tolerancia)
        │  → residuo "fuera de macrozona" a capa diagnóstica
        ▼
(5) CLUSTERING INTRA-MACROZONA                 ← doc 02 §2
        │  HDBSCAN por macrozona · KDE como superficie de control
        ▼
(6) POLIGONIZACIÓN                             ← doc 02 §3
        │  concave hull + buffer · cápsula sobre eje si es corredor
        │  recorte a macrozona y a CABA
        ▼
(7) QA AUTOMÁTICO (gates duros + banderas)     ← §6
        ▼
(8) REVISIÓN HUMANA (checklist + decisiones registradas)
        ▼
(9) MICROZONAS FINALES versionadas (GeoJSON + metadatos + linaje)
```

Cada etapa lee la salida versionada de la anterior; ninguna escribe sobre insumos.

## 4. Detalle por etapa

### (1) Universo consolidado
Tabla maestra de **entidades gastronómicas** (no de filas de fuente): una fila por entidad
resuelta, con banderas de evidencia por fuente (`en_f01`, `en_f02`, `en_semilla`, …), mejor
coordenada disponible con su calidad (`usig_exacta` > centroide), categoría canónica y fechas
de evidencia. Ver doc 03. **Decisión pendiente de Diego:** qué fuentes entran a la v1.

### (2) Normalización
- Direcciones vía USIG (ya existe `src/geocode_usig.py` como referencia de método; esta línea
  experimental usa sus mismos criterios sin tocar el pipeline).
- Reproyección a CRS métrico (POSGAR/Gauss-Krüger faja 5 o UTM 21S) **antes** de cualquier
  cálculo de distancias: los grados no son metros y CABA está lejos del ecuador.
- Categorías canónicas (restaurante, café, bar, pizzería, …) con diccionario único; los
  rubros administrativos de F02 se mapean, no se copian.

### (3) Deduplicación
El perfilado empírico mostró que la conciliación por ID de ubicación es casi nula entre
fuentes (21 direcciones compartidas entre F01 y F02 sobre 2.628 y 7.908). La resolución debe
ser **espacial + textual**: bloqueo por celda/cuadra, score de similitud de nombre +
distancia + rubro, banda de revisión humana. Detalle y umbrales en doc 03 §5.

### (4) Asignación a macrozona
- Capa editorial de referencia: geometrías de subzonas V4
  (`fase16_mapas_editoriales_v4/tablas/subzonas_editoriales_geometrias.geojson`), **solo
  lectura**. Si la macrozona editorial es textual (base cartográfica de 32 polos), habrá que
  digitalizar su contorno aproximado una única vez, como capa de trabajo experimental.
- Buffer de tolerancia (~100–150 m) para no perder locales de vereda de enfrente en el borde.
- Un punto pertenece a **una sola** macrozona (la de mayor solapamiento / menor distancia);
  Abasto se trata como subzona de Corrientes (decisión editorial vigente, no se re-litiga).

### (5) Clustering intra-macrozona
Recomendación (fundamentos en doc 02): **HDBSCAN** por macrozona como detector principal
(densidad variable, sin `eps` global, outliers explícitos), con **KDE** como superficie de
control y visualización, y una corrida DBSCAN de continuidad para comparar contra Tandas 1–2.
Parámetros iniciales a calibrar (§5 del doc 02): `min_cluster_size = max(8, 3 % de los puntos
de la macrozona)`, `min_samples = 5`, `cluster_selection_epsilon = 50 m`.

### (6) Poligonización
Regla híbrida (doc 02 §3–4): forma compacta → concave hull + buffer de frente de local
(~30–40 m); forma alargada (elongación PCA > 3 y largo > 600 m) → cápsula sobre el eje
(principal o vial cuando esté disponible la base callejera GCBA, pendiente ya identificado en
el plan de mapas V3); n < mínimo → marcador puntual, sin polígono. Siempre: recorte a la
macrozona y al límite de CABA; sin solapamiento entre microzonas hermanas.

### (7–8) QA automático y revisión humana → §6 y §7.

### (9) Salida final
Por corrida: `microzonas_vYYYYMMDD.geojson` (polígonos con atributos), tabla de puntos por
microzona, tabla de decisiones humanas, y un `metadatos.md` con universo usado, fecha de
corte por fuente, parámetros, versión de la capa editorial y resultados de QA. Con
`kpis_lock.json` si algún número se vuelve canónico para informes.

## 5. Atributos mínimos de cada microzona

| Atributo | Ejemplo |
|---|---|
| `id_microzona` | `MZ_PALERMO_HOLLYWOOD_01` |
| `macrozona` / `subzona editorial` | Palermo Hollywood |
| `nombre_descriptivo` (humano) | Núcleo Fitz Roy–Honduras |
| `n_locales`, `densidad_ha`, `superficie_ha` | 42 · 3.1 · 13.5 |
| `forma` | compacta / corredor / puntual |
| `metodo_poligono` | concave_hull_buffer / capsula_eje |
| `confianza` | alta / media / baja (por n, densidad y estabilidad) |
| `estado_revision` | aprobada / recortada / rechazada / fusionada / pendiente |
| `universo_version`, `fecha_corte`, `parametros_id` | trazabilidad |

## 6. QA automático — restricciones contra polígonos absurdos

Lección directa de la Tanda 2 (hulls de 1.546 ha en Chacarita): los límites se imponen como
**gates duros** (rechazan) y **banderas** (mandan a revisión). Valores provisionales, a
calibrar en la primera tanda con universo completo:

| Regla | Gate duro (rechaza) | Bandera (revisar) |
|---|---|---|
| Superficie máxima | > 35 ha | > 20 ha |
| Cantidad mínima de locales | < 5 | < 8 |
| Densidad mínima | < 1 local/ha | < 2 locales/ha |
| Distancia máx. al vecino más cercano intra-cluster | > 250 m | > 150 m |
| Diámetro máximo (no corredor) | > 1.200 m | > 800 m |
| Elongación (corredor no declarado) | — | ratio PCA > 3 |
| Contención en macrozona | < 90 % del área dentro | < 98 % |
| Solapamiento entre microzonas | > 0 (se resuelve, no se publica) | — |
| Fuera de CABA | cualquier vértice fuera | — |

Además, dos validaciones de estabilidad (banderas):
- **Sensibilidad a parámetros:** la microzona debe sobrevivir (Jaccard de área > 0.6) a una
  perturbación de ±25 % en `min_cluster_size`; si no, `inestable_parametros`.
- **Sensibilidad a fuente:** si al quitar una fuente del universo la microzona desaparece,
  `dependiente_de_fuente_X` (relevante mientras conviva evidencia F01/F02 con sesgos propios).

## 7. Revisión humana obligatoria

Checklist mínimo por microzona, sobre mapa con puntos + polígono + trama urbana:

1. ¿El polígono corresponde a un núcleo reconocible en terreno? (validación de quien conoce
   la zona; el ejemplo canónico es que en Palermo Hollywood emerja Fitz Roy–Honduras–Gorriti
   y no todo el barrio).
2. ¿Incluye locales apartados que lo deforman? → recortar puntos y regenerar (equivalente a
   los "10 apartados" de la Tanda 2, que resultaron ser errores de sede de Fase 11).
3. ¿Hay microzonas hermanas que deberían fusionarse o separarse?
4. ¿El nombre descriptivo es correcto y no inventa toponimia?
5. Decisión registrada en tabla (`aprobada` / `recortada` / `rechazada` / `fusionada`), con
   autor y fecha. La tabla de decisiones es parte del snapshot versionado.

## 8. Estrategia de adopción (sin tocar nada vigente)

1. **Fase A — diseño (esta entrega):** documentos metodológicos + perfilado de fuentes.
2. **Fase B — universo v1:** construir la tabla maestra con F01 + F02 (público, sin costo),
   con resolución de entidades y QA propio. Decisión de Diego sobre incluir semilla y OSM.
3. **Fase C — piloto en 3 macrozonas:** Palermo (Soho + Hollywood), San Telmo y Corrientes
   (incluye un corredor, el caso difícil). Calibrar parámetros y umbrales de QA.
4. **Fase D — corrida completa:** todas las macrozonas, revisión humana, snapshot v1 de
   microzonas.
5. **Fase E — integración editorial:** solo si jefatura lo aprueba, las microzonas entran a
   los mapas del informe como capa adicional; las macrozonas no cambian.

Todo dentro de `scripts/polos_gastro/experimentos/`, `docs/polos_gastro/experimentos/` y
`outputs/polos_gastro/experimentos/` hasta la aprobación explícita de la Fase E.

## 9. Riesgos conocidos

- **El universo manda:** con el semilla de 106 puntos este pipeline no mejora nada (techo ya
  demostrado en Tanda 2). La Fase B es condición previa, no opcional.
- **F02 mide trámites históricos** (2015–2023, con caída fuerte post-2019 en lo integrado):
  usarlo sin ponderación de recencia infla núcleos que pueden haber decaído. Ver doc 03 §6.
- **Digitalizar contornos de macrozonas** donde solo hay delimitación textual introduce una
  capa de trabajo que debe marcarse como aproximada y no institucional.
- **Nombres de microzonas**: es tentador bautizar núcleos; la toponimia es decisión
  editorial, no del algoritmo.
