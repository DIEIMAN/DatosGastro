# QA final — INFRAESTRUCTURA_AGENTES_SKILLS_V1_1_1_HOTFIX

Fecha: 2026-07-11
Estado: **HOTFIX DE EMPAQUETADO APROBABLE / PILOTO**

## Controles

| control | resultado |
| --- | --- |
| Manifest filas válidas | ver validación automática del script |
| Checksums internos válidos | ver validación automática |
| Encoding UTF-8 textos auditados | ver AUDITORIA_ENCODING_UTF8.json |
| Diff punteros UTF-8 | convertido si era UTF-16 |
| ZIP íntegro + extracción reverify | ver salida del script |
| Rutas absolutas en ZIP | prohibidas / validadas |
| `.claude/settings.json` | no tocado por este hotfix |
| Política / agentes / skills / E2E | no modificados |
| staging | debe estar vacío |
| commit / push | no |

## Causa del bug V1.1

`CHECKSUMS_INTERNO.txt` se firmó con el hash del manifest y luego el empaquetador **regeneró** `MANIFEST_CONTENIDO.csv`, invalidando la firma sin actualizar el checksums.

## Hash de referencia V1.1

- Incorrecto en CHECKSUMS_INTERNO: `aba38d7c25cae33c1413fa7ddbb4de6bcac3a274281c85d36f60c1cb928f6c80`
- Real del manifest empaquetado: `d480685d63d376aac4368607575dce2b4b300cee0ce4f98ffc7137206d83ba5c`
