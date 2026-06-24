# Mercados gastronómicos CABA — Integración de URLs visibles de Perplexity (V2.3)

> Tanda documental V2.3: refuerza **trazabilidad documental** con URLs visibles. **No cambia el
> conteo** ni la decisión conservadora V2.2. Fecha: 2026-06-24. Sin requests, sin API keys.

## 1. Qué se integró

Se procesaron **19 fuentes** provistas por Perplexity (texto plano con URLs). El crudo se guardó en
`outputs/mercados_caba/internal/perplexity_raw/perplexity_fuentes_urls_completas_mercados_2026_06_24.md`
(**interno, gitignored, no va al pack**). Las fuentes procesadas viven en:

- `fuentes_documentales_mercados_v2_3.csv` (matriz de fuentes, con `estado_url`).
- `afirmaciones_mercados_v2_3.csv` (afirmación por fuente, con `usar_en_informe`).
- `contradicciones_y_brechas_v2_3.csv` (divergencias y decisiones).
- `fuentes_url_truncadas_requieren_verificacion_v2_3.csv` (URLs incompletas).

## 2. URLs completas vs. truncadas

- **16 fuentes con URL completa** (`url_completa_visible`): Clarín y El Cronista (Mercat Caballito),
  sitio propio de San Telmo, Turismo BA (San Telmo EN, Progreso, San Nicolás, Soho, Gastronomía),
  GCBA (Mercados de la Ciudad, Lecheros ×2, Smart Plaza), Argentina.gob.ar (Bonpland),
  Radio Hache (cierre Carruajes), Boletín Oficial (Disposición 205/2024) y el Pliego GCBA.
- **3 fuentes con URL truncada** (`url_truncada_requiere_verificacion`): **TN** (Mercado Soho),
  **Infobae** y **El Trece/Cucinare** (Mercado de los Carruajes). **No se usan como fuente final**
  hasta recuperar la URL completa.

## 3. Qué refuerza (sin cambiar el conteo)

- **Fuentes oficiales** para mercados activos: Lecheros (incl. nota 2026 "cumple 5 años" →
  estado activo reciente), Smart Plaza, San Nicolás (2025), Bonpland (gestión cooperativa),
  Progreso y "Mercados de la Ciudad" (multi-mercado).
- **Contexto normativo de gestión:** Disposición 205/2024 de la DG de Concesiones y Permisos y un
  Pliego GCBA, que **respaldan el modelo de concesión** (refuerza las clasificaciones "mixta").

## 4. Contradicciones reforzadas

| Caso | Conflicto | Decisión | Impacto en conteo |
|---|---|---|---|
| **San Telmo** | horarios sitio propio vs Turismo BA | fuentes divergentes, no cerrar uno | ninguno |
| **Progreso** | horarios GCBA general vs ficha Turismo BA | marcar divergencia, validar | ninguno |
| **Mercado Soho** | fuentes 2021/2024 (existencia) vs Google 2026 (cierre) | **mantener en revisión** | ninguno |
| **Mercat Caballito** | fuentes 2021/2022 (apertura) vs Google 2026 (cierre) | **mantener en revisión** | ninguno |
| **Mercado de los Carruajes** | apertura 2022 vs cierre 2025 | **mantener cerrado documentado** | ninguno |

Las notas de apertura de Soho y Mercat Caballito son **antecedentes**, no estado actual: **no
revierten** la señal de cierre reciente. Por eso **siguen en revisión**.

## 5. Reglas de conteo (sin cambios)

- **12 mercados gastronómicos activos confirmados para conteo.**
- **3 casos en revisión** (Mercado Soho, Mercat Caballito, El Galpón).
- **1 cerrado documentado** (Mercado de los Carruajes).
- **No se sumó ningún candidato** por estas fuentes. **0 pendientes metodológicos.**

## 6. Privacidad

Sin teléfonos, emails, CUIT/DNI, referentes, place_id ni links privados. Las URLs son públicas
(medios y organismos). El crudo de Perplexity queda en interno gitignored y **no** se incluye en el
pack.
