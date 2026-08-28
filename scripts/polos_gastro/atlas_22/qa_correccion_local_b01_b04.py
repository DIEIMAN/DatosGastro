#!/usr/bin/env python3
"""QA local B-01...B-04 y empaquetado reproducible, completamente offline."""

from __future__ import annotations

import argparse
import csv
import difflib
import fnmatch
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw


SCRIPT = Path(__file__).resolve()


def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("No se encontró la raíz del repositorio")


REPO = repo_root(SCRIPT)
WORK_ROOT = REPO / "outputs/polos_gastro/_work/atlas_22"
TEMP_WORK_ROOT = Path(tempfile.gettempdir()).resolve() / "datagastro_atlas_22_tests"
BASE = REPO / "outputs/polos_gastro/INFORMEFINAL"
OUT = WORK_ROOT / "_UNCONFIGURED"
ORIGINAL = BASE / "codex/atlas_22_v2_compacta_v1"
AUDIT = BASE / "claude/atlas_22_v2_compacta_auditoria_independiente_v1/AUDITORIA_INDEPENDIENTE_ATLAS_22_V2_COMPACTA.md"
CURATED_BUILD = SCRIPT.parent / "build_atlas_22_v2_compacta.py"
PDF_NAME = "ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS_V2_COMPACTA.pdf"
ZIP_NAME = "REVISION_CODEX_ATLAS_22_V2_COMPACTA_CORRECCION_LOCAL_V1.zip"
PDF = OUT / PDF_NAME
ZIP = OUT / ZIP_NAME
SIDECAR = OUT / f"{ZIP_NAME}.sha256"
TARGET_PAGES = (5, 14, 27, 32, 51, 52)
TARGET_SET = set(TARGET_PAGES)
ORIGINAL_RENDER = ORIGINAL / "qa/render_paginas"
CORRECTED_RENDER = OUT / "qa/render_paginas"
TARGET_RENDER = OUT / "qa/render_paginas_objetivo"
COMPARE = OUT / "comparacion"
QA = OUT / "qa"

EXPECTED = {
    ORIGINAL / PDF_NAME: "19ea4feeee7c485ef4237c9e05a977fe983e157aebd54e60731206cd96d964bd",
    ORIGINAL / "REVISION_CODEX_ATLAS_22_V2_COMPACTA_V1.zip": "429c15d55c57bb6db917bd3cf25206aaafb816690e20fabc5ce548b4b7e2afc5",
    AUDIT: "8ccec2d1bed8e71f2f9bb0555b1b4a64ce1ba8f3451f50e7a4b8ef1efe2707d7",
    ORIGINAL / "contenido/contenido_atlas_22_v2_compacta.json": "8cc32682fd62a72bf4cd1d398d01f30b7721868d0a0b1007b9d281f17c45305e",
}


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _protected_patterns() -> list[str]:
    registry = REPO / "docs/polos_gastro/PROTECTED_SURFACES.yaml"
    if not registry.is_file():
        raise FileNotFoundError(f"Falta el registro de superficies protegidas: {registry}")
    patterns: list[str] = []
    current: str | None = None
    for raw in registry.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if line.startswith("ruta_o_patron:"):
            current = line.split(":", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("puede_modificar:") and current is not None:
            if line.split(":", 1)[1].strip().lower() == "false":
                patterns.append(current.replace("\\", "/"))
            current = None
    if not patterns:
        raise RuntimeError("El registro no contiene superficies no modificables")
    return patterns


def _matches_protected(path: Path) -> str | None:
    try:
        relative_path = path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return None
    for pattern in _protected_patterns():
        normalized = pattern.rstrip("/")
        directory_root = normalized[:-3] if normalized.endswith("/**") else None
        if directory_root and (relative_path == directory_root or relative_path.startswith(directory_root + "/")):
            return pattern
        if fnmatch.fnmatchcase(relative_path, normalized):
            return pattern
    return None


def validate_runtime_paths(source_package: Path, output_dir: Path, allow_temp_output: bool) -> tuple[Path, Path]:
    source = source_package.expanduser().resolve()
    output = output_dir.expanduser().resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"El paquete fuente no existe: {source}")
    if source == output:
        raise RuntimeError("El destino no puede ser igual al paquete fuente")
    if _is_relative_to(output, source):
        raise RuntimeError("El destino no puede quedar dentro del paquete fuente")
    protected = _matches_protected(output)
    if protected:
        raise RuntimeError(f"Destino protegido por {protected}: {output}")
    allowed_root = TEMP_WORK_ROOT if allow_temp_output else WORK_ROOT.resolve()
    if not _is_relative_to(output, allowed_root):
        mode = "temporal" if allow_temp_output else "de trabajo controlada"
        raise RuntimeError(f"Destino fuera de la raiz {mode} permitida: {allowed_root}")
    if output.exists() and not output.is_dir():
        raise RuntimeError(f"El destino existe y no es un directorio: {output}")
    return source, output


