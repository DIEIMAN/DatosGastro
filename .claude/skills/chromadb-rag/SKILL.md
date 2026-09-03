---
name: chromadb-rag
description: >
  Memoria vectorial local con ChromaDB para búsqueda semántica sobre textos del
  proyecto (descripciones de locales, cartas, notas de prensa ya recolectadas).
  Usar cuando haya que indexar y consultar por similitud un corpus de textos.
  Corre 100 % local (embeddings por defecto ONNX, sin API).
---

# ChromaDB — búsqueda vectorial local

Instalado en un venv propio (sus dependencias chocan con las de `.venv-tools`):
`.agent-tools\chromadb\.venv\Scripts\python.exe` (chromadb 1.5.9). No esta en `.venv` ni en `.venv-tools`.

## Uso básico

```python
import chromadb

client = chromadb.PersistentClient(path="outputs/analisis_interno/chroma")
col = client.get_or_create_collection("polos_textos")

col.add(
    ids=["doc1"],
    documents=["Parrilla tradicional en Boedo con carta de pastas caseras"],
    metadatas=[{"fuente": "web_propia", "fecha": "2026-08-14"}],
)

res = col.query(query_texts=["casas de pastas"], n_results=5)
```

## Reglas propias de la herramienta

1. Metadatos obligatorios por documento: `fuente` (código F/I/E) y `fecha` de
   captura; sin ese campo la colección mezcla universos.
2. La base persistente hereda la sensibilidad del corpus: va a `outputs/analisis_interno/`.
3. Un resultado de similitud es una hipótesis, no un match confirmado: para
   vinculación de registros usar la skill `dedupe-registros`.

Los guardrails generales (3, 7, 8) ya estan cargados desde `CLAUDE.md`; no se repiten aca.
