# -*- coding: utf-8 -*-
"""El control de anclas: qué establecimiento de cada polo queda adentro del borde y cuál no.

POR QUÉ EXISTE ESTE CONTROL
---------------------------
Hay dos casos conocidos en los que el borde de un polo deja afuera el establecimiento que lo
justifica. En La Boca se vio porque el borde había quedado parcial: La Perla de Caminito estaba
a 26 m. En Balvanera **no se vio**, porque el borde cerró bien —cierra sobre calles y contiene
las cinco puertas del enclave— y aun así deja el Café de los Angelitos, Bar Notable y evidencia
con la que la zona entró al atlas, 768 m afuera. Un borde que cierra bien no es un borde que
describa al polo. Este control mide los 41 y dice cuántas páginas tienen ese problema.

QUÉ MIDE Y QUÉ NO
-----------------
  - `dentro_del_borde` se resuelve con `covers()` **de un punto contra un polígono**, que es lo
    correcto y no lo que la regla prohíbe: la regla prohíbe verificar la contención de un
    POLÍGONO dentro de otro con un predicado en vez de por superficie perdida. Para un punto,
    `contains` daría False a un establecimiento que está a 0 m sobre el borde, y la ronda 17 ya
    se comió ese error una vez.
  - `sostiene_condicion_historia` marca los establecimientos que sostienen la **vía B** de la
    zona —trayectoria e instituciones—. La vía B se mide **sobre la zona y no sobre el recorte**:
    ésa es la regla que salió del caso Almagro y no se toca acá. Lo que este control agrega es
    que la página **tiene que decirlo**, y hoy la mayoría no lo dice: cuando el establecimiento
    que abre la vía B queda fuera del borde dibujado, el lector ve un polígono que no contiene
    su propia prueba.
  - La ubicación de cada ancla sale, por orden: (1) del punto de la capa de reconocimiento, que
    es una coordenada real; (2) de la altura de puerta contra el callejero oficial, que devuelve
    el **centro de la cuadra** y no la puerta —precisión de media cuadra, unos 50 m—. El método
    de cada fila va escrito en la columna `ubicacion_metodo` y no al pie.
  - Un ancla que la página nombra y que no se puede ubicar por ninguna de las dos vías sale en
    la tabla con `ubicacion_metodo = sin ubicar` y sin distancia. No se la deja afuera: que la
    página nombre algo que el repositorio no sabe dónde está es parte del resultado.

Se mide en EPSG:5347 y se guarda en EPSG:4326. Cero requests.
"""

import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union

SALIDA = Path(__file__).resolve().parent
BARRIDO = SALIDA.parent
ROOT = SALIDA.parents[2]
sys.path.insert(0, str(SALIDA))
sys.path.insert(0, str(SALIDA.parent / "ronda_17"))
import geometria_vigente  # noqa: E402
from cierre_geometrico import Callejero, limpia, RECETAS  # noqa: E402

CRS_M, CRS_G = "EPSG:5347", "EPSG:4326"
HOY = date.today().isoformat()

SOPORTES = BARRIDO / "ronda_16_codex" / "geometria" / "soportes_41.geojson"
R17 = BARRIDO / "ronda_17" / "geometria" / "perimetros_cierre.geojson"
R18 = SALIDA / "geometria" / "perimetros_ronda_18.geojson"
ZONAS = BARRIDO / "geometria_r7" / "zonas_r8.geojson"
MAGNITUDES = BARRIDO / "desde_cowork" / "evidencia_2026" / "magnitudes_sin_perimetro.csv"
FICHAS = BARRIDO / "ronda_17_codex" / "fichas_corpus_polos.csv"
HITOS = BARRIDO / "hitos" / "hitos_capa_2026_r11.csv"

# Los tipos de la capa de reconocimiento que cuentan para la vía B. Es la misma lista con la que
# la vía B se midió en su momento (scripts/barrido_ciudad/ronda_7_familias_de_vias.py), y no se
# cambia acá: si se cambiara, este control estaría midiendo otra condición que la que la página
# invoca.
TIPOS_VIA_B = {"Bar Notable", "Restaurante Icónico", "Pizzería emblemática",
               "Heladería histórica", "MICHELIN", "Ranking internacional"}
