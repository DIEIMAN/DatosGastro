# -*- coding: utf-8 -*-
"""Ronda 12 · decision n.23 · la via C se abre por CENTRALIDAD, no por concentracion
de oferta bajo un techo.

Criterio de Diego (08/08/2026), que reemplaza al de la decision n.21:
    prueba = el objeto organiza su entorno, o fue puesto en el?
    publico/privado deja de ser la variable; planificado solo tampoco alcanza.

Consecuencia declarada por Diego: Bonpland, Belgrano y del Progreso MANTIENEN.
Patio Costanera Norte NO abre via C.

Antes de aplicar, las dos verificaciones que pidio:
  (a) R07 sigue abriendo por otra via?  -> si no, no se da de baja, pero la ficha
      tiene que declarar por que se sostiene.
  (b) PG009 sigue abriendo?             -> esa si puede caerse.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pandas as pd

BASE = "outputs/BARRIDO_CIUDAD_2026-08/"
SV = BASE + "seis_vias/"

filas = pd.read_csv(SV + "seis_vias_94_filas_r10.csv")
zonas = pd.read_csv(SV + "seis_vias_22_zonas_r4.csv")
zbd = pd.read_csv(SV + "zonas_via_B_via_D_r8.csv")
viaE = pd.read_csv(
    BASE + "desde_cowork/evidencia_2026/via_E_22_referencias.csv",
    engine="python",
    on_bad_lines="skip",
)

# --------------------------------------------------------------------------
# (a) R07 Costanera Norte
# --------------------------------------------------------------------------
z = zonas[zonas["referencia_id"] == "R07"].iloc[0]
b = zbd[zbd["zona_id"] == "R07"].iloc[0]
e = viaE[viaE["referencia_id"] == "R07"].iloc[0]

r07 = {
    "A · densidad y continuidad": z["via_A_abierta"],
    "B · trayectoria e instituciones": b["via_B_abierta"],
    "C · mercados y centralidades": z["via_C_abierta"],
    "D · comunidades y especializacion": b["via_D_abierta"],
    "E · reconocimiento externo": e["via_E_abierta"],
    "F · corredor": z["via_F_abierta"],
}

# --------------------------------------------------------------------------
# (b) PG009 Costanera Norte (fila de las 94)
# --------------------------------------------------------------------------
f = filas[filas["polo_id"] == "PG009_COSTANERA_NORTE"].iloc[0]
pg009 = {
    "A · densidad y continuidad": f["via_A_abierta"],
    "B · trayectoria e instituciones": f"heredada de {f['zona_via_B']} ({b['via_B_abierta']})",
    "C · mercados y centralidades": f["via_C_abierta"],
    "D · comunidades y especializacion": f"heredada de {f['zona_via_D']} ({b['via_D_abierta']})",
    "E · reconocimiento externo": f"heredada de {f['zona_via_E']} ({e['via_E_abierta']})",
    "F · corredor": f["via_F_abierta"],
}


def abiertas_sin_C(d):
    return [k for k, v in d.items() if not k.startswith("C") and str(v).startswith("si")]


print("=" * 78)
print("(a) R07 COSTANERA NORTE — estado de las seis vias ANTES de aplicar")
print("=" * 78)
for k, v in r07.items():
    print(f"  {k:36s} {v}")
print(f"\n  elongacion {z['via_F_elongacion']:.2f} · frac_banda_100m {z['via_F_frac_banda_100m']:.3f}")
print(f"  {int(z['n_locales'])} locales · {z['ha']} ha · via A con el polo {z['via_A_polos']}")
print(f"  via B: {b['via_B_total']} hito(s) — {b['via_B_nombres']} — soporte {b['via_B_soporte']}")
print(f"  via E: {e['via_E_nivel_max']}, {e['via_E_n_grupos']} grupo — {e['via_E_advertencia'][:90]}...")
ab = abiertas_sin_C(r07)
print(f"\n  >>> SIN la via C, R07 sigue abriendo por: {', '.join(ab) if ab else 'NINGUNA'}")
print(f"  >>> VEREDICTO: {'SE SOSTIENE' if ab else 'NO ABRE POR NINGUNA OTRA VIA'}")

print()
print("=" * 78)
print("(b) PG009_COSTANERA_NORTE — fila de las 94")
print("=" * 78)
for k, v in pg009.items():
    print(f"  {k:36s} {v}")
print(f"\n  {int(f['n_locales'])} locales · {f['ha']} ha · soporte: {f['soporte_clase']}")
print(f"  cobertura de la zona: {f['cobertura_de_la_zona_pct']} %")
ab9 = abiertas_sin_C(pg009)
print(f"\n  >>> SIN la via C, PG009 sigue abriendo por: {', '.join(ab9) if ab9 else 'NINGUNA'}")
print(f"  >>> VEREDICTO: {'SE SOSTIENE' if ab9 else 'SE CAE — hay que argumentar la baja'}")

# --------------------------------------------------------------------------
# aplicacion
# --------------------------------------------------------------------------
filas.loc[filas["polo_id"] == "PG009_COSTANERA_NORTE", "via_C_abierta"] = "no"
filas.loc[filas["polo_id"] == "PG009_COSTANERA_NORTE", "n_vias_geometricas_abiertas"] = (
    int(f["n_vias_geometricas_abiertas"]) - 1
)
filas.loc[filas["polo_id"] == "PG009_COSTANERA_NORTE", "nota"] = (
    str(f["nota"])
    + " || RONDA 12, decision n.23: el Patio Costanera Norte NO abre la via C. "
    "La via C se abre por centralidad (el objeto organiza su entorno), no por "
    "concentracion de oferta bajo un techo. La fila se sostiene por A y F."
)

zonas.loc[zonas["referencia_id"] == "R07", "via_C_abierta"] = "no"
zonas.loc[zonas["referencia_id"] == "R07", "via_C_mercado_patio"] = "no computa"
zonas.loc[zonas["referencia_id"] == "R07", "via_C_cual"] = (
    "Patio Costanera Norte — NO computa (decision n.23)"
)
zonas.loc[zonas["referencia_id"] == "R07", "n_vias_medibles"] = int(z["n_vias_medibles"]) - 1
zonas.loc[zonas["referencia_id"] == "R07", "n_vias_medibles_r4"] = int(z["n_vias_medibles_r4"]) - 1

filas.to_csv(SV + "seis_vias_94_filas_r12.csv", index=False, encoding="utf-8")
zonas.to_csv(SV + "seis_vias_22_zonas_r12.csv", index=False, encoding="utf-8")

resumen = pd.DataFrame(
    [
        {
            "universo": "22 zonas",
            "id": "R07",
            "nombre": "Costanera Norte",
            "abria_la_via_C_con": "Patio Costanera Norte",
            "decision_23": "la via C NO se abre (fue puesto en su entorno, no lo organiza)",
            "vias_abiertas_antes": "A · C · F",
            "vias_abiertas_despues": " · ".join(x.split(" · ")[0] for x in ab),
            "se_da_de_baja": "NO",
            "que_declara_la_ficha": (
                "R07 se sostiene por densidad (via A, polo P001) y por forma "
                "(via F, elongacion 8,06 — la mas alta de las 22). El patio dejo "
                "de contar. B queda pendiente con un solo hito sin verificar "
                "(Happening); D esta cerrada; E quedo a un grupo del umbral."
            ),
        },
        {
            "universo": "94 filas",
            "id": "PG009_COSTANERA_NORTE",
            "nombre": "Costanera Norte",
            "abria_la_via_C_con": "Patio Costanera Norte",
            "decision_23": "la via C NO se abre (fue puesto en su entorno, no lo organiza)",
            "vias_abiertas_antes": "A · C · F",
            "vias_abiertas_despues": " · ".join(x.split(" · ")[0] for x in ab9),
            "se_da_de_baja": "NO",
            "que_declara_la_ficha": (
                "Mismo cuerpo que R07: 67 locales en 38,5 ha, cobertura 100 % de "
                "la zona. Se sostiene por A y F."
            ),
        },
        {
            "universo": "22 zonas / 94 filas",
            "id": "R01 · PG001B · R05 · R10 · PG008",
            "nombre": "Palermo · Belgrano · Caballito",
            "abria_la_via_C_con": "Mercado Bonpland · Mercado de Belgrano · Mercado del Progreso",
            "decision_23": "MANTIENEN — los tres organizan su entorno",
            "vias_abiertas_antes": "sin cambio",
            "vias_abiertas_despues": "sin cambio",
            "se_da_de_baja": "NO",
            "que_declara_la_ficha": (
                "El del Progreso es privado y de 1889: con el criterio anterior "
                "('privada y planificada') se salvaba por la segunda condicion; "
                "con el nuevo se salva por la prueba directa, que es mas robusta."
            ),
        },
    ]
)
resumen.to_csv(BASE + "ronda_12/decision_23_aplicada.csv", index=False, encoding="utf-8")

print()
print("=" * 78)
print("APLICADO · escritos:")
print("  " + SV + "seis_vias_94_filas_r12.csv")
print("  " + SV + "seis_vias_22_zonas_r12.csv")
print("  " + BASE + "ronda_12/decision_23_aplicada.csv")
print()
print("Filas de las 94 con via C abierta, antes y despues:")
antes = pd.read_csv(SV + "seis_vias_94_filas_r10.csv")
print("  antes: ", (antes["via_C_abierta"] == "si").sum())
print("  despues:", (filas["via_C_abierta"] == "si").sum())
print("Zonas de las 22 con via C abierta:")
zantes = pd.read_csv(SV + "seis_vias_22_zonas_r4.csv")
print("  antes: ", (zantes["via_C_abierta"] == "si").sum())
print("  despues:", (zonas["via_C_abierta"] == "si").sum())
