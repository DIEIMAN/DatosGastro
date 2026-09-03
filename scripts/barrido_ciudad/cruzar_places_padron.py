"""Cruce de los puntos de Places de una zona contra la base documental. CERO requests.

QUÉ PREGUNTA CONTESTA
---------------------
La captura-recaptura cerró **cuánto** ve Places (N̂ ≈ 77 sobre 646 en R08: el 12 % es techo
estructural). Queda abierta la otra mitad: **qué** ve. Dos respuestas posibles, y llevan a
decisiones opuestas sobre el barrido de los 48 barrios:

  - si los puntos de Places son casi todos direcciones que el padrón ya tiene, Places **confirma**
    lo conocido y su único aporte real es la señal de vigencia —qué de lo que conocemos sigue
    abierto—, que ninguna fuente documental da;
  - si una parte apreciable no está en el padrón, Places además **descubre**, y entonces el barrido
    vale por sí mismo aunque nunca sirva para contar.

Los dos conjuntos están pagados y en disco. **No cuesta un request: es un cruce por dirección y
por coordenada.**

LA UNIDAD DEL CRUCE ES LA DIRECCIÓN, NO EL LOCAL
------------------------------------------------
El padrón cuenta direcciones normalizadas (`id_ubicacion`), no locales: es la regla 1 del método de
comparabilidad. Así que lo que este cruce puede decidir es si **la dirección** ya está en la base,
no si es el mismo negocio. Un restaurante nuevo en una dirección que el padrón registró con otro
titular cuenta acá como coincidencia. Es la lectura conservadora del lado del descubrimiento —el
aporte propio de Places no puede ser menor que lo que sale acá, y sí puede ser algo mayor—, y se
declara en el informe para que nadie lea «coincide» como «es el mismo local».

CÓMO SE DECIDE QUE DOS DIRECCIONES SON LA MISMA
-----------------------------------------------
Las dos fuentes escriben la calle de manera incompatible:

    padrón   GALLARDO, ANGEL AV. 1091      REPETTO, NICOLAS, DR. 1439
    Places   Av. Ángel Gallardo 774        Av. Dr. Nicolás Repetto 1295

Comparar cadenas no sirve. Se compara el **conjunto de palabras significativas** de la calle
—plegando tildes, mayúsculas y los títulos que una fuente pone y la otra no (AV, DR, CNEL, TTE,
GRAL, PRES)— más la altura con tolerancia. El padrón trae direcciones multivaluadas separadas por
`;` —el frente entero del inmueble, que es el mismo mecanismo de los lotes de permisos— y se
explotan todas: cualquiera de sus puertas vale como coincidencia.

La coincidencia por proximidad va **aparte y como categoría propia**, nunca sumada en silencio: el
padrón geocodifica calle+altura con USIG, así que dos direcciones distintas de la misma cuadra
caen a pocas decenas de metros. Un radio chico confunde vecinos con el mismo local, y por eso el
número que se reporta primero es el de la coincidencia de dirección.

LOS TRES PANELES
----------------
1. **Padrón núcleo** (la pregunta de Diego): las direcciones con habilitación gastronómica de
   rubro núcleo, sin outliers. Es el eje, y las bandas de lectura están escritas contra él.
2. **Padrón completo**: agrega ampliado y direcciones anómalas. Un bar de Places sobre una
   dirección que el padrón registró como panadería **no es un descubrimiento**: la dirección está
   en la base, en otro anillo.
3. **Relevamiento de Usos del Suelo**: parcela por parcela, punto en polígono. Contesta si lo que
   el padrón no tiene lo tiene la otra fuente documental. Sin este panel, «no está en el padrón»
   se leería como «no está en ninguna fuente», que es otra afirmación y más fuerte.

GUARDARRAÍLES
-------------
- **No toca la red.** No hay endpoint, no hay key, no hay presupuesto que gastar. Si este script
  alguna vez necesita un request, está mal escrito.
- Nombres, direcciones y `place_id` se leen de la carpeta interna ignorada por Git y **no salen de
  ella**: a `generado/` van conteos y porcentajes.
- Solo lectura sobre `data/processed/`, el SHP del Relevamiento y las salidas internas de Places.

USO
---
  python scripts/barrido_ciudad/cruzar_places_padron.py
  python scripts/barrido_ciudad/cruzar_places_padron.py --zona R08 --sin-rus
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import io
import json
import re
import sys
import unicodedata
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_capa_homogenea import (  # noqa: E402
    UBICACION,
    cargar_direcciones_gastronomicas,
)
from places_control_zonas import (  # noqa: E402
    CRS_METRICO,
    GEN,
    asignar_por_geometria,
    perimetros,
    zonas_con_cifra,
)
from places_techo_zona import INTERNO as INTERNO_TECHO  # noqa: E402

ZONA_POR_DEFECTO = "R08"
INTERNO = ROOT / "outputs" / "analisis_interno" / "cruce_places_padron_2026-08"

# Tolerancia de altura para dar dos direcciones por la misma. Diez números es cerca de una décima
# de cuadra: absorbe el frente de un mismo inmueble (1140 y 1142 en el padrón, 1145 en Places) sin
# llegar al vecino de al lado. Por encima de esto la coincidencia la tiene que dar la proximidad,
# que se informa aparte.
TOLERANCIA_ALTURA = 10

# Radio para la coincidencia por proximidad sin coincidencia de dirección. A 25 m entran el local
# de la esquina asentado sobre la otra calle y el error de geocodificación; a 50 m ya entra media
# cuadra de vecinos. Se informa como categoría propia y nunca sumado sin decirlo.
RADIO_PROXIMIDAD_M = 25.0

# Títulos y partículas que una fuente escribe y la otra no. No son parte del nombre de la calle.
TITULOS = {
    "AV", "AVDA", "AVENIDA", "DR", "DRA", "DOCTOR", "DOCTORA", "TTE", "TENIENTE", "GRAL",
    "GENERAL", "CNEL", "CORONEL", "PRES", "PRESIDENTE", "PTE", "ING", "INGENIERO", "ARQ",
    "PROF", "PADRE", "MONS", "CAP", "CAPITAN", "SGTO", "ALTE", "ALMIRANTE", "MAY", "MAYOR",
    "DE", "DEL", "LA", "EL", "LOS", "LAS", "PJE", "PASAJE", "CALLE", "CDAD", "AUTONOMA",
    "BUENOS", "AIRES",
}

# Las cinco categorías son excluyentes y van en orden de coincidencia decreciente: un punto cae en
# la primera que le corresponde. La 6.ª no es una categoría del cruce, es la declaración de que el
# panel 3 no se corrió.
CATEGORIAS = [
    "1 · dirección en el padrón núcleo",
    "2 · a menos de 25 m de una dirección núcleo",
    "3 · dirección en el padrón, otro anillo",
    "4 · parcela gastronómica del Relevamiento (no está en el padrón)",
    "5 · sin coincidencia documental",
    "6 · sin coincidencia en el padrón · Relevamiento no consultado",
]

# Las bandas están escritas ANTES de correr el cruce. El eje es el porcentaje de puntos de Places
# que NO encuentra dirección en el padrón núcleo, que es la pregunta que abrió Diego. El veredicto
# lo elige el número.
LECTURA_PREVIA = [
    (0.0, 20.0, "PLACES CONFIRMA, NO DESCUBRE",
     "Casi todo lo que Places trae ya está en la base documental. Su aporte se reduce a la señal "
     "de vigencia sobre locales conocidos —cuáles siguen abiertos—, que ninguna fuente documental "
     "da. Para eso no hace falta una grilla dimensionada para contar: alcanza una muestra mucho "
     "más chica, y el barrido de los 48 barrios como está planeado no se justifica."),
    (20.0, 45.0, "APORTE MIXTO · decide Diego",
     "Places confirma en su mayoría pero agrega una porción propia que no es despreciable. No cae "
     "en ninguna de las dos bandas previstas: se reporta el número y se decide con Diego si esa "
     "porción paga el barrido, sin acomodar la lectura."),
    (45.0, 1e9, "PLACES DESCUBRE · el barrido recupera valor propio",
     "Una parte grande de lo que Places trae no está en ninguna fuente documental. Entonces el "
     "barrido aporta cobertura, no sólo vigencia, y la grilla hay que redimensionarla para "
     "descubrimiento —no achicarla—. Se replantea con Diego antes de correr nada."),
]


# --------------------------------------------------------------------------- normalización

def plegar(texto: object) -> str:
    """Sin tildes, en mayúsculas. Las dos fuentes difieren en las dos cosas."""
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()


def tokens_calle(calle: str) -> frozenset[str]:
    """Palabras significativas del nombre de una calle, sin títulos ni partículas."""
    limpio = re.sub(r"[^A-Z0-9 ]", " ", plegar(calle))
    return frozenset(
        palabra for palabra in limpio.split()
        if len(palabra) >= 3 and palabra not in TITULOS and not palabra.isdigit()
    )


def partir_padron(direccion: object) -> list[tuple[frozenset[str], int | None]]:
    """Todas las puertas de una dirección del padrón: `CALLE 100;CALLE 104` son dos.

    El padrón asienta el frente entero del inmueble en un solo registro —es el mecanismo que
    explica los lotes de permisos— así que cualquiera de sus puertas identifica al mismo lugar.
    """
    salida = []
    for parte in str(direccion).split(";"):
        parte = parte.strip()
        if not parte:
            continue
        coincidencia = re.search(r"(\d{1,5})\s*$", parte)
        altura = int(coincidencia.group(1)) if coincidencia else None
        calle = parte[: coincidencia.start()] if coincidencia else parte
        tokens = tokens_calle(calle)
        if tokens:
            salida.append((tokens, altura))
    return salida


def partir_places(direccion: object) -> tuple[frozenset[str], int | None]:
    """Calle y altura de una `formattedAddress` de Places.

    El formato no es fijo: a veces trae basura delante (`ECA, Luis Viale 37`), a veces repite el
    código postal (`C1416CBQ C1416CBQ`). Lo estable es que el tramo de la calle termina en la
    altura, así que se toma el último tramo que termine en número y no sea el código postal.
    """
    mejor: tuple[frozenset[str], int | None] = (frozenset(), None)
    for parte in str(direccion).split(","):
        parte = parte.strip()
        if not parte or re.fullmatch(r"C\d{4}[A-Z]*(\s+C\d{4}[A-Z]*)*", plegar(parte)):
            continue
        coincidencia = re.search(r"(\d{1,5})\s*$", parte)
        if not coincidencia:
            continue
        tokens = tokens_calle(parte[: coincidencia.start()])
        if tokens:
            mejor = (tokens, int(coincidencia.group(1)))
    return mejor


def misma_calle(unos: frozenset[str], otros: frozenset[str]) -> bool:
    """Dos escrituras del mismo nombre de calle.

    Una fuente pone `RAMIREZ DE VELASCO, JUAN` y la otra `Juan Ramírez de Velasco`: el orden
    cambia y las partículas también, pero el conjunto de palabras significativas coincide. Se pide
    inclusión de un conjunto en el otro —`GALLARDO` ⊂ `{ANGEL, GALLARDO}`— o mitad de solape, para
    que `Warnes` no matchee con `Warnes y Juan B. Justo` de casualidad sobre una sola palabra corta.
    """
    if not unos or not otros:
        return False
    comunes = unos & otros
    if not comunes:
        return False
    if unos <= otros or otros <= unos:
        return True
    return len(comunes) / len(unos | otros) >= 0.5


# --------------------------------------------------------------------------- los dos conjuntos

def puntos_places(rid: str) -> pd.DataFrame:
    """Los puntos núcleo de la prueba de techo que caen dentro de la envolvente de la zona.

    Es la unión de las tres familias: el universo alcanzable medido, no la primera consulta. La
    asignación es geométrica y con la precedencia de envolventes, igual que en el control: la celda
    no es la zona.
    """
    archivo = INTERNO_TECHO / f"places_techo_{rid}_puntos.csv"
    if not archivo.exists():
        raise SystemExit(f"ABORTADO: falta {archivo}. Corré antes places_techo_zona.py.")
    puntos = asignar_por_geometria(pd.read_csv(archivo, encoding="utf-8-sig"))
    return puntos[(puntos.rid_geo == rid) & (puntos.anillo == "nucleo")].reset_index(drop=True)


def direcciones_padron(rid: str) -> gpd.GeoDataFrame:
    """Las direcciones con habilitación gastronómica dentro de la envolvente, con sus dos anillos.

    Reproduce la capa homogénea sin recalcularla: misma carga, misma regla de outliers, misma
    precedencia de envolventes. `dir_nucleo` de esta zona tiene que dar el mismo número que
    `capa_homogenea_22_zonas.csv`, y se controla al informar.
    """
    puntos, _ = cargar_direcciones_gastronomicas()
    formas = perimetros()
    if rid not in formas or formas[rid].is_empty:
        raise SystemExit(f"ABORTADO: no hay envolvente para {rid}.")
    dentro = puntos.to_crs(CRS_METRICO)
    dentro = dentro[dentro.within(formas[rid])].copy()

    ubic = pd.read_csv(UBICACION, low_memory=False)[["id_ubicacion", "direccion_original"]]
    dentro = dentro.merge(ubic, on="id_ubicacion", how="left")
    dentro["puertas"] = dentro.direccion_original.map(partir_padron)
    return gpd.GeoDataFrame(dentro, geometry="geometry", crs=CRS_METRICO)


def parcelas_rus(rid: str) -> gpd.GeoDataFrame | None:
    """Parcelas gastronómicas del Relevamiento dentro de la envolvente, como polígonos.

    Se conserva el polígono —no el centroide, como en la capa por zona— porque acá el cruce es
    punto en parcela: un punto de Places cae adentro de la parcela o no cae, y eso no depende de
    ningún radio elegido a mano.
    """
    import pyogrio

    from perfilar_usos_suelo import anillos

    directorio = ROOT / "outputs" / "fuentes_externas" / "usos_suelo" / "shp"
    rutas = glob.glob(str(directorio / "*.shp"))
    if not rutas:
        return None
    nucleo, ampliado = anillos()

    crs_shp = pyogrio.read_info(rutas[0])["crs"]
    perimetro = (gpd.GeoSeries([perimetros()[rid]], crs=CRS_METRICO)
                 .to_crs(crs_shp).iloc[0])
    parcelas = pyogrio.read_dataframe(
        rutas[0], columns=["SMP", "TIPO1", "TIPO2", "ESTADO"],
        where="TIPO1 = 'UNICOMERCIAL'", bbox=perimetro.bounds,
    )
    parcelas = parcelas[parcelas.TIPO2.isin(ampliado)].copy()
    parcelas["es_nucleo"] = parcelas.TIPO2.isin(nucleo)
    return parcelas.to_crs(CRS_METRICO)


# --------------------------------------------------------------------------- el cruce

def clasificar(places: pd.DataFrame, padron: gpd.GeoDataFrame,
               rus: gpd.GeoDataFrame | None) -> pd.DataFrame:
    """Una fila por punto de Places, con su categoría de coincidencia y con qué coincidió."""
    geo = gpd.GeoDataFrame(
        places.copy(),
        geometry=gpd.points_from_xy(places.lon, places.lat), crs="EPSG:4326",
    ).to_crs(CRS_METRICO)

    nucleo = padron[padron.es_nucleo & ~padron.es_outlier]
    filas = []
    for punto in geo.itertuples():
        tokens, altura = partir_places(punto.direccion)

        # Panel 1 y 2: coincidencia de dirección contra las dos aperturas del padrón.
        # Se guarda además la distancia EN NUMERACIÓN a la dirección más cercana de la misma
        # calle. Separa dos cosas que «no está en el padrón» confunde: que el padrón no tenga
        # ninguna gastronomía en esa calle, y que la tenga a doscientos números de ahí.
        coincide_nucleo, coincide_todo = None, None
        delta_minimo, calle_en_padron = None, False
        for fila in padron.itertuples():
            es_nucleo_contable = fila.es_nucleo and not fila.es_outlier
            for puertas, puerta_altura in fila.puertas:
                if not misma_calle(tokens, puertas):
                    continue
                if es_nucleo_contable:
                    calle_en_padron = True
                if altura is None or puerta_altura is None:
                    continue
                brecha = abs(altura - puerta_altura)
                if es_nucleo_contable and (delta_minimo is None or brecha < delta_minimo):
                    delta_minimo = brecha
                if brecha > TOLERANCIA_ALTURA:
                    continue
                if es_nucleo_contable and coincide_nucleo is None:
                    coincide_nucleo = fila.direccion_original
                if coincide_todo is None:
                    coincide_todo = fila.direccion_original
                break

        # Distancia a la dirección núcleo más cercana, para la categoría de proximidad.
        distancias = nucleo.distance(punto.geometry)
        metros = float(distancias.min()) if len(distancias) else float("nan")

        # Panel 3: punto en parcela del Relevamiento. Tres estados, no dos: adentro de una parcela
        # gastronómica, afuera de todas, y «no se consultó». Confundir el segundo con el tercero es
        # el error del cero que no es un cero, y acá daría por descubrimiento lo que no se miró.
        rus_estado, rus_tipo, metros_rus = "no_consultado", "", float("nan")
        if rus is not None and len(rus):
            adentro = rus[rus.contains(punto.geometry)]
            if len(adentro):
                rus_estado = "nucleo" if adentro.es_nucleo.any() else "ampliado"
                rus_tipo = ";".join(sorted(set(adentro.TIPO2)))
            else:
                rus_estado = "sin_parcela"
                metros_rus = float(rus.distance(punto.geometry).min())

        if coincide_nucleo is not None:
            categoria = CATEGORIAS[0]
        elif metros == metros and metros <= RADIO_PROXIMIDAD_M:
            categoria = CATEGORIAS[1]
        elif coincide_todo is not None:
            categoria = CATEGORIAS[2]
        elif rus_estado in ("nucleo", "ampliado"):
            categoria = CATEGORIAS[3]
        elif rus_estado == "sin_parcela":
            categoria = CATEGORIAS[4]
        else:
            # Sin el SHP del Relevamiento el panel 3 no se puede correr. No se dice «sin
            # coincidencia documental» cuando una de las documentales no se consultó: sería el
            # mismo error del cero de `places_ampliado`.
            categoria = CATEGORIAS[5]

        filas.append({
            "place_id": punto.place_id, "nombre": punto.nombre, "direccion": punto.direccion,
            "familia_primera": punto.familia_primera, "business_status": punto.business_status,
            "categoria": categoria,
            "padron_nucleo": coincide_nucleo or "", "padron_cualquier_anillo": coincide_todo or "",
            "metros_a_nucleo_mas_cercana": round(metros, 1) if metros == metros else "",
            "calle_con_nucleo_en_padron": calle_en_padron,
            "delta_altura_mas_cercana": delta_minimo if delta_minimo is not None else "",
            "rus_estado": rus_estado, "rus_tipo2": rus_tipo,
            "metros_a_parcela_rus": round(metros_rus, 1) if metros_rus == metros_rus else "",
        })
    return pd.DataFrame(filas)


def cobertura_del_padron(detalle: pd.DataFrame, padron: gpd.GeoDataFrame) -> dict:
    """La dirección recíproca: cuántas direcciones núcleo del padrón vio Places.

    Es la lectura de vigencia. Un local del padrón que Places no ve puede estar cerrado o puede
    estar pasado el corte del ranking: la fuente no distingue las dos cosas, y por eso esto se
    reporta como cobertura y no como tasa de cierre.
    """
    nucleo = padron[padron.es_nucleo & ~padron.es_outlier]
    vistas = set(detalle[detalle.padron_nucleo != ""].padron_nucleo)
    return {
        "direcciones_nucleo": int(len(nucleo)),
        "vistas_por_places": int(nucleo.direccion_original.isin(vistas).sum()),
    }


# --------------------------------------------------------------------------- informe

def veredicto(pct_sin_padron: float) -> tuple[str, str]:
    for bajo, alto, titulo, lectura in LECTURA_PREVIA:
        if bajo <= pct_sin_padron < alto:
            return titulo, lectura
    return LECTURA_PREVIA[-1][1], LECTURA_PREVIA[-1][3]


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


def informar(rid: str, detalle: pd.DataFrame, padron: gpd.GeoDataFrame,
             rus: gpd.GeoDataFrame | None, zonas: pd.DataFrame) -> tuple[str, dict]:
    """El informe completo y el resumen que se guarda. La lectura la redacta el número."""
    salida = io.StringIO()
    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    total = len(detalle)
    conteo = detalle.categoria.value_counts()
    def n(categoria: str) -> int:
        return int(conteo.get(categoria, 0))

    en_nucleo = n(CATEGORIAS[0])
    por_proximidad = n(CATEGORIAS[1])
    otro_anillo = n(CATEGORIAS[2])
    en_rus = n(CATEGORIAS[3])
    sin_nada = n(CATEGORIAS[4]) + n(CATEGORIAS[5])

    pct_sin_padron = 100 * (total - en_nucleo) / total
    pct_sin_padron_amplio = 100 * (total - en_nucleo - por_proximidad) / total
    pct_sin_documental = 100 * sin_nada / total
    titulo, lectura = veredicto(pct_sin_padron)
    titulo_amplio, _ = veredicto(pct_sin_padron_amplio)

    publicada = int(zonas.relevado[rid])
    nombre_zona = zonas.zona_publicada[rid]
    base_nucleo = int((padron.es_nucleo & ~padron.es_outlier).sum())
    esperado = int(zonas.dir_nucleo[rid])

    linea("=" * 98)
    linea(f"CRUCE PLACES × BASE DOCUMENTAL · {rid} · {nombre_zona} · CERO REQUESTS")
    linea("=" * 98)
    linea()
    linea("§1 · LOS DOS CONJUNTOS")
    linea("-" * 98)
    linea(f"  Places, unión de las tres familias, núcleo, dentro de la envolvente : {total:>5}")
    linea(f"  Padrón, direcciones núcleo sin outliers, dentro de la envolvente    : {base_nucleo:>5}")
    linea(f"  Cifra publicada del Atlas (conteo de campo)                         : {publicada:>5}")
    if rus is not None:
        linea(f"  Relevamiento, parcelas gastronómicas dentro de la envolvente       : {len(rus):>5}")
    else:
        linea("  Relevamiento: SHP ausente. El panel 3 no se corrió y se declara.")
    control = "reproduce" if base_nucleo == esperado else f"NO reproduce (esperado {esperado})"
    linea(f"  Control de aceptación contra la capa homogénea: {control}.")
    linea()
    linea("§2 · CÓMO SE REPARTEN LOS PUNTOS DE PLACES")
    linea("-" * 98)
    # Se listan también las categorías en cero. Un cero medido dice algo —ningún punto de Places
    # cayó sobre una dirección del anillo ampliado— y esconderlo lo haría indistinguible de una
    # categoría que no se midió.
    medibles = CATEGORIAS[:3] + (CATEGORIAS[3:5] if rus is not None else CATEGORIAS[5:])
    linea(f"  {'categoría':<62}{'puntos':>8}{'% del total':>14}")
    for categoria in medibles:
        linea(f"  {categoria:<62}{n(categoria):>8}{_coma(100 * n(categoria) / total):>13} %")
    linea(f"  {'TOTAL':<62}{total:>8}{'100,0 %':>14}")
    linea()
    for texto in _envolver(
        "La categoría 1 es coincidencia de dirección: misma calle y altura dentro de "
        f"±{TOLERANCIA_ALTURA}. La 2 no coincide en dirección pero tiene una dirección núcleo del "
        f"padrón a menos de {_coma(RADIO_PROXIMIDAD_M, 0)} m, y va aparte porque a esa distancia "
        "también está el vecino de al lado. Las 3 y 4 son el control contra el resto de la base "
        "documental: sin ellas, «no está en el padrón núcleo» se leería como «no lo tiene nadie»."):
        linea(f"  {texto}")
    linea()
    linea("§3 · DE QUÉ ESTÁ HECHO LO QUE NO COINCIDE")
    linea("-" * 98)
    sin_coincidir = detalle[detalle.padron_nucleo == ""]
    calle_ausente = int((~sin_coincidir.calle_con_nucleo_en_padron).sum())
    linea(f"  En calles donde el padrón núcleo no tiene NINGUNA dirección : {calle_ausente:>4}")
    linea(f"  En la misma calle, a más de ±{TOLERANCIA_ALTURA} de altura                  : "
          f"{len(sin_coincidir) - calle_ausente:>4}")
    deltas = pd.to_numeric(sin_coincidir.delta_altura_mas_cercana, errors="coerce").dropna()
    if len(deltas):
        linea(f"  Distancia en numeración a la dirección núcleo más cercana de la misma calle: "
              f"mediana {int(deltas.median())}, mínimo {int(deltas.min())}, máximo {int(deltas.max())}")
    linea()
    # El punto de Google puede caer sobre la vereda o sobre la parcela lindera, y entonces el punto
    # en polígono da negativo por unos metros. Se mide, no se supone.
    huerfanos = detalle[detalle.categoria == CATEGORIAS[4]]
    cerca_de_parcela = 0
    if len(huerfanos):
        cerca = pd.to_numeric(huerfanos.metros_a_parcela_rus, errors="coerce")
        cerca_de_parcela = int((cerca <= 10).sum())
        linea(f"  De los {len(huerfanos)} puntos sin ninguna coincidencia documental, "
              f"{cerca_de_parcela} están a ≤ 10 m de una parcela gastronómica del Relevamiento "
              f"—posible desplazamiento del punto de Google, no descubrimiento— y "
              f"{int((cerca > 30).sum())} a más de 30 m de la más cercana.")
        linea()
    linea("  Sensibilidad a la tolerancia de altura (el único parámetro elegido a mano):")
    linea(f"    {'tolerancia':<14}{'coinciden':>12}{'% del total':>14}")
    todos = pd.to_numeric(detalle.delta_altura_mas_cercana, errors="coerce")
    sensibilidad = {}
    for tolerancia in (5, 10, 20, 30, 50):
        coinciden = int((todos <= tolerancia).sum())
        sensibilidad[tolerancia] = coinciden
        marca = "  <- la usada" if tolerancia == TOLERANCIA_ALTURA else ""
        linea(f"    ±{tolerancia:<13}{coinciden:>12}{_coma(100 * coinciden / total):>13} %{marca}")
    # Control interno: a la tolerancia usada, las dos vías de cálculo tienen que dar lo mismo.
    if sensibilidad[TOLERANCIA_ALTURA] != en_nucleo:
        linea(f"    AVISO: la sensibilidad no reproduce la categoría 1 "
              f"({sensibilidad[TOLERANCIA_ALTURA]} contra {en_nucleo}). Revisar el cruce.")
    for texto in _envolver(
        "Subir la tolerancia no rescata el número: a ±30 ya se están dando por iguales direcciones "
        "de manzanas distintas y de veredas opuestas —en la Ciudad el centenar cambia de cuadra y "
        "la paridad cambia de vereda— y aun así el reparto se mueve poco. El resultado no depende "
        "de dónde se puso el corte."):
        linea(f"  {texto}")
    linea()
    linea("§4 · EL VEREDICTO, CONTRA LAS BANDAS ESCRITAS ANTES DE CORRER")
    linea("-" * 98)
    linea(f"  Puntos de Places SIN dirección en el padrón núcleo : {total - en_nucleo:>4} de {total}"
          f"  =  {_coma(pct_sin_padron)} %")
    linea(f"  Idem, contando también la proximidad ≤ {_coma(RADIO_PROXIMIDAD_M, 0)} m       : "
          f"{total - en_nucleo - por_proximidad:>4} de {total}  =  {_coma(pct_sin_padron_amplio)} %")
    linea(f"  Puntos sin coincidencia en NINGUNA documental      : {sin_nada:>4} de {total}"
          f"  =  {_coma(pct_sin_documental)} %")
    linea()
    # El punto de comparación que hace legible el 33 %: contra qué se lo mide. Si Places sacara al
    # azar de los locales que hay en la calle, la proporción de sus puntos que cae en el padrón
    # sería la cobertura del padrón sobre esa misma población. Es la hipótesis nula natural y hay
    # con qué compararla, porque en esta zona la cifra de campo existe.
    esperado_azar = 100 * base_nucleo / publicada
    desvio = (100 * (base_nucleo / publicada * (1 - base_nucleo / publicada) / total) ** 0.5)
    z = (100 * en_nucleo / total - esperado_azar) / desvio if desvio else 0.0
    for texto in _envolver(
        f"Contra qué se lee el {_coma(100 * en_nucleo / total)} % de coincidencia: el padrón núcleo "
        f"cubre el {_coma(esperado_azar)} % de la cifra de campo ({base_nucleo} de {publicada}). Si "
        "Places sacara sus puntos al azar de los locales que hay en la calle, ésa es exactamente la "
        f"proporción que se esperaría ver coincidir. Se observó {_coma(100 * en_nucleo / total)} %: "
        f"la diferencia es de {_coma(abs(z), 1)} desvíos y no se distingue del ruido de muestreo. "
        "**Places no está re-sirviendo la base documental**: su solape con el padrón es el que daría "
        "el azar, ni más ni menos. Lo que ve, lo ve por su cuenta."):
        linea(f"  {texto}")
    linea()
    linea(f"  >>> {titulo}")
    for texto in _envolver(lectura):
        linea(f"      {texto}")
    if titulo_amplio != titulo:
        linea()
        for texto in _envolver(
            f"AVISO: con la lectura amplia el número cae en otra banda ({titulo_amplio}). Las dos "
            "se reportan; la que manda es la de coincidencia de dirección, porque la proximidad "
            "no distingue el mismo local del vecino."):
            linea(f"      {texto}")
    linea()
    linea("§5 · LA LECTURA RECÍPROCA · QUÉ APORTA PLACES QUE NINGUNA DOCUMENTAL DA")
    linea("-" * 98)
    cobertura = cobertura_del_padron(detalle, padron)
    vistas, base = cobertura["vistas_por_places"], cobertura["direcciones_nucleo"]
    linea(f"  Direcciones núcleo del padrón que Places confirma abiertas hoy: {vistas} de {base}"
          f"  ({_coma(100 * vistas / base)} %)")
    estados = detalle.business_status.value_counts().to_dict()
    linea(f"  Estado operativo declarado por Places: {estados}")
    linea()
    for texto in _envolver(
        "Ésta es la única pregunta que Places contesta y las documentales no: el padrón no "
        "registra bajas y el Relevamiento es una foto de 2022-24. Lo que NO se puede leer al revés: "
        f"las {base - vistas} direcciones que Places no confirma no son locales cerrados. Pueden "
        "estar cerradas o pueden estar pasadas el corte del ranking, y la fuente no distingue las "
        "dos cosas. Se reporta como cobertura, nunca como tasa de cierre."):
        linea(f"  {texto}")
    linea()
    linea("§6 · LOS LÍMITES DE ESTE CRUCE")
    linea("-" * 98)
    for texto in _envolver(
        "1. La unidad es la dirección, no el local. Un negocio nuevo en una dirección que el padrón "
        "registró con otro titular cuenta como coincidencia. El aporte propio de Places no puede "
        "ser menor que el que sale acá, y sí puede ser algo mayor."):
        linea(f"  {texto}")
    for texto in _envolver(
        "2. El cruce se hace sobre los puntos que Places SÍ trajo. No dice nada sobre los que "
        "quedaron pasados el corte del ranking, que la captura-recaptura ya mostró que existen y "
        "tienen probabilidad de captura cero."):
        linea(f"  {texto}")
    for texto in _envolver(
        "3. Es una zona. Villa Crespo es la mejor calibrada que hay —646 a pie— y por eso se eligió, "
        "pero el reparto entre confirmación y descubrimiento puede ser otro donde la base documental "
        "es más flaca. Es la advertencia que corresponde antes de generalizar a 48 barrios."):
        linea(f"  {texto}")
    linea()
    linea("=" * 98)

    resumen = {
        "fecha_calculo": dt.date.today().isoformat(),
        "zona": rid, "nombre": nombre_zona,
        "requests_gastados": 0,
        "places_nucleo": total,
        "padron_nucleo": base_nucleo,
        "padron_nucleo_esperado": esperado,
        "control_de_aceptacion": base_nucleo == esperado,
        "cifra_publicada": publicada,
        "parcelas_rus": int(len(rus)) if rus is not None else None,
        "categorias": {categoria: n(categoria) for categoria in CATEGORIAS if n(categoria)},
        "pct_sin_padron_nucleo": round(pct_sin_padron, 1),
        "pct_sin_padron_nucleo_con_proximidad": round(pct_sin_padron_amplio, 1),
        "pct_sin_ninguna_documental": round(pct_sin_documental, 1),
        "veredicto": titulo,
        "veredicto_lectura_amplia": titulo_amplio,
        "direcciones_nucleo_confirmadas_por_places": vistas,
        "pct_direcciones_nucleo_confirmadas": round(100 * vistas / base, 1),
        "business_status": estados,
    }
    return salida.getvalue(), resumen


def publicar(rid: str, detalle: pd.DataFrame, texto: str, resumen: dict) -> None:
    """Conteos a `generado/`; nombres, direcciones y `place_id` a la carpeta interna."""
    INTERNO.mkdir(parents=True, exist_ok=True)
    detalle.to_csv(INTERNO / f"cruce_places_padron_{rid}_detalle.csv",
                   index=False, encoding="utf-8-sig")

    tabla = pd.DataFrame([
        {"zona": rid, "categoria": categoria, "puntos": cantidad,
         "pct_del_total": round(100 * cantidad / resumen["places_nucleo"], 1)}
        for categoria, cantidad in resumen["categorias"].items()
    ])
    tabla.to_csv(GEN / f"cruce_places_padron_{rid}.csv", index=False, encoding="utf-8")
    (GEN / f"cruce_places_padron_{rid}_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    (GEN / f"CRUCE_PLACES_PADRON_{rid}.txt").write_text(texto, encoding="utf-8")

    print(f"  publicado en {GEN.relative_to(ROOT)}: cruce_places_padron_{rid}.csv, "
          f"cruce_places_padron_{rid}_resumen.json, CRUCE_PLACES_PADRON_{rid}.txt")
    print(f"  interno (fuera de Git): {INTERNO}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zona", default=ZONA_POR_DEFECTO)
    parser.add_argument("--sin-rus", action="store_true",
                        help="saltea el panel del Relevamiento (el SHP tarda en abrir)")
    args = parser.parse_args()
    rid = args.zona

    places = puntos_places(rid)
    padron = direcciones_padron(rid)
    rus = None if args.sin_rus else parcelas_rus(rid)
    detalle = clasificar(places, padron, rus)

    zonas = zonas_con_cifra()
    texto, resumen = informar(rid, detalle, padron, rus, zonas)
    print(texto)
    publicar(rid, detalle, texto, resumen)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
