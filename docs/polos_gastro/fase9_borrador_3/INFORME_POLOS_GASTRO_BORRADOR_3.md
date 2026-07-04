# Polos gastronomicos de la Ciudad de Buenos Aires

> **Borrador 3 - documento interno de trabajo para revision humana.**
> No es informe final, no es documento publico, no es PDF ni DOCX, no tiene diseno aplicado y no
> representa delimitaciones oficiales de polos gastronomicos. Fecha de corte documental de base:
> 2026-06-30 (Borrador 2). Incorporaciones de Fase 8 liviana y Fase 8 fuerte: 2026-07-01.
> Fase 9: no se realizaron busquedas web nuevas ni se incorporaron fuentes nuevas respecto de las
> ya registradas en Fase 8. No se uso Google Places.

---

## 1. Introduccion

Este Borrador 3 parte del Borrador 2 y lo enriquece de forma prudente con dos incorporaciones
posteriores: las recomendaciones documentales de la Fase 8 liviana y la capa objetiva de contexto
territorial de la Fase 8 fuerte. El objetivo no cambia respecto del Borrador 2: ordenar la evidencia
disponible, distinguir niveles de respaldo y dejar una base prudente para revision humana.

Las incorporaciones se hacen sin aplicar cambios automaticos de clasificacion. La Fase 8 liviana
aporta recomendaciones que quedan marcadas como sugerencias a revisar, no como decisiones aplicadas.
La Fase 8 fuerte aporta una senal objetiva de contexto que se trata siempre como contexto, nunca
como ranking, densidad real ni validacion de subpolos o corredores.

Con la evidencia disponible, este documento sigue siendo un borrador interno. No mide locales
activos, densidad gastronomica ni vigencia comercial.

---

## 2. Objetivo y alcance

**Objetivo.** Consolidar una lectura territorial prudente de los polos gastronomicos documentados,
integrando la validacion documental liviana y una capa objetiva de contexto, de modo que la revision
humana posterior pueda decidir cambios de clasificacion, redaccion editorial y futuras piezas
cartograficas.

**Alcance.** El trabajo cubre el universo documental de 32 registros territoriales heredado de Fase
5 y del Borrador 2. No amplia el universo. No cierra un mapa oficial de polos, no delimita
poligonos, no produce padron ni censo, y no reemplaza mediciones de densidad o habilitaciones.

**Fuera de alcance en esta fase.** Informe final, PDF, DOCX, diseno aplicado, mapas, graficos,
dashboards, uso de Google Places o de plataformas privadas, y cualquier cambio a datos fuente.

---

## 3. Metodologia y fuentes

El Borrador 3 combina tres capas de trabajo, mantenidas conceptualmente separadas:

1. **Capa documental de base (Borrador 2).** Universo de 32 registros con grupo, tipo territorial,
   estado de documentacion y referencias preliminares del documento semilla interno.
2. **Capa de validacion documental liviana (Fase 8 liviana).** Revision acotada de casos debiles o
   pendientes con fuentes abiertas oficiales, periodisticas y gastronomicas. Todas sus
   recomendaciones estan marcadas como "no aplicar ahora".
3. **Capa objetiva de contexto (Fase 8 fuerte).** Lectura de presencia relativa por barrio y comuna
   a partir de fuentes locales del pipeline (F01 oferta registrada y F02 habilitaciones historicas),
   en solo lectura y sin descargas nuevas.

Estas capas no tienen el mismo valor probatorio y no deben mezclarse. La capa documental sostiene la
clasificacion; la validacion liviana sugiere revisiones; la capa objetiva solo aporta contexto. El
detalle metodologico esta en `NOTAS_METODOLOGICAS_BORRADOR_3.md` y en el
`ANEXO_TECNICO_CAPA_OBJETIVA_BORRADOR_3.md`.

No se uso Google Places porque el trabajo debe basarse en fuentes abiertas u oficiales locales y no
en APIs privadas ni datos crudos de plataformas.

---

## 4. Universo consolidado

