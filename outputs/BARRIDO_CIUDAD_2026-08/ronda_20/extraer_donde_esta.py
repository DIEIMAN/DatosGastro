# -*- coding: utf-8 -*-
"""Saca del documento el bloque «Dónde está» de cada una de las 41 páginas, entero y literal.

Es la mitad mecánica del control del perímetro escrito: recortar el bloque y resolver contra el
callejero oficial qué nombres de los que aparecen son calles de verdad. **La otra mitad —en qué
categoría cae cada página y si el borde se puede reconstruir desde el texto— no la resuelve un
patrón**, y por eso va declarada a mano en `perimetro_escrito_41.py`, con el texto literal al lado
para que se pueda cotejar.

El bloque va desde `**Dónde está.**` hasta el próximo rótulo en negrita al principio de párrafo o
el próximo título. Las citas textuales de adentro del bloque —las que van con `>`— entran, porque
en varias páginas la delimitación **es** la cita.

Cero requests.
"""

import re
import sys
import unicodedata
from pathlib import Path

import geopandas as gpd

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
DOC = BARRIDO / "documento" / "ATLAS_V3_DOCUMENTO.md"
BORDES = SALIDA / "geometria" / "bordes_vigentes_41.geojson"

# Los dos nombres que la página escribe distinto de como los trae la capa.
ALIAS = {
    "Centro y Microcentro": "Centro / Microcentro",
    "Barracas · Av. Montes de Oca": "Av. Montes de Oca",
}


def clave(x):
    x = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", x)


def bloques_del_documento():
    """{clave del título de la página: (título, texto del bloque «Dónde está»)}"""
    texto = DOC.read_text(encoding="utf-8")
    cuerpo = texto[texto.index("## Comuna 1"):]
    partes = re.split(r"^### (.+)$", cuerpo, flags=re.M)
    salida = {}
    for i in range(1, len(partes), 2):
        titulo, pagina = partes[i].strip(), partes[i + 1]
        m = re.search(r"^\*\*Dónde está\.\*\*(.*?)(?=^\*\*[^*\n]{2,60}?\.\*\*|^#{2,3} |\Z)",
                      pagina, flags=re.M | re.S)
        salida[clave(titulo)] = (titulo, m.group(0).strip() if m else "")
    return salida


def paginas():
    """[(polo_id, polo_nombre, titulo_en_el_documento, texto_del_bloque)] para los 41."""
    bordes = gpd.read_file(BORDES)
    doc = bloques_del_documento()
    filas, sin_bloque = [], []
    for r in sorted(bordes.itertuples(), key=lambda x: x.polo_id):
        titulo_esperado = ALIAS.get(r.polo_nombre, r.polo_nombre)
        hit = doc.get(clave(titulo_esperado))
        if hit is None:
            sin_bloque.append((r.polo_id, r.polo_nombre))
            continue
        filas.append((r.polo_id, r.polo_nombre, hit[0], hit[1]))
    if sin_bloque:
        raise SystemExit(f"{len(sin_bloque)} polos no tienen página en el documento: "
                         f"{sin_bloque}. No se audita un perímetro escrito que no se encontró.")
    vacios = [(p, n) for p, n, _, t in filas if not t]
    if vacios:
        raise SystemExit(f"{len(vacios)} páginas no tienen bloque «Dónde está»: {vacios}. "
                         f"Si de verdad no lo tienen es un hallazgo y hay que declararlo, no "
                         f"dejarlo pasar como una fila vacía.")
    return filas


def calles_del_callejero():
    """El resolvedor de nombres de calle del repositorio, para preguntar si un nombre es calle."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "barrido_ciudad"))
    from callejero_canonico import cargar, familias  # noqa: E402
    calles = cargar()
    return calles, familias(calles)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    filas = paginas()
    print("=" * 98)
    print(f"EL BLOQUE «DÓNDE ESTÁ» DE LAS {len(filas)} PÁGINAS, LITERAL")
    print("=" * 98)
    for pid, nombre, titulo, texto in filas:
        print("\n" + "-" * 98)
        print(f"{pid} · {nombre}   (la página se titula «{titulo}»)")
        print("-" * 98)
        print(texto)


if __name__ == "__main__":
    main()
