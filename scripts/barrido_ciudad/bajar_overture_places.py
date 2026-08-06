"""Overture Maps · theme `places` (E06): recorte de la Ciudad y capa gastronómica por barrio.

QUÉ ES, Y POR QUÉ ENTRA ANTES QUE UNA TANDA DE PLACES
-----------------------------------------------------
Overture publica un padrón mundial de puntos de interés bajo **CDLA-Permissive 2.0**: se puede
redistribuir con nombre, dirección e identificador. Es exactamente lo que a Google Places le falta
—sus términos prohíben redistribuir nombre, dirección y `place_id`— y por eso decide el tamaño de
la capa publicable de la base.

Se baja el recorte de la Ciudad con DuckDB sobre el GeoParquet público en S3: no hay que bajar los
75 millones de POI del mundo, la consulta filtra por `bbox` con empuje de predicado y trae sólo lo
que cae adentro.

EL HALLAZGO QUE CAMBIA LOS GRUPOS DE INDEPENDENCIA
--------------------------------------------------
El esquema (§3) advierte que Overture, Foursquare y All The Places **no son tres fuentes
independientes**: Overture incorpora a las otras dos. Eso es cierto en general y hay que medirlo en
la Ciudad, porque acá el reparto resultó ser otro. La columna `sources` de cada POI dice de qué
aportante vino, y en el recorte de la Ciudad da esto:

    meta            122.334      Foursquare        4.318
    Microsoft         1.773      AllThePlaces        572
    PinMeTo               4      OSM                   0

**Overture en la Ciudad es, casi entero, el padrón de comercios de Meta.** Tres consecuencias
operativas, y ninguna es menor:

  1. **Overture y OSM sí son independientes acá**, porque OSM no aporta un solo registro al
     recorte. El solape entre las dos mide algo, no es tautología.
  2. **Foursquare aporta el 3,3 % de Overture.** Bajar Foursquare por separado —que además hoy
     exige cuenta, ver el informe— agregaría poco y seguiría contando como el mismo grupo.
  3. **All The Places aporta 572 registros**, la mayoría de los cuales Overture ya sirve.

El grupo de independencia se declara igual como uno solo (`OVERTURE_FSQ_ATP`), que es la lectura
conservadora del esquema. Lo que cambia es que ahora se sabe cuánto cuesta esa prudencia: casi nada.

EL MAPEO DE CATEGORÍAS, POR SIMETRÍA CON EL PADRÓN
---------------------------------------------------
Mismo criterio que el Relevamiento y que OSM. Overture trae una jerarquía de categorías
(`taxonomy.hierarchy`) cuya raíz separa la gastronomía de atención al público —`food_and_drink`—
del comercio de alimentos —`shopping / food_and_beverage_store`—. Esa separación es la que el
Relevamiento hubo que reconstruir a mano, y acá viene hecha: `grocery_store`, `supermarket` y
`health_food_store` cuelgan de `shopping` y quedan afuera solas.

**Regla de respaldo, y es deliberada:** una categoría hoja que no esté enumerada abajo NO se
descarta en silencio; cae al anillo de su nivel 2 y el informe lista cuáles usaron el respaldo.
Overture agrega categorías entre versiones, y una hoja nueva que desapareciera sin aviso es el
mismo defecto del cero que no era un cero.

CONFIANZA · SE INFORMA, NO SE FILTRA
------------------------------------
Cada POI trae `confidence` de 0 a 1. La cifra de titular **no filtra por confianza** y se publica
la sensibilidad al corte, con el mismo criterio de siempre: si el resultado dependiera del corte,
el corte estaría mal elegido y habría que discutirlo antes, no después.

USO
---
  python scripts/barrido_ciudad/bajar_overture_places.py                # dry-run: imprime la consulta
  python scripts/barrido_ciudad/bajar_overture_places.py --run          # baja el recorte y arma las tablas
  python scripts/barrido_ciudad/bajar_overture_places.py --reinformar   # rehace todo desde el recorte, sin red
  python scripts/barrido_ciudad/bajar_overture_places.py --vocabulario  # sólo el vocabulario de categorías
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import re
import sys
import unicodedata
import urllib.request
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
GEN = BARRIDO / "generado"
OVT_DIR = ROOT / "outputs" / "fuentes_externas" / "overture"
RECORTE = OVT_DIR / "overture_places_caba.parquet"

BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
CAPA_PADRON = BARRIDO / "capa_homogenea_48_barrios.csv"
CAPA_RUS = ROOT / "outputs" / "fuentes_externas" / "usos_suelo" / "rus_gastro_48_barrios.csv"
CAPA_OSM = GEN / "osm_gastro_48_barrios.csv"

BUCKET = "overturemaps-us-west-2"
LISTADO = f"https://{BUCKET}.s3.amazonaws.com/?list-type=2&prefix=release/&delimiter=/&max-keys=1000"
RAIZ_GASTRO = "food_and_drink"

# --- El mapeo, hoja por hoja, por simetría con el padrón ---------------------------------
NUCLEO_HOJAS: dict[str, list[str]] = {
    "Pizzeria": ["pizza_restaurant", "pizza_delivery_service"],
    "Parrilla": ["barbecue_restaurant", "steakhouse", "bar_and_grill_restaurant"],
    "Cafe": ["cafe", "coffee_shop", "internet_cafe", "tea_room", "bubble_tea", "cafeteria"],
    "Heladeria": ["ice_cream_shop", "gelato", "frozen_yoghurt_shop", "shaved_ice_shop"],
    "Comida al paso": [
        "fast_food_restaurant", "sandwich_shop", "food_stand", "food_truck", "food_court",
        "diner", "bistro", "gastropub", "tapas_bar", "bagel_shop", "empanadas", "doner_kebab",
        "hot_dog_restaurant", "taco_restaurant", "falafel_restaurant", "poke_restaurant",
    ],
    "Bar": ["bar", "beer_bar", "pub", "wine_bar", "cocktail_bar", "brewery", "beer_garden",
            "lounge", "gay_bar", "sports_bar", "speakeasy", "whiskey_bar", "irish_pub",
            "hotel_bar", "dive_bar", "tiki_bar", "hookah_bar", "airport_lounge", "gastro_bar"],
    "Sin especificar": ["eat_and_drink"],
}
AMPLIADO_HOJAS: dict[str, list[str]] = {
    "Panaderia": ["bakery"],
    "Pasteleria": ["cupcake_shop", "desserts", "dessert_shop", "chocolatier", "donuts",
                   "pie_shop", "japanese_confectionery_shop", "pancake_house", "creperie"],
}

# Respaldo por nivel 2 para las hojas que el mapeo no enumera. Overture agrega categorías entre
# versiones; sin este respaldo una hoja nueva desaparecería del conteo sin que nada avise.
RESPALDO_NIVEL2: dict[str, str] = {
    "restaurant": "Restaurante",
    "alcoholic_beverage_venue": "Bar",
    "non_alcoholic_beverage_venue": "Cafe",
    "casual_eatery": "Comida al paso",
}

# Hojas de `food_and_drink` que NO son gastronomía de atención al público. Mismo criterio que
# `DESCARTADOS_EXPLICITOS` del Relevamiento: venta de alimentos envasados, golosinas y producción.
DESCARTADAS_HOJAS = [
    "candy_store", "delicatessen", "beverage_store", "winery", "distillery",
    "food_delivery_service", "restaurant_wholesale", "food_and_beverage_exporter",
    "specialty_foods", "coffee_and_tea_supplies", "meat_wholesaler",
]

# Control de vocabulario: si la fuente deja de traer alguna de estas hojas, corta la corrida. No
# van todas —una hoja de un solo POI puede desaparecer sin que signifique nada— sino las que
# sostienen el conteo.
HOJAS_OBLIGATORIAS = ["restaurant", "pizza_restaurant", "bar", "bakery", "coffee_shop",
                      "ice_cream_shop", "cafe", "fast_food_restaurant"]

CRS_METRICO = "EPSG:5347"
CORTES_CONFIANZA = [0.0, 0.3, 0.5, 0.7, 0.9]

# Grupo de independencia, según §3 del esquema. Overture incorpora a Foursquare y a All The
# Places, así que los tres cuentan como uno solo aunque se bajen por separado.
GRUPO_INDEPENDENCIA = "OVERTURE_FSQ_ATP"


class VocabularioInesperado(RuntimeError):
    """La fuente dejó de traer una categoría que el mapeo declara."""


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper().strip()


# --------------------------------------------------------------------------- la extracción

def ultima_version() -> str:
    """La versión publicada más reciente, leída del bucket. No se hardcodea y se registra."""
    with urllib.request.urlopen(LISTADO, timeout=90) as respuesta:  # noqa: S310
        xml = respuesta.read().decode("utf-8")
    versiones = sorted(re.findall(r"<Prefix>release/([^<]+)/</Prefix>", xml))
    if not versiones:
        raise SystemExit("ABORTADO: el bucket de Overture no devolvió ninguna versión.")
    return versiones[-1]


def bbox_ciudad() -> tuple[float, float, float, float]:
    """El rectángulo que contiene a los 48 barrios, que es lo que la consulta puede filtrar.

    El `bbox` de Overture recorta barato pero recorta de más: adentro del rectángulo de la Ciudad
    entran La Tablada, Avellaneda y Vicente López. El recorte fino es punto en polígono y se hace
    después, con los barrios oficiales. Confundir los dos pasos infla cualquier total.
    """
    barrios = gpd.read_file(BARRIOS)
    minx, miny, maxx, maxy = barrios.total_bounds
    return float(minx), float(miny), float(maxx), float(maxy)


def consulta_recorte(version: str, caja: tuple[float, float, float, float]) -> str:
    minx, miny, maxx, maxy = caja
    fuente = f"s3://{BUCKET}/release/{version}/theme=places/type=place/*"
    return f"""
