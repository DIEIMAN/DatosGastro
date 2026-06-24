# Mercados gastronómicos CABA — Enriquecimiento V2 (Google Places, fuentes internas, documental)

> Etapa de **enriquecimiento** sobre la base V1.2. Objetivo: mejorar cobertura, validar
> información y detectar posibles omitidos **sin inflar el número**. Fecha: 2026-06-24.
> Sin commit, sin push, sin exponer datos sensibles, sin API keys en código ni outputs.

## 1. Estado de la etapa

Etapa **ejecutada**: se corrió el inventario interno (119 archivos) y Google Places en modo `run`
(con key cargada en `.env`, gitignored). Perplexity/documental quedó sembrado con fuentes ya
verificadas, listo para ampliarse.

## 2. Qué aportaron las fuentes internas (DGDGAS)

- **119 archivos** leídos de `fuentes_internas_mercados_caba/` (solo metadata; sin copiar
  contactos, teléfonos, emails, CUIT ni links privados). **1 archivo** se marcó
  `sensible_no_usar` y no se exporta su contenido.
- Clasificación: **40 `mercados_gastronomicos`**, 7 `programas`, 4 `gestion_concesiones`,
  1 `eventos`, 1 `prensa_comunicacion`, 65 `dudoso`.
- **Corroboran 4 de los 15 activos** por nombre de archivo: **Mercado de Belgrano (9 archivos),
  Mercado Bonpland (7), Mercado San Nicolás (3), Mercado del Progreso (1)**.
- Hay listados maestros internos ("BASE DE DATOS - MERCADOS Y PATIOS", "LISTADO MERCADOS Y PATIOS",
  "MERCADOS Y PATIOS DE LA CIUDAD…") útiles para cruces futuros (no se leyó su contenido en esta
  etapa para no exponer datos).
- Salidas: `fuentes_internas_mercados_resumen_v2.csv` y `candidatos_mercados_fuentes_internas_v2.csv`
  (sanitizadas); inventario completo en interno gitignored.

## 3. Qué aportó Google Places

- **Modo `run` ejecutado.** Primero **prueba de 5 queries** (sin errores tras corregir el
  `locationBias`), luego **corrida limitada de 25 queries** (15 validación + 10 descubrimiento).
- **25 queries ejecutadas, 0 errores, 98 resultados.** **Costo estimado ~USD 0.80** (orden de
  magnitud, ~0.032/req; más ~0.16 de la prueba; **confirmar contra pricing vigente**).
- **Los 15 activos aparecen en Google** (15/15 matches por nombre).
- **Discrepancias de estado (a validar, NO se cambia el conteo):**
  - **Mercado Soho** y **Mercat Caballito** figuran **`CLOSED_PERMANENTLY`** en Google, contra el
    sitio propio / prensa que los daban activos. Quedan marcados `validar_cierre_google`.
  - **El Galpón**: Google devolvió un **teatro/`event_venue` homónimo** en Chacarita; el match es
    dudoso (`revisar_match_google`).
- Outputs: `google_places_matches_v1_2.csv`, `google_places_posibles_omitidos_v2.csv`,
  `google_places_mercados_resumen_v2.csv` (**sin `place_id`, teléfono, email ni dirección
  individual**). Crudos JSON y staging con `place_id` quedan en interno **gitignored**.

## 4. Qué aportó la búsqueda documental / Perplexity

`18_prompts_perplexity_enriquecimiento_v2.md` (10 prompts) y
`fuentes_documentales_mercados_v2.csv` con **17 fuentes oficiales ya verificadas** (V1.2). No se
hizo búsqueda web nueva; la tabla queda lista para ampliarse con resultados de Perplexity (solo con
URL verificable).

## 5. Qué validó sobre los 15 activos

- **Presencia en Google: 15/15.** 13 `OPERATIONAL`; 2 con discrepancia de cierre (Soho, Mercat
  Caballito); 1 match dudoso (El Galpón).
- **Web oficial:** 6 con sitio propio, 9 institucional, 1 sin web (Mercat Caballito).
- **Horarios confirmados:** 12/16 (sin cambios respecto de V1.2).
- **Corroboración interna:** 4 activos confirmados en fuentes DGDGAS.

## 6. Posibles omitidos detectados

**7 `posible_omitido_pendiente_revision`** (de Google), que **NO se suman al conteo**:
Gourmand Food Hall, Feria del Productor al Consumidor (FAUBA), Mercado Punto Verde, Lo Simple
Mercado Natural, Feria Leer y Comer, Andes Mercado, Le marché. Además, **2 detecciones resultaron
ya conocidas**: *Mercado Primera Junta* (abasto no gastronómico, NC-0006) y *Patio Parque
Patricios* (= Smart Plaza, MG-0010). El resto fue ruido (grocery, bazar, online, mayorista).
Ver `mercados_gastronomicos_posibles_omitidos_v2.csv`.

## 7. Cambios respecto de V1.2

- **El conteo principal NO cambió: 15 mercados gastronómicos activos para conteo** (13 fijos + 2
  itinerantes), 1 cerrado, 0 pendientes, 2 distritos, 3 abastos no gastronómicos, 2 fuera de
  alcance.
- Se **validaron los 15 activos contra Google** y se **corroboraron 4 con fuentes internas**.
- Se **registraron 2 discrepancias de cierre** (Soho, Mercat Caballito) y **1 match dudoso**
  (El Galpón) para validación territorial; **no** se modificó el conteo por una sola fuente.
- Se sumaron **7 posibles omitidos** en revisión, sin incorporarlos.

## 8. Qué queda pendiente antes del informe final V2

1. **Validar en terreno / fuente oficial** el estado de **Mercado Soho** y **Mercat Caballito**
   (discrepancia Google ↔ sitio/prensa).
2. **Resolver el match de El Galpón** (mercado orgánico vs teatro homónimo).
3. **Revisar los 7 posibles omitidos** con fuente oficial antes de decidir inclusión.
4. **Leer (con cuidado de PII) los listados maestros DGDGAS** para detectar omitidos adicionales.
5. **Resolver horarios de San Telmo** y los itinerantes (por sede).

## 9. Privacidad y seguridad

- API key **solo** desde entorno/`.env` (gitignored); **nunca** impresa ni escrita en outputs.
  Se acepta `GOOGLE_PLACES_API_KEY` o `GOOGLE_MAPS_API_KEY`.
- Crudos de Google en `outputs/mercados_caba/internal/google_places_raw/` y staging con `place_id`
  en interno; **gitignored**. Fuentes internas en `fuentes_internas_mercados_caba/` (gitignored).
- Outputs sanitizados **sin** `place_id`, teléfonos, emails, CUIT/DNI, referentes ni links privados.
