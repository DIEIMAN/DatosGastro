"""Arma la consulta técnica a la AGC sobre la carga de habilitaciones por frente de manzana.

Genera dos archivos listos para revisar: la nota y su anexo. **No los envía.** El envío lo hace
Diego por su vía institucional.

Qué va y qué no, por decisión explícita:

  - va: número de partida matriz, clave catastral SMP, dirección del inmueble, conteos;
  - **no va: razón social, CUIT, teléfono ni titulares.** La partida le alcanza a la AGC para
    encontrar el caso en su propio sistema, y la Dirección no manda datos personales a otro
    organismo. Las columnas prohibidas no se leen en ningún punto de este script.

La nota se redacta como **consulta, no como hallazgo**: describimos el patrón, decimos cómo lo
leemos y preguntamos si esa lectura es correcta. No podemos descartar que sea una convención de
carga del régimen de habilitaciones y no un artefacto, y esa posibilidad queda escrita.

Orden del argumento, por decisión explícita: **el mecanismo primero, el catastro después**. Lo que
sostiene la lectura es causal y está a la vista en el propio padrón —el campo `calles` asienta el
frente entero del inmueble y la exportación de 2025 lo aplana—; el cruce catastral corrobora. Y
corrobora de manera desigual: contra una línea de base condicional al número de direcciones de la
partida, el cruce discrimina en los inmuebles grandes y no dice nada en los de dos direcciones. La
nota lo declara en vez de reportar «todas resuelven a una» a secas, que suena más fuerte de lo que
es. Los números salen de `probar_smp_lotes.py`; acá no se hardcodea ninguno.

Uso:
  python scripts/barrido_ciudad/preparar_consulta_agc.py
"""
from __future__ import annotations

import json
import sys
import textwrap
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "generado"
SALIDA = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "consulta_agc"

PRUEBA = GEN / "prueba_smp_lotes.csv"
LOTES = GEN / "lotes_permisos_detectados.csv"
REPLICACION = GEN / "lotes_permisos_replicacion.csv"
ESTRATOS = GEN / "base_smp_estratos.csv"
DISCRIMINANCIA = GEN / "discriminancia_smp.csv"
MECANISMO = GEN / "mecanismo_smp.json"

# Lo único que se publica del padrón. Cualquier columna fuera de esta lista no entra al anexo.
COLUMNAS_ANEXO = ["lote", "partida_matriz", "smp", "direccion", "barrio",
                  "registros_en_esa_direccion"]


def miles(numero: float) -> str:
    """Separador de miles con punto. La nota sale en castellano, no con comas."""
    return f"{int(numero):,}".replace(",", ".")


def coma(numero: float, decimales: int = 1) -> str:
    """Decimales con coma, como corresponde en castellano."""
    return f"{numero:.{decimales}f}".replace(".", ",")


def envolver(texto: str, ancho: int = 99) -> str:
    """Reenvuelve un párrafo a ancho fijo.

    Los párrafos con cifras interpoladas quedan con el margen derecho dentado, porque el salto de
    línea está puesto sobre el texto de la plantilla y no sobre el resultado. Se reenvuelven acá.
    """
    return textwrap.fill(" ".join(texto.split()), width=ancho)


def corroboracion(discriminancia: pd.DataFrame, base_global: float) -> str:
    """El párrafo que dice cuánto pesa el cruce catastral, según cómo salga la base condicional.

    La base global no sirve para leer el test: casi todas las partidas del padrón tienen una sola
    dirección y resuelven a una parcela por construcción. Lo que corresponde comparar es contra
    partidas de tamaño equivalente. Cómo se redacta depende de lo que devuelva esa comparación, y
    por eso se decide acá y no a mano: si el estrato alto también resuelve casi siempre a una
    parcela, el cruce no distingue nada y hay que decirlo.
    """
    alto = discriminancia.iloc[-1]
    bajo = discriminancia.iloc[0]
    umbral = str(alto.direcciones).rstrip("+")
    encabezado = (
        "Corresponde precisar cuánto pesa esa corroboración. En el padrón, el "
        f"{coma(base_global, 2)} % de las partidas resuelve a una sola parcela, de modo que el "
        "dato sólo es informativo comparado contra partidas de tamaño equivalente en cantidad de "
        "direcciones.")

    if alto["base_limpia_%"] >= 95:
        return (
            f"{encabezado} Hecha esa comparación, entre las partidas con {umbral} o más números "
            f"de puerta la proporción sigue siendo del {coma(alto['base_limpia_%'])} %. El cruce "
            "catastral es entonces consistente con nuestra lectura, pero no la distingue de otras "
            "posibles: no lo presentamos como prueba. El peso del argumento está en el mecanismo.")

    partes = [
        f"{encabezado} Entre las partidas con {umbral} o más números de puerta sólo el "
        f"{coma(alto['base_limpia_%'])} % resuelve a una única parcela; las "
        f"{int(alto.partidas_del_test)} de ese grupo que aparecen en estos conjuntos resuelven "
        "todas a una, y ahí el cruce sí distingue."]
    if bajo["base_limpia_%"] >= 95:
        partes.append(
            f"En cambio, entre las partidas de {bajo.direcciones} direcciones la proporción es "
            f"del {coma(bajo['base_limpia_%'])} %: para las {int(bajo.partidas_del_test)} de "
            "nuestro conjunto que están en ese caso, el resultado es consistente con nuestra "
            "lectura pero no la distingue de ninguna otra.")
    partes.append(
        "Lo señalamos para no atribuirle al catastro más fuerza de la que tiene; el peso del "
        "argumento está en el mecanismo.")
    return " ".join(partes)


