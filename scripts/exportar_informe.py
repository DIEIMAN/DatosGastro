from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "07_informe_completo.ipynb"
OUTPUT_DIR = ROOT / "outputs"
HTML_OUTPUT = OUTPUT_DIR / "informe_completo.html"
PDF_OUTPUT = OUTPUT_DIR / "informe_completo.pdf"


def run_command(command: list[str], description: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"\n{description}")
    print(" ".join(str(part) for part in command))
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    if check and result.returncode != 0:
        raise SystemExit(f"ERROR: fallo {description.lower()} (codigo {result.returncode}).")
    return result


def warn_overwrite(path: Path) -> None:
    if path.exists():
        print(f"AVISO: se sobrescribira el archivo existente: {path}")


def has_weasyprint() -> bool:
    result = subprocess.run(
        [sys.executable, "-c", "import weasyprint"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def export_html(execute: bool) -> None:
    if not NOTEBOOK.exists():
        raise SystemExit(f"ERROR: no existe la notebook esperada: {NOTEBOOK}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    warn_overwrite(HTML_OUTPUT)

    command = [
        sys.executable,
        "-m",
        "nbconvert",
        "--to",
        "html",
        "--no-input",
        "--output",
        "informe_completo",
        "--output-dir",
        str(OUTPUT_DIR),
    ]
    if execute:
        command.append("--execute")
    command.append(str(NOTEBOOK))

    run_command(command, "Exportando notebook a HTML")
    print(f"\nOK: informe HTML generado en {HTML_OUTPUT}")


def export_pdf() -> None:
    warn_overwrite(PDF_OUTPUT)
    if has_weasyprint() and HTML_OUTPUT.exists():
        run_command(
            [sys.executable, "-m", "weasyprint", str(HTML_OUTPUT), str(PDF_OUTPUT)],
            "Exportando PDF con WeasyPrint",
        )
        print(f"OK: informe PDF generado en {PDF_OUTPUT}")
        return

    result = run_command(
        [
            sys.executable,
            "-m",
            "nbconvert",
            "--to",
            "pdf",
            "--no-input",
            "--output",
            "informe_completo",
            "--output-dir",
            str(OUTPUT_DIR),
            str(NOTEBOOK),
        ],
        "Intentando exportar PDF con nbconvert",
        check=False,
    )
    if result.returncode == 0 and PDF_OUTPUT.exists():
        print(f"OK: informe PDF generado en {PDF_OUTPUT}")
    else:
        print("AVISO: no se genero PDF. Instalar WeasyPrint o las dependencias PDF de nbconvert si se necesita este formato.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exporta notebooks/07_informe_completo.ipynb a HTML y, si es posible, PDF.")
    parser.add_argument(
        "--sin-ejecutar",
        action="store_true",
        help="Convierte la notebook sin ejecutarla. Por defecto se ejecuta para regenerar graficos.",
    )
    parser.add_argument(
        "--sin-pdf",
        action="store_true",
        help="No intenta generar la copia PDF opcional.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_html(execute=not args.sin_ejecutar)
    if args.sin_pdf:
        print("PDF omitido por opcion --sin-pdf.")
    else:
        export_pdf()


if __name__ == "__main__":
    main()
