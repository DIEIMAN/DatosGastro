# Skill 04 — Pipeline reproducible

Cómo trabajar sin romper lo que ya funciona.

## 1. Mapa del pipeline (qué no se toca sin permiso)

| Capa | Carpeta / archivo | Regla |
| --- | --- | --- |
| Ingesta / modelo | `src/build_model.py` | **No modificar sin permiso.** |
| Analítica | `src/build_analytics.py` | **No modificar sin permiso.** |
| Datos procesados | `data/processed/` | **No modificar sin permiso.** Son salida del pipeline. |
| Analítica derivada | `data/analytics/` | **No modificar sin permiso.** |
| Tablero | `dashboard/` | **No modificar sin permiso.** |
| Notebooks | `notebooks/` | **No modificar sin permiso.** |
| Informe final | `docs/archive/v3_2026-06/informe_ejecutivo.*` | **No modificar sin permiso.** |

Resto de `src/` (contratos, normalización, geocoding, validación) se puede leer libremente; para
modificar, seguir el flujo de la sección 4.

## 2. Principios

1. **Documentar antes de codear.** Cualquier integración nueva primero se describe (ficha de
   fuente, skill 02) y se aprueba; recién después se convierte en código.
2. **`--strict-real` manda.** No inventar datos ni URLs. Si no existe un archivo real, el modo
   estricto no debe fallar por su ausencia, pero tampoco se rellena con datos falsos.
3. **Seeds ≠ reales.** Los seeds son fallback de desarrollo y toda salida marca `apto_dashboard`
   en función de si el dato es real.
4. **Idempotencia.** Re-correr el pipeline sobre los mismos insumos debe dar el mismo resultado.
5. **Trazabilidad por fila.** Fuente, fecha de consulta y calidad por registro.

## 3. Comandos de referencia (pipeline vigente)

```bash
python src/build_model.py --strict-real
python src/build_analytics.py --strict-real
python src/validate_model.py --strict-real
python -m unittest discover tests
```

> No ejecutar estos comandos con intención de **regenerar** `data/processed/` o `data/analytics/`
> salvo que Diego lo pida: sobrescribirían salidas productivas.

## 4. Flujo para agregar una fuente nueva (sin romper)

1. **Ficha + contrato** documentados (skill 02; estilo `src/source_contracts.py`).
2. **Schema/stub** vacío si es fuente privada (no datos falsos, solo estructura).
3. **Validación tolerante**: si el archivo de la fuente no existe, no debe fallar; si existe,
   se valida estructura y ausencia de datos personales.
4. **Tests** específicos de la fuente (IDs no nulos, fecha presente, coordenadas dentro de CABA,
   categorías normalizadas no vacías, etc.).
5. **Correr validaciones** (sección 3) y revisar que no se tocó nada productivo.
6. **Aprobación de Diego** antes de cablear la fuente al pipeline público.

## 5. Validaciones y tests

- `src/validate_model.py` valida el modelo; correrlo en modo `--strict-real`.
- `tests/` usa `unittest`. Para módulos nuevos, agregar tests en la misma convención.
- Para fuentes externas se agrega `scripts/external_sources/validate_fuentes_externas.py`, que
  valida los **catálogos/documentación** de fuentes externas (no llama APIs, no scrapea).
- `python -m compileall <carpeta>` para chequear que los scripts compilan sin ejecutarlos.

## 6. Qué hacer si algo del pipeline parece estar mal

No "arreglarlo" silenciosamente. Documentar el hallazgo, proponer el cambio, y esperar permiso.
El pipeline F01–F05 se considera estable y auditado hasta que Diego diga lo contrario.
