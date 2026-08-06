"""Relevamiento de Usos del Suelo 2022-2024: los dos controles previos y la capa por barrio.

Fuente candidata del barrido de la Ciudad (data.buenosaires.gob.ar, GCBA, parcela por parcela).
La documentación oficial NO publica el diccionario de códigos, así que el vocabulario de `TIPO2`
se establece por conteo sobre el archivo, no por supuesto.

Controles que ejecuta:
  1. Vocabulario: valores distintos de `TIPO2` con frecuencia, y cuáles son gastronómicos.
  2. Cobertura: qué barrios cubre y con qué año de relevamiento cada uno.

Y produce la capa por barrio comparable contra `capa_homogenea_48_barrios.csv`.

Dos advertencias del archivo que este script resuelve:
  - Las cadenas vienen con doble codificación (`CAF├ë` por `CAFÉ`): UTF-8 leído como CP437.
  - La unidad es la **parcela** (`SMP`) y una parcela puede traer varios registros de uso, así
    que se cuenta `SMP` distinto, no filas.

Descarga previa (este script no baja nada):
  curl -L -o outputs/fuentes_externas/usos_suelo/rus_2022_2024.csv \\
    https://data.buenosaires.gob.ar/dataset/relevamiento-usos-suelo/resource/3c7e5f10-577a-44ea-b614-82cc05f842aa/download

Uso:
  python scripts/barrido_ciudad/perfilar_usos_suelo.py
"""
from __future__ import annotations

import io
import sys
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FUENTE = ROOT / "outputs" / "fuentes_externas" / "usos_suelo" / "rus_2022_2024.csv"
OUT_DIR = ROOT / "outputs" / "fuentes_externas" / "usos_suelo"
CAPA_HABILITACIONES = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "capa_homogenea_48_barrios.csv"

# Equivalencia entre el vocabulario TIPO2 del Relevamiento y los dos anillos de rubro del
# método de comparabilidad. Establecida por conteo sobre el archivo (471 valores distintos).
#
# Criterio (decisión de Diego, 2026-08-05): **simetría con el mapeo de habilitaciones**. Cada
# valor de TIPO2 va al anillo donde ya cae su equivalente en `fact_habilitacion_gastronomica.csv`.
# Verificado contra el padrón:
#   despacho de bebidas, wisqueria, cerveceria -> Bar          => CERVECERIA al núcleo
#   restaurante, cantina -> Restaurante                        => SUSHI al núcleo (no tiene
#                                                                 rubro propio en el padrón)
#   confiteria (1.721 habilitaciones) -> Pasteleria            => CONFITERIA al ampliado
NUCLEO = {
    "Restaurante": ["RESTAURANTE", "SUSHI"],
    "Bar": ["BAR", "CERVECERIA"],
    "Cafe": ["CAFÉ", "CAFÉ (VTA AL PASO)"],
    "Pizzeria": ["PIZZERIA"],
    "Parrilla": ["PARRILLA"],
    "Comida al paso": ["COMIDAS PARA LLEVAR", "COMIDA RAPIDA", "EMPANADAS", "ROTISERIA", "SANDWICHERIA"],
    "Heladeria": ["HELADERIA"],
}
AMPLIADO_SUMA = {
    "Panaderia": ["PANADERIA"],
    "Pasteleria": ["CONFITERIA"],
}

# PENDIENTE (no ejecutar sin decisión de Diego): el mapeo `confiteria -> Pasteleria` del padrón
# es discutible. Una confitería porteña es un café con servicio de mesa, no una pastelería. Pero
# corregirlo de un solo lado rompe la comparación entre las dos bases: si se cambia, se cambia en
# habilitaciones y en el Relevamiento en la misma corrida y se recalcula todo. Hoy no se toca.
# Va agrupado con el renombre de `habilitaciones` a `tramites`: los dos obligan a recongelar la
# referencia de `build_capa_homogenea.py --check`, y esa referencia se rompe una sola vez. La
# lista completa está en el docstring de `comparar()`, en ese archivo.

