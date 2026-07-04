# Handoff general - DataGastro / DGDGAS

Fecha: 2026-07-02. Documento interno de traspaso para retomar el trabajo sin perder contexto.
Cubre las tres lineas activas: PolosGastro, Design System DGDGAS y Cafecito. Todo el trabajo
reciente esta **sin commitear** en la rama `mercados-gastronomicos-v2` (HEAD en `525480a`).

---

## 1. Estado general

Las tres lineas quedaron en punto de decision humana, no de ejecucion:

- **PolosGastro** tiene el Borrador 3 metodologicamente cerrado, auditado y con dos ajustes
  menores post-auditoria aplicados y trazados. Existe una propuesta de decisiones humanas para
  habilitar el Borrador 4.
- **Design System DGDGAS** tiene el mapeo experimental validado con dos previews HTML (v1 minima y
  v2 ampliada con tabla completa, cinta de estado y contraste corregido). Nada esta canonizado.
- **Cafecito** tiene una version ejecutiva simplificada en Markdown (~4 paginas vs ~14 de la
  Revision 4), lista para revision humana. La Revision 4 en PDF quedo intacta.

Nada se publico, nada se commiteo, ningun dato fuente ni script productivo se toco. El pipeline
publico F01-F05 esta intacto.

---

## 2. PolosGastro

**Fases cerradas.** Fase 7 (Borrador 2), Fase 8 liviana (validacion documental), Fase 8 fuerte
(capa objetiva de contexto), Fase 9 (Borrador 3), auditoria final del Borrador 3 y fase de
consolidacion post-auditoria.

**Archivos principales creados (recientes).**

- `docs/polos_gastro/fase9_borrador_3/` - los 6 documentos del Borrador 3 mas
  `AJUSTES_MENORES_POST_AUDITORIA_BORRADOR_3.md` y `PROPUESTA_DECISIONES_HUMANAS_BORRADOR_4.md`.
- `outputs/polos_gastro/fase9_borrador_3/tablas/tabla_polos_para_informe_borrador_3.csv` - tabla
  consolidada de 32 registros.
- `docs/revisiones/REVISION_FINAL_BORRADOR_3_POLOS_GASTRO_2026_07_01.md` - auditoria (verdicto:
  avanzar con condiciones).
- `docs/revisiones/PLAN_PROXIMOS_PASOS_POLOS_Y_DESIGN_SYSTEM_2026_07_01.md` - plan etapas A-F.
- `docs/revisiones/PLAN_BORRADOR_4_POLOS_GASTRO_2026_07_01.md` - plan del Borrador 4.
- QAs: `QA_FABLE5_PREVIEW_Y_BORRADOR3_2026_07_01.md` y
  `QA_CONSOLIDACION_POST_PREVIEW_2026_07_01.md`.

**Estado del Borrador 3.** Cerrado y auditado: 32 registros, 4 areas nucleo (Palermo con
subpolos, Recoleta, San Telmo, Puerto Madero con documentacion media), Belgrano como macroarea de
revision, Abasto en anexo, capa objetiva tratada como contexto (nunca ranking; el indice numerico
no viaja al documento). Ajustes post-auditoria aplicados: (a) Paternal paso de tipo "corredor" a
"area de revision (barrio-circuito a validar)" para eliminar la unica excepcion a la regla
"corredor sin delimitacion = no calculable"; (b) en Avenida Corrientes se suavizo "validan
identidad" por "respaldan la identidad". Ningun cambio de grupo aplicado.

**Estado de la preview v2.** Creada en
`outputs/datagastro_design_system/previews/polos_borrador3_preview_v2/` (HTML + CSS, 6 hojas A4
simuladas): portada DGDGAS, tabla ejecutiva de 8 casos, tabla completa de 32 filas en 3 hojas con
cortes por grupo, capa objetiva con advertencias y muestrario de 10 chips de estado. Pendiente de
validacion visual humana. La preview v1 (`polos_borrador3_preview_minima/`) se conserva.

