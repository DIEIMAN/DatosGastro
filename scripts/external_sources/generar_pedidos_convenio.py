"""Genera borradores de PEDIDO DE CONVENIO de datos agregados para plataformas privadas.

NO hace scraping ni llamadas de red. Toma el catálogo normalizado, filtra las fuentes cuyo
acceso es por convenio (Rappi, PedidosYa, Mercado Pago, adquirentes, POS, reservas, telcos) y
genera un borrador de solicitud por fuente, basado en la plantilla institucional.

Cada borrador pide SOLO datos agregados (comuna/rubro/mes) con umbral mínimo por celda; nunca
datos personales, tarjetas, repartidores, domicilios ni CUIT nominal.

Ver docs/fuentes_externas/plantilla_pedido_convenio_datos.md y
docs/skills_claude/06_fuentes_externas_privadas.md.

Salida: data/fuentes_externas/pedidos_convenio/E<id>_<slug>.md
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CAT = ROOT / "config" / "fuentes_externas" / "catalogo_fuentes_externas.csv"
OUT_DIR = ROOT / "data" / "fuentes_externas" / "pedidos_convenio"

CAMPOS_AGREGADOS = [
    "mes", "comuna o barrio", "rubro/categoría gastronómica",
    "cantidad de comercios activos en la plataforma",
    "cantidad agregada de pedidos/transacciones",
    "monto agregado o índice base 100", "ticket promedio agregado",
    "franjas horarias de mayor actividad", "altas/bajas de comercios",
    "plataforma/fuente", "aclaración metodológica",
]
NO_PEDIR = [
    "datos personales de usuarios o repartidores", "tarjetas", "CUIT/DNI nominal",
    "domicilios individuales", "transacciones individuales", "facturación por comercio",
]


def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")[:40]


def build_doc(row: dict) -> str:
    fuente = row["fuente"]
    campos = "\n".join(f"- {c};" for c in CAMPOS_AGREGADOS)
    no_pedir = "\n".join(f"- {c};" for c in NO_PEDIR)
    return f"""# Borrador de pedido de convenio — {fuente} ({row['id_externa']})

> Borrador para revisión institucional. No es un envío. Ajustar destinatario y firma.

Asunto: Solicitud de reunión y posible convenio de datos agregados – ecosistema gastronómico CABA

Hola [Equipo de {fuente}],

Desde [área/ministerio] trabajamos en DataGastro, una base analítica trazable del ecosistema
gastronómico de la Ciudad de Buenos Aires, para mejorar el diagnóstico territorial del sector y
diseñar políticas públicas basadas en evidencia, sin acceder a datos personales ni información
comercial individual identificable.

Nos interesaría evaluar una colaboración con {fuente} para contar con indicadores **agregados y
anonimizados** sobre actividad gastronómica en CABA. La información ideal sería mensual, agregada
por comuna/barrio y categoría gastronómica, por ejemplo:

{campos}

No buscamos:

{no_pedir}

Podemos trabajar con **umbrales mínimos por celda** para evitar cualquier reidentificación.
Nos gustaría coordinar una reunión breve de 30 minutos.

Gracias,
[Nombre] · [Cargo / área] · [Contacto]

---
Contexto de la fuente (catálogo): {row.get('que_aporta', '')}
Acceso real: {row.get('acceso_real', '')}
"""


def main() -> None:
    if not CAT.exists():
        raise SystemExit(f"Falta catálogo: {CAT}. Corré build_catalogo_externas.py primero.")
    df = pd.read_csv(CAT, dtype=str).fillna("")
    convenio = df[df["universo_sugerido"] == "externa_privada_convenio"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generados = []
    for row in convenio.to_dict("records"):
        path = OUT_DIR / f"{row['id_externa']}_{slug(row['fuente'])}.md"
        path.write_text(build_doc(row), encoding="utf-8")
        generados.append(path.name)
    print(f"Borradores de convenio generados (sin red, sin scraping): {len(generados)}")
    for name in generados:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
