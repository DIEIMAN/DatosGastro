# -*- coding: utf-8 -*-
"""Repara ERR-17/18/19, mide el reparto del sur y documenta Z55.

La corrida no llama APIs ni modifica fuentes F01-F05. Las geometrías P son soportes
analíticos y no se adoptan como límites institucionales.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
EVIDENCIA = BARRIDO / "desde_cowork" / "evidencia_2026"
OUT = BARRIDO / "ronda_15_codex"
CRS_METRICO = "EPSG:5347"
UNIVERSO_ESPERADO = 23_981
CONTEO_ADMITIDOS_VIGENTE = 41
TOLERANCIA_CONTENCION_M2 = 1.0
AREA_DISJUNTA_M2 = 0.01

CORPUS = EVIDENCIA / "fichas_corpus_polos.csv"
SUR = EVIDENCIA / "seis_vias_sur_consolidado.csv"
CRITERIO = EVIDENCIA / "criterio_admision_55.csv"
VIA_E = EVIDENCIA / "via_E_22_referencias.csv"

VIA_IDS = tuple("ABCDEF")
ERR18_IDS = ("R02", "R04", "R05", "R19", "Z37")
NUEVAS_IDS = ("Z50", "Z51", "Z52", "Z53", "Z54")
SOPORTES = {"Z50": "P066", "Z51": "P008", "Z52": "P033", "Z53": "P032", "Z54": "P024"}


def clave(texto: object) -> str:
    normal = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", normal.strip().lower())


def via_abre(valor: object) -> bool:
    return clave(valor).startswith("abre")


def contar_vias(fila: pd.Series | dict[str, object]) -> int:
    return sum(via_abre(fila[f"via_{via}"]) for via in VIA_IDS)


def cargar_universo() -> gpd.GeoDataFrame:
    base = pd.read_csv(BARRIDO / "base" / "local.csv", low_memory=False)
    universo = base[(base["anillo"] == "nucleo") & (base["apto_geometria"] == True)].copy()  # noqa: E712
    if len(universo) != UNIVERSO_ESPERADO:
        raise RuntimeError(f"ERR-10: universo {len(universo)} != {UNIVERSO_ESPERADO}")
    return gpd.GeoDataFrame(
        universo,
        geometry=gpd.points_from_xy(universo["lon"], universo["lat"]),
        crs="EPSG:4326",
    ).to_crs(CRS_METRICO)


def construir_filas_sur(corpus: pd.DataFrame) -> pd.DataFrame:
    sur = pd.read_csv(SUR, encoding="utf-8-sig", dtype=str).fillna("").set_index("zona_id")
    nombres_p = pd.read_csv(
        BARRIDO / "desde_cowork" / "POLOS_NOMBRADOS.csv", encoding="utf-8-sig", dtype=str
    ).fillna("").set_index("polo_id")
    faltan = sorted(set(NUEVAS_IDS) - set(sur.index))
    if faltan:
        raise RuntimeError(f"ERR-17: faltan filas del sur: {faltan}")

    vias_corregidas = {
        "Z50": {"A": "abre", "B": "abre", "C": "no abre", "D": "no abre", "E": "abre", "F": "abre"},
        "Z51": {"A": "abre", "B": "abre", "C": "no abre", "D": "no abre", "E": "abre", "F": "parcial (no abre)"},
        "Z52": {"A": "no abre (evidencia en contra)", "B": "abre", "C": "no abre", "D": "parcial (no abre)", "E": "parcial (no abre)", "F": "abre"},
        "Z53": {"A": "parcial (no abre)", "B": "abre", "C": "no abre", "D": "abre", "E": "parcial (no abre)", "F": "no abre"},
        "Z54": {"A": "no abre", "B": "abre", "C": "abre", "D": "no abre", "E": "parcial (no abre)", "F": "parcial (no abre)"},
    }
    faltantes_ficha = {
        "Z50": "Cerrar el perímetro del corredor 280-1702; P066 cubre sólo una parte. Vínculo con ronda 14 asentado.",
        "Z51": "Resolver el reparto con Z50 y R11; trazar perímetro propio y consolidar el soporte documental de vía E.",
        "Z52": "Trazar el tramo de 340 m documentado por la obra pública y verificar vigencia individual de los hitos.",
        "Z53": "Trazar el entorno de Caminito y Vuelta de Rocha y verificar El Obrero y Genovés.",
        "Z54": "Resolver el reparto con Z40; cargar el Mercado de Pompeya en la capa de hitos con dirección trazable.",
    }

    filas: list[dict[str, object]] = []
    for zona_id in NUEVAS_IDS:
        s = sur.loc[zona_id]
        soporte = SOPORTES[zona_id]
        vias = vias_corregidas[zona_id]
        decisiones = str(s["decisiones_aplicadas"]).strip()
        if zona_id == "Z50":
            decisiones = "Vinculada con P066 y ronda_14/montes_de_oca_seis_vias.csv"
        fila = {
            "polo_id": zona_id,
            "nombre_ficha": s["zona"],
            "origen": f"zona nueva · sur; soporte analítico {soporte}",
            "comunas": s["comuna"],
            "barrios": s["barrios"],
            "estado": "ENTRA",
            "n_vias": sum(via_abre(vias[v]) for v in VIA_IDS),
            "morfologia": s["morfologia"],
            "perimetro_textual": s["perimetro_textual"],
            "anclaje_normativo": s["anclaje_normativo"],
            **{f"via_{v}": vias[v] for v in VIA_IDS},
            "via_E_texto_publicable": s["via_E_texto_publicable"],
            "n_grupos_E": "",
            # Las fichas nuevas declaran que no publican magnitud hasta cerrar perímetro.
            "n_locales": "",
            "ha": "",
            "hitos_conocidos": s["hitos"],
            "alerta_de_vigencia": s["alerta_de_vigencia"],
            "nota_de_delimitacion": (
                f"{s['nota_de_delimitacion']} Soporte analítico: {soporte} "
                f"({nombres_p.loc[soporte, 'nombre_mapa'] or nombres_p.loc[soporte, 'nombre_en_ficha']})."
            ).strip(),
            "decisiones_aplicadas": decisiones,
            "que_falta_para_la_ficha": faltantes_ficha[zona_id],
        }
        if fila["n_vias"] != {"Z50": 4, "Z51": 3, "Z52": 2, "Z53": 2, "Z54": 2}[zona_id]:
            raise RuntimeError(f"{zona_id}: conteo de vías inesperado {fila['n_vias']}")
        filas.append(fila)
    nuevas = pd.DataFrame(filas, columns=corpus.columns)
    return nuevas


def actualizar_corpus() -> pd.DataFrame:
    corpus = pd.read_csv(CORPUS, encoding="utf-8-sig", dtype=str).fillna("")
    if corpus["polo_id"].duplicated().any():
        raise RuntimeError("corpus con IDs duplicados antes de ERR-17")

    corpus = corpus[~corpus["polo_id"].isin(NUEVAS_IDS)].copy()
    corpus.loc[corpus["polo_id"] == "Z37", "via_C"] = (
        "no abre (cerrada en ronda 13: una FIAB no abre la vía C)"
    )
    for polo_id in ERR18_IDS:
        idx = corpus.index[corpus["polo_id"] == polo_id]
        if len(idx) != 1:
            raise RuntimeError(f"ERR-18: {polo_id} aparece {len(idx)} veces")
        corpus.loc[idx, "n_vias"] = str(contar_vias(corpus.loc[idx[0]]))

    nuevas = construir_filas_sur(corpus)
    corpus = pd.concat([corpus, nuevas], ignore_index=True)
    if len(corpus) != 53 or corpus["polo_id"].duplicated().any():
        raise RuntimeError(f"ERR-17: corpus final inválido: {len(corpus)} filas")
    for polo_id in (*ERR18_IDS, *NUEVAS_IDS):
        fila = corpus.loc[corpus["polo_id"] == polo_id].iloc[0]
        if int(fila["n_vias"]) != contar_vias(fila):
            raise RuntimeError(f"n_vias no deriva de columnas en {polo_id}")
    corpus.to_csv(CORPUS, index=False, encoding="utf-8-sig", lineterminator="\r\n")
    return corpus


def reparar_err19() -> None:
    with VIA_E.open("r", encoding="utf-8-sig", newline="") as fh:
        filas = list(csv.reader(fh))
    ancho = len(filas[0])
    salida = [filas[0]]
    for fila in filas[1:]:
        if fila and fila[0] == "R03" and len(fila) > ancho:
            fila = fila[:7] + [", ".join(x.strip() for x in fila[7:-2])] + fila[-2:]
        if len(fila) != ancho:
            raise RuntimeError(f"ERR-19: fila {fila[0] if fila else '?'} tiene {len(fila)} campos")
        salida.append(fila)
    with VIA_E.open("w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh, lineterminator="\r\n").writerows(salida)


def reparar_referencias_err18() -> None:
    criterio = pd.read_csv(CRITERIO, encoding="utf-8-sig", dtype=str).fillna("")
    criterio["motivo"] = criterio["motivo"].str.replace("ERR-16", "ERR-18", regex=False)
    criterio.loc[criterio["polo_id"] == "Z37", "motivo"] = (
        "CINCO vías, no seis: la vía C se cerró por medición en ronda 13. ERR-18 aplicada al corpus."
    )
    criterio.to_csv(CRITERIO, index=False, encoding="utf-8-sig", lineterminator="\r\n")


def medir_par(
    universo: gpd.GeoDataFrame,
    zona_id: str,
    zona_nombre: str,
    zona_geom,
    candidato_id: str,
    candidato_nombre: str,
    candidato_geom,
    fuente_zona: str,
    fuente_candidato: str,
) -> dict[str, object]:
    interseccion = zona_geom.intersection(candidato_geom)
    area_inter = float(interseccion.area)
    perdida = float(zona_geom.difference(candidato_geom).area)
    mascara_zona = universo.geometry.within(zona_geom)
    mascara_candidato = universo.geometry.within(candidato_geom)
    n_zona = int(mascara_zona.sum())
    n_candidato = int(mascara_candidato.sum())
    compartidos = int((mascara_zona & mascara_candidato).sum())
    fuera = n_zona - compartidos

    if perdida <= TOLERANCIA_CONTENCION_M2 and fuera == 0:
        clase_reparto = "CONTENIDA"
        recomendacion = "RECOMENDAR FUSION; requiere firma de Diego"
    elif area_inter <= AREA_DISJUNTA_M2 and compartidos == 0:
        clase_reparto = "DISJUNTA"
        recomendacion = "MANTENER SEPARADA"
    else:
        clase_reparto = "PARCIAL"
        recomendacion = "NO FUSIONAR AUTOMATICAMENTE; decide Diego con el reparto"

    return {
        "zona_id": zona_id,
        "zona": zona_nombre,
        "candidato_id": candidato_id,
        "candidato": candidato_nombre,
        "soporte_geometrico_zona": fuente_zona,
        "soporte_geometrico_candidato": fuente_candidato,
        "area_zona_m2": round(float(zona_geom.area), 2),
        "area_candidato_m2": round(float(candidato_geom.area), 2),
        "area_interseccion_m2": round(area_inter, 2),
        "superficie_zona_perdida_m2": round(perdida, 2),
        "pct_superficie_zona_en_candidato": round(100 * area_inter / zona_geom.area, 4),
        "pct_superficie_candidato_en_zona": round(100 * area_inter / candidato_geom.area, 4),
        "n_locales_zona": n_zona,
        "n_locales_candidato": n_candidato,
        "n_locales_compartidos": compartidos,
        "n_locales_zona_fuera_candidato": fuera,
        "pct_locales_zona_en_candidato": round(100 * compartidos / n_zona, 4) if n_zona else 0.0,
        "pct_locales_candidato_en_zona": round(100 * compartidos / n_candidato, 4) if n_candidato else 0.0,
        "universo": "anillo == nucleo AND apto_geometria == True (n=23981)",
        "verificacion_contencion": "superficie perdida; no se uso covers()",
        "clase_reparto": clase_reparto,
        "recomendacion": recomendacion,
    }


def medir_reparto() -> tuple[pd.DataFrame, int]:
    universo = cargar_universo()
    polos = gpd.read_file(BARRIDO / "borrador_polos" / "polos_publicables.geojson").to_crs(CRS_METRICO)
    zonas = gpd.read_file(BARRIDO / "geometria_r7" / "zonas_r7.geojson").to_crs(CRS_METRICO)
    p = polos.set_index("polo_id")
    z = zonas.set_index("zona_id")
    requeridos_p = {"P008", "P066", "P024"}
    requeridos_z = {"R11", "Z40"}
    if not requeridos_p.issubset(p.index) or not requeridos_z.issubset(z.index):
        raise RuntimeError("faltan geometrías requeridas para el reparto")

    fuente_p = "outputs/BARRIDO_CIUDAD_2026-08/borrador_polos/polos_publicables.geojson"
    fuente_z = "outputs/BARRIDO_CIUDAD_2026-08/geometria_r7/zonas_r7.geojson"
    filas = [
        medir_par(universo, "Z51", "Barracas · Iriarte, California y Vieytes", p.loc["P008"].geometry,
                  "Z50", "Barracas · Av. Montes de Oca", p.loc["P066"].geometry,
                  f"{fuente_p}#P008", f"{fuente_p}#P066"),
        medir_par(universo, "Z51", "Barracas · Iriarte, California y Vieytes", p.loc["P008"].geometry,
                  "R11", "Boulevard Caseros", z.loc["R11"].geometry,
                  f"{fuente_p}#P008", f"{fuente_z}#R11"),
        medir_par(universo, "Z54", "Nueva Pompeya · eje Av. Sáenz", p.loc["P024"].geometry,
                  "Z40", "Nueva Pompeya y Parque Patricios", z.loc["Z40"].geometry,
                  f"{fuente_p}#P024", f"{fuente_z}#Z40"),
    ]
    reparto = pd.DataFrame(filas)
    zonas_fusion = set(reparto.loc[reparto["clase_reparto"] == "CONTENIDA", "zona_id"])
    conteo_si_firma = CONTEO_ADMITIDOS_VIGENTE - len(zonas_fusion)
    reparto["conteo_polos_admitidos_vigente"] = CONTEO_ADMITIDOS_VIGENTE
    reparto["conteo_si_Diego_firma_recomendaciones"] = conteo_si_firma
    reparto.to_csv(OUT / "reparto_sur.csv", index=False, encoding="utf-8-sig", lineterminator="\r\n")
    return reparto, conteo_si_firma


def documentar_z55() -> pd.DataFrame:
    ferias = pd.read_csv(ROOT / "data" / "raw" / "f03_ferias.csv", dtype=str).fillna("")
    mercados = pd.read_csv(ROOT / "data" / "raw" / "f03_mercados.csv", dtype=str).fillna("")
    fiab = json.loads((ROOT / "data" / "raw" / "f03_fiab.geojson").read_text(encoding="utf-8"))["features"]

    def contiene(tabla: pd.DataFrame, patron: str) -> int:
        return int(tabla.astype(str).apply(lambda c: c.str.contains(patron, case=False, regex=True)).any(axis=1).sum())

    fiab_soldati = [f for f in fiab if clave(f["properties"].get("barrio")) == "villa soldati"]
    fiab_mariano = [f for f in fiab if "mariano acosta" in clave(f["properties"])]
    filas = [
        {
            "fuente_publica": "F03_FERIAS",
            "archivo_verificado": "data/raw/f03_ferias.csv",
            "url_publica": "https://data.buenosaires.gob.ar/dataset/ferias-mercados/resource/juqdkmgo-1121-resource/download",
            "fecha_descarga": "2026-06-12",
            "universo_fuente": f"{len(ferias)} ferias especializadas/no FIAB",
            "coincidencias_Villa_Soldati": contiene(ferias, r"Villa Soldati"),
            "coincidencias_Mariano_Acosta_Janer": contiene(ferias, r"Mariano Acosta|Ana Mar[ií]a Janer"),
            "resultado": "No se encontró la feria alegada en el recurso público almacenado.",
        },
        {
            "fuente_publica": "F03_FIAB_GEOJSON",
            "archivo_verificado": "data/raw/f03_fiab.geojson",
            "url_publica": "https://data.buenosaires.gob.ar/dataset/ferias-mercados/resource/89d4e504-2fa8-4703-9c05-2471fa47cdfa/download",
            "fecha_descarga": "2026-06-12",
            "universo_fuente": f"{len(fiab)} ubicaciones FIAB",
            "coincidencias_Villa_Soldati": len(fiab_soldati),
            "coincidencias_Mariano_Acosta_Janer": len(fiab_mariano),
            "resultado": "Dos FIAB en Villa Soldati (Lacarra/Roca y Predio Villa Olímpica); ninguna sobre Mariano Acosta.",
        },
        {
            "fuente_publica": "F03_MERCADOS",
            "archivo_verificado": "data/raw/f03_mercados.csv",
            "url_publica": "https://data.buenosaires.gob.ar/dataset/ferias-mercados/resource/juqdkmgo-1126-resource/download",
            "fecha_descarga": "2026-06-12",
            "universo_fuente": f"{len(mercados)} mercados",
            "coincidencias_Villa_Soldati": contiene(mercados, r"Villa Soldati"),
            "coincidencias_Mariano_Acosta_Janer": contiene(mercados, r"Mariano Acosta|Ana Mar[ií]a Janer"),
            "resultado": "No se encontró la feria alegada en el recurso público almacenado.",
        },
    ]
    tabla = pd.DataFrame(filas)
    tabla.to_csv(OUT / "z55_fuentes_publicas.csv", index=False, encoding="utf-8-sig", lineterminator="\r\n")
    return tabla


def validar_antes_de_documentar(corpus: pd.DataFrame, reparto: pd.DataFrame, conteo_si_firma: int) -> None:
    criterio = pd.read_csv(CRITERIO, encoding="utf-8-sig", dtype=str).fillna("")
    admitidos = set(criterio.loc[criterio["categoria_por_criterio"] == "polo admitido", "polo_id"])
    if len(admitidos) != CONTEO_ADMITIDOS_VIGENTE:
        raise RuntimeError(f"el criterio ya no contiene 41 admitidos: {len(admitidos)}")
    if not set(NUEVAS_IDS).issubset(corpus["polo_id"]):
        raise RuntimeError("ERR-17: el corpus no contiene las cinco filas")
    if conteo_si_firma != CONTEO_ADMITIDOS_VIGENTE - reparto.loc[
        reparto["clase_reparto"] == "CONTENIDA", "zona_id"
    ].nunique():
        raise RuntimeError("el impacto del reparto no coincide con las recomendaciones")
    # El documento no se escribe antes de que este gate cierre.


def escribir_ronda(corpus: pd.DataFrame, reparto: pd.DataFrame, conteo_si_firma: int) -> None:
    def fmt(valor: object, dec: int = 2) -> str:
        return f"{float(valor):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")

    lineas = []
    for r in reparto.itertuples():
        lineas.append(
            f"| {r.zona_id} | {r.candidato_id} | {fmt(r.area_interseccion_m2)} | "
            f"{fmt(r.superficie_zona_perdida_m2)} | {fmt(r.pct_superficie_zona_en_candidato, 4)} % | "
            f"{r.n_locales_compartidos}/{r.n_locales_zona} ({fmt(r.pct_locales_zona_en_candidato, 4)} %) | "
            f"{r.n_locales_compartidos}/{r.n_locales_candidato} ({fmt(r.pct_locales_candidato_en_zona, 4)} %) | "
            f"{r.clase_reparto} | {r.recomendacion} |"
        )
    fusiones = sorted(set(reparto.loc[reparto["clase_reparto"] == "CONTENIDA", "zona_id"]))
    z51 = reparto[reparto["zona_id"] == "Z51"]
    rec_z51 = "mantener separada" if (z51["clase_reparto"] == "DISJUNTA").all() else "no fusionar automáticamente"
    rec_z54 = reparto.loc[reparto["zona_id"] == "Z54", "recomendacion"].iloc[0].lower()

    md = f"""# Ronda 15 · Codex

