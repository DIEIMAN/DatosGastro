"""Genera la version editable DOCX / Google Docs del informe Cafecito DGDGAS revision 4.

No modifica el PDF aprobado ni los datos fuente. Produce un DOCX editable, un payload JSON
para Apps Script, un Apps Script opcional y una guia de uso para Drive/Google Docs.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from textwrap import dedent
from typing import Any

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.cafecito import generar_informe_cafecito_revision_4 as rev4  # noqa: E402
from scripts.cafecito import generar_informe_datagastro_final as final  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_final import clean_text, pct  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_final_editable import fmt  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_revision_1 import (  # noqa: E402
    FRANJAS,
    number_context,
    respuestas_por_dia_franja,
)

DOCX_OUT_DIR = REPO_ROOT / "outputs" / "cafecito" / "google_docs"
DOCX_DOCS_DIR = REPO_ROOT / "docs" / "cafecito" / "google_docs"
ASSETS_DIR = DOCX_OUT_DIR / "assets"
FINAL_DIR = REPO_ROOT / "Cafesito" / "final"

DOCX_OUT = DOCX_OUT_DIR / "INFORME_CAFECITO_DGDGAS_REVISION_4_EDITABLE.docx"
DOCX_FINAL = FINAL_DIR / "INFORME_CAFECITO_DGDGAS_REVISION_4_EDITABLE.docx"
PAYLOAD_JSON = DOCX_OUT_DIR / "cafecito_google_docs_payload_revision_4.json"
APPS_SCRIPT = DOCX_DOCS_DIR / "apps_script_crear_doc_cafecito.gs"
DRIVE_GUIDE = DOCX_DOCS_DIR / "COMO_USAR_VERSION_EDITABLE_DRIVE.md"

PDF_REV = REPO_ROOT / "outputs" / "cafecito" / "INFORME_CAFECITO_DGDGAS_REVISION_4.pdf"

INK = "1F3B57"
ORANGE = "C0762B"
BLUE = "2C7FB8"
GREY = "555555"
LIGHT = "EEF2F6"
SOFT_BLUE = "EAF2F8"
SOFT_ORANGE = "FFF4E6"
WHITE = "FFFFFF"
LINE = "D5DCE3"

A4_WIDTH = 11906
A4_HEIGHT = 16838
MARGIN = 1080
CONTENT_WIDTH = A4_WIDTH - (MARGIN * 2)


def x(text: Any) -> str:
    return escape(str(text), quote=False)


def rel_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def display(label: str) -> str:
    return clean_text(label)


def percent(value: int, base: int) -> str:
    return f"{pct(value, base):.0f}%"


def filled_pages(content: dict[str, Any], numbers: dict[str, Any]) -> dict[str, Any]:
    pages = {}
    for page_key, page in content["paginas"].items():
        pages[page_key] = {key: fmt(value, numbers) for key, value in page.items()}
    return pages


@dataclass
class DocxBuilder:
    rels: list[dict[str, str]] = field(default_factory=list)
    media: list[tuple[str, Path]] = field(default_factory=list)
    next_rid: int = 2

    def add_relationship(self, rel_type: str, target: str) -> str:
        rid = f"rId{self.next_rid}"
        self.next_rid += 1
        self.rels.append({"id": rid, "type": rel_type, "target": target})
        return rid

    def add_image(self, image_path: Path, *, width_inches: float = 5.9) -> str:
        image_index = len(self.media) + 1
        name = f"image{image_index}{image_path.suffix.lower()}"
        self.media.append((name, image_path))
        return self.add_relationship(
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
            f"media/{name}",
        )

    def write(self, path: Path, body_xml: str, image_info: dict[str, dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types_xml(self.media))
            zf.writestr("_rels/.rels", package_rels_xml())
            zf.writestr("docProps/core.xml", core_xml())
            zf.writestr("docProps/app.xml", app_xml())
            zf.writestr("word/document.xml", document_xml(body_xml))
            zf.writestr("word/styles.xml", styles_xml())
            zf.writestr("word/settings.xml", settings_xml())
            zf.writestr("word/numbering.xml", numbering_xml())
            zf.writestr("word/footer1.xml", footer_xml())
            zf.writestr("word/_rels/document.xml.rels", document_rels_xml(self.rels))
            for media_name, media_path in self.media:
                zf.write(media_path, f"word/media/{media_name}")


def content_types_xml(media: list[tuple[str, Path]]) -> str:
    defaults = {
        "rels": "application/vnd.openxmlformats-package.relationships+xml",
        "xml": "application/xml",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
    }
    default_xml = "\n".join(
        f'<Default Extension="{ext}" ContentType="{ctype}"/>' for ext, ctype in defaults.items()
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
{default_xml}
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''


def package_rels_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''


def document_rels_xml(rels: list[dict[str, str]]) -> str:
    fixed = [
        {
            "id": "rId1",
            "type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles",
            "target": "styles.xml",
        },
        {
            "id": "rIdNumbering",
            "type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering",
            "target": "numbering.xml",
        },
        {
            "id": "rIdSettings",
            "type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings",
            "target": "settings.xml",
        },
        {
            "id": "rIdFooter",
            "type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer",
            "target": "footer1.xml",
        },
    ]
    all_rels = fixed + rels
    lines = [
        f'<Relationship Id="{r["id"]}" Type="{r["type"]}" Target="{x(r["target"])}"/>'
        for r in all_rels
    ]
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        + "\n".join(lines)
        + "\n</Relationships>"
    )


def core_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>Cafecito BA en tu barrio - Resultados de encuestas</dc:title>
<dc:creator>DGDGAS</dc:creator>
<cp:lastModifiedBy>DGDGAS</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">2026-06-30T00:00:00Z</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">2026-06-30T00:00:00Z</dcterms:modified>
</cp:coreProperties>'''


def app_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
<Application>Microsoft Word</Application>
<DocSecurity>0</DocSecurity>
<ScaleCrop>false</ScaleCrop>
<Company>DGDGAS</Company>
<LinksUpToDate>false</LinksUpToDate>
<SharedDoc>false</SharedDoc>
<HyperlinksChanged>false</HyperlinksChanged>
<AppVersion>16.0000</AppVersion>
</Properties>'''


def styles_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal">
<w:name w:val="Normal"/>
<w:qFormat/>
<w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="22"/><w:color w:val="222222"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Title">
<w:name w:val="Title"/>
<w:basedOn w:val="Normal"/>
<w:qFormat/>
<w:pPr><w:spacing w:before="240" w:after="220"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="44"/><w:color w:val="{INK}"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Subtitle">
<w:name w:val="Subtitle"/>
<w:basedOn w:val="Normal"/>
<w:qFormat/>
<w:pPr><w:spacing w:after="220"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:i/><w:sz w:val="25"/><w:color w:val="{GREY}"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Heading1">
<w:name w:val="Heading 1"/>
<w:basedOn w:val="Normal"/>
<w:next w:val="Normal"/>
<w:qFormat/>
<w:pPr><w:keepNext/><w:spacing w:before="420" w:after="160"/><w:outlineLvl w:val="0"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="32"/><w:color w:val="{INK}"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Heading2">
<w:name w:val="Heading 2"/>
<w:basedOn w:val="Normal"/>
<w:next w:val="Normal"/>
<w:qFormat/>
<w:pPr><w:keepNext/><w:spacing w:before="240" w:after="120"/><w:outlineLvl w:val="1"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="26"/><w:color w:val="{INK}"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="BoxTitle">
<w:name w:val="Box Title"/>
<w:basedOn w:val="Normal"/>
<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="22"/><w:color w:val="{INK}"/></w:rPr>
</w:style>
</w:styles>'''


def settings_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:zoom w:percent="100"/>
<w:defaultTabStop w:val="720"/>
</w:settings>'''


def numbering_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:abstractNum w:abstractNumId="1">
<w:multiLevelType w:val="hybridMultilevel"/>
<w:lvl w:ilvl="0">
<w:start w:val="1"/>
<w:numFmt w:val="bullet"/>
<w:lvlText w:val="•"/>
<w:lvlJc w:val="left"/>
<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:hint="default"/></w:rPr>
</w:lvl>
</w:abstractNum>
<w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>
</w:numbering>'''


def footer_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:p>
<w:pPr><w:pStyle w:val="Normal"/><w:jc w:val="left"/></w:pPr>
<w:r><w:rPr><w:sz w:val="18"/><w:color w:val="{GREY}"/></w:rPr><w:t>DGDGAS · Cafecito BA en tu barrio · Resultados de encuestas</w:t></w:r>
</w:p>
</w:ftr>'''


def document_xml(body_xml: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" mc:Ignorable="w14 wp14">
<w:body>
{body_xml}
<w:sectPr>
<w:footerReference w:type="default" r:id="rIdFooter"/>
<w:pgSz w:w="{A4_WIDTH}" w:h="{A4_HEIGHT}"/>
<w:pgMar w:top="{MARGIN}" w:right="{MARGIN}" w:bottom="{MARGIN}" w:left="{MARGIN}" w:header="720" w:footer="720" w:gutter="0"/>
<w:cols w:space="720"/>
<w:docGrid w:linePitch="360"/>
</w:sectPr>
</w:body>
</w:document>'''


def run(text: str, *, bold: bool = False, italic: bool = False, color: str | None = None, size: int | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    if size:
        props.append(f'<w:sz w:val="{size}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f"<w:r>{rpr}<w:t xml:space=\"preserve\">{x(text)}</w:t></w:r>"


def paragraph(
    text: str = "",
    *,
    style: str | None = None,
    bold: bool = False,
    italic: bool = False,
    color: str | None = None,
    size: int | None = None,
    align: str | None = None,
    before: int | None = None,
    after: int | None = None,
    shading: str | None = None,
    border_bottom: str | None = None,
    page_break_before: bool = False,
    bullet: bool = False,
) -> str:
    ppr_parts = []
    if style:
        ppr_parts.append(f'<w:pStyle w:val="{style}"/>')
    if page_break_before:
        ppr_parts.append("<w:pageBreakBefore/>")
    if bullet:
        ppr_parts.append('<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>')
    if border_bottom:
        ppr_parts.append(f'<w:pBdr><w:bottom w:val="single" w:sz="8" w:space="4" w:color="{border_bottom}"/></w:pBdr>')
    if shading:
        ppr_parts.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{shading}"/>')
    spacing = []
    if before is not None:
        spacing.append(f'w:before="{before}"')
    if after is not None:
        spacing.append(f'w:after="{after}"')
    if spacing:
        ppr_parts.append(f"<w:spacing {' '.join(spacing)}/>")
    if align:
        ppr_parts.append(f'<w:jc w:val="{align}"/>')
    ppr = f"<w:pPr>{''.join(ppr_parts)}</w:pPr>" if ppr_parts else ""
    return f"<w:p>{ppr}{run(text, bold=bold, italic=italic, color=color, size=size)}</w:p>"


def heading(text: str, level: int = 1, *, page_break_before: bool = False) -> str:
    return paragraph(text, style=f"Heading{level}", page_break_before=page_break_before)


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def cell(content: str, width: int, *, fill: str = WHITE, valign: str = "top") -> str:
    return f'''<w:tc>
<w:tcPr>
<w:tcW w:w="{width}" w:type="dxa"/>
<w:tcBorders><w:top w:val="single" w:sz="4" w:color="{LINE}"/><w:left w:val="single" w:sz="4" w:color="{LINE}"/><w:bottom w:val="single" w:sz="4" w:color="{LINE}"/><w:right w:val="single" w:sz="4" w:color="{LINE}"/></w:tcBorders>
<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>
<w:tcMar><w:top w:w="90" w:type="dxa"/><w:left w:w="120" w:type="dxa"/><w:bottom w:w="90" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar>
<w:vAlign w:val="{valign}"/>
</w:tcPr>
{content}
</w:tc>'''


def table(rows: list[list[str]], widths: list[int], *, header: bool = False) -> str:
    tr_xml = []
    total_width = sum(widths)
    for idx, row in enumerate(rows):
        fill = INK if header and idx == 0 else (LIGHT if idx % 2 else WHITE)
        cells = []
        for col_idx, value in enumerate(row):
            color = WHITE if header and idx == 0 else "222222"
            bold = header and idx == 0
            cells.append(cell(paragraph(str(value), bold=bold, color=color, after=0), widths[col_idx], fill=fill))
        tr_xml.append(f"<w:tr>{''.join(cells)}</w:tr>")
    return f'''<w:tbl>
<w:tblPr>
<w:tblW w:w="{total_width}" w:type="dxa"/>
<w:tblBorders><w:top w:val="single" w:sz="4" w:color="{LINE}"/><w:left w:val="single" w:sz="4" w:color="{LINE}"/><w:bottom w:val="single" w:sz="4" w:color="{LINE}"/><w:right w:val="single" w:sz="4" w:color="{LINE}"/><w:insideH w:val="single" w:sz="4" w:color="{LINE}"/><w:insideV w:val="single" w:sz="4" w:color="{LINE}"/></w:tblBorders>
<w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar>
</w:tblPr>
<w:tblGrid>{''.join(f'<w:gridCol w:w="{w}"/>' for w in widths)}</w:tblGrid>
{''.join(tr_xml)}
</w:tbl>'''


def box(title: str, content: str | list[str], *, fill: str = SOFT_BLUE, border: str = BLUE) -> str:
    if isinstance(content, list):
        body = paragraph(title, style="BoxTitle", after=60)
        for item in content:
            body += paragraph(str(item), bullet=True, after=60)
    else:
        body = paragraph(title, style="BoxTitle", after=60) + paragraph(content, after=60)
    return f'''<w:tbl>
<w:tblPr>
<w:tblW w:w="{CONTENT_WIDTH}" w:type="dxa"/>
<w:tblBorders><w:top w:val="single" w:sz="8" w:color="{border}"/><w:left w:val="single" w:sz="8" w:color="{border}"/><w:bottom w:val="single" w:sz="8" w:color="{border}"/><w:right w:val="single" w:sz="8" w:color="{border}"/></w:tblBorders>
</w:tblPr>
<w:tblGrid><w:gridCol w:w="{CONTENT_WIDTH}"/></w:tblGrid>
<w:tr>{cell(body, CONTENT_WIDTH, fill=fill)}</w:tr>
</w:tbl>'''


def question_box(pregunta: str, tipo: str, observa: str) -> str:
    text = f"{pregunta}\n{tipo}\n{observa}"
    content = (
        paragraph(pregunta, style="BoxTitle", after=40)
        + paragraph(tipo, after=40)
        + paragraph(observa, after=40)
    )
    return f'''<w:tbl>
<w:tblPr><w:tblW w:w="{CONTENT_WIDTH}" w:type="dxa"/><w:tblBorders><w:top w:val="single" w:sz="8" w:color="{BLUE}"/><w:left w:val="single" w:sz="8" w:color="{BLUE}"/><w:bottom w:val="single" w:sz="8" w:color="{BLUE}"/><w:right w:val="single" w:sz="8" w:color="{BLUE}"/></w:tblBorders></w:tblPr>
<w:tblGrid><w:gridCol w:w="{CONTENT_WIDTH}"/></w:tblGrid>
<w:tr>{cell(content, CONTENT_WIDTH, fill=SOFT_BLUE)}</w:tr>
</w:tbl>'''


def image_paragraph(rid: str, width_px: int, height_px: int, title: str) -> str:
    cx = int(width_px * 9525)
    cy = int(height_px * 9525)
    docpr_id = abs(hash(rid)) % 100000
    return f'''<w:p>
<w:pPr><w:spacing w:before="120" w:after="120"/><w:jc w:val="center"/></w:pPr>
<w:r>
<w:drawing>
<wp:inline distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="{cx}" cy="{cy}"/>
<wp:docPr id="{docpr_id}" name="{x(title)}" descr="{x(title)}"/>
<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>
<a:graphic>
<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic>
<pic:nvPicPr><pic:cNvPr id="0" name="{x(title)}"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
</pic:pic>
</a:graphicData>
</a:graphic>
</wp:inline>
</w:drawing>
</w:r>
</w:p>'''


def scaled_image(builder: DocxBuilder, path: Path, title: str, *, width_inches: float = 6.2) -> str:
    rid = builder.add_image(path, width_inches=width_inches)
    with Image.open(path) as img:
        w_px, h_px = img.size
    target_px_w = int(width_inches * 96)
    target_px_h = max(1, int(target_px_w * h_px / w_px))
    return paragraph(title, bold=True, color=INK, size=24, before=160, after=60) + image_paragraph(
        rid, target_px_w, target_px_h, title
    )


def stat_table(title: str, items: list[tuple[str, int]], base: int, *, multi: bool = False, limit: int | None = None) -> str:
    chosen = items[:limit] if limit else items
    if multi:
        headers = ["Opción", "Menciones", "% sobre base"]
    else:
        headers = ["Categoría", "Respuestas", "%"]
    rows = [headers]
    for label, value in chosen:
        rows.append([display(label), str(value), percent(value, base)])
    note = (
        f"Base: {base} respuestas. Pregunta multi-respuesta: se muestran menciones por opcion."
        if multi
        else f"Base: {base} respuestas."
    )
    return (
        paragraph(title, bold=True, color=INK, size=24, before=180, after=80)
        + table(rows, [5400, 1800, 1800], header=True)
        + paragraph(note, italic=True, color=GREY, size=18, after=120)
    )


def make_fact_table(inst: dict[str, str], ev: dict[str, str], n_total: int) -> list[list[str]]:
    return [
        ["Etiqueta", "Contenido"],
        ["Evento", ev["nombre"]],
        ["Lugar", ev["lugar"]],
        ["Dirección", ev["direccion"]],
        ["Fechas", f'{ev["fecha_sabado"]}\n{ev["fecha_domingo"]}'],
        ["Respuestas obtenidas", str(n_total)],
        ["Modalidad", "Encuesta en formulario digital"],
        ["Presenta", f'{inst["sigla"]} – {inst["nombre"]}'],
    ]


def make_payload(
    content: dict[str, Any],
    pages: dict[str, Any],
    stats: dict[str, Any],
    p: dict[str, Any],
    filas: list[dict[str, Any]],
    barrios: tuple[list[tuple[str, int, float]], int, int] | None,
    sedes_comuna: list[dict[str, str]],
    assets: list[dict[str, str]],
) -> dict[str, Any]:
    inst = content["institucion"]
    ev = content["evento"]

    def rows_for(key: str, *, multi: bool = False, limit: int | None = None) -> dict[str, Any]:
        items = stats[key]["items"][:limit] if limit else stats[key]["items"]
        return {
            "base": stats[key]["base"],
            "multiResponse": multi,
            "rows": [
                {"label": display(label), "count": value, "percent": percent(value, stats[key]["base"])}
                for label, value in items
            ],
        }

    sections = [
        {
            "number": "1",
            "title": pages["datos_generales"]["titulo"].split(". ", 1)[1],
            "page": 3,
            "subtitle": pages["datos_generales"]["subtitulo"],
            "blocks": [
                {"type": "facts", "rows": make_fact_table(inst, ev, p["n"])[1:]},
                {"type": "paragraph", "text": pages["datos_generales"]["modalidad_texto"]},
                {
                    "type": "table",
                    "title": pages["datos_generales"]["distribucion_titulo"],
                    "intro": pages["datos_generales"]["distribucion_intro"],
                    "headers": ["Dia", *FRANJAS, "Total"],
                    "rows": [
                        [fila["dia"], *[fila["franjas"][franja] for franja in FRANJAS], fila["total"]]
                        for fila in filas
                    ],
                },
            ],
        },
        {
            "number": "2",
            "title": pages["preguntas"]["titulo"].split(". ", 1)[1],
            "page": 4,
            "subtitle": pages["preguntas"]["subtitulo"],
            "blocks": [
                {"type": "paragraph", "text": pages["preguntas"]["intro"]},
                {"type": "questions", "items": rev4.PREGUNTAS_FORMULARIO},
                {"type": "note", "text": pages["preguntas"]["nota_pie"]},
            ],
        },
        {
            "number": "3",
            "title": pages["perfil"]["titulo"].split(". ", 1)[1],
            "page": 5,
            "subtitle": pages["perfil"]["subtitulo"],
            "blocks": [
                {"type": "question", "text": pages["perfil"]["pregunta_edad"], "kind": pages["perfil"]["tipo_edad"], "observes": pages["perfil"]["observa_edad"]},
                {"type": "resultTable", "title": "Rango de edad", **rows_for("rango_edad")},
                {"type": "question", "text": pages["perfil"]["pregunta_genero"], "kind": pages["perfil"]["tipo_genero"], "observes": pages["perfil"]["observa_genero"]},
                {"type": "resultTable", "title": "Género declarado", **rows_for("genero")},
                {"type": "reading", "text": pages["perfil"]["lectura"]},
            ],
        },
        {
            "number": "4",
            "title": pages["residencia"]["titulo"].split(". ", 1)[1],
            "page": 6,
            "subtitle": pages["residencia"]["subtitulo"],
            "blocks": [
                {"type": "question", "text": pages["residencia"]["pregunta_a"], "kind": pages["residencia"]["tipo_a"], "observes": pages["residencia"]["observa"]},
                {"type": "question", "text": pages["residencia"]["pregunta_b"], "kind": pages["residencia"]["tipo_b"], "observes": pages["residencia"]["observa"]},
                {"type": "resultTable", "title": pages["residencia"]["macro_titulo"], **rows_for("donde_vivis")},
                {
                    "type": "resultTable",
                    "title": pages["residencia"]["barrios_titulo"],
                    "base": barrios[1] if barrios else 0,
                    "multiResponse": False,
                    "rows": [
                        {"label": name, "count": value, "percent": f"{share:.0f}%"}
                        for name, value, share in (barrios[0] if barrios else [])
                    ]
                    + ([{"label": "Otras respuestas", "count": barrios[2], "percent": f"{pct(barrios[2], barrios[1]):.0f}%"}] if barrios else []),
                },
                {"type": "reading", "text": pages["residencia"]["lectura"]},
            ],
        },
        {
            "number": "5",
            "title": pages["vinculo"]["titulo"].split(". ", 1)[1],
            "page": 7,
            "subtitle": pages["vinculo"]["subtitulo"],
            "blocks": [
                {"type": "question", "text": pages["vinculo"]["pregunta_primera"], "kind": pages["vinculo"]["tipo_primera"], "observes": pages["vinculo"]["observa_primera"]},
                {"type": "resultTable", "title": "Primera vez o participación previa", **rows_for("primera_vez")},
                {"type": "question", "text": pages["vinculo"]["pregunta_contacto"], "kind": pages["vinculo"]["tipo_contacto"], "observes": pages["vinculo"]["observa_contacto"]},
                {"type": "resultTable", "title": "Acepta recibir informacion", **rows_for("acepta_contacto")},
                {"type": "reading", "text": pages["vinculo"]["lectura"]},
            ],
        },
        {
            "number": "6",
            "title": pages["canales"]["titulo"].split(". ", 1)[1],
            "page": 8,
            "subtitle": pages["canales"]["subtitulo"],
            "blocks": [
                {"type": "question", "text": pages["canales"]["pregunta"], "kind": pages["canales"]["tipo"], "observes": pages["canales"]["observa"]},
                {"type": "note", "text": pages["canales"]["nota_multi"]},
                {"type": "resultTable", "title": "Cómo se enteraron del evento", **rows_for("como_se_entero", multi=True)},
                {"type": "reading", "text": pages["canales"]["lectura"]},
            ],
        },
        {
            "number": "7",
            "title": pages["acompanamiento"]["titulo"].split(". ", 1)[1],
            "page": 9,
            "subtitle": pages["acompanamiento"]["subtitulo"],
            "blocks": [
                {"type": "question", "text": pages["acompanamiento"]["pregunta_con_quien"], "kind": pages["acompanamiento"]["tipo_con_quien"], "observes": pages["acompanamiento"]["observa_con_quien"]},
                {"type": "resultTable", "title": "Con quien asistio al evento", **rows_for("con_quien")},
                {"type": "reading", "text": pages["acompanamiento"]["lectura"]},
            ],
        },
        {
            "number": "8",
            "title": pages["motivaciones"]["titulo"].split(". ", 1)[1],
            "page": 10,
            "subtitle": pages["motivaciones"]["subtitulo"],
            "blocks": [
                {"type": "question", "text": pages["motivaciones"]["pregunta_intereso"], "kind": pages["motivaciones"]["tipo_intereso"], "observes": pages["motivaciones"]["observa_intereso"]},
                {"type": "resultTable", "title": "Qué fue lo que más le interesó", **rows_for("que_intereso")},
                {"type": "reading", "text": pages["motivaciones"]["lectura"]},
            ],
        },
        {
            "number": "9",
            "title": pages["intereses"]["titulo"].split(". ", 1)[1],
            "page": 11,
            "subtitle": pages["intereses"]["subtitulo"],
            "blocks": [
                {"type": "question", "text": pages["intereses"]["pregunta"], "kind": pages["intereses"]["tipo"], "observes": pages["intereses"]["observa"]},
                {"type": "note", "text": pages["intereses"]["nota_multi"]},
                {"type": "resultTable", "title": "Intereses para próximas ediciones", **rows_for("eventos_futuros", multi=True, limit=8)},
                {"type": "reading", "text": pages["intereses"]["lectura"]},
            ],
        },
        {
            "number": "10",
            "title": pages["sintesis"]["titulo"].split(". ", 1)[1],
            "page": 12,
            "subtitle": pages["sintesis"]["subtitulo"],
            "blocks": [
                {"type": "paragraph", "text": pages["sintesis"]["intro"]},
                {"type": "bullets", "items": pages["sintesis"]["puntos"]},
                {"type": "note", "text": pages["sintesis"]["nota"]},
            ],
        },
        {
            "number": "11",
            "title": pages["aspectos"]["titulo"].split(". ", 1)[1],
            "page": 13,
            "subtitle": pages["aspectos"]["subtitulo"],
            "blocks": [
                {"type": "paragraph", "text": pages["aspectos"]["intro"]},
                {"type": "bullets", "items": pages["aspectos"]["puntos"]},
                {"type": "note", "text": pages["aspectos"]["nota"]},
            ],
        },
        {
            "number": "12",
            "title": pages["anexo_red"]["titulo"].split(". ", 1)[1],
            "page": 14,
            "subtitle": pages["anexo_red"]["subtitulo"],
            "blocks": [
                {"type": "paragraph", "text": pages["anexo_red"]["intro"]},
                *[
                    {
                        "type": "image",
                        "title": asset["title"],
                        "imagePath": asset["imagePath"],
                        "imageName": asset["imageName"],
                        "driveFileIdPlaceholder": asset["driveFileIdPlaceholder"],
                    }
                    for asset in assets
                ],
                {"type": "bullets", "title": pages["anexo_red"]["en_numeros_titulo"], "items": pages["anexo_red"]["en_numeros"]},
                {"type": "table", "title": "Comunas con más sedes", "headers": ["Comuna", "Sedes"], "rows": [[r["comuna"], r["cantidad_sedes"]] for r in sedes_comuna if str(r.get("comuna", "")).isdigit()][:5]},
                {"type": "note", "text": pages["anexo_red"]["nota_prudente"]},
            ],
        },
    ]

    return {
        "meta": {
            "title": pages["portada"]["titulo"].replace("\n", " "),
            "subtitle": pages["portada"]["subtitulo"],
            "presenta": f'{inst["sigla"]} – {inst["nombre"]}',
            "footer": content["footer"],
            "version": "REVISION_4_EDITABLE",
        },
        "cover": {
            "intro": pages["portada"]["descripcion"],
            "facts": [
                ["Evento", ev["nombre"]],
                ["Lugar", ev["lugar"]],
                ["Dirección", ev["direccion"]],
                ["Fechas", f'{ev["fecha_sabado"]}\n{ev["fecha_domingo"]}'],
                ["Presenta", f'{inst["sigla"]} – {inst["nombre"]}'],
            ],
        },
        "index": pages["indice"]["entradas"],
        "sections": sections,
        "assets": assets,
    }


def build_docx(
    content: dict[str, Any],
    pages: dict[str, Any],
    stats: dict[str, Any],
    p: dict[str, Any],
    filas: list[dict[str, Any]],
    barrios: tuple[list[tuple[str, int, float]], int, int] | None,
    sedes_comuna: list[dict[str, str]],
    asset_paths: dict[str, Path],
) -> None:
    inst = content["institucion"]
    ev = content["evento"]
    builder = DocxBuilder()
    body = []

    body.append(paragraph(pages["portada"]["kicker_marca"], bold=True, color=ORANGE, size=22, after=180))
    body.append(paragraph(pages["portada"]["titulo"].replace("\n", " "), style="Title", after=100))
    body.append(paragraph(pages["portada"]["subtitulo"], style="Subtitle", after=260))
    body.append(paragraph(pages["portada"]["descripcion"], size=23, after=260))
    body.append(table(make_fact_table(inst, ev, p["n"]), [2600, 6400], header=True))
    body.append(paragraph(f'{inst["sigla"]} – {inst["nombre"]}', bold=True, color=INK, size=22, before=260))
    body.append(page_break())

    body.append(heading("Índice", 1))
    index_rows = [["Seccion", "Titulo", "Pagina PDF"]]
    for item in pages["indice"]["entradas"]:
        index_rows.append([item.get("num", ""), item.get("texto", ""), item.get("pagina", "")])
    body.append(table(index_rows, [1300, 6100, 1600], header=True))
    body.append(paragraph("Los numeros de pagina corresponden al PDF aprobado. En Google Docs pueden cambiar segun el entorno de edicion.", italic=True, color=GREY, size=18))
    body.append(page_break())

    body.append(heading(pages["datos_generales"]["titulo"], 1))
    body.append(paragraph(pages["datos_generales"]["subtitulo"], style="Subtitle"))
    body.append(box(pages["datos_generales"]["ficha_titulo"], ""))
    body.append(table(make_fact_table(inst, ev, p["n"]), [2600, 6400], header=True))
    body.append(paragraph(pages["datos_generales"]["modalidad_texto"]))
    body.append(heading(pages["datos_generales"]["distribucion_titulo"], 2))
    body.append(paragraph(pages["datos_generales"]["distribucion_intro"]))
    franja_rows = [["Dia", *FRANJAS, "Total"]]
    for fila in filas:
        franja_rows.append([fila["dia"], *[str(fila["franjas"][franja]) for franja in FRANJAS], str(fila["total"])])
    body.append(table(franja_rows, [1900, 1900, 2100, 1900, 1200], header=True))
    body.append(page_break())

    body.append(heading(pages["preguntas"]["titulo"], 1))
    body.append(paragraph(pages["preguntas"]["subtitulo"], style="Subtitle"))
    body.append(paragraph(pages["preguntas"]["intro"]))
    pregunta_rows = [["N", "Pregunta", "Tipo", "Objetivo"]]
    for idx, question in enumerate(rev4.PREGUNTAS_FORMULARIO, 1):
        pregunta_rows.append([str(idx), question["pregunta"], question["tipo"], question["objetivo"]])
    body.append(table(pregunta_rows, [600, 3000, 1900, 3500], header=True))
    body.append(paragraph(pages["preguntas"]["nota_pie"], italic=True, color=GREY, size=18))
    body.append(page_break())

    body.append(heading(pages["perfil"]["titulo"], 1))
    body.append(paragraph(pages["perfil"]["subtitulo"], style="Subtitle"))
    body.append(question_box(pages["perfil"]["pregunta_edad"], pages["perfil"]["tipo_edad"], pages["perfil"]["observa_edad"]))
    body.append(stat_table("Rango de edad", stats["rango_edad"]["items"], stats["rango_edad"]["base"]))
    body.append(question_box(pages["perfil"]["pregunta_genero"], pages["perfil"]["tipo_genero"], pages["perfil"]["observa_genero"]))
    body.append(stat_table("Género declarado", stats["genero"]["items"], stats["genero"]["base"]))
    body.append(box("Lectura de resultados", pages["perfil"]["lectura"]))
    body.append(page_break())

    body.append(heading(pages["residencia"]["titulo"], 1))
    body.append(paragraph(pages["residencia"]["subtitulo"], style="Subtitle"))
    body.append(question_box(pages["residencia"]["pregunta_a"], pages["residencia"]["tipo_a"], pages["residencia"]["observa"]))
    body.append(stat_table(pages["residencia"]["macro_titulo"], stats["donde_vivis"]["items"], stats["donde_vivis"]["base"]))
    body.append(question_box(pages["residencia"]["pregunta_b"], pages["residencia"]["tipo_b"], pages["residencia"]["observa"]))
    if barrios:
        filas_b, total_b, otras_b = barrios
        barrio_rows = [["Barrio/localidad", "Respuestas", "%"]]
        for name, count, share in filas_b:
            barrio_rows.append([name, str(count), f"{share:.0f}%"])
        barrio_rows.append(["Otras respuestas", str(otras_b), f"{pct(otras_b, total_b):.0f}%"])
        body.append(paragraph(pages["residencia"]["barrios_titulo"], bold=True, color=INK, size=24, before=180, after=80))
        body.append(paragraph(pages["residencia"]["barrios_fuente"], italic=True, color=GREY, size=18))
        body.append(table(barrio_rows, [5400, 1800, 1800], header=True))
        body.append(paragraph(pages["residencia"]["barrios_nota"], italic=True, color=GREY, size=18))
    body.append(box("Lectura de resultados", pages["residencia"]["lectura"]))
    body.append(page_break())

    body.append(heading(pages["vinculo"]["titulo"], 1))
    body.append(paragraph(pages["vinculo"]["subtitulo"], style="Subtitle"))
    body.append(question_box(pages["vinculo"]["pregunta_primera"], pages["vinculo"]["tipo_primera"], pages["vinculo"]["observa_primera"]))
    body.append(stat_table("Primera vez o participación previa", stats["primera_vez"]["items"], stats["primera_vez"]["base"]))
    body.append(question_box(pages["vinculo"]["pregunta_contacto"], pages["vinculo"]["tipo_contacto"], pages["vinculo"]["observa_contacto"]))
    body.append(stat_table("Acepta recibir informacion", stats["acepta_contacto"]["items"], stats["acepta_contacto"]["base"]))
    body.append(box("Lectura de resultados", pages["vinculo"]["lectura"]))
    body.append(page_break())

    body.append(heading(pages["canales"]["titulo"], 1))
    body.append(paragraph(pages["canales"]["subtitulo"], style="Subtitle"))
    body.append(question_box(pages["canales"]["pregunta"], pages["canales"]["tipo"], pages["canales"]["observa"]))
    body.append(paragraph(pages["canales"]["nota_multi"], italic=True, color=GREY, size=19))
    body.append(stat_table("Cómo se enteraron del evento", stats["como_se_entero"]["items"], stats["como_se_entero"]["base"], multi=True))
    body.append(box("Lectura de resultados", pages["canales"]["lectura"]))
    body.append(page_break())

    body.append(heading(pages["acompanamiento"]["titulo"], 1))
    body.append(paragraph(pages["acompanamiento"]["subtitulo"], style="Subtitle"))
    body.append(question_box(pages["acompanamiento"]["pregunta_con_quien"], pages["acompanamiento"]["tipo_con_quien"], pages["acompanamiento"]["observa_con_quien"]))
    body.append(stat_table("Con quien asistio al evento", stats["con_quien"]["items"], stats["con_quien"]["base"]))
    body.append(box("Lectura de resultados", pages["acompanamiento"]["lectura"]))
    body.append(page_break())

    body.append(heading(pages["motivaciones"]["titulo"], 1))
    body.append(paragraph(pages["motivaciones"]["subtitulo"], style="Subtitle"))
    body.append(question_box(pages["motivaciones"]["pregunta_intereso"], pages["motivaciones"]["tipo_intereso"], pages["motivaciones"]["observa_intereso"]))
    body.append(stat_table("Qué fue lo que más le interesó", stats["que_intereso"]["items"], stats["que_intereso"]["base"]))
    body.append(box("Lectura de resultados", pages["motivaciones"]["lectura"]))
    body.append(page_break())

    body.append(heading(pages["intereses"]["titulo"], 1))
    body.append(paragraph(pages["intereses"]["subtitulo"], style="Subtitle"))
    body.append(question_box(pages["intereses"]["pregunta"], pages["intereses"]["tipo"], pages["intereses"]["observa"]))
    body.append(paragraph(pages["intereses"]["nota_multi"], italic=True, color=GREY, size=19))
    body.append(stat_table("Intereses para próximas ediciones", stats["eventos_futuros"]["items"], stats["eventos_futuros"]["base"], multi=True, limit=8))
    body.append(box("Lectura de resultados", pages["intereses"]["lectura"]))
    body.append(page_break())

    body.append(heading(pages["sintesis"]["titulo"], 1))
    body.append(paragraph(pages["sintesis"]["subtitulo"], style="Subtitle"))
    body.append(paragraph(pages["sintesis"]["intro"]))
    for item in pages["sintesis"]["puntos"]:
        body.append(paragraph(item, bullet=True))
    body.append(box("Sobre estos resultados", pages["sintesis"]["nota"], fill=LIGHT, border=GREY))
    body.append(page_break())

    body.append(heading(pages["aspectos"]["titulo"], 1))
    body.append(paragraph(pages["aspectos"]["subtitulo"], style="Subtitle"))
    body.append(paragraph(pages["aspectos"]["intro"]))
    for item in pages["aspectos"]["puntos"]:
        body.append(paragraph(item, bullet=True))
    body.append(box("Alcance de estas consideraciones", pages["aspectos"]["nota"], fill=SOFT_ORANGE, border=ORANGE))
    body.append(page_break())

    body.append(heading(pages["anexo_red"]["titulo"], 1))
    body.append(paragraph(pages["anexo_red"]["subtitulo"], style="Subtitle"))
    body.append(paragraph(pages["anexo_red"]["intro"]))
    for title, path in asset_paths.items():
        body.append(scaled_image(builder, path, title, width_inches=6.1))
    body.append(box(pages["anexo_red"]["en_numeros_titulo"], pages["anexo_red"]["en_numeros"], fill=WHITE, border=BLUE))
    sedes_rows = [["Comuna", "Sedes"]]
    for row in [r for r in sedes_comuna if str(r.get("comuna", "")).isdigit()][:5]:
        sedes_rows.append([f'Comuna {row["comuna"]}', str(row["cantidad_sedes"])])
    body.append(paragraph("Comunas con más sedes", bold=True, color=INK, size=24, before=180, after=80))
    body.append(table(sedes_rows, [5400, 3600], header=True))
    body.append(box("Nota sobre esta lectura", pages["anexo_red"]["nota_prudente"], fill=SOFT_ORANGE, border=ORANGE))

    builder.write(DOCX_OUT, "\n".join(body), {})
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DOCX_OUT, DOCX_FINAL)


def copy_assets() -> list[dict[str, str]]:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    assets = [
        {
            "title": "Sedes de cafeterias vinculadas en CABA",
            "source": final.MAPA_SEDES,
            "imageName": "mapa_sedes_cafeterias_revision_4.png",
            "driveFileIdPlaceholder": "PEGAR_ID_DRIVE_MAPA_SEDES",
        },
        {
            "title": "Sedes de cafeterias y respuestas por comuna",
            "source": final.MAPA_COMBINADO,
            "imageName": "mapa_cafeterias_y_publico_revision_4.png",
            "driveFileIdPlaceholder": "PEGAR_ID_DRIVE_MAPA_COMBINADO",
        },
    ]
    copied = []
    for asset in assets:
        src = Path(asset["source"])
        if not src.exists():
            continue
        dst = ASSETS_DIR / asset["imageName"]
        shutil.copy2(src, dst)
        copied.append(
            {
                "title": asset["title"],
                "imagePath": f"assets/{asset['imageName']}",
                "imageName": asset["imageName"],
                "driveFileIdPlaceholder": asset["driveFileIdPlaceholder"],
            }
        )
    return copied


def write_payload(payload: dict[str, Any]) -> None:
    PAYLOAD_JSON.parent.mkdir(parents=True, exist_ok=True)
    PAYLOAD_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_apps_script() -> None:
    APPS_SCRIPT.parent.mkdir(parents=True, exist_ok=True)
    APPS_SCRIPT.write_text(
        dedent(
            r'''
            /**
             * Crea un Google Doc editable del informe Cafecito BA en tu barrio a partir
             * del payload JSON. Completar PAYLOAD_JSON_FILE_ID con el ID del archivo JSON
             * subido a Drive.
             */
            const PAYLOAD_JSON_FILE_ID = 'PEGAR_ID_DEL_JSON_EN_DRIVE';

            const COLORS = {
              ink: '#1f3b57',
              orange: '#c0762b',
              blue: '#2c7fb8',
              grey: '#555555',
              light: '#eef2f6',
              softBlue: '#eaf2f8',
              softOrange: '#fff4e6'
            };

            function crearInformeCafecitoDesdePayload() {
              const payload = leerPayload_();
              const doc = DocumentApp.create(payload.meta.title + ' - editable');
              const body = doc.getBody();
              body.clear();

              configurarDocumento_(body);
              agregarPortada_(body, payload);
              body.appendPageBreak();
              agregarIndice_(body, payload.index || []);
              body.appendPageBreak();
              (payload.sections || []).forEach((section, index) => {
                agregarSeccion_(body, section);
                if (index < payload.sections.length - 1) body.appendPageBreak();
              });

              const footer = doc.addFooter();
              footer.appendParagraph(payload.meta.footer || 'DGDGAS · Cafecito BA en tu barrio · Resultados de encuestas')
                .setForegroundColor(COLORS.grey)
                .setFontSize(8);

              doc.saveAndClose();
              Logger.log('Documento creado: ' + doc.getUrl());
            }

            function leerPayload_() {
              const file = DriveApp.getFileById(PAYLOAD_JSON_FILE_ID);
              return JSON.parse(file.getBlob().getDataAsString('UTF-8'));
            }

            function configurarDocumento_(body) {
              body.setMarginTop(54);
              body.setMarginBottom(54);
              body.setMarginLeft(54);
              body.setMarginRight(54);
              body.setAttributes({
                [DocumentApp.Attribute.FONT_FAMILY]: 'Arial',
                [DocumentApp.Attribute.FONT_SIZE]: 11,
                [DocumentApp.Attribute.FOREGROUND_COLOR]: '#222222'
              });
            }

            function agregarPortada_(body, payload) {
              agregarTexto_(body, payload.meta.presenta, 12, true, COLORS.orange);
              agregarTexto_(body, payload.meta.title, 28, true, COLORS.ink);
              agregarTexto_(body, payload.meta.subtitle, 14, false, COLORS.grey).setItalic(true);
              body.appendParagraph(payload.cover.intro || '').setSpacingAfter(12);
              agregarTablaSimple_(body, [['Etiqueta', 'Contenido']].concat(payload.cover.facts || []), true);
            }

            function agregarIndice_(body, entries) {
              agregarTexto_(body, 'Índice', 22, true, COLORS.ink);
              const rows = [['Seccion', 'Titulo', 'Pagina PDF']];
              entries.forEach(e => rows.push([e.num || '', e.texto || '', e.pagina || '']));
              agregarTablaSimple_(body, rows, true);
              body.appendParagraph('Los numeros de pagina corresponden al PDF aprobado; pueden cambiar al editar en Google Docs.')
                .setItalic(true)
                .setForegroundColor(COLORS.grey)
                .setFontSize(9);
            }

            function agregarSeccion_(body, section) {
              agregarTexto_(body, section.number + '. ' + section.title, 20, true, COLORS.ink);
              if (section.subtitle) agregarTexto_(body, section.subtitle, 12, false, COLORS.grey).setItalic(true);
              (section.blocks || []).forEach(block => agregarBloque_(body, block));
            }

            function agregarBloque_(body, block) {
              if (block.type === 'paragraph') {
                body.appendParagraph(block.text || '');
              } else if (block.type === 'note') {
                agregarCaja_(body, 'Nota', block.text || '', COLORS.softOrange);
              } else if (block.type === 'reading') {
                agregarCaja_(body, 'Lectura de resultados', block.text || '', COLORS.softBlue);
              } else if (block.type === 'facts') {
                agregarCaja_(body, 'Ficha del relevamiento', '', COLORS.softBlue);
                agregarTablaSimple_(body, [['Etiqueta', 'Contenido']].concat(block.rows || []), true);
              } else if (block.type === 'questions') {
                const rows = [['N', 'Pregunta', 'Tipo', 'Objetivo']];
                (block.items || []).forEach((q, i) => rows.push([String(i + 1), q.pregunta, q.tipo, q.objetivo]));
                agregarTablaSimple_(body, rows, true);
              } else if (block.type === 'question') {
                agregarCaja_(body, block.text || 'Pregunta analizada', [block.kind, block.observes].filter(Boolean).join('\n'), COLORS.softBlue);
              } else if (block.type === 'resultTable') {
                agregarTexto_(body, block.title || 'Resultados', 13, true, COLORS.ink);
                const rows = [[block.multiResponse ? 'Opción' : 'Categoría', block.multiResponse ? 'Menciones' : 'Respuestas', '%']];
                (block.rows || []).forEach(r => rows.push([r.label, String(r.count), r.percent]));
                agregarTablaSimple_(body, rows, true);
                const base = block.multiResponse
                  ? 'Base: ' + block.base + ' respuestas. Pregunta multi-respuesta: se muestran menciones por opcion.'
                  : 'Base: ' + block.base + ' respuestas.';
                body.appendParagraph(base).setItalic(true).setForegroundColor(COLORS.grey).setFontSize(9);
              } else if (block.type === 'table') {
                if (block.title) agregarTexto_(body, block.title, 13, true, COLORS.ink);
                if (block.intro) body.appendParagraph(block.intro);
                agregarTablaSimple_(body, [block.headers || []].concat(block.rows || []), true);
              } else if (block.type === 'bullets') {
                if (block.title) agregarTexto_(body, block.title, 13, true, COLORS.ink);
                (block.items || []).forEach(item => body.appendListItem(item).setGlyphType(DocumentApp.GlyphType.BULLET));
              } else if (block.type === 'image') {
                agregarImagenOpcional_(body, block);
              }
            }

            function agregarImagenOpcional_(body, block) {
              agregarTexto_(body, block.title || 'Imagen', 13, true, COLORS.ink);
              const id = block.driveFileId || block.driveFileIdPlaceholder || '';
              if (id && !/^PEGAR_/.test(id)) {
                const blob = DriveApp.getFileById(id).getBlob();
                const image = body.appendImage(blob);
                image.setWidth(520);
              } else {
                body.appendParagraph('Imagen pendiente: subir ' + (block.imageName || block.imagePath || 'archivo') + ' a Drive y completar driveFileId.')
                  .setItalic(true)
                  .setForegroundColor(COLORS.grey)
                  .setFontSize(9);
              }
            }

            function agregarCaja_(body, title, text, color) {
              const table = body.appendTable([[title], [text || '']]);
              table.setBorderColor(COLORS.blue);
              table.getRow(0).getCell(0).setBackgroundColor(color);
              table.getRow(0).getCell(0).editAsText().setBold(true).setForegroundColor(COLORS.ink);
              table.getRow(1).getCell(0).setBackgroundColor(color);
            }

            function agregarTablaSimple_(body, rows, header) {
              const table = body.appendTable(rows);
              table.setBorderColor('#d5dce3');
              if (header && table.getNumRows() > 0) {
                const row = table.getRow(0);
                for (let i = 0; i < row.getNumCells(); i++) {
                  row.getCell(i).setBackgroundColor(COLORS.ink);
                  row.getCell(i).editAsText().setBold(true).setForegroundColor('#ffffff');
                }
              }
              return table;
            }

            function agregarTexto_(body, text, size, bold, color) {
              const p = body.appendParagraph(text || '');
              p.setFontSize(size);
              p.setBold(!!bold);
              p.setForegroundColor(color || '#222222');
              return p;
            }
            '''
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def write_drive_guide() -> None:
    DRIVE_GUIDE.parent.mkdir(parents=True, exist_ok=True)
    DRIVE_GUIDE.write_text(
        dedent(
            """
            # Como usar la version editable en Google Drive

            Esta version editable acompana al PDF aprobado de Cafecito BA en tu barrio. Sirve para abrir el informe como Google Docs y recibir comentarios. No reemplaza al YAML ni al generador como fuente de verdad.

            ## DOCX editable

            1. Subir `INFORME_CAFECITO_DGDGAS_REVISION_4_EDITABLE.docx` a Google Drive.
            2. Abrir el archivo con Google Docs.
            3. Revisar visualmente portada, indice, tablas, imagenes y saltos de pagina.
            4. Usar el documento para comentarios y sugerencias de texto.
            5. Si hay cambios de redaccion aprobados, trasladarlos luego al YAML de revision 4.
            6. Si hay cambios de datos, calculos o graficos, corregir el generador correspondiente y volver a producir los outputs.
            7. No editar el PDF aprobado a mano.

            ## Apps Script opcional

            1. Subir `cafecito_google_docs_payload_revision_4.json` a Google Drive.
            2. Copiar el ID del archivo JSON desde la URL de Drive.
            3. Abrir Apps Script y pegar el contenido de `apps_script_crear_doc_cafecito.gs`.
            4. Reemplazar `PEGAR_ID_DEL_JSON_EN_DRIVE` por el ID del JSON.
            5. Ejecutar `crearInformeCafecitoDesdePayload`.
            6. Si se quieren insertar imagenes desde Apps Script, subir los PNG de `assets/` a Drive.
            7. Completar en el JSON los campos `driveFileId` o reemplazar los placeholders de cada imagen.
            8. Volver a ejecutar el script para crear un Google Doc nuevo.

            ## Criterio de uso

            - El DOCX prioriza edicion y claridad sobre replica pixel-perfect del PDF.
            - Las tablas son editables para facilitar comentarios.
            - Los mapas del anexo se incluyen como imagenes.
            - La version editable no debe usarse para cambiar datos sin volver al flujo reproducible.
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]], Any, list[dict[str, str]]]:
    content = rev4._load_yaml(rev4.CONTENIDO_YAML)
    records = final.base.read_xlsx(final.base.XLSX)
    stats = final.build_stats(records)
    p = final.stats_payload(records, stats)
    ranking_rows = final.read_csv(final.RANKING_COMUNAL)
    sedes_comuna = final.read_csv(final.RESUMEN_SEDES_COMUNA)
    filas, _con_ts = respuestas_por_dia_franja(records)
    barrios = rev4.top_barrios(records, top_n=5, min_freq=2)
    numbers = {**number_context(p, stats, ranking_rows, sedes_comuna), **content["institucion"]}
    pages = filled_pages(content, numbers)
    return content, pages, stats, p, filas, barrios, sedes_comuna


