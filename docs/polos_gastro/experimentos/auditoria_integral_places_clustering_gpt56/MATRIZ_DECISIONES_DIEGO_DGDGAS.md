# Matriz de decisiones de Diego / DGDGAS

Estas decisiones no deben resolverse automáticamente. La recomendación técnica es no vinculante.

| Zona | Problema | Opciones | Evidencia a favor / en contra | Impacto visual / metodológico | Recomendación no vinculante | Decisión requerida | Urgencia / bloquea |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Palermo Soho | HDBSCAN sensible y límite con Palermo Hollywood | una unidad; núcleos; polígono compacto | 673 puntos, 44,6 % Places; bootstrap 0,37 | Cambia número y borde de piezas | Usar núcleo compacto + KDE; no fijar límite común aún | Definir si Soho es unidad única | Alta / sí |
| Palermo Hollywood | Red multinuclear | un polígono; núcleos separados | estabilidad media; 41,0 % Places | Un polígono oculta vacíos | Núcleos separados bajo nombre paraguas | Jerarquía y nombre | Media / sí para mapa principal |
| San Telmo | Mercado, Defensa y casco histórico se solapan conceptualmente | núcleo; eje; combinación | 46,6 % Places; ruido 34,1 %; estabilidad media | Polígono único puede sobregeneralizar | Núcleo Mercado/casco + eje Defensa | Alcance del nombre “San Telmo” | Alta / sí |
| Corrientes | 23 tiles KMeans sobre un corredor | corredor único; tramos; no mostrar polígonos | detector estable; 39,9 % Places; KMeans total | Gran cambio de lenguaje cartográfico | Eje con buffer y 2-3 tramos nombrados | Número y nombres de tramos | Alta / sí |
| Microcentro | Solape funcional con Corrientes/Centro | fusionar; separar núcleos; jerarquía | 31,0 % Places; estabilidad media; 11 unidades actuales | Riesgo de doble conteo visual | Separar núcleos peatonales y administrativos; evitar solape | Límite Corrientes-Microcentro | Alta / sí |
| Belgrano | Partición inestable y cuatro unidades v4 | macroárea; Barrio Chino/Bajo/Cabildo separados | 56,4 % Places; bootstrap 0,14 | Puede contradecir lectura Fase 25 | Mantener jerarquía Fase 25 y usar puntos/heatmap como evidencia | Fusión/separación y nombres | Alta / sí |
| Caballito | 33 tiles; 60,4 % Places | 3-4 corredores/núcleos; anexo | HDBSCAN base estable, pero KMeans domina | Teselación ilegible y artificial | No mostrar v4 como límites; definir Acoyte/Rivadavia/Goyena con evidencia urbana | Qué unidades merecen nombre | Alta / sí |
| Recoleta | Área extensa y difusa | polígono; heatmap; núcleos | 47,3 % Places; epsilon 100 cambia fuerte | Mancha amplia sugiere límite inexistente | Heatmap + 2-3 núcleos | Si entra al principal y con qué nombre | Media / no si queda anexo |
| Villa Crespo | Alta dependencia e inestabilidad | fusionar; núcleos; no mostrar | 60,5 % Places; mediana local ARI 0,06 | Riesgo alto de sobreajuste | No mostrar aún; probar comunidades/grafo | Inclusión/exclusión | Alta / sí |
| Chacarita | 65,5 % Places y celdas refinadas parcialmente | núcleo central; corredor; anexo | estabilidad baja; refino de 2 celdas saturadas | Puede confundir Chacarita con bordes vecinos | Mantener anexo y validar central/Lacroze | Jerarquía y frontera con Villa Crespo | Alta / sí |
| Puerto Madero | Frente lineal convertido en manchas; 71,1 % Places | docks como eje; norte/sur; polígonos | estabilidad alta; fuente dependiente | Corredor representa mejor la costa | Eje/buffer sobre docks, con norte/sur sólo si se valida | Número de frentes y nombres | Alta / sí |
| Costanera Norte | 93,1 % Places | puntos; eje; excluir | 5 F01/F02 y 67 Places | Polígono aparenta validación inexistente | Puntos o señal exploratoria, nunca polígono principal | Inclusión en anexo | Media / no si se excluye |
| Caseros/Barracas | Corredor con 69,0 % Places | corredor; señal; excluir | sólo 18 F01/F02; estabilidad alta | Eje legible, polígono engañoso | Corredor exploratorio con nota | Nombre y alcance | Media / no si queda anexo |
| Todas | 16 pares de solape v4 | aceptar; recortar; redibujar; jerarquizar | 144 ha acumuladas; v4.1 recorta sólo dibujo | El mapa puede sugerir doble pertenencia | Resolver por jerarquía y reasignar puntos si cambia geometría analítica | Regla institucional de solape | Alta / sí |
| Todas | 14 exclusiones entre v2 y v3 | confirmar; reabrir | exclusiones completas y trazables, pero manuales | Cambia universo mostrado | Confirmar una por una con motivo | Aprobación de exclusiones | Alta / sí |
| Todas | Nombres orientativos | aprobar; renombrar; dejar genérico | no existe nomenclatura oficial única | Impacto político alto | Usar nombres conocidos y etiqueta “área/eje de lectura” | Aprobación nominal | Alta / sí |

