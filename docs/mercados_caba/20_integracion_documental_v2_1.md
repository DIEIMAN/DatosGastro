# Mercados gastronómicos CABA — Integración del pack documental V2.1

> Integración del pack documental (respuestas de Perplexity, armado externo) como **insumo
> secundario**. Fecha: 2026-06-24. **No cambia el conteo automáticamente.** Sin requests nuevas,
> sin datos sensibles.

## 1. Qué se integró

El ZIP `PACK_MERCADOS_DOCUMENTAL_PERPLEXITY_V2_1.zip` se extrajo (de forma segura, sin rutas
absolutas ni traversal) a `outputs/mercados_caba/sanitized/documental_v2_1/`. Contiene:

- `fuentes_documentales_mercados_v2_1.csv` — matriz de fuentes y afirmaciones.
- `afirmaciones_mercados_v2_1.csv` — afirmaciones campo por campo.
- `contradicciones_y_brechas_v2_1.csv` — divergencias y decisiones recomendadas.
- `posibles_omitidos_documentales_v2_1.csv` — pistas de omitidos / eventos.
- `resumen_narrativo_documental_v2_1.md` y `README_MERCADOS_DOCUMENTAL_V2_1.md`.

**Escaneo de privacidad:** sin emails, teléfonos, CUIT, place_id, API keys ni links privados.

## 2. Qué aportó Perplexity (documental)

1. **Refuerzo de fuentes oficiales** GCBA/Turismo BA para Belgrano, San Nicolás, Bonpland,
   Lecheros, Smart Plaza Parque Patricios, Costanera Norte y Rodrigo Bueno.
2. **Datos operativos parciales** (integrados a `fuentes_documentales_mercados_v2_2.csv`):
   - **Mercado del Progreso:** 17 negocios a la calle + 174 puestos interiores.
   - **Mercado de Belgrano:** ~37 locales, horarios diferenciados.
   - **Mercado San Nicolás:** 18 puestos/locales (consistente con GCBA).
3. **Pistas de posibles omitidos:** Gourmand Food Hall y Mercado Fusión, además de varios eventos.

## 3. Fuentes con URL visible vs. no visible

En el export de Perplexity **varias URLs aparecen solo como `Link`**. Esas filas se integraron con
`url_no_visible_en_export` y **nivel de confianza bajo (C4/C5)**: sirven como pista, **no** como
fuente final. No se inventaron URLs.

## 4. Contradicciones y brechas que suma

- **San Telmo — horarios:** sitio propio (Lun–Dom 9–20) vs. Turismo BA EN (Mar–Vie 10:30–19:30;
  Sáb/Dom/feriados 9–20). → mantener "fuentes divergentes".
- **Progreso — horarios:** 8–14 vs. 8–18. → marcar divergencia; no modificar sin validar.
- **San Telmo (mercado) ≠ Feria de San Telmo** (antigüedades): entidades separadas; la feria queda
  fuera de alcance gastronómico.
- **Mercat Caballito:** la fuente oficial recuperada es una **mención en agenda/evento**, sin ficha
  propia con dirección/horario. → **refuerza** la decisión de pasarlo a *en revisión*.
- **Mercado Soho:** Turismo BA aporta perfil/oferta, pero dirección/horario solo desde prensa; sin
  sitio oficial recuperado. → **refuerza** la decisión de pasarlo a *en revisión*.

## 5. Posibles omitidos documentales

- **Gourmand Food Hall** (prioridad alta; dentro de Patio Bullrich — validar entidad propia).
- **Mercado Fusión** (prioridad media-alta; probable feria/evento temporal).
- **Eventos gastronómicos (no mercado):** Food Fest 2026, Festival del Sándwich, Sabor a Buenos
  Aires, Food Fest BA → a derivar a agenda de eventos, **no** al padrón de mercados.

Todos quedan en `mercados_gastronomicos_posibles_omitidos_v2_2.csv`, **sin** sumarse al conteo.

## 6. Por qué no cambia automáticamente el conteo

El pack documental es un **insumo secundario**: refuerza fuentes y revela contradicciones, pero
no constituye validación territorial. Su efecto es **cualitativo** (mejor trazabilidad y señales
para revisión), no cuantitativo. El ajuste del conteo (V2.2) se decide por criterio metodológico
explícito (ver `21_ajuste_conservador_estado_operativo_v2_2.md`), apoyado en señales de estado
operativo, no por el solo hecho de integrar el pack.


---

> **Nota V2.3 (2026-06-24):** Se incorporó una tanda V2.3 de URLs visibles de Perplexity para reforzar trazabilidad documental. No modifica conteos (siguen 12 activos confirmados y 3 en revisión); las fuentes con URL truncada quedan pendientes de verificación. Ver `23_integracion_urls_perplexity_v2_3.md`.
