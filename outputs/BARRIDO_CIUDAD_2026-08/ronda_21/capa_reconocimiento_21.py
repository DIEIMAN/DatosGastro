# -*- coding: utf-8 -*-
"""Regenerar la capa de reconocimiento que leen las páginas, y volver a contar.

QUÉ ESTABA MAL
---------------
`hitos/hitos_capa_2026.geojson` —la capa que alimenta el bloque «Para conocer» de las 41 páginas—
es una foto anterior de la capa canónica. Tiene **215 filas contra 225**, y por eso La Boca
publicaba cuatro lugares con reconocimiento cuando adentro hay tres —el Café Roma estaba cargado
dos veces— y el Centro y Microcentro publicaba veintiuno cuando adentro hay veintidós: le faltaba
el Bar Iberia. La tanda anterior lo midió y no lo tocó, porque regenerar el insumo de las páginas
no es una decisión de un control. Ahora está decidido.

QUÉ HACE ESTA CORRIDA
----------------------
  1. **Regenera la capa** desde la canónica `hitos_capa_2026_r11.csv`, con las mismas reglas con
     las que se escribió la anterior: una fila por hito con punto, en EPSG:4326.
  2. **Conserva las cinco columnas de auditoría** que la capa vieja traía y la canónica no
     —`nombre_original`, `direccion_original` y las tres de `conflicto_direccion`—, cruzando por
     `hito_id`. Las filas que entran ahora no las tienen, y en vez de rellenarlas con
     «sin_conflicto_declarado» —que sería inventar un veredicto que nadie dio— quedan marcadas
     como **`no_auditado_en_r18`**.
  3. **Vuelve a contar los lugares con reconocimiento adentro del borde de cada página**, y no
     una vez sino dos, porque las dos cuentas son distintas y las dos hacen falta:
       - contra **los bordes publicados hoy**, que es lo que confirma o refuta las dos
         correcciones hechas a mano;
       - contra **la geometría después de los cinco repartos y de la fusión**, que es lo que van
         a decir las páginas cuando las decisiones se apliquen.

     Son distintas de verdad y no por decimales: el Bar Iberia está en Av. de Mayo 1196, o sea
     adentro de la franja que el reparto A3 le pasa a Monserrat. Contra el borde de hoy suma al
     Microcentro; contra el borde de después, suma a Monserrat.

QUÉ NO TOCA
------------
`hitos/hitos_capa_2026.csv` **queda como está**. Es la entrada de la cadena que produjo r3 → …
→ r11, y pisarla con la salida de esa misma cadena la volvería irreproducible. La capa que leen
las páginas es el `.geojson`, y es la que se regenera. La versión anterior se guarda entera en
`ronda_21/geometria/` antes de escribir nada.

EPSG:5347 para medir, EPSG:4326 para guardar. Cero requests.
"""

import json
import shutil
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
sys.path.insert(0, str(BARRIDO / "ronda_20"))

import geometria_vigente_20 as gv  # noqa: E402
from geometria_vigente_20 import limpia  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()
QUE_LEEN_LAS_PAGINAS = BARRIDO / "hitos" / "hitos_capa_2026.geojson"
CANONICA = BARRIDO / "hitos" / "hitos_capa_2026_r11.csv"
REPARTIDOS = SALIDA / "geometria" / "bordes_repartidos_41.geojson"
FUNDIDOS = SALIDA / "geometria" / "bordes_39.geojson"

AUDITORIA = ["nombre_original", "direccion_original", "conflicto_direccion_original",
             "conflicto_direccion_estado", "conflicto_direccion_resolucion"]

