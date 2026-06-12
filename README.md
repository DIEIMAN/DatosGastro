# DatosGastro

Proyecto de datos sobre el ecosistema gastronomico de la Ciudad Autonoma de Buenos Aires.

La V3 prepara una base reproducible para pasar de seeds/manuales a datos reales descargados de BA Data / GCBA, sin inventar fuentes ni presentar seeds como datos reales.

## Que problema resuelve

Ordena fuentes, oferta gastronomica registrada, habilitaciones aprobadas, eventos, programas, ferias y mercados en un modelo trazable para analisis territorial y tableros. Permite correr un pipeline local aun cuando falten URLs directas de descarga: los seeds funcionan como fallback de desarrollo y toda salida marca si es apta o no para dashboard.

## Fuentes

- F01 Oferta y Establecimientos Gastronomicos: URL directa CKAN y CDN registradas en `src/config.py`. Alimenta `fact_establecimiento.csv`.
- F02 Habilitaciones Aprobadas AGC: recursos reales 2015-2025 registrados en `src/config.py`; 2026 no esta publicado y no se exige en modo estricto. Alimenta `fact_habilitacion_gastronomica.csv`.
- F03 Ferias y Mercados: CSV combinado, CSV complementarios y GeoJSON FIAB registrados en `src/config.py`. Alimenta `fact_espacio_feria_mercado.csv` para espacios reales y `fact_puesto_feria.csv` como insumo tecnico de puestos/personas.
- F04 Eventos gastronomicos semiestructurados: relevamiento manual trazable con fuente por fila. Alimenta `fact_evento_gastronomico.csv`.
- F05 Programas y politicas gastronomicas semiestructuradas: catalogo manual trazable con fuente por fila. Alimenta `fact_programa_politica.csv`.
- Otras fuentes relevadas en `data/seeds/raw_fuentes_relevadas.csv`.

No se inventan datos ni URLs. Las paginas portal quedan documentadas, pero la descarga automatica requiere enlaces directos a CSV/archivo. F04 y F05 no provienen de datasets oficiales estructurados: son relevamientos manuales trazables y no representan el universo completo de eventos ni programas gastronomicos de CABA.

## Estructura

- `data/raw/`: CSV reales descargados o cargados manualmente.
- `data/seeds/`: CSV seed/manuales de desarrollo. No son aptos para dashboard real.
- `data/processed/`: dimensiones y hechos normalizados.
- `data/analytics/`: salidas agregadas para analisis/dashboard.
- `data/archive/`: artefactos de datos historicos conservados, no usados por el pipeline.
- `src/`: scripts del pipeline.
- `sql/`: DDL, carga, queries y vistas.
- `docs/`: criterios, trazabilidad, limitaciones y guia de ejecucion.
- `docs/archive/`: documentacion heredada o versiones anteriores.
- `docs/references/`: fuentes documentales de referencia.
- `outputs/tablas_resumen/`: perfilado automatico de fuentes.
- `scripts/compat/`: wrappers de compatibilidad; el punto de entrada canonico sigue siendo `src/`.

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Pipeline

```bash
python src/download_sources.py
python src/profile_sources.py
python src/build_model.py
python src/build_analytics.py
python src/validate_model.py
```

`download_sources.py` reporta `PENDING` cuando falta una URL directa. Eso es esperado hasta completar `SOURCE_CONFIG` en `src/config.py`.

`build_model.py` busca primero CSV reales en `data/raw/` con patrones `f01_*.csv`, `f02_*.csv`, `f03_*.csv`, `f04_*.csv` y `f05_*.csv`. Si no los encuentra, usa `data/seeds/` como fallback de desarrollo y lo informa en consola. El mapeo de columnas queda reportado en `outputs/tablas_resumen/contratos_fuentes.csv` y `docs/contratos_fuentes.md`.

Regla conceptual para dashboard:

- `fact_establecimiento.csv` representa solo F01: oferta/establecimientos gastronomicos registrados.
- `fact_habilitacion_gastronomica.csv` representa solo F02: habilitaciones aprobadas AGC inferidas como gastronomicas por rubro.
- `fact_espacio_feria_mercado.csv` representa F03 a grano espacio real: mercados, ferias especializadas y FIAB.
- `fact_puesto_feria.csv` representa F03 a grano puesto/persona y queda solo como insumo tecnico; no es KPI de espacios ni se expone en dashboard.
- `fact_evento_gastronomico.csv` representa F04: eventos/activaciones relevados manualmente con trazabilidad.
- `fact_programa_politica.csv` representa F05: catalogo de programas, politicas, normativa e instrumentos.

