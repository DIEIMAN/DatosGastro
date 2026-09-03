"""El `foco_menor`: cómo se registra un foco secundario que NO llega a subzona.

QUÉ PROBLEMA RESUELVE
----------------------
P103 San Telmo pasó la regla de partes de Belgrano con dos piezas de 290 y 44 locales. Pasarla no
alcanza para publicarse como polo con partes, y la decisión fue **no publicarlo como subzona** por
tres motivos, de los cuales manda el tercero:

  1. El Atlas publica R03 San Telmo como **«Polo»** a secas, sin partes. No hay respaldo documental
     para una división.
  2. Una asimetría de 15 % (290 contra 44) es un satélite, no una parte. En el vocabulario del
     Atlas las partes son piezas comparables y con nombre —Soho/Hollywood/Cañitas,
     Barrio Chino/Bajo Belgrano/Belgrano R—; Belgrano dio 107/82/23 y por eso pasó.
  3. **Falla la condición 3 de la regla de Belgrano: el foco no tiene nombre de uso corriente.**

POR QUÉ ESTE CAMPO NO LLEVA UMBRAL NUMÉRICO, Y ES A PROPÓSITO
---------------------------------------------------------------
La tentación era fijar una razón mínima entre la pieza chica y la grande. **No se hace, porque el
número no separa los casos:** Belgrano —el precedente publicado, con tres partes— tiene 23/107 =
21,5 %, y P103 tiene 44/290 = 15,2 %. Cualquier corte que deje afuera a P103 por proporción deja
a Belgrano a 6 puntos de caerse también. La proporción es evidencia, no criterio.

Lo que separa los casos es la condición 3, que **no la evalúa un algoritmo** (§5 de
CRITERIOS_LECTURA). Así que este campo registra una **decisión humana** y la acompaña de la
evidencia medible que la sostiene. El script calcula la evidencia; el veredicto está declarado
abajo, con su motivo, y se lee como lo que es: una decisión registrada.

Y el foco se describe **por sus calles, no por un nombre**. Ponerle nombre sería justamente lo que
la condición 3 dice que no se puede hacer: si tuviera nombre de uso corriente, sería subzona.

Google Places: 0 requests. No se toca ninguna cifra publicada.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_foco_menor.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import (  # noqa: E402
    CRS_METRICO, ENVOLVENTES_22, PARAMETROS, cargar_puntos,
)
from polos_atributos_clases import OUT  # noqa: E402
from polos_particion_anada_estructura import MINIMO, componentes  # noqa: E402
# El normalizador vivía acá adentro por accidente histórico —éste fue el primer script que lo
# necesitó— y ese domicilio es parte de por qué se parchó caso por caso cuatro veces. Ahora vive en
# `normalizar_calles.py`. Se reexporta para no romper a quien lo importaba de acá.
from normalizar_calles import (  # noqa: E402,F401
    ABREVIATURAS_DE_NOMBRE, CONECTORES_COLA, CPA, MARCADORES, MARCADORES_PAREADOS,
    ResolutorDeCalles, calle, clave_calle, reparar_mojibake, resolutor_desde,
)

# Los polos con partes aceptadas por `polos_partes_nombrables.py`, con el umbral adoptado.
# Se lee del resumen para no repetir el barrido y para que un cambio allá llegue solo.
RESUMEN = OUT / "partes_nombrables_resumen.csv"

# --- LAS DECISIONES REGISTRADAS. No las calcula el script: las tomó una persona, y acá quedan
# con su motivo para que se puedan discutir sin releer una conversación.
DECISIONES = {
    "P103": {
        "resuelve": "mencion",
        "motivo": (
            "El Atlas publica R03 San Telmo como «Polo» sin partes; la asimetría 290/44 es un "
            "satélite y no una pieza comparable; y falla la condición 3 — el foco no tiene "
            "nombre de uso corriente."
        ),
    },
}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)
    resumen = pd.read_csv(RESUMEN)
    aceptados = resumen[resumen.veredicto == "PARTES ESTABLES"]
    # Sobre toda la base, no sobre el foco: la etiqueta de una calle no puede depender de en qué
    # recorte se la esté mirando.
    resolutor = resolutor_desde(geo)

    p("FOCO MENOR · un foco secundario que no llega a subzona")
    p("=" * 100)
    p("")
    p("  Este campo NO tiene umbral numérico, y es a propósito. Belgrano —publicado con tres")
    p("  partes— tiene una pieza chica de 23 contra 107 = 21,5 %. P103 tiene 44 contra 290 =")
    p("  15,2 %. Seis puntos separan al precedente publicado del caso que se rechaza: la")
    p("  proporción no puede ser el criterio. Lo que decide es la condición 3 —nombre de uso")
    p("  corriente o respaldo documental—, que no la evalúa un algoritmo.")
    p("")
    p("  El script calcula la evidencia. El veredicto está declarado en DECISIONES, con motivo.")
    p("")

    filas = []
    for polo in aceptados.itertuples():
        cuerpo = geo[geo.polo_unido == polo.polo_id]
        partes = [c for c in componentes(cuerpo, int(polo.umbral)) if len(c) >= MINIMO]
        if len(partes) < 2:
            continue
        cuerpo_principal = cuerpo.iloc[partes[0]]
        for indices in partes[1:]:
            foco = cuerpo.iloc[indices]
            proporcion = len(foco) / len(cuerpo_principal)
            # Sobre cuántos locales se apoya la evidencia de calles. Va al lado del resultado y no
            # en una nota: la mitad de este foco no tiene dirección, y una línea de ficha que diga
            # «sobre Chacabuco» tiene que dejar ver que sale de 24 locales y no de 44.
            con_direccion = int(foco.direccion_norm.notna().sum())
            calles = foco.direccion_norm.dropna().map(resolutor.etiqueta)
            calles = calles[calles.str.len() > 2].value_counts()
            geometria = foco.geometry.union_all().convex_hull
            solapes = {z.referencia_id: geometria.intersection(z.geometry).area / geometria.area
                       for z in zonas.itertuples() if geometria.intersects(z.geometry)}
            solapes = {k: v for k, v in sorted(solapes.items(), key=lambda x: -x[1]) if v > 0.05}
            decision = DECISIONES.get(polo.polo_id, {})
            filas.append({
                "polo_id": polo.polo_id,
                "foco_menor": True,
                "foco_locales": len(foco),
                "foco_pct_del_polo": round(len(foco) / len(cuerpo) * 100, 1),
                "foco_proporcion_vs_cuerpo": round(proporcion, 3),
                "foco_calles": "; ".join(
                    f"{c.title()} ({n})" for c, n in calles.head(5).items()),
                "foco_locales_con_direccion": con_direccion,
                "foco_pct_con_direccion": round(con_direccion / len(foco) * 100, 1),
                "foco_barrios": "; ".join(
                    f"{b} ({n})" for b, n in foco.barrio.value_counts().head(3).items()),
                "foco_zona_publicada": "; ".join(f"{k} {v:.0%}" for k, v in solapes.items()) or "—",
                "resuelve": decision.get("resuelve", "SIN DECISION REGISTRADA"),
                "motivo": decision.get("motivo", ""),
            })

    tabla = pd.DataFrame(filas)
    p("-" * 100)
    p("  LA EVIDENCIA")
    p("")
    for fila in tabla.itertuples():
        p(f"  {fila.polo_id}")
        p(f"    foco de {fila.foco_locales} locales · {fila.foco_pct_del_polo} % del polo · "
          f"{fila.foco_proporcion_vs_cuerpo:.0%} del cuerpo principal")
        p(f"    calles: {fila.foco_calles}")
        p(f"      (sobre {fila.foco_locales_con_direccion} de {fila.foco_locales} locales con "
          f"dirección · {fila.foco_pct_con_direccion} %)")
        p(f"    barrios: {fila.foco_barrios}")
        p(f"    zona publicada encima: {fila.foco_zona_publicada}")
        p(f"    RESUELVE: {fila.resuelve}")
        p(f"    motivo: {fila.motivo}")
        p("")

    p("-" * 100)
    p("  LA LÍNEA DE FICHA, para el polo que se resuelve como mención")
    p("")
    p("  El foco se describe por sus calles y NO se le pone nombre: ponerle nombre sería hacer")
    p("  justamente lo que la condición 3 dice que no corresponde. Si tuviera nombre de uso")
    p("  corriente, sería subzona.")
    p("")
    lineas = []
    for fila in tabla[tabla.resuelve == "mencion"].itertuples():
        calles_top = [c.split(" (")[0] for c in fila.foco_calles.split("; ")[:3]]
        linea = (f"Hay un foco menor de {fila.foco_locales} locales sobre "
                 f"{', '.join(calles_top[:-1])} y {calles_top[-1]}, separado del cuerpo principal. "
                 f"No se publica como subzona: no tiene nombre de uso corriente.")
        lineas.append({"polo_id": fila.polo_id, "linea_de_ficha": linea})
        p(f"  {fila.polo_id}:")
        p(f"    «{linea}»")
        p(f"    base de las calles: {fila.foco_locales_con_direccion} de {fila.foco_locales} "
          f"locales tienen dirección ({fila.foco_pct_con_direccion} %). Las calles nombran dónde")
        p("    está el foco; NO son un recuento de oferta por calle y no se pueden leer así.")
        p("")
    p("  La redacción final la reescribe una persona —§2 de FICHA_DE_POLO_ENRIQUECIMIENTO: el")
    p("  generador produce datos y viñetas, no prosa—. Esto es la viñeta.")
    p("")

    if len(lineas):
        tabla = tabla.merge(pd.DataFrame(lineas), on="polo_id", how="left")

    p("=" * 100)
    p(f"  {len(tabla)} foco(s) menor(es) registrado(s). Ninguno se publica como subzona.")
    p("=" * 100)
    p("")

    salida = buffer.getvalue()
    (OUT / "FOCO_MENOR.txt").write_text(salida, encoding="utf-8")
    tabla.to_csv(OUT / "polos_foco_menor.csv", index=False, encoding="utf-8")

    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
