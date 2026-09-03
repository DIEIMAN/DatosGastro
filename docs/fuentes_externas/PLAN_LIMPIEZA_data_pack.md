# Plan de limpieza — `data/datagastro_fuentes_externas_pack/`

Generado para confirmación de Diego (guardrails #4 y skill 08).

> **RESUELTO (2026-06-19):** por decisión de Diego, el pack original NO se borró: se **movió** a
> `data/archive/_a_revisar/datagastro_fuentes_externas_pack/` (cuarentena, reversible). El `data/`
> raíz quedó limpio. Las ubicaciones canónicas son `docs/fuentes_externas/`,
> `config/fuentes_externas/` y `data/fuentes_externas/`.

## Situación

El contenido del ZIP de fuentes externas fue agregado manualmente dentro de `data/`. `data/` es
para datos fuente del pipeline (público/seed/raw), **no** para documentación, catálogos ni outputs
derivados. Por eso este pack estaba **mal ubicado**.

Ya se **copió** (no movido) cada archivo a su ubicación correcta y se verificó que las copias son
**byte a byte idénticas** a los originales (SHA-256):

| Archivo original en `data/datagastro_fuentes_externas_pack/` | Copiado a | Categoría |
| --- | --- | --- |
| `README_fuentes_externas.md` | `docs/fuentes_externas/` | documentación |
| `checklist_legal_y_metodologico.md` | `docs/fuentes_externas/` | documentación |
| `plantilla_pedido_convenio_datos.md` | `docs/fuentes_externas/` | documentación |
| `prompt_codex_fuentes_externas.md` | `docs/fuentes_externas/` | documentación |
| `acciones_diego.csv` | `docs/fuentes_externas/` | documentación (lista de acciones) |
| `matriz_fuentes_externas.csv` | `config/fuentes_externas/` | catálogo fuente |
| `matriz_fuentes_externas.xlsx` | `config/fuentes_externas/` | catálogo fuente |
| `campos_objetivo_integraciones.csv` | `config/fuentes_externas/` | esquema de campos |

Derivados generados a partir de la matriz (no estaban en el ZIP):
`config/fuentes_externas/catalogo_fuentes_externas.csv` / `.json` y
`data/fuentes_externas/fuentes_prioridad_{alta,media,baja}.csv`.

## Clasificación de limpieza

| Categoría | Ítem | Acción propuesta |
| --- | --- | --- |
| **Seguro borrar** (tras confirmar) | Carpeta completa `data/datagastro_fuentes_externas_pack/` | Borrar: ya está copiada íntegra y verificada por hash en `docs/` y `config/`. Es un duplicado. |
| **Revisar** | — | (nada) |
| **No borrar** | Las copias nuevas en `docs/fuentes_externas/`, `config/fuentes_externas/`, `data/fuentes_externas/` | Quedan como ubicación canónica |

## Confirmación pendiente

> **¿Confirmás que borre `data/datagastro_fuentes_externas_pack/`?**
> Es un duplicado exacto de lo ya reubicado. Si preferís conservarlo por las dudas, lo dejo y no
> se toca. No borro nada hasta tu OK.

Como red de seguridad, si querés, en lugar de borrar puedo moverlo a
`data/archive/_a_revisar/datagastro_fuentes_externas_pack/`.
