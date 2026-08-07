"""Los tres conteos de Bares Notables que no coinciden: 84, 95 y 90. Quién tiene qué.

QUÉ PREGUNTA CONTESTA, Y CUÁL NO
---------------------------------
Hay tres listas de Bares Notables en el repositorio y **ninguna coincide con las otras**:

    REFERENTES_2026 · catálogo GCBA (data.buenosaires)          84
    dataset_bares_notables · Wikidata (CC0)                     95
    hitos_documentales_caba · catálogo del Boletín Oficial      90

`RECONCILIACION_HITOS.md` lo marcó como «la clase de divergencia silenciosa que este proyecto ya
cazó tres veces» y pidió una corrida que cruce las tres **sin decidir cuál manda**. Eso hace ésta:
dice quién tiene qué. **No elige.** Elegir requiere saber a qué fecha está cada lista y contra qué
acto administrativo, y eso no está en ninguno de los tres archivos.

POR QUÉ EL CRUCE ES POR NOMBRE **Y** DIRECCIÓN, Y NO POR UNO SOLO
-------------------------------------------------------------------
Por nombre solo no alcanza: hay bares homónimos y hay el mismo bar escrito de tres formas —«Café
Tortoni», «CAFE TORTONI», «El Tortoni»—. Por dirección sola tampoco: las tres listas asientan la
calle con convenciones distintas —«Avenida de Mayo 825» contra «DE MAYO AV. 825, CABA»— que es
exactamente el problema que resolvió `normalizar_calles.py`, así que **se reusa su clave** en vez
de escribir otra normalización acá.

Se cruza en dos pasadas: primero por (calle, altura), que es la identidad fuerte; después, sobre
lo que quedó suelto, por nombre plegado. Cada emparejamiento queda anotado con **cómo** se hizo,
para que se pueda revisar el que se hizo por el camino débil.

Google Places: 0 requests. No se consulta ningún servicio: sólo se leen los tres archivos.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/hitos_cruzar_bares_notables.py
"""
from __future__ import annotations

import io
import re
import sys
import unicodedata
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from normalizar_calles import clave_calle  # noqa: E402

REFERENTES = ROOT / "outputs" / "polos_gastro" / "REFERENTES_2026" / "matriz_referentes_final_2026.csv"
WIKIDATA = (ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "dataset_bares_notables" /
            "bares_notables_caba.csv")
DOCUMENTAL = (ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "desde_cowork" /
              "hitos_documentales_caba.csv")
OUT = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "hitos"

# Palabras que anteceden al nombre y no lo distinguen: las tres listas las ponen o no las ponen.
PREFIJOS_VACIOS = {"CAFE", "BAR", "CONFITERIA", "EL", "LA", "LOS", "LAS", "DE", "DEL", "Y",
                   "RESTAURANT", "RESTAURANTE", "PIZZERIA", "BILLARES", "NOTABLE"}


def plegar_nombre(nombre: str) -> str:
    """El nombre sin tildes, sin caja y sin las palabras que las tres listas ponen a discreción."""
    texto = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode().upper()
    tokens = [t for t in re.split(r"[^A-Z0-9]+", texto) if t and t not in PREFIJOS_VACIOS]
    return " ".join(sorted(tokens))


def altura(direccion: str) -> str:
    """La altura de la dirección. Es la mitad fuerte de la identidad; la otra es la calle."""
    hallada = re.search(r"\b(\d{1,5})\b", str(direccion))
    return hallada.group(1) if hallada else ""


def clave_domicilio(direccion: str) -> str:
    """`(calle, altura)` con la clave de calle del normalizador, que ya pliega las convenciones."""
    if not isinstance(direccion, str) or not direccion.strip():
        return ""
    numero = altura(direccion)
    calle = clave_calle(direccion)
    return f"{calle}|{numero}" if calle and numero else ""


