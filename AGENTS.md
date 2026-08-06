# AGENTS.md - DataGastro

Instrucciones para agentes que trabajen en este repositorio. Estas reglas aplican a Codex y a
cualquier asistente automatizado.

## DataGastro reporting standard

Para informes DataGastro, consultar antes de trabajar:

- `agent_skills/README.md`
- `agent_skills/shared/datagastro_modelo_informes.md`
- `agent_skills/shared/datagastro_proyectos_cortos.md`
- `agent_skills/shared/datagastro_reporte_formulario.md` para formularios, encuestas y planillas
  de respuestas.
- `agent_skills/shared/datagastro_qa_privacidad.md` antes de cerrar entregables públicos.

Si la tarea toca guardrails, privacidad, fuentes, pipeline, geodatos, fuentes externas o limpieza,
consultar también la skill importada correspondiente en `agent_skills/claude_imported/`.

## Infraestructura agentes y skills (V1.1, controlada)

Para trabajo multiagente, experimentos o packs de revisión (sin reemplazar las reglas de arriba):

1. Política: `docs/infraestructura_agentes_skills_v1_1/POLITICA_OPERATIVA_DATAGASTRO_V1_1.md`
2. Ciclo y roles: `docs/infraestructura_agentes_skills_v1_1/CICLO_OPERATIVO_UNA_PASADA.md`
   (una producción → una auditoría independiente → una corrección → decisión → cierre; estados
   canónicos; fuente vigente única por etapa).
3. Catálogo: `docs/infraestructura_agentes_skills_v1_1/CATALOGO_AGENTES_SKILLS.json`
4. Guía y evaluación: `docs/infraestructura_agentes_skills_v1_1/` (ver `README.md`)
5. Superficies protegidas por subproyecto: p. ej. `docs/polos_gastro/PROTECTED_SURFACES.yaml`
6. Adaptadores Codex delgados: `docs/infraestructura_agentes_skills_v1_1/adaptadores/codex/`
7. Definiciones de skills (procedimientos): `docs/infraestructura_agentes_skills_v1/skills/`

La V1 histórica permanece en `docs/infraestructura_agentes_skills_v1/` (no sobrescribir).
No asumir carga automática de `.codex/`. No inventar datos ni vulnerar privacidad aunque haya autorización para commit/API.

## Reglas obligatorias

- No inventar datos, métricas, fuentes, URLs ni conclusiones.
- No exponer datos personales ni sensibles.
- No publicar correos, teléfonos, nombres, CUIT, DNI, IDs técnicos, links privados ni API keys.
- No modificar fuentes originales salvo pedido explícito.
- No tocar `.env`, credenciales, datos internos ni crudos.
- No modificar pipelines de DataGastro general sin pedido explícito.
- No hacer commit ni push sin pedido explícito.
- No usar `git add .`.
- Mantener estilo institucional, claro, sobrio y prudente.

## Alcance por defecto

Ante pedidos de informes o estándares, trabajar en documentación, scripts y outputs del proyecto
pedido. No reescribir informes existentes ni tocar `MercadosGastro/`, `CasasDePastas/`,
`Cafesito/`, `data/`, `src/`, `dashboard/` o `notebooks/` salvo que el usuario lo pida de forma
explícita.

## Privacidad y QA

Antes de cerrar, verificar que los outputs no contienen emails, teléfonos, nombres de personas,
CUIT, DNI, links privados ni API keys. Reportar qué archivos se crearon o modificaron y confirmar
si se tocaron o no datos fuente.

## Contexto del proyecto (resumen vigente)

Proyecto de datos del ecosistema gastronómico de CABA para DGDGAS (Dirección General de
Desarrollo Gastronómico; "DataGastro" solo en docs internos). Rol esperado: analista senior de
datos y políticas públicas, español argentino, tono institucional sobrio. Fuentes públicas GCBA
primero; separar dato confirmado / inferido / pendiente / no encontrado; trazabilidad
fuente-fecha-universo en toda cifra.

Las instrucciones Cowork originales (arranque desde ZIP, estructura y prioridades iniciales)
están **supersedidas** y archivadas en
`docs/legacy/AGENTS_cowork_importado_SUPERSEDIDO_2026-07-14.md`. No usarlas como instrucciones
operativas.
