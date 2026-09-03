# -*- coding: utf-8 -*-
"""Las cifras canónicas al día de esta tanda, y el texto del documento contra ellas.

QUÉ HACE
--------
Toma las canónicas de la tanda anterior, actualiza las que ésta movió, agrega las que ésta midió
por primera vez y corre la verificación con el mismo código de siempre —no una copia— para que el
resultado sea comparable con el de la vez pasada. Al final compara las dos verificaciones y dice
**qué números dejaron de coincidir y cuáles empezaron a coincidir**.

LAS CUATRO QUE CAMBIARON Y SON CORRECTAS
----------------------------------------
  - **Los polos sin borde propio son 3**, no 4: Núñez y Retiro publican el polígono de su barrio
    y Villa Santa Rita no tiene ningún trazado. Mataderos sale de esa lista porque ahora tiene un
    borde, **transitorio**, y eso se cuenta aparte: un borde transitorio no es un borde cerrado,
    pero tampoco es no tener ninguno.
  - **La Boca · Caminito: 4,15 ha y 37 locales.**
  - **Mataderos: 43,99 ha y 17 locales, transitorio.**
  - **Los lugares separados son 40.**

No corrige nada. Señala; la corrección la firma quien escribe.
"""

import json
import sys
from datetime import date
from pathlib import Path

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
R17 = BARRIDO / "ronda_17"
R18 = BARRIDO / "ronda_18"
sys.path.insert(0, str(R17))
import verificar_cifras as vc  # noqa: E402

HOY = date.today().isoformat()
R = "outputs/BARRIDO_CIUDAD_2026-08/ronda_19"


