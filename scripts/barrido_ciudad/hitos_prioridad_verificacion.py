"""Ronda 4 · qué hito verificar primero: los que deciden una fila y los que rinden en muchas.

EL PROBLEMA
-----------
La vía B quedó en 7 confirmadas de 94 con 37 pendientes, y entre las filas que **tienen** hitos el
82 % está sin verificar. Ese es el cuello de botella. No se resuelve verificando 220 hitos: se
resuelve verificando los que deciden algo.

«Decidir algo» acá tiene una definición operativa y no una intuición:

    FRÁGIL      la vía B de la fila cuelga de UN SOLO hito. Si ese hito cerró, la fila no baja de
                grado: se cae entera y pasa a `extinguido`. Es exactamente lo que pasó con P008
                Barracas y Los Laureles, y por eso la ronda 3 tuvo que revertirla.

    RINDE       el hito está adentro de varias filas. Una sola verificación mueve todas: en la
                matriz las filas se superponen, y un bar que está en tres envolventes es una
                consulta y tres celdas.

LOS DOS PODERES DE UN HITO, QUE NO SON EL MISMO
------------------------------------------------
    abre    si se lo verifica ABIERTO, cuántas filas pasan de `pendiente` a `activo` de una vez.
            Cualquier fila que lo contenga y hoy no tenga ningún hito verificado abierto.

    cierra  si se lo verifica CERRADO, cuántas filas quedan RESUELTAS —no abiertas: resueltas—
            porque era el último sin verificar que les quedaba.

El segundo es el que la ronda 3 aprendió a respetar: una fila con un cerrado y un sin verificar no
es extinguida, así que un `no` sólo cierra la fila cuando no queda nada más por mirar.

LO QUE ESTE SCRIPT NO HACE
---------------------------
No verifica nada. No consulta ninguna fuente, no abre ninguna URL, no llama a ningún servicio: lee
la capa de la ronda 3 y ordena el trabajo. La verificación documental es la ronda que viene, y
sale de estas dos listas.

Google Places: 0 requests. USIG: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/hitos_prioridad_verificacion.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import (  # noqa: E402
    BARRIDO,
    CRS_GEOGRAFICO,
    CRS_METRICO,
    envolventes_22,
    soportes_94,
)

OUT = BARRIDO / "seis_vias"
HITOS = BARRIDO / "hitos"
CAPA_R3 = HITOS / "hitos_capa_2026_r3.csv"

# Los estados que dejan trabajo pendiente. `dudosa` cuenta como pendiente —hay motivo positivo para
# dudar y nadie miró— y `en_disputa` también: dos fuentes se contradicen y ninguna gana sola.
PENDIENTES = ("sin_verificar", "dudosa", "en_disputa")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    if not CAPA_R3.exists():
        raise SystemExit("falta hitos_capa_2026_r3.csv — correr hitos_ronda_3_vigencia.py")

    capa = pd.read_csv(CAPA_R3)
    con_punto = capa[capa.latitud.notna() & capa.longitud.notna()].copy()
    hitos = gpd.GeoDataFrame(
        con_punto, geometry=gpd.points_from_xy(con_punto.longitud, con_punto.latitud),
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO).reset_index(drop=True)

    soportes = soportes_94()
    zonas = envolventes_22()

    p("RONDA 4 · PRIORIDAD DE VERIFICACIÓN · QUÉ HITO MUEVE LA MATRIZ")
    p("=" * 100)
    p("")
    p(f"  capa: {len(capa)} hitos · {len(hitos)} con punto · "
      f"{int(capa.vigencia_verificada.isin(PENDIENTES).sum())} en algún estado pendiente")
    p("  No se verifica nada acá: se ordena el trabajo. 0 consultas a cualquier servicio.")
    p("")

    # ---------------------------------------------------------------- el cruce hito × fila
    dentro_94 = gpd.sjoin(hitos, soportes[["polo_id", "nombre_polo", "geometry"]],
                          predicate="within", how="inner")
    dentro_22 = gpd.sjoin(hitos, zonas[["referencia_id", "nombre", "geometry"]],
                          predicate="within", how="inner")

    # Una fila puede contener al mismo hito una sola vez; un hito puede estar en varias filas, y
    # eso es el punto entero de la lista 2.
    por_fila = []
    for identificador, grupo in dentro_94.groupby("polo_id"):
        estados = list(grupo.vigencia_verificada.astype(str))
        por_fila.append({
            "polo_id": identificador,
            "nombre_polo": grupo.nombre_polo.iloc[0],
            "n_hitos": len(grupo),
            "n_pendientes": sum(1 for e in estados if e in PENDIENTES),
            "n_abiertos": estados.count("si"),
            "n_cerrados": estados.count("no"),
            "n_en_disputa": estados.count("en_disputa"),
            "hitos": "; ".join(sorted(grupo.nombre.astype(str))),
            "hito_ids": "; ".join(sorted(grupo.hito_id.astype(str))),
            "estados": "; ".join(f"{n}={e}" for n, e in
                                 sorted(zip(grupo.nombre.astype(str), estados))),
        })
    filas = pd.DataFrame(por_fila)

    # El estado de vía B de la fila, con la misma precedencia de la ronda 3.
    def soporte(fila) -> str:
        if fila.n_abiertos and fila.n_cerrados:
            return "mixto"
        if fila.n_abiertos:
            return "activo"
        if fila.n_en_disputa:
            return "en_disputa"
        if fila.n_pendientes:
            return "sin_verificar"
        return "extinguido"

    filas["via_B_soporte"] = filas.apply(soporte, axis=1)
    filas["decidida_por_un_solo_hito"] = (filas.n_hitos == 1)
    filas["ultimo_pendiente"] = (filas.n_pendientes == 1) & (filas.n_abiertos == 0)

    p("-" * 100)
    p("  DE DÓNDE SALE EL CUELLO DE BOTELLA")
    p("")
    p(f"      filas de las 94 con al menos un hito adentro: {len(filas)}")
    for valor, cuantas in filas.via_B_soporte.value_counts().items():
        p(f"            {valor:<16}{cuantas:>4}")
    p("")

    # ================================================================ LISTA 1 · las frágiles
    fragiles = filas[filas.decidida_por_un_solo_hito].copy()
    fragiles = fragiles.merge(
        hitos[["hito_id", "nombre", "tipo", "direccion", "barrio_declarado",
               "vigencia_verificada", "vigencia_fecha", "es_patrimonio_normativo"]].rename(
            columns={"nombre": "hito", "vigencia_verificada": "estado_del_hito"}),
        left_on="hito_ids", right_on="hito_id", how="left")
    orden_estado = {"sin_verificar": 0, "dudosa": 1, "en_disputa": 2, "si": 3, "no": 4}
    fragiles["orden"] = fragiles.estado_del_hito.map(orden_estado).fillna(9)
    fragiles = fragiles.sort_values(["orden", "polo_id"])

    p("-" * 100)
    p("  LISTA 1 · LAS FRÁGILES · la vía B de la fila cuelga de UN SOLO hito")
    p("")
    p(f"      {len(fragiles)} filas de las {len(filas)} con hitos dependen de uno solo.")
    p(f"      De ésas, {int(fragiles.estado_del_hito.isin(PENDIENTES).sum())} tienen ese único "
      "hito sin resolver: verificarlo decide la fila entera,")
    p("      en cualquiera de los dos sentidos. Es el caso P008 / Los Laureles, que ya nos costó")
    p("      una reversión.")
    p("")
    p(f"      {'fila':<24}{'polo':<26}{'hito':<30}{'estado':<15}qué pasa si")
    for fila in fragiles.itertuples():
        if fila.estado_del_hito in PENDIENTES:
            consecuencia = "abierto→activo · cerrado→EXTINGUIDA"
        elif fila.estado_del_hito == "si":
            consecuencia = "ya resuelta (activo)"
        else:
            consecuencia = "ya resuelta (extinguida)"
        p(f"      {str(fila.polo_id)[:23]:<24}{str(fila.nombre_polo)[:25]:<26}"
          f"{str(fila.hito)[:29]:<30}{str(fila.estado_del_hito):<15}{consecuencia}")
    p("")

    # El escalón siguiente: dos hitos, uno ya cerrado. Frágil de hecho aunque no de conteo.
    casi = filas[(~filas.decidida_por_un_solo_hito) & filas.ultimo_pendiente]
    p(f"      Y el escalón de al lado, que la consigna no pide y conviene tener: {len(casi)} filas")
    p("      con más de un hito donde queda UN SOLO pendiente y ninguno abierto. Verificar ése")
    p("      cierra la fila sin margen: si da cerrado, la fila queda extinguida completa.")
    for fila in casi.itertuples():
        p(f"            {str(fila.polo_id)[:23]:<24}{str(fila.nombre_polo)[:25]:<26}"
          f"{fila.n_hitos} hitos · {fila.estados[:52]}")
    p("")

    # ================================================================ LISTA 2 · los que rinden
    conteo = dentro_94.groupby("hito_id").agg(
        filas_94=("polo_id", "nunique"),
        cuales_94=("polo_id", lambda s: "; ".join(sorted(set(s)))),
    ).reset_index()
    conteo22 = dentro_22.groupby("hito_id").agg(
        zonas_22=("referencia_id", "nunique"),
        cuales_22=("referencia_id", lambda s: "; ".join(sorted(set(s)))),
    ).reset_index()

    estado_por_fila = filas.set_index("polo_id").via_B_soporte.to_dict()
    ultimo_por_fila = filas.set_index("polo_id").ultimo_pendiente.to_dict()

    poder = []
    for hito_id, grupo in dentro_94.groupby("hito_id"):
        suyas = list(grupo.polo_id)
        abre = sum(1 for f in suyas if estado_por_fila.get(f) in ("sin_verificar", "en_disputa"))
        cierra = sum(1 for f in suyas if ultimo_por_fila.get(f, False))
        poder.append({"hito_id": hito_id, "filas_que_abre_si_abre": abre,
                      "filas_que_resuelve_si_cierra": cierra})
    poder = pd.DataFrame(poder)

    rendimiento = (hitos[["hito_id", "nombre", "tipo", "direccion", "barrio_declarado",
                          "vigencia_verificada", "vigencia_fecha", "vigencia_fuente",
                          "es_patrimonio_normativo", "es_alta_2026_08_03"]]
                   .merge(conteo, on="hito_id", how="left")
                   .merge(conteo22, on="hito_id", how="left")
                   .merge(poder, on="hito_id", how="left"))
    for columna in ("filas_94", "zonas_22", "filas_que_abre_si_abre",
                    "filas_que_resuelve_si_cierra"):
        rendimiento[columna] = rendimiento[columna].fillna(0).astype(int)
    rendimiento["pendiente"] = rendimiento.vigencia_verificada.isin(PENDIENTES)
    rendimiento = rendimiento.sort_values(
        ["pendiente", "filas_que_abre_si_abre", "filas_94", "zonas_22"],
        ascending=[False, False, False, False])

    pendientes_con_fila = rendimiento[rendimiento.pendiente & (rendimiento.filas_94 > 0)]

    p("-" * 100)
    p("  LISTA 2 · LOS QUE RINDEN · el hito que está adentro de más filas")
    p("")
    p(f"      {int(rendimiento.pendiente.sum())} hitos pendientes en total, de los cuales "
      f"{len(pendientes_con_fila)} caen adentro de alguna de las 94.")
    p(f"      Los otros {int(rendimiento.pendiente.sum()) - len(pendientes_con_fila)} no tocan "
      "ninguna fila: verificarlos no mueve la matriz, y por eso no encabezan la ronda.")
    p("")
    p(f"      {'hito':<32}{'barrio':<18}{'filas':>6}{'zonas':>6}{'abre':>6}{'cierra':>7}"
      f"   {'estado':<14}tipo")
    for fila in pendientes_con_fila.head(30).itertuples():
        p(f"      {str(fila.nombre)[:31]:<32}{str(fila.barrio_declarado)[:17]:<18}"
          f"{fila.filas_94:>6}{fila.zonas_22:>6}{fila.filas_que_abre_si_abre:>6}"
          f"{fila.filas_que_resuelve_si_cierra:>7}   {str(fila.vigencia_verificada):<14}"
          f"{str(fila.tipo)[:22]}")
    p("")
    p("      `abre`   = filas hoy pendientes que pasarían a `activo` con un solo «está abierto».")
    p("      `cierra` = filas que quedarían RESUELTAS con un «está cerrado», porque era el último")
    p("                 pendiente que les quedaba. Las dos columnas no se suman: son dos futuros")
    p("                 distintos del mismo hito.")
    p("")

    # ================================================================ el orden de ataque
    p("-" * 100)
    p("  EL ORDEN DE ATAQUE QUE SALE DE CRUZAR LAS DOS LISTAS")
    p("")
    unicos = set(fragiles[fragiles.estado_del_hito.isin(PENDIENTES)].hito_id.dropna())
    rendimiento["decide_una_fila_sola"] = rendimiento.hito_id.isin(unicos)
    tanda_a = rendimiento[rendimiento.decide_una_fila_sola & rendimiento.pendiente]
    tanda_b = rendimiento[(~rendimiento.decide_una_fila_sola) & rendimiento.pendiente
                          & (rendimiento.filas_94 >= 2)]
    tanda_c = rendimiento[(~rendimiento.decide_una_fila_sola) & rendimiento.pendiente
                          & (rendimiento.filas_94 == 1)]
    p(f"      TANDA A · {len(tanda_a)} hitos que son el ÚNICO de su fila. Cada verificación")
    p("                decide una fila completa, para los dos lados. Máxima consecuencia por")
    p("                consulta, y es donde está el riesgo de repetir la reversión de P008.")
    p(f"      TANDA B · {len(tanda_b)} hitos que están en DOS O MÁS filas. Una consulta, varias")
    p("                celdas. Rinden aunque no decidan solos.")
    p(f"      TANDA C · {len(tanda_c)} hitos en una sola fila que comparten con otros. Se")
    p("                verifican después: mueven la matriz sólo si el resultado es «abierto».")
    p(f"      FUERA   · {int((rendimiento.pendiente & (rendimiento.filas_94 == 0)).sum())} hitos "
      "pendientes que no caen en ninguna fila. No entran a esta ronda.")
    p("")
    total_ronda = len(tanda_a) + len(tanda_b)
    filas_tocadas = set()
    for fila in pd.concat([tanda_a, tanda_b]).itertuples():
        filas_tocadas.update(x for x in str(fila.cuales_94).split("; ") if x and x != "nan")
    p(f"      Las tandas A y B juntas son {total_ronda} verificaciones y tocan "
      f"{len(filas_tocadas)} filas distintas")
    p(f"      de las {len(filas)} que tienen hitos. Contra las 220 fichas de la capa entera, es "
      f"{total_ronda / len(capa) * 100:.0f} % del trabajo")
    p(f"      para {len(filas_tocadas) / len(filas) * 100:.0f} % de las filas con hitos.")
    p("")

    # ================================================================ salidas
    columnas_fragiles = ["polo_id", "nombre_polo", "hito_id", "hito", "tipo", "direccion",
                         "barrio_declarado", "estado_del_hito", "vigencia_fecha",
                         "es_patrimonio_normativo", "via_B_soporte", "n_hitos"]
    fragiles[columnas_fragiles].to_csv(
        OUT / "prioridad_verificacion_filas_fragiles.csv", index=False, encoding="utf-8")
    columnas_rend = ["hito_id", "nombre", "tipo", "direccion", "barrio_declarado",
                     "vigencia_verificada", "vigencia_fecha", "pendiente", "filas_94",
                     "zonas_22", "filas_que_abre_si_abre", "filas_que_resuelve_si_cierra",
                     "decide_una_fila_sola", "cuales_94", "cuales_22", "es_alta_2026_08_03"]
    rendimiento[columnas_rend].to_csv(
        OUT / "prioridad_verificacion_hitos.csv", index=False, encoding="utf-8")
    filas.to_csv(OUT / "prioridad_verificacion_filas.csv", index=False, encoding="utf-8")

    p("=" * 100)
    p(f"  {len(fragiles)} filas frágiles · {len(pendientes_con_fila)} hitos pendientes con fila · "
      f"tanda A {len(tanda_a)} + tanda B {len(tanda_b)} · 0 consultas")
    p("=" * 100)
    p("")

    (OUT / "PRIORIDAD_VERIFICACION.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
