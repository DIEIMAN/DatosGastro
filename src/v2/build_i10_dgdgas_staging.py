"""DataGastro V2 - Etapa 3: staging interno seguro y minimizado de la fuente I10 DGDGAS.

Lee el Excel local del directorio gastronomico interno (I10), EXCLUYE PII y produce:
  - perfil de columnas por hoja            -> outputs/v2/internal/  (GITIGNORED)
  - establecimientos minimizados (con nombre/direccion, SENSIBLE) -> outputs/v2/internal/
  - agregados sanitizados (sin nombre/direccion/PII)              -> outputs/v2/sanitized/

Garantias:
  - OFFLINE: no hace requests, no usa API keys, no descarga nada.
  - NO modifica, mueve ni borra el Excel original (lectura por zipfile, solo lectura).
  - NO lee .gsheet ni links de Drive. Solo el .xlsx local.
  - PII (celular, mail, referente, instagram, cargo, telefono, nombre de persona, etc.)
    se EXCLUYE: nunca se escribe, ni siquiera en el staging interno.
  - nombre_local y direccion son SENSIBLES operativos: solo en outputs/v2/internal/
    (gitignored), nunca en outputs/v2/sanitized/.
  - No geocodifica, no genera GeoJSON, no publica direcciones.

I10 NO es padron oficial ni censo: es fuente interna de validacion / catalogo candidato.
No implica local activo confirmado. No reemplaza AGC ni fuentes oficiales.

Uso:
    python src/v2/build_i10_dgdgas_staging.py
"""
from __future__ import annotations

import csv
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INTERNAL_DIR = REPO_ROOT / "outputs" / "v2" / "internal"
SANITIZED_DIR = REPO_ROOT / "outputs" / "v2" / "sanitized"

FUENTE_CODIGO = "I10_directorio_gastronomico_dgdgas"

# Ubicaciones candidatas del Excel I10 (solo .xlsx local; nunca .gsheet).
EXCEL_CANDIDATAS = [
    "Algunas Cosas de Drive/Copia de Base de datos   DGDGAS EVENTOS.xlsx",
    "Algunas Cosas de Drive/Copia de Base de datos DGDGAS EVENTOS.xlsx",
]

# Hojas de rubro a procesar como establecimientos -> subcategoria_v2 sugerida.
# Las hojas mixtas y los rubros no estables NO se resuelven a la fuerza.
SHEET_TO_SUBCAT = {
    "Bares": "bares",
    "Bodegones": "bodegones",
    "Cocina internacional": "restaurantes",
    "Heladería": "heladerias",
    "Parrillas": "parrillas",
    "Restaurantes": "restaurantes",
    "Restaurantes de autor": "restaurantes",
    "Café y dulce": "pendiente_desagregar_hoja_mixta",
    "Pizza, empanadas y pasta": "pendiente_desagregar_hoja_mixta",
    "Hamburguesería": "pendiente_revision_taxonomica",
    "Foodtrucks": "pendiente_revision_taxonomica",
    "Emprendimientos": "pendiente_revision_taxonomica",
}
# Hojas que NO son establecimientos (resumen, organizadores con PII, referencia territorial).
SHEETS_EXCLUIDAS = {"BASE", "Organizadores", "Comunas"}

PENDIENTE_VALUES = {"pendiente_desagregar_hoja_mixta", "pendiente_revision_taxonomica"}

# Encabezados PII a excluir SIEMPRE (normalizados a minuscula sin acento).
PII_HEADERS = {
    "celular", "telefono", "tel", "mail", "email", "correo", "referente",
    "contacto", "instagram", "redes", "cargo", "dni", "cuit", "nombre", "detalle",
}
# Encabezados operativos utiles.
COL_NOMBRE = {"local"}
COL_BARRIO = {"barrio"}
COL_DIRECCION = {"direccion"}

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NS_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def norm(s: str) -> str:
    s = (s or "").strip().lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        s = s.replace(a, b)
    return s


def col_to_idx(ref: str) -> int:
    """'B3' -> 1 (0-based)."""
    letters = re.match(r"[A-Z]+", ref or "")
    if not letters:
        return 0
    idx = 0
    for ch in letters.group(0):
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


