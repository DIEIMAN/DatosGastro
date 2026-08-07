"""Ronda 3 · la vigencia con cinco valores, las doce altas y la procedencia del catálogo.

QUÉ HACE
--------
Tres cosas que van juntas porque las tres son sobre **el estado de un hito**, no sobre su lugar.

**1 · Revierte P008 y estrena el vocabulario de cinco valores.** La ronda 2 puso Los Laureles en
`no` sobre una sola lectura, y P008 Barracas dejó de abrir vía B. La Nación y Canal 26 publican el
mismo día que cerró y que no cerró. Los Laureles pasa a `en_disputa`, que no es ni abrir ni cerrar.

**2 · Carga la evidencia de vigencia que la ronda 2 dejó afuera.** De las ~20 filas del CSV de
vigencia, la ronda 2 transcribió 4. Acá entran las demás, más lo que trae la ronda 3.

**3 · Hashea lo que hay en disco.** El PDF servido bajo la URL de la Res. MCGC 3758/24 fue
reeditado sin cambiar de número. Se guarda SHA-256 y `mtime` de cada archivo de catálogo que el
repositorio ya tiene, **sin volver a descargar nada**: descargarlo hoy daría un tercer contenido y
perdería la trazabilidad de las corridas que ya usaron el que está.

LO QUE NO SE HACE
-----------------
No se marca `dudosa` un hito porque «el catálogo no acredita apertura». Eso vale para los 90 y es
exactamente lo que `sin_verificar` significa. `dudosa` se reserva para donde hay un motivo positivo
para dudar: Bar Oviedo (sin observación de campo desde 2013) y El Faro (única fuente, 2011).

Google Places: 0 requests. USIG: 0 requests nuevos (todo sale del caché de la ronda 2).

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/hitos_ronda_3_vigencia.py
"""
from __future__ import annotations

import hashlib
import io
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polos_soporte import CRS_GEOGRAFICO  # noqa: E402

BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
HITOS = BARRIDO / "hitos"
EVIDENCIA = BARRIDO / "desde_cowork" / "evidencia_2026"
ENTRADA = HITOS / "hitos_capa_2026.csv"
SALIDA = HITOS / "hitos_capa_2026_r3.csv"

# Los archivos de catálogo que el repositorio tiene en disco y que alguna corrida usó. Se hashean
# tal como están. No se descarga nada: el punto entero es fijar QUÉ contenido se usó.
CATALOGOS = [
    (ROOT / "outputs" / "polos_gastro" / "REFERENTES_2026" / "_fuentes" /
     "bares_notables_consolidado_2025_anexo_res_1225_2026.pdf",
     "anexo del catálogo consolidado de Bares Notables (PDF)"),
    (BARRIDO / "desde_cowork" / "hitos_documentales_caba.csv",
     "transcripción documental que cita RES-MCGC-3758-24 como fuente"),
    (HITOS / "bares_notables_canon_boletin.csv",
     "canon de 90 que la ronda 2 fijó a partir de la transcripción"),
    (BARRIDO / "dataset_bares_notables" / "bares_notables_caba.csv",
     "lista de Wikidata (95), fuente independiente"),
    (ROOT / "outputs" / "polos_gastro" / "REFERENTES_2026" / "matriz_referentes_final_2026.csv",
     "lista del GCBA (84), fuente independiente"),
]

