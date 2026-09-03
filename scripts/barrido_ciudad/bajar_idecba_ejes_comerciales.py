"""Los dos .xlsx del IDECBA sobre ejes comerciales: se bajan y se leen acá.

POR QUÉ
-------
Un agente web no puede abrir un binario. Estos dos sí importan:

  AC_EJ_48_GLOS.xlsx    el glosario con la delimitación VIGENTE —calle y altura— de los 48 ejes
  AC_EJ_2026_03.xlsx    locales relevados, ocupados y densidad comercial por eje, 1.er cuatr. 2026

Y hace falta porque **la delimitación que estamos usando es de 2010**. «Alberdi 5401 6199» y
«Rivadavia 10801 11699» salen de un informe de mayo de 2010; en el medio el universo de ejes pasó
de 37 a 53 a 48. Citar esas alturas como delimitación actual sería un error de dieciséis años.

El script baja los dos crudos, imprime **todas** las hojas con su forma —una hoja que nadie mira
es una hoja que no existe— y compara los ejes vigentes contra los que el repositorio viene usando.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/bajar_idecba_ejes_comerciales.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

import pandas as pd
import requests

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "idecba"
CRUDOS = OUT / "crudos"

FUENTES = {
    "AC_EJ_48_GLOS.xlsx":
        "https://estadisticaciudad.gob.ar/eyc/wp-content/uploads/2026/06/AC_EJ_48_GLOS.xlsx",
    "AC_EJ_2026_03.xlsx":
        "https://estadisticaciudad.gob.ar/eyc/wp-content/uploads/2026/06/AC_EJ_2026_03.xlsx",
}
CABECERAS = {"User-Agent": "DataGastro/1.0 (DGDGAS, GCBA; consumo de dato publico)"}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    CRUDOS.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    p("IDECBA · ejes comerciales · los dos .xlsx bajados y leídos")
    p("=" * 100)
    p("")

    for nombre, url in FUENTES.items():
        destino = CRUDOS / nombre
        respuesta = requests.get(url, timeout=120, headers=CABECERAS)
        respuesta.raise_for_status()
        destino.write_bytes(respuesta.content)
        p(f"  {nombre}  ({len(respuesta.content):,} bytes)  ←  {url}")
    p("")

    for nombre in FUENTES:
        destino = CRUDOS / nombre
        libro = pd.ExcelFile(destino)
        p("-" * 100)
        p(f"  {nombre} · {len(libro.sheet_names)} hoja(s): {libro.sheet_names}")
        p("")
        for hoja in libro.sheet_names:
            crudo = pd.read_excel(destino, sheet_name=hoja, header=None)
            p(f"      hoja «{hoja}» — {crudo.shape[0]} filas × {crudo.shape[1]} columnas")
            for indice in range(min(len(crudo), 14)):
                celdas = [str(v) for v in crudo.iloc[indice].tolist() if pd.notna(v)]
                if celdas:
                    p(f"          {indice:>3} | " + " | ".join(c[:34] for c in celdas[:7]))
            if len(crudo) > 14:
                p(f"          ... {len(crudo) - 14} filas más")
            p("")
            crudo.to_csv(OUT / f"{destino.stem}__{hoja}.csv".replace(" ", "_"),
                         index=False, header=False, encoding="utf-8")

    # ------------------------------------------------------------------ el glosario, estructurado
    glosario = pd.read_excel(CRUDOS / "AC_EJ_48_GLOS.xlsx", header=None)
    filas, eje_id, eje_nombre = [], None, None
    for _, cruda in glosario.iloc[2:].iterrows():
        numero, nombre, calle, altura = (cruda[0], cruda[1], cruda[2], cruda[3])
        if pd.isna(calle) or pd.isna(altura):
            continue
        if pd.notna(numero):
            eje_id, eje_nombre = int(numero), str(nombre).strip()
        rango = str(altura).replace("–", "-").split("-")
        filas.append({
            "eje_id": eje_id, "eje": eje_nombre, "calle": str(calle).strip(),
            "altura_desde": int(rango[0]) if rango[0].strip().isdigit() else None,
            "altura_hasta": int(rango[-1]) if rango[-1].strip().isdigit() else None,
            "altura_texto": str(altura).strip(),
        })
    ejes = pd.DataFrame(filas)
    ejes.to_csv(OUT / "ejes_comerciales_48_vigente.csv", index=False, encoding="utf-8")

    p("-" * 100)
    p("  LA DELIMITACIÓN VIGENTE · 48 ejes, calle y altura")
    p("")
    p(f"      {len(ejes)} tramos para {ejes.eje_id.nunique()} ejes "
      f"({int((ejes.groupby('eje_id').size() > 1).sum())} ejes tienen más de una calle)")
    if ejes.eje_id.nunique() != 48:
        p(f"      CORTE · el glosario debería tener 48 ejes y tiene {ejes.eje_id.nunique()}.")
    p("")

    # ------------------------------------------------------------------ contra lo que usábamos
    p("-" * 100)
    p("  CONTRA LO QUE EL REPOSITORIO VENÍA USANDO (informe 437, mayo de 2010)")
    p("")
    for eje, viejo in [("Mataderos", "Alberdi 5401-6199"), ("Liniers", "Rivadavia 10801-11699")]:
        vigente = ejes[ejes.eje == eje]
        actual = " + ".join(f"{f.calle} {f.altura_texto}" for f in vigente.itertuples())
        p(f"      {eje}")
        p(f"          usábamos:  {viejo}")
        p(f"          vigente:   {actual or 'NO FIGURA en el glosario de los 48'}")
    p("")

    # ------------------------------------------------------------------ el relevamiento 2026
    hoja = [h for h in pd.ExcelFile(CRUDOS / "AC_EJ_2026_03.xlsx").sheet_names
            if h.strip().startswith("1er. cuatr. de 2026")][0]
    crudo = pd.read_excel(CRUDOS / "AC_EJ_2026_03.xlsx", sheet_name=hoja, header=1)
    crudo = crudo.rename(columns={c: str(c).split("(")[0].strip().lower().replace(" ", "_")
                                  for c in crudo.columns})
    # La fila de pie —«Fuente: Instituto de Estadística…»— cae en la columna `eje` y se cuela como
    # un eje más si se filtra sólo por no nulo. Se corta por la que sí trae medición.
    relevamiento = crudo[crudo.eje.notna() & crudo.locales_relevados.notna()].copy()
    relevamiento.to_csv(OUT / "ejes_relevamiento_2026_c1.csv", index=False, encoding="utf-8")

    total = relevamiento[relevamiento.eje.astype(str).str.strip().str.lower() == "total"]
    con_dato = relevamiento[relevamiento.eje.astype(str).str.strip().str.lower() != "total"]
    p("-" * 100)
    p("  EL RELEVAMIENTO · 1.er cuatrimestre de 2026")
    p("")
    p(f"      {len(con_dato)} ejes con dato")
    nombres_glosario = set(ejes.eje.astype(str).str.strip())
    nombres_relevamiento = set(con_dato.eje.astype(str).str.strip())
    if nombres_glosario != nombres_relevamiento:
        p(f"      AVISO · glosario y relevamiento no coinciden en los nombres.")
        p(f"          sólo en el relevamiento: {sorted(nombres_relevamiento - nombres_glosario)}")
        p(f"          sólo en el glosario:     {sorted(nombres_glosario - nombres_relevamiento)}")
    else:
        p("      Los 48 nombres del glosario y los del relevamiento coinciden exactamente.")
    if len(total):
        fila = total.iloc[0]
        p(f"      TOTAL Ciudad: {int(fila.locales_relevados):,} locales relevados · "
          f"{int(fila.locales_ocupados):,} ocupados · "
          f"tasa de ocupación {float(fila.tasa_de_ocupación):.1f} %")
    p("")
    columna = "densidad_comercial"
    if columna in relevamiento.columns:
        top = con_dato.sort_values(columna, ascending=False).head(8)
        p(f"      {'eje':<28}{'relevados':>11}{'ocupados':>10}{'ocupación':>11}{'dens/cuadra':>13}")
        for fila in top.itertuples():
            p(f"      {str(fila.eje)[:27]:<28}{int(fila.locales_relevados):>11,}"
              f"{int(fila.locales_ocupados):>10,}{float(fila.tasa_de_ocupación):>10.1f}%"
              f"{float(getattr(fila, columna)):>13.1f}")
    p("")

    p("=" * 100)
    p(f"  crudos en {CRUDOS.relative_to(ROOT)} · hojas volcadas a CSV en {OUT.relative_to(ROOT)}")
    p("=" * 100)
    p("")

    (OUT / "IDECBA_EJES.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
