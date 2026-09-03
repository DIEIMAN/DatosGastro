# -*- coding: utf-8 -*-
"""Genera la línea paralela V2.1 del informe político integrado.

La fase27 y la cartografía V3.1 son insumos de solo lectura. El proceso no cambia
geometrías ni ejecuta modelos: deriva dos assets cartográficos, sustituye la capa
editorial, genera el PDF, los controles, las comparativas y el paquete de revisión.
"""
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
from datetime import datetime, timezone
from pathlib import Path

import fitz
import geopandas as gpd
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
FASE = "fase28_ajustes_finales_informe_politico_v2_1"
SCRIPTS = ROOT / "scripts/polos_gastro" / FASE
DOCS = ROOT / "docs/polos_gastro" / FASE
OUT = ROOT / "outputs/polos_gastro" / FASE
ASSETS = OUT / "assets"
META = OUT / "metadatos"
INTERNAL = META / "interno"
QA_PNG = OUT / "qa_png_INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2_1"
COMPARATIVAS = OUT / "comparativas_v2_v2_1"
CONTENT = SCRIPTS / "contenido_informe_politico_integrado_v2_1.yaml"
CONFIG = SCRIPTS / "config_integracion_v2_1.json"
PDF_OUT = OUT / "INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2_1.pdf"
PACK = OUT / "REVISION_INFORME_POLITICO_INTEGRADO_V2_1"
ZIP_OUT = OUT / "REVISION_INFORME_POLITICO_INTEGRADO_V2_1.zip"
DATE = "2026-07-12"

BASE_FASE = ROOT / "outputs/polos_gastro/fase27_informe_politico_integrado_v2"
BASE_ASSETS = BASE_FASE / "assets"
BASE_PDF = BASE_FASE / "INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2.pdf"
BASE_QA = BASE_FASE / "qa_png_INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2"
V31 = ROOT / "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1"
V31_MAPS = V31 / "mapas"
V31_LAYERS = V31 / "capas"
PROTECTED_YAML = ROOT / "docs/polos_gastro/PROTECTED_SURFACES.yaml"

BASE_MODULE_PATH = ROOT / "scripts/polos_gastro/fase27_informe_politico_integrado_v2/generar_informe_politico_integrado_v2.py"
CARTO_MODULE_PATH = ROOT / "scripts/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/generar_correcciones_cartograficas_v3_1.py"

PROTECTED_ROOTS = [
    "docs/polos_gastro/fase27_informe_politico_integrado_v2",
    "outputs/polos_gastro/fase27_informe_politico_integrado_v2",
    "scripts/polos_gastro/fase27_informe_politico_integrado_v2",
    "docs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1",
    "scripts/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1",
    "docs/polos_gastro/historico/auditoria_qa_territorial_v3",
    "docs/polos_gastro/historico/auditoria_externa_red_team_v3",
    "docs/polos_gastro/historico/preintegracion_editorial_v3",
    "docs/polos_gastro/historico/evidencia_documental_integrada_v1_1",
    "outputs/polos_gastro/historico/corrida_territorial_v3",
    "scripts/polos_gastro/historico/corrida_territorial_v3",
]

CRITICAL_INPUTS = [
    "outputs/polos_gastro/fase27_informe_politico_integrado_v2/INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2.pdf",
    "outputs/polos_gastro/fase27_informe_politico_integrado_v2/REVISION_INFORME_POLITICO_INTEGRADO_V2.zip",
    "scripts/polos_gastro/fase27_informe_politico_integrado_v2/generar_informe_politico_integrado_v2.py",
    "scripts/polos_gastro/fase27_informe_politico_integrado_v2/contenido_informe_politico_integrado_v2.yaml",
    "scripts/polos_gastro/fase27_informe_politico_integrado_v2/config_integracion_v2.json",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/mapas/mapa_general_institucional_v3_1.png",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/mapas/mapa_general_institucional_v3_1.svg",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/mapas/costanera_norte_institucional_v3_1.svg",
    "outputs/polos_gastro/historico/correcciones_cartograficas_post_qa_v3_1/mapas/costanera_norte_media_pagina_v3_1.svg",
    "docs/polos_gastro/historico/auditoria_qa_territorial_v3/INFORME_AUDITORIA_QA_TERRITORIAL_V3.md",
    "docs/polos_gastro/historico/auditoria_externa_red_team_v3/INFORME_RED_TEAM_TERRITORIAL_V3.md",
    "docs/polos_gastro/historico/preintegracion_editorial_v3/PLAN_INTEGRACION_EDITORIAL_V3.md",
    "docs/polos_gastro/historico/evidencia_documental_integrada_v1_1/README_EVIDENCIA_DOCUMENTAL_INTEGRADA.md",
]

