"""Los cinco bordes de la ronda 3, resueltos con el callejero oficial y no por suposición.

QUÉ HACE
--------
Cinco direcciones caen sobre límites de barrio y dos fuentes las ponen en barrios distintos. El
precedente de **La Academia** —el catálogo oficial la consigna en Comuna 5 con domicilio en Av.
Callao 368, que no está en Comuna 5— dice que el campo `barrio`/`comuna` del catálogo no es
confiable acá.

Se resuelven con **dos consultas independientes a USIG**:

    normalizar    → el punto (lat/lon) de la dirección, filtrando por `cod_partido == caba`
    datos_utiles  → barrio y comuna DEL PUNTO, que es la pregunta que importa

Y con una **tercera lectura offline**: el polígono de barrios del GCBA que ya está en el
repositorio. Tres respuestas que coinciden valen más que una.

LO QUE ESTE SCRIPT NO HACE
--------------------------
No resuelve la disputa editorial. USIG dice a qué barrio **administrativo** pertenece la puerta;
que La Nación titule «un clásico de Saavedra» sigue siendo cierto como uso. Lo que se corrige es
el campo de la matriz, no la cita.

Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/usig_bordes_ronda_3.py
"""
from __future__ import annotations

import io
import json
import sys
import time
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset_bares_notables import consultar, limpiar  # noqa: E402
from polos_soporte import CRS_GEOGRAFICO, sin_tildes  # noqa: E402

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT = BARRIDO / "seis_vias"
CACHE = BARRIDO / "dataset_bares_notables" / "_cache_usig.json"
CACHE_DATOS = BARRIDO / "seis_vias" / "_cache_usig_datos_utiles.json"
BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"

DATOS_UTILES = "https://ws.usig.buenosaires.gob.ar/datos_utiles/"
PAUSA_S = 0.35

# Los cinco bordes, con las dos atribuciones enfrentadas tal como llegan. Se transcriben acá y no
# se parsean del prosa: son cinco y son justamente los que no hay que decidir solos.
BORDES = [
    ("La Escuela", "Manuela Pedraza 2803",
     "catálogo Bares Notables: Núñez, Comuna 13",
     "La Nación: «un clásico de Saavedra»; La Comuna 12: a metros de Saavedra y Coghlan",
     "decide la única vía B de Núñez (Z41)"),
    ("La Mezzetta", "Av. Alvarez Thomas 1321",
     "Canal 26 / El Cronista: Villa Ortúzar",
     "esquina de Av. de los Incas, borde con Chacarita; el GCBA la da en Álvarez Thomas 1311",
     "decide si la Pizzería Emblemática cuenta para Z44 Villa Ortúzar o para R09 Chacarita"),
    ("Vereda Adentro", "11 de Septiembre 3201",
     "Ohlalá: Núñez", "El Cronista: Saavedra", "adscripción de un local del corredor norte"),
    ("Corte Comedor", "Av. Olazabal 1391",
     "Time Out: Núñez", "la altura de Olazábal corresponde a Belgrano",
     "adscripción; la altura y el barrio publicado no coinciden"),
    # El que quedó de la ronda anterior: cuatro puertas del enclave judío sefardí de Flores (E06),
    # todas sobre la franja Flores / Floresta.
    ("E06 · Av. Avellaneda 3069", "Av. Avellaneda 3069",
     "Diario de Flores y GCBA: Flores", "La Nación y Nueva Ciudad: Floresta",
     "franja limítrofe del enclave sefardí (E06) y del coreano de Ruperto Godoy (E04)"),
    ("E06 · Cuenca 954", "Cuenca 954",
     "Diario de Flores y GCBA: Flores", "La Nación y Nueva Ciudad: Floresta",
     "franja limítrofe del enclave sefardí (E06)"),
    ("E06 · Campana 685", "Campana 685",
     "Diario de Flores y GCBA: Flores", "La Nación y Nueva Ciudad: Floresta",
     "franja limítrofe del enclave sefardí (E06)"),
    # Ruperto Godoy 700-800 es un pasaje de 100 m: se consultan las dos cabeceras del rango, que
    # es lo que la delimitación de E04 nombra. Una sola altura no contesta si el pasaje cruza el
    # límite, y esa es exactamente la pregunta.
    ("E04 · Ruperto Godoy 700", "Ruperto Godoy 700",
     "GCBA y Diario de Flores: Flores", "La Nación 2020 «Corea Soho»: Floresta",
     "cabecera baja del Pasaje Ruperto Godoy (E04)"),
    ("E04 · Ruperto Godoy 800", "Ruperto Godoy 800",
     "GCBA y Diario de Flores: Flores", "La Nación 2020 «Corea Soho»: Floresta",
     "cabecera alta del Pasaje Ruperto Godoy (E04)"),
]

