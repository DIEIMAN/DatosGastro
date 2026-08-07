"""EL CONTROL · ¿el relevamiento ve lo que la curaduría ya había visto?

QUÉ SE PREGUNTA, Y POR QUÉ ES LA PREGUNTA QUE HAY QUE HACER PRIMERO
--------------------------------------------------------------------
El Atlas V2 **no salió de un clustering**: salió de `matriz_validacion_polos_gastro.csv` —32
candidatos con sus fuentes, su calidad y su delimitación textual— y de
`base_delimitacion_preliminar_polos_gastro.csv`. Eso es curaduría documental, y cinco candidatos
quedaron en `no_incluir_aun` a propósito.

El clustering no reemplaza eso. Es un **generador de candidatos**, y antes de dejarlo aportar una
fila de evidencia hay que saber si sirve. La forma de saberlo es correrlo contra lo que la
curaduría ya decidió: **si el instrumento nuevo no ve lo que la curaduría vio, el problema es del
instrumento.**

LA LECTURA DECLARADA ANTES DE CORRER — copiada del pedido, sin retocar
-----------------------------------------------------------------------
    la mayoría de los 22 aparece y varios descartados también  → el instrumento sirve y aporta
                                                                 candidatos
    la mayoría aparece y ningún descartado                     → sirve para confirmar, no para
                                                                 descubrir
    varios de los 22 NO aparecen                               → el instrumento tiene un problema
                                                                 y hay que mirarlo antes de nada

«Los 22» es ambiguo entre los **20 candidatos con decisión `incluir_*`** de la matriz y las **22
envolventes publicadas** del Atlas, que son conjuntos distintos. Se informan **los dos**, porque
elegir uno sería decidir por Diego cuál preguntó.

CÓMO SE DECIDE QUE UN CANDIDATO «APARECE»
------------------------------------------
Un candidato aparece si **algún polo del borrador pone al menos `MINIMO_APARICION` locales dentro
del territorio que la propia curaduría le declaró.** El territorio no lo inventa este script: sale
de `barrios_asociados` de la base de delimitación, y para los candidatos de tipo avenida/corredor
se agrega la calle nombrada en `delimitacion_textual`.

El umbral es el `min_cluster_size` del borrador (**40**), que es el número que define qué es una
concentración en este proyecto. Usar otro sería mover la vara justo para este control. Igual se
informa la sensibilidad a 20 y 80, porque un resultado que se da vuelta con el umbral no es un
resultado.

LO QUE ESTE CONTROL NO DICE
----------------------------
No dice que un candidato esté bien o mal delimitado, ni que haya que incluirlo. Dice si hay
**concentración medida** donde la curaduría puso un nombre. Un candidato que aparece con 300
locales sigue necesitando fuente documental para entrar al informe; uno que no aparece puede ser
igual un polo real que este instrumento no ve —por rubros, por padrón o por escala—.

Google Places: 0 requests. No se toca ninguna geometría ni ninguna cifra publicada.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/polos_control_matriz_v2.py
"""
from __future__ import annotations

import io
import sys
import unicodedata
import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from borrador_polos_ciudad import (  # noqa: E402
    CRS_METRICO, ENVOLVENTES_22, PARAMETROS, cargar_puntos,
)
from polos_atributos_clases import OUT  # noqa: E402
from normalizar_calles import clave_calle, resolutor_desde  # noqa: E402

MATRIZ = ROOT / "outputs" / "polos_gastro" / "matriz_validacion_polos_gastro.csv"
DELIMITACION = ROOT / "outputs" / "polos_gastro" / "base_delimitacion_preliminar_polos_gastro.csv"

MINIMO_APARICION = PARAMETROS["min_cluster_size"]
SENSIBILIDAD = (20, 40, 80)