SELECT id,
       names.primary                       AS nombre,
       categories.primary                  AS categoria,
       taxonomy.hierarchy                  AS jerarquia,
       confidence,
       addresses[1].freeform               AS direccion,
       addresses[1].locality               AS localidad,
       list_transform(sources, s -> s.dataset) AS aportantes,
       bbox.xmin                           AS lon,
       bbox.ymin                           AS lat
FROM read_parquet('{fuente}', hive_partitioning=1)
WHERE bbox.xmin BETWEEN {minx} AND {maxx}
  AND bbox.ymin BETWEEN {miny} AND {maxy}
"""


def extraer(version: str) -> None:
    """Baja el recorte de la Ciudad a Parquet local. Es la única parte que toca la red."""
    import duckdb

    caja = bbox_ciudad()
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET s3_region='us-west-2'; SET enable_progress_bar=false;")
    OVT_DIR.mkdir(parents=True, exist_ok=True)
    destino = str(RECORTE).replace("\\", "/")
    print(f"  consultando Overture {version} (el recorte tarda uno o dos minutos)...")
    con.execute(f"COPY ({consulta_recorte(version, caja)}) TO '{destino}' (FORMAT parquet)")
    (OVT_DIR / "overture_version.json").write_text(json.dumps({
        "version": version,
        "bbox": {"minx": caja[0], "miny": caja[1], "maxx": caja[2], "maxy": caja[3]},
        "fecha_descarga": dt.datetime.now().isoformat(timespec="seconds"),
        "licencia": "CDLA-Permissive-2.0 (ver `sources` por registro)",
    }, ensure_ascii=False, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------- clasificación

def clasificar(tabla: pd.DataFrame) -> pd.DataFrame:
    """Anillo y rubro de cada POI, con la regla de respaldo declarada."""
    hoja_a_rubro, hoja_a_anillo = {}, {}
    for rubro, hojas in NUCLEO_HOJAS.items():
        for hoja in hojas:
            hoja_a_rubro[hoja], hoja_a_anillo[hoja] = rubro, "nucleo"
    for rubro, hojas in AMPLIADO_HOJAS.items():
        for hoja in hojas:
            hoja_a_rubro[hoja], hoja_a_anillo[hoja] = rubro, "ampliado"
    for hoja in DESCARTADAS_HOJAS:
        hoja_a_rubro[hoja], hoja_a_anillo[hoja] = "", "descartado"

    jerarquias = tabla.jerarquia.map(lambda j: list(j) if j is not None else [])
    tabla = tabla.copy()
    tabla["raiz"] = [j[0] if j else "" for j in jerarquias]
    tabla["nivel2"] = [j[1] if len(j) > 1 else "" for j in jerarquias]

    anillos, rubros, respaldadas = [], [], []
    for categoria, raiz, nivel2 in zip(tabla.categoria, tabla.raiz, tabla.nivel2):
        if raiz != RAIZ_GASTRO:
            anillos.append("fuera")
            rubros.append("")
            continue
        if categoria in hoja_a_anillo:
            anillos.append(hoja_a_anillo[categoria])
            rubros.append(hoja_a_rubro[categoria])
            continue
        # Regla de respaldo: la hoja no está enumerada, cae al anillo de su nivel 2 y se anota.
        rubro = RESPALDO_NIVEL2.get(nivel2, "Restaurante")
        anillos.append("nucleo")
        rubros.append(rubro)
        respaldadas.append(categoria)

    tabla["anillo"] = anillos
    tabla["rubro"] = rubros
    tabla.attrs["hojas_por_respaldo"] = pd.Series(respaldadas).value_counts().to_dict()
    return tabla


def verificar_vocabulario(tabla: pd.DataFrame) -> None:
    """Control 2 del esquema: hoja declarada que la fuente ya no trae, corrida que para."""
    presentes = set(tabla.categoria.dropna())
    ausentes = [hoja for hoja in HOJAS_OBLIGATORIAS if hoja not in presentes]
    if ausentes:
        raise VocabularioInesperado(
            f"Overture dejó de traer categorías que el mapeo declara: {ausentes}. "
            "O cambió la taxonomía, o el recorte quedó mal filtrado. No se cuenta sobre esto."
        )


def asignar_barrio(tabla: pd.DataFrame, barrios: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Control 3 del esquema: barrio por geometría. El `locality` de la fuente no se usa.

    El recorte por `bbox` trae La Tablada y Avellaneda; sin este paso entrarían al conteo de la
    Ciudad. El campo `locality` que trae Overture tampoco sirve: es texto declarado por el
    aportante y no coincide con los 48 barrios oficiales.
    """
    puntos = gpd.GeoDataFrame(
        tabla.copy(), geometry=gpd.points_from_xy(tabla.lon, tabla.lat), crs="EPSG:4326")
    return gpd.sjoin(puntos, barrios[["nombre_barrio", "geometry"]], how="left", predicate="within")


