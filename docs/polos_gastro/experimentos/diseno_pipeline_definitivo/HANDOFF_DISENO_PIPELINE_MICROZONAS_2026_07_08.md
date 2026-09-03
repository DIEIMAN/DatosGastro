# HANDOFF — Diseño del pipeline definitivo de microzonas (2026-07-08)

## Qué se pidió

Tras cerrar las Tandas 1 y 2 de clustering (conclusión: metodología validada, universo de 106
puntos insuficiente), Diego pidió **diseñar** —no implementar— el pipeline definitivo para
detectar microzonas gastronómicas **dentro** de las macrozonas editoriales (que no se
redefinen). Entregables: doc de pipeline, doc comparativo de algoritmos, doc de construcción
del universo, y scripts exploratorios solo si respaldan conclusiones. Sin commits, sin push,
sin tocar Fase 25 ni informes.

## Qué se hizo (completo)

1. `docs/polos_gastro/experimentos/diseno_pipeline_definitivo/` con:
   - `01_PIPELINE_MICROZONAS_PROPUESTO.md` — flujo de 9 etapas, clustering intra-macrozona,
     QA con gates duros (superficie máx 35 ha, mínimo de locales, densidad mínima, elongación,
     contención), revisión humana obligatoria, adopción en fases A–E.
   - `02_COMPARACION_ALGORITMOS_Y_POLIGONIZACION.md` — recomendación: HDBSCAN (detector) +
     KDE (control) + DBSCAN solo continuidad; poligonización híbrida: concave hull + buffer
     para núcleos compactos, buffer-unión para n chico, cápsula sobre eje para corredores,
     Voronoi solo como frontera entre núcleos pegados.
   - `03_CONSTRUCCION_UNIVERSO_GASTRONOMICO.md` — fichas F01/F02/semilla/I/OSM/Places,
     tabla maestra de entidades con evidencia por fuente, deduplicación espacial+textual en
     4 pasos, actualización por snapshots versionados; universo v1 recomendado = F01+F02.
   - `README.md` — índice y decisiones pendientes.
2. Script de respaldo (solo lectura): `scripts/polos_gastro/experimentos/
   perfilar_fuentes_universo_definitivo.py` → salidas en `outputs/polos_gastro/experimentos/
   diseno_pipeline_definitivo/` (corrido OK 2026-07-08).

## Hallazgos empíricos clave (del perfilado)

- F01: 2.704 gastronómicos, 100 % geocodificados, pero 49 % concentrado en Comunas 1+14.
- F02: 44.169 filas gastro → solo **7.908 ubicaciones únicas** (duplicación interna 5,6×);
  mejor cobertura territorial que F01.
- El recurso F02-2025 (25.289 filas gastro, el más reciente y voluminoso) entra hoy **sin
  fecha de habilitación** en el mapeo → revisar mapeo antes de usarlo como evidencia fechada.
- Solapamiento F01∩F02 por `id_ubicacion`: **21 direcciones** (≈0). La deduplicación entre
  fuentes debe ser espacial + similitud de nombre; la clave de ubicación no reconcilia.

## Pendiente (decisiones de Diego, antes de implementar nada)

(a) Confirmar F01+F02 como universo v1 · (b) revisar mapeo F02-2025 · (c) OSM sí/no como
tercera evidencia (ficha F06+ previa) · (d) Google Places solo validación por muestreo con
presupuesto explícito. Luego: Fase B (universo v1) y Fase C (piloto en Palermo, San Telmo y
Corrientes) según `01_PIPELINE_MICROZONAS_PROPUESTO.md` §8.

## Estado del repo

Todo nuevo, sin commits (pedido explícito). Nada del pipeline oficial fue tocado ni
regenerado; el perfilado fue de solo lectura sobre `data/processed/`.
