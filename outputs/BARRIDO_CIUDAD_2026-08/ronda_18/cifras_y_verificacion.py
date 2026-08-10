# -*- coding: utf-8 -*-
"""Las cifras canónicas al día de esta ronda, y el texto del atlas contra ellas.

QUÉ HACE
--------
Toma las cifras canónicas de la ronda anterior, **actualiza las que esta ronda movió** y agrega
las que esta ronda produjo por primera vez. Después corre la verificación con el mismo código de
la ronda 17 —no una copia— para que el resultado sea comparable con el de la tanda pasada.

DOS CIFRAS QUE YA HABÍAN CAMBIADO Y ESTÁN BIEN
----------------------------------------------
`polos_sin_borde` vale **4** y `objetos_disjuntos` vale **40**. El texto todavía dice «dieciocho»
y «39»; la que está vieja es la prosa, no la medición. Van con nota para que nadie las «corrija»
al revés.

No corrige nada. Señala; la corrección la firma quien escribe.
"""

import json
import sys
from datetime import date
from pathlib import Path

SALIDA = Path(__file__).resolve().parent
R17 = SALIDA.parent / "ronda_17"
ROOT = SALIDA.parents[2]
sys.path.insert(0, str(R17))
import verificar_cifras as vc  # noqa: E402

HOY = date.today().isoformat()


