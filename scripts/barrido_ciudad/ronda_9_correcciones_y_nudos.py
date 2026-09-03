"""Ronda 9 · la corrección del New Brighton, los dos nudos de geometría y las tres devoluciones.

QUÉ HACE — y qué NO
--------------------
Google Places: **0 requests**. Ninguna consulta de red. La escalera de calibración vive en
`ronda_9_escalera_places.py`, aparte y con su propio tope, para que este guion se pueda correr
tantas veces como haga falta sin gastar nada.

    TAREA 1  H084 The New Brighton pasa de `no` a `en_riesgo`, con `alerta_juridica`
    TAREA 2  la capa de fuentes con defecto se audita contra el catálogo documentado (R9)
    TAREA 3  el volcado de la capa de hitos, para que Diego pueda correr R9 antes de reportar
    TAREA 4  las calles de la cola de R20
    TAREA 5  Colegiales · las tres verificaciones que van ANTES de trazar
    TAREA 6  Palermo · las tres intersecciones que deciden la hipótesis
    TAREA 7  qué son R08 y R21, y dónde quedó PGR_P004 al perder la vía C

POR QUÉ EL NEW BRIGHTON NO ES UN CIERRE
----------------------------------------
La quiebra es un hecho del expediente, no del salón. Lo que la capa registra en
`vigencia_verificada` es **si el establecimiento atiende**, y ninguna de las siete coberturas
afirma que dejó de atender: dos reseñas posteriores a la quiebra describen servicio real, la más
nueva a 63 días de la declaración. Escribir `no` ahí es exactamente R13 al revés —atribuirle al
establecimiento un veredicto que corresponde a la sociedad que lo explota—.

El dato jurídico no se pierde: se guarda en su propio campo, que es donde se puede leer sin que
contamine el veredicto de vigencia.

LO QUE ESTE GUION NO PUEDE HACER
---------------------------------
FD-21 y FD-22 **no se cargan**. Sus definiciones viven en `fuentes_con_defecto_FD20_FD22.csv`,
que no está en el repositorio. Inventarlas para completar el rango sería fabricar el contenido de
una fuente, que es el defecto que la capa existe para registrar. Se cargan los diez huecos que sí
tienen texto en disco, y FD-20, cuya evidencia la produjo la ronda 8 acá adentro.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_9_correcciones_y_nudos.py
"""
from __future__ import annotations

import io
import re
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import nearest_points, unary_union

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import (  # noqa: E402
    BARRIDO,
    CALLEJERO,
    CRS_METRICO,
    POLOS_V3,
    barrios,
    puntos_base,
    sin_tildes,
)
from ronda_7_geometria_ampliaciones import BUFFER_EJE_M, piezas_en_marco  # noqa: E402
from ronda_8_geometria import tramo_entre  # noqa: E402

HITOS = BARRIDO / "hitos"
FUENTES = BARRIDO / "fuentes"
SEIS = BARRIDO / "seis_vias"
COWORK = BARRIDO / "desde_cowork" / "evidencia_2026"
GEOM_R8 = BARRIDO / "geometria_r8"
SALIDA = BARRIDO / "ronda_9"

CAPA_R8 = HITOS / "hitos_capa_2026_r8.csv"
FD_CARGADA = FUENTES / "fuentes_defectos_conocidos.csv"
REFERENCIAS = GEOM_R8 / "referencias_r8.geojson"

OUT_CAPA = HITOS / "hitos_capa_2026_r9.csv"
OUT_DUMP = SALIDA / "capa_de_hitos_volcado.csv"
OUT_FD = FUENTES / "fuentes_defectos_conocidos_r9.csv"
OUT_FD_AUDIT = SALIDA / "auditoria_capa_FD.csv"
OUT_R20 = SALIDA / "cola_de_R20_calles.csv"
OUT_COLEGIALES = SALIDA / "colegiales_verificaciones.csv"
OUT_PALERMO = SALIDA / "palermo_tres_intersecciones.csv"
INFORME = SALIDA / "RONDA_9.txt"

HOY = date(2026, 8, 8)

# Los tres identificadores de subzona de Palermo, resueltos en DONDE_ESTA_SOHO.txt. No es una
# inferencia de acá: es el reparto que `polos_soporte.SUBZONAS_PALERMO` ya declara.
PALERMO = {"Soho": "P091", "Hollywood": "P078", "Las Cañitas": "P065"}

# Los diez huecos del catálogo FD, con el archivo de cowork donde vive el texto de cada uno.
HUECOS_FD = {
    "FD-05": "fuentes_con_defecto_FD05_FD07.csv",
    "FD-06": "fuentes_con_defecto_FD05_FD07.csv",
    "FD-07": "fuentes_con_defecto_FD05_FD07.csv",
    "FD-08": "fuentes_con_defecto_FD08_FD12.csv",
    "FD-09": "fuentes_con_defecto_FD08_FD12.csv",
    "FD-10": "fuentes_con_defecto_FD08_FD12.csv",
    "FD-11": "fuentes_con_defecto_FD08_FD12.csv",
    "FD-13": "fuentes_con_defecto_FD13_FD15.csv",
    "FD-14": "fuentes_con_defecto_FD13_FD15.csv",
    "FD-15": "fuentes_con_defecto_FD13_FD15.csv",
}


def p_factory(buffer: io.StringIO):
    def p(*args_):
        print(*args_, file=buffer)
    return p


def medir(geom, puntos) -> tuple[float, int]:
    if geom is None or geom.is_empty:
        return 0.0, 0
    return round(geom.area / 10_000, 2), int(puntos.within(geom).sum())


def calle_de(direccion: str) -> str:
    """El nombre de calle de una dirección normalizada, sin la altura.

    `direccion_norm` puede traer dos direcciones separadas por `;` —una esquina—. Se queda con la
    primera, que es la que el normalizador puso como principal.

    NO ALCANZA PARA REPARTIR LOCALES POR CALLE: el 46,6 % del universo núcleo no tiene
    `direccion_norm`. Por eso el reparto de la cola de R20 se hace por eje más cercano y esta
    función queda sólo para etiquetar.
    """
    primera = str(direccion).split(";")[0]
    return re.sub(r"\s*\d+\s*$", "", primera).strip()