El universo documental conserva **32 registros territoriales**. Palermo Soho, Palermo Hollywood y
Las Canitas siguen existiendo como 3 registros base y, para la lectura ejecutiva, se agrupan dentro
de una unica area nucleo Palermo. Por eso el cuerpo presenta **4 areas nucleo** sin reducir ni
eliminar registros del universo base.

La tabla de trabajo del Borrador 3 esta en
`outputs/polos_gastro/fase9_borrador_3/tablas/tabla_polos_para_informe_borrador_3.csv`. Esa tabla
mantiene el orden del Borrador 2 (no se ordena por senal objetiva) y agrega columnas de contexto:
recomendacion de Fase 8 liviana, evidencia asociada, senal objetiva descrita cualitativamente,
lectura prudente, limitacion territorial y decision de uso en cuerpo o anexo.

---

## 5. Criterios de clasificacion

Se mantienen los criterios del Borrador 2:

- **Grupo ejecutivo:** area nucleo, zona relevante, emergente con documentacion media, candidato a
  validar con documentacion debil, anexo / caso secundario, y en espera de evidencia.
- **Tipo territorial visible:** barrio, subpolo, corredor, zona, area central, area costera o area
  de revision.
- **Categoria prudente:** "En espera de evidencia" reemplaza cualquier lenguaje de descarte. No
  implica ausencia de actividad gastronomica; indica que, con la evidencia actual, el caso no entra
  al cuerpo principal.

En el Borrador 3 se agrega un criterio de integracion:

- **La senal objetiva no modifica el grupo.** Una senal alta no sube un caso; una senal baja no lo
  baja. La senal solo acompana o matiza la lectura documental. Los cambios de clasificacion quedan
  reservados a la revision humana.

---

## 6. Lectura ejecutiva actualizada

La lectura ejecutiva del universo se mantiene estable respecto del Borrador 2. La Fase 8 no cambio
la estructura de grupos; aporto recomendaciones puntuales (liviana) y contexto (fuerte).

| Grupo ejecutivo | Lectura ejecutiva | Cambio respecto de Borrador 2 |
| --- | --- | --- |
| Areas nucleo | Palermo, Recoleta, San Telmo y Puerto Madero. | Sin cambios de grupo. La capa objetiva acompana a Palermo y Recoleta; en San Telmo y Puerto Madero la senal es baja y solo contextual. |
| Zonas relevantes | Chacarita, Barrio Chino, Microcentro / Centro, Monserrat y Retiro. | Sin cambios de grupo. Microcentro / Centro aparece con senal media y alta cautela territorial. |
| Emergentes con documentacion media | Villa Crespo, Caballito, Costanera Norte, Devoto, DoHo / Donado-Holmberg, Villa Urquiza y Colegiales. | Sin cambios de grupo. Costanera Norte y DoHo quedan como no calculables por ser corredores/areas sin delimitacion. |
| Candidatos a validar con documentacion debil | Avenida Corrientes y Paternal. | Sin cambios aplicados. Fase 8 liviana sugiere revisar a Paternal como posible documentacion media (a revision humana); Corrientes se mantiene como eje candidato, no nucleo. |
| Anexo / casos secundarios | Belgrano R, Avenida Caseros / Barracas, Abasto, Nuevo Bajo en Retiro, Parque Saavedra / Garcia del Rio, Flores, Floresta y Parque Patricios. | Sin cambios aplicados. Caseros/Barracas y Parque Saavedra reciben evidencia especifica que refuerza su tratamiento como anexo. Abasto tiene senal objetiva media pero se mantiene en anexo: la senal se aproxima por Balvanera y no separa Abasto de Corrientes, por lo que no cambia de grupo. |
| En espera de evidencia | Bajo Belgrano, Avenida Boedo, Federico Lacroze y Villa Pueyrredon / Avenida San Martin. | Sin cambios aplicados. Bajo Belgrano suma evidencia (a evaluar como anexo a validar); el resto se mantiene en espera de evidencia. |

---

## 7. Areas nucleo

