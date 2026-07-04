"""DGDGAS Informes v1 — carga y resolucion de tokens de diseno.

Este modulo carga los tokens desde
``docs/datagastro_design_system/tokens/design_tokens_dgdgas.json`` y resuelve
las referencias semanticas (por ejemplo ``"brand.primary"`` ->
``"#1F3B57"``) para que los generadores de informes usen SIEMPRE nombres
semanticos y nunca HEX hardcodeado.

Es un ESQUELETO de la base reutilizable: no genera informes por si mismo. No
depende de librerias externas (solo stdlib) para poder cargarse en cualquier
entorno del repo.

Uso tipico::

    from scripts.shared.reporting_dgdgas.style_tokens_dgdgas import Tokens

    t = Tokens.load()
    ink = t.color("brand.primary")          # "#1F3B57"
    fill = t.resolve("box.reading.fill")     # "#EAF1F8" (resuelve la referencia)
    body = t.font_size("body")               # 9.5

No inventa valores: si una clave no existe, lanza ``KeyError`` explicito.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ruta al JSON de tokens (fuente de verdad para herramientas). Relativa al repo.
REPO_ROOT = Path(__file__).resolve().parents[3]
TOKENS_JSON = (
    REPO_ROOT
    / "docs"
    / "datagastro_design_system"
    / "tokens"
    / "design_tokens_dgdgas.json"
)

# Prefijos cuyos valores string se interpretan como referencias semanticas
# a resolver (por ejemplo "brand.primary", "surface.card"). Un valor que ya es
# un HEX ("#1F3B57") o un literal (numero, bool) se devuelve tal cual.
_REF_ROOTS = ("color.", "brand.", "text.", "surface.", "border.", "status.")


def _looks_like_ref(value: Any) -> bool:
    """True si el string parece una referencia semantica y no un color/HEX."""
    if not isinstance(value, str):
        return False
    if value.startswith("#"):
        return False
    # Referencia con punto: "brand.primary", "box.reading.fill", etc.
    return "." in value


@dataclass
class Tokens:
    """Vista de los tokens con resolucion de referencias semanticas."""

    data: dict = field(default_factory=dict)
    _color_index: dict = field(default_factory=dict, repr=False)

    # ---- carga -------------------------------------------------------------
    @classmethod
    def load(cls, path: Path | None = None) -> "Tokens":
        p = Path(path) if path else TOKENS_JSON
        if not p.exists():
            raise FileNotFoundError(f"No se encontraron tokens en: {p}")
        data = json.loads(p.read_text(encoding="utf-8"))
        t = cls(data=data)
        t._build_color_index()
        return t

    def _build_color_index(self) -> None:
        """Aplana color.* a un indice 'grupo.nombre' -> HEX para resolver."""
        idx: dict[str, str] = {}
        for group, entries in self.data.get("color", {}).items():
            if isinstance(entries, dict):
                for name, val in entries.items():
                    if isinstance(val, str) and val.startswith("#"):
                        idx[f"{group}.{name}"] = val
        self._color_index = idx

    # ---- acceso basico -----------------------------------------------------
    def get(self, dotted: str) -> Any:
        """Devuelve el valor crudo en la ruta 'a.b.c' (sin resolver refs)."""
        node: Any = self.data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                raise KeyError(f"Token inexistente: {dotted!r} (falla en {part!r})")
            node = node[part]
        return node

    # ---- resolucion de color ----------------------------------------------
    def color(self, name: str) -> str:
        """Resuelve un nombre de color semantico a HEX.

        Acepta 'brand.primary', 'surface.card', 'status.pending', o un HEX
        literal ('#1F3B57', devuelto tal cual).
        """
        if isinstance(name, str) and name.startswith("#"):
            return name
        if name in self._color_index:
            return self._color_index[name]
        raise KeyError(f"Color semantico inexistente: {name!r}")

    def resolve(self, dotted: str) -> Any:
        """Devuelve el valor de una ruta resolviendo referencias de color.

        Ej.: resolve('box.reading.fill') -> lee 'surface.note' -> '#EAF1F8'.
        """
        value = self.get(dotted)
        if _looks_like_ref(value) and value in self._color_index:
            return self._color_index[value]
        return value

    # ---- helpers de tipografia / layout -----------------------------------
    def font_size(self, role: str) -> float:
        return float(self.get(f"typography.scale.{role}"))

    def family(self, role: str = "sans") -> str:
        # role puede ser un rol ('body') o una familia directa ('sans').
        roles = self.data.get("typography", {}).get("role", {})
        fam_key = roles.get(role, role)
        return self.get(f"typography.family.{fam_key}")

    def margin_frac(self) -> dict:
        return dict(self.get("layout.margin_frac"))

    def chart_sequence(self) -> list[str]:
        return list(self.get("color.chart.sequence"))

    def box_style(self, kind: str) -> dict:
        """Estilo de caja resuelto a HEX. kind: question|reading|method|warning|validation."""
        raw = self.get(f"box.{kind}")
        out: dict[str, Any] = {}
        for k, v in raw.items():
            if _looks_like_ref(v) and v in self._color_index:
                out[k] = self._color_index[v]
            else:
                out[k] = v
        return out

    def content_state(self, state: str) -> dict:
        raw = self.get(f"content_states.{state}")
        return {
            "color": self.color(raw["color"]),
            "label": raw["label"],
        }


if __name__ == "__main__":  # pragma: no cover - smoke check manual
    t = Tokens.load()
    print("Sistema:", t.get("meta.system"), t.get("meta.version"))
    print("brand.primary ->", t.color("brand.primary"))
    print("box.reading    ->", t.box_style("reading"))
    print("estado pendiente ->", t.content_state("pendiente"))
    print("secuencia chart ->", t.chart_sequence())
