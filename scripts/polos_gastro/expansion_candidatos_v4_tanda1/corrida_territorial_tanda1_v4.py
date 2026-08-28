from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs/polos_gastro/expansion_candidatos_v4_tanda1"
DOC = ROOT / "docs/polos_gastro/expansion_candidatos_v4_tanda1"
EVID = ROOT / "outputs/polos_gastro/evidencia_documental_expansion_v4"
INTEGRATED = ROOT / "outputs/polos_gastro/preparacion_integrada_expansion_v4"
ZONES = {"Z01": "Villa Crespo", "Z02": "Chacarita", "Z03": "Caballito multinodo", "Z04": "Boulevard Caseros — Parque Lezama"}


def fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def main() -> int:
    metrics = pd.read_csv(OUT / "METRICAS_COMPARACION_FUENTES_TANDA1_V4.csv", encoding="utf-8-sig")
    decisions = pd.read_csv(OUT / "MATRIZ_DECISION_TECNICA_TANDA1_V4.csv", encoding="utf-8-sig")
    evidence = pd.read_csv(EVID / "MATRIZ_EVIDENCIA_DOCUMENTAL_EXPANSION_V4.csv", encoding="utf-8-sig")
    qa_sources = pd.read_csv(EVID / "QA_FUENTES_DOCUMENTALES_EXPANSION_V4.csv", encoding="utf-8-sig")
    open_sources = set(qa_sources.loc[qa_sources["estado_url"] == "ABIERTA_Y_LEIDA", "source_id"])
    contrast = []
    for zone, name in ZONES.items():
        d = decisions[decisions["zona_id"] == zone].iloc[0]
        ev = evidence[(evidence["zona_id"] == zone) & (evidence["source_id"].isin(open_sources))]
        ids = ";".join(ev["evidence_id"].astype(str).tolist())
        match = "PARCIAL" if len(ev) else "NO_EVALUABLE"
        contradiction = "La documentación no define geometría; no puede confirmar el cluster."
        if zone == "Z04":
            contradiction = "La evidencia respalda un tramo acotado; no respalda extensión continua hacia Parque Patricios."
        contrast.append({
            "zona": name, "resultado_espacial": d["resultado_tecnico_principal"],
            "nombre_provisional": name, "evidence_ids": ids,
            "coincidencia": match, "contradicción": contradiction,
            "límite_documental": "Interpretación post hoc; sin efecto sobre clusters.",
            "lenguaje_permitido": "estructura espacial candidata; resultado técnico provisional",
            "lenguaje_no_permitido": "polo oficial; delimitación institucional; adopción cerrada",
            "decisión_humana": d["decision_humana_necesaria"],
        })
    pd.DataFrame(contrast).to_csv(OUT / "MATRIZ_CONTRASTE_DOCUMENTAL_POST_HOC_TANDA1_V4.csv",
                                  index=False, encoding="utf-8-sig")

    methodology = """# Metodología — Tanda 1 Expansión V4

**Estado:** EXPERIMENTAL / NO OFICIAL. **Modo:** REUSE_ONLY.

Se reutilizó el universo sanitizado de 6.461 puntos con corte Places 8–9 de julio de 2026. No se ejecutaron consultas nuevas. Los puntos se asignaron mediante intersección geométrica en EPSG:5347; el campo barrio del CSV no intervino.

Se construyeron universos administrativo (F01/F02), Places y combinado. Los controles incluyeron HDBSCAN, variante conservadora, grafo de proximidad de 250 m, continuidad, envolvente cóncava restringida, ablación por fuente y bootstrap por bloques de 250 m. La evidencia documental se incorporó únicamente post hoc y solo cuando su fuente tenía estado `ABIERTA_Y_LEIDA` en el QA documental.

Limitación central: 330 filas categoría×celda —66 celdas físicas— permanecen sin consultar. Por eso las clasificaciones son recomendaciones técnicas provisionales y no adopciones institucionales.
"""
    (DOC / "METODOLOGIA_TANDA1_EXPANSION_V4.md").write_text(methodology, encoding="utf-8")

    specific = {
        "Z01": ("VILLA_CRESPO_RESULTADOS_V4.md", "La señal combinada produce varias piezas. La independencia respecto de Palermo y la transición con Chacarita deben resolverse antes de cualquier adopción. No se crea una prolongación automática de Palermo."),
        "Z02": ("CHACARITA_RESULTADOS_V4.md", "La estructura combinada es multiparte. Newbery y Dorrego deben conservarse como subunidades analíticas separadas; Federico Lacroze opera solo como control. No se crean unidades híbridas con Palermo o Villa Crespo."),
        "Z03": ("CABALLITO_RESULTADOS_V4.md", "La hipótesis nula de fragmentación no se rechaza: el modelo combinado devuelve más de una pieza. Los nodos no se fuerzan dentro de un único Polo Caballito y las 45 filas pendientes permanecen fuera."),
        "Z04": ("BOULEVARD_CASEROS_RESULTADOS_V4.md", "La señal reutilizada es compatible con un corredor técnico acotado en torno a Parque Lezama, pero la evidencia administrativa es pequeña y el tramo no debe extenderse automáticamente hacia Parque Patricios."),
    }
    for zone, (filename, narrative) in specific.items():
        rows = metrics[metrics["zona_id"] == zone]
        d = decisions[decisions["zona_id"] == zone].iloc[0]
        table = ["| Universo | Puntos | F01/F02 | Places | Dependencia Places | Clusters | Estabilidad | Continuidad |",
                 "|---|---:|---:|---:|---:|---:|---:|---|"]
        for r in rows.itertuples():
            table.append(f"| {r.universo} | {r.puntos} | {r.puntos_f01_f02} | {r.puntos_places} | {r.dependencia_places_pct}% | {r.clusters_hdbscan} | {r.estabilidad_bootstrap_bloques} | {r.continuidad} |")
        text = [f"# {ZONES[zone]} — resultados V4", "", "**EXPERIMENTAL / NO OFICIAL · REUSE_ONLY**", "",
                narrative, "", "## Comparación por fuente", "", *table, "", "## Recomendación", "",
                f"- Principal: `{d['resultado_tecnico_principal']}`.", f"- Alternativa: `{d['alternativa']}`.",
                f"- Decisión humana: {d['decision_humana_necesaria']}",
                "- Brecha: la clasificación debe revalidarse si se ejecutan las consultas autorizadas pendientes.", ""]
        (DOC / filename).write_text("\n".join(text), encoding="utf-8")

    decision_lines = ["# Decisión técnica — Tanda 1 Expansión V4", "", "**EXPERIMENTAL / NO OFICIAL. No constituye adopción institucional.**", "",
                      "| Zona | Recomendación principal | Alternativa | Decisión humana |", "|---|---|---|---|"]
    for r in decisions.itertuples():
        decision_lines.append(f"| {r.zona} | `{r.resultado_tecnico_principal}` | `{r.alternativa}` | {r.decision_humana_necesaria} |")
    decision_lines += ["", "La recomendación se basa en el universo reutilizado y queda condicionada por las 330 filas de brecha no ejecutadas.", ""]
    (DOC / "DECISION_TECNICA_TANDA1_V4.md").write_text("\n".join(decision_lines), encoding="utf-8")
    (DOC / "HANDOFF_INTERPRETACION_DOCUMENTAL_POST_HOC_TANDA1_V4.md").write_text(
        "# Handoff — interpretación documental post hoc\n\nUsar exclusivamente las filas vinculadas a fuentes `ABIERTA_Y_LEIDA` en `QA_FUENTES_DOCUMENTALES_EXPANSION_V4.csv`. La documentación interpreta y nombra; no altera clusters. La matriz operativa está en outputs.\n",
        encoding="utf-8")
    (DOC / "HANDOFF_DECISION_HUMANA_TANDA1_V4.md").write_text(
        "# Handoff — decisión humana\n\nQuedan pendientes: adopción o descarte de cada recomendación; nombre institucional; límites; resolución de Villa Crespo respecto de Palermo; relación Newbery–Dorrego; tratamiento multinodo de Caballito; y alcance exacto del tramo Caseros. Ninguna decisión fue tomada automáticamente.\n",
        encoding="utf-8")
    (DOC / "README_TANDA1_EXPANSION_V4.md").write_text(
        "# Tanda 1 — Expansión territorial V4\n\nLínea paralela experimental para Z01–Z04. Modo final `REUSE_ONLY`: sin llamadas API, sin modificación de preflight, evidencia documental, polos cerrados ni informe político. Ver `PRECHECK_API_TANDA1_V4.md`, metodología, resultados por zona y matriz de decisión.\n",
        encoding="utf-8")
    print("DOCS_Y_CONTRASTE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
