#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cartografia vectorial nativa del Atlas V2 (bloques B1 y B2).

Dibuja las 22 referencias, las 7 vistas de detalle y el mapa general de la Ciudad
directamente sobre el canvas de reportlab, como trazos vectoriales y texto real del PDF.
No se embebe ningun raster: por eso el QA de cierre puede auditar lo que dicen los mapas.

Paleta C (D-4): colores institucionales aprobados + trama por familia, para que las cinco
familias sigan siendo distinguibles cuando el Atlas se imprime en blanco y negro.

Registro visual (AG-1):
  continuo -> envolvente derivada de puntos observados o geometria editorial cerrada
  punteado -> area de consulta declarada, no envolvente de oferta observada
"""

from __future__ import annotations

import math
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import geopandas as gpd
import shapely
from reportlab.lib.colors import HexColor, white
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import linemerge, unary_union

MM = 72 / 25.4
CRS_M = "EPSG:5347"

FAMILIA_COLOR = {
    "polo": "#1F3B57",
    "multiparte": "#2C7FB8",
    "eje": "#C0762B",
    "segmentada": "#2D7A68",
    "dispersa": "#7353A6",
}
FAMILIA_ETIQUETA = {
    "polo": "Polo",
    "multiparte": "Polo con subzonas o partes",
    "eje": "Eje o corredor",
    "segmentada": "Área segmentada",
    "dispersa": "Referencia dispersa",
}
# Trama por familia: angulo en grados y paso en puntos. None = relleno liso.
FAMILIA_TRAMA = {
    "polo": None,
    "multiparte": (45, 3.4),
    "eje": (0, 3.4),
    "segmentada": (90, 3.4),
    "dispersa": (135, 3.4),
}

GRIS_BARRIO = HexColor("#F4F7FA")
GRIS_BORDE = HexColor("#DFE5EB")
GRIS_CALLE = HexColor("#E3E9EF")
GRIS_CALLE_PPAL = HexColor("#D2DAE3")
AZUL_TEXTO = HexColor("#1F3B57")
GRIS_TEXTO = HexColor("#555555")
GRIS_ROTULO_CALLE = HexColor("#6B7480")
GRIS_CALLE_ROTULADA = HexColor("#BAC4CF")
GRIS_RESTO = HexColor("#B9C4D0")      # el resto de la referencia en las paginas de zoom

# Texto que cambia entre la edicion tecnica y la de conduccion. El generador lo fija
# antes de dibujar; el valor por defecto es el de la edicion tecnica.
ROTULO_EDITORIAL: dict[str, str] = {}
LEYENDA_AREA = "área de la referencia"
LEYENDA_COMPONENTE = "componente interno"
LEYENDA_CALLE = "calle de referencia"
NOTA_TRAZO_PUNTEADO = ("Trazo punteado: área de consulta declarada, no envolvente de "
                       "oferta observada.")

# ---------------------------------------------------------------------------------------
# F-01 · Calles de referencia rotuladas
#
# Cada mapa rotula las calles que su propia linea "Que muestra este mapa" nombra, tomadas
# del callejero oficial GCBA. Son basemap, no producto: se dibujan en gris y se rotulan en
# gris, nunca con el color de la familia, y no entran en ninguna envolvente.
#
# D-02 · Monroe y Congreso entran aqui para R17: la ficha nombra tres ejes y el mapa dibuja
# uno solo. Rotularlas como calles del callejero elimina la disonancia sin convertirlas en
# ejes de producto, que es exactamente lo que BLOQUEADO-02 mantiene sin decidir.
# ---------------------------------------------------------------------------------------

CALLE_ROTULO = {
    "CORRIENTES AV.": "Av. Corrientes",
    "9 DE JULIO AV.": "Av. 9 de Julio",
    "CALLAO AV.": "Av. Callao",
    "DEFENSA": "Defensa",
    "CABILDO AV.": "Av. Cabildo",
    "JURAMENTO AV.": "Av. Juramento",
    "THAMES": "Thames",
    "GURRUCHAGA": "Gurruchaga",
    "NEWBERY, JORGE AV.": "Av. Jorge Newbery",
    "DORREGO AV.": "Av. Dorrego",
    "GOYENA, PEDRO AV.": "Av. Pedro Goyena",
    "CASEROS AV.": "Av. Caseros",
    "BOEDO AV.": "Av. Boedo",
    "DONADO": "Donado",
    "HOLMBERG": "Holmberg",
    "TRIUNVIRATO AV.": "Av. Triunvirato",
    "MONROE AV.": "Av. Monroe",
    "MONROE": "Monroe",
    "CONGRESO AV.": "Av. Congreso",
    "CONGRESO": "Congreso",
    "ESMERALDA": "Esmeralda",
    "PARAGUAY": "Paraguay",
    "LACROZE, FEDERICO AV.": "Av. Federico Lacroze",
    "DEL LIBERTADOR AV.": "Av. del Libertador",
    "ALVAREZ THOMAS AV.": "Av. Álvarez Thomas",
    "GARCIA DEL RIO AV.": "Av. García del Río",
    "GARCIA DEL RIO": "García del Río",
    "PAZ, GRAL. AV.": "Av. Gral. Paz",
    # S-02/S-03 · avenidas del entorno de las tres partes de Palermo. Salen del mismo
    # callejero oficial GCBA que el resto: son basemap para ubicarse dentro del zoom,
    # no ejes de producto ni delimitaciones de las subzonas.
    "SCALABRINI ORTIZ, RAUL AV.": "Av. Raúl Scalabrini Ortiz",
    "JUSTO, JUAN B. AV.": "Av. Juan B. Justo",
    "SANTA FE AV.": "Av. Santa Fe",
    "CORDOBA AV.": "Av. Córdoba",
    "CAMPOS, LUIS M. AV.": "Av. Luis María Campos",
    "BULLRICH, INT. AV.": "Av. Intendente Bullrich",
}

# Solo se rotula lo que la linea "Que muestra este mapa" de esa pagina nombra.
CALLES_POR_MAPA = {
    "R02": ["CORRIENTES AV.", "9 DE JULIO AV.", "CALLAO AV."],
    "R03": ["DEFENSA"],
    "R05": ["CABILDO AV.", "JURAMENTO AV."],
    "R08": ["THAMES", "GURRUCHAGA"],
    "R09": ["NEWBERY, JORGE AV.", "DORREGO AV."],
    "R10": ["GOYENA, PEDRO AV."],
    "R11": ["CASEROS AV."],
    "R13": ["CORRIENTES AV."],
    "R14": ["BOEDO AV."],
    "R16": ["DONADO", "HOLMBERG"],
    "R17": ["TRIUNVIRATO AV.", "MONROE AV.", "MONROE", "CONGRESO AV.", "CONGRESO"],
    "R18": ["ESMERALDA", "PARAGUAY"],
    "R19": ["LACROZE, FEDERICO AV.", "CABILDO AV.", "DEL LIBERTADOR AV.", "ALVAREZ THOMAS AV."],
    "R20": ["GARCIA DEL RIO AV.", "GARCIA DEL RIO", "CABILDO AV."],
    "R02_R13_CONTEXTO_CORRIENTES_ABASTO.png": ["CORRIENTES AV."],
    "R19_DETALLE_LACROZE_CABILDO.png": ["LACROZE, FEDERICO AV.", "CABILDO AV."],
    "R20_DETALLE_CABILDO_PARQUE_SAAVEDRA.png": ["GARCIA DEL RIO AV.", "GARCIA DEL RIO",
                                                "CABILDO AV."],
    "R01_DETALLE_PALERMO_SOHO.png": ["SCALABRINI ORTIZ, RAUL AV.", "JUSTO, JUAN B. AV.",
                                     "SANTA FE AV.", "CORDOBA AV."],
    "R01_DETALLE_PALERMO_HOLLYWOOD.png": ["JUSTO, JUAN B. AV.", "CORDOBA AV.",
                                          "SANTA FE AV.", "LACROZE, FEDERICO AV."],
    "R01_DETALLE_LAS_CANITAS.png": ["DEL LIBERTADOR AV.", "CAMPOS, LUIS M. AV.",
                                    "CABILDO AV.", "BULLRICH, INT. AV."],
}

# Paginas de zoom que amplian UNA parte declarada de una referencia.
SUBZONA_DE_DETALLE = {
    "R01_DETALLE_PALERMO_SOHO.png": ("R01", "Palermo Soho"),
    "R01_DETALLE_PALERMO_HOLLYWOOD.png": ("R01", "Palermo Hollywood"),
    "R01_DETALLE_LAS_CANITAS.png": ("R01", "Las Cañitas"),
}


# ---------------------------------------------------------------------------------------
# Transformacion y utilidades de dibujo
# ---------------------------------------------------------------------------------------

class Vista:
    """Traduce coordenadas metricas EPSG:5347 a puntos de la pagina."""

    def __init__(self, bounds, x, y, w, h):
        minx, miny, maxx, maxy = bounds
        dx, dy = max(maxx - minx, 1.0), max(maxy - miny, 1.0)
        self.k = min(w / dx, h / dy)
        self.x0 = x + (w - dx * self.k) / 2 - minx * self.k
        self.y0 = y + (h - dy * self.k) / 2 - miny * self.k
        self.rect = (x, y, w, h)
        self.bounds_geo = bounds

    def __call__(self, px, py):
        return self.x0 + px * self.k, self.y0 + py * self.k

    def metros_a_puntos(self, m):
        return m * self.k

    @property
    def extent(self):
        x, y, w, h = self.rect
        return box(*self.inv(x, y), *self.inv(x + w, y + h))

    def inv(self, px, py):
        return (px - self.x0) / self.k, (py - self.y0) / self.k


def _anillos(geom):
    if geom.is_empty:
        return []
    piezas = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    salida = []
    for p in piezas:
        salida.append((list(p.exterior.coords), [list(r.coords) for r in p.interiors]))
    return salida


def solo_poligonos(geom):
    """Descarta lo que una diferencia deja como linea o punto suelto."""
    if geom is None or geom.is_empty:
        return Polygon()
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    piezas = [g for g in getattr(geom, "geoms", []) if g.geom_type in ("Polygon", "MultiPolygon")]
    return unary_union(piezas) if piezas else Polygon()


def path_de(c, geom, vista):
    p = c.beginPath()
    for ext, ints in _anillos(geom):
        for anillo in [ext, *ints]:
            for i, (px, py) in enumerate(anillo):
                X, Y = vista(px, py)
                (p.moveTo if i == 0 else p.lineTo)(X, Y)
            p.close()
    return p


def trama(c, geom, vista, angulo, paso, color, ancho=0.35, alpha=0.55):
    """Trama vectorial recortada al poligono: el segundo indicio para lectura en gris."""
    if geom.is_empty:
        return
    c.saveState()
    c.clipPath(path_de(c, geom, vista), stroke=0, fill=0)
    x, y, w, h = vista.rect
    minx, miny, maxx, maxy = geom.bounds
    X0, Y0 = vista(minx, miny)
    X1, Y1 = vista(maxx, maxy)
    diag = math.hypot(X1 - X0, Y1 - Y0) + 8
    cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
    rad = math.radians(angulo)
    dx, dy = math.cos(rad), math.sin(rad)
    nx, ny = -dy, dx
    c.setStrokeColor(color)
    c.setStrokeAlpha(alpha)
    c.setLineWidth(ancho)
    pasos = int(diag / paso) + 2
    for i in range(-pasos, pasos + 1):
        ox, oy = cx + nx * i * paso, cy + ny * i * paso
        c.line(ox - dx * diag, oy - dy * diag, ox + dx * diag, oy + dy * diag)
    c.setStrokeAlpha(1)
    c.restoreState()


def texto_con_halo(c, x, y, texto, fuente, tamano, color, halo=white, grosor=1.5,
                   centrado=True, angulo=0.0):
    """Rotulo legible sobre el mapa, con halo dibujado por desplazamiento.

    No se usa el modo de render de texto con contorno: reportlab no vuelve a emitir el
    operador cuando el modo coincide con el que ya cree tener, y el trazo blanco del
    objeto anterior termina comiendose el glifo siguiente. Ocho copias desplazadas del
    texto en blanco, y el texto real encima, funcionan en cualquier visor.

    `angulo` (grados) permite acompanar el trazado de una calle o de un borde.
    """
    c.saveState()
    if angulo:
        c.translate(x, y)
        c.rotate(angulo)
        x, y = 0.0, 0.0
    c.setFont(fuente, tamano)
    ancho = c.stringWidth(texto, fuente, tamano)
    x0 = x - ancho / 2 if centrado else x
    c.setFillColor(halo)
    for dx in (-grosor, 0, grosor):
        for dy in (-grosor, 0, grosor):
            if dx or dy:
                c.drawString(x0 + dx, y + dy, texto)
    c.setFillColor(color)
    c.drawString(x0, y, texto)
    c.restoreState()


def _lineas(geom):
    """Aplana a una lista de LineString."""
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type == "LineString":
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if g.geom_type == "LineString"]


def _unir_tramos(geom):
    """linemerge tolerante: acepta una sola linea o una coleccion mixta."""
    partes = _lineas(geom)
    if len(partes) <= 1:
        return partes
    return _lineas(linemerge(partes)) or partes


def rumbo(linea, fraccion=0.5, tramo_m=350.0):
    """Punto y angulo de dibujo (grados, siempre legible) sobre una linea metrica."""
    largo = linea.length
    d = max(min(largo * fraccion, largo), 0.0)
    a = linea.interpolate(max(d - tramo_m, 0.0))
    b = linea.interpolate(min(d + tramo_m, largo))
    ang = math.degrees(math.atan2(b.y - a.y, b.x - a.x))
    if ang > 90:
        ang -= 180
    elif ang < -90:
        ang += 180
    return linea.interpolate(d), ang


# ---------------------------------------------------------------------------------------
# Cartografo
# ---------------------------------------------------------------------------------------

class Cartografo:
    def __init__(self, repo: Path, capas: Path):
        self.env = gpd.read_file(capas / "envolventes_editoriales_v2.geojson").to_crs(CRS_M)
        self.comp = gpd.read_file(capas / "componentes_editoriales_v2.geojson").to_crs(CRS_M)
        self.barrios = gpd.read_file(repo / "data/raw/geo_barrios.geojson").to_crs(CRS_M)
        self.comunas = gpd.read_file(repo / "data/raw/geo_comunas.geojson").to_crs(CRS_M)
        calles = gpd.read_file(
            repo / "outputs/polos_gastro/FASE5-29/fase15_mapas_callejeros_v3/assets"
                 / "callejero_gcba_2026_06_02.geojson").to_crs(CRS_M)
        self.calles = calles
        self.nombres_calle = calles["nomoficial"].astype(str)
        self.troncales = calles[calles["red_jerarq"].astype(str).str.contains("TRONCAL|PRINCIPAL", na=False)]
        self.caba = unary_union(list(self.barrios.geometry))
        self.escalas: dict[str, int] = {}
        self.rotulos_calle: dict[str, list[str]] = {}

    def fila(self, rid: str):
        return self.env[self.env.referencia_id == rid].iloc[0]

    @staticmethod
    def rotulo(nombre: str) -> str:
        """Ortografia de publicacion. Solo acentua y normaliza guiones: no renombra nada.

        `ROTULO_EDITORIAL` es la unica excepcion: la edicion de conduccion reemplaza el
        rotulo que nombraba un objeto interno del proyecto por lo que efectivamente
        nombra en el territorio. No cambia ninguna geometria ni ninguna cifra.
        """
        nombre = ROTULO_EDITORIAL.get(str(nombre), str(nombre))
        arreglos = {
            "Nucleo Dorrego": "Núcleo Dorrego",
            "Primera Junta-Mercado del Progreso": "Primera Junta–Mercado del Progreso",
            "Donado-Holmberg": "Donado–Holmberg",
            "Garcia del Rio": "García del Río",
            "Villa Pueyrredon": "Villa Pueyrredón",
            "Esmeralda-Paraguay": "Esmeralda–Paraguay",
        }
        return arreglos.get(str(nombre), str(nombre))

    # -- contexto ------------------------------------------------------------------
    def _contexto(self, c, vista, con_calles=True):
        ext = vista.extent
        loc = self.barrios[self.barrios.intersects(ext)]
        if not loc.empty:
            c.setFillColor(GRIS_BARRIO)
            c.setStrokeColor(GRIS_BORDE)
            c.setLineWidth(0.4)
            for g in loc.geometry:
                c.drawPath(path_de(c, g, vista), fill=1, stroke=1)
        if not con_calles:
            return
        sub = self.calles[self.calles.intersects(ext)]
        c.setStrokeColor(GRIS_CALLE)
        c.setLineWidth(0.25)
        for linea in sub.geometry:
            for parte in (linea.geoms if linea.geom_type.startswith("Multi") else [linea]):
                cs = list(parte.coords)
                p = c.beginPath()
                for i, (px, py) in enumerate(cs):
                    X, Y = vista(px, py)
                    (p.moveTo if i == 0 else p.lineTo)(X, Y)
                c.drawPath(p, fill=0, stroke=1)

    # -- calles de referencia rotuladas (F-01 / D-02) --------------------------------
    def _rotular_calles(self, c, vista, clave: str, cerca=None, evitar=()) -> list[str]:
        """Rotula, en gris de basemap, las calles que el texto de la pagina nombra.

        No agrega geometria de producto: usa el trazado del callejero oficial GCBA que
        el mapa ya dibuja de fondo, lo resalta un tono y le pone el nombre encima.
        """
        pedidas = CALLES_POR_MAPA.get(clave, [])
        if not pedidas:
            return []
        x, y, w, h = vista.rect
        ext = vista.extent
        if cerca is not None and not cerca.is_empty:
            ext = ext.intersection(cerca.buffer(400.0)) or ext
        puestos: list[str] = []
        # El rotulo de la referencia manda: la calle busca otro punto de la traza.
        ocupados: list[tuple[float, float]] = list(evitar)
        def raiz(nombre: str) -> str:
            return nombre.replace("Av. ", "").casefold()

        for nombre_oficial in pedidas:
            etiqueta = CALLE_ROTULO[nombre_oficial]
            # "GARCIA DEL RIO" y "GARCIA DEL RIO AV." son la misma calle: se rotula una vez.
            if any(raiz(p) == raiz(etiqueta) for p in puestos):
                continue
            sel = self.calles[self.nombres_calle == nombre_oficial]
            if sel.empty:
                continue
            recortado = unary_union([g for g in sel.geometry if g.intersects(ext)])
            if recortado.is_empty:
                continue
            recortado = recortado.intersection(ext)
            tramos = _unir_tramos(recortado)
            if not tramos:
                continue
            linea = max(tramos, key=lambda g: g.length)
            tam = 6.6
            ancho_rotulo = c.stringWidth(etiqueta, "AtlasSans-Bold", tam)
            if vista.metros_a_puntos(linea.length) < ancho_rotulo + 10:
                continue
            # Resalta el trazado un tono sobre el resto del callejero.
            c.saveState()
            c.setStrokeColor(GRIS_CALLE_ROTULADA)
            c.setLineWidth(1.5)
            for parte in _lineas(recortado):
                p = c.beginPath()
                for i, (px, py) in enumerate(parte.coords):
                    X, Y = vista(px, py)
                    (p.moveTo if i == 0 else p.lineTo)(X, Y)
                c.drawPath(p, fill=0, stroke=1)
            c.restoreState()
            colocado = False
            for fraccion in (0.5, 0.32, 0.68, 0.18, 0.82):
                pt, ang = rumbo(linea, fraccion)
                X, Y = vista(pt.x, pt.y)
                if not (x + ancho_rotulo / 2 + 3 < X < x + w - ancho_rotulo / 2 - 3
                        and y + 14 < Y < y + h - 8):
                    continue
                if any(math.hypot(X - ox, Y - oy) < 34 for ox, oy in ocupados):
                    continue
                texto_con_halo(c, X, Y, etiqueta, "AtlasSans-Bold", tam, GRIS_ROTULO_CALLE,
                               grosor=1.3, angulo=ang)
                ocupados.append((X, Y))
                puestos.append(etiqueta)
                colocado = True
                break
            if not colocado:
                continue
        self.rotulos_calle[clave] = puestos
        return puestos

    # -- area de una referencia ----------------------------------------------------
    def _area(self, c, geom, familia, punteado, alpha=0.28, borde=1.3):
        pass  # sustituido por _pintar; se conserva la firma por claridad historica

    def _pintar(self, c, geom, vista, familia, punteado, alpha=0.30, borde=1.35):
        color = HexColor(FAMILIA_COLOR[familia])
        p = path_de(c, geom, vista)
        c.saveState()
        c.setFillColor(color)
        c.setFillAlpha(alpha)
        c.setStrokeAlpha(0)
        c.drawPath(p, fill=1, stroke=0)
        c.setFillAlpha(1)
        c.restoreState()
        t = FAMILIA_TRAMA[familia]
        if t:
            trama(c, geom, vista, t[0], t[1], color)
        c.saveState()
        c.setStrokeColor(color)
        c.setLineWidth(borde)
        if punteado:
            c.setDash([3.4, 2.2])
        c.drawPath(path_de(c, geom, vista), fill=0, stroke=1)
        c.setDash([])
        c.restoreState()

    # -- barra de escala (D-7) -----------------------------------------------------
    def _escala(self, c, vista, rid=None):
        x, y, w, h = vista.rect
        ancho_m = w / vista.k
        metros = 250 if ancho_m < 2600 else 500
        if rid:
            self.escalas[rid] = metros
        largo = vista.metros_a_puntos(metros)
        px, py = x + 8, y + 10
        c.setStrokeColor(HexColor("#111827"))
        c.setLineWidth(2.6)
        c.line(px, py, px + largo, py)
        c.setLineWidth(0.8)
        c.line(px, py - 2.4, px, py + 2.4)
        c.line(px + largo, py - 2.4, px + largo, py + 2.4)
        c.setFont("AtlasSans", 7)
        c.setFillColor(HexColor("#111827"))
        c.drawString(px + largo + 4, py - 2.4, f"{metros} m")
        return metros

    def _norte(self, c, vista):
        x, y, w, h = vista.rect
        px, py = x + w - 14, y + h - 26
        c.setStrokeColor(HexColor("#111827"))
        c.setFillColor(HexColor("#111827"))
        c.setLineWidth(1.2)
        c.line(px, py, px, py + 13)
        p = c.beginPath()
        p.moveTo(px, py + 18)
        p.lineTo(px - 3.2, py + 11)
        p.lineTo(px + 3.2, py + 11)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.setFont("AtlasSans-Bold", 7)
        c.drawCentredString(px, py - 8, "N")

    # -- mapa principal de una referencia ------------------------------------------
    def mapa_referencia(self, c, rid: str, x, y, w, h) -> dict:
        f = self.fila(rid)
        geom = f.geometry
        minx, miny, maxx, maxy = geom.bounds
        pad = 0.18 * max(maxx - minx, maxy - miny)
        vista = Vista((minx - pad, miny - pad, maxx + pad, maxy + pad), x, y, w, h)

        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)
        self._contexto(c, vista)
        self._pintar(c, geom, vista, f.familia, f.trazo == "punteado")

        comps = self.comp[self.comp.referencia_id == rid]
        if len(comps) > 1:
            anclas = [cp.geometry.representative_point() for _, cp in comps.iterrows()]
        else:
            piezas_ = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
            anclas = [max(piezas_, key=lambda g: g.area).representative_point()]
        calles = self._rotular_calles(c, vista, rid, cerca=geom,
                                      evitar=[vista(q.x, q.y) for q in anclas])

        etiquetas = []
        if len(comps) > 1:
            c.setFont("AtlasSans-Bold", 6.6)
            for _, cp in comps.iterrows():
                pt = cp.geometry.representative_point()
                X, Y = vista(pt.x, pt.y)
                if not (x + 2 < X < x + w - 2 and y + 12 < Y < y + h - 6):
                    continue
                texto_con_halo(c, X, Y, self.rotulo(cp.componente), "AtlasSans-Bold", 6.6, AZUL_TEXTO)
                etiquetas.append(self.rotulo(cp.componente))
        else:
            piezas = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
            pt = max(piezas, key=lambda g: g.area).representative_point()
            X, Y = vista(pt.x, pt.y)
            texto_con_halo(c, X, Y, self.rotulo(f.nombre), "AtlasSans-Bold", 8.2, AZUL_TEXTO)
            etiquetas.append(self.rotulo(f.nombre))

        metros = self._escala(c, vista, rid)
        self._norte(c, vista)
        c.restoreState()
        c.setStrokeColor(GRIS_BORDE)
        c.setLineWidth(0.7)
        c.rect(x, y, w, h, fill=0, stroke=1)
        return {"escala_m": metros, "etiquetas": etiquetas, "calles": calles}

    # -- mapa general de la Ciudad (B1) --------------------------------------------
    def mapa_general(self, c, x, y, w, h, paginas: dict[str, int]) -> dict:
        minx, miny, maxx, maxy = self.caba.bounds
        pad = 0.02 * (maxx - minx)
        bounds = (minx - pad, miny - pad, maxx + pad, maxy + pad)
        # El alto se ajusta a la proporcion real de la Ciudad y el mapa se apoya arriba:
        # asi no queda una banda blanca entre el mapa y la leyenda.
        proporcion = (bounds[3] - bounds[1]) / (bounds[2] - bounds[0])
        h_util = min(h, w * proporcion)
        vista = Vista(bounds, x, y + h - h_util, w, h_util)

        c.saveState()
        p = c.beginPath()
        p.rect(x, y + h - h_util, w, h_util)
        c.clipPath(p, stroke=0, fill=0)

        # Comunas en gris muy tenue
        c.setFillColor(HexColor("#F8FAFC"))
        c.setStrokeColor(HexColor("#E4EAF0"))
        c.setLineWidth(0.5)
        for g in self.comunas.geometry:
            c.drawPath(path_de(c, g, vista), fill=1, stroke=1)
        # Costa y Riachuelo: el contorno de la Ciudad es su ancla
        c.setStrokeColor(HexColor("#8FA3B8"))
        c.setLineWidth(1.25)
        c.drawPath(path_de(c, self.caba, vista), fill=0, stroke=1)
        anclas = self._anclas_geograficas(c, vista)

        orden = self.env.sort_values(["z_orden", "referencia_id"])
        for _, f in orden.iterrows():
            self._pintar(c, f.geometry, vista, f.familia, f.trazo == "punteado",
                         alpha=0.42, borde=0.9)
        for _, f in orden.iterrows():
            piezas = list(f.geometry.geoms) if f.geometry.geom_type == "MultiPolygon" else [f.geometry]
            pt = max(piezas, key=lambda g: g.area).representative_point()
            X, Y = vista(pt.x, pt.y)
            color = HexColor(FAMILIA_COLOR[f.familia])
            c.setFillColor(color)
            c.setStrokeColor(white)
            c.setLineWidth(0.9)
            c.circle(X, Y, 6.2, fill=1, stroke=1)
            c.setFillColor(white)
            c.setFont("AtlasSans-Bold", 6.4)
            c.drawCentredString(X, Y - 2.2, f.referencia_id[1:])
        c.restoreState()
        return {"escala": "vista unica de la Ciudad", "alto_usado": h_util, "anclas": anclas}

    # -- anclas geograficas del mapa general (M-02) ---------------------------------
    def _anclas_geograficas(self, c, vista) -> list[str]:
        """Numero de comuna, Rio de la Plata, Av. Gral. Paz y Riachuelo.

        Sin estas anclas la p6 es una silueta con manchas para quien no maneja la
        geografia fina de la Ciudad. Las cuatro salen de fuentes que el Atlas ya usa:
        el poligono oficial de comunas, el callejero GCBA y el propio contorno de la
        Ciudad, cuyos bordes oeste y sur son la avenida y el riacho.
        """
        x, y, w, h = vista.rect
        puestas: list[str] = []

        # 1. Numero de las 15 comunas sobre el gris. Se aparta del disco numerado de una
        #    referencia cuando caen encima: manda el numero de la referencia.
        discos = []
        for _, f in self.env.iterrows():
            piezas = list(f.geometry.geoms) if f.geometry.geom_type == "MultiPolygon" else [f.geometry]
            q = max(piezas, key=lambda g: g.area).representative_point()
            discos.append(vista(q.x, q.y))
        for _, com in self.comunas.iterrows():
            pt = com.geometry.representative_point()
            X, Y = vista(pt.x, pt.y)
            for dx_, dy_ in ((0, 0), (0, 15), (16, 0), (0, -15), (-16, 0), (16, 15), (-16, -15)):
                cx_, cy_ = X + dx_, Y + dy_
                if not (x + 6 < cx_ < x + w - 6 and y + 6 < cy_ < y + h - 6):
                    continue
                if any(math.hypot(cx_ - bx, cy_ - by) < 13 for bx, by in discos):
                    continue
                if not com.geometry.contains(Point(*vista.inv(cx_, cy_))):
                    continue
                texto_con_halo(c, cx_, cy_, str(int(com.comuna)), "AtlasSans-Bold", 7.4,
                               HexColor("#98A6B5"), grosor=1.2)
                break
        puestas.append("comunas 1-15")

        # 2. Av. Gral. Paz: trazado real del callejero oficial, resaltado y rotulado.
        gp = self.calles[self.nombres_calle == "PAZ, GRAL. AV."]
        if not gp.empty:
            union = unary_union(list(gp.geometry))
            c.saveState()
            c.setStrokeColor(HexColor("#AEBBC8"))
            c.setLineWidth(1.6)
            for parte in _lineas(union):
                p = c.beginPath()
                for i, (px, py) in enumerate(parte.coords):
                    X, Y = vista(px, py)
                    (p.moveTo if i == 0 else p.lineTo)(X, Y)
                c.drawPath(p, fill=0, stroke=1)
            c.restoreState()
            tramos = _lineas(linemerge(union)) or _lineas(union)
            if tramos:
                oeste = min(tramos, key=lambda g: g.centroid.x)
                pt, ang = rumbo(oeste, 0.5, tramo_m=900)
                X, Y = vista(pt.x, pt.y)
                texto_con_halo(c, X, Y, "Av. Gral. Paz", "AtlasSans-Bold", 7.2,
                               GRIS_ROTULO_CALLE, grosor=1.4, angulo=ang)
                puestas.append("Av. Gral. Paz")

        # 3. Riachuelo: el limite sur de la Ciudad. Se rotula el borde, no se dibuja
        #    geometria propia: no hay capa de hidrografia para el curso de agua.
        #    El tramo se identifica solo: es el trecho del contorno que esta lejos de la
        #    Gral. Paz y dentro de la franja sur. El resto del perimetro es avenida al
        #    oeste y costa del rio al este.
        borde = self.caba.exterior if self.caba.geom_type == "Polygon" else \
            max(self.caba.geoms, key=lambda g: g.area).exterior
        minx, miny, maxx, maxy = self.caba.bounds
        contorno = shapely.segmentize(LineString(borde.coords), 200.0)
        avenida = unary_union(list(gp.geometry)) if not gp.empty else None
        tramo = [Point(cc) for cc in contorno.coords
                 if (cc[1] - miny) / (maxy - miny) < 0.30
                 and (avenida is None or Point(cc).distance(avenida) > 2000.0)]
        if tramo:
            tramo.sort(key=contorno.project)
            centro = tramo[len(tramo) // 2]
            pt, ang = rumbo(contorno, contorno.project(centro) / contorno.length, tramo_m=1200)
            X, Y = vista(pt.x, pt.y)
            if x + 30 < X < x + w - 30 and y + 16 < Y < y + h - 12:
                texto_con_halo(c, X, Y - 9, "Riachuelo", "AtlasSans-Bold", 7.2,
                               HexColor("#7A8FA6"), grosor=1.4, angulo=ang)
                puestas.append("Riachuelo")

        # 4. Rio de la Plata: sobre el vacio al este de la costa.
        for frac_x, frac_y in ((0.90, 0.80), (0.92, 0.70), (0.88, 0.88), (0.94, 0.60)):
            X, Y = x + w * frac_x, y + h * frac_y
            gx, gy = vista.inv(X, Y)
            if self.caba.distance(Point(gx, gy)) < 900:
                continue
            texto_con_halo(c, X, Y, "Río de la Plata", "AtlasSans-Bold", 7.8,
                           HexColor("#7A8FA6"), grosor=1.5, angulo=-32)
            puestas.append("Río de la Plata")
            break
        return puestas

    # -- vistas de detalle ----------------------------------------------------------
    def mapa_detalle(self, c, clave: str, x, y, w, h, extras) -> dict:
        """Zoom vectorial construido con la misma pila geometrica que los principales."""
        self._clave_detalle = clave
        if clave in SUBZONA_DE_DETALLE:
            rid, parte = SUBZONA_DE_DETALLE[clave]
            return self.mapa_subzona(c, rid, parte, x, y, w, h)
        if clave == "R02_R13_CONTEXTO_CORRIENTES_ABASTO.png":
            a, b = self.fila("R02"), self.fila("R13")
            return self._detalle_par(c, a, b, x, y, w, h)
        if clave == "R08_DETALLE_SATURACIONES_RESIDUALES.png":
            return self._detalle_generico(
                c, self.fila("R08").geometry, "R08", x, y, w, h, ["Villa Crespo"],
                marcas=extras.get("saturaciones", []), marca_radio_m=200)
        if clave == "R12_DETALLE_SUBUNIDADES_SATURACION.png":
            return self._detalle_generico(c, self.fila("R12").geometry, "R12", x, y, w, h,
                                          [], con_componentes=True)
        if clave == "R15_DETALLE_NUCLEO_PERIFERIA.png":
            return self._detalle_generico(c, self.fila("R15").geometry, "R15", x, y, w, h,
                                          ["Devoto"])
        if clave == "R19_DETALLE_LACROZE_CABILDO.png":
            return self._detalle_generico(c, self.fila("R19").geometry, "R19", x, y, w, h,
                                          [], con_componentes=True)
        if clave == "R20_DETALLE_CABILDO_PARQUE_SAAVEDRA.png":
            return self._detalle_generico(c, self.fila("R20").geometry, "R20", x, y, w, h,
                                          ["García del Río"],
                                          control=extras.get("parque_saavedra"),
                                          control_rotulo="Parque Saavedra · control")
        raise RuntimeError(f"Vista de detalle sin cartografia: {clave}")

    def _detalle_generico(self, c, geom, rid, x, y, w, h, etiquetas, *, resaltado=None,
                          con_componentes=False, marcas=(), marca_radio_m=0,
                          control=None, control_rotulo=""):
        piezas = [geom] + ([control] if control is not None else [])
        total = unary_union(piezas)
        minx, miny, maxx, maxy = total.bounds
        pad = 0.20 * max(maxx - minx, maxy - miny)
        vista = Vista((minx - pad, miny - pad, maxx + pad, maxy + pad), x, y, w, h)
        f = self.fila(rid)

        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)
        self._contexto(c, vista)
        if control is not None:
            c.saveState()
            c.setFillColor(HexColor("#2D7A68"))
            c.setFillAlpha(0.16)
            c.drawPath(path_de(c, control, vista), fill=1, stroke=0)
            c.setFillAlpha(1)
            c.setStrokeColor(HexColor("#2D7A68"))
            c.setLineWidth(1.0)
            c.setDash([2.4, 2.0])
            c.drawPath(path_de(c, control, vista), fill=0, stroke=1)
            c.setDash([])
            c.restoreState()
            pt = control.representative_point()
            X, Y = vista(pt.x, pt.y)
            texto_con_halo(c, X, Y, control_rotulo, "AtlasSans-Bold", 6.6, HexColor("#2D7A68"))
        self._pintar(c, geom, vista, f.familia, f.trazo == "punteado")
        calles = self._rotular_calles(c, vista, getattr(self, "_clave_detalle", ""), cerca=geom)

        vistos = list(etiquetas)
        if con_componentes:
            comps = self.comp[self.comp.referencia_id == rid]
            c.setFont("AtlasSans-Bold", 6.8)
            for _, cp in comps.iterrows():
                pt = cp.geometry.representative_point()
                X, Y = vista(pt.x, pt.y)
                if x + 2 < X < x + w - 2 and y + 12 < Y < y + h - 6:
                    texto_con_halo(c, X, Y, self.rotulo(cp.componente), "AtlasSans-Bold", 6.8, AZUL_TEXTO)
                    vistos.append(self.rotulo(cp.componente))
        else:
            for nombre in etiquetas:
                pz = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
                pt = max(pz, key=lambda g: g.area).representative_point()
                X, Y = vista(pt.x, pt.y)
                texto_con_halo(c, X, Y, nombre, "AtlasSans-Bold", 8.0, AZUL_TEXTO)

        for mx, my in marcas:
            X, Y = vista(mx, my)
            r = vista.metros_a_puntos(marca_radio_m)
            c.setStrokeColor(HexColor("#B0403A"))
            c.setLineWidth(1.1)
            c.setDash([2.2, 1.8])
            c.circle(X, Y, max(r, 3), fill=0, stroke=1)
            c.setDash([])

        metros = self._escala(c, vista)
        self._norte(c, vista)
        c.restoreState()
        c.setStrokeColor(GRIS_BORDE)
        c.setLineWidth(0.7)
        c.rect(x, y, w, h, fill=0, stroke=1)
        return {"escala_m": metros, "etiquetas": vistos, "calles": calles}

    # -- zoom sobre una parte declarada (S-02/S-03) ---------------------------------
    def mapa_subzona(self, c, rid: str, componente: str, x, y, w, h) -> dict:
        """Amplia UNA parte de una referencia, con el resto de la referencia atras.

        La "vista de detalle" de Las Cañitas no era un zoom: al no haber partes de R01
        en la capa de componentes, el encuadre caia sobre la envolvente entera y salia
        el mismo mapa de Palermo con otro rotulo. Acá el encuadre se calcula sobre la
        parte, y las otras partes quedan en gris de contexto, rotuladas, para que se
        vea que la parte ampliada no es el conjunto.
        """
        f = self.fila(rid)
        comps = self.comp[self.comp.referencia_id == rid]
        sel = comps[comps.componente == componente]
        if sel.empty:
            raise RuntimeError(f"{rid}: no hay una parte llamada «{componente}» en la capa")
        foco = sel.geometry.iloc[0]

        minx, miny, maxx, maxy = foco.bounds
        pad = 0.30 * max(maxx - minx, maxy - miny)
        vista = Vista((minx - pad, miny - pad, maxx + pad, maxy + pad), x, y, w, h)

        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)
        self._contexto(c, vista)

        # El resto de la referencia, en gris tenue: es contexto, no producto de esta pagina.
        resto = solo_poligonos(f.geometry.difference(foco.buffer(1.0)))
        if not resto.is_empty:
            c.saveState()
            c.setFillColor(GRIS_RESTO)
            c.setFillAlpha(0.42)
            c.setStrokeAlpha(0)
            c.drawPath(path_de(c, resto, vista), fill=1, stroke=0)
            c.setFillAlpha(1)
            c.setStrokeColor(GRIS_RESTO)
            c.setLineWidth(0.9)
            c.setDash([2.6, 2.0])
            c.drawPath(path_de(c, resto, vista), fill=0, stroke=1)
            c.setDash([])
            c.restoreState()

        self._pintar(c, foco, vista, f.familia, f.trazo == "punteado")

        pt_foco = foco.representative_point()
        calles = self._rotular_calles(c, vista, getattr(self, "_clave_detalle", ""),
                                      evitar=[vista(pt_foco.x, pt_foco.y)])

        # Las otras partes, rotuladas en gris: son la referencia de que esto es una parte.
        # Solo se rotula la que entra con superficie suficiente para reconocerse, y solo
        # si el rotulo entero cabe en el encuadre: media palabra colgando del borde dice
        # menos que no decir nada.
        etiquetas = []
        minima = 0.004 * vista.extent.area
        for _, cp in comps.iterrows():
            if cp.componente == componente:
                continue
            trozo = solo_poligonos(cp.geometry.intersection(vista.extent))
            if trozo.is_empty or trozo.area < minima:
                continue
            piezas = list(trozo.geoms) if trozo.geom_type == "MultiPolygon" else [trozo]
            q = max(piezas, key=lambda g: g.area).representative_point()
            rotulo = self.rotulo(cp.componente)
            ancho = c.stringWidth(rotulo, "AtlasSans-Bold", 6.8)
            X, Y = vista(q.x, q.y)
            if not (x + ancho / 2 + 4 < X < x + w - ancho / 2 - 4 and y + 14 < Y < y + h - 8):
                continue
            texto_con_halo(c, X, Y, rotulo, "AtlasSans-Bold", 6.8, GRIS_ROTULO_CALLE)
            etiquetas.append(rotulo)

        X, Y = vista(pt_foco.x, pt_foco.y)
        texto_con_halo(c, X, Y, self.rotulo(componente), "AtlasSans-Bold", 9.0, AZUL_TEXTO)
        etiquetas.insert(0, self.rotulo(componente))

        metros = self._escala(c, vista)
        self._norte(c, vista)
        c.restoreState()
        c.setStrokeColor(GRIS_BORDE)
        c.setLineWidth(0.7)
        c.rect(x, y, w, h, fill=0, stroke=1)
        return {"escala_m": metros, "etiquetas": etiquetas, "calles": calles}

    def _detalle_par(self, c, fa, fb, x, y, w, h):
        total = unary_union([fa.geometry, fb.geometry])
        minx, miny, maxx, maxy = total.bounds
        pad = 0.14 * max(maxx - minx, maxy - miny)
        vista = Vista((minx - pad, miny - pad, maxx + pad, maxy + pad), x, y, w, h)
        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)
        self._contexto(c, vista)
        for f in (fb, fa):
            self._pintar(c, f.geometry, vista, f.familia, f.trazo == "punteado")
        calles = self._rotular_calles(c, vista, getattr(self, "_clave_detalle", ""),
                                      cerca=unary_union([fa.geometry, fb.geometry]))
        for f in (fa, fb):
            pz = list(f.geometry.geoms) if f.geometry.geom_type == "MultiPolygon" else [f.geometry]
            pt = max(pz, key=lambda g: g.area).representative_point()
            X, Y = vista(pt.x, pt.y)
            texto_con_halo(c, X, Y, self.rotulo(f.nombre), "AtlasSans-Bold", 7.6, AZUL_TEXTO)
        metros = self._escala(c, vista)
        self._norte(c, vista)
        c.restoreState()
        c.setStrokeColor(GRIS_BORDE)
        c.setLineWidth(0.7)
        c.rect(x, y, w, h, fill=0, stroke=1)
        return {"escala_m": metros, "etiquetas": [fa.nombre, fb.nombre], "calles": calles}

    # -- leyenda comun (B3) ---------------------------------------------------------
    def leyenda(self, c, x, y, w, familia: str, punteado: bool, rid: str | None = None) -> float:
        """Leyenda real, con muestra de color. Solo anuncia lo que el mapa dibuja."""
        color = HexColor(FAMILIA_COLOR[familia])
        items = [(color, LEYENDA_AREA, True)]
        if rid is not None and len(self.comp[self.comp.referencia_id == rid]) > 1:
            items.append((color, LEYENDA_COMPONENTE, False))
        items.append((HexColor("#8A9099"), LEYENDA_CALLE, None))
        c.setFont("AtlasSans", 7.2)
        cx = x
        for col, texto, relleno in items:
            if relleno is None:
                c.setStrokeColor(col)
                c.setLineWidth(1.4)
                c.line(cx, y + 3, cx + 9, y + 3)
            else:
                c.saveState()
                c.setFillColor(col)
                c.setFillAlpha(0.30 if relleno else 0.16)
                c.rect(cx, y, 9, 6.5, fill=1, stroke=0)
                c.setFillAlpha(1)
                c.setStrokeColor(col)
                c.setLineWidth(0.9)
                if not relleno:
                    c.setDash([1.8, 1.4])
                c.rect(cx, y, 9, 6.5, fill=0, stroke=1)
                c.setDash([])
                c.restoreState()
            c.setFillColor(GRIS_TEXTO)
            c.drawString(cx + 12, y + 1, texto)
            cx += 12 + c.stringWidth(texto, "AtlasSans", 7.2) + 14
        if punteado:
            c.setFillColor(GRIS_TEXTO)
            c.setFont("AtlasSans", 7.2)
            c.drawString(x, y - 10, NOTA_TRAZO_PUNTEADO)
            return y - 10
        return y
