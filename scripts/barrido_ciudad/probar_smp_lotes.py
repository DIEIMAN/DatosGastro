"""Prueba del SMP: ¿los lotes de permisos son un solo inmueble cargado por frente de manzana?

El detector de lotes (`detectar_lotes_permisos.py`) dejó una hipótesis muy bien fundada pero no
cerrada: 45 lotes donde varias direcciones distintas cuelgan de la misma partida matriz, con la
misma firma de rubros y sin fecha de habilitación. La lectura propuesta era que no son locales por
puerta sino **un inmueble cargado contra cada número del frente de manzana**. Faltaba la prueba.

La prueba está en los crudos de F02 de 2015 a 2024, que traen `seccion`, `manzana` y `parcela` — la
clave catastral SMP — además de `partida_matriz`. La cohorte 2025, que es donde están los lotes,
trae partida pero no SMP. Uniendo por partida se resuelve la pregunta:

  - si las direcciones de un lote caen todas en **una sola parcela SMP**, es un inmueble y el
    patrón es carga por frente de manzana: confirmado;
  - si caen en parcelas distintas, la interpretación hay que revisarla.

El test necesita una línea de base, porque «una partida = una parcela» sólo prueba algo si no es
cierto por construcción. Y la línea de base tiene que ser **condicional al número de direcciones de
la partida**: la enorme mayoría de las ~40.000 partidas del crudo tiene una sola dirección, y una
partida con una dirección resuelve a una parcela trivialmente. Medida contra ese universo, la tasa
global no discrimina — 48 de 48 sería lo esperable por azar. La comparación honesta es contra el
estrato al que pertenecen los lotes, que es el de muchas direcciones. Las partidas del test se
excluyen además de su propio estrato: si no, la base se mide en parte sobre lo que se quiere probar.

Hay una segunda evidencia, más directa, dentro del mismo crudo: el campo `calles` admite **varios
números de puerta en un mismo registro** (`PUEYRREDON AV. 460;PUEYRREDON AV. 468`). Es el
mecanismo a la vista: el padrón anota todo el frente del inmueble en un registro, y cuando la
exportación de 2025 lo aplana a un `domicilio` por fila, cada número del frente se convierte en una
«dirección» propia. Ésta es la evidencia causal, y es la que sostiene la conclusión; el catastro
corrobora.

Privacidad: los crudos traen `titulares` y `cuits`. **No se leen.** Las columnas que se abren están
declaradas en `COLUMNAS_SEGURAS`; cualquier otra queda fuera del `usecols`, así que no entra en
memoria. Lo que se exporta es partida, SMP, dirección del inmueble y conteos.

Uso:
  python scripts/barrido_ciudad/probar_smp_lotes.py
"""
from __future__ import annotations

import io
import json
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "generado"
LOTES = OUT_DIR / "lotes_permisos_detectados.csv"
F02_2025 = RAW / "f02_habilitaciones_aprobadas_2025.csv"

# Las cohortes con clave catastral. La de 2025 no la tiene: aporta la partida y el domicilio.
COHORTES_SMP = ["2015_2018", "2019", "2020", "2021", "2022", "2023", "2024"]

# Único punto donde se declara qué se lee. `titulares` y `cuits` no están y no pueden estarlo:
# el `usecols` de pandas se arma desde acá.
COLUMNAS_SEGURAS = {
    "seccion": "seccion", "manzana": "manzana", "parcela": "parcela",
    "partida_matriz": "partida_matriz", "calles": "calles",
    "fecha_habilitacion": "fecha", "fechahabilitacion": "fecha",
    "descripcion_rubro": "rubro", "descripcionrubro": "rubro",
    "numero_expediente": "expediente", "numeroexp": "expediente",
}
CLAVES_SMP = ["seccion", "manzana", "parcela", "partida_matriz"]

# Los estratos de la línea de base: partidas agrupadas por cuántas direcciones distintas tienen.
ESTRATOS = [(1, 1, "1"), (2, 2, "2"), (3, 5, "3-5"), (6, 10, "6-10"), (11, 10 ** 9, "11+")]
SIN_DIRECCION = "sin dato"


def leer_cohortes_smp() -> pd.DataFrame:
    """Los crudos de 2015-2024, sólo con las columnas seguras. `latin-1` y separador `;`."""
    marcos = []
    for cohorte in COHORTES_SMP:
        ruta = RAW / f"f02_habilitaciones_aprobadas_{cohorte}.csv"
        encabezado = pd.read_csv(ruta, sep=";", encoding="latin-1", nrows=0)
        renombre = {c: COLUMNAS_SEGURAS[c.lower()] for c in encabezado.columns
                    if c.lower() in COLUMNAS_SEGURAS}
        datos = pd.read_csv(ruta, sep=";", encoding="latin-1", low_memory=False,
                            usecols=list(renombre)).rename(columns=renombre)
        datos["cohorte"] = cohorte
        marcos.append(datos)
    return pd.concat(marcos, ignore_index=True)


