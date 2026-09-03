# Especificación de repetición — Puerto Madero (frente gastronómico)

Estado: EXPERIMENTAL / NO OFICIAL. Fecha de corte: 2026-07-10.
Es un diseño: **no ejecuta nada**. La corrida es local; no requiere APIs, Google Places
ni descargas.
Plan de pruebas tabulado: `outputs/.../decisiones_y_repeticiones_pipeline_hibrido_v1/tabla_plan_pruebas_puerto_madero.csv`.
Inventario de soportes verificado: `outputs/.../decisiones_y_repeticiones_pipeline_hibrido_v1/inventario_ejes_viales_puerto_madero.csv`.

## 1. Problema a resolver

El prototipo v1 tiene la estructura de puntos más estable de las cinco zonas (robustez
por bloques 0,86 con p10 0,81) pero el frente dibujado asigna **102 de 294 puntos
(34,7 %)**: 192 puntos quedan a más de 180 m del único soporte usado (Alicia Moreau de
Justo, lado oeste de los diques), que además quedó disuelto en 18 componentes.
La robustez alta es del patrón de puntos, no del frente: **no debe interpretarse 0,86
como cobertura suficiente**.

La sospecha de soporte territorial incompleto queda confirmada por el inventario del
callejero local: existen ejes paralelos del lado este de los diques que el prototipo no
consideró.

## 2. Inventario de soportes locales existentes (verificado, no inventado)

Fuente: `callejero_gcba_2026_06_02.geojson` (capa local, 31.961 tramos) recortado al
contenedor MZ_PUERTO_MADERO + 50 m. Ejes relevantes por longitud dentro del recorte:

| Eje (nomoficial) | Longitud en zona | Posición urbana |
| --- | ---: | --- |
| `MOREAU DE JUSTO, ALICIA AV.` | 4.411 m | frente oeste de los diques (usado en v1) |
| `MANSO JUANA` | 3.876 m | eje este, paralelo a los diques |
| `HUERGO, ING. AV.` | 3.802 m | borde oeste del barrio (vía distribuidora; no frente gastronómico a priori) |
| `DEALESSI, PIERINA` | 2.873 m | ribera este de los diques (tramo norte) |
| `MADERO, EDUARDO AV.` | 2.181 m | borde oeste, tramo norte |
| `GORRITI JUANA MANUELA` | 2.851 m | este del barrio |
| `COSSETTINI, OLGA` | 1.650 m | ribera este de los diques (tramo sur) |
| `DE LOS ITALIANOS AV.` | 1.635 m | este, hacia Costanera Sur |
| Transversales: `GUEMES, MACACHA` (1.234 m), `VILLAFLOR, AZUCENA` (1.402 m), `VERA PEÑALOZA, ROSARIO` (1.437 m), `LANTERI JULIETA` (1.017 m) | | conexiones oeste–este entre diques |

Limitaciones del soporte (declaradas, no salvables localmente):

- El callejero **no incluye hidrografía ni geometría de los diques** (limitación ya
  registrada en `inventario_capas_urbanas_locales.csv` del v1). "Ambos lados de los
  diques" se aproxima con los ejes viales de cada margen; el espejo de agua no se puede
  dibujar con las capas actuales.
- Los nombres de ejes provienen del campo `nomoficial` del callejero GCBA; no se
  inventó ningún eje ni tramo.

## 3. Opciones de representación a comparar

Todas se construyen con la misma técnica del v1 (tramos respaldados por puntos a
distancia D, disolución, buffer), variando soporte y parámetros:

- **PM-A (línea de base):** frente único sobre AMJ, D = 180 m — reproduce v1.
- **PM-B (hipótesis principal):** frente doble — AMJ (margen oeste) + eje este
  compuesto por Juana Manso y/o Pierina Dealessi + Olga Cossettini, según qué tramos
  queden respaldados. La composición exacta del eje este la deciden los datos
  (respaldo por tramo), no una preferencia.
- **PM-C:** segmentación norte/centro/sur del mejor frente de A/B, derivada de valles
  del perfil longitudinal (no impuesta). Los rótulos N/C/S son códigos, no nombres.
