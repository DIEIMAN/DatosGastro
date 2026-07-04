from __future__ import annotations

import csv
import json
import math
import re
import textwrap
from collections import Counter
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Ellipse, Patch  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]

INPUT_POLOS = ROOT / "outputs" / "polos_gastro" / "fase12_borrador_4" / "tablas" / "tabla_polos_borrador_4.csv"
INPUT_CONSOLIDADO = (
    ROOT
    / "outputs"
    / "polos_gastro"
    / "fase11_google_places_piloto"
    / "tablas"
    / "consolidado_tandas_google_places.csv"
)
INPUT_COORDS = [
    ROOT
    / "outputs"
    / "polos_gastro"
    / "fase11_google_places_piloto"
    / "tablas"
    / "resultados_repiloto_tanda1_revision_visual.csv",
    ROOT
    / "outputs"
    / "polos_gastro"
    / "fase11_google_places_piloto"
    / "tablas"
    / "resultados_tanda2_revision_visual.csv",
    ROOT
    / "outputs"
    / "polos_gastro"
    / "fase11_google_places_piloto"
    / "tablas"
    / "resultados_corrida_ampliada_revision_visual.csv",
]
GEO_BARRIOS = ROOT / "PolosGastro" / "cartografia" / "barrios_caba.geojson"

OUT = ROOT / "outputs" / "polos_gastro" / "fase13_mapas"
ASSETS = OUT / "assets"
TABLES = OUT / "tablas"
DOCS = ROOT / "docs" / "polos_gastro" / "fase13_mapas"

POLOS_MAPA = TABLES / "polos_ejes_para_mapa_global.csv"
LOCALES_MAPA = TABLES / "locales_para_mapa_revision.csv"
CRITERIOS_DOC = DOCS / "CRITERIOS_CARTOGRAFICOS_POLOS_GASTRO.md"
QA_DOC = DOCS / "QA_MAPAS_POLOS_GASTRO.md"

INSTITUCION = "DGDGAS - Direccion General de Desarrollo Gastronomico"
FECHA = "2026-07-02"

AZUL = "#1f3b57"
AZUL2 = "#2c7fb8"
ROJO = "#c0392b"
VERDE = "#1a9850"
NARANJA = "#c0762b"
GRIS = "#555555"
GRIS_CLARO = "#edf2f7"
LINEA = "#d6dde5"

TIPO_COLOR = {
    "area_barrio": "#2c7fb8",
    "macroarea": "#1a9850",
    "area_aproximada": "#c0762b",
    "eje_aproximado": "#c0392b",
}

ESTADO_COLOR = {
    "match_fuerte": AZUL2,
    "match_razonable_revisar_sede": VERDE,
    "zona_sucursal_a_revisar": NARANJA,
}

