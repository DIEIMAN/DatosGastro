# Ronda 22 — base estructural candidata

**Estado:** REVISION. Producción técnica terminada; requiere auditoría independiente antes de cualquier integración.

## Resultado

- Base candidata: **225 establecimientos/referentes**. Parte de R11 (225), excluye H064 y agrega El Sol de Galicia.
- Bares Notables canónicos: **90**. Bar Iberia permanece por constar como orden 10 en la Resolución MCGC 1225/26; sale La Esquina de Aníbal Troilo, preservada como antecedente.
- Geometrías: **39/39 válidas**, sin vacíos. R12 fue reparada; R08 pasó por el mismo procedimiento y resultó idéntica con la versión local de GEOS.
- Conteos R22: **10,819 locales únicos**, **11,119 ocurrencias en fichas**, **300 duplicaciones**. No hay pertenencias triples.
- Vía A: **9 divergencias reconciliadas**; ningún caso pierde admisión.
- Referentes asignados a fichas: **167 únicos / 190 relaciones referente–polo**. Quedan **5** sin coordenada y **52** relaciones documentales fuera de geometría identificadas.

## Decisiones estructurales aplicadas sólo a la candidata

- Café/Bar Olimpo: Bar Olimpo como nombre normativo, Café Olimpo como alias; Irigoyen 1491, Monte Castro, Comuna 10; verificación humana del 07/08/2026. El registro OLIMPO de Arregui 5794 se mantiene separado y fuera del canon vigente.
- Baek-ku: unidad independiente; sin relación de subzona con Parque Avellaneda.
- Z54: `pieza_anidada`, padre Z40, ficha propia y exclusión del total global aditivo.
- Chacagiales: sistema con Chacarita, Federico Lacroze y Colegiales; la continuidad documentada es de 732 locales a ≤120 m. Villa Ortúzar conserva identidad propia y relación `FUERTE_CONTINUIDAD_CON_CHACAGIALES`: la prueba conjunta alcanza 795 locales e incluye 69/69 de Villa Ortúzar, sin fusión.
- Warnes: se conserva la variante adoptada por masa propia; “al este” queda como antecedente editorial, no como algoritmo.

## Alcance

La base masiva `base/local.csv` se usa sólo como instrumento de pertenencia y conteo. No se convierte oferta registrada en actividad actual. Overture se conserva como señal espacial y no se usa para inferir apertura o cierre. No hubo red, APIs, Places, descargas, clustering, PDF, cambios de criterio de admisión ni edición de Atlas V2/R21.
