# Resumen documental V2.1 — Mercados gastronómicos CABA

Fecha de armado: 2026-06-24

## Qué es este paquete

Este paquete transforma las respuestas de Perplexity sobre mercados gastronómicos en insumos controlables para el proyecto. No cambia el conteo V1.2 de mercados activos: mantiene **15 mercados gastronómicos activos para conteo** como base hasta que nuevas fuentes verificables justifiquen una modificación.

## Lectura ejecutiva

Perplexity aporta tres cosas útiles:

1. **Refuerzo de fuentes oficiales GCBA/Turismo BA** para mercados y patios como Mercado Belgrano, Mercado San Nicolás, Mercado Bonpland, Patio de los Lecheros, Smart Plaza Parque Patricios, Patio Costanera Norte y Patio Rodrigo Bueno.
2. **Datos operativos parciales** sobre horarios, oferta y cantidad de puestos/locales para algunos mercados. Los casos más útiles son Mercado del Progreso, Mercado Bonpland, Mercado Belgrano, Mercado San Nicolás, Mercado Soho y Mercado de San Telmo.
3. **Pistas de posibles omitidos**, especialmente Gourmand Food Hall y Mercado Fusión. El resto de hallazgos parece más cercano a eventos o festivales temporarios que a mercados permanentes.

## Qué NO debe hacerse todavía

- No sumar nuevos mercados al conteo por estos resultados.
- No usar Perplexity como fuente final si no hay URL completa visible.
- No cerrar horarios divergentes sin decidir fuente preferida.
- No mezclar ferias/eventos temporales con mercados gastronómicos activos permanentes.

## Puntos fuertes encontrados

### Fuentes oficiales / institucionales

Las respuestas identifican páginas de GCBA/Buenos Aires Ciudad y Turismo BA como anclas documentales para mercados y patios gastronómicos. En el export, varias URLs aparecen solo como `Link`, por lo que en los CSV se marcó `url_no_visible_en_export`.

### Mercados con datos operativos útiles

- **Mercado del Progreso**: 17 negocios a la calle y 174 puestos interiores; oferta amplia de bares, pizzerías, vinotecas, carnicerías, panaderías, pescaderías y otros rubros.
- **Mercado Bonpland**: horarios y oferta desde GCBA; gestión cooperativa/economía solidaria desde Argentina.gob.ar.
- **Mercado Belgrano**: oferta alimentaria desde GCBA; cifra de 37 locales y horarios diferenciados desde Instagram oficial/prensa.
- **Mercado San Nicolás**: horarios y oferta desde GCBA; cifra de 18 puestos/locales desde prensa.
- **Mercado Soho**: oferta y perfil desde Turismo BA; dirección/horarios desde prensa.

## Divergencias relevantes

1. **Mercado de San Telmo — horarios**: sitio propio: lunes a domingo, 9 a 20 h; Turismo BA en inglés: martes a viernes 10:30 a 19:30 y sábados/domingos/feriados 9 a 20 h.
2. **Mercado del Progreso — horarios**: aparece una divergencia entre 8 a 14 h y 8 a 18 h.
3. **San Telmo — mercado vs feria**: la Feria de San Telmo aparece asociada a antigüedades/objetos de colección y no debe confundirse con el Mercado de San Telmo.
4. **Mercat Caballito**: la fuente oficial recuperada es una mención en agenda/evento, no una ficha con dirección/horario propio.

## Posibles omitidos

- **Gourmand Food Hall**: revisar con prioridad alta. Podría ser un food hall, pero está dentro de Patio Bullrich; hay que definir si tiene entidad propia y foco gastronómico suficiente.
- **Mercado Fusión**: revisar con prioridad media-alta. Podría ser encuentro o feria temporal, no mercado permanente.
- **Food Fest / Festival del Sándwich / Sabor a Buenos Aires / Food Fest BA**: derivar a agenda de eventos gastronómicos, no al padrón de mercados activos.

## Archivos generados

- `fuentes_documentales_mercados_v2_1.csv`
- `afirmaciones_mercados_v2_1.csv`
- `contradicciones_y_brechas_v2_1.csv`
- `posibles_omitidos_documentales_v2_1.csv`
- `resumen_narrativo_documental_v2_1.md`

## Recomendación para integración al proyecto

Guardar estos archivos en:

```text
outputs/mercados_caba/sanitized/documental_v2_1/
```

Luego pedirle a Claude Code que los use para actualizar `fuentes_documentales_mercados_v2.csv`, `mercados_gastronomicos_posibles_omitidos_v2.csv` y el documento de enriquecimiento, sin cambiar el conteo de 15 activos salvo validación posterior.
