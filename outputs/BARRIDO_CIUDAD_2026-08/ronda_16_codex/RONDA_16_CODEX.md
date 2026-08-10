# Ronda 16 · correspondencia, solapamientos y borde de Palermo

Estado: **EXPERIMENTAL / NO OFICIAL**. Corrida local, sin red ni APIs. Esta ronda mide; no adopta
fusiones ni ampliaciones.

## 1. Soportes

El universo tiene **41 polos admitidos**: **31** con soporte
REAL y **10** con soporte PROVISORIO. Los cuatro cierres
parciales de ronda 15 no se usan como si fueran el polo completo.

Palermo R01 se reconstruyó como el sistema publicado `R01 ∪ P091 ∪ P078 ∪ P065`: 
**385,51 ha**
y **1.916**
registros del universo ERR-10.

## 2. Correspondencia 124 × 41

Se obtuvieron **143 pares** con intersección mayor a 0.01 m²:
**95 publicables** y
**48 pendientes de perímetro**.
La tabla declara ambos soportes y ambos denominadores. Las concentraciones sin cruce en los
soportes actuales permanecen identificadas como pendientes mientras existan
**10 soportes provisorios**.

## 3. Matriz 41 × 41

La matriz contiene los **820 pares no ordenados**. Hay **31** pares con intersección
material; **14** tienen ambos soportes reales y pueden leerse territorialmente.
Otros **355** pares quedan clasificados `PENDIENTE DE PERÍMETRO` porque al menos un
lado es provisorio, tengan o no intersección observada.

Z54–Z40 queda correctamente bloqueado: intersección observada
**504.234,53 m²**, relación observada `CONTENIDA`, clase final
**`PENDIENTE DE PERÍMETRO`**. No se emite recomendación.

Pares reales con mayor superficie de intersección (hasta 20):

| polo_A | polo_B | interseccion_ha | pct_area_A | pct_area_B | locales_compartidos | pct_locales_A | pct_locales_B | clase |
|---|---|---|---|---|---|---|---|---|
| R19 | Z43 | 67.02 | 22.1 | 29.26 | 115 | 21.62 | 26.08 | SOLAPADA |
| R09 | R19 | 60.37 | 63.68 | 19.91 | 153 | 75.74 | 28.76 | SOLAPADA |
| R08 | R21 | 49.68 | 14.81 | 12.89 | 91 | 11.06 | 29.64 | SOLAPADA |
| R01 | R19 | 22.86 | 5.93 | 7.54 | 98 | 5.11 | 18.42 | SOLAPADA |
| R02 | R12 | 21.72 | 43.73 | 11.8 | 133 | 37.57 | 12.27 | SOLAPADA |
| R01 | R08 | 12.55 | 3.26 | 3.74 | 77 | 4.02 | 9.36 | SOLAPADA |
| R12 | Z47 | 8.68 | 4.71 | 62.98 | 76 | 7.01 | 57.14 | SOLAPADA |
| R01 | Z43 | 7.85 | 2.04 | 3.43 | 8 | 0.42 | 1.81 | SOLAPADA |
| R08 | R19 | 7.78 | 2.32 | 2.56 | 1 | 0.12 | 0.19 | SOLAPADA |
| R19 | R21 | 7.25 | 2.39 | 1.88 | 5 | 0.94 | 1.63 | SOLAPADA |
| R09 | Z43 | 6.91 | 7.29 | 3.02 | 21 | 10.4 | 4.76 | SOLAPADA |
| R01 | R09 | 4.3 | 1.12 | 4.54 | 9 | 0.47 | 4.46 | SOLAPADA |
| R09 | R21 | 2.25 | 2.37 | 0.58 | 4 | 1.98 | 1.3 | SOLAPADA |
| R11 | Z50 | 1.55 | 3.1 | 3.06 | 3 | 5.0 | 3.57 | SOLAPADA |

Entre los 14 cruces positivos con ambos soportes reales hay
**0 contenciones completas**: los 14 son solapamientos parciales. Entre los
cruces bloqueados aparece otro caso que parecería contención si se ignorara el soporte: Z52–Z53
da **61.375,73 m²** y 3 registros,
pero Z53 sigue representada por La Boca y la clase correcta es `PENDIENTE DE PERÍMETRO`.

## 4. Palermo · 584 registros en seis concentraciones

El control de pertenencia de las seis concentraciones reproduce **584**
registros, que es el número del Anexo B. El recuento espacial de puntos que caen dentro de los seis
polígonos generalizados da **582**. No reemplaza al
primero: los polígonos de representación pueden incluir o dejar fuera puntos de su agrupamiento.
Por eso se publican las dos columnas y se conserva 584 como denominador de las concentraciones.
La clasificación de continuidad usa 40 m, fijados antes de correr; se publican también los cortes
20/60/80/120 m.

| concentracion_id | nombre | ha | locales_concentracion | locales_en_poligono | interseccion_con_sistema_m2 | distancia_m | componente_mas_cercano | clase_continuidad_40m |
|---|---|---|---|---|---|---|---|---|
| P073 | Palermo Botánico | 39,19 | 207 | 207 | 0.0 | 717,97 | R01_BASE | OBJETO_APARTE_A_40M |
| P087 | Palermo Pacífico | 5,80 | 56 | 47 | 0.0 | 207,73 | P078_PALERMO_HOLLYWOOD | OBJETO_APARTE_A_40M |
| P092 | Villa Freud | 11,71 | 79 | 79 | 0.0 | 34,65 | R01_BASE | CONTINUA_CON_EL_SISTEMA_A_40M |
| P088 | Palermo · Gascón y Honduras | 7,79 | 76 | 69 | 0.0 | 16,15 | P091_PALERMO_SOHO | CONTINUA_CON_EL_SISTEMA_A_40M |
| P064 | Palermo · Plaza Italia y Av. del Libertador | 9,12 | 45 | 39 | 0.0 | 432,73 | R01_BASE | OBJETO_APARTE_A_40M |
| P104 | Alto Palermo | 24,85 | 121 | 141 | 0.0 | 888,80 | R01_BASE | OBJETO_APARTE_A_40M |

No se propone ampliación del perímetro. La decisión de delimitación queda para Diego.

## 5. Límites y gates

- Universo: `anillo == 'nucleo' AND apto_geometria == True`, **23.981 registros**.
- CRS métrico: EPSG:5347.
- Contención: superficie perdida, tolerancia 1 m²; no se usa `covers()`.
- Intersección material: mayor a 0,01 m².
- Los conteos describen registros del universo analítico, no actividad comercial vigente.
- Fuentes originales y pipeline F01–F05: sólo lectura.
