"""Mejora analitica del informe Cafecito sin remaquetar PDF.

Genera diagnostico, conclusiones por categoria, lectura territorial agregada,
ranking/mapa comunal y cruces interpretativos. Lee el XLSX original en modo
solo lectura y no publica respuestas individuales ni datos personales.

Uso:
    python scripts/cafecito/mejorar_analitica_cafecito.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
import textwrap
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.cafecito import analizar_cafecito as base  # noqa: E402

DOCS_DIR = REPO_ROOT / "docs" / "cafecito"
OUT_DIR = REPO_ROOT / "outputs" / "cafecito"
GRAF_DIR = OUT_DIR / "graficos_datagastro"
RAW_DIR = REPO_ROOT / "data" / "raw"

DIAGNOSTICO = DOCS_DIR / "DIAGNOSTICO_MEJORAS_INFORME_CAFECITO.md"
CONCLUSIONES = DOCS_DIR / "conclusiones_por_categoria_cafecito.md"
INFORME_MD = DOCS_DIR / "INFORME_CAFECITO_EXPLORATORIO.md"
README = DOCS_DIR / "README_CAFECITO.md"
RESUMEN_TERRITORIAL = OUT_DIR / "resumen_territorial_agregado.csv"
RANKING_COMUNAL = OUT_DIR / "ranking_comunal_cafecito.csv"
CRUCES_INTERPRETATIVOS = OUT_DIR / "cruces_interpretativos_cafecito.md"
MAPA_COMUNAL = GRAF_DIR / "mapa_comunal_cafecito.png"
RANKING_COMUNAL_PNG = GRAF_DIR / "ranking_comunal_cafecito.png"

INK = "#1F3B57"
BLUE = "#2C7FB8"
ORANGE = "#C0762B"
COFFEE = "#6F4E37"
GREY = "#68717C"
LIGHT = "#EEF2F6"
LINE = "#D7DEE8"

EVENT_COMUNA = 13
MIN_PUBLIC_CELL = 3

# Correcciones controladas para texto libre de barrio/localidad. No se publican
# valores individuales; solo se usan para asignar comuna agregada.
BARRIO_ALIASES = {
    "villa pueyrrendon": "villa pueyrredon",
    "villa pueyrredon": "villa pueyrredon",
    "villa lugsno": "villa lugano",
    "lugano": "villa lugano",
    "lugano 1 y 2": "villa lugano",
    "villa ortuzar": "villa ortuzar",
    "villa del parque": "villa del parque",
    "villa mitre": "villa general mitre",
    "nunez": "nunez",
    "nuñez": "nunez",
}


def norm(s: str) -> str:
    s = base.norm_space(s).lower()
    s = "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def pct(n: int, d: int) -> float:
    return (n / d * 100) if d else 0.0


def pct_s(n: int, d: int) -> str:
    return f"{pct(n, d):.1f}%"


def load_barrio_to_comuna() -> dict[str, int]:
    data = json.loads((RAW_DIR / "geo_barrios.geojson").read_text(encoding="utf-8"))
    mapping = {}
    for feature in data["features"]:
        name = feature["properties"]["nombre"]
        comuna = int(feature["properties"]["comuna"])
        mapping[norm(name)] = comuna
    mapping.update({
        "villa pueyrredon": 12,
        "nunez": 13,
        "villa ortuzar": 15,
        "villa general mitre": 11,
        "villa lugano": 8,
    })
    return mapping


def classify_territory(records: list[dict]) -> list[dict]:
    barrio_to_comuna = load_barrio_to_comuna()
    out = []
    for r in records:
        raw = base.norm_space(r.get("barrio_localidad", ""))
        where = base.norm_space(r.get("donde_vivis", ""))
        key = BARRIO_ALIASES.get(norm(raw), norm(raw))
        comuna = barrio_to_comuna.get(key)
        if comuna:
            grupo = "CABA con comuna normalizada"
            confianza = "alta" if norm(raw) == key or key in barrio_to_comuna else "media"
        elif where == "CABA":
            grupo = "CABA sin comuna normalizada"
            confianza = "baja"
        elif where in {"Gran Buenos Aires", "Provincia de Buenos Aires, fuera del GBA"}:
            grupo = where
            confianza = "macro"
        elif where:
            grupo = where
            confianza = "macro"
        else:
            grupo = "No clasificado"
            confianza = "baja"
        out.append({
            "grupo_territorial": grupo,
            "comuna": comuna,
            "confianza": confianza,
            "donde_vivis": where,
        })
    return out


def build_stats(records: list[dict]) -> dict[str, dict]:
    stats = {}
    for key in base.CERRADAS_SIMPLES:
        c = base.count_simple(records, key)
        stats[key] = {"items": base.ordered_items(key, c), "base": sum(c.values())}
    for key in base.CERRADAS_MULTI:
        c, n = base.count_multi(records, key)
        stats[key] = {"items": c.most_common(), "base": n}
    return stats


def dict_items(stats: dict, key: str) -> dict[str, int]:
    return dict(stats[key]["items"])


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def write_territorial_outputs(records: list[dict], territorial: list[dict]) -> tuple[list[dict], list[dict]]:
    n_total = len(records)
    macro = Counter(t["donde_vivis"] or "No clasificado" for t in territorial)
    grupos = Counter(t["grupo_territorial"] for t in territorial)
    resumen_rows = []
    for category, count in macro.most_common():
        resumen_rows.append({
            "tipo": "procedencia_macro_declarada",
            "categoria": category,
            "cantidad": count,
            "porcentaje": f"{pct(count, n_total):.1f}",
            "nota": "Variable cerrada del formulario; no usa barrio/localidad libre.",
        })
    for category, count in grupos.most_common():
        resumen_rows.append({
            "tipo": "normalizacion_territorial_agregada",
            "categoria": category,
            "cantidad": count,
            "porcentaje": f"{pct(count, n_total):.1f}",
            "nota": "Derivado agregado de barrio/localidad; no publica valores individuales.",
        })
    write_csv(RESUMEN_TERRITORIAL, resumen_rows, ["tipo", "categoria", "cantidad", "porcentaje", "nota"])

    comuna_counts = Counter(t["comuna"] for t in territorial if t["comuna"])
    ranking_rows = []
    low_count_total = 0
    low_communes = 0
    for comuna, count in comuna_counts.most_common():
        if count < MIN_PUBLIC_CELL:
            low_count_total += count
            low_communes += 1
            continue
        ranking_rows.append({
            "comuna": str(comuna),
            "cantidad_respuestas": count,
            "porcentaje_total_respuestas": f"{pct(count, n_total):.1f}",
            "porcentaje_caba_normalizada": f"{pct(count, sum(comuna_counts.values())):.1f}",
            "publicable": "si",
            "nota": "Ranking agregado por comuna; no expone barrios/localidades individuales.",
        })
    if low_count_total:
        ranking_rows.append({
            "comuna": "Otras comunas CABA normalizadas",
            "cantidad_respuestas": low_count_total,
            "porcentaje_total_respuestas": f"{pct(low_count_total, n_total):.1f}",
            "porcentaje_caba_normalizada": f"{pct(low_count_total, sum(comuna_counts.values())):.1f}",
            "publicable": "agrupado",
            "nota": f"Agrupa {low_communes} comunas con menos de {MIN_PUBLIC_CELL} respuestas.",
        })
    write_csv(
        RANKING_COMUNAL,
        ranking_rows,
        ["comuna", "cantidad_respuestas", "porcentaje_total_respuestas",
         "porcentaje_caba_normalizada", "publicable", "nota"],
    )
    return resumen_rows, ranking_rows


def draw_ranking_comunal(ranking_rows: list[dict]) -> None:
    public_rows = [r for r in ranking_rows if str(r["comuna"]).isdigit()]
    if not public_rows:
        return
    labels = [f"Comuna {r['comuna']}" for r in reversed(public_rows)]
    values = [int(r["cantidad_respuestas"]) for r in reversed(public_rows)]
    colors = [ORANGE if label == f"Comuna {EVENT_COMUNA}" else BLUE for label in labels]
    fig, ax = plt.subplots(figsize=(8.4, max(3.0, 0.48 * len(labels) + 1.5)))
    ax.barh(labels, values, color=colors, height=0.62)
    ax.set_title("Ranking comunal agregado de respuestas CABA", loc="left",
                 color=INK, fontsize=14, fontweight="bold", pad=12)
    ax.text(0, 1.02, "Solo comunas normalizadas desde barrio/localidad con confianza suficiente.",
            transform=ax.transAxes, color=GREY, fontsize=9)
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.tick_params(axis="x", length=0, labelbottom=False)
    max_v = max(values)
    for i, v in enumerate(values):
        ax.text(v + max_v * 0.03, i, str(v), va="center", color=INK, fontweight="bold")
    ax.set_xlim(0, max_v * 1.22)
    fig.text(0.02, 0.03, "Fuente: formulario Cafecito. Lectura agregada; no representa al público total.",
             color=GREY, fontsize=8)
    fig.tight_layout(rect=[0, 0.06, 1, 0.94])
    GRAF_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(RANKING_COMUNAL_PNG, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def rings(geom: dict) -> list[list[list[float]]]:
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [poly[0] for poly in geom["coordinates"]]
    return []


def draw_mapa_comunal(ranking_rows: list[dict]) -> bool:
    geo_path = RAW_DIR / "geo_comunas.geojson"
    if not geo_path.exists():
        return False
    counts = {int(r["comuna"]): int(r["cantidad_respuestas"]) for r in ranking_rows if str(r["comuna"]).isdigit()}
    data = json.loads(geo_path.read_text(encoding="utf-8"))
    max_count = max(counts.values()) if counts else 1
    cmap = plt.get_cmap("Blues")
    fig, ax = plt.subplots(figsize=(7.8, 8.0))
    for feature in data["features"]:
        comuna = int(feature["properties"]["comuna"])
        count = counts.get(comuna, 0)
        color = cmap(0.18 + 0.72 * (count / max_count)) if count else "#F2F4F7"
        for ring in rings(feature["geometry"]):
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            ax.fill(xs, ys, facecolor=color, edgecolor="white", lw=1.1)
        # centroide aproximado para etiqueta
        coords = [p for ring in rings(feature["geometry"]) for p in ring]
        if coords:
            cx = sum(p[0] for p in coords) / len(coords)
            cy = sum(p[1] for p in coords) / len(coords)
            label = f"C{comuna}\n{count}" if count else f"C{comuna}"
            ax.text(cx, cy, label, ha="center", va="center", fontsize=7.6,
                    color=INK if count < max_count * 0.65 else "white", fontweight="bold")
    ax.set_title("Respuestas normalizadas por comuna (CABA)", loc="left",
                 color=INK, fontsize=14, fontweight="bold", pad=12)
    ax.text(0, 1.01, "Lectura agregada desde barrio/localidad. No publica respuestas individuales.",
            transform=ax.transAxes, fontsize=9, color=GREY)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.text(0.02, 0.03,
             "Nota: si Comuna 13 aparece alta, puede reflejar cercanía al evento y punto de captación.",
             color=GREY, fontsize=8)
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    GRAF_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(MAPA_COMUNAL, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return True


def channel_flags(record: dict) -> dict[str, bool]:
    parts = set(base.split_multi(record.get("como_se_entero", ""), "como_se_entero"))
    return {
        "instagram": "Instagram" in parts,
        "paso_zona": "Pase por la zona y lo ví" in parts,
        "interpersonal": "Por amigos, familia o conocidos" in parts,
    }


def age_group(age: str) -> str:
    if age in {"18 a 24", "25 a 34"}:
        return "18 a 34"
    if age in {"35 a 44"}:
        return "35 a 44"
    if age in {"45 a 54", "55 a 64", "65 o más", "65 o mas"}:
        return "45 o más"
    return "Sin dato"


def crosstab(records: list[dict], a_fn, b_fn) -> tuple[dict[str, Counter], int]:
    table: dict[str, Counter] = defaultdict(Counter)
    base_n = 0
    for r in records:
        a = a_fn(r)
        b = b_fn(r)
        if not a or not b:
            continue
        table[a][b] += 1
        base_n += 1
    return table, base_n


def md_table(table: dict[str, Counter]) -> list[str]:
    cols = sorted({c for row in table.values() for c in row})
    lines = ["| Segmento | " + " | ".join(cols) + " | Total |",
             "|" + "---|" * (len(cols) + 2)]
    for key in sorted(table):
        total = sum(table[key].values())
        lines.append("| " + key + " | " + " | ".join(str(table[key].get(c, 0)) for c in cols) + f" | {total} |")
    return lines


def write_cruces(records: list[dict], territorial: list[dict]) -> None:
    enriched = []
    for r, t in zip(records, territorial):
        rr = dict(r)
        rr.update(t)
        flags = channel_flags(r)
        rr.update(flags)
        rr["edad_grupo"] = age_group(base.norm_space(r.get("rango_edad", "")))
        rr["canal_principal"] = base.split_multi(r.get("como_se_entero", ""), "como_se_entero")[0] if base.split_multi(r.get("como_se_entero", ""), "como_se_entero") else ""
        rr["comuna_grupo"] = f"Comuna {t['comuna']}" if t.get("comuna") else t["grupo_territorial"]
        enriched.append(rr)

    sections: list[str] = ["# Cruces interpretativos Cafecito\n",
                           "Lecturas exploratorias. No se fuerzan conclusiones con celdas chicas.\n"]

    table, base_n = crosstab(enriched, lambda r: r["edad_grupo"], lambda r: r["canal_principal"])
    sections += ["## Edad x canal principal\n",
                 f"*Base: {base_n}. Señal para ajustar comunicación; no segmentación concluyente.*\n",
                 *md_table(table), ""]

    table, base_n = crosstab(enriched, lambda r: r["edad_grupo"], lambda r: "pasó por la zona" if r["paso_zona"] else "otros canales")
    older = table.get("45 o más", Counter())
    older_paso = older.get("pasó por la zona", 0)
    older_total = sum(older.values())
    sections += ["## Edad x paso por la zona\n",
                 f"*Base: {base_n}. En 45 o más, {older_paso}/{older_total} mencionó paso por la zona. "
                 "Por bajo N se formula como hipótesis, no como conclusión fuerte.*\n",
                 *md_table(table), ""]

    table, base_n = crosstab(enriched, lambda r: base.norm_space(r.get("primera_vez", "")), lambda r: base.norm_space(r.get("acepta_contacto", "")))
    sections += ["## Primera vez x aceptación de contacto\n",
                 f"*Base: {base_n}. Sirve para ver potencial de convertir primeras visitas y sostener recurrentes.*\n",
                 *md_table(table), ""]

    table, base_n = crosstab(enriched, lambda r: r["comuna_grupo"] if r.get("comuna") and sum(1 for x in enriched if x.get("comuna") == r.get("comuna")) >= MIN_PUBLIC_CELL else "No CABA / no clasificado", lambda r: base.norm_space(r.get("que_intereso", "")))
    sections += ["## Procedencia/comuna agregada x interés principal\n",
                 f"*Base: {base_n}. Comunas con menos de {MIN_PUBLIC_CELL} respuestas se agrupan para evitar granularidad riesgosa.*\n",
                 *md_table(table), ""]

    table, base_n = crosstab(enriched, lambda r: base.norm_space(r.get("con_quien", "")), lambda r: base.norm_space(r.get("que_intereso", "")))
    sections += ["## Con quién vino x interés principal\n",
                 f"*Base: {base_n}. Lectura sobre tipo de plan; no mide consumo ni tamaño real del grupo.*\n",
                 *md_table(table), ""]

    CRUCES_INTERPRETATIVOS.write_text("\n".join(sections) + "\n", encoding="utf-8")


def write_diagnostico() -> None:
    text = """# Diagnóstico de mejoras - Informe Cafecito

