# Mercados gastronómicos en la Ciudad de Buenos Aires

### Relevamiento documental, clasificación y lectura territorial — Versión V2.2 (conservadora)

**DataGastro** · Elaborado por **Diego Aleman** · **Versión V2.2**
**Fecha del informe:** 2026-06-24 · **Fecha de corte de datos:** 2026-06-24

> **Relevamiento documental** y **padrón candidato** con fuentes públicas verificables, fuentes
> internas (DGDGAS), Google Places y documental (Perplexity). **Pendiente de validación
> territorial.** No es un censo definitivo ni un padrón oficial.

---

## 1. Resumen ejecutivo

- Se identificaron **12 mercados gastronómicos activos confirmados para conteo** (10 de sede fija +
  2 itinerantes).
- **3 casos gastronómicos relevantes quedan en revisión** (Mercado Soho, Mercat Caballito,
  El Galpón), retirados del conteo **por prudencia**.
- El relevamiento **combina fuentes públicas, internas, Google Places y documental**, separando
  explícitamente activos, en revisión, cerrados, distritos, abastos no gastronómicos y fuera de
  alcance.
- **No es un censo definitivo ni un padrón oficial.** Los posibles omitidos **no se suman** hasta
  validación.

## 2. Cambio respecto de la versión previa (15 → 12)

Una versión previa (V2) trabajaba con **15 activos**. **V2.2 adopta una lectura conservadora** por
señales de estado operativo: tres casos con indicios de cierre o match dudoso pasan a *en revisión*
en lugar de contarse. Es una **decisión metodológica explícita, transparente y reversible** (no un
descarte), que se presenta como **fortaleza metodológica**: preferimos subreportar con trazabilidad
antes que sobrereportar con casos dudosos. Detalle en
`21_ajuste_conservador_estado_operativo_v2_2.md`.

## 3. Metodología y alcance

- **Inclusión:** la gastronomía/los alimentos/los productores son el eje central.
- **Exclusión:** antigüedades, ropa, shoppings/outlets, supermercados y mayoristas sin experiencia
  gastronómica.
- **Fuentes:** GCBA / Buenos Aires Ciudad, Turismo BA, BA Capital Gastronómica, sitios oficiales de
  los mercados; fuentes internas DGDGAS (solo metadata, sin PII); Google Places (señal operativa);
  documental Perplexity (insumo secundario, solo con URL verificable como fuente final).
- **Niveles de confianza:** C1 oficial · C2 sitio oficial del mercado · C3 multifuente · C4/C5
  auxiliar/pendiente.
- **Regla de conteo:** solo cuentan los mercados en alcance con estado **activo/itinerante** y
  `activo_para_conteo = si`. No suman: en revisión, cerrados, distritos, abastos no gastronómicos
  ni fuera de alcance.

## 4. Universo identificado

| Categoría | Cantidad | Observación |
|---|---|---|
| **Activos para conteo** | **12** | número principal |
| — sede fija | 10 | |
| — itinerantes | 2 | Buenos Aires Market, Sabe la Tierra |
| En revisión (no contabilizados) | 3 | Soho, Mercat Caballito, El Galpón |
| Cerrados documentados | 1 | Mercado de los Carruajes |
| Pendientes metodológicos | 0 | |
| Distritos gastronómicos (no mercado) | 2 | Barrio Chino, Los Arcos del Rosedal |
| Abasto barrial no gastronómico | 3 | Pompeya, Villa Pueyrredón, Primera Junta |
| Fuera de alcance | 2 | Mercado de las Pulgas (= M1), Distrito Arcos |

## 5. Mercados activos para conteo (12)

| Nombre | Tipo | Gestión | Barrio | Comuna | Horario (si confirmado) |
|---|---|---|---|---|---|
| Mercado de San Telmo | identidad histórica | mixta | San Telmo | 1 | pendiente (fuentes divergentes) |
| Mercado de Belgrano | identidad histórica | mixta | Belgrano | 13 | frescos 8:30–20; gastro 11–24 |
| Mercado del Progreso | barrial alimentario | privada | Caballito | 6 | Lun–Vie 7:30–13 y 17–20; Sáb 7:30–14 y 17–20 |
| Mercat Villa Crespo | food hall | privada | Villa Crespo | 15 | Mar–Jue y Dom 12–23; Vie–Sáb 12–01 |
| Patio de los Lecheros | patio gastronómico | pública | Caballito | 6 | Dom–Mié 9–24; Jue 9–2; Vie–Sáb 9–3 |
| Mercado Bonpland | productores | mixta | Palermo | 14 | Mar, Mié, Vie y Sáb 10–19/20 |
| Smart Plaza Parque Patricios | patio gastronómico | pública | Parque Patricios | 4 | Dom–Jue 11–24; Vie–Sáb 11–1 |
| Patio Costanera Norte | patio gastronómico | mixta | Costanera Norte | 13 | Mié 12–19; Jue–Sáb 12–24; Dom 12–21 |
| Patio Gastronómico Rodrigo Bueno | patio gastronómico | pública | Puerto Madero | 1 | Vie–Dom 11–23 |
| Mercado San Nicolás | identidad histórica | mixta | San Nicolás | 1 | mercado 8–18; gastro 11–24 |
| Buenos Aires Market | feria gastronómica | privada | itinerante | — | por sede |
| Sabe la Tierra | productores | privada | itinerante | — | por sede |

**Gestión de los 12:** 3 públicos · 4 privados · 5 mixtos. Validados contra Google (OPERATIONAL) y,
varios, corroborados por fuentes internas DGDGAS (Belgrano, Bonpland, San Nicolás, Progreso).

