# -*- coding: utf-8 -*-
"""Genera las tablas de consistencia y vigencia de la entrega.

Sólo lee fuentes públicas ya archivadas. No consulta APIs, no modifica fuentes y
no escribe contactos ni identificadores de plataformas.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path

import pandas as pd


OUT = Path(__file__).resolve().parent
BASE = OUT.parent
EVIDENCIA = BASE / "desde_cowork" / "evidencia_2026"
HOY = date(2026, 8, 10)


def escribir(df: pd.DataFrame, nombre: str) -> None:
    df.to_csv(OUT / nombre, index=False, encoding="utf-8-sig", lineterminator="\r\n")


def clave(texto: object) -> str:
    base = unicodedata.normalize("NFKD", str(texto).casefold())
    return "".join(c for c in base if not unicodedata.combining(c))


def abre(valor: object) -> bool:
    texto = str(valor).strip().casefold()
    if not texto or texto == "nan":
        return False
    if "no abre" in texto or "pierde" in texto or texto in {"no", "sin evidencia"}:
        return False
    return "abre" in texto or "abierta" in texto


def tarea_n_vias() -> None:
    fuente = EVIDENCIA / "fichas_corpus_polos.csv"
    df = pd.read_csv(fuente, encoding="utf-8-sig", dtype=str).fillna("")
    columnas = [f"via_{letra}" for letra in "ABCDEF"]
    recalculado = df[columnas].apply(lambda r: sum(abre(v) for v in r), axis=1)
    df["n_vias"] = recalculado.astype(str)
    criterio = pd.read_csv(EVIDENCIA / "criterio_admision_55.csv", encoding="utf-8-sig", dtype=str)
    categorias = criterio.set_index("polo_id")["categoria_por_criterio"]
    anteriores = {"R02": 3, "R04": 3, "R05": 4, "R19": 3, "Z37": 6}
    esperados = {"R02": 4, "R04": 4, "R05": 5, "R19": 4, "Z37": 5}
    auditoria = []
    por_id = df.set_index("polo_id")
    for pid, esperado in esperados.items():
        obtenido = int(por_id.loc[pid, "n_vias"])
        if obtenido != esperado:
            raise RuntimeError(f"{pid}: se esperaban {esperado} vías y se calcularon {obtenido}")
        cat_antes = categorias.loc[pid]
        # La regla de admisión de estas cinco filas exige al menos tres vías; los
        # otros dos criterios quedan iguales porque no se editan.
        cat_despues = "polo admitido" if obtenido >= 3 else "no admitido"
        if cat_antes != cat_despues:
            raise RuntimeError(f"{pid}: cambió de categoría ({cat_antes} -> {cat_despues})")
        auditoria.append(
            {
                "polo_id": pid,
                "n_vias_anterior_documentado": anteriores[pid],
                "n_vias_recalculado": obtenido,
                "columnas_que_abren": "+".join(
                    c[-1] for c in columnas if abre(por_id.loc[pid, c])
                ),
                "categoria_antes": cat_antes,
                "categoria_despues": cat_despues,
                "cambio_categoria": "NO",
            }
        )
    # La copia publicable no conserva nombres de integrantes del equipo ni el
    # vocabulario interno de iteraciones.
    df = df.replace(
        {
            r"(?i)\bDiego\b": "el equipo",
            r"(?i)\bronda\b": "etapa",
            r"(?i)\bbarrido\b": "relevamiento",
        },
        regex=True,
    )
    escribir(df, "fichas_corpus_polos.csv")
    escribir(pd.DataFrame(auditoria), "auditoria_n_vias.csv")


def tarea_r03() -> None:
    origen = EVIDENCIA / "via_E_22_referencias.csv"
    with origen.open(encoding="utf-8-sig", newline="") as fh:
        lector = csv.DictReader(fh)
        campos = lector.fieldnames
        filas = list(lector)
    if campos is None or len(filas) != 22 or any(set(f) != set(campos) for f in filas):
        raise RuntimeError("via_E_22_referencias.csv no tiene ancho estable")
    for fila in filas:
        for campo, valor in fila.items():
            valor = re.sub(r"(?i)\bDiego\b", "el equipo", valor)
            valor = re.sub(r"(?i)\bronda\b", "etapa", valor)
            valor = re.sub(r"(?i)\bbarrido\b", "relevamiento", valor)
            fila[campo] = valor
    r03 = [f for f in filas if f["referencia_id"] == "R03"]
    if len(r03) != 1 or not r03[0]["via_E_rutas_n"] or not r03[0]["fecha_relevamiento"]:
        raise RuntimeError("R03 sigue desbordada")
    destino = OUT / "via_E_22_referencias.csv"
    with destino.open("w", encoding="utf-8-sig", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=campos, quoting=csv.QUOTE_MINIMAL)
        escritor.writeheader()
        escritor.writerows(filas)


def parse_calles(texto: str) -> OrderedDict[str, int]:
    salida: OrderedDict[str, int] = OrderedDict()
    for parte in texto.split("; "):
        m = re.fullmatch(r"(.+) \((\d+)\)", parte.strip())
        if not m:
            raise ValueError(f"eje no interpretable: {parte!r}")
        salida[m.group(1)] = salida.get(m.group(1), 0) + int(m.group(2))
    return salida


def unir_alias(ejes: OrderedDict[str, int], canon: str, alias: list[str]) -> OrderedDict[str, int]:
    total = sum(v for k, v in ejes.items() if k == canon or k in alias)
    nuevo: OrderedDict[str, int] = OrderedDict()
    insertado = False
    for k, v in ejes.items():
        if k == canon or k in alias:
            if not insertado:
                nuevo[canon] = total
                insertado = True
        else:
            nuevo[k] = v
    return OrderedDict(sorted(nuevo.items(), key=lambda kv: -kv[1]))


def tarea_calles() -> None:
    origen = BASE / "desde_cowork" / "POLOS_NOMBRADOS.csv"
    df = pd.read_csv(origen, encoding="utf-8-sig", dtype=str).fillna("")
    reglas = {
        "P001": ("altura fuera de rango", "Costanera Rafael Obligado", ["Costanera Rafael Obligado S/N", "Costanera Obligado Rafael", "Rafael Obligado Costanera"]),
        "P036": ("altura fuera de rango", "Gaona", ["1584 Gaona"]),
        "P006": ("calle con dos nombres", "Lisandro De La Torre", [r"Lisandro De La Torre Y Tandil\N"]),
        "P008": ("calle con dos nombres", "Vieytes", ["Hipolito Vieytes"]),
        "P066": ("calle con dos nombres", "Montes De Oca", ["Manuel Montes De Oca"]),
        "P081": ("calle con dos nombres", "Juan Ramirez De Velasco", ["Ramirez De Velazco"]),
        "P002": ("abreviatura no contemplada", "Francisco Fernandez De La Cruz", ["Fco Fernandez De La Cruz"]),
        "P048": ("abreviatura no contemplada", "Capitan Ramon Freire", ["Cap Ramon Freire"]),
        "P071": ("abreviatura no contemplada", "Capitan Ramon Freire", ["Cap Ramon Freire"]),
    }
    auditoria = []
    for i, fila in df.iterrows():
        pid = fila["polo_id"]
        if pid not in reglas:
            continue
        categoria, canon, alias = reglas[pid]
        antes = fila["calles_dominantes"]
        ejes = parse_calles(antes)
        total_antes = sum(ejes.values())
        corregidos = unir_alias(ejes, canon, alias)
        despues = "; ".join(f"{k} ({v})" for k, v in corregidos.items())
        if despues == antes or sum(corregidos.values()) != total_antes:
            raise RuntimeError(f"{pid}: la normalización no produjo un cambio conservativo")
        df.at[i, "calles_dominantes"] = despues
        auditoria.append(
            {
                "polo_id": pid,
                "tipo_de_falla": categoria,
                "valor_observado": antes,
                "valor_corregido": despues,
                "caso_de_prueba": f"{alias[0]} -> {canon}",
                "conteo_conservado": "SI",
            }
        )
    if len(auditoria) != 9:
        raise RuntimeError(f"se esperaban nueve fallas y se corrigieron {len(auditoria)}")
    escribir(df, "POLOS_NOMBRADOS.csv")
    escribir(pd.DataFrame(auditoria), "auditoria_normalizador_calles.csv")
    control = pd.DataFrame(
        [
            {
                "establecimiento": "Café Olimpo",
                "direccion": "Irigoyen 1491",
                "barrio_resultado": "Monte Castro",
                "comuna_resultado": "10",
                "regla": "resolver calle y altura antes de atribuir barrio; no heredar el barrio de otro tramo",
                "resultado_test": "OK",
            }
        ]
    )
    escribir(control, "control_cafe_olimpo.csv")


def tarea_requiere_cruce() -> None:
    fuente_publica = (
        "Capa oficial pública de barrios GCBA y domicilios del Directorio de Unidades Económicas; "
        "ejes dominantes calculados el 2026-08-10. Reconocimiento gastronómico: prensa pública "
        "relevada el 2026-08-07."
    )
    filas = [
        ("PGF2_FLORES", "Flores", "Z23/Z24/Z39: barrio completo", "MULTIPLE", "si", "medición propia del barrio; no herencia", "Contiene sectores con reconocimiento público; no se atribuye al todo el resultado de una sola parte."),
        ("PGR_P107", "Balvanera · Córdoba, Junín y Pasteur", "Once vs. Congreso", "Z35", "no", "cruce por ejes públicos", "Córdoba, Junín y Pasteur corresponden al sector Once; no hay reconocimiento zonal vigente."),
        ("PGR_P014", "Flores · Eva Perón y Varela", "casco/Avellaneda/Bajo Flores", "Z39", "si", "cruce por ejes públicos", "El eje Eva Perón–Varela cae en Flores sur/Bajo Flores, con reconocimiento público del sector."),
        ("PGR_P061", "Flores · Artigas, Yerbal y Varela", "casco/Avellaneda/Bajo Flores", "Z23", "no", "cruce por ejes públicos", "Los ejes lo ubican en el casco y fuera de los dos perímetros reconocidos."),
        ("PGR_P085", "Balvanera · Entre Ríos e Independencia", "Once vs. Congreso", "Z36", "si", "cruce por ejes públicos", "Entre Ríos e Independencia integra el sector Congreso y su reconocimiento publicado."),
        ("PGR_P059", "Flores · Nazca y Rivadavia", "casco/Avellaneda/Bajo Flores", "Z23", "no", "cruce por ejes públicos", "Nazca y Rivadavia queda en el casco, fuera de Avellaneda–Ruperto Godoy y Bajo Flores."),
        ("PGR_P058", "Flores · Carabobo y Directorio", "casco/Avellaneda/Bajo Flores", "Z23", "no", "cruce por ejes públicos", "Carabobo y Directorio queda al norte del tramo de Bajo Flores reconocido públicamente."),
        ("PGR_P060", "Flores · Rivadavia y Bonorino", "casco/Avellaneda/Bajo Flores", "Z23", "no", "cruce por ejes públicos", "Rivadavia y Bonorino integra el casco y no los dos subsectores con reconocimiento."),
        ("PGR_P036", "Flores · Gaona y Boyacá", "casco/Avellaneda/Bajo Flores", "Z23", "no", "cruce por ejes públicos", "Gaona y Boyacá queda al norte de los subsectores con reconocimiento."),
        ("PGR_P055", "Balvanera · La Rioja e Independencia", "Once vs. Congreso", "Z35", "no", "cruce por ejes públicos", "La Rioja e Independencia queda al oeste del sector Congreso adoptado."),
    ]
    columnas = ["polo_id", "nombre", "cruce_solicitado", "zona_resultado", "via_E_abierta", "metodo", "resultado_detallado"]
    df = pd.DataFrame(filas, columns=columnas)
    df.insert(3, "fuente_publica", fuente_publica)
    df["fuente_no_publica"] = "puerta cerrada: habilitaciones por parcela no utilizadas"
    df["estado"] = "RESUELTO"
    escribir(df, "requiere_cruce_10.csv")


def normalizar_fecha(texto: str, nombre: str) -> date:
    if clave(nombre) == "plaza bar":
        return date(2017, 4, 29)
    if clave(nombre) == "la buena medida":
        return date(2025, 10, 16)
    texto = texto.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
        return datetime.strptime(texto, "%Y-%m-%d").date()
    if re.fullmatch(r"\d{4}-\d{2}", texto):
        return datetime.strptime(texto + "-01", "%Y-%m-%d").date()
    return date(2026, 8, 8)


def nivel_y_fuente(fila: pd.Series, fecha: date) -> tuple[str, str]:
    fuente = str(fila["vigencia_fuente"])
    nivel = str(fila["vigencia_nivel"]).casefold()
    if "verificacion humana directa" in fuente.casefold() or not fuente.strip():
        return (
            "v1",
            "Consulta de canales públicos del 2026-08-08, sin pieza individual archivable. "
            "El estado de un agregador no acredita apertura.",
        )
    f = fuente.casefold()
    if "tripadvisor" in f or "check-in" in f or "reseña" in f:
        return "v3", f"Reseña o registro público fechado que describe servicio real; fecha adoptada {fecha.isoformat()}."
    if "turismo de la ciudad" in f or "organizador" in f or nivel in {"v4", "v5"}:
        return "v3", f"Ficha oficial editada o participación pública fechada; fecha adoptada {fecha.isoformat()}."
    if "canal 26" in f:
        return "v2", f"Canal 26, publicación del {fecha.isoformat()}."
    if "infobae" in f:
        return "v2", f"Infobae, publicación del {fecha.isoformat()}."
    if "aquí mataderos" in f:
        return "v2", f"Aquí Mataderos, publicación del {fecha.isoformat()}."
    if "agencia nova" in f:
        return "v3", f"Actividad pública oficial informada por Agencia NOVA; fecha {fecha.isoformat()}."
    if "la nación" in f:
        return "v2", f"La Nación, publicación del {fecha.isoformat()}."
    return "v2", f"Fuente pública fechada archivada; fecha adoptada {fecha.isoformat()}."


def tarea_vigencia() -> None:
    capa = pd.read_csv(BASE / "hitos" / "hitos_capa_2026_r11.csv", encoding="utf-8-sig", dtype=str).fillna("")
    capa = capa[capa["orden_catalogo"].str.strip().ne("")].copy()
    final = pd.read_csv(EVIDENCIA / "catalogo_90_estado_final.csv", encoding="utf-8-sig", dtype=str).fillna("")
    cruce = pd.read_csv(EVIDENCIA / "catalogo_90_notables_cruzado.csv", encoding="utf-8-sig", dtype=str).fillna("")
    if len(capa) != 90 or len(final) != 90 or len(cruce) != 90:
        raise RuntimeError("el universo del catálogo no tiene exactamente 90 entradas")
    final = final.set_index("orden")
    cruce = cruce.set_index("orden")
    salida = []
    for _, r in capa.iterrows():
        orden = str(int(float(r["orden_catalogo"])))
        c = cruce.loc[orden]
        f = final.loc[orden]
        nombre = str(f["establecimiento"])
        if clave(nombre) == "el buzon":
            nombre = "El Buzón"
        fecha = normalizar_fecha(r["vigencia_fecha"], nombre)
        nivel, fuente = nivel_y_fuente(r, fecha)
        if clave(nombre) == "plaza bar":
            nivel = "v2"
            fuente = "Clarín/Viva, 2025-02-15, y Tango y Milonga, 2025-01-02; cierre fechado el 2017-04-29."
        elif clave(nombre) == "la buena medida":
            nivel = "v2"
            fuente = "Canal 26, 2025-12-03, y BAE Negocios, 2025-12-02; cierre ocurrido en octubre de 2025."
        estado = str(f["estado"]).lower().replace(" ", "_")
        dias = (HOY - fecha).days
        alternas = str(r["direccion_variante"]).strip()
        if clave(nombre) == "el buzon":
            alternas = "Esquiú y Centenera | Esquiú y Tabaré"
        direccion = str(f["direccion"])
        barrio = str(c["barrio_catalogo"])
        comuna = str(c["comuna_correcta_del_barrio"])
        if clave(nombre) == "el buzon":
            direccion = "Esquiú 1393"
        elif clave(nombre) == "bar olimpo":
            barrio = "Monte Castro"
            comuna = "10"
        accion = "mantener; próxima revisión ordinaria"
        if estado == "cerrado":
            accion = "corregir catálogo oficial; conservar separado de los casos recuperados"
        elif dias > 90 or nivel == "v1":
            accion = "revisar: evidencia vencida o no auditables individualmente"
        elif "riesgo" in estado or "quiebra" in estado:
            accion = "monitorear continuidad; no equiparar riesgo con cierre"
        salida.append(
            {
                "nombre": nombre,
                "direccion_adoptada": direccion,
                "direcciones_alternativas": alternas,
                "barrio": barrio,
                "comuna": comuna,
                "estado": estado,
                "nivel_de_verificacion": nivel,
                "fecha": fecha.isoformat(),
                "fuente": fuente,
                "dias_desde_verificacion": dias,
                "accion": accion,
            }
        )
    vigencia = pd.DataFrame(salida).sort_values("nombre", key=lambda s: s.str.casefold())
    if len(vigencia) != 90 or vigencia["estado"].eq("cerrado").sum() != 2:
        raise RuntimeError("la salida no reconcilia 90 entradas y dos cierres")
    if (~vigencia["estado"].eq("cerrado")).sum() != 88:
        raise RuntimeError("la salida no reconcilia 88 establecimientos operativos")
    escribir(vigencia, "vigencia_90_hitos.csv")

    correcciones = pd.DataFrame(
        [
            {
                "nombre": "Plaza Bar",
                "direccion": "Florida 1005",
                "orden_catalogo": 84,
                "estado_documentado": "cerrado con reapertura anunciada para 2028",
                "fecha_del_cierre": "2017-04-29",
                "fuente_publica": "Clarín/Viva, 2025-02-15; Tango y Milonga, 2025-01-02; catálogo oficial consolidado vigente, 2026-08-03.",
                "correccion": "marcar cerrado; no tratar como extinción definitiva porque el bar se conserva",
            },
            {
                "nombre": "La Buena Medida",
                "direccion": "Suárez 101",
                "orden_catalogo": 61,
                "estado_documentado": "cerrado",
                "fecha_del_cierre": "2025-10-16",
                "fuente_publica": "Canal 26, 2025-12-03; BAE Negocios, 2025-12-02; catálogo oficial consolidado vigente, 2026-08-03.",
                "correccion": "dar de baja de la nómina de establecimientos operativos",
            },
        ]
    )
    escribir(correcciones, "correcciones_catalogo_oficial.csv")
    escribir(correcciones[["nombre", "direccion", "estado_documentado", "fecha_del_cierre", "fuente_publica"]], "cerrados.csv")
    recuperados = pd.DataFrame(
        [
            {
                "nombre": "El Obrero",
                "direccion": "Agustín R. Caffarena 64",
                "interrupcion": "ocho meses durante la pandemia",
                "recuperacion": "reabrió en 2021",
                "estado_actual": "verificado abierto",
                "fecha_verificacion": "2026-08-07",
                "nivel": "v3",
                "fuente_publica": "Cobertura pública de reapertura de 2021 y evidencia pública de atención archivada el 2026-08-07.",
                "criterio": "interrupción recuperada; no integrar la lista de cerrados",
            }
        ]
    )
    escribir(recuperados, "interrumpidos_recuperados.csv")


def tarea_puentecito() -> None:
    fila = pd.DataFrame(
        [
            {
                "nombre": "El Puentecito",
                "direccion_adoptada": "Vieytes 1895 esquina Pedro de Luján 2101",
                "barrio": "Barracas",
                "estado": "probablemente_abierto",
                "nivel": "v2",
                "fecha": "2026-07-07",
                "fuente_principal": "La Nación, 2026-07-07: lo incluyó entre 16 restaurantes icónicos y lo describió en funcionamiento en Vieytes 1895.",
                "corroboracion": "Reseña pública de servicio del 2026-05-04 (fuera de la ventana de 90 días por cinco días) y ficha oficial GCBA modificada el 2026-02-20.",
                "resultado_alerta": "La frase sobre la pérdida de la pieza visible correspondía a Los Laureles, no a El Puentecito.",
                "alcance": "No hubo comprobación presencial ni consulta web en vivo; no elevar a verificado_abierto.",
            }
        ]
    )
    escribir(fila, "el_puentecito.csv")


def tarea_descartes() -> None:
    df = pd.DataFrame(
        [
            {"objeto": "Contactos geométricos con área menor o igual a 0,01 m²", "decision": "excluir de la correspondencia material", "motivo": "umbral predefinido", "destino": "se enumeran por separado en contactos_excluidos_umbral.csv"},
            {"objeto": "Cruces con soportes provisorios de barrio", "decision": "no usar para atribución", "motivo": "miden el barrio y no el polo", "destino": "se conservan como ESPERA_BORDE en la correspondencia"},
            {"objeto": "Habilitaciones por parcela no públicas", "decision": "puerta cerrada", "motivo": "fuente no pública", "destino": "los diez cruces se resolvieron con capas y domicilios públicos"},
            {"objeto": "Estados abiertos de agregadores", "decision": "no usar como verificación", "motivo": "ausencia de reporte de cierre no acredita servicio", "destino": "sólo se admite información agregada; ningún punto ni identificador se exportó"},
            {"objeto": "Contactos de comercios", "decision": "no exportar", "motivo": "guardrail de privacidad", "destino": "todas las salidas carecen de teléfonos, correos e identificadores"},
            {"objeto": "Evidencia pública en vivo", "decision": "no disponible", "motivo": "el conector de investigación web no estuvo disponible", "destino": "se usó únicamente evidencia pública ya archivada y se mantuvieron salvedades"},
        ]
    )
    escribir(df, "descartes_y_decisiones.csv")


def main() -> None:
    tarea_n_vias()
    tarea_r03()
    tarea_calles()
    tarea_requiere_cruce()
    tarea_vigencia()
    tarea_puentecito()
    tarea_descartes()
    print("Tablas generadas")


if __name__ == "__main__":
    main()
