from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from pathlib import Path

import pandas as pd


FECHA_CONSULTA = "2026-07-01"

ROOT = Path(__file__).resolve().parents[2]

DOCS_DIR = ROOT / "docs" / "polos_gastro" / "fase8_fuerte"
OUTPUTS_DIR = ROOT / "outputs" / "polos_gastro" / "fase8_fuerte"
TABLAS_DIR = OUTPUTS_DIR / "tablas"
QA_DIR = OUTPUTS_DIR / "qa"

PATHS = {
    "f01_raw": ROOT / "data" / "raw" / "f01_oferta_establecimientos_gastronomicos.csv",
    "f02_fact": ROOT / "data" / "processed" / "fact_habilitacion_gastronomica.csv",
    "dim_ubicacion": ROOT / "data" / "processed" / "dim_ubicacion.csv",
    "analytics_f01_barrio": ROOT
    / "data"
    / "analytics"
    / "analytics_establecimientos_por_categoria_barrio.csv",
    "analytics_f02_barrio": ROOT / "data" / "analytics" / "analytics_habilitaciones_por_barrio.csv",
    "analytics_f02_anio": ROOT / "data" / "analytics" / "analytics_habilitaciones_por_anio.csv",
    "geo_barrios": ROOT / "data" / "raw" / "geo_barrios.geojson",
    "geo_comunas": ROOT / "data" / "raw" / "geo_comunas.geojson",
    "tabla_polos_b2": ROOT
    / "outputs"
    / "polos_gastro"
    / "fase7"
    / "tablas"
    / "tabla_polos_para_informe_borrador_2.csv",
    "tabla_polos_f5": ROOT
    / "outputs"
    / "polos_gastro"
    / "fase5"
    / "polos_gastro_universo_consolidado_fase5.csv",
    "fase8_validacion": ROOT
    / "outputs"
    / "polos_gastro"
    / "fase8"
    / "tablas"
    / "validacion_documental_polos_fase8.csv",
    "fase8_recomendaciones": ROOT
    / "outputs"
    / "polos_gastro"
    / "fase8"
    / "tablas"
    / "recomendaciones_cambio_clasificacion_fase8.csv",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def ensure_dirs() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    TABLAS_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path, *, sep: str = ",", encoding: str | None = None, **kwargs) -> pd.DataFrame:
    encodings = [encoding] if encoding else ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    errors: list[str] = []
    for enc in encodings:
        if enc is None:
            continue
        try:
            return pd.read_csv(path, sep=sep, encoding=enc, low_memory=False, **kwargs)
        except Exception as exc:  # pragma: no cover - diagnostic path
            errors.append(f"{enc}: {type(exc).__name__}")
    raise RuntimeError(f"No se pudo leer {rel(path)}. Intentos: {errors}")


def count_rows(path: Path, encoding: str = "utf-8") -> int | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding=encoding, errors="replace") as fh:
            return max(sum(1 for _ in fh) - 1, 0)
    except Exception:
        return None