def normalizar(serie: pd.Series) -> pd.Series:
    """Sección, manzana y parcela vienen con relleno de ceros y espacios, y la parcela es
    alfanumérica (`016q`, `158C`). Sin normalizar, `105 ` y `105` cuentan como dos manzanas."""
    return serie.astype(str).str.strip().str.upper().str.lstrip("0")


def explotar_multivalor(datos: pd.DataFrame) -> pd.DataFrame:
    """Un registro puede abarcar dos parcelas, y entonces las cuatro claves vienen con `;` adentro.

    Los cuatro campos vienen alineados posicionalmente (`29;29` / `105 ;105` / `019 ;019A` /
    `341115;378814`), así que se explotan juntos. Si alguna fila no estuviera alineada se descarta,
    y el conteo se informa: preferimos perder una fila antes que cruzar la sección de una con la
    parcela de otra.
    """
    datos = datos.dropna(subset=CLAVES_SMP).copy()
    for clave in CLAVES_SMP:
        datos[clave] = datos[clave].astype(str).str.split(";")
    largo = datos.seccion.str.len()
    alineadas = datos[(datos.manzana.str.len() == largo) & (datos.parcela.str.len() == largo)
                      & (datos.partida_matriz.str.len() == largo)]
    if len(alineadas) < len(datos):
        print(f"  aviso: {len(datos) - len(alineadas)} filas con claves desalineadas, descartadas")

    abierto = alineadas.explode(CLAVES_SMP)
    abierto["smp"] = (normalizar(abierto.seccion) + "-" + normalizar(abierto.manzana)
                      + "-" + normalizar(abierto.parcela))
    abierto["partida"] = pd.to_numeric(abierto.partida_matriz.str.strip(), errors="coerce")
    return abierto.dropna(subset=["partida"]).astype({"partida": int})


def puertas(grupo: pd.DataFrame) -> list[str]:
    """Números de puerta distintos de una parcela, abriendo los `calles` multivalor."""
    return sorted({d.strip() for valor in grupo.calles.dropna()
                   for d in str(valor).split(";") if d.strip()})


def direcciones_por_partida(abierto: pd.DataFrame) -> pd.Series:
    """Números de puerta distintos de cada partida, abriendo los `calles` multivalor.

    Es la variable que estratifica la línea de base. Se mide sobre el mismo crudo que el test, así
    que los estratos y el test hablan de lo mismo.
    """
    largo = abierto[["partida", "calles"]].dropna(subset=["calles"]).copy()
    largo["puerta"] = largo.calles.astype(str).str.split(";")
    largo = largo.explode("puerta")
    largo["puerta"] = largo.puerta.str.strip()
    return largo[largo.puerta != ""].groupby("partida").puerta.nunique()


def etiqueta_estrato(cuantas: int) -> str:
    for bajo, alto, nombre in ESTRATOS:
        if bajo <= cuantas <= alto:
            return nombre
    return SIN_DIRECCION


def linea_de_base(abierto: pd.DataFrame, partidas_test: set[int]) -> pd.DataFrame:
    """Una fila por partida: cuántas parcelas SMP tiene, cuántas direcciones, en qué estrato cae."""
    parcelas = abierto.groupby("partida").smp.nunique()
    base = pd.DataFrame({
        "parcelas": parcelas,
        "registros": abierto.groupby("partida").smp.size(),
        "direcciones": direcciones_por_partida(abierto).reindex(parcelas.index, fill_value=0),
    })
    base["estrato"] = base.direcciones.map(etiqueta_estrato)
    base["una_parcela"] = base.parcelas == 1
    base["es_test"] = base.index.isin(partidas_test)
    return base


def partidas_de_los_lotes() -> pd.DataFrame:
    """Partida matriz de cada lote, leída de la cohorte 2025 por el domicilio del lote."""
    lotes = pd.read_csv(LOTES, encoding="utf-8")
    crudo = pd.read_csv(F02_2025, low_memory=False, encoding="utf-8",
                        usecols=["domicilio", "nropartidamatriz"])
    crudo["domicilio"] = crudo.domicilio.astype(str).str.strip()
    cruce = crudo[crudo.domicilio.isin(set(lotes.direccion))].merge(
        lotes[["direccion", "lote", "barrio", "calle"]].drop_duplicates(),
        left_on="domicilio", right_on="direccion")
    cruce["partida"] = pd.to_numeric(cruce.nropartidamatriz, errors="coerce")
    return cruce.dropna(subset=["partida"]).astype({"partida": int})


