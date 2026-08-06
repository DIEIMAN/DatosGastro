"""Inventario de las formas que toma un nombre de calle en la base. El corte de la serie R8.

POR QUÉ EXISTE
--------------
Tres bugs de la misma familia en dos días —«INDEPENDENCIA AV.» vs «Avenida Independencia»,
«CALVO, CARLOS» vs «Carlos Calvo», «VEGA, NICETO, Cnel. AV.» con dos comas— no es mala suerte:
es que el normalizador se escribió caso por caso, a medida que cada bicho aparecía, **sin un
inventario previo de las formas que toma un nombre de calle en estas bases.**

Cada uno se arregló cuando apareció, y cada uno apareció porque alguien miró una tabla y notó la
misma calle dos veces. Los que nadie miró siguen ahí. Este script los busca todos de una.

Ninguno de estos bugs rompe nada ni tira excepción: devuelven dos filas plausibles donde hay una,
con la mitad de los locales cada una, y el ranking de calles sale mal sin avisar.

LAS DOS DIRECCIONES DEL ERROR, Y LA SEGUNDA ES LA QUE IMPORTA
----------------------------------------------------------------
  **sobre-plegado** · dos calles distintas caen en la misma clave. Es lo que Diego pidió listar:
                      «todas las variantes distintas que producen la misma calle normalizada».
                      La mayoría de los grupos son plegados CORRECTOS —ahí está el trabajo bien
                      hecho— y lo que hay que revisar son los pocos donde dos nombres distintos
                      terminaron juntos.
  **sub-plegado**   · la misma calle cae en dos claves. **Es el bug de la familia R8**, el que
                      partió a Niceto Vega en dos. No se ve mirando las claves: hay que buscar
                      pares de claves que probablemente sean la misma calle.

El script hace las dos. La segunda usa una clave más agresiva —sin marcadores en ninguna posición,
sin iniciales sueltas, con los tokens ordenados— **sólo para detectar candidatos**. Esa clave
agresiva NO se usa para contar: pliega de más a propósito, y lo que produce son sospechas para
mirar, no un resultado.

Google Places: 0 requests. No toca ningún dato: sólo lee y reporta.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/inventario_nombres_de_calle.py
"""
from __future__ import annotations

import io
import re
import sys
import unicodedata
import warnings
from collections import defaultdict
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import BASE  # noqa: E402
from polos_atributos_clases import OUT  # noqa: E402
from polos_foco_menor import calle  # noqa: E402

# Tratamientos y su forma larga. Para la clave AGRESIVA de detección, no para contar.
EQUIVALENCIAS = {
    "AV": "", "AVDA": "", "AVENIDA": "", "AVE": "",
    "CNEL": "CORONEL", "GRAL": "GENERAL", "TTE": "TENIENTE", "MCAL": "MARISCAL",
    "ALTE": "ALMIRANTE", "BRIG": "BRIGADIER", "INT": "INTENDENTE",
    "PTE": "PRESIDENTE", "PRES": "PRESIDENTE", "DR": "DOCTOR", "DRA": "DOCTORA",
    "PROF": "PROFESOR", "ING": "INGENIERO", "PBRO": "PRESBITERO", "MONS": "MONSENOR",
    "STA": "SANTA", "STO": "SANTO", "S": "SAN",
}
# Palabras que no distinguen una calle de otra y sólo agregan ruido a la comparación.
VACIAS = {"DE", "DEL", "LA", "EL", "LOS", "LAS", "Y", "CALLE", "PASAJE", "PJE", "DIAG", "DIAGONAL"}

# Código postal argentino pegado a la dirección: «BARTOLOME MITRE C1201AAX».
CPA = re.compile(r"^[A-Z]\d{4}[A-Z]{3}$")


def clave_agresiva(nombre: str) -> str:
    """Clave SÓLO para detectar sub-plegado. Pliega de más a propósito: no sirve para contar."""
    texto = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode()
    tokens = []
    for token in re.split(r"[\s.,]+", texto.upper()):
        token = token.strip(".")
        if not token or CPA.match(token):
            continue
        token = EQUIVALENCIAS.get(token, token)
        if not token or token in VACIAS:
            continue
        if len(token) == 1:            # inicial suelta: «Jose G. Artigas» vs «Jose Gervasio»
            continue
        tokens.append(token)
    return " ".join(sorted(tokens))


