"""El soporte geométrico de cada fila de la matriz, y los cuatro enclaves comunitarios.

POR QUÉ ESTE MÓDULO EXISTE
---------------------------
Las 94 filas de la matriz **no son objetos del mismo tipo**. Hay polos salidos de un algoritmo,
envolventes dibujadas a mano por el Atlas, barrios administrativos y subzonas sin delimitación
propia. Medir densidad, forma o hitos exige decir sobre **qué** se mide, y esa decisión no puede
quedar escondida adentro de tres scripts distintos: vive acá, se declara una vez y viaja como
columna en toda tabla que salga de este módulo.

El reparto está escrito en `LECTURA_PREVIA.md` §2 y es éste:

    PGR_*                            62   polígono del polo de `borrador_polos_v3.geojson`
    Soho / Hollywood / Cañitas        3   polos P091 / P078 / P065, según DONDE_ESTA_SOHO.txt
    Barrio Chino                      1   el enclave comunitario con límites documentados
    resto con envolvente publicada   20   envolvente editorial del Atlas
    PGF2_*                            6   polígono del barrio (GCBA)
    Bajo Belgrano / Belgrano R        2   SIN SOPORTE — el control las declaró sin resolución

**Lo que no se hace:** inventarle soporte a las dos que no lo tienen. Un barrio entero en lugar de
una subzona sin delimitar no es una aproximación: es atribuirle a la parte lo del todo, que es el
error que el control de ayer evitó a propósito.

LOS CUATRO ENCLAVES
-------------------
Se construyen desde el callejero oficial del GCBA, tramo por tramo, con los límites que dio Diego.
Un tramo es el pedazo de la calle nombrada **entre** sus dos calles de corte, resuelto por
geometría: se proyecta cada cruce sobre el eje de la calle y se corta entre los dos. El buffer
—150 m por convención declarada, una cuadra a cada lado— convierte los tramos en área.

«Las vías» del tramo de Mendoza sale del propio callejero: es el segmento que la columna
`tipo_ffcc` marca como cruce ferroviario. Si no apareciera, se declara y se corta por el extremo,
sin inventar el punto.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiLineString
from shapely.ops import linemerge, unary_union

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

CRS_METRICO = "EPSG:5347"
CRS_GEOGRAFICO = "EPSG:4326"

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
BASE = BARRIDO / "base" / "local.csv"
POLOS_V3 = BARRIDO / "borrador_polos" / "borrador_polos_v3.geojson"
PERTENENCIA = BARRIDO / "borrador_polos" / "pertenencia_local_polo_v3.csv"
ENVOLVENTES = ROOT / "outputs" / "polos_gastro" / "ATLAS_V2" / "capas" / "envolventes_editoriales_v2.geojson"
# La capa de barrios canónica del proyecto, adoptada el 10/08/2026. Tiene procedencia, commit y
# sha256 verificables en `insumos/PROCEDENCIA_capas_administrativas.json`; la anterior no tenía
# ninguno de los tres. El costo está medido y publicado en `ronda_17/impacto_capa_barrios.csv`:
# **siete locales de 23.981 cambian de barrio y doce barrios mueven su conteo, con un neto de +1**.
# La diferencia geométrica es la línea de ribera del Río de la Plata y no lleva locales.
BARRIOS = BARRIDO / "insumos" / "caba_barrios.geojson"
# La anterior queda alcanzable para reproducir cualquier número que ya haya circulado.
BARRIOS_ANTERIOR = ROOT / "data" / "raw" / "geo_barrios.geojson"
CALLEJERO = (ROOT / "outputs" / "polos_gastro" / "FASE5-29" / "fase15_mapas_callejeros_v3" /
             "assets" / "callejero_gcba_2026_06_02.geojson")
MATRIZ = ROOT / "outputs" / "polos_gastro" / "matriz_validacion_polos_gastro.csv"
CONTROL = BARRIDO / "borrador_polos" / "control_matriz_v2.csv"
COTEJO_22 = BARRIDO / "material_metodo" / "cotejo_22_zonas_final.csv"

# Convención declarada en LECTURA_PREVIA §4 (vía D): una cuadra a cada lado del eje.
BUFFER_ENCLAVE_M = 150
CURVA_BUFFER_M = (50, 100, 150, 200, 300)

# La resolución que `DONDE_ESTA_SOHO.txt` ya había dejado escrita. No es una inferencia de acá.
SUBZONAS_PALERMO = {
    "PG001A_PALERMO_SOHO": ("P091", "DONDE_ESTA_SOHO.txt: Soho es P091"),
    "PG001B_PALERMO_HOLLYWOOD": ("P078", "DONDE_ESTA_SOHO.txt: Hollywood es P078"),
    "PG001C_LAS_CANITAS": ("P065", "DONDE_ESTA_SOHO.txt: Cañitas está dentro de P065 (Báez 17/17)"),
}

SIN_SOPORTE = {
    "PG006B_BAJO_BELGRANO": "subzona de Belgrano sin delimitación propia; el control la declaró sin resolución",
    "PG006C_BELGRANO_R": "sub-barrio sin delimitación propia; el control la declaró sin resolución",
}

# Los cuatro enclaves, con los límites tal como los dio Diego. Cada tramo es
# (calle, corte_a, corte_b) con los nombres como los escribe el callejero oficial.
#
# EL FILTRO POR BARRIO NO ES UN AGRUPAMIENTO POR BARRIO. Es lo contrario: las calles del
# callejero corren de punta a punta de la Ciudad —José León Suárez mide 7,3 km y cruza cuatro
# barrios— y sin acotarlas el «tramo» se estira hasta donde el nombre exista. El barrio acá
# recorta el eje al lugar que la propia delimitación nombra («microcentro boliviano **de
# Liniers**»), no define el polo.
ENCLAVES = {
    "Barrio Chino": {
        "barrios": ["Belgrano"],
        "tramos": [
            ("ARRIBEÑOS", "JURAMENTO", "OLAZABAL"),
            ("MENDOZA", "MONTAÑESES", "__VIAS__"),
        ],
    },
    "Barrio Coreano Baek-ku": {
        "barrios": ["Flores"],
        "tramos": [("CARABOBO AV.", "CASTAÑARES AV.", "PERON, EVA AV.")],
    },
    "Pasaje Ruperto Godoy": {
        "barrios": [],
        "tramos": [("GODOY, RUPERTO", "HELGUERA", "CUENCA")],
    },
    # El único de los cuatro que la delimitación NO cierra por los dos lados. Dice «José León
    # Suárez **desde** Rivadavia» y después nombra tres calles sueltas —Falcón, Ibarrola, Gral.
    # Paz— sin decir entre qué y qué. Gral. Paz es el límite de la Ciudad y el barrio ya lo
    # respeta; las otras dos entran enteras dentro de Liniers, y el tamaño que sale queda a la
    # vista para que Diego lo apriete si hace falta. Cerrar el tramo por nuestra cuenta habría
    # sido inventar la delimitación, no leerla.
    "Microcentro boliviano de Liniers": {
        "barrios": ["Liniers"],
        "tramos": [
            ("SUAREZ, JOSE LEON", "RIVADAVIA AV.", None),
            ("FALCON, RAMON L.,CNEL. AV.", None, None),
            ("IBARROLA", None, None),
        ],
    },
}


def sin_tildes(texto: str) -> str:
    limpio = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", limpio)).strip()


def puntos_base() -> gpd.GeoDataFrame:
    """El universo con el que se construyeron los 124 polos. Declarado en LECTURA_PREVIA §1."""
    base = pd.read_csv(BASE)
    universo = base[(base.anillo == "nucleo") & (base.apto_geometria)].copy()
    geo = gpd.GeoDataFrame(
        universo, geometry=gpd.points_from_xy(universo.lon, universo.lat),
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO)
    return geo.reset_index(drop=True)


def envolventes_22() -> gpd.GeoDataFrame:
    """Las 22 tal como se dibujaron, SIN la resta por solape.

    La precedencia de solape existe para contar sin duplicar. Para medir **forma** hay que usar el
    dibujo entero: restarle a R18 lo que comparte con R12 la deja casi vacía y su elongación
    pasaría a describir un recorte que nadie dibujó.
    """
    capa = gpd.read_file(ENVOLVENTES)[
        ["referencia_id", "nombre", "familia", "familia_etiqueta", "geometry"]]
    # La columna `familia` del geojson trae la etiqueta corta —«eje», «polo»— y la que Diego
    # señaló como fuente de la clasificación es la de `cotejo_22_zonas_final.csv`, que trae la
    # larga: «Eje o corredor», «Polo». Se usa esa y se cruza por `referencia_id`. Filtrar por la
    # corta creyendo que decía la larga es cómo esta corrida devolvió, en su primera pasada,
    # cero corredores y cero polos sin tirar ningún error.
    familias = pd.read_csv(COTEJO_22)[["referencia_id", "familia"]].rename(
        columns={"familia": "familia_cotejo"})
    capa = capa.merge(familias, on="referencia_id", how="left")
    faltan = capa[capa.familia_cotejo.isna()]
    if len(faltan):
        raise SystemExit(
            "cotejo_22_zonas_final.csv no tiene familia para: "
            + ", ".join(faltan.referencia_id))
    capa["familia_corta"] = capa.familia
    capa["familia"] = capa.familia_cotejo
    return capa.drop(columns="familia_cotejo").to_crs(CRS_METRICO).sort_values(
        "referencia_id").reset_index(drop=True)


def polos_borrador() -> gpd.GeoDataFrame:
    return gpd.read_file(POLOS_V3).to_crs(CRS_METRICO)


def barrios(anterior: bool = False) -> gpd.GeoDataFrame:
    """Los 48 barrios, con la geometría de la capa oficial y los nombres de siempre.

    LA GEOMETRÍA CAMBIA Y EL NOMBRE NO, Y ESO ES DELIBERADO
    --------------------------------------------------------
    La capa oficial escribe **«BOCA»** donde este proyecto escribe **«La Boca»**, y **«NUÑEZ»**
    donde escribe «Nuñez». Los llamadores de esta función buscan por `clave`, que es
    `sin_tildes(nombre)`: con los nombres de la capa oficial, `sin_tildes("La Boca")` daría
    «LA BOCA» y no encontraría nada. **Y no fallaría**: `capa_barrios[capa_barrios.clave == ...]`
    devuelve un DataFrame vacío y `geometry.get(clave)` devuelve None. Un barrio entero
    desaparecería de una medición sin que nada avisara.

    Por eso `nombre` y `clave` conservan la grafía histórica del proyecto y la geometría es la
    oficial. Quien necesite el nombre tal como lo escribe la fuente lo tiene en `nombre_oficial`.

    El emparejamiento no es una lista escrita a mano: son los 48 pares que
    `ronda_17/nombres_de_barrio.py` resuelve por clave normalizada, verificados en
    `ronda_17/test_capa_de_barrios.py`. El único par que la normalización simple no salva es
    «La Boca» / «BOCA», y lo resuelve la regla del artículo inicial.

    `anterior=True` devuelve la capa que se usaba antes, para reproducir un número ya publicado.
    """
    if anterior:
        capa = gpd.read_file(BARRIOS_ANTERIOR)[["nombre", "geometry"]].to_crs(CRS_METRICO)
        capa["clave"] = capa.nombre.map(sin_tildes)
        capa["nombre_oficial"] = capa.nombre
        return capa

    sys.path.insert(0, str(BARRIDO / "ronda_17"))
    from nombres_de_barrio import clave as _clave_barrio

    oficial = gpd.read_file(BARRIOS).rename(columns={"BARRIO": "nombre_oficial"})
    oficial = oficial[["nombre_oficial", "geometry"]].to_crs(CRS_METRICO)
    historica = gpd.read_file(BARRIOS_ANTERIOR)[["nombre"]]
    por_clave = {_clave_barrio(n): n for n in historica.nombre}

    faltan = [n for n in oficial.nombre_oficial if _clave_barrio(n) not in por_clave]
    if faltan:
        raise SystemExit(
            f"la capa oficial trae barrios que la grafía histórica no tiene: {faltan}. "
            f"No se sigue con un nombre inventado ni con un barrio de menos.")

    oficial["nombre"] = oficial.nombre_oficial.map(lambda n: por_clave[_clave_barrio(n)])
    oficial["clave"] = oficial.nombre.map(sin_tildes)
    return oficial[["nombre", "clave", "nombre_oficial", "geometry"]]


# --------------------------------------------------------------------------- enclaves


def _segmentos_de(calle: str, callejero: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Los segmentos del callejero que llevan ese nombre. Sin unir: la unión es la trampa."""
    return callejero[callejero.clave == sin_tildes(calle)]


