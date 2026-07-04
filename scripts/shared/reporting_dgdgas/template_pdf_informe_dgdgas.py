"""DGDGAS Informes v1 — ESQUELETO de generador de informe PDF.

Plantilla reutilizable para producir un informe PDF con el sistema visual
DGDGAS. NO genera todavia un informe completo ni se integra con Cafecito o
PolosGastro: describe el flujo, arma la secuencia de componentes desde un YAML
de contenido y deja el render matplotlib como punto de extension.

Para instanciarlo en un proyecto concreto (fase futura):
  1. Preparar el YAML de contenido a partir de
     docs/datagastro_design_system/templates/template_informe_dgdgas.yaml
  2. Implementar la clase MplCanvas (backend matplotlib) siguiendo el contrato
     Canvas de report_components_dgdgas.py. La paleta y margenes ya salen de los
     tokens; reutilizar el enfoque de coordenadas relativas de los generadores
     existentes (scripts/cafecito) como referencia de layout.
  3. Guardar la salida en outputs/<proyecto>/ con un nombre de version NUEVO
     (nunca sobrescribir un final existente).

Uso previsto (una vez implementado el backend):
    python -m scripts.shared.reporting_dgdgas.template_pdf_informe_dgdgas \
        --contenido docs/<proyecto>/contenido_informe.yaml \
        --salida outputs/<proyecto>/INFORME_<PROYECTO>_V1.pdf
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .report_components_dgdgas import Components
from .style_tokens_dgdgas import Tokens


def _load_contenido(path: Path) -> dict:
    """Carga el YAML de contenido. Usa PyYAML si esta; si no, avisa claro.

    No se instalan dependencias nuevas en la v1. Si PyYAML no esta disponible,
    se documenta el requisito en lugar de fallar silenciosamente.
    """
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover - entorno sin PyYAML
        raise RuntimeError(
            "Para generar el informe se necesita PyYAML (leer el contenido). "
            "No se instala automaticamente en la v1: pedir autorizacion para "
            "agregar la dependencia o pasar el contenido ya parseado."
        ) from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def build_report_plan(contenido: dict, tokens: Tokens) -> list[dict]:
    """Traduce el contenido a una secuencia de componentes (sin renderizar).

    Devuelve la lista de specs de componentes en orden de pagina. Esta funcion
    es el corazon reutilizable: mapea el YAML a la API de Components segun las
    plantillas de pagina de DGDGAS. Un backend concreto luego dibuja cada spec.
    """
    c = Components(tokens)

    # -- Portada (P0) --------------------------------------------------------
    portada = contenido.get("portada", {})
    c.portada(
        kicker=portada.get("kicker_marca", tokens.get("meta.marca_publica")),
        titulo=portada.get("titulo", ""),
        subtitulo=portada.get("subtitulo", ""),
        descripcion=portada.get("descripcion", ""),
        datos_generales=portada.get("datos_generales", []),
        presenta=portada.get("pie_institucional", ""),
    )

    # -- Indice (P1) ---------------------------------------------------------
    indice = contenido.get("indice", {})
    c.indice(
        titulo=indice.get("titulo", "Indice"),
        subtitulo=indice.get("subtitulo", ""),
        entradas=indice.get("entradas", []),
    )

    # -- Datos generales (P2) -----------------------------------------------
    dg = contenido.get("datos_generales", {})
    if dg:
        ficha = dg.get("ficha", {})
        c.ficha_relevamiento(
            titulo=dg.get("titulo", "Datos generales"),
            filas=[[k.capitalize(), v] for k, v in ficha.items()],
        )

    # -- Preguntas / variables (P3) -----------------------------------------
    preguntas = contenido.get("preguntas", {})
    for item in preguntas.get("items", []):
        c.caja_pregunta(
            pregunta=item.get("pregunta", ""),
            tipo=item.get("tipo", "cerrada"),
            observa=item.get("observa", ""),
            nota_multi=item.get("nota_multi"),
        )

    # -- Resultados (P4/P5) --------------------------------------------------
    resultados = contenido.get("resultados", {})
    for bloque in resultados.get("bloques", []):
        visual = bloque.get("visual")
        if bloque.get("pregunta"):
            c.caja_pregunta(
                pregunta=bloque["pregunta"],
                tipo=bloque.get("tipo_pregunta", "cerrada"),
                observa=bloque.get("observa", ""),
            )
        if visual == "mapa":
            c.mapa_territorial(
                titulo=bloque.get("titulo", ""),
                leyenda=bloque.get("leyenda", []),
                nota_alcance=bloque.get("nota_alcance"),
                conceptual=bloque.get("estado") in ("preliminar", "pendiente"),
            )
        elif visual == "tabla":
            c.tabla(
                titulo=bloque.get("titulo"),
                headers=bloque.get("headers", []),
                rows=bloque.get("rows", []),
                numeric_cols=bloque.get("numeric_cols", []),
                base=bloque.get("base"), fuente=bloque.get("fuente"),
            )
        else:  # grafico por defecto
            c.grafico_barras(
                titulo=bloque.get("titulo", ""),
                items=bloque.get("items", []),
                base=bloque.get("base", ""), fuente=bloque.get("fuente", ""),
                es_multi=bloque.get("tipo_pregunta", "") == "multi",
            )
        if bloque.get("lectura"):
            c.caja_lectura(texto=bloque["lectura"])

    # -- Sintesis (P8) -------------------------------------------------------
    sintesis = contenido.get("sintesis", {})
    if sintesis:
        c.lista_puntos(
            titulo=sintesis.get("titulo", "Sintesis"),
            intro=sintesis.get("intro", ""),
            puntos=sintesis.get("puntos", []),
            nota=sintesis.get("nota"),
        )

    # -- Aspectos a considerar (P9) -----------------------------------------
    aspectos = contenido.get("aspectos", {})
    if aspectos:
        c.lista_puntos(
            titulo=aspectos.get("titulo", "Aspectos a considerar"),
            intro=aspectos.get("intro", ""),
            puntos=aspectos.get("puntos", []),
            nota=aspectos.get("nota"),
        )

    # -- Anexos (P10) --------------------------------------------------------
    anexos = contenido.get("anexos", {})
    for bloque in anexos.get("bloques", []):
        c.anexo(
            titulo=bloque.get("titulo", "Anexo"),
            intro=bloque.get("intro", ""),
            nota_prudente=bloque.get("nota_prudente"),
        )

    return c.log


def render_pdf(plan: list[dict], tokens: Tokens, salida: Path) -> None:
    """Renderiza el plan a PDF. PUNTO DE EXTENSION (aun no implementado).

    Un backend matplotlib debe implementar la clase MplCanvas (contrato Canvas)
    y recorrer ``plan`` dibujando cada componente con los tokens ya resueltos.
    Se deja como NotImplementedError para no fingir una salida en la v1.
    """
    raise NotImplementedError(
        "El backend de render PDF se implementa en la fase de aplicacion "
        f"(ver HANDOFF). Plan con {len(plan)} componentes listo para "
        f"renderizar hacia: {salida}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generador PDF DGDGAS (esqueleto).")
    parser.add_argument("--contenido", required=True, type=Path)
    parser.add_argument("--salida", required=True, type=Path)
    parser.add_argument("--plan-only", action="store_true",
                        help="Solo construir y mostrar el plan de componentes.")
    args = parser.parse_args(argv)

    tokens = Tokens.load()
    contenido = _load_contenido(args.contenido)
    plan = build_report_plan(contenido, tokens)

    if args.plan_only:
        for i, entry in enumerate(plan, 1):
            print(f"{i:>2}. {entry['component']}")
        return 0

    render_pdf(plan, tokens, args.salida)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
