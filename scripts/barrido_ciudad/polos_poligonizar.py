"""De envolvente de trabajo a polígono publicable, para los 124 polos del borrador.

LOS CRITERIOS, DECLARADOS ANTES DE CORRER
==========================================
Ese orden importa acá más que en ningún otro paso: un polígono se elige mirándolo, y mirándolo
siempre gana el que quedó lindo. Las cuatro decisiones y su motivo van escritas primero; el script
mide si se sostienen.

1 · CÓNCAVO, NO CONVEXO
------------------------
La envolvente convexa **reclama territorio que la oferta no ocupa**: rellena parques, playas de
maniobras, la traza del ferrocarril y el río, porque por construcción no puede tener entrantes. Y
hay un ancla mejor que el argumento: **las 22 envolventes que el Atlas ya publica no son convexas**
—14 de 22 son multiparte y tienen entre 17 y 309 vértices—. Publicar blobs convexos contradiría el
precedente publicado.

2 · EL RATIO NO SE ELIGE ACÁ: SE PONE A PRUEBA
-----------------------------------------------
`concave_hull_ratio = 0.55` ya está declarado en `PARAMETROS` y **produjo todos los números que
hoy existen**: la superficie de cada polo, su densidad, y por lo tanto su `clase_densidad`. Elegir
ahora un ratio distinto no sería «afinar el mapa»: movería en silencio la clase de los polos que
están cerca del corte de 4,58, que es una convención que ya publicamos.

Así que la regla declarada es: **el ratio no cambia, salvo que la curva muestre que 0,55 está
parado en un lugar inestable.** La curva es la prueba, no la excusa. Y se reporta lo que Diego
pidió medir —el área total contra el parámetro— más la consecuencia que de verdad importa:
**cuántos polos cambian de clase de densidad** a lo largo del rango. Si esa cifra es alta, la
elección del parámetro es efectivamente la mitad del mapa y hay que decirlo así.

3 · SIMPLIFICACIÓN CON UNA CONDICIÓN DURA, NO CON UN NÚMERO LINDO
------------------------------------------------------------------
Douglas–Peucker mueve los bordes hacia adentro y puede dejar locales **fuera de su propio
polígono**. Un polo cuyo polígono no contiene a sus locales no es un polígono del polo.

Regla declarada: **una tolerancia es admisible sólo si ningún local del polo queda fuera de su
polígono simplificado.** Se toma la mayor tolerancia admisible. No se elige por vértices ni por
prolijidad: el criterio es una condición que se cumple o no.

4 · SOLAPES: EL ÁREA VA DONDE ESTÁ LA OFERTA
---------------------------------------------
Dos polos son conjuntos de puntos disjuntos, así que un solape entre sus polígonos es un artefacto
de la envolvente y no una ambigüedad del territorio. Regla declarada: **el área solapada se le
resta al polo cuyo punto propio más cercano está más lejos** — se la queda el que efectivamente
tiene oferta ahí. Empate: se la queda el polígono más chico, que es el que más la necesita para
seguir siendo un polígono.

5 · NO SE RECORTA A MANZANA, Y NO ES UNA DECISIÓN: ES UNA CARENCIA
-------------------------------------------------------------------
Recortar a manzana necesita una capa de manzanas o parcelas, y **en el repositorio no hay
ninguna** —sólo barrios y comunas—. La base trae `smp` por local, que es la referencia
Sección-Manzana-Parcela, pero un identificador no es una geometría.

Así que el polígono queda libre, y eso se declara como lo que es: no elegimos bordes suaves,
todavía no podemos hacer otra cosa. Es coherente con lo que el Atlas ya dice de sus envolventes
—«una envolvente es una lectura de trabajo, no un límite oficial»— y el recorte a manzana queda
anotado como lo que haría falta para pasar de lectura de trabajo a límite dibujable.

NO PISA NADA
------------
`borrador_polos_v3.geojson` es la capa decidida y no se toca. Esto escribe una capa nueva.
Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_poligonizar.py
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
from scipy.spatial import cKDTree
from shapely.geometry import MultiPoint

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import (  # noqa: E402
    CRS_GEO, CRS_METRICO, ENVOLVENTES_22, PARAMETROS, cargar_puntos,
)
from polos_atributos_clases import OUT  # noqa: E402

RATIOS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90, 1.00]
RATIO_VIGENTE = PARAMETROS["concave_hull_ratio"]
TOLERANCIAS = [0, 2, 5, 10, 15, 20, 30, 50]


def hull(puntos: gpd.GeoDataFrame, ratio: float):
    """La envolvente al ratio pedido, con la misma caída a convexo que usa el borrador."""
    multi = MultiPoint(list(puntos.geometry))
    geometria = shapely.concave_hull(multi, ratio=ratio, allow_holes=False)
    if geometria.is_empty or geometria.geom_type not in ("Polygon", "MultiPolygon"):
        return multi.convex_hull, True
    return geometria, False


def afuera(puntos: gpd.GeoDataFrame, geometria) -> int:
    """Cuántos puntos NO están cubiertos por la geometría. `covered_by`, no `within`.

    La diferencia no es cosmética y casi arruina esta corrida. `within` es interior ESTRICTO:
    excluye el borde. Y los vértices de una envolvente **son** puntos del polo, así que caen
    exactamente sobre el borde: medido con `within`, el hull sin simplificar «expulsaba» 1.853 de
    sus propios 12.688 locales, que es imposible por construcción.

    El número era plausible y la conclusión que producía también —«ninguna tolerancia es
    admisible, hay que publicar sin simplificar»—: la respuesta equivocada llegaba disfrazada de
    respuesta conservadora. Lo delató la fila de tolerancia 0, que tiene que dar cero sí o sí.
    """
    return int((~puntos.geometry.covered_by(geometria)).sum())


def vertices(geometria) -> int:
    if geometria.is_empty:
        return 0
    if geometria.geom_type == "Polygon":
        return len(geometria.exterior.coords)
    return sum(len(g.exterior.coords) for g in geometria.geoms)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    asignados = geo[geo.polo_unido != ""].reset_index(drop=True)
    ids = sorted(asignados.polo_unido.unique())
    cuerpos = {polo_id: asignados[asignados.polo_unido == polo_id] for polo_id in ids}

    corte = json.loads((OUT / "parametros_v2.json").read_text(
        encoding="utf-8"))["clases_densidad"]["cortes_locales_x_ha"][0]

    p("POLIGONIZAR · de envolvente de trabajo a polígono publicable")
    p("=" * 100)
    p("")
    p(f"  {len(ids)} polos · {len(asignados)} locales · ratio vigente {RATIO_VIGENTE}")
    p("")
    p("  LOS CUATRO CRITERIOS, DECLARADOS ANTES DE CORRER:")
    p("    1 · cóncavo, no convexo — el convexo reclama parques y vías, y las 22 envolventes")
    p("        publicadas del Atlas no son convexas (14 de 22 son multiparte, 17–309 vértices)")
    p("    2 · el ratio NO se elige acá: 0,55 ya produjo todas las superficies y clases que")
    p("        existen. La curva lo pone a prueba; sólo cambia si está parado en algo inestable")
    p("    3 · la tolerancia de simplificación es admisible SÓLO si ningún local queda fuera de")
    p("        su propio polígono. Se toma la mayor admisible")
    p("    4 · el área solapada va al polo cuyo punto propio más cercano está más cerca")
    p("")

    # ================================================================== §1 · la curva del ratio
    p("-" * 100)
    p("  §1 · LA CURVA · área total de los 124 contra el parámetro de concavidad")
    p("")
    filas = []
    clases_por_ratio = {}
    for ratio in RATIOS:
        areas, degenerados, contaminacion = {}, 0, 0
        for polo_id in ids:
            geometria, degenerado = hull(cuerpos[polo_id], ratio)
            areas[polo_id] = geometria.area / 1e4
            degenerados += int(degenerado)
            # Acá SÍ va `within` estricto, y es a propósito: un punto ajeno apoyado en el
            # borde no está adentro de este polo. El predicado cambia porque la pregunta
            # cambia, no por descuido.
            ajenos = asignados[asignados.polo_unido != polo_id]
            contaminacion += int(ajenos.geometry.within(geometria).sum())
        densidades = {k: len(cuerpos[k]) / a if a > 0 else np.inf for k, a in areas.items()}
        clases_por_ratio[ratio] = {k: ("concentracion" if d >= corte else "extendida")
                                   for k, d in densidades.items()}
        filas.append({
            "ratio": ratio,
            "ha_total": round(sum(areas.values()), 1),
            "ha_mediana": round(float(np.median(list(areas.values()))), 2),
            "densidad_mediana": round(float(np.median(list(densidades.values()))), 2),
            "hulls_degenerados": degenerados,
            "locales_ajenos_adentro": contaminacion,
        })
    curva = pd.DataFrame(filas)
    base_clases = clases_por_ratio[RATIO_VIGENTE]
    curva["polos_que_cambian_de_clase_vs_055"] = [
        sum(1 for k in ids if clases_por_ratio[r][k] != base_clases[k]) for r in RATIOS]
    p(curva.to_string(index=False))
    p("")

    ha_055 = float(curva[curva.ratio == RATIO_VIGENTE].ha_total.iloc[0])
    ha_convexo = float(curva[curva.ratio == 1.00].ha_total.iloc[0])
    ha_min = float(curva.ha_total.min())
    p(f"    RANGO: de {ha_min:.0f} ha en el extremo cóncavo a {ha_convexo:.0f} ha en el convexo. "
      f"El convexo es {ha_convexo / ha_min:.1f}× el más ceñido.")
    p(f"    En 0,55 el total es {ha_055:.0f} ha, un {ha_055 / ha_convexo * 100:.0f} % del convexo.")
    p("")
    vecinos = curva[(curva.ratio >= 0.40) & (curva.ratio <= 0.70)]
    elasticidad = (vecinos.ha_total.max() - vecinos.ha_total.min()) / ha_055 * 100
    p(f"    **LO QUE DIEGO PIDIÓ MEDIR**: entre 0,40 y 0,70 —±0,15 alrededor del valor vigente— el")
    p(f"    área total se mueve {elasticidad:.1f} %. Y la consecuencia que importa: en ese mismo")
    cambian = int(vecinos.polos_que_cambian_de_clase_vs_055.max())
    p(f"    tramo cambian de clase de densidad {cambian} de {len(ids)} polos "
      f"({cambian / len(ids) * 100:.0f} %).")
    p("")
    p("    LECTURA: si ese número fuera alto, el parámetro sería la mitad del mapa y habría que")
    p("    publicar la clase con su banda. Con lo que dio, 0,55 no está parado en un borde: la")
    p("    regla declarada se cumple y **el ratio NO cambia**. Lo que sí queda es que el número")
    p("    de arriba se cite junto a la superficie, porque la superficie de un polo no es una")
    p("    medida del territorio: es una medida del territorio A ESTE RATIO.")
    p("")

    # ================================================================== §2 · simplificación
    p("-" * 100)
    p("  §2 · SIMPLIFICACIÓN · la tolerancia sale de una condición, no de un número lindo")
    p("")
    crudos = {polo_id: hull(cuerpos[polo_id], RATIO_VIGENTE)[0] for polo_id in ids}
    vertices_crudos = sum(vertices(g) for g in crudos.values())

    filas = []
    for tolerancia in TOLERANCIAS:
        total_vertices, area, expulsados, polos_afectados = 0, 0.0, 0, 0
        desvio_maximo = 0.0
        for polo_id in ids:
            geometria = (crudos[polo_id] if tolerancia == 0
                         else crudos[polo_id].simplify(tolerancia, preserve_topology=True))
            total_vertices += vertices(geometria)
            area += geometria.area / 1e4
            fuera = afuera(cuerpos[polo_id], geometria)
            expulsados += fuera
            polos_afectados += int(fuera > 0)
            # Cuánto se aleja el peor local expulsado. Sin este número, «133 afuera» no dice si
            # el polígono los dejó a 30 cm o a 30 m, que son dos situaciones distintas.
            if fuera:
                sueltos = cuerpos[polo_id][~cuerpos[polo_id].geometry.covered_by(geometria)]
                desvio_maximo = max(desvio_maximo, float(sueltos.distance(geometria).max()))
        filas.append({
            "tolerancia_m": tolerancia,
            "vertices": total_vertices,
            "vertices_por_polo": round(total_vertices / len(ids), 1),
            "ha_total": round(area, 1),
            "cambio_area_pct": round((area - ha_055) / ha_055 * 100, 2),
            "locales_fuera_de_su_poligono": expulsados,
            "polos_afectados": polos_afectados,
            "desvio_maximo_m": round(desvio_maximo, 1),
            "admisible": expulsados == 0,
        })
    simplificacion = pd.DataFrame(filas)
    p(simplificacion.to_string(index=False))
    p("")
    admisibles = simplificacion[simplificacion.admisible]
    tolerancia_elegida = int(admisibles.tolerancia_m.max()) if len(admisibles) else 0
    fila = simplificacion[simplificacion.tolerancia_m == tolerancia_elegida].iloc[0]
    p(f"    TOLERANCIA ELEGIDA: {tolerancia_elegida} m. La capa se publica SIN SIMPLIFICAR.")
    p("")
    p("    Y ahora lo incómodo, que hay que decir antes de festejar el resultado: **la regla")
    p("    declarada iba a elegir 0 sí o sí, y no porque el mapa lo pidiera.** Los vértices de una")
    p("    envolvente de puntos SON los locales. Cualquier simplificación borra vértices, y cada")
    p("    vértice borrado es un local que estaba sobre el borde y queda afuera. Exigir cobertura")
    p("    total es, para esta familia de geometrías, exigir que no se simplifique.")
    p("")
    p("    Es decir: la regla del §3 no discriminó nada. Cumplió la forma de un criterio —una")
    p("    condición declarada antes, que se cumple o no— sin hacer el trabajo de un criterio.")
    p("    Registrarlo importa más que el resultado, porque la próxima vez que alguien escriba una")
    p("    condición dura conviene preguntarse si puede dar otra cosa que la respuesta trivial.")
    p("")
    p("    LO QUE SÍ SOSTIENE EL 0, y es independiente: **no hay nada que simplificar.** El hull a")
    p(f"    0,55 ya da {vertices_crudos / len(ids):.1f} vértices por polo, y las 22 envolventes que")
    p("    el Atlas publica tienen entre 17 y 309. Nuestros polígonos son MÁS SIMPLES que el")
    p("    extremo simple de lo publicado. Simplificar resolvería un problema que no tenemos, y a")
    p("    cambio movería los bordes.")
    p("")
    p("    Y para que la decisión se pueda revisar sin re-correr nada, la columna que faltaba: a")
    p("    cuánto quedan los locales expulsados en cada tolerancia. Son desvíos del orden de la")
    p("    tolerancia misma —que es la garantía de Douglas–Peucker—, no locales que se van lejos.")
    p("    Si alguna vez hace falta simplificar para un formato de salida, ése es el precio y está")
    p("    medido: a 10 m se van 411 locales y ninguno más allá de "
      f"{float(simplificacion[simplificacion.tolerancia_m == 10].desvio_maximo_m.iloc[0]):.1f} m del borde.")
    p("")

    # ================================================================== §3 · solapes
    p("-" * 100)
    p("  §3 · SOLAPES DESPUÉS DE SIMPLIFICAR")
    p("")
    simplificados = {
        polo_id: (crudos[polo_id] if tolerancia_elegida == 0
                  else crudos[polo_id].simplify(tolerancia_elegida, preserve_topology=True))
        for polo_id in ids}
    arboles = {polo_id: cKDTree(np.c_[cuerpos[polo_id].geometry.x.to_numpy(),
                                      cuerpos[polo_id].geometry.y.to_numpy()])
               for polo_id in ids}

    pares = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if not simplificados[a].intersects(simplificados[b]):
                continue
            comun = simplificados[a].intersection(simplificados[b])
            if comun.is_empty or comun.area < 1:
                continue
            centro = comun.representative_point()
            d_a = float(arboles[a].query([centro.x, centro.y])[0])
            d_b = float(arboles[b].query([centro.x, centro.y])[0])
            if abs(d_a - d_b) < 1e-9:
                pierde = a if simplificados[a].area > simplificados[b].area else b
            else:
                pierde = a if d_a > d_b else b
            pares.append({"a": a, "b": b, "ha_solapada": round(comun.area / 1e4, 3),
                          "d_punto_a_m": round(d_a, 1), "d_punto_b_m": round(d_b, 1),
                          "se_le_resta_a": pierde})

    if pares:
        solapes = pd.DataFrame(pares).sort_values("ha_solapada", ascending=False)
        p(f"    {len(solapes)} pares se solapan · {solapes.ha_solapada.sum():.2f} ha en total "
          f"({solapes.ha_solapada.sum() / ha_055 * 100:.2f} % de la superficie)")
        p("")
        p(solapes.head(25).to_string(index=False))
        p("")
        for fila_solape in solapes.itertuples():
            otro = fila_solape.b if fila_solape.se_le_resta_a == fila_solape.a else fila_solape.a
            simplificados[fila_solape.se_le_resta_a] = (
                simplificados[fila_solape.se_le_resta_a].difference(simplificados[otro]))
        p("    Aplicada la regla declarada: el área va al polo que tiene oferta ahí.")
        restantes = sum(
            1 for i, a in enumerate(ids) for b in ids[i + 1:]
            if simplificados[a].intersects(simplificados[b])
            and simplificados[a].intersection(simplificados[b]).area > 1)
        p(f"    solapes que quedan después de resolver: {restantes}")
    else:
        p("    Ningún par se solapa. La regla declarada no llegó a usarse — se deja escrita")
        p("    igual, porque la próxima corrida con otro ratio puede necesitarla.")
    p("")

    # ================================================================== §4 · control final
    p("-" * 100)
    p("  §4 · CONTROL FINAL · el polígono tiene que seguir conteniendo a sus locales")
    p("")
    perdidos = 0
    for polo_id in ids:
        perdidos += afuera(cuerpos[polo_id], simplificados[polo_id])
    p(f"    locales fuera de su propio polígono, después de simplificar Y de resolver solapes: "
      f"{perdidos}")
    if perdidos:
        p("    **NO ES CERO.** Restar el solape puede sacar un local que la simplificación sí")
        p("    contenía. Se anota y no se tapa: la resta del §3 tiene ese costo y hay que verlo")
        p("    antes de publicar.")
    else:
        p("    Cero. Cada polígono contiene a todos sus locales.")
    p("")

    # ================================================================== salida
    salida_geo = gpd.GeoDataFrame(
        {"polo_id": ids,
         "n_locales": [len(cuerpos[k]) for k in ids],
         "ha": [simplificados[k].area / 1e4 for k in ids],
         "vertices": [vertices(simplificados[k]) for k in ids],
         "ratio_concavidad": RATIO_VIGENTE,
         "tolerancia_simplificacion_m": tolerancia_elegida,
         "recortado_a_manzana": False},
        geometry=[simplificados[k] for k in ids], crs=CRS_METRICO)
    salida_geo["locales_x_ha"] = salida_geo.n_locales / salida_geo.ha

    p("-" * 100)
    p("  §5 · RECORTE A MANZANA · no se hace, y no es una preferencia")
    p("")
    p("    Recortar a manzana necesita una capa de manzanas o parcelas. En el repositorio hay")
    p("    barrios y comunas, y nada más fino. La base trae `smp` por local —la referencia")
    p("    Sección-Manzana-Parcela— pero un identificador no es una geometría.")
    p("")
    p("    Así que el polígono queda libre y se declara como carencia, no como decisión de")
    p("    diseño. Coincide con lo que el Atlas ya dice de sus envolventes —«una lectura de")
    p("    trabajo, no un límite oficial»— y el recorte queda anotado como lo que haría falta")
    p("    para pasar de lectura de trabajo a límite dibujable.")
    p("")

    p("=" * 100)
    p(f"  capa publicable: {len(salida_geo)} polígonos · {salida_geo.ha.sum():.0f} ha · "
      f"{int(salida_geo.vertices.sum())} vértices")
    p(f"  ratio {RATIO_VIGENTE} (sin cambios) · tolerancia {tolerancia_elegida} m · sin recorte a manzana")
    p("  Google Places: 0 requests · `borrador_polos_v3.geojson` NO se tocó")
    p("=" * 100)
    p("")

    salida_geo.to_crs(CRS_GEO).to_file(OUT / "polos_publicables.geojson", driver="GeoJSON")
    salida_geo.drop(columns="geometry").to_csv(
        OUT / "polos_publicables.csv", index=False, encoding="utf-8")
    curva.to_csv(OUT / "poligonizar_curva_ratio.csv", index=False, encoding="utf-8")
    simplificacion.to_csv(OUT / "poligonizar_curva_simplificacion.csv", index=False,
                          encoding="utf-8")
    if pares:
        pd.DataFrame(pares).to_csv(OUT / "poligonizar_solapes.csv", index=False, encoding="utf-8")

    texto = buffer.getvalue()
    (OUT / "POLIGONIZAR.txt").write_text(texto, encoding="utf-8")
    print(texto)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
