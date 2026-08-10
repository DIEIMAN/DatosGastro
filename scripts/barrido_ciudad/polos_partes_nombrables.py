"""¿Los polos grandes tienen PARTES nombrables? El barrido de Belgrano, con su regla de aceptación.

EL HUECO DEL MÉTODO QUE ESTE SCRIPT CIERRA
-------------------------------------------
El criterio de partición que se venía usando estaba diseñado para cazar **encadenamiento**: polos
grandes y RALOS, donde `eom` había pegado barrios contiguos en una mancha. Por eso la población a
partir era «percentil 90 de superficie Y debajo de la densidad mediana», y por eso P091 y P078
nunca fueron candidatos: son densos.

Pero el Atlas no parte sólo lo que está mal unido. **También reconoce partes en lo que está bien
unido.** Palermo, Belgrano, Costanera Norte, Caballito, Villa Urquiza y Puerto Madero están
publicados como polo con subzonas o partes. Y a Belgrano sus tres partes se las encontró un
**barrido de continuidad**, no una prueba anti-encadenamiento. Son dos preguntas distintas:

    partición   · «¿esto son dos cosas que el algoritmo pegó mal?»      → grandes y ralos
    partes      · «¿esto es una cosa con partes reconocibles adentro?»  → cualquier polo grande

Este script hace la segunda, y **no parte nada**: reporta si hay partes nombrables y estables, para
que la Dirección decida si corresponde publicarlas como subzonas de una zona con nombre común.

LA REGLA DE ACEPTACIÓN ES LA DE BELGRANO, NO LA DE LA PARTICIÓN
----------------------------------------------------------------
Declarada antes de correr, y las tres condiciones son necesarias:

  1. **Las partes se llevan casi todos los locales.** Es la condición que faltó en P065 y por la
     que su partición de 55 m parecía razonable: dos partes nombrables acompañadas de 28 esquirlas
     no son una estructura de partes, son tejido continuo mirado con lupa. Umbral: `COBERTURA_MINIMA`.
  2. **El conteo de partes es estable en un rango de umbral.** Una estructura que existe en un solo
     valor del barrido es un accidente del valor. Umbral: `TRAMOS_ESTABLES` umbrales consecutivos
     con el mismo conteo.
  3. **Cada parte tiene nombre de uso corriente o respaldo documental.** Esto **NO lo decide el
     algoritmo** —lo dice el §5 de CRITERIOS_LECTURA— así que el script no la evalúa: aporta la
     evidencia para que se decida a ojo (barrios que toca cada parte, y qué zona publicada del
     Atlas le cae encima).

LA GRILLA DE UMBRALES SE EXTIENDE HACIA ABAJO, Y HAY QUE DECIR POR QUÉ
------------------------------------------------------------------------
La grilla anterior (40–300 m) se diseñó para polos de 2 a 4 locales/ha. La distancia típica entre
vecinos escala con 1/√densidad: a 8 locales/ha —P091— los puntos están a la mitad de distancia que
a 2, así que con un piso de 40 m todo aparece conectado desde el primer valor y el barrido no
resuelve nada. Se agregan 20, 25, 30 y 35 m **por esa razón geométrica**, no para que aparezcan las
partes que uno espera. Y se verifica: si las partes de un polo denso sólo existen en los umbrales
nuevos y desaparecen apenas se sube, la condición 2 las descarta sola.

Google Places no interviene. 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_partes_nombrables.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import (  # noqa: E402
    CRS_METRICO, ENVOLVENTES_22, PARAMETROS, cargar_puntos, envolver,
)
from polos_atributos_clases import OUT  # noqa: E402
from polos_particion_anada_estructura import MINIMO, componentes  # noqa: E402

# --- población: cualquier polo grande, denso o no. El tamaño es lo único que importa acá, porque
# la pregunta es si adentro hay partes reconocibles y un polo chico no tiene lugar para dos.
TAMANIO_MINIMO = 300

# --- la grilla, extendida hacia abajo por la razón geométrica del docstring
UMBRALES = (20, 25, 30, 35, 40, 55, 70, 80, 120, 160, 200, 250, 300)

# --- la regla de aceptación de Belgrano, declarada antes de correr
COBERTURA_MINIMA = 0.80    # las partes se llevan al menos el 80 % de los locales del polo
TRAMOS_ESTABLES = 2        # el conteo se repite en al menos 2 umbrales consecutivos


def evaluar(cuerpo: gpd.GeoDataFrame) -> pd.DataFrame:
    """El barrido completo de un polo, con las dos condiciones medibles por umbral."""
    filas = []
    for umbral in UMBRALES:
        partes = componentes(cuerpo, umbral)
        nombrables = [c for c in partes if len(c) >= MINIMO]
        en_partes = sum(len(c) for c in nombrables)
        filas.append({
            "umbral_m": umbral,
            "componentes": len(partes),
            "partes_nombrables": len(nombrables),
            "pct_locales_en_esas_componentes": round(en_partes / len(cuerpo) * 100, 1),
            "cumple_cobertura": en_partes / len(cuerpo) >= COBERTURA_MINIMA,
            "tamanos": ";".join(str(len(c)) for c in partes[:6]),
        })
    return pd.DataFrame(filas)


def tramos_de_conteo_constante(curva: pd.DataFrame, exigir_cobertura: bool) -> list[tuple[int, list[int]]]:
    """Todos los tramos de umbrales consecutivos con el mismo conteo de partes (≥ 2).

    Con `exigir_cobertura` es la condición de aceptación completa. Sin ella sirve para el
    diagnóstico de los que fallan: permite preguntar «¿la estructura era estable y le faltó
    cobertura, o directamente no era estable?», que son dos fracasos distintos y se arreglan de
    maneras distintas.
    """
    apto = curva[curva.partes_nombrables >= 2]
    if exigir_cobertura:
        apto = apto[apto.cumple_cobertura]
    tramos, actual, conteo_actual = [], [], None
    for fila in curva.itertuples():           # se recorre la curva entera para respetar el orden
        if fila.umbral_m not in set(apto.umbral_m) or fila.partes_nombrables != conteo_actual:
            if len(actual) >= TRAMOS_ESTABLES and conteo_actual:
                tramos.append((conteo_actual, actual))
            actual = []
            conteo_actual = None
        if fila.umbral_m in set(apto.umbral_m):
            if conteo_actual is None:
                conteo_actual = int(fila.partes_nombrables)
            actual = actual + [int(fila.umbral_m)]
    if len(actual) >= TRAMOS_ESTABLES and conteo_actual:
        tramos.append((conteo_actual, actual))
    return tramos


def tramo_estable(curva: pd.DataFrame) -> tuple[int, list[int]] | None:
    """El tramo más largo de umbrales consecutivos con ≥2 partes y cobertura suficiente.

    Devuelve el conteo de partes y los umbrales del tramo. Si el conteo cambia de un umbral al
    siguiente, el tramo se corta: una estructura que aparece con 3 partes y sigue con 5 no es la
    misma estructura vista dos veces.
    """
    mejor = None
    apto = curva[(curva.partes_nombrables >= 2) & curva.cumple_cobertura]
    for conteo, grupo in apto.groupby("partes_nombrables"):
        umbrales = sorted(grupo.umbral_m)
        posiciones = [UMBRALES.index(u) for u in umbrales]
        actual = [posiciones[0]]
        for anterior, siguiente in zip(posiciones, posiciones[1:]):
            actual = actual + [siguiente] if siguiente == anterior + 1 else [siguiente]
            if mejor is None or len(actual) > len(mejor[1]):
                mejor = (int(conteo), list(actual))
        if mejor is None or len(actual) > len(mejor[1]):
            mejor = (int(conteo), list(actual))
    if mejor is None or len(mejor[1]) < TRAMOS_ESTABLES:
        return None
    return mejor[0], [UMBRALES[i] for i in mejor[1]]


def describir_partes(cuerpo: gpd.GeoDataFrame, umbral: int, zonas: gpd.GeoDataFrame) -> pd.DataFrame:
    """Las partes en el umbral elegido, con la evidencia para que alguien las nombre.

    El algoritmo NO nombra: el §5 del criterio de lectura lo dice explícito. Lo que se aporta es
    con qué barrios se corresponde cada parte y qué zona publicada le cae encima, que es el
    respaldo documental sobre el que se decide a ojo.
    """
    filas = []
    for orden, indices in enumerate(
            [c for c in componentes(cuerpo, umbral) if len(c) >= MINIMO], start=1):
        miembros = cuerpo.iloc[indices]
        geometria, _ = envolver(miembros, PARAMETROS["concave_hull_ratio"])
        ha = geometria.area / 1e4
        solapes = {z.referencia_id: geometria.intersection(z.geometry).area / geometria.area
                   for z in zonas.itertuples() if geometria.intersects(z.geometry)}
        solapes = {k: v for k, v in sorted(solapes.items(), key=lambda x: -x[1]) if v > 0.05}
        barrios = miembros.barrio.value_counts()
        filas.append({
            "parte": f"S{orden}",
            "locales": len(miembros),
            "ha": round(ha, 1),
            "locales_x_ha": round(len(miembros) / ha, 2),
            "barrios": ";".join(f"{b} ({c})" for b, c in barrios.head(3).items()),
            "zona_publicada_encima": ";".join(f"{k} {v:.0%}" for k, v in solapes.items()) or "—",
        })
    return pd.DataFrame(filas)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    polos = pd.read_csv(OUT / "borrador_polos_v3.csv")
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)

    grandes = polos[polos.locales >= TAMANIO_MINIMO].sort_values("locales", ascending=False)

    p("¿LOS POLOS GRANDES TIENEN PARTES NOMBRABLES? · barrido de continuidad de Belgrano")
    p("=" * 100)
    p("")
    p("NO SE PARTE NADA ACÁ. Esto reporta si hay partes reconocibles adentro de un polo, para que")
    p("la Dirección decida si corresponde publicarlas como subzonas de una zona con nombre común.")
    p("Google Places: 0 requests.")
    p("")
    p("  LA PREGUNTA ES OTRA QUE LA DE LA PARTICIÓN, Y POR ESO LA POBLACIÓN ES OTRA")
    p("    partición · «¿esto son dos cosas que el algoritmo pegó mal?»     → grandes y RALOS")
    p("    partes    · «¿esto es una cosa con partes reconocibles adentro?» → cualquier polo grande")
    p("  El Atlas publica seis zonas como polo con subzonas o partes —Palermo, Belgrano, Costanera")
    p("  Norte, Caballito, Villa Urquiza y Puerto Madero—, y a las tres partes de Belgrano se las")
    p("  encontró este barrido, no una prueba anti-encadenamiento.")
    p("")
    p(f"  población: polos de {TAMANIO_MINIMO} locales o más → {len(grandes)} polos")
    p(f"  grilla extendida a {UMBRALES[0]}–{UMBRALES[-1]} m: la distancia típica entre vecinos")
    p("  escala con 1/√densidad, así que un polo de 8 loc/ha necesita umbrales que la grilla vieja")
    p("  (40–300 m) no tenía. Si las partes sólo existen en los umbrales nuevos, la condición de")
    p("  estabilidad las descarta sola.")
    p("")
    p("  REGLA DE ACEPTACIÓN, declarada antes de correr:")
    p(f"    1 · las partes se llevan ≥ {COBERTURA_MINIMA:.0%} de los locales del polo")
    p(f"    2 · el conteo de partes se repite en ≥ {TRAMOS_ESTABLES} umbrales consecutivos")
    p("    3 · cada parte tiene nombre de uso corriente o respaldo documental — **esto no lo")
    p("        decide el algoritmo**; se aporta la evidencia y se decide a ojo")
    p("")

    curvas, resumen, detalles = [], [], []
    for polo in grandes.itertuples():
        cuerpo = geo[geo.polo_unido == polo.polo_id]
        curva = evaluar(cuerpo)
        curva.insert(0, "polo_id", polo.polo_id)
        curvas.append(curva)
        estable = tramo_estable(curva)

        p("-" * 100)
        p(f"  {polo.polo_id} · {polo.barrio_principal} · {polo.locales} locales · "
          f"{polo.ha:.1f} ha · {polo.locales_x_ha:.2f} loc/ha · {polo.clase_densidad}")
        p(f"     barrios: {polo.barrios}")
        p("")
        p(curva.drop(columns=["polo_id"]).to_string(index=False))
        p("")
        if estable is None:
            p("     VEREDICTO: NO tiene partes nombrables y estables.")
            apto = curva[(curva.partes_nombrables >= 2) & curva.cumple_cobertura]
            if not len(apto):
                falla = curva[curva.partes_nombrables >= 2]
                if len(falla):
                    p(f"       aparecen 2 o más partes en {len(falla)} umbrales, pero ninguno llega")
                    p(f"       al {COBERTURA_MINIMA:.0%} de cobertura: el resto queda en esquirlas.")
                    p(f"       cobertura máxima con 2+ partes: "
                      f"{falla.pct_locales_en_esas_componentes.max():.1f} %")
                else:
                    p("       nunca aparecen 2 partes nombrables: el polo es un solo cuerpo en toda")
                    p("       la grilla.")
            else:
                p(f"       hay umbrales que cumplen cobertura ({', '.join(str(u) for u in apto.umbral_m)})")
                p(f"       pero el conteo no se repite en {TRAMOS_ESTABLES} umbrales consecutivos:")
                p("       la estructura cambia de forma con el umbral, así que es del umbral.")
            # Cuán cerca estuvo. Un umbral que falla por poco es información y un «no» a secas la
            # esconde: si el corte hubiera sido 0,79 en vez de 0,80 la respuesta sería otra, y eso
            # hay que poder verlo sin recorrer la tabla a mano.
            # Los dos fracasos son distintos y hay que separarlos: «la estructura era estable y le
            # faltó cobertura» se mide contra el umbral de cobertura; «no era estable» ni siquiera
            # llega a esa pregunta. Mirar la fila de máxima cobertura mezcla las dos y puede dar
            # una distancia negativa —una fila que cumple cobertura pero no estabilidad—.
            estables = tramos_de_conteo_constante(curva, exigir_cobertura=False)
            al_filo = False
            if estables:
                conteo_e, tramo_e = max(
                    estables,
                    key=lambda t: curva[curva.umbral_m.isin(t[1])].pct_locales_en_esas_componentes.max())
                cobertura_e = curva[curva.umbral_m.isin(tramo_e)].pct_locales_en_esas_componentes.max()
                falta = COBERTURA_MINIMA * 100 - cobertura_e
                al_filo = 0 < falta <= 5
                p("")
                p(f"       CUÁN CERCA ESTUVO: su mejor tramo estable son {conteo_e} partes en los")
                p(f"       umbrales {', '.join(str(u) for u in tramo_e)} m, con cobertura máxima "
                  f"{cobertura_e:.1f} %.")
                p(f"       Le faltan {falta:.1f} puntos de cobertura para pasar.")
                if al_filo:
                    p("       **AL FILO. El umbral se fijó antes de correr y NO se mueve para")
                    p("       alcanzarlo.** Pero queda anotado que un criterio editorial podría leerlo")
                    p("       del otro lado con el mismo derecho, y que estas partes merecen una")
                    p("       mirada a ojo antes de descartarlas.")
                    # Se muestran las partes aunque NO estén aceptadas. Esconderlas por un punto de
                    # diferencia sería dejar sin evidencia la única decisión que queda por tomar.
                    filo = describir_partes(cuerpo, max(tramo_e), zonas)
                    filo.insert(0, "polo_id", polo.polo_id)
                    filo["estado"] = "AL FILO · no aceptada"
                    detalles.append(filo)
                    p("")
                    p("       LAS PARTES QUE NO SE ACEPTAN, mostradas igual para que la decisión")
                    p("       editorial tenga con qué:")
                    p(filo.drop(columns=["polo_id"]).to_string(index=False))
            else:
                mejor = curva[curva.partes_nombrables >= 2]
                p("")
                if len(mejor):
                    p("       CUÁN CERCA ESTUVO: aparecen 2 o más partes en algún umbral, pero el")
                    p("       conteo nunca se repite en umbrales consecutivos. Falló por estabilidad,")
                    p("       no por cobertura: la estructura cambia de forma con el umbral, así que")
                    p("       es del umbral.")
                else:
                    p("       CUÁN CERCA ESTUVO: nada. Nunca aparecen 2 partes nombrables en toda la")
                    p("       grilla: el polo es un solo cuerpo.")
            resumen.append({"polo_id": polo.polo_id, "locales": polo.locales,
                            "partes": 0, "umbral": None,
                            "veredicto": "AL FILO" if al_filo else "SIN PARTES ESTABLES"})
            p("")
            continue

        conteo, tramo = estable
        umbral = max(tramo)   # el más alto del tramo estable: el conservador, el que menos fragmenta
        detalle = describir_partes(cuerpo, umbral, zonas)
        detalle.insert(0, "polo_id", polo.polo_id)
        detalle["estado"] = "ACEPTADA"
        detalles.append(detalle)
        p(f"     VEREDICTO: **{conteo} partes nombrables y estables**, en los umbrales "
          f"{', '.join(str(u) for u in tramo)} m")
        p(f"       se adopta el más alto del tramo ({umbral} m), que es el que menos fragmenta")
        p(f"       cobertura: {curva.loc[curva.umbral_m == umbral, 'pct_locales_en_esas_componentes'].iloc[0]:.1f} % de los locales")
        p("")
        p(detalle.drop(columns=["polo_id"]).to_string(index=False))
        p("")
        # Belgrano dio partes de 107, 82 y 23: comparables. Un cuerpo grande con un satélite chico
        # pasa la regla y no es lo mismo, así que la proporción se dice.
        proporcion = detalle.locales.min() / detalle.locales.max()
        if proporcion < 0.25:
            p(f"       ATENCIÓN a la proporción: la parte más chica tiene el {proporcion:.0%} de la")
            p("       más grande. Esto se parece más a «un cuerpo con un satélite» que a un polo de")
            p("       partes comparables como Belgrano (107 / 82 / 23). Pasa la regla igual, y la")
            p("       decisión de si eso amerita publicarse como subzona es editorial.")
            p("")
        p("       La condición 3 —nombre de uso corriente o respaldo documental— NO la evalúa el")
        p("       algoritmo. La evidencia está en las dos últimas columnas: con qué barrios se")
        p("       corresponde cada parte y qué zona publicada le cae encima.")
        resumen.append({"polo_id": polo.polo_id, "locales": polo.locales,
                        "partes": conteo, "umbral": umbral, "veredicto": "PARTES ESTABLES"})
        p("")

    p("=" * 100)
    p("RESUMEN")
    p("=" * 100)
    p("")
    tabla = pd.DataFrame(resumen)
    p(tabla.to_string(index=False))
    p("")
    con_partes = tabla[tabla.partes > 0]
    if len(con_partes):
        p(f"  {len(con_partes)} de {len(tabla)} polos grandes tienen partes nombrables y estables.")
        p("")
        p("  QUÉ SIGNIFICA Y QUÉ NO. Esto NO es una corrección del mapa: es exactamente lo que el")
        p("  Atlas ya publica para seis de sus zonas. Y es el camino por el que puede bajar el")
        p("  número de zonas sin perder información —agrupando polos como partes de una zona con")
        p("  nombre común— en vez de por consolidación geométrica, que en la unión a 100 m sólo")
        p("  produjo 2 fusiones de 35 candidatas.")
        p("")
        p("  LO QUE FALTA, Y NO LO PUEDE HACER UN SCRIPT: ponerles nombre. El §5 del criterio de")
        p("  lectura es explícito en que los nombres son de uso corriente y territorial y no salen")
        p("  de un cluster. La evidencia para hacerlo está en las tablas de arriba.")
    else:
        p(f"  Ninguno de los {len(tabla)} polos grandes tiene partes nombrables y estables con la")
        p("  regla de Belgrano. La consolidación por subzonas no aparece por este camino.")
    p("")

    salida = buffer.getvalue()
    (OUT / "PARTES_NOMBRABLES.txt").write_text(salida, encoding="utf-8")
    pd.concat(curvas).to_csv(OUT / "curvas_continuidad_polos_grandes.csv", index=False,
                             encoding="utf-8")
    tabla.to_csv(OUT / "partes_nombrables_resumen.csv", index=False, encoding="utf-8")
    if detalles:
        pd.concat(detalles).to_csv(OUT / "partes_nombrables_detalle.csv", index=False,
                                   encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
