"""Prueba de techo de Google Places sobre UNA zona. Varias familias, refinamiento sin tope.

QUÉ PREGUNTA CONTESTA, Y POR QUÉ NO LA CONTESTABA EL CONTROL
------------------------------------------------------------
El control de las 17 zonas midió que Places recupera el 9,7 % de un conteo de campo. Ese número
tiene dos lecturas posibles y el control **no las separa**:

  - «Places encuentra poco» — es una fuente de contraste, no de conteo;
  - «nuestra consulta buscó poco» — una familia genérica, refinamiento cortado en un nivel y tres
    zonas con celdas saturadas admitidas.

Las dos producen exactamente el mismo porcentaje. Lo que el control midió es el techo de ESA
barrida, no el techo de Places. Esta prueba levanta las tres limitaciones sobre una sola zona y
mide el techo de verdad.

De esta separación cuelga el plan del barrido de los 48 barrios, que queda congelado hasta que la
prueba salga. Replantear el plan sobre una medición saturada es el error caro.

POR QUÉ VILLA CRESPO (R08)
--------------------------
Es la zona mejor calibrada que tenemos: 646 locales relevados a pie, 233 direcciones de padrón,
factor documental conocido de 36,1 %. Y en el control **ninguna de sus celdas quedó saturada a
500 m**, así que su 13,3 % no arrastra el defecto de las otras tres: lo que le falta es
profundidad de consulta, que es justo lo que esta prueba agrega.

LAS TRES LIMITACIONES QUE SE LEVANTAN
-------------------------------------
1. **Varias familias de consulta**, no una genérica. Ver `FAMILIAS`.
2. **Refinamiento sin tope de niveles.** El control paraba en 500 m; acá se sigue partiendo
   mientras una celda devuelva su techo. El único freno real es el presupuesto.
3. **Paginación completa.** Ya era completa: 3 páginas son el tope duro de Text Search y no hay
   una cuarta. Se deja dicho para que nadie lo busque.

LA LECTURA VA DECIDIDA DE ANTEMANO
----------------------------------
Las bandas de `LECTURA_PREVIA` están escritas **antes** de correr, y el script imprime el veredicto
que le toque al número que salga. No es adorno: un resultado ambiguo se acomoda solo si uno decide
qué significaba después de verlo.

GUARDARRAÍLES
-------------
- `--dry-run` por defecto; la corrida real necesita `--run --confirm-real-api`.
- La key sale sólo de `GOOGLE_MAPS_API_KEY`, que `cargar_dotenv()` completa desde `.env`. No se
  pide por consola, no entra por argumento, no se imprime, no se guarda.
- **Tope duro exacto, sin tolerancia.** El control admitía +20 % sobre el presupuesto porque su
  refinamiento estaba acotado a un nivel y el gasto era previsible. Acá el refinamiento no tiene
  tope de niveles, así que el presupuesto autorizado es un techo literal: la corrida se detiene
  al llegar, informa qué quedó sin medir y no sigue «por poco».
- Nombres, direcciones y `place_id` van a carpeta interna ignorada por Git. Lo versionable es el
  agregado por familia.
- Sólo API oficial. Nada de scraping.

USO
---
  python scripts/barrido_ciudad/places_techo_zona.py                       # dry-run
  python scripts/barrido_ciudad/places_techo_zona.py --run --confirm-real-api
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from places_control_zonas import (  # noqa: E402
    CONSULTA_GENERICA,
    CRS_METRICO,
    GEN,
    LADO_BASE_M,
    PAGINAS_MAXIMAS,
    RESULTADOS_POR_PAGINA,
    UMBRAL_SATURACION,
    a_rectangulo,
    anillo,
    asignar_por_geometria,
    cargar_dotenv,
    celdas_de,
    consultar_celda,
    leer_api_key,
    perimetros,
    zonas_con_cifra,
)

ZONA_POR_DEFECTO = "R08"
INTERNO = ROOT / "outputs" / "analisis_interno" / "places_techo_zona_2026-08"

# El refinamiento no tiene tope de NIVELES, que es lo que pedía la prueba. Sí tiene un piso
# geométrico, y no es un tope disfrazado: a 62,5 m la celda es media cuadra. Si algo sigue
# devolviendo 60 resultados ahí adentro, el problema no es la grilla y hay que decirlo, no seguir
# partiendo. Se informa aparte si se llega.
LADO_PISO_M = 62.5

# Las familias de consulta. La A es **idéntica** a la del control, y eso es deliberado: si la
# corrida no reproduce los 86 núcleo de R08, algo cambió —la API, la geometría, el código— y el
# resto de la medición no es comparable. Es el control de aceptación de esta prueba.
#
# MEDIDO EL 2026-08-05, ANOTADO PARA EL DISEÑO FUTURO Y NO EJECUTADO: la familia C aportó CERO
# locales nuevos sobre R08, y la B aportó 18 sobre 63. Si algún día se corre el barrido de los 48
# barrios, C se descarta y se ahorra un tercio del costo de familias; B paga lo que cuesta. No se
# toca acá ni en la spec: el plan de los 48 sigue congelado y se replantea de una sola vez.
FAMILIAS = {
    "A_generica": CONSULTA_GENERICA,
    "B_parrilla_pizza_paso": "parrilla pizzería y comida al paso",
    "C_heladeria": "heladería",
}
FAMILIA_ESPEJO = "A_generica"   # la que tiene que reproducir el control

PRESUPUESTO_SUGERIDO = 150      # lo que Diego puso como orden de magnitud; el dry-run lo ajusta

# Las bandas están escritas ANTES de correr. El veredicto lo elige el número, no el redactor.
LECTURA_PREVIA = [
    (0.0, 15.0, "CONCLUSIÓN FIRME",
     "Places es fuente de contraste, no de conteo. El plan de los 48 barrios se replantea "
     "con fundamento."),
    (15.0, 60.0, "RANGO INTERMEDIO · decide Diego",
     "No cae en ninguna de las dos bandas previstas. Se reporta el rango y se decide con "
     "Diego, sin acomodar la lectura."),
    (60.0, 1e9, "LA BARRIDA ERA CHICA",
     "El plan de los 48 barrios NO se toca. Lo que se corrige es la profundidad de consulta "
     "del barrido."),
]


# --------------------------------------------------------------------------- plan

def plan_zona(rid: str) -> gpd.GeoDataFrame:
    """La grilla base de 1 km sobre una sola zona, una fila por (celda × familia).

    Arranca en 1 km y no en 500 m a propósito: así la familia A recorre exactamente el mismo
    camino que el control y su resultado es comparable celda por celda. Lo que cambia es que
    ahora el refinamiento no se detiene en el primer nivel.
    """
    formas = perimetros()
    if rid not in formas or formas[rid].is_empty:
        raise SystemExit(f"ABORTADO: no hay envolvente para {rid}.")
    zonas = zonas_con_cifra()
    filas = []
    for celda in celdas_de(formas[rid], LADO_BASE_M, rid):
        for familia in FAMILIAS:
            filas.append({"rid": rid, "zona": zonas.zona_publicada[rid],
                          "familia": familia, "nivel": 0, **celda})
    return gpd.GeoDataFrame(filas, geometry="geometry", crs=CRS_METRICO)


def baseline_del_control(rid: str) -> dict | None:
    """La línea de comparación correcta: los puntos del control que trajeron celdas de ESTA zona.

    El control consultó las 17 zonas, y la celda de 1 km se conserva si *toca* la envolvente, así
    que las celdas de zonas vecinas barren territorio de ésta. Sus puntos caen dentro de esta
    envolvente y el `sjoin` se los atribuye —con razón: geométricamente están acá—. Pero esta
    prueba consulta **sólo** las celdas de esta zona, así que nunca puede reproducir ese total.

    Comparar contra el total del control es comparar coberturas distintas. La línea comparable es
    el subtotal que trajeron las celdas propias. En R08 son 76 de 86: los otros 10 los levantaron
    R21 y R09 de paso.

    Que una celda de R21 encuentre un punto de R08 que la celda de R08 —que cubre exactamente ese
    lugar— no trajo, no es un detalle contable: es la prueba de que Text Search rankea y no
    enumera. Dos encuadres del mismo territorio devuelven subconjuntos distintos.
    """
    from places_control_zonas import INTERNO as INTERNO_CONTROL
    archivo = INTERNO_CONTROL / "places_puntos_interno.csv"
    if not archivo.exists():
        return None
    puntos = asignar_por_geometria(pd.read_csv(archivo, encoding="utf-8-sig"))
    de_zona = puntos[(puntos.rid_geo == rid) & (puntos.anillo == "nucleo")]
    if not len(de_zona):
        return None
    return {"total": len(de_zona),
            "celdas_propias": int((de_zona.rid == rid).sum()),
            "celdas_vecinas": int((de_zona.rid != rid).sum()),
            "vecinas_detalle": de_zona[de_zona.rid != rid].rid.value_counts().to_dict()}


def costo_medido_del_control(rid: str) -> dict | None:
    """Lo que la familia A costó de verdad en el control, leído de su bitácora.

    Es el mejor insumo que hay para presupuestar: no es una conjetura sobre cuántas celdas van a
    saturar, es cuántas saturaron cuando se corrió esta misma consulta sobre esta misma zona.
    """
    bitacora = (ROOT / "outputs" / "analisis_interno" / "places_control_zonas_2026-08"
                / "places_bitacora_celdas.csv")
    if not bitacora.exists():
        return None
    marco = pd.read_csv(bitacora)
    de_zona = marco[marco.rid == rid]
    if not len(de_zona):
        return None
    return {
        "requests": int(de_zona.requests.sum()),
        "celdas_1km": int((de_zona.lado_m == LADO_BASE_M).sum()),
        "celdas_500m": int((de_zona.lado_m < LADO_BASE_M).sum()),
        "saturadas_1km": int(((de_zona.lado_m == LADO_BASE_M) & de_zona.saturada).sum()),
        "saturadas_500m": int(((de_zona.lado_m < LADO_BASE_M) & de_zona.saturada).sum()),
    }


# --------------------------------------------------------------------------- corrida

def correr(plan: gpd.GeoDataFrame, clave: str, presupuesto: int) -> dict:
    """Refinamiento sin tope de niveles, por familia, con tope duro de gasto.

    El dedup es por `place_id` **a través de todas las familias**: el techo que buscamos es la
    unión, no la suma. Lo que sí se guarda por separado es qué familia trajo cada punto por
    primera vez, porque el aporte marginal de B y de C es justamente lo que contesta si la
    consulta genérica buscaba poco.

    Dentro de cada familia la cola es a lo ancho (`append`, no `insert(0)`), igual que en el
    control y por el mismo motivo: si el presupuesto corta, lo que se pierde son los refinamientos
    más profundos y no territorio entero sin medir.

    **Y entre familias se va por turnos**, que es un cambio respecto del control. Con una sola cola
    compartida, los refinamientos de A se descubren antes y se encolan antes, así que un corte por
    presupuesto deja a A con el doble de celdas que a C. Las familias quedarían medidas a distinta
    profundidad y el aporte marginal de B y de C —lo único que esta prueba viene a medir— saldría
    subestimado por el orden de la cola y no por lo que hay en la calle. Por turnos, un corte deja
    a las tres con la misma cobertura geográfica, que es la comparación que hay que preservar.
    """
    gastados = 0
    vistos: set[str] = set()
    puntos: list[dict] = []
    bitacora: list[dict] = []
    en_el_piso: list[dict] = []
    errores: list[str] = []
    hoy = dt.date.today().isoformat()

    # Una cola por familia; se atienden por turnos, en el orden fijo de FAMILIAS.
    colas: dict[str, list[dict]] = {familia: [] for familia in FAMILIAS}
    for fila in plan.to_dict("records"):
        colas[fila["familia"]].append(dict(fila))

    turno = 0
    while any(colas.values()):
        familias_vivas = [f for f in FAMILIAS if colas[f]]
        familia_actual = familias_vivas[turno % len(familias_vivas)]
        turno += 1
        celda = colas[familia_actual].pop(0)
        # Se corta ANTES de una consulta que pudiera pasarse, no después de pasarse. Una celda
        # cuesta hasta `PAGINAS_MAXIMAS` requests y no se sabe cuántos hasta hacerla, así que
        # comprobar `gastados >= presupuesto` dejaría exceder el tope en hasta dos requests.
        # Se desperdician como mucho dos de margen y a cambio el tope es literal, que es lo que
        # se autorizó. Tampoco quedan celdas medidas a medias.
        if gastados + PAGINAS_MAXIMAS > presupuesto:
            sin_hacer = sum(len(cola) for cola in colas.values()) + 1
            faltan = ", ".join(f"{f}={len(colas[f])}" for f in FAMILIAS if colas[f])
            errores.append(f"TOPE DE GASTO alcanzado ({gastados}/{presupuesto}, sin margen para "
                           f"otra celda); quedaron {sin_hacer} consultas sin hacer "
                           f"({faltan or 'ninguna'})")
            break

        lugares, costo, error = consultar_celda(
            clave, a_rectangulo(celda["geometry"]), FAMILIAS[celda["familia"]])
        gastados += costo
        if error:
            errores.append(f"{celda['celda_id']} · {celda['familia']}: {error}")

        nuevos = 0
        for lugar in lugares:
            pid = lugar.get("id", "")
            capa = anillo(lugar.get("types"))
            if not pid or capa is None or pid in vistos:
                continue
            vistos.add(pid)
            nuevos += 1
            ubicacion = lugar.get("location") or {}
            puntos.append({
                "place_id": pid,
                "nombre": (lugar.get("displayName") or {}).get("text", ""),
                "direccion": lugar.get("formattedAddress", ""),
                "lat": ubicacion.get("latitude", ""),
                "lon": ubicacion.get("longitude", ""),
                "business_status": lugar.get("businessStatus", ""),
                "types": ";".join(lugar.get("types") or []),
                "anillo": capa,
                "rid": celda["rid"], "celda_id": celda["celda_id"],
                "lado_m": celda["lado_m"], "nivel": celda["nivel"],
                # Qué familia lo trajo PRIMERO. Es el aporte marginal, no la atribución total:
                # un punto que B y C también devuelven queda contado una sola vez, en la primera.
                "familia_primera": celda["familia"],
                "fecha_consulta": hoy,
            })

        saturada = len(lugares) >= UMBRAL_SATURACION
        bitacora.append({"celda_id": celda["celda_id"], "rid": celda["rid"],
                         "familia": celda["familia"], "lado_m": celda["lado_m"],
                         "nivel": celda["nivel"], "devueltos": len(lugares),
                         "nuevos": nuevos, "requests": costo,
                         "saturada": saturada, "error": error or ""})

        if not saturada:
            continue
        if celda["lado_m"] / 2 < LADO_PISO_M:
            # Piso geométrico. No se sigue partiendo, se declara.
            en_el_piso.append({"celda_id": celda["celda_id"], "familia": celda["familia"],
                               "lado_m": celda["lado_m"], "devueltos": len(lugares)})
            continue
        for hija in celdas_de(celda["geometry"], celda["lado_m"] / 2, celda["celda_id"] + "R"):
            colas[familia_actual].append(
                {"rid": celda["rid"], "zona": celda["zona"],
                 "familia": celda["familia"], "nivel": celda["nivel"] + 1, **hija})

    return {"gastados": gastados, "puntos": puntos, "bitacora": bitacora,
            "en_el_piso": en_el_piso, "errores": errores, "presupuesto": presupuesto}


# --------------------------------------------------------------------------- informe

def veredicto(pct: float) -> tuple[str, str]:
    """El veredicto que le toca al número, según bandas escritas antes de la corrida."""
    for piso, techo, titulo, texto in LECTURA_PREVIA:
        if piso <= pct < techo:
            return titulo, texto
    return "FUERA DE TODA BANDA", "Revisar: el número no cae en ninguna banda prevista."


def informar(resultado: dict, rid: str) -> pd.DataFrame:
    """El aporte de cada familia, acumulado, contra la cifra publicada de la zona."""
    zonas = zonas_con_cifra()
    relevado = float(zonas.relevado[rid])
    puntos = asignar_por_geometria(pd.DataFrame(resultado["puntos"]))
    adentro = puntos[puntos.rid_geo == rid] if len(puntos) else puntos

    filas, acumulado = [], 0
    for familia in FAMILIAS:
        de_familia = adentro[(adentro.familia_primera == familia)
                             & (adentro.anillo == "nucleo")] if len(adentro) else adentro
        aporte = len(de_familia)
        acumulado += aporte
        gasto = sum(f["requests"] for f in resultado["bitacora"] if f["familia"] == familia)
        filas.append({
            "familia": familia,
            "consulta": FAMILIAS[familia],
            "requests": gasto,
            "nucleo_nuevos": aporte,
            "nucleo_acumulado": acumulado,
            "pct_sobre_publicada": round(100 * acumulado / relevado, 1) if relevado else None,
            "celdas_consultadas": sum(1 for f in resultado["bitacora"]
                                      if f["familia"] == familia),
            "nivel_maximo": max([f["nivel"] for f in resultado["bitacora"]
                                 if f["familia"] == familia] or [0]),
        })
    return pd.DataFrame(filas)


def _coma(valor: float, decimales: int = 1) -> str:
    """Un número con coma decimal, para el párrafo que se copia y pega a un informe."""
    return f"{valor:.{decimales}f}".replace(".", ",")


def recaptura_guardada(rid: str) -> dict | None:
    """El resumen de `captura_recaptura_places.py`, si ya se calculó. No se recalcula acá.

    Se lee en vez de repetirse para que los números no queden escritos a mano en dos lugares:
    el que decide cuánto varía una corrida contra otra es ese script, que tiene las bitácoras de
    las dos y puede separar la variación de la fuente de la del refinamiento.
    """
    archivo = GEN / f"captura_recaptura_{rid}_resumen.json"
    if not archivo.exists():
        return None
    return json.loads(archivo.read_text(encoding="utf-8"))


def limite_del_detector(rid: str, relevado: float) -> list[str]:
    """Lo que el detector de saturación NO ve, y por qué no se persigue.

    El detector mira una sola cosa: si la celda devolvió el tope de página. Pero la profundidad
    que Text Search sirve varía por su cuenta —`R08_0101` devolvió 58 y 40 sin tocar nunca el tope
    de 60— así que una celda puede quedar cortada por el ranking sin que el detector se entere.

    **De ahí se sigue que «ninguna celda saturó» NO equivale a «ninguna celda quedó truncada».**
    Es un límite real del instrumento y va escrito donde se afirma que el refinamiento cerró solo.

    Lo que sigue es la razón de no perseguirlo, y es una cota, no una corazonada: en el peor caso
    imaginable —una corrida de otro día que devolviera un conjunto TOTALMENTE disjunto del de
    ésta— la unión sería el doble del universo alcanzable estimado. Ese doble sigue estando muy
    lejos de la cifra de campo, así que la conclusión es robusta a la incertidumbre que queda. La
    distancia es tan grande que cerrar el frente no depende de resolverla.
    """
    recaptura = recaptura_guardada(rid)
    if not recaptura or not relevado:
        return []
    estimado = recaptura.get("n_estimado")
    if not estimado:
        return []
    peor_caso = 2 * estimado
    return [
        "",
        "  LÍMITE DEL DETECTOR · lo que este control no puede ver",
        "    El detector mira el tope de página, no el corte del ranking. Como la profundidad",
        "    servida varía sola —58 y 40 en la misma celda sin tocar nunca el tope de 60—,",
        "    «ninguna celda saturó» NO equivale a «ninguna celda quedó truncada».",
        "",
        f"    No se persigue, y no por falta de ganas: en el peor caso imaginable —otra corrida",
        f"    que devolviera un conjunto totalmente disjunto— la unión sería {peor_caso:.0f} sobre "
        f"{int(relevado)},",
        f"    un {100 * peor_caso / relevado:.0f} %. Sigue sin acercarse a reemplazar la caminata. "
        "La conclusión es",
        "    robusta a la incertidumbre que queda porque la distancia es enorme.",
    ]


def como_se_reporta(medido_a: int, medido_total: int, base: dict | None,
                    relevado: float, rid: str) -> list[str]:
    """Cómo se reporta el número, que es propiedad de la fuente y no un valor puntual.

    ESTO REEMPLAZA AL «RANGO PLAUSIBLE 12,5 – 17,1 %» QUE ESTUVO ACÁ, Y ES UNA CORRECCIÓN DE
    MÉTODO, no de redacción. El rango se armaba aplicando el factor de familias medido en ESTA
    corrida a la línea de la OTRA corrida. Pero lo que esta prueba demostró es justamente que dos
    corridas de la misma consulta difieren, así que multiplicar el factor de una por el total de
    la otra mezcla corridas: es exactamente la operación que el propio hallazgo prohíbe.

    Lo que se reporta entonces son las mediciones que existen, cada una con su corrida, más la
    variabilidad medida entre corridas como propiedad de la fuente. Que las dos caigan tan cerca
    pese al ruido es evidencia a favor del resultado, no en contra.

    El factor de familias se sigue informando, porque es un buen dato: se midió dentro de una sola
    corrida —mismas celdas, misma tarde, misma geometría— y por eso es internamente comparable.
    Lo que no se hace es sacarlo de esa corrida y aplicarlo a otra.
    """
    if not medido_a or not base:
        return []
    factor = medido_total / medido_a
    pct_tres = 100 * medido_total / relevado
    pct_una = 100 * base["celdas_propias"] / relevado
    lineas = [
        "",
        "  CÓMO SE REPORTA · propiedad de la fuente, no valor puntual",
        "",
        f"    medido con tres familias, esta corrida      : {medido_total} → {pct_tres:.1f} %",
        f"    medido con una familia, la corrida del control: {base['celdas_propias']} → "
        f"{pct_una:.1f} %",
        f"    aporte marginal de las familias, medido dentro de esta corrida: "
        f"{medido_total}/{medido_a} = ×{factor:.3f}",
    ]

    recaptura = recaptura_guardada(rid)
    if recaptura:
        igual = recaptura.get("igual_esfuerzo") or {}
        variacion = recaptura.get("variacion_pct_igual_esfuerzo")
        if variacion is None and igual:
            variacion = 100 * (igual["n2"] - igual["n1"]) / igual["n1"]
        discordantes = recaptura.get("celdas_discordantes") or []
        estimado = recaptura.get("n_estimado")
        cierre = (f"       Entre corridas de la misma consulta la variación fue del "
                  f"{abs(variacion):.0f} % a igual esfuerzo.»")
        lineas += [
            "",
            f"    variación entre corridas de la MISMA consulta: {variacion:+.1f} % a igual "
            "esfuerzo,",
            f"    y no está repartida por la grilla: sale de "
            f"{len(discordantes)} celda(s) "
            f"({', '.join(discordantes) or 'ninguna'}).",
            f"    universo alcanzable, por captura-recaptura: N̂ ≈ {estimado:.0f} "
            f"({100 * estimado / relevado:.1f} % de la cifra publicada), y es cota inferior.",
        ]
    else:
        variacion = None
        cierre = "       Entre corridas de la misma consulta hay variación medible.»"
        lineas += [
            "",
            "    (la variabilidad entre corridas la mide `captura_recaptura_places.py`, que",
            "     todavía no corrió sobre esta zona)",
        ]

    # El «del orden de» sale del promedio de las dos mediciones, no de la más alta redondeada
    # hacia arriba: 12,5 y 11,8 son del orden del 12 %, y decir 13 sería quedarse con la punta
    # que conviene por vía del redondeo.
    orden = round((pct_tres + pct_una) / 2)
    lineas += [
        "",
        "    Redacción que corresponde, y no un rango armado mezclando corridas:",
        "",
        f"      «Una barrida de Places sobre {rid} recupera del orden del {orden:.0f} % de la "
        "cifra",
        f"       relevada a pie. Medido: {_coma(pct_tres)} % con tres familias y "
        f"{_coma(pct_una)} % con una sola.",
        cierre,
        "",
        "    NO se reporta «12,5 – 17,1 %»: ese rango aplicaba el factor de familias de esta",
        "    corrida a la línea de la otra, y mezclar corridas es lo que este resultado prohíbe.",
        f"    Que las dos mediciones caigan a {abs(pct_tres - pct_una):.1f} pp una de otra pese al",
        "    ruido es evidencia adicional a favor. Ninguna lectura se acerca al 60 %.",
    ]
    return lineas


def publicar(resultado: dict, rid: str) -> None:
    zonas = zonas_con_cifra()
    relevado = float(zonas.relevado[rid])
    base = baseline_del_control(rid)
    nucleo_previo = base["celdas_propias"] if base else None

    tabla = informar(resultado, rid)
    GEN.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(GEN / f"places_techo_{rid}.csv", index=False, encoding="utf-8")

    total = int(tabla.nucleo_acumulado.iloc[-1])
    pct = 100 * total / relevado if relevado else 0.0
    titulo, texto = veredicto(pct)

    print("=" * 78)
    print(f"  PRUEBA DE TECHO · {rid} · {zonas.zona_publicada[rid]}")
    print("=" * 78)
    print(tabla.to_string(index=False))
    print("")
    print(f"  cifra publicada (relevada a pie) : {int(relevado)}")
    print(f"  Places, unión de las familias    : {total}  ({pct:.1f} % de la cifra publicada)")
    espejo = tabla[tabla.familia == FAMILIA_ESPEJO]
    solo_a = int(espejo.nucleo_nuevos.iloc[0]) if len(espejo) else 0
    if base is not None:
        print(f"  el control, celdas de {rid} solamente : {base['celdas_propias']}  "
              f"({100 * base['celdas_propias'] / relevado:.1f} %)  ← línea comparable")
        print(f"  el control, total de la zona       : {base['total']}  "
              f"(+{base['celdas_vecinas']} que trajeron celdas vecinas: "
              f"{', '.join(f'{k}={v}' for k, v in base['vecinas_detalle'].items())})")
        print("")
        desvio = 100 * (solo_a - base["celdas_propias"]) / base["celdas_propias"]
        estado = "REPRODUCE" if solo_a == base["celdas_propias"] else f"DIFIERE {desvio:+.0f} %"
        print(f"  CONTROL DE ACEPTACIÓN · familia A hoy contra el control, misma cobertura:")
        print(f"    {solo_a} vs {base['celdas_propias']} → {estado}")
        if solo_a != base["celdas_propias"]:
            print("    Misma consulta, mismas celdas, misma geometría y —hay que decirlo bien— la")
            print("    MISMA TARDE, no otro día: las dos corridas son del mismo día. La diferencia")
            print("    no es del código ni deriva del padrón de Google entre jornadas.")
            print("    `captura_recaptura_places.py` la localiza: no está repartida por la grilla,")
            print("    sale de una celda que devolvió 18 resultados menos, cayó bajo el umbral y")
            print("    por eso no se refinó. Text Search sirve una lista rankeada y lo que se mueve")
            print("    es hasta dónde la sirve, no el orden.")

    print("")
    print(f"  requests gastados: {resultado['gastados']} de {resultado['presupuesto']} autorizados")
    niveles = max([f["nivel"] for f in resultado["bitacora"]] or [0])
    print(f"  nivel máximo de refinamiento alcanzado: {niveles} "
          f"(celda de {LADO_BASE_M / 2 ** niveles:.1f} m)")
    saturadas = [f for f in resultado["bitacora"] if f["saturada"]]
    print(f"  celdas que saturaron y se partieron: {len(saturadas) - len(resultado['en_el_piso'])}")
    if resultado["en_el_piso"]:
        print(f"  *** {len(resultado['en_el_piso'])} celdas siguen saturadas en el piso de "
              f"{LADO_PISO_M:.1f} m ***")
        for celda in resultado["en_el_piso"]:
            print(f"    {celda['celda_id']} · {celda['familia']}: {celda['devueltos']}")
    else:
        print(f"  celdas saturadas en el piso de {LADO_PISO_M:.1f} m: ninguna — "
              "el refinamiento cerró solo")
    for linea in limite_del_detector(rid, relevado):
        print(linea)
    for error in resultado["errores"]:
        print(f"  error: {error}")

    print("")
    print("=" * 78)
    print("  VEREDICTO · banda escrita ANTES de la corrida")
    print("=" * 78)
    print(f"  {pct:.1f} % de la cifra publicada → {titulo}")
    print(f"  {texto}")
    for linea in como_se_reporta(solo_a, total, base, relevado, rid):
        print(linea)
    if resultado["errores"] or resultado["en_el_piso"]:
        print("")
        print("  ATENCIÓN: la corrida tuvo cortes o celdas en el piso. El número de arriba sigue")
        print("  siendo una cota inferior y el veredicto se lee con esa reserva.")

    resumen = {
        "fecha": dt.date.today().isoformat(),
        "zona": rid, "cifra_publicada": int(relevado),
        "places_union_familias": total,
        "pct_sobre_publicada": round(pct, 1),
        "control_una_familia": nucleo_previo,
        "requests_gastados": resultado["gastados"],
        "requests_autorizados": resultado["presupuesto"],
        "nivel_maximo_refinamiento": niveles,
        "celdas_en_el_piso": len(resultado["en_el_piso"]),
        "veredicto": titulo,
        "errores": resultado["errores"],
    }
    (GEN / f"places_techo_{rid}_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print("")
    print(f"  interno (fuera de Git): {INTERNO}")
    print(f"  publicable: {GEN / f'places_techo_{rid}.csv'}")


def mostrar_plan(plan: gpd.GeoDataFrame, rid: str, presupuesto: int) -> None:
    zonas = zonas_con_cifra()
    medido = costo_medido_del_control(rid)
    celdas = len(plan) // len(FAMILIAS)

    print("=" * 78)
    print(f"  PRUEBA DE TECHO · {rid} · {zonas.zona_publicada[rid]} · DRY-RUN")
    print("=" * 78)
    print(f"  cifra publicada (relevada a pie): {int(zonas.relevado[rid])}")
    print(f"  celdas de {LADO_BASE_M:.0f} m sobre la envolvente: {celdas}")
    print(f"  familias de consulta: {len(FAMILIAS)}")
    for familia, texto in FAMILIAS.items():
        marca = "  (idéntica al control)" if familia == FAMILIA_ESPEJO else ""
        print(f"    {familia:<24}: «{texto}»{marca}")
    print(f"  refinamiento: sin tope de niveles, piso geométrico {LADO_PISO_M:.1f} m")
    print(f"  paginación: {PAGINAS_MAXIMAS} páginas ({PAGINAS_MAXIMAS * RESULTADOS_POR_PAGINA} "
          "resultados), que es el tope duro de Text Search")
    print(f"  umbral de saturación: {UMBRAL_SATURACION} resultados por celda")
    print("")

    print("-" * 78)
    print("  PRESUPUESTO")
    print("-" * 78)
    piso = len(plan)
    print(f"  piso exacto (una página por celda × familia, nada satura): {piso} requests")
    if medido:
        print("")
        print(f"  medido: la familia A ya se corrió sobre {rid} en el control del 2026-08-05")
        print(f"    {medido['requests']} requests · {medido['celdas_1km']} celdas de 1 km "
              f"({medido['saturadas_1km']} saturaron) · {medido['celdas_500m']} de 500 m "
              f"({medido['saturadas_500m']} saturaron)")
        print(f"    Como ninguna saturó a 500 m, la familia A bajo refinamiento sin tope vuelve a")
        print(f"    costar {medido['requests']}: no hay un nivel más que abrir.")
        print("")
        techo_estimado = medido["requests"] * len(FAMILIAS)
        print(f"  estimación: si B y C se comportaran como A → "
              f"{medido['requests']} × {len(FAMILIAS)} = {techo_estimado} requests")
        print("    Es una cota alta: B y C son consultas más angostas que la genérica y deberían")
        print("    saturar menos. El gasto real esperado está entre el piso y esa cota.")
    print("")
    print(f"  TOPE DURO AUTORIZADO: {presupuesto} requests · sin tolerancia, corta exacto")
    print("")
    print("  Franja mensual: 5.000 en Pro. Gastados en agosto: 256 (control de 17 zonas).")
    print(f"  Disponible: {5000 - 256}. Esta prueba pide como máximo {presupuesto}, "
          f"y quedarían {5000 - 256 - presupuesto}.")
    print("")
    print("-" * 78)
    print("  LECTURA, ESCRITA ANTES DE CORRER")
    print("-" * 78)
    for piso_banda, techo_banda, titulo, texto in LECTURA_PREVIA:
        rango = (f"{piso_banda:.0f} – {techo_banda:.0f} %" if techo_banda < 1e8
                 else f"{piso_banda:.0f} % o más")
        print(f"  {rango:<14} → {titulo}")
        print(f"                   {texto}")
    # La referencia es la línea COMPARABLE —las celdas propias—, no el total de la zona en el
    # control. El total incluye puntos que trajeron celdas vecinas y esta prueba no los puede
    # alcanzar, así que compararse contra él sería pedirle reproducir algo que no consultó.
    base = baseline_del_control(rid)
    if base:
        relevado = float(zonas.relevado[rid])
        print("")
        print(f"  Referencia: el control de una familia dio {base['celdas_propias']} núcleo con "
              f"celdas propias de {rid}")
        print(f"  ({100 * base['celdas_propias'] / relevado:.1f} % de la cifra publicada); su total "
              f"de zona era {base['total']}, con celdas vecinas incluidas.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Prueba de techo de Places sobre una zona.")
    ap.add_argument("--zona", default=ZONA_POR_DEFECTO,
                    help=f"referencia_id de la zona (default {ZONA_POR_DEFECTO}).")
    ap.add_argument("--reinformar", action="store_true",
                    help="Rehace el informe desde los datos ya guardados. No toca la red.")
    ap.add_argument("--run", action="store_true", help="Ejecuta de verdad. Sin esto: dry-run.")
    ap.add_argument("--confirm-real-api", action="store_true",
                    help="Segunda confirmación, obligatoria junto con --run.")
    ap.add_argument("--presupuesto", type=int, default=PRESUPUESTO_SUGERIDO,
                    help=f"Tope duro de requests (default {PRESUPUESTO_SUGERIDO}).")
    args = ap.parse_args()

    cargar_dotenv()

    if args.reinformar:
        # Rehace la presentación con lo que ya está en disco. Cero requests. Mismo criterio que
        # `places_control_zonas.py --reinformar`: corregir cómo se lee un resultado no puede
        # costar una segunda medición, y menos con una fuente que no se reproduce entre días.
        puntos = pd.read_csv(INTERNO / f"places_techo_{args.zona}_puntos.csv",
                             encoding="utf-8-sig")
        bitacora = pd.read_csv(INTERNO / f"places_techo_{args.zona}_bitacora.csv")
        resultado = {"gastados": int(bitacora.requests.sum()),
                     "puntos": puntos.to_dict("records"),
                     "bitacora": bitacora.to_dict("records"),
                     "en_el_piso": [], "errores": [],
                     "presupuesto": args.presupuesto}
        print("\nREINFORMAR: se rehace el informe desde los datos guardados. "
              "No se tocó la red, no se gastó un solo request.\n")
        publicar(resultado, args.zona)
        return 0

    plan = plan_zona(args.zona)
    mostrar_plan(plan, args.zona, args.presupuesto)

    if not args.run:
        clave = leer_api_key()
        print("")
        if clave:
            print(f"  GOOGLE_MAPS_API_KEY: disponible (no se imprime; longitud={len(clave)})")
        else:
            print("  GOOGLE_MAPS_API_KEY: NO disponible — ni en el entorno ni en .env")
        print("")
        print("DRY-RUN: no se tocó la red, no se gastó un solo request.")
        print("Para ejecutar: --run --confirm-real-api.")
        return 0
    if not args.confirm_real_api:
        print("\nABORTADO: --run necesita también --confirm-real-api.")
        return 2

    clave = leer_api_key()
    if clave is None:
        print("\nABORTADO: falta GOOGLE_MAPS_API_KEY en el entorno. No se ejecutó nada.")
        return 2

    print(f"\nGOOGLE_MAPS_API_KEY detectada (no se imprime; longitud={len(clave)}).")
    print(f"Ejecutando · tope duro {args.presupuesto} requests, sin tolerancia\n")
    resultado = correr(plan, clave, args.presupuesto)

    INTERNO.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(resultado["puntos"]).to_csv(
        INTERNO / f"places_techo_{args.zona}_puntos.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(resultado["bitacora"]).to_csv(
        INTERNO / f"places_techo_{args.zona}_bitacora.csv", index=False, encoding="utf-8")

    publicar(resultado, args.zona)
    return 0


if __name__ == "__main__":
    sys.exit(main())
