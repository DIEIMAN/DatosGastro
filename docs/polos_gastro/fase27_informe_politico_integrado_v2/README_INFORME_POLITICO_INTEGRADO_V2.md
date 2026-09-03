# Informe político integrado V2 — fase27 (línea experimental paralela)

Rol: `integrador_tecnico_editorial` (infraestructura V1.1.1). Fecha: 2026-07-12.
Estado: **PENDIENTE_QA_FINAL_INDEPENDIENTE_Y_REVISION_DIEGO** (no es el informe oficial de oficina).

## Qué es esta línea

Nueva versión integrada del informe político de Polos Gastronómicos (10 páginas reales), que
incorpora las decisiones territoriales cerradas y los assets cartográficos institucionales V3.1.
Es una línea completamente paralela: no modifica Fase 25 (oficina ni política experimental),
Fase 26, la corrida territorial V3, las correcciones V3.1, la preintegración ni la evidencia
documental.

## Base editorial (solo lectura; hashes SHA-256 verificados pre y post)

| Insumo | Ruta | SHA-256 |
| --- | --- | --- |
| PDF político experimental V1 | `outputs/polos_gastro/experimentos/fase25_politica_e_integracion_editorial_v1/INFORME_POLOS_GASTRO_FASE25_POLITICA_EXPERIMENTAL_V1.pdf` | `f9ba2effcb93999bf0a860d143cbc825279312bb9221cc577a9a7b879171c7d7` |
| Generador V1 | `scripts/polos_gastro/experimentos/fase25_politica_e_integracion_editorial_v1/generar_fase25_politica_experimental_v1.py` | `a06f6c5fdba21aeae5b5c4fcced938dd2ba3c935e0cf93b233edfdaa5ed4e9e2` |
| YAML editable V1 | `docs/polos_gastro/experimentos/fase25_politica_e_integracion_editorial_v1/contenido_fase25_politica_experimental_v1.yaml` | `ae9c5de6b14d03f003ffa8e35d645fd53bfeab022d5b3ab2fa0577a5a3acbe84` |
| KPI lock preliminar V1 | `docs/polos_gastro/experimentos/fase25_politica_e_integracion_editorial_v1/kpis_lock_preliminar.json` | `eed67adefd7844972f343f2428099c260578977a199385eaee49dfa9521038da` |
| Paquete `REVISION_FASE25_POLITICA_EXPERIMENTAL.zip` | `outputs/polos_gastro/experimentos/fase25_politica_e_integracion_editorial_v1/REVISION_FASE25_POLITICA_EXPERIMENTAL.zip` | `b75e62a38fb6edeb0dc3034c86c38ef7a072f51dc0ac16586995317347275a8d` |

Los assets de aquella versión (6 PNG placeholder) quedaron registrados en
`outputs/polos_gastro/fase27_informe_politico_integrado_v2/metadatos/` (snapshot pre) y no se
reutilizan: todos los mapas de la V2 provienen de V3.1 o de renders nuevos desde capas vigentes.

## Decisiones aplicadas (cerradas; no se reabren)

- **7 zonas seleccionadas en detalle**: Palermo, Corrientes, San Telmo, Puerto Madero,
  Belgrano, Recoleta, Costanera Norte (los subpolos/centralidades/componentes no cuentan
  como zonas adicionales).
- **Belgrano**: un único polo; tres centralidades territoriales; siete piezas topológicas
  internas (no comunicadas como polos); Belgrano R = `SECTOR_SECUNDARIO`, sin promoción.
  Cobertura 35,58 % NO usada como KPI público.
- **Recoleta**: un único polo; una unidad pública; nueve núcleos solo analíticos (no
  mostrados); sin división pública en subzonas; sin "zona en observación"/"candidata".
- **Costanera Norte**: tipo público `Polo multiparte`; cuatro componentes discontinuos
  (cinco piezas: un componente es multiparte); CN_C02 componente pleno; vacíos preservados,
  sin conectores artificiales; "containers" reemplazado por "contenedores" en el texto propio
  (la leyenda del asset V3.1 conserva la denominación descriptiva documentada).
