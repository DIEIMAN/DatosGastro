# Cierre alternativo - Fase22 como base de oficina

## Estado

- Estado: FASE22 RECUPERADA COMO BASE VISUAL
- Motivo: fase23 presentó regresiones visuales frente a fase22.
- PDF fuente fase22: `outputs/polos_gastro/fase22_microajustes_texto_oficina/INFORME_POLOS_GASTRO_DGDGAS_11P_TEXTO.pdf`
- PDF copiado para entrega: `outputs/polos_gastro/entrega_oficina_fase22_base/INFORME_POLOS_GASTRO_DGDGAS_11P_OFICINA_BASE_FASE22.pdf`
- Fecha: 2026-07-03

## Verificaciones mínimas

- 11 páginas reales: confirmado por `pdfinfo` en el PDF copiado.
- Marca visible correcta DGDGAS — Dirección General de Desarrollo Gastronómico: DGDGAS aparece visible; se conserva el PDF fase22 sin modificaciones. Observación: el render y la extracción textual muestran mojibake en acentos y separador del nombre institucional en fase22 (`DGDGAS ? Direcci?n General de Desarrollo Gastron?mico`), por lo que esta verificación queda con observación si se exige exactitud tipográfica.
- No aparece DataGastro como marca pública: confirmado por búsqueda textual con `pdftotext`.
- No aparece Dirección General de Desarrollo Gastronómico: confirmado por búsqueda textual con `pdftotext`.
- No aparecen marcas internas: Ale, preliminar, borrador, prueba, revisión, documento interno, a validar: confirmado por búsqueda textual con `pdftotext`.
- Mantiene los microajustes textuales de fase22: confirmado en tanto el PDF copiado es idéntico byte a byte al PDF fuente fase22.
- No se tocaron datos fuente: confirmado por alcance de trabajo; solo se creó documentación de cierre, una carpeta de salida y una copia del PDF fase22.
- No se ejecutó API/scraping/Google Places: confirmado.
- No se hizo commit/push/staging: confirmado al cierre por `git diff --cached --name-only` sin resultados.

## Hashes

- SHA256 PDF fase22 fuente: `284627146FA097027126AC4D64880520D0515F4D67AA9183940E98A4B3BD8EAF`
- SHA256 copia de entrega: `284627146FA097027126AC4D64880520D0515F4D67AA9183940E98A4B3BD8EAF`

## Conclusión

Fase22 puede usarse como base visual de oficina mientras no se haga una nueva corrección visual
controlada. La copia de entrega fue creada sin modificar el PDF fuente y conserva 11 páginas. La
observación pendiente es textual/encoding: si la entrega requiere marca institucional exacta con
acentos y separador correctos, debe resolverse en una nueva iteración controlada sobre copia, no
sobre fase23 ni sobre `entrega_oficina_fase23`.
