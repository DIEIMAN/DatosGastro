"""Visuales V5 para el informe final de mercados gastronomicos de CABA.

No recalcula el universo: lee los CSV V4 sanitizados y genera una nueva
iteracion visual. No hace requests ni usa APIs.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, OrderedDict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from shapely.geometry import Point, shape  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SAN = ROOT / "outputs" / "mercados_caba" / "sanitized"
GEO = ROOT / "data" / "raw"

INK = "#1f3b57"
BLUE = "#2c7fb8"
ORANGE = "#c0762b"
RED = "#c0392b"
GREEN = "#1a9850"
VIOLET = "#7b5ea7"
GREY = "#626a73"
LIGHT = "#eef2f6"
LINE = "#cfd8e3"

TYPE_LABEL = {
    "mercado_historico": "Mercado historico",
    "mercado_barrial_alimentario": "Barrial alimentario",
    "food_hall": "Food hall",
    "patio_gastronomico": "Patio gastronomico",
    "mercado_de_productores": "Mercado de productores",
    "feria_gastronomica": "Feria gastronomica",
}
TYPE_COLOR = {
    "mercado_historico": INK,
    "mercado_barrial_alimentario": VIOLET,
    "food_hall": ORANGE,
    "patio_gastronomico": BLUE,
    "mercado_de_productores": GREEN,
    "feria_gastronomica": RED,
}

# Coordenadas aproximadas de ubicacion territorial de las sedes fijas. Se usan
# para lectura ejecutiva, no como geocodificacion exacta ni validacion territorial.
FIXED_COORDS = {
    "MG-0001": (-34.6190, -58.3733),  # San Telmo
    "MG-0002": (-34.5627, -58.4560),  # Belgrano
    "MG-0013": (-34.6030, -58.3868),  # San Nicolas
    "MG-0003": (-34.6186, -58.4411),  # Caballito
    "MG-0004": (-34.5968, -58.4381),  # Villa Crespo
    "MG-0017": (-34.5889, -58.3838),  # Retiro / Patio Bullrich
    "MG-0006": (-34.6144, -58.4480),  # Caballito
    "MG-0010": (-34.6358, -58.4005),  # Parque Patricios
    "MG-0011": (-34.5548, -58.4235),  # Costanera Norte, aproximado en borde CABA
    "MG-0012": (-34.6177, -58.3585),  # Rodrigo Bueno / Puerto Madero
    "MG-0008": (-34.5882, -58.4360),  # Palermo
}

LABELS = {
    "MG-0001": "San Telmo",
    "MG-0002": "Belgrano",
    "MG-0013": "San Nicolas",
    "MG-0003": "Progreso",
    "MG-0004": "Mercat V. Crespo",
    "MG-0017": "Gourmand",
    "MG-0006": "Lecheros",
    "MG-0010": "Smart Plaza",
    "MG-0011": "Costanera Norte",
    "MG-0012": "Rodrigo Bueno",
    "MG-0008": "Bonpland",
}

LABEL_OFFSETS = {
    "MG-0001": (10, -4),
    "MG-0002": (10, 4),
    "MG-0013": (10, 8),
    "MG-0003": (10, -10),
    "MG-0004": (10, 2),
    "MG-0017": (10, 6),
    "MG-0006": (10, 12),
    "MG-0010": (10, -4),
    "MG-0011": (10, 4),
    "MG-0012": (-78, 4),
    "MG-0008": (10, 8),
}


def read_csv(name: str) -> list[dict[str, str]]:
    with (SAN / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def load_geo(name: str) -> list[dict]:
    return json.loads((GEO / name).read_text(encoding="utf-8"))["features"]


def rings(geom: dict) -> list[list[list[float]]]:
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [poly[0] for poly in geom["coordinates"]]
    return []


def draw_geo_base(ax, barrios: list[dict], comunas: list[dict]) -> None:
    for f in barrios:
        for ring in rings(f["geometry"]):
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            ax.fill(xs, ys, facecolor="#f7f9fb", edgecolor="#dde5ee", lw=0.45, zorder=1)
    for f in comunas:
        for ring in rings(f["geometry"]):
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            ax.plot(xs, ys, color="#aab7c4", lw=0.9, zorder=2)


def validate_and_export_points(rows: list[dict[str, str]], comunas: list[dict]) -> list[dict[str, object]]:
    city = unary_union([shape(f["geometry"]) for f in comunas])
    out = []
    for r in rows:
        if r["es_itinerante"] == "si":
            continue
        lat, lon = FIXED_COORDS[r["id"]]
        inside = city.contains(Point(lon, lat)) or city.touches(Point(lon, lat))
        if not inside:
            raise ValueError(f"Punto fuera de CABA: {r['id']} {r['nombre']} ({lat}, {lon})")
        out.append({
            "id": r["id"],
            "nombre": r["nombre"],
            "tipo_primario": r["tipo_primario"],
            "gestion": r["gestion"],
            "barrio": r["barrio"],
            "comuna": r["comuna"],
            "lat_aprox": f"{lat:.5f}",
            "lon_aprox": f"{lon:.5f}",
            "nota_ubicacion": "aproximada_para_lectura_territorial_no_geocodificacion_exacta",
        })
    write_csv(
        SAN / "mercados_sedes_fijas_v5.csv",
        out,
        ["id", "nombre", "tipo_primario", "gestion", "barrio", "comuna", "lat_aprox", "lon_aprox", "nota_ubicacion"],
    )
    return out


def save(fig, name: str) -> None:
    fig.savefig(SAN / name, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"ok: {name}")


def hbar(labels: list[str], values: list[int], title: str, name: str, accent: int = 0) -> None:
    order = sorted(range(len(values)), key=lambda i: values[i])
    labels = [labels[i] for i in order]
    values = [values[i] for i in order]
    colors = [BLUE] * len(values)
    if colors:
        colors[-1 if accent == 0 else accent] = ORANGE
    fig, ax = plt.subplots(figsize=(7.6, max(2.5, 0.48 * len(values) + 1.15)))
    ax.barh(labels, values, color=colors, height=0.62)
    ax.set_title(title, color=INK, fontsize=12.5, fontweight="bold", loc="left", pad=8)
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.spines["left"].set_color("#aab7c4")
    ax.tick_params(axis="x", length=0, labelbottom=False)
    ax.tick_params(axis="y", labelsize=9.2)
    mx = max(values) if values else 1
    for i, v in enumerate(values):
        ax.text(v + mx * 0.02, i, str(v), va="center", color=INK, fontsize=9.2, fontweight="bold")
    ax.set_xlim(0, mx * 1.18)
    save(fig, name)


def kpi_cards() -> None:
    cards = [
        ("13", "activos\nidentificados"),
        ("11", "sedes fijas"),
        ("2", "itinerantes"),
        ("6", "comunas"),
        ("3/5/5", "publica / privada /\nmixta"),
        ("3", "relevantes no\ncontabilizados"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(9.2, 3.6))
    for ax, (num, lab) in zip(axes.ravel(), cards):
        ax.axis("off")
        ax.add_patch(Rectangle((0.04, 0.12), 0.92, 0.76, transform=ax.transAxes,
                               facecolor=INK, edgecolor=INK))
        ax.text(0.5, 0.59, num, ha="center", va="center", fontsize=24, color=ORANGE, fontweight="bold")
        ax.text(0.5, 0.27, lab, ha="center", va="center", fontsize=9.4, color="white")
    fig.suptitle("Mercados gastronomicos de CABA - indicadores V5", x=0.06, ha="left",
                 color=INK, fontsize=13.5, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    save(fig, "grafico_kpi_cards_v5.png")


def map_sedes() -> None:
    active = read_csv("mercados_gastronomicos_activos_v4.csv")
    barrios = load_geo("geo_barrios.geojson")
    comunas = load_geo("geo_comunas.geojson")
    points = validate_and_export_points(active, comunas)

    fig, ax = plt.subplots(figsize=(8.1, 8.5))
    fig.patch.set_facecolor("white")
    draw_geo_base(ax, barrios, comunas)
    for p in points:
        lon = float(p["lon_aprox"])
        lat = float(p["lat_aprox"])
        color = TYPE_COLOR[p["tipo_primario"]]
        ax.scatter(lon, lat, s=115, color=color, edgecolor="white", lw=1.4, zorder=5)
        dx, dy = LABEL_OFFSETS[p["id"]]
        ax.annotate(
            LABELS[p["id"]],
            (lon, lat),
            xytext=(dx, dy),
            textcoords="offset points",
            ha="left" if dx >= 0 else "right",
            va="center",
            fontsize=8.2,
            color=INK,
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#d8dee6", alpha=0.94),
            path_effects=[pe.withStroke(linewidth=1.8, foreground="white")],
            zorder=6,
        )
    legend_items = [
        Line2D([0], [0], marker="o", color="w", label=TYPE_LABEL[t],
               markerfacecolor=c, markeredgecolor="white", markersize=8)
        for t, c in TYPE_COLOR.items() if t != "feria_gastronomica"
    ]
    ax.legend(handles=legend_items, title="Tipo primario", loc="lower left",
              frameon=True, framealpha=0.94, fontsize=8, title_fontsize=9)
    ax.set_title("Mapa principal de sedes fijas", color=INK, fontsize=14,
                 fontweight="bold", loc="left", pad=14)
    ax.text(
        0.0,
        1.012,
        "Mercados gastronomicos con sede fija. Itinerantes excluidos del punto fijo por operar con sedes variables.",
        transform=ax.transAxes,
        color=GREY,
        fontsize=8.7,
    )
    ax.set_aspect(1.28)
    ax.axis("off")
    ax.set_xlim(-58.535, -58.335)
    ax.set_ylim(-34.675, -34.535)
    save(fig, "mapa_sedes_fijas_mercados_gastronomicos_v5.png")


# --------------------------------------------------------------------------- #
# Mapa V2: nombres completos, callouts con linea guia, fuente mayor.
# --------------------------------------------------------------------------- #
# Nombres completos oficiales (sin abreviar) para el mapa institucional.
LABELS_FULL = {
    "MG-0001": "Mercado de San Telmo",
    "MG-0002": "Mercado de Belgrano",
    "MG-0013": "Mercado San Nicolás",
    "MG-0003": "Mercado del Progreso",
    "MG-0004": "Mercat Villa Crespo",
    "MG-0017": "Gourmand Food Hall",
    "MG-0006": "Patio de los Lecheros",
    "MG-0010": "Smart Plaza Parque Patricios",
    "MG-0011": "Patio Costanera Norte",
    "MG-0012": "Patio Gastronómico Rodrigo Bueno",
    "MG-0008": "Mercado Bonpland",
}

# Anclaje de cada etiqueta en coordenadas del eje (0..1). Posiciones elegidas
# a mano para que ninguna etiqueta se pise ni se salga del recuadro, con linea
# guia desde el punto hasta la caja de texto.
LABEL_ANCHORS = {
    "MG-0011": (0.62, 0.95, "left"),    # Costanera Norte (arriba)
    "MG-0002": (0.02, 0.90, "left"),    # Belgrano (arriba izq)
    "MG-0008": (0.02, 0.70, "left"),    # Bonpland
    "MG-0004": (0.02, 0.57, "left"),    # Villa Crespo
    "MG-0017": (0.80, 0.74, "left"),    # Gourmand (der)
    "MG-0013": (0.80, 0.60, "left"),    # San Nicolas (der)
    "MG-0006": (0.02, 0.42, "left"),    # Lecheros (izq)
    "MG-0003": (0.02, 0.30, "left"),    # Progreso (izq)
    "MG-0010": (0.02, 0.16, "left"),    # Smart Plaza (abajo izq)
    "MG-0012": (0.80, 0.30, "left"),    # Rodrigo Bueno (der)
    "MG-0001": (0.80, 0.16, "left"),    # San Telmo (abajo der)
}


def map_sedes_v2() -> None:
    """Mapa institucional con nombres completos y callouts (V2 visual).

    Mismos datos y coordenadas aproximadas que la V5; solo cambia el diseño:
    nombres oficiales completos, fuente mayor, lineas guia, leyenda reubicada y
    mas area de mapa. No recalcula el universo ni mueve puntos.
    """
    active = read_csv("mercados_gastronomicos_activos_v4.csv")
    barrios = load_geo("geo_barrios.geojson")
    comunas = load_geo("geo_comunas.geojson")
    points = validate_and_export_points(active, comunas)

    fig, ax = plt.subplots(figsize=(9.6, 8.2))
    fig.patch.set_facecolor("white")
    draw_geo_base(ax, barrios, comunas)

    ax.set_aspect(1.28)
    ax.axis("off")
    ax.set_xlim(-58.545, -58.330)
    ax.set_ylim(-34.680, -34.530)

    by_id = {p["id"]: p for p in points}
    for mid, (ax_x, ax_y, ha) in LABEL_ANCHORS.items():
        p = by_id[mid]
        lon = float(p["lon_aprox"])
        lat = float(p["lat_aprox"])
        color = TYPE_COLOR[p["tipo_primario"]]
        ax.scatter(lon, lat, s=150, color=color, edgecolor="white", lw=1.6, zorder=6)
        ax.annotate(
            LABELS_FULL[mid],
            xy=(lon, lat),
            xycoords="data",
            xytext=(ax_x, ax_y),
            textcoords="axes fraction",
            ha=ha,
            va="center",
            fontsize=10.0,
            color=INK,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.30", fc="white", ec=color, lw=1.1, alpha=0.97),
            arrowprops=dict(arrowstyle="-", color="#9aa6b2", lw=0.9,
                            shrinkA=2, shrinkB=4, connectionstyle="arc3,rad=0.0"),
            zorder=7,
        )

    legend_items = [
        Line2D([0], [0], marker="o", color="w", label=TYPE_LABEL[t],
               markerfacecolor=c, markeredgecolor="white", markersize=9)
        for t, c in TYPE_COLOR.items() if t != "feria_gastronomica"
    ]
    leg = ax.legend(handles=legend_items, title="Tipo primario", loc="lower center",
                    bbox_to_anchor=(0.5, -0.02), ncol=3, frameon=True, framealpha=0.96,
                    fontsize=8.6, title_fontsize=9.4, borderpad=0.7, columnspacing=1.6)
    leg.get_frame().set_edgecolor("#cfd8e3")
    save(fig, "mapa_sedes_fijas_mercados_gastronomicos_v5_2.png")


def itinerantes_visual() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 1.7))
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor=LIGHT, edgecolor="#d8dee6", lw=1.2))
    ax.text(0.035, 0.72, "Itinerantes: no se mapean como punto fijo", color=INK,
            fontsize=13, fontweight="bold", transform=ax.transAxes)
    ax.text(
        0.035,
        0.40,
        "Buenos Aires Market y Sabe la Tierra integran el conteo activo identificado, "
        "pero operan con sedes variables. Sin evidencia suficiente para fijar una coordenada unica.",
        color="#222222",
        fontsize=9.2,
        transform=ax.transAxes,
        wrap=True,
    )
    ax.text(0.035, 0.16, "Tratamiento V5: atributo de itinerancia, no tipologia adicional.",
            color=ORANGE, fontsize=9.4, fontweight="bold", transform=ax.transAxes)
    save(fig, "visual_itinerantes_mercados_gastronomicos_v5.png")


def charts() -> None:
    active = read_csv("mercados_gastronomicos_activos_v4.csv")
    tip = [r for r in read_csv("tipologias_mercados_v4.csv") if r["tipo_primario"].upper() != "TOTAL"]
    respaldo = read_csv("respaldo_fuentes_mercados_v4.csv")

    kpi_cards()
    hbar(
        [TYPE_LABEL[r["tipo_primario"]] for r in tip],
        [int(r["cantidad"]) for r in tip],
        "Tipologia primaria: suma 13 sin doble conteo",
        "grafico_tipo_primario_v5.png",
    )
    hbar(
        [k.capitalize() for k in Counter(r["gestion"] for r in active).keys()],
        list(Counter(r["gestion"] for r in active).values()),
        "Gestion de los mercados activos identificados",
        "grafico_gestion_v5.png",
    )
    freq = Counter(frequency_bucket(r["dias_apertura"]) for r in active)
    hbar(list(freq.keys()), list(freq.values()), "Frecuencia de apertura documentada", "grafico_horarios_v5.png")
    pub = Counter(public_bucket(r["publico_objetivo"]) for r in active)
    hbar(list(pub.keys()), list(pub.values()), "Perfil de publico orientativo", "grafico_publicos_objetivo_v5.png")
    sources = OrderedDict([
        ("Multifuente (>=2 tipos)", sum(r["es_multifuente"] == "si" for r in respaldo)),
        ("Google Places (senal no oficial)", sum(r["google_places_operational"] == "si" for r in respaldo)),
        ("Fuente oficial GCBA/Turismo", sum(r["fuente_oficial_gcba_turismo"] == "si" for r in respaldo)),
        ("Documental / prensa", sum(r["documental_prensa"] == "si" for r in respaldo)),
        ("Sitio propio", sum(r["sitio_propio"] == "si" for r in respaldo)),
        ("Fuente interna sanitizada", sum(r["fuente_interna_sanitizada"] == "si" for r in respaldo)),
    ])
    hbar(list(sources.keys()), list(sources.values()), "Respaldo documental por tipo de fuente", "grafico_respaldo_fuentes_v5.png")


def frequency_bucket(value: str) -> str:
    v = value.lower()
    if "fines de semana" in v:
        return "Itinerante / fin de semana"
    if "todos los dias" in v or ("lunes" in v and "domingo" in v):
        return "Diaria / casi diaria"
    return "Dias especificos"


def public_bucket(value: str) -> str:
    v = value.lower()
    if "consciente" in v:
        return "Consumo consciente"
    if "turistico" in v and "barrial" in v:
        return "Turistico y barrial"
    if "turistico" in v:
        return "Turistico"
    if "mixto" in v:
        return "Mixto"
    return "Barrial"


def main() -> int:
    charts()
    map_sedes()
    map_sedes_v2()
    itinerantes_visual()
    print("Visuales V5 generados sin requests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
