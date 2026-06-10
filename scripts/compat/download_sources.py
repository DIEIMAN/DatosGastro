import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from download_sources import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
