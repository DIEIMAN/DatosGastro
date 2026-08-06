# Política operativa DataGastro / DGDGAS

**ID:** `POLITICA_OPERATIVA_DATAGASTRO`  
**Versión:** 1.0 (paquete infraestructura agentes/skills V1)  
**Fecha:** 2026-07-11  
**Ámbito:** todas las skills y agentes de este paquete; compatible con Claude Code, Codex y otros asistentes.  
**Precedencia:** ante conflicto con un prompt puntual, **gana esta política** y los guardrails de `docs/skills_claude/01_datagastro_guardrails.md`.

Esta política es **corta a propósito**. El detalle vive en skills y en `docs/skills_claude/`.  
Referenciar como: *“Aplicar `POLITICA_OPERATIVA_DATAGASTRO` v1”*.

---

## 1. Protección de datos

1. No inventar datos, métricas, URLs, fuentes, fechas ni resultados.  
2. No modificar datos fuente (CSV/XLSX/PDF originales, crudos, Drive).  
3. No exponer ni versionar secretos (`.env`, API keys, credenciales).  
4. No scrapear ni llamar APIs de plataformas privadas sin autorización explícita y presupuesto.  
5. No ejecutar Google Places ni descargas externas salvo pedido autorizado y documentado.

## 2. Protección de finales

1. No modificar PDFs finales, packs de oficina cerrados ni fases oficiales (p. ej. Fase 25 oficial, Fase 26, resultados técnicos v2.1 ya cerrados como baseline).  
2. No “mejorar in-place” un entregable cerrado: se abre **línea paralela** con nombre de paquete nuevo.  
3. Pipeline público F01–F05 y `src/build_*`, `data/processed`, `data/analytics`, `dashboard/`, `notebooks/` no se tocan sin permiso de Diego.

## 3. Líneas experimentales

1. Todo experimento se etiqueta **EXPERIMENTAL / NO OFICIAL** hasta decisión humana en contrario.  
2. Estructura típica: `docs/.../<paquete>/`, `outputs/.../<paquete>/`, `scripts/.../<paquete>/`.  
3. Capa analítica y capa de presentación se mantienen **separadas** (archivos y lenguaje distintos).  
4. Geometrías, buffers y clusters no son límites institucionales salvo decisión firmada.

## 4. Git

1. No `git add .`.  
2. No staging masivo de outputs, secretos o crudos.  
3. No commit ni push sin autorización explícita.  
4. Reportar siempre: archivos creados/modificados y si se tocaron fuentes (respuesta esperada: no).

## 5. Privacidad

1. Entregables publicables: agregados y redacción prudente.  
2. Prohibido en publicables: emails, teléfonos, CUIT/DNI, nombres de personas no institucionales, `place_id`, montos/transacciones individuales, links privados de Drive/Docs, API keys.  
3. Escaneo automático ayuda; no reemplaza revisión humana.  
4. Crudos e internos van a rutas ignoradas por Git (`outputs/analisis_interno/`, `**/interno/`, etc.).

## 6. Trazabilidad

1. Cada paquete cierra con manifest (rutas, tamaños, hashes cuando aplique).  
2. Insumos críticos y superficies protegidas se verifican por hash pre/post cuando el paquete lo requiera.  
3. Cada cifra reportada debe poder rastrearse a fuente, universo y fecha de corte.  
4. Scripts y comandos de regeneración se documentan.

## 7. Fuentes

1. Universos **F / I / E** no se mezclan ni se suman como un total único.  
2. Usar el sustantivo que mide la fuente (habilitación, oferta registrada, permiso, evento).  
3. Prohibido presentar habilitaciones o registros parciales como “locales activos” sin base.  
4. Fuentes privadas u off-pipeline se declaran como tales.

## 8. QA

1. Un PDF no está terminado sin renderizar y **revisar página por página**.  
2. Si existe `kpis_lock.json`, validar KPIs antes de entregar.  
3. Cierre experimental típico: controles de política + manifest + privacidad + (si hay) ZIP sanitizado + `QA_FINAL`.  
4. El productor de un entregable **no** lo aprueba en definitivo: interviene un rol de auditoría distinto o Diego.

## 9. Decisiones humanas

1. Separar siempre: **evidencia** | **inferencia técnica** | **decisión institucional**.  
2. Las decisiones humanas firmadas (Diego / área) **no se reabren por defecto**.  
3. Una contradicción técnica nueva genera **nota de contradicción** y escala; no revierte sola la decisión.  
4. Nombres institucionales, inclusión en informe político y jerarquía editorial son decisión humana, no del algoritmo.

## 10. Carpetas exclusivas y trabajo paralelo

1. Cada agente o herramienta escribe solo en las rutas de su paquete/misión.  
2. No escribir en la carpeta de trabajo de otro agente en curso.  
3. Consumir del otro solo entregables finales con su propio QA.  
4. Drive: solo lectura.

## 11. Handoffs y entregas

1. Al cortar sesión o transferir: `HANDOFF_*.md` con estado, rutas, pendientes y prohibiciones.  
2. Entrega mínima: outputs + limitaciones + checklist QA + rutas absolutas.  
3. Estado del material (borrador interno / experimental / mostrable) se declara sin ambigüedad.  
4. Marca en publicables: **DGDGAS**. “DataGastro” solo en documentación interna.

## 12. Incertidumbre y defensa de lo adoptado

1. Obligación de declarar incertidumbre real (n, cobertura, sesgo, no verificado).  
2. Obligación de **no debilitar repetidamente** decisiones institucionales ya adoptadas en el mismo ciclo de trabajo.  
3. Si hay que cuestionar una decisión firmada: un solo bloque de “contradicción / propuesta de reapertura”, no reescritura dispersa del informe.  
4. Preferir “no encontrado / no verificable” antes que rellenar.

## 13. Entorno

1. Windows: invocar `.venv/Scripts/python.exe`, no `python` genérico.  
2. No instalar librerías en tareas de este paquete salvo autorización.  
3. No activar configuraciones experimentales globales del IDE sin documentarlo.

## 14. Autorización humana obligatoria

Requiere pedido explícito de Diego (o responsable):

- commit / push  
- modificar finales o pipeline F01–F05  
- borrar/mover archivos del repo  
- llamadas Places/APIs pagas  
- reabrir decisión institucional firmada  
- promover experimento a oficial  
- sobrescribir `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json` o skills productivas

## 15. Referencias canónicas (detalle)

| Tema | Ruta |
| --- | --- |
| Guardrails largos | `docs/skills_claude/01_datagastro_guardrails.md` |
| Fuentes F/I/E | `docs/skills_claude/02_metodologia_fuentes.md` |
| Privacidad | `docs/skills_claude/03_privacidad_datos_sensibles.md` |
| Pipeline | `docs/skills_claude/04_pipeline_reproducible.md` |
| Informes | `docs/skills_claude/07_informes_ejecutivos.md` + `agent_skills/shared/datagastro_modelo_informes.md` |
| Matriz reglas | `docs/infraestructura_agentes_skills_v1/MATRIZ_REGLAS_REUTILIZABLES.md` |
| Resumen Claude | `CLAUDE.md` |
| Resumen multiagente/Codex | `AGENTS.md` |

---

**Fin de la política v1.0.** Skills y agentes deben citar esta política; no re-pegar este texto completo salvo en onboarding.