Estado: **EXPERIMENTAL / NO OFICIAL**. Cero requests a APIs. La fusión territorial queda pendiente de firma de Diego.

## 1. ERR-17 · corpus del sur

Se incorporaron **Z50–Z54** a `fichas_corpus_polos.csv`. El corpus pasó de 48 a **{len(corpus)} filas**. Cada alta conserva las seis columnas de vía, los hitos y el perímetro textual de `seis_vias_sur_consolidado.csv`; Z51–Z54 se cotejaron además con `FICHAS_SUR_NUEVAS.md`.

Z50 quedó vinculada explícitamente con **P066** y `ronda_14/montes_de_oca_seis_vias.csv`. No se la duplicó como “polo 42”. Las cifras de superficie y registros de las cinco fichas siguen sin publicarse porque sus límites institucionales no están adoptados.

## 2. Reparto del sur

Universo: `anillo == 'nucleo' AND apto_geometria == True`, **23.981 registros** de `base/local.csv`. Superficies en EPSG:5347. La contención se verificó por **superficie perdida**, no con `covers()`.

| zona | candidato | intersección m² | superficie de la zona perdida m² | superficie de la zona dentro | registros compartidos / zona | registros compartidos / candidato | clase | recomendación |
|---|---|---:|---:|---:|---:|---:|---|---|
{chr(10).join(lineas)}