## Qué sirve de la versión actual

- Ya existe una base reproducible: lectura del XLSX en modo solo lectura, outputs agregados, gráficos y PDF.
- El informe ya declara la muestra como exploratoria y mantiene fuera de outputs públicos correos, marca temporal y barrio/localidad granular.
- La categoría `Por amigos, familia o conocidos` quedó unificada y protegida en el análisis multi-respuesta.
- La estética DataGastro mejoró respecto de la exportación cruda de Google Forms: hay portada, KPI cards, gráficos y footer homogéneo.

## Qué falta para acercarse a Mercados/Casas

- La lectura todavía estaba muy centrada en describir categorías; faltaba traducir cada resultado en decisión de gestión.
- Faltaba una sección de conclusiones por categoría: fidelización, captación, comunicación, experiencia, programación y operativo de campo.
- La lectura territorial estaba limitada a CABA vs no CABA; faltaba explorar comuna agregada sin publicar barrios/localidades individuales.
- Los cruces existentes eran útiles, pero necesitaban interpretación textual y advertencias sobre celdas chicas.

## Páginas/secciones con oportunidad de mejora visual

- Algunas páginas del PDF funcionan como separadores con mucho aire; conviene aprovechar recuadros tipo "Lectura ejecutiva", "Cuidado metodológico" y "Qué decisión habilita".
- Las páginas de gráficos podrían sumar una línea de decisión debajo de cada visual, no solo descripción del máximo.
- La tabla pregunta por pregunta es útil, pero en PDF puede volverse densa; conviene convertirla en bloques o recuadros cuando se remaquete.

