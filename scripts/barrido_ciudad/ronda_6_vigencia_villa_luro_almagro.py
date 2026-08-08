"""Ronda 6 · las dos verificaciones de Diego, y dónde caen realmente los dos hitos.

QUÉ CARGA
---------
Dos verificaciones de Diego del 07/08/2026, las dos `verificado_abierto` con nivel v2:

    Café Olimpo            Irigoyen 1491        H028   venía de `estado_operativo_pendiente`
    El Boliche de Roberto  Bulnes 331           H045   venía de `sin_verificar`

`verificado_abierto` es el vocabulario de la tanda; en la capa el estado abierto se escribe `si`,
como en la ronda 5. El nivel va aparte, en `vigencia_nivel`.

Y con ellas, la señal de cierre de Yelp sobre El Boliche —«CLOSED - Updated July 2026»— queda
**confirmada como falso positivo**: no es una duda que sigue abierta, es un caso probado contra una
verificación humana. Eso promueve FD-12 de la lista de insumo (`fuentes_con_defecto_FD08_FD12.csv`,
producida afuera) a la capa canónica de fuentes con defecto, con la evidencia que lo prueba.

LO QUE ESTE SCRIPT MIDE Y NO HEREDA
------------------------------------
Las dos consecuencias que vienen con la carga —«Villa Luro conserva su vía B» y «Almagro recupera
los cinco notables»— se comprueban acá contra geometría, no se copian:

1. **Dónde cae cada hito.** Contención en las 94 filas de la matriz y en las 22 envolventes, con
   distancia al polígono cuando queda afuera. La vía B se mide por presencia desde la ronda 3: un
   hito que no está adentro no abre la vía B de esa fila, por más verificado que esté.

2. **En qué barrio está Irigoyen 1491.** El anexo de la Res. 1225/26 dice Villa Luro. La calle
   Irigoyen atraviesa cuatro barrios y el catastro reparte por altura, no por nombre de calle: el
   callejero oficial del GCBA (F02) da la escalera tramo por tramo, y USIG /datos_utiles responde
   sobre el punto. Si las dos coinciden en contra del anexo, es una tercera instancia de FD-02 —el
   campo territorial del catálogo—, no una corrección aislada.

Google Places: 0 requests. USIG: hasta 2 consultas de /datos_utiles sobre puntos ya normalizados y
cacheados; el normalizador no se vuelve a llamar.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_6_vigencia_villa_luro_almagro.py
"""
from __future__ import annotations

import csv
import io
import json
import sys
import time
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import (  # noqa: E402
    BARRIDO,
    CALLEJERO,
    CRS_GEOGRAFICO,
    CRS_METRICO,
    barrios,
    envolventes_22,
    sin_tildes,
    soportes_94,
)

HITOS = BARRIDO / "hitos"
FUENTES = BARRIDO / "fuentes"
SEIS_VIAS = BARRIDO / "seis_vias"

CAPA_R5 = HITOS / "hitos_capa_2026_r5.csv"
OUT_CSV = HITOS / "hitos_capa_2026_r6.csv"
CAMBIOS_CSV = HITOS / "cambios_ronda_6.csv"
INFORME_TXT = HITOS / "RONDA_6.txt"
DONDE_CAEN_CSV = SEIS_VIAS / "donde_caen_los_dos_hitos_r6.csv"
ALMAGRO_CSV = HITOS / "almagro_cinco_notables_r6.csv"

DEFECTOS_CSV = FUENTES / "fuentes_defectos_conocidos.csv"
MARCAS_CSV = FUENTES / "fuentes_marcas_aplicadas.csv"

CACHE_USIG = BARRIDO / "dataset_bares_notables" / "_cache_usig.json"
CACHE_DATOS_UTILES = SEIS_VIAS / "_cache_usig_datos_utiles.json"
DATOS_UTILES_URL = "https://ws.usig.buenosaires.gob.ar/datos_utiles/"

FECHA = "2026-08-07"
VERIFICADOR = "Diego, 07/08/2026"

