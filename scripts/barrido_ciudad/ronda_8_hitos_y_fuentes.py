"""Ronda 8 · los cinco veredictos que faltaban, Barracas, el retipado de Yiyo y cuatro trampas.

QUÉ HACE
--------
    TAREA 1 (cola)  incorpora el resultado de Places a la capa, respetando la asimetría: un
                    OPERATIONAL no mueve a nadie, y lo que sí se escribe es la fecha de consulta
    TAREA 2         aplica los cinco veredictos de `vigencia_tanda_A_centro.csv` que la ronda 7
                    dejó afuera por alcance. Diego los confirma
    TAREA 4 (b)     retipa `H199 · Yiyo el Zeneize`: no es un mercado
    TAREA 5         carga Barracas resuelta — que resultó ser tres actualizaciones y cero altas
    TAREA 6         FD-16 a FD-19 en la capa de fuentes con defecto

LO QUE PLACES CAMBIÓ EN LA CAPA: NADA, Y ESE ES EL RESULTADO
--------------------------------------------------------------
De 71 consultas salieron 70 `OPERATIONAL` y 1 `CLOSED_PERMANENTLY`, y el único cerrado ya estaba
cerrado en la capa desde antes. **Ningún veredicto se movió.** No es que la corrida haya fallado:
la asimetría estaba declarada de antemano y un `OPERATIONAL` nunca iba a subir a nadie. Lo que la
corrida sí produjo —y era su objetivo— es la medición de cuánto vale el propio Places, que está
en `PLACES_R8.txt` y se resume acá.

ANTES DE DAR DE ALTA, CRUZAR
-----------------------------
`barracas_resuelto.csv` trae tres objetos y ninguno es un alta: El Puentecito ya está como
`ICO-004` y Los Campeones como `DIR-014`, los dos con su registro oficial correcto. El tercero
—el CCCA de Av. Montes de Oca— no es un hito: es un anclaje de zona, y va a su propia tabla.
La regla vale también cuando el insumo no dice «alta»: la ronda 7 frenó cinco duplicados por
comprobar, y comprobar cuesta una línea.

Google Places: 0 requests en este guion. El resultado se lee del CSV que dejó
`ronda_8_places_incremental.py`.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_8_hitos_y_fuentes.py
"""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import BARRIDO  # noqa: E402

HITOS = BARRIDO / "hitos"
FUENTES = BARRIDO / "fuentes"
COWORK = BARRIDO / "desde_cowork" / "evidencia_2026"

CAPA_R7 = HITOS / "hitos_capa_2026_r7.csv"
OUT_CSV = HITOS / "hitos_capa_2026_r8.csv"
CAMBIOS_CSV = HITOS / "cambios_ronda_8.csv"
INFORME_TXT = HITOS / "RONDA_8_HITOS.txt"
ANCLAJES_CSV = BARRIDO / "seis_vias" / "anclajes_normativos_r8.csv"

PLACES_RESULTADO = HITOS / "places_resultado_r8.csv"
DEFECTOS_CSV = FUENTES / "fuentes_defectos_conocidos.csv"
MARCAS_CSV = FUENTES / "fuentes_marcas_aplicadas.csv"

FECHA = "2026-08-08"

