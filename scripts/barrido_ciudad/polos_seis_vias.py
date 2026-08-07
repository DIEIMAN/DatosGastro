"""Las columnas medibles de las seis vías, sobre las 94 filas de la matriz y sobre las 22 del Atlas.

QUÉ HACE
--------
La definición adoptada el 2026-08-07 dice que un polo entra **por cualquiera de seis vías** y que
basta con una. Cinco de las seis se pueden medir con lo que ya está en el repositorio; la sexta
—reconocimiento externo— la llena Diego desde afuera y acá **queda vacía a propósito**.

    A · densidad y continuidad      n_locales, ha, locales_x_ha y tres medidas de continuidad
    B · trayectoria e instituciones hitos adentro, desagregados por tipo
    C · mercados y centralidades    mercado o patio del listado oficial adentro
    D · comunidades                 intersección con los cuatro enclaves con límites documentados
    E · reconocimiento externo      VACÍA. La llena Diego.
    F · corredor                    el índice de `polos_indice_corredor.py`

Y contesta el control de la Tarea 4: **por cuántas vías medibles entra cada una de las 22 zonas
publicadas**, que es la pregunta que valida la grilla.

TODO LO DECLARADO ESTÁ EN `LECTURA_PREVIA.md`, ESCRITO ANTES DE CORRER
------------------------------------------------------------------------
Cortes, convenciones y curvas: 60 m de continuidad, 50 % de pertenencia al soporte, 150 m de
buffer de enclave, y el barrido de los cuatro. Nada de eso se movió después de ver un resultado.

LA LISTA DE BARES NOTABLES QUE SE USA ES LA NUEVA
--------------------------------------------------
`hitos_cerrar_bares_notables.py` ya fijó el Boletín Oficial como declaratoria: 90 bares, todos con
punto. Esta corrida arma una **capa vigente** que reemplaza el bloque de Bar Notable de
`hitos_capa_unificada.csv` por el canon y **deja el archivo de ayer intacto**, porque pisarlo
borraría el estado desde el que se lo puede comparar.

Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_seis_vias.py
"""
from __future__ import annotations

import io
import sys
import unicodedata
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import (  # noqa: E402
    BARRIDO,
    CRS_GEOGRAFICO,
    CRS_METRICO,
    CURVA_BUFFER_M,
    PERTENENCIA,
    construir_enclaves,
    envolventes_22,
    puntos_base,
    soportes_94,
)

OUT = BARRIDO / "seis_vias"
HITOS = BARRIDO / "hitos"
DOCUMENTAL = BARRIDO / "desde_cowork" / "hitos_documentales_caba.csv"

# --------------------------------------------------------------------------- lo declarado
UMBRAL_CONTINUIDAD_M = 60           # ≈ media cuadra: dos locales «en el mismo tramo»
CURVA_CONTINUIDAD_M = (20, 40, 60, 80, 120)
PERTENENCIA_MINIMA = 0.50           # «más de la mitad, pertenece»
CURVA_PERTENENCIA = (0.25, 0.50, 0.75, 1.00)

TIPOS_VIA_B = {
    "Bar Notable": "bar_notable",
    "Restaurante Icónico": "restaurante_iconico",
    "Pizzería emblemática": "pizzeria_emblematica",
    "Heladería histórica": "heladeria_historica",
    "MICHELIN": "michelin",
    "Ranking internacional": "50best",
}
# `patrimonio normativo` no es un `tipo` de la capa: es una propiedad del reconocimiento, y hay
# que definirla con cuidado. La primera versión buscaba «Ley » y devolvió 80 hitos: la propia
# distinción de Bar Notable es «Cafe, Bar, Billar o Confiteria Notable (Ley 35...)», así que los
# 90 bares entraban por la puerta de atrás y la columna dejaba de distinguir nada. El patrimonio
# normativo que la definición pide es el que declara un valor **histórico**, no la distinción
# gastronómica: monumento, sitio histórico, área de protección, patrimonio inmaterial.
PATRON_PATRIMONIO = r"Monumento Hist|Sitio Hist|Patrimonio hist|Area de Protecci|\bAPH\b"


