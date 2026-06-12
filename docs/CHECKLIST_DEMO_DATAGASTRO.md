# Checklist demo DataGastro

## 1. Reconstruir el proyecto

Desde la raiz del proyecto:

```bash
python src/download_sources.py
python src/build_model.py --strict-real
python src/build_analytics.py --strict-real
python src/validate_model.py --strict-real
python src/audit_real_data.py
python -m unittest discover tests
python -m compileall src scripts dashboard
```

La validacion estricta esperada debe cerrar con:

```text
ERROR=0
```

Warnings aceptables hoy:

- `F02_2026` como `PENDING`: recurso no publicado y no requerido para `--strict-real`.
- `F04` y `F05` como `PENDING` en descarga: son relevamientos manuales trazables cargados en `data/raw/`, no datasets oficiales con URL directa.
- `F03_MERCADOS` con archivo chico: recurso complementario de mercados, validado junto con el resto de F03.

## 2. Abrir dashboard

```bash
python -m streamlit run dashboard/app.py
```

La demo debe recorrer:

1. Panorama.
2. Territorio.
3. Dinamismo (F02).
4. Ecosistema publico (F03-F05).
5. Metodologia y calidad.

## 3. Abrir o exportar notebook

Abrir:

```bash
jupyter notebook notebooks/05_informe_ejecutivo_datagastro.ipynb
```

Exportar a HTML:

```bash
jupyter nbconvert --to html notebooks/05_informe_ejecutivo_datagastro.ipynb
```

No generar PDF en esta version si requiere dependencias externas.

## 4. KPIs esperados

- F01 oferta registrada: 2.823 filas.
- F02 habilitaciones gastronomicas aprobadas: 44.169 filas.
- F03 espacios reales: 259 filas.
- F03 puestos tecnicos: 4.352 filas, solo auditoria interna.
- F04 eventos gastronomicos relevados: 29 filas.
- F05 programas/politicas relevados: 9 filas.
- `dim_territorio.csv`: 48 barrios.

## 5. Advertencias para decir en la presentacion

- F01 mide oferta registrada, no vigencia actual garantizada.
- F02 mide habilitaciones aprobadas; no son locales activos ni locales unicos.
- F01 y F02 no se suman.
- F02 2025 se muestra separado o advertido como no comparable.
- F03 mide espacios reales; los puestos/personas quedan fuera de KPIs publicos.
- F04 y F05 son relevamientos manuales trazables, parciales y no oficiales como dataset estructurado.

## 6. Que no afirmar

- No afirmar cantidad de locales gastronomicos activos.
- No afirmar aperturas netas, cierres, supervivencia o bajas.
- No afirmar impacto economico, empleo, ventas o facturacion.
- No afirmar cobertura completa de eventos o programas.
- No mapear F02 como puntos hasta geocodificar y validar.
- No exponer datos personales del padron F03.

## 7. Proximos pasos recomendados

- Preparar geocodificacion USIG de F02 con cache y validacion muestral.
- Evaluar F06 permisos de area gastronomica como nueva fuente separada.
- Disenar export ejecutivo HTML/PDF simple despues de estabilizar la narrativa.
- Definir criterios de versionado para snapshots de demo interna.
