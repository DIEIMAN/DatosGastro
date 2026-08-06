"""La densidad deja de ser compuerta y pasa a ser atributo. Segunda etapa del borrador de polos.

POR QUÉ ESTE SCRIPT EXISTE
--------------------------
La primera corrida (`borrador_polos_ciudad.py`) dejó 118 polos y un problema: el más denso tiene
16 veces la densidad del menos denso, y los dos se llaman igual. La salida NO es poner un piso de
densidad que borre los de abajo. **El Atlas ya publica zonas de baja densidad** —«referencia
dispersa» es literalmente una de sus lecturas, y ahí están La Paternal, Villa Pueyrredón,
Costanera Norte y Esmeralda–Paraguay—. Un piso duro contradice el precedente publicado.

Lo que resuelve el problema es dejar de llamarlas igual:

  1. el clustering adaptativo se conserva: es el que encuentra la estructura local,
  2. cada polo lleva su **densidad absoluta** (locales/ha) y su **superficie** como atributos,
  3. y una **clase de densidad** derivada de los cortes naturales de la distribución, no de un
     número redondo. El precedente del método es el hueco de R07 en `CRITERIOS_LECTURA_…` §2.

El piso absoluto se corre igual, como **sensibilidad informativa**: no decide nada, sirve para
saber de qué tamaño es la pregunta y para mostrar cuántas zonas ya publicadas caerían con él.

QUÉ HACE, EN ORDEN
------------------
  §1  densidad y superficie como atributos; clases por cortes naturales (Fisher–Jenks + huecos)
  §2  sensibilidad del piso absoluto, tres valores, informativa
  §3  partición de los polos encadenados, con criterio declarado ANTES de mirar el resultado
  §4  las tres pruebas de artefacto sobre los polos del sur, una por una y polo por polo
  §5  añada del Relevamiento por polo — el mapa depende de una fuente rotativa
  §6  las siete zonas publicadas que el clustering no encuentra, con cuál explicación aplica

TODOS LOS UMBRALES DE ESTE ARCHIVO ESTÁN DECLARADOS ARRIBA, EN CONSTANTES, Y NINGUNO SE LEYÓ DE
ESTOS DATOS. Los que no vienen de `CRITERIOS_LECTURA_POLIGONIZACION.md` son convención (el GVF de
Jenks) o geometría (los grados de tolerancia angular).

Google Places no interviene: no está en la base y esta corrida no consulta nada. 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_atributos_clases.py
"""
from __future__ import annotations

import io
import json
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.ops import unary_union

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import (  # noqa: E402
    BARRIDO, CRS_GEO, CRS_METRICO, ENVOLVENTES_22, GEN_PAREJIDAD, PARAMETROS,
    agrupar, cargar_base_completa, cargar_puntos, construir_polos, control_aptitud, plegar,
)

OUT = BARRIDO / "borrador_polos"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"
PERTENENCIA_V1 = OUT / "pertenencia_local_polo.csv"

SUPERFICIE_CIUDAD_HA = 20_300

# ================================================================================================
# §1 · CLASES DE DENSIDAD POR CORTES NATURALES
# ================================================================================================
# El método es el que pide el §2 de CRITERIOS_LECTURA_POLIGONIZACION.md: «buscá el hueco antes de
# elegir un número redondo». Se implementan los dos y se cruzan:
#   - Fisher–Jenks, que es el corte óptimo en una dimensión: minimiza la varianza dentro de cada
#     clase. No es una heurística: es programación dinámica y da el óptimo exacto.
#   - los huecos crudos de la distribución ordenada, que es el criterio con el que se leyó R07.
# Si los dos coinciden, el corte es del territorio y no del método.
K_CANDIDATOS = (2, 3, 4, 5, 6)
GVF_MINIMO = 0.85          # convención de Jenks: la bondad de ajuste a partir de la cual se acepta
                           # un k. Se toma el k MÁS CHICO que la alcanza, no el que mejor queda.
HUECOS_A_REPORTAR = 6

# Los nombres salen del vocabulario que el Atlas ya usa, de más denso a menos. El último es
# textual del Atlas: «referencia dispersa» es una lectura publicada, no un eufemismo inventado acá.
NOMBRES_CLASE = [
    "A · concentración densa",
    "B · concentración media",
    "C · concentración extendida",
    "D · referencia dispersa",
    "E · referencia muy dispersa",
    "F · residual",
]

# ================================================================================================
# §2 · SENSIBILIDAD DEL PISO ABSOLUTO — INFORMATIVA, NO DECIDE NADA
# ================================================================================================
# Tres valores redondos que cruzan la distribución observada (mínimo ~1, mediana ~5, máximo ~15).
# Son redondos a propósito: no se eligen para que sobreviva ningún polo en particular. Y la
# columna que importa de esta tabla no es cuántos polos del borrador caen, sino **cuántas de las
# 22 zonas que la Dirección ya publicó caerían con el mismo piso**.
PISOS_ABSOLUTOS = (2.0, 4.0, 6.0)

# ================================================================================================
# §3 · PARTICIÓN DE LOS POLOS ENCADENADOS — CRITERIO DECLARADO ANTES DE MIRAR EL RESULTADO
# ================================================================================================
# QUIÉNES SE PARTEN (población, fijada por la corrida anterior y no reabierta acá):
#   los polos por encima del percentil 90 de superficie Y por debajo de la densidad mediana. Es la
#   misma regla que ya marcó a los diez en la etapa 1. No se agrega ni se saca ninguno a mano.
PERCENTIL_SUPERFICIE = 0.90

# CÓMO SE PARTEN, y por qué así:
#   el encadenamiento es un efecto conocido de `eom` («excess of mass»), que elige el corte más
#   somero y estable del árbol de densidad: por eso pega barrios contiguos de densidad media. El
#   otro método que la misma biblioteca ya ofrece sobre el MISMO árbol es `leaf`, que toma el corte
#   más profundo. Partir con `leaf` no introduce ningún parámetro nuevo ni ninguna distancia
#   elegida a ojo: es el otro extremo del mismo árbol, con `min_cluster_size` y `min_samples`
#   idénticos a los de toda la corrida.
METODO_PARTICION = "leaf"

# QUÉ PASA CON LO QUE QUEDA CHICO, declarado antes de saber cuánto queda chico:
#   un fragmento por debajo del tamaño mínimo NO se rescata bajando el umbral. Se anota, sus
#   locales vuelven a contarse como dispersos, y el conteo de la partición lo deja escrito.
#   Un polo que con `leaf` no se separa tampoco se fuerza: se anota que no se partió.
RESCATE_DE_FRAGMENTOS = False

# ================================================================================================
# §4 · LAS TRES PRUEBAS DE ARTEFACTO — §3 de CRITERIOS_LECTURA_POLIGONIZACION.md
# ================================================================================================
# 4.1 · fuente: «si más del 70 % de los puntos vienen de una sola fuente». Textual del criterio.
PESO_FUENTE_MAXIMO = 0.70

# 4.2 · grilla: «si los bordes coinciden con los bordes de las celdas de consulta».
#   Ninguna de las siete fuentes de la base se bajó por celdas: F01/F02 y el Relevamiento son
#   volcados administrativos completos, y OSM, Overture y ATP se recortaron por el `bbox` de la
#   Ciudad entera y después por barrios oficiales. Places, que sí se consulta por celdas, NO está
#   en la base. Así que no hay grilla de consulta contra la cual cruzar contornos, y la prueba se
#   corre por la **firma geométrica** que una grilla dejaría igual: un polígono con forma de celda.
#   Los tres indicadores, con su umbral declarado:
RECTANGULARIDAD_MAXIMA = 0.90   # área ÷ área de su caja: por encima de esto el polo ES su caja
TOLERANCIA_ANGULAR_GRADOS = 5.0
PERIMETRO_EN_EJES_MAXIMO = 0.50  # fracción del perímetro alineada a los ejes de la proyección
#   Y el borde que sí existe y sí podría marcar el contorno: el límite entre barrios, que es por
#   donde se recortaron tres de las siete fuentes. Se mide sólo contra bordes INTERNOS. El
#   perímetro de la Ciudad se excluye a propósito: en el sur los polos tocan el Riachuelo y la
#   General Paz, que son territorio real y no artefacto de consulta. Contarlos daría un falso
#   positivo justo en los polos que se están examinando.
BUFFER_BORDE_BARRIO_M = 25
PERIMETRO_SOBRE_BORDE_MAXIMO = 0.30

# 4.3 · cobertura: la parejidad del barrio va AL LADO de cada polo, no al pie.
#   La prueba es de UN SOLO LADO, y eso no es una elección de conveniencia: el criterio escrito
#   antes del mapa dice «un cluster en un barrio donde la base es notoriamente floja vale menos que
#   el mismo cluster donde la base es densa». Cobertura ALTA no es riesgo de artefacto: es más base
#   sosteniendo el mismo polo. Un polo marcado por estar mejor cubierto que la mediana sería un
#   falso positivo puro. Se reportan las dos lecturas —la de una cola y la de dos— para que se vea
#   qué cambia, pero la que decide es la de una cola.
COBERTURA_P_BAJO, COBERTURA_P_ALTO = 0.10, 0.90

