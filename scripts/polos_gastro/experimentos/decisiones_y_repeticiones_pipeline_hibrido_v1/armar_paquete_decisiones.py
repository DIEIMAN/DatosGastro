# -*- coding: utf-8 -*-
"""Arma el PAQUETE_DECISIONES_DIEGO del experimento decisiones_y_repeticiones_pipeline_hibrido_v1.

Solo lectura sobre insumos; escribe únicamente dentro de las carpetas nuevas del
experimento. Sin APIs, sin descargas, sin git.

Fases:
  --fase empaquetar : verifica hashes de insumos críticos v1, QA de privacidad,
                      copia docs/CSVs/mapas al paquete, escribe metadata y ZIP.
  --fase manifest   : regenera MANIFEST_ARCHIVOS.md con todos los archivos nuevos.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "docs/polos_gastro/experimentos/decisiones_y_repeticiones_pipeline_hibrido_v1"
OUT = ROOT / "outputs/polos_gastro/experimentos/decisiones_y_repeticiones_pipeline_hibrido_v1"
PKG = OUT / "PAQUETE_DECISIONES_DIEGO"
SCRIPTS = ROOT / "scripts/polos_gastro/experimentos/decisiones_y_repeticiones_pipeline_hibrido_v1"
V1_OUT = ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1"
V1_MANIFEST = ROOT / "docs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/MANIFEST_ARCHIVOS.md"

DOCS_A_PAQUETE = [
    "REVISION_CRITICA_PROTOTIPOS_HIBRIDOS.md",
    "MATRIZ_DECISIONES_HUMANAS_AMPLIADA.md",
    "ESPECIFICACION_REPETICION_BELGRANO.md",
    "ESPECIFICACION_REPETICION_PUERTO_MADERO.md",
    "PLAN_CONSULTAS_QUIRURGICAS_PLACES_FUTURAS.md",
    "MATRIZ_ESCALADO_INMEDIATO.md",
]
CSVS_A_PAQUETE = [
    "tabla_plan_pruebas_belgrano.csv",
    "tabla_plan_pruebas_puerto_madero.csv",
    "inventario_ejes_viales_puerto_madero.csv",
]
MAPAS_V1 = [
    "comparativa_san_telmo_actual_vs_hibrido.png",
    "comparativa_corrientes_actual_vs_hibrido.png",
    "comparativa_belgrano_actual_vs_hibrido.png",
    "comparativa_puerto_madero_actual_vs_hibrido.png",
    "comparativa_costanera_actual_vs_hibrido.png",
    "mapa_resumen_cinco_prototipos.png",
]
# Insumos críticos v1 usados en esta tanda (se verifican contra el manifest v1).
INSUMOS_CRITICOS = [
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/metadata_pipeline_hibrido_v1.json",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/metricas_estabilidad_desagregadas_v1.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/mezcla_fuentes_representaciones_v1.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/robustez_bootstrap_bloques_v1.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/robustez_ablacion_fuentes_v1.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/robustez_bordes_v1.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/belgrano_comparacion_comunidades.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/san_telmo_comparacion_metodos.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/corrientes_perfil_longitudinal.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/puerto_madero_perfil_frente.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/tabla_comparacion_prototipos_hibridos_v1.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/diagnostico_places_por_zona_corregido.csv",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/san_telmo_nucleo_candidato.geojson",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/belgrano_nucleos_candidatos.geojson",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/corrientes_eje_candidato.geojson",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/puerto_madero_frentes_candidatos.geojson",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/costanera_concentraciones_exploratorias.geojson",
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/inventario_capas_urbanas_locales.csv",
] + ["outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/mapas/" + m for m in MAPAS_V1]

# Errata preexistente del empaquetado v1: el manifest v1 registró una versión anterior
# (1573 bytes) de metadata_pipeline_hibrido_v1.json; las tres copias actuales (suelta,
# carpeta del paquete y ZIP v1, este último intacto) son byte-idénticas entre sí con el
# hash de abajo. No es un cambio de esta tanda; ver QA_FINAL_DECISIONES_Y_REPETICIONES.md.
ERRATAS_PREEXISTENTES_V1 = {
    "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/metadata_pipeline_hibrido_v1.json":
        "2a453994653c77b223d656c56c5f33df818dd926594e886108f8c4d34933c8f3",
}

# Patrones de datos sensibles que no deben aparecer en los entregables.
PATRONES_PRIVACIDAD = {
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+"),
    "cuit": re.compile(r"\b(20|23|24|27|30|33|34)-?\d{8}-?\d\b"),
    "telefono": re.compile(r"\b(?:\+54|011|15)[\s-]?\d{4}[\s-]?\d{4}\b"),
    "api_key": re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hashes_manifest_v1() -> dict:
    esperados = {}
    for line in V1_MANIFEST.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| `([^`]+)` \| \d+ \| `([0-9a-f]{64})` \|", line.replace(" ", " "))
        if not m:
            m = re.match(r"\| `([^`]+)` \| [\d.,]+ \| `([0-9a-f]{64})` \|", line)
        if m:
            esperados[m.group(1)] = m.group(2)
    return esperados


def verificar_insumos() -> list:
    esperados = hashes_manifest_v1()
    filas = []
    for rel in INSUMOS_CRITICOS:
        p = ROOT / rel
        actual = sha256(p)
        esperado = esperados.get(rel)
        if esperado is None:
            estado = "SIN_REFERENCIA"
        elif actual == esperado:
            estado = "OK"
        elif ERRATAS_PREEXISTENTES_V1.get(rel) == actual:
            estado = "DISCREPANCIA_PREEXISTENTE_V1"
        else:
            estado = "CAMBIADO"
        filas.append({"ruta": rel, "sha256_actual": actual, "sha256_manifest_v1": esperado or "", "estado": estado})
    return filas


def qa_privacidad(paths) -> list:
    hallazgos = []
    for p in paths:
        if p.suffix.lower() not in {".md", ".csv", ".json"}:
            continue
        texto = p.read_text(encoding="utf-8", errors="replace")
        for nombre, pat in PATRONES_PRIVACIDAD.items():
            for m in pat.finditer(texto):
                hallazgos.append({"archivo": str(p.relative_to(ROOT)), "tipo": nombre, "muestra": m.group(0)[:40]})
    return hallazgos


def archivos_nuevos() -> list:
    files = []
    for base in (DOCS, OUT, SCRIPTS):
        for p in sorted(base.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                files.append(p)
    return files


def fase_empaquetar():
    PKG.mkdir(parents=True, exist_ok=True)
    (PKG / "mapas").mkdir(exist_ok=True)

    filas = verificar_insumos()
    cambiados = [f for f in filas if f["estado"] == "CAMBIADO"]
    sin_ref = [f for f in filas if f["estado"] == "SIN_REFERENCIA"]
    erratas = [f for f in filas if f["estado"] == "DISCREPANCIA_PREEXISTENTE_V1"]
    if erratas:
        for f in erratas:
            print("  DISCREPANCIA_PREEXISTENTE_V1 (documentada, no es cambio de esta tanda):", f["ruta"])
    import csv as _csv
    with open(OUT / "verificacion_hashes_insumos_v1.csv", "w", newline="", encoding="utf-8") as fh:
        w = _csv.DictWriter(fh, fieldnames=["ruta", "sha256_actual", "sha256_manifest_v1", "estado"])
        w.writeheader()
        w.writerows(filas)
    print(f"[hashes] insumos={len(filas)} ok={len(filas)-len(cambiados)-len(sin_ref)} "
          f"cambiados={len(cambiados)} sin_referencia={len(sin_ref)}")
    if cambiados:
        for f in cambiados:
            print("  CAMBIADO:", f["ruta"])
        sys.exit("ABORTADO: insumos críticos v1 cambiaron; revisar antes de empaquetar.")

    for name in DOCS_A_PAQUETE:
        shutil.copy2(DOCS / name, PKG / name)
    for name in CSVS_A_PAQUETE:
        shutil.copy2(OUT / name, PKG / name)
    for name in MAPAS_V1:
        shutil.copy2(V1_OUT / "mapas" / name, PKG / "mapas" / name)
    print(f"[copias] docs={len(DOCS_A_PAQUETE)} csvs={len(CSVS_A_PAQUETE)} mapas={len(MAPAS_V1)}")

    textos = [p for p in PKG.rglob("*") if p.is_file()] + [DOCS / d for d in DOCS_A_PAQUETE]
    hallazgos = qa_privacidad(textos)
    if hallazgos:
        for h in hallazgos:
            print("  PRIVACIDAD:", h)
        sys.exit("ABORTADO: posibles datos sensibles en entregables.")
    print("[privacidad] limpio: sin emails, CUIT/DNI, teléfonos ni API keys en el paquete")

    metadata = {
        "experimento": "decisiones_y_repeticiones_pipeline_hibrido_v1",
        "estado": "EXPERIMENTAL_NO_OFICIAL",
        "fecha_corte": str(date.today()),
        "insumo": "pipeline_hibrido_tipo_territorial_v1 (REVISION_PROTOTIPOS_HIBRIDOS_V1)",
        "veredicto_vigente": "PIPELINE_HIBRIDO_POR_TIPO_TERRITORIAL",
        "recomendacion_vigente": "ESCALAR_CON_AJUSTES",
        "sin_api": True,
        "sin_google_places": True,
        "sin_descargas": True,
        "sin_cambios_fase25_fase26_v1_v42_prototipos": True,
        "sin_git_add_commit_push": True,
        "hashes_insumos_criticos": {
            "verificados": len(filas),
            "ok": len([f for f in filas if f["estado"] == "OK"]),
            "cambiados": len(cambiados),
            "discrepancias_preexistentes_v1_documentadas": len(erratas),
            "sin_referencia_en_manifest_v1": len(sin_ref),
            "detalle": "verificacion_hashes_insumos_v1.csv",
        },
        "decisiones": {
            "con_recomendacion_suficiente": ["DH-02", "DH-03", "DH-04", "DH-07", "DH-08", "DH-09", "DH-12"],
            "requieren_prueba_local_previa": ["DH-01", "DH-05", "DH-06", "DH-11"],
            "se_activan_despues": ["DH-10"],
        },
        "repeticiones_disenadas_no_ejecutadas": ["Belgrano (BEL-R01..R15)", "Puerto Madero (PM-R01..R12)"],
        "consultas_places": {"autorizadas": 0, "recomendadas_ejecutar": 0,
                             "en_espera": ["QP-01", "QP-02", "QP-03", "QP-04"],
                             "no_ejecutar": ["QP-05", "QP-06", "QP-07"]},
    }
    with open(OUT / "metadata_decisiones_y_repeticiones.json", "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, ensure_ascii=False, indent=2)
    print("[metadata] escrito")

    zip_path = OUT / "PAQUETE_DECISIONES_DIEGO.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(PKG.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(PKG.parent))
    print(f"[zip] {zip_path.relative_to(ROOT)} ({zip_path.stat().st_size:,} bytes)")


def fase_manifest():
    lineas = ["# Manifest de archivos — decisiones_y_repeticiones_pipeline_hibrido_v1", "",
              "Estado: EXPERIMENTAL / NO OFICIAL. Generado por `armar_paquete_decisiones.py`.", "",
              "| Ruta | Bytes | SHA-256 |", "| --- | ---: | --- |"]
    manifest_path = DOCS / "MANIFEST_ARCHIVOS.md"
    n = 0
    for p in archivos_nuevos():
        rel = p.relative_to(ROOT).as_posix()
        if p == manifest_path:
            lineas.append(f"| `{rel}` | — | (este archivo) |")
            continue
        lineas.append(f"| `{rel}` | {p.stat().st_size} | `{sha256(p)}` |")
        n += 1
    manifest_path.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"[manifest] {n} archivos listados en {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fase", choices=["empaquetar", "manifest"], required=True)
    args = ap.parse_args()
    if args.fase == "empaquetar":
        fase_empaquetar()
    else:
        fase_manifest()
