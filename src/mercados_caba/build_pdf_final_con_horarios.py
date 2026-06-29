"""Genera la version comparativa final con horarios documentados.

No sobrescribe la entrega final simple. Usa los insumos sanitizados existentes
de horarios y mantiene conteos, universo, estados, mapa y graficos.
"""
from __future__ import annotations

import csv
import importlib.util
import shutil
import tempfile
import zipfile
from pathlib import Path

from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "mercados_caba"
SAN = ROOT / "outputs" / "mercados_caba" / "sanitized"

ENTREGA_BUILDER = ROOT / "src" / "mercados_caba" / "build_pdf_final_entrega.py"

PDF = SAN / "MercadosGastroCABA_con_horarios.pdf"
SUMMARY = SAN / "ResumenEjecutivo_MercadosGastroCABA_con_horarios.pdf"
PACK = SAN / "PACK_MercadosGastroCABA_con_horarios.zip"
HORARIOS_CSV = SAN / "horarios_documentados_mercados_vfinal.csv"
ANEXO_HORARIOS = DOCS / "ANEXO_HORARIOS_DOCUMENTADOS_MERCADOS.md"

README_V4_1 = DOCS / "README_REGENERAR_INFORME_FINAL_V4_1.md"
OPORTUNIDAD_V4_1 = DOCS / "OPORTUNIDAD_GESTION_MERCADOS_CABA_V4_1.md"
ANEXO_METODOLOGIA_V4_1 = DOCS / "ANEXO_FUENTES_Y_METODOLOGIA_MERCADOS_V4_1.md"
OPORTUNIDADES_CSV_V4_1 = SAN / "oportunidades_gestion_mercados_v4_1.csv"
PILOTOS_CSV_V4_1 = SAN / "pilotos_recomendados_mercados_v4_1.csv"
PUBLICOS_CSV_V4_1 = SAN / "publicos_objetivo_mercados_v4_1.csv"

METODOLOGIA_HORARIOS = (
    "Los horarios se presentan como información documental de referencia. Pueden variar por "
    "temporada, operador, sede o actualización de canales públicos, por lo que requieren "
    "validación antes de su uso operativo o comunicación al público."
)

