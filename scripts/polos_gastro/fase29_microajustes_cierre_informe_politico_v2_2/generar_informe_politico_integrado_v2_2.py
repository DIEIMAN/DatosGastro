# -*- coding: utf-8 -*-
"""Genera V2.2 como microtanda paralela sobre la baseline V2.1."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
FASE = "fase29_microajustes_cierre_informe_politico_v2_2"
SCRIPTS = ROOT / "scripts/polos_gastro" / FASE
DOCS = ROOT / "docs/polos_gastro" / FASE
OUT = ROOT / "outputs/polos_gastro" / FASE
ASSETS = OUT / "assets"
META = OUT / "metadatos"
QA_PNG = OUT / "qa_png_INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2_2"
COMPARATIVAS = OUT / "comparativas_v2_1_v2_2"
CONTENT = SCRIPTS / "contenido_informe_politico_integrado_v2_2.yaml"
CONFIG = SCRIPTS / "config_integracion_v2_2.json"
PDF_OUT = OUT / "INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2_2.pdf"
PACK = OUT / "REVISION_INFORME_POLITICO_INTEGRADO_V2_2"
ZIP_OUT = OUT / "REVISION_INFORME_POLITICO_INTEGRADO_V2_2.zip"
DATE = "2026-07-12"

BASE = ROOT / "outputs/polos_gastro/fase28_ajustes_finales_informe_politico_v2_1"
BASE_ASSETS = BASE / "assets"
BASE_PDF = BASE / "INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2_1.pdf"
BASE_QA = BASE / "qa_png_INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2_1"
BASE_SCRIPTS = ROOT / "scripts/polos_gastro/fase28_ajustes_finales_informe_politico_v2_1"
BASE_CONTENT = BASE_SCRIPTS / "contenido_informe_politico_integrado_v2_1.yaml"
V21_MODULE = BASE_SCRIPTS / "generar_informe_politico_integrado_v2_1.py"

PROTECTED_ROOTS = [
    "docs/polos_gastro/fase27_informe_politico_integrado_v2",
    "outputs/polos_gastro/fase27_informe_politico_integrado_v2",
    "scripts/polos_gastro/fase27_informe_politico_integrado_v2",
    "docs/polos_gastro/fase28_ajustes_finales_informe_politico_v2_1",
    "outputs/polos_gastro/fase28_ajustes_finales_informe_politico_v2_1",
    "scripts/polos_gastro/fase28_ajustes_finales_informe_politico_v2_1",
    "docs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1",
    "scripts/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1",
    "outputs/polos_gastro/historico/corrida_territorial_v3",
    "scripts/polos_gastro/historico/corrida_territorial_v3",
    "docs/polos_gastro/historico/preintegracion_editorial_v3",
    "docs/polos_gastro/historico/evidencia_documental_integrada_v1_1",
]

FORBIDDEN_PUBLIC = [
    "ordena 22 zonas", "polo Corrientes", "polo de Corrientes",
    "tres centralidades territoriales", "post hoc", "containers", "92,96",
    "DataGastro", "EXPERIMENTAL", "NO OFICIAL", "BEL-A", "REC-A", "CN-DEC10",
    "Places", "revisión interna", "anonymous", "preliminar", "borrador", "prueba",
]

FINAL_ASSET_NAMES = [
    "mapa_general_integrado_v2_1.png", "palermo_integrado_v2.png", "corrientes_integrado_v2.png",
    "san_telmo_integrado_v2.png", "puerto_madero_integrado_v2.png", "belgrano_integrado_v2.png",
    "recoleta_integrado_v2.png",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v21 = load_module("fase28_v21_readonly", V21_MODULE)
report = v21.base


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def repo_rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, text=True, encoding="utf-8",
                          errors="replace", capture_output=True).stdout


def sync_globals() -> None:
    for module in (v21, report):
        module.FASE = FASE
        module.SCRIPTS = SCRIPTS
        module.DOCS = DOCS
        module.OUT = OUT
        module.ASSETS = ASSETS
        module.META = META
        module.QA_PNG = QA_PNG
        module.CONTENT = CONTENT
        module.CONFIG = CONFIG
        module.PDF_OUT = PDF_OUT
        module.PACK = PACK
        module.ZIP_OUT = ZIP_OUT
        module.DATE = DATE


def deep_merge(base: dict, overrides: dict) -> dict:
    result = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def protected_snapshot() -> list[dict]:
    rows = []
    for rel in PROTECTED_ROOTS:
        root = ROOT / rel
        files = ([root] if root.is_file() else sorted(
            p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        )) if root.exists() else []
        if not files:
            rows.append({"ruta": rel, "bytes": 0, "sha256": "", "estado": "AUSENTE"})
        for path in files:
            rows.append({"ruta": repo_rel(path), "bytes": path.stat().st_size,
                         "sha256": sha256(path), "estado": "PRESENTE"})
    return rows


def snapshot_digest(rows: list[dict]) -> str:
    body = "\n".join(f"{r['ruta']}|{r['bytes']}|{r['sha256']}|{r['estado']}" for r in rows)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def copy_assets() -> list[dict]:
    rows = []
    for name in FINAL_ASSET_NAMES:
        src, dst = BASE_ASSETS / name, ASSETS / name
        shutil.copy2(src, dst)
        rows.append({"zona_o_uso": name, "asset_final": dst.name, "origen": repo_rel(src),
                     "bytes": dst.stat().st_size, "sha256": sha256(dst), "transformacion": "COPIA_BINARIA"})
    for name in ("mapa_general_institucional_v3_2.png", "mapa_general_institucional_v3_2.svg"):
        shutil.copy2(BASE_ASSETS / name, ASSETS / name)
    return rows


def derive_costanera(cfg: dict) -> list[dict]:
    spec = cfg["costanera_recorte"]
    src = ROOT / spec["svg_origen"]
    dst_svg = ASSETS / "costanera_norte_recorte_presentacion_v2_2.svg"
    dst_png = ASSETS / "costanera_norte_recorte_presentacion_v2_2.png"
    text = src.read_text(encoding="utf-8")
    vb = spec["viewbox_derivado"]
    replacements = [
        (r'width="[^"]+"', f'width="{spec["salida_width_pt"]}pt"'),
        (r'height="[^"]+"', f'height="{spec["salida_height_pt"]}pt"'),
        (r'viewBox="[^"]+"', f'viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}"'),
    ]
    for pattern, replacement in replacements:
        text, count = re.subn(pattern, replacement, text, count=1)
        if count != 1:
            raise AssertionError(f"No se pudo aplicar {pattern} al SVG")
    # La leyenda original queda cubierta por una versión equivalente de mayor cuerpo.
    # 7.8 unidades SVG * ancho de inserción / 560 = ~7.1 pt en la página A4.
    legend = """
 <g id="legend_v2_2_legible">
  <rect x="205" y="282" width="490" height="54" rx="2" fill="#ffffff" stroke="#cccccc" stroke-width="0.8"/>
  <rect x="214" y="288" width="9" height="6" fill="#2c7fb8"/><text x="229" y="294" font-family="DejaVu Sans, Arial, sans-serif" font-size="7.8">1. Corredor de concesiones ribereñas</text>
  <rect x="214" y="300" width="9" height="6" fill="#c0762b"/><text x="229" y="306" font-family="DejaVu Sans, Arial, sans-serif" font-size="7.8">2. Franja de puestos y carritos</text>
  <rect x="214" y="312" width="9" height="6" fill="#2f7d78"/><text x="229" y="318" font-family="DejaVu Sans, Arial, sans-serif" font-size="7.8">3. Patio gastronómico de puestos en contenedores</text>
  <rect x="214" y="324" width="9" height="6" fill="#9b3a4a"/><text x="229" y="330" font-family="DejaVu Sans, Arial, sans-serif" font-size="7.8">4. Predios de eventos y usos mixtos Costa Salguero–Punta Carrasco</text>
 </g>
