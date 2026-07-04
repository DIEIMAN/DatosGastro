"""Análisis exploratorio del Formulario Cafecito (evento Cafecito BA en tu barrio).

Lee el XLSX ORIGINAL de respuestas SIN modificarlo, excluye datos personales y produce
outputs agregados (CSV, resumen cualitativo y gráficos de barras) en outputs/cafecito/.

Principios:
  - El XLSX original NO se modifica (solo lectura, vía zipfile + XML; openpyxl no está instalado).
  - Datos personales (correo, marca temporal, barrio fino) NO se publican.
  - Muestra chica: todo es exploratorio, no representativo. El script no infiere ni completa datos.
  - Multi-respuesta (canal de difusión, eventos futuros) se desagrega; los % suman >100 %.

Uso:
    python scripts/cafecito/analizar_cafecito.py
"""
from __future__ import annotations

import csv
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "Cafesito"
XLSX = SRC_DIR / "Formulario Cafecito (Respuestas).xlsx"
PDF_FORM = SRC_DIR / "Formulario cafecito.pdf"
INFO_FILE = SRC_DIR / "InfoCafecito"
OUT_DIR = REPO_ROOT / "outputs" / "cafecito"
GRAF_DIR = OUT_DIR / "graficos"
DOCS_DIR = REPO_ROOT / "docs" / "cafecito"
REPORT_MD = DOCS_DIR / "INFORME_CAFECITO_EXPLORATORIO.md"
README_MD = DOCS_DIR / "README_CAFECITO.md"
DOCX_REPORT = OUT_DIR / "INFORME_CAFECITO_GRAFICOS.docx"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# Columnas del formulario (letra de columna -> clave interna normalizada).
COLS = {
    "A": "marca_temporal",          # SENSIBLE (no se publica)
    "B": "correo",                  # SENSIBLE: dato personal -> excluido
    "C": "acepta_contacto",
    "D": "rango_edad",
    "E": "genero",
    "F": "donde_vivis",
    "G": "barrio_localidad",        # SENSIBLE: texto libre identificable -> no se lista
    "H": "primera_vez",
    "I": "con_quien",
    "J": "como_se_entero",          # multi-respuesta
    "K": "que_intereso",
    "L": "eventos_futuros",         # multi-respuesta
}
# No se publican en ningún output:
SENSIBLE = {"marca_temporal", "correo", "barrio_localidad"}
# Preguntas cerradas de una sola opción:
CERRADAS_SIMPLES = ["rango_edad", "genero", "donde_vivis", "primera_vez",
                    "con_quien", "que_intereso", "acepta_contacto"]
# Preguntas cerradas multi-respuesta (se desagregan por coma):
CERRADAS_MULTI = ["como_se_entero", "eventos_futuros"]
# Etiquetas legibles para gráficos/CSV:
LABELS = {
    "rango_edad": "Rango de edad",
    "genero": "Género",
    "donde_vivis": "Dónde vive (nivel macro)",
    "primera_vez": "¿Primera vez en un evento gastronómico?",
    "con_quien": "¿Con quién vino?",
    "que_intereso": "Qué fue lo que más le interesó",
    "acepta_contacto": "¿Acepta recibir información?",
    "como_se_entero": "Cómo se enteró del evento (multi-respuesta)",
    "eventos_futuros": "Eventos que le interesarían a futuro (multi-respuesta)",
}
# Orden natural para edad (categoría ordinal).
ORDEN_EDAD = ["18 a 24", "25 a 34", "35 a 44", "45 a 54", "55 a 64", "65 o mas"]

DECISIONES: list[str] = []


# --------------------------------------------------------------------------- IO

def col_letter(ref: str) -> str:
    return re.match(r"([A-Z]+)", ref).group(1)


def row_num(ref: str) -> int:
    return int(re.search(r"(\d+)", ref).group(1))


