"""Lectores compartidos de las fuentes publicas locales (F01, F02).

Un solo lugar donde se resuelve como se abre cada archivo crudo del proyecto, para
que cada estudio de rubro (panaderias, casas de pastas, pizzerias, ...) mida el mismo
universo y no dependa de un lector copiado.

Uso tipico desde un builder de rubro:

    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT))
    from scripts.shared.fuentes_locales import iter_f02, iter_f01

Recordatorio de guardrail 5: F02 son HABILITACIONES / registros administrativos.
Nunca se reportan como "locales activos".
"""
__all__ = [
    "RegistroF02", "DialectoF02", "detectar_dialecto", "iter_f02",
    "listar_archivos_f02", "perfilar_f02",
    "RegistroF01", "iter_f01",
    "normalizar", "reparar_mojibake",
]


def __getattr__(name):
    """Carga diferida para que los modulos tambien puedan ejecutarse con ``-m``.

    El import ansioso de ``f02`` desde el paquete hacia que
    ``python -m scripts.shared.fuentes_locales.f02`` emitiera un warning de runpy antes
    de perfilar la fuente. La API publica se conserva, pero cada modulo se carga solo
    cuando se pide uno de sus simbolos.
    """
    if name in {"RegistroF02", "DialectoF02", "detectar_dialecto", "iter_f02",
                "listar_archivos_f02", "perfilar_f02"}:
        from . import f02
        return getattr(f02, name)
    if name in {"RegistroF01", "iter_f01"}:
        from . import f01
        return getattr(f01, name)
    if name in {"normalizar", "reparar_mojibake"}:
        from . import texto
        return getattr(texto, name)
    raise AttributeError(name)
