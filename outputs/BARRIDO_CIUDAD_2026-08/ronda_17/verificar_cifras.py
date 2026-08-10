# -*- coding: utf-8 -*-
"""Recorre los documentos, encuentra cada cifra y avisa cuál no coincide con la canónica.

QUÉ HACE
--------
Lee `cifras_canonicas.json`, recorre los `.md` del atlas y, para cada cifra, busca sus patrones.
Cada patrón captura el número **en su contexto**, en un grupo llamado `valor`. Después compara.
El resultado son tres listas:

    COINCIDE      el texto dice lo mismo que la fuente
    NO COINCIDE   el texto dice otra cosa, con archivo, línea y las dos cifras
    SIN MENCIÓN   la cifra no aparece en ningún documento: no es un error, es información

**Entiende números escritos con letra**, porque el atlas los usa: «Dieciocho de los cuarenta y un
polos» es exactamente una de las frases que hay que atrapar, y con un patrón numérico no se
atrapa. Los cardinales del cero al cien están en `PALABRAS`.

Y **entiende el formato de acá**: `3.128,5` es tres mil ciento veintiocho con cinco. Leerlo con
`float()` da 3.128 y el control pasaría por error.

CÓMO SE USA
-----------
    .venv/Scripts/python.exe outputs/BARRIDO_CIUDAD_2026-08/ronda_17/verificar_cifras.py

    --solo Z          limita a los documentos cuyo nombre contenga Z
    --json            escribe verificacion_cifras.json además de imprimir
    --estricto        sale con código 1 si hay alguna discrepancia (para un hook o CI)

QUÉ NO HACE, Y ES A PROPÓSITO
------------------------------
**No corrige nada.** Un reemplazo automático sobre prosa cambia frases que dicen algo distinto de
lo que el patrón cree —«la cifra correcta es X» y «el documento decía X» llevan el mismo número y
sólo una hay que tocar—. Este script señala; la corrección la firma quien escribe.

Cero requests.
"""

import argparse
import json
import re
import sys
from pathlib import Path

SALIDA = Path(__file__).resolve().parent
BASE = SALIDA.parents[0]
ROOT = SALIDA.parents[2]
CANONICAS = SALIDA / "cifras_canonicas.json"

# Los documentos del atlas. Se declara la lista en vez de barrer todo `outputs/`: un archivo de
# trabajo de una ronda vieja puede tener una cifra vieja a propósito, y marcarla sería ruido.
DOCUMENTOS = [
    BASE / "documento" / "ATLAS_V3_DOCUMENTO.md",
    *sorted((BASE / "desde_cowork").glob("*.md")),
    *sorted((BASE / "desde_cowork" / "evidencia_2026").glob("*.md")),
]

PALABRAS = {
    "cero": 0, "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12,
    "trece": 13, "catorce": 14, "quince": 15, "dieciseis": 16, "diecisiete": 17,
    "dieciocho": 18, "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintidos": 22,
    "veintitres": 23, "veinticuatro": 24, "veinticinco": 25, "veintiseis": 26,
    "veintisiete": 27, "veintiocho": 28, "veintinueve": 29, "treinta": 30, "cuarenta": 40,
    "cincuenta": 50, "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90, "cien": 100,
}
# Compuestos que el atlas escribe con letra: «cuarenta y un», «treinta y nueve».
for _d, _dv in (("treinta", 30), ("cuarenta", 40), ("cincuenta", 50), ("sesenta", 60),
                ("setenta", 70), ("ochenta", 80), ("noventa", 90)):
    for _u, _uv in (("un", 1), ("uno", 1), ("una", 1), ("dos", 2), ("tres", 3), ("cuatro", 4),
                    ("cinco", 5), ("seis", 6), ("siete", 7), ("ocho", 8), ("nueve", 9)):
        PALABRAS[f"{_d} y {_u}"] = _dv + _uv


def sin_tildes(texto):
    import unicodedata
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()


def a_numero(bruto):
    """Convierte «3.128,5», «12.688», «dieciocho» o «cuarenta y un» en un número.

    Devuelve None si no es un número: un patrón puede capturar una palabra cualquiera y eso no
    es una discrepancia, es un patrón que enganchó de más.
    """
    texto = str(bruto).strip().strip("*").strip()
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})*(?:,\d+)?", texto):
        return float(texto.replace(".", "").replace(",", "."))
    if re.fullmatch(r"\d+(?:,\d+)?", texto):
        return float(texto.replace(",", "."))
    return PALABRAS.get(sin_tildes(texto))


