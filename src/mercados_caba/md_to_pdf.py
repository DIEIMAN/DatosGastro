"""Conversor minimo Markdown -> PDF para los entregables de mercados gastronomicos.

Usa SOLO reportlab (disponible en el venv). No hace requests ni instala nada.
Soporta: titulos (#, ##, ###), parrafos, negritas (**), codigo inline (`),
listas (-, *), citas (>), reglas (---) y TABLAS Markdown (| ... |).

Uso:
    python src/mercados_caba/md_to_pdf.py <entrada.md> <salida.pdf>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, Image)

_TRANS = {"→": "->", "←": "<-", "↔": "<->", "≠": "!=",
          "≥": ">=", "≤": "<=", "×": "x", "✓": "OK"}


def _translit(text: str) -> str:
    out = []
    for ch in text:
        if ch in _TRANS:
            out.append(_TRANS[ch])
            continue
        try:
            ch.encode("cp1252")
            out.append(ch)
        except UnicodeEncodeError:
            out.append("?")
    return "".join(out)


def _inline(text: str) -> str:
    text = _translit(text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier" size="8">\1</font>', text)
    return text


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("H1x", parent=ss["Heading1"], fontSize=17, spaceAfter=8, spaceBefore=4))
    ss.add(ParagraphStyle("H2x", parent=ss["Heading2"], fontSize=13, spaceAfter=6, spaceBefore=10))
    ss.add(ParagraphStyle("H3x", parent=ss["Heading3"], fontSize=11, spaceAfter=4, spaceBefore=8))
    ss.add(ParagraphStyle("Body", parent=ss["BodyText"], fontSize=9.5, leading=13, spaceAfter=5))
    ss.add(ParagraphStyle("MBullet", parent=ss["BodyText"], fontSize=9.5, leading=13,
                          leftIndent=14, bulletIndent=4, spaceAfter=2))
    ss.add(ParagraphStyle("Quote", parent=ss["BodyText"], fontSize=9, leading=12,
                          leftIndent=10, textColor=colors.HexColor("#444444"),
                          borderColor=colors.HexColor("#cccccc"), borderWidth=0, spaceAfter=5))
    ss.add(ParagraphStyle("Cell", parent=ss["BodyText"], fontSize=7.6, leading=9.5))
    ss.add(ParagraphStyle("CellH", parent=ss["BodyText"], fontSize=7.6, leading=9.5,
                          textColor=colors.white))
    return ss


def _table_flow(rows, ss, avail_w):
    cells = []
    for r in rows:
        parts = [c.strip() for c in r.strip().strip("|").split("|")]
        cells.append(parts)
    ncol = max(len(r) for r in cells)
    cells = [r + [""] * (ncol - len(r)) for r in cells]
    data = []
    for i, r in enumerate(cells):
        sty = ss["CellH"] if i == 0 else ss["Cell"]
        data.append([Paragraph(_inline(c), sty) for c in r])
    t = Table(data, colWidths=[avail_w / ncol] * ncol, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#365f91")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
    ]))
    return t


def convert(md_path: Path, pdf_path: Path):
    lines = md_path.read_text(encoding="utf-8").splitlines()
    ss = _styles()
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4,
                            leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    avail_w = doc.width
    flow = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s:
            flow.append(Spacer(1, 4)); i += 1; continue
        # tabla: bloque de lineas que empiezan con |
        if s.startswith("|"):
            block = []
            while i < n and lines[i].strip().startswith("|"):
                block.append(lines[i]); i += 1
            block = [b for b in block if not re.match(r"^\s*\|[\s:\-|]+\|\s*$", b)]
            if block:
                flow.append(_table_flow(block, ss, avail_w))
                flow.append(Spacer(1, 6))
            continue
        mimg = re.match(r"^!\[[^\]]*\]\(([^)]+)\)\s*$", s)
        if mimg:
            ip = (md_path.parent / mimg.group(1)).resolve()
            if ip.is_file():
                iw, ih = ImageReader(str(ip)).getSize()
                w = min(avail_w, iw)
                h = w * ih / iw
                if h > 15 * cm:
                    h = 15 * cm
                    w = h * iw / ih
                flow.append(Image(str(ip), width=w, height=h))
                flow.append(Spacer(1, 6))
            else:
                flow.append(Paragraph(f"[imagen no encontrada: {mimg.group(1)}]", ss["Body"]))
            i += 1
            continue
        if s.startswith("### "):
            flow.append(Paragraph(_inline(s[4:]), ss["H3x"]))
        elif s.startswith("## "):
            flow.append(Paragraph(_inline(s[3:]), ss["H2x"]))
        elif s.startswith("# "):
            flow.append(Paragraph(_inline(s[2:]), ss["H1x"]))
        elif s.startswith("---"):
            flow.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#bbbbbb"),
                                   spaceBefore=4, spaceAfter=6))
        elif s.startswith("> "):
            flow.append(Paragraph(_inline(s[2:]), ss["Quote"]))
        elif re.match(r"^[-*] ", s):
            flow.append(Paragraph(_inline(s[2:]), ss["MBullet"], bulletText="•"))
        elif re.match(r"^\d+\. ", s):
            flow.append(Paragraph(_inline(s), ss["Body"]))
        else:
            flow.append(Paragraph(_inline(s), ss["Body"]))
        i += 1
    doc.build(flow)


def main() -> int:
    if len(sys.argv) != 3:
        print("uso: python src/mercados_caba/md_to_pdf.py <entrada.md> <salida.pdf>")
        return 2
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.parent.mkdir(parents=True, exist_ok=True)
    convert(src, dst)
    print(f"PDF generado: {dst} ({dst.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