**Decisiones humanas pendientes** (detalle con recomendacion conservadora en
`PROPUESTA_DECISIONES_HUMANAS_BORRADOR_4.md`): Paternal (sube o no a documentacion media), Bajo
Belgrano (pase a anexo a validar), Corrientes/Abasto (tratamiento cruzado), Caseros/Barracas
(denominacion y recorte), DoHo y Costanera Norte (recortes textuales), Parque Saavedra (fuente
Clarin sin verificar), referencias del documento semilla (recomendado: insumo interno), esquema de
capa objetiva (recomendado: mantener cuerpo cualitativo + anexo sin indice), columna de senal en
la tabla del anexo, y mapas futuros (recomendado: posponer).

**Proximo paso recomendado.** Acta breve de decisiones (una linea por caso) y recien despues
redactar el Borrador 4 como Markdown presentable interno, copiando desde el Borrador 3 (nunca
editando fase9 en el lugar).

---

## 3. Design System DGDGAS

**Export de Claude Design.** Importado en
`docs/datagastro_design_system/claude_design_export_v1/` (tokens.json + componentes + handoff).
Revisado; no entra al pipeline por accidente.

**Mapeo experimental.** `tokens/design_tokens_dgdgas_claude_design_mapped_v1.json` +
`tokens/MAPEO_TOKENS_CLAUDE_DESIGN_A_BASE_LOCAL.md` + diff CSV. Conserva la forma local del JSON
(compatible con `style_tokens_dgdgas.py`) y guarda lo nuevo como extension experimental marcada
`do_not_use_as_canonical: true`.

**Que esta listo.**

- Dos previews HTML validando que los tokens alcanzan para piezas institucionales sobrias.
- Evaluaciones en `docs/datagastro_design_system/previews/`: README y evaluacion de la v1,
  `EVALUACION_ACCESIBILIDAD_PREVIEW_V2.md` (contraste WCAG calculado con funcion propia) y
  `EVALUACION_TABLA_32_FILAS_PREVIEW_V2.md`.
- Componentes probados: portada, cinta de estado del documento (nueva en v2), TablaPolos
  (ejecutiva y completa), EstadoChip con 10 estados, cajas de lectura/advertencia/metodo,
  placeholder de mapa con disclaimer.
- Propuestas concretas de `state_details` para los estados faltantes (contexto, no_delimita,
  anexo) con contraste verificado.

**Que no conviene canonizar todavia.**

