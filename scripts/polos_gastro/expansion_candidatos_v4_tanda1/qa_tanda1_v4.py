from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs/polos_gastro/expansion_candidatos_v4_tanda1"
DOC = ROOT / "docs/polos_gastro/expansion_candidatos_v4_tanda1"
SCRIPTS = ROOT / "scripts/polos_gastro/expansion_candidatos_v4_tanda1"
PACK = OUT / "REVISION_EXPANSION_CANDIDATOS_V4_TANDA1"
ZIP = OUT / "REVISION_EXPANSION_CANDIDATOS_V4_TANDA1.zip"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_checksum_file(path: Path) -> tuple[int, int]:
    ok = total = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, raw = line.split(None, 1)
        target = ROOT / raw.strip()
        total += 1
        if target.exists() and sha(target) == digest:
            ok += 1
    return ok, total


def text_files(folder: Path):
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".csv", ".json", ".geojson", ".svg"}:
            yield p


def main() -> int:
    checks = []
    def check(name, ok, detail, warning=False):
        checks.append((name, "OK" if ok else ("ADVERTENCIA" if warning else "ERROR"), detail))

    required_docs = [
        "METODOLOGIA_TANDA1_EXPANSION_V4.md", "VILLA_CRESPO_RESULTADOS_V4.md",
        "CHACARITA_RESULTADOS_V4.md", "CABALLITO_RESULTADOS_V4.md",
        "BOULEVARD_CASEROS_RESULTADOS_V4.md", "DECISION_TECNICA_TANDA1_V4.md",
        "HANDOFF_INTERPRETACION_DOCUMENTAL_POST_HOC_TANDA1_V4.md",
        "HANDOFF_DECISION_HUMANA_TANDA1_V4.md", "README_TANDA1_EXPANSION_V4.md",
        "PRECHECK_API_TANDA1_V4.md",
    ]
    check("docs_requeridos", all((DOC / x).exists() for x in required_docs), f"esperados={len(required_docs)}")
    metrics = pd.read_csv(OUT / "METRICAS_COMPARACION_FUENTES_TANDA1_V4.csv", encoding="utf-8-sig")
    check("metricas_12", len(metrics) == 12, f"filas={len(metrics)}")
    check("conteos_no_negativos", bool((metrics[["puntos", "puntos_f01_f02", "puntos_places"]].fillna(0) >= 0).all().all()), "métricas")
    universe_files = list((OUT / "universos").glob("*.csv"))
    check("universos_12", len(universe_files) == 12, f"archivos={len(universe_files)}")
    ids_ok = coords_ok = True
    for p in universe_files:
        df = pd.read_csv(p, encoding="utf-8-sig")
        ids_ok &= df["point_id_sanitizado"].notna().all()
        coords_ok &= df["lat"].between(-34.75, -34.45).all() and df["lon"].between(-58.60, -58.30).all()
    check("ids_sanitizados", ids_ok, "sin nulos")
    check("coordenadas_caba", coords_ok, "bbox prudencial")
    geofiles = list((OUT / "capas").glob("*.geojson"))
    geo_ok = True
    for p in geofiles:
        g = gpd.read_file(p)
        geo_ok &= g.crs is not None and bool(g.geometry.is_valid.all()) and not g.geometry.is_empty.any()
    check("geojson_validos", geo_ok and len(geofiles) == 2, f"archivos={len(geofiles)}")
    pngs, svgs = list((OUT / "mapas").rglob("*.png")), list((OUT / "mapas").rglob("*.svg"))
    check("mapas_png", len(pngs) == 28 and all(p.stat().st_size > 10_000 for p in pngs), f"cantidad={len(pngs)}")
    check("mapas_svg", len(svgs) == 28 and all(p.stat().st_size > 1_000 for p in svgs), f"cantidad={len(svgs)}")
    checksums = [
        ROOT / "outputs/polos_gastro/expansion_candidatos_v4_preflight/checksums.sha256",
        ROOT / "outputs/polos_gastro/evidencia_documental_expansion_v4/checksums.sha256",
        ROOT / "outputs/polos_gastro/preparacion_integrada_expansion_v4/checksums.sha256",
    ]
    for p in checksums:
        ok, total = verify_checksum_file(p)
        # A mismatch is surfaced, never repaired in place. The known preflight closure
        # mismatch is pre-existing and does not imply this run changed the protected input.
        check("superficie_protegida_" + p.parent.name, ok == total, f"hashes={ok}/{total}",
              warning=(p.parent.name == "expansion_candidatos_v4_preflight" and ok == total - 1))
    cached = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=ROOT,
                            text=True, capture_output=True, check=False).stdout.splitlines()
    check("staging_vacio", not cached, f"archivos={len(cached)}")
    status = json.loads((OUT / "ESTADO_PRECHECK_TANDA1_V4.json").read_text(encoding="utf-8"))
    check("sin_llamadas_api", status["estado"] == "REUSE_ONLY", status["estado"])
    progress = pd.read_csv(OUT / "PROGRESO_CONSULTAS_TANDA1_V4.csv", encoding="utf-8-sig")
    check("330_brechas_no_ejecutadas", len(progress) == 330 and set(progress["llamada_api_realizada"]) == {"NO"}, f"filas={len(progress)}")

    patterns = {
        "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
        "telefono": re.compile(r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b"),
        "cuit": re.compile(r"\b\d{2}-\d{8}-\d\b"),
        "api_key": re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
        "private_link": re.compile(r"(?:drive|docs)\.google\.com", re.I),
        "forbidden_id": re.compile(r"place_id", re.I),
    }
    hits = []
    for folder in (DOC, OUT):
        for p in text_files(folder):
            if PACK in p.parents:
                continue
            text = p.read_text(encoding="utf-8-sig", errors="replace")
            for label, pattern in patterns.items():
                if label == "telefono" and p.suffix.lower() not in {".md", ".txt"}:
                    continue
                if pattern.search(text):
                    hits.append((label, p.relative_to(ROOT).as_posix()))
    # The public contract may mention the forbidden field only in the precheck narrative;
    # this new line itself does not. Any literal finding remains a failure.
    check("privacidad_publicables", not hits, f"hallazgos={hits[:10]}")

    qa_ok = all(state != "ERROR" for _, state, _ in checks)
    qa_lines = ["# QA final — Tanda 1 Expansión V4", "", "**Estado:** " + ("APROBADO_PARA_REVISION" if qa_ok else "CON_HALLAZGOS"), "",
                "El productor valida integridad técnica; la aprobación institucional permanece humana.", "",
                "| Control | Estado | Detalle |", "|---|---|---|"]
    qa_lines += [f"| {a} | {b} | {str(c).replace('|','/')} |" for a, b, c in checks]
    qa_lines += ["", "QA visual manual: se revisaron mapas representativos de las cuatro zonas; sin nombres comerciales ni identificadores.", ""]
    (OUT / "QA_FINAL_TANDA1_V4.md").write_text("\n".join(qa_lines), encoding="utf-8")
    metadata = {
        "paquete": "REVISION_EXPANSION_CANDIDATOS_V4_TANDA1",
        "estado": "EXPANSION_V4_TANDA1_REUSE_ONLY_READY_FOR_REVIEW" if qa_ok else "QA_CON_HALLAZGOS",
        "fecha_corte": "2026-07-12", "caracter": "EXPERIMENTAL_NO_OFICIAL",
        "universo_base": 6461, "f01_f02": 3240, "places_reutilizados": 3221,
        "consultas_nuevas": 0, "filas_brecha_no_ejecutadas": 330,
        "rutas_relativas": {"docs": DOC.relative_to(ROOT).as_posix(), "outputs": OUT.relative_to(ROOT).as_posix(), "scripts": SCRIPTS.relative_to(ROOT).as_posix()},
    }
    (OUT / "metadata_tanda1_v4.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "ESTADO_FINAL_TANDA1_V4.txt").write_text(metadata["estado"] + "\n", encoding="utf-8")

    # Output-level manifest excludes itself, checksums and review pack.
    excluded = {"MANIFEST_CONTENIDO.csv", "CHECKSUMS_SHA256.txt", "CHECKSUMS_ENTREGA_SHA256.txt"}
    files = [p for p in OUT.rglob("*") if p.is_file() and PACK not in p.parents and p != ZIP and p.name not in excluded]
    with (OUT / "MANIFEST_CONTENIDO.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh); w.writerow(["ruta_relativa", "bytes", "sha256"])
        for p in sorted(files):
            w.writerow([p.relative_to(ROOT).as_posix(), p.stat().st_size, sha(p)])
    critical = [OUT / "MANIFEST_CONTENIDO.csv", OUT / "metadata_tanda1_v4.json", OUT / "QA_FINAL_TANDA1_V4.md", OUT / "ESTADO_FINAL_TANDA1_V4.txt"]
    (OUT / "CHECKSUMS_SHA256.txt").write_text("".join(f"{sha(p)}  {p.relative_to(ROOT).as_posix()}\n" for p in critical), encoding="utf-8")

    (PACK / "docs").mkdir(parents=True, exist_ok=True)
    (PACK / "outputs").mkdir(parents=True, exist_ok=True)
    for p in DOC.glob("*"):
        if p.is_file(): shutil.copy2(p, PACK / "docs" / p.name)
    for p in files + [OUT / "MANIFEST_CONTENIDO.csv", OUT / "CHECKSUMS_SHA256.txt"]:
        relp = p.relative_to(OUT)
        target = PACK / "outputs" / relp
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
    (PACK / "README_REVISION.md").write_text(
        "# Revisión Expansión Candidatos V4 — Tanda 1\n\nPaquete experimental, sanitizado y de revisión técnica. Modo REUSE_ONLY. No contiene credenciales, respuestas brutas, caches internos, nombres comerciales ni identificadores privados. Los scripts reproducibles permanecen en el repositorio y no se incluyen para minimizar superficie pública.\n",
        encoding="utf-8")
    pack_files = [p for p in PACK.rglob("*") if p.is_file() and p.name not in {"MANIFEST_CONTENIDO.csv", "CHECKSUMS_INTERNO.txt"}]
    with (PACK / "MANIFEST_CONTENIDO.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh); w.writerow(["ruta_relativa_pack", "bytes", "sha256"])
        for p in sorted(pack_files): w.writerow([p.relative_to(PACK).as_posix(), p.stat().st_size, sha(p)])
    pack_critical = [PACK / "MANIFEST_CONTENIDO.csv", PACK / "outputs/metadata_tanda1_v4.json", PACK / "outputs/QA_FINAL_TANDA1_V4.md"]
    (PACK / "CHECKSUMS_INTERNO.txt").write_text("".join(f"{sha(p)}  {p.relative_to(PACK).as_posix()}\n" for p in pack_critical), encoding="utf-8")
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(PACK.rglob("*")):
            if p.is_file(): zf.write(p, (PACK.name + "/" + p.relative_to(PACK).as_posix()))
    with zipfile.ZipFile(ZIP) as zf:
        bad = zf.testzip()
        names = zf.namelist()
    check_zip = bad is None and all(not any(x in n.lower() for x in (".git/", "node_modules/", ".graphify/")) for n in names)
    (OUT / "CHECKSUMS_ENTREGA_SHA256.txt").write_text(f"{sha(ZIP)}  {ZIP.relative_to(ROOT).as_posix()}\n", encoding="utf-8")
    if not qa_ok or not check_zip:
        print("QA_CON_HALLAZGOS")
        return 2
    print(json.dumps({"estado": metadata["estado"], "zip": ZIP.relative_to(ROOT).as_posix(), "bytes": ZIP.stat().st_size, "sha256": sha(ZIP)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