def main() -> int:
    buffer = io.StringIO()

    def p(*args):
        print(*args, file=buffer)

    p("Prueba del SMP · ¿los lotes de permisos son un solo inmueble?")
    p("=" * 78)
    p("")

    crudo = leer_cohortes_smp()
    abierto = explotar_multivalor(crudo)
    p(f"crudos de F02 {COHORTES_SMP[0]}–{COHORTES_SMP[-1]}: {len(crudo):,} registros, "
      f"{len(abierto):,} pares registro-parcela")
    p(f"  con clave catastral completa: {100 * len(abierto) / len(crudo):.1f} % de los registros")
    p("")

    # 1 · La línea de base, estratificada. Sin estratificar no discrimina: casi todas las partidas
    #     del crudo tienen una sola dirección y resuelven a una parcela por construcción.
    lotes = partidas_de_los_lotes()
    partidas_test = set(lotes.partida.unique())
    base = linea_de_base(abierto, partidas_test)
    base_una = 100 * base.una_parcela.mean()

    p("1 · LÍNEA DE BASE — ¿una partida matriz equivale a una parcela?")
    p(f"  partidas distintas en el crudo: {len(base):,}")
    p(f"  tasa global de una sola parcela SMP: {base_una:.2f} %  "
      f"(mediana {base.parcelas.median():g}, máximo {int(base.parcelas.max())})")
    p("")
    p("  Esa tasa global NO es la línea de base del test. El "
      f"{100 * base.direcciones.le(1).mean():.1f} % de las partidas tiene")
    p("  una sola dirección, y una partida con una dirección resuelve a una parcela")
    p("  trivialmente. Los lotes viven en el otro extremo. La base tiene que ser condicional al")
    p("  número de direcciones de la partida, y sin las partidas del test adentro.")
    p("")

    orden = [nombre for _, _, nombre in ESTRATOS] + [SIN_DIRECCION]
    tasa_limpia: dict[str, float] = {}
    resumen = []
    for nombre in orden:
        estrato = base[base.estrato == nombre]
        if estrato.empty:
            continue
        limpio = estrato[~estrato.es_test]
        tasa_limpia[nombre] = limpio.una_parcela.mean() if len(limpio) else float("nan")
        resumen.append({
            "direcciones": nombre,
            "partidas": len(estrato),
            "una_parcela_%": round(100 * estrato.una_parcela.mean(), 2),
            "sin_las_del_test": len(limpio),
            "base_limpia_%": round(100 * tasa_limpia[nombre], 2) if len(limpio) else None,
            "partidas_del_test": int(estrato.es_test.sum()),
        })
    tabla_base = pd.DataFrame(resumen)
    p("  " + tabla_base.to_string(index=False).replace("\n", "\n  "))
    p("")
    p("  `base_limpia_%` es la columna que vale: la tasa del estrato excluyendo las partidas de")
    p("  los lotes, que si no se mediría en parte sobre lo que se quiere probar.")
    p("")

    # 2 · El test. Cada partida de cada lote, contra el catastro.
    filas = []
    for fila in lotes[["lote", "partida"]].drop_duplicates().itertuples():
        parcela = abierto[abierto.partida == fila.partida]
        detalle = lotes[(lotes.lote == fila.lote) & (lotes.partida == fila.partida)]
        filas.append({
            "lote": fila.lote,
            "partida_matriz": fila.partida,
            "barrio": detalle.barrio.iloc[0],
            "direcciones_2025": int(detalle.domicilio.nunique()),
            "registros_2015_2024": len(parcela),
            "parcelas_smp": int(parcela.smp.nunique()) if len(parcela) else None,
            "smp": parcela.smp.iloc[0] if len(parcela) else "",
            "puertas_en_el_crudo": len(puertas(parcela)) if len(parcela) else None,
            "estrato": base.estrato.get(fila.partida, ""),
        })
    prueba = pd.DataFrame(filas).sort_values("lote")
    halladas = prueba[prueba.parcelas_smp.notna()]
    una_sola = halladas[halladas.parcelas_smp == 1]

    p("2 · EL TEST — las direcciones de cada lote, ¿caen en una parcela o en varias?")
    p(f"  pares lote-partida examinados: {len(prueba)}  "
      f"({prueba.partida_matriz.nunique()} partidas distintas)")
    p(f"  halladas en el crudo 2015-2024: {len(halladas)} de {len(prueba)}")
    p(f"  **que resuelven a UNA SOLA parcela SMP: {len(una_sola)} de {len(halladas)} "
      f"({100 * len(una_sola) / len(halladas):.1f} %)**")
    if len(halladas) > len(una_sola):
        p("")
        p("  las que NO resuelven a una sola parcela (revisar la interpretación en estos casos):")
        p("  " + halladas[halladas.parcelas_smp > 1].to_string(index=False).replace("\n", "\n  "))
    p("")
    p(prueba.to_string(index=False))
    p("")

    # 2b · ¿El test discrimina? Se compara el resultado contra la base ingenua y contra la
    #      condicional, estrato por estrato. La unidad independiente es la partida, no el par:
    #      37, no 48 — los pares repiten inmuebles (la manzana de Florida sale tres veces).
    unicas = halladas.drop_duplicates("partida_matriz")
    p_ingenua = base.una_parcela.mean() ** len(unicas)

    aporte = []
    for nombre in orden:
        en_estrato = unicas[unicas.estrato == nombre]
        if en_estrato.empty:
            continue
        tasa = tasa_limpia.get(nombre, float("nan"))
        aporte.append({
            "direcciones": nombre,
            "partidas_del_test": len(en_estrato),
            "resuelven_a_una": int((en_estrato.parcelas_smp == 1).sum()),
            "base_limpia_%": round(100 * tasa, 2),
            "p_por_azar_%": round(100 * tasa ** len(en_estrato), 3),
        })
    tabla_aporte = pd.DataFrame(aporte)
    p_condicional = float((tabla_aporte["p_por_azar_%"] / 100).prod())

    p("2b · ¿DISCRIMINA EL TEST? — el resultado contra cada línea de base")
    p(f"  unidades independientes: {len(unicas)} partidas distintas "
      f"(los {len(halladas)} pares repiten inmuebles)")
    p("")
    p("  " + tabla_aporte.to_string(index=False).replace("\n", "\n  "))
    p("")
    p(f"  con la base GLOBAL ({100 * base.una_parcela.mean():.2f} %), acertar las {len(unicas)} "
      f"por azar: {100 * p_ingenua:.1f} %")
    p(f"  con la base CONDICIONAL al estrato:                     "
      f"          {100 * p_condicional:.2f} %")
    p("")
    p("  DIAGNÓSTICO. El test discrimina, pero no parejo, y el promedio lo esconde:")
    p("")
    fuerte = tabla_aporte[tabla_aporte["base_limpia_%"] < 90]
    debil = tabla_aporte[tabla_aporte["base_limpia_%"] >= 99]
    if len(fuerte):
        n_fuerte = int(fuerte.partidas_del_test.sum())
        p(f"  · donde vale: las {n_fuerte} partidas de los estratos altos "
          f"({', '.join(fuerte.direcciones)} direcciones). Ahí la")
        p(f"    base cae al {fuerte['base_limpia_%'].min():.1f} % —la partida se reparte entre "
          "varias parcelas con")
        p("    frecuencia real— y sin embargo resuelven todas a una. Son además los inmuebles que")
        p("    generan el grueso del fenómeno: las manzanas del centro, Liniers y Palermo.")
    if len(debil):
        n_debil = int(debil.partidas_del_test.sum())
        p(f"  · donde no dice nada: las {n_debil} partidas de {', '.join(debil.direcciones)} "
          f"direcciones, con base ≥ {debil['base_limpia_%'].min():.1f} %.")
        p("    Que resuelvan a una parcela era lo esperable sin hipótesis ninguna. Contarlas como")
        p("    aciertos infla el resultado: por eso no se reporta «48 de 48» a secas.")
    p("")

    # 3 · El mecanismo, a la vista en el propio crudo.
    multi = crudo.calles.astype(str).str.contains(";", na=False)
    por_parcela = abierto.groupby("smp").apply(lambda g: len(puertas(g)))
    p("3 · EL MECANISMO — el padrón anota el frente entero del inmueble en un registro")
    p(f"  registros con más de un número de puerta en el campo `calles`: {int(multi.sum()):,} "
      f"= {100 * multi.mean():.1f} % del crudo")
    p("  Ejemplo textual del crudo: `PUEYRREDON AV. 460;PUEYRREDON AV. 468` — una parcela, una")
    p("  partida, dos números. `CIUDAD DE LA PAZ 2369;CABILDO AV. 2370` — una esquina.")
    p("")
    p(f"  parcelas con más de un número de puerta: {int((por_parcela > 1).sum()):,} de "
      f"{len(por_parcela):,} ({100 * (por_parcela > 1).mean():.1f} %)")
    p(f"  máximo de números de puerta en una sola parcela: {int(por_parcela.max())}")
    p("")
    p("  Las parcelas más grandes, con nombre y apellido. Una misma parcela puede aparecer en")
    p("  varios lotes: es el mismo inmueble visto desde calles distintas de su frente.")
    # Una fila por parcela, no por par lote-partida: si no, la manzana de Florida sale tres veces.
    por_inmueble = prueba.groupby("partida_matriz").agg(
        lotes=("lote", lambda s: "/".join(sorted(s))),
        direcciones_2025=("direcciones_2025", "sum"),
        smp=("smp", "first"), barrio=("barrio", "first"),
        puertas=("puertas_en_el_crudo", "first")).reset_index()
    for _, fila in por_inmueble[por_inmueble.puertas.fillna(0) > 10].nlargest(
            6, "puertas").iterrows():
        parcela = abierto[abierto.partida == fila.partida_matriz]
        calles = sorted({d.rsplit(" ", 1)[0] for d in puertas(parcela)})
        p(f"    {fila.lotes} · partida {fila.partida_matriz} · SMP {fila.smp} · {fila.barrio}")
        p(f"       {int(fila.puertas)} números de puerta sobre {len(calles)} "
          f"calle(s): {', '.join(calles[:5])}")
        p(f"       de ahí salen las {int(fila.direcciones_2025)} «direcciones» del padrón 2025")
    p("")

    p("VEREDICTO")
    if len(halladas) and len(una_sola) == len(halladas):
        p("  El patrón queda confirmado: **son inmuebles únicos cargados contra cada número de su")
        p("  frente de manzana**, no locales por puerta. Lo que lo prueba es el mecanismo del")
        p("  punto 3, que es causal y está dentro del propio padrón: el campo `calles` asienta el")
        p(f"  frente entero del inmueble en un solo registro ({100 * multi.mean():.1f} % de los "
          "registros), y la")
        p("  exportación de 2025 lo aplana a un domicilio por fila.")
        p("")
        p(f"  El catastro corrobora: las {halladas.partida_matriz.nunique()} partidas distintas de "
          f"los {prueba.lote.nunique()} lotes ({len(halladas)} pares) resuelven")
        p("  todas a una sola parcela, sin excepciones. Con qué fuerza hay que leer ese dato lo")
        p("  dice el punto 2b, no el 100 % a secas.")
    else:
        p("  El test no da unánime. Revisar los casos de más de una parcela antes de afirmar nada.")
    p("")
    p("  Consecuencia práctica, que no cambia: la regla 3 del método ya saca estas direcciones del")
    p("  conteo, así que ninguna cifra publicada está afectada. Lo que sí cambia es el estatus de")
    p("  la consulta a la AGC: deja de ser «¿esto qué es?» y pasa a ser «esto es esto, ¿lo")
    p("  confirman?».")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    prueba.to_csv(OUT_DIR / "prueba_smp_lotes.csv", index=False, encoding="utf-8")
    tabla_base.to_csv(OUT_DIR / "base_smp_estratos.csv", index=False, encoding="utf-8")
    tabla_aporte.to_csv(OUT_DIR / "discriminancia_smp.csv", index=False, encoding="utf-8")
    # Los escalares del mecanismo, para que la nota a la AGC los cite sin hardcodearlos.
    json.dump({
        "registros_crudo": int(len(crudo)),
        "pct_registros_multivalor": round(100 * float(multi.mean()), 1),
        "parcelas_con_mas_de_una_puerta": int((por_parcela > 1).sum()),
        "parcelas_totales": int(len(por_parcela)),
        "pct_parcelas_multipuerta": round(100 * float((por_parcela > 1).mean()), 1),
        "max_puertas_en_una_parcela": int(por_parcela.max()),
        "base_global_pct": round(float(base_una), 2),
        "p_ingenua_pct": round(100 * float(p_ingenua), 1),
        "p_condicional_pct": round(100 * p_condicional, 2),
        "partidas_test": int(len(unicas)),
    }, (OUT_DIR / "mecanismo_smp.json").open("w", encoding="utf-8"), indent=2,
        ensure_ascii=False)
    (OUT_DIR / "PRUEBA_SMP_LOTES.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    print(f"escrito en {OUT_DIR.relative_to(ROOT)}: PRUEBA_SMP_LOTES.txt, prueba_smp_lotes.csv, "
          "base_smp_estratos.csv, discriminancia_smp.csv, mecanismo_smp.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