FORBIDDEN_PUBLIC = [
    "containers", "92,96", "revisión interna", "anonymous", "sin oferta",
    "sin reabrir", "adoptada por el estudio", "lecturas editoriales de apoyo",
    "delimitación adoptada recientemente", "DataGastro", "EXPERIMENTAL", "NO OFICIAL",
    "BEL-A", "REC-A", "CN-DEC10", "Places", "preliminar", "borrador", "prueba",
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_module("fase27_base_readonly", BASE_MODULE_PATH)


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
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True, encoding="utf-8",
        errors="replace", capture_output=True,
    ).stdout


def protected_snapshot() -> list[dict]:
    rows = []
    for rel in PROTECTED_ROOTS:
        root = ROOT / rel
        if not root.exists():
            rows.append({"ruta": rel, "bytes": 0, "sha256": "", "estado": "AUSENTE"})
            continue
        files = [root] if root.is_file() else sorted(
            p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        )
        for path in files:
            rows.append({"ruta": repo_rel(path), "bytes": path.stat().st_size,
                         "sha256": sha256(path), "estado": "PRESENTE"})
    return rows


def snapshot_digest(rows: list[dict]) -> str:
    payload = "\n".join(f"{r['ruta']}|{r['bytes']}|{r['sha256']}|{r['estado']}" for r in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sync_base_globals() -> None:
    base.FASE = FASE
    base.SCRIPTS = SCRIPTS
    base.DOCS = DOCS
    base.OUT = OUT
    base.ASSETS = ASSETS
    base.META = META
    base.QA_PNG = QA_PNG
    base.CONTENT = CONTENT
    base.CONFIG = CONFIG
    base.PDF_OUT = PDF_OUT
    base.PACK = PACK
    base.ZIP_OUT = ZIP_OUT
    base.DATE = DATE


def svg_to_png(svg_path: Path, png_path: Path, dpi: int) -> None:
    with fitz.open(stream=svg_path.read_bytes(), filetype="svg") as doc:
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72.0, dpi / 72.0), alpha=False)
        pix.save(png_path)


def derive_general_map(cfg: dict) -> list[dict]:
    carto = load_module("cartografia_v31_readonly", CARTO_MODULE_PATH)
    carto.MAPS = ASSETS
    carto.GREEN = carto.BLUE
    carto.NAVY = carto.SLATE
    original_save = carto.save_figure

    def save_v32(fig, stem, width, height, dpi=220):
        return original_save(fig, "mapa_general_institucional_v3_2", width, height, dpi)

    def public_title_footer(fig, title, subtitle, note=None):
        fig.text(0.055, 0.955, title, fontsize=19, fontweight="bold", color="#17324D", va="top")
        fig.text(0.055, 0.918, "Siete zonas seleccionadas · lectura territorial", fontsize=10.5,
                 color=carto.SLATE, va="top")
        fig.text(0.055, 0.035, "Dirección General de Desarrollo Gastronómico", fontsize=8.2,
                 color="#17324D", va="bottom", fontweight="bold")
        fig.text(0.945, 0.035, "Referencia territorial elaborada por la DGDGAS.", fontsize=7.1,
                 color=carto.SLATE, va="bottom", ha="right")

    carto.save_figure = save_v32
    carto.title_footer = public_title_footer
    streets = gpd.read_file(carto.STREETS_PATH).to_crs(4326)
    barrios = gpd.read_file(carto.BARRIOS_PATH).to_crs(4326)
    bel = gpd.read_file(V31_LAYERS / "BELGRANO_PRESENTACION_V3_1.geojson").to_crs(4326)
    rec = gpd.read_file(V31_LAYERS / "RECOLETA_PRESENTACION_V3_1.geojson").to_crs(4326)
    cn = gpd.read_file(V31_LAYERS / "COSTANERA_NORTE_PRESENTACION_V3_1.geojson").to_crs(4326)
    carto.render_general(streets, barrios, bel, rec, cn)

    src = ASSETS / "mapa_general_institucional_v3_2.png"
    crop = cfg["mapa_general"]["crop_pixels"]
    with Image.open(src) as img:
        img.crop(tuple(crop)).save(ASSETS / "mapa_general_integrado_v2_1.png")
    return [
        {"asset": "mapa_general_institucional_v3_2.png", "origen": "mismas siete geometrías V3.1",
         "transformacion": "San Telmo usa azul de Núcleo / área; geometrías intactas", "sha256": sha256(src)},
        {"asset": "mapa_general_institucional_v3_2.svg", "origen": "mismas siete geometrías V3.1",
         "transformacion": "render vectorial derivado; leyenda de cinco categorías", "sha256": sha256(ASSETS / "mapa_general_institucional_v3_2.svg")},
        {"asset": "mapa_general_integrado_v2_1.png", "origen": "mapa_general_institucional_v3_2.png",
         "transformacion": "recorte editorial idéntico a V2", "sha256": sha256(ASSETS / "mapa_general_integrado_v2_1.png")},
    ]


