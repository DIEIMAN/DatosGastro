# Segunda pasada jerárquica sobre clusters sobredimensionados (Etapa V2-4)

**Fecha:** 2026-07-08 · **Carácter:** prueba experimental paralela. No reemplaza el
detector de la Etapa 3 ni cambia ningún parámetro global — corre solo sobre los 6
clusters que ya superaban el gate de 35 ha, tomando cada uno como universo propio.

**Método:** para cada cluster sobredimensionado, HDBSCAN otra vez con
`min_cluster_size = max(5, 3 % de sus puntos)`, `cluster_selection_epsilon = 25 m` (mitad
del valor de la Etapa 3, porque se subdivide una zona ya densa) y
`cluster_selection_method = "leaf"` (extrae hojas de la jerarquía, más granular que
`eom`). Script: `s07_segunda_pasada.py`. Mapas antes/después en
`outputs/.../segunda_pasada/mapas/`.

## Resultado agregado

| Macrozona | Cluster | n original | ha original | Subclusters | Ruido 2ª pasada |
|---|---|---|---|---|---|
| Microcentro y Centro | C0 | 432 | 91,8 | 10 | 36 % |
| Palermo | C2 | 244 | 86,9 | 11 | 37 % |
| Palermo | C5 | 242 | 72,8 | 10 | 39 % |
| Microcentro y Centro | C4 | 190 | 60,7 | 11 | 29 % |
| Avenida Corrientes | C7 | 133 | 46,5 | 11 | 29 % |
| Belgrano | C2 | 88 | 42,0 | 3 | **61 %** |

**Los 6 casos se dividen** (nunca queda un único subcluster monolítico), pero con un costo
de ruido que sube respecto de la Etapa 3 (20–34 %) a 29–39 % — y en un caso, 61 %.

## Lectura cualitativa (mapas antes/después)

- **Microcentro C0 (432→10) y Corrientes C7 (133→11):** la segunda pasada revela una
  estructura de "cuadras calientes" bien definida y espacialmente separada — no era una
  sola cosa, eran ~10 focos discretos que el detector de la Etapa 3 no podía separar
  porque, vistos desde afuera, forman un bloque continuo sin huecos claros al ojo (la
  distribución es casi de grilla uniforme). Es el resultado **más útil** de los seis: pasa
  de "todo el microcentro es denso" (poco accionable) a 10 focos concretos.
- **Palermo C2 y C5 (244→11, 242→10):** mismo patrón — aparecen 10-11 focos chicos y
  compactos, separados por huecos que antes quedaban enmascarados dentro del polígono
  monolítico. Consistente con la hipótesis del diagnóstico editorial (Palermo Soho y
  Hollywood probablemente tienen 2-3 corazones cada uno, no uno solo).
- **Belgrano C2 (88→3, ruido 61 %):** caso distinto y más débil. El cluster original era
  alargado (spanea Barrio Chino + Cabildo/Juramento + Bajo Belgrano, según el diagnóstico
  editorial). La segunda pasada solo logra formar 3 grupos chicos en el extremo más denso
  y **descarta como ruido la mitad norte entera** (la punta hacia Bajo Belgrano). No es una
  subdivisión limpia en 2-3 identidades editoriales: es una poda severa. Con un cluster
  alargado y de densidad decreciente hacia los extremos, `epsilon=25 m` es agresivo — un
  valor intermedio (35-40 m) probablemente conservaría más puntos sin volver a fusionar
  todo.

## Conclusión de la Etapa V2-4

**La segunda pasada demuestra que SÍ mejora la interpretabilidad en clusters grandes y
razonablemente homogéneos** (Microcentro, Palermo, Corrientes): convierte un polígono
"todo es denso" en un puñado de focos concretos, que es justamente lo que un informe
editorial necesita. **No funciona igual de bien en clusters grandes pero alargados y de
densidad decreciente** (Belgrano): ahí poda en vez de subdividir.

Recomendación para una futura V2 (no implementada aún, ver Etapa V2-7): condicionar la
segunda pasada a la forma del cluster original — aplicar `leaf + epsilon chico` solo
cuando el cluster es compacto (compacidad alta, elongación baja) y usar un epsilon mayor
(o directamente no forzar la segunda pasada) cuando el cluster sobredimensionado es
alargado como Belgrano C2.