# Valores de TIPO2 que la búsqueda por palabra clave trae pero NO son gastronomía de atención
# al público: comercio de alimentos, elaboración sin salón, equipamiento y falsos positivos.
DESCARTADOS_EXPLICITOS = [
    "BARBERIA", "ALIMENTOS PARA MASCOTAS", "VINOS (VENTA)", "BEBIDAS ALCOHOLICAS",
    "FABRICA DE PASTAS", "EQUIP. GASTRONOMICO", "VENTA DE CAFÉ (PRODUCTOS)",
    "REPARACION DE HELADERAS", "HELADERAS Y BALANZAS COMERCIALES (VTA)", "RESTAURACIONES",
    "INSTITUTO DE GASTRONOMIA", "VENTA POR MAYOR DE ALIMENTOS Y BEBIDAS", "GALERÍA BARRIAL",
]


# Marcadores de doble codificación CP437/UTF-8: aparecen cuando bytes UTF-8 se leyeron como
# CP437 (`CAF├ë` por `CAFÉ`). No es una molestia cosmética: si no se repara, CAFÉ desaparece del
# vocabulario y se pierden 1.803 parcelas sin que ninguna corrida falle.
MARCADORES_MOJIBAKE = ("├", "┬", "┼", "╬", "╤", "Ã", "Â")


class CodificacionInesperada(RuntimeError):
    """La fuente trae doble codificación que no se pudo reparar, o cambió su vocabulario."""


def descodificar(texto: object) -> object:
    """Repara el doble encoding del archivo: bytes UTF-8 que fueron leídos como CP437."""
    if not isinstance(texto, str):
        return texto
    try:
        return texto.encode("cp437").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto


def verificar_codificacion(crudo: pd.Series, reparado: pd.Series, columna: str) -> int:
    """Control, no limpieza: si queda doble codificación sin reparar, corta la corrida.

    Se ejecuta siempre. Una fuente nueva con el mismo defecto tiene que hacer fallar esto en vez
    de pasar de largo y borrar categorías en silencio.
    """
    sospechosos = {v for v in crudo.dropna().unique()
                   if any(m in str(v) for m in MARCADORES_MOJIBAKE)}
    restantes = sorted({v for v in reparado.dropna().unique()
                        if any(m in str(v) for m in MARCADORES_MOJIBAKE)})
    if restantes:
        raise CodificacionInesperada(
            f"{columna}: {len(restantes)} valores siguen con doble codificación después de "
            f"reparar: {restantes[:10]}. Revisar la codificación de origen antes de contar."
        )
    return len(sospechosos)


def verificar_vocabulario(rus: pd.DataFrame) -> None:
    """Control: todos los valores de TIPO2 que el mapeo declara tienen que existir en la fuente.

    Si el Relevamiento renombra una categoría o la deja de usar, el conteo caería en silencio.
    Acá corta.
    """
    declarados = [v for vs in NUCLEO.values() for v in vs] + [v for vs in AMPLIADO_SUMA.values() for v in vs]
    presentes = set(rus.TIPO2.dropna().unique())
    ausentes = [v for v in declarados if v not in presentes]
    if ausentes:
        raise CodificacionInesperada(
            f"TIPO2: el mapeo declara valores que la fuente no tiene: {ausentes}. "
            "O cambió el vocabulario del Relevamiento, o falló la reparación de codificación."
        )


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper().strip()


def cargar() -> pd.DataFrame:
    rus = pd.read_csv(FUENTE, low_memory=False, encoding="utf-8")
    rus = rus.rename(columns={rus.columns[-1]: "ANIO"})  # el encabezado "AÑO" llega mal codificado
    reparados = 0
    for columna in ("TIPO1", "TIPO2", "BARRIO"):
        crudo = rus[columna]
        rus[columna] = crudo.map(descodificar)
        reparados += verificar_codificacion(crudo, rus[columna], columna)
    rus.attrs["valores_recodificados"] = reparados
    verificar_vocabulario(rus)
    return rus


def anillos() -> tuple[list[str], list[str]]:
    """Los dos anillos como listas planas de valores de TIPO2."""
    nucleo = [v for valores in NUCLEO.values() for v in valores]
    ampliado = nucleo + [v for valores in AMPLIADO_SUMA.values() for v in valores]
    return nucleo, ampliado


