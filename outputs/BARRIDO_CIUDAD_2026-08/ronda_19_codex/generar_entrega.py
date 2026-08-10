from __future__ import annotations

import csv
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PREV = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "ronda_18_codex"
GEO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "ronda_18" / "anclas_dentro_y_fuera.csv"
EJES = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08" / "idecba" / "ejes_relevamiento_2026_c1.csv"
CUT = date(2026, 8, 10)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^A-Z0-9]+", " ", value.upper()).strip()
    return value


S_DBA_2025 = "https://buenosaires.gob.ar/sites/default/files/2025-10/DBA%20701%20WEB_0.pdf"
S_TUR_2025 = "https://turismo.buenosaires.gob.ar/es/article/la-noche-de-los-bares-notables"
S_MUSEOS_2025 = "https://buenosaires.gob.ar/noticias/charlas-en-los-bares-notables-de-la-ciudad"
S_DBA_2024 = "https://buenosaires.gob.ar/sites/default/files/2024-10/Suplemento%20semanal%20Descubrir%20BA%20%E2%80%A2%2031%20de%20octubre%20al%206%20de%20noviembre%20de%202024%20%E2%80%A2.pdf"
S_PROG_2024 = "https://buenosaires.gob.ar/sites/default/files/2024-10/Programaci%C3%B3n_0.pdf"
S_BORGES_2026 = "https://buenosaires.gob.ar/gcaba_historico/noticias/borges-vuelve-los-bares-notables"
S_MAYO_2026 = "https://buenosaires.gob.ar/gcaba_historico/noticias/actividades-de-mayo-en-los-bares-notables"
S_PROGRESO_2022 = "https://buenosaires.gob.ar/sites/default/files/media/document/2022/10/25/76961abb6ac6cfd729e46cbd62f3328b39ac793a.pdf"


def ev(day: str, source: str, detail: str) -> tuple[str, str, str]:
    return day, source, detail


