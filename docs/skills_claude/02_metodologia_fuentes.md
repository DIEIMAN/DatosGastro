# Skill 02 — Metodología de fuentes

Cómo clasificar, describir y priorizar cualquier fuente de datos antes de tocar código.

## 1. Espacios de identificadores (no mezclar)

| Prefijo | Universo | Ejemplos | Estado |
| --- | --- | --- | --- |
| `F01–F05` | **Públicas actuales** ya en el pipeline | Oferta gastronómica (F01), Habilitaciones AGC (F02), Ferias y mercados (F03), Eventos (F04), Programas/políticas (F05) | Productivas, **no se tocan sin permiso** |
| `F06+` | **Públicas nuevas** candidatas a pipeline público | Permisos de área gastronómica, OSM, padrón vivo AGC | Roadmap; entran solo tras documentar y aprobar |
| `I01–I99` | **Internas de gestión** (Drive/área) | `I01_eventos_internos_2026`, `I04_seguimiento_operativo_eventos` | Análisis interno; nunca al pipeline público sin minimización + contrato |
| `E01–E99` | **Externas privadas o públicas nuevas de terceros** | Google Places, Rappi, PedidosYa, Mercado Pago, TheFork | Roadmap; mayoría requiere convenio/API oficial |

> Regla: una fuente vive en **un solo** espacio. Si tiene dos naturalezas (p. ej. un Excel
> interno que además contiene datos públicos), se separa en dos fuentes con IDs distintos.

## 2. Ficha mínima de fuente

Toda fuente nueva debe describirse con esta ficha **antes** de integrarse:

- **ID y universo**: F / I / E + número.
- **Qué mide**: la magnitud real (oferta registrada, habilitación aprobada, permiso, evento,
  pedidos, transacciones, reservas, flujo de personas, reputación digital...).
- **Qué NO mide**: explícito. Ej.: "no mide locales activos hoy", "no mide facturación real".
- **Granularidad**: grano de fila (local, trámite, evento, comuna-mes, área/polígono...).
- **Cobertura temporal**: rango de fechas, fecha de corte, periodicidad de actualización.
- **Cobertura territorial**: CABA completa / parcial / sesgada a zonas turísticas, etc.
- **Limitaciones**: huecos, duplicados, falta de estado vigente, dependencia de comunidad, etc.
- **Riesgo de uso**: legal (TOS, scraping), privacidad, reputacional.
- **Prioridad**: alta / media / baja, con justificación.
- **Destino**: ¿entra al **pipeline** (y bajo qué condiciones) o queda en **roadmap**?

Para fuentes externas/privadas usar además el `checklist_legal_y_metodologico.md`
(ver `docs/fuentes_externas/`).

## 3. Qué mide vs. qué no mide (errores típicos)

- Habilitaciones aprobadas → mide **trámites aprobados históricos**, no locales abiertos hoy.
- Oferta registrada / directorios (Google, OSM) → mide **oferta visible publicada**, no padrón
  oficial ni confirmación de habilitación.
- Delivery (Rappi/PeYa) → mide **actividad en esa plataforma**, no el universo gastronómico.
- Pagos (Mercado Pago/adquirentes) → mide **actividad económica de comercios adheridos**, no
  todo el sector.
- Eventos internos → miden **gestión y seguimiento operativo**, no necesariamente facturación
  validada ni asistentes reales auditados.

Cada una responde una pregunta distinta. No se suman ni se comparan como si midieran lo mismo.

## 4. Criterio para entrar al pipeline

Una fuente entra al pipeline público solo si:

1. Tiene ficha completa y contrato documentado (estilo `src/source_contracts.py`).
2. Tiene identificador estable y fecha de corte.
3. Pasa `--strict-real` (no inventa) y validaciones.
4. No mezcla universos ni introduce datos sensibles sin minimizar.
5. **Diego aprobó** la integración explícitamente.

Si falta cualquiera de estos puntos: queda en **roadmap** documentado, no en código productivo.

## 5. Trazabilidad

- Cada fila debe poder rastrearse a su fuente (URL, archivo, fecha de consulta).
- Las páginas portal se documentan, pero la descarga automática requiere enlace directo a
  archivo. No se inventan URLs.
- Ver `docs/fuentes_y_trazabilidad.md` y `docs/contratos_fuentes.md` para el detalle del pipeline
  vigente.
