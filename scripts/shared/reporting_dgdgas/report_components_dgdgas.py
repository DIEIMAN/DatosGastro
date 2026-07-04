"""DGDGAS Informes v1 — primitivas de componentes (ESQUELETO).

Define la API de los componentes reutilizables del sistema (portada, indice,
cajas, tabla, mapa, sintesis, etc.) como funciones que reciben tokens ya
resueltos y un "lienzo" abstracto. No fija todavia el motor de render: los
generadores concretos (PDF via matplotlib, DOCX via python-docx) implementan
el metodo de dibujo, y estas primitivas describen QUE se dibuja y con QUE
tokens, de forma consistente entre formatos.

Es intencionalmente un esqueleto: cada funcion documenta contrato, tokens y
reglas, y deja el render como ``NotImplementedError`` o como no-op registrando
la intencion. Asi la base es reutilizable sin acoplarse a un backend ni generar
todavia un informe completo.

Reglas transversales (ver docs/datagastro_design_system):
  - Marca publica DGDGAS.
  - Preguntas antes de resultados.
  - Multi-respuesta: mostrar menciones, aclarar que la suma puede superar 100%.
  - Mapas: nota de alcance obligatoria si son conceptuales/preliminares.
  - Sin datos individuales, contactos, rutas ni keys.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Sequence

from .style_tokens_dgdgas import Tokens


class Canvas(Protocol):
    """Contrato minimo que debe cumplir un backend de render (PDF/DOCX).

    Los generadores concretos implementan estos metodos. Las primitivas de
    abajo solo llaman a esta interfaz, de modo que el mismo componente sirve
    para PDF y DOCX sin duplicar la logica de estilo.
    """

    def rect(self, x: float, y: float, w: float, h: float,
             fill: str | None = None, edge: str | None = None,
             radius: float = 0.0) -> None: ...

    def text(self, x: float, y: float, s: str, *, size: float,
             color: str, bold: bool = False, align: str = "left") -> None: ...

    def accent_bar(self, x: float, y: float, h: float, color: str) -> None: ...

    def new_page(self) -> None: ...


@dataclass
class Components:
    """Fabrica de componentes ligada a un set de tokens.

    ``canvas`` es opcional: si falta, las primitivas solo devuelven una
    descripcion estructurada del componente (util para tests y para el handoff
    a otros backends) sin dibujar nada.
    """

    tokens: Tokens
    canvas: Canvas | None = None
    _log: list[dict] = field(default_factory=list, repr=False)

    # ---- utilidades internas ----------------------------------------------
    def _emit(self, component: str, **spec: Any) -> dict:
        """Registra la intencion de dibujar un componente y la devuelve.

        Si hay canvas, el generador concreto es responsable de traducir esta
        spec a llamadas de dibujo. El esqueleto solo garantiza contrato y
        tokens correctos.
        """
        entry = {"component": component, **spec}
        self._log.append(entry)
        return entry

    @property
    def log(self) -> list[dict]:
        """Secuencia de componentes emitidos (para inspeccion/tests)."""
        return list(self._log)

    # ---- 1. Portada institucional -----------------------------------------
    def portada(self, *, kicker: str, titulo: str, subtitulo: str,
                descripcion: str, datos_generales: Sequence[Sequence[str]],
                presenta: str) -> dict:
        """Portada: la Direccion mas visible que el nombre interno."""
        return self._emit(
            "portada",
            fill=self.tokens.color("brand.primary"),
            text_on=self.tokens.color("text.on_brand"),
            kicker_color=self.tokens.color("brand.secondary"),
            kicker=kicker, titulo=titulo, subtitulo=subtitulo,
            descripcion=descripcion, datos_generales=list(map(list, datos_generales)),
            presenta=presenta,
            size_display=self.tokens.font_size("display"),
        )

    # ---- 2. Indice ---------------------------------------------------------
    def indice(self, *, titulo: str, subtitulo: str,
               entradas: Sequence[dict]) -> dict:
        """Indice con numeros de pagina; subsecciones indentadas (sub=si)."""
        return self._emit(
            "indice", titulo=titulo, subtitulo=subtitulo,
            entradas=list(entradas),
            rule=self.tokens.color("border.subtle"),
            text_color=self.tokens.color("text.primary"),
            page_color=self.tokens.color("text.secondary"),
        )

    # ---- 3. Ficha de relevamiento -----------------------------------------
    def ficha_relevamiento(self, *, titulo: str, filas: Sequence[Sequence[str]]) -> dict:
        return self._emit(
            "ficha_relevamiento", titulo=titulo,
            filas=list(map(list, filas)),
            fill=self.tokens.color("surface.card"),
            edge=self.tokens.color("border.subtle"),
            title_color=self.tokens.color("brand.primary"),
        )

    # ---- 4/5/6. Cajas (pregunta / lectura / nota / advertencia / validacion)
    def caja(self, kind: str, *, titulo: str, cuerpo: str,
             extra: dict | None = None) -> dict:
        """Caja generica segun tipo. kind: question|reading|method|warning|validation."""
        style = self.tokens.box_style(kind)
        return self._emit(
            "caja", kind=kind, titulo=titulo, cuerpo=cuerpo,
            extra=extra or {},
            fill=style["fill"], edge=style["border"], accent=style["accent"],
            radius=style.get("radius"), pad_mm=style.get("pad_mm"),
        )

    def caja_pregunta(self, *, pregunta: str, tipo: str, observa: str,
                      nota_multi: str | None = None) -> dict:
        cuerpo = f"Tipo: {tipo}. Que permite observar: {observa}."
        extra = {}
        if tipo.startswith("multi") and not nota_multi:
            nota_multi = ("Permitia mas de una opcion; se muestran menciones y "
                          "la suma puede superar 100%.")
        if nota_multi:
            extra["nota_multi"] = nota_multi
        return self.caja("question", titulo=f"Pregunta analizada: {pregunta}",
                          cuerpo=cuerpo, extra=extra)

    def caja_lectura(self, *, texto: str) -> dict:
        return self.caja("reading", titulo="Lectura de resultados", cuerpo=texto)

    def caja_nota_metodologica(self, *, texto: str) -> dict:
        return self.caja("method", titulo="Nota metodologica", cuerpo=texto)

    def caja_advertencia(self, *, texto: str) -> dict:
        return self.caja("warning", titulo="Alcance / advertencia", cuerpo=texto)

    def caja_validacion(self, *, texto: str) -> dict:
        return self.caja("validation", titulo="Requiere validacion", cuerpo=texto)

    # ---- 7/8. Tabla institucional / de polos ------------------------------
    def tabla(self, *, titulo: str | None, headers: Sequence[str],
              rows: Sequence[Sequence[Any]], numeric_cols: Sequence[int] = (),
              base: str | None = None, fuente: str | None = None) -> dict:
        tt = self.tokens.get("table")
        return self._emit(
            "tabla", titulo=titulo, headers=list(headers),
            rows=[list(r) for r in rows], numeric_cols=list(numeric_cols),
            base=base, fuente=fuente,
            header_fill=self.tokens.color(tt["header_fill"]),
            header_text=self.tokens.color(tt["header_text"]),
            row_fill=self.tokens.color(tt["row_fill"]),
            row_fill_alt=self.tokens.color(tt["row_fill_alt"]),
            border=self.tokens.color(tt["border"]),
        )

    # ---- 9. Ficha de polo --------------------------------------------------
    def ficha_polo(self, *, nombre: str, referencia_territorial: str,
                   descripcion: str, aspectos: str, estado: str = "principal") -> dict:
        st = self.tokens.content_state(estado)
        return self._emit(
            "ficha_polo", nombre=nombre,
            referencia_territorial=referencia_territorial,
            descripcion=descripcion, aspectos=aspectos,
            estado_label=st["label"], estado_color=st["color"],
            fill=self.tokens.color("surface.card"),
            title_color=self.tokens.color("brand.primary"),
        )

    # ---- 10. Mapa territorial ---------------------------------------------
    def mapa_territorial(self, *, titulo: str, leyenda: Sequence[str],
                         nota_alcance: str | None, conceptual: bool = False) -> dict:
        """Mapa sobrio de referencia. Nota de alcance obligatoria si es conceptual."""
        if conceptual and not nota_alcance:
            raise ValueError(
                "Un mapa conceptual/preliminar requiere nota de alcance "
                "(no representar limites oficiales inexistentes)."
            )
        m = self.tokens.get("map")
        return self._emit(
            "mapa_territorial", titulo=titulo, leyenda=list(leyenda),
            nota_alcance=nota_alcance,
            land=m["land_fill"], water=m["water_fill"],
            boundary=m["boundary_line"],
            point=self.tokens.color(m["point_fill"]),
        )

    # ---- 11. Grafico de barras --------------------------------------------
    def grafico_barras(self, *, titulo: str, items: Sequence[tuple[str, float]],
                       base: str, fuente: str, es_multi: bool = False) -> dict:
        return self._emit(
            "grafico_barras", titulo=titulo, items=list(items),
            base=base, fuente=fuente, es_multi=es_multi,
            sequence=self.tokens.chart_sequence(),
            grid=self.tokens.color("chart.grid"),
        )

    # ---- 12/13. Sintesis / Aspectos ---------------------------------------
    def lista_puntos(self, *, titulo: str, intro: str,
                     puntos: Sequence[str], nota: str | None = None) -> dict:
        return self._emit(
            "lista_puntos", titulo=titulo, intro=intro,
            puntos=list(puntos), nota=nota,
            text_color=self.tokens.color("text.primary"),
            note_color=self.tokens.color("text.secondary"),
            title_color=self.tokens.color("brand.primary"),
        )

    # ---- 14. Anexo ---------------------------------------------------------
    def anexo(self, *, titulo: str, intro: str, nota_prudente: str | None = None) -> dict:
        st = self.tokens.content_state("anexo")
        return self._emit(
            "anexo", titulo=titulo, intro=intro, nota_prudente=nota_prudente,
            estado_label=st["label"], header_color=self.tokens.color("text.muted"),
        )

    # ---- 16. Estado de documentacion --------------------------------------
    def estado_documentacion(self, *, estado: str) -> dict:
        st = self.tokens.content_state(estado)
        return self._emit("estado_documentacion",
                          estado=estado, label=st["label"], color=st["color"])


if __name__ == "__main__":  # pragma: no cover - smoke check manual
    t = Tokens.load()
    c = Components(t)
    c.caja_pregunta(pregunta="Como te enteraste?", tipo="multi-respuesta",
                    observa="canales de llegada")
    c.caja_lectura(texto="Ejemplo de lectura descriptiva.")
    c.tabla(titulo="Ejemplo", headers=["Categoria", "Menciones"],
            rows=[["A", 10], ["B", 5]], numeric_cols=[1])
    for entry in c.log:
        print(entry["component"], "->", {k: v for k, v in entry.items() if k != "component"})