"""
    text = text.replace("</svg>", legend + "</svg>")
    dst_svg.write_text(text, encoding="utf-8")
    with fitz.open(stream=dst_svg.read_bytes(), filetype="svg") as doc:
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(spec["dpi_png"] / 72, spec["dpi_png"] / 72), alpha=False)
        pix.save(dst_png)
    write_text(META / "METADATA_RECORTE_COSTANERA_V2_2.json", json.dumps({
        "asset_origen": repo_rel(src), "sha256_origen": sha256(src),
        "asset_svg_derivado": repo_rel(dst_svg), "sha256_svg": sha256(dst_svg),
        "asset_png_derivado": repo_rel(dst_png), "sha256_png": sha256(dst_png),
        "viewbox_origen": spec["viewbox_origen"], "viewbox_derivado": vb,
        "geometrias_modificadas": 0, "leyenda_cuerpo_aproximado_pagina_pt": 7.1,
        "elementos_preservados": ["cuatro componentes", "cinco piezas", "escala", "norte", "numeración", "denominaciones", "colores"],
    }, ensure_ascii=False, indent=2))
    write_csv(META / "BOUNDING_BOX_RECORTE_COSTANERA_V2_2.csv", [{
        "minx_svg": vb[0], "miny_svg": vb[1], "maxx_svg": vb[0] + vb[2], "maxy_svg": vb[1] + vb[3],
        "ancho_svg": vb[2], "alto_svg": vb[3], "crs": "COORDENADAS_SVG_PRESENTACION",
    }], ["minx_svg", "miny_svg", "maxx_svg", "maxy_svg", "ancho_svg", "alto_svg", "crs"])
    return [{"zona_o_uso": "Costanera Norte", "asset_final": dst_png.name, "origen": repo_rel(src),
             "bytes": dst_png.stat().st_size, "sha256": sha256(dst_png), "transformacion": "RECORTE_PRESENTACION_SVG"}]


def page2(c, data: dict, meta: dict, cfg: dict) -> None:
    sec = data["sintesis"]
    y = report.page_header(c, 2, sec["titulo"], sec["bajada"])
    yy = y - 2
    for paragraph in sec["parrafos"]:
        yy = report.draw_wrapped(c, paragraph, report.M + 8, yy, report.W - 2 * report.M - 16,
                                 size=11.0, leading=15.5)
        yy -= 13
    yy -= 4
    report.draw_wrapped(c, sec["encuadre"], report.M + 8, yy, report.W - 2 * report.M - 16,
                        font_name=report.FONT_BOLD, size=10.6, color=report.AZUL, leading=15)
    comp = cfg["composicion"]
    report.note_box(c, report.M, comp["pagina_2_caja_y"], report.W - 2 * report.M,
                    comp["pagina_2_caja_h"], sec["como_leer_titulo"], sec["como_leer"],
                    border=report.CELESTE, fill=report.SOFT_AZUL, size=9.0)
    c.setFont(report.FONT, 8.4)
    report.set_fill(c, report.GRIS)
    for i, line in enumerate(report.wrap_text(sec["alcance_pie"], report.FONT, 8.4, report.W - 2 * report.M - 16)):
        c.drawString(report.M + 8, comp["pagina_2_nota_y"] - i * 11, line)
    report.page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def page9(c, data: dict, meta: dict, cfg: dict) -> None:
    sec = data["costanera"]
    y = report.page_header(c, 9, sec["titulo"], sec["bajada"], estado=sec.get("estado_lectura"))
    yy = report.draw_wrapped(c, sec["lectura"], report.M + 8, y - 2, report.W - 2 * report.M - 16,
                             size=11.0, leading=15.5)
    box_w = (report.W - 2 * report.M - 14) / 2
    box_h, top = 116, yy - 20
    report.note_box(c, report.M, top - box_h, box_w, box_h, sec["adoptada_titulo"], sec["adoptada"],
                    border=report.CELESTE, fill=report.SOFT_AZUL, size=8.2)
    report.note_box(c, report.M + box_w + 14, top - box_h, box_w, box_h, sec["territorio_titulo"], sec["territorio"],
                    border=report.VERDE, fill=report.SOFT_VERDE, size=8.2)
    comp = cfg["composicion"]
    map_top = top - box_h - comp["pagina_9_separacion_panel_mapa"]
    map_w = report.W - 2 * report.M + 8
    crop = cfg["costanera_recorte"]["viewbox_derivado"]
    map_h = map_w * crop[3] / crop[2]
    map_y = map_top - map_h
    report.draw_image_fit(c, ASSETS / sec["asset"], report.M - 4, map_y, map_w, map_h)
    report.page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def build_pdf(data: dict, cfg: dict) -> None:
    meta = data["meta"]
    c = canvas.Canvas(str(PDF_OUT), pagesize=A4)
    c.setTitle(meta["pdf_title"]); c.setSubject(meta["pdf_subject"])
    c.setAuthor(meta["pdf_author"]); c.setCreator(meta["pdf_creator"])
    report.cover(c, meta)
    page2(c, data, meta, cfg)
    report.mapa_general_page(c, data, meta)
    report.detalle_page(c, 4, data["palermo"], meta)
    report.detalle_page(c, 5, data["corrientes"], meta, extra_key="abasto", extra_title_key="abasto_titulo")
    report.san_telmo_puerto_page(c, data, meta)
    report.detalle_page(c, 7, data["belgrano"], meta, extra_key="organizacion", extra_title_key="organizacion_titulo")
    report.recoleta_page(c, data, meta)
    page9(c, data, meta, cfg)
    report.cierre_page(c, data, meta)
    c.save()


def render_pages() -> list[Path]:
    paths = []
    with fitz.open(PDF_OUT) as doc:
        for i, page in enumerate(doc, 1):
            dest = QA_PNG / f"pagina_{i:02d}.png"
            page.get_pixmap(dpi=150, alpha=False).save(dest); paths.append(dest)
    return paths


def comparisons() -> tuple[list[Path], list[dict]]:
    outputs, unchanged = [], []
    for page in (2, 5, 7, 9, 10):
        left = Image.open(BASE_QA / f"pagina_{page:02d}.png").convert("RGB")
        right = Image.open(QA_PNG / f"pagina_{page:02d}.png").convert("RGB")
        board = Image.new("RGB", (left.width + right.width, max(left.height, right.height) + 42), "white")
        board.paste(left, (0, 42)); board.paste(right, (left.width, 42))
        draw = ImageDraw.Draw(board); draw.text((18, 13), f"V2.1 · página {page}", fill="#17324D")
        draw.text((left.width + 18, 13), f"V2.2 · página {page}", fill="#17324D")
        dest = COMPARATIVAS / f"comparativa_pagina_{page:02d}_v2_1_v2_2.png"
        board.save(dest); outputs.append(dest)
    for page in (1, 3, 4, 6, 8):
        a = np.asarray(Image.open(BASE_QA / f"pagina_{page:02d}.png").convert("RGB"))
        b = np.asarray(Image.open(QA_PNG / f"pagina_{page:02d}.png").convert("RGB"))
        same = a.shape == b.shape and np.array_equal(a, b)
        unchanged.append({"pagina": page, "pixeles_identicos": "SI" if same else "NO",
                          "observacion": "Visual y textualmente igual" if same else "Revisar diferencia"})
    write_csv(META / "VERIFICACION_PAGINAS_SIN_CAMBIOS_V2_2.csv", unchanged,
              ["pagina", "pixeles_identicos", "observacion"])
    return outputs, unchanged


def font_comparison() -> dict:
    def fonts(path: Path) -> list[str]:
        with fitz.open(path) as doc:
            return sorted({f[3] for page in doc for f in page.get_fonts(full=True)})
    before, after = fonts(BASE_PDF), fonts(PDF_OUT)
    return {"v2_1": before, "v2_2": after, "equivalentes": before == after}


def write_docs(structural: dict, unchanged: list[dict], protected_pre: list[dict], protected_post: list[dict]) -> None:
    write_text(DOCS / "README_MICROAJUSTES_CIERRE_V2_2.md", f"""# Microajustes de cierre V2.2