def read_xlsx(path: Path) -> list[dict]:
    """Lee la primera hoja del XLSX como lista de dicts (solo lectura, sin openpyxl)."""
    zf = zipfile.ZipFile(path)
    shared: list[str] = []
    with zf.open("xl/sharedStrings.xml") as f:
        for si in ET.parse(f).getroot():
            shared.append("".join(n.text or "" for n in si.iter(NS + "t")))
    cells: dict[int, dict[str, str]] = {}
    with zf.open("xl/worksheets/sheet1.xml") as f:
        sheet = ET.parse(f).getroot()
    for row in sheet.iter(NS + "row"):
        for c in row:
            if c.tag != NS + "c":
                continue
            ref = c.get("r")
            letter, r = col_letter(ref), row_num(ref)
            t = c.get("t")
            v = c.find(NS + "v")
            if v is not None:
                val = shared[int(v.text)] if t == "s" else (v.text or "")
            else:
                inl = c.find(NS + "is")
                val = "".join(n.text or "" for n in inl.iter(NS + "t")) if inl is not None else ""
            cells.setdefault(r, {})[letter] = val
    if not cells:
        return []
    header_row = min(cells)
    records = []
    for r in sorted(cells):
        if r == header_row:
            continue
        rec = {COLS.get(letter, letter): cells[r].get(letter, "").strip() for letter in COLS}
        records.append(rec)
    return records


# ------------------------------------------------------------------- normalize

def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


# Opciones canónicas que contienen comas internas: se protegen antes de separar por coma.
# En Google Forms las multi-respuestas llegan concatenadas por coma, por eso necesitamos
# conocer estas opciones de antemano para no partir una categoría válida.
OPCIONES_CANONICAS_CON_COMA = {
    "como_se_entero": [
        "Por amigos, familia o conocidos",
    ],
}

GRAPH_ORDER = [
    "rango_edad",
    "genero",
    "donde_vivis",
    "primera_vez",
    "con_quien",
    "como_se_entero",
    "que_intereso",
    "eventos_futuros",
    "acepta_contacto",
]


def split_multi(s: str, key: str | None = None) -> list[str]:
    """Separa respuestas multi-opción sin romper opciones canónicas con coma interna."""
    s = s or ""
    protegidas = {}
    for i, opt in enumerate(OPCIONES_CANONICAS_CON_COMA.get(key or "", [])):
        token = f"<<OPT{i}>>"
        if opt in s:
            s = s.replace(opt, token)
            protegidas[token] = opt
    partes = []
    for p in re.split(r"[,;]", s):
        p = norm_space(p)
        if not p:
            continue
        partes.append(protegidas.get(p, p))
    return partes


def is_blank(s: str) -> bool:
    return not norm_space(s)


# ---------------------------------------------------------------------- análisis

def count_simple(records, key):
    c = Counter(norm_space(r.get(key, "")) for r in records if not is_blank(r.get(key, "")))
    return c


def count_multi(records, key):
    """Cuenta por opción desagregada y devuelve también cuántos respondentes (base)."""
    c = Counter()
    base = 0
    for r in records:
        parts = split_multi(r.get(key, ""), key)
        if parts:
            base += 1
        for p in parts:
            c[p] += 1
    return c, base


def ordered_items(key, counter):
    if key == "rango_edad":
        items = [(k, counter.get(k, 0)) for k in ORDEN_EDAD if k in counter]
        # cualquier valor inesperado al final
        extra = [(k, v) for k, v in counter.items() if k not in ORDEN_EDAD]
        return items + sorted(extra, key=lambda x: -x[1])
    return counter.most_common()


# ------------------------------------------------------------------------ plots

def barplot(items, title, outfile, base_n, multi=False, note=None):
    if not items:
        return False
    labels = [k for k, _ in items]
    values = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(8, max(2.4, 0.55 * len(labels) + 1.4)))
    ax.barh(range(len(labels)), values, color="#6f4e37")  # tono café
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels([l if len(l) <= 42 else l[:39] + "…" for l in labels], fontsize=9)
    ax.invert_yaxis()
    for i, v in enumerate(values):
        pct = (v / base_n * 100) if base_n else 0
        ax.text(v + max(values) * 0.01, i, f"{v} ({pct:.0f}%)", va="center", fontsize=8)
    ax.set_xlabel("Respuestas")
    ax.set_xlim(0, max(values) * 1.18)
    subtitle = f"n = {base_n} respuestas" + (" · multi-respuesta (suma >100%)" if multi else "")
    ax.set_title(f"{title}\n{subtitle}", fontsize=11, loc="left")
    foot = note or "Cafecito · muestra exploratoria, no representativa"
    fig.text(0.01, 0.01, foot, fontsize=7, color="#666666")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(outfile, dpi=130)
    plt.close(fig)
    return True