## Gráficos a reforzar

- Territorio: agregar ranking comunal y mapa agregado por comuna cuando haya geometría disponible.
- Comunicación: destacar Instagram, recomendación interpersonal y paso por la zona como tres mecanismos distintos.
- Fidelización: cruzar primera vez y aceptación de contacto.
- Operativo de campo: sumar un bloque de aprendizajes para mejorar captación, QR, incentivos y rol de locales adheridos.

## Inspiración del Google Form / gráficos originales

- El DOCX exportado de Google Forms confirma que el formulario cubre las preguntas principales, pero su visual es descriptivo.
- La mejora DataGastro debe conservar la trazabilidad de esas preguntas y agregar interpretación: qué se buscaba medir, qué se observó y qué decisión habilita.
"""
    DIAGNOSTICO.write_text(text, encoding="utf-8")


def write_conclusiones(stats: dict, territorial_rows: list[dict], ranking_rows: list[dict]) -> None:
    d_primera = dict_items(stats, "primera_vez")
    d_contacto = dict_items(stats, "acepta_contacto")
    d_edad = dict_items(stats, "rango_edad")
    d_genero = dict_items(stats, "genero")
    d_vivis = dict_items(stats, "donde_vivis")
    d_canal = dict_items(stats, "como_se_entero")
    d_quien = dict_items(stats, "con_quien")
    d_interes = dict_items(stats, "que_intereso")
    d_futuro = dict_items(stats, "eventos_futuros")
    n = stats["rango_edad"]["base"]
    contacto_base = stats["acepta_contacto"]["base"]
    numeric_ranking = [r for r in ranking_rows if str(r["comuna"]).isdigit()]
    top_comunas = ", ".join(f"Comuna {r['comuna']} ({r['cantidad_respuestas']})" for r in numeric_ranking[:5]) or "sin comuna normalizada suficiente"
    grouped_low = next((r for r in ranking_rows if not str(r["comuna"]).isdigit()), None)
    grouped_text = f" Las comunas por debajo del umbral se agrupan como '{grouped_low['comuna']}' ({grouped_low['cantidad_respuestas']})." if grouped_low else ""
    comuna13 = next((r for r in numeric_ranking if int(r["comuna"]) == EVENT_COMUNA), None)
    comuna13_text = (
        f"Comuna 13 aparece con {comuna13['cantidad_respuestas']} respuestas normalizadas; puede reflejar cercanía a Belgrano y al punto de captación."
        if comuna13 else
        "Comuna 13 no aparece entre las comunas normalizadas principales."
    )

    text = f"""# Conclusiones por categoría - Cafecito

