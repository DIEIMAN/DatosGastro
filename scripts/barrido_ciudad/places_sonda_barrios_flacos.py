"""La sonda de Places sobre los 5 barrios más flacos de la base. AUTORIZADA: 97 requests.

QUÉ ES ESTA CORRIDA Y POR QUÉ SE HACE ASÍ
------------------------------------------
Por decisión de alcance no habrá denominador externo de completitud —ni INDEC, ni APRA, ni AGIP, ni
Estadística y Censos—. **Places pasa a ocupar ese lugar**: no como sustituto del INDEC, que no lo
es, sino como lo que se puede hacer sin él — una **sonda de descubrimiento** en los barrios donde
la base está más flaca.

La selección la hizo `places_criterio_destino.py` con un criterio declarado antes de mirar qué
barrios salían: intersección del tercio más bajo de `aporte_otras_fuentes` y de `pct_padron`.

Y LAS DOS LECTURAS ESTÁN ESCRITAS ANTES DE CORRER, para que el resultado sea falsable:
  · fracción nueva BAJA → la base está más completa de lo que podíamos afirmar, y la afirmación
    pasa a tener respaldo propio;
  · fracción nueva ALTA → hay faltante, y queda localizado y con tamaño.
Ninguna de las dos se puede anticipar y las dos son publicables.

LO QUE ESTA CORRIDA NO PUEDE DECIR, y no se relitiga
-----------------------------------------------------
**Places aporta descubrimiento, NO vigencia.** Ya está medido: la mediana de lo que trae no está
en el padrón (62,5 %) y sólo confirma el 11 % del padrón. Ningún resultado de acá se puede leer
como que un local siga abierto.

Y **lo que traiga no entra a la base**: la licencia de Places no es redistribuible y por eso la
base se construyó sin él. El producto es un número de diagnóstico, no puntos. Por eso la salida va
a `outputs/analisis_interno/`, que está ignorada por Git.

LAS SALVAGUARDAS, QUE SON LA PARTE QUE IMPORTA
-----------------------------------------------
- **Presupuesto duro.** `PRESUPUESTO_AUTORIZADO` es lo que autorizó Diego. Si la corrida se desvía
  más de `DESVIO_TOLERADO`, **se corta sola** y deja escrito dónde quedó. Nunca se gasta de más
  «porque faltaba poco».
- **La key no se imprime, no se guarda y no se loguea.** Se lee de `.env` al entorno del proceso.
- **Sin `--run` no se ejecuta nada.** El default es dry-run.
- **Cada página es un request** y se cuentan páginas, no celdas: Text Search pagina hasta 3 veces.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/places_sonda_barrios_flacos.py          # dry-run
  .venv/Scripts/python.exe scripts/barrido_ciudad/places_sonda_barrios_flacos.py --run    # ejecuta
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import BARRIDO, CRS_METRICO, plegar  # noqa: E402
from places_control_zonas import (  # noqa: E402
    CONSULTA_GENERICA, LADO_BASE_M, LADO_REFINO_M, PAUSA_S, UMBRAL_SATURACION,
    AMPLIADO, EXCLUIDOS, NUCLEO, a_rectangulo, cargar_dotenv, celdas_de,
    consultar_celda,
)

BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
SELECCION = BARRIDO / "places_criterio_destino" / "barrios_seleccionados.csv"
BASE = BARRIDO / "base" / "local.csv"
# Salida interna: lo que trae Places no es redistribuible y no entra al repositorio.
INTERNO = ROOT / "outputs" / "analisis_interno" / "places_sonda_barrios_2026-08"

PRESUPUESTO_AUTORIZADO = 97     # lo que autorizó Diego, con el dry-run en la mano
YA_GASTADO_EN_ESTA_SONDA = 37   # primera corrida, perdida por leer `primaryType` en
                                # vez de `types`. Se descuenta: el techo es el de la
                                # autorización, no el de cada intento.
DESVIO_TOLERADO = 0.20          # si se pasa de esto, se corta

# Cuándo se considera que un punto de Places «ya lo teníamos». La base está deduplicada por
# dirección normalizada, así que el cruce se hace por proximidad: dos fichas del mismo local rara
# vez caen a más de 40 m una de otra, y ése es el radio que ya usó el cruce con el padrón.
RADIO_COINCIDENCIA_M = 40.0


def plan() -> gpd.GeoDataFrame:
    """Las celdas de 1 km sobre los 5 barrios seleccionados."""
    elegidos = pd.read_csv(SELECCION, index_col=0)
    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]].to_crs(CRS_METRICO)
    barrios["barrio_k"] = barrios.nombre.map(plegar)
    barrios = barrios[barrios.barrio_k.isin(elegidos.index)]

    filas = []
    for barrio in barrios.itertuples():
        for celda in celdas_de(barrio.geometry, LADO_BASE_M, barrio.barrio_k.replace(" ", "")[:8]):
            celda["barrio"] = barrio.nombre
            celda["barrio_k"] = barrio.barrio_k
            filas.append(celda)
    return gpd.GeoDataFrame(filas, geometry="geometry", crs=CRS_METRICO)


def anillo_de(tipos: list[str]) -> str:
    """A qué anillo del universo pertenece un punto de Places, según sus `types`.

    Es lo que decide si un punto «nuevo» es un local que nos falta o un comercio que nunca estuvo
    en nuestro universo. Sin esta columna, la fracción nueva mezcla las dos cosas y no se puede
    leer: la consulta «restaurantes bares y cafés» devuelve también kioscos, dietéticas y
    delivery, que el proyecto excluye por definición y no por omisión.
    """
    conjunto = set(tipos or [])
    if conjunto & EXCLUIDOS:
        return "excluido"
    if conjunto & NUCLEO:
        return "nucleo"
    if conjunto & AMPLIADO:
        return "ampliado"
    return "fuera_del_universo"


def base_del_barrio() -> gpd.GeoDataFrame:
    """Los locales de la base en los barrios de la sonda, para medir qué es nuevo."""
    base = pd.read_csv(BASE, low_memory=False)
    base = base[base.anillo == "nucleo"]
    base["barrio_k"] = base.barrio.map(plegar)
    return gpd.GeoDataFrame(
        base, geometry=gpd.points_from_xy(base.lon, base.lat), crs="EPSG:4326").to_crs(CRS_METRICO)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true",
                        help="ejecuta de verdad; sin esto es dry-run y no gasta nada")
    parser.add_argument("--solo-analisis", action="store_true",
                        help="rehace el informe desde los crudos ya guardados, sin consultar nada")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    celdas = plan()
    lineas = []

    def p(*args_):
        texto = " ".join(str(a) for a in args_)
        lineas.append(texto)
        print(texto)

    p("SONDA DE PLACES SOBRE LOS 5 BARRIOS MÁS FLACOS DE LA BASE")
    p("=" * 100)
    p("")
    p(f"  presupuesto autorizado : {PRESUPUESTO_AUTORIZADO} requests")
    p(f"  corte automático       : {int(PRESUPUESTO_AUTORIZADO * (1 + DESVIO_TOLERADO))} "
      f"(+{DESVIO_TOLERADO:.0%})")
    p(f"  celdas planificadas    : {len(celdas)} de {celdas.barrio.nunique()} barrios")
    p(f"  consulta               : «{CONSULTA_GENERICA}»")
    p("")
    p(celdas.groupby("barrio").size().rename("celdas").to_string())
    p("")

    # Adquisición y análisis están separados a propósito. La primera corrida se perdió por leer
    # la clave equivocada del JSON, y rehacer el INFORME no puede costar requests: con los crudos
    # guardados, cualquier cambio de lectura se rehace gratis.
    crudo_guardado = INTERNO / "places_crudos.csv"
    if args.solo_analisis:
        if not crudo_guardado.exists():
            p(f"falta {crudo_guardado.name}: no hay crudos para reanalizar.")
            return 1
        crudos = pd.read_csv(crudo_guardado)
        gastados, incidencias, inicio = 0, ["reanálisis desde crudos, 0 requests"],             datetime.now(timezone.utc)
        p("REANÁLISIS desde crudos guardados · 0 requests")
        return informe(crudos, celdas, gastados, incidencias, inicio, p, lineas)

    if not args.run:
        p("DRY-RUN · no se ejecutó ninguna llamada. Para ejecutar: --run")
        return 0

    cargar_dotenv()
    import os
    if not os.environ.get("GOOGLE_MAPS_API_KEY", "").strip():
        p("ABORTADO: falta GOOGLE_MAPS_API_KEY. No se ejecutó nada.")
        return 1
    clave = os.environ["GOOGLE_MAPS_API_KEY"]

    INTERNO.mkdir(parents=True, exist_ok=True)
    tope = int(PRESUPUESTO_AUTORIZADO * (1 + DESVIO_TOLERADO)) - YA_GASTADO_EN_ESTA_SONDA
    gastados, registros, incidencias = 0, [], []
    inicio = datetime.now(timezone.utc)

    def barrer(cola: list, etapa: str) -> list:
        """Consulta una tanda de celdas. Devuelve las que saturaron, para refinarlas.

        Una celda que devuelve 50 o más resultados probablemente chocó contra el techo de 60 de
        Text Search, y entonces su conteo es una cota inferior: no sabemos cuánto más había. Se
        refina partiéndola en cuatro, que es lo que ya hace el barrido de las 22 zonas. Sin este
        paso, la «fracción nueva» sale sesgada justo en las celdas con más oferta.
        """
        nonlocal gastados
        saturadas = []
        for celda in cola:
            if gastados >= tope:
                incidencias.append(
                    f"CORTE por presupuesto en {celda['celda_id']} ({etapa}): {gastados} ≥ {tope}")
                break
            lugares, usados, error = consultar_celda(clave, a_rectangulo(celda["geometry"]))
            gastados += usados
            if error:
                incidencias.append(f"{celda['celda_id']}: {error}")
            for lugar in lugares:
                ubicacion = lugar.get("location", {})
                # `types` y NO `primaryType`: el FieldMask de `places_control_zonas` pide
                # `places.types`, y `primaryType` no se pidió. Leer la clave equivocada devuelve
                # None en todas las filas sin que nada falle, y deja el resultado sin rubro —o
                # sea, sin poder distinguir un restaurante de un kiosco—. Pasó en la primera
                # corrida y costó repetirla.
                registros.append({
                    "celda_id": celda["celda_id"], "barrio": celda["barrio"], "etapa": etapa,
                    "place_id": lugar.get("id"),
                    "lon": ubicacion.get("longitude"), "lat": ubicacion.get("latitude"),
                    "tipos": ";".join(lugar.get("types", [])),
                    "anillo": anillo_de(lugar.get("types", [])),
                    "estado": lugar.get("businessStatus"),
                })
            if len(lugares) >= UMBRAL_SATURACION:
                saturadas.append(celda)
                incidencias.append(
                    f"{celda['celda_id']}: {len(lugares)} resultados, posible saturación del techo "
                    "de 60 — se refina a 500 m")
            time.sleep(PAUSA_S)
        return saturadas

    base_cola = [dict(celda_id=c.celda_id, barrio=c.barrio, geometry=c.geometry)
                 for c in celdas.itertuples()]
    saturadas = barrer(base_cola, "base_1km")

    # Refinamiento: sólo donde saturó, y sólo si queda presupuesto. No se planifica de antemano
    # porque no se sabe dónde va a saturar hasta consultarlo.
    if saturadas and gastados < tope:
        refino = []
        for celda in saturadas:
            for sub in celdas_de(celda["geometry"], LADO_REFINO_M, celda["celda_id"] + "r"):
                sub["barrio"] = celda["barrio"]
                refino.append(sub)
        p(f"  refinando {len(saturadas)} celdas saturadas → {len(refino)} subceldas de "
          f"{LADO_REFINO_M:.0f} m")
        barrer(refino, "refino_500m")
    elif saturadas:
        incidencias.append(
            f"{len(saturadas)} celdas saturaron y NO se refinaron por presupuesto agotado: sus "
            "conteos son cotas inferiores")

    crudos = pd.DataFrame(registros)
    INTERNO.mkdir(parents=True, exist_ok=True)
    crudos.to_csv(INTERNO / "places_crudos.csv", index=False, encoding="utf-8")
    return informe(crudos, celdas, gastados, incidencias, inicio, p, lineas)


def informe(crudos, celdas, gastados, incidencias, inicio, p, lineas) -> int:
    """El informe, calculado desde los crudos. No consulta nada."""
    p("EJECUCIÓN")
    p("=" * 100)
    p("")
    p(f"  requests gastados : {gastados} de {PRESUPUESTO_AUTORIZADO} autorizados "
      f"({gastados / PRESUPUESTO_AUTORIZADO * 100:.1f} %)")
    p(f"  celdas consultadas: {crudos.celda_id.nunique() if len(crudos) else 0} de {len(celdas)}")
    p(f"  puntos traídos    : {len(crudos)} ({crudos.place_id.nunique() if len(crudos) else 0} únicos)")
    p(f"  duración          : {(datetime.now(timezone.utc) - inicio).seconds} s")
    p("")
    if incidencias:
        p("  INCIDENCIAS")
        for incidencia in incidencias:
            p(f"    {incidencia}")
        p("")

    if not len(crudos):
        p("  Sin resultados. No se puede medir nada.")
        (INTERNO / "SONDA_PLACES.txt").write_text("\n".join(lineas), encoding="utf-8")
        return 1

    # --- la medición: qué fracción de lo que trae Places NO está en la base
    unicos = crudos.dropna(subset=["lon", "lat"]).drop_duplicates("place_id")
    puntos = gpd.GeoDataFrame(
        unicos, geometry=gpd.points_from_xy(unicos.lon, unicos.lat),
        crs="EPSG:4326").to_crs(CRS_METRICO)
    base = base_del_barrio()
    base = base[base.barrio_k.isin(celdas.barrio_k.unique())]

    cerca = gpd.sjoin_nearest(puntos, base[["local_id", "geometry"]],
                              max_distance=RADIO_COINCIDENCIA_M, how="left")
    cerca = cerca.drop_duplicates("place_id")
    cerca["ya_estaba"] = cerca.local_id.notna()

    resumen = cerca.groupby("barrio").agg(
        places=("place_id", "size"), ya_estaba=("ya_estaba", "sum"))
    resumen["nuevos"] = resumen.places - resumen.ya_estaba
    resumen["pct_nuevos"] = (resumen.nuevos / resumen.places * 100).round(1)
    resumen["base_nucleo"] = resumen.index.map(
        base.groupby("barrio").local_id.count())

    p("  QUÉ TRAJO, BARRIO POR BARRIO · todos los puntos, sin filtrar por rubro")
    p(f"    «ya estaba» = hay un local de la base a menos de {RADIO_COINCIDENCIA_M:.0f} m")
    p(resumen.to_string())
    p("")

    # EL FILTRO QUE HACE INTERPRETABLE EL NÚMERO. La consulta «restaurantes bares y cafés» trae
    # también almacenes, vinotecas y delivery, que el proyecto EXCLUYE por definición y no por
    # omisión. Contarlos como «faltante» convertiría una diferencia de universo en un agujero de
    # cobertura, que es exactamente el error que la base viene evitando desde el principio.
    p("  DE QUÉ RUBRO ES LO QUE TRAJO · sin esto el número anterior no se puede leer")
    p(cerca.groupby(["anillo", "ya_estaba"]).size().unstack(fill_value=0).to_string())
    p("")
    p("    `excluido` son almacenes, vinotecas, delivery y similares: el proyecto los deja afuera")
    p("    por definición. No son locales que nos falten.")
    p("")

    nucleo = cerca[cerca.anillo == "nucleo"]
    pct_global = nucleo.ya_estaba.eq(False).mean() * 100 if len(nucleo) else 0.0
    por_barrio = nucleo.groupby("barrio").agg(
        places_nucleo=("place_id", "size"), ya_estaba=("ya_estaba", "sum"))
    por_barrio["nuevos"] = por_barrio.places_nucleo - por_barrio.ya_estaba
    por_barrio["pct_nuevos"] = (por_barrio.nuevos / por_barrio.places_nucleo * 100).round(1)
    por_barrio["base_nucleo"] = por_barrio.index.map(base.groupby("barrio").local_id.count())
    por_barrio["nuevos_sobre_base"] = (
        por_barrio.nuevos / por_barrio.base_nucleo * 100).round(1)

    p("  EL UNIVERSO COMPARABLE · sólo puntos del anillo núcleo, que es lo que la base mapea")
    p(por_barrio.to_string())
    p("")
    p(f"  FRACCIÓN NUEVA sobre el universo comparable: {pct_global:.1f} % "
      f"({int(por_barrio.nuevos.sum())} de {int(por_barrio.places_nucleo.sum())} puntos del núcleo)")
    p(f"  Y en términos de la base: {int(por_barrio.nuevos.sum())} locales sobre los "
      f"{int(por_barrio.base_nucleo.sum())} que la base tiene en esos cinco barrios "
      f"({por_barrio.nuevos.sum() / por_barrio.base_nucleo.sum() * 100:.1f} %).")
    p("")
    p("  LECTURA, contra las dos escritas antes de correr:")
    if pct_global < 40:
        p(f"    La fracción nueva es BAJA ({pct_global:.1f} %). En los barrios donde la base está")
        p("    más flaca —elegidos por criterio declarado, no a ojo— Places encuentra poco que no")
        p("    tuviéramos. **La cobertura de la base queda acotada por arriba con un número")
        p("    propio**, que es justo lo que no teníamos y lo que el denominador externo iba a dar.")
    else:
        p(f"    La fracción nueva es ALTA ({pct_global:.1f} %). Hay faltante en los barrios más")
        p("    flacos y queda localizado y con tamaño. No es un veredicto sobre toda la Ciudad:")
        p("    estos cinco barrios se eligieron por ser los peores, así que esto es una COTA")
        p("    SUPERIOR del faltante, no un promedio.")
    p("")
    p("  Y lo que este número NO dice: nada sobre vigencia. Places descubre, no confirma.")
    p("")

    (INTERNO / "SONDA_PLACES.txt").write_text("\n".join(lineas), encoding="utf-8")
    cerca.drop(columns=["geometry"]).to_csv(INTERNO / "places_puntos.csv", index=False,
                                            encoding="utf-8")
    # DOS resúmenes, y los nombres tienen que decir cuál es cuál. El que sale de `resumen` es el
    # de TODOS los puntos, sin filtrar por rubro: es el 49,2 %→52,2 % que mezcla universos y que
    # NO se puede reportar como faltante. El del núcleo es el comparable. Un archivo llamado
    # `places_resumen_por_barrio.csv` a secas invita a agarrar el equivocado, así que se renombra.
    resumen.to_csv(INTERNO / "places_resumen_SIN_FILTRAR_no_usar_como_faltante.csv",
                   encoding="utf-8")
    por_barrio.to_csv(INTERNO / "places_resumen_nucleo_comparable.csv", encoding="utf-8")
    (INTERNO / "corrida.json").write_text(json.dumps({
        "fecha": inicio.isoformat(), "autorizado": PRESUPUESTO_AUTORIZADO,
        "requests_gastados": gastados, "celdas_planificadas": len(celdas),
        "celdas_consultadas": int(crudos.celda_id.nunique()),
        "puntos_unicos": int(len(unicos)), "pct_nuevos": round(float(pct_global), 1),
        "incidencias": incidencias,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"escrito en {INTERNO.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
