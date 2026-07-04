"""QA de PDFs de DataGastro: renderiza páginas a PNG y extrae texto.

Uso (siempre con el Python del venv):
    .venv/Scripts/python.exe scripts/qa/pdf_check.py INFORME.pdf
    .venv/Scripts/python.exe scripts/qa/pdf_check.py INFORME.pdf --pages 1,3,7-9 --dpi 110
    .venv/Scripts/python.exe scripts/qa/pdf_check.py INFORME.pdf --text --no-png

Salida: PNGs en <carpeta_del_pdf>/qa_png_<nombre>/pagina_NN.png (o --outdir),
más un resumen por stdout (páginas, tamaño de página, texto vacío = posible página rota).
Reemplaza los snippets ad hoc de pdftoppm/pdfminer que fallaban por dependencias.
"""
import argparse
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("Falta pymupdf en el venv: .venv/Scripts/python.exe -m pip install pymupdf")


def parse_pages(spec: str, total: int) -> list[int]:
    """'1,3,7-9' -> índices 0-based; sin spec -> todas."""
    if not spec:
        return list(range(total))
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a) - 1, int(b)))
        elif part:
            out.add(int(part) - 1)
    return sorted(i for i in out if 0 <= i < total)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--pages", default="", help="Páginas 1-based, ej: 1,3,7-9 (default: todas)")
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--outdir", type=Path, default=None)
    ap.add_argument("--text", action="store_true", help="Imprimir texto extraído por página")
    ap.add_argument("--no-png", action="store_true", help="No renderizar PNGs (solo resumen/texto)")
    args = ap.parse_args()

    if not args.pdf.exists():
        sys.exit(f"No existe: {args.pdf}")

    doc = fitz.open(args.pdf)
    pages = parse_pages(args.pages, doc.page_count)
    outdir = args.outdir or args.pdf.parent / f"qa_png_{args.pdf.stem}"

    print(f"PDF: {args.pdf.resolve()}")
    print(f"Paginas: {doc.page_count} | render: {len(pages)} | dpi: {args.dpi}")

    if not args.no_png:
        outdir.mkdir(parents=True, exist_ok=True)

    zoom = args.dpi / 72
    for i in pages:
        page = doc[i]
        text = page.get_text().strip()
        w, h = round(page.rect.width), round(page.rect.height)
        flag = " [SIN TEXTO — revisar]" if not text else ""
        print(f"  p{i + 1:>3}: {w}x{h}pt, {len(text)} chars de texto{flag}")
        if args.text and text:
            print("    " + text[:600].replace("\n", "\n    "))
        if not args.no_png:
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            dest = outdir / f"pagina_{i + 1:02d}.png"
            pix.save(dest)
    if not args.no_png:
        print(f"PNGs en: {outdir.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
