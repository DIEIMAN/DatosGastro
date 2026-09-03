---
name: datagastro-guardrails
description: Checklist de los guardrails permanentes de DataGastro, incluido el borrado seguro de archivos locales. Usar SIEMPRE antes de borrar, mover o modificar archivos, tocar el pipeline F01-F05, escribir en Google Drive, recolectar de plataformas externas o exponer datos sensibles.
---

# Guardrails DataGastro: checklist

Las nueve reglas viven en `CLAUDE.md` (resumen cargado en cada sesion) y en detalle en
`docs/skills_claude/01_datagastro_guardrails.md`. Esta skill no las repite: es la lista de
preguntas que hay que responder antes de actuar. El hook `scripts/hooks/guardrails_pretooluse.py`
bloquea en codigo las tres mas graves (Drive, superficies protegidas, `python` a secas); todo lo
demas depende de esta lista.

1. ¿Escribe en Drive? No se hace. Leer y copiar desde Drive hacia el proyecto si.
2. ¿Toca `src/build_*`, `data/processed`, `data/analytics`, `dashboard`, `notebooks` o un
   entregable final? Pedir permiso antes, con el plan escrito.
3. ¿Mezcla universos F/I/E o llama "activo" a una habilitacion, permiso o registro? Corregir la
   redaccion antes de que salga.
4. ¿Expone o commitea datos personales (CUIT, DNI, email, telefono, montos individuales)? Agregar,
   anonimizar o mandar a carpeta ignorada. Detalle en `datagastro-privacidad`.
5. ¿Borra o mueve archivos locales? Ver el bloque de abajo.
6. ¿Recoleccion o API de plataforma externa? Aplicar `datagastro-fuentes-externas`: autorizacion
   por tarea, alcance acotado, salida interna, trazabilidad, revision humana antes de integrar.
7. ¿Produce un numero que se va a leer como conclusion? Antes de correr, leer
   `agent_skills/shared/datagastro_metodo_experimental.md`.

Ante la duda, frenar y preguntar.

## Borrado y movimiento seguro de archivos locales (guardrail 9)

Detalle en `docs/skills_claude/08_limpieza_archivos_locales.md`.

- Primero el plan, despues la confirmacion de Diego, despues la accion. Nunca al reves.
- Clasificar cada item en **seguro borrar** / **revisar** / **no borrar**, con peso y riesgo.
- No borrar nunca sin permiso: outputs finales, scripts, datos fuente publicos, `data/processed`,
  `data/analytics`, documentacion, configuracion, paquetes sellados con `.sha256`.
- Priorizar lo regenerable: renders de QA, caches, `__pycache__`, duplicados con hash identico,
  diagnosticos temporales, venvs de herramientas.
- Ante la duda, cuarentena antes que borrado: `_delete_candidates/<fecha>/` (ignorada por Git),
  que vence a los 14 dias si nadie la reclama. Anotar el vencimiento en el handoff.
- Mover con `git mv` lo trackeado, y antes de mover una carpeta grepear su ruta en `scripts/`,
  `src/`, `docs/` y `.gitignore`; parchear en el mismo commit.
- Toda fase de reorganizacion termina en commit. Lo que queda "movido en disco" y sin commit se
  pierde con el primer `git checkout .`.
