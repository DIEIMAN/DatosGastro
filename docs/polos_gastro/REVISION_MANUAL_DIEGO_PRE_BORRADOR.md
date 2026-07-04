# Revisión manual de Diego — pre borrador PolosGastro

Fecha: 2026-06-29.

Paquete de revisión para decidir si se pasa a **Fase 5: primer borrador Markdown**. Reúne en un
solo lugar los visuales, los matches de Google Places a revisar y las URLs pendientes, para que
no haya que buscar archivo por archivo. **No hay mapas nuevos, ni PDF, ni cambios de universo.**

---

## 1. Qué revisar antes del borrador

Esta revisión decide si el proyecto puede avanzar a **Fase 5 (primer borrador en Markdown, sin
PDF)**. Hay tres bloques a mirar:
1. **Visuales Fase 4A** — confirmar cuáles entran al informe.
2. **Google Places** — revisar los matches de baja/media confianza del piloto.
3. **URLs pendientes** — decidir qué bloquea y qué no.

Al final hay una lista de **decisiones** y el **próximo prompt** sugerido.

---

## 2. Visuales Fase 4A para abrir

Todos en `outputs/polos_gastro/graficos/fase4a/`.

### `mapa_estatico_caba_polos_gastro_v1.png`
Mapa territorial real de CABA (barrios oficiales) con núcleo + relevantes + candidatos. Mirar:
que los barrios resaltados y las etiquetas combinadas (Palermo, Villa Urquiza/DoHo) se entiendan.
- [ ] Se entiende.  [ ] Se ve prolijo.  [ ] Sirve para informe.  [ ] Solo sirve interno.  [ ] Hay que rediseñar.

### `mapa_estatico_caba_polos_gastro_nucleo_v1.png`
Versión limpia: solo núcleo + zonas relevantes. Candidata para el cuerpo del informe. Mirar:
legibilidad y que la nota metodológica sea visible.
- [ ] Se entiende.  [ ] Se ve prolijo.  [ ] Sirve para informe.  [ ] Solo sirve interno.  [ ] Hay que rediseñar.

### `mapa_conceptual_polos_gastro_resumido_v2.png`
Esquema conceptual (núcleo + relevantes + candidatos), sin solapes. Mirar: que las etiquetas no
se encimen y que la nota roja se vea.
- [ ] Se entiende.  [ ] Se ve prolijo.  [ ] Sirve para informe.  [ ] Solo sirve interno.  [ ] Hay que rediseñar.

### `mapa_conceptual_polos_gastro_completo_v2.png`
Esquema con todo el universo salvo "no incluir". Más denso. Mirar: si sirve para anexo o solo
interno.
- [ ] Se entiende.  [ ] Se ve prolijo.  [ ] Sirve para informe.  [ ] Solo sirve interno.  [ ] Hay que rediseñar.

### `familias_territoriales_polos_v2.png`
Barras agrupadas por familia y grupo. Mirar: que se comparen bien las familias.
- [ ] Se entiende.  [ ] Se ve prolijo.  [ ] Sirve para informe.  [ ] Solo sirve interno.  [ ] Hay que rediseñar.

### `universo_polos_por_grupo_v2.png`
Cantidad de polos por grupo (6/5/9/8/4). Mirar: claridad general.
- [ ] Se entiende.  [ ] Se ve prolijo.  [ ] Sirve para informe.  [ ] Solo sirve interno.  [ ] Hay que rediseñar.

### `precision_delimitacion_polos_v2.png`
Precisión de delimitación (3/11/16/2), escala ordinal. Mirar: que se lea como escala.
- [ ] Se entiende.  [ ] Se ve prolijo.  [ ] Sirve para informe.  [ ] Solo sirve interno.  [ ] Hay que rediseñar.

---

## 3. Revisión de Google Places

Fuente: `outputs/polos_gastro/experimentos_google_places/locales_places_piloto_resultados.csv`.
El piloto fue **experimental** (10 locales de Palermo, 10 matches). Aquí están solo los **4 de
confianza baja/media** que conviene revisar. Los 6 de confianza alta (Don Julio, Niño Gordo,
Gran Dabbang, Mishiguene, La Mar, Cosi Mi Piace) no se listan: se consideran correctos.

> En `decision_manual`, opciones: `aceptar_match` · `rechazar_match` · `revisar_manual` · `no_usar_places`.

