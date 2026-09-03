# AGENTS.md - DataGastro

Instrucciones para agentes que no son Claude Code (Codex y cualquier asistente automatizado).
**Las reglas del proyecto viven en `CLAUDE.md`**: guardrails, entorno, alcance por subproyecto y
mapa del repo. Leerlo primero; este archivo agrega solo lo que cambia para esos agentes.

## Skills

Las skills canónicas están en `.claude/skills/<skill>/SKILL.md`. Para agentes que no las cargan
solos, `.agents/skills/` tiene réplicas puntero con el mismo nombre y descripción. Ante diferencia
gana la canónica; validador: `scripts/infraestructura_agentes_skills_v1_1/check_skills_parity.py`.

## Estándar de informes DataGastro

Antes de producir un informe, consultar en este orden:

1. `agent_skills/README.md`
2. `agent_skills/shared/datagastro_modelo_informes.md`
3. `agent_skills/shared/datagastro_proyectos_cortos.md` (relevamientos cortos, tipo Cafecito)
4. `agent_skills/shared/datagastro_reporte_formulario.md` (formularios, encuestas, planillas)
5. `agent_skills/shared/datagastro_qa_privacidad.md` antes de cerrar entregables públicos
6. `agent_skills/shared/datagastro_metodo_experimental.md` **siempre que una corrida vaya a
   producir un número que después se lea como conclusión**

La skill `datagastro-informes` trae la plantilla DGDGAS (portada sin fecha ni versión, índice,
secciones numeradas, anexo metodológico, lenguaje prudente: "identificados", no "confirmados").

## Infraestructura agentes y skills (V1.1)

Para trabajo multiagente o packs de revisión: política, ciclo de una pasada (producción →
auditoría independiente → corrección → decisión → cierre), catálogo y adaptadores en
`docs/infraestructura_agentes_skills_v1_1/`. Superficies protegidas por subproyecto en
`docs/<subproyecto>/PROTECTED_SURFACES.yaml`. La V1 histórica queda en
`docs/infraestructura_agentes_skills_v1/`. No asumir carga automática de `.codex/`.

## Reglas que Codex tiende a saltear

- No hacer commit ni push sin pedido explícito. **No usar `git add .`** ni `git add -A`.
- Python: `.venv/Scripts/python.exe`, nunca `python` a secas.
- Datos personales o sensibles: se pueden usar internamente para un cruce autorizado, con
  minimización de campos, finalidad explícita, trazabilidad y almacenamiento en carpeta ignorada
  por Git. **Nunca** en entregables públicos: ni correos, teléfonos, nombres de personas, CUIT,
  DNI, IDs técnicos, links privados ni API keys. Los identificadores que enlazan fuentes se
  eliminan, anonimizan o agregan antes de publicar.
- No modificar fuentes originales, `.env`, credenciales ni crudos.
- Ante pedidos de informes, trabajar en `docs/`, `scripts/` y `outputs/` del subproyecto pedido.
  No reescribir informes existentes ni tocar `data/`, `src/`, `dashboard/`, `notebooks/` ni otros
  subproyectos salvo pedido explícito.
- Antes de cerrar: separar salidas internas de entregables públicos, reportar qué archivos se
  crearon o modificaron y confirmar si se tocaron datos fuente.

## Contexto

Proyecto de datos del ecosistema gastronómico de CABA para la DGDGAS (Dirección General de
Desarrollo Gastronómico; "DataGastro" solo en docs internos). Rol esperado: analista senior de
datos y políticas públicas, español argentino, tono institucional sobrio. Fuentes públicas GCBA
primero; separar dato confirmado / inferido / pendiente / no encontrado; trazabilidad
fuente-fecha-universo en toda cifra.

Las instrucciones Cowork originales están supersedidas y archivadas en
`docs/legacy/AGENTS_cowork_importado_SUPERSEDIDO_2026-07-14.md`.
