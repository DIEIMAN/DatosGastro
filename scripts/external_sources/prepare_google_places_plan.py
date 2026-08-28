"""Prepara el PLAN de piloto de Google Places para CABA. NO llama a ninguna API.

Fuente E01/E02 (Google Places / Places Aggregate): API oficial paga. Por política del proyecto
este script **solo genera documentación de plan**: grilla de comunas piloto, campos mínimos
permitidos, controles de TOS y presupuesto. No ejecuta requests, no requiere ni guarda API key.

Ver docs/skills_claude/06_fuentes_externas_privadas.md.

Salida: data/fuentes_externas/google_places_plan.md
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "fuentes_externas" / "google_places_plan.md"

COMUNAS_PILOTO = ["San Nicolás (Comuna 1)", "Palermo (Comuna 14)"]
CAMPOS_MINIMOS_PERMITIDOS = [
    "place_id", "name", "formatted_address", "location (lat/lon)", "types/primaryType",
    "businessStatus", "rating", "userRatingCount", "priceLevel",
    "currentOpeningHours", "fecha_consulta",
]
CONTROLES_TOS = [
    "Revisar Google Maps Platform Terms antes de persistir cualquier campo.",
    "Respetar restricciones de almacenamiento/caché y atribución.",
    "No usar scraping de Google Maps ni de Popular Times.",
    "Guardar siempre place_id + fecha_consulta para trazabilidad.",
    "No persistir más campos que los mínimos del caso de uso.",
]


def build_plan() -> str:
    comunas = "\n".join(f"- {c}" for c in COMUNAS_PILOTO)
    campos = "\n".join(f"- `{c}`" for c in CAMPOS_MINIMOS_PERMITIDOS)
    controles = "\n".join(f"- {c}" for c in CONTROLES_TOS)
    return f"""# Plan de piloto — Google Places (E01) / Places Aggregate (E02)

> Documento de PLAN. No se llamó a ninguna API. Requiere autorización de Diego para crear el
> proyecto Google Cloud, cargar presupuesto acotado y recién entonces ejecutar.

## Objetivo
Validar la oferta gastronómica **visible** en Google para 2 comunas piloto y compararla con
F01/F02. Recordatorio: Google Places mide oferta visible publicada, **no** padrón oficial ni
locales activos habilitados.

## Comunas piloto
{comunas}

## Enfoque
- **Places Aggregate (E02)** primero: conteos/densidad por polígono (comuna/barrio/radio), más
  institucional y con menor costo de almacenamiento.
- **Places Details/Nearby (E01)** después, solo si se necesita el detalle por local, con grilla
  acotada a las comunas piloto.

## Campos mínimos permitidos a persistir
{campos}

## Controles de Términos de Servicio y privacidad
{controles}

## Presupuesto y autorización
- Definir tope mensual chico antes de cualquier request.
- Sin autorización presupuestaria explícita: NO ejecutar llamadas (son pagas).
- No guardar API keys en el repo ni en outputs; usar variables de entorno fuera del repo.

## Próximos pasos
1. Autorización de proyecto Google Cloud + billing acotado (Diego / área).
2. Piloto Places Aggregate en las 2 comunas.
3. Comparar densidad vs F01/F02; documentar sesgos (skill 05).
4. Recién con resultados y permiso: evaluar contrato F-pipeline.
"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_plan(), encoding="utf-8")
    print(f"Plan generado (sin llamadas a API): {OUT}")
    print("Recordatorio: este script nunca llama a Google ni usa API keys.")


if __name__ == "__main__":
    main()
