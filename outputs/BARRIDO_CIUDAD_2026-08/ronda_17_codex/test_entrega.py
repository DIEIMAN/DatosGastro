# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

import pandas as pd


OUT = Path(__file__).resolve().parent
BASE = OUT.parent
EVIDENCIA = BASE / "desde_cowork" / "evidencia_2026"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ancho_estable(path: Path) -> tuple[int, int]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        filas = list(csv.reader(fh))
    if not filas:
        return 0, 0
    ancho = len(filas[0])
    malas = sum(len(f) != ancho for f in filas[1:])
    return ancho, malas


class EntregaTests(unittest.TestCase):
    def test_n_vias_derivadas_y_categoria_estable(self):
        fichas = pd.read_csv(OUT / "fichas_corpus_polos.csv", dtype=str).fillna("").set_index("polo_id")
        audit = pd.read_csv(OUT / "auditoria_n_vias.csv", dtype=str).set_index("polo_id")
        esperados = {"R02": 4, "R04": 4, "R05": 5, "R19": 4, "Z37": 5}
        for pid, esperado in esperados.items():
            self.assertEqual(int(fichas.loc[pid, "n_vias"]), esperado)
            self.assertEqual(int(audit.loc[pid, "n_vias_recalculado"]), esperado)
            self.assertEqual(audit.loc[pid, "cambio_categoria"], "NO")

    def test_ancho_de_todos_los_csv_y_r03(self):
        archivos = list(EVIDENCIA.glob("*.csv")) + list(OUT.glob("*.csv"))
        self.assertGreaterEqual(len(list(EVIDENCIA.glob("*.csv"))), 72)
        errores = [(p.name, ancho_estable(p)) for p in archivos if ancho_estable(p)[1]]
        self.assertEqual(errores, [])
        r03 = pd.read_csv(OUT / "via_E_22_referencias.csv", dtype=str).query("referencia_id == 'R03'")
        self.assertEqual(len(r03), 1)
        self.assertTrue(r03.iloc[0]["via_E_advertencia"].strip())
        self.assertTrue(r03.iloc[0]["via_E_rutas_n"].strip())
        self.assertRegex(r03.iloc[0]["fecha_relevamiento"], r"^\d{4}-\d{2}-\d{2}$")

    def test_nueve_fallas_de_calles_y_control_olimpo(self):
        audit = pd.read_csv(OUT / "auditoria_normalizador_calles.csv")
        self.assertEqual(len(audit), 9)
        self.assertEqual(
            audit.tipo_de_falla.value_counts().to_dict(),
            {"calle con dos nombres": 4, "abreviatura no contemplada": 3, "altura fuera de rango": 2},
        )
        self.assertTrue(audit.conteo_conservado.eq("SI").all())
        olimpo = pd.read_csv(OUT / "control_cafe_olimpo.csv").iloc[0]
        self.assertEqual(olimpo.barrio_resultado, "Monte Castro")
        self.assertEqual(int(olimpo.comuna_resultado), 10)
        self.assertEqual(olimpo.resultado_test, "OK")

    def test_diez_cruces_resueltos_con_fuente_publica(self):
        df = pd.read_csv(OUT / "requiere_cruce_10.csv")
        self.assertEqual(len(df), 10)
        self.assertTrue(df.estado.eq("RESUELTO").all())
        self.assertFalse(df.astype(str).apply(lambda c: c.str.contains("pendiente", case=False)).any().any())
        self.assertEqual(df.via_E_abierta.value_counts().to_dict(), {"no": 7, "si": 3})
        self.assertTrue(df.fuente_publica.str.contains("pública", case=False).all())
        self.assertTrue(df.fuente_no_publica.str.startswith("puerta cerrada").all())

    def test_vigencia_90_reconcilia_y_expira(self):
        df = pd.read_csv(OUT / "vigencia_90_hitos.csv", dtype=str).fillna("")
        self.assertEqual(len(df), 90)
        self.assertEqual(df.estado.eq("cerrado").sum(), 2)
        self.assertEqual(df.estado.ne("cerrado").sum(), 88)
        self.assertEqual(set(df.nivel_de_verificacion), {"v1", "v2", "v3"})
        dias = pd.to_numeric(df.dias_desde_verificacion)
        self.assertEqual((dias > 90).sum(), 10)
        vencidas = df.loc[dias > 90]
        self.assertTrue(
            (
                vencidas["accion"].str.startswith("revisar")
                | vencidas["estado"].eq("cerrado")
            ).all()
        )
        buzon = df[df.nombre == "El Buzón"].iloc[0]
        self.assertEqual(buzon.direccion_adoptada, "Esquiú 1393")
        self.assertIn("Esquiú y Centenera", buzon.direcciones_alternativas)
        self.assertIn("Esquiú y Tabaré", buzon.direcciones_alternativas)
        olimpo = df[df.nombre.str.casefold() == "bar olimpo"].iloc[0]
        self.assertEqual(olimpo.barrio, "Monte Castro")

    def test_listas_separadas_y_correccion_oficial(self):
        cerrados = pd.read_csv(OUT / "cerrados.csv")
        recuperados = pd.read_csv(OUT / "interrumpidos_recuperados.csv")
        correcciones = pd.read_csv(OUT / "correcciones_catalogo_oficial.csv")
        self.assertEqual(set(cerrados.nombre.str.casefold()), {"plaza bar", "la buena medida"})
        self.assertNotIn("el obrero", set(cerrados.nombre.str.casefold()))
        self.assertIn("el obrero", set(recuperados.nombre.str.casefold()))
        plaza = correcciones[correcciones.nombre.str.casefold() == "plaza bar"].iloc[0]
        self.assertEqual(plaza.fecha_del_cierre, "2017-04-29")
        self.assertEqual(int(plaza.orden_catalogo), 84)

    def test_puentecito_prudente(self):
        fila = pd.read_csv(OUT / "el_puentecito.csv").iloc[0]
        self.assertEqual(fila.estado, "probablemente_abierto")
        self.assertNotEqual(fila.estado, "verificado_abierto")
        self.assertEqual(fila.fecha, "2026-07-07")
        self.assertIn("Los Laureles", fila.resultado_alerta)

    def test_correspondencia_y_metadatos(self):
        df = pd.read_csv(OUT / "correspondencia_124_x_41.csv")
        resumen = json.loads((OUT / "correspondencia_resumen.json").read_text(encoding="utf-8"))
        inter = df[df.fila_tipo == "INTERSECCION"]
        self.assertEqual(df.concentracion_id.nunique(), 124)
        self.assertEqual(len(inter), 143)
        self.assertEqual((inter.bloque == "PUBLICABLE").sum(), 95)
        self.assertEqual((inter.bloque == "ESPERA_BORDE").sum(), 48)
        self.assertTrue(inter.loc[inter.bloque == "ESPERA_BORDE", "atribuible"].eq("NO").all())
        self.assertEqual(resumen["umbral_interseccion_m2"], 0.01)
        excluidos = pd.read_csv(OUT / "contactos_excluidos_umbral.csv")
        self.assertEqual(len(excluidos), resumen["contactos_excluidos_por_umbral"])
        self.assertTrue(excluidos.interseccion_m2.le(0.01).all())
        self.assertIsNone(resumen["tope_de_filas"])

    def test_idempotencia(self):
        productos = sorted(p for p in OUT.iterdir() if p.suffix in {".csv", ".json"})
        antes = {p.name: digest(p) for p in productos}
        subprocess.run([sys.executable, str(OUT / "generar_entrega.py")], check=True, cwd=OUT.parents[2])
        subprocess.run([sys.executable, str(OUT / "generar_correspondencia.py")], check=True, cwd=OUT.parents[2])
        despues = {p.name: digest(p) for p in productos}
        self.assertEqual(antes, despues)

    def test_qa_privacidad_y_prosa(self):
        textos = []
        for p in OUT.iterdir():
            if p.suffix.lower() in {".csv", ".json", ".md"}:
                textos.append(p.read_text(encoding="utf-8-sig"))
        corpus = "\n".join(textos)
        self.assertNotRegex(corpus, r"(?i)[\w.+-]+@[\w.-]+\.[a-z]{2,}")
        self.assertNotRegex(corpus, r"(?i)place[_ -]?id|api[_ -]?key")
        self.assertNotIn("diego", corpus.casefold())
        informe = (OUT / "INFORME.md").read_text(encoding="utf-8").casefold()
        self.assertNotRegex(informe, r"\bbarrido\b")
        self.assertNotRegex(informe, r"\bronda\b")


if __name__ == "__main__":
    unittest.main(verbosity=2)
