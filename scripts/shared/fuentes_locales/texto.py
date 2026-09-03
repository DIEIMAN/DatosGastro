"""Normalizacion de texto compartida por los estudios de rubro.

`normalizar` es la misma funcion que venian copiando panaderias_patterns.norm y
pastas_patterns.norm: NFKD, sin acentos, minusculas, solo [a-z0-9 ].

`reparar_mojibake` corrige el caso real de F02 2022, que trae UTF-8 releido como
latin-1 y vuelto a grabar asi (doble codificacion en el archivo de origen): el rubro
llega como "PANADERÃA" en vez de "PANADERIA". Sin reparar, `normalizar` lo
convierte en "panader a" y el clasificador deja de reconocerlo.
"""
from __future__ import annotations

import re
import unicodedata

# Marca de mojibake: "Ã"/"Â" seguidas de un caracter no alfabetico corriente.
_MOJIBAKE = re.compile("[ÃÂ][-¿–—‘-”€�]")


def reparar_mojibake(texto: str) -> str:
    """Deshace la doble codificacion cuando la detecta; si no, devuelve el original.

    Conservador a proposito: solo actua ante una secuencia tipica de mojibake y solo
    acepta el resultado si el round-trip no introdujo caracteres de reemplazo.
    """
    if not texto or not _MOJIBAKE.search(texto):
        return texto
    try:
        arreglado = texto.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto
    return arreglado if "�" not in arreglado else texto


def normalizar(value: object) -> str:
    """NFKD sin acentos, minusculas, solo letras/numeros/espacio."""
    texto = reparar_mojibake(str(value or ""))
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", texto)).strip()


def clave_columna(nombre: str) -> str:
    """Clave canonica de un encabezado: sin acentos, sin separadores, minuscula.

    Hace que `descripcion_rubro`, `DescripcionRubro` y `Descripcion Rubro` sean la
    misma columna, que es exactamente como cambia F02 de un anio a otro.
    """
    base = unicodedata.normalize("NFKD", str(nombre or ""))
    base = "".join(ch for ch in base if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", base.lower())