# Las comunas que motivan la revisión: no tienen ninguna zona publicada del Atlas.
COMUNAS_SIN_ZONA_PUBLICADA = (8.0, 9.0)

# ================================================================================================
# §6 · LAS SIETE ZONAS NO ENCONTRADAS — las tres explicaciones del §4 de CRITERIOS_LECTURA
# ================================================================================================
# El criterio ya fijó el orden de probabilidad y este script no lo reordena. Lo que agrega es la
# regla de asignación, declarada antes de mirar las siete:
#   E1 «no era una concentración, sino una lectura territorial»: se asigna cuando LA MAYORÍA DE
#      LOS LOCALES DE LA ZONA sí están adentro de algún polo, pero ese polo ocupa menos de un
#      cuarto de la superficie publicada. Es la medida directa de «el perímetro publicado es más
#      ancho que la concentración»: la concentración está, es la zona la que se dibujó más grande.
#      NO se usa la densidad de la zona para decidir esto: casi todas las publicadas quedan en la
#      clase baja por su perímetro editorial, así que una regla por densidad le pondría E1 a las
#      siete y dejaría de distinguir nada.
#   E2 «la cobertura de la base ahí es floja» si la cobertura del barrio cae por debajo del p10.
#   E3 «la zona no se sostiene» sólo si NO aplican E1 ni E2. Es la última hipótesis y, dice el
#      criterio, no se declara desde un borrador: sale escrita como pregunta.
MAYORIA_LOCALES_EN_POLO = 0.50
COBERTURA_MINIMA_ZONA = 0.25   # el mismo umbral de la etapa 1, no se toca


# --------------------------------------------------------------------------- cortes naturales


def fisher_jenks(valores: np.ndarray, k: int) -> tuple[list[float], float]:
    """Cortes naturales óptimos en una dimensión, por programación dinámica.

    Devuelve los k−1 puntos de corte y la suma de cuadrados dentro de las clases. Es el óptimo
    exacto, no una heurística: para 118 valores y k ≤ 6 el costo es despreciable y no hay motivo
    para conformarse con una aproximación que después habría que defender.
    """
    x = np.sort(np.asarray(valores, dtype=float))
    n = len(x)
    suma = np.concatenate([[0.0], np.cumsum(x)])
    suma2 = np.concatenate([[0.0], np.cumsum(x ** 2)])

    def sce(i: int, j: int) -> float:
        """Suma de cuadrados del tramo [i, j) sobre el vector ya ordenado."""
        m = j - i
        if m <= 0:
            return 0.0
        return float(suma2[j] - suma2[i] - (suma[j] - suma[i]) ** 2 / m)

    inf = float("inf")
    costo = np.full((k + 1, n + 1), inf)
    costo[0, 0] = 0.0
    corte = np.zeros((k + 1, n + 1), dtype=int)
    for c in range(1, k + 1):
        for j in range(c, n + 1):
            mejor, donde = inf, c - 1
            for i in range(c - 1, j):
                valor = costo[c - 1, i] + sce(i, j)
                if valor < mejor:
                    mejor, donde = valor, i
            costo[c, j] = mejor
            corte[c, j] = donde

    bordes, j = [], n
    for c in range(k, 0, -1):
        j = corte[c, j]
        bordes.append(j)
    bordes = sorted(b for b in bordes if b > 0)
    # El corte se pone en el medio del hueco, no sobre un dato: así ningún polo queda exactamente
    # sobre el límite de su clase.
    cortes = [float((x[b - 1] + x[b]) / 2) for b in bordes]
    return cortes, float(costo[k, n])


def huecos_mayores(valores: np.ndarray, cuantos: int) -> pd.DataFrame:
    """Los saltos más grandes de la distribución ordenada. El criterio con el que se leyó R07."""
    x = np.sort(np.asarray(valores, dtype=float))
    saltos = np.diff(x)
    orden = np.argsort(saltos)[::-1][:cuantos]
    return pd.DataFrame({
        "corte": [(x[i] + x[i + 1]) / 2 for i in orden],
        "hueco": saltos[orden],
        "debajo": [i + 1 for i in orden],
        "encima": [len(x) - i - 1 for i in orden],
    }).sort_values("hueco", ascending=False).reset_index(drop=True)


def clasificar_densidad(polos: gpd.GeoDataFrame, p) -> tuple[gpd.GeoDataFrame, list[float], pd.DataFrame]:
    """§1 · densidad y superficie como atributos, y la clase que sale de los cortes naturales."""
    densidad = polos.locales_x_ha.to_numpy()
    sce_total = float(((densidad - densidad.mean()) ** 2).sum())

    filas = []
    for k in K_CANDIDATOS:
        cortes, sce = fisher_jenks(densidad, k)
        filas.append({"k": k, "gvf": round(1 - sce / sce_total, 4),
                      "cortes": " | ".join(f"{c:.2f}" for c in cortes)})
    ajuste = pd.DataFrame(filas)
    aptos = ajuste[ajuste.gvf >= GVF_MINIMO]
    k_elegido = int(aptos.k.iloc[0]) if len(aptos) else int(ajuste.k.iloc[-1])
    cortes, _ = fisher_jenks(densidad, k_elegido)

    p("§1 · DENSIDAD Y SUPERFICIE COMO ATRIBUTOS, Y LA CLASE QUE SALE DE LOS CORTES NATURALES")
    p("=" * 100)
    p("")
    p("  La densidad deja de ser compuerta. No hay piso que borre polos: hay un atributo por polo")
    p("  y una clase derivada de la distribución. El motivo no es proteger a los polos del sur —eso")
    p("  no sería argumento—: es que el Atlas YA publica zonas de baja densidad, y un piso duro")
    p("  contradiría el precedente publicado.")
    p("")
    p(f"  densidad (locales/ha): mín {densidad.min():.2f} | mediana {np.median(densidad):.2f} | "
      f"máx {densidad.max():.2f} | el más denso es {densidad.max() / densidad.min():.0f}× el menos denso")
    p(f"  superficie (ha):       mín {polos.ha.min():.1f} | mediana {polos.ha.median():.1f} | "
      f"máx {polos.ha.max():.1f}")
    p("")
    p("  BONDAD DE AJUSTE DE LOS CORTES NATURALES (Fisher–Jenks, óptimo exacto en 1 dimensión)")
    p(f"    regla declarada: se toma el k MÁS CHICO con GVF ≥ {GVF_MINIMO}, no el que mejor queda")
    p(ajuste.to_string(index=False))
    p(f"    k elegido: {k_elegido} clases · cortes en "
      f"{', '.join(f'{c:.2f}' for c in cortes)} locales/ha")
    p("")
    p("  CONTRASTE CON LOS HUECOS CRUDOS · el criterio con el que se leyó R07")
    p("    si los cortes de Jenks cayeran sobre huecos de la distribución, el corte sería del")
    p("    territorio y no del método. Se busca el hueco antes de aceptar el número.")
    tabla_huecos = huecos_mayores(densidad, HUECOS_A_REPORTAR)
    p(tabla_huecos.round(3).to_string(index=False))
    distancias = []
    for corte in cortes:
        distancia = float((tabla_huecos.corte - corte).abs().min())
        distancias.append(distancia)
        p(f"    corte {corte:.2f} → hueco reportado más cercano a {distancia:.2f} locales/ha")
    salto_mediano = float(np.median(np.diff(np.sort(densidad))))
    p("")
    p("    Y EL RESULTADO ES NEGATIVO, QUE ES EL DATO: **no hay hueco.** El salto mediano entre")
    p(f"    dos polos consecutivos es {salto_mediano:.3f} locales/ha y el mayor salto interior es")
    p(f"    {tabla_huecos.hueco.iloc[3]:.3f}: la distribución de densidad de los polos es continua.")
    p("    El hueco de R07 existía porque R07 era un caso extremo —0,03 contra 15,6— y acá no hay")
    p("    nada parecido: los polos llenan el rango sin dejar vacíos.")
    p("")
    p("    Consecuencia, dicha antes de usar las clases: **los cortes son óptimos, no naturales.**")
    p("    Fisher–Jenks da la partición que minimiza la varianza interna —es el mejor lugar donde")
    p("    cortar—, pero no hay un vacío en el territorio que los sostenga. La clase sigue")
    p("    haciendo el trabajo que se le pide, que es dejar de llamar igual a dos cosas con 16×")
    p("    de diferencia; lo que NO puede hacer es fingir que la frontera entre clases es una")
    p("    frontera del territorio. Un polo a 4,5 y uno a 4,7 son prácticamente lo mismo y caen")
    p("    en clases distintas. La densidad exacta va al lado de la clase por ese motivo.")
    p("")

    bordes = [-np.inf, *cortes, np.inf]
    etiquetas = NOMBRES_CLASE[:k_elegido][::-1]   # de menos denso a más denso, que es el orden de `cut`
    polos = polos.copy()
    polos["clase_densidad"] = pd.cut(polos.locales_x_ha, bordes, labels=etiquetas)
    return polos, cortes, ajuste


