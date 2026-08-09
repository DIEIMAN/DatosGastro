# -*- coding: utf-8 -*-
"""Ronda 12 · errata ERR-01 y ERR-02 · el IDECBA vigente son 48 ejes, no 53.

La autoridad es el XLSX (`AC_EJ_2026_03.xlsx`), no el informe en PDF.
Este script:
  1. arma la tabla autoridad de los 48 ejes (1er cuatrimestre de 2026) con sus tramos;
  2. cruza contra las dos tablas que se escribieron desde el PDF y saca las que no estan;
  3. deja constancia de que sostenia cada eje que sale;
  4. atribuye los 90 Bares Notables a los ejes por calle + altura (los 80 tramos del glosario);
  5. recalcula los extremos que citaban las laminas 4, 12, 14 y 15.
"""
import re
import sys, io
import unicodedata as ud

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pandas as pd

BASE = "outputs/BARRIDO_CIUDAD_2026-08/"
COW = BASE + "desde_cowork/evidencia_2026/"
OUT = BASE + "ronda_12/"


def sinacento(s):
    return "".join(c for c in ud.normalize("NFD", str(s)) if ud.category(c) != "Mn")


def nk(s):
    s = sinacento(s).strip().upper().replace(".", "")
    return re.sub(r"\s+", " ", s)


# ---------------------------------------------------------------- 1 · autoridad
aut = pd.read_csv(BASE + "ronda_10/idecba_densidad_48_ejes.csv")
glos = pd.read_csv(BASE + "idecba/ejes_comerciales_48_vigente.csv")
tramos = (
    glos.assign(t=glos["calle"].str.strip() + " " + glos["altura_texto"])
    .groupby("eje", sort=False)["t"]
    .apply(" · ".join)
)
aut["tramos"] = aut["eje"].map(tramos)
assert aut["tramos"].notna().all(), aut[aut["tramos"].isna()]["eje"].tolist()
aut["k"] = aut["eje"].map(nk)

# ---------------------------------------------------------------- 2 · el cruce
occ = pd.read_csv(COW + "idecba_ocupacion_por_eje.csv")
ejc = pd.read_csv(COW + "idecba_ejes_comerciales.csv")
occ["k"] = occ["eje"].map(nk)
ejc["k"] = ejc["eje"].map(nk)

k48 = set(aut["k"])
salen = sorted(set(occ["k"]) - k48)
entra = sorted(k48 - set(occ["k"]))
print(f"ejes en el PDF: {len(occ)} · ejes en el XLSX vigente: {len(aut)}")
print(f"SALEN (estaban en el PDF y no en los 48): {salen}")
print(f"ENTRA (esta en los 48 y no estaba en mi lista): {entra}")

zona = dict(zip(occ["k"], occ["zona"]))
nota_atlas = dict(zip(occ["k"], occ["que_es_en_el_atlas"].fillna("")))
en_atlas = dict(zip(ejc["k"], ejc["esta_en_el_atlas"]))

# Lavalle no estaba en la lista del PDF: no hereda zona ni anotacion.
aut["zona"] = aut["k"].map(zona).fillna("Centro")
aut["zona_origen"] = aut["k"].map(
    lambda k: "heredada del PDF" if k in zona else "asignada por localizacion (el XLSX no trae zona)"
)
aut["que_es_en_el_atlas"] = aut["k"].map(nota_atlas).fillna("")
aut["esta_en_el_atlas"] = aut["k"].map(en_atlas).fillna("NO — candidato a evaluar con las seis vias")