# Dentro de la vía B, cuáles son de trayectoria y cuáles son distinción contemporánea. La
# condición que la página invoca cuando habla de «establecimientos con historia» son las
# primeras; las otras dos abren la misma vía pero no dicen lo mismo, y conviene poder separarlas.
TIPOS_TRAYECTORIA = {"Bar Notable", "Restaurante Icónico", "Pizzería emblemática",
                     "Heladería histórica"}

RUIDO = re.compile(
    r"^(michelin|bar notable|restaurante ic[oó]nico|pizzeria emblematica|alta \d{4}|"
    r"verificado|probablemente|se mud[oó]|cerrad[oa]|dudoso|en riesgo|desde \d{4}|"
    r"m[aá]s de \d+|de \d{4}|ninguno|nan|otros?|etc|recomendados?|"
    r"via_b_nombres|sin direccion|deficit)\b", re.I)
PREAMBULO = re.compile(
    r"^(MAS|MÁS|ONCE|NUEVE|CUATRO|TRES|DOS|LOS CINCO|SOLO|NINGUNO|CUATRO BARES|"
    r"NUEVE DE LOS)\b", re.I)
# El número puede venir pegado a una coma —«Av. Alvarez Jonte 4702, verificado abierto»—, así que
# el cierre es «no siga otro dígito» y no «venga un espacio». Con la versión anterior, seis anclas
# con dirección escrita salieron como «sin ubicar»: el error no se veía porque la fila igual salía.
DIRECCION = re.compile(r"^([A-Za-zÁÉÍÓÚÜÑáéíóúüñ'\.\s,]{3,45}?)\s+(\d{1,5})(?!\d)")
SOLO_NUMERO = re.compile(r"^(\d{1,5})(?!\d)")
COLA_CALLE = re.compile(r"\s+(al|y|esq|esquina|entre)\.?$", re.I)


def clave(texto):
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", t.lower())


def tokens(texto):
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()
    t = re.sub(r"\b(AV|AVDA|AVENIDA|PJE|PASAJE|DIAG|DIAGONAL|CALLE|DR|GRAL|PRES|TTE|"
               r"CDORO|CMDTE|CMTE|COMODORO|COMANDANTE|CNEL|CORONEL|ING|INT|PJE)\b\.?", " ", t)
    return frozenset(x for x in re.split(r"[^A-Z0-9]+", t) if len(x) > 1)


VACIAS = {"bar", "cafe", "el", "la", "los", "las", "de", "del", "y", "restaurante", "pizzeria",
          "confiteria", "heladeria", "don", "casa", "parrilla", "resto"}


def palabras(nombre):
    t = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode().lower()
    ps = {x for x in re.split(r"[^a-z0-9]+", t) if len(x) > 2 and x not in VACIAS}
    return ps or {x for x in re.split(r"[^a-z0-9]+", t) if len(x) > 2}


class Indice:
    """clave -> (nombre tal como está escrito, lo que sea que se quiera guardar)."""

    def __init__(self):
        self.por_clave = {}

    def poner(self, nombre, payload):
        self.por_clave.setdefault(clave(nombre), (nombre, payload))

    def subconjunto(self, prueba):
        otro = Indice()
        otro.por_clave = {k: v for k, v in self.por_clave.items() if prueba(v[1])}
        return otro

    def __contains__(self, k):
        return k in self.por_clave

    def __len__(self):
        return len(self.por_clave)