def control_vocabulario(rus: pd.DataFrame, p) -> tuple[list[str], list[str]]:
    """Control 1: qué valores tiene TIPO2 y cuáles corresponden a gastronomía."""
    nucleo, ampliado = anillos()

    p("CONTROL 1 · vocabulario de TIPO2")
    p(f"  valores distintos: {rus.TIPO2.nunique()} | registros sin TIPO2: {int(rus.TIPO2.isna().sum()):,}")
    p(f"  registros totales: {len(rus):,} | parcelas (SMP) distintas: {rus.SMP.nunique():,}")
    p(f"  valores con doble codificación reparados y verificados: {rus.attrs['valores_recodificados']}")
    p("")
    p("  correspondencia con nuestros anillos, por simetría con el padrón (parcelas activas):")
    activo = rus[rus.ESTADO == "ACTIVO"]
    for anillo, valores in NUCLEO.items():
        detalle = ", ".join(f"{v} {int((activo.TIPO2 == v).sum())}" for v in valores)
        p(f"    núcleo · {anillo:<15} {int(activo.TIPO2.isin(valores).sum()):>5}  ({detalle})")
    for anillo, valores in AMPLIADO_SUMA.items():
        detalle = ", ".join(f"{v} {int((activo.TIPO2 == v).sum())}" for v in valores)
        p(f"    ampliado · {anillo:<13} {int(activo.TIPO2.isin(valores).sum()):>5}  ({detalle})")
    p("  sin equivalente en el Relevamiento: Catering (no ocupa local a la calle)")
    p("")
    p("  descartados aunque el nombre sugiera gastronomía:")
    for v in DESCARTADOS_EXPLICITOS:
        cuenta = int((activo.TIPO2 == v).sum())
        if cuenta:
            p(f"    {v:<40} {cuenta:>5}")
    p("")
    gastro = rus[rus.TIPO2.isin(ampliado)]
    p(f"  estado de los registros gastronómicos: {gastro.ESTADO.value_counts().to_dict()}")
    p(f"  todos caen bajo TIPO1: {sorted(gastro.TIPO1.dropna().unique())}")
    p("")
    return nucleo, ampliado


def control_cobertura(rus: pd.DataFrame, p) -> None:
    """Control 2: qué barrios cubre y si el relevamiento 2022-24 está completo."""
    p("CONTROL 2 · cobertura y completitud")
    por_barrio = rus.groupby("BARRIO").agg(registros=("OBJECTID", "size"), parcelas=("SMP", "nunique"))
    anios = rus.groupby("BARRIO").ANIO.unique()
    p(f"  barrios presentes: {len(por_barrio)} de 48 | ninguno vacío: {bool((por_barrio.parcelas > 0).all())}")
    p(f"  parcelas relevadas: {rus.SMP.nunique():,} | registros: {len(rus):,}")
    p(f"  barrios con más de un año de relevamiento: {int((anios.map(len) > 1).sum())}")
    p("")
    p("  el relevamiento es rotativo: cada barrio tiene un año, no hay foto simultánea")
    for anio, grupo in rus.groupby("ANIO"):
        barrios = sorted(grupo.BARRIO.unique())
        p(f"    {anio}: {len(barrios)} barrios | {grupo.SMP.nunique():,} parcelas")
        p(f"      {', '.join(barrios)}")
    p("")