def cifra(valor, unidad, archivo, como, patrones=(), nota="", origen="medido"):
    return dict(valor=valor, unidad=unidad, fecha_de_calculo=HOY, archivo_del_que_sale=archivo,
                como_se_calcula=como, origen=origen, patrones_en_el_texto=list(patrones),
                nota=nota)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    canon = json.loads((R17 / "cifras_canonicas.json").read_text(encoding="utf-8"))
    cifras = canon["cifras"]

    bordes = json.loads((SALIDA / "bordes_ronda_18.json").read_text(encoding="utf-8"))
    anclas = json.loads((SALIDA / "anclas_resumen.json").read_text(encoding="utf-8"))
    solapes = json.loads((SALIDA / "solapes_resumen.json").read_text(encoding="utf-8"))
    R = "outputs/BARRIDO_CIUDAD_2026-08/ronda_18"

    # --- las dos que ya habían cambiado y siguen valiendo lo mismo -------------------------
    cifras["polos_sin_borde"]["nota"] = (
        "vale 4 y el texto dice «dieciocho»: la prosa es la que está vieja. Siguen sin borde "
        "propio Z27, Z33, Z41 y Z46. De los cuatro, Mataderos (Z33) pasa a tener un borde "
        "TENTATIVO en esta ronda, que no es un borde cerrado y por eso la cifra no baja a 3; "
        "Núñez (Z41) y Retiro (Z46) publican el polígono de su barrio")
    cifras["polos_sin_borde"]["archivo_del_que_sale"] = f"{R}/perimetros_ronda_18.csv"
    cifras["objetos_disjuntos"]["nota"] = (
        "vale 40 y el texto dice 39. El documento cuenta a Baek-ku como subzona de Parque "
        "Avellaneda y medido queda 100 % fuera de los otros cuarenta")

    # --- lo que esta ronda movió o midió por primera vez ------------------------------------
    nuevas = {
        "la_boca_caminito_ha": cifra(
            bordes["Z53"]["ha"], "hectáreas", f"{R}/perimetros_ronda_18.csv",
            "Caminito entero más Av. Don Pedro de Mendoza 1871-1939, manzanas frentistas",
            nota="el borde anterior medía 1,27 ha; se extiende para contener La Perla de "
                 "Caminito, que estaba 26 m afuera"),
        "la_boca_caminito_locales": cifra(
            bordes["Z53"]["n_locales"], "locales", f"{R}/perimetros_ronda_18.csv",
            "locales del universo anillo=nucleo & apto_geometria dentro del polígono",
            nota="el borde anterior tenía 16"),
        "mataderos_tentativo_ha": cifra(
            bordes["Z33"]["ha"], "hectáreas", f"{R}/perimetros_ronda_18.csv",
            "manzanas frentistas del cruce de Av. Lisandro de la Torre y Av. de los Corrales",
            nota="BORDE TENTATIVO, no cerrado. 40,70 de las 43,99 ha son una sola manzana: la "
                 "densidad por hectárea de esta zona no es comparable con la de las demás"),
        "mataderos_tentativo_locales": cifra(
            bordes["Z33"]["n_locales"], "locales", f"{R}/perimetros_ronda_18.csv",
            "locales dentro del borde tentativo", nota="BORDE TENTATIVO, no cerrado"),
        "mataderos_eje_alberdi_ha": cifra(
            bordes["Z33"]["eje_alberdi_ha"], "hectáreas", f"{R}/perimetros_ronda_18.csv",
            "Av. Juan B. Alberdi 5501-6299, el eje comercial que releva la Ciudad",
            nota="lectura medida y publicada aparte: es el eje del IDECBA, no el perímetro del "
                 "polo. No comparte superficie con el borde tentativo"),
        "mataderos_eje_alberdi_locales": cifra(
            bordes["Z33"]["eje_alberdi_locales"], "locales", f"{R}/perimetros_ronda_18.csv",
            "locales dentro del eje comercial de Av. Alberdi"),
        "balvanera_lectura_enclave_ha": cifra(
            bordes["Z35"]["lectura_1_ha"], "hectáreas", f"{R}/perimetros_ronda_18.csv",
            "eje Tucumán 2379-2755 y transversal Paso 700-799",
            nota="deja el Café de los Angelitos afuera; la decisión entre las dos lecturas "
                 "está abierta"),
        "balvanera_lectura_extendida_ha": cifra(
            bordes["Z35"]["lectura_2_ha"], "hectáreas", f"{R}/perimetros_ronda_18.csv",
            "lo anterior más Pasteur entre Tucumán y Av. Rivadavia, y Av. Rivadavia 2001-2200",
            nota="contiene el Café de los Angelitos"),
        "balvanera_lectura_extendida_locales": cifra(
            bordes["Z35"]["lectura_2_locales"], "locales", f"{R}/perimetros_ronda_18.csv",
            "locales dentro de la lectura extendida"),
        "villa_ortuzar_ha": cifra(
            bordes["Z44"]["ha"], "hectáreas", f"{R}/perimetros_ronda_18.csv",
            "las dos aceras de Av. Álvarez Thomas entre el 600 y el 1700"),
        "villa_ortuzar_locales": cifra(
            bordes["Z44"]["n_locales"], "locales", f"{R}/perimetros_ronda_18.csv",
            "locales dentro del corredor de dos aceras"),
        "villa_ortuzar_solape_ha": cifra(
            solapes["villa_ortuzar_solape_ha"], "hectáreas", f"{R}/solapes_declarados.csv",
            "intersección del corredor con la unión de Chacarita, Colegiales y Federico Lacroze",
            nota="verificado contra la geometría vigente de los tres: coincide con la cifra de "
                 "la decisión"),
        "villa_ortuzar_solape_locales": cifra(
            solapes["villa_ortuzar_solape_locales"], "locales", f"{R}/solapes_declarados.csv",
            "locales dentro de esa intersección"),
        "pares_de_polos_con_solape": cifra(
            solapes["pares_con_solape"], "pares", f"{R}/solapes_declarados.csv",
            "todo par de polos cuya intersección supera 1 m²"),
        "locales_en_dos_o_mas_polos": cifra(
            solapes["locales_en_dos_o_mas_polos"], "locales", f"{R}/solapes_declarados.csv",
            "locales distintos que caen dentro de más de un polo",
            nota=f"la suma de los 41 por separado da {solapes['suma_de_los_41']} y la unión "
                 f"{solapes['union_de_los_41']}: {solapes['se_cuentan_de_mas']} de más"),
        "concentraciones_dentro_de_un_polo": cifra(
            solapes["concentraciones_dentro_de_un_polo"], "concentraciones",
            f"{R}/correspondencia_124_x_41.csv",
            "concentraciones contenidas o con más de la mitad de su superficie dentro de un polo",
            nota="medido por superficie perdida contra la geometría vigente, no con covers()"),
        "concentraciones_fuera_de_todo_polo": cifra(
            solapes["concentraciones_fuera"], "concentraciones",
            f"{R}/correspondencia_124_x_41.csv",
            "las 124 menos las que caen dentro de algún polo",
            nota=f"suman {solapes['locales_de_las_que_no']} locales"),
        "anclas_con_historia_fuera_de_su_borde": cifra(
            anclas["con_historia_y_quedan_afuera"], "establecimientos",
            f"{R}/anclas_dentro_y_fuera.csv",
            "establecimientos de trayectoria que sostienen la vía B de su zona y no caen dentro "
            "del borde de su polo",
            nota=f"en {anclas['paginas_con_el_problema']} páginas. En "
                 f"{len(anclas['paginas_sin_ninguno_adentro'])} de ellas el borde no contiene "
                 f"ninguno"),
        "paginas_con_el_ancla_afuera": cifra(
            anclas["paginas_con_el_problema"], "páginas",
            f"{R}/anclas_dentro_y_fuera.csv",
            "polos con al menos un establecimiento de trayectoria fuera de su borde"),
    }
    cifras.update(nuevas)

    destino = SALIDA / "cifras_canonicas.json"
    destino.write_text(json.dumps(dict(generado=HOY, cifras=cifras), ensure_ascii=False,
                                  indent=2), encoding="utf-8")
    print("=" * 98)
    print(f"CIFRAS CANÓNICAS AL DÍA · {len(cifras)} cifras "
          f"({len(nuevas)} nuevas o actualizadas en esta ronda)")
    print("=" * 98)
    for nombre in nuevas:
        c = cifras[nombre]
        print(f"  {nombre:<42}{str(c['valor']):>10} {c['unidad']}")
    print(f"\nEscrito: {destino.name}\n")

    # --- la verificación, con el código de la ronda 17 y las canónicas de ésta --------------
    vc.CANONICAS = destino
    vc.SALIDA = SALIDA
    sys.argv = [sys.argv[0], "--json"]
    vc.main()


if __name__ == "__main__":
    main()
