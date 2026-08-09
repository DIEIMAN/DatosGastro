# -*- coding: utf-8 -*-
"""Ronda 12 · carga del catalogo de 90 Bares Notables cerrado al 100 % en la capa de hitos.

Entrada  : desde_cowork/evidencia_2026/catalogo_90_estado_final.csv  (autoridad de estado)
           hitos/hitos_capa_2026_r9.csv                              (capa vigente)
Salida   : hitos/hitos_capa_2026_r11.csv
           ronda_12/carga_catalogo_90_diff.csv
           ronda_12/catalogo_90_sin_fecha_individual.csv

Regla de Diego (08/08/2026): el nivel v2/v3 SIN FECHA INDIVIDUAL alcanza para resolver
la fila, NO alcanza para citar en el documento.
"""
import re
import unicodedata as ud

import pandas as pd

BASE = "outputs/BARRIDO_CIUDAD_2026-08/"
CAT = BASE + "desde_cowork/evidencia_2026/catalogo_90_estado_final.csv"
CAPA_IN = BASE + "hitos/hitos_capa_2026_r9.csv"
CAPA_OUT = BASE + "hitos/hitos_capa_2026_r11.csv"


def clave_direccion(s):
    """calle|altura normalizada, que es lo que empareja sin ambiguedad."""
    s = str(s).strip().lower()
    s = "".join(c for c in ud.normalize("NFD", s) if ud.category(c) != "Mn")
    s = s.replace("avenida", "av").replace("av.", "av ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^av ", "", s)
    m = re.search(r"(\d+)", s)
    num = m.group(1) if m else ""
    calle = re.sub(r"\s+", " ", re.sub(r"\d+", "", s)).strip()
    return calle + "|" + num


# tres variantes de direccion que no empatan por texto y son el mismo local
ALIAS = {
    "benito perez galdos|207": "benito perez galdos|201",
    "esqui|1393": "esquiu|1393",
    "neuquen esq espinosa|1100": "neuquen|1100",
}

# estado del catalogo -> vocabulario canonico de vigencia_verificada de la capa
ESTADO_A_VIGENCIA = {
    "ABIERTO": "si",
    "ABIERTO EN QUIEBRA": "si",
    "EN RIESGO": "en_riesgo",
    "CERRADO": "no",
}

cat = pd.read_csv(CAT)
capa = pd.read_csv(CAPA_IN)

cat["k"] = cat["direccion"].map(clave_direccion).replace(ALIAS)
capa["k"] = capa["direccion"].map(clave_direccion)

es_bar = capa["tipo"] == "Bar Notable"
idx = {k: i for i, k in capa.loc[es_bar, "k"].items()}

faltan = [k for k in cat["k"] if k not in idx]
assert not faltan, f"filas del catalogo sin fila en la capa: {faltan}"

for col in (
    "estado_catalogo_2026_08_08",
    "orden_catalogo",
    "citable_en_documento",
    "nota_ronda_12",
):
    if col not in capa.columns:
        capa[col] = pd.NA

diff = []
for _, fila in cat.iterrows():
    i = idx[fila["k"]]
    antes = (capa.at[i, "vigencia_verificada"], capa.at[i, "vigencia_nivel"])

    directa = str(fila["verificado_por"]).startswith("Diego")
    capa.at[i, "estado_catalogo_2026_08_08"] = fila["estado"]
    capa.at[i, "orden_catalogo"] = fila["orden"]
    capa.at[i, "vigencia_verificada"] = ESTADO_A_VIGENCIA[fila["estado"]]

    if directa:
        # verificacion humana directa de Diego, 08/08/2026, redes y Google Maps.
        # Resuelve la fila; no lleva fecha por establecimiento, asi que no se cita.
        capa.at[i, "vigencia_nivel"] = "v2/v3 sin fecha individual"
        capa.at[i, "vigencia_fuente"] = (
            "Verificacion humana directa (Diego, DGDGAS): redes sociales y Google Maps"
        )
        capa.at[i, "vigencia_fecha_consulta"] = "2026-08-08"
        capa.at[i, "citable_en_documento"] = False
        capa.at[i, "nota_ronda_12"] = (
            "Resuelto por verificacion humana directa del 08/08/2026. "
            "SIN FECHA DE EVIDENCIA INDIVIDUAL: no se cita en el documento."
        )
    else:
        # las 38 que ya venian del relevamiento documental o de la auditoria
        # conservan su nivel y su fecha; solo se sella el estado del catalogo.
        capa.at[i, "citable_en_documento"] = bool(
            pd.notna(capa.at[i, "vigencia_fecha"])
        )
        capa.at[i, "nota_ronda_12"] = (
            "Estado sellado contra catalogo_90_estado_final.csv (08/08/2026); "
            "nivel y fecha propios conservados."
        )

    diff.append(
        {
            "orden": fila["orden"],
            "hito_id": capa.at[i, "hito_id"],
            "nombre_capa": capa.at[i, "nombre"],
            "nombre_catalogo": fila["establecimiento"],
            "direccion": fila["direccion"],
            "vigencia_antes": antes[0],
            "vigencia_despues": capa.at[i, "vigencia_verificada"],
            "nivel_antes": antes[1],
            "nivel_despues": capa.at[i, "vigencia_nivel"],
            "cambia": antes[0] != capa.at[i, "vigencia_verificada"],
            "verificado_por": fila["verificado_por"],
            "citable_en_documento": capa.at[i, "citable_en_documento"],
            "detalle": fila["detalle"],
        }
    )

diff = pd.DataFrame(diff)
capa = capa.drop(columns=["k"])
capa.to_csv(CAPA_OUT, index=False, encoding="utf-8")
diff.to_csv(BASE + "ronda_12/carga_catalogo_90_diff.csv", index=False, encoding="utf-8")

sin_fecha = diff[~diff["citable_en_documento"].astype(bool)]
sin_fecha.to_csv(
    BASE + "ronda_12/catalogo_90_sin_fecha_individual.csv", index=False, encoding="utf-8"
)

bar = capa[capa["tipo"] == "Bar Notable"]
print("capa escrita:", CAPA_OUT, capa.shape)
print("\nBar Notable en la capa:", len(bar))
print("\nvigencia_verificada (los 90 del catalogo):")
print(bar[bar["estado_catalogo_2026_08_08"].notna()]["vigencia_verificada"].value_counts())
print("\nestado del catalogo:")
print(bar["estado_catalogo_2026_08_08"].value_counts(dropna=False))
print("\nfilas que cambiaron de veredicto:", int(diff["cambia"].sum()))
print("resueltas por Diego (sin fecha individual, NO citables):", len(sin_fecha))
print("citables con fecha propia:", int(diff["citable_en_documento"].astype(bool).sum()))
print("\nBar Notable en la capa que NO esta en los 90:")
print(bar[bar["estado_catalogo_2026_08_08"].isna()][["hito_id", "nombre", "direccion", "vigencia_verificada"]].to_string(index=False))
