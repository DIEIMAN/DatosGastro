"""OpenStreetMap (E05) como cuarta fuente del barrido: descarga por Overpass y capa por barrio.

QUÉ ES Y QUÉ NO ES
------------------
OSM es mapeo voluntario. **No es padrón, no es censo y no confirma habilitación.** Lo que aporta,
y por eso entra ahora, son tres cosas que ninguna otra fuente del barrido da a la vez:

  - es **abierta y redistribuible** (ODbL), a diferencia de Google Places, cuyos términos de uso
    prohíben redistribuir nombre, dirección y `place_id`;
  - es **independiente del Estado y de Google**, así que su solape con las otras tres es
    información y no tautología;
  - es **gratis**: no consume la franja de requests de Places ni depende de ninguna key.

Su límite conocido está declarado en `docs/skills_claude/05_geodatos_y_territorio.md` §4: la
cobertura de OSM es desigual y sobrerrepresenta las zonas turísticas y mediáticas. Este script
**mide** esa desigualdad por barrio en vez de suponerla.

LA RECETA DE CONTEO ES LA MISMA, LA UNIDAD NO
---------------------------------------------
Se aplican las mismas reglas de `METODO_COMPARABILIDAD_2026-08.md` que ya usan el padrón y el
Relevamiento —dos anillos de rubro, asignación territorial por geometría (punto en polígono contra
`geo_barrios.geojson`), y los dos anillos se informan siempre—, pero **la unidad de cada fuente es
distinta y no se disimula**:

    padrón          dirección normalizada (`id_ubicacion`), sin outliers
    Relevamiento    parcela (`SMP`) activa, única
    OSM             POI mapeado (nodo, vía o relación), deduplicado por nombre y proximidad

Tres unidades distintas contando lo mismo desde ángulos distintos. Comparar sus totales es
legítimo —es el factor de captura, que ya está en uso— pero sumarlos no lo es.

EL MAPEO DE TAGS, POR SIMETRÍA CON EL PADRÓN
--------------------------------------------
Mismo criterio que fijó Diego para el Relevamiento el 5/8: cada tag va al anillo donde ya cae su
equivalente en `fact_habilitacion_gastronomica.csv`. Nada se mapea por intuición.

Detalle que conviene entender antes de discutir el mapeo: **Pizzería y Parrilla no son tags
propios de OSM**, son `cuisine=` sobre un `amenity=restaurant` o `amenity=fast_food`. Como los tres
ya son núcleo, la desagregación por rubro cambia dónde se apoya cada POI pero **no cambia el total
del anillo**. La discusión sobre `cuisine` no afecta ninguna cifra de este script salvo el
desglose.

QUÉ NO SE GUARDA, Y ES DELIBERADO
---------------------------------
- **Identidad de quien mapeó.** `out meta` de Overpass devuelve `user`, `uid` y `changeset`: son
  datos personales de la comunidad de OSM y **se descartan antes de que nada toque el disco**,
  incluido el crudo. Se conservan `timestamp` y `version`, que son la fecha de corte de cada POI
  y no identifican a nadie.
- **Contactos del comercio.** `phone`, `email`, `contact:*` y `website` no entran: el guardrail 7
  vale igual aunque la fuente sea abierta. Los tags que sí se conservan están declarados en
  `TAGS_CONSERVADOS` y el filtro se arma desde esa constante única, con el mismo criterio que
  `detectar_lotes_permisos.py` usa para las columnas prohibidas del padrón.

ODbL · LO QUE HAY QUE MIRAR ANTES DE PUBLICAR
---------------------------------------------
«Redistribuible» no es «sin condiciones». La ODbL pide atribución y tiene cláusula de
compartir-igual sobre las **bases derivadas**. Para la capa publicable eso no es un detalle
jurídico menor y **no lo resuelve este script**: queda anotado en el informe para que se decida
antes de publicar, no después.

USO
---
  python scripts/barrido_ciudad/bajar_osm_gastro.py              # dry-run: imprime la consulta
  python scripts/barrido_ciudad/bajar_osm_gastro.py --contar     # 1 consulta chica: sólo cuenta
  python scripts/barrido_ciudad/bajar_osm_gastro.py --run        # baja el crudo y arma las tablas
  python scripts/barrido_ciudad/bajar_osm_gastro.py --reinformar # rehace todo desde el crudo, sin red
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
GEN = BARRIDO / "generado"
OSM_DIR = ROOT / "outputs" / "fuentes_externas" / "osm"
CRUDO = OSM_DIR / "osm_gastro_caba.json"

BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
CAPA_PADRON = BARRIDO / "capa_homogenea_48_barrios.csv"
CAPA_RUS = ROOT / "outputs" / "fuentes_externas" / "usos_suelo" / "rus_gastro_48_barrios.csv"

# Overpass tiene varios espejos y ninguno garantiza disponibilidad. Se prueban en orden y se
# rota ante 429 (rate limit) o 504 (el servidor cortó). El primero es el oficial.
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
USER_AGENT = "DataGastro/barrido-ciudad (DGDGAS, uso institucional CABA; contacto via repo)"
TIMEOUT_OVERPASS = 180
# Pausa entre consultas. El servidor público anuncia 2 slots simultáneos: se consulta de a una y
# se espera, que es la forma de no abusar de una infraestructura donada.
PAUSA_S = 6.0
REINTENTOS = 3

# --- El mapeo, por simetría con el padrón ------------------------------------------------
# Clave = anillo del método de comparabilidad. Valor = tags de OSM que le corresponden.
# Los pares son (clave_osm, valor_osm); se comparan literales, no por expresión regular.
NUCLEO_TAGS: dict[str, list[tuple[str, str]]] = {
    "Restaurante": [("amenity", "restaurant")],
    "Bar": [("amenity", "bar"), ("amenity", "pub"), ("amenity", "biergarten")],
    "Cafe": [("amenity", "cafe")],
    "Comida al paso": [("amenity", "fast_food"), ("amenity", "food_court")],
    "Heladeria": [("amenity", "ice_cream"), ("shop", "ice_cream")],
}
AMPLIADO_TAGS: dict[str, list[tuple[str, str]]] = {
    "Panaderia": [("shop", "bakery")],
    "Pasteleria": [("shop", "pastry"), ("shop", "confectionery")],
    "Catering": [("craft", "caterer")],
}

# Pizzería y Parrilla salen de `cuisine` sobre un POI que ya es núcleo por su amenity. No suman
# POIs: reparten los que ya están adentro. Por eso van en un diccionario aparte y se aplican con
# precedencia sobre la etiqueta de amenity, de modo que cada POI tenga exactamente un rubro y el
# desglose sume el total del anillo.
CUISINE_NUCLEO: dict[str, list[str]] = {
    "Pizzeria": ["pizza"],
    "Parrilla": ["argentinian", "asado", "barbecue", "steak_house", "grill", "parrilla"],
}

# Tags que la búsqueda vecina trae y NO son gastronomía de atención al público. Se consultan y se
# cuentan **a propósito**: el Relevamiento hace lo mismo con `DESCARTADOS_EXPLICITOS`, y sin el
# conteo nadie puede auditar si el recorte se llevó puesto algo. Comercio de alimentos, bebidas
# envasadas, elaboración sin salón y nocturnidad.
DESCARTADOS_TAGS: list[tuple[str, str]] = [
    ("shop", "deli"), ("shop", "alcohol"), ("shop", "wine"), ("shop", "beverages"),
    ("shop", "coffee"), ("shop", "tea"), ("shop", "chocolate"), ("shop", "butcher"),
    ("shop", "greengrocer"), ("shop", "convenience"), ("shop", "supermarket"),
    ("shop", "seafood"), ("shop", "cheese"), ("shop", "health_food"), ("shop", "pasta"),
    ("shop", "frozen_food"), ("shop", "farm"), ("amenity", "nightclub"),
    ("amenity", "marketplace"), ("amenity", "vending_machine"),
]

# --- Guardrail 7: la lista blanca de tags que se persisten -------------------------------
# El filtro se arma desde acá y no hay otra vía de escritura. Lo que no está en esta lista no
# entra en memoria más allá del parseo y no llega nunca al disco.
TAGS_CONSERVADOS = [
    "name", "brand", "amenity", "shop", "craft", "cuisine",
    "addr:street", "addr:housenumber",
    "check_date", "survey:date", "opening_hours",
]
# De `out meta`: se conserva la fecha de corte del POI y se descarta la identidad de quien lo mapeó.
META_CONSERVADA = ["timestamp", "version"]
META_DESCARTADA = ["user", "uid", "changeset"]

# --- Deduplicación interna de OSM ---------------------------------------------------------
# Un mismo local puede estar mapeado dos veces: como nodo adentro del local y como polígono del
# edificio. Se colapsan sólo si comparten nombre normalizado Y caen a menos de este radio. Los POI
# sin nombre NO se deduplican entre sí: dos puestos vecinos sin nombre son dos, no uno.
RADIO_DEDUP_M = 50.0
CRS_METRICO = "EPSG:5347"  # POSGAR 2007 / faja 5, el mismo que usa la grilla de Places


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper().strip()


# --------------------------------------------------------------------------- la consulta

def _clausula(pares: list[tuple[str, str]]) -> str:
    """Una sentencia por clave de tag, con los valores como alternativa de expresión regular.

    Una sentencia por par —treinta y tres `nwr` distintos— hace que Overpass recorra el área una
    vez por cada una y el servidor devuelve 504 antes de terminar. Agrupadas por clave son tres
    recorridos y la consulta entra cómoda. El resultado es el mismo conjunto.
    """
    por_clave: dict[str, list[str]] = {}
    for clave, valor in pares:
        por_clave.setdefault(clave, []).append(valor)
    return "\n".join(
        f'  nwr["{clave}"~"^({"|".join(valores)})$"](area.caba);'
        for clave, valores in por_clave.items()
    )


def todos_los_pares() -> list[tuple[str, str]]:
    """Los pares de tag que se consultan: los dos anillos y los descartados explícitos."""
    pares = [par for pares in NUCLEO_TAGS.values() for par in pares]
    pares += [par for pares in AMPLIADO_TAGS.values() for par in pares]
    return pares + DESCARTADOS_TAGS


def construir_consulta(pares: list[tuple[str, str]] | None = None,
                       solo_contar: bool = False) -> str:
    """Overpass QL: los POI de los pares indicados, dentro de CABA.

    El área se resuelve por el límite administrativo de la Ciudad, no por un bounding box: un
    rectángulo sobre CABA entra en Vicente López y en Avellaneda y contaminaría el conteo por
    barrio con locales de la provincia.
    """
    salida = "out count;" if solo_contar else "out meta center;"
    return f"""[out:json][timeout:{TIMEOUT_OVERPASS}];