def cifra(valor, unidad, archivo, como, patrones=(), nota="", origen="medido"):
    return dict(valor=valor, unidad=unidad, fecha_de_calculo=HOY, archivo_del_que_sale=archivo,
                como_se_calcula=como, origen=origen, patrones_en_el_texto=list(patrones),
                nota=nota)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    canon = json.loads((R18 / "cifras_canonicas.json").read_text(encoding="utf-8"))
    cifras = canon["cifras"]

    solapes = json.loads((SALIDA / "solapes_resumen.json").read_text(encoding="utf-8"))
    cinco = json.loads((SALIDA / "cinco_sin_ancla_resumen.json").read_text(encoding="utf-8"))
    cerca = json.loads((SALIDA / "hitos_cerca_resumen.json").read_text(encoding="utf-8"))

    # --- la que cambia de valor y es correcta -----------------------------------------------
    cifras["polos_sin_borde"]["valor"] = 3
    cifras["polos_sin_borde"]["fecha_de_calculo"] = HOY
    cifras["polos_sin_borde"]["archivo_del_que_sale"] = f"{R}/geometria/bordes_vigentes_41.geojson"
    cifras["polos_sin_borde"]["nota"] = (
        "vale 3 y el texto dice «dieciocho»: la prosa es la que está vieja. Los tres son Villa "
        "Santa Rita, que no tiene ningún trazado, y Núñez y Retiro, que publican el polígono de "
        "su barrio. Mataderos sale de la lista porque ya tiene un borde, transitorio, y eso se "
        "cuenta aparte: la cifra de al lado es polos_con_borde_transitorio = 1")
    cifras["objetos_disjuntos"]["nota"] = (
        "vale 40 y el texto dice 39. El documento cuenta a Baek-ku como subzona de Parque "
        "Avellaneda y medido queda 100 % fuera de los otros cuarenta")
    cifras["objetos_disjuntos"]["patrones_en_el_texto"] = list(
        cifras["objetos_disjuntos"].get("patrones_en_el_texto") or []) + [
        r"(?:son|hay)\s+\*{0,2}(?P<valor>\d{1,3}|cuarenta|treinta y nueve)\*{0,2}\s+lugares "
        r"separados"]

    # --- lo que esta tanda midió -------------------------------------------------------------
    nuevas = {
        "polos_con_borde_transitorio": cifra(
            1, "polos", f"{R}/geometria/bordes_vigentes_41.geojson",
            "polos con un borde publicado y declarado transitorio",
            nota="es Mataderos. Un borde transitorio se publica y no se toma por una "
                 "delimitación cerrada"),
        "union_de_los_41_ha": cifra(
            solapes["union_de_los_41_ha"], "hectáreas", f"{R}/solapes_declarados.csv",
            "superficie de la unión de los 41 bordes vigentes, con el solape descontado una "
            "sola vez",
            nota=f"la suma de los 41 por separado da {solapes['suma_de_los_41_ha']} ha: "
                 f"{solapes['se_cuentan_de_mas_ha']} se cuentan dos veces"),
        "union_de_los_41_locales": cifra(
            solapes["union_de_los_41_locales"], "locales", f"{R}/solapes_declarados.csv",
            "locales del universo anillo=nucleo & apto_geometria dentro de la unión de los 41",
            nota=f"la suma de los 41 por separado da {solapes['suma_de_los_41_locales']}: "
                 f"{solapes['se_cuentan_de_mas_locales']} se cuentan dos veces, repartidos en "
                 f"{solapes['locales_en_dos_o_mas_polos']} locales distintos"),
        "locales_contados_dos_veces": cifra(
            solapes["se_cuentan_de_mas_locales"], "locales", f"{R}/solapes_declarados.csv",
            "la suma de los 41 por separado menos la unión de los 41"),
        "pares_de_polos_con_solape": cifra(
            solapes["pares_con_solape"], "pares", f"{R}/solapes_declarados.csv",
            "todo par de polos cuya intersección supera 1 m²"),
        "locales_en_dos_o_mas_polos": cifra(
            solapes["locales_en_dos_o_mas_polos"], "locales", f"{R}/solapes_locales_detalle.csv",
            "locales distintos que caen dentro de más de un polo"),
        "villa_ortuzar_solape_ha": cifra(
            solapes["villa_ortuzar_solape_ha"], "hectáreas", f"{R}/solapes_declarados.csv",
            "intersección del corredor con la unión de Chacarita, Colegiales y Federico Lacroze",
            nota="verificado contra la geometría vigente: coincide con la cifra adoptada"),
        "villa_ortuzar_solape_locales": cifra(
            solapes["villa_ortuzar_solape_locales"], "locales", f"{R}/solapes_declarados.csv",
            "locales dentro de esa intersección"),
        "concentraciones_dentro_de_un_polo": cifra(
            solapes["concentraciones_dentro_de_un_polo"], "concentraciones",
            f"{R}/correspondencia_124_x_41.csv",
            "concentraciones contenidas o con más de la mitad de su superficie dentro de un polo",
            nota="medido por superficie perdida contra la geometría vigente, no con covers()"),
        "concentraciones_fuera_de_todo_polo": cifra(
            solapes["concentraciones_fuera"], "concentraciones",
            f"{R}/correspondencia_124_x_41.csv",
            "las 124 menos las que caen dentro de algún polo",
            nota=f"suman {solapes['locales_de_las_que_no']} locales. De ellas, "
                 f"{solapes['concentraciones_fuera_de_todo_polo']} no tocan ningún borde"),
        "paginas_sin_ningun_ancla_adentro": cifra(
            len(cinco["paginas"]), "páginas", f"{R}/cinco_sin_ancla_adentro.csv",
            "páginas cuyo borde no contiene ninguno de los establecimientos con trayectoria "
            "sobre los que su zona se apoya"),
        "hitos_fuera_de_todo_borde": cifra(
            cerca["fuera_de_todo_borde"], "establecimientos", f"{R}/hitos_cerca_del_borde.csv",
            "establecimientos de la capa de reconocimiento a más de 3 m de los 41 bordes",
            nota="antes eran 60, medidos contra la instantánea anterior de bordes. La diferencia "
                 "no es que hayan aparecido establecimientos: es que los perímetros trazados son "
                 "más chicos que los soportes provisorios que reemplazaron"),
        "hitos_a_250_m_o_menos_del_borde": cifra(
            cerca["a_250_m_o_menos"], "establecimientos", f"{R}/hitos_cerca_del_borde.csv",
            "de los que quedan fuera, los que están a 250 m o menos del borde más cercano",
            nota="el corte de 250 m es una prioridad de inspección y no una prueba de que el "
                 "borde esté incompleto. Son 45 filas y 44 establecimientos distintos: la capa "
                 "trae el Café Roma dos veces, con dos direcciones y un solo punto"),
        "hitos_cerca_sobre_calle_ya_nombrada": cifra(
            cerca["sobre_calle_ya_nombrada"], "establecimientos",
            f"{R}/hitos_cerca_del_borde.csv",
            "de los que quedan a 250 m o menos, aquellos cuya calle de puerta está nombrada en "
            "el perímetro escrito de la página y además toca el borde",
            nota="son los únicos que se resolverían sin inventar una línea"),
    }
    cifras.update(nuevas)

    # --- ¿aparece la cifra, escrita, en algún documento? -------------------------------------
    #
    # Es otra pregunta que la de la verificación por patrón, y hace falta hacerla aparte. Un
    # patrón busca la cifra EN SU FRASE: sirve cuando se sabe cómo está escrita. Para saber si un
    # número que todavía no se publicó **aparece o no**, el patrón suelto no sirve: la primera
    # versión de esta corrida puso «Caminito … NN ha» y enganchó «Caminito y Vuelta de Rocha con
    # 105 locales», que es la concentración y no el polo, y lo reportó como una discrepancia que
    # no existía. Acá se busca la cadena exacta, que no puede engancharse de más.
    LITERALES = [
        ("la_boca_caminito_ha", "4,15"), ("la_boca_caminito_locales", "37 locales"),
        ("mataderos_tentativo_ha", "43,99"), ("mataderos_tentativo_locales", "17 locales"),
        ("mataderos_eje_alberdi_ha", "24,27"),
        ("balvanera_lectura_enclave_ha", "19,18"),
        ("balvanera_lectura_extendida_ha", "44,75"),
        ("villa_ortuzar_ha", "34,39"), ("villa_ortuzar_solape_ha", "15,93"),
        ("anclas_con_historia_fuera_de_su_borde", "42 establecimientos"),
        ("union_de_los_41_ha", "5.434,11"), ("union_de_los_41_locales", "10.801"),
        ("locales_en_dos_o_mas_polos", "1.263"),
        ("hitos_a_250_m_o_menos_del_borde", "45 establecimientos"),
    ]

    destino = SALIDA / "cifras_canonicas.json"
    destino.write_text(json.dumps(dict(generado=HOY, cifras=cifras), ensure_ascii=False,
                                  indent=2), encoding="utf-8")
    print("=" * 98)
    print(f"CIFRAS CANÓNICAS AL DÍA · {len(cifras)} cifras "
          f"({len(nuevas)} nuevas o actualizadas en esta tanda, más polos_sin_borde)")
    print("=" * 98)
    print(f"  {'polos_sin_borde':<44}{'3':>10} polos   (era 4; Mataderos pasa a transitorio)")
    for nombre in nuevas:
        c = cifras[nombre]
        print(f"  {nombre:<44}{str(c['valor']):>10} {c['unidad']}")
    print(f"\nEscrito: {destino.name}\n")

    # --- la verificación ---------------------------------------------------------------------
    vc.CANONICAS = destino
    vc.SALIDA = SALIDA
    sys.argv = [sys.argv[0], "--json"]
    vc.main()

    # --- qué cambió contra la verificación anterior -------------------------------------------
    antes_ruta = R18 / "verificacion_cifras.json"
    ahora = json.loads((SALIDA / "verificacion_cifras.json").read_text(encoding="utf-8"))
    print("\n" + "=" * 98)
    print("QUÉ CAMBIÓ CONTRA LA VERIFICACIÓN ANTERIOR")
    print("=" * 98)
    if not antes_ruta.exists():
        print("  no hay verificación anterior con la que comparar")
        return
    antes = json.loads(antes_ruta.read_text(encoding="utf-8"))
    a_mal, h_mal = set(antes["no_coinciden"]), set(ahora["no_coinciden"])
    a_bien, h_bien = set(antes["coinciden"]), set(ahora["coinciden"])
    a_sin, h_sin = set(antes["sin_mencion"]), set(ahora["sin_mencion"])
    print(f"  antes: {len(a_mal)} no coinciden · {len(a_bien)} sí · {len(a_sin)} sin mención")
    print(f"  ahora: {len(h_mal)} no coinciden · {len(h_bien)} sí · {len(h_sin)} sin mención")
    for etiqueta, cuales in (
            ("dejaron de coincidir", sorted((h_mal - a_mal) & (a_bien | a_mal | a_sin))),
            ("empezaron a coincidir", sorted(h_bien - a_bien)),
            # Sólo las que ANTES estaban en el texto. Una cifra nueva nunca «dejó de
            # aparecer»: no existía.
            ("dejaron de aparecer en el texto", sorted((h_sin - a_sin) & (a_mal | a_bien))),
            ("aparecieron en el texto", sorted((a_sin - h_sin) & (h_bien | h_mal)))):
        print(f"\n  {etiqueta}: {len(cuales)}")
        for n in cuales:
            v = (ahora["no_coinciden"][n]["canonico"] if n in ahora["no_coinciden"]
                 else ahora["coinciden"].get(n, ""))
            print(f"      {n:<46} canónico {v}")
    print("\n  las que no coinciden hoy, una por una:")
    for n, c in sorted(ahora["no_coinciden"].items()):
        dice = sorted({m["encontrado"] for m in c["menciones_mal"]})
        print(f"      {n:<46} el texto dice {', '.join(dice)[:40]:<42} "
              f"la fuente dice {c['canonico']}")

    # --- ¿están escritas, en algún documento, las cifras de las dos últimas tandas? ----------
    print("\n" + "=" * 98)
    print("¿ESTÁN ESCRITAS EN ALGÚN DOCUMENTO? · búsqueda de la cadena exacta")
    print("=" * 98)
    documentos = [d for d in vc.DOCUMENTOS if d.exists()]
    print(f"  {len(documentos)} documentos revisados\n")
    presencia = {}
    for nombre, literal in LITERALES:
        hallazgos = []
        for doc in documentos:
            texto = doc.read_text(encoding="utf-8")
            pos = texto.find(literal)
            while pos != -1 and len(hallazgos) < 4:
                hallazgos.append(f"{doc.name}:{texto.count(chr(10), 0, pos) + 1}")
                pos = texto.find(literal, pos + 1)
        presencia[nombre] = hallazgos
        estado = ", ".join(hallazgos) if hallazgos else "NO APARECE EN NINGUNO"
        print(f"  {nombre:<44} «{literal:<18}» {estado}")
    (SALIDA / "presencia_en_documentos.json").write_text(
        json.dumps(dict(fecha=HOY, documentos=len(documentos), presencia=presencia),
                   ensure_ascii=False, indent=2), encoding="utf-8")
    faltan = [n for n, h in presencia.items() if not h]
    print(f"\n  de las {len(LITERALES)} cifras buscadas, {len(faltan)} no están escritas en "
          f"ningún documento.")
    print(f"\nEscrito: presencia_en_documentos.json")


if __name__ == "__main__":
    main()
