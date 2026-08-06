"""P078 contra las tres pruebas de CUANDO_DOS_POLOS_SON_UNO.md. La que nunca se le corrió.

POR QUÉ ESTO NO ES CAMBIAR EL MOTIVO
--------------------------------------
La excepción de P078 se pidió por cobertura (79,0 % contra 80 %) y su motivo documental se midió y
se cayó. Esta corrida **no reemplaza ese motivo**: corre por primera vez la prueba que
correspondía desde el principio y nunca se aplicó. La regla es anterior al caso —está en
`CUANDO_DOS_POLOS_SON_UNO.md`, reconstruida de Recoleta, Belgrano y Costanera— así que aplicarla
ahora no es elegir la vara después de ver el resultado.

Lo que sí hay que cuidar: **el veredicto de esta prueba no revive la excepción de cobertura.** Son
dos preguntas distintas. Ésta responde «¿la partición en tres es estable o es del umbral?»; la
otra respondía «¿las tres partes se llevan casi todos los locales?». Una partición puede ser
perfectamente estable y aun así dejar el 21 % afuera.

LA LECTURA, DECLARADA ANTES DE CORRER (R1)
--------------------------------------------
    el nº de partes se mantiene en 3 en un rango ≥ 60 m   → ESTABLE, la partición se sostiene
    el nº cambia dentro de ±40 m del umbral elegido       → ARBITRARIA, P078 entero
    aparecen 4+ piezas de tamaño comparable               → NI 3 NI 1, se reabre

El umbral elegido es 55 m, así que la ventana de la segunda condición es **15–95 m**.

LA GRILLA ES FINA A PROPÓSITO, Y NO ES MOVER NADA
---------------------------------------------------
La lectura está escrita en METROS de rango, no en cantidad de pasos de grilla, así que medirla
con la grilla vieja (40, 55, 70, 80, 120…) daría una resolución que no alcanza: entre 80 y 120 hay
un salto de 40 m, que es justo el ancho de la ventana que hay que evaluar. Se barre cada 5 m.
**Ningún umbral de aceptación cambia**: cambia el instrumento con que se mide, no la vara.

PRUEBA 3 EN PARALELO
---------------------
Las dos columnas —nombre de uso corriente y respaldo documental propio— van escritas, con la
evidencia de calles y de zona publicada al lado. El algoritmo no las decide: las expone.

Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_p078_prueba_estabilidad.py
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
from polos_foco_menor import calle  # noqa: E402
from polos_particion_anada_estructura import MINIMO, componentes  # noqa: E402

POLO = "P078"
UMBRAL_ELEGIDO = 55
GRILLA = tuple(range(20, 301, 5))

# --- la lectura declarada antes de correr
RANGO_ESTABLE_M = 60        # el conteo se mantiene en 3 a lo largo de al menos este rango
VENTANA_M = 40              # ±40 m alrededor del umbral elegido
PARTES_ESPERADAS = 3
COMPARABLE = 0.25           # «tamaño comparable» para la tercera condición


def curva(cuerpo: gpd.GeoDataFrame) -> pd.DataFrame:
    """La curva completa, en el formato de Belgrano: umbral, componentes, tamaños, cobertura."""
    filas = []
    for umbral in GRILLA:
        todas = componentes(cuerpo, umbral)
        partes = [c for c in todas if len(c) >= MINIMO]
        en_partes = sum(len(c) for c in partes)
        filas.append({
            "umbral_m": umbral,
            "n_componentes": len(todas),
            "n_partes": len(partes),
            "tamanos": "; ".join(str(len(c)) for c in todas[:8]),
            "tamanos_partes": "; ".join(str(len(c)) for c in partes),
            "pct_locales": round(en_partes / len(cuerpo) * 100, 1),
        })
    return pd.DataFrame(filas)


def tramo_mas_largo(tabla: pd.DataFrame, conteo: int) -> tuple[int, int, int] | None:
    """El tramo contiguo más largo (en metros) donde `n_partes` vale exactamente `conteo`."""
    mejor, actual = None, []
    for fila in tabla.itertuples():
        if fila.n_partes == conteo:
            actual.append(int(fila.umbral_m))
        else:
            if actual and (mejor is None or actual[-1] - actual[0] > mejor[2]):
                mejor = (actual[0], actual[-1], actual[-1] - actual[0])
            actual = []
    if actual and (mejor is None or actual[-1] - actual[0] > mejor[2]):
        mejor = (actual[0], actual[-1], actual[-1] - actual[0])
    return mejor


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    cuerpo = geo[geo.polo_unido == POLO].reset_index(drop=True)
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)
    nombres_zona = dict(zip(zonas.referencia_id, zonas.nombre))

    tabla = curva(cuerpo)

    p(f"{POLO} CONTRA LAS TRES PRUEBAS DE «CUÁNDO DOS POLOS SON UNO»")
    p("=" * 100)
    p("")
    p("  Esta prueba nunca se le corrió a P078. La regla es anterior al caso, así que correrla no")
    p("  es cambiar el motivo de la excepción: es aplicar por primera vez la vara que correspondía.")
    p("")
    p("  Y NO revive la excepción de cobertura. Son dos preguntas distintas: una partición puede")
    p("  ser estable y dejar igual el 21 % afuera.")
    p("")
    p("  LECTURA DECLARADA ANTES DE CORRER:")
    p(f"    n.º de partes = {PARTES_ESPERADAS} en un rango ≥ {RANGO_ESTABLE_M} m → ESTABLE")
    p(f"    n.º cambia dentro de ±{VENTANA_M} m de {UMBRAL_ELEGIDO} m "
      f"({UMBRAL_ELEGIDO - VENTANA_M}–{UMBRAL_ELEGIDO + VENTANA_M} m) → ARBITRARIA, {POLO} entero")
    p(f"    4+ piezas de tamaño comparable → NI 3 NI 1, se reabre")
    p("")
    p(f"  grilla: {GRILLA[0]}–{GRILLA[-1]} m cada 5 m. La lectura está escrita en metros de rango,")
    p("  así que la grilla vieja no tenía resolución para evaluarla. Ninguna vara cambia.")
    p("")

    p("-" * 100)
    p("  LA CURVA COMPLETA · formato Belgrano")
    p("")
    p(tabla.to_string(index=False))
    p("")

    # --- prueba 2, condición A: ¿hay un rango largo con 3 partes?
    tramo3 = tramo_mas_largo(tabla, PARTES_ESPERADAS)
    p("-" * 100)
    p("  PRUEBA 2 · ESTABILIDAD")
    p("")
    if tramo3:
        inicio, fin, ancho = tramo3
        p(f"    tramo contiguo más largo con {PARTES_ESPERADAS} partes: "
          f"{inicio}–{fin} m  →  **{ancho} m de ancho**")
        p(f"    condición: ≥ {RANGO_ESTABLE_M} m  →  "
          f"{'CUMPLE' if ancho >= RANGO_ESTABLE_M else 'NO CUMPLE'}")
    else:
        inicio = fin = ancho = 0
        p(f"    NUNCA aparecen exactamente {PARTES_ESPERADAS} partes en toda la grilla.")
    p("")

    # --- prueba 2, condición B: ¿el conteo cambia en la ventana de ±40 m?
    ventana = tabla[(tabla.umbral_m >= UMBRAL_ELEGIDO - VENTANA_M)
                    & (tabla.umbral_m <= UMBRAL_ELEGIDO + VENTANA_M)]
    conteos = sorted(ventana.n_partes.unique())
    estable_en_ventana = len(conteos) == 1
    p(f"    ventana ±{VENTANA_M} m ({UMBRAL_ELEGIDO - VENTANA_M}–{UMBRAL_ELEGIDO + VENTANA_M} m): "
      f"n.º de partes toma los valores {conteos}")
    p(f"    condición: no cambia  →  {'CUMPLE' if estable_en_ventana else 'NO CUMPLE'}")
    if not estable_en_ventana:
        cambios = ventana[["umbral_m", "n_partes", "tamanos_partes", "pct_locales"]]
        p("")
        p(cambios.to_string(index=False))
    p("")

    # --- prueba 2, condición C: ¿4+ piezas comparables en algún lado?
    reabre = []
    for fila in tabla.itertuples():
        tamanos = [int(t) for t in fila.tamanos_partes.split("; ") if t]
        if len(tamanos) >= 4 and min(tamanos) / max(tamanos) >= COMPARABLE:
            reabre.append({"umbral_m": fila.umbral_m, "piezas": len(tamanos),
                           "tamanos": fila.tamanos_partes})
    p(f"    4+ piezas de tamaño comparable (mín/máx ≥ {COMPARABLE:.0%}): "
      f"{'SÍ, en ' + str(len(reabre)) + ' umbral(es)' if reabre else 'NO en ningún umbral'}")
    if reabre:
        p(pd.DataFrame(reabre).to_string(index=False))
    p("")

    if reabre:
        veredicto = "SE REABRE"
    elif tramo3 and ancho >= RANGO_ESTABLE_M and estable_en_ventana:
        veredicto = "ESTABLE"
    else:
        veredicto = "ARBITRARIA"
    p(f"    VEREDICTO PRUEBA 2: **{veredicto}**")
    p("")

    # --- prueba 1, de paso: los vacíos entre las tres partes, formato Recoleta
    partes = [c for c in componentes(cuerpo, UMBRAL_ELEGIDO) if len(c) >= MINIMO]
    p("-" * 100)
    p("  PRUEBA 1 · CONTINUIDAD · los vacíos entre las tres partes, formato Recoleta")
    p("")
    vacios = []
    for i in range(len(partes)):
        for j in range(i + 1, len(partes)):
            a, b = cuerpo.iloc[partes[i]], cuerpo.iloc[partes[j]]
            geo_a, _ = envolver(a, PARAMETROS["concave_hull_ratio"])
            geo_b, _ = envolver(b, PARAMETROS["concave_hull_ratio"])
            vacios.append({
                "par": f"S{i + 1}–S{j + 1}",
                "d_envolventes_m": round(geo_a.distance(geo_b), 1),
                "d_entre_puntos_m": round(min(a.geometry.distance(q).min() for q in b.geometry), 1),
            })
    tabla_vacios = pd.DataFrame(vacios)
    p(tabla_vacios.to_string(index=False))
    p("")
    p("    Recoleta unió nueve núcleos con tres pares a 0,0 m y mediana de 25 m. Acá el vacío más")
    p(f"    chico entre partes es de {tabla_vacios.d_entre_puntos_m.min():.0f} m entre puntos.")
    p("    No es la situación de Recoleta: las tres partes están separadas de verdad.")
    p("")

    # --- prueba 3: las dos columnas, con la evidencia al lado
    p("-" * 100)
    p("  PRUEBA 3 · ¿LA DIVISIÓN MEJORA LA LECTURA? · las dos columnas")
    p("")
    filas3 = []
    for orden, indices in enumerate(partes, start=1):
        miembros = cuerpo.iloc[indices]
        geometria, _ = envolver(miembros, PARAMETROS["concave_hull_ratio"])
        solapes = {z.referencia_id: geometria.intersection(z.geometry).area / geometria.area
                   for z in zonas.itertuples() if geometria.intersects(z.geometry)}
        solapes = {k: v for k, v in sorted(solapes.items(), key=lambda x: -x[1]) if v > 0.05}
        calles = miembros.direccion_norm.dropna().map(calle)
        calles = calles[calles.str.len() > 2].value_counts()
        filas3.append({
            "parte": f"S{orden}",
            "locales": len(indices),
            # Separador « · » y no coma: hay nombres de calle con coma adentro y con la coma como
            # separador no se puede saber dónde termina una entrada.
            "calles_dominantes": " · ".join(c.title() for c in calles.head(6).index),
            "con_direccion": f"{miembros.direccion_norm.notna().sum()}/{len(indices)}",
            "zona_publicada": ", ".join(
                f"{nombres_zona.get(k, k)} ({k}) {v:.0%}" for k, v in solapes.items()) or "—",
        })
    tabla3 = pd.DataFrame(filas3)
    for fila in tabla3.itertuples():
        p(f"    {fila.parte} · {fila.locales} locales")
        p(f"      calles dominantes : {fila.calles_dominantes}")
        p(f"      (base de calles)  : {fila.con_direccion} locales con dirección")
        p(f"      zona publicada    : {fila.zona_publicada}")
        p("")
    p("    LÍMITE DE LA LISTA DE CALLES: no hay callejero canónico detrás, así que variantes de")
    p("    una misma calle pueden seguir apareciendo por separado. Es evidencia para un ojo")
    p("    humano, no un recuento por calle, y menos de la mitad de los locales tiene dirección.")
    p("")
    p("    LAS DOS COLUMNAS, para completar a ojo. El algoritmo NO las decide (§5 de")
    p("    CRITERIOS_LECTURA): expone la evidencia y una persona escribe el nombre.")
    p("")
    p("      parte | nombre de uso corriente | respaldo documental propio")
    p("      ------|-------------------------|---------------------------")
    for fila in tabla3.itertuples():
        p(f"      {fila.parte:<5} | {'':<23} | {fila.zona_publicada[:40]}")
    p("")
    p("    Ojo con el respaldo: que las tres caigan sobre R01 Palermo NO es respaldo documental")
    p("    PROPIO de cada parte. R01 respalda al conjunto. Belgrano R sobrevivió con 2 locales")
    p("    porque tenía respaldo propio, no porque cayera adentro de Belgrano.")
    p("")

    salida = buffer.getvalue()
    (OUT / "P078_PRUEBA_ESTABILIDAD.txt").write_text(salida, encoding="utf-8")
    tabla.to_csv(OUT / "p078_curva_estabilidad.csv", index=False, encoding="utf-8")
    tabla3.to_csv(OUT / "p078_prueba3_nombres.csv", index=False, encoding="utf-8")
    tabla_vacios.to_csv(OUT / "p078_vacios_entre_partes.csv", index=False, encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
