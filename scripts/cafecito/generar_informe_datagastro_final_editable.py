"""Genera una version EDITABLE (de prueba) del informe Cafecito DataGastro.

Misma maqueta, mismos datos, mismos graficos y misma marca que el generador
FINAL (`generar_informe_datagastro_final.py`), pero los TEXTOS visibles del PDF
se leen desde un archivo editable:

    docs/cafecito/contenido_editable_informe_cafecito.yaml

Asi una persona puede corregir titulos, bajadas, notas metodologicas,
recomendaciones, etc. sin tocar este script ni el generador final.

Que reutiliza del generador FINAL (importado, no duplicado):
  - Lectura del XLSX original (solo lectura, no lo modifica).
  - Calculo de estadisticas y del payload de numeros (`stats_payload`).
  - Dibujo de mapas y graficos (mismos PNG `*_final.png`).
  - Todas las primitivas de layout: header, footer, add_box, KPI, hbar, donut,
    stacked, mini_table, add_image, etc.

Que NO hace:
  - No sobrescribe `INFORME_CAFECITO_DATAGASTRO_FINAL.pdf` (ni en outputs ni en
    Cafesito/final). Escribe a archivos con sufijo `_EDITABLE_TEST`.
  - No modifica el XLSX original ni los CSV de datos.
  - No regenera el Markdown ni el README del informe final.

Salidas:
  - outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_FINAL_EDITABLE_TEST.pdf
  - Cafesito/final/INFORME_CAFECITO_DATAGASTRO_FINAL_EDITABLE_TEST.pdf

Uso:
    python scripts/cafecito/generar_informe_datagastro_final_editable.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Reutilizamos TODO el motor del generador final: datos, calculos, layout y
# primitivas de dibujo. Solo redefinimos las paginas para tomar textos del YAML.
from scripts.cafecito import generar_informe_datagastro_final as final  # noqa: E402
from scripts.cafecito.generar_informe_datagastro_final import (  # noqa: E402
    Counter,
    Counter as _Counter,  # re-export defensivo
    INK,
    ORANGE,
    GREEN,
    BLUE,
    GREY,
    WHITE,
    LIGHT,
    LINE,
    SOFT_BLUE,
    SOFT_ORANGE,
    SOFT_GREEN,
    add_box,
    add_image,
    add_kpi_cards,
    clean_text,
    crosstab,
    donut,
    footer,
    hbar,
    header,
    items_dict,
    mini_table,
    page,
    pct_s,
    stacked,
    wrap_text,
)

DOCS_DIR = REPO_ROOT / "docs" / "cafecito"
OUT_DIR = REPO_ROOT / "outputs" / "cafecito"
FINAL_DIR = REPO_ROOT / "Cafesito" / "final"

CONTENIDO_YAML = DOCS_DIR / "contenido_editable_informe_cafecito.yaml"

# Salidas con sufijo _EDITABLE_TEST: nunca pisan el FINAL.
PDF_TEST = OUT_DIR / "INFORME_CAFECITO_DATAGASTRO_FINAL_EDITABLE_TEST.pdf"
FINAL_PDF_TEST = FINAL_DIR / "INFORME_CAFECITO_DATAGASTRO_FINAL_EDITABLE_TEST.pdf"

# Mapas/graficos: reutilizamos las mismas rutas y funciones del generador final.
MAPA_COMUNAL = final.MAPA_COMUNAL
MAPA_SEDES = final.MAPA_SEDES
MAPA_COMBINADO = final.MAPA_COMBINADO


# --------------------------------------------------------------- mini YAML
# Parser minimo del subconjunto de YAML usado por el contenido editable.
# Evita depender de PyYAML (no instalado en el venv del proyecto). Soporta:
#   - claves "clave: valor"
#   - strings entre comillas dobles, con \n literal interpretado
#   - listas de escalares ("- texto")
#   - listas de mapas ("- clave: valor" + claves indentadas)
#   - anidamiento por indentacion (2 espacios)
# No soporta YAML avanzado (anclas, flow, multilinea |, etc.): no se usa aca.

def _parse_scalar(token: str):
    token = token.strip()
    if token == "":
        return None
    if token[0] in "\"'" and token[-1] == token[0] and len(token) >= 2:
        inner = token[1:-1]
        # Interpretar saltos de linea escritos como \n en el YAML.
        return inner.replace("\\n", "\n")
    return token


def _strip_comment(line: str) -> str:
    """Quita comentarios '# ...' fuera de comillas."""
    out = []
    in_str = False
    quote = ""
    for ch in line:
        if in_str:
            out.append(ch)
            if ch == quote:
                in_str = False
        else:
            if ch in "\"'":
                in_str = True
                quote = ch
                out.append(ch)
            elif ch == "#":
                break
            else:
                out.append(ch)
    return "".join(out)


def _load_yaml(path: Path) -> dict:
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    # Pre-proceso: indentacion + contenido, descartando vacias y comentarios.
    items = []  # (indent, text)
    for line in raw_lines:
        stripped = _strip_comment(line).rstrip()
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        items.append((indent, stripped.strip()))

    pos = [0]

    def parse_block(min_indent: int):
        # Decide si el bloque actual es lista o mapa segun el primer item.
        if pos[0] >= len(items):
            return None
        indent, text = items[pos[0]]
        if text.startswith("- "):
            return parse_list(indent)
        return parse_map(min_indent)

    def parse_map(indent_level: int) -> dict:
        result: dict = {}
        while pos[0] < len(items):
            indent, text = items[pos[0]]
            if indent < indent_level:
                break
            if text.startswith("- "):
                break
            key, _, rest = text.partition(":")
            key = key.strip()
            rest = rest.strip()
            pos[0] += 1
            if rest == "":
                # valor anidado (mapa o lista) en lineas siguientes
                child_indent = None
                if pos[0] < len(items):
                    child_indent = items[pos[0]][0]
                if child_indent is not None and child_indent > indent:
                    result[key] = parse_block(child_indent)
                else:
                    result[key] = None
            else:
                result[key] = _parse_scalar(rest)
        return result

    def parse_list(indent_level: int) -> list:
        result: list = []
        while pos[0] < len(items):
            indent, text = items[pos[0]]
            if indent < indent_level or not text.startswith("- "):
                break
            body = text[2:].strip()
            if ":" in body and not (body[:1] in "\"'"):
                # Item de lista que es un mapa: re-inyectar la primera clave.
                key, _, rest = body.partition(":")
                pos[0] += 1
                entry: dict = {}
                rest = rest.strip()
                if rest == "":
                    # mapa cuyas claves estan en lineas siguientes mas indentadas
                    child_indent = items[pos[0]][0] if pos[0] < len(items) else indent
                    sub = parse_map(child_indent)
                    entry = sub
                else:
                    entry[key.strip()] = _parse_scalar(rest)
                    # Posibles claves adicionales del mismo item (mas indentadas).
                    if pos[0] < len(items) and items[pos[0]][0] > indent:
                        more = parse_map(items[pos[0]][0])
                        entry.update(more)
                result.append(entry)
            else:
                pos[0] += 1
                result.append(_parse_scalar(body))
        return result

    return parse_map(0)


# ----------------------------------------------------------- formateo textos

def fmt(value, numbers: dict):
    """Reemplaza marcadores {clave} por numeros calculados, robusto a faltantes.

    Recorre recursivamente strings, listas y dicts (p. ej. los KPIs y tarjetas,
    que son listas de mapas), para que ningun marcador {...} quede sin sustituir.
    """
    if isinstance(value, str):
        try:
            return value.format(**numbers)
        except (KeyError, IndexError):
            return value
    if isinstance(value, list):
        return [fmt(v, numbers) for v in value]
    if isinstance(value, dict):
        return {k: fmt(v, numbers) for k, v in value.items()}
    return value


def number_context(p: dict, ranking_rows: list[dict], sedes_comuna: list[dict], stats: dict) -> dict:
    """Arma el diccionario de numeros disponibles para los marcadores {...}."""
    numeric = [r for r in ranking_rows if str(r["comuna"]).isdigit()][:5]
    top_comunas = ", ".join(f"Comuna {r['comuna']} ({r['cantidad_respuestas']})" for r in numeric)
    top = [r for r in sedes_comuna if str(r["comuna"]).isdigit()][:6]
    top_sedes = ", ".join(f"Comuna {r['comuna']} ({r['cantidad_sedes']})" for r in top)
    gen = items_dict(stats, "genero")
    ctx = dict(p)
    ctx["nb"] = gen.get("No binario", 0)
    ctx["top_comunas"] = top_comunas
    ctx["top_sedes"] = top_sedes
    return ctx


# --------------------------------------------------------------------- paginas
# Cada funcion replica la maqueta del generador final pero toma los textos
# desde el dict `c` (contenido del YAML), ya formateado con los numeros.

def cover_page(pdf: PdfPages, c: dict) -> None:
    fig = page()
    fig.patches.append(Rectangle((0, 0.70), 1, 0.30, transform=fig.transFigure, facecolor=INK, edgecolor="none"))
    fig.patches.append(Rectangle((0, 0.688), 1, 0.012, transform=fig.transFigure, facecolor=ORANGE, edgecolor="none"))
    fig.text(0.065, 0.93, c["kicker_marca"], color=WHITE, fontsize=13, fontweight="bold")
    fig.text(0.935, 0.93, c["kicker_tipo"], color="#c9d6e4", fontsize=10, ha="right")
    fig.text(0.065, 0.84, c["titulo"], color=WHITE, fontsize=34, fontweight="bold", va="top", linespacing=0.95)
    fig.text(0.065, 0.728, c["subtitulo"], color="#dbe5ef", fontsize=12.5, va="center")
    fig.text(0.065, 0.585, c["bajada_linea_1"], color=INK, fontsize=12.5, va="center")
    fig.text(0.065, 0.555, c["bajada_linea_2"], color=INK, fontsize=12.5, va="center")
    fig.lines.append(Line2D([0.065, 0.55], [0.50, 0.50], color=LINE, lw=1.2, transform=fig.transFigure))
    y = 0.455
    for eje in c["ejes"]:
        fig.text(0.065, y, eje["titulo"], color=ORANGE, fontsize=11, fontweight="bold", va="center")
        fig.text(0.235, y, eje["descripcion"], color="#333333", fontsize=10.5, va="center")
        y -= 0.040
    add_box(
        fig, 0.065, 0.175, 0.87, 0.085, c["advertencia_titulo"],
        c["advertencia_texto"],
        face=SOFT_ORANGE, edge=ORANGE, body_size=10.0, title_size=10.5,
    )
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def summary_page(pdf: PdfPages, c: dict, page_no: int) -> None:
    fig = page()
    y = header(fig, page_no, c["titulo"], c["subtitulo"])
    cards = [(k["valor"], k["label"], k["nota"]) for k in c["kpis"]]
    add_kpi_cards(fig, cards, y - 0.105)
    add_box(fig, 0.065, 0.420, 0.42, 0.245, c["que_sabemos_titulo"], c["que_sabemos"],
            face=WHITE, edge=BLUE, bullet=True, body_size=8.9)
    add_box(fig, 0.515, 0.420, 0.42, 0.245, c["oportunidad_titulo"], c["oportunidad"],
            face=SOFT_BLUE, edge=BLUE, bullet=True, body_size=8.9)
    add_box(fig, 0.065, 0.225, 0.42, 0.170, c["decisiones_titulo"], c["decisiones"],
            face=SOFT_GREEN, edge=GREEN, bullet=True, body_size=8.9)
    add_box(fig, 0.515, 0.225, 0.42, 0.170, c["recomendaciones_titulo"], c["recomendaciones"],
            face=WHITE, edge=ORANGE, bullet=True, body_size=8.9)
    add_box(fig, 0.065, 0.105, 0.87, 0.085, c["cuidado_titulo"], c["cuidado_texto"],
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def decision_page(pdf: PdfPages, c: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    x0, y0 = 0.065, 0.660
    for i, card in enumerate(c["tarjetas"]):
        col = i % 2
        row = i // 2
        x = x0 + col * 0.455
        y = y0 - row * 0.150
        add_box(fig, x, y, 0.415, 0.115, card["titulo"], card["texto"],
                face=WHITE if i % 2 else LIGHT, edge=BLUE if i < 4 else ORANGE)
    add_box(fig, 0.065, 0.150, 0.87, 0.140, c["lectura_titulo"], c["lectura_texto"],
            face=SOFT_BLUE, edge=INK, body_size=9.4)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def profile_page(pdf: PdfPages, c: dict, stats: dict, p: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    hbar(fig, [0.085, 0.500, 0.40, 0.300], stats["rango_edad"]["items"], stats["rango_edad"]["base"],
         c["titulo_grafico_edad"], accents={"18 a 24", "25 a 34", "35 a 44"})
    stacked(fig, [0.560, 0.745, 0.360, 0.072], stats["genero"]["items"], stats["genero"]["base"],
            c["titulo_grafico_genero"], [INK, ORANGE, GREY])
    caba = p["caba"]
    no_caba = p["n"] - caba
    fig.text(0.575, 0.655, c["titulo_procedencia"], color=INK, fontsize=10.5, fontweight="bold", va="top")
    donut(fig, [0.575, 0.480, 0.320, 0.165], [("CABA", caba), ("No CABA", no_caba)],
          "", f"{pct_s(caba, p['n'])}\nCABA", [BLUE, "#e6b17e"])
    add_box(fig, 0.065, 0.255, 0.42, 0.180, c["lectura_titulo"], c["lectura_texto"],
            face=SOFT_BLUE, edge=BLUE, body_size=9.2)
    add_box(fig, 0.515, 0.255, 0.42, 0.180, c["cuidado_titulo"], c["cuidado_texto"],
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.2)
    add_box(fig, 0.065, 0.105, 0.87, 0.115, c["decision_titulo"], c["decision_texto"],
            face=SOFT_GREEN, edge=GREEN, body_size=9.2)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def public_territory_page(pdf: PdfPages, c: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    add_image(fig, MAPA_COMUNAL, [0.065, 0.375, 0.87, 0.475])
    add_box(fig, 0.065, 0.235, 0.42, 0.115, c["como_leer_titulo"], c["como_leer_texto"],
            face=SOFT_BLUE, edge=BLUE, body_size=8.4)
    add_box(fig, 0.515, 0.235, 0.42, 0.115, c["cuidado_titulo"], c["cuidado_texto"],
            face=SOFT_ORANGE, edge=ORANGE, body_size=8.4)
    add_box(fig, 0.065, 0.105, 0.87, 0.100, c["lectura_titulo"], c["lectura_texto"],
            face=SOFT_GREEN, edge=GREEN, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def network_page(pdf: PdfPages, c: dict, network_note: str, page_no: int) -> None:
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    add_image(fig, MAPA_SEDES, [0.065, 0.395, 0.87, 0.455])
    add_box(fig, 0.065, 0.230, 0.255, 0.125, c["en_numeros_titulo"], c["en_numeros"],
            face=WHITE, edge=BLUE, bullet=True, body_size=8.1)
    add_box(fig, 0.345, 0.230, 0.590, 0.125, c["comunas_titulo"], c["comunas_texto"],
            face=SOFT_BLUE, edge=BLUE, body_size=8.4)
    add_box(fig, 0.065, 0.105, 0.87, 0.095, c["como_leer_titulo"], network_note,
            face=SOFT_ORANGE, edge=ORANGE, body_size=8.8)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def public_vs_network_page(pdf: PdfPages, c: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    add_image(fig, MAPA_COMBINADO, [0.065, 0.395, 0.87, 0.455])
    add_box(fig, 0.065, 0.230, 0.42, 0.125, c["coincidencias_titulo"], c["coincidencias"],
            face=SOFT_BLUE, edge=BLUE, bullet=True, body_size=8.3)
    add_box(fig, 0.515, 0.230, 0.42, 0.125, c["oportunidad_titulo"], c["oportunidad"],
            face=SOFT_GREEN, edge=GREEN, bullet=True, body_size=8.3)
    add_box(fig, 0.065, 0.105, 0.87, 0.095, c["cuidado_titulo"], c["cuidado_texto"],
            face=SOFT_ORANGE, edge=ORANGE, body_size=8.8)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def channels_page(pdf: PdfPages, c: dict, stats: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    hbar(fig, [0.080, 0.470, 0.50, 0.350], stats["como_se_entero"]["items"], stats["como_se_entero"]["base"],
         c["titulo_grafico"], color=BLUE,
         accents={"Instagram", "Por amigos, familia o conocidos", "Pase por la zona y lo ví"}, multi=True)
    add_box(fig, 0.620, 0.660, 0.315, 0.160, c["lectura_titulo"], c["lectura_texto"],
            face=SOFT_BLUE, edge=BLUE, body_size=8.8)
    add_box(fig, 0.620, 0.470, 0.315, 0.170, c["oportunidad_titulo"], c["oportunidad_texto"],
            face=SOFT_GREEN, edge=GREEN, body_size=8.8)
    add_box(fig, 0.065, 0.230, 0.87, 0.190, c["pedir_titulo"], c["pedir"],
            face=WHITE, edge=ORANGE, bullet=True, body_size=8.8)
    add_box(fig, 0.065, 0.105, 0.87, 0.095, c["proximas_titulo"], c["proximas_texto"],
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def loyalty_page(pdf: PdfPages, c: dict, stats: dict, p: dict, records: list[dict], page_no: int) -> None:
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    stacked(fig, [0.085, 0.700, 0.420, 0.110], stats["primera_vez"]["items"], stats["primera_vez"]["base"],
            c["titulo_grafico_primera_vez"], [INK, ORANGE, GREY])
    donut(fig, [0.600, 0.610, 0.250, 0.210], stats["acepta_contacto"]["items"], c["titulo_grafico_contacto"],
          f"{pct_s(p['contact_yes'], p['contact_base'])}", [GREEN, GREY])
    table = crosstab(records, "primera_vez", "acepta_contacto")
    rows = []
    label_disp = {
        "No, ya participé de otros eventos": "Recurrentes",
        "Si, es la primera vez": "Primera vez",
        "No estoy seguro/a": "No está seguro/a",
    }
    total_acepta = total_base = 0
    for label, disp in label_disp.items():
        row = table.get(label, Counter())
        if row:
            acepta = row.get("Si, acepto", 0)
            base_n = sum(row.values())
            total_acepta += acepta
            total_base += base_n
            rows.append((disp, str(acepta), str(base_n)))
    rows.append(("Total", str(total_acepta), str(total_base)))
    mini_table(fig, 0.090, 0.405, 0.760, 0.120, rows, c["titulo_tabla"])
    add_box(fig, 0.065, 0.235, 0.42, 0.150, c["lectura_titulo"], c["lectura_texto"],
            face=SOFT_BLUE, edge=BLUE, body_size=9.2)
    add_box(fig, 0.515, 0.235, 0.42, 0.150, c["decision_titulo"], c["decision_texto"],
            face=SOFT_GREEN, edge=GREEN, body_size=9.2)
    add_box(fig, 0.065, 0.110, 0.87, 0.100, c["cuidado_titulo"], c["cuidado_texto"],
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def motivations_page(pdf: PdfPages, c: dict, stats: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    hbar(fig, [0.085, 0.560, 0.40, 0.250], stats["que_intereso"]["items"], stats["que_intereso"]["base"],
         c["titulo_grafico_atrajo"], color=final.COFFEE,
         accents={"Probar café / cafeterías", "Pasear o hacer una salida"})
    hbar(fig, [0.560, 0.470, 0.375, 0.340], stats["eventos_futuros"]["items"], stats["eventos_futuros"]["base"],
         c["titulo_grafico_futuro"], color=BLUE,
         accents={"Vino", "Pasteleria", "Food trucks", "Café", "Ferias y mercados"}, limit=8, multi=True)
    add_box(fig, 0.065, 0.295, 0.42, 0.140, c["atrajo_titulo"], c["atrajo_texto"],
            face=SOFT_BLUE, edge=BLUE, body_size=9.0)
    add_box(fig, 0.515, 0.295, 0.42, 0.140, c["programacion_titulo"], c["programacion_texto"],
            face=SOFT_GREEN, edge=GREEN, body_size=9.0)
    add_box(fig, 0.065, 0.110, 0.87, 0.155, c["cuidado_titulo"], c["cuidado"],
            face=SOFT_ORANGE, edge=ORANGE, bullet=True, body_size=9.0)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def conclusions_page(pdf: PdfPages, c: dict, page_no: int) -> None:
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    fig.text(0.065, 0.805, c["cierre_titulo"], color=INK, fontsize=11.5, fontweight="bold", va="top")
    yy = 0.778
    for t in c["cierre"]:
        for line in wrap_text("• " + t, 108):
            fig.text(0.065, yy, line, color="#222222", fontsize=9.6, va="top")
            yy -= 0.0185
        yy -= 0.007
    add_box(fig, 0.065, 0.395, 0.42, 0.120, c["decision_titulo"], c["decision_texto"],
            face=SOFT_GREEN, edge=GREEN, body_size=9.2)
    add_box(fig, 0.515, 0.395, 0.42, 0.120, c["recomendacion_titulo"], c["recomendacion_texto"],
            face=WHITE, edge=ORANGE, body_size=9.2)
    add_box(fig, 0.065, 0.250, 0.42, 0.120, c["lectura_titulo"], c["lectura_texto"],
            face=SOFT_BLUE, edge=BLUE, body_size=9.2)
    add_box(fig, 0.515, 0.250, 0.42, 0.120, c["cuidado_titulo"], c["cuidado_texto"],
            face=SOFT_ORANGE, edge=ORANGE, body_size=9.2)
    add_box(fig, 0.065, 0.105, 0.87, 0.115, c["proximas_titulo"], c["proximas"],
            face=LIGHT, edge=INK, bullet=True, body_size=8.8)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


def annex_page(pdf: PdfPages, c: dict, network_note: str, page_no: int) -> None:
    fig = page()
    header(fig, page_no, c["titulo"], c["subtitulo"])
    add_box(fig, 0.065, 0.610, 0.42, 0.205, c["base_titulo"], c["base"],
            face=WHITE, edge=BLUE, bullet=True, body_size=8.6)
    add_box(fig, 0.515, 0.610, 0.42, 0.205, c["privacidad_titulo"], c["privacidad"],
            face=SOFT_ORANGE, edge=ORANGE, bullet=True, body_size=8.6)
    add_box(fig, 0.065, 0.380, 0.42, 0.205, c["multi_titulo"], c["multi"],
            face=LIGHT, edge=INK, bullet=True, body_size=8.6)
    add_box(fig, 0.515, 0.380, 0.42, 0.205, c["red_titulo"], c["red"],
            face=LIGHT, edge=INK, bullet=True, body_size=8.6)
    add_box(fig, 0.065, 0.190, 0.87, 0.155, c["como_leer_titulo"], network_note,
            face=SOFT_BLUE, edge=BLUE, body_size=9.2)
    footer(fig)
    pdf.savefig(fig)
    final.plt.close(fig)


# ----------------------------------------------------------------------- build

def write_pdf(content: dict, records: list[dict], stats: dict, p: dict,
              ranking_rows: list[dict], sedes_comuna: list[dict]) -> int:
    pages = content["paginas"]
    numbers = number_context(p, ranking_rows, sedes_comuna, stats)
    network_note = content.get("network_note", final.NETWORK_NOTE)

    def page_content(key: str) -> dict:
        return {k: fmt(v, numbers) for k, v in pages[key].items()}

    # El footer del informe se respeta desde el YAML (footer global del modulo
    # final controla el texto; aca lo sincronizamos si difiere).
    final.FOOTER = content.get("footer", final.FOOTER)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    with PdfPages(PDF_TEST) as pdf:
        cover_page(pdf, page_content("portada"))
        summary_page(pdf, page_content("resumen_ejecutivo"), 2)
        decision_page(pdf, page_content("que_permite_decidir"), 3)
        profile_page(pdf, page_content("perfil_muestra"), stats, p, 4)
        public_territory_page(pdf, page_content("lectura_territorial"), 5)
        network_page(pdf, page_content("red_cafeterias"), network_note, 6)
        public_vs_network_page(pdf, page_content("publico_y_red"), 7)
        channels_page(pdf, page_content("canales_llegada"), stats, 8)
        loyalty_page(pdf, page_content("vinculo_fidelizacion"), stats, p, records, 9)
        motivations_page(pdf, page_content("motivaciones"), stats, 10)
        conclusions_page(pdf, page_content("conclusiones"), 11)
        annex_page(pdf, page_content("anexo"), network_note, 12)
    shutil.copy2(PDF_TEST, FINAL_PDF_TEST)
    return 12


def main() -> None:
    if not CONTENIDO_YAML.exists():
        raise SystemExit(f"No se encontro el contenido editable: {CONTENIDO_YAML}")
    content = _load_yaml(CONTENIDO_YAML)

    # Datos y graficos: identicos al generador final (no se duplican).
    final.ensure_analysis_outputs()
    records = final.base.read_xlsx(final.base.XLSX)
    stats = final.build_stats(records)
    p = final.stats_payload(records, stats)
    ranking_rows = final.read_csv(final.RANKING_COMUNAL)
    sedes_comuna = final.read_csv(final.RESUMEN_SEDES_COMUNA)

    sedes_all = final.read_csv(final.SEDES_CSV)
    sedes_mapa = [s for s in sedes_all if s.get("usar_en_mapa", "").strip() == "si"]

    final.draw_mapa_comunal_publico(ranking_rows)
    final.draw_plan_barras(stats)
    final.draw_mapa_sedes(sedes_mapa)
    final.draw_mapa_combinado(sedes_mapa, ranking_rows)

    pages = write_pdf(content, records, stats, p, ranking_rows, sedes_comuna)

    print("=" * 72)
    print("Informe Cafecito DataGastro EDITABLE (TEST)")
    print(f"  Contenido editable: {CONTENIDO_YAML}")
    print(f"  Respuestas: {len(records)}")
    print(f"  Sedes mapeadas (usar_en_mapa=si): {len(sedes_mapa)}")
    print(f"  Paginas PDF: {pages}")
    print(f"  PDF test: {PDF_TEST}")
    print(f"  Copia test: {FINAL_PDF_TEST}")
    print("  (El PDF FINAL original NO fue modificado.)")
    print("=" * 72)


if __name__ == "__main__":
    main()