- **Palermo** delimitación vigente sin reabrir; **Corrientes** corredor continuo v2.1
  separado de Abasto; **San Telmo** núcleo + Defensa contextual; **Puerto Madero** `PM_PRES_C`.
- Sin placeholders: los 8 mapas del informe son institucionales.

## Assets cartográficos (QA cartográfico)

Trazabilidad completa (origen, transformación, hashes de origen e insertado):
`outputs/polos_gastro/fase27_informe_politico_integrado_v2/metadatos/ASSETS_TRAZABILIDAD_V2.csv`.

- Página 3: `mapa_general_institucional_v3_1.png` (copia recortada reproducible).
- Página 4: render nuevo Palermo (delimitación vigente; estilo V3.1).
- Página 5: render nuevo Corrientes (corredor v2.1).
- Página 6: renders nuevos San Telmo (núcleo + Defensa) y Puerto Madero (PM_PRES_C).
- Página 7: `belgrano_institucional_v3_1.png` (copia recortada).
- Página 8: `recoleta_institucional_v3_1.png` (copia recortada).
- Página 9: `costanera_norte_media_pagina_v3_1.png` (copia recortada).

El recorte (parámetros en `config_integracion_v2.json`) elimina solo franjas de título/pie
internas de las copias —incluida la referencia interna "V3.1 · post-QA" del mapa general—;
el contenido cartográfico, las leyendas, la escala y el norte se conservan. Los originales
V3.1 no se modifican (verificado por hash en `VERIFICACION_PREDECESORES_V2.csv`).

## Estructura (10 páginas)

Ver `PLAN_PAGINACION_FINAL_V2.md`. Opción editorial recomendada de la preintegración:
Recoleta obtiene página propia (8); "Próximos pasos" se compacta y absorbe la nota
metodológica en la página 10.

## Reproducción

Desde la raíz del repositorio:

```
.venv/Scripts/python.exe scripts/polos_gastro/fase27_informe_politico_integrado_v2/generar_informe_politico_integrado_v2.py
```

Capa editable: `scripts/polos_gastro/fase27_informe_politico_integrado_v2/contenido_informe_politico_integrado_v2.yaml`
(el contenido visible se edita ahí, sin tocar el motor gráfico). Configuración de assets:
`config_integracion_v2.json`. El script no usa red, APIs, Places ni clustering; verifica por
hash que los predecesores y las superficies protegidas queden intactos, y termina generando
el paquete de revisión y su ZIP (usar `--no-pack` durante iteraciones).

## KPIs

Únicas fuentes: `outputs/polos_gastro/corrida_territorial_v3/KPI_LOCK_CARTOGRAFICO_V3.csv`,
`docs/polos_gastro/preintegracion_editorial_v3/PLANTILLA_KPI_LOCK_V3.csv` y decisiones
editoriales firmadas. Registro consolidado: `KPI_LOCK_EDITORIAL_V2.csv`. Los porcentajes de
cobertura/estabilidad/dependencia quedan reservados a metodología; el único publicado es la
dependencia de fuente externa de Costanera Norte (92,96 %), exigido por DEC-10, una sola vez
en la nota metodológica.

## QA

- Estructural: `QA_ESTRUCTURAL_PDF_V2.md` (pdfinfo: 10 páginas A4; sin páginas en blanco).
- Visual: `QA_VISUAL_PAGINA_POR_PAGINA_V2.csv` (10/10 páginas inspeccionadas; sin
  `AJUSTE_IMPORTANTE` ni `NO_APTO`).
- Textual: `QA_TEXTUAL_INSTITUCIONAL_V2.csv` (16 términos controlados).
- Comparativa V1→V2: `AUDITORIA_COMPARATIVA_V1_V2.md`.
- Handoff: `HANDOFF_AUDITOR_FINAL_INFORME_POLITICO_V2.md`.
