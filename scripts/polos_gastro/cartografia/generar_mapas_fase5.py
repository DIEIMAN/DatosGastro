# -*- coding: utf-8 -*-
"""
Fase 5 — Mapas territoriales útiles PolosGastro (sobrios, no decorativos).

Genera en outputs/polos_gastro/fase5/mapas/ (carpeta nueva, NO sobrescribe nada previo):
- mapa1_universo_por_grupo.png       (núcleo + relevante + emergente + anexo)
- mapa2_nucleos_principales.png      (solo núcleo principal)
- mapa3_relevantes_y_emergentes.png  (zona relevante + emergente/candidato)
- mapa4_anexo_casos_secundarios.png  (anexo)
- mapa5_revision_documentacion.png   (polos con estado débil o pendiente)

Reglas:
- Barrios/comunas oficiales (Buenos Aires Data) = REFERENCIA territorial, NO delimitación de polos.
- Sin polígonos de polos, sin coordenadas Google, sin geocodificar locales.
- Si un polo no tiene barrio reconocible en la cartografía oficial, se marca como pendiente y
  NO se inventa geometría.
- Insumo de barrio/comuna por polo: base_delimitacion_preliminar_polos_gastro.csv.
- Estado de documentación: polos_gastro_universo_consolidado_fase5.csv.
"""
from __future__ import annotations

import csv
import unicodedata
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs" / "polos_gastro"
MAPDIR = OUT / "fase5" / "mapas"
CARTO = ROOT / "PolosGastro" / "cartografia"
FECHA_CORTE = "2026-06-30"

DELIM = OUT / "base_delimitacion_preliminar_polos_gastro.csv"
CONS = OUT / "fase5" / "polos_gastro_universo_consolidado_fase5.csv"
BARRIOS_GEOJSON = CARTO / "barrios_caba.geojson"

GROUP_ORDER = ["nucleo_principal", "zona_relevante", "emergente_o_candidato", "anexo", "no_incluir_por_ahora"]
GROUP_LABELS = {
    "nucleo_principal": "Núcleo principal",
    "zona_relevante": "Zona relevante",
    "emergente_o_candidato": "Emergente / candidato",
    "anexo": "Anexo",
    "no_incluir_por_ahora": "No incluir por ahora",
}
GROUP_COLORS = {
    "nucleo_principal": "#275DAD",
    "zona_relevante": "#2A9D8F",
    "emergente_o_candidato": "#E9B44C",
    "anexo": "#7D8597",
    "no_incluir_por_ahora": "#C44536",
}
PRIORIDAD = {"nucleo_principal": 1, "zona_relevante": 2, "emergente_o_candidato": 3,
             "anexo": 4, "no_incluir_por_ahora": 5}

FOOTER = ("Base cartográfica: Buenos Aires Data — Barrios CABA (GeoJSON). "
          "Barrios = referencia territorial, no delimitación oficial de polos. "
          f"Fecha de corte: {FECHA_CORTE}.")


def norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s.lower().strip()


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def primer_barrio(barrios_asociados: str) -> str:
    raw = barrios_asociados.split(";")[0].split(",")[0].strip()
    raw = (raw.replace("La Paternal", "Paternal")
              .replace("Nunez/Belgrano entorno Ciudad Universitaria", "Nunez")
              .replace("Belgrano/Colegiales (aproximacion)", "Belgrano")
              .replace("San Nicolas", "San Nicolas"))
    return raw


def load_polos() -> list[dict]:
    """Une delimitación (barrio/comuna) + consolidado (estado_documentacion)."""
    delim = {r["polo_id"].strip(): r for r in read_csv(DELIM)}
    cons = {r["polo_id"].strip(): r for r in read_csv(CONS)}
    polos = []
    for pid, d in delim.items():
        c = cons.get(pid, {})
        polos.append({
            "polo_id": pid,
            "nombre": d["nombre_publico"],
            "grupo": d["grupo_informe"],
            "barrio": primer_barrio(d["barrios_asociados"]),
            "barrios_raw": d["barrios_asociados"],
            "precision": d["nivel_precision"],
            "estado_doc": c.get("estado_documentacion", "pendiente"),
            "prioridad_rev": c.get("prioridad_revision", "media"),
        })
    return polos


def barrio_match(polos, barrios_norm):
    """Marca qué polos tienen barrio reconocible en cartografía oficial."""
    pend = []
    for p in polos:
        p["match"] = norm(p["barrio"]) in barrios_norm
        if not p["match"]:
            pend.append(p["nombre"])
    return pend


