from __future__ import annotations

import argparse
import asyncio
import json

from common import BLOCKED_HOSTS, validate_public_url


async def run(args: argparse.Namespace) -> None:
    host = validate_public_url(args.url, args.allow_host)
    from browser_use import BrowserSession

    session = BrowserSession(
        is_local=True,
        headless=True,
        allowed_domains=[host],
        prohibited_domains=sorted(BLOCKED_HOSTS),
        keep_alive=False,
        enable_default_extensions=False,
    )
    try:
        await session.start()
        await session.navigate_to(args.url)
        title = await session.get_current_page_title()
        current_url = await session.get_current_page_url()
        state = await session.get_state_as_text()
        print(json.dumps({"ok": True, "title": title, "url": current_url, "state_chars": len(state)}))
    finally:
        await session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Browser-Use sin cookies para un host autorizado")
    parser.add_argument("--url", required=True)
    parser.add_argument("--allow-host", action="append", default=[], required=True)
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
