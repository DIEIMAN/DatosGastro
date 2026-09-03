# Fichas técnicas — 12 macrozonas de `macrozonas_v1_experimental` (Etapa Cal-1)

**Fecha:** 2026-07-08 · Estado revisado: snapshot de `macrozonas_v1_experimental.geojson`
antes de aplicar las correcciones de la Etapa Cal-2. Cada ficha resume lo ya construido
(`METODOLOGIA_MACROZONAS_V1.md`) y lo ya auditado (`QA_MACROZONAS_V1.md`) en formato de
revisión rápida, campo por campo.

---

## 1. Palermo (incluye subzonas Palermo Soho y Palermo Hollywood)

- **Nivel de confianza:** Palermo (contextual) = baja · Palermo Soho = **alta** ·
  Palermo Hollywood = **alta**
- **Superficie:** Palermo 1.585,6 ha · Soho 154,9 ha · Hollywood 88,5 ha
- **Entidades contenidas:** Palermo 1.360 · Soho 373 · Hollywood 213
- **Barrios involucrados:** Palermo (barrio administrativo completo para el polo); Soho y
  Hollywood son internos al barrio, no cruzan a otros barrios
- **Calles límite:** Soho = Scalabrini Ortiz, Córdoba, Juan B. Justo, Santa Fe (ficha
  PG001A); Hollywood = Juan B. Justo, Dorrego, Santa Fe, Córdoba (ficha PG001B); Palermo
  (polo) = ninguna, es el barrio administrativo completo
- **Fuente:** callejero GCBA (Soho/Hollywood) + `barrios_caba.geojson` (Palermo)
- **Problemas detectados:** Palermo (polo) solapa 67,8 % con Costanera Norte (bandera QA,
  bajo impacto porque no es contenedor de clustering); Las Cañitas, Palermo Chico y
  Palermo Nuevo/Botánico no tienen subzona propia todavía.
- **Observaciones:** Soho y Hollywood son el estándar de calidad al que deberían
  converger las demás macrozonas. No forma parte de los 4 bloqueantes de la Etapa Cal-2.

---

## 2. Avenida Corrientes — **BLOQUEANTE #1 (con Microcentro)**

- **Nivel de confianza:** media
- **Superficie:** 291,5 ha
- **Entidades contenidas:** 754 (321 cercanas fuera, ≤150 m)
- **Barrios involucrados:** Almagro, Balvanera, San Nicolás (corredor que los atraviesa)
- **Calles límite:** eje real de Av. Corrientes (callejero GCBA), semiancho editorial
  350 m, desde el entorno de Callao/9 de Julio hasta Abasto
- **Fuente:** callejero GCBA + semilla Fase 13 (Corrientes+Abasto, 12 puntos)
- **Problemas detectados:** **solapa 49,2 % con Microcentro y Centro — 406 entidades
  compartidas.** Es el bloqueante de mayor prioridad.
- **Observaciones:** la prueba de pipeline (tanda anterior) ya mostró que este corredor,
  en sí mismo, funciona muy bien (0 clusters sobredimensionados, incorpora territorio real
  que el contenedor viejo dejaba afuera). El problema no es la calidad del corredor: es
  su frontera con Microcentro.

## 3. Microcentro y Centro — **BLOQUEANTE #1 (con Corrientes)**

- **Nivel de confianza:** media
- **Superficie:** 229,0 ha
- **Entidades contenidas:** 763 (254 cercanas fuera)
- **Barrios involucrados:** San Nicolás (barrio completo usado como contorno)
- **Calles límite:** ninguna — es el barrio San Nicolás completo
- **Fuente:** `barrios_caba.geojson`
- **Problemas detectados:** mismo solapamiento que Corrientes (406 entidades
  compartidas); no incluye Retiro (la ficha PG011 menciona "Retiro y área central").
- **Observaciones:** al ser un barrio completo sin recorte, el corredor de Corrientes lo
  atraviesa de lado a lado — es esperable que se solapen mientras Microcentro no excluya
  la franja que ya cubre Corrientes.