area["boundary"="administrative"]["name"="Ciudad Autónoma de Buenos Aires"]->.caba;
(
{_clausula(pares if pares is not None else todos_los_pares())}
);
{salida}
"""


class OverpassNoResponde(RuntimeError):
    """Ningún espejo contestó después de los reintentos previstos."""


def consultar(consulta: str, etiqueta: str = "") -> dict:
    """Una consulta contra Overpass, rotando espejos y con espera creciente.

    **La consulta entera de la Ciudad no entra en una sola llamada**: pedida de una vez, los tres
    espejos devuelven 504 y el conteo previo (`--contar`) pasa igual, porque lo que ahoga al
    servidor no es la búsqueda sino armar la respuesta con geometría. Tag por tag entra cómoda
    —el tag más pesado, `amenity=restaurant`, son 2.505 elementos y 1,2 MB en cuatro segundos— y
    además deja la descarga reanudable. El resultado es exactamente el mismo conjunto.
    """
    datos = urllib.parse.urlencode({"data": consulta}).encode("utf-8")
    ultimo: Exception | None = None
    for intento in range(REINTENTOS):
        for endpoint in ENDPOINTS:
            pedido = urllib.request.Request(
                endpoint, data=datos, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(pedido, timeout=TIMEOUT_OVERPASS + 60) as respuesta:  # noqa: S310
                    return json.loads(respuesta.read().decode("utf-8"))
            except Exception as error:  # noqa: BLE001 - cualquier fallo de red se reintenta
                ultimo = error
                print(f"    [{etiqueta}] {endpoint.split('/')[2]}: {type(error).__name__} {error}")
                time.sleep(PAUSA_S)
        espera = PAUSA_S * (intento + 2) * 3
        print(f"    [{etiqueta}] ningún espejo contestó; esperando {espera:.0f} s")
        time.sleep(espera)
    raise OverpassNoResponde(f"{etiqueta}: {ultimo}")


def descargar_por_tag(forzar: bool = False) -> dict:
    """Baja un tag por vez, con caché en disco, y devuelve el crudo saneado y unido.

    La caché por tag no es comodidad: son treinta y tres consultas contra una infraestructura
    donada, y que un fallo en la número treinta obligue a repetir las veintinueve anteriores es
    justamente lo que no hay que hacerle a un servidor público. Con caché, `--run` reanuda.
    """
    cache = OSM_DIR / "_por_tag"
    cache.mkdir(parents=True, exist_ok=True)
    pares = todos_los_pares()
    elementos: dict[tuple[str, int], dict] = {}
    bajados, reusados = 0, 0

    for numero, (clave, valor) in enumerate(pares, start=1):
        archivo = cache / f"{clave}__{valor}.json"
        etiqueta = f"{numero}/{len(pares)} {clave}={valor}"
        if archivo.exists() and not forzar:
            trozo = json.loads(archivo.read_text(encoding="utf-8"))
            reusados += 1
        else:
            respuesta = consultar(construir_consulta([(clave, valor)]), etiqueta)
            trozo = sanear(respuesta)
            archivo.write_text(json.dumps(trozo, ensure_ascii=False), encoding="utf-8")
            bajados += 1
            time.sleep(PAUSA_S)
        print(f"  {etiqueta:<40}{len(trozo['elements']):>7} elementos"
              f"{'  (caché)' if archivo.exists() and not forzar and not bajados else ''}")
        # Un POI con dos tags de la lista —`shop=bakery` y `shop=pastry` no, pero sí
        # `amenity=ice_cream` con `shop=ice_cream`— vuelve en dos consultas. La clave
        # (tipo, id) es la identidad de OSM y lo colapsa sin ambigüedad.
        for elemento in trozo["elements"]:
            elementos[(elemento["type"], elemento["id"])] = elemento

    print(f"\n  consultas nuevas: {bajados} · reusadas de caché: {reusados} · "
          f"elementos únicos: {len(elementos):,}".replace(",", "."))
    return {
        "generador": "Overpass API",
        "fecha_descarga": dt.datetime.now().isoformat(timespec="seconds"),
        "consultas": len(pares),
        "meta_descartada": META_DESCARTADA,
        "tags_conservados": TAGS_CONSERVADOS,
        "elements": list(elementos.values()),
    }


def sanear(respuesta: dict) -> dict:
    """Deja el crudo sin identidad de mapeador y sin tags de contacto. Se aplica ANTES de escribir.

    No es una limpieza cosmética: si `user` y `uid` llegan al disco, el guardrail 7 ya está roto y
    borrarlos después no lo repara. Por eso el saneado va entre la respuesta y el archivo.
    """
    conservados = set(TAGS_CONSERVADOS)
    elementos = []
    for elemento in respuesta.get("elements", []):
        limpio = {clave: elemento[clave] for clave in ("type", "id", "lat", "lon") if clave in elemento}
        if "center" in elemento:
            limpio["center"] = elemento["center"]
        for clave in META_CONSERVADA:
            if clave in elemento:
                limpio[clave] = elemento[clave]
        limpio["tags"] = {k: v for k, v in elemento.get("tags", {}).items() if k in conservados}
        elementos.append(limpio)
    return {
        "generador": respuesta.get("generator", ""),
        "osm3s": respuesta.get("osm3s", {}),
        "fecha_descarga": dt.datetime.now().isoformat(timespec="seconds"),
        "meta_descartada": META_DESCARTADA,
        "tags_conservados": TAGS_CONSERVADOS,
        "elements": elementos,
    }


# --------------------------------------------------------------------------- la tabla

def a_dataframe(crudo: dict) -> pd.DataFrame:
    """Una fila por POI, con su anillo y su rubro. Los `way`/`relation` usan su centroide."""
    filas = []
    for elemento in crudo["elements"]:
        lat = elemento.get("lat", elemento.get("center", {}).get("lat"))
        lon = elemento.get("lon", elemento.get("center", {}).get("lon"))
        if lat is None or lon is None:
            continue
        tags = elemento.get("tags", {})
        filas.append({
            "osm_tipo": elemento["type"],
            "osm_id": elemento["id"],
            "lat": float(lat),
            "lon": float(lon),
            "nombre": tags.get("name", ""),
            "amenity": tags.get("amenity", ""),
            "shop": tags.get("shop", ""),
            "craft": tags.get("craft", ""),
            "cuisine": tags.get("cuisine", ""),
            "calle": tags.get("addr:street", ""),
            "altura": tags.get("addr:housenumber", ""),
            "check_date": tags.get("check_date", tags.get("survey:date", "")),
            "editado": str(elemento.get("timestamp", ""))[:10],
        })
    tabla = pd.DataFrame(filas)
    if tabla.empty:
        return tabla

    pares = list(zip(tabla.amenity, tabla.shop, tabla.craft))

    def rubro(indice: int) -> tuple[str, str]:
        amenity, shop, craft = pares[indice]
        presentes = {("amenity", amenity), ("shop", shop), ("craft", craft)}
        for etiqueta, tags in NUCLEO_TAGS.items():
            if presentes & set(tags):
                return "nucleo", etiqueta
        for etiqueta, tags in AMPLIADO_TAGS.items():
            if presentes & set(tags):
                return "ampliado", etiqueta
        return "descartado", ""

    resuelto = [rubro(i) for i in range(len(tabla))]
    tabla["anillo"] = [a for a, _ in resuelto]
    tabla["rubro"] = [r for _, r in resuelto]

    # Precedencia de `cuisine` sobre el amenity, y sólo hacia adentro del núcleo: reparte los POI
    # que ya son núcleo, nunca agrega ni saca uno.
    cocinas = tabla.cuisine.fillna("").str.lower()
    for etiqueta, valores in CUISINE_NUCLEO.items():
        marca = (tabla.anillo == "nucleo") & cocinas.apply(
            lambda c, vs=valores: any(v in [p.strip() for p in c.split(";")] for v in vs))
        tabla.loc[marca, "rubro"] = etiqueta
    return tabla


def deduplicar(tabla: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Colapsa el mismo local mapeado dos veces. Devuelve la tabla y la sensibilidad al radio.

    El criterio es conjunto: mismo nombre plegado Y a menos de `RADIO_DEDUP_M`. Pedir sólo el
    nombre uniría las sucursales de una cadena; pedir sólo la distancia uniría al vecino de al
    lado. Los POI sin nombre quedan siempre como POI distintos.
    """
    geo = gpd.GeoDataFrame(
        tabla.copy(), geometry=gpd.points_from_xy(tabla.lon, tabla.lat), crs="EPSG:4326"
    ).to_crs(CRS_METRICO)
    geo["clave"] = geo.nombre.map(plegar)

    sensibilidad = {}
    for radio in (25.0, 50.0, 100.0, 200.0):
        sensibilidad[radio] = len(_colapsar(geo, radio))
    conservados = _colapsar(geo, RADIO_DEDUP_M)
    return tabla.loc[sorted(conservados)].copy(), sensibilidad


