# Reproducción — Informe político integrado V2 (fase27)

## Comando

Desde la raíz del repositorio (usar SIEMPRE el Python del venv):

```
.venv/Scripts/python.exe scripts/polos_gastro/fase27_informe_politico_integrado_v2/generar_informe_politico_integrado_v2.py
```

Opción `--no-pack`: omite el paquete de revisión y el ZIP (útil durante iteraciones de QA).

## Archivos de esta carpeta

- `generar_informe_politico_integrado_v2.py` — generador único (assets + PDF + QA + paquete).
- `contenido_informe_politico_integrado_v2.yaml` — **capa editable**: todo el texto visible del
  informe se cambia aquí, sin tocar el motor gráfico.
- `config_integracion_v2.json` — configuración de integración: recortes reproducibles de los
  assets V3.1, rutas de capas v2.1, delimitación vigente de Palermo, DPI.
- `README_REPRODUCCION.md` — este archivo.

## Insumos (solo lectura)

- Assets V3.1: `outputs/polos_gastro/correcciones_cartograficas_post_qa_v3_1/mapas/`.
- Capas v2.1: `outputs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/` (+ `HANDOFF_FABLE/`).
- Fondo: callejero GCBA local (`outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/`) y
  `data/raw/geo_barrios.geojson`. Sin red, sin APIs, sin Places.

## Salidas

En `outputs/polos_gastro/fase27_informe_politico_integrado_v2/`:
PDF de 10 páginas, `assets/` insertados, `qa_png_*/` (10 páginas a PNG), `metadatos/`
(QA estructural, scan textual, trazabilidad de assets, verificación de predecesores y
superficies protegidas, snapshots git), `MANIFEST_CONTENIDO.csv`, `CHECKSUMS_SHA256.txt`,
`REVISION_INFORME_POLITICO_INTEGRADO_V2/` y su `.zip`.

## Garantías del script

- Aborta (assert) si cambia cualquier predecesor controlado (Fase 25 política/oficina, KPI
  lock V3, assets V3.1) o el digest de superficies protegidas.
- No escribe fuera de la línea fase27.
- QA visual: después de regenerar, mirar las 10 páginas PNG (obligatorio antes de dar por
  bueno el PDF; `datagastro-qa-pdf`).
