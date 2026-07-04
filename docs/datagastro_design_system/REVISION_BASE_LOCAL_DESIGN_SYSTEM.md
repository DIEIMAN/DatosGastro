# Revision base local - DGDGAS Informes Design System v1

Fecha de revision: 2026-07-01.

Alcance revisado:

- `docs/datagastro_design_system/`
- `scripts/shared/reporting_dgdgas/`

No se revisaron ni modificaron Cafecito, PolosGastro, MercadosGastro, CasasDePastas, PDFs finales, datos fuente, `src/`, `dashboard/`, `notebooks/` ni outputs de informes.

## 1. Archivos existentes

### Documentacion del sistema

| Archivo | Funcion |
| --- | --- |
| `README_DGDGAS_DESIGN_SYSTEM.md` | Punto de entrada. Resume alcance, estructura, relacion con el pack de Claude Design y orden de lectura. |
| `DGDGAS_INFORMES_DESIGN_SYSTEM_V1.md` | Documento maestro. Define marca, tono, estructura comun, reglas de contenido, cartografia, tokens resumidos, estados y QA publico. |
| `COMPONENTES_INFORMES_DGDGAS.md` | Catalogo de componentes reutilizables. Describe proposito, tokens, contenido esperado y reglas por componente. |
| `PLANTILLAS_PAGINA_DGDGAS.md` | Plantillas de pagina A4: portada, indice, datos generales, preguntas, resultados, mapas, fichas, tablas, sintesis, aspectos y anexos. |
| `HANDOFF_CLAUDE_DESIGN_A_CODE.md` | Guia de pasaje desde Claude Design a implementacion local. Explica fuente de verdad, flujo de generacion y guardrails. |
| `QA_VISUAL_INFORMES_DGDGAS.md` | Checklist de QA visual, editorial y publico para informes o plantillas. |

### Tokens y plantillas

| Archivo | Funcion |
| --- | --- |
| `tokens/design_tokens_dgdgas.yaml` | Fuente de verdad declarada para tokens semanticos. |
| `tokens/design_tokens_dgdgas.json` | Version equivalente para herramientas y scripts Python. |
| `templates/template_informe_dgdgas.yaml` | Plantilla de contenido de informe. Se debe copiar y completar por proyecto en una fase futura. |
| `templates/template_payload_google_docs_dgdgas.json` | Plantilla de payload por bloques para Google Docs. |

### Scripts compartidos

| Archivo | Funcion |
| --- | --- |
| `scripts/shared/reporting_dgdgas/README.md` | Explica el rol de la base de codigo, el flujo contenido -> plan -> backend y las dependencias. |
| `style_tokens_dgdgas.py` | Carga tokens desde JSON, resuelve referencias semanticas y expone helpers de color, tipografia, layout, cajas y estados. Solo usa stdlib. |
| `report_components_dgdgas.py` | Define el contrato de canvas y la fabrica `Components`. Emite specs de componentes sin renderizar. Solo usa stdlib y tokens. |
| `template_pdf_informe_dgdgas.py` | Esqueleto de generador PDF. Construye un plan desde YAML, pero `render_pdf()` sigue pendiente. |
| `template_docx_informe_dgdgas.py` | Esqueleto de generador DOCX / Google Docs. Convierte plan a payload GDocs; `render_docx()` sigue pendiente. |

Archivos creados por esta revision:

- `REVISION_BASE_LOCAL_DESIGN_SYSTEM.md`
- `CHECKLIST_SYNC_CLAUDE_DESIGN.md`

## 2. Funcion de cada bloque

- Documentacion: fija criterio editorial, visual, de marca y QA.
- Tokens: separan estilo de contenido y permiten reestilar sin tocar generadores.
- Plantillas: separan estructura de contenido de implementacion visual.
- Componentes Python: definen una API comun para PDF, DOCX y Google Docs.
- Templates PDF/DOCX: preparan el flujo, pero todavia no renderizan documentos completos.

## 3. Tokens definidos

Los tokens estan agrupados en:

- `meta`: sistema, version, marca publica, nombre interno y descripcion.
- `color.brand`: `primary`, `secondary`, `accent`.
- `color.text`: `primary`, `secondary`, `muted`, `on_brand`.
- `color.surface`: `page`, `card`, `note`, `warn`, `ok`, `zebra`.
- `color.border`: `subtle`, `strong`.
- `color.status`: `strong`, `medium`, `weak`, `pending`, `review`.
- `color.chart`: secuencia de colores, grilla y color de vacio.
- `typography`: familias, roles, escala, pesos e interlineado.
- `layout`: pagina A4 vertical, DPI, margenes y ancho util.
- `spacing`: escala base 4 (`xs` a `xxl`).
- `radius`: `none`, `sm`, `md`, `lg`, `pill`.
- `table`: estilo de encabezado, filas, bordes, padding y alineaciones.
- `box`: estilos para `question`, `reading`, `method`, `warning`, `validation`.
- `map`: colores y reglas base para mapas territoriales.
- `footer`: patron, color, regla y numero de pagina.
- `content_states`: `principal`, `secundario`, `preliminar`, `pendiente`, `anexo`, `advertencia`, `interno`, `historico`.

Verificacion: `design_tokens_dgdgas.yaml` y `design_tokens_dgdgas.json` tienen la misma estructura y valores funcionales. La unica diferencia detectada es un salto de linea final en `meta.descripcion` al parsear YAML.

## 4. Componentes definidos

En documentacion y en `Components` estan definidos:

- Portada institucional.
- Indice.
- Ficha de relevamiento.
- Caja de pregunta analizada.
- Caja de lectura de resultados.
- Nota metodologica breve.
- Alcance / advertencia.
- Requiere validacion.
- Tabla institucional.
- Tabla de polos.
- Ficha de polo.
- Mapa territorial.
- Grafico de barras.
- Sintesis / lista de puntos.
- Aspectos a considerar / lista de puntos.
- Anexo.
- Estado de documentacion.

La implementacion actual emite specs estructuradas y valida algunas reglas, por ejemplo nota de alcance obligatoria en mapas conceptuales. No dibuja todavia PDF ni DOCX reales.

## 5. Plantillas existentes

Plantillas de pagina documentadas:

- P0 Portada.
- P1 Indice.
- P2 Datos generales.
- P3 Preguntas / variables.
- P4 Resultado con grafico.
- P5 Resultado con mapa.
- P6 Ficha de polo.
- P7 Tabla comparativa / de polos.
- P8 Sintesis.
- P9 Aspectos a considerar.
- P10 Anexo.

Plantillas de contenido:

- `template_informe_dgdgas.yaml`: estructura completa de informe con portada, indice, datos generales, fuente, preguntas, resultados, sintesis, aspectos, anexos y nota metodologica.
- `template_payload_google_docs_dgdgas.json`: estructura de bloques para Google Docs.

## 6. Que falta implementar

- Backend real de PDF (`render_pdf`) con canvas matplotlib u otro motor.
- Backend real de DOCX (`render_docx`) con `python-docx`.
- Agrupacion fina de componentes por paginas/secciones para Google Docs.
- Exportacion real de un informe aplicado a un proyecto concreto.
- Tests unitarios sobre `build_report_plan()`, tokens y reglas de componentes.
- Validacion automatica de QA publico sobre salidas finales.
- Previews visuales de componentes para comparar con Claude Design.
- Sincronizacion con un proyecto remoto de Claude Design cuando exista.

## 7. Que depende de Claude Design

- Confirmar si el sistema remoto se llamara exactamente `DGDGAS Informes` o `DGDGAS Informes - v1`.
- Importar o recrear tokens en el proyecto remoto.
- Crear previews visuales aprobadas de componentes y plantillas.
- Comparar decisiones visuales finas: jerarquia, espaciado, cajas, tablas, mapas, portadas y anexos.
- Detectar diferencias entre el criterio visual remoto y la base local.
- Definir si el remoto sera fuente visual principal o solo referencia de validacion.

No hay que usar Claude Design para aplicar el sistema a informes hasta que el usuario lo pida explicitamente.

## 8. Que depende de PyYAML o python-docx

Estado local verificado sin instalar nada:

- `yaml`: disponible.
- `docx`: no disponible.
- `matplotlib`: disponible.

Dependencias por funcion:

- PyYAML: necesario para que `_load_contenido()` lea archivos `.yaml` y para usar `template_pdf_informe_dgdgas.py --plan-only` desde YAML. Si se quisiera evitar PyYAML en otro entorno, se podria alimentar `build_report_plan()` con un dict ya parseado o usar una entrada JSON.
- python-docx: necesario para implementar el render DOCX real. La base actual no lo requiere para cargar tokens, emitir componentes ni generar payload Google Docs.
- matplotlib: necesario para implementar el render PDF real segun la orientacion actual del esqueleto. Esta disponible en el entorno, pero el backend todavia no esta implementado.

## 9. Que se puede hacer sin dependencias nuevas

Sin instalar nada nuevo se puede:

- Leer y documentar el sistema.
- Validar sintaxis Python con `py_compile`.
- Cargar tokens JSON con `style_tokens_dgdgas.py`.
- Resolver tokens semanticos a HEX.
- Emitir specs de componentes con `report_components_dgdgas.py`.
- Construir el plan desde YAML en este entorno, porque PyYAML ya esta disponible.
- Comparar YAML/JSON de tokens.
- Editar documentacion, tokens y plantillas.
- Crear payloads o planes en memoria.
- Preparar previews estaticas simples si se implementan con herramientas ya disponibles.

No se puede, en el estado actual, generar un PDF final real o un DOCX final real solo con estos esqueletos: ambos renderers estan marcados como pendientes.

## 10. Que comparar cuando exista el proyecto remoto en claude.ai/design

Cuando exista el proyecto remoto, conviene comparar:

- Nombre del proyecto remoto contra el nombre local del sistema.
- Version (`1.0.0`) y criterio de marca publica DGDGAS.
- Paleta completa: `brand`, `text`, `surface`, `border`, `status`, `chart`.
- Tipografias, escala y pesos.
- Margenes A4, espaciado y radios.
- Estilos de cajas: pregunta, lectura, nota, advertencia, validacion.
- Estilos de tablas y tablas de polos.
- Estilos de mapas territoriales y nota de alcance.
- Footer y patron de pagina.
- Estados de contenido y etiquetas.
- Plantillas P0-P10.
- Compatibilidad entre componentes remotos y funciones de `Components`.
- Diferencias que deban aplicarse en repo, siempre sin tocar informes finales.

## Verificacion realizada

- `python -m scripts.shared.reporting_dgdgas.style_tokens_dgdgas`: OK.
- `python -m scripts.shared.reporting_dgdgas.report_components_dgdgas`: OK.
- `python -m py_compile` sobre los cuatro scripts compartidos: OK.
- `python -m scripts.shared.reporting_dgdgas.template_pdf_informe_dgdgas --contenido docs/datagastro_design_system/templates/template_informe_dgdgas.yaml --salida outputs/_no_escribir_revision_base_local.pdf --plan-only`: OK, devuelve 13 componentes y no escribe salida.
- Comparacion JSON/YAML de tokens: misma estructura y sin diferencia funcional, salvo salto final en `meta.descripcion`.