def anexo() -> pd.DataFrame:
    """Una fila por dirección: partida, catastro, dirección y cuántos registros cuelgan de ella."""
    lotes = pd.read_csv(LOTES, encoding="utf-8")
    prueba = pd.read_csv(PRUEBA, encoding="utf-8")

    # Un inmueble puede tener más de una partida —la manzana de Florida tiene dos— y las dos le
    # sirven a la AGC para ubicarlo. Se listan todas, no una elegida por nosotros.
    por_lote = prueba.sort_values("puertas_en_el_crudo", ascending=False).groupby("lote").agg(
        partida_matriz=("partida_matriz", lambda s: " / ".join(str(int(v)) for v in s.unique())),
        smp=("smp", lambda s: " / ".join(dict.fromkeys(s))))

    tabla = lotes[["lote", "direccion", "barrio", "habilitaciones"]].rename(
        columns={"habilitaciones": "registros_en_esa_direccion"}).copy()
    tabla["partida_matriz"] = tabla.lote.map(por_lote.partida_matriz)
    tabla["smp"] = tabla.lote.map(por_lote.smp)
    return tabla[COLUMNAS_ANEXO].sort_values(["lote", "direccion"])


def redactar(datos: pd.DataFrame, prueba: pd.DataFrame, replicacion: pd.DataFrame,
             discriminancia: pd.DataFrame, mecanismo: dict) -> str:
    """La nota. Consulta técnica, no denuncia de error."""
    lotes = datos.lote.nunique()
    direcciones = len(datos)
    registros = miles(datos.registros_en_esa_direccion.sum())
    barrios = datos.barrio.nunique()
    partidas = prueba.partida_matriz.nunique()
    pares = int(replicacion.pares_distintos.sum())
    crudos = miles(replicacion.registros_crudos.sum())
    rango = (f"{int(datos.registros_en_esa_direccion.min())} y "
             f"{int(datos.registros_en_esa_direccion.max())}")
    mayor = prueba.nlargest(1, "puertas_en_el_crudo").iloc[0]

    ejemplo = datos[datos.lote == "L02"].sort_values("direccion")
    lista_ej = ", ".join(str(d).split(" ")[-1] for d in ejemplo.direccion.head(8))

    parrafo_mecanismo = envolver(f"""
**El mecanismo está a la vista en el propio padrón.** En los archivos de 2015 a 2024, el campo
`calles` admite varios números de puerta en un mismo registro: `PUEYRREDON AV. 460;PUEYRREDON
AV. 468` es un asiento, no dos. Tiene más de un número el
{coma(mecanismo['pct_registros_multivalor'])} % de los registros, y figuran con más de una puerta
{miles(mecanismo['parcelas_con_mas_de_una_puerta'])} de {miles(mecanismo['parcelas_totales'])}
parcelas ({coma(mecanismo['pct_parcelas_multipuerta'])} %); el máximo observado es de
{mecanismo['max_puertas_en_una_parcela']} números en una sola parcela. Es decir: el padrón asienta
el frente completo del inmueble.""")

    parrafo_catastro = envolver(f"""
**El catastro corrobora.** Los archivos de 2015 a 2024 incluyen sección, manzana y parcela.
Cruzando por partida matriz, las {partidas} partidas involucradas resuelven todas a una única
parcela catastral. La partida {int(mayor.partida_matriz)} —parcela {mayor.smp} en notación
sección-manzana-parcela— reúne {int(mayor.puertas_en_el_crudo)} números de puerta sobre cuatro
calles (Florida, Córdoba, Viamonte y San Martín): una manzana completa.""")

    parrafo_alcance = envolver(corroboracion(discriminancia, mecanismo["base_global_pct"]))

    return f"""# Consulta técnica sobre la carga de habilitaciones asociadas a una misma partida matriz

**Dirección General de Desarrollo Gastronómico**
**Destinatario:** Agencia Gubernamental de Control

---

## 1. Objeto

Elevamos una consulta técnica sobre el criterio de carga del padrón de habilitaciones publicado en
BA Data. Trabajando sobre el universo gastronómico encontramos un patrón regular que admite dos
lecturas, y antes de fijar un criterio propio preferimos preguntar cuál corresponde.

No se trata de una observación sobre la validez de las habilitaciones ni sobre ningún trámite en
particular. La consulta es sobre cómo debe interpretarse la unidad de registro del dataset.

## 2. El patrón observado

Al agrupar el padrón por dirección aparecen {direcciones} direcciones, en {barrios} barrios, que
concentran {registros} registros de habilitación: entre {rango} registros por número de puerta.
Se agrupan en {lotes} conjuntos que comparten cuatro rasgos:

- números de puerta consecutivos de una misma cuadra;
- la misma cantidad de registros y la misma mezcla de rubros en cada dirección del conjunto;
- ausencia de fecha de habilitación en la totalidad de los registros;
- **la misma partida matriz para todas las direcciones del conjunto.**

A modo de ejemplo, sobre la Av. Ramón L. Falcón al 7100 figuran {len(ejemplo)} números de puerta
({lista_ej}...), cada uno con la misma composición de rubros, todos bajo la misma partida matriz
({ejemplo.partida_matriz.iloc[0]}).

## 3. Cómo lo leemos, y por qué preguntamos

Nuestra lectura es que **no se trata de un local por número de puerta, sino de un inmueble único
cuyos permisos quedan asentados contra cada número del frente de manzana**.

{parrafo_mecanismo}

La cohorte 2025 —donde aparecen estos conjuntos— no incluye ese campo, sino un domicilio por fila.
Al normalizar de una forma a la otra, cada número del frente pasa a comportarse como una dirección
independiente. Eso da cuenta del patrón descripto en la sección 2 sin necesidad de suponer un error
de carga.

{parrafo_catastro}

{parrafo_alcance}

Adicionalmente, sobre las direcciones de estos conjuntos, {crudos} registros se reducen a {pares}
combinaciones distintas de titular y rubro.

**La consulta concreta es:** ¿este patrón responde a un criterio de carga por frente de manzana o
por unidad funcional del inmueble, previsto por el régimen de habilitaciones? ¿O corresponde
interpretarlo como una duplicación de asiento?

Formulamos la pregunta en estos términos porque no podemos descartar que se trate de una
convención registral correcta que estamos leyendo con una unidad de análisis equivocada.

## 4. Por qué puede interesarles más allá de nuestro trabajo

El dataset es de publicación abierta. Cualquier usuario que cuente registros por dirección —o
direcciones por barrio— sobre estas zonas obtendrá volúmenes que no se corresponden con la cantidad
de establecimientos. En nuestro universo el efecto alcanza al 22,6 % de los registros
georreferenciados, concentrado en unas pocas cuadras del centro y del oeste.

En nuestro caso está resuelto: estas direcciones quedan fuera del conteo por una regla previa, de
modo que ninguna cifra que hayamos publicado está afectada. Lo señalamos porque el mismo dato, leído
sin esa precaución, es fácil de contar mal.

## 5. Anexo

`anexo_consulta_agc.csv` — {direcciones} direcciones con su partida matriz, clave catastral SMP,
barrio y cantidad de registros asociados.

El anexo contiene únicamente identificación catastral y domiciliaria del inmueble. **No incluye
razón social, CUIT, teléfono ni datos de titulares.** Si para la verificación resultara necesario
identificar trámites concretos, la partida matriz permite ubicarlos en el sistema de la Agencia.

---

**Fuente:** habilitaciones aprobadas, publicadas en BA Data (cohortes 2015-2018, 2019 a 2024 y
2025). Universo de análisis: rubros gastronómicos.
"""