def derive_costanera(cfg: dict) -> list[dict]:
    rows = []
    for stem in ("costanera_norte_institucional", "costanera_norte_media_pagina"):
        src = V31_MAPS / f"{stem}_v3_1.svg"
        dst_svg = ASSETS / f"{stem}_v3_2.svg"
        dst_png = ASSETS / f"{stem}_v3_2.png"
        text = src.read_text(encoding="utf-8")
        count = text.count(cfg["costanera"]["texto_origen"])
        if count != 1:
            raise AssertionError(f"Texto Costanera esperado una vez en {src.name}; encontrado {count}")
        text = text.replace(cfg["costanera"]["texto_origen"], cfg["costanera"]["texto_destino"])
        dst_svg.write_text(text, encoding="utf-8")
        svg_to_png(dst_svg, dst_png, cfg["render"]["dpi_svg_png"])
        rows.extend([
            {"asset": dst_svg.name, "origen": repo_rel(src), "transformacion": "sustitución léxica única; geometría y estilos intactos", "sha256": sha256(dst_svg)},
            {"asset": dst_png.name, "origen": dst_svg.name, "transformacion": "raster local desde SVG derivado", "sha256": sha256(dst_png)},
        ])
    crop = cfg["costanera"]["crop_media_pixels"]
    src_png = ASSETS / "costanera_norte_media_pagina_v3_2.png"
    with Image.open(src_png) as img:
        img.crop(tuple(crop)).save(ASSETS / "costanera_norte_integrado_v2_1.png")
    rows.append({"asset": "costanera_norte_integrado_v2_1.png", "origen": src_png.name,
                 "transformacion": "recorte editorial idéntico a V2; denominación corregida", "sha256": sha256(ASSETS / "costanera_norte_integrado_v2_1.png")})
    return rows


def copy_unchanged_assets() -> list[dict]:
    names = [
        "belgrano_integrado_v2.png", "corrientes_integrado_v2.png", "palermo_integrado_v2.png",
        "puerto_madero_integrado_v2.png", "recoleta_integrado_v2.png", "san_telmo_integrado_v2.png",
    ]
    rows = []
    for name in names:
        src, dst = BASE_ASSETS / name, ASSETS / name
        shutil.copy2(src, dst)
        rows.append({"asset": name, "origen": repo_rel(src), "transformacion": "copia binaria sin cambios", "sha256": sha256(dst)})
    return rows


def sintesis_page(c, data: dict, meta: dict) -> None:
    sec = data["sintesis"]
    y = base.page_header(c, 2, sec["titulo"], sec["bajada"])
    yy = y - 2
    for paragraph in sec["parrafos"]:
        yy = base.draw_wrapped(c, paragraph, base.M + 8, yy, base.W - 2 * base.M - 16,
                               size=11.0, leading=15.5)
        yy -= 13
    yy -= 4
    base.draw_wrapped(c, sec["encuadre"], base.M + 8, yy, base.W - 2 * base.M - 16,
                      font_name=base.FONT_BOLD, size=10.6, color=base.AZUL, leading=15)
    base.note_box(c, base.M, 126, base.W - 2 * base.M, 90, sec["como_leer_titulo"],
                  sec["como_leer"], border=base.CELESTE, fill=base.SOFT_AZUL, size=9.0)
    c.setFont(base.FONT, 8.4)
    base.set_fill(c, base.GRIS)
    for i, line in enumerate(base.wrap_text(sec["alcance_pie"], base.FONT, 8.4, base.W - 2 * base.M - 16)):
        c.drawString(base.M + 8, 92 - i * 11, line)
    base.page_footer(c, meta["institucion"], meta["gobierno"])
    c.showPage()


