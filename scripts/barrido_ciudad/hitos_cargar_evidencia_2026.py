"""La capa de hitos 2026: direcciones que faltaban, patrimonio normativo y vigencia verificada.

QUÉ CIERRA
----------
Los tres huecos que la corrida de las seis vías dejó a la vista, con la evidencia que Diego
levantó el 2026-08-07 (`desde_cowork/evidencia_2026/`):

  1 · las 20 pizzerías y 5 heladerías que no tenían **ninguna** coordenada;
  2 · `patrimonio_normativo`, que tenía 2 hitos en toda la Ciudad y pasa a 10;
  3 · `vigencia_verificada`, que no existía — y sin ella una declaratoria de 1998 se lee como
      prueba de que el local abre hoy.

Y produce la capa vigente en disco (`hitos_capa_2026.csv/geojson`), que es la que leen las seis
vías. `hitos_capa_unificada.csv` **queda intacto**: es el estado contra el que se compara.

LAS TRES DECISIONES QUE ESTE SCRIPT NO TOMA
--------------------------------------------
**Los cinco conflictos de dirección no se resuelven.** Se cargan las dos —o las tres— variantes,
se geocodifican todas y se mide **la distancia entre ellas**, que es lo único que cambia algo:
un conflicto de 20 m no mueve a ningún local de polígono y uno de 900 m sí. Medir la consecuencia
no es elegir el ganador.

**El Fortín se georreferencia por esquina.** El GCBA confirma Lope de Vega y Álvarez Jonte y la
Comuna 10 pero no publica altura; el 5299 sale sólo de agregadores. La altura queda **vacía** y el
método queda anotado.

**Lo que no se verificó no se declara vigente.** `vigencia_verificada` toma `si`, `no` o `dudosa`
sólo donde hay evidencia, y `sin_verificar` en todo lo demás. Poner `si` por omisión sería
exactamente el error que Los Laureles acaba de demostrar: el circuito oficial lo sigue publicando
y el bar cerró en julio de 2026.

Google Places: 0 requests. USIG sí: es el geocodificador oficial, gratuito y sin credenciales.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/hitos_cargar_evidencia_2026.py
"""
from __future__ import annotations

import io
import json
import re
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

from dataset_bares_notables import CACHE, consultar, limpiar  # noqa: E402
from hitos_cruzar_bares_notables import clave_domicilio, plegar_nombre  # noqa: E402
from polos_soporte import CRS_GEOGRAFICO, CRS_METRICO  # noqa: E402

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
HITOS = BARRIDO / "hitos"
EVIDENCIA = BARRIDO / "desde_cowork" / "evidencia_2026"

# ---------------------------------------------------------------- lo transcripto a mano, a la vista
#
# Las variantes salen de la columna `nota` del CSV y del mensaje de Diego, que están en prosa. Se
# transcriben acá en vez de parsearlas: una expresión regular sobre texto libre es una decisión
# escondida, y estas cinco son justamente las que no hay que decidir solas.
VARIANTES = {
    "La Mezzetta": [
        ("Av. Alvarez Thomas 1321", "prensa (Cronista)", "Villa Ortuzar"),
        ("Av. Alvarez Thomas 1311", "GCBA", "Chacarita"),
    ],
    "Banchero": [
        ("Suarez 396", "GCBA", "La Boca"),
        ("Av. Almirante Brown 1220", "canal26", "La Boca"),
    ],
    "Saverio Helados": [
        ("Av. San Juan 2809", "oficial", "San Cristobal"),
        ("Av. San Juan 2816", "La Nacion", "San Cristobal"),
        ("Av. San Juan 2727", "fundacional (YA NO OPERA)", "San Cristobal"),
    ],
    "San Carlos": [
        ("Av. Rivadavia 4548", "dos fuentes", "Caballito"),
        ("Av. Rivadavia y Av. La Plata", "prensa (descripcion)", "Caballito"),
    ],
    # La Americana no tiene dos direcciones: tiene dos comunas. Se registra como conflicto de
    # atribución, sin segundo punto, porque inventar uno sería fabricar el conflicto.
    "La Americana": [
        ("Av. Callao 83", "sitio oficial · Comuna 3", "Balvanera"),
    ],
}

