"""Auditoría de calidad del padrón candidato integrado (SIN nuevos requests).

Verifica que la deduplicación entre fuentes no INFLE (duplicados no fusionados) ni
PIERDA/degrade locales (falsas fusiones; independientes descartados injustamente),
con foco en cadenas (La Juvenil, Master Pastas, Multipasta, Biasatti, Caprizzi, Raviolon,
etc.) y preservando las casas independientes/de barrio.

Reutiliza la carga + dedup del integrador (mismo criterio) a nivel MIEMBRO para poder ver
distancias intra-grupo y entre grupos. No llama a APIs, no usa API key, no commitea.

Salidas en outputs/casas_pastas_integrado/auditoria_calidad/.
"""
from __future__ import annotations

import csv
import datetime as dt
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google_places_clasificador import MARCAS_ESPERADAS, norm_nombre  # noqa: E402
import google_places_integrar as gi  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
AUD = INT / "auditoria_calidad"
PADRON = INT / "padron_candidato_integrado.csv"

# Cadenas a auditar (clave normalizada -> etiqueta).
CADENAS = {
    "la juvenil": "La Juvenil",
    "master pastas": "Master Pastas / Pastas Master",
    "pastas master": "Master Pastas / Pastas Master",
    "multipasta": "Multipasta",
    "biasatti": "Biasatti",
    "caprizzi": "Caprizzi",
    "raviolon": "Raviolon",
    "mazzeo": "Pastas Mazzeo",
    "pastas bayo": "Pastas Bayo",
    "milena pastas": "Milena Pastas Artesanales",
    "el buen gusto": "El Buen Gusto",
    "las malvinas": "Las Malvinas",
}

UNDER_MERGE_M = 150   # dos grupos del mismo nombre/cadena más cerca que esto = posible duplicado no fusionado
OVER_MERGE_M = 300    # miembros de un mismo grupo más lejos que esto = posible falsa fusión


def cadena_de(nrm: str) -> str | None:
    for clave, etiqueta in CADENAS.items():
        if clave in nrm:
            return etiqueta
    return None


def grupo_info(g):
    """Datos agregados de un grupo de dedup (lista de miembros)."""
    clase, conf, rev, fuentes, motivo = gi.clasificar_grupo(g)
    rep = gi.elegir_repr(g)
    # distancia intra-grupo máxima
    maxd = 0.0
    for i in range(len(g)):
        for j in range(i + 1, len(g)):
            d = gi.haversine_m(g[i]["lat"], g[i]["lon"], g[j]["lat"], g[j]["lon"])
            if d < 9e8:
                maxd = max(maxd, d)
    return {
        "nombre": rep["nombre"], "nrm": norm_nombre(rep["nombre"]),
        "lat": rep["lat"], "lon": rep["lon"], "clase": clase, "conf": conf,
        "rev": rev, "fuentes": fuentes, "n_fuentes": len(fuentes),
        "n_miembros": len(g), "max_intra_m": round(maxd, 0),
        "src_counter": Counter(m["fuente"] for m in g),
        "tipo_google": rep.get("tipo_google", ""),
    }


