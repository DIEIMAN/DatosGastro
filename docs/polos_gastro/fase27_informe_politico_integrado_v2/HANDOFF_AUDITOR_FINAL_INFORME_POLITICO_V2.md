# HANDOFF — Auditor final del informe político integrado V2 (fase27)

| Campo | Valor |
| --- | --- |
| Origen | `integrador_tecnico_editorial` (V1.1.1) |
| Destino | Auditor final independiente + revisión de Diego |
| Fecha | 2026-07-12 |
| Estado | `POLITICAL_REPORT_V2_INTEGRATED_READY_FOR_FINAL_QA` — **no es el informe oficial** |

## Entregable principal

- PDF: `outputs/polos_gastro/fase27_informe_politico_integrado_v2/INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2.pdf`
  (10 páginas A4; hash y bytes en `CHECKSUMS_SHA256.txt` de la misma carpeta).
- Paquete de revisión: `REVISION_INFORME_POLITICO_INTEGRADO_V2/` + `.zip` (manifest y checksums adentro).
- Capa editable + generador + configuración + README de reproducción:
  `scripts/polos_gastro/fase27_informe_politico_integrado_v2/`.

## Qué se integró

1. Assets institucionales V3.1 (mapa general, Belgrano, Recoleta, Costanera media página)
   como copias recortadas reproducibles; originales intactos (hash en
   `metadatos/VERIFICACION_PREDECESORES_V2.csv`).
2. Renders institucionales nuevos para Palermo (delimitación vigente), Corrientes (corredor
   v2.1), San Telmo (núcleo + Defensa contextual) y Puerto Madero (PM_PRES_C), con el estilo
   y el fondo callejero local de la línea V3.1. Cero placeholders.
3. Decisiones cerradas: 7 zonas; Belgrano un polo / 3 centralidades / Belgrano R secundario;
   Recoleta unidad pública única; Costanera polo multiparte de 4 componentes con vacíos
   preservados; lenguaje DEC-10; nota metodológica pública única; dependencia de fuente
   externa de Costanera una sola vez en metodología (92,96 %).

## Qué debe verificar el auditor final

- QA visual independiente de las 10 páginas (PNG en
  `outputs/.../qa_png_INFORME_POLOS_GASTRO_POLITICO_INTEGRADO_V2/`).
- QA textual independiente (matriz del integrador: `QA_TEXTUAL_INSTITUCIONAL_V2.csv`).
- Consistencia texto–mapa–chip–KPI por página (gate de la línea V21).
- El único punto abierto de lenguaje: la leyenda del asset V3.1 de Costanera contiene la
  denominación descriptiva documentada "Patio gastronómico de puestos en containers". El texto
  propio del informe no usa "containers". Si Diego prefiere "contenedores" también dentro del
  mapa, corresponde pedir una regeneración V3.2 al cartógrafo (el integrador no edita la línea
  V3.1).

## Decisiones que quedan en Diego

1. Aprobación editorial general de la V2 (textos nuevos de Belgrano, Recoleta y Costanera).
2. Confirmación del chip "delimitación adoptada" como categoría estable del sistema
   tipo/madurez.
3. La eventual regeneración V3.2 del asset de Costanera por el término "containers".
4. Promoción de esta línea a informe oficial de oficina (fuera del alcance de esta tanda:
   el PDF oficial definitivo NO se generó).

## Guardrails cumplidos

- Sin red, APIs, Places, scraping ni clustering. Sin instalaciones ni borrados.
- Fase 25 (oficina y política), Fase 26, corrida V3, correcciones V3.1, preintegración y
  evidencia documental: intactas (verificación por hash y digest de superficies protegidas en
  `metadatos/QA_SUPERFICIES_PROTEGIDAS_V2.json`).
- Sin datos personales, sin puntos individuales, sin conteos convertibles a "locales activos".
- Sin staging/commit/push (`git diff --cached` vacío antes y después; snapshots en `metadatos/`).