HORARIOS_ROWS = [
    {
        "mercado": "Mercado de San Telmo",
        "sede": "sede fija",
        "frecuencia_apertura": "Lunes a domingo",
        "horario_documentado": "9 a 22 (a confirmar)",
        "observacion": "Fuentes documentales divergentes; no usar como horario operativo definitivo.",
        "nivel_confianza": "parcial_fuentes_divergentes",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; GCBA/Turismo BA/sitio propio",
    },
    {
        "mercado": "Mercado de Belgrano",
        "sede": "sede fija",
        "frecuencia_apertura": "Lunes a domingo",
        "horario_documentado": "frescos 8:30-20; gastronomía 11-24",
        "observacion": "Diferencia entre rubro de frescos y oferta gastronómica.",
        "nivel_confianza": "alto_documental",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2",
    },
    {
        "mercado": "Mercado San Nicolás",
        "sede": "sede fija",
        "frecuencia_apertura": "Lunes a sábado",
        "horario_documentado": "mercado 8-18; gastronomía 11-24",
        "observacion": "Permite lectura de almuerzo laboral y franja post-laboral.",
        "nivel_confianza": "alto_documental",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; respaldo documental multifuente",
    },
    {
        "mercado": "Mercado del Progreso",
        "sede": "sede fija",
        "frecuencia_apertura": "Lunes a sábado",
        "horario_documentado": "Lun-Vie 7:30-13 y 17-20; Sáb hasta 14 y 17-20",
        "observacion": "Horario documental con posible divergencia entre fuentes; validar antes de publicar.",
        "nivel_confianza": "alto_documental_con_divergencia_a_validar",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; sitio propio",
    },
    {
        "mercado": "Mercat Villa Crespo",
        "sede": "sede fija",
        "frecuencia_apertura": "Martes a domingo",
        "horario_documentado": "12 a 23 (Vie-Sáb hasta 01)",
        "observacion": "Útil para lectura de almuerzo, tarde-noche y salida corta.",
        "nivel_confianza": "alto_documental",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; Turismo BA",
    },
    {
        "mercado": "Gourmand Food Hall",
        "sede": "sede fija",
        "frecuencia_apertura": "Todos los días",
        "horario_documentado": "Dom-Jue 10-23; Vie-Sáb 10-1",
        "observacion": "Horario documental de food hall; validar vigencia antes de comunicar.",
        "nivel_confianza": "alto_documental",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; sitio propio y validación documental multifuente",
    },
    {
        "mercado": "Patio de los Lecheros",
        "sede": "sede fija",
        "frecuencia_apertura": "Todos los días",
        "horario_documentado": "9 a 24 (Vie-Sáb hasta 3)",
        "observacion": "Operación extendida; gastronomía documentada desde las 13 en fichas previas.",
        "nivel_confianza": "alto_documental",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; GCBA",
    },
    {
        "mercado": "Smart Plaza Parque Patricios",
        "sede": "sede fija",
        "frecuencia_apertura": "Todos los días",
        "horario_documentado": "11 a 24 (Vie-Sáb hasta 1)",
        "observacion": "Permite lectura de almuerzo, tarde y salida post-laboral.",
        "nivel_confianza": "alto_documental",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; GCBA",
    },
    {
        "mercado": "Patio Costanera Norte",
        "sede": "sede fija",
        "frecuencia_apertura": "Miércoles a domingo",
        "horario_documentado": "Mié 12-19; Jue-Sáb 12-24; Dom 12-21",
        "observacion": "Horario incorporado como documental; validar antes de programación operativa.",
        "nivel_confianza": "alto_documental",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; ficha V1.2 sanitizada",
    },
    {
        "mercado": "Patio Gastronómico Rodrigo Bueno",
        "sede": "sede fija",
        "frecuencia_apertura": "Viernes a domingo",
        "horario_documentado": "11 a 23",
        "observacion": "Horario de fin de semana; validar por operador antes de publicar.",
        "nivel_confianza": "alto_documental",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; GCBA",
    },
    {
        "mercado": "Mercado Bonpland",
        "sede": "sede fija",
        "frecuencia_apertura": "Martes, miércoles, viernes y sábado",
        "horario_documentado": "10 a 19/20",
        "observacion": "Mercado de productores y economía social; días específicos.",
        "nivel_confianza": "alto_documental",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; Turismo BA",
    },
    {
        "mercado": "Sabe la Tierra",
        "sede": "itinerante",
        "frecuencia_apertura": "Fines de semana",
        "horario_documentado": "depende de sede/programación; sin horario fijo único consolidado",
        "observacion": "No asignar horario fijo único; requiere calendario de edición y sede.",
        "nivel_confianza": "por_sede_no_consolidado",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; sitio propio",
    },
    {
        "mercado": "Buenos Aires Market",
        "sede": "itinerante",
        "frecuencia_apertura": "Fines de semana",
        "horario_documentado": "depende de sede/programación; sin horario fijo único consolidado",
        "observacion": "No asignar horario fijo único; requiere calendario de edición y sede.",
        "nivel_confianza": "por_sede_no_consolidado",
        "fuente_respaldo": "horarios_mercados_gastronomicos_v3.csv; fichas sanitizadas V1/V1.2; sitio propio",
    },
]


