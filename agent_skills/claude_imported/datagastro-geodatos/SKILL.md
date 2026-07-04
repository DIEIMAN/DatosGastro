---
name: datagastro-geodatos
description: Tratar direcciones, comunas, barrios, lat/lon, USIG, OSM y Google Places en DataGastro. Usar al geocodificar o hacer análisis territorial, densidad vs volumen y sesgos.
---

# Geodatos y territorio

Contenido canónico: `docs/skills_claude/05_geodatos_y_territorio.md`.

Regla central: **geocodificar NO prueba que el local exista ni esté activo hoy.**

- Preferir USIG para normalizar y asignar comuna/barrio en CABA; OSM y Google son contraste
  externo, no padrón.
- Distinguir densidad vs volumen; declarar siempre el denominador y la fecha de corte.
- Vigilar sesgos: cobertura (zonas turísticas), geocodificación (centroides), fuente, temporal.
- Usar el sustantivo correcto: oferta registrada/visible, habilitaciones aprobadas, permisos —
  no "locales activos".
