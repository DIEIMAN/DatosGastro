# Plan de posibles consultas quirúrgicas de Google Places (futuras)

Estado: EXPERIMENTAL / NO OFICIAL. Fecha de corte: 2026-07-10.

**Este documento no ejecuta ni autoriza ninguna consulta.** Toda ejecución requiere
autorización explícita de Diego, presupuesto confirmado y el mismo protocolo controlado
del piloto (scripts con `--execute --confirm-real-api`, límites de consultas, QA de
privacidad, sin raw JSON). Google Places es fuente externa auxiliar (E-serie): mide
oferta visible en la plataforma, nunca "locales activos", y no puede convertir una
señal Places-only en polo firme.

Principio rector: una consulta quirúrgica solo se justifica si responde una **duda
metodológica concreta** cuyo resultado cambiaría una decisión. Cobertura "por las
dudas" no se ejecuta.

Antecedente relevante (verificado en
`docs/polos_gastro/experimentos/google_places_microzonas_ampliacion_v1/RESUMEN_METODOLOGICO_COMPLETA_V1.md`):
el refinamiento 3×3 de las 2 celdas saturadas de Chacarita devolvió 35 puntos únicos
pero **0 puntos nuevos incorporables** tras contención y deduplicación. Es decir: el
refinamiento de celdas saturadas puede no agregar nada. Este antecedente baja la
expectativa de retorno de QP-01/02/03 y es parte de la evidencia.

## Costos

Los volúmenes se expresan en cantidad de consultas (unidad controlable del protocolo).
El costo monetario depende de la tarifa vigente de la API al momento de autorizar; no
se estima acá para no fijar números que envejecen. Referencia de escala: el piloto
2026-07-09 ejecutó 379 consultas autorizadas; la ampliación dejó un margen remanente de
165 consultas que Tanda B no consumió.

## QP-01 — Celdas saturadas de Recoleta

- **Zona:** Recoleta (MZ_RECOLETA).
- **Duda:** ¿la densidad real de oferta visible en las 29 celdas saturadas es
  sustancialmente mayor que la capturada (subcaptura por tope de resultados)?
- **Evidencia actual:** Tanda B registró 29 celdas saturadas en Recoleta (de 58
  totales); el resumen metodológico recomienda tratar esos resultados como "densos pero
  potencialmente subcapturados". Recoleta tiene 47,3 % Places y estabilidad local MEDIA
  (0,703).
- **Celdas / área mínima:** las 29 celdas saturadas registradas, refinamiento 2×2.
- **Cantidad estimada:** 29 × 4 = **116 consultas**.
- **Resultado que cambiaría una decisión:** si el refino aporta puntos nuevos
  incorporables que alteren la forma de los núcleos candidatos cuando Recoleta entre al
  escalado (hoy no entró).
- **Resultado que NO justificaría la consulta:** más puntos que solo engordan celdas ya
  densas sin cambiar estructura (el antecedente Chacarita sugiere que esto es
  probable).
- **Prioridad:** MEDIA (condicionada al escalado de Recoleta).
- **Recomendación: ESPERAR.** No ejecutar antes de que Recoleta tenga su corrida de
  escalado con los datos actuales; solo si esa corrida muestra núcleos cuya forma
  depende de celdas saturadas, evaluar el refino con criterio de priorización
  territorial definido antes (requisito ya documentado en la ampliación).

## QP-02 — Celdas saturadas de Villa Crespo

- **Zona:** Villa Crespo (MZ_VILLA_CRESPO).
- **Duda:** ídem QP-01 para 19 celdas saturadas.
- **Evidencia actual:** 19 celdas saturadas en Tanda B. Pero Villa Crespo tiene la peor
  estabilidad local de las 13 macrozonas (0,045; sensibilidad global mínima −0,005) y
  60,5 % Places con dependencia ALTA y confianza BAJA.
- **Celdas / área mínima:** 19 celdas, refinamiento 2×2.
- **Cantidad estimada:** 19 × 4 = **76 consultas**.
- **Resultado que cambiaría una decisión:** ninguno a corto plazo: el problema de Villa
  Crespo no es densidad de Places sino ausencia de estructura estable y de respaldo
  F01/F02; más Places no arregla ninguna de las dos cosas.
- **Resultado que NO justificaría la consulta:** cualquier engorde de celdas sin
  estructura F01/F02 que lo acompañe.
- **Prioridad:** BAJA.
- **Recomendación: ESPERAR** (cercana a NO_EJECUTAR). Recién reevaluar si el tipo
  multinuclear (post repetición Belgrano) produce en Villa Crespo candidatos cuya
  estabilidad dependa de las celdas saturadas.

## QP-03 — Celdas saturadas de Caballito

- **Zona:** Caballito (MZ_CABALLITO).
- **Duda:** ídem QP-01 para 10 celdas saturadas.
- **Evidencia actual:** 10 celdas saturadas en Tanda B; 60,4 % Places, dependencia
  ALTA, confianza BAJA; partición inestable entre leaf/eom (0,136) — el problema
  dominante es metodológico, no de captura.
- **Cantidad estimada:** 10 × 4 = **40 consultas**.
- **Resultado que cambiaría una decisión / que no:** análogo a QP-02.
- **Prioridad:** BAJA.
- **Recomendación: ESPERAR.**