def casi_igual(nombre, indice, restringir=None):
    """Empareja «Boca a Boca» con «Bar Boca a Boca» y «El Hipopotamo» con «HIPOPOTAMO».

    Tres pasadas, y el orden importa. Primero la clave exacta. Después, por conjunto de palabras
    significativas, **restringido a los establecimientos de la propia zona**. Y sólo si eso no
    resuelve, el mismo criterio contra la ciudad entera. En las tres, si hay más de un candidato
    no se empareja nada.

    El primer intento comparaba prefijos y sufijos de la cadena pegada y emparejó «Argot», de
    Villa Santa Rita, con «Café Margot», de Boedo: «cafemargot» termina en «argot». Un
    emparejamiento así no inventa un dato, hace algo peor —le mueve la ubicación a un
    establecimiento real— y no se ve en ninguna cifra agregada. Por eso el desempate es la zona
    y el criterio es «si hay dos candidatos, no hay ninguno».
    """
    k = clave(nombre)
    if k in indice.por_clave:
        return indice.por_clave[k][1]
    # `ps` se calcula sobre el NOMBRE y no sobre la clave: la clave viene sin separadores y
    # «elhipopotamo» es una sola palabra. Con la clave, la comparación por palabras no comparaba
    # nada y devolvía None siempre, en silencio y sin que ninguna fila faltara.
    ps = palabras(nombre)
    if not ps:
        return None
    for universo in ([restringir] if restringir is not None else []) + [indice]:
        exactos = [v for nn, v in universo.por_clave.values() if palabras(nn) == ps]
        if len(exactos) == 1:
            return exactos[0]
        if exactos:
            continue
        sub = [v for nn, v in universo.por_clave.values()
               if palabras(nn) and (palabras(nn) < ps or ps < palabras(nn))]
        if len(sub) == 1:
            return sub[0]
    return None


class Direcciones:
    """Resuelve «Ruperto Godoy 712» contra un callejero que lo escribe «GODOY, RUPERTO».

    El callejero oficial invierte apellido y nombre y agrega tratamientos —«ANCHORENA, TOMAS
    MANUEL DE, DR.»—, así que comparar la cadena entera no sirve. Se compara por conjunto de
    palabras: gana la calle cuyo conjunto contiene a todas las del texto y agrega menos.
    """

    def __init__(self, cj):
        self.cj = cj
        self.por_tokens = defaultdict(list)
        for nom in set(cj.calles.nomoficial):
            self.por_tokens[tokens(nom)].append(nom)

    def calle(self, texto):
        pedido = tokens(texto)
        if not pedido:
            return None
        mejor, sobra = None, 99
        for tks, noms in self.por_tokens.items():
            if pedido <= tks and len(tks - pedido) < sobra:
                mejor, sobra = sorted(noms)[0], len(tks - pedido)
        return mejor

    def punto(self, texto_calle, altura):
        nom = self.calle(texto_calle)
        if nom is None:
            return None, None
        try:
            return self.cj.punto_de_altura(nom, int(altura)), nom
        except SystemExit:
            return None, nom


