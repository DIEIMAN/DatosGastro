"""Las 22 zonas del Atlas, recalculadas desde la base. CERO requests.

POR QUÉ ESTE COTEJO EXISTE
--------------------------
Las cifras de las 22 zonas viven hoy en un JSON congelado producido por otra cadena de trabajo.
Si no se pueden **reproducir desde la base**, hay dos verdades paralelas sobre la misma Ciudad, y
la que va a envejecer mal es la del Atlas: la base se actualiza y el JSON no.

**Ninguna cifra publicada se toca.** Lo que este script hace es recortar la base por las
envolventes editoriales, contar con la misma receta, y **explicar la diferencia** donde no
coincida. Una diferencia explicada no es un error; una diferencia que nadie puede explicar sí.

LA CORRECCIÓN DEL 2026-08-05, QUE CAMBIA CÓMO SE LEE TODO ESTO
---------------------------------------------------------------
La primera versión de este cotejo escribió sus bandas sobre una premisa falsa: que la cifra
publicada de la familia «relevamiento propio» era un conteo de campo, y que por eso la base tenía
que quedar por debajo. **No hay ningún conteo de campo en este proyecto.**
`METODOLOGIA_REAL_DEL_ATLAS.md` §1 y §3 lo documentan con el desglose del propio JSON canónico:

    R08 Villa Crespo · 646 = 178 capas administrativas + 467 Google Places  (72 % Places)
    R10 Caballito    · 907 = 265 capas administrativas + 642 Google Places  (71 % Places)

O sea que **toda cifra publicada es una consolidación de fuentes**, no una medición del
territorio: dos en la familia de relevamiento propio, una sola en la de directorio comercial. Y la
base es una consolidación de siete. Comparar las dos por su razón compara **el tamaño de dos
consolidaciones**, y una base con más fuentes tiene que dar más. Eso no valida nada.

Consecuencia directa: **«13 de 17 zonas en banda» no era una validación de la base** y se retira.
Donde la base supera a lo publicado, la ganancia es la esperada por sumar fuentes.

QUÉ QUEDA EN PIE COMO PRUEBA, Y QUÉ NO
---------------------------------------
Sobrevive **una sola** comparación con dirección falsable: la familia `minimo relevado`, cuya
cifra está declarada como cota inferior. Que la base no alcance una cota inferior sí es una
señal —pero sólo si se cuenta sobre **el mismo perímetro y el mismo universo de rubros** que la
corrida que produjo la cota. Alinear esos dos ejes es lo que hace
`diagnosticar_faltante_zonas.py`, y hasta que ese diagnóstico corra, un «por debajo del mínimo»
en este cuadro no es un hallazgo: es una pregunta.

Todo lo demás que este script imprime es **descriptivo**. Las bandas originales se conservan en
`LECTURA_PREVIA` y se siguen evaluando, pero como registro de una expectativa que se escribió con
una premisa equivocada, no como veredicto.

USO
---
  python scripts/barrido_ciudad/cotejar_22_zonas_base.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import sys
import unicodedata
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from places_control_zonas import CRS_METRICO, perimetros  # noqa: E402

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
BASE = BARRIDO / "base" / "local.csv"
GEN = BARRIDO / "generado"
CAPA_22 = BARRIDO / "capa_homogenea_22_zonas.csv"
# Las 22, no las 17. `zonas_con_cifra()` filtra a las que tienen número publicado, y acá hacen
# falta también las cinco «sin conteo»: son las que el cotejo no puede evaluar, y decirlo es parte
# del resultado. Una zona ausente de la tabla se leería como una zona que dio bien.
CIFRAS_22 = BARRIDO / "insumos" / "cifras_publicadas_atlas_22.csv"

# Bandas escritas ANTES de correr, por familia de método de la cifra publicada. Son razones
# base ÷ publicada.
#
# SE CONSERVAN COMO REGISTRO, NO COMO VEREDICTO. La banda de «relevamiento propio» se escribió
# creyendo que su cifra publicada era un conteo de campo, y no lo es: es 178 de capas
# administrativas más 467 de Places. Borrar la banda equivocada dejaría el cuadro más prolijo y
# haría desaparecer la prueba de que la expectativa era otra, así que se deja escrita, con el
# motivo original intacto y el motivo corregido al lado.
LECTURA_PREVIA = {
    "relevamiento propio": (0.30, 1.00,
                            "El conteo publicado se hizo cruzando fuentes sobre el territorio y la "
                            "base todavía no tiene Places. Que la base quede por debajo es lo "
                            "esperado; que la superara obligaría a revisar el conteo de campo."),
    "directorio comercial": (1.00, 4.00,
                             "La cifra publicada salió sólo de Google Places, que en la Ciudad "
                             "recupera del orden del 12 % de un conteo de campo. Overture aporta "
                             "mucho más, así que la base tiene que superarla holgadamente."),
    "minimo relevado": (1.00, 5.00,
                        "Son cotas inferiores por tope de consulta. La base tiene que superarlas; "
                        "si no lo hace, el problema está en la base."),
    "relevamiento anterior": (0.30, 3.00,
                              "Cifras de otra añada y de otro método. La banda es ancha a propósito: "
                              "no hay una expectativa fuerte y se reporta el número sin forzarlo."),
}

# Qué es realmente la cifra publicada de cada familia, y qué se puede concluir de su razón contra
# la base. `falsable` marca la única familia cuya comparación tiene dirección: una cota inferior
# que la base no alcanza es una señal. Las demás comparan dos consolidaciones de distinto tamaño,
# y su razón describe cuántas fuentes entraron en cada una, no cuál mide mejor.
QUE_ES_LA_CIFRA = {
    "relevamiento propio": {
        "falsable": False,
        "composicion": "capas administrativas + Google Places (72 % Places en R08, 71 % en R10)",
        "lectura": "Consolidación de dos fuentes contra una de siete. Que la base la supere es la "
                   "ganancia esperada por sumar fuentes, no un problema de la base ni del "
                   "conteo publicado. Que quede por debajo tampoco prueba falta de cobertura: la "
                   "base no tiene Places, que es el 70 % de esta cifra.",
    },
    "directorio comercial": {
        "falsable": False,
        "composicion": "Google Places solo (100 %)",
        "lectura": "Una fuente contra siete. La razón mide cuánto agrega el resto de las fuentes "
                   "sobre Places, y nada más.",
    },
    "minimo relevado": {
        "falsable": True,
        "composicion": "Google Places con tope de consulta, declarada «al menos»",
        "lectura": "La ÚNICA comparación con dirección: la base debería alcanzar la cota. Pero "
                   "sólo vale contada sobre el mismo perímetro y el mismo universo de rubros que "
                   "la corrida que la produjo — ver diagnosticar_faltante_zonas.py.",
    },
    "relevamiento anterior": {
        "falsable": False,
        "composicion": "cifra de otra añada, método no reconstruido",
        "lectura": "Sin expectativa. Se reporta el número y no se concluye de él.",
    },
}


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


def familia_de(metodo: str) -> str:
    """A qué familia de método pertenece la cifra publicada de una zona.

    Se compara el método COMPLETO y plegado, no su primera palabra: «relevamiento propio» y
    «relevamiento anterior» empiezan igual y son familias opuestas —una es un conteo de campo y la
    otra una cifra de otra añada—. Emparejar por la primera palabra las mezclaba y el veredicto de
    dos zonas salía contra la banda equivocada.
    """
    texto = unicodedata.normalize("NFKD", str(metodo)).encode("ascii", "ignore").decode().lower().strip()
    for clave in LECTURA_PREVIA:
        plegada = unicodedata.normalize("NFKD", clave).encode("ascii", "ignore").decode().lower()
        if texto == plegada:
            return clave
    return "sin conteo"


def recortar_por_zona(local: pd.DataFrame) -> pd.DataFrame:
    """La base recortada por cada envolvente, con la precedencia que evita el doble conteo.

    La regla de precedencia no es opcional: R02 se solapa con R12 y R18 está contenido en R12 en
    un 64 %. Sin descontar la superficie compartida, R12 y R18 cuentan dos veces el mismo
    territorio. Es la misma regla que usan la capa homogénea y el control de Places.
    """
    formas = perimetros()
    puntos = gpd.GeoDataFrame(
        local[local.lon.notna()].copy(),
        geometry=gpd.points_from_xy(local[local.lon.notna()].lon, local[local.lon.notna()].lat),
        crs="EPSG:4326").to_crs(CRS_METRICO)

    filas = {}
    for rid, forma in formas.items():
        if forma is None or forma.is_empty:
            continue
        dentro = puntos[puntos.within(forma)]
        nucleo = dentro[dentro.anillo == "nucleo"]
        filas[rid] = {
            "base_nucleo": int(len(nucleo)),
            "base_ampliado": int(len(dentro)),
            "base_aptos": int(nucleo.apto_geometria.sum()),
            "base_corroborados": int((nucleo.n_fuentes >= 2).sum()),
        }
    return pd.DataFrame(filas).T


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    if not BASE.exists():
        raise SystemExit(f"ABORTADO: falta {BASE.relative_to(ROOT)}. Corré antes "
                         "build_base_gastronomica.py.")
    local = pd.read_csv(BASE, low_memory=False)
    zonas = pd.read_csv(CIFRAS_22).set_index("rid")
    recorte = recortar_por_zona(local)

    tabla = zonas.join(recorte, how="left")
    tabla["familia"] = tabla.metodo.map(familia_de)
    tabla["razon"] = (tabla.base_nucleo / tabla.relevado).round(2)

    # La capa homogénea del padrón, para tener las tres columnas en el mismo cuadro.
    if CAPA_22.exists():
        homogenea = pd.read_csv(CAPA_22, index_col=0, encoding="utf-8")
        homogenea.index = [str(i).split(" · ")[0] for i in homogenea.index]
        tabla = tabla.join(homogenea[["dir_nucleo"]])

    salida = io.StringIO()

    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    linea("=" * 98)
    linea("LAS 22 ZONAS DEL ATLAS, RECALCULADAS DESDE LA BASE · 0 REQUESTS")
    linea("=" * 98)
    linea(f"fecha {dt.date.today().isoformat()} · base de {len(local):,} locales · "
          "ninguna cifra publicada se toca".replace(",", "."))
    linea()

    linea("§1 · EL COTEJO, ZONA POR ZONA")
    linea("-" * 98)
    linea(f"  {'ref':<5}{'zona':<30}{'publicada':>10}{'base':>8}{'razón':>8}{'padrón':>8}"
          f"{'corrob.':>9}  familia")
    for fila in tabla.itertuples():
        publicada = fila.relevado if fila.relevado == fila.relevado else None
        base_n = int(fila.base_nucleo) if fila.base_nucleo == fila.base_nucleo else 0
        razon = _coma(fila.razon) if fila.razon == fila.razon else "  —"
        padron = int(getattr(fila, "dir_nucleo", 0) or 0)
        corrob = int(fila.base_corroborados) if fila.base_corroborados == fila.base_corroborados else 0
        linea(f"  {fila.Index:<5}{str(fila.zona_publicada)[:29]:<30}"
              f"{(publicada if publicada else '—'):>10}{base_n:>8}{razon:>8}{padron:>8}"
              f"{corrob:>9}  {fila.familia}")
    sin_conteo = tabla[tabla.relevado.isna()]
    if len(sin_conteo):
        linea(f"  {len(sin_conteo)} zonas sin cifra publicada, que el cotejo no puede evaluar: "
              + ", ".join(f"{i} {str(z)[:22]}" for i, z in
                          zip(sin_conteo.index, sin_conteo.zona_publicada)))
        linea("  La base sí las cuenta, y ese número es información nueva: son zonas que el Atlas "
              "describió sin poder contar.")
    linea()

    linea("§2 · QUÉ ES CADA CIFRA PUBLICADA, Y QUÉ SE PUEDE CONCLUIR DE SU RAZÓN")
    linea("-" * 98)
    con_cifra = tabla[tabla.relevado.notna() & tabla.base_nucleo.notna()]
    veredictos = {}
    for familia, ficha in QUE_ES_LA_CIFRA.items():
        grupo = con_cifra[con_cifra.familia == familia]
        if not len(grupo):
            continue
        bajo, alto, motivo_original = LECTURA_PREVIA[familia]
        adentro = int(((grupo.razon >= bajo) & (grupo.razon <= alto)).sum())
        veredictos[familia] = {
            "zonas": int(len(grupo)),
            "comparacion_falsable": ficha["falsable"],
            "composicion_de_la_cifra": ficha["composicion"],
            "razon_min": float(grupo.razon.min()),
            "razon_mediana": float(grupo.razon.median()),
            "razon_max": float(grupo.razon.max()),
            "banda_original": [bajo, alto],
            "en_banda_original": adentro,
        }
        marca = "COMPARACIÓN FALSABLE" if ficha["falsable"] else "descriptiva, no valida nada"
        linea(f"  {familia.upper()} · {marca}")
        linea(f"    la cifra publicada es: {ficha['composicion']}")
        linea(f"    {len(grupo)} zonas · razón base ÷ publicada {_coma(grupo.razon.min())} – "
              f"{_coma(grupo.razon.max())} (mediana {_coma(grupo.razon.median())})")
        for texto in _envolver(ficha["lectura"], 92):
            linea(f"      {texto}")
        if ficha["falsable"]:
            debajo = grupo[grupo.razon < 1.00]
            if len(debajo):
                for fila in debajo.itertuples():
                    linea(f"      NO ALCANZA LA COTA · {fila.Index} "
                          f"{str(fila.zona_publicada)[:38]}: publicada {int(fila.relevado)}, "
                          f"base {int(fila.base_nucleo)}, razón {_coma(fila.razon)}")
                linea("      Antes de leer esto como falta de cobertura hay que alinear perímetro y")
                linea("      universo de rubros: diagnosticar_faltante_zonas.py.")
            else:
                linea("      Todas alcanzan la cota.")
        linea(f"    [registro] banda escrita antes de correr: {_coma(bajo)} – {_coma(alto)}, "
              f"{adentro} de {len(grupo)} adentro.")
        for texto in _envolver("Se conserva por trazabilidad y NO se lee como veredicto: "
                               + motivo_original, 88):
            linea(f"      {texto}")
        linea()

    linea("§3 · QUÉ SIGNIFICA ESTO PARA LAS DOS VERDADES PARALELAS")
    linea("-" * 98)
    falsables = [f for f, v in veredictos.items() if v["comparacion_falsable"]]
    for texto in _envolver(
        "La base **no reproduce** las cifras del Atlas y no tenía por qué. Pero la razón entre las "
        "dos tampoco decide cuál es mejor: **toda cifra publicada es una consolidación de fuentes** "
        "—una o dos— y la base es una consolidación de siete. Que la base dé más es la ganancia "
        "aritmética de sumar fuentes. Un cuadro de «cuántas zonas caen en banda» mediría el tamaño "
        "relativo de dos consolidaciones y lo presentaría como validación; por eso se retiró."):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        f"De las cuatro familias, sólo {', '.join(falsables)} admite una conclusión: su cifra está "
        "declarada como cota inferior, así que tiene dirección. Las otras tres se reportan y no se "
        "concluyen."):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        "Lo que NO se puede hacer con esto, y conviene decirlo antes de que alguien lo intente: "
        "corregir una cifra publicada con la de la base. Son dos consolidaciones con distinta fecha, "
        "distinto perímetro y distinto universo de rubros, y reemplazar una por otra sin decirlo "
        "rompería la trazabilidad del Atlas."):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        "Y falta una pieza para cerrar el cotejo del todo: **la base todavía no tiene Google "
        "Places**, que es entre el 70 % y el 100 % de cada cifra publicada. Ese cotejo se repite "
        "después de la primera tanda, si se corre."):
        linea(f"  {texto}")
    linea()
    linea("=" * 98)

    texto_final = salida.getvalue()
    print(texto_final)

    GEN.mkdir(parents=True, exist_ok=True)
    columnas = ["zona_publicada", "metodo", "familia", "relevado", "base_nucleo", "base_ampliado",
                "base_aptos", "base_corroborados", "razon"]
    if "dir_nucleo" in tabla:
        columnas.append("dir_nucleo")
    tabla[columnas].to_csv(GEN / "cotejo_22_zonas_base.csv", encoding="utf-8")
    (GEN / "COTEJO_22_ZONAS_BASE.txt").write_text(texto_final, encoding="utf-8")
    (GEN / "cotejo_22_zonas_resumen.json").write_text(
        json.dumps({"fecha_calculo": dt.date.today().isoformat(),
                    "locales_en_la_base": int(len(local)),
                    "places_en_la_base": False,
                    "conteo_en_banda_retirado": (
                        "La cifra publicada de todas las familias es una consolidación de fuentes, "
                        "no una medición del territorio (METODOLOGIA_REAL_DEL_ATLAS.md §1 y §3). "
                        "Su razón contra la base compara dos consolidaciones de distinto tamaño y "
                        "no valida la base."),
                    "por_familia": veredictos}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  publicado en {GEN.relative_to(ROOT)}: cotejo_22_zonas_base.csv, "
          "COTEJO_22_ZONAS_BASE.txt, cotejo_22_zonas_resumen.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
