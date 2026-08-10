from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

from shapely.geometry import Point, shape


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT = Path(__file__).resolve().parent
CUT = "2026-08-10"


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def row(
    polo: str,
    nombre: str,
    direccion: str,
    existe: str,
    estado: str,
    fuente: str,
    fecha: str,
    nivel: str,
    observaciones: str,
) -> dict:
    return {
        "polo": polo,
        "nombre": nombre,
        "direccion": direccion,
        "existe": existe,
        "estado": estado,
        "fuente": fuente,
        "fecha": fecha,
        "nivel_de_verificacion": nivel,
        "observaciones": observaciones,
    }


LN_COREA = (
    "https://www.lanacion.com.ar/sabado/"
    "pasaje-ruperto-godoy-el-patio-de-comidas-coreano-del-shopping-a-cielo-abierto-"
    "que-se-creo-alrededor-nid15062023/"
)
HERALD_COREA = (
    "https://buenosairesherald.com/what-to-do-in-argentina/what-to-do-in-buenos-aires/"
    "koreatown-buenos-aires-little-known-hotspot-for-spicy-food-and-karaoke"
)
KOSHER_2015 = (
    "https://turismo.buenosaires.gob.ar/sites/turismo/files/"
    "establecimientos_KOSHER_2015_0.pdf"
)
TIMEOUT_PARQUE = (
    "https://www.timeout.com/es/buenos-aires/"
    "que-hacer-parque-avellaneda-viejo-mercado-yiyo-el-zeneize-olivera"
)
VILLA_LURO_2023 = (
    "https://www.infogastronomica.com.ar/"
    "villa-luro-los-nuevos-bares-y-restaurantes-de-un-polo-gastronomico-que-no-para-de-crecer/"
)


verificaciones = [
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Barthalé", "Ruperto Godoy 712", "sí", "probablemente_abierto", "https://es.restaurantguru.com/Barthale-Deli-and-Lounge-Buenos-Aires", "2026-07 (reseña de servicio)", "v2", "La reseña fechada acredita servicio; no se usó el rótulo abierto del agregador."),
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Bulmat", "Ruperto Godoy 731", "sí", "vigencia_no_verificada", LN_COREA, "2023-06-19", "v2", "Existencia y atención acreditadas sólo a la fecha de la nota."),
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Karaoke W", "Ruperto Godoy 761", "sí", "abierto_a_fecha_fuente", HERALD_COREA, "2025 (día no recuperado)", "v2", "La nota individualiza el local y su servicio; no prueba atención al corte."),
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Pan Moa", "Ruperto Godoy 763", "sí", "abierto_a_fecha_fuente", HERALD_COREA, "2025 (día no recuperado)", "v2", "La nota individualiza el local y su servicio; no prueba atención al corte."),
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Dashimaki", "Ruperto Godoy 770", "sí", "abierto_a_fecha_fuente", HERALD_COREA, "2025 (día no recuperado)", "v2", "La nota individualiza el local y su servicio; no prueba atención al corte."),
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Maum", "Felipe Vallese 3135", "sí", "abierto_a_fecha_fuente", HERALD_COREA, "2025 (día no recuperado)", "v2", "No confundir con el antecedente de Ruperto Godoy 733."),
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Makarios", "Felipe Vallese 3130", "sí", "vigencia_no_verificada", LN_COREA, "2023-06-19", "v2", "Sin pieza pública posterior localizada."),
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Pulpería Norte", "Felipe Vallese 3123", "sí", "vigencia_no_verificada", LN_COREA, "2023-06-19", "v2", "Sin pieza pública posterior localizada."),
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Yugane", "Páez 3063", "sí", "probablemente_abierto", "https://assets.mobile.playdigital.com.ar/promotions_dynamics/8bed371a-2d8f-4bb4-a793-7eb4d7081ac7/Comercios%20adheridos.pdf", "2026-06", "v3", "Participación operativa fechada en una promoción; no se usó un estado de agregador."),
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Shabu Shabu 153", "Páez 3154", "sí", "conflicto_de_vigencia", "https://es.restaurantguru.com/Shabu-Shabu-153-Buenos-Aires | https://carta.menu/restaurants/buenos-aires/shabu-shabu-153", "2025-07-02 / 2026-04-12", "v2", "Dos fuentes públicas secundarias discrepan; no se declara ni abierto ni cerrado."),
    row("Flores · Avellaneda y Pasaje Ruperto Godoy", "Ichiban", "Felipe Vallese y Ruperto Godoy", "sí", "vigencia_no_verificada", LN_COREA, "2023-06-19", "v2", "La nota no publica número de puerta y no se localizó una pieza posterior."),
]


