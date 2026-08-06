"""Fuentes nuevas del GCBA con coordenada: descarga, perfilado y capa por barrio.

QUÉ ENTRA Y POR QUÉ
-------------------
Seis datasets de BA Data que el proyecto no tenía y que aportan algo que las cuatro fuentes
grandes no dan. Todos con licencia declarada en la ficha del portal y **todos con coordenada o
dirección**, que es la condición para entrar a una base territorial:

| id                       | qué aporta que no teníamos                                        |
|--------------------------|-------------------------------------------------------------------|
| `permisos_gastro`        | mesas y sillas en la vereda. Es el único registro **específicamente
|                          | gastronómico** con fecha de vencimiento: dice hasta cuándo vale    |
| `venta_alimentos`        | puestos callejeros y food trucks — lo que ninguna otra fuente ve   |
| `bailables`              | serie histórica con capacidad declarada y estado                   |
| `espacios_culturales`    | la categoría «bares» de Cultura, que es oferta con programación    |
| `ciclistas`              | comercios adheridos, chico pero con nombre y dirección abiertos    |
| `decks`                  | tramos de calzada gastronómica autorizados. **No son puntos**      |

EL DATO QUE NINGUNA OTRA FUENTE TIENE
-------------------------------------
`permisos_gastro` y `venta_alimentos` traen **fecha de vencimiento de la disposición**. Es la única
afirmación de vigencia con fecha futura que hay en todo el conjunto de fuentes: el padrón no
registra bajas, el Relevamiento es una foto, OSM dice cuándo se editó y Places dice qué ve hoy.
Un permiso vigente al día de hoy es evidencia positiva fechada, que es exactamente lo que el
esquema pide para `frescura` (§4). No dice que el local esté abierto —dice que alguien pagó por
tener mesas en la vereda hasta tal fecha—, y así se reporta.

PRIVACIDAD · LA LISTA PERMITIDA, NO LA LISTA PROHIBIDA
-------------------------------------------------------
Cuatro de los seis traen datos personales: `titular`, `DNI_CUIT`, `nro_documento`, `TELEFONO`,
`MAIL`, `email`, `Apellido`. **Ninguna de esas columnas se abre.** Cada fuente declara su lista de
columnas permitidas y el `usecols` de pandas se arma desde esa lista, con el mismo criterio que
`detectar_lotes_permisos.py` aplica al padrón: lo prohibido no entra en memoria, no se filtra
después. Y hay un control que corta la corrida si una columna prohibida aparece en la salida.

TRAMPAS DE ESTOS ARCHIVOS, ENCONTRADAS Y RESUELTAS
---------------------------------------------------
- **`venta_alimentos` viene mal escapado en CSV** y rompe cualquier parser ingenuo. Se lee el XLSX,
  que el portal publica con el mismo contenido y sin el defecto. Si algún día hace falta el CSV,
  el fallback está escrito y declarado.
- **Nombres de columna con tabuladores adentro** (`CAPACIDAD_TOTAL\\t`, `ESTABLECIMIENTO\\t`,
  `id\\t`): los encabezados se normalizan al leer o la columna no existe con el nombre que uno cree.
- **`decks` no son puntos**: son tramos de calle con altura inicial y final por vereda. Entran como
  contexto territorial, no como locales, y no se suman a ningún conteo de POI.
- **`fiscalizaciones` no entra acá**: su unidad es la inspección, no el local, y hay que colapsar
  por parcela antes de que signifique algo. Queda anotada, no cargada.

USO
---
  python scripts/barrido_ciudad/bajar_fuentes_gcba.py            # baja lo que falte y perfila
  python scripts/barrido_ciudad/bajar_fuentes_gcba.py --reinformar   # perfila desde el disco
  python scripts/barrido_ciudad/bajar_fuentes_gcba.py --fuente permisos_gastro
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
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
GCBA_DIR = ROOT / "outputs" / "fuentes_externas" / "gcba_nuevas"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
CAPA_PADRON = BARRIDO / "capa_homogenea_48_barrios.csv"

USER_AGENT = "DataGastro/barrido-ciudad (DGDGAS, uso institucional CABA)"

# Columnas prohibidas en cualquier salida. El control las busca por nombre plegado, así que
# `DNI_CUIT`, `dni_cuit` y `nro_documento` caen todas.
PROHIBIDAS = ["titular", "cuit", "cuil", "dni", "documento", "telefono", "mail", "email",
              "apellido", "razon_social", "web", "facebook", "twitter", "instagram"]

CDN = "https://cdn.buenosaires.gob.ar/datosabiertos/datasets"

# --- Las seis fuentes, declaradas ---------------------------------------------------------
# `columnas`: la lista PERMITIDA. Todo lo que no esté acá no se lee.
# `lon`/`lat`: nombres de las columnas de coordenada ya normalizados, o None si no tiene punto.
FUENTES: dict[str, dict] = {
    "permisos_gastro": {
        "titulo": "Permisos Uso Espacio Público · Área gastronómica",
        "organismo": "Secretaría de Atención Ciudadana",
        "licencia": "CC-BY-2.5-AR",
        "url": f"{CDN}/atencion-ciudadana/permisos-uso-espacio-publico-area-gastronomica/"
               "permisos-uso-espacio-publico-gastronomicos.xlsx",
        "archivo": "permisos_gastronomicos.xlsx",
        "formato": "xlsx",
        # Las columnas son las del archivo publicado hoy, verificadas abriéndolo. La ficha de
        # CKAN describe otras —incluidas `x` e `y`— y está desactualizada. Ver §6 del informe.
        "columnas": ["AÑO", "Expediente", "Dirección", "Altura", "Barrio", "Comuna",
                     "Estado Vereda", "N° de Dispo / Reso", "Fecha de Inicio",
                     "Fecha de Vencimiento"],
        "lon": None, "lat": None,
        "calle": "Dirección", "altura": "Altura", "barrio_declarado": "Barrio",
        "vencimiento": "Fecha de Vencimiento",
        "estado": "Estado Vereda",
        "que_mide": "permisos de mesas y sillas en la vereda, con fecha de vencimiento y estado",
        "que_no_mide": "no es un padrón de locales: sólo los que pidieron permiso de vereda",
    },
    "venta_alimentos": {
        "titulo": "Permisos para la venta de alimentos en el espacio público",
        "organismo": "Secretaría de Atención Ciudadana",
        "licencia": "CC-BY (Creative Commons Attribution)",
        "url": f"{CDN}/atencion-ciudadana/venta-de-alimentos/permisos_alimentos.xlsx",
        "archivo": "permisos_alimentos.xlsx",
        "formato": "xlsx",
        "columnas": ["AÑO", "Nº DE EXPEDIENTE", "CATEGORIA", "LOCACION", "BARRIO", "Comuna",
                     "Estado", "N° de Dispo / Reso", "Fecha de Inicio", "Fecha de Vencimiento"],
        "lon": None, "lat": None,
        "barrio_declarado": "BARRIO",
        "vencimiento": "Fecha de Vencimiento",
        "estado": "Estado",
        "que_mide": "permisos de venta de alimentos en la vía pública: puestos y food trucks",
        "que_no_mide": "no cubre locales a la calle; y su ubicación es un topónimo "
                       "(`COSTANERA SUR`), no una dirección: no se puede llevar a un punto",
        "nota_csv": "el CSV del portal viene en latin-1, separado por `;` y con columnas "
                    "sobrantes al final de cada fila; se usa el XLSX, mismo contenido",
    },
    "bailables": {
        "titulo": "Locales Bailables · registro histórico acumulado",
        "organismo": "Agencia Gubernamental de Control (AGC)",
        "licencia": "CC-BY-2.5-AR",
        "url": f"{CDN}/agencia-gubernamental-de-control/locales-bailables/"
               "registro-historico-acumulado-de-locales-bailables.csv",
        "archivo": "locales_bailables_historico.csv",
        "formato": "csv",
        "columnas": ["periodo", "nombre", "longitud", "latitud", "direccion", "piso", "barrio",
                     "comuna", "capacidad", "clase", "estado", "vencimiento", "numero_registro",
                     "numero_expediente"],
        "lon": "longitud", "lat": "latitud",
        "vencimiento": "vencimiento",
        # El «registro histórico acumulado» es una foto por período: el mismo local aparece una vez
        # por corte. Sin colapsar, Palermo daba 14.080 locales bailables, que es absurdo y se nota;
        # lo que no se nota es el error equivalente en un barrio chico. Se colapsa por número de
        # registro y se conserva el período más reciente de cada uno.
        "colapsar_por": "numero_registro",
        "colapsar_orden": "periodo",
        "que_mide": "locales bailables inscriptos, con capacidad declarada y estado del registro",
        "que_no_mide": "no es gastronomía: es nocturnidad. Entra como contexto, no al anillo",
    },
    "espacios_culturales": {
        "titulo": "Espacios culturales",
        "organismo": "Ministerio de Cultura",
        "licencia": "CC-BY-2.5-AR",
        "url": f"{CDN}/ministerio-de-cultura/espacios-culturales/espacios-culturales.csv",
        "archivo": "espacios_culturales.csv",
        "formato": "csv",
        "columnas": ["fid", "FUNCION_PRINCIPAL", "SUBCATEGORIA", "ESTABLECIMIENTO",
                     "FUNCION_SECUNDARIA", "CALLE", "ALTURA", "BARRIO", "COMUNA", "DIRECCION",
                     "LONGITUD", "LATITUD", "CAPACIDAD_TOTAL", "CANTIDAD_SALAS"],
        "lon": "LONGITUD", "lat": "LATITUD",
        "vencimiento": None,
        "que_mide": "espacios culturales relevados por Cultura; incluye la subcategoría bares",
        "que_no_mide": "no es un padrón gastronómico: el bar entra si tiene programación cultural",
    },
    "ciclistas": {
        "titulo": "Comercios con beneficios a ciclistas",
        "organismo": "Secretaría de Transporte y Obras Públicas",
        "licencia": "CC-BY-2.5-AR",
        "url": f"{CDN}/transporte-y-obras-publicas/comercios-con-beneficios-ciclistas/"
               "comercios-con-beneficios-a-ciclistas.geojson",
        "archivo": "comercios_ciclistas.geojson",
        "formato": "geojson",
        "columnas": ["id", "nombre", "estacionam", "beneficio", "calle", "altura", "calle2",
                     "direccion_", "barrio", "comuna"],
        "lon": None, "lat": None,
        "vencimiento": None,
        "que_mide": "comercios adheridos al programa de beneficios a ciclistas",
        "que_no_mide": "es una adhesión voluntaria a un programa, no un universo de comercios",
    },
    "decks": {
        "titulo": "Expansión de calzada gastronómica (decks)",
        "organismo": "Secretaría de Transporte y Obras Públicas",
        "licencia": "CC-BY-2.5-AR",
        "url": f"{CDN}/transporte-y-obras-publicas/calzada-gastronomica/"
               "decks_permitidos_WGS84.geojson",
        "archivo": "decks_gastronomicos.geojson",
        "formato": "geojson",
        "columnas": ["NOMOFICIAL", "ALT_DERINI", "ALT_DERFIN", "ALT_IZQINI", "ALT_IZQFIN",
                     "COMUNA", "BARRIO"],
        "lon": None, "lat": None,
        "vencimiento": None,
        "es_tramo": True,
        "que_mide": "tramos de calzada donde se autorizó expansión gastronómica",
        "que_no_mide": "no son locales ni puntos: son segmentos de calle con rango de altura",
    },
}

# Anotada y NO cargada: su unidad no es el local. Queda escrito para que la próxima persona no
# tenga que redescubrirlo abriendo doce archivos.
NO_CARGADAS = {
    "fiscalizaciones": "una fila por inspección, no por local. Las cohortes 2020-2025 traen "
                       "sección/manzana/parcela y ninguna coordenada; las de 2018-2019 sí traen "
                       "long/lat. Sirve para vigencia por parcela DESPUÉS de colapsar por SMP, "
                       "y ese colapso es trabajo propio que no se hace de paso.",
    "vigiladores-locales-bailables": "registro de personas, no de locales. No entra.",
    "capacitadores-manipuladores-alimentos": "registro de personas. No entra.",
}


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper().strip()


def plegar_bajo(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower().strip()


class ColumnaProhibida(RuntimeError):
    """Una columna con datos personales se coló en una salida."""


def control_privacidad(tabla: pd.DataFrame, donde: str) -> None:
    """Control que corta: ninguna salida puede llevar una columna de la lista prohibida."""
    culpables = [c for c in tabla.columns
                 if any(p in plegar_bajo(c) for p in PROHIBIDAS)]
    if culpables:
        raise ColumnaProhibida(
            f"{donde}: columnas con datos personales en la salida: {culpables}. "
            "La lista permitida de la fuente está mal declarada; no se escribe nada."
        )


# --------------------------------------------------------------------------- descarga

def bajar(clave: str, ficha: dict) -> Path:
    destino = GCBA_DIR / ficha["archivo"]
    if destino.exists():
        print(f"  [{clave}] ya está en disco ({destino.stat().st_size / 1e3:.0f} KB)")
        return destino
    GCBA_DIR.mkdir(parents=True, exist_ok=True)
    pedido = urllib.request.Request(ficha["url"], headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(pedido, timeout=180) as respuesta:  # noqa: S310
        destino.write_bytes(respuesta.read())
    print(f"  [{clave}] bajado · {destino.stat().st_size / 1e3:.0f} KB")
    return destino


def normalizar_encabezados(tabla: pd.DataFrame) -> pd.DataFrame:
    """Los encabezados vienen con tabuladores y espacios adentro. Sin esto, la columna no existe."""
    tabla.columns = [str(c).replace("\t", "").strip() for c in tabla.columns]
    return tabla


def leer(clave: str, ficha: dict, archivo: Path) -> gpd.GeoDataFrame:
    """Lee sólo las columnas permitidas y devuelve la capa ya georreferenciada."""
    permitidas = ficha["columnas"]

    if ficha["formato"] == "geojson":
        capa = gpd.read_file(archivo)
        capa = normalizar_encabezados(capa)
        presentes = [c for c in permitidas if c in capa.columns]
        capa = capa[presentes + ["geometry"]]
        if capa.crs is None:
            capa = capa.set_crs("EPSG:4326")
        return capa.to_crs("EPSG:4326")

    if ficha["formato"] == "xlsx":
        cruda = normalizar_encabezados(pd.read_excel(archivo, dtype=str))
    else:
        cruda = None
        for codificacion in ("utf-8", "latin-1"):
            for separador in (",", ";"):
                try:
                    intento = pd.read_csv(archivo, dtype=str, encoding=codificacion,
                                          sep=separador, low_memory=False)
                except (UnicodeDecodeError, ValueError):
                    continue
                if intento.shape[1] > 1:
                    cruda = normalizar_encabezados(intento)
                    break
            if cruda is not None:
                break
        if cruda is None:
            raise SystemExit(f"ABORTADO: no se pudo leer {archivo.name} con ninguna combinación.")

    presentes = [c for c in permitidas if c in cruda.columns]
    faltantes = [c for c in permitidas if c not in cruda.columns]
    if faltantes:
        print(f"    [{clave}] aviso: la fuente ya no trae {faltantes}")
    tabla = cruda[presentes].copy()

    lon, lat = ficha.get("lon"), ficha.get("lat")
    if lon and lat and lon in tabla.columns and lat in tabla.columns:
        # Las coordenadas llegan como texto y a veces con coma decimal. La máscara se calcula una
        # sola vez y se aplica a las tres series: filtrar la tabla por un lado y hacer `dropna()`
        # por otro da largos distintos en cuanto una fila tenga sólo una de las dos coordenadas.
        x = pd.to_numeric(tabla[lon].astype(str).str.replace(",", "."), errors="coerce")
        y = pd.to_numeric(tabla[lat].astype(str).str.replace(",", "."), errors="coerce")
        con_punto = x.notna() & y.notna()
        tabla = tabla[con_punto].copy()
        return gpd.GeoDataFrame(
            tabla, geometry=gpd.points_from_xy(x[con_punto], y[con_punto]), crs="EPSG:4326")
    return gpd.GeoDataFrame(tabla, geometry=gpd.GeoSeries([None] * len(tabla)), crs="EPSG:4326")


# --------------------------------------------------------------------------- perfilado

def colapsar(clave: str, ficha: dict, capa: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Una fila por local cuando la fuente publica una foto por período.

    La unidad de la base es el local, no el corte administrativo. Una fuente que repite el mismo
    local en cada período no está diciendo que haya más locales; contar sus filas es el error de
    unidad que el método de comparabilidad viene evitando desde la regla 1.
    """
    llave = ficha.get("colapsar_por")
    if not llave or llave not in capa.columns:
        return capa
    orden = ficha.get("colapsar_orden")
    antes = len(capa)
    ordenada = capa.sort_values(orden) if orden and orden in capa.columns else capa
    colapsada = ordenada.drop_duplicates(subset=llave, keep="last").copy()
    colapsada.attrs["filas_antes_de_colapsar"] = antes
    print(f"    [{clave}] colapsado por `{llave}`: {antes} filas -> {len(colapsada)} locales")
    return colapsada


