# PolosGastro — README

Subproyecto de DataGastro sobre polos gastronómicos de la Ciudad de Buenos Aires.
Fecha de corte vigente: 2026-06-29.

> Base candidata, **no oficial**. Universo de lectura, no padrón de locales activos.

## Estado del proyecto

Auditoría técnica y exploración cartográfica/visual **cerrada**. **Sin informe final aún.**
No hay PDF, mapa final, geocodificación ni shapefiles. Todo el subproyecto está untracked en Git
(sin commit/push/staging).

## Fases completadas

- **Fase 1** — Base candidata desde `PolosGastro/Polos gastronómicos.pdf`: 23 polos candidatos,
  100 locales destacados (semilla).
- **Fase 2** — Validación documental: 32 fichas, matriz de validación, 80 fuentes externas,
  fuentes semilla y complementarias.
- **Universo defendible** — 32 polos clasificados por grupo, evidencia, decisión y familia.
- **Fase 3A** — URLs (16 de 20 resueltas; 4 pendientes: PX023A, PX023B, PX024B, PX025A) y
  delimitación textual (alta 3, media 11, baja 16, sin delimitación 2). 8 familias territoriales.
- **Fase 3B** — Base de mapa conceptual + 6 gráficos. Diagrama esquemático, no geográfico.
- **Auditoría pre-informe** — auditoría integral, QA de consistencia, auditoría visual, notas
  del paquete USIG, fuentes cartográficas CABA, comparación de librerías, prototipo USIG aislado,
  propuesta visual y lista de pedidos externos.
- **Insumos externos + Google Places + herramientas** — Respuesta 2 de Perplexity (sin fuentes
  nuevas); roadmap y diseño de experimento Google Places; script piloto.
- **Fuentes manuales + piloto Places real** — 12 fuentes manuales (ChatGPT) incorporadas;
  García del Río: no_incluir → anexo. Piloto Google Places ejecutado (10 locales del núcleo,
  10 matches, experimental, sin coordenadas en mapas).
- **Fase 4A — rediseño visual + mapa territorial (esta fase)** — gráficos v2, mapas conceptuales
  v2 sin solapes y **mapa territorial real** con barrios oficiales de Buenos Aires Data. QA visual
  y plan de ensamblado del informe.

## Conteos clave

- 23 polos candidatos (Fase 1) · **32** en universo defendible.
- Grupos (actual): núcleo 6 · zona relevante 5 · emergente 9 · **anexo 8** · **no incluir 4**.
- 100 locales destacados · **92 fuentes externas** · 32 fichas · 8 familias.

## Archivos clave

- **Universo**: `outputs/polos_gastro/universo_informe_polos_gastro.csv`.
- **Validación**: `outputs/polos_gastro/matriz_validacion_polos_gastro.csv`.
- **Delimitación**: `outputs/polos_gastro/base_delimitacion_preliminar_polos_gastro.csv`.
- **Mapa conceptual**: `outputs/polos_gastro/base_mapa_conceptual_polos_gastro.csv` + `graficos/`.
- **Visuales Fase 4A**: `outputs/polos_gastro/graficos/fase4a/` (gráficos v2 + mapa territorial),
  `base_cartografica_visual_polos_gastro.csv`, `cartografia/fase4a/*.md`.
- **Cartografía oficial**: `PolosGastro/cartografia/barrios_caba.geojson` y `comunas_caba.geojson`
  (Buenos Aires Data; referencia territorial, no delimitación de polos).
