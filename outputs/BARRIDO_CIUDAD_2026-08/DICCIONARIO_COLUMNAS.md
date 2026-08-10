# Diccionario de columnas · Barrido de la Ciudad

Acompaña a los CSV de esta carpeta. Si un CSV se entrega suelto, este archivo va con él.

> ## Aviso sobre la columna `habilitaciones`
>
> **No es un indicador de volumen de oferta.** Cuenta trámites de habilitación, no locales.
>
> En 45 conjuntos de direcciones —137 direcciones, 9.697 trámites, el **22,6 % del padrón
> georreferenciado**— un mismo permiso figura repetido contra cada puerta del frente de manzana
> de un inmueble. El mecanismo está en el propio padrón: el campo `calles` asienta el frente
> entero del inmueble en un solo registro (13,9 % de los registros crudos traen más de un número
> de puerta), y la exportación de 2025 lo aplana a un domicilio por fila. El catastro lo
> corrobora: las 37 partidas matriz involucradas resuelven **todas a una única parcela**.
>
> El caso más engañoso de la Ciudad es **Liniers**: el 77 % de sus trámites viene de tres
> conjuntos replicados. Un lector que ordene barrios por esta columna lo pondría entre los más
> densos de la Ciudad, y no lo es.
>
> **Las columnas de direcciones (`dir_nucleo`, `dir_ampliado`) no están afectadas:** la regla 3
> del método deja estas direcciones fuera del conteo desde el principio. Ninguna cifra publicada
> depende de `habilitaciones`.
>
> La columna se publica igual porque mide algo que sí importa —carga de trámite sobre el
> territorio— pero se lee como eso y no como oferta.

---

## Qué CSV traen la columna avisada

- `capa_homogenea_22_zonas.csv` — **trae `habilitaciones`**
- `capa_homogenea_48_barrios.csv` — **trae `habilitaciones`**
- `generado/capa_homogenea_22_zonas.csv` — **trae `habilitaciones`**
- `generado/capa_homogenea_48_barrios.csv` — **trae `habilitaciones`**
- `generado/direcciones_anomalas_324.csv` — **trae `habilitaciones`**
- `generado/fichas_documentales_oeste_sur.csv` — **trae `habilitaciones`**
- `generado/lotes_permisos_detectados.csv` — **trae `habilitaciones`**

Otros 13 CSV de la carpeta no la traen.

---

## Glosario

- **`anio_relevamiento`** — Año en que el Relevamiento pasó por ese barrio. El operativo es rotativo: no todos los barrios tienen la misma añada.
- **`dir_ampliado`** — Ídem, sumando el anillo ampliado (panadería, pastelería, confitería).
- **`dir_nucleo`** — Direcciones distintas con al menos una habilitación gastronómica del anillo núcleo entre 2015 y 2025. **Es la unidad de conteo del trabajo.**
- **`dir_outlier`** — Direcciones con más de 20 trámites, excluidas del conteo por la regla 3 del método. Centros comerciales, complejos y cargas masivas del padrón.
- **`direcciones_con_esa_partida`** — Cuántas direcciones del padrón cuelgan de la misma partida. Más de una = el mismo inmueble cargado en varias puertas.
- **`direcciones_en_lotes`** — Direcciones involucradas en esos conjuntos.
- **`f01_locales`** — Establecimientos de la oferta registrada en F01. Universo distinto y mucho más chico: no es un censo.
- **`foco_menor`** — Un polo tiene un foco secundario estable que **no se publica como subzona**. Es una **decisión humana registrada**, no un cálculo: el criterio que la decide —nombre de uso corriente o respaldo documental— no lo evalúa un algoritmo. No tiene umbral de proporción a propósito; ver `FICHA_DE_POLO_ENRIQUECIMIENTO.md` §1.1.
- **`foco_calles`** — Las calles del foco menor, para ubicarlo sin ponerle nombre. **No es un recuento de oferta por calle**, y sale sólo de los locales con dirección: `foco_pct_con_direccion` dice cuántos son.
- **`habilitaciones`** — **Cantidad de trámites de habilitación, no de locales.** Ver el aviso de arriba antes de usarla.
- **`habilitaciones_en_lotes`** — Trámites involucrados. Contra `habilitaciones` da la proporción del volumen de trámite del barrio que es repetición.
- **`lotes_detectados`** — Conjuntos de permisos replicados detectados en el barrio.
- **`partidas_matriz`** — Partidas matriz distintas asociadas a la dirección en el crudo 2025.
- **`rus_ampliado`** — Ídem, con el anillo ampliado.
- **`rus_inactivo`** — Parcelas gastronómicas que el Relevamiento encontró inactivas.
- **`rus_nucleo`** — Parcelas con uso gastronómico del anillo núcleo según el Relevamiento de Usos del Suelo, en la añada declarada para ese barrio.
- **`smp`** — Clave catastral sección-manzana-parcela.

---

**Fuentes:** habilitaciones aprobadas y oferta gastronómica de BA Data (F01, F02, cohortes 2015-2025); Relevamiento de Usos del Suelo, GCBA. La prueba catastral está en `generado/PRUEBA_SMP_LOTES.txt`.