HIST_EVIDENCE = {
    "EL PROGRESO": ev("2022-10-28", S_PROGRESO_2022, "programación cultural oficial fechada en el establecimiento"),
    "ESQUINA HOMERO MANZI": ev("2024-11-02", S_DBA_2024, "actividad oficial fechada en el establecimiento"),
    "CABILDO DE BUENOS AIRES": ev("2026-05-25", "https://holasantelmo.ar/el-bar-donde-desayunaba-el-papa-y-se-fundo-un-club-de-futbol/", "pieza barrial fechada que describe la operación actual del establecimiento"),
    "LONDON CITY": ev("2024-11-02", S_DBA_2024, "actividad oficial fechada en el establecimiento"),
    "BAR 9 DE JULIO": ev("2025-10-16", S_DBA_2025, "actividad oficial fechada en el establecimiento"),
    "LA ESCUELA": ev("2026-07-16", "https://www.diariodecultura.com.ar/turismo-cultural/bar-la-escuela-en-el-barrio-de-nunez/", "pieza periodística fechada y centrada en el establecimiento"),
    "CAFE SAN BERNARDO": ev("2025-10-16", S_DBA_2025, "actividad oficial fechada en el establecimiento"),
    "ALMACEN Y BAR LAVALLE": ev("2025-10-16", S_DBA_2025, "actividad oficial fechada en el establecimiento"),
    "CELTA BAR": ev("2025-10-16", S_TUR_2025, "programación turística oficial fechada en el establecimiento"),
    "EL GATO NEGRO": ev("2025-10-16", S_DBA_2025, "actividad oficial fechada en el establecimiento"),
    "LA ACADEMIA": ev("2025-11-08", S_MUSEOS_2025, "actividad oficial fechada en el establecimiento"),
    "LA BIELA": ev("2024-11-02", S_DBA_2024, "actividad oficial fechada en el establecimiento"),
    "LA GIRALDA": ev("2025-10-16", S_DBA_2025, "actividad oficial fechada en el establecimiento"),
    "LA OPERA": ev("2025-10-16", S_TUR_2025, "programación turística oficial fechada en el establecimiento"),
    "LOS GALGOS": ev("2025-10-16", S_TUR_2025, "programación turística oficial fechada en el establecimiento"),
    "BARBARO BAR": ev("2025-10-16", S_DBA_2025, "actividad oficial fechada en el establecimiento"),
    "CONFITERIA SAINT MORITZ": ev("2025-11-08", S_MUSEOS_2025, "actividad oficial fechada en el establecimiento"),
    "JOSEPHINA'S CAFE": ev("2025-10-16", S_TUR_2025, "programación turística oficial fechada en el establecimiento"),
    "CONFITERIA LA IDEAL": ev("2024-11-02", S_DBA_2024, "actividad oficial fechada en el establecimiento"),
    "EL QUERANDI": ev("2026-07-23", S_BORGES_2026, "itinerario cultural oficial fechado con parada en el establecimiento"),
    "LA PUERTO RICO": ev("2025-11-08", S_MUSEOS_2025, "actividad oficial fechada en el establecimiento"),
    "PAULIN": ev("2025-10-16", S_TUR_2025, "programación turística oficial fechada en el establecimiento"),
    "CLARIDGE'S BAR": ev("2026-05-30", "https://bairessecreta.com/en/this-may-you-can-enjoy-live-tango-for-free-at-5-iconic-notable-bars-in-buenos-aires/", "agenda pública fechada con actividad en el establecimiento"),
    "BAR EL COLONIAL": ev("2026-05-22", S_MAYO_2026, "actividad oficial fechada en el establecimiento"),
    "BAR PLAZA DORREGO": ev("2026-07-23", S_BORGES_2026, "itinerario cultural oficial fechado con parada en el establecimiento"),
    "BAR PORTUARIO": ev("2025-11-08", S_MUSEOS_2025, "actividad oficial fechada en el establecimiento"),
    "BAR QUINTINO": ev("2024-11-02", S_DBA_2024, "actividad oficial fechada en el establecimiento"),
    "BAR SEDDON": ev("2025-10-16", S_DBA_2025, "actividad oficial fechada en el establecimiento"),
    "BAR SUR": ev("2025-10-16", S_DBA_2025, "actividad oficial fechada en el establecimiento"),
    "BAR VIA 71": ev("2024-11-02", S_DBA_2024, "actividad oficial fechada en el establecimiento"),
    "BOCA A BOCA BAR": ev("2024-11-02", S_PROG_2024, "programación oficial fechada en el establecimiento"),
    "CAFE CORTAZAR": ev("2025-10-16", S_TUR_2025, "programación turística oficial fechada en el establecimiento"),
    "CAFE RIVAS": ev("2026-02-06", "https://www.eltrecetv.com.ar/cucinare/2026/02/06/reabrio-cafe-rivas-volver-sin-empezar-de-cero/", "pieza periodística fechada que documenta la reapertura"),
    "CAFE ROMA": ev("2025-06-22", "https://www.infobae.com/sociedad/2025/06/22/cafetines-de-buenos-aires-el-bar-centenario-que-funciona-como-sede-social-del-barrio-de-la-boca-y-exhibe-donaciones-de-vecinos/", "pieza periodística fechada y centrada en el establecimiento"),
    "CAFE TABAC": ev("2026-03-03", "https://bairesparatodos.com.ar/cafe-tabac-la-nueva-meca-del-levante-en-buenos-aires/", "pieza periodística fechada y centrada en el establecimiento"),
    "CAFE THIBON": ev("2026-05-31", "https://www.usal.edu.ar/best/beneficios/", "beneficio operativo público y fechado para consumos en el establecimiento"),
    "CLASICA Y MODERNA": ev("2026-07-16", "https://clasicaymoderna.com.ar/", "sitio del establecimiento con actividad fechada"),
    "HOTEL SAVOY / BAR IMPERIO": ev("2026-05-30", "https://bairessecreta.com/en/this-may-you-can-enjoy-live-tango-for-free-at-5-iconic-notable-bars-in-buenos-aires/", "agenda pública fechada con actividad en el establecimiento"),
    "EL HIPOPOTAMO": ev("2025-10-16", S_DBA_2025, "actividad oficial fechada en el establecimiento"),
    "LA FLOR DE BARRACAS": ev("2025-11-08", S_MUSEOS_2025, "actividad oficial fechada en el establecimiento"),
    "LA POESIA": ev("2025-10-16", S_TUR_2025, "programación turística oficial fechada en el establecimiento"),
    "LE CARAVELLE": ev("2026-07-14", "https://www.canal26.com/turismo/2026/07/14/el-bar-escondido-de-buenos-aires-que-parece-detenido-en-los-anos-60-y-sirve-un-capuchino-legendario/", "pieza periodística fechada y centrada en el establecimiento"),
    "MAR AZUL": ev("2024-11-02", S_PROG_2024, "programación oficial fechada en el establecimiento"),
    "MIRAMAR": ev("2026-07-01", "https://www.diariodecultura.com.ar/costumbres-y-tendencias/los-bares-portenos-mas-elegidos-para-peliculas-y-publicidades-tradicion-identidad-y-un-pasado-que-vuelve/", "pieza periodística fechada y centrada en el establecimiento"),
    "MONTECARLO BAR Y DESPENSA": ev("2026-02-14", "https://static.buenosaires.gob.ar/sites/default/files/2026-02/DBA%20715%20WEB.pdf", "actividad oficial fechada en el establecimiento"),
    "OCHO ESQUINAS": ev("2025-10-16", S_TUR_2025, "programación turística oficial fechada en el establecimiento"),
    "PLAZA CAFE": ev("2025-09-27", "https://www.restaurants10.com/AR/Buenos-Aires/197281274342342/PLAZA-CAFE---Caballito", "publicación fechada del canal del establecimiento reproducida en un espejo público"),
    "ROMA DEL ABASTO": ev("2025-10-16", S_TUR_2025, "programación turística oficial fechada en el establecimiento"),
}
HIST_EVIDENCE = {norm(key): value for key, value in HIST_EVIDENCE.items()}


ALIASES_42 = {
    "9 DE JULIO": "BAR 9 DE JULIO",
    "EL COLONIAL": "BAR EL COLONIAL",
    "EL PORTUARIO": "BAR PORTUARIO",
    "BAR BOCA A BOCA": "BOCA A BOCA BAR",
}