def strip_accents(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in value if not unicodedata.combining(ch))


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    fixes = {
        "Ã±": "ñ",
        "Ã¡": "a",
        "Ã©": "e",
        "Ã­": "i",
        "Ã³": "o",
        "Ãº": "u",
        "Â°": "",
    }
    for old, new in fixes.items():
        text = text.replace(old, new)
    text = strip_accents(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def key(value: object) -> str:
    text = clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_barrio(value: object) -> str:
    text = clean_text(value)
    aliases = {
        "Boca": "La Boca",
        "Nuñez": "Nunez",
        "NuÃ±ez": "Nunez",
        "Villa General Mitre": "Villa Gral. Mitre",
    }
    return aliases.get(text, text)


def clean_comuna(value: object) -> str:
    text = clean_text(value)
    if not text:
        return "No determinada"
    match = re.search(r"\b([1-9]|1[0-5])\b", text)
    if match:
        return match.group(1)
    return "No determinada" if "no determinada" in text.lower() else text


def nivel(indice: float | int | None) -> str:
    if indice is None or pd.isna(indice):
        return "no calculable"
    if indice >= 66:
        return "alto"
    if indice >= 33:
        return "medio"
    if indice > 0:
        return "bajo"
    return "sin senal"


def normalize(series: pd.Series) -> pd.Series:
    max_value = series.max()
    if pd.isna(max_value) or max_value == 0:
        return pd.Series([0] * len(series), index=series.index, dtype=float)
    return (series / max_value * 100).round(2)


def inventory_geojson(path: Path) -> tuple[int | None, list[str]]:
    if not path.exists():
        return None, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        features = data.get("features", [])
        columns = sorted({key for feature in features for key in feature.get("properties", {}).keys()})
        return len(features), columns[:12]
    except Exception:
        return None, []


def source_inventory() -> pd.DataFrame:
    records: list[dict[str, object]] = []

    def add_csv(
        path: Path,
        name: str,
        source_type: str,
        *,
        sep: str = ",",
        encoding: str | None = None,
        used: str,
        recommended_use: str,
        limitations: str,
        period: str,
    ) -> None:
        if not path.exists():
            records.append(
                {
                    "fuente_encontrada": name,
                    "ruta_relativa": rel(path),
                    "tipo_fuente": source_type,
                    "filas": "",
                    "columnas_principales": "archivo no encontrado",
                    "fecha_o_periodo": period,
                    "uso_recomendado": recommended_use,
                    "limitaciones": limitations,
                    "usada_en_fase": "NO",
                }
            )
            return
        try:
            df = read_csv(path, sep=sep, encoding=encoding, nrows=0)
            rows = count_rows(path, encoding=encoding or "utf-8")
            columns = "; ".join(list(df.columns)[:14])
        except Exception as exc:
            rows = ""
            columns = f"no legible en inventario rapido: {type(exc).__name__}"
        records.append(
            {
                "fuente_encontrada": name,
                "ruta_relativa": rel(path),
                "tipo_fuente": source_type,
                "filas": rows if rows is not None else "",
                "columnas_principales": columns,
                "fecha_o_periodo": period,
                "uso_recomendado": recommended_use,
                "limitaciones": limitations,
                "usada_en_fase": used,
            }
        )

    add_csv(
        PATHS["f01_raw"],
        "F01 - Oferta y establecimientos gastronomicos",
        "datos abiertos / fuente publica local",
        sep=";",
        encoding="cp1252",
        used="SI",
        recommended_use="Base principal para oferta registrada por barrio y comuna.",
        limitations="Directorio de oferta registrada; no valida vigencia operativa ni habilitacion actual.",
        period="sin fecha de corte explicita en columnas; consulta local 2026-07-01",
    )
    add_csv(
        PATHS["f02_fact"],
        "F02 procesada - Habilitaciones gastronomicas",
        "salida procesada local del pipeline, solo lectura",
        used="SI",
        recommended_use="Base para habilitaciones gastronomicas por comuna.",
        limitations="Mide habilitaciones aprobadas historicas; no locales activos. Barrio no confiable para esta fase.",
        period="2015-2025 segun campo anio_fuente/periodo_fuente",
    )
    add_csv(
        PATHS["dim_ubicacion"],
        "Dimension ubicacion",
        "salida procesada local del pipeline, solo lectura",
        used="SI",
        recommended_use="Apoyo para comuna normalizada de habilitaciones.",
        limitations="El barrio derivado de F02 queda mayormente no determinado; se usa comuna, no barrio.",
        period="derivado local vigente al momento de consulta",
    )
    add_csv(
        PATHS["analytics_f01_barrio"],
        "Analytics establecimientos por categoria y barrio",
        "analytics local, solo lectura",
        used="NO",
        recommended_use="Contraste metodologico, no base principal de esta fase.",
        limitations="Agrega por categoria; para esta fase se reprocesa F01 de forma simple.",
        period="derivado local vigente al momento de consulta",
    )
    add_csv(
        PATHS["analytics_f02_barrio"],
        "Analytics habilitaciones por barrio",
        "analytics local, solo lectura",
        used="NO",
        recommended_use="No usar para lectura barrial de habilitaciones en esta fase.",
        limitations="El campo barrio no aporta desagregacion barrial util; concentra no determinado.",
        period="derivado local vigente al momento de consulta",
    )
    add_csv(
        PATHS["analytics_f02_anio"],
        "Analytics habilitaciones por anio",
        "analytics local, solo lectura",
        used="NO",
        recommended_use="Contraste temporal general.",
        limitations="No reemplaza el agregado comunal construido en esta fase.",
        period="2015-2025",
    )

    for path in sorted((ROOT / "data" / "raw").glob("f02_habilitaciones_aprobadas_*.csv")):
        period = path.stem.replace("f02_habilitaciones_aprobadas_", "")
        add_csv(
            path,
            f"F02 cruda - habilitaciones aprobadas {period}",
            "dato abierto crudo local",
            sep=";",
            used="NO",
            recommended_use="No usar directamente en salidas; usar derivado procesado agregado.",
            limitations="Incluye columnas sensibles o identificatorias; solo lectura e inventario.",
            period=period,
        )

    for path, name in [
        (PATHS["geo_barrios"], "Cartografia barrios CABA"),
        (PATHS["geo_comunas"], "Cartografia comunas CABA"),
    ]:
        rows, columns = inventory_geojson(path)
        records.append(
            {
                "fuente_encontrada": name,
                "ruta_relativa": rel(path),
                "tipo_fuente": "cartografia oficial local, solo lectura",
                "filas": rows if rows is not None else "",
                "columnas_principales": "; ".join(columns),
                "fecha_o_periodo": "sin uso analitico directo en esta fase",
                "uso_recomendado": "Insumo futuro para mapas de contexto, no para delimitar polos.",
                "limitaciones": "No se generaron mapas ni poligonos en esta fase.",
                "usada_en_fase": "NO",
            }
        )

    return pd.DataFrame(records)


def build_f01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    f01 = read_csv(PATHS["f01_raw"], sep=";", encoding="cp1252", dtype=str)
    f01["barrio"] = f01["barrio"].map(clean_barrio)
    f01["comuna"] = f01["comuna"].map(clean_comuna)
    f01["id_conteo"] = f01["id"].fillna("").where(f01["id"].fillna("") != "", f01.index.astype(str))

    barrio = (
        f01.groupby(["barrio", "comuna"], dropna=False)
        .agg(cantidad_oferta_registrada=("id_conteo", "count"))
        .reset_index()
        .sort_values(["cantidad_oferta_registrada", "barrio"], ascending=[False, True])
    )
    barrio["fuente"] = "F01 oferta y establecimientos gastronomicos"
    barrio["universo"] = "oferta registrada en fuente local"
    barrio["nota_metodologica"] = (
        "Cuenta registros de oferta; no mide locales activos ni habilitaciones vigentes."
    )

    comuna = (
        f01.groupby(["comuna"], dropna=False)
        .agg(cantidad_oferta_registrada=("id_conteo", "count"))
        .reset_index()
        .sort_values(["comuna"], key=lambda s: s.map(lambda x: int(x) if str(x).isdigit() else 99))
    )
    comuna["fuente"] = "F01 oferta y establecimientos gastronomicos"
    comuna["universo"] = "oferta registrada en fuente local"
    comuna["nota_metodologica"] = (
        "Cuenta registros de oferta; no mide locales activos ni habilitaciones vigentes."
    )
    return f01, barrio, comuna


def build_f02() -> tuple[pd.DataFrame, pd.DataFrame]:
    fact = read_csv(PATHS["f02_fact"], encoding="utf-8-sig", dtype=str)
    dim = read_csv(PATHS["dim_ubicacion"], encoding="utf-8-sig", dtype=str)
    merged = fact.merge(
        dim[["id_ubicacion", "comuna", "barrio", "calidad_geo"]],
        on="id_ubicacion",
        how="left",
        suffixes=("_fact", "_dim"),
    )
    merged["comuna_contexto"] = merged["comuna_dim"].map(clean_comuna)
    merged["barrio_contexto"] = merged["barrio_dim"].map(clean_barrio)
    merged["anio_num"] = merged["anio_fuente"].map(lambda x: int(x) if str(x).isdigit() else None)
    merged["en_ultimos_5_anios_fuente"] = merged["anio_num"].map(lambda x: bool(x and 2021 <= x <= 2025))
    merged["en_ultimos_10_anios_aprox"] = True

    comuna = (
        merged.groupby("comuna_contexto", dropna=False)
        .agg(
            cantidad_habilitaciones_gastronomicas=("id_habilitacion", "count"),
            cantidad_ultimos_5_anios_fuente_2021_2025=("en_ultimos_5_anios_fuente", "sum"),
            cantidad_ultimos_10_anios_aprox_2015_2025=("en_ultimos_10_anios_aprox", "sum"),
        )
        .reset_index()
        .rename(columns={"comuna_contexto": "comuna"})
        .sort_values(["comuna"], key=lambda s: s.map(lambda x: int(x) if str(x).isdigit() else 99))
    )
    comuna["fuente"] = "F02 habilitaciones gastronomicas procesadas"
    comuna["universo"] = "habilitaciones aprobadas historicas clasificadas como gastronomicas"
    comuna["nota_metodologica"] = (
        "Cuenta habilitaciones aprobadas, no locales activos. El corte de 10 anios es aproximado por bloque 2015-2018."
    )
    return merged, comuna


def build_indices(
    oferta_barrio: pd.DataFrame,
    oferta_comuna: pd.DataFrame,
    habil_comuna: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    idx_barrio = oferta_barrio[["barrio", "comuna", "cantidad_oferta_registrada"]].copy()
    idx_barrio["indice_senal_objetiva"] = normalize(idx_barrio["cantidad_oferta_registrada"])
    idx_barrio["nivel_senal_objetiva"] = idx_barrio["indice_senal_objetiva"].map(nivel)
    idx_barrio["fuentes_usadas"] = "F01 oferta registrada"
    idx_barrio["nota_metodologica"] = (
        "Indice interno relativo dentro de F01. No es ranking, densidad real ni delimitacion de polo."
    )
    idx_barrio = idx_barrio.sort_values(
        ["comuna", "barrio"], key=lambda s: s.map(lambda x: int(x) if str(x).isdigit() else x)
    )

    f01c = oferta_comuna[["comuna", "cantidad_oferta_registrada"]].copy()
    f02c = habil_comuna[habil_comuna["comuna"].astype(str).str.match(r"^\d+$")][
        ["comuna", "cantidad_habilitaciones_gastronomicas"]
    ].copy()
    idx_comuna = f01c.merge(f02c, on="comuna", how="outer").fillna(0)
    idx_comuna["cantidad_oferta_registrada"] = idx_comuna["cantidad_oferta_registrada"].astype(int)
    idx_comuna["cantidad_habilitaciones_gastronomicas"] = idx_comuna[
        "cantidad_habilitaciones_gastronomicas"
    ].astype(int)
    idx_comuna["indice_oferta_registrada"] = normalize(idx_comuna["cantidad_oferta_registrada"])
    idx_comuna["indice_habilitaciones"] = normalize(idx_comuna["cantidad_habilitaciones_gastronomicas"])
    idx_comuna["indice_senal_objetiva"] = (
        (idx_comuna["indice_oferta_registrada"] + idx_comuna["indice_habilitaciones"]) / 2
    ).round(2)
    idx_comuna["nivel_senal_objetiva"] = idx_comuna["indice_senal_objetiva"].map(nivel)
    idx_comuna["fuentes_usadas"] = "F01 oferta registrada + F02 habilitaciones historicas"
    idx_comuna["nota_metodologica"] = (
        "Indice interno relativo por comuna. No es ranking, no mide locales activos y no delimita polos."
    )
    idx_comuna = idx_comuna.sort_values(
        "comuna", key=lambda s: s.map(lambda x: int(x) if str(x).isdigit() else 99)
    )
    return idx_barrio, idx_comuna


def barrios_from_text(text: str) -> list[str]:
    if not text or pd.isna(text):
        return []
    text = clean_text(text)
    parts = re.split(r";|,|/|\(|\)", text)
    out: list[str] = []
    for part in parts:
        part = clean_barrio(part.replace("entorno Ciudad Universitaria", "").strip())
        if not part or "aproximacion" in part.lower() or "segun tramo" in part.lower():
            continue
        if part.lower() in {"borde belgrano r", "borde", "comuna", "comunas"}:
            continue
        out.append(part)
    return out


def comunas_from_text(text: str) -> list[str]:
    if not text or pd.isna(text):
        return []
    return sorted(set(re.findall(r"\b([1-9]|1[0-5])\b", str(text))), key=lambda x: int(x))


def average_index(names: list[str], idx_barrio: pd.DataFrame) -> float | None:
    if not names:
        return None
    mapping = {key(row["barrio"]): row["indice_senal_objetiva"] for _, row in idx_barrio.iterrows()}
    aliases = {
        "la paternal": "paternal",
        "nunez": "nunez",
        "nunez belgrano entorno ciudad universitaria": "nunez",
    }
    values: list[float] = []
    for name in names:
        k = aliases.get(key(name), key(name))
        if k in mapping:
            values.append(float(mapping[k]))
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def first_available_barrio(names: list[str], idx_barrio: pd.DataFrame) -> str:
    mapping = {key(row["barrio"]): row["barrio"] for _, row in idx_barrio.iterrows()}
    aliases = {"la paternal": "paternal"}
    for name in names:
        k = aliases.get(key(name), key(name))
        if k in mapping:
            return mapping[k]
    return "; ".join(names)


def build_polos_cross(idx_barrio: pd.DataFrame, idx_comuna: pd.DataFrame) -> pd.DataFrame:
    f7 = read_csv(PATHS["tabla_polos_b2"], encoding="utf-8-sig", dtype=str)
    f5 = read_csv(PATHS["tabla_polos_f5"], encoding="utf-8-sig", dtype=str)
    f5["join_key"] = f5["nombre_polo"].map(key)
    f7["join_key"] = f7["polo"].map(key)
    merged = f7.merge(
        f5[["join_key", "barrios_relacionados", "comunas_relacionadas"]],
        on="join_key",
        how="left",
    )

    rows: list[dict[str, object]] = []
    for _, row in merged.iterrows():
        polo = row["polo"]
        nk = key(polo)
        tipo = key(row["tipo_territorial"])
        barrios = barrios_from_text(row.get("barrios_relacionados", ""))
        comunas = comunas_from_text(row.get("comunas_relacionadas", ""))
        indice: float | None = None
        referencia = "; ".join(barrios) if barrios else "; ".join(f"Comuna {c}" for c in comunas)
        tipo_cruce = "aproximado por barrio de referencia"
        senal = "si - parcial"
        limitacion = "La capa objetiva se interpreta como contexto territorial, no como delimitacion del polo."
        recomendacion = "Usar solo como contexto en revision humana."
        usar = "SI"

        no_calc = {
            "avenida corrientes": "Corredor cultural-gastronomico sin tramo operativo cerrado.",
            "avenida caseros barracas": "Corredor con solapamiento San Telmo/Barracas; requiere recorte territorial.",
            "costanera norte": "Corredor costero multibarrial; no se debe asignar a un barrio unico.",
            "doho donado holmberg": "Corredor entre Villa Urquiza y Belgrano R; requiere delimitacion fina.",
            "avenida boedo": "Corredor sin delimitacion operativa; el barrio Boedo no valida el eje.",
            "federico lacroze libertador a cabildo": "Corredor sin delimitacion operativa ni evidencia suficiente.",
            "villa pueyrredon av san martin": "Corredor propuesto; el barrio completo no valida Avenida San Martin.",
        }
        special_partial = {
            "palermo soho": "Palermo como barrio aproxima el area nucleo, no el subpolo Soho.",
            "palermo hollywood": "Palermo como barrio aproxima el area nucleo, no el subpolo Hollywood.",
            "las canitas": "Palermo como barrio aproxima el area nucleo, no Las Canitas como subpolo.",
            "barrio chino": "Belgrano como barrio no valida Barrio Chino como subpolo.",
            "bajo belgrano": "Belgrano como barrio no valida Bajo Belgrano como subzona.",
            "belgrano r": "Belgrano como barrio no valida Belgrano R como subzona independiente.",
            "nuevo bajo en retiro esmeralda y paraguay": "Retiro como barrio no valida el subpolo Esmeralda-Paraguay.",
            "parque saavedra garcia del rio": "Saavedra como barrio no valida el eje Garcia del Rio.",
            "paternal": "Paternal como barrio aporta contexto; no valida el corredor gastronomico.",
            "abasto": "Balvanera como barrio no separa Abasto de Corrientes.",
        }

        if nk in no_calc:
            tipo_cruce = "no calculable por corredor/subpolo sin delimitacion"
            senal = "no calculable"
            indice = None
            limitacion = no_calc[nk]
            recomendacion = "No usar para sostener cambios de clasificacion sin delimitacion humana previa."
            usar = "NO"
        elif nk in special_partial:
            if nk.startswith("palermo") or nk == "las canitas":
                barrios = ["Palermo"]
                referencia = "Palermo"
            elif nk in {"barrio chino", "bajo belgrano", "belgrano r"}:
                barrios = ["Belgrano"]
                referencia = "Belgrano"
            elif nk == "nuevo bajo en retiro esmeralda y paraguay":
                barrios = ["Retiro"]
                referencia = "Retiro"
            elif nk == "parque saavedra garcia del rio":
                barrios = ["Saavedra"]
                referencia = "Saavedra"
            elif nk == "paternal":
                barrios = ["Paternal"]
                referencia = "Paternal"
            elif nk == "abasto":
                barrios = ["Balvanera"]
                referencia = "Balvanera"
            indice = average_index(barrios, idx_barrio)
            tipo_cruce = "aproximado por barrio de referencia"
            limitacion = special_partial[nk]
            recomendacion = "Usar en Borrador 3 solo como advertencia contextual, no como validacion del subpolo."
            usar = "SI"
        elif tipo == "barrio" and len(barrios) == 1:
            referencia = first_available_barrio(barrios, idx_barrio)
            indice = average_index(barrios, idx_barrio)
            tipo_cruce = "directo por barrio"
            senal = "si"
            limitacion = "El cruce coincide con barrio de referencia, pero no mide vigencia operativa."
            recomendacion = "Puede citarse como contexto barrial agregado."
            usar = "SI"
        elif nk == "microcentro centro":
            barrios = ["San Nicolas", "Monserrat", "Retiro"]
            referencia = "San Nicolas; Monserrat; Retiro"
            indice = average_index(barrios, idx_barrio)
            tipo_cruce = "aproximado por barrio de referencia"
            limitacion = "Area central multibarrial; el promedio no delimita Microcentro."
            recomendacion = "Usar solo como contexto multibarrial."
            usar = "SI"
        elif len(barrios) == 1:
            referencia = first_available_barrio(barrios, idx_barrio)
            indice = average_index(barrios, idx_barrio)
            tipo_cruce = "aproximado por barrio de referencia"
            limitacion = "El barrio de referencia no equivale al poligono del polo."
            recomendacion = "Usar solo como contexto agregado."
            usar = "SI"
        elif comunas:
            comuna_map = {str(row["comuna"]): row["indice_senal_objetiva"] for _, row in idx_comuna.iterrows()}
            values = [float(comuna_map[c]) for c in comunas if c in comuna_map]
            indice = round(sum(values) / len(values), 2) if values else None
            referencia = "; ".join(f"Comuna {c}" for c in comunas)
            tipo_cruce = "aproximado por comuna"
            limitacion = "La comuna es mas amplia que el polo y puede incluir zonas no vinculadas."
            recomendacion = "Usar solo como contexto comunal agregado."
            usar = "SI"

        lectura = (
            "La senal objetiva acompana la lectura documental."
            if indice is not None and indice >= 66
            else "La fuente disponible muestra presencia territorial, pero no confirma densidad del polo."
            if indice is not None and indice > 0
            else "El cruce no es recomendable sin delimitacion territorial previa."
        )

        rows.append(
            {
                "polo": polo,
                "grupo_borrador_2": row["grupo_actualizado"],
                "tipo_territorial": row["tipo_territorial"],
                "estado_documental": row["estado_documentacion"],
                "barrio_o_comuna_de_referencia": referencia,
                "tipo_cruce": tipo_cruce,
                "senal_objetiva_disponible": senal,
                "indice_senal_objetiva": "" if indice is None else indice,
                "nivel_senal_objetiva": nivel(indice),
                "lectura_prudente": lectura,
                "limitacion_territorial": limitacion,
                "recomendacion_metodologica": recomendacion,
                "usar_en_borrador_3_si_no": usar,
                "observaciones": "No aplicar cambios de clasificacion automaticamente.",
            }
        )

    return pd.DataFrame(rows)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8-sig")


def md_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    if df.empty:
        return "_Sin registros._"
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("\n", " ").replace("|", "/") for col in cols]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def docs_inventory(inventory: pd.DataFrame) -> None:
    cols = [
        "fuente_encontrada",
        "ruta_relativa",
        "tipo_fuente",
        "filas",
        "columnas_principales",
        "fecha_o_periodo",
        "uso_recomendado",
        "limitaciones",
        "usada_en_fase",
    ]
    write_text(
        DOCS_DIR / "INVENTARIO_FUENTES_CAPA_OBJETIVA.md",
        f"""
# Inventario de fuentes - Capa objetiva Fase 8 fuerte

Fecha de consulta: {FECHA_CONSULTA}.

Este inventario registra fuentes locales disponibles para construir una capa objetiva de contexto
territorial de PolosGastro. No se modificaron datos fuente y no se descargaron archivos nuevos.
Las rutas se informan en forma relativa al repositorio.

{md_table(inventory[cols])}

## Lectura metodologica

- La fuente F01 se usa para oferta gastronomica registrada por barrio y comuna.
- La fuente F02 procesada se usa para habilitaciones gastronomicas por comuna.
- No se usa F02 cruda en salidas porque contiene columnas identificatorias o sensibles.
- No se usa una tabla barrial de habilitaciones porque el campo barrio procesado no aporta
  cobertura suficiente para una lectura territorial robusta.
- La cartografia local queda como insumo futuro; en esta fase no se generan mapas ni poligonos.
""",
    )


def docs_fuentes_insuficientes(f02_rows: int, f02_no_barrio: int) -> None:
    write_text(
        DOCS_DIR / "FUENTES_INSUFICIENTES_CAPA_OBJETIVA.md",
        f"""
# Fuentes insuficientes para capa objetiva barrial

Fecha de consulta: {FECHA_CONSULTA}.

La Fase 8 fuerte pudo construir oferta gastronomica por barrio a partir de F01, pero no una tabla
confiable de habilitaciones gastronomicas por barrio.

## Caso principal

- Fuente evaluada: `data/processed/fact_habilitacion_gastronomica.csv` junto con
  `data/processed/dim_ubicacion.csv`.
- Registros de habilitaciones leidos: {f02_rows}.
- Registros con barrio no determinado o no util para lectura barrial: {f02_no_barrio}.

## Decision

No se crea `habilitaciones_gastronomicas_por_barrio_fase8_fuerte.csv` porque podria sugerir una
precision territorial que la fuente procesada no sostiene. La lectura de F02 queda limitada a
comuna.

## Impacto

- El indice por barrio usa solo F01.
- El indice por comuna combina F01 y F02.
- Los cruces de polos de tipo corredor, subpolo o area de revision siguen requiriendo delimitacion
  humana antes de cualquier comparacion cuantitativa fina.
""",
    )


def docs_methodology(
    f01_rows: int,
    f02_rows: int,
    f02_no_barrio: int,
    no_determinada_f02: int,
) -> None:
    write_text(
        DOCS_DIR / "METODOLOGIA_CAPA_OBJETIVA_FASE_8_FUERTE.md",
        f"""
# Metodologia - Capa objetiva Fase 8 fuerte

Fecha de consulta: {FECHA_CONSULTA}.

## Objetivo

Construir una capa objetiva de contexto territorial para contrastar la lectura documental de
PolosGastro con datos abiertos u oficiales disponibles localmente. La capa es un insumo tecnico:
no es ranking, no delimita polos y no modifica clasificaciones.

## Fuentes usadas

- F01 - `data/raw/f01_oferta_establecimientos_gastronomicos.csv`: {f01_rows} registros de oferta
  gastronomica registrada.
- F02 procesada - `data/processed/fact_habilitacion_gastronomica.csv`: {f02_rows} habilitaciones
  gastronomicas historicas.
- `data/processed/dim_ubicacion.csv`: apoyo para comuna normalizada de F02.
- `outputs/polos_gastro/fase7/tablas/tabla_polos_para_informe_borrador_2.csv`: universo de 32
  registros territoriales de Borrador 2, solo lectura.
- `outputs/polos_gastro/fase5/polos_gastro_universo_consolidado_fase5.csv`: barrios y comunas de
  referencia, solo lectura.

No hubo descargas nuevas.

## Campos usados

F01:

- `barrio`
- `comuna`
- `id`
- `categoria`

F02 procesada:

- `id_habilitacion`
- `id_ubicacion`
- `anio_fuente`
- `fecha_habilitacion`
- `categoria_gastronomica_inferida`

Dimension ubicacion:

- `id_ubicacion`
- `comuna`
- `barrio`
- `calidad_geo`

## Agregacion

- Oferta registrada por barrio: conteo de registros F01 por `barrio` y `comuna`.
- Oferta registrada por comuna: conteo de registros F01 por `comuna`.
- Habilitaciones por comuna: conteo de registros F02 por comuna normalizada desde
  `dim_ubicacion`.
- Habilitaciones por barrio: no se calcula. En F02, {f02_no_barrio} registros quedan sin barrio
  util o determinado, por lo que la lectura barrial no es robusta.
- Habilitaciones sin comuna determinada luego del cruce: {no_determinada_f02} registros.

## Cortes temporales

F02 permite una lectura aproximada por `anio_fuente`. Se calcula:

- total historico disponible 2015-2025;
- ultimos 5 anios de fuente, aproximados como 2021-2025;
- ultimos 10 anios, solo como aproximacion 2015-2025 porque el bloque 2015-2018 no puede
  separarse con precision uniforme.

## Indice de senal objetiva

El `indice_senal_objetiva` es un indicador interno de 0 a 100.

- Por barrio: normaliza la cantidad de oferta registrada F01 contra el maximo barrial observado.
- Por comuna: promedia dos senales normalizadas, F01 oferta registrada y F02 habilitaciones
  historicas.

El indice significa presencia relativa en las fuentes disponibles. No significa densidad real,
vigencia operativa, calidad gastronomica, importancia institucional ni delimitacion oficial.

## Limites

- F01 es una fuente de oferta registrada; no prueba que los establecimientos sigan abiertos.
- F02 mide habilitaciones aprobadas historicas; no equivale a locales activos.
- La lectura por comuna es mas estable pero menos precisa para corredores y subpolos.
- La lectura por barrio no resuelve calles, ejes ni bordes.
- Los corredores requieren una delimitacion territorial previa para evitar comparaciones falsas.
- Palermo, Belgrano, Corrientes, Abasto, DoHo, Costanera Norte, Avenida Caseros y Federico Lacroze
  requieren tratamiento especial por subpolos, solapamientos o recorridos.
- No se usa Google Places porque la fase debe basarse en fuentes abiertas/oficiales locales y no
  en APIs privadas o datos crudos de plataformas.
- No se generan delimitaciones oficiales porque la capa es solo contexto.
""",
    )


def docs_comparative(polos_cross: pd.DataFrame) -> None:
    high = polos_cross[
        (polos_cross["estado_documental"].isin(["fuerte", "media"]))
        & (polos_cross["nivel_senal_objetiva"].isin(["alto"]))
    ][["polo", "estado_documental", "nivel_senal_objetiva", "lectura_prudente"]]
    non_conclusive = polos_cross[
        (polos_cross["estado_documental"].isin(["fuerte", "media"]))
        & (~polos_cross["nivel_senal_objetiva"].isin(["alto"]))
    ][["polo", "estado_documental", "nivel_senal_objetiva", "limitacion_territorial"]]
    weak_high = polos_cross[
        (polos_cross["estado_documental"].isin(["debil", "pendiente"]))
        & (polos_cross["nivel_senal_objetiva"].isin(["alto", "medio"]))
    ][["polo", "estado_documental", "nivel_senal_objetiva", "limitacion_territorial"]]
    no_calc = polos_cross[polos_cross["nivel_senal_objetiva"].eq("no calculable")][
        ["polo", "tipo_territorial", "limitacion_territorial"]
    ]
    write_text(
        DOCS_DIR / "LECTURA_COMPARADA_EVIDENCIA_DOCUMENTAL_Y_CAPA_OBJETIVA.md",
        f"""
# Lectura comparada - evidencia documental y capa objetiva

Fecha de consulta: {FECHA_CONSULTA}.

La lectura comparada cruza la clasificacion documental del Borrador 2 con una senal objetiva de
contexto territorial. El resultado no es ranking y no aplica cambios de clasificacion.

## Evidencia documental fuerte/media con senal objetiva alta

{md_table(high)}

Lectura prudente: en estos casos, la senal objetiva acompana la lectura documental en el barrio o
comuna de referencia. No valida limites internos ni vigencia de locales.

## Evidencia documental fuerte/media con senal objetiva no concluyente

{md_table(non_conclusive)}

Lectura prudente: la fuente disponible muestra presencia gastronomica en el barrio o comuna de
referencia, pero no alcanza para validar subpolos, corredores o recortes finos.

## Evidencia documental debil/pendiente con senal objetiva de barrio o comuna media/alta

{md_table(weak_high)}

Lectura prudente: una senal objetiva alta del barrio no convierte automaticamente al caso en polo.
Puede indicar que conviene revisar el caso, no que deba subir de categoria.

## Casos no calculables por delimitacion territorial

{md_table(no_calc)}

## Advertencia

Esta capa no debe usarse como ranking publico ni como prueba de densidad real. Sirve para ubicar
barrios y comunas con mayor presencia relativa en las fuentes disponibles, y para ordenar la
revision humana de Borrador 3.
""",
    )


def docs_recommendations() -> None:
    write_text(
        DOCS_DIR / "RECOMENDACIONES_BORRADOR_3_CON_CAPA_OBJETIVA.md",
        f"""
# Recomendaciones para Borrador 3 con capa objetiva

Fecha de consulta: {FECHA_CONSULTA}.

## Que podria incorporarse

- Una nota metodologica que explique que Fase 8 fuerte agrega contexto territorial por barrio y
  comuna.
- Una tabla de oferta registrada por barrio como insumo de contexto, no como ranking de polos.
- Una tabla de indice de senal objetiva por barrio o comuna en anexo tecnico.
- Una lectura prudente para casos donde la senal objetiva acompana la evidencia documental.
- Una advertencia especifica para corredores y subpolos sin delimitacion.

## Que no conviene incorporar

- Ranking de polos.
- Afirmaciones sobre el mejor polo o el polo mas importante.
- Delimitaciones oficiales.
- Conteos de locales activos.
- Mapas de poligonos de polos.
- Cambios automaticos de clasificacion.

## Casos que requieren validacion humana

- Palermo: mantener lectura de area nucleo con subpolos; no convertir Palermo barrio en poligono
  de Soho, Hollywood o Las Canitas.
- Belgrano: separar Barrio Chino, Bajo Belgrano y Belgrano R.
- Avenida Corrientes y Abasto: revisar solapamiento narrativo y territorial.
- Avenida Caseros / Barracas: definir si corresponde a San Telmo, Barracas o borde Caseros.
- DoHo / Donado-Holmberg: definir recorte entre Villa Urquiza y Belgrano R.
- Costanera Norte: tratar como corredor costero, no como barrio.
- Federico Lacroze, Avenida Boedo, Parque Saavedra / Garcia del Rio, Paternal y Villa
  Pueyrredon / Avenida San Martin: no usar barrio completo como prueba del eje.

## Como mencionar la capa objetiva

Formula sugerida:

> La capa objetiva de Fase 8 fuerte aporta una lectura de contexto por barrio y comuna sobre
> oferta registrada e habilitaciones historicas. No mide locales activos, no valida corredores y no
> delimita oficialmente polos gastronomicos.

## Ubicacion sugerida de tablas

- Cuerpo del Borrador 3: una sintesis metodologica y, como maximo, una tabla compacta de lectura
  comparada.
- Anexo tecnico: tablas de oferta por barrio/comuna, habilitaciones por comuna, indices y cruce
  PolosGastro.
- Mapas futuros: solo mapas de contexto por barrio/comuna, con advertencia visible.

## Mapas que no conviene hacer todavia

- Poligonos oficiales de polos.
- Mapas de ranking de polos.
- Mapas de corredores sin tramo definido.
- Mapas que mezclen subpolos de Belgrano o Palermo sin aclaracion.
""",
    )


def docs_map_notes() -> None:
    write_text(
        DOCS_DIR / "NOTAS_MAPA_CONTEXTO_OBJETIVO_FUTURO.md",
        f"""
# Notas para mapa de contexto objetivo futuro

Fecha de consulta: {FECHA_CONSULTA}.

El archivo `outputs/polos_gastro/fase8_fuerte/tablas/insumo_mapa_contexto_objetivo_fase8_fuerte.csv`
es un insumo tabular. No es un mapa final.

## Uso posible

- Mapa coropletico de contexto por barrio o comuna.
- Capa de referencia para observar oferta registrada y habilitaciones historicas.
- Complemento visual para la lectura documental de polos.

## Limites

- No delimita polos.
- No valida corredores.
- No muestra locales activos.
- No reemplaza revision humana.
- No debe usarse para ranking publico.

## Recomendacion de visualizacion futura

Si se generan mapas mas adelante, conviene combinar:

- contexto por barrio/comuna;
- puntos o halos conceptuales de polos, sin poligonos oficiales;
- notas visibles de fuente y limite metodologico;
- separacion explicita de Palermo, Belgrano, Corrientes/Abasto y corredores sin delimitacion.
""",
    )


def docs_closing(
    f01_rows: int,
    f02_rows: int,
    oferta_barrios: int,
    oferta_comunas: int,
    habil_comunas: int,
) -> None:
    write_text(
        DOCS_DIR / "CIERRE_FASE_8_FUERTE_CAPA_OBJETIVA.md",
        f"""
# Cierre Fase 8 fuerte - Capa objetiva de contexto

Fecha de consulta: {FECHA_CONSULTA}.

## Que se hizo

Se construyo una capa objetiva de contexto territorial para PolosGastro a partir de fuentes locales
abiertas/oficiales y salidas procesadas existentes. La fase produce insumos tecnicos para revision
humana futura o Borrador 3.

## Fuentes usadas

- F01 oferta y establecimientos gastronomicos: {f01_rows} registros.
- F02 habilitaciones gastronomicas procesadas: {f02_rows} registros.
- Dimension local de ubicacion para apoyo comunal.
- Tabla de polos Borrador 2, solo lectura.
- Universo consolidado Fase 5, solo lectura.

No hubo descargas nuevas.

## Tablas creadas

- `outputs/polos_gastro/fase8_fuerte/tablas/oferta_gastronomica_por_barrio_fase8_fuerte.csv`
  ({oferta_barrios} barrios).
- `outputs/polos_gastro/fase8_fuerte/tablas/oferta_gastronomica_por_comuna_fase8_fuerte.csv`
  ({oferta_comunas} comunas).
- `outputs/polos_gastro/fase8_fuerte/tablas/habilitaciones_gastronomicas_por_comuna_fase8_fuerte.csv`
  ({habil_comunas} comunas o categorias de comuna).
- `outputs/polos_gastro/fase8_fuerte/tablas/indice_senal_objetiva_por_barrio_fase8_fuerte.csv`.
- `outputs/polos_gastro/fase8_fuerte/tablas/indice_senal_objetiva_por_comuna_fase8_fuerte.csv`.
- `outputs/polos_gastro/fase8_fuerte/tablas/polos_vs_capa_objetiva_fase8_fuerte.csv`.
- `outputs/polos_gastro/fase8_fuerte/tablas/insumo_mapa_contexto_objetivo_fase8_fuerte.csv`.

## Principales hallazgos

- F01 permite una lectura barrial de oferta registrada.
- F02 permite una lectura comunal de habilitaciones gastronomicas historicas.
- La lectura barrial de F02 no es suficiente para esta fase.
- Los barrios con senal objetiva alta tienden a coincidir con areas ya relevantes en la lectura
  documental, pero eso no valida subpolos ni corredores.
- Casos como Corrientes, Abasto, Caseros, DoHo, Costanera Norte y Federico Lacroze requieren
  delimitacion territorial antes de cruzarse con datos cuantitativos finos.

## Limitaciones

- La capa no mide locales activos.
- La capa no mide densidad real.
- La capa no valida vigencia operativa.
- La capa no cierra delimitaciones oficiales.
- La capa no modifica clasificaciones.
- El indice es interno y relativo a fuentes disponibles.

## Que no se hizo

- No se modifico Borrador 2.
- No se modificaron tablas de Fase 7.
- No se modifico la validacion de Fase 8 liviana.
- No se tocaron datos fuente.
- No se uso Google Places.
- No se generaron PDF, DOCX, mapas, graficos ni dashboards.
- No se hizo commit, push ni staging.

## Como usar la capa

Usarla como contexto para Borrador 3, idealmente en anexo tecnico y con advertencias visibles.
No usarla como veredicto, ranking ni delimitacion oficial.

## Proximos pasos recomendados

- Revision humana del cruce `polos_vs_capa_objetiva_fase8_fuerte.csv`.
- Definir delimitaciones preliminares solo textuales para corredores prioritarios.
- Decidir que tablas pueden entrar al Borrador 3 y cuales deben quedar en anexo.
- Si se hacen mapas futuros, producir solo mapas de contexto, no poligonos oficiales.
""",
    )


def docs_qa(
    f01_rows: int,
    f02_rows: int,
    processed_rows: dict[str, int],
    privacy_results: pd.DataFrame,
) -> None:
    hit_count = int(privacy_results["hit"].sum()) if not privacy_results.empty else 0
    write_text(
        DOCS_DIR / "QA_CAPA_OBJETIVA_FASE_8_FUERTE.md",
        f"""
# QA - Capa objetiva Fase 8 fuerte

Fecha de consulta: {FECHA_CONSULTA}.

## Fuentes usadas

- F01 oferta y establecimientos gastronomicos: {f01_rows} filas leidas.
- F02 habilitaciones gastronomicas procesadas: {f02_rows} filas leidas.
- Dimension ubicacion: apoyo para comuna de F02.
- Borrador 2 y universo Fase 5: solo lectura para cruce metodologico.

## Filas procesadas

{md_table(pd.DataFrame([{"archivo": k, "filas": v} for k, v in processed_rows.items()]))}

## Privacidad

Se generaron solo agregados por barrio/comuna y tablas metodologicas. No se exportaron nombres de
establecimientos, direcciones individuales, telefonos, correos, identificadores fiscales/personales
ni identificadores tecnicos de plataformas privadas.

Archivo de QA automatico:

- `outputs/polos_gastro/fase8_fuerte/qa/qa_privacidad_fase8_fuerte.csv`

Resultado automatico: {hit_count} alertas.

## Confirmaciones

- [x] No se uso Google Places.
- [x] No se llamaron APIs privadas.
- [x] No se tocaron datos fuente.
- [x] No se modifico `data/`.
- [x] No se modifico Borrador 2.
- [x] No se modificaron tablas de Fase 7.
- [x] No se modifico la validacion de Fase 8 liviana.
- [x] No se genero PDF.
- [x] No se genero DOCX.
- [x] No se generaron mapas.
- [x] No se generaron graficos.
- [x] No se generaron dashboards.
- [x] No hubo commit, push ni staging.

## Nota

La ausencia de alertas automaticas no reemplaza revision humana antes de publicar. Esta fase queda
como insumo interno.
""",
    )


def scan_privacy(paths: list[Path]) -> pd.DataFrame:
    google_private_identifier = "place" + "_id"
    patterns = {
        "at_symbol": re.compile(r"@"),
        "email": re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
        "telefono_arg": re.compile(
            r"\b(?!20\d{2}[-\s]20\d{2})(?:\+?54\s*)?(?:11\s*)?\d{4}[-\s]?\d{4}\b"
        ),
        "identificador_fiscal_numerico": re.compile(r"\b\d{2}-\d{8}-\d\b"),
        "dni_numerico": re.compile(r"\b\d{7,8}\b"),
        "google_api_key": re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
        "google_private_identifier": re.compile(re.escape(google_private_identifier), re.I),
        "drive_docs": re.compile(r"drive\.google\.com|docs\.google\.com", re.I),
    }
    records: list[dict[str, object]] = []
    for path in paths:
        if path.suffix.lower() not in {".md", ".csv", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except Exception:
            text = ""
        for label, pattern in patterns.items():
            records.append(
                {
                    "archivo": rel(path),
                    "chequeo": label,
                    "hit": bool(pattern.search(text)),
                }
            )
    return pd.DataFrame(records)


def main() -> None:
    ensure_dirs()

    inventory = source_inventory()
    write_csv(inventory, TABLAS_DIR / "inventario_fuentes_capa_objetiva_fase8_fuerte.csv")

    f01, oferta_barrio, oferta_comuna = build_f01()
    f02, habil_comuna = build_f02()
    f02_no_barrio = int((f02["barrio_contexto"].eq("") | f02["barrio_contexto"].eq("No determinado")).sum())
    no_determinada_f02 = int(habil_comuna.loc[habil_comuna["comuna"].eq("No determinada"), "cantidad_habilitaciones_gastronomicas"].sum()) if "No determinada" in set(habil_comuna["comuna"]) else 0

    idx_barrio, idx_comuna = build_indices(oferta_barrio, oferta_comuna, habil_comuna)
    polos_cross = build_polos_cross(idx_barrio, idx_comuna)

    insumo_mapa = idx_barrio[
        ["barrio", "comuna", "cantidad_oferta_registrada", "indice_senal_objetiva", "nivel_senal_objetiva"]
    ].copy()
    habil_by_comuna = habil_comuna[["comuna", "cantidad_habilitaciones_gastronomicas"]]
    insumo_mapa = insumo_mapa.merge(habil_by_comuna, on="comuna", how="left")
    insumo_mapa["cantidad_habilitaciones"] = insumo_mapa["cantidad_habilitaciones_gastronomicas"].fillna(0).astype(int)
    insumo_mapa = insumo_mapa.drop(columns=["cantidad_habilitaciones_gastronomicas"])
    insumo_mapa["observaciones"] = (
        "Insumo de contexto por barrio; no delimita polos ni valida corredores."
    )

    write_csv(oferta_barrio, TABLAS_DIR / "oferta_gastronomica_por_barrio_fase8_fuerte.csv")
    write_csv(oferta_comuna, TABLAS_DIR / "oferta_gastronomica_por_comuna_fase8_fuerte.csv")
    write_csv(habil_comuna, TABLAS_DIR / "habilitaciones_gastronomicas_por_comuna_fase8_fuerte.csv")
    write_csv(idx_barrio, TABLAS_DIR / "indice_senal_objetiva_por_barrio_fase8_fuerte.csv")
    write_csv(idx_comuna, TABLAS_DIR / "indice_senal_objetiva_por_comuna_fase8_fuerte.csv")
    write_csv(polos_cross, TABLAS_DIR / "polos_vs_capa_objetiva_fase8_fuerte.csv")
    write_csv(insumo_mapa, TABLAS_DIR / "insumo_mapa_contexto_objetivo_fase8_fuerte.csv")

    docs_inventory(inventory)
    docs_fuentes_insuficientes(len(f02), f02_no_barrio)
    docs_methodology(len(f01), len(f02), f02_no_barrio, no_determinada_f02)
    docs_comparative(polos_cross)
    docs_recommendations()
    docs_map_notes()
    docs_closing(len(f01), len(f02), len(oferta_barrio), len(oferta_comuna), len(habil_comuna))

    generated_pre_qa = list(DOCS_DIR.glob("*.md")) + list(TABLAS_DIR.glob("*.csv"))
    privacy_results = scan_privacy(generated_pre_qa)
    write_csv(privacy_results, QA_DIR / "qa_privacidad_fase8_fuerte.csv")

    processed_rows = {
        "oferta_gastronomica_por_barrio_fase8_fuerte.csv": len(oferta_barrio),
        "oferta_gastronomica_por_comuna_fase8_fuerte.csv": len(oferta_comuna),
        "habilitaciones_gastronomicas_por_comuna_fase8_fuerte.csv": len(habil_comuna),
        "indice_senal_objetiva_por_barrio_fase8_fuerte.csv": len(idx_barrio),
        "indice_senal_objetiva_por_comuna_fase8_fuerte.csv": len(idx_comuna),
        "polos_vs_capa_objetiva_fase8_fuerte.csv": len(polos_cross),
        "insumo_mapa_contexto_objetivo_fase8_fuerte.csv": len(insumo_mapa),
    }
    docs_qa(len(f01), len(f02), processed_rows, privacy_results)

    all_generated = list(DOCS_DIR.glob("*.md")) + list(TABLAS_DIR.glob("*.csv")) + list(QA_DIR.glob("*.csv"))
    manifest = {
        "fecha_consulta": FECHA_CONSULTA,
        "descargas_nuevas": False,
        "fuentes_usadas": [
            rel(PATHS["f01_raw"]),
            rel(PATHS["f02_fact"]),
            rel(PATHS["dim_ubicacion"]),
            rel(PATHS["tabla_polos_b2"]),
            rel(PATHS["tabla_polos_f5"]),
        ],
        "filas_leidas": {
            "f01": len(f01),
            "f02": len(f02),
        },
        "archivos_generados": [rel(path) for path in sorted(all_generated)],
    }
    (QA_DIR / "resumen_ejecucion_fase8_fuerte.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
