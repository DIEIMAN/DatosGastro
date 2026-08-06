#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dibujo de las páginas propias de la edición de conducción.

Solo vive acá lo que la conducción hace distinto de la edición técnica: la ficha de
cuatro bloques, el resumen de apertura, la página de lectura de tres ideas, la de
familias sin etiqueta fina, el Anexo A con encabezados en castellano y la página
"Cómo se hizo este Atlas y qué no dice".

Los mapas, la cartografía, la portada y toda la maquinaria de medición se reutilizan
de `build_atlas_v2.py` sin tocarlas: se importan en el momento de la llamada para no
crear una dependencia circular entre módulos.
"""

from __future__ import annotations

from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics

import contenido_conduccion as C


def _base():
    import build_atlas_v2 as B
    return B


# ---------------------------------------------------------------------------------------
# B3 · La ficha
# ---------------------------------------------------------------------------------------

def ficha_bloques(ficha: dict) -> dict:
    """Los cuatro bloques del lector para una referencia."""
    rid = ficha["referencia_id"]
    fuente = C.FICHAS[rid]
    return {
        "es": fuente["es"],
        "frase": C.frase_cifra(ficha),
        "contexto": fuente["contexto"],
        "compone": list(fuente["compone"]),
        "cuenta": list(fuente["cuenta"]),
    }


def draw_ficha_conduccion(atlas, ficha: dict, x: float, y_top: float, width: float,
                          y_bottom: float, compact: bool, *, escala: float = 1.0,
                          aire: float = 0.0, medir: bool = False) -> float:
    """Cuatro bloques, en el orden en que los necesita quien abre el documento.

    La estructura de la V2.1 —Lectura · Evidencia y método · Componentes y relaciones ·
    Qué no se puede concluir— era la del proceso de trabajo. Esta es la del lector.
    """
    B = _base()
    c = atlas.c
    rid, nombre = ficha["referencia_id"], ficha["nombre"]
    bloques = ficha_bloques(ficha)

    title_size = 12.5 if compact else 17
    body = (8.6 if compact else 9.3) * escala
    leading = (10.8 if compact else 12.4) * escala
    tam_rotulo = (8.6 if compact else 9.3) * min(escala, 1.2)
    salto = 12 * min(escala, 1.25)

    c.setFont("AtlasSans-Bold", title_size)
    c.setFillColor(B.COLORS["primary"])
    c.drawString(x, y_top, f"{rid} · {nombre}")
    y = y_top - (15 if compact else 22)
    c.setFont("AtlasSans", 8.4 if compact else 9.5)
    c.setFillColor(B.COLORS["text2"])
    c.drawString(x, y, B.FAMILIA_ETIQUETA[B.FAMILIA_DE[rid]])
    y -= 14 + aire * 0.4

    def rotulo(texto: str, y: float) -> float:
        c.setFont("AtlasSans-Bold", tam_rotulo)
        c.setFillColor(B.COLORS["primary"])
        c.drawString(x, y, texto)
        return y - salto

    # 1 · Qué es esta zona
    y = rotulo("Qué es esta zona", y)
    y = B.draw_text(c, bloques["es"], x, y, width, size=body,
                    color=B.COLORS["text"], leading=leading)
    y -= aire

    # 2 · Cuánta oferta hay. B2: una línea en lenguaje natural, destacada
    #     tipográficamente pero sin símbolo ni etiqueta en mayúsculas.
    y = rotulo("Cuánta oferta hay", y)
    cuerpo_cifra = (11.2 if compact else 13.0) * min(escala, 1.18)
    y = B.draw_text(c, bloques["frase"], x, y + 1, width, font="AtlasSans-Bold",
                    size=cuerpo_cifra, color=B.COLORS["primary"],
                    leading=cuerpo_cifra * 1.16) - 2
    y = B.draw_text(c, bloques["contexto"], x, y, width, size=body,
                    color=B.COLORS["text2"], leading=leading)
    y -= aire

    # 3 · De qué se compone
    y = rotulo("De qué se compone", y)
    y = B.draw_bullets(c, bloques["compone"], x, y, width, size=body,
                       leading=leading, gap=1)
    y -= aire

    # 4 · Qué hay que tener en cuenta
    y = rotulo("Qué hay que tener en cuenta", y)
    y = B.draw_bullets(c, bloques["cuenta"], x, y, width, size=body, leading=leading,
                       color=B.COLORS["text2"], gap=1)

    # B4: la línea "Fuente ... datos al ..." salió de las 22 fichas. Queda el enlace, que
    # en la ficha de página entera se ancla al pie y en la doble sigue al último bloque.
    ancla = (y_bottom + 14) if not compact else (y + 3)
    c.setFont("AtlasSans-Bold", 8.1)
    c.setFillColor(B.COLORS["secondary"])
    c.drawRightString(x + width, ancla,
                      f"{B.IR_AL_MAPA[B.EDICION]} · p. {B.REF_PAGES[rid][1]}")
    atlas.link(f"map_{rid}", (x + width - 115, ancla - 4, x + width, ancla + 9))

    if y < y_bottom + 28 and not medir:
        raise RuntimeError(f"Desborde de ficha {rid}: y={y:.1f}, mínimo={y_bottom + 28:.1f}")
    return y


def draw_pagina_fichas(atlas, primera: dict, segunda: dict | None) -> None:
    """Una o dos fichas por página, según lo que entre cómodo."""
    B = _base()
    left, _, width = atlas.new_page("Zonas R01-R22", f"ficha_{primera['referencia_id']}")
    if primera["referencia_id"] == "R01":
        atlas.c.bookmarkPage("section_references")
        atlas.bookmarks.add("section_references")
    top = B.TOP_Y - 7 * B.MM
    pie = B.BOTTOM_Y + 11 * B.MM

    if segunda is None:
        escala, aire = B.ajuste_ficha(primera, width, top, pie, compact=False,
                                      dibujante=draw_ficha_conduccion, tope=1.34,
                                      aire_max=34.0)
        B.AJUSTES_FICHA.append({"referencia_id": primera["referencia_id"],
                                "pagina": atlas.page, "tipo": "simple",
                                "escala_cuerpo": round(escala, 3), "aire_pt": round(aire, 2)})
        draw_ficha_conduccion(atlas, primera, left, top, width, pie, compact=False,
                              escala=escala, aire=aire)
    else:
        atlas.c.bookmarkPage(f"ficha_{segunda['referencia_id']}")
        atlas.bookmarks.add(f"ficha_{segunda['referencia_id']}")
        medio = B.PAGE_H / 2 - 1 * B.MM
        atlas.c.setStrokeColor(B.COLORS["strong"])
        atlas.c.line(left, medio, left + width, medio)
        for ficha, y_top, y_bottom in ((primera, top, medio + 10),
                                       (segunda, medio - 14, pie)):
            escala, aire = B.ajuste_ficha(ficha, width, y_top, y_bottom, compact=True,
                                          dibujante=draw_ficha_conduccion, tope=1.30,
                                          aire_max=15.0)
            B.AJUSTES_FICHA.append({"referencia_id": ficha["referencia_id"],
                                    "pagina": atlas.page, "tipo": "doble",
                                    "escala_cuerpo": round(escala, 3),
                                    "aire_pt": round(aire, 2)})
            draw_ficha_conduccion(atlas, ficha, left, y_top, width, y_bottom, compact=True,
                                  escala=escala, aire=aire)

    # B3 · Corrección editorial 2026-08-04: la advertencia al pie se repetía en las 22
    # páginas de ficha. Se retiró. La salvedad sigue completa en «Cómo leer el Atlas» y en
    # el cierre, que es donde el lector la necesita una vez.


# ---------------------------------------------------------------------------------------
# Apertura
# ---------------------------------------------------------------------------------------

def draw_resumen(atlas) -> None:
    B = _base()
    left, _, width = atlas.new_page("Apertura", "opening_summary")
    c = atlas.c
    y = B.draw_heading(c, "1. Resumen ejecutivo", left, B.TOP_Y - 5 * B.MM, width)

    cantidad, lista = B.comunas_resumen()
    familias: dict[str, int] = {}
    for rid in B.EXPECTED_REFS:
        familias[B.FAMILIA_DE[rid]] = familias.get(B.FAMILIA_DE[rid], 0) + 1
    orden = sorted(familias.items(), key=lambda kv: -kv[1])
    resumen_fam = "; ".join(f"{B.FAMILIA_ETIQUETA[k].lower()}, {v}" for k, v in orden)

    # Corrección editorial 2026-08-04: el resumen abre diciendo qué es un atlas y para qué
    # es éste, antes de la primera cifra. Son dos párrafos y el orden importa.
    y = B.draw_text(c, C.QUE_ES_UN_ATLAS, left, y, width, size=9.5,
                    color=B.COLORS["text"], leading=9.5 * 1.26) - B.RITMO["parrafo"]
    y = B.draw_text(c, C.ATLAS_REUNE, left, y, width, size=9.5,
                    color=B.COLORS["text"], leading=9.5 * 1.26) - B.RITMO["bloque"]

    techo_caja = B.draw_box(
        c, C.CAJA_QUE_MUESTRA_TITULO,
        f"La Dirección identificó y caracterizó 22 zonas gastronómicas de la Ciudad, "
        f"presentes en {cantidad} de las 15 comunas (comunas {lista}). "
        f"Se agrupan en cinco familias territoriales, que describen la forma en que la oferta "
        f"se ordena en el terreno: {resumen_fam}. "
        f"No hay zonas identificadas en el sur profundo de la Ciudad.",
        left, y, width, fill=B.COLORS["note"], size=9.5,
    )

    # B7: el cuerpo se calcula para que la página se llene. Con cuatro grupos en vez del
    # aparato de la V2.1, el tamaño heredado dejaba media hoja en blanco.
    # M-03: el aire entre grupos ya no se reparte a ojo; es un valor de la escala, y la
    # caja de cierre sigue al último grupo en vez de estar clavada al pie de la página.
    # Clavada dejaba 166 pt de hueco en el medio; abajo, el sobrante se lee como margen.
    pie = B.BOTTOM_Y + 9 * B.MM
    caja_h = 14 + B.box_height(C.CAJA_USO, width, 9.8, 9) + 4
    aire = B.RITMO["bloque"]
    titulo_size = lambda cuerpo: cuerpo + 2.4

    def alto_grupos(cuerpo: float) -> float:
        alto = len(B.wrap_lines(C.NOTA_GRUPOS, width, "AtlasSans", cuerpo - 0.6)) * (cuerpo * 1.24)
        alto += B.RITMO["parrafo"]
        for titulo, datos, nota in C.GRUPOS_RESUMEN:
            alto += len(B.wrap_lines(titulo, width, "AtlasSans-Bold", cuerpo)) * (cuerpo * 1.24)
            alto += len(B.wrap_lines(datos, width - 6, "AtlasSans", cuerpo)) * (cuerpo * 1.26)
            alto += len(B.wrap_lines(nota, width - 6, "AtlasSans-Italic", cuerpo - 0.9)) * (cuerpo * 1.16)
            alto += aire
        return alto

    cuerpo = 8.9
    for prueba in (13.5, 13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0, 9.6, 9.2, 8.9):
        techo_titulo = techo_caja - B.RITMO["seccion"]
        disponible = techo_titulo - pdfmetrics.getAscent("AtlasSans-Bold", titulo_size(prueba)) \
            - B.RITMO["parrafo"] - pie - caja_h - B.RITMO["seccion"] - B.RITMO["bloque"]
        if alto_grupos(prueba) <= disponible:
            cuerpo = prueba
            break

    # M-02: el título arranca por debajo del borde de la caja, medido contra el techo de
    # sus mayúsculas.
    y = B.base_bajo(techo_caja, titulo_size(cuerpo), B.RITMO["seccion"])
    c.setFont("AtlasSans-Bold", titulo_size(cuerpo))
    c.setFillColor(B.COLORS["primary"])
    c.drawString(left, y, C.TITULO_GRUPOS)
    y = B.base_bajo(y - pdfmetrics.getDescent("AtlasSans-Bold", titulo_size(cuerpo)),
                    cuerpo - 0.6, B.RITMO["parrafo"], font="AtlasSans")
    y = B.draw_text(c, C.NOTA_GRUPOS, left, y, width, size=cuerpo - 0.6,
                    color=B.COLORS["text2"], leading=cuerpo * 1.24) - B.RITMO["parrafo"]

    for idx, (titulo, datos, nota) in enumerate(C.GRUPOS_RESUMEN):
        if idx:
            # Una línea fina entre grupos: así el aire se lee como separación entre los
            # cuatro modos de conteo y no como un hueco de armado.
            c.setStrokeColor(B.COLORS["border"])
            c.setLineWidth(0.5)
            c.line(left, y + aire / 2, left + width, y + aire / 2)
        y = B.draw_text(c, titulo, left, y, width, font="AtlasSans-Bold", size=cuerpo,
                        color=B.COLORS["primary"], leading=cuerpo * 1.24)
        y = B.draw_text(c, datos, left + 6, y, width - 6, size=cuerpo,
                        color=B.COLORS["text"], leading=cuerpo * 1.26)
        y = B.draw_text(c, nota, left + 6, y, width - 6, font="AtlasSans-Italic",
                        size=cuerpo - 0.9, color=B.COLORS["muted"],
                        leading=cuerpo * 1.16) - aire

    # El último grupo ya descontó su `aire`: lo que falta para llegar a la separación de
    # sección es la diferencia entre los dos valores de la escala.
    y -= B.RITMO["seccion"] - aire
    base_caja = B.draw_box(c, C.CAJA_USO_TITULO, C.CAJA_USO,
                           left, y, width, fill=B.COLORS["warn"],
                           accent=B.COLORS["accent"], size=9.8)
    # B4: la fuente y la fecha aparecen UNA vez en todo el documento, acá.
    c.setFont("AtlasSans", 8.2)
    c.setFillColor(B.COLORS["muted"])
    c.drawString(left, B.base_bajo(base_caja, 8.2, B.RITMO["bloque"], font="AtlasSans"),
                 C.FUENTE_UNICA)


def draw_como_leer(atlas) -> None:
    """B6 · ocho cajas de método pasan a tres ideas."""
    B = _base()
    left, _, width = atlas.new_page("Apertura", "how_to")
    c = atlas.c
    y = B.draw_heading(c, "3. Cómo leer el Atlas", left, B.TOP_Y - 5 * B.MM, width)
    # Corrección editorial 2026-08-04, observación «otra vez negativo». La frase «no ordena
    # las zonas de mejor a peor» no se pierde: sigue en el cierre del documento.
    cierre = ("Este Atlas dice dónde hay oferta gastronómica en la Ciudad y cómo es cada "
              "lugar. Cada zona se lee por separado, con lo que explica su propia ficha.")
    # B7: el cuerpo se elige de modo que las cuatro cajas llenen la página. Con tres ideas
    # en vez de ocho, dejar el tamaño de la V2.1 vaciaba media hoja.
    # M-05: el sobrante ya NO se reparte dentro de las cajas. Cada caja se ajusta a su
    # contenido; lo que ganaba la caja eran dos centímetros de vacío debajo del texto.
    # Lo que llena la página es el cuerpo, que es lo que además se lee mejor.
    # El cuerpo no pasa de 13,5: por encima queda más grande que el título de la página y
    # se lee como un cartel. Con las cajas ajustadas a su contenido y el ritmo fijo, lo que
    # sobra queda al pie, donde se lee como margen y no como un hueco de armado.
    disponible = y - (B.BOTTOM_Y + 6 * B.MM)
    respiro = B.RITMO["bloque"]
    textos = [t for _, t in C.COMO_LEER] + [cierre]
    cuerpo = 9.6
    for prueba in (13.5, 13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0, 9.6):
        alto = sum(B.box_height(t, width, prueba) + 18 for t in textos) + 3 * respiro
        if alto <= disponible:
            cuerpo = prueba
            break
    fondos = [B.COLORS["card"], B.COLORS["note"], B.COLORS["card"]]
    for (titulo, texto), fondo in zip(C.COMO_LEER, fondos):
        y = B.draw_box(c, titulo, texto, left, y, width, fill=fondo, size=cuerpo) - respiro
    B.draw_box(c, C.CAJA_CIERRE_TITULO, cierre, left, y, width, fill=B.COLORS["warn"],
               accent=B.COLORS["accent"], size=cuerpo)


def draw_familias(atlas, content: dict) -> None:
    """Las cinco familias. Sin la etiqueta fina: viaja a la edición técnica."""
    B = _base()
    left, _, width = atlas.new_page("Apertura", "typologies")
    c = atlas.c
    y = B.draw_heading(
        c, "4. Las cinco familias territoriales", left, B.TOP_Y - 5 * B.MM, width,
        subtitle="Cinco formas de estar en el territorio. El color de cada familia es el "
                 "que usa el mapa de la página siguiente.",
    )
    nombres = {f["referencia_id"]: f["nombre"] for f in content["fichas"]}
    definicion = {
        "polo": "Concentración reconocible en torno de un área, con identidad propia.",
        "multiparte": "Un polo que se lee en partes separadas, sin unirlas artificialmente.",
        "eje": "La oferta se organiza a lo largo de una calle o avenida, no en una mancha.",
        "segmentada": "Un área que solo se puede leer por partes independientes entre sí.",
        "dispersa": "Oferta presente y documentada, sin un centro único demostrado.",
    }
    for fam, etiqueta in B.FAMILIA_ETIQUETA.items():
        refs = [r for r in B.EXPECTED_REFS if B.FAMILIA_DE[r] == fam]
        color = HexColor(B.FAMILIA_COLOR[fam])
        alto = 30 + 12.8 * len(refs)
        B.registrar_caja(left, y - 2, width, alto + 10)
        c.setFillColor(HexColor("#F7F9FB"))
        c.roundRect(left, y - alto - 12, width, alto + 10, 4, fill=1, stroke=0)
        c.saveState()
        c.setFillColor(color)
        c.setFillAlpha(0.45)
        c.rect(left + 8, y - 13, 13, 9, fill=1, stroke=0)
        c.setFillAlpha(1)
        c.restoreState()
        c.setStrokeColor(color)
        c.setLineWidth(0.9)
        c.rect(left + 8, y - 13, 13, 9, fill=0, stroke=1)
        c.setFont("AtlasSans-Bold", 9.6)
        c.setFillColor(B.COLORS["primary"])
        c.drawString(left + 27, y - 11, f"{etiqueta}  ({len(refs)})")
        c.setFont("AtlasSans", 8.6)
        c.setFillColor(B.COLORS["text2"])
        c.drawString(left + 27, y - 24, definicion[fam])
        yy = y - 40
        for rid in refs:
            c.setFont("AtlasSans-Bold", 8.8)
            c.setFillColor(B.COLORS["primary"])
            c.drawString(left + 27, yy, rid)
            sangria = 27 + c.stringWidth("R00  ", "AtlasSans-Bold", 8.8)
            c.setFont("AtlasSans", 8.8)
            c.setFillColor(B.COLORS["text"])
            c.drawString(left + sangria, yy, nombres[rid])
            yy -= 12.8
        # El panel termina en `y - alto - 12`; el siguiente arranca un bloque más abajo.
        y = (y - alto - 12) - B.RITMO["bloque"] + 2
    B.draw_box(c, C.CAJA_FAMILIAS_TITULO, C.CAJA_FAMILIAS,
               left, max(y, B.BOTTOM_Y + 24 * B.MM), width,
               fill=B.COLORS["note"], size=9.0)


# ---------------------------------------------------------------------------------------
# Anexos
# ---------------------------------------------------------------------------------------

def draw_matriz(atlas, fichas: list[dict], parte: str, marcador: str) -> None:
    B = _base()
    left, _, width = atlas.new_page("Anexos", marcador)
    if parte == "1 de 2":
        atlas.c.bookmarkPage("section_annexes")
        atlas.bookmarks.add("section_annexes")
    y = B.draw_heading(
        atlas.c, f"Las 22 zonas de un vistazo · {parte}", left, B.TOP_Y - 5 * B.MM, width,
        subtitle="Tabla de consulta rápida. Cada fila remite a la ficha de su zona.",
    )
    # M-06: la columna "Qué mide la cifra" decía lo mismo que "Cuánta oferta hay" —en cinco
    # de las once filas, literalmente lo mismo— y en las otras seis lo repetía con otras
    # palabras: la frase de cifra ya distingue el conteo propio ("907 locales relevados"),
    # el mínimo ("Al menos 797 locales"), el antecedente ("697 locales según un relevamiento
    # anterior") y la ausencia ("Zona caracterizada, sin conteo propio"). Queda una sola.
    filas = [[f["referencia_id"], f["nombre"], B.FAMILIA_ETIQUETA[B.FAMILIA_DE[f["referencia_id"]]],
              C.frase_cifra(f)] for f in fichas]
    # La columna de la zona tiene que admitir "Esmeralda–Paraguay" entero y la de tipo de
    # zona su propio encabezado: con 35 mm sobraba 8,6 pt y pisaba al de al lado.
    anchos = [14 * B.MM, 46 * B.MM, 42 * B.MM, width - 102 * B.MM]
    # B7: la tabla de once filas ocupaba un tercio de la hoja. Las filas se estiran para
    # llenar la página, que es lo que se espera de una tabla de consulta rápida.
    pie = B.BOTTOM_Y + 20 * B.MM
    alto_fila = max(21.0, (y - 24 - pie) / len(filas))
    B.draw_table(atlas.c, C.ANEXO_A_ENCABEZADOS, filas, left, y, anchos, font_size=9.2,
                 max_bottom=B.BOTTOM_Y + 17 * B.MM, alto_min_fila=alto_fila)
    atlas.c.setFont("AtlasSans-Italic", 8)
    atlas.c.setFillColor(B.COLORS["muted"])
    B.draw_text(atlas.c, C.ANEXO_A_PIE, left, B.BOTTOM_Y + 15 * B.MM, width,
                font="AtlasSans-Italic", size=8, color=B.COLORS["muted"], leading=9.8)


def draw_como_se_hizo(atlas) -> None:
    """B5 · la página nueva que reemplaza a los seis anexos que se fueron."""
    B = _base()
    left, _, width = atlas.new_page("Anexos", "annex_metodo")
    c = atlas.c
    y = B.draw_heading(c, C.COMO_SE_HIZO_TITULO, left, B.TOP_Y - 5 * B.MM, width)
    # B5 pide media carilla: seis frases en castellano. La página cierra el documento y
    # queda deliberadamente aireada; no se rellena para ocupar el alto completo.
    ancho = width * 0.86
    for parrafo in C.COMO_SE_HIZO:
        y = B.draw_text(c, parrafo, left, y - 6, ancho, size=11.4,
                        color=B.COLORS["text"], leading=16.4) - 9
    c.setFillColor(B.COLORS["accent"])
    c.rect(left, y - 14, 48 * B.MM, 1.6 * B.MM, fill=1, stroke=0)