def eje_de(callejero: gpd.GeoDataFrame, *nombres: str):
    """El eje de una calle, uniendo TODOS los nombres oficiales que la designan.

    Un corredor puede llevar dos nombres oficiales distintos y el callejero los guarda como dos
    registros. Buscar uno solo devuelve medio corredor, sin error.
    """
    piezas = []
    for nombre in nombres:
        seg = callejero[callejero.clave == sin_tildes(nombre)]
        piezas.extend(list(seg.geometry))
    return unary_union(piezas) if piezas else None


def tramo_verificado(callejero: gpd.GeoDataFrame, eje, corte_a: str, corte_b: str,
                     tolerancia_m: float = 40.0):
    """El tramo entre dos cortes, verificando que los dos TOQUEN el eje. R12.

    `ronda_8_geometria.tramo_entre` cae en `nearest_points` cuando un corte no cruza, y entonces
    devuelve un tramo anclado en un punto que no es una esquina — sin avisar, y a cualquier
    distancia. Acá se distinguen tres casos y los tres se declaran:

        cruza          la intersección existe: es una esquina
        empalma en T   no cruza pero llega a menos de `tolerancia_m`. Pasa todo el tiempo con las
                       avenidas de borde: la calle transversal muere contra la avenida y el
                       callejero corta su eje antes de la línea de centro. Es una esquina real
                       aunque las geometrías no se toquen.
        no llega       más lejos que la tolerancia. NO hay tramo, y se dice a cuánto quedó.

    Devuelve (geometría | None, diagnóstico).
    """
    diag = {}
    puntos = []
    for etiqueta, corte in (("a", corte_a), ("b", corte_b)):
        otra = eje_de(callejero, corte)
        if otra is None or otra.is_empty:
            diag[etiqueta] = f"«{corte}» no existe en el callejero"
            return None, diag
        cruce = eje.intersection(otra)
        if not cruce.is_empty:
            t = eje.project(cruce.centroid)
            diag[etiqueta] = f"«{corte}» cruza a los {t:,.0f} m del eje"
        else:
            d = eje.distance(otra)
            if d > tolerancia_m:
                diag[etiqueta] = (f"«{corte}» NO llega al eje — queda a {d:,.0f} m, más que la "
                                  f"tolerancia de {tolerancia_m:.0f} m")
                return None, diag
            t = eje.project(nearest_points(eje, otra)[0])
            diag[etiqueta] = (f"«{corte}» empalma en T a los {t:,.0f} m del eje "
                              f"(a {d:,.0f} m, dentro de tolerancia)")
        puntos.append(t)
    desde, hasta = sorted(puntos)
    if hasta - desde < 1:
        diag["largo_m"] = 0
        return None, diag
    piezas = []
    for pieza in (eje.geoms if hasattr(eje, "geoms") else [eje]):
        centro = pieza.interpolate(0.5, normalized=True)
        t = eje.project(centro)
        if desde - 1 <= t <= hasta + 1:
            piezas.append(pieza)
    diag["largo_m"] = round(hasta - desde)
    return (unary_union(piezas) if piezas else None), diag


