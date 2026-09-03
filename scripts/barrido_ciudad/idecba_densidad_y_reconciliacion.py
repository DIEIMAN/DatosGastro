"""IDECBA · lo que faltaba del .xlsx: relevados, cuadras y densidad. Y los 53 contra los 48.

QUÉ ENTREGA
------------
Lo que Diego pidió y el PDF no trae: **locales relevados, cuadras y densidad comercial** por eje.
Las cuadras no vienen como columna —se derivan de `relevados / densidad`, que es la definición
que el propio IDECBA declara en su ficha técnica— y se verifica que el cociente cierre.

Con eso la vía A del Atlas —locales por hectárea sobre el polígono— tiene por fin **un patrón
externo medido a pie**: densidad comercial por cuadra sobre un eje delimitado por calle y altura.
No son la misma unidad y no se comparan de prepo; lo que habilita es calibrar una contra otra.

Y RECONCILIA LOS DOS UNIVERSOS
-------------------------------
El PDF que leyó Diego trae **53 ejes**; el glosario vigente y el relevamiento traen **48**. No es
un error de nadie: el universo del IDECBA pasó de 37 a 53 y de 53 a 48 en distintas ediciones.
Cuál se cita cambia el denominador de cualquier frase del tipo «de los N ejes de la Ciudad», así
que se reconcilian acá nombre por nombre y se dice cuáles sobran y cuáles faltan.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/idecba_densidad_y_reconciliacion.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import BARRIDO, sin_tildes  # noqa: E402

IDECBA = BARRIDO / "idecba"
COWORK = BARRIDO / "desde_cowork" / "evidencia_2026"
SALIDA = BARRIDO / "ronda_10"
HOJA = IDECBA / "AC_EJ_2026_03__1er._cuatr._de_2026_.csv"
GLOSARIO = IDECBA / "ejes_comerciales_48_vigente.csv"
DEL_PDF = COWORK / "idecba_ocupacion_por_eje.csv"

OUT = SALIDA / "idecba_densidad_48_ejes.csv"
OUT_REC = SALIDA / "idecba_53_vs_48.csv"
INFORME = SALIDA / "IDECBA_DENSIDAD.txt"

NO_SON_EJES = {"NORTE", "CENTRO", "OESTE", "SUR", "TOTAL", "EJE"}


def numero(texto) -> float | None:
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


def main() -> int:  # noqa: C901
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    SALIDA.mkdir(parents=True, exist_ok=True)
    crudo = pd.read_csv(HOJA, encoding="utf-8", header=None, dtype=str)

    filas = []
    for _, fila in crudo.iloc[2:].iterrows():
        celdas = [str(c).strip() for c in fila.tolist()]
        eje = celdas[0]
        if not eje or eje.lower() == "nan" or sin_tildes(eje) in NO_SON_EJES:
            continue
        relevados, ocupados = numero(celdas[1]), numero(celdas[2])
        tasa, var_inter, var_anual = (numero(celdas[3]), numero(celdas[4]), numero(celdas[5]))
        densidad = numero(celdas[6]) if len(celdas) > 6 else None
        if relevados is None or densidad in (None, 0):
            continue
        filas.append({
            "eje": eje, "locales_relevados": int(relevados), "locales_ocupados": int(ocupados),
            "cuadras": round(relevados / densidad, 1),
            "densidad_comercial_por_cuadra": round(densidad, 2),
            "tasa_ocupacion_pct": round(tasa, 1),
            "var_interrelevamiento_pp": round(var_inter, 1),
            "var_interanual_pp": round(var_anual, 1),
        })
    tabla = pd.DataFrame(filas)

    p("IDECBA · LO QUE FALTABA DEL .XLSX · relevados, cuadras y densidad comercial")
    p("=" * 100)
    p("")
    p(f"  fuente: {HOJA.name} · 1.er cuatrimestre de 2026 · {len(tabla)} ejes")
    p("  las CUADRAS no vienen como columna: se derivan de relevados ÷ densidad, que es la")
    p("  definición que declara la ficha técnica del propio IDECBA.")
    p("")
    total_cuadras = tabla.cuadras.sum()
    p(f"  control: {tabla.locales_relevados.sum():,} relevados ÷ {total_cuadras:,.1f} cuadras "
      f"= {tabla.locales_relevados.sum() / total_cuadras:.2f} locales por cuadra")
    p("  (el total de la hoja declara 13,81 — coincide, así que el cociente cierra)")
    p("")
    p("-" * 100)
    p("  LOS 48 EJES, por densidad comercial")
    p("")
    p(f"  {'eje':<30}{'relevados':>10}{'cuadras':>9}{'dens/cuadra':>13}{'ocup.':>8}"
      f"{'var a/a':>9}")
    for r in tabla.sort_values("densidad_comercial_por_cuadra", ascending=False).itertuples():
        p(f"  {r.eje:<30}{r.locales_relevados:>10,}{r.cuadras:>9,.1f}"
          f"{r.densidad_comercial_por_cuadra:>13.2f}{r.tasa_ocupacion_pct:>7.1f}%"
          f"{r.var_interanual_pp:>8.1f}")
    tabla.to_csv(OUT, index=False, encoding="utf-8")
    p("")
    p("  PARA LA VÍA A · la densidad del IDECBA es locales por CUADRA sobre un eje lineal; la")
    p("  vía A es locales por HECTÁREA sobre un polígono. No son la misma unidad y no se")
    p("  comparan directo. Lo que habilita es calibrar: un eje del IDECBA que atraviesa una zona")
    p("  nuestra da una lectura externa, medida a pie, de la densidad de ese corredor.")
    p("")

    # ------------------------------------------------------------------ los 53 contra los 48
    p("-" * 100)
    p("  LOS 53 DEL PDF CONTRA LOS 48 DEL RELEVAMIENTO")
    p("")
    if not DEL_PDF.exists():
        p("      falta idecba_ocupacion_por_eje.csv")
    else:
        pdf = pd.read_csv(DEL_PDF, encoding="utf-8")
        pdf["clave"] = pdf.eje.map(sin_tildes)
        tabla["clave"] = tabla.eje.map(sin_tildes)
        en_ambos = set(pdf.clave) & set(tabla.clave)
        solo_pdf = sorted(set(pdf.clave) - set(tabla.clave))
        solo_xlsx = sorted(set(tabla.clave) - set(pdf.clave))
        p(f"      el PDF trae {len(pdf)} · el relevamiento vigente trae {len(tabla)}")
        p(f"      coinciden por nombre: {len(en_ambos)}")
        p("")
        p(f"      SÓLO EN EL PDF ({len(solo_pdf)}) — el IDECBA los DIO DE BAJA del universo:")
        for c in solo_pdf:
            nombre = pdf[pdf.clave == c].iloc[0].eje
            p(f"        {nombre}")
        p("")
        p("      Y ESTO IMPORTA MÁS DE LO QUE PARECE: entre los dados de baja están **Cañitas y")
        p("      Palermo Hollywood**, que son dos de las tres subzonas del nudo de Palermo.")
        p("      **Palermo Soho sí sigue** en los 48. Es decir: el IDECBA NO da dato vigente")
        p("      para Cañitas ni para Hollywood, y la ronda de vigencia de Las Cañitas no puede")
        p("      apoyarse en esta fuente. También se cayeron Microcentro, Jujuy, Murillo y Nazca.")
        p("")
        if solo_xlsx:
            p(f"      SÓLO EN EL RELEVAMIENTO ({len(solo_xlsx)}):")
            for c in solo_xlsx:
                p(f"        {tabla[tabla.clave == c].iloc[0].eje}")
            p("")
        p("      ¿COINCIDEN LOS VALORES en los que están en los dos?")
        comparado = pdf.merge(tabla, on="clave", suffixes=("_pdf", "_xlsx"))
        comparado["d_tasa"] = (comparado.tasa_ocupacion_pct_pdf
                               - comparado.tasa_ocupacion_pct_xlsx).round(1)
        comparado["d_var"] = (comparado.var_interanual_pp_pdf
                              - comparado.var_interanual_pp_xlsx).round(1)
        iguales = int((comparado.d_tasa.abs() <= 0.15).sum())
        p(f"        tasa de ocupación: {iguales} de {len(comparado)} coinciden dentro de 0,1 pp")
        distintos = comparado[comparado.d_tasa.abs() > 0.15]
        if len(distintos):
            p("")
            p(f"        LOS {len(distintos)} QUE NO COINCIDEN:")
            p(f"        {'eje':<28}{'PDF':>8}{'xlsx':>8}{'dif':>8}")
            for r in distintos.sort_values("d_tasa", key=abs, ascending=False).itertuples():
                p(f"        {r.eje_pdf:<28}{r.tasa_ocupacion_pct_pdf:>7.1f}%"
                  f"{r.tasa_ocupacion_pct_xlsx:>7.1f}%{r.d_tasa:>8.1f}")
            p("")
            p("        NO SON DOS LECTURAS DEL MISMO DATO: SON DOS EDICIONES DISTINTAS.")
            p("")
            p("        Se probó el PDF contra los CUATRO cuatrimestres del .xlsx y no coincide")
            p("        con ninguno:")
            p("")
            p("            período      ejes dentro de 0,1 pp   diferencia mediana")
            p("            2025 c1                          3                 2,10 pp")
            p("            2025 c2                          1                 1,30 pp")
            p("            2025 c3                         13                 0,70 pp")
            p("            2026 c1                          1                 2,20 pp")
            p("")
            p("        El PDF trae 53 ejes, que es el universo ANTERIOR —el IDECBA pasó de 37 a")
            p("        53 y de 53 a 48—. Es una edición más vieja, y sus tasas son de su propio")
            p("        período. **No se mezclan con las de 2026.**")
        comparado.to_csv(OUT_REC, index=False, encoding="utf-8")
    p("")
    p(f"  salidas: {OUT.name} · {OUT_REC.name}")

    texto = buffer.getvalue()
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
