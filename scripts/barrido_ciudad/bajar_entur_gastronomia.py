"""El dataset de gastronomía del Ente de Turismo, bajado desde el repositorio.

POR QUÉ LO BAJA ESTE SCRIPT Y NO UN AGENTE WEB
------------------------------------------------
`data.buenosaires.gob.ar` devolvió robots y 500 en dos rondas desde afuera, incluida la API CKAN.
Desde acá sale limpio. Es **dato abierto y redistribuible** —CC-BY-2.5-AR—, así que no hay nada
que pedir: se baja, se guarda el crudo tal como vino, y el análisis se hace desde el disco.

LO PRIMERO QUE HAY QUE MIRAR, Y NO ES EL CONTENIDO
---------------------------------------------------
El catálogo dice «actualizado el 22/07/2026». Ese es el `metadata_modified` **del registro**, no
de los archivos. Cada recurso trae su propio `last_modified`, y el script los imprime al lado del
del dataset justamente para que la diferencia no pase inadvertida: una fuente vieja presentada
como nueva es la clase de error que después se cita.

Se guarda el JSON completo del `package_show`, los archivos crudos tal como vinieron, y un perfil
de columnas de cada tabla. **Google Places: 0 requests.**

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/bajar_entur_gastronomia.py
"""
from __future__ import annotations

import io
import json
import sys
import warnings
from pathlib import Path

import pandas as pd
import requests

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
OUT = BARRIDO / "entur"
CRUDOS = OUT / "crudos"

CKAN = "https://data.buenosaires.gob.ar/api/3/action/package_show"
DATASET = "oferta-establecimientos-gastronomicos"
CABECERAS = {"User-Agent": "DataGastro/1.0 (DGDGAS, GCBA; consumo de dato abierto)"}
FORMATOS = {"CSV", "GeoJSON"}       # los que se leen acá; el resto se registra sin bajar