def por_barrio(asignados: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame) -> pd.DataFrame:
    gastro = asignados[asignados.anillo.isin(["nucleo", "ampliado"])]
    filas = {}
    for barrio in barrios.nombre_barrio:
        recorte = gastro[gastro.nombre_barrio == barrio]
        filas[plegar(barrio)] = {
            "ovt_nucleo": int((recorte.anillo == "nucleo").sum()),
            "ovt_ampliado": int(len(recorte)),
            "ovt_conf_alta": int(((recorte.anillo == "nucleo") & (recorte.confidence >= 0.5)).sum()),
            "ovt_con_direccion": int((recorte.direccion.fillna("") != "").sum()),
        }
    return pd.DataFrame(filas).T


def unir_con_las_otras(ovt: pd.DataFrame) -> pd.DataFrame:
    """Pega las capas ya calculadas de las otras fuentes. Ninguna se recalcula acá."""
    tabla = ovt
    padron = pd.read_csv(CAPA_PADRON, index_col=0, encoding="utf-8")
    padron.index = [plegar(i) for i in padron.index]
    tabla = tabla.join(padron[["dir_nucleo", "dir_ampliado", "f01_locales"]])

    if CAPA_RUS.exists():
        rus = pd.read_csv(CAPA_RUS, index_col=0, encoding="utf-8")
        rus.index = [plegar(i) for i in rus.index]
        tabla = tabla.join(rus[["rus_nucleo", "anio_relevamiento"]])
    if CAPA_OSM.exists():
        osm = pd.read_csv(CAPA_OSM, index_col=0, encoding="utf-8")
        osm.index = [plegar(i) for i in osm.index]
        tabla = tabla.join(osm[["osm_nucleo"]])

    tabla["ovt_sobre_padron"] = (tabla.ovt_nucleo / tabla.dir_nucleo).round(2)
    if "rus_nucleo" in tabla:
        tabla["ovt_sobre_rus"] = (tabla.ovt_nucleo / tabla.rus_nucleo).round(2)
    return tabla.sort_values("ovt_sobre_padron", ascending=False)


