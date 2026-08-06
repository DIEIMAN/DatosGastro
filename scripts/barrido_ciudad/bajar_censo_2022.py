"""Censo Nacional de Población, Hogares y Viviendas 2022 (INDEC): el recorte de CABA.

QUÉ ES Y PARA QUÉ ENTRA
-----------------------
**No es una fuente de locales y no aporta ni una fila a la base.** Entra como *denominador*, igual
que el tabulado del Censo Económico que Diego está gestionando (§11 del esquema), pero mide otra
cosa: población, no establecimientos. Sirve para el indicador «locales cada mil habitantes», que
es interpretable por cualquiera y sirve para presentar, y no sirve para diagnosticar cobertura
—la gastronomía se ubica donde hay oficinas y turismo, no donde hay camas—.

Licencia **CC BY 4.0**, publicado en datos.gob.ar. Redistribuible con atribución.

QUÉ BAJA, Y POR QUÉ LOS DOS ARCHIVOS
------------------------------------
1. `radios-censales-2022.zip` — shapefile de los 66.502 radios censales del país. Trae el campo
   `POB_TOT_P`: población total en viviendas particulares por radio. Es todo lo que hace falta
   para el denominador, y además la geometría para repartir por barrio.

2. `02-caba-2022.zip` — las tablas por radio de CABA (persona, hogar, vivienda). **No son
   microdatos**: son conteos ya agregados por radio × variable × categoría, así que no hay ningún
   dato individual. Se baja por un solo motivo: **control cruzado**. La suma de `PERSONA_P02`
   (sexo registrado al nacer, que aplica a toda la población) tiene que dar exactamente el mismo
   total que `POB_TOT_P` del shapefile. Son dos archivos distintos del mismo organismo y hacerlos
   coincidir es gratis; darlo por sentado, no.

EL DENOMINADOR ES POBLACIÓN EN VIVIENDAS PARTICULARES, Y HAY QUE DECIRLO
-----------------------------------------------------------------------
Los dos archivos dan 3.095.454 para CABA. El total de la Ciudad publicado por el INDEC para 2022
es más alto: la diferencia es la población en **viviendas colectivas** (hospitales, hoteles,
geriátricos, institutos), que la base por radio no distribuye. Para una razón «locales cada mil
habitantes» la diferencia es de menos del 1 % y no cambia ninguna lectura, pero el rótulo tiene
que decir «en viviendas particulares» y no «población de la Ciudad».

Los archivos crudos quedan fuera de Git (`.gitignore`): pesan 66 MB y se rebajan con este script.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/bajar_censo_2022.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
DESTINO = ROOT / "outputs" / "fuentes_externas" / "censo"

BASE = "https://infra.datos.gob.ar/catalog/indec/dataset"
ARCHIVOS = {
    "radios-censales-2022.zip": f"{BASE}/50/distribution/50.3/download/radios-censales-2022.zip",
    "02-caba-2022.zip": f"{BASE}/48/distribution/48.1/download/02-caba-2022.zip",
}

# Lo que se espera de cada archivo, escrito antes de bajarlo. Un cambio de tamaño grande significa
# que el INDEC republicó la base, y eso se mira antes de recalcular nada.
TAMANIOS_ESPERADOS = {
    "radios-censales-2022.zip": 55_698_883,
    "02-caba-2022.zip": 10_866_045,
}


def bajar(nombre: str, url: str) -> Path:
    destino = DESTINO / nombre
    if destino.exists():
        print(f"  ya está: {nombre} ({destino.stat().st_size / 1e6:.1f} MB)")
        return destino
    print(f"  bajando {nombre} …")
    with requests.get(url, timeout=900, stream=True) as respuesta:
        respuesta.raise_for_status()
        with destino.open("wb") as fh:
            for bloque in respuesta.iter_content(1 << 20):
                fh.write(bloque)
    print(f"  ok: {nombre} ({destino.stat().st_size / 1e6:.1f} MB)")
    return destino


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    print("Censo Nacional 2022 · INDEC · CC BY 4.0 · recorte de CABA")
    avisos = []
    for nombre, url in ARCHIVOS.items():
        ruta = bajar(nombre, url)
        esperado = TAMANIOS_ESPERADOS[nombre]
        real = ruta.stat().st_size
        if real != esperado:
            avisos.append(f"{nombre}: {real:,} bytes, se esperaban {esperado:,}")
    if avisos:
        print("\nEl archivo publicado cambió de tamaño. No se recalcula nada hasta mirarlo:")
        for aviso in avisos:
            print(f"  - {aviso}")
        return 1
    print(f"\nen {DESTINO.relative_to(ROOT)} — el uso está en parejidad_cobertura.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
