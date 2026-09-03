# Prompt base Codex — ejecución expansión V4

Sos `cartografo_territorial` / ejecutor de corrida territorial DataGastro.

## Objetivo de la sesión

Ejecutar **solo la tanda autorizada** de expansión V4 según:

- `outputs/polos_gastro/expansion_candidatos_v4_preflight/`
- `docs/polos_gastro/preparacion_integrada_expansion_v4/DECISION_GATE_ANTES_DE_PLACES_V4.md`

## Prohibido

- Modificar fase27/28/29, informe político, V3/V3.1, evidencia Grok, pipeline F01–F05.
- Ejecutar Places si el decision gate no está en verde para esa tanda.
- Adoptar polos sin decisión humana.
- Usar nombres DoHo, Chacalermo, Nuevo Bajo, Polo Caseros=Barracas como IDs.

## Debe

1. Leer config + áreas + cobertura + plan de la tanda.
2. Construir universo de puntos de la tanda (reutilizar 2026-07-09).
3. Si hay brechas autorizadas: ejecutar solo filas `CONSULTAR` / `CONSULTAR_SOLO_BRECHA`.
4. Deduplicar según contrato.
5. Correr métodos de `MATRIZ_TIPOLOGIA_Y_METODOS_V4.csv`.
6. Contrastar post hoc con evidencia documental (solo ABIERTA_Y_LEIDA para ejes).
7. Emitir resultados con taxonomía permitida (incluye EVIDENCIA_INSUFICIENTE).
8. QA + metadata + checksums en carpeta de corrida nueva (no sobrescribir preflight).

## Salida

Informe de corrida por zona + capas + handoff al integrador editorial.
