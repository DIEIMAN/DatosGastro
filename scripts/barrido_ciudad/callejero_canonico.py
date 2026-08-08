"""El callejero oficial parte la misma calle en varios nombres. Acá se canonicaliza, y se prueba.

POR QUÉ ESTE MÓDULO EXISTE
---------------------------
Tres veces, en tres rondas distintas, una búsqueda por nombre devolvió **medio corredor** y el
resultado siguió adelante sin error:

    «esq» adentro de ESQUIÚ            un normalizador que abreviaba «esquina» partía el nombre
    INDEPENDENCIA AV. / INDEPENDENCIA  dos registros para la misma avenida
    GARCIA DEL RIO AV. / GARCIA DEL RIO el corredor de R20, empalmado en Pinto

A la tercera deja de ser un bicho y pasa a ser **una propiedad del callejero**: el nombre oficial
de un eje puede cambiar a lo largo del eje. Un módulo que lo ignore va a producir tramos cortos,
delimitaciones sin longitud y anclajes fuera del eje, siempre en silencio.

QUÉ HACE Y QUÉ NO
------------------
`familias()` agrupa nombres que (1) comparten raíz al normalizar el sufijo de tipo de vía —AV.,
AVENIDA, PJE., PASAJE, DIAG.— **y** (2) están **geométricamente en contacto**. Las dos
condiciones juntas, porque ninguna alcanza sola:

    sólo la raíz     uniría CONDE con CONDE (otra ciudad) o ALBERDI con ALBERDI AV. estando a
                     tres kilómetros: mismo nombre, ejes distintos
    sólo el contacto uniría cualquier par de calles que se cruzan, que son casi todas

`eje_canonico()` devuelve el eje completo de una calle, uniendo su familia. Es lo que había que
usar en la ronda 8 y no se usó.

**No renombra nada en disco.** El callejero oficial no se toca: la canonicalización es una vista.

EL TEST
-------
`test_callejero_canonico.py`, al lado. Lleva **casos negativos**, que son los que importan: un
test que sólo prueba que los tres casos conocidos se unen pasaría también con una función que une
todo con todo.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import geopandas as gpd
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import CALLEJERO, CRS_METRICO, sin_tildes  # noqa: E402

# Sufijos que designan el TIPO de vía, no su nombre. Se sacan para comparar raíces.
SUFIJOS = r"\b(AV|AVDA|AVENIDA|PJE|PASAJE|DIAG|DIAGONAL|BLVD|BOULEVARD|CALLE)\b"

# Contacto: dos piezas de la misma raíz que se tocan a menos de esto son el mismo corredor. Una
# esquina real mide menos; 25 m cubre el ancho de una avenida sin unir cuadras distintas.
CONTACTO_M = 25.0


def raiz(nombre: str) -> str:
    """El nombre sin el sufijo de tipo de vía. «GARCIA DEL RIO AV.» → «GARCIA DEL RIO»."""
    limpio = sin_tildes(nombre)
    return re.sub(r"\s+", " ", re.sub(SUFIJOS, " ", limpio)).strip()


def cargar(ruta: Path | None = None) -> gpd.GeoDataFrame:
    capa = gpd.read_file(ruta or CALLEJERO).to_crs(CRS_METRICO)
    capa["clave"] = capa.nomoficial.map(sin_tildes)
    capa["raiz"] = capa.nomoficial.map(raiz)
    return capa


def familias(callejero: gpd.GeoDataFrame) -> dict[str, set[str]]:
    """{clave → conjunto de claves del mismo corredor}. Sólo une lo que además se toca."""
    salida: dict[str, set[str]] = {}
    for r, bloque in callejero.groupby("raiz"):
        claves = sorted(set(bloque.clave))
        if len(claves) == 1:
            salida[claves[0]] = {claves[0]}
            continue
        geoms = {c: unary_union(list(bloque[bloque.clave == c].geometry)) for c in claves}
        # componentes conexas por contacto
        pendientes, grupos = set(claves), []
        while pendientes:
            grupo = {pendientes.pop()}
            creciendo = True
            while creciendo:
                creciendo = False
                for otra in sorted(pendientes):
                    if any(geoms[otra].distance(geoms[g]) <= CONTACTO_M for g in grupo):
                        grupo.add(otra)
                        pendientes.discard(otra)
                        creciendo = True
            grupos.append(grupo)
        for grupo in grupos:
            for c in grupo:
                salida[c] = set(grupo)
    return salida


def eje_canonico(callejero: gpd.GeoDataFrame, nombre: str,
                 mapa: dict[str, set[str]] | None = None):
    """El eje COMPLETO de una calle, uniendo los nombres oficiales de su familia."""
    clave = sin_tildes(nombre)
    mapa = mapa if mapa is not None else familias(callejero)
    claves = mapa.get(clave, {clave})
    piezas = list(callejero[callejero.clave.isin(claves)].geometry)
    return unary_union(piezas) if piezas else None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    callejero = cargar()
    mapa = familias(callejero)
    partidas = {c: f for c, f in mapa.items() if len(f) > 1}
    grupos = {frozenset(f) for f in partidas.values()}
    print(f"callejero: {len(callejero):,} segmentos · {callejero.clave.nunique():,} nombres")
    print(f"familias con más de un nombre oficial: {len(grupos)}")
    print()
    for grupo in sorted(grupos, key=lambda g: sorted(g)[0]):
        largos = {c: unary_union(list(callejero[callejero.clave == c].geometry)).length
                  for c in sorted(grupo)}
        total = sum(largos.values())
        print(f"  {' + '.join(sorted(grupo))}")
        for c, m in sorted(largos.items()):
            print(f"      {c:<44}{m:>9,.0f} m  ({m / total * 100:.0f} % del corredor)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