def historical_rows() -> list[dict[str, object]]:
    previous = [r for r in read_csv(PREV / "vigencia_historicos_priorizados.csv") if r["nivel_resultante"] == "v1"]
    anchors = read_csv(GEO)
    outer = {
        ALIASES_42.get(norm(r["establecimiento"]), norm(r["establecimiento"]))
        for r in anchors
        if r["sostiene_condicion_historia"] == "si" and r["dentro_del_borde"] == "no"
    }
    output = []
    for row in previous:
        item = dict(row)
        key = norm(item["nombre"])
        item["es_de_los_42"] = "si" if key in outer else "no"
        if key in HIST_EVIDENCE:
            day, source, detail = HIST_EVIDENCE[key]
            item["resultado"] = "abierto_a_fecha_fuente"
            item["nivel_resultante"] = "v2"
            item["fecha_nueva"] = day
            item["fuente_nueva"] = source
            item["observaciones"] = f"{detail.capitalize()}. Acredita vigencia en esa fecha; no equivale a constatación al corte."
        else:
            item["resultado"] = "pendiente_pieza_individual_fechada"
            item["nivel_resultante"] = "v1"
            item["fecha_nueva"] = ""
            item["fuente_nueva"] = ""
            item["observaciones"] = "No se localizó una pieza pública individual y fechada que supere el estándar previo. La ausencia de evidencia no se interpreta como cierre."
        output.append(item)
    output.sort(key=lambda r: (0 if r["es_de_los_42"] == "si" else 1, int(r["orden_prioridad"])))
    for pos, item in enumerate(output, 1):
        item["orden_prioridad"] = pos
    return output


LOCAL_NAMES = [
    "Brest Patisserie", "Estación de Milanesas", "García Restaurante", "Mich Bar",
    "Bulmat", "Makarios", "Pulpería Norte", "Ichiban", "Cimino R",
    "American Kosher", "Amltí Kosher", "Azulay", "Behar Almacén", "Hamra",
    "Kosher City", "Matok", "Nacca", "Productos Cohen", "Soultani",
]


LOCAL_UPDATES = {
    "Brest Patisserie": (
        "https://buenosairesconnect.com/barrio-villa-luro/", "2026-05-09",
        "Pieza pública fechada que describe al local y su oferta en Villa Luro."
    ),
    "Bulmat": (
        "https://tn.com.ar/turismo/2025/02/06/el-pintoresco-pasaje-coreano-en-pleno-buenos-aires-con-arte-callejero-cafes-karaokes-y-restaurantes/",
        "2025-02-06", "Pieza periodística fechada que individualiza el local y su oferta."
    ),
    "Ichiban": (
        "https://tn.com.ar/turismo/2025/02/06/el-pintoresco-pasaje-coreano-en-pleno-buenos-aires-con-arte-callejero-cafes-karaokes-y-restaurantes/",
        "2025-02-06", "Pieza periodística fechada que individualiza el local y su oferta."
    ),
    "Matok": (
        "https://mashaladigital.com/kosher-matok-en-flores-ahora-mas-grande-mas-lindo-y-con-mas-de-todo/",
        "2025-05-09", "Pieza comunitaria fechada que documenta la reapertura del local."
    ),
}


def local_rows() -> list[dict[str, object]]:
    source = {r["nombre"]: r for r in read_csv(PREV / "verificacion_locales_sin_catalogo.csv")}
    output = []
    for name in LOCAL_NAMES:
        item = dict(source[name])
        if name in LOCAL_UPDATES:
            url, day, note = LOCAL_UPDATES[name]
            item.update(
                existe="sí_a_fecha_fuente", estado="abierto_a_fecha_fuente", fuente=url,
                fecha=day, nivel_de_verificacion="v2",
                observaciones=note + " No acredita atención al corte.",
            )
        else:
            item["estado"] = "vigencia_no_verificada"
            item["observaciones"] = (
                "Se buscaron piezas públicas posteriores al antecedente disponible. Los directorios sin fecha y "
                "los catálogos de entrega recuperados no se usaron para afirmar vigencia; tampoco se infiere cierre."
            )
        output.append(item)
    return output


