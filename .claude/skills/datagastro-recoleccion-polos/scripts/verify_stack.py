from __future__ import annotations

import importlib
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def version(distribution: str) -> str:
    return importlib.metadata.version(distribution)


def check_import(name: str, module: str, distribution: str) -> dict:
    try:
        importlib.import_module(module)
        return {"name": name, "status": "OK", "version": version(distribution)}
    except Exception as exc:
        return {"name": name, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    checks = [
        check_import("Agent Reach", "agent_reach", "agent-reach"),
        check_import("Crawl4AI", "crawl4ai", "Crawl4AI"),
        check_import("ScrapeGraph-AI", "scrapegraphai", "scrapegraphai"),
        check_import("Browser-Use", "browser_use", "browser-use"),
        check_import("OSMnx", "osmnx", "osmnx"),
        check_import("Folium", "folium", "folium"),
        check_import("HDBSCAN", "hdbscan", "hdbscan"),
        check_import("scikit-learn", "sklearn", "scikit-learn"),
        check_import("DuckDB", "duckdb", "duckdb"),
    ]
    try:
        import duckdb

        assert duckdb.connect(":memory:").execute("SELECT 42").fetchone()[0] == 42
        checks.append({"name": "DuckDB query", "status": "OK"})
    except Exception as exc:
        checks.append({"name": "DuckDB query", "status": "FAIL", "error": str(exc)})
    try:
        from common import safe_output_path, validate_public_url

        assert validate_public_url("https://example.com", ["example.com"]) == "example.com"
        for allowed_url, allowed_host in (
            ("https://maps.google.com/", "maps.google.com"),
            ("https://www.rappi.com/", "rappi.com"),
        ):
            validated_host = validate_public_url(allowed_url, [allowed_host])
            assert validated_host == allowed_host or validated_host.endswith("." + allowed_host)
        for blocked_url, allowed_host in (("http://127.0.0.1/", "127.0.0.1"),):
            try:
                validate_public_url(blocked_url, [allowed_host])
            except ValueError:
                continue
            raise AssertionError(f"URL bloqueada aceptada: {blocked_url}")
        try:
            safe_output_path("docs/no_permitido.json")
        except ValueError:
            pass
        else:
            raise AssertionError("Se aceptó una salida fuera de las raíces seguras")
        try:
            validate_public_url("https://example.com", ["otra-fuente.example"])
        except ValueError:
            pass
        else:
            raise AssertionError("Se aceptó un host no declarado con --allow-host")
        checks.append({"name": "Controlled collection wrappers", "status": "OK"})
    except Exception as exc:
        checks.append({"name": "Controlled collection wrappers", "status": "FAIL", "error": str(exc)})
    try:
        import folium

        rendered = folium.Map(location=[-34.61, -58.42], zoom_start=10).get_root().render()
        assert "leaflet" in rendered.lower()
        checks.append({"name": "Folium render", "status": "OK"})
    except Exception as exc:
        checks.append({"name": "Folium render", "status": "FAIL", "error": str(exc)})
    try:
        import hdbscan
        import numpy as np

        points = np.array([[0.0, 0.0], [0.0, 0.001], [1.0, 1.0], [1.0, 1.001]])
        labels = hdbscan.HDBSCAN(min_cluster_size=2).fit_predict(points)
        assert len(labels) == 4
        checks.append({"name": "HDBSCAN synthetic", "status": "OK"})
    except Exception as exc:
        checks.append({"name": "HDBSCAN synthetic", "status": "FAIL", "error": str(exc)})
    chroma_python = ROOT / ".agent-tools" / "chromadb" / ".venv" / "Scripts" / "python.exe"
    chroma_code = (
        "import chromadb; c=chromadb.EphemeralClient(); x=c.create_collection('smoke'); "
        "x.add(ids=['a'], documents=['texto'], embeddings=[[1.0,0.0]]); "
        "r=x.query(query_embeddings=[[1.0,0.0]], n_results=1); assert r['ids'][0][0]=='a'; "
        "print(chromadb.__version__)"
    )
    try:
        result = subprocess.run(
            [str(chroma_python), "-c", chroma_code],
            check=True,
            capture_output=True,
            text=True,
            timeout=90,
        )
        checks.append({"name": "ChromaDB synthetic", "status": "OK", "version": result.stdout.strip()})
    except Exception as exc:
        checks.append({"name": "ChromaDB synthetic", "status": "FAIL", "error": str(exc)})
    try:
        from splink import DuckDBAPI, Linker, SettingsCreator  # noqa: F401

        checks.append({"name": "Record linkage (Splink)", "status": "OK", "version": version("splink")})
    except Exception as exc:
        checks.append({
            "name": "Record linkage (Splink)",
            "status": "FAIL",
            "error": f"{type(exc).__name__}: {exc}",
        })
    print(json.dumps({"python": sys.version.split()[0], "checks": checks}, ensure_ascii=False, indent=2))
    failed = [item for item in checks if item["status"] == "FAIL"]
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