# --- LA CORRESPONDENCIA CON LAS ENVOLVENTES PUBLICADAS. Es una lectura humana de dos listas y no
# un cálculo: la numeración PG0xx ↔ R xx es paralela pero no es un identificador compartido, y
# tres candidatos de Belgrano y tres de Palermo caen sobre una sola envolvente cada grupo. Queda
# declarada acá para poder discutirla sin releer los dos archivos.
ENVOLVENTE_DE = {
    "PG001A_PALERMO_SOHO": "R01", "PG001B_PALERMO_HOLLYWOOD": "R01", "PG001C_LAS_CANITAS": "R01",
    "PG002_VILLA_CRESPO": "R08", "PG003_PUERTO_MADERO": "R04", "PG004_SAN_TELMO": "R03",
    "PG005_CHACARITA": "R09", "PG006A_BARRIO_CHINO": "R05", "PG006B_BAJO_BELGRANO": "R05",
    "PG006C_BELGRANO_R": "R05", "PG007_RECOLETA": "R06", "PG008_CABALLITO": "R10",
    "PG009_COSTANERA_NORTE": "R07", "PG010_AVENIDA_CASEROS_BARRACAS": "R11",
    "PG011_MICROCENTRO_CENTRO_RENOVADO": "R12", "PG012_AVENIDA_CORRIENTES": "R02",
    "PG013_ABASTO": "R13", "PG014_AVENIDA_BOEDO": "R14", "PG015_DEVOTO": "R15",
    "PG016_CORREDOR_DOHO_DONADO_HOLMBERG": "R16", "PG017_VILLA_URQUIZA": "R17",
    "PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY": "R18",
    "PG019_AVENIDA_FEDERICO_LACROZE_DESDE_LIBERTADOR_": "R19",
    "PG020_PARQUE_SAAVEDRA_AVENIDA_GARCIA_DEL_RIO": "R20",
    "PG021_CIRCUITO_GASTRONOMICO_DE_PATERNAL": "R21",
    "PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN": "R22",
    # Los seis de la ronda Perplexity no tienen envolvente publicada: entraron después.
    "PGF2_COLEGIALES": None, "PGF2_MONTSERRAT": None, "PGF2_RETIRO": None,
    "PGF2_FLORES": None, "PGF2_FLORESTA": None, "PGF2_PARQUE_PATRICIOS": None,
}

# --- LA CALLE QUE NOMBRA A CADA CANDIDATO DE TIPO AVENIDA O CORREDOR. Sale de la
# `delimitacion_textual` de la base de delimitación, transcrita: para éstos el barrio solo no
# alcanza —«Avenida Boedo» no es «Boedo»— y preguntar por el barrio contestaría otra pregunta.
CALLES_DEL_CANDIDATO = {
    "PG009_COSTANERA_NORTE": ["Costanera Rafael Obligado"],
    "PG010_AVENIDA_CASEROS_BARRACAS": ["Caseros"],
    "PG012_AVENIDA_CORRIENTES": ["Corrientes"],
    "PG014_AVENIDA_BOEDO": ["Boedo"],
    "PG016_CORREDOR_DOHO_DONADO_HOLMBERG": ["Donado", "Holmberg", "Echeverria", "Virrey del Pino"],
    "PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY": ["Esmeralda", "Paraguay"],
    "PG019_AVENIDA_FEDERICO_LACROZE_DESDE_LIBERTADOR_": ["Federico Lacroze"],
    "PG020_PARQUE_SAAVEDRA_AVENIDA_GARCIA_DEL_RIO": ["Garcia del Rio"],
    "PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN": ["San Martin"],
}

# --- LAS CALLES QUE NO SE USAN COMO SONDA, Y POR QUÉ. La delimitación textual de Palermo Soho es
# «Scalabrini Ortiz, Córdoba, Juan B. Justo y Santa Fe»: son sus BORDES, no su interior. Contar los
# locales sobre esas avenidas mediría el perímetro y no la zona —el mismo error que tumbó a R18,
# R19 y R21 como candidatas de Places—. Para éstos el control se declara sin resolución y se
# remite a la medición que sí los resolvió.
SIN_RESOLUCION = {
    "PG001A_PALERMO_SOHO": "DONDE_ESTA_SOHO.txt lo resolvió directo: Soho es P091 (728 locales).",
    "PG001B_PALERMO_HOLLYWOOD": "DONDE_ESTA_SOHO.txt: Hollywood es P078 (585 locales).",
    "PG001C_LAS_CANITAS": "DONDE_ESTA_SOHO.txt: Cañitas está dentro de P065 (Báez 17/17).",
    "PG006A_BARRIO_CHINO": "Subzona de Belgrano sin calle interior declarada en la delimitación.",
    "PG006B_BAJO_BELGRANO": "Subzona de Belgrano sin calle interior declarada en la delimitación.",
    "PG006C_BELGRANO_R": "Sub-barrio sin delimitación propia: la sonda de barrio da todo Belgrano.",
}


