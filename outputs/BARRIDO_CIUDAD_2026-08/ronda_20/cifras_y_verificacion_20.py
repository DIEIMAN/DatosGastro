# -*- coding: utf-8 -*-
"""Las cifras canónicas al día, y el documento **vigente** contra ellas.

QUÉ CAMBIA RESPECTO DE LA TANDA ANTERIOR
-----------------------------------------
La verificación anterior se corrió contra un archivo del atlas de la 01:00 que no contenía lo que
se le había incorporado. El archivo en disco ahora es de las 18:21 y sí lo contiene, así que **esta
verificación mide el documento real**. Todo lo que aparezca acá es del texto que hay.

LO QUE SE ACTUALIZA, Y POR QUÉ
------------------------------
  - **Los polos que se miden sobre su barrio son tres, no cuatro**, porque Mataderos tiene borde
    transitorio. Las dos cifras del conjunto pasan de 527 locales y 112,9 ha a **347 locales y
    41,1 ha**, verificadas contra `magnitudes_sin_perimetro.csv` fila por fila.
  - **Las cifras de conjunto se vuelven a medir con La Boca ya adoptada.** La unión de los 41, la
    suma de los 41 y los establecimientos que quedan fuera de todo borde cambian porque cambió la
    geometría. Publicar como canónica una cifra medida sobre la geometría anterior sería fijar el
    error.
  - **Se agregan las que el documento publica por primera vez** con el patrón que las encuentra en
    su frase: los pares de solape, las 53 y las 71, los bordes nuevos de Caminito, Balvanera,
    Mataderos, Villa Ortúzar y La Boca, y lo que midió esta tanda sobre el perímetro escrito.

No corrige nada. Señala; la corrección la firma quien escribe.
"""

import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
R17 = BARRIDO / "ronda_17"
R18 = BARRIDO / "ronda_18"
R19 = BARRIDO / "ronda_19"
sys.path.insert(0, str(SALIDA))
sys.path.insert(0, str(R17))
import geometria_vigente_20 as gv  # noqa: E402
import verificar_cifras as vc  # noqa: E402

HOY = date.today().isoformat()
R = "outputs/BARRIDO_CIUDAD_2026-08/ronda_20"
CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
MAGNITUDES = BARRIDO / "desde_cowork" / "evidencia_2026" / "magnitudes_sin_perimetro.csv"
LOS_TRES = ["Z41", "Z46", "Z27"]


def cifra(valor, unidad, archivo, como, patrones=(), nota="", origen="medido"):
    return dict(valor=valor, unidad=unidad, fecha_de_calculo=HOY, archivo_del_que_sale=archivo,
                como_se_calcula=como, origen=origen, patrones_en_el_texto=list(patrones),
                nota=nota)


