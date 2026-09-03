"""Clasificador estricto de panaderias (universos A / B / C).

Alcance decidido por Diego el 2026-08-27 (nucleo + punto de coccion):

  A — nucleo: donde se ELABORA pan o se DESPACHA pan.
      * elaboracion de productos de panaderia con venta directa al publico
      * elaboracion industrial de productos de panaderia
      * elaboracion de productos de panaderia n.c.p.
      * com.min. despacho de pan y productos afines

  B — frontera / punto de coccion: fabricacion de masas y demas productos de
      pasteleria y sandwiches, y coccion de productos de panaderia cuando se
      recibe la masa ya elaborada. Tambien nombres con "panaderia" cuyo rubro
      no es concluyente. Son panaderias en el uso corriente pero NO elaboran
      la masa: se separan para poder contar con y sin ellas.

  C — fuera del universo, con etiqueta propia para poder recuperarlo:
      confiteria, com.min. de masas/bombones/sandwiches sin elaboracion,
      pizza/empanadas/faina, galletitas y bizcochos, churros y facturas
      fritas, y todo lo que no tiene senial de pan.

Recordatorio de guardrail: F02 son HABILITACIONES, no locales activos.

Devuelve un dict con: nivel, categoria_panaderia, patron_detectado,
confianza_categoria, motivo_categoria. Sin dependencias externas.
"""
from __future__ import annotations

import re
import unicodedata


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text)).strip()


# --- Universo A: rubros de elaboracion o despacho de pan -------------------------------
# Cada patron: (regex sobre texto normalizado, categoria_panaderia, etiqueta)
NUCLEO_PATTERNS = [
    (r"elaboracion industrial de productos de panaderia",
     "elaboracion_industrial", "elaboracion_industrial_panaderia"),
    (r"elaboracion de productos de panaderia con venta directa",
     "elaboracion_con_venta_directa", "elaboracion_panaderia_venta_directa"),
    (r"elaboracion de productos de panaderia n c p",
     "elaboracion_ncp", "elaboracion_panaderia_ncp"),
    (r"elaboracion de productos de panaderia",
     "elaboracion_panaderia", "elaboracion_panaderia"),
    (r"despacho de pan(\b| y productos afines)",
     "despacho_de_pan", "despacho_de_pan"),
    (r"\bpanificadora\b", "panificadora", "panificadora"),
    (r"\bfabrica de pan\b", "fabrica_de_pan", "fabrica_de_pan"),
]

# --- Universo B: punto de coccion / masas y pasteleria ---------------------------------
COCCION_PATTERNS = [
    (r"coccion de productos de panaderia",
     "punto_de_coccion", "coccion_masa_ya_elaborada"),
    (r"fabricacion de masas y demas productos de pasteleria",
     "masas_y_pasteleria", "fabricacion_masas_pasteleria"),
]

# --- Exclusiones explicitas: quedan en C pero etiquetadas ------------------------------
# El orden importa: se evalua de arriba hacia abajo.
EXCLUIDOS_PATTERNS = [
    (r"com min de masas bombones sandwiches|masas bombones sandwiches \(?sin elaboracion",
     "despacho_masas_sin_elaboracion", "masas_bombones_sin_elaboracion"),
    (r"sin elaboracion", "despacho_sin_elaboracion", "sin_elaboracion"),
    (r"elaboracion de galletitas y bizcochos|galletitas y bizcochos",
     "galletitas_bizcochos", "galletitas_y_bizcochos"),
    (r"churros y facturas fritas", "churros_facturas_fritas", "churros_facturas_fritas"),
    (r"\bconfiteria\b", "confiteria", "confiteria"),
    (r"pizza|fugazza|faina|empanadas", "pizzeria_empanadas", "pizza_empanadas"),
    (r"fabricacion de hornos|hogares y quemadores", "no_gastronomico", "fabricacion_de_hornos"),
]

# --- Senial de pan por nombre (para B cuando el rubro no dice nada) --------------------
PAN_HINT = re.compile(
    r"\bpanaderia\b|\bpanaderias\b|\bpanificad|\bboulangerie\b|\bbakery\b|"
    r"\bpanaderos?\b|\bel horno\b|\bhorno de barro\b|\bfacturas?\b|\bbolleria\b")
# Contexto de produccion que refuerza B
PROD_CONTEXT = re.compile(r"elaborac|fabric|artesanal|casera|caseras|amasad|horne|masa madre|venta")