| local_id | nombre_local | nombre_polo | query_busqueda | nombre_google | direccion_google | business_status | match_confidence | observaciones | decision_manual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LG002_LA_CABRERA | La Cabrera | Palermo (Soho, Hollywood y Las Cañitas) | La Cabrera, Palermo, CABA, Argentina | La Cabrera Buenos Aires | José A. Cabrera 5100, C1414BGR CABA | OPERATIONAL | media | Probable match correcto (nombre extendido). | _(a completar)_ |
| LG006_OSAKA | Osaka | Palermo (Soho, Hollywood y Las Cañitas) | Osaka, Palermo, CABA, Argentina | Osaki Sushi Palermo | Gorriti 4977, C1414 CABA | OPERATIONAL | baja | Posible falso positivo ("Osaki" ≠ "Osaka"). | _(a completar)_ |
| LG008_ALDOS_PALERMO | Aldo's (Palermo) | Palermo (Soho, Hollywood y Las Cañitas) | Aldo's (Palermo), Palermo, CABA, Argentina | Artemisia | Costa Rica 5893 Esquina, Dr. Emilio Ravignani, C1414 CABA | OPERATIONAL | baja | Probable falso positivo (nombre distinto). | _(a completar)_ |
| LG010_OPORTO | Oporto | Palermo (Soho, Hollywood y Las Cañitas) | Oporto, Palermo, CABA, Argentina | Alto Palermo Shopping | Av. Sta. Fe 3253, C1091 CABA | OPERATIONAL | baja | Probable falso positivo (devolvió un shopping). | _(a completar)_ |

> Recomendación general: tratar Osaka, Aldo's y Oporto como `revisar_manual`/`rechazar_match`;
> La Cabrera probablemente `aceptar_match`. En cualquier caso, **no usar Places en el informe**
> todavía (validación experimental interna).

---

## 4. URLs pendientes / requiere revisión

### URLs sin fuente verificable (universo)

| Polo | Fuente | Grupo | ¿Bloquea informe? | Recomendación |
| --- | --- | --- | --- | --- |
| Federico Lacroze / Libertador a Cabildo | PX023A, PX023B (sin fuente) | no_incluir_por_ahora | No bloquea | Mantener fuera; ya está como "no incluir". |
| Parque Saavedra / García del Río | PX024B (sin fuente) | anexo | No bloquea | Mantener en anexo con prudencia. |
| Paternal | PX025A (sin fuente) | emergente_o_candidato | No bloquea | Mantener como candidato débil. |

### Fuentes manuales con `requiere_revision_url`

| ID | Polo | Fuente | URL | ¿Bloquea? | Recomendación |
| --- | --- | --- | --- | --- | --- |
| CM005 | Barrio Chino | GCBA histórico | buenosaires.gob.ar/gcaba_historico/noticias/como-recorrer-la-ciudad-dia-por-dia | No | Verificar URL antes de citar; subzona de Belgrano. |
| CM006 | Chacarita | Clarín Gourmet | clarin.com/gourmet/chacarita-…-newbery | No | clarin.com no abrió; verificar manual. Chacarita ya tiene otras fuentes. |
| CM010 | Federico Lacroze | Clarín (antigua) | clarin.com/ciudades/Federico-Lacroze-… | No | Fuente antigua; no elevar. |
| CM011 | Parque Saavedra / García del Río | Clarín Gourmet | clarin.com/gourmet/bulevar-garcia-rio-… | No | Verificar URL; sostiene el paso a anexo. |
| CM012 | Paternal | TimeOut | timeout.com/…/escena-gastronomica-…-2026 | No | Mención genérica; evidencia débil. |

> **Ninguna URL bloquea el informe.** Todas afectan a polos que ya están en su grupo correcto
> (no incluir / anexo / emergente). Son verificaciones para nota al pie, no para reclasificar.

---

## 5. Decisiones que tiene que tomar Diego

1. **¿Usar mapa territorial estático real en el informe?** — Recomendación: **sí**, con nota
   metodológica (barrios = referencia, no delimitación de polos).
2. **¿Usar mapa conceptual resumido?** — Recomendación: **sí**, si visualmente está claro.
3. **¿Usar mapa conceptual completo?** — Recomendación: **solo interno/anexo** si no satura.
4. **¿Usar Google Places en el informe?** — Recomendación: **no todavía**; solo validación
   experimental interna.
5. **¿Pasar a Fase 5?** — Recomendación: **sí**, si los visuales principales están aprobados.

| Decisión | Recomendación | Resolución de Diego |
| --- | --- | --- |
| Mapa territorial estático | Sí, con nota | _(a completar)_ |
| Mapa conceptual resumido | Sí | _(a completar)_ |
| Mapa conceptual completo | Solo interno/anexo | _(a completar)_ |
| Google Places en informe | No todavía | _(a completar)_ |
| Pasar a Fase 5 | Sí | _(a completar)_ |

---

## 6. Próximo prompt recomendado

> **Fase 5 — primer borrador Markdown, sin PDF**, usando los visuales aprobados en esta revisión
> y manteniendo prudencia metodológica: universo defendible (no padrón), barrios como referencia
> (no delimitación de polos), separar hallazgos de límites, y dejar Google Places como validación
> experimental interna. Seguir la estructura de `PLAN_ENSAMBLADO_INFORME_POLOS_GASTRO.md`.

> Resumen accionable también en `outputs/polos_gastro/revision_manual_pre_borrador.csv`.
