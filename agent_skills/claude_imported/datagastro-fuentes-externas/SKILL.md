---
name: datagastro-fuentes-externas
description: Reglas por plataforma externa/privada en DataGastro (Google Places, Rappi, PedidosYa, Mercado Pago, Mercado Libre, POS, TheFork, TripAdvisor, redes). Usar al evaluar o preparar integraciones de terceros. NO scraping.
---

# Fuentes externas y privadas

Contenido canónico: `docs/skills_claude/06_fuentes_externas_privadas.md`. Matriz y plantillas en
`docs/fuentes_externas/` y `config/fuentes_externas/`.

Regla central: **no scraping**. Solo APIs oficiales, convenios, datos agregados o
planes/documentación. No ejecutar llamadas pagas sin autorización. No guardar credenciales.

- OSM/Overpass: script exploratorio permitido (abierto, con atribución).
- Google Places: solo plan/diseño de piloto, sin llamar la API.
- Rappi/PedidosYa/Mercado Pago/Mercado Libre/TheFork/TripAdvisor/redes: solo convenio o
  documentación de solicitud; nunca scraping.
- Pedir a privados: tabla mensual agregada por comuna/rubro con umbral mínimo por celda; sin
  datos personales.