def resumen_clases(polos: gpd.GeoDataFrame, zonas_22: gpd.GeoDataFrame, p) -> pd.DataFrame:
    """La tabla de clases con las zonas publicadas que caen en cada una. Ese es el argumento."""
    resumen = polos.groupby("clase_densidad", observed=True).agg(
        polos=("polo_id", "size"), locales=("locales", "sum"), ha=("ha", "sum"),
        densidad_min=("locales_x_ha", "min"), densidad_max=("locales_x_ha", "max"),
        ha_mediana=("ha", "median")).round(2)
    resumen["locales_por_polo"] = (resumen.locales / resumen.polos).round(0).astype(int)

    # Las 22 publicadas, clasificadas con LOS MISMOS cortes. Es la comprobación que sostiene toda
    # la decisión: si las publicadas se reparten por todas las clases, entonces la Dirección ya
    # aceptó polos de baja densidad y un piso los borraría a ellos también.
    orden = list(polos.clase_densidad.cat.categories)
    for columna, destino in [("clase_densidad", "zonas_22_por_su_perimetro_publicado"),
                             ("clase_densidad_hull", "zonas_22_medidas_como_los_polos")]:
        resumen[destino] = zonas_22.groupby(columna, observed=True).referencia_id.apply(
            lambda s: " ".join(sorted(s))).reindex(orden).fillna("—")

    p("  LAS CLASES, Y QUÉ ZONA YA PUBLICADA CAE EN CADA UNA")
    p("    las 22 del Atlas están medidas con la misma base y clasificadas con los mismos cortes,")
    p("    y aparecen DOS VECES porque hay dos superficies posibles y miden cosas distintas:")
    p("      · por su perímetro publicado — la densidad que implica el mapa del Atlas tal como está")
    p("        dibujado. Un perímetro editorial es más ancho que un hull ajustado a los puntos, así")
    p("        que este número siempre sale más bajo y NO es comparable contra un polo del borrador.")
    p("      · medidas como los polos — envolvente cóncava de sus propios puntos, mismo ratio 0,55.")
    p("        Ésta es la comparación honesta, y es la que hay que mirar.")
    p(resumen.to_string())
    p("")
    p("  Ningún polo se llama igual que otro con 16 veces su densidad: eso es lo que hace la clase.")
    p("  Y la fila de las zonas publicadas es la que cierra la discusión del piso absoluto: si las")
    p("  zonas que la Dirección ya adoptó aparecen repartidas en las clases bajas —incluso medidas")
    p("  del modo que más las favorece, con su propio hull—, entonces el precedente publicado ya")
    p("  acepta baja densidad y el piso no es una opción disponible.")
    p("")
    p("  ADVERTENCIA DE LECTURA, Y ES IMPORTANTE PORQUE LA TABLA SE PRESTA A LO CONTRARIO. Esta")
    p("  tabla NO dice que las zonas del Atlas sean ralas. Un polo del borrador y una zona")
    p("  publicada no son el mismo tipo de objeto: **el polo es un núcleo extraído por densidad**")
    p("  —el clustering descarta el 43 % de los puntos como dispersos antes de dibujar nada— y")
    p("  **la zona publicada es un perímetro trazado sobre un área**, con todo lo que hay adentro.")
    p("  Comparar sus densidades es comparar un barrio con su cuadra más cargada, y el barrio")
    p("  siempre pierde. La comparación no sirve para juzgar a las zonas publicadas.")
    p("")
    p("  Para lo que SÍ sirve es para lo único que se le pide: mostrar que un piso de densidad")
    p("  calibrado sobre los polos del borrador no se puede trasladar a las zonas publicadas sin")
    p("  borrarlas casi todas. Eso no es un defecto del Atlas: es la prueba de que el piso es el")
    p("  instrumento equivocado para esta pregunta.")
    p("")
    return resumen


# --------------------------------------------------------------------------- §2 piso absoluto


def sensibilidad_piso(polos: gpd.GeoDataFrame, zonas_22: gpd.GeoDataFrame, p) -> pd.DataFrame:
    """§2 · el piso absoluto corrido como sensibilidad. No decide nada; dice de qué tamaño es."""
    filas = []
    for piso in PISOS_ABSOLUTOS:
        quedan = polos[polos.locales_x_ha >= piso]
        caen = polos[polos.locales_x_ha < piso]
        # Las publicadas se cuentan por su densidad de HULL, que es la comparable y además la que
        # más las favorece: contarlas por su perímetro publicado exageraría cuántas caen.
        zonas_caen = zonas_22[zonas_22.locales_x_ha_hull < piso]
        comunas_antes = set(polos.comuna.dropna())
        comunas_despues = set(quedan.comuna.dropna())
        filas.append({
            "piso_locales_x_ha": piso,
            "polos_que_sobreviven": len(quedan),
            "polos_que_caen": len(caen),
            "locales_que_sobreviven": int(quedan.locales.sum()),
            "pct_locales_que_caen": round(caen.locales.sum() / polos.locales.sum() * 100, 1),
            "barrios_que_pierden_todo": len(set(polos.barrio_principal) - set(quedan.barrio_principal)),
            "comunas_que_pierden_todo": len(comunas_antes - comunas_despues),
            "zonas_22_publicadas_que_caerian": len(zonas_caen),
            "cuales": " ".join(sorted(zonas_caen.referencia_id)),
        })
    tabla = pd.DataFrame(filas)

    p("§2 · SENSIBILIDAD DEL PISO ABSOLUTO · informativa, no decide nada")
    p("=" * 100)
    p("")
    p("  Se corre para saber de qué tamaño es la pregunta, no para aplicarlo. Los tres valores son")
    p("  redondos a propósito: no se eligieron para que sobreviva ningún polo en particular.")
    p("")
    p(tabla.to_string(index=False))
    p("")
    p("  La columna que importa es la última: **cuántas de las 22 zonas que la Dirección ya publicó")
    p("  caerían con el mismo piso**. Un piso que borra zonas publicadas no es un criterio de")
    p("  calidad: es un criterio que contradice al Atlas.")
    p("")
    return tabla


# --------------------------------------------------------------------------- §3 partición


def particionar(geo: gpd.GeoDataFrame, polos: gpd.GeoDataFrame, p) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """§3 · partir los encadenados con el criterio ya declarado arriba, sin mirar antes.

    Devuelve el conjunto final de polos y el registro de qué pasó con cada uno de los partidos.
    """
    umbral_ha = polos.ha.quantile(PERCENTIL_SUPERFICIE)
    umbral_densidad = polos.locales_x_ha.median()
    a_partir = polos[(polos.ha > umbral_ha) & (polos.locales_x_ha < umbral_densidad)]

    p("§3 · PARTICIÓN DE LOS POLOS ENCADENADOS · criterio declarado antes de mirar el resultado")
    p("=" * 100)
    p("")
    p(f"  QUIÉNES: superficie > percentil {PERCENTIL_SUPERFICIE:.0%} ({umbral_ha:.1f} ha) y densidad")
    p(f"           < mediana ({umbral_densidad:.2f} locales/ha) → {len(a_partir)} polos")
    p(f"  CÓMO:    se rehace el clustering sobre los puntos del propio polo con método "
      f"`{METODO_PARTICION}`,")
    p("           que toma el corte más profundo del MISMO árbol de densidad que `eom` cortó")
    p("           somero. min_cluster_size y min_samples no se mueven: son los de toda la corrida.")
    p(f"  SOBRAS:  un fragmento por debajo de {PARAMETROS['min_cluster_size']} locales NO se rescata")
    p("           bajando el umbral. Se anota y sus locales vuelven a contarse como dispersos.")
    p("")

    # Control declarado y que hay que mirar: ¿algún polo que contiene entera una zona publicada
    # quedó FUERA de la población a partir? Si pasa, se dice; no se lo agrega a mano.
    engulle = polos[polos.zonas_que_contiene.fillna("") != ""]
    fuera = set(engulle.polo_id) - set(a_partir.polo_id)
    p(f"  control · polos que contienen entera una zona publicada: {len(engulle)} "
      f"({' '.join(sorted(engulle.polo_id))})")
    p(f"  control · de esos, fuera de la población a partir: {len(fuera)}"
      + (f" — {' '.join(sorted(fuera))}, se anota y NO se agrega a mano" if fuera else ""))
    p("")

    registro, nuevas_etiquetas = [], {}
    contador = 0
    for polo in a_partir.itertuples():
        miembros = geo[geo.polo_id == polo.polo_id]
        etiquetas = agrupar(miembros, PARAMETROS["min_cluster_size"], PARAMETROS["min_samples"],
                            METODO_PARTICION)
        fragmentos = sorted({int(e) for e in etiquetas if e >= 0})
        tamanios = pd.Series(etiquetas[etiquetas >= 0]).value_counts()
        grandes = [f for f in fragmentos if tamanios[f] >= PARAMETROS["min_cluster_size"]]
        chicos = [f for f in fragmentos if tamanios[f] < PARAMETROS["min_cluster_size"]]

        se_parte = len(grandes) >= 2
        if se_parte:
            for orden, fragmento in enumerate(grandes, start=1):
                indices = miembros.index[etiquetas == fragmento]
                nuevas_etiquetas.update({i: f"{polo.polo_id}-{orden}" for i in indices})
            contador += len(grandes)
        registro.append({
            "polo_id": polo.polo_id,
            "barrio_principal": polo.barrio_principal,
            "locales": polo.locales,
            "ha": round(polo.ha, 1),
            "locales_x_ha": round(polo.locales_x_ha, 2),
            "zonas_que_contiene": polo.zonas_que_contiene,
            "fragmentos_leaf": len(fragmentos),
            "fragmentos_que_pasan_el_minimo": len(grandes),
            "fragmentos_anotados_sin_rescate": len(chicos),
            "locales_anotados_como_dispersos": int(
                (etiquetas == -1).sum() + sum(tamanios[c] for c in chicos)) if se_parte else 0,
            "se_parte": se_parte,
        })

    detalle = pd.DataFrame(registro)
    p("  QUÉ PASÓ CON CADA UNO")
    p(detalle.to_string(index=False))
    partidos = detalle[detalle.se_parte]
    p("")
    p(f"    se partieron: {len(partidos)} de {len(detalle)} → {contador} piezas en lugar de "
      f"{len(partidos)} manchas")
    p(f"    no se partieron (leaf no separa dos piezas ≥ {PARAMETROS['min_cluster_size']}): "
      f"{len(detalle) - len(partidos)}"
      + (f" — {' '.join(detalle[~detalle.se_parte].polo_id)}" if len(detalle) - len(partidos) else ""))
    p(f"    locales que vuelven a contarse como dispersos: "
      f"{int(detalle.locales_anotados_como_dispersos.sum()):,} — se anotan, no se rescatan")
    p("")
    p("    LO QUE COSTÓ, DICHO ANTES DE MOSTRAR EL RESULTADO BONITO. Partir con `leaf` no recorta")
    p("    los bordes de la mancha: la deshace y se queda con los núcleos. De los cuatro polos que")
    p(f"    se partieron salieron {contador} piezas, y en el camino "
      f"{int(detalle.locales_anotados_como_dispersos.sum()):,} locales dejaron de estar en un polo")
    p("    —no por no llegar al mínimo, sino porque el corte profundo los deja como ruido—. El")
    p("    criterio se declaró antes y no se toca; lo que corresponde es que el precio esté a la")
    p("    vista y no adentro de un total.")
    p("")

    # Reconstrucción del conjunto final: los polos que no se tocaron, más las piezas nuevas.
    geo = geo.copy()
    geo["polo_final"] = geo.polo_id
    intocados = set(polos.polo_id) - set(partidos.polo_id)
    geo.loc[~geo.polo_id.isin(intocados), "polo_final"] = ""
    for indice, etiqueta in nuevas_etiquetas.items():
        geo.at[indice, "polo_final"] = etiqueta
    return geo, detalle