# --------------------------------------------------------------------- cruces

def crosstab(records, key_a, key_b, min_cell_base=8):
    """Cruce simple A x B con conteos. Devuelve None si la base es muy chica."""
    valid = [r for r in records if not is_blank(r.get(key_a, "")) and not is_blank(r.get(key_b, ""))]
    if len(valid) < min_cell_base:
        return None
    table = defaultdict(Counter)
    for r in valid:
        table[norm_space(r.get(key_a))][norm_space(r.get(key_b))] += 1
    return dict(table), len(valid)


# --------------------------------------------------------------------- informes

def rel(p: Path) -> str:
    return str(p.relative_to(REPO_ROOT)).replace("\\", "/")


def fmt_pct(n: int, base: int) -> str:
    return f"{(n / base * 100):.1f}%" if base else "0.0%"


def stat_top(stats: dict, key: str) -> tuple[str, int, int]:
    items = stats.get(key, {}).get("items", [])
    base = stats.get(key, {}).get("base", 0)
    if not items:
        return "sin datos", 0, base
    val, n = max(items, key=lambda item: item[1])
    return val, n, base


def count_lines(stats: dict, key: str, limit: int | None = None) -> list[str]:
    items = stats.get(key, {}).get("items", [])
    base = stats.get(key, {}).get("base", 0)
    selected = items[:limit] if limit else items
    return [f"- **{val}**: {n} ({fmt_pct(n, base)})" for val, n in selected]


def source_files() -> list[Path]:
    extras_txt = sorted(p for p in SRC_DIR.glob("*.txt") if p.is_file())
    extras_docx = sorted(p for p in SRC_DIR.glob("*.docx") if p.is_file())
    sources = [XLSX, PDF_FORM, INFO_FILE]
    sources.extend(extras_txt)
    sources.extend(extras_docx)
    return [p for p in sources if p.exists()]


def build_conclusions(stats: dict, n_total: int) -> list[str]:
    edad, edad_n, edad_base = stat_top(stats, "rango_edad")
    genero, genero_n, genero_base = stat_top(stats, "genero")
    residencia, residencia_n, residencia_base = stat_top(stats, "donde_vivis")
    interes, interes_n, interes_base = stat_top(stats, "que_intereso")
    futuro, futuro_n, futuro_base = stat_top(stats, "eventos_futuros")
    canal_counts = dict(stats.get("como_se_entero", {}).get("items", []))
    canal_base = stats.get("como_se_entero", {}).get("base", 0)
    instagram = canal_counts.get("Instagram", 0)
    amigos = canal_counts.get("Por amigos, familia o conocidos", 0)
    paso = canal_counts.get("Pase por la zona y lo ví", 0)

    return [
        f"El relevamiento reunió {n_total} respuestas y sirve como muestra exploratoria para aprender sobre el público y el formulario, no como medición representativa del evento.",
        f"El perfil agregado muestra mayor presencia de {edad} ({edad_n}/{edad_base}) y {genero} ({genero_n}/{genero_base}), con procedencia principal declarada en {residencia} ({residencia_n}/{residencia_base}).",
        f"Instagram fue el canal más mencionado ({instagram}/{canal_base}), seguido por la recomendación de amigos, familia o conocidos ({amigos}/{canal_base}); el paso por la zona también aparece ({paso}/{canal_base}).",
        f"El atractivo más señalado fue {interes} ({interes_n}/{interes_base}), una señal útil para ajustar programación y comunicación en futuras ediciones.",
        f"Entre los intereses futuros, {futuro} fue la categoría más mencionada ({futuro_n}/{futuro_base}); las respuestas multi-opción sugieren demanda por formatos variados.",
        "Los cruces simples ayudan a orientar hipótesis de trabajo, pero las celdas chicas obligan a evitar conclusiones fuertes por segmento.",
    ]


