---
name: crawl4ai
description: >
  Extracción profunda de páginas web públicas a Markdown/JSON apto para LLMs
  (menús, cartas, páginas de locales gastronómicos, notas de prensa). Usar cuando
  haya que leer el contenido completo de una URL públicamente visible con render
  de JavaScript, incluidas muestras autorizadas de directorios, delivery, reservas
  y redes como evidencia externa no canónica.
---

# Crawl4AI — lectura profunda de web pública

Instalado en el venv de herramientas de recolección (NO el venv del pipeline):

```
.venv-tools\Scripts\python.exe
```

## Uso básico (async, Python)

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://ejemplo.com/carta")
        print(result.markdown)

asyncio.run(main())
```

Ejecutar siempre con `.venv-tools\Scripts\python.exe script.py`.

## Extracción estructurada (CSS/JSON schema)

Usar `JsonCssExtractionStrategy` con un schema de selectores cuando la página tiene
estructura repetitiva (listas de platos, precios). Ver docs: https://docs.crawl4ai.com

## Reglas DataGastro (obligatorias)

1. Solo contenido públicamente visible y autorizado para la tarea. No eludir login, CAPTCHA,
   paywall ni controles de acceso.
2. Respetar robots.txt y no hacer ráfagas: una URL por vez, con pausa, caché y tope declarado.
3. No exportar datos personales (teléfonos, emails de contacto individual).
4. Los resultados van a `.agent-tools/` u `outputs/analisis_interno/` con fuente y fecha de
   captura; clasificarlos como `EVIDENCIA_EXTERNA_NO_CANONICA` según la metodología de fuentes.
