"""DGDGAS Informes v1 — ESQUELETO de generador de informe DOCX / Google Docs.

Plantilla reutilizable para producir un DOCX editable (o payload para Google
Docs) con el sistema visual DGDGAS. Comparte el "plan de componentes" con el
generador PDF (build_report_plan), de modo que el mismo contenido produce PDF y
DOCX consistentes.

NO genera todavia un documento completo ni se integra con proyectos concretos.
El backend DOCX (python-docx) se implementa en la fase de aplicacion.

Formatos que cubre esta plantilla:
  - DOCX editable (python-docx).
  - Payload de bloques para Google Docs, compatible con
    docs/datagastro_design_system/templates/template_payload_google_docs_dgdgas.json

Uso previsto (una vez implementado el backend):
    python -m scripts.shared.reporting_dgdgas.template_docx_informe_dgdgas \
        --contenido docs/<proyecto>/contenido_informe.yaml \
        --salida outputs/<proyecto>/INFORME_<PROYECTO>_V1.docx
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .report_components_dgdgas import Components
from .style_tokens_dgdgas import Tokens
from .template_pdf_informe_dgdgas import build_report_plan, _load_contenido


# Mapeo de componentes internos -> tipos de bloque del payload Google Docs.
# Mantiene alineado el esqueleto con template_payload_google_docs_dgdgas.json.
_COMPONENT_TO_BLOCK = {
    "caja": {
        "question": "question",
        "reading": "reading",
        "method": "method",
        "warning": "warning",
        "validation": "warning",
    },
    "tabla": "table",
    "lista_puntos": "bullets",
    "ficha_relevamiento": "facts",
    "mapa_territorial": "map",
    "grafico_barras": "image",
    "anexo": "paragraph",
}


def plan_to_gdocs_payload(plan: list[dict], contenido: dict) -> dict:
    """Convierte el plan de componentes a un payload de bloques Google Docs.

    Produce la misma estructura que el template de payload (meta/cover/index/
    sections). Es una traduccion 1:1 del plan; el estilo real lo aplica el
    consumidor del payload (Google Docs) segun los tokens.
    """
    meta = contenido.get("meta", {})
    portada = contenido.get("portada", {})
    payload: dict[str, Any] = {
        "meta": {
            "title": portada.get("titulo", ""),
            "subtitle": portada.get("subtitulo", ""),
            "presenta": portada.get("kicker_marca", ""),
            "footer": meta.get("footer", "DGDGAS"),
            "version": "GENERADO_V1",
        },
        "cover": {
            "intro": portada.get("descripcion", ""),
            "facts": portada.get("datos_generales", []),
        },
        "index": contenido.get("indice", {}).get("entradas", []),
        "sections": [],
    }

    # Agrupacion simple: cada componente se emite como un bloque suelto. Un
    # backend mas fino puede agrupar por seccion; el esqueleto mantiene el
    # orden del plan para trazabilidad.
    blocks: list[dict] = []
    for entry in plan:
        comp = entry["component"]
        if comp == "caja":
            btype = _COMPONENT_TO_BLOCK["caja"].get(entry.get("kind"), "paragraph")
            blocks.append({"type": btype, "titulo": entry.get("titulo"),
                           "text": entry.get("cuerpo")})
        elif comp in _COMPONENT_TO_BLOCK:
            btype = _COMPONENT_TO_BLOCK[comp]
            block = {"type": btype, "title": entry.get("titulo") or entry.get("nombre")}
            for key in ("headers", "rows", "items", "intro", "filas",
                        "base", "fuente", "nota", "nota_alcance"):
                if key in entry:
                    block[key] = entry[key]
            blocks.append(block)

    payload["sections"].append({
        "number": "",
        "title": "Contenido",
        "page": None,
        "subtitle": "",
        "blocks": blocks,
    })
    return payload


def render_docx(plan: list[dict], tokens: Tokens, salida: Path) -> None:
    """Renderiza el plan a DOCX. PUNTO DE EXTENSION (aun no implementado).

    Un backend python-docx debe recorrer ``plan`` y crear parrafos/tablas/cajas
    con los estilos derivados de los tokens (familia sans, escala de titulos,
    colores de caja). Se deja como NotImplementedError para no fingir salida.
    """
    raise NotImplementedError(
        "El backend de render DOCX se implementa en la fase de aplicacion "
        f"(ver HANDOFF). Plan con {len(plan)} componentes listo para {salida}. "
        "Alternativa disponible ya: exportar el payload Google Docs con "
        "--gdocs."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generador DOCX/GDocs DGDGAS (esqueleto).")
    parser.add_argument("--contenido", required=True, type=Path)
    parser.add_argument("--salida", required=True, type=Path)
    parser.add_argument("--gdocs", action="store_true",
                        help="Exportar payload de bloques Google Docs (JSON) en lugar de DOCX.")
    args = parser.parse_args(argv)

    tokens = Tokens.load()
    contenido = _load_contenido(args.contenido)
    plan = build_report_plan(contenido, tokens)

    if args.gdocs:
        payload = plan_to_gdocs_payload(plan, contenido)
        args.salida.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Payload Google Docs escrito en: {args.salida}")
        return 0

    render_docx(plan, tokens, args.salida)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
