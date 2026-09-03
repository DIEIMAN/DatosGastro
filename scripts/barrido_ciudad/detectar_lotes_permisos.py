"""Detector de lotes de permisos en el padrón de habilitaciones.

El caso R18 · Esmeralda-Paraguay mostró el patrón: once direcciones con exactamente 120
habilitaciones cada una, la misma mezcla de rubros, todas sin fecha de habilitación, sobre números
consecutivos de la misma cuadra de Florida y Av. Córdoba. No son 120 locales por puerta: es un
lote de permisos de un complejo cargado contra cada número del frente de manzana.

Esto no es un problema del Atlas, es un problema de calidad del padrón, y le sirve a la Dirección
más allá de este trabajo. El detector recorre las direcciones anómalas —más de 20 habilitaciones,
regla 3 del método— y las agrupa en lotes según cuatro señales, informando cada una por separado
para que el caso se pueda revisar y no haya que creerle al puntaje:

  1. firma de rubros idéntica: mismo total de habilitaciones y misma mezcla de categorías
  2. **partida matriz compartida**: varias direcciones distintas cuelgan de la misma partida, o
     sea del mismo inmueble. Es la prueba de propiedad, no un indicio.
  3. sin fecha de habilitación en la enorme mayoría de los registros
  4. direcciones consecutivas de la misma cuadra: misma calle, misma centena de altura

Sobre la señal 2: el `id_habilitacion` del modelo es una clave nuestra, no el número de
expediente, así que no sirve para medir correlatividad —probarlo daba tiradas de largo 1—. El
número de partida sí viene en el crudo de 2025 (`nropartidamatriz`), que es justo la cohorte donde
están los lotes.

Privacidad: los crudos de F02 traen `titulares`, `cuits` y `telefono`. **No se leen ni se
exportan.** De `razon_social` sólo se informa el conteo de valores distintos, nunca los valores:
alcanza para distinguir un complejo real de una carga replicada. Lo que se publica es dirección
del inmueble, partida, conteos y rubros.

Uso:
  python scripts/barrido_ciudad/detectar_lotes_permisos.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_capa_homogenea import (  # noqa: E402
    BARRIOS,
    UBICACION,
    UMBRAL_OUTLIER,
    cargar_direcciones_gastronomicas,
)

OUT_DIR = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "generado"
# Crudo de la cohorte 2025, la única que trae número de partida matriz. Se leen sólo tres
# columnas: domicilio, partida y razón social (de esta última, únicamente el conteo de distintos).
# `titulares`, `cuits` y `telefono` no se leen.
F02_2025 = ROOT / "data" / "raw" / "f02_habilitaciones_aprobadas_2025.csv"
COLUMNAS_CRUDO = ["domicilio", "nropartidamatriz", "razon_social", "rubro"]

SIN_FECHA = {"No disponible", "nan", "No informada", ""}


def partir_direccion(direccion: str) -> tuple[str, int | None]:
    """Separa calle y altura de una dirección normalizada del padrón."""
    texto = str(direccion).replace(", CABA", "").strip()
    match = re.search(r"(\d+)\s*$", texto)
    if not match:
        return texto, None
    return texto[: match.start()].strip().rstrip(",").strip(), int(match.group(1))


def firma_rubros(grupo: pd.DataFrame) -> str:
    """Total y mezcla de categorías de una dirección, como texto comparable."""
    mezcla = grupo.categoria_gastronomica_inferida.value_counts().sort_index()
    return f"{len(grupo)}|" + ",".join(f"{k}:{v}" for k, v in mezcla.items())


def cargar_partidas() -> pd.DataFrame:
    """Partida matriz por domicilio, desde el crudo de 2025. Sin titulares, cuits ni teléfonos."""
    crudo = pd.read_csv(F02_2025, low_memory=False, encoding="utf-8", usecols=COLUMNAS_CRUDO)
    crudo["domicilio"] = crudo.domicilio.astype(str).str.strip()
    return crudo


def perfilar_anomalas() -> pd.DataFrame:
    """Una fila por dirección anómala, con las cuatro señales medidas."""
    puntos, habilitaciones = cargar_direcciones_gastronomicas()
    anomalas = puntos[puntos.es_outlier]

    ubicaciones = pd.read_csv(UBICACION, low_memory=False).set_index("id_ubicacion")
    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]].rename(columns={"nombre": "barrio"})
    anomalas = gpd.sjoin(anomalas, barrios, how="left", predicate="within")

    crudo = cargar_partidas()
    por_domicilio = crudo.groupby("domicilio")
    # Cuántas direcciones distintas cuelgan de cada partida: si una partida abarca varias, esas
    # direcciones son el mismo inmueble cargado varias veces.
    direcciones_por_partida = crudo.groupby("nropartidamatriz").domicilio.nunique()

    filas = []
    for fila in anomalas.itertuples():
        grupo = habilitaciones[habilitaciones.id_ubicacion == fila.id_ubicacion]
        direccion = str(ubicaciones.loc[fila.id_ubicacion, "direccion_normalizada"])
        limpia = direccion.replace(", CABA", "").strip()
        calle, altura = partir_direccion(direccion)
        sin_fecha = grupo.fecha_habilitacion.astype(str).isin(SIN_FECHA).mean()

        partidas = razones = alcance = None
        if limpia in por_domicilio.groups:
            registros = por_domicilio.get_group(limpia)
            partidas = int(registros.nropartidamatriz.nunique())
            razones = int(registros.razon_social.nunique())
            alcance = int(direcciones_por_partida.reindex(
                registros.nropartidamatriz.dropna().unique()).max())

        filas.append({
            "id_ubicacion": fila.id_ubicacion,
            "direccion": limpia,
            "calle": calle,
            "altura": altura,
            "cuadra": None if altura is None else (altura // 100) * 100,
            "barrio": fila.barrio,
            "habilitaciones": int(fila.habilitaciones),
            "firma": firma_rubros(grupo),
            "pct_sin_fecha": round(100 * sin_fecha, 1),
            "partidas_matriz": partidas,
            "direcciones_con_esa_partida": alcance,
            "razones_sociales": razones,
            "anios_fuente": "/".join(sorted(grupo.anio_fuente.astype(str).unique())),
        })
    return pd.DataFrame(filas)


def agrupar_lotes(anomalas: pd.DataFrame) -> pd.DataFrame:
    """Agrupa en lotes las direcciones que comparten firma y cuadra.

    Un lote necesita las dos cosas: la misma firma de rubros —mismo total y misma mezcla— y la
    misma cuadra. La firma sola juntaría direcciones parecidas de puntas opuestas de la Ciudad; la
    cuadra sola juntaría vecinos con trámites propios.
    """
    anomalas = anomalas.copy()
    anomalas["clave_lote"] = anomalas.firma + " @ " + anomalas.calle + " " + anomalas.cuadra.astype(str)
    tamanos = anomalas.clave_lote.value_counts()
    anomalas["direcciones_en_lote"] = anomalas.clave_lote.map(tamanos)

    lotes = anomalas[anomalas.direcciones_en_lote > 1].copy()
    orden = {clave: i + 1 for i, clave in enumerate(
        lotes.groupby("clave_lote").habilitaciones.sum().sort_values(ascending=False).index
    )}
    lotes["lote"] = lotes.clave_lote.map(lambda c: f"L{orden[c]:02d}")
    return lotes.sort_values(["lote", "altura"])


def evidencia_replicacion(lotes: pd.DataFrame, crudo: pd.DataFrame) -> pd.DataFrame:
    """Mide, por lote, cuánto de la carga es repetición del mismo permiso en otra puerta.

    Es el test que decide el caso. Se cuentan los pares (razón social, rubro) distintos del lote y
    se compara contra la cantidad de registros: si 5.321 registros se reducen a 29 pares, la carga
    está replicando el mismo permiso puerta por puerta. Se informan conteos, nunca los valores.
    """
    filas = {}
    for lote, grupo in lotes.groupby("lote"):
        registros = crudo[crudo.domicilio.isin(set(grupo.direccion))]
        if not len(registros):
            continue
        pares = registros.groupby(["razon_social", "rubro"], dropna=False).domicilio.nunique()
        filas[lote] = {
            "registros_crudos": len(registros),
            "pares_distintos": len(pares),
            "pct_registros_repetidos": round(100 * (len(registros) - len(pares)) / len(registros), 1),
            "pares_en_varias_direcciones_pct": round(100 * (pares > 1).mean(), 1),
            "max_direcciones_por_par": int(pares.max()),
        }
    return pd.DataFrame(filas).T


def main() -> int:
    buffer = io.StringIO()

    def p(*args):
        print(*args, file=buffer)

    anomalas = perfilar_anomalas()
    lotes = agrupar_lotes(anomalas)
    replicacion = evidencia_replicacion(lotes, cargar_partidas())
    _, habilitaciones = cargar_direcciones_gastronomicas()
    total_registros = len(habilitaciones)

    p("Detector de lotes de permisos · padrón de habilitaciones gastronómicas")
    p("=" * 78)
    p("")
    p(f"direcciones anómalas examinadas (más de {UMBRAL_OUTLIER} habilitaciones): {len(anomalas)}")
    p(f"  suman {int(anomalas.habilitaciones.sum()):,} habilitaciones = "
      f"{100 * anomalas.habilitaciones.sum() / total_registros:.1f} % del padrón georreferenciado")
    p("")
    p(f"agrupadas en lotes (misma firma de rubros y misma cuadra): {lotes.lote.nunique()} lotes, "
      f"{len(lotes)} direcciones")
    p(f"  suman {int(lotes.habilitaciones.sum()):,} habilitaciones = "
      f"{100 * lotes.habilitaciones.sum() / total_registros:.1f} % del padrón georreferenciado")
    p("")
    if len(replicacion):
        p("EL TEST QUE DECIDE: cuánto de la carga es el mismo permiso repetido en otra puerta")
        p(f"  sobre los {len(replicacion)} lotes con crudo disponible:")
        p(f"    registros crudos involucrados: {int(replicacion.registros_crudos.sum()):,}")
        p(f"    permisos distintos detrás de esos registros: {int(replicacion.pares_distintos.sum()):,}")
        p(f"    proporción de registros que son repetición: mediana "
          f"{replicacion.pct_registros_repetidos.median():g} %, mínimo "
          f"{replicacion.pct_registros_repetidos.min():g} %")
        p(f"    un mismo permiso llega a figurar en hasta "
          f"{int(replicacion.max_direcciones_por_par.max())} puertas distintas")
        p("")
    p("Las señales, sobre las direcciones agrupadas en lotes:")
    p(f"  sin fecha de habilitación en el 100 % de sus registros: "
      f"{int((lotes.pct_sin_fecha == 100).sum())} de {len(lotes)} direcciones")
    con_partida = lotes[lotes.partidas_matriz.notna()]
    p(f"  con partida matriz identificable en el crudo 2025: {len(con_partida)} de {len(lotes)}")
    if len(con_partida):
        comparten = con_partida[con_partida.direcciones_con_esa_partida > 1]
        p(f"  cuya partida abarca más de una dirección: {len(comparten)} de {len(con_partida)} "
          f"— o sea, el mismo inmueble cargado en varias puertas")
        p(f"  máximo de direcciones colgadas de una sola partida: "
          f"{int(con_partida.direcciones_con_esa_partida.max())}")
        p(f"  partidas distintas por dirección: mediana {con_partida.partidas_matriz.median():g}, "
          f"máximo {int(con_partida.partidas_matriz.max())}")
    p("")

    p("LOTES DETECTADOS, con nombre y apellido")
    p("")
    for lote, grupo in lotes.groupby("lote"):
        primera = grupo.iloc[0]
        total, mezcla = primera.firma.split("|", 1)
        p(f"{lote} · {primera.calle} {int(primera.cuadra)}-{int(primera.cuadra) + 99} · "
          f"{primera.barrio}")
        p(f"    {len(grupo)} direcciones × {total} habilitaciones = "
          f"{int(grupo.habilitaciones.sum()):,} registros")
        p(f"    alturas: {', '.join(str(int(a)) for a in sorted(grupo.altura))}")
        p(f"    mezcla de rubros idéntica en todas: {mezcla}")
        p(f"    sin fecha de habilitación: {grupo.pct_sin_fecha.min():g}–{grupo.pct_sin_fecha.max():g} % "
          f"| años de fuente: {'/'.join(sorted(set(grupo.anios_fuente)))}")
        if grupo.partidas_matriz.notna().any():
            p(f"    partida matriz: hasta {int(grupo.partidas_matriz.max())} por dirección; la "
              f"partida más extendida abarca {int(grupo.direcciones_con_esa_partida.max())} "
              "direcciones del padrón")
        if lote in replicacion.index:
            r = replicacion.loc[lote]
            p(f"    replicación: {int(r.registros_crudos):,} registros crudos en estas direcciones "
              f"se reducen a {int(r.pares_distintos)} permisos distintos "
              f"({r.pct_registros_repetidos:g} % son repetición); un mismo permiso figura en hasta "
              f"{int(r.max_direcciones_por_par)} puertas")
        p("")

    sueltas = anomalas[~anomalas.id_ubicacion.isin(lotes.id_ubicacion)]
    sospechosas = sueltas[(sueltas.pct_sin_fecha == 100) &
                          (sueltas.direcciones_con_esa_partida.fillna(0) > 1)]
    p("DIRECCIONES ANÓMALAS SUELTAS CON LAS MISMAS SEÑALES")
    p("  No forman lote porque no comparten cuadra con otra, pero la carga tiene la misma pinta:")
    p("  sin fecha en el 100 % de los registros y partida matriz compartida con otra dirección.")
    p("")
    columnas = ["direccion", "barrio", "habilitaciones", "partidas_matriz",
                "direcciones_con_esa_partida", "anios_fuente"]
    p(sospechosas.sort_values("habilitaciones", ascending=False)[columnas].to_string(index=False))
    p("")
    p(f"  son {len(sospechosas)} direcciones con {int(sospechosas.habilitaciones.sum()):,} "
      f"habilitaciones = {100 * sospechosas.habilitaciones.sum() / total_registros:.1f} % del padrón")
    p("")
    p("QUÉ HACER CON ESTO")
    p("  La regla 3 del método ya las saca del conteo de direcciones, así que ninguna cifra")
    p("  publicada está afectada. Lo que hay que revisar es al revés: la columna")
    p("  `habilitaciones` no sirve como indicador de volumen en zonas con lotes, y conviene")
    p("  mostrarla siempre al lado de `dir_outlier`. El listado de acá se puede pasar a la AGC")
    p("  como consulta de calidad de carga del padrón.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    anomalas.to_csv(OUT_DIR / "direcciones_anomalas_324.csv", index=False, encoding="utf-8")
    lotes.drop(columns=["clave_lote"]).to_csv(
        OUT_DIR / "lotes_permisos_detectados.csv", index=False, encoding="utf-8")
    replicacion.rename_axis("lote").to_csv(
        OUT_DIR / "lotes_permisos_replicacion.csv", encoding="utf-8")
    (OUT_DIR / "LOTES_PERMISOS.txt").write_text(buffer.getvalue(), encoding="utf-8")

    print(buffer.getvalue())
    print(f"escrito en {OUT_DIR.relative_to(ROOT)}: direcciones_anomalas_324.csv, "
          "lotes_permisos_detectados.csv, LOTES_PERMISOS.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