def _punto_de_cruce(segmentos: gpd.GeoDataFrame, otra: gpd.GeoDataFrame):
    """Dónde cruza `otra` a la calle: el punto del eje más cercano a ella.

    NO se usa el centroide de la calle que corta. Av. Gral. Paz rodea la Ciudad entera y su
    centroide no está ni cerca de donde cruza a José León Suárez; proyectarlo devolvía un tramo
    de 10 m y la corrida no fallaba, sólo mentía.
    """
    eje = unary_union(list(segmentos.geometry))
    corte = unary_union(list(otra.geometry))
    from shapely.ops import nearest_points
    return nearest_points(eje, corte)[0]


def _tramo_entre(segmentos: gpd.GeoDataFrame, punto_a, punto_b, holgura_m: float = 200.0):
    """Los segmentos que caen entre dos puntos, medidos sobre la recta que los une.

    Trabaja sobre el conjunto de segmentos y **no** sobre un eje unido, porque una calle del
    callejero llega partida —José León Suárez son 66 tramos— y `linemerge` no puede ordenar
    piezas disjuntas: la posición acumulada sale arbitraria. Proyectar cada segmento sobre la
    recta A–B no depende de ningún orden. `holgura_m` tolera que la calle no sea perfectamente
    recta entre los dos cortes.
    """
    ax, ay = punto_a.x, punto_a.y
    dx, dy = punto_b.x - ax, punto_b.y - ay
    largo2 = dx * dx + dy * dy
    if largo2 == 0:
        return None
    elegidos = []
    for geometria in segmentos.geometry:
        centro = geometria.interpolate(0.5, normalized=True)
        t = ((centro.x - ax) * dx + (centro.y - ay) * dy) / largo2
        perpendicular = abs((centro.x - ax) * dy - (centro.y - ay) * dx) / largo2 ** 0.5
        if -0.02 <= t <= 1.02 and perpendicular <= holgura_m:
            elegidos.append(geometria)
    return unary_union(elegidos) if elegidos else None


