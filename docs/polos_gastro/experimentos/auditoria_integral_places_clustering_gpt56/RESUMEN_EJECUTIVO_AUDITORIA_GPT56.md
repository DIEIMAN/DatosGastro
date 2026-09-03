# Resumen ejecutivo de auditoría

## Veredicto

La nueva línea de trabajo mejora de forma clara la base de evidencia respecto de Fase 25, pero la cartografía actual no debe cerrarse como delimitación institucional. La recomendación es **PIPELINE_HIBRIDO_POR_TIPO_TERRITORIAL**.

Se partió de un universo semilla de 106 referencias geolocalizadas y de una lectura editorial de 22 polos/ejes en Fase 25. Luego se construyó un universo F01/F02 de 9.739 entidades y se incorporaron resultados almacenados de Google Places. Dentro de las 13 macrozonas estudiadas, el universo vigente tiene 6.461 puntos: 3.240 de F01/F02 y 3.221 Places.

Places aportó cobertura real. Cambió la lectura de varias zonas y permitió observar concentraciones que F01/F02 no mostraban con igual nitidez. Sin embargo, su peso llega a 93 % en Costanera Norte, 71 % en Puerto Madero y supera 60 % en Caballito, Chacarita, Villa Crespo y Caseros/Barracas. Esas zonas no deberían presentarse como firmes sin corroboración y decisión humana.

HDBSCAN mejora a DBSCAN porque no obliga a usar una única distancia para toda la Ciudad y maneja mejor densidades diferentes. El problema principal aparece después: los clusters grandes se subdividen con KMeans. Esa operación genera 91 de los 163 polígonos y afecta 57 % de los puntos asignados. En Corrientes y Caballito, toda la cartografía técnica depende de esas divisiones. KMeans resuelve el tamaño de las piezas, no el territorio; por eso produce tiles artificiales.

La simplificación editorial de 163 piezas a 41 grupos retenidos y luego a 31 unidades hace el mapa mucho más legible. Pero los nombres, fusiones, exclusiones y jerarquías son decisiones humanas incorporadas al código. Además, v4 conserva 16 pares de solape y v4.1 los corrige sólo en la capa de dibujo, sin reasignar puntos ni conteos.

La recomendación es usar métodos y representaciones distintos según el tipo de zona:

- polígonos o contornos de densidad para núcleos compactos;
- ejes con buffer para Corrientes, Puerto Madero y otros corredores/frentes;
- núcleos separados o comunidades espaciales para Belgrano, Microcentro, Villa Crespo y Chacarita;
- heatmap o puntos para zonas difusas o exploratorias;
- no mostrar aún unidades con alta dependencia Places y baja estabilidad.

Antes del nuevo informe, el equipo debe decidir nombres, fusiones, solapes, límites aproximados, inclusión en mapa principal y tratamiento de zonas exploratorias. También debe validar una muestra de deduplicación y reemplazar KMeans en los casos principales. No hace falta volver a llamar Places para tomar estas decisiones.

El próximo paso recomendado es un piloto metodológico corto en cuatro casos: Corrientes como corredor, San Telmo como núcleo compacto, Belgrano como red multinuclear y Costanera como señal sin polígono. Si esas cuatro representaciones funcionan y son entendibles para jefatura, se extiende el criterio a las demás zonas.