def recontar_anclas(bordes):
    """Los establecimientos con historia que quedan fuera de SU borde, con la geometría de ahora.

    La cifra estaba medida contra la geometría anterior y La Boca la mueve: el borde que se adoptó
    se extendió justamente para contener tres de ellos. Se recuenta desde la misma tabla, cambiando
    sólo el polígono contra el que se prueba cada punto.
    """
    anclas = pd.read_csv(R18 / "anclas_dentro_y_fuera.csv")
    capa = pd.read_csv(BARRIDO / "hitos" / "hitos_capa_2026_r11.csv")
    capa = capa[capa.latitud.notna()]
    punto = {}
    for r in capa.itertuples():
        punto.setdefault(str(r.nombre), Point(r.longitud, r.latitud))
    proyectados = {}
    if punto:
        gs = gpd.GeoSeries(list(punto.values()), crs=CRS_G).to_crs(CRS_M)
        proyectados = dict(zip(punto.keys(), gs))

    con_historia = anclas[anclas.sostiene_condicion_historia == "si"].copy()
    # La página es el prefijo de `polo`, NO `zona_id`: `zona_id` es la zona de origen de la que
    # se recortó la página, y para ocho páginas son cosas distintas —las dos de La Boca salen de
    # S_LABOCA, las dos de Barracas de S_BARRACAS, el eje Sáenz de Z40—. La primera versión de
    # este recuento usó `zona_id`, no encontró esos polos entre los bordes y se quedó con el valor
    # viejo: devolvió 42 y 42, o sea «no cambió nada», que era exactamente lo que había que medir.
    con_historia["pagina"] = con_historia.polo.astype(str).str.split(" · ").str[0]
    afuera, sin_punto = [], 0
    dentro_por_pagina = {}
    for r in con_historia.itertuples():
        pid = str(r.pagina)
        pt = proyectados.get(str(r.establecimiento))
        if pt is None or pid not in bordes:
            sin_punto += 1
            # sin punto no se puede volver a medir: se conserva lo que decía la tabla
            if str(r.dentro_del_borde) == "no":
                afuera.append((pid, str(r.establecimiento)))
            else:
                dentro_por_pagina.setdefault(pid, 0)
                dentro_por_pagina[pid] += 1
            continue
        if bordes[pid].covers(pt):
            dentro_por_pagina[pid] = dentro_por_pagina.get(pid, 0) + 1
        else:
            afuera.append((pid, str(r.establecimiento)))
    paginas = sorted({p for p, _ in afuera})
    sin_ninguno = sorted(p for p in paginas if not dentro_por_pagina.get(p))
    return len(afuera), len({e for _, e in afuera}), sin_ninguno, sin_punto


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    canon = json.loads((R19 / "cifras_canonicas.json").read_text(encoding="utf-8"))
    cifras = canon["cifras"]

    solapes = json.loads((SALIDA / "solapes_resumen.json").read_text(encoding="utf-8"))
    cerca = json.loads((SALIDA / "cerca_del_borde_resumen.json").read_text(encoding="utf-8"))
    perim = json.loads((SALIDA / "perimetro_escrito_resumen.json").read_text(encoding="utf-8"))
    recorte = json.loads((SALIDA / "recorte_resumen.json").read_text(encoding="utf-8"))
    roma = json.loads((SALIDA / "cafe_roma_resumen.json").read_text(encoding="utf-8"))

    print("=" * 98)
    print("1 · LAS DOS QUE QUEDARON VIEJAS · verificadas contra la capa, no copiadas del pedido")
    print("=" * 98)
    mag = pd.read_csv(MAGNITUDES).set_index("polo_id")
    faltan = [p for p in LOS_TRES if p not in mag.index]
    if faltan:
        raise SystemExit(f"{faltan} no están en {MAGNITUDES.name}. No se corrige una canónica "
                         f"contra una fuente incompleta.")
    tres = mag.loc[LOS_TRES]
    loc = int(tres.locales_en_concentraciones.sum())
    ha = round(float(tres.ha_en_concentraciones.sum()), 2)
    for p in LOS_TRES:
        f = mag.loc[p]
        print(f"    {p:<6} {str(f.nombre):<20} {int(f.locales_en_concentraciones):>5} locales · "
              f"{float(f.ha_en_concentraciones):>7,.2f} ha concentradas · barrio "
              f"{float(f.ha_del_contenedor):>8,.2f} ha")
    print(f"    {'':6} {'suma de los tres':<20} {loc:>5} locales · {ha:>7,.2f} ha")
    print(f"\n    el documento publica «347 locales en 41,1 hectáreas»: "
          f"{'COINCIDE' if loc == 347 and abs(ha - 41.1) < 0.05 else 'NO COINCIDE'}")
    print(f"    antes valían 527 locales y 112,9 ha, con cuatro polos: Mataderos sale porque "
          f"tiene borde transitorio")

    cifras["locales_en_barrios_sin_borde"].update(
        valor=loc, fecha_de_calculo=HOY,
        archivo_del_que_sale="outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026/"
                             "magnitudes_sin_perimetro.csv",
        como_se_calcula="locales en concentraciones dentro del barrio que contiene a cada uno de "
                        "los TRES polos que se miden sobre su barrio: Núñez, Retiro y Villa Santa "
                        "Rita",
        nota="valía 527 con cuatro polos. Mataderos sale de la lista porque tiene borde "
             "transitorio, y esa es toda la diferencia",
        patrones_en_el_texto=[r"Los tres suman \*\*(?P<valor>[\d.]+) locales en"])
    cifras["ha_en_barrios_sin_borde"].update(
        valor=ha, fecha_de_calculo=HOY,
        archivo_del_que_sale="outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026/"
                             "magnitudes_sin_perimetro.csv",
        como_se_calcula="superficie concentrada en esos mismos tres barrios",
        nota="valía 112,9 con cuatro polos",
        patrones_en_el_texto=[
            r"Los tres suman \*\*[\d.]+ locales en (?P<valor>[\d.,]+) hectáreas concentradas"])

    # ---------------------------------------------------------------- 2 · lo que movió La Boca
    print("\n" + "=" * 98)
    print("2 · LO QUE MOVIÓ LA ADOPCIÓN DE LA BOCA · cifras de conjunto vueltas a medir")
    print("=" * 98)
    bordes, _, _ = gv.cargar()
    n_afuera, n_distintos, sin_ninguno, sin_punto = recontar_anclas(bordes)
    print(f"    unión de los 41            {cifras['union_de_los_41_ha']['valor']:>10,.2f} ha -> "
          f"{solapes['union_de_los_41_ha']:>10,.2f} ha")
    print(f"    unión de los 41            {cifras['union_de_los_41_locales']['valor']:>10,} "
          f"locales -> {solapes['union_de_los_41_locales']:>10,} locales")
    print(f"    con historia fuera de su borde  {cifras['anclas_con_historia_fuera_de_su_borde']['valor']:>5} "
          f"-> {n_afuera:>5}   ({n_distintos} establecimientos distintos)")
    print(f"    páginas sin ningún ancla adentro {cifras['paginas_sin_ningun_ancla_adentro']['valor']:>4} "
          f"-> {len(sin_ninguno):>5}   ({', '.join(sin_ninguno)})")
    print(f"    fuera de todo borde        {cifras['hitos_fuera_de_todo_borde']['valor']:>10} -> "
          f"{cerca['fuera_de_todo_borde']:>10}")
    print(f"    a 250 m o menos            {cifras['hitos_a_250_m_o_menos_del_borde']['valor']:>10} "
          f"-> {cerca['a_250_m_o_menos']:>10}")
    print(f"    sobre calle ya nombrada    {cifras['hitos_cerca_sobre_calle_ya_nombrada']['valor']:>10} "
          f"-> {cerca['sobre_calle_ya_nombrada']:>10}")

    # ---------------------------------------------------------------- 3 · las nuevas
    lb = next(f for f in recorte["filas"] if f["polo_id"] == "Z43")
    nuevas = {
        "la_boca_almirante_brown_ha": cifra(
            16.17, "hectáreas", f"{R}/geometria/bordes_vigentes_41.geojson",
            "el borde adoptado en esta tanda: el tramo de la obra pública extendido sobre Av. "
            "Suárez y Olavarría con las manzanas frentistas",
            [r"ya nombraba— pasa a (?P<valor>[\d.,]+) hect"],
            nota="es la lectura C que la tanda anterior midió y no adoptó. Contiene a Banchero, "
                 "La Buena Medida y el Café Roma; los otros cinco siguen afuera"),
        "la_boca_almirante_brown_locales": cifra(
            21, "locales", f"{R}/geometria/bordes_vigentes_41.geojson",
            "locales del universo anillo=nucleo & apto_geometria dentro de ese borde",
            [r"ya nombraba— pasa a [\d.,]+ hectáreas y (?P<valor>[\d.]+) locales"]),
        "suma_de_los_41_locales": cifra(
            solapes["suma_de_los_41_locales"], "locales", f"{R}/solapes_declarados.csv",
            "la suma de los 41 bordes por separado, contando dos veces lo que se pisa",
            [r"Sumar los 41 por separado da \*\*(?P<valor>[\d.]+) locales"],
            nota="sube 18 contra la tanda anterior por la adopción de La Boca. No es una cifra "
                 "publicable por sí sola: existe para poder restarla"),
        "paginas_con_perimetro_reconstruible": cifra(
            len(perim["reconstruible"]["si"]), "páginas", f"{R}/perimetro_escrito_41.csv",
            "páginas cuyo bloque «Dónde está» da las piezas y su extensión, de modo que el borde "
            "publicado sale de aplicarle la regla de las manzanas frentistas y nada más",
            nota=f"otras {len(perim['reconstruible']['en parte'])} lo dan en parte y "
                 f"{len(perim['reconstruible']['no'])} no lo dan"),
        "paginas_con_calles_y_alturas": cifra(
            len(perim["por_categoria"]["da calles y alturas"]), "páginas",
            f"{R}/perimetro_escrito_41.csv",
            "páginas cuyo perímetro escrito nombra calles y da números de puerta"),
        "paginas_sin_ninguna_calle_escrita": cifra(
            perim["sin_ninguna_calle"], "páginas", f"{R}/perimetro_escrito_41.csv",
            "páginas cuyo bloque «Dónde está» no nombra ninguna calle",
            nota="dos de ellas no escriben perímetro de ninguna clase: el bloque entero dice "
                 "«Perímetro vigente.»"),
        "polos_que_publican_el_poligono_de_su_barrio": cifra(
            len(recorte["filas"]), "polos", f"{R}/recorte_de_los_cuatro.csv",
            "polos cuyo contorno publicado coincide con el polígono administrativo de su barrio, "
            "medido por superficie perdida en los dos sentidos",
            nota="son cuatro y no tres: Núñez coincide exacto —0 m² por los dos lados—, Villa "
                 "Santa Rita y Colegiales al 99,9 %, y Retiro es el barrio más las 15,62 ha del "
                 "núcleo coreano, que caen en San Nicolás. Colegiales se declara en esta tanda: "
                 "la capa lo trae como borde propio"),
        "colegiales_recorte_de_adentro_ha": cifra(
            lb["ha_del_recorte_de_adentro"], "hectáreas",
            f"{R}/recorte_de_los_cuatro.csv",
            "el recorte más chico de adentro que contiene las concentraciones del barrio, por "
            "manzanas frentistas de las cuadras donde están sus locales",
            nota="medido y no adoptado. Su página ya declara que «todavía no está dibujado el "
                 "recorte más chico de adentro»"),
    }

    # las que ya existían y esta tanda vuelve a medir o le pone patrón
    cifras["union_de_los_41_ha"].update(
        valor=solapes["union_de_los_41_ha"], fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/solapes_declarados.csv",
        patrones_en_el_texto=[r"la unión real es de \*\*[\d.]+ locales en (?P<valor>[\d.]+) hect"],
        nota="vuelta a medir con La Boca ya adoptada: sube 10,04 ha. El documento la escribe "
             "redondeada a hectáreas enteras y el comparador de este control tiene una tolerancia "
             "fija de 0,1, así que para que coincida hay que escribirla con decimales")
    cifras["union_de_los_41_locales"].update(
        valor=solapes["union_de_los_41_locales"], fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/solapes_declarados.csv",
        patrones_en_el_texto=[r"la unión real es de \*\*(?P<valor>[\d.]+) locales en"],
        nota="vuelta a medir con La Boca ya adoptada: sube 18 locales")
    cifras["locales_contados_dos_veces"].update(
        valor=solapes["se_cuentan_de_mas_locales"], fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/solapes_declarados.csv")
    cifras["locales_en_dos_o_mas_polos"].update(
        valor=solapes["locales_en_dos_o_mas_polos"], fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/solapes_locales_detalle.csv",
        patrones_en_el_texto=[r"La diferencia son \*\*(?P<valor>[\d.]+) locales que"],
        nota="el número es correcto y la palabra con la que el documento lo presenta no: lo llama "
             "«la diferencia» entre la suma y la unión, y esa diferencia son 1.286. Son dos cosas "
             "distintas: 1.263 locales distintos están en dos o más polos, y como algunos están "
             "en tres, la resta da 1.286")
    cifras["pares_de_polos_con_solape"].update(
        valor=solapes["pares_con_solape"], fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/solapes_declarados.csv",
        patrones_en_el_texto=[
            r"\*\*(?P<valor>[A-Za-zÁÉÍÓÚáéíóúñ]+) pares de polos comparten superficie"])
    cifras["concentraciones_dentro_de_un_polo"].update(
        valor=solapes["concentraciones_dentro_de_un_polo"], fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/correspondencia_124_x_41.csv",
        patrones_en_el_texto=[r"\*\*(?P<valor>\d+) de las 124 concentraciones están adentro"])
    cifras["concentraciones_fuera_de_todo_polo"].update(
        valor=solapes["concentraciones_fuera"], fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/correspondencia_124_x_41.csv",
        patrones_en_el_texto=[
            r"de las 124 concentraciones están adentro de un polo y (?P<valor>\d+) no"])
    cifras["la_boca_caminito_ha"]["patrones_en_el_texto"] = [
        r"Borde cerrado en esta edición: (?P<valor>[\d.,]+) hectáreas y [\d.]+ locales\.\*\* Es "
        r"Caminito"]
    cifras["la_boca_caminito_locales"]["patrones_en_el_texto"] = [
        r"Borde cerrado en esta edición: [\d.,]+ hectáreas y (?P<valor>[\d.]+) locales\.\*\* Es "
        r"Caminito"]
    cifras["mataderos_tentativo_ha"]["patrones_en_el_texto"] = [
        r"primera aproximación: (?P<valor>[\d.,]+) hectáreas y [\d.]+ locales"]
    cifras["mataderos_tentativo_locales"]["patrones_en_el_texto"] = [
        r"primera aproximación: [\d.,]+ hectáreas y (?P<valor>[\d.]+) locales"]
    cifras["balvanera_lectura_enclave_ha"]["patrones_en_el_texto"] = [
        r"el enclave solo\*\*: \*\*(?P<valor>[\d.,]+) hect"]
    cifras["villa_ortuzar_ha"]["patrones_en_el_texto"] = [
        r"Borde cerrado en esta edición: (?P<valor>[\d.,]+) hectáreas y [\d.]+ locales\*\*, "
        r"leyendo"]
    cifras["villa_ortuzar_locales"]["patrones_en_el_texto"] = [
        r"Borde cerrado en esta edición: [\d.,]+ hectáreas y (?P<valor>[\d.]+) locales\*\*, "
        r"leyendo"]
    cifras["anclas_con_historia_fuera_de_su_borde"].update(
        valor=n_afuera, fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/geometria/bordes_vigentes_41.geojson",
        nota=f"recontado con la geometría de ahora: eran 42 y la adopción de La Boca mete a tres "
             f"adentro. Son {n_distintos} establecimientos distintos")
    cifras["paginas_sin_ningun_ancla_adentro"].update(
        valor=len(sin_ninguno), fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/geometria/bordes_vigentes_41.geojson",
        nota=f"eran cinco; La Boca sale de la lista al adoptar su borde. Quedan "
             f"{', '.join(sin_ninguno)}")
    cifras["hitos_fuera_de_todo_borde"].update(
        valor=cerca["fuera_de_todo_borde"], fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/cerca_del_borde_20.csv",
        nota="eran 80 contra la geometría anterior y contra una foto vieja de la capa. Salen los "
             "tres que La Boca ahora contiene y entran cuatro que la foto no tenía")
    cifras["hitos_a_250_m_o_menos_del_borde"].update(
        valor=cerca["a_250_m_o_menos"], fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/cerca_del_borde_20.csv",
        nota="43 filas y 43 establecimientos: leída la capa canónica, el Café Roma ya no está "
             "cargado dos veces")
    cifras["hitos_cerca_sobre_calle_ya_nombrada"].update(
        valor=cerca["sobre_calle_ya_nombrada"], fecha_de_calculo=HOY,
        archivo_del_que_sale=f"{R}/cerca_del_borde_20.csv",
        nota="eran 12. Bajan a 7 porque la prueba se corre contra el bloque «Dónde está» de la "
             "página publicada y no contra la ficha de trabajo: la de la ficha daba positivo para "
             "Av. Alvear en Retiro, y lo que la página nombra es M. T. de Alvear, que es otra "
             "calle")
    cifras.update(nuevas)

    destino = SALIDA / "cifras_canonicas.json"
    destino.write_text(json.dumps(dict(generado=HOY, cifras=cifras), ensure_ascii=False,
                                  indent=2), encoding="utf-8")
    print("\n" + "=" * 98)
    print(f"3 · CIFRAS CANÓNICAS AL DÍA · {len(cifras)} cifras ({len(nuevas)} nuevas)")
    print("=" * 98)
    for nombre in nuevas:
        c = cifras[nombre]
        print(f"    {nombre:<46}{str(c['valor']):>10} {c['unidad']}")
    print(f"\nEscrito: {destino.name}\n")

    # ---------------------------------------------------------------- 4 · la verificación
    vc.CANONICAS = destino
    vc.SALIDA = SALIDA
    sys.argv = [sys.argv[0], "--json"]
    vc.main()

    antes = json.loads((R19 / "verificacion_cifras.json").read_text(encoding="utf-8"))
    ahora = json.loads((SALIDA / "verificacion_cifras.json").read_text(encoding="utf-8"))
    print("\n" + "=" * 98)
    print("QUÉ CAMBIÓ CONTRA LA VERIFICACIÓN ANTERIOR")
    print("=" * 98)
    print("  Con una salvedad que hay que leer antes: la anterior se corrió contra un documento")
    print("  que no tenía lo de la tanda previa. La comparación dice qué cambió entre las dos")
    print("  corridas, y buena parte de lo que cambió es que ahora hay texto donde no había.")
    a_mal, h_mal = set(antes["no_coinciden"]), set(ahora["no_coinciden"])
    a_bien, h_bien = set(antes["coinciden"]), set(ahora["coinciden"])
    a_sin, h_sin = set(antes["sin_mencion"]), set(ahora["sin_mencion"])
    print(f"\n  antes: {len(a_mal)} no coinciden · {len(a_bien)} sí · {len(a_sin)} sin mención")
    print(f"  ahora: {len(h_mal)} no coinciden · {len(h_bien)} sí · {len(h_sin)} sin mención")
    for etiqueta, cuales in (
            ("empezaron a aparecer en el texto", sorted((a_sin - h_sin) & (h_bien | h_mal))),
            ("empezaron a coincidir", sorted(h_bien - a_bien)),
            ("dejaron de coincidir", sorted(h_mal - a_mal))):
        print(f"\n  {etiqueta}: {len(cuales)}")
        for n in cuales:
            v = (ahora["no_coinciden"][n]["canonico"] if n in ahora["no_coinciden"]
                 else ahora["coinciden"].get(n, ""))
            print(f"      {n:<48} canónico {v}")

    print("\n" + "-" * 98)
    print(f"LAS QUE NO COINCIDEN HOY · {len(ahora['no_coinciden'])}")
    print("-" * 98)
    for n, c in sorted(ahora["no_coinciden"].items()):
        dice = sorted({m["encontrado"] for m in c["menciones_mal"]})
        donde = sorted({f"{m['archivo'].split('/')[-1]}:{m['linea']}"
                        for m in c["menciones_mal"]})[:3]
        print(f"  {n}")
        print(f"      el texto dice {', '.join(dice)}   ·   la fuente dice {c['canonico']} "
              f"{c['unidad']}")
        print(f"      en {', '.join(donde)}")

    resumen = dict(fecha=HOY, no_coinciden=len(ahora["no_coinciden"]),
                   coinciden=len(ahora["coinciden"]), sin_mencion=len(ahora["sin_mencion"]),
                   cafe_roma=roma)
    (SALIDA / "verificacion_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nEscrito: verificacion_cifras.json · verificacion_resumen.json")


if __name__ == "__main__":
    main()
