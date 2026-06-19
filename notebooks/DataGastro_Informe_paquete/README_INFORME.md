# Informe ejecutivo DataGastro — paquete reproducible

Este paquete genera el **informe ejecutivo de DataGastro en PDF** a partir de los
datos del proyecto. No modifica el pipeline, los datos procesados, el dashboard
ni las validaciones: solo **lee** los outputs ya generados y arma el documento.

## Contenido del paquete

| Archivo | Qué es |
|---|---|
| `DataGastro_Informe.pdf` | El informe final, listo para distribuir. |
| `scripts/generar_informe_pdf.py` | **Fuente principal de reproducción.** Genera las figuras y el PDF con ReportLab. |
| `outputs/informe/figures/` | Las seis figuras del informe (se regeneran al correr el script). |
| `docs/DataGastro_Informe_texto.md` | El texto completo del informe en formato editable. |
| `docs/DataGastro_Informe.tex` | Versión alternativa en LaTeX (opcional). |
| `requirements_informe.txt` | Dependencias mínimas para regenerar el informe. |
| `README_INFORME.md` | Este archivo. |

## Cómo regenerar el informe

Desde la raíz del proyecto DataGastro (la carpeta que contiene `data/`):

```bash
pip install -r requirements_informe.txt
python scripts/generar_informe_pdf.py
```

El script:

1. Detecta automáticamente la raíz del proyecto (no usa rutas absolutas).
2. Lee los outputs de `data/analytics/` y `data/processed/`.
3. Regenera las figuras en `outputs/informe/figures/`.
4. Escribe el PDF en `outputs/informe/DataGastro_Informe.pdf`.

Las cifras del informe se toman de los outputs del proyecto; el script no
recalcula métricas ni inventa números. Si los datos se actualizan y se reejecuta
el pipeline, basta volver a correr este script para obtener un informe al día.

## Editar el contenido

- Para cambios de **texto o números**, la fuente que produce el PDF es
  `scripts/generar_informe_pdf.py`. El archivo `docs/DataGastro_Informe_texto.md`
  es una copia legible y editable del mismo contenido; si se edita, conviene
  reflejar el cambio en el script para mantener el PDF sincronizado.
- Para cambios de **diseño** (colores, márgenes, tipografías), todo está en la
  sección de estilos del script (`INK`, `ACCENT`, estilos de párrafo, etc.).

## Versión LaTeX (opcional)

`docs/DataGastro_Informe.tex` es una alternativa para quienes prefieran LaTeX.
**No es la forma principal de reproducir el informe**: la herramienta usada para
generarlo es el script de ReportLab. La versión LaTeX usa las mismas figuras de
`outputs/informe/figures/` y se compila con:

```bash
pdflatex docs/DataGastro_Informe.tex
```

## Nota metodológica

El informe respeta las reglas del proyecto:

- No se suman F01 y F02: son universos distintos.
- F02 son habilitaciones aprobadas, **no** locales activos.
- F03 cuenta espacios reales, **no** puestos ni personas.
- F04 y F05 son inventarios trazables, **no** universos completos.
- Los permisos de área gastronómica están identificados como régimen, pero su
  dataset operativo **todavía no está integrado** como fuente analítica.
