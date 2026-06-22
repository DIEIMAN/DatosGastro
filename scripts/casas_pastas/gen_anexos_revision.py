"""Genera anexos INTERNOS para la revisión manual de los 42 casos (SIN requests).

Salidas (carpeta interna, gitignored — pueden tener nombres individuales):
  outputs/casas_pastas_reporte/anexos_internos/listado_42_revision_manual.csv
  outputs/casas_pastas_reporte/anexos_internos/listado_42_revision_manual_para_buscar.md
  outputs/casas_pastas_reporte/anexos_internos/checklist_validacion_manual.md

No para el pack compartible. No commitea. No toca el pipeline principal.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INT = ROOT / "outputs" / "casas_pastas_integrado"
OUT = ROOT / "outputs" / "casas_pastas_reporte" / "anexos_internos"
PADRON = INT / "padron_candidato_integrado_v2.csv"
AUDIT = INT / "auditoria_calidad" / "auditoria_revision_manual_prioritaria_ordenada.csv"


def que_verificar(accion: str, motivo: str) -> str:
    if accion == "revisar_fusion":
        return "¿Es el mismo local que un candidato cercano? (posible duplicado)"
    if "tipo_venta" in motivo or "nombre_compatible" in motivo:
        return "¿Sigue existiendo y vende pastas (casa de pastas / pastificio)?"
    return "Confirmar existencia y rubro (pastas vs. restaurante/otro)."


def main() -> int:
    pad = list(csv.DictReader(PADRON.open(encoding="utf-8-sig")))
    B = [r for r in pad if r["clase_integrada"] == "B_revision_manual"]
    aud = {r["nombre"]: r for r in csv.DictReader(AUDIT.open(encoding="utf-8-sig"))} if AUDIT.exists() else {}
    OUT.mkdir(parents=True, exist_ok=True)

    filas = []
    for i, r in enumerate(B, 1):
        a = aud.get(r["nombre"], {})
        motivo = a.get("motivo_prioridad", "senal_debil")
        accion = a.get("accion_sugerida", "validar_manual")
        prioridad = int(a.get("prioridad_revision", "3") or 3)
        filas.append({
            "id_anonimo": f"REV{i:02d}", "nombre": r["nombre"],
            "fuente": r["fuentes_detectan"], "clase_actual": r["clase_integrada"],
            "comuna": r["comuna"], "barrio": r["barrio"],
            "motivo_revision": motivo, "accion_sugerida": accion,
            "_prioridad": prioridad, "_verificar": que_verificar(accion, motivo),
        })
    filas.sort(key=lambda x: (x["_prioridad"], x["nombre"]))

    # CSV
    cols = ["id_anonimo", "nombre", "fuente", "clase_actual", "comuna", "barrio",
            "motivo_revision", "accion_sugerida"]
    with (OUT / "listado_42_revision_manual.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(filas)

    # MD para buscar
    L = ["# Casos en revisión manual\n",
         f"_Total: {len(filas)} casos. Listado interno para validación manual. No publicar._\n"]
    for nivel, etq in ((2, "Prioridad alta"), (3, "Prioridad media")):
        grupo = [f for f in filas if f["_prioridad"] == nivel]
        if not grupo:
            continue
        L.append(f"## {etq} ({len(grupo)})\n")
        for f in grupo:
            terr = " / ".join(x for x in [f["barrio"], f"Comuna {f['comuna']}" if f["comuna"] else ""] if x)
            L.append(f"- **{f['nombre']}** — {terr or 's/d'} — {f['motivo_revision']} — {f['_verificar']}")
        L.append("")
    (OUT / "listado_42_revision_manual_para_buscar.md").write_text("\n".join(L), encoding="utf-8")

    # Checklist de validación
    chk = """# Checklist de validación manual — casas de pastas candidatas

Tareas para la revisión manual de los casos pendientes:

1. Buscar los 42 casos en internet.
2. Confirmar si siguen existiendo.
3. Confirmar si venden pastas frescas / casa de pastas / pastificio.
4. Confirmar si son restaurante, bodegón o rubro no incluido.
5. Revisar páginas oficiales de cadenas para validar cantidad de sucursales.
6. Revisar manualmente los casos de posibles fusiones.
7. Documentar fuente consultada y decisión.
"""
    (OUT / "checklist_validacion_manual.md").write_text(chk, encoding="utf-8")

    print(f"Anexos generados en {OUT.relative_to(ROOT)}: {len(filas)} casos")
    print(f"  prioridad alta (2): {sum(1 for f in filas if f['_prioridad']==2)} · "
          f"media (3): {sum(1 for f in filas if f['_prioridad']==3)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
