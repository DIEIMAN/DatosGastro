"""IDECBA · la serie de cuatro cuatrimestres, y el cruce con las zonas del Atlas.

POR QUÉ IMPORTA
----------------
Es **la única medida de estado a escala de zona que existe**, y es del propio GCBA: 48 ejes
comerciales relevados **a pie**, cuatrimestralmente, con locales relevados, ocupados, tasa de
ocupación y densidad por cuadra. No depende de Google Places ni de ninguna de las fuentes que se
cayeron esta semana.

Y el .xlsx trae **cuatro cuatrimestres**, no uno: 1.º, 2.º y 3.º de 2025 y 1.º de 2026. Con eso la
variación interanual se computa acá, sobre el mismo eje y el mismo método de relevamiento, en vez
de leerse de una columna cuyo cálculo no vemos.

LO QUE ESTE GUION NO HACE
--------------------------
**No cruza por geometría.** El IDECBA delimita sus ejes por calle y altura; la base tiene
`direccion_norm` vacía en el 46,6 % de los casos (Parte X). Cruzar por nombre de eje contra nombre
de zona es un cruce **nominal**, y se declara como tal: sirve para saber qué ejes tenemos y cuáles
no, no para atribuirle a una zona la tasa de ocupación de un eje.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/idecba_serie_y_cruce.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import BARRIDO, sin_tildes  # noqa: E402

IDECBA = BARRIDO / "idecba"
COWORK = BARRIDO / "desde_cowork" / "evidencia_2026"
SALIDA = BARRIDO / "ronda_10"
OUT_SERIE = SALIDA / "idecba_serie_48_ejes.csv"
OUT_CRUCE = SALIDA / "idecba_x_atlas.csv"
INFORME = SALIDA / "IDECBA_SERIE.txt"

PERIODOS = {
    "2025_c1": "AC_EJ_2026_03__1er._cuatr._de_2025.csv",
    "2025_c2": "AC_EJ_2026_03__2do._cuatr._de_2025.csv",
    "2025_c3": "AC_EJ_2026_03__3er._cuatr._de_2025.csv",
    "2026_c1": "AC_EJ_2026_03__1er._cuatr._de_2026_.csv",
}


# Filas que no son ejes: los cuatro subtotales por región y los totales de Ciudad.
NO_SON_EJES = {"NORTE", "CENTRO", "OESTE", "SUR", "TOTAL", "CIUDAD DE BUENOS AIRES",
               "TOTAL CIUDAD", "EJE COMERCIAL"}


def _numero(texto: str) -> float | None:
    """Parsea un número del volcado del .xlsx SIN romper los decimales.

    El volcado usa punto decimal («96.98630136986301»). Sacar los puntos como si fueran separador
    de miles convertía una tasa del 97 % en 9.698.630.136.986.301, y la tabla salía igual. Sólo se
    trata el punto como separador de miles cuando además hay una coma decimal.
    """
    texto = str(texto).strip()
    if not texto or texto.lower() == "nan":
        return None
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


def leer_periodo(ruta: Path) -> pd.DataFrame:
    """Las hojas traen el título en la fila 0 y los encabezados abajo. Se busca el eje por texto."""
    crudo = pd.read_csv(ruta, encoding="utf-8", header=None, dtype=str)
    filas = []
    for _, fila in crudo.iterrows():
        celdas = [str(c).strip() for c in fila.tolist()]
        eje = celdas[0]
        if not eje or sin_tildes(eje) in NO_SON_EJES or eje.lower() == "nan"                 or eje.startswith("Local"):
            continue
        numeros = [_numero(c) for c in celdas[1:]]
        if numeros[:2] == [None, None]:
            continue
        filas.append({"eje": eje, "relevados": numeros[0], "ocupados": numeros[1],
                      "tasa_ocupacion": numeros[2] if len(numeros) > 2 else None,
                      "densidad": numeros[-1]})
    return pd.DataFrame(filas)


def main() -> int:  # noqa: C901
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    SALIDA.mkdir(parents=True, exist_ok=True)
    p("IDECBA · ejes comerciales · la serie de cuatro cuatrimestres")
    p("=" * 100)
    p("")
    p("  relevamiento A PIE del GCBA. No depende de Places ni de ninguna fuente caída esta semana.")
    p("")

    series = {}
    for etiqueta, archivo in PERIODOS.items():
        ruta = IDECBA / archivo
        if not ruta.exists():
            p(f"      !! falta {archivo}")
            continue
        d = leer_periodo(ruta)
        series[etiqueta] = d.set_index(d.eje.map(sin_tildes))
        p(f"      {etiqueta}: {len(d)} ejes · {d.relevados.sum():,.0f} relevados · "
          f"{d.ocupados.sum():,.0f} ocupados · "
          f"{d.ocupados.sum() / d.relevados.sum() * 100:.1f} % de ocupación")
    p("")

    if "2025_c1" not in series or "2026_c1" not in series:
        p("      sin los dos primeros cuatrimestres no hay interanual.")
        INFORME.write_text(buffer.getvalue(), encoding="utf-8")
        print(buffer.getvalue())
        return 1

    base, ahora = series["2025_c1"], series["2026_c1"]
    tabla = ahora[["eje", "relevados", "ocupados", "tasa_ocupacion", "densidad"]].copy()
    tabla = tabla.join(base[["relevados", "ocupados", "tasa_ocupacion"]],
                       rsuffix="_2025_c1", how="left")
    tabla["var_ocupados_interanual_pct"] = (
        (tabla.ocupados - tabla.ocupados_2025_c1) / tabla.ocupados_2025_c1 * 100).round(1)
    tabla["var_tasa_pp"] = (tabla.tasa_ocupacion - tabla.tasa_ocupacion_2025_c1).round(1)
    for etiqueta in ("2025_c2", "2025_c3"):
        if etiqueta in series:
            tabla[f"ocupados_{etiqueta}"] = series[etiqueta]["ocupados"]
    tabla = tabla.sort_values("var_ocupados_interanual_pct")
    tabla.to_csv(OUT_SERIE, index=False, encoding="utf-8")

    p("-" * 100)
    p("  VARIACIÓN INTERANUAL · 1.er cuatrimestre de 2025 → 1.er cuatrimestre de 2026")
    p("")
    p(f"      {'eje':<30}{'ocup. 2025':>11}{'ocup. 2026':>11}{'var %':>9}{'tasa 2026':>11}"
      f"{'Δ pp':>7}")
    con_dato = tabla.dropna(subset=["var_ocupados_interanual_pct"])
    p("")
    p("      LOS DIEZ QUE MÁS CAEN")
    for r in con_dato.head(10).itertuples():
        p(f"      {r.eje:<30}{r.ocupados_2025_c1:>11,.0f}{r.ocupados:>11,.0f}"
          f"{r.var_ocupados_interanual_pct:>8.1f}%{r.tasa_ocupacion:>10.1f}%"
          f"{r.var_tasa_pp:>7.1f}")
    p("")
    p("      LOS DIEZ QUE MÁS SUBEN")
    for r in con_dato.tail(10).iloc[::-1].itertuples():
        p(f"      {r.eje:<30}{r.ocupados_2025_c1:>11,.0f}{r.ocupados:>11,.0f}"
          f"{r.var_ocupados_interanual_pct:>8.1f}%{r.tasa_ocupacion:>10.1f}%"
          f"{r.var_tasa_pp:>7.1f}")
    p("")
    total_2025 = con_dato.ocupados_2025_c1.sum()
    total_2026 = con_dato.ocupados.sum()
    p(f"      TOTAL de los {len(con_dato)} ejes con serie completa: "
      f"{total_2025:,.0f} → {total_2026:,.0f} ocupados "
      f"({(total_2026 - total_2025) / total_2025 * 100:+.1f} %)")
    p("")

    p("-" * 100)
    p("  EL CRUCE CON EL ATLAS · NOMINAL, no geométrico")
    p("")
    ruta_cruce = COWORK / "idecba_ejes_comerciales.csv"
    if ruta_cruce.exists():
        cruce = pd.read_csv(ruta_cruce, encoding="utf-8")
        cruce["clave"] = cruce.eje.map(sin_tildes)
        idecba = tabla.copy()
        idecba["clave"] = idecba.index
        unido = cruce.merge(idecba.reset_index(drop=True), on="clave", how="left",
                            suffixes=("", "_idecba"))
        unido["en_el_atlas"] = unido.esta_en_el_atlas.str.startswith(("SI", "parcial"))
        con = unido[unido.en_el_atlas & unido.ocupados.notna()]
        sin = unido[~unido.en_el_atlas & unido.ocupados.notna()]
        p(f"      el CSV de cowork mapea {len(cruce)} ejes. **Son 48 los vigentes, no 53**: el")
        p("      universo pasó de 37 a 53 y de 53 a 48 entre 2010 y hoy, y el glosario vigente")
        p("      trae 48. Los nombres del glosario y los del relevamiento coinciden exactamente.")
        p("")
        p(f"      con dato del IDECBA y presentes en el Atlas: {len(con)}")
        p(f"      con dato del IDECBA y NO en el Atlas:        {len(sin)}")
        p("")
        if len(con):
            p("      LOS QUE YA TENEMOS, ordenados por variación interanual:")
            p(f"        {'eje':<28}{'zona del Atlas':<34}{'var %':>8}{'tasa':>8}")
            for r in con.sort_values("var_ocupados_interanual_pct").itertuples():
                p(f"        {r.eje:<28}{str(r.esta_en_el_atlas)[:32]:<34}"
                  f"{r.var_ocupados_interanual_pct:>7.1f}%{r.tasa_ocupacion:>7.1f}%")
        unido.to_csv(OUT_CRUCE, index=False, encoding="utf-8")
        p("")
        p("      POR QUÉ EL CRUCE ES NOMINAL Y NO GEOMÉTRICO: el IDECBA delimita por calle y")
        p("      altura, y la base tiene `direccion_norm` vacía en el 46,6 % (Parte X). Este")
        p("      cruce dice QUÉ EJES TENEMOS, no le atribuye a ninguna zona la tasa de su eje.")
        p("      Para eso hay que construir los 80 tramos del glosario como geometría.")
    p("")
    p("  DOS DELIMITACIONES QUE VENÍAMOS USANDO MAL (informe 437, mayo de 2010):")
    p("      Mataderos  usábamos Alberdi 5401-6199   · vigente Av. Alberdi 5501-6299")
    p("      Liniers    usábamos Rivadavia 10801-11699 · vigente Ramón Falcón 6801-7299")
    p("")
    p(f"  salidas: {OUT_SERIE.name} · {OUT_CRUCE.name}")

    texto = buffer.getvalue()
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
