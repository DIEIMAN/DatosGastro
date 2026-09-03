"""Diagnosticos sobre el padron de panaderias ya construido.

No vuelve a leer las fuentes crudas ni consulta nada externo: trabaja sobre
outputs/panaderias/panaderias_maestro.csv y responde preguntas que hoy no estan
contestadas y que condicionan como se puede leer el padron.

  D1  Sesgo de geocodificacion: el 65 % que tiene coordenadas, se parece al 35 % que no?
  D2  Elaboracion vs despacho por comuna: donde se hornea y donde solo se vende.
  D3  Direcciones sin geo: cuantas son direccionables (dimensiona la corrida USIG).
  D4  Calidad del agrupamiento: que tan lejos esta el dedup de fusionar o partir de mas.
  D5  Firmas repetidas entre los registros que tienen nombre (cadenas).
  D6  Barrios sin ninguna panaderia geolocalizada.
  D7  Solapamiento con casas de pastas, si se le pasa su maestro con --pastas.
  D9  Renovaciones candidatas: el precio de contar por habilitacion y no por inmueble.

Uso:
  .venv/Scripts/python.exe scripts/panaderias/diagnostico_panaderias.py
  .venv/Scripts/python.exe scripts/panaderias/diagnostico_panaderias.py --pastas RUTA/casas_pastas_maestro.csv
  .venv/Scripts/python.exe scripts/panaderias/diagnostico_panaderias.py --maestro RUTA/panaderias_maestro.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))
from panaderias_patterns import norm  # noqa: E402

OUT = ROOT / "outputs" / "panaderias"
ANA = OUT / "analisis"
MAESTRO = OUT / "panaderias_maestro.csv"
GEO_BARRIOS = ROOT / "data" / "raw" / "geo_barrios.geojson"

# Patrones del universo A que declaran elaboracion, frente al que solo despacha.
ELABORA = {"elaboracion_panaderia_venta_directa", "elaboracion_panaderia_ncp",
           "elaboracion_industrial_panaderia", "panificadora", "fabrica_de_pan"}


def read_maestro(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(name: str, rows: list[dict], cols: list[str]) -> None:
    ANA.mkdir(parents=True, exist_ok=True)
    with (ANA / name).open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def pct(a: int, b: int) -> str:
    return f"{100.0 * a / b:.1f} %" if b else "-"


def esquema_de(row: dict) -> str:
    return "legacy" if "esquema=legacy" in (row.get("observaciones") or "") else "moderno"


def tiene_geo(row: dict) -> bool:
    return bool((row.get("lat") or "").strip())


# --------------------------------------------------------------------------------------
def d1_sesgo_geo(rows: list[dict]) -> list[str]:
    """El subconjunto geolocalizado, es representativo del universo?"""
    a = [r for r in rows if r["nivel_universo"] == "A"]
    lineas = ["D1. Sesgo de geocodificacion (universo A, n=%d)" % len(a)]

    filas = []
    for campo, etiqueta in [("patron_detectado", "rubro"), (None, "esquema")]:
        grupos = defaultdict(lambda: [0, 0])
        for r in a:
            k = esquema_de(r) if campo is None else r[campo]
            grupos[k][0] += 1
            grupos[k][1] += tiene_geo(r)
        for k, (tot, geo) in sorted(grupos.items(), key=lambda kv: -kv[1][0]):
            filas.append({"dimension": etiqueta, "valor": k, "total": tot,
                          "geolocalizados": geo, "cobertura_geo": pct(geo, tot)})
            lineas.append("   %-8s %-38s %5d  geo %5d  %s" % (etiqueta, k[:38], tot, geo, pct(geo, tot)))

    # La pregunta que importa: cambia la mezcla elaboracion/despacho al geolocalizar?
    def mezcla(sub):
        e = sum(1 for r in sub if r["patron_detectado"] in ELABORA)
        return e, len(sub) - e
    e_g, d_g = mezcla([r for r in a if tiene_geo(r)])
    e_s, d_s = mezcla([r for r in a if not tiene_geo(r)])
    lineas += [
        "   ---",
        "   elaboracion vs despacho entre los GEOLOCALIZADOS: %d / %d  (%s elaboracion)"
        % (e_g, d_g, pct(e_g, e_g + d_g)),
        "   elaboracion vs despacho entre los SIN GEO       : %d / %d  (%s elaboracion)"
        % (e_s, d_s, pct(e_s, e_s + d_s)),
    ]
    filas.append({"dimension": "mezcla", "valor": "geolocalizados", "total": e_g + d_g,
                  "geolocalizados": e_g, "cobertura_geo": pct(e_g, e_g + d_g)})
    filas.append({"dimension": "mezcla", "valor": "sin_geo", "total": e_s + d_s,
                  "geolocalizados": e_s, "cobertura_geo": pct(e_s, e_s + d_s)})
    write_csv("d1_sesgo_geocodificacion.csv", filas,
              ["dimension", "valor", "total", "geolocalizados", "cobertura_geo"])
    return lineas


# --------------------------------------------------------------------------------------
def d2_elabora_vs_despacha(rows: list[dict]) -> list[str]:
    a = [r for r in rows if r["nivel_universo"] == "A" and r.get("comuna_efectiva")]
    g = defaultdict(lambda: [0, 0])
    for r in a:
        g[r["comuna_efectiva"]][0 if r["patron_detectado"] in ELABORA else 1] += 1
    filas = []
    for c, (e, d) in sorted(g.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 99):
        filas.append({"comuna": c, "elabora": e, "solo_despacha": d, "total": e + d,
                      "share_elaboracion": pct(e, e + d)})
    write_csv("d2_elaboracion_vs_despacho_por_comuna.csv", filas,
              ["comuna", "elabora", "solo_despacha", "total", "share_elaboracion"])
    lineas = ["D2. Elaboracion vs despacho por comuna (universo A con comuna, n=%d)" % len(a)]
    for f in sorted(filas, key=lambda f: -float(f["share_elaboracion"].split()[0])):
        lineas.append("   Comuna %-3s elabora %3d  despacha %3d  -> %s elaboracion"
                      % (f["comuna"], f["elabora"], f["solo_despacha"], f["share_elaboracion"]))
    return lineas


# --------------------------------------------------------------------------------------
ALTURA = re.compile(r"\b\d{1,5}\b")


def d3_direcciones_sin_geo(rows: list[dict]) -> list[str]:
    sin = [r for r in rows if not tiene_geo(r)]
    unicas = defaultdict(list)
    for r in sin:
        unicas[norm(r["direccion_original"])].append(r)

    con_altura = {k: v for k, v in unicas.items() if k and ALTURA.search(k)}
    sin_altura = {k: v for k, v in unicas.items() if k and not ALTURA.search(k)}
    vacias = {k: v for k, v in unicas.items() if not k}

    filas = [{"direccion": v[0]["direccion_original"], "registros": len(v),
              "direccionable": "si" if k in con_altura else "no",
              "nivel": v[0]["nivel_universo"],
              "patron": v[0]["patron_detectado"]}
             for k, v in sorted(unicas.items(), key=lambda kv: -len(kv[1])) if k]
    write_csv("d3_direcciones_sin_geocodificar.csv", filas,
              ["direccion", "registros", "direccionable", "nivel", "patron"])
    return [
        "D3. Direcciones sin geocodificar (universo A+B)",
        "   registros sin lat/lon      : %d" % len(sin),
        "   direcciones unicas         : %d" % len(unicas),
        "   con altura (direccionables): %d  -> es el tamanio real de la corrida USIG" % len(con_altura),
        "   sin altura (esquina/S-N)   : %d  -> USIG no las resuelve solas" % len(sin_altura),
        "   direccion vacia            : %d" % len(vacias),
    ]


# --------------------------------------------------------------------------------------
def d4_calidad_agrupamiento(rows: list[dict]) -> list[str]:
    tam = Counter(int(r["registros_agrupados"]) for r in rows)

    def tipo_clave(r):
        # Desde F1 la clave preferida es la habilitacion (solicitud legacy o disposicion
        # moderna); la partida, que identifica el inmueble, quedo de respaldo.
        if (r.get("clave_habilitacion") or "").strip():
            return "habilitacion"
        if (r.get("id_registro_original") or "").strip():
            return "partida+nombre"
        return "nombre+calle" if (r.get("nombre_original") or "").strip() else "solo_domicilio"
    clav = Counter(tipo_clave(r) for r in rows)

    grandes = sorted(rows, key=lambda r: -int(r["registros_agrupados"]))[:20]
    write_csv("d4_grupos_mas_grandes.csv",
              [{"registros_agrupados": r["registros_agrupados"],
                "nombre": r["nombre_original"], "direccion": r["direccion_original"],
                "partida": r["id_registro_original"], "patron": r["patron_detectado"],
                "nivel": r["nivel_universo"], "tipo_clave": tipo_clave(r)} for r in grandes],
              ["registros_agrupados", "nombre", "direccion", "partida", "patron", "nivel", "tipo_clave"])

    lineas = ["D4. Calidad del agrupamiento (n=%d establecimientos)" % len(rows),
              "   clave usada:"]
    for k, v in clav.most_common():
        lineas.append("     %-16s %5d  (%s)" % (k, v, pct(v, len(rows))))
    lineas.append("   tamanio de grupo: 1 registro = %d establecimientos; 2-10 = %d; >10 = %d; max = %d"
                  % (tam.get(1, 0),
                     sum(v for k, v in tam.items() if 2 <= k <= 10),
                     sum(v for k, v in tam.items() if k > 10),
                     max(tam) if tam else 0))
    return lineas


# --------------------------------------------------------------------------------------
def d5_firmas(rows: list[dict]) -> list[str]:
    con_nombre = [r for r in rows if (r.get("nombre_original") or "").strip()]
    c = Counter(norm(r["nombre_original"]) for r in con_nombre)
    rep = [(k, v) for k, v in c.most_common() if v > 1]
    ejemplo = {}
    for r in con_nombre:
        ejemplo.setdefault(norm(r["nombre_original"]), r["nombre_original"])
    write_csv("d5_firmas_con_varias_bocas.csv",
              [{"firma": ejemplo[k], "establecimientos": v} for k, v in rep],
              ["firma", "establecimientos"])
    lineas = ["D5. Firmas con mas de un establecimiento (solo los %d registros con nombre)"
              % len(con_nombre),
              "   firmas distintas: %d | con mas de una boca: %d" % (len(c), len(rep))]
    for k, v in rep[:10]:
        lineas.append("     %-46s %d" % (ejemplo[k][:46], v))
    return lineas


# --------------------------------------------------------------------------------------
def d6_barrios_vacios(rows: list[dict]) -> list[str]:
    barrios = set()
    if GEO_BARRIOS.exists():
        gj = json.loads(GEO_BARRIOS.read_text(encoding="utf-8"))
        for f in gj.get("features", []):
            n = f.get("properties", {}).get("nombre")
            if n:
                barrios.add(str(n))
    con = Counter(r["barrio_efectivo"] for r in rows
                  if r["nivel_universo"] == "A" and r.get("barrio_efectivo"))
    vacios = sorted(b for b in barrios if con.get(b, 0) == 0)
    write_csv("d6_barrios_sin_panaderias.csv",
              [{"barrio": b, "panaderias_A_geolocalizadas": 0,
                "nota": "cero en el padron geolocalizado; con 35 % del universo sin coordenadas "
                        "no es evidencia de ausencia"} for b in vacios],
              ["barrio", "panaderias_A_geolocalizadas", "nota"])
    return ["D6. Barrios sin ninguna panaderia del universo A geolocalizada: %d de %d"
            % (len(vacios), len(barrios)),
            "   " + (", ".join(vacios) if vacios else "(ninguno)")]


# --------------------------------------------------------------------------------------
def d7_solape_pastas(rows: list[dict], pastas_path: Path) -> list[str]:
    if not pastas_path.exists():
        return ["D7. Solapamiento con casas de pastas: no se paso --pastas, omitido"]
    pastas = read_maestro(pastas_path)

    def claves(rs):
        por_part, por_dir = defaultdict(list), defaultdict(list)
        for r in rs:
            p = (r.get("id_registro_original") or "").strip()
            if p:
                por_part[p].append(r)
            d = norm(r.get("direccion_original") or "")
            if d:
                por_dir[d].append(r)
        return por_part, por_dir

    p_part, p_dir = claves(rows)
    q_part, q_dir = claves(pastas)
    comunes_part = set(p_part) & set(q_part)
    comunes_dir = set(p_dir) & set(q_dir)

    filas = []
    for d in sorted(comunes_dir):
        pan, pas = p_dir[d][0], q_dir[d][0]
        filas.append({"direccion": pan["direccion_original"],
                      "partida": pan["id_registro_original"],
                      "panaderia_patron": pan["patron_detectado"],
                      "panaderia_nivel": pan["nivel_universo"],
                      "pastas_patron": pas.get("patron_detectado", ""),
                      "pastas_nivel": pas.get("nivel_universo", "")})
    write_csv("d7_solape_con_casas_de_pastas.csv", filas,
              ["direccion", "partida", "panaderia_patron", "panaderia_nivel",
               "pastas_patron", "pastas_nivel"])
    return ["D7. Solapamiento con casas de pastas (maestro corregido, n=%d)" % len(pastas),
            "   mismo domicilio en ambos universos: %d" % len(comunes_dir),
            "   misma partida matriz              : %d" % len(comunes_part)]


# --------------------------------------------------------------------------------------
def d8_qa_geocodificacion(rows: list[dict]) -> list[str]:
    """Control de la geocodificacion, que viene marcada `sin_control_comuna`.

    Tres preguntas: cae algun punto fuera de CABA, coincide la comuna geocodificada con la
    declarada donde ambas existen, y cuantos establecimientos comparten coordenada exacta.
    La segunda es la que detecta calles homonimas, que en esta ciudad son un problema real.
    """
    geo = [r for r in rows if tiene_geo(r)]
    if not geo:
        return ["D8. QA de geocodificacion: no hay puntos"]
    try:
        import geopandas as gpd
        from shapely.geometry import Point
    except ImportError:
        return ["D8. QA de geocodificacion: geopandas no disponible, omitido"]

    comunas = gpd.read_file(ROOT / "data" / "raw" / "geo_comunas.geojson").to_crs(4326)
    caba = comunas.geometry.union_all()
    fuera = [r for r in geo
             if not caba.contains(Point(float(r["lon"]), float(r["lat"])))]

    discrepan, comparadas = [], 0
    for r in geo:
        decl = "".join(c for c in (r.get("comuna_original") or "") if c.isdigit()).lstrip("0")
        geoc = (r.get("comuna_efectiva") or "").lstrip("0")
        if decl and geoc:
            comparadas += 1
            if decl != geoc:
                discrepan.append({"direccion": r["direccion_original"],
                                  "comuna_declarada": decl, "comuna_geocodificada": geoc,
                                  "calidad_geo": r["calidad_geo"],
                                  "nota": "revisar: puede ser calle homonima o limite de comuna"})

    coord = Counter((round(float(r["lat"]), 6), round(float(r["lon"]), 6)) for r in geo)
    repetidas = [(k, v) for k, v in coord.items() if v > 1]

    write_csv("d8_qa_geocodificacion.csv",
              discrepan + [{"direccion": r["direccion_original"], "comuna_declarada": "",
                            "comuna_geocodificada": r.get("comuna_efectiva", ""),
                            "calidad_geo": r["calidad_geo"],
                            "nota": "punto fuera del poligono de CABA"} for r in fuera],
              ["direccion", "comuna_declarada", "comuna_geocodificada", "calidad_geo", "nota"])

    return [
        "D8. QA de geocodificacion (%d puntos)" % len(geo),
        "   fuera del poligono de CABA          : %d" % len(fuera),
        "   comuna declarada vs geocodificada   : %d comparables, %d discrepan"
        % (comparadas, len(discrepan)),
        "   coordenada exacta compartida        : %d puntos, %d establecimientos"
        % (len(repetidas), sum(v for _, v in repetidas)),
        "   (compartir coordenada es esperable: dos habilitaciones en el mismo domicilio)",
    ]


# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
def d9_renovaciones(rows: list[dict]) -> list[str]:
    """Lo que cuesta contar por habilitacion: una renovacion son dos habilitaciones.

    Desde F1 el padron agrupa por tramite (solicitud legacy / disposicion moderna), que es
    lo mas cerca de un local que publica la fuente. El precio es que un mismo local
    habilitado dos veces -renovacion, cambio de titular, ampliacion de rubro- entra dos
    veces. No se puede resolver a ciegas: dos panaderias pegadas en la misma cuadra son
    igual de compatibles con la evidencia que una sola habilitada dos veces. Lo que si se
    puede es acotarlo y dejar la lista corta para mirar.
    """
    a = [r for r in rows if r["nivel_universo"] == "A"]
    por_domicilio = defaultdict(list)
    for r in a:
        d = norm(r["direccion_original"])
        if d:
            por_domicilio[d].append(r)

    candidatos, exceso = [], 0
    for d, v in sorted(por_domicilio.items()):
        if len(v) < 2:
            continue
        por_patron = defaultdict(list)
        for r in v:
            por_patron[r["patron_detectado"]].append(r)
        for patron, rr in por_patron.items():
            if len(rr) < 2:
                continue
            exceso += len(rr) - 1
            for r in rr:
                candidatos.append({
                    "direccion": r["direccion_original"], "patron": patron,
                    "anio_habilitacion": r["fecha_habilitacion"],
                    "clave_habilitacion": r.get("clave_habilitacion", ""),
                    "partida_matriz": r["id_registro_original"],
                    "archivo_origen": r["archivo_origen"],
                    "comuna": r.get("comuna_efectiva", ""),
                    "misma_partida": "si" if len({x["id_registro_original"] for x in rr}) == 1 else "no",
                })

    write_csv("d9_renovaciones_candidatas.csv", candidatos,
              ["direccion", "patron", "anio_habilitacion", "clave_habilitacion",
               "partida_matriz", "archivo_origen", "comuna", "misma_partida"])

    misma = len({c["direccion"] for c in candidatos if c["misma_partida"] == "si"})
    return [
        "D9. Renovaciones candidatas (universo A, n=%d)" % len(a),
        "   grupos con mismo domicilio y mismo patron : %d" % len({c["direccion"] for c in candidatos}),
        "   establecimientos involucrados             : %d" % len(candidatos),
        "   exceso maximo si TODOS fueran el mismo local: %d (%s del universo A)"
        % (exceso, pct(exceso, len(a))),
        "   de esos domicilios, con una sola partida   : %d" % misma,
        "   -> es la cota superior del doble conteo que introduce contar por habilitacion;",
        "      la lista completa esta en d9_renovaciones_candidatas.csv y se revisa a mano.",
    ]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pastas", default=None, help="ruta a casas_pastas_maestro.csv para el solape")
    ap.add_argument("--maestro", default=None,
                    help="maestro a diagnosticar; por defecto el publicado. Los CSV salen "
                         "junto al maestro, para poder diagnosticar una corrida de prueba "
                         "sin pisar outputs/panaderias/analisis.")
    args = ap.parse_args()

    global ANA
    maestro = Path(args.maestro) if args.maestro else MAESTRO
    if args.maestro:
        ANA = maestro.parent / "analisis"
    rows = read_maestro(maestro)
    bloques = [
        d1_sesgo_geo(rows), d2_elabora_vs_despacha(rows), d3_direcciones_sin_geo(rows),
        d4_calidad_agrupamiento(rows), d5_firmas(rows), d6_barrios_vacios(rows),
        d7_solape_pastas(rows, Path(args.pastas)) if args.pastas
        else ["D7. Solapamiento con casas de pastas: no se paso --pastas, omitido"],
        d8_qa_geocodificacion(rows),
        d9_renovaciones(rows),
    ]
    for b in bloques:
        print("\n".join(b))
        print()
    print("CSV en", ANA)


if __name__ == "__main__":
    main()
