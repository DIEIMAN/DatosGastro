# Correcciones de los 4 bloqueantes — ANTES / DESPUÉS / justificación (Etapa Cal-3)

**Fecha:** 2026-07-08 · Generado con
`scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/corregir_bloqueantes_v1.py`.
**Ninguna corrección reemplazó automáticamente `macrozonas_v1_experimental.geojson`** —
las geometrías nuevas viven aparte en `outputs/.../correcciones_bloqueantes/
geometrias_corregidas.geojson`, a la espera de que Diego las revise (Etapa Cal-6) antes
de ensamblarlas en la capa candidata (Etapa Cal-5).

## 1. Avenida Corrientes × Microcentro y Centro

**ANTES:** Microcentro y Centro = barrio San Nicolás completo, 229,0 ha, 763 entidades.
Solapaba 49,2 % con Avenida Corrientes (406 entidades compartidas).

**DESPUÉS:** Microcentro y Centro = barrio San Nicolás **menos** el corredor de Avenida
Corrientes (que queda intacto). 116,3 ha, 357 entidades.

**Justificación:** la prueba de pipeline de la tanda anterior ya demostró que el corredor
real de Avenida Corrientes funciona muy bien por sí solo (0 clusters sobredimensionados,
incorpora territorio real que el contenedor viejo no cubría). No había motivo para
tocarlo. El problema era exclusivamente que Microcentro, al ser el barrio completo sin
recortar, se superponía con él. Restarle la franja ya cubierta por Corrientes es la
corrección mínima que elimina el solapamiento sin degradar ninguna de las dos
macrozonas. Ver `correcciones_bloqueantes/antes_despues_microcentro.png`.

**Efecto colateral a revisar:** el "hueco" rectangular que deja el recorte (donde estaba
Corrientes) parte a Microcentro en dos franjas (norte y sur) — geométricamente correcto,
pero conviene que Diego confirme que esto no genera dos identidades editoriales
distintas donde antes había una sola.

## 2. Belgrano

**ANTES:** unión de 4 elipses editoriales de fase16 (dibujadas a mano, nunca verificadas
contra calles reales) ∩ barrio Belgrano. 202,0 ha, 273 entidades, confianza **baja**.

**DESPUÉS:** corredores reales sobre las 3 avenidas que la propia documentación de
fase16 ya usaba como referencia geográfica textual (Juramento para Barrio Chino,
Libertador para Bajo Belgrano, Cabildo para Belgrano R), semiancho 250 m, ∩ barrio
Belgrano. 232,5 ha, 304 entidades, confianza propuesta **media**.

**Justificación:** ninguna ficha de las 3 subzonas de Belgrano tiene calles límite
completas (a diferencia de Palermo Soho/Hollywood), así que no era posible aplicar el
mismo método de "4 calles → partición del plano". Pero las 3 avenidas mencionadas SÍ son
reales y SÍ están documentadas como referencia geográfica de cada subzona — usarlas como
eje de un corredor es más verificable que heredar una elipse dibujada a mano. El área
creció un 15 % (202→232 ha) porque las 3 avenidas reales cubren un poco más que las
elipses originales; se acepta ese costo a cambio de que la geometría ahora sea trazable
y auditable. Ver `correcciones_bloqueantes/antes_despues_belgrano.png`.

**Limitación explícita:** esto sigue siendo **un solo polígono a nivel de polo**, no 3
subzonas independientes (a diferencia de Palermo). Subdividir Belgrano en Barrio
Chino/Bajo Belgrano/Belgrano R como subzonas propias —lo que la validación anterior
sugirió que hacía falta para desenredar el cluster dominante— queda pendiente de una
sesión futura con más tiempo de digitalización, no se resuelve en esta corrección.

## 3. Costanera Norte

**ANTES:** corredor sobre Av. Costanera Rafael Obligado, semiancho 350 m, bbox amplio.
225,1 ha, 5 entidades (0,02/ha) — casi la mitad del polígono sin ninguna entidad cerca.

**DESPUÉS:** mismo eje real, semiancho reducido a 250 m, bbox acotado al tramo donde
están las 5 entidades reales (con margen). 150,8 ha, mismas 5 entidades (0,03/ha).

**Justificación:** no hay "más evidencia" que agregar — los datos F01+F02 simplemente no
tienen mucho registrado en esta franja costera. La corrección no inventa cobertura: la
reduce a lo que el propio corredor puede defender con evidencia real, cortando el tramo
norte que no tenía ninguna entidad cerca. Es una reducción del 33 % en superficie sin
perder ninguna entidad. Ver `correcciones_bloqueantes/antes_despues_costanera_norte.png`.

**Límite de esta corrección:** la densidad sigue siendo extremadamente baja (0,03/ha).
Achicar el polígono es más honesto que dejarlo grande, pero no resuelve el problema de
fondo (evidencia insuficiente). Ver recomendación en la Etapa Cal-6: esta macrozona debería
marcarse "△ modificar" como mínimo, no "✓ aprobar" directo.

## 4. Chacarita

**ANTES:** barrio Chacarita completo (fallback, la semilla estaba mal geocodificada para
este polo). 311,7 ha, 116 entidades (0,37/ha).

**DESPUÉS:** barrio Chacarita ∩ buffer 400 m alrededor de las 116 entidades reales del
universo V1 (no la semilla). 262,0 ha, mismas 116 entidades (0,44/ha).

**Justificación:** a diferencia de lo esperado inicialmente, las 116 entidades reales
**sí están distribuidas en casi todo el rango del barrio** (lat/lon casi idénticos a los
límites del barrio administrativo) — no concentradas en una esquina, como se pensó al
revisar solo una muestra parcial en la ficha técnica. Por eso la mejora es modesta (16 %
de reducción de superficie), no dramática: el barrio completo ya era, en la práctica,
una aproximación razonable a dónde está la oferta gastronómica real. La corrección igual
vale la pena porque reemplaza un fallback ciego (barrio completo "porque la semilla
falló") por un recorte basado en datos reales y confiables (F01+F02), aunque el
resultado numérico sea parecido. Ver
`correcciones_bloqueantes/antes_despues_chacarita.png`.

**Corrección al diagnóstico previo:** la ficha técnica (Etapa Cal-1) había señalado que
las entidades parecían concentradas en ~2×2 km; al graficar el rango completo se
confirma que en realidad cubren casi todo el barrio. Se documenta el error de lectura
para no repetirlo.

## Resumen de superficie y entidades (las 4 correcciones)

| Macrozona | Área antes (ha) | Área después (ha) | Δ área | Entidades antes | Entidades después |
|---|---|---|---|---|---|
| Microcentro y Centro | 229,0 | 116,3 | −49 % | 763 | 357 |
| Belgrano | 202,0 | 232,5 | +15 % | 273 | 304 |
| Costanera Norte | 225,1 | 150,8 | −33 % | 5 | 5 |
| Chacarita | 311,7 | 262,0 | −16 % | 116 | 116 |

Ninguna corrección fue automática ni definitiva: las 4 quedan pendientes de aprobación
editorial explícita (Etapa Cal-6) antes de reemplazar sus versiones en
`macrozonas_v1_experimental.geojson`.
