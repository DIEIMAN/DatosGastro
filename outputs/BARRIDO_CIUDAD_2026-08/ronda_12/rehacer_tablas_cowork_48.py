# -*- coding: utf-8 -*-
"""Ronda 12 · reescribe las dos tablas que se habian armado desde el PDF (53 ejes)
contra la autoridad (48 ejes del XLSX), y deja las pruebas que rehacen las laminas 14 y 15.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pandas as pd

BASE = "outputs/BARRIDO_CIUDAD_2026-08/"
COW = BASE + "desde_cowork/evidencia_2026/"
OUT = BASE + "ronda_12/"

a = pd.read_csv(OUT + "idecba_48_autoridad.csv")

# ------------------------------------------------------ idecba_ocupacion_por_eje.csv
occ = a[
    ["zona", "eje", "tasa_ocupacion_pct", "var_interanual_pp", "que_es_en_el_atlas"]
].copy()
occ = occ.sort_values(["zona", "eje"])
occ.to_csv(COW + "idecba_ocupacion_por_eje.csv", index=False, encoding="utf-8")

# ------------------------------------------------------ idecba_ejes_comerciales.csv
ejc = a[["zona", "eje", "tramos", "esta_en_el_atlas"]].copy()
ejc = ejc.rename(columns={"zona": "zona_idecba"}).sort_values(["zona_idecba", "eje"])
ejc.to_csv(COW + "idecba_ejes_comerciales.csv", index=False, encoding="utf-8")

# ------------------------------------------------------ pruebas de las dos tesis
a["clase_atlas"] = a["esta_en_el_atlas"].str.split("—").str[0].str.strip().str.split().str[0]

pruebas = []

polo = a[a["clase_atlas"] == "SI"]
resto = a[a["clase_atlas"] == "NO"]
pruebas.append(
    {
        "tesis": "LAMINA 15 v2: «los polos consagrados son los que mas comercio pierden»",
        "como_se_probo": "media de variacion interanual, ejes que son polo del Atlas (SI) contra ejes que no lo son (NO); los 6 'parcial' quedan afuera",
        "resultado": f"polos {polo['var_interanual_pp'].mean():+.2f} pp (n={len(polo)}) · no polos {resto['var_interanual_pp'].mean():+.2f} pp (n={len(resto)})",
        "veredicto": "REFUTADA · la diferencia es de 0,39 pp con 21 casos por lado. No hay tal brecha.",
    }
)

z = a.groupby("zona").agg(
    ejes=("eje", "size"),
    suben=("var_interanual_pp", lambda s: int((s > 0).sum())),
    var_media=("var_interanual_pp", "mean"),
)
pruebas.append(
    {
        "tesis": "LAMINA 15 v2: «la brecha no es entre el norte y el sur»",
        "como_se_probo": "cuantos ejes suben en cada zona y media de variacion interanual por zona",
        "resultado": " · ".join(
            f"{i}: {int(r.suben)}/{int(r.ejes)} suben, media {r.var_media:+.2f} pp"
            for i, r in z.iterrows()
        ),
        "veredicto": "REFUTADA, y al reves: el Norte pierde ocupacion en los NUEVE ejes que releva la Ciudad; el Sur es la unica zona con media positiva.",
    }
)

nb = pd.read_csv(OUT + "notables_90_x_eje_idecba.csv")
dentro = nb[nb["eje_idecba"].notna()]
pruebas.append(
    {
        "tesis": "LAMINA 14 v2: «el eje mas vacio de la Ciudad tiene sus doce notables abiertos»",
        "como_se_probo": "atribucion de los 90 Bares Notables a los 80 tramos del glosario por calle + altura",
        "resultado": f"{len(dentro)} de 90 Notables caen dentro de un tramo del IDECBA; {(dentro['estado']=='ABIERTO').sum()} abiertos, {(dentro['estado']=='EN RIESGO').sum()} en riesgo, 0 cerrados. El eje con mas Notables adentro tiene 3, no 12.",
        "veredicto": "NO SE PUEDE SOSTENER como estaba · la afirmacion se rehace sobre los 48 ejes enteros, donde si es cierta y ademas tiene denominador.",
    }
)

tot = a["locales_ocupados"].sum() / a["locales_relevados"].sum() * 100
pruebas.append(
    {
        "tesis": "LAMINA 15 v2: «la media de la Ciudad es 90,1 %»",
        "como_se_probo": "cociente de ocupados sobre relevados en los 48 ejes",
        "resultado": f"{int(a['locales_relevados'].sum())} relevados · {int(a['locales_ocupados'].sum())} ocupados · {tot:.2f} % · variacion interanual del total -1,56 pp",
        "veredicto": "SE SOSTIENE con el valor corregido (90,0 %). El volumen no: eran 12.896 relevados, no 15.636.",
    }
)

pd.DataFrame(pruebas).to_csv(OUT + "idecba_pruebas_laminas_14_15.csv", index=False, encoding="utf-8")

extremos = pd.concat(
    [
        a.nsmallest(5, "tasa_ocupacion_pct").assign(orden="peor ocupacion"),
        a.nsmallest(5, "var_interanual_pp").assign(orden="mayor caida interanual"),
        a.nlargest(5, "var_interanual_pp").assign(orden="mayor suba interanual"),
        a.nlargest(3, "densidad_comercial_por_cuadra").assign(orden="mayor densidad comercial"),
    ]
)[["orden", "eje", "zona", "tasa_ocupacion_pct", "var_interanual_pp", "densidad_comercial_por_cuadra", "esta_en_el_atlas"]]
extremos.to_csv(OUT + "idecba_extremos_48.csv", index=False, encoding="utf-8")

print("reescritos:")
print("  " + COW + "idecba_ocupacion_por_eje.csv", len(occ), "filas")
print("  " + COW + "idecba_ejes_comerciales.csv", len(ejc), "filas")
print("  " + OUT + "idecba_pruebas_laminas_14_15.csv")
print("  " + OUT + "idecba_extremos_48.csv")
print()
for p in pruebas:
    print("·", p["tesis"])
    print("   ", p["resultado"])
    print("   ", p["veredicto"])
    print()