Recomendación técnica: **Z51 {rec_z51}** frente a Z50 y R11; **Z54: {rec_z54}**. El conteo vigente continúa en **41 polos admitidos**. Si Diego firma todas las fusiones recomendadas ({', '.join(fusiones) if fusiones else 'ninguna'}), el contrafáctico pasa a **{conteo_si_firma}**. La corrida no toma esa decisión.

## 3. ERR-18 y ERR-19

`n_vias` se recalculó desde `via_A`…`via_F`: **R02=4, R04=4, R05=5, R19=4 y Z37=5**. En Z37 la vía C quedó escrita como cerrada por ronda 13. Ninguna fila cambia de categoría.

La fila R03 de `via_E_22_referencias.csv` quedó en **10 campos**, como el encabezado. `via_E_advertencia` conserva completo el texto con comas; `via_E_rutas_n=6` y `fecha_relevamiento=2026-08-07` vuelven a sus columnas.

## 4. Z55 · fuente pública

Se verificaron los tres recursos oficiales F03 conservados en el repositorio, descargados el **12/06/2026** desde BA Data: 30 ferias, 184 ubicaciones FIAB y 6 mercados. El GeoJSON registra dos FIAB en Villa Soldati —Lacarra/Roca y Predio Villa Olímpica— y ninguna sobre Mariano Acosta. Los recursos de ferias y mercados tampoco contienen “Mariano Acosta” ni “Ana María Janer”.

