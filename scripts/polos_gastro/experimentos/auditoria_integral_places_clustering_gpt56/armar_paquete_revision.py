# -*- coding: utf-8 -*-
"""Arma el paquete sanitizado de revisión de la auditoría y su ZIP."""
from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/polos_gastro/historico/experimentos/auditoria_integral_places_clustering_gpt56"
DOC = ROOT / "docs/polos_gastro/historico/experimentos/auditoria_integral_places_clustering_gpt56"
PACK = OUT / "REVISION_AUDITORIA_GPT56"
ZIP = OUT / "REVISION_AUDITORIA_GPT56.zip"

DOCS = [
    "AUDITORIA_INTEGRAL_PLACES_CLUSTERING_GPT56.md",
    "RESUMEN_EJECUTIVO_AUDITORIA_GPT56.md",
    "INVENTARIO_TRAZABILIDAD_AUDITORIA.md",
    "AUDITORIA_APORTE_GOOGLE_PLACES.md",
    "AUDITORIA_DEDUPLICACION.md",
    "AUDITORIA_CLUSTERING_ACTUAL.md",
    "RESUMEN_ESTABILIDAD_CLUSTERING.md",
    "COMPARACION_FASE25_VS_PIPELINE_NUEVO.md",
    "MATRIZ_DECISIONES_DIEGO_DGDGAS.md",
    "PLAN_RECOMENDADO_POST_AUDITORIA.md",
]

TABLES = [
    "diagnostico_places_por_zona.csv",
    "muestra_casos_deduplicacion_revision.csv",
    "sensibilidad_umbral_deduplicacion.csv",
    "metricas_robustez_por_zona.csv",
    "sensibilidad_hdbscan_detalle.csv",
    "diagnostico_subdivision_kmeans.csv",
    "prueba_controlada_optics.csv",
    "MATRIZ_COMPARATIVA_METODOS.csv",
    "DIAGNOSTICO_METODOLOGICO_POR_ZONA.csv",
    "comparacion_por_zona_fase25_nuevo.csv",
    "trazabilidad_163_41_31.csv",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if PACK.exists() or ZIP.exists():
        raise SystemExit("El paquete o el ZIP ya existen; no se sobrescriben ni borran automáticamente.")
    for sub in (PACK / "documentos", PACK / "tablas", PACK / "graficos"):
        sub.mkdir(parents=True, exist_ok=True)
    for name in DOCS:
        shutil.copy2(DOC / name, PACK / "documentos" / name)
    for name in TABLES:
        shutil.copy2(OUT / name, PACK / "tablas" / name)
    for path in sorted((OUT / "graficos").glob("*.png")):
        shutil.copy2(path, PACK / "graficos" / path.name)

    readme = """# Revisión de auditoría GPT56\n\nPaquete experimental y sanitizado para revisión metodológica interna.\n\nOrden sugerido:\n\n1. `documentos/RESUMEN_EJECUTIVO_AUDITORIA_GPT56.md`\n2. `documentos/AUDITORIA_INTEGRAL_PLACES_CLUSTERING_GPT56.md`\n3. `documentos/MATRIZ_DECISIONES_DIEGO_DGDGAS.md`\n4. `tablas/DIAGNOSTICO_METODOLOGICO_POR_ZONA.csv`\n5. `tablas/metricas_robustez_por_zona.csv`\n\nNo contiene datos fuente, resultados crudos, identificadores privados, credenciales ni información personal. No es un informe oficial ni una delimitación institucional.\n"""
    note = """# Nota para ChatGPT / Claude\n\nRevisar críticamente el veredicto `PIPELINE_HIBRIDO_POR_TIPO_TERRITORIAL`. No asumir que polígonos o nombres son correctos. Separar hechos, inferencias, hipótesis y recomendaciones. No pedir ni reconstruir datos individuales. No llamar APIs. El foco de la revisión debe estar en: dependencia por fuente, estabilidad, efecto de KMeans, representación por tipo territorial y decisiones humanas pendientes.\n"""
    (PACK / "README.md").write_text(readme, encoding="utf-8")
    (PACK / "NOTA_PARA_CHATGPT_CLAUDE.md").write_text(note, encoding="utf-8")

    files = sorted(p for p in PACK.rglob("*") if p.is_file())
    manifest = ["# Manifest de archivos", "", f"Cantidad: {len(files) + 1}", "", "| Ruta | Bytes | SHA-256 |", "| --- | ---: | --- |"]
    for p in files:
        rel = p.relative_to(PACK).as_posix()
        manifest.append(f"| `{rel}` | {p.stat().st_size} | `{digest(p)}` |")
    (PACK / "MANIFEST.md").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(PACK.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(PACK.parent).as_posix())
    print(f"pack={PACK}")
    print(f"zip={ZIP} bytes={ZIP.stat().st_size}")
    print(f"files={sum(1 for p in PACK.rglob('*') if p.is_file())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
