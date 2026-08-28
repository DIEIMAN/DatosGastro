"""Arma el paquete publico de revision del piloto hibrido territorial v1.

El empaquetado usa una lista cerrada, falla si el destino ya existe y excluye
por construccion la muestra interna de deduplicacion.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1"
DOC = ROOT / "docs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1"
PACK = OUT / "REVISION_PROTOTIPOS_HIBRIDOS_V1"
ZIP = OUT / "REVISION_PROTOTIPOS_HIBRIDOS_V1.zip"
QA = OUT / "qa_paquete_revision.json"

DOCS = [
    "FE_DE_ERRATAS_AUDITORIA_GPT56.md",
    "DIAGNOSTICO_SAN_TELMO.md",
    "DIAGNOSTICO_CORRIENTES.md",
    "DIAGNOSTICO_BELGRANO.md",
    "DIAGNOSTICO_PUERTO_MADERO.md",
    "DIAGNOSTICO_COSTANERA.md",
    "COMPARACION_PROTOTIPOS_HIBRIDOS_V1.md",
    "MATRIZ_DECISIONES_POST_PROTOTIPO.md",
    "PLAN_ESCALADO_PIPELINE_HIBRIDO.md",
    "GUIA_REVISION_DEDUPLICACION.md",
    "QA_FINAL_PIPELINE_HIBRIDO_V1.md",
    "MANIFEST_ARCHIVOS.md",
]

OUTPUTS = [
    "diagnostico_places_por_zona_corregido.csv",
    "inventario_capas_urbanas_locales.csv",
    "metricas_estabilidad_desagregadas_v1.csv",
    "san_telmo_comparacion_metodos.csv",
    "san_telmo_nucleo_candidato.geojson",
    "corrientes_perfil_longitudinal.csv",
    "corrientes_eje_candidato.geojson",
    "corrientes_buffer_candidato.geojson",
    "belgrano_comparacion_comunidades.csv",
    "belgrano_nucleos_candidatos.geojson",
    "puerto_madero_perfil_frente.csv",
    "puerto_madero_frentes_candidatos.geojson",
    "costanera_concentraciones_exploratorias.geojson",
    "robustez_ablacion_fuentes_v1.csv",
    "robustez_bootstrap_bloques_v1.csv",
    "robustez_bordes_v1.csv",
    "mezcla_fuentes_representaciones_v1.csv",
    "tabla_comparacion_prototipos_hibridos_v1.csv",
    "metadata_pipeline_hibrido_v1.json",
    "mapas/comparativa_belgrano_actual_vs_hibrido.png",
    "mapas/comparativa_corrientes_actual_vs_hibrido.png",
    "mapas/comparativa_costanera_actual_vs_hibrido.png",
    "mapas/comparativa_puerto_madero_actual_vs_hibrido.png",
    "mapas/comparativa_san_telmo_actual_vs_hibrido.png",
    "mapas/mapa_belgrano_prototipo_multinuclear.png",
    "mapas/mapa_corrientes_prototipo_corredor.png",
    "mapas/mapa_costanera_senal_exploratoria.png",
    "mapas/mapa_puerto_madero_prototipo_frente.png",
    "mapas/mapa_resumen_cinco_prototipos.png",
    "mapas/mapa_san_telmo_prototipo_hibrido.png",
]

README = """# Revisión — prototipos híbridos territoriales v1

Paquete público de revisión técnica del piloto experimental de Polos Gastronómicos.

## Alcance

- Cinco prototipos: San Telmo, Corrientes, Belgrano, Puerto Madero y Costanera.
- Corrección trazable de inconsistencias de la auditoría anterior.
- Comparación de métodos, robustez, mapas y plan de escalado.
- Trabajo completamente offline con insumos locales preexistentes.

## Advertencias

- EXPERIMENTAL / NO OFICIAL.
- No constituye una delimitación oficial ni un ranking de zonas.
- No es Fase 25 ni Fase 26 y no modifica sus productos.
- Los resultados requieren decisiones humanas y, en dos casos, repetición del prototipo.
- La muestra de deduplicación es interna y fue excluida deliberadamente de este paquete.

Comenzar por `docs/COMPARACION_PROTOTIPOS_HIBRIDOS_V1.md`, continuar con
`docs/MATRIZ_DECISIONES_POST_PROTOTIPO.md` y revisar luego los diagnósticos por zona.
"""

REVIEW_NOTE = """# Nota para revisión con ChatGPT o Claude

Revisar este paquete como una auditoría metodológica conservadora. No asumir que las
geometrías son delimitaciones oficiales. Contrastar cada conclusión con los CSV,
GeoJSON y mapas incluidos; separar mejora de forma, estabilidad estadística y
representatividad de fuentes.

Preguntas sugeridas:

1. ¿La fe de erratas separa correctamente resultados HDBSCAN y posprocesamiento?
2. ¿La evidencia respalda escalar San Telmo y Corrientes con ajustes?
3. ¿Belgrano y Puerto Madero deben repetirse antes de escalar?
4. ¿Costanera está correctamente limitada a señal exploratoria/anexo?
5. ¿Qué decisiones humanas siguen abiertas y qué evidencia adicional exigirían?

No inferir identidades de establecimientos ni solicitar datos internos. La muestra
manual de deduplicación no integra este paquete.
"""

TEXT_PATTERNS = {
    "email": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
    "api_key_google": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    "link_privado": re.compile(r"https?://[^\s)\]]*(?:drive\.google|docs\.google|sharepoint|localhost|127\.0\.0\.1)", re.I),
    "cuit_dni_rotulado": re.compile(r"\b(?:CUIT|DNI)\s*[:=]?\s*\d", re.I),
}
FORBIDDEN_PARTS = {"interno_revision_deduplicacion", "raw", ".env"}
FORBIDDEN_HEADERS = {
    "nombre", "nombre_original", "razon_social", "direccion", "domicilio",
    "telefono", "email", "cuit", "dni", "place_id", "google_place_id", "lat", "lon",
    "latitude", "longitude",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_sources() -> list[tuple[Path, str]]:
    entries = [(DOC / name, f"docs/{name}") for name in DOCS]
    entries += [(OUT / name, f"resultados/{name}") for name in OUTPUTS]
    missing = [str(source) for source, _ in entries if not source.is_file()]
    if missing:
        raise FileNotFoundError("Faltan archivos permitidos:\n" + "\n".join(missing))
    return entries


def privacy_scan(base: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        rel = path.relative_to(base).as_posix()
        lower_parts = {part.lower() for part in path.relative_to(base).parts}
        if lower_parts & FORBIDDEN_PARTS:
            findings.append({"archivo": rel, "tipo": "ruta_prohibida"})
        if path.suffix.lower() not in {".md", ".csv", ".json", ".geojson", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in TEXT_PATTERNS.items():
            if pattern.search(text):
                findings.append({"archivo": rel, "tipo": label})
        if path.suffix.lower() == ".csv":
            rows = csv.reader(text.splitlines())
            header = next(rows, [])
            forbidden = sorted({str(value).strip().lower() for value in header} & FORBIDDEN_HEADERS)
            if forbidden:
                findings.append({"archivo": rel, "tipo": "columnas_prohibidas:" + ",".join(forbidden)})
    return findings


def main() -> None:
    if PACK.exists() or ZIP.exists() or QA.exists():
        raise FileExistsError("El paquete, ZIP o QA ya existe; no se sobrescribe.")

    entries = validate_sources()
    PACK.mkdir(parents=False)
    try:
        for source, relative in entries:
            destination = PACK / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        (PACK / "README.md").write_text(README, encoding="utf-8")
        (PACK / "NOTA_REVISION_CHATGPT_CLAUDE.md").write_text(REVIEW_NOTE, encoding="utf-8")

        findings = privacy_scan(PACK)
        if findings:
            raise RuntimeError("El control de privacidad impide empaquetar: " + json.dumps(findings, ensure_ascii=False))

        files = sorted(p for p in PACK.rglob("*") if p.is_file())
        manifest = [
            {
                "archivo": path.relative_to(PACK).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        ]
        (PACK / "MANIFEST_PAQUETE.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        with zipfile.ZipFile(ZIP, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(p for p in PACK.rglob("*") if p.is_file()):
                archive.write(path, (Path(PACK.name) / path.relative_to(PACK)).as_posix())

        with zipfile.ZipFile(ZIP) as archive:
            bad_member = archive.testzip()
            zip_names = archive.namelist()
        if bad_member:
            raise RuntimeError(f"ZIP corrupto en {bad_member}")
        forbidden_zip = [
            name for name in zip_names
            if any(part.lower() in FORBIDDEN_PARTS for part in Path(name).parts)
        ]
        if forbidden_zip:
            raise RuntimeError("El ZIP contiene rutas prohibidas: " + repr(forbidden_zip))

        qa = {
            "generado_utc": datetime.now(timezone.utc).isoformat(),
            "estado": "APROBADO",
            "archivos_en_zip": len(zip_names),
            "zip_bytes": ZIP.stat().st_size,
            "zip_sha256": sha256(ZIP),
            "hallazgos_privacidad": findings,
            "muestra_interna_incluida": False,
            "lista_cerrada": True,
            "zip_test": "OK",
        }
        QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(qa, ensure_ascii=False, indent=2))
    except Exception:
        print("El empaquetado no terminó. Se conservan los artefactos parciales para auditoría manual.")
        raise


if __name__ == "__main__":
    main()