No sumar F01 + F02 como si fueran establecimientos activos unicos. En particular, no mostrar "40.295 establecimientos gastronomicos" ni ningun total combinado F01+F02 como establecimientos. Mostrar metricas separadas con fuente, fecha de consulta y limitaciones.

Para validar si el proyecto esta listo para analisis serio o dashboard real:

```bash
python src/build_model.py --strict-real
python src/build_analytics.py --strict-real
python src/validate_model.py --strict-real
```

En modo estricto no se permiten seeds. Si faltan F01/F02/F03 reales o F04/F05 semiestructurados, el comando debe fallar.

## Dashboard V1 de validacion

El dashboard local esta en `dashboard/app.py`. Es una app de validacion metodologica, no una pieza final de presentacion.

Instalar dependencias y correr:

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

La app lee `data/analytics/` y `data/processed/`, separa F01/F02/F03/F04/F05, muestra fuentes y limitaciones, y mantiene fuera de metricas fuertes las filas cualitativas o en validacion.

## Datos seed

Siguen siendo seed/manuales los archivos `raw_*` en `data/seeds/`, especialmente establecimientos, eventos, programas y ferias cargadas desde el relevamiento inicial. No representan padrones completos y no son aptos para dashboard real.

## Datos que requieren descarga real

- F01 para oferta/listado de establecimientos registrados.
- F02 para habilitaciones aprobadas por anio y rubro, sin tratarlas como padron vivo.
- F03 para ferias/mercados completos con geometria o ubicaciones oficiales.
- F04/F05 para eventos y programas solo como relevamientos manuales trazables; no como datasets oficiales completos.

## Fuentes en dashboard

Cada salida analytics incluye `fuentes_utilizadas`, `urls_fuentes`, `fecha_consulta_min`, `fecha_consulta_max`, `nota_metodologica`, `limitaciones` y `apto_dashboard`. En un dashboard, citar siempre esos campos debajo de cada grafico. Ver `docs/GUIA_FUENTES_DASHBOARD.md`.

## Indicadores base actuales

- 2.823 registros en Oferta Gastronomica F01.
- 44.169 habilitaciones gastronomicas inferidas desde AGC F02.
- 220 espacios reales F03: 6 mercados, 30 ferias especializadas y 184 FIAB.
- 4.352 registros de puestos F03 conservados solo como insumo tecnico/auditoria interna.
- 29 eventos F04 cargados; 13 aptos para metricas fuertes y 16 cualitativos/en validacion/no aptos.
- 9 programas/instrumentos F05 cargados; 4 aptos para catalogo dashboard y 5 cualitativos/en validacion/no aptos.

## Limitaciones actuales

- Geocodificacion USIG queda preparada pero no se ejecuta offline.
- Los eventos sin sede fija usan `U00000`.
- F04 no representa el universo completo de eventos gastronomicos; las metricas fuertes solo usan `apto_dashboard = si`, `requiere_validacion = no` y fecha completa.
- F05 es catalogo/fichero, no serie temporal de impacto; no usar montos viejos como vigentes.
- F02 no representa establecimientos activos unicos: son habilitaciones aprobadas y la clasificacion gastronomica es inferida desde el rubro.
- F02 2025 queda marcado con `requiere_validacion = si`: el recurso tiene esquema distinto y contiene disposiciones de varios anios, por lo que no debe leerse como flujo anual comparable. La serie anual excluye 2025 y el periodo agregado 2015-2018 del grafico comparable.
- F03 contiene recursos con distintos niveles de grano. Los puestos individuales no deben interpretarse como ferias o mercados. Los indicadores principales usan espacios reales; los registros de puestos, si se conservan, quedan solo como insumo tecnico y no se exponen en dashboard.
- F01 no trae vigencia por registro y puede estar desactualizado.
- Las metricas publicas de impacto de programas no estan estructuradas.

## Proximos pasos

Refrescar F01/F02/F03 con `python src/download_sources.py` cuando corresponda, mantener F04/F05 curados con fuente por fila, revisar `docs/perfilado_fuentes.md`, y volver a correr el pipeline estricto. Proximo foco: disenar el dashboard con las advertencias metodologicas visibles.
