---
name: datagastro-fuentes-externas
description: Reglas de recolección controlada e integración de fuentes externas/privadas en DataGastro (Google Maps/Places, Rappi, PedidosYa, Mercado Pago, Mercado Libre, POS, TheFork, TripAdvisor y redes). Usar al investigar, extraer, contrastar o preparar integraciones de terceros.
---

# Fuentes externas y privadas

Contenido canónico: `docs/skills_claude/06_fuentes_externas_privadas.md`. Matriz y plantillas en
`docs/fuentes_externas/` y `config/fuentes_externas/`.

Regla central: **recolección controlada, separación de evidencia e integración**. Se puede
relevar información comercial públicamente visible, incluso mediante navegador o extracción
automatizada, con autorización explícita por tarea, alcance acotado, trazabilidad, ritmo prudente
y salida interna. No ejecutar llamadas pagas sin autorización ni guardar credenciales.

- OSM/Overpass: script exploratorio permitido (abierto, con atribución).
- Google Maps/Places, delivery, reservas, directorios y redes: se permiten como señales externas
  para investigación interna. No eludir login, CAPTCHA, paywall ni controles de acceso; no usar
  cuentas o sesiones personales salvo autorización expresa y lectura puntual.
- Todo resultado automatizado queda como `EVIDENCIA_EXTERNA_NO_CANONICA`: no prueba por sí solo
  vigencia, identidad ni actividad, y requiere corroboración/revisión humana antes de publicarse.
- Pedir a privados: tabla mensual agregada por comuna/rubro con umbral mínimo por celda; sin
  datos personales.