Las areas nucleo no tienen todas el mismo nivel documental. Palermo, Recoleta y San Telmo tienen
respaldo fuerte en la base de Fase 5. Puerto Madero se mantiene como area nucleo con documentacion
media.

- **Palermo (Soho, Hollywood y Las Canitas).** Area nucleo con subpolos, documentacion fuerte. La
  capa objetiva muestra senal alta a nivel del barrio Palermo, pero esa senal aproxima el area
  nucleo, **no valida cada subpolo**. El 100 relativo del barrio no debe leerse como confirmacion de
  Soho, Hollywood o Las Canitas como poligonos.
- **Recoleta.** Barrio, documentacion fuerte. La capa objetiva muestra senal alta que **acompana**
  la lectura documental en el barrio de referencia. No valida limites internos ni vigencia de
  locales.
- **San Telmo.** Barrio, documentacion fuerte. La capa objetiva muestra senal baja; el cruce
  coincide con el barrio de referencia, pero no mide vigencia operativa. La documentacion sostiene
  el caso; la senal objetiva no lo contradice ni lo refuerza de forma concluyente.
- **Puerto Madero.** Zona, documentacion media. Se mantiene como area nucleo por reconocimiento
  urbano e institucional. La senal objetiva es baja y el barrio de referencia no equivale al
  poligono del polo. Requiere delimitacion fina y, si se quisiera medir densidad, una metodologia
  aprobada.

---

## 8. Zonas relevantes

Se mantienen en el cuerpo con redaccion prudente. No tienen el estatus de las areas nucleo.

- **Chacarita** (barrio, media). Senal objetiva baja; se mantiene como zona relevante.
- **Barrio Chino** (subpolo, fuerte). Debe leerse dentro de la macroarea Belgrano. La senal objetiva
  se aproxima por el barrio Belgrano, que **no valida** Barrio Chino como subpolo.
- **Microcentro / Centro** (area central, media). Senal objetiva **media** con alta cautela: es un
  area central multibarrial (San Nicolas, Monserrat, Retiro) y el promedio no delimita Microcentro.
- **Monserrat y Retiro** (barrios, media). Sublecturas de la zona central; no se convierten en polos
  cerrados sin delimitacion adicional.

**Belgrano como macroarea de revision.** Se mantiene la separacion del Borrador 2: Barrio Chino como
subzona fuerte dentro de Belgrano; Bajo Belgrano y Belgrano R con tratamiento diferenciado (ver
seccion 10). La capa objetiva de Belgrano es una senal barrial que no distingue estas subzonas.

---

## 9. Emergentes y candidatos

### Emergentes con documentacion media

Villa Crespo, Caballito, Devoto, Villa Urquiza y Colegiales se mantienen como secundarios con senal
objetiva baja de contexto, sin afirmaciones de densidad. Costanera Norte y DoHo / Donado-Holmberg
son **no calculables** en la capa objetiva por ser corredor costero y corredor sin delimitacion:
la senal de un barrio no valida el eje.

### Candidatos a validar con documentacion debil

- **Avenida Corrientes.** Se mantiene como eje cultural-gastronomico candidato, **no area nucleo**.
  Fuentes oficiales respaldan la identidad de teatro/pizza, pero no un corredor gastronomico cerrado. La
  capa objetiva es no calculable por corredor sin delimitacion. Debe revisarse junto con Abasto.
- **Paternal.** Fase 8 liviana encontro evidencia periodistica especifica de circuito gastronomico
  y contexto institucional del Distrito del Vino. **Podria** considerarse el pase a candidato a
  validar con documentacion media, pero **no se aplica** el cambio: requiere revision humana y
  cuidado de no sobreusar el Distrito del Vino o listados de locales como prueba de densidad. La
  senal objetiva del barrio Paternal es baja y solo aporta contexto.

---

## 10. Anexo territorial y casos a validar

- **Belgrano R** (area de revision, debil). Se mantiene como anexo o caso a validar. Hay oferta y
  referencias de subzona, pero no evidencia suficiente de polo independiente. No elevar por menciones
  genericas de Belgrano ni por borde con DoHo.