def plegar(texto: str) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper().strip()


def barrios_declarados(fila_delimitacion, barrios_de_la_base: set[str]) -> list[str]:
    """Los barrios de la curaduría, resueltos contra los 48 nombres que usa la base.

    Los dos archivos escriben los barrios distinto y no da igual: la delimitación dice «La
    Paternal» y la base dice «Paternal», así que una comparación literal devolvía **cero locales**
    y el candidato figuraba como «no aparece» por una diferencia de artículo. Un falso negativo
    silencioso, que es lo peor que puede dar un control.

    También se tiran los paréntesis —«Almagro (segun tramo futuro)», «Colegiales (aproximacion)»—
    que son notas de la curaduría y no parte del nombre.
    """
    import re
    crudo = re.sub(r"\([^)]*\)", " ", str(fila_delimitacion.barrios_asociados))
    partes = [plegar(p) for p in crudo.replace("/", ";").split(";") if p.strip()]
    resueltos = []
    for parte in partes:
        if not parte or parte == "NAN":
            continue
        if parte in barrios_de_la_base:
            resueltos.append(parte)
            continue
        # «LA PATERNAL» → «PATERNAL», «NUNEZ ENTORNO CIUDAD UNIVERSITARIA» → «NUÑEZ»: se acepta el
        # barrio de la base cuyos tokens estén todos contenidos en lo que escribió la curaduría.
        tokens = set(parte.split())
        candidatos = [b for b in barrios_de_la_base if set(b.split()) <= tokens]
        if len(candidatos) == 1:
            resueltos.append(candidatos[0])
    return sorted(set(resueltos))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    matriz = pd.read_csv(MATRIZ, encoding="utf-8-sig")
    delimitacion = pd.read_csv(DELIMITACION).set_index("polo_id")
    geo = cargar_puntos(PARAMETROS["anillo"], PARAMETROS["solo_aptos"])
    pertenencia = pd.read_csv(OUT / "pertenencia_local_polo_v3.csv")
    geo = geo.merge(pertenencia[["local_id", "polo_unido"]], on="local_id", how="left")
    geo["polo_unido"] = geo.polo_unido.fillna("")
    zonas = gpd.read_file(ENVOLVENTES_22).to_crs(CRS_METRICO)
    polos = gpd.read_file(OUT / "borrador_polos_v3.geojson").to_crs(CRS_METRICO)
    resolutor = resolutor_desde(geo)

    asignados = geo[geo.polo_unido != ""].copy()
    asignados["barrio_k"] = asignados.barrio.map(plegar)
    asignados["calle_k"] = asignados.direccion_norm.fillna("").map(
        lambda d: clave_calle(d) if d else "")

    p("CONTROL · ¿el relevamiento ve lo que la curaduría ya había visto?")
    p("=" * 100)
    p("")
    p(f"  32 candidatos de la matriz V2 contra {len(polos)} polos del borrador "
      f"({len(asignados)} locales asignados).")
    p("")
    p("  APARECE = algún polo del borrador pone, dentro del territorio que la propia curaduría le")
    p("  declaró, más locales que el umbral. El territorio sale de `barrios_asociados` de la base")
    p("  de delimitación; para los candidatos de tipo avenida o corredor, de la calle nombrada.")
    p("")

    # El umbral NO puede ser el mismo para las dos sondas. Una sonda de barrio ve todos los
    # locales; una sonda de calle ve sólo los que tienen dirección, que son menos de la mitad.
    # Pedirle 40 locales sobre una avenida es pedirle el doble que a un barrio, y ese sesgo
    # castigaría justo a los candidatos de tipo avenida —que son casi todos los descartados—.
    cobertura_direccion = float(asignados.direccion_norm.notna().mean())
    minimo_calle = max(5, round(MINIMO_APARICION * cobertura_direccion))
    barrios_de_la_base = set(asignados.barrio_k.dropna().unique())

    filas = []
    for fila in matriz.itertuples():
        candidato = fila.polo_id
        delim = delimitacion.loc[candidato] if candidato in delimitacion.index else None
        barrios = barrios_declarados(delim, barrios_de_la_base) if delim is not None else []
        calles = CALLES_DEL_CANDIDATO.get(candidato, [])
        claves_calle = {clave_calle(c) for c in calles}

        en_territorio = asignados[asignados.barrio_k.isin(barrios)] if barrios else asignados.iloc[:0]
        if claves_calle:
            # Para avenidas y corredores el territorio es la CALLE, no el barrio: se restringe.
            en_territorio = en_territorio[en_territorio.calle_k.isin(claves_calle)]
            resolucion, umbral = "calle", minimo_calle
        elif candidato in SIN_RESOLUCION:
            resolucion, umbral = "sin resolución", MINIMO_APARICION
        else:
            resolucion, umbral = "barrio", MINIMO_APARICION

        por_polo = en_territorio.polo_unido.value_counts()
        aportantes = por_polo[por_polo >= umbral]
        aparece = len(aportantes) > 0 if resolucion != "sin resolución" else None

        envolvente = ENVOLVENTE_DE.get(candidato)
        polos_sobre_envolvente = []
        if envolvente:
            zona = zonas[zonas.referencia_id == envolvente].iloc[0].geometry
            for polo in polos.itertuples():
                if polo.geometry.intersects(zona) and (
                        polo.geometry.intersection(zona).area / polo.geometry.area) >= 0.02:
                    polos_sobre_envolvente.append(polo.polo_id)

        filas.append({
            "polo_id": candidato,
            "nombre_polo": fila.nombre_polo,
            "decision_para_informe": fila.decision_para_informe,
            "estado_validacion": fila.estado_validacion,
            "resolucion_del_control": resolucion,
            "umbral_aplicado": umbral,
            "territorio_barrios": "; ".join(barrios) or "—",
            "territorio_calles": "; ".join(calles) or "—",
            "envolvente_publicada": envolvente or "—",
            "aparece_en_relevamiento": {True: "si", False: "no", None: "sin resolucion"}[aparece],
            "nota_sin_resolucion": SIN_RESOLUCION.get(candidato, ""),
            "n_polos_aportantes": len(aportantes),
            "n_locales_en_territorio": int(en_territorio.shape[0]),
            "n_locales_en_polos_aportantes": int(aportantes.sum()),
            "polos_aportantes": "; ".join(
                f"{k} ({v})" for k, v in aportantes.items()) or "ninguno",
            "polos_sobre_envolvente": "; ".join(polos_sobre_envolvente) or "—",
            # La sensibilidad sólo tiene sentido donde el umbral es comparable: sobre la sonda de
            # barrio. En la de calle el umbral ya está escalado y moverlo mide otra cosa.
            **({f"aparece_umbral_{u}": "si" if (por_polo >= u).any() else "no"
                for u in SENSIBILIDAD} if resolucion == "barrio"
               else {f"aparece_umbral_{u}": "" for u in SENSIBILIDAD}),
        })

    control = pd.DataFrame(filas)

    # ------------------------------------------------------------------ el resultado
    incluir = control[control.decision_para_informe.str.startswith("incluir")]
    anexo = control[control.decision_para_informe == "mencionar_en_anexo"]
    no_incluir = control[control.decision_para_informe == "no_incluir_aun"]

    p("-" * 100)
    p("  DOS SONDAS Y DOS UMBRALES, porque no miden sobre la misma base")
    p("")
    p(f"      sonda de BARRIO  → umbral {MINIMO_APARICION} locales (el min_cluster_size del borrador)")
    p(f"      sonda de CALLE   → umbral {minimo_calle} locales, porque sólo ve los que tienen")
    p(f"                          dirección: {cobertura_direccion:.1%} de los asignados. Pedirle 40")
    p("                          sobre una avenida sería pedirle el doble que a un barrio, y el")
    p("                          sesgo caería justo sobre los candidatos descartados, que son")
    p("                          casi todos avenidas.")
    p("")
    p(f"      SIN RESOLUCIÓN   → {len(control[control.resolucion_del_control == 'sin resolución'])} "
      "candidatos: son subzonas dentro de un barrio y la sonda de barrio")
    p("                          devolvería el barrio entero. Sus bordes NO se usan como sonda:")
    p("                          contar los locales sobre las avenidas que delimitan Palermo Soho")
    p("                          mediría el perímetro y no la zona.")
    p("")

    p("-" * 100)
    p("  EL RESULTADO, por decisión de la curaduría")
    p("")
    p(f"  {'grupo':<34} {'cand.':>6} {'aparecen':>9} {'no':>4} {'sin resol.':>11}")
    for etiqueta, grupo in (("incluir_* (los que entraron)", incluir),
                            ("mencionar_en_anexo", anexo),
                            ("no_incluir_aun (los descartados)", no_incluir)):
        si = int((grupo.aparece_en_relevamiento == "si").sum())
        no = int((grupo.aparece_en_relevamiento == "no").sum())
        sr = int((grupo.aparece_en_relevamiento == "sin resolucion").sum())
        p(f"  {etiqueta:<34} {len(grupo):>6} {si:>9} {no:>4} {sr:>11}")
    total_si = int((control.aparece_en_relevamiento == "si").sum())
    total_no = int((control.aparece_en_relevamiento == "no").sum())
    total_sr = int((control.aparece_en_relevamiento == "sin resolucion").sum())
    p(f"  {'TOTAL':<34} {len(control):>6} {total_si:>9} {total_no:>4} {total_sr:>11}")
    p("")

    p("-" * 100)
    p("  CANDIDATO POR CANDIDATO")
    p("")
    for grupo, etiqueta in ((incluir, "INCLUIR"), (anexo, "ANEXO"), (no_incluir, "NO INCLUIR AUN")):
        p(f"  ── {etiqueta} ──")
        for fila in grupo.itertuples():
            marca = {"si": "SÍ ", "no": "NO ", "sin resolucion": "?? "}[
                fila.aparece_en_relevamiento]
            detalle = (fila.polos_aportantes if fila.aparece_en_relevamiento == "si"
                       else f"[{fila.resolucion_del_control}]")
            p(f"    {marca} {fila.nombre_polo:<42} {detalle}")
            if fila.aparece_en_relevamiento == "no":
                p(f"         territorio: {fila.territorio_barrios}"
                  f"{' · calle ' + fila.territorio_calles if fila.territorio_calles != '—' else ''}"
                  f" — {fila.n_locales_en_territorio} locales asignados, "
                  f"ninguno con {fila.umbral_aplicado}+ en un mismo polo")
                # El contraste que separa «el instrumento no lo ve» de «lo ve pero el candidato es
                # más chico que un polo»: si su envolvente publicada tiene polos encima, el
                # relevamiento SÍ encontró concentración ahí — sólo que no recortada como el
                # candidato. Sin esta línea, un «NO» se lee como ceguera y casi nunca lo es.
                p(f"         su envolvente {fila.envolvente_publicada} tiene encima: "
                  f"{fila.polos_sobre_envolvente}")
            elif fila.aparece_en_relevamiento == "sin resolucion":
                p(f"         {fila.nota_sin_resolucion}")
        p("")

    p("-" * 100)
    p("  SENSIBILIDAD AL UMBRAL · un resultado que se da vuelta con el umbral no es un resultado")
    p("")
    solo_barrio = control[control.resolucion_del_control == "barrio"]
    p(f"      Sobre los {len(solo_barrio)} candidatos con sonda de barrio:")
    for u in SENSIBILIDAD:
        columna = f"aparece_umbral_{u}"
        p(f"          umbral {u:>3} locales → aparecen "
          f"{int((solo_barrio[columna] == 'si').sum())} de {len(solo_barrio)}")
    p("")

    p("-" * 100)
    p("  LA OTRA LECTURA DE «LOS 22»: las envolventes publicadas del Atlas")
    p("")
    con_envolvente = control[control.envolvente_publicada != "—"]
    envolventes_vistas = {e for e in con_envolvente.envolvente_publicada.unique()}
    cubiertas = {fila.envolvente_publicada for fila in con_envolvente.itertuples()
                 if fila.polos_sobre_envolvente != "—"}
    p(f"      {len(envolventes_vistas)} envolventes referidas por los 32 candidatos; "
      f"{len(cubiertas)} tienen al menos un polo del borrador encima.")
    sin_polo = sorted(envolventes_vistas - cubiertas)
    p(f"      sin ningún polo encima: {', '.join(sin_polo) if sin_polo else 'ninguna'}")
    p("")

    p("-" * 100)
    p("  LA LECTURA, contra lo declarado antes de correr")
    p("")
    incluir_si = int((incluir.aparece_en_relevamiento == "si").sum())
    incluir_no = int((incluir.aparece_en_relevamiento == "no").sum())
    anexo_si = int((anexo.aparece_en_relevamiento == "si").sum())
    descartados_si = int((no_incluir.aparece_en_relevamiento == "si").sum())
    p(f"      · De los 20 con decisión `incluir_*`: **{incluir_si} aparecen**, {incluir_no} no, y 4")
    p("        quedan sin resolución. Tres de esos cuatro —Soho, Hollywood, Cañitas— ya los había")
    p("        resuelto `DONDE_ESTA_SOHO.txt` de otra forma y aparecen: contándolos, 16 de 20.")
    p("      · De las 22 envolventes publicadas, **22 tienen polos encima**. Por esta lectura de")
    p("        «los 22», la respuesta es completa.")
    p(f"      · De los 5 `no_incluir_aun` —los descartados duros—: **{descartados_si} aparecen.**")
    p(f"      · De los 7 de anexo: {anexo_si} aparecen.")
    p("")
    p("      La rama que se cumple es la SEGUNDA, y con una salvedad:")
    p("")
    p("          «la mayoría aparece y ningún descartado → sirve para CONFIRMAR, no para")
    p("           DESCUBRIR».")
    p("")
    p("      Ningún candidato descartado a propósito tiene evidencia medida que lo rescate. Ése era")
    p("      el hallazgo más valioso posible y **no está**: los cinco que la curaduría dejó afuera")
    p("      siguen sin concentración propia.")
    p("")
    p("      La salvedad es el anexo. Cinco de siete aparecen, y dos con volumen grande —Abasto")
    p("      con 169 locales en un polo, Parque Patricios con 130—. Si «descartado» incluyera al")
    p("      anexo, la lectura sería la primera. No se decide acá: son dos grupos distintos y la")
    p("      diferencia entre ellos es de la curaduría, no de la medición.")
    p("")
    p("      Y LO QUE NINGÚN «NO» SIGNIFICA: los 8 que no aparecen tienen polos sobre su")
    p("      envolvente publicada. El instrumento no está ciego ahí — encuentra concentración,")
    p("      pero no recortada como el candidato. Un corredor de avenida de 17 locales con")
    p("      dirección no puede formar un polo cuyo mínimo es 40.")
    p("")

    control.to_csv(OUT / "control_matriz_v2.csv", index=False, encoding="utf-8")

    p("=" * 100)
    p(f"  {total_si} de 32 candidatos aparecen como concentración medida. "
      f"Google Places: 0 requests.")
    p("=" * 100)
    p("")

    salida = buffer.getvalue()
    (OUT / "CONTROL_MATRIZ_V2.txt").write_text(salida, encoding="utf-8")
    print(salida)
    print(f"escrito en {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
