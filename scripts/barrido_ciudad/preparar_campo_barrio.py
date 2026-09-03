"""Paquete de preparación para relevar un barrio a pie. NO releva nada, y no toca la red.

PARA QUÉ
--------
Núñez y La Boca son los dos barrios que la Dirección quiere al nivel de Caballito y Villa Crespo:
conteo de campo, cifra propia. La prueba de techo y la captura-recaptura ya cerraron que no hay
atajo digital —Places recupera del orden del 12 % de una cifra contada a pie, y es techo
estructural—, así que lo que corresponde es salir a la calle.

Lo que se puede preparar sin salir es todo lo demás, y es bastante:

  1. **el piso documental** que ya está en el repositorio, por fuente y por anillo;
  2. **un perímetro tentativo**, armado desde dónde se concentra ese piso, con las cuadras
     enumeradas —que es la unidad con la que se camina, no el polígono—;
  3. **el factor de captura esperado contra las dos bases**, para que el resultado se pueda
     controlar cuando vuelva: si la cifra que traen deja un factor fuera de la banda medida en las
     zonas que sí se contaron, hay algo que revisar antes de publicarla.

Esto es preparación, no relevamiento, y no espera a nadie para hacerse.

POR QUÉ EL PERÍMETRO SE ARMA DESDE LAS CALLES
---------------------------------------------
Un polígono es cómodo para el SIG e inútil para el equipo que camina. La gastronomía de la Ciudad
se ordena sobre corredores —una avenida, dos o tres calles transversales— y el relevamiento se
hace por cuadra. Así que el perímetro sale como lista de calles con su tramo de alturas, ordenada
por cuánto de la base documental concentra cada una, y con el corte donde se llega a
`COBERTURA_OBJETIVO`. El resto del barrio no se descarta: se declara como lo que queda afuera del
primer recorte, para que la decisión de ampliarlo sea de la Dirección y no del script.

QUÉ NO HACE ESTE PAQUETE
------------------------
No dice cuántos locales hay. El piso documental es un piso: en las cuatro zonas contadas a pie el
padrón recuperó entre el 7,6 % y el 36,1 % de lo que había en la calle. Un paquete de preparación
que insinúe un número condiciona el conteo, que es exactamente lo que no se quiere.

GUARDARRAÍLES
-------------
- No toca la red. Solo lectura sobre `data/processed/`, `data/raw/` y el SHP del Relevamiento.
- Del padrón se usan dirección y rubro. Titulares, CUIT y teléfonos no se leen: la carga viene de
  `build_capa_homogenea.py`, que ya trabaja sólo con las columnas declaradas.
- Lo que se publica es agregado por calle y tramo de cien. El listado dirección por dirección
  queda en la carpeta interna ignorada por Git.

USO
---
  python scripts/barrido_ciudad/preparar_campo_barrio.py
  python scripts/barrido_ciudad/preparar_campo_barrio.py --barrio "Nuñez"
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import io
import sys
import unicodedata
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_capa_homogenea import (  # noqa: E402
    BARRIOS,
    UBICACION,
    cargar_direcciones_gastronomicas,
)
from places_control_zonas import CRS_METRICO, GEN  # noqa: E402
from cruzar_places_padron import partir_padron, tokens_calle  # noqa: E402

INTERNO = ROOT / "outputs" / "analisis_interno" / "campo_barrios_2026-08"
CAPA_48 = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "capa_homogenea_48_barrios.csv"
CAPA_RUS_BARRIOS = ROOT / "outputs" / "fuentes_externas" / "usos_suelo" / "rus_gastro_48_barrios.csv"
FACTORES = GEN / "factor_captura_22_zonas_dos_bases.csv"
SHP_DIR = ROOT / "outputs" / "fuentes_externas" / "usos_suelo" / "shp"

BARRIOS_POR_DEFECTO = ["Nuñez", "La Boca"]

# La clave sigue siendo la del insumo —`geo_barrios.geojson` escribe «Nuñez» sin tilde y ahí no se
# toca nada—, pero un documento que va a la Dirección lleva el nombre bien escrito.
NOMBRE_PUBLICO = {"Nuñez": "Núñez"}

# Cuánto de la base documental núcleo del barrio tiene que quedar dentro del perímetro propuesto.
# Con 60 % el recorte es chico y camina; con 90 % deja de ser un recorte. La cifra es una decisión
# de diseño y está acá para que se pueda mover a la vista.
COBERTURA_OBJETIVO = 60.0

# La banda de control sale SÓLO de las zonas contadas a pie por la Dirección. Las de directorio
# comercial y las de mínimo relevado no sirven de referencia para un relevamiento nuevo: sus cifras
# no son conteos de campo, y usar su factor como expectativa importaría el defecto de esas fuentes.
FAMILIA_DE_REFERENCIA = "relevamiento propio"


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()


# --------------------------------------------------------------------------- las dos bases

def padron_del_barrio(barrio: str) -> pd.DataFrame:
    """Direcciones con habilitación gastronómica dentro del polígono del barrio.

    Asignación geométrica, regla 4 del método: el campo `barrio` del padrón viene en «No
    determinado» y no se usa. Reproduce `capa_homogenea_48_barrios.csv` y se controla al informar.
    """
    puntos, _ = cargar_direcciones_gastronomicas()
    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]]
    poligono = barrios[barrios.nombre == barrio]
    if not len(poligono):
        raise SystemExit(f"ABORTADO: no hay polígono para «{barrio}». "
                         f"Nombres válidos: {', '.join(sorted(barrios.nombre))}")
    forma = poligono.to_crs(CRS_METRICO).geometry.iloc[0]

    dentro = puntos.to_crs(CRS_METRICO)
    dentro = dentro[dentro.within(forma)].copy()
    ubic = pd.read_csv(UBICACION, low_memory=False)[["id_ubicacion", "direccion_original"]]
    return dentro.merge(ubic, on="id_ubicacion", how="left")


def rus_del_barrio(barrio: str) -> pd.DataFrame | None:
    """Parcelas gastronómicas del Relevamiento en el barrio, con calle y puerta.

    Se filtra por el campo BARRIO del Relevamiento y no por geometría, a propósito: es el mismo
    criterio con el que se calcularon `rus_gastro_48_barrios.csv` y las 20 fichas documentales, y
    cambiarlo acá haría que este paquete no reprodujera la ficha del mismo barrio.

    Dos reglas más que vienen de ahí y que hay que respetar o el número no es el mismo: la unidad
    es la **parcela** (`SMP` único, no el registro: una parcela con dos usos gastronómicos es una
    sola), y el conteo de las dos anillos es sobre las parcelas **ACTIVAS** al momento del
    relevamiento. Las inactivas se informan aparte y no se suman.
    """
    import pyogrio

    from perfilar_usos_suelo import anillos

    rutas = glob.glob(str(SHP_DIR / "*.shp"))
    if not rutas:
        return None
    nucleo, ampliado = anillos()
    clave = plegar(barrio)
    parcelas = pyogrio.read_dataframe(
        rutas[0], columns=["SMP", "BARRIO", "TIPO1", "TIPO2", "ESTADO", "CALLE", "PUERTA", "AÑO"],
        where="TIPO1 = 'UNICOMERCIAL'", read_geometry=False,
    )
    parcelas = parcelas[parcelas.BARRIO.map(plegar) == clave]
    parcelas = parcelas[parcelas.TIPO2.isin(ampliado)].copy()
    parcelas["es_nucleo"] = parcelas.TIPO2.isin(nucleo)
    parcelas["es_activo"] = parcelas.ESTADO == "ACTIVO"
    return parcelas


def cuenta_rus(parcelas: pd.DataFrame, solo_nucleo: bool, activas: bool = True) -> int:
    """Parcelas únicas, en la definición canónica de `perfilar_usos_suelo.capa_por_barrio`."""
    recorte = parcelas[parcelas.es_activo] if activas else parcelas[~parcelas.es_activo]
    if solo_nucleo:
        recorte = recorte[recorte.es_nucleo]
    return int(recorte.SMP.nunique())


# --------------------------------------------------------------------------- corredores

def tramo(altura: int) -> int:
    """El tramo de cien al que pertenece una altura. Es la cuadra, que es la unidad de campo."""
    return int(altura) // 100 * 100


def corredores(padron: pd.DataFrame, rus: pd.DataFrame | None) -> pd.DataFrame:
    """Base documental núcleo por calle y tramo de cien, sumando las dos fuentes.

    Las dos escriben la calle distinto (`CABILDO AV.` contra `AV. CABILDO`), así que se agrupa por
    el conjunto de palabras significativas y se muestra la grafía del Relevamiento, que es la más
    parecida a como está el cartel en la esquina.
    """
    filas = []
    for fila in padron[padron.es_nucleo & ~padron.es_outlier].itertuples():
        for puertas, altura in partir_padron(fila.direccion_original):
            if altura is None:
                continue
            filas.append({"clave": puertas, "grafia_padron": " ".join(sorted(puertas)),
                          "tramo": tramo(altura), "fuente": "padron"})
            break   # una dirección cuenta una vez, en su primera puerta

    if rus is not None:
        # Misma unidad que el conteo canónico: parcela activa del anillo núcleo, `SMP` única.
        activas = rus[rus.es_nucleo & rus.es_activo].drop_duplicates("SMP")
        for fila in activas.itertuples():
            altura = pd.to_numeric(fila.PUERTA, errors="coerce")
            clave = tokens_calle(fila.CALLE)
            if not clave or altura != altura:
                continue
            filas.append({"clave": clave, "grafia_rus": fila.CALLE,
                          "tramo": tramo(altura), "fuente": "rus"})

    if not filas:
        return pd.DataFrame(columns=["calle", "tramo", "padron", "rus", "total"])

    marco = pd.DataFrame(filas)
    grafias = (marco[marco.fuente == "rus"].groupby("clave").grafia_rus.agg(
        lambda serie: serie.value_counts().index[0]).to_dict())
    del_padron = (marco[marco.fuente == "padron"].groupby("clave").grafia_padron.first().to_dict())

    tabla = (marco.groupby(["clave", "tramo"]).fuente.value_counts().unstack(fill_value=0)
             .reset_index())
    for columna in ("padron", "rus"):
        if columna not in tabla:
            tabla[columna] = 0
    tabla["calle"] = [grafias.get(clave, del_padron.get(clave, " ".join(sorted(clave))))
                      for clave in tabla.clave]
    tabla["total"] = tabla.padron + tabla.rus
    return tabla[["calle", "tramo", "padron", "rus", "total"]].sort_values(
        ["total", "calle", "tramo"], ascending=[False, True, True]).reset_index(drop=True)


def recorte(tabla: pd.DataFrame, objetivo: float) -> pd.DataFrame:
    """Las calles que hacen falta para cubrir `objetivo` % de la base documental núcleo.

    Se corta por calle entera, no por tramo suelto: nadie releva media avenida salteada. Dentro de
    cada calle se informa el tramo y ahí sí se puede recortar a ojo sobre el mapa.
    """
    por_calle = tabla.groupby("calle", as_index=False).total.sum().sort_values(
        "total", ascending=False).reset_index(drop=True)
    por_calle["acumulado"] = por_calle.total.cumsum()
    por_calle["pct_acumulado"] = (100 * por_calle.acumulado / por_calle.total.sum()).round(1)
    corte = por_calle[por_calle.pct_acumulado >= objetivo]
    hasta = int(corte.index[0]) if len(corte) else len(por_calle) - 1
    return por_calle.iloc[:hasta + 1]


# --------------------------------------------------------------------------- control

def bandas_de_control() -> dict:
    """Las bandas del factor de captura, medidas sobre las zonas que sí se contaron a pie.

    No son una predicción de cuántos locales hay. Son el rango dentro del cual tiene que caer el
    cociente base/conteo cuando el relevamiento vuelva: afuera de ese rango, o el perímetro no es
    comparable o el conteo tiene un problema, y en cualquier caso se revisa antes de publicar.
    """
    if not FACTORES.exists():
        return {}
    marco = pd.read_csv(FACTORES)
    campo = marco[(marco.metodo == FAMILIA_DE_REFERENCIA) & marco.relevado.notna()]
    salida = {}
    for columna, etiqueta in (("captura_hab_%", "padron"), ("captura_rus_%", "rus")):
        serie = pd.to_numeric(campo[columna], errors="coerce").dropna()
        if len(serie):
            salida[etiqueta] = {"minimo": float(serie.min()), "mediana": float(serie.median()),
                                "maximo": float(serie.max()), "zonas": int(len(serie))}
    return salida


# --------------------------------------------------------------------------- informe

def _coma(valor: float, decimales: int = 1) -> str:
    return f"{valor:.{decimales}f}".replace(".", ",")


def _miles(valor: int) -> str:
    """Separador de miles a la española: 1.504, no 1,504."""
    return f"{valor:,}".replace(",", ".")


def redactar(barrio: str, padron: pd.DataFrame, rus: pd.DataFrame | None,
             tabla: pd.DataFrame, seleccion: pd.DataFrame, bandas: dict, p) -> dict:
    """La ficha de preparación de un barrio. Devuelve sus cifras para el resumen."""
    nucleo = int((padron.es_nucleo & ~padron.es_outlier).sum())
    ampliado = int((padron.es_ampliado & ~padron.es_outlier).sum())
    outliers = int(padron.es_outlier.sum())
    tramites = int(padron.habilitaciones.sum())

    referencia = pd.read_csv(CAPA_48, index_col=0, encoding="utf-8-sig")
    esperado = int(referencia.dir_nucleo.get(barrio, -1))
    controles = ["reproduce la capa homogénea" if esperado == nucleo else
                 f"NO reproduce la capa homogénea (esperado {esperado})"]
    if rus is not None and CAPA_RUS_BARRIOS.exists():
        ficha = pd.read_csv(CAPA_RUS_BARRIOS, index_col=0, encoding="utf-8")
        ficha.index = [plegar(i) for i in ficha.index]
        esperado_rus = ficha.rus_nucleo.get(plegar(barrio))
        obtenido_rus = cuenta_rus(rus, solo_nucleo=True)
        if esperado_rus is not None and esperado_rus == esperado_rus:
            controles.append("reproduce el conteo del Relevamiento"
                             if int(esperado_rus) == obtenido_rus else
                             f"NO reproduce el Relevamiento ({obtenido_rus} contra "
                             f"{int(esperado_rus)} de `rus_gastro_48_barrios.csv`)")

    p(f"## {NOMBRE_PUBLICO.get(barrio, barrio)}")
    p()
    p("### 1 · El piso documental que ya está")
    p()
    p("| fuente | núcleo | ampliado | observación |")
    p("|---|---:|---:|---|")
    p(f"| Padrón de habilitaciones · direcciones | {nucleo} | {ampliado} | "
      f"{_miles(tramites)} trámites 2015-2025, sin bajas; {outliers} direcciones anómalas "
      f"aparte |")
    if rus is not None:
        anada = rus.drop_duplicates("SMP").AÑO.value_counts(normalize=True)
        anada_txt = ", ".join(f"{int(a)}: {_coma(100 * c)} %" for a, c in anada.items())
        p(f"| Relevamiento de Usos del Suelo · parcelas activas | "
          f"{cuenta_rus(rus, solo_nucleo=True)} | {cuenta_rus(rus, solo_nucleo=False)} | "
          f"{cuenta_rus(rus, solo_nucleo=False, activas=False)} parcelas gastronómicas figuran "
          f"inactivas; añada {anada_txt} |")
    p()
    p(f"Control de aceptación: {'; '.join(controles)}.")
    p()
    p("**El piso es un piso.** En las cuatro zonas que la Dirección contó a pie, el padrón "
      "recuperó entre el 7,6 % y el 36,1 % de lo que había en la calle. Estos números dicen dónde "
      "empezar a caminar, no cuánto se va a encontrar.")
    p()

    p("### 2 · Perímetro tentativo")
    p()
    if not len(seleccion):
        p("Sin base documental suficiente para proponer un recorte. Se releva el barrio entero.")
        p()
        return {"barrio": barrio, "nucleo": nucleo, "calles": 0, "cuadras": 0}

    dentro = tabla[tabla.calle.isin(seleccion.calle)]
    cuadras = int(len(dentro))
    p(f"Las **{len(seleccion)} calles** de abajo concentran el "
      f"{_coma(seleccion.pct_acumulado.iloc[-1])} % de la base documental núcleo del barrio "
      f"({int(seleccion.total.sum())} de {int(tabla.total.sum())} registros). Son "
      f"**{cuadras} cuadras** con por lo menos un registro documental.")
    p()
    p("| calle | registros | % acumulado | tramos de altura donde se concentra |")
    p("|---|---:|---:|---|")
    for fila in seleccion.itertuples():
        tramos = dentro[dentro.calle == fila.calle].sort_values("tramo")
        detalle = ", ".join(f"{int(t.tramo)}–{int(t.tramo) + 99} ({int(t.total)})"
                            for t in tramos.itertuples() if t.total >= 2)
        p(f"| {fila.calle} | {int(fila.total)} | {_coma(fila.pct_acumulado)} % | "
          f"{detalle or 'disperso, sin tramo dominante'} |")
    p()
    p("El número entre paréntesis es cuántos registros documentales hay en ese tramo de cien: "
      "sirve para ordenar el recorrido, no para anticipar el conteo. Los tramos con un solo "
      "registro se omiten de la tabla y siguen contando en el total de la calle.")
    p()
    p(f"**Lo que queda afuera de este recorte:** el {_coma(100 - seleccion.pct_acumulado.iloc[-1])} % "
      f"de la base documental, repartido en "
      f"{int(tabla.calle.nunique() - len(seleccion))} calles con pocos registros cada una. "
      "Ampliar el perímetro es decisión de la Dirección; el recorte de arriba es el que hace "
      "caminar menos por registro documental, no el único posible.")
    p()

    p("### 3 · El control para cuando vuelva el conteo")
    p()
    base_padron = int(dentro.padron.sum())
    base_rus = int(dentro.rus.sum())
    p(f"Dentro del perímetro propuesto hay **{base_padron} direcciones del padrón** y "
      f"**{base_rus} parcelas del Relevamiento** en el anillo núcleo. Cuando el relevamiento "
      "traiga su cifra `N`, el factor de captura de cada base es `base ÷ N`, y tiene que caer "
      "dentro de la banda medida en las zonas que sí se contaron a pie:")
    p()
    if bandas:
        p("| base | banda medida (4 zonas contadas a pie) | mediana | si el conteo da N, se espera |")
        p("|---|---|---:|---|")
        for etiqueta, titulo, base in (("padron", "Padrón de habilitaciones", base_padron),
                                       ("rus", "Relevamiento de Usos del Suelo", base_rus)):
            banda = bandas.get(etiqueta)
            if not banda or not base:
                continue
            alto = base / (banda["minimo"] / 100)
            bajo = base / (banda["maximo"] / 100)
            p(f"| {titulo} | {_coma(banda['minimo'])} % – {_coma(banda['maximo'])} % | "
              f"{_coma(banda['mediana'])} % | N entre {int(bajo)} y {int(alto)} |")
        p()
        p("**La banda es ancha a propósito y no es un pronóstico.** Un conteo que caiga adentro no "
          "queda validado por eso; uno que caiga afuera sí obliga a revisar —el perímetro, el "
          "criterio de rubro o el conteo— antes de publicar nada.")
    else:
        p("No se encontró `factor_captura_22_zonas_dos_bases.csv`: la banda de control no se pudo "
          "calcular. Corré `capa_rus_por_zona.py` antes de usar este paquete.")
    p()
    p("### 4 · Que el conteo salga comparable")
    p()
    p("Para que la cifra se pueda poner al lado de Villa Crespo y Caballito, el relevamiento tiene "
      "que usar las mismas tres reglas que ésas:")
    p()
    p("1. **Anillo núcleo**: restaurante, bar, café, pizzería, parrilla, comida al paso y "
      "heladería. Panadería, pastelería y catering se anotan aparte, en el ampliado.")
    p("2. **La unidad es el local con puerta a la calle.** Los puestos dentro de un patio de "
      "comidas o de un mercado se anotan aparte: en el padrón entran como una sola dirección y "
      "mezclarlos rompe la comparación.")
    p("3. **Fecha del recorrido por cuadra.** Es lo que permite leer después una diferencia como "
      "apertura o cierre en vez de como error.")
    p()
    return {"barrio": barrio, "nucleo": nucleo, "calles": int(len(seleccion)),
            "cuadras": cuadras, "base_padron_perimetro": base_padron,
            "base_rus_perimetro": base_rus}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--barrio", action="append", dest="barrios",
                        help="puede repetirse; por defecto Nuñez y La Boca")
    args = parser.parse_args()
    barrios = args.barrios or BARRIOS_POR_DEFECTO

    salida = io.StringIO()
    def p(*texto) -> None:
        print(*texto, file=salida)

    p("# Preparación de campo · Núñez y La Boca")
    p()
    p(f"**Fecha:** {dt.date.today().strftime('%d de agosto de %Y')}  ")
    p("**Qué es:** el piso documental, un perímetro tentativo y el control de resultado para dos "
      "barrios que se van a relevar a pie. **No es un conteo y no lo reemplaza.**")
    p()
    p("Estos dos barrios no salen como fichas documentales. Las otras veinte sí, con su salvedad "
      "y su añada declaradas, porque ahí la base documental es lo que hay. Acá se decidió otra "
      "cosa: Núñez y La Boca se cuentan en la calle, al nivel de Caballito y Villa Crespo. La "
      "prueba de techo sobre Places cerró que no hay atajo —recupera del orden del 12 % de una "
      "cifra contada a pie, y es techo estructural de la fuente, no de esa corrida—.")
    p()
    p("---")
    p()

    bandas = bandas_de_control()
    resumenes, corredores_todos = [], []
    INTERNO.mkdir(parents=True, exist_ok=True)
    for barrio in barrios:
        padron = padron_del_barrio(barrio)
        rus = rus_del_barrio(barrio)
        tabla = corredores(padron, rus)
        seleccion = recorte(tabla, COBERTURA_OBJETIVO) if len(tabla) else tabla
        resumenes.append(redactar(barrio, padron, rus, tabla, seleccion, bandas, p))
        p("---")
        p()

        marcado = tabla.copy()
        marcado.insert(0, "barrio", barrio)
        marcado["en_el_perimetro"] = marcado.calle.isin(seleccion.calle) if len(seleccion) else False
        corredores_todos.append(marcado)
        # El listado dirección por dirección queda afuera de Git.
        padron[["id_ubicacion", "direccion_original", "habilitaciones",
                "es_nucleo", "es_ampliado", "es_outlier"]].to_csv(
            INTERNO / f"padron_{plegar(barrio).replace(' ', '_')}.csv",
            index=False, encoding="utf-8-sig")

    p("## Lo que este paquete no dice")
    p()
    p("- **No dice cuántos locales hay.** El piso documental es un piso y la banda de control es "
      "ancha; anticipar un número condicionaría el conteo.")
    p("- **No fija el perímetro.** Propone el recorte que concentra la base documental conocida; "
      "si la Dirección sabe de un corredor que el padrón no ve, ese corredor entra.")
    p("- **No reemplaza la ficha documental de La Boca**, que existe y sigue siendo válida para "
      "lo que es: base documental con su añada declarada.")
    p()

    destino = GEN / "PREPARACION_CAMPO_NUNEZ_LA_BOCA.md"
    destino.write_text(salida.getvalue(), encoding="utf-8")
    pd.concat(corredores_todos).to_csv(
        GEN / "corredores_campo_nunez_la_boca.csv", index=False, encoding="utf-8")
    print(salida.getvalue())
    print(f"  publicado: {destino.relative_to(ROOT)}")
    print(f"  publicado: {(GEN / 'corredores_campo_nunez_la_boca.csv').relative_to(ROOT)}")
    print(f"  interno (fuera de Git): {INTERNO}")
    for resumen in resumenes:
        print(f"    {resumen['barrio']}: {resumen['nucleo']} núcleo, "
              f"{resumen['calles']} calles, {resumen['cuadras']} cuadras")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