GEOCODIFICAR_POR_ESQUINA = {"El Fortin": "Av. Alvarez Jonte y Av. Lope de Vega"}

# Dos fichas con el mismo nombre plegado son el mismo local si sus puntos caen a menos de esto.
# Convención: la manzana de la Ciudad mide ~100 m, así que 150 m tolera que el local tenga dos
# frentes asentados en calles distintas y no llega a juntar dos locales de barrios distintos.
DISTANCIA_MISMO_LOCAL_M = 150

# ---------------------------------------------------------------- Tarea 3, la evidencia de vigencia
#
# `si` / `no` / `dudosa` sólo donde hay evidencia. El resto queda `sin_verificar`, que es un cuarto
# valor y está a propósito: los tres del enunciado suponen que alguien miró, y en 200 hitos nadie
# miró. Un `si` por omisión sería la afirmación más cara de la tabla.
VIGENCIA = {
    ("LOS LAURELES", "IRIARTE"): (
        "no", "cerró a fines de julio de 2026; el circuito gastronómico oficial del GCBA lo "
        "sigue publicando", "2026-08-07"),
    ("BAR OVIEDO", "DE LA TORRE"): (
        "dudosa", "catálogo oficial lo lista y APH 21 lo protege, pero la última observación de "
        "campo del GCBA es de enero de 2013 y no participó de la Noche de los Bares Notables "
        "2025 mientras Del Glorias y 9 de Julio sí", "2026-08-07"),
    ("PENA LOS AMIGOS BAR EL CHINO", "BEAZLEY"): (
        "dudosa", "Sitio de Interés Cultural 1999; sin cobertura posterior a 2017", "2026-08-07"),
    ("CASA BURGIO", "CABILDO"): (
        "si", "operativa; cerró en 2021 y reabrió en octubre de 2022 con otro dueño",
        "2026-08-07"),
}

# Continuidad ≠ vigencia. Casa Burgio abre hoy y su antigüedad NO es ininterrumpida; si el Atlas
# publica años de trayectoria, ese matiz cambia la cifra.
CONTINUIDAD_INTERRUMPIDA = {
    "CASA BURGIO": "cerró en 2021 y reabrió en octubre de 2022 con otro dueño",
}

# Cierres confirmados que NO están en la capa. No son filas a marcar: son una lista de guardia
# para que ninguno entre en una carga futura sin que salte.
CIERRES_FUERA_DE_LA_CAPA = [
    ("Bar Lisandro", "bar notable", "1908", "cierre confirmado"),
    ("El Malevo", "bar", "—", "cierre confirmado"),
    ("Banchero · sucursal Once", "pizzería", "—", "cierre de la sucursal; la casa de La Boca sigue"),
    ("Saverio · local fundacional", "heladería", "Av. San Juan 2727", "ya no opera"),
    ("Gino", "heladería", "Liniers", "cierre confirmado"),
    ("Venus", "heladería", "Liniers", "cierre confirmado"),
    ("Vecchio", "heladería", "Liniers", "cierre confirmado"),
    ("Fratelli", "heladería", "Liniers", "cierre confirmado"),
    ("La Veneciana", "heladería", "Liniers", "cierre confirmado"),
    ("Sandro", "heladería", "Liniers", "cierre confirmado"),
]

TIPO_LARGO = {"pizzeria_emblematica": "Pizzería emblemática",
              "heladeria_historica": "Heladería histórica"}


def plegar(texto: str) -> str:
    limpio = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", limpio)).strip()


def sin_parentesis(direccion: str) -> str:
    return re.sub(r"\s*\([^)]*\)", "", str(direccion)).strip()