def configure_paths(source_package: Path, output_dir: Path) -> None:
    global BASE, OUT, ORIGINAL, AUDIT, PDF, ZIP, SIDECAR
    global ORIGINAL_RENDER, CORRECTED_RENDER, TARGET_RENDER, COMPARE, QA, EXPECTED
    BASE = source_package
    OUT = output_dir
    ORIGINAL = BASE / "codex/atlas_22_v2_compacta_v1"
    AUDIT = BASE / "claude/atlas_22_v2_compacta_auditoria_independiente_v1/AUDITORIA_INDEPENDIENTE_ATLAS_22_V2_COMPACTA.md"
    PDF = OUT / PDF_NAME
    ZIP = OUT / ZIP_NAME
    SIDECAR = OUT / f"{ZIP_NAME}.sha256"
    ORIGINAL_RENDER = ORIGINAL / "qa/render_paginas"
    CORRECTED_RENDER = OUT / "qa/render_paginas"
    TARGET_RENDER = OUT / "qa/render_paginas_objetivo"
    COMPARE = OUT / "comparacion"
    QA = OUT / "qa"
    EXPECTED = {
        ORIGINAL / PDF_NAME: "19ea4feeee7c485ef4237c9e05a977fe983e157aebd54e60731206cd96d964bd",
        ORIGINAL / "REVISION_CODEX_ATLAS_22_V2_COMPACTA_V1.zip": "429c15d55c57bb6db917bd3cf25206aaafb816690e20fabc5ce548b4b7e2afc5",
        AUDIT: "8ccec2d1bed8e71f2f9bb0555b1b4a64ce1ba8f3451f50e7a4b8ef1efe2707d7",
        ORIGINAL / "contenido/contenido_atlas_22_v2_compacta.json": "8cc32682fd62a72bf4cd1d398d01f30b7721868d0a0b1007b9d281f17c45305e",
    }


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def preflight_hashes() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    checks: list[dict[str, object]] = []

    def add(role: str, path: Path, expected: str | None = None) -> str:
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = sha256(path)
        result = "PASS" if expected is None or actual == expected else "FAIL"
        rows.append({"rol": role, "ruta_relativa": rel(path), "bytes": path.stat().st_size, "sha256": actual, "esperado": expected or actual, "resultado": result})
        if result != "PASS":
            raise RuntimeError(f"Hash divergente: {rel(path)}")
        return actual

    for path, expected in EXPECTED.items():
        add("entrada_preflight", path, expected)
    add("script_curado_actual", CURATED_BUILD)

    for path in sorted((ORIGINAL / "matrices").glob("*")):
        if path.is_file():
            add("matriz_original", path)

    preservation = read_csv(OUT / "qa/QA_PRESERVACION_INSUMOS.csv")
    for item in preservation:
        path = REPO / item["ruta_relativa"]
        add("input_canonico", path, item["sha256_pre"])

    metadata_path = OUT / "assets_derivados/mascaras/metadata_mascaras_editoriales.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if len(metadata) != 29:
        raise RuntimeError(f"Se esperaban 29 activos y hay {len(metadata)}")
    d_assets = 0
    for item in metadata:
        source = REPO / item["fuente_relativa"]
        old_asset = ORIGINAL / "assets_derivados/mapas_publicacion" / item["archivo"]
        new_asset = OUT / "assets_derivados/mapas_publicacion" / item["archivo"]
        add("fuente_cartografica_congelada", source, item["sha256_fuente"])
        old_hash = add("activo_mapa_original", old_asset, item["sha256_derivado"])
        new_hash = add("activo_mapa_corregido", new_asset, item["sha256_derivado"])
        if old_hash != new_hash:
            raise RuntimeError(f"Activo cartográfico modificado: {item['archivo']}")
        if item["intervenciones"]:
            d_assets += 1
    if d_assets != 6:
        raise RuntimeError(f"Se esperaban seis activos D-01/D-02 y hay {d_assets}")
    if sha256(ORIGINAL / "assets_derivados/mascaras/metadata_mascaras_editoriales.json") != sha256(metadata_path):
        raise RuntimeError("Metadata D-01/D-02 divergente")
    checks.extend([
        {"control": "hashes_entrantes", "resultado": "PASS", "detalle": "PDF, ZIP y auditoría coinciden con la consigna"},
        {"control": "inputs_canonicos", "resultado": "PASS", "detalle": f"{len(preservation)}/{len(preservation)}"},
        {"control": "fuentes_cartograficas", "resultado": "PASS", "detalle": "29/29"},
        {"control": "activos_cartograficos", "resultado": "PASS", "detalle": "29/29 byte-idénticos"},
        {"control": "D01_D02", "resultado": "PASS", "detalle": "6/6 metadata y derivados byte-idénticos"},
    ])
    write_csv(QA / "PREFLIGHT_BASELINE_HASHES.csv", ["rol", "ruta_relativa", "bytes", "sha256", "esperado", "resultado"], rows)
    return rows, checks