def build_recommendations() -> list[str]:
    return [
        "Aumentar la muestra y planificar puntos/horarios de captación para reducir sesgos.",
        "Definir antes de salir a campo qué decisión de gestión alimenta cada pregunta.",
        "Mantener las preguntas que mostraron utilidad analítica: edad, procedencia macro, canal de llegada, vínculo con eventos previos, atractivo principal e intereses futuros.",
        "Mejorar las preguntas multi-opción documentando opciones canónicas y evitando separadores ambiguos en opciones con coma interna.",
        "Evitar campos que no se usarán en análisis o que aumentan fricción sin una decisión asociada.",
        "Cuidar la carga en tablets/celulares: formulario corto, opciones legibles y mínimos campos obligatorios.",
        "Prever uso offline o baja conectividad si el operativo depende de dispositivos en vía pública.",
        "Separar mejor preguntas cerradas, aptas para conteo, de preguntas abiertas pensadas para lectura cualitativa.",
    ]


def chart_readings(stats: dict) -> dict[str, str]:
    readings = {}
    for key in GRAPH_ORDER:
        val, n, base = stat_top(stats, key)
        if key == "como_se_entero":
            counts = dict(stats.get(key, {}).get("items", []))
            amigos = counts.get("Por amigos, familia o conocidos", 0)
            readings[key] = (
                f"Instagram aparece como principal canal ({counts.get('Instagram', 0)}/{base}). "
                f"La categoría 'Por amigos, familia o conocidos' queda unificada y suma {amigos}/{base}; "
                "no se reporta partida entre amigos y familia."
            )
        elif key == "eventos_futuros":
            top3 = ", ".join(f"{v} ({n})" for v, n in stats.get(key, {}).get("items", [])[:3])
            readings[key] = (
                f"Las menciones se concentran en {top3}. Como es multi-respuesta, los porcentajes "
                "suman más de 100% y se leen como intereses declarados, no como preferencias excluyentes."
            )
        elif key == "acepta_contacto":
            readings[key] = (
                f"La opción más frecuente fue {val} ({n}/{base}). La base es de respuestas no vacías; "
                "los correos no se incluyen en ningún output público."
            )
        else:
            readings[key] = f"La categoría con más respuestas fue {val} ({n}/{base}, {fmt_pct(n, base)})."
    return readings