def classify(*texts: str) -> dict:
    """Clasifica un registro a partir de uno o mas campos textuales (rubro, nombre, etc.).

    El rubro manda sobre el nombre: un local llamado "Panaderia" con rubro de
    confiteria queda en C, igual que en pastas un "La Pasta" con rubro
    restaurante quedaba fuera.
    """
    blob = " ".join(norm(t) for t in texts if t)

    # 1) nucleo -> A
    for pattern, categoria, etiqueta in NUCLEO_PATTERNS:
        if re.search(pattern, blob):
            return {
                "nivel": "A",
                "categoria_panaderia": categoria,
                "patron_detectado": etiqueta,
                "confianza_categoria": 0.9,
                "motivo_categoria": f"Rubro de nucleo: {etiqueta}",
            }

    # 2) punto de coccion / masas y pasteleria -> B
    for pattern, categoria, etiqueta in COCCION_PATTERNS:
        if re.search(pattern, blob):
            return {
                "nivel": "B",
                "categoria_panaderia": categoria,
                "patron_detectado": etiqueta,
                "confianza_categoria": 0.7,
                "motivo_categoria": (
                    "Punto de coccion / masas y pasteleria: vende productos de panaderia "
                    "pero no elabora la masa"),
            }

    # 3) exclusiones con etiqueta -> C recuperable
    for pattern, categoria, etiqueta in EXCLUIDOS_PATTERNS:
        if re.search(pattern, blob):
            return {
                "nivel": "C",
                "categoria_panaderia": categoria,
                "patron_detectado": etiqueta,
                "confianza_categoria": 0.2,
                "motivo_categoria": f"Fuera del alcance decidido: {etiqueta}",
            }

    tiene_pan = bool(PAN_HINT.search(blob))

    # 4) nombre de panaderia con contexto de produccion, rubro no concluyente -> B
    if tiene_pan and PROD_CONTEXT.search(blob):
        return {
            "nivel": "B",
            "categoria_panaderia": "probable_panaderia_produccion",
            "patron_detectado": "pan+contexto_produccion",
            "confianza_categoria": 0.6,
            "motivo_categoria": (
                "Mencion de panaderia con contexto de elaboracion/venta, rubro no concluyente"),
        }

    # 5) nombre de panaderia sin contexto -> B debil
    if tiene_pan:
        return {
            "nivel": "B",
            "categoria_panaderia": "probable_nombre_panaderia",
            "patron_detectado": "pan_en_texto",
            "confianza_categoria": 0.5,
            "motivo_categoria": "Texto menciona panaderia sin rubro concluyente",
        }

    # 6) sin senial de pan -> C (no entra al universo)
    return {
        "nivel": "C",
        "categoria_panaderia": "sin_senial_pan",
        "patron_detectado": "",
        "confianza_categoria": 0.0,
        "motivo_categoria": "Sin patron de panaderia",
    }


if __name__ == "__main__":
    pruebas = [
        # (texto, nivel esperado)
        ("Elaboracion de productos de panaderia con venta directa al publico.", "A"),
        ("Elaboracion industrial de productos de panaderia, excluido galletitas y bizcochos", "A"),
        ("Elaboracion de productos de panaderia n.c.p.", "A"),
        ("Com.Min.Despacho de pan y productos afines", "A"),
        ("Fabricacion de masas y demas productos de pasteleria y sandwiches. Coccion de "
         "productos de panaderia cuando se reciba la masa ya elaborada.", "B"),
        ("COM.MIN. DE PRODUCTOS ALIMENTICIOS | Panaderia La Nueva Esperanza", "B"),
        ("Confiteria | Panaderia y Confiteria Del Angel", "C"),
        ("Com.min.de masas,bombones, sandwiches (sin elaboracion)", "C"),
        ("Elaboracion de galletitas y bizcochos", "C"),
        ("Elaboracion de churros y facturas fritas con venta directa al publico.", "C"),
        ("Com.min. elab. y vta.pizza, fuga- zza, faina, empanadas", "C"),
        ("Fabricacion de hornos; hogares y quemadores", "C"),
        ("VENTA DE ROPA | Boutique Panamera", "C"),
    ]
    fallos = 0
    for texto, esperado in pruebas:
        got = classify(*texto.split("|"))
        ok = got["nivel"] == esperado
        fallos += not ok
        print(f"[{'OK ' if ok else 'FALLA'}] {esperado} vs {got['nivel']:1} "
              f"{got['patron_detectado']:32} | {texto[:70]}")
    print(f"\n{len(pruebas) - fallos}/{len(pruebas)} casos correctos")