---

## 4. Belgrano — **BLOQUEANTE #2**

- **Nivel de confianza:** baja
- **Superficie:** 202,0 ha
- **Entidades contenidas:** 273 (83 cercanas fuera)
- **Barrios involucrados:** Belgrano
- **Calles límite:** ninguna verificada — el método actual usa 4 elipses editoriales de
  fase16 (dibujadas a mano) intersectadas con el barrio
- **Fuente:** `subzonas_editoriales_geometrias.geojson` (fase16) + `barrios_caba.geojson`
- **Problemas detectados:** confianza baja porque hereda una aproximación no verificada
  contra calles reales; la validación anterior sugirió que el cluster dominante mezcla 3
  identidades (Barrio Chino, Bajo Belgrano, Belgrano R). Además, al investigar la semilla
  para un posible recorte: **de 11 puntos, 3 están a 2-10 km de distancia** (Ichisou,
  Alo's Café muy lejos; BAO Kitchen y Tori Tori a 2-4 km) — la semilla de este polo está
  sesgada hacia Barrio Chino específicamente y no sirve para recortar el polo completo.
- **Observaciones:** las 3 identidades internas SÍ tienen calles de referencia en la
  documentación existente (Juramento/Arribeños para Barrio Chino, Libertador para Bajo
  Belgrano, Cabildo para Belgrano R) — nunca antes usadas como corte real. Es la base de
  la corrección propuesta en la Etapa Cal-2.

---

## 5. Costanera Norte — **BLOQUEANTE #3**

- **Nivel de confianza:** baja
- **Superficie:** 225,1 ha
- **Entidades contenidas:** 5 (0,02/ha — la más baja de las 12; 0 cercanas fuera)
- **Barrios involucrados:** Belgrano, Palermo, Recoleta (corredor costero que los bordea)
- **Calles límite:** eje real de Av. Costanera Rafael Obligado, semiancho editorial 350 m
- **Fuente:** callejero GCBA
- **Problemas detectados:** evidencia extremadamente escasa; al graficar las 5 entidades
  reales se confirma que están concentradas en 3 micro-ubicaciones dentro de un tramo de
  ~2,2 km, mientras el corredor actual cubre ~4,4 km (casi el doble) — la mitad norte del
  polígono no tiene ninguna entidad. 1 de los 6 puntos semilla originales ("Puerto
  Cristal") está geocodificado a ~6 km de distancia.
- **Observaciones:** no hay "más evidencia" que agregar — el ajuste posible es acotar el
  corredor al tramo real con datos y no fingir cobertura donde no la hay.

---

## 6. Chacarita — **BLOQUEANTE #4**

- **Nivel de confianza:** baja
- **Superficie:** 311,7 ha
- **Entidades contenidas:** 116 (0,37/ha; 86 cercanas fuera)
- **Barrios involucrados:** Chacarita (barrio completo usado como contorno)
- **Calles límite:** ninguna — barrio completo, sin recorte
- **Fuente:** `barrios_caba.geojson` únicamente (se intentó recortar con semilla y
  falló: área resultante 0 ha, ver metodología anterior)
- **Problemas detectados:** al graficar las 116 entidades reales del universo V1 (F01+F02,
  no la semilla), quedó claro que **están concentradas en un rectángulo de ~2 km × 2 km**
  dentro del barrio, no distribuidas por sus 311,7 ha — el barrio completo es varias
  veces más grande que la zona gastronómica real.
- **Observaciones:** a diferencia de la semilla (mal geocodificada para este polo), las
  116 entidades del universo V1 sí son una señal confiable y compacta — es la base de la
  corrección propuesta.

---

## 7. San Telmo

- **Nivel de confianza:** media · **Superficie:** 123,2 ha · **Entidades:** 171 (71 cerca-fuera)
- **Barrios:** San Telmo (con bordes tocando Barracas/Constitución/Monserrat/La Boca)
- **Calles límite:** ninguna documentada con precisión — barrio ∩ buffer 700 m de semilla
- **Fuente:** `barrios_caba.geojson` + semilla Fase 13 (8 puntos)
- **Problemas detectados:** la validación anterior encontró 2 clusters HDBSCAN fuera de
  toda elipse editorial (uno al norte hacia Constitución, uno al sur hacia Barracas) —
  sin verificar todavía si el buffer de 700 m los excluye.
- **Observaciones:** no es uno de los 4 bloqueantes; queda para un refinamiento menor
  posterior.

## 8. Villa Crespo

- **Nivel de confianza:** media · **Superficie:** 160,5 ha · **Entidades:** 179 (68 cerca-fuera)
- **Barrios:** Villa Crespo · **Calles límite:** ninguna · **Fuente:** barrio + semilla (9 puntos)
- **Problemas detectados:** ninguno relevado. Caso "neutro" en todas las tandas anteriores.

## 9. Puerto Madero

- **Nivel de confianza:** media · **Superficie:** 503,2 ha · **Entidades:** 85 (30 cerca-fuera; 0,17/ha)
- **Barrios:** Puerto Madero (con bordes tocando Retiro/San Nicolás/San Telmo/Monserrat/La Boca)
- **Calles límite:** ninguna — barrio completo, con 4 huecos interiores (los diques de
  agua, esperado)
- **Problemas detectados:** densidad muy baja; el barrio completo probablemente excede la
  zona gastronómica real (concentrada en la franja este/docks). No es bloqueante, pero es
  candidato a refinamiento menor.

## 10. Recoleta

- **Nivel de confianza:** media · **Superficie:** 245,8 ha · **Entidades:** 404 (147 cerca-fuera)
- **Barrios:** Recoleta (borde tocando Retiro) · **Fuente:** barrio + semilla (7 puntos)
- **Problemas detectados:** ninguno bloqueante; 147 cercanas-fuera es alto en términos
  absolutos, candidato a revisar el radio de buffer en un refinamiento menor.

## 11. Caballito

- **Nivel de confianza:** media · **Superficie:** 347,4 ha · **Entidades:** 265 (140 cerca-fuera)
- **Barrios:** Caballito (borde tocando Flores) · **Fuente:** barrio + semilla (5 puntos)
- **Problemas detectados:** ninguno bloqueante. Nota técnica ya resuelta: la construcción
  generó una autointersección al reproyectar (corregida con limpieza post-reproyección).

## 12. Avenida Caseros / Barracas

- **Nivel de confianza:** baja · **Superficie:** 55,9 ha (la más chica de las 12) ·
  **Entidades:** 18 (32 cerca-fuera)
- **Barrios:** Barracas (borde tocando Constitución/Parque Patricios)
- **Calles límite:** eje real de Av. Caseros, semiancho 300 m, recortado al barrio
- **Problemas detectados:** semilla mayormente ruido (3 de 5 puntos "duplicado_probable",
  1 sede de Palermo mal asignada) — no se usó para acotar el corredor. No es uno de los 4
  bloqueantes según el pedido, pero comparte el mismo patrón de "evidencia escasa" que
  Costanera Norte; queda para revisión en una próxima ronda.

---

## Resumen de bloqueantes a resolver en la Etapa Cal-2 (en el orden pedido)

1. **Avenida Corrientes / Microcentro y Centro** — solapamiento operativo (406 entidades).
2. **Belgrano** — confianza baja, aproximación heredada sin verificar contra calles reales.
3. **Costanera Norte** — corredor sobredimensionado respecto de la evidencia real.
4. **Chacarita** — barrio completo sobredimensionado respecto de la concentración real de entidades.

Ningún refinamiento menor (San Telmo, Puerto Madero, Recoleta, Caseros/Barracas) se toca
hasta resolver estos 4, según lo pedido explícitamente.
