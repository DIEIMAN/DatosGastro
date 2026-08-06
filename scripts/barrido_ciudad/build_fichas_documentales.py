"""Fichas documentales de los barrios del oeste y del sur.

Producto nuevo, separado de la edición técnica V2.1 del Atlas, que queda sellada e intacta.

Son fichas **documentales**, no fichas de zona. La diferencia no es de formato: estos barrios no
tienen relevamiento propio, así que **no tienen factor de captura** —no hay contra qué
calcularlo— y su base es el cruce de las fuentes documentales. Las dos condiciones que Diego
aceptó están implementadas acá:

  1. sin factor de captura, y dicho explícitamente en cada ficha;
  2. la añada del Relevamiento declarada en cada una, porque nueve de los doce barrios del oeste
     se relevaron en 2022 y eso es dato de hace tres años.

Insumos (solo lectura): la capa homogénea de habilitaciones, la capa del Relevamiento por barrio,
el detector de lotes de permisos y el CSV del Relevamiento para la composición por rubro. Correr
antes, en este orden: `build_capa_homogenea.py`, `perfilar_usos_suelo.py`,
`detectar_lotes_permisos.py`.

Uso:
  python scripts/barrido_ciudad/build_fichas_documentales.py
"""
from __future__ import annotations

import io
import sys
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from perfilar_usos_suelo import NUCLEO, cargar  # noqa: E402

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT_DIR = BARRIDO / "generado"
CAPA_HAB = BARRIDO / "capa_homogenea_48_barrios.csv"
CAPA_RUS = ROOT / "outputs" / "fuentes_externas" / "usos_suelo" / "rus_gastro_48_barrios.csv"
LOTES = OUT_DIR / "lotes_permisos_detectados.csv"

# Los doce del oeste, tal como se propusieron y se aceptaron. Ninguno recibe más del 5 % de
# superficie de las 22 envolventes del Atlas.
OESTE = ["Flores", "Liniers", "Villa Del Parque", "Mataderos", "Floresta", "Monte Castro",
         "Villa Luro", "Villa Santa Rita", "Parque Avellaneda", "Velez Sarsfield", "Villa Real",
         "Versalles"]
SUR = ["Barracas", "La Boca", "Parque Patricios", "Parque Chacabuco", "Nueva Pompeya",
       "Villa Lugano", "Villa Riachuelo", "Villa Soldati"]


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper().strip()


def composicion_por_rubro(rus: pd.DataFrame) -> pd.DataFrame:
    """Parcelas activas del anillo núcleo por barrio y por rubro nuestro."""
    equivalencias = {valor: anillo for anillo, valores in NUCLEO.items() for valor in valores}
    activo = rus[(rus.ESTADO == "ACTIVO") & rus.TIPO2.isin(equivalencias)].copy()
    activo["anillo"] = activo.TIPO2.map(equivalencias)
    activo["barrio"] = activo.BARRIO.map(plegar)
    return activo.pivot_table(index="barrio", columns="anillo", values="SMP",
                              aggfunc="nunique", fill_value=0)


def armar_fichas() -> tuple[pd.DataFrame, pd.DataFrame]:
    hab = pd.read_csv(CAPA_HAB, index_col=0, encoding="utf-8")
    hab.index = [plegar(i) for i in hab.index]
    rus_barrio = pd.read_csv(CAPA_RUS, index_col=0, encoding="utf-8")
    rus_barrio.index = [plegar(i) for i in rus_barrio.index]

    lotes = pd.read_csv(LOTES, encoding="utf-8") if LOTES.exists() else pd.DataFrame()
    if len(lotes):
        lotes["barrio"] = lotes.barrio.map(plegar)
        por_barrio = lotes.groupby("barrio").agg(
            lotes_detectados=("lote", "nunique"),
            direcciones_en_lotes=("direccion", "nunique"),
            habilitaciones_en_lotes=("habilitaciones", "sum"))
    else:
        por_barrio = pd.DataFrame()

    ficha = hab.join(rus_barrio[["rus_nucleo", "rus_ampliado", "rus_inactivo",
                                 "anio_relevamiento"]]).join(por_barrio)
    for columna in ("lotes_detectados", "direcciones_en_lotes", "habilitaciones_en_lotes"):
        if columna in ficha:
            ficha[columna] = ficha[columna].fillna(0).astype(int)
        else:
            ficha[columna] = 0

    ficha["grupo"] = ["oeste" if i in [plegar(b) for b in OESTE]
                      else "sur" if i in [plegar(b) for b in SUR] else "resto"
                      for i in ficha.index]
    seleccion = ficha[ficha.grupo != "resto"].copy()
    return seleccion, composicion_por_rubro(cargar())