def geocodificar(direccion: str, cache: dict) -> tuple[float | None, float | None, str]:
    """USIG sobre una dirección. Devuelve (lat, lon, dirección normalizada) o (None, None, '')."""
    candidato = consultar(limpiar(direccion), cache)
    if not candidato or not candidato.get("coordenadas"):
        return None, None, ""
    return (float(candidato["coordenadas"]["y"]), float(candidato["coordenadas"]["x"]),
            candidato.get("direccion", ""))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    p("CAPA DE HITOS 2026 · direcciones, patrimonio normativo y vigencia verificada")
    p("=" * 100)
    p("")

    # ================================================================== base: la capa + el canon
    capa = pd.read_csv(HITOS / "hitos_capa_unificada.csv")
    canon = pd.read_csv(HITOS / "bares_notables_canon_boletin.csv")
    otros = capa[~capa.tipo.isin(["Bar Notable", "Pizzería emblemática",
                                  "Heladería histórica"])].copy()
    bares = pd.DataFrame({
        "hito_id": canon.id_boletin, "nombre": canon.bar, "tipo": "Bar Notable",
        "reconocimiento": "Bar Notable (Boletín Oficial · declaratoria)",
        "direccion": canon.direccion_boletin, "barrio_declarado": np.nan,
        "latitud": canon.latitud, "longitud": canon.longitud,
        "origen": "BOLETIN_90 (canon)", "fuente_primaria": "Boletín Oficial CABA",
        "edicion_o_anio": np.nan, "confianza": "alta",
        "metodo_geocodificacion": canon.origen_punto,
    })

    # ================================================================== TAREA 1 · las direcciones
    entrada = pd.read_csv(EVIDENCIA / "direcciones_pizzerias_heladerias.csv")
    p("-" * 100)
    p("  TAREA 1 · LAS DIRECCIONES QUE FALTABAN")
    p("")
    p(f"      entrada: {len(entrada)} filas · "
      f"{int(entrada.direccion.notna().sum())} con dirección · "
      f"{int((entrada.calidad_fuente == 'alta').sum())} de calidad alta")
    p("")

    filas, variantes = [], []
    for fila in entrada.itertuples():
        nombre = str(fila.nombre)
        por_esquina = nombre in GEOCODIFICAR_POR_ESQUINA
        consulta = GEOCODIFICAR_POR_ESQUINA[nombre] if por_esquina else sin_parentesis(
            fila.direccion)
        lat, lon, normalizada = geocodificar(consulta, cache)
        if lat is None and not por_esquina and "esq" in str(fila.direccion).lower():
            # La dirección trae altura y esquina; si la altura no resuelve, la esquina sí.
            esquina = re.search(r"\(esq\.?\s*([^)]+)\)", str(fila.direccion), flags=re.I)
            if esquina:
                calle = sin_parentesis(fila.direccion).rsplit(" ", 1)[0]
                lat, lon, normalizada = geocodificar(
                    f"{calle} y {esquina.group(1)}", cache)
                por_esquina = bool(lat)
        filas.append({
            "hito_id": f"DIR-{fila.Index + 1:03d}",
            "nombre": nombre,
            "tipo": TIPO_LARGO.get(fila.tipo, fila.tipo),
            "reconocimiento": f"{fila.distincion} ({fila.edicion})",
            "direccion": "" if por_esquina and nombre in GEOCODIFICAR_POR_ESQUINA
                         else sin_parentesis(fila.direccion),
            "barrio_declarado": fila.barrio,
            "latitud": lat, "longitud": lon,
            "origen": f"evidencia_2026 · {fila.calidad_fuente}",
            "fuente_primaria": fila.url_fuente,
            "edicion_o_anio": fila.edicion,
            "confianza": fila.calidad_fuente,
            "metodo_geocodificacion": ("USIG por esquina (sin altura publicada)" if por_esquina
                                       else "USIG sobre la dirección" if lat else "sin resolver"),
            "conflicto_direccion": "si" if str(fila.conflicto) == "SI" else "",
            "nota_carga": fila.nota if pd.notna(fila.nota) else "",
        })
        for direccion, fuente, barrio in VARIANTES.get(nombre, []):
            vlat, vlon, _ = geocodificar(direccion, cache)
            variantes.append({"nombre": nombre, "direccion": direccion, "fuente": fuente,
                              "barrio": barrio, "latitud": vlat, "longitud": vlon})

    nuevos = pd.DataFrame(filas)
    resueltos = int(nuevos.latitud.notna().sum())
    p(f"      geocodificados: {resueltos} de {len(nuevos)}")
    for fila in nuevos[nuevos.latitud.isna()].itertuples():
        p(f"            SIN RESOLVER: {fila.nombre} — {fila.direccion}")
    for fila in nuevos[nuevos.metodo_geocodificacion.str.contains("esquina")].itertuples():
        p(f"            por esquina, altura vacía: {fila.nombre} "
          f"({GEOCODIFICAR_POR_ESQUINA.get(fila.nombre, '')})")
    p("")

    # ---- los conflictos: se mide la consecuencia, no se elige el ganador
    tabla_variantes = pd.DataFrame(variantes)
    p("      LOS CINCO CONFLICTOS · las variantes cargadas y la distancia entre ellas")
    p("")
    resumen_conflictos = []
    for nombre, grupo in tabla_variantes.groupby("nombre", sort=False):
        con_punto = grupo.dropna(subset=["latitud"])
        if len(con_punto) >= 2:
            puntos = gpd.GeoSeries(
                gpd.points_from_xy(con_punto.longitud, con_punto.latitud),
                crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO)
            distancia = max(puntos.iloc[i].distance(puntos.iloc[j])
                            for i in range(len(puntos)) for j in range(i + 1, len(puntos)))
        else:
            distancia = np.nan
        resumen_conflictos.append({"nombre": nombre, "variantes": len(grupo),
                                   "con_punto": len(con_punto),
                                   "distancia_max_m": round(distancia, 1)
                                   if not np.isnan(distancia) else np.nan})
        p(f"          {nombre}")
        for fila in grupo.itertuples():
            marca = "·" if pd.notna(fila.latitud) else "×"
            p(f"              {marca} {fila.direccion:<32}{fila.fuente:<28}{fila.barrio}")
        if not np.isnan(distancia):
            juicio = ("MISMA ESQUINA: no cambia ningún polígono" if distancia <= 60 else
                      "MISMA CUADRA: no cambia ningún polígono" if distancia <= 120 else
                      "MATERIAL: puede caer en polígonos distintos")
            p(f"              distancia máxima entre variantes: {distancia:,.0f} m — {juicio}")
        else:
            p("              una sola variante con punto: el conflicto no es de dirección")
        p("")
    tabla_variantes.to_csv(HITOS / "hitos_variantes_direccion.csv", index=False, encoding="utf-8")
    pd.DataFrame(resumen_conflictos).to_csv(
        HITOS / "hitos_conflictos_resumen.csv", index=False, encoding="utf-8")

    # ================================================================== TAREA 2 · patrimonio
    patrimonio = pd.read_csv(EVIDENCIA / "patrimonio_normativo.csv")
    patrimonio["clave"] = patrimonio.nombre.map(plegar)
    coordenadas = []
    for fila in patrimonio.itertuples():
        lat, lon, _ = geocodificar(fila.direccion, cache)
        coordenadas.append((lat, lon))
    patrimonio["latitud"] = [c[0] for c in coordenadas]
    patrimonio["longitud"] = [c[1] for c in coordenadas]

    p("-" * 100)
    p("  TAREA 2 · LA CAPA patrimonio_normativo")
    p("")
    p(f"      {len(patrimonio)} establecimientos · "
      f"{int(patrimonio.latitud.notna().sum())} geocodificados (antes la columna tenía 2 hitos)")
    p("")
    for fila in patrimonio.itertuples():
        reserva = " ⚠" if isinstance(fila.nota, str) and "FALTA confirmar" in fila.nota else ""
        p(f"          {fila.nombre[:44]:<46}{str(fila.declaratoria)[:44]:<46}"
          f"{fila.norma}{reserva}")
    p("")
    p("      DOS RESERVAS, y viajan en la columna `nota` de la capa:")
    p("          · Decreto 1021/1979 (Antiguo Matadero) sale de una fuente barrial y FALTA")
    p("            confirmarlo contra el registro nacional. Entra marcado, no entra validado.")
    p("          · El Mercado de San Telmo queda 64 m afuera de la envolvente R03. Se carga con")
    p("            su dirección real: el problema es de la delimitación de la zona, no del hito.")
    p("")
    p("      Y el caso que conviene mirar: la Ley 6.533 declara patrimonio la CARTA GASTRONÓMICA")
    p("      de Yiyo el Zeneize, no sólo el edificio. Es el patrimonio gastronómico por normativa")
    p("      más nítido de la Ciudad y no tiene equivalente en las otras nueve.")
    p("")

    # ================================================================== armar la capa
    otros["metodo_geocodificacion"] = otros.get("metodo_geocodificacion", "heredado de la capa")
    vigente = pd.concat([otros, bares, nuevos], ignore_index=True)
    vigente["clave"] = vigente.nombre.map(plegar)
    # Emparejar el patrimonio por el nombre crudo dejaba fuera «Pizzeria El Cedron» contra
    # «El Cedron» y «Pizzeria Banchero» contra «Banchero», y los dos entraban como fila nueva:
    # el mismo local dos veces, inflando `via_B_total`, que es justo lo que la vía B cuenta. Se
    # empareja por el nombre plegado —que tira PIZZERIA, BAR, CAFE— **o** por (calle, altura).
    vigente["clave_nombre"] = vigente.nombre.map(plegar_nombre)
    vigente["clave_dom"] = vigente.direccion.map(clave_domicilio)
    patrimonio["clave_nombre"] = patrimonio.nombre.map(plegar_nombre)
    patrimonio["clave_dom"] = patrimonio.direccion.map(clave_domicilio)

    def calle_de(clave: str) -> frozenset:
        return frozenset(clave.split("|")[0].split()) if clave else frozenset()

    vigente["calle_tokens"] = vigente.clave_dom.map(calle_de)
    patrimonio["calle_tokens"] = patrimonio.clave_dom.map(calle_de)

    claves_nombre = dict(zip(patrimonio.clave_nombre, patrimonio.itertuples(index=False)))
    claves_dom = {d: r for d, r in zip(patrimonio.clave_dom, patrimonio.itertuples(index=False))
                  if d}
    vigente["es_patrimonio_normativo"] = False
    vigente["patrimonio_norma"] = ""
    vigente["patrimonio_declaratoria"] = ""
    vigente["patrimonio_organismo"] = ""
    vigente["patrimonio_nota"] = ""
    marcados, emparejados = [], set()
    for indice, fila in vigente.iterrows():
        registro = claves_dom.get(fila.clave_dom) if fila.clave_dom else None
        if registro is None:
            candidato = claves_nombre.get(fila.clave_nombre)
            # El nombre plegado tira BAR y RESTAURANTE: «Restaurante Oviedo» (Recoleta) y «Bar
            # Oviedo» (Mataderos) quedan los dos en «OVIEDO», y la primera pasada los fusionó.
            # Pero exigir la misma calle tampoco sirve: el Mercado de San Telmo está asentado en
            # Defensa 961 en una fuente y en Bolívar 954 en la otra —tiene dos frentes— y El
            # Puentecito igual. Lo que desempata es la DISTANCIA entre los dos puntos, que es lo
            # único que distingue «dos nombres del mismo local» de «dos locales homónimos».
            if candidato is not None and pd.notna(fila.latitud) and pd.notna(candidato.latitud):
                puntos = gpd.GeoSeries(
                    gpd.points_from_xy([fila.longitud, candidato.longitud],
                                       [fila.latitud, candidato.latitud]),
                    crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO)
                if puntos.iloc[0].distance(puntos.iloc[1]) <= DISTANCIA_MISMO_LOCAL_M:
                    registro = candidato
        if registro is None:
            continue
        vigente.loc[indice, "es_patrimonio_normativo"] = True
        vigente.loc[indice, "patrimonio_norma"] = registro.norma
        vigente.loc[indice, "patrimonio_declaratoria"] = registro.declaratoria
        vigente.loc[indice, "patrimonio_organismo"] = registro.organismo
        vigente.loc[indice, "patrimonio_nota"] = registro.nota if pd.notna(registro.nota) else ""
        marcados.append(f"{fila.nombre} ← {registro.nombre}")
        emparejados.add(registro.nombre)

    faltantes = patrimonio[~patrimonio.nombre.isin(emparejados)]
    agregados = pd.DataFrame({
        "hito_id": [f"PAT-{i + 1:03d}" for i in range(len(faltantes))],
        "nombre": faltantes.nombre, "tipo": "Patrimonio normativo",
        "reconocimiento": faltantes.declaratoria, "direccion": faltantes.direccion,
        "barrio_declarado": faltantes.barrio, "latitud": faltantes.latitud,
        "longitud": faltantes.longitud, "origen": "evidencia_2026 · patrimonio_normativo",
        "fuente_primaria": faltantes.url_fuente, "edicion_o_anio": faltantes.anio,
        "confianza": "alta", "metodo_geocodificacion": "USIG sobre la dirección",
        "es_patrimonio_normativo": True, "patrimonio_norma": faltantes.norma,
        "patrimonio_declaratoria": faltantes.declaratoria,
        "patrimonio_organismo": faltantes.organismo,
        "patrimonio_nota": faltantes.nota.fillna(""),
    })
    vigente = pd.concat([vigente, agregados], ignore_index=True)
    vigente["clave"] = vigente.nombre.map(plegar)
    vigente["es_patrimonio_normativo"] = vigente.es_patrimonio_normativo.fillna(False)

    p(f"      marcados sobre hitos que ya estaban: {len(marcados)} → {marcados}")
    p(f"      agregados como fila nueva:           {len(agregados)} → "
      f"{list(agregados.nombre)}")
    p("")

    # ================================================================== TAREA 3 · vigencia
    vigente["vigencia_verificada"] = "sin_verificar"
    vigente["vigencia_fuente"] = ""
    vigente["vigencia_fecha"] = ""
    vigente["continuidad_ininterrumpida"] = ""
    aplicadas = []
    for (clave_nombre, clave_calle), (estado, fuente, fecha) in VIGENCIA.items():
        # Nombre Y calle: «BAR OVIEDO» (Mataderos, bar notable) y «Restaurante Oviedo» (Recoleta,
        # restaurante icónico) son dos establecimientos distintos, y marcar por nombre suelto
        # habría puesto en duda al que nadie puso en duda.
        objetivo = vigente.clave.str.contains(clave_nombre, regex=False) & \
            vigente.direccion.map(plegar).str.contains(clave_calle, regex=False)
        if not objetivo.any():
            p(f"      AVISO · no se encontró en la capa: {clave_nombre} / {clave_calle}")
            continue
        vigente.loc[objetivo, "vigencia_verificada"] = estado
        vigente.loc[objetivo, "vigencia_fuente"] = fuente
        vigente.loc[objetivo, "vigencia_fecha"] = fecha
        aplicadas.append((clave_nombre, estado, int(objetivo.sum())))
    for clave_nombre, motivo in CONTINUIDAD_INTERRUMPIDA.items():
        objetivo = vigente.clave.str.contains(clave_nombre, regex=False)
        vigente.loc[objetivo, "continuidad_ininterrumpida"] = f"no · {motivo}"

    p("-" * 100)
    p("  TAREA 3 · vigencia_verificada / vigencia_fuente / vigencia_fecha")
    p("")
    for nombre, estado, cuantas in aplicadas:
        p(f"          {estado.upper():<14}{nombre:<34}{cuantas} fila(s)")
    p("")
    for estado, cuantas in vigente.vigencia_verificada.value_counts().items():
        p(f"          {estado:<16}{cuantas:>5}")
    p("")
    p("      `sin_verificar` es un CUARTO valor y está a propósito. Los tres del enunciado —si,")
    p("      no, dudosa— suponen que alguien miró, y sobre estos hitos nadie miró. Poner `si` por")
    p("      omisión sería exactamente el error que Los Laureles acaba de demostrar.")
    p("")
    cierres = pd.DataFrame(CIERRES_FUERA_DE_LA_CAPA,
                           columns=["nombre", "tipo", "referencia", "estado"])
    cierres.to_csv(HITOS / "cierres_registrados_fuera_de_la_capa.csv",
                   index=False, encoding="utf-8")
    p(f"      Y {len(cierres)} cierres confirmados que NO están en la capa quedan en")
    p("      `cierres_registrados_fuera_de_la_capa.csv` como lista de guardia, para que ninguno")
    p("      entre en una carga futura sin que salte:")
    for fila in cierres.itertuples():
        p(f"          {fila.nombre:<34}{fila.tipo:<16}{fila.referencia:<22}{fila.estado}")
    p("")

    # ================================================================== salida
    vigente = vigente.drop(columns=["clave", "clave_nombre", "clave_dom", "calle_tokens"], errors="ignore")
    con_punto = vigente[vigente.latitud.notna() & vigente.longitud.notna()]
    if len(con_punto) == 0:
        p("  CORTE R8: ninguna fila quedó con coordenadas. No se escribe la capa.")
        (HITOS / "HITOS_2026.txt").write_text(buffer.getvalue(), encoding="utf-8")
        print(buffer.getvalue())
        return 1

    vigente.to_csv(HITOS / "hitos_capa_2026.csv", index=False, encoding="utf-8")
    gpd.GeoDataFrame(
        con_punto, geometry=gpd.points_from_xy(con_punto.longitud, con_punto.latitud),
        crs=CRS_GEOGRAFICO).to_file(HITOS / "hitos_capa_2026.geojson", driver="GeoJSON")
    patrimonio_con_punto = patrimonio[patrimonio.latitud.notna()]
    gpd.GeoDataFrame(
        patrimonio_con_punto.drop(columns="clave"),
        geometry=gpd.points_from_xy(patrimonio_con_punto.longitud,
                                    patrimonio_con_punto.latitud),
        crs=CRS_GEOGRAFICO).to_file(HITOS / "patrimonio_normativo.geojson", driver="GeoJSON")
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

    p("-" * 100)
    p("  LA CAPA 2026 · cobertura por tipo, que es lo que cambia la vía B")
    p("")
    antes = pd.read_csv(HITOS / "hitos_capa_unificada.csv").groupby("tipo").apply(
        lambda g: int(g.latitud.notna().sum()))
    p(f"      {'tipo':<26}{'hitos':>7}{'con punto':>11}{'antes':>8}")
    for tipo, grupo in vigente.groupby("tipo"):
        p(f"      {tipo:<26}{len(grupo):>7}{int(grupo.latitud.notna().sum()):>11}"
          f"{antes.get(tipo, 0):>8}")
    p("")
    p("=" * 100)
    p(f"  {len(vigente)} hitos · {len(con_punto)} con punto · "
      f"{int(vigente.es_patrimonio_normativo.sum())} patrimonio normativo · "
      f"Google Places: 0 requests")
    p("=" * 100)
    p("")

    (HITOS / "HITOS_2026.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
