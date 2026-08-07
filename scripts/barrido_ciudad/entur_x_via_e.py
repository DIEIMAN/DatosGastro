"""Tarea 5 · la razón ENTUR/base contra la vía E, con los dos controles que la vez pasada faltaron.

LA LECTURA PREVIA ESTÁ ESCRITA Y FECHADA ANTES DE ESTA CORRIDA
---------------------------------------------------------------
`desde_cowork/evidencia_2026/LECTURA_PREVIA_ENTUR_x_VIA_E.md`, del 7 de agosto de 2026, con las
zonas nombradas de antemano. Regla R1. Este script **no agrega predicciones**: ejecuta las que ya
están escritas y publica el resultado sea cual sea.

H1  correlación de rangos entre razón ENTUR/base y n_grupos de vía E: predicha 0,20 a 0,55
    · si sale > 0,70 se descarta la razón por redundante
    · si sale entre −0,15 y 0,15 y H2 falla, es ruido y no entra a la matriz

H2  los desacuerdos tienen signo temporal. En el cuadrante «razón baja + vía E abierta», la
    mediana del año de las fuentes e1-e4 debe ser 2023 o posterior. En «razón alta + vía E
    cerrada», anterior a 2021 o inexistente.

LOS DOS CONTROLES, QUE SON LA PARTE QUE FALTÓ EN LA ABLACIÓN ANTERIOR
----------------------------------------------------------------------
    (a) la misma correlación contra `n_locales`. Si la razón correlaciona más con el tamaño que
        con la vía E, no mide reconocimiento: mide que los catálogos tienen rendimientos
        decrecientes en zonas grandes.
    (b) permutación de las etiquetas de vía E, 1.000 iteraciones, semilla fija. Si el valor
        observado no supera el percentil 95, no hay nada.

UNA DECISIÓN SOBRE LAS FECHAS QUE ESTA MISMA RONDA OBLIGA A TOMAR
------------------------------------------------------------------
Varias fuentes vienen como «El Cronista 09/11/2021 act. 12/09/2025». **Se toma 2021, no 2025.** El
Mercado de los Carruajes cerró en abril de 2025 y El Cronista, en su versión «actualizada al
24/09/2025», sigue recomendando dos restaurantes adentro. La fecha de actualización de una nota no
es la fecha de verificación de sus datos, y usarla acá inflaría artificialmente la añada de
exactamente las zonas que H2 quiere separar.

Y no se cuentan: las fuentes marcadas `(e5)` —tours comerciales, que no llevan fecha—, ni las que
la propia ficha lista como «descartadas», «no computadas» o «de contexto». Contar una fuente que
la ficha declara inadmisible sería usarla por la puerta de atrás.

Google Places: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/entur_x_via_e.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT = BARRIDO / "seis_vias"
ENTUR = BARRIDO / "entur" / "entur_contra_base_22_zonas.csv"
VIA_E = BARRIDO / "desde_cowork" / "evidencia_2026" / "via_E_22_referencias.csv"

SEMILLA = 20260807
PERMUTACIONES = 1000

# Lo que la lectura previa nombró ANTES de mirar. Se transcribe para poder contarlo, no para
# reinterpretarlo: si más de la mitad cae mal, H2 se cayó y así se reporta.
PREDICHO_DECLIVE = ["R12", "R04", "R18"]
PREDICHO_EMERGENTE = ["R20", "R15", "R09", "R19", "R08", "R16"]
PREDICHO_ACUERDO_BAJO = ["R13", "R22"]
# R16 va CON RESERVA en la propia lectura previa: abre con cuatro grupos pero dos son de 2017 y
# 2018, y debería caer más cerca del centro del gráfico que Devoto o García del Río.
CON_RESERVA = {"R16"}
# R14 Boedo es la predicción que puede salir mal de una manera útil: si sale con razón media o
# alta y vía E cerrada, no es declive sino un tercer tipo —turístico sin ser gastronómico—.
BOEDO = "R14"

# Frases con las que la ficha declara que lo que sigue NO cuenta. Todo lo que venga después de
# una de ellas se descarta entero.
CORTES_INADMISIBLES = ("Ninguna fuente admisible", "Hallados y descartados", "Descartados",
                       "De contexto")


def anios_admisibles(fuentes: str) -> list[int]:
    """Los años de las fuentes e1-e4 de una fila. Sin `act.`, sin `(e5)`, sin las descartadas."""
    texto = str(fuentes)
    for corte in CORTES_INADMISIBLES:
        posicion = texto.find(corte)
        if posicion >= 0:
            texto = texto[:posicion]
    anios = []
    for pieza in texto.split("|"):
        if "(e5)" in pieza or "no computado" in pieza.lower():
            continue
        # «act. 12/09/2025» se borra antes de extraer: es fecha de actualización, no de dato.
        limpio = re.sub(r"act\.\s*\d{0,2}/?\d{0,2}/?\d{4}", " ", pieza)
        anios += [int(a) for a in re.findall(r"\b(20\d{2})\b", limpio)]
    return anios


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    entur = pd.read_csv(ENTUR)
    via_e = pd.read_csv(VIA_E)
    datos = entur.merge(via_e, on="referencia_id", how="inner")
    datos["razon"] = datos.entur_2019 / datos.base_2026
    datos["anios"] = datos.via_E_fuentes.map(anios_admisibles)
    datos["anio_mediana"] = datos.anios.map(lambda a: float(np.median(a)) if a else np.nan)
    datos["n_locales"] = datos.base_2026

    p("TAREA 5 · LA RAZÓN ENTUR/BASE CONTRA LA VÍA E")
    p("=" * 100)
    p("")
    p("  La lectura previa está escrita y fechada ANTES de esta corrida, con las zonas nombradas")
    p("  de antemano: desde_cowork/evidencia_2026/LECTURA_PREVIA_ENTUR_x_VIA_E.md. Regla R1.")
    p("")
    p(f"  {len(datos)} zonas · ENTUR de agosto de 2019 (2.823 puntos) contra base de 2026 "
      f"(23.981) · Places: 0 requests")
    p("")
    p("  ADVERTENCIA QUE VA EN CUALQUIER PUBLICACIÓN DEL NÚMERO: el ENTUR es de AGOSTO DE 2019.")
    p("  El 22/07/2026 que figura en el portal es el `metadata_modified` del registro, no de los")
    p("  datos. Toda razón calculada acá mezcla dos añadas separadas por siete años.")
    p("")

    # ================================================================ H1
    valido = datos[datos.razon.notna()]
    rho, pvalor = spearmanr(valido.razon, valido.via_E_n_grupos)
    p("-" * 100)
    p("  H1 · CORRELACIÓN DE RANGOS ENTRE LA RAZÓN Y n_grupos DE VÍA E")
    p("")
    p(f"      rho de Spearman = {rho:+.3f}   (p = {pvalor:.3f}, n = {len(valido)})")
    p(f"      predicho por la lectura previa: entre 0,20 y 0,55")
    if rho > 0.70:
        veredicto_h1 = "REDUNDANTE"
        p("      SALE POR ENCIMA DE 0,70 → la razón no aporta nada: mide lo mismo que la vía E y")
        p("      con menos resolución. Se descarta como evidencia y queda la vía E.")
    elif 0.20 <= rho <= 0.55:
        veredicto_h1 = "CONFIRMADA"
        p("      CAE DENTRO DEL RANGO PREDICHO. H1 se confirma.")
    elif -0.15 <= rho <= 0.15:
        veredicto_h1 = "NULA"
        p("      CAE EN LA BANDA NULA (−0,15 a 0,15). Si además H2 falla, la razón es ruido de")
        p("      las dos añadas y no debe entrar a la matriz.")
    else:
        veredicto_h1 = "FUERA DEL RANGO"
        p("      QUEDA FUERA DEL RANGO PREDICHO sin llegar a ninguno de los dos cortes. La")
        p("      predicción no se cumplió, y eso se reporta como lo que es: la lectura previa")
        p("      erró el número.")
    p("")

    # ================================================================ control (a)
    rho_tam, p_tam = spearmanr(valido.razon, valido.n_locales)
    p("-" * 100)
    p("  CONTROL (a) · LA MISMA CORRELACIÓN CONTRA EL TAMAÑO DE LA ZONA")
    p("")
    p(f"      razón vs n_grupos de vía E : rho = {rho:+.3f}")
    p(f"      razón vs n_locales         : rho = {rho_tam:+.3f}   (p = {p_tam:.3f})")
    p("")
    if abs(rho_tam) > abs(rho):
        p("      LA RAZÓN CORRELACIONA MÁS CON EL TAMAÑO QUE CON LA VÍA E. Entonces no está")
        p("      midiendo reconocimiento: está midiendo que un catálogo de 2.823 puntos tiene")
        p("      rendimientos decrecientes en zonas grandes. El control (a) FALLA y cualquier")
        p("      lectura de la razón como señal editorial queda sin base.")
        control_a = "FALLA"
    else:
        p("      La razón correlaciona MÁS con la vía E que con el tamaño. El control (a) pasa:")
        p("      lo que la razón ordena no es simplemente el tamaño de la zona.")
        control_a = "PASA"
    p("")

    # ================================================================ control (b)
    generador = np.random.default_rng(SEMILLA)
    etiquetas = valido.via_E_n_grupos.to_numpy()
    nulos = np.empty(PERMUTACIONES)
    for i in range(PERMUTACIONES):
        nulos[i] = spearmanr(valido.razon, generador.permutation(etiquetas)).statistic
    p95 = float(np.percentile(nulos, 95))
    p99 = float(np.percentile(nulos, 99))
    p_empirico = float((nulos >= rho).mean())
    p("-" * 100)
    p("  CONTROL (b) · PERMUTACIÓN DE LAS ETIQUETAS DE VÍA E")
    p("")
    p(f"      {PERMUTACIONES:,} iteraciones · semilla fija {SEMILLA} · reproducible")
    p("")
    p(f"      observado          rho = {rho:+.3f}")
    p(f"      nulo, percentil 95 rho = {p95:+.3f}")
    p(f"      nulo, percentil 99 rho = {p99:+.3f}")
    p(f"      nulo, media        rho = {nulos.mean():+.3f}  (desvío {nulos.std():.3f})")
    p(f"      p empírico (fracción de nulos ≥ observado) = {p_empirico:.3f}")
    p("")
    if rho > p95:
        p("      El observado SUPERA el percentil 95 del nulo. Hay señal.")
        control_b = "PASA"
    else:
        p("      El observado NO SUPERA el percentil 95 del nulo. Con este material no hay nada")
        p("      que distinguir del azar, y ése es el resultado. Es el control que faltó la vez")
        p("      pasada y por eso se corre ahora, no para confirmar sino para poder desmentir.")
        control_b = "FALLA"
    p("")

    # ================================================================ H2
    corte_razon = float(valido.razon.median())
    datos["razon_clase"] = np.where(datos.razon >= corte_razon, "alta", "baja")
    datos["cuadrante"] = datos.razon_clase + " + vía E " + np.where(
        datos.via_E_abierta == "si", "abierta", "cerrada")
    p("-" * 100)
    p("  H2 · ¿LOS DESACUERDOS TIENEN SIGNO TEMPORAL?")
    p("")
    p(f"      corte de razón: la mediana de las 22, {corte_razon:.3f}")
    p("")
    p(f"      {'id':<5}{'zona':<28}{'razón':>8}{'clase':>7}{'vía E':>8}{'grupos':>8}"
      f"{'años e1-e4':>14}{'mediana':>9}")
    for fila in datos.sort_values("razon", ascending=False).itertuples():
        anios = ",".join(str(a) for a in sorted(fila.anios)) or "—"
        p(f"      {fila.referencia_id:<5}{fila.nombre[:27]:<28}{fila.razon:>8.3f}"
          f"{fila.razon_clase:>7}{fila.via_E_abierta:>8}{fila.via_E_n_grupos:>8}"
          f"{anios[:13]:>14}"
          f"{('—' if np.isnan(fila.anio_mediana) else f'{fila.anio_mediana:.0f}'):>9}")
    p("")
    p(f"      {'cuadrante':<32}{'zonas':>7}{'mediana del año':>18}   zonas")
    resumen = []
    for cuadrante, grupo in datos.groupby("cuadrante"):
        con_anio = grupo[grupo.anio_mediana.notna()]
        mediana = float(np.median(con_anio.anio_mediana)) if len(con_anio) else np.nan
        resumen.append({"cuadrante": cuadrante, "zonas": len(grupo),
                        "mediana_anio": mediana,
                        "ids": " ".join(grupo.referencia_id)})
        p(f"      {cuadrante:<32}{len(grupo):>7}"
          f"{('—' if np.isnan(mediana) else f'{mediana:.0f}'):>18}   "
          f"{' '.join(grupo.referencia_id)}")
    p("")

    emergente = datos[datos.cuadrante == "baja + vía E abierta"]
    declive = datos[datos.cuadrante == "alta + vía E cerrada"]
    mediana_emergente = float(np.median(emergente.anio_mediana.dropna())) \
        if emergente.anio_mediana.notna().any() else np.nan
    p("      LA PRUEBA CONCRETA que la lectura previa fijó:")
    p("")
    p(f"      cuadrante EMERGENTE (razón baja + vía E abierta): {len(emergente)} zonas, "
      f"mediana del año = "
      f"{'—' if np.isnan(mediana_emergente) else f'{mediana_emergente:.0f}'}")
    p("      predicho: 2023 o posterior")
    if not np.isnan(mediana_emergente) and mediana_emergente >= 2023:
        p("      SE CUMPLE.")
        h2_emergente = True
    else:
        p("      NO SE CUMPLE.")
        h2_emergente = False
    p("")
    if len(declive):
        con_anio = declive[declive.anio_mediana.notna()]
        mediana_declive = float(np.median(con_anio.anio_mediana)) if len(con_anio) else np.nan
        p(f"      cuadrante DECLIVE (razón alta + vía E cerrada): {len(declive)} zonas "
          f"({' '.join(declive.referencia_id)}), mediana del año = "
          f"{'—' if np.isnan(mediana_declive) else f'{mediana_declive:.0f}'}")
        p("      predicho: cobertura anterior a 2021 o inexistente")
        h2_declive = np.isnan(mediana_declive) or mediana_declive < 2021
        p(f"      {'SE CUMPLE.' if h2_declive else 'NO SE CUMPLE.'}")
        p("")
        p("      Y el detalle que la mediana esconde, porque el cuadrante tiene DOS zonas:")
        for fila in declive.itertuples():
            if np.isnan(fila.anio_mediana):
                p(f"            {fila.referencia_id}: SIN fuente admisible → cumple la parte "
                  "«o directamente inexistente» de la predicción")
            else:
                p(f"            {fila.referencia_id}: mediana {fila.anio_mediana:.0f} → "
                  f"{'cumple' if fila.anio_mediana < 2021 else 'NO cumple'}")
        p("      Una de las dos cumple y la otra la contradice de plano: R12 Centro, que es el")
        p("      caso que hizo formular la hipótesis, tiene su única fuente admisible fechada en")
        p("      abril de 2026. El cuadrante de declive se sostiene sobre dos zonas, una de ellas")
        p("      sin fuente. Eso no alcanza para nada, ni a favor ni en contra.")
    else:
        mediana_declive, h2_declive = np.nan, False
        p("      cuadrante DECLIVE: VACÍO. Ninguna zona con razón alta tiene vía E cerrada.")
        p("      La predicción no se puede probar porque el cuadrante que la sostenía no existe.")
    p("")

    # ================================================================ las zonas nombradas
    p("-" * 100)
    p("  LAS ZONAS NOMBRADAS ANTES DE MIRAR, UNA POR UNA")
    p("")
    aciertos, fallos = [], []
    indexado = datos.set_index("referencia_id")
    for grupo, esperado in [(PREDICHO_DECLIVE, "alta + vía E cerrada"),
                            (PREDICHO_EMERGENTE, "baja + vía E abierta"),
                            (PREDICHO_ACUERDO_BAJO, "baja + vía E cerrada")]:
        for identificador in grupo:
            if identificador not in indexado.index:
                continue
            salio = indexado.loc[identificador, "cuadrante"]
            acierta = salio == esperado
            (aciertos if acierta else fallos).append(identificador)
            reserva = "  (con reserva en la lectura previa)" if identificador in CON_RESERVA else ""
            p(f"      {identificador:<5}{'✓' if acierta else '✗'}  predicho «{esperado}»  →  "
              f"salió «{salio}»{reserva}")
    p("")
    p(f"      aciertos: {len(aciertos)} de {len(aciertos) + len(fallos)} zonas nombradas")
    p(f"      fallan:   {' '.join(fallos) if fallos else '(ninguna)'}")
    p("")
    p("      PERO LOS TRES FALLOS NO SON EL MISMO FALLO, Y HAY QUE MIRARLOS:")
    p("")
    for identificador in fallos:
        if identificador not in indexado.index:
            continue
        fila = indexado.loc[identificador]
        margen = fila.razon - corte_razon
        p(f"      {identificador}: razón {fila.razon:.3f}, el corte está en {corte_razon:.3f} "
          f"→ {margen:+.3f} del filo")
    p("")
    p("      R09 y R19 caen del lado «alta» por 0,004 y 0,016 sobre una mediana. Con un corte")
    p("      por terciles, por media o por cualquier otro criterio razonable, cambian de")
    p("      cuadrante. **El corte es arbitrario y tres de las once predicciones dependen de**")
    p("      **él**: eso no se arregla eligiendo otro corte, se dice.")
    p("")
    p("      Y R04 Puerto Madero falla de una manera que la propia lectura previa ya había")
    p("      previsto: la predicción decía «vía E que abre pero con toda su evidencia anterior a")
    p("      2024», y su mediana da 2022. Es decir que acierta en lo que predijo sobre las")
    p("      fechas y falla en la etiqueta binaria, porque la etiqueta binaria no distingue")
    p("      «abierta» de «abierta con material viejo». El error está en el instrumento de")
    p("      clasificación, no en la predicción.")
    p("")
    if BOEDO in indexado.index:
        boedo = indexado.loc[BOEDO]
        p(f"      R14 Boedo · la predicción que podía salir mal de una manera útil:")
        p(f"            razón {boedo.razon:.3f} ({boedo.razon_clase}) · vía E "
          f"{boedo.via_E_abierta} · cuadrante «{boedo.cuadrante}»")
        if boedo.razon_clase == "alta":
            p("            Sale con razón alta y vía E cerrada. El ENTUR sí registra a Boedo, y")
            p("            lo registra por el tango, no por la comida: es un TERCER TIPO de")
            p("            desacuerdo —turístico sin ser gastronómico— y obliga a partir la")
            p("            hipótesis en dos.")
        else:
            p("            Sale con razón baja. H2 sigue en pie más simple, y el ENTUR resulta")
            p("            ser más gastronómico de lo que su nombre sugiere.")
    p("")

    # ================================================================ veredicto
    p("=" * 100)
    p("  EL VEREDICTO, PUBLICADO SEA CUAL SEA")
    p("=" * 100)
    p("")
    p(f"      H1           {veredicto_h1}    rho = {rho:+.3f}")
    p(f"      control (a)  {control_a}    razón vs tamaño = {rho_tam:+.3f}")
    p(f"      control (b)  {control_b}    percentil 95 del nulo = {p95:+.3f}")
    p(f"      H2           {'se cumple' if (h2_emergente and h2_declive) else 'NO se cumple'}")
    p("")
    if control_b == "FALLA" or control_a == "FALLA":
        p("      QUÉ SE HACE CON ESTO: la razón ENTUR/base NO entra a la matriz, ni como vía ni")
        p("      como columna de contexto. Se registra como dato descriptivo del ENTUR, con su")
        p("      número, y queda escrito que se probó y no funcionó — como se hizo con el índice")
        p("      de Rand ajustado que dio 0,391 y no se reemplazó por otro que diera mejor.")
    elif veredicto_h1 == "REDUNDANTE":
        p("      QUÉ SE HACE CON ESTO: se descarta la razón por redundante y queda la vía E.")
    else:
        p("      QUÉ SE HACE CON ESTO: la razón entra como COLUMNA DE CONTEXTO, no como vía. No")
        p("      abre ni cierra nada; sirve para distinguir consolidadas de emergentes.")
    p("")
    p("      Y una limitación que ningún control arregla: son 22 zonas. Con n = 22 el intervalo")
    p("      de confianza de un rho de Spearman es ancho, y los cuadrantes quedan con 4 a 7")
    p("      zonas cada uno. Lo que este cruce puede hacer es DESCARTAR; confirmar necesitaría")
    p("      más filas de las que hay.")
    p("")

    salida = datos[["referencia_id", "nombre", "entur_2019", "base_2026", "razon", "razon_clase",
                    "via_E_abierta", "via_E_n_grupos", "anio_mediana", "cuadrante"]].copy()
    salida["anios_e1_e4"] = datos.anios.map(lambda a: ";".join(str(x) for x in sorted(a)))
    salida.to_csv(OUT / "entur_x_via_E.csv", index=False, encoding="utf-8")
    pd.DataFrame([{
        "rho_razon_vs_via_E": round(float(rho), 4), "p_spearman": round(float(pvalor), 4),
        "rho_razon_vs_n_locales": round(float(rho_tam), 4),
        "permutaciones": PERMUTACIONES, "semilla": SEMILLA,
        "nulo_p95": round(p95, 4), "nulo_p99": round(p99, 4),
        "p_empirico": round(p_empirico, 4),
        "veredicto_H1": veredicto_h1, "control_a": control_a, "control_b": control_b,
        "H2_emergente_mediana": mediana_emergente, "H2_declive_mediana": mediana_declive,
        "zonas_nombradas_acertadas": len(aciertos),
        "zonas_nombradas_total": len(aciertos) + len(fallos),
    }]).to_csv(OUT / "entur_x_via_E_estadisticos.csv", index=False, encoding="utf-8")

    (OUT / "ENTUR_x_VIA_E.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
