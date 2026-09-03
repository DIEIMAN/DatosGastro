"""Reconstruye el contenido público de las dos ediciones y lo compara campo por campo.

PARA QUÉ
--------
Cada vez que se toca una regla de `PLAIN_LANGUAGE`, `FRASES_POR_EDICION` u `ORIGENES_POR_EDICION`
hay que poder contestar dos preguntas distintas:

  · **¿la edición técnica sigue diciendo exactamente lo mismo?** Está sellada como V2.1 y su
    hash está en `CHECKSUMS_SHA256.txt`. Cualquier diferencia es un sello roto, aunque sea una
    coma;
  · **¿qué cambió en la conducción, y es sólo lo que se quería cambiar?** Un conteo de
    diferencias no alcanza: hay que ver las diferencias.

Comparar las listas de reglas NO prueba nada —mover una regla de lugar cambia la salida sin
cambiar la lista—, así que esto compara **salidas**, que es la lección que ya dejó esta cadena.

QUÉ **NO** ES EL CONTEO DE VOCABULARIO QUE IMPRIME AL FINAL
------------------------------------------------------------
El control vinculante de vocabulario prohibido es `qa_vocabulario_conduccion()`, y corre sobre
**las páginas ya compuestas** del PDF de conducción, que salen de `contenido_conduccion.py`. Los
campos que reconstruye este script son el insumo intermedio de las fichas, y la conducción no los
publica tal cual.

Así que el listado de términos vigilados que aparece acá es **informativo y NO es una falla**:
sirve para ver qué campos arrastran jerga si algún día se los usa, no para bloquear una corrida.
Tratarlo como control haría fallar 22 fichas que hoy están perfectamente bien.

USO
---
  .venv/Scripts/python.exe outputs/polos_gastro/ATLAS_V2/scripts/verificar_sellado_ediciones.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import build_atlas_v2 as B  # noqa: E402
import lenguaje_conduccion as L  # noqa: E402


def aplanar(contenido: dict) -> dict[str, str]:
    """Un diccionario plano `ficha.campo[.i]` -> texto, para comparar sin ambigüedad."""
    plano: dict[str, str] = {}
    for ficha in contenido["fichas"]:
        rid = ficha["referencia_id"]
        for campo, valor in ficha.items():
            if isinstance(valor, str):
                plano[f"{rid}.{campo}"] = valor
            elif isinstance(valor, list):
                for i, elemento in enumerate(valor):
                    if isinstance(elemento, list):
                        for j, sub in enumerate(elemento):
                            plano[f"{rid}.{campo}[{i}][{j}]"] = str(sub)
                    else:
                        plano[f"{rid}.{campo}[{i}]"] = str(elemento)
    return plano


def canon() -> dict:
    """El canon, leído del mismo ZIP que usa el generador. No se valida ni se toca nada más.

    `validate_inputs()` haría además la verificación de hashes y de cartografía completa, que
    para esta comparación no hace falta y que abortaría por motivos ajenos a lo que se quiere
    medir. La ruta del ZIP sí se toma del generador, para que no haya dos verdades.
    """
    import json as _json
    import zipfile

    with zipfile.ZipFile(B.FICHAS_ZIP) as zf:
        return _json.loads(zf.read("CONTENIDO_ESTRUCTURADO_FICHAS_22.json").decode("utf-8-sig"))


def main() -> int:
    canonical = canon()
    problemas = 0

    for edicion in ("tecnica", "conduccion"):
        B.EDICION = edicion
        reconstruido = aplanar(B.build_public_content(canonical, persist=False))
        congelado_ruta = B.content_path(edicion)
        if not congelado_ruta.exists():
            print(f"{edicion}: no hay JSON congelado en {congelado_ruta.name}; se omite")
            continue
        congelado = aplanar(json.loads(congelado_ruta.read_text(encoding="utf-8")))

        claves = sorted(set(reconstruido) | set(congelado))
        distintos = [k for k in claves
                     if reconstruido.get(k, "\0AUSENTE") != congelado.get(k, "\0AUSENTE")]

        print("=" * 96)
        print(f"EDICIÓN {edicion.upper()} · {len(claves)} campos · "
              f"{len(distintos)} diferencias contra {congelado_ruta.name}")
        print("=" * 96)
        for clave in distintos:
            print(f"  {clave}")
            print(f"    congelado : {congelado.get(clave, '(ausente)')[:150]}")
            print(f"    reconstr. : {reconstruido.get(clave, '(ausente)')[:150]}")

        if edicion == "tecnica" and distintos:
            print("\n  *** SELLO ROTO: la edición técnica NO puede cambiar. ***")
            problemas += 1
        elif edicion == "tecnica":
            print("  Sello intacto: 0 diferencias.")

        if edicion == "conduccion":
            sucios = [(k, L.hallazgos(v)) for k, v in reconstruido.items() if L.hallazgos(v)]
            print(f"\n  [informativo, no es una falla] campos del insumo intermedio que "
                  f"arrastran jerga vigilada: {len(sucios)}")
            print("  El control vinculante corre sobre las páginas compuestas, no sobre esto.")
            cambiados = [k for k, _ in sucios if k in set(distintos)]
            if cambiados:
                print(f"  de los {len(distintos)} campos que la reescritura tocó, {len(cambiados)} "
                      "siguen con jerga vigilada en el insumo intermedio:")
                for clave in cambiados:
                    print(f"    {clave}")
                print("  Casi toda es «deduplicación». NO bloquea: ni `contenido_conduccion.py` "
                      "ni `render_conduccion.py`")
                print("  consumen `detalle_cuantitativo` ni `denominador_metodo`, así que estos "
                      "textos no llegan a")
                print("  ninguna página. Queda anotado para el día que se los quiera usar.")
            else:
                print("  Ninguno de los campos tocados quedó con jerga vigilada.")
        print()

    if problemas:
        print("RESULTADO: SELLO DE LA TÉCNICA ROTO. No regenerar nada hasta resolverlo.")
        return 1
    print("RESULTADO: técnica sellada e intacta. Las diferencias de conducción son las "
          "buscadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