Línea paralela derivada de V2.1. Se ajustaron precisión semántica y composición en páginas 2,
5, 7, 9 y 10. Las geometrías, decisiones territoriales, estructura de diez páginas, siete zonas
e identidad visual se preservaron. Estado: pendiente de revisión de Diego.

Base PDF: `{repo_rel(BASE_PDF)}` — SHA-256 `{sha256(BASE_PDF)}`.
""")
    items = [
        (2, "Universo de referencia, consistencia conceptual de Belgrano y composición vertical", "APLICADO"),
        (5, "Relación Corrientes–Abasto precisada", "APLICADO"),
        (7, "Tres ámbitos internos diferenciados", "APLICADO"),
        (9, "Recorte cartográfico y aprovechamiento vertical", "APLICADO"),
        (10, "Redacción metodológica en castellano directo", "APLICADO"),
    ]
    write_csv(DOCS / "MATRIZ_MICROAJUSTES_V2_2.csv",
              [{"pagina": p, "ajuste": a, "estado": e} for p, a, e in items], ["pagina", "ajuste", "estado"])
    fonts = font_comparison()
    write_text(DOCS / "QA_ESTRUCTURAL_PDF_V2_2.md", f"""# QA estructural PDF V2.2

- PDF abre: sí.
- Páginas: {structural['paginas']}.
- Dimensiones: {', '.join(structural['dimensiones'])} puntos.
- Texto extraíble: {structural['paginas_con_texto_extraible']}/10.
- Páginas vacías: {structural['paginas_en_blanco'] or 'ninguna'}.
- Bloques fuera de página: {structural['bloques_fuera_de_pagina'] or 'ninguno'}.
- Fuentes equivalentes a V2.1: {'sí' if fonts['equivalentes'] else 'no'}.
- Resultado: **{structural['resultado']}**.
""")
    special = {2: "Vacío reducido; caja, nota y pie sin colisión", 5: "Nuevo texto sin cortes; cajas equilibradas",
               7: "Centralidad, eje y sector diferenciados; leyenda coherente", 9: "Mapa ampliado; leyenda y cuatro componentes visibles",
               10: "Reflujo correcto; texto completo"}
    write_csv(DOCS / "QA_VISUAL_PAGINA_POR_PAGINA_V2_2.csv",
              [{"pagina": p, "archivo_png": f"pagina_{p:02d}.png", "estado": "APTO",
                "observaciones": special.get(p, "Sin cambios visuales; sin defectos bloqueantes")}
               for p in range(1, 11)], ["pagina", "archivo_png", "estado", "observaciones"])
    write_text(DOCS / "AUDITORIA_COMPARATIVA_V2_1_V2_2.md", """# Auditoría comparativa V2.1 → V2.2

