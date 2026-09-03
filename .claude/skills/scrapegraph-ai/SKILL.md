---
name: scrapegraph-ai
description: >
  Extracción estructurada de páginas web públicas con esquema definido vía LLM
  (ScrapeGraph-AI). Usar cuando se necesite convertir una página pública en un
  JSON con campos definidos (nombre, dirección, rubro, horarios publicados).
  Requiere una API key de LLM en runtime. Puede usarse sobre plataformas externas
  autorizadas con salida interna y estado de evidencia no canónica.
---

# ScrapeGraph-AI — extracción con esquema vía LLM

Instalado en `.venv-tools` (NO el venv del pipeline). Ejecutar con
`.venv-tools\Scripts\python.exe`.

## Uso básico

```python
from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "api_key": "<ANTHROPIC_API_KEY desde variable de entorno, nunca hardcodeada>",
        "model": "anthropic/claude-sonnet-5",
    },
}

smart = SmartScraperGraph(
    prompt="Extraé nombre, dirección y horarios publicados de cada local listado",
    source="https://ejemplo.com/guia-gastronomica",
    config=graph_config,
)
print(smart.run())
```

## Reglas DataGastro (obligatorias)

1. La API key se toma de una variable de entorno (`$env:ANTHROPIC_API_KEY`);
   nunca se guarda en el repo ni en outputs. No guardar credenciales (guardrail 6).
2. Solo contenido públicamente visible y autorizado; no eludir login, CAPTCHA, paywall ni
   controles de acceso. Declarar esquema y tope antes de correr.
3. Todo dato extraído es "oferta publicada en la web", no "local activo"
   (guardrail 5): declararlo así en cualquier informe.
4. Guardar URL, fecha y método en salida interna; exigir corroboración/revisión humana antes de
   promover datos al Atlas.
5. Costo: cada corrida consume tokens del LLM; avisar antes de corridas masivas.
