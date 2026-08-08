"""Ronda 11 · las cuatro decisiones de criterio, y el barrido de la vía C.

Google Places: **0 requests**.

    TAREA 1  las cuatro decisiones se cruzan contra las 20 ya registradas (R9) antes de cargarlas
    TAREA 2  el barrido: ¿alguna otra fila abre la vía C sobre una centralidad privada planificada?
    TAREA 3  R22 Villa Pueyrredón · la ficha con la debilidad declarada

POR QUÉ EL BARRIDO NO SE HACE A OJO
------------------------------------
La decisión (c) dice que una **centralidad comercial privada y planificada** no abre la vía C. Para
aplicarla hace falta saber, de cada mercado o patio de la capa, **qué es y quién lo gestiona** — y
la capa de hitos no tiene ese campo: `registro_oficial` está vacío en los once `Mercado/patio`.

El dato existe, y está relevado: `outputs/mercados_caba/sanitized/mercados_gastronomicos_activos_v4.csv`
trae `tipo_primario` y `gestion` para los trece del subproyecto Mercados. Se lee de ahí en vez de
clasificar de memoria, que es R13.

LO QUE EL CRITERIO NO RESUELVE SOLO
------------------------------------
«Privada **y** planificada» son dos condiciones, y el relevamiento tiene tres valores de gestión
—`publica`, `mixta`, `privada`—. Un patio gastronómico de gestión **mixta** es planificado pero no
es privado. Ese caso se marca **PARA DECISIÓN** y no se resuelve acá: elegir una lectura del
criterio de Diego sin preguntarle sería inventar la decisión, no aplicarla.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_11_decisiones_y_barrido_via_C.py
"""
from __future__ import annotations

import io
import sys
import textwrap
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import BARRIDO, sin_tildes  # noqa: E402

SEIS = BARRIDO / "seis_vias"
HITOS = BARRIDO / "hitos"
COWORK = BARRIDO / "desde_cowork" / "evidencia_2026"
SALIDA = BARRIDO / "ronda_11"
MERCADOS = ROOT / "outputs" / "mercados_caba" / "sanitized" / "mercados_gastronomicos_activos_v4.csv"

OUT_DEC = SALIDA / "decisiones_tomadas_2026-08-08.csv"
OUT_BARRIDO = SALIDA / "barrido_via_C_titularidad.csv"
OUT_R22 = SALIDA / "R22_ficha_debilidad_declarada.csv"
INFORME = SALIDA / "RONDA_11.txt"

HOY = date(2026, 8, 8)

# Las cuatro que Diego mandó, con la decisión ya registrada que las cubre (si la hay).
LAS_CUATRO = [
    ("a", "Untappd computa como v3b. La Perla se mantiene verificado_abierto.", 3),
    ("b", "Reporteo a nivel PROGRAMA acredita v4, no v1.", 2),
    ("c", "Una centralidad comercial privada y planificada NO abre la vía C. "
          "El Polo Concepción va por vía E.", None),
    ("d", "R22 Villa Pueyrredón se publica con una sola vía y 5,6 % de continuidad, "
          "con la debilidad declarada en la ficha.", None),
]

# Tipologías que SÍ son centralidad comercial planificada. Las otras —histórico, barrial,
# productores— son mercados de abasto o de trayectoria, no desarrollos comerciales.
PLANIFICADAS = {"food_hall", "patio_gastronomico"}


def p_factory(buffer: io.StringIO):
    def p(*args_):
        print(*args_, file=buffer)
    return p


