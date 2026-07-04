# reporting_dgdgas — base de generación de informes DGDGAS (v1)

Base de código **reutilizable** para producir informes institucionales de la
Dirección General de Desarrollo Gastronómico (DGDGAS) con el sistema visual
`DGDGAS Informes — Design System v1`.

> **Estado:** esqueleto. Estos módulos definen la API, el estilo y el flujo,
> pero **no generan todavía un informe completo** ni se integran con Cafecito
> ni PolosGastro. La documentación del sistema está en
> `docs/datagastro_design_system/`.

## Módulos

| Archivo | Rol |
|---------|-----|
| `style_tokens_dgdgas.py` | Carga los tokens (`docs/.../tokens/design_tokens_dgdgas.json`) y resuelve nombres semánticos → HEX. Fuente de estilo. |
| `report_components_dgdgas.py` | Primitivas de componentes (portada, índice, cajas, tabla, mapa, síntesis, ficha de polo…). Backend-agnósticas. |
| `template_pdf_informe_dgdgas.py` | Esqueleto de generador PDF. Arma el «plan de componentes» desde el YAML de contenido. Render matplotlib = punto de extensión. |
| `template_docx_informe_dgdgas.py` | Esqueleto de generador DOCX / payload Google Docs. Comparte el plan con el PDF. |

## Principio de diseño

```
contenido (YAML/JSON)  ──►  build_report_plan()  ──►  plan de componentes
      │                          (mapea a Components)         │
      │                                                       ▼
   tokens (semánticos)  ──────────────────────────►  backend PDF / DOCX / GDocs
```

- **Contenido** → en YAML/JSON, uno por informe (nunca hardcodeado en código).
- **Estilo** → en tokens; el código usa nombres semánticos.
- **Backend** → traduce el plan a un formato. El plan es común a PDF, DOCX y
  Google Docs, así que un mismo contenido produce salidas consistentes.

## Uso rápido (inspección del plan, sin render)

Los esqueletos ya permiten construir e inspeccionar el plan de componentes.
El render binario se implementa en la fase de aplicación (ver
`docs/datagastro_design_system/HANDOFF_CLAUDE_DESIGN_A_CODE.md`).

```
# Smoke check de tokens y componentes (no genera archivos):
python -m scripts.shared.reporting_dgdgas.style_tokens_dgdgas
python -m scripts.shared.reporting_dgdgas.report_components_dgdgas

# Construir el plan desde un YAML de contenido (requiere PyYAML):
python -m scripts.shared.reporting_dgdgas.template_pdf_informe_dgdgas \
    --contenido docs/<proyecto>/contenido_informe.yaml \
    --salida outputs/<proyecto>/INFORME.pdf --plan-only

# Exportar payload Google Docs (JSON) desde el contenido:
python -m scripts.shared.reporting_dgdgas.template_docx_informe_dgdgas \
    --contenido docs/<proyecto>/contenido_informe.yaml \
    --salida outputs/<proyecto>/payload_gdocs.json --gdocs
```

## Dependencias

- `style_tokens_dgdgas.py` y `report_components_dgdgas.py`: **solo stdlib**.
- Construir el plan desde YAML: **PyYAML** (leer contenido).
- Render PDF: **matplotlib** (ya usado en el repo).
- Render DOCX: **python-docx** (no requerido para el payload Google Docs).

> No se instalan dependencias nuevas en la v1. Si en la fase de aplicación
> hiciera falta `python-docx` u otra, se pide autorización antes de instalar.

## Reglas al implementar un informe concreto

- Marca pública **DGDGAS** (no DataGastro).
- Preguntas antes de resultados; multi-respuesta como menciones (suma puede
  superar 100 %).
- Mapas: nota de alcance obligatoria si son conceptuales/preliminares; sin
  límites oficiales inexistentes.
- Salidas en `outputs/<proyecto>/` con **nombre de versión nuevo**; nunca
  sobrescribir un final.
- Pasar el QA de `docs/datagastro_design_system/QA_VISUAL_INFORMES_DGDGAS.md`.
- **No** integrar aún con Cafecito ni PolosGastro (la v1 es solo la base).
