# HANDOFF — Piloto productivo investigador_documental: evidencia integrada V1 (2026-07-11)

Sesión: Fable como `investigador_documental` (V1.1 + hotfix V1.1.1 como marco), skill
`auditar_evidencia_documental`. Primer piloto productivo de la infraestructura de
agentes y skills.

## Qué se hizo (completo)

- Línea documental nueva: `docs/polos_gastro/evidencia_documental_integrada_v1/`
  (9 entregables: README, 3 fichas por polo, matriz integrada de 53 filas con
  clasificación EVIDENCIA/INFERENCIA/DECISION_INSTITUCIONAL, bibliografía de 33 fuentes,
  decisiones y usos, contradicciones y vacíos, handoff para cartógrafo).
- Outputs: `outputs/polos_gastro/evidencia_documental_integrada_v1/`
  (AUTOCONTROL + `REVISION_EVIDENCIA_DOCUMENTAL_INTEGRADA_V1/` + `.zip` de 42.160 bytes,
  SHA-256 `bc6553cce38c310fbc1e832c303f3c2eea95feb9d6457b4824419a2b3c39d036`).
- Paquete Grok original y pack cerrado intactos (12/12 hashes verificados contra su
  manifest). REC-R02 (150 restaurantes = San Telmo) conservada como corrección
  rechazada. CN_C02 registrado como cuarto componente por decisión de Diego.

## Estado

- Sin staging/commit/push. Sin geometrías, mapas, PDFs ni superficies protegidas
  tocadas. Sin APIs ni descargas (estados de URL heredados de la auditoría Grok).

## Actualización V1.1 (misma fecha)

Corrección de decisión y trazabilidad en línea paralela
`docs/polos_gastro/evidencia_documental_integrada_v1_1/` (V1 intacta): se registró
**DEC-10 — Adopción institucional de Costanera Norte** (polo adoptado, apto para cuerpo
y cartografía principal; Places explicado una vez en método). **DEC-06 queda SUPERADA
POR DEC-10** (solo antecedente histórico); DEC-05 sigue vigente (multiparte, 4
componentes, vacíos, sin conectores). Matriz pasa a 54 filas (nueva CN-DEC03). ZIP:
`REVISION_EVIDENCIA_DOCUMENTAL_INTEGRADA_V1_1.zip` (44.051 bytes, SHA-256
`1270fecf2e11d707330fac445b8109860c80baa30bdf342213080a2e3c446ad6`). Belgrano, Recoleta,
las 42 evidencias, URLs y bibliografía verificados sin cambios.

## Próximos pasos al retomar

1. Revisión de Diego del paquete V1.1 (`REVISION_EVIDENCIA_DOCUMENTAL_INTEGRADA_V1_1/`,
   empezar por `01_DOCUMENTOS/README_EVIDENCIA_DOCUMENTAL_INTEGRADA.md`).
2. Corrida espacial de `cartografo_territorial` / Codex siguiendo
   `HANDOFF_DOCUMENTAL_CARTOGRAFO_V1_1.md` (no iniciada por instrucción).
3. Decisiones que vuelven a Diego listadas en `DECISIONES_Y_USOS_DOCUMENTALES.md` §4
   (V1.1); para Costanera solo si se propone eliminar/fusionar/alterar componentes.