## 1. Valoración general e interés futuro

Una parte importante de las personas encuestadas aceptó recibir novedades sobre próximos eventos ({d_contacto.get('Si, acepto', 0)}/{contacto_base}). Leído junto con que la mayoría declaró haber participado previamente en eventos gastronómicos de la Ciudad ({d_primera.get('No, ya participé de otros eventos', 0)}/{n}), esto sugiere que entre quienes respondieron hay un público interesado, relativamente fidelizado y dispuesto a seguir recibiendo información.

No se mide satisfacción directa: la lectura correcta es **interés declarado** y **potencial de contacto**, no satisfacción del público total.

## 2. Fidelización y captación

El evento combina público recurrente y público nuevo: {d_primera.get('No, ya participé de otros eventos', 0)}/{n} ya habían participado en otros eventos, mientras {d_primera.get('Si, es la primera vez', 0)}/{n} era primera vez. Esto habilita una estrategia doble: fidelizar a quienes ya reconocen propuestas gastronómicas de la Ciudad y convertir primeras visitas en audiencia futura.

La aceptación de contacto ({d_contacto.get('Si, acepto', 0)}/{contacto_base}) refuerza esa oportunidad, siempre sin exponer correos ni datos personales en outputs públicos.

## 3. Público captado

El público más captado por el relevamiento fue joven-adulto: 25 a 34 fue el tramo principal ({d_edad.get('25 a 34', 0)}/{n}) y el bloque 18 a 44 suma {d_edad.get('18 a 24', 0) + d_edad.get('25 a 34', 0) + d_edad.get('35 a 44', 0)}/{n}. También hubo mayoría de respuestas de mujeres ({d_genero.get('Mujer', 0)}/{n}) y de personas que declaran vivir en CABA ({d_vivis.get('CABA', 0)}/{n}).

