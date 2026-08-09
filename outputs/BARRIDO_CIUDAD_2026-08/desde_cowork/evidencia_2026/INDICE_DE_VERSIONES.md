# Índice de versiones · evidencia 2026

Qué documento de esta carpeta está vigente y cuál quedó superado. **Nada se borra**: un documento
que circuló tiene que poder encontrarse, junto con el rastro de que se corrigió.

*Última actualización: 8 de agosto de 2026 · ronda 12.*

---

## Láminas del Plan 2026

| documento | estado | |
|---|---|---|
| `LAMINAS_v2_2026-08-08.md` | **VIGENTE en v2.1** | corregido en la ronda 12 |
| `LAMINAS_PLAN_2026_POLOS_Y_CLUSTERS.md` | **SUPERADO** por la v2 | circuló |

### Qué cambió en la v2.1 (ronda 12)

**La lámina 10 se reescribió entera**: el catálogo está cerrado al 100 % —90 de 90 verificados,
88 operando— y el hallazgo de los nueve años queda con denominador.

**Las láminas 14 y 15 se rehicieron de cero.** Estaban armadas sobre el informe en PDF del
IDECBA. **«Microcentro» no está entre los 48 ejes vigentes**, así que el 63,2 % y el −7,2 pp
—que sostenían la lámina 14 entera y la primera fila de la 15— no existen en la serie de la
Ciudad. Con la planilla como autoridad se cayeron además dos afirmaciones: que *«los polos
consagrados son los que más comercio pierden»* (medido: −1,69 pp contra −1,30 pp, con 21 casos
por lado) y que *«la brecha no es entre el norte y el sur»* (el Norte pierde en los nueve ejes
que releva la Ciudad; el Sur es la única zona con media positiva).

**Y dos cifras más:** la lámina 4 pierde el −4,6 de Liniers (en la serie vigente Liniers no se
movió) y la 12 corrige la de Montes de Oca (89,7 % y −1,9 pp, no 87,1 % y estable).

**Pendiente que bloquea la lámina 5:** Plaza Asturias y El Globo no están cargados como hitos y
no tienen verificación.

**Qué cambió, y por qué conviene que el rastro quede.** La v1 decía en la lámina 10 que *«3 bares
notables del catálogo oficial están cerrados y siguen figurando en el padrón vigente»*, listando
Plaza Bar, La Buena Medida y **The New Brighton**.

Son **dos**. The New Brighton opera con quiebra decretada y **sigue atendiendo**: hay una reseña de
mayo de 2026, posterior a la quiebra, que describe servicio real con piano en vivo, y ninguna de
las siete coberturas afirma que dejó de atender. El cierre fue una inferencia sobre un titular —el
defecto quedó registrado como **FD-20**, «un acto jurídico no es un hecho operativo»—.

La lámina **mejora** con la corrección: nueve años de un local cerrado en un catálogo firmado el
03/08/2026 ya es el hallazgo, y ahora resiste que alguien en la sala diga «pero yo comí ahí».

---

## Lo que la ronda 10 dejó vigente sobre estos documentos

| documento | estado |
|---|---|
| `fuentes_con_defecto_FD20_FD22.csv` | **VIGENTE y cargado** — la capa quedó completa, FD-01 a FD-22 |
| `idecba_ocupacion_por_eje.csv` | **REESCRITO en la ronda 12** sobre los 48 ejes del XLSX |
| `idecba_ejes_comerciales.csv` | **REESCRITO en la ronda 12** sobre los 48 ejes, con tramos |
| `LOS_POLOS_CONSAGRADOS_SON_LOS_QUE_CAEN.md` | **REFUTADO en la ronda 12** — no se usa; se conserva porque circuló |
| `EL_CATALOGO_CERRADO.md` | **VIGENTE**, con el remate del Microcentro corregido en la ronda 12 |
| `LA_FUENTE_QUE_NOS_FALTABA.md` | **VIGENTE**, corregido en la ronda 12 (48 ejes; calibración, no equivalencia) |
| `catalogo_90_estado_final.csv` | **VIGENTE y cargado** — capa `hitos_capa_2026_r11.csv` |
| `catalogo_pendientes_para_diego.csv` · `tanda_1_y_2_para_diego.csv` | **SUPERADOS** por el cierre del catálogo al 100 % |
| `errata_2026-08-08.csv` | aplicada, salvo los puntos que la ronda 10 volvió a mover |
| `errata_2026-08-08_ronda_10.csv` | **aplicada** en la ronda 12 — ver `ronda_12/errata_ronda_10_aplicada.csv` |

### ~~Salvedad~~ sobre `idecba_ocupacion_por_eje.csv` — **RESUELTO en la ronda 12**

Sus **53 ejes eran el universo anterior** del IDECBA. El glosario y el relevamiento vigentes traen
**48**. Probado contra los cuatro cuatrimestres del `.xlsx` —1.º, 2.º y 3.º de 2025 y 1.º de
2026—, el PDF **no coincide con ninguno**: es una edición más vieja y sus tasas son de su propio
período. **No se mezclan con las de 2026.**

Seis ejes del PDF ya no existen en el universo vigente: **Cañitas**, **Palermo Hollywood**,
Microcentro, Jujuy, Murillo y Nazca. **Palermo Soho sí sigue.** Se sumó Lavalle.

**La ronda 12 reescribió las dos tablas** —`idecba_ocupacion_por_eje.csv` y
`idecba_ejes_comerciales.csv`— sobre los 48 ejes con los valores del XLSX (1.er cuatrimestre de
2026) y los tramos del glosario. La tabla completa, con tramos y cruce contra el Atlas, está en
`ronda_12/idecba_48_autoridad.csv`; qué sostenía cada eje que salió, en
`ronda_12/idecba_los_6_que_salen.csv`.

**Esta salvedad estaba escrita desde la ronda 10 y las láminas se armaron igual con los números
del PDF.** Registrar el defecto no lo corrige: el aviso quedó en este índice y no llegó al
documento que circulaba.

### Correcciones de la ronda 10 sobre la errata

| punto de la errata | qué dice la errata | qué midió la ronda 10 |
|---|---|---|
| 5 · cola de R20 | 41 % de superficie y 53 % de locales | **47 % y 30 %** — el tramo «Cabildo–Balbín» de la ronda 8 estaba mal anclado |
| 8 · catálogo FD | «faltarían seis» | faltaban **diez**; los cinco cargados incluían FD-12, no FD-05 |
| 10 · PGR_P004 | ¿sigue abriendo por otra vía? | **sí, por la vía A**. No es baja, pero queda con una sola vía |
