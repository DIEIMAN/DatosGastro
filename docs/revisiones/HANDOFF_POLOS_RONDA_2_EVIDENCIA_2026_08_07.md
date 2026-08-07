# HANDOFF · Ronda 2 · la evidencia cargada, el ENTUR y los ejes comerciales · 2026-08-07

Continúa `HANDOFF_POLOS_SEIS_VIAS_2026_08_07.md` (misma fecha, ronda anterior). Rama
`mercados-gastronomicos-v2`. **Google Places: 0 requests.** USIG sí. Ninguna geometría publicada
tocada. Lectura escrita antes de correr: `outputs/BARRIDO_CIUDAD_2026-08/seis_vias/LECTURA_PREVIA_RONDA_2.md`.

**El informe completo está en `outputs/BARRIDO_CIUDAD_2026-08/seis_vias/INFORME_RONDA_2.md`.**

---

## Lo primero, porque cambia cómo se lee lo anterior

**El hueco de fuente SÍ movía la grilla.** Cargar 25 direcciones y 8 declaratorias cambió la vía B
en **20 de 94 filas**, y 5 cambiaron su número de vías abiertas. Por la rama declarada, **todo
conteo de vía B anterior a esta carga queda provisorio**: el 40 de 94 de la ronda 1 se reemplaza
por **43 de 94**.

Y la fila que justifica el campo de vigencia sola: **P008 Barracas dejó de abrir vía B** porque su
único hito era **Los Laureles**, que cerró en julio de 2026 y que el circuito gastronómico oficial
del GCBA sigue publicando.

---

## Scripts nuevos

| script | qué hace |
|---|---|
| `hitos_cargar_evidencia_2026.py` | Tareas 1-3: direcciones, patrimonio normativo y vigencia → `hitos_capa_2026.csv/geojson` |
| `bajar_entur_gastronomia.py` | Tarea 4: dataset del Ente de Turismo + perfil + contraste contra la base |
| `bajar_idecba_ejes_comerciales.py` | Tarea 5: los dos .xlsx, el glosario de 48 ejes y el relevamiento 2026 |

`polos_seis_vias.py` ahora **lee** la capa de hitos del disco en vez de rearmarla adentro.
`hitos_capa_unificada.csv` queda intacto como estado de comparación.

---

## Los cinco resultados

1. **25 de 25 direcciones geocodificadas.** Pizzerías y heladerías pasan de **0 a 25 coordenadas**.
   San Antonio entró y es el cuarto hito de Boedo. El Fortín se georreferenció **por esquina**, con
   la altura vacía.
2. **Los cinco conflictos: cargados los dos y medida la consecuencia, no resuelto ninguno.**
   La Mezzetta 12 m · Banchero 28 m · San Carlos 80 m · **Saverio 136 m** · La Americana no es
   conflicto de dirección sino de comuna. **Cuatro de cinco no cambian ningún polígono**, y ahora
   está medido.
3. **Patrimonio normativo de 2 a 10.** Siete marcados sobre hitos que ya estaban, tres nuevos. Las
   dos reservas —Decreto 1021/1979 sin confirmar, Mercado de San Telmo 64 m afuera de R03— viajan
   en la columna `patrimonio_nota`.
4. **El ENTUR es de 2019, no de 2026** —`metadata_modified` del registro contra `last_modified` de
   los recursos— y con 2.823 puntos no puede resolver la vía A. Pero su razón contra la base va de
   **0,02 a 0,25** según la zona y **es una medida directa del sesgo de cobertura turística**.
5. **Las dos delimitaciones de ejes que usábamos estaban mal.** Mataderos se corrió 100 m
   (5401-6199 → **5501-6299**) y **Liniers cambió de calle**: ya no es Rivadavia sino **Ramón
   Falcón 6801-7299**, que es una de las tres calles del microcentro boliviano. El eje comercial
   oficial corrobora la delimitación de la vía D sin que la hubiéramos buscado.

---

## Estado de la matriz

**53 columnas** (51 + `via_B_cerrados` + `via_B_dudosos`). Las **23 originales verificadas contra
el commit anterior a la ronda 1: 0 celdas distintas**. `via_E_reconocimiento` sigue vacía.

| vía | ronda 1 | ronda 2 |
|---|---:|---:|
| A | 89 de 94 | 89 de 94 |
| **B** | **40** | **43** |
| C | 4 | 4 |
| D | 7 | 7 |
| F | 53 | 53 |

Las 22 publicadas siguen abriendo al menos una vía medible; ninguna tiene hitos cerrados adentro.

---

## Trampas encontradas hoy

- **El nombre plegado tira BAR y RESTAURANTE**, así que «Restaurante Oviedo» (Recoleta) y «Bar
  Oviedo» (Mataderos) quedan los dos en «OVIEDO» y la primera pasada los fusionó. Pero exigir la
  misma calle rompía el **Mercado de San Telmo**, que está asentado en Defensa 961 en una fuente y
  en Bolívar 954 en la otra porque tiene dos frentes. Desempata **la distancia**: 150 m.
- **Una fecha de catálogo no es una fecha de datos.** El ENTUR dice 22/07/2026 en el registro y
  05/08/2019 en todos sus recursos.
- **La fila de pie de un .xlsx cae en la columna de datos.** «Fuente: Instituto de Estadística…»
  se colaba como un eje 49.º si se filtraba sólo por no nulo.
- **Un CSV oficial puede no ser UTF-8.** El del ENTUR es latin-1; leerlo mal produce mojibake que
  después parece dato.
- **Guardrail 7 sobre dato abierto:** el ENTUR trae `telefono` y `mail` por establecimiento. Son
  comercios, pero la regla nombra emails y teléfonos sin esa distinción: los crudos quedan fuera de
  Git y se versiona la derivada `*_sin_contacto`.

---

## Lo que espera decisión

1. **La vía E**, que seguís llenando vos.
2. **El quinto enclave: el Corredor Peruano de Agüero**, con delimitación textual. Sin él, Abasto
   **no puede abrir vía D medida** aunque vos lo cuentes por B y D.
3. **Confirmar el Decreto 1021/1979** contra el registro nacional.
4. **La envolvente R03 de San Telmo**, que sigue dejando su mercado 64 m afuera.
5. **Verificar vigencia sobre los 216 `sin_verificar`**, priorizando los hitos que son el único de
   su zona: son los que pueden dar vuelta una fila entera, como P008.
6. **Convertir los 48 ejes comerciales en geometría** para contrastar la vía A contra una medición
   oficial y actual (12.896 locales relevados, 1.er cuatrimestre 2026).
7. **Actualizar las citas de los ejes de Mataderos y Liniers** en lo ya escrito: la delimitación
   vieja circula en `desde_cowork/evidencia_2026/sur_oeste_seis_vias.csv`.
8. Sigue de antes: las 39 filas que superponen territorio de una vieja, `Ultramarinos` sin
   geocodificar, `Mercado San Nicolás` y `Smart Plaza Parque Patricios` sin dirección, los ~7.000
   archivos sin rastrear, el saliente N–NE, R01 en la V3 con el 47,7 %, la cláusula ODbL, el visto
   de Patricia, Foursquare y el documento extenso del método.
