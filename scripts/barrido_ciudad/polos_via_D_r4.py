"""Ronda 4 · qué le hace a la vía D que E02 y E07 hayan cambiado de forma.

POR QUÉ HAY QUE CORRERLO
------------------------
La vía D se abre cuando la fila toca un enclave cruzable. E07 pasó de 131,7 a 15,6 ha y E02 de
17,6 a 30,7: uno se achicó ocho veces y el otro casi se duplicó. Dejar la matriz de la ronda 3 sin
recomputar sería publicar un cruce contra una geometría que ya no existe.

**Sólo se recomputa la vía D.** A, B, C y F se leen de la ronda 3 sin tocar: sus insumos no se
movieron. Y la ronda 3 queda intacta en sus archivos; esto escribe con sufijo `_r4`.

Google Places: 0 requests. USIG: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_via_D_r4.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import BARRIDO, CRS_METRICO, envolventes_22, soportes_94  # noqa: E402

OUT = BARRIDO / "seis_vias"


def cruzar(soporte: gpd.GeoDataFrame, clave: str, enclaves: gpd.GeoDataFrame) -> pd.DataFrame:
    cruzables = enclaves[enclaves.computa_via_D == "si"]
    sin_computo = enclaves[(enclaves.computa_via_D == "no") & enclaves.geometry.notna()]
    filas = []
    for fila in soporte.itertuples():
        registro = {clave: getattr(fila, clave)}
        if fila.geometry is None or fila.geometry.is_empty:
            registro.update({"via_D_estado_r4": "", "via_D_abierta_r4": "",
                             "via_D_enclave_r4": "", "via_D_enclave_sin_computo_r4": ""})
            filas.append(registro)
            continue
        tocados = cruzables[cruzables.intersects(fila.geometry)]
        vistos = sin_computo[sin_computo.intersects(fila.geometry)]
        registro["via_D_estado_r4"] = "abierta" if len(tocados) else "no_medida"
        registro["via_D_abierta_r4"] = "si" if len(tocados) else "pendiente"
        registro["via_D_enclave_r4"] = "; ".join(sorted(tocados.enclave_id))
        registro["via_D_enclave_sin_computo_r4"] = "; ".join(sorted(vistos.enclave_id))
        filas.append(registro)
    return pd.DataFrame(filas)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    enclaves = gpd.read_file(OUT / "enclaves_comunitarios_r4.geojson").to_crs(CRS_METRICO)
    viejos = gpd.read_file(OUT / "enclaves_comunitarios_r3.geojson").to_crs(CRS_METRICO)

    p("RONDA 4 · LA VÍA D RECOMPUTADA CONTRA LA GEOMETRÍA NUEVA DE E02 Y E07")
    p("=" * 100)
    p("")
    p("  Sólo la vía D. A, B, C y F se leen de la ronda 3 sin recalcular.")
    p("  Google Places: 0 requests.")
    p("")
    p(f"      {'enclave':<9}{'ha ronda 3':>12}{'ha ronda 4':>12}   computa")
    for fila in enclaves.itertuples():
        antes = viejos[viejos.enclave_id == fila.enclave_id]
        ha_antes = float(antes.geometry.iloc[0].area / 10_000) if len(antes) else 0.0
        marca = "  ←" if abs(ha_antes - fila.ha) > 0.05 else ""
        p(f"      {fila.enclave_id:<9}{ha_antes:>12.1f}{fila.ha:>12.1f}   "
          f"{fila.computa_via_D}{marca}")
    p("")

    for archivo, clave, soporte, etiqueta in [
            ("seis_vias_94_filas", "polo_id", soportes_94(), "LAS 94 FILAS"),
            ("seis_vias_22_zonas", "referencia_id", envolventes_22(), "LAS 22 ZONAS")]:
        tabla = pd.read_csv(OUT / f"{archivo}_r3.csv")
        nuevo = cruzar(soporte, clave, enclaves)
        tabla = tabla.merge(nuevo, on=clave, how="left")
        movidas = tabla[(tabla.via_D_estado.astype(str) != tabla.via_D_estado_r4.astype(str))
                        & tabla.via_D_estado_r4.astype(str).ne("")]

        p("-" * 100)
        p(f"  {etiqueta}")
        p("")
        antes = int((tabla.via_D_estado == "abierta").sum())
        ahora = int((tabla.via_D_estado_r4 == "abierta").sum())
        p(f"      vía D abierta:  {antes} → {ahora}")
        p(f"      filas que cambian de estado: {len(movidas)}")
        for fila in movidas.itertuples():
            nombre = getattr(fila, "nombre_polo", None) or getattr(fila, "nombre", "")
            p(f"            {str(getattr(fila, clave))[:24]:<26}{str(nombre)[:26]:<28}"
              f"{fila.via_D_estado} → {fila.via_D_estado_r4}   "
              f"{fila.via_D_enclave} → {fila.via_D_enclave_r4}")
        p("")
        # El recuento de vías se rehace con la D nueva y la B de la ronda 3 sin tocar.
        tabla["n_vias_medibles_r4"] = (
            (tabla.via_A_abierta == "si").astype(int) + (tabla.via_B_abierta == "si").astype(int)
            + (tabla.via_C_abierta == "si").astype(int)
            + (tabla.via_D_abierta_r4 == "si").astype(int)
            + (tabla.via_F_abierta == "si").astype(int))
        con_soporte = tabla[tabla.via_D_estado_r4.astype(str) != ""]
        cambia_recuento = con_soporte[
            con_soporte.n_vias_medibles.fillna(-1) != con_soporte.n_vias_medibles_r4]
        p(f"      filas cuyo NÚMERO de vías abiertas cambia: {len(cambia_recuento)}")
        for fila in cambia_recuento.itertuples():
            nombre = getattr(fila, "nombre_polo", None) or getattr(fila, "nombre", "")
            p(f"            {str(getattr(fila, clave))[:24]:<26}{str(nombre)[:26]:<28}"
              f"{fila.n_vias_medibles:.0f} → {fila.n_vias_medibles_r4}")
        p("")
        tabla.to_csv(OUT / f"{archivo}_r4.csv", index=False, encoding="utf-8")

    p("=" * 100)
    p("  la ronda 3 queda intacta; esto escribe seis_vias_94_filas_r4.csv y "
      "seis_vias_22_zonas_r4.csv")
    p("=" * 100)
    p("")

    (OUT / "VIA_D_R4.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
