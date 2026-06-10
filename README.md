# DatosGastro

Proyecto de datos sobre el ecosistema gastronomico de la Ciudad Autonoma de Buenos Aires.

La V2 prepara una base reproducible para pasar de datos seed/manuales a datos reales descargados de BA Data / GCBA, sin inventar fuentes ni reemplazar evidencia pendiente de validacion.

## Que problema resuelve

Ordena fuentes, establecimientos, eventos, programas, ferias y mercados en un modelo trazable para analisis territorial y tableros. Permite correr un pipeline local aun cuando falten URLs directas de descarga: los seeds funcionan como fallback y los pendientes quedan marcados.

## Fuentes

- F01 Oferta y Establecimientos Gastronomicos: pendiente de URL directa en `src/config.py`.
- F02 Habilitaciones Aprobadas AGC: pendiente de URL directa en `src/config.py`.
- F03 Ferias y Mercados: pendiente de URL directa en `src/config.py`.
- Otras fuentes relevadas en `data/raw/raw_fuentes_relevadas.csv`.

No se inventan datos ni URLs. Las paginas portal quedan documentadas, pero la descarga automatica requiere enlaces directos a CSV/archivo.

## Estructura

- `data/raw/`: CSV seed/manuales y futuros CSV reales descargados.
- `data/processed/`: dimensiones y hechos normalizados.
- `data/analytics/`: salidas agregadas para analisis/dashboard.
- `src/`: scripts del pipeline.
- `sql/`: DDL, carga, queries y vistas.
- `docs/`: criterios, trazabilidad, limitaciones y guia de ejecucion.
- `outputs/tablas_resumen/`: perfilado automatico de fuentes.

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

`download_sources.py` reporta `PENDING` cuando falta una URL directa. Eso es esperado en la V2 hasta completar `SOURCE_CONFIG` en `src/config.py`.

## Datos seed

Siguen siendo seed/manuales los archivos `raw_*` en `data/raw/`, especialmente establecimientos, eventos, programas y ferias cargadas desde el relevamiento inicial. No representan padrones completos.

## Datos que requieren descarga real

- F01 para padron/listado completo de establecimientos.
- F02 para habilitaciones aprobadas por anio y rubro.
- F03 para ferias/mercados completos con geometria o ubicaciones oficiales.

## Limitaciones actuales

- Geocodificacion USIG queda preparada pero no se ejecuta offline.
- Los eventos sin sede fija usan `U00000`.
- Habilitaciones F02 estan sin registros reales en el seed actual.
- Las metricas publicas de impacto de programas no estan estructuradas.

## Proximos pasos

Completar URLs directas oficiales en `src/config.py`, descargar fuentes reales, revisar `docs/perfilado_fuentes.md`, ajustar mapeos de columnas reales y volver a correr validacion.
