# Fase23 no entregable - Regresiones visuales

## Decisión

Fase23 no queda aprobada como versión de oficina. La comparación visual página por página muestra
que, aunque corrige algunos textos y aumenta la escala de los mapas, empeora el equilibrio general
frente a fase22: reduce aire visual, tensiona encuadres, acerca etiquetas y leyendas a bordes y en
algunas páginas deja elementos truncados o demasiado pegados al límite del mapa.

La base para cualquier entrega de oficina debe volver a ser fase22, salvo que se abra una nueva
corrección visual controlada sobre una copia y con criterios acotados.

## PDF comparados

- Fase22: `outputs/polos_gastro/fase22_microajustes_texto_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_TEXTO.pdf`
- Fase23: `outputs/polos_gastro/fase23_microajustes_mapas_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_MAPAS.pdf`
- Entrega fase23: `outputs/polos_gastro/entrega_oficina_fase23/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA.pdf`

## Regresiones detectadas

| Página | Elemento | Fase22 | Fase23 | Diagnóstico | Severidad |
| --- | --- | --- | --- | --- | --- |
| 3 | Recuadro de lectura institucional | Recuadro ancho, apoyado en la grilla inferior, con aire y lectura estable. | Recuadro mucho más chico y desplazado hacia la derecha inferior. | La página gana corrección textual, pero pierde jerarquía visual y equilibrio de cierre. | media |
| 5 | Mapa general | Mapa grande, centrado y con buena respiración respecto de la caja de lectura. | Mapa más chico dentro de un bloque con trama y leyenda interna; queda con más presión visual en la zona inferior. | La composición pierde presencia territorial y aire; la leyenda interna suma ruido y reduce claridad. | media |
| 7 | Palermo / Las Cañitas | Mapa contenido, con márgenes amplios y relación equilibrada entre mapa y cajas inferiores. | Mapa ampliado hasta ocupar casi todo el ancho; polígonos y rótulos quedan cerca de los bordes. | El aumento de escala mejora lectura de algunas etiquetas, pero empeora el aire visual y deja una composición más pesada. | media |
| 8 | Puerto Madero | Mapa vertical contenido; eje costero y rótulos quedan dentro del encuadre. | El mapa ampliado corta parcialmente el borde superior/derecho del área y tensiona el eje costero. | Hay pérdida de encuadre y elementos pegados al límite; el mapa queda menos prolijo como pieza de oficina. | crítica |
| 9 | San Telmo | Mapa compacto, con rótulos contenidos y composición clara. | Mapa ampliado con rótulos más grandes y elementos muy próximos a los bordes superior e inferior. | Se reduce el aire visual y el área gastronómica domina de forma excesiva el plano. | media |
| 10 | Corrientes / Abasto | Composición panorámica con separación clara entre Abasto y eje Corrientes. | Mapa ampliado; Abasto queda más pesado y la zona Obelisco/teatros se acerca al margen derecho. | El encuadre mejora algo la legibilidad de etiquetas, pero la página pierde balance horizontal. | media |
| 11 | Belgrano | Mapa panorámico con tres sectores visibles y margen suficiente. | Bajo Belgrano queda pegado al borde derecho y parcialmente tensionado por el recorte; la leyenda compite con Belgrano R. | Regresión clara de encuadre: elementos relevantes quedan demasiado cerca del margen y la lectura se vuelve más forzada. | crítica |

## Recomendación

Volver a fase22 como base visual principal para cualquier entrega de oficina. Si se necesita
corregir texto, encoding o rótulos, hacerlo más adelante sobre una copia controlada de fase22, con
criterio mínimo y revisión renderizada página por página, manteniendo 11 páginas.

## Qué NO hacer

- No seguir corrigiendo sobre fase23.
- No usar `entrega_oficina_fase23` como entregable.
- No abrir ajustes amplios de diseño.
- No regenerar todo el informe desde cero.
