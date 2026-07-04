"""DataGastro V2 - Etapa 2.5: inventario OFFLINE y sanitizado de la carpeta interna DGDGAS.

Recorre la carpeta interna copiada de Drive (por defecto 'Algunas Cosas de Drive') y produce
un inventario a NIVEL DE ARCHIVO, sin exponer informacion sensible.

Garantias de privacidad y seguridad:
  - NO hace requests, NO usa API keys, NO descarga nada.
  - NO modifica, mueve ni borra los archivos originales.
  - NO lee valores de celdas. De los .xlsx solo lee 'xl/workbook.xml' (nombres de hoja),
    que es metadata estructural, nunca 'sharedStrings' (que contendria valores/PII).
  - NO abre ni expone el contenido de .gdoc/.gsheet/.lnk (punteros privados de Drive):
    solo registra que son punteros sin contenido local.
  - Usa SOLO rutas relativas. No escribe rutas absolutas ni links privados de Drive.

Salida: outputs/v2/sanitized/inventario_dgdgas_archivos_sanitizado.csv

Uso:
    python src/v2/build_dgdgas_inventory.py
    python src/v2/build_dgdgas_inventory.py --carpeta "Algunas Cosas de Drive"
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "outputs" / "v2" / "sanitized"
OUT_CSV = OUT_DIR / "inventario_dgdgas_archivos_sanitizado.csv"

# Nombres candidatos de la carpeta interna (orden de preferencia).
CANDIDATAS = [
    "Algunas Cosas de Drive",
    "DGDGAS",
    "DG DGAS",
    "DGAS",
    "Direccion Gastronomia",
    "Direccion Gastronomia CABA",
]

# Punteros de Drive / accesos directos: NO se abren.
PUNTEROS = {".gdoc", ".gsheet", ".gslides", ".gform", ".lnk", ".url"}

COLUMNS = [
    "ruta_relativa", "nombre_archivo", "extension", "tipo_archivo",
    "tamano_aproximado", "fecha_modificacion_si_disponible", "carpeta_padre",
    "posible_tema", "posible_fuente_v2", "nivel_sensibilidad_estimado",
    "utilidad_datagastro_v2", "accion_recomendada", "contiene_pii_probable",
    "observaciones",
]


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n/1024:.0f}{unit}" if unit == "KB" else f"{n/1024/1024:.1f}{unit}"
        n = n  # noqa
    return f"{n}B"


def size_bucket(path: Path) -> str:
    try:
        b = path.stat().st_size
    except OSError:
        return "desconocido"
    if b == 0:
        return "0B (puntero)"
    if b < 50 * 1024:
        return "<50KB"
    if b < 500 * 1024:
        return "50-500KB"
    if b < 5 * 1024 * 1024:
        return "0.5-5MB"
    return ">5MB"


def mtime(path: Path) -> str:
    try:
        return dt.datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
    except OSError:
        return "no_disponible"


def xlsx_sheets(path: Path) -> list[str]:
    """Lee SOLO nombres de hoja desde xl/workbook.xml. No toca valores de celdas."""
    try:
        with zipfile.ZipFile(path) as z:
            wb = z.read("xl/workbook.xml").decode("utf-8", "ignore")
            return re.findall(r'<sheet[^>]*name="([^"]+)"', wb)
    except Exception:
        return []


def classify(name: str, ext: str) -> dict:
    """Clasifica tema / fuente / sensibilidad / utilidad por NOMBRE y EXTENSION (no contenido)."""
    n = name.lower()
    d = {
        "posible_tema": "dudoso",
        "posible_fuente_v2": "pendiente",
        "nivel_sensibilidad_estimado": "revisar",
        "utilidad_datagastro_v2": "media",
        "accion_recomendada": "pendiente_revision",
        "contiene_pii_probable": "revisar",
        "observaciones": "",
    }

    if ext in PUNTEROS:
        d.update(nivel_sensibilidad_estimado="revisar", contiene_pii_probable="no",
                 observaciones="puntero/acceso directo a Drive, sin contenido local; no se abre")
        if ext == ".lnk":
            d.update(posible_tema="administrativo_interno", utilidad_datagastro_v2="descartar_por_ahora",
                     accion_recomendada="no_usar_por_sensible")
            return d

    # Base de datos DGDGAS (directorio de locales por rubro, perfilado en V1: PII alto)
    if "base de datos" in n and ("dgdgas" in n or "evento" in n):
        d.update(posible_tema="relevamientos_establecimientos",
                 posible_fuente_v2="I10_directorio_gastronomico_dgdgas",
                 nivel_sensibilidad_estimado="alto",
                 utilidad_datagastro_v2="alta",
                 accion_recomendada="fuente_para_catalogo_interno",
                 contiene_pii_probable="si",
                 observaciones="directorio de locales por rubro; columnas de contacto (celular/mail/referente) = PII; usar agregado sin PII")
        return d
    if "recap" in n and "evento" in n:
        d.update(posible_tema="eventos_gastronomicos",
                 posible_fuente_v2="I11_recap_eventos_dgdgas",
                 nivel_sensibilidad_estimado="medio",
                 utilidad_datagastro_v2="alta",
                 accion_recomendada="ancla_eventos",
                 contiene_pii_probable="revisar",
                 observaciones="recaps de eventos propios por edicion; puede enriquecer F04 (eventos)")
        return d
    if "ade" in n or "foodtruck" in n or "seguimiento" in n:
        d.update(posible_tema="ferias_mercados",
                 posible_fuente_v2="I12_seguimiento_ade_dgdgas",
                 nivel_sensibilidad_estimado="medio",
                 utilidad_datagastro_v2="media",
                 accion_recomendada="pendiente_revision",
                 contiene_pii_probable="revisar",
                 observaciones="seguimiento/ranking de foodtrucks y eventos; incluye dashboards de gestion")
        return d
    if "eventos acompa" in n:
        d.update(posible_tema="eventos_gastronomicos",
                 posible_fuente_v2="I11_recap_eventos_dgdgas",
                 utilidad_datagastro_v2="media",
                 accion_recomendada="ancla_eventos",
                 observaciones="eventos acompanados; revisar grano y fechas")
        return d
    if "informe" in n or "documento_maestro" in n or "ecosistema" in n:
        d.update(posible_tema="documental_historico",
                 posible_fuente_v2="I13_documental_dgdgas",
                 nivel_sensibilidad_estimado="bajo",
                 utilidad_datagastro_v2="media",
                 accion_recomendada="fuente_documental",
                 contiene_pii_probable="no",
                 observaciones="documento/informe institucional; util para contexto y casos historicos")
        return d
    if "readme" in n:
        d.update(posible_tema="administrativo_interno",
                 posible_fuente_v2="I13_documental_dgdgas",
                 nivel_sensibilidad_estimado="bajo",
                 utilidad_datagastro_v2="baja",
                 accion_recomendada="contexto_programas",
                 contiene_pii_probable="no",
                 observaciones="readme/documentacion interna")
        return d
    if "rysde" in n:
        d.update(posible_tema="dudoso", posible_fuente_v2="pendiente",
                 observaciones="sigla no resuelta; requiere confirmacion con DGDGAS")
        return d

    return d


def find_folder(explicit: str | None) -> Path | None:
    if explicit:
        p = REPO_ROOT / explicit
        return p if p.is_dir() else None
    for name in CANDIDATAS:
        p = REPO_ROOT / name
        if p.is_dir():
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", default=None, help="Carpeta interna a inventariar (relativa al repo)")
    args = ap.parse_args()

    print("=" * 78)
    print("DataGastro V2 - Etapa 2.5: inventario OFFLINE y sanitizado de DGDGAS")
    print("No hace requests, no usa API keys, no lee valores de celdas, no modifica originales.")
    print("=" * 78)

    folder = find_folder(args.carpeta)
    if folder is None:
        print("\n[ERROR] No se encontro carpeta DGDGAS. Rutas revisadas (relativas al repo):")
        for name in (CANDIDATAS if not args.carpeta else [args.carpeta]):
            print(f"  - {name}")
        print("Inventario no generado. (No es un fallo si el proyecto se movio de maquina.)")
        return 0

    rel_folder = folder.relative_to(REPO_ROOT)
    print(f"\nCarpeta detectada: {rel_folder}")

    rows = []
    n_dirs = 0
    for path in sorted(folder.rglob("*")):
        if path.is_dir():
            n_dirs += 1
            continue
        ext = path.suffix.lower()
        info = classify(path.name, ext)
        obs = info["observaciones"]
        if ext in (".xlsx", ".xlsm"):
            sheets = xlsx_sheets(path)
            if sheets:
                obs = (obs + " | " if obs else "") + f"hojas={len(sheets)}: " + ", ".join(sheets)
            tipo = "planilla_excel"
        elif ext in PUNTEROS:
            tipo = "puntero_drive"
        elif ext in (".md", ".txt"):
            tipo = "texto"
        elif ext == ".zip":
            tipo = "comprimido"
        elif ext in (".pdf",):
            tipo = "pdf"
        elif ext in (".docx", ".doc"):
            tipo = "documento_word"
        else:
            tipo = ext.lstrip(".") or "sin_extension"

        rows.append({
            "ruta_relativa": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "nombre_archivo": path.name,
            "extension": ext or "(ninguna)",
            "tipo_archivo": tipo,
            "tamano_aproximado": size_bucket(path),
            "fecha_modificacion_si_disponible": mtime(path),
            "carpeta_padre": str(path.parent.relative_to(REPO_ROOT)).replace("\\", "/"),
            "posible_tema": info["posible_tema"],
            "posible_fuente_v2": info["posible_fuente_v2"],
            "nivel_sensibilidad_estimado": info["nivel_sensibilidad_estimado"],
            "utilidad_datagastro_v2": info["utilidad_datagastro_v2"],
            "accion_recomendada": info["accion_recomendada"],
            "contiene_pii_probable": info["contiene_pii_probable"],
            "observaciones": obs,
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    print(f"Carpetas recorridas: {n_dirs + 1} | archivos inventariados: {len(rows)}")
    print(f"Inventario sanitizado escrito en: {OUT_CSV.relative_to(REPO_ROOT)}")
    print("\nResumen por utilidad:")
    for u in ("alta", "media", "baja", "descartar_por_ahora"):
        c = sum(1 for r in rows if r["utilidad_datagastro_v2"] == u)
        print(f"  {u}: {c}")
    print("Archivos con PII probable = si:",
          sum(1 for r in rows if r["contiene_pii_probable"] == "si"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