def read_xlsx(path: Path) -> dict[str, list[list[str]]]:
    """Lee un xlsx por zipfile. Devuelve {hoja: [filas]} (fila 0 = encabezados)."""
    with zipfile.ZipFile(path) as z:
        # shared strings
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            sroot = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sroot:
                texts = [t.text or "" for t in si.iter(f"{NS}t")]
                shared.append("".join(texts))
        # workbook: nombre -> r:id
        wbroot = ET.fromstring(z.read("xl/workbook.xml"))
        name_to_rid = {}
        for sh in wbroot.iter(f"{NS}sheet"):
            name_to_rid[sh.get("name")] = sh.get(f"{NS_R}id")
        # rels: r:id -> target
        relroot = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {}
        for rel in relroot:
            rid_to_target[rel.get("Id")] = rel.get("Target")

        result: dict[str, list[list[str]]] = {}
        for name, rid in name_to_rid.items():
            target = rid_to_target.get(rid, "")
            if not target:
                continue
            part = "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
            if part not in z.namelist():
                part = "xl/" + target.split("xl/")[-1]
            try:
                sroot = ET.fromstring(z.read(part))
            except KeyError:
                continue
            rows: list[list[str]] = []
            for row in sroot.iter(f"{NS}row"):
                cells: dict[int, str] = {}
                for c in row.findall(f"{NS}c"):
                    ref = c.get("r", "")
                    t = c.get("t", "")
                    v = c.find(f"{NS}v")
                    if t == "s" and v is not None:
                        val = shared[int(v.text)] if v.text and v.text.isdigit() else ""
                    elif t == "inlineStr":
                        is_el = c.find(f"{NS}is")
                        val = "".join(tt.text or "" for tt in is_el.iter(f"{NS}t")) if is_el is not None else ""
                    else:
                        val = v.text if v is not None and v.text is not None else ""
                    cells[col_to_idx(ref)] = (val or "").strip()
                if not cells:
                    continue
                width = max(cells) + 1
                rows.append([cells.get(i, "") for i in range(width)])
            result[name] = rows
        return result


def find_excel() -> Path | None:
    for rel in EXCEL_CANDIDATAS:
        p = REPO_ROOT / rel
        if p.is_file():
            return p
    # busqueda flexible
    for p in (REPO_ROOT / "Algunas Cosas de Drive").glob("*DGDGAS*EVENTOS*.xlsx") \
            if (REPO_ROOT / "Algunas Cosas de Drive").is_dir() else []:
        return p
    return None