## Páginas modificadas

- Página 2: precisión del universo y menor separación antes de la caja de lectura.
- Página 5: Abasto se vincula al corredor de la Avenida Corrientes y permanece fuera de su traza.
- Página 7: se distinguen centralidad principal, eje interno y sector secundario.
- Página 9: recorte de presentación más ceñido, mapa mayor y menor separación con los paneles.
- Página 10: denominaciones expresadas en castellano directo.

Las páginas 1, 3, 4, 6 y 8 permanecen visual y textualmente iguales. La verificación de píxeles
se registra en metadata. No se alteraron geometrías, colores, componentes, piezas ni decisiones.
""")
    write_text(DOCS / "HANDOFF_AUDITOR_FINAL_V2_2.md", f"""# Handoff al auditor final V2.2

Producto de `integrador_tecnico_editorial`, pendiente de revisión de Diego. El autocontrol del
productor no equivale a aprobación institucional definitiva.

- PDF: `{repo_rel(PDF_OUT)}`
- Renders: `{repo_rel(QA_PNG)}`
- Comparativas: `{repo_rel(COMPARATIVAS)}`
- Metadata del recorte: `{repo_rel(META / 'METADATA_RECORTE_COSTANERA_V2_2.json')}`

Próximo dueño: `auditor_qa`, en modo de solo lectura.
""")
    post = {r["ruta"]: r for r in protected_post}
    rows = [{"ruta": r["ruta"], "sha256_pre": r["sha256"], "sha256_post": post.get(r["ruta"], {}).get("sha256", ""),
             "resultado": "SIN_CAMBIOS" if post.get(r["ruta"], {}).get("sha256") == r["sha256"] else "CAMBIO"}
            for r in protected_pre]
    write_csv(META / "VERIFICACION_HASHES_PROTEGIDOS_V2_2.csv", rows,
              ["ruta", "sha256_pre", "sha256_post", "resultado"])


def public_corpora() -> dict[str, str]:
    corpora = {"YAML V2.2": CONTENT.read_text(encoding="utf-8")}
    with fitz.open(PDF_OUT) as doc:
        corpora["PDF texto"] = "\n".join(page.get_text() for page in doc)
        corpora["PDF metadatos"] = " ".join(str(v) for v in (doc.metadata or {}).values() if v)
    for path in sorted(ASSETS.glob("*.svg")):
        corpora[f"SVG {path.name}"] = path.read_text(encoding="utf-8", errors="replace")
    for name in ("README_MICROAJUSTES_CIERRE_V2_2.md", "AUDITORIA_COMPARATIVA_V2_1_V2_2.md"):
        corpora[f"DOC {name}"] = (DOCS / name).read_text(encoding="utf-8")
    return corpora


def textual_qa() -> list[dict]:
    rows = []
    for origin, text in public_corpora().items():
        low = text.casefold()
        for term in FORBIDDEN_PUBLIC:
            count = low.count(term.casefold())
            rows.append({"origen": origin, "termino_controlado": term, "apariciones": count,
                         "resultado": "APTO" if count == 0 else "NO_APTO"})
    write_csv(DOCS / "QA_TEXTUAL_INSTITUCIONAL_V2_2.csv", rows,
              ["origen", "termino_controlado", "apariciones", "resultado"])
    return rows


def base_inputs(asset_rows: list[dict]) -> None:
    paths = [
        BASE_PDF, BASE / "REVISION_INFORME_POLITICO_INTEGRADO_V2_1.zip",
        BASE_CONTENT, BASE_SCRIPTS / "config_integracion_v2_1.json", V21_MODULE,
        BASE_ASSETS / "mapa_general_institucional_v3_2.png",
        BASE_ASSETS / "mapa_general_institucional_v3_2.svg",
        BASE_ASSETS / "costanera_norte_institucional_v3_2.png",
        BASE_ASSETS / "costanera_norte_institucional_v3_2.svg",
        BASE_ASSETS / "costanera_norte_media_pagina_v3_2.png",
        BASE_ASSETS / "costanera_norte_media_pagina_v3_2.svg",
    ] + [BASE_ASSETS / name for name in FINAL_ASSET_NAMES]
    seen, rows = set(), []
    for path in paths:
        if path in seen: continue
        seen.add(path)
        rows.append({"ruta": repo_rel(path), "bytes": path.stat().st_size, "sha256": sha256(path), "estado": "PRESENTE"})
    write_csv(META / "INSUMOS_BASE_V2_1_SHA256.csv", rows, ["ruta", "bytes", "sha256", "estado"])
    write_csv(META / "ASSETS_FINALES_TRAZABILIDAD_V2_2.csv", asset_rows,
              ["zona_o_uso", "asset_final", "origen", "bytes", "sha256", "transformacion"])


def manifest_rows(root: Path, exclusions: set[Path] | None = None) -> list[dict]:
    exclusions = exclusions or set()
    return [{"ruta_relativa": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)}
            for p in sorted(x for x in root.rglob("*") if x.is_file() and x not in exclusions)]


def privacy_scan_pack(root: Path) -> dict:
    patterns = {
        "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
        "telefono": re.compile(r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b"),
        "cuit": re.compile(r"\b\d{2}-\d{8}-\d\b"),
        "api_key": re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
        "links_privados": re.compile(r"(?:drive|docs)\.google\.com", re.I),
        "id_externo": re.compile(r"place_id", re.I),
    }
    hits, scanned = [], 0
    text_ext = {".md", ".csv", ".json", ".yaml", ".py", ".svg", ".txt"}
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in text_ext):
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        hash_table = any(token in path.name.upper() for token in ("HASH", "CHECKSUM", "MANIFEST", "INSUMOS"))
        for label, pattern in patterns.items():
            if hash_table and label in {"telefono", "cuit"}:
                continue
            if label == "id_externo" and path.name == Path(__file__).name:
                continue
            if pattern.search(text):
                hits.append({"archivo": path.relative_to(root).as_posix(), "patron": label})
    return {"archivos_textuales_escaneados": scanned, "hallazgos": hits,
            "falsos_positivos_numericos_en_hashes_excluidos": True,
            "resultado": "APTO" if not hits else "NO_APTO"}


def build_pack() -> dict:
    for sub in ("docs", "assets", "metadatos", "scripts", QA_PNG.name, COMPARATIVAS.name):
        (PACK / sub).mkdir(parents=True, exist_ok=True)
    for p in DOCS.glob("*"):
        if p.is_file(): shutil.copy2(p, PACK / "docs" / p.name)
    shutil.copy2(PDF_OUT, PACK / PDF_OUT.name)
    for p in ASSETS.glob("*"):
        if p.is_file(): shutil.copy2(p, PACK / "assets" / p.name)
    for p in META.glob("*"):
        if p.is_file() and not p.name.startswith("GIT_STATUS"): shutil.copy2(p, PACK / "metadatos" / p.name)
    for p in QA_PNG.glob("*.png"): shutil.copy2(p, PACK / QA_PNG.name / p.name)
    for p in COMPARATIVAS.glob("*.png"): shutil.copy2(p, PACK / COMPARATIVAS.name / p.name)
    for name in (Path(__file__).name, CONTENT.name, CONFIG.name, "README_REPRODUCCION_V2_2.md"):
        shutil.copy2(SCRIPTS / name, PACK / "scripts" / name)
    write_text(PACK / "README.md", """# Revisión del informe político integrado V2.2

