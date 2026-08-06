"""Por qué la base no llega al mínimo declarado en R18, R19 y R21. CERO requests.

QUÉ PREGUNTA CONTESTA
---------------------
El cotejo de las 22 zonas dejó tres zonas donde la base queda POR DEBAJO de una cifra publicada
como **cota inferior**: R18 (0,48), R21 (0,82) y R19 (0,89). Una cota inferior que la base no
alcanza tiene sólo dos explicaciones posibles, y son muy distintas entre sí:

  · **faltante de cobertura** — en ese territorio la base efectivamente tiene menos locales que
    los que hay, y ahí Places compraría algo;
  · **faltante de perímetro** — los dos números no cuentan sobre la misma superficie ni sobre el
    mismo universo de rubros, y la diferencia es un artefacto de comparación.

Antes de gastar un request hay que separarlas, porque son decisiones opuestas: la primera manda
a consultar y la segunda manda a corregir la comparación. **Todo lo que hace falta ya está en
disco.**

LOS TRES EJES QUE SE DESALINEAN, Y POR QUÉ
-------------------------------------------
1. **Perímetro con precedencia.** El cotejo recorta la base con la regla de precedencia de
   solape —la superficie compartida queda para el `referencia_id` menor—, que existe para que
   ninguna dirección se cuente dos veces en el mismo cuadro. Las cifras publicadas **no usan esa
   regla**: `ANALISIS_R12_SUBUNIDADES.csv` etiqueta la subunidad C-S07 como
   `ETIQUETA_COMPARTIDA_CON_R18`, o sea que los mismos 216 establecimientos cuentan en R12 y en
   R18 a la vez. Aplicarle a la base una regla que la cifra publicada no aplicó le saca a R18 el
   64 % de su superficie y después le pide el conteo entero.

2. **Perímetro de consulta contra envolvente editorial.** La cifra publicada se contó sobre la
   geometría con que se consultó —un disco de 400 m en R18, dos ventanas de buffer en R19, una
   red de buffers de 300 m en R21—, y la base se cuenta sobre la envolvente editorial del Atlas,
   que es otro polígono dibujado después y con otro criterio. No tienen por qué medir lo mismo.

3. **Universo de rubros.** Las corridas publicadas consultaron cinco categorías de Places:
   `restaurant`, `cafe`, `bar`, `bakery` y `meal_takeaway`. `bakery` cae en el anillo **ampliado**
   de este proyecto, no en el núcleo. Comparar `base_nucleo` contra esas cifras le descuenta a la
   base todas las panaderías y confiterías y no se lo descuenta a la cifra publicada.

CÓMO SE SEPARAN
---------------
Se cuenta la base sobre los tres perímetros y los dos universos, y se mira la **densidad por
hectárea**, que es lo único comparable cuando las superficies difieren. Si con el perímetro y el
universo de la corrida publicada la base alcanza la cota, el faltante era de comparación. Si no
la alcanza, el faltante es de cobertura y está cuantificado.

LO QUE ESTE SCRIPT NO HACE
--------------------------
No toca ninguna cifra publicada, no toca la base, no reescribe el cotejo y no consulta ninguna
API. Sólo lee y cuenta.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/diagnosticar_faltante_zonas.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_capa_homogenea import ENVOLVENTES, PRECEDENCIA_ENVOLVENTES  # noqa: E402
from places_control_zonas import CRS_METRICO  # noqa: E402

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
BASE = BARRIDO / "base" / "local.csv"
GEN = BARRIDO / "generado"
CIFRAS_22 = BARRIDO / "insumos" / "cifras_publicadas_atlas_22.csv"

PREFLIGHT = ROOT / "outputs" / "polos_gastro" / "INFORMEFINAL" / "codex"
AREAS_A = PREFLIGHT / "preflight_tecnico_grupo_a_v1" / "areas" / "AREAS_PROVISIONALES_GRUPO_A.geojson"
AREAS_B = (PREFLIGHT / "preflight_tecnico_grupo_b_reparado_v1" / "areas"
           / "AREAS_PROVISIONALES_GRUPO_B.geojson")
AREAS_C = PREFLIGHT / "preflight_tecnico_grupo_c_v1" / "areas" / "AREAS_PROVISIONALES_GRUPO_C.geojson"

# Las zonas cuya cifra publicada es una cota inferior producida por una corrida de Places con
# geometría documentada. Son las únicas que este diagnóstico puede tratar: de las demás no hay
# perímetro de consulta contra el cual comparar.
ZONAS = ["R12", "R13", "R18", "R19", "R20", "R21", "R22"]

# Las categorías que consultaron las corridas publicadas (contrato congelado del Grupo B y plan
# del Grupo A). `bakery` es la que cruza el borde entre nuestros dos anillos.
CATEGORIAS_PUBLICADAS = ["restaurant", "cafe", "bar", "bakery", "meal_takeaway"]

# Del anillo ampliado, lo que `bakery` de Places alcanza a cubrir. `Catering` NO: no es un tipo
# de Places y no se consultó, así que un local que sólo es catering no podía aparecer en la cifra
# publicada y no debe sumarse a la base para compararla.
AMPLIADO_COMPARABLE = ("panaderia", "pasteleria", "bakery", "confiteria", "cupcake", "dessert",
                       "chocolat", "donut", "pancake", "pie_shop", "postres")


def _coma(valor: float, decimales: int = 2) -> str:
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


# --------------------------------------------------------------------------- perímetros

def envolventes_crudas() -> dict[str, object]:
    """Las envolventes editoriales tal cual, SIN la regla de precedencia de solape."""
    capa = gpd.read_file(ENVOLVENTES)[["referencia_id", "geometry"]].to_crs(CRS_METRICO)
    return dict(zip(capa.referencia_id, capa.geometry))


def envolventes_con_precedencia() -> dict[str, object]:
    """Las mismas envolventes con la superficie compartida cedida al `referencia_id` menor.

    Es exactamente lo que usan `build_capa_homogenea.py`, `places_control_zonas.py` y el cotejo.
    Se reimplementa acá en vez de importarse porque `places_control_zonas.perimetros()` hace lo
    mismo: importarla ataría este diagnóstico a un módulo que además carga la configuración de la
    API, y este script no tiene por qué poder tocar la red ni siquiera por accidente.
    """
    capa = gpd.read_file(ENVOLVENTES)[["referencia_id", "geometry"]].to_crs(CRS_METRICO)
    capa = capa.sort_values(PRECEDENCIA_ENVOLVENTES).reset_index(drop=True)
    resultado = {}
    for posicion, zona in capa.iterrows():
        perimetro = zona.geometry
        for previa in capa.iloc[:posicion].itertuples():
            if perimetro.intersects(previa.geometry):
                perimetro = perimetro.difference(previa.geometry)
        resultado[zona.referencia_id] = perimetro
    return resultado


def perimetros_de_consulta() -> dict[str, object]:
    """La geometría sobre la que se contó cada cifra publicada, unida por zona.

    Se toman sólo las áreas de PRODUCTO. Los controles quedan afuera por definición: no
    produjeron universo. R18 aparece en el paquete del Grupo A con `referencia_id` compuesto
    (`R18;R12`) porque su disco es compartido, y se le asigna a R18 —que es la zona cuya cifra
    publicada ES ese disco entero—.
    """
    formas: dict[str, list] = {}

    grupo_a = gpd.read_file(AREAS_A).to_crs(CRS_METRICO)
    grupo_a = grupo_a[grupo_a.geometry.notna() & ~grupo_a.geometry.is_empty]
    for fila in grupo_a.itertuples():
        estado = str(fila.estado)
        if not estado.startswith("PROVISIONAL_NO_OFICIAL"):
            continue  # controles y subunidades sin Places no produjeron conteo
        # `R18;C-S07` es una sola geometría con dos productos. La cifra publicada de R18 es el
        # disco entero, así que el disco va a R18. R12 también lo contiene —su 797 está
        # deduplicado sobre las cinco subunidades, C-S07 incluida— y por eso va a los dos.
        for rid in str(fila.referencia_id).split(";"):
            formas.setdefault(rid.strip(), []).append(fila.geometry)

    grupo_b = gpd.read_file(AREAS_B).to_crs(CRS_METRICO)
    for fila in grupo_b.itertuples():
        if "PRODUCTO" not in str(fila.funcion):
            continue
        formas.setdefault(str(fila.referencia_id).strip(), []).append(fila.geometry)

    grupo_c = gpd.read_file(AREAS_C).to_crs(CRS_METRICO)
    for fila in grupo_c.itertuples():
        formas.setdefault(str(fila.referencia_id).strip(), []).append(fila.geometry)

    from shapely.ops import unary_union
    return {rid: unary_union(piezas) for rid, piezas in formas.items()}


# --------------------------------------------------------------------------- universos

def puntos_de_la_base(local: pd.DataFrame) -> gpd.GeoDataFrame:
    """La base como puntos en CRS métrico, con la marca del universo comparable.

    `comparable` es el universo que la corrida publicada pudo ver: el anillo núcleo más lo que
    `bakery` alcanza del ampliado. No es todo el ampliado.
    """
    con_punto = local[local.lon.notna() & local.lat.notna()].copy()
    categoria = con_punto.categoria.fillna("").astype(str).str.lower()
    panificacion = categoria.str.contains("|".join(AMPLIADO_COMPARABLE), regex=True)
    con_punto["comparable"] = (con_punto.anillo == "nucleo") | (
        (con_punto.anillo == "ampliado") & panificacion)
    return gpd.GeoDataFrame(
        con_punto,
        geometry=gpd.points_from_xy(con_punto.lon, con_punto.lat),
        crs="EPSG:4326").to_crs(CRS_METRICO)


def contar(puntos: gpd.GeoDataFrame, forma) -> dict:
    if forma is None or forma.is_empty:
        return {"ha": None, "nucleo": None, "comparable": None}
    dentro = puntos[puntos.within(forma)]
    return {
        "ha": round(forma.area / 1e4, 2),
        "nucleo": int((dentro.anillo == "nucleo").sum()),
        "comparable": int(dentro.comparable.sum()),
    }


# --------------------------------------------------------------------------- informe

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    for ruta in (BASE, CIFRAS_22, AREAS_A, AREAS_B, AREAS_C):
        if not ruta.exists():
            raise SystemExit(f"ABORTADO: falta {ruta.relative_to(ROOT)}")

    local = pd.read_csv(BASE, low_memory=False)
    cifras = pd.read_csv(CIFRAS_22).set_index("rid")
    puntos = puntos_de_la_base(local)

    crudas = envolventes_crudas()
    con_precedencia = envolventes_con_precedencia()
    consulta = perimetros_de_consulta()

    filas = []
    for rid in ZONAS:
        publicada = cifras.relevado.get(rid)
        fila = {"rid": rid, "zona": cifras.zona_publicada.get(rid),
                "publicada": int(publicada) if publicada == publicada else None}
        for etiqueta, formas in (("precedencia", con_precedencia),
                                 ("envolvente", crudas),
                                 ("consulta", consulta)):
            medido = contar(puntos, formas.get(rid))
            fila[f"ha_{etiqueta}"] = medido["ha"]
            fila[f"nucleo_{etiqueta}"] = medido["nucleo"]
            fila[f"comparable_{etiqueta}"] = medido["comparable"]
        filas.append(fila)
    tabla = pd.DataFrame(filas).set_index("rid")

    # La razón que importa: el universo comparable sobre el perímetro de consulta, que es la
    # única combinación en la que los dos números miden lo mismo.
    tabla["razon_cotejo"] = (tabla.nucleo_precedencia / tabla.publicada).round(2)
    tabla["razon_corregida"] = (tabla.comparable_consulta / tabla.publicada).round(2)
    tabla["dens_consulta"] = (tabla.comparable_consulta / tabla.ha_consulta).round(2)
    tabla["dens_publicada"] = (tabla.publicada / tabla.ha_consulta).round(2)

    salida = io.StringIO()

    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    linea("=" * 98)
    linea("PERÍMETRO O COBERTURA · POR QUÉ LA BASE NO LLEGA AL MÍNIMO DECLARADO · 0 REQUESTS")
    linea("=" * 98)
    linea(f"fecha {dt.date.today().isoformat()} · base de {len(local):,} locales · "
          "ninguna cifra publicada se toca".replace(",", "."))
    linea()

    linea("§1 · LAS TRES SUPERFICIES, QUE NO SON LA MISMA")
    linea("-" * 98)
    linea("  Hectáreas sobre las que cuenta cada perímetro. `precedencia` es el que usó el cotejo;")
    linea("  `consulta` es el que usó la corrida que produjo la cifra publicada.")
    linea()
    linea(f"  {'ref':<5}{'zona':<30}{'precedencia':>12}{'envolvente':>12}{'consulta':>10}"
          f"{'cons÷prec':>11}")
    for fila in tabla.itertuples():
        factor = (fila.ha_consulta / fila.ha_precedencia) if fila.ha_precedencia else None
        linea(f"  {fila.Index:<5}{str(fila.zona)[:29]:<30}{_coma(fila.ha_precedencia, 1):>12}"
              f"{_coma(fila.ha_envolvente, 1):>12}{_coma(fila.ha_consulta, 1):>10}"
              f"{(_coma(factor) + '×' if factor else '—'):>11}")
    linea()

    linea("§2 · LA BASE SOBRE CADA PERÍMETRO Y CADA UNIVERSO")
    linea("-" * 98)
    linea("  `núcleo` es lo que contó el cotejo. `comparable` suma la panificación que la consulta")
    linea(f"  publicada sí pedía (categorías: {', '.join(CATEGORIAS_PUBLICADAS)}).")
    linea()
    linea(f"  {'ref':<5}{'publicada':>10}{'núcleo/prec':>13}{'compar/prec':>13}"
          f"{'núcleo/cons':>13}{'compar/cons':>13}")
    for fila in tabla.itertuples():
        linea(f"  {fila.Index:<5}{fila.publicada:>10}{fila.nucleo_precedencia:>13}"
              f"{fila.comparable_precedencia:>13}{fila.nucleo_consulta:>13}"
              f"{fila.comparable_consulta:>13}")
    linea()

    linea("§3 · LA RAZÓN, ANTES Y DESPUÉS DE ALINEAR PERÍMETRO Y UNIVERSO")
    linea("-" * 98)
    linea(f"  {'ref':<5}{'zona':<30}{'cotejo':>9}{'corregida':>11}{'alcanza':>9}   qué era")
    for fila in tabla.itertuples():
        alcanza = "sí" if fila.razon_corregida >= 1 else "NO"
        if fila.razon_cotejo >= 1 and fila.razon_corregida >= 1:
            lectura = "nunca estuvo por debajo"
        elif fila.razon_corregida >= 1:
            lectura = "era PERÍMETRO/UNIVERSO"
        else:
            faltan = int(fila.publicada - fila.comparable_consulta)
            lectura = f"queda COBERTURA: faltan {faltan}"
        linea(f"  {fila.Index:<5}{str(fila.zona)[:29]:<30}{_coma(fila.razon_cotejo):>9}"
              f"{_coma(fila.razon_corregida):>11}{alcanza:>9}   {lectura}")
    linea()

    linea("§4 · DE DÓNDE SALE LA DIFERENCIA, DESCOMPUESTA")
    linea("-" * 98)
    linea("  Cuánto aporta cada eje al pasar del conteo del cotejo al conteo comparable. No son")
    linea("  intercambiables: si domina el perímetro, la zona nunca estuvo mal medida; si domina el")
    linea("  universo, lo que faltaba era contar las panaderías que la consulta publicada sí pedía.")
    linea()
    linea(f"  {'ref':<5}{'cotejo':>8}{'+perímetro':>12}{'+universo':>11}{'=comparable':>13}"
          f"   eje dominante")
    for fila in tabla.itertuples():
        por_perimetro = fila.nucleo_consulta - fila.nucleo_precedencia
        por_universo = fila.comparable_consulta - fila.nucleo_consulta
        if por_perimetro == por_universo == 0:
            dominante = "ninguno: los perímetros coinciden"
        elif abs(por_perimetro) >= abs(por_universo):
            cuanto = abs(por_perimetro) / max(abs(por_perimetro) + abs(por_universo), 1)
            dominante = f"perímetro ({cuanto:.0%} de la diferencia)"
        else:
            cuanto = abs(por_universo) / max(abs(por_perimetro) + abs(por_universo), 1)
            dominante = f"universo de rubros ({cuanto:.0%})"
        linea(f"  {fila.Index:<5}{fila.nucleo_precedencia:>8}{por_perimetro:>+12}"
              f"{por_universo:>+11}{fila.comparable_consulta:>13}   {dominante}")
    linea()

    linea("§5 · DENSIDAD POR HECTÁREA SOBRE EL PERÍMETRO DE CONSULTA")
    linea("-" * 98)
    linea("  Es la comparación que sobrevive a que las superficies difieran.")
    linea()
    linea(f"  {'ref':<5}{'ha':>9}{'base/ha':>10}{'publicada/ha':>14}")
    for fila in tabla.itertuples():
        linea(f"  {fila.Index:<5}{_coma(fila.ha_consulta, 1):>9}{_coma(fila.dens_consulta):>10}"
              f"{_coma(fila.dens_publicada):>14}")
    linea()

    linea("§6 · QUÉ DECIDE ESTO SOBRE CORRER PLACES")
    linea("-" * 98)
    resueltas = tabla[(tabla.razon_cotejo < 1) & (tabla.razon_corregida >= 1)]
    persisten = tabla[(tabla.razon_cotejo < 1) & (tabla.razon_corregida < 1)]
    if len(resueltas):
        for texto in _envolver(
            f"{len(resueltas)} de las zonas que aparecían por debajo del mínimo "
            f"({', '.join(resueltas.index)}) lo alcanzan en cuanto se cuenta sobre el mismo "
            "perímetro y el mismo universo de rubros que la corrida publicada. **No eran faltante "
            "de cobertura: eran faltante de comparación.** Consultar Places ahí compraría muy "
            "poco, y el diagnóstico que las señalaba como candidatas queda sin efecto."):
            linea(f"  {texto}")
        linea()
    if len(persisten):
        for texto in _envolver(
            f"{len(persisten)} zona(s) siguen por debajo con todo alineado: "
            f"{', '.join(persisten.index)}. Ahí el faltante es real y está cuantificado en la "
            "columna «qué era» del §3. Son las únicas candidatas legítimas a una tanda de Places, "
            "y el tamaño de la tanda se dimensiona con ese faltante, no con la zona entera."):
            linea(f"  {texto}")
        linea()
    for texto in _envolver(
        "Y una advertencia que vale para todo el cotejo: la cifra publicada de estas zonas también "
        "salió de Google Places. Que la base la alcance no prueba que la base esté completa: prueba "
        "que llega adonde llegó una corrida de Places de julio. El mínimo declarado es una cota "
        "inferior de esa corrida, no del territorio."):
        linea(f"  {texto}")
    linea()
    linea("=" * 98)

    texto_final = salida.getvalue()
    print(texto_final)

    GEN.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(GEN / "diagnostico_faltante_zonas.csv", encoding="utf-8")
    (GEN / "DIAGNOSTICO_FALTANTE_ZONAS.txt").write_text(texto_final, encoding="utf-8")
    (GEN / "diagnostico_faltante_zonas_resumen.json").write_text(
        json.dumps({
            "fecha_calculo": dt.date.today().isoformat(),
            "requests_gastados": 0,
            "categorias_de_la_corrida_publicada": CATEGORIAS_PUBLICADAS,
            "zonas_resueltas_por_perimetro_o_universo": sorted(resueltas.index),
            "zonas_con_faltante_de_cobertura": sorted(persisten.index),
            "faltante_por_zona": {rid: int(tabla.publicada[rid] - tabla.comparable_consulta[rid])
                                  for rid in persisten.index},
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  publicado en {GEN.relative_to(ROOT)}: diagnostico_faltante_zonas.csv, "
          "DIAGNOSTICO_FALTANTE_ZONAS.txt, diagnostico_faltante_zonas_resumen.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