def load_entrega_builder():
    spec = importlib.util.spec_from_file_location("mercados_entrega_builder", ENTREGA_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo importar {ENTREGA_BUILDER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def apply_final_qa_overrides(v3_module) -> None:
    fixed_cards = []
    for title, use, applies, color in v3_module.DECISION_CARDS_V2:
        if title == "Patios públicos":
            fixed_cards.append((title, "Activar patios públicos como dinamizadores barriales.", applies, color))
        else:
            fixed_cards.append((title, use, applies, color))
    v3_module.DECISION_CARDS_V2 = fixed_cards


def patch_inserted_page_footer(base_builder) -> None:
    def footer_final(fig, note: str = "") -> None:
        fig.lines.append(
            base_builder.Line2D(
                [0.07, 0.93],
                [0.056, 0.056],
                transform=fig.transFigure,
                color="#dddddd",
                lw=0.8,
            )
        )
        fig.text(
            0.07,
            0.036,
            "DataGastro · Mercados gastronómicos de CABA · Informe final",
            color=base_builder.GREY,
            fontsize=7.8,
        )
        if note:
            fig.text(0.93, 0.036, note, color=base_builder.GREY, fontsize=7.5, ha="right")

    base_builder.footer = footer_final


def write_horarios_csv() -> None:
    fieldnames = [
        "mercado",
        "sede",
        "frecuencia_apertura",
        "horario_documentado",
        "observacion",
        "nivel_confianza",
        "fuente_respaldo",
    ]
    with HORARIOS_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(HORARIOS_ROWS)


def write_anexo_horarios() -> None:
    lines = [
        "# Anexo - Horarios documentados de mercados gastronómicos CABA",
        "",
        "## Metodología",
        "",
        METODOLOGIA_HORARIOS,
        "",
        "La tabla consolida únicamente información ya presente en archivos sanitizados del proyecto, "
        "especialmente `horarios_mercados_gastronomicos_v3.csv`, `mercados_gastronomicos_activos_v4.csv` "
        "y fichas documentales V1/V1.2. No se hicieron requests, no se usaron API keys y no se inventaron horarios.",
        "",
        "Los itinerantes se mantienen sin horario fijo único: su funcionamiento depende de sede, fecha y programación.",
        "",
        "## Tabla de horarios documentados",
        "",
        "| Mercado | Sede | Frecuencia de apertura | Horario documentado | Observación | Nivel de confianza | Fuente de respaldo |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in HORARIOS_ROWS:
        lines.append(
            "| {mercado} | {sede} | {frecuencia_apertura} | {horario_documentado} | "
            "{observacion} | {nivel_confianza} | {fuente_respaldo} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Recomendación de uso",
            "",
            "Usar esta capa como referencia interna para orientar programación, priorización de validaciones "
            "y comunicación institucional. Antes de publicar horarios al público o programar acciones "
            "operativas, corresponde validarlos con el operador, la sede vigente o el canal oficial actualizado.",
        ]
    )
    ANEXO_HORARIOS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_horarios_page(v3_module, path: Path) -> None:
    with PdfPages(path) as pdf:
        fig = v3_module.page()
        v3_module.header(
            fig,
            6,
            "Frecuencia, horarios documentados y públicos objetivo",
            "Frecuencia de apertura, franjas documentadas y perfiles de público, como referencia orientativa.",
        )
        v3_module.image_fit(fig, "grafico_horarios_v5.png", 0.060, 0.790, 0.44)
        v3_module.image_fit(fig, "grafico_publicos_objetivo_v5.png", 0.590, 0.800, 0.34)
        v3_module.box(
            fig,
            0.07,
            0.455,
            0.86,
            0.120,
            "Lectura de horarios",
            "11 de 13 casos tienen horario documentado o frecuencia de apertura identificada. En sedes fijas, "
            "las franjas orientan programación; en itinerantes, dependen de sede y edición.",
        )
        examples = [
            ["San Nicolás", "Mercado 8-18; gastro 11-24; almuerzo laboral"],
            ["Belgrano", "Frescos 8:30-20; gastro 11-24; tarde/post-laboral"],
            ["Lecheros", "Horario 9-24; vie-sáb hasta 3; salida barrial"],
            ["Bonpland", "Horario 10-19/20; mar/mié/vie/sáb; productores"],
            ["Buenos Aires Market y Sabe la Tierra", "itinerantes; dependen de sede y edición"],
        ]
        v3_module.table(
            fig,
            [0.07, 0.265, 0.86, 0.150],
            examples,
            ["Mercado", "Franja documentada / lectura horaria"],
            font=7.4,
            yscale=1.25,
            col_widths=[0.40, 0.60],
        )
        v3_module.box(
            fig,
            0.07,
            0.105,
            0.86,
            0.115,
            "Cuidado metodológico",
            "Los horarios son autodeclarados o documentales y pueden cambiar por temporada, operador, sede "
            "o canal público. Requieren validación antes de publicar o programar acciones.",
            "cuid",
        )
        v3_module.footer(fig, "Horarios documentales; pueden cambiar")
        pdf.savefig(fig)
        v3_module.plt.close(fig)


def build_cierre_page(v3_module, path: Path) -> None:
    with PdfPages(path) as pdf:
        fig = v3_module.page()
        v3_module.header(
            fig,
            11,
            "Limitaciones, próximos pasos y cierre",
            "Alcances del relevamiento y próximos pasos para consolidar la base candidata.",
        )
        v3_module.box(
            fig,
            0.07,
            0.640,
            0.86,
            0.155,
            "Limitaciones",
            "Relevamiento documental y multifuente. No reemplaza la validación territorial ni el "
            "registro oficial. Google Places es señal auxiliar no oficial. Horarios autodeclarados y "
            "a veces divergentes. Coordenadas aproximadas por barrio. El respaldo documental alto o "
            "medio no equivale a confianza territorial.",
            "cuid",
        )
        fig.text(0.07, 0.600, "Próximos pasos", color=v3_module.INK, fontsize=10.5, fontweight="bold")
        v3_module.bullet_column(
            fig,
            0.085,
            0.560,
            [
                "Validar en terreno los casos de respaldo medio o a validar.",
                "Monitorear los espacios con señales de cierre (Soho, Mercat Caballito, El Galpón).",
                "Homogeneizar la información pública de horarios, gestión y oferta.",
                "Validar y mantener actualizados los horarios antes de publicarlos como información operativa.",
                "Mantener la base candidata como insumo actualizable, no como total definitivo.",
            ],
            wrap=84,
            gap=0.040,
        )
        v3_module.box(
            fig,
            0.07,
            0.135,
            0.86,
            0.155,
            "Qué aporta DataGastro",
            "Un método replicable que integra registro oficial, sitios propios, señal operativa, fuente interna "
            "y revisión documental para construir una base candidata trazable, distinguir tipologías y separar "
            "con claridad activos identificados, casos en revisión, cerrados y fuera de alcance. Es una base "
            "candidata, no oficial.",
        )
        v3_module.footer(fig, "No es censo ni padrón oficial")
        pdf.savefig(fig)
        v3_module.plt.close(fig)


def build_final_pdf(builder, base_v3: Path, new_pages: Path, horarios_page: Path, cierre_page: Path, tmp: Path) -> None:
    for src, dst in [
        (base_v3, tmp / "base_v3_1.pdf"),
        (new_pages, tmp / "new_pages_v4_1.pdf"),
        (horarios_page, tmp / "horarios_page.pdf"),
        (cierre_page, tmp / "cierre_page.pdf"),
    ]:
        if src.resolve() != dst.resolve():
            shutil.copyfile(src, dst)

    sequence = [
        ("base_v3_1.pdf", 1),
        ("base_v3_1.pdf", 2),
        ("new_pages_v4_1.pdf", 1),
        ("base_v3_1.pdf", 3),
        ("base_v3_1.pdf", 4),
        ("base_v3_1.pdf", 5),
        ("horarios_page.pdf", 1),
        ("base_v3_1.pdf", 7),
        ("base_v3_1.pdf", 8),
        ("base_v3_1.pdf", 9),
        ("base_v3_1.pdf", 10),
        ("new_pages_v4_1.pdf", 2),
        ("base_v3_1.pdf", 11),
        ("cierre_page.pdf", 1),
    ]
    pages = [builder.tex_page(source, source_page, final_page) for final_page, (source, source_page) in enumerate(sequence, start=1)]
    tex = "\n".join(
        [
            r"\documentclass[a4paper]{article}",
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage[margin=0pt]{geometry}",
            r"\usepackage{graphicx}",
            r"\usepackage{xcolor}",
            r"\usepackage{eso-pic}",
            r"\pagestyle{empty}",
            r"\setlength{\parindent}{0pt}",
            r"\begin{document}",
            *pages,
            r"\end{document}",
        ]
    )
    tex_path = tmp / "informe_con_horarios.tex"
    tex_path.write_text(tex, encoding="utf-8")
    builder.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(tmp), str(tex_path)], cwd=tmp)
    shutil.copyfile(tmp / "informe_con_horarios.pdf", PDF)