def write_markdown_report(records: list[dict], stats: dict, graf_generados: list[str]) -> None:
    n_total = len(records)
    sources = source_files()
    conclusions = build_conclusions(stats, n_total)
    recommendations = build_recommendations()

    lines = [
        "# Informe exploratorio Cafecito",
        "",
        "## 1. Objetivo del relevamiento",
        "",
        "Cafecito BA en tu barrio fue una propuesta gastronómica y cultural realizada en La Glorieta de Barrancas de Belgrano, con entrada libre y gratuita, durante el sábado 27 y domingo 28 de junio de 2026. La actividad combinó puestos especializados en café y pastelería, música y experiencias al aire libre.",
        "",
        "El formulario fue una primera experiencia de recolección de datos en un evento gastronómico. Su objetivo fue conocer mejor al público asistente, evaluar canales de comunicación, identificar intereses y validar qué preguntas sirven como insumo para futuras acciones de difusión, programación y fidelización.",
        "",
        "## 2. Alcance y limitaciones",
        "",
        f"- Respuestas analizadas: **{n_total}**.",
        "- La muestra es chica y exploratoria.",
        "- No debe leerse como representativa del público total del evento.",
        "- Puede haber sesgo de captación por horario, punto de encuesta, predisposición a responder y disponibilidad de dispositivos.",
        "- Los porcentajes se calculan sobre respuestas válidas por pregunta; en preguntas multi-respuesta pueden sumar más de 100%.",
        "- No se exponen correos, marcas temporales, barrios/localidades libres ni identificadores personales.",
        "",
        "## 3. Perfil general de las personas encuestadas",
        "",
        "### Edad",
        "",
        *count_lines(stats, "rango_edad"),
        "",
        "### Género",
        "",
        *count_lines(stats, "genero"),
        "",
        "### Residencia declarada",
        "",
        *count_lines(stats, "donde_vivis"),
        "",
        "## 4. Vínculo con eventos gastronómicos de la Ciudad",
        "",
        "### Primera vez en un evento gastronómico de la Ciudad",
        "",
        *count_lines(stats, "primera_vez"),
        "",
        "### Con quién vinieron",
        "",
        *count_lines(stats, "con_quien"),
        "",
        "La lectura es útil para pensar dinámicas de asistencia y servicios, pero no alcanza para inferir comportamiento general del público del evento.",
        "",
        "## 5. Canales de llegada",
        "",
        "La pregunta de canales es multi-respuesta. La opción **Por amigos, familia o conocidos** fue tratada como una sola categoría, aunque contiene una coma interna.",
        "",
        *count_lines(stats, "como_se_entero"),
        "",
        "## 6. Motivaciones e intereses",
        "",
        "### Qué fue lo que más interesó del evento",
        "",
        *count_lines(stats, "que_intereso"),
        "",
        "### Eventos gastronómicos de interés futuro",
        "",
        *count_lines(stats, "eventos_futuros", limit=12),
        "",
        "Estas respuestas sirven para orientar hipótesis de programación. No deben leerse como una demanda cerrada ni como ranking definitivo.",
        "",
        "## 7. Cruces exploratorios",
        "",
        "Se generaron cruces simples en `outputs/cafecito/cruces_simples.md`. La recomendación metodológica es leerlos como señales preliminares: cuando hay pocas respuestas por celda, no se fuerza una conclusión por segmento.",
        "",
        "Cruces incluidos:",
        "",
        "- Edad x canal principal de llegada.",
        "- Procedencia x atractivo principal.",
        "- Primera vez x aceptación de contacto.",
        "- Género x atractivo principal.",
        "",
        "## 8. Conclusiones principales",
        "",
        *(f"{i}. {txt}" for i, txt in enumerate(conclusions, 1)),
        "",
        "## 9. Recomendaciones para próximos relevamientos",
        "",
        *(f"{i}. {txt}" for i, txt in enumerate(recommendations, 1)),
        "",
        "## Fuentes revisadas",
        "",
        *(f"- `{rel(p)}`" for p in sources),
        "",
        f"Gráficos regenerados: {len(graf_generados)} archivos en `outputs/cafecito/graficos/`.",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_readme() -> None:
    sources = source_files()
    lines = [
        "# Cafecito - análisis exploratorio",
        "",
        "Este paquete documenta el análisis exploratorio del formulario Cafecito BA en tu barrio.",
        "",
        "## Datos fuente",
        "",
        *(f"- `{rel(p)}`" for p in sources),
        "",
        "El XLSX original se usa solo en modo lectura y no debe modificarse.",
        "",
        "## Script",
        "",
        "- `scripts/cafecito/analizar_cafecito.py`",
        "",
        "Para regenerar los outputs:",
        "",
        "```powershell",
        "python scripts/cafecito/analizar_cafecito.py",
        "```",
        "",
        "## Outputs",
        "",
        "- Tablas y resúmenes: `outputs/cafecito/`",
        "- Gráficos: `outputs/cafecito/graficos/`",
        "- Informe Markdown: `docs/cafecito/INFORME_CAFECITO_EXPLORATORIO.md`",
        "- Documento Word con gráficos: `outputs/cafecito/INFORME_CAFECITO_GRAFICOS.docx`",
        "",
        "## Privacidad",
        "",
        "No publicar correos, marcas temporales, barrios/localidades libres, teléfonos ni identificadores personales. Los outputs públicos trabajan con agregados y omiten datos personales directos.",
        "",
        "La muestra es exploratoria y no representativa del público total del evento.",
        "",
    ]
    README_MD.write_text("\n".join(lines), encoding="utf-8")


def docx_paragraph(text: str = "", size: int = 22, bold: bool = False, spacing: int = 140) -> str:
    b = "<w:b/>" if bold else ""
    return (
        f'<w:p><w:pPr><w:spacing w:after="{spacing}"/></w:pPr>'
        f"<w:r><w:rPr>{b}<w:sz w:val=\"{size}\"/></w:rPr>"
        f'<w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r></w:p>'
    )


def docx_heading(text: str, level: int = 1) -> str:
    size = 34 if level == 1 else 28
    spacing = 220 if level == 1 else 160
    return docx_paragraph(text, size=size, bold=True, spacing=spacing)


def image_extent(path: Path) -> tuple[int, int]:
    emu_per_inch = 914400
    max_cx = int(6.2 * emu_per_inch)
    max_cy = int(4.4 * emu_per_inch)
    try:
        from PIL import Image
        with Image.open(path) as im:
            width, height = im.size
    except Exception:
        return max_cx, int(3.1 * emu_per_inch)
    cx = max_cx
    cy = int(cx * height / width)
    if cy > max_cy:
        cy = max_cy
        cx = int(cy * width / height)
    return cx, cy


def docx_image(rid: str, name: str, docpr_id: int, cx: int, cy: int) -> str:
    return f"""
<w:p><w:r><w:drawing>
<wp:inline distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="{cx}" cy="{cy}"/>
<wp:docPr id="{docpr_id}" name="{xml_escape(name)}"/>
<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic>
<pic:nvPicPr><pic:cNvPr id="0" name="{xml_escape(name)}"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"/></pic:spPr>
</pic:pic>
</a:graphicData></a:graphic>
</wp:inline>
</w:drawing></w:r></w:p>
"""


def write_docx_report(stats: dict, n_total: int) -> None:
    readings = chart_readings(stats)
    conclusions = build_conclusions(stats, n_total)
    recommendations = build_recommendations()
    body: list[str] = []
    images: list[tuple[str, Path]] = []

    body.append(docx_heading("Informe exploratorio Cafecito", 1))
    body.append(docx_paragraph("Cafecito BA en tu barrio - gráficos y lectura agregada.", size=24, bold=True))
    body.append(docx_paragraph(f"Respuestas analizadas: {n_total}."))
    body.append(docx_paragraph("Muestra exploratoria, no representativa del público total del evento. No incluye correos, nombres, teléfonos, barrios/localidades libres ni identificadores personales."))

    body.append(docx_heading("Nota metodológica", 2))
    body.append(docx_paragraph("Los gráficos se regeneran desde el XLSX original en modo solo lectura. Las preguntas multi-respuesta se cuentan sobre respondentes y pueden sumar más de 100%. La opción 'Por amigos, familia o conocidos' se trata como una sola categoría."))

    for key in GRAPH_ORDER:
        img = GRAF_DIR / f"{key}.png"
        if not img.exists():
            continue
        body.append(docx_heading(LABELS[key], 2))
        rid = f"rId{len(images) + 1}"
        media_name = f"image{len(images) + 1}.png"
        cx, cy = image_extent(img)
        body.append(docx_image(rid, img.name, len(images) + 1, cx, cy))
        body.append(docx_paragraph("Lectura: " + readings.get(key, "Lectura agregada exploratoria.")))
        images.append((media_name, img))

    body.append(docx_heading("Conclusiones finales", 2))
    for txt in conclusions:
        body.append(docx_paragraph("- " + txt))

    body.append(docx_heading("Recomendaciones para próximos relevamientos", 2))
    for txt in recommendations:
        body.append(docx_paragraph("- " + txt))

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
<w:body>
{''.join(body)}
<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1080" w:bottom="1440" w:left="1080"/></w:sectPr>
</w:body></w:document>"""

    rels_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for i, (media_name, _) in enumerate(images, 1):
        rels_xml.append(
            f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{media_name}"/>'
        )
    rels_xml.append("</Relationships>")

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
    package_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    with zipfile.ZipFile(DOCX_REPORT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", package_rels)
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/_rels/document.xml.rels", "".join(rels_xml))
        for media_name, img in images:
            zf.write(img, f"word/media/{media_name}")


# ------------------------------------------------------------------------- main

def main() -> int:
    records = read_xlsx(XLSX)
    n_total = len(records)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    GRAF_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Control de completitud del correo (sin exponerlo).
    con_correo = sum(1 for r in records if not is_blank(r.get("correo", "")))
    DECISIONES.append(
        f"Correo (B): {con_correo}/{n_total} respuestas lo traían. Se EXCLUYE de todo output; "
        "solo se reporta este conteo de completitud."
    )
    DECISIONES.append(
        "Marca temporal (A) y barrio/localidad libre (G) se tratan como sensibles: no se publican "
        "valores individuales."
    )
    DECISIONES.append(
        "No se imputan faltantes. Normalización aplicada: trim de espacios y colapso de espacios "
        "múltiples. No se corrigen categorías de texto libre."
    )
    DECISIONES.append(
        "como_se_entero (J) y eventos_futuros (L) son multi-respuesta: se desagregan por coma; "
        "los porcentajes se calculan sobre respondentes y suman más de 100%."
    )
    DECISIONES.append(
        "La opción canónica 'Por amigos, familia o conocidos' contiene coma interna y se protege "
        "antes de separar multi-respuestas."
    )

    # 1) resumen_variables.csv -----------------------------------------------
    with (OUT_DIR / "resumen_variables.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["columna_xlsx", "variable", "tipo", "respuestas_no_vacias",
                    "valores_unicos", "sensible_no_publicada"])
        for letter, key in COLS.items():
            no_vacias = sum(1 for r in records if not is_blank(r.get(key, "")))
            if key in CERRADAS_MULTI:
                c, _ = count_multi(records, key)
                tipo = "cerrada_multi"
                uniq = len(c)
            elif key in CERRADAS_SIMPLES:
                tipo = "cerrada_simple"
                uniq = len(count_simple(records, key))
            elif key in SENSIBLE:
                tipo = "sensible"
                uniq = ""  # no se calcula/expone cardinalidad fina
            else:
                tipo = "texto_libre"
                uniq = len({norm_space(r.get(key, "")) for r in records if not is_blank(r.get(key, ""))})
            w.writerow([letter, key, tipo, no_vacias, uniq, "si" if key in SENSIBLE else "no"])

    # 2) resumen_respuestas_cerradas.csv + gráficos ---------------------------
    rows_cerradas = []
    graf_generados = []
    stats = {}
    for key in CERRADAS_SIMPLES:
        c = count_simple(records, key)
        base = sum(c.values())
        items = ordered_items(key, c)
        stats[key] = {"items": items, "base": base, "multi": False}
        for val, n in items:
            rows_cerradas.append([LABELS[key], val, n, round(n / base * 100, 1) if base else 0, base, "no"])
        out = GRAF_DIR / f"{key}.png"
        if barplot(items, LABELS[key], out, base, multi=False):
            graf_generados.append(out.name)

    for key in CERRADAS_MULTI:
        c, base = count_multi(records, key)
        # para el CSV: top y cola; para el gráfico: top 12
        items_all = c.most_common()
        stats[key] = {"items": items_all, "base": base, "multi": True}
        for val, n in items_all:
            rows_cerradas.append([LABELS[key], val, n, round(n / base * 100, 1) if base else 0, base, "si"])
        items_plot = items_all[:12]
        out = GRAF_DIR / f"{key}.png"
        if barplot(items_plot, LABELS[key], out, base, multi=True):
            graf_generados.append(out.name)

    with (OUT_DIR / "resumen_respuestas_cerradas.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pregunta", "respuesta", "cantidad", "porcentaje", "base_n", "multi_respuesta"])
        w.writerows(rows_cerradas)

    # 3) cruces simples (solo con base suficiente) ----------------------------
    cruces_txt = []
    cruces_def = [
        ("rango_edad", "como_se_entero_simple", "Edad x cómo se enteró (canal principal)"),
        ("donde_vivis", "que_intereso", "Procedencia x qué le interesó"),
        ("primera_vez", "acepta_contacto", "Primera vez x acepta contacto"),
        ("genero", "que_intereso", "Género x qué le interesó"),
    ]
    # canal principal = primer canal declarado (para cruce legible)
    for r in records:
        partes = split_multi(r.get("como_se_entero", ""), "como_se_entero")
        r["como_se_entero_simple"] = partes[0] if partes else ""

    for a, b, titulo in cruces_def:
        res = crosstab(records, a, b, min_cell_base=8)
        if res is None:
            cruces_txt.append(f"### {titulo}\n\n_No se reporta: base insuficiente para un cruce prudente._\n")
            continue
        table, base = res
        cruces_txt.append(f"### {titulo}\n\n*Base: {base} respuestas. Lectura exploratoria; celdas chicas no son concluyentes.*\n")
        cats_b = sorted({bk for row in table.values() for bk in row})
        header = "| " + LABELS.get(a, a) + " \\ " + (LABELS.get(b, b)) + " | " + " | ".join(cats_b) + " | Total |"
        sep = "|" + "---|" * (len(cats_b) + 2)
        cruces_txt.append(header)
        cruces_txt.append(sep)
        for ak in sorted(table):
            rowvals = [str(table[ak].get(bk, 0)) for bk in cats_b]
            tot = sum(table[ak].values())
            cruces_txt.append("| " + ak + " | " + " | ".join(rowvals) + f" | {tot} |")
        cruces_txt.append("")

    # 4) resumen_respuestas_abiertas.md --------------------------------------
    abiertas = []
    abiertas.append("# Resumen cualitativo — respuestas abiertas / multi-respuesta Cafecito\n")
    abiertas.append("**Muestra exploratoria (n = %d). No representativa.** Sin datos personales.\n" % n_total)

    # K (qué interesó): semi-cerrada, ya cuantificada; aquí lectura cualitativa
    ck = count_simple(records, "que_intereso")
    abiertas.append("## Qué fue lo que más interesó (K)\n")
    abiertas.append("Respuesta única por persona, opciones acotadas. Conteo:\n")
    for val, n in ck.most_common():
        abiertas.append(f"- **{val}** — {n}")
    abiertas.append("")

    # L (eventos futuros): categorías agregadas + cola libre
    cl, base_l = count_multi(records, "eventos_futuros")
    abiertas.append("## Tipos de eventos que les interesarían a futuro (L)\n")
    abiertas.append(f"Multi-respuesta (base {base_l}; suma >100%). Categorías más mencionadas:\n")
    for val, n in cl.most_common(12):
        abiertas.append(f"- **{val}** — {n}")
    cola = [v for v, n in cl.items() if n == 1]
    if cola:
        abiertas.append("\nMenciones únicas (cola de texto libre, temas sueltos, anonimizados):\n")
        abiertas.append("> " + "; ".join(sorted(cola)[:20]))
    abiertas.append("")
    abiertas.append("## Lectura prudente\n")
    abiertas.append(
        "- El interés declarado a futuro se concentra en **vino, pastelería, food trucks y café**, "
        "coherente con la temática del evento.\n"
        "- Hay demanda de formatos participativos (clases/talleres, degustaciones) y de "
        "**ferias y mercados**, que conecta con otras líneas del área.\n"
        "- La cola de menciones únicas sugiere intereses diversos; no se generaliza por su bajo N."
    )

    (OUT_DIR / "resumen_respuestas_abiertas.md").write_text("\n".join(abiertas) + "\n", encoding="utf-8")

    # 5) volcar cruces a un archivo para que el informe los referencie
    (OUT_DIR / "cruces_simples.md").write_text(
        "# Cruces simples Cafecito (exploratorios)\n\n" + "\n".join(cruces_txt) + "\n",
        encoding="utf-8",
    )

    # 6) decisiones de limpieza
    (OUT_DIR / "decisiones_limpieza.md").write_text(
        "# Decisiones de limpieza — análisis Cafecito\n\n" +
        "\n".join(f"- {d}" for d in DECISIONES) + "\n",
        encoding="utf-8",
    )

    # 7) informe, README y DOCX ----------------------------------------------
    write_markdown_report(records, stats, graf_generados)
    write_readme()
    write_docx_report(stats, n_total)

    # ---- consola ----
    print("=" * 70)
    print("Análisis Cafecito (exploratorio)")
    print(f"  XLSX (solo lectura): {XLSX.relative_to(REPO_ROOT)}")
    print(f"  Respuestas: {n_total}")
    print(f"  Correo presente en: {con_correo} (excluido de outputs)")
    print(f"  Gráficos generados: {len(graf_generados)} -> {GRAF_DIR.relative_to(REPO_ROOT)}")
    for g in graf_generados:
        print(f"    + {g}")
    print(f"  Outputs en: {OUT_DIR.relative_to(REPO_ROOT)}")
    print(f"  Informe Markdown: {REPORT_MD.relative_to(REPO_ROOT)}")
    print(f"  DOCX con gráficos: {DOCX_REPORT.relative_to(REPO_ROOT)}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
