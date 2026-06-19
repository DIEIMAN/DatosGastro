"""Genera la versión SANITIZADA (publicable) del análisis de casas/fábricas de pastas.

Lee las salidas crudas de outputs/casas_pastas/ (gitignored, con datos individuales) y produce
en outputs/casas_pastas_reporte/ SOLO agregados, sin razón social, nombres de personas,
direcciones, teléfonos, mails, CUIT ni IDs individuales.

Salidas:
  tabla_resumen_general.csv, top_comunas_cantidad.csv, top_barrios_cantidad.csv,
  top_comunas_densidad.csv, top_barrios_densidad.csv, comparacion_agc_osm.csv,
  limitaciones_metodologicas.csv, mapa_nodos_agregado.png, mapa_nodos_puntos.geojson (sin nombres).
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "outputs" / "casas_pastas"
OUT = ROOT / "outputs" / "casas_pastas_reporte"
GEO_COMUNAS = ROOT / "data" / "raw" / "geo_comunas.geojson"

# campos que NUNCA deben salir a la versión publicable
PROHIBIDOS = {"nombre_original", "razon_social", "direccion_original", "descripcion_original",
              "id_registro_original", "telefono", "mail", "email", "cuit", "observaciones"}


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # guardia dura: ningún campo prohibido puede colarse
    safe_cols = [c for c in cols if c.lower() not in PROHIBIDOS]
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=safe_cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    resumen = json.loads((SRC / "_resumen_build.json").read_text(encoding="utf-8"))
    por_comuna = read_csv(SRC / "casas_pastas_por_comuna.csv")
    por_barrio = read_csv(SRC / "casas_pastas_por_barrio.csv")
    osm = read_csv(SRC / "osm_casas_pastas_candidatos.csv")
    anios = read_csv(SRC / "casas_pastas_habilitaciones_por_anio.csv")

    def num(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return 0.0

    # --- tabla_resumen_general ---
    osm_niv = Counter(r.get("nivel_universo", "") for r in osm)
    resumen_rows = [
        {"indicador": "Universo A estricto (AGC, deduplicado)", "valor": resumen["universo_A"],
         "fuente": "F02 / AGC", "tipo": "registro administrativo oficial"},
        {"indicador": "Universo B probable (AGC)", "valor": resumen["universo_B"],
         "fuente": "F02 / AGC", "tipo": "pendiente de validacion"},
        {"indicador": "Geolocalizados (A)", "valor": resumen["geolocalizados_A"], "fuente": "F02 + cache local", "tipo": "oficial"},
        {"indicador": "Sin geolocalizar (A)", "valor": resumen["sin_geo_A"], "fuente": "F02", "tipo": "oficial"},
        {"indicador": "Puntos A en OSM (shop=pasta / equiv.)", "valor": osm_niv.get("A", 0),
         "fuente": "OpenStreetMap", "tipo": "relevamiento abierto auxiliar"},
        {"indicador": "Puntos B en OSM", "valor": osm_niv.get("B", 0), "fuente": "OpenStreetMap", "tipo": "auxiliar"},
        {"indicador": "Puntos descartados (C) en OSM", "valor": osm_niv.get("C", 0), "fuente": "OpenStreetMap", "tipo": "auxiliar"},
    ]
    write_csv(OUT / "tabla_resumen_general.csv", resumen_rows, ["indicador", "valor", "fuente", "tipo"])

    # --- tops cantidad / densidad ---
    pc = [r for r in por_comuna if int(float(r["cantidad"])) > 0]
    write_csv(OUT / "top_comunas_cantidad.csv",
              sorted(pc, key=lambda r: -int(float(r["cantidad"])))[:10],
              ["comuna", "cantidad", "cantidad_geolocalizada", "area_km2", "densidad_por_km2"])
    write_csv(OUT / "top_comunas_densidad.csv",
              sorted([r for r in por_comuna if num(r["densidad_por_km2"]) > 0], key=lambda r: -num(r["densidad_por_km2"]))[:10],
              ["comuna", "cantidad", "area_km2", "densidad_por_km2"])
    pb = [r for r in por_barrio if int(float(r["cantidad"])) > 0]
    write_csv(OUT / "top_barrios_cantidad.csv",
              sorted(pb, key=lambda r: -int(float(r["cantidad"])))[:10],
              ["barrio", "comuna", "cantidad", "area_km2", "densidad_por_km2"])
    write_csv(OUT / "top_barrios_densidad.csv",
              sorted(pb, key=lambda r: -num(r["densidad_por_km2"]))[:10],
              ["barrio", "comuna", "cantidad", "area_km2", "densidad_por_km2"])

    # --- comparacion AGC vs OSM ---
    comp = [
        {"fuente": "AGC / F02 (oficial)", "tipo": "registro administrativo oficial",
         "universo_A": resumen["universo_A"], "universo_B": resumen["universo_B"],
         "nota": "habilitaciones vinculadas a elaboracion de pastas; NO locales activos"},
        {"fuente": "OpenStreetMap (auxiliar)", "tipo": "relevamiento abierto colaborativo",
         "universo_A": osm_niv.get("A", 0), "universo_B": osm_niv.get("B", 0),
         "nota": "shop=pasta y equivalentes; no oficial, no verificado, pendiente de validacion"},
    ]
    write_csv(OUT / "comparacion_agc_osm.csv", comp, ["fuente", "tipo", "universo_A", "universo_B", "nota"])

    # --- limitaciones ---
    lims = [
        {"id": "L1", "limitacion": "AGC mide habilitaciones, no locales activos",
         "implicancia": "un registro puede estar cerrado hoy"},
        {"id": "L2", "limitacion": "Rubro AGC estricto angosto",
         "implicancia": "subrepresenta casas de pastas registradas bajo rubros genericos"},
        {"id": "L3", "limitacion": "Geocodificacion solo con cache local",
         "implicancia": "1 de 10 sin punto; sin servicios externos pagos"},
        {"id": "L4", "limitacion": "Sin poblacion local",
         "implicancia": "no se calcula densidad por 10.000 habitantes"},
        {"id": "L5", "limitacion": "OSM colaborativo e incompleto",
         "implicancia": "no es padron oficial; util como contraste y para validar"},
        {"id": "L6", "limitacion": "N pequeno en universo A",
         "implicancia": "rankings de densidad sensibles; diagnostico inicial, no censo"},
        {"id": "L7", "limitacion": "Diferencia AGC vs OSM",
         "implicancia": "no es error: es diferencia de fuente y definicion"},
    ]
    write_csv(OUT / "limitaciones_metodologicas.csv", lims, ["id", "limitacion", "implicancia"])

    # --- mapa agregado + geojson sin nombres (solo AGC, A) ---
    maestro_gj = json.loads((SRC / "casas_pastas_maestro.geojson").read_text(encoding="utf-8"))
    safe_feats = []
    coords = []
    for ft in maestro_gj.get("features", []):
        props = ft.get("properties", {})
        if props.get("fuente") != "F02":  # solo AGC oficial en la capa publicable
            continue
        coords.append(ft["geometry"]["coordinates"])
        safe_feats.append({
            "type": "Feature", "geometry": ft["geometry"],
            "properties": {
                "fuente": "AGC/F02", "comuna": props.get("comuna_efectiva", ""),
                "barrio": props.get("barrio_efectivo", ""),
                "categoria_pastas": props.get("categoria_pastas", ""),
                "calidad_geo": props.get("calidad_geo", ""),
                # SIN nombre_original, SIN direccion, SIN id
            }})
    (OUT / "mapa_nodos_puntos.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": safe_feats,
                    "_nota": "Solo AGC/F02 (oficial). Sin nombres ni direcciones. OSM queda aparte."},
                   ensure_ascii=False), encoding="utf-8")

    try:
        import geopandas as gpd
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        comunas = gpd.read_file(GEO_COMUNAS).to_crs(4326)
        fig, ax = plt.subplots(figsize=(8, 9))
        comunas.boundary.plot(ax=ax, color="#999", linewidth=0.6)
        if coords:
            ax.scatter([c[0] for c in coords], [c[1] for c in coords], s=26, color="#c0392b",
                       alpha=0.85, edgecolor="white", linewidth=0.4)
        ax.set_title(f"Casas/fábricas de pastas — registro AGC oficial (A, n={len(coords)})\n"
                     "Sin etiquetas individuales · OSM (auxiliar) no incluido")
        ax.set_axis_off()
        fig.tight_layout(); fig.savefig(OUT / "mapa_nodos_agregado.png", dpi=140); plt.close(fig)
        mapa_ok = True
    except Exception as exc:  # noqa: BLE001
        mapa_ok = False
        print("AVISO mapa:", exc)

    print("Reporte sanitizado generado en outputs/casas_pastas_reporte/")
    print("Archivos:", sorted(p.name for p in OUT.iterdir()))
    print("mapa_agregado:", mapa_ok, "| puntos AGC en geojson:", len(safe_feats))


if __name__ == "__main__":
    main()
