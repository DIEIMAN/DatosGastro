# -*- coding: utf-8 -*-
"""Los solapes, la unión de los 41 y la correspondencia, recalculados con La Boca ya adoptada.

POR QUÉ HAY QUE RECALCULARLOS
------------------------------
El pedido de esta tanda dice que se sumen como canónicas «la unión de los 41 (10.801 locales y
5.434,11 ha), los 25 pares de solape, las 53 concentraciones dentro de un polo y las 71 fuera».
Esas cuatro cifras se midieron la tanda anterior **con La Boca en 6,14 ha**. Esta tanda adopta el
borde de 16,17 ha. Una cifra de conjunto medida sobre una geometría que ya cambió no es canónica:
es la cifra de antes. Así que se vuelve a medir todo, y **la diferencia se publica**.

No se copia el código: se **importa el de la tanda anterior** y se le cambia la geometría de
entrada y la carpeta de salida. Si el método cambiara, cambiaría para las dos mediciones a la vez
y la comparación seguiría siendo válida. Una copia se desincroniza sin que nadie lo note.

Se mide en EPSG:5347 y se guarda en EPSG:4326. Cero requests.
"""

import json
import sys
from pathlib import Path

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
R19 = BARRIDO / "ronda_19"
sys.path.insert(0, str(SALIDA))
sys.path.insert(0, str(R19))

import geometria_vigente_20 as gv20  # noqa: E402
import solapes_y_correspondencia as sc  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    # la misma medición, otra geometría de entrada y otra carpeta de salida
    sc.gv = gv20
    sc.limpia = gv20.limpia
    sc.SALIDA = SALIDA
    sc.main()

    ahora = json.loads((SALIDA / "solapes_resumen.json").read_text(encoding="utf-8"))
    antes = json.loads((R19 / "solapes_resumen.json").read_text(encoding="utf-8"))

    print("\n" + "=" * 98)
    print("QUÉ MOVIÓ LA ADOPCIÓN DE LA BOCA · contra la medición de la tanda anterior")
    print("=" * 98)
    print(f"  {'cifra':<44}{'antes':>12}{'ahora':>12}   {'diferencia':>12}")
    for clave in ("pares_con_solape", "suma_de_los_41_ha", "union_de_los_41_ha",
                  "se_cuentan_de_mas_ha", "suma_de_los_41_locales", "union_de_los_41_locales",
                  "se_cuentan_de_mas_locales", "locales_en_dos_o_mas_polos",
                  "concentraciones_dentro_de_un_polo", "concentraciones_fuera",
                  "locales_de_las_que_no"):
        a, h = antes.get(clave), ahora.get(clave)
        if a is None or h is None:
            continue
        d = h - a
        marca = "   <-- cambia" if abs(d) > 1e-9 else ""
        print(f"  {clave:<44}{a:>12,.2f}{h:>12,.2f}   {d:>+12,.2f}{marca}"
              if isinstance(a, float) else
              f"  {clave:<44}{a:>12,}{h:>12,}   {d:>+12,}{marca}")

    (SALIDA / "que_movio_la_adopcion.json").write_text(
        json.dumps(dict(antes=antes, ahora=ahora), ensure_ascii=False, indent=2),
        encoding="utf-8")
    print("\nEscrito: que_movio_la_adopcion.json")


if __name__ == "__main__":
    main()
