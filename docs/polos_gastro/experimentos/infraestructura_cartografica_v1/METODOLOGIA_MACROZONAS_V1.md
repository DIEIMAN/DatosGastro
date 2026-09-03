# Metodología — `macrozonas_v1_experimental.geojson`

**Fecha:** 2026-07-08 · **Carácter:** primera versión operativa, experimental,
`estado_revision = borrador` en las 14 features. Construida con
`scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/construir_macrozonas_v1.py`
sobre el esquema de `02_DISENO_CAPA_EDITORIAL.md`. No reemplaza nada oficial; no se
aprobó ningún polígono todavía.

## Resumen

| | Cantidad |
|---|---|
| Features totales | 14 (12 polos + 2 subzonas) |
| Confianza alta | 2 (Palermo Soho, Palermo Hollywood) |
| Confianza media | 7 |
| Confianza baja | 5 |
| Contenedores de clustering (`es_contenedor_clustering=true`) | 13 |
| Solo contextual (no clusteriza) | 1 (Palermo, nivel polo) |

Fuentes usadas: callejero GCBA (calles reales), `barrios_caba.geojson` (BA Data, límites
administrativos oficiales), semilla Fase 13 (106 puntos, depurada), elipses editoriales
de fase16 (heredadas, solo Belgrano), fichas de polo (`docs/polos_gastro/fichas_polos/`).

## Ficha por macrozona

### MZ_PALERMO_SOHO — confianza ALTA
- **Método:** calles reales (regresión de línea + partición del plano sobre el
  callejero GCBA, Etapa Infra-4).
- **Fuente:** ficha PG001A + callejero GCBA.
- **Límites asumidos:** Scalabrini Ortiz, Córdoba, Juan B. Justo, Santa Fe.
- **Dudas:** ninguna sobre el método; sí sobre si el borde exacto (a mitad de calle o a
  un lado) es el correcto editorialmente.
- **Qué revisar:** aprobar o ajustar bordes contra conocimiento de terreno (caso de
  prueba canónico de la validación: ¿el polígono corresponde a lo que un conocedor
  llamaría "Soho"?). 373 entidades contenidas, 173 entidades a ≤150 m fuera (revisar si
  alguna debería estar adentro).

### MZ_PALERMO_HOLLYWOOD — confianza ALTA
- **Método/fuente/límites:** igual que Soho, con ficha PG001B (Juan B. Justo, Dorrego,
  Santa Fe, Córdoba).
- **Dudas/revisión:** igual que Soho. 213 entidades contenidas, 51 cercanas fuera.

### MZ_PALERMO (nivel polo, contextual — NO clusteriza)
- **Método:** barrio oficial GCBA completo (Palermo), sin recortar.
- **Fuente:** `barrios_caba.geojson`.
- **Límites asumidos:** el barrio administrativo completo (1.585,6 ha).
- **Dudas:** este contorno es deliberadamente impreciso — es solo un contenedor
  contextual/de reporte, no se usa para clustering (para eso están Soho y Hollywood).
  **Solapa 67,8 % con Costanera Norte** (bandera B2): esperable dado que ambos son
  aproximaciones gruesas en la misma zona geográfica, pero a resolver si algún informe
  llegara a usar el polo "Palermo" como si fuera un contenedor operativo.
- **Qué revisar:** decidir si Las Cañitas, Palermo Chico y Palermo Nuevo/Botánico
  necesitan su propia subzona con contorno real en la próxima versión (hoy quedan
  "dentro" de este contorno grueso pero sin geometría propia).

### MZ_SAN_TELMO — confianza MEDIA
- **Método:** barrio oficial (San Telmo) ∩ buffer 700 m alrededor de la semilla Fase 13
  depurada.
- **Fuente:** `barrios_caba.geojson` + semilla Fase 13 (8 puntos, sin duplicados
  probables).
- **Límites asumidos:** el barrio administrativo, acotado a donde hay evidencia semilla
  cercana.
- **Dudas:** la validación anterior (Etapa V2-3) encontró 2 clusters HDBSCAN fuera de
  toda elipse editorial de San Telmo (uno al norte hacia Constitución, uno al sur hacia
  Barracas) — sin verificar todavía si este contorno nuevo los excluye correctamente.
- **Qué revisar:** 171 entidades contenidas, 71 cercanas fuera — revisar si el radio de
  700 m es demasiado generoso hacia el norte/sur.

### MZ_BELGRANO — confianza BAJA
- **Método:** unión de las 4 elipses editoriales de fase16 (Barrio Chino, Bajo Belgrano,
  Belgrano R, Cabildo/Juramento) ∩ barrio oficial Belgrano.