# ---------------------------------------------------------------- Tarea 1 · vigencia, cinco valores
#
# La clave es (nombre plegado, token de la calle). Nombre suelto no alcanza: «BAR OVIEDO» de
# Mataderos y «Restaurante Oviedo» de Recoleta son dos establecimientos, y la ronda 2 ya pagó ese
# aprendizaje. El estado, la fuente y la fecha viajan juntos: un estado sin fuente no es evidencia.
VIGENCIA_R3 = {
    # ---------------------------------------------------------------- LA REVERSIÓN
    ("LOS LAURELES", "IRIARTE"): (
        "en_disputa",
        "La Nación 05/08/2026 «El último adiós de Los Laureles» CONTRA Canal 26 05/08/2026 «Los "
        "Laureles no cierra… ya anunció nueva milonga». El sitio de turismo del GCBA lo sigue "
        "publicando sin nota. Tres fuentes, tres estados.", "2026-08-05", ""),
    # ---------------------------------------------------------------- verificados abiertos
    ("EL TOKIO", "ALVAREZ JONTE"): (
        "si", "Canal 26 05/08/2026. Abierto el 23/04/1930.", "2026-08-05",
        "no · cerró en 2023 y reabrió en 2025 (Infobae 06/04/2025, C5N); ningún listado registró "
        "ni el cierre ni la reapertura"),
    # El Fortín viaja SIN calle a propósito: la ronda 2 lo geocodificó por esquina y le dejó la
    # dirección vacía. Emparejarlo por calle lo perdía en silencio, que es peor que no marcarlo.
    ("EL FORTIN", ""): (
        "si", "CPPHC ficha id=124; Canal 26 28/08/2025 sobre las 10 pizzerías emblemáticas.",
        "2025-08-26", ""),
    ("EL BUZON", "ESQUIU"): (
        "si", "Infobae 10/08/2025.", "2025-08-10",
        "abierto EN RETRACCIÓN · atiende sólo lunes a viernes de 7 a 16, sin la programación "
        "nocturna y de fin de semana que tenía antes"),
    ("EL CEDRON", "ALBERDI"): (
        "si", "Canal 26 05/12/2025. Pizzería de 1935, Interés Cultural (Legislatura, 2013).",
        "2025-12-05", ""),
    ("CASA BOGOTA", "BOGOTA"): (
        "si", "sitio propio con horarios publicados; La Nación 04/12/2025, Revista Gente "
        "08/03/2026.", "2026-08-01",
        "no · la trayectoria es del EDIFICIO (casona de 1914); el restaurante abrió en 2025"),
    ("CASA MADRILIA", "ALVAREZ JONTE"): (
        "si", "ficha con horarios vigentes e Instagram activo.", "2026-08-01",
        "antigüedad NO documentada · sin atributo de trayectoria"),
    ("CONDE", "LACROZE"): (
        "si", "verificado abierto al 29/07/2026, cinco días antes de la declaración del 03/08. "
        "En funcionamiento desde 1902.", "2026-07-29", ""),
    ("GALGOS", "CALLAO"): (
        "si", "declaración de su responsable, 02/08/2026 (vía E · R02).", "2026-08-02", ""),
    ("ATLANTICO", "ARROYO"): (
        "si", "distinguido por Time Out el 20/12/2024 y verificado abierto (vía E · Z46).",
        "2024-12-20", ""),
    ("CASA BURGIO", "CABILDO"): (
        "si", "operativa.", "2026-08-07",
        "no · cerró en 2021 y reabrió en octubre de 2022 con otro dueño"),
    # ---------------------------------------------------------------- verificados cerrados
    ("NEW BRIGHTON", "SARMIENTO"): (
        "no", "declarado en quiebra por la Justicia el 18/03/2026 tras más de un siglo. Sigue en "
        "el catálogo.", "2026-03-18", ""),
    # ---------------------------------------------------------------- dudosos con motivo propio
    ("BAR OVIEDO", "DE LA TORRE"): (
        "dudosa", "el catálogo lo lista y APH 21 lo protege, pero la última observación de campo "
        "del GCBA es de enero de 2013 y no participó de la Noche de los Bares Notables 2025 "
        "mientras Del Glorias y 9 de Julio sí. Diario CEMBA publicó el 17/04/2026 pero bloquea "
        "acceso automatizado: LECTURA FALLIDA, no confirmación.", "2021-03-01", ""),
    ("EL FARO", "CONSTITUYENTES"): (
        "dudosa", "la única fuente que lo describe en operación es de mayo de 2011: quince años. "
        "Figura en el catálogo vigente. Perfil idéntico a Los Laureles y Bar Oviedo.",
        "2011-05-01", ""),
    ("PENA LOS AMIGOS BAR EL CHINO", "BEAZLEY"): (
        "dudosa", "Sitio de Interés Cultural 1999; sin cobertura posterior a 2017.",
        "2026-08-07", ""),
}

