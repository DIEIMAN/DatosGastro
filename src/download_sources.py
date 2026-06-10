from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests

from config import DATA_RAW, OUTPUTS, PENDING_URL, SOURCE_CONFIG

MIN_SIZE_BYTES = 1024
LOG_PATH = OUTPUTS / "download_sources.log"


def _is_pending_url(url: str | None) -> bool:
    return url is None or str(url).strip() in {"", PENDING_URL, "None"}


def _filename_from_url(url: str, fallback: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    return name or fallback


def download_file(source_id: str, url: str, target_filename: str | None = None) -> dict:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    source = SOURCE_CONFIG[source_id]
    filename = target_filename or _filename_from_url(url, source["target_filename"])
    out_path = DATA_RAW / filename

    response = requests.get(url, timeout=90)
    response.raise_for_status()
    out_path.write_bytes(response.content)
    size = out_path.stat().st_size
    status = "WARNING" if size < MIN_SIZE_BYTES else "OK"
    return {
        "source_id": source_id,
        "status": status,
        "url": url,
        "path": str(out_path),
        "bytes": size,
        "message": "archivo sospechosamente chico" if status == "WARNING" else "descarga completa",
    }


def run_downloads() -> list[dict]:
    results = []
    for source_id, source in SOURCE_CONFIG.items():
        url = source.get("url")
        if _is_pending_url(url):
            results.append(
                {
                    "source_id": source_id,
                    "status": "PENDING",
                    "url": source.get("portal_url", ""),
                    "path": "",
                    "bytes": 0,
                    "message": "falta completar URL directa de recurso en src/config.py",
                }
            )
            continue
        try:
            results.append(download_file(source_id, str(url)))
        except Exception as exc:
            results.append(
                {
                    "source_id": source_id,
                    "status": "ERROR",
                    "url": str(url),
                    "path": "",
                    "bytes": 0,
                    "message": str(exc),
                }
            )
    return results


def write_log(results: list[dict]) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# download_sources {timestamp}\n")
        for result in results:
            fh.write(
                "{source_id}\t{status}\t{bytes}\t{path}\t{url}\t{message}\n".format(**result)
            )


def main() -> int:
    results = run_downloads()
    write_log(results)
    has_error = False
    for result in results:
        print(
            f"{result['status']:7s} {result['source_id']} "
            f"{result['bytes']:>8} bytes {result['path']} {result['message']}"
        )
        if result["status"] == "ERROR":
            has_error = True
    print(f"Log: {LOG_PATH}")
    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
