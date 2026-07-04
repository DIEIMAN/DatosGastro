# QA — Revisión institucional Casas de Pastas

## Archivos encontrados (informe actual y materiales de soporte)

**Informe principal (fuente de la revisión):**

- `outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.md` — versión final del informe (Markdown editable). **Elegido como base.**
- `outputs/casas_pastas_reporte/INFORME_CASAS_PASTAS_INTEGRADO_V4.pdf` — PDF actual (no editado).
- `outputs/casas_pastas_reporte/PACK_REVISION_EXTERNA_254_V4/INFORME_CASAS_PASTAS_INTEGRADO_V4.md` — **copia idéntica** del anterior (verificada).

**Por qué se eligió `INFORME_CASAS_PASTAS_INTEGRADO_V4.md`:** es el Markdown más reciente y completo (universo depurado de 254 candidatos), tiene su PDF asociado con el mismo nombre y su copia en el pack de revisión externa coincide carácter por carácter. Es inequívocamente el informe final vigente.

**Materiales de soporte usados para metodología y anexos (no son "el informe"):**

- `docs/casas_pastas/NOTAS_METODOLOGICAS_INTEGRADO.md` — metodología del padrón integrado.
- `docs/casas_pastas/NOTAS_METODOLOGICAS.md` — criterios A/B/C, deduplicación, geocodificación.
- `docs/casas_pastas/GOOGLE_PLACES_PILOTO.md` — piloto Google Places (contexto de fuente).
- `docs/casas_pastas/PLAN_PDF_CASAS_PASTAS.md` — plan editorial previo (corresponde a una etapa anterior de 10 establecimientos AGC).
- `outputs/casas_pastas_reporte/integrado_sanitizado/*_v3_depurado.csv` — agregados sanitizados del universo de 254 (usados para las tablas completas del Anexo B).
- `outputs/casas_pastas_reporte/*.csv` — tablas sanitizadas de una etapa anterior (universo AGC 10). **No se usaron para las cifras del cuerpo** para no mezclar universos.

## Archivos creados

Todos en `docs/casas_de_pastas/revision_institucional/`:

1. `INFORME_CASAS_DE_PASTAS_REVISION_INSTITUCIONAL.md` — nueva versión institucional.
2. `CAMBIOS_PROPUESTOS_CASAS_DE_PASTAS_REVISION_INSTITUCIONAL.md` — tabla de cambios.
3. `QA_CASAS_DE_PASTAS_REVISION_INSTITUCIONAL.md` — este documento.

## Nota sobre la carpeta de destino

El prompt pedía `docs/casas_de_pastas/revision_institucional/`. La carpeta del proyecto existente usa **guion bajo** (`docs/casas_pastas/`). Se respetó el nombre pedido en el prompt y se creó `docs/casas_de_pastas/` (con "de"), separada de la carpeta técnica existente, para no mezclar la revisión institucional con las notas técnicas. Ambas conviven; ninguna se modificó.

## Confirmaciones

| Ítem | Estado |
|---|---|
| ¿Se tocó el informe original (V4 md/pdf)? | **No.** Intacto. |
| ¿Se editó el PDF? | **No.** |
| ¿Se tocaron datos fuente? | **No.** Solo se leyeron agregados sanitizados y notas. |
| ¿Se generó PDF? | **No.** |
| ¿Se generó DOCX? | **No.** |
| ¿Se sacó DataGastro como marca pública? | **Sí.** Título y firma ahora son DGDGAS — Dirección General de Desarrollo Gastronómico. |
| ¿Se agregó índice? | **Sí.** Con secciones numeradas. |
| ¿Se numeraron las secciones? | **Sí** (1 a 10). |
| ¿Se concentró la metodología? | **Sí** (sección 3 + Anexo A). |
| ¿Anexos al final? | **Sí** (A–E). |
| ¿Se mantuvo la información existente? | **Sí.** Sin recortes de contenido relevante. |
| ¿Se inventaron datos/porcentajes/conclusiones? | **No.** |
| ¿Hubo commit? | **No.** |
| ¿Hubo push? | **No.** |
| ¿Hubo staging / git add? | **No.** |
| ¿Se tocó Cafecito? | **No.** |
| ¿Se tocó PolosGastro? | **No.** |
| ¿Se tocó Mercados? | **No.** (Solo se verificó que este informe no depende de esa estructura.) |

## Trazabilidad de las cifras

Todas las cifras del informe institucional provienen del informe V4 y/o de los agregados sanitizados `*_v3_depurado.csv` (universo de 254):

- 254 candidatos, 173 independientes / 81 cadenas, 53 multifuente, 252 georreferenciados → informe V4 + `resumen_integrado_v3_depurado.csv`.
- Composición por fuente (solo OSM 92, solo Google 90, Google+OSM 53, solo AGC 11, recall 7, documental 1) → `integrado_por_fuente_v3_depurado.csv`.
- Tablas por comuna y barrio (cantidad y densidad) → `integrado_por_comuna_v3_depurado.csv`, `integrado_por_barrio_v3_depurado.csv` y sus versiones de densidad.
- Cadenas → `cobertura_cadenas_e_independientes.csv` y §7 del V4.
- Casos documentales y limitaciones → informe V4 y `limitaciones_metodologicas.csv`.

## Pendiente / decisiones humanas

- **Revisión humana** del recorte editorial (qué queda en cuerpo vs anexo).
- Decidir si esta versión **reemplaza** al V4 como pieza principal o **convive** como versión institucional.
- Decidir si se conserva o no la firma de autoría personal (retirada del cuerpo público por defecto).
- Confirmar el nombre definitivo de la carpeta (`casas_de_pastas` con "de" vs `casas_pastas` técnica existente).
- Si se aprueba, decidir destino del render (PDF/DOCX) — no realizado por regla.
- Verificar títulos de sección "Mercados de Pastas": el prompt menciona "Casas de Pastas / Mercados de Pastas"; el informe original es "casas de pastas". Se mantuvo el doble nombre en el título por pedido, sin alterar el contenido, que refiere a casas de pastas.
