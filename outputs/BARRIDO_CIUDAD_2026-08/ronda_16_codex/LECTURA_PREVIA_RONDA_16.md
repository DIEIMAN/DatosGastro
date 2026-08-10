# Lectura previa · ronda 16 Codex

Estado: **EXPERIMENTAL / NO OFICIAL**. Esta lectura se fija antes de ejecutar las mediciones.

## Universo y proyección

- Registros: `base/local.csv` filtrado por `anillo == 'nucleo' AND apto_geometria == True`.
- Gate esperado: **23.981 registros** con coordenadas.
- Superficies y distancias: **EPSG:5347**.
- Las 124 concentraciones provienen de `borrador_polos/polos_publicables.geojson` y se consideran
  soportes reales del instrumento de concentración.
- Los 41 polos son únicamente las filas con `categoria_por_criterio == 'polo admitido'` en
  `criterio_admision_55.csv`.

## Regla de soporte

1. Los 23 polos que no integraron la lista de 18 sin perímetro conservan su geometría propia y
   se marcan **REAL**.
2. Entre los 18 de `ronda_15/perimetros_18.csv`, sólo `cerrado_si_no == 'si'` permite usar como
   geometría del polo la unión de sus piezas en `ronda_15/geometria/perimetros_18.geojson` y se
   marca **REAL**.
3. `parcial` no representa al polo completo: se conserva el soporte anterior y se marca
   **PROVISORIO**. `no` también queda **PROVISORIO**.
4. Cuando el soporte anterior es un barrio compartido, se declara el alias usado (`S_BARRACAS`,
   `S_LABOCA` o `Z40`) y no se interpreta como borde del polo.
5. Z54 conserva el soporte **P024**, declarado REAL en la medición firmada de ronda 15. Que su
   perímetro textual no haya cerrado no convierte a P024 en el barrio; sólo Z40 queda provisorio.
6. Palermo R01 se mide con el sistema publicado: unión de R01 con P091 Palermo Soho, P078 Palermo
   Hollywood y P065 Las Cañitas. Ese sistema es **REAL**; no se usa la pieza R01 aislada.

Lectura esperada por construcción: **31 soportes reales y 10 provisorios**.

### Corrección del inventario previa a la corrida válida

Una primera ejecución diagnóstica asignó a Z54 el alias barrial Z40 y produjo dos geometrías
idénticas de 870,07 ha. Esa salida se descartó: contradecía el input explícito de la tanda
(`Z54 = P024, REAL`; `Z40 = barrio, PROVISORIO`) y reproducía el error que esta regla debe evitar.
No se cambió ningún umbral ni se usó el resultado para elegir geometría; se corrigió la lectura
del soporte declarado antes de generar la corrida válida.

## Correspondencia 124 × 41

- Se calcula toda intersección de superficie y se conservan pares con área mayor a **0,01 m²**;
  el umbral es el mismo control de ruido geométrico de ronda 14.
- Cada fila declara `soporte_es_real_A` y `soporte_es_real_B`.
- Un par va a `PUBLICABLE` sólo si ambos soportes son reales; si el polo usa soporte provisorio,
  va a `PENDIENTE_DE_PERIMETRO`.
- Se informan ambos denominadores de superficie. No se fuerza una asignación exclusiva de cada P.

## Matriz 41 × 41

- Se generan los **820 pares no ordenados** (`41 × 40 / 2`), incluidos los disjuntos.
- Para cada par se miden: intersección; superficie perdida de A y B; registros compartidos;
  total de registros de A y B; y porcentaje compartido en ambos sentidos.
- La contención se prueba por superficie perdida. Tolerancia preinscrita: **1 m²**.
- Clase:
  - si algún soporte es provisorio: `PENDIENTE DE PERÍMETRO`, sin recomendación;
  - con ambos soportes reales e intersección ≤ 0,01 m²: `DISJUNTA`;
  - con ambos soportes reales y pérdida ≤ 1 m² en al menos un lado: `CONTENIDA`;
  - en otro caso con intersección positiva: `SOLAPADA`.
- La matriz no decide fusiones ni ampliaciones.

## Palermo · seis concentraciones exteriores

Objetos: P073 Botánico, P087 Pacífico, P092 Villa Freud, P088 Gascón y Honduras, P064 Plaza Italia
y Av. del Libertador, y P104 Alto Palermo. El control previo es que sus conteos de la capa sumen
**584**.

- Se mide cada geometría contra el borde del sistema publicado de Palermo.
- Se reportan superficie, registros del universo ERR-10, intersección y registros compartidos.
- `distancia_al_borde_m` es la distancia mínima en EPSG:5347 entre la concentración y el borde
  del sistema.
- La continuidad se clasifica al umbral común ya usado por el atlas para la vía A: **40 m**.
  Distancia ≤ 40 m → `CONTINUA_CON_EL_SISTEMA_A_40M`; distancia > 40 m →
  `OBJETO_APARTE_A_40M`.
- Para no esconder dependencia del parámetro, se incluyen además indicadores a 20, 60, 80 y
  120 m. No se propone ampliación: la delimitación queda para Diego.