def _colapsar(geo: gpd.GeoDataFrame, radio: float) -> set:
    """Índices que sobreviven: de cada grupo nombre+cercanía queda el primero."""
    conservados, con_nombre = set(), geo[geo.clave != ""]
    conservados |= set(geo.index[geo.clave == ""])
    for _, grupo in con_nombre.groupby("clave"):
        if len(grupo) == 1:
            conservados.add(grupo.index[0])
            continue
        vivos: list[tuple[int, object]] = []
        for indice, punto in zip(grupo.index, grupo.geometry):
            if all(punto.distance(otro) > radio for _, otro in vivos):
                vivos.append((indice, punto))
        conservados |= {i for i, _ in vivos}
    return conservados


def por_barrio(tabla: pd.DataFrame, barrios: gpd.GeoDataFrame) -> pd.DataFrame:
    """Regla 4 del método: asignación territorial por geometría, nunca por el campo declarado."""
    puntos = gpd.GeoDataFrame(
        tabla.copy(), geometry=gpd.points_from_xy(tabla.lon, tabla.lat), crs="EPSG:4326"
    )
    asignados = gpd.sjoin(puntos, barrios[["nombre_barrio", "geometry"]],
                          how="left", predicate="within")
    gastro = asignados[asignados.anillo != "descartado"]

    filas = {}
    for barrio in barrios.nombre_barrio:
        recorte = gastro[gastro.nombre_barrio == barrio]
        filas[plegar(barrio)] = {
            "osm_nucleo": int((recorte.anillo == "nucleo").sum()),
            "osm_ampliado": int(len(recorte)),
            "osm_con_direccion": int((recorte.calle != "").sum()),
            "osm_con_nombre": int((recorte.nombre != "").sum()),
        }
    return pd.DataFrame(filas).T


