# Evaluación agentes y skills V1.1

**Fecha:** 2026-07-11  
**Método:** pruebas end-to-end en `outputs/infraestructura_agentes_skills_v1_1/casos_e2e/` + paridad de skills.  
**Escala:** `APTO_DOCUMENTAL` | `APTO_PILOTO` | `APTO_PRODUCTIVO_CONTROLADO` | `NO_APTO`

No se declara APTO productivo solo por existencia de archivos.

---

## Resumen

| Elemento | Aptitud |
| --- | --- |
| Política V1.1 | **APTO_PRODUCTIVO_CONTROLADO** (núcleo genérico + registros) |
| Superficies protegidas (registro) | **APTO_PRODUCTIVO_CONTROLADO** (Polos + plantilla) |
| Esquema manifest | **APTO_PILOTO** (corregido; validado en empaquetado) |
| Paridad skills | **APTO_DOCUMENTAL** (reporte; sin copiar productivas) |
| investigador_documental + auditar_evidencia | **APTO_PILOTO** (E2E caso1) |
| cartografo + transformar_cartografia | **APTO_PILOTO** (E2E caso2) |
| integrador + integrar_handoffs | **APTO_PILOTO** (E2E caso3) |
| auditor_qa + QA stack | **APTO_PILOTO** (E2E caso4) |
| validar_metricas_y_kpis | **APTO_PILOTO** (E2E caso5; límite del validador de strings documentado) |
| qa_pdf_pagina_por_pagina | **APTO_PILOTO** (herramienta + V1; no re-render completo en cada E2E) |
| crear_paquete + manifest hashes | **APTO_PILOTO** (empaquetador V1.1) |
| auditar_git_y_protegidos | **APTO_PILOTO** (hash analítico + staged empty) |
| Adaptadores Claude nativos | **NO_APTO** / no activados (schema no verificado) |
| Adaptadores Codex delgados | **APTO_DOCUMENTAL** → **APTO_PILOTO** vía punteros AGENTS |
| coordinador / editor / metodológico nativos | **NO_APTO** para nativos esta tanda (explícito) |
| Infra completa como única capa productiva | **NO_APTO** — usar como **piloto controlado** |

**Veredicto de paquete V1.1:** **APTO_PILOTO** para uso con punteros en AGENTS/CLAUDE y scripts E2E.  
**No** `APTO_PRODUCTIVO_CONTROLADO` global hasta paridad de copias productivas y agents nativos con permisos acotados.

---

## Casos E2E

| Caso | Obediencia | Calidad | Trazabilidad | Independencia | Resultado |
| --- | --- | --- | --- | --- | --- |
| 1 Documental | Alta (REC-R02, handoff nuevo) | Alta | Hashes insumos | N/A productor | PASS |
| 2 Cartografía | Alta (analítica intacta) | Mapa generado | hash pre/post | N/A | PASS |
| 3 Integración | Alta (línea nueva) | Ficha+lock+contradicciones | handoffs | N/A | PASS |
| 4 QA | Alta (no corrige producto) | INFORME_QA | KPIs+git+protegidos | **Sí** rol separado | PASS |
| 5 KPIs | Alta | Documenta límite universo | JSON resultados | N/A | PASS |

### Detalle caso 5

- Correcto: exit 0  
- Discrepante: exit 1 (falta '99')  
- Universo incorrecto: el script puede devolver OK si el string está; el fallo metodológico se documenta (no es bug del script)  
- No verificable: cualitativo  

---

## Paridad (hallazgos automáticos)

Ver `REPORTE_PARIDAD_SKILLS.md`. Esperado:

- `datagastro-qa-pdf` ausente en `.agents` e imported  
- `datagastro-informes` / `guardrails` pueden diverger entre capas  

**No se copiaron skills productivas en esta tanda.**

---

## Consumo de contexto

| Carga | Nivel |
| --- | --- |
| Política V1.1 sola | bajo |
| Política + 1 agente + 1 skill | medio |
| 10 skills de una vez | alto — evitar |
| Catálogo JSON completo | medio |

---

## Conflictos / portabilidad

- Rutas en handoffs E2E: relativas al repo (canónico V1.1).  
- ZIP: sin rutas absolutas de máquina en arcnombres.  
- Windows + venv respetado.  

---

## Errores V1 corregidos en esta evaluación

1. Manifest autorreferente → `MANIFEST_CONTENIDO` + `CHECKSUMS`  
2. Política con fases Polos hardcodeadas → registro YAML  
3. APTO por prueba documental parcial → reclasificado; E2E eleva a PILOTO  
4. Drive: lectura + escritura solo con autorización  
5. Precedencia explícita incl. autorización humana limitada  

---

## Correcciones futuras

1. Promover paridad de `datagastro-qa-pdf` e informes a espejos Codex  
2. Verificar schema `.claude/agents/` antes de activar  
3. Ampliar muestra URL y pdf_check en QA de ficha si se genera PDF  
4. Script genérico `verify_protected_surfaces.py` leyendo YAML  
