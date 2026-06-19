# Roadmap de fuentes externas — DataGastro

Hoja de ruta para ampliar DataGastro con fuentes externas **sin romper el pipeline público
F01–F05, sin mezclar universos y sin scraping**. Documentación, no implementación.

Ver reglas en `docs/skills_claude/06_fuentes_externas_privadas.md` y clasificación en
`docs/skills_claude/02_metodologia_fuentes.md`.

## Artefactos

- **Catálogo normalizado**: `config/fuentes_externas/catalogo_fuentes_externas.csv` / `.json`
  (29 fuentes, IDs `E01–E29`, con `id_matriz_original` para trazar a la matriz).
- **Matriz fuente**: `config/fuentes_externas/matriz_fuentes_externas.csv` / `.xlsx`.
- **Esquema de campos objetivo**: `config/fuentes_externas/campos_objetivo_integraciones.csv`.
- **Splits por prioridad**: `outputs/fuentes_externas/fuentes_prioridad_{alta,media,baja}.csv`.
- **Documentación de apoyo** (`docs/fuentes_externas/`): `README_fuentes_externas.md`,
  `checklist_legal_y_metodologico.md`, `plantilla_pedido_convenio_datos.md`,
  `prompt_codex_fuentes_externas.md`, `acciones_diego.csv`.

## Prioridad (29 fuentes: 17 alta · 4 media · 8 baja)

### Alta — primero lo público/interno, después contraste abierto y convenios
1. **Cerrar lo público/interno crítico** (evita decir "44 mil locales activos"):
   `E22` Padrón vivo AGC, `E23` Permisos de área gastronómica (F06), `E25` Eventos GCBA,
   `E24` AGIP agregado, `E28` Formulario voluntario opt-in.
2. **Contraste externo rápido y barato**: `E05` OpenStreetMap/Overpass (abierto),
   `E01`/`E02` Google Places / Places Aggregate (API paga, solo piloto con autorización).
   Validación en 2 comunas: San Nicolás y Palermo.
3. **Convenios de alto impacto** (demanda/actividad real): `E09` Rappi, `E10` PedidosYa,
   `E11` Mercado Pago, `E13` adquirentes/bancos, `E14` POS, `E15` reservas, `E19` telcos.

### Media
`E12` Mercado Libre (insumos/equipamiento), `E18` Google Trends, `E17` TikTok Research,
`E16` Instagram/Meta. Uso complementario, no como padrón de locales.

### Baja / no recomendada
Yelp, Tripadvisor, Waze, SUBE, webs/menús, noticias; y **no recomendadas**: `E04` Google
Popular Times y `E29` scraping de plataformas (prohibido por guardrails).

## Reglas de avance (qué se puede hacer hoy)

| Fuente | Qué se puede hacer ahora | Qué NO |
| --- | --- | --- |
| OSM/Overpass (`E05`) | Script **exploratorio** (`scripts/external_sources/explore_osm_gastro.py`) | Abusar de servidores públicos |
| Google Places (`E01`,`E02`) | **Plan** de piloto (`prepare_google_places_plan.py`), sin llamar la API | Ejecutar API sin autorización; scraping de Maps |
| Rappi/PeYa/MP/POS/reservas/telcos | Preparar **pedido de convenio** (`generar_pedidos_convenio.py`) | Scraping; pedir datos personales/nominales |
| Internas GCBA (`E22–E25`) | Pedir bases por canal institucional | Tratar como universo público sin contrato |
| Popular Times / scraping (`E04`,`E29`) | Nada (documentar como no recomendada) | Implementar scraping |

## Criterio para pasar de roadmap a pipeline

Una fuente entra al pipeline solo con: ficha + contrato, ID estable, fecha de corte, pasa
`--strict-real`, no mezcla universos ni datos sensibles, y **aprobación explícita de Diego**
(skill 04). Hasta entonces, todo queda en este roadmap.

## Próximos pasos sugeridos (de `acciones_diego.csv`)

1. Pedir padrón vivo AGC y base de permisos de área gastronómica (inmediato).
2. Autorizar piloto Google Cloud acotado + 2 comunas; integrar OSM como contraste.
3. Armar one-pager de convenio para Rappi/PedidosYa y para Mercado Pago/procesadores.
4. Formulario opt-in de comercios vía BA Capital Gastronómica / cámaras.
