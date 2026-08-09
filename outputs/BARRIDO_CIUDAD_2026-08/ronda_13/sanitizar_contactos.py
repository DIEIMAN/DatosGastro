# -*- coding: utf-8 -*-
"""Produce las derivadas `*_sin_contacto.csv` de los cuatro CSV de vigencia que
traen telefono y mail de establecimientos.

Por que existe. El guardrail 7 nombra "emails, telefonos, contactos" sin distinguir
persona de comercio, y en este repo ya esta escrito el precedente: la regla del ENTUR
en el .gitignore dice textualmente que el crudo trae telefono y mail de cada
establecimiento, que son comercios y no personas, "pero el guardrail 7 los nombra sin
esa distincion y no se la hacemos nosotros", y versiona la derivada `*_sin_contacto`.
Esto hace lo mismo para los cuatro archivos de la ronda 12 que quedaron fuera de esa
regla porque no vienen del ENTUR.

Que se retira: telefonos (fijos de CABA y moviles +54 9 11) y direcciones de correo.
Que se conserva, a proposito: los handles de Instagram y las webs propias. No son
contacto de una persona sino el canal publico donde vive la evidencia fechada, y el
metodo de vigencia entero se apoya en "hay posteo fechado en @cuenta". Retirarlos
vaciaria el archivo de su valor probatorio sin proteger a nadie.

Idempotente: correrlo dos veces da el mismo resultado.
Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "desde_cowork" / "evidencia_2026"

ARCHIVOS = [
    "PARA_CHEQUEAR_DIEGO.csv",
    "vigencia_tanda_A_centro.csv",
    "vigencia_tanda_B_almagro_norte.csv",
    "vigencia_verificada_ronda_2.csv",
]

# Columnas que son contacto de punta a punta: se vacian enteras.
COLUMNAS_DE_CONTACTO = {"telefono"}

MARCA = "[retirado - guardrail 7]"

# Movil con prefijo internacional, movil sin prefijo, y fijo de CABA de 8 digitos.
RE_TEL = re.compile(
    r"(?:\+?\s?54\s?)?(?:\(?\s?9\s?\)?\s?)?(?:\(?\s?11\s?\)?[\s-]?)?"
    r"\b\d{4}[\s.-]?\d{4}\b"
)
RE_MAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
# No confundir un rango de alturas de calle ni un anio con un telefono.
RE_FALSO_POSITIVO = re.compile(r"^\d{4}[\s.-]?\d{4}$")


def limpiar_texto(txt):
    """Retira mails y telefonos de una celda de texto libre, deja el resto intacto."""
    if not txt:
        return txt
    txt = RE_MAIL.sub(MARCA, txt)

    def _tel(m):
        crudo = m.group(0).strip()
        # 4 digitos, guion, 4 digitos es siempre un telefono: ninguna altura de calle
        # ni ningun anio se escribe asi. Se retira sin pedir contexto.
        if "-" in crudo:
            return MARCA
        # Sin guion (4 digitos, espacio o punto, 4 digitos) el numero es ambiguo, asi
        # que se exige un indicio de telefono en la ventana de alrededor.
        ventana = txt[max(0, m.start() - 24) : m.end() + 5].lower()
        indicio = any(
            s in ventana
            for s in ("+54", "tel", "whatsapp", "wsp", "cel", "llam", "(11)", " 11 ")
        )
        if not indicio and RE_FALSO_POSITIVO.match(crudo):
            return crudo
        return MARCA

    return RE_TEL.sub(_tel, txt)


def main():
    print("Sanitizado de contactos - ronda 13\n")
    for nombre in ARCHIVOS:
        origen = BASE / nombre
        destino = BASE / (origen.stem + "_sin_contacto.csv")

        with origen.open(encoding="utf-8", newline="") as fh:
            filas = list(csv.DictReader(fh))
        campos = list(filas[0].keys()) if filas else []

        vaciadas = 0
        limpiadas = 0
        for fila in filas:
            for campo in campos:
                valor = fila.get(campo) or ""
                if campo.strip().lower() in COLUMNAS_DE_CONTACTO:
                    if valor.strip():
                        fila[campo] = MARCA
                        vaciadas += 1
                    continue
                nuevo = limpiar_texto(valor)
                if nuevo != valor:
                    fila[campo] = nuevo
                    limpiadas += 1

        with destino.open("w", encoding="utf-8", newline="") as fh:
            escritor = csv.DictWriter(fh, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(filas)

        # Control: la derivada no debe conservar ningun mail ni telefono.
        texto = destino.read_text(encoding="utf-8")
        resto_mail = [m for m in RE_MAIL.findall(texto) if not m.startswith("[retirado")]
        print(
            f"{destino.name}\n"
            f"    filas {len(filas)} - columnas de contacto vaciadas {vaciadas}"
            f" - celdas de texto limpiadas {limpiadas}\n"
            f"    control: mails que quedan {len(resto_mail)}"
        )
        if resto_mail:
            print("    ATENCION, quedaron mails:", resto_mail)

    print(
        "\nLos cuatro originales van al .gitignore. Lo que se versiona son estas "
        "derivadas.\nSe conservan a proposito los handles de Instagram y las webs "
        "propias: son el canal\nde la evidencia fechada, no contacto de una persona."
    )


if __name__ == "__main__":
    main()