- **Avenida Caseros / Barracas** (corredor, media). Se mantiene como anexo con evidencia especifica
  reforzada de tramo. Existe evidencia para una cuadra/tramo de Avenida Caseros, pero requiere
  definir el recorte territorial y cuidar el solapamiento San Telmo/Barracas. Capa objetiva no
  calculable por corredor sin delimitacion.
- **Abasto** (subpolo, media). Se mantiene en anexo y se revisa junto con Avenida Corrientes. La
  evidencia valida hitos comerciales/culturales, no un polo gastronomico independiente. La senal
  objetiva es **media** pero se aproxima por Balvanera, que no separa Abasto de Corrientes: alta
  cautela.
- **Parque Saavedra / Garcia del Rio** (zona, debil). Puede reforzarse como anexo o candidato a
  validar con documentacion media, **no como corredor oficial**. Una fuente Clarin clave sigue sin
  revision completa.
- **Nuevo Bajo en Retiro / Esmeralda y Paraguay, Flores, Floresta, Parque Patricios.** Se mantienen
  como anexo / casos secundarios, con senal objetiva baja de contexto barrial.

**Bajo Belgrano** (area de revision, pendiente). Fase 8 liviana encontro evidencia especifica de
circuito/recorrido gastronomico, aunque con fuentes antiguas y riesgo de solapamiento. **Podria**
evaluarse su pase a anexo a validar, **sin aplicarlo aun** y sin mezclarlo con Barrio Chino o
Belgrano general. Es un caso a marcar para revision humana.

---

## 11. En espera de evidencia

Se mantienen fuera del cuerpo principal por falta de evidencia suficiente:

- **Avenida Boedo.** Las fuentes oficiales verificadas son culturales o de bares puntuales, no de
  corredor gastronomico. Mantener en espera de evidencia.
- **Federico Lacroze / Libertador a Cabildo.** La unica fuente especifica localizada es antigua y no
  verificada completa. Mantener en espera de evidencia.
- **Villa Pueyrredon / Avenida San Martin.** No se encontro evidencia de corredor; solo un hito
  puntual. Mantener en espera de evidencia.

La denominacion "En espera de evidencia" es deliberada: no descarta valor gastronomico potencial.
Indica que el recorte actual no permite sostener estos casos como polos del informe.

---

## 12. Capa objetiva de contexto territorial

La Fase 8 fuerte construyo una capa objetiva de presencia relativa por barrio y comuna a partir de
F01 (oferta registrada) y F02 (habilitaciones historicas). Es un insumo tecnico de contexto.

Que **es**: una lectura de presencia relativa en las fuentes disponibles, util para ubicar barrios y
comunas con mayor presencia registrada y para ordenar la revision humana.

Que **no es**: no es ranking, no mide densidad real, no valida vigencia operativa, no confirma
subpolos ni corredores, y no delimita oficialmente polos. El indice interno no se presenta solo:
siempre se acompana de la lectura prudente y de la limitacion territorial. El detalle esta en el
`ANEXO_TECNICO_CAPA_OBJETIVA_BORRADOR_3.md`.

Por decision metodologica, la senal objetiva permanece en anexo tecnico y no viaja al cuerpo como
dato duro.

---

## 13. Lectura comparada: evidencia documental + senal objetiva

Cruzando la clasificacion documental con la senal objetiva de contexto, con la evidencia disponible:

- **Evidencia documental fuerte con senal objetiva alta:** Palermo (subpolos), Recoleta. La senal
  acompana la lectura documental en el barrio o comuna de referencia. No valida limites internos ni
  vigencia.
- **Evidencia documental fuerte/media con senal no concluyente:** San Telmo, Puerto Madero, Barrio
  Chino, Chacarita, Monserrat, Retiro y varios emergentes. La fuente muestra presencia en el barrio,
  pero no alcanza para validar subpolos o recortes finos.
- **Senal objetiva media con alta cautela territorial:** Microcentro / Centro y Abasto. El numero no
  debe citarse sin su limitacion territorial.