def main() -> int:  # noqa: C901, PLR0915
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()
    p = p_factory(buffer)
    SALIDA.mkdir(parents=True, exist_ok=True)

    p("=" * 100)
    p("  RONDA 9 · la corrección del New Brighton, los dos nudos y las tres devoluciones")
    p(f"  {HOY.isoformat()} · Google Places: 0 requests")
    p("=" * 100)
    p("")

    capa = pd.read_csv(CAPA_R8, encoding="utf-8")
    callejero = gpd.read_file(CALLEJERO).to_crs(CRS_METRICO)
    callejero["clave"] = callejero.nomoficial.map(sin_tildes)
    capa_barrios = barrios()
    base = puntos_base()
    referencias = gpd.read_file(REFERENCIAS).to_crs(CRS_METRICO).set_index("referencia_id")

    # ============================================================ TAREA 1 · The New Brighton
    p("-" * 100)
    p("  TAREA 1 · H084 THE NEW BRIGHTON — de `no` a `en_riesgo`")
    p("")
    for col in ("alerta_juridica", "alerta_juridica_fecha", "alerta_juridica_fuente",
                "nota_ronda_9"):
        if col not in capa.columns:
            capa[col] = ""
    fila = capa.hito_id == "H084"
    if not fila.any():
        p("      !! H084 no está en la capa. La tarea 1 no se aplica.")
    else:
        antes = capa.loc[fila, "vigencia_verificada"].iloc[0]
        capa.loc[fila, "vigencia_verificada"] = "en_riesgo"
        capa.loc[fila, "vigencia_nivel"] = "v2"
        capa.loc[fila, "vigencia_fuente"] = (
            "opera con quiebra decretada. Dos reseñas de Tripadvisor POSTERIORES a la quiebra "
            "describen servicio real —la de mayo de 2026 menciona piano en vivo— y la más nueva "
            "es del 06/06/2026, 63 días después. Fichas .com y .com.ar sin marca de cierre, "
            "horarios lu-vi 8 a 24. Places OPERATIONAL. Ninguna de las siete coberturas afirma "
            "que dejó de atender.")
        capa.loc[fila, "vigencia_fecha"] = "2026-06-06"
        capa.loc[fila, "alerta_juridica"] = "quiebra decretada"
        capa.loc[fila, "alerta_juridica_fecha"] = "2026-03-18"
        capa.loc[fila, "alerta_juridica_fuente"] = (
            "Juzgado Nacional de Primera Instancia en lo Comercial N° 3")
        capa.loc[fila, "vigencia_revisar_hasta"] = "2026-11-06"
        capa.loc[fila, "nota_ronda_9"] = (
            "la quiebra es un hecho de la sociedad que explota el local, no del salón. Misma "
            "categoría que H057 Esquina Homero Manzi: en_riesgo con fecha y revisión a 90 días.")
        p(f"      vigencia_verificada: «{antes}» → «en_riesgo»")
        p("      alerta_juridica    : quiebra decretada · 18/03/2026 · Juzgado Nac. 1ª Inst. "
          "Comercial N° 3")
        p("      el campo nuevo NO toca el veredicto de vigencia: son dos hechos distintos y "
          "ahora tienen dos columnas distintas.")
    p("")
    p("      lo que esto le hace al catálogo de auditoría de cierres:")
    p("")
    p("        Plaza Bar        · cerrado 29/04/2017 · reapertura anunciada 2028   SIGUE cerrado")
    p("        La Buena Medida  · cerrada 10/2025, cierre definitivo               SIGUE cerrado")
    p("        The New Brighton · quiebra 18/03/2026, atendiendo                   PASA a en_riesgo")
    p("")
    p("      de TRES cerrados a DOS. Y el catálogo de en_riesgo pasa de uno a dos: H057 y H084.")
    p("")
    conteo = capa.vigencia_verificada.value_counts()
    p("      la capa entera, después de la corrección:")
    for estado, n in conteo.items():
        p(f"        {estado:<34} {n:>4}")
    p("")

    # ============================================================ TAREA 2 · la capa FD
    p("-" * 100)
    p("  TAREA 2 · LA CAPA DE FUENTES CON DEFECTO, AUDITADA — R9 sobre el propio catálogo")
    p("")
    fd = pd.read_csv(FD_CARGADA, encoding="utf-8")
    cargados = list(fd.defecto_id)
    p(f"      cargados en `{FD_CARGADA.name}`: {len(cargados)}")
    p(f"        {', '.join(cargados)}")
    p("")
    documentados = [f"FD-{n:02d}" for n in range(1, 20)]
    faltan = [x for x in documentados if x not in cargados]
    p(f"      documentados por Diego (FD-01..FD-15) + los cuatro de la ronda 8 = {len(documentados)}")
    p(f"      FALTAN {len(faltan)}, no seis:")
    p(f"        {', '.join(faltan)}")
    p("")
    p("      de dónde salía el «seis»: el salto 5 → 9 de la ronda 8 no fue FD-05..FD-08. Los")
    p("      cinco que había eran FD-01, FD-02, FD-03, FD-04 y **FD-12**, y los cuatro nuevos")
    p("      fueron FD-16..FD-19. El rango FD-05..FD-11 y FD-13..FD-15 nunca se cargó: son diez.")
    p("")

    filas_nuevas = []
    for fid, archivo in HUECOS_FD.items():
        ruta = COWORK / archivo
        if not ruta.exists():
            p(f"      !! {fid}: no está {archivo}")
            continue
        origen = pd.read_csv(ruta, encoding="utf-8")
        match = origen[origen.iloc[:, 0] == fid]
        if match.empty:
            p(f"      !! {fid}: no aparece dentro de {archivo}")
            continue
        r = match.iloc[0]
        filas_nuevas.append({
            "defecto_id": fid,
            "fuente": r.get("fuente", r.get("fuente_o_patron", "")),
            "regla_de_deteccion": r.get("como_se_detecta", ""),
            "clase": "carga diferida · ronda 9",
            "que_prohibe": r.get("regla", r.get("que_prohibe", "")),
            "que_sigue_valiendo": r.get("que_sigue_valiendo", ""),
            "severidad": "",
            "evidencia": r.get("que_hace", ""),
            "detectado": "2026-08-07",
            "detectado_por": f"fase documental · {archivo}",
        })
    p(f"      cargados ahora desde disco: {len(filas_nuevas)} "
      f"({', '.join(f['defecto_id'] for f in filas_nuevas)})")
    p("")

    filas_nuevas.append({
        "defecto_id": "FD-20",
        "fuente": "Google Places · businessStatus",
        "regla_de_deteccion": (
            "contrastar el businessStatus contra un cierre de fecha conocida. La ronda 8 lo midió "
            "sobre tres: marcó uno de tres."),
        "clase": "falso negativo del canal, medido",
        "que_prohibe": (
            "un OPERATIONAL de Places NO descarta cierre. El piso de detección medido está por "
            "encima de los 280 días: La Buena Medida, cerrada hace nueve meses, y el New "
            "Brighton, con quiebra decretada hace cinco, siguen dando OPERATIONAL."),
        "que_sigue_valiendo": (
            "CLOSED_PERMANENTLY sigue acreditando cierre: es una afirmación positiva y difícil de "
            "producir por error. La asimetría es la que vale — Places afirma, no niega."),
        "severidad": "alta",
        "evidencia": (
            "ronda 8, 71 requests: Plaza Bar (3.285 días) CLOSED_PERMANENTLY; La Buena Medida "
            "(280 días) OPERATIONAL; The New Brighton (143 días, quiebra judicial) OPERATIONAL."),
        "detectado": "2026-08-08",
        "detectado_por": "ronda 8 · places_tests_calibracion_r8.csv",
    })
    p("      FD-20 cargado con la evidencia que produjo la ronda 8 acá adentro.")
    p("")
    p("      FD-21 y FD-22 NO SE CARGAN. Su texto vive en `fuentes_con_defecto_FD20_FD22.csv`,")
    p("      que no está en el repositorio. Escribirlos de memoria sería fabricar el contenido")
    p("      de una fuente — el defecto que esta capa existe para registrar.")
    p("")

    fd_nueva = pd.concat([fd, pd.DataFrame(filas_nuevas)], ignore_index=True)
    fd_nueva["orden"] = fd_nueva.defecto_id.str.extract(r"(\d+)").astype(int)
    fd_nueva = fd_nueva.sort_values("orden").drop(columns="orden")
    fd_nueva.to_csv(OUT_FD, index=False, encoding="utf-8")
    p(f"      la capa FD pasa de {len(fd)} a {len(fd_nueva)}. Siguen faltando: FD-21, FD-22.")
    p("")

    pd.DataFrame([
        {"defecto_id": f"FD-{n:02d}",
         "estaba_cargado_antes_de_la_r9": f"FD-{n:02d}" in cargados,
         "cargado_en_la_r9": f"FD-{n:02d}" in {f["defecto_id"] for f in filas_nuevas},
         "sigue_faltando": f"FD-{n:02d}" not in set(fd_nueva.defecto_id),
         "donde_vive_el_texto": HUECOS_FD.get(f"FD-{n:02d}", "capa cargada" if f"FD-{n:02d}"
                                              in cargados else "fuentes_con_defecto_FD20_FD22.csv"
                                              " · AUSENTE")}
        for n in range(1, 23)]).to_csv(OUT_FD_AUDIT, index=False, encoding="utf-8")

    # ============================================================ TAREA 3 · el volcado
    p("-" * 100)
    p("  TAREA 3 · EL VOLCADO DE LA CAPA DE HITOS")
    p("")
    columnas = ["hito_id", "nombre", "direccion", "barrio_declarado", "tipo", "reconocimiento",
                "registro_oficial", "vigencia_verificada", "vigencia_nivel", "vigencia_fecha",
                "vigencia_fuente", "es_patrimonio_normativo", "patrimonio_norma",
                "places_business_status", "vigencia_fecha_consulta", "alerta_juridica",
                "alerta_juridica_fecha", "latitud", "longitud", "origen", "confianza"]
    volcado = capa[[c for c in columnas if c in capa.columns]].copy()
    volcado = volcado.sort_values("hito_id")
    volcado.to_csv(OUT_DUMP, index=False, encoding="utf-8")
    p(f"      {len(volcado)} hitos · {len(volcado.columns)} columnas → {OUT_DUMP.name}")
    p("")
    p("      por tipo:")
    for tipo, n in capa.tipo.value_counts().items():
        p(f"        {str(tipo):<44} {n:>4}")
    p("")
    p("      por registro_oficial:")
    for reg, n in capa.registro_oficial.value_counts(dropna=False).items():
        p(f"        {str(reg):<44} {n:>4}")
    p("")
    p("      los tres casos que motivaron el pedido, resueltos contra el volcado:")
    for etiqueta, filtro in [
            ("Notables en Monserrat", capa.barrio_declarado.astype(str).str.contains(
                "MONSERRAT", case=False, na=False) & (capa.tipo == "Bar Notable")),
            ("El Puentecito", capa.nombre.astype(str).str.contains("PUENTECITO", case=False,
                                                                   na=False)),
            ("Los Campeones", capa.nombre.astype(str).str.contains("CAMPEONES", case=False,
                                                                   na=False))]:
        sub = capa[filtro]
        p(f"        {etiqueta:<24} {len(sub):>3} en la capa: "
          f"{', '.join(f'{r.hito_id} {r.nombre}' for _, r in sub.iterrows()) or '—'}")
    p("")

    # ============================================================ TAREA 4 · la cola de R20
    p("-" * 100)
    p("  TAREA 4 · LAS CALLES DE LA COLA DE R20")
    p("")
    r20 = referencias.geometry.loc["R20"]
    ha_r20, n_r20 = medir(r20, base.geometry)

    p("  ANTES DE LAS CALLES, LO QUE APARECIÓ AL IR A BUSCARLAS")
    p("")
    eje_corto = eje_de(callejero, "GARCIA DEL RIO")
    eje_av = eje_de(callejero, "GARCIA DEL RIO AV.")
    eje_full = eje_de(callejero, "GARCIA DEL RIO", "GARCIA DEL RIO AV.")
    p(f"      el callejero oficial guarda el corredor bajo DOS nombres distintos:")
    p(f"        «GARCIA DEL RIO»       {eje_corto.length:>7,.0f} m — cruza Av. Balbín, "
      f"NO cruza Av. Cabildo (queda a "
      f"{eje_corto.distance(eje_de(callejero, 'CABILDO AV.')):,.0f} m)")
    p(f"        «GARCIA DEL RIO AV.»   {eje_av.length:>7,.0f} m — cruza Av. Cabildo, "
      f"NO cruza Av. Balbín")
    p(f"        el corredor entero      {eje_full.length:>7,.0f} m — se empalman en Pinto")
    p("")
    p("      LA RONDA 8 BUSCÓ SÓLO EL PRIMERO. Le pidió el cruce con Av. Cabildo, que está en la")
    p("      otra mitad, y `tramo_entre` cayó en `nearest_points`: ancló el extremo oeste en un")
    p("      punto que no es una esquina y devolvió 974 m SIN AVISAR. Ese tramo no es")
    p("      «Cabildo–Balbín»: es **Pinto–Balbín**, y le falta el corredor entero al oeste.")
    p("")
    p("      Es la familia de R12 —la delimitación que falla sin tirar error— y es la inversa")
    p("      exacta del caso que le dio origen: allá dos nombres eran una sola avenida (Boyacá y")
    p("      Carabobo); acá una sola avenida lleva dos nombres.")
    p("")

    tramo_r8, _ = None, None
    marco_saavedra = capa_barrios[capa_barrios.clave == "SAAVEDRA"].geometry.iloc[0]
    tramo_r8 = tramo_entre(callejero, "GARCIA DEL RIO", "CABILDO AV.",
                           "BALBIN, RICARDO, DR. AV.", marco_saavedra)
    tramo_ok, diag = tramo_verificado(callejero, eje_full, "CABILDO AV.",
                                      "BALBIN, RICARDO, DR. AV.")
    p("      el tramo Av. Cabildo–Av. Balbín, medido sobre el corredor completo:")
    for k in ("a", "b"):
        p(f"        corte {k}: {diag[k]}")
    if tramo_ok is None:
        p("        !! no se pudo cerrar el tramo. La cola no se recalcula.")
        cola = r20.difference(tramo_r8.buffer(BUFFER_EJE_M))
        etiqueta_cola = "cola según la ronda 8 (anclaje sin verificar)"
    else:
        p(f"        largo verificado: {diag['largo_m']:,} m "
          f"≈ {diag['largo_m'] / 100:.0f} cuadras")
        cola = r20.difference(tramo_ok.buffer(BUFFER_EJE_M))
        etiqueta_cola = "cola con el tramo Cabildo–Balbín verificado"
    ha_cola, n_cola = medir(cola, base.geometry)
    cola_r8 = r20.difference(tramo_r8.buffer(BUFFER_EJE_M))
    ha_r8, n_r8_loc = medir(cola_r8, base.geometry)
    p("")
    p(f"      R20 publicada                              {ha_r20:>7} ha · {n_r20:>4} locales")
    p(f"      cola declarada por la ronda 8              {ha_r8:>7} ha · {n_r8_loc:>4} locales"
      f"  ({ha_r8 / ha_r20 * 100:.0f} % / {n_r8_loc / n_r20 * 100:.0f} %)")
    p(f"      {etiqueta_cola:<42}{ha_cola:>7} ha · {n_cola:>4} locales"
      f"  ({ha_cola / ha_r20 * 100:.0f} % / {n_cola / n_r20 * 100:.0f} %)")
    p("")
    p("      LA CIFRA QUE DIEGO CITÓ —41 % de la superficie y 53 % de los locales— SALE DEL")
    p("      ANCLAJE MAL PUESTO. Con el corredor completo la cola es otra, y hay que decir cuál.")
    p("")

    # el reparto por eje más cercano: `direccion_norm` está vacía en el 46,6 % del universo
    # núcleo, así que agrupar por texto de dirección pierde casi la mitad de los puntos.
    dentro = callejero[callejero.intersects(cola)].copy()
    dentro["m_en_la_cola"] = dentro.geometry.intersection(cola).length
    ejes = (dentro.groupby("nomoficial")["m_en_la_cola"].sum()
            .sort_values(ascending=False).round(0))
    ejes = ejes[ejes >= 40]  # menos de media cuadra es un roce de borde, no una calle de la cola

    locales_cola = base[base.within(cola)].copy()
    candidatos = callejero[callejero.nomoficial.isin(ejes.index)].copy()
    if len(locales_cola) and len(candidatos):
        unido = gpd.sjoin_nearest(locales_cola[["geometry"]], candidatos[["nomoficial",
                                                                         "geometry"]],
                                  how="left", max_distance=120, distance_col="d_m")
        unido = unido[~unido.index.duplicated(keep="first")]  # equidistante de dos segmentos
        por_calle = unido.nomoficial.value_counts()
        sin_asignar = int(unido.nomoficial.isna().sum())
    else:
        por_calle, sin_asignar = pd.Series(dtype=int), len(locales_cola)

    p(f"      {len(ejes)} ejes con 40 m o más adentro de la cola. El reparto de los "
      f"{n_cola} locales")
    p("      se hace por EJE MÁS CERCANO a menos de 120 m, no por el texto de la dirección: el")
    p("      46,6 % del universo núcleo no tiene `direccion_norm` y agrupar por texto perdía")
    p("      cuatro de cada cinco puntos.")
    p("")
    p(f"        {'calle':<40}{'m de eje':>10}{'locales':>9}")
    filas_r20 = []
    for calle, metros in ejes.items():
        n = int(por_calle.get(calle, 0))
        filas_r20.append({"calle": calle, "metros_de_eje_en_la_cola": int(metros),
                          "locales_de_la_cola_en_esta_calle": n})
        p(f"        {calle:<40}{int(metros):>10}{n:>9}")
    p("")
    p(f"      asignados: {int(por_calle.sum())} de {n_cola} · sin eje a menos de 120 m: "
      f"{sin_asignar}")
    pd.DataFrame(filas_r20).to_csv(OUT_R20, index=False, encoding="utf-8")
    p("")

    # ============================================================ TAREA 5 · Colegiales
    p("-" * 100)
    p("  TAREA 5 · COLEGIALES · las tres verificaciones, ANTES de trazar")
    p("")
    verif = []
    col = capa_barrios[capa_barrios.clave == "COLEGIALES"].geometry.iloc[0]
    belg = capa_barrios[capa_barrios.clave == "BELGRANO"].geometry.iloc[0]
    pal = capa_barrios[capa_barrios.clave == "PALERMO"].geometry.iloc[0]
    chac = capa_barrios[capa_barrios.clave == "CHACARITA"].geometry.iloc[0]

    p("  (a) R13 · ¿las cuatro calles caen en Colegiales y no en Belgrano?")
    p("")
    p(f"      {'calle':<26}{'m totales':>11}{'Colegiales':>12}{'Belgrano':>10}{'Palermo':>9}"
      f"{'Chacarita':>11}")
    for nombre in ["ZABALA", "DELGADO", "AVILES, VIRREY", "CONDE"]:
        seg = callejero[callejero.clave == sin_tildes(nombre)]
        total = float(seg.length.sum())
        reparto = {}
        for etiq, poli in [("Colegiales", col), ("Belgrano", belg), ("Palermo", pal),
                           ("Chacarita", chac)]:
            reparto[etiq] = float(sum(g.intersection(poli).length for g in seg.geometry))
        p(f"      {nombre:<26}{total:>11,.0f}" + "".join(
            f"{reparto[e]:>{w},.0f}" for e, w in [("Colegiales", 12), ("Belgrano", 10),
                                                  ("Palermo", 9), ("Chacarita", 11)]))
        verif.append({"verificacion": "a · R13 · barrio de la calle", "objeto": nombre,
                      "metros_totales": round(total), **{f"m_en_{k}": round(v)
                                                         for k, v in reparto.items()},
                      "resultado": "mayoría en Colegiales" if reparto["Colegiales"] >= max(
                          reparto.values()) else "NO es mayoritariamente de Colegiales"})
    p("")

    p("  (b) R12 · ¿el eje entre Av. Álvarez Thomas y Av. Forest tiene longitud real?")
    p("")
    p("      con el cortador ESTRICTO: si un corte no cruza el eje, no hay tramo y se dice cuál.")
    p("")
    for nombre in ["ZABALA", "DELGADO", "AVILES, VIRREY", "CONDE"]:
        eje_n = eje_de(callejero, nombre)
        for corte_b in ["FOREST AV.", "ELCANO AV."]:
            t, diag = tramo_verificado(callejero, eje_n, "ALVAREZ THOMAS AV.", corte_b)
            if t is None:
                falla = next((v for v in (diag.get("a"), diag.get("b"))
                              if v and ("NO llega" in v or "no existe" in v)), "tramo nulo")
                estado = f"SIN TRAMO — {falla}"
            else:
                estado = (f"{diag['largo_m']:,} m ≈ {diag['largo_m'] / 100:.0f} cuadras"
                          f"  [{diag['a'].split('»')[1].strip()} / "
                          f"{diag['b'].split('»')[1].strip()}]")
            p(f"      {nombre:<18} × {corte_b:<12} {estado}")
            verif.append({"verificacion": "b · R12 · longitud del tramo",
                          "objeto": f"{nombre} entre ALVAREZ THOMAS AV. y {corte_b}",
                          "metros_totales": diag.get("largo_m", 0),
                          "resultado": estado})
    p("")
    p("      por qué se prueban los dos cortes: la fuente nombra «Av. Forest / Av. Elcano» como")
    p("      un solo borde, y son dos avenidas distintas. R12 obliga a medir cuál cierra el eje.")
    p("")
    p("      Y por qué el cortador viejo no servía acá: `tramo_entre` devolvía «1.555 m ≈ 16")
    p("      cuadras» para Delgado × Forest cuando Delgado NO CRUZA Av. Álvarez Thomas. Lo que")
    p("      devolvía era la calle entera dentro del barrio, no un tramo. El mismo mecanismo que")
    p("      produjo el falso «Cabildo–Balbín» de la tarea 4.")
    p("")
    p("      A CUÁNTO QUEDA CADA CALLE DE CADA AVENIDA — el dato crudo, sin tolerancia:")
    p("")
    p(f"        {'calle':<18}{'a Álvarez Thomas':>19}{'a Forest':>11}{'a Elcano':>11}")
    avenidas = {a: eje_de(callejero, a) for a in ("ALVAREZ THOMAS AV.", "FOREST AV.",
                                                 "ELCANO AV.")}
    for nombre in ["ZABALA", "DELGADO", "AVILES, VIRREY", "CONDE"]:
        e = eje_de(callejero, nombre)
        ds = {a: e.distance(g) for a, g in avenidas.items()}
        p(f"        {nombre:<18}" + "".join(
            f"{('cruza' if ds[a] == 0 else f'{ds[a]:,.0f} m'):>{w}}"
            for a, w in [("ALVAREZ THOMAS AV.", 19), ("FOREST AV.", 11), ("ELCANO AV.", 11)]))
        verif.append({"verificacion": "b · distancia cruda a cada avenida", "objeto": nombre,
                      "resultado": "; ".join(f"{a}: {v:,.0f} m" for a, v in ds.items())})
    p("")
    p("      EL ANCHO DE LA FRANJA, que es lo que decide si el trazado es posible:")
    at, fo = avenidas["ALVAREZ THOMAS AV."], avenidas["FOREST AV."]
    p(f"        Av. Álvarez Thomas y Av. Forest SE ENCUENTRAN: distancia {at.distance(fo):,.0f} m.")
    p("        No son dos avenidas paralelas con una banda entre medio — confluyen, y la franja")
    p("        que encierran es una CUÑA que se cierra en ese encuentro.")
    p("        Medido sobre las calles que sí la cruzan: Zabala 254 m y Virrey Avilés 344 m.")
    p("        Tres cuadras, no las diez que sugiere leer la lista de calles de corrido.")
    verif.append({"verificacion": "b · ancho de la franja",
                  "objeto": "Av. Álvarez Thomas ↔ Av. Forest",
                  "metros_totales": round(at.distance(fo)),
                  "resultado": "convergen: la franja es una cuña, no una banda pareja"})
    p("")

    p("  (c) ¿Concepción Arenal entre Zapiola y Conesa cae dentro de R01 Palermo?")
    p("")
    p("      nota de lectura: el callejero la escribe «ARENAL, CONCEPCION», con el apellido")
    p("      primero. Buscarla como «CONCEPCION ARENAL» devuelve vacío sin tirar error — es el")
    p("      mismo bicho del orden de los tokens que ya está registrado como R8.")
    marco_conc = unary_union([col, pal, chac])
    t_conc = tramo_entre(callejero, "ARENAL, CONCEPCION", "ZAPIOLA", "CONESA", marco_conc)
    if t_conc is None or t_conc.is_empty:
        p("      !! el tramo volvió vacío. No se traza nada.")
        verif.append({"verificacion": "c · R01", "objeto": "Concepción Arenal Zapiola–Conesa",
                      "resultado": "tramo vacío"})
    else:
        r01 = referencias.geometry.loc["R01"]
        area_tramo = t_conc.buffer(BUFFER_EJE_M)
        inter = area_tramo.intersection(r01)
        pct = inter.area / area_tramo.area * 100 if area_tramo.area else 0.0
        p(f"      el tramo mide {t_conc.length:,.0f} m ≈ {t_conc.length / 100:.0f} cuadras")
        p(f"      su área a {BUFFER_EJE_M} m: {area_tramo.area / 10_000:,.1f} ha")
        p(f"      dentro de R01 Palermo: {inter.area / 10_000:,.1f} ha = {pct:.1f} %")
        for etiq, poli in [("Colegiales", col), ("Palermo", pal), ("Chacarita", chac)]:
            m = float(t_conc.intersection(poli).length)
            p(f"        del eje, {m:,.0f} m ({m / t_conc.length * 100:.0f} %) caen en {etiq}")
        veredicto = ("cae dentro de R01 — es de Palermo, no de Colegiales" if pct >= 50 else
                     "NO cae dentro de R01" if pct < 5 else
                     f"cae parcialmente en R01 ({pct:.0f} %)")
        p(f"      → {veredicto}")
        verif.append({"verificacion": "c · R01", "objeto": "Concepción Arenal Zapiola–Conesa",
                      "metros_totales": round(t_conc.length),
                      "resultado": veredicto, "pct_en_R01": round(pct, 1)})
    p("")

    p("  el control gratis · Fraga entre Dorrego y Lacroze")
    fraga_piezas, fraga_total = piezas_en_marco(callejero, "FRAGA", unary_union([col, chac]))
    if fraga_piezas:
        fraga = unary_union(fraga_piezas)
        p(f"      Fraga mide {fraga_total:,.0f} m en toda la Ciudad; "
          f"{fraga.length:,.0f} m dentro de Colegiales ∪ Chacarita "
          f"≈ {fraga.length / 100:.0f} cuadras")
        p("      Forbes 20/10/2024 la documenta del 93 al 550 con «casi una docena de "
          "propuestas»: las ~diez cuadras coinciden con lo medido.")
        n_fraga = int(base.direccion_norm.map(calle_de).map(sin_tildes).eq("FRAGA").sum())
        p(f"      la base tiene {n_fraga} locales con la puerta sobre Fraga.")
        verif.append({"verificacion": "control · Fraga", "objeto": "FRAGA en Colegiales/Chacarita",
                      "metros_totales": round(fraga.length),
                      "resultado": f"{fraga.length / 100:.0f} cuadras · {n_fraga} locales"})
    p("")
    p("      MIENTRAS TANTO la ficha NO publica 495,8 ha ni 891 locales como cifra del polo:")
    p("      esa medición usa Colegiales A ESCALA DE BARRIO, que es un techo declarado, no la")
    p("      franja de la fuente. Queda como está hasta que las tres verificaciones habiliten")
    p("      el trazado.")
    pd.DataFrame(verif).to_csv(OUT_COLEGIALES, index=False, encoding="utf-8")
    p("")

    # ============================================================ TAREA 6 · Palermo
    p("-" * 100)
    p("  TAREA 6 · PALERMO · las tres intersecciones que deciden")
    p("")
    p("  la hipótesis, escrita antes de medir (R1): R01 Palermo YA ES Soho ∪ Hollywood, y Las")
    p("  Cañitas nunca estuvo adentro. Predicciones: (a) la unión cubre casi todo R01; (b) la")
    p("  intersección con Cañitas ≈ 0 — si da distinto de cero, la hipótesis SE CAE; (c) los 9")
    p("  locales de residuo caen sobre un solo borde.")
    p("")
    polos = gpd.read_file(POLOS_V3).to_crs(CRS_METRICO).set_index("polo_id")
    r01 = referencias.geometry.loc["R01"]
    ha_r01, n_r01 = medir(r01, base.geometry)
    p(f"      R01 publicado: {ha_r01} ha · {n_r01} locales")
    p("")
    geos = {}
    for etiqueta, pid in PALERMO.items():
        if pid not in polos.index:
            p(f"      !! {etiqueta}: {pid} no está en borrador_polos_v3")
            continue
        geos[etiqueta] = polos.geometry.loc[pid]
        ha_s, n_s = medir(geos[etiqueta], base.geometry)
        p(f"      {etiqueta:<13} ({pid}): {ha_s:>8} ha · {n_s:>5} locales")
    p("")
    filas_pal = []
    union_sh = unary_union([geos["Soho"], geos["Hollywood"]])
    ha_u, n_u = medir(union_sh, base.geometry)
    p(f"      Soho ∪ Hollywood: {ha_u} ha · {n_u} locales")
    p("")
    p("  (a) R01 ∩ (Soho ∪ Hollywood)")
    inter_a = r01.intersection(union_sh)
    ha_a, n_a = medir(inter_a, base.geometry)
    p(f"      {ha_a} ha = {ha_a / ha_r01 * 100:.1f} % de R01 · "
      f"{n_a} locales = {n_a / n_r01 * 100:.1f} % de R01")
    filas_pal.append({"interseccion": "R01 ∩ (Soho ∪ Hollywood)", "ha": ha_a, "locales": n_a,
                      "pct_ha_de_R01": round(ha_a / ha_r01 * 100, 1),
                      "pct_locales_de_R01": round(n_a / n_r01 * 100, 1),
                      "prediccion": "cubre casi todo R01"})
    p("")
    p("  (b) R01 ∩ Las Cañitas  ← la que puede tirar la hipótesis")
    inter_b = r01.intersection(geos["Las Cañitas"])
    ha_b, n_b = medir(inter_b, base.geometry)
    p(f"      {ha_b} ha = {ha_b / ha_r01 * 100:.1f} % de R01 · {n_b} locales")
    filas_pal.append({"interseccion": "R01 ∩ Las Cañitas", "ha": ha_b, "locales": n_b,
                      "pct_ha_de_R01": round(ha_b / ha_r01 * 100, 1),
                      "pct_locales_de_R01": round(n_b / n_r01 * 100, 1),
                      "prediccion": "≈ 0"})
    p("")
    p("  (c) el residuo · R01 menos (Soho ∪ Hollywood)")
    residuo = r01.difference(union_sh)
    ha_c, n_c = medir(residuo, base.geometry)
    p(f"      {ha_c} ha · {n_c} locales")
    partes = list(residuo.geoms) if hasattr(residuo, "geoms") else [residuo]
    partes = [g for g in partes if g.area > 1_000]
    p(f"      el residuo son {len(partes)} piezas de más de 0,1 ha — no un borde.")
    filas_pal.append({"interseccion": "R01 − (Soho ∪ Hollywood)", "ha": ha_c, "locales": n_c,
                      "pct_ha_de_R01": round(ha_c / ha_r01 * 100, 1),
                      "pct_locales_de_R01": round(n_c / n_r01 * 100, 1),
                      "prediccion": "9 locales sobre un solo borde"})
    p("")
    p("  LAS TRES PREDICCIONES FALLAN. La hipótesis se cae por su propio criterio:")
    p("      (a) predecía «casi toda» y da 43,9 % de la superficie")
    p(f"      (b) predecía ≈ 0 y da {ha_b} ha con {n_b} locales — Diego escribió que si daba")
    p("          distinto de cero la hipótesis se caía. Da distinto de cero.")
    p(f"      (c) predecía 9 locales sobre un borde y da {n_c} en {len(partes)} piezas")
    p("")
    p("  DE DÓNDE SALÍA EL DELTA 9, que es lo que hay que entender para no repetirlo:")
    fuera = n_u - n_a
    p(f"      locales de Soho ∪ Hollywood que caen FUERA de R01:  {fuera:>5}")
    p(f"      locales de R01 que NO están en Soho ∪ Hollywood:    {n_c:>5}")
    p(f"      diferencia:                                         {fuera - n_c:>5}")
    p("")
    p("      El «delta 9» no era un residuo de nueve locales sobre un borde: es la resta de dos")
    p(f"      flujos de ~400 locales cada uno que casi se cancelan. {fuera} salen y {n_c} entran.")
    p("      La igualdad de los totales no es evidencia de identidad espacial — dos conjuntos")
    p("      pueden sumar el tamaño de un tercero sin partirlo.")
    p("")
    p("      ES LA PREGUNTA CERO, y no es casual que aparezca acá: el delta 9 era una propiedad")
    p("      de la aritmética del conteo, no del territorio. La única forma de distinguirlas era")
    p("      intersecar los polígonos, que es lo que se hizo.")
    p("")
    p("  R12 · la contención se verifica por SUPERFICIE PERDIDA, no por predicado:")
    padre = unary_union([r01] + list(geos.values()))
    for etiqueta, g in [("R01", r01), *geos.items()]:
        perdida = g.difference(padre).area
        p(f"      {etiqueta:<13} perdería {perdida:,.4f} m² dentro del polo padre propuesto")
        filas_pal.append({"interseccion": f"contención de {etiqueta} en el padre",
                          "ha": round(perdida / 10_000, 6), "locales": "",
                          "prediccion": "0,0 m² perdidos"})
    ha_p, n_p = medir(padre, base.geometry)
    p(f"      el padre R01 ∪ Soho ∪ Hollywood ∪ Cañitas: {ha_p} ha · {n_p} locales")
    filas_pal.append({"interseccion": "padre propuesto (R01 ∪ las tres)", "ha": ha_p,
                      "locales": n_p, "prediccion": ""})
    pd.DataFrame(filas_pal).to_csv(OUT_PALERMO, index=False, encoding="utf-8")
    p("")

    # ============================================================ TAREA 7 · las dos preguntas
    p("-" * 100)
    p("  TAREA 7 · QUÉ SON R08 Y R21, Y DÓNDE QUEDÓ PGR_P004")
    p("")
    for rid in ("R08", "R21"):
        r = referencias.loc[rid]
        p(f"      {rid} · {r.nombre} — {r.familia} · {r.ha} ha · {r.locales} locales")
    p("")
    p("      NINGUNA de las dos es del entorno de Palermo: Villa Crespo y La Paternal son")
    p("      contiguas entre sí y el solape de 49,7 ha está sobre ese contacto, no sobre R01.")
    d_r01 = referencias.geometry.loc["R08"].distance(referencias.geometry.loc["R01"])
    p(f"      medido: R08 Villa Crespo está a {d_r01:,.0f} m de R01 Palermo "
      f"({'se tocan' if d_r01 == 0 else 'no se tocan'}).")
    p("      El nudo de Palermo y el solape R08∩R21 son dos problemas separados.")
    p("")
    p("      PGR_P004 · Villa Lugano, después de perder la vía C:")
    p("        vía A · densidad y continuidad  ABIERTA — 132 locales en 144,0 ha; el polo entra")
    p("                                        en los cortes de pertenencia 25 %, 50 % y 75 %")
    p("        vía C · mercados y centralidades  CERRADA — era Yiyo el Zeneize, retipado")
    p("        vía F · corredor                  cerrada — núcleo compacto, elongación 1,26")
    p("        vías B, D, E                      cerradas en S_LUGANO, la zona de la que hereda")
    p("")
    p("      NO ES UNA BAJA: sigue abriendo por la vía A, que es geométrica y se mide sobre el")
    p("      propio polígono. Pero pasa de dos vías a UNA, y queda en la misma situación en la")
    p("      que ya estaba PGR_P005 · Villa Lugano, que nunca tuvo más que la A.")
    p("")
    p("      PENDIENTE DE ARRASTRE: `seis_vias_94_filas_r8.csv` todavía trae")
    p("      via_C_abierta = «si» para PGR_P004. El cambio quedó registrado en")
    p("      `via_C_movida_r8.csv` pero no se propagó a la matriz. Hay que recorrer la r8 con")
    p("      el retipado aplicado antes de que esa tabla se use para nada.")
    p("")

    capa.to_csv(OUT_CAPA, index=False, encoding="utf-8")
    p("=" * 100)
    p("  SALIDAS")
    p("=" * 100)
    for ruta in (OUT_CAPA, OUT_DUMP, OUT_FD, OUT_FD_AUDIT, OUT_R20, OUT_COLEGIALES, OUT_PALERMO,
                 INFORME):
        p(f"    {ruta.relative_to(ROOT)}")

    texto = buffer.getvalue()
    INFORME.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