def construir_enclaves(buffer_m: float = BUFFER_ENCLAVE_M) -> tuple[gpd.GeoDataFrame, list[str]]:
    """Los cuatro enclaves como área, más el registro de cómo se resolvió cada tramo."""
    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)

    # «Las vías»: el cruce ferroviario que el propio callejero marca. No se inventa el punto.
    cruces_ffcc = callejero[callejero.tipo_ffcc.astype(str).str.strip() != "Sin Iteracción"]

    filas, bitacora = [], []
    for enclave, receta in ENCLAVES.items():
        piezas = []
        if receta["barrios"]:
            marco = callejero[callejero.barrio.isin(receta["barrios"])]
        else:
            marco = callejero
        for calle, corte_a, corte_b in receta["tramos"]:
            segmentos = _segmentos_de(calle, marco)
            if segmentos.empty:
                bitacora.append(f"{enclave} · {calle}: NO está en el callejero — tramo omitido")
                continue
            largo_total = float(segmentos.length.sum())

            if corte_a is None and corte_b is None:
                piezas.append(unary_union(list(segmentos.geometry)))
                bitacora.append(
                    f"{enclave} · {calle}: la delimitación la nombra sin decir entre qué y qué; "
                    f"entra entera dentro del marco ({largo_total:,.0f} m)")
                continue

            cruces, faltantes = [], []
            for corte in (corte_a, corte_b):
                if corte is None:
                    # «desde X»: el extremo abierto es el punto de la calle más lejano al cruce.
                    cruces.append("__EXTREMO__")
                    continue
                if corte == "__VIAS__":
                    otra = cruces_ffcc[(cruces_ffcc.clave == sin_tildes(calle)) &
                                       (cruces_ffcc.index.isin(marco.index))]
                    etiqueta = "las vías"
                    if not otra.empty:
                        bitacora.append(
                            f"{enclave} · {calle}: «las vías» = {len(otra)} segmento(s) que el "
                            "callejero marca con cruce ferroviario en tipo_ffcc")
                else:
                    otra = callejero[callejero.clave == sin_tildes(corte)]
                    etiqueta = corte
                if otra.empty:
                    bitacora.append(f"{enclave} · corte «{etiqueta}»: no aparece — se declara")
                    faltantes.append(etiqueta)
                    cruces.append(None)
                    continue
                cruces.append(_punto_de_cruce(segmentos, otra))

            if any(c is None for c in cruces):
                bitacora.append(
                    f"{enclave} · {calle}: falta un corte; se toma la calle entera dentro del "
                    "marco y queda declarado, sin inventar el punto")
                pieza = unary_union(list(segmentos.geometry))
            else:
                if "__EXTREMO__" in cruces:
                    fijo = [c for c in cruces if c != "__EXTREMO__"][0]
                    eje = unary_union(list(segmentos.geometry))
                    puntos = [p for g in (eje.geoms if hasattr(eje, "geoms") else [eje])
                              for p in g.coords]
                    from shapely.geometry import Point
                    lejano = max(puntos, key=lambda c: (c[0] - fijo.x) ** 2 + (c[1] - fijo.y) ** 2)
                    cruces = [fijo, Point(lejano)]
                pieza = _tramo_entre(segmentos, cruces[0], cruces[1])
            if pieza is None or pieza.is_empty:
                bitacora.append(f"{enclave} · {calle}: el tramo salió vacío — se omite")
                continue
            piezas.append(pieza)
            bitacora.append(
                f"{enclave} · {calle} entre {corte_a} y {corte_b}: "
                f"{pieza.length:,.0f} m de eje (la calle dentro del marco: {largo_total:,.0f} m)")

        if not piezas:
            bitacora.append(f"{enclave}: SIN TRAMOS resueltos — no entra a la capa")
            continue
        filas.append({"enclave": enclave, "n_tramos": len(piezas),
                      "largo_eje_m": round(sum(p.length for p in piezas), 1),
                      "geometry": unary_union(piezas).buffer(buffer_m)})

    capa = gpd.GeoDataFrame(filas, geometry="geometry", crs=CRS_METRICO)
    capa["buffer_m"] = buffer_m
    capa["ha"] = (capa.area / 10_000).round(2)
    return capa, bitacora