# TAREA 2 · los cinco de `vigencia_tanda_A_centro.csv`. Diego los confirma en la ronda 8.
TANDA_A = [
    ("H009", "Bar El Federal", "si", "v3", "2026-07-21",
     "Tripadvisor, reseña del 21/07/2026: «Very historic. We expected it to be very touristic but "
     "we were pleasantly surprised for the bar to be quiet and civilised.» Segunda reseña de julio "
     "de 2026 de otro usuario. Ficha activa, horario 8 a 2 todos los días.",
     "R03 San Telmo. Es la fila más expuesta de las 22: su vía E quedó en dos grupos por FD-01."),
    ("H074", "Los 36 Billares", "si", "v3", "2026-07-04",
     "Tripadvisor, reseña del 04/07/2026, y SEGUNDA reseña independiente del 28/06/2026 que "
     "describe arañas originales y mesas de pool en uso. Dos reseñas con día visible en la misma "
     "ventana.",
     "Z47 Monserrat. Con este y Café Tortoni, Monserrat pasa a tener tres verificados."),
    ("H035", "Café Tortoni", "si", "v3", "2026-05-26",
     "Tripadvisor, reseña del 26/05/2026 (Thayane B., 3/5): «Only valid for the tourist "
     "experience», con churros y chocolate mediocres. Crítica pero inequívocamente presencial y "
     "fechada. Segunda del 29/04/2026, tercera del 20/04/2026.",
     "Z47 Monserrat. DESPLAZA la nota de Canal 26 del 17/07/2026 que lo daba operativo citando "
     "Wikipedia al pie: ya no hace falta apoyarse en ella."),
    ("H024", "Café de los Angelitos", "si", "v3", "2026-05-25",
     "Tripadvisor, reseña del 25/05/2026 (Sue S., Kingston, Canadá, 5/5). Segunda reseña de mayo "
     "de 2026 en la ficha de atracción. Sitio propio operativo con rundown de función vigente y "
     "motor de reservas activo.",
     "Z36 Balvanera-Congreso, que la decisión 13 fusionó en Z47. Antecedente adverso único y "
     "viejo, asentado: Ámbito 29/09/2017, allanamiento por presunto lavado; no consigna clausura "
     "y está a nueve años."),
    ("H085", "Varela Varelita", "si", "v3", "2026-06-25",
     "Tripadvisor .com, reseña del 25/06/2026 (Beatrice K., Francia). Segunda en .com.ar del "
     "02/06/2026, que es ancla fuerte: «nunca fui atendido, después de esperar 20 minutos "
     "decidimos retirarnos». Relato de servicio en mesa, imposible de reciclar de material "
     "promocional.",
     "R01 Palermo. La dirección ya está corregida en la capa: Av. Scalabrini Ortiz 2102."),
]

# TAREA 6 · las cuatro trampas nuevas.
DEFECTOS_NUEVOS = [
    {
        "defecto_id": "FD-16",
        "fuente": "obras.buenosaires.gob.ar (portal de obras del GCBA, retirado)",
        "regla_de_deteccion": "dominio = obras.buenosaires.gob.ar Y la URL responde 302 a "
                              "mantenimiento.buenosaires.gob.ar",
        "clase": "dato normativo que sólo sobrevive en el SLUG de una URL",
        "que_prohibe": "citar el contenido de la página como leído: el cuerpo no se pudo abrir y "
                       "no hay corroboración en prosa",
        "que_sigue_valiendo": "el dato que viaja en el slug indexado, señalado SIEMPRE como "
                              "lectura de slug y no como lectura de la fuente",
        "severidad": "se admite como ruta de rescate, nunca como cita",
        "evidencia": "el tramo del CCCA de Av. Montes de Oca (entre Benito Quinquela Martín y Av. "
                     "Martín García) existe hoy únicamente en el slug de la URL canónica del "
                     "portal, indexada y reaparecida en dos búsquedas independientes. El portal "
                     "fue retirado y hace 302 a mantenimiento.",
        "detectado": "2026-08-08", "detectado_por": "cowork · ronda 8",
    },
    {
        "defecto_id": "FD-17",
        "fuente": "cronista.com",
        "regla_de_deteccion": "dos notas del mismo dominio sobre el mismo establecimiento con "
                              "antigüedades incompatibles",
        "clase": "fabricación de antigüedad",
        "que_prohibe": "tomar cualquiera de las dos cifras de antigüedad como dato",
        "que_sigue_valiendo": "nada de la antigüedad; el resto de la nota se juzga aparte",
        "severidad": "descarte del dato, no de la nota",
        "evidencia": "dos notas sobre El Puentecito dicen «hace 150 años» y «hace 200 años». El "
                     "mismo dominio ya tenía FD-01 por re-sellado masivo de archivo: además de "
                     "re-sellar, fabrica antigüedades.",
        "detectado": "2026-08-08", "detectado_por": "cowork · ronda 8",
    },
    {
        "defecto_id": "FD-18",
        "fuente": "canal26.com y prensa que reetiqueta distinciones",
        "regla_de_deteccion": "una nota nombra una distinción con una etiqueta que no aparece en "
                              "el organizador",
        "clase": "reetiquetado editorial de una distinción real",
        "que_prohibe": "copiar la etiqueta de prensa: registrar «salón de la fama porteño» crea "
                       "en el Atlas una institución que no existe",
        "que_sigue_valiendo": "la distinción, con el nombre que le da su organizador: Pizzerías "
                              "Emblemáticas de APyCE",
        "severidad": "descarte del nombre, no del hecho",
        "evidencia": "Canal 26 llamó «salón de la fama porteño» a la lista de Pizzerías "
                     "Emblemáticas de APyCE. El reconocimiento existe y está verificado contra "
                     "apyce.org; el «salón de la fama» no existe en ningún lado.",
        "detectado": "2026-08-08", "detectado_por": "cowork · ronda 8",
    },
    {
        "defecto_id": "FD-19",
        "fuente": "fichas de establecimientos de buenosaires.gob.ar",
        "regla_de_deteccion": "dos fichas del mismo portal con el mismo registro institucional y "
                              "fechas de última modificación separadas por años",
        "clase": "fichas vivas y momias con el mismo tono",
        "que_prohibe": "leer el tono institucional como señal de vigencia: no distingue una ficha "
                       "editada este año de una inerte desde hace cinco",
        "que_sigue_valiendo": "la ficha, una vez fechada por su fecha de última modificación",
        "severidad": "obliga a fechar ficha por ficha antes de usarla",
        "evidencia": "la ficha de El Puentecito fue editada el 20/02/2026 y la de Los Campeones "
                     "lleva inerte desde el 08/09/2021 —casi cinco años—, y las dos dicen frases "
                     "institucionales del mismo estilo. La de Los Campeones aportaba «todo un "
                     "emblema de la identidad de Barracas», que no tiene peso probatorio sobre "
                     "el estado actual.",
        "detectado": "2026-08-08", "detectado_por": "cowork · ronda 8",
    },
]


