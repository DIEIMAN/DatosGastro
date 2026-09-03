# Compatibilidad del handoff documental V1.1

**Estado:** COMPATIBLE  
**Fecha de lectura:** 2026-07-11  
**Rol:** `cartografo_territorial`  
**Infraestructura:** política V1.1 con hotfix V1.1.1  
**Alcance:** actualización documental del preflight V3; no se ejecutó la corrida territorial.

## Handoff vigente

| Campo | Valor |
| --- | --- |
| Ruta | `docs/polos_gastro/evidencia_documental_integrada_v1_1/HANDOFF_DOCUMENTAL_CARTOGRAFO_V1_1.md` |
| Formato | Markdown UTF-8 |
| Tamaño | 10120 bytes |
| SHA-256 | `ed588e728eb591ddae3c758a7c23789067a9fe9e8a5a5e32adc80afa4f5f2048` |
| Estado declarado | Evidencia integrada; apta para contraste espacial en Belgrano, Recoleta y Costanera Norte |
| Sustitución | Reemplaza para toda ejecución futura al handoff V1; V1 queda como antecedente histórico de solo lectura |

Handoff sustituido: `docs/polos_gastro/evidencia_documental_integrada_v1/HANDOFF_DOCUMENTAL_CARTOGRAFO_V1.md`, 9551 bytes, SHA-256 `3735a6d803774e1c4c2d099a83d6109f33d14bfb5a7052815b7fd494c918ae7a`.

## Archivos asociados revisados

La línea documental V1.1 contiene nueve archivos. Para esta compatibilidad se revisaron como insumos obligatorios:

| Archivo | Bytes | SHA-256 | Uso |
| --- | ---: | --- | --- |
| `HANDOFF_DOCUMENTAL_CARTOGRAFO_V1_1.md` | 10120 | `ed588e728eb591ddae3c758a7c23789067a9fe9e8a5a5e32adc80afa4f5f2048` | Instrucción documental vigente. |
| `DECISIONES_Y_USOS_DOCUMENTALES.md` | 10796 | `14b093cc50440c25cf4d974c6d2acaeb162ae25bf7ac59428aa9718fabc720cc` | Decisiones cerradas y reglas de uso. |
| `CONTRADICCIONES_Y_VACIOS_DOCUMENTALES.md` | 5990 | `247c05945e43b975d7bf76a997fcd5dba0860f814bea6a71a7a81cb540c02bbe` | Correcciones, tensiones y registro futuro de desacuerdos. |
| `MATRIZ_EVIDENCIA_DOCUMENTAL_INTEGRADA.csv` | 29104 | `eab8fdac71c656264f7d5528f2690fa3437f764ebd37d4bcce4bd76235e5e308` | Evidencias, inferencias y decisiones trazables. |
| `COSTANERA_NORTE_EVIDENCIA_DOCUMENTAL_INTEGRADA.md` | 8504 | `1fb508b2be837e8660904fc56111a59af8eb915c192ddd2309a2cfac5223d177` | Aplicación de DEC-05 y DEC-10 a Costanera Norte. |

También están disponibles `BELGRANO_EVIDENCIA_DOCUMENTAL_INTEGRADA.md`, `RECOLETA_EVIDENCIA_DOCUMENTAL_INTEGRADA.md`, `BIBLIOGRAFIA_DOCUMENTAL_VERIFICADA.csv` y `README_EVIDENCIA_DOCUMENTAL_INTEGRADA.md`. Todos permanecen sin modificación.

## Validación de la matriz

| Control | Esperado | Verificado | Resultado |
| --- | ---: | ---: | --- |
| Filas totales | 54 | 54 | OK |
| Evidencias originales | 42 | 42 | OK |
| Inferencias | 4 | 4 | OK |
| Decisiones institucionales | 8 | 8 | OK |
| `REC-R02` | Rechazada; solo uso interno | Fortaleza `RECHAZADA`, contradicción `CONTENIDO_NO_COINCIDE`; cifra atribuida a San Telmo | OK |
| `CN-DEC03` | Registrar DEC-10 | DEC-10, cuatro componentes incluido `CN_C02`, cuerpo y cartografía principal | OK |

Las 42 evidencias originales se preservan con los IDs `BEL-E01–BEL-E14`, `REC-R01–REC-R12` y `CN-01–CN-16`.

## Comparación acotada V1 vs. V1.1

| Tema | Handoff V1 | Handoff V1.1 | Impacto operativo |
| --- | --- | --- | --- |
| Handoff de entrada | Línea `evidencia_documental_integrada_v1` | Línea `evidencia_documental_integrada_v1_1` | Toda futura corrida debe citar V1.1; V1 es histórico. |
| Matriz | 53 filas | 54 filas | Se agrega la decisión institucional `CN-DEC03` / DEC-10. |
| Estatus Costanera | Exploratoria; DEC-05/06; anexo | Polo adoptado; DEC-05 + DEC-10; cuerpo y cartografía principal | Cambia jerarquía editorial y salida esperada. |
| `CN_C02` | Incluido, pero el preflight V3 conciliaba su rol como contexto | Cuarto componente obligatorio y pleno | Debe estar en capa analítica y de presentación; no se revalida su jerarquía. |
| Dependencia de Places | Condicionaba la lectura exploratoria | Se documenta una vez en método | No elimina ni degrada `CN_C02`; sigue siendo una limitación de fuente. |
| Retorno a decisión humana | Podía incluir cambio de estatus o ubicación de `CN_C02` | Solo eliminar, fusionar o alterar componentes requiere retorno | La existencia y jerarquía de Costanera ya están adoptadas. |
| Belgrano | Unidad macro, estructuras internas, nombres post hoc | Sin cambios sustantivos | Se conserva el plan V3. |
| Recoleta | Unidad general vs máximo dos subzonas | Sin cambios sustantivos | Se conserva el plan V3. |

No se compararon exhaustivamente todas las fuentes porque no era necesario para determinar el cambio de ejecución.

## Compatibilidad con el preflight V3

- Los 24 insumos espaciales siguen existiendo y sus hashes coinciden con `MATRIZ_INSUMOS_Y_DEPENDENCIAS.csv`: **24/24 OK**.
- Los tres scripts previstos mantienen sus hashes; siguen siendo reutilizables como referencia o base derivada en una línea nueva.
- CRS, campos, universos, filtros y métricas del inventario V3 no cambian.
- Las superficies registradas en `PROTECTED_SURFACES.yaml` siguen siendo de solo lectura.
- No hace falta agregar un insumo espacial; sí se agrega la línea documental V1.1 como entrada normativa obligatoria.
- Hace falta un paso específico de correspondencia documental para `CN_C01–CN_C04`, incorporado en el plan V3.1.

## Dictamen

El handoff V1.1 es compatible con el preflight técnico. El único cambio material es normativo/editorial: DEC-10 supera el tratamiento exploratorio de Costanera y cualquier instrucción que reduzca `CN_C02` a contexto secundario. No existe bloqueo técnico real para iniciar la corrida cuando se reciba la instrucción de ejecución.