def build_pack() -> None:
    files = [
        PDF,
        SUMMARY,
        ANEXO_HORARIOS,
        HORARIOS_CSV,
        README_V4_1,
        OPORTUNIDAD_V4_1,
        ANEXO_METODOLOGIA_V4_1,
        OPORTUNIDADES_CSV_V4_1,
        PILOTOS_CSV_V4_1,
        PUBLICOS_CSV_V4_1,
    ]
    missing = [path for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError("Faltan archivos para el pack con horarios:\n" + "\n".join(map(str, missing)))
    with zipfile.ZipFile(PACK, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, path.relative_to(ROOT).as_posix())


def main() -> int:
    builder = load_entrega_builder()
    base_builder = builder.load_base_builder()
    patch_inserted_page_footer(base_builder)

    with tempfile.TemporaryDirectory(prefix="mercados_con_horarios_") as tmp_name:
        tmp = Path(tmp_name)
        v3_module = base_builder.load_v3_module()
        base_builder.patch_v3_module(v3_module, tmp)
        builder.apply_delivery_overrides(v3_module)
        apply_final_qa_overrides(v3_module)

        meta = v3_module.load_master_meta()
        v3_module.build_pdf_v2(meta)
        v3_module.build_summary_pdf_v2(meta)
        v3_module.build_pdf_v3(meta)

        new_pages = tmp / "new_pages_v4_1.pdf"
        base_builder.build_new_pages(new_pages)
        horarios_page = tmp / "horarios_page_custom.pdf"
        cierre_page = tmp / "cierre_page_custom.pdf"
        build_horarios_page(v3_module, horarios_page)
        build_cierre_page(v3_module, cierre_page)
        build_final_pdf(base_builder, v3_module.PDF_V3, new_pages, horarios_page, cierre_page, tmp)
        shutil.copyfile(v3_module.PDF_RESUMEN_V2, SUMMARY)

    write_horarios_csv()
    write_anexo_horarios()
    build_pack()
    print(f"ok: {PDF}")
    print(f"ok: {SUMMARY}")
    print(f"ok: {HORARIOS_CSV}")
    print(f"ok: {ANEXO_HORARIOS}")
    print(f"ok: {PACK}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