- **Casos no calculables:** los corredores y areas sin delimitacion (Costanera Norte, Avenida
  Corrientes, DoHo, Avenida Caseros / Barracas, Avenida Boedo, Federico Lacroze, Villa Pueyrredon /
  Avenida San Martin) se mantienen como no calculables. La senal de un barrio no valida el eje.

**Control de riesgo metodologico.** El cuadrante "evidencia documental debil o pendiente + senal
objetiva alta" quedo **vacio**. Es decir, no hay ningun caso debil o pendiente al que la senal
objetiva empuje hacia arriba. Se deja constancia explicita porque ese cuadrante es el de mayor
riesgo de conclusion indebida: una senal barrial alta no convierte automaticamente un caso en polo.

---

## 14. Que habilita este relevamiento

Con la evidencia disponible, este relevamiento permite ordenar el universo de polos gastronomicos
documentados y distinguir areas consolidadas, zonas relevantes, emergentes y casos a validar.
Tambien permite cruzar evidencia documental con una capa objetiva de contexto, sin mezclar ambos
universos como si tuvieran el mismo valor probatorio.

Como herramienta de gestion, **podria** orientar futuras validaciones territoriales, relevamientos
de campo, comunicacion institucional y planificacion. **Permitiria** identificar zonas donde el area
ya tiene senales de interes pero donde todavia falta respaldo documental.

**No habilita** afirmar densidad, ranking, padron, vigencia ni delimitacion oficial. No reemplaza
mediciones de habilitaciones ni una verificacion de locales activos. No convierte habilitaciones u
oferta registrada en "locales activos".

---

## 15. Proximas etapas

- Revision humana de las recomendaciones de Fase 8 liviana (especialmente Paternal y Bajo Belgrano)
  antes de aplicar cualquier cambio de clasificacion.
- Revision humana del cruce `polos_vs_capa_objetiva` para decidir que tablas de contexto entran al
  anexo tecnico del Borrador 3.
- Definir recortes territoriales preliminares (solo textuales) para corredores prioritarios antes de
  cualquier cruce cuantitativo fino.
- Decidir el tratamiento editorial de las referencias gastronomicas del documento semilla (cuerpo,
  fichas o anexo).
- Solo despues: evaluar mapas de contexto (no poligonos oficiales), diseno y una version presentable.

---

## 16. Anexo metodologico

**Fuentes de base.** Borrador 2 (Fase 7), universo consolidado de Fase 5 y documento semilla interno,
todo en solo lectura. No se agregaron fuentes nuevas en Fase 9.

**Fase 8 liviana.** Reviso fuentes abiertas oficiales, periodisticas y gastronomicas para 10 casos
debiles o pendientes. No se saltaron paywalls, no se uso Google Places y las recomendaciones quedaron
marcadas como "no aplicar ahora". Detalle en
`docs/polos_gastro/fase8/VALIDACION_DOCUMENTAL_LIVIANA_FASE_8.md`.

**Fase 8 fuerte.** Capa objetiva desde F01 (2823 registros de oferta registrada) y F02 (44169
habilitaciones historicas), en solo lectura. Detalle en
`docs/polos_gastro/fase8_fuerte/METODOLOGIA_CAPA_OBJETIVA_FASE_8_FUERTE.md`.

**Advertencia.** Las referencias gastronomicas del documento semilla son preliminares. No constituyen
padron, ranking, censo, prueba de densidad ni validacion de vigencia.

---

## 17. Anexo tecnico de capa objetiva

El tratamiento tecnico de la capa objetiva -metodologia resumida, tabla interpretativa (no ranking),
casos de senal alta, media y no calculables, y advertencias obligatorias- esta en
`docs/polos_gastro/fase9_borrador_3/ANEXO_TECNICO_CAPA_OBJETIVA_BORRADOR_3.md`.

La tabla consolidada del Borrador 3, con las columnas de contexto por caso, esta en
`outputs/polos_gastro/fase9_borrador_3/tablas/tabla_polos_para_informe_borrador_3.csv`.