- **Plan de informe**: `PLAN_ENSAMBLADO_INFORME_POLOS_GASTRO.md`.
- **Fuentes**: `outputs/polos_gastro/fuentes_externas_polos_gastro.csv` + `fuentes_externas/`.
- **Fichas**: `docs/polos_gastro/fichas_polos/` (32).
- **Esqueleto del informe**: `docs/polos_gastro/ESQUELETO_INFORME_POLOS_GASTRO.md`.
- **Auditorías y cartografía** (esta fase):
  - `AUDITORIA_INTEGRAL_PRE_INFORME_POLOS_GASTRO.md`
  - `QA_CONSISTENCIA_UNIVERSO_POLOS_GASTRO.md`
  - `AUDITORIA_VISUAL_GRAFICOS_POLOS_GASTRO.md`
  - `PROPUESTA_VISUAL_INFORME_POLOS_GASTRO.md`
  - `PEDIDOS_EXTERNOS_PARA_MEJORAR_POLOS_GASTRO.md`
  - `cartografia/FUENTES_CARTOGRAFICAS_CABA.md`
  - `cartografia/LIBRERIAS_MAPAS_INFORMES_DATAGASTRO.md`
  - `cartografia/USIG_MAPA_INTERACTIVO_NOTAS_TECNICAS.md`
- **Insumos externos / Places / herramientas** (esta fase):
  - `fuentes_externas/perplexity_respuesta_2_busqueda_puntual_faltantes.md`
  - `outputs/polos_gastro/perplexity_respuesta_2_aportes_normalizados.csv`
  - `fuentes_externas/ESTADO_FUENTES_PENDIENTES_POST_PERPLEXITY_2.md`
  - `google_places/GOOGLE_PLACES_API_ROADMAP_POLOS_GASTRO.md`
  - `google_places/DISEÑO_EXPERIMENTO_GOOGLE_PLACES.md`
  - `HERRAMIENTAS_REUTILIZABLES_DATAGASTRO_PROPUESTA.md`
- **Scripts**: `scripts/polos_gastro/` (5 scripts reproducibles).
- **Experimento cartográfico aislado**:
  `scripts/polos_gastro/cartografia_experimentos/usig_mapa_interactivo_minimo/`.
- **Piloto Google Places (dry-run, experimental, fuera del pipeline)**:
  `scripts/polos_gastro/google_places/` (`places_piloto_locales.py`, `README.md`, `.env.example`).

## Estado de roadmaps experimentales

- **Respuesta 2 Perplexity**: incorporada. No agregó fuentes de validación; **universo sin
  cambios**. Detalle en `fuentes_externas/ESTADO_FUENTES_PENDIENTES_POST_PERPLEXITY_2.md`.
- **Google Places**: piloto **ejecutado** sobre 10 locales del núcleo (10 matches, experimental,
  sin coordenadas en mapas). Ver `google_places/REPORTE_PILOTO_GOOGLE_PLACES.md`.
- **Cartografía / mapa territorial**: **resuelto** en Fase 4A (barrios oficiales + mapa estático).
- **Herramientas reutilizables DataGastro**: propuesta documental; nada implementado fuera de
  PolosGastro.

## Próximos pasos (Fase 5)

1. **Redactar el primer borrador en Markdown** según `PLAN_ENSAMBLADO_INFORME_POLOS_GASTRO.md`,
   con los visuales `fase4a/` ya insertados.
2. Verificar manualmente las 5 URLs `requiere_revision_url` (clarin.com / GCBA) y los 3 matches
   de baja confianza del piloto Places.
3. Pedir estructura/redacción a ChatGPT; alinear estilo con Mercados/CasasDePastas.
4. Recién con el borrador revisado: evaluar PDF (no antes).

## Qué NO hacer todavía

- No generar PDF final ni mapa final.
- No geocodificar locales.
- No crear shapefiles/geojson definitivos.
- No convertir locales destacados en padrón oficial.
- No afirmar delimitaciones oficiales sin fuente.
- No ejecutar llamadas reales a Google Places sin API key autorizada, billing controlado y ToS
  revisados (el piloto queda en dry-run).
- No guardar ni imprimir API keys; `.env` real fuera de Git.
- No crear carpetas `shared/` ni tocar otros subproyectos (Cafecito, MercadosGastro,
  CasasDePastas) ni el pipeline general.