def sin_tildes(texto: str) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()


def capa_hitos_vigente() -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """La capa de hitos con el bloque de Bar Notable reemplazado por el canon del Boletín."""
    capa = pd.read_csv(HITOS / "hitos_capa_unificada.csv")
    canon = pd.read_csv(HITOS / "bares_notables_canon_boletin.csv")

    otros = capa[capa.tipo != "Bar Notable"].copy()
    nuevos = pd.DataFrame({
        "hito_id": canon.id_boletin,
        "nombre": canon.bar,
        "tipo": "Bar Notable",
        "reconocimiento": "Bar Notable (Boletín Oficial · declaratoria)",
        "direccion": canon.direccion_boletin,
        "barrio_declarado": np.nan,
        "latitud": canon.latitud,
        "longitud": canon.longitud,
        "origen": "BOLETIN_90 (canon) · " + canon.origen_punto.fillna(""),
        "fuente_primaria": "Boletín Oficial CABA",
        "edicion_o_anio": np.nan,
        "confianza": "alta",
    })
    vigente = pd.concat([otros, nuevos], ignore_index=True)

    # `patrimonio normativo` se saca del catálogo documental, que es el que guarda el acto: la
    # capa unificada lo pierde al reescribir `reconocimiento` de los mercados.
    documental = pd.read_csv(DOCUMENTAL)
    patrimonio = documental[documental.distincion.astype(str).str.contains(
        PATRON_PATRIMONIO, case=False, na=False, regex=True)]
    claves_patrimonio = {sin_tildes(n).upper().strip() for n in patrimonio.nombre}
    vigente["es_patrimonio_normativo"] = vigente.nombre.map(
        lambda n: sin_tildes(n).upper().strip() in claves_patrimonio)
    # El reconocimiento de la propia capa también cuenta cuando nombra un acto.
    vigente["es_patrimonio_normativo"] |= vigente.reconocimiento.astype(str).str.contains(
        PATRON_PATRIMONIO, case=False, na=False, regex=True)

    con_punto = vigente[vigente.latitud.notna() & vigente.longitud.notna()].copy()
    geo = gpd.GeoDataFrame(
        con_punto, geometry=gpd.points_from_xy(con_punto.longitud, con_punto.latitud),
        crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO)

    cobertura = vigente.groupby("tipo").apply(
        lambda g: pd.Series({
            "hitos": len(g),
            "con_punto": int(g.latitud.notna().sum()),
            "sin_punto": int(g.latitud.isna().sum()),
        })).reset_index()
    return geo.reset_index(drop=True), cobertura


def continuidad(coordenadas: np.ndarray, umbral: float) -> float:
    """% de puntos en la componente conexa mayor uniendo todo lo que esté a <= umbral."""
    n = len(coordenadas)
    if n == 0:
        return np.nan
    if n == 1:
        return 100.0
    arbol = cKDTree(coordenadas)
    pares = np.array(list(arbol.query_pairs(umbral))) if n > 1 else np.empty((0, 2), int)
    if len(pares) == 0:
        return round(100.0 / n, 1)
    grafo = coo_matrix((np.ones(len(pares)), (pares[:, 0], pares[:, 1])), shape=(n, n))
    _, etiquetas = connected_components(grafo, directed=False)
    return round(100.0 * np.bincount(etiquetas).max() / n, 1)


def vecino_medio(coordenadas: np.ndarray) -> float:
    if len(coordenadas) < 2:
        return np.nan
    distancias, _ = cKDTree(coordenadas).query(coordenadas, k=2)
    return float(distancias[:, 1].mean())


