from __future__ import annotations

import csv
import json
import re
from pathlib import Path


OUT = Path(__file__).resolve().parent
BASE = OUT.parent


def rows(name: str) -> list[dict]:
    with (OUT / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def test_densidad_continuidad() -> None:
    data = rows("densidad_y_continuidad_41.csv")
    assert len(data) == 41
    assert len({row["polo_id"] for row in data}) == 41
    administrativos = {row["polo"] for row in data if row["tipo_de_borde"] == "poligono_de_barrio"}
    assert administrativos == {"Mataderos", "Núñez", "Retiro", "Villa Santa Rita"}
    for row in data:
        assert int(row["n_locales"]) > 0
        assert float(row["superficie_ha"]) > 0
        assert float(row["locales_por_ha"]) >= 0
        curva = [float(row[f"continuidad_pct_{distancia}m"]) for distancia in (20, 40, 60, 80, 120)]
        assert curva == sorted(curva)
        assert all(0 <= valor <= 100 for valor in curva)
        assert row["definicion_continuidad"] == "porcentaje de locales en la componente conexa mayor"


def test_capa_normalizada() -> None:
    with (BASE / "hitos" / "hitos_capa_2026.geojson").open(encoding="utf-8") as fh:
        capa = json.load(fh)
    assert len(capa["features"]) == 215
    cambios_nombre = 0
    cambios_direccion = 0
    conflictos = 0
    for feature in capa["features"]:
        props = feature["properties"]
        assert "nombre_original" in props and "direccion_original" in props
        assert "conflicto_direccion_original" in props
        if props["nombre"] != props["nombre_original"]:
            cambios_nombre += 1
        if props["direccion"] != props["direccion_original"]:
            cambios_direccion += 1
        if str(props.get("conflicto_direccion_original") or "").strip():
            conflictos += 1
            assert str(props.get("conflicto_direccion_estado") or "").strip()
            assert str(props.get("conflicto_direccion_resolucion") or "").strip()
    assert cambios_nombre == 33
    assert cambios_direccion == 17
    assert conflictos == 5
    ejemplo = next(f["properties"] for f in capa["features"] if f["properties"]["direccion_original"] == "MOREAU DE JUSTO, ALICIA AV. 1840")
    assert ejemplo["direccion"] == "Av. Alicia Moreau de Justo 1840"


def test_hitos_fuera_y_conflictos() -> None:
    fuera = rows("hitos_fuera_de_todo_polo.csv")
    assert len(fuera) == 60
    assert sum(row["lectura"] == "posible_borde_incompleto" for row in fuera) == 41
    assert sum(row["lectura"] == "esperable_zona_sin_polo" for row in fuera) == 19
    assert all(float(row["distancia_m"]) >= 0 for row in fuera)
    assert len(rows("hitos_contacto_borde_tolerancia.csv")) == 2
    conflictos = rows("conflictos_direccion.csv")
    assert len(conflictos) == 6
    assert all(row["conflicto_direccion_estado"] and row["conflicto_direccion_resolucion"] for row in conflictos)
    marte = next(row for row in conflictos if row["nombre"] == "Marte")
    assert marte["direccion"] == "Crisólogo Larralde 2772"
    assert marte["conflicto_direccion_estado"] == "resuelto_fuera_de_la_capa"


def test_verificaciones_y_prioridad() -> None:
    verif = rows("verificacion_locales_sin_catalogo.csv")
    assert len(verif) == 37
    requeridas = {"polo", "nombre", "direccion", "existe", "estado", "fuente", "fecha", "nivel_de_verificacion"}
    assert requeridas.issubset(verif[0])
    assert sum(row["nombre"].startswith("Registro kosher no individualizado") for row in verif) == 2
    assert all(row["estado"] != "abierto" for row in verif)
    prioridad = rows("vigencia_historicos_priorizados.csv")
    assert len(prioridad) == 61
    assert [int(row["orden_prioridad"]) for row in prioridad] == list(range(1, 62))
    assert sum(row["nivel_resultante"] == "v1" for row in prioridad) == 54
    assert sum(row["nivel_resultante"] == "v2" for row in prioridad) == 5
    assert sum(row["nivel_resultante"] == "v3" for row in prioridad) == 2
    assert prioridad[0]["hitos_reconocidos_en_polo"] == "1"


def test_prosa_y_privacidad() -> None:
    informe = (OUT / "INFORME.md").read_text(encoding="utf-8")
    assert not re.search(r"\b(barrido|ronda)\b", informe, flags=re.IGNORECASE)
    auditables = [
        OUT / "densidad_y_continuidad_41.csv",
        OUT / "hitos_fuera_de_todo_polo.csv",
        OUT / "conflictos_direccion.csv",
        OUT / "verificacion_locales_sin_catalogo.csv",
        OUT / "vigencia_historicos_priorizados.csv",
        BASE / "hitos" / "hitos_capa_2026.geojson",
        OUT / "INFORME.md",
    ]
    for path in auditables:
        text = path.read_text(encoding="utf-8-sig")
        assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
        assert "+54" not in text
        assert not re.search(r"(?i)(api[_-]?key|secret[_-]?key|bearer\s+[a-z0-9._-]+)", text)
        if path.suffix == ".csv":
            assert not re.search(r"(?i)(^|,)(telefono|teléfono|correo|email)(,|$)", text.splitlines()[0])


if __name__ == "__main__":
    tests = [
        test_densidad_continuidad,
        test_capa_normalizada,
        test_hitos_fuera_y_conflictos,
        test_verificaciones_y_prioridad,
        test_prosa_y_privacidad,
    ]
    for test in tests:
        test()
        print(f"OK {test.__name__}")