# Lo que Diego ya corrigió a mano y esta corrida tiene que confirmar o desmentir.
A_CONFIRMAR = [("Z52", "La Boca · Almirante Brown y Necochea", 4, 3),
               ("R12", "Centro y Microcentro", 21, 22)]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 98)
    print("LA CAPA DE RECONOCIMIENTO · regenerada desde la canónica, y las cuentas de nuevo")
    print("=" * 98 + "\n")

    # Idempotencia: si el respaldo ya existe, esta corrida ya se hizo y «la vieja» es el respaldo.
    # Leer el archivo vigente como si fuera la vieja compararía la capa nueva contra sí misma y
    # devolvería «no cambió nada», que es la peor salida posible: una que parece tranquilizadora.
    respaldo = SALIDA / "geometria" / "hitos_capa_2026_ANTES_DE_LA_RONDA_21.geojson"
    if respaldo.exists():
        print(f"    (el respaldo ya existe: esta corrida ya se hizo. «La vieja» se lee de "
              f"{respaldo.name} y el respaldo no se pisa)")
        vieja = gpd.read_file(respaldo).to_crs(CRS_G)
    else:
        vieja = gpd.read_file(QUE_LEEN_LAS_PAGINAS).to_crs(CRS_G)
    canon = pd.read_csv(CANONICA)
    print(f"    la que leen las páginas : {len(vieja)} filas · {QUE_LEEN_LAS_PAGINAS.name}")
    print(f"    la canónica             : {len(canon)} filas · {CANONICA.name}")

    con_punto = canon[canon.latitud.notna() & canon.longitud.notna()].copy()
    print(f"    de la canónica tienen punto: {len(con_punto)} · las otras "
          f"{len(canon) - len(con_punto)} no entran en ninguna cuenta geométrica\n")

    # ---------------------------------------------------------------- 1 · regenerar
    print("-" * 98)
    print("1 · LA CAPA NUEVA")
    print("-" * 98)
    aud = vieja[["hito_id"] + AUDITORIA].drop_duplicates("hito_id")
    nueva = con_punto.merge(aud, on="hito_id", how="left")
    sin_auditar = nueva.conflicto_direccion_estado.isna()
    nueva.loc[sin_auditar, "nombre_original"] = nueva.loc[sin_auditar, "nombre"]
    nueva.loc[sin_auditar, "direccion_original"] = nueva.loc[sin_auditar, "direccion"]
    nueva.loc[sin_auditar, "conflicto_direccion_original"] = ""
    nueva.loc[sin_auditar, "conflicto_direccion_estado"] = "no_auditado_en_r18"
    nueva.loc[sin_auditar, "conflicto_direccion_resolucion"] = ""
    print(f"    {len(nueva)} filas · {int(sin_auditar.sum())} marcadas «no_auditado_en_r18»")

    capa = gpd.GeoDataFrame(nueva, geometry=gpd.points_from_xy(nueva.longitud, nueva.latitud),
                            crs=CRS_G)
    if not respaldo.exists():
        shutil.copy2(QUE_LEEN_LAS_PAGINAS, respaldo)
        print(f"    la versión anterior queda entera en {respaldo.name}")
    capa.to_file(QUE_LEEN_LAS_PAGINAS, driver="GeoJSON")
    print(f"    escrita {QUE_LEEN_LAS_PAGINAS.name}: {len(vieja)} → {len(capa)} filas "
          f"(+{len(capa) - len(vieja)})")

    entran = sorted(set(capa.hito_id) - set(vieja.hito_id))
    print(f"\n    entran {len(entran)} establecimientos que la capa vieja no tenía:")
    for h in entran:
        r = capa[capa.hito_id == h].iloc[0]
        print(f"        {h:<9} {str(r.nombre)[:34]:<36} {str(r.tipo)[:24]:<26} "
              f"{str(r.direccion)[:30]}")
    salen = sorted(set(vieja.hito_id) - set(capa.hito_id))
    print(f"    salen {len(salen)}" + (f": {salen}" if salen else " · ninguno"))

    movidos = []
    for h in sorted(set(capa.hito_id) & set(vieja.hito_id)):
        a = vieja[vieja.hito_id == h].iloc[0]
        b = capa[capa.hito_id == h].iloc[0]
        d = gpd.GeoSeries([a.geometry, b.geometry], crs=CRS_G).to_crs(CRS_M)
        metros = d.iloc[0].distance(d.iloc[1])
        if metros > 1.0:
            movidos.append((h, str(a.nombre), str(b.nombre), str(a.direccion),
                            str(b.direccion), round(metros, 1)))
    print(f"    cambian de punto {len(movidos)}:")
    for h, na, nb, da, db, m in movidos:
        print(f"        {h:<9} «{na}» {da}  →  «{nb}» {db}   ({m:,.1f} m)")

    # ---------------------------------------------------------------- 2 · contar
    print("\n" + "-" * 98)
    print("2 · LOS LUGARES CON RECONOCIMIENTO ADENTRO DEL BORDE DE CADA PÁGINA")
    print("-" * 98)

    publicados = gv.cargar()[0]
    nombres = {pid: str(gv.cargar()[2].polo_nombre.loc[pid]) for pid in publicados}

    def cuenta(capa_pts, bordes):
        pts = capa_pts.to_crs(CRS_M)
        salida = {}
        for pid, g in bordes.items():
            dentro = pts[pts.geometry.within(g)]
            salida[pid] = set(dentro.hito_id.astype(str))
        return salida

    antes = cuenta(vieja, publicados)
    ahora = cuenta(capa, publicados)

    filas, cambian = [], 0
    print(f"\n    contra LOS BORDES PUBLICADOS HOY:\n")
    print(f"    {'polo':<6} {'página':<40}{'vieja':>7}{'nueva':>7}  qué cambia")
    for pid in sorted(publicados):
        a, b = antes[pid], ahora[pid]
        if a != b:
            cambian += 1
        detalle = []
        for h in sorted(b - a):
            detalle.append(f"+{h} {str(capa[capa.hito_id == h].iloc[0]['nombre'])}")
        for h in sorted(a - b):
            detalle.append(f"−{h} {str(vieja[vieja.hito_id == h].iloc[0]['nombre'])}")
        if a != b:
            print(f"    {pid:<6} {nombres[pid][:38]:<40}{len(a):>7}{len(b):>7}  "
                  f"{'; '.join(detalle)}")
        filas.append(dict(polo=pid, polo_nombre=nombres[pid], geometria="borde publicado hoy",
                          cuenta_vieja=len(a), cuenta_nueva=len(b),
                          entran=" ".join(sorted(b - a)), salen=" ".join(sorted(a - b)),
                          detalle="; ".join(detalle)))
    print(f"\n    {cambian} páginas de {len(publicados)} cambian de cuenta. "
          f"Las otras {len(publicados) - cambian} quedan igual.")
    print(f"    total de lugares con reconocimiento adentro de algún borde: "
          f"{len(set().union(*antes.values()))} → {len(set().union(*ahora.values()))}")

    print(f"\n    las dos correcciones hechas a mano:")
    for pid, nom, vieja_n, nueva_n in A_CONFIRMAR:
        ok = len(antes[pid]) == vieja_n and len(ahora[pid]) == nueva_n
        print(f"        {nom:<44} {vieja_n} → {nueva_n} · medido {len(antes[pid])} → "
              f"{len(ahora[pid])} · {'CONFIRMA' if ok else 'NO CONFIRMA'}")
        if not ok:
            print(f"            adentro con la capa nueva: "
                  f"{', '.join(sorted(str(capa[capa.hito_id == h].iloc[0]['nombre']) for h in ahora[pid]))}")

    # --- contra la geometría de después
    if REPARTIDOS.exists() and FUNDIDOS.exists():
        despues = gpd.read_file(FUNDIDOS).to_crs(CRS_M).set_index("polo_id")
        bordes_39 = {pid: limpia(g) for pid, g in despues.geometry.items()}
        nombres39 = {pid: str(despues.polo_nombre.loc[pid]) for pid in bordes_39}
        luego = cuenta(capa, bordes_39)
        print(f"\n    contra LA GEOMETRÍA DE DESPUÉS · los cinco repartos y la fusión aplicados:\n")
        print(f"    {'polo':<12} {'página':<40}{'hoy':>6}{'después':>9}  qué se mueve")
        movidas = 0
        for pid in sorted(bordes_39, key=lambda p: -len(luego[p])):
            hoy = ahora.get(pid, set())
            if pid == "R09+R19+Z43":
                hoy = ahora.get("R09", set()) | ahora.get("R19", set()) | ahora.get("Z43", set())
            if hoy == luego[pid]:
                continue
            movidas += 1
            det = ([f"+{h}" for h in sorted(luego[pid] - hoy)]
                   + [f"−{h}" for h in sorted(hoy - luego[pid])])
            print(f"    {pid:<12} {nombres39[pid][:38]:<40}{len(hoy):>6}{len(luego[pid]):>9}  "
                  f"{'; '.join(det)}")
            filas.append(dict(polo=pid, polo_nombre=nombres39[pid],
                              geometria="después de repartos y fusión",
                              cuenta_vieja=len(hoy), cuenta_nueva=len(luego[pid]),
                              entran=" ".join(sorted(luego[pid] - hoy)),
                              salen=" ".join(sorted(hoy - luego[pid])),
                              detalle="; ".join(det)))
        print(f"\n    {movidas} páginas cambian de cuenta al aplicar las decisiones, "
              f"sobre la misma capa de reconocimiento.")
        for pid, nom, _, esperado in A_CONFIRMAR:
            if pid in luego and len(luego[pid]) != esperado:
                print(f"    OJO · {nom}: hoy cuenta {esperado} y después de los repartos "
                      f"cuenta {len(luego[pid])}. La corrección a mano vale para el borde de hoy.")
    else:
        print("\n    (falta la geometría de después: corré repartos_21.py y chacagiales_21.py)")

    pd.DataFrame(filas).to_csv(SALIDA / "reconocimiento_cuentas.csv", index=False,
                               encoding="utf-8")
    pd.DataFrame([dict(hito_id=h, nombre=str(capa[capa.hito_id == h].iloc[0]["nombre"]),
                       tipo=str(capa[capa.hito_id == h].iloc[0]["tipo"]),
                       direccion=str(capa[capa.hito_id == h].iloc[0]["direccion"]),
                       que_pasa="entra: faltaba en la capa que leen las páginas")
                 for h in entran]
                + [dict(hito_id=h, nombre=nb, tipo="", direccion=db,
                        que_pasa=f"cambia de punto {m:,.1f} m · antes «{na}» {da}")
                   for h, na, nb, da, db, m in movidos]).to_csv(
        SALIDA / "reconocimiento_diff_de_la_capa.csv", index=False, encoding="utf-8")
    (SALIDA / "reconocimiento_resumen.json").write_text(json.dumps(dict(
        fecha=HOY, capa_vieja=len(vieja), capa_nueva=len(capa),
        entran=entran, salen=salen, cambian_de_punto=[m[0] for m in movidos],
        paginas_que_cambian_de_cuenta=cambian,
        total_dentro_de_algun_borde_antes=len(set().union(*antes.values())),
        total_dentro_de_algun_borde_ahora=len(set().union(*ahora.values()))),
        ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nEscrito: {QUE_LEEN_LAS_PAGINAS.name} (regenerada) · "
          f"geometria/{respaldo.name} (la anterior) · reconocimiento_cuentas.csv · "
          f"reconocimiento_diff_de_la_capa.csv · reconocimiento_resumen.json")


if __name__ == "__main__":
    main()
