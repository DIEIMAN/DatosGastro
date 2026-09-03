"""Geocodificacion compartida de los estudios de rubro, contra USIG.

USIG (servicios.usig.buenosaires.gob.ar) es el normalizador y geocodificador oficial del
GCBA: fuente publica, gratuita y publicable. No hay API paga ni scraping en juego.

Por que una cache aparte
------------------------
El geocodificador del pipeline (`src/geocode_usig.py`) escribe en
`data/processed/geo_cache.csv`, que es superficie protegida por el guardrail 2. Los
estudios de rubro **leen** esa cache y la de `dim_ubicacion`, pero escriben en la suya:
`data/geo/geo_cache_rubros.csv`. Asi se acumula geocodificacion entre rubros sin tocar
una sola fila del pipeline.

El motor de consulta es el del pipeline: se importa `geocode_address` de
`src/geocode_usig.py` en vez de reimplementarlo, para que la normalizacion de direcciones
F02, el control de comuna y los criterios de seleccion sean exactamente los mismos.

Uso
---
    python -m scripts.shared.fuentes_locales.geo --desde outputs/panaderias/panaderias_maestro.csv
    python -m scripts.shared.fuentes_locales.geo --desde <csv> --limit 50   # prueba corta
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Iterable

from .texto import normalizar

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "data" / "processed"
CACHE_RUBROS = ROOT / "data" / "geo" / "geo_cache_rubros.csv"

# Caches de solo lectura del pipeline (guardrail 2: se leen, no se escriben).
CACHES_LECTURA = [PROC / "geo_cache.csv", PROC / "dim_ubicacion.csv"]

COLUMNAS_CACHE = [
    "direccion_original", "direccion_consulta", "direccion_candidatas",
    "direccion_normalizada", "latitud", "longitud", "barrio_usig", "comuna_usig",
    "comuna_fuente", "coincide_comuna", "precision", "estado", "calidad_geo",
    "criterio_seleccion", "fecha_consulta",
]


def _a_float(valor) -> float | None:
    try:
        v = float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return None
    return v if v else None


def _leer_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
        return list(csv.DictReader(fh))


def cargar_cache() -> dict[str, tuple[float, float, str]]:
    """Direccion normalizada -> (lat, lon, calidad). Primero el pipeline, despues la propia.

    La cache de rubros va ultima a proposito: si una direccion ya estaba resuelta por el
    pipeline, gana esa, que es la que usan las demas salidas del proyecto.
    """
    lookup: dict[str, tuple[float, float, str]] = {}
    for path in CACHES_LECTURA + [CACHE_RUBROS]:
        for fila in _leer_csv(path):
            clave = normalizar(fila.get("direccion_original", ""))
            lat, lon = _a_float(fila.get("latitud")), _a_float(fila.get("longitud"))
            if clave and lat and lon and clave not in lookup:
                lookup[clave] = (lat, lon, fila.get("calidad_geo") or "usig_cache")
    return lookup


def direcciones_pendientes(direcciones: Iterable[str]) -> list[str]:
    """Las que no resuelve ninguna cache, sin repetir y en orden estable."""
    cache = cargar_cache()
    vistas, pendientes = set(), []
    for direccion in direcciones:
        direccion = (direccion or "").strip()
        clave = normalizar(direccion)
        if not clave or clave in cache or clave in vistas:
            continue
        vistas.add(clave)
        pendientes.append(direccion)
    return pendientes


def geocodificar(direcciones: list[str], *, limit: int | None = None,
                 verbose: bool = True) -> list[dict]:
    """Consulta USIG para las direcciones pendientes y las agrega a la cache de rubros.

    Ritmo prudente: el motor del pipeline ya espacia las consultas 0,25 s entre
    candidatas de una misma direccion.
    """
    import requests  # se importa aca para no exigirlo cuando solo se lee la cache

    sys.path.insert(0, str(ROOT / "src"))
    from geocode_usig import geocode_address  # noqa: E402

    pendientes = direcciones_pendientes(direcciones)
    if limit:
        pendientes = pendientes[:limit]
    if not pendientes:
        if verbose:
            print("no hay direcciones pendientes: la cache ya las cubre")
        return []

    if verbose:
        print(f"consultando USIG por {len(pendientes)} direcciones nuevas")
    sesion = requests.Session()
    filas = []
    for i, direccion in enumerate(pendientes, 1):
        filas.append(geocode_address(direccion, session=sesion).as_row())
        if verbose and (i % 50 == 0 or i == len(pendientes)):
            resueltas = sum(1 for f in filas if f["latitud"])
            print(f"  {i}/{len(pendientes)} consultadas, {resueltas} con coordenadas")

    _guardar(filas)
    return filas


def _guardar(filas: list[dict]) -> None:
    """Agrega filas nuevas a la cache de rubros sin pisar lo ya resuelto."""
    CACHE_RUBROS.parent.mkdir(parents=True, exist_ok=True)
    existentes = _leer_csv(CACHE_RUBROS)
    ya = {normalizar(f.get("direccion_original", "")) for f in existentes}
    nuevas = [f for f in filas if normalizar(f.get("direccion_original", "")) not in ya]
    with open(CACHE_RUBROS, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS_CACHE, extrasaction="ignore")
        w.writeheader()
        w.writerows(existentes + nuevas)


def _cli(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Geocodifica con USIG las direcciones que faltan.")
    ap.add_argument("--desde", required=True, help="CSV con las direcciones (ej. un maestro de rubro)")
    ap.add_argument("--columna", default="direccion_original", help="columna de direcciones")
    ap.add_argument("--limit", type=int, default=None, help="tope de direcciones nuevas a consultar")
    ap.add_argument("--solo-faltantes", action="store_true",
                    help="solo las filas del CSV que no traen lat")
    args = ap.parse_args(argv)

    filas = _leer_csv(Path(args.desde))
    if args.solo_faltantes:
        filas = [f for f in filas if not (f.get("lat") or "").strip()]
    direcciones = [f.get(args.columna, "") for f in filas]
    print(f"{len(filas)} filas leidas de {args.desde}")

    resultados = geocodificar(direcciones, limit=args.limit)
    if resultados:
        con_geo = sum(1 for r in resultados if r["latitud"])
        print(f"\nresueltas {con_geo} de {len(resultados)} ({con_geo / len(resultados):.1%})")
        estados: dict[str, int] = {}
        for r in resultados:
            estados[r["estado"]] = estados.get(r["estado"], 0) + 1
        for estado, n in sorted(estados.items(), key=lambda x: -x[1]):
            print(f"  {estado}: {n}")
        print(f"cache: {CACHE_RUBROS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
