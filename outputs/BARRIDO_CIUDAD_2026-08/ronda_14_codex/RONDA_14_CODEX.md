# Ronda 14 · Codex

Estado: **EXPERIMENTAL / NO OFICIAL**. Cero requests a APIs.

## 1. Correspondencia 124 × 42

Se cruzaron 124 polígonos P con 41 fichas no rechazadas y el corredor Av. Montes de Oca 280–1702. Se obtuvieron **171 pares con intersección de superficie**. La tabla incluye ambos sentidos y ambos denominadores. Quedaron **19 P sin R/Z** y **1 R/Z sin P**; las listas están en las secciones `P_SIN_RZ` y `RZ_SIN_P` del CSV.

## 2. Calles dominantes

Se regeneró el ranking de las nueve filas señaladas y se conservaron las otras 115. El diff quedó en **9 filas**. `test_callejero_canonico.py`: **14/14 pruebas aprobadas**, incluido el control negativo San Martín.

## 3. Curvas de continuidad

Con el universo `anillo == nucleo AND apto_geometria == True` (**23.981 registros**), al umbral común de 40 m se obtuvo: **MDO280_1702 8,9%; R11 11,7%; Z28 5,9%; Z42 7,4%**. La curva control R22 reprodujo **2,5 / 5,6 / 11,6 / 15,7 / 31,3 %**.

## Controles y faltantes

Gate reproducido: R01=1.358; Soho=772; Hollywood=595; Cañitas=361. No quedó ninguna celda vacía ni medición pendiente. La continuidad es una propiedad del instrumento: porcentaje de puntos en la mayor componente conexa, no porcentaje de superficie urbana. Montes de Oca usa los segmentos del callejero que solapan 280–1702 y el buffer territorial convencional de 150 m; no usa el eje IDECBA 501–1199.

Esta corrida no escribió en fuentes ni en las carpetas `ronda_14/` y `desde_cowork/`.
