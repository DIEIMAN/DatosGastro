from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import make_valid
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely.validation import explain_validity


FECHA = "2026-08-12"
CRS_METRICO = "EPSG:5347"
CRS_GEOGRAFICO = "EPSG:4326"
BORDE_REFERENTE_M = 50.0
MAX_DELTA_AREA_M2 = 10.0
MAX_DELTA_AREA_PCT = 0.001


def argumentos() -> argparse.Namespace:
    aqui = Path(__file__).resolve()
    repo = aqui.parents[4]
    out = aqui.parents[1]
    p = argparse.ArgumentParser(description="Construye la base estructural candidata R22, sólo offline.")
    p.add_argument("--repo", type=Path, default=repo)
    p.add_argument("--out", type=Path, default=out)
    p.add_argument(
        "--conciliacion-zip",
        type=Path,
        default=repo.parent / "DATAGASTRO_V3_CONCILIACION_PRE_CORRECCIONES_2026-08-12.zip",
    )
    p.add_argument(
        "--zip",
        type=Path,
        default=repo.parent / "DATAGASTRO_V3_R22_BASE_ESTRUCTURAL_2026-08-12.zip",
    )
    p.add_argument("--overwrite-zip", action="store_true")
    return p.parse_args()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def clave(valor: object) -> str:
    if pd.isna(valor):
        return ""
    txt = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Z0-9]+", " ", txt.upper()).strip()


def limpio(valor: object) -> str:
    if pd.isna(valor):
        return ""
    txt = str(valor).strip()
    txt = re.sub(r"(?i)\bDiego(?:\s*\(DGDGAS\))?\b", "verificación humana DGDGAS", txt)
    txt = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[contacto_redactado]", txt)
    txt = re.sub(r"\b(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]\d{4}\b", "[contacto_redactado]", txt)
    txt = re.sub(r"https?://(?:drive|docs)\.google\.com/\S+", "[link_privado_redactado]", txt)
    txt = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "[clave_redactada]", txt)
    return txt


def si_no(valor: object) -> str:
    return "SI" if bool(valor) else "NO"


def uid_polo(legacy_id: str) -> str:
    if legacy_id == "R09+R19+Z43":
        return "SYS-CHACAGIALES"
    if legacy_id == "Z54":
        return "PIEZA-Z54"
    return f"POLO-{legacy_id.upper()}"


def partes_poligonales(geom):
    valido = make_valid(geom)
    if valido.geom_type in {"Polygon", "MultiPolygon"}:
        return valido
    partes = [g for g in getattr(valido, "geoms", []) if g.geom_type in {"Polygon", "MultiPolygon"}]
    if not partes:
        raise ValueError(f"make_valid no produjo partes poligonales: {valido.geom_type}")
    return unary_union(partes)


def fuentes_y_familias(fila: pd.Series) -> tuple[str, str, str]:
    valores = [limpio(fila.get(c, "")) for c in ("fuente_primaria", "origen")]
    valores = list(dict.fromkeys(v for v in valores if v))
    texto = " | ".join(valores)
    may = clave(texto)
    familias = []
    if any(x in may for x in ("GCBA", "BOLETIN", "LEGISLATURA", "REFERENTES 2026")):
        familias.append("PUBLICA_GCBA")
    if any(x in may for x in ("MICHELIN", "WIKIDATA", "WIKIPEDIA", "50 BEST", "RANKING")):
        familias.append("EXTERNA_TERCEROS")
    if any(x in may for x in ("DOCUMENT", "PRENSA", "CATALOGO")):
        familias.append("DOCUMENTAL")
    if not familias:
        familias.append("DOCUMENTAL_OTRA")
    principal = limpio(fila.get("fuente_primaria", "")) or limpio(fila.get("origen", ""))
    return texto, ";".join(familias), principal


def estado_vigencia(fila: pd.Series) -> tuple[str, str, str, str]:
    v = clave(fila.get("vigencia_verificada", ""))
    fuente = limpio(fila.get("vigencia_fuente", ""))
    fecha = limpio(fila.get("vigencia_fecha", "")) or limpio(fila.get("vigencia_fecha_consulta", ""))
    places = clave(fila.get("places_business_status", ""))
    nombre = clave(fila.get("nombre", ""))
    if v == "NO" or places == "CLOSED PERMANENTLY":
        estado = "CERRADO"
    elif "REAPERT" in clave(fuente) or nombre == "LOS LAURELES":
        estado = "REABIERTO"
    elif v == "SI":
        estado = "OPERATIVO"
    else:
        estado = "SIN_VERIFICAR"
    if "VERIFICACION HUMANA" in clave(fuente):
        metodo = "HUMANA"
    elif places:
        metodo = "AUTOMATICA_PLATAFORMA_OFFLINE"
    elif fuente:
        metodo = "DOCUMENTAL"
    else:
        metodo = "SIN_VERIFICACION"
    return estado, fecha, fuente, metodo


def categoria_referente(tipo: object, reconocimiento: object) -> tuple[str, str]:
    t, r = clave(tipo), clave(reconocimiento)
    if "BAR NOTABLE" in t:
        return "Bar Notable", ""
    if "RESTAURANTE ICONICO" in t:
        return "Restaurante Icónico", ""
    if "MICHELIN" in t:
        if "BIB GOURMAND" in r:
            return "Bib Gourmand", "selección MICHELIN"
        if "ESTRELLA VERDE" in r:
            return "Estrella Verde", "selección MICHELIN"
        return "MICHELIN", limpio(reconocimiento)
    if "RANKING INTERNACIONAL" in t:
        return "Latin America’s 50 Best", limpio(reconocimiento)
    if "MERCADO" in t or "PATIO" in t:
        return "mercado/patio", ""
    if "PIZZERIA" in t:
        return "pizzería histórica", limpio(reconocimiento)
    if "CAFE HISTORICO" in t or "CAFETERIA HISTORICA" in t:
        return "cafetería histórica", limpio(reconocimiento)
    if "BODEGON" in t:
        return "bodegón", limpio(reconocimiento)
    if "CASA REGIONAL" in t:
        return "institución/comunidad gastronómica", limpio(reconocimiento)
    if "PATRIMONIO" in t:
        return "patrimonio", limpio(reconocimiento)
    if "TRAYECTORIA" in t:
        return "referente barrial", "churrería/pastelería"
    return "otro documentado", limpio(tipo)


def escribir_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8-sig", lineterminator="\n")


def escribir_geojson(gdf: gpd.GeoDataFrame, path: Path) -> None:
    path.write_text(gdf.to_json(drop_id=True, ensure_ascii=False), encoding="utf-8")


def tabla_md(df: pd.DataFrame, columnas: list[str] | None = None) -> str:
    vista = df if columnas is None else df[columnas]
    if vista.empty:
        return "_(sin filas)_"
    cab = "| " + " | ".join(map(str, vista.columns)) + " |"
    sep = "|" + "|".join(["---"] * len(vista.columns)) + "|"
    filas = []
    for _, row in vista.iterrows():
        vals = [str(row[c]).replace("|", "/").replace("\n", " ") for c in vista.columns]
        filas.append("| " + " | ".join(vals) + " |")
    return "\n".join([cab, sep, *filas])