# --------------------------------------------------------------------------- soportes


def soportes_94() -> gpd.GeoDataFrame:
    """Una fila por fila de la matriz, con su soporte y la procedencia del soporte."""
    matriz = pd.read_csv(MATRIZ)
    control = pd.read_csv(CONTROL)[["polo_id", "envolvente_publicada", "territorio_barrios"]]
    matriz = matriz.merge(control, on="polo_id", how="left")

    polos = polos_borrador().set_index("polo_id")
    envolventes = envolventes_22().set_index("referencia_id")
    capa_barrios = barrios().set_index("clave")
    enclaves, _ = construir_enclaves()
    enclave_chino = enclaves[enclaves.enclave == "Barrio Chino"]

    filas = []
    for fila in matriz.itertuples():
        geometria, clase, detalle = None, "", ""
        if fila.polo_id in SIN_SOPORTE:
            clase, detalle = "sin soporte", SIN_SOPORTE[fila.polo_id]
        elif fila.polo_id in SUBZONAS_PALERMO:
            polo, motivo = SUBZONAS_PALERMO[fila.polo_id]
            geometria, clase, detalle = polos.geometry.get(polo), "polo del borrador", motivo
        elif fila.polo_id == "PG006A_BARRIO_CHINO":
            if not enclave_chino.empty:
                geometria = enclave_chino.geometry.iloc[0]
                clase = "enclave comunitario"
                detalle = "Arribeños entre Juramento y Olazábal; Mendoza entre Montañeses y las vías"
        elif str(fila.polo_id).startswith("PGR_"):
            clave = str(fila.polo_id)[4:]
            geometria = polos.geometry.get(clave)
            clase, detalle = "polo del borrador", f"polo {clave} de borrador_polos_v3"
        elif isinstance(fila.envolvente_publicada, str) and fila.envolvente_publicada.startswith("R"):
            geometria = envolventes.geometry.get(fila.envolvente_publicada)
            clase = "envolvente publicada"
            detalle = f"envolvente editorial {fila.envolvente_publicada} del Atlas"
        elif isinstance(fila.territorio_barrios, str) and fila.territorio_barrios.strip():
            claves = [sin_tildes(b) for b in fila.territorio_barrios.split(";")]
            trozos = [capa_barrios.geometry.get(c) for c in claves]
            trozos = [t for t in trozos if t is not None]
            if trozos:
                geometria = unary_union(trozos)
                clase = "barrio administrativo"
                detalle = f"polígono GCBA de {fila.territorio_barrios}"
        if geometria is None and clase != "sin soporte":
            clase = clase or "sin soporte"
            detalle = detalle or "no se pudo resolver un soporte"
        filas.append({
            "polo_id": fila.polo_id, "nombre_polo": fila.nombre_polo,
            "soporte_clase": clase, "soporte_detalle": detalle, "geometry": geometria,
        })
    return gpd.GeoDataFrame(filas, geometry="geometry", crs=CRS_METRICO)
