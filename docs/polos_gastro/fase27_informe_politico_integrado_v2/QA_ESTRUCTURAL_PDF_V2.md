# QA estructural — INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2.pdf

Fecha: 2026-07-12. Herramientas: `pdfinfo` (Poppler vía MiKTeX) + PyMuPDF
(`metadatos/QA_ESTRUCTURAL_V2.json`, regenerado en cada corrida del generador).

| Control | Resultado | Detalle |
| --- | --- | --- |
| El PDF abre | APTO | Apertura verificada con pdfinfo y PyMuPDF sin errores de lectura |
| Cantidad de páginas (`pdfinfo`) | APTO | `Pages: 10` |
| Dimensiones consistentes | APTO | 10/10 páginas `595.276 x 841.89 pts (A4)`, rotación 0 |
| Fuentes renderizadas | APTO | Arial / Arial Bold embebidas (subset `AAAAAA+ArialMT`, `AAAAAA+Arial-BoldMT`); Helvetica base |
| Sin páginas en blanco | APTO | Detección por varianza de píxeles: 0 páginas en blanco |
| Sin objetos fuera de página | APTO | 0 bloques de texto fuera del mediabox (tolerancia 2 pt) |
| Sin errores de lectura | APTO | `pdfinfo` sin warnings; PyMuPDF recorre las 10 páginas |
| Texto extraíble | APTO | 10/10 páginas con texto extraíble |
| Encoding | APTO | Acentos, guiones largos y "ñ" correctos en extracción y en render (verificación visual 10/10) |
| Cifrado / JavaScript | APTO | `Encrypted: no`, `JavaScript: no` |

Resultado global: **APTO**.

Nota: los valores dinámicos (hash y bytes del PDF) se registran en
`outputs/polos_gastro/fase27_informe_politico_integrado_v2/CHECKSUMS_SHA256.txt` y en
`metadatos/METADATA_INFORME_POLITICO_INTEGRADO_V2.json` de la corrida final.