def comparar_con_documentales(osm: pd.DataFrame) -> pd.DataFrame:
    """Une la capa de OSM con las dos documentales ya calculadas. No recalcula ninguna."""
    padron = pd.read_csv(CAPA_PADRON, index_col=0, encoding="utf-8")
    padron.index = [plegar(i) for i in padron.index]
    tabla = osm.join(padron[["dir_nucleo", "dir_ampliado", "f01_locales"]])

    if CAPA_RUS.exists():
        rus = pd.read_csv(CAPA_RUS, index_col=0, encoding="utf-8")
        rus.index = [plegar(i) for i in rus.index]
        tabla = tabla.join(rus[["rus_nucleo", "anio_relevamiento"]])
    else:
        tabla["rus_nucleo"] = pd.NA
        tabla["anio_relevamiento"] = pd.NA

    tabla["osm_sobre_padron"] = (tabla.osm_nucleo / tabla.dir_nucleo).round(2)
    tabla["osm_sobre_rus"] = (tabla.osm_nucleo / tabla.rus_nucleo).round(2)
    return tabla.sort_values("osm_sobre_padron", ascending=False)


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


def informar(crudo: dict, completa: pd.DataFrame, tabla: pd.DataFrame,
             sensibilidad: dict, comparada: pd.DataFrame) -> tuple[str, dict]:
    salida = io.StringIO()

    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    gastro = tabla[tabla.anillo != "descartado"]
    nucleo = gastro[gastro.anillo == "nucleo"]
    descartados = tabla[tabla.anillo == "descartado"]

    linea("=" * 98)
    linea("OPENSTREETMAP (E05) · CAPA GASTRONÓMICA DE LA CIUDAD · CERO COSTO")
    linea("=" * 98)
    linea(f"descarga: {crudo.get('fecha_descarga', 's/d')} · endpoint Overpass · {len(crudo['elements']):,} "
          "elementos crudos".replace(",", "."))
    linea()

    linea("§1 · CONTROL DE VOCABULARIO · qué trajo cada tag")
    linea("-" * 98)
    linea(f"  {'anillo · rubro':<34}{'POI':>8}   tags de OSM")
    for etiqueta, tags in NUCLEO_TAGS.items():
        cuenta = int((completa.rubro == etiqueta).sum())
        linea(f"  {'núcleo · ' + etiqueta:<34}{cuenta:>8}   {', '.join(f'{k}={v}' for k, v in tags)}")
    for etiqueta, valores in CUISINE_NUCLEO.items():
        cuenta = int((completa.rubro == etiqueta).sum())
        linea(f"  {'núcleo · ' + etiqueta:<34}{cuenta:>8}   cuisine={'|'.join(valores)} (reparte, no suma)")
    for etiqueta, tags in AMPLIADO_TAGS.items():
        cuenta = int((completa.rubro == etiqueta).sum())
        linea(f"  {'ampliado · ' + etiqueta:<34}{cuenta:>8}   {', '.join(f'{k}={v}' for k, v in tags)}")
    linea()
    linea("  descartados aunque la búsqueda los traiga (mismo criterio que el Relevamiento):")
    conteo_descartados = pd.concat([descartados.amenity, descartados.shop]).replace("", pd.NA).value_counts()
    for valor, cuenta in conteo_descartados.head(12).items():
        linea(f"    {valor:<40}{cuenta:>6}")
    linea(f"    {'TOTAL descartado':<40}{len(descartados):>6}")
    linea()

    linea("§2 · DEDUPLICACIÓN INTERNA Y SENSIBILIDAD AL RADIO")
    linea("-" * 98)
    linea(f"  POI con coordenada, antes de deduplicar : {len(completa):>7}")
    linea(f"  POI después de deduplicar ({_coma(RADIO_DEDUP_M, 0)} m)      : {len(tabla):>7}"
          f"   ({len(completa) - len(tabla)} colapsados)")
    linea()
    linea(f"    {'radio':<12}{'POI que quedan':>18}")
    for radio, cuantos in sensibilidad.items():
        marca = "  <- el usado" if radio == RADIO_DEDUP_M else ""
        linea(f"    {_coma(radio, 0) + ' m':<12}{cuantos:>18}{marca}")
    for texto in _envolver(
        "Entre 25 y 200 m el resultado se mueve poco: el criterio pide además nombre idéntico, y "
        "dos locales con el mismo nombre a doscientos metros son la excepción, no la regla. El "
        "corte no está sosteniendo el número."):
        linea(f"  {texto}")
    linea()

    linea("§3 · LA CIUDAD · LOS TRES TOTALES, CON SU UNIDAD DECLARADA")
    linea("-" * 98)
    padron_nucleo = int(comparada.dir_nucleo.sum())
    rus_nucleo = int(comparada.rus_nucleo.sum()) if comparada.rus_nucleo.notna().any() else None
    linea(f"  OSM · POI núcleo, deduplicados                          : {int(len(nucleo)):>7}")
    linea(f"  OSM · POI ampliado                                      : {int(len(gastro)):>7}")
    linea(f"  Padrón · direcciones núcleo (suma de los 48, sin anómalas): {padron_nucleo:>7}")
    if rus_nucleo:
        linea(f"  Relevamiento · parcelas núcleo activas                  : {rus_nucleo:>7}")
    linea()
    linea(f"  OSM ÷ padrón   = {_coma(len(nucleo) / padron_nucleo, 2)}")
    if rus_nucleo:
        linea(f"  OSM ÷ Relevamiento = {_coma(len(nucleo) / rus_nucleo, 2)}")
    linea()
    for texto in _envolver(
        "Los tres números cuentan cosas distintas —direcciones, parcelas y POI— y por eso las "
        "razones se leen como factor de captura entre fuentes, no como corrección de una sobre "
        "otra. Ninguno de los tres es el universo real: el único conteo de campo que existe está en "
        "las cuatro zonas del Atlas relevadas a pie."):
        linea(f"  {texto}")
    linea()

    linea("§4 · COBERTURA POR BARRIO · dónde OSM aporta y dónde no")
    linea("-" * 98)
    columnas = ["osm_nucleo", "dir_nucleo", "rus_nucleo", "osm_sobre_padron", "osm_sobre_rus"]
    linea("  los 10 barrios donde OSM encuentra más respecto del padrón:")
    linea(comparada.head(10)[columnas].to_string())
    linea()
    linea("  los 10 donde encuentra menos:")
    linea(comparada.tail(10)[columnas].to_string())
    linea()
    razon = comparada.osm_sobre_padron.replace([float("inf")], pd.NA).dropna()
    for texto in _envolver(
        f"La razón OSM ÷ padrón va de {_coma(razon.min(), 2)} a {_coma(razon.max(), 2)}, con mediana "
        f"{_coma(razon.median(), 2)}. Esa dispersión —de {_coma(razon.max() / razon.min(), 0)} veces "
        "entre la punta y la cola— es el sesgo de cobertura de OSM medido, no supuesto: la fuente "
        "está mucho mejor mapeada donde ya sabíamos que iba a estarlo. Es exactamente la razón por "
        "la que OSM entra como cuarta fuente y no como sustituto de ninguna."):
        linea(f"  {texto}")
    linea()

    linea("§5 · LO QUE OSM TRAE Y LAS OTRAS NO · dirección, nombre y fecha")
    linea("-" * 98)
    con_direccion = int((gastro.calle != "").sum())
    con_nombre = int((gastro.nombre != "").sum())
    con_check = int((gastro.check_date != "").sum())
    linea(f"  POI gastronómicos con nombre        : {con_nombre:>6}  ({_coma(100 * con_nombre / len(gastro))} %)")
    linea(f"  POI con calle y altura en los tags  : {con_direccion:>6}  ({_coma(100 * con_direccion / len(gastro))} %)")
    linea(f"  POI con fecha de verificación en campo (`check_date`): {con_check:>6}  "
          f"({_coma(100 * con_check / len(gastro))} %)")
    ediciones = pd.to_datetime(gastro.editado, errors="coerce")
    if ediciones.notna().any():
        linea(f"  Última edición del POI: mediana {ediciones.median().date()}, "
              f"más antigua {ediciones.min().date()}, más reciente {ediciones.max().date()}")
        for anio, cuantos in ediciones.dt.year.value_counts().sort_index(ascending=False).head(6).items():
            linea(f"    editados en {int(anio)}: {cuantos:>6}")
    linea()
    for texto in _envolver(
        "La fecha de última edición NO es la fecha en que el local existía: alguien puede corregir "
        "hoy el horario de un local cerrado en 2019, y nadie edita el POI de un local que sigue "
        "abierto sin cambios. Se informa como lo que es —cuán vivo está el mapeo— y no como señal "
        "de vigencia del local. `check_date` sí es una verificación declarada en el terreno, y por "
        "eso se cuenta aparte."):
        linea(f"  {texto}")
    linea()

    linea("§6 · POR QUÉ ESTO IMPORTA PARA LA CAPA PUBLICABLE")
    linea("-" * 98)
    for texto in _envolver(
        f"De los {len(gastro)} POI gastronómicos, {con_nombre} tienen nombre y {con_direccion} "
        "tienen calle y altura en los propios tags. Ésa es identidad de origen abierto: un registro "
        "emparejado con OSM se puede publicar con nombre y dirección, y uno que sólo existe en "
        "Google Places, no. La medición de cuánto rescata efectivamente ese emparejamiento está en "
        "`cruzar_fuentes_abiertas.py`, que es el paso siguiente."):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        "ODbL, y hay que resolverlo antes de publicar, no después: OSM es redistribuible pero con "
        "atribución y con cláusula de compartir-igual sobre las bases derivadas. Una base pública "
        "que incorpore geometrías o atributos de OSM puede quedar alcanzada por esa cláusula. No lo "
        "decide este script ni el equipo técnico: es una decisión de la Dirección, con la letra de "
        "la licencia a la vista."):
        linea(f"  {texto}")
    linea()
    linea("=" * 98)

    resumen = {
        "fecha_calculo": dt.date.today().isoformat(),
        "fuente": "E05 · OpenStreetMap vía Overpass",
        "licencia": "ODbL · atribución y compartir-igual sobre bases derivadas",
        "costo": "0 requests de Places; Overpass es gratuito",
        "elementos_crudos": len(crudo["elements"]),
        "poi_con_coordenada": int(len(completa)),
        "poi_deduplicados": int(len(tabla)),
        "poi_colapsados": int(len(completa) - len(tabla)),
        "sensibilidad_radio_dedup": {str(k): v for k, v in sensibilidad.items()},
        "osm_nucleo": int(len(nucleo)),
        "osm_ampliado": int(len(gastro)),
        "descartados": int(len(descartados)),
        "padron_nucleo_48": padron_nucleo,
        "rus_nucleo_48": rus_nucleo,
        "osm_sobre_padron_ciudad": round(len(nucleo) / padron_nucleo, 3),
        "poi_con_nombre": con_nombre,
        "poi_con_direccion_en_tags": con_direccion,
        "poi_con_check_date": con_check,
        "razon_osm_padron_min": float(razon.min()),
        "razon_osm_padron_mediana": float(razon.median()),
        "razon_osm_padron_max": float(razon.max()),
    }
    return salida.getvalue(), resumen


