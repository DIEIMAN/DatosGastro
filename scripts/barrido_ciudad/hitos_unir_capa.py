"""Une la capa de hitos: `REFERENTES_2026` manda, y el CSV documental aporta lo que falta.

QUÉ SE UNE Y POR QUÉ EN ESE ORDEN
----------------------------------
`outputs/polos_gastro/REFERENTES_2026/` tiene **169 referentes ya geocodificados con USIG** y
asignados a las envolventes publicadas: 84 Bares Notables del GCBA, 16 Restaurantes Icónicos, 58
MICHELIN con Estrella Verde y 11 mercados/patios. `RECONCILIACION_HITOS.md` ya dictaminó que
**manda** y que de `hitos_documentales_caba.csv` (199 filas) sólo aportan **51**: las otras 148
—bares notables y Michelin— están mejor resueltas allá y se descartan.

Este script no rediscute eso: lo ejecuta, y **deja el descarte anotado fila por fila** en vez de
tirarlo, para que se pueda auditar sin volver a leer los dos archivos.

LAS TRES FORMAS DE APORTAR, QUE NO SON LA MISMA
-----------------------------------------------
  · **capa nueva**   — 50 Best (16), pizzerías emblemáticas (20) y heladerías (5) no existen en
                       REFERENTES. Entran como filas nuevas.
  · **relleno**      — de los 11 mercados de REFERENTES, 9 estaban sin coordenadas. Las
                       direcciones del CSV documental los completan. **No entra una fila nueva: se
                       completa la que ya estaba**, porque duplicar el mercado sería exactamente
                       el trabajo duplicado que la reconciliación vino a evitar.
  · **descarte**     — bares notables y Michelin.

EL NÚMERO QUE NO DA, Y SE DICE ACÁ
-----------------------------------
La reconciliación estimaba que los mercados pasaban de 2/11 a **~9/11**. Medido, no da 9: dos de
las ocho direcciones —San Telmo y Costanera Norte— son de mercados que **ya tenían coordenadas**,
así que no suman cobertura, y una novena —Yiyo el Zeneize— es un mercado que **no está entre los
11** y entra como fila nueva. El script imprime la cobertura que realmente queda.

LAS COORDENADAS SE GEOCODIFICAN CON USIG, COMO TODO LO DEMÁS
--------------------------------------------------------------
Mismo servicio oficial del GCBA que usó `dataset_bares_notables.py`, con el mismo caché y el mismo
filtro por `cod_partido == "caba"` que evita traerse la misma altura de otro partido. Las
coordenadas de REFERENTES **no se recalculan**: si ya está geocodificado, se respeta.

LO QUE NO SE PUEDE GEOCODIFICAR, Y NO SE INVENTA
--------------------------------------------------
Las **20 pizzerías** y las **5 heladerías** vienen con nombre y barrio, sin altura. Entran a la
capa **sin coordenadas y declaradas así**: sirven para la ficha de un polo sólo si alguien les
consigue la dirección. Geocodificar «Guerrín, San Nicolás» al centroide del barrio pondría un hito
en un lugar donde no está, que es peor que no tenerlo.

Google Places: 0 requests. USIG sí —es el geocodificador oficial, gratuito y sin credenciales—.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/hitos_unir_capa.py
"""
from __future__ import annotations

import io
import json
import sys
import unicodedata
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset_bares_notables import CACHE, consultar, limpiar  # noqa: E402

REFERENTES = ROOT / "outputs" / "polos_gastro" / "REFERENTES_2026" / "matriz_referentes_final_2026.csv"
DOCUMENTAL = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "desde_cowork" / "hitos_documentales_caba.csv"
OUT = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "hitos"

# Los tipos del CSV documental que YA están resueltos en REFERENTES_2026 y se descartan.
DUPLICADOS = {"bar_notable", "michelin"}
# Los que aportan, con el nombre que llevan en la capa unida.
APORTAN = {
    "ranking_internacional": "Ranking internacional",
    "pizzeria_emblematica": "Pizzería emblemática",
    "heladeria_historica": "Heladería histórica",
    "mercado_o_patrimonio": "Mercado/patio",
}
# Palabras que no distinguen un mercado de otro y sólo estorban al emparejar.
VACIAS_NOMBRE = {"DE", "DEL", "LA", "EL", "LOS", "LAS", "Y", "GASTRONOMICO", "GASTRONOMICOS"}


