"""Copia SOLO agregados seguros del padrón integrado a una carpeta publicable/versionable
y genera un GeoJSON de mapa sanitizado (sin nombre, dirección, razón social ni place_id).

Origen (gitignored, sensible): outputs/casas_pastas_integrado/
Destino (versionable):         outputs/casas_pastas_reporte/integrado_sanitizado/

NO copia padrón, geojson con nombres, dedup ni revisión manual (tienen datos individuales).
NO hace requests. NO commitea. Verifica que ningún archivo publicado tenga columnas sensibles.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
AUD = INT / "auditoria_calidad"
DEST = ROOT / "outputs" / "casas_pastas_reporte" / "integrado_sanitizado"

# Agregados seguros a publicar (sin filas individuales sensibles).
COPIAR = [
    INT / "resumen_integrado.csv",
    INT / "integrado_por_fuente.csv",
    INT / "integrado_por_comuna.csv",
    INT / "integrado_por_barrio.csv",
    INT / "densidad_integrado_por_comuna.csv",
    INT / "densidad_integrado_por_barrio.csv",
    INT / "calidad_google_queries.csv",
    INT / "cobertura_cadenas_e_independientes.csv",
    AUD / "resumen_auditoria_calidad.csv",
]

# Columnas/contenido que NO deben aparecer en lo publicado.
COLS_PROHIBIDAS = {"nombre", "direccion", "place_id", "id_origen", "razon_social",
                   "nombre_original", "direccion_original", "lat", "lon"}
PAT_PROHIBIDOS = [
    re.compile(r"ChIJ[A-Za-z0-9_\-]{10,}"),       # place_id de Google
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),         # emails
    re.compile(r"\b\d{2}-\d{8}-\d\b"),              # CUIT
]

# GeoJSON sanitizado: solo estos campos (+ geometry).
GEO_PROPS = ["id_anonimo", "fuente_principal", "clasificacion_integrada",
             "es_cadena_detectada", "tipo_establecimiento_google", "comuna", "barrio"]


def verificar(path: Path) -> list[str]:
    """Devuelve lista de problemas (vacía si está limpio)."""
    problemas = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    if not rows:
        return problemas
    header = [h.strip().lower() for h in rows[0]]
    for c in header:
        if c in COLS_PROHIBIDAS:
            problemas.append(f"columna prohibida: {c}")
    blob = "\n".join(",".join(r) for r in rows)
    for pat in PAT_PROHIBIDOS:
        if pat.search(blob):
            problemas.append(f"patrón sensible: {pat.pattern}")
    return problemas


def main() -> int:
    faltan = [p.name for p in COPIAR if not p.exists()]
    if faltan:
        print(f"ABORTADO: faltan insumos: {faltan}. Corré integrador + auditoría primero.")
        return 2
    DEST.mkdir(parents=True, exist_ok=True)

    copiados, rechazados = [], []
    for src in COPIAR:
        problemas = verificar(src)
        if problemas:
            rechazados.append((src.name, problemas))
            continue
        shutil.copy2(src, DEST / src.name)
        copiados.append(src.name)

    # ---- GeoJSON sanitizado desde el padrón ----
    padron = INT / "padron_candidato_integrado.csv"
    feats = []
    if padron.exists():
        for i, r in enumerate(csv.DictReader(padron.open(encoding="utf-8-sig")), 1):
            try:
                lat, lon = float(r["lat"]), float(r["lon"])
            except (TypeError, ValueError):
                continue
            props = {
                "id_anonimo": f"PT{i:04d}",
                "fuente_principal": r.get("fuente_principal", ""),
                "clasificacion_integrada": r.get("clase_integrada", ""),
                "es_cadena_detectada": r.get("es_cadena_detectada", ""),
                "tipo_establecimiento_google": r.get("tipo_establecimiento_google", ""),
                "comuna": r.get("comuna", ""),
                "barrio": r.get("barrio", ""),
            }
            feats.append({"type": "Feature",
                          "geometry": {"type": "Point", "coordinates": [lon, lat]},
                          "properties": props})
    geo_path = DEST / "mapa_puntos_sanitizado.geojson"
    geo_path.write_text(json.dumps({"type": "FeatureCollection", "features": feats},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    # verificar geojson sanitizado
    gtext = geo_path.read_text(encoding="utf-8")
    geo_ok = not any(p.search(gtext) for p in PAT_PROHIBIDOS) and \
        all(k not in gtext for k in ("\"nombre\"", "\"direccion\"", "\"place_id\""))

    print(f"Copiados ({len(copiados)}):")
    for c in copiados:
        print(f"  + {c}")
    if rechazados:
        print("RECHAZADOS por contenido sensible:")
        for n, ps in rechazados:
            print(f"  - {n}: {ps}")
    print(f"GeoJSON sanitizado: {geo_path.name} ({len(feats)} puntos) | limpio={geo_ok}")
    print(f"Destino: {DEST.relative_to(ROOT)}")
    return 0 if not rechazados and geo_ok else 1


if __name__ == "__main__":
    sys.exit(main())
