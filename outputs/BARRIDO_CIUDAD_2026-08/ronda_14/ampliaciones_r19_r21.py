# -*- coding: utf-8 -*-
"""Las dos ampliaciones decididas el 07/08, medidas antes y despues.

LO PRIMERO, PORQUE CAMBIA QUE ES ESTA CORRIDA
----------------------------------------------
**Las dos ampliaciones ya estaban medidas.** `geometria_r7/ampliaciones_r7.csv` y
`geometria_r7/AMPLIACIONES_R7.txt` las corrieron el 08/08 con la misma regla —union con el viejo,
buffer de 150 m, contencion por superficie perdida— y los poligonos resultantes viajaron a
`referencias_r7.geojson` y de ahi a `referencias_r8.geojson`. El pendiente 6 del tablero pide algo
que esta hecho. Es la sexta vez que pasa lo mismo en este proyecto y por la misma causa.

Asi que esta corrida deja de ser una medicion nueva y pasa a ser lo que corresponde: **una
reproduccion independiente**. Se rehizo desde el texto de las decisiones, sin abrir el resultado de
la ronda 7 hasta despues de tener numeros propios. Una de las dos reproduce exacto y la otra no.

QUE PIDEN LAS DOS DECISIONES
----------------------------
  decision 6 · R19 Federico Lacroze  "El reconocimiento externo recae sobre Fraga, Dorrego,
      Charlone y Jorge Newbery y sobre el entorno de Plaza Los Andes, NO sobre la Av. Federico
      Lacroze. Ampliar hacia esos ejes."
  decision 8 · R21 La Paternal       "La prensa situa el circuito sobre Belaustegui, Remedios de
      Escalada, Paz Soldan, Rojas, Avalos, Espinosa y Terrero, hacia el limite con Villa Crespo."

LA CONTENCION SE MIDE POR SUPERFICIE PERDIDA, NO POR PREDICADO
--------------------------------------------------------------
`covers()` es un predicado exacto sobre coordenadas de punto flotante y devuelve False en casos que
si contienen. Ya paso con Palermo —predicado False, superficie perdida 0,0 m2—. Se reportan los dos
y manda la superficie: `area(viejo - nuevo)`.

**La prueba no es vacia aunque el nuevo se construya como union con el viejo.** Lo que puede comerse
superficie no es la union: es la reparacion. `buffer(0)` sobre una geometria invalida descarta lo
que no puede resolver y no avisa.

COMO SE RESUELVE CADA CALLE · Y ES ACA DONDE ESTA LA DIFERENCIA CON LA RONDA 7
------------------------------------------------------------------------------
Convertir "Dorrego" en geometria tiene dos trampas conocidas, y cada corrida cayo en una:

  1. **El nombre.** El callejero parte un mismo eje en varios `nomoficial`: DORREGO y DORREGO AV.
     son dos registros. Buscar el nombre exacto devuelve medio corredor. Lo documenta
     `callejero_canonico.py`... escrito en la ronda 10, **tres rondas despues de la ronda 7**, que
     por eso busco los nombres exactos.
  2. **El barrio.** Filtrar por la columna `barrio` pierde los tramos donde la calle ES el limite
     entre dos barrios: ahi la columna trae uno solo o ninguno. La ronda 7 ya lo sabia y por eso
     recorta contra el POLIGONO del barrio. Esta corrida cayo en esa trampa en su primera pasada.

Aca se usan las dos correcciones juntas —raiz canonica **y** recorte contra el poligono— y se
reportan las tres resoluciones lado a lado, calle por calle, para que la diferencia se vea en el
caso y no en el agregado.

El buffer es el declarado del proyecto: 150 m, una cuadra a cada lado (`BUFFER_ENCLAVE_M`). Se
reporta la curva 50/100/150/200/300: es sensibilidad al parametro, **no** la curva de continuidad.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import sys
from pathlib import Path

import geopandas as gpd
from shapely.ops import unary_union

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"

VERDES = (ROOT / "outputs" / "polos_gastro" / "INVESTIGACION_DESBLOQUEOS_V21" / "paquete" /
          "r15_plaza_arenales" / "fuentes" / "espacios_verdes_publicos_gcba.geojson")
REFERENCIAS_R8 = BASE / "geometria_r8" / "referencias_r8.geojson"
AMPLIACIONES_R7 = BASE / "geometria_r7" / "ampliaciones_r7.csv"

BUFFER_M = 150.0
CURVA = (50, 100, 150, 200, 300)

AMPLIACIONES = {
    "R19": {
        "nombre": "Federico Lacroze",
        "decision": "6 (07/08)",
        "marco": ["Chacarita", "Colegiales"],
        # (nombre de la decision, nombre exacto que uso la ronda 7)
        "calles": [("FRAGA", "FRAGA"), ("DORREGO", "DORREGO AV."), ("CHARLONE", "CHARLONE"),
                   ("NEWBERY JORGE", "NEWBERY, JORGE")],
        "verdes": ["Parque Los Andes"],
        "vecinas": ["R09", "R01", "R08", "R09R19_CHACAGIALES"],
    },
    "R21": {
        "nombre": "La Paternal",
        "decision": "8 (07/08)",
        # Villa Crespo entra porque la decision dice "hacia el limite con Villa Crespo": tres de
        # las siete calles que nombra no existen dentro de La Paternal.
        "marco": ["Paternal", "Villa Crespo"],
        "calles": [(n, n) for n in
                   ["BELAUSTEGUI LUIS DR", "ESCALADA DE SAN MARTIN R", "PAZ SOLDAN", "ROJAS",
                    "AVALOS", "ESPINOSA", "TERRERO"]],
        "verdes": [],
        "vecinas": ["R08", "R09", "R09R19_CHACAGIALES"],
    },
}


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def piezas(g):
    return len(getattr(g, "geoms", [g]))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
    from polos_soporte import puntos_base, envolventes_22, barrios, sin_tildes  # noqa: E402
    from callejero_canonico import cargar, familias  # noqa: E402

    puntos = puntos_base()
    env = envolventes_22().set_index("referencia_id")
    r8 = gpd.read_file(REFERENCIAS_R8).to_crs(CRS_METRICO).set_index("referencia_id")
    calles = cargar()
    mapa = familias(calles)
    capa_barrios = barrios().set_index("clave")
    verdes = gpd.read_file(VERDES).to_crs(CRS_METRICO)
    r7 = {f["referencia_id"]: f for f in csv.DictReader(AMPLIACIONES_R7.open(encoding="utf-8"))}

    print("=" * 96)
    print("LAS DOS AMPLIACIONES · reproduccion independiente de la ronda 7")
    print("=" * 96)
    print(f"universo de locales: {len(puntos):,} (anillo == 'nucleo' y apto_geometria == True)")
    print(f"buffer declarado: {BUFFER_M:.0f} m\n")

    filas, filas_calles = [], []
    for rid, receta in AMPLIACIONES.items():
        viejo = limpia(env.geometry.loc[rid])
        ha_v, loc_v = viejo.area / 10_000, int(puntos.within(viejo).sum())
        marco = limpia(unary_union(
            [capa_barrios.geometry.loc[sin_tildes(b)] for b in receta["marco"]]))
        print("-" * 96)
        print(f"{rid} · {receta['nombre']} · decision {receta['decision']} · "
              f"marco {' + '.join(receta['marco'])}")
        print("-" * 96)
        print(f"ANTES: {ha_v:,.2f} ha · {loc_v} locales · {piezas(viejo)} pieza(s) · "
              f"{loc_v / ha_v:.2f} loc/ha · geometria valida={viejo.is_valid}")

        # ---- las tres resoluciones de cada calle, lado a lado ----------------------------
        print("\nCada calle, resuelta de tres maneras (metros de eje dentro del marco):\n")
        print(f"{'calle':<28}{'r7: nombre exacto':>19}{'columna barrio':>16}"
              f"{'raiz + poligono':>17}{'ya dentro':>11}")
        ejes = []
        for etiqueta, nombre_r7 in receta["calles"]:
            # A · como la ronda 7: nomoficial exacto, recortado contra el poligono del marco
            seg_a = calles[calles.clave == sin_tildes(nombre_r7)]
            m_a = (limpia(unary_union(list(seg_a.geometry))).intersection(marco).length
                   if len(seg_a) else 0.0)
            # B · la trampa de la primera pasada: raiz, pero filtrando por la COLUMNA barrio
            seg_b = calles[(calles.raiz == etiqueta) & (calles.barrio.isin(receta["marco"]))]
            m_b = limpia(unary_union(list(seg_b.geometry))).length if len(seg_b) else 0.0
            # C · lo correcto: raiz canonica (familia con contacto) recortada contra el poligono
            claves = mapa.get(sin_tildes(nombre_r7), {sin_tildes(nombre_r7)})
            seg_c = calles[calles.clave.isin(claves)]
            geom_c = limpia(unary_union(list(seg_c.geometry))).intersection(marco)
            m_c = geom_c.length
            if m_c:
                ejes.append(geom_c)
            dentro = geom_c.intersection(viejo).length
            print(f"{etiqueta:<28}{m_a:>19,.0f}{m_b:>16,.0f}{m_c:>17,.0f}{dentro:>11,.0f}")
            filas_calles.append(dict(
                referencia=rid, calle=etiqueta, nombre_en_la_ronda_7=nombre_r7,
                metros_r7_nombre_exacto=round(m_a), metros_columna_barrio=round(m_b),
                metros_raiz_canonica_y_poligono=round(m_c), metros_ya_dentro_del_viejo=round(dentro),
                nombres_oficiales_de_la_familia=" + ".join(sorted(claves))))

        for nombre_verde in receta["verdes"]:
            sel = verdes[verdes.nombre.map(sin_tildes) == sin_tildes(nombre_verde)]
            geom = limpia(unary_union(list(sel.geometry))) if len(sel) else None
            if geom is None:
                print(f"{nombre_verde:<28}{'NO ESTA EN LA CAPA DE ESPACIOS VERDES':>63}")
                continue
            ejes.append(geom)
            print(f"{nombre_verde:<28}{geom.area / 10_000:>18,.2f} ha"
                  f"{'(espacio verde)':>16}{'':>17}{viejo.distance(geom):>8,.0f} m")
            filas_calles.append(dict(
                referencia=rid, calle=nombre_verde, nombre_en_la_ronda_7=nombre_verde,
                metros_r7_nombre_exacto="", metros_columna_barrio="",
                metros_raiz_canonica_y_poligono=f"{geom.area / 10_000:.2f} ha de parque",
                metros_ya_dentro_del_viejo=f"a {viejo.distance(geom):.0f} m del poligono viejo",
                nombres_oficiales_de_la_familia=f"nombre oficial GCBA: {sel.iloc[0]['nombre']}"))

        # ---- sensibilidad al buffer -------------------------------------------------------
        print("\nSensibilidad al buffer (no es la curva de continuidad):\n")
        print(f"{'buffer':>8}{'ha':>12}{'locales':>10}{'loc/ha':>9}{'piezas':>8}"
              f"{'superficie perdida':>21}")
        for radio in CURVA:
            nuevo = limpia(unary_union([viejo] + [e.buffer(radio) for e in ejes]))
            perdida = limpia(viejo.difference(nuevo)).area
            loc_n = int(puntos.within(nuevo).sum())
            marca = "  <<< el declarado" if radio == BUFFER_M else ""
            print(f"{radio:>7} m{nuevo.area / 10_000:>12,.2f}{loc_n:>10}"
                  f"{loc_n / (nuevo.area / 10_000):>9.2f}{piezas(nuevo):>8}"
                  f"{perdida:>18,.4f} m2{marca}")

        # ---- la ampliacion, al buffer declarado -------------------------------------------
        nuevo = limpia(unary_union([viejo] + [e.buffer(BUFFER_M) for e in ejes]))
        ha_n, loc_n = nuevo.area / 10_000, int(puntos.within(nuevo).sum())
        perdida = limpia(viejo.difference(nuevo)).area
        predicado = nuevo.covers(viejo)
        print(f"\nDESPUES: {ha_n:,.2f} ha · {loc_n} locales · {piezas(nuevo)} pieza(s) · "
              f"{loc_n / ha_n:.2f} loc/ha")
        print(f"  delta: {ha_n - ha_v:+,.2f} ha ({(ha_n / ha_v - 1) * 100:+.1f} %) · "
              f"{loc_n - loc_v:+d} locales ({(loc_n / loc_v - 1) * 100:+.1f} %) · "
              f"densidad {loc_n / ha_n - loc_v / ha_v:+.2f} loc/ha")
        print(f"  CONTENCION · superficie del viejo que queda afuera: {perdida:,.4f} m2   "
              f"(el predicado covers() dice {predicado})")

        # ---- contra la ronda 7 -------------------------------------------------------------
        vieja_r7 = r7.get(rid)
        if vieja_r7:
            ha_r7, loc_r7 = float(vieja_r7["ha_despues"]), int(vieja_r7["locales_despues"])
            acuerdo = abs(ha_n - ha_r7) < 0.1 and loc_n == loc_r7
            print(f"\n  Contra la ronda 7: {ha_r7:,.2f} ha · {loc_r7} locales   -> "
                  f"{'REPRODUCE' if acuerdo else 'NO REPRODUCE'}"
                  f"  (delta {ha_n - ha_r7:+,.2f} ha · {loc_n - loc_r7:+d} locales)")

        # ---- contra lo que hoy esta en la capa r8 -------------------------------------------
        if rid in r8.index:
            g_r8 = limpia(r8.geometry.loc[rid])
            print(f"  Contra referencias_r8: {g_r8.area / 10_000:,.2f} ha · "
                  f"{int(puntos.within(g_r8).sum())} locales · "
                  f"diferencia simetrica {limpia(g_r8.symmetric_difference(nuevo)).area:,.1f} m2")
        else:
            print(f"  {rid} NO esta en referencias_r8: la ronda 8 lo fusiono.")

        # ---- solapes -------------------------------------------------------------------------
        print("\n  Solape con las vecinas, antes y despues:")
        vecindad = []
        for otra in receta["vecinas"]:
            fuente = env if otra in env.index else (r8 if otra in r8.index else None)
            if fuente is None:
                continue
            g_otra = limpia(fuente.geometry.loc[otra])
            antes = limpia(viejo.intersection(g_otra)).area / 10_000
            despues = limpia(nuevo.intersection(g_otra)).area / 10_000
            cubierto = despues / (nuevo.area / 10_000) * 100
            print(f"    {otra:<22}{antes:>9,.2f} ha  ->{despues:>9,.2f} ha  "
                  f"({despues - antes:+,.2f}) · el {cubierto:.0f} % del poligono nuevo")
            vecindad.append(f"{otra}: {antes:.2f} -> {despues:.2f} ha")
            # Si la vecina es la fusion que se comio a esta referencia, lo que importa no es el
            # solape sino lo que SOBRA: la parte de la ampliacion que la fusion no cubre.
            if otra == "R09R19_CHACAGIALES" and rid == "R19":
                sobra = limpia(nuevo.difference(g_otra))
                print(f"      -> lo que la ampliacion agrega FUERA de la fusion: "
                      f"{sobra.area / 10_000:,.2f} ha · {int(puntos.within(sobra).sum())} locales "
                      f"en {piezas(sobra)} pieza(s)")
                vecindad.append(f"fuera de la fusion: {sobra.area / 10_000:.2f} ha / "
                                f"{int(puntos.within(sobra).sum())} locales")

        filas.append(dict(
            referencia=rid, nombre=receta["nombre"], decision=receta["decision"],
            ha_antes=round(ha_v, 2), locales_antes=loc_v, piezas_antes=piezas(viejo),
            ha_despues=round(ha_n, 2), locales_despues=loc_n, piezas_despues=piezas(nuevo),
            delta_ha=round(ha_n - ha_v, 2), delta_locales=loc_n - loc_v,
            loc_ha_antes=round(loc_v / ha_v, 2), loc_ha_despues=round(loc_n / ha_n, 2),
            superficie_perdida_m2=round(perdida, 4), predicado_covers=predicado,
            ha_ronda_7=vieja_r7["ha_despues"] if vieja_r7 else "",
            locales_ronda_7=vieja_r7["locales_despues"] if vieja_r7 else "",
            reproduce_la_ronda_7=(abs(ha_n - float(vieja_r7["ha_despues"])) < 0.1
                                  and loc_n == int(vieja_r7["locales_despues"])) if vieja_r7 else "",
            buffer_m=BUFFER_M, marco=" + ".join(receta["marco"]),
            solape_vecinas=" · ".join(vecindad)))
        print()

    for destino, datos, campos in [
        (SALIDA / "ampliaciones_r19_r21.csv", filas,
         ["referencia", "nombre", "decision", "ha_antes", "locales_antes", "piezas_antes",
          "ha_despues", "locales_despues", "piezas_despues", "delta_ha", "delta_locales",
          "loc_ha_antes", "loc_ha_despues", "superficie_perdida_m2", "predicado_covers",
          "ha_ronda_7", "locales_ronda_7", "reproduce_la_ronda_7", "buffer_m", "marco",
          "solape_vecinas"]),
        (SALIDA / "ampliaciones_calles_nombradas.csv", filas_calles,
         ["referencia", "calle", "nombre_en_la_ronda_7", "metros_r7_nombre_exacto",
          "metros_columna_barrio", "metros_raiz_canonica_y_poligono",
          "metros_ya_dentro_del_viejo", "nombres_oficiales_de_la_familia"]),
    ]:
        with destino.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=campos)
            w.writeheader()
            w.writerows(datos)
        print(f"Escrito: {destino.name} ({len(datos)} filas)")


if __name__ == "__main__":
    main()
