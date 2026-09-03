# INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX

Hotfix de **empaquetado y trazabilidad** sobre el piloto V1.1.

No reescribe arquitectura, skills, agentes, adaptadores, casos E2E, superficies protegidas ni punteros.

## Qué corrige

1. Orden de cierre: checksums sobre manifest **definitivo**
2. Encoding UTF-8 del diff de punteros y auditoría de textos
3. Inventario de dependencias externas sin duplicar canónicos
4. Evidencia Git (status, patches, cached vacío)
5. ZIP con extracción y re-verificación de hashes

## Ejecutar

```text
.venv/Scripts/python.exe scripts/infraestructura_agentes_skills_v1_1_1_hotfix/empaquetar_y_validar_hotfix.py
```

## Salida

- `outputs/infraestructura_agentes_skills_v1_1_1_hotfix/REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX/`
- `.../REVISION_INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX.zip`
- `.../CHECKSUMS_SHA256.txt`
- `.../HOTFIX_VALIDATION_REPORT.json`