def plegar_nombre(nombre: str) -> frozenset[str]:
    """El nombre como conjunto de tokens, para emparejar «Patio Gastronomico Rodrigo Bueno» con
    «Patio Rodrigo Bueno». Mismo criterio que el normalizador de calles: conjunto, no cadena."""
    texto = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode().upper()
    return frozenset(t for t in texto.replace(".", " ").replace(",", " ").split()
                     if t and t not in VACIAS_NOMBRE)


def emparejar(nombre: str, candidatos: dict[frozenset[str], str]) -> str | None:
    """El candidato cuyo nombre contiene o está contenido en éste. None si no hay uno solo.

    Contención y no igualdad, porque las dos fuentes escriben el mismo mercado con distinta
    cantidad de palabras. Si empatan dos, devuelve None: **un emparejamiento ambiguo se reporta,
    no se resuelve por orden de aparición.**
    """
    tokens = plegar_nombre(nombre)
    hallados = [v for k, v in candidatos.items() if k <= tokens or tokens <= k]
    return hallados[0] if len(hallados) == 1 else None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    referentes = pd.read_csv(REFERENTES, comment="#")
    documental = pd.read_csv(DOCUMENTAL)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    p("CAPA DE HITOS UNIFICADA · REFERENTES_2026 manda; el CSV documental completa")
    p("=" * 100)
    p("")
    p(f"  REFERENTES_2026: {len(referentes)} filas, {referentes.latitud.notna().sum()} con coordenadas")
    p(f"  hitos_documentales_caba.csv: {len(documental)} filas")
    p("")

    # ------------------------------------------------------------------ 1 · el descarte, anotado
    duplicadas = documental[documental.tipo.isin(DUPLICADOS)]
    aportantes = documental[documental.tipo.isin(APORTAN)].copy()
    p("-" * 100)
    p("  1 · EL DESCARTE, fila por fila y no como total")
    p("")
    for tipo, n in duplicadas.tipo.value_counts().items():
        equivalente = {"bar_notable": "Bar Notable", "michelin": "MICHELIN"}[tipo]
        tiene = int((referentes.tipo == equivalente).sum())
        p(f"    {tipo:<24} {n:>4} filas descartadas — REFERENTES_2026 tiene {tiene} y está "
          f"geocodificado")
    p(f"    {'TOTAL descartado':<24} {len(duplicadas):>4} filas")
    p("")
    p(f"  Aportan: {len(aportantes)} filas.")
    for tipo, n in aportantes.tipo.value_counts().items():
        p(f"    {tipo:<24} {n:>4}")
    p("")

    # ------------------------------------------------------------------ 2 · relleno de mercados
    mercados_ref = referentes[referentes.tipo == "Mercado/patio"]
    catalogo = {plegar_nombre(f.nombre): f.id for f in mercados_ref.itertuples()}
    p("-" * 100)
    p("  2 · RELLENO DE MERCADOS · se completa la fila que ya estaba, no se agrega una nueva")
    p("")
    p(f"      cobertura ANTES: {int(mercados_ref.latitud.notna().sum())} de {len(mercados_ref)} "
      f"con coordenadas")
    p("")

    relleno = {}
    nuevos_mercados = []
    for fila in aportantes[aportantes.tipo == "mercado_o_patrimonio"].itertuples():
        destino = emparejar(fila.nombre, catalogo)
        if destino is None:
            nuevos_mercados.append(fila.hito_id)
            p(f"      {fila.nombre:<38} → NO está entre los 11: entra como fila nueva")
            continue
        ya = mercados_ref[mercados_ref.id == destino].iloc[0]
        if pd.notna(ya.latitud):
            p(f"      {fila.nombre:<38} → {destino}: ya tenía coordenadas, se respeta "
              f"(no suma cobertura)")
        elif pd.isna(fila.direccion):
            p(f"      {fila.nombre:<38} → {destino}: sigue sin dirección en las dos fuentes")
        else:
            relleno[destino] = fila.direccion
            p(f"      {fila.nombre:<38} → {destino}: se completa con «{fila.direccion}»")
    p("")

    # ------------------------------------------------------------------ 3 · la capa unida
    filas = []
    for fila in referentes.itertuples():
        direccion = relleno.get(fila.id, fila.direccion)
        filas.append({
            "hito_id": fila.id,
            "nombre": fila.nombre,
            "tipo": fila.tipo,
            "reconocimiento": fila.reconocimiento,
            "direccion": direccion,
            "barrio_declarado": fila.barrio_ubicacion,
            "latitud": fila.latitud,
            "longitud": fila.longitud,
            "origen": "REFERENTES_2026" + (" + dirección documental" if fila.id in relleno else ""),
            "fuente_primaria": fila.fuente_primaria,
            "edicion_o_anio": fila.edicion_o_anio,
            "confianza": str(fila.confianza).lower(),
        })
    for fila in aportantes.itertuples():
        if fila.tipo == "mercado_o_patrimonio" and fila.hito_id not in nuevos_mercados:
            continue
        filas.append({
            "hito_id": fila.hito_id,
            "nombre": fila.nombre,
            "tipo": APORTAN[fila.tipo],
            "reconocimiento": fila.distincion,
            "direccion": fila.direccion,
            "barrio_declarado": fila.barrio,
            "latitud": None,
            "longitud": None,
            "origen": "hitos_documentales_caba",
            "fuente_primaria": fila.fuente,
            "edicion_o_anio": fila.anio,
            "confianza": fila.confianza,
        })
    capa = pd.DataFrame(filas)

    # ------------------------------------------------------------------ 4 · geocodificar lo nuevo
    p("-" * 100)
    p("  3 · GEOCODIFICACIÓN CON USIG · sólo lo que no tiene coordenadas y sí tiene dirección")
    p("")
    faltan = capa[capa.latitud.isna() & capa.direccion.notna()]
    p(f"      {len(faltan)} filas para geocodificar. Las que ya venían de REFERENTES no se tocan.")
    p("")
    resueltas, sin_resolver = 0, []
    for indice, fila in faltan.iterrows():
        candidato = consultar(limpiar(fila.direccion), cache)
        if candidato and candidato.get("coordenadas"):
            capa.at[indice, "latitud"] = float(candidato["coordenadas"]["y"])
            capa.at[indice, "longitud"] = float(candidato["coordenadas"]["x"])
            resueltas += 1
        else:
            sin_resolver.append(fila.nombre)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    p(f"      resueltas: {resueltas} de {len(faltan)}")
    if sin_resolver:
        p(f"      sin resolver: {'; '.join(sin_resolver)}")
    p("")

    sin_coordenadas = capa[capa.latitud.isna()]
    p(f"      quedan SIN coordenadas: {len(sin_coordenadas)} filas, y no se inventan.")
    for tipo, n in sin_coordenadas.tipo.value_counts().items():
        p(f"        {tipo:<26} {n:>3}")
    p("")
    p("      Las pizzerías y heladerías vienen con nombre y barrio, sin altura. Ponerlas en el")
    p("      centroide del barrio sería colocar un hito donde no está: entran declaradas y sin punto.")
    p("")

    mercados_final = capa[capa.tipo == "Mercado/patio"]
    p(f"      cobertura de mercados DESPUÉS: {int(mercados_final.latitud.notna().sum())} de "
      f"{len(mercados_final)} — la reconciliación estimaba ~9 de 11.")
    p("")

    # ------------------------------------------------------------------ 5 · salidas
    capa.to_csv(OUT / "hitos_capa_unificada.csv", index=False, encoding="utf-8")
    con_punto = capa[capa.latitud.notna()]
    gpd.GeoDataFrame(
        con_punto.copy(),
        geometry=gpd.points_from_xy(con_punto.longitud, con_punto.latitud),
        crs="EPSG:4326").to_file(OUT / "hitos_capa_unificada.geojson", driver="GeoJSON")

    p("=" * 100)
    p(f"  {len(capa)} hitos en la capa · {int(capa.latitud.notna().sum())} con punto · "
      f"{len(duplicadas)} filas descartadas por duplicado · Google Places: 0 requests")
    p("=" * 100)
    p("")

    salida = buffer.getvalue()
    (OUT / "HITOS_CAPA_UNIFICADA.txt").write_text(salida, encoding="utf-8")
    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
