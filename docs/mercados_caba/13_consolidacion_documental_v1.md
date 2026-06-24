# Mercados gastronómicos CABA — Consolidación documental V1

> Mejora de **calidad documental** sobre el padrón candidato V0 (no ampliación por ampliación).
> Fecha de corte: **2026-06-23**. Sin Google Places API, sin API keys, sin datos personales, sin
> inventar: lo no confirmado quedó `pendiente`.

## 1. Qué se hizo

Se revisaron los **16 mercados en alcance** del V0 y los **8 pendientes**, verificando con
fuentes públicas (priorizando sitio oficial del mercado y GCBA/Turismo BA) los campos:
estado operativo, días, horarios, gestión, dirección, oferta y cantidad de puestos. Se
introdujo el control de **estado operativo** para no mezclar mercados activos con cerrados.

## 2. Campos nuevos de control (metodológico)

- `estado_operativo`: `activo` | `cerrado` | `pendiente_verificacion` | `itinerante` | `fuera_de_alcance`.
- `activo_para_conteo`: `si` | `no` — define si suma al total de mercados gastronómicos **activos**.
- `motivo_no_activo`: razón cuando `activo_para_conteo = no` (p. ej. cierre).

Un mercado cerrado se conserva como **antecedente documentado**, pero **no** se cuenta como activo.

## 3. Qué se verificó y confirmó (resumen)

| Campo | Antes (V0) | Ahora (V1) |
|---|---|---|
| Horarios confirmados | ~5 | **11** |
| Direcciones precisas | parcial | casi todas (faltan matices) |
| Gestión confirmada | tentativa | **13** con fuente sólida |
| Estado operativo explícito | no | **sí** (activo/cerrado/itinerante) |

Confirmaciones destacadas con fuente:
- **Mercado del Progreso** — sitio oficial propio (C2): Rivadavia 5430; Lun–Sáb (cerrado domingos);
  gestión **privada** confirmada.
- **Mercado San Nicolás** (GCBA): Av. Córdoba 1750; mercado 8–18 y gastronomía 11–24; 18 locales.
- **Mercado de Belgrano** (GCBA): frescos Lun–Sáb 8:30–20; gastronomía Lun–Dom 11–24.
- **Smart Plaza Parque Patricios** (GCBA): Pepirí 185; Dom–Jue 11–24, Vie–Sáb 11–1; 6 puestos.
- **Patio Rodrigo Bueno** (GCBA/IVC): Av. España 2230; Vie–Dom 11–23; BA Capital Gastronómica.
- **Mercado Bonpland** (Turismo BA/GCBA): Bonpland 1660; Mar–Mié–Vie–Sáb 10–19/20; economía solidaria.
- **El Galpón** (sitio oficial + Turismo BA): Federico Lacroze 4171; Mié y Sáb 9–18; agroecológico.
- **Mercat Caballito** (prensa C3): **abierto** todos los días 10–24 (Shopping Caballito).
- **Mercado de los Carruajes** (GCBA + La Nación): **cerrado** definitivamente en abril 2025.

## 4. Hallazgo de consolidación: equivalencias CAM ↔ mercado

Dos "Centros de Abastecimiento Municipal" del listado de pendientes resultaron ser **mercados ya
en alcance**, renovados y rebrandeados:
- **CAM Nº 72 (Av. Córdoba 1750) = Mercado San Nicolás (MG-0013).**
- **CAM Nº 128 (Av. Juramento 2527) = Mercado de Belgrano (MG-0002).**

Esto evita doble conteo y resuelve 2 de los 8 pendientes.

## 5. Fuentes usadas (prioridad aplicada)

1. **Sitio oficial del mercado** (C2): mercadodelprogreso.com, mercadosoho.com.ar, elgalpon.org.ar,
   mercadosantelmo.com.ar, buenosairesmarket.com, sabelatierra.org.
2. **GCBA / Turismo BA / BA Capital Gastronómica** (C1): fichas oficiales, noticias de
   reinauguración, listado "Mercados y Patios Gastronómicos".
3. **Prensa confiable** (C3) solo como apoyo (Mercat Caballito, cierre de Carruajes, horarios de
   Belgrano).
4. **Auxiliar** (C4): trámite de CAMs (existencia/horarios de abasto), Wikipedia (puestos del Progreso).

Registro completo en `fuentes_mercados_urls_v1.csv`. No se usaron fuentes débiles para
afirmaciones centrales cuando había fuente oficial.

## 6. Límites

Sigue habiendo sesgo hacia mercados emblemáticos/turísticos (mejor documentados). Listado/registro
oficial ≠ operación verificada en terreno. Horarios autodeclarados a contrastar. Itinerantes sin
horario por sede. Detalle de pendientes en `15_decisiones_metodologicas_v1.md` y
`mercados_gastronomicos_pendientes_v1.csv`.
