# Diseño del pipeline definitivo de microzonas gastronómicas

**Línea experimental** separada del pipeline oficial (F01–F05 intacto, Fase 25 intacta,
informes intactos). Iniciada 2026-07-08 a pedido de Diego, como continuación conceptual —
no experimental — de las Tandas 1 y 2 de clustering (`docs/polos_gastro/
experimentos_clustering/` y `experimentos_clustering_v2/`), cuyos resultados se dan por
aprendidos y no se repiten.

**Objetivo:** dejar diseñada la metodología para que, cuando exista una base gastronómica
completa de la Ciudad, se puedan generar automáticamente **microzonas** (núcleos
gastronómicos precisos, p. ej. Fitz Roy–Honduras–Gorriti) **dentro** de las macrozonas
editoriales de DGDGAS, sin redefinir las macrozonas.

## Contenido

| Documento | Qué responde |
|---|---|
| `01_PIPELINE_MICROZONAS_PROPUESTO.md` | flujo completo (universo → normalización → deduplicación → clustering → poligonización → QA → revisión humana → salida versionada), restricciones anti-polígonos-absurdos, gobernanza y fases de adopción |
| `02_COMPARACION_ALGORITMOS_Y_POLIGONIZACION.md` | comparación DBSCAN / HDBSCAN / OPTICS / KDE / grilla-hotspot / etc.; métodos de poligonización (convex/concave hull, alpha shapes, buffers, ejes viales, Voronoi) y regla híbrida recomendada |
| `03_CONSTRUCCION_UNIVERSO_GASTRONOMICO.md` | fichas y sesgos de F01, F02, semilla, internas, OSM, Google Places; diseño de la tabla maestra; estrategia de deduplicación y de actualización; recomendación de universo v1 |

## Evidencia empírica de respaldo

- Script (solo lectura): `scripts/polos_gastro/experimentos/perfilar_fuentes_universo_definitivo.py`
- Salidas: `outputs/polos_gastro/experimentos/diseno_pipeline_definitivo/`
  (`perfil_fuentes_universo.md`, `cobertura_por_comuna.csv`)

## Estado y decisiones pendientes (Diego)

Diseño terminado; **nada implementado** por decisión explícita. Antes de la Fase B (universo
v1) hace falta decidir: (a) F01+F02 como universo v1, (b) revisión del mapeo del recurso
F02-2025 (sin fecha hoy), (c) inclusión de OSM como tercera evidencia, (d) alcance de Google
Places (solo validación por muestreo, con presupuesto).
