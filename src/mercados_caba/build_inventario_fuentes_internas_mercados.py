"""Inventario OFFLINE y seguro de fuentes internas de mercados gastronomicos (CABA).

Lee SOLO metadata no sensible de los archivos en `fuentes_internas_mercados_caba/`:
  - nombre, formato, tamano, fecha de modificacion;
  - para .xlsx: cantidad de hojas, filas aproximadas y nombres de columnas (filtrando
    columnas sensibles, que se reemplazan por una marca);
  - clasificacion heuristica por nombre de archivo.

NO modifica los originales. NO copia valores de celdas (no exporta telefonos, emails,
CUIT/DNI, referentes ni links privados). NO hace requests. Solo libreria estandar.

Salidas:
  - outputs/mercados_caba/internal/inventario_fuentes_internas_mercados.csv  (gitignored)
  - outputs/mercados_caba/sanitized/fuentes_internas_mercados_resumen_v2.csv (sanitizado)
  - outputs/mercados_caba/sanitized/candidatos_mercados_fuentes_internas_v2.csv (sanitizado)

Uso:
    python src/mercados_caba/build_inventario_fuentes_internas_mercados.py
"""
from __future__ import annotations

import csv
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[2]
INTERNAL_SRC = REPO_ROOT / "fuentes_internas_mercados_caba"
INTERNAL_OUT = REPO_ROOT / "outputs" / "mercados_caba" / "internal"
SAN_OUT = REPO_ROOT / "outputs" / "mercados_caba" / "sanitized"

SENSITIVE_COL = re.compile(
    r"(?i)(tel|cel|whats|email|mail|correo|cuit|cuil|dni|referent|contacto|"
    r"domicilio|direccion_personal|drive\.google|docs\.google)"
)

CLASS_RULES = [
    ("sensible_no_usar", re.compile(r"(?i)(contacto|telefono|padron_personal|cuit)")),
    ("mercados_gastronomicos", re.compile(r"(?i)(mercado|food.?hall|gastron)")),
    ("ferias_gastronomicas", re.compile(r"(?i)feria")),
    ("eventos", re.compile(r"(?i)(evento|activacion|agenda)")),
    ("programas", re.compile(r"(?i)(programa|ba.?capital|politica)")),
    ("gestion_concesiones", re.compile(r"(?i)(concesion|gestion|pliego|licitacion)")),
    ("prensa_comunicacion", re.compile(r"(?i)(prensa|comunicacion|nota|articulo)")),
    ("fuera_de_alcance", re.compile(r"(?i)(pulga|antigued|shopping|outlet|ropa)")),
]

XLSX_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def classify(name: str) -> str:
    for label, pat in CLASS_RULES:
        if pat.search(name):
            return label
    return "dudoso"


def xlsx_meta(path: Path):
    """Devuelve (n_hojas, filas_aprox, columnas_sanitizadas) sin leer datos sensibles."""
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            sheets = [n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n)]
            n_hojas = len(sheets) or 1
            filas = 0
            cols = []
            if sheets:
                with z.open(sheets[0]) as fh:
                    # contar <row> de forma liviana
                    data = fh.read()
                filas = data.count(b"<row ")
            # encabezados: primera fila de la primera hoja (solo nombres de columna)
            try:
                shared = []
                if "xl/sharedStrings.xml" in names:
                    with z.open("xl/sharedStrings.xml") as fh:
                        root = ET.fromstring(fh.read())
                        for si in root.findall("m:si", XLSX_NS):
                            shared.append("".join(t.text or "" for t in si.iter()
                                                  if t.tag.endswith('}t')))
                if sheets:
                    with z.open(sheets[0]) as fh:
                        root = ET.fromstring(fh.read())
                    sd = root.find("m:sheetData", XLSX_NS)
                    if sd is not None:
                        rows = sd.findall("m:row", XLSX_NS)
                        if rows:
                            for c in rows[0].findall("m:c", XLSX_NS):
                                v = c.find("m:v", XLSX_NS)
                                if v is None or v.text is None:
                                    cols.append("")
                                    continue
                                if c.get("t") == "s":
                                    idx = int(v.text)
                                    cols.append(shared[idx] if idx < len(shared) else "")
                                else:
                                    cols.append(v.text)
            except Exception:
                pass
            cols_san = ["[columna_sensible_omitida]" if SENSITIVE_COL.search(c or "") else c
                        for c in cols]
            return n_hojas, max(filas - 1, 0), cols_san
    except Exception:
        return 0, 0, []


def main() -> int:
    INTERNAL_OUT.mkdir(parents=True, exist_ok=True)
    SAN_OUT.mkdir(parents=True, exist_ok=True)

    files = []
    if INTERNAL_SRC.is_dir():
        for p in sorted(INTERNAL_SRC.rglob("*")):
            if p.is_file() and p.name.lower() not in {"leeme.txt", "readme.txt", ".gitkeep"}:
                files.append(p)

    inv_rows, res_rows, cand_rows = [], [], []
    for p in files:
        rel = p.relative_to(INTERNAL_SRC).as_posix()
        ext = p.suffix.lower().lstrip(".")
        size = p.stat().st_size
        clasif = classify(p.name)
        n_hojas = filas = 0
        cols = []
        if ext == "xlsx":
            n_hojas, filas, cols = xlsx_meta(p)
        cols_join = " | ".join(c for c in cols if c)[:300]
        inv_rows.append([rel, ext, size, clasif, n_hojas, filas, cols_join])
        res_rows.append([p.name, clasif, ext or "sin_extension", n_hojas, filas,
                         cols_join, "metadata_no_sensible",
                         "clasificacion heuristica; revisar manualmente"])
        if clasif in {"mercados_gastronomicos", "ferias_gastronomicas"} and clasif != "sensible_no_usar":
            cand_rows.append([p.stem, p.name, clasif, "por_revisar",
                              "revisar si ya esta en V1.2 o es posible omitido"])

    # interno (gitignored): incluye nombres de archivo y columnas (ya sanitizadas)
    with (INTERNAL_OUT / "inventario_fuentes_internas_mercados.csv").open(
            "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["archivo_rel", "formato", "tamano_bytes", "clasificacion",
                    "cantidad_hojas", "filas_aprox", "columnas_sanitizadas"])
        w.writerows(inv_rows)

    # sanitizado: resumen por archivo (sin valores de celdas)
    with (SAN_OUT / "fuentes_internas_mercados_resumen_v2.csv").open(
            "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["archivo", "clasificacion", "formato", "cantidad_hojas",
                    "filas_aprox", "columnas_detectadas_no_sensibles", "senal",
                    "observacion"])
        w.writerows(res_rows)

    # sanitizado: candidatos detectados en fuentes internas
    with (SAN_OUT / "candidatos_mercados_fuentes_internas_v2.csv").open(
            "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mercado_detectado", "archivo_origen", "tipo_clasificacion",
                    "ya_en_v1_2", "accion"])
        w.writerows(cand_rows)

    print(f"Fuentes internas encontradas: {len(files)}")
    print(f"  inventario interno (gitignored): {INTERNAL_OUT / 'inventario_fuentes_internas_mercados.csv'}")
    print(f"  resumen sanitizado: {SAN_OUT / 'fuentes_internas_mercados_resumen_v2.csv'}")
    print(f"  candidatos sanitizado: {SAN_OUT / 'candidatos_mercados_fuentes_internas_v2.csv'}")
    if not files:
        print("  (carpeta vacia: se generaron CSV con encabezado y 0 filas; estado pendiente de carga)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
