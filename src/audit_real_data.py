from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from config import DATA_ANALYTICS, DATA_PROCESSED, DATA_RAW, DATA_SEEDS, DOCS, PROFILE_OUTPUTS

TODAY = date.today().isoformat()


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception:
        return pd.DataFrame()


def classify_file(path: Path, layer: str, df: pd.DataFrame) -> dict:
    rows = len(df)
    columns = len(df.columns)
    name = path.name
    if layer == "raw":
        origin = "dataset real probable" if not name.startswith("raw_") and path.stat().st_size >= 1024 else "pendiente/insuficiente"
    elif layer == "seeds":
        origin = "seed/manual"
    elif layer == "analytics":
        if "estado_datos" in df.columns and not df.empty:
            origin = " | ".join(sorted(set(df["estado_datos"].astype(str))))
        else:
            origin = "sin estado_datos"
    else:
        if "origen_dato" in df.columns and not df.empty:
            origin = " | ".join(sorted(set(df["origen_dato"].astype(str))))
        else:
            origin = "modelo/dimension"

    if rows == 0:
        apto = "no"
        reason = "archivo vacio o sin filas"
    elif layer == "analytics":
        apto = "si" if "apto_dashboard" in df.columns and df["apto_dashboard"].astype(str).eq("si").all() else "no"
        reason = "apto_dashboard provisto por analytics" if apto == "si" else "analytics no apta o basada en seed/parcial"
    elif "seed" in origin.lower():
        apto = "no"
        reason = "seed/manual; solo desarrollo"
    elif layer == "raw" and path.stat().st_size < 1024:
        apto = "no"
        reason = "archivo menor a 1 KB; no tratar como dataset real"
    elif layer == "processed" and "origen_dato" in df.columns and df["origen_dato"].astype(str).str.contains("seed", case=False).any():
        apto = "no"
        reason = "tabla procesada contiene registros seed"
    else:
        apto = "requiere_validacion"
        reason = "requiere revisar contrato, fuente y cobertura antes de dashboard"

    sources = "No disponible"
    if "id_fuente" in df.columns and not df.empty:
        sources = " | ".join(sorted({value for value in df["id_fuente"].astype(str) if value}))
    elif "fuentes_utilizadas" in df.columns and not df.empty:
        sources = " | ".join(sorted({value for value in df["fuentes_utilizadas"].astype(str) if value}))

    return {
        "archivo": name,
        "capa": layer,
        "filas": rows,
        "columnas": columns,
        "origen_detectado": origin,
        "apto_dashboard": apto,
        "motivo": reason,
        "fuentes_utilizadas": sources,
        "fecha_consulta": TODAY,
        "requiere_accion": "si" if apto != "si" else "no",
    }


def collect_rows() -> list[dict]:
    rows = []
    for layer, folder in (
        ("raw", DATA_RAW),
        ("seeds", DATA_SEEDS),
        ("processed", DATA_PROCESSED),
        ("analytics", DATA_ANALYTICS),
    ):
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.csv")):
            rows.append(classify_file(path, layer, read_csv(path)))
    return rows


def write_markdown(rows: list[dict]) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    lines = [
        "# Auditoria de datos reales vs seed",
        "",
        f"Generado: {TODAY}",
        "",
        "Regla V3: ninguna salida de dashboard debe presentarse como dato real si deriva de seeds/manuales.",
        "",
        "## Decision de estructura",
        "",
        "Se eligio la opcion A: `data/raw/` queda reservado para datos reales descargados y `data/seeds/` contiene fallback de desarrollo.",
        "",
    ]
    for layer in ("raw", "seeds", "processed", "analytics"):
        subset = df[df["capa"] == layer]
        lines.extend([f"## {layer}", ""])
        if subset.empty:
            lines.extend(["No hay archivos.", ""])
            continue
        for _, row in subset.iterrows():
            lines.extend(
                [
                    f"### {row['archivo']}",
                    "",
                    f"- Filas x columnas: {row['filas']} x {row['columnas']}",
                    f"- Origen detectado: {row['origen_detectado']}",
                    f"- Apto dashboard: {row['apto_dashboard']}",
                    f"- Motivo: {row['motivo']}",
                    f"- Fuentes: {row['fuentes_utilizadas']}",
                    f"- Riesgo de decision: {'alto' if row['apto_dashboard'] != 'si' else 'bajo/normal'}",
                    f"- Recomendacion: {'cargar fuente real o validar cobertura antes de usar' if row['apto_dashboard'] != 'si' else 'puede usarse citando fuentes y fecha'}",
                    "",
                ]
            )
    lines.extend(
        [
            "## Resumen dashboard",
            "",
            "- Apto hoy: ninguna tabla analytics importante es apta para dashboard real mientras F01/F02/F03 usen seeds o falten.",
            "- No apto hoy: resumen general, establecimientos por barrio/comuna, eventos, ferias/mercados y mapa de oportunidades.",
        ]
    )
    (DOCS / "AUDITORIA_DATOS_REALES.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = collect_rows()
    PROFILE_OUTPUTS.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(PROFILE_OUTPUTS / "auditoria_datos_reales.csv", index=False, encoding="utf-8")
    write_markdown(rows)
    print(f"OK auditoria: {PROFILE_OUTPUTS / 'auditoria_datos_reales.csv'}")
    print(f"OK docs: {DOCS / 'AUDITORIA_DATOS_REALES.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