## 6. Casos en revisión (no contabilizados por prudencia)

| Caso | Señal | Acción |
|---|---|---|
| **Mercado Soho** | Google `CLOSED_PERMANENTLY`; sin evidencia reciente suficiente | validar en terreno / sitio oficial |
| **Mercat Caballito** | Google `CLOSED_PERMANENTLY`; solo mención de evento en fuente oficial | validación externa |
| **El Galpón** | match Google inconsistente (teatro homónimo); situación no clara | desambiguar y validar |

No son fuera de alcance: son **casos gastronómicos relevantes** que vuelven al conteo si se valida
su actividad. Ver `mercados_gastronomicos_en_revision_v2_2.csv`.

## 7. Tipologías (activos)

Identidad histórica (San Telmo, Belgrano, San Nicolás), food hall (Mercat Villa Crespo),
patios gastronómicos (Lecheros, Smart Plaza, Costanera Norte, Rodrigo Bueno), productores
(Bonpland) y feria itinerante / productores (Buenos Aires Market, Sabe la Tierra), más el barrial
alimentario (Progreso). Los food halls privados quedaron más afectados por el ajuste conservador
(Soho y Mercat Caballito en revisión).

## 8. Perfil territorial

Concentración en **Caballito** (Progreso, Lecheros) y **Comuna 1** (San Telmo, San Nicolás,
Rodrigo Bueno); **Palermo** (Bonpland); ribera (Costanera Norte); sur (Smart Plaza, Parque
Patricios). Itinerantes recorren varias comunas. Se mide **volumen documentado**, no densidad.

## 9. Horarios y funcionamiento

Horarios confirmados en la mayoría de los 12; **San Telmo** queda con **fuentes divergentes** (sitio
propio vs Turismo BA) y **Progreso** con una divergencia menor (documental), que **no** se cierra
sin validar. Itinerantes: horario por sede.

## 10. Oferta y público objetivo

Oferta confirmada por fuente en todos los activos. **Turístico:** San Telmo (alto), Belgrano,
Costanera Norte. **Barrial:** Progreso, Lecheros, Smart Plaza, Rodrigo Bueno. **Productores /
consumo consciente:** Bonpland, Sabe la Tierra, Buenos Aires Market.

## 11. Integración documental V2.1 (Perplexity)

El pack documental (insumo secundario) **refuerza fuentes oficiales**, aporta **datos operativos**
(Progreso 17 calle + 174 interiores; Belgrano ~37 locales; San Nicolás 18) y **señala
contradicciones** (horarios de San Telmo y Progreso; Mercat Caballito sin ficha propia; Soho sin
sitio oficial recuperado), que **refuerzan** la decisión conservadora. No cambia el conteo por sí
mismo. Detalle en `20_integracion_documental_v2_1.md`. Donde Perplexity no expuso la URL, se marcó
`url_no_visible_en_export` (pista, no fuente final).

## 12. Casos documentados pero no contabilizados

- **Cerrado:** Mercado de los Carruajes (abril 2025).
- **Distritos gastronómicos (no mercado):** Barrio Chino, Los Arcos del Rosedal.
- **Abasto barrial no gastronómico:** CAM 27 (Pompeya), CAM 116 (Villa Pueyrredón), Primera Junta.
- **Fuera de alcance:** Mercado de las Pulgas (= "Mercado M1"), Distrito Arcos.

## 13. Posibles omitidos (no se suman)

**Pendiente de revisión:** Gourmand Food Hall (alta), Feria del Productor FAUBA, Mercado Punto
Verde, Mercado Fusión (probable feria temporal). **Eventos gastronómicos (no mercado):** Food Fest,
Festival del Sándwich, Sabor a Buenos Aires, Food Fest BA. Ver
`mercados_gastronomicos_posibles_omitidos_v2_2.csv`.

## 14. Hallazgos principales

1. **12 mercados gastronómicos activos confirmados**, con base documental, interna y de Google.
2. La **lectura conservadora** evita sobrereportar: 3 casos con dudas pasan a revisión.
3. **Mercados históricos, productores y patios públicos** sostienen el núcleo confirmado.
4. **Food halls privados** son los más sensibles a la verificación de estado operativo.
5. Persiste la **falta de un registro integrado y actualizado**; las fuentes son dispersas.

## 15. Limitaciones y próximos pasos

- Relevamiento documental; **no valida actividad en campo**; no es padrón oficial.
- **Próximos pasos:** validación territorial de los **3 en revisión** (podrían volver al conteo) y
  de los posibles omitidos prioritarios; recuperar URLs faltantes del documental; resolver
  divergencias de horarios.

## 16. Anexo

- **Bases:** `mercados_gastronomicos_candidatos_v2_2.csv`, `..._activos_v2_2.csv`,
  `..._en_revision_v2_2.csv`, `..._no_contabilizados_v2_2.csv`, `..._posibles_omitidos_v2_2.csv`,
  `fuentes_documentales_mercados_v2_2.csv`, `resumen_relevamiento_mercados_v2_2.csv`,
  y `documental_v2_1/` (pack Perplexity).
- **Privacidad:** sin teléfonos, emails, CUIT/DNI, referentes, place_id ni links privados.
- **Validación técnica:** `src/mercados_caba/validate_mercados_setup.py`.


---

> **Nota V2.3 (2026-06-24):** Se incorporó una tanda V2.3 de URLs visibles de Perplexity para reforzar trazabilidad documental. No modifica conteos (siguen 12 activos confirmados y 3 en revisión); las fuentes con URL truncada quedan pendientes de verificación. Ver `23_integracion_urls_perplexity_v2_3.md`.
