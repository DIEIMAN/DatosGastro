# Correspondencia de secciones · política V1 → V1.1

**Por qué existe este archivo.** `AGENTS.md` manda usar las skills de procedimiento de
`docs/infraestructura_agentes_skills_v1/skills/` bajo la política **V1.1**. Pero esas skills
fueron escritas contra la numeración de la **V1**, que cambió. Hoy varias mandan a leer la
sección equivocada.

Se corrige acá, con una tabla, en vez de editar diez archivos de skills: las skills V1 no se
sobrescriben (son históricas) y una tabla se mantiene en un solo lugar.

**Regla de lectura:** cuando una skill V1 cite «§N de la política», traducí con esta tabla antes
de buscar.

---

## Tabla de equivalencias

| V1 · sección citada | V1.1 · sección real | tema |
|---|---|---|
| §1 | §1 | Protección de datos |
| §2 | §2 | Superficies protegidas |
| §3 | §3 | Líneas experimentales |
| §4 | §4 | Git |
| §5 | §5 | Privacidad |
| **§6** | **§8** | **Trazabilidad y manifests** |
| §7 | §9 | Fuentes |
| **§8** | **§10** | **QA** |
| §9 | §11 | Decisiones humanas |
| §10 | §12 | Paralelo y carpetas exclusivas |
| §11 | §13 | Handoffs y entregas |
| **§12** | **§17** | **Incertidumbre y defensa de lo adoptado** |
| §13 | §14 | Entorno |
| §14 | §15 | Autorización humana |

Las dos filas que más importan son **§6 → §8** y **§8 → §10**, porque son las que citan
`auditar_entregable_experimental`, `auditar_evidencia_documental` y `qa_pdf_pagina_por_pagina`.

## Nota sobre §12 → §17

La V1.1 **no había reproducido** la sección de incertidumbre de la V1. Se restituyó el
2026-08-06 como **§17**, al final de la política para no renumerar nada. Cualquier skill V1 que
cite «§12 · Incertidumbre» apunta ahora a §17.

## Citas conocidas a corregir al leer

| skill V1 | cita | leer en su lugar |
|---|---|---|
| `auditar_entregable_experimental` | «§§1–5, 8, 14» | §§1–5, **§10**, **§15** |
| `auditar_evidencia_documental` | «§§7, 9, 12» | **§9**, **§11**, **§17** |
| `qa_pdf_pagina_por_pagina` | «§8» | **§10** |

---

*Si la política vuelve a renumerarse, se actualiza esta tabla y no las skills.*
