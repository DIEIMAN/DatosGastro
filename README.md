# DatosGastro

Proyecto de datos sobre el ecosistema gastronomico de la Ciudad Autonoma de Buenos Aires.

La V3 prepara una base reproducible para pasar de seeds/manuales a datos reales descargados de BA Data / GCBA, sin inventar fuentes ni presentar seeds como datos reales.

## Que problema resuelve

Ordena fuentes, establecimientos, eventos, programas, ferias y mercados en un modelo trazable para analisis territorial y tableros. Permite correr un pipeline local aun cuando falten URLs directas de descarga: los seeds funcionan como fallback de desarrollo y toda salida marca si es apta o no para dashboard.

## Fuentes

- F01 Oferta y Establecimientos Gastronomicos: URL directa CKAN y CDN registradas en `src/config.py`.
- F02 Habilitaciones Aprobadas AGC: recursos reales 2015-2025 registrados en `src/config.py`; 2026 no esta publicado y no se exige en modo estricto.
- F03 Ferias y Mercados: CSV combinado, CSV complementarios y GeoJSON FIAB registrados en `src/config.py`.
- Otras fuentes relevadas en `data/seeds/raw_fuentes_relevadas.csv`.

No se inventan datos ni URLs. Las paginas portal quedan documentadas, pero la descarga automatica requiere enlaces directos a CSV/archivo.

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

`build_model.py` busca primero CSV reales en `data/raw/` con patrones `f01_*.csv`, `f02_*.csv` y `f03_*.csv`. Si no los encuentra, usa `data/seeds/` como fallback de desarrollo y lo informa en consola. El mapeo de columnas queda reportado en `outputs/tablas_resumen/contratos_fuentes.csv` y `docs/contratos_fuentes.md`.

Para validar si el proyecto esta listo para analisis serio o dashboard real:

```bash
python src/build_model.py --strict-real
python src/build_analytics.py --strict-real
python src/validate_model.py --strict-real
```

En modo estricto no se permiten seeds. Si faltan F01/F02/F03 reales, el comando debe fallar.

## Datos seed

Siguen siendo seed/manuales los archivos `raw_*` en `data/seeds/`, especialmente establecimientos, eventos, programas y ferias cargadas desde el relevamiento inicial. No representan padrones completos y no son aptos para dashboard real.

## Datos que requieren descarga real

- F01 para padron/listado completo de establecimientos.
- F02 para habilitaciones aprobadas por anio y rubro.
- F03 para ferias/mercados completos con geometria o ubicaciones oficiales.

## Fuentes en dashboard

Cada salida analytics incluye `fuentes_utilizadas`, `urls_fuentes`, `fecha_consulta_min`, `fecha_consulta_max`, `nota_metodologica`, `limitaciones` y `apto_dashboard`. En un dashboard, citar siempre esos campos debajo de cada grafico. Ver `docs/GUIA_FUENTES_DASHBOARD.md`.

## Limitaciones actuales

- Geocodificacion USIG queda preparada pero no se ejecuta offline.
- Los eventos sin sede fija usan `U00000`.
- Habilitaciones F02 estan sin registros reales en el seed actual.
- Las metricas publicas de impacto de programas no estan estructuradas.

## Proximos pasos

Cargar o refrescar fuentes reales con `python src/download_sources.py`, revisar `docs/perfilado_fuentes.md`, y volver a correr el pipeline estricto. Proximo foco: fuente real estructurada de eventos y programas si se quieren dashboards de esas vistas.
