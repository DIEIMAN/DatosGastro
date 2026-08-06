"""Deja la inferencia del vocabulario `TIPO2` auditable sin el diccionario oficial. 0 requests.

POR QUÉ EXISTE ESTE ARCHIVO
---------------------------
El Relevamiento de Usos del Suelo **sostiene el mapa** —la ablación lo midió: sin él la corrida
colapsa y sacar la misma cantidad de puntos al azar no la rompe ninguna de las cinco veces—. Y su
documentación oficial **no publica el diccionario de códigos de `TIPO2`**, así que el vocabulario
está inferido por conteo sobre el archivo.

Por decisión de alcance del 2026-08-06 no se piden datos fuera de la Dirección, así que **el
diccionario oficial no va a llegar**. La inferencia deja de ser provisoria y pasa a ser lo que hay.
Entonces tiene que quedar auditable: valor por valor, con su frecuencia real en la fuente, para que
cualquiera pueda revisarla contra el territorio sin el diccionario.

Y la consecuencia hay que decirla con todas las letras: **si la clasificación inferida está
corrida, el mapa se mueve.** Un valor de `TIPO2` mal asignado al anillo núcleo agrega o saca
parcelas de la fuente que sostiene la corrida.

El documento se GENERA desde el mapeo vivo de `perfilar_usos_suelo.py`, no se escribe a mano: si
alguien cambia el mapeo y no regenera, la diferencia se ve. Escribirlo a mano garantizaba que se
desincronizara en la primera corrección.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/documentar_inferencia_tipo2.py
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from perfilar_usos_suelo import (  # noqa: E402
    AMPLIADO_SUMA, DESCARTADOS_EXPLICITOS, NUCLEO,
)

SALIDA = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "INFERENCIA_TIPO2_RELEVAMIENTO.md"
VOCABULARIO = ROOT / "outputs" / "fuentes_externas" / "usos_suelo" / "rus_vocabulario_tipo2.csv"


def frecuencias() -> dict[str, int]:
    """Cuántos registros tiene cada valor de TIPO2 en la fuente.

    Es la columna que hace auditable la tabla: sin ella el mapeo es una lista de opiniones, y con
    ella se ve de inmediato cuáles asignaciones mueven mucho y cuáles son marginales.
    """
    if not VOCABULARIO.exists():
        return {}
    tabla = pd.read_csv(VOCABULARIO)
    return dict(zip(tabla.TIPO2, tabla.registros))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    conteo = frecuencias()

    def fila(valor: str, anillo: str, categoria: str) -> str:
        n = conteo.get(valor)
        return f"| `{valor}` | {anillo} | {categoria} | {n if n is not None else '—'} |"

    lineas = [
        "# Inferencia del vocabulario `TIPO2` del Relevamiento de Usos del Suelo",
        "",
        "**Generado por `scripts/barrido_ciudad/documentar_inferencia_tipo2.py` desde el mapeo vivo",
        "de `perfilar_usos_suelo.py`. No editar a mano: regenerar.**",
        "",
        "## Por qué este documento es necesario",
        "",
        "El Relevamiento **sostiene el mapa**: la ablación con control aleatorio midió que sin él la",
        "corrida colapsa, y que sacar la misma cantidad de puntos al azar no la rompe ninguna de las",
        "cinco veces. Y su documentación oficial **no publica el diccionario de códigos de `TIPO2`**.",
        "",
        "Por la decisión de alcance del 2026-08-06 —sin pedidos fuera de la Dirección— **el",
        "diccionario oficial no va a llegar**. La inferencia deja de ser provisoria: es lo que hay, y",
        "por eso queda acá valor por valor.",
        "",
        "> **Si esta clasificación está corrida, el mapa se mueve.** Un valor mal asignado al anillo",
        "> núcleo agrega o saca parcelas de la fuente que sostiene la corrida. Esta advertencia viaja",
        "> con el mapa, no sólo con este documento.",
        "",
        "## Cómo se estableció",
        "",
        "Por conteo sobre el archivo (471 valores distintos de `TIPO2`), con un criterio único:",
        "**simetría con el mapeo de habilitaciones** (decisión de Diego, 2026-08-05). Cada valor va",
        "al anillo donde ya cae su equivalente en `fact_habilitacion_gastronomica.csv`. El criterio",
        "no es «qué nos parece que es» sino «dónde lo pusimos ya en la otra base», para que las dos",
        "sigan siendo comparables.",
        "",
        "Sólo se consideran parcelas con `TIPO1 = UNICOMERCIAL` y `ESTADO = ACTIVO`.",
        "",
        "## Anillo núcleo · gastronomía de atención al público",
        "",
        "| valor de `TIPO2` | anillo | categoría del proyecto | parcelas en la fuente |",
        "|---|---|---|---:|",
    ]
    for categoria, valores in NUCLEO.items():
        for valor in valores:
            lineas.append(fila(valor, "núcleo", categoria))

    lineas += [
        "",
        "### Las dos asignaciones que hubo que justificar",
        "",
        "- **`CERVECERIA` → núcleo (Bar).** En el padrón, «despacho de bebidas», «wisquería» y",
        "  «cervecería» caen todas en Bar. Se respeta esa simetría.",
        "- **`SUSHI` → núcleo (Restaurante).** No tiene rubro propio en el padrón; su equivalente",
        "  más cercano —«restaurante», «cantina»— está en Restaurante.",
        "",
        "## Anillo ampliado · comercio de alimentos, fuera del universo principal",
        "",
        "| valor de `TIPO2` | anillo | categoría del proyecto | parcelas en la fuente |",
        "|---|---|---|---:|",
    ]
    for categoria, valores in AMPLIADO_SUMA.items():
        for valor in valores:
            lineas.append(fila(valor, "ampliado", categoria))

    lineas += [
        "",
        "### La asignación discutible, declarada como tal y NO corregida",
        "",
        "**`CONFITERIA` → ampliado (Pastelería).** Es discutible y se sabe: una confitería porteña es",
        "un café con servicio de mesa, no una pastelería. Se mantiene porque el padrón la manda a",
        "Pastelería (1.721 habilitaciones) y **corregirla de un solo lado rompería la comparación",
        "entre las dos bases**. Si se cambia, se cambia en habilitaciones y en el Relevamiento en la",
        "misma corrida, y se recalcula todo. Hoy no se toca — y queda escrito para que quien audite",
        "sepa que es una decisión y no un descuido.",
        "",
        "Es, además, la asignación con más impacto potencial: el anillo ampliado no entra a la",
        "poligonización, así que mover `CONFITERIA` al núcleo cambiaría el universo del mapa.",
        "",
        "## Valores que la búsqueda por palabra clave trae y NO son gastronomía",
        "",
        "Descartados explícitamente. La lista importa tanto como la de arriba: son los falsos",
        "positivos que una búsqueda ingenua por «café», «bar» o «gastronómico» habría incorporado.",
        "",
        "| valor de `TIPO2` | por qué se descarta |",
        "|---|---|",
    ]
    razones = {
        "BARBERIA": "no es gastronomía; entra por parecido de cadena de texto",
        "ALIMENTOS PARA MASCOTAS": "comercio de alimentos, no atención al público gastronómica",
        "VINOS (VENTA)": "venta de bebidas para llevar, sin salón",
        "BEBIDAS ALCOHOLICAS": "venta para llevar, sin salón",
        "FABRICA DE PASTAS": "elaboración; además es el universo de otro subproyecto",
        "EQUIP. GASTRONOMICO": "venta de equipamiento, no gastronomía",
        "VENTA DE CAFÉ (PRODUCTOS)": "venta del producto, no cafetería",
        "REPARACION DE HELADERAS": "servicio técnico",
        "HELADERAS Y BALANZAS COMERCIALES (VTA)": "venta de equipamiento",
        "RESTAURACIONES": "restauración de bienes; falso positivo por «restaur-»",
        "INSTITUTO DE GASTRONOMIA": "enseñanza, no oferta gastronómica",
        "VENTA POR MAYOR DE ALIMENTOS Y BEBIDAS": "mayorista, sin atención al público",
        "GALERÍA BARRIAL": "contenedor de locales, no un local",
    }
    for valor in DESCARTADOS_EXPLICITOS:
        lineas.append(f"| `{valor}` | {razones.get(valor, '—')} |")

    lineas += [
        "",
        "## Cómo auditar esto sin el diccionario oficial",
        "",
        "1. Tomar una muestra de parcelas de cada valor de `TIPO2` del núcleo y mirar la dirección",
        "   en la calle. Es lento y es el único control real disponible.",
        "2. Contrastar el conteo por barrio contra el padrón de habilitaciones del mismo barrio: un",
        "   valor mal asignado se ve como una discrepancia concentrada en un rubro.",
        "3. Revisar primero `CONFITERIA`, `CERVECERIA` y `SUSHI`, que son las tres asignaciones que",
        "   no salieron directas del padrón.",
        "",
        "## Un defecto de codificación que hay que conocer",
        "",
        "La fuente llega con doble codificación CP437/UTF-8 (`CAF├ë` por `CAFÉ`). No es cosmético:",
        "**sin reparar, `CAFÉ` desaparece del vocabulario y se pierden 1.803 parcelas sin que ninguna",
        "corrida falle.** El reparador y su control están en `perfilar_usos_suelo.py`.",
        "",
    ]
    SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"escrito {SALIDA.relative_to(ROOT)}")
    print(f"  núcleo: {sum(len(v) for v in NUCLEO.values())} valores en "
          f"{len(NUCLEO)} categorías")
    print(f"  ampliado: {sum(len(v) for v in AMPLIADO_SUMA.values())} valores")
    print(f"  descartados explícitos: {len(DESCARTADOS_EXPLICITOS)}")
    print(f"  frecuencias encontradas: {'sí' if conteo else 'no (falta el perfilado)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
