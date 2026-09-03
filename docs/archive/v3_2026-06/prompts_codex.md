# Prompts para Codex — DataGastro

Estos prompts están listos para copiar y pegar en Codex (o GitHub Copilot Chat). Cada uno es autocontenido: incluye el contexto del archivo, qué cambiar y por qué. Usarlos en orden o en paralelo según conveniencia.

---

## PROMPT 1 — Exportar el informe completo a PDF/HTML

**Contexto:** El proyecto DataGastro tiene una notebook en `notebooks/07_informe_completo.ipynb` que es el informe principal de análisis. Queremos poder generar un documento PDF o HTML limpio para distribuir internamente.

**Tarea:** Crear un script `scripts/exportar_informe.py` en la raíz del proyecto que:

1. Ejecute la notebook `notebooks/07_informe_completo.ipynb` con `nbconvert` en modo `execute` (para que genere los gráficos) y la exporte a HTML en `outputs/informe_completo.html`.
2. Opcionalmente también exporte a PDF si `weasyprint` o `nbconvert --to pdf` está disponible.
3. Imprima un mensaje claro cuando termine indicando dónde quedó el archivo.
4. Maneje el caso donde el archivo de salida ya existe (sobreescribirlo con aviso).

El comando para exportar sin ejecutar la notebook (solo convertir) sería:
```bash
python -m nbconvert --to html --no-input notebooks/07_informe_completo.ipynb --output-dir outputs/
```

El comando para ejecutar y exportar:
```bash
python -m nbconvert --to html --execute notebooks/07_informe_completo.ipynb --output-dir outputs/
```

El script debe usar `subprocess` para llamar a estos comandos y reportar el resultado.

**Archivo a crear:** `scripts/exportar_informe.py`

---

## PROMPT 2 — Agregar sección de hallazgo de densidad al dashboard (pestaña Territorio)

**Contexto:** En el proyecto DataGastro (`dashboard/app.py`), la pestaña "Dónde está la gastronomía" (`render_territorio`) muestra un mapa con puntos y una coropleta de habilitaciones por comuna. Falta destacar el hallazgo analítico más importante del proyecto: **San Nicolás tiene 6–7 veces más densidad gastronómica que Palermo**, aunque Palermo lidera en volumen absoluto.

**Tarea:** En la función `render_territorio` de `dashboard/app.py`, después de mostrar la coropleta de oferta registrada por barrio (`Oferta registrada por barrio (F01)`), agregar:

1. Un `st.metric` o `st.info` que destaque el hallazgo: algo como "El barrio de San Nicolás tiene ~7x más densidad gastronómica que Palermo (registros por km²)".
2. Un párrafo explicativo breve (puede ser texto estático en `dashboard/textos.py` bajo la clave `HALLAZGO_DENSIDAD`) que explique la diferencia entre volumen y densidad y por qué importa para gestión.

El texto a agregar en `textos.py` puede ser:
```python
HALLAZGO_DENSIDAD = (
    "**Hallazgo clave:** en volumen absoluto, Palermo lidera la oferta registrada. "
    "Pero por densidad (registros por km²), San Nicolás concentra entre 6 y 7 veces más actividad gastronómica. "
    "El núcleo real por intensidad es el microcentro y el casco histórico (San Nicolás, Monserrat, San Telmo), "
    "no Palermo. Esta diferencia importa para planificación de uso del suelo y permisos de espacio público."
)
```

**Archivos a modificar:** `dashboard/app.py` y `dashboard/textos.py`

---

## PROMPT 3 — Mejorar los KPI labels del dashboard para eliminar abreviaturas

**Contexto:** En `dashboard/textos.py`, los labels de los KPI (indicadores numéricos principales que aparecen en la pestaña Panorama) usan siglas y abreviaturas como "F01", "F02", "USIG" sin explicación. Queremos que cualquier persona que vea el dashboard entienda qué significa cada número sin conocer la jerga interna del proyecto.

**Tarea:** En `dashboard/textos.py`, modificar el diccionario `KPI_LABELS` (y el correspondiente `KPI_HELP` si existe) para que:

- `KPI_LABELS["f01"]` diga algo como `"Oferta registrada en guía oficial"` en lugar de `"Establecimientos F01"`.
- `KPI_LABELS["f02"]` diga `"Habilitaciones aprobadas (2015–2024)"` en lugar de `"Habilitaciones F02"`.
- `KPI_LABELS["f03"]` diga `"Espacios de ferias, mercados y FIAB"` en lugar de `"Espacios F03"`.
- `KPI_LABELS["f04"]` diga `"Eventos gastronómicos verificados"`.
- Los textos de ayuda (`KPI_HELP`) deben expandir las siglas: "F02" → "Fuente: Agencia Gubernamental de Control (AGC)", "USIG" → "Geocodificación con el Sistema de Información Geográfica del GCBA", etc.

**Archivo a modificar:** `dashboard/textos.py`

---

## PROMPT 4 — Agregar glosario a la pestaña Metodología del dashboard

**Contexto:** El dashboard DataGastro tiene una pestaña de "Metodología" (`render_metodologia` en `dashboard/app.py`) que explica las fuentes y limitaciones. Falta un glosario de siglas para que cualquier usuario pueda entender el significado de USIG, AGC, FIAB, F01-F05 sin tener que leer toda la documentación.