def modo_ubicacion(ficha: dict, capa: gpd.GeoDataFrame) -> str:
    """Con qué precisión se puede ubicar cada fila de esta fuente. Decide `apto_geometria`."""
    if capa.geometry.notna().any() and not capa.geometry.isna().all():
        return "punto"
    if ficha.get("calle"):
        return "direccion"
    if ficha.get("barrio_declarado"):
        return "barrio"
    return "sin_ubicacion"


def barrios_oficiales(barrios: gpd.GeoDataFrame) -> dict[str, str]:
    return {plegar(n): n for n in barrios.nombre_barrio}


def perfilar(clave: str, ficha: dict, capa: gpd.GeoDataFrame, barrios: gpd.GeoDataFrame,
             oficiales: dict[str, str]) -> tuple[dict, pd.DataFrame | None]:
    """Cuántas filas, con qué precisión se ubican, cuántas vigentes y el reparto por barrio."""
    modo = modo_ubicacion(ficha, capa)
    perfil = {
        "fuente": clave,
        "titulo": ficha["titulo"],
        "organismo": ficha["organismo"],
        "licencia": ficha["licencia"],
        "que_mide": ficha["que_mide"],
        "que_no_mide": ficha["que_no_mide"],
        "filas": int(len(capa)),
        "modo_ubicacion": modo,
        "es_tramo": bool(ficha.get("es_tramo")),
    }
    if "filas_antes_de_colapsar" in capa.attrs:
        perfil["filas_antes_de_colapsar"] = int(capa.attrs["filas_antes_de_colapsar"])
        perfil["colapsado_por"] = ficha.get("colapsar_por")

    columna_vto = ficha.get("vencimiento")
    if columna_vto and columna_vto in capa.columns:
        vencimientos = pd.to_datetime(capa[columna_vto], errors="coerce", dayfirst=True)
        hoy = pd.Timestamp(dt.date.today())
        perfil["con_fecha_de_vencimiento"] = int(vencimientos.notna().sum())
        perfil["vigentes_hoy"] = int((vencimientos >= hoy).sum())
        perfil["vencidos"] = int((vencimientos < hoy).sum())
        if vencimientos.notna().any():
            perfil["vencimiento_maximo"] = str(vencimientos.max().date())

    columna_estado = ficha.get("estado")
    if columna_estado and columna_estado in capa.columns:
        perfil["estados"] = capa[columna_estado].value_counts().head(8).to_dict()

    if modo == "punto":
        con_geometria = capa[capa.geometry.notna() & ~capa.geometry.is_empty]
        perfil["con_geometria"] = int(len(con_geometria))
        asignados = gpd.sjoin(con_geometria, barrios[["nombre_barrio", "geometry"]],
                              how="left", predicate="intersects")
        # Un tramo puede cruzar dos barrios y el `sjoin` lo devuelve dos veces: para el conteo por
        # barrio eso es correcto, para el total de la fuente no. Se declaran los dos números.
        perfil["dentro_de_la_ciudad"] = int(asignados.nombre_barrio.notna().sum())
        perfil["registros_distintos_asignados"] = int(
            asignados[asignados.nombre_barrio.notna()].index.nunique())
        conteo = (asignados[asignados.nombre_barrio.notna()]
                  .groupby("nombre_barrio").size().rename(f"{clave}_registros"))
        conteo.index = [plegar(i) for i in conteo.index]
        return perfil, conteo.to_frame()

    # Sin coordenada: el barrio se toma del campo declarado y se VALIDA contra los 48 oficiales.
    # No es lo mismo que la asignación por geometría y no se lo presenta como si lo fuera: acá el
    # barrio lo afirma la fuente, y lo único que este paso comprueba es que el nombre exista.
    columna_barrio = ficha.get("barrio_declarado")
    perfil["con_geometria"] = 0
    if not columna_barrio or columna_barrio not in capa.columns:
        return perfil, None

    declarado = capa[columna_barrio].map(plegar)
    reconocido = declarado.map(lambda b: b in oficiales)
    perfil["barrio_declarado_reconocido"] = int(reconocido.sum())
    perfil["barrio_declarado_desconocido"] = sorted(
        set(declarado[~reconocido].dropna()))[:10]
    if ficha.get("calle"):
        con_calle = capa[ficha["calle"]].fillna("").astype(str).str.strip() != ""
        perfil["con_calle_y_altura"] = int(
            (con_calle & (capa[ficha["altura"]].fillna("").astype(str).str.strip() != "")).sum())

    conteo = declarado[reconocido].value_counts().rename(f"{clave}_registros")
    return perfil, conteo.to_frame()


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