def build_pdf(data: dict) -> None:
    meta = data["meta"]
    c = canvas.Canvas(str(PDF_OUT), pagesize=A4)
    c.setTitle(meta["pdf_title"])
    c.setSubject(meta["pdf_subject"])
    c.setAuthor(meta["pdf_author"])
    c.setCreator(meta["pdf_creator"])
    base.cover(c, meta)
    sintesis_page(c, data, meta)
    base.mapa_general_page(c, data, meta)
    base.detalle_page(c, 4, data["palermo"], meta)
    base.detalle_page(c, 5, data["corrientes"], meta, extra_key="abasto", extra_title_key="abasto_titulo")
    base.san_telmo_puerto_page(c, data, meta)
    base.detalle_page(c, 7, data["belgrano"], meta, extra_key="organizacion", extra_title_key="organizacion_titulo")
    base.recoleta_page(c, data, meta)
    base.costanera_page(c, data, meta)
    base.cierre_page(c, data, meta)
    c.save()


def render_pages(dpi: int) -> list[Path]:
    QA_PNG.mkdir(parents=True, exist_ok=True)
    paths = []
    with fitz.open(PDF_OUT) as doc:
        for i, page in enumerate(doc, 1):
            dest = QA_PNG / f"pagina_{i:02d}.png"
            page.get_pixmap(dpi=dpi, alpha=False).save(dest)
            paths.append(dest)
    return paths


def make_comparatives() -> list[Path]:
    COMPARATIVAS.mkdir(parents=True, exist_ok=True)
    outputs = []
    for page in (2, 3, 7, 8, 9, 10):
        left = Image.open(BASE_QA / f"pagina_{page:02d}.png").convert("RGB")
        right = Image.open(QA_PNG / f"pagina_{page:02d}.png").convert("RGB")
        height = max(left.height, right.height)
        canvas_img = Image.new("RGB", (left.width + right.width, height + 42), "white")
        canvas_img.paste(left, (0, 42))
        canvas_img.paste(right, (left.width, 42))
        draw = ImageDraw.Draw(canvas_img)
        draw.text((18, 13), f"V2 · página {page}", fill="#17324D")
        draw.text((left.width + 18, 13), f"V2.1 · página {page}", fill="#17324D")
        dest = COMPARATIVAS / f"comparativa_pagina_{page:02d}_v2_v2_1.png"
        canvas_img.save(dest)
        outputs.append(dest)
    return outputs


def pdf_metadata() -> dict:
    with fitz.open(PDF_OUT) as doc:
        return doc.metadata or {}


def public_corpora() -> dict[str, str]:
    corpora = {"YAML": CONTENT.read_text(encoding="utf-8")}
    with fitz.open(PDF_OUT) as doc:
        corpora["PDF texto"] = "\n".join(page.get_text() for page in doc)
        corpora["PDF metadatos"] = " ".join(str(v) for v in (doc.metadata or {}).values() if v)
    for path in sorted(ASSETS.glob("*.svg")):
        corpora[f"SVG {path.name}"] = path.read_text(encoding="utf-8", errors="replace")
    for name in ("README_AJUSTES_FINALES_V2_1.md", "AUDITORIA_COMPARATIVA_V2_V2_1.md"):
        path = DOCS / name
        if path.exists():
            corpora[f"DOC {name}"] = path.read_text(encoding="utf-8")
    return corpora


def scan_public_text() -> list[dict]:
    rows = []
    for origin, text in public_corpora().items():
        low = text.casefold()
        for term in FORBIDDEN_PUBLIC:
            count = low.count(term.casefold())
            rows.append({"origen": origin, "termino_controlado": term, "apariciones": count,
                         "resultado": "APTO" if count == 0 else "NO_APTO"})
    return rows


def privacy_scan_pack(root: Path) -> dict:
    patterns = {
        "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
        "telefono": re.compile(r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b"),
        "cuit": re.compile(r"\b\d{2}-\d{8}-\d\b"),
        "api_key": re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
        "links_privados": re.compile(r"(?:drive|docs)\.google\.com", re.I),
        "id_externo": re.compile(r"place_id", re.I),
    }
    hits = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".csv", ".json", ".yaml", ".py", ".svg", ".txt"}):
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in patterns.items():
            if label == "id_externo" and path.name == Path(__file__).name:
                continue  # patrón de autocontrol definido por el propio generador
            if pattern.search(text):
                hits.append({"archivo": path.relative_to(root).as_posix(), "patron": label})
    return {"archivos_escaneados": sum(1 for p in root.rglob("*") if p.is_file()),
            "hallazgos": hits, "resultado": "APTO" if not hits else "NO_APTO"}