# Cierres confirmados de esta ronda que hay que buscar en la capa de mercados por si están.
CIERRES_MERCADOS = {
    ("CARRUAJES", "ALEM"): (
        "no", "cerró a fines de abril de 2025; tenía más de 40 espacios comerciales y el edificio "
        "—caballeriza presidencial de 1900, reabierto como mercado en febrero de 2022— se "
        "reconvierte en salón de eventos. Era el único mercado gastronómico de Retiro.",
        "2025-04-30", ""),
}

# Las doce altas del 03/08/2026, con la referencia que toca cada una. La fuente es SÓLO PRENSA: no
# se localizó número de resolución ni publicación en el Boletín Oficial.
ALTAS = EVIDENCIA / "bares_notables_altas_2026-08-03.csv"

# El caso que la reedición del PDF ya produjo. Se transcribe porque los dos nombres existen y son
# dos bares distintos, y confundirlos cambia de referencia: 1799 toca R02/R12, 4101 toca Z37.
SINTOMA_LA_OPERA = (
    "La prosa de la ronda 3 §6 nombra «La Ópera (Av. Corrientes 4101, Almagro)» como el caso "
    "conflictivo. En el CSV que la acompaña, Av. Corrientes 4101 / Almagro es LA ORQUÍDEA, y La "
    "Ópera figura aparte en Av. Corrientes 1799 / San Nicolás. La capa tiene los dos: H063 La "
    "Orquidea (4101) y H068 La Opera (1799). El síntoma de la reedición es real; el nombre con el "
    "que se lo cita es el equivocado, y no es lo mismo porque cambia la referencia que toca.")


def plegar(texto: str) -> str:
    limpio = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", limpio)).strip()


def sha256_de(ruta: Path) -> str:
    digestor = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1 << 20), b""):
            digestor.update(bloque)
    return digestor.hexdigest()