# las anotaciones del PDF traen valores del PDF adentro: se limpian las que citan cifras
aut.loc[aut["k"] == "LINIERS", "que_es_en_el_atlas"] = (
    "E07 Mercado Andino — SIN CAIDA en la serie vigente (0,0 pp)"
)
aut.loc[aut["k"] == "DEFENSA", "que_es_en_el_atlas"] = (
    "R03 San Telmo — SUBE 2,7 pp en la serie vigente; su via E ya estaba en dos grupos"
)
aut.loc[aut["k"] == "PALERMO SOHO", "que_es_en_el_atlas"] = "subzona de Palermo"
aut.loc[aut["k"] == "AVELLANEDA", "que_es_en_el_atlas"] = "la mayor densidad comercial de los 48"
aut.loc[aut["k"] == "LAVALLE", "que_es_en_el_atlas"] = (
    "R12 Centro — Corrientes 501-999 · Lavalle 501-999 · Esmeralda 401-599. "
    "Es el eje del microcentro peatonal en la serie vigente."
)
aut.loc[aut["k"] == "FLORIDA", "que_es_en_el_atlas"] = (
    "R12 Centro — Florida 1-999. OJO: Plaza Bar esta en Florida 1005, seis numeros afuera del eje."
)
aut.loc[aut["k"] == "VILLA CRESPO", "que_es_en_el_atlas"] = (
    "R08 — LA MAYOR CAIDA INTERANUAL DE LOS 48 (-9,1 pp)"
)
aut.loc[aut["k"] == "PARQUE AVELLANEDA", "que_es_en_el_atlas"] = (
    "LA PEOR OCUPACION DE LOS 48 (77,8 %), pero sube 2,5 pp"
)

cols = [
    "eje", "zona", "zona_origen", "tramos", "locales_relevados", "locales_ocupados",
    "cuadras", "densidad_comercial_por_cuadra", "tasa_ocupacion_pct",
    "var_interrelevamiento_pp", "var_interanual_pp", "esta_en_el_atlas", "que_es_en_el_atlas",
]
aut[cols].sort_values(["zona", "eje"]).to_csv(
    OUT + "idecba_48_autoridad.csv", index=False, encoding="utf-8"
)

# ------------------------------------------------- 3 · que sostenia cada uno que sale
sostenia = {
    "MICROCENTRO": "LAMINA 14 entera (63,2 % de ocupacion, -7,2 pp, 'el eje mas vacio de la Ciudad'), "
                   "la primera fila de la LAMINA 15, el remate de EL_CATALOGO_CERRADO.md "
                   "('el corredor mas vacio y sus doce notables abiertos') y la recomendacion "
                   "'si hace falta una sola lamina, la 14'.",
    "PALERMO HOLLYWOOD": "la quinta fila de la LAMINA 15 (80,5 % / -4,1 pp) y una de las tres patas del "
                         "argumento de que el IDECBA trata Soho, Hollywood y Canitas como ejes distintos.",
    "CANITAS": "la corroboracion del censo de Las Canitas en LA_FUENTE_QUE_NOS_FALTABA.md "
               "(89,2 % / +3,2 pp, 'CORROBORA LA RECONVERSION') y una de las subas de la LAMINA 15.",
    "NAZCA": "la mayor suba citada en la LAMINA 15 (+5,7 pp).",
    "MURILLO": "una de las subas de la LAMINA 15 (+4,0 pp) y un 'candidato que no esta en nuestra matriz'.",
    "JUJUY": "solo una fila de la tabla de ocupacion; no sostenia ninguna afirmacion publicada.",
}
sal = occ[occ["k"].isin(salen)].copy()
sal["que_sostenia"] = sal["k"].map(sostenia)
sal["por_que_sale"] = (
    "No figura en ninguno de los cuatro cuatrimestres de la serie vigente "
    "(1er 2025 · 2do 2025 · 3er 2025 · 1er 2026), que son de 48 ejes. "
    "El valor viene de una edicion anterior del relevamiento leida en PDF."
)
sal[["zona", "eje", "tasa_ocupacion_pct", "var_interanual_pp", "que_sostenia", "por_que_sale"]].to_csv(
    OUT + "idecba_los_6_que_salen.csv", index=False, encoding="utf-8"
)

# ------------------------------------------------- 4 · los 90 Notables sobre los tramos
CALLE_ALIAS = {
    "SERRANO / BORGES": ["SERRANO", "JORGE LUIS BORGES", "BORGES"],
    "A M DE JUSTO": ["ALICIA MOREAU DE JUSTO", "A M DE JUSTO"],
    "AV REG DE LOS PATRICIOS": ["AV REGIMIENTO DE PATRICIOS", "REGIMIENTO DE PATRICIOS"],
    "JOSE MARIA MORENO": ["JOSE MARIA MORENO"],
    "RAMON FALCON": ["RAMON L FALCON", "RAMON FALCON"],
    "ORTIZ": ["RM ORTIZ", "R M ORTIZ", "ROBERTO M ORTIZ"],
}


