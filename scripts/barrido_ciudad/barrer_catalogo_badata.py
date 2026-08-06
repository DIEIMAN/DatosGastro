"""Barrido del catálogo entero de BA Data por API CKAN: qué fuentes hay que la búsqueda no muestra.

POR QUÉ UN BARRIDO Y NO UNA BÚSQUEDA
------------------------------------
Buscar «gastronomía» en el portal devuelve los datasets que se llaman así. El padrón de permisos
de venta de alimentos en el espacio público no se llama así, y es lo más cercano a un registro de
puestos callejeros y food trucks que existe. Los datasets útiles rara vez tienen el nombre que uno
busca.

El barrido recorre los 453 datasets del catálogo, mira **los nombres de columna de cada recurso**
—que CKAN publica en `attributesDescription`— y ordena por dos ejes que son los que deciden si una
fuente sirve para esta base:

  1. **¿tiene dónde?** columnas de coordenada o de dirección. Sin eso no entra a una base
     territorial, por interesante que sea el contenido;
  2. **¿tiene qué?** vocabulario gastronómico o de local comercial en el título, la descripción o
     los nombres de columna.

Y marca un tercer eje que no ordena pero condiciona: **columnas con datos personales**. Un dataset
con `titular`, `DNI_CUIT` o `nro_documento` se puede usar, pero esas columnas no se abren nunca
—se declara la lista permitida y el `usecols` de pandas se arma desde ahí, igual que en
`detectar_lotes_permisos.py`—. Marcarlo acá evita que alguien lo descubra después de haberlo
cargado entero en memoria.

LO QUE ESTE SCRIPT NO HACE
--------------------------
No baja ningún recurso ni decide que ninguna fuente entre al proyecto. Produce un inventario
ordenado; qué se baja y qué queda en el roadmap se decide leyéndolo, con la ficha de fuente de
`docs/skills_claude/02_metodologia_fuentes.md`.

USO
---
  python scripts/barrido_ciudad/barrer_catalogo_badata.py            # barre y publica el inventario
  python scripts/barrido_ciudad/barrer_catalogo_badata.py --reinformar  # rehace desde el crudo
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
GEN = BARRIDO / "generado"
CATALOGO_DIR = ROOT / "outputs" / "fuentes_externas" / "badata_catalogo"
CRUDO = CATALOGO_DIR / "badata_paquetes.json"

API = "https://data.buenosaires.gob.ar/api/3/action"
USER_AGENT = "DataGastro/barrido-ciudad (DGDGAS, uso institucional CABA)"
PAGINA = 50
PAUSA_S = 1.0

# --- Los tres ejes, como listas declaradas ------------------------------------------------
COLUMNAS_COORDENADA = [
    "lat", "latitud", "latitude", "lon", "long", "longitud", "longitude",
    "x", "y", "coord", "geom", "wkt", "punto", "the_geom",
]
COLUMNAS_DIRECCION = [
    "direccion", "domicilio", "calle", "altura", "puerta", "ubicacion", "nombre_calle",
    "calle_nombre", "calle_altura", "smp", "manzana", "parcela", "catastro",
]
PALABRAS_GASTRO = [
    "gastronom", "restaurant", "bar ", "bares", "cafe", "confiteria", "pizzer", "parrilla",
    "heladeria", "panaderia", "alimento", "bebida", "comida", "feria", "mercado", "food",
    "cerveceria", "vino", "bodegon", "delivery", "bailable", "boliche", "nocturn",
]
PALABRAS_LOCAL = [
    "comercio", "local", "habilitacion", "permiso", "establecimiento", "empresa", "pyme",
    "negocio", "rubro", "actividad economica", "fiscalizacion", "inspeccion", "clausura",
    "espacio cultural", "cultural",
]
COLUMNAS_SENSIBLES = [
    "cuit", "cuil", "dni", "documento", "titular", "telefono", "celular", "mail", "email",
    "contacto", "apellido", "razon_social", "razonsocial", "nombre_titular",
]


def plegar(texto: object) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()


def pedir(ruta: str) -> dict:
    pedido = urllib.request.Request(f"{API}/{ruta}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(pedido, timeout=120) as respuesta:  # noqa: S310
        return json.loads(respuesta.read().decode("utf-8"))


def bajar_catalogo() -> list[dict]:
    """Los paquetes con sus recursos, de a página. Es una API pública y se la trata como tal."""
    paquetes, desplazamiento = [], 0
    while True:
        consulta = urllib.parse.urlencode({"limit": PAGINA, "offset": desplazamiento})
        pagina = pedir(f"current_package_list_with_resources?{consulta}")["result"]
        if not pagina:
            break
        paquetes.extend(pagina)
        print(f"  {len(paquetes)} paquetes...")
        desplazamiento += PAGINA
        time.sleep(PAUSA_S)
    return paquetes


# --------------------------------------------------------------------------- análisis

def columnas_de(recurso: dict) -> list[str]:
    """Nombres de columna que CKAN publica para el recurso, si los publica."""
    crudo = recurso.get("attributesDescription")
    if not crudo:
        return []
    try:
        atributos = json.loads(crudo) if isinstance(crudo, str) else crudo
    except ValueError:
        return []
    if not isinstance(atributos, list):
        return []
    return [plegar(a.get("title", "")) for a in atributos if isinstance(a, dict)]


def _alguna(candidatos: list[str], agujas: list[str]) -> list[str]:
    return sorted({a for a in agujas for c in candidatos if a in c})


def analizar(paquete: dict) -> dict:
    titulo = paquete.get("title", "")
    notas = paquete.get("notes", "") or ""
    texto = plegar(f"{titulo} {notas} {paquete.get('name', '')}")
    recursos = paquete.get("resources", [])

    columnas: list[str] = []
    formatos: set[str] = set()
    for recurso in recursos:
        columnas.extend(columnas_de(recurso))
        formatos.add((recurso.get("format") or "").upper())
    columnas = sorted(set(columnas))

    coordenada = _alguna(columnas, COLUMNAS_COORDENADA)
    # `x` e `y` como nombre entero de columna, no como subcadena: `sexo` contiene una `x`.
    coordenada = [c for c in coordenada if c not in ("x", "y")] + \
                 [c for c in ("x", "y") if c in columnas]
    direccion = _alguna(columnas, COLUMNAS_DIRECCION)
    sensibles = _alguna(columnas, COLUMNAS_SENSIBLES)
    gastro = sorted({p.strip() for p in PALABRAS_GASTRO
                     if p in texto or any(p in c for c in columnas)})
    local = sorted({p for p in PALABRAS_LOCAL if p in texto or any(p in c for c in columnas)})

    geo = bool(coordenada) or bool(direccion) or bool(formatos & {"GEOJSON", "SHP", "KML", "KMZ"})
    puntaje = (
        3 * len(gastro) + len(local)
        + (4 if coordenada else 0) + (2 if direccion else 0)
        + (2 if formatos & {"GEOJSON", "SHP", "KML"} else 0)
    )

    return {
        "id": paquete.get("name", ""),
        "titulo": titulo,
        "organismo": (paquete.get("organization") or {}).get("title", ""),
        "licencia": paquete.get("license_title") or paquete.get("license_id") or "",
        "actualizado": (paquete.get("metadata_modified") or "")[:10],
        "recursos": len(recursos),
        "formatos": " ".join(sorted(f for f in formatos if f)),
        "tiene_coordenada": bool(coordenada),
        "tiene_direccion": bool(direccion),
        "georreferenciable": geo,
        "palabras_gastro": " ".join(gastro),
        "palabras_local": " ".join(local),
        "columnas_sensibles": " ".join(sensibles),
        "puntaje": puntaje,
        "columnas": " | ".join(columnas[:40]),
        "url_portal": f"https://data.buenosaires.gob.ar/dataset/{paquete.get('name', '')}",
    }


# --------------------------------------------------------------------------- informe

def _envolver(texto: str, ancho: int = 96) -> list[str]:
    lineas, actual = [], ""
    for palabra in texto.split():
        if len(actual) + len(palabra) + 1 > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f"{actual} {palabra}".strip()
    if actual:
        lineas.append(actual)
    return lineas


# Fuentes que el proyecto ya usa o ya tiene inventariadas. Se marcan para que el inventario
# muestre lo NUEVO y no vuelva a proponer lo que ya está trabajado.
YA_EN_EL_PROYECTO = {
    # los identificadores son los de CKAN, verificados contra el catálogo, no supuestos
    "oferta-establecimientos-gastronomicos",   # F01
    "habilitaciones-aprobadas",                # F02
    "ferias-mercados",                         # F03
    "relevamiento-usos-suelo",                 # Relevamiento de Usos del Suelo
    "mapa-oportunidades-comerciales-moc",      # MOC, perfilado y descartado para vigencia
    "permisos-uso-espacio-publico-area-gastronomica",
    "venta-de-alimentos",
    "locales-bailables",
    "espacios-culturales",
}


def informar(tabla: pd.DataFrame) -> tuple[str, dict]:
    salida = io.StringIO()

    def linea(texto: str = "") -> None:
        print(texto, file=salida)

    georreferenciables = tabla[tabla.georreferenciable]
    candidatos = tabla[(tabla.puntaje >= 6) & tabla.georreferenciable]
    nuevos = candidatos[~candidatos.id.isin(YA_EN_EL_PROYECTO)]

    linea("=" * 98)
    linea("BA DATA · BARRIDO DEL CATÁLOGO COMPLETO POR API CKAN")
    linea("=" * 98)
    linea(f"fecha {dt.date.today().isoformat()} · {len(tabla)} datasets · sin bajar ningún recurso")
    linea()

    linea("§1 · QUÉ HAY EN EL CATÁLOGO")
    linea("-" * 98)
    linea(f"  datasets totales                                   : {len(tabla):>5}")
    linea(f"  con columna de coordenada declarada                : {int(tabla.tiene_coordenada.sum()):>5}")
    linea(f"  con columna de dirección declarada                 : {int(tabla.tiene_direccion.sum()):>5}")
    linea(f"  georreferenciables (coordenada, dirección o SIG)   : {len(georreferenciables):>5}")
    linea(f"  con vocabulario gastronómico                       : {int((tabla.palabras_gastro != '').sum()):>5}")
    linea(f"  con columnas de datos personales                   : {int((tabla.columnas_sensibles != '').sum()):>5}")
    linea()
    licencias = tabla.licencia.value_counts()
    linea("  licencias declaradas: " + " · ".join(f"{k or 's/d'} {v}" for k, v in licencias.head(6).items()))
    linea()

    linea("§2 · CANDIDATOS NUEVOS · georreferenciables y con vocabulario del rubro")
    linea("-" * 98)
    if len(nuevos):
        for fila in nuevos.head(25).itertuples():
            linea(f"  [{fila.puntaje:>3}] {fila.titulo[:78]}")
            linea(f"        {fila.id}  ·  {fila.organismo[:44]}  ·  {fila.licencia}")
            marcas = []
            if fila.tiene_coordenada:
                marcas.append("coordenada")
            if fila.tiene_direccion:
                marcas.append("dirección")
            if fila.columnas_sensibles:
                marcas.append(f"DATOS PERSONALES: {fila.columnas_sensibles}")
            linea(f"        {' · '.join(marcas)}")
            if fila.palabras_gastro:
                linea(f"        vocabulario: {fila.palabras_gastro}")
            linea()
    else:
        linea("  Ninguno por encima del umbral. El catálogo ya está inventariado.")
    linea()

    linea("§3 · LO QUE YA ESTÁ EN EL PROYECTO, PARA NO REPETIRLO")
    linea("-" * 98)
    conocidos = tabla[tabla.id.isin(YA_EN_EL_PROYECTO)]
    for fila in conocidos.sort_values("puntaje", ascending=False).itertuples():
        linea(f"  [{fila.puntaje:>3}] {fila.id:<48}{fila.licencia}")
    linea()

    linea("§4 · CÓMO LEER ESTE INVENTARIO")
    linea("-" * 98)
    for texto in _envolver(
        "El puntaje ordena, no decide. Pesa cuatro cosas: vocabulario gastronómico (×3), "
        "vocabulario de local comercial, tener coordenada declarada (+4) y tener dirección (+2). "
        "Un dataset con puntaje alto puede seguir sin servir —una serie mensual por comuna no entra "
        "a una base de locales— y uno con puntaje bajo puede ser clave si su unidad es el local. "
        "La ficha de fuente sigue siendo obligatoria antes de integrar nada."):
        linea(f"  {texto}")
    linea()
    for texto in _envolver(
        "La columna `columnas_sensibles` no baja el puntaje: marca. Un padrón de permisos con "
        "`titular` y `DNI_CUIT` es una fuente legítima y hay que usarla; lo que no se hace es "
        "abrir esas columnas. La lista permitida se declara en el script que la lee y el `usecols` "
        "de pandas se arma desde esa lista, de modo que lo prohibido no entra en memoria."):
        linea(f"  {texto}")
    linea()
    linea("=" * 98)

    resumen = {
        "fecha_calculo": dt.date.today().isoformat(),
        "datasets": int(len(tabla)),
        "georreferenciables": int(len(georreferenciables)),
        "con_coordenada": int(tabla.tiene_coordenada.sum()),
        "con_direccion": int(tabla.tiene_direccion.sum()),
        "con_vocabulario_gastro": int((tabla.palabras_gastro != "").sum()),
        "con_columnas_sensibles": int((tabla.columnas_sensibles != "").sum()),
        "candidatos": int(len(candidatos)),
        "candidatos_nuevos": nuevos.id.tolist(),
    }
    return salida.getvalue(), resumen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reinformar", action="store_true",
                        help="rehace el inventario desde el crudo en disco, sin red")
    args = parser.parse_args()

    if args.reinformar:
        if not CRUDO.exists():
            raise SystemExit(f"ABORTADO: falta {CRUDO.relative_to(ROOT)}.")
        paquetes = json.loads(CRUDO.read_text(encoding="utf-8"))
    else:
        print("[barrido] catálogo de BA Data por API CKAN...")
        paquetes = bajar_catalogo()
        CATALOGO_DIR.mkdir(parents=True, exist_ok=True)
        CRUDO.write_text(json.dumps(paquetes, ensure_ascii=False), encoding="utf-8")
        print(f"  crudo en {CRUDO.relative_to(ROOT)}")

    tabla = pd.DataFrame([analizar(p) for p in paquetes]).sort_values(
        ["puntaje", "titulo"], ascending=[False, True])
    texto, resumen = informar(tabla)
    print(texto)

    GEN.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(GEN / "badata_catalogo_inventario.csv", index=False, encoding="utf-8")
    (GEN / "BADATA_CATALOGO.txt").write_text(texto, encoding="utf-8")
    (GEN / "badata_catalogo_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  publicado en {GEN.relative_to(ROOT)}: badata_catalogo_inventario.csv, "
          "BADATA_CATALOGO.txt, badata_catalogo_resumen.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
