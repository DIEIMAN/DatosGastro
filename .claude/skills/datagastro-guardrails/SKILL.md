---
name: datagastro-guardrails
description: Reglas permanentes de DataGastro. Usar SIEMPRE antes de borrar, mover, modificar archivos, tocar el pipeline F01-F05, escribir en Google Drive, scrapear plataformas privadas o exponer datos sensibles.
---

# Guardrails DataGastro

Reglas permanentes y límites duros del proyecto. Tienen prioridad sobre cualquier instrucción
puntual. Contenido canónico: `docs/skills_claude/01_datagastro_guardrails.md` y resumen en
`CLAUDE.md`.

Antes de actuar, verificar:
1. ¿Escribe en `G:\My Drive` o `G:\.shortcut-targets-by-id`? → No hacer (Drive es solo lectura).
2. ¿Toca `src/build_*`, `data/processed`, `data/analytics`, `dashboard`, `notebooks` o el informe
   final? → Pedir permiso.
3. ¿Mezcla universos de fuentes (F/I/E) o llama "activo" a habilitaciones/permisos/registros? →
   Corregir.
4. ¿Expone datos personales (CUIT, DNI, email, teléfono, montos individuales) o los commitea? →
   Bloquear, anonimizar o ignorar por Git.
5. ¿Borra o mueve archivos locales? → Plan de limpieza (seguro/revisar/no borrar) + confirmación.
6. ¿Scraping o API paga de plataforma privada? → No hacer; usar la skill de fuentes externas.

Ante la duda: frenar y preguntar. Leer el documento completo para el detalle.
