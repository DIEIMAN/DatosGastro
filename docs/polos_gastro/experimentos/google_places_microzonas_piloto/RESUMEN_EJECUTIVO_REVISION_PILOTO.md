# Resumen ejecutivo — revisión editorial del piloto de microzonas

**Fecha:** 2026-07-09 · **EXPERIMENTAL — no oficial.** Base: 78 microzonas del piloto
(4 zonas, 6 macrozonas). Tabla completa: `outputs/.../revision/tabla_revision_editorial_microzonas.csv`.

**Balance de clasificación:** 23 APROBAR · 9 APROBAR CON OBSERVACIONES · 43 REVISAR
CORTE · 3 REVISAR UNIVERSO · 0 DESCARTAR/FUSIONAR.

## Hallazgos robustos

1. **El defecto que motivó el piloto está resuelto:** las 78 microzonas miden entre 0,9
   y 12,1 ha; ninguna ocupa una macrozona entera.
2. **Las dos fuentes ven la misma ciudad:** 92 % de las microzonas combinan F01+F02 y
   Google Places (20–80 % de cada una). Es la validación cruzada más fuerte del piloto.
3. **San Telmo es el caso limpio:** 8 de 8 microzonas aprobables, alineadas al eje
   Defensa (Plaza Dorrego, Mercado de San Telmo); el resto de la macrozona queda vacío —
   el método distingue el núcleo real y no arrastra por cercanía.
4. **Palermo detecta sus corredores con nombre propio:** Plaza Serrano, Honduras/
   Armenia y el eje Fitz Roy emergen como núcleos separados, sin volver a la macrozona
   gigante (el núcleo de 58 ha de la validación anterior no reaparece).
5. **Places le dio estructura real a Belgrano:** pasó de 2 masas amorfas a 5 clusters;
   apareció un núcleo aislado con 74 % Places en el entorno de Barrio Chino que F01+F02
   solo no veía — coincide con la pregunta abierta de la revisión de macrozonas (los 53
   locales huérfanos de Belgrano).
6. **Evidencia concreta de mejora con Places:** +1.651 puntos (+76 %); el ruido bajó en
   Soho (47 %→33 %), Corrientes (25 %→17 %) y Microcentro (22 %→6 %); el polígono máximo
   de Corrientes bajó de 11,7 a 10,0 ha.

## Pendientes editoriales

7. **Corrientes/Microcentro es un continuo, no un mosaico:** sus 29 piezas de
   subdivisión son cortes geométricos dentro de un corredor denso continuo. El corredor
   es real; los límites internos no. Redibujar a mano por cruces reconocibles (Callao,
   Obelisco, peatonales) antes de usar.
8. **Belgrano necesita la separación editorial pendiente:** 14 de 17 piezas son cortes
   automáticos sobre Cabildo/Juramento. Las señales para separar Barrio Chino / Bajo
   Belgrano / eje Cabildo ya están en los datos; el trazado debe ser editorial.
9. **Tres microzonas dependen ≥70 % de Places** (entorno Barrio Chino, peatonal
   Lavalle/Florida, un núcleo de Soho): verificar contra registro antes de aprobar —
   pueden ser oferta nueva real o sesgo de prominencia de Google.
10. **Places mide prominencia, no censo** (máx. 20 resultados por celda): en corredores
    saturados los conteos son piso, no total. No usar para comparar volúmenes absolutos
    entre zonas.
