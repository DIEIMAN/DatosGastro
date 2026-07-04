"""DataGastro V2 - Etapa 3.5: normalizacion interna de I10 (barrios + rubros).

OFFLINE. Lee el staging interno minimizado de I10 y los configs de normalizacion, y produce:
  - un dataset interno normalizado (GITIGNORED) con barrio/rubro normalizados;
  - agregados sanitizados (sin nombre/direccion/PII) para revision.

Garantias:
  - No hace requests, no usa API keys, no descarga nada.
  - No modifica el Excel original ni el staging previo.
  - No deduplica contra fuentes externas, no geocodifica, no crea padron final.
  - Nombres y direcciones NO se copian a outputs sanitizados (se usan solo para clasificar
    rubro en hojas mixtas y permanecen en el staging interno gitignored).

I10 = fuente interna de validacion / catalogo candidato. No es padron ni local activo.

Uso:
    python src/v2/normalize_i10_dgdgas.py
"""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INTERNAL_DIR = REPO_ROOT / "outputs" / "v2" / "internal"
SANITIZED_DIR = REPO_ROOT / "outputs" / "v2" / "sanitized"
CONFIG_DIR = REPO_ROOT / "config" / "v2"

IN_MINIM = INTERNAL_DIR / "i10_dgdgas_establecimientos_minimizados.csv"
IN_ALIASES = CONFIG_DIR / "barrios_caba_aliases_v2.csv"
IN_REGLAS = CONFIG_DIR / "reglas_desagregacion_i10_v2.csv"
OUT_NORM = INTERNAL_DIR / "i10_dgdgas_establecimientos_normalizados.csv"

HOJAS_MIXTAS = {"Café y dulce", "Pizza, empanadas y pasta"}
HOJAS_PENDIENTES_TAX = {"Hamburguesería", "Foodtrucks", "Emprendimientos"}
TIPOS_BARRIO_OK = {"oficial", "variante_ortografica", "subzona"}
SEP_RE = re.compile(r"\s*[\/\n;]\s*|\s+-\s+|\s*,\s*|\s+y\s+")


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"\(.*?\)", "", s)  # quita parentesis
    return s.strip().lower()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, header: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


def load_aliases() -> dict[str, tuple[str, str, str]]:
    """na(alias) -> (barrio_oficial, comuna, tipo_alias)."""
    m: dict[str, tuple[str, str, str]] = {}
    for r in read_csv(IN_ALIASES):
        m[fold(r["alias"])] = (r["barrio_oficial"], r["comuna"], r["tipo_alias"])
    return m


def load_reglas() -> dict[str, list[tuple[re.Pattern, str, str]]]:
    """hoja_origen -> [(patron_compilado, subcategoria_destino, confianza)]."""
    reglas: dict[str, list] = defaultdict(list)
    for r in read_csv(IN_REGLAS):
        pat = re.compile(r["patron"], re.IGNORECASE)
        reglas[r["hoja_origen"]].append((pat, r["subcategoria_v2_destino"], r["confianza"]))
    return reglas


def normalizar_barrio(raw: str, alias: dict) -> tuple[str, str, str]:
    """Devuelve (barrio_normalizado, comuna_normalizada, estado_barrio)."""
    raw = (raw or "").strip()
    if not raw:
        return "", "", "sin_barrio"
    parts = [p for p in SEP_RE.split(raw) if p.strip()]
    resolved = [alias.get(fold(p)) for p in parts]
    officials = {r[0] for r in resolved if r and r[2] in TIPOS_BARRIO_OK}
    if len(officials) >= 2:
        return "(multiple)", "", "multiple_barrio"
    cand = alias.get(fold(raw))
    if cand is None:
        cand = next((r for r in resolved if r is not None), None)
    if cand is None:
        return "", "", "pendiente_revision"
    bo, com, tipo = cand
    if tipo in TIPOS_BARRIO_OK:
        return bo, com, "normalizado"
    if tipo == "generico_caba":
        return "", "", "ambiguo"
    if tipo == "no_barrio":
        return "", "", "ambiguo"
    if tipo == "fuera_caba":
        return "", "", "fuera_caba_probable"
    return "", "", "pendiente_revision"


def normalizar_rubro(hoja: str, subcat_orig: str, nombre_local: str,
                     reglas: dict) -> tuple[str, str, str]:
    """Devuelve (subcategoria_normalizada, estado_rubro, nivel_confianza)."""
    if hoja in HOJAS_MIXTAS:
        for pat, destino, conf in reglas.get(hoja, []):
            if pat.search(nombre_local or ""):
                return destino, "desagregado_tentativo", conf
        return "pendiente_desagregar_hoja_mixta", "pendiente_desagregar", "baja"
    if hoja in HOJAS_PENDIENTES_TAX:
        return "pendiente_revision_taxonomica", "pendiente_taxonomica", "baja"
    # hoja de rubro clara: hereda la subcategoria sugerida
    return subcat_orig, "directo_hoja", "media"


