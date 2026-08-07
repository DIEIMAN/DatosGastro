"""EL DOSSIER DE MEDICIÓN · una fila por candidato sin zona publicada encima.

PARA QUÉ EXISTE
---------------
Los 62 polos del borrador que **no tienen ninguna zona publicada encima** (4.678 locales) son los
únicos sobre los que el relevamiento puede aportar algo que la curaduría no tenga ya. Este archivo
los describe con lo que ya está calculado, para que la investigación documental salga a buscar
fuentes **sabiendo qué hay medido en cada lugar**.

No es un producto: es un insumo para cruzar. La cartografía está frenada y `polos_publicables.geojson`
queda como INSUMO. Acá **no se agrupa, no se redibuja y no se mueve ningún umbral**: es el estado
actual, descrito.

QUÉ VA EN CADA FILA, Y DE DÓNDE SALE
-------------------------------------
Todo relee salidas ya existentes. Este script **no calcula ninguna decisión nueva**:

    n_locales, ha, densidad, clase       ← borrador_polos_v3.csv
    barrios con conteo, comunas          ← pertenencia_local_polo_v3.csv sobre la base
    calles dominantes                    ← el resolutor de normalizar_calles.py
    % de locales con dirección           ← la base
    hitos adentro                        ← hitos_capa_unificada.geojson
    distancia a la zona publicada        ← envolventes de las 22, medida ENTRE PUNTOS

LAS CUATRO ADVERTENCIAS QUE VIAJAN CON LA TABLA Y NO AL PIE
-------------------------------------------------------------
1. **`calles_dominantes` no es un censo por calle.** Es dónde caen los locales de este polo QUE
   TIENEN DIRECCIÓN, y esa fracción va en la columna de al lado. Un polo con 30 % de direcciones
   nombra sus calles sobre un tercio de sus locales.
2. **`hitos_adentro` mide dónde miran las guías, no dónde hay oferta.** Es el encuadre de
   REFERENTES_2026: son dos geografías distintas, y un polo sin hitos no es un polo sin valor —es
   un polo que esos catálogos no relevaron—. Además 30 hitos de la capa no tienen coordenadas
   —20 pizzerías y 5 heladerías entre ellos— así que el conteo es un piso, no un total.
3. **`d_a_zona_publicada_m` se mide ENTRE PUNTOS**, no entre envolventes, por la regla 4 de
   `CUANDO_DOS_POLOS_SON_UNO`: la distancia entre envolventes puede ser varias veces menor y
   llevar a unir de más.
4. **La superficie es una medida al ratio 0,55** del hull cóncavo. No es un dato del territorio:
   es un dato de esa convención, y la densidad la hereda.

Google Places: 0 requests. No se toca ninguna geometría ni ninguna cifra publicada.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_dossier_medicion.py
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

from borrador_polos_ciudad import (  # noqa: E402
    CRS_METRICO, ENVOLVENTES_22, PARAMETROS, cargar_puntos,
)
from polos_atributos_clases import OUT  # noqa: E402
from normalizar_calles import resolutor_desde  # noqa: E402

HITOS = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "hitos" / "hitos_capa_unificada.geojson"
CALLES_TOP = 6
SOLAPE_MINIMO = 0.02      # el mismo de POLOS_PARA_NOMBRAR: por debajo, la zona apenas roza el polo


def formato_conteo(serie: pd.Series, tope: int | None = None) -> str:
    """«Palermo (210); Villa Crespo (44)». Separador « ; » y no coma: hay nombres con coma."""
    conteos = serie.value_counts()
    if tope is not None:
        conteos = conteos.head(tope)
    return "; ".join(f"{k} ({v})" for k, v in conteos.items())


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    polos = gpd.read_file(OUT / "borrador_polos_v3.geojson").to_crs(CRS_METRICO)
    atributos = pd.read_csv(OUT / "borrador_polos_v3.csv").set_index("polo_id")
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)
    resolutor = resolutor_desde(geo)

    hitos = gpd.read_file(HITOS).to_crs(CRS_METRICO) if HITOS.exists() else None
    if hitos is None:
        print("Falta la capa de hitos: correr antes hitos_unir_capa.py", file=sys.stderr)
        return 1

    asignados = geo[geo.polo_unido != ""].reset_index(drop=True)
    xy = np.c_[asignados.geometry.x.to_numpy(), asignados.geometry.y.to_numpy()]

    # Los puntos de las zonas publicadas, para medir ENTRE PUNTOS y no entre envolventes: un local
    # asignado a cualquiera de las 22 es un punto de «lo publicado».
    en_zona = np.zeros(len(asignados), dtype=bool)
    for zona in zonas.itertuples():
        en_zona |= asignados.geometry.within(zona.geometry).to_numpy()
    arbol_publicado = cKDTree(xy[en_zona]) if en_zona.any() else None

    filas = []
    for polo in polos.itertuples():
        cuerpo = asignados[asignados.polo_unido == polo.polo_id]
        atrib = atributos.loc[polo.polo_id]

        # --- zonas publicadas encima, con los dos porcentajes (igual que POLOS_PARA_NOMBRAR)
        solapes = []
        for zona in zonas.itertuples():
            if not polo.geometry.intersects(zona.geometry):
                continue
            comun = polo.geometry.intersection(zona.geometry).area
            del_polo = comun / polo.geometry.area
            if del_polo < SOLAPE_MINIMO:
                continue
            solapes.append((del_polo, f"{zona.referencia_id} {zona.nombre} "
                                      f"({del_polo:.0%} del polo, "
                                      f"{comun / zona.geometry.area:.0%} de la zona)"))
        solapes.sort(reverse=True)

        con_direccion = cuerpo.direccion_norm.dropna()
        calles = con_direccion.map(resolutor.etiqueta)
        calles = calles[calles.str.len() > 2].value_counts().head(CALLES_TOP)

        adentro = hitos[hitos.geometry.within(polo.geometry)]

        if arbol_publicado is not None:
            propios = np.isin(asignados.index.to_numpy(),
                              cuerpo.index.to_numpy())
            distancias, _ = arbol_publicado.query(xy[propios])
            d_publicada = round(float(distancias.min()), 1)
        else:
            d_publicada = None

        filas.append({
            "polo_id": polo.polo_id,
            "zonas_publicadas_encima": " · ".join(t for _, t in solapes) or "ninguna",
            "n_locales": len(cuerpo),
            "ha": round(atrib.ha, 2),
            "locales_x_ha": round(atrib.locales_x_ha, 3),
            "clase_densidad": atrib.clase_densidad,
            "barrios": formato_conteo(cuerpo.barrio),
            "barrio_principal": cuerpo.barrio.value_counts().index[0] if len(cuerpo) else "",
            "comunas": "; ".join(str(int(c)) for c in sorted(cuerpo.comuna.dropna().unique())),
            "calles_dominantes": "; ".join(f"{c.title()} ({n})" for c, n in calles.items()),
            "pct_locales_con_direccion": round(len(con_direccion) / len(cuerpo) * 100, 1),
            "n_hitos_adentro": len(adentro),
            "hitos_adentro": "; ".join(
                f"{h.nombre} ({h.tipo})" for h in adentro.itertuples()) or "ninguno",
            "d_a_zona_publicada_m": d_publicada,
        })

    tabla = pd.DataFrame(filas)
    dossier = tabla[tabla.zonas_publicadas_encima == "ninguna"].sort_values(
        "n_locales", ascending=False).reset_index(drop=True)

    # ------------------------------------------------------------------ el informe
    p("DOSSIER DE MEDICIÓN · los candidatos sin zona publicada encima")
    p("=" * 110)
    p("")
    p(f"  {len(dossier)} de {len(tabla)} polos del borrador no tienen ninguna zona publicada "
      f"encima: {int(dossier.n_locales.sum())} locales.")
    p("")
    p("  Es el estado actual DESCRITO. No se agrupó, no se redibujó y no se movió ningún umbral.")
    p("  El identificador para cruzar es `polo_id`; el lugar, `barrio_principal` + "
      "`calles_dominantes`.")
    p("")
    p("  CUATRO COLUMNAS QUE SE PUEDEN LEER MAL:")
    p("")
    p("   · calles_dominantes    — dónde caen los locales CON DIRECCIÓN, no un censo por calle.")
    p("   · n_hitos_adentro      — mide dónde miran las guías, no dónde hay oferta. Son dos")
    p("                            geografías distintas (encuadre de REFERENTES_2026). Y es un")
    p("                            PISO: 30 hitos de la capa no tienen coordenadas.")
    p("   · d_a_zona_publicada_m — ENTRE PUNTOS, no entre envolventes (regla 4 de CUANDO_DOS_POLOS).")
    p("   · ha / locales_x_ha    — medidas al ratio 0,55 del hull cóncavo, que es una convención.")
    p("")

    p("-" * 110)
    p("  LA TABLA, resumida. El CSV lleva las columnas largas enteras.")
    p("")
    columnas = ["polo_id", "n_locales", "ha", "locales_x_ha", "clase_densidad",
                "barrio_principal", "comunas", "pct_locales_con_direccion",
                "n_hitos_adentro", "d_a_zona_publicada_m"]
    p(dossier[columnas].to_string(index=False))
    p("")

    p("-" * 110)
    p("  FICHA POR CANDIDATO")
    p("")
    for fila in dossier.itertuples():
        p(f"  {fila.polo_id} · {fila.n_locales} locales · {fila.ha} ha · "
          f"{fila.locales_x_ha} loc/ha ({fila.clase_densidad})")
        p(f"      barrios:  {fila.barrios}")
        p(f"      comunas:  {fila.comunas}")
        p(f"      calles:   {fila.calles_dominantes or '—'}")
        p(f"                (sobre el {fila.pct_locales_con_direccion} % de los locales, "
          f"que son los que tienen dirección)")
        p(f"      hitos:    {fila.hitos_adentro}")
        p(f"      a {fila.d_a_zona_publicada_m} m de la zona publicada más cercana, entre puntos")
        p("")

    p("-" * 110)
    p("  LO QUE CONVIENE MIRAR ANTES DE SALIR A BUSCAR FUENTES")
    p("")
    grandes = dossier[dossier.n_locales >= 100]
    p(f"  · candidatos de 100 locales o más: {len(grandes)}. Son los que más pesan si se confirman.")
    for fila in grandes.itertuples():
        p(f"      {fila.polo_id:<8} {fila.n_locales:>4} locales · {fila.barrio_principal}")
    p("")

    flojos = dossier[dossier.pct_locales_con_direccion < 50]
    p(f"  · candidatos donde MENOS de la mitad tiene dirección: {len(flojos)}. En ésos las calles")
    p("    se apoyan en poca evidencia y no alcanzan para nombrar el lugar solas.")
    p("")

    sin_hitos = dossier[dossier.n_hitos_adentro == 0]
    p(f"  · candidatos sin ningún hito adentro: {len(sin_hitos)} de {len(dossier)}. **No es un")
    p("    veredicto sobre ellos**: es que los catálogos de distinciones no relevaron esas zonas.")
    p("")

    lejos = dossier.nlargest(10, "d_a_zona_publicada_m")
    p("  · los 10 más lejos de todo lo publicado, entre puntos — donde el Atlas no llega:")
    for fila in lejos.itertuples():
        p(f"      {fila.polo_id:<8} {fila.d_a_zona_publicada_m:>8.0f} m · {fila.n_locales:>4} "
          f"locales · {fila.barrio_principal}")
    p("")

    dossier.to_csv(OUT / "DOSSIER_MEDICION_CANDIDATOS.csv", index=False, encoding="utf-8")

    p("=" * 110)
    p(f"  {len(dossier)} candidatos · {int(dossier.n_locales.sum())} locales · "
      f"{dossier.ha.sum():.0f} ha · {int(dossier.n_hitos_adentro.sum())} hitos "
      f"· Google Places: 0 requests")
    p("=" * 110)
    p("")

    salida = buffer.getvalue()
    (OUT / "DOSSIER_MEDICION_CANDIDATOS.txt").write_text(salida, encoding="utf-8")
    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
