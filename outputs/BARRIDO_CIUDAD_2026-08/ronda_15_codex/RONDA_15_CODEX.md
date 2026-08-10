# Ronda 15 · Codex

Estado: **EXPERIMENTAL / NO OFICIAL**. Cero requests a APIs. La fusión territorial queda pendiente de firma de Diego.

## 1. ERR-17 · corpus del sur

Se incorporaron **Z50–Z54** a `fichas_corpus_polos.csv`. El corpus pasó de 48 a **53 filas**. Cada alta conserva las seis columnas de vía, los hitos y el perímetro textual de `seis_vias_sur_consolidado.csv`; Z51–Z54 se cotejaron además con `FICHAS_SUR_NUEVAS.md`.

Z50 quedó vinculada explícitamente con **P066** y `ronda_14/montes_de_oca_seis_vias.csv`. No se la duplicó como “polo 42”. Las cifras de superficie y registros de las cinco fichas siguen sin publicarse porque sus límites institucionales no están adoptados.

## 2. Reparto del sur

Universo: `anillo == 'nucleo' AND apto_geometria == True`, **23.981 registros** de `base/local.csv`. Superficies en EPSG:5347. La contención se verificó por **superficie perdida**, no con `covers()`.

| zona | candidato | intersección m² | superficie de la zona perdida m² | superficie de la zona dentro | registros compartidos / zona | registros compartidos / candidato | clase | recomendación |
|---|---|---:|---:|---:|---:|---:|---|---|
| Z51 | Z50 | 0,00 | 235.189,30 | 0,0000 % | 0/38 (0,0000 %) | 0/62 (0,0000 %) | DISJUNTA | MANTENER SEPARADA |
| Z51 | R11 | 0,00 | 235.189,30 | 0,0000 % | 0/38 (0,0000 %) | 0/60 (0,0000 %) | DISJUNTA | MANTENER SEPARADA |
| Z54 | Z40 | 504.234,53 | 0,00 | 100,0000 % | 95/95 (100,0000 %) | 95/546 (17,3993 %) | CONTENIDA | RECOMENDAR FUSION; requiere firma de Diego |

Recomendación técnica: **Z51 mantener separada** frente a Z50 y R11; **Z54: recomendar fusion; requiere firma de diego**. El conteo vigente continúa en **41 polos admitidos**. Si Diego firma todas las fusiones recomendadas (Z54), el contrafáctico pasa a **40**. La corrida no toma esa decisión.

## 3. ERR-18 y ERR-19

`n_vias` se recalculó desde `via_A`…`via_F`: **R02=4, R04=4, R05=5, R19=4 y Z37=5**. En Z37 la vía C quedó escrita como cerrada por ronda 13. Ninguna fila cambia de categoría.

La fila R03 de `via_E_22_referencias.csv` quedó en **10 campos**, como el encabezado. `via_E_advertencia` conserva completo el texto con comas; `via_E_rutas_n=6` y `fecha_relevamiento=2026-08-07` vuelven a sus columnas.

## 4. Z55 · fuente pública

Se verificaron los tres recursos oficiales F03 conservados en el repositorio, descargados el **12/06/2026** desde BA Data: 30 ferias, 184 ubicaciones FIAB y 6 mercados. El GeoJSON registra dos FIAB en Villa Soldati —Lacarra/Roca y Predio Villa Olímpica— y ninguna sobre Mariano Acosta. Los recursos de ferias y mercados tampoco contienen “Mariano Acosta” ni “Ana María Janer”.

La afirmación de una feria de 840 m no trae URL, norma, permiso ni identificador de fuente en `seis_vias_sur_consolidado.csv`. Por eso queda como **puerta documental cerrada / no verificable con la fuente pública disponible** y **no abre la vía C**. Esto no prueba que la feria no exista; prueba que el instrumento no tiene respaldo público trazable para computarla. El corte del padrón (12/06/2026) impide usar la ausencia como prueba territorial.

Hay una segunda consecuencia lógica: aun si una fuente futura abriera C, Z55 pasaría de 0 a **1 vía**, por debajo del umbral común de **2 vías**. Con el criterio vigente, esta contradicción por sí sola **no puede crear un polo en la Comuna 8**.

## 5. Gates

- Universo ERR-10: **23.981**, reproducido.
- Corpus: **53 IDs únicos**; Z50–Z54 presentes.
- Criterio: **41 admitidos**; no se promovió ninguna fusión.
- Reparto: ambos denominadores de superficie y registros presentes; superficie perdida explícita.
- ERR-19: todas las filas tienen 10 campos.
- Fuentes originales F01–F05: sólo lectura; no se modificaron.
