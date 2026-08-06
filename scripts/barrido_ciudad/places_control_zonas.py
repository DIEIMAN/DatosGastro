"""Control de Google Places sobre las 17 zonas con cifra publicada. Grilla adaptativa.

QUÉ DECIDE ESTA CORRIDA
-----------------------
No es un conteo más: es una calibración. Las 17 zonas con cifra publicada se reparten en familias
de método —relevamiento propio, mínimo relevado, directorio comercial y relevamiento anterior— y
cada una es un punto de comparación distinto. Lo que se mide es contra cuál de ellas se parece
Places.

QUÉ ES EL DENOMINADOR, Y POR QUÉ NO ES UN PATRÓN DE ORO
-------------------------------------------------------
Todo lo que sigue se divide por la **cifra publicada**, y esa cifra **no es una medición del
territorio**: es una consolidación de fuentes. `METODOLOGIA_REAL_DEL_ATLAS.md` §3 lo desglosa del
JSON canónico —R08 Villa Crespo son 646 = 178 de capas administrativas + 467 de Google Places, y
R10 Caballito 907 = 265 + 642—. **No hubo trabajo de campo en ninguna zona.**

Eso no invalida el eje: dividir todo por el mismo denominador sigue siendo la única forma de
comparar métodos entre sí. Lo que cambia es la conclusión que se puede sacar. Un método que
recupera el 36 % de la cifra publicada recupera el 36 % de **otra consolidación que ya era 70 %
Places**, no el 36 % de lo que hay en la calle. Y cuando el método que se mide es Places, la
comparación es en buena parte circular: es la misma fuente consultada con dos diseños distintos.

Places tiene que entrar en ese mismo eje: **Places ÷ cifra publicada**. La primera versión de este
informe encabezaba con **Places ÷ base** —que es otra cantidad, con otro denominador— y la comparaba
contra esas bandas. Que un número cayera adentro de la banda del otro era coincidencia aritmética,
no equivalencia. Con el denominador correcto, Belgrano es 29/697 = 4,2 % y no 29/100 = 29,0 %.

Por eso la tabla pone los tres métodos sobre el **mismo** denominador —padrón, Relevamiento de Usos
del Suelo y Places, todos divididos por la cifra publicada— y ésa es la única comparación que se lee
contra las bandas. Las columnas `pct_places_sobre_padron` y `pct_places_sobre_rus` se conservan
porque contestan otra pregunta —si Places ve locales que la fuente documental no tiene— y van
rotuladas como eso, nunca como factor de captura.

Un factor de captura no significa nada sin decir contra qué se calculó: es el par (método, base).

LA GRILLA ES ADAPTATIVA, Y ESE ES EL PUNTO
------------------------------------------
Ni 500 m en todos lados ni 1 km fijo. Se consulta a **1 km** y se vuelve a partir en **500 m**
cualquier celda que devuelva `UMBRAL_SATURACION` resultados o más.

El motivo de no bajar la grilla a ciegas: el techo de Text Search es 60 resultados por consulta, y
el universo esperado por celda sale de un factor de captura calibrado en otros barrios. Es la
estimación menos confiable que tenemos, justo en los barrios que menos conocemos. Si está corta por
dos, la celda satura y se pierden locales **sin que nada falle**. La regla adaptativa ahorra las
consultas cuando la estimación es buena y se corrige sola cuando no.

Cuántas celdas hubo que repartir se informa por separado: es información sobre dónde nuestro factor
de captura estimado se queda corto, y eso vale aparte del conteo.

GUARDARRAÍLES
-------------
- `--dry-run` es el modo por defecto. La ejecución real necesita `--run --confirm-real-api`.
- La API key se lee **sólo** de la variable de entorno `GOOGLE_MAPS_API_KEY`. No se pide por
  consola, no entra por argumento, no se imprime, no se guarda y no va a ningún log ni archivo de
  salida. **No hay que exportarla a mano:** vive en el `.env` del repositorio —ignorado por Git— y
  `cargar_dotenv()` la vuelca al entorno al arrancar, sin pisar lo que ya esté exportado. Si en
  una sesión limpia el script dice que falta la key, el problema es el `.env`, no la sesión.
- **Tope duro de requests.** Si el gasto se desvía más de `DESVIO_TOLERADO` del presupuesto
  autorizado, la corrida se detiene y avisa. No sigue "por poco".
- Los resultados con nombre, dirección y `place_id` quedan en carpeta interna ignorada por Git. Lo
  versionable son agregados por zona, vía `google_places_publicar_sanitizado.py`.
- Sólo API oficial. Nada de scraping.

USO
---
  # plan, sin gastar nada ni tocar la red:
  python scripts/barrido_ciudad/places_control_zonas.py

  # ejecución real (la key sale del `.env`; no hay que exportar nada):
  python scripts/barrido_ciudad/places_control_zonas.py --run --confirm-real-api
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import box

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_capa_homogenea import (  # noqa: E402
    CIFRAS_ATLAS,
    ENVOLVENTES,
    PRECEDENCIA_ENVOLVENTES,
)

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
GEN = BARRIDO / "generado"
CAPA_ZONAS = GEN / "capa_homogenea_22_zonas.csv"
CAPA_RUS = GEN / "capa_rus_22_zonas.csv"
# Carpeta interna: nombres, direcciones y place_id. Ignorada por Git.
INTERNO = ROOT / "outputs" / "analisis_interno" / "places_control_zonas_2026-08"

ENDPOINT = "https://places.googleapis.com/v1/places:searchText"

# CRS métrico de la Ciudad. Toda la geometría se hace acá y no en grados: en grados los tamaños
# de celda y las áreas salen mal, que es la trampa ya documentada del barrido.
CRS_METRICO = "EPSG:5347"
CRS_GEOGRAFICO = "EPSG:4326"

LADO_BASE_M = 1000.0       # la grilla arranca en 1 km
LADO_REFINO_M = 500.0      # y se parte en 500 m donde satura
UMBRAL_SATURACION = 50     # a partir de acá se sospecha que el techo de 60 recortó la celda
RESULTADOS_POR_PAGINA = 20
PAGINAS_MAXIMAS = 3        # el tope de Text Search: 3 páginas = 60 resultados
TECHO_API = RESULTADOS_POR_PAGINA * PAGINAS_MAXIMAS

PRESUPUESTO_AUTORIZADO = 301   # lo que autorizó Diego para el control de las 17 zonas
DESVIO_TOLERADO = 0.20         # si se pasa de esto, se corta y se avisa

PAUSA_S = 0.2

# La consulta genérica del anillo núcleo, una por celda. Pedir cada cocina nacional por separado
# multiplicaría el costo sin agregar cobertura: Places devuelve el tipo específico en `types`.
CONSULTA_GENERICA = "restaurantes bares y cafés"

# La consulta pide el NÚCLEO y nada más. Panaderías, pastelerías y bombonerías no se buscan, así
# que el anillo ampliado **no está medido** en esta corrida: su columna va vacía, no en cero. Un
# cero diría «no hay», y lo que pasa es que no se preguntó. Si algún día la consulta los incluye,
# se pone en True y la columna se llena sola.
CONSULTA_CUBRE_AMPLIADO = False

FIELDS = [
    "places.id", "places.displayName", "places.formattedAddress",
    "places.location", "places.businessStatus", "places.types",
    "nextPageToken",
]

# Anillos del universo gastronómico, según SPEC_PLACES_BARRIDO.md §1.
NUCLEO = {
    "restaurant", "bar", "cafe", "coffee_shop", "pizza_restaurant", "steak_house",
    "bar_and_grill", "barbecue_restaurant", "fast_food_restaurant", "meal_takeaway",
    "sandwich_shop", "hamburger_restaurant", "ice_cream_shop", "pub", "wine_bar",
    "cocktail_bar", "brewpub", "gastropub", "diner", "bistro", "cafeteria", "snack_bar",
    "food_court", "tea_house", "juice_shop",
}
AMPLIADO = {
    "bakery", "pastry_shop", "cake_shop", "confectionery", "dessert_shop", "donut_shop",
    "chocolate_shop", "candy_store",
}
EXCLUIDOS = {
    "meal_delivery", "pizza_delivery", "grocery_store", "supermarket", "food_store",
    "liquor_store", "winery", "brewery",
}


# --------------------------------------------------------------------------- geometría

def zonas_con_cifra() -> pd.DataFrame:
    """Las 17 zonas con cifra publicada, con su familia de método y sus dos bases."""
    cifras = pd.read_csv(CIFRAS_ATLAS).set_index("rid")
    capa = pd.read_csv(CAPA_ZONAS, index_col=0, encoding="utf-8")
    capa.index = [str(i).split(" · ")[0] for i in capa.index]
    rus = pd.read_csv(CAPA_RUS, index_col=0, encoding="utf-8")

    tabla = cifras[cifras.relevado.notna()].copy()
    tabla["dir_nucleo"] = capa.dir_nucleo
    # `rus_nucleo` son las parcelas del anillo núcleo del Relevamiento: la segunda base.
    tabla["parcelas_rus"] = rus.rus_nucleo
    tabla["cobertura_rus"] = rus.cobertura_rus
    tabla["hectareas"] = rus.hectareas
    return tabla


def perimetros() -> dict[str, object]:
    """Envolventes con la precedencia de solape ya aplicada, en CRS métrico.

    Es la misma regla que `build_capa_homogenea.py`: la superficie compartida queda para el
    `referencia_id` menor. Sin esto R12 y R18 se cuentan dos veces y el control mide mal.
    """
    envolventes = gpd.read_file(ENVOLVENTES)[["referencia_id", "nombre", "geometry"]]
    envolventes = envolventes.to_crs(CRS_METRICO).sort_values(PRECEDENCIA_ENVOLVENTES)
    envolventes = envolventes.reset_index(drop=True)

    resultado = {}
    for posicion, zona in envolventes.iterrows():
        perimetro = zona.geometry
        for previa in envolventes.iloc[:posicion].itertuples():
            if perimetro.intersects(previa.geometry):
                perimetro = perimetro.difference(previa.geometry)
        resultado[zona.referencia_id] = perimetro
    return resultado


def celdas_de(perimetro, lado: float, prefijo: str) -> list[dict]:
    """Cuadrícula de `lado` metros sobre un perímetro. Sólo las celdas que lo tocan."""
    minx, miny, maxx, maxy = perimetro.bounds
    celdas, fila = [], 0
    y = miny
    while y < maxy:
        columna, x = 0, minx
        while x < maxx:
            cuadro = box(x, y, x + lado, y + lado)
            if cuadro.intersects(perimetro):
                celdas.append({"celda_id": f"{prefijo}_{fila:02d}{columna:02d}",
                               "lado_m": lado, "geometry": cuadro})
            columna, x = columna + 1, x + lado
        fila, y = fila + 1, y + lado
    return celdas


def a_rectangulo(geometria) -> dict:
    """La celda en grados, como `locationRestriction.rectangle` de Places."""
    serie = gpd.GeoSeries([geometria], crs=CRS_METRICO).to_crs(CRS_GEOGRAFICO)
    minx, miny, maxx, maxy = serie.iloc[0].bounds
    return {"rectangle": {"low": {"latitude": miny, "longitude": minx},
                          "high": {"latitude": maxy, "longitude": maxx}}}


def plan_base() -> pd.DataFrame:
    """El plan de la grilla de 1 km sobre las 17 zonas. Sin refinamientos: esos se deciden solos."""
    zonas, formas = zonas_con_cifra(), perimetros()
    filas = []
    for rid in zonas.index:
        if rid not in formas or formas[rid].is_empty:
            continue
        for celda in celdas_de(formas[rid], LADO_BASE_M, rid):
            filas.append({"rid": rid, "zona": zonas.zona_publicada[rid],
                          "metodo": zonas.metodo[rid], **celda})
    return gpd.GeoDataFrame(filas, geometry="geometry", crs=CRS_METRICO)


# --------------------------------------------------------------------------- API

def cargar_dotenv(ruta: Path | None = None) -> None:
    """Vuelca `.env` al entorno del proceso **sin pisar lo que ya esté exportado**.

    La key vive en `.env`, que está ignorado por Git. Ningún script la cargaba al entorno, así
    que en una sesión limpia de PowerShell la variable no existía y la corrida abortaba por falta
    de key teniendo la key ahí: abortaba bien, pero por el motivo equivocado.

    Tres condiciones, y las tres importan:

    - **la sesión gana.** Si `GOOGLE_MAPS_API_KEY` ya viene exportada con un valor real, `.env`
      no la pisa. Sólo se completa lo que está ausente o vacío;
    - **sin dependencia nueva.** `python-dotenv` metería un `pip install` en el arranque y este
      entorno corre sin red. Partir en el primer `=` y sacar comillas alcanza;
    - **si `.env` no está, no falla.** Sigue de largo y el abort de siempre hace su trabajo.

    El guardarraíl no se toca: la key se sigue leyendo sólo del entorno, no entra por argumento
    de línea de comandos, no se imprime y no se escribe a disco.
    """
    ruta = ruta or ROOT / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        nombre, _, valor = linea.removeprefix("export ").partition("=")
        nombre = nombre.strip()
        if not os.environ.get(nombre, "").strip():
            os.environ[nombre] = valor.strip().strip("\"'")


def leer_api_key() -> str | None:
    """Sólo del entorno, que `cargar_dotenv()` ya completó desde `.env` si hacía falta.

    Nunca se pide por consola ni se escribe a disco.
    """
    clave = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    return clave or None


def consultar_celda(clave: str, rectangulo: dict,
                    consulta: str = CONSULTA_GENERICA) -> tuple[list[dict], int, str | None]:
    """Text Search paginado sobre una celda. Devuelve (lugares, requests_gastados, error).

    Cada página es un request y se cobra como tal: por eso se cuentan páginas, no celdas.

    `consulta` tiene default para que el control de las 17 zonas siga siendo exactamente el mismo
    llamado que se corrió el 2026-08-05 —su reproducibilidad no depende de que el que la llame
    pase el texto—. El parámetro existe para `places_techo_zona.py`, que necesita varias familias
    de consulta sobre la misma celda.
    """
    import requests  # import diferido: el dry-run no necesita la librería

    encabezados = {"Content-Type": "application/json", "X-Goog-Api-Key": clave,
                   "X-Goog-FieldMask": ",".join(FIELDS)}
    cuerpo = {"textQuery": consulta, "languageCode": "es", "regionCode": "AR",
              "pageSize": RESULTADOS_POR_PAGINA, "locationRestriction": rectangulo}

    lugares, gastados, token = [], 0, None
    for _ in range(PAGINAS_MAXIMAS):
        if token:
            cuerpo["pageToken"] = token
        try:
            respuesta = requests.post(ENDPOINT, headers=encabezados, json=cuerpo, timeout=30)
        except Exception as exc:  # noqa: BLE001
            return lugares, gastados, f"excepción de red: {type(exc).__name__}"
        gastados += 1
        if respuesta.status_code != 200:
            # No se vuelca el cuerpo crudo: puede traer el eco de la request, y ahí va la key.
            try:
                mensaje = respuesta.json().get("error", {}).get("message", "")
            except Exception:  # noqa: BLE001
                mensaje = ""
            return lugares, gastados, f"HTTP {respuesta.status_code}: {mensaje[:200]}"
        datos = respuesta.json()
        lugares.extend(datos.get("places", []))
        token = datos.get("nextPageToken")
        if not token:
            break
        time.sleep(PAUSA_S)
    return lugares, gastados, None


def anillo(tipos: list[str]) -> str | None:
    """Núcleo, ampliado o fuera del universo. Los excluidos ganan sobre todo lo demás."""
    conjunto = set(tipos or [])
    if conjunto & EXCLUIDOS:
        return None
    if conjunto & NUCLEO:
        return "nucleo"
    if conjunto & AMPLIADO:
        return "ampliado"
    return None


# --------------------------------------------------------------------------- corrida

def estimar_requests(plan: gpd.GeoDataFrame) -> int:
    """Cota del plan base: una página por celda, más las que el refinamiento pueda agregar.

    No se puede saber de antemano cuántas celdas van a saturar —ese es justamente el punto de la
    grilla adaptativa—, así que el plan informa el piso (una página por celda) y el techo.
    """
    return len(plan)


def correr(plan: gpd.GeoDataFrame, clave: str, presupuesto: int) -> dict:
    """La corrida real, con refinamiento adaptativo y tope duro de gasto."""
    tope = int(presupuesto * (1 + DESVIO_TOLERADO))
    gastados = 0
    vistos: set[str] = set()
    puntos: list[dict] = []
    bitacora: list[dict] = []
    refinadas: list[str] = []
    saturadas_pese_al_refino: list[str] = []
    errores: list[str] = []
    hoy = dt.date.today().isoformat()

    pendientes = [dict(fila) for fila in plan.to_dict("records")]
    while pendientes:
        celda = pendientes.pop(0)
        if gastados >= tope:
            errores.append(f"TOPE DE GASTO alcanzado ({gastados}/{tope}); "
                           f"quedaron {len(pendientes) + 1} celdas sin consultar")
            break

        lugares, costo, error = consultar_celda(clave, a_rectangulo(celda["geometry"]))
        gastados += costo
        if error:
            errores.append(f"{celda['celda_id']}: {error}")

        nuevos = 0
        for lugar in lugares:
            pid = lugar.get("id", "")
            capa = anillo(lugar.get("types"))
            if not pid or capa is None or pid in vistos:
                continue
            vistos.add(pid)
            nuevos += 1
            ubicacion = lugar.get("location") or {}
            puntos.append({
                "place_id": pid,
                "nombre": (lugar.get("displayName") or {}).get("text", ""),
                "direccion": lugar.get("formattedAddress", ""),
                "lat": ubicacion.get("latitude", ""),
                "lon": ubicacion.get("longitude", ""),
                "business_status": lugar.get("businessStatus", ""),
                "types": ";".join(lugar.get("types") or []),
                "anillo": capa,
                "rid": celda["rid"], "celda_id": celda["celda_id"],
                "lado_m": celda["lado_m"], "fecha_consulta": hoy,
            })

        saturada = len(lugares) >= UMBRAL_SATURACION
        bitacora.append({"celda_id": celda["celda_id"], "rid": celda["rid"],
                         "lado_m": celda["lado_m"], "devueltos": len(lugares),
                         "nuevos": nuevos, "requests": costo,
                         "saturada": saturada, "error": error or ""})

        # LA REGLA ADAPTATIVA. Sólo un nivel: 1 km -> 500 m, como se decidió.
        # Las hijas van al FINAL de la cola, no al principio: así se completan primero las 95
        # celdas base de las 17 zonas y, si el tope de gasto corta, lo que se pierde son
        # refinamientos y no zonas enteras sin consultar.
        # NO CAMBIAR A `pendientes.insert(0, ...)` NI A UNA COLA POR PRIORIDAD. Refinar en
        # profundidad parece más prolijo y da mejor detalle en las primeras zonas, pero convierte
        # un corte por presupuesto en zonas enteras sin medir, y una zona sin medir no se puede
        # distinguir de una zona sin locales. Es una decisión de cobertura, no de eficiencia.
        if saturada and celda["lado_m"] > LADO_REFINO_M:
            refinadas.append({"celda_id": celda["celda_id"], "rid": celda["rid"],
                              "zona": celda["zona"], "devueltos": len(lugares)})
            for hija in celdas_de(celda["geometry"], LADO_REFINO_M, celda["celda_id"] + "R"):
                pendientes.append({"rid": celda["rid"], "zona": celda["zona"],
                                   "metodo": celda["metodo"], **hija})
        elif saturada:
            # Ya está en 500 m y sigue saturando: la zona queda subcontada y hay que decirlo.
            saturadas_pese_al_refino.append({"celda_id": celda["celda_id"], "rid": celda["rid"],
                                             "zona": celda["zona"], "devueltos": len(lugares)})

    return {"gastados": gastados, "puntos": puntos, "bitacora": bitacora,
            "refinadas": refinadas, "saturadas_pese_al_refino": saturadas_pese_al_refino,
            "errores": errores, "tope": tope}


# --------------------------------------------------------------------------- informe

def mostrar_plan(plan: gpd.GeoDataFrame, zonas: pd.DataFrame, presupuesto: int) -> None:
    piso = estimar_requests(plan)
    print("=" * 78)
    print("  CONTROL DE PLACES · 17 ZONAS CON CIFRA PUBLICADA · GRILLA ADAPTATIVA")
    print("=" * 78)
    print(f"  endpoint            : {ENDPOINT}")
    print(f"  consulta por celda  : «{CONSULTA_GENERICA}» + locationRestriction rectángulo")
    print(f"  grilla base         : {LADO_BASE_M:.0f} m · refino a {LADO_REFINO_M:.0f} m "
          f"si una celda devuelve >= {UMBRAL_SATURACION}")
    print(f"  paginación          : hasta {PAGINAS_MAXIMAS} páginas por celda "
          f"({TECHO_API} resultados), y cada página es un request")
    print(f"  presupuesto         : {presupuesto} requests autorizados · "
          f"corta en {int(presupuesto * (1 + DESVIO_TOLERADO))} (+{DESVIO_TOLERADO:.0%})")
    print(f"  salida interna      : {INTERNO.relative_to(ROOT)}  (fuera de Git)")
    print("  API key             : $GOOGLE_MAPS_API_KEY, completada desde .env · no se imprime ni se guarda")
    print("=" * 78)
    print("")

    resumen = plan.groupby(["rid", "zona", "metodo"]).size().rename("celdas_1km").reset_index()
    resumen["relevado"] = resumen.rid.map(zonas.relevado).astype(int)
    resumen["habilitaciones_dir_nucleo"] = resumen.rid.map(zonas.dir_nucleo)
    resumen["parcelas_rus"] = resumen.rid.map(zonas.parcelas_rus)
    print(resumen.to_string(index=False))
    print("")
    print(f"  celdas de 1 km            : {len(plan)}")
    print(f"  requests si nada satura   : {piso}  (una página por celda)")
    print(f"  cota si todas paginaran   : {piso * PAGINAS_MAXIMAS}")
    print(f"  presupuesto autorizado    : {presupuesto}")
    print("")
    print("  El refinamiento no se puede presupuestar de antemano: se dispara con lo que")
    print("  devuelve la API, que es justamente lo que no sabemos. Cada celda que satura suma")
    print("  4 celdas de 500 m. El tope duro protege el presupuesto.")


def asignar_por_geometria(puntos: pd.DataFrame) -> pd.DataFrame:
    """Reasigna cada punto a la envolvente que **lo contiene**, no a la celda que lo trajo.

    La celda es un cuadrado de 1 km que se conserva si *toca* la envolvente, y a la API se le pide
    el rectángulo entero. Para una zona angosta —un bulevar, una avenida por tramos— el rectángulo
    cubre muchísimo más territorio que la envolvente, y Places devuelve todo lo que hay adentro.
    Atribuir esos puntos a la zona por la celda que los trajo infla el conteo con locales que
    están afuera: es lo que hacía que una zona diera «captura» por encima del 100 %.

    Se resuelve con punto en polígono contra los mismos perímetros con precedencia de solape que
    usa la grilla, así que ningún punto se cuenta dos veces. Lo que cae fuera de toda envolvente
    no se pierde —queda en el archivo interno— pero no suma a ninguna zona.
    """
    if not len(puntos):
        return puntos.assign(rid_geo=None)
    formas = perimetros()
    geo = gpd.GeoDataFrame(
        puntos.copy(),
        geometry=gpd.points_from_xy(pd.to_numeric(puntos.lon, errors="coerce"),
                                    pd.to_numeric(puntos.lat, errors="coerce")),
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO)

    envolventes = gpd.GeoDataFrame(
        {"rid_geo": list(formas)}, geometry=list(formas.values()), crs=CRS_METRICO)
    unido = gpd.sjoin(geo, envolventes, how="left", predicate="within")
    # Un punto no puede caer en dos envolventes: la precedencia ya las hizo disjuntas. Si el
    # sjoin devolviera duplicados igual, nos quedamos con el primero y no inventamos un conteo.
    return unido[~unido.index.duplicated(keep="first")]


def informar(resultado: dict, zonas: pd.DataFrame, presupuesto: int) -> pd.DataFrame:
    """El control: los tres métodos sobre la cifra publicada, más las dos razones invertidas.

    Las columnas están agrupadas a propósito y el orden importa:

    1. `pct_*_sobre_publicada` — **el eje comparable**. Padrón, Relevamiento y Places divididos por
       el mismo denominador, la cifra publicada. Es lo único que se lee contra las bandas de
       `factor_captura_22_zonas.csv`, porque esas bandas son exactamente `base ÷ publicada`.
    2. `pct_places_sobre_*` — **otra pregunta**. Cuánto del padrón (o del Relevamiento) alcanza a
       ver Places. Sirve para saber si Places aporta locales que la fuente documental no tiene, y
       es la razón inversa de la anterior: no se compara contra las bandas ni se llama captura.

    Mezclarlas fue el error de la primera versión: `Places ÷ base` daba 29,6 % de mediana y caía
    adentro de la banda 7,6-36,1 % de `base ÷ publicada`. Números parecidos, cantidades distintas.
    """
    puntos = asignar_por_geometria(pd.DataFrame(resultado["puntos"]))
    # Cuántas celdas hubo que repartir en cada zona. Va en columna aparte, nunca mezclado con el
    # factor de captura: dice dónde la estimación previa se quedó corta, que es otra pregunta.
    repartidas = pd.DataFrame(resultado["refinadas"]).rid.value_counts() \
        if resultado["refinadas"] else pd.Series(dtype=int)
    # Zonas donde alguna celda sigue saturando a 500 m: ahí Places devolvió su techo y el conteo
    # es una COTA INFERIOR, no una medición. El factor de esas zonas se lee «al menos», nunca «=».
    subcontadas = {c["rid"] for c in resultado["saturadas_pese_al_refino"]}
    filas = []
    for rid in zonas.index:
        # `rid_geo`, no `rid`: la envolvente que contiene el punto, no la celda que lo trajo.
        de_zona = puntos[puntos.rid_geo == rid] if len(puntos) else puntos
        nucleo = int((de_zona.anillo == "nucleo").sum()) if len(de_zona) else 0
        relevado = float(zonas.relevado[rid])
        habilitaciones = zonas.dir_nucleo.get(rid)
        parcelas = zonas.parcelas_rus.get(rid)
        hay_rus = bool(parcelas) and zonas.cobertura_rus.get(rid) == "si"

        def sobre_publicada(valor) -> float | None:
            """El eje comparable: cualquier método dividido por la cifra publicada."""
            return round(100 * valor / relevado, 1) if relevado and valor is not None else None

        # La razón inversa. Se conserva, pero no es un factor de captura y no se compara contra
        # las bandas: dice qué proporción de la fuente documental alcanza a ver Places.
        places_sobre_padron = round(100 * nucleo / habilitaciones, 1) if habilitaciones else None
        places_sobre_rus = round(100 * nucleo / parcelas, 1) if hay_rus else None

        # Las advertencias que tienen que viajar pegadas al número, no en una nota al pie.
        avisos = []
        if rid in subcontadas:
            avisos.append("cota inferior: satura a 500 m")
        if (places_sobre_padron or 0) > 100 or (places_sobre_rus or 0) > 100:
            # Sólo afecta a las columnas invertidas, y sólo dice que la base documental es más
            # chica que lo que Places encontró. No toca el eje comparable, cuyo denominador es la
            # cifra publicada: R07 y R11 siguen contando ahí con normalidad.
            avisos.append("Places > base documental (base chica): la razón invertida no se lee")

        filas.append({
            "rid": rid, "zona": zonas.zona_publicada[rid], "metodo": zonas.metodo[rid],
            "cifra_publicada": int(relevado),
            # --- eje comparable: los tres métodos sobre el MISMO denominador ---
            "padron_nucleo": habilitaciones,
            "pct_padron_sobre_publicada": sobre_publicada(habilitaciones),
            # R07 · Costanera Norte tiene 1 parcela relevada en 38,5 ha: su cero no es un cero, es
            # falta de cobertura de la fuente. Va vacío en vez de arrastrar un 0 % que no midió nada.
            "rus_nucleo": parcelas if hay_rus else None,
            "pct_rus_sobre_publicada": sobre_publicada(parcelas) if hay_rus else None,
            "places_nucleo": nucleo,
            "pct_places_sobre_publicada": sobre_publicada(nucleo),
            # --- razón invertida: otra pregunta, rotulada como tal ---
            "pct_places_sobre_padron": places_sobre_padron,
            "pct_places_sobre_rus": places_sobre_rus,
            # --- resto ---
            # Vacío, no cero: la consulta no pide panaderías ni pastelerías. Ver CONSULTA_CUBRE_AMPLIADO.
            "places_ampliado": (int((de_zona.anillo == "ampliado").sum()) if len(de_zona) else 0)
                               if CONSULTA_CUBRE_AMPLIADO else None,
            "cobertura_relevamiento": zonas.cobertura_rus.get(rid),
            "celdas_repartidas_500m": int(repartidas.get(rid, 0)),
            "advertencia": " · ".join(avisos),
        })
    return pd.DataFrame(filas)


def leer_comparacion(control: pd.DataFrame) -> str:
    """Redacta la lectura del control **desde los números**, no desde una conclusión escrita a mano.

    Se genera acá y no en un informe aparte por el motivo de siempre: si la próxima corrida mueve
    los números, la lectura se mueve con ellos. Una conclusión narrada a mano sobrevive a los datos
    que la desmienten, y eso fue exactamente lo que pasó con la primera versión de este control.

    Las bandas salen de las familias de método presentes en la tabla, no de constantes escritas
    acá: si mañana cambia la clasificación de una zona, la banda se recalcula sola.
    """
    lineas: list[str] = []
    eje = control[control.pct_places_sobre_publicada.notna()]

    def franja(serie: pd.Series) -> str:
        limpia = serie.dropna()
        if limpia.empty:
            return "sin cobertura"
        return (f"{limpia.min():6.1f} – {limpia.max():6.1f} %   "
                f"mediana {limpia.median():6.1f}   n={len(limpia)}")

    # ESTRATIFICADO POR FAMILIA, y no en un solo promedio, porque el denominador cambia de
    # naturaleza entre familias: la cifra publicada es un conteo de campo en unas zonas y un
    # directorio comercial en otras. Un 20 % contra el campo y un 20 % contra un directorio no
    # dicen lo mismo, y mezclarlos vuelve a producir una banda sin significado.
    #
    # El orden es de mayor a menor fuerza de la cifra publicada, no alfabético: arriba queda la
    # familia donde el denominador es un conteo de campo real, que es la que decide.
    orden = ["relevamiento propio", "minimo relevado", "relevamiento anterior",
             "directorio comercial"]
    lineas.append("  CUÁNTO RECUPERA CADA MÉTODO DE LA CIFRA PUBLICADA (mismo denominador)")
    lineas.append("")
    familias = {f: g for f, g in eje.groupby("metodo")}
    for familia in orden + [f for f in familias if f not in orden]:
        grupo = familias.get(familia)
        if grupo is None:
            continue
        lineas.append(f"    cifra publicada por {familia.upper()}")
        for etiqueta, columna in (("padrón de habilitaciones", "pct_padron_sobre_publicada"),
                                  ("Relevamiento de Usos", "pct_rus_sobre_publicada"),
                                  ("Google Places", "pct_places_sobre_publicada")):
            lineas.append(f"      {etiqueta:<26}: {franja(grupo[columna])}")
        lineas.append("")
    lineas.append("    La cifra publicada es el 100 % por construcción: es el patrón contra el que")
    lineas.append("    se mide, no una columna más.")

    # La familia de denominador más grande. NO es un conteo de campo: es la consolidación de dos
    # fuentes —capas administrativas + Places— y el 70 % de su volumen lo puso Places. Por eso la
    # comparación de abajo es en parte circular y se declara como tal en vez de leerse como
    # cobertura del territorio.
    propio = eje[eje.metodo == "relevamiento propio"]
    if len(propio):
        campo_places = propio.pct_places_sobre_publicada.dropna()
        campo_padron = propio.pct_padron_sobre_publicada.dropna()
        lineas.append("")
        lineas.append("  CONTRA LA CIFRA MÁS CONSOLIDADA · las 4 zonas de relevamiento propio")
        lineas.append("")
        lineas.append("    El denominador acá es capas administrativas + Places (72 % Places en")
        lineas.append("    R08, 71 % en R10). No es un conteo de campo: no hubo campo.")
        lineas.append("")
        lineas.append(f"    Esta barrida de Places recupera el {campo_places.median():.1f} % de esa "
                      f"cifra (rango {campo_places.min():.1f} – {campo_places.max():.1f} %);")
        lineas.append(f"    el padrón de habilitaciones, solo, recupera el "
                      f"{campo_padron.median():.1f} %.")
        veces = campo_padron.median() / campo_places.median() if campo_places.median() else 0
        if veces:
            lineas.append(f"    O sea: esta barrida encuentra del orden de {1 / veces:.1f} veces lo "
                          f"que ya encuentra el padrón.")
        lineas.append("")
        lineas.append("    Y lo que mide no es cobertura del territorio, sino DISEÑO DE CONSULTA:")
        lineas.append("    el 70 % del denominador salió de Places, así que esto compara nuestra")
        lineas.append("    consulta de agosto contra la consulta de julio, no una fuente contra")
        lineas.append("    otra. Ese es todo el alcance del número.")

    # Comparación pareada: la misma zona, el mismo denominador. Es más fuerte que comparar
    # medianas de conjuntos distintos, porque no depende de qué zonas entraron en cada familia.
    pareadas = eje[eje.pct_padron_sobre_publicada.notna()]
    gana_places = int((pareadas.pct_places_sobre_publicada
                       > pareadas.pct_padron_sobre_publicada).sum())
    lineas.append("")
    lineas.append(f"  Comparación pareada (misma zona, mismo denominador): Places supera al padrón "
                  f"en {gana_places} de {len(pareadas)} zonas")
    if gana_places:
        cuales = pareadas[pareadas.pct_places_sobre_publicada
                          > pareadas.pct_padron_sobre_publicada]
        detalle = ", ".join(f"{f.rid} ({f.pct_places_sobre_publicada:.1f} % contra "
                            f"{f.pct_padron_sobre_publicada:.1f} %)" for f in cuales.itertuples())
        lineas.append(f"    y son {detalle} — las dos de padrón más chico de la tabla.")
    return "\n".join(lineas)


def resultado_guardado(zonas: pd.DataFrame) -> dict:
    """Reconstruye el resultado de la última corrida desde los archivos internos.

    Sirve para rehacer el informe cuando cambia cómo se presenta —una columna que tenía que ir
    vacía, una advertencia que faltaba— **sin volver a gastar un solo request**. Los puntos y la
    bitácora ya están en disco; lo único que se recalcula es la presentación.
    """
    puntos = pd.read_csv(INTERNO / "places_puntos_interno.csv", encoding="utf-8-sig")
    bitacora = pd.read_csv(INTERNO / "places_bitacora_celdas.csv", encoding="utf-8")
    saturadas = bitacora[bitacora.saturada]

    def a_dicts(marco: pd.DataFrame) -> list[dict]:
        return [{"celda_id": f.celda_id, "rid": f.rid,
                 "zona": zonas.zona_publicada.get(f.rid, f.rid), "devueltos": int(f.devueltos)}
                for f in marco.itertuples()]
    return {
        "gastados": int(bitacora.requests.sum()),
        "puntos": puntos.to_dict("records"),
        "bitacora": bitacora.to_dict("records"),
        "refinadas": a_dicts(saturadas[saturadas.lado_m > LADO_REFINO_M]),
        "saturadas_pese_al_refino": a_dicts(saturadas[saturadas.lado_m <= LADO_REFINO_M]),
        "errores": [], "tope": 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Control de Places sobre las 17 zonas con cifra.")
    ap.add_argument("--reinformar", action="store_true",
                    help="Rehace el informe desde los datos ya guardados. No toca la red.")
    ap.add_argument("--run", action="store_true", help="Ejecuta de verdad. Sin esto: dry-run.")
    ap.add_argument("--confirm-real-api", action="store_true",
                    help="Segunda confirmación, obligatoria junto con --run.")
    ap.add_argument("--presupuesto", type=int, default=PRESUPUESTO_AUTORIZADO,
                    help=f"Requests autorizados (default {PRESUPUESTO_AUTORIZADO}).")
    args = ap.parse_args()

    cargar_dotenv()
    zonas = zonas_con_cifra()
    plan = plan_base()
    mostrar_plan(plan, zonas, args.presupuesto)

    GEN.mkdir(parents=True, exist_ok=True)
    plan.drop(columns="geometry").to_csv(GEN / "plan_places_control_17_zonas.csv",
                                         index=False, encoding="utf-8")

    if args.reinformar:
        # Rehace la presentación con lo que ya está en disco. Cero requests.
        resultado = resultado_guardado(zonas)
        print("\nREINFORMAR: se rehace el informe desde los datos guardados. "
              "No se tocó la red, no se gastó un solo request.\n")
        publicar(resultado, zonas, plan, args.presupuesto)
        return 0

    if not args.run:
        # Se informa si la key está disponible, sin revelarla: así se sabe que la corrida real va
        # a arrancar, sin gastar un request para averiguarlo.
        clave = leer_api_key()
        print("")
        if clave:
            print(f"  GOOGLE_MAPS_API_KEY: disponible (no se imprime; longitud={len(clave)})")
        else:
            print("  GOOGLE_MAPS_API_KEY: NO disponible — ni en el entorno ni en .env")
        print("")
        print("DRY-RUN: no se tocó la red, no se gastó un solo request.")
        print("Para ejecutar: --run --confirm-real-api.")
        return 0
    if not args.confirm_real_api:
        print("\nABORTADO: --run necesita también --confirm-real-api.")
        return 2

    clave = leer_api_key()
    if clave is None:
        print("\nABORTADO: falta GOOGLE_MAPS_API_KEY en el entorno. No se ejecutó nada.")
        print("La pone Diego en su sesión; este script no la pide ni la manipula.")
        return 2

    print(f"\nGOOGLE_MAPS_API_KEY detectada (no se imprime; longitud={len(clave)}).")
    print(f"Ejecutando · presupuesto {args.presupuesto} · tope duro "
          f"{int(args.presupuesto * (1 + DESVIO_TOLERADO))}\n")
    resultado = correr(plan, clave, args.presupuesto)

    INTERNO.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(resultado["puntos"]).to_csv(
        INTERNO / "places_puntos_interno.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(resultado["bitacora"]).to_csv(
        INTERNO / "places_bitacora_celdas.csv", index=False, encoding="utf-8")

    publicar(resultado, zonas, plan, args.presupuesto)
    return 0


def publicar(resultado: dict, zonas: pd.DataFrame, plan: gpd.GeoDataFrame,
             presupuesto: int) -> None:
    """Escribe el CSV publicable y el resumen, y los imprime. No toca la red."""
    control = informar(resultado, zonas, presupuesto)
    control.to_csv(GEN / "places_control_17_zonas.csv", index=False, encoding="utf-8")

    gastados = resultado["gastados"]
    desvio = (gastados - presupuesto) / presupuesto
    resumen = {
        "fecha": dt.date.today().isoformat(),
        "requests_gastados": gastados,
        "requests_presupuestados": presupuesto,
        "desvio_pct": round(100 * desvio, 1),
        "celdas_base_1km": len(plan),
        "celdas_refinadas_a_500m": len(resultado["refinadas"]),
        "zonas_con_refinamiento": sorted({c["rid"] for c in resultado["refinadas"]}),
        "celdas_saturadas_pese_al_refino": len(resultado["saturadas_pese_al_refino"]),
        "zonas_subcontadas": sorted({c["rid"] for c in resultado["saturadas_pese_al_refino"]}),
        "puntos_unicos": len(resultado["puntos"]),
        "errores": len(resultado["errores"]),
    }
    (GEN / "places_control_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 78)
    print("  RESULTADO DEL CONTROL")
    print("=" * 78)
    print(control.to_string(index=False))
    print("")
    print(f"  requests gastados: {gastados} contra {presupuesto} estimados "
          f"({100 * desvio:+.1f} %)")
    if abs(desvio) > DESVIO_TOLERADO:
        print(f"  *** DESVÍO MAYOR AL {DESVIO_TOLERADO:.0%} — la corrida se detuvo. "
              "Revisar antes de seguir. ***")
    print(f"  celdas de 1 km consultadas: {len(plan)}")
    print(f"  celdas que hubo que repartir en 500 m: {len(resultado['refinadas'])}")
    if resultado["refinadas"]:
        # Por zona, no sólo por celda_id: dónde se repartió es información sobre dónde nuestro
        # factor de captura estimado se queda corto, y eso se lee por territorio.
        for rid, grupo in pd.DataFrame(resultado["refinadas"]).groupby("rid"):
            print(f"    {rid} · {grupo.zona.iloc[0]}: {len(grupo)} celda(s) — "
                  f"{', '.join(grupo.celda_id)}")
        print("    Ahí la estimación previa se quedó corta. Vale por separado del factor.")
    if resultado["saturadas_pese_al_refino"]:
        quedan = pd.DataFrame(resultado["saturadas_pese_al_refino"])
        print(f"  *** {len(quedan)} celdas siguen saturadas a 500 m: esas zonas quedan "
              "SUBCONTADAS ***")
        for rid, grupo in quedan.groupby("rid"):
            print(f"    {rid} · {grupo.zona.iloc[0]}: {', '.join(grupo.celda_id)}")
    for error in resultado["errores"]:
        print(f"  error: {error}")
    ubicados = asignar_por_geometria(pd.DataFrame(resultado["puntos"]))
    if len(ubicados):
        adentro = int(ubicados.rid_geo.notna().sum())
        print("")
        print(f"  puntos devueltos por la API: {len(ubicados)}")
        print(f"  dentro de alguna envolvente: {adentro} "
              f"({100 * adentro / len(ubicados):.1f} %) — son los que cuentan")
        print(f"  fuera de toda envolvente   : {len(ubicados) - adentro} — la celda de 1 km cubre "
              "más territorio")
        print("    que la zona; se consultan por la grilla y se descartan por geometría. Quedan")
        print("    en el archivo interno, no suman a ninguna zona.")

    if not CONSULTA_CUBRE_AMPLIADO:
        print("")
        print("  `places_ampliado` va VACÍO, no en cero: la consulta pide restaurantes, bares y")
        print("  cafés, y nunca busca panaderías ni pastelerías. El anillo ampliado no se midió")
        print("  en esta corrida, así que no se compara contra la base ampliada.")

    print("")
    print("=" * 78)
    print("  LECTURA DEL CONTROL")
    print("=" * 78)
    print(leer_comparacion(control))

    # La salvedad que impide leer esto como el techo de Places. Va acá, pegada a la lectura, y no
    # en una nota al pie: son dos causas que producen el mismo número y esta corrida no las separa.
    print("")
    print("  QUÉ MIDE ESTO, Y QUÉ NO")
    print("")
    print("  Lo medido es el techo de ESTA barrida, no el techo de Places. Dos motivos, los dos")
    print("  reconocidos por la propia corrida:")
    print("")
    if resultado["saturadas_pese_al_refino"]:
        zonas_cota = sorted({c["rid"] for c in resultado["saturadas_pese_al_refino"]})
        print(f"    - saturación admitida: {', '.join(zonas_cota)} conservan alguna celda en su")
        print(f"      techo aún a {LADO_REFINO_M:.0f} m, y el refinamiento se cortó en un nivel;")
    print(f"    - una sola familia de consulta («{CONSULTA_GENERICA}»), cuando la especificación")
    print("      preveía hasta tres por celda.")
    print("")
    print("  «Places encuentra poco» y «nuestra consulta buscó poco» dan el mismo resultado, y")
    print("  esta corrida no los distingue. Los porcentajes de arriba son COTAS INFERIORES de lo")
    print("  que Places puede devolver. La prueba de techo sobre una zona sola —varias familias,")
    print("  refinamiento sin tope, paginación completa— es la que separa las dos causas.")
    print("")
    print(f"  interno (fuera de Git): {INTERNO}")
    print(f"  publicable: {GEN / 'places_control_17_zonas.csv'}")


if __name__ == "__main__":
    sys.exit(main())
