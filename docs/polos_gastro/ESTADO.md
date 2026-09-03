# Polos Gastronómicos — estado

**Fecha de corte:** 2026-09-03. **Fuente de estatus institucional:**
`outputs/polos_gastro/INFORMEFINAL/ESTADO_GENERAL_INFORMEFINAL.md` (estado al 2026-08-04 más nota
de la reorganización) y `DECISIONES_CERRADAS_Y_PENDIENTES.md`. Este archivo es el resumen fechado
y el puntero; ningún mapa técnico es fuente de estatus.

## Líneas y entregables

| Línea | Entregable vigente | Estado |
|---|---|---|
| Atlas 22 / INFORMEFINAL | `outputs/polos_gastro/INFORMEFINAL/` (V2 Compacta corregida, cerrada y congelada 2026-07-20) | Cerrado. |
| ATLAS_V2 (tres ediciones) | `outputs/polos_gastro/ATLAS_V2/` (conducción, técnica, .docx), selladas 2026-08-05 | Cerrado. |
| Atlas informativo de 39 polos | `outputs/polos_gastro/ATLAS_INFORMATIVO_39_2026-08-13/` (documento V6.4 del 2026-08-19; anexo de establecimientos 39/39) | Vigente. Auditoría de respaldo técnico: APTO_CON_CORRECCION (2026-08-16). |
| Recuperación nominal de establecimientos | Capa integrada 2026-08-25 (inventario por polo y local; ver handoffs de agosto) | Integrada. Ampliación con Places preparada y bloqueada hasta leer saldo por SKU. |
| Referentes 2026 | `outputs/polos_gastro/REFERENTES_2026/` | Reconciliación referentes↔inventario 2026-08-14. |
| Todo lo anterior al 2026-08-13 | `outputs/polos_gastro/historico/` (1,5 GB: FASE5-29, revisiones, evidencias v1–v4, experimentos, cuatro iteraciones del 2026-08-12) | Histórico, movido como contenedor el 2026-08-28 (commit del 2026-09-03). |

## Decisiones que esperan a Diego

- Destino de las copias `.docx` intermedias del Atlas 39 (v5.1, v6.0–v6.3 con sufijos
  `_PRE_SANITIZAR`, `_GOOGLE_DOCS`, `_TITULO_SANITIZADO`, ~574 MB).
- `docs/polos_gastro/`: 189 archivos duplican byte a byte `outputs/polos_gastro/historico/`;
  archivar o borrar la copia de docs.
- Ampliación de la recuperación nominal (cola de ~5.000 consultas a Places, techo de presupuesto
  registrado en el handoff del 2026-08-21).

## Dónde seguir

- Handoffs: `docs/revisiones/HANDOFF_POLOS_*`, `HANDOFF_PLACES_DOS_POLOS_2026_08_21.md`.
- Superficies protegidas: `docs/polos_gastro/PROTECTED_SURFACES.yaml`.
- Scripts: `scripts/polos_gastro/` (rutas parcheadas a `historico/` el 2026-08-28).