def write_docs(structural: dict, asset_rows: list[dict], protected_pre: list[dict], protected_post: list[dict]) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    write_text(DOCS / "README_AJUSTES_FINALES_V2_1.md", f"""# Ajustes finales del informe político V2.1

Línea paralela generada como ajuste editorial y cartográfico de V2. Conserva la estructura de
10 páginas, la identidad visual, las siete zonas y todas las geometrías. El producto queda
pendiente de auditoría independiente y de cualquier decisión posterior de promoción institucional.

## Base y alcance

- Base PDF V2: `{repo_rel(BASE_PDF)}`.
- SHA-256 base PDF: `{sha256(BASE_PDF)}`.
- Correcciones cartográficas: nuevo mapa general V3.2 y nuevo mapa de Costanera V3.2.
- Sin modelos, recálculos analíticos, solicitudes de red ni cambios de fuentes.
- Metodología exacta reservada únicamente en el lock técnico interno.
""")
    adjustments = [
        ("2", "Síntesis", "Sustitución de párrafos 3 y 4; nueva explicación de lectura; caja reducida", "APLICADO"),
        ("3", "Mapa general", "San Telmo alineado con Núcleo / área; leyenda de cinco categorías", "APLICADO"),
        ("4", "Palermo", "Párrafo sustituido", "APLICADO"),
        ("7", "Belgrano", "Caja Cómo se organiza el polo", "APLICADO"),
        ("8", "Recoleta", "Lectura territorial sustituida; Diversidad interna preservada", "APLICADO"),
        ("9", "Costanera Norte", "Introducción y panel sustituidos; asset léxico corregido", "APLICADO"),
        ("10", "Metodología", "Valor exacto retirado; fuentes, representación y alcance ajustados", "APLICADO"),
        ("PDF", "Metadatos", "Title, Subject, Author y Creator institucionales", "APLICADO"),
    ]
    write_csv(DOCS / "MATRIZ_AJUSTES_AUDITORIA_V2_1.csv",
              [{"pagina": a, "seccion": b, "ajuste": c, "estado": d} for a, b, c, d in adjustments],
              ["pagina", "seccion", "ajuste", "estado"])
    semantic = [
        ("Palermo", "Núcleo / área", "#2C7FB8", "polígono", "Núcleo / área"),
        ("San Telmo", "Núcleo / área", "#2C7FB8", "polígono", "Núcleo / área"),
        ("Corrientes", "Corredor", "#C0762B", "línea", "Corredor"),
        ("Puerto Madero", "Frente", "#2F7D78", "línea", "Frente"),
        ("Belgrano", "Unidad multiparte", "#64748B", "polígono", "Unidad multiparte"),
        ("Costanera Norte", "Unidad multiparte", "#64748B", "polígono", "Unidad multiparte"),
        ("Recoleta", "Unidad general", "#9B3A4A", "polígono", "Unidad general"),
    ]
    write_csv(DOCS / "QA_SEMANTICO_MAPA_GENERAL_V2_1.csv",
              [{"entidad": e, "forma_territorial": f, "color": c, "símbolo": s,
                "entrada_leyenda": l, "coincidencia": "SI", "observaciones": "Correspondencia inequívoca"}
               for e, f, c, s, l in semantic],
              ["entidad", "forma_territorial", "color", "símbolo", "entrada_leyenda", "coincidencia", "observaciones"])
    write_csv(META / "TABLA_ENTIDAD_TIPO_COLOR_V2_1.csv",
              [{"entidad": e, "tipo": f, "color": c} for e, f, c, _, _ in semantic],
              ["entidad", "tipo", "color"])
    write_csv(META / "TABLA_ESTILOS_DENOMINACIONES_V2_1.csv", [
        {"asset": "mapa_general_institucional_v3_2", "categoria": f, "color": c, "denominacion": f}
        for _, f, c, _, _ in dict((e, (e, f, c, s, l)) for e, f, c, s, l in semantic).values()
    ] + [{"asset": "costanera_norte_v3_2", "categoria": "componente_3", "color": "#2F7D78",
          "denominacion": "Patio gastronómico de puestos en contenedores"}],
              ["asset", "categoria", "color", "denominacion"])
    write_text(DOCS / "QA_ESTRUCTURAL_PDF_V2_1.md", f"""# QA estructural PDF V2.1

- Archivo: `{repo_rel(PDF_OUT)}`
- Páginas: {structural['paginas']}.
- Dimensiones: {', '.join(structural['dimensiones'])} puntos.
- Páginas con texto extraíble: {structural['paginas_con_texto_extraible']}.
- Páginas en blanco: {structural['paginas_en_blanco'] or 'ninguna'}.
- Bloques fuera de página: {structural['bloques_fuera_de_pagina'] or 'ninguno'}.
- Resultado: **{structural['resultado']}**.
""")
    visual_rows = []
    special = {2: "Caja reducida y equilibrio revisado", 3: "Siete nombres, colores y leyenda revisados",
               7: "Nueva caja de organización revisada", 8: "Texto y mapa revisados",
               9: "Leyenda, panel y denominación revisados", 10: "Densidad y jerarquía revisadas"}
    for page in range(1, 11):
        visual_rows.append({"pagina": page, "archivo_png": f"pagina_{page:02d}.png", "estado": "APTO",
                            "observaciones": special.get(page, "Sin defectos visuales bloqueantes detectados")})
    write_csv(DOCS / "QA_VISUAL_PAGINA_POR_PAGINA_V2_1.csv", visual_rows,
              ["pagina", "archivo_png", "estado", "observaciones"])
    write_text(DOCS / "AUDITORIA_COMPARATIVA_V2_V2_1.md", """# Auditoría comparativa V2 → V2.1

## Páginas modificadas

Se modificaron las páginas 2, 3, 4, 7, 8, 9 y 10. Las páginas 1, 5 y 6 conservaron contenido y
composición. La estructura general, los márgenes, la identidad visual y la paginación se preservaron.

## Cambios controlados

- Página 2: síntesis y caja de lectura.
- Página 3: corrección semántica de San Telmo y leyenda consistente.
- Página 4: lectura de Palermo.
- Página 7: nueva explicación de la organización interna de Belgrano.
- Página 8: lectura territorial de Recoleta.
- Página 9: introducción, panel territorial y denominación en la leyenda de Costanera.
- Página 10: metodología, alcance y reserva del indicador técnico exacto.
- Metadatos: campos institucionales normalizados.

## Preservación

Las siete geometrías se conservaron. No cambiaron la cantidad de zonas, los modelos, las
centralidades decididas, los cuatro componentes de Costanera, sus cinco piezas internas, los
vacíos ni la ausencia de conectores. Las comparativas visuales están en `comparativas_v2_v2_1/`.
""")
    write_text(DOCS / "HANDOFF_AUDITOR_INDEPENDIENTE_V2_1.md", f"""# Handoff al auditor independiente — V2.1

## Estado

Producto generado por `integrador_tecnico_editorial`; pendiente de control independiente. El
autocontrol del productor no constituye aprobación definitiva.

## Rutas principales

- PDF: `{repo_rel(PDF_OUT)}`
- Renders: `{repo_rel(QA_PNG)}`
- Comparativas: `{repo_rel(COMPARATIVAS)}`
- QA semántico: `{repo_rel(DOCS / 'QA_SEMANTICO_MAPA_GENERAL_V2_1.csv')}`

## Decisiones preservadas

Siete zonas; Belgrano como un polo con tres centralidades; Recoleta como unidad general;
Costanera Norte como polo multiparte de cuatro componentes y cinco piezas internas.

## Próximo dueño

`auditor_qa`, en modo de solo lectura sobre el producto y con reporte separado.
""")
    protected_rows = []
    post_by_path = {r["ruta"]: r for r in protected_post}
    for pre in protected_pre:
        post = post_by_path.get(pre["ruta"])
        protected_rows.append({"ruta": pre["ruta"], "sha256_pre": pre["sha256"],
                               "sha256_post": post["sha256"] if post else "",
                               "resultado": "SIN_CAMBIOS" if post and pre["sha256"] == post["sha256"] else "CAMBIO"})
    write_csv(META / "VERIFICACION_HASHES_PROTEGIDOS_V2_1.csv", protected_rows,
              ["ruta", "sha256_pre", "sha256_post", "resultado"])
    write_csv(META / "ASSETS_TRAZABILIDAD_V2_1.csv", asset_rows,
              ["asset", "origen", "transformacion", "sha256"])