def entradas_del_pdf(ruta: Path) -> tuple[int, str]:
    """Cuántas entradas numeradas trae el anexo, y su identificador interno GEDO."""
    try:
        import fitz
    except ImportError:
        return -1, ""
    documento = fitz.open(ruta)
    texto = "".join(pagina.get_text() for pagina in documento)
    numeradas = re.findall(r"(?m)^\s*(\d{1,3})\.\s+\S", texto)
    gedo = re.search(r"(IF-\d{4}-\d+-GCABA-\w+)", texto)
    return (max(int(n) for n in numeradas) if numeradas else 0,
            gedo.group(1) if gedo else "")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    capa = pd.read_csv(ENTRADA)
    capa["clave"] = capa.nombre.map(plegar)
    capa["clave_dom"] = capa.direccion.map(plegar)

    p("RONDA 3 · VIGENCIA CON CINCO VALORES, LAS DOCE ALTAS Y LA PROCEDENCIA DEL CATÁLOGO")
    p("=" * 100)
    p("")
    p(f"  capa de entrada: {len(capa)} hitos · lo declarado está en LECTURA_PREVIA_RONDA_3.md")
    p("  Google Places: 0 requests. Nada se vuelve a descargar.")
    p("")

    # ================================================================ TAREA 1 · vigencia
    antes = capa.vigencia_verificada.copy()
    capa["vigencia_verificada"] = "sin_verificar"
    capa["vigencia_fuente"] = ""
    capa["vigencia_fecha"] = ""
    capa["continuidad_ininterrumpida"] = ""

    aplicadas, sin_hallar = [], []
    for (clave_nombre, clave_calle), datos in {**VIGENCIA_R3, **CIERRES_MERCADOS}.items():
        estado, fuente, fecha, continuidad = datos
        objetivo = capa.clave.str.contains(clave_nombre, regex=False) & \
            capa.clave_dom.str.contains(clave_calle, regex=False)
        if not objetivo.any():
            sin_hallar.append((clave_nombre, clave_calle, estado))
            continue
        capa.loc[objetivo, "vigencia_verificada"] = estado
        capa.loc[objetivo, "vigencia_fuente"] = fuente
        capa.loc[objetivo, "vigencia_fecha"] = fecha
        if continuidad:
            capa.loc[objetivo, "continuidad_ininterrumpida"] = continuidad
        aplicadas.append((clave_nombre, estado, int(objetivo.sum()),
                          "; ".join(capa.loc[objetivo, "nombre"].astype(str))))

    p("-" * 100)
    p("  TAREA 1 · LA VIGENCIA, CON CINCO VALORES")
    p("")
    p("      El vocabulario del hito: si · no · en_disputa · dudosa · sin_verificar")
    p("      El de la fila de la matriz —via_B_soporte— es otro y sale del cruce, no de acá.")
    p("")
    p(f"      {'estado':<14}{'clave':<32}{'filas':>7}   hito(s)")
    for clave_nombre, estado, cuantas, nombres in sorted(aplicadas, key=lambda t: t[1]):
        p(f"      {estado.upper():<14}{clave_nombre[:31]:<32}{cuantas:>7}   {nombres[:44]}")
    p("")
    if sin_hallar:
        p("      NO ESTÁN EN LA CAPA (se declaran, no se inventan):")
        for clave_nombre, clave_calle, estado in sin_hallar:
            p(f"            {clave_nombre} / {clave_calle} — se quería marcar {estado}")
        p("")

    p("      El reparto que queda:")
    for estado, cuantas in capa.vigencia_verificada.value_counts().items():
        p(f"            {estado:<16}{cuantas:>5}")
    p("")
    movidos = capa[antes.values != capa.vigencia_verificada.values]
    p(f"      hitos cuyo estado CAMBIÓ respecto de la ronda 2: {len(movidos)}")
    for fila in movidos.itertuples():
        p(f"            {str(fila.nombre)[:34]:<36}"
          f"{antes.iloc[fila.Index] if fila.Index < len(antes) else '?':<16}→  "
          f"{fila.vigencia_verificada}")
    p("")
    p("      LA REVERSIÓN, dicha entera: la ronda 2 puso Los Laureles en `no` y con eso P008")
    p("      Barracas dejó de abrir vía B. Ese `no` era una lectura de una sola fuente. Pasa a")
    p("      `en_disputa`, que no abre ni cierra, y P008 vuelve a quedar pendiente.")
    p("")
    p("      Y lo que NO se marcó, que también es una decisión: los cuatro Bares Notables de")
    p("      Retiro y Casa Watson llegaron etiquetados «dudosos». El motivo que traen —«el")
    p("      catálogo no acredita apertura»— vale para los 90 y es la definición misma de")
    p("      `sin_verificar`. `dudosa` se reserva para donde hay un motivo positivo para dudar:")
    p("      Bar Oviedo (sin observación de campo desde 2013) y El Faro (única fuente, 2011).")
    p("")

    # ================================================================ TAREA 6 · las doce altas
    altas = pd.read_csv(ALTAS)
    capa["es_alta_2026_08_03"] = False
    capa["declaratoria_localizada"] = ""
    capa["alta_referencia_que_toca"] = ""
    encontradas, faltantes = [], []
    for fila in altas.itertuples():
        clave_nombre = plegar(fila.establecimiento)
        # Se empareja por nombre plegado Y por la altura de la dirección: dos bares de Corrientes
        # con nombres parecidos son el caso que esta tarea vino a separar.
        numero = re.search(r"\b(\d{1,5})\b", str(fila.direccion))
        por_nombre = capa.clave.str.contains(
            re.sub(r"^(BAR|CAFE|CONFITERIA|LA|EL) ", "", clave_nombre), regex=False)
        objetivo = por_nombre
        discrepancia = ""
        if numero is not None:
            con_altura = por_nombre & capa.clave_dom.str.contains(numero.group(1), regex=False)
            if con_altura.any():
                objetivo = con_altura
            elif por_nombre.sum() == 1:
                # Un solo homónimo y la altura no coincide: es la misma puerta con dos alturas
                # publicadas, no dos bares. Se empareja y se registra la discrepancia, que es
                # justamente el tipo de cosa que la reedición del catálogo produce.
                discrepancia = (f"la lista de altas dice «{fila.direccion}»; la capa tiene "
                                f"«{capa.loc[por_nombre, 'direccion'].iloc[0]}»")
        if not objetivo.any():
            faltantes.append((fila.establecimiento, fila.direccion))
            continue
        capa.loc[objetivo, "es_alta_2026_08_03"] = True
        capa.loc[objetivo, "declaratoria_localizada"] = "no · sólo prensa"
        capa.loc[objetivo, "alta_referencia_que_toca"] = fila.referencia_o_zona_que_toca
        encontradas.append((fila.establecimiento, fila.direccion,
                            "; ".join(capa.loc[objetivo, "hito_id"].astype(str)) +
                            (f"   ← {discrepancia}" if discrepancia else "")))

    p("-" * 100)
    p("  TAREA 6 · LAS DOCE ALTAS DEL 03/08/2026")
    p("")
    p(f"      {len(encontradas)} de {len(altas)} ya estaban en la capa de hitos.")
    for nombre, direccion, ids in encontradas:
        p(f"            {nombre[:28]:<30}{direccion[:30]:<32}{ids}")
    for nombre, direccion in faltantes:
        p(f"            NO ESTÁ: {nombre} — {direccion}")
    p("")
    p("      declaratoria_localizada = «no · sólo prensa» para las doce. No se localizó el número")
    p("      de resolución ni su publicación en el Boletín Oficial: la fuente son La Nación del 6")
    p("      de agosto y Canal 26 del 3, con Infobae y Perfil como réplicas.")
    p("")
    p("      EL SÍNTOMA, con el nombre corregido:")
    for linea in re.findall(r".{1,88}(?:\s|$)", SINTOMA_LA_OPERA):
        p(f"            {linea.strip()}")
    p("")

    # ================================================================ TAREA 6 · procedencia
    filas_proc = []
    for ruta, que_es in CATALOGOS:
        if not ruta.exists():
            filas_proc.append({"archivo": str(ruta.relative_to(ROOT)), "que_es": que_es,
                               "existe": "no"})
            continue
        estado = ruta.stat()
        # Los CSV del repositorio llegan con cabecera comentada («#…») en algunos casos; contar
        # sin `comment` los rompe y el conteo no es el punto de esta tabla, el hash sí.
        entradas, gedo = (entradas_del_pdf(ruta) if ruta.suffix.lower() == ".pdf"
                          else (len(pd.read_csv(ruta, comment="#")), ""))
        filas_proc.append({
            "archivo": str(ruta.relative_to(ROOT)), "que_es": que_es, "existe": "si",
            "sha256": sha256_de(ruta), "bytes": estado.st_size,
            "mtime_utc": datetime.fromtimestamp(estado.st_mtime, timezone.utc).isoformat(
                timespec="seconds"),
            "hasheado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "entradas": entradas, "identificador_interno": gedo,
        })
    procedencia = pd.DataFrame(filas_proc)
    procedencia.to_csv(HITOS / "PROCEDENCIA_CATALOGOS.csv", index=False, encoding="utf-8")

    p("-" * 100)
    p("  TAREA 6 · PROCEDENCIA · SHA-256 Y FECHA DE LO QUE HAY EN DISCO")
    p("")
    p("      No se volvió a descargar nada. Lo que se hashea es lo que las corridas usaron; bajar")
    p("      el PDF hoy daría un tercer contenido y perdería la trazabilidad de lo ya corrido.")
    p("")
    for fila in procedencia.itertuples():
        p(f"      {fila.archivo}")
        if fila.existe != "si":
            p("            NO ESTÁ EN DISCO")
            continue
        p(f"            {fila.que_es}")
        p(f"            sha256   {fila.sha256}")
        p(f"            en disco desde {fila.mtime_utc} · {fila.bytes:,} bytes · "
          f"{fila.entradas} entradas")
        if fila.identificador_interno:
            p(f"            identificador interno del documento: {fila.identificador_interno}")
    p("")

    # El contraste que el hash solo no muestra: qué trae ESTE contenido respecto de las altas.
    pdf = CATALOGOS[0][0]
    if pdf.exists():
        import fitz
        texto_pdf = plegar("".join(pagina.get_text() for pagina in fitz.open(pdf)))
        adentro = [(f.establecimiento, plegar(f.establecimiento) in texto_pdf)
                   for f in altas.itertuples()]
        cuantas = sum(1 for _, esta in adentro if esta)
        p("      QUÉ TRAE EL CONTENIDO QUE TENEMOS, contra las doce altas del 03/08/2026")
        p("")
        for nombre, esta in adentro:
            p(f"            {'ESTÁ    ' if esta else 'NO ESTÁ '}{nombre}")
        p("")
        p(f"      {cuantas} de {len(altas)} en un anexo cuya hoja de firmas está fechada el")
        p("      26 de febrero de 2026 —seis meses antes de la fecha de las altas—, con 90")
        p("      entradas. Diego reporta que la URL de la Res. MCGC 3758/24 sirve HOY un PDF de")
        p("      88 entradas con 7 de las 12, sin El Greco ni Plaza Café.")
        p("")
        p("      Entonces circulan TRES contenidos, no dos:")
        p("            90 entradas · el que está en disco desde el 03/08/2026, firmado 26/02/2026")
        p("            88 entradas · el que la URL sirve hoy")
        p("            84 y 95     · las listas del GCBA y de Wikidata, ya cruzadas en la ronda 2")
        p("")
        p("      Y una consecuencia que no es de forma: si un documento firmado en febrero de")
        p("      2026 ya lista los doce, entonces «alta del 3 de agosto» no describe el acto")
        p("      declaratorio. Puede ser la fecha de difusión de un catálogo ya consolidado. NO")
        p("      SE AFIRMA CUÁL DE LAS DOS COSAS ES: se afirma que la prensa y el documento no")
        p("      dicen lo mismo, y que la resolución que declararía las altas sigue sin")
        p("      localizarse.")
        p("")
        p("      El «1225/2026» del nombre del archivo es NUESTRO, no del documento: ese número")
        p("      no aparece en el texto del PDF. El identificador que sí es suyo es el GEDO")
        p("      IF-2026-10314379-GCABA-DGPMYCH. La procedencia se cita por ése.")
        p("")

    # ================================================================ salida
    capa = capa.drop(columns=["clave", "clave_dom"])
    capa.to_csv(SALIDA, index=False, encoding="utf-8")
    con_punto = capa[capa.latitud.notna() & capa.longitud.notna()]
    gpd.GeoDataFrame(
        con_punto, geometry=gpd.points_from_xy(con_punto.longitud, con_punto.latitud),
        crs=CRS_GEOGRAFICO).to_file(HITOS / "hitos_capa_2026_r3.geojson", driver="GeoJSON")

    p("=" * 100)
    p(f"  {len(capa)} hitos · {len(con_punto)} con punto · "
      f"{int((capa.vigencia_verificada == 'si').sum())} verificados abiertos · "
      f"{int((capa.vigencia_verificada == 'no').sum())} cerrados · "
      f"{int((capa.vigencia_verificada == 'en_disputa').sum())} en disputa")
    p(f"  la capa de la ronda 2 queda intacta en {ENTRADA.name}; esto escribe {SALIDA.name}")
    p("=" * 100)
    p("")

    (HITOS / "VIGENCIA_RONDA_3.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