def igual(a, b):
    """Compara con la tolerancia del redondeo con que se publican estas cifras.

    No es laxitud: el documento publica «893,5» y la suma da 893,4 porque suma valores ya
    redondeados. Media unidad de la última posición escrita es exactamente esa diferencia, y
    todo lo que la pase es una cifra distinta, no un redondeo.
    """
    return abs(a - b) <= 0.05 * max(1.0, abs(b)) ** 0 + 0.05


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--solo", default=None, help="limita a documentos cuyo nombre contenga esto")
    ap.add_argument("--json", action="store_true", help="escribe verificacion_cifras.json")
    ap.add_argument("--estricto", action="store_true", help="código 1 si hay discrepancias")
    args = ap.parse_args()

    canon = json.loads(CANONICAS.read_text(encoding="utf-8"))
    cifras = canon["cifras"]
    documentos = [d for d in DOCUMENTOS if d.exists()]
    if args.solo:
        documentos = [d for d in documentos if args.solo.lower() in d.name.lower()]

    print("=" * 98)
    print("VERIFICACIÓN DE CIFRAS · el texto contra la fuente")
    print("=" * 98)
    print(f"canónicas de {canon['generado']} · {len(cifras)} cifras · "
          f"{len(documentos)} documentos\n")

    coinciden, discrepan, sin_pattern, no_numericas = [], [], [], []
    for nombre, c in cifras.items():
        patrones = c.get("patrones_en_el_texto") or []
        if not patrones:
            sin_pattern.append(nombre)
            continue
        esperado = float(c["valor"])
        hallazgos = []
        for doc in documentos:
            texto = doc.read_text(encoding="utf-8")
            lineas_hasta = None
            for patron in patrones:
                for m in re.finditer(patron, texto):
                    bruto = m.groupdict().get("valor")
                    if bruto is None:
                        continue
                    valor = a_numero(bruto)
                    if valor is None:
                        no_numericas.append((nombre, doc.name, bruto))
                        continue
                    if lineas_hasta is None:
                        lineas_hasta = texto
                    linea = texto.count("\n", 0, m.start()) + 1
                    hallazgos.append(dict(archivo=str(doc.relative_to(ROOT)).replace("\\", "/"),
                                          linea=linea, encontrado=bruto, valor=valor,
                                          ok=igual(valor, esperado),
                                          contexto=m.group(0).replace("\n", " ")[:100]))
        malos = [h for h in hallazgos if not h["ok"]]
        buenos = [h for h in hallazgos if h["ok"]]
        if not hallazgos:
            sin_pattern.append(nombre)
        elif malos:
            discrepan.append((nombre, c, buenos, malos))
        else:
            coinciden.append((nombre, c, buenos))

    # ---- salida ---------------------------------------------------------------------------
    print("-" * 98)
    print(f"NO COINCIDEN · {len(discrepan)} cifras")
    print("-" * 98)
    for nombre, c, buenos, malos in discrepan:
        print(f"\n  {nombre}   canónico: {c['valor']} {c['unidad']}   "
              f"({len(buenos)} menciones bien, {len(malos)} mal)")
        print(f"      fuente: {c['archivo_del_que_sale']}")
        vistos = set()
        for h in malos:
            k = (h["archivo"], h["encontrado"])
            if k in vistos:
                continue
            vistos.add(k)
            print(f"      {h['archivo']}:{h['linea']}  dice «{h['encontrado']}»  "
                  f"y la fuente dice «{c['valor']}»")
            print(f"          …{h['contexto']}…")
        if c.get("nota"):
            print(f"      nota: {c['nota']}")

    print("\n" + "-" * 98)
    print(f"COINCIDEN · {len(coinciden)} cifras")
    print("-" * 98)
    for nombre, c, buenos in coinciden:
        archivos = sorted({h["archivo"].split("/")[-1] for h in buenos})
        print(f"  {nombre:<34}{str(c['valor']):>12} {c['unidad']:<12} "
              f"{len(buenos)} menciones en {len(archivos)} documentos")

    if sin_pattern:
        print("\n" + "-" * 98)
        print(f"SIN MENCIÓN EN NINGÚN DOCUMENTO · {len(sin_pattern)} cifras")
        print("-" * 98)
        print("  No es un error: la cifra existe y el texto todavía no la usa.")
        for nombre in sin_pattern:
            print(f"      {nombre:<34}{str(cifras[nombre]['valor']):>12} "
                  f"{cifras[nombre]['unidad']}")

    if no_numericas:
        print("\n" + "-" * 98)
        print(f"PATRONES QUE ENGANCHARON ALGO QUE NO ES UN NÚMERO · {len(no_numericas)}")
        print("-" * 98)
        print("  Hay que apretar el patrón en cifras_canonicas.py; no son discrepancias.")
        for nombre, archivo, bruto in sorted(set(no_numericas))[:20]:
            print(f"      {nombre:<34}{archivo:<44}«{bruto}»")

    print("\n" + "=" * 98)
    print(f"RESULTADO: {len(discrepan)} cifras del texto no coinciden con su fuente, "
          f"{len(coinciden)} sí, {len(sin_pattern)} sin mención")
    print("=" * 98)

    if args.json:
        destino = SALIDA / "verificacion_cifras.json"
        destino.write_text(json.dumps(dict(
            fecha_de_la_verificacion=canon["generado"],
            documentos=[str(d.relative_to(ROOT)).replace("\\", "/") for d in documentos],
            no_coinciden={n: dict(canonico=c["valor"], unidad=c["unidad"],
                                  fuente=c["archivo_del_que_sale"], menciones_mal=m,
                                  menciones_bien=len(b))
                          for n, c, b, m in discrepan},
            coinciden={n: c["valor"] for n, c, _ in coinciden},
            sin_mencion=sin_pattern,
        ), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nEscrito: {destino.name}")

    if args.estricto and discrepan:
        sys.exit(1)


if __name__ == "__main__":
    main()
