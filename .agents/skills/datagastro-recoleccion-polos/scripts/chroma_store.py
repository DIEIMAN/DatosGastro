from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from common import reject_sensitive_text, safe_output_path


def hash_embedding(text: str, dimensions: int = 32) -> list[float]:
    data = hashlib.sha256(text.encode("utf-8")).digest()
    return [((data[index % len(data)] / 255.0) * 2.0) - 1.0 for index in range(dimensions)]


def collection_for(args: argparse.Namespace):
    import chromadb

    db_path = safe_output_path(args.db, directory=True)
    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_or_create_collection(args.collection)


def smoke() -> None:
    import chromadb

    client = chromadb.EphemeralClient()
    collection = client.create_collection("smoke")
    collection.add(ids=["uno", "dos"], documents=["café", "restaurante"], embeddings=[[1.0, 0.0], [0.0, 1.0]])
    result = collection.query(query_embeddings=[[1.0, 0.0]], n_results=1)
    if result["ids"][0][0] != "uno":
        raise RuntimeError("ChromaDB no devolvió el vecino esperado")
    print(json.dumps({"ok": True, "mode": "ephemeral-synthetic"}))


def main() -> None:
    parser = argparse.ArgumentParser(description="ChromaDB local con control de privacidad")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("smoke")
    for name in ("add", "query"):
        item = sub.add_parser(name)
        item.add_argument("--db", default=".agent-tools/chromadb/data")
        item.add_argument("--collection", default="polos")
        item.add_argument("--embedding-mode", choices=("default", "hash-test"), default="default")
        if name == "add":
            item.add_argument("--input-jsonl", required=True)
        else:
            item.add_argument("--text", required=True)
            item.add_argument("--n", type=int, default=5)
    args = parser.parse_args()
    if args.command == "smoke":
        smoke()
        return
    collection = collection_for(args)
    if args.command == "add":
        records = [json.loads(line) for line in Path(args.input_jsonl).read_text(encoding="utf-8").splitlines() if line.strip()]
        ids = [str(record["id"]) for record in records]
        documents = [str(record["text"]) for record in records]
        for document in documents:
            reject_sensitive_text(document, "documento vectorial")
        metadatas = [record.get("metadata", {}) for record in records]
        kwargs = {"ids": ids, "documents": documents, "metadatas": metadatas}
        if args.embedding_mode == "hash-test":
            kwargs["embeddings"] = [hash_embedding(document) for document in documents]
        collection.add(**kwargs)
        print(json.dumps({"ok": True, "added": len(ids), "embedding_mode": args.embedding_mode}))
        return
    reject_sensitive_text(args.text, "consulta vectorial")
    kwargs = {"n_results": args.n}
    if args.embedding_mode == "hash-test":
        kwargs["query_embeddings"] = [hash_embedding(args.text)]
    else:
        kwargs["query_texts"] = [args.text]
    result = collection.query(**kwargs)
    print(json.dumps(result, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