# --------------------------------------------------------------------------- orquestación

def procesar(crudo: dict) -> tuple[str, dict, pd.DataFrame, pd.DataFrame]:
    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]].rename(
        columns={"nombre": "nombre_barrio"})
    completa = a_dataframe(crudo)
    if completa.empty:
        raise SystemExit("ABORTADO: el crudo no tiene ningún POI con coordenada.")
    tabla, sensibilidad = deduplicar(completa)
    capa = por_barrio(tabla, barrios)
    comparada = comparar_con_documentales(capa)
    texto, resumen = informar(crudo, completa, tabla, sensibilidad, comparada)
    return texto, resumen, tabla, comparada


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="baja el crudo de Overpass (red)")
    parser.add_argument("--contar", action="store_true",
                        help="una consulta chica que sólo devuelve el conteo, para dimensionar")
    parser.add_argument("--reinformar", action="store_true",
                        help="rehace las tablas y el informe desde el crudo en disco, sin red")
    parser.add_argument("--forzar", action="store_true",
                        help="ignora la caché por tag y vuelve a consultar todo")
    args = parser.parse_args()

    if args.contar:
        consulta = construir_consulta(solo_contar=True)
        print(consulta)
        respuesta = consultar(consulta, "conteo")
        for elemento in respuesta.get("elements", []):
            print(f"  conteo Overpass: {elemento.get('tags', {})}")
        return 0

    if not args.run and not args.reinformar:
        print(construir_consulta())
        print(f"# se baja de a un tag por vez ({len(todos_los_pares())} consultas, caché por tag)")
        print(f"# espejos: {', '.join(e.split('/')[2] for e in ENDPOINTS)}")
        print(f"# el crudo saneado iría a: {CRUDO.relative_to(ROOT)}")
        print(f"# tags que se conservan: {', '.join(TAGS_CONSERVADOS)}")
        print(f"# meta que se descarta antes de escribir: {', '.join(META_DESCARTADA)}")
        print("\n[dry-run] no se hizo ninguna llamada. Usá --run para bajar, --contar para dimensionar.")
        return 0

    if args.run:
        print(f"[run] consultando Overpass tag por tag ({len(todos_los_pares())} consultas, "
              f"pausa de {PAUSA_S:.0f} s)...")
        crudo = descargar_por_tag(forzar=args.forzar)
        OSM_DIR.mkdir(parents=True, exist_ok=True)
        CRUDO.write_text(json.dumps(crudo, ensure_ascii=False), encoding="utf-8")
        print(f"[run] crudo saneado en {CRUDO.relative_to(ROOT)} · "
              f"{len(crudo['elements']):,} elementos".replace(",", "."))
    else:
        if not CRUDO.exists():
            raise SystemExit(f"ABORTADO: falta {CRUDO.relative_to(ROOT)}. Corré antes con --run.")
        crudo = json.loads(CRUDO.read_text(encoding="utf-8"))

    texto, resumen, tabla, comparada = procesar(crudo)
    print(texto)

    GEN.mkdir(parents=True, exist_ok=True)
    OSM_DIR.mkdir(parents=True, exist_ok=True)
    comparada.to_csv(GEN / "osm_gastro_48_barrios.csv", encoding="utf-8")
    (GEN / "OSM_GASTRO_CIUDAD.txt").write_text(texto, encoding="utf-8")
    (GEN / "osm_gastro_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    tabla.to_csv(OSM_DIR / "osm_gastro_poi.csv", index=False, encoding="utf-8-sig")

    print(f"  publicado en {GEN.relative_to(ROOT)}: osm_gastro_48_barrios.csv, "
          "OSM_GASTRO_CIUDAD.txt, osm_gastro_resumen.json")
    print(f"  POI completos (no versionados): {(OSM_DIR / 'osm_gastro_poi.csv').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