def conflict_rows() -> list[dict[str, object]]:
    return [
        {
            "establecimiento": "La Mezzetta", "direccion_previa": "Av. Álvarez Thomas 1321",
            "direccion_en_conflicto": "Av. Álvarez Thomas 1311", "direccion_adoptada": "Av. Álvarez Thomas 1321",
            "estado_resolucion": "resuelto", "criterio": "Dos piezas oficiales fechadas respaldan 1321; la ficha turística que publica 1311 queda documentada como discrepancia.",
            "fuentes_publicas": "https://parlamentaria.legislatura.gob.ar/pages/download.aspx?IdDoc=206457 | https://buenosaires.gob.ar/gcaba_historico/noticias/los-vecinos-eligieron-las-mejores-pizzerias-de-buenos-aires",
            "fecha_fuente_mas_reciente": "2024-05-10", "impacto_en_polos": "sin cambio en la asignación vigente",
            "pendiente": "ninguno para el domicilio público",
        },
        {
            "establecimiento": "San Carlos", "direccion_previa": "Av. Rivadavia 4548",
            "direccion_en_conflicto": "Av. La Plata", "direccion_adoptada": "Av. Rivadavia 4548",
            "estado_resolucion": "resuelto", "criterio": "El sitio del establecimiento y una pieza fechada coinciden en Rivadavia 4548; Av. La Plata funciona como referencia de esquina.",
            "fuentes_publicas": "https://sancarlospizza.com/ | https://www.canal26.com/turismo/2026/05/11/la-pizzeria-de-caballito-con-show-de-pizza-en-el-aire-donde-queda-y-cuanto-cuesta/",
            "fecha_fuente_mas_reciente": "2026-05-11", "impacto_en_polos": "sin cambio en la asignación vigente",
            "pendiente": "ninguno para el domicilio público",
        },
        {
            "establecimiento": "Saverio", "direccion_previa": "Av. San Juan 2816",
            "direccion_en_conflicto": "Av. San Juan 2809", "direccion_adoptada": "Av. San Juan 2809",
            "estado_resolucion": "resuelto_para_acceso_publico; pendiente_vinculo_catastral",
            "criterio": "La pieza pública más reciente ubica el acceso en 2809. La ficha oficial histórica conserva 2816; no se demostró si ambos números corresponden al mismo inmueble o a accesos distintos.",
            "fuentes_publicas": "https://viagemeturismo.abril.com.br/mundo/7-gelaterias-para-se-deliciar-em-buenos-aires/ | https://turismo.buenosaires.gob.ar/es/gastronomico/saverio",
            "fecha_fuente_mas_reciente": "2026-03-02", "impacto_en_polos": "sin cambio material por tratarse de veredas enfrentadas",
            "pendiente": "confirmar habilitación o parcela actual y relación entre ambos números",
        },
    ]


def add_claim(rows: list[dict[str, object]], page: str, cited: str, official: str, metric: str,
              value: float, super_cited: str = "", super_correct: str = "") -> None:
    unit = {"ocupacion": "%", "variacion_interanual": "pp", "densidad": "locales/frente de manzana"}[metric]
    cited_unit = "locales/cuadra" if metric == "densidad" else unit
    rows.append({
        "pagina": page, "eje_citado": cited, "eje_en_la_fuente": official,
        "valor_citado": f"{metric}={value:g} {cited_unit}",
        "valor_en_la_fuente": f"{metric}={value:g} {unit}",
        "anio": "2026 (1er cuatrimestre)",
        "coincide": "sí" if metric != "densidad" else "sí en valor; no en unidad publicada",
        "superlativo_citado": super_cited, "superlativo_correcto": super_correct,
    })