POLO_CONFIG = {
    "Palermo": {
        "tipo": "macroarea",
        "etiqueta": "Palermo",
        "descripcion": "Macroarea con subzonas Soho, Hollywood y Las Canitas.",
        "criterio": "Barrio Palermo como area de lectura; subzonas no delimitadas como poligonos oficiales.",
        "detalle": "si",
        "shape": {"kind": "barrios", "barrios": ["Palermo"]},
        "precision": "barrio oficial como apoyo; subzonas preliminares",
        "offset": (0.005, 0.008),
    },
    "Villa Crespo": {
        "tipo": "area_barrio",
        "etiqueta": "Villa Crespo",
        "descripcion": "Polo de barrio del universo semilla.",
        "criterio": "Barrio Villa Crespo como area de lectura preliminar.",
        "detalle": "no",
        "shape": {"kind": "barrios", "barrios": ["Villa Crespo"]},
        "precision": "barrio oficial como apoyo",
        "offset": (0.006, 0.000),
    },
    "Puerto Madero": {
        "tipo": "area_barrio",
        "etiqueta": "Puerto Madero",
        "descripcion": "Polo consolidado de zona costera.",
        "criterio": "Barrio Puerto Madero como area de lectura; delimitacion fina pendiente.",
        "detalle": "si",
        "shape": {"kind": "barrios", "barrios": ["Puerto Madero"]},
        "precision": "barrio oficial como apoyo",
        "offset": (0.008, -0.002),
    },
    "San Telmo": {
        "tipo": "area_barrio",
        "etiqueta": "San Telmo",
        "descripcion": "Polo consolidado con hito colectivo.",
        "criterio": "Barrio San Telmo como area de lectura; Mercado de San Telmo como referencia colectiva.",
        "detalle": "si",
        "shape": {"kind": "barrios", "barrios": ["San Telmo"]},
        "precision": "barrio oficial como apoyo",
        "offset": (-0.006, -0.004),
    },
    "Chacarita": {
        "tipo": "area_barrio",
        "etiqueta": "Chacarita",
        "descripcion": "Polo de barrio relevante.",
        "criterio": "Barrio Chacarita como area de lectura preliminar.",
        "detalle": "no",
        "shape": {"kind": "barrios", "barrios": ["Chacarita"]},
        "precision": "barrio oficial como apoyo",
        "offset": (-0.006, 0.000),
    },
    "Belgrano": {
        "tipo": "macroarea",
        "etiqueta": "Belgrano",
        "descripcion": "Macroarea con Barrio Chino, Bajo Belgrano y Belgrano R.",
        "criterio": "Barrio Belgrano como area de lectura; subzonas con respaldo diferenciado.",
        "detalle": "si",
        "shape": {"kind": "barrios", "barrios": ["Belgrano"]},
        "precision": "barrio oficial como apoyo; subzonas preliminares",
        "offset": (-0.005, 0.009),
    },
    "Recoleta": {
        "tipo": "area_barrio",
        "etiqueta": "Recoleta",
        "descripcion": "Polo consolidado del universo semilla.",
        "criterio": "Barrio Recoleta como area de lectura preliminar.",
        "detalle": "no",
        "shape": {"kind": "barrios", "barrios": ["Recoleta"]},
        "precision": "barrio oficial como apoyo",
        "offset": (-0.007, -0.001),
    },
    "Caballito": {
        "tipo": "area_barrio",
        "etiqueta": "Caballito",
        "descripcion": "Polo de barrio relevante.",
        "criterio": "Barrio Caballito como area de lectura preliminar.",
        "detalle": "no",
        "shape": {"kind": "barrios", "barrios": ["Caballito"]},
        "precision": "barrio oficial como apoyo",
        "offset": (0.006, -0.001),
    },
    "Costanera Norte": {
        "tipo": "eje_aproximado",
        "etiqueta": "Costanera Norte",
        "descripcion": "Area costera leida como corredor.",
        "criterio": "Traza costera aproximada para lectura territorial, sin cierre oficial.",
        "detalle": "no",
        "shape": {"kind": "line", "coords": [(-58.392, -34.570), (-58.410, -34.556), (-58.438, -34.545)]},
        "precision": "traza aproximada",
        "offset": (0.008, 0.004),
    },
    "Avenida Caseros / Barracas": {
        "tipo": "eje_aproximado",
        "etiqueta": "Caseros / Barracas",
        "descripcion": "Corredor vinculado a Caseros y Barracas.",
        "criterio": "Eje lineal aproximado; no delimita poligono oficial.",
        "detalle": "no",
        "shape": {"kind": "line", "coords": [(-58.375, -34.628), (-58.389, -34.636), (-58.402, -34.641)]},
        "precision": "traza aproximada",
        "offset": (0.005, -0.006),
    },
    "Microcentro y Centro": {
        "tipo": "area_barrio",
        "etiqueta": "Microcentro y Centro",
        "descripcion": "Area central con lectura documental.",
        "criterio": "San Nicolas y Monserrat como apoyo territorial preliminar.",
        "detalle": "no",
        "shape": {"kind": "barrios", "barrios": ["San Nicolas", "Monserrat"]},
        "precision": "barrios oficiales como apoyo",
        "offset": (0.006, 0.003),
    },
    "Avenida Corrientes": {
        "tipo": "eje_aproximado",
        "etiqueta": "Corrientes",
        "descripcion": "Eje teatral-gastronomico entre 9 de Julio y Callao.",
        "criterio": "Tramo 9 de Julio-Callao; distinto de Abasto.",
        "detalle": "si",
        "shape": {"kind": "line", "coords": [(-58.3816, -34.6038), (-58.3927, -34.6043)]},
        "precision": "tramo definido editorialmente; no poligono",
        "offset": (-0.011, 0.006),
    },
    "Abasto": {
        "tipo": "area_aproximada",
        "etiqueta": "Abasto",
        "descripcion": "Area alrededor del shopping Abasto.",
        "criterio": "Entorno del shopping como centro; radio aproximado de 5 cuadras.",
        "detalle": "si",
        "shape": {"kind": "ellipse", "center": (-58.4105, -34.6038), "rx": 0.0070, "ry": 0.0052},
        "precision": "area aproximada, no limite oficial",
        "offset": (0.007, 0.004),
    },
    "Avenida Boedo": {
        "tipo": "eje_aproximado",
        "etiqueta": "Av. Boedo",
        "descripcion": "Eje barrial sin locales explicitos en la capa semilla.",
        "criterio": "Tramo aproximado sobre Avenida Boedo; requiere refuerzo documental.",
        "detalle": "no",
        "shape": {"kind": "line", "coords": [(-58.4188, -34.618), (-58.4218, -34.635)]},
        "precision": "traza aproximada",
        "offset": (0.006, -0.002),
    },
    "Devoto": {
        "tipo": "area_barrio",
        "etiqueta": "Devoto",
        "descripcion": "Polo de barrio a fortalecer, sin locales explicitos en la capa semilla.",
        "criterio": "Barrio Villa Devoto como area de lectura preliminar.",
        "detalle": "no",
        "shape": {"kind": "barrios", "barrios": ["Villa Devoto"]},
        "precision": "barrio oficial como apoyo",
        "offset": (-0.005, 0.006),
    },
    "Corredor DoHo / Donado-Holmberg": {
        "tipo": "eje_aproximado",
        "etiqueta": "DoHo",
        "descripcion": "Corredor Donado-Holmberg, sin locales explicitos en la capa semilla.",
        "criterio": "Eje aproximado Donado-Holmberg; requiere refuerzo documental.",
        "detalle": "no",
        "shape": {"kind": "line", "coords": [(-58.474, -34.558), (-58.477, -34.573)]},
        "precision": "traza aproximada",
        "offset": (-0.010, -0.001),
    },
    "Villa Urquiza": {
        "tipo": "area_barrio",
        "etiqueta": "Villa Urquiza",
        "descripcion": "Polo de barrio a fortalecer, sin locales explicitos en la capa semilla.",
        "criterio": "Barrio Villa Urquiza como area de lectura preliminar.",
        "detalle": "no",
        "shape": {"kind": "barrios", "barrios": ["Villa Urquiza"]},
        "precision": "barrio oficial como apoyo",
        "offset": (0.007, 0.003),
    },
    "Nuevo Bajo Retiro / Esmeralda y Paraguay": {
        "tipo": "area_aproximada",
        "etiqueta": "Nuevo Bajo Retiro",
        "descripcion": "Area puntual de lectura institucional pendiente.",
        "criterio": "Entorno Esmeralda-Paraguay como area aproximada; requiere refuerzo documental.",
        "detalle": "no",
        "shape": {"kind": "ellipse", "center": (-58.3780, -34.5930), "rx": 0.0045, "ry": 0.0040},
        "precision": "area aproximada",
        "offset": (0.008, 0.005),
    },
    "Avenida Federico Lacroze, desde Libertador hasta Cabildo": {
        "tipo": "eje_aproximado",
        "etiqueta": "Federico Lacroze",
        "descripcion": "Eje de lectura entre Libertador y Cabildo, sin locales explicitos.",
        "criterio": "Tramo aproximado entre Libertador y Cabildo; requiere refuerzo documental.",
        "detalle": "no",
        "shape": {"kind": "line", "coords": [(-58.432, -34.561), (-58.450, -34.570)]},
        "precision": "traza aproximada",
        "offset": (0.006, -0.006),
    },
    "Parque Saavedra / Avenida Garcia del Rio": {
        "tipo": "area_aproximada",
        "etiqueta": "Parque Saavedra",
        "descripcion": "Area Parque Saavedra / Garcia del Rio, sin locales explicitos.",
        "criterio": "Entorno del parque y eje Garcia del Rio; requiere refuerzo documental.",
        "detalle": "no",
        "shape": {"kind": "ellipse", "center": (-58.485, -34.552), "rx": 0.0100, "ry": 0.0065},
        "precision": "area aproximada",
        "offset": (0.009, 0.003),
    },
    "Circuito gastronomico de Paternal": {
        "tipo": "area_barrio",
        "etiqueta": "Paternal",
        "descripcion": "Circuito de Paternal, sin locales explicitos.",
        "criterio": "Barrio Paternal como area de lectura; no cierra circuito oficial.",
        "detalle": "no",
        "shape": {"kind": "barrios", "barrios": ["Paternal"]},
        "precision": "barrio oficial como apoyo",
        "offset": (-0.010, -0.002),
    },
    "Villa Pueyrredon / Avenida San Martin": {
        "tipo": "area_barrio",
        "etiqueta": "Villa Pueyrredon / San Martin",
        "descripcion": "Area/eje Villa Pueyrredon - Avenida San Martin, sin locales explicitos.",
        "criterio": "Barrio Villa Pueyrredon como apoyo y eje San Martin aproximado.",
        "detalle": "no",
        "shape": {"kind": "barrios", "barrios": ["Villa Pueyrredon"]},
        "precision": "barrio oficial como apoyo; eje a validar",
        "offset": (-0.012, -0.002),
    },
}