kosher = [
    ("American Kosher", "Av. Avellaneda 2701"),
    ("Amltí Kosher", "Bolivia 449"),
    ("Azulay", "Dr. Juan F. Aranguren 2941"),
    ("Behar Almacén", "Campana 349"),
    ("Hamra", "Dr. Juan F. Aranguren 3192"),
    ("Kosher City", "Av. Avellaneda 2395"),
    ("Matok", "Av. Avellaneda 2433"),
    ("Nacca", "Argerich 843"),
    ("Productos Cohen", "Cuenca 180"),
    ("Soultani", "Cuenca 515"),
]
for nombre, direccion in kosher:
    verificaciones.append(
        row(
            "Flores · Avellaneda y Pasaje Ruperto Godoy",
            nombre,
            direccion,
            "sí_a_fecha_fuente",
            "vigencia_no_verificada",
            KOSHER_2015,
            "2015",
            "v2",
            "El padrón oficial acredita existencia histórica, no atención al corte.",
        )
    )
for numero in (11, 12):
    verificaciones.append(
        row(
            "Flores · Avellaneda y Pasaje Ruperto Godoy",
            f"Registro kosher no individualizado {numero}",
            "",
            "no_determinable",
            "no_verificable",
            KOSHER_2015,
            "2015",
            "v1",
            "El texto del atlas afirma doce, pero el padrón público permite identificar diez en Flores.",
        )
    )


verificaciones += [
    row("Parque Avellaneda", "La Barra del Parque", "Lacarra 836", "sí", "conflicto_de_vigencia", f"{TIMEOUT_PARQUE} | https://es.restaurantguru.com/La-Barra-Del-Parque-Buenos-Aires", "2025 / 2026-01-19", "v2", "La nota describe atención y el agregador luego marca cierre; el rótulo del agregador no basta para resolverlo."),
    row("Parque Avellaneda", "De Flores Café", "Lacarra 1500", "sí", "abierto_a_fecha_fuente", TIMEOUT_PARQUE, "2025 (día no recuperado)", "v2", "La nota publica propuesta y horarios; no acredita atención al corte."),
    row("Parque Avellaneda", "Viejo Mercado", "Av. Olivera 1557", "sí", "abierto_a_fecha_fuente", TIMEOUT_PARQUE, "2025 (día no recuperado)", "v2", "La nota publica propuesta y domicilio; no acredita atención al corte."),
    row("Donado–Holmberg", "Cimino R", "Donado 1919", "sí", "vigencia_no_verificada", "https://www.lanacion.com.ar/la-nacion-revista/sabores-unicos-quienes-son-y-como-trabajan-los-nuevos-alquimistas-del-helado-nid19022022/", "2022-02-19", "v2", "Se acredita la sede en 2022; los listados posteriores recuperados no traen una fecha editorial confiable."),
    row("Donado–Holmberg", "Vespress", "Donado 1720", "sí", "probablemente_abierto", "https://vespress.com/locales/", f"consulta {CUT}", "v1", "Sitio oficial vigente, pero sin fecha editorial; no alcanza el estándar de pieza fechada."),
    row("Donado–Holmberg", "Cigaló", "Holmberg 2004", "sí", "probablemente_abierto", "https://www.mastercard.com.ar/content/dam/public/mastercardcom/lac/ar/home/consumidores/conozca-nuestras-ofertas-y-promociones/Gastronomia.pdf", "2026-05", "v3", "Participación operativa fechada en una promoción pública."),
    row("Donado–Holmberg", "Chicama", "Donado 1995", "sí", "conflicto_de_domicilio_y_vigencia", "https://www.happycow.net/reviews/chicama-buenos-aires-315812 | https://godiamo.com.ar/cafes-y-dulces/chicama/", "2024-09-21 / 2026-07", "v2", "Una fuente informa mudanza a Echeverría 4322 y otra conserva Donado 1995; requiere constatación adicional."),
    row("Donado–Holmberg", "El Bohemio", "Donado 1802", "sí", "abierto_a_fecha_fuente", "https://tn.com.ar/cocina/gastronomia/2024/12/10/el-restaurante-que-lleva-10-anos-en-una-antigua-casona-de-villa-urquiza-y-conserva-su-alma-bohemia/", "2024-12-10", "v2", "Pieza individual fechada; no acredita atención al corte."),
    row("Villa Luro", "Brest Patisserie", "Acassuso 5183", "sí", "vigencia_no_verificada", VILLA_LURO_2023, "2023-03-26", "v2", "Sin pieza pública posterior suficientemente fechada."),
    row("Villa Luro", "Estación de Milanesas", "Acassuso 5202", "sí", "vigencia_no_verificada", VILLA_LURO_2023, "2023-03-26", "v2", "Sin pieza pública posterior localizada para esta sede."),
    row("Villa Luro", "Casa Tónica", "Av. Rivadavia 10101", "sí", "probablemente_abierto", "https://www.restaurants10.com/AR/Buenos-Aires/109823178650922/Casa-T%C3%B3nica-Gintoner%C3%ADa", "2026-06-08", "v2", "Espejo público de publicaciones fechadas del canal del local; señal útil, no verificación independiente."),
    row("Villa Luro", "García Restaurante", "García de Cossio 5727", "sí", "vigencia_no_verificada", VILLA_LURO_2023, "2023-03-26", "v2", "Sin pieza pública posterior localizada."),
    row("Villa Luro", "Mich Bar", "Basualdo 103", "sí", "vigencia_no_verificada", VILLA_LURO_2023, "2023-03-26", "v2", "Sin pieza pública posterior; un catálogo de entrega no se usó como verificación."),
    row("Villa Luro", "Alma y Fuego", "Av. Rivadavia 10399", "sí", "probablemente_abierto", "https://buenosairesconnect.com/barrio-villa-luro/", "2026-05-09", "v2", "La pieza describe oferta actual; el artículo de 2023 sólo anunciaba una apertura futura."),
]

