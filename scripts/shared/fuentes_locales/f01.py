"""Lector unico de F01 (oferta y establecimientos gastronomicos, GCBA).

Un solo archivo, delimitador ";", codificacion cp1252 (no es UTF-8: se verifico sobre
`data/raw/f01_oferta_establecimientos_gastronomicos.csv`). Trae coordenadas ya
cargadas, con coma decimal.

Privacidad (guardrail 7): `telefono` y `mail` no se exponen. Se descartan en el parseo.

F01 es un relevamiento de oferta registrada, con su propia fecha de corte: no es un
padron de locales activos ni es comparable fila a fila con F02.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

from .texto import clave_columna, reparar_mojibake

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
ARCHIVO_F01 = RAW / "f01_oferta_establecimientos_gastronomicos.csv"

COLUMNAS_PROHIBIDAS = {"telefono", "mail", "email"}


@dataclass
class RegistroF01:
    archivo_origen: str
    id_registro: str = ""
    nombre: str = ""
    categoria: str = ""
    cocina: str = ""
    ambientacion: str = ""
    direccion: str = ""
    calle_nombre: str = ""
    calle_altura: str = ""
    barrio: str = ""
    comuna: str = ""
    lat: float | None = None
    lon: float | None = None
    crudo: dict = field(default_factory=dict, repr=False)

    @property
    def rubro_completo(self) -> str:
        return " / ".join(x for x in (self.categoria, self.cocina) if x)

    @property
    def texto_clasificable(self) -> str:
        return " ".join(x for x in (self.nombre, self.categoria, self.cocina,
                                    self.ambientacion) if x).strip()


def _a_float(valor: str) -> float | None:
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return None


def iter_f01(
    path: str | Path | None = None,
    *,
    filtro: Callable[[RegistroF01], bool] | None = None,
    incluir_crudo: bool = False,
) -> Iterator[RegistroF01]:
    ruta = Path(path or ARCHIVO_F01)
    with open(ruta, encoding="cp1252", errors="replace", newline="") as fh:
        for fila in csv.DictReader(fh, delimiter=";"):
            can = {}
            for k, v in fila.items():
                if not k:
                    continue
                clave = clave_columna(k)
                if clave in COLUMNAS_PROHIBIDAS:
                    continue
                can[clave] = reparar_mojibake(str(v or "")).strip()
            reg = RegistroF01(
                archivo_origen=ruta.name,
                id_registro=can.get("id", ""),
                nombre=can.get("nombre", ""),
                categoria=can.get("categoria", ""),
                cocina=can.get("cocina", ""),
                ambientacion=can.get("ambientacion", ""),
                direccion=can.get("direccioncompleta", ""),
                calle_nombre=can.get("callenombre", ""),
                calle_altura=can.get("callealtura", ""),
                barrio=can.get("barrio", ""),
                comuna=can.get("comuna", ""),
                lat=_a_float(can.get("lat", "")),
                lon=_a_float(can.get("long", "")),
                crudo=can if incluir_crudo else {},
            )
            if filtro is None or filtro(reg):
                yield reg