Esto describe la muestra encuestada, no el público total del evento.

## 4. Alcance territorial

CABA concentra la mayor parte de las respuestas ({d_vivis.get('CABA', 0)}/{n}), pero no debe asumirse que todo el público proviene de Belgrano. La columna barrio/localidad permite una lectura interna más fina, aunque no conviene publicar la lista granular por la cantidad de categorías chicas.

Ranking comunal agregado: {top_comunas}.{grouped_text} {comuna13_text} La lectura territorial debe tomarse como señal de captación y cercanía, no como mapa representativo de asistencia.

## 5. Comunicación y canales de llegada

Instagram aparece como canal principal ({d_canal.get('Instagram', 0)}/{n}). La recomendación interpersonal también pesa ({d_canal.get('Por amigos, familia o conocidos', 0)}/{n}) y el paso por la zona aparece como tercer mecanismo ({d_canal.get('Pase por la zona y lo ví', 0)}/{n}).

En las respuestas procesadas no aparece una categoría fuerte asociada a cafeterías o locales adheridos como canal de llegada. Esto abre una oportunidad: pedir a cafeterías/locales participantes que comuniquen el evento mediante historias, posteos, folletería, cartelería o QR en el local.

Para público de mayor edad o personas que no viven cerca del evento, depender solo de Instagram o del paso casual por la zona puede dejar afuera segmentos potenciales. Los locales adheridos pueden funcionar como puntos físicos de difusión.

