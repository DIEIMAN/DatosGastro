# Mercados gastronómicos CABA — Cierre fino V1.2

> Etapa corta de calidad: cerrar gestión tentativa y resolver los 4 pendientes. **No** se amplió
> el universo. Fecha de corte: 2026-06-23. Sin Google Places API, sin API keys, sin datos
> personales, sin inventar.

## 1. Gestión tentativa cerrada

- **Mercado de San Telmo → mixta (confirmada).** El inmueble es **patrimonial municipal**
  (restauración y administración de bienes a cargo de GCBA; monumento histórico), con **puestos
  privados**. Fuentes: GCBA Descubrir BA, Argentina.gob.ar (monumentos). Horarios siguen
  `pendiente` (las fuentes públicas difieren ~9–22); se mantiene declarado.
- **Patio Costanera Norte → mixta (confirmada) + horarios confirmados.** Es un **espacio público
  GCBA con concesión gastronómica privada**. Días/horarios: **Mié 12–19; Jue–Sáb 12–24; Dom
  12–21** (Av. Costanera Rafael Obligado 7010; 546 m², ~150 personas). Fuentes: GCBA Desarrollo
  Económico, Turismo BA.

No quedan gestiones "tentativas" abiertas (solo matices menores del modelo de Bonpland).

## 2. Pendientes resueltos (4 de 4)

| Caso | Decisión | Categoría final | ¿Cuenta como activo? |
|---|---|---|---|
| **CAM 27 / Mercado Pompeya** | documentar_como_abasto_no_gastronomico | mercado_barrial_alimentario | **No** |
| **CAM 116 / Villa Pueyrredón** | documentar_como_abasto_no_gastronomico | mercado_barrial_alimentario | **No** |
| **Mercado Comunitario Primera Junta** | documentar_como_abasto_no_gastronomico | mercado_barrial_alimentario | **No** |
| **Mercado M1** | fuera_de_alcance_no_gastronomico | mercado_de_antigüedades | **No** |

Detalle:
- **Mercado Pompeya (CAM 27)**: mercado municipal de abasto barrial (Av. Sáenz 790; Lun–Sáb 8–19,
  Dom 8–12). Tiene rubros alimentarios y algunos de comida (panadería, heladería, confitería),
  pero **no** es un polo/experiencia gastronómica → se documenta como abasto, no se cuenta.
- **Villa Pueyrredón (CAM 116)**: mercado municipal de abasto en el Barrio Grafa (Ezeiza 2885;
  Lun–Sáb 8–19), con rubros no alimentarios (limpieza, librería, etc.) → abasto, no se cuenta.
- **Primera Junta**: centro de abastecimiento municipal de 11 locales en calle Rojas. Se confirma
  que es **distinto del Mercado del Progreso** (Rivadavia/Centenera). Abasto barrial → no se cuenta.
- **Mercado M1**: "M1" es el **nombre administrativo del predio del Mercado de las Pulgas**
  (Álvarez Thomas y Dorrego; antigüedades y usados). Es el **mismo sitio** ya listado fuera de
  alcance → fuera de alcance (no es un sitio nuevo).

**No se forzó ninguna inclusión para inflar el número.**

## 3. Efecto en los conteos

El total de **mercados activos para conteo no cambió: sigue en 15** (13 fijos + 2 itinerantes). El
cierre fino reclasificó pendientes en **abasto no gastronómico (3)** y **fuera de alcance (M1 =
Pulgas)**, dejando **0 pendientes**. Mejoró la calidad documental (gestión y horarios), no la
cantidad.

## 4. Fuentes nuevas usadas

- GCBA sección **Mercados** (`/mercados/...`): Pompeya, Primera Junta, Pulgas.
- GCBA Espacio Público — **Mercado de Villa Pueyrredón**.
- GCBA Desarrollo Económico y **Turismo BA** — Patio Costanera Norte.
- GCBA Descubrir BA + **Argentina.gob.ar** (monumentos) — gestión de San Telmo.

Registro en `fuentes_mercados_urls_v1_2.csv`. Sin fuentes débiles para afirmaciones centrales.

## 5. Límites

San Telmo conserva horarios `pendiente` (fuentes difieren). Ningún caso alcanza confianza "alto"
por verificación territorial. Los mercados de abasto documentados podrían reevaluarse si en el
futuro suman un polo gastronómico.
