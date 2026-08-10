# -*- coding: utf-8 -*-
"""Aplica ERR-12 al unico archivo donde vive el error: la fila del Britanico de la ronda 13.

QUE SE CORRIGE Y QUE NO
-----------------------
El catalogo NO esta mal. `catalogo_90_estado_final.csv` da BAR BRITANICO en Brasil 399 (San Telmo)
y BAR SEDDON en Defensa 695 (Monserrat), y las dos coinciden con la geocodificacion USIG del
dataset de Notables. La direccion cruzada aparece en un solo lugar: el campo `direccion` de la fila
del Britanico en `ronda_13/verificaciones_seis_fichas_r13.csv`, que dice
"Defensa 695 esq. Brasil 399" — una altura de Monserrat con una esquina de San Telmo.

Se corrige ese campo y se le pega el puntero a la errata. No se toca ninguna otra columna: el
veredicto de la fila (verificado_abierto v1, 18/04/2026) no cambia, porque el punto del Britanico
cae DENTRO de R11 y la fuente que lo cierra sigue siendo la misma.

Se edita el TEXTO del archivo y no se reescribe con `csv.DictWriter`. Reescribirlo cambia el
entrecomillado de otras tres filas —el modulo csv saca las comillas de los campos que no las
necesitan— y el diff pasa de una linea a cuatro. Un diff que toca filas que nadie corrigio es
exactamente lo que hace que nadie los lea.

La seccion VII no se toca desde el repositorio: es contenido.
"""

from pathlib import Path

SALIDA = Path(__file__).resolve().parent
DESTINO = SALIDA.parent / "ronda_13" / "verificaciones_seis_fichas_r13.csv"

VIEJA = "Defensa 695 esq. Brasil 399"
NUEVA = "Brasil 399 esq. Defensa (Defensa 1499/1501)"
NOTA = (" ERR-12: la direccion decia 'Defensa 695 esq. Brasil 399'. Defensa 695 es la esquina de "
        "Chile, en Monserrat, y es de BAR SEDDON; Brasil cruza Defensa en el 1499/1501. Corregida "
        "el 09/08/2026 sin tocar el veredicto: el punto del Britanico cae dentro de R11.")


CIERRE_QUE_FALTA = 'cierra pero no con holgura."'


def main():
    texto = DESTINO.read_text(encoding="utf-8")
    if texto.count(VIEJA) != 1 or texto.count(CIERRE_QUE_FALTA) != 1:
        raise SystemExit("el archivo no esta como esperaba: no se toca nada")
    texto = texto.replace(VIEJA, NUEVA)
    texto = texto.replace(CIERRE_QUE_FALTA, CIERRE_QUE_FALTA[:-1] + NOTA + '"')
    DESTINO.write_text(texto, encoding="utf-8", newline="")
    print(f"{DESTINO.name}: 1 fila corregida ({VIEJA!r} -> {NUEVA!r})")


if __name__ == "__main__":
    main()
