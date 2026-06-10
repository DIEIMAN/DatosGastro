# Proyecto de Datos: Ecosistema Gastronómico de CABA

Versión operativa inicial generada el 2026-06-09 a partir del relevamiento `gastronomia_caba_v1.md.pdf`.

## Qué contiene

- Datos crudos seedeados en `data/raw/`.
- Modelo normalizado en `data/processed/`.
- Tablas analíticas iniciales en `data/analytics/`.
- SQL para crear esquema, tablas, cargas y vistas.
- Scripts Python para descarga, limpieza, normalización, construcción del modelo y exportación de informe.
- Documentación ejecutiva y técnica en `docs/`.

## Importante

Este paquete es una versión starter. Los CSV descargables oficiales no fueron descargados en este entorno; quedaron scripts preparados para hacerlo desde una máquina con internet.

Los campos con datos no encontrados o no validados se marcan explícitamente como `No disponible`, `No encontrado en fuente pública`, `Requiere validación` o `Dato inferido`.

## Cómo correr

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/download_sources.py
python src/build_model.py
python src/build_analytics.py
```

## Próximo paso recomendado

Correr `src/download_sources.py`, descargar F01-F03, perfilar los CSV reales y reemplazar los seeds por cargas completas.
# DatosGastro
