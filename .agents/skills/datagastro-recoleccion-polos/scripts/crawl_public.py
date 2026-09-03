from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone

from common import safe_output_path, validate_public_url


async def run(args: argparse.Namespace) -> None:
    host = validate_public_url(args.url, args.allow_host)
    output_dir = safe_output_path(args.output_dir, directory=True)
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=args.url)
    if not getattr(result, "success", False):
        raise RuntimeError(getattr(result, "error_message", "Crawl4AI no devolvió contenido"))
    markdown = getattr(result, "markdown", "")
    if hasattr(markdown, "raw_markdown"):
        markdown = markdown.raw_markdown
    markdown = str(markdown or "")
    if not markdown.strip():
        raise RuntimeError("El campo markdown llegó vacío")
    (output_dir / "contenido.md").write_text(markdown, encoding="utf-8")
    metadata = {
        "fuente_url": args.url,
        "host_autorizado": host,
        "fecha_consulta_utc": datetime.now(timezone.utc).isoformat(),
        "universo": "E-web-externa",
        "estado": "EVIDENCIA_EXTERNA_NO_CANONICA",
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"ok": True, "output_dir": str(output_dir), "chars": len(markdown)}))


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl4AI para un host público autorizado")
    parser.add_argument("--url", required=True)
    parser.add_argument("--allow-host", action="append", default=[], required=True)
    parser.add_argument("--output-dir", required=True)
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