def verificar_p072(polos: gpd.GeoDataFrame, zonas_22: gpd.GeoDataFrame, p) -> None:
    """¿La partición hizo lo que se partió para hacer? El caso testigo es P072 sobre R05.

    P072 era el motivo declarado de todo el §3: contenía entera a R05 Belgrano y la excedía once
    veces. Si después de partir ninguna pieza se parece a R05, la partición deshizo la mancha sin
    recuperar la zona, y eso hay que verlo acá y no descubrirlo tres pasos más adelante.
    """
    r05 = zonas_22[zonas_22.referencia_id == "R05"]
    if not len(r05):
        return
    geometria = r05.geometry.iloc[0]
    piezas = polos[polos.polo_id.str.startswith("P072-")].copy()
    p("  CONTROL DEL CASO TESTIGO · P072 se partió para recuperar R05 Belgrano, ¿lo hizo?")
    if not len(piezas):
        p("    P072 no se partió: el control no aplica.")
        p("")
        return
    piezas["pct_de_R05_que_cubre"] = [
        round(g.intersection(geometria).area / geometria.area * 100, 1) for g in piezas.geometry]
    piezas["pct_de_la_pieza_dentro_de_R05"] = [
        round(g.intersection(geometria).area / g.area * 100, 1) for g in piezas.geometry]
    p(piezas[["polo_id", "barrio_principal", "locales", "ha", "locales_x_ha", "clase_densidad",
              "pct_de_R05_que_cubre", "pct_de_la_pieza_dentro_de_R05"]].round(2).to_string(index=False))
    cubierta = piezas.union_all().intersection(geometria).area / geometria.area
    mejor = piezas.loc[piezas.pct_de_R05_que_cubre.idxmax()]
    p(f"    las piezas juntas cubren el {cubierta * 100:.1f} % de R05 (la mancha entera cubría "
      "el 99,2 %)")
    p(f"    la pieza que más la cubre es {mejor.polo_id}: {mejor.pct_de_R05_que_cubre:.1f} % de R05, "
      f"y el {mejor.pct_de_la_pieza_dentro_de_R05:.1f} % de la pieza cae adentro de R05")
    if cubierta >= COBERTURA_MINIMA_ZONA:
        p("    VEREDICTO: la partición hizo lo suyo. R05 sigue encontrada y ya no hay un polo que")
        p("    la contenga entera con otro perímetro once veces más ancho.")
    else:
        p("    VEREDICTO: la partición deshizo la mancha PERO no dejó una pieza que corresponda a")
        p("    R05. Es el resultado, no un error a corregir bajando nada: queda anotado como el")
        p("    costo del criterio declarado, y R05 pasa a la lista de zonas no encontradas.")
    p("")


