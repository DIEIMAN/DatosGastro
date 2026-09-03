---
name: chromadb-rag
description: >
  Memoria vectorial local con ChromaDB para búsqueda semántica sobre textos del
  proyecto (descripciones de locales, cartas, notas de prensa ya recolectadas).
  Usar cuando haya que indexar y consultar por similitud un corpus de textos.
  Corre 100 % local (embeddings por defecto ONNX, sin API).
---

# ChromaDB — búsqueda vectorial local

Instalado en `.venv-tools`. Ejecutar con `.venv-tools\Scripts\python.exe`.

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

## Reglas DataGastro

1. Metadatos obligatorios por documento: `fuente` (código F/I/E) y `fecha` de
   captura. No mezclar universos en una colección sin ese campo (guardrail 3).
2. Corpus con datos internos/sensibles → persistir SOLO bajo
   `outputs/analisis_interno/` o carpeta ignorada por Git (guardrail 8).
3. No indexar datos personales (teléfonos, emails, CUIT) — guardrail 7.
4. Un resultado de similitud es una hipótesis, no un match confirmado: para
   vinculación de registros usar la skill `dedupe-registros`.