def redactar(fichas: pd.DataFrame, rubros: pd.DataFrame, p) -> None:
    p("# Fichas documentales · barrios del oeste y del sur")
    p("")
    p("**Fecha:** 5 de agosto de 2026 · **Para:** Dirección General de Desarrollo Gastronómico")
    p("")
    p("Veinte barrios que las veintidós zonas del Atlas no cubren: doce del oeste y ocho del sur.")
    p("Entran por base documental, sin relevamiento de calle.")
    p("")
    p("**Estas fichas no tienen factor de captura.** El factor de captura compara un relevamiento")
    p("contra una base documental, y en estos barrios no hubo relevamiento propio. Lo que hay es")
    p("el cruce de dos fuentes documentales, cada una con su propia unidad y su propia fecha.")
    p("")
    p("Cada ficha declara el año en que el Relevamiento de Usos del Suelo pasó por ese barrio. No")
    p("es un detalle de método: el operativo es rotativo y **nueve de los doce barrios del oeste**")
    p("**se relevaron en 2022**, así que su dato tiene tres años.")
    p("")
    p("> **La columna `habilitaciones` del padrón no es un indicador de volumen de oferta.** Cuenta")
    p("> trámites, no locales, y en 45 conjuntos de direcciones —el 22,6 % del padrón")
    p("> georreferenciado— un mismo permiso figura repetido contra cada puerta del frente de")
    p("> manzana del inmueble. Está probado contra el catastro: las partidas involucradas resuelven")
    p("> todas a una única parcela. Los barrios afectados van marcados con † en las tablas de")
    p("> abajo. Las columnas de **direcciones** no están afectadas: la regla 3 del método ya las")
    p("> deja fuera del conteo.")
    p("")
    p("---")
    p("")

    for grupo, titulo in (("oeste", "Oeste"), ("sur", "Sur")):
        seleccion = fichas[fichas.grupo == grupo].sort_values("rus_nucleo", ascending=False)
        p(f"## {titulo} · {len(seleccion)} barrios")
        p("")
        p("| barrio | parcelas núcleo | parcelas ampliado | direcciones núcleo | direcciones ampliado | oferta F01 | trámites del padrón | año del relevamiento |")
        p("|---|---:|---:|---:|---:|---:|---:|---:|")
        for fila in seleccion.itertuples():
            # La daga viaja pegada al nombre del barrio: quien lea sólo la tabla igual la ve.
            marca = " †" if fila.lotes_detectados else ""
            tramites = f"{int(fila.habilitaciones):,}".replace(",", ".")
            p(f"| {fila.Index.title()}{marca} | {int(fila.rus_nucleo)} | {int(fila.rus_ampliado)} | "
              f"{int(fila.dir_nucleo)} | {int(fila.dir_ampliado)} | {int(fila.f01_locales)} | "
              f"{tramites} | {int(fila.anio_relevamiento)} |")
        p(f"| **subtotal** | **{int(seleccion.rus_nucleo.sum())}** | "
          f"**{int(seleccion.rus_ampliado.sum())}** | **{int(seleccion.dir_nucleo.sum())}** | "
          f"**{int(seleccion.dir_ampliado.sum())}** | **{int(seleccion.f01_locales.sum())}** | "
          f"**{int(seleccion.habilitaciones.sum()):,}**".replace(",", ".") + " | |")
        p("")
        afectados = seleccion[seleccion.lotes_detectados > 0]
        if len(afectados):
            nombres = ", ".join(n.title() for n in afectados.index)
            p(f"† **Trámites inflados por lotes de permisos replicados:** {nombres}. En estos")
            p("barrios la columna «trámites del padrón» **no se lee como volumen de oferta**: un")
            p("mismo permiso figura contra cada puerta del frente de manzana del inmueble. Las")
            p("columnas de direcciones y de parcelas no están afectadas.")
            p("")

    p("---")
    p("")
    p("## Ficha por barrio")
    p("")
    anillos_orden = list(NUCLEO)
    for grupo, titulo in (("oeste", "Oeste"), ("sur", "Sur")):
        p(f"### {titulo}")
        p("")
        for fila in fichas[fichas.grupo == grupo].sort_values("rus_nucleo", ascending=False).itertuples():
            nombre = fila.Index.title()
            p(f"#### {nombre}")
            p("")
            p(f"- **Parcelas con uso gastronómico relevado, anillo núcleo:** {int(fila.rus_nucleo)} "
              f"(ampliado {int(fila.rus_ampliado)}), relevamiento de {int(fila.anio_relevamiento)}.")
            p(f"- **Direcciones con habilitación gastronómica 2015-2025, anillo núcleo:** "
              f"{int(fila.dir_nucleo)} (ampliado {int(fila.dir_ampliado)}).")
            p(f"- **Oferta registrada en F01:** {int(fila.f01_locales)} establecimientos.")
            if fila.rus_inactivo:
                p(f"- **Parcelas gastronómicas inactivas al momento del relevamiento:** "
                  f"{int(fila.rus_inactivo)}.")
            if int(fila.dir_outlier):
                p(f"- **Direcciones anómalas excluidas del conteo:** {int(fila.dir_outlier)}.")
            if fila.lotes_detectados:
                registros = f"{int(fila.habilitaciones_en_lotes):,}".replace(",", ".")
                proporcion = 100 * fila.habilitaciones_en_lotes / fila.habilitaciones
                p(f"- **† Atención:** el detector encontró {int(fila.lotes_detectados)} lote(s) de "
                  f"permisos replicados en este barrio, sobre {int(fila.direcciones_en_lotes)} "
                  f"direcciones y {registros} trámites — el {proporcion:.0f} % de los trámites del "
                  "barrio. Está probado contra el catastro: esas direcciones cuelgan de una única "
                  "parcela, así que **el volumen de trámite de este barrio no se lee como volumen "
                  "de locales**.")
            if fila.Index in rubros.index:
                detalle = rubros.loc[fila.Index].reindex(anillos_orden).fillna(0).astype(int)
                detalle = detalle[detalle > 0].sort_values(ascending=False)
                p(f"- **Composición del núcleo relevado:** "
                  f"{', '.join(f'{k} {v}' for k, v in detalle.items())}.")
            p(f"- **Sin factor de captura:** no hubo relevamiento propio en este barrio.")
            p("")

    p("---")
    p("")
    p("## Cómo leer estos números")
    p("")
    p("- **Parcelas con uso gastronómico relevado** es la unidad del Relevamiento de Usos del")
    p("  Suelo: una parcela con uso gastronómico al momento del censo. No es «locales abiertos")
    p("  hoy», y el año de cada barrio está declarado en su ficha.")
    p("- **Direcciones con habilitación** es la unidad del padrón: direcciones que alguna vez")
    p("  tuvieron habilitación gastronómica en la década. El padrón no registra bajas.")
    p("- **Trámites del padrón** (la columna `habilitaciones` de los CSV) cuenta expedientes, no")
    p("  locales, y **no es un indicador de volumen de oferta**. Un mismo permiso puede figurar")
    p("  repetido contra cada puerta del frente de manzana de un inmueble: pasa en el 22,6 % del")
    p("  padrón georreferenciado. Los barrios donde se detectó van con † arriba. Se publica")
    p("  igual porque mide otra cosa que sí importa —carga de trámite— pero se lee como eso.")
    p("- Las dos series **no se suman**: miden cosas distintas sobre el mismo territorio y se")
    p("  informan una al lado de la otra a propósito.")
    p("- Ninguna de las dos es un relevamiento de calle. Donde la Dirección relevó caminando, el")
    p("  número resultó entre dos y trece veces más alto que estas bases.")


def main() -> int:
    fichas, rubros = armar_fichas()
    buffer = io.StringIO()

    def p(*args):
        print(*args, file=buffer)

    redactar(fichas, rubros, p)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "FICHAS_DOCUMENTALES_OESTE_SUR.md").write_text(buffer.getvalue(), encoding="utf-8")
    fichas.to_csv(OUT_DIR / "fichas_documentales_oeste_sur.csv", encoding="utf-8")

    print(f"{len(fichas)} fichas: {int((fichas.grupo == 'oeste').sum())} del oeste, "
          f"{int((fichas.grupo == 'sur').sum())} del sur")
    print(f"parcelas núcleo: oeste {int(fichas[fichas.grupo == 'oeste'].rus_nucleo.sum())}, "
          f"sur {int(fichas[fichas.grupo == 'sur'].rus_nucleo.sum())}")
    print(f"escrito en {OUT_DIR.relative_to(ROOT)}: FICHAS_DOCUMENTALES_OESTE_SUR.md, "
          "fichas_documentales_oeste_sur.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