## QP-04 — Bordes de Puerto Madero (margen este / Costanera Sur)

- **Zona:** Puerto Madero, franja este de los diques y contacto con Costanera Sur.
- **Duda:** ¿el margen este tiene oferta visible no capturada que cambie la decisión
  frente único vs. frente doble (DH-06)?
- **Evidencia actual:** 192/294 puntos fuera del frente oeste; el tramo norte del
  perfil ya es 87 % Places; el anillo externo de 200 m tiene **42 F01/F02 + 46 Places
  ya almacenados localmente** sin incorporar.
- **Celdas / área mínima:** franja de ~200 m sobre el margen este solo en tramos donde
  la repetición PM-B deje huecos inexplicados; estimación gruesa 10–20 celdas.
- **Cantidad estimada:** **10–20 consultas** (1 por celda; sin refino).
- **Resultado que cambiaría una decisión:** oferta visible en tramos del margen este
  donde hoy no hay puntos, suficiente para cambiar la composición del eje este en PM-B.
- **Resultado que NO justificaría la consulta:** más Places donde ya hay Places (el
  margen este ya está dominado por Places; sumar más no mejora la validez
  institucional).
- **Prioridad:** MEDIA.
- **Recomendación: ESPERAR.** Orden correcto: (1) correr la repetición local PM-R01..12;
  (2) revisar el anillo ya almacenado (sin API); (3) solo si queda un hueco concreto
  que decida entre opciones, ejecutar esta consulta.

## QP-05 — Bordes de Belgrano

- **Zona:** Belgrano, fuera del contenedor de corredores de 250 m.
- **Duda:** ¿hay estructura cortada por el contenedor?
- **Evidencia actual:** 32,7 % de puntos a ≤100 m del borde; 53 entidades conocidas
  fuera de toda macrozona (ficha del contenedor); anillo externo de 200 m con
  **131 F01/F02 + 157 Places ya almacenados**.
- **Celdas / área mínima:** no definible todavía; depende de BEL-R11 (contenedor barrio
  completo).
- **Cantidad estimada:** no estimable con rigor hoy (probable 0).
- **Resultado que cambiaría una decisión:** ninguno antes de BEL-R11: la pregunta se
  responde primero con datos locales (barrio oficial completo + anillo almacenado).
- **Resultado que NO justificaría la consulta:** cualquier resultado que el contenedor
  de contraste local pueda dar gratis.
- **Prioridad:** BAJA (hasta la repetición).
- **Recomendación: NO_EJECUTAR** en esta etapa; reevaluar solo si tras BEL-R11 quedara
  un borde externo al barrio oficial con indicios de estructura (improbable).

## QP-06 — Bordes de Costanera Norte

- **Zona:** Costanera Norte, extremos del corredor costero.
- **Duda:** ¿hay más oferta visible fuera del bbox acotado?
- **Evidencia actual:** universo de 72 puntos con 5 F01/F02 (93,1 % Places); anillo
  externo: 0 F01/F02 y 3 Places brutos. La zona ya está en el mínimo de validez
  institucional.
- **Cantidad estimada:** n/a.
- **Resultado que cambiaría una decisión:** ninguno. Más Places solo aumentaría la
  dependencia de la fuente externa; no puede crear el respaldo F01/F02 que falta, y la
  decisión DH-07 (anexo sin polígono) no depende de la cantidad de puntos Places.
- **Prioridad:** —
- **Recomendación: NO_EJECUTAR.**

## QP-07 — Huecos puntuales en corredores o frentes

- **Zona:** Corrientes (corredor), Puerto Madero (frentes), futuros corredores.
- **Duda:** ¿los huecos de densidad en un corredor/frente son reales o subcaptura?
- **Evidencia actual:** Corrientes: **0 bins vacíos** en 4,4 km de perfil — no hay
  huecos que explicar. Puerto Madero: el perfil no tiene huecos de proyección; la
  fragmentación del frente v1 (18 componentes) es un problema de soporte vial, no de
  captura de puntos.
- **Cantidad estimada:** 0.
- **Resultado que cambiaría una decisión:** hoy ninguno; no existe el hueco que esta
  consulta respondería.
- **Prioridad:** —
- **Recomendación: NO_EJECUTAR** (sin objeto). Si un corredor futuro (p. ej. Caseros)
  mostrara bins vacíos con F01/F02 presente alrededor, redactar entonces una QP
  específica con celdas concretas.

## Resumen

| ID | Zona | Consultas estimadas | Recomendación |
| --- | --- | ---: | --- |
| QP-01 | Recoleta (29 celdas saturadas) | 116 | ESPERAR |
| QP-02 | Villa Crespo (19 celdas) | 76 | ESPERAR |
| QP-03 | Caballito (10 celdas) | 40 | ESPERAR |
| QP-04 | Borde este Puerto Madero | 10–20 | ESPERAR |
| QP-05 | Bordes Belgrano | 0 (hoy) | NO_EJECUTAR |
| QP-06 | Bordes Costanera Norte | 0 | NO_EJECUTAR |
| QP-07 | Huecos en corredores/frentes | 0 | NO_EJECUTAR |

Ninguna consulta queda autorizada por este documento. Ninguna tiene hoy recomendación
EJECUTAR: en todos los casos hay pasos locales gratuitos pendientes que van primero.