- **Fuente:** `subzonas_editoriales_geometrias.geojson` (fase16) + `barrios_caba.geojson`.
- **Límites asumidos:** los que ya usaban los mapas oficiales hasta Fase 25 (elipses
  dibujadas a mano, "no límite oficial" en su propia documentación).
- **Dudas:** es una aproximación **heredada**, no una construcción nueva — la confianza
  es baja porque no se verificó contra calles reales. La validación anterior sugirió que
  el cluster dominante de Belgrano probablemente mezcla las 3 identidades internas.
- **Qué revisar:** 273 entidades contenidas, 83 cercanas fuera. Candidato prioritario
  para subdividir en subzonas (Barrio Chino / Bajo Belgrano / Belgrano R) con calles
  reales en la próxima versión, igual que se hizo con Palermo Soho/Hollywood.

### MZ_CHACARITA — confianza BAJA
- **Método:** barrio oficial (Chacarita) completo, sin recorte por semilla.
- **Fuente:** `barrios_caba.geojson`.
- **Límites asumidos:** el barrio administrativo completo (311,7 ha).
- **Dudas:** se intentó recortar con semilla (como San Telmo) pero **4 de los 6 puntos
  semilla de este polo caen a 3-6 km del barrio real** (p. ej. "Bar Chacabuco" y "Cantina
  Urondo" a la altura de Parque Patricios/Nueva Pompeya, "Bar Roma" cerca de Almagro) —
  el buffer resultante no llegaba a tocar el barrio (área 0, bug detectado y corregido
  usando el barrio completo como fallback).
- **Qué revisar:** **esos 4 locales tienen sede mal geocodificada en la Fase 13** y
  deberían corregirse en la cola de calidad del universo semilla, no en esta capa. 116
  entidades contenidas, 86 cercanas fuera.

### MZ_VILLA_CRESPO — confianza MEDIA
- **Método:** barrio oficial (Villa Crespo) ∩ buffer 700 m de semilla.
- **Fuente:** `barrios_caba.geojson` + semilla Fase 13 (9 puntos).
- **Dudas:** ninguna particular; caso "neutro" en la validación anterior.
- **Qué revisar:** 179 entidades contenidas, 68 cercanas fuera.

### MZ_PUERTO_MADERO — confianza MEDIA
- **Método:** barrio oficial (Puerto Madero) completo, sin recorte.
- **Fuente:** `barrios_caba.geojson`.
- **Límites asumidos:** el barrio administrativo (503,2 ha) — no se usó semilla porque 1
  de 9 puntos ("Puerto Cristal") está geocodificado a ~6 km de distancia.
- **Dudas:** el barrio incluye los diques de agua (por eso aparecen 4 huecos interiores
  en la geometría — bandera B1, **esperable e intencional**, no un error). Densidad muy
  baja (0,17 entidades/ha, la más baja después de Costanera Norte) — el barrio completo
  puede ser más grande que la zona gastronómica real.
- **Qué revisar:** 85 entidades contenidas, 30 cercanas fuera; considerar recortar a la
  franja este (docks) en una próxima versión en vez de todo el barrio.

### MZ_RECOLETA — confianza MEDIA
- **Método:** barrio oficial (Recoleta) ∩ buffer 700 m de semilla.
- **Fuente:** `barrios_caba.geojson` + semilla Fase 13 (7 puntos).
- **Qué revisar:** 404 entidades contenidas, 147 cercanas fuera (la mayor cercanía-fuera
  en términos absolutos junto con Corrientes/Microcentro) — revisar si el radio de
  buffer deja fuera locales relevantes cerca del borde.

### MZ_CABALLITO — confianza MEDIA
- **Método:** barrio oficial (Caballito) ∩ buffer 700 m de semilla.
- **Fuente:** `barrios_caba.geojson` + semilla Fase 13 (5 puntos).
- **Dudas técnicas:** la intersección barrio∩buffer generó inicialmente una geometría
  inválida (autointersección) al reproyectar de metros a grados — corregido con limpieza
  de geometría (`limpiar_geometria`, buffer(0) tras cada intersección/reproyección);
  documentado para que quede claro que no es un error de datos sino de precisión
  numérica en la construcción.
- **Qué revisar:** 265 entidades contenidas, 140 cercanas fuera.

### MZ_COSTANERA_NORTE — confianza BAJA
- **Método:** corredor real sobre el eje de la Av. Costanera Rafael Obligado
  (callejero GCBA), semiancho 350 m, sin anclar a semilla.
- **Fuente:** callejero GCBA.
- **Límites asumidos:** semiancho editorial de 350 m sin calibrar contra evidencia
  (no hay evidencia suficiente para calibrar: solo 5 entidades contenidas en 225 ha,
  densidad 0,02/ha — la más baja de las 12).
- **Dudas:** de los 6 puntos semilla, 1 ("Puerto Cristal") está a ~6 km de distancia
  (mal geocodificado) y 2 más están marcados "zona_sucursal_a_revisar" — por eso no se
  usó semilla para acotar el corredor.
- **Qué revisar:** esta es, con los datos actuales, **la macrozona menos confiable de
  las 12** — su forma (bulbosa, seguía la curva del callejero) fue la más irregular en
  la inspección visual. Antes de usarla en un informe, revisar sede de "Puerto Cristal" y
  evaluar si conviene directamente marcarla "evidencia insuficiente" (como se hizo en el
  prototipo V1) en vez de forzar un contorno.

### MZ_AVENIDA_CASEROS_BARRACAS — confianza BAJA
- **Método:** corredor real sobre Av. Caseros ∩ barrio Barracas, semiancho 300 m.
- **Fuente:** callejero GCBA + `barrios_caba.geojson`.
- **Dudas:** de los 5 puntos semilla, 3 están marcados "duplicado_probable" y 1
  "zona_sucursal_a_revisar" (era en realidad una sede de Palermo) — la semilla de este
  polo es mayormente ruido, no se usó para acotar el corredor.
- **Qué revisar:** solo 55,9 ha (la macrozona más chica), 18 entidades contenidas, 32
  cercanas fuera — revisar si el semiancho de 300 m es demasiado angosto.

### MZ_AVENIDA_CORRIENTES — confianza MEDIA
- **Método:** corredor real sobre Av. Corrientes desde el entorno de Callao/9 de Julio
  hasta Abasto, semiancho 350 m (Abasto = subzona de este polo, decisión editorial
  vigente, no se re-litiga).
- **Fuente:** callejero GCBA + semilla Fase 13 (Avenida Corrientes + Abasto, 12 puntos).
- **Dudas:** **solapa 49,2 % con Microcentro y Centro, con 406 entidades en la zona de
  solape** (bandera B2/SOLAPE) — es el problema más serio de esta versión: ambas
  macrozonas son contenedores de clustering (`es_contenedor_clustering=true`), así que
  esas 406 entidades quedarían procesadas por ambas si se corre el pipeline sin resolver
  esto antes.
- **Qué revisar:** **decisión editorial pendiente y prioritaria** —¿dónde termina
  Corrientes y empieza Microcentro? La validación anterior (Etapa V2-3) ya había
  encontrado que el cluster más grande de esta macrozona caía en San Nicolás, fuera de
  la elipse editorial "Corrientes 9 de Julio-Callao": este solapamiento es la misma
  ambigüedad medida ahora con números concretos.

### MZ_MICROCENTRO_Y_CENTRO — confianza MEDIA
- **Método:** barrio oficial San Nicolás completo (el "microcentro" tradicional).
- **Fuente:** `barrios_caba.geojson`.
- **Límites asumidos:** la ficha PG011 dice "Retiro y área central, sin delimitación
  fina" — este contorno **no incluye Retiro**.
- **Dudas:** ver solapamiento con Avenida Corrientes arriba (mismo problema, desde este
  lado).
- **Qué revisar:** decidir si Retiro necesita su propia macrozona (ya tiene ficha PGF2
  propia, no incorporada a los 12 principales) y resolver el solapamiento con Corrientes.
  763 entidades contenidas (la mayor densidad de las 12: 3,33/ha), 254 cercanas fuera.

## Patrón general de las dudas

Tres problemas se repiten y no son anecdóticos:

1. **Semillas mal geocodificadas** (Chacarita, Costanera Norte, Caseros/Barracas):
   siempre que se intentó "barrio + semilla", una fracción de los puntos de esa fuente
   resultó estar a kilómetros de distancia. Esto es un problema del **universo semilla
   de Fase 13**, no de esta capa — pero esta capa lo hizo visible con datos concretos.
2. **Corredores sin evidencia para calibrar el semiancho** (Costanera Norte,
   Caseros/Barracas, en menor medida Corrientes): el ancho del corredor es una decisión
   editorial pura, no derivada de datos, mientras la evidencia sea escasa.
3. **Fronteras entre macrozonas vecinas sin resolver** (Corrientes/Microcentro, y en
   menor medida Palermo/Costanera Norte): dos contenedores de clustering solapados
   procesan las mismas entidades dos veces — es el hallazgo más urgente de resolver
   antes de usar esta capa en una corrida completa.