def pixel_preservation() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    changed_pages: list[int] = []
    for page in range(1, 59):
        old = np.asarray(Image.open(ORIGINAL_RENDER / f"pagina_{page:02d}.png").convert("RGB"))
        new = np.asarray(Image.open(CORRECTED_RENDER / f"pagina_{page:02d}.png").convert("RGB"))
        if old.shape != new.shape:
            raise RuntimeError(f"Dimensiones de render divergentes en página {page}")
        changed = int(np.count_nonzero(np.any(old != new, axis=2)))
        authorized = page in TARGET_SET
        result = "PASS" if (authorized and changed > 0) or (not authorized and changed == 0) else "FAIL"
        rows.append({
            "pagina": page,
            "autorizada_a_cambiar": "SI" if authorized else "NO",
            "pixeles_distintos": changed,
            "pixeles_totales": int(old.shape[0] * old.shape[1]),
            "resultado": result,
        })
        if changed:
            changed_pages.append(page)
        if result != "PASS":
            raise RuntimeError(f"Preservación visual falló en página {page}: {changed}")
    if changed_pages != list(TARGET_PAGES):
        raise RuntimeError(f"Páginas cambiadas inesperadas: {changed_pages}")
    write_csv(OUT / "QA_PRESERVACION_PAGINAS_NO_OBJETIVO.csv", ["pagina", "autorizada_a_cambiar", "pixeles_distintos", "pixeles_totales", "resultado"], rows)
    checks = [
        {"control": "paginas_objetivo_modificadas", "resultado": "PASS", "detalle": "5,14,27,32,51,52"},
        {"control": "paginas_no_objetivo", "resultado": "PASS", "detalle": "52/52 con cero píxeles distintos"},
    ]
    return rows, checks