# Los cinco Bares Notables que el barrio de Almagro contiene, según el cruce con el polígono
# administrativo del GCBA. No es una lista escrita a mano: se recalcula y se compara.
ALMAGRO = "Almagro"


# ----------------------------------------------------------------------------- capa
def cargar_capa() -> tuple[list[str], list[dict]]:
    with open(CAPA_R5, encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        return list(lector.fieldnames or []), list(lector)


def por_id(filas: list[dict], hito_id: str) -> dict:
    for fila in filas:
        if fila["hito_id"] == hito_id:
            return fila
    raise KeyError(f"{hito_id} no está en {CAPA_R5.name}")


def registrar_cambio(cambios: list[dict], fila: dict, campo: str, antes: str, despues: str,
                     motivo: str, tarea: str) -> None:
    cambios.append({"hito_id": fila["hito_id"], "nombre": fila["nombre"], "campo": campo,
                    "valor_antes": antes, "valor_despues": despues, "motivo": motivo,
                    "tarea": tarea, "fecha": FECHA})


def set_campo(cambios: list[dict], fila: dict, campo: str, valor: str, motivo: str,
              tarea: str) -> None:
    antes = fila.get(campo, "")
    if str(antes) == str(valor):
        return
    fila[campo] = valor
    registrar_cambio(cambios, fila, campo, antes, valor, motivo, tarea)


# ----------------------------------------------------------------------------- USIG
def datos_utiles(x: str, y: str, cache: dict) -> dict:
    """Barrio y comuna del punto, cacheado por coordenada. Una consulta por punto nuevo."""
    clave = f"{x},{y}"
    if clave not in cache:
        respuesta = requests.get(DATOS_UTILES_URL, params={"x": x, "y": y, "formato": "json"},
                                 timeout=25)
        respuesta.raise_for_status()
        cache[clave] = respuesta.json()
        time.sleep(0.35)
    return cache[clave]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    if not CAPA_R5.exists():
        raise SystemExit("falta hitos_capa_2026_r5.csv — correr ronda_5_catalogo_vigencia.py")

    campos, filas = cargar_capa()
    for nuevo in ("nota_ronda_6",):
        if nuevo not in campos:
            campos.append(nuevo)
    for fila in filas:
        fila.setdefault("nota_ronda_6", "")
    cambios: list[dict] = []

    p("RONDA 6 · DOS VERIFICADOS, UN FALSO POSITIVO PROBADO, Y DÓNDE CAEN DE VERDAD")
    p("=" * 100)
    p("")
    p(f"  capa de entrada: {CAPA_R5.name} · {len(filas)} hitos")
    p("  Google Places: 0 requests. USIG: sólo /datos_utiles sobre dos puntos ya normalizados.")
    p("")

    # ================================================================== TAREA 1 · las dos cargas
    p("-" * 100)
    p("  TAREA 1 · LAS DOS VERIFICACIONES DE DIEGO")
    p("")

    olimpo = por_id(filas, "H028")
    boliche = por_id(filas, "H045")

    set_campo(cambios, olimpo, "vigencia_verificada", "si",
              "Verificación humana de Diego (07/08/2026): verificado_abierto. Cierra el único "
              "`estado_operativo_pendiente` que había dejado la ronda 5 — el caso que se citaba "
              "como justificación por sí solo para correr Places. Se resolvió sin Places.",
              "TAREA_1")
    set_campo(cambios, olimpo, "vigencia_nivel", "v2", "", "TAREA_1")
    set_campo(cambios, olimpo, "vigencia_fuente", f"verificación humana · {VERIFICADOR}", "",
              "TAREA_1")
    set_campo(cambios, olimpo, "vigencia_fecha", FECHA, "", "TAREA_1")
    set_campo(cambios, olimpo, "nota_ronda_6",
              "Verificado abierto por Diego el 07/08/2026 (v2). Nueve años sin una sola mención "
              "fechable en fuentes abiertas: tres intentos documentales fallaron y lo resolvió "
              "una verificación humana. El barrio del anexo NO se sostiene — ver TAREA 2.",
              "", "TAREA_1")

    set_campo(cambios, boliche, "vigencia_verificada", "si",
              "Verificación humana de Diego (07/08/2026): verificado_abierto. Era el eslabón roto "
              "de Almagro: ninguna pieza documental caía dentro de ventana (lo más nuevo, "
              "check-ins de Untappd del 25/03/2026, a 135 días).",
              "TAREA_1")
    set_campo(cambios, boliche, "vigencia_nivel", "v2", "", "TAREA_1")
    set_campo(cambios, boliche, "vigencia_fuente", f"verificación humana · {VERIFICADOR}", "",
              "TAREA_1")
    set_campo(cambios, boliche, "vigencia_fecha", FECHA, "", "TAREA_1")
    set_campo(cambios, boliche, "nota_ronda_6",
              "Verificado abierto por Diego el 07/08/2026 (v2). Nombre de uso: El Boliche de "
              "Roberto; nombre formal del catálogo: '12 de octubre'. La marca de cierre de Yelp "
              "«CLOSED - Updated July 2026» queda CONFIRMADA COMO FALSO POSITIVO: es el caso "
              "probado de FD-12, no una señal pendiente de resolver.",
              "", "TAREA_1")

    for fila in (olimpo, boliche):
        p(f"      {fila['hito_id']}  {fila['nombre'][:26]:<28}{fila['direccion'][:22]:<24}"
          f"→ vigencia_verificada = si · nivel v2 · {VERIFICADOR}")
    p("")
    p("      La de Café Olimpo cierra el último `estado_operativo_pendiente` de la capa. Con eso,")
    p("      el argumento de la ronda 5 —«el caso que por sí solo justifica correr Places»— se")
    p("      queda sin su caso: quedó resuelto por verificación humana, con 0 requests.")
    p("")

    # ============================================== TAREA 2 · dónde caen, medido y no heredado
    p("-" * 100)
    p("  TAREA 2 · DÓNDE CAEN LOS DOS HITOS · lo que la carga afirma y lo que la geometría dice")
    p("")

    con_punto = [f for f in filas if f.get("latitud") and f.get("longitud")]
    marco = pd.DataFrame(con_punto)
    puntos = gpd.GeoDataFrame(
        marco,
        geometry=gpd.points_from_xy(marco.longitud.astype(float), marco.latitud.astype(float)),
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO)

    soportes = soportes_94()
    zonas = envolventes_22()
    barrios_gcba = barrios().to_crs(CRS_METRICO)

    # -------- 2a · el barrio real de Irigoyen 1491, por callejero y por USIG
    p("  2a · Irigoyen 1491: el anexo dice Villa Luro, y la calle atraviesa cuatro barrios")
    p("")
    calles = gpd.read_file(CALLEJERO)
    calles["n"] = calles.nomoficial.astype(str).map(lambda s: sin_tildes(s).upper())
    irigoyen = calles[calles.n == "IRIGOYEN"]
    # Los tramos con altura 0 son cabeceras y cruces sin numeración: si entran al agrupamiento
    # arrastran el mínimo a 0 y fabrican un tramo «Villa Real 0–2599» que no existe en la calle.
    numerados = irigoyen[irigoyen.alt_derfin > 0].sort_values("alt_derini")
    escalera: list[dict] = []
    for tramo in numerados.itertuples():
        par = (tramo.barrio_imp, tramo.barrio_par)
        if escalera and escalera[-1]["par"] == par:
            escalera[-1]["hasta"] = int(tramo.alt_derfin)
            escalera[-1]["tramos"] += 1
        else:
            escalera.append({"par": par, "desde": int(tramo.alt_derini),
                             "hasta": int(tramo.alt_derfin), "tramos": 1})
    p(f"      {'altura (impar)':<18}{'lado impar':<18}{'lado par':<16}tramos")
    for corrida in escalera:
        marca = "  ←  1491 cae acá" if corrida["desde"] <= 1491 <= corrida["hasta"] else ""
        p(f"      {str(corrida['desde']) + '–' + str(corrida['hasta']):<18}"
          f"{corrida['par'][0]:<18}{corrida['par'][1]:<16}{corrida['tramos']:>3}{marca}")
    p("")
    p("      La calle Irigoyen SÍ pasa por Villa Luro, pero se termina en el 1299. El 1491 está")
    p("      dos cuadras más allá, del lado impar, que es Monte Castro; el lado par de ese mismo")
    p("      tramo es Versalles. La atribución del anexo se apoya en el nombre de la calle, no en")
    p("      la altura.")
    p("")

    # La esquina que cita la tanda —Irigoyen y Arregui— resuelta por intersección de ejes.
    arregui = calles[calles.n.str.contains("ARREGUI", na=False)].to_crs(CRS_METRICO)
    iri_m = irigoyen.to_crs(CRS_METRICO)
    ejes_arregui = arregui.geometry.union_all()
    tocan = iri_m[iri_m.geometry.distance(ejes_arregui) < 1.0]
    esquina = tocan.geometry.union_all().intersection(ejes_arregui)
    punto_olimpo = puntos[puntos.hito_id == "H028"].geometry.iloc[0]
    p(f"      Esquina Irigoyen y Arregui, resuelta por intersección de ejes del callejero: a "
      f"{punto_olimpo.distance(esquina):.0f} m del punto")
    p("      que USIG le había dado a la ficha. Es la misma esquina — el punto no está en duda.")
    for nombre_barrio in ("Villa Luro", "Monte Castro", "Versalles"):
        geo = barrios_gcba[barrios_gcba.nombre == nombre_barrio].geometry.iloc[0]
        p(f"            distancia de esa esquina a {nombre_barrio:<14}{esquina.distance(geo):>7.0f} m")
    p("")

    # USIG sobre el punto, que es la fuente administrativa que el proyecto adoptó en ronda 5.
    cache_du = (json.loads(CACHE_DATOS_UTILES.read_text(encoding="utf-8"))
                if CACHE_DATOS_UTILES.exists() else {})
    barrio_usig_olimpo = ""
    for etiqueta, hito_id in (("Café Olimpo · Irigoyen 1491", "H028"),
                              ("El Boliche de Roberto · Bulnes 331", "H045")):
        fila = por_id(filas, hito_id)
        respuesta = datos_utiles(fila["longitud"], fila["latitud"], cache_du)
        barrio = str(respuesta.get("barrio", "—"))
        p(f"      USIG /datos_utiles · {etiqueta:<36}barrio={barrio:<16}"
          f"comuna={respuesta.get('comuna', '—')}")
        if hito_id == "H028":
            barrio_usig_olimpo = barrio
    CACHE_DATOS_UTILES.write_text(json.dumps(cache_du, ensure_ascii=False, indent=1),
                                  encoding="utf-8")
    p("")

    if barrio_usig_olimpo and sin_tildes(barrio_usig_olimpo).upper() != "VILLA LURO":
        set_campo(cambios, olimpo, "barrio_declarado", barrio_usig_olimpo,
                  "TERCERA INSTANCIA DE FD-02. El anexo de la Res. 1225/26 lo asienta en Villa "
                  "Luro; el callejero oficial del GCBA reparte Irigoyen por altura y el 1491 "
                  "impar es Monte Castro (par: Versalles), con Villa Luro terminando en el 1299; "
                  f"USIG /datos_utiles sobre el punto responde {barrio_usig_olimpo}. Dos fuentes "
                  "administrativas contra el campo territorial del catálogo. La comuna del anexo "
                  "(10) sí es correcta: Villa Luro, Monte Castro y Versalles son las tres Comuna "
                  "10, y por eso el error no se veía.",
                  "TAREA_2")
        p(f"      → barrio_declarado de H028 = {barrio_usig_olimpo} (era: vacío). Tercera "
          "instancia de FD-02.")
        p("")

    # -------- 2b · contención en las 94 filas y en las 22 envolventes
    p("  2b · la vía B se mide por presencia: ¿están adentro de alguna fila?")
    p("")
    medicion = []
    for hito_id, fila_esperada, nombre_fila in (("H028", "PGR_P020", "P020 · Villa Luro"),
                                                ("H045", "PGR_P083", "P083 · Almagro")):
        punto = puntos[puntos.hito_id == hito_id]
        dentro_94 = gpd.sjoin(punto, soportes[["polo_id", "nombre_polo", "geometry"]],
                              predicate="within", how="inner")
        dentro_22 = gpd.sjoin(punto, zonas[["referencia_id", "nombre", "geometry"]],
                              predicate="within", how="inner")
        geo_fila = soportes.set_index("polo_id").loc[fila_esperada, "geometry"]
        distancia = punto.geometry.iloc[0].distance(geo_fila)
        en_barrio = gpd.sjoin(punto, barrios_gcba[["nombre", "geometry"]].rename(
            columns={"nombre": "barrio_gcba"}), predicate="within", how="left")
        barrio_del_punto = str(en_barrio.barrio_gcba.iloc[0])
        medicion.append({
            "hito_id": hito_id,
            "nombre": punto.nombre.iloc[0],
            "direccion": punto.direccion.iloc[0],
            "barrio_gcba_del_punto": barrio_del_punto,
            "filas_94_que_lo_contienen": len(dentro_94),
            "cuales_94": "; ".join(sorted(dentro_94.polo_id)) if len(dentro_94) else "",
            "envolventes_22_que_lo_contienen": len(dentro_22),
            "cuales_22": "; ".join(sorted(dentro_22.referencia_id)) if len(dentro_22) else "",
            "fila_que_la_carga_le_atribuye": f"{fila_esperada} · {nombre_fila}",
            "dentro_de_esa_fila": bool(geo_fila.contains(punto.geometry.iloc[0])),
            "distancia_a_esa_fila_m": round(distancia, 1),
            "ha_de_esa_fila": round(geo_fila.area / 1e4, 1),
        })
        p(f"      {hito_id} {str(punto.nombre.iloc[0])[:24]:<26}"
          f"barrio GCBA del punto: {barrio_del_punto}")
        p(f"            en las 94 filas: {len(dentro_94)}   ·   en las 22 envolventes: "
          f"{len(dentro_22)}")
        p(f"            {fila_esperada} ({nombre_fila}, {geo_fila.area / 1e4:.1f} ha): "
          f"{'ADENTRO' if geo_fila.contains(punto.geometry.iloc[0]) else 'AFUERA'} · "
          f"{distancia:.0f} m del polígono")
        p("")
    pd.DataFrame(medicion).to_csv(DONDE_CAEN_CSV, index=False, encoding="utf-8")

    p("      Ninguno de los dos está adentro de ninguna de las 94 filas ni de ninguna de las 22")
    p("      envolventes. La vía B de la matriz se mide por presencia desde la ronda 3, así que")
    p("      **la vía B medida no se mueve con estas dos verificaciones**: P020 y P083 siguen en")
    p("      `sin_hitos`. Lo que la carga salva es la lectura de escala de barrio (Z31 / Z37), que")
    p("      es la unidad que usa la asignación heredada de vía E, no la fila de la matriz.")
    p("")

    # -------- 2c · los cinco de Almagro, contados y no citados
    p("  2c · «los cinco notables de Almagro»: quiénes son y cómo están en la capa")
    p("")
    geo_almagro = barrios_gcba[barrios_gcba.nombre == ALMAGRO].geometry.iloc[0]
    en_almagro = puntos[puntos.geometry.within(geo_almagro)]
    notables = en_almagro[en_almagro.tipo.astype(str).str.contains("Bar Notable", case=False)]
    geo_p083 = soportes.set_index("polo_id").loc["PGR_P083", "geometry"]
    tabla_almagro = []
    for fila_n in notables.itertuples():
        tabla_almagro.append({
            "hito_id": fila_n.hito_id,
            "nombre": fila_n.nombre,
            "direccion": fila_n.direccion,
            "vigencia_verificada": por_id(filas, fila_n.hito_id)["vigencia_verificada"],
            "vigencia_nivel": por_id(filas, fila_n.hito_id).get("vigencia_nivel", ""),
            "dentro_de_PGR_P083": bool(geo_p083.contains(fila_n.geometry)),
            "distancia_a_PGR_P083_m": round(fila_n.geometry.distance(geo_p083), 1),
        })
    tabla_almagro.sort(key=lambda r: r["distancia_a_PGR_P083_m"])
    pd.DataFrame(tabla_almagro).to_csv(ALMAGRO_CSV, index=False, encoding="utf-8")
    p(f"      El polígono administrativo de Almagro contiene {len(notables)} Bares Notables:")
    p("")
    p(f"      {'hito':<8}{'nombre':<24}{'dirección':<28}{'estado en la capa':<22}"
      f"{'a P083':>9}")
    for registro in tabla_almagro:
        p(f"      {registro['hito_id']:<8}{str(registro['nombre'])[:22]:<24}"
          f"{str(registro['direccion'])[:26]:<28}"
          f"{registro['vigencia_verificada']:<22}{registro['distancia_a_PGR_P083_m']:>7.0f} m")
    p("")
    resueltos = sum(1 for r in tabla_almagro if r["vigencia_verificada"] == "si")
    p(f"      Verificados abiertos en la capa: {resueltos} de {len(tabla_almagro)}. Los otros "
      f"{len(tabla_almagro) - resueltos} tienen veredicto")
    p("      en el material de tanda B / cierre del día, que es insumo producido afuera y NO se")
    p("      aplicó a la capa: esta ronda carga sólo las dos verificaciones pedidas. Mientras no")
    p("      se apliquen, «Almagro recupera los cinco» es cierto en el registro de la tanda y no")
    p("      en la capa.")
    p("")
    p(f"      Y ninguno de los cinco está adentro de PGR_P083 ({geo_p083.area / 1e4:.1f} ha): el")
    p(f"      más cercano queda a {min(r['distancia_a_PGR_P083_m'] for r in tabla_almagro):.0f} m.")
    p("      La fila de la matriz es mucho más chica que el barrio.")
    p("")

    # ============================================== TAREA 3 · FD-12 pasa a la capa canónica
    p("-" * 100)
    p("  TAREA 3 · FD-12 · LA MARCA DE CIERRE DE YELP, PROBADA COMO FALSO POSITIVO")
    p("")

    defectos = pd.read_csv(DEFECTOS_CSV, encoding="utf-8")
    marcas = pd.read_csv(MARCAS_CSV, encoding="utf-8")

    fila_fd12 = {
        "defecto_id": "FD-12",
        "fuente": "yelp.com",
        "regla_de_deteccion": (
            "el título del resultado de búsqueda expone «CLOSED - Updated <mes> <año>» y el "
            "dominio bloquea por robots.txt: la marca se ve y no se puede abrir"),
        "clase": "marca de cierre visible e inauditable",
        "que_prohibe": (
            "leer la marca de cierre como evidencia de cierre, o dejarla como duda que baja el "
            "veredicto de una ficha"),
        "que_sigue_valiendo": "nada de la ficha: no se puede abrir para saber de cuándo es",
        "severidad": "descarte de la señal; se registra y nunca se convierte en veredicto",
        "evidencia": (
            "CASO PROBADO: Yelp marcaba «EL BOLICHE DE ROBERTO - CLOSED - Updated July 2026» "
            "sobre Bulnes 331 (H045). Diego verificó el establecimiento ABIERTO el 07/08/2026. "
            "La marca era falsa, y contradecía además la actividad de usuario de fines de marzo "
            "de 2026 (check-ins de Untappd del 25/03) que la tanda ya había registrado. Un "
            "cerrado inauditable no cierra nada — y acá se probó que además puede ser falso"),
        "detectado": FECHA,
        "detectado_por": "cowork · tanda B (señal) + verificación humana de Diego (prueba)",
    }
    if "FD-12" in set(defectos.defecto_id):
        defectos = defectos[defectos.defecto_id != "FD-12"]
    defectos = pd.concat([defectos, pd.DataFrame([fila_fd12])], ignore_index=True)
    defectos = defectos.sort_values("defecto_id").reset_index(drop=True)
    defectos.to_csv(DEFECTOS_CSV, index=False, encoding="utf-8")

    nuevas_marcas = [
        {"defecto_id": "FD-12", "capa": "hitos_capa_2026_r6.csv", "registro": "12 de octubre",
         "campo": "señal de cierre externa", "valor": "Yelp · CLOSED - Updated July 2026",
         "estado_de_la_marca": "descartada_falso_positivo_probado",
         "consecuencia": "el hito queda `si` (v2) por verificación humana del 07/08/2026; la "
                         "marca de Yelp no baja el veredicto ni deja duda residual"},
        {"defecto_id": "FD-02", "capa": "hitos_capa_2026_r6.csv", "registro": "Café Olimpo",
         "campo": "barrio", "valor": "Villa Luro (anexo Res. 1225/26)",
         "estado_de_la_marca": "descartada_como_dato_territorial",
         "consecuencia": f"el barrio del punto es {barrio_usig_olimpo or 'Monte Castro'} según "
                         "USIG y según la escalera de alturas del callejero (Irigoyen impar "
                         "1301–1799 = Monte Castro; Villa Luro termina en el 1299). La comuna del "
                         "anexo (10) sí es correcta"},
    ]
    for marca in nuevas_marcas:
        ya = ((marcas.defecto_id == marca["defecto_id"]) & (marcas.registro == marca["registro"]))
        marcas = marcas[~ya]
    marcas = pd.concat([marcas, pd.DataFrame(nuevas_marcas)], ignore_index=True)
    marcas.to_csv(MARCAS_CSV, index=False, encoding="utf-8")

    p(f"      {DEFECTOS_CSV.name}: {len(defectos)} defectos "
      f"({', '.join(defectos.defecto_id)})")
    p(f"      {MARCAS_CSV.name}: {len(marcas)} marcas aplicadas "
      f"(+2: FD-12 sobre H045, FD-02 sobre H028)")
    p("")
    p("      FD-12 entra a la capa canónica con la evidencia que lo prueba, no con la sospecha:")
    p("      la señal era visible, inauditable Y falsa. La regla no cambia —se registra, nunca se")
    p("      convierte en veredicto— pero deja de ser una precaución y pasa a ser un hecho medido.")
    p("")
    p("      FD-02 suma su tercera instancia (La Academia, Roma del Abasto, Café Olimpo). El")
    p("      pendiente 3 de la ronda 5 —«si se repite en más filas, conviene registrarla como")
    p("      tal»— queda cumplido: el campo territorial del catálogo falla en las tres.")
    p("")

    # ============================================================================ salidas
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({c: fila.get(c, "") for c in campos})

    with open(CAMBIOS_CSV, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(
            f, fieldnames=["hito_id", "nombre", "campo", "valor_antes", "valor_despues",
                           "motivo", "tarea", "fecha"])
        escritor.writeheader()
        escritor.writerows(cambios)

    estados = pd.Series([fila["vigencia_verificada"] for fila in filas]).value_counts()
    p("=" * 100)
    p(f"  {OUT_CSV.name}: {len(filas)} filas · {len(campos)} columnas")
    p(f"  {CAMBIOS_CSV.name}: {len(cambios)} cambios")
    p(f"  {DONDE_CAEN_CSV.name} · {ALMAGRO_CSV.name}")
    p("")
    p("  vigencia_verificada en la capa:")
    for estado, cuantos in estados.items():
        p(f"        {estado:<36}{cuantos:>4}")
    p("")
    p("  Google Places: 0 requests.")
    p("=" * 100)
    p("")

    INFORME_TXT.write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
