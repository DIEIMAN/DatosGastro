---
name: browser-use
description: >
  Automatización de navegador con agente LLM (browser-use + Playwright) para
  sitios y plataformas dinámicas que Crawl4AI no puede leer (contenido cargado
  por JS con interacción). Requiere API key de LLM. Usar también para muestras
  controladas de Google Maps, delivery, reservas y redes cuando la tarea esté
  autorizada y el resultado quede como evidencia externa no canónica.
---

# Browser-Use — navegación automatizada de sitios públicos

Instalado en `.venv-tools` con Playwright/Chromium. Ejecutar con
`.venv-tools\Scripts\python.exe`.

## Uso básico

```python
import asyncio
from browser_use import Agent, ChatAnthropic

async def main():
    agent = Agent(
        task="Abrir https://ejemplo.com y listar los locales gastronómicos publicados",
        llm=ChatAnthropic(model="claude-sonnet-5"),
    )
    await agent.run()

asyncio.run(main())
```

API key vía `$env:ANTHROPIC_API_KEY` (nunca hardcodeada ni commiteada).

## Reglas DataGastro (obligatorias)

1. Declarar el host, objetivo, campos y tope de páginas/locales antes de ejecutar.
2. No eludir login, CAPTCHA, paywall ni controles. No guardar credenciales o cookies. Una sesión
   iniciada por el usuario requiere autorización puntual y solo lectura.
3. Solo lectura: no enviar formularios, no crear cuentas, no interactuar con
   contenido ajeno.
4. No recolectar datos de personas. Guardar URL, fecha y método; marcar el resultado
   `EVIDENCIA_EXTERNA_NO_CANONICA`.
5. Cada corrida consume tokens del LLM; avisar antes de tareas largas.