def main() -> int:  # noqa: C901, PLR0915
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()
    p = p_factory(buffer)
    SALIDA.mkdir(parents=True, exist_ok=True)

    p("=" * 100)
    p("  RONDA 11 · las cuatro decisiones, y el barrido de la vía C")
    p(f"  {HOY.isoformat()} · Google Places: 0 requests")
    p("=" * 100)
    p("")

    # ==================================================== TAREA 1 · las decisiones
    p("-" * 100)
    p("  TAREA 1 · LAS CUATRO DECISIONES, CRUZADAS CONTRA LAS 20 YA REGISTRADAS")
    p("")
    previas = pd.read_csv(COWORK / "DECISIONES_TOMADAS_2026-08-07.csv", encoding="utf-8")
    capa = pd.read_csv(HITOS / "hitos_capa_2026_r9.csv", encoding="utf-8")

    p("      R9 sobre el catálogo de decisiones: DOS DE LAS CUATRO YA ESTABAN TOMADAS el 07/08.")
    p("")
    nuevas, ya_estaban = [], []
    for letra, texto, n_previa in LAS_CUATRO:
        if n_previa:
            fila = previas[previas.n == n_previa].iloc[0]
            ya_estaban.append((letra, texto, fila))
            p(f"      ({letra}) YA REGISTRADA como decisión n.º {n_previa}:")
            p(f"           «{str(fila.decision)[:84]}»")
            p(f"           → {str(fila.resolucion)[:84]}")
        else:
            nuevas.append((letra, texto))
            p(f"      ({letra}) NUEVA — se registra")
        p("")

    p("      ¿ESTÁN APLICADAS EN LA CAPA? (no alcanza con que la decisión exista)")
    p("")
    p(f"        {'hito':<28}{'veredicto':<24}{'nivel':<8}fuente")
    for pat in ("PERLA", "TANCAT", "IMPARCIAL"):
        for _, r in capa[capa.nombre.astype(str).str.contains(pat, case=False,
                                                              na=False)].iterrows():
            p(f"        {str(r['nombre'])[:26]:<28}{str(r.vigencia_verificada):<24}"
              f"{str(r.vigencia_nivel):<8}{str(r.vigencia_fuente)[:40]}")
    p("")
    p("      LAS TRES YA ESTÁN APLICADAS. Y una precisión sobre (b): **Tancat no queda en")
    p("      `probablemente_abierto`**. Bajó a v4 por el reporteo de programa, pero conserva")
    p("      `verificado_abierto` por el v2 de Instagram que verificaste vos el 07/08 — está")
    p("      escrito así en la consecuencia de la decisión n.º 2. El que queda en")
    p("      `probablemente_abierto` es El Imparcial.")
    p("")

    filas_dec = []
    for i, (letra, texto) in enumerate(nuevas, start=21):
        filas_dec.append({
            "n": i, "bloque": "criterio", "decision": texto, "resolucion": texto,
            "tomada_por": "Diego", "fecha": HOY.isoformat(),
            "consecuencia_operativa": "",
        })
    p(f"      se registran {len(filas_dec)} decisiones nuevas: n.º "
      f"{', '.join(str(f['n']) for f in filas_dec)}")
    p("")

    # ==================================================== TAREA 2 · el barrido
    p("-" * 100)
    p("  TAREA 2 · EL BARRIDO DE LA VÍA C")
    p("")
    s94 = pd.read_csv(SEIS / "seis_vias_94_filas_r10.csv", encoding="utf-8")
    orig = pd.read_csv(SEIS / "seis_vias_94_filas.csv", encoding="utf-8")
    z22 = pd.read_csv(SEIS / "seis_vias_22_zonas_r4.csv", encoding="utf-8")
    mercados = pd.read_csv(MERCADOS, encoding="utf-8")
    mercados["clave"] = mercados.nombre.map(sin_tildes)

    abiertas94 = s94[s94.via_C_abierta == "si"][["polo_id", "nombre_polo"]].merge(
        orig[["polo_id", "via_C_cual"]], on="polo_id", how="left")
    abiertas22 = z22[z22.via_C_abierta == "si"][["referencia_id", "nombre", "via_C_cual"]]
    p(f"      filas de las 94 con vía C abierta: {len(abiertas94)} "
      f"(eran 4 antes del retipado de Yiyo el Zeneize)")
    p(f"      zonas de las 22 con vía C abierta: {len(abiertas22)}")
    p("")
    p("      LA CAPA DE HITOS NO TIENE CON QUÉ DECIDIR: `registro_oficial` está vacío en los")
    p("      once `Mercado/patio` y no hay campo de titularidad ni de gestión. El dato existe")
    p("      relevado en el subproyecto Mercados y se lee de ahí — R13, contra la entidad")
    p("      nombrada y no contra mi impresión de cada nombre.")
    p("")

    filas_b = []
    for etiqueta, tabla, col_id, col_nom in (
            ("94 filas", abiertas94, "polo_id", "nombre_polo"),
            ("22 zonas", abiertas22, "referencia_id", "nombre")):
        for r in tabla.itertuples():
            cual = getattr(r, "via_C_cual")
            hit = mercados[mercados.clave == sin_tildes(str(cual))]
            if hit.empty:
                filas_b.append({"universo": etiqueta, "id": getattr(r, col_id),
                                "nombre": getattr(r, col_nom), "abre_la_via_C_con": cual,
                                "tipo_primario": "NO ESTÁ en el relevamiento de Mercados",
                                "gestion": "", "es_planificada": "",
                                "veredicto": "NO SE PUEDE DECIDIR · falta la ficha"})
                continue
            m = hit.iloc[0]
            planificada = m.tipo_primario in PLANIFICADAS
            if not planificada:
                veredicto = "MANTIENE la vía C · no es una centralidad planificada"
            elif m.gestion == "privada":
                veredicto = "PIERDE la vía C · privada y planificada"
            elif m.gestion == "publica":
                veredicto = "MANTIENE la vía C · planificada pero PÚBLICA"
            else:
                veredicto = "PARA DECISIÓN DE DIEGO · planificada y de gestión MIXTA"
            filas_b.append({"universo": etiqueta, "id": getattr(r, col_id),
                            "nombre": getattr(r, col_nom), "abre_la_via_C_con": cual,
                            "tipo_primario": m.tipo_primario, "gestion": m.gestion,
                            "es_planificada": "sí" if planificada else "no",
                            "veredicto": veredicto})
    tabla_b = pd.DataFrame(filas_b)
    p(f"      {'universo':<10}{'quién':<26}{'abre con':<26}{'tipo':<28}{'gestión':<9}")
    for r in tabla_b.itertuples():
        p(f"      {r.universo:<10}{str(r.nombre)[:24]:<26}{str(r.abre_la_via_C_con)[:24]:<26}"
          f"{str(r.tipo_primario)[:26]:<28}{str(r.gestion):<9}")
    p("")
    p("      VEREDICTOS")
    for v, bloque in tabla_b.groupby("veredicto"):
        p(f"        {v}")
        for r in bloque.itertuples():
            p(f"            {r.universo} · {r.nombre} ({r.abre_la_via_C_con})")
    tabla_b.to_csv(OUT_BARRIDO, index=False, encoding="utf-8")
    p("")
    pierden = tabla_b[tabla_b.veredicto.str.startswith("PIERDE")]
    decidir = tabla_b[tabla_b.veredicto.str.startswith("PARA DECISIÓN")]
    p(f"      NINGUNA fila pierde la vía C automáticamente." if pierden.empty
      else f"      {len(pierden)} pierden la vía C.")
    p("")
    p("      EL CASO QUE QUEDA ABIERTO, y por qué no lo cierro yo:")
    for cual, bloque in decidir.groupby("abre_la_via_C_con"):
        m = bloque.iloc[0]
        donde = ", ".join(f"{r.universo} · {r.nombre}" for r in bloque.itertuples())
        p(f"        «{cual}» — {m.tipo_primario} de gestión {m.gestion}")
        p(f"        abre la vía C en: {donde}")
    p("")
    p("      Tu criterio dice «privada Y planificada». Esto es planificado y NO es privado: es")
    p("      mixto. Por la letra, mantiene la vía C. Por el espíritu —una centralidad comercial")
    p("      construida como desarrollo— sería el caso que quisiste excluir. **Elegir una de las")
    p("      dos lecturas es tomar tu decisión, no aplicarla**, así que queda para vos.")
    p("")
    p("      Y UNA NOTA SOBRE EL MERCADO DEL PROGRESO, que sorprende: el relevamiento lo tipifica")
    p("      como `mercado_barrial_alimentario` de gestión **privada**. Es privado pero NO es")
    p("      planificado —abrió en 1889 y funciona como abasto de barrio—, así que mantiene la")
    p("      vía C sin ambigüedad. Es la prueba de que las dos condiciones hacen falta juntas.")
    p("")

    # ==================================================== TAREA 3 · R22
    p("-" * 100)
    p("  TAREA 3 · R22 VILLA PUEYRREDÓN · la ficha con la debilidad declarada")
    p("")
    fila_r22 = s94[s94.polo_id.str.contains("PUEYRREDON", na=False)]
    if fila_r22.empty:
        p("      no se encontró la fila de Villa Pueyrredón en las 94.")
    else:
        r = fila_r22.iloc[0]
        vias = {"A · densidad y continuidad": r.via_A_abierta,
                "C · mercados y centralidades": r.via_C_abierta,
                "F · corredor": r.via_F_abierta}
        p(f"      {r.polo_id} · {r.nombre_polo}")
        p(f"      {r.n_locales:.0f} locales · {r.ha:.2f} ha")
        p("")
        for k, v in vias.items():
            p(f"        vía {k:<32} {'ABIERTA' if v == 'si' else 'cerrada'}")
        p(f"        vías B, D y E se heredan de la zona {r.zona_via_B}")
        p("")
        abiertas = sum(1 for v in vias.values() if v == "si")
        p(f"      abre {abiertas} vía geométrica. La decisión (d) la publica igual, con la")
        p("      debilidad declarada en la ficha.")
        p("")
        curva = {c.replace("cont_pct_comp_mayor_", ""): orig.loc[
            orig.polo_id == r.polo_id, c].iloc[0]
            for c in orig.columns if c.startswith("cont_pct_comp_mayor_")}
        p("      EL 5,6 % VERIFICADO, Y SU CURVA — la continuidad depende del umbral (R4):")
        p("")
        p("        umbral   " + "".join(f"{k:>9}" for k in curva))
        p("        continua " + "".join(f"{v:>8.1f}%" for v in curva.values()))
        p("")
        p("        El 5,6 % es el umbral de 40 m, que es el que usa el conjunto. Citarlo solo")
        p("        no es incorrecto, pero la ficha gana con la curva: a 120 m la continuidad es")
        p("        del 31,3 %, y esa diferencia es lo que hace que la fila sea discutible.")
        p(f"        Densidad: {orig.loc[orig.polo_id == r.polo_id, 'locales_x_ha'].iloc[0]} "
          f"locales/ha · vecino medio "
          f"{orig.loc[orig.polo_id == r.polo_id, 'vecino_medio_m'].iloc[0]} m")
        texto = (
            "Esta referencia se publica con UNA sola vía abierta —densidad y continuidad— y una "
            "continuidad del 5,6 % medida a 40 metros (2,5 % a 20 m; 31,3 % a 120 m). Es la más "
            "débil del conjunto y se consigna como tal: su inclusión responde a una decisión "
            "editorial de conducción, no a la fuerza de la evidencia. No se compara con "
            "referencias que abren tres o más vías.")
        p("")
        p("      TEXTO PARA LA FICHA:")
        for linea in textwrap.wrap(texto, 88):
            p(f"        {linea}")
        pd.DataFrame([{
            "referencia_id": "R22", "polo_id": r.polo_id, "nombre": r.nombre_polo,
            "n_locales": r.n_locales, "ha": r.ha,
            "vias_geometricas_abiertas": abiertas,
            "continuidad_declarada_pct": 5.6,
            "decision": "se publica con la debilidad declarada (decisión d, 2026-08-08)",
            "texto_para_la_ficha": texto,
        }]).to_csv(OUT_R22, index=False, encoding="utf-8")

        for f in filas_dec:
            if f["n"] == 22:
                f["consecuencia_operativa"] = (
                    f"{r.polo_id} se publica con {abiertas} vía abierta y 5,6 % de continuidad. "
                    "La ficha lleva el texto de debilidad declarada.")
            if f["n"] == 21:
                f["consecuencia_operativa"] = (
                    "Barrido de las 94 filas y las 22 zonas: ninguna pierde la vía C "
                    "automáticamente. Queda para decisión Patio Costanera Norte "
                    "(patio_gastronomico de gestión mixta), que abre R07 y PG009.")
    pd.DataFrame(filas_dec).to_csv(OUT_DEC, index=False, encoding="utf-8")
    p("")

    p("=" * 100)
    p("  SALIDAS")
    for ruta in (OUT_DEC, OUT_BARRIDO, OUT_R22, INFORME):
        p(f"    {ruta.relative_to(ROOT)}")

    texto_final = buffer.getvalue()
    INFORME.write_text(texto_final, encoding="utf-8")
    print(texto_final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