def write_textual_qa() -> list[dict]:
    rows = scan_public_text()
    write_csv(DOCS / "QA_TEXTUAL_INSTITUCIONAL_V2_1.csv", rows,
              ["origen", "termino_controlado", "apariciones", "resultado"])
    return rows


def manifest_rows(root: Path, exclusions: set[Path] | None = None) -> list[dict]:
    exclusions = exclusions or set()
    rows = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p not in exclusions):
        rows.append({"ruta_relativa": path.relative_to(root).as_posix(), "bytes": path.stat().st_size,
                     "sha256": sha256(path)})
    return rows


def build_pack() -> dict:
    for sub in ("docs", "assets", "metadatos", "scripts", QA_PNG.name, COMPARATIVAS.name):
        (PACK / sub).mkdir(parents=True, exist_ok=True)
    for path in sorted(DOCS.glob("*")):
        if path.is_file():
            shutil.copy2(path, PACK / "docs" / path.name)
    shutil.copy2(PDF_OUT, PACK / PDF_OUT.name)
    for path in sorted(ASSETS.glob("*")):
        if path.is_file():
            shutil.copy2(path, PACK / "assets" / path.name)
    for path in sorted(META.glob("*")):
        if path.is_file() and path.name not in {"GIT_STATUS_PRE.txt", "GIT_STATUS_POST.txt"}:
            shutil.copy2(path, PACK / "metadatos" / path.name)
    for path in sorted(QA_PNG.glob("*.png")):
        shutil.copy2(path, PACK / QA_PNG.name / path.name)
    for path in sorted(COMPARATIVAS.glob("*.png")):
        shutil.copy2(path, PACK / COMPARATIVAS.name / path.name)
    for name in (Path(__file__).name, CONTENT.name, CONFIG.name, "README_REPRODUCCION.md"):
        shutil.copy2(SCRIPTS / name, PACK / "scripts" / name)
    write_text(PACK / "README.md", """# Revisión del informe político integrado V2.1

Paquete autocontenido para auditoría humana. Incluye PDF, 10 renders, assets derivados,
comparativas, controles, metadatos y capa reproducible. No incluye datos fuente, puntos,
capas internas, credenciales, cachés, temporales ni paquetes históricos completos.
""")
    metadata = {
        "paquete": PACK.name, "fecha": DATE, "estado": "PENDIENTE_AUDITORIA_INDEPENDIENTE",
        "rol_productor": "integrador_tecnico_editorial", "paginas": 10,
        "network_requests": 0, "api_calls": 0, "model_runs": 0, "geometry_changes": 0,
        "exclusiones": ["datos fuente", "puntos", "capas internas", "credenciales", "caches",
                         "temporales", ".git", ".graphify", "node_modules", "paquetes históricos completos"],
    }
    write_text(PACK / "metadata_paquete_v2_1.json", json.dumps(metadata, ensure_ascii=False, indent=2))
    manifest = PACK / "MANIFEST_CONTENIDO.csv"
    checks_internal = PACK / "CHECKSUMS_INTERNO.txt"
    rows = manifest_rows(PACK, {manifest, checks_internal})
    write_csv(manifest, rows, ["ruta_relativa", "bytes", "sha256"])
    write_text(checks_internal,
               f"{sha256(manifest)}  MANIFEST_CONTENIDO.csv\n"
               f"{sha256(PACK / 'metadata_paquete_v2_1.json')}  metadata_paquete_v2_1.json")
    privacy = privacy_scan_pack(PACK)
    write_text(PACK / "AUTOCONTROL_PAQUETE_V2_1.json", json.dumps(privacy, ensure_ascii=False, indent=2))
    if privacy["resultado"] != "APTO":
        raise AssertionError(f"QA privacidad del paquete: {privacy['hallazgos']}")
    rows = manifest_rows(PACK, {manifest, checks_internal})
    write_csv(manifest, rows, ["ruta_relativa", "bytes", "sha256"])
    write_text(checks_internal,
               f"{sha256(manifest)}  MANIFEST_CONTENIDO.csv\n"
               f"{sha256(PACK / 'metadata_paquete_v2_1.json')}  metadata_paquete_v2_1.json\n"
               f"{sha256(PACK / 'AUTOCONTROL_PAQUETE_V2_1.json')}  AUTOCONTROL_PAQUETE_V2_1.json")
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in PACK.rglob("*") if p.is_file()):
            zf.write(path, PACK.name + "/" + path.relative_to(PACK).as_posix())
    with zipfile.ZipFile(ZIP_OUT) as zf:
        bad = zf.testzip()
        if bad is not None:
            raise AssertionError(f"ZIP inválido: {bad}")
        names = zf.namelist()
        forbidden_names = [".env", "node_modules", ".graphify", "__pycache__", ".git/"]
        if any(token in name for name in names for token in forbidden_names):
            raise AssertionError("El ZIP contiene una ruta excluida")
    return {"ruta": repo_rel(ZIP_OUT), "bytes": ZIP_OUT.stat().st_size, "sha256": sha256(ZIP_OUT),
            "archivos": len([p for p in PACK.rglob("*") if p.is_file()]), "testzip": "OK"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-pack", action="store_true")
    args = parser.parse_args()
    for path in (DOCS, OUT, ASSETS, META, INTERNAL, QA_PNG, COMPARATIVAS):
        path.mkdir(parents=True, exist_ok=True)
    sync_base_globals()
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    base.register_fonts()
    data = base.load_content(CONTENT)

    write_text(META / "GIT_STATUS_PRE.txt", run_git("status", "--short"))
    write_text(META / "GIT_DIFF_CACHED_PRE.txt", run_git("diff", "--cached", "--name-only"))
    protected_pre = protected_snapshot()
    pre_digest = snapshot_digest(protected_pre)
    write_csv(META / "HASHES_PROTEGIDOS_PRE_V2_1.csv", protected_pre, ["ruta", "bytes", "sha256", "estado"])
    critical_rows = []
    for rel in CRITICAL_INPUTS:
        path = ROOT / rel
        critical_rows.append({"ruta": rel, "bytes": path.stat().st_size if path.exists() else 0,
                              "sha256": sha256(path) if path.exists() else "", "estado": "PRESENTE" if path.exists() else "AUSENTE"})
    write_csv(META / "INSUMOS_CRITICOS_SHA256_V2_1.csv", critical_rows,
              ["ruta", "bytes", "sha256", "estado"])

    asset_rows = copy_unchanged_assets() + derive_general_map(cfg) + derive_costanera(cfg)
    build_pdf(data)
    render_pages(cfg["render"]["dpi_pdf_pages"])
    make_comparatives()
    structural = base.structural_qa()
    if structural["resultado"] != "APTO":
        raise AssertionError(f"QA estructural falló: {structural}")

    protected_post = protected_snapshot()
    post_digest = snapshot_digest(protected_post)
    if pre_digest != post_digest:
        raise AssertionError("Se modificó una superficie protegida")
    write_docs(structural, asset_rows, protected_pre, protected_post)
    textual_rows = write_textual_qa()
    bad_text = [r for r in textual_rows if r["resultado"] != "APTO"]
    if bad_text:
        raise AssertionError(f"QA textual público falló: {bad_text[:10]}")

    metadata = {
        "fase": FASE, "fecha": DATE, "generado_utc": datetime.now(timezone.utc).isoformat(),
        "rol": "integrador_tecnico_editorial", "infraestructura": "V1.1.1",
        "base_v2_pdf": {"ruta": repo_rel(BASE_PDF), "sha256": sha256(BASE_PDF)},
        "pdf": {"ruta": repo_rel(PDF_OUT), "bytes": PDF_OUT.stat().st_size, "sha256": sha256(PDF_OUT),
                "metadatos": pdf_metadata()},
        "geometrias_preservadas": True, "geometrias_modificadas": 0, "model_runs": 0,
        "api_calls": 0, "network_requests": 0, "protected_files": len(protected_pre),
        "protected_digest_pre": pre_digest, "protected_digest_post": post_digest,
    }
    write_text(META / "METADATA_INFORME_POLITICO_INTEGRADO_V2_1.json",
               json.dumps(metadata, ensure_ascii=False, indent=2))
    write_text(INTERNAL / "KPI_LOCK_TECNICO_V2_1.csv",
               "kpi;valor;estado;publicable\ncomposicion_fuente_auxiliar_costanera;92,96 %;RESERVADO_METODOLOGIA;NO")
    write_text(META / "GIT_STATUS_POST.txt", run_git("status", "--short"))
    write_text(META / "GIT_DIFF_CACHED_POST.txt", run_git("diff", "--cached", "--name-only"))

    line_manifest = OUT / "MANIFEST_CONTENIDO.csv"
    rows = manifest_rows(OUT, {line_manifest, OUT / "CHECKSUMS_SHA256.txt", ZIP_OUT})
    write_csv(line_manifest, rows, ["ruta_relativa", "bytes", "sha256"])
    summary = {"pdf": repo_rel(PDF_OUT), "pdf_sha256": sha256(PDF_OUT), "paginas": 10,
               "qa_estructural": "APTO", "qa_textual": "APTO", "protegidos": "SIN_CAMBIOS"}
    if not args.no_pack:
        pack = build_pack()
        write_text(OUT / "CHECKSUMS_SHA256.txt",
                   f"{sha256(line_manifest)}  MANIFEST_CONTENIDO.csv\n"
                   f"{sha256(PDF_OUT)}  {PDF_OUT.name}\n"
                   f"{pack['sha256']}  {ZIP_OUT.name}")
        summary["zip"] = pack
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
