"""Wikidata: qué aporta a la base gastronómica de la Ciudad. Licencia CC0.

QUÉ SE ESPERA DE ESTA FUENTE, ESCRITO ANTES DE CORRER
------------------------------------------------------
**Volumen bajo y sesgado a lo notable.** Wikidata no es un directorio comercial: tiene lo que
alguien consideró enciclopédico. Así que no sirve para densidad ni para contar un barrio, y
medirla contra el padrón sería medir la cosa equivocada. Sirve para **enriquecer**: nombre
canónico, año de fundación, declaratorias patrimoniales e identificadores cruzados.

Si el aporte es de decenas y no de miles, la fuente cumplió: eso es lo que es.

LA COORDENADA DE WIKIDATA NO ENTRA A LA BASE
---------------------------------------------
El wiki de OpenStreetMap advierte que muchas coordenadas de Wikidata vienen de Wikipedia, que a
su vez las tomó de Google Maps. **Procedencia viciada**: importarlas metería en una base pública
un dato derivado de una plataforma cuyos términos no lo permiten, sin que quede rastro de dónde
salió.

Acá la coordenada se usa **sólo para seleccionar candidatos** —el servicio de caja de Wikidata es
la única forma de acotar la consulta sin que el endpoint expire— y para emparejar por cercanía
contra la base. Nunca se escribe como posición de un local: la posición la sigue poniendo la
fuente que ya la tenía. La columna sale marcada como `coordenada_no_usable` para que nadie la
levante por error más adelante.

LA TRAMPA DEL TIPO: UN CAFÉ PATRIMONIAL ESTÁ CARGADO COMO EDIFICIO
--------------------------------------------------------------------
Filtrar la gastronomía por `P31` **pierde el 85 % de los Bares Notables**. De los 95 que Wikidata
tiene con esa declaratoria, **81 están clasificados como «edificio»** y sólo 14 como cafetería,
bar o restaurante: al catalogarlos, lo enciclopédico fue el inmueble y no el negocio que hay
adentro. La consulta por árbol de clases encuentra 17; la consulta por declaratoria encuentra 95.

Por eso este script hace las dos y las reporta por separado. Y por eso conviene desconfiar en
general del `P31` de Wikidata como filtro temático: describe qué es la *entidad*, no qué
*actividad* pasa ahí.

POR QUÉ LA CONSULTA ESTÁ PARTIDA Y NO ES UNA SOLA
--------------------------------------------------
La consulta natural —«todo lo que sea de tipo gastronómico y esté en la Ciudad»— **expira**. Tres
formas se probaron y las tres dieron HTTP 504:

  · `?item wdt:P31/wdt:P279* wd:Q11707` + `?item wdt:P131* wd:Q1486`;
  · el árbol de clases como VALUES de 492 elementos más `P131*`;
  · ese mismo VALUES dentro del servicio de caja.

Lo que sí entra: pedir el árbol de clases por un lado, pedir la caja geográfica cruda por otro, y
**cruzar los dos conjuntos en memoria**. Cada consulta es barata; el producto cartesiano que las
hacía expirar no se le pide al servidor. Como efecto lateral, el listado de la caja queda en
disco y sirve para volver a filtrar con otro árbol de clases sin volver a consultar.

Además, un VALUES de 492 clases no entra por GET: `Request Header Fields Too Large`, HTTP 431.
Todo va por POST.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/bajar_wikidata_gastro.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
GEN = BARRIDO / "generado"
EXTERNAS = ROOT / "outputs" / "fuentes_externas" / "wikidata"
BASE = BARRIDO / "base" / "local.csv"

ENDPOINT = "https://query.wikidata.org/sparql"
# La política de Wikimedia pide un User-Agent que identifique al cliente y permita contactarlo.
# Un cliente anónimo puede ser bloqueado, y con razón: la infraestructura está donada.
USER_AGENT = ("DataGastro-DGDGAS/1.0 (Direccion General de Desarrollo Gastronomico, GCBA; "
              "construccion de base publica de gastronomia)")
PAUSA_S = 1.0
REINTENTOS = 4

# La caja de la Ciudad, generosa a propósito: el recorte fino se hace después contra el polígono,
# igual que en Overture. Un rectángulo no es la Ciudad y eso ya está documentado.
CAJA = {"oeste": "Point(-58.54 -34.71)", "este": "Point(-58.33 -34.52)"}

# Raíces del árbol de clases gastronómicas. Se toma el cierre `P279*` porque Wikidata clasifica
# muy fino —«parrilla», «pizzería», «casa de té»— y una lista escrita a mano se quedaría corta.
RAICES = {
    "Q11707": "restaurante",
    "Q30022": "cafetería",
    "Q187456": "bar",
    "Q1195942": "comida rápida",
    "Q194326": "pizzería",
    "Q1043336": "confitería / pastelería",
    "Q5307557": "casa de comidas",
}

CONSULTA_CLASES = """
SELECT DISTINCT ?c WHERE {
  VALUES ?raiz { %s }
  ?c wdt:P279* ?raiz .
}
"""

CONSULTA_CAJA = """
SELECT ?item ?clase ?coord WHERE {
  SERVICE wikibase:box {
    ?item wdt:P625 ?coord .
    bd:serviceParam wikibase:cornerWest "%(oeste)s"^^geo:wktLiteral .
    bd:serviceParam wikibase:cornerEast "%(este)s"^^geo:wktLiteral .
  }
  ?item wdt:P31 ?clase .
}
"""

# La declaratoria «Bar Notable» de la Ciudad. Es la consulta que **no** pasa por el tipo, y es la
# que rescata los 81 que están cargados como edificio. El barrido del catálogo de BA Data no
# encontró ningún dataset con esta lista: son 453 datasets revisados y cero coincidencias con
# «notable». O sea que hoy Wikidata es el índice abierto más completo de los Bares Notables.
BAR_NOTABLE = "Q5664697"

CONSULTA_PATRIMONIO = """
SELECT ?item ?itemLabel ?claseLabel ?inicio ?direccion ?sitio ?comunaLabel WHERE {
  ?item wdt:P1435 wd:%s .
  OPTIONAL { ?item wdt:P31 ?clase }
  OPTIONAL { ?item wdt:P571 ?inicio }
  OPTIONAL { ?item wdt:P6375 ?direccion }
  OPTIONAL { ?item wdt:P856 ?sitio }
  OPTIONAL { ?item wdt:P131 ?comuna }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en". }
}
"""

# Los atributos que justifican la fuente. Ninguno es una coordenada.
#   P571  fecha de fundación          P6375 dirección postal
#   P856  sitio web oficial           P402  identificador de relación en OSM
#   P1435 declaratoria patrimonial    P18   imagen (Commons)
#   P131  entidad territorial         P1448 nombre oficial
CONSULTA_ATRIBUTOS = """
SELECT ?item ?itemLabel ?claseLabel ?inicio ?direccion ?sitio ?osm ?patrimonioLabel
       ?comunaLabel ?nombreOficial WHERE {
  VALUES ?item { %s }
  OPTIONAL { ?item wdt:P31 ?clase }
  OPTIONAL { ?item wdt:P571 ?inicio }
  OPTIONAL { ?item wdt:P6375 ?direccion }
  OPTIONAL { ?item wdt:P856 ?sitio }
  OPTIONAL { ?item wdt:P402 ?osm }
  OPTIONAL { ?item wdt:P1435 ?patrimonio }
  OPTIONAL { ?item wdt:P131 ?comuna }
  OPTIONAL { ?item wdt:P1448 ?nombreOficial }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en". }
}
"""


def consultar(sparql: str, etiqueta: str) -> list[dict]:
    """POST con reintentos. El servicio expira seguido y un 504 no es un error del cliente."""
    encabezados = {"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"}
    for intento in range(1, REINTENTOS + 1):
        try:
            respuesta = requests.post(ENDPOINT, data={"query": sparql},
                                      headers=encabezados, timeout=300)
        except Exception as exc:  # noqa: BLE001
            print(f"  {etiqueta}: intento {intento}/{REINTENTOS} — {type(exc).__name__}")
            time.sleep(PAUSA_S * intento * 3)
            continue
        if respuesta.status_code == 200:
            return respuesta.json()["results"]["bindings"]
        print(f"  {etiqueta}: intento {intento}/{REINTENTOS} — HTTP {respuesta.status_code}")
        time.sleep(PAUSA_S * intento * 3)
    raise SystemExit(f"ABORTADO: {etiqueta} no respondió en {REINTENTOS} intentos. "
                     "No se escribió nada.")


def qid(valor: str) -> str:
    return valor.rsplit("/", 1)[-1]


def punto(wkt: str) -> tuple[float | None, float | None]:
    """`Point(lon lat)` a (lon, lat). Sólo para emparejar; no entra a la base como posición."""
    try:
        crudo = wkt[wkt.index("(") + 1:wkt.index(")")]
        lon, lat = crudo.split()
        return float(lon), float(lat)
    except Exception:  # noqa: BLE001
        return None, None


def _envolver(texto: str, ancho: int = 96) -> list[str]:
    lineas, actual = [], ""
    for palabra in texto.split():
        if len(actual) + len(palabra) + 1 > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f"{actual} {palabra}".strip()
    if actual:
        lineas.append(actual)
    return lineas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sin-red", action="store_true",
                        help="Rehace el informe desde lo ya bajado. No consulta nada.")
    args = parser.parse_args()

    EXTERNAS.mkdir(parents=True, exist_ok=True)
    crudo_caja = EXTERNAS / "wikidata_caja_ciudad.csv"
    crudo_clases = EXTERNAS / "wikidata_clases_gastro.csv"

    if args.sin_red:
        if not (crudo_caja.exists() and crudo_clases.exists()):
            raise SystemExit("ABORTADO: --sin-red necesita las descargas previas.")
        caja = pd.read_csv(crudo_caja)
        clases = set(pd.read_csv(crudo_clases).clase)
    else:
        print("Consulta 1/3 · el árbol de clases gastronómicas")
        valores_raices = " ".join(f"wd:{q}" for q in RAICES)
        filas = consultar(CONSULTA_CLASES % valores_raices, "árbol de clases")
        clases = {qid(f["c"]["value"]) for f in filas}
        pd.DataFrame({"clase": sorted(clases)}).to_csv(crudo_clases, index=False,
                                                       encoding="utf-8")
        print(f"  {len(clases)} clases bajo {len(RAICES)} raíces")

        time.sleep(PAUSA_S)
        print("Consulta 2/3 · todo lo georreferenciado en la caja de la Ciudad")
        filas = consultar(CONSULTA_CAJA % CAJA, "caja de la Ciudad")
        caja = pd.DataFrame([{"item": qid(f["item"]["value"]),
                              "clase": qid(f["clase"]["value"]),
                              "coord": f["coord"]["value"]} for f in filas])
        caja.to_csv(crudo_caja, index=False, encoding="utf-8")
        print(f"  {len(caja)} pares ítem-clase · {caja.item.nunique()} ítems distintos")

    # El cruce que el endpoint no podía hacer.
    gastro = caja[caja.clase.isin(clases)].copy()
    items = sorted(gastro.item.unique())
    print(f"\nCruce en memoria: {len(items)} ítems gastronómicos con coordenada en la caja")

    atributos = pd.DataFrame()
    if items and not args.sin_red:
        time.sleep(PAUSA_S)
        print("Consulta 3/3 · atributos de los ítems que quedaron")
        filas = consultar(CONSULTA_ATRIBUTOS % " ".join(f"wd:{i}" for i in items), "atributos")
        atributos = pd.DataFrame([{
            "item": qid(f["item"]["value"]),
            "nombre": f.get("itemLabel", {}).get("value", ""),
            "nombre_oficial": f.get("nombreOficial", {}).get("value", ""),
            "clase": f.get("claseLabel", {}).get("value", ""),
            "fundacion": f.get("inicio", {}).get("value", "")[:10],
            "direccion": f.get("direccion", {}).get("value", ""),
            "sitio_web": f.get("sitio", {}).get("value", ""),
            "osm_id": f.get("osm", {}).get("value", ""),
            "patrimonio": f.get("patrimonioLabel", {}).get("value", ""),
            "comuna_o_barrio": f.get("comunaLabel", {}).get("value", ""),
        } for f in filas])
        # Un ítem trae varias filas si tiene varias clases o varias declaratorias. Se colapsa a
        # una fila por ítem juntando los valores distintos: la unidad de la tabla es el ítem.
        if len(atributos):
            atributos = atributos.groupby("item", as_index=False).agg(
                lambda serie: " · ".join(sorted({v for v in serie if v})))
    elif items:
        salida_previa = EXTERNAS / "wikidata_gastro_ciudad.csv"
        if salida_previa.exists():
            atributos = pd.read_csv(salida_previa)

    if len(atributos):
        posiciones = gastro.drop_duplicates("item").set_index("item").coord
        atributos["coordenada_no_usable"] = atributos.item.map(posiciones)
        atributos.to_csv(EXTERNAS / "wikidata_gastro_ciudad.csv", index=False, encoding="utf-8")

    # La segunda consulta: por declaratoria y NO por tipo. Es la que rescata los 81 cargados como
    # edificio, y la que convierte a Wikidata en algo más que una curiosidad.
    salida_notables = EXTERNAS / "wikidata_bares_notables.csv"
    notables = pd.DataFrame()
    if not args.sin_red:
        time.sleep(PAUSA_S)
        print("Consulta 4/4 · los Bares Notables, por declaratoria patrimonial")
        filas = consultar(CONSULTA_PATRIMONIO % BAR_NOTABLE, "Bares Notables")
        notables = pd.DataFrame([{
            "item": qid(f["item"]["value"]),
            "nombre": f.get("itemLabel", {}).get("value", ""),
            "clase_wikidata": f.get("claseLabel", {}).get("value", ""),
            "fundacion": f.get("inicio", {}).get("value", "")[:10],
            "direccion": f.get("direccion", {}).get("value", ""),
            "sitio_web": f.get("sitio", {}).get("value", ""),
            "comuna_o_barrio": f.get("comunaLabel", {}).get("value", ""),
        } for f in filas])
        if len(notables):
            notables = notables.groupby("item", as_index=False).agg(
                lambda serie: " · ".join(sorted({v for v in serie if v})))
            notables["geocodificar_con"] = "USIG desde `direccion`; NO usar coordenada de Wikidata"
            notables.to_csv(salida_notables, index=False, encoding="utf-8")
    elif salida_notables.exists():
        notables = pd.read_csv(salida_notables)

    # ------------------------------------------------------------------ informe
    salida = io.StringIO()

    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    linea("=" * 98)
    linea("WIKIDATA · QUÉ APORTA A LA BASE GASTRONÓMICA DE LA CIUDAD · CC0")
    linea("=" * 98)
    linea(f"fecha {dt.date.today().isoformat()} · endpoint {ENDPOINT}")
    linea()

    linea("§1 · EL VOLUMEN, QUE ES LO PRIMERO QUE HAY QUE MIRAR")
    linea("-" * 98)
    linea(f"  clases gastronómicas en el árbol de Wikidata  : {len(clases)}")
    linea(f"  ítems georreferenciados en la caja de la Ciudad: {caja.item.nunique()}")
    linea(f"  de ésos, gastronómicos POR TIPO                : {len(items)}")
    linea(f"  gastronómicos POR DECLARATORIA (Bar Notable)   : {len(notables)}")
    linea()
    for texto in _envolver(
        f"{len(items)} ítems por tipo contra los 27.727 locales de la base. **Wikidata no es una "
        "fuente de densidad y no se va a usar como tal.** Eso es exactamente lo que se escribió "
        "esperar antes de correr, y no decepciona."):
        linea(f"  {texto}")
    linea()
    if len(notables):
        tipo_gastro = notables.clase_wikidata.fillna("").astype(str).str.lower().str.contains(
            "cafeter|bar|restaurant|pizzer|confiter|helader")
        cargados_gastro = int(tipo_gastro.sum())
        for texto in _envolver(
            f"Pero la consulta por tipo se queda corta por una razón que no es de volumen: de los "
            f"{len(notables)} Bares Notables, sólo {cargados_gastro} están cargados como "
            f"cafetería, bar o restaurante. **Los otros {len(notables) - cargados_gastro} figuran "
            "como «edificio».** Al catalogarlos, lo enciclopédico fue el inmueble y no el negocio "
            "que hay adentro. Filtrar gastronomía por `P31` en Wikidata pierde el grueso de lo que "
            "importa; hay que preguntar por la declaratoria."):
            linea(f"  {texto}")
        linea()

    if len(notables):
        linea("§1b · LOS BARES NOTABLES · EL APORTE QUE JUSTIFICA LA FUENTE")
        linea("-" * 98)
        con_direccion = int((notables.direccion.fillna("").astype(str).str.len() > 0).sum())
        linea(f"  ítems con declaratoria «Bar Notable»    : {len(notables)}")
        linea(f"  con dirección postal declarada          : {con_direccion} "
              f"({100 * con_direccion / len(notables):.0f} %)")
        linea()
        for texto in _envolver(
            "El barrido del catálogo de BA Data —453 datasets— no devolvió **ningún** dataset con "
            "esta lista. O sea que hoy el índice abierto más completo de los Bares Notables de la "
            "Ciudad está en Wikidata, bajo CC0, y no en el portal del Gobierno que los declaró. "
            "Conviene decirlo con cuidado: puede existir y no estar catalogado con esa palabra. "
            "Lo verificable es que el barrido no lo encontró."):
            linea(f"  {texto}")
        linea()
        for texto in _envolver(
            f"Y trae dirección postal en el {100 * con_direccion / len(notables):.0f} % de los "
            "casos, que es la salida limpia al problema de la coordenada: se geocodifica con USIG "
            "desde la dirección y la coordenada de Wikidata no se toca."):
            linea(f"  {texto}")
        linea()
        linea("  Los diez primeros, para que se vea qué son:")
        for fila in notables.head(10).itertuples():
            linea(f"    {str(fila.nombre)[:40]:<41} {str(fila.direccion)[:44]:<45}"
                  f"{str(fila.clase_wikidata)[:12]}")
        linea()

    if len(atributos):
        linea("§2 · QUÉ TRAE CADA ÍTEM, QUE ES DONDE ESTÁ EL VALOR")
        linea("-" * 98)
        for columna, etiqueta in (("nombre", "nombre"),
                                  ("nombre_oficial", "nombre oficial"),
                                  ("fundacion", "año de fundación"),
                                  ("direccion", "dirección postal"),
                                  ("sitio_web", "sitio web oficial"),
                                  ("osm_id", "identificador OSM"),
                                  ("patrimonio", "declaratoria patrimonial")):
            if columna not in atributos:
                continue
            llenos = int((atributos[columna].fillna("").astype(str).str.len() > 0).sum())
            pct = 100 * llenos / len(atributos)
            linea(f"  {etiqueta:<26}: {llenos:>4} de {len(atributos)} ({pct:.0f} %)")
        linea()
        con_fundacion = atributos[atributos.fundacion.fillna("").astype(str).str.len() > 0]
        if len(con_fundacion):
            linea("  Los más antiguos con fecha declarada:")
            for fila in con_fundacion.sort_values("fundacion").head(8).itertuples():
                linea(f"    {str(fila.fundacion)[:4]}  {str(fila.nombre)[:52]:<53}"
                      f"{str(fila.clase)[:28]}")
            linea()
        con_patrimonio = atributos[atributos.patrimonio.fillna("").astype(str).str.len() > 0]
        linea(f"  Con declaratoria patrimonial: {len(con_patrimonio)}")
        for fila in con_patrimonio.head(10).itertuples():
            linea(f"    {str(fila.nombre)[:44]:<45} {str(fila.patrimonio)[:48]}")
        linea()

    linea("§3 · CÓMO ENTRA A LA BASE, Y CÓMO NO")
    linea("-" * 98)
    for texto in _envolver(
        "Entra como **capa de enriquecimiento**, nunca como universo ni como grupo de "
        "independencia propio: un local que sólo existe en Wikidata no debería crear un registro "
        "en la base, porque su existencia la afirma un editor voluntario y no un organismo ni un "
        "relevamiento. Lo que sí aporta, sobre locales que la base ya tiene: nombre canónico, año "
        "de fundación, declaratoria patrimonial e identificador de OSM."):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        "La declaratoria es la excepción parcial a esa regla: **«Bar Notable» es un acto "
        "administrativo de la Ciudad, no una opinión de un editor.** Wikidata acá es el "
        "transporte, no la autoridad. Si un Bar Notable no aparece en la base, eso es un faltante "
        "de la base y no un dato dudoso — pero antes de darlo por bueno conviene confirmar la "
        "lista contra la normativa, porque el que la transcribió sí es un voluntario."):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        "**Su coordenada no se copia.** El wiki de OSM advierte que muchas coordenadas de Wikidata "
        "vienen de Wikipedia, que las tomó de Google Maps: procedencia viciada. Acá se usó sólo "
        "para acotar la consulta y para emparejar, y la columna viaja rotulada "
        "`coordenada_no_usable`."):
        linea(f"  {texto}")
    linea()
    linea("=" * 98)

    texto_final = salida.getvalue()
    print("\n" + texto_final)

    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "WIKIDATA_GASTRO_CIUDAD.txt").write_text(texto_final, encoding="utf-8")
    (GEN / "wikidata_gastro_resumen.json").write_text(json.dumps({
        "fecha_consulta": dt.date.today().isoformat(),
        "licencia": "CC0 1.0",
        "clases_en_el_arbol": len(clases),
        "items_georreferenciados_en_la_caja": int(caja.item.nunique()),
        "items_gastronomicos_por_tipo": len(items),
        "bares_notables_por_declaratoria": len(notables),
        "bares_notables_cargados_como_edificio": (
            len(notables) - int(notables.clase_wikidata.fillna("").astype(str).str.lower()
                                .str.contains("cafeter|bar|restaurant|pizzer|confiter|helader")
                                .sum()) if len(notables) else 0),
        "coordenadas_importadas_a_la_base": 0,
        "motivo": "procedencia viciada (Wikipedia -> Google Maps), segun el wiki de OSM",
        "geocodificacion_prevista": "USIG desde la direccion postal declarada",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  publicado en {GEN.relative_to(ROOT)}: WIKIDATA_GASTRO_CIUDAD.txt, "
          "wikidata_gastro_resumen.json")
    if len(atributos):
        print(f"  tabla en {(EXTERNAS / 'wikidata_gastro_ciudad.csv').relative_to(ROOT)}")
    if len(notables):
        print(f"  tabla en {salida_notables.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