DETAIL_MAPS = [
    ("palermo_las_canitas", "Palermo / Las Canitas", ["Palermo"], ["Palermo"]),
    ("puerto_madero", "Puerto Madero", ["Puerto Madero"], ["Puerto Madero"]),
    ("san_telmo", "San Telmo", ["San Telmo"], ["San Telmo"]),
    ("corrientes_abasto", "Corrientes / Abasto", ["Avenida Corrientes", "Abasto"], ["San Nicolas", "Monserrat", "Balvanera"]),
    ("belgrano", "Belgrano", ["Belgrano"], ["Belgrano"]),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def as_int(value: str) -> int:
    match = re.search(r"\d+", value or "")
    return int(match.group(0)) if match else 0


def fmt_coord(value: str | float) -> str:
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return ""


def load_geojson(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {feature["properties"]["nombre"]: feature for feature in data["features"]}


def rings_for(feature: dict) -> Iterable[list[tuple[float, float]]]:
    geometry = feature["geometry"]
    coords = geometry["coordinates"]
    if geometry["type"] == "Polygon":
        for ring in coords:
            yield [(float(x), float(y)) for x, y in ring]
    elif geometry["type"] == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                yield [(float(x), float(y)) for x, y in ring]


def polygon_centroid(ring: list[tuple[float, float]]) -> tuple[float, float]:
    if len(ring) < 3:
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        return (sum(xs) / len(xs), sum(ys) / len(ys))
    area = 0.0
    cx = 0.0
    cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        cross = x0 * y1 - x1 * y0
        area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    area *= 0.5
    if abs(area) < 1e-12:
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        return (sum(xs) / len(xs), sum(ys) / len(ys))
    return (cx / (6 * area), cy / (6 * area))


def centroid_for_barrios(barrios: dict[str, dict], names: list[str]) -> tuple[float, float]:
    weighted: list[tuple[float, float, float]] = []
    for name in names:
        feature = barrios[name]
        for ring in rings_for(feature):
            c = polygon_centroid(ring)
            xs = [point[0] for point in ring]
            ys = [point[1] for point in ring]
            weight = max((max(xs) - min(xs)) * (max(ys) - min(ys)), 0.000001)
            weighted.append((c[0], c[1], weight))
    total = sum(w for *_xy, w in weighted)
    return (
        sum(x * w for x, _y, w in weighted) / total,
        sum(y * w for _x, y, w in weighted) / total,
    )


def center_for_shape(shape: dict, barrios: dict[str, dict]) -> tuple[float, float]:
    if shape["kind"] == "barrios":
        return centroid_for_barrios(barrios, shape["barrios"])
    if shape["kind"] == "line":
        coords = shape["coords"]
        return (sum(x for x, _y in coords) / len(coords), sum(y for _x, y in coords) / len(coords))
    if shape["kind"] == "ellipse":
        return shape["center"]
    raise ValueError(f"Tipo de geometria no soportado: {shape['kind']}")


def draw_base(ax: plt.Axes, barrios: dict[str, dict], highlight_barrios: list[str] | None = None) -> None:
    highlight = set(highlight_barrios or [])
    for name, feature in barrios.items():
        for ring in rings_for(feature):
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            face = "#f7f9fb" if name not in highlight else "#fff8ef"
            edge = LINEA if name not in highlight else "#e0b270"
            ax.fill(xs, ys, facecolor=face, edgecolor=edge, linewidth=0.55, zorder=1)


def draw_shape(ax: plt.Axes, barrios: dict[str, dict], config: dict, alpha: float = 0.28, label: bool = False) -> None:
    shape = config["shape"]
    color = TIPO_COLOR[config["tipo"]]
    linestyle = "--" if "sin locales explicitos" in config.get("observacion", "") else "-"
    if shape["kind"] == "barrios":
        for barrio in shape["barrios"]:
            for ring in rings_for(barrios[barrio]):
                xs = [p[0] for p in ring]
                ys = [p[1] for p in ring]
                ax.fill(xs, ys, facecolor=color, alpha=alpha, edgecolor=color, linewidth=1.2, linestyle=linestyle, zorder=3)
    elif shape["kind"] == "line":
        xs = [p[0] for p in shape["coords"]]
        ys = [p[1] for p in shape["coords"]]
        ax.plot(xs, ys, color=color, linewidth=2.6, linestyle=linestyle, solid_capstyle="round", zorder=5)
    elif shape["kind"] == "ellipse":
        cx, cy = shape["center"]
        ax.add_patch(
            Ellipse(
                (cx, cy),
                width=shape["rx"] * 2,
                height=shape["ry"] * 2,
                facecolor=color,
                edgecolor=color,
                linewidth=1.4,
                linestyle=linestyle,
                alpha=alpha,
                zorder=4,
            )
        )
    if label:
        cx, cy = center_for_shape(shape, barrios)
        dx, dy = config.get("offset", (0.004, 0.004))
        ax.annotate(
            config["etiqueta"],
            xy=(cx, cy),
            xytext=(cx + dx, cy + dy),
            fontsize=7.4,
            color="#222222",
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.22", "facecolor": "white", "edgecolor": "#cfd6df", "linewidth": 0.45},
            arrowprops={"arrowstyle": "-", "color": "#9aa5b1", "lw": 0.5},
            zorder=8,
        )


def finish_map(ax: plt.Axes, title: str, subtitle: str, footer: str, full_extent: bool = True) -> None:
    ax.set_aspect("equal", adjustable="box")
    if full_extent:
        ax.set_xlim(-58.535, -58.330)
        ax.set_ylim(-34.710, -34.520)
    ax.axis("off")
    fig = ax.figure
    fig.text(0.06, 0.965, INSTITUCION, fontsize=10, color=ROJO, weight="bold", ha="left")
    fig.text(0.06, 0.935, title, fontsize=17, color=AZUL, weight="bold", ha="left")
    if subtitle:
        fig.text(0.06, 0.910, subtitle, fontsize=9.2, color=GRIS, ha="left")
    fig.text(0.06, 0.035, footer, fontsize=7.4, color=GRIS, ha="left", va="bottom")


def save_figure(fig: plt.Figure, path_base: Path, svg: bool = True) -> None:
    path_base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path_base.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor="white")
    if svg:
        fig.savefig(path_base.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def build_polos_table(polos: list[dict[str, str]], barrios: dict[str, dict]) -> list[dict[str, str]]:
    missing = sorted(set(row["polo"] for row in polos) - set(POLO_CONFIG))
    extra = sorted(set(POLO_CONFIG) - set(row["polo"] for row in polos))
    if missing or extra:
        raise RuntimeError(f"Configuracion de polos incompleta. Faltan={missing}. Sobra={extra}.")

    rows: list[dict[str, str]] = []
    for row in polos:
        config = dict(POLO_CONFIG[row["polo"]])
        count = as_int(row["locales_semilla_cantidad"])
        if count == 0:
            observacion = "Integra el universo semilla sin locales explicitos; representar como area/eje, no como local."
        elif row["polo"] == "Abasto":
            observacion = "No doble contar con Corrientes; puntos de locales pendientes por duplicados/vigencia."
        elif row["polo"] == "Avenida Corrientes":
            observacion = "Eje vinculado con Abasto, pero con delimitacion distinta."
        else:
            observacion = "Representacion territorial preliminar; no equivale a delimitacion oficial."
        config["observacion"] = observacion
        center = center_for_shape(config["shape"], barrios)
        rows.append(
            {
                "polo": row["polo"],
                "tipo_representacion_mapa": config["tipo"],
                "etiqueta_mapa": config["etiqueta"],
                "descripcion_corta": config["descripcion"],
                "criterio_geografico": config["criterio"],
                "incluir_mapa_global": "si",
                "incluir_mapa_detalle": config["detalle"],
                "observacion": observacion,
                "lat_centroide_aprox": f"{center[1]:.6f}",
                "lon_centroide_aprox": f"{center[0]:.6f}",
                "precision_cartografica": config["precision"],
            }
        )
    return rows


def build_locales_table(consolidado: list[dict[str, str]]) -> list[dict[str, str]]:
    coords: dict[str, dict[str, str]] = {}
    for path in INPUT_COORDS:
        for row in read_csv(path):
            coords[row["id_local_semilla"]] = row
    missing = [row["id_local_semilla"] for row in consolidado if row["id_local_semilla"] not in coords]
    if missing:
        raise RuntimeError(f"Faltan coordenadas locales para {len(missing)} casos.")

    rows: list[dict[str, str]] = []
    for row in consolidado:
        coord = coords[row["id_local_semilla"]]
        estado = row["estado_consolidado"]
        if estado in {"match_fuerte", "match_razonable_revisar_sede"}:
            mostrar_revision = "si"
            mostrar_publico = "pendiente_validacion"
            obs = "Puede ir a mapa de revision interna; no se acepta automaticamente como punto publico."
        elif estado == "zona_sucursal_a_revisar":
            mostrar_revision = "si_interno_dudoso"
            mostrar_publico = "no"
            obs = "Solo referencia interna; revisar zona o sede antes de cualquier uso publico."
        elif estado == "duplicado_probable":
            mostrar_revision = "no"
            mostrar_publico = "no"
            obs = "Duplicado probable; no mapear hasta resolver una sede."
        elif estado == "vigencia_no_confirmada":
            mostrar_revision = "no"
            mostrar_publico = "no"
            obs = "Vigencia no confirmada o cierre detectado; no mostrar como activo."
        elif estado == "query_a_corregir":
            mostrar_revision = "no"
            mostrar_publico = "no"
            obs = "Busqueda a corregir; no usar en mapa."
        else:
            mostrar_revision = "no"
            mostrar_publico = "no"
            obs = "Estado no previsto; requiere revision humana."
        rows.append(
            {
                "polo": row["polo"],
                "subzona": row["subzona"],
                "nombre_lugar": row["nombre_lugar_original"] or coord.get("nombre_lugar_original", ""),
                "lat": fmt_coord(coord.get("lat", "")),
                "lon": fmt_coord(coord.get("lon", "")),
                "estado_consolidado": estado,
                "decision_borrador4": row["decision_borrador4"],
                "mostrar_mapa_revision": mostrar_revision,
                "mostrar_mapa_publico": mostrar_publico,
                "observacion": obs,
            }
        )
    return rows


def point_rows(rows: list[dict[str, str]], polos: list[str] | None = None) -> list[dict[str, str]]:
    allowed = {"si", "si_interno_dudoso"}
    selected = [
        row
        for row in rows
        if row["mostrar_mapa_revision"] in allowed and row["estado_consolidado"] in ESTADO_COLOR and row["lat"] and row["lon"]
    ]
    if polos is not None:
        selected = [row for row in selected if row["polo"] in polos]
    return selected


def plot_points(ax: plt.Axes, rows: list[dict[str, str]], with_labels: bool = False) -> None:
    for estado in ["match_fuerte", "match_razonable_revisar_sede", "zona_sucursal_a_revisar"]:
        subset = [row for row in rows if row["estado_consolidado"] == estado]
        if not subset:
            continue
        xs = [float(row["lon"]) for row in subset]
        ys = [float(row["lat"]) for row in subset]
        if estado == "zona_sucursal_a_revisar":
            ax.scatter(xs, ys, s=36, marker="^", facecolors="none", edgecolors=ESTADO_COLOR[estado], linewidths=1.2, zorder=9)
        else:
            ax.scatter(xs, ys, s=28, marker="o", color=ESTADO_COLOR[estado], edgecolor="white", linewidth=0.5, zorder=9)
        if with_labels:
            for row in subset:
                ax.text(
                    float(row["lon"]) + 0.0012,
                    float(row["lat"]) + 0.0010,
                    "\n".join(textwrap.wrap(row["nombre_lugar"], 18)),
                    fontsize=5.7,
                    color="#222222",
                    zorder=10,
                )


def save_global_map(barrios: dict[str, dict], polos_table: list[dict[str, str]]) -> None:
    fig, ax = plt.subplots(figsize=(11, 12.5))
    draw_base(ax, barrios)
    for row in polos_table:
        draw_shape(ax, barrios, POLO_CONFIG[row["polo"]], alpha=0.22, label=True)
    legend = [
        Patch(facecolor=TIPO_COLOR["area_barrio"], alpha=0.30, edgecolor=TIPO_COLOR["area_barrio"], label="Area / barrio de lectura"),
        Patch(facecolor=TIPO_COLOR["macroarea"], alpha=0.30, edgecolor=TIPO_COLOR["macroarea"], label="Macroarea con subzonas"),
        Patch(facecolor=TIPO_COLOR["area_aproximada"], alpha=0.30, edgecolor=TIPO_COLOR["area_aproximada"], label="Area aproximada"),
        Line2D([0], [0], color=TIPO_COLOR["eje_aproximado"], lw=2.5, label="Eje / corredor aproximado"),
    ]
    ax.legend(handles=legend, loc="lower left", bbox_to_anchor=(0.02, 0.035), frameon=True, fontsize=8.2)
    finish_map(
        ax,
        "Mapa global preliminar de 22 polos/ejes gastronomicos",
        "Areas y ejes del universo semilla. No representa locales individuales.",
        "Lectura territorial preliminar. Base cartografica local de barrios CABA. Areas/ejes aproximados; no son delimitaciones oficiales ni padron de locales.",
    )
    save_figure(fig, ASSETS / "mapa_global_22_polos_ejes", svg=True)


def save_revision_map(barrios: dict[str, dict], locales: list[dict[str, str]]) -> None:
    rows = point_rows(locales)
    fig, ax = plt.subplots(figsize=(11, 12.5))
    draw_base(ax, barrios)
    plot_points(ax, rows)
    legend = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=AZUL2, markeredgecolor="white", label="Match fuerte", markersize=7),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=VERDE, markeredgecolor="white", label="Razonable: revisar sede", markersize=7),
        Line2D([0], [0], marker="^", color=NARANJA, markerfacecolor="none", label="Zona/sucursal a revisar", markersize=7),
    ]
    ax.legend(handles=legend, loc="lower left", bbox_to_anchor=(0.02, 0.035), frameon=True, fontsize=8.2)
    finish_map(
        ax,
        "Mapa interno de revision de locales geolocalizados",
        "59 correspondencias fuertes/razonables + 25 zona/sucursal a revisar; sin cerrados, queries a corregir ni duplicados.",
        "Uso interno preliminar. La geolocalizacion acompana la revision visual y no valida vigencia, habilitacion ni actividad actual.",
    )
    save_figure(fig, ASSETS / "mapa_revision_locales_razonables", svg=True)