def parte_calle(direccion: str) -> str:
    """El pedazo de la dirección cruda que corresponde al nombre, antes de normalizar."""
    return re.sub(r"\s+\d.*$", "", str(direccion).split(";")[0]).strip()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    base = pd.read_csv(BASE, low_memory=False)
    direcciones = base.direccion_norm.dropna()

    crudas = direcciones.map(parte_calle)
    claves = direcciones.map(calle)
    tabla = pd.DataFrame({"cruda": crudas, "clave": claves})
    tabla = tabla[tabla.clave.str.len() > 2]

    p("INVENTARIO DE NOMBRES DE CALLE · las formas que toma una calle en esta base")
    p("=" * 100)
    p("")
    p(f"  {len(tabla)} direcciones con nombre de calle legible, de {len(base)} locales de la base.")
    p(f"  {tabla.cruda.nunique()} formas crudas distintas → {tabla.clave.nunique()} claves.")
    p("")
    p("  El inventario existe porque el normalizador se escribió caso por caso: cada bicho de la")
    p("  familia R8 se arregló cuando alguien lo vio en una tabla. Los que nadie miró siguen ahí.")
    p("")

    # ------------------------------------------------------------------ (A) sobre-plegado
    grupos = tabla.groupby("clave").cruda.value_counts()
    por_clave = defaultdict(list)
    for (clave_, cruda_), n in grupos.items():
        por_clave[clave_].append((n, cruda_))
    multiples = {k: sorted(v, reverse=True) for k, v in por_clave.items() if len(v) > 1}
    orden = sorted(multiples.items(), key=lambda kv: -sum(n for n, _ in kv[1]))

    p("-" * 100)
    p("  (A) VARIANTES DISTINTAS QUE PRODUCEN LA MISMA CLAVE · ordenadas por frecuencia")
    p("")
    p(f"      {len(multiples)} claves reciben más de una forma cruda "
      f"({sum(sum(n for n, _ in v) for v in multiples.values())} direcciones).")
    p("")
    p("      La mayoría son plegados CORRECTOS y ésa es la parte que funciona. Lo que hay que")
    p("      revisar acá son los pocos grupos donde dos nombres realmente distintos cayeron juntos.")
    p("")
    for clave_, variantes in orden[:60]:
        total = sum(n for n, _ in variantes)
        p(f"    {clave_}  ({total} direcciones, {len(variantes)} formas)")
        for n, cruda_ in variantes[:8]:
            p(f"        {n:>5}  {cruda_}")
        if len(variantes) > 8:
            p(f"        {'':>5}  … y {len(variantes) - 8} formas más")
    p("")

    # ------------------------------------------------------------------ (B) sub-plegado
    agresiva = {c: clave_agresiva(c) for c in tabla.clave.unique()}
    conteo_clave = tabla.clave.value_counts()
    sospechas = defaultdict(list)
    for clave_, agr in agresiva.items():
        if agr:
            sospechas[agr].append(clave_)
    sospechas = {k: v for k, v in sospechas.items() if len(v) > 1}
    orden_sospechas = sorted(
        sospechas.items(), key=lambda kv: -sum(conteo_clave.get(c, 0) for c in kv[1]))

    p("-" * 100)
    p("  (B) CLAVES DISTINTAS QUE PROBABLEMENTE SEAN LA MISMA CALLE · el bug de la familia R8")
    p("")
    p(f"      {len(sospechas)} grupos sospechosos, "
      f"{sum(len(v) for v in sospechas.values())} claves involucradas, "
      f"{sum(sum(conteo_clave.get(c, 0) for c in v) for v in sospechas.values())} direcciones.")
    p("")
    p("      Cada grupo es una calle que HOY se cuenta como dos o más. Es exactamente lo que le")
    p("      pasó a Niceto Vega: la misma calle en dos filas, con la mitad de los locales cada una.")
    p("")
    for agr, lista in orden_sospechas[:70]:
        total = sum(conteo_clave.get(c, 0) for c in lista)
        p(f"    {total:>5} direcciones repartidas en {len(lista)} claves:")
        for clave_ in sorted(lista, key=lambda c: -conteo_clave.get(c, 0)):
            p(f"        {conteo_clave.get(clave_, 0):>5}  {clave_}")
    p("")

    # ------------------------------------------------------------------ (C) patologías puntuales
    p("-" * 100)
    p("  (C) PATOLOGÍAS PUNTUALES DE LA FORMA CRUDA")
    p("")

    mojibake = tabla[tabla.cruda.str.contains("Ã|Â|â€|Ãƒ", regex=True, na=False)]
    p(f"      · MOJIBAKE: {len(mojibake)} direcciones. El texto pasó dos veces por una")
    p("        conversión equivocada de codificación y la ñ quedó como una ristra de símbolos.")
    for cruda_, n in mojibake.cruda.value_counts().head(10).items():
        p(f"          {n:>5}  {cruda_!r}  →  clave {calle(cruda_)!r}")
    p("")

    con_cpa = tabla[tabla.cruda.str.contains(r"\b[A-Z]\d{4}[A-Z]{3}\b", regex=True, na=False)]
    p(f"      · CÓDIGO POSTAL pegado al nombre: {len(con_cpa)} direcciones.")
    for cruda_, n in con_cpa.cruda.value_counts().head(6).items():
        p(f"          {n:>5}  {cruda_!r}  →  clave {calle(cruda_)!r}")
    p("")

    cola = tabla[tabla.clave.str.match(r".*\s(DE|DEL|Y|LA|EL)$", na=False)]
    p(f"      · CLAVE TERMINADA EN CONECTOR: {len(cola)} direcciones. Es la marca de un nombre")
    p("        recortado — «11 de Septiembre de 1888» pierde el año y queda «11 DE SEPTIEMBRE DE».")
    for clave_, n in cola.clave.value_counts().head(10).items():
        p(f"          {n:>5}  {clave_!r}")
    p("")

    unicas = conteo_clave[conteo_clave == 1]
    p(f"      · CLAVES CON UNA SOLA DIRECCIÓN: {len(unicas)} de {tabla.clave.nunique()}. No son")
    p("        todas errores —hay calles con un solo local— pero es donde se esconde el resto.")
    p("")

    # ------------------------------------------------------------------ salida tabular
    filas_a = [{"tipo": "sobre_plegado", "clave": k, "direcciones": sum(n for n, _ in v),
                "n_formas": len(v), "formas": " · ".join(f"{c} ({n})" for n, c in v[:10])}
               for k, v in orden]
    filas_b = [{"tipo": "sub_plegado_sospechado",
                "clave": " | ".join(sorted(v, key=lambda c: -conteo_clave.get(c, 0))),
                "direcciones": sum(conteo_clave.get(c, 0) for c in v),
                "n_formas": len(v),
                "formas": " · ".join(f"{c} ({conteo_clave.get(c, 0)})"
                                     for c in sorted(v, key=lambda c: -conteo_clave.get(c, 0)))}
               for _, v in orden_sospechas]
    inventario = pd.DataFrame(filas_a + filas_b)

    p("=" * 100)
    p(f"  {len(filas_a)} grupos de sobre-plegado · {len(filas_b)} grupos de sub-plegado sospechado")
    p("=" * 100)
    p("")
    p("  QUÉ SE HACE CON ESTO: el bloque (B) es la lista de trabajo. Cada grupo es una calle")
    p("  contada dos veces hoy. Lo que se puede arreglar mecánicamente —mojibake, marcadores en")
    p("  cualquier posición, tratamientos abreviados, códigos postales— se arregla en `calle()`")
    p("  con su caso en el test. Lo que necesita un callejero canónico —una inicial contra un")
    p("  nombre completo— NO se arregla adivinando: se anota y espera a la fuente.")
    p("")

    salida = buffer.getvalue()
    (OUT / "INVENTARIO_NOMBRES_DE_CALLE.txt").write_text(salida, encoding="utf-8")
    inventario.to_csv(OUT / "inventario_nombres_de_calle.csv", index=False, encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
