# Prompt Codex — Tanda 1 expansión V4

Ejecutá **solo Tanda 1**: Z01 Villa Crespo, Z02 Chacarita, Z03 Caballito, Z04 Boulevard Caseros.

## Inputs

- Áreas y cobertura del preflight V4
- Universo sanitizado 2026-07-09
- Evidencia documental Grok (post hoc)
- Decision gate en verde para reutilización; autorización humana para brechas

## Tareas

1. Filtrar puntos del universo a las áreas Tanda 1 (geometría).
2. Reportar cobertura y brechas reales.
3. Si hay autorización: ejecutar únicamente `CONSULTAR_SOLO_BRECHA` / `CONSULTAR` de esas zonas.
4. Deduplicar.
5. Correr métodos:
   - Crespo: multiparte / red de nodos; control borde Palermo
   - Chacarita: Newbery + Dorrego; no Lacroze completa
   - Caballito: nodos separados; hipótesis nula fragmentación
   - Caseros: corredor corto; controles San Telmo / Barracas / Patricios
6. Clasificar con taxonomía permitida.
7. Contrastar con expedientes Z01–Z04 (sin supervisar clusters).
8. QA + handoff.

## Prohibido

Adoptar polos · renombrar a Chacalermo · fusionar Caballito · extender Caseros a Patricios · tocar V3/informe político.
