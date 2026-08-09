# -*- coding: utf-8 -*-
"""Genera desde_cowork/evidencia_2026/INDICE.csv leyendo la carpeta, no una lista a mano.

El handoff nombraba este archivo como si existiera y no existia. Se genera en vez de escribirse
para que se pueda regenerar: la carpeta crecio de 16 a 99 archivos en tres dias y un indice
escrito a mano nace desactualizado.

Cada fila: archivo, tipo, tamano, filas (si es CSV) o titulo (si es MD), fecha de modificacion y
si esta bajo git. La columna `bajo_git` es la que importaba en la auditoria del 09/08.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import subprocess
from datetime import datetime
from pathlib import Path

CARPETA = Path(__file__).resolve().parents[1] / "desde_cowork" / "evidencia_2026"
RAIZ = Path(__file__).resolve().parents[3]


def rastreados():
    """Ruta relativa al repo de todo lo que git ya sigue dentro de la carpeta."""
    out = subprocess.run(
        ["git", "ls-files", str(CARPETA.relative_to(RAIZ)).replace("\\", "/")],
        capture_output=True, text=True, cwd=RAIZ,
    ).stdout
    return {line.strip().split("/")[-1] for line in out.splitlines() if line.strip()}


def ignorados(nombres):
    """Los que el .gitignore excluye a proposito, para no confundirlos con un olvido.

    Los paths van como ARGUMENTOS y no por --stdin: el --stdin del git de Windows devuelve
    rc=1 y salida vacia aunque el path este efectivamente ignorado. Con argumentos anda.
    """
    rel = [f"{CARPETA.relative_to(RAIZ)}/{n}".replace("\\", "/") for n in nombres]
    encontrados = set()
    for i in range(0, len(rel), 50):  # de a 50 para no pasarse del largo de linea de comando
        out = subprocess.run(
            ["git", "check-ignore", *rel[i : i + 50]],
            capture_output=True, text=True, cwd=RAIZ,
        ).stdout
        encontrados |= {l.strip().split("/")[-1] for l in out.splitlines() if l.strip()}
    return encontrados


def titulo_md(ruta):
    with ruta.open(encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            if linea.startswith("# "):
                return linea[2:].strip()
    return ""


def perfil_csv(ruta):
    try:
        with ruta.open(encoding="utf-8", errors="replace", newline="") as fh:
            lector = csv.reader(fh)
            cabecera = next(lector, [])
            n = sum(1 for _ in lector)
        return n, len(cabecera), "; ".join(cabecera[:6])
    except Exception:
        return "", "", ""


def main():
    archivos = sorted([p for p in CARPETA.iterdir() if p.is_file()], key=lambda p: p.name.lower())
    nombres = [p.name for p in archivos]
    en_git = rastreados()
    fuera = ignorados(nombres)

    filas = []
    for p in archivos:
        if p.name == "INDICE.csv":
            continue
        ext = p.suffix.lower().lstrip(".")
        n_filas = n_cols = cols = ""
        titulo = ""
        if ext == "csv":
            n_filas, n_cols, cols = perfil_csv(p)
        elif ext == "md":
            titulo = titulo_md(p)
        if p.name in en_git:
            estado = "rastreado"
        elif p.name in fuera:
            estado = "ignorado a proposito"
        else:
            estado = "SIN RASTREAR"
        filas.append(dict(
            archivo=p.name, tipo=ext, kb=round(p.stat().st_size / 1024, 1),
            filas=n_filas, columnas=n_cols,
            titulo_o_columnas=titulo or cols,
            modificado=datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            bajo_git=estado,
        ))

    destino = CARPETA / "INDICE.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)

    resumen = {}
    for f in filas:
        resumen[f["bajo_git"]] = resumen.get(f["bajo_git"], 0) + 1
    print(f"INDICE.csv: {len(filas)} archivos")
    for k, v in sorted(resumen.items()):
        print(f"   {k:<22} {v}")
    tipos = {}
    for f in filas:
        tipos[f["tipo"]] = tipos.get(f["tipo"], 0) + 1
    print("   por tipo:", tipos)


if __name__ == "__main__":
    main()
