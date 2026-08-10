# -*- coding: utf-8 -*-
"""Genera `cifras_canonicas.json`: cada cifra del atlas, con su valor, su fecha y su archivo.

EL PROBLEMA QUE RESUELVE
-------------------------
Hoy las cifras están tipeadas a mano en el texto de cada documento. Cuando una medición cambia,
el número cambia en el archivo que lo produjo y **queda viejo en los seis documentos que lo
citan**, sin que nada avise. Ya pasó: la superficie total de las concentraciones se midió el 7 de
agosto en 3.128,5 ha, la capa se rehizo después, y hoy la misma capa da 3.143,53 ha mientras seis
documentos siguen publicando la vieja.

Este archivo declara **una sola fuente por cifra**. Cada entrada dice cuánto vale, de qué archivo
sale, cómo se calcula y con qué fecha. `verificar_cifras.py` recorre los documentos y avisa cuál
número del texto no coincide.

LA REGLA, PARA QUE ESTO NO SE CONVIERTA EN OTRO ARCHIVO QUE SE DESACTUALIZA
---------------------------------------------------------------------------
**Toda cifra que se pueda medir, se mide acá y no se escribe a mano.** El campo `origen` dice
`medido` o `declarado`. Las `declarado` son las que no salen de ningún archivo del repositorio
—una decisión editorial, un dato de una fuente externa— y llevan escrito de dónde vienen.

Cero requests. Se ejecuta con .venv/Scripts/python.exe.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nombres_de_barrio import clave as clave_barrio  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
SALIDA = Path(__file__).resolve().parent
CRS_METRICO = "EPSG:5347"
HOY = date.today().isoformat()

REL = lambda p: str(Path(p).resolve().relative_to(ROOT)).replace("\\", "/")  # noqa: E731


def limpia(g):
    return g if g.is_valid else g.buffer(0)


def cifra(valor, unidad, archivo, como, origen="medido", patrones=(), nota=""):
    return dict(valor=valor, unidad=unidad, fecha_de_calculo=HOY,
                archivo_del_que_sale=archivo, como_se_calcula=como, origen=origen,
                patrones_en_el_texto=list(patrones), nota=nota)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 98)
    print("CIFRAS CANÓNICAS · una sola fuente por número")
    print("=" * 98 + "\n")

    sys.path.insert(0, str(ROOT / "scripts" / "barrido_ciudad"))
    from polos_soporte import puntos_base  # noqa: E402

    puntos = puntos_base()
    base = pd.read_csv(BASE / "base" / "local.csv")
    criterio = pd.read_csv(BASE / "desde_cowork" / "evidencia_2026" / "criterio_admision_55.csv")
    admitidos = criterio[criterio.categoria_por_criterio == "polo admitido"]
    publicables = gpd.read_file(BASE / "borrador_polos" / "polos_publicables.geojson").to_crs(
        CRS_METRICO)
    pertenencia = pd.read_csv(BASE / "borrador_polos" / "pertenencia_local_polo_v3.csv")
    soportes = gpd.read_file(
        BASE / "ronda_16_codex" / "geometria" / "soportes_41.geojson").to_crs(
        CRS_METRICO).set_index("polo_id")
    enclaves = pd.read_csv(
        BASE / "desde_cowork" / "evidencia_2026" / "enclaves_comunitarios_delimitados.csv")
    notables = pd.read_csv(
        BASE / "desde_cowork" / "evidencia_2026" / "catalogo_90_estado_final.csv")
    magnitudes = pd.read_csv(
        BASE / "desde_cowork" / "evidencia_2026" / "magnitudes_sin_perimetro.csv")
    barrios = gpd.read_file(BASE / "insumos" / "caba_barrios.geojson").to_crs(CRS_METRICO)
    cierre = pd.read_csv(SALIDA / "perimetros_cierre.csv")
    total = json.loads((SALIDA / "total_recalculado.json").read_text(encoding="utf-8"))

    # --- las que se miden ------------------------------------------------------------------
    u124 = limpia(unary_union([limpia(g) for g in publicables.geometry]))
    ha124 = u124.area / 1e4
    ha_ciudad = limpia(barrios.geometry.union_all()).area / 1e4
    en_polos = int(pertenencia.polo_final.notna().sum())
    n_relevados = len(puntos)

    # Comunas con polo: la columna trae texto como «1 y 3» o «7 (borde en 10 y 11)», así que se
    # cuenta la comuna PRINCIPAL de cada polo -el primer número-, que es la que ordena la
    # sección VII. Contar todos los números daría 19 y eso no es «comunas con polo».
    principales = sorted({int(re.search(r"\d+", str(c)).group())
                          for c in admitidos.comuna if re.search(r"\d+", str(c))})

    # Los que siguen sin borde propio: su geometría es todavía el polígono de un barrio.
    ya_trazados = set(cierre[cierre.cerrado_si_no.isin(
        ["si", "si_con_exclusion_declarada", "parcial", "dos_opciones_medidas"])].zona_id)
    provisorios_antes = [pid for pid in soportes.index if not bool(soportes.soporte_es_real[pid])]
    sin_borde = [pid for pid in provisorios_antes if pid not in ya_trazados]
    sin_borde_ha = magnitudes[magnitudes.polo_id.isin(sin_borde)].drop_duplicates(
        subset=["contenedor"])
    sin_borde_antes = magnitudes.drop_duplicates(subset=["contenedor"])

    print(f"universo: {n_relevados:,} locales · polos admitidos: {len(admitidos)} · "
          f"concentraciones: {len(publicables)}")
    print(f"comunas con polo: {len(principales)} -> {principales}")
    print(f"siguen sin borde propio: {sin_borde}")

    cifras = {
        "locales_relevados": cifra(
            n_relevados, "locales", REL(BASE / "base" / "local.csv"),
            "filas de local.csv con anillo == 'nucleo' y apto_geometria == True; el universo "
            "con el que se construyeron las concentraciones",
            patrones=[r"(?P<valor>[\d.]+) locales gastronómicos relevados",
                      r"(?P<valor>[\d.]+) locales\*\* relevados en toda la Ciudad",
                      r"\*\*(?P<valor>[\d.]+)\*\* \| locales gastronómicos relevados",
                      r"(?P<valor>[\d.]+) registros de los [\d.]+"],
            nota=f"sobre {len(base):,} filas totales de la base"),

        "polos": cifra(
            len(admitidos), "polos", REL(BASE / "desde_cowork" / "evidencia_2026"
                                         / "criterio_admision_55.csv"),
            "filas con categoria_por_criterio == 'polo admitido'",
            patrones=[r"\*\*(?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) polos admitidos",
                      r"(?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) polos admitidos en (?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?) comunas",
                      r"(?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) polos gastronómicos admitidos"]),

        "fichas": cifra(
            len(soportes), "fichas", REL(BASE / "ronda_16_codex" / "geometria"
                                         / "soportes_41.geojson"),
            "una ficha por polo admitido; coincide con la cantidad de soportes geométricos",
            patrones=[r"(?P<valor>\d+) fichas en prosa",
                      r"(?P<valor>\d+) fichas agrupadas",
                      r"[Dd]os de las (?P<valor>\d+) fichas"]),

        "objetos_disjuntos": cifra(
            total["objetos_disjuntos"], "objetos",
            REL(SALIDA / "total_recalculado.json"),
            "fichas cuya geometría NO queda contenida en la de otra, medido por superficie "
            "perdida contra la unión de todas las demás",
            patrones=[r"objetos territoriales disjuntos[^.]{0,40}?son \*\*(?P<valor>\d+)\*\*"],
            nota="el documento dice 39 porque cuenta a Baek-ku como subzona de Parque "
                 "Avellaneda; medido, Baek-ku queda 100 % fuera de los otros cuarenta y el "
                 "más cercano está a 1.274 m. La única ficha realmente contenida en otra es "
                 "el eje Sáenz dentro de Nueva Pompeya"),

        "zonas_evaluadas": cifra(
            len(criterio), "zonas", REL(BASE / "desde_cowork" / "evidencia_2026"
                                        / "criterio_admision_55.csv"),
            "filas del archivo de criterio: todo lo que se midió, entrara o no",
            patrones=[r"[Ss]e evaluaron \*\*(?P<valor>\d+) zonas",
                      r"sobre las (?P<valor>\d+) unidades evaluadas"]),

        "agrupamientos_detectados": cifra(
            len(publicables), "concentraciones",
            REL(BASE / "borrador_polos" / "polos_publicables.geojson"),
            "polígonos de la capa de concentraciones detectadas por densidad",
            patrones=[r"(?P<valor>[\d.]+) concentraciones detectadas",
                      r"[Ll]as (?P<valor>[\d.]+) concentraciones de las que salieron",
                      r"[Ll]as (?P<valor>[\d.]+) son disjuntas",
                      r"hay (?P<valor>[\d.]+) concentraciones y \d+ polos admitidos"]),

        "locales_en_polos": cifra(
            en_polos, "locales", REL(BASE / "borrador_polos" / "pertenencia_local_polo_v3.csv"),
            "locales con polo_final asignado por el agrupamiento. NO es un conteo de punto "
            "dentro de polígono",
            patrones=[r"su unión da \*\*(?P<valor>[\d.]+) locales en",
                      r"suman exactamente \*\*(?P<valor>[\d.]+) locales en",
                      r"calculada sobre la unión: \*\*(?P<valor>[\d.]+) locales en",
                      r"\*\*(?P<valor>[\d.]+)\*\* \| locales en los polos",
                      r"de su superficie\*\* — (?P<valor>[\d.]+)\s*\n?locales en",
                      r"\| \*\*(?P<valor>[\d.]+) locales en [\d.,]+ hectáreas\*\* \| el \*\*\d+ ?%"],
            nota="contando por punto dentro de la unión de los polígonos da 12.520, o sea 168 "
                 "menos. La diferencia es real y no es un error: un local puede pertenecer al "
                 "agrupamiento y caer fuera de la envolvente simplificada. Las dos cifras "
                 "miden cosas distintas y el texto tiene que decir cuál usa"),

        "locales_en_polos_por_geometria": cifra(
            int(puntos.within(u124).sum()), "locales",
            REL(BASE / "borrador_polos" / "polos_publicables.geojson"),
            "locales del universo que caen dentro de la unión de las concentraciones",
            patrones=[r"(?P<valor>[\d.]+) locales por geometría",
                      r"contando por punto[^.]{0,60}?da (?P<valor>[\d.]+)"]),

        "ha_en_polos": cifra(
            round(ha124, 2), "hectáreas",
            REL(BASE / "borrador_polos" / "polos_publicables.geojson"),
            "área de la unión de las concentraciones, medida en EPSG:5347. Las 124 son "
            "disjuntas, así que la unión y la suma coinciden",
            patrones=[r"su unión da \*\*[\d.]+ locales en (?P<valor>[\d.,]+) hect",
                      r"suman exactamente \*\*[\d.]+ locales en\s*\n?(?P<valor>[\d.,]+) hect",
                      r"calculada sobre la unión: \*\*[\d.]+ locales en (?P<valor>[\d.,]+) hect",
                      r"de su superficie\*\* — [\d.]+\s*\n?locales en (?P<valor>[\d.,]+) hect",
                      r"\| \*\*[\d.]+ locales en (?P<valor>[\d.,]+) hectáreas\*\* \| el \*\*\d+ ?%",
                      r"área de la \*\*unión\*\* \| \*\*(?P<valor>[\d.,]+) ha\*\*",
                      r"suma de las áreas individuales \| \*\*(?P<valor>[\d.,]+) ha\*\*"],
            nota="el documento publica 3.128,5 ha, medidas el 07/08/2026 sobre una versión "
                 "anterior de la capa. La capa de hoy da 3.143,53: son 15,03 ha más"),

        "pct_locales_en_polos": cifra(
            round(en_polos / n_relevados * 100), "por ciento", "derivada",
            "locales_en_polos / locales_relevados, redondeado al entero",
            patrones=[r"[Ee]l \*\*(?P<valor>\d+) ?%\*\* de la gastronomía relevada"]),

        "pct_superficie": cifra(
            round(ha124 / ha_ciudad * 100), "por ciento", "derivada",
            "ha_en_polos / superficie de la Ciudad según la capa oficial de 48 barrios "
            f"({ha_ciudad:,.0f} ha), redondeado al entero",
            patrones=[r"en el \*\*(?P<valor>\d+) ?%\*\* de su superficie",
                      r"en el \*\*(?P<valor>\d+) ?%\*\* de la superficie de la Ciudad"]),

        "bares_notables": cifra(
            len(notables), "bares",
            REL(BASE / "desde_cowork" / "evidencia_2026" / "catalogo_90_estado_final.csv"),
            "entradas del catálogo consolidado firmado el 03/08/2026",
            patrones=[r"\d+ de (?P<valor>\d+) bares notables",
                      r"(?P<valor>\d+) de \d+ bares notables"]),

        "bares_notables_abiertos": cifra(
            int((notables.estado.str.upper() != "CERRADO").sum()), "bares",
            REL(BASE / "desde_cowork" / "evidencia_2026" / "catalogo_90_estado_final.csv"),
            "entradas cuyo estado no es CERRADO: incluye 1 en riesgo y 1 abierto en quiebra",
            patrones=[r"(?P<valor>\d+) operando"],
            nota="el desglose es " + " · ".join(
                f"{k} {v}" for k, v in notables.estado.value_counts().items())),

        "enclaves_comunitarios": cifra(
            len(enclaves), "enclaves",
            REL(BASE / "desde_cowork" / "evidencia_2026"
                / "enclaves_comunitarios_delimitados.csv"),
            "enclaves con delimitación escrita en calles y alturas",
            patrones=[r"(?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) enclaves comunitarios delimitados",
                      r"\*\*(?P<valor>\d+)\*\* \| enclaves comunitarios",
                      r"los (?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) enclaves delimitados son",
                      r"territorio: (?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) enclaves delimitados",
                      r"delimita \*\*(?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) enclaves comunitarios"]),

        "polos_sin_borde": cifra(
            len(sin_borde), "polos", REL(SALIDA / "perimetros_cierre.csv"),
            "polos cuya geometría sigue siendo el polígono administrativo de un barrio, "
            "después del cierre geométrico",
            patrones=[r"(?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) de los cuarenta y un polos",
                      r"(?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) de los 41 polos[^.]{0,30}?perímetro",
                      r"[Ll]os (?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) sin perímetro trazado"],
            nota=f"eran 18 antes de esta corrida; siguen sin borde propio {', '.join(sin_borde)}"),

        "locales_en_barrios_sin_borde": cifra(
            int(sin_borde_ha.locales_en_concentraciones.sum()), "locales",
            REL(BASE / "desde_cowork" / "evidencia_2026" / "magnitudes_sin_perimetro.csv"),
            "locales en concentraciones dentro de los barrios que contienen a los polos que "
            "siguen sin borde, deduplicando los barrios que contienen dos polos",
            patrones=[r"el conjunto son \*\*(?P<valor>[\d.]+) locales en",
                      r"— (?P<valor>[\d.]+)\s*\n?locales en [\d.,]+ hectáreas para el conjunto"],
            nota=f"con los 18 de antes eran "
                 f"{int(sin_borde_antes.locales_en_concentraciones.sum()):,} locales"),

        "ha_en_barrios_sin_borde": cifra(
            round(float(sin_borde_ha.ha_en_concentraciones.sum()), 1), "hectáreas",
            REL(BASE / "desde_cowork" / "evidencia_2026" / "magnitudes_sin_perimetro.csv"),
            "superficie concentrada en esos mismos barrios, deduplicada",
            patrones=[r"el conjunto son \*\*[\d.]+ locales en (?P<valor>[\d.,]+) hect",
                      r"locales en (?P<valor>[\d.,]+) hectáreas para el conjunto"],
            nota=f"con los 18 de antes eran "
                 f"{float(sin_borde_antes.ha_en_concentraciones.sum()):,.1f} ha; el documento "
                 f"publica 893,5 y la suma da 893,4 -diferencia de redondeo-"),

        "comunas_con_polo": cifra(
            len(principales), "comunas",
            REL(BASE / "desde_cowork" / "evidencia_2026" / "criterio_admision_55.csv"),
            "comunas distintas entre las comunas principales de los polos admitidos",
            patrones=[r"admitidos en (?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) comunas",
                      r"(?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) comunas tienen al menos un polo",
                      r"en (?P<valor>(?:\d+|[\wáéíóúñ]+(?: y [\wáéíóúñ]+)?)) de las quince comunas"],
            nota=f"son las comunas {principales}; la 8 sigue sin ninguno"),
    }

    salida = dict(
        generado=HOY,
        que_es=("La única fuente de cada cifra del atlas. Si un documento dice otra cosa, manda "
                "esto. Se regenera con cifras_canonicas.py y se controla con "
                "verificar_cifras.py."),
        universo=("anillo == 'nucleo' AND apto_geometria == True: "
                  f"{n_relevados:,} de {len(base):,} registros de la base"),
        crs_de_medicion=CRS_METRICO,
        cifras=cifras,
    )
    destino = SALIDA / "cifras_canonicas.json"
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'cifra':<36}{'valor':>14}  {'origen':<10} archivo")
    for nombre, c in cifras.items():
        print(f"{nombre:<36}{str(c['valor']):>14}  {c['origen']:<10} {c['archivo_del_que_sale']}")
    print(f"\nEscrito: {destino.name} ({len(cifras)} cifras)")


if __name__ == "__main__":
    main()