def write_csv(path: Path, header: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    print("=" * 78)
    print("DataGastro V2 - Etapa 3: staging interno minimizado de I10 DGDGAS (OFFLINE)")
    print("No requests, no API keys, no modifica el Excel original, excluye PII.")
    print("=" * 78)

    excel = find_excel()
    if excel is None:
        print("\n[ERROR] No se encontro el Excel I10. Rutas revisadas (relativas al repo):")
        for rel in EXCEL_CANDIDATAS:
            print(f"  - {rel}")
        print("Staging NO generado. (Si el proyecto se movio de maquina, es esperable.)")
        return 1

    print(f"\nExcel I10 detectado: {excel.relative_to(REPO_ROOT)}")
    data = read_xlsx(excel)

    perfil_rows = []
    minim_rows = []
    seq = 0
    pii_cells_excluidas = 0

    for hoja, rows in data.items():
        if not rows:
            continue
        header = rows[0]
        data_rows = rows[1:]
        norm_headers = [norm(h) for h in header]
        cols_pii = [header[i] for i, h in enumerate(norm_headers) if h in PII_HEADERS]
        cols_utiles = [header[i] for i, h in enumerate(norm_headers)
                       if h in COL_NOMBRE | COL_BARRIO | COL_DIRECCION]

        es_establecimiento = hoja in SHEET_TO_SUBCAT
        accion = ("minimizar_a_staging" if es_establecimiento
                  else "excluir_no_es_establecimiento")
        perfil_rows.append({
            "hoja": hoja,
            "cantidad_filas": len(data_rows),
            "cantidad_columnas": len(header),
            "columnas_detectadas": " | ".join(h for h in header if h),
            "columnas_pii_detectadas": " | ".join(cols_pii),
            "columnas_utiles_detectadas": " | ".join(cols_utiles),
            "accion_recomendada": accion,
        })

        if not es_establecimiento:
            continue

        # indices de columnas utiles
        idx_nombre = next((i for i, h in enumerate(norm_headers) if h in COL_NOMBRE), None)
        idx_barrio = next((i for i, h in enumerate(norm_headers) if h in COL_BARRIO), None)
        idx_dir = next((i for i, h in enumerate(norm_headers) if h in COL_DIRECCION), None)
        idx_pii = [i for i, h in enumerate(norm_headers) if h in PII_HEADERS]
        subcat = SHEET_TO_SUBCAT[hoja]

        for r in data_rows:
            def cell(i):
                return r[i].strip() if (i is not None and i < len(r)) else ""
            nombre = cell(idx_nombre)
            barrio = cell(idx_barrio)
            direccion = cell(idx_dir)
            # contar PII no vacio que se descarta (no se escribe en ningun lado)
            for i in idx_pii:
                if cell(i):
                    pii_cells_excluidas += 1
            if not (nombre or barrio or direccion):
                continue  # fila vacia operativa
            seq += 1
            minim_rows.append({
                "id_i10_anonimo": f"I10-{seq:06d}",
                "fuente_codigo": FUENTE_CODIGO,
                "hoja_origen": hoja,
                "rubro_origen_hoja": hoja,
                "subcategoria_v2_sugerida": subcat,
                "nombre_local": nombre,           # SENSIBLE - solo interno
                "barrio": barrio,
                "comuna_si_existe": "",            # las hojas de rubro no traen comuna
                "direccion_si_existe": direccion,  # SENSIBLE - solo interno
                "observacion_no_sensible_si_existe": "",
                "estado_revision": "minimizado_no_integrado",
            })

    # --- escribir staging INTERNO (gitignored) ---
    write_csv(INTERNAL_DIR / "i10_dgdgas_perfil_columnas.csv",
              ["hoja", "cantidad_filas", "cantidad_columnas", "columnas_detectadas",
               "columnas_pii_detectadas", "columnas_utiles_detectadas", "accion_recomendada"],
              perfil_rows)
    write_csv(INTERNAL_DIR / "i10_dgdgas_establecimientos_minimizados.csv",
              ["id_i10_anonimo", "fuente_codigo", "hoja_origen", "rubro_origen_hoja",
               "subcategoria_v2_sugerida", "nombre_local", "barrio", "comuna_si_existe",
               "direccion_si_existe", "observacion_no_sensible_si_existe", "estado_revision"],
              minim_rows)

    # --- agregados SANITIZADOS (sin nombre/direccion/PII) ---
    total = len(minim_rows)
    con_barrio = sum(1 for m in minim_rows if m["barrio"])
    con_dir = sum(1 for m in minim_rows if m["direccion_si_existe"])
    en_mixtas = sum(1 for m in minim_rows
                    if m["subcategoria_v2_sugerida"] == "pendiente_desagregar_hoja_mixta")
    en_pendiente_tax = sum(1 for m in minim_rows
                           if m["subcategoria_v2_sugerida"] == "pendiente_revision_taxonomica")

    # por hoja
    por_hoja = {}
    for m in minim_rows:
        h = m["hoja_origen"]
        d = por_hoja.setdefault(h, {"subcat": m["subcategoria_v2_sugerida"], "n": 0,
                                    "barrio": 0, "dir": 0})
        d["n"] += 1
        d["barrio"] += 1 if m["barrio"] else 0
        d["dir"] += 1 if m["direccion_si_existe"] else 0
    por_hoja_rows = [{
        "rubro_origen_hoja": h,
        "subcategoria_v2_sugerida": d["subcat"],
        "cantidad_registros": d["n"],
        "cantidad_con_barrio": d["barrio"],
        "cantidad_con_direccion_interna": d["dir"],
        "cantidad_pendiente_desagregar": d["n"] if d["subcat"] in PENDIENTE_VALUES else 0,
        "nivel_sensibilidad": "bajo (agregado sin PII)",
        "uso_recomendado": "validacion_interna_y_cobertura_por_rubro",
    } for h, d in sorted(por_hoja.items())]

    # por rubro v2
    por_rubro = {}
    for m in minim_rows:
        s = m["subcategoria_v2_sugerida"]
        d = por_rubro.setdefault(s, {"n": 0, "barrio": 0, "hojas": set()})
        d["n"] += 1
        d["barrio"] += 1 if m["barrio"] else 0
        d["hojas"].add(m["hoja_origen"])
    por_rubro_rows = [{
        "subcategoria_v2_sugerida": s,
        "cantidad_registros": d["n"],
        "cantidad_hojas_aportan": len(d["hojas"]),
        "cantidad_con_barrio": d["barrio"],
        "nivel_sensibilidad": "bajo (agregado sin PII)",
        "uso_recomendado": ("pendiente_desagregar" if s in PENDIENTE_VALUES
                            else "cobertura_por_rubro"),
    } for s, d in sorted(por_rubro.items())]

    # por barrio (solo nombre de barrio + conteos, sin direcciones ni nombres)
    por_barrio = {}
    for m in minim_rows:
        b = m["barrio"] or "(sin_barrio)"
        d = por_barrio.setdefault(b, {"n": 0, "hojas": set()})
        d["n"] += 1
        d["hojas"].add(m["hoja_origen"])
    por_barrio_rows = [{
        "barrio": b,
        "cantidad_registros": d["n"],
        "cantidad_hojas": len(d["hojas"]),
        "nivel_sensibilidad": "bajo (agregado sin PII)",
        "uso_recomendado": "cobertura_territorial_interna",
    } for b, d in sorted(por_barrio.items(), key=lambda kv: -kv[1]["n"])]

    resumen_rows = [
        {"metrica": "total_registros_i10", "valor": total,
         "observacion": "establecimientos minimizados desde hojas de rubro (no es padron ni censo)"},
        {"metrica": "hojas_procesadas", "valor": len(SHEET_TO_SUBCAT),
         "observacion": "hojas de rubro tratadas como establecimientos"},
        {"metrica": "registros_con_barrio", "valor": con_barrio,
         "observacion": "registros con barrio no vacio"},
        {"metrica": "registros_con_direccion_interna", "valor": con_dir,
         "observacion": "direccion solo en staging interno gitignored, nunca sanitizado"},
        {"metrica": "registros_en_hojas_mixtas", "valor": en_mixtas,
         "observacion": "Cafe y dulce + Pizza/empanadas/pasta: requieren desagregacion"},
        {"metrica": "registros_pendiente_revision_taxonomica", "valor": en_pendiente_tax,
         "observacion": "Hamburgueseria + Foodtrucks + Emprendimientos: rubro no estable"},
        {"metrica": "registros_excluidos_por_pii", "valor": pii_cells_excluidas,
         "observacion": "valores de PII (celular/mail/referente/instagram/cargo) descartados; no se elimino ningun establecimiento"},
        {"metrica": "hojas_excluidas_no_establecimiento", "valor": len(SHEETS_EXCLUIDAS),
         "observacion": "BASE, Organizadores (PII), Comunas (PII): no son establecimientos"},
    ]

    write_csv(SANITIZED_DIR / "i10_dgdgas_agregado_por_hoja.csv",
              ["rubro_origen_hoja", "subcategoria_v2_sugerida", "cantidad_registros",
               "cantidad_con_barrio", "cantidad_con_direccion_interna",
               "cantidad_pendiente_desagregar", "nivel_sensibilidad", "uso_recomendado"],
              por_hoja_rows)
    write_csv(SANITIZED_DIR / "i10_dgdgas_agregado_por_rubro_v2.csv",
              ["subcategoria_v2_sugerida", "cantidad_registros", "cantidad_hojas_aportan",
               "cantidad_con_barrio", "nivel_sensibilidad", "uso_recomendado"],
              por_rubro_rows)
    write_csv(SANITIZED_DIR / "i10_dgdgas_agregado_por_barrio.csv",
              ["barrio", "cantidad_registros", "cantidad_hojas", "nivel_sensibilidad",
               "uso_recomendado"],
              por_barrio_rows)
    write_csv(SANITIZED_DIR / "i10_dgdgas_resumen_integracion.csv",
              ["metrica", "valor", "observacion"], resumen_rows)

    print(f"\nHojas leidas: {len(data)} | hojas de establecimientos: {len(SHEET_TO_SUBCAT)} | "
          f"hojas excluidas: {len(SHEETS_EXCLUIDAS)}")
    print(f"Total establecimientos minimizados (interno): {total}")
    print(f"  con barrio: {con_barrio} | con direccion (solo interno): {con_dir}")
    print(f"  en hojas mixtas: {en_mixtas} | pendiente revision taxonomica: {en_pendiente_tax}")
    print(f"  valores PII excluidos: {pii_cells_excluidas}")
    print("\nInternos (GITIGNORED):")
    print("  outputs/v2/internal/i10_dgdgas_perfil_columnas.csv")
    print("  outputs/v2/internal/i10_dgdgas_establecimientos_minimizados.csv")
    print("Sanitizados (versionables, sin PII):")
    print("  outputs/v2/sanitized/i10_dgdgas_agregado_por_hoja.csv")
    print("  outputs/v2/sanitized/i10_dgdgas_agregado_por_rubro_v2.csv")
    print("  outputs/v2/sanitized/i10_dgdgas_agregado_por_barrio.csv")
    print("  outputs/v2/sanitized/i10_dgdgas_resumen_integracion.csv")
    print("\nI10 = fuente interna de validacion / catalogo candidato. No es padron ni local activo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