write_csv(
    OUT / "verificacion_locales_sin_catalogo.csv",
    verificaciones,
    ["polo", "nombre", "direccion", "existe", "estado", "fuente", "fecha", "nivel_de_verificacion", "observaciones"],
)


def key(value: str) -> str:
    plain = unicodedata.normalize("NFKD", value.casefold()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", plain)


with (BASE / "hitos" / "hitos_capa_2026.geojson").open(encoding="utf-8") as fh:
    hitos = json.load(fh)
with (OUT / "soportes_41_usados.geojson").open(encoding="utf-8") as fh:
    soportes_fc = json.load(fh)
with (BASE / "ronda_17_codex" / "vigencia_90_hitos.csv").open(encoding="utf-8-sig", newline="") as fh:
    vigencia = list(csv.DictReader(fh))

soportes = [
    (
        feat["properties"]["polo_id"],
        feat["properties"]["polo_nombre"],
        shape(feat["geometry"]),
    )
    for feat in soportes_fc["features"]
]
conteos = {polo_id: 0 for polo_id, _, _ in soportes}
for feat in hitos["features"]:
    punto = Point(feat["geometry"]["coordinates"])
    for polo_id, _, geom in soportes:
        if geom.covers(punto):
            conteos[polo_id] += 1

bares = [feat for feat in hitos["features"] if feat["properties"]["tipo"] == "Bar Notable"]
alias = {
    key("Boca a Boca Bar"): "Bar Boca a Boca",
    key("Hotel Savoy / Bar Imperio"): "Bar Imperio",
    key("Roma del Abasto"): "Café Roma",
}

mejoras = {
    key("Café de la U"): ("abierto_a_fecha_fuente", "v2", "2025-06-24", "https://www.lanacion.com.ar/revista-lugares/villa-urquiza-el-barrio-tradicional-que-que-no-para-de-crecer-y-convoca-a-jovenes-y-foodies-nid24062025/", "Pieza individual fechada; sigue requiriendo actualización para vigencia al corte."),
    key("Bar Británico"): ("probablemente_abierto", "v2", "2026-07", "https://www.timeout.com/es/buenos-aires/que-hacer-planes-experiencias-teatro-museo-bares-restaurantes-musica-avenidad-corrientes", "Recomendación editorial reciente con visita propuesta; no es constatación directa."),
    key("Confitería El Greco"): ("abierto_a_fecha_fuente", "v3", "2026-02-25", "https://caballitourbano.com.ar/caballito-jugo-con-su-historia/", "Actividad pública fechada realizada dentro del establecimiento."),
    key("Café de García"): ("abierto_a_fecha_fuente", "v3", "2026-02", "https://static.buenosaires.gob.ar/sites/default/files/2026-02/DBA%20714%20WEB.pdf", "Participación operativa fechada en agenda oficial."),
    key("Stylo Café"): ("abierto_a_fecha_fuente", "v2", "2026-03-07", "https://www.canal26.com/turismo/2026/03/07/un-viaje-al-pasado-el-bar-notable-de-villa-devoto-con-mas-de-70-anos-que-mantiene-viva-la-tradicion-del-cafe-de-pocillo/", "Pieza individual fechada sobre el servicio."),
    key("Café Margot"): ("abierto_a_fecha_fuente", "v2", "2026-06-01", "https://la100.cienradios.com/sociedad/cuanto-cuesta-una-merienda-para-2-personas-en-cafe-margot-en-junio-2026/", "Pieza individual fechada con oferta de servicio."),
    key("Museo Fotográfico Simik"): ("abierto_a_fecha_fuente", "v2", "2026-04-21", "https://www.infobae.com/sociedad/2020/03/15/la-fantastica-historia-del-bombero-que-se-transformo-en-el-mayor-coleccionista-de-maquinas-fotograficas-y-de-cine-del-pais//", "La actualización pública ubica el museo dentro del bar; acredita el hecho a esa fecha."),
}

priorizados = []
for item in vigencia:
    if item["nivel_de_verificacion"] != "v1":
        continue
    objetivo = alias.get(key(item["nombre"]), item["nombre"])
    candidatos = [feat for feat in bares if key(feat["properties"]["nombre"]) == key(objetivo)]
    if not candidatos:
        candidatos = [feat for feat in bares if key(feat["properties"]["direccion"]) == key(item["direccion_adoptada"])]
    polos = []
    if candidatos:
        punto = Point(candidatos[0]["geometry"]["coordinates"])
        polos = [(polo_id, nombre, conteos[polo_id]) for polo_id, nombre, geom in soportes if geom.covers(punto)]
    if polos:
        minimo = min(valor for _, _, valor in polos)
        criterio = "sostiene_condicion_historia; priorizar_por_pocos_hitos"
        prioridad_base = 0
        polo_ids = ";".join(polo_id for polo_id, _, _ in polos)
        polo_nombres = ";".join(nombre for _, nombre, _ in polos)
    else:
        minimo = ""
        criterio = "fuera_de_soportes; prioridad_posterior"
        prioridad_base = 1
        polo_ids = ""
        polo_nombres = ""
    mejora = mejoras.get(key(item["nombre"]))
    if mejora:
        resultado, nivel_nuevo, fecha_nueva, fuente_nueva, nota = mejora
    else:
        resultado, nivel_nuevo, fecha_nueva, fuente_nueva, nota = (
            "pendiente_pieza_individual_fechada",
            "v1",
            "",
            "",
            "No se localizó en esta pasada una pieza pública individual que supere el estándar previo.",
        )
    priorizados.append(
        {
            "_sort": (prioridad_base, minimo if isinstance(minimo, int) else 9999, key(item["nombre"])),
            "nombre": item["nombre"],
            "barrio": item["barrio"],
            "polo_id": polo_ids,
            "polo_nombre": polo_nombres,
            "hitos_reconocidos_en_polo": minimo,
            "criterio_prioridad": criterio,
            "estado_previo": item["estado"],
            "nivel_previo": item["nivel_de_verificacion"],
            "dias_desde_verificacion_previa": item["dias_desde_verificacion"],
            "resultado": resultado,
            "nivel_resultante": nivel_nuevo,
            "fecha_nueva": fecha_nueva,
            "fuente_nueva": fuente_nueva,
            "observaciones": nota,
        }
    )

priorizados.sort(key=lambda x: x["_sort"])
for orden, item in enumerate(priorizados, 1):
    item["orden_prioridad"] = orden
    del item["_sort"]

write_csv(
    OUT / "vigencia_historicos_priorizados.csv",
    priorizados,
    [
        "orden_prioridad", "nombre", "barrio", "polo_id", "polo_nombre",
        "hitos_reconocidos_en_polo", "criterio_prioridad", "estado_previo", "nivel_previo",
        "dias_desde_verificacion_previa", "resultado", "nivel_resultante", "fecha_nueva",
        "fuente_nueva", "observaciones",
    ],
)

print(f"verificaciones={len(verificaciones)} historicos_v1={len(priorizados)} mejoras={len(mejoras)}")