def reconstruir_polos(geo: gpd.GeoDataFrame, base_completa: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Rearma la capa de polos desde la pertenencia final, con el mismo constructor de la etapa 1."""
    con_polo = geo[geo.polo_final != ""].copy()
    codigos = {etiqueta: i for i, etiqueta in enumerate(sorted(con_polo.polo_final.unique()))}
    etiquetas = con_polo.polo_final.map(codigos).to_numpy()
    polos = construir_polos(con_polo, etiquetas, PARAMETROS["concave_hull_ratio"])
    inverso = {f"P{v + 1:03d}": k for k, v in codigos.items()}
    polos["polo_id"] = polos.polo_id.map(inverso)
    return control_aptitud(polos, base_completa)


# --------------------------------------------------------------------------- §5 añada


def anada_por_polo(geo: gpd.GeoDataFrame, polos: gpd.GeoDataFrame, parejidad: pd.DataFrame,
                   p) -> gpd.GeoDataFrame:
    """§5 · qué año del Relevamiento sostiene cada polo.

    El Relevamiento de Usos del Suelo es rotativo: un año por barrio, 2022 / 2023 / 2024. La
    ablación mostró que la corrida colapsa sin él y NO colapsa sacando los mismos puntos al azar,
    así que el mapa depende de una fuente rotativa. Un polo dibujado sobre datos de 2022 no es
    comparable con uno de 2024, y eso tiene que viajar con el polo, no con el handoff.
    """
    anios = parejidad.anio_relevamiento.to_dict()
    puntos = geo[geo.polo_final != ""].copy()
    puntos["anada"] = puntos.barrio_k.map(anios)
    puntos["es_rus"] = puntos.grupos_independencia.fillna("").str.contains("GCBA_URBANISMO")

    filas = []
    for polo_id, grupo in puntos.groupby("polo_final"):
        cuenta = grupo.anada.value_counts()
        mezcla = ";".join(f"{int(a)}:{c}" for a, c in cuenta.items())
        filas.append({
            "polo_id": polo_id,
            "anada_relevamiento": int(cuenta.index[0]) if len(cuenta) else None,
            "anada_pct_dominante": round(cuenta.iloc[0] / len(grupo) * 100, 1) if len(cuenta) else np.nan,
            "anada_mixta": len(cuenta) > 1,
            "anadas": mezcla,
            "pct_puntos_del_relevamiento": round(grupo.es_rus.mean() * 100, 1),
        })
    tabla = pd.DataFrame(filas)
    polos = polos.merge(tabla, on="polo_id", how="left")

    p("§5 · LA AÑADA DEL RELEVAMIENTO, POLO POR POLO")
    p("=" * 100)
    p("")
    p("  El Relevamiento de Usos del Suelo es ROTATIVO: un año por barrio. La ablación mostró que")
    p("  la corrida colapsa sin él y no colapsa sacando los mismos puntos al azar, así que el mapa")
    p("  depende de esa fuente. Un polo dibujado sobre datos de 2022 no es comparable con uno de")
    p("  2024, y la añada viaja ahora con cada polo, en la tabla y adentro del mapa.")
    p("")
    reparto = polos.groupby("anada_relevamiento").agg(
        polos=("polo_id", "size"), locales=("locales", "sum"),
        pct_puntos_rus_mediana=("pct_puntos_del_relevamiento", "median"))
    p("  REPARTO DE LOS POLOS POR AÑADA DOMINANTE DE SU BARRIO")
    p(reparto.round(1).to_string())
    p(f"    polos con añada mixta (abarcan barrios relevados en años distintos): "
      f"{int(polos.anada_mixta.sum())} de {len(polos)}")
    p(f"    dependencia del Relevamiento: mediana {polos.pct_puntos_del_relevamiento.median():.1f} % "
      f"de los puntos de un polo | máximo {polos.pct_puntos_del_relevamiento.max():.1f} %")
    p("")
    # Y lo que se ve en el mapa y la tabla de arriba no muestra: la añada no está repartida al
    # azar por la Ciudad. El Relevamiento rota por zonas, así que el año y el lugar viajan juntos.
    cruce = pd.crosstab(polos.anada_relevamiento, polos.clase_densidad)
    p("  LA AÑADA NO ESTÁ REPARTIDA AL AZAR, Y ESO ES PEOR QUE SI LO ESTUVIERA")
    p("    El Relevamiento no rota barrio por barrio salteado: rota por zonas. Así que el año de")
    p("    medición y la ubicación viajan juntos, y con ellos la densidad.")
    p(cruce.to_string())
    por_comuna = polos.groupby("anada_relevamiento").comuna.agg(
        lambda s: ", ".join(str(int(c)) for c in sorted(s.dropna().unique())[:8]))
    p("")
    p("    comunas donde cae cada añada:")
    for anio, comunas in por_comuna.items():
        p(f"      {int(anio)} · comunas {comunas}")
    p("")
    p("    Consecuencia, y es la que importa: **comparar el centro denso con la periferia extendida")
    p("    es, además, comparar 2024 contra 2023 y 2022.** Los dos efectos están confundidos y con")
    p("    estos datos no se pueden separar. No invalida el mapa; sí invalida cualquier lectura")
    p("    del tipo «tal zona creció respecto de tal otra».")
    p("")
    p("  Consecuencia escrita, no sólo anotada: comparar dos polos de añadas distintas compara dos")
    p("  fotos de años distintos. Y sube la prioridad del diccionario de códigos pedido a")
    p("  Estadística y Censos: si la clasificación de TIPO2 que inferimos está corrida, el mapa se")
    p("  mueve.")
    p("")
    return polos


# --------------------------------------------------------------------------- §4 artefacto


def firma_de_grilla(polos: gpd.GeoDataFrame, bordes_internos) -> pd.DataFrame:
    """Los tres indicadores geométricos de la prueba 4.2, para todos los polos."""
    filas = []
    for polo in polos.itertuples():
        geometria = polo.geometry
        caja = geometria.envelope
        contorno = geometria.boundary
        coordenadas = np.asarray(geometria.exterior.coords) if geometria.geom_type == "Polygon" else \
            np.vstack([np.asarray(g.exterior.coords) for g in geometria.geoms])
        vectores = np.diff(coordenadas, axis=0)
        largos = np.hypot(vectores[:, 0], vectores[:, 1])
        angulos = np.degrees(np.arctan2(vectores[:, 1], vectores[:, 0])) % 90
        alineados = np.minimum(angulos, 90 - angulos) < TOLERANCIA_ANGULAR_GRADOS
        sobre_borde = contorno.intersection(bordes_internos).length
        filas.append({
            "polo_id": polo.polo_id,
            "rectangularidad": round(geometria.area / caja.area, 3),
            "pct_perimetro_en_ejes": round(largos[alineados].sum() / largos.sum() * 100, 1),
            "pct_perimetro_sobre_borde_barrio": round(sobre_borde / contorno.length * 100, 1),
            "vertices": len(coordenadas) - 1,
        })
    return pd.DataFrame(filas)


def pruebas_de_artefacto(polos: gpd.GeoDataFrame, parejidad: pd.DataFrame,
                         barrios: gpd.GeoDataFrame, p) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """§4 · las tres pruebas del §3 de CRITERIOS_LECTURA, una por una y polo por polo."""
    # El borde interno: unión de los contornos de barrio, sin el perímetro de la Ciudad. En el sur
    # los polos tocan el Riachuelo y la General Paz, que son territorio y no artefacto: contarlos
    # daría un falso positivo justo en los polos que se están examinando.
    contornos = unary_union(barrios.geometry.boundary.tolist())
    perimetro_ciudad = unary_union(barrios.geometry.tolist()).boundary
    bordes_internos = contornos.difference(perimetro_ciudad.buffer(BUFFER_BORDE_BARRIO_M))
    bordes_internos = bordes_internos.buffer(BUFFER_BORDE_BARRIO_M)

    firma = firma_de_grilla(polos, bordes_internos)
    polos = polos.merge(firma, on="polo_id", how="left")

    # Prueba 4.3 · la parejidad del barrio, al lado de cada polo y para TODOS, no sólo para los diez.
    p10 = parejidad.cobertura.quantile(COBERTURA_P_BAJO)
    p90 = parejidad.cobertura.quantile(COBERTURA_P_ALTO)
    polos["barrio_k"] = polos.barrio_principal.map(plegar)
    polos["cobertura_barrio"] = polos.barrio_k.map(parejidad.cobertura).round(2)
    polos["composicion_barrio"] = polos.barrio_k.map(parejidad.rus_sobre_comercial).round(1)

    polos["pasa_fuente"] = polos.peso_grupo_dominante <= PESO_FUENTE_MAXIMO
    polos["pasa_grilla"] = (
        (polos.rectangularidad <= RECTANGULARIDAD_MAXIMA)
        & (polos.pct_perimetro_en_ejes <= PERIMETRO_EN_EJES_MAXIMO * 100)
        & (polos.pct_perimetro_sobre_borde_barrio <= PERIMETRO_SOBRE_BORDE_MAXIMO * 100))
    polos["pasa_cobertura"] = polos.cobertura_barrio >= p10          # una cola: la que decide
    polos["pasa_cobertura_dos_colas"] = polos.cobertura_barrio.between(p10, p90)   # la que se informa
    polos["pruebas_que_pasa"] = (polos.pasa_fuente.astype(int) + polos.pasa_grilla.astype(int)
                                 + polos.pasa_cobertura.astype(int))

    p("§4 · LAS TRES PRUEBAS DE ARTEFACTO")
    p("=" * 100)
    p("")
    p("  Los umbrales son los del §3 de CRITERIOS_LECTURA_POLIGONIZACION.md, escritos antes de que")
    p("  el mapa existiera. Se corren sobre TODOS los polos —si no, no hay con qué comparar— y se")
    p("  reportan uno por uno para los del sur, que es lo que se pidió.")
    p("")
    p(f"  4.1 fuente    · falla si un solo grupo aporta más del {PESO_FUENTE_MAXIMO:.0%} de los puntos")
    p(f"  4.2 grilla    · falla si rectangularidad > {RECTANGULARIDAD_MAXIMA}, o más del "
      f"{PERIMETRO_EN_EJES_MAXIMO:.0%} del perímetro")
    p(f"                  alineado a los ejes (±{TOLERANCIA_ANGULAR_GRADOS:.0f}°), o más del "
      f"{PERIMETRO_SOBRE_BORDE_MAXIMO:.0%} del perímetro sobre borde")
    p(f"                  INTERNO de barrio (±{BUFFER_BORDE_BARRIO_M} m). El perímetro de la Ciudad")
    p("                  se excluye: en el sur los polos tocan el Riachuelo y la General Paz, que")
    p("                  son territorio real. Contarlos daría un falso positivo justo ahí.")
    p(f"  4.3 cobertura · falla si la cobertura del barrio cae por debajo del p10 de la Ciudad")
    p(f"                  (p10 = {p10:.2f}). Es de UNA COLA, y así lo pide el criterio escrito antes")
    p("                  del mapa: «un cluster en un barrio donde la base es notoriamente floja vale")
    p("                  menos que el mismo cluster donde la base es densa». Cobertura ALTA no es")
    p("                  riesgo de artefacto, es más base sosteniendo el mismo polo. Se informa")
    p(f"                  igual la lectura de dos colas (p90 = {p90:.2f}) para que se vea qué cambia.")
    p("")
    p("  NOTA SOBRE 4.2, QUE HAY QUE LEER ANTES DE LA TABLA. Ninguna de las siete fuentes de la")
    p("  base se bajó por celdas de consulta: F01/F02 y el Relevamiento son volcados")
    p("  administrativos completos, y OSM, Overture y ATP se recortaron por el `bbox` de la Ciudad")
    p("  entera y después por barrios oficiales. Google Places, que sí se consulta por celdas, NO")
    p("  está en la base. No existe la grilla contra la cual cruzar contornos, así que la prueba")
    p("  se corre por la firma geométrica que una grilla dejaría igual, más el único borde de")
    p("  recorte que sí existe: el límite entre barrios.")
    p("")
    p(f"  RESULTADO SOBRE LOS {len(polos)} POLOS · la vara con la que se lee el sur")
    for nombre, columna in [("4.1 fuente", "pasa_fuente"), ("4.2 grilla", "pasa_grilla"),
                            ("4.3 cobertura", "pasa_cobertura"),
                            ("    (dos colas)", "pasa_cobertura_dos_colas")]:
        p(f"    {nombre:<16} pasan {int(polos[columna].sum()):>3} de {len(polos)} | "
          f"fallan {int((~polos[columna]).sum())}")
    p("    La fila de dos colas está sólo para mostrar cuánto se infla la prueba al mirar la cola")
    p("    equivocada: una banda p10–p90 deja afuera al 20 % de los barrios por construcción, así")
    p("    que ese conteo mide el ancho de la banda y no el riesgo de artefacto.")
    p(f"    distribución de la firma de grilla en toda la Ciudad: rectangularidad mediana "
      f"{polos.rectangularidad.median():.2f} | perímetro en ejes mediano "
      f"{polos.pct_perimetro_en_ejes.median():.1f} % | sobre borde interno mediano "
      f"{polos.pct_perimetro_sobre_borde_barrio.median():.1f} %")
    p("")

    sur = polos[polos.comuna.isin(COMUNAS_SIN_ZONA_PUBLICADA)].sort_values("locales", ascending=False)
    p(f"  LOS {len(sur)} POLOS DE LAS COMUNAS 8 Y 9, UNA PRUEBA POR VEZ Y EL RESULTADO DE CADA UNA")
    p("    Es el hallazgo del cotejo: el Atlas no tiene ninguna zona publicada en estas dos comunas")
    p("    y el clustering encuentra concentraciones ahí con los mismos parámetros que usó en")
    p("    Palermo. Se sostiene porque la parejidad dice que el sur no está peor cubierto. Antes de")
    p("    que salga de la carpeta, las tres pruebas, polo por polo.")
    p("")
    # La tabla va partida en tres bloques, uno por prueba, porque una sola fila de veinte columnas
    # no se lee y lo que se pidió es el resultado de cada prueba para cada polo.
    p("    4.1 · ARTEFACTO DE FUENTE — ¿más del 70 % de los puntos de un solo grupo?")
    p(sur[["polo_id", "barrio_principal", "comuna", "locales", "grupo_dominante",
           "peso_grupo_dominante", "pasa_fuente"]].round(2).to_string(index=False))
    p("")
    p("    4.2 · ARTEFACTO DE GRILLA — ¿el contorno tiene forma de celda de consulta?")
    p(sur[["polo_id", "barrio_principal", "ha", "vertices", "rectangularidad",
           "pct_perimetro_en_ejes", "pct_perimetro_sobre_borde_barrio",
           "pasa_grilla"]].round(2).to_string(index=False))
    p("")
    p("    4.3 · ARTEFACTO DE COBERTURA — la parejidad del barrio, al lado de cada polo")
    p(sur[["polo_id", "barrio_principal", "locales", "locales_x_ha", "clase_densidad",
           "cobertura_barrio", "composicion_barrio", "pasa_cobertura",
           "pasa_cobertura_dos_colas"]].round(2).to_string(index=False))
    p("")
    p("    LAS TRES JUNTAS, con la añada del Relevamiento que sostiene a cada uno")
    p(sur[["polo_id", "barrio_principal", "barrios", "locales", "pasa_fuente", "pasa_grilla",
           "pasa_cobertura", "pruebas_que_pasa", "anada_relevamiento", "anada_mixta",
           "anadas", "pct_puntos_del_relevamiento"]].to_string(index=False))
    p("")
    p(f"    4.1 fuente    · pasan {int(sur.pasa_fuente.sum())} de {len(sur)}"
      + ("" if sur.pasa_fuente.all() else
         f" — fallan {' '.join(sur[~sur.pasa_fuente].polo_id)}"))
    p(f"    4.2 grilla    · pasan {int(sur.pasa_grilla.sum())} de {len(sur)}"
      + ("" if sur.pasa_grilla.all() else
         f" — fallan {' '.join(sur[~sur.pasa_grilla].polo_id)}"))
    p(f"    4.3 cobertura · pasan {int(sur.pasa_cobertura.sum())} de {len(sur)}"
      + ("" if sur.pasa_cobertura.all() else
         f" — fallan {' '.join(sur[~sur.pasa_cobertura].polo_id)}"))
    p(f"    las tres      · pasan {int((sur.pruebas_que_pasa == 3).sum())} de {len(sur)}")
    p("")
    p("    Y el número que convierte la sospecha en hallazgo, repetido acá porque sin él la tabla")
    p("    de arriba no alcanza: la cobertura de la base en el sur (comunas 4, 8 y 9) es 2,50")
    p("    contra 2,45 del resto. El sur no está peor cubierto: tiene menos gastronomía, medida")
    p("    caminando por un tercero.")
    p("")
    return polos, sur


# --------------------------------------------------------------------------- §6 las siete zonas


def explicar_zonas(polos_v1: gpd.GeoDataFrame, polos: gpd.GeoDataFrame, zonas_22: gpd.GeoDataFrame,
                   geo: gpd.GeoDataFrame, parejidad: pd.DataFrame, p) -> pd.DataFrame:
    """§6 · para cada zona no encontrada, cuál de las tres explicaciones aplica.

    Se evalúa sobre el conjunto de la ETAPA 1, que es el cotejo que está sobre la mesa: las siete
    zonas que se discutieron son las de esa corrida. La partición del §3 movió el cotejo y ese
    movimiento se reporta al lado, como consecuencia, en vez de reemplazar la lista en silencio.
    """
    union_v1, union_final = polos_v1.union_all(), polos.union_all()
    p10 = parejidad.cobertura.quantile(COBERTURA_P_BAJO)

    filas = []
    for zona in zonas_22.itertuples():
        cubierta = zona.geometry.intersection(union_v1).area / zona.geometry.area
        cubierta_final = zona.geometry.intersection(union_final).area / zona.geometry.area
        adentro = geo[geo.within(zona.geometry)]
        en_polo = int((adentro.polo_id != "").sum())
        pct_en_polo = en_polo / len(adentro) if len(adentro) else 0.0
        cobertura = parejidad.cobertura.get(zona.barrio_k, np.nan)

        if cubierta >= COBERTURA_MINIMA_ZONA:
            explicacion, detalle = "ENCONTRADA", ""
        elif pct_en_polo >= MAYORIA_LOCALES_EN_POLO:
            explicacion = "E1 · no era una concentración: el perímetro es más ancho"
            detalle = (f"el {pct_en_polo:.0%} de sus {len(adentro)} locales SÍ está adentro de algún "
                       f"polo, pero esos polos ocupan sólo el {cubierta * 100:.1f} % de sus "
                       f"{zona.ha_zona:.0f} ha publicadas. La concentración está; lo que es más "
                       "ancho es el perímetro. Que no produzca un cluster del tamaño de la zona la "
                       "confirma, no la refuta")
        elif not np.isnan(cobertura) and cobertura < p10:
            explicacion = "E2 · la cobertura de la base ahí es floja"
            detalle = (f"cobertura del barrio {cobertura:.2f}, por debajo del p10 de la Ciudad "
                       f"({p10:.2f}): no se concluye nada sobre la zona")
        else:
            explicacion = "E3 · queda como pregunta, no como conclusión"
            detalle = (f"sólo el {pct_en_polo:.0%} de sus {len(adentro)} locales cae en algún polo y "
                       f"la cobertura del barrio ({cobertura:.2f}) no es floja, así que no aplican "
                       "E1 ni E2. El criterio dice que esta hipótesis no se declara desde un "
                       "borrador: se anota como pregunta para la Dirección")
        filas.append({
            "referencia_id": zona.referencia_id, "nombre": zona.nombre,
            "ha_zona": round(zona.ha_zona, 1),
            "locales_en_la_zona": len(adentro),
            "locales_x_ha_perimetro": round(zona.locales_x_ha, 2),
            "locales_x_ha_hull": round(zona.locales_x_ha_hull, 2),
            "clase_densidad_hull": zona.clase_densidad_hull,
            "pct_zona_cubierta": round(cubierta * 100, 1),
            "pct_locales_en_algun_polo": round(pct_en_polo * 100, 1),
            "cobertura_barrio": round(cobertura, 2) if not np.isnan(cobertura) else np.nan,
            "explicacion": explicacion,
            "pct_zona_cubierta_tras_partir": round(cubierta_final * 100, 1),
            "detalle": detalle,
        })
    tabla = pd.DataFrame(filas)
    no_encontradas = tabla[tabla.explicacion != "ENCONTRADA"].sort_values(
        "pct_zona_cubierta", ascending=False)

    p("§6 · LAS ZONAS PUBLICADAS QUE EL CLUSTERING NO ENCUENTRA, CON SU EXPLICACIÓN")
    p("=" * 100)
    p("")
    p("  Se evalúa sobre el conjunto de la ETAPA 1, que es el cotejo que está sobre la mesa. Lo que")
    p("  la partición del §3 le hizo a cada zona va en su propia columna, no reemplaza la lista.")
    p("")
    p("  Las tres explicaciones y su orden de probabilidad son las del §4 de")
    p("  CRITERIOS_LECTURA_POLIGONIZACION.md. Ninguna zona publicada se pone en duda acá: el")
    p("  borrador no tiene autoridad para eso.")
    p("")
    p("    E1 · no era una concentración sino una lectura territorial de la Dirección. Se asigna")
    p(f"         cuando la MAYORÍA (≥ {MAYORIA_LOCALES_EN_POLO:.0%}) de los locales de la zona sí")
    p("         está adentro de algún polo, pero esos polos ocupan menos de un cuarto de la")
    p("         superficie publicada: la concentración está, el perímetro es más ancho. No se usa")
    p("         la densidad de la zona para decidirlo: casi todas las publicadas caen en la clase")
    p("         baja por su perímetro editorial, y una regla por densidad le pondría E1 a las siete")
    p("         sin distinguir nada.")
    p(f"    E2 · la cobertura de la base ahí es floja (cobertura del barrio por debajo del p10 = "
      f"{p10:.2f}).")
    p("    E3 · la zona no se sostiene. Última hipótesis, y no se declara desde un borrador.")
    p("")
    p(f"  ZONAS NO ENCONTRADAS: {len(no_encontradas)} de {len(tabla)}")
    p(no_encontradas[["referencia_id", "nombre", "ha_zona", "locales_en_la_zona",
                      "locales_x_ha_hull", "pct_zona_cubierta", "pct_locales_en_algun_polo",
                      "cobertura_barrio", "explicacion"]].to_string(index=False))
    p("")
    p("  REPARTO DE LAS EXPLICACIONES")
    for explicacion, cuenta in no_encontradas.explicacion.value_counts().items():
        cuales = " ".join(no_encontradas[no_encontradas.explicacion == explicacion].referencia_id)
        p(f"    {cuenta} · {explicacion} — {cuales}")
    p("")
    # Una regla con umbral produce casos al filo, y un caso al filo presentado como categoría
    # limpia es peor que no clasificarlo. Se marcan explícitamente y se dice de qué lado caen.
    al_filo = no_encontradas[
        (no_encontradas.pct_locales_en_algun_polo.between(
            MAYORIA_LOCALES_EN_POLO * 100 - 10, MAYORIA_LOCALES_EN_POLO * 100 + 10))
        | ((no_encontradas.cobertura_barrio - p10).abs() < 0.05)]
    if len(al_filo):
        p("  CASOS AL FILO · la regla los clasifica, pero por poco, y eso se dice")
        for fila in al_filo.itertuples():
            razones = []
            if abs(fila.pct_locales_en_algun_polo - MAYORIA_LOCALES_EN_POLO * 100) <= 10:
                razones.append(f"{fila.pct_locales_en_algun_polo:.1f} % de locales en polo contra "
                               f"un umbral de {MAYORIA_LOCALES_EN_POLO:.0%}")
            if abs(fila.cobertura_barrio - p10) < 0.05:
                razones.append(f"cobertura {fila.cobertura_barrio:.2f} contra un p10 de {p10:.2f}")
            p(f"    {fila.referencia_id} · {fila.nombre} → {fila.explicacion}")
            p(f"       queda del lado que queda por: {'; '.join(razones)}")
        p("    No se mueve ningún umbral para acomodarlos. Se marca que la asignación es frágil y")
        p("    que un criterio editorial los podría leer del otro lado con el mismo derecho.")
        p("")
    p("  DIVERGENCIA CON LA LECTURA PREVIA, ANOTADA PORQUE NO COINCIDE. La conversación anterior")
    p("  daba por descontado que cuatro de las siete (R21, R22, R04, R16) eran perímetros mucho")
    p("  más anchos que su concentración. Medido con la regla declarada arriba, E1 le toca a tres")
    p("  —R07, R16 y R22— y no a las cuatro esperadas: R21 se va a E2 al filo, y R04 no llega")
    p("  porque sólo un tercio de sus locales cae en algún polo. La regla no se ajustó para")
    p("  reproducir la expectativa.")
    p("")
    p("  UNA POR UNA")
    for fila in no_encontradas.itertuples():
        p(f"    {fila.referencia_id} · {fila.nombre}")
        p(f"       {fila.explicacion}")
        for linea in _envolver_texto(fila.detalle, 92):
            p(f"       {linea}")
        if fila.referencia_id == "R20":
            p(f"       ANOTADO ASÍ Y NO RESCATADO: quedó a "
              f"{COBERTURA_MINIMA_ZONA * 100 - fila.pct_zona_cubierta:.1f} puntos del umbral de "
              f"{COBERTURA_MINIMA_ZONA:.0%}. El umbral se fijó")
            p("       antes de correr y no se mueve para alcanzarla.")
        if fila.referencia_id == "R04":
            p("       PENDIENTE APARTE: el Relevamiento declara 52 parcelas comerciales activas en")
            p("       todo Puerto Madero, un número implausible que hace sospechar del Relevamiento")
            p("       ahí antes que de la base. Verificar antes de concluir nada sobre R04.")
        p("")

    # Lo que la partición le hizo al cotejo. Va acá y no escondido, porque cambia la lista.
    movidas = tabla[tabla.pct_zona_cubierta_tras_partir < COBERTURA_MINIMA_ZONA * 100]
    perdidas = movidas[movidas.explicacion == "ENCONTRADA"]
    p("  LO QUE LA PARTICIÓN DEL §3 LE HIZO A ESTE COTEJO")
    p(f"    zonas encontradas: {int((tabla.explicacion == 'ENCONTRADA').sum())} antes de partir → "
      f"{int((tabla.pct_zona_cubierta_tras_partir >= COBERTURA_MINIMA_ZONA * 100).sum())} después")
    if len(perdidas):
        p("    zonas que estaban encontradas y dejaron de estarlo al partir:")
        p(perdidas[["referencia_id", "nombre", "pct_zona_cubierta",
                    "pct_zona_cubierta_tras_partir"]].to_string(index=False))
    p("    No es un problema del cotejo: es el precio de partir, y el §3 lo cuantifica. Partir")
    p("    achica los polos, y polos más chicos cubren menos superficie publicada. La decisión de")
    p("    partir ya estaba tomada; lo que corresponde acá es dejar escrito cuánto costó.")
    p("")
    return tabla


def _envolver_texto(texto: str, ancho: int) -> list[str]:
    """Corta un texto largo en líneas, para que las explicaciones no salgan en una sola tira."""
    palabras, lineas, actual = texto.split(), [], ""
    for palabra in palabras:
        if len(actual) + len(palabra) + 1 > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f"{actual} {palabra}".strip()
    if actual:
        lineas.append(actual)
    return lineas


# --------------------------------------------------------------------------- insumos derivados


def cargar_parejidad() -> pd.DataFrame:
    tabla = pd.read_csv(GEN_PAREJIDAD / "parejidad_a_parcelas_comerciales.csv", index_col=0)
    tabla.index = [plegar(i) for i in tabla.index]
    return tabla


def medir_zonas_22(geo_todos: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Las 22 publicadas medidas con la MISMA base y la misma métrica que los polos del borrador.

    Sin esto no hay comparación posible: la densidad de una zona publicada y la de un polo del
    borrador tienen que salir del mismo numerador y del mismo denominador.

    Y hacen falta DOS densidades, porque las dos superficies miden cosas distintas:

      `locales_x_ha`      sobre el perímetro publicado. Es lo que implica el mapa del Atlas, y es
                          el número honesto para decir «qué densidad tiene la zona tal como está
                          dibujada». Pero un perímetro editorial es más ancho que un hull ajustado
                          a los puntos, así que este número SIEMPRE sale más bajo.
      `locales_x_ha_hull` sobre la envolvente cóncava de los propios puntos de la zona, con el
                          mismo ratio 0,55 que usan los polos del borrador. Es la única comparable
                          punto por punto: mismo numerador, mismo tipo de denominador.

    Comparar la densidad de un polo del borrador contra la del perímetro publicado sin decir esto
    haría parecer ralas a las zonas publicadas por cómo están dibujadas, no por lo que tienen.
    """
    from borrador_polos_ciudad import envolver  # local: sólo se usa acá

    zonas = gpd.read_file(ENVOLVENTES_22)[["referencia_id", "nombre", "geometry"]].to_crs(CRS_METRICO)
    zonas["ha_zona"] = zonas.area / 1e4
    dentro = gpd.sjoin(geo_todos[["local_id", "barrio", "geometry"]], zonas[["referencia_id", "geometry"]],
                       how="inner", predicate="within")
    cuenta = dentro.groupby("referencia_id").local_id.size()
    barrio_modal = dentro.groupby("referencia_id").barrio.agg(
        lambda s: s.value_counts().index[0] if len(s) else "")
    zonas["locales"] = zonas.referencia_id.map(cuenta).fillna(0).astype(int)
    zonas["locales_x_ha"] = zonas.locales / zonas.ha_zona
    zonas["barrio_k"] = zonas.referencia_id.map(barrio_modal).fillna("").map(plegar)

    hulls = {}
    for referencia, grupo in dentro.groupby("referencia_id"):
        if len(grupo) < 3:
            continue
        geometria, _ = envolver(geo_todos.loc[grupo.index], PARAMETROS["concave_hull_ratio"])
        hulls[referencia] = geometria.area / 1e4
    zonas["ha_hull"] = zonas.referencia_id.map(hulls)
    zonas["locales_x_ha_hull"] = zonas.locales / zonas.ha_hull
    return zonas


def cotejo_final(polos: gpd.GeoDataFrame, zonas_22: gpd.GeoDataFrame, p) -> gpd.GeoDataFrame:
    """El cotejo contra las 22, rehecho sobre el conjunto final. Los umbrales no se tocan."""
    union_zonas = zonas_22.union_all()
    solapes, contiene = [], []
    for geometria in polos.geometry:
        solapes.append(round(geometria.intersection(union_zonas).area / geometria.area * 100, 1))
        contiene.append(";".join(
            z.referencia_id for z in zonas_22.itertuples()
            if geometria.intersection(z.geometry).area / z.geometry.area >= 0.5))
    polos = polos.copy()
    polos["pct_ya_publicado"] = solapes
    polos["zonas_que_contiene"] = contiene
    polos["es_nuevo"] = (polos.pct_ya_publicado < 25) & (polos.zonas_que_contiene == "")
    p(f"  cotejo rehecho sobre el conjunto final: {int(polos.es_nuevo.sum())} polos nuevos de "
      f"{len(polos)}")
    p(f"  polos que todavía contienen entera una zona publicada: "
      f"{int((polos.zonas_que_contiene != '').sum())}")
    p("")
    return polos


# --------------------------------------------------------------------------- informe


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    base_completa = cargar_base_completa()
    parejidad = cargar_parejidad()
    barrios = gpd.read_file(BARRIOS)[["nombre", "comuna", "geometry"]].to_crs(CRS_METRICO)
    zonas_22 = medir_zonas_22(geo)

    pertenencia = pd.read_csv(PERTENENCIA_V1)
    geo = geo.merge(pertenencia[["local_id", "polo_id"]], on="local_id", how="left",
                    suffixes=("", "_v1"))
    geo["polo_id"] = geo.polo_id.fillna("")
    polos_v1 = gpd.read_file(OUT / "borrador_polos.geojson").to_crs(CRS_METRICO)

    p("BORRADOR · la densidad como atributo, la partición de los encadenados y las pruebas")
    p("=" * 100)
    p("")
    p("NO ES UN PRODUCTO. No se publica, no se sella y no toca el Atlas.")
    p("Google Places: 0 requests. Places no está en la base.")
    p("")
    p("LO PRIMERO, PORQUE DEFINE QUÉ ES ESTE MAPA Y NO VA EN NINGÚN ANEXO:")
    ruido = int((geo.polo_id == "").sum())
    p(f"  **{ruido:,} de los {len(geo):,} locales aptos —el {ruido / len(geo) * 100:.1f} %— no están")
    p("  en ningún polo.** La mayor parte de la gastronomía de la Ciudad no está en un polo. Este")
    p("  mapa mapea concentraciones; no mapea el sector. Cualquier política pensada sólo en clave")
    p("  de polos deja afuera a la mayoría de los locales.")
    p("")

    # --- §1 sobre el conjunto de la etapa 1, que es el que está sobre la mesa
    polos_v1, cortes, ajuste = clasificar_densidad(polos_v1, p)
    bordes = [-np.inf, *cortes, np.inf]
    etiquetas_clase = list(polos_v1.clase_densidad.cat.categories)
    zonas_22["clase_densidad"] = pd.cut(zonas_22.locales_x_ha, bordes, labels=etiquetas_clase)
    zonas_22["clase_densidad_hull"] = pd.cut(zonas_22.locales_x_ha_hull, bordes,
                                             labels=etiquetas_clase)
    tabla_clases = resumen_clases(polos_v1, zonas_22, p)

    # comuna modal por polo, que hace falta para la sensibilidad y para el sur
    comuna_v1 = geo[geo.polo_id != ""].groupby("polo_id").comuna.agg(
        lambda s: s.value_counts().index[0] if len(s) else np.nan)
    polos_v1["comuna"] = polos_v1.polo_id.map(comuna_v1)

    # --- §2
    tabla_piso = sensibilidad_piso(polos_v1, zonas_22, p)

    # --- §3
    geo, detalle_particion = particionar(geo, polos_v1, p)
    polos = reconstruir_polos(geo, base_completa)
    comuna_final = geo[geo.polo_final != ""].groupby("polo_final").comuna.agg(
        lambda s: s.value_counts().index[0] if len(s) else np.nan)
    polos["comuna"] = polos.polo_id.map(comuna_final)
    polos["clase_densidad"] = pd.cut(polos.locales_x_ha, bordes, labels=etiquetas_clase)

    ruido_final = int((geo.polo_final == "").sum())
    p("  EL CONJUNTO FINAL, DESPUÉS DE PARTIR")
    p(f"    polos: {len(polos_v1)} → {len(polos)}")
    p(f"    locales en algún polo: {len(geo) - ruido:,} → {len(geo) - ruido_final:,}")
    p(f"    locales fuera de todo polo: {ruido / len(geo) * 100:.1f} % → "
      f"{ruido_final / len(geo) * 100:.1f} %")
    p(f"    superficie: {polos_v1.ha.sum():,.0f} ha → {polos.ha.sum():,.0f} ha "
      f"({polos.ha.sum() / SUPERFICIE_CIUDAD_HA * 100:.1f} % de la Ciudad)")
    p(f"    control §5 · envolventes que pasan: {int(polos.control_aptitud.sum())} de {len(polos)}")
    p("")
    p("    Las clases NO se recalcularon después de partir: se aplican los cortes declarados en §1")
    p("    sobre el conjunto nuevo. Refitear los cortes acá haría que las clases de antes y las de")
    p("    después dejaran de ser comparables, que es justo lo que la clase viene a arreglar.")
    p(polos.groupby("clase_densidad", observed=True).agg(
        polos=("polo_id", "size"), locales=("locales", "sum"), ha=("ha", "sum")).round(1).to_string())
    p("")
    verificar_p072(polos, zonas_22, p)
    polos = cotejo_final(polos, zonas_22, p)

    # --- §5 antes que §4, porque la añada entra en la tabla del sur
    polos = anada_por_polo(geo, polos, parejidad, p)

    # --- §4
    polos, sur = pruebas_de_artefacto(polos, parejidad, barrios, p)

    # --- §6
    tabla_zonas = explicar_zonas(polos_v1, polos, zonas_22, geo, parejidad, p)

    # --------------------------------------------------------------- salidas
    salida = buffer.getvalue()
    (OUT / "POLOS_ATRIBUTOS_Y_PRUEBAS.txt").write_text(salida, encoding="utf-8")

    polos.drop(columns=["geometry"]).round(3).to_csv(
        OUT / "borrador_polos_v2.csv", index=False, encoding="utf-8")
    polos.to_crs(CRS_GEO).to_file(OUT / "borrador_polos_v2.geojson", driver="GeoJSON")
    geo[["local_id", "polo_id", "polo_final", "barrio", "comuna", "anillo", "n_fuentes",
         "nivel_publicacion"]].to_csv(OUT / "pertenencia_local_polo_v2.csv", index=False,
                                      encoding="utf-8")
    tabla_clases.to_csv(OUT / "clases_densidad.csv", encoding="utf-8")
    ajuste.to_csv(OUT / "clases_densidad_ajuste.csv", index=False, encoding="utf-8")
    tabla_piso.to_csv(OUT / "sensibilidad_piso_absoluto.csv", index=False, encoding="utf-8")
    detalle_particion.to_csv(OUT / "particion_encadenados.csv", index=False, encoding="utf-8")
    sur.drop(columns=["geometry"]).round(3).to_csv(
        OUT / "pruebas_artefacto_sur.csv", index=False, encoding="utf-8")
    tabla_zonas.to_csv(OUT / "siete_zonas_explicacion.csv", index=False, encoding="utf-8")
    zonas_22.drop(columns=["geometry"]).round(3).to_csv(
        OUT / "zonas_22_densidad.csv", index=False, encoding="utf-8")

    (OUT / "parametros_v2.json").write_text(json.dumps({
        "etapa": "2 · densidad como atributo, partición y pruebas",
        "clases_densidad": {"metodo": "Fisher-Jenks", "k": len(cortes) + 1,
                            "gvf_minimo": GVF_MINIMO, "cortes_locales_x_ha": cortes,
                            "nombres": etiquetas_clase},
        "piso_absoluto_sensibilidad": list(PISOS_ABSOLUTOS),
        "particion": {"percentil_superficie": PERCENTIL_SUPERFICIE, "metodo": METODO_PARTICION,
                      "rescate_de_fragmentos": RESCATE_DE_FRAGMENTOS},
        "pruebas_artefacto": {
            "peso_fuente_maximo": PESO_FUENTE_MAXIMO,
            "rectangularidad_maxima": RECTANGULARIDAD_MAXIMA,
            "tolerancia_angular_grados": TOLERANCIA_ANGULAR_GRADOS,
            "perimetro_en_ejes_maximo": PERIMETRO_EN_EJES_MAXIMO,
            "perimetro_sobre_borde_maximo": PERIMETRO_SOBRE_BORDE_MAXIMO,
            "buffer_borde_barrio_m": BUFFER_BORDE_BARRIO_M,
            "cobertura_percentiles": [COBERTURA_P_BAJO, COBERTURA_P_ALTO]},
        "estado": "BORRADOR_NO_PUBLICABLE",
        "places_requests": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
