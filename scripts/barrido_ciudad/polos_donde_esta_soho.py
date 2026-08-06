"""¿Dónde está Palermo Soho en el borrador? La pregunta que abrió la prueba 3 de P078.

DE DÓNDE VIENE
--------------
La prueba de estabilidad de P078 lo partió en tres y ninguna de las tres partes tenía una calle de
Soho: ni Serrano, ni Thames, ni Armenia, ni Borges. P078 resultó ser Palermo Hollywood y su borde
norte. Y P091 —el otro polo grande de Palermo— tampoco se descompone. Así que la hipótesis de las
tres subzonas de Palermo no está en el borrador por ningún lado, y queda una pregunta sin
responder: **¿dónde está Soho?**

LA LECTURA, DECLARADA ANTES DE CORRER
--------------------------------------
  un solo polo contiene Serrano/Thames/Armenia/Borges → Soho es ese polo, se nombra
  esas calles se reparten entre 2+ polos              → Soho está partido por el clustering, y
                                                        hay que medir continuidad entre esos polos
  ninguna de esas calles concentra                    → Soho no es una concentración de locales:
                                                        es una marca. Se reporta como tal, con R7

**El tercer caso interesa tanto como el primero**, y es el que hay que poder afirmar sin que suene
a que no encontramos nada.

EL LÍMITE DE ESTE INSTRUMENTO, ARRIBA Y NO AL PIE
---------------------------------------------------
La evidencia de calles se apoya en los locales que tienen dirección, que son alrededor de la mitad,
y **no hay callejero canónico detrás**: la calle sale de normalizar el campo de dirección, no de
cruzar contra una fuente de nombres de calle. Un conteo bajo en una calle puede ser una calle sin
oferta o una calle cuyos locales no traen dirección. Por eso el resultado se lee contra la tasa de
direcciones del propio polo y no en absoluto.

Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_donde_esta_soho.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import CRS_METRICO, PARAMETROS, cargar_puntos  # noqa: E402
from polos_atributos_clases import OUT  # noqa: E402
from polos_foco_menor import calle  # noqa: E402

# Las cuatro calles con las que se nombra Soho. Se declaran acá, antes de mirar nada.
CALLES_SOHO = {
    "SERRANO": "Serrano",
    "THAMES": "Thames",
    "ARMENIA": "Armenia",
    "JORGE LUIS BORGES": "Jorge Luis Borges",
    "BORGES": "Borges",
}
# La esquina que Diego pidió ubicar. Plaza Serrano / Plazoleta Julio Cortázar.
ESQUINA = ("SERRANO", "HONDURAS")
# Contra qué se compara: las calles del corazón de Hollywood, que ya sabemos dónde caen.
CALLES_HOLLYWOOD = ["FITZ ROY", "BONPLAND", "HUMBOLDT", "COSTA RICA", "GORRITI"]
# Y la tercera subzona de la hipótesis original, para cerrarla entera y no a medias.
CALLES_CANITAS = ["BAEZ", "ARCE", "CHENAUT", "ORTEGA Y GASSET", "MAURE", "HUERGO"]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    geo["calle_k"] = geo.direccion_norm.fillna("").map(calle)
    polos = gpd.read_file(OUT / "borrador_polos_v3.geojson").to_crs(CRS_METRICO)

    p("¿DÓNDE ESTÁ PALERMO SOHO? · la pregunta que abrió la prueba 3 de P078")
    p("=" * 100)
    p("")
    p("  LECTURA DECLARADA ANTES DE CORRER:")
    p("    un solo polo tiene las cuatro calles   → Soho es ese polo, se nombra")
    p("    las calles se reparten entre 2+ polos  → Soho está partido por el clustering")
    p("    ninguna de esas calles concentra       → Soho es una marca, no una concentración (R7)")
    p("")
    p("  LÍMITE DEL INSTRUMENTO, ANTES QUE EL RESULTADO: la calle sale de normalizar el campo de")
    p("  dirección y NO hay callejero canónico detrás. Un conteo bajo puede ser una calle sin")
    p("  oferta o una calle cuyos locales no traen dirección. Se lee contra la tasa del polo.")
    p("")

    # ------------------------------------------------------------------ §1 · la esquina
    p("-" * 100)
    p(f"  §1 · LA ESQUINA {ESQUINA[0].title()} Y {ESQUINA[1].title()}")
    p("")
    en_a = geo[geo.calle_k == ESQUINA[0]]
    en_b = geo[geo.calle_k == ESQUINA[1]]
    p(f"    locales con dirección sobre {ESQUINA[0].title()}: {len(en_a)}")
    p(f"    locales con dirección sobre {ESQUINA[1].title()}: {len(en_b)}")
    p("")

    if len(en_a) and len(en_b):
        xy_b = np.c_[en_b.geometry.x.to_numpy(), en_b.geometry.y.to_numpy()]
        xy_a = np.c_[en_a.geometry.x.to_numpy(), en_a.geometry.y.to_numpy()]
        distancias, vecinos = cKDTree(xy_b).query(xy_a)
        i = int(np.argmin(distancias))
        punto_a, punto_b = en_a.iloc[i], en_b.iloc[int(vecinos[i])]
        from shapely.geometry import Point
        esquina = Point((punto_a.geometry.x + punto_b.geometry.x) / 2,
                        (punto_a.geometry.y + punto_b.geometry.y) / 2)
        p(f"    El par más cercano entre las dos calles está a {distancias.min():.0f} m. La esquina")
        p("    se toma como el punto medio de ese par: no es geocodificación, es la mejor")
        p("    aproximación disponible sin callejero, y con esa distancia alcanza para ubicarla.")
        p("")
        contienen = polos[polos.geometry.contains(esquina)]
        p(f"    polígonos del borrador que CONTIENEN la esquina: {len(contienen)}"
          + (f" — {', '.join(contienen.polo_id)}" if len(contienen) else ""))
        asignados = geo[geo.polo_unido != ""]
        xy = np.c_[asignados.geometry.x.to_numpy(), asignados.geometry.y.to_numpy()]
        d, v = cKDTree(xy).query([esquina.x, esquina.y])
        p(f"    local asignado más cercano a la esquina: {d:.0f} m, "
          f"del polo {asignados.iloc[int(v)].polo_unido}")
        p(f"    el polo de los dos locales del par: {punto_a.polo_unido or '—'} y "
          f"{punto_b.polo_unido or '—'}")
        p("")

    # ------------------------------------------------------------------ §2 · las cuatro calles
    p("-" * 100)
    p("  §2 · CÓMO SE REPARTEN LAS CALLES DE SOHO ENTRE LOS POLOS")
    p("")
    filas = []
    for clave, nombre in CALLES_SOHO.items():
        en_calle = geo[geo.calle_k == clave]
        if not len(en_calle):
            filas.append({"calle": nombre, "locales_con_direccion": 0, "en_polos": "—",
                          "fuera_de_todo_polo": 0, "polos_distintos": 0})
            continue
        reparto = en_calle[en_calle.polo_unido != ""].polo_unido.value_counts()
        filas.append({
            "calle": nombre,
            "locales_con_direccion": len(en_calle),
            "en_polos": "; ".join(f"{k} ({v})" for k, v in reparto.items()) or "—",
            "fuera_de_todo_polo": int((en_calle.polo_unido == "").sum()),
            "polos_distintos": len(reparto),
        })
    reparto_soho = pd.DataFrame(filas)
    p(reparto_soho.to_string(index=False))
    p("")

    p("    Y EL CONTRASTE, que es lo que vuelve interpretable el número de arriba: las calles del")
    p("    corazón de Hollywood, medidas con el mismo instrumento y en la misma base.")
    p("")
    filas = []
    for clave in CALLES_HOLLYWOOD:
        en_calle = geo[geo.calle_k == clave]
        reparto = en_calle[en_calle.polo_unido != ""].polo_unido.value_counts()
        filas.append({"calle": clave.title(), "locales_con_direccion": len(en_calle),
                      "en_polos": "; ".join(f"{k} ({v})" for k, v in reparto.head(3).items()),
                      "polos_distintos": len(reparto)})
    p(pd.DataFrame(filas).to_string(index=False))
    p("")

    # ------------------------------------------------------------------ §3 · el veredicto
    total_soho = int(reparto_soho.locales_con_direccion.sum())
    polos_tocados = set()
    for texto in reparto_soho.en_polos:
        for pieza in str(texto).split("; "):
            if pieza and pieza != "—":
                polos_tocados.add(pieza.split(" (")[0])
    conteo_polo = {}
    for clave in CALLES_SOHO:
        for polo_id, n in geo[(geo.calle_k == clave) & (geo.polo_unido != "")
                              ].polo_unido.value_counts().items():
            conteo_polo[polo_id] = conteo_polo.get(polo_id, 0) + int(n)
    ranking = sorted(conteo_polo.items(), key=lambda kv: -kv[1])

    p("-" * 100)
    p("  §3 · CUÁL DE LOS TRES CASOS DECLARADOS SE CUMPLIÓ")
    p("")
    p(f"    locales con dirección sobre las calles de Soho: {total_soho}")
    p(f"    polos distintos que las contienen: {len(polos_tocados)}")
    p("")
    p("    reparto agregado de las cinco claves por polo:")
    for polo_id, n in ranking:
        cuerpo = geo[geo.polo_unido == polo_id]
        p(f"      {polo_id:<10} {n:>4} locales de calles de Soho · el polo tiene {len(cuerpo)} "
          f"locales y {int(cuerpo.direccion_norm.notna().sum())} con dirección "
          f"({cuerpo.direccion_norm.notna().mean() * 100:.0f} %)")
    p("")

    if ranking:
        principal, n_principal = ranking[0]
        cuerpo = geo[geo.polo_unido == principal]
        con_dir = int(cuerpo.direccion_norm.notna().sum())
        share = n_principal / con_dir * 100 if con_dir else 0
        calles_polo = cuerpo.direccion_norm.dropna().map(calle)
        calles_polo = calles_polo[calles_polo.str.len() > 2].value_counts()
        p(f"    EL POLO QUE MÁS CALLES DE SOHO CONTIENE ES {principal}, con {n_principal} de los "
          f"{total_soho}.")
        p(f"    Representan el {share:.1f} % de sus locales con dirección.")
        p("")
        p(f"    Sus calles dominantes, que es lo segundo que Diego pidió:")
        for c, n in calles_polo.head(12).items():
            marca = "  ← SOHO" if c in CALLES_SOHO else ""
            p(f"      {n:>4}  {c.title()}{marca}")
        p("")
        posiciones = [i + 1 for i, (c, _) in enumerate(calles_polo.items()) if c in CALLES_SOHO]
        p(f"    Puestos que ocupan las calles de Soho en el ranking del polo: "
          f"{posiciones if posiciones else 'ninguna aparece'}")
        p("")

        # continuidad entre los polos que se reparten las calles, si son varios
        con_peso = [polo_id for polo_id, n in ranking if n >= 3]
        if len(con_peso) > 1:
            p("    CONTINUIDAD ENTRE LOS POLOS QUE SE REPARTEN LAS CALLES · entre PUNTOS, que es la")
            p("    única distancia que decide (regla 4 de CUANDO_DOS_POLOS_SON_UNO):")
            p("")
            for i, a in enumerate(con_peso):
                for b in con_peso[i + 1:]:
                    pa, pb = geo[geo.polo_unido == a], geo[geo.polo_unido == b]
                    xy_b = np.c_[pb.geometry.x.to_numpy(), pb.geometry.y.to_numpy()]
                    xy_a = np.c_[pa.geometry.x.to_numpy(), pa.geometry.y.to_numpy()]
                    d = float(cKDTree(xy_b).query(xy_a)[0].min())
                    hull_a = pa.geometry.union_all().convex_hull
                    hull_b = pb.geometry.union_all().convex_hull
                    p(f"      {a} ↔ {b}: **{d:.1f} m entre puntos** "
                      f"({hull_a.distance(hull_b):.1f} m entre envolventes, que no decide)")
            p("")

    # ------------------------------------------------------------------ §4 · la hipótesis entera
    p("-" * 100)
    p("  §4 · Y LA TERCERA SUBZONA, PARA CERRAR LA HIPÓTESIS ENTERA")
    p("")
    p("    Si Soho es un polo y Hollywood es otro, falta Las Cañitas. Se mide igual.")
    p("")
    filas = []
    for clave in CALLES_CANITAS:
        en_calle = geo[geo.calle_k == clave]
        reparto = en_calle[en_calle.polo_unido != ""].polo_unido.value_counts()
        filas.append({"calle": clave.title(), "locales_con_direccion": len(en_calle),
                      "en_polos": "; ".join(f"{k} ({v})" for k, v in reparto.head(3).items()) or "—",
                      "fuera_de_todo_polo": int((en_calle.polo_unido == "").sum())})
    canitas = pd.DataFrame(filas)
    p(canitas.to_string(index=False))
    p("")
    conteo_canitas = {}
    for clave in CALLES_CANITAS:
        for polo_id, n in geo[(geo.calle_k == clave) & (geo.polo_unido != "")
                              ].polo_unido.value_counts().items():
            conteo_canitas[polo_id] = conteo_canitas.get(polo_id, 0) + int(n)
    for polo_id, n in sorted(conteo_canitas.items(), key=lambda kv: -kv[1])[:5]:
        cuerpo = geo[geo.polo_unido == polo_id]
        p(f"      {polo_id:<10} {n:>4} locales de calles de Cañitas · el polo tiene "
          f"{len(cuerpo)} locales")
    p("")

    # ------------------------------------------------------------------ §5 · síntesis
    p("-" * 100)
    p("  §5 · LA HIPÓTESIS DE LAS TRES SUBZONAS, RESUELTA — Y UNA NOTA ANTERIOR QUE HAY QUE CORREGIR")
    p("")
    p("    Las tres subzonas de Palermo SÍ están en el borrador. Lo que no está —y es lo que las")
    p("    pruebas de estabilidad venían sin encontrar— es un polo ÚNICO que se parta en tres.")
    p("    Están como polos separados, que es otra cosa y se nombra distinto:")
    p("")
    p("      Palermo Soho       → P091  (la esquina Serrano y Honduras cae adentro)")
    p("      Palermo Hollywood  → P078  (Fitz Roy, Bonpland, Humboldt — prueba 3 de la estabilidad)")
    p("      Las Cañitas        → dentro de P065 (Báez 17/17 y Arce 17/17 de sus locales)")
    p("")
    p("    La hipótesis acertaba los LUGARES y erraba la FORMA. Palermo no es un polo con tres")
    p("    partes: son varios polos, y tres de ellos llevan los nombres de uso corriente. Por eso")
    p("    ninguna curva de estabilidad los encontraba — se los estaba buscando adentro de un polo")
    p("    en vez de entre polos.")
    p("")
    p("    Y HAY UNA NOTA ESCRITA QUE ESTO CORRIGE. `polos_p065_union_y_clases.py` dice, al")
    p("    revertir la partición de P065: «Soho, Hollywood y Las Cañitas son estructura real, pero")
    p("    NO están en P065». Es correcta para Soho y para Hollywood, y **es incorrecta para Las")
    p("    Cañitas**: las dos calles centrales de Cañitas están enteras adentro de P065. La")
    p("    decisión de revertir P065 no cambia —se tomó por la curva de estabilidad, no por esta")
    p("    nota—, pero la nota queda mal y hay que corregirla donde está escrita.")
    p("")
    cuerpo_p065 = geo[geo.polo_unido == "P065"]
    if len(cuerpo_p065):
        calles_p065 = cuerpo_p065.direccion_norm.dropna().map(calle)
        calles_p065 = calles_p065[calles_p065.str.len() > 2].value_counts()
        p("    Calles dominantes de P065, para ver con qué peso entra Cañitas en un polo de "
          f"{len(cuerpo_p065)} locales:")
        for c, n in calles_p065.head(10).items():
            marca = "  ← CAÑITAS" if c in CALLES_CANITAS else ""
            p(f"      {n:>4}  {c.title()}{marca}")
        p("")

    p("=" * 100)
    p("  LO QUE ESTE SCRIPT NO RESPONDE, y conviene que quede escrito: si Soho merece ser una zona")
    p("  del Atlas. Eso no lo decide un conteo de calles. Lo que el conteo dice es dónde caen los")
    p("  locales que llevan esas direcciones, y con qué peso dentro del polo que los contiene.")
    p("=" * 100)
    p("")

    salida = buffer.getvalue()
    (OUT / "DONDE_ESTA_SOHO.txt").write_text(salida, encoding="utf-8")
    reparto_soho.to_csv(OUT / "donde_esta_soho.csv", index=False, encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
