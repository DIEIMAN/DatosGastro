#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B1 · Vocabulario de la edición de conducción — lista única.

Este archivo es el ÚNICO lugar del código donde vive la lista de términos que no
pueden aparecer en la edición de conducción. El control automático
`vocabulario_conduccion` la lee de acá; ninguna otra parte del generador la repite.

La regla de la fase es: se simplifica cómo se dice, no qué se dice. Cada término de
esta lista sigue existiendo, íntegro, en la edición técnica; lo que se prohíbe es que
llegue al lector de la edición de conducción sin traducir.

Dos bloques:

1. TERMINOS_TECNICOS — el vocabulario de método. Entre paréntesis, la frecuencia que
   tenían en la V2.1, que es lo que esta fase tuvo que traducir.
2. JERGA_DISFRAZADA — expresiones que ya están en castellano y por eso son peores:
   el lector cree entenderlas y en realidad nombran un objeto interno del proyecto.
"""

from __future__ import annotations

import re

# (patrón, término tal como se lo nombra en el informe de cambios)
TERMINOS_TECNICOS: list[tuple[str, str]] = [
    (r"\bcomparab\w*", "comparable / no comparable"),
    (r"\buniversos?\b", "universo"),
    (r"\bdedup\w*", "deduplicación / deduplicado"),
    (r"\bfusi[oó]\w*|\bfusionar\b", "fusión"),
    (r"\babsor[bc]\w*", "absorber / absorción"),
    (r"\benvolvente\w*", "envolvente"),
    (r"\bcan[oó]nic\w*|\bcanon\b", "canónico"),
    (r"\bsatura\w*", "saturado / saturación"),
    (r"\baditiv\w*", "no aditivo"),
    (r"\bcapas?\s+administrativas?\b", "capas administrativas"),
    (r"\bno[-\s]producto\w*", "no-producto"),
    (r"\bestado\s+declarado\b", "estado declarado"),
    (r"\bcorridas?\b", "corrida"),
    (r"\bventanas?\b", "ventana"),
    (r"\bregistros?\s*(?:/|por)\s*centro\b", "registros/centro"),
    (r"\btrazabilidad\b", "trazabilidad"),
    (r"\bcotas?\s+inferior(?:es)?\b", "cota inferior"),
    (r"\bcensad\w*", "piso censado"),
    (r"\bconsultas?\s+de\s+red\b", "consultas de red"),
    (r"\bobservacional\w*", "observacional"),
    (r"\bfechas?\s+de\s+corte\b", "fecha de corte"),
]

JERGA_DISFRAZADA: list[tuple[str, str]] = [
    (r"\bel\s+tercer\s+tramo\s+evaluado\b", "el tercer tramo evaluado"),
    (r"\bcontrol\s+Lacroze\b", "el control Lacroze-Chacarita"),
    (r"\bred\s+occidental\b", "la red occidental de calles documentadas"),
    (r"\bvistas?\s+de\s+detalle\b", "vista de detalle"),
    (r"\bpiezas?\s+topol[oó]gic\w*", "piezas topológicas"),
    (r"\bmembres[ií]a\w*", "membresía"),
    (r"\bdenominador\b", "denominador"),
    (r"\bKPI\b", "KPI"),
]

VOCABULARIO_PROHIBIDO: list[tuple[str, str]] = TERMINOS_TECNICOS + JERGA_DISFRAZADA

_COMPILADO = [(re.compile(p, re.IGNORECASE), termino) for p, termino in VOCABULARIO_PROHIBIDO]


def hallazgos(texto: str) -> list[tuple[str, str]]:
    """Devuelve (término prohibido, forma encontrada) por cada aparición distinta."""
    encontrados: list[tuple[str, str]] = []
    vistos: set[tuple[str, str]] = set()
    for patron, termino in _COMPILADO:
        for m in patron.finditer(texto):
            clave = (termino, m.group(0).lower())
            if clave not in vistos:
                vistos.add(clave)
                encontrados.append((termino, m.group(0)))
    return encontrados


def limpio(texto: str) -> bool:
    return not hallazgos(texto)