def calles_de(nombre):
    n = nk(nombre)
    n = re.sub(r"^AV ", "", n)
    base = [n]
    for k, v in CALLE_ALIAS.items():
        if nk(k) == nk(nombre):
            base = [nk(x) for x in v]
    return base


def calle_de_direccion(d):
    s = nk(d)
    s = re.sub(r"\bAV\b", "", s)
    s = re.sub(r"\d+.*$", "", s).strip()
    s = s.strip(" ,")
    return s


def altura_de(d):
    m = re.search(r"(\d+)", str(d))
    return int(m.group(1)) if m else None


glos["calles_norm"] = glos["calle"].map(lambda c: calles_de(c))
cat = pd.read_csv(COW + "catalogo_90_estado_final.csv")

asign = []
for _, b in cat.iterrows():
    c = calle_de_direccion(b["direccion"])
    a = altura_de(b["direccion"])
    hit = None
    for _, g in glos.iterrows():
        if c and any(c == x or c.endswith(" " + x) or x.endswith(" " + c) for x in g["calles_norm"]):
            if a is not None and int(g["altura_desde"]) <= a <= int(g["altura_hasta"]):
                hit = g["eje"]
                break
    asign.append(hit)
cat["eje_idecba"] = asign

cat[["orden", "establecimiento", "direccion", "barrio", "estado", "eje_idecba"]].to_csv(
    OUT + "notables_90_x_eje_idecba.csv", index=False, encoding="utf-8"
)
dentro = cat[cat["eje_idecba"].notna()]
print(f"\nBares Notables de los 90 que caen dentro de un tramo del IDECBA: {len(dentro)} de 90")
print(dentro.groupby("eje_idecba")["orden"].count().sort_values(ascending=False).to_string())

# ------------------------------------------------- 5 · los extremos, recalculados
print("\n" + "=" * 78)
print("EXTREMOS DE LA SERIE VIGENTE (48 ejes · 1er cuatrimestre de 2026)")
print("=" * 78)
print("\nPeor ocupacion:")
print(aut.nsmallest(5, "tasa_ocupacion_pct")[["eje", "tasa_ocupacion_pct", "var_interanual_pp"]].to_string(index=False))
print("\nMayor caida interanual:")
print(aut.nsmallest(6, "var_interanual_pp")[["eje", "tasa_ocupacion_pct", "var_interanual_pp"]].to_string(index=False))
print("\nMayor suba interanual:")
print(aut.nlargest(5, "var_interanual_pp")[["eje", "tasa_ocupacion_pct", "var_interanual_pp"]].to_string(index=False))
tot = aut["locales_ocupados"].sum() / aut["locales_relevados"].sum() * 100
print(f"\nTotal: {int(aut['locales_relevados'].sum())} relevados · {int(aut['locales_ocupados'].sum())} ocupados · {tot:.2f} %")
print("\nMedia por zona (ponderada por locales relevados):")
z = aut.groupby("zona").apply(
    lambda d: pd.Series(
        {
            "ejes": len(d),
            "relevados": int(d["locales_relevados"].sum()),
            "tasa_pct": d["locales_ocupados"].sum() / d["locales_relevados"].sum() * 100,
            "var_media_pp": d["var_interanual_pp"].mean(),
        }
    ),
    include_groups=False,
)
print(z.to_string())

print("\nLos ejes que las laminas citan, con el valor de la autoridad:")
for e in ["Liniers", "Defensa", "Montes de Oca", "Palermo Soho", "Florida", "Lavalle", "Monserrat", "Villa Crespo"]:
    r = aut[aut["eje"] == e].iloc[0]
    print(f"  {e:16s} {r['tasa_ocupacion_pct']:5.1f} %  {r['var_interanual_pp']:+5.1f} pp   {r['tramos']}")