def assert_pdf_base_ok() -> None:
    if not PDF_REV.exists():
        raise SystemExit(f"No existe el PDF base esperado: {PDF_REV}")
    text = ""
    try:
        import subprocess

        result = subprocess.run(
            ["pdftotext", "-layout", str(PDF_REV), "-"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        text = result.stdout
    except Exception as exc:  # pragma: no cover - fallback defensivo
        raise SystemExit(f"No se pudo verificar el PDF base con pdftotext: {exc}") from exc
    if "Sábado Sábado" in text or "Domingo Domingo" in text:
        raise SystemExit("El PDF base todavia contiene la repeticion de dias.")
    required = [
        "Fechas",
        "Sábado 27 de junio de 2026",
        "Domingo 28 de junio de 2026",
    ]
    missing = [value for value in required if value not in text]
    if missing:
        raise SystemExit(f"El PDF base no contiene la ficha de fechas corregida: {missing}")
    if "DataGastro" in text:
        raise SystemExit("El PDF base contiene DataGastro.")


def main() -> None:
    assert_pdf_base_ok()
    DOCX_OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCX_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    assets = copy_assets()
    asset_paths = {asset["title"]: ASSETS_DIR / asset["imageName"] for asset in assets}
    content, pages, stats, p, filas, barrios, sedes_comuna = load_inputs()
    payload = make_payload(content, pages, stats, p, filas, barrios, sedes_comuna, assets)
    build_docx(content, pages, stats, p, filas, barrios, sedes_comuna, asset_paths)
    write_payload(payload)
    write_apps_script()
    write_drive_guide()

    print("DOCX:", rel_path(DOCX_OUT))
    print("DOCX copia:", rel_path(DOCX_FINAL))
    print("JSON:", rel_path(PAYLOAD_JSON))
    print("Apps Script:", rel_path(APPS_SCRIPT))
    print("Guia:", rel_path(DRIVE_GUIDE))
    print("Assets:", len(assets))


if __name__ == "__main__":
    main()
