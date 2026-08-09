# -*- coding: utf-8 -*-
"""El cruce IDECBA x polo a nivel POLO, no solo a nivel eje.

ronda_12/idecba_48_autoridad.csv marca 21 de los 48 ejes como `esta_en_el_atlas = SI`, pero esa
columna se lleno por nombre de eje. Esto lo mide: parsea los tramos de los 48 ejes -calle y rango
de alturas-, ubica en la base los locales de esa calle y ese rango, y prueba si caen dentro del
poligono de cada referencia. Sin construir los 80 tramos como geometria, que sigue pendiente: se
usan los locales como sonda del tramo.

NO ATRIBUYE A MANO. Av. Corrientes es el caso explicito: R02 no tiene su tramo fijado todavia, y
esa es la condicion previa. La fila sale como PENDIENTE declarado, no como SI ni como NO.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import csv
import re
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"

# Las referencias sobre las que pregunta la tarea, mas Corrientes que es el caso a NO resolver.
FOCO = {
    "R02": "Avenida Corrientes",
    "R07": "Costanera Norte",
    "R11": "Boulevard Caseros",
}


def norm(s):
    """Sin tildes, sin puntuacion, en minusculas y sin el prefijo Av./Avenida."""
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().replace(".", " ")
    s = re.sub(r"^\s*(av|avda|avenida)\s+", "", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_tramos(txt):
    """'Av. Corrientes 1101-1799 - Lavalle 501-999' -> [(calle, desde, hasta), ...]"""
    if not isinstance(txt, str):
        return []
    out = []
    for parte in re.split(r"[·;|]|\s-\s", txt):
        m = re.search(r"^(.*?)\s*(\d+)\s*[-a]\s*(\d+)\s*$", parte.strip())
        if m:
            out.append((norm(m.group(1)), int(m.group(2)), int(m.group(3))))
    return out


def calle_y_altura(direccion):
    """'Av. Corrientes 3787' -> ('corrientes', 3787)"""
    if not isinstance(direccion, str):
        return None, None
    m = re.search(r"^(.*?)\s+(\d{1,5})(?:\D|$)", direccion.strip())
    if not m:
        return norm(direccion), None
    return norm(m.group(1)), int(m.group(2))


def main():
    ejes = list(csv.DictReader(
        open(BASE / "ronda_12" / "idecba_48_autoridad.csv", encoding="utf-8")))
    refs = gpd.read_file(BASE / "geometria_r8" / "referencias_r8.geojson").to_crs(CRS_METRICO)
    refs["geometry"] = refs.geometry.map(lambda g: g if g.is_valid else g.buffer(0))

    loc = pd.read_csv(BASE / "base" / "local.csv", low_memory=False).dropna(subset=["lon", "lat"])
    loc = loc[(loc["anillo"] == "nucleo") & (loc["apto_geometria"])].copy()
    loc[["_calle", "_altura"]] = loc["direccion_norm"].apply(
        lambda d: pd.Series(calle_y_altura(d)))
    pts = gpd.GeoDataFrame(
        loc, geometry=gpd.points_from_xy(loc["lon"], loc["lat"]), crs="EPSG:4326"
    ).to_crs(CRS_METRICO)

    filas = []
    print("=" * 84)
    print("LOS 48 EJES CONTRA LAS TRES REFERENCIAS DEL FOCO")
    print("=" * 84)

    for rid, rnombre in FOCO.items():
        fila_ref = refs[refs["referencia_id"] == rid]
        if fila_ref.empty:
            print(f"\n{rid} {rnombre}: NO esta en referencias_r8")
            continue
        g = fila_ref.geometry.iloc[0]
        dentro_ref = pts[pts.within(g)]
        print(f"\n{'-' * 84}\n{rid} {rnombre} - {g.area / 10_000:.1f} ha, {len(dentro_ref)} locales")

        hallados = []
        for e in ejes:
            for calle, desde, hasta in parse_tramos(e.get("tramos", "")):
                cand = pts[(pts["_calle"] == calle)
                           & (pts["_altura"] >= desde) & (pts["_altura"] <= hasta)]
                if cand.empty:
                    continue
                n_dentro = int(cand.within(g).sum())
                if n_dentro:
                    hallados.append((e["eje"], calle, desde, hasta, n_dentro, len(cand),
                                     e.get("tasa_ocupacion_pct"), e.get("var_interanual_pp"),
                                     e.get("esta_en_el_atlas")))

        if not hallados:
            print("   NINGUN eje relevado cae adentro.")
            filas.append(dict(
                referencia=rid, nombre=rnombre, eje_idecba="", tramo="",
                locales_del_tramo_dentro=0, locales_del_tramo_total=0,
                tasa_ocupacion_pct="", var_interanual_pp="", decia_esta_en_el_atlas="",
                veredicto="SIN EJE RELEVADO - la ficha puede declararlo en vez de omitirlo",
            ))
        for eje, calle, desde, hasta, n_d, n_t, ocup, var, decia in hallados:
            print(f"   {eje:<28} {calle} {desde}-{hasta:<6} {n_d:3d} de {n_t:3d} locales adentro"
                  f"  | ocup {ocup} % var {var} pp | decia: {decia[:30]}")
            veredicto = ("PENDIENTE - el tramo de R02 no esta fijado; NO se atribuye a mano"
                         if rid == "R02" else "CAE ADENTRO - medido")
            filas.append(dict(
                referencia=rid, nombre=rnombre, eje_idecba=eje,
                tramo=f"{calle} {desde}-{hasta}",
                locales_del_tramo_dentro=n_d, locales_del_tramo_total=n_t,
                tasa_ocupacion_pct=ocup, var_interanual_pp=var,
                decia_esta_en_el_atlas=decia, veredicto=veredicto,
            ))

    # ---- Calibracion del instrumento, ANTES de creerle un solo negativo -------------------
    #
    # La primera version de esto reportaba "21 de 48 desacuerdos entre la columna y la medicion".
    # ERA UN ARTEFACTO DE LA SONDA, no un hallazgo. La sonda necesita que el nombre de calle del
    # tramo del IDECBA normalice igual que el `direccion_norm` de la base, y para varios ejes eso
    # no pasa: 'Ram�n Falc�n' contra 'Ramon L. Falcon', 'Lacroze' contra 'Federico Lacroze',
    # 'A. M. De Justo' contra 'Alicia Moreau De Justo', 'Alberdi' contra 'Juan B. Alberdi'.
    # Esos ejes matchean CERO locales en toda la base, asi que la sonda no puede verlos aunque
    # esten. Un negativo de un instrumento ciego no es un negativo.
    #
    # Se reporta caso por caso, no agregado: lo que localiza el corte de deteccion es el
    # escalonamiento, no el "acierta N de M".
    print()
    print("=" * 84)
    print("CALIBRACION DE LA SONDA - cuantos locales de la base ve cada eje, antes de geometria")
    print("=" * 84)
    ciegos = []
    for e in ejes:
        total = 0
        for calle, desde, hasta in parse_tramos(e.get("tramos", "")):
            total += int(((pts["_calle"] == calle) & (pts["_altura"] >= desde)
                          & (pts["_altura"] <= hasta)).sum())
        if total < 3:
            ciegos.append((e["eje"], total, e.get("tramos", "")))
        filas.append(dict(
            referencia="(calibracion)", nombre="", eje_idecba=e["eje"],
            tramo=e.get("tramos", ""), locales_del_tramo_dentro="",
            locales_del_tramo_total=total, tasa_ocupacion_pct="", var_interanual_pp="",
            decia_esta_en_el_atlas=e.get("esta_en_el_atlas"),
            veredicto=("LA SONDA NO LO VE - menos de 3 locales matchean en toda la base"
                       if total < 3 else "la sonda lo ve"),
        ))
    print(f"   ejes que la sonda NO puede ver ({len(ciegos)} de 48):")
    for nombre, total, tramos in sorted(ciegos, key=lambda t: t[1]):
        print(f"      {nombre:<30} {total} locales  | {tramos[:46]}")
    print(f"\n   >>> Sobre estos {len(ciegos)} ejes esta corrida NO dice nada, ni si ni no.")
    print("   >>> Construir los 80 tramos como geometria es lo que lo resuelve (pendiente 4).")

    # ---- El negativo de R07 y R11, verificado sin depender de la sonda -------------------
    #
    # La tarea pide confirmar que Costanera Norte y Boulevard Caseros NO tienen eje relevado,
    # para que la ficha pueda declararlo. Un negativo de la sonda no alcanza, asi que se verifica
    # por el otro lado: se listan las CALLES de los locales que caen adentro de cada poligono y
    # se cruzan contra las calles de los 48 tramos. Si ninguna calle de la referencia aparece en
    # ningun tramo, el negativo es solido y no depende de que la altura parsee bien.
    print()
    print("=" * 84)
    print("EL NEGATIVO DE R07 Y R11, VERIFICADO POR CALLE Y NO POR LA SONDA")
    print("=" * 84)
    calles_relevadas = {}
    for e in ejes:
        for calle, desde, hasta in parse_tramos(e.get("tramos", "")):
            calles_relevadas.setdefault(calle, []).append((e["eje"], desde, hasta))

    for rid in ("R07", "R11"):
        fila_ref = refs[refs["referencia_id"] == rid]
        if fila_ref.empty:
            continue
        g = fila_ref.geometry.iloc[0]
        dentro_ref = pts[pts.within(g)]
        print(f"\n   {rid} {FOCO[rid]}")
        choques = []
        for calle in sorted({c for c in dentro_ref["_calle"] if isinstance(c, str) and c}):
            for relevada, tramos in calles_relevadas.items():
                # coincidencia laxa a proposito: si la calle de la referencia CONTIENE el nombre
                # relevado o al reves, se mira. Falsos positivos si; falsos negativos no.
                if relevada and (relevada in calle or calle in relevada):
                    alturas = sorted(a for a in dentro_ref.loc[dentro_ref["_calle"] == calle,
                                                               "_altura"].dropna())
                    for eje, desde, hasta in tramos:
                        solapa = any(desde <= a <= hasta for a in alturas)
                        choques.append((calle, eje, desde, hasta, alturas, solapa))
        if not choques:
            print("      ninguna de sus calles figura en ningun tramo de los 48. NEGATIVO SOLIDO.")
        for calle, eje, desde, hasta, alturas, solapa in choques:
            rango = f"{min(alturas)}-{max(alturas)}" if alturas else "sin altura"
            estado = "SOLAPA" if solapa else "no solapa"
            print(f"      calle '{calle}' esta en el eje {eje} ({desde}-{hasta}); "
                  f"la referencia la tiene en {rango} -> {estado}")
            filas.append(dict(
                referencia=rid, nombre=FOCO[rid], eje_idecba=eje,
                tramo=f"{calle} {desde}-{hasta}",
                locales_del_tramo_dentro="", locales_del_tramo_total="",
                tasa_ocupacion_pct="", var_interanual_pp="", decia_esta_en_el_atlas="",
                veredicto=(f"misma calle, alturas {rango} contra {desde}-{hasta}: {estado}"),
            ))

    destino = SALIDA / "idecba_x_polo.csv"
    with destino.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"\nEscrito: {destino.name} ({len(filas)} filas)")


if __name__ == "__main__":
    main()
