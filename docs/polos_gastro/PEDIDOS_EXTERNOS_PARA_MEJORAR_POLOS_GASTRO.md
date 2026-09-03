# Pedidos externos para mejorar PolosGastro

> **Actualización del 27 de agosto de 2026.** Para los pedidos institucionales a AGC e IDECBA
> usar el paquete vigente en
> `docs/polos_gastro/pedidos_institucionales_padron_2026-08-27/`. Allí se distingue lo ya
> publicado de la información que todavía requiere intercambio entre áreas. La lista que sigue
> conserva su valor como hoja de ruta histórica para búsquedas y tareas complementarias.

Fecha: 2026-06-29.

Lista concreta de qué buscar/pedir con cada herramienta antes y durante el informe. Nada de
esto valida solo: toda fuente nueva debe verificarse (URL, contenido, fecha, pertinencia, sesgo)
y no convertir menciones turísticas en padrón ni delimitaciones oficiales.

---

## Para buscar con Perplexity

### URLs pendientes (4) — prioridad alta
- **PX023A / PX023B** — Federico Lacroze / Libertador a Cabildo: fuente verificable que respalde
  ese tramo como corredor gastronómico.
- **PX024B** — Parque Saavedra / García del Río: fuente del corredor García del Río.
- **PX025A** — Paternal: fuente específica de un circuito gastronómico de Paternal (más allá del
  Distrito del Vino / contexto C15).

### Polos débiles a reforzar
- Avenida Caseros / Barracas, Costanera Norte (corredor completo), Villa Urquiza (barrio vs.
  eje DoHo), Devoto, Nuevo Bajo en Retiro (tramo Esmeralda-Paraguay), Abasto (polo propio vs.
  solapamiento con Corrientes), Boedo, Villa Pueyrredón / Av. San Martín.
- Reutilizar las consultas ya redactadas en
  `fuentes_externas/BUSQUEDAS_COMPLEMENTARIAS_PENDIENTES.md`.

### Fuentes institucionales sobre corredores
- Programas/distritos del GCBA sobre corredores gastronómicos, Distrito del Vino, BA Capital
  Gastronómica, "Barrios a la Carta".

### Historia / identidad de cada polo
- Material histórico-cultural por polo (Palermo, San Telmo, Recoleta, Abasto/Corrientes,
  Barrio Chino) para la sección narrativa.

### Material de turismo / GCBA
- Páginas vigentes de Turismo Buenos Aires por barrio/circuito; verificar que sigan activas.
- Confirmar el recurso/ID GeoJSON vigente de **barrios** y **comunas** en Buenos Aires Data.

---

## Para pedir a ChatGPT

- **Estructura narrativa** del informe (a partir del `ESQUELETO_INFORME_POLOS_GASTRO.md`).
- **Redacción ejecutiva** sobria para jefatura (tono DataGastro, sin lenguaje de IA, hallazgos
  separados de límites).
- **Revisión metodológica** del criterio de universo/grupos/precisión.
- **Comparación** con los informes de MercadosGastro y CasasDePastas para alinear estilo y
  estructura (sin copiar datos de esos proyectos).

---

## Para pedir a Claude Code

- **Mejoras de scripts**: rediseño del gráfico de familias (barras agrupadas/heatmap) y del
  mapa conceptual completo (anti-solapamiento); reubicar la caja "No mapeados".
- **Visuales**: prototipo de mapa estático GeoPandas + matplotlib del núcleo principal sobre
  barrios GeoJSON (sin geocodificar locales).
- **Prototipos**: validar el HTML de `cartografia_experimentos/` cuando se autorice.
- **QA del repo**: re-chequear consistencia tras cualquier regeneración de CSV; alinear el
  campo interno `nombre_polo` de la matriz con tildes si se regenera.
- **Generación futura del informe**: ensamblado de secciones y export, cuando se apruebe.

---

## Para buscar manualmente

- **Mapas oficiales**: visor Mapa Interactivo BA, IDECBA / Banco de mapas (verificar capas).
- **PDFs institucionales**: planes de desarrollo turístico, distritos económicos.
- **Notas de prensa**: cobertura sobre corredores/polos emergentes (Chacarita, Villa Crespo,
  DoHo, Costanera Norte).
- **Datasets**: Buenos Aires Data — barrios, comunas (GeoJSON); revisar si hay oferta
  gastronómica georreferenciada utilizable a futuro (sin scraping de plataformas privadas).