def medir_via_a(coordenadas: np.ndarray, hectareas: float) -> dict:
    n = len(coordenadas)
    salida = {"n_locales": n, "ha": round(hectareas, 2),
              "locales_x_ha": round(n / hectareas, 3) if hectareas else np.nan}
    for metros in CURVA_CONTINUIDAD_M:
        salida[f"cont_pct_comp_mayor_{metros}m"] = continuidad(coordenadas, metros)
    observado = vecino_medio(coordenadas)
    salida["vecino_medio_m"] = round(observado, 1) if not np.isnan(observado) else np.nan
    # 1/(2·√λ) con λ en locales por m². Es la ley de Poisson que ya usa el proyecto.
    if hectareas and n >= 2:
        lambda_m2 = n / (hectareas * 10_000)
        predicho = 1 / (2 * np.sqrt(lambda_m2))
        salida["vecino_obs_sobre_poisson"] = round(observado / predicho, 3)
    else:
        salida["vecino_obs_sobre_poisson"] = np.nan
    return salida


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    puntos = puntos_base()
    pertenencia = pd.read_csv(PERTENENCIA)[["local_id", "polo_unido"]]
    puntos = puntos.merge(pertenencia, on="local_id", how="left")
    hitos, cobertura_hitos = capa_hitos_vigente()
    enclaves, bitacora = construir_enclaves()
    mercados = hitos[hitos.tipo == "Mercado/patio"]

    p("LAS SEIS VÍAS · las columnas medibles, sobre las 94 filas y sobre las 22 publicadas")
    p("=" * 100)
    p("")
    p(f"  puntos: {len(puntos):,} · hitos con punto: {len(hitos)} · "
      f"mercados ubicables: {len(mercados)} · enclaves: {len(enclaves)}")
    p("  Todo lo declarado está en LECTURA_PREVIA.md. Google Places: 0 requests.")
    p("")

    # ------------------------------------------------------------------ R8 sobre vía B
    p("-" * 100)
    p("  LA COBERTURA DE LOS HITOS, AL LADO DEL CONTEO Y NO AL PIE")
    p("")
    p(f"      {'tipo':<26}{'hitos':>7}{'con punto':>11}{'sin punto':>11}")
    for fila in cobertura_hitos.itertuples():
        p(f"      {fila.tipo:<26}{fila.hitos:>7}{fila.con_punto:>11}{fila.sin_punto:>11}")
    patrimonio_total = int(hitos.es_patrimonio_normativo.sum())
    p("")
    p(f"      patrimonio normativo (ubicables): {patrimonio_total}")
    for fila in hitos[hitos.es_patrimonio_normativo].itertuples():
        p(f"            {fila.nombre} — {fila.reconocimiento}")
    if patrimonio_total == 0:
        p("      CORTE R8: la columna de patrimonio normativo llegó vacía entera. No se reporta")
        p("      ninguna conclusión sobre ella.")
    else:
        p("      Estaba avisado en LECTURA_PREVIA §4: la columna sale casi entera en cero y eso")
        p("      es un hueco de la fuente, no un resultado sobre el territorio. La Esquina Homero")
        p("      Manzi, que la definición cita como Sitio Histórico Nacional, figura en la capa")
        p("      sólo como Bar Notable: su declaratoria nacional no está cargada en ningún lado.")
    p("")
    p("      Un 0 en una fila puede ser «no hay» o «no sabemos dónde». Las 20 pizzerías y las 5")
    p("      heladerías sin altura no se ubican en el centroide del barrio: quedan sin punto.")
    p("")

    def medir_capa(capa: gpd.GeoDataFrame, clave: str) -> pd.DataFrame:
        dentro = gpd.sjoin(puntos[["local_id", "polo_unido", "geometry"]],
                           capa[[clave, "geometry"]], predicate="within", how="inner")
        hitos_dentro = gpd.sjoin(hitos, capa[[clave, "geometry"]],
                                 predicate="within", how="inner")
        mercados_dentro = gpd.sjoin(mercados, capa[[clave, "geometry"]],
                                    predicate="within", how="inner")
        # Cuántos locales tiene cada polo del borrador, para la regla de pertenencia de vía A.
        tamano_polo = puntos.polo_unido.value_counts()

        filas = []
        for fila in capa.itertuples():
            identificador = getattr(fila, clave)
            registro = {clave: identificador}
            if fila.geometry is None or fila.geometry.is_empty:
                registro["soporte_ausente"] = "si"
                filas.append(registro)
                continue
            registro["soporte_ausente"] = "no"

            miembros = dentro[dentro[clave] == identificador]
            coordenadas = np.array([[g.x, g.y] for g in
                                    puntos.loc[miembros.index.unique(), "geometry"]]) \
                if len(miembros) else np.empty((0, 2))
            registro.update(medir_via_a(coordenadas, fila.geometry.area / 10_000))

            # vía A abierta: algún polo del borrador con >= X % de sus locales adentro.
            adentro_por_polo = miembros.polo_unido.value_counts()
            for corte in CURVA_PERTENENCIA:
                cumplen = [polo for polo, cuantos in adentro_por_polo.items()
                           if isinstance(polo, str) and polo
                           and cuantos / tamano_polo.get(polo, np.inf) >= corte]
                registro[f"via_A_polos_pert_{int(corte * 100)}"] = len(cumplen)
                if corte == PERTENENCIA_MINIMA:
                    registro["via_A_polos"] = "; ".join(sorted(cumplen))
                    registro["via_A_abierta"] = "si" if cumplen else "no"

            propios = hitos_dentro[hitos_dentro[clave] == identificador]
            for tipo, columna in TIPOS_VIA_B.items():
                registro[f"via_B_{columna}"] = int((propios.tipo == tipo).sum())
            registro["via_B_patrimonio_normativo"] = int(propios.es_patrimonio_normativo.sum())
            registro["via_B_total"] = len(propios)
            registro["via_B_abierta"] = "si" if len(propios) else "no"
            registro["via_B_nombres"] = "; ".join(sorted(propios.nombre.astype(str))[:12])

            suyos = mercados_dentro[mercados_dentro[clave] == identificador]
            registro["via_C_mercado_patio"] = "si" if len(suyos) else "no"
            registro["via_C_cual"] = "; ".join(sorted(suyos.nombre.astype(str)))
            registro["via_C_abierta"] = registro["via_C_mercado_patio"]

            tocados = enclaves[enclaves.intersects(fila.geometry)]
            registro["via_D_enclave"] = "; ".join(sorted(tocados.enclave))
            registro["via_D_abierta"] = "si" if len(tocados) else "no"

            registro["via_E_reconocimiento"] = ""      # la llena Diego
            filas.append(registro)
        return pd.DataFrame(filas)

    # ------------------------------------------------------------------ curva del buffer (R4)
    p("-" * 100)
    p("  CÓMO SE CONSTRUYERON LOS CUATRO ENCLAVES (vía D)")
    p("")
    for linea in bitacora:
        p(f"      {linea}")
    p("")
    p(f"      {'enclave':<34}{'tramos':>8}{'eje m':>10}{'ha':>9}")
    for fila in enclaves.itertuples():
        p(f"      {fila.enclave:<34}{fila.n_tramos:>8}{fila.largo_eje_m:>10,.0f}{fila.ha:>9.1f}")
    p("")
    p("  LA CURVA DEL BUFFER (R4) · cuántas de las 94 tocan algún enclave según el radio")
    soportes = soportes_94()
    fila_curva = []
    for radio in CURVA_BUFFER_M:
        capa, _ = construir_enclaves(radio)
        tocan = sum(1 for g in soportes.geometry
                    if g is not None and not g.is_empty and capa.intersects(g).any())
        fila_curva.append((radio, tocan))
    p("      " + "".join(f"{r:>8}m" for r, _ in fila_curva))
    p("      " + "".join(f"{t:>9}" for _, t in fila_curva))
    p("")
    desde_100 = {t for r, t in fila_curva if r >= 100}
    if len({t for _, t in fila_curva}) == 1:
        p("      El resultado NO cambia en todo el rango: el radio no es la mitad del resultado.")
    elif len(desde_100) == 1:
        p("      Cambia sólo entre 50 y 100 m y después queda plano hasta 300. El valor elegido")
        p("      —150 m— cae adentro de la meseta, así que no está sosteniendo el resultado.")
    else:
        p("      El resultado cambia a lo largo del rango: la elección de los 150 m es parte del")
        p("      resultado y hay que decirlo al lado de cualquier conteo de vía D.")
    p("")

    # ------------------------------------------------------------------ TAREA 1 · las 94
    medidas94 = medir_capa(soportes, "polo_id")
    tabla94 = soportes.drop(columns="geometry").merge(medidas94, on="polo_id", how="left")
    indice = pd.read_csv(OUT / "indice_corredor_94_filas.csv")[
        ["polo_id", "elongacion", "frac_banda_100m", "ancho_p80_m", "largo_p5_p95_m",
         "forma_declarada", "rama_calibracion"]]
    tabla94 = tabla94.merge(indice, on="polo_id", how="left")
    tabla94 = tabla94.rename(columns={
        "elongacion": "via_F_elongacion", "frac_banda_100m": "via_F_frac_banda_100m",
        "ancho_p80_m": "via_F_ancho_p80_m", "largo_p5_p95_m": "via_F_largo_m",
        "forma_declarada": "via_F_forma"})
    tabla94["via_F_abierta"] = np.where(tabla94.via_F_forma == "corredor", "si", "no")
    tabla94.to_csv(OUT / "seis_vias_94_filas.csv", index=False, encoding="utf-8")

    p("-" * 100)
    p("  TAREA 1 · LAS 94 FILAS · cuántas abren cada vía")
    p("")
    for via, columna in [("A · densidad", "via_A_abierta"), ("B · trayectoria", "via_B_abierta"),
                         ("C · mercados", "via_C_abierta"), ("D · comunidades", "via_D_abierta"),
                         ("F · corredor", "via_F_abierta")]:
        p(f"      {via:<20}{int((tabla94[columna] == 'si').sum()):>4} de 94")
    p(f"      {'E · reconocimiento':<20}{'—':>4}   columna vacía a propósito: la llena Diego")
    p("")
    tabla94["n_vias_medibles"] = (
        (tabla94.via_A_abierta == "si").astype(int) + (tabla94.via_B_abierta == "si").astype(int)
        + (tabla94.via_C_abierta == "si").astype(int) + (tabla94.via_D_abierta == "si").astype(int)
        + (tabla94.via_F_abierta == "si").astype(int))
    # Sin soporte no es «cero vías»: es «no medido». Un 0 ahí se lee como hallazgo y no lo es.
    tabla94.loc[tabla94.soporte_ausente != "no", "n_vias_medibles"] = np.nan
    p("      vías medibles abiertas por fila (sobre las 92 con soporte):")
    for cuantas, n in tabla94[tabla94.soporte_ausente == "no"].n_vias_medibles.value_counts(
    ).sort_index().items():
        p(f"            {cuantas} vía(s): {n} filas")
    ninguna = tabla94[(tabla94.soporte_ausente == "no") & (tabla94.n_vias_medibles == 0)]
    p(f"      filas con CERO vías medibles abiertas: {len(ninguna)}")
    for fila in ninguna.itertuples():
        p(f"            {fila.polo_id} — {fila.nombre_polo}")
    p("")
    p("      Las que abren vía D (comunidades):")
    for fila in tabla94[tabla94.via_D_abierta == "si"].itertuples():
        p(f"            {str(fila.polo_id):<26}{str(fila.nombre_polo)[:24]:<26}{fila.via_D_enclave}")
    p("")
    p("      Las que abren vía C (mercados y patios):")
    for fila in tabla94[tabla94.via_C_abierta == "si"].itertuples():
        p(f"            {str(fila.polo_id):<26}{str(fila.nombre_polo)[:24]:<26}{fila.via_C_cual}")
    ubicados = {n for celda in tabla94.via_C_cual.dropna() for n in str(celda).split("; ") if n}
    huerfanos = sorted(set(mercados.nombre.astype(str)) - ubicados)
    p("")
    p(f"      Y los {len(huerfanos)} mercados ubicables que NO caen en ninguna de las 94 —que es")
    p("      cobertura del recorte, no ausencia del mercado—:")
    for nombre in huerfanos:
        p(f"            {nombre}")
    p("")
    p("  LA CURVA DE LA PERTENENCIA (R4) · cuántas de las 94 abren vía A según el corte")
    p("      " + "".join(f"{int(c * 100):>8}%" for c in CURVA_PERTENENCIA))
    p("      " + "".join(f"{int((tabla94[f'via_A_polos_pert_{int(c * 100)}'] > 0).sum()):>9}"
                        for c in CURVA_PERTENENCIA))
    p("")
    tabla94.to_csv(OUT / "seis_vias_94_filas.csv", index=False, encoding="utf-8")

    # ------------------------------------------------------------------ TAREA 4 · las 22
    envolventes = envolventes_22()
    medidas22 = medir_capa(envolventes, "referencia_id")
    tabla22 = envolventes.drop(columns="geometry").merge(
        medidas22, on="referencia_id", how="left")
    indice22 = pd.read_csv(OUT / "indice_corredor_22_zonas.csv")[
        ["referencia_id", "elongacion", "frac_banda_100m"]]
    tabla22 = tabla22.merge(indice22, on="referencia_id", how="left")
    tabla22 = tabla22.rename(columns={"elongacion": "via_F_elongacion",
                                      "frac_banda_100m": "via_F_frac_banda_100m"})
    tabla22["via_F_abierta"] = np.where(tabla22.via_F_elongacion >= 2.0, "si", "no")
    tabla22["n_vias_medibles"] = (
        (tabla22.via_A_abierta == "si").astype(int) + (tabla22.via_B_abierta == "si").astype(int)
        + (tabla22.via_C_abierta == "si").astype(int) + (tabla22.via_D_abierta == "si").astype(int)
        + (tabla22.via_F_abierta == "si").astype(int))
    tabla22 = tabla22.sort_values(["n_vias_medibles", "referencia_id"],
                                  ascending=[False, True]).reset_index(drop=True)
    tabla22.to_csv(OUT / "seis_vias_22_zonas.csv", index=False, encoding="utf-8")

    p("=" * 100)
    p("  TAREA 4 · EL CONTROL · por cuántas vías medibles entra cada una de las 22")
    p("=" * 100)
    p("")
    p(f"  {'id':<5}{'zona':<32}{'A':>3}{'B':>3}{'C':>3}{'D':>3}{'F':>3}{'total':>7}   hitos")
    for fila in tabla22.itertuples():
        marcas = "".join(f"{'X' if getattr(fila, f'via_{v}_abierta') == 'si' else '·':>3}"
                         for v in "ABCDF")
        p(f"  {fila.referencia_id:<5}{fila.nombre[:31]:<32}{marcas}{fila.n_vias_medibles:>7}"
          f"   {fila.via_B_total}")
    p("")
    sin_vias = tabla22[tabla22.n_vias_medibles == 0]
    p(f"      zonas con al menos una vía medible abierta: "
      f"{int((tabla22.n_vias_medibles > 0).sum())} de 22")
    p(f"      zonas con CERO:                             {len(sin_vias)}")
    p("")
    if len(sin_vias) == 0:
        p("      RAMA DECLARADA · «todas las 22 abren al menos una vía medible» →")
        p("      LA GRILLA SE SOSTIENE SOLA. No depende del trabajo documental para funcionar.")
    else:
        p("      RAMA DECLARADA · hay zonas sin ninguna vía medible. El primer sospechoso NO es")
        p("      el territorio sino el soporte: se mide antes de concluir nada.")
        for fila in sin_vias.itertuples():
            p(f"            {fila.referencia_id} {fila.nombre}: {fila.n_locales} locales, "
              f"{fila.ha} ha, {fila.via_B_total} hitos")
    p("")
    p("      Distribución:")
    for cuantas, n in tabla22.n_vias_medibles.value_counts().sort_index().items():
        p(f"            {cuantas} vía(s): {n} zonas")
    p("")

    p("=" * 100)
    p(f"  94 filas y 22 zonas medidas · vía E vacía a propósito · "
      f"rama del índice: {indice.rama_calibracion.iloc[0]} · Places: 0 requests")
    p("=" * 100)
    p("")

    (OUT / "SEIS_VIAS.txt").write_text(buffer.getvalue(), encoding="utf-8")
    enclaves.to_file(OUT / "enclaves_comunitarios.geojson", driver="GeoJSON")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
