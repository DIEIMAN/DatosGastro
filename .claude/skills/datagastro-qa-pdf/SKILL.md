---
name: datagastro-qa-pdf
description: QA visual obligatorio de PDFs en DataGastro. Usar SIEMPRE después de generar o regenerar cualquier PDF (informes, mapas, packs) y antes de reportarlo como terminado. Renderiza páginas a PNG con PyMuPDF y las inspecciona visualmente.
---

# QA visual de PDFs

Un PDF generado sin mirar sus páginas NO está terminado. Este skill reemplaza el ciclo de
"Diego revisa a ojo y dicta correcciones" por auto-revisión antes de entregar.

## Procedimiento

1. Generar el PDF con el generador que corresponda (siempre `.venv/Scripts/python.exe`).
2. Renderizar todas las páginas:
   `.venv/Scripts/python.exe scripts/qa/pdf_check.py <ruta.pdf>`
   (PNGs a `qa_png_<nombre>/`; usar `--pages` para re-chequeos parciales, `--dpi 150` si hay
   texto chico).
3. **Leer los PNG con la herramienta Read (son imágenes) y mirar cada página**, buscando:
   - texto o leyendas que se pisan / quedan pegados a mapas, tablas o bordes;
   - desbordes de tabla, cortes de palabra feos, viudas/huérfanas notorias;
   - páginas en blanco o con `[SIN TEXTO]` en el resumen del script;
   - portada: sin fecha, sin versión, sin "borrador/prueba/documento interno";
   - marca: DGDGAS, nunca DataGastro;
   - numeración de secciones e índice consistentes con el contenido;
   - mapas: leyendas legibles, sin superposición, referencias completas.
4. Si hay defectos: corregir el generador, regenerar y volver al paso 2. No entregar con
   defectos conocidos "menores" sin señalarlos.
5. Si existe `kpis_lock.json` del informe:
   `.venv/Scripts/python.exe scripts/qa/validate_kpis.py <lock> <ruta.pdf>`.
6. Al reportar, decir explícitamente: cuántas páginas se revisaron, qué se corrigió, y la ruta
   absoluta del PDF final y de los PNG de QA.

## Reglas

- Nunca declarar "listo" un PDF solo porque el script terminó sin error.
- No usar `pdftoppm`/poppler ni instalar dependencias nuevas: PyMuPDF (`fitz`) ya está en el venv.
- Los PNG de QA van junto al PDF o a una carpeta `qa_*`; no commitearlos si el output es interno.
- Ante una regresión visual respecto de la versión anterior, avisar y preguntar qué base usar;
  no asumir que "más nuevo" es la base correcta.