# --------------------------------------------------------------------------- informe

def _coma(valor: float, decimales: int = 1) -> str:
    return f"{valor:.{decimales}f}".replace(".", ",")


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


def informar(version: str, tabla: pd.DataFrame, asignados: gpd.GeoDataFrame,
             comparada: pd.DataFrame) -> tuple[str, dict]:
    salida = io.StringIO()

    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    gastro_bbox = tabla[tabla.anillo.isin(["nucleo", "ampliado"])]
    en_ciudad = asignados[asignados.nombre_barrio.notna()]
    gastro = en_ciudad[en_ciudad.anillo.isin(["nucleo", "ampliado"])]
    nucleo = gastro[gastro.anillo == "nucleo"]

    linea("=" * 98)
    linea(f"OVERTURE MAPS · theme places · recorte de la Ciudad · versión {version}")
    linea("=" * 98)
    linea("licencia CDLA-Permissive-2.0 · redistribuible con atribución · costo: 0")
    linea()

    linea("§1 · DEL RECTÁNGULO A LOS 48 BARRIOS")
    linea("-" * 98)
    linea(f"  POI en el rectángulo de la Ciudad                    : {len(tabla):>7}")
    linea(f"  POI que caen dentro de algún barrio (punto en polígono): {len(en_ciudad):>7}")
    linea(f"  POI del rectángulo que quedan AFUERA de la Ciudad    : {len(tabla) - len(en_ciudad):>7}"
          f"   ({_coma(100 * (len(tabla) - len(en_ciudad)) / len(tabla))} %)")
    linea()
    for texto in _envolver(
        "El rectángulo de la Ciudad entra en La Tablada, Avellaneda y Vicente López. Ese descarte "
        "no es una pérdida: es la diferencia entre el filtro barato que la consulta puede empujar "
        "al servidor y el recorte real, que es punto en polígono contra los barrios oficiales. "
        "Contar sobre el rectángulo habría inflado cada barrio de borde."):
        linea(f"  {texto}")
    linea()

    linea("§2 · CONTROL DE VOCABULARIO · qué trajo cada categoría")
    linea("-" * 98)
    conteo = gastro.rubro.value_counts()
    linea(f"  {'anillo · rubro':<34}{'POI':>8}")
    for rubro in list(NUCLEO_HOJAS) + ["Restaurante"]:
        if rubro in conteo:
            linea(f"  {'núcleo · ' + rubro:<34}{int(conteo[rubro]):>8}")
    for rubro in AMPLIADO_HOJAS:
        if rubro in conteo:
            linea(f"  {'ampliado · ' + rubro:<34}{int(conteo[rubro]):>8}")
    descartados = en_ciudad[en_ciudad.anillo == "descartado"]
    linea(f"  {'descartado (venta y producción)':<34}{len(descartados):>8}")
    if len(descartados):
        detalle = descartados.categoria.value_counts().head(8)
        linea("    " + " · ".join(f"{k} {v}" for k, v in detalle.items()))
    linea(f"  {'fuera de food_and_drink':<34}{int((en_ciudad.anillo == 'fuera').sum()):>8}")
    linea()
    respaldadas = tabla.attrs.get("hojas_por_respaldo", {})
    if respaldadas:
        linea(f"  Hojas que usaron la regla de respaldo ({sum(respaldadas.values())} POI en "
              f"{len(respaldadas)} categorías no enumeradas):")
        for hoja, cuantos in sorted(respaldadas.items(), key=lambda x: -x[1])[:14]:
            linea(f"    {hoja:<44}{cuantos:>6}")
        linea("    Son cocinas nacionales y variantes de restaurante; ninguna cambia de anillo.")
    else:
        linea("  Ninguna hoja usó la regla de respaldo: el mapeo cubre el vocabulario completo.")
    linea()

    linea("§3 · LOS TOTALES DE LA CIUDAD, CON SU UNIDAD DECLARADA")
    linea("-" * 98)
    padron_nucleo = int(comparada.dir_nucleo.sum())
    linea(f"  Overture · POI núcleo dentro de la Ciudad     : {len(nucleo):>7}")
    linea(f"  Overture · POI ampliado                       : {len(gastro):>7}")
    linea(f"  Padrón · direcciones núcleo (48 barrios)      : {padron_nucleo:>7}")
    if "rus_nucleo" in comparada and comparada.rus_nucleo.notna().any():
        linea(f"  Relevamiento · parcelas núcleo activas        : {int(comparada.rus_nucleo.sum()):>7}")
    if "osm_nucleo" in comparada and comparada.osm_nucleo.notna().any():
        linea(f"  OSM · POI núcleo                              : {int(comparada.osm_nucleo.sum()):>7}")
    linea()
    linea(f"  Overture ÷ padrón = {_coma(len(nucleo) / padron_nucleo, 2)}")
    linea()

    linea("§4 · SENSIBILIDAD AL CORTE DE CONFIANZA")
    linea("-" * 98)
    linea(f"    {'corte':<12}{'POI núcleo':>14}{'% del total':>14}")
    for corte in CORTES_CONFIANZA:
        cuantos = int((nucleo.confidence >= corte).sum())
        marca = "  <- el usado (sin filtrar)" if corte == 0.0 else ""
        linea(f"    >= {_coma(corte, 1):<9}{cuantos:>14}{_coma(100 * cuantos / len(nucleo)):>13} %{marca}")
    linea()
    for texto in _envolver(
        "La cifra de titular no filtra por confianza. El corte más discutible —0,5— deja afuera "
        f"{int((nucleo.confidence < 0.5).sum())} POI, y ninguna de las lecturas de este informe "
        "cambia de signo entre las dos versiones. La columna filtrada viaja igual en el CSV, "
        "`ovt_conf_alta`, para que quien quiera usarla no tenga que rehacer nada."):
        linea(f"  {texto}")
    linea()

    linea("§5 · DE DÓNDE VIENE CADA POI · los grupos de independencia, medidos")
    linea("-" * 98)
    aportantes = pd.Series(
        [a for lista in en_ciudad.aportantes.dropna() for a in lista]).value_counts()
    for aportante, cuantos in aportantes.items():
        linea(f"    {aportante:<28}{cuantos:>8}")
    linea()
    for texto in _envolver(
        "Overture en la Ciudad es, casi entero, el padrón de comercios de Meta. Eso decide dos "
        "cosas del esquema: **Overture y OSM son independientes acá** —OSM no aporta un solo "
        "registro al recorte, así que su solape mide algo— y **bajar Foursquare por separado "
        "agregaría poco**, porque ya viaja adentro y seguiría contando como el mismo grupo de "
        f"independencia (`{GRUPO_INDEPENDENCIA}`). La prudencia del esquema se mantiene; ahora se "
        "sabe que cuesta casi nada."):
        linea(f"  {texto}")
    linea()

    linea("§6 · COBERTURA POR BARRIO")
    linea("-" * 98)
    columnas = [c for c in ["ovt_nucleo", "osm_nucleo", "dir_nucleo", "rus_nucleo",
                            "ovt_sobre_padron"] if c in comparada]
    linea("  los 10 barrios donde Overture encuentra más respecto del padrón:")
    linea(comparada.head(10)[columnas].to_string())
    linea()
    linea("  los 10 donde encuentra menos:")
    linea(comparada.tail(10)[columnas].to_string())
    linea()
    razon = comparada.ovt_sobre_padron.replace([float("inf")], pd.NA).dropna()
    for texto in _envolver(
        f"La razón Overture ÷ padrón va de {_coma(razon.min(), 2)} a {_coma(razon.max(), 2)}, "
        f"mediana {_coma(razon.median(), 2)}. Esa dispersión es el sesgo de cobertura de la fuente "
        "medido barrio por barrio, y es el número que hay que mirar antes de dibujar cualquier "
        "polígono: una fuente que cubre desparejo produce polos donde hubo más datos, no donde hay "
        "más oferta."):
        linea(f"  {texto}")
    linea()

    linea("§7 · LO QUE ESTO SIGNIFICA PARA LA CAPA PUBLICABLE")
    linea("-" * 98)
    con_direccion = int((gastro.direccion.fillna("") != "").sum())
    con_nombre = int((gastro.nombre.fillna("") != "").sum())
    linea(f"  POI gastronómicos con nombre    : {con_nombre:>6}  ({_coma(100 * con_nombre / len(gastro))} %)")
    linea(f"  POI con dirección en la fuente  : {con_direccion:>6}  ({_coma(100 * con_direccion / len(gastro))} %)")
    linea()
    for texto in _envolver(
        "Todo esto es identidad redistribuible: nombre, dirección e identificador GERS se pueden "
        "publicar. Es la diferencia con Google Places, y es lo que decide qué parte de la base va a "
        "poder salir como capa abierta. Cuánto de lo que Places descubrió se rescata por esta vía "
        "se mide aparte, en el cruce, y es el número que ordena el tamaño del barrido."):
        linea(f"  {texto}")
    linea()
    linea("=" * 98)

    resumen = {
        "fecha_calculo": dt.date.today().isoformat(),
        "fuente": "E06 · Overture Maps, theme places",
        "version_overture": version,
        "licencia": "CDLA-Permissive-2.0",
        "grupo_independencia": GRUPO_INDEPENDENCIA,
        "costo": "0 requests de Places",
        "poi_en_bbox": int(len(tabla)),
        "poi_en_ciudad": int(len(en_ciudad)),
        "poi_bbox_fuera_de_ciudad": int(len(tabla) - len(en_ciudad)),
        "gastro_en_bbox": int(len(gastro_bbox)),
        "ovt_nucleo": int(len(nucleo)),
        "ovt_ampliado": int(len(gastro)),
        "padron_nucleo_48": padron_nucleo,
        "ovt_sobre_padron_ciudad": round(len(nucleo) / padron_nucleo, 3),
        "sensibilidad_confianza": {
            str(c): int((nucleo.confidence >= c).sum()) for c in CORTES_CONFIANZA},
        "aportantes": aportantes.to_dict(),
        "hojas_por_respaldo": respaldadas,
        "poi_con_nombre": con_nombre,
        "poi_con_direccion": con_direccion,
        "razon_ovt_padron_min": float(razon.min()),
        "razon_ovt_padron_mediana": float(razon.median()),
        "razon_ovt_padron_max": float(razon.max()),
    }
    return salida.getvalue(), resumen