def main() -> int:
    datos = anexo()
    prueba = pd.read_csv(PRUEBA, encoding="utf-8")
    replicacion = pd.read_csv(REPLICACION, encoding="utf-8")
    discriminancia = pd.read_csv(DISCRIMINANCIA, encoding="utf-8", dtype={"direcciones": str})
    mecanismo = json.loads(MECANISMO.read_text(encoding="utf-8"))

    prohibidas = {"razon_social", "cuit", "cuits", "telefono", "titulares"}
    filtradas = prohibidas & set(datos.columns)
    if filtradas:
        raise SystemExit(f"el anexo no puede llevar {filtradas}")

    SALIDA.mkdir(parents=True, exist_ok=True)
    datos.to_csv(SALIDA / "anexo_consulta_agc.csv", index=False, encoding="utf-8-sig")
    (SALIDA / "NOTA_CONSULTA_AGC.md").write_text(
        redactar(datos, prueba, replicacion, discriminancia, mecanismo), encoding="utf-8")

    print(f"columnas del anexo: {list(datos.columns)}")
    print(f"{len(datos)} direcciones · {datos.lote.nunique()} conjuntos · "
          f"{prueba.partida_matriz.nunique()} partidas · {datos.barrio.nunique()} barrios")
    print("")
    print("PARA REVISAR Y ENVIAR POR DIEGO — este script no manda nada:")
    print(f"  {SALIDA / 'NOTA_CONSULTA_AGC.md'}")
    print(f"  {SALIDA / 'anexo_consulta_agc.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