def lee_pagina(texto, dirs):
    """Los establecimientos que la página nombra, con su dirección si la trae."""
    if not isinstance(texto, str) or not texto.strip() or texto.strip().lower() == "nan":
        return []
    salida = []
    for chunk in texto.split("·"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" in chunk and PREAMBULO.match(chunk):
            chunk = chunk.split(":", 1)[1]
        calle_previa = None
        trozos = []
        for t in re.split(r",(?![^(]*\))", chunk):
            # «Casa Veltri y Presencia (Michelin)» y «Alcanfor (Aguirre 949) y Horta (Aguirre
            # 1080)» son dos establecimientos cada uno, no uno con un nombre largo.
            if t.count("(") > 1 or ("(" not in t and re.search(r"\s+y\s+[A-ZÁÉÍÓÚÑ]", t)):
                trozos.extend(re.split(r"\s+y\s+(?=[A-ZÁÉÍÓÚÑ])", t))
            else:
                trozos.append(t)
        for trozo in trozos:
            trozo = trozo.strip(" .;")
            if not trozo:
                continue
            m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", trozo)
            nombre, detalle = (m.group(1), m.group(2)) if m else (trozo, "")
            nombre = re.sub(r"^(MAS|MÁS|Y)\s+", "", nombre.strip(), flags=re.I).strip(" .;'\"")
            if not nombre or len(nombre) > 48 or RUIDO.match(nombre):
                continue
            if not re.search(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]{3}", nombre):
                continue
            # «Cafe Olimpo, que era su unico Notable, RESULTO ESTAR EN MONTE CASTRO» deja un
            # trozo que empieza en minúscula. Un nombre de establecimiento no empieza así.
            if nombre[0].islower():
                continue
            calle = altura = None
            md = DIRECCION.match(detalle)
            mn = SOLO_NUMERO.match(detalle)
            if md:
                calle = COLA_CALLE.sub("", md.group(1).strip(" .,")).strip(" .,")
                altura = int(md.group(2))
                calle_previa = calle
            elif mn and calle_previa:
                # «Bulmat (731)» hereda la calle del ítem anterior de la misma enumeración
                calle, altura = calle_previa, int(mn.group(1))
            salida.append(dict(nombre=nombre, calle=calle, altura=altura,
                               direccion_texto=(f"{calle} {altura}" if calle else "")))
    return salida


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 98)
    print("ANCLAS DENTRO Y FUERA · los establecimientos de cada página contra su borde")
    print("=" * 98 + "\n")

    cj = Callejero()
    dirs = Direcciones(cj)

    # ------------------------------------------------------------------ geometría vigente
    bordes, procedencia, soportes = geometria_vigente.cargar()
    tentativos = geometria_vigente.TENTATIVOS
    sin_borde_propio = geometria_vigente.SIN_BORDE_PROPIO

    print(f"geometría vigente: {len(bordes)} polos")
    for etq in ("soporte previo (ronda 16)", "ronda 17", "ronda 18"):
        cuales = sorted(k for k, v in procedencia.items() if v == etq)
        print(f"  de {etq:<26} {len(cuales):>2}: {', '.join(cuales)}")
    print()

    # ------------------------------------------------------------------ la zona de cada polo
    zonas = gpd.read_file(ZONAS).to_crs(CRS_M).set_index("zona_id")
    zg = {zid: limpia(g) for zid, g in zonas.geometry.items()}
    mag = pd.read_csv(MAGNITUDES).set_index("polo_id")
    zona_de, como_zona = {}, {}
    for pid, borde in bordes.items():
        if pid in mag.index:
            zona_de[pid] = str(mag.contenedor.loc[pid])
            como_zona[pid] = "declarada en magnitudes_sin_perimetro.csv"
        elif pid in zg:
            zona_de[pid] = pid
            como_zona[pid] = "misma id en la capa de zonas"
        else:
            mejor, area = None, 0.0
            for zid, g in zg.items():
                a = limpia(borde.intersection(g)).area
                if a > area:
                    mejor, area = zid, a
            zona_de[pid] = mejor
            como_zona[pid] = (f"mayor solape con el borde ({area / borde.area * 100:.0f} % "
                              f"del borde)")
    faltan = [p for p, z in zona_de.items() if z not in zg]
    if faltan:
        raise SystemExit(f"sin zona en la capa: {faltan}. No se sigue sin contenedor.")

    print("la zona de la que se recorta cada polo (la vía B se mide acá, no en el recorte):")
    for pid in sorted(bordes):
        print(f"  {pid:<6} -> {zona_de[pid]:<20} {como_zona[pid]}")
    print()

    # ------------------------------------------------------------------ capa de reconocimiento
    hitos = pd.read_csv(HITOS)
    con_punto = hitos[hitos.latitud.notna()].copy()
    pts = gpd.GeoSeries([Point(x, y) for x, y in zip(con_punto.longitud, con_punto.latitud)],
                        crs=CRS_G).to_crs(CRS_M)
    con_punto["punto"] = list(pts)
    por_clave = Indice()
    for r in con_punto.itertuples():
        por_clave.poner(str(r.nombre), r)
    print(f"capa de reconocimiento: {len(hitos)} establecimientos, {len(con_punto)} con punto, "
          f"{len(hitos) - len(con_punto)} sin punto (no se los ubica en el centroide de nada)")

    # vía B de cada zona, contada sobre la zona
    via_b_zona = {}
    for zid, g in zg.items():
        dentro = [r for r in con_punto.itertuples()
                  if r.tipo in TIPOS_VIA_B and g.covers(r.punto)]
        via_b_zona[zid] = dentro
    print(f"vía B por zona: {sum(1 for v in via_b_zona.values() if v)} zonas con al menos un "
          f"establecimiento de vía B adentro\n")

    # ------------------------------------------------------------------ armar las anclas
    fichas = pd.read_csv(FICHAS).set_index("polo_id")
    referentes_r17 = defaultdict(list)
    for receta in RECETAS:
        for nom, calle, altura in receta.get("referentes", []):
            referentes_r17[receta["zona"]].append((nom, calle, altura))

    filas = []
    for pid in sorted(bordes):
        borde = bordes[pid]
        zid = zona_de[pid]
        zona = zg[zid]
        nombre_polo = str(soportes.polo_nombre.loc[pid])
        de_la_zona = por_clave.subconjunto(lambda r: zona.covers(r.punto))
        vistos = Indice()

        def suma(nombre, direccion, tipo, reconocimiento, punto, metodo, origen, vigencia=""):
            k = clave(nombre)
            if not k:
                return
            previa = casi_igual(nombre, vistos)
            if previa is not None:
                if previa["origen_del_dato"] != origen:
                    previa["origen_del_dato"] = "la página y la capa de reconocimiento"
                if punto is not None and previa["_punto"] is None:
                    previa.update(_punto=punto, ubicacion_metodo=metodo)
                if direccion and not previa["direccion"]:
                    previa["direccion"] = direccion
                if tipo and not previa["tipo"]:
                    previa.update(tipo=tipo, reconocimiento=reconocimiento)
                return
            vistos.poner(nombre, dict(
                polo=f"{pid} · {nombre_polo}", establecimiento=nombre, direccion=direccion,
                tipo=tipo, reconocimiento=reconocimiento, _punto=punto,
                ubicacion_metodo=metodo, origen_del_dato=origen, estado_vigencia=vigencia,
                zona_id=zid))

        def del_reconocimiento(r, origen):
            suma(str(r.nombre), str(r.direccion) if pd.notna(r.direccion) else "",
                 str(r.tipo), str(r.reconocimiento) if pd.notna(r.reconocimiento) else "",
                 r.punto, "punto de la capa de reconocimiento", origen,
                 str(r.estado_catalogo_2026_08_08) if pd.notna(r.estado_catalogo_2026_08_08)
                 else (str(r.vigencia_verificada) if pd.notna(r.vigencia_verificada) else ""))

        def de_la_pagina(nombre, calle, altura, direccion_texto):
            """Un nombre de la página: primero se busca en la capa; si no, se geocodifica."""
            en_capa = casi_igual(nombre, por_clave, restringir=de_la_zona)
            if en_capa is not None:
                if not pd.notna(en_capa.direccion) and direccion_texto:
                    suma(str(en_capa.nombre), direccion_texto, str(en_capa.tipo),
                         str(en_capa.reconocimiento) if pd.notna(en_capa.reconocimiento) else "",
                         en_capa.punto, "punto de la capa de reconocimiento", "la página")
                else:
                    del_reconocimiento(en_capa, "la página")
                return True
            punto = None
            if calle:
                punto, _ = dirs.punto(calle, altura)
            suma(nombre, direccion_texto, "", "", punto,
                 "altura de puerta contra el callejero (centro de cuadra, ±½ cuadra)"
                 if punto is not None else
                 ("la calle no resuelve en el callejero" if calle else "sin ubicar"),
                 "la página")
            return False

        # (a) la capa de reconocimiento, sobre la ZONA
        for r in con_punto.itertuples():
            if zona.covers(r.punto):
                del_reconocimiento(r, "la capa de reconocimiento")

        # (b) lo que la página nombra
        texto = fichas.hitos_conocidos.get(pid) if pid in fichas.index else None
        for item in lee_pagina(texto, dirs):
            # «Casa Veltri y Presencia (Michelin)» son dos, «Cantina y Teatro Tai» es uno. La
            # única forma honesta de distinguirlos es preguntarle a la capa: se parte sólo si
            # las dos mitades existen por separado y son distintas.
            partes = re.split(r"\s+y\s+(?=[A-ZÁÉÍÓÚÑ])", item["nombre"])
            if len(partes) == 2:
                a = casi_igual(partes[0], por_clave, restringir=de_la_zona)
                b = casi_igual(partes[1], por_clave, restringir=de_la_zona)
                if a is not None and b is not None and a.hito_id != b.hito_id:
                    del_reconocimiento(a, "la página")
                    del_reconocimiento(b, "la página")
                    continue
            de_la_pagina(item["nombre"], item["calle"], item["altura"],
                         item["direccion_texto"])

        # (c) los referentes que la ronda 17 ya había curado para su zona
        for nom, calle, altura in referentes_r17.get(pid, []):
            de_la_pagina(nom, calle, altura, f"{calle} {altura}")

        # medir
        claves_via_b = {clave(r.nombre) for r in via_b_zona[zid]}
        for k, (_, fila) in vistos.por_clave.items():
            punto = fila.pop("_punto")
            if punto is None:
                fila.update(dentro_del_borde="sin ubicar", distancia_m="")
            else:
                dentro = borde.covers(punto)
                fila.update(dentro_del_borde="si" if dentro else "no",
                            distancia_m=0.0 if dentro else round(borde.distance(punto), 1))
            sostiene = k in claves_via_b
            fila["sostiene_condicion_historia"] = (
                "si" if sostiene and fila["tipo"] in TIPOS_TRAYECTORIA else
                ("si (distinción contemporánea, no trayectoria)" if sostiene else "no"))
            fila["borde_tentativo"] = "si" if pid in tentativos else "no"
            fila["borde_es_propio"] = "no" if pid in sin_borde_propio else "si"
            filas.append(fila)

    campos = ["polo", "establecimiento", "direccion", "tipo", "reconocimiento",
              "dentro_del_borde", "distancia_m", "sostiene_condicion_historia",
              "zona_id", "origen_del_dato", "ubicacion_metodo", "estado_vigencia",
              "borde_tentativo", "borde_es_propio"]
    filas.sort(key=lambda f: (f["polo"], f["dentro_del_borde"] != "no",
                              -(f["distancia_m"] or 0) if isinstance(f["distancia_m"], float)
                              else 0, f["establecimiento"]))
    with (SALIDA / "anclas_dentro_y_fuera.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)

    # ------------------------------------------------------------------ el resultado
    print("=" * 98)
    print("EL RESULTADO · qué páginas dejan afuera el establecimiento que las sostiene")
    print("=" * 98 + "\n")

    d = pd.DataFrame(filas)
    d["trayectoria"] = d.sostiene_condicion_historia == "si"
    d["sostiene"] = d.sostiene_condicion_historia.str.startswith("si")
    problema = d[d.trayectoria & (d.dentro_del_borde == "no")]
    problema_amplio = d[d.sostiene & (d.dentro_del_borde == "no")]
    polos_con_problema = sorted(problema.polo.unique())
    print(f"anclas medidas: {len(d)} en {d.polo.nunique()} polos")
    print(f"  adentro del borde        : {(d.dentro_del_borde == 'si').sum()}")
    print(f"  afuera del borde         : {(d.dentro_del_borde == 'no').sum()}")
    print(f"  sin ubicar               : {(d.dentro_del_borde == 'sin ubicar').sum()}")
    print(f"  sostienen la vía B       : {d.sostiene.sum()}   "
          f"(de trayectoria {d.trayectoria.sum()}, "
          f"de distinción contemporánea {d.sostiene.sum() - d.trayectoria.sum()})")
    print(f"\n  LA CIFRA DEL CONTROL: {len(problema)} establecimientos con historia —Bar Notable,")
    print(f"  restaurante icónico, pizzería emblemática, heladería histórica— sostienen la")
    print(f"  condición de su zona y quedan FUERA del borde de su polo, en "
          f"{len(polos_con_problema)} de {d.polo.nunique()} páginas.")
    print(f"  Son {problema.establecimiento.nunique()} establecimientos distintos: diez aparecen")
    print(f"  en dos páginas cada uno porque dos polos se recortan de la misma zona -La Boca,")
    print(f"  Barracas y Pompeya tienen dos polos cada una-, y la evidencia de la zona la")
    print(f"  invocan las dos páginas.")
    print(f"  Contando también las distinciones contemporáneas -MICHELIN y rankings-, son "
          f"{len(problema_amplio)}\n  filas en {problema_amplio.polo.nunique()} páginas.\n")

    for polo in polos_con_problema:
        sub = problema[problema.polo == polo].sort_values("distancia_m", ascending=False)
        adentro = d[(d.polo == polo) & d.trayectoria & (d.dentro_del_borde == "si")]
        print(f"  {polo}")
        print(f"      con historia: {len(sub)} afuera, {len(adentro)} adentro"
              + ("   ← el borde no contiene NINGUNO" if len(adentro) == 0 else ""))
        for r in sub.itertuples():
            print(f"        {r.establecimiento[:38]:<40} {r.tipo[:22]:<24} "
                  f"a {r.distancia_m:>7,.0f} m")
    print()

    sin_ninguno = []
    for polo in sorted(d.polo.unique()):
        sub = d[(d.polo == polo) & d.trayectoria]
        if len(sub) and not (sub.dentro_del_borde == "si").any():
            sin_ninguno.append((polo, len(sub)))
    print(f"  EL CASO GRAVE —el borde no contiene NI UNO de los establecimientos con historia")
    print(f"  sobre los que su zona se apoya—: {len(sin_ninguno)} páginas")
    for polo, n in sin_ninguno:
        print(f"      {polo}  ({n} afuera)")

    print("\n" + "-" * 98)
    print("LOS 41, UNO POR UNO")
    print("-" * 98)
    print(f"  {'polo':<46} {'anclas':>6} {'dentro':>6} {'fuera':>6} {'s/ub':>5} "
          f"{'historia dentro/fuera':>22}")
    for polo in sorted(d.polo.unique()):
        sub = d[d.polo == polo]
        h = sub[sub.trayectoria]
        marca = ""
        if len(h) and not (h.dentro_del_borde == "si").any():
            marca = "  ←"
        print(f"  {polo[:44]:<46} {len(sub):>6} {(sub.dentro_del_borde == 'si').sum():>6} "
              f"{(sub.dentro_del_borde == 'no').sum():>6} "
              f"{(sub.dentro_del_borde == 'sin ubicar').sum():>5} "
              f"{(h.dentro_del_borde == 'si').sum():>10} / "
              f"{(h.dentro_del_borde == 'no').sum():<8}{marca}")
    faltantes = sorted(set(bordes) - set(x.split(" · ")[0] for x in d.polo.unique()))
    if faltantes:
        print(f"\n  sin ninguna ancla en ninguna de las dos fuentes: {', '.join(faltantes)}")

    print("\n" + "-" * 98)
    print("LO QUE LA PÁGINA NOMBRA Y EL REPOSITORIO NO SABE DÓNDE ESTÁ")
    print("-" * 98)
    sinub = d[d.dentro_del_borde == "sin ubicar"]
    print(f"  {len(sinub)} anclas. No se las ubica en el centroide de nada y no se las descarta:")
    for r in sinub.itertuples():
        print(f"      {r.polo[:40]:<42} {r.establecimiento[:32]:<34} {r.ubicacion_metodo}")

    resumen = dict(
        fecha=HOY, anclas=len(d), polos=int(d.polo.nunique()),
        adentro=int((d.dentro_del_borde == "si").sum()),
        afuera=int((d.dentro_del_borde == "no").sum()),
        sin_ubicar=int((d.dentro_del_borde == "sin ubicar").sum()),
        sostienen_via_B=int(d.sostiene.sum()),
        sostienen_con_historia=int(d.trayectoria.sum()),
        con_historia_y_quedan_afuera=len(problema),
        con_historia_afuera_establecimientos_distintos=int(problema.establecimiento.nunique()),
        sostienen_via_B_y_quedan_afuera=len(problema_amplio),
        paginas_con_el_problema=len(polos_con_problema),
        paginas_sin_ninguno_adentro=[p for p, _ in sin_ninguno],
        polos_con_el_problema=polos_con_problema)
    (SALIDA / "anclas_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nEscrito: anclas_dentro_y_fuera.csv ({len(filas)} filas) · anclas_resumen.json")


if __name__ == "__main__":
    main()