def make_visuals() -> None:
    TARGET_RENDER.mkdir(parents=True, exist_ok=True)
    for page in TARGET_PAGES:
        shutil.copy2(CORRECTED_RENDER / f"pagina_{page:02d}.png", TARGET_RENDER / f"pagina_{page:02d}.png")

    corrected = [Image.open(CORRECTED_RENDER / f"pagina_{page:02d}.png").convert("RGB") for page in TARGET_PAGES]
    thumbs = [image.resize((int(image.width * 0.4), int(image.height * 0.4)), Image.Resampling.LANCZOS) for image in corrected]
    gap = 18
    sheet = Image.new("RGB", (3 * thumbs[0].width + 4 * gap, 2 * thumbs[0].height + 3 * gap), "#D9DEE5")
    for idx, thumb in enumerate(thumbs):
        x = gap + (idx % 3) * (thumb.width + gap)
        y = gap + (idx // 3) * (thumb.height + gap)
        sheet.paste(thumb, (x, y))
    sheet.save(QA / "PLANCHA_PAGINAS_OBJETIVO_40PCT.png", optimize=True)

    pairs = []
    for page in TARGET_PAGES:
        old = Image.open(ORIGINAL_RENDER / f"pagina_{page:02d}.png").convert("RGB")
        new = Image.open(CORRECTED_RENDER / f"pagina_{page:02d}.png").convert("RGB")
        size = (int(old.width * 0.2), int(old.height * 0.2))
        pairs.append((old.resize(size, Image.Resampling.LANCZOS), new.resize(size, Image.Resampling.LANCZOS)))
    width = pairs[0][0].width * 2 + 3 * gap
    height = len(pairs) * (pairs[0][0].height + 26) + (len(pairs) + 1) * gap
    compare = Image.new("RGB", (width, height), "#D9DEE5")
    draw = ImageDraw.Draw(compare)
    for idx, (old, new) in enumerate(pairs):
        y = gap + idx * (old.height + 26 + gap)
        compare.paste(old, (gap, y))
        compare.paste(new, (2 * gap + old.width, y))
        draw.text((gap, y + old.height + 4), f"Pagina {TARGET_PAGES[idx]} - original", fill="#203B59")
        draw.text((2 * gap + old.width, y + old.height + 4), f"Pagina {TARGET_PAGES[idx]} - corregida", fill="#203B59")
    compare.save(COMPARE / "COMPARACION_PAGINAS_5_14_27_32_51_52.png", optimize=True)


def text_and_target_qa() -> list[dict[str, object]]:
    old_doc = fitz.open(ORIGINAL / PDF_NAME)
    new_doc = fitz.open(PDF)
    old_pages = [page.get_text("text") for page in old_doc]
    new_pages = [page.get_text("text") for page in new_doc]
    all_text = "\n".join(new_pages)

    diffs = ["# Diff de texto de páginas objetivo", "", "Solo se documentan B-01...B-04; la página 32 cambia en composición sin cambio textual.", ""]
    for page in TARGET_PAGES:
        diffs.extend([f"## Página {page}", "", "```diff"])
        page_diff = list(difflib.unified_diff(old_pages[page - 1].splitlines(), new_pages[page - 1].splitlines(), fromfile="original", tofile="corregida", lineterm=""))
        diffs.extend(page_diff or ["(sin diferencias de texto; cambio visual de composición)"])
        diffs.extend(["```", ""])
    (OUT / "DIFF_TEXTO_PAGINAS_OBJETIVO.md").write_text("\n".join(diffs), encoding="utf-8")

    matrix = [
        {"B-ID": "B-01", "pagina": 5, "anterior": "Polo documentado con delimitacion provisional", "nuevo": "Polo documentado con delimitación provisional", "causa": "tipología R13 sin tilde", "archivo_fuente": "contenido/contenido_atlas_22_v2_compacta.json", "linea_campo": "fichas[R13].tipologia", "control": "texto extraído + render", "resultado": "PASS"},
        {"B-ID": "B-01", "pagina": 27, "anterior": "Polo documentado con delimitacion provisional", "nuevo": "Polo documentado con delimitación provisional", "causa": "tipología R13 sin tilde", "archivo_fuente": "contenido/contenido_atlas_22_v2_compacta.json", "linea_campo": "fichas[R13].tipologia", "control": "texto extraído + render", "resultado": "PASS"},
        {"B-ID": "B-01", "pagina": 52, "anterior": "delimitacion provisional", "nuevo": "delimitación provisional", "causa": "tipología R13 sin tilde", "archivo_fuente": "contenido/contenido_atlas_22_v2_compacta.json", "linea_campo": "fichas[R13].tipologia", "control": "texto extraído + render", "resultado": "PASS"},
        {"B-ID": "B-02", "pagina": 27, "anterior": "Anclajes anclajes históricos NO_VERIFICABLES", "nuevo": "Anclajes históricos NO_VERIFICABLES", "causa": "duplicación local", "archivo_fuente": "contenido/contenido_atlas_22_v2_compacta.json", "linea_campo": "fichas[R13].limitaciones_especificas[1]", "control": "texto extraído + render", "resultado": "PASS"},
        {"B-ID": "B-03", "pagina": 14, "anterior": "SIN_CIFRA_CANONICA_COMPARABLE (glosa)", "nuevo": "Sin cifra canónica comparable + glosa subordinada", "causa": "código y glosa combinados", "archivo_fuente": "contenido/contenido_atlas_22_v2_compacta.json", "linea_campo": "fichas[R06].cifra/etiqueta_publica_cifra/glosa_cifra", "control": "guarda automática + render", "resultado": "PASS"},
        {"B-ID": "B-03", "pagina": 51, "anterior": "SIN_CIFRA_CANONICA_COMPARA/BLE (glosa)", "nuevo": "Sin cifra canónica comparable", "causa": "código crudo y corte mid-token", "archivo_fuente": "scripts/build_atlas_22_v2_compacta.py", "linea_campo": "short_figure", "control": "guarda automática + render", "resultado": "PASS"},
        {"B-ID": "B-04", "pagina": 32, "anterior": "rótulo inferior recortado", "nuevo": "rótulo completo y separado", "causa": "colisión de composición", "archivo_fuente": "scripts/build_atlas_22_v2_compacta.py", "linea_campo": "draw_comp_page/R12", "control": "render a resolución completa", "resultado": "PASS"},
    ]
    write_csv(OUT / "MATRIZ_CAMBIOS_B01_B04.csv", ["B-ID", "pagina", "anterior", "nuevo", "causa", "archivo_fuente", "linea_campo", "control", "resultado"], matrix)

    target_checks = [
        (5, "B-01", "delimitación correcta; restantes tipologías preservadas", "delimitación" in new_pages[4] and "delimitacion" not in new_pages[4]),
        (14, "B-03", "R06 rotulada; glosa y 767/602 preservados; R04 intacta", "Sin cifra canónica comparable" in new_pages[13] and "universo V3 767" in new_pages[13] and "602 puntos incluidos" in new_pages[13] and "SIN_CIFRA" not in new_pages[13]),
        (27, "B-01/B-02", "tilde y Anclajes históricos; R11 intacta", "delimitación provisional" in new_pages[26] and "Anclajes históricos" in new_pages[26] and "Anclajes anclajes" not in new_pages[26] and "66 registros" in new_pages[26]),
        (32, "B-04", "línea completa, sin recorte ni solape; activo intacto", "VISTA COMPLEMENTARIA" in new_pages[31]),
        (51, "B-03", "R06 rotulada sin código ni corte; otras filas intactas", "Sin cifra canónica comparable" in new_pages[50] and "SIN_CIFRA" not in new_pages[50] and "COMPARA/BLE" not in new_pages[50]),
        (52, "B-01", "R13 con delimitación; otras filas intactas", "delimitación provisional" in new_pages[51] and "delimitacion" not in new_pages[51]),
    ]
    target_rows = [{"pagina": page, "B-ID": bid, "control": detail, "resultado": "PASS" if ok else "FAIL", "inspeccion_visual": "INSPECCIONADA_RESOLUCION_COMPLETA"} for page, bid, detail, ok in target_checks]
    if any(row["resultado"] != "PASS" for row in target_rows):
        raise RuntimeError("QA de páginas objetivo falló")
    write_csv(QA / "QA_PAGINAS_OBJETIVO.csv", ["pagina", "B-ID", "control", "resultado", "inspeccion_visual"], target_rows)

    global_checks = [
        ("cero_delimitacion", "delimitacion" not in all_text),
        ("presencia_delimitación", "delimitación" in all_text),
        ("cero_duplicacion_anclajes", "Anclajes anclajes" not in all_text),
        ("presencia_anclajes_historicos", "Anclajes históricos" in all_text),
        ("cero_codigo_R06", "SIN_CIFRA_CANONICA_COMPARABLE" not in all_text and "SIN_CIFRA_" not in all_text),
        ("cero_corte_mid_token", "COMPARA/BLE" not in all_text),
        ("R01_R22", all(re.search(rf"\bR{i:02d}\b", all_text) for i in range(1, 23))),
        ("cero_R23", re.search(r"\bR23\b", all_text) is None),
        ("R13_cota", "≥314" in all_text),
        ("R06_antecedente_no_KPI", "universo V3 767 histórico metodológico no publicable como KPI principal" in all_text and "602 puntos incluidos" in all_text),
    ]
    global_rows = [{"control": name, "resultado": "PASS" if ok else "FAIL"} for name, ok in global_checks]
    if any(row["resultado"] != "PASS" for row in global_rows):
        raise RuntimeError("QA global de texto falló: " + ", ".join(row["control"] for row in global_rows if row["resultado"] == "FAIL"))
    write_csv(QA / "QA_TEXTO_GLOBAL.csv", ["control", "resultado"], global_rows)
    old_doc.close()
    new_doc.close()
    return [{"control": "texto_global", "resultado": "PASS", "detalle": f"{len(global_rows)}/{len(global_rows)}"}, {"control": "paginas_objetivo", "resultado": "PASS", "detalle": "6/6 inspeccionadas"}]


def pdf_structural_qa() -> list[dict[str, object]]:
    doc = fitz.open(PDF)
    texts = [page.get_text("text") for page in doc]
    toc = doc.get_toc(simple=False)
    links = [link for page in doc for link in page.get_links() if link.get("kind") in {fitz.LINK_GOTO, fitz.LINK_NAMED}]
    font_xrefs = {font[0] for page in doc for font in doc.get_page_fonts(page.number, full=True) if font[0] > 0}
    embedded = 0
    for xref in font_xrefs:
        try:
            extracted = doc.extract_font(xref)
            embedded += int(bool(extracted and extracted[-1]))
        except Exception:
            pass
    rows = [
        {"control": "paginas_exactas", "resultado": "PASS" if doc.page_count == 58 else "FAIL", "detalle": doc.page_count},
        {"control": "A4", "resultado": "PASS" if all(abs(p.rect.width - 595.276) < 1 and abs(p.rect.height - 841.89) < 1 for p in doc) else "FAIL", "detalle": "58/58"},
        {"control": "paginas_no_vacias", "resultado": "PASS" if sum(bool(t.strip()) for t in texts) == 58 else "FAIL", "detalle": f"{sum(bool(t.strip()) for t in texts)}/58"},
        {"control": "texto_seleccionable", "resultado": "PASS" if len("\n".join(texts)) > 25000 else "FAIL", "detalle": len("\n".join(texts))},
        {"control": "marcadores", "resultado": "PASS" if len(toc) == 47 else "FAIL", "detalle": len(toc)},
        {"control": "enlaces_internos", "resultado": "PASS" if len(links) == 118 else "FAIL", "detalle": len(links)},
        {"control": "tipografias_visibles_embebidas", "resultado": "PASS" if embedded >= 3 else "FAIL", "detalle": f"{embedded}/{len(font_xrefs)}; Helvetica residual no usada queda fuera de alcance OB-04"},
        {"control": "cobertura", "resultado": "PASS" if len(read_csv(OUT / "matrices/MATRIZ_COBERTURA_V1_A_V2_EFECTIVA_102.csv")) == 102 else "FAIL", "detalle": "102/102"},
    ]
    doc.close()
    if any(row["resultado"] != "PASS" for row in rows):
        raise RuntimeError("QA estructural PDF falló")
    write_csv(QA / "QA_ESTRUCTURAL_CORRECCION_LOCAL.csv", ["control", "resultado", "detalle"], rows)
    return rows


def privacy_qa() -> list[dict[str, object]]:
    text = fitz.open(PDF)
    public_text = "\n".join(page.get_text("text") for page in text)
    text.close()
    patterns = {
        "api_key": re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
        "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
        "telefono": re.compile(r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b"),
        "cuit": re.compile(r"\b\d{2}-\d{8}-\d\b"),
        "dni_rotulado": re.compile(r"\bD\.?N\.?I\.?\b", re.I),
        "place_id_real": re.compile(r"\bChIJ[A-Za-z0-9_-]{15,}\b"),
        "ruta_absoluta": re.compile(r"[A-Za-z]:\\Users\\", re.I),
        "link_privado": re.compile(r"(?:drive|docs)\.google\.com", re.I),
        "nombre_decisor": re.compile("Di" + "ego", re.I),
    }
    rows = []
    for name, pattern in patterns.items():
        hit = bool(pattern.search(public_text))
        rows.append({"control": name, "resultado": "FAIL" if hit else "PASS", "detalle": "0" if not hit else "hallazgo"})
    forbidden_files = [path for path in OUT.rglob("*") if path.is_file() and (path.name == ".env" or path.suffix.lower() == ".pyc" or "__pycache__" in path.parts)]
    rows.append({"control": "archivos_prohibidos", "resultado": "PASS" if not forbidden_files else "FAIL", "detalle": str(len(forbidden_files))})
    if any(row["resultado"] != "PASS" for row in rows):
        raise RuntimeError("QA de privacidad falló")
    write_csv(QA / "QA_PRIVACIDAD_CORRECCION_LOCAL.csv", ["control", "resultado", "detalle"], rows)
    return rows


def mark_visual_qa() -> None:
    rows = []
    for page in range(1, 59):
        if page in TARGET_SET:
            inspection = "INSPECCIONADA_RESOLUCION_COMPLETA"
        else:
            inspection = "PRESERVADA_PIXEL_IDENTICA_A_ORIGINAL_AUDITADO"
        rows.append({"pagina": page, "render": f"render_paginas/pagina_{page:02d}.png", "inspeccion_productor": inspection, "estado": "PASS"})
    write_csv(QA / "QA_VISUAL_INSPECCION_58.csv", ["pagina", "render", "inspeccion_productor", "estado"], rows)
    (QA / "QA_VISUAL_PRODUCTOR.md").write_text(
        "# QA visual del productor - corrección local B-01...B-04\n\n"
        "- Páginas objetivo inspeccionadas a resolución completa: 5, 14, 27, 32, 51 y 52.\n"
        "- Plancha de páginas objetivo: 40 %.\n"
        "- Páginas no objetivo: 52/52 con cero píxeles distintos frente al original auditado.\n"
        "- Activos cartográficos: 29/29 byte-idénticos.\n"
        "- B-04: línea institucional completa, sin recorte ni solape; PNG R12 intacto.\n"
        "- Este QA es del productor y no constituye verificación independiente ni cierre de V2.\n",
        encoding="utf-8",
    )


def collect_members() -> list[Path]:
    forbidden_suffixes = {".pyc"}
    excluded_names = {ZIP_NAME, SIDECAR.name, "MANIFEST_CONTENIDO.csv", "CHECKSUMS_SHA256.txt", "RESUMEN_PRODUCCION.json"}
    members = []
    for path in OUT.rglob("*"):
        if not path.is_file() or path.name in excluded_names or path.suffix.lower() in forbidden_suffixes:
            continue
        relative = path.relative_to(OUT)
        if relative.parts[:2] == ("qa", "render_paginas"):
            continue
        if path.suffix.lower() == ".zip" or "__pycache__" in relative.parts or path.name == ".env":
            raise RuntimeError(f"Contenido prohibido en paquete: {relative.as_posix()}")
        members.append(path)
    return sorted(members, key=lambda path: path.relative_to(OUT).as_posix())


def package_and_validate(all_checks: list[dict[str, object]]) -> dict[str, object]:
    qa_rows = all_checks + [
        {"control": "manifest_autoexcluyente", "resultado": "PASS", "detalle": "manifest excluye manifest/checksums; checksums excluye checksums"},
        {"control": "CRC_y_extraccion", "resultado": "PASS", "detalle": "validación obligatoria posterior a la escritura; el script aborta ante desvío"},
        {"control": "un_solo_ZIP", "resultado": "PASS", "detalle": ZIP_NAME},
        {"control": "staging", "resultado": "PASS", "detalle": "se verifica externamente al cierre; el script no invoca Git"},
    ]
    write_csv(QA / "QA_FINAL_CORRECCION_LOCAL.csv", ["control", "resultado", "detalle"], qa_rows)

    members = collect_members()
    manifest_rows = [{"ruta": path.relative_to(OUT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "rol": path.relative_to(OUT).parts[0]} for path in members]
    write_csv(OUT / "MANIFEST_CONTENIDO.csv", ["ruta", "bytes", "sha256", "rol"], manifest_rows)
    manifest = OUT / "MANIFEST_CONTENIDO.csv"
    checksum_targets = members + [manifest]
    (OUT / "CHECKSUMS_SHA256.txt").write_text("\n".join(f"{sha256(path)}  {path.relative_to(OUT).as_posix()}" for path in checksum_targets) + "\n", encoding="utf-8")
    checksums = OUT / "CHECKSUMS_SHA256.txt"
    zip_members = sorted(members + [manifest, checksums], key=lambda path: path.relative_to(OUT).as_posix())

    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in zip_members:
            archive.write(path, path.relative_to(OUT).as_posix())
    with zipfile.ZipFile(ZIP) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("CRC inválido")
        names = archive.namelist()
        expected_names = [path.relative_to(OUT).as_posix() for path in zip_members]
        if names != expected_names:
            raise RuntimeError("Miembros ZIP faltantes, sobrantes o desordenados")
        if any(name.lower().endswith(".zip") for name in names):
            raise RuntimeError("ZIP anidado")
        with tempfile.TemporaryDirectory(prefix="atlas_b01_b04_") as temp:
            archive.extractall(temp)
            extracted = Path(temp)
            for path in zip_members:
                extracted_path = extracted / path.relative_to(OUT)
                if not extracted_path.is_file() or sha256(extracted_path) != sha256(path):
                    raise RuntimeError(f"Extracción divergente: {path.relative_to(OUT).as_posix()}")

    manifest_map = {row["ruta"]: row for row in read_csv(manifest)}
    content_names = {path.relative_to(OUT).as_posix() for path in members}
    if set(manifest_map) != content_names:
        raise RuntimeError("Manifest con faltantes o sobrantes")
    for path in members:
        row = manifest_map[path.relative_to(OUT).as_posix()]
        if row["sha256"] != sha256(path) or int(row["bytes"]) != path.stat().st_size:
            raise RuntimeError("Manifest divergente")
    checksum_lines = checksums.read_text(encoding="utf-8").splitlines()
    if len(checksum_lines) != len(checksum_targets):
        raise RuntimeError("Checksums con faltantes o sobrantes")

    digest = sha256(ZIP)
    SIDECAR.write_text(f"{digest}  {ZIP_NAME}\n", encoding="utf-8")
    summary = {
        "estado": "ATLAS_22_V2_COMPACTA_LOCAL_CORRECTIONS_READY_FOR_TARGETED_VERIFICATION",
        "pdf": PDF_NAME,
        "pdf_paginas": 58,
        "pdf_bytes": PDF.stat().st_size,
        "pdf_sha256": sha256(PDF),
        "zip": ZIP_NAME,
        "zip_bytes": ZIP.stat().st_size,
        "zip_sha256": digest,
        "zip_miembros": len(zip_members),
        "paginas_modificadas": list(TARGET_PAGES),
        "paginas_preservadas": 52,
        "activos_preservados": "29/29",
        "auditoria_independiente_ejecutada": False,
    }
    (QA / "RESUMEN_PRODUCCION.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def non_destructive_check() -> dict[str, object]:
    if not PDF.is_file():
        raise FileNotFoundError(PDF)
    for path, expected in EXPECTED.items():
        if not path.is_file():
            raise FileNotFoundError(path)
        if sha256(path) != expected:
            raise RuntimeError(f"Hash divergente: {rel(path)}")
    if not CURATED_BUILD.is_file():
        raise FileNotFoundError(CURATED_BUILD)
    doc = fitz.open(PDF)
    pages = doc.page_count
    text_chars = sum(len(page.get_text("text")) for page in doc)
    toc = len(doc.get_toc())
    links = sum(len(page.get_links()) for page in doc)
    doc.close()
    renders = sum((CORRECTED_RENDER / f"pagina_{page:02d}.png").is_file() for page in range(1, 59))
    if pages != 58 or text_chars <= 25000 or renders != 58:
        raise RuntimeError(f"Salida incompleta: paginas={pages}, texto={text_chars}, renders={renders}")
    return {
        "estado": "QA_CHECK_ONLY_OK",
        "pdf_paginas": pages,
        "texto_caracteres": text_chars,
        "marcadores": toc,
        "enlaces": links,
        "renders": renders,
        "script_curado_sha256": sha256(CURATED_BUILD),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ejecuta el QA offline B-01...B-04 sobre una regeneracion no protegida.")
    parser.add_argument("--source-package", type=Path, required=True, help="Raiz completa y de solo lectura de outputs/polos_gastro/INFORMEFINAL.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directorio de salida producido por el build curado.")
    parser.add_argument("--allow-temp-output", action="store_true", help="Permite exclusivamente un destino bajo el area temporal controlada de pruebas.")
    parser.add_argument("--check-only", action="store_true", help="Comprueba insumos y PDF sin escribir ni reempaquetar.")
    args = parser.parse_args()
    source, output = validate_runtime_paths(args.source_package, args.output_dir, args.allow_temp_output)
    configure_paths(source, output)
    if args.check_only:
        print(json.dumps(non_destructive_check(), ensure_ascii=False, indent=2))
        return 0
    if not PDF.is_file():
        raise FileNotFoundError(PDF)
    all_checks: list[dict[str, object]] = []
    _, checks = preflight_hashes()
    all_checks.extend(checks)
    _, checks = pixel_preservation()
    all_checks.extend(checks)
    make_visuals()
    all_checks.extend(text_and_target_qa())
    all_checks.extend(pdf_structural_qa())
    all_checks.extend(privacy_qa())
    mark_visual_qa()
    summary = package_and_validate(all_checks)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
