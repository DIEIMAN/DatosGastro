"""Registra los tres documentos de la fase documental en el índice de `material_metodo`.

QUÉ HACE
--------
1. Agrega al `INDICE.csv` los tres archivos nuevos de `desde_cowork/evidencia_2026/`.
2. Convierte el **Anexo B** de `EDICION_TECNICA_FASE_DOCUMENTAL.md` en una tabla
   `tema → archivo` versionable, `correspondencia_fase_documental.csv`.

Y HACE UNA COSA MÁS, QUE ES LA QUE JUSTIFICA QUE ESTO SEA UN GUION
-------------------------------------------------------------------
El Anexo B no se transcribe: **se verifica archivo por archivo**. Una tabla de correspondencia que
nombra archivos que no existen es peor que no tener tabla, porque promete trazabilidad. Cada
archivo nombrado se busca en disco y la columna `existe` dice si está. Los que falten quedan
listados, no escondidos.

Es el mismo criterio de R12 aplicado a un índice en vez de a una geometría: una delimitación se
verifica midiéndola, y una correspondencia se verifica abriéndola.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/registrar_fase_documental.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import BARRIDO  # noqa: E402

COWORK = BARRIDO / "desde_cowork" / "evidencia_2026"
MATERIAL = BARRIDO / "material_metodo"
INDICE = MATERIAL / "INDICE.csv"
CORRESPONDENCIA = MATERIAL / "correspondencia_fase_documental.csv"
INFORME = MATERIAL / "REGISTRO_FASE_DOCUMENTAL.txt"

EDICION = COWORK / "EDICION_TECNICA_FASE_DOCUMENTAL.md"

NUEVOS = [
    {
        "archivo": "LAMINAS_PLAN_2026_POLOS_Y_CLUSTERS.md",
        "que_es": "Material para la presentación del Plan Gastronomía 2026: una lámina por "
                  "bloque, con título, la línea que lo sostiene y de dónde sale. ADVERTENCIA DE "
                  "USO que viaja con el archivo: sus números están calculados sobre la UNIÓN de "
                  "los polígonos, no sobre la suma de filas de la matriz de trabajo — sumar la "
                  "matriz duplica áreas.",
        "script_de_origen": "documento de cowork (no lo produce un script del repositorio)",
        "ruta_original": r"outputs\BARRIDO_CIUDAD_2026-08\desde_cowork\evidencia_2026\LAMINAS_PLAN_2026_POLOS_Y_CLUSTERS.md",
    },
    {
        "archivo": "EDICION_TECNICA_FASE_DOCUMENTAL.md",
        "que_es": "Parte segunda de la edición técnica: continúa EDICION_TECNICA_METODO.md "
                  "(secciones 0 a 26) con la fase documental. Su Anexo B es la tabla de "
                  "correspondencia tema → archivo, versionada aparte en "
                  "`correspondencia_fase_documental.csv`.",
        "script_de_origen": "documento de cowork (no lo produce un script del repositorio)",
        "ruta_original": r"outputs\BARRIDO_CIUDAD_2026-08\desde_cowork\evidencia_2026\EDICION_TECNICA_FASE_DOCUMENTAL.md",
    },
    {
        "archivo": "ATLAS_V3_SECCIONES_II_V_VI_IX.md",
        "que_es": "Secciones II, V, VI y IX del Atlas V3, con la propuesta de renumeración: el "
                  "borrador anterior tenía siete secciones y la fase documental agregó tres "
                  "objetos que ese esquema no contemplaba.",
        "script_de_origen": "documento de cowork (no lo produce un script del repositorio)",
        "ruta_original": r"outputs\BARRIDO_CIUDAD_2026-08\desde_cowork\evidencia_2026\ATLAS_V3_SECCIONES_II_V_VI_IX.md",
    },
]


def leer_anexo_b(texto: str) -> list[dict]:
    """Las filas de la tabla del Anexo B, con los archivos separados uno por uno."""
    inicio = texto.find("# Anexo B")
    if inicio < 0:
        raise SystemExit("EDICION_TECNICA_FASE_DOCUMENTAL.md no tiene un «# Anexo B»")
    bloque = texto[inicio:]
    fin = bloque.find("\n# ", 3)
    if fin > 0:
        bloque = bloque[:fin]
    filas = []
    for linea in bloque.splitlines():
        linea = linea.strip()
        if not linea.startswith("|") or linea.startswith("|---") or "| tema" in linea:
            continue
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        if len(celdas) < 2:
            continue
        tema, archivos = celdas[0], celdas[1]
        # Los archivos vienen entre backticks y separados por comas; algunos usan la forma
        # abreviada `_ronda_2.csv`, que es un sufijo del anterior y no un archivo.
        nombres = re.findall(r"`([^`]+)`", archivos)
        for nombre in nombres:
            filas.append({"tema": tema, "archivo": nombre})
    return filas


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    p("REGISTRO DE LA FASE DOCUMENTAL EN material_metodo")
    p("=" * 100)
    p("")

    # ------------------------------------------------------------------ 1 · el índice
    indice = pd.read_csv(INDICE)
    ya = set(indice.archivo)
    faltan = [n for n in NUEVOS if n["archivo"] not in ya]
    p(f"  INDICE.csv tenía {len(indice)} entradas.")
    for nuevo in NUEVOS:
        estado = "ya estaba" if nuevo["archivo"] in ya else "AGREGADO"
        presente = (COWORK / nuevo["archivo"]).exists()
        p(f"   {'✓' if presente else '✗'} {nuevo['archivo']:<44} [{estado}]"
          + ("" if presente else "  — NO ESTÁ EN DISCO"))
    if faltan:
        indice = pd.concat([indice, pd.DataFrame(faltan)], ignore_index=True)
        indice.to_csv(INDICE, index=False, encoding="utf-8")
    p(f"  INDICE.csv queda en {len(indice)} entradas.")
    p("")

    # ------------------------------------------------------------------ 2 · el Anexo B
    p("-" * 100)
    p("  ANEXO B · TABLA DE CORRESPONDENCIA tema → archivo, VERIFICADA CONTRA DISCO")
    p("")
    filas = leer_anexo_b(EDICION.read_text(encoding="utf-8"))
    for fila in filas:
        ruta = COWORK / fila["archivo"]
        fila["existe"] = "si" if ruta.exists() else "no"
        fila["ruta"] = str(ruta.relative_to(ROOT)) if ruta.exists() else ""
    tabla = pd.DataFrame(filas)
    tabla.to_csv(CORRESPONDENCIA, index=False, encoding="utf-8")

    hay = int((tabla.existe == "si").sum())
    no_hay = tabla[tabla.existe == "no"]
    p(f"  el Anexo B nombra {len(tabla)} archivos en {tabla.tema.nunique()} temas.")
    p(f"  están en disco: {hay} · NO están: {len(no_hay)}")
    p("")
    if len(no_hay):
        p("  LOS QUE NO ESTÁN. No se borran de la tabla: se marcan. Una correspondencia que")
        p("  nombra archivos ausentes promete una trazabilidad que no tiene, y esconderlos es")
        p("  peor que listarlos.")
        p("")
        for fila in no_hay.itertuples():
            p(f"      {fila.archivo:<46} ({fila.tema})")
        p("")
        p("  Los que tienen forma de sufijo —`_ronda_2.csv`— son abreviaturas de la entrada")
        p("  anterior en la tabla original, no archivos: se dejan marcados igual, porque una")
        p("  abreviatura en una tabla de trazabilidad tampoco resuelve.")
    p("")

    p("-" * 100)
    p(f"  {INDICE.name} · {len(indice)} entradas")
    p(f"  {CORRESPONDENCIA.name} · {len(tabla)} filas, con la columna `existe`")

    texto = buffer.getvalue()
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
