from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from common import reject_sensitive_text, safe_output_path, validate_public_url


def main() -> None:
    parser = argparse.ArgumentParser(description="ScrapeGraph-AI con validación JSON Schema")
    parser.add_argument("--url", required=True)
    parser.add_argument("--allow-host", action="append", default=[], required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="openai/gpt-4o-mini")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    args = parser.parse_args()
    validate_public_url(args.url, args.allow_host)
    reject_sensitive_text(args.prompt, "prompt")
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise RuntimeError(f"Falta la variable de entorno {args.api_key_env}; no guardar claves en el repo")
    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    from jsonschema import validate
    from scrapegraphai.graphs import SmartScraperGraph

    graph = SmartScraperGraph(
        prompt=args.prompt,
        source=args.url,
        config={"llm": {"model": args.model, "api_key": api_key}, "verbose": False, "headless": True},
    )
    result = graph.run()
    validate(instance=result, schema=schema)
    output = safe_output_path(args.output)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(output)}))


if __name__ == "__main__":
    main()
