# Mercados gastronómicos CABA — Plan de relevamiento

> Hoja de ruta por etapas para el informe de **mercados gastronómicos**. Cada etapa termina en un
> gate de aprobación. Esta etapa deja preparado el método; **no** ejecuta integraciones externas.
> En cada etapa se aplica primero el filtro de alcance gastronómico (`00_vision_y_objetivo.md`).

## Etapa A — Anclas oficiales locales (hecha en preparación)
- Leer F03 (mercados/ferias) y `fact_espacio_feria_mercado` (V1, solo lectura).
- Salida: `mercados_candidatos_iniciales.csv` con 7 registros: 5 con foco alimentario a revisar
  (4 CAM + Mercado Comunitario Primera Junta, `revisar_foco_gastronomico`), 1 dudoso (M1) y
  1 **fuera de alcance** (Mercado de las Pulgas, antigüedades/usados). Campos faltantes =
  `pendiente`. Los CAM se incluyen como candidatos a verificar, no como mercados gastronómicos
  confirmados.

## Etapa B — Fuentes oficiales a relevar (con aprobación)
- BA Data: buscar dataset directo de mercados/food halls.
- Turismo BA / buenosaires.gob.ar: fichas de mercados emblemáticos y con perfil turístico.
- BA Capital Gastronómica: contexto de política pública.
- Registrar cada fuente con ficha (título, URL, fecha). No inventar URLs.

## Etapa C — Externas auxiliares (plan, no ejecución)
- OSM por Overpass (`08_plan_osm_mercados.md`): `amenity=marketplace`, `food_court`, etc.
- Google Places (`07_plan_google_places_mercados.md`): queries por rubro/barrio, topado y con
  presupuesto aprobado. Separar mercado real de supermercado/shopping/feria temporal.

## Etapa D — Documental (sitios oficiales + prensa)
- Sitios y redes oficiales de cada mercado: horarios, días, oferta (autodeclarados, a contrastar).
- Prensa con autoría y fecha para casos e historia.
- Perplexity solo como **localizador** (`06_prompt_perplexity_mercados.md`); sin URL verificable,
  no entra.

## Etapa E — Internas DGDGAS (metadata/agregados)
- Usar señales internas ("PATIO Y MERCADOS", "BUENOS AIRES MARKET") como contexto de
  eventos/activaciones en mercados. Solo agregados, sin PII.

## Etapa F — Revisión manual
- Resolver foco gastronómico (`revisar_foco_gastronomico`, `dudoso_pendiente_revision`),
  tipología, gestión y desambiguación (food hall vs shopping/patio de comidas, mercado de
  productores vs feria de pulgas/antigüedades, mercado alimentario vs supermercado/mayorista).
- Confirmar `fuera_de_alcance_no_gastronomico` solo con evidencia de que la gastronomía es
  accesoria o inexistente.

## Etapa G — Validación territorial posterior
- Confirmar estado operativo, oferta y horarios en terreno. Sube fichas a confianza `alto`.

## Resolución de duplicados
- Deduplicar por nombre normalizado + dirección/zona + barrio (heurística conservadora, estilo
  DataGastro). No fusionar mercados distintos del mismo barrio sin evidencia.

## Orden recomendado
```text
A (hecho) -> B y D (sin costo) -> E -> C/Google (con presupuesto) -> F -> G
```

## Qué NO hace esta etapa
- No descarga, no consulta APIs, no usa Perplexity, no expone PII, no completa el universo.