def axis_claims() -> list[dict[str, object]]:
    # Cada tupla representa una cifra efectivamente publicada en el bloque indicado.
    specs = [
        ("R02 · Avenida Corrientes", "Corrientes y Callao", "Corrientes y Callao", 94.0, 1.1, None),
        ("R02 · Avenida Corrientes", "Corrientes y Pueyrredón", "Corrientes y Pueyrredón", 97.0, 0.6, None),
        ("R03 · San Telmo", "Defensa", "Defensa", 84.8, 2.7, None),
        ("R04 · Puerto Madero", "Puerto Madero", "Puerto Madero", 87.6, 1.3, 2.23),
        ("R12 · Centro y Microcentro", "Florida", "Florida", 86.8, -3.2, None),
        ("R12 · Centro y Microcentro", "Lavalle", "Lavalle", 80.3, -3.2, None),
        ("Z46 · Retiro", "Florida", "Florida", 86.8, -3.2, None),
        ("Z47 · Monserrat y Congreso", "Monserrat", "Monserrat", 88.5, -1.4, 9.93),
        ("R06 · Recoleta", "Recoleta", "Recoleta", 89.5, -3.2, 5.94),
        ("R07 · Abasto", "Once", "Once", 92.2, -1.6, None),
        ("R07 · Abasto", "Corrientes y Medrano", "Corrientes y Medrano", 90.3, -2.7, None),
        ("Z35 · Balvanera y Once", "Once", "Once", 92.2, -1.6, None),
        ("Z50 · Montes de Oca", "Montes de Oca", "Montes de Oca", 89.7, -1.9, None),
        ("Z40 · Nueva Pompeya y Parque Patricios", "Parque Patricios", "Parque Patricios", 89.2, 1.4, None),
        ("Z40 · Nueva Pompeya y Parque Patricios", "Av. Patricios", "Av. Patricios", 88.2, 1.1, None),
        ("Z40 · Nueva Pompeya y Parque Patricios", "Av. Sáenz", "Sáenz", 87.3, -1.5, 17.67),
        ("R14 · Avenida Boedo", "Boedo", "Boedo", 91.2, -1.8, None),
        ("Z37 · Almagro", "Almagro", "Almagro", 94.5, -1.0, None),
        ("Z38 · Caballito", "Caballito", "Caballito", 96.7, -0.3, None),
        ("R15 · Avellaneda y pasaje comercial", "Avellaneda", "Avellaneda", 94.6, -0.2, 23.33),
        ("R16 · Enclave coreano", "Flores Sur", "Flores Sur", 92.6, 3.3, 20.17),
        ("Z32 · Liniers", "Liniers", "Liniers", 92.9, 0.0, 18.2),
        ("Z33 · Mataderos", "Mataderos", "Mataderos", 92.3, -1.4, None),
        ("Z27 · Parque Avellaneda", "Parque Avellaneda", "Parque Avellaneda", 77.8, 2.5, None),
        ("Z28 · Monte Castro", "Monte Castro", "Monte Castro", 86.9, -5.1, 18.61),
        ("R18 · Devoto", "Devoto", "Devoto", 88.1, -1.8, 16.0),
        ("Z39 · Villa Urquiza", "Triunvirato", "Triunvirato", 92.1, -1.3, 16.44),
        ("R10 · García del Río", "Cabildo", "Cabildo", 91.8, -3.8, None),
        ("R11 · Belgrano", "Cabildo", "Cabildo", 91.8, -3.8, None),
        ("R09 · Federico Lacroze", "Chacarita", "Chacarita", 91.8, -1.6, None),
        ("R09 · Federico Lacroze", "Colegiales", "Colegiales", 91.2, -0.4, None),
        ("Z43 · Colegiales", "Colegiales", "Colegiales", 91.2, -0.4, None),
        ("R20 · Palermo", "Palermo Soho", "Palermo Soho", 87.3, -1.4, None),
        ("R08 · Villa Crespo", "Villa Crespo", "Villa Crespo", 79.8, -9.1, None),
        ("R19 · Chacarita", "Chacarita", "Chacarita", 91.8, -1.6, None),
        ("Z42 · La Paternal", "Warnes", "Warnes", 82.5, -6.8, None),
        ("Z42 · La Paternal", "Av. San Martín", "Av. San Martín", 88.9, 3.2, None),
        ("Flores · casco histórico", "Flores", "Flores", 90.5, -2.4, 15.24),
    ]
    rows: list[dict[str, object]] = [
        {
            "pagina": "Apertura · síntesis comercial", "eje_citado": "Conjunto de 48 ejes",
            "eje_en_la_fuente": "Total", "valor_citado": "variacion_interanual=-1.6 pp",
            "valor_en_la_fuente": "variacion_interanual=-1.561567 pp",
            "anio": "2026 (1er cuatrimestre)", "coincide": "sí (redondeo publicado)",
            "superlativo_citado": "", "superlativo_correcto": "",
        },
        {
            "pagina": "Apertura · síntesis comercial", "eje_citado": "Norte (9 ejes)",
            "eje_en_la_fuente": "Zona Norte del informe", "valor_citado": "9 de 9 con baja interanual",
            "valor_en_la_fuente": "9 de 9 con baja interanual",
            "anio": "2026 (1er cuatrimestre)", "coincide": "sí",
            "superlativo_citado": "", "superlativo_correcto": "",
        },
        {
            "pagina": "Apertura · síntesis comercial", "eje_citado": "Sur",
            "eje_en_la_fuente": "Zona Sur del informe", "valor_citado": "media interanual positiva",
            "valor_en_la_fuente": "media interanual positiva",
            "anio": "2026 (1er cuatrimestre)", "coincide": "sí",
            "superlativo_citado": "única zona con media positiva",
            "superlativo_correcto": "sí: única zona con media positiva",
        },
    ]
    for page, cited, official, occ, var, density in specs:
        occ_super = ""
        occ_correct = ""
        var_super = ""
        var_correct = ""
        den_super = ""
        den_correct = ""
        if official == "Lavalle":
            occ_super, occ_correct = "tercera peor ocupación de 48", "sí: 3.º menor valor"
        elif official == "Parque Avellaneda":
            occ_super, occ_correct = "peor ocupación de 48", "sí: menor valor"
        elif official == "Almagro":
            occ_super, occ_correct = "entre los ejes más llenos", "sí: 4.º mayor valor"
        elif official == "Caballito":
            occ_super, occ_correct = "entre los ejes más llenos", "sí: 2.º mayor valor"
        if official == "Monte Castro":
            var_super = "quinta mayor caída de 48"
            var_correct = "sí: 5.ª mayor caída con valores exactos"
        elif official == "Colegiales" and page == "R09 · Federico Lacroze":
            var_super = "caída más chica de los ejes atribuidos por el documento"
            var_correct = "no: Caballito cayó menos y Liniers subió 0,039463 puntos"
        elif official == "Colegiales" and page == "Z43 · Colegiales":
            var_super = "sólo Caballito cayó menos y cuatro ejes subieron"
            var_correct = "no: Liniers subió 0,039463 puntos; hubo cinco subas, no cuatro"
        elif official == "Flores Sur":
            var_super, var_correct = "entre las mayores subas", "sí: 3.ª mayor suba"
        elif official == "Villa Crespo":
            var_super, var_correct = "mayor caída de 48", "sí: mayor caída"
        elif official == "Warnes":
            var_super = "empate en tercer puesto entre mayores caídas"
            var_correct = "no: Warnes es 3.º con -6,830396; Santa Fe y Callao es 4.º con -6,763471"
        elif official == "Av. San Martín":
            var_super, var_correct = "entre las mayores subas", "sí: 4.ª mayor suba"
        if official == "Puerto Madero":
            den_super, den_correct = "menor densidad de 48", "sí: menor valor"
        elif official == "Recoleta":
            den_super, den_correct = "segunda menor densidad de 48", "sí: 2.º menor valor"
        elif official == "Sáenz":
            den_super, den_correct = "entre los ejes más densos", "sí: 8.º mayor valor"
        elif official == "Avellaneda":
            den_super, den_correct = "mayor densidad de 48", "sí: mayor valor"
        elif official == "Flores Sur":
            den_super, den_correct = "tercera mayor densidad de 48", "sí: 3.º mayor valor"
        elif official == "Liniers":
            den_super, den_correct = "sexta mayor densidad de 48", "sí: 6.º mayor valor"
        elif official == "Monte Castro":
            den_super, den_correct = "quinta mayor densidad de 48", "sí: 5.º mayor valor"
        add_claim(rows, page, cited, official, "ocupacion", occ, occ_super, occ_correct)
        add_claim(rows, page, cited, official, "variacion_interanual", var, var_super, var_correct)
        if density is not None:
            add_claim(rows, page, cited, official, "densidad", density, den_super, den_correct)
    exact = {r["eje"]: r for r in read_csv(EJES)}
    exact_key = {
        "ocupacion": "tasa_de_ocupación", "variacion_interanual": "variación_interanual",
        "densidad": "densidad_comercial",
    }
    unit = {"ocupacion": "%", "variacion_interanual": "pp", "densidad": "locales/frente de manzana"}
    for row in rows[3:]:
        metric = str(row["valor_citado"]).split("=", 1)[0]
        value = float(exact[str(row["eje_en_la_fuente"])][exact_key[metric]])
        rendered = f"{value:.6f}".rstrip("0").rstrip(".")
        row["valor_en_la_fuente"] = f"{metric}={rendered} {unit[metric]}"
        if metric == "densidad":
            row["coincide"] = "sí en valor redondeado; no en unidad publicada"
        elif metric == "variacion_interanual" and row["eje_en_la_fuente"] == "Liniers":
            row["coincide"] = "sí por redondeo; no para la lectura ‘sin movimiento’"
        else:
            row["coincide"] = "sí (redondeo publicado)"
    return rows


