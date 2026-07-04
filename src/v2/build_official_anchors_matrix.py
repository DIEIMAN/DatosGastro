"""DataGastro V2 - Etapa 2: reporte offline de anclas oficiales y cobertura por rubro.

Lee SOLO archivos locales versionados (config/v2/*.csv) y verifica la presencia de
inventarios locales como metadata. NO hace requests, NO usa API keys, NO descarga nada,
NO lee filas sensibles de los inventarios (solo comprueba si existen), NO escribe datos.

Produce por stdout:
  - cantidad de fuentes oficiales/candidatas;
  - distribucion de cobertura por rubro (mejor cobertura oficial disponible);
  - rubros con buena ancla oficial vs rubros que dependeran de Google/OSM/revision;
  - presencia de inventarios locales (encontrado / no encontrado).

Uso:
    python src/v2/build_official_anchors_matrix.py
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
try:
    from src.v2.load_config import read_csv  # type: ignore
except Exception:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from load_config import read_csv  # type: ignore

CONFIG_DIR = REPO_ROOT / "config" / "v2"

# Orden de mejor a peor para resumir la "mejor cobertura oficial disponible" por rubro.
COBERTURA_ORDEN = {"alta": 4, "media": 3, "baja": 2, "desconocida": 1, "nula": 0}
ROLES_OFICIALES = {"nucleo_oficial", "ancla_institucional"}

# Inventarios locales que la Etapa 2 puede mirar SOLO como metadata (sin abrir filas).
INVENTARIOS = [
    "inventario_archivos.csv",
    "inventario_carpetas.csv",
    "inventario_columnas.csv",
    "inventario_tablas.csv",
    "google_docs_a_exportar.csv",
    "catalogo_eventos_candidato.csv",
]


def find_inventory(name: str) -> list[str]:
    """Devuelve rutas relativas donde existe el inventario (sin leer su contenido)."""
    hits = []
    for path in REPO_ROOT.rglob(name):
        parts = set(path.parts)
        if ".venv" in parts or ".git" in parts:
            continue
        hits.append(str(path.relative_to(REPO_ROOT)))
    return hits


def main() -> int:
    print("=" * 78)
    print("DataGastro V2 - Etapa 2: anclas oficiales y cobertura por rubro (OFFLINE)")
    print("No hace requests, no usa API keys, no descarga ni integra datos.")
    print("=" * 78)

    # --- Fuentes oficiales candidatas ---
    fuentes_path = CONFIG_DIR / "fuentes_oficiales_candidatas_v2.csv"
    _, fuentes = read_csv(fuentes_path)
    disponibles = [f for f in fuentes if f.get("requiere_descarga_futura", "").strip() == "no"]
    candidatas = [f for f in fuentes if f.get("requiere_descarga_futura", "").strip() == "si"]
    print(f"\n[Fuentes] total={len(fuentes)} | sin descarga futura={len(disponibles)} | "
          f"candidatas a descarga={len(candidatas)}")
    for f in fuentes:
        print(f"  - {f['codigo_fuente']:<4} {f['nombre_fuente']} "
              f"(oficialidad={f['nivel_oficialidad']}, sensible={f['sensible']})")

    # --- Cobertura por rubro ---
    cob_path = CONFIG_DIR / "cobertura_fuente_rubro_v2.csv"
    _, cobertura = read_csv(cob_path)
    mejor: dict[str, tuple[int, str, str]] = {}
    for row in cobertura:
        rubro = row["subcategoria_v2"]
        cov = row["cobertura"].strip().lower()
        rol = row["rol"].strip().lower()
        score = COBERTURA_ORDEN.get(cov, 0) if rol in ROLES_OFICIALES else 0
        prev = mejor.get(rubro)
        if prev is None or score > prev[0]:
            mejor[rubro] = (score, cov if rol in ROLES_OFICIALES else "nula", row["codigo_fuente"])

    buena = sorted(r for r, v in mejor.items() if v[0] >= 3)       # alta/media oficial
    parcial = sorted(r for r, v in mejor.items() if v[0] == 2)     # baja oficial
    sin_ancla = sorted(r for r, v in mejor.items() if v[0] <= 1)   # nula/desconocida

    print(f"\n[Cobertura oficial por rubro] rubros evaluados={len(mejor)}")
    print(f"  buena ancla oficial (alta/media): {len(buena)}")
    for r in buena:
        print(f"    + {r} <- {mejor[r][2]} ({mejor[r][1]})")
    print(f"  ancla parcial (baja): {len(parcial)}")
    for r in parcial:
        print(f"    ~ {r} <- {mejor[r][2]} ({mejor[r][1]})")
    print(f"  sin ancla oficial util (nula/desconocida): {len(sin_ancla)}")
    for r in sin_ancla:
        print(f"    x {r}")

    # --- Universo: dependencia de externas / revision ---
    uni_path = CONFIG_DIR / "rubros_universo_gastronomico_v2.csv"
    _, universo = read_csv(uni_path)
    dep_google = [u["subcategoria_v2"] for u in universo if u.get("requiere_google_places") == "si"]
    dep_osm = [u["subcategoria_v2"] for u in universo if u.get("requiere_osm") == "si"]
    dep_manual = [u["subcategoria_v2"] for u in universo if u.get("requiere_revision_manual") == "si"]
    riesgo_alto = [u["subcategoria_v2"] for u in universo if u.get("riesgo_de_confusion") == "alto"]
    por_prioridad: dict[str, int] = defaultdict(int)
    for u in universo:
        por_prioridad[u.get("prioridad", "?")] += 1

    print(f"\n[Universo gastronomico] rubros={len(universo)}")
    print(f"  prioridad: " + ", ".join(f"{k}={v}" for k, v in sorted(por_prioridad.items())))
    print(f"  requieren Google Places: {len(dep_google)}")
    print(f"  requieren OSM: {len(dep_osm)}")
    print(f"  requieren revision manual: {len(dep_manual)}")
    print(f"  riesgo de confusion alto: {len(riesgo_alto)}")
    print(f"    -> {', '.join(sorted(riesgo_alto))}")

    # --- Inventarios locales (solo metadata de presencia) ---
    print("\n[Inventarios locales] (solo presencia, no se leen filas sensibles)")
    for name in INVENTARIOS:
        hits = find_inventory(name)
        if hits:
            print(f"  encontrado: {name} -> {hits}")
        else:
            print(f"  no encontrado: {name}")

    print("\n" + "-" * 78)
    print("Reporte Etapa 2 OK. Diseño y matriz; sin integraciones ejecutadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
