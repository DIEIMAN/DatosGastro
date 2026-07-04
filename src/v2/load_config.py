"""Carga y valida los CSV de configuracion de DataGastro V2 (config/v2/).

No hace requests, no usa API keys, no lee datos reales. Solo lee archivos de configuracion
versionados y verifica que tengan las columnas esperadas.

Uso:
    python src/v2/load_config.py            # imprime resumen de configs
    from src.v2.load_config import load_all # uso programatico

Diseno: solo libreria estandar (csv, pathlib). No depende de pandas ni de PyYAML.
"""
from __future__ import annotations

import csv
from pathlib import Path

# Raiz del repo: este archivo esta en src/v2/load_config.py -> subir dos niveles.
REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config" / "v2"

# Columnas esperadas por cada config. Es el contrato minimo de cada CSV.
EXPECTED_COLUMNS: dict[str, list[str]] = {
    "taxonomia_gastronomica_v2.csv": [
        "categoria_principal",
        "subcategoria",
        "incluye",
        "excluye",
        "fuentes_sugeridas",
        "riesgo_metodologico",
        "criterio_de_validacion",
        "es_transversal",
    ],
    "fuentes_v2.csv": [
        "codigo_fuente",
        "nombre_fuente",
        "universo",
        "naturaleza",
        "rol_metodologico",
        "oficial",
        "uso_permitido",
        "limitaciones",
        "sensible",
        "versionable",
    ],
    "google_places_query_templates.csv": [
        "subcategoria",
        "query_template",
        "tipo_query",
        "riesgo",
        "requiere_revision_manual",
    ],
    "osm_tags_v2.csv": [
        "tag_osm",
        "valor_osm",
        "subcategoria_v2",
        "confianza_tag",
        "riesgo",
        "requiere_revision_manual",
    ],
    "niveles_confianza_v2.csv": [
        "nivel",
        "etiqueta",
        "descripcion",
        "condicion_tipica",
        "limitacion",
    ],
    "reglas_exclusion_v2.csv": [
        "patron",
        "motivo_exclusion",
        "aplica_a",
        "accion",
    ],
    "rubros_piloto_v2.csv": [
        "rubro_piloto",
        "subcategorias_incluidas",
        "prioridad",
        "justificacion",
    ],
    # --- Etapa 2 ---
    "fuentes_oficiales_candidatas_v2.csv": [
        "codigo_fuente",
        "nombre_fuente",
        "tipo_fuente",
        "origen_institucional",
        "descripcion",
        "cobertura_esperada",
        "rubros_potenciales",
        "nivel_oficialidad",
        "limitaciones",
        "riesgo_metodologico",
        "requiere_descarga_futura",
        "requiere_convenio_o_permiso",
        "versionable",
        "sensible",
    ],
    "cobertura_fuente_rubro_v2.csv": [
        "codigo_fuente",
        "subcategoria_v2",
        "cobertura",
        "calidad_esperada",
        "rol",
        "observacion",
    ],
    "rubros_universo_gastronomico_v2.csv": [
        "subcategoria_v2",
        "categoria_principal",
        "prioridad",
        "incluido_en_universo_general",
        "apto_para_informe_especifico",
        "fuentes_principales_probables",
        "requiere_google_places",
        "requiere_osm",
        "requiere_revision_manual",
        "riesgo_de_confusion",
        "observacion",
    ],
    # --- Etapa 3.5 (normalizacion I10) ---
    "barrios_caba_aliases_v2.csv": [
        "barrio_oficial",
        "alias",
        "comuna",
        "tipo_alias",
        "confianza",
        "observacion",
    ],
    "reglas_desagregacion_i10_v2.csv": [
        "hoja_origen",
        "patron",
        "campo_aplicable",
        "subcategoria_v2_destino",
        "confianza",
        "accion",
        "observacion",
    ],
    # --- Etapa 2.5 (fuentes internas DGDGAS) ---
    "fuentes_internas_v2.csv": [
        "codigo_fuente",
        "nombre_fuente",
        "carpeta_origen",
        "tipo_fuente",
        "rol_metodologico",
        "sensibilidad",
        "versionable",
        "uso_permitido",
        "limitaciones",
        "estado_revision",
    ],
}


class ConfigError(Exception):
    """Error de configuracion V2 (archivo faltante o columnas invalidas)."""


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Lee un CSV UTF-8 y devuelve (encabezados, filas como dicts)."""
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        rows = [dict(r) for r in reader]
    return header, rows


def validate_config_file(filename: str, expected: list[str]) -> dict:
    """Valida existencia y columnas de un config. Devuelve un dict-resumen."""
    path = CONFIG_DIR / filename
    result = {
        "archivo": filename,
        "existe": path.exists(),
        "filas": 0,
        "columnas_ok": False,
        "faltan_columnas": [],
        "columnas_extra": [],
    }
    if not path.exists():
        return result

    header, rows = read_csv(path)
    header_set = set(header)
    expected_set = set(expected)
    result["filas"] = len(rows)
    result["faltan_columnas"] = sorted(expected_set - header_set)
    result["columnas_extra"] = sorted(header_set - expected_set)
    result["columnas_ok"] = not result["faltan_columnas"]
    return result


def load_all(strict: bool = False) -> dict:
    """Valida todos los configs declarados. Si strict, lanza ConfigError ante el primer fallo."""
    summary: dict[str, dict] = {}
    for filename, expected in EXPECTED_COLUMNS.items():
        res = validate_config_file(filename, expected)
        summary[filename] = res
        if strict and (not res["existe"] or not res["columnas_ok"]):
            raise ConfigError(f"Config invalida: {filename} -> {res}")
    return summary


def main() -> int:
    print(f"[load_config] Directorio de configs: {CONFIG_DIR}")
    summary = load_all(strict=False)
    ok = True
    for filename, res in summary.items():
        estado = "OK" if (res["existe"] and res["columnas_ok"]) else "FALLA"
        if estado == "FALLA":
            ok = False
        print(f"  [{estado}] {filename}: existe={res['existe']} filas={res['filas']} "
              f"faltan={res['faltan_columnas']}")
    print("[load_config] Resultado:", "OK" if ok else "HAY FALLAS")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