def validate_axis_values(rows: list[dict[str, object]]) -> None:
    official = {r["eje"]: r for r in read_csv(EJES)}
    key_by_metric = {
        "ocupacion": "tasa_de_ocupación", "variacion_interanual": "variación_interanual",
        "densidad": "densidad_comercial",
    }
    for row in rows[3:]:
        metric, tail = str(row["valor_citado"]).split("=", 1)
        number = float(tail.split()[0])
        expected = float(official[str(row["eje_en_la_fuente"])][key_by_metric[metric]])
        decimals = 2 if metric == "densidad" else 1
        if number != round(expected, decimals):
            raise ValueError(f"Desajuste en {row['pagina']} / {row['eje_en_la_fuente']} / {metric}")


def write_report(hist: list[dict[str, object]], locals_: list[dict[str, object]], axes: list[dict[str, object]]) -> None:
    improved_hist = sum(r["nivel_resultante"] == "v2" for r in hist)
    pending_hist = len(hist) - improved_hist
    improved_local = sum(r["estado"] == "abierto_a_fecha_fuente" for r in locals_)
    wrong_super = sum(str(r["superlativo_correcto"]).startswith("no:") for r in axes)
    wrong_units = sum("no en unidad" in str(r["coincide"]) for r in axes)
    text = f"""# Valores que cambiaron

- **Vigencia histórica:** {improved_hist} de 54 registros pasan de catálogo sin fecha a evidencia pública individual fechada; {pending_hist} continúan pendientes. No se incorporan cierres. Origen: universo provisto y publicaciones públicas enumeradas en la tabla, corte 2026-08-10.
- **Locales sin vigencia reciente:** {improved_local} de 19 obtienen evidencia posterior al antecedente disponible: Brest Patisserie, Bulmat, Ichiban y Matok. Los otros {19-improved_local} no se declaran cerrados. Fuentes: [Buenos Aires Connect, 2026-05-09](https://buenosairesconnect.com/barrio-villa-luro/), [TN, 2025-02-06](https://tn.com.ar/turismo/2025/02/06/el-pintoresco-pasaje-coreano-en-pleno-buenos-aires-con-arte-callejero-cafes-karaokes-y-restaurantes/) y [Mashala Digital, 2025-05-09](https://mashaladigital.com/kosher-matok-en-flores-ahora-mas-grande-mas-lindo-y-con-mas-de-todo/).
- **Domicilios:** La Mezzetta queda en Av. Álvarez Thomas 1321; San Carlos, en Av. Rivadavia 4548; Saverio adopta Av. San Juan 2809 para el acceso público y conserva pendiente el vínculo con el número 2816. Fuentes y fechas: [Legislatura de la Ciudad, 2024-05-10](https://parlamentaria.legislatura.gob.ar/pages/download.aspx?IdDoc=206457), [sitio del establecimiento](https://sancarlospizza.com/) y [Canal 26, 2026-05-11](https://www.canal26.com/turismo/2026/05/11/la-pizzeria-de-caballito-con-show-de-pizza-en-el-aire-donde-queda-y-cuanto-cuesta/), [Viajes y Turismo, actualizado 2026-03-02](https://viagemeturismo.abril.com.br/mundo/7-gelaterias-para-se-deliciar-em-buenos-aires/) y [ficha turística oficial sin fecha editorial](https://turismo.buenosaires.gob.ar/es/gastronomico/saverio).
- **Contexto comercial:** los valores numéricos coinciden por redondeo con el cuadro oficial de 48 ejes, pero las {wrong_units} menciones de densidad publican una unidad incorrecta. Debe decirse “locales relevados por frente de manzana”. Fuente: [IDECBA, primer cuatrimestre de 2026, publicado el 2026-06-11](https://www.estadisticaciudad.gob.ar/eyc/wp-content/uploads/2026/06/ir_2026_2033.pdf).
- **Comparaciones:** se corrigen {wrong_super} formulaciones. Warnes ocupa el tercer lugar sin empate; Colegiales no presenta la menor caída del conjunto atribuido; y Liniers subió 0,039463 puntos, por lo que hubo cinco subas y no cuatro. Fuente: cálculo reproducible sobre los valores oficiales sin redondear, 2026-08-10.

## Alcance y criterio

La revisión usa como fecha de corte el **2026-08-10**. Una programación oficial o una pieza periodística fechada acredita actividad únicamente a la fecha de la pieza; no prueba atención el día del corte. Un directorio sin fecha, un catálogo de entrega o el rótulo de un agregador no se acepta como verificación de apertura. Este criterio de decisión se fijó antes de clasificar los resultados y no se modificó durante la búsqueda.

Los 54 históricos se reordenan poniendo primero los registros que también aparecen entre las 42 observaciones exteriores. La marca es booleana y se conserva el universo completo: ningún registro se elimina. Origen: cruce determinístico de los dos universos provistos, ejecutado el 2026-08-10.

## Vigencia de establecimientos históricos

Las mejoras se sostienen en actividades individualizadas por el Gobierno de la Ciudad o su sitio turístico: [programación del 2022-10-28](https://buenosaires.gob.ar/sites/default/files/media/document/2022/10/25/76961abb6ac6cfd729e46cbd62f3328b39ac793a.pdf); [programación del 2024-11-02](https://buenosaires.gob.ar/sites/default/files/2024-10/Programaci%C3%B3n_0.pdf); [agenda del 2025-10-16](https://buenosaires.gob.ar/sites/default/files/2025-10/DBA%20701%20WEB_0.pdf); [actividades del 2025-11-08](https://buenosaires.gob.ar/noticias/charlas-en-los-bares-notables-de-la-ciudad); [agenda de mayo de 2026](https://buenosaires.gob.ar/gcaba_historico/noticias/actividades-de-mayo-en-los-bares-notables); e [itinerario del 2026-07-23](https://buenosaires.gob.ar/gcaba_historico/noticias/borges-vuelve-los-bares-notables). Cada fila conserva la URL y la fecha aplicable. Estas señales llevan a **v2**, no a una afirmación de apertura actual.

También se localizaron piezas individuales o agendas fechadas para Café Roma (2025-06-22), Cabildo de Buenos Aires (2026-05-25), La Escuela (2026-07-16), Café Rivas (2026-02-06), Café Tabac (2026-03-03), [Café Thibon (2026-05-31)](https://www.usal.edu.ar/best/beneficios/), Clásica y Moderna (2026-07-16), Le Caravelle (2026-07-14), Miramar (2026-07-01), Montecarlo Bar y Despensa (2026-02-14), Claridge's Bar y Bar Imperio (2026-05-30), y Plaza Café (2025-09-27). Fuentes: enlaces públicos individualizados en cada fila, consultados el 2026-08-10. El cierre de Café Thibon informado en 2023 no se trasladó al presente porque fue seguido por una reapertura documentada en 2024 y por el beneficio operativo de 2026.

Los {pending_hist} casos restantes siguen en **v1** porque no se localizó una pieza pública individual y fechada que superara el antecedente. Esto incluye los casos en que existe una ficha oficial vigente pero sin fecha editorial. Resultado al 2026-08-10: **pendiente**, no cerrado.

## Verificación de 19 locales

[Brest Patisserie tiene una pieza barrial fechada el 2026-05-09](https://buenosairesconnect.com/barrio-villa-luro/); [Bulmat e Ichiban aparecen individualizados en una nota del 2025-02-06](https://tn.com.ar/turismo/2025/02/06/el-pintoresco-pasaje-coreano-en-pleno-buenos-aires-con-arte-callejero-cafes-karaokes-y-restaurantes/); [Matok cuenta con una pieza comunitaria del 2025-05-09](https://mashaladigital.com/kosher-matok-en-flores-ahora-mas-grande-mas-lindo-y-con-mas-de-todo/) que documenta su reapertura. Esas cuatro filas pasan a “abierto a fecha de fuente”, nivel v2.

Para los otros 15 se mantuvo el antecedente público disponible y se documentó la búsqueda negativa. Los resultados sin fecha editorial y los catálogos de entrega fueron revisados sólo como pistas y no como prueba. Fuente: búsquedas públicas realizadas el 2026-08-10; conclusión: vigencia no verificada.

## Conflictos de domicilio

**La Mezzetta.** Se adopta Av. Álvarez Thomas 1321. [Un documento legislativo fechado el 2024-05-10](https://parlamentaria.legislatura.gob.ar/pages/download.aspx?IdDoc=206457) y [una publicación oficial del 2018-09-07](https://buenosaires.gob.ar/gcaba_historico/noticias/los-vecinos-eligieron-las-mejores-pizzerias-de-buenos-aires) coinciden en ese número; la ficha turística que informa 1311 queda registrada como discrepancia. No cambia la asignación territorial vigente.

**San Carlos.** Se adopta Av. Rivadavia 4548. [El sitio del establecimiento, consultado el 2026-08-10](https://sancarlospizza.com/) y [una pieza fechada el 2026-05-11](https://www.canal26.com/turismo/2026/05/11/la-pizzeria-de-caballito-con-show-de-pizza-en-el-aire-donde-queda-y-cuanto-cuesta/) coinciden; “Av. La Plata” describe la cercanía de la esquina y no una segunda sede. No cambia la asignación territorial vigente.

**Saverio.** Se adopta Av. San Juan 2809 como acceso público por ser el dato de [la pieza pública actualizada el 2026-03-02](https://viagemeturismo.abril.com.br/mundo/7-gelaterias-para-se-deliciar-em-buenos-aires/). [La ficha turística oficial sin fecha editorial](https://turismo.buenosaires.gob.ar/es/gastronomico/saverio) conserva 2816. Como ambos números están enfrentados, queda pendiente verificar habilitación o parcela y establecer si se trata del mismo inmueble o de accesos distintos. No se fuerza una resolución catastral con evidencia insuficiente.

## Auditoría de ejes comerciales

Se contrastaron {len(axes)} menciones numéricas, incluidas las repeticiones publicadas. Para ocupación y variación interanual, eje, valor, período y universo coinciden con el [cuadro oficial del primer cuatrimestre de 2026](https://www.estadisticaciudad.gob.ar/eyc/banco-datos/locales-relevados-ocupados-densidad-comercial-tasa-de-ocupacion-y-variacion-respecto-del-relevamiento-previo-e-interanual-por-eje-comercial-48-ejes-comerciales-ciudad-de-buenos-aires-1er-cuatri/). Para densidad, el valor coincide pero la etiqueta no: el Instituto divide locales relevados por frentes de manzana. Fuente: [IDECBA, reporte publicado el 2026-06-11](https://www.estadisticaciudad.gob.ar/eyc/wp-content/uploads/2026/06/ir_2026_2033.pdf).

Las tres comparaciones que requieren corrección quedan marcadas con “no” y su formulación correcta en la tabla. El resto de los ordinales se recalculó sobre los 48 ejes completos usando los decimales sin redondear. Cálculo: tabla oficial de 48 filas, reproducido el 2026-08-10.

## Pendientes explícitos

- {pending_hist} establecimientos históricos continúan sin pieza pública individual fechada posterior que permita subir de v1.
- 15 de los 19 locales continúan con vigencia no verificada; no se interpretan como cierres.
- Saverio requiere verificación municipal, catastral o de campo para vincular 2809 y 2816.
- El archivo fuente en formato de planilla no pudo abrirse con el entorno de artefactos exigido porque esa capacidad no estaba disponible. La comprobación se hizo contra la página oficial del banco de datos, el informe oficial y la copia tabular ya trazada a ese cuadro; no se instaló un lector alternativo ni se estimaron valores.
- El documento principal no fue modificado. La corrección de unidad y las tres formulaciones comparativas quedan listas para una edición posterior autorizada.

## Control de cierre

Se revisaron los entregables al 2026-08-10 para excluir correos, teléfonos, identificadores fiscales, claves, enlaces privados y nombres de personas no necesarios. No se modificaron fuentes originales, datos crudos, geometrías, pipelines ni el documento principal. No se hicieron envíos ni publicaciones.
"""
    (OUT / "INFORME.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hist = historical_rows()
    locals_ = local_rows()
    conflicts = conflict_rows()
    axes = axis_claims()
    validate_axis_values(axes)
    hist_fields = [
        "orden_prioridad", "nombre", "barrio", "polo_id", "polo_nombre",
        "hitos_reconocidos_en_polo", "criterio_prioridad", "estado_previo", "nivel_previo",
        "dias_desde_verificacion_previa", "resultado", "nivel_resultante", "fecha_nueva",
        "fuente_nueva", "observaciones", "es_de_los_42",
    ]
    write_csv(OUT / "vigencia_historicos_ronda_19.csv", hist, hist_fields)
    write_csv(OUT / "verificacion_locales_ronda_19.csv", locals_, [
        "polo", "nombre", "direccion", "existe", "estado", "fuente", "fecha",
        "nivel_de_verificacion", "observaciones",
    ])
    write_csv(OUT / "conflictos_direccion_ronda_19.csv", conflicts, [
        "establecimiento", "direccion_previa", "direccion_en_conflicto", "direccion_adoptada",
        "estado_resolucion", "criterio", "fuentes_publicas", "fecha_fuente_mas_reciente",
        "impacto_en_polos", "pendiente",
    ])
    write_csv(OUT / "ejes_comerciales_control.csv", axes, [
        "pagina", "eje_citado", "eje_en_la_fuente", "valor_citado", "valor_en_la_fuente",
        "anio", "coincide", "superlativo_citado", "superlativo_correcto",
    ])
    # Copia técnica coherente con un nombre provisional ya generado; no se elimina sin autorización.
    write_csv(OUT / "auditoria_ejes_comerciales_ronda_19.csv", axes, [
        "pagina", "eje_citado", "eje_en_la_fuente", "valor_citado", "valor_en_la_fuente",
        "anio", "coincide", "superlativo_citado", "superlativo_correcto",
    ])
    write_report(hist, locals_, axes)


if __name__ == "__main__":
    main()