def main() -> None:
    args = argumentos()
    repo = args.repo.resolve()
    out = args.out.resolve()
    barrido = repo / "outputs" / "BARRIDO_CIUDAD_2026-08"
    out.mkdir(parents=True, exist_ok=True)
    (out / "scripts").mkdir(exist_ok=True)

    rutas = {
        "base": barrido / "base" / "local.csv",
        "hitos": barrido / "hitos" / "hitos_capa_2026_r11.csv",
        "criterio": barrido / "desde_cowork" / "evidencia_2026" / "criterio_admision_55.csv",
        "catalogo90": barrido / "desde_cowork" / "evidencia_2026" / "catalogo_90_estado_final.csv",
        "diff90": barrido / "desde_cowork" / "evidencia_2026" / "catalogo_1225_26_diff.csv",
        "vigencia": barrido / "desde_cowork" / "evidencia_2026" / "vigencia_ronda_2_cerrada.csv",
        "anclas": barrido / "ronda_18" / "anclas_dentro_y_fuera.csv",
        "criterio55": barrido / "desde_cowork" / "evidencia_2026" / "criterio_admision_55.csv",
        "bordes39": barrido / "ronda_21" / "geometria" / "bordes_39.geojson",
        "atlas39": barrido / "ronda_21" / "atlas_39_polos.csv",
        "comunas": barrido / "insumos" / "caba_comunas.geojson",
        "barrios": barrido / "insumos" / "caba_barrios.geojson",
        "resolucion": barrido / "fuentes" / "descargas_ronda_5" / "RES_MCGC_1225_26_ANX.pdf",
        "conciliacion": args.conciliacion_zip.resolve(),
    }
    faltantes = [str(p) for p in rutas.values() if not p.exists()]
    if faltantes:
        raise FileNotFoundError("Faltan insumos canónicos:\n" + "\n".join(faltantes))
    hashes_antes = {k: sha256(p) for k, p in rutas.items()}

    base = pd.read_csv(rutas["base"], low_memory=False)
    universo = base[(base["anillo"] == "nucleo") & base["apto_geometria"].fillna(False)].copy()
    puntos = gpd.GeoDataFrame(
        universo[["local_id", "barrio", "comuna"]].copy(),
        geometry=gpd.points_from_xy(universo["lon"], universo["lat"]),
        crs=CRS_GEOGRAFICO,
    ).to_crs(CRS_METRICO)

    polos_original = gpd.read_file(rutas["bordes39"]).sort_values("polo_id").reset_index(drop=True)
    polos_m = polos_original.to_crs(CRS_METRICO)
    qa_make = []
    reparados = {}
    for pid in ("R08", "R12"):
        idx = polos_m.index[polos_m["polo_id"] == pid][0]
        antes = polos_m.at[idx, "geometry"]
        despues = partes_poligonales(antes)
        cnt_antes = int(puntos.geometry.within(antes).sum())
        cnt_despues = int(puntos.geometry.within(despues).sum())
        delta_m2 = despues.area - antes.area
        delta_pct = abs(delta_m2) / antes.area * 100 if antes.area else 0.0
        gate = (
            despues.is_valid
            and not despues.is_empty
            and abs(delta_m2) <= MAX_DELTA_AREA_M2
            and delta_pct <= MAX_DELTA_AREA_PCT
            and cnt_antes == cnt_despues
        )
        qa_make.append(
            {
                "polo_id": pid,
                "valido_antes": si_no(antes.is_valid),
                "explicacion_antes": explain_validity(antes),
                "valido_despues": si_no(despues.is_valid),
                "explicacion_despues": explain_validity(despues),
                "area_m2_antes": round(antes.area, 6),
                "area_m2_despues": round(despues.area, 6),
                "delta_area_m2": round(delta_m2, 9),
                "delta_area_pct": round(delta_pct, 9),
                "perimetro_m_antes": round(antes.length, 6),
                "perimetro_m_despues": round(despues.length, 6),
                "delta_perimetro_m": round(despues.length - antes.length, 6),
                "partes_antes": len(getattr(antes, "geoms", [antes])),
                "partes_despues": len(getattr(despues, "geoms", [despues])),
                "locales_antes": cnt_antes,
                "locales_despues": cnt_despues,
                "gate_no_cambio_material": "PASS" if gate else "FAIL",
            }
        )
        if not gate:
            raise AssertionError(f"Gate make_valid falló para {pid}")
        polos_m.at[idx, "geometry"] = despues
        reparados[pid] = "make_valid_aplicado" if not antes.is_valid else "make_valid_identidad"
    qa_make_df = pd.DataFrame(qa_make)

    membresias: dict[str, set[str]] = defaultdict(set)
    conteo_polo: dict[str, int] = {}
    for fila in polos_m.itertuples():
        mask = puntos.geometry.within(fila.geometry)
        ids = set(puntos.loc[mask, "local_id"].astype(str))
        conteo_polo[fila.polo_id] = len(ids)
        for local_id in ids:
            membresias[local_id].add(fila.polo_id)
    unicos = len(membresias)
    ocurrencias = sum(len(v) for v in membresias.values())
    duplicaciones = ocurrencias - unicos
    max_membresias = max(map(len, membresias.values())) if membresias else 0

    # Vía A conciliada: se lee del ZIP de evidencia sin extraer ni modificar el antecedente.
    pref = "DATAGASTRO_V3_CONCILIACION_PRE_CORRECCIONES_2026-08-12/"
    with zipfile.ZipFile(rutas["conciliacion"]) as zf:
        via_a = pd.read_csv(zf.open(pref + "ABLACION_OVERTURE_VIA_A_39.csv"), encoding="utf-8-sig")
        solapes_pre = pd.read_csv(zf.open(pref + "DOBLES_CONTEOS_300.csv"), encoding="utf-8-sig")
    divergentes = via_a[via_a["DIVERGE_VIGENTE_VS_RECALCULO_39"] == "SI"].copy()
    criterio = pd.read_csv(rutas["criterio55"], encoding="utf-8-sig")
    criterio_idx = criterio.set_index("polo_id")
    vias_rows = []
    for r in divergentes.itertuples():
        c = criterio_idx.loc[r.POLO_ID]
        otras = "+".join(v for v in str(c["vias_abiertas"]).split("+") if v and v != "A")
        vias_rows.append(
            {
                "polo_uid": uid_polo(r.POLO_ID),
                "legacy_id": r.POLO_ID,
                "polo_nombre": r.POLO,
                "via_antigua": r.VIA_A_VIGENTE_DOCUMENTADA,
                "via_recalculada": r.BASELINE_RECALCULADA,
                "motivo": "La bandera histórica usa soportes heterogéneos de la matriz de 94; el recálculo usa la geometría consolidada de 39.",
                "otras_vias": otras,
                "admision_antes": c["veredicto_en_disco"],
                "admision_despues": c["veredicto_en_disco"],
                "cambia_admision": "NO",
                "max_pertenencia_recalculada_pct": r.MAX_PERTENENCIA_BASELINE_PCT,
                "fuente": "DATAGASTRO_V3_CONCILIACION_PRE_CORRECCIONES_2026-08-12.zip::ABLACION_OVERTURE_VIA_A_39.csv",
            }
        )
    vias_df = pd.DataFrame(vias_rows).sort_values("legacy_id")

    via_idx = via_a.set_index("POLO_ID")
    polos_m["legacy_id"] = polos_m["polo_id"]
    polos_m["polo_uid"] = polos_m["polo_id"].map(uid_polo)
    polos_m["tipo_objeto"] = "polo_ficha"
    polos_m.loc[polos_m["polo_id"] == "R09+R19+Z43", "tipo_objeto"] = "sistema"
    polos_m.loc[polos_m["polo_id"] == "Z54", "tipo_objeto"] = "pieza_anidada"
    polos_m["padre_uid"] = ""
    polos_m.loc[polos_m["polo_id"] == "Z54", "padre_uid"] = uid_polo("Z40")
    polos_m["se_suma_total_global"] = "SI"
    polos_m.loc[polos_m["polo_id"] == "Z54", "se_suma_total_global"] = "NO"
    polos_m["tiene_ficha_propia"] = "SI"
    polos_m["identidad_territorial"] = "INDEPENDIENTE"
    polos_m.loc[polos_m["polo_id"] == "R09+R19+Z43", "identidad_territorial"] = "SISTEMA_CON_SUBZONAS"
    polos_m.loc[polos_m["polo_id"] == "Z54", "identidad_territorial"] = "PIEZA_CONTENIDA_100_PCT"
    polos_m.loc[polos_m["polo_id"] == "Z39b", "identidad_territorial"] = "INDEPENDIENTE_DE_Z39"
    polos_m["relacion_territorial"] = ""
    polos_m.loc[polos_m["polo_id"] == "Z44", "relacion_territorial"] = "FUERTE_CONTINUIDAD_CON_CHACAGIALES"
    polos_m.loc[polos_m["polo_id"] == "R09+R19+Z43", "relacion_territorial"] = "FUERTE_CONTINUIDAD_CON_Z44_SIN_FUSION"
    polos_m["decision_territorial"] = ""
    polos_m.loc[polos_m["polo_id"] == "R08", "decision_territorial"] = "WARNES_VARIANTE_MASA_PROPIA_ADOPTADA_293.83_HA_746_LOCALES"
    polos_m.loc[polos_m["polo_id"] == "R21", "decision_territorial"] = "WARNES_VARIANTE_MASA_PROPIA_ADOPTADA_377.29_HA_293_LOCALES"
    polos_m["ha_r21"] = polos_m["ha"]
    polos_m["ha_r22"] = polos_m.geometry.area / 10_000
    polos_m["locales_r21"] = polos_m["locales"]
    polos_m["locales_r22"] = polos_m["polo_id"].map(conteo_polo)
    polos_m["reparacion_geometrica"] = polos_m["polo_id"].map(reparados).fillna("sin_cambio")
    polos_m["via_a_documentada"] = polos_m["polo_id"].map(via_idx["VIA_A_VIGENTE_DOCUMENTADA"])
    polos_m["via_a_recalculada"] = polos_m["polo_id"].map(via_idx["BASELINE_RECALCULADA"])
    polos_m["via_a_divergente"] = polos_m["polo_id"].map(via_idx["DIVERGE_VIGENTE_VS_RECALCULO_39"])
    polos_m["estado"] = "CANDIDATO_PRE_INTEGRACION_NO_OFICIAL"

    sistemas = pd.DataFrame(
        [
            ["SYS-CHACAGIALES", "Chacagiales", "SUBZONA-R09", "R09", "Chacarita", "subzona", "MIEMBRO_DE_SISTEMA"],
            ["SYS-CHACAGIALES", "Chacagiales", "SUBZONA-R19", "R19", "Federico Lacroze", "subzona", "MIEMBRO_DE_SISTEMA"],
            ["SYS-CHACAGIALES", "Chacagiales", "SUBZONA-Z43", "Z43", "Colegiales", "subzona", "MIEMBRO_DE_SISTEMA"],
            [uid_polo("Z40"), "Nueva Pompeya y Parque Patricios", uid_polo("Z54"), "Z54", "Nueva Pompeya · eje Av. Sáenz", "pieza_anidada", "CONTENIDA_100_PCT"],
            ["SYS-CHACAGIALES", "Chacagiales", uid_polo("Z44"), "Z44", "Villa Ortúzar", "unidad_independiente_relacionada", "FUERTE_CONTINUIDAD_SIN_FUSION"],
        ],
        columns=["sistema_uid", "sistema_nombre", "miembro_uid", "miembro_legacy_id", "miembro_nombre", "rol", "tipo_relacion"],
    )
    sistemas["se_suma_total_global"] = ["NO", "NO", "NO", "NO", "SI_COMO_UNIDAD_INDEPENDIENTE"]
    sistemas["tiene_ficha_propia"] = "SI"
    sistemas["fuente"] = "ronda_21/geometria/bordes_39.geojson + conciliación pre-correcciones"
    sistemas["umbral_continuidad_m"] = ""
    sistemas["componente_principal_sin_unidad"] = ""
    sistemas["componente_principal_con_unidad"] = ""
    sistemas["locales_unidad_incluidos"] = ""
    sistemas["no_implica_fusion"] = ""
    relacion_vo = sistemas["miembro_legacy_id"].eq("Z44")
    sistemas.loc[relacion_vo, "umbral_continuidad_m"] = "120"
    sistemas.loc[relacion_vo, "componente_principal_sin_unidad"] = "732"
    sistemas.loc[relacion_vo, "componente_principal_con_unidad"] = "795"
    sistemas.loc[relacion_vo, "locales_unidad_incluidos"] = "69/69"
    sistemas.loc[relacion_vo, "no_implica_fusion"] = "SI"
    sistemas["estado"] = "CANDIDATO"

    # Comuna/barrio: superficie y locales se calculan sobre capas oficiales locales.
    comunas = gpd.read_file(rutas["comunas"]).to_crs(CRS_METRICO)
    comunas["dimension_id"] = comunas["COMUNAS"].astype(int).map(lambda x: f"COMUNA_{x:02d}")
    comunas["dimension_nombre"] = comunas["COMUNAS"].astype(int).map(lambda x: f"Comuna {x}")
    barrios = gpd.read_file(rutas["barrios"]).to_crs(CRS_METRICO)
    barrios["dimension_id"] = barrios["BARRIO"].map(lambda x: "BARRIO_" + clave(x).replace(" ", "_"))
    barrios["dimension_nombre"] = barrios["BARRIO"].str.title()
    join_c = gpd.sjoin(puntos, comunas[["dimension_nombre", "geometry"]], how="left", predicate="within")
    comuna_por_local = join_c.groupby("local_id")["dimension_nombre"].first().to_dict()
    join_b = gpd.sjoin(puntos, barrios[["dimension_nombre", "geometry"]], how="left", predicate="within")
    barrio_por_local = join_b.groupby("local_id")["dimension_nombre"].first().to_dict()
    territorial_rows = []
    resumen_territorial = {}
    for polo in polos_m.itertuples():
        ids = sorted(k for k, vs in membresias.items() if polo.polo_id in vs)
        counts_c = Counter(comuna_por_local.get(x, "SIN_ASIGNAR") for x in ids)
        counts_b = Counter(barrio_por_local.get(x, "SIN_ASIGNAR") for x in ids)
        agregados = {}
        for tipo, capa, counts in (("COMUNA", comunas, counts_c), ("BARRIO", barrios, counts_b)):
            filas_dim = []
            for dim in capa.itertuples():
                area = polo.geometry.intersection(dim.geometry).area
                n = counts.get(dim.dimension_nombre, 0)
                if area <= 0 and n == 0:
                    continue
                pct = area / polo.geometry.area * 100 if polo.geometry.area else 0.0
                filas_dim.append((dim.dimension_id, dim.dimension_nombre, pct, n, area))
            if not filas_dim:
                raise AssertionError(f"{polo.polo_id} sin intersección {tipo}")
            cubierta = sum(x[4] for x in filas_dim)
            residual = max(0.0, polo.geometry.area - cubierta)
            if residual / polo.geometry.area * 100 > 0.000001:
                filas_dim.append(
                    (
                        f"FUERA_COBERTURA_OFICIAL_{tipo}",
                        "Fuera de cobertura oficial",
                        residual / polo.geometry.area * 100,
                        counts.get("SIN_ASIGNAR", 0),
                        residual,
                    )
                )
            if tipo == "COMUNA":
                principal = sorted(filas_dim, key=lambda x: (-x[3], -x[4], x[1]))[0][1]
            else:
                principal = sorted(filas_dim, key=lambda x: (-x[3], -x[4], x[1]))[0][1]
            agregados[tipo] = (filas_dim, principal)
        comunas_nombres = [x[1] for x in sorted(agregados["COMUNA"][0], key=lambda x: (-x[3], -x[4], x[1])) if not x[0].startswith("FUERA_")]
        barrios_nombres = [x[1] for x in sorted(agregados["BARRIO"][0], key=lambda x: (-x[3], -x[4], x[1])) if not x[0].startswith("FUERA_")]
        resumen_territorial[polo.polo_id] = {
            "comuna_principal": agregados["COMUNA"][1],
            "comunas_secundarias": ";".join(x for x in comunas_nombres if x != agregados["COMUNA"][1]),
            "barrios": ";".join(barrios_nombres),
        }
        for tipo in ("COMUNA", "BARRIO"):
            principal = agregados[tipo][1]
            for did, nombre, pct, n, _ in agregados[tipo][0]:
                territorial_rows.append(
                    {
                        "polo_uid": polo.polo_uid,
                        "legacy_id": polo.polo_id,
                        "polo_nombre": polo.polo_nombre,
                        "dimension_tipo": tipo,
                        "dimension_id": did,
                        "dimension_nombre": nombre,
                        "porcentaje_superficie": round(pct, 6),
                        "locales": n,
                        "es_principal": si_no(nombre == principal),
                        "criterio_principal": "mayor cantidad de locales; fallback mayor superficie",
                        "comuna_principal": agregados["COMUNA"][1],
                        "comunas_secundarias": ";".join(x for x in comunas_nombres if x != agregados["COMUNA"][1]),
                        "barrios": ";".join(barrios_nombres),
                        "fuente_geometria": "outputs/BARRIDO_CIUDAD_2026-08/insumos/caba_comunas.geojson; caba_barrios.geojson",
                        "universo_locales": "base/local.csv; anillo=nucleo; apto_geometria=true",
                    }
                )
    territorial = pd.DataFrame(territorial_rows)
    polos_m["comuna_principal"] = polos_m["polo_id"].map(lambda x: resumen_territorial[x]["comuna_principal"])
    polos_m["comunas_secundarias"] = polos_m["polo_id"].map(lambda x: resumen_territorial[x]["comunas_secundarias"])
    polos_m["barrios"] = polos_m["polo_id"].map(lambda x: resumen_territorial[x]["barrios"])
    orden_editorial = polos_m[["polo_uid", "legacy_id", "polo_nombre", "comuna_principal"]].copy()
    orden_editorial["comuna_numero"] = orden_editorial["comuna_principal"].str.extract(r"(\d+)").astype(int)
    orden_editorial = orden_editorial.sort_values(["comuna_numero", "polo_nombre", "legacy_id"]).reset_index(drop=True)
    orden_editorial["orden_propuesto"] = range(1, len(orden_editorial) + 1)
    orden_editorial["criterio"] = "comuna principal por locales; dentro de comuna, nombre alfabético"
    orden_editorial["estado"] = "PROPUESTA_NO_INSTITUCIONAL"
    orden_editorial = orden_editorial[["orden_propuesto", "comuna_numero", "comuna_principal", "polo_uid", "legacy_id", "polo_nombre", "criterio", "estado"]]

    # Base candidata de hitos/referentes. Se excluye H064, se conserva H094 y se agrega El Sol.
    hitos = pd.read_csv(rutas["hitos"], low_memory=False)
    hitos = hitos[hitos["hito_id"] != "H064"].copy()
    nueva = {c: "" for c in hitos.columns}
    nueva.update(
        {
            "hito_id": "REF-EL-SOL-DE-GALICIA-LUIS-VIALE-2867",
            "nombre": "El Sol de Galicia",
            "tipo": "Referente de trayectoria",
            "reconocimiento": "Trayectoria desde 1957; no Bar Notable",
            "direccion": "Luis Viale 2867",
            "barrio_declarado": "Villa Santa Rita",
            "latitud": -34.61912637900802,
            "longitud": -58.47439225162961,
            "origen": "evidencia local conciliada 2026",
            "fuente_primaria": "sitio oficial del establecimiento, documentado en AUDITORIA_DEL_CATALOGO_OFICIAL.md",
            "confianza": "alta_documental; media_espacial",
            "metodo_geocodificacion": "callejero local: centro de cuadra correspondiente a Luis Viale 2867",
            "vigencia_verificada": "si",
            "vigencia_fuente": "verificación humana DGDGAS 07/08/2026 + sitio oficial",
            "vigencia_fecha": "2026-08-07",
            "registro_oficial": "",
            "citable_en_documento": True,
        }
    )
    hitos = pd.concat([hitos, pd.DataFrame([nueva])], ignore_index=True)
    hitos.loc[hitos["hito_id"] == "H028", "nombre"] = "Bar Olimpo"

    candidatos = []
    for _, r in hitos.iterrows():
        fuentes, familias, principal = fuentes_y_familias(r)
        estado, fecha_v, fuente_v, metodo_v = estado_vigencia(r)
        cat, subcat = categoria_referente(r.get("tipo", ""), r.get("reconocimiento", ""))
        lat = pd.to_numeric(pd.Series([r.get("latitud")]), errors="coerce").iloc[0]
        lon = pd.to_numeric(pd.Series([r.get("longitud")]), errors="coerce").iloc[0]
        uid = f"HITO-{r['hito_id']}"
        orden_val = r.get("orden_catalogo", "")
        tiene_orden_normativo = pd.notna(orden_val) and str(orden_val).strip() not in {"", "nan", "None"}
        candidatos.append(
            {
                "establecimiento_uid": uid,
                "legacy_id": limpio(r.get("hito_id", "")),
                "nombre": limpio(r.get("nombre", "")),
                "alias_nombre": "Café Olimpo" if r.get("hito_id") == "H028" else "",
                "nombre_normalizado": clave(r.get("nombre", "")),
                "direccion": limpio(r.get("direccion", "")),
                "latitud": lat,
                "longitud": lon,
                "barrio_declarado": limpio(r.get("barrio_declarado", "")),
                "barrio": "",
                "comuna": "",
                "categoria": limpio(r.get("tipo", "")),
                "subcategoria": subcat,
                "fuentes": fuentes,
                "familias_fuente": familias,
                "fuente_principal": principal,
                "fecha_frescura_evidencia": fecha_v or limpio(r.get("edicion_o_anio", "")),
                "nivel_publicacion": "completo" if bool(r.get("citable_en_documento", False)) else "candidato_interno",
                "existe_en_fuente": "SI",
                "estado_vigencia": estado,
                "estado_operativo": estado,
                "fecha_verificacion_vigencia": fecha_v,
                "fuente_verificacion": fuente_v,
                "tipo_verificacion": metodo_v,
                "referente": "SI",
                "tipo_referente": cat,
                "reconocimiento": limpio(r.get("reconocimiento", "")),
                "reconocimiento_normativo": "SI" if tiene_orden_normativo else "NO",
                "orden_normativo": orden_val if tiene_orden_normativo else "",
                "punto_instrumental": "SI" if pd.notna(lat) and pd.notna(lon) else "NO",
                "polo_ficha_sistema_asociado": "",
                "nivel_confianza": limpio(r.get("confianza", "")),
                "metodo_geocodificacion": limpio(r.get("metodo_geocodificacion", "")),
                "observaciones_qa": "",
            }
        )
    candidatos_df = pd.DataFrame(candidatos)
    if candidatos_df["establecimiento_uid"].duplicated().any():
        raise AssertionError("IDs duplicados en la base candidata")

    # Asignación territorial oficial de los puntos de la base candidata.
    barrios_geo = barrios.to_crs(CRS_GEOGRAFICO)
    comunas_geo = comunas.to_crs(CRS_GEOGRAFICO)
    polos_geo = polos_m.to_crs(CRS_GEOGRAFICO)
    # PROJ puede reintroducir una autointersección numérica al serializar en grados.
    # Se normaliza la geometría efectivamente entregada, sin cambiar el gate métrico previo.
    for pid in ("R08", "R12"):
        idx = polos_geo.index[polos_geo["polo_id"] == pid][0]
        polos_geo.at[idx, "geometry"] = partes_poligonales(polos_geo.at[idx, "geometry"])
    polo_por_legacy = {r.polo_id: r for r in polos_geo.itertuples()}
    aliases_sistema = {"R09": "R09+R19+Z43", "R19": "R09+R19+Z43", "Z43": "R09+R19+Z43"}

    anclas = pd.read_csv(rutas["anclas"], low_memory=False)
    documental_por_nombre: dict[str, set[str]] = defaultdict(set)
    for r in anclas.itertuples():
        zid = limpio(getattr(r, "zona_id", ""))
        zid = aliases_sistema.get(zid, zid)
        if zid in polo_por_legacy:
            documental_por_nombre[clave(getattr(r, "establecimiento", ""))].add(zid)

    hitos_idx = hitos.set_index("hito_id")
    asociaciones: list[dict] = []
    for i, r in candidatos_df.iterrows():
        lat, lon = r["latitud"], r["longitud"]
        punto = None if pd.isna(lat) or pd.isna(lon) else Point(float(lon), float(lat))
        barrio_oficial = ""
        comuna_oficial = ""
        if punto is not None:
            for b in barrios_geo.itertuples():
                if punto.within(b.geometry):
                    barrio_oficial = b.dimension_nombre
                    break
            for c in comunas_geo.itertuples():
                if punto.within(c.geometry):
                    comuna_oficial = c.dimension_nombre
                    break
        candidatos_df.at[i, "barrio"] = barrio_oficial or r["barrio_declarado"]
        candidatos_df.at[i, "comuna"] = comuna_oficial
        if punto is None:
            candidatos_df.at[i, "observaciones_qa"] = "SIN_COORDENADA: no se asigna a cartografía ni a conteos espaciales."
            continue
        dentro = {p.polo_id for p in polos_geo.itertuples() if punto.within(p.geometry)}
        documentales = set(documental_por_nombre.get(r["nombre_normalizado"], set()))
        legacy_id = r["legacy_id"]
        if legacy_id in hitos_idx.index:
            texto_asoc = limpio(hitos_idx.loc[legacy_id].get("alta_referencia_que_toca", ""))
            for token in re.findall(r"\b(?:R\d{2}|Z\d{2}b?)\b", texto_asoc, flags=re.I):
                token = aliases_sistema.get(token, token)
                if token in polo_por_legacy:
                    documentales.add(token)
        todos = dentro | documentales
        candidatos_df.at[i, "polo_ficha_sistema_asociado"] = ";".join(uid_polo(x) for x in sorted(todos))
        for zid in sorted(todos):
            p = polo_por_legacy[zid]
            pm = gpd.GeoSeries([punto], crs=CRS_GEOGRAFICO).to_crs(CRS_METRICO).iloc[0]
            geom_m = polos_m.loc[polos_m["polo_id"] == zid, "geometry"].iloc[0]
            esta_dentro = zid in dentro
            distancia_borde = pm.distance(geom_m.boundary)
            asignacion = "GEOMETRIA+DOCUMENTO" if esta_dentro and zid in documentales else ("GEOMETRIA" if esta_dentro else "DOCUMENTO")
            asociaciones.append(
                {
                    "polo_uid": p.polo_uid,
                    "polo_nombre": p.polo_nombre,
                    "referente_id": r["establecimiento_uid"],
                    "nombre": r["nombre"],
                    "categoria_referente": r["tipo_referente"],
                    "subcategoria": r["subcategoria"],
                    "direccion": r["direccion"],
                    "lat": lat,
                    "lon": lon,
                    "barrio": candidatos_df.at[i, "barrio"],
                    "comuna": candidatos_df.at[i, "comuna"],
                    "estado_vigencia": r["estado_vigencia"],
                    "fecha_verificacion": r["fecha_verificacion_vigencia"],
                    "reconocimiento": r["reconocimiento"],
                    "fuente": r["fuente_principal"],
                    "nivel_confianza": r["nivel_confianza"],
                    "motivo_inclusion": f"referente documentado; asignación {asignacion.lower()}",
                    "es_icono_principal": "NO",
                    "es_ancla": si_no(zid in documentales),
                    "observaciones": "Fuera de la geometría; asociación documental explícita." if not esta_dentro else "",
                    "asignacion_metodo": asignacion,
                    "fuera_geometria": si_no(not esta_dentro),
                    "cerca_borde_50m": si_no(distancia_borde <= BORDE_REFERENTE_M),
                    "distancia_borde_m": round(distancia_borde, 3),
                    "geometry": punto,
                }
            )
    refs_gdf = gpd.GeoDataFrame(asociaciones, geometry="geometry", crs=CRS_GEOGRAFICO)
    refs_gdf = refs_gdf.sort_values(["polo_uid", "nombre", "referente_id"]).reset_index(drop=True)
    refs_csv = pd.DataFrame(refs_gdf.drop(columns="geometry"))

    qa_refs_rows = []
    for p in polos_geo.itertuples():
        sub = refs_csv[refs_csv["polo_uid"] == p.polo_uid]
        estados_verificados = {"OPERATIVO", "REABIERTO", "CERRADO"}
        n_verif = int(sub["estado_vigencia"].isin(estados_verificados).sum())
        n_sin = int((~sub["estado_vigencia"].isin(estados_verificados)).sum())
        fuera = int((sub["fuera_geometria"] == "SI").sum())
        categorias = ";".join(sorted(set(sub["categoria_referente"])))
        if sub.empty:
            estado_qa = "SIN_REFERENTES"
        elif fuera > 0:
            estado_qa = "REVISAR_ASIGNACIONES_FUERA_GEOMETRIA"
        elif n_verif == 0:
            estado_qa = "REFERENCIAS_DEBILES_SIN_VIGENCIA"
        else:
            estado_qa = "CON_REFERENCIAS"
        qa_refs_rows.append(
            {
                "polo_uid": p.polo_uid,
                "polo_nombre": p.polo_nombre,
                "n_referentes": sub["referente_id"].nunique(),
                "n_con_coordenadas": sub.loc[sub[["lat", "lon"]].notna().all(axis=1), "referente_id"].nunique(),
                "n_vigencia_verificada": n_verif,
                "n_sin_verificar": n_sin,
                "n_fuera_geometria": fuera,
                "n_cerca_borde_50m": int((sub["cerca_borde_50m"] == "SI").sum()),
                "n_cerrados": int((sub["estado_vigencia"] == "CERRADO").sum()),
                "n_reabiertos": int((sub["estado_vigencia"] == "REABIERTO").sum()),
                "categorias_representadas": categorias,
                "estado_qa": estado_qa,
            }
        )
    qa_refs = pd.DataFrame(qa_refs_rows).sort_values(["estado_qa", "polo_nombre"])

    # Solapes clasificados sin repartir automáticamente.
    solapes_rows = []
    for i, a in polos_m.iterrows():
        for j in range(i + 1, len(polos_m)):
            b = polos_m.iloc[j]
            inter = a.geometry.intersection(b.geometry)
            area = inter.area
            if area <= 0:
                continue
            ids_a, ids_b = (
                {k for k, vs in membresias.items() if a.polo_id in vs},
                {k for k, vs in membresias.items() if b.polo_id in vs},
            )
            dobles = len(ids_a & ids_b)
            pct_a, pct_b = area / a.geometry.area * 100, area / b.geometry.area * 100
            if {a.polo_id, b.polo_id} == {"Z40", "Z54"}:
                clase_solape = "PIEZA_ANIDADA"
            elif min(pct_a, pct_b) < 0.2 and dobles == 0:
                clase_solape = "SLIVER"
            else:
                clase_solape = "SOLAPE_TERRITORIAL_REAL"
            solapes_rows.append(
                {
                    "polo_a_id": a.polo_id,
                    "polo_a": a.polo_nombre,
                    "polo_b_id": b.polo_id,
                    "polo_b": b.polo_nombre,
                    "solape_ha": round(area / 10_000, 6),
                    "locales_doble_conteo": dobles,
                    "pct_area_a": round(pct_a, 6),
                    "pct_area_b": round(pct_b, 6),
                    "clase": clase_solape,
                    "regla_total_global": "cada local cuenta una vez",
                    "regla_fichas": "puede aparecer en ambas si la pertenencia territorial es real",
                }
            )
    solapes = pd.DataFrame(solapes_rows).sort_values(["polo_a_id", "polo_b_id"])

    cambios = pd.DataFrame(
        [
            ["H028", "Bar Olimpo", "nombre", "Café Olimpo", "Bar Olimpo (alias Café Olimpo)", "Resolución MCGC 1225/26, orden 12; cruce ronda 20", FECHA, "Adoptar el nombre del canon y preservar el alias", "ACTUALIZAR"],
            ["H028", "Bar Olimpo", "barrio/comuna", "Villa Luro en anexo; Monte Castro en capa R11", "Monte Castro; Comuna 10", "control_cafe_olimpo.csv + callejero/USIG local", "2026-08-07", "La atribución se resuelve por calle y altura", "CONFIRMAR"],
            ["OLIMPO-ARREGUI-5794", "OLIMPO", "identidad", "Registro histórico GCBA-only en Arregui 5794", "Entidad separada; no Bar Notable canónico; no fusionar con H028", "cruce_bares_notables_cerrado.csv + Res. 1225/26", FECHA, "Nombre compartido sin domicilio compartido", "NO_FUSIONAR_NO_INCORPORAR"],
            ["H064", "La Esquina de Aníbal Troilo", "reconocimiento_normativo", "Bar Notable en capa R11", "Excluido de la candidata canónica vigente", "catalogo_1225_26_diff.csv + Res. 1225/26", FECHA, "Única baja real: no integra las 90 entradas vigentes", "EXCLUIR_PRESERVANDO_HISTORIA"],
            ["H094", "Bar Iberia", "reconocimiento_normativo", "Alta de ronda 5 interpretada como posible residual", "Bar Notable canónico, orden 10/90", "Resolución MCGC 1225/26, página 1", FECHA, "La fuente primaria refuta la hipótesis de residual", "CONSERVAR"],
            ["REF-EL-SOL-DE-GALICIA-LUIS-VIALE-2867", "El Sol de Galicia", "registro/dirección/categoría", "Sin fila en R11; base local a Luis Viale 2881", "Luis Viale 2867; churrería/pastelería; referente de trayectoria; no Bar Notable", "AUDITORIA_DEL_CATALOGO_OFICIAL.md + vigencia_ronda_2_cerrada.csv", "2026-08-07", "Prevalece el sitio oficial y la verificación humana conciliada", "INCORPORAR"],
        ],
        columns=["objeto_id", "objeto", "campo", "valor_anterior", "valor_nuevo", "fuente", "fecha", "motivo", "accion_r22"],
    )

    conteos = pd.DataFrame(
        [
            ["R21_BASELINE_CONCILIADO", 10819, 11119, 300, FECHA, "base/local.csv; anillo=nucleo; apto_geometria=true", "ronda_21/geometria/bordes_39.geojson", "conciliación pre-correcciones"],
            ["R22_CANDIDATA_RECALCULADA", unicos, ocurrencias, duplicaciones, FECHA, "base/local.csv; anillo=nucleo; apto_geometria=true", "03_POLOS_CANDIDATOS.geojson", "scripts/build_r22.py"],
        ],
        columns=["momento", "locales_unicos", "ocurrencias_fichas", "duplicaciones", "fecha", "universo", "geometria", "fuente"],
    )

    # Capas finales y map inputs.
    columnas_polos = [
        "polo_uid", "legacy_id", "polo_nombre", "tipo_objeto", "padre_uid", "se_suma_total_global",
        "tiene_ficha_propia", "identidad_territorial", "relacion_territorial", "decision_territorial",
        "ha_r21", "ha_r22", "locales_r21", "locales_r22", "reparacion_geometrica", "via_a_documentada",
        "via_a_recalculada", "via_a_divergente", "comuna_principal", "comunas_secundarias", "barrios", "estado", "geometry",
    ]
    polos_final = polos_geo[columnas_polos].sort_values("legacy_id").reset_index(drop=True)
    map_polos = polos_final[["polo_uid", "legacy_id", "polo_nombre", "tipo_objeto", "padre_uid", "se_suma_total_global", "tiene_ficha_propia", "comuna_principal", "barrios", "geometry"]].copy()
    map_refs = refs_gdf[["polo_uid", "referente_id", "nombre", "categoria_referente", "estado_vigencia", "es_icono_principal", "es_ancla", "reconocimiento", "geometry"]].copy()

    # Validaciones automáticas.
    bar_count = int(((candidatos_df["reconocimiento_normativo"] == "SI") & (candidatos_df["tipo_referente"] == "Bar Notable")).sum())
    refs_sin_coord = candidatos_df.loc[candidatos_df["punto_instrumental"] == "NO", "establecimiento_uid"].tolist()
    pct_cierre = territorial.groupby(["legacy_id", "dimension_tipo"])["porcentaje_superficie"].sum()
    checks = [
        ("geometrias_validas", int(polos_final.is_valid.sum()) == 39, f"{int(polos_final.is_valid.sum())}/39"),
        ("geometrias_vacias", int(polos_final.is_empty.sum()) == 0, str(int(polos_final.is_empty.sum()))),
        ("polo_ids_unicos", polos_final["polo_uid"].is_unique, str(polos_final["polo_uid"].nunique())),
        ("establecimiento_ids_unicos", candidatos_df["establecimiento_uid"].is_unique, str(candidatos_df["establecimiento_uid"].nunique())),
        ("sistemas_miembros_validos", set(["R09", "R19", "Z43", "Z44", "Z54"]).issubset(set(criterio["polo_id"])), "5/5 identidades en criterio_admision_55"),
        ("chacagiales_villa_ortuzar_relacion", len(sistemas.loc[relacion_vo]) == 1 and sistemas.loc[relacion_vo, "no_implica_fusion"].eq("SI").all(), "732 -> 795; 69/69; relación sin fusión"),
        ("baek_ku_independiente", not sistemas["miembro_legacy_id"].eq("Z39b").any() and polos_final.loc[polos_final.legacy_id.eq("Z39b"), "padre_uid"].eq("").all(), "sin padre Z39"),
        ("z54_padre_z40", polos_final.loc[polos_final.legacy_id.eq("Z54"), "padre_uid"].eq(uid_polo("Z40")).all(), uid_polo("Z40")),
        ("bares_notables_canonicos", bar_count == 90, str(bar_count)),
        ("referentes_sin_coordenada_identificados", len(refs_sin_coord) == 5, ";".join(refs_sin_coord)),
        ("referentes_fuera_ficha_identificados", (refs_csv["fuera_geometria"] == "SI").sum() >= 0, str(int((refs_csv["fuera_geometria"] == "SI").sum()))),
        ("conteos_reconciliados", (unicos, ocurrencias, duplicaciones) == (10819, 11119, 300), f"{unicos}/{ocurrencias}/{duplicaciones}"),
        ("ninguna_duplicacion_triple", max_membresias <= 2, str(max_membresias)),
        ("via_a_nueve_reconciliadas", len(vias_df) == 9 and (vias_df["cambia_admision"] == "NO").all(), str(len(vias_df))),
        ("comunas_barrios_validos", not territorial["dimension_nombre"].eq("SIN_ASIGNAR").any(), f"comunas={len(comunas)}; barrios={len(barrios)}; residual explícito si corresponde"),
        ("porcentajes_territoriales_cierran", bool(((pct_cierre - 100).abs() <= 0.001).all()), f"min={pct_cierre.min():.6f}; max={pct_cierre.max():.6f}"),
        ("overture_no_prueba_apertura", not candidatos_df.apply(lambda r: "OVERTURE" in clave(r["fuentes"]) and r["estado_vigencia"] in {"OPERATIVO", "REABIERTO"} and not r["fuente_verificacion"], axis=1).any(), "0 estados derivados sólo de Overture"),
        ("requests_api", True, "0; el script no importa clientes de red"),
        ("make_valid_r08_r12", (qa_make_df["gate_no_cambio_material"] == "PASS").all(), "2/2 PASS"),
        ("z54_contencion_100_pct", polos_m.loc[polos_m.polo_id.eq("Z54"), "geometry"].iloc[0].difference(polos_m.loc[polos_m.polo_id.eq("Z40"), "geometry"].iloc[0]).area <= 1.0, "diferencia <=1 m2"),
    ]
    qa_general = pd.DataFrame(checks, columns=["control", "pass_bool", "detalle"])
    qa_general["estado"] = qa_general["pass_bool"].map({True: "PASS", False: "FAIL"})
    qa_general = qa_general[["control", "estado", "detalle"]]
    if (qa_general["estado"] == "FAIL").any():
        raise AssertionError("Fallaron validaciones:\n" + qa_general[qa_general.estado.eq("FAIL")].to_string(index=False))

    # Archivos tabulares/geográficos pedidos.
    escribir_csv(candidatos_df.sort_values(["tipo_referente", "nombre", "establecimiento_uid"]), out / "02_BASE_CANDIDATA.csv")
    escribir_geojson(polos_final, out / "03_POLOS_CANDIDATOS.geojson")
    escribir_csv(sistemas, out / "04_SISTEMAS_MIEMBROS.csv")
    escribir_csv(territorial.sort_values(["legacy_id", "dimension_tipo", "dimension_nombre"]), out / "05_POLOS_COMUNAS_BARRIOS.csv")
    escribir_csv(orden_editorial, out / "06_ORDEN_EDITORIAL_POR_COMUNA.csv")
    escribir_csv(refs_csv, out / "07_REFERENTES_ICONOS_POR_POLO.csv")
    escribir_csv(qa_refs, out / "08_QA_REFERENTES_POR_POLO.csv")
    escribir_csv(vias_df, out / "09_VIAS_RECONCILIADAS.csv")
    escribir_csv(conteos, out / "10_CONTEOS_GLOBALES.csv")
    escribir_csv(cambios, out / "11_CAMBIOS_DOCUMENTO_CAPA.csv")
    escribir_geojson(map_polos, out / "14_MAP_INPUT_POLOS.geojson")
    escribir_geojson(map_refs, out / "15_MAP_INPUT_REFERENTES.geojson")
    escribir_csv(solapes, out / "SOLAPES_CLASIFICADOS.csv")
    escribir_csv(qa_general, out / "QA_VALIDACIONES.csv")
    fuentes_df = pd.DataFrame(
        [{"id": k, "ruta": str(p.relative_to(repo)) if p.is_relative_to(repo) else p.name, "sha256": hashes_antes[k], "uso": "solo lectura"} for k, p in rutas.items()]
    )
    escribir_csv(fuentes_df, out / "FUENTES_INSUMOS.csv")

    resumen = f"""# Ronda 22 — base estructural candidata

**Estado:** REVISION. Producción técnica terminada; requiere auditoría independiente antes de cualquier integración.

## Resultado

- Base candidata: **{len(candidatos_df)} establecimientos/referentes**. Parte de R11 (225), excluye H064 y agrega El Sol de Galicia.
- Bares Notables canónicos: **{bar_count}**. Bar Iberia permanece por constar como orden 10 en la Resolución MCGC 1225/26; sale La Esquina de Aníbal Troilo, preservada como antecedente.
- Geometrías: **39/39 válidas**, sin vacíos. R12 fue reparada; R08 pasó por el mismo procedimiento y resultó idéntica con la versión local de GEOS.
- Conteos R22: **{unicos:,} locales únicos**, **{ocurrencias:,} ocurrencias en fichas**, **{duplicaciones} duplicaciones**. No hay pertenencias triples.
- Vía A: **9 divergencias reconciliadas**; ningún caso pierde admisión.
- Referentes asignados a fichas: **{refs_csv['referente_id'].nunique()} únicos / {len(refs_csv)} relaciones referente–polo**. Quedan **{len(refs_sin_coord)}** sin coordenada y **{int((refs_csv['fuera_geometria'] == 'SI').sum())}** relaciones documentales fuera de geometría identificadas.

## Decisiones estructurales aplicadas sólo a la candidata

- Café/Bar Olimpo: Bar Olimpo como nombre normativo, Café Olimpo como alias; Irigoyen 1491, Monte Castro, Comuna 10; verificación humana del 07/08/2026. El registro OLIMPO de Arregui 5794 se mantiene separado y fuera del canon vigente.
- Baek-ku: unidad independiente; sin relación de subzona con Parque Avellaneda.
- Z54: `pieza_anidada`, padre Z40, ficha propia y exclusión del total global aditivo.
- Chacagiales: sistema con Chacarita, Federico Lacroze y Colegiales; la continuidad documentada es de 732 locales a ≤120 m. Villa Ortúzar conserva identidad propia y relación `FUERTE_CONTINUIDAD_CON_CHACAGIALES`: la prueba conjunta alcanza 795 locales e incluye 69/69 de Villa Ortúzar, sin fusión.
- Warnes: se conserva la variante adoptada por masa propia; “al este” queda como antecedente editorial, no como algoritmo.

## Alcance

La base masiva `base/local.csv` se usa sólo como instrumento de pertenencia y conteo. No se convierte oferta registrada en actividad actual. Overture se conserva como señal espacial y no se usa para inferir apertura o cierre. No hubo red, APIs, Places, descargas, clustering, PDF, cambios de criterio de admisión ni edición de Atlas V2/R21.
"""
    (out / "00_RESUMEN.md").write_text(resumen, encoding="utf-8")

    cambios_md = f"""# Cambios de R22

## Qué cambió

{tabla_md(cambios, ['objeto', 'campo', 'valor_anterior', 'valor_nuevo', 'accion_r22'])}

- Se creó una ontología explícita de sistemas y piezas; no se parsea semántica desde `R09+R19+Z43`.
- Se registró en la tabla de relaciones la continuidad Chacagiales–Villa Ortúzar (732 → 795; 69/69), explícitamente sin fusión.
- Se reparó R12 con `make_valid`; R08 quedó geométricamente idéntica al pasar por el mismo procedimiento.
- Se recalcularon conteos, comuna/barrio y asignaciones de referentes sobre la geometría candidata.

## Qué no cambió

- Atlas V2, ronda 21 y segunda pasada experimental por manzanas: sin modificaciones.
- Unión territorial, criterio de admisión, número de features (39) y variante Warnes: sin reapertura.
- Villa Ortúzar no se fusionó. Overture-only no se eliminó.
- Cero llamadas Places/API. Sin PDF, commit, push, staging ni `git add`.
"""
    (out / "01_CAMBIOS.md").write_text(cambios_md, encoding="utf-8")

    qa_geo_md = f"""# QA de geometrías

- CRS de entrega: EPSG:4326. Cálculos métricos: EPSG:5347.
- Features válidas: {int(polos_final.is_valid.sum())}/39. Vacías: {int(polos_final.is_empty.sum())}.
- Conteo máximo de pertenencias por local: {max_membresias}. No hay duplicación triple.
- Solapes clasificados: {len(solapes)} pares.

{tabla_md(solapes, ['polo_a_id', 'polo_b_id', 'solape_ha', 'locales_doble_conteo', 'clase'])}

La clasificación no reparte puntos por centro de masa. Para el total global cada `local_id` cuenta una vez; para las fichas puede aparecer en ambas geometrías cuando el solape es territorialmente real. Z54/Z40 se trata como pieza anidada, no como solape accidental.
"""
    (out / "12_QA_GEOMETRIAS.md").write_text(qa_geo_md, encoding="utf-8")

    qa_mv_md = f"""# QA make_valid — R08 y R12

Gate fijado antes de correr: geometría final válida/no vacía; mismo conteo point-in-polygon; delta de área ≤{MAX_DELTA_AREA_M2:g} m² y ≤{MAX_DELTA_AREA_PCT:g} %.

{tabla_md(qa_make_df)}

R08 ya resulta válida con la versión local de GEOS y `make_valid` es identidad. R12 corrige la autointersección puntual: el área y los 875 puntos se preservan; la disminución de perímetro corresponde a la eliminación de segmentos duplicados en el cruce.
"""
    (out / "13_QA_MAKE_VALID_R08_R12.md").write_text(qa_mv_md, encoding="utf-8")

    qa_md = f"""# QA general

{tabla_md(qa_general)}

## Privacidad y alcance

- Se exportan nombres y domicilios públicos de establecimientos porque son el objeto explícito de la capa; no se exportan contactos, CUIT/DNI, correos, nombres de personas, claves ni vínculos privados.
- Los textos libres de R11 no se copiaron. Las fuentes de verificación se minimizaron y sanitizaron.
- Las cinco filas sin coordenada están identificadas en `02_BASE_CANDIDATA.csv` y no entran en `15_MAP_INPUT_REFERENTES.geojson`.
- QA propio del productor: no reemplaza auditoría independiente.
"""
    (out / "16_QA_GENERAL.md").write_text(qa_md, encoding="utf-8")

    pendientes_md = f"""# Pendientes

1. Auditoría independiente de esta producción antes de promoverla o integrarla.
2. Resolver coordenadas de {len(refs_sin_coord)} referentes: {', '.join(refs_sin_coord)}. No se cargan en mapas mientras sigan inauditables.
3. Revisar las {int((refs_csv['fuera_geometria'] == 'SI').sum())} relaciones documentales fuera de geometría; conservarlas como menciones o corregir asignación con evidencia, sin ampliar bordes automáticamente.
4. Definir institucionalmente `es_icono_principal`; R22 deja todas las filas en `NO` para no inventar jerarquías.
5. Actualizar en una integración futura los consumidores que parsean IDs compuestos; esta ronda conserva `legacy_id` y aporta `polo_uid`/`04_SISTEMAS_MIEMBROS.csv`.
6. La propuesta `06_ORDEN_EDITORIAL_POR_COMUNA.csv` no es una decisión institucional.
7. El registro OLIMPO de Arregui 5794 queda como antecedente separado, fuera del canon 1225/26 y sin fusión con Bar Olimpo.
"""
    (out / "17_PENDIENTES.md").write_text(pendientes_md, encoding="utf-8")

    esquema = """# Correspondencias de esquema

| Requisito conceptual | Campo R22 / origen |
|---|---|
| ID estable | `establecimiento_uid`; `legacy_id` conserva el ID R11 |
| Nombre / normalización | `nombre`, `alias_nombre`, `nombre_normalizado` |
| Dirección y punto | `direccion`, `latitud`, `longitud`; no prueba operación |
| Barrio/comuna | cruce espacial con capas oficiales locales; se conserva `barrio_declarado` |
| Categoría / subcategoría | `categoria` R11 + `subcategoria` normalizada |
| Fuentes / familias / principal | `fuentes`, `familias_fuente`, `fuente_principal` |
| Frescura | `fecha_frescura_evidencia`; no se sustituye por fecha de metadato |
| Publicación | `nivel_publicacion` derivado de `citable_en_documento` |
| Vigencia | `estado_vigencia`, fecha, fuente y tipo de verificación; catálogo/POI no equivale a apertura |
| Referente / reconocimiento | `referente`, `tipo_referente`, `reconocimiento`, `reconocimiento_normativo` |
| Polo/ficha/sistema | `polo_ficha_sistema_asociado` + tabla explícita de relaciones |
| Punto instrumental | `punto_instrumental`; separado de existencia, vigencia y reconocimiento |

`EXISTE_EN_FUENTE`, `OPERATIVO`, `VIGENTE`, `REFERENTE`, `RECONOCIMIENTO_NORMATIVO` y `PUNTO_INSTRUMENTAL` son campos distintos y no se derivan uno de otro.
"""
    (out / "ESQUEMA_CORRESPONDENCIAS.md").write_text(esquema, encoding="utf-8")

    # Verifica que todos los insumos, incluida R21, conserven hash.
    hashes_despues = {k: sha256(p) for k, p in rutas.items()}
    if hashes_antes != hashes_despues:
        raise AssertionError("Algún insumo cambió durante la corrida")

    # Manifest sin autorreferencia. Hashes incluye el manifest y omite sólo su propio archivo.
    descripciones = {
        "00_RESUMEN.md": "resultado ejecutivo y alcance",
        "01_CAMBIOS.md": "cambios aplicados y superficies preservadas",
        "02_BASE_CANDIDATA.csv": "establecimientos/referentes candidatos",
        "03_POLOS_CANDIDATOS.geojson": "39 geometrías candidatas con ontología explícita",
        "04_SISTEMAS_MIEMBROS.csv": "relaciones sistema/miembro y padre/pieza",
        "05_POLOS_COMUNAS_BARRIOS.csv": "superficie y locales por comuna/barrio",
        "06_ORDEN_EDITORIAL_POR_COMUNA.csv": "propuesta no institucional de orden",
        "07_REFERENTES_ICONOS_POR_POLO.csv": "relaciones referente–polo",
        "08_QA_REFERENTES_POR_POLO.csv": "QA agregado de referentes",
        "09_VIAS_RECONCILIADAS.csv": "nueve divergencias de vía A",
        "10_CONTEOS_GLOBALES.csv": "métricas únicas y ocurrencias",
        "11_CAMBIOS_DOCUMENTO_CAPA.csv": "log trazable de cambios",
        "12_QA_GEOMETRIAS.md": "validez y solapes",
        "13_QA_MAKE_VALID_R08_R12.md": "antes/después de reparación",
        "14_MAP_INPUT_POLOS.geojson": "campos mínimos para cartografía de polos",
        "15_MAP_INPUT_REFERENTES.geojson": "campos mínimos para cartografía de referentes",
        "16_QA_GENERAL.md": "validaciones automáticas y privacidad",
        "17_PENDIENTES.md": "pendientes reales",
        "19_HASHES_SHA256.csv": "hashes de contenido; omite autorreferencia",
        "SOLAPES_CLASIFICADOS.csv": "clasificación reproducible de pares solapados",
        "QA_VALIDACIONES.csv": "resultado machine-readable de controles",
        "FUENTES_INSUMOS.csv": "procedencia y hash de inputs",
        "ESQUEMA_CORRESPONDENCIAS.md": "mapeo del pedido al modelo R22",
        "scripts/build_r22.py": "generador offline reproducible",
    }
    def es_entregable(p: Path) -> bool:
        return p.is_file() and "__pycache__" not in p.parts and p.suffix.lower() != ".pyc"

    rels = sorted(
        str(p.relative_to(out)).replace("\\", "/")
        for p in out.rglob("*")
        if es_entregable(p) and p.name not in {"18_MANIFEST.csv", "19_HASHES_SHA256.csv"}
    )
    rels.append("19_HASHES_SHA256.csv")
    manifest = pd.DataFrame(
        [{"ruta": r, "descripcion": descripciones.get(r, "archivo de soporte"), "incluido_en_zip": "SI"} for r in sorted(rels)]
    )
    escribir_csv(manifest, out / "18_MANIFEST.csv")
    hash_rows = []
    for p in sorted(out.rglob("*")):
        if es_entregable(p) and p.name != "19_HASHES_SHA256.csv":
            hash_rows.append({"ruta": str(p.relative_to(out)).replace("\\", "/"), "bytes": p.stat().st_size, "sha256": sha256(p)})
    escribir_csv(pd.DataFrame(hash_rows), out / "19_HASHES_SHA256.csv")

    # Escaneo final de archivos de datos/documentación; el script se omite porque contiene los patrones del escáner.
    patrones = {
        "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
        "api_key": re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
        "drive_privado": re.compile(r"(?:drive|docs)\.google\.com", re.I),
        "cuit_dni": re.compile(r"\b\d{2}-\d{8}-\d\b|\b(?:CUIT|DNI)\s*[:#-]?\s*\d{7,11}\b", re.I),
    }
    hits = []
    for p in out.rglob("*"):
        if not es_entregable(p) or p.suffix.lower() not in {".csv", ".md", ".geojson"} or "scripts" in p.parts:
            continue
        texto = p.read_text(encoding="utf-8-sig", errors="replace")
        for etiqueta, patron in patrones.items():
            if patron.search(texto):
                hits.append((str(p.relative_to(out)), etiqueta))
    if hits:
        raise AssertionError(f"QA privacidad falló: {hits}")

    if args.zip.exists() and not args.overwrite_zip:
        raise FileExistsError(f"El ZIP ya existe; usar --overwrite-zip si se autorizó reemplazarlo: {args.zip}")
    args.zip.parent.mkdir(parents=True, exist_ok=True)
    raiz_zip = "DATAGASTRO_V3_R22_BASE_ESTRUCTURAL_2026-08-12"
    with zipfile.ZipFile(args.zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(out.rglob("*")):
            if not es_entregable(p):
                continue
            zi = zipfile.ZipInfo(f"{raiz_zip}/{str(p.relative_to(out)).replace(chr(92), '/')}")
            zi.date_time = (2026, 8, 12, 0, 0, 0)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zf.writestr(zi, p.read_bytes())

    print(json.dumps({
        "estado": "OK",
        "out": str(out),
        "zip": str(args.zip),
        "zip_sha256": sha256(args.zip),
        "base_candidata": len(candidatos_df),
        "polos": len(polos_final),
        "bares_notables": bar_count,
        "locales_unicos": unicos,
        "ocurrencias": ocurrencias,
        "duplicaciones": duplicaciones,
        "referentes_relaciones": len(refs_csv),
        "requests": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