def main() -> int:
    if not PADRON.exists():
        print(f"ABORTADO: falta {PADRON}. Corré primero el integrador.")
        return 2
    AUD.mkdir(parents=True, exist_ok=True)

    grupos = gi.integrar()
    info = [grupo_info(g) for g in grupos]
    for k, gobj in enumerate(grupos):
        info[k]["_id"] = f"GRP{k:04d}"

    # marca cadena/independiente a nivel grupo (solo candidatos no descartados)
    cand = [x for x in info if x["clase"] != "C_descartado"]
    # conteo por nombre normalizado (para independiente vs cadena por repetición)
    cnt_nrm = Counter(x["nrm"] for x in cand)
    for x in cand:
        et = cadena_de(x["nrm"])
        if et or cnt_nrm[x["nrm"]] >= 2:
            x["tipo"], x["cadena"] = "cadena", (et or x["nrm"])
        else:
            x["tipo"], x["cadena"] = "independiente", ""

    # ---------- 1. Auditoría de fusiones por cadena ----------
    cad_rows = []
    cadenas_focus = defaultdict(list)
    for x in cand:
        if x["tipo"] == "cadena" and cadena_de(x["nrm"]):
            cadenas_focus[cadena_de(x["nrm"])].append(x)
    for et, miembros in sorted(cadenas_focus.items(), key=lambda kv: -len(kv[1])):
        n = len(miembros)
        por_g = sum(1 for m in miembros if "google" in m["fuentes"])
        por_o = sum(1 for m in miembros if "osm" in m["fuentes"])
        por_a = sum(1 for m in miembros if "agc" in m["fuentes"])
        multif = sum(1 for m in miembros if m["n_fuentes"] >= 2)
        # pares cercanos entre grupos distintos (under-merge)
        cercanos = 0
        for i in range(len(miembros)):
            for j in range(i + 1, len(miembros)):
                d = gi.haversine_m(miembros[i]["lat"], miembros[i]["lon"],
                                   miembros[j]["lat"], miembros[j]["lon"])
                if d < UNDER_MERGE_M:
                    cercanos += 1
        # falsas fusiones (over-merge): grupos con miembros muy separados
        falsas = sum(1 for m in miembros if m["max_intra_m"] > OVER_MERGE_M)
        if cercanos > 0:
            veredicto = "posible_inflacion_revisar_duplicados"
        elif falsas > 0:
            veredicto = "posible_falsa_fusion_revisar"
        else:
            veredicto = "ok_union_de_fuentes"
        cad_rows.append({
            "cadena": et, "sucursales_integradas": n, "por_google": por_g, "por_osm": por_o,
            "por_agc": por_a, "multifuente": multif, "pares_cercanos_<150m": cercanos,
            "grupos_con_miembros_lejanos_>300m": falsas, "veredicto": veredicto,
        })

    # ---------- 2. Posibles duplicados (cualquier par de candidatos, no solo cadenas) ----------
    dup_rows = []
    for i in range(len(cand)):
        for j in range(i + 1, len(cand)):
            a, b = cand[i], cand[j]
            d = gi.haversine_m(a["lat"], a["lon"], b["lat"], b["lon"])
            if d >= UNDER_MERGE_M:
                continue
            rt = gi.ratio(a["nrm"], b["nrm"])
            if rt >= 0.6:
                dup_rows.append({
                    "id_a": a["_id"], "nombre_a": a["nombre"], "fuentes_a": "+".join(a["fuentes"]),
                    "id_b": b["_id"], "nombre_b": b["nombre"], "fuentes_b": "+".join(b["fuentes"]),
                    "distancia_m": round(d), "similitud_nombre": round(rt, 2),
                    "accion_sugerida": "revisar_fusion",
                })
    dup_rows.sort(key=lambda r: (r["distancia_m"], -r["similitud_nombre"]))

    # ---------- 3. Sucursales por cadena (detalle para eyeball) ----------
    suc_rows = []
    for et, miembros in sorted(cadenas_focus.items(), key=lambda kv: -len(kv[1])):
        for m in sorted(miembros, key=lambda x: (str(x["clase"]), str(x.get("_id")))):
            suc_rows.append({
                "cadena": et, "id_grupo": m["_id"], "clase_integrada": m["clase"],
                "fuentes": "+".join(m["fuentes"]), "comuna_aprox": "",  # comuna se ve en padrón
                "max_intra_m": m["max_intra_m"], "n_miembros": m["n_miembros"],
            })

    # ---------- 4. Muestra de independientes ----------
    ind = [x for x in cand if x["tipo"] == "independiente"]
    ind_A = [x for x in ind if str(x["clase"]).startswith("A_")]
    ind_multi = [x for x in ind if x["n_fuentes"] >= 2]
    ind_rev = [x for x in ind if x["rev"] == "si"]
    muestra = []
    def add(grupo, etiqueta, k):
        for x in grupo[:k]:
            muestra.append({
                "id_grupo": x["_id"], "muestra": etiqueta, "nombre": x["nombre"],
                "clase_integrada": x["clase"], "fuentes": "+".join(x["fuentes"]),
                "tipo_establecimiento": x["tipo"], "confianza_integrada": x["conf"],
            })
    add(ind_A, "independiente_A", 30)
    add(ind_multi, "independiente_multifuente", 20)
    add(ind_rev, "independiente_revision", 20)

    # ---------- 5. Revisión manual prioritaria ordenada ----------
    revs = [x for x in info if x["rev"] == "si"]  # B_revision_manual
    # comunas baja cobertura: <=2 candidatos
    com_cnt = Counter(None for _ in [])
    # recomputar cantidad por comuna desde el padrón (rep usa misma asignación)
    padron_rows = list(csv.DictReader(PADRON.open(encoding="utf-8-sig")))
    com_count = Counter(r["comuna"] for r in padron_rows if r["comuna"])
    baja_cob = {c for c, n in com_count.items() if n <= 2}
    # cercanía a candidatos A
    a_pts = [(x["lat"], x["lon"]) for x in cand if str(x["clase"]).startswith("A_")]
    rev_rows = []
    for x in revs:
        nrm = x["nrm"]
        compat = any(t in nrm for t in ("pasta", "raviol", "sorrentin", "noqui", "gnocchi",
                                        "tallarin", "fideo", "pastificio"))
        tipo_venta = any(t in x["tipo_google"] for t in
                         ("food_store", "store", "manufacturer", "noodle_shop"))
        # comuna del rep: buscar en padron por nombre (aprox); si no, vacío
        cerca_A = False
        for (la, lo) in a_pts:
            if gi.haversine_m(x["lat"], x["lon"], la, lo) < 150:
                cerca_A = True
                break
        score = 0
        motivos = []
        if x["n_fuentes"] >= 2:
            score += 3; motivos.append("multifuente")
        if compat:
            score += 2; motivos.append("nombre_compatible_pastas")
        if tipo_venta:
            score += 2; motivos.append("tipo_venta")
        if cerca_A:
            score += 2; motivos.append("cercano_a_candidato_A")
        # acción sugerida
        if cerca_A and (compat or x["n_fuentes"] >= 2):
            accion = "revisar_fusion"
        elif x["n_fuentes"] >= 2 or (compat and tipo_venta):
            accion = "probable_promover_A"
        elif compat or tipo_venta:
            accion = "validar_manual"
        elif not compat and not tipo_venta:
            accion = "probable_descartar"
        else:
            accion = "mantener_como_B"
        nivel = 1 if score >= 6 else 2 if score >= 4 else 3 if score >= 2 else 4
        rev_rows.append({
            "id_grupo": x["_id"], "nombre": x["nombre"], "clase_integrada": x["clase"],
            "fuentes": "+".join(x["fuentes"]), "tipo_establecimiento_google": x["tipo_google"][:60],
            "prioridad_revision": nivel, "motivo_prioridad": ";".join(motivos) or "senal_debil",
            "accion_sugerida": accion,
        })
    rev_rows.sort(key=lambda r: (r["prioridad_revision"], r["nombre"]))

    # ---------- escritura ----------
    _wr(AUD / "auditoria_fusiones_cadenas.csv",
        ["cadena", "sucursales_integradas", "por_google", "por_osm", "por_agc", "multifuente",
         "pares_cercanos_<150m", "grupos_con_miembros_lejanos_>300m", "veredicto"], cad_rows)
    _wr(AUD / "auditoria_posibles_duplicados.csv",
        ["id_a", "nombre_a", "fuentes_a", "id_b", "nombre_b", "fuentes_b", "distancia_m",
         "similitud_nombre", "accion_sugerida"], dup_rows)
    _wr(AUD / "auditoria_sucursales_cadenas.csv",
        ["cadena", "id_grupo", "clase_integrada", "fuentes", "comuna_aprox", "max_intra_m",
         "n_miembros"], suc_rows)
    _wr(AUD / "auditoria_independientes_muestra.csv",
        ["id_grupo", "muestra", "nombre", "clase_integrada", "fuentes", "tipo_establecimiento",
         "confianza_integrada"], muestra)
    _wr(AUD / "auditoria_revision_manual_prioritaria_ordenada.csv",
        ["id_grupo", "nombre", "clase_integrada", "fuentes", "tipo_establecimiento_google",
         "prioridad_revision", "motivo_prioridad", "accion_sugerida"], rev_rows)

    niveles = Counter(r["prioridad_revision"] for r in rev_rows)
    acciones = Counter(r["accion_sugerida"] for r in rev_rows)
    inflad = [r["cadena"] for r in cad_rows if r["veredicto"] != "ok_union_de_fuentes"]
    resumen = [
        ("fecha", dt.date.today().isoformat()),
        ("candidatos_unicos", len(cand)),
        ("cadenas_auditadas", len(cad_rows)),
        ("cadenas_con_alerta", "; ".join(inflad) or "(ninguna)"),
        ("posibles_duplicados_pares", len(dup_rows)),
        ("falsas_fusiones_grupos", sum(r["grupos_con_miembros_lejanos_>300m"] for r in cad_rows)),
        ("independientes_total", len(ind)),
        ("independientes_A", len(ind_A)),
        ("revision_manual_total", len(rev_rows)),
        ("revision_nivel_1", niveles.get(1, 0)),
        ("revision_nivel_2", niveles.get(2, 0)),
        ("revision_nivel_3", niveles.get(3, 0)),
        ("revision_nivel_4", niveles.get(4, 0)),
        ("accion_probable_promover_A", acciones.get("probable_promover_A", 0)),
        ("accion_revisar_fusion", acciones.get("revisar_fusion", 0)),
        ("accion_validar_manual", acciones.get("validar_manual", 0)),
        ("accion_probable_descartar", acciones.get("probable_descartar", 0)),
        ("comunas_baja_cobertura", "; ".join(sorted(baja_cob)) or "(ninguna)"),
    ]
    _wr(AUD / "resumen_auditoria_calidad.csv", ["indicador", "valor"],
        [{"indicador": k, "valor": v} for k, v in resumen])

    print(f"Cadenas auditadas: {len(cad_rows)} | con alerta: {inflad or '(ninguna)'}")
    print(f"Posibles duplicados (pares <150m, similitud>=0.6): {len(dup_rows)}")
    print(f"Independientes: {len(ind)} (A={len(ind_A)}) | revisión manual: {len(rev_rows)}")
    print(f"  niveles: {dict(niveles)} | acciones: {dict(acciones)}")
    for r in cad_rows:
        print(f"  {r['cadena']:30s} suc={r['sucursales_integradas']:>2} "
              f"(g{r['por_google']}/o{r['por_osm']}/a{r['por_agc']}, multi={r['multifuente']}) "
              f"-> {r['veredicto']}")
    print(f"Salidas en: {AUD.relative_to(ROOT)}")
    return 0


def _wr(path, cols, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