def capa_por_barrio(rus: pd.DataFrame, nucleo: list[str], ampliado: list[str], p) -> pd.DataFrame:
    """Parcelas gastronómicas por barrio, comparadas contra la capa de habilitaciones."""
    activo = rus[rus.ESTADO == "ACTIVO"]
    tabla = pd.DataFrame({
        "rus_nucleo": activo[activo.TIPO2.isin(nucleo)].groupby("BARRIO").SMP.nunique(),
        "rus_ampliado": activo[activo.TIPO2.isin(ampliado)].groupby("BARRIO").SMP.nunique(),
        "rus_inactivo": rus[rus.TIPO2.isin(ampliado) & (rus.ESTADO == "INACTIVO")].groupby("BARRIO").SMP.nunique(),
        "anio_relevamiento": rus.groupby("BARRIO").ANIO.max(),
    })
    tabla["rus_inactivo"] = tabla.rus_inactivo.fillna(0).astype(int)

    hab = pd.read_csv(CAPA_HABILITACIONES, index_col=0, encoding="utf-8")
    hab.index = [plegar(i) for i in hab.index]
    tabla.index = [plegar(i) for i in tabla.index]
    tabla = tabla.join(hab[["dir_nucleo", "dir_ampliado", "f01_locales", "dir_outlier"]])
    tabla["rus_sobre_habilitaciones"] = (tabla.rus_nucleo / tabla.dir_nucleo).round(2)
    tabla = tabla.sort_values("rus_sobre_habilitaciones", ascending=False)

    p("CAPA POR BARRIO · Relevamiento contra habilitaciones (anillo núcleo)")
    p(f"  CABA: Relevamiento {int(tabla.rus_nucleo.sum()):,} parcelas activas | "
      f"habilitaciones {int(tabla.dir_nucleo.sum()):,} direcciones | "
      f"razón {tabla.rus_nucleo.sum() / tabla.dir_nucleo.sum():.2f}")
    p(f"  parcelas gastronómicas INACTIVAS al momento del relevamiento: {int(tabla.rus_inactivo.sum())}")
    p("")
    # Conciliación: los dos totales de direcciones núcleo que circulan no son una discrepancia.
    # El titular de CABA cuenta también las direcciones anómalas; la suma de los 48 barrios las
    # excluye por la regla 3. La diferencia son las anómalas que además son núcleo, y el número
    # comparable contra parcelas es el que las excluye, porque las anómalas no son locales.
    # `build_capa_homogenea.py` imprime las tres cifras y su conciliación exacta.
    p(f"  la base de comparación es la suma de los 48 barrios sin anómalas: "
      f"{int(tabla.dir_nucleo.sum()):,} direcciones núcleo. El titular de CABA es más alto porque")
    p("    incluye las anómalas; ver la conciliación en build_capa_homogenea.py.")
    p("")
    p("  donde el Relevamiento encuentra más que el padrón (razón más alta):")
    p(tabla.head(12)[["dir_nucleo", "rus_nucleo", "rus_ampliado", "anio_relevamiento",
                      "rus_sobre_habilitaciones"]].to_string())
    p("")
    p("  donde encuentra menos o casi lo mismo:")
    p(tabla.tail(6)[["dir_nucleo", "rus_nucleo", "rus_ampliado", "anio_relevamiento",
                     "rus_sobre_habilitaciones"]].to_string())
    p("")
    return tabla


def main() -> int:
    if not FUENTE.exists():
        print(f"falta el archivo {FUENTE.relative_to(ROOT)} — ver la URL de descarga en el docstring")
        return 1

    rus = cargar()
    buffer = io.StringIO()

    def p(*args):
        print(*args, file=buffer)

    p("Relevamiento de Usos del Suelo 2022-2024 · controles previos")
    p(f"archivo: {FUENTE.name} ({FUENTE.stat().st_size / 1e6:.1f} MB)")
    p("=" * 78)
    p("")
    nucleo, ampliado = control_vocabulario(rus, p)
    control_cobertura(rus, p)
    tabla = capa_por_barrio(rus, nucleo, ampliado, p)

    (OUT_DIR / "CONTROLES_RUS_2022_2024.txt").write_text(buffer.getvalue(), encoding="utf-8")
    tabla.to_csv(OUT_DIR / "rus_gastro_48_barrios.csv", encoding="utf-8")
    vocabulario = rus.TIPO2.value_counts(dropna=False).rename("registros")
    vocabulario.to_csv(OUT_DIR / "rus_vocabulario_tipo2.csv", encoding="utf-8")

    print(buffer.getvalue())
    print(f"escrito en {OUT_DIR.relative_to(ROOT)}: CONTROLES_RUS_2022_2024.txt, "
          "rus_gastro_48_barrios.csv, rus_vocabulario_tipo2.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