## 6. Experiencia del evento y tipo de plan

Cafecito funciona principalmente como plan social: en pareja ({d_quien.get('En pareja', 0)}), con amigos/as ({d_quien.get('Con amigos/as', 0)}) y con familia ({d_quien.get('Con familia', 0)}) concentran la mayor parte de las respuestas. Solo/a y trabajo/estudio son minoritarios.

Esto debería orientar espacios, señalética, horarios, disponibilidad de mesas/zonas de descanso, comunicación y propuestas complementarias.

## 7. Motivación principal

El atractivo no es solo consumir café. Probar café/cafeterías fue la principal motivación ({d_interes.get('Probar café / cafeterías', 0)}/{n}), seguida por pasear o hacer una salida ({d_interes.get('Pasear o hacer una salida', 0)}/{n}) y conocer propuestas gastronómicas nuevas ({d_interes.get('Conocer propuestas gastronomicas nuevas', 0)}/{n}).

La comunicación debería vender tanto producto como experiencia: café, paseo, música, salida y descubrimiento.

## 8. Programación futura

Las respuestas sugieren líneas iniciales para próximos eventos o activaciones: vino ({d_futuro.get('Vino', 0)}), pastelería ({d_futuro.get('Pasteleria', 0)}), food trucks ({d_futuro.get('Food trucks', 0)}), café ({d_futuro.get('Café', 0)}) y ferias/mercados ({d_futuro.get('Ferias y mercados', 0)}).

No se trata de demanda representativa: son señales de interés dentro de la muestra.

## 9. Diseño del formulario y operativo de campo

Este fue un primer experimento de medición. Para próximos relevamientos conviene:

