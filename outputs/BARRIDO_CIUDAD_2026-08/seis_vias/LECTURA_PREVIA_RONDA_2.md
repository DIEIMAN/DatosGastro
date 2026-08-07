# LECTURA PREVIA · ronda 2 · la capa de hitos 2026 y lo que cambia de las seis vías

**Escrito antes de volver a correr.** Complementa `LECTURA_PREVIA.md`, que sigue vigente en todo lo
que no contradiga. Fecha: 2026-08-07 · Google Places: **0 requests**.

---

## 1 · Qué cambia de insumo

La vía B pasa a leer `hitos/hitos_capa_2026.csv` en lugar de reconstruir la capa adentro del script
de medición. La capa nueva incorpora la evidencia de `desde_cowork/evidencia_2026/`:

- **20 pizzerías emblemáticas y 5 heladerías históricas** que antes no tenían ninguna coordenada;
- **patrimonio normativo de 2 a 10** establecimientos, con norma y organismo;
- **tres campos de vigencia** que antes no existían.

`hitos_capa_unificada.csv` queda intacto: es el estado contra el que se compara.

---

## 2 · La regla nueva, declarada antes de medir: qué hace un hito cerrado con la vía B

Los Laureles cerró en julio de 2026 y el circuito oficial lo sigue publicando. Si un hito cerrado
abre una vía, el instrumento certifica trayectoria con un local que ya no existe.

```
via_B_abierta = hay al menos un hito dentro del soporte QUE NO ESTÉ VERIFICADO COMO CERRADO

  vigencia_verificada = "no"             NO cuenta para abrir la vía
  vigencia_verificada = "dudosa"         SÍ cuenta, y el conteo de dudosos viaja al lado
  vigencia_verificada = "sin_verificar"  SÍ cuenta, y el conteo viaja al lado
```

**`sin_verificar` es un cuarto valor y está puesto a propósito.** Los tres del enunciado —`si`,
`no`, `dudosa`— suponen que alguien miró. Sobre 220 hitos, alguien miró 4. Rellenar el resto con
`si` sería afirmar 216 cosas que nadie comprobó, y es exactamente el error que Los Laureles acaba
de demostrar. Un `sin_verificar` que se lee como incertidumbre es preferible a un `si` que se lee
como hecho.

Columnas nuevas en la medición, para que el conteo nunca esconda su composición:

```
via_B_total        todos los hitos adentro
via_B_cerrados     los verificados como cerrados (no cuentan para abrir)
via_B_dudosos      los de vigencia dudosa (cuentan, pero se ven)
```

---

## 3 · Lo que se declara antes de mirar el resultado

**La comparación contra la ronda 1 es el resultado, no un detalle.** Cuántas filas cambian de vía
abierta al cargar 25 direcciones y 8 declaratorias es lo que mide si el hueco de fuente era grave.

```
cambian pocas filas (≤5)     -> el hueco existía pero no movía la grilla; se dice y se sigue
cambian muchas (>5)          -> el hueco SÍ movía la grilla, y todo conteo de vía B anterior a
                                esta carga queda marcado como provisorio
ninguna cambia               -> revisar el cruce antes de creerlo: 25 puntos nuevos que no caen
                                en ningún soporte es más probable que sea un error de join
```

Y una que ya se sabe y se anota igual: **Boedo debería sumar San Antonio**, que era el cuarto hito
que faltaba. Si no lo suma, hay un problema en el cruce y no en la evidencia.

---

## 4 · Lo que esta ronda NO toca

Geometría, agrupamientos, fichas y cartografía siguen congelados. El corte del índice de corredor
(2,0), el de continuidad (60 m), el de pertenencia (50 %) y el buffer de enclave (150 m) **no se
mueven**: son los mismos de la ronda 1 y no se retocan porque cambió el insumo de otra vía.

Y `via_E_reconocimiento` sigue **vacía**: la llena Diego.
