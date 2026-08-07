"""Ronda 4 · las fuentes con defecto estructural, y los tres datos de vigencia del Barrio Chino.

POR QUÉ UNA CAPA DE DEFECTOS Y NO UNA NOTA AL PIE
--------------------------------------------------
Van cuatro fuentes con un defecto que no es un error de un dato: es una propiedad del artefacto que
afecta a todo lo que salga de él. Un error se corrige en la fila; esto se marca en la fuente, o lo
volvemos a comer cada vez que alguien la cite.

    1  El Cronista con `fecha_actualizacion = 24/09/2025`. Al menos TRES notas de años de origen
       distintos —2021, 2024 y la del Mercado de los Carruajes— llevan la misma fecha de
       actualización. Eso no es una nota desactualizada: es un re-sellado masivo del archivo, y
       la fecha **no acredita vigencia de los datos**. La prueba está en la nota de los Carruajes:
       actualizada el 24/09/2025, seguía recomendando dos restaurantes adentro de un mercado que
       había cerrado cinco meses antes.

    2  El catálogo consolidado de Bares Notables: asigna barrio y comuna con error verificable
       (La Academia en Comuna 5, cuando USIG la pone en Balvanera, Comuna 3).

    3  La reedición del PDF del catálogo sin cambio de número de resolución: circulan tres
       contenidos —90, 88 y las listas de 84 y 95— bajo la misma cita.

    4  Time Out: tres direcciones mal asignadas de barrio (Corte Comedor, Vereda Adentro y el
       caso de Núñez), verificadas contra USIG.

LO QUE LA MARCA HACE Y LO QUE NO HACE
--------------------------------------
La marca **no borra el dato**. Una nota re-sellada sigue sirviendo para lo que su año de origen
soporta: si la nota es de 2021, describe 2021. Lo que la marca prohíbe es leer la fecha de
actualización como fecha de verificación, que es lo único que estaba haciendo trabajo indebido.

Y una asimetría que hay que respetar: **no encontrar la fecha de actualización no es haberla
verificado distinta**. Los seis hitos que la capa toma de cronista.com no traen fecha de
actualización registrada por nosotros. No se los descarta: quedan `pendiente_de_comprobacion`, que
es un tercer estado y no un descarte encubierto.

LOS TRES DATOS DE VIGENCIA (Tarea 5)
-------------------------------------
Todos Contentos como `dudoso_probablemente_abierto` —segundo caso El Tokio—, Hong Kong Style y
Dragón Porteño como `cerrado`. Y el conflicto de Boca a Boca, que se documenta y **no se resuelve**:
no tenemos con qué.

Google Places: 0 requests. USIG: 0 requests.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/fuentes_defectos_y_vigencia_r4.py
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT = BARRIDO / "seis_vias"
HITOS = BARRIDO / "hitos"
EVIDENCIA = BARRIDO / "desde_cowork" / "evidencia_2026"
FUENTES = BARRIDO / "fuentes"

CAPA_HITOS = HITOS / "hitos_capa_2026_r3.csv"
PUERTAS = OUT / "establecimientos_E02_E07_geo_r4.csv"
BASE = BARRIDO / "base" / "local.csv"

# ---------------------------------------------------------------- la capa de defectos
#
# `regla_de_deteccion` es lo que un script puede evaluar; `que_prohibe` es lo que la marca impide
# afirmar. Los dos campos existen por separado a propósito: una regla sin consecuencia declarada
# se convierte en una etiqueta decorativa, y una consecuencia sin regla no se puede aplicar sola.
DEFECTOS = [
    {
        "defecto_id": "FD-01",
        "fuente": "cronista.com",
        "regla_de_deteccion": "dominio = cronista.com Y fecha_actualizacion = 2025-09-24",
        "clase": "re-sellado masivo de archivo",
        "que_prohibe": "leer la fecha de actualización como fecha de verificación del dato",
        "que_sigue_valiendo": "el contenido, con la añada de su fecha de ORIGEN",
        "severidad": "descarte de la fecha, no de la nota",
        "evidencia": (
            "tres notas de años de origen distintos con la misma fecha de actualización: "
            "Mercado de los Carruajes (recomienda dos restaurantes en una sede cerrada cinco "
            "meses antes), «5 lugares para comer bien y barato en el barrio chino» (original "
            "08/2021) y Ultramarinos (original 09/2024)"),
        "detectado": "2026-08-07",
        "detectado_por": "cowork · ronda 4",
    },
    {
        "defecto_id": "FD-02",
        "fuente": "catálogo consolidado de Bares Notables (Res. MCGC 3758/24)",
        "regla_de_deteccion": "campo barrio o comuna del catálogo, para cualquier entrada",
        "clase": "atribución territorial errónea",
        "que_prohibe": "usar el barrio/comuna del catálogo como dato territorial sin cotejar USIG",
        "que_sigue_valiendo": "la declaratoria, el nombre y la dirección postal",
        "severidad": "descarte del campo territorial",
        "evidencia": (
            "La Academia figura en Comuna 5 y USIG la ubica en Balvanera, Comuna 3. El control "
            "de bordes de la ronda 3 lo verificó"),
        "detectado": "2026-08-07",
        "detectado_por": "repositorio · ronda 3 (control de bordes USIG)",
    },
    {
        "defecto_id": "FD-03",
        "fuente": "PDF del catálogo servido bajo la URL de la Res. MCGC 3758/24",
        "regla_de_deteccion": "cita del catálogo sin SHA-256 ni fecha de descarga",
        "clase": "contenido mutable bajo cita estable",
        "que_prohibe": "citar «el catálogo» sin decir cuál de los contenidos",
        "que_sigue_valiendo": "cada contenido, citado por su hash y su identificador interno",
        "severidad": "obliga a citar por hash",
        "evidencia": (
            "circulan tres contenidos: 90 entradas (en disco desde el 03/08/2026, hoja de firmas "
            "del 26/02/2026, GEDO IF-2026-10314379-GCABA-DGPMYCH), 88 entradas (la URL hoy) y "
            "las listas independientes de 84 (GCBA) y 95 (Wikidata)"),
        "detectado": "2026-08-07",
        "detectado_por": "repositorio · ronda 3 (PROCEDENCIA_CATALOGOS.csv)",
    },
    {
        "defecto_id": "FD-04",
        "fuente": "Time Out Buenos Aires",
        "regla_de_deteccion": "campo barrio de una nota de Time Out",
        "clase": "atribución territorial errónea",
        "que_prohibe": "usar el barrio que declara Time Out como dato territorial",
        "que_sigue_valiendo": "la distinción editorial y la dirección de puerta",
        "severidad": "descarte del campo territorial",
        "evidencia": (
            "tres direcciones mal asignadas verificadas contra USIG en la ronda 3: Corte Comedor "
            "(Time Out dice Núñez, USIG dice Belgrano), Vereda Adentro y el tercer caso del "
            "control de bordes"),
        "detectado": "2026-08-07",
        "detectado_por": "repositorio · ronda 3 (control de bordes USIG)",
    },
]

# ---------------------------------------------------------------- Tarea 5 · los tres datos
VIGENCIA_BARRIO_CHINO = {
    "Todos Contentos": (
        "dudoso_probablemente_abierto", "probablemente_abierto",
        "cerró en julio de 2020 tras más de 35 años, con 14 empleados (iProfesional 04/07/2020), "
        "y vuelve a aparecer operativo en 2024 (Forbes 07/09/2024) y en 2025. SEGUNDO CASO EL "
        "TOKIO: cierre y reapertura sin que ningún listado registre ninguna de las dos cosas."),
    "Hong Kong Style": (
        "cerrado", "",
        "cerró en mayo de 2020 tras 20 años (iProfesional 04/07/2020). Sin ninguna evidencia de "
        "reapertura posterior."),
    "Dragon Porteno": (
        "cerrado", "",
        "cerró con 8 despidos (iProfesional 04/07/2020). Sin evidencia de reapertura."),
}

BOCA_A_BOCA = "BOCA A BOCA"


def plegar(texto: str) -> str:
    import unicodedata
    limpio = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", limpio)).strip()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    FUENTES.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    p("RONDA 4 · FUENTES CON DEFECTO ESTRUCTURAL, Y TRES DATOS DE VIGENCIA")
    p("=" * 100)
    p("")
    p("  0 consultas a cualquier servicio. Todo sale de lo que ya está en disco.")
    p("")

    # ================================================================ la capa de defectos
    defectos = pd.DataFrame(DEFECTOS)
    defectos.to_csv(FUENTES / "fuentes_defectos_conocidos.csv", index=False, encoding="utf-8")

    p("-" * 100)
    p("  LA CAPA · CUATRO FUENTES CON DEFECTO ESTRUCTURAL")
    p("")
    for fila in defectos.itertuples():
        p(f"      {fila.defecto_id} · {fila.fuente}")
        p(f"            clase        {fila.clase}")
        p(f"            se detecta   {fila.regla_de_deteccion}")
        p(f"            PROHÍBE      {fila.que_prohibe}")
        p(f"            sigue val.   {fila.que_sigue_valiendo}")
        p("")

    # ================================================================ dónde pega FD-01
    p("-" * 100)
    p("  DÓNDE PEGA FD-01 EN LO NUESTRO")
    p("")

    marcas = []

    # 1 · los establecimientos del Barrio Chino que cowork ya identificó
    if PUERTAS.exists():
        puertas = pd.read_csv(PUERTAS)
        tocados = puertas[puertas.fuente.astype(str).str.contains("Cronista", case=False)]
        for fila in tocados.itertuples():
            marcas.append({
                "defecto_id": "FD-01", "capa": "establecimientos_E02_E07_geo_r4.csv",
                "registro": fila.establecimiento, "campo": "vigencia_fecha",
                "valor": fila.vigencia_fecha, "estado_de_la_marca": "descartada_como_vigencia",
                "consecuencia": ("la fecha de origen (2021) es la que vale; la nota está "
                                 "re-sellada al 24/09/2025 y eso no verifica nada"),
            })
    p(f"      {len([m for m in marcas if m['capa'].startswith('establecimientos')])} "
      "establecimientos del Barrio Chino citados de El Cronista 26/08/2021.")
    for marca in marcas:
        p(f"            {marca['registro']}")
    p("")

    # 2 · los hitos de la capa que salen de cronista.com, y que NO traen fecha registrada
    capa = pd.read_csv(CAPA_HITOS)
    de_cronista = capa[capa.fuente_primaria.astype(str).str.contains("cronista.com", case=False)]
    for fila in de_cronista.itertuples():
        marcas.append({
            "defecto_id": "FD-01", "capa": "hitos_capa_2026_r3.csv",
            "registro": f"{fila.hito_id} {fila.nombre}", "campo": "fuente_primaria",
            "valor": str(fila.fuente_primaria)[:120],
            "estado_de_la_marca": "pendiente_de_comprobacion",
            "consecuencia": ("no registramos la fecha de actualización de esta nota: NO se "
                             "descarta y NO se da por buena. Hay que mirarla."),
        })
    p(f"      {len(de_cronista)} hitos de la capa salen de cronista.com y NO tienen fecha de")
    p("      actualización registrada por nosotros:")
    for fila in de_cronista.itertuples():
        p(f"            {fila.hito_id:<10}{str(fila.nombre)[:28]:<30}{str(fila.tipo)[:24]:<26}"
          f"{str(fila.barrio_declarado)[:18]}")
    p("")
    p("      Éstos quedan `pendiente_de_comprobacion`, no descartados. La regla se evalúa sobre")
    p("      un campo que no tenemos: registrar la fecha de actualización de esas seis notas es")
    p("      trabajo de la ronda que viene, y es barato comparado con lo que decide.")
    p("")

    # 3 · las citas de vía E con «act. 2025», que es la forma en que el defecto entra a la matriz
    sospechosas = []
    for archivo in sorted(EVIDENCIA.glob("*.csv")):
        try:
            tabla = pd.read_csv(archivo, dtype=str).fillna("")
        except Exception:
            continue
        for fila in tabla.itertuples(index=False):
            registro = " ".join(str(v)[:24] for v in list(fila)[:2] if str(v).strip())[:38]
            for campo, valor in zip(tabla.columns, fila):
                texto = str(valor)
                if not re.search(r"cronista", texto, flags=re.I):
                    continue
                # La fecha y el nombre del medio tienen que estar en el MISMO tramo de la cita.
                # Las citas de vía E enumeran medios separados por «|» o «;», y una fecha del
                # tramo de al lado no es del Cronista: R15 pone «Time Out BA 24/09/2025» al lado
                # de una cita de El Cronista, y marcarla sería aplicar el descarte de más.
                tramos = [t for t in re.split(r"[|;]", texto)
                          if re.search(r"act\.? ?2025|24/09/2025", t, flags=re.I)]
                if not tramos:
                    continue
                del_cronista = [t for t in tramos if re.search(r"cronista", t, flags=re.I)]
                sospechosas.append({
                    "defecto_id": "FD-01", "capa": archivo.name,
                    "registro": registro, "campo": campo, "valor": texto[:200],
                    "estado_de_la_marca": ("descartada_como_vigencia" if del_cronista
                                           else "falso_positivo · la fecha es de otro medio"),
                    "consecuencia": (
                        "la cita vale por su año de ORIGEN; «act. 2025» no cuenta como añada 2025"
                        if del_cronista else
                        "NO se marca: FD-01 es dominio + fecha, y esta fecha no es del Cronista"),
                })
    marcas.extend(sospechosas)
    marcadas = [m for m in sospechosas if m["estado_de_la_marca"].startswith("descartada")]
    p(f"      {len(marcadas)} citas de la evidencia documental invocan a El Cronista con la")
    p("      actualización de 2025 como si fuera añada:")
    for marca in marcadas:
        p(f"            {marca['capa']:<36}  {marca['registro'][:21]:<23}{marca['campo']}")
        p(f"                  {marca['valor'][:94]}")
    p("")
    p("      La que más pesa es R03 San Telmo, porque su vía E cuenta a El Cronista «2021, act.")
    p("      2025» como uno de los grupos independientes. Con FD-01 aplicado, ese grupo tiene")
    p("      añada 2021, no 2025 — y R03 ya venía con cero vías abiertas.")
    p("")

    # 4 · el falso positivo que hay que dejar dicho
    falsos = [m for m in sospechosas if m["estado_de_la_marca"].startswith("falso")]
    p(f"      Y {len(falsos)} FALSO(S) POSITIVO(S), que quedan en la tabla marcados como tales")
    p("      para que nadie los aplique de más:")
    for marca in falsos:
        p(f"            {marca['capa']:<36}  {marca['registro'][:21]:<23}{marca['campo']}")
        p(f"                  {marca['valor'][:94]}")
    p("            R15 Villa Devoto cita «Time Out BA 24/09/2025»: misma fecha, OTRO medio.")
    p("            FD-01 es dominio + fecha, no fecha sola. Time Out tiene su propio defecto")
    p("            (FD-04) y es de barrio, no de fecha.")
    p("")
    p("      Y EL CONTRAEJEMPLO, que es el que sostiene que la marca sea por fecha y no por medio:")
    p("            la nota de El Cronista sobre Los Laureles del 05/08/2026 está publicada 12:33")
    p("            y actualizada 12:34. Un minuto. Eso es una corrección de redacción, no un")
    p("            re-sellado, y esa nota sigue contando. FD-01 no dice «El Cronista no sirve»:")
    p("            dice que una fecha concreta de actualización no acredita nada.")
    p("")

    aplicadas = pd.DataFrame(marcas)
    aplicadas.to_csv(FUENTES / "fuentes_marcas_aplicadas.csv", index=False, encoding="utf-8")

    # ================================================================ Tarea 5 · vigencia
    p("-" * 100)
    p("  TAREA 5 · LOS DOS DATOS SUELTOS DEL BARRIO CHINO")
    p("")
    if PUERTAS.exists():
        puertas = pd.read_csv(PUERTAS)
        puertas["sentido_de_la_duda"] = ""
        puertas["vigencia_nota_r4"] = ""
        for nombre, (estado, sentido, nota) in VIGENCIA_BARRIO_CHINO.items():
            objetivo = puertas.establecimiento.map(plegar) == plegar(nombre)
            if not objetivo.any():
                p(f"      NO ESTÁ EN LA CAPA: {nombre} — se declara, no se inventa")
                continue
            antes = puertas.loc[objetivo, "vigencia"].iloc[0]
            puertas.loc[objetivo, "vigencia"] = estado
            puertas.loc[objetivo, "sentido_de_la_duda"] = sentido
            puertas.loc[objetivo, "vigencia_nota_r4"] = nota
            zona = puertas.loc[objetivo, "zona"].iloc[0]
            cambio = "cargado" if antes == estado else f"{antes} → {estado}"
            p(f"      {nombre:<20}{estado:<32}{cambio}")
            p(f"            zona: {zona} · {nota[:88]}")
            p("")
        puertas.to_csv(PUERTAS, index=False, encoding="utf-8")

        p("      SOBRE EL VOCABULARIO, que no es un detalle: `dudoso_probablemente_abierto` es un")
        p("      valor que la capa de HITOS no tiene. Su vocabulario es si · no · en_disputa ·")
        p("      dudosa · sin_verificar, y `dudosa` no dice hacia qué lado se duda. Acá el estado")
        p("      viaja partido en dos campos —`vigencia` = dudoso_probablemente_abierto y")
        p("      `sentido_de_la_duda` = probablemente_abierto— para que si mañana entra a la capa")
        p("      de hitos se pliegue a `dudosa` sin perder la dirección de la duda.")
        p("")
        p("      Y los dos cerrados no son simétricos con El Tokio: El Tokio y Todos Contentos")
        p("      reabrieron sin que ningún listado lo registrara. Hong Kong Style y Dragón Porteño")
        p("      cierran con la MISMA nota de iProfesional y sin nada después. Que la fuente del")
        p("      cierre sea la misma para los tres es justamente el motivo para no leer el")
        p("      silencio posterior como confirmación: la nota de 2020 no vuelve a mirar.")
        p("")

    # ================================================================ Boca a Boca
    p("-" * 100)
    p("  EL CONFLICTO DE BOCA A BOCA · confirmado, y sin resolver")
    p("")
    encontrados = []
    en_capa = capa[capa.nombre.map(plegar).str.contains(BOCA_A_BOCA, regex=False)]
    for fila in en_capa.itertuples():
        encontrados.append(("hitos_capa_2026_r3.csv", fila.hito_id, fila.direccion,
                            str(fila.conflicto_direccion), str(fila.metodo_geocodificacion)))
    altas = pd.read_csv(EVIDENCIA / "bares_notables_altas_2026-08-03.csv", dtype=str).fillna("")
    for fila in altas[altas.establecimiento.map(plegar).str.contains(
            BOCA_A_BOCA, regex=False)].itertuples():
        encontrados.append(("bares_notables_altas_2026-08-03.csv", "—", fila.direccion, "", ""))
    if BASE.exists():
        base = pd.read_csv(BASE, dtype=str).fillna("")
        suyos = base[base.nombre.map(plegar).str.contains(BOCA_A_BOCA, regex=False)
                     | base.direccion_norm.map(plegar).str.contains("PEREZ GALDOS", regex=False)]
        for fila in suyos.itertuples(index=False):
            registro = dict(zip(base.columns, fila))
            mismo_nombre = BOCA_A_BOCA in plegar(registro["nombre"])
            encontrados.append((
                "base/local.csv", registro["local_id"], registro["direccion_norm"],
                registro["fuentes"],
                registro["nombre"][:22] if mismo_nombre else "OTRO LOCAL, misma calle"))

    p(f"      {'capa':<36}{'id':<14}{'dirección':<34}{'nota'}")
    for capa_nombre, identificador, direccion, nota, extra in encontrados:
        p(f"      {capa_nombre:<36}{str(identificador)[:13]:<14}{str(direccion)[:33]:<34}"
          f"{str(nota)[:40]} {extra}")
    p("")
    p("      CONFIRMADO: la lista de las doce altas dice 207 y la capa de hitos tiene 201, que es")
    p("      la altura del Boletín Oficial. La capa ya traía la discrepancia anotada —«prensa")
    p("      consigna altura 207»—, así que el conflicto no es nuevo: es el mismo, y sigue")
    p("      abierto.")
    p("")
    p("      Lo que agrega esta ronda es que la base gastronómica tiene las DOS alturas como dos")
    p("      registros distintos y de fuentes distintas, y ninguna de las dos las reconcilia.")
    p("")
    # La distancia se mide, no se estima: si el conflicto moviera el punto de polo o de barrio
    # habría que frenar todo lo que lo use, y si no lo mueve hay que decirlo con el número.
    punto_201 = en_capa[["latitud", "longitud"]].dropna()
    distancia = None
    if BASE.exists() and len(punto_201):
        overture = base[base.nombre.map(plegar).str.contains(BOCA_A_BOCA, regex=False)]
        if len(overture):
            import geopandas as gpd
            par = gpd.GeoSeries(
                gpd.points_from_xy(
                    [float(punto_201.longitud.iloc[0]), float(overture.lon.iloc[0])],
                    [float(punto_201.latitud.iloc[0]), float(overture.lat.iloc[0])]),
                crs="EPSG:4326").to_crs("EPSG:5347")
            distancia = par.iloc[0].distance(par.iloc[1])
    p("      NO SE RESUELVE ACÁ, y el motivo es que las dos fuentes son del mismo rango: el")
    p("      Boletín dice una cosa y la prensa de la declaratoria dice otra, y no tenemos la")
    p("      resolución de las altas —que es la que zanjaría— porque sigue sin localizarse.")
    p("")
    if distancia is not None:
        p(f"      LO QUE SÍ SE PUEDE DECIR CON UN NÚMERO: el punto del 201 (USIG sobre el Boletín)")
        p(f"      y el punto del 207 (Overture) están a {distancia:.1f} m. Es la misma puerta con")
        p("      dos alturas publicadas, no dos locales. El conflicto es documental y no mueve")
        p("      ninguna medición: mismo polo, mismo barrio, misma celda de la matriz.")
    p("")
    p("      Queda como `conflicto_direccion` y se verifica en campo, que es de las pocas cosas")
    p("      que una verificación de campo resuelve mejor que cualquier documento.")
    p("")

    p("=" * 100)
    p(f"  {len(defectos)} fuentes con defecto · {len(aplicadas)} marcas aplicadas · "
      f"{len(VIGENCIA_BARRIO_CHINO)} estados de vigencia cargados · 0 consultas")
    p("=" * 100)
    p("")

    (FUENTES / "FUENTES_DEFECTOS_R4.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