# Guardrail 7: el dataset trae teléfono y mail de cada establecimiento. Son de un dataset abierto
# y son de comercios, no de personas, pero la regla nombra «emails» y «teléfonos» sin hacer esa
# distinción y no se la vamos a hacer nosotros. Los crudos quedan en disco y fuera de Git; lo que
# se versiona es la tabla derivada, sin estas columnas, y el perfil con el ejemplo tapado.
COLUMNAS_CONTACTO = {"telefono", "email", "mail", "facebook", "web"}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    CRUDOS.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()

    def p(*args_):
        print(*args_, file=buffer)

    respuesta = requests.get(CKAN, params={"id": DATASET}, timeout=60, headers=CABECERAS)
    respuesta.raise_for_status()
    paquete = respuesta.json()["result"]
    (OUT / "package_show.json").write_text(
        json.dumps(paquete, ensure_ascii=False, indent=1), encoding="utf-8")

    p("ENTE DE TURISMO · «Oferta y Establecimientos gastronómicos» · bajado desde el repositorio")
    p("=" * 100)
    p("")
    p(f"  título:     {paquete.get('title')}")
    p(f"  licencia:   {paquete.get('license_title')}  → redistribuible")
    p(f"  organismo:  {paquete.get('organization', {}).get('title')}")
    p(f"  metadata_modified del DATASET: {paquete.get('metadata_modified')}")
    p("")

    p("-" * 100)
    p("  LA FECHA DEL REGISTRO NO ES LA FECHA DE LOS ARCHIVOS")
    p("")
    p(f"      {'formato':<10}{'last_modified del recurso':<30}recurso")
    for recurso in paquete["resources"]:
        fecha = recurso.get("last_modified") or recurso.get("created") or "—"
        p(f"      {recurso['format']:<10}{fecha:<30}{recurso['name']}")
    fechas = {(r.get("last_modified") or r.get("created") or "")[:4]
              for r in paquete["resources"]}
    p("")
    p(f"      años de los archivos: {sorted(a for a in fechas if a)}")
    p(f"      año del registro:     {str(paquete.get('metadata_modified'))[:4]}")
    p("")

    filas_perfil = []
    for recurso in paquete["resources"]:
        if recurso["format"] not in FORMATOS:
            p(f"      {recurso['format']}: registrado y no bajado (ZIP/XLSX duplican al CSV)")
            continue
        destino = CRUDOS / Path(recurso["url"]).name
        contenido = requests.get(recurso["url"], timeout=180, headers=CABECERAS)
        contenido.raise_for_status()
        destino.write_bytes(contenido.content)
        p(f"      bajado: {destino.name}  ({len(contenido.content):,} bytes)")

        if destino.suffix == ".csv":
            # El CSV no viene en UTF-8: trae bytes 0xBA (º) de latin-1. Se prueba en orden y se
            # anota cuál entró, porque leerlo mal produce mojibake que después parece dato —el
            # error que este proyecto ya cazó tres veces—.
            tabla = None
            for codificacion in ("utf-8", "utf-8-sig", "latin-1"):
                try:
                    tabla = pd.read_csv(destino, sep=None, engine="python",
                                        encoding=codificacion, on_bad_lines="skip")
                    p(f"          codificación: {codificacion}")
                    break
                except UnicodeDecodeError:
                    continue
            if tabla is None:
                p("          CORTE: no se pudo decodificar el CSV con ninguna codificación")
                continue
        else:
            import geopandas as gpd
            tabla = gpd.read_file(destino)
        for columna in tabla.columns:
            serie = tabla[columna]
            contacto = columna.lower() in COLUMNAS_CONTACTO
            filas_perfil.append({
                "recurso": destino.name, "columna": columna, "tipo": str(serie.dtype),
                "no_nulos": int(serie.notna().sum()), "filas": len(tabla),
                "distintos": int(serie.nunique(dropna=True)),
                "ejemplo": "[columna de contacto · no se transcribe]" if contacto else (
                    str(serie.dropna().iloc[0])[:60] if serie.notna().any() else ""),
            })
        p(f"          {len(tabla):,} filas × {len(tabla.columns)} columnas")

        publicable = tabla[[c for c in tabla.columns if c.lower() not in COLUMNAS_CONTACTO]]
        if destino.suffix == ".geojson":
            publicable.to_file(OUT / f"{destino.stem}_sin_contacto.geojson", driver="GeoJSON")
        else:
            publicable.to_csv(OUT / f"{destino.stem}_sin_contacto.csv",
                              index=False, encoding="utf-8")
        quitadas = len(tabla.columns) - len(publicable.columns)
        p(f"          derivada sin contacto: {len(publicable.columns)} columnas "
          f"({quitadas} quitadas por guardrail 7)")

    perfil = pd.DataFrame(filas_perfil)
    perfil.to_csv(OUT / "perfil_columnas_entur.csv", index=False, encoding="utf-8")

    p("")
    p("-" * 100)
    p("  QUÉ TRAE CADA TABLA")
    p("")
    for recurso, grupo in perfil.groupby("recurso"):
        p(f"      {recurso} — {grupo.filas.iloc[0]:,} filas")
        for fila in grupo.itertuples():
            p(f"          {fila.columna:<26}{fila.no_nulos:>7} no nulos  "
              f"{fila.distintos:>6} distintos   {fila.ejemplo}")
        p("")

    # ------------------------------------------------------------------ contra la base
    oferta = CRUDOS / "oferta-gastronomica.geojson"
    if oferta.exists():
        import geopandas as gpd
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from polos_soporte import CRS_METRICO, envolventes_22, puntos_base  # noqa: E402

        entur = gpd.read_file(oferta).to_crs(CRS_METRICO)
        base = puntos_base()
        envolventes = envolventes_22()
        dentro_entur = gpd.sjoin(entur, envolventes[["referencia_id", "geometry"]],
                                 predicate="within", how="inner")
        dentro_base = gpd.sjoin(base[["local_id", "geometry"]],
                                envolventes[["referencia_id", "geometry"]],
                                predicate="within", how="inner")
        p("-" * 100)
        p("  CONTRA LA BASE · ¿puede esta fuente resolver la vía A «por conteo real»?")
        p("")
        p(f"      ENTUR (2019):        {len(entur):,} puntos en toda la Ciudad")
        p(f"      base del barrido:    {len(base):,} puntos del anillo núcleo")
        p(f"      razón ENTUR/base:    {len(entur) / len(base):.2f}")
        p("")
        p(f"      {'id':<5}{'zona':<32}{'ENTUR':>8}{'base':>8}{'razón':>8}")
        conteo_entur = dentro_entur.referencia_id.value_counts()
        conteo_base = dentro_base.referencia_id.value_counts()
        for referencia in envolventes.referencia_id:
            nombre = envolventes.loc[envolventes.referencia_id == referencia, "nombre"].iloc[0]
            a, b = int(conteo_entur.get(referencia, 0)), int(conteo_base.get(referencia, 0))
            razon = f"{a / b:.2f}" if b else "—"
            p(f"      {referencia:<5}{nombre[:31]:<32}{a:>8}{b:>8}{razon:>8}")
        p("")
        pd.DataFrame({"referencia_id": envolventes.referencia_id,
                      "entur_2019": [int(conteo_entur.get(r, 0))
                                     for r in envolventes.referencia_id],
                      "base_2026": [int(conteo_base.get(r, 0))
                                    for r in envolventes.referencia_id]}).to_csv(
            OUT / "entur_contra_base_22_zonas.csv", index=False, encoding="utf-8")

    p("=" * 100)
    p(f"  crudos en {CRUDOS.relative_to(ROOT)} · perfil en perfil_columnas_entur.csv · "
      "Google Places: 0 requests")
    p("=" * 100)
    p("")

    (OUT / "ENTUR.txt").write_text(buffer.getvalue(), encoding="utf-8")
    print(buffer.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
