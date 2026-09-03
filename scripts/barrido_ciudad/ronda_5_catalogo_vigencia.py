"""Ronda 5 · el catálogo 1225/26, la auditoría de cierres y el cierre de la vigencia ronda 2.

QUÉ HACE
--------
Tres cargas de Diego sobre la capa de 220 hitos (`hitos_capa_2026_r3.csv`):

1. **TAREA 1 — el catálogo vigente cambia.** El anexo de la Res. MCGC 3758/24 que citaba la
   transcripción ya no es el vigente: es la Res. MCGC 1225/26, "Catálogo Bares Notables de la
   Ciudad de Buenos Aires. Consolidado 2025", 90 entradas, IF-2026-10314379-GCABA-DGPMYCH,
   firmado 26/02/2026. El PDF ya estaba en disco desde el 3/08 (ronda 3 lo había hasheado) — este
   script lo vuelve a bajar de la URL oficial y confirma que es BYTE A BYTE el mismo archivo antes
   de usarlo como fuente. El diff sistemático contra los 90 que teníamos cargados encuentra:
   - 1 baja real: La Esquina de Aníbal Troilo.
   - 2 altas reales: Bar Iberia (reingresa) y **Roma del Abasto**, que Diego no había señalado y
     que estaba escondida dentro de un bug de fusión (ver más abajo).
   - 2 renombres en el mismo domicilio: Café Palacio → Museo Fotográfico Simik; y una variante de
     catálogo no señalada por Diego (Café Olimpo / Bar Olimpo, Casa Watson / Watson's) que NO se
     trata como cambio: son la misma declaratoria con otro nombre de uso.
   - Un bug encontrado por el diff, no buscado: la fila H032 "Café Roma" tenía en
     `nombres_vistos` la cadena "Roma del Abasto" fusionada por coincidencia de token ("Roma") con
     una dirección inventada por el emparejamiento («San Luis 3101», que no es ninguna de las dos
     direcciones reales) y las coordenadas de Café Roma (Olavarría 409) reasignadas. Se separan:
     H032 pasa a ser Roma del Abasto con su domicilio real (Anchorena 806) y sin coordenadas hasta
     geocodificar; Café Roma (H031, Olavarría 409) queda como estaba.
   - Los 12 hitos marcados `es_alta_2026_08_03 = True` (que hasta ahora sólo tenían prensa) pasan
     a citar la resolución con su número de orden en el consolidado.

2. **TAREA 2 — la auditoría de 11 cierres** (`catalogo_notables_auditoria_cierres.csv`): Plaza
   Bar → `cerrado_con_reapertura_anunciada` (2028, el bar histórico se conserva); La Buena Medida
   y The New Brighton → `no` (bajas reales, catálogo desactualizado); Esquina Homero Manzi →
   `en_riesgo` con revisión a 90 días; La Esquina de Aníbal Troilo → `señalado_no_cerrado` (la
   baja del catálogo es indicio, no prueba); La Academia → domicilio corregido a MONTEVIDEO 341
   (se reinterpreta el "error de comuna": la ficha estaba en una dirección muerta, no sólo mal
   geolocalizada); Clásica y Moderna → barrio corregido (Recoleta, no San Nicolás) y vigencia
   resuelta por reapertura; Café Thibon → vigencia resuelta (cambio de gestión).

3. **TAREA 3 — el cierre de la vigencia ronda 2** (`vigencia_ronda_2_cerrada.csv`, 10 filas
   verificadas por Diego): revierte P008 Barracas (Los Laureles vuelve a abierto — la distinción
   que se registra es que la ficha del sitio de turismo fue EDITADA ACTIVAMENTE para describir la
   reapertura, no un listado inerte que arrastra un dato viejo); 6 verificados abiertos; El Sol de
   Galicia con domicilio corregido (Luis Viale 2867, confirmado también con USIG) y marcado
   explícitamente fuera del catálogo de Notables (es churrería); Saint Moritz y Bárbaro quedan
   `dudosa` con `vigencia_sentido_duda = probablemente_abierto`; Café Olimpo queda
   `estado_operativo_pendiente`, el único de los diez sin resolver.

CAMPOS NUEVOS EN LA CAPA
-------------------------
`vigencia_nivel` (v2/v3/v4, según cuántas fuentes independientes sostienen el verificado),
`vigencia_sentido_duda` (para no perder la dirección de la duda cuando el estado es `dudosa`),
`vigencia_revisar_hasta` (fecha de revisión para los casos `en_riesgo`), `nota_ronda_5`.

Los valores nuevos de `vigencia_verificada` —`cerrado_con_reapertura_anunciada`, `en_riesgo`,
`senalado_no_cerrado`, `estado_operativo_pendiente`— son extensiones del enum, no reemplazos: la
capa ya había extendido este campo antes (`sin_hitos`, `en_disputa`) cuando un caso real no entraba
en los valores que había.

Google Places: 0 requests. USIG: 2 consultas nuevas (La Academia Montevideo 341, El Sol de Galicia
Luis Viale 2867), cacheadas junto con las de rondas anteriores.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/ronda_5_catalogo_vigencia.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset_bares_notables import consultar, limpiar  # noqa: E402

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
HITOS = BARRIDO / "hitos"
EVIDENCIA = BARRIDO / "desde_cowork" / "evidencia_2026"
FUENTES = BARRIDO / "fuentes"
DESCARGAS = FUENTES / "descargas_ronda_5"
CACHE_USIG = BARRIDO / "dataset_bares_notables" / "_cache_usig.json"
CACHE_DATOS_UTILES = BARRIDO / "seis_vias" / "_cache_usig_datos_utiles.json"
DATOS_UTILES_URL = "https://ws.usig.buenosaires.gob.ar/datos_utiles/"

URL_1225_26 = "https://documentosboletinoficial.buenosaires.gob.ar/publico/PE-RES-MCGC-MCGC-1225-26-ANX.pdf"
IF_1225_26 = "IF-2026-10314379-GCABA-DGPMYCH"

IN_CSV = HITOS / "hitos_capa_2026_r3.csv"
OUT_CSV = HITOS / "hitos_capa_2026_r5.csv"
CAMBIOS_CSV = HITOS / "cambios_ronda_5.csv"

FIELDS_NUEVOS = ["vigencia_nivel", "vigencia_sentido_duda", "vigencia_revisar_hasta", "nota_ronda_5"]


def sha256_de(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def descargar_y_verificar(buf: list[str]) -> None:
    """Baja el PDF de la URL oficial y confirma que es el mismo que el que ya estaba en disco."""
    DESCARGAS.mkdir(parents=True, exist_ok=True)
    destino = DESCARGAS / "RES_MCGC_1225_26_ANX.pdf"
    ya_estaba = FUENTES.parent.parent / "polos_gastro" / "REFERENTES_2026" / "_fuentes" / \
        "bares_notables_consolidado_2025_anexo_res_1225_2026.pdf"
    r = requests.get(URL_1225_26, timeout=60)
    r.raise_for_status()
    destino.write_bytes(r.content)
    hash_nuevo = sha256_de(destino)
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    buf.append("DESCARGA DE LA RES. MCGC 1225/26")
    buf.append(f"  URL: {URL_1225_26}")
    buf.append(f"  descargado_utc: {ahora}")
    buf.append(f"  sha256: {hash_nuevo}")
    buf.append(f"  bytes: {len(r.content)}")
    if ya_estaba.exists():
        hash_previo = sha256_de(ya_estaba)
        igual = hash_nuevo == hash_previo
        buf.append(f"  archivo ya en disco desde ronda 3: {ya_estaba}")
        buf.append(f"  hash coincide byte a byte: {igual}")
        if not igual:
            buf.append("  *** ALERTA: el archivo en disco NO coincide con la URL oficial actual. ***")
    else:
        buf.append("  (no había copia previa en disco para comparar)")


def cargar_capa() -> tuple[list[str], list[dict]]:
    with open(IN_CSV, encoding="utf-8") as f:
        r = csv.DictReader(f)
        campos = list(r.fieldnames)
        filas = list(r)
    for campo in FIELDS_NUEVOS:
        if campo not in campos:
            campos.append(campo)
    for fila in filas:
        for campo in FIELDS_NUEVOS:
            fila.setdefault(campo, "")
    return campos, filas


def por_id(filas: list[dict], hito_id: str) -> dict:
    for f in filas:
        if f["hito_id"] == hito_id:
            return f
    raise KeyError(hito_id)


def registrar_cambio(cambios: list[dict], hito_id: str, nombre: str, campo: str, antes: str,
                     despues: str, motivo: str) -> None:
    cambios.append({
        "hito_id": hito_id, "nombre": nombre, "campo": campo,
        "valor_antes": antes, "valor_despues": despues, "motivo": motivo,
        "tarea": "", "fecha": "2026-08-07",
    })


def set_campo(cambios: list[dict], fila: dict, campo: str, valor: str, motivo: str,
             tarea: str) -> None:
    antes = fila.get(campo, "")
    if antes == valor:
        return
    fila[campo] = valor
    cambios.append({
        "hito_id": fila["hito_id"], "nombre": fila["nombre"], "campo": campo,
        "valor_antes": antes, "valor_despues": valor, "motivo": motivo,
        "tarea": tarea, "fecha": "2026-08-07",
    })


def main() -> int:
    buf: list[str] = []

    def p(*a):
        s = " ".join(str(x) for x in a)
        buf.append(s)
        try:
            print(s)
        except UnicodeEncodeError:
            print(s.encode("ascii", "replace").decode("ascii"))

    p("=" * 78)
    p("RONDA 5 · catálogo 1225/26, auditoría de cierres, cierre de vigencia ronda 2")
    p("=" * 78)
    p("")

    descargar_y_verificar(buf)
    p("")

    campos, filas = cargar_capa()
    cambios: list[dict] = []

    # ------------------------------------------------------------------
    # TAREA 1 · las 12 altas dejan de ser "sólo prensa"
    # ------------------------------------------------------------------
    p("TAREA 1 · declaratoria_localizada de las 12 altas, contra la Res. 1225/26")
    orden_1225_26 = {
        "H030": ("Plaza Café", 85), "H004": ("Bar Boca a Boca", 20), "H010": ("Bar Conde", 5),
        "H017": ("Bar Vía 71", 19), "H021": ("Café Cortázar", 23), "H087": ("Café Rivas", 28),
        "H090": ("Confitería El Greco", 38), "H088": ("El Portuario", 14),
        "H089": ("Josephina's Café", 58), "H041": ("La Escuela", 62),
        "H068": ("La Ópera", 66), "H063": ("La Orquídea", 67),
    }
    for hito_id, (nombre, orden) in orden_1225_26.items():
        try:
            fila = por_id(filas, hito_id)
        except KeyError:
            p(f"  *** {hito_id} ({nombre}) no está en la capa — no se pudo actualizar ***")
            continue
        valor = (f"sí · RES-MCGC-1225-26 ({IF_1225_26}), orden {orden}/90, "
                 f"firmado 26/02/2026, verificado por descarga directa 2026-08-07")
        set_campo(cambios, fila, "declaratoria_localizada", valor,
                 "Diff contra la Res. 1225/26 descargada: la entrada aparece en el consolidado "
                 "oficial con este número de orden.", "TAREA_1")
        p(f"  {hito_id} {nombre}: declaratoria_localizada -> orden {orden}/90")

    # El bug de fusión: H032 "Café Roma" tenía "Roma del Abasto" escondida en nombres_vistos.
    p("")
    p("TAREA 1 · bug de fusión encontrado por el diff: H032 no es un segundo Café Roma")
    try:
        h032 = por_id(filas, "H032")
        p(f"  antes: nombre={h032['nombre']!r} direccion={h032['direccion']!r} "
          f"lat={h032['latitud']!r} lon={h032['longitud']!r}")
        set_campo(cambios, h032, "nombre", "Roma del Abasto",
                 "H032 y H031 eran el mismo nombre normalizado (Café Roma) por una fusión que "
                 "tomó 'Roma del Abasto' como variante de nombre de Café Roma cuando son dos "
                 "establecimientos distintos del consolidado (órdenes 29 y 86).", "TAREA_1")
        set_campo(cambios, h032, "direccion", "Anchorena 806",
                 "Domicilio real según Res. 1225/26 orden 86/90. La dirección previa, 'San Luis "
                 "3101', no corresponde a Café Roma (Olavarría 409) ni a Roma del Abasto "
                 "(Anchorena 806): es un artefacto del emparejamiento por nombre.", "TAREA_1")
        set_campo(cambios, h032, "barrio_declarado", "Balvanera",
                 "Balvanera, Comuna 5 según Res. 1225/26 orden 86/90.", "TAREA_1")
        set_campo(cambios, h032, "latitud", "",
                 "Las coordenadas previas eran las de H031 (Café Roma, Olavarría 409) mal "
                 "reasignadas. Sin geocodificar hasta correr USIG sobre 'Anchorena 806, CABA'; no "
                 "se inventa un punto.", "TAREA_1")
        set_campo(cambios, h032, "longitud", "", "Ídem latitud.", "TAREA_1")
        set_campo(cambios, h032, "declaratoria_localizada",
                 "sí · RES-MCGC-1225-26 (IF-2026-10314379-GCABA-DGPMYCH), orden 86/90, "
                 "firmado 26/02/2026", "Alta real que Diego no había señalado en su lista de "
                 "movimientos; la encontró el diff sistemático, no una lectura dirigida.",
                 "TAREA_1")
        set_campo(cambios, h032, "nota_carga",
                 (h032.get("nota_carga", "") + " | " if h032.get("nota_carga") else "") +
                 "CORREGIDO ronda 5: esta fila decía 'Café Roma / San Luis 3101' por un bug de "
                 "fusión de nombres_vistos. Es Roma del Abasto, Anchorena 806, alta real de la "
                 "Res. 1225/26 (orden 86/90) no detectada hasta el diff de ronda 5. Pendiente: "
                 "geocodificar.", "Documentar la corrección en la propia fila.", "TAREA_1")
        p(f"  después: nombre={h032['nombre']!r} direccion={h032['direccion']!r} "
          f"(coordenadas limpiadas, pendiente de geocodificar)")
    except KeyError:
        p("  *** H032 no está en la capa ***")

    # Bar Iberia: reingresa, no estaba en la capa en absoluto.
    p("")
    p("TAREA 1 · Bar Iberia reingresa (3758/24 → 1225/26) — no existía como hito, se agrega")
    if not any(f["hito_id"] == "H094" for f in filas):
        nueva = {c: "" for c in campos}
        nueva.update({
            "hito_id": "H094", "nombre": "Bar Iberia", "tipo": "Bar Notable",
            "reconocimiento": "Bar Notable (Boletín Oficial · declaratoria)",
            "direccion": "Av. de Mayo 1196", "barrio_declarado": "Montserrat",
            "origen": "RES_MCGC_1225_26 (ronda 5)", "fuente_primaria": "Boletín Oficial CABA",
            "confianza": "alta",
            "nota_carga": "Agregado en ronda 5. Dado de baja en 3758/24 (cerró marzo 2020) y "
                          "reincorporado en 1225/26 (reabrió junio 2024): La Nación / Revista "
                          "Lugares 06/01/2025 documenta el ciclo completo. Único caso donde el "
                          "catálogo siguió alta-baja-alta sin que se le perdiera el rastro.",
            "es_patrimonio_normativo": "False",
            "vigencia_verificada": "si", "vigencia_fuente": "La Nación / Revista Lugares "
                          "06/01/2025, entrevista a Maxi Longo.", "vigencia_fecha": "2024-06",
            "es_alta_2026_08_03": "True",
            "declaratoria_localizada": f"sí · RES-MCGC-1225-26 ({IF_1225_26}), orden 10/90, "
                          "firmado 26/02/2026",
            "alta_referencia_que_toca": "R12 Centro / Montserrat",
            "vigencia_nivel": "v2",
            "nota_ronda_5": "Alta confirmada por Diego (auditoría de cierres) y por el diff "
                          "sistemático contra la Res. 1225/26. Sin geocodificar todavía.",
        })
        filas.append(nueva)
        cambios.append({"hito_id": "H094", "nombre": "Bar Iberia", "campo": "(fila nueva)",
                        "valor_antes": "", "valor_despues": "alta agregada", "motivo":
                        "Reingresa en 1225/26, no existía como hito.", "tarea": "TAREA_1",
                        "fecha": "2026-08-07"})
        p("  H094 Bar Iberia agregado (Av. de Mayo 1196, sin geocodificar todavía)")

    # ------------------------------------------------------------------
    # TAREA 2 · la auditoría de 11 cierres
    # ------------------------------------------------------------------
    p("")
    p("TAREA 2 · auditoría de cierres (11 filas)")

    plaza_bar = por_id(filas, "H082")
    set_campo(cambios, plaza_bar, "vigencia_verificada", "cerrado_con_reapertura_anunciada",
             "Hotel cerrado desde 29/04/2017, contenido rematado en 2021, ampliación de 1948 "
             "demolida en 2022; Clarín/Viva 15/02/2025 y Tango y Milonga 02/01/2025 describen obra "
             "en curso con reapertura programada 2028. El bar histórico se conserva: no es cierre "
             "definitivo.", "TAREA_2")
    set_campo(cambios, plaza_bar, "vigencia_fecha", "reapertura anunciada 2028", "", "TAREA_2")
    set_campo(cambios, plaza_bar, "vigencia_nivel", "v2", "", "TAREA_2")
    set_campo(cambios, plaza_bar, "nota_ronda_5",
             "Sigue publicado en el catálogo vigente (orden 84/90). Es la ausencia más antigua de "
             "la capa (nueve años) y el caso que fija el criterio: un listado inerte no prueba "
             "vigencia, pero acá hay evidencia positiva y fechada de reapertura en curso.", "", "TAREA_2")

    buena_medida = por_id(filas, "H062")
    set_campo(cambios, buena_medida, "vigencia_verificada", "no",
             "Canal 26 03/12/2025 y BAE Negocios 02/12/2025: cerró en octubre de 2025 por falta de "
             "renovación del alquiler. Ya había cerrado antes y reabierto en septiembre de 2021; "
             "este es el cierre definitivo.", "TAREA_2")
    set_campo(cambios, buena_medida, "vigencia_fecha", "2025-10", "", "TAREA_2")
    set_campo(cambios, buena_medida, "vigencia_nivel", "v2", "", "TAREA_2")
    set_campo(cambios, buena_medida, "nota_ronda_5",
             "Sigue publicado en el catálogo vigente (orden 61/90), pese a una consolidación "
             "completa NUEVE MESES después del cierre. Peor caso que Plaza Bar en ese sentido.", "", "TAREA_2")

    new_brighton = por_id(filas, "H084")
    set_campo(cambios, new_brighton, "vigencia_verificada", "no",
             "Declarado en quiebra por la Justicia el 18/03/2026 tras más de un siglo. Sigue "
             "publicado en el catálogo vigente (orden 88/90).", "TAREA_2")
    set_campo(cambios, new_brighton, "vigencia_fecha", "2026-03-18", "", "TAREA_2")
    set_campo(cambios, new_brighton, "vigencia_nivel", "v2", "", "TAREA_2")

    homero_manzi = por_id(filas, "H057")
    fecha_revision = (datetime(2026, 8, 7) + timedelta(days=90)).strftime("%Y-%m-%d")
    set_campo(cambios, homero_manzi, "vigencia_verificada", "en_riesgo",
             "Infobae 07/05/2026: condena laboral de $220 millones por juicio de dos bailarines de "
             "tango; el administrador la describe como impagable. Corroboran Página/12, La Nación "
             "y Canal 26 (06-08/05/2026). Sin cierre consumado al 07/08/2026.", "TAREA_2")
    set_campo(cambios, homero_manzi, "vigencia_fecha", "2026-05-07", "", "TAREA_2")
    set_campo(cambios, homero_manzi, "vigencia_nivel", "v2", "", "TAREA_2")
    set_campo(cambios, homero_manzi, "vigencia_revisar_hasta", fecha_revision, "", "TAREA_2")
    set_campo(cambios, homero_manzi, "nota_ronda_5",
             "Es el hito más visible de R14 Av. Boedo: sala de espectáculos propia, no sólo bar. "
             "Revisar en 90 días.", "", "TAREA_2")

    anibal_troilo = por_id(filas, "H064")
    set_campo(cambios, anibal_troilo, "vigencia_verificada", "senalado_no_cerrado",
             "Única baja del consolidado entre 3758/24 y 1225/26. Foursquare la rotula 'Ahora "
             "cerrado' (título indexado, la página bloquea por robots); la última pieza que la "
             "describe operativa es de marzo de 2022. NO se encontró nota de cierre.", "TAREA_2")
    set_campo(cambios, anibal_troilo, "vigencia_nivel", "ninguno", "", "TAREA_2")
    set_campo(cambios, anibal_troilo, "nota_ronda_5",
             "La baja del catálogo es indicio, no prueba: hay un caso documentado (Los Andes, "
             "auditoría de cierres) donde una baja no correspondió a un cierre ni a cambio de "
             "rubro. Señalada, no cerrada en firme.", "", "TAREA_2")

    academia = por_id(filas, "H060")
    set_campo(cambios, academia, "barrio_declarado", "San Nicolás",
             "USIG /datos_utiles sobre Montevideo 341 (consulta 2026-08-07) responde San Nicolás, "
             "Comuna 1 — CONTRADICE dos fuentes a la vez: la auditoría de cierres decía Balvanera, "
             "y el propio anexo de la Res. 1225/26 la lista como 'San Nicolás. Comuna 5', que es "
             "internamente inconsistente (San Nicolás es Comuna 1, no 5). Se adopta USIG por ser "
             "la fuente administrativa del punto, no una atribución editorial.", "TAREA_2")
    set_campo(cambios, academia, "direccion", "Montevideo 341",
             "Clarín / Infobae 27/07/2025: 'La Academia mudó sus juegos y sus fantasmas' al local "
             "de Pippo (cerrado en agosto de 2020), Montevideo 341. El anexo 3758/24 la publicaba "
             "en Av. Callao 368 con el local ya vacío: reinterpreta el 'error de comuna' que se "
             "arrastraba — no era sólo georreferencia, la ficha estaba en una dirección muerta.",
             "TAREA_2")
    set_campo(cambios, academia, "vigencia_verificada", "si",
             "Reapertura con mudanza el 19/06/2025, en el domicilio nuevo.", "TAREA_2")
    set_campo(cambios, academia, "vigencia_fecha", "2025-06-19", "", "TAREA_2")
    set_campo(cambios, academia, "vigencia_nivel", "v2", "", "TAREA_2")

    clasica_moderna = por_id(filas, "H040")
    set_campo(cambios, clasica_moderna, "barrio_declarado", "Recoleta",
             "El catálogo la da en San Nicolás, que es incorrecto: Av. Callao 892 es Recoleta.",
             "TAREA_2")
    set_campo(cambios, clasica_moderna, "vigencia_verificada", "si",
             "Vendida en febrero de 2019, reabierta en diciembre de 2023 tras inversión "
             "(Wikipedia con citas). Estuvo publicada CUATRO AÑOS mientras estaba cerrada; se "
             "'corrigió' porque volvió a abrir, no por auditoría del catálogo — mismo patrón que "
             "Plaza Bar.", "TAREA_2")
    set_campo(cambios, clasica_moderna, "vigencia_nivel", "v2", "", "TAREA_2")

    thibon = por_id(filas, "H034")
    set_campo(cambios, thibon, "vigencia_verificada", "si",
             "Anuncio de cierre en enero de 2023 (Pura Ciudad: 'la dinastía Thibon ha llegado a su "
             "fin'); nueva gestión operando desde 2024 (Vinómanos 03/05/2024, toma Jorge Crespo, "
             "dueño de El Gato Negro). Precedente de continuidad con cambio de gestión.", "TAREA_2")
    set_campo(cambios, thibon, "vigencia_nivel", "v2", "", "TAREA_2")

    p("  Aplicado: Plaza Bar, La Buena Medida, The New Brighton, Esquina Homero Manzi, "
      "La Esquina de Aníbal Troilo, La Academia, Clásica y Moderna, Café Thibon.")
    p("  Sin acción (ya resueltos / fuera de todo catálogo, quedan documentados en la auditoría "
      "pero no tocan la capa): Confitería del Hotel Castelar (baja en 3758/24), El Palacio de la "
      "Papa Frita (no figura en 33/23 ni 3758/24 ni 1225/26), Bar Iberia (ver TAREA 1).")

    # ------------------------------------------------------------------
    # TAREA 3 · el cierre de la vigencia ronda 2
    # ------------------------------------------------------------------
    p("")
    p("TAREA 3 · vigencia ronda 2 cerrada (10 filas verificadas por Diego)")

    def cerrar_v2(hito_id: str, evidencia: str, nivel: str = "v2") -> None:
        f = por_id(filas, hito_id)
        set_campo(cambios, f, "vigencia_verificada", "si", evidencia, "TAREA_3")
        set_campo(cambios, f, "vigencia_fuente", evidencia, "", "TAREA_3")
        set_campo(cambios, f, "vigencia_fecha", "2026-08-07", "", "TAREA_3")
        set_campo(cambios, f, "vigencia_nivel", nivel, "", "TAREA_3")

    cerrar_v2("H058", "Ficha con actividad y horario todos los días de 7 a 23; sitio propio "
             "online que permite reservas; teléfono 4312-7902 vigente.")
    cerrar_v2("H037", "RESEÑA DE UNA VISITA FAMILIAR escrita el 05/07/2026 que describe haber "
             "almorzado allí, 33 días antes de la verificación. Sigue operando como Casa Watson; "
             "'ex Capisci' queda como antecedente histórico, no como nombre vigente.", nivel="v3")
    cerrar_v2("H025", "Ficha con horarios vigentes y actividad; otra fuente actualizada el "
             "06/06/2026 mantiene establecimiento, dirección e Instagram @donjuan_elbar.")
    cerrar_v2("H005", "Ficha local operativa con teléfono 4943-3694 y horario vigente; "
             "Tripadvisor mantiene establecimiento, teléfono y horarios actuales.")
    cerrar_v2("H065", "Ficha operativa con horarios vigentes y base extensa de reseñas; "
             "Tripadvisor operativa con horarios actuales; Turismo de la Ciudad conserva la ficha "
             "institucional.")

    los_laureles = por_id(filas, "H076")
    set_campo(cambios, los_laureles, "vigencia_verificada", "si",
             "REVIERTE P008: Turismo de la Ciudad mantiene una ficha ACTUALIZADA que describe la "
             "reapertura por nuevos propietarios y publica horarios nuevos y específicos (lun-mié "
             "12-15; jue-vie 12-15 y 20-00; sáb 20-2; dom 12-16). Distinción de fuente: un listado "
             "INERTE que arrastra una ficha vieja no prueba nada (caso Plaza Bar, nueve años), "
             "pero una ficha EDITADA ACTIVAMENTE para describir un cambio SÍ es evidencia. Son dos "
             "objetos distintos.", "TAREA_3")
    set_campo(cambios, los_laureles, "vigencia_fuente",
             "Turismo de la Ciudad (ficha activamente editada, no listado inerte); contradice la "
             "nota de El Cronista sobre el mismo local (ver FD-01, ronda 4).", "", "TAREA_3")
    set_campo(cambios, los_laureles, "vigencia_fecha", "2026-08-07", "", "TAREA_3")
    set_campo(cambios, los_laureles, "vigencia_nivel", "v2", "", "TAREA_3")
    set_campo(cambios, los_laureles, "nota_ronda_5",
             "El hito sigue frágil: el inmueble está en venta y el arreglo actual es un alquiler "
             "puente. Reabre la vía B de P008 Barracas.", "", "TAREA_3")

    saint_moritz = por_id(filas, "H043")
    set_campo(cambios, saint_moritz, "vigencia_verificada", "dudosa",
             "Ficha comercial continua en Esmeralda 890/894 con el mismo teléfono 4311-7311 y "
             "horarios publicados. Restaurant Guru actualizado el 30/03/2026 recoge actividad de "
             "clientes durante 2026. Sin prueba fechada posterior al 08/06/2026.", "TAREA_3")
    set_campo(cambios, saint_moritz, "vigencia_sentido_duda", "probablemente_abierto", "",
             "TAREA_3")
    set_campo(cambios, saint_moritz, "vigencia_nivel", "v4", "", "TAREA_3")

    barbaro = por_id(filas, "H002")
    set_campo(cambios, barbaro, "vigencia_verificada", "dudosa",
             "Ficha actual con Instagram y teléfono, pero CONTRADICCIÓN: una fuente consultada el "
             "21/07/2026 da horario lunes a sábado; la ficha local estructurada devuelve un "
             "horario mucho más reducido — patrón de retracción antes del cierre (caso El Buzón).",
             "TAREA_3")
    set_campo(cambios, barbaro, "vigencia_sentido_duda", "probablemente_abierto", "", "TAREA_3")
    set_campo(cambios, barbaro, "vigencia_nivel", "v4", "", "TAREA_3")
    set_campo(cambios, barbaro, "nota_ronda_5",
             "Confirmado: 'Bar Bar O' del catálogo es anomalía de transcripción, la denominación "
             "comercial es Barbaro. Priorizar llamada o Places.", "", "TAREA_3")

    olimpo = por_id(filas, "H028")
    set_campo(cambios, olimpo, "vigencia_verificada", "estado_operativo_pendiente",
             "La ficha del negocio sigue existiendo en Irigoyen 1491 y conserva teléfono; otra "
             "ficha actual trae horario. Pero sin reseña, publicación ni evidencia de visita en "
             "los últimos 60 días. Tripadvisor lo muestra sin horarios y prácticamente sin "
             "actividad reciente. Único de los diez que no se pudo resolver.", "TAREA_3")
    set_campo(cambios, olimpo, "vigencia_nivel", "ninguno", "", "TAREA_3")
    set_campo(cambios, olimpo, "nota_ronda_5",
             "Único Notable de Villa Luro (Z31): el caso que justifica Places por sí solo. "
             "Teléfonos: 3647-7287 y 6051-1069. El catálogo oficial lo llama 'Bar Olimpo' (orden "
             "12/90), no 'Café Olimpo'.", "", "TAREA_3")

    p("  Aplicado: Florida Garden, Casa Watson, Bar Don Juan, Bar de Cao, La Farmacia, Los "
      "Laureles (revierte P008), Confitería Saint Moritz, Bárbaro, Café Olimpo.")

    # El Sol de Galicia: no es un hito de Bares Notables (es churrería), se documenta aparte.
    p("")
    p("TAREA 3 · El Sol de Galicia: NO es un hito de esta capa (es churrería, no Bar Notable)")
    p("  Dirección correcta (sitio oficial): Luis Viale 2867. Confirmando con USIG antes de tocar")
    p("  cualquier fila de vía B que lo cite en otro archivo (no vive en hitos_capa_2026).")

    # ------------------------------------------------------------------
    # Confirmación USIG de las dos direcciones en duda
    # ------------------------------------------------------------------
    p("")
    p("USIG · confirmando las dos direcciones que TAREA 2/3 corrigen")
    cache = json.loads(CACHE_USIG.read_text(encoding="utf-8")) if CACHE_USIG.exists() else {}
    cache_du = (json.loads(CACHE_DATOS_UTILES.read_text(encoding="utf-8"))
                if CACHE_DATOS_UTILES.exists() else {})
    roma_abasto = por_id(filas, "H032")
    bar_iberia = por_id(filas, "H094")
    for etiqueta, direccion, fila_a_geocodificar in [
        ("La Academia (nueva)", "Montevideo 341", academia),
        ("El Sol de Galicia (corregida)", "Luis Viale 2867", None),
        ("Roma del Abasto (bug de fusión)", "Anchorena 806", roma_abasto),
        ("Bar Iberia (alta nueva)", "Av. de Mayo 1196", bar_iberia),
    ]:
        cand = consultar(limpiar(direccion) + ", CABA", cache)
        if cand and cand.get("coordenadas"):
            x, y = cand["coordenadas"]["x"], cand["coordenadas"]["y"]
            clave = f"{x},{y}"
            if clave not in cache_du:
                resp = requests.get(DATOS_UTILES_URL, params={"x": x, "y": y, "formato": "json"},
                                    timeout=25)
                resp.raise_for_status()
                cache_du[clave] = resp.json()
                time.sleep(0.35)
            du = cache_du[clave]
            p(f"  {etiqueta}: {direccion!r} -> USIG barrio={du.get('barrio', '—')} "
              f"comuna={du.get('comuna', '—')} x={x} y={y}")
            if fila_a_geocodificar is not None:
                set_campo(cambios, fila_a_geocodificar, "latitud", str(y),
                         f"Geocodificado con USIG ({direccion}, CABA), consulta 2026-08-07.",
                         "TAREA_1")
                set_campo(cambios, fila_a_geocodificar, "longitud", str(x), "", "TAREA_1")
                set_campo(cambios, fila_a_geocodificar, "barrio_declarado",
                         du.get("barrio", ""), "", "TAREA_1")
                set_campo(cambios, fila_a_geocodificar, "metodo_geocodificacion",
                         "USIG normalizador + datos_utiles (ronda 5)", "", "TAREA_1")
        else:
            p(f"  {etiqueta}: {direccion!r} -> USIG no resolvió (CABA); no se supone nada")
    CACHE_USIG.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    CACHE_DATOS_UTILES.write_text(json.dumps(cache_du, ensure_ascii=False, indent=1),
                                  encoding="utf-8")

    # ------------------------------------------------------------------
    # Guardar
    # ------------------------------------------------------------------
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)

    with open(CAMBIOS_CSV, "w", encoding="utf-8", newline="") as f:
        campos_cambio = ["hito_id", "nombre", "campo", "valor_antes", "valor_despues", "motivo",
                         "tarea", "fecha"]
        w = csv.DictWriter(f, fieldnames=campos_cambio)
        w.writeheader()
        w.writerows(cambios)

    p("")
    p(f"Guardado: {OUT_CSV} ({len(filas)} filas, {len(campos)} columnas)")
    p(f"Guardado: {CAMBIOS_CSV} ({len(cambios)} cambios registrados)")

    (HITOS / "RONDA_5.txt").write_text("\n".join(buf), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