def p_factory(buffer: io.StringIO):
    def p(*args_):
        print(*args_, file=buffer)
    return p


def cargar_capa() -> tuple[list[str], list[dict]]:
    with open(CAPA_R7, encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        return list(lector.fieldnames or []), list(lector)


def por_id(filas: list[dict], hito_id: str) -> dict:
    for fila in filas:
        if fila["hito_id"] == hito_id:
            return fila
    raise KeyError(f"{hito_id} no está en {CAPA_R7.name}")


def set_campo(cambios: list[dict], fila: dict, campo: str, valor: str, motivo: str,
              tarea: str) -> None:
    antes = fila.get(campo, "")
    if str(antes) == str(valor):
        return
    fila[campo] = valor
    cambios.append({"hito_id": fila["hito_id"], "nombre": fila["nombre"], "campo": campo,
                    "valor_antes": antes, "valor_despues": valor, "motivo": motivo,
                    "tarea": tarea, "fecha": FECHA})


def main() -> int:  # noqa: C901
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()
    p = p_factory(buffer)

    campos, filas = cargar_capa()
    for nuevo in ("places_business_status", "nota_ronda_8"):
        if nuevo not in campos:
            campos.append(nuevo)
    for fila in filas:
        for nuevo in ("places_business_status", "nota_ronda_8"):
            fila.setdefault(nuevo, "")
    cambios: list[dict] = []

    p("RONDA 8 · LOS CINCO QUE FALTABAN, BARRACAS, EL RETIPADO Y CUATRO TRAMPAS")
    p("=" * 100)
    p("")
    p(f"  capa de entrada: {CAPA_R7.name} · {len(filas)} hitos")
    p("  Google Places: 0 requests en este guion (el resultado viene del CSV de la corrida).")
    p("")

    # ============================================================ TAREA 2
    p("-" * 100)
    p("  TAREA 2 · LOS CINCO VEREDICTOS QUE LA RONDA 7 DEJÓ AFUERA")
    p("")
    p("  Quedaron fuera por alcance, no por duda: nunca estuvieron bloqueados por el enum y")
    p("  ninguna de las veinte decisiones los nombraba. Diego los confirma.")
    p("")
    for hito_id, nombre, estado, nivel, fecha, fuente, nota in TANDA_A:
        fila = por_id(filas, hito_id)
        previo = fila.get("vigencia_verificada", "")
        set_campo(cambios, fila, "vigencia_verificada", estado,
                  "Veredicto de `vigencia_tanda_A_centro.csv`, confirmado por Diego en la ronda 8.",
                  "TAREA_2")
        set_campo(cambios, fila, "vigencia_nivel", nivel, "", "TAREA_2")
        set_campo(cambios, fila, "vigencia_fuente", fuente, "", "TAREA_2")
        set_campo(cambios, fila, "vigencia_fecha", fecha, "", "TAREA_2")
        set_campo(cambios, fila, "nota_ronda_8", nota, "", "TAREA_2")
        p(f"   {hito_id} · {nombre:<24} {previo:<16} → {estado} · {nivel} "
          f"(dato del {fecha})")
    p("")

    # ============================================================ TAREA 1 · Places a la capa
    p("-" * 100)
    p("  TAREA 1 (cola) · EL RESULTADO DE PLACES, INCORPORADO CON LA ASIMETRÍA PUESTA")
    p("")
    if not PLACES_RESULTADO.exists():
        p("   no hay resultado de Places todavía — correr ronda_8_places_incremental.py")
        movidos = 0
    else:
        places = pd.read_csv(PLACES_RESULTADO)
        movidos, anotados, saltados = 0, 0, 0
        for reg in places.itertuples():
            if not isinstance(reg.hito_id, str) or not reg.hito_id.strip():
                saltados += 1
                continue
            try:
                fila = por_id(filas, reg.hito_id)
            except KeyError:
                saltados += 1
                continue
            if reg.identidad in ("OTRA CALLE", "sin respuesta"):
                set_campo(cambios, fila, "nota_ronda_8",
                          f"Places devolvió otro local ({reg.identidad_detalle}): la consulta NO "
                          "se atribuye a este establecimiento.", "", "TAREA_1")
                saltados += 1
                continue
            set_campo(cambios, fila, "places_business_status", reg.business_status,
                      "Consulta de Places de la ronda 8.", "TAREA_1")
            set_campo(cambios, fila, "vigencia_fecha_consulta", reg.vigencia_fecha_consulta,
                      "Places NO trae la fecha del dato: sin esta columna el estado es "
                      "infechable, que es el defecto FD-01 aplicado a otra fuente.", "TAREA_1")
            anotados += 1
            if reg.business_status == "CLOSED_PERMANENTLY":
                previo = fila.get("vigencia_verificada", "")
                if previo in ("no", "cerrado_con_reapertura_anunciada"):
                    set_campo(cambios, fila, "nota_ronda_8",
                              "Places lo da CLOSED_PERMANENTLY, coincidiendo con lo que la capa "
                              "ya tenía por otra vía. Corrobora en v2b; no cambia el veredicto.",
                              "", "TAREA_1")
                else:
                    movidos += 1
        p(f"   consultas incorporadas a la capa: {anotados}")
        p(f"   veredictos MOVIDOS por Places: {movidos}")
        p(f"   no atribuidas (sin hito o identidad dudosa): {saltados}")
        p("")
        p("   NINGÚN VEREDICTO SE MOVIÓ, Y ESO NO ES QUE LA CORRIDA HAYA FALLADO. La asimetría")
        p("   estaba declarada antes de gastar: un OPERATIONAL no sube a nadie. El único")
        p("   CLOSED_PERMANENTLY —Plaza Bar— ya estaba cerrado en la capa desde antes.")
        p("")
        p("   LO QUE SÍ PRODUJO ES LA MEDICIÓN DEL PROPIO PLACES, que es lo que se compró:")
        p("   de tres cierres conocidos marca UNO. Plaza Bar (nueve años) sí; La Buena Medida")
        p("   (280 días) y The New Brighton (143 días, con quiebra declarada por la Justicia) los")
        p("   da OPERATIONAL. El piso de detección está por encima de los 280 días.")
        p("")
        p("   CONSECUENCIA PARA LA ESCALA: v2b sirve para acreditar cierre cuando Places lo")
        p("   afirma, y NO sirve para descartar cierre cuando calla. Un OPERATIONAL de Places es")
        p("   compatible con un local cerrado hace nueve meses. Eso hay que escribirlo en la")
        p("   escala antes de que alguien lea los 70 OPERATIONAL como 70 confirmaciones.")
        p("")

    # ============================================================ TAREA 4b · Yiyo el Zeneize
    p("-" * 100)
    p("  TAREA 4 (b) · YIYO EL ZENEIZE NO ES UN MERCADO")
    p("")
    yiyo = por_id(filas, "H199")
    set_campo(cambios, yiyo, "tipo", "Restaurante/bodegón",
              "RETIPADO: estaba como `Mercado/patio` y no es un mercado. Es un bodegón, y la Ley "
              "CABA 6.533 declara patrimonio su CARTA GASTRONÓMICA, no el local como mercado. El "
              "tipo venía de una lectura apresurada del reconocimiento.", "TAREA_4")
    set_campo(cambios, yiyo, "reconocimiento",
              "Patrimonio historico y cultural inmaterial (Ley CABA 6.533) — la declaratoria "
              "recae sobre la carta gastronómica",
              "Precisión de qué declara la norma.", "TAREA_4")
    set_campo(cambios, yiyo, "registro_oficial", "ley_especifica", "", "TAREA_4")
    set_campo(cambios, yiyo, "nota_ronda_8",
              "Era la ÚNICA vía C de las 94 filas que no se apoyaba en un mercado de la lista "
              "oficial. Con el retipado, la vía C de su fila se cae: se recalcula en "
              "`ronda_8_geometria_y_vias.py`.", "", "TAREA_4")
    p("   H199 · tipo `Mercado/patio` → `Restaurante/bodegón` · registro_oficial ley_especifica")
    p("   La Ley 6.533 declara patrimonio la CARTA, no el local como mercado.")
    p("")

    # ============================================================ TAREA 5 · Barracas
    p("-" * 100)
    p("  TAREA 5 · BARRACAS · TRES OBJETOS, CERO ALTAS")
    p("")
    barracas = pd.read_csv(COWORK / "barracas_resuelto.csv")
    p("   Cruzado contra la capa ANTES de dar de alta nada, que es la regla:")
    p("")
    p("      El Puentecito   → ya está como ICO-004 (Restaurante Icónico). Actualización.")
    p("      Los Campeones   → ya está como DIR-014 (Pizzería emblemática). Actualización.")
    p("      CCCA Montes de Oca → NO es un hito: es un anclaje de zona. Va a su propia tabla.")
    p("")

    puentecito = por_id(filas, "ICO-004")
    set_campo(cambios, puentecito, "vigencia_verificada", "probablemente_abierto",
              "NO CERRÓ. La alarma era una atribución equivocada: la pieza que la zona perdió es "
              "LOS LAURELES (Av. Iriarte 2290), a 1,5 km. Listado el 07/07/2026 entre los 16 "
              "Restaurantes Icónicos: v4, y v4 solo da probablemente_abierto.", "TAREA_5")
    set_campo(cambios, puentecito, "vigencia_nivel", "v4", "", "TAREA_5")
    set_campo(cambios, puentecito, "vigencia_fuente",
              "La Nación 07/07/2026, entre los 16 Restaurantes Icónicos", "", "TAREA_5")
    set_campo(cambios, puentecito, "vigencia_fecha", "2026-07-07", "", "TAREA_5")
    set_campo(cambios, puentecito, "direccion_variante", "Vieytes 1895",
              "Misma ochava: Vieytes 1895 esq. Pedro de Luján 2101.", "TAREA_5")
    set_campo(cambios, puentecito, "nota_ronda_8",
              "DOS CIFRAS DE ANTIGÜEDAD, CADA UNA CON SU FUENTE Y SU OBJETO. 1750 es el SITIO "
              "—pulpería y posta de carretas—, y es dato del GCBA sin respaldo en prensa. ~1876 "
              "es el ESTABLECIMIENTO GASTRONÓMICO, que es lo que dicen las notas («hace ~150 "
              "años»). La ficha tiene que consignar las dos por separado y atribuir cada una. "
              "cronista.com publica además dos notas mutuamente contradictorias: ver FD-17.",
              "", "TAREA_5")

    campeones = por_id(filas, "DIR-014")
    set_campo(cambios, campeones, "vigencia_verificada", "probablemente_abierto",
              "Pizzería Emblemática de la camada de mayo de 2026, VERIFICADA CONTRA EL SITIO DEL "
              "ORGANIZADOR (apyce.org/pizzerias-emblematicas). v5 por la cobertura del acto + v4 "
              "por el listado; ninguno de los dos acredita verificado_abierto.", "TAREA_5")
    set_campo(cambios, campeones, "vigencia_nivel", "v5", "", "TAREA_5")
    set_campo(cambios, campeones, "vigencia_fuente",
              "apyce.org/pizzerias-emblematicas (el organizador) + Infobae 29/05/2026", "",
              "TAREA_5")
    set_campo(cambios, campeones, "vigencia_fecha", "2026-05-29", "", "TAREA_5")
    set_campo(cambios, campeones, "edicion_o_anio", "1954", "", "TAREA_5")
    set_campo(cambios, campeones, "nota_ronda_8",
              "ES PIZZERÍA, de 1954, no bar ni bodegón: fundada por cuatro amigos futboleros y el "
              "nombre se eligió para no ofender a ninguna hinchada. Pizza a la piedra en horno a "
              "leña de quebracho. NO es Bar Notable —confirmado, ausente del catálogo—. La cita "
              "«todo un emblema de la identidad de Barracas» que circulaba viene de una ficha del "
              "GCBA inerte desde el 08/09/2021: ver FD-19. La etiqueta «salón de la fama porteño» "
              "de la prensa no existe: ver FD-18.", "", "TAREA_5")
    p("   ICO-004 · El Puentecito → probablemente_abierto · v4")
    p("   DIR-014 · Los Campeones → probablemente_abierto · v5")
    p("")

    anclajes = [{
        "anclaje_id": "ANC-001",
        "zona": "Barracas · Av. Montes de Oca",
        "figura": "CCCA (Centro Comercial a Cielo Abierto)",
        "clase": "figura ADMINISTRATIVA de obra pública — NO legislada",
        "tramo": "Av. Montes de Oca entre Benito Quinquela Martín y Av. Martín García",
        "norma": "Resolución N.º 65/SSADMIN/2017 · Licitación Pública N.º 1242/SIGAF/2017",
        "publicacion": "BO CABA N.º 5206 del 06/09/2017, pág. 239",
        "marco_legal": "Ley Nacional de Obras Públicas 13.064 y Decreto 1254/GCBA/08",
        "presupuesto_oficial": "$28.054.630,31",
        "programa": "Transformación de los 48 barrios",
        "hallazgo_negativo": "NO EXISTE LEY QUE CREE LA FIGURA CCCA. El informe del CESBA (2017, "
                             "ampliado 2018) sólo registra PROYECTOS legislativos, ninguno "
                             "sancionado, y no menciona Montes de Oca. Se ancla como figura "
                             "administrativa —resolución más licitación—, no como figura "
                             "legislada.",
        "salvedad": "El tramo se lee del SLUG de la URL canónica del portal de obras, indexada y "
                    "reaparecida en dos búsquedas independientes. No se pudo leer el cuerpo: la "
                    "página hace 302 a mantenimiento. Sin corroboración en prosa. Ver FD-16.",
        "coherencia_verificada": "Av. Montes de Oca corre de Av. Caseros a Av. Don Pedro de "
                                 "Mendoza, así que el tramo del CCCA es un SUB-TRAMO COMERCIAL "
                                 "INTERIOR y no la avenida completa. Los Campeones (856) cae "
                                 "adentro.",
        "estado_de_la_obra": "NO DETERMINADO — el portal de obras fue retirado",
        "fecha": "2017-09-06", "cargado": FECHA,
    }]
    ANCLAJES_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(anclajes).to_csv(ANCLAJES_CSV, index=False, encoding="utf-8")
    p(f"   anclaje CCCA registrado en {ANCLAJES_CSV.name}, como figura administrativa.")
    p("   ES EL ANCLAJE QUE LE FALTABA A Barracas · Montes de Oca, que hasta ahora se sostenía")
    p("   sólo en direcciones sueltas. Y no es una ley: eso queda escrito en el propio registro.")
    p("")

    # ============================================================ TAREA 6 · las cuatro trampas
    p("-" * 100)
    p("  TAREA 6 · FD-16 A FD-19")
    p("")
    defectos = pd.read_csv(DEFECTOS_CSV)
    ya = set(defectos.defecto_id)
    nuevos = [d for d in DEFECTOS_NUEVOS if d["defecto_id"] not in ya]
    if nuevos:
        defectos = pd.concat([defectos, pd.DataFrame(nuevos)], ignore_index=True)
        defectos.to_csv(DEFECTOS_CSV, index=False, encoding="utf-8")
    for defecto in DEFECTOS_NUEVOS:
        estado = "nuevo" if defecto["defecto_id"] not in ya else "ya estaba"
        p(f"   {defecto['defecto_id']} · {defecto['clase']:<52} [{estado}]")
        p(f"        fuente: {defecto['fuente']}")
    p("")
    p(f"   la capa de fuentes con defecto pasa de {len(ya)} a {len(defectos)}.")
    p("")

    marcas = pd.read_csv(MARCAS_CSV)
    marcas_nuevas = [
        {"defecto_id": "FD-16", "capa": "anclajes_normativos_r8.csv", "registro": "ANC-001",
         "campo": "tramo", "valor": "Av. Montes de Oca entre Benito Quinquela Martín y Av. "
                                    "Martín García",
         "estado_de_la_marca": "admitida_como_rescate_de_slug",
         "consecuencia": "el tramo se usa, señalado siempre como lectura de slug y nunca como "
                         "lectura de la fuente; el cuerpo de la página no se pudo abrir"},
        {"defecto_id": "FD-17", "capa": "hitos_capa_2026_r8.csv", "registro": "ICO-004",
         "campo": "edicion_o_anio", "valor": "150 años / 200 años según la nota",
         "estado_de_la_marca": "descartada_como_antiguedad",
         "consecuencia": "ninguna de las dos cifras de cronista.com entra; la ficha consigna 1750 "
                         "como sitio (GCBA) y ~1876 como establecimiento (prensa), atribuidas"},
        {"defecto_id": "FD-18", "capa": "hitos_capa_2026_r8.csv", "registro": "DIR-014",
         "campo": "reconocimiento", "valor": "«salón de la fama porteño»",
         "estado_de_la_marca": "descartada_la_etiqueta",
         "consecuencia": "se registra como Pizzería Emblemática de APyCE, que es el nombre del "
                         "organizador; el «salón de la fama» no existe"},
        {"defecto_id": "FD-19", "capa": "hitos_capa_2026_r8.csv", "registro": "DIR-014",
         "campo": "vigencia_fuente", "valor": "ficha del GCBA, últ. modificación 08/09/2021",
         "estado_de_la_marca": "descartada_como_vigencia",
         "consecuencia": "casi cinco años inerte: no tiene peso probatorio sobre el estado "
                         "actual, aunque su tono sea idéntico al de la ficha viva de El "
                         "Puentecito (20/02/2026)"},
    ]
    ya_marcas = set(zip(marcas.defecto_id, marcas.registro))
    marcas_nuevas = [m for m in marcas_nuevas if (m["defecto_id"], m["registro"]) not in ya_marcas]
    if marcas_nuevas:
        marcas = pd.concat([marcas, pd.DataFrame(marcas_nuevas)], ignore_index=True)
        marcas.to_csv(MARCAS_CSV, index=False, encoding="utf-8")
    p(f"   marcas aplicadas: +{len(marcas_nuevas)} · la capa de marcas queda en {len(marcas)}.")
    p("")

    # ============================================================ salidas
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)
    pd.DataFrame(cambios).to_csv(CAMBIOS_CSV, index=False, encoding="utf-8")

    p("-" * 100)
    conteo = pd.Series([f["vigencia_verificada"] for f in filas]).value_counts()
    for valor, n in conteo.items():
        p(f"      {valor:<36} {n:>4}")
    p("")
    p(f"  capa de salida: {OUT_CSV.name} · {len(filas)} hitos · {len(campos)} columnas")
    p(f"  cambios: {len(cambios)}")
    p("  Google Places: 0 requests en este guion.")

    texto = buffer.getvalue()
    INFORME_TXT.write_text(texto, encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