def informar(perfiles: list[dict], tabla_barrios: pd.DataFrame) -> str:
    salida = io.StringIO()

    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    linea("=" * 98)
    linea("FUENTES NUEVAS DEL GCBA CON COORDENADA · descarga y perfilado")
    linea("=" * 98)
    linea(f"fecha {dt.date.today().isoformat()} · todas con licencia abierta declarada en BA Data")
    linea()

    linea("§1 · QUÉ TRAJO CADA UNA")
    linea("-" * 98)
    linea(f"  {'fuente':<22}{'filas':>8}{'con punto':>11}{'ubicación':>13}   licencia")
    for perfil in perfiles:
        linea(f"  {perfil['fuente']:<22}{perfil['filas']:>8}{perfil.get('con_geometria', 0):>11}"
              f"{perfil.get('modo_ubicacion', '?'):>13}   {perfil['licencia']}")
    linea()
    for perfil in perfiles:
        linea(f"  · {perfil['titulo']}")
        linea(f"    mide      : {perfil['que_mide']}")
        linea(f"    NO mide   : {perfil['que_no_mide']}")
        if "vigentes_hoy" in perfil:
            linea(f"    vigencia  : {perfil['vigentes_hoy']} vigentes hoy · "
                  f"{perfil['vencidos']} vencidos · último vencimiento "
                  f"{perfil.get('vencimiento_maximo', 's/d')}")
        if "estados" in perfil:
            linea(f"    estado    : " + " · ".join(f"{k} {v}" for k, v in perfil["estados"].items()))
        if perfil.get("modo_ubicacion") == "direccion":
            linea(f"    ubicación : calle y altura en {perfil.get('con_calle_y_altura', 0)} filas; "
                  "hay que geocodificar con USIG antes de que sirva para dibujar")
        elif perfil.get("modo_ubicacion") == "barrio":
            linea("    ubicación : sólo barrio declarado. No se puede llevar a un punto")
        linea()

    linea("§2 · LA VIGENCIA CON FECHA, QUE ES LO QUE NINGUNA OTRA FUENTE TIENE")
    linea("-" * 98)
    con_vto = [p for p in perfiles if "vigentes_hoy" in p]
    if con_vto:
        for perfil in con_vto:
            total = perfil.get("con_fecha_de_vencimiento", 0)
            if total:
                linea(f"  {perfil['fuente']:<22}{perfil['vigentes_hoy']:>6} vigentes de {total:>6}"
                      f"  ({_coma(100 * perfil['vigentes_hoy'] / total)} %)")
        linea()
        for texto in _envolver(
            "Un permiso vigente es **evidencia positiva fechada**, que es lo que el esquema pide "
            "para `frescura` (§4). Y hay que decir exactamente qué evidencia es: dice que alguien "
            "pagó por tener mesas en la vereda hasta tal fecha, no que el local esté abierto hoy. "
            "La diferencia se sostiene en el vocabulario o el campo deja de significar nada."):
            linea(f"  {texto}")
    else:
        linea("  Ninguna de las fuentes cargadas trae fecha de vencimiento legible.")
    linea()

    linea("§3 · REPARTO POR BARRIO")
    linea("-" * 98)
    if tabla_barrios is not None and len(tabla_barrios):
        columnas = [c for c in tabla_barrios.columns if c.endswith("_registros")]
        ordenada = tabla_barrios.sort_values(columnas[0], ascending=False) if columnas else tabla_barrios
        linea(ordenada.head(15).fillna(0).astype(int).to_string())
        linea()
        linea("  (48 barrios completos en el CSV; acá van los 15 primeros)")
    linea()

    linea("§4 · LO QUE SE MIRÓ Y NO SE CARGÓ, CON EL MOTIVO")
    linea("-" * 98)
    for clave, motivo in NO_CARGADAS.items():
        linea(f"  · {clave}")
        for texto in _envolver(motivo, 92):
            linea(f"      {texto}")
    linea()

    linea("§5 · LA FICHA DE CKAN NO COINCIDE CON EL ARCHIVO, Y HAY QUE SABERLO")
    linea("-" * 98)
    for texto in _envolver(
        "La ficha del portal declara para los dos padrones de permisos columnas de coordenada "
        "—`x`/`y` en el gastronómico, `lat`/`long` en el de alimentos—. **Los archivos publicados "
        "hoy no las traen.** El gastronómico trae `Dirección` y `Altura`, que sirven pero hay que "
        "geocodificar; el de alimentos trae un topónimo (`COSTANERA SUR`) y el barrio, y no se "
        "puede llevar a un punto sin un criterio propio."):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        "No es un defecto de estas dos fuentes: es un aviso sobre el método. El barrido del "
        "catálogo por API lee `attributesDescription`, que es metadato declarado, no el archivo. "
        "Sirve para ordenar 453 datasets y decidir cuáles abrir; **no sirve para afirmar que un "
        "dataset tiene coordenadas**. Eso se comprueba abriéndolo, y por eso el inventario ordena "
        "candidatos en vez de decidir integraciones."):
        linea(f"  {texto}")
    linea()

    linea("§6 · PRIVACIDAD")
    linea("-" * 98)
    for texto in _envolver(
        "Cuatro de estas fuentes traen datos personales —`titular`, `DNI_CUIT`, `nro_documento`, "
        "`TELEFONO`, `MAIL`—. Ninguna de esas columnas se abrió: cada fuente declara su lista de "
        "columnas permitidas y el `usecols` se arma desde ahí, así que lo prohibido no entra en "
        "memoria. Hay además un control que corta la corrida si una columna prohibida aparece en "
        "una salida, y este informe no se habría escrito si hubiera saltado."):
        linea(f"  {texto}")
    linea()
    linea("=" * 98)
    return salida.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reinformar", action="store_true",
                        help="perfila desde los archivos ya bajados, sin red")
    parser.add_argument("--fuente", default=None, help="perfila una sola fuente")
    args = parser.parse_args()

    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]].rename(
        columns={"nombre": "nombre_barrio"})
    oficiales = barrios_oficiales(barrios)
    claves = [args.fuente] if args.fuente else list(FUENTES)

    perfiles, conteos = [], []
    for clave in claves:
        ficha = FUENTES[clave]
        archivo = GCBA_DIR / ficha["archivo"]
        if not args.reinformar:
            archivo = bajar(clave, ficha)
        if not archivo.exists():
            print(f"  [{clave}] falta {archivo.name}; se saltea")
            continue
        capa = leer(clave, ficha, archivo)
        capa = colapsar(clave, ficha, capa)
        control_privacidad(capa.drop(columns="geometry", errors="ignore"), clave)
        perfil, conteo = perfilar(clave, ficha, capa, barrios, oficiales)
        perfiles.append(perfil)
        if conteo is not None:
            conteos.append(conteo)

        GCBA_DIR.mkdir(parents=True, exist_ok=True)
        salida = capa.copy()
        if "geometry" in salida and salida.geometry.notna().any():
            salida["lon"] = salida.geometry.centroid.x
            salida["lat"] = salida.geometry.centroid.y
        salida = salida.drop(columns="geometry", errors="ignore")
        control_privacidad(salida, f"{clave} (salida)")
        salida.to_csv(GCBA_DIR / f"{clave}_limpio.csv", index=False, encoding="utf-8-sig")

    tabla_barrios = pd.concat(conteos, axis=1) if conteos else pd.DataFrame()
    if len(tabla_barrios):
        padron = pd.read_csv(CAPA_PADRON, index_col=0, encoding="utf-8")
        padron.index = [plegar(i) for i in padron.index]
        tabla_barrios = tabla_barrios.join(padron[["dir_nucleo"]])

    texto = informar(perfiles, tabla_barrios)
    print(texto)

    GEN.mkdir(parents=True, exist_ok=True)
    if len(tabla_barrios):
        tabla_barrios.to_csv(GEN / "gcba_nuevas_48_barrios.csv", encoding="utf-8")
    (GEN / "FUENTES_GCBA_NUEVAS.txt").write_text(texto, encoding="utf-8")
    (GEN / "gcba_nuevas_resumen.json").write_text(
        json.dumps({"fecha_calculo": dt.date.today().isoformat(), "fuentes": perfiles,
                    "no_cargadas": NO_CARGADAS}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  publicado en {GEN.relative_to(ROOT)}: gcba_nuevas_48_barrios.csv, "
          "FUENTES_GCBA_NUEVAS.txt, gcba_nuevas_resumen.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
