from __future__ import annotations

import ipaddress
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[4]
SAFE_OUTPUT_ROOTS = (
    (ROOT / ".agent-tools").resolve(),
    (ROOT / "outputs" / "analisis_interno").resolve(),
)

# Se conserva el nombre por compatibilidad con browser_public.py. La autorización se controla
# por tarea mediante --allow-host; no hay una prohibición global por marca o plataforma.
BLOCKED_HOSTS: set[str] = set()

SENSITIVE_PATTERNS = (
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"\b(?:CUIT|CUIL|DNI)\s*[:#-]?\s*\d{7,11}\b", re.I),
    re.compile(r"(?:\+?54\s*)?(?:\(?\d{2,4}\)?[\s.-]*)?\d{3,4}[\s.-]*\d{4}\b"),
)


def _host_is(host: str, candidate: str) -> bool:
    return host == candidate or host.endswith("." + candidate)


def validate_public_url(url: str, allowed_hosts: list[str]) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Solo se permiten URLs http/https con host explícito")
    host = parsed.hostname.lower().rstrip(".")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip and (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved):
        raise ValueError("No se permiten hosts locales, privados ni reservados")
    if host in {"localhost", "localhost.localdomain"}:
        raise ValueError("No se permite localhost")
    allowed = [item.lower().rstrip(".") for item in allowed_hosts]
    if not allowed or not any(_host_is(host, item) for item in allowed):
        raise ValueError(f"El host {host} debe declararse explícitamente con --allow-host")
    return host


def safe_output_path(raw_path: str | Path, *, directory: bool = False) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    if not any(resolved == base or base in resolved.parents for base in SAFE_OUTPUT_ROOTS):
        raise ValueError("La salida debe quedar bajo .agent-tools/ u outputs/analisis_interno/")
    if directory:
        resolved.mkdir(parents=True, exist_ok=True)
    else:
        resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def reject_sensitive_text(text: str, label: str = "contenido") -> None:
    if any(pattern.search(text) for pattern in SENSITIVE_PATTERNS):
        raise ValueError(f"{label} parece contener datos personales; redactar antes de continuar")


def safe_identifier(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError(f"Identificador SQL inválido: {value}")
    return value