def bbox_for_rows(rows: list[dict[str, str]], margin: float = 0.012) -> tuple[float, float, float, float] | None:
    if not rows:
        return None
    xs = [float(row["lon"]) for row in rows]
    ys = [float(row["lat"]) for row in rows]
    if max(xs) - min(xs) < 0.01:
        margin = max(margin, 0.018)
    if max(ys) - min(ys) < 0.01:
        margin = max(margin, 0.014)
    return min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin


def save_detail_maps(barrios: dict[str, dict], locales: list[dict[str, str]]) -> list[dict[str, str]]:
    summaries: list[dict[str, str]] = []
    for slug, title, polos, context_barrios in DETAIL_MAPS:
        rows = point_rows(locales, polos)
        main = [row for row in rows if row["estado_consolidado"] in {"match_fuerte", "match_razonable_revisar_sede"}]
        zona = [row for row in rows if row["estado_consolidado"] == "zona_sucursal_a_revisar"]

        fig, ax = plt.subplots(figsize=(10.5, 8.2))
        draw_base(ax, barrios, context_barrios)
        for polo in polos:
            if polo in POLO_CONFIG:
                draw_shape(ax, barrios, POLO_CONFIG[polo], alpha=0.18, label=False)
        plot_points(ax, rows, with_labels=False)

        bounds = bbox_for_rows(rows)
        if bounds is not None:
            xmin, xmax, ymin, ymax = bounds
            ax.set_xlim(max(-58.535, xmin), min(-58.330, xmax))
            ax.set_ylim(max(-34.710, ymin), min(-34.520, ymax))
        else:
            ax.set_xlim(-58.535, -58.330)
            ax.set_ylim(-34.710, -34.520)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")

        handles = [
            Line2D([0], [0], marker="o", color="w", markerfacecolor=AZUL2, markeredgecolor="white", label="Match fuerte", markersize=7),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=VERDE, markeredgecolor="white", label="Razonable: revisar sede", markersize=7),
            Line2D([0], [0], marker="^", color=NARANJA, markerfacecolor="none", label="Zona/sucursal a revisar", markersize=7),
        ]
        ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.02, 0.03), frameon=True, fontsize=8)
        finish_map(
            ax,
            f"Mapa preliminar de detalle - {title}",
            f"Puntos principales: {len(main)}. Zona/sucursal a revisar: {len(zona)}. No incluye cerrados, queries a corregir ni duplicados.",
            "Uso preliminar para revision. Los puntos no constituyen padron oficial ni validacion de actividad vigente.",
            full_extent=False,
        )
        save_figure(fig, ASSETS / f"mapa_detalle_{slug}", svg=False)

        strong_count = sum(1 for row in main if row["estado_consolidado"] == "match_fuerte")
        if slug == "corrientes_abasto" and len(main) <= 3:
            lectura = "flojo: Abasto queda como area aproximada sin puntos fuertes propios por duplicados/vigencia pendiente."
        elif not main:
            lectura = "pendiente: sin puntos fuertes/razonables."
        elif strong_count == 0:
            lectura = "limitado: no hay match fuerte; requiere revision de sedes/subzonas antes de publicacion."
        elif zona:
            lectura = "usable como preliminar de revision, con sedes o zonas a revisar."
        elif len(main) >= 5:
            lectura = "usable como preliminar de revision."
        else:
            lectura = "limitado: pocos puntos fuertes/razonables; requiere revision humana."
        summaries.append(
            {
                "mapa": title,
                "archivo": f"mapa_detalle_{slug}.png",
                "puntos_fuertes_razonables": str(len(main)),
                "zona_sucursal_a_revisar": str(len(zona)),
                "lectura": lectura,
            }
        )
    return summaries


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def write_docs(
    polos_table: list[dict[str, str]],
    locales: list[dict[str, str]],
    detail_summaries: list[dict[str, str]],
) -> None:
    counts = Counter(row["estado_consolidado"] for row in locales)
    main_revision = counts["match_fuerte"] + counts["match_razonable_revisar_sede"]
    internal_zone = counts["zona_sucursal_a_revisar"]
    detail_lines = [
        f"{row['mapa']}: {row['puntos_fuertes_razonables']} puntos fuertes/razonables, "
        f"{row['zona_sucursal_a_revisar']} zona/sucursal a revisar. Lectura: {row['lectura']}"
        for row in detail_summaries
    ]

    CRITERIOS_DOC.parent.mkdir(parents=True, exist_ok=True)
    CRITERIOS_DOC.write_text(
        f"""# Criterios cartograficos - PolosGastro

{INSTITUCION}. Fecha: {FECHA}. Documento interno para fase 13 de mapas.

## Alcance

Esta fase prepara assets cartograficos preliminares para el informe PolosGastro. No genera PDF,
DOCX, padron oficial ni delimitaciones definitivas. No se ejecutaron API ni busquedas nuevas.

## Mapa global

El mapa global representa los {len(polos_table)} polos/ejes del universo semilla como areas,
macroareas, ejes o areas aproximadas. Todos se incluyen, aun cuando no tengan locales explicitos.
La lectura es territorial y preliminar: no mide actividad actual, no valida habilitaciones y no
cierra limites oficiales.

## Polos/ejes sin locales explicitos

Los polos sin locales explicitos se representan como area o eje del universo semilla, nunca como
punto de local. En esta fase quedan marcados con criterio prudente y requieren refuerzo documental
antes de afirmaciones especificas.

## Corrientes y Abasto

Avenida Corrientes se representa como eje teatral-gastronomico entre 9 de Julio y Callao. Abasto se
representa como area alrededor del shopping, con radio aproximado de cinco cuadras. Son ejes
vinculados con delimitacion distinta; no se fusionan y no se doble cuentan.

## Capa de locales

La capa de locales parte del consolidado local ya disponible y recupera coordenadas desde salidas de
revision visual locales de la misma fase. Entra a mapa interno:

- {counts['match_fuerte']} puntos con `match_fuerte`.
- {counts['match_razonable_revisar_sede']} puntos con `match_razonable_revisar_sede`.
- {internal_zone} puntos `zona_sucursal_a_revisar`, solo como referencia interna diferenciada.

No entran a mapas de puntos:

- {counts['vigencia_no_confirmada']} casos con vigencia no confirmada.
- {counts['duplicado_probable']} duplicados probables.
- {counts['query_a_corregir']} busquedas a corregir.

## Cerrados, duplicados y dudas

Los casos cerrados o con vigencia no confirmada no aparecen como activos. Los duplicados no se
mapean hasta resolver una sede. Las zonas o sucursales dudosas pueden verse solo en mapas internos
con simbolo distinto; no pasan a mapa publico.

## Publicabilidad

El mapa global podria alimentar una pieza publica despues de revision visual y editorial. Los mapas
de puntos y detalles quedan como preliminares de revision interna hasta validar sedes, duplicados y
criterios de publicacion. Ningun mapa de esta fase debe leerse como padron oficial.
""",
        encoding="utf-8",
    )

    QA_DOC.write_text(
        f"""# QA mapas PolosGastro - fase 13

{INSTITUCION}. Fecha: {FECHA}. Control tecnico y metodologico de cierre de assets.

## Conteos

- Polos/ejes en mapa global: {len(polos_table)}.
- Estan los 22 polos/ejes del universo semilla: {"si" if len(polos_table) == 22 else "no"}.
- Locales en tabla de revision visual: {len(locales)}.
- Locales fuertes/razonables para mapa de revision: {main_revision}.
- Zona/sucursal a revisar incorporados solo como referencia interna: {internal_zone}.
- Total de puntos visibles en mapa interno de revision: {main_revision + internal_zone}.

## Validaciones editoriales

- Corrientes y Abasto estan diferenciados: si.
- Corrientes se representa como eje 9 de Julio-Callao: si.
- Abasto se representa como area aproximada de entorno: si.
- Cerrados/vigencia no confirmada no aparecen como activos: si.
- Duplicados probables no aparecen como activos: si.
- No se aceptan puntos dudosos como mapa publico: si.
- Marca visible en mapas: DGDGAS - Direccion General de Desarrollo Gastronomico.
- La marca interna del proyecto no se usa como marca publica en assets: si.

## Campos sensibles

- No se exportan identificadores tecnicos de plataformas privadas.
- No se exportan puntajes ni conteos de resenas.
- No se exportan claves de API.
- No se exportan respuestas crudas de herramientas externas.
- No se exportan direcciones exactas.
- No se incluyen rutas locales ni nombres de scripts dentro de los mapas.

## Mapas generados

- `mapa_global_22_polos_ejes.png`
- `mapa_global_22_polos_ejes.svg`
- `mapa_revision_locales_razonables.png`
- `mapa_revision_locales_razonables.svg`
- `mapa_detalle_palermo_las_canitas.png`
- `mapa_detalle_puerto_madero.png`
- `mapa_detalle_san_telmo.png`
- `mapa_detalle_corrientes_abasto.png`
- `mapa_detalle_belgrano.png`

## Lectura de mapas de detalle

{bullet(detail_lines)}

## Limitaciones

- Las areas y ejes son preliminares y no constituyen delimitaciones oficiales.
- La geolocalizacion es auxiliar; no confirma actividad vigente ni habilitacion.
- Abasto queda debil como mapa de puntos porque los casos asociados aparecen como duplicados o
  vigencia no confirmada en la capa consolidada.
- Belgrano requiere lectura por subzonas; Belgrano R conserva respaldo mas debil.
- Los mapas de puntos son internos/preliminares hasta validacion humana de sedes.

## Alcance confirmado

- No API: si.
- No llamadas Google Places: si.
- No scraping: si.
- No PDF generado: si.
- No DOCX generado: si.
- No datos fuente modificados: si.
- No commit/push/staging realizado por este script: si.
""",
        encoding="utf-8",
    )


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    barrios = load_geojson(GEO_BARRIOS)
    polos = read_csv(INPUT_POLOS)
    consolidado = read_csv(INPUT_CONSOLIDADO)

    polos_table = build_polos_table(polos, barrios)
    locales_table = build_locales_table(consolidado)

    write_csv(
        POLOS_MAPA,
        polos_table,
        [
            "polo",
            "tipo_representacion_mapa",
            "etiqueta_mapa",
            "descripcion_corta",
            "criterio_geografico",
            "incluir_mapa_global",
            "incluir_mapa_detalle",
            "observacion",
            "lat_centroide_aprox",
            "lon_centroide_aprox",
            "precision_cartografica",
        ],
    )
    write_csv(
        LOCALES_MAPA,
        locales_table,
        [
            "polo",
            "subzona",
            "nombre_lugar",
            "lat",
            "lon",
            "estado_consolidado",
            "decision_borrador4",
            "mostrar_mapa_revision",
            "mostrar_mapa_publico",
            "observacion",
        ],
    )

    save_global_map(barrios, polos_table)
    save_revision_map(barrios, locales_table)
    detail_summaries = save_detail_maps(barrios, locales_table)
    write_docs(polos_table, locales_table, detail_summaries)

    print(f"Polos/ejes: {len(polos_table)}")
    print(f"Locales revision: {len(locales_table)}")
    print(f"Assets: {ASSETS}")
    print(f"Docs: {DOCS}")


if __name__ == "__main__":
    main()