- motivar mejor a visitantes para contestar;
- asegurar recompensas claras por completar correctamente el formulario;
- aumentar cantidad de recompensas disponibles si la dinámica lo permite;
- pedir a la productora o equipo organizador que asigne personas a encuestar;
- colocar QR visibles en varios puntos del evento;
- usar cartelería con mensaje claro;
- simplificar preguntas;
- revisar conectividad/offline;
- definir antes qué decisión alimenta cada pregunta.
"""
    CONCLUSIONES.write_text(text, encoding="utf-8")


def update_informe(conclusiones_text: str) -> None:
    current = INFORME_MD.read_text(encoding="utf-8")
    start = current.find("## Conclusiones por categoría")
    if start != -1:
        end = current.find("## Conclusión general", start)
        if end != -1:
            next_section = current.find("\n## ", end + 1)
            if next_section != -1:
                current = current[:start].rstrip() + "\n\n" + current[next_section:].lstrip()
            else:
                current = current[:start].rstrip() + "\n"

    general = """## Conclusión general

El relevamiento no permite representar al total del público, pero sí muestra señales útiles: Cafecito captó principalmente público joven-adulto de CABA, con alta presencia femenina en la muestra; combina público recurrente y nuevas visitas; Instagram es el principal canal, pero la recomendación interpersonal y la visibilidad territorial también importan; la aceptación de contacto abre una oportunidad para construir audiencia futura; y el interés en vino, pastelería, food trucks, café y ferias/mercados ofrece pistas para programación posterior.

El formulario funcionó como primer experimento de medición, pero debería fortalecerse con mayor muestra, mejor incentivo, más QR, equipo de encuestadores y mejor articulación con locales adheridos.
"""
    insert = "\n".join(CONCLUSIONES.read_text(encoding="utf-8").splitlines()[2:])
    block = "## Conclusiones por categoría\n\n" + insert.strip() + "\n\n" + general.strip() + "\n\n"
    marker = "## 12. Anexo metodológico"
    if marker in current:
        current = current.replace(marker, block + marker)
    else:
        current = current.rstrip() + "\n\n" + block
    INFORME_MD.write_text(current, encoding="utf-8")


def update_readme(map_created: bool) -> None:
    text = README.read_text(encoding="utf-8")
    block = f"""## Mejora analítica territorial e interpretativa

Para regenerar la capa analítica previa a una nueva maquetación PDF:

```powershell
python scripts/cafecito/mejorar_analitica_cafecito.py
```

Outputs nuevos:

- Diagnóstico de mejoras: `docs/cafecito/DIAGNOSTICO_MEJORAS_INFORME_CAFECITO.md`
- Conclusiones por categoría: `docs/cafecito/conclusiones_por_categoria_cafecito.md`
- Resumen territorial agregado: `outputs/cafecito/resumen_territorial_agregado.csv`
- Ranking comunal: `outputs/cafecito/ranking_comunal_cafecito.csv`
- Cruces interpretativos: `outputs/cafecito/cruces_interpretativos_cafecito.md`
- Gráfico ranking comunal: `outputs/cafecito/graficos_datagastro/ranking_comunal_cafecito.png`
- Mapa comunal: `outputs/cafecito/graficos_datagastro/mapa_comunal_cafecito.png` {"(generado)" if map_created else "(pendiente: geometría no disponible)"}
"""
    heading = "## Mejora analítica territorial e interpretativa"
    if heading in text:
        text = text[:text.find(heading)].rstrip() + "\n\n" + block
    else:
        text = text.rstrip() + "\n\n" + block
    README.write_text(text, encoding="utf-8")


def main() -> int:
    records = base.read_xlsx(base.XLSX)
    stats = build_stats(records)
    territorial = classify_territory(records)
    _, ranking_rows = write_territorial_outputs(records, territorial)
    draw_ranking_comunal(ranking_rows)
    map_created = draw_mapa_comunal(ranking_rows)
    write_cruces(records, territorial)
    write_diagnostico()
    write_conclusiones(stats, territorial, ranking_rows)
    update_informe(CONCLUSIONES.read_text(encoding="utf-8"))
    update_readme(map_created)

    print("=" * 72)
    print("Mejora analítica Cafecito")
    print(f"  Respuestas: {len(records)}")
    print(f"  Ranking comunal: {RANKING_COMUNAL.relative_to(REPO_ROOT)}")
    print(f"  Mapa comunal: {'generado' if map_created else 'pendiente'}")
    print(f"  Cruces: {CRUCES_INTERPRETATIVOS.relative_to(REPO_ROOT)}")
    print(f"  Conclusiones: {CONCLUSIONES.relative_to(REPO_ROOT)}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