def main() -> int:
    print("=" * 78)
    print("DataGastro V2 - Etapa 3.5: normalizacion interna de I10 (OFFLINE)")
    print("No requests, no API keys, no toca el Excel original, no crea padron final.")
    print("=" * 78)

    if not IN_MINIM.is_file():
        print(f"\n[ERROR] No existe el staging interno: {IN_MINIM.relative_to(REPO_ROOT)}")
        print("Corre antes: python src/v2/build_i10_dgdgas_staging.py")
        return 1

    alias = load_aliases()
    reglas = load_reglas()
    registros = read_csv(IN_MINIM)

    norm_rows = []
    for r in registros:
        b_norm, comuna, estado_b = normalizar_barrio(r.get("barrio", ""), alias)
        subcat_norm, estado_r, conf = normalizar_rubro(
            r.get("hoja_origen", ""), r.get("subcategoria_v2_sugerida", ""),
            r.get("nombre_local", ""), reglas)
        flags = []
        if estado_b != "normalizado":
            flags.append(f"barrio_{estado_b}")
        if estado_r in ("pendiente_desagregar", "pendiente_taxonomica"):
            flags.append("rubro_pendiente")
        elif estado_r == "desagregado_tentativo":
            flags.append("rubro_desagregado")
        norm_rows.append({
            "id_i10_anonimo": r.get("id_i10_anonimo", ""),
            "hoja_origen": r.get("hoja_origen", ""),
            "rubro_origen_hoja": r.get("rubro_origen_hoja", ""),
            "subcategoria_v2_sugerida_original": r.get("subcategoria_v2_sugerida", ""),
            "subcategoria_v2_normalizada": subcat_norm,
            "barrio_original": r.get("barrio", ""),
            "barrio_normalizado": b_norm,
            "comuna_normalizada": comuna,
            "estado_barrio": estado_b,
            "estado_rubro": estado_r,
            "nivel_confianza_rubro": conf,
            "flags_calidad": " | ".join(flags),
        })

    # --- INTERNO (gitignored) ---
    write_csv(OUT_NORM,
              ["id_i10_anonimo", "hoja_origen", "rubro_origen_hoja",
               "subcategoria_v2_sugerida_original", "subcategoria_v2_normalizada",
               "barrio_original", "barrio_normalizado", "comuna_normalizada",
               "estado_barrio", "estado_rubro", "nivel_confianza_rubro", "flags_calidad"],
              norm_rows)

    total = len(norm_rows)

    # --- A) calidad de barrios ---
    est_b = Counter(r["estado_barrio"] for r in norm_rows)
    obs_b = {
        "normalizado": "barrio mapeado a barrio oficial CABA",
        "sin_barrio": "celda de barrio vacia",
        "ambiguo": "referencia generica (CABA/Buenos Aires) o no-barrio",
        "multiple_barrio": "varios barrios en una celda",
        "fuera_caba_probable": "localidad fuera de CABA (GBA u otra)",
        "pendiente_revision": "no se pudo mapear, requiere revision",
    }
    calidad_rows = [{
        "estado_barrio": k,
        "cantidad_registros": v,
        "porcentaje": f"{100*v/total:.1f}",
        "observacion": obs_b.get(k, ""),
    } for k, v in sorted(est_b.items(), key=lambda kv: -kv[1])]

    # --- B) agregado barrio normalizado ---
    by_barrio = defaultdict(lambda: {"n": 0, "hojas": set()})
    for r in norm_rows:
        if r["estado_barrio"] == "normalizado":
            d = by_barrio[(r["barrio_normalizado"], r["comuna_normalizada"])]
            d["n"] += 1
            d["hojas"].add(r["hoja_origen"])
    barrio_rows = [{
        "barrio_normalizado": b,
        "comuna_normalizada": c,
        "cantidad_registros": d["n"],
        "cantidad_hojas": len(d["hojas"]),
        "estado_barrio": "normalizado",
    } for (b, c), d in sorted(by_barrio.items(), key=lambda kv: -kv[1]["n"])]

    # --- C) agregado rubro normalizado ---
    by_rubro = defaultdict(lambda: {"n": 0, "hojas": set()})
    for r in norm_rows:
        key = (r["subcategoria_v2_normalizada"], r["estado_rubro"], r["nivel_confianza_rubro"])
        d = by_rubro[key]
        d["n"] += 1
        d["hojas"].add(r["hoja_origen"])
    rubro_rows = [{
        "subcategoria_v2_normalizada": s,
        "cantidad_registros": d["n"],
        "cantidad_hojas": len(d["hojas"]),
        "estado_rubro": est,
        "nivel_confianza": conf,
    } for (s, est, conf), d in sorted(by_rubro.items(), key=lambda kv: -kv[1]["n"])]

    # --- D) desagregacion de hojas mixtas / pendientes ---
    by_desag = defaultdict(lambda: {"n": 0, "conf": Counter()})
    for r in norm_rows:
        if r["hoja_origen"] in HOJAS_MIXTAS | HOJAS_PENDIENTES_TAX:
            d = by_desag[(r["hoja_origen"], r["subcategoria_v2_normalizada"])]
            d["n"] += 1
            d["conf"][r["nivel_confianza_rubro"]] += 1
    desag_rows = [{
        "hoja_origen": h,
        "subcategoria_v2_destino": s,
        "cantidad_registros": d["n"],
        "nivel_confianza": d["conf"].most_common(1)[0][0],
        "observacion": ("clasificacion tentativa por nombre" if s not in
                        ("pendiente_desagregar_hoja_mixta", "pendiente_revision_taxonomica")
                        else "sin match claro, queda pendiente"),
    } for (h, s), d in sorted(by_desag.items(), key=lambda kv: (kv[0][0], -kv[1]["n"]))]

    # --- E) pendientes de revision ---
    pend = []
    n_desag_pend = sum(1 for r in norm_rows if r["estado_rubro"] == "pendiente_desagregar")
    n_tax = sum(1 for r in norm_rows if r["estado_rubro"] == "pendiente_taxonomica")
    pend.append({"tipo_pendiente": "rubro_pendiente_desagregar", "cantidad_registros": n_desag_pend,
                 "motivo": "hoja mixta sin match de nombre a subcategoria",
                 "accion_recomendada": "afinar reglas o revision manual"})
    pend.append({"tipo_pendiente": "rubro_pendiente_revision_taxonomica", "cantidad_registros": n_tax,
                 "motivo": "Hamburgueseria/Foodtrucks/Emprendimientos: rubro no estable",
                 "accion_recomendada": "decidir subcategoria nueva o mapeo"})
    for est in ("sin_barrio", "ambiguo", "multiple_barrio", "fuera_caba_probable", "pendiente_revision"):
        pend.append({"tipo_pendiente": f"barrio_{est}", "cantidad_registros": est_b.get(est, 0),
                     "motivo": obs_b.get(est, ""),
                     "accion_recomendada": "normalizar/desagregar o excluir si es fuera de CABA"})

    write_csv(SANITIZED_DIR / "i10_dgdgas_calidad_barrios.csv",
              ["estado_barrio", "cantidad_registros", "porcentaje", "observacion"], calidad_rows)
    write_csv(SANITIZED_DIR / "i10_dgdgas_agregado_barrio_normalizado.csv",
              ["barrio_normalizado", "comuna_normalizada", "cantidad_registros",
               "cantidad_hojas", "estado_barrio"], barrio_rows)
    write_csv(SANITIZED_DIR / "i10_dgdgas_agregado_rubro_normalizado.csv",
              ["subcategoria_v2_normalizada", "cantidad_registros", "cantidad_hojas",
               "estado_rubro", "nivel_confianza"], rubro_rows)
    write_csv(SANITIZED_DIR / "i10_dgdgas_desagregacion_hojas_mixtas.csv",
              ["hoja_origen", "subcategoria_v2_destino", "cantidad_registros",
               "nivel_confianza", "observacion"], desag_rows)
    write_csv(SANITIZED_DIR / "i10_dgdgas_pendientes_revision.csv",
              ["tipo_pendiente", "cantidad_registros", "motivo", "accion_recomendada"], pend)

    # --- resumen consola ---
    n_norm = est_b.get("normalizado", 0)
    print(f"\nTotal registros: {total}")
    print(f"  barrio normalizado: {n_norm} ({100*n_norm/total:.1f}%)")
    print(f"  sin_barrio: {est_b.get('sin_barrio',0)} | ambiguo: {est_b.get('ambiguo',0)} | "
          f"multiple: {est_b.get('multiple_barrio',0)} | fuera_caba: {est_b.get('fuera_caba_probable',0)} | "
          f"pendiente: {est_b.get('pendiente_revision',0)}")
    print(f"  barrios oficiales distintos detectados: {len(by_barrio)}")
    est_r = Counter(r["estado_rubro"] for r in norm_rows)
    print(f"  rubro directo_hoja: {est_r.get('directo_hoja',0)} | desagregado: {est_r.get('desagregado_tentativo',0)} | "
          f"pendiente_desagregar: {est_r.get('pendiente_desagregar',0)} | pendiente_taxonomica: {est_r.get('pendiente_taxonomica',0)}")
    print("\nInterno (GITIGNORED): outputs/v2/internal/i10_dgdgas_establecimientos_normalizados.csv")
    print("Sanitizados: i10_dgdgas_calidad_barrios.csv, _agregado_barrio_normalizado.csv,")
    print("             _agregado_rubro_normalizado.csv, _desagregacion_hojas_mixtas.csv, _pendientes_revision.csv")
    print("\nSigue sin ser padron final: una sola fuente, sin deduplicar, sin geocodificar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