- `footer.text_color -> text.muted`: falla AA (2.98:1); necesita un token caption AA.
- `brand.secondary` y `brand.accent` como colores de texto chico (4.34 y 3.26): solo filetes,
  bordes o texto grande; si se necesitan como texto, usar las variantes oscurecidas probadas
  (#2C6E9E, #9A5C1F, #8A4B22).
- Chips complejos, halos de mapa, sombras de impresion: sin backend probado.
- La decision tipografica (las previews solo demuestran el fallback Arial/Calibri; Libre
  Franklin / Source Sans 3 no estan instaladas).

**Que falta antes de aplicar diseno real.** Validacion visual humana de la preview v2; tokenizar
los ajustes aprobados (state_details faltantes, cinta de estado, caption AA) en un mapeo v2 o en
canonicos con aprobacion explicita; y recien despues aplicar sobre **copia controlada** del
Borrador 4 (etapas C-E del plan de proximos pasos). Tocar `design_tokens_dgdgas.json/.yaml` o
`scripts/shared/` requiere permiso explicito de Diego.

---

## 4. Cafecito

**Problema editorial detectado.** La Revision 4 (14 paginas, 12 secciones) esta armada como
expediente: andamiaje "Pregunta analizada / Tipo / Que permite observar" repetido 9 veces, nota de
multi-respuesta duplicada, inventario de preguntas que duplica las secciones tematicas y sintesis
al final. El contenido y la prudencia estan bien; la arquitectura no sirve para una lectura de
autoridad.

**Version ejecutiva creada.** `INFORME_CAFECITO_VERSION_EJECUTIVA_SIMPLIFICADA.md` (~4 paginas):
piramide invertida (sintesis primero), ficha del relevamiento, 4-5 bloques con formato
dato/lectura/implicancia, lectura institucional, 6 aspectos a considerar y anexo metodologico
breve. Marca DGDGAS; cifras reales del CSV de resultados (79 respuestas; base 78 en contacto).

**Archivos creados** (en `docs/cafecito/revision_ejecutiva/`):
`DIAGNOSTICO_EDITORIAL_CAFECITO_REVISION_4.md`, `INFORME_CAFECITO_VERSION_EJECUTIVA_SIMPLIFICADA.md`,
`CAMBIOS_PROPUESTOS_CAFECITO_VERSION_EJECUTIVA.md`, `RESUMEN_PARA_JEFATURA_CAFECITO.md` (una
pagina para mail) y `QA_REVISION_EJECUTIVA_CAFECITO.md`.

**Que quedo fuera del cuerpo** (como respaldo, no perdido): indice, inventario de preguntas,
desglose de respuestas por dia/franja, acompanamiento (pareja/amigos/familia), tipos de pregunta,
cruces exploratorios, y los mapas/rankings de la red de cafeterias (quedo solo la ficha de 3 datos
con nota prudente en el anexo).

**Decisiones pendientes.** Si "acompanamiento" vuelve al cuerpo; si el desglose por dia vuelve a
la ficha (el dato vive en la Revision 4, no en los outputs editables); y si la version ejecutiva
reemplaza a la Revision 4 como pieza principal o convive como resumen.

**Proximo paso recomendado.** Revision humana del recorte editorial; si se aprueba, decidir el
destino (nueva revision del PDF via YAML editable + script de revision, con permiso, o pieza
Markdown independiente).

---

## 5. Que NO hacer todavia

- **No generar PDF final** de nada (Polos, Cafecito ejecutivo, previews).
- **No generar DOCX final.**
- **No commit / no push / no staging** (todo el trabajo esta untracked por decision de Diego).
- **No aplicar diseno completo** a informes reales; solo sobre copia controlada y tras validar la
  preview v2 y tokenizar ajustes.
- **No tocar datos fuente** (`data/`, XLSX de Cafecito, pipeline F01-F05) ni scripts productivos
  (`src/`, `scripts/shared/`, `style_tokens_dgdgas.py`, generadores de Cafecito) sin permiso.
- **No tocar tokens canonicos** (`design_tokens_dgdgas.json/.yaml`).
- **No publicar el Borrador 3** (es interno por diseno) ni circular las previews como muestra
  institucional.
- **No reemplazar Cafecito Revision 4 sin revision humana** del recorte editorial.
- **No usar Google Places** ni plataformas privadas; **no usar DataGastro como marca publica**.

---

## 6. Proximos pasos priorizados

1. **Revisar la version ejecutiva de Cafecito** (es lo mas cerca de un entregable a jefatura):
   validar recorte, cerrar las 3 decisiones editoriales pendientes.
2. **Cerrar las decisiones humanas de PolosGastro** con acta breve, usando la propuesta con
   recomendaciones conservadoras.
3. **Preparar el Borrador 4 interno de PolosGastro** (Markdown presentable, copia desde Borrador
   3, decisiones aplicadas con trazabilidad).
4. **Validar la preview visual v2** en navegador y aprobar/rechazar los ajustes de tokens
   propuestos (state_details, caption AA, cinta de estado, tipografia).
5. **Recien despues, evaluar PDF/DOCX de prueba** (marcados "prueba - no publicable"), con permiso
   para tocar scripts de render si hiciera falta.

---

## 7. Prompt corto para la proxima sesion

> Retomamos DataGastro (repo `C:\proyectos\Gastronomia\DataGastro`). Lee primero
> `docs/revisiones/HANDOFF_GENERAL_DATAGASTRO_DGDGAS_2026_07_02.md` y trabaja segun sus reglas
> (no commit/push/staging, no PDF/DOCX, no tocar datos fuente, ni scripts productivos, ni tokens
> canonicos; marca publica DGDGAS). Hoy quiero avanzar con el paso N de los proximos pasos
> priorizados: [describir paso y decisiones ya tomadas]. Estas son mis decisiones sobre los
> pendientes: [pegar respuestas a las decisiones humanas que correspondan].

(Reemplazar N y los corchetes. Si el paso es el Borrador 4, adjuntar o dictar el acta de
decisiones; sin acta, el Borrador 4 no se redacta.)
