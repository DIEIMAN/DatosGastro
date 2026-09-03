from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import reject_sensitive_text, safe_identifier


READ_ONLY = re.compile(r"^\s*(SELECT|WITH)\b", re.I)
FORBIDDEN = re.compile(r"\b(INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|COPY|EXPORT|IMPORT|ATTACH|DETACH|CALL|INSTALL|LOAD)\b", re.I)


def main() -> None:
    parser = argparse.ArgumentParser(description="Consulta DuckDB local y de solo lectura")
    parser.add_argument("--sql", required=True)
    parser.add_argument("--csv", action="append", default=[], metavar="ALIAS=PATH")
    parser.add_argument("--parquet", action="append", default=[], metavar="ALIAS=PATH")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()
    if not READ_ONLY.search(args.sql) or FORBIDDEN.search(args.sql):
        raise ValueError("Solo se permiten SELECT/WITH; DDL, DML, COPY, ATTACH e INSTALL están bloqueados")
    if not 1 <= args.limit <= 1000:
        raise ValueError("--limit debe estar entre 1 y 1000")
    import duckdb

    con = duckdb.connect(":memory:")
    for kind, specs in (("csv", args.csv), ("parquet", args.parquet)):
        for spec in specs:
            alias, separator, raw_path = spec.partition("=")
            if not separator:
                raise ValueError(f"Registro inválido: {spec}; usar ALIAS=PATH")
            alias = safe_identifier(alias)
            path = Path(raw_path).resolve()
            if not path.is_file():
                raise FileNotFoundError(path)
            relation = con.read_csv(str(path)) if kind == "csv" else con.read_parquet(str(path))
            relation.create_view(alias)
    cursor = con.execute(f"SELECT * FROM ({args.sql.rstrip(';')}) AS q LIMIT {args.limit}")
    columns = [item[0] for item in cursor.description]
    rows = cursor.fetchall()
    payload = [dict(zip(columns, row, strict=True)) for row in rows]
    serialized = json.dumps(payload, ensure_ascii=False, default=str)
    reject_sensitive_text(serialized, "resultado SQL")
    print(serialized)


if __name__ == "__main__":
    main()