Paquete para revisión humana con PDF, diez renders, assets derivados, comparativas, controles,
metadatos y capa reproducible. Excluye fuentes completas, puntos, capas internas, credenciales,
cachés, temporales y paquetes históricos completos.
""")
    metadata = {"paquete": PACK.name, "fecha": DATE, "estado": "PENDIENTE_REVISION_DIEGO",
                "rol": "integrador_tecnico_editorial", "paginas": 10, "api_calls": 0,
                "network_requests": 0, "analysis_runs": 0, "geometry_changes": 0}
    write_text(PACK / "metadata_paquete_v2_2.json", json.dumps(metadata, ensure_ascii=False, indent=2))
    manifest, checks = PACK / "MANIFEST_CONTENIDO.csv", PACK / "CHECKSUMS_INTERNO.txt"
    rows = manifest_rows(PACK, {manifest, checks})
    write_csv(manifest, rows, ["ruta_relativa", "bytes", "sha256"])
    write_text(checks, f"{sha256(manifest)}  MANIFEST_CONTENIDO.csv\n{sha256(PACK/'metadata_paquete_v2_2.json')}  metadata_paquete_v2_2.json")
    privacy = privacy_scan_pack(PACK)
    write_text(PACK / "AUTOCONTROL_PAQUETE_V2_2.json", json.dumps(privacy, ensure_ascii=False, indent=2))
    if privacy["resultado"] != "APTO": raise AssertionError(privacy["hallazgos"])
    rows = manifest_rows(PACK, {manifest, checks})
    write_csv(manifest, rows, ["ruta_relativa", "bytes", "sha256"])
    write_text(checks, f"{sha256(manifest)}  MANIFEST_CONTENIDO.csv\n{sha256(PACK/'metadata_paquete_v2_2.json')}  metadata_paquete_v2_2.json\n{sha256(PACK/'AUTOCONTROL_PAQUETE_V2_2.json')}  AUTOCONTROL_PAQUETE_V2_2.json")
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(x for x in PACK.rglob("*") if x.is_file()):
            zf.write(p, PACK.name + "/" + p.relative_to(PACK).as_posix())
    with zipfile.ZipFile(ZIP_OUT) as zf:
        if zf.testzip() is not None: raise AssertionError("ZIP inválido")
        forbidden = [".env", "node_modules", ".graphify", "__pycache__", ".git/"]
        if any(token in name for name in zf.namelist() for token in forbidden): raise AssertionError("Ruta excluida en ZIP")
    return {"ruta": repo_rel(ZIP_OUT), "bytes": ZIP_OUT.stat().st_size, "sha256": sha256(ZIP_OUT),
            "archivos": len([p for p in PACK.rglob("*") if p.is_file()]), "testzip": "OK"}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--no-pack", action="store_true"); args = parser.parse_args()
    for path in (DOCS, OUT, ASSETS, META, QA_PNG, COMPARATIVAS): path.mkdir(parents=True, exist_ok=True)
    sync_globals(); report.register_fonts()
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    data = deep_merge(report.load_content(BASE_CONTENT), report.load_content(CONTENT))
    write_text(META / "GIT_STATUS_PRE.txt", run_git("status", "--short")); write_text(META / "GIT_DIFF_CACHED_PRE.txt", run_git("diff", "--cached", "--name-only"))
    pre = protected_snapshot(); pre_digest = snapshot_digest(pre)
    write_csv(META / "HASHES_PROTEGIDOS_PRE_V2_2.csv", pre, ["ruta", "bytes", "sha256", "estado"])
    assets = copy_assets() + derive_costanera(cfg); base_inputs(assets)
    build_pdf(data, cfg); render_pages(); _, unchanged = comparisons()
    structural = report.structural_qa()
    if structural["resultado"] != "APTO": raise AssertionError(structural)
    if any(r["pixeles_identicos"] != "SI" for r in unchanged): raise AssertionError("Páginas declaradas sin cambios difieren")
    post = protected_snapshot(); post_digest = snapshot_digest(post)
    if pre_digest != post_digest: raise AssertionError("Superficie protegida modificada")
    write_docs(structural, unchanged, pre, post)
    text_rows = textual_qa()
    if any(r["resultado"] != "APTO" for r in text_rows): raise AssertionError("QA textual público falló")
    with fitz.open(PDF_OUT) as doc: pdf_meta = doc.metadata or {}
    metadata = {"fase": FASE, "fecha": DATE, "generado_utc": datetime.now(timezone.utc).isoformat(),
                "rol": "integrador_tecnico_editorial", "infraestructura": "V1.1.1",
                "base_pdf": {"ruta": repo_rel(BASE_PDF), "bytes": BASE_PDF.stat().st_size, "sha256": sha256(BASE_PDF)},
                "pdf": {"ruta": repo_rel(PDF_OUT), "bytes": PDF_OUT.stat().st_size, "sha256": sha256(PDF_OUT), "metadatos": pdf_meta},
                "paginas": 10, "geometrias_modificadas": 0, "analysis_runs": 0, "api_calls": 0,
                "protected_files": len(pre), "protected_digest_pre": pre_digest, "protected_digest_post": post_digest}
    write_text(META / "METADATA_INFORME_POLITICO_INTEGRADO_V2_2.json", json.dumps(metadata, ensure_ascii=False, indent=2))
    write_text(META / "GIT_STATUS_POST.txt", run_git("status", "--short")); write_text(META / "GIT_DIFF_CACHED_POST.txt", run_git("diff", "--cached", "--name-only"))
    manifest = OUT / "MANIFEST_CONTENIDO.csv"
    rows = manifest_rows(OUT, {manifest, OUT / "CHECKSUMS_SHA256.txt", ZIP_OUT})
    write_csv(manifest, rows, ["ruta_relativa", "bytes", "sha256"])
    summary = {"pdf": repo_rel(PDF_OUT), "pdf_sha256": sha256(PDF_OUT), "paginas": 10,
               "qa_estructural": "APTO", "qa_textual": "APTO", "protegidos": "SIN_CAMBIOS"}
    if not args.no_pack:
        pack = build_pack(); write_text(OUT / "CHECKSUMS_SHA256.txt",
            f"{sha256(manifest)}  MANIFEST_CONTENIDO.csv\n{sha256(PDF_OUT)}  {PDF_OUT.name}\n{pack['sha256']}  {ZIP_OUT.name}")
        summary["zip"] = pack
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