- **PM-D:** varios frentes cortos — solo componentes respaldadas de longitud ≥ 300 m,
  publicadas como piezas.
- **PM-E:** frente con buffer variable por densidad (p. ej. 120/180/240 m por terciles,
  análogo a Corrientes 60/90/120).
- **PM-F:** frente(s) + puntos de contexto — todo punto no asignado se muestra como
  capa de contexto (interactúa con DH-09).

## 4. Métricas por opción (todas obligatorias)

1. Puntos asignados y **% del universo cubierto** (294 puntos).
2. Densidad por km de frente.
3. Composición por fuente dentro y fuera (F01/F02 vs. Places; el universo es 71,1 %
   Places — reportar siempre junto a la cobertura).
4. Continuidad: nº de componentes tras disolución, longitud total, longitud de la
   componente mayor, huecos > 200 m sobre el eje.
5. Estabilidad por bloques de la **asignación** (no solo del clustering): repetir el
   submuestreo por bloques y medir qué fracción de puntos cambia de asignado/no
   asignado (bloques 200/300 m, 50 repeticiones).
6. Puntos aislados: a > 250 m de todo frente de la opción.
7. Dependencia del borde: puntos asignados a ≤ 100 m del borde del contenedor;
   sensibilidad de la opción al encogimiento de 100 m.
8. Solapamiento entre frentes (opciones B/D): % de puntos asignables a más de un
   frente con D actual; regla de desempate documentada (frente más cercano).
9. Superficie de banda total (ha) y % del área del barrio que ocupa la banda —
   insumo del criterio anti–"banda gigantesca".

## 5. Criterio de selección (definido antes de correr)

- **No se elige la opción de mayor cobertura por sí sola.** Se busca equilibrio entre
  cobertura, continuidad y lectura urbana.
- Reglas de descarte (anti falsa precisión):
  - descartar toda opción que necesite D > 250 m o banda > 40 % del área del barrio
    para superar a otra en cobertura;
  - descartar segmentaciones (PM-C) cuyos cortes no coincidan con valles reproducibles
    del perfil en ≥ 2 tamaños de bin;
  - ninguna opción se publica sin su cifra de cobertura al lado.
- Zona objetivo razonable (orientativa, no vinculante): cobertura ≥ 60 % con D ≤ 180 m
  y ≤ 4 componentes por frente. Si ninguna opción la alcanza, el resultado es
  igualmente válido: significa que parte de la oferta de Puerto Madero no es "de
  frente" y debe tratarse vía DH-09 (contexto), no estirando buffers.
- La decisión final entre opciones que empaten en métricas es humana (DH-06):
  Diego + revisión cartográfica.

## 6. Dudas que esta repetición NO puede cerrar (y cómo se cerrarían)

| Duda | Vía futura posible | Condición |
| --- | --- | --- |
| ¿La oferta del margen este es mayor que la registrada? (tramo norte del perfil: 87 % Places) | consulta quirúrgica Places en celdas del borde este | solo si tras PM-B la cobertura del margen este queda ambigua; ver `PLAN_CONSULTAS_QUIRURGICAS_PLACES_FUTURAS.md` (QP-04) — hoy ESPERAR |
| ¿Hay estructura fuera del contenedor? | anillo externo 200 m ya almacenado (42 F01/F02 + 46 Places): rededuplicar e incorporar es decisión aparte | sin API; requiere rededuplicación formal |
| ¿Los diques como objeto cartográfico? | mejor callejero/capa hidrográfica oficial GCBA | descarga nueva = fuera de alcance de esta tanda; requiere permiso |
| ¿Qué frente "es" gastronómicamente relevante más allá de los conteos? | revisión humana (Diego/DGDGAS conocen el terreno) | ficha DH-06 |

## 7. Qué NO hace esta repetición

- No consulta APIs ni Google Places; no descarga capas nuevas.
- No modifica el universo ni el prototipo v1 (PM_FRENTE_01 queda como línea de base).
- No impone nombres norte/centro/sur: si PM-C gana, los tramos llevan códigos hasta
  DH-06.
- No corre hasta que Diego apruebe el protocolo (DH-06).