# El control: una dirección cuyo error ya está documentado. Si el procedimiento no lo detecta,
# el procedimiento no sirve para los otros cinco.
CONTROL = ("La Academia", "Av. Callao 368", "catálogo oficial: Comuna 5")


def datos_utiles(x: float, y: float, cache: dict) -> dict:
    """Barrio y comuna DEL PUNTO. Es un servicio distinto de `normalizar` y contesta otra cosa."""
    clave = f"{x},{y}"
    if clave not in cache:
        respuesta = requests.get(DATOS_UTILES, params={"x": x, "y": y, "formato": "json"},
                                 timeout=25)
        respuesta.raise_for_status()
        cache[clave] = respuesta.json()
        time.sleep(PAUSA_S)
    return cache[clave]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    cache_norm = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    cache_datos = json.loads(CACHE_DATOS.read_text(encoding="utf-8")) \
        if CACHE_DATOS.exists() else {}
    barrios = gpd.read_file(BARRIOS)[["nombre", "geometry"]].to_crs(CRS_GEOGRAFICO)

    p("LOS CINCO BORDES · USIG, no suposición")
    p("=" * 100)
    p("")
    p("  Tres lecturas por dirección, dos de ellas independientes entre sí:")
    p("      1. USIG /normalizar    → el punto de la puerta")
    p("      2. USIG /datos_utiles  → barrio y comuna DEL PUNTO (servicio distinto)")
    p("      3. geo_barrios.geojson → el polígono oficial del GCBA que ya está en el repositorio")
    p("")
    p("  Google Places: 0 requests.")
    p("")

    def resolver(nombre: str, direccion: str) -> dict:
        candidato = consultar(limpiar(direccion), cache_norm)
        if not candidato or not candidato.get("coordenadas"):
            return {"nombre": nombre, "direccion": direccion, "resuelto": "no"}
        x = float(candidato["coordenadas"]["x"])
        y = float(candidato["coordenadas"]["y"])
        utiles = datos_utiles(x, y, cache_datos)
        punto = gpd.GeoSeries(gpd.points_from_xy([x], [y]), crs=CRS_GEOGRAFICO).iloc[0]
        tocados = barrios[barrios.contains(punto)]
        return {
            "nombre": nombre, "direccion": direccion, "resuelto": "si",
            "direccion_normalizada": candidato.get("direccion", ""),
            "latitud": y, "longitud": x,
            "usig_barrio": utiles.get("barrio", ""),
            "usig_comuna": utiles.get("comuna", ""),
            "poligono_gcba_barrio": tocados.nombre.iloc[0] if len(tocados) else "",
            "coinciden_las_dos_lecturas":
                "si" if sin_tildes(utiles.get("barrio", "")) ==
                sin_tildes(tocados.nombre.iloc[0] if len(tocados) else "") else "NO",
        }

    # --------------------------------------------------------------------- el control primero
    p("-" * 100)
    p("  EL CONTROL · La Academia, cuyo error ya está documentado")
    p("")
    control = resolver(CONTROL[0], CONTROL[1])
    p(f"      {CONTROL[0]} · {CONTROL[1]}")
    p(f"          el catálogo dice:      {CONTROL[2]}")
    p(f"          USIG /datos_utiles:    {control.get('usig_barrio', '—')}, "
      f"{control.get('usig_comuna', '—')}")
    p(f"          polígono GCBA:         {control.get('poligono_gcba_barrio', '—')}")
    if control.get("usig_comuna", "").replace("Comuna ", "").strip() == "5":
        p("      EL CONTROL FALLA: USIG confirma la Comuna 5 que el catálogo dice y que el")
        p("      material declaró errónea. No se usa este procedimiento para los otros bordes.")
        (OUT / "BORDES_USIG.txt").write_text(buffer.getvalue(), encoding="utf-8")
        print(buffer.getvalue())
        return 1
    p("      EL CONTROL PASA: USIG contradice al catálogo en el caso donde ya sabíamos que el")
    p("      catálogo estaba mal. El procedimiento distingue.")
    p("")

    # --------------------------------------------------------------------- los cinco
    filas = []
    for nombre, direccion, fuente_a, fuente_b, para_que in BORDES:
        registro = resolver(nombre, direccion)
        registro.update({"fuente_a": fuente_a, "fuente_b": fuente_b, "decide": para_que})
        filas.append(registro)

    tabla = pd.DataFrame(filas)
    tabla.to_csv(OUT / "bordes_usig_ronda_3.csv", index=False, encoding="utf-8")

    p("-" * 100)
    p("  LOS BORDES, UNO POR UNO")
    p("")
    for fila in tabla.itertuples():
        p(f"      {fila.nombre} · {fila.direccion}")
        if fila.resuelto != "si":
            p("          USIG NO RESUELVE la dirección. Queda sin adscribir; no se supone.")
            p("")
            continue
        p(f"          normalizada:        {fila.direccion_normalizada}")
        p(f"          USIG barrio/comuna: {fila.usig_barrio} · {fila.usig_comuna}")
        p(f"          polígono GCBA:      {fila.poligono_gcba_barrio}"
          f"{'' if fila.coinciden_las_dos_lecturas == 'si' else '   ← LAS DOS NO COINCIDEN'}")
        p(f"          fuente A:           {fila.fuente_a}")
        p(f"          fuente B:           {fila.fuente_b}")
        p(f"          decide:             {fila.decide}")
        p("")

    p("-" * 100)
    p("  RESUMEN")
    p("")
    p(f"      {'establecimiento':<30}{'USIG':<16}{'polígono GCBA':<16}{'comuna':<12}")
    for fila in tabla.itertuples():
        p(f"      {fila.nombre[:29]:<30}{str(fila.usig_barrio)[:15]:<16}"
          f"{str(fila.poligono_gcba_barrio)[:15]:<16}{str(fila.usig_comuna):<12}")
    p("")
    discordes = tabla[tabla.coinciden_las_dos_lecturas == "NO"]
    p(f"      direcciones donde las dos lecturas oficiales NO coinciden: {len(discordes)}")
    for fila in discordes.itertuples():
        p(f"            {fila.nombre}: USIG «{fila.usig_barrio}» vs polígono "
          f"«{fila.poligono_gcba_barrio}»")
    p("")
    p("      USIG resuelve la adscripción ADMINISTRATIVA. Que una nota titule «un clásico de")
    p("      Saavedra» sigue siendo cierto como uso: lo que se corrige es el campo de la matriz,")
    p("      no la cita.")
    p("")

    CACHE.write_text(json.dumps(cache_norm, ensure_ascii=False, indent=1), encoding="utf-8")
    CACHE_DATOS.write_text(json.dumps(cache_datos, ensure_ascii=False, indent=1),
                           encoding="utf-8")
    (OUT / "BORDES_USIG.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