def cargar() -> dict[str, pd.DataFrame]:
    referentes = pd.read_csv(REFERENTES, comment="#")
    referentes = referentes[referentes.tipo == "Bar Notable"]
    wikidata = pd.read_csv(WIKIDATA, comment="#")
    documental = pd.read_csv(DOCUMENTAL)
    documental = documental[documental.tipo == "bar_notable"]
    return {
        "GCBA_84": pd.DataFrame({
            "id": referentes.id, "nombre": referentes.nombre, "direccion": referentes.direccion}),
        "WIKIDATA_95": pd.DataFrame({
            "id": wikidata.wikidata_id, "nombre": wikidata.nombre,
            "direccion": wikidata.direccion_declarada}),
        "BOLETIN_90": pd.DataFrame({
            "id": documental.hito_id, "nombre": documental.nombre,
            "direccion": documental.direccion}),
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    listas = cargar()
    for nombre, tabla in listas.items():
        tabla["clave_dom"] = tabla.direccion.map(clave_domicilio)
        tabla["clave_nom"] = tabla.nombre.map(plegar_nombre)
        tabla["lista"] = nombre

    p("BARES NOTABLES · las tres listas cruzadas. Quién tiene qué, sin decidir cuál manda.")
    p("=" * 100)
    p("")
    for nombre, tabla in listas.items():
        p(f"  {nombre:<14} {len(tabla):>3} filas · "
          f"{int((tabla.clave_dom != '').sum())} con domicilio utilizable")
    p("")
    p("  El cruce es en dos pasadas: (calle, altura) primero —identidad fuerte, con la clave de")
    p("  `normalizar_calles.py`— y nombre plegado después, sobre lo que quedó suelto. Cada")
    p("  emparejamiento dice por cuál de los dos caminos se hizo.")
    p("")

    # ------------------------------------------------------------------ unir en grupos
    #
    # Tres criterios de fusión, en orden de fuerza, y **ninguno implícito**. La primera versión de
    # este cruce fusionaba por nombre plegado a secas y juntó «Café Roma» (Olavarría 409) con
    # «Roma del Abasto» (San Luis 3101): dos bares distintos contados como uno, que es el error
    # más caro acá porque infla «está en las tres listas». El nombre solo no alcanza: por eso la
    # fusión por nombre exige además la misma calle.
    todas = pd.concat(listas.values(), ignore_index=True).reset_index(drop=True)
    padre = list(range(len(todas)))

    def raiz(i):
        while padre[i] != i:
            padre[i] = padre[padre[i]]
            i = padre[i]
        return i

    def unir(a, b, motivo, registro):
        ra, rb = raiz(a), raiz(b)
        if ra != rb:
            padre[rb] = ra
            registro.append(motivo)

    motivos: dict[int, set[str]] = {}

    def anotar(indice, motivo):
        motivos.setdefault(indice, set()).add(motivo)

    # La calle se compara por CONTENCIÓN de tokens y no por igualdad, porque las tres listas
    # escriben el nombre de pila del prócer o no lo escriben: `MONTES DE OCA` contra
    # `MANUEL MONTES DE OCA`, `QUINTANA` contra `MANUEL QUINTANA`, `SCALABRINI ORTIZ` contra
    # `RAUL SCALABRINI ORTIZ`. Es el residuo que `normalizar_calles.py` declara que no puede cerrar
    # sin callejero; acá no hace falta cerrarlo, sólo tolerarlo para emparejar.
    def calle_y_altura(indice):
        calle, alt = todas.clave_dom[indice].split("|")
        return frozenset(calle.split()), int(alt)

    def misma_calle(i, j):
        a, b = calle_y_altura(i)[0], calle_y_altura(j)[0]
        return bool(a) and bool(b) and (a <= b or b <= a)

    con_domicilio = [i for i in range(len(todas)) if todas.clave_dom[i]]

    # 1 · misma calle (por contención) y MISMA altura: identidad fuerte.
    for a in range(len(con_domicilio)):
        for b in range(a + 1, len(con_domicilio)):
            i, j = con_domicilio[a], con_domicilio[b]
            if raiz(i) == raiz(j):
                continue
            if calle_y_altura(i)[1] == calle_y_altura(j)[1] and misma_calle(i, j):
                registro = []
                unir(i, j, "domicilio", registro)
                if registro:
                    anotar(raiz(i), "domicilio")

    # 2 · mismo nombre plegado Y misma calle Y altura a menos de TOLERANCIA_ALTURA:
    #     «36 Billares» está en Av. de Mayo 1262 y 1265 según quién lo cargó. La tolerancia es una
    #     convención declarada, no una medición, y cada fusión que pasa por acá se imprime.
    TOLERANCIA_ALTURA = 50
    fusiones_por_nombre = []
    homonimos_otra_calle = []
    con_nombre: dict[str, list[int]] = {}
    for i in con_domicilio:
        if todas.clave_nom[i]:
            con_nombre.setdefault(todas.clave_nom[i], []).append(i)
    for indices in con_nombre.values():
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                i, j = indices[a], indices[b]
                if raiz(i) == raiz(j):
                    continue
                if misma_calle(i, j) and abs(
                        calle_y_altura(i)[1] - calle_y_altura(j)[1]) <= TOLERANCIA_ALTURA:
                    registro = []
                    unir(i, j, "nombre+calle", registro)
                    if registro:
                        anotar(raiz(i), "nombre+calle")
                        fusiones_por_nombre.append(
                            f"{todas.nombre[i]} ({todas.direccion[i]})  +  "
                            f"{todas.nombre[j]} ({todas.direccion[j]})")
                else:
                    # La altura decide qué mirar primero: mismo nombre y MISMA altura en calles
                    # que no matchean es casi siempre la misma calle escrita distinto —«Jorge Luis
                    # Borges» contra «Jorge L. Borges», el residuo de las iniciales—. Con altura
                    # distinta es más probable que sean dos bares de verdad.
                    misma_alt = calle_y_altura(i)[1] == calle_y_altura(j)[1]
                    par = tuple(sorted([
                        f"{todas.nombre[i]} ({todas.direccion[i]})",
                        f"{todas.nombre[j]} ({todas.direccion[j]})"]))
                    homonimos_otra_calle.append((misma_alt, par))

    # 3 · sin domicilio utilizable: sólo queda el nombre, y se dice que fue por ahí.
    sin_domicilio_pegados = []
    primero_con_nombre = {}
    for i, fila in todas.iterrows():
        if fila.clave_dom and fila.clave_nom:
            primero_con_nombre.setdefault(fila.clave_nom, i)
    for i, fila in todas.iterrows():
        if fila.clave_dom or not fila.clave_nom:
            continue
        destino = primero_con_nombre.get(fila.clave_nom)
        if destino is not None:
            registro = []
            unir(destino, i, "solo nombre", registro)
            if registro:
                anotar(raiz(destino), "solo nombre")
                sin_domicilio_pegados.append(f"{fila.nombre} → {todas.nombre[destino]}")

    finales: dict[int, dict] = {}
    for i in range(len(todas)):
        grupo = finales.setdefault(raiz(i), {"miembros": [], "por": set()})
        grupo["miembros"].append(todas.iloc[i])
    for indice, grupo in finales.items():
        grupo["por"] = "+".join(sorted(motivos.get(indice, {"unico"}))) or "unico"

    # ------------------------------------------------------------------ el reporte
    filas = []
    for grupo in finales.values():
        presentes = {m.lista for m in grupo["miembros"]}
        filas.append({
            "bar": sorted({m.nombre for m in grupo["miembros"]}, key=len)[0],
            "nombres_vistos": " | ".join(sorted({str(m.nombre) for m in grupo["miembros"]})),
            "direcciones_vistas": " | ".join(
                sorted({str(m.direccion) for m in grupo["miembros"] if pd.notna(m.direccion)})),
            "en_GCBA_84": "si" if "GCBA_84" in presentes else "no",
            "en_WIKIDATA_95": "si" if "WIKIDATA_95" in presentes else "no",
            "en_BOLETIN_90": "si" if "BOLETIN_90" in presentes else "no",
            "n_listas": len(presentes),
            "emparejado_por": grupo["por"],
        })
    cruce = pd.DataFrame(filas).sort_values(
        ["n_listas", "bar"], ascending=[False, True]).reset_index(drop=True)

    p("-" * 100)
    p("  EL RESULTADO")
    p("")
    p(f"      {len(cruce)} bares distintos entre las tres listas.")
    p("")
    combinaciones = cruce.groupby(
        ["en_GCBA_84", "en_WIKIDATA_95", "en_BOLETIN_90"]).size().sort_values(ascending=False)
    p("      GCBA  WIKI  BOLETIN   bares")
    for (g, w, b), n in combinaciones.items():
        marca = "  ← en las tres" if g == w == b == "si" else ""
        p(f"      {g:<5} {w:<5} {b:<9} {n:>3}{marca}")
    p("")

    en_las_tres = int((cruce.n_listas == 3).sum())
    p(f"      En las TRES: {en_las_tres}. En una sola: {int((cruce.n_listas == 1).sum())}.")
    p("")
    p("      Los tres totales —84, 95, 90— no son tres recortes de una misma lista: cada una tiene")
    p("      bares que las otras dos no tienen. No hay una que contenga a las demás.")
    p("")

    for lista in ("GCBA_84", "WIKIDATA_95", "BOLETIN_90"):
        columna = f"en_{lista}"
        otras = [f"en_{o}" for o in ("GCBA_84", "WIKIDATA_95", "BOLETIN_90") if o != lista]
        solos = cruce[(cruce[columna] == "si") & (cruce[otras[0]] == "no") &
                      (cruce[otras[1]] == "no")]
        p(f"      SÓLO en {lista}: {len(solos)}")
        for fila in solos.itertuples():
            p(f"          {fila.bar}  —  {fila.direcciones_vistas or 'sin dirección'}")
        p("")

    p("-" * 100)
    p("  LO QUE SE FUSIONÓ POR EL CAMINO DÉBIL, para que se pueda revisar sin releer los archivos")
    p("")
    p(f"      · por nombre + misma calle, altura a menos de {TOLERANCIA_ALTURA}: "
      f"{len(fusiones_por_nombre)}")
    for texto in fusiones_por_nombre:
        p(f"          {texto}")
    p("")
    p(f"      · sin domicilio utilizable, pegados sólo por nombre: {len(sin_domicilio_pegados)}")
    for texto in sin_domicilio_pegados:
        p(f"          {texto}")
    p("")
    unicos = sorted({(m, par) for m, par in homonimos_otra_calle}, key=lambda x: (not x[0], x[1]))
    misma_altura = [par for m, par in unicos if m]
    otra_altura = [par for m, par in unicos if not m]
    p(f"      · MISMO NOMBRE EN OTRA CALLE: {len(unicos)} pares. **No se fusionan**, y por eso")
    p("        están acá: puede ser un homónimo de verdad o el mismo bar con la calle escrita de")
    p("        otra forma, y las dos cosas se ven igual desde el dato.")
    p("")
    p(f"        MISMA ALTURA ({len(misma_altura)}) — casi siempre la misma calle escrita distinto,")
    p("        y casi siempre por el residuo de las iniciales que el normalizador declara abierto:")
    for a, b in misma_altura:
        p(f"          {a}")
        p(f"              vs  {b}")
    p("")
    p(f"        ALTURA DISTINTA ({len(otra_altura)}) — acá es más probable que sean dos bares:")
    for a, b in otra_altura:
        p(f"          {a}")
        p(f"              vs  {b}")
    p("")

    cruce.to_csv(OUT / "cruce_bares_notables.csv", index=False, encoding="utf-8")

    p("=" * 100)
    p(f"  {len(cruce)} bares · {en_las_tres} en las tres listas · NO se decide cuál manda: eso")
    p("  necesita la fecha de corte y el acto administrativo de cada lista, que no está en los")
    p("  archivos. Google Places: 0 requests.")
    p("=" * 100)
    p("")

    salida = buffer.getvalue()
    (OUT / "CRUCE_BARES_NOTABLES.txt").write_text(salida, encoding="utf-8")
    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