def render_map(polos, barrios, filename, titulo, subtitulo, grupos_incluidos,
               modo_revision=False):
    barrios = barrios.to_crs(3857)
    barrios = barrios.copy()
    barrios["_norm"] = barrios["nombre"].map(norm)

    sel = [p for p in polos if p["grupo"] in grupos_incluidos and p["match"]]
    if modo_revision:
        sel = [p for p in polos if p["match"] and p["estado_doc"] in ("debil", "pendiente")]

    # barrio -> grupo (prioridad: grupo más alto si se comparte barrio)
    barrio_to_group = {}
    for p in sorted(sel, key=lambda p: PRIORIDAD[p["grupo"]], reverse=True):
        barrio_to_group[norm(p["barrio"])] = p["grupo"]

    fig, ax = plt.subplots(figsize=(11, 12), dpi=170)
    barrios.plot(ax=ax, color="#F4F4F4", edgecolor="#CFCFCF", linewidth=0.6, zorder=1)

    if modo_revision:
        # color por estado (rojo pendiente, naranja débil), no por grupo
        EST_COLOR = {"pendiente": "#C44536", "debil": "#E9B44C"}
        barrio_est = {}
        for p in sorted(sel, key=lambda p: 0 if p["estado_doc"] == "pendiente" else 1):
            barrio_est[norm(p["barrio"])] = p["estado_doc"]
        for est, col in EST_COLOR.items():
            names = [bn for bn, e in barrio_est.items() if e == est]
            sub = barrios[barrios["_norm"].isin(names)]
            if len(sub):
                sub.plot(ax=ax, color=col, edgecolor="white", linewidth=0.7, alpha=0.8, zorder=2)
        legend = [Patch(facecolor=EST_COLOR["pendiente"], edgecolor="white", label="Documentación pendiente"),
                  Patch(facecolor=EST_COLOR["debil"], edgecolor="white", label="Documentación débil")]
        leg_title = "Estado de documentación"
    else:
        for grp in GROUP_ORDER:
            names = [bn for bn, g in barrio_to_group.items() if g == grp]
            if not names:
                continue
            sub = barrios[barrios["_norm"].isin(names)]
            if len(sub):
                sub.plot(ax=ax, color=GROUP_COLORS[grp], edgecolor="white",
                         linewidth=0.7, alpha=0.80, zorder=2)
        legend = [Patch(facecolor=GROUP_COLORS[g], edgecolor="white", label=GROUP_LABELS[g])
                  for g in GROUP_ORDER if g in barrio_to_group.values()]
        leg_title = "Grupo (barrio asociado)"

    # etiquetas combinadas por barrio
    by_barrio = defaultdict(list)
    for p in sel:
        by_barrio[norm(p["barrio"])].append(p)
    BARRIO_LABEL = {
        norm("Palermo"): "Palermo\n(Soho/Hollywood/Cañitas)",
        norm("Villa Urquiza"): "Villa Urquiza / DoHo",
    }
    for bn, items in by_barrio.items():
        sub = barrios[barrios["_norm"] == bn]
        if not len(sub):
            continue
        c = sub.geometry.representative_point().iloc[0]
        if bn in BARRIO_LABEL and not modo_revision:
            label = BARRIO_LABEL[bn]
        elif len(items) == 1:
            label = items[0]["nombre"]
        elif modo_revision and len(items) > 2:
            # En el mapa interno, evitar etiquetas largas: usar el nombre del barrio + conteo.
            label = f"{barrios[barrios['_norm'] == bn]['nombre'].iloc[0]}\n(+{len(items)} casos)"
        else:
            label = " / ".join(dict.fromkeys(i["nombre"] for i in items))
        ax.annotate(label, (c.x, c.y), fontsize=7.4, ha="center", va="center",
                    color="#1A1A1A", zorder=5,
                    bbox={"boxstyle": "round,pad=0.18", "facecolor": "white",
                          "alpha": 0.85, "edgecolor": "none"})

    ax.set_axis_off()
    fig.suptitle(titulo, fontsize=16, x=0.5, y=0.965)
    ax.set_title(subtitulo, fontsize=11, color="#444", pad=6)
    ax.legend(handles=legend, loc="lower left", frameon=False, fontsize=9, title=leg_title)
    fig.text(0.5, 0.085,
             "Mapa territorial preliminar. Barrios como referencia; no delimita oficialmente polos.",
             ha="center", fontsize=9.5, color="#C44536", weight="bold")
    fig.text(0.01, 0.01, FOOTER, ha="left", va="bottom", fontsize=7, color="#4A4A4A")
    fig.savefig(MAPDIR / filename, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return len(sel)


def main():
    MAPDIR.mkdir(parents=True, exist_ok=True)
    polos = load_polos()
    barrios = gpd.read_file(BARRIOS_GEOJSON)
    barrios_norm = {norm(x) for x in barrios["nombre"]}
    pend = barrio_match(polos, barrios_norm)
    if pend:
        print("[fase5] polos sin barrio reconocible en cartografía (marcados pendientes, no mapeados):")
        for n in pend:
            print("   -", n)

    n1 = render_map(polos, barrios, "mapa1_universo_por_grupo.png",
                    "Universo de polos por grupo — PolosGastro",
                    "Núcleo principal, zonas relevantes, emergentes y anexo (sin 'no incluir')",
                    {"nucleo_principal", "zona_relevante", "emergente_o_candidato", "anexo"})
    n2 = render_map(polos, barrios, "mapa2_nucleos_principales.png",
                    "Núcleos principales — PolosGastro",
                    "Solo polos de núcleo principal",
                    {"nucleo_principal"})
    n3 = render_map(polos, barrios, "mapa3_relevantes_y_emergentes.png",
                    "Zonas relevantes y emergentes — PolosGastro",
                    "Zona relevante + emergente/candidato",
                    {"zona_relevante", "emergente_o_candidato"})
    n4 = render_map(polos, barrios, "mapa4_anexo_casos_secundarios.png",
                    "Anexo y casos secundarios — PolosGastro",
                    "Polos de anexo (mención cualitativa, no cuerpo principal)",
                    {"anexo"})
    n5 = render_map(polos, barrios, "mapa5_revision_documentacion.png",
                    "Mapa de revisión — documentación débil o pendiente",
                    "Uso interno: dónde falta reforzar evidencia",
                    set(), modo_revision=True)

    print(f"[fase5] mapas generados en {MAPDIR}")
    print(f"   mapa1 universo={n1}  mapa2 nucleos={n2}  mapa3 rel+emerg={n3}  "
          f"mapa4 anexo={n4}  mapa5 revision={n5}")


if __name__ == "__main__":
    main()