**Tarea:** En la función `render_metodologia` de `dashboard/app.py`, agregar al final (antes del expander de "Catálogo de fuentes") una sección de glosario. El glosario puede venir de un diccionario definido en `dashboard/textos.py`:

```python
GLOSARIO = {
    "AGC": "Agencia Gubernamental de Control — organismo del GCBA que aprueba habilitaciones comerciales.",
    "GCBA": "Gobierno de la Ciudad de Buenos Aires.",
    "USIG": "Sistema de Información Geográfica del GCBA — servicio oficial para normalizar y ubicar direcciones en el mapa.",
    "FIAB": "Ferias Itinerantes de Abastecimiento Barrial — ferias de productos frescos (frutas, verduras, pan, pescado) que rotan por barrios.",
    "F01": "Fuente 1: Oferta gastronómica registrada en la guía oficial del Ente de Turismo del GCBA.",
    "F02": "Fuente 2: Habilitaciones gastronómicas aprobadas por la Agencia Gubernamental de Control (2015–2024).",
    "F03": "Fuente 3: Espacios de ferias, mercados y FIAB de la Dirección General de Ferias del GCBA.",
    "F04": "Fuente 4: Eventos gastronómicos relevados manualmente con fuente anotada por fila.",
    "F05": "Fuente 5: Programas y políticas gastronómicas relevados manualmente con normativa de referencia.",
    "Geocodificación": "Proceso de convertir una dirección de texto en coordenadas geográficas para mostrarla en el mapa.",
    "Habilitación": "Autorización formal del GCBA para operar un rubro comercial en una dirección.",
    "Padrón vivo": "Registro actualizado de locales activos con altas y bajas. DataGastro no tiene esta fuente todavía.",
}
```

Mostrar el glosario como una tabla de dos columnas (Término / Definición) usando `st.table` o `st.dataframe`.

**Archivos a modificar:** `dashboard/textos.py` y `dashboard/app.py`

---

## PROMPT 5 — Agregar contador de hallazgos a la notebook 06

**Contexto:** La notebook `notebooks/06_informe_presentacion.ipynb` es la versión de presentación del análisis. Actualmente usa abreviaturas como "F01", "F02", "FIAB", "USIG", "AGC" sin expandirlas en las primeras menciones de cada sección. Esto dificulta la comprensión para audiencias que no conocen la jerga interna del proyecto.

**Tarea:** Revisar cada celda markdown de `notebooks/06_informe_presentacion.ipynb` y reemplazar:

- Primera mención de "F01" en cada sección → "oferta gastronómica registrada (F01)"
- Primera mención de "F02" en cada sección → "habilitaciones gastronómicas aprobadas (F02)"
- Primera mención de "F03" en cada sección → "espacios de ferias, mercados y Ferias Itinerantes de Abastecimiento Barrial (F03)"
- Primera mención de "FIAB" → "Ferias Itinerantes de Abastecimiento Barrial (FIAB)"
- Primera mención de "USIG" → "Sistema de Información Geográfica del GCBA (USIG)"
- Primera mención de "AGC" → "Agencia Gubernamental de Control (AGC)"
- Primera mención de "GCBA" → "Gobierno de la Ciudad de Buenos Aires (GCBA)"

Las menciones posteriores dentro de la misma celda pueden mantener la sigla sola.

**Archivo a modificar:** `notebooks/06_informe_presentacion.ipynb` (solo celdas de tipo markdown, no código)

---

## PROMPT 6 — Script para generar resumen ejecutivo en PDF con ReportLab

**Contexto:** El proyecto DataGastro ya tiene `reportlab` en `requirements.txt` y un archivo `src/export_report.py` que actualmente está casi vacío (75 bytes). Hay un archivo `docs/informe_ejecutivo.pdf` que es una versión antigua y pequeña del informe.

**Tarea:** Implementar `src/export_report.py` para que genere un PDF de resumen ejecutivo a partir de los datos en `data/analytics/analytics_resumen_ejecutivo.csv`. El PDF debe:

1. Tener una portada con el título "DataGastro — Resumen Ejecutivo" y la fecha de los datos.
2. Incluir una tabla con los indicadores principales (separados por fuente, nunca sumados).
3. Incluir una sección de "Qué responde hoy" y "Qué no responde todavía" como texto estático.
4. Guardar el archivo en `outputs/resumen_ejecutivo_datagastro.pdf`.

Usar la librería `reportlab` (ya está en requirements.txt). El script debe ser ejecutable directamente:
```bash
python src/export_report.py
```

**Archivo a modificar:** `src/export_report.py`

---

## NOTAS GENERALES PARA CODEX

- **No sumar fuentes**: Nunca generar código que sume F01 + F02 + F03 como "total de establecimientos gastronómicos". Cada fuente es un universo distinto.
- **No llamar F02 "locales activos"**: Son habilitaciones aprobadas, no establecimientos en funcionamiento.
- **No inventar datos**: Si un archivo no existe o está vacío, el código debe mostrar un mensaje claro, no generar números.
- **Nombres completos en la UI**: Cualquier texto visible al usuario (labels, títulos, captions) debe usar el nombre completo antes de usar la sigla.
- **Fuente siempre visible**: Cualquier gráfico o tabla debe tener una caption que identifique la fuente de los datos.