La afirmación de una feria de 840 m no trae URL, norma, permiso ni identificador de fuente en `seis_vias_sur_consolidado.csv`. Por eso queda como **puerta documental cerrada / no verificable con la fuente pública disponible** y **no abre la vía C**. Esto no prueba que la feria no exista; prueba que el instrumento no tiene respaldo público trazable para computarla. El corte del padrón (12/06/2026) impide usar la ausencia como prueba territorial.

Hay una segunda consecuencia lógica: aun si una fuente futura abriera C, Z55 pasaría de 0 a **1 vía**, por debajo del umbral común de **2 vías**. Con el criterio vigente, esta contradicción por sí sola **no puede crear un polo en la Comuna 8**.

## 5. Gates

- Universo ERR-10: **23.981**, reproducido.
- Corpus: **53 IDs únicos**; Z50–Z54 presentes.
- Criterio: **41 admitidos**; no se promovió ninguna fusión.
- Reparto: ambos denominadores de superficie y registros presentes; superficie perdida explícita.
- ERR-19: todas las filas tienen 10 campos.
- Fuentes originales F01–F05: sólo lectura; no se modificaron.
"""
    (OUT / "RONDA_15_CODEX.md").write_text(md, encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    corpus = actualizar_corpus()
    reparar_err19()
    reparar_referencias_err18()
    reparto, conteo_si_firma = medir_reparto()
    documentar_z55()
    validar_antes_de_documentar(corpus, reparto, conteo_si_firma)
    escribir_ronda(corpus, reparto, conteo_si_firma)
    print((OUT / "RONDA_15_CODEX.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
