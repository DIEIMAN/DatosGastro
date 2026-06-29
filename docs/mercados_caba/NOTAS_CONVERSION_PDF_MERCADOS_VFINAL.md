# Notas de conversión a PDF — Mercados gastronómicos CABA (VFinal)

Documento de apoyo para una futura conversión a PDF del Markdown maestro
(`INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_MARKDOWN_MASTER.md`).

**No genera PDF ni toca scripts de PDF.** Es solo una guía editorial y de maquetación.

---

## 1. Fuente editorial

- Fuente única de verdad: `INFORME_FINAL_MERCADOS_GASTRONOMICOS_CABA_MARKDOWN_MASTER.md`.
- Conteos y framing ya validados ahí. No re-derivar números desde otras versiones.
- Estrategia Markdown-first: primero se cierra el texto, después se diseña el PDF.

---

## 2. Visuales necesarios

Reutilizables de V5/V5.1 (ya existen en `outputs/mercados_caba/sanitized/`):

- `grafico_kpi_cards_v5.png` → sección 1 (KPI cards: 13 / 11 / 2 / 6 comunas / 13 multifuente).
- `mapa_sedes_fijas_mercados_gastronomicos_v5.png` → sección 4 (solo sedes fijas).
- `grafico_tipo_primario_v5.png` → sección 5 (tipología, suma 13).
- `grafico_gestion_v5.png`, `grafico_horarios_v5.png`, `grafico_publicos_objetivo_v5.png` → sección 6.
- `visual_itinerantes_mercados_gastronomicos_v5.png` → apoyo a la separación sede fija / itinerante.
- `grafico_respaldo_fuentes_v5.png` → sección 12 (anexo de fuentes).

A diseñar o mejorar para el PDF final:

- **Lámina única de gestión + horarios + públicos** (sección 6): hoy son 3 gráficos separados; conviene una sola lámina compacta para no fragmentar la página.
- **Cards de espacios no contabilizados** (sección 8): Soho, Mercat Caballito, El Galpón y Carruajes, con etiqueta clara de "no contabilizado" / "cerrado documentado".
- **KPI cards** revisados para que no queden cajas ajustadas (ver problemas V5.1).

Regla de mapa: el mapa principal muestra **solo las 11 sedes fijas**. Los 2 itinerantes **nunca** se grafican como punto fijo.

---

## 3. Páginas problemáticas detectadas en V5.1

- **Cajas muy ajustadas:** KPI cards y cards de cierre con texto pegado a los bordes.
- **Aire desigual entre páginas:** algunas secciones quedan apretadas y otras con demasiado espacio en blanco.
- **Tablas demasiado chicas:** la tabla final y las de tipología pierden legibilidad por tamaño de fuente reducido.
- **Sensación de maquetación forzada:** se nota el ajuste manual para encajar bloques en la página.
- **Portada / títulos al límite:** riesgo de título cortado o portada incompleta (corregido en parte en V5.1, vigilar al re-exportar).

---

## 4. Recomendaciones para diseñar el PDF final

- **Una idea por bloque, no una sección por página.** Dejar que el contenido fluya; no forzar saltos.
- **Tablas legibles:** fuente mínima cómoda, padding interno suficiente, columnas que no se compriman.
- **Respiración uniforme:** márgenes y espaciado consistentes entre secciones.
- **Jerarquía clara:** resumen ejecutivo (sección 1), indicadores (2) y decisión que permite tomar (9) como secciones más fuertes.
- **Sección 9 ("Qué decisión permite tomar") destacada:** es uno de los puntos más valiosos para gestión.
- **Pie de página discreto** con la aclaración "base candidata trazable, no oficial".
- **Lenguaje obligatorio en headers y pies:** "activos identificados", "relevamiento documental y multifuente", "base candidata trazable", "Google Places como señal auxiliar no oficial".

---

## 5. Qué NO hacer

- ❌ Tablas anchas que se salgan del área de texto o se corten al margen.
- ❌ Cajas / cards cortadas o con texto pegado al borde.
- ❌ Puntos itinerantes en el mapa de sedes fijas (Buenos Aires Market y Sabe la Tierra **no** son punto fijo).
- ❌ Título o portada cortados.
- ❌ Páginas vacías o con aire desigual.
- ❌ Repetir la metodología en cada sección (va una sola vez, en la 3, con recordatorios mínimos).
- ❌ Usar como headline: "activos confirmados", "padrón oficial", "total definitivo", "geolocalización exacta".
- ❌ Cambiar conteos: se mantiene 13 / 11 / 2 / 13 multifuente / 12 alto / 6 comunas / 3 no contabilizados / 1 cerrado.

---

_Apoyo de maquetación. La fuente editorial es el Markdown maestro; este archivo no reemplaza datos ni conteos._
