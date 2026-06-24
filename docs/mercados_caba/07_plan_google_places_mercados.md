# Mercados gastronómicos CABA — Plan Google Places (no ejecución)

> **Plan, no ejecución.** No se llama a la API, no se usa API key, no hay requests. Sigue los
> guardrails de DataGastro V2 (`docs/datagastro_v2/04_plan_integracion_google_places.md`).

## 1. Encuadre

- Google Places es **señal operativa no oficial**: cobertura amplia, `businessStatus`, tipos.
  No es registro oficial. Solo **API oficial**, nunca scraping de Google Maps.
- Objetivo acotado: **mercados gastronómicos** (food halls, mercados de productores/alimentos,
  ferias gastronómicas). Los resultados sin eje gastronómico se descartan o se marcan fuera de
  alcance.
- Requiere **aprobación + presupuesto confirmado + topes** antes de cualquier ejecución.

## 2. Guardrails (obligatorios)
```text
- API key solo desde variable de entorno; nunca impresa, logueada ni commiteada.
- Modo dry-run por defecto; sin --run no hay request real.
- Topes duros (--max-queries, --max-results) que abortan si se exceden.
- Brutos a outputs/mercados_caba/internal/ o raw/ (GITIGNORED).
- Entregables: solo agregados sanitizados, sin place_id/teléfono/dirección individual.
```

## 3. Queries candidatas (Text Search) — foco gastronómico
```text
mercado gastronómico CABA
mercado de comidas CABA
food hall Buenos Aires
mercado de productores CABA
mercado gourmet Buenos Aires
mercado gastronómico {barrio} CABA
feria gastronómica CABA
mercado de alimentos CABA
mercado con puestos de comida CABA
mercado orgánico CABA
```
`{barrio}` se expande con los 48 barrios oficiales de CABA (grilla territorial, por lotes
topeados).

### Términos a excluir / descartar en post-proceso
```text
flea market
mercado de pulgas
shopping
supermercado
galería comercial
feria de ropa
feria de antigüedades
```
Si el `displayName` o los `types` matchean estos términos sin señal gastronómica, el resultado se
descarta (conservado en bruto interno) o se marca `fuera_de_alcance_no_gastronomico`.

## 4. Campos mínimos (primera pasada)
`id`, `displayName`, `formattedAddress`, `location`, `businessStatus`, `types`. (Sin `rating`,
`reviews`, `phone`, `website` en la primera pasada: mayor costo.)

## 5. Criterios de separación (clasificación conservadora)

| Resultado | Acción |
|---|---|
| **mercado gastronómico real** (público/privado/mixto/productores/food hall) | candidato |
| feria gastronómica / de productores de alimentos | candidato |
| supermercado | `fuera_de_alcance_no_gastronomico` (conservado) |
| galería comercial / shopping | `fuera_de_alcance_no_gastronomico` (conservado) |
| mercado de pulgas / antigüedades / ropa / artesanías | `fuera_de_alcance_no_gastronomico` (conservado) |
| feria general sin foco alimentario | `fuera_de_alcance_no_gastronomico` (conservado) |
| restaurante individual fuera de un mercado | descartar (conservado) |
| mayorista sin experiencia gastronómica | `fuera_de_alcance_no_gastronomico` (conservado) |
| mercado de abasto con posible oferta de comida | `dudoso_pendiente_revision` (verificar foco) |
| espacio fuera de CABA | descartar (fuera de área) |

Señales: términos gastronómicos del nombre (fuerte: "mercado gastronómico", "food hall",
"mercado de comidas/productores/alimentos") + `types` de Google (débil) + ubicación dentro de
polígonos CABA. Solo entra si hay **señal de eje gastronómico/alimentario**. Ante señales mixtas →
`dudoso_pendiente_revision`; ante eje claramente no gastronómico → `fuera_de_alcance_no_gastronomico`.

## 6. Deduplicación
Por `place_id` (intra-Google) y, contra otras fuentes, por nombre+dirección normalizados +
distancia (heurística conservadora). Coincidir con F03/OSM **sube** confianza.

## 7. Costo y control
Estimación de **orden de magnitud** a confirmar contra el pricing vigente de Google y el crédito
gratuito **antes** de ejecutar. Siempre por lotes topeados, nunca una corrida masiva.

## 8. Estado
Diseño versionable (sin API key ni datos sensibles). Ejecución **bloqueada** hasta aprobación.