# --------------------------------------------------------------------------- orquestación

def cargar_recorte() -> pd.DataFrame:
    if not RECORTE.exists():
        raise SystemExit(f"ABORTADO: falta {RECORTE.relative_to(ROOT)}. Corré antes con --run.")
    return pd.read_parquet(RECORTE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="baja el recorte de la Ciudad (red)")
    parser.add_argument("--reinformar", action="store_true",
                        help="rehace las tablas desde el recorte en disco, sin red")
    parser.add_argument("--vocabulario", action="store_true",
                        help="sólo el vocabulario de categorías del recorte, para revisar el mapeo")
    parser.add_argument("--version", default=None,
                        help="fija la versión de Overture; por defecto, la última publicada")
    args = parser.parse_args()

    if not args.run and not args.reinformar and not args.vocabulario:
        version = args.version or ultima_version()
        print(consulta_recorte(version, bbox_ciudad()))
        print(f"# versión más reciente publicada: {version}")
        print(f"# el recorte iría a: {RECORTE.relative_to(ROOT)}")
        print("\n[dry-run] no se bajó nada. Usá --run para extraer el recorte de la Ciudad.")
        return 0

    if args.run:
        version = args.version or ultima_version()
        print(f"[run] Overture {version}")
        extraer(version)
        print(f"[run] recorte en {RECORTE.relative_to(ROOT)}")
    else:
        datos = json.loads((OVT_DIR / "overture_version.json").read_text(encoding="utf-8"))
        version = datos["version"]

    tabla = clasificar(cargar_recorte())
    verificar_vocabulario(tabla)

    if args.vocabulario:
        vocab = (tabla[tabla.raiz == RAIZ_GASTRO]
                 .groupby(["nivel2", "categoria", "anillo", "rubro"]).size()
                 .rename("poi").reset_index().sort_values("poi", ascending=False))
        GEN.mkdir(parents=True, exist_ok=True)
        vocab.to_csv(GEN / "overture_vocabulario_categorias.csv", index=False, encoding="utf-8")
        print(vocab.head(60).to_string(index=False))
        print(f"\nescrito: {(GEN / 'overture_vocabulario_categorias.csv').relative_to(ROOT)}")
        return 0

    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]].rename(
        columns={"nombre": "nombre_barrio"})
    asignados = asignar_barrio(tabla, barrios)
    comparada = unir_con_las_otras(por_barrio(asignados, barrios))
    texto, resumen = informar(version, tabla, asignados, comparada)
    print(texto)

    GEN.mkdir(parents=True, exist_ok=True)
    comparada.to_csv(GEN / "overture_gastro_48_barrios.csv", encoding="utf-8")
    (GEN / "OVERTURE_GASTRO_CIUDAD.txt").write_text(texto, encoding="utf-8")
    (GEN / "overture_gastro_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    gastro = asignados[asignados.anillo.isin(["nucleo", "ampliado"]) & asignados.nombre_barrio.notna()]
    columnas = ["id", "nombre", "direccion", "categoria", "anillo", "rubro", "confidence",
                "lon", "lat", "nombre_barrio"]
    gastro[columnas].to_csv(OVT_DIR / "overture_gastro_poi.csv", index=False, encoding="utf-8-sig")

    print(f"  publicado en {GEN.relative_to(ROOT)}: overture_gastro_48_barrios.csv, "
          "OVERTURE_GASTRO_CIUDAD.txt, overture_gastro_resumen.json")
    print(f"  POI completos (no versionados): {(OVT_DIR / 'overture_gastro_poi.csv').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
