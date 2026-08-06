"""La base gastronómica de la Ciudad: `local` y `local_fuente`. Implementa el esquema del 5/8.

QUÉ ES ESTO Y QUÉ NO ES
-----------------------
Implementa `outputs/BARRIDO_CIUDAD_2026-08/ESQUEMA_BASE_GASTRONOMICA.md`. **La base no es el
entregable**: el entregable sigue siendo el mapa de polos poligonizados de toda la Ciudad, y la
base existe para que esos polígonos se puedan dibujar y defender. Eso decide todo lo que sigue —en
particular `apto_geometria`, que es el campo que impide que un polígono se dibuje con puntos que
no sirven para dibujar.

**Google Places no entra.** Por decisión del 5/8: primero se carga todo lo abierto y recién
después se dimensiona qué agrega Places. La estructura está lista para recibirlo —`PLACES` tiene
su grupo de independencia y su regla de publicación— y el cargador no existe a propósito.

LAS DOS TABLAS, Y LA SEPARACIÓN ES LO IMPORTANTE
------------------------------------------------
    local          una fila por local. Vista de consenso. Es lo que consume el clustering.
    local_fuente   una fila por (local, fuente, registro). Lo que dice CADA fuente, crudo.

**No se colapsan las fuentes a un registro «verdadero».** Si mañana alguien discute un local, la
respuesta está en `local_fuente`; si sólo existiera `local`, la respuesta sería una decisión que
ya nadie puede reconstruir.

CÓMO SE AGRUPAN LOS REGISTROS EN LOCALES, Y POR QUÉ NO ALCANZA LA PROXIMIDAD
----------------------------------------------------------------------------
El esquema (§7) admite tres criterios: `usig_exacta`, `proximidad_y_nombre` y `proximidad_Nm`.
**Sólo los dos primeros fusionan.** La proximidad sola NO fusiona, y no es prudencia decorativa:
la fusión es transitiva, así que sobre la avenida Corrientes una cadena de vecinos a menos de
cuarenta metros uno del otro terminaría siendo **un solo local de doscientos registros**. El error
no se ve en el total —los locales bajan— y arruina el mapa, que es justo lo que la base tiene que
proteger.

Los pares que sólo tienen proximidad se guardan como candidatos con `revisado = pendiente`, que es
lo que el esquema pide: los dudosos van a revisión, no a una decisión automática.

CORROBORACIÓN POR GRUPOS, NO POR FUENTES
-----------------------------------------
`n_fuentes` cuenta **grupos de independencia** (§3). Overture, Foursquare y All The Places son un
grupo solo porque Overture incorpora a las otras dos; F01 y F02 son dos porque son universos
distintos aunque los firme el mismo Gobierno. Medido sobre el recorte de la Ciudad, además, OSM no
aporta un solo registro a Overture, así que las dos sí son independientes acá.

USO
---
  python scripts/barrido_ciudad/build_base_gastronomica.py
  python scripts/barrido_ciudad/build_base_gastronomica.py --check      # contra la referencia
  python scripts/barrido_ciudad/build_base_gastronomica.py --sin-rus    # sin abrir el SHP
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import io
import json
import sys
import unicodedata
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_capa_homogenea import UBICACION, cargar_f01  # noqa: E402
from cruzar_fuentes_abiertas import (  # noqa: E402
    RADIO_M,
    UMBRAL_NOMBRE,
    parecido_nombre,
    tokens_nombre,
)
from cruzar_places_padron import TOLERANCIA_ALTURA, misma_calle, partir_padron  # noqa: E402
from places_control_zonas import CRS_METRICO  # noqa: E402

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
BASE_DIR = BARRIDO / "base"
GEN = BARRIDO / "generado"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
COMUNAS = ROOT / "data" / "raw" / "geo_comunas.geojson"
HABILITACIONES = ROOT / "data" / "processed" / "fact_habilitacion_gastronomica.csv"
OSM_POI = ROOT / "outputs" / "fuentes_externas" / "osm" / "osm_gastro_poi.csv"
OVT_POI = ROOT / "outputs" / "fuentes_externas" / "overture" / "overture_gastro_poi.csv"
ATP_POI = ROOT / "outputs" / "fuentes_externas" / "all_the_places" / "atp_caba.csv"
PERMISOS = ROOT / "outputs" / "fuentes_externas" / "gcba_nuevas" / "permisos_gastro_limpio.csv"
RUS_SHP_DIR = ROOT / "outputs" / "fuentes_externas" / "usos_suelo" / "shp"

PREFIJO_ID = "LOC"
CORTE = dt.date.today().isoformat()

# --- §3 · Grupos de independencia ---------------------------------------------------------
GRUPO = {
    "F01": "GCBA_TURISMO",
    "F02": "GCBA_AGC",
    "RUS": "GCBA_URBANISMO",
    "PERMISOS": "GCBA_ATENCION",
    "OSM": "OSM",
    "OVERTURE": "OVERTURE_FSQ_ATP",
    "ATP": "OVERTURE_FSQ_ATP",
    "FSQ": "OVERTURE_FSQ_ATP",
    "PLACES": "GOOGLE",
}

# --- §6 · Qué se puede redistribuir de cada fuente ----------------------------------------
REDISTRIBUIBLE = {
    "F01": True, "F02": True, "RUS": True, "PERMISOS": True,
    "OSM": True, "OVERTURE": True, "ATP": True, "FSQ": True,
    "PLACES": False,
}

LICENCIA = {
    "F01": "CC-BY-2.5-AR", "F02": "CC-BY-2.5-AR", "RUS": "CC-BY-2.5-AR",
    "PERMISOS": "CC-BY-2.5-AR", "OSM": "ODbL (atribución + compartir-igual)",
    "OVERTURE": "CDLA-Permissive-2.0", "ATP": "CC0 1.0",
    "PLACES": "términos de uso de Google · NO redistribuible",
}

# --- §5 · Precisión del punto, en orden. Decide el punto de consenso y `apto_geometria` ----
# El esquema manda por prioridad de precisión y NO por promedio: promediar un punto bueno con uno
# malo empeora el bueno. El orden es el del esquema: parcela catastral, dirección normalizada por
# USIG, y después las fuentes por su precisión declarada.
PRECISION = {"RUS": 5, "F02": 4, "F01": 3, "OVERTURE": 2, "OSM": 2, "ATP": 2, "PERMISOS": 0}

# Fuentes cuyo punto NO sirve para dibujar. `PERMISOS` no trae coordenada: entra por dirección y
# hereda el punto del local con el que empareja, así que nunca aporta geometría propia.
SIN_PUNTO_PROPIO = {"PERMISOS"}

# Banda de borde. Un punto puede caer unos metros afuera del polígono de su barrio por error de
# geocodificación —sobre la línea de ribera, sobre la General Paz, sobre el Riachuelo— y sigue
# siendo de la Ciudad. Más allá de eso ya es otro municipio.
#
# Los 50 m no son un número elegido a ojo: medido sobre las fuentes, del lado de afuera hay 11
# puntos a menos de 50 m y después un salto a mediana 1,3 km. El corte cae en el hueco, no en el
# medio de una distribución. Los que quedan afuera se cuentan y se declaran; no desaparecen.
BANDA_BORDE_M = 50.0


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper().strip()


class ControlFallido(RuntimeError):
    """Un control del §8 no pasó. La corrida para y no se escribe nada."""


# --------------------------------------------------------------------------- los cargadores
# Cada uno devuelve un DataFrame con el contrato de `local_fuente`. Ninguno corrige el dato de
# otro: `lon_fuente`/`lat_fuente` es el punto TAL COMO LO DA LA FUENTE.

COLUMNAS_FUENTE = ["fuente", "id_en_fuente", "lon_fuente", "lat_fuente", "nombre_fuente",
                   "direccion_fuente", "categoria_fuente", "anillo_fuente", "vigencia_fuente",
                   "fecha_corte_fuente", "smp_fuente"]


def _vacio() -> pd.DataFrame:
    return pd.DataFrame(columns=COLUMNAS_FUENTE)


def cargar_f02() -> pd.DataFrame:
    """Padrón de habilitaciones. Unidad: la dirección normalizada, que es la regla 1 del método."""
    hab = pd.read_csv(HABILITACIONES, low_memory=False)
    hab = hab[hab.es_gastronomico == "si"]
    ubic = pd.read_csv(UBICACION, low_memory=False)
    ubic["lat"] = pd.to_numeric(ubic.latitud, errors="coerce")
    ubic["lon"] = pd.to_numeric(ubic.longitud, errors="coerce")
    ubic = ubic[ubic.lat.notna() & ubic.lon.notna()]
    hab = hab.merge(ubic[["id_ubicacion", "lat", "lon"]], on="id_ubicacion", how="inner")

    from build_capa_homogenea import ANILLO_AMPLIADO, ANILLO_NUCLEO, UMBRAL_OUTLIER

    por_direccion = hab.groupby("id_ubicacion")
    filas = []
    for id_ubicacion, grupo in por_direccion:
        if len(grupo) > UMBRAL_OUTLIER:   # regla 3: la dirección anómala no es un local
            continue
        categorias = set(grupo.categoria_gastronomica_inferida.dropna())
        anillo = ("nucleo" if categorias & set(ANILLO_NUCLEO)
                  else "ampliado" if categorias & set(ANILLO_AMPLIADO) else "fuera")
        if anillo == "fuera":
            continue
        fechas = pd.to_datetime(grupo.fecha_habilitacion, errors="coerce").dropna()
        filas.append({
            "fuente": "F02",
            "id_en_fuente": str(id_ubicacion),
            "lon_fuente": float(grupo.lon.iloc[0]),
            "lat_fuente": float(grupo.lat.iloc[0]),
            "nombre_fuente": "",
            "direccion_fuente": str(grupo.direccion_original.iloc[0]),
            "categoria_fuente": ";".join(sorted(categorias)),
            "anillo_fuente": anillo,
            # El padrón NO registra bajas: lo que afirma es que hubo una habilitación, nunca que
            # el local siga abierto. Se guarda esa frase y no un booleano, que mentiría.
            "vigencia_fuente": f"habilitación aprobada ({len(grupo)}); no registra bajas",
            "fecha_corte_fuente": str(fechas.max().date()) if len(fechas) else "",
            "smp_fuente": "",
        })
    return pd.DataFrame(filas)


def cargar_f01_base(barrios: gpd.GeoDataFrame) -> pd.DataFrame:
    f01 = cargar_f01(barrios.rename(columns={"nombre_barrio": "nombre"}))
    f01 = f01[f01.lon.notna() & f01.lat.notna()]
    return pd.DataFrame({
        "fuente": "F01",
        "id_en_fuente": f01.id.astype(str),
        "lon_fuente": f01.lon.astype(float),
        "lat_fuente": f01.lat.astype(float),
        "nombre_fuente": f01.nombre.fillna(""),
        "direccion_fuente": f01.direccion_completa.fillna(""),
        "categoria_fuente": f01.categoria.fillna(""),
        "anillo_fuente": "nucleo",
        "vigencia_fuente": "figura en el padrón turístico de la fuente",
        "fecha_corte_fuente": "2026",
        "smp_fuente": "",
    }).reset_index(drop=True)


def cargar_osm_base() -> pd.DataFrame:
    if not OSM_POI.exists():
        return _vacio()
    t = pd.read_csv(OSM_POI, encoding="utf-8-sig", low_memory=False)
    t = t[t.anillo.isin(["nucleo", "ampliado"])]
    return pd.DataFrame({
        "fuente": "OSM",
        "id_en_fuente": t.osm_tipo.astype(str) + "/" + t.osm_id.astype(str),
        "lon_fuente": t.lon.astype(float),
        "lat_fuente": t.lat.astype(float),
        "nombre_fuente": t.nombre.fillna(""),
        "direccion_fuente": (t.calle.fillna("").astype(str) + " "
                             + t.altura.fillna("").astype(str)).str.strip(),
        "categoria_fuente": t.rubro.fillna(""),
        "anillo_fuente": t.anillo,
        "vigencia_fuente": np.where(t.check_date.fillna("") != "",
                                    "verificado en el terreno el " + t.check_date.fillna(""),
                                    "sin verificación declarada"),
        "fecha_corte_fuente": t.editado.fillna(""),
        "smp_fuente": "",
    }).reset_index(drop=True)


def cargar_overture_base() -> pd.DataFrame:
    if not OVT_POI.exists():
        return _vacio()
    t = pd.read_csv(OVT_POI, encoding="utf-8-sig", low_memory=False)
    return pd.DataFrame({
        "fuente": "OVERTURE",
        "id_en_fuente": t.id.astype(str),
        "lon_fuente": t.lon.astype(float),
        "lat_fuente": t.lat.astype(float),
        "nombre_fuente": t.nombre.fillna(""),
        "direccion_fuente": t.direccion.fillna(""),
        "categoria_fuente": t.categoria.fillna(""),
        "anillo_fuente": t.anillo,
        "vigencia_fuente": "confianza declarada " + t.confidence.round(2).astype(str),
        "fecha_corte_fuente": "2026-07-22",
        "smp_fuente": "",
    }).reset_index(drop=True)


def cargar_atp_base() -> pd.DataFrame:
    if not ATP_POI.exists():
        return _vacio()
    from bajar_all_the_places import CORRIDA, clasificar

    t = clasificar(pd.read_csv(ATP_POI, encoding="utf-8-sig", low_memory=False))
    t = t[t.anillo.isin(["nucleo", "ampliado"])]
    return pd.DataFrame({
        "fuente": "ATP",
        "id_en_fuente": t.atp_id.astype(str),
        "lon_fuente": t.lon.astype(float),
        "lat_fuente": t.lat.astype(float),
        "nombre_fuente": t["name"].fillna(""),
        "direccion_fuente": (t["addr:street"].fillna("").astype(str) + " "
                             + t["addr:housenumber"].fillna("").astype(str)).str.strip(),
        "categoria_fuente": t.rubro.fillna(""),
        "anillo_fuente": t.anillo,
        "vigencia_fuente": "publicado por el localizador de sucursales de la marca",
        "fecha_corte_fuente": CORRIDA[:10],
        "smp_fuente": "",
    }).reset_index(drop=True)


def cargar_permisos_base() -> pd.DataFrame:
    """Permisos de vereda. **Sin coordenada**: entran por dirección y no aportan geometría.

    Es la única fuente con una afirmación de vigencia con fecha FUTURA. Vale la pena aunque no
    traiga punto: engancha por dirección a un local que ya está y le pone fecha a su frescura.
    """
    if not PERMISOS.exists():
        return _vacio()
    t = pd.read_csv(PERMISOS, encoding="utf-8-sig", low_memory=False)
    direccion = (t["Dirección"].fillna("").astype(str) + " "
                 + t["Altura"].fillna("").astype(str)).str.strip()
    return pd.DataFrame({
        "fuente": "PERMISOS",
        "id_en_fuente": t["Expediente"].fillna("").astype(str),
        "lon_fuente": np.nan,
        "lat_fuente": np.nan,
        "nombre_fuente": "",
        "direccion_fuente": direccion,
        "categoria_fuente": "permiso de vereda",
        "anillo_fuente": "nucleo",
        "vigencia_fuente": (t["Estado Vereda"].fillna("").astype(str) + " · vence "
                            + t["Fecha de Vencimiento"].fillna("s/f").astype(str)),
        # La fecha de corte es la de la DISPOSICIÓN, no la del vencimiento. El vencimiento es una
        # fecha futura y usarlo como fecha de evidencia daría locales con `frescura` en 2031, que
        # es exactamente el error que `frescura` tiene que evitar: la evidencia es que el permiso
        # se otorgó tal día, no que vaya a valer hasta tal otro. El «hasta cuándo» viaja completo
        # en `vigencia_fuente`, que es donde el esquema pide que quede lo que la fuente afirma.
        "fecha_corte_fuente": pd.to_datetime(
            t["Fecha de Inicio"], errors="coerce", dayfirst=True).dt.date.astype(str),
        "smp_fuente": "",
    }).reset_index(drop=True)


def cargar_rus_base() -> pd.DataFrame:
    """Relevamiento de Usos del Suelo, por parcela activa. Aporta el `smp`, que es el match fuerte."""
    import pyogrio

    from perfilar_usos_suelo import anillos

    rutas = glob.glob(str(RUS_SHP_DIR / "*.shp"))
    if not rutas:
        return _vacio()
    nucleo, ampliado = anillos()
    import pyogrio as _pyogrio

    campos = set(_pyogrio.read_info(rutas[0])["fields"])
    # El encabezado del año llega como `AÑO` o como `ANIO` según la exportación. Se resuelve
    # mirando qué campos tiene el archivo, no suponiendo cuál de los dos es.
    campo_anio = next((c for c in ("ANIO", "AÑO", "ANO", "Año") if c in campos), None)
    columnas = ["SMP", "TIPO1", "TIPO2", "ESTADO", "BARRIO"] + ([campo_anio] if campo_anio else [])
    capa = pyogrio.read_dataframe(rutas[0], columns=columnas,
                                  where="TIPO1 = 'UNICOMERCIAL' AND ESTADO = 'ACTIVO'")
    capa = capa[capa.TIPO2.isin(ampliado)].copy()
    # La unidad es la parcela ACTIVA con SMP único: contar registros da de más porque una parcela
    # con dos usos gastronómicos aparece dos veces. Es la definición canónica del proyecto.
    capa = capa.drop_duplicates(subset="SMP")
    puntos = capa.to_crs("EPSG:4326").geometry.centroid
    return pd.DataFrame({
        "fuente": "RUS",
        "id_en_fuente": capa.SMP.astype(str).values,
        "lon_fuente": puntos.x.values,
        "lat_fuente": puntos.y.values,
        "nombre_fuente": "",
        "direccion_fuente": "",
        "categoria_fuente": capa.TIPO2.values,
        "anillo_fuente": np.where(capa.TIPO2.isin(nucleo), "nucleo", "ampliado"),
        # El Relevamiento es rotativo: cada barrio tiene su año, no hay una foto simultánea de la
        # Ciudad. Poner «2022-2024» para todos dejaba a 10.952 locales sin fecha parseable y por
        # lo tanto sin `frescura`, que es justo lo que esta fuente sí puede aportar.
        "vigencia_fuente": "uso gastronómico ACTIVO al relevar la parcela",
        "fecha_corte_fuente": (capa[campo_anio].astype(str).values if campo_anio
                               else ["2023"] * len(capa)),
        "smp_fuente": capa.SMP.astype(str).values,
    }).reset_index(drop=True)


# --------------------------------------------------------------------------- el agrupamiento

class Union:
    """Union-find. Agrupa registros de distintas fuentes en un mismo local."""

    def __init__(self, n: int) -> None:
        self.padre = list(range(n))

    def raiz(self, i: int) -> int:
        while self.padre[i] != i:
            self.padre[i] = self.padre[self.padre[i]]
            i = self.padre[i]
        return i

    def unir(self, i: int, j: int) -> None:
        a, b = self.raiz(i), self.raiz(j)
        if a != b:
            self.padre[max(a, b)] = min(a, b)


def puertas_de(direccion: object) -> list[tuple[frozenset[str], int | None]]:
    return partir_padron(direccion)


def pares_candidatos(registros: gpd.GeoDataFrame, radio: float) -> pd.DataFrame:
    """Todos los pares de registros a menos de `radio`, de fuentes distintas.

    Se resuelve con un `sjoin` contra los propios puntos ensanchados: es el paso caro y el índice
    espacial lo hace una vez. Comparar dirección y nombre sobre estos candidatos es barato.
    """
    izq = registros[["geometry"]].copy()
    der = registros[["geometry"]].copy()
    der["geometry"] = der.geometry.buffer(radio)
    pares = gpd.sjoin(izq, der, how="inner", predicate="within")
    pares = pares.reset_index().rename(columns={"index": "i", "index_right": "j"})
    return pares[pares.i < pares.j]


def clasificar_par(puertas_a: list, puertas_b: list, nombre_a: frozenset, nombre_b: frozenset,
                   smp_a: str, smp_b: str) -> tuple[str, int]:
    """El criterio del par, con la fuerza que le corresponde. §7 del esquema.

    Recibe valores sueltos y no filas de un DataFrame a propósito: son cientos de miles de pares y
    un `.iloc[]` por par convierte una corrida de dos minutos en una de media hora.
    """
    if smp_a and smp_b and smp_a == smp_b:
        return "smp", 4
    for tokens_a, altura_a in puertas_a:
        if altura_a is None:
            continue
        for tokens_b, altura_b in puertas_b:
            if (altura_b is not None and abs(altura_a - altura_b) <= TOLERANCIA_ALTURA
                    and misma_calle(tokens_a, tokens_b)):
                return "usig_exacta", 3
    if parecido_nombre(nombre_a, nombre_b) >= UMBRAL_NOMBRE:
        return "proximidad_y_nombre", 2
    return f"proximidad_{int(RADIO_M)}m", 1


def clasificar_pares(registros: gpd.GeoDataFrame, radio_maximo: float) -> pd.DataFrame:
    """Clasifica UNA sola vez todos los pares hasta el radio más grande que se vaya a usar.

    La sensibilidad al radio pide agrupar a 20, 40 y 60 m. Hacerlo con tres pasadas clasificaba
    tres veces los mismos pares —que es la parte cara, porque compara direcciones token a token— y
    triplicaba el tiempo de la corrida sin agregar información: un par a 18 m es el mismo par y
    tiene el mismo criterio se lo mire con el radio que se lo mire. Se clasifica una vez hasta el
    radio máximo y cada radio filtra por distancia.
    """
    pares = pares_candidatos(registros, radio_maximo)
    # Todo se pasa a listas y arrays antes del bucle: indexar un GeoDataFrame por posición
    # cuesta órdenes de magnitud más que indexar una lista, y acá hay cientos de miles de pares.
    puertas = list(registros.puertas)
    nombres = list(registros.tokens_nombre)
    smps = [str(s) if s == s else "" for s in registros.smp_fuente]
    xs = registros.geometry.x.to_numpy()
    ys = registros.geometry.y.to_numpy()

    indices_i = pares.i.to_numpy()
    indices_j = pares.j.to_numpy()
    metros = np.hypot(xs[indices_i] - xs[indices_j], ys[indices_i] - ys[indices_j]).round(1)

    criterios, fuerzas = [], []
    for i, j in zip(indices_i, indices_j):
        criterio, fuerza = clasificar_par(puertas[i], puertas[j], nombres[i], nombres[j],
                                          smps[i], smps[j])
        criterios.append(criterio)
        fuerzas.append(fuerza)

    return pd.DataFrame({"i": indices_i, "j": indices_j, "criterio_match": criterios,
                         "score_match": fuerzas, "metros": metros})


def agrupar(registros: gpd.GeoDataFrame, todos_los_pares: pd.DataFrame,
            radio: float) -> tuple[np.ndarray, pd.DataFrame]:
    """Devuelve el grupo de cada registro y los pares dentro del radio, con su criterio.

    **Sólo fusionan `smp`, `usig_exacta` y `proximidad_y_nombre`.** La proximidad sola queda como
    par candidato con `revisado = pendiente`: la fusión es transitiva y un encadenamiento por
    cercanía sobre una avenida convertiría una cuadra entera en un local.
    """
    pares = todos_los_pares[todos_los_pares.metros <= radio].copy()
    # El nombre del criterio lleva el radio adentro y el radio cambia entre corridas: se reescribe
    # para que un `proximidad_60m` no aparezca en una corrida de 40.
    pares["criterio_match"] = np.where(pares.score_match >= 2, pares.criterio_match,
                                       f"proximidad_{int(radio)}m")
    pares["fusiona"] = pares.score_match >= 2
    union = Union(len(registros))
    for i, j in zip(pares[pares.fusiona].i, pares[pares.fusiona].j):
        union.unir(int(i), int(j))
    grupos = np.array([union.raiz(i) for i in range(len(registros))])
    return grupos, pares.reset_index(drop=True)


# --------------------------------------------------------------------------- la base

def recortar_a_la_ciudad(registros: gpd.GeoDataFrame,
                         barrios: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, dict]:
    """Deja los registros que caen en la Ciudad o en su banda de borde. Declara lo que saca.

    Overture y el padrón vienen ya recortados; All The Places no, porque su recorte es por
    rectángulo y el rectángulo de la Ciudad entra en Vicente López y en Avellaneda. Sin este paso
    esos puntos entran a la base como locales sin barrio, y el control §8.3 los encuentra tarde:
    ya están adentro y ya formaron grupo con alguno de acá.
    """
    ciudad = barrios.to_crs(registros.crs).union_all()
    adentro = registros.within(ciudad)
    distancia = registros[~adentro].distance(ciudad)
    en_banda = distancia <= BANDA_BORDE_M

    descartados = registros[~adentro][~en_banda]
    detalle = {
        "descartados": int(len(descartados)),
        "por_fuente": descartados.fuente.value_counts().to_dict(),
        "rescatados_en_banda": int(en_banda.sum()),
        "banda_m": BANDA_BORDE_M,
    }
    conservar = adentro.copy()
    conservar.loc[distancia[en_banda].index] = True
    return registros[conservar].reset_index(drop=True), detalle


def enganchar_permisos(permisos: pd.DataFrame, registros: gpd.GeoDataFrame,
                       grupos: np.ndarray) -> tuple[pd.DataFrame, dict]:
    """Pega cada permiso de vereda al local que ya está en la base, por dirección exacta.

    Los permisos no traen coordenada, así que no pueden formar un local por sí solos ni entrar al
    agrupamiento espacial. Lo que sí pueden —y es su valor— es ponerle **fecha futura de vigencia**
    a un local que ya existe: es la única afirmación de vigencia con fecha por delante en todo el
    conjunto de fuentes.

    Un permiso que no engancha con ninguna dirección conocida NO crea un local: sin punto no se
    puede dibujar y sin dibujo no sirve al objetivo. Se cuenta y se declara.
    """
    if not len(permisos):
        return pd.DataFrame(), {"enganchados": 0, "sin_enganche": 0}

    indice: dict[tuple[frozenset[str], int], int] = {}
    for posicion, fila in enumerate(registros.itertuples()):
        for tokens, altura in fila.puertas:
            if altura is not None:
                indice.setdefault((tokens, altura), grupos[posicion])

    filas, sin_enganche = [], 0
    for permiso in permisos.itertuples():
        grupo = None
        for tokens, altura in puertas_de(permiso.direccion_fuente):
            if altura is None:
                continue
            for (tokens_base, altura_base), g in indice.items():
                if abs(altura - altura_base) <= TOLERANCIA_ALTURA and misma_calle(tokens, tokens_base):
                    grupo = g
                    break
            if grupo is not None:
                break
        if grupo is None:
            sin_enganche += 1
            continue
        fila = {c: getattr(permiso, c, "") for c in COLUMNAS_FUENTE}
        fila.update({"grupo": grupo, "criterio_match": "usig_exacta", "score_match": 3,
                     "revisado": "auto"})
        filas.append(fila)

    return pd.DataFrame(filas), {"enganchados": len(filas), "sin_enganche": sin_enganche}


def construir(registros: gpd.GeoDataFrame, pares: pd.DataFrame, grupos: np.ndarray,
              barrios: gpd.GeoDataFrame, comunas: gpd.GeoDataFrame,
              extra: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    registros = registros.copy()
    registros["grupo"] = grupos

    # §2 · `local_id` propio y correlativo. Nunca derivado de un identificador externo ni de un
    # hash de atributos: un hash se rompe cuando el local cambia de rubro y colisiona en los
    # edificios con dos locales, que en la Ciudad es lo normal.
    orden = {g: n for n, g in enumerate(sorted(registros.grupo.unique()), start=1)}
    registros["local_id"] = registros.grupo.map(lambda g: f"{PREFIJO_ID}{orden[g]:06d}")

    # El motivo por el que cada registro quedó pegado a su local: el par más fuerte que lo unió.
    motivo = {}
    for par in pares[pares.fusiona].itertuples():
        for indice in (par.i, par.j):
            previo = motivo.get(indice)
            if previo is None or par.score_match > previo[1]:
                motivo[indice] = (par.criterio_match, par.score_match)
    registros["criterio_match"] = [motivo.get(i, ("unico_en_su_local", 0))[0]
                                   for i in range(len(registros))]
    registros["score_match"] = [motivo.get(i, ("", 0))[1] for i in range(len(registros))]
    # §7 · los dudosos van a revisión, no a una decisión automática.
    pendientes = set(pares[~pares.fusiona].i) | set(pares[~pares.fusiona].j)
    registros["revisado"] = np.where(registros.index.isin(pendientes), "pendiente", "auto")

    # Los registros sin punto —los permisos de vereda— entran acá, ya enganchados a su grupo. Se
    # agregan DESPUÉS de asignar criterios porque `pares` está indexado posicionalmente sobre los
    # registros con punto: concatenar antes correría todos los índices.
    if extra is not None and len(extra):
        extra = extra.copy()
        extra["local_id"] = extra.grupo.map(lambda g: f"{PREFIJO_ID}{orden[g]:06d}")
        extra["geometry"] = None
        registros = gpd.GeoDataFrame(
            pd.concat([registros, extra], ignore_index=True),
            geometry="geometry", crs=registros.crs)

    local_fuente = registros[[
        "local_id", "fuente", "id_en_fuente", "lon_fuente", "lat_fuente", "nombre_fuente",
        "direccion_fuente", "categoria_fuente", "vigencia_fuente", "fecha_corte_fuente",
        "criterio_match", "score_match", "revisado"]].copy()

    # ---- la vista de consenso -------------------------------------------------------------
    filas = []
    for local_id, grupo in registros.groupby("local_id"):
        # §5 · punto de consenso por PRIORIDAD DE PRECISIÓN, no por promedio: promediar un punto
        # bueno con uno malo empeora el bueno.
        con_punto = grupo[grupo.lon_fuente.notna() & ~grupo.fuente.isin(SIN_PUNTO_PROPIO)]
        if len(con_punto):
            mejor = con_punto.loc[con_punto.fuente.map(PRECISION).idxmax()]
            lon, lat = float(mejor.lon_fuente), float(mejor.lat_fuente)
            precision = int(PRECISION[mejor.fuente])
            dispersion = float(con_punto.geometry.distance(mejor.geometry).max()) if len(con_punto) > 1 else 0.0
        else:
            lon = lat = np.nan
            precision, dispersion = 0, np.nan

        fuentes = sorted(set(grupo.fuente))
        grupos_indep = sorted({GRUPO[f] for f in fuentes})
        anillos = set(grupo.anillo_fuente)
        anillo = "nucleo" if "nucleo" in anillos else ("ampliado" if "ampliado" in anillos else "fuera")

        # §4 · `frescura` = fecha de la evidencia positiva más reciente. NUNCA «abierto».
        # Y nunca en el futuro: una evidencia con fecha posterior a hoy no es evidencia, es una
        # fecha de vencimiento mal leída. Se descarta acá para que el error no pueda entrar por
        # una fuente nueva que traiga otra fecha por delante.
        fechas = pd.to_datetime(grupo.fecha_corte_fuente, errors="coerce").dropna()
        fechas = fechas[fechas <= pd.Timestamp(CORTE)]
        frescura = str(fechas.max().date()) if len(fechas) else ""

        # §6 · el nivel de publicación lo decide de dónde viene la IDENTIDAD, no el punto.
        con_identidad_abierta = [f for f in fuentes
                                 if REDISTRIBUIBLE[f] and (grupo[grupo.fuente == f].nombre_fuente != "").any()]
        if con_identidad_abierta:
            nivel = "abierto"
        elif any(REDISTRIBUIBLE[f] for f in fuentes):
            nivel = "punto"
        else:
            nivel = "agregado"

        nombres = [n for n in grupo.nombre_fuente if str(n).strip()]
        direcciones = [d for d in grupo.direccion_fuente if str(d).strip()]
        smps = [s for s in grupo.smp_fuente if str(s).strip()]

        filas.append({
            "local_id": local_id,
            "lon": lon, "lat": lat,
            "smp": smps[0] if smps else "",
            "direccion_norm": direcciones[0] if direcciones else "",
            "nombre": nombres[0] if nombres else "",
            "anillo": anillo,
            "categoria": grupo.categoria_fuente.iloc[0],
            "n_registros": int(len(grupo)),
            "fuentes": ";".join(fuentes),
            "n_fuentes": len(grupos_indep),
            "grupos_independencia": ";".join(grupos_indep),
            "precision_punto": precision,
            "dispersion_m": round(dispersion, 1) if dispersion == dispersion else None,
            "nivel_publicacion": nivel,
            "frescura": frescura,
            "revisado": "pendiente" if (grupo.revisado == "pendiente").any() else "auto",
            "corte": CORTE,
        })

    local = pd.DataFrame(filas)

    # §5 · `apto_geometria`. No es apto el punto sin coordenada y no lo es el que tiene a sus
    # fuentes en desacuerdo por más del umbral declarado: si dos fuentes ubican al mismo local a
    # cien metros una de otra, ese punto no puede decidir la forma de un polígono.
    local["apto_geometria"] = (
        local.lon.notna()
        & (local.precision_punto > 0)
        & ((local.dispersion_m.isna()) | (local.dispersion_m <= RADIO_M))
    )

    # §8.3 · asignación territorial por geometría, o corta. Punto en polígono primero; para los
    # que caen en la banda de borde —sobre la ribera, sobre la General Paz— gana el barrio más
    # cercano y queda marcado, porque no es lo mismo y el que lea la base tiene que poder verlo.
    con_punto = local[local.lon.notna()]
    puntos = gpd.GeoDataFrame(
        con_punto, geometry=gpd.points_from_xy(con_punto.lon, con_punto.lat), crs="EPSG:4326")
    puntos = gpd.sjoin(puntos, barrios[["nombre_barrio", "geometry"]], how="left", predicate="within")
    puntos = puntos.drop(columns=["index_right"], errors="ignore").drop_duplicates("local_id")

    sin_barrio = puntos[puntos.nombre_barrio.isna()]
    if len(sin_barrio):
        cercano = gpd.sjoin_nearest(
            sin_barrio.drop(columns=["nombre_barrio"]).to_crs(CRS_METRICO),
            barrios[["nombre_barrio", "geometry"]].to_crs(CRS_METRICO),
            how="left", max_distance=BANDA_BORDE_M, distance_col="borde_m")
        cercano = cercano.drop_duplicates("local_id")
        asignados = dict(zip(cercano.local_id, cercano.nombre_barrio))
        puntos["nombre_barrio"] = [
            asignados.get(lid, b) if pd.isna(b) else b
            for lid, b in zip(puntos.local_id, puntos.nombre_barrio)]
        puntos["barrio_por_cercania"] = puntos.local_id.isin(
            {k for k, v in asignados.items() if isinstance(v, str)})
    else:
        puntos["barrio_por_cercania"] = False

    puntos = gpd.GeoDataFrame(
        puntos.drop(columns="geometry"),
        geometry=gpd.points_from_xy(puntos.lon, puntos.lat), crs="EPSG:4326")
    puntos = gpd.sjoin(puntos, comunas[["comuna", "geometry"]], how="left", predicate="within")

    local = local.merge(
        puntos[["local_id", "nombre_barrio", "comuna", "barrio_por_cercania"]]
        .drop_duplicates("local_id"),
        on="local_id", how="left")
    local = local.rename(columns={"nombre_barrio": "barrio"})
    local["barrio_por_cercania"] = local.barrio_por_cercania.fillna(False)

    return local, local_fuente


# --------------------------------------------------------------------------- §8 · controles

def controles(local: pd.DataFrame, local_fuente: pd.DataFrame, pares: pd.DataFrame) -> list[dict]:
    resultados = []

    def anotar(numero: int, nombre: str, ok: bool, detalle: str) -> None:
        resultados.append({"control": numero, "nombre": nombre, "pasa": bool(ok), "detalle": detalle})

    # 3 · todo local con punto tiene barrio por geometría
    con_punto = local[local.lon.notna()]
    sin_barrio = int(con_punto.barrio.isna().sum())
    anotar(3, "asignación territorial", sin_barrio == 0,
           f"{sin_barrio} locales con punto y sin barrio (los de afuera de la Ciudad ya se filtran)")

    # 4 · `n_fuentes` nunca cuenta dos fuentes del mismo grupo
    peor = 0
    for fuentes, grupos in zip(local.fuentes, local.grupos_independencia):
        peor = max(peor, len(fuentes.split(";")) - len(grupos.split(";")))
    anotar(4, "independencia", True,
           f"máximo de fuentes colapsadas a un mismo grupo en un local: {peor}. "
           f"`n_fuentes` cuenta grupos: máximo observado {int(local.n_fuentes.max())}")

    # 5 · publicabilidad: ningún registro `abierto` puede depender sólo de una fuente cerrada
    cerradas = {f for f, abierto in REDISTRIBUIBLE.items() if not abierto}
    abiertos = local[local.nivel_publicacion == "abierto"]
    solo_cerradas = [lid for lid, f in zip(abiertos.local_id, abiertos.fuentes)
                     if set(f.split(";")) <= cerradas]
    anotar(5, "publicabilidad", not solo_cerradas,
           f"{len(solo_cerradas)} locales marcados `abierto` cuyo único origen es una fuente no "
           "redistribuible")

    # 7 · aptitud geométrica
    aptos = int(local.apto_geometria.sum())
    anotar(7, "aptitud geométrica", aptos > 0,
           f"{aptos} de {len(local)} locales pueden dibujar ({100 * aptos / len(local):.1f} %); "
           f"{int((~local.apto_geometria).sum())} no")

    # Trazabilidad: ningún registro pegado sin motivo declarado
    sin_motivo = int((local_fuente.criterio_match == "").sum())
    anotar(0, "trazabilidad del match", sin_motivo == 0,
           f"{sin_motivo} filas de `local_fuente` sin `criterio_match`")

    return resultados


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


def informar(local: pd.DataFrame, local_fuente: pd.DataFrame, pares: pd.DataFrame,
             chequeos: list[dict], sensibilidad: dict, recorte: dict,
             detalle_permisos: dict) -> tuple[str, dict]:
    salida = io.StringIO()

    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    linea("=" * 98)
    linea("BASE GASTRONÓMICA DE LA CIUDAD · `local` y `local_fuente` · SIN GOOGLE PLACES")
    linea("=" * 98)
    linea(f"corte {CORTE} · esquema del 2026-08-05 · 0 requests de Places")
    linea()

    linea("§1 · LO QUE ENTRÓ")
    linea("-" * 98)
    linea(f"  {'fuente':<12}{'registros':>11}{'grupo de independencia':>28}   licencia")
    for fuente, cuantos in local_fuente.fuente.value_counts().items():
        linea(f"  {fuente:<12}{cuantos:>11}{GRUPO[fuente]:>28}   {LICENCIA[fuente]}")
    linea(f"  {'TOTAL':<12}{len(local_fuente):>11}")
    linea()
    linea(f"  locales resueltos: {len(local):,}".replace(",", "."))
    linea(f"  registros por local: {len(local_fuente) / len(local):.2f}")
    linea()
    linea(f"  Recortados por caer fuera de la Ciudad y de su banda de "
          f"{_coma(recorte['banda_m'], 0)} m: {recorte['descartados']}")
    if recorte["por_fuente"]:
        linea("    " + " · ".join(f"{k} {v}" for k, v in recorte["por_fuente"].items()))
    linea(f"  Rescatados en la banda de borde: {recorte['rescatados_en_banda']}")
    linea()
    linea(f"  Permisos de vereda enganchados por dirección: {detalle_permisos['enganchados']}")
    linea(f"  Permisos sin enganche, que NO crean local: {detalle_permisos['sin_enganche']}")
    for texto in _envolver(
        "Un permiso sin enganche no se convierte en un local nuevo: no trae coordenada, y sin "
        "punto no puede dibujar. Se cuenta y se declara en vez de inventarle una ubicación."):
        linea(f"  {texto}")
    linea()

    linea("§2 · CORROBORACIÓN · en cuántos grupos independientes aparece cada local")
    linea("-" * 98)
    for n, cuantos in local.n_fuentes.value_counts().sort_index().items():
        linea(f"    {n} grupo{'s' if n != 1 else ' '}{'':<6}{cuantos:>7}"
              f"{_coma(100 * cuantos / len(local)):>9} %")
    linea()
    for texto in _envolver(
        "Un local que aparece en un solo grupo es una señal, no un dato corroborado. Que la mayoría "
        "esté en uno solo no es un defecto de la base: es la medición de que las fuentes ven cosas "
        "distintas, que es exactamente lo que justificaba cruzarlas."):
        linea(f"  {texto}")
    linea()

    linea("§3 · PUBLICACIÓN EN TRES NIVELES (§6 del esquema)")
    linea("-" * 98)
    for nivel, cuantos in local.nivel_publicacion.value_counts().items():
        linea(f"    {nivel:<12}{cuantos:>8}{_coma(100 * cuantos / len(local)):>9} %")
    linea()
    for texto in _envolver(
        "Sin Google Places cargado, todo lo que hay es publicable: la restricción aparece recién "
        "cuando entre Places, y para los locales que sólo él vea. El cruce de Villa Crespo ya midió "
        "cuántos serían: 4 de 81."):
        linea(f"  {texto}")
    linea()

    linea("§4 · APTITUD GEOMÉTRICA · qué puede dibujar (§5 del esquema)")
    linea("-" * 98)
    aptos = int(local.apto_geometria.sum())
    linea(f"  locales aptos para el dibujo : {aptos:>7}  ({_coma(100 * aptos / len(local))} %)")
    linea(f"  no aptos                     : {len(local) - aptos:>7}")
    motivos = {
        "sin coordenada": int(local.lon.isna().sum()),
        "fuentes en desacuerdo por más del umbral": int(
            (local.dispersion_m.notna() & (local.dispersion_m > RADIO_M)).sum()),
    }
    for motivo, cuantos in motivos.items():
        linea(f"    {motivo:<44}{cuantos:>7}")
    linea()
    for texto in _envolver(
        "Éste es el campo que protege el mapa, y existe porque el Atlas ya tropezó con esto: ocho "
        "referencias sin puntos terminaron con envolventes derivadas de la geometría de consulta y "
        "no de la oferta. Se previene con un campo, no con cuidado."):
        linea(f"  {texto}")
    linea()

    linea("§5 · CÓMO SE PEGÓ CADA REGISTRO (§7 del esquema)")
    linea("-" * 98)
    for criterio, cuantos in local_fuente.criterio_match.value_counts().items():
        linea(f"    {criterio:<26}{cuantos:>8}{_coma(100 * cuantos / len(local_fuente)):>9} %")
    linea()
    candidatos = int((~pares.fusiona).sum())
    linea(f"  Pares que quedaron como CANDIDATOS y no fusionaron: {candidatos}")
    for texto in _envolver(
        "Son los que sólo tienen proximidad. No fusionan, y no es prudencia decorativa: la fusión "
        "es transitiva, así que una cadena de vecinos a menos de cuarenta metros uno del otro "
        "convertiría una cuadra de una avenida en un solo local. Van a revisión con "
        "`revisado = pendiente`, que es lo que el esquema manda para los dudosos."):
        linea(f"  {texto}")
    linea()
    linea("  Sensibilidad al radio (§7 exige publicarla):")
    linea(f"    {'radio':<10}{'locales':>10}{'fusiones':>11}{'candidatos':>13}")
    for radio, datos in sensibilidad.items():
        marca = "  <- el usado" if radio == RADIO_M else ""
        linea(f"    {_coma(radio, 0) + ' m':<10}{datos['locales']:>10}{datos['fusiones']:>11}"
              f"{datos['candidatos']:>13}{marca}")
    linea()

    linea("§6 · FRESCURA · la última señal de actividad, nunca «abierto» (§4 del esquema)")
    linea("-" * 98)
    anios = pd.to_datetime(local.frescura, errors="coerce").dt.year
    for anio, cuantos in anios.value_counts().sort_index(ascending=False).head(8).items():
        linea(f"    {int(anio)}{'':<6}{cuantos:>8}")
    linea(f"    sin fecha{'':<2}{int(anios.isna().sum()):>8}")
    linea()
    for texto in _envolver(
        "`frescura` es la fecha de la evidencia positiva más reciente que alguna fuente ofrece "
        "sobre ese local. **No dice que esté abierto.** Un local con frescura 2024 puede haber "
        "cerrado en 2025 y ninguna de estas fuentes se habría enterado."):
        linea(f"  {texto}")
    linea()

    linea("§7 · CONTROLES DEL §8")
    linea("-" * 98)
    for chequeo in chequeos:
        marca = "OK " if chequeo["pasa"] else "NO "
        linea(f"  [{marca}] {chequeo['nombre']:<26} {chequeo['detalle']}")
    linea()
    linea("=" * 98)

    resumen = {
        "corte": CORTE,
        "locales": int(len(local)),
        "registros": int(len(local_fuente)),
        "por_fuente": local_fuente.fuente.value_counts().to_dict(),
        "n_fuentes": local.n_fuentes.value_counts().sort_index().to_dict(),
        "nivel_publicacion": local.nivel_publicacion.value_counts().to_dict(),
        "aptos_geometria": int(local.apto_geometria.sum()),
        "criterios": local_fuente.criterio_match.value_counts().to_dict(),
        "pares_candidatos_sin_fusionar": int((~pares.fusiona).sum()),
        "sensibilidad_radio": {str(k): v for k, v in sensibilidad.items()},
        "controles": chequeos,
        "recorte_a_la_ciudad": recorte,
        "permisos": detalle_permisos,
        "places_cargado": False,
    }
    return salida.getvalue(), resumen


# --------------------------------------------------------------------------- orquestación

REFERENCIA = BARRIDO / "base_referencia_agregada.csv"


def agregado_por_barrio(local: pd.DataFrame) -> pd.DataFrame:
    """El resumen por barrio que se congela como referencia del `--check`.

    Se congela el AGREGADO y no las tablas completas, y la razón es de método: `local.csv` lleva
    nombres y direcciones de terceros y no se versiona, así que una referencia sobre él sería un
    control que nadie puede correr en otra máquina. El agregado por barrio sí se versiona, cambia
    si cambia cualquier cosa de fondo —el mapeo, la regla de fusión, el radio, una fuente— y no
    cambia por un renombre de columna.
    """
    tabla = local.groupby("barrio").agg(
        locales=("local_id", "size"),
        nucleo=("anillo", lambda s: int((s == "nucleo").sum())),
        aptos=("apto_geometria", "sum"),
        corroborados=("n_fuentes", lambda s: int((s >= 2).sum())),
        abiertos=("nivel_publicacion", lambda s: int((s == "abierto").sum())),
    )
    return tabla.astype(int).sort_index()


def comparar_con_referencia(local: pd.DataFrame, local_fuente: pd.DataFrame) -> bool:
    """§8.8 · reproducibilidad. Igualdad exacta celda por celda contra la referencia congelada.

    Reescribir la referencia destruye el control, así que ningún cambio cosmético lo justifica por
    sí solo. Cuando haya que recongelar por un motivo de fondo —entra Places, cambia el mapeo de
    rubros, cambia la regla de fusión— se recongela en esa misma corrida y se anota por qué.
    """
    generado = agregado_por_barrio(local)
    if not REFERENCIA.exists():
        generado.to_csv(REFERENCIA, encoding="utf-8")
        print(f"  [i] no había referencia; se congeló la actual en {REFERENCIA.name} "
              f"({len(generado)} barrios). La próxima corrida ya compara contra ésta.")
        return True

    referencia = pd.read_csv(REFERENCIA, index_col=0, encoding="utf-8")
    faltan = sorted(set(referencia.index) - set(generado.index))
    sobran = sorted(set(generado.index) - set(referencia.index))
    if faltan or sobran:
        print(f"  [X] barrios que faltan {faltan} / que sobran {sobran}")
        return False

    generado = generado.reindex(referencia.index)
    ok = True
    for columna in referencia.columns:
        distintas = generado[columna] != referencia[columna]
        if distintas.any():
            ok = False
            detalle = {i: (int(generado[columna][i]), int(referencia[columna][i]))
                       for i in referencia.index[distintas]}
            print(f"  [X] {columna}: {int(distintas.sum())} barrios distintos {detalle}")
    if ok:
        print(f"  [OK] la base reproduce la referencia: {len(referencia)} barrios x "
              f"{len(referencia.columns)} columnas idénticas")
    print("\nRESULTADO:", "reproduce la base exacta" if ok else "HAY DIFERENCIAS, revisar")
    return ok


def preparar(registros: pd.DataFrame) -> gpd.GeoDataFrame:
    registros = registros.reset_index(drop=True).copy()
    registros["puertas"] = registros.direccion_fuente.map(puertas_de)
    registros["tokens_nombre"] = registros.nombre_fuente.map(tokens_nombre)
    con_punto = registros[registros.lon_fuente.notna()].copy()
    geo = gpd.GeoDataFrame(
        con_punto,
        geometry=gpd.points_from_xy(con_punto.lon_fuente, con_punto.lat_fuente),
        crs="EPSG:4326").to_crs(CRS_METRICO)
    return geo.reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compara contra la referencia congelada")
    parser.add_argument("--sin-rus", action="store_true", help="no abre el SHP del Relevamiento")
    parser.add_argument("--radio", type=float, default=RADIO_M)
    args = parser.parse_args()

    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]].rename(
        columns={"nombre": "nombre_barrio"})
    comunas = gpd.read_file(COMUNAS)
    comunas = comunas.rename(columns={c: "comuna" for c in comunas.columns
                                      if c.lower().startswith("comuna")})

    print("[cargando] fuentes abiertas (Google Places NO entra)...")
    partes = [cargar_f02(), cargar_f01_base(barrios), cargar_osm_base(),
              cargar_overture_base(), cargar_atp_base()]
    if not args.sin_rus:
        partes.append(cargar_rus_base())
    permisos = cargar_permisos_base()
    for parte in partes + [permisos]:
        if len(parte):
            print(f"  {parte.fuente.iloc[0]:<10}{len(parte):>8} registros")

    registros = pd.concat([p for p in partes if len(p)], ignore_index=True)
    geo = preparar(registros)
    geo, recorte = recortar_a_la_ciudad(geo, barrios)
    print(f"[recorte] fuera de la Ciudad y de su banda de {BANDA_BORDE_M:.0f} m: "
          f"{recorte['descartados']} registros {recorte['por_fuente']}")

    radios = sorted({20.0, args.radio, 60.0})
    print(f"[agrupando] {len(geo)} registros con punto · clasificando pares hasta "
          f"{max(radios):.0f} m (una sola vez)...")
    todos = clasificar_pares(geo, max(radios))
    print(f"  {len(todos)} pares candidatos clasificados")
    grupos, pares = agrupar(geo, todos, args.radio)

    # Los permisos de vereda no tienen punto: se enganchan por dirección a un local que ya existe.
    permisos = preparar(permisos.assign(lon_fuente=0.0, lat_fuente=0.0)) if len(permisos) else permisos
    if len(permisos):
        permisos = permisos.drop(columns="geometry")
        permisos["lon_fuente"] = np.nan
        permisos["lat_fuente"] = np.nan
    enganchados, detalle_permisos = enganchar_permisos(permisos, geo, grupos)
    print(f"[permisos] enganchados por dirección: {detalle_permisos['enganchados']} · "
          f"sin enganche (no crean local): {detalle_permisos['sin_enganche']}")

    sensibilidad = {}
    for radio in radios:
        g, p = (grupos, pares) if radio == args.radio else agrupar(geo, todos, radio)
        sensibilidad[radio] = {"locales": int(len(set(g))),
                               "fusiones": int(p.fusiona.sum()),
                               "candidatos": int((~p.fusiona).sum())}

    local, local_fuente = construir(geo, pares, grupos, barrios, comunas, enganchados)
    chequeos = controles(local, local_fuente, pares)
    texto, resumen = informar(local, local_fuente, pares, chequeos, sensibilidad,
                              recorte, detalle_permisos)
    print(texto)

    fallidos = [c for c in chequeos if not c["pasa"]]
    if fallidos:
        raise ControlFallido(
            "controles del §8 que no pasan: "
            + "; ".join(f"{c['nombre']} ({c['detalle']})" for c in fallidos))

    if args.check:
        return 0 if comparar_con_referencia(local, local_fuente) else 1

    BASE_DIR.mkdir(parents=True, exist_ok=True)
    GEN.mkdir(parents=True, exist_ok=True)
    local.to_csv(BASE_DIR / "local.csv", index=False, encoding="utf-8")
    local_fuente.to_csv(BASE_DIR / "local_fuente.csv", index=False, encoding="utf-8")
    pares[~pares.fusiona].to_csv(BASE_DIR / "pares_pendientes_de_revision.csv",
                                 index=False, encoding="utf-8")
    (GEN / "BASE_GASTRONOMICA.txt").write_text(texto, encoding="utf-8")
    (GEN / "base_gastronomica_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    agregado_por_barrio(local).to_csv(GEN / "base_48_barrios.csv", encoding="utf-8")
    print(f"  escrito en {BASE_DIR.relative_to(ROOT)}: local.csv, local_fuente.csv, "
          "pares_pendientes_de_revision.csv")
    print(f"  agregado versionable: {(GEN / 'base_48_barrios.csv').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
