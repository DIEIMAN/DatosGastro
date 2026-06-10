from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from config import DATA_RAW, OUTPUTS, PROFILE_OUTPUTS, SOURCE_CONFIG

MIN_SIZE_BYTES = 1024


def _pending(url: str | None) -> bool:
    return url is None or str(url).strip() == ""


def _download(url: str) -> requests.Response:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    return response


def download_resource(key: str, source: dict) -> dict:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    output_path = DATA_RAW / source["output_filename"]
    started = datetime.now().isoformat(timespec="seconds")
    url = source.get("download_url")

    row = {
        "key_fuente": key,
        "id_fuente": source.get("id_fuente", key),
        "nombre": source.get("nombre", source.get("name", key)),
        "download_url": url or "",
        "output_path": str(output_path),
        "status": "PENDING",
        "http_status": "",
        "size_bytes": 0,
        "fecha_descarga": started,
        "error": "",
        "observaciones": source.get("limitaciones", ""),
    }

    if _pending(url):
        row["error"] = "download_url pendiente o no publicado"
        return row

    urls_to_try = [url]
    if source.get("download_url_cdn"):
        urls_to_try.append(source["download_url_cdn"])

    last_error = ""
    for candidate_url in urls_to_try:
        try:
            response = _download(candidate_url)
            output_path.write_bytes(response.content)
            size = output_path.stat().st_size
            row["download_url"] = candidate_url
            row["http_status"] = response.status_code
            row["size_bytes"] = size
            if size < MIN_SIZE_BYTES:
                row["status"] = "WARNING"
                row["error"] = "archivo sospechosamente chico (<1 KB)"
            else:
                row["status"] = "OK"
            return row
        except Exception as exc:
            last_error = str(exc)
            row["http_status"] = getattr(getattr(exc, "response", None), "status_code", "")
            continue

    row["status"] = "ERROR"
    row["error"] = last_error
    return row


def run_downloads() -> list[dict]:
    rows = []
    for key, source in SOURCE_CONFIG.items():
        if source.get("formato") not in {"csv", "geojson"}:
            continue
        rows.append(download_resource(key, source))
    return rows


def write_log(rows: list[dict]) -> None:
    PROFILE_OUTPUTS.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(PROFILE_OUTPUTS / "download_log.csv", index=False, encoding="utf-8")
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    with (OUTPUTS / "download_sources.log").open("a", encoding="utf-8") as fh:
        fh.write(f"\n# download_sources {datetime.now().isoformat(timespec='seconds')}\n")
        for row in rows:
            fh.write(
                "{key_fuente}\t{id_fuente}\t{status}\t{size_bytes}\t{output_path}\t{error}\n".format(**row)
            )


def main() -> int:
    rows = run_downloads()
    write_log(rows)
    has_error = False
    for row in rows:
        print(
            f"{row['status']:7s} {row['key_fuente']:16s} {row['size_bytes']:>10} bytes "
            f"{row['output_path']} {row['error']}"
        )
        if row["status"] == "ERROR":
            has_error = True
    print(f"Log CSV: {PROFILE_OUTPUTS / 'download_log.csv'}")
    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
