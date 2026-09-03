# Handoff — lector compartido de fuentes locales (2026-08-27)

## Qué se hizo

Se sacó la lectura de F01/F02 de cada estudio de rubro y se puso en un módulo único,
`scripts/shared/fuentes_locales/`. El defecto que motivó el trabajo: cada estudio copiaba
el lector del anterior, y el heredado entendía un solo esquema de F02; los otros siete
archivos devolvían cero filas sin fallar, así que el estudio publicaba un piso artificial.

Al corregirlo apareció un segundo error, más silencioso: forzar latin-1 sobre archivos que
son UTF-8 rompe los acentos de la nomenclatura moderna y el clasificador deja de reconocer
el rubro.

## Efecto

| | antes | después |
|---|---|---|
| Panaderías, universo A | 569 | 1.176 |
| Panaderías, A + B | 646 | 1.647 |
| Casas de pastas, universo A | 10 | 159 |

Detalle y tabla por archivo: `docs/estudios_de_rubro/IMPACTO_LECTOR_2026_08_27.md`.

## Archivos tocados

Nuevos:
- `scripts/shared/fuentes_locales/{__init__,f02,f01,texto}.py`
- `tests/test_fuentes_locales.py` (15 pruebas)
- `docs/estudios_de_rubro/{LECTOR_FUENTES_LOCALES,COMO_ABRIR_UN_RUBRO_NUEVO,IMPACTO_LECTOR_2026_08_27,ACCIONES_PARA_DIEGO}.md`

Modificados:
- `scripts/panaderias/build_panaderias.py` — usa el lector compartido; acepta `--out DIR`.
- `scripts/casas_pastas/build_casas_pastas.py` — ídem.
- `docs/panaderias/{README_PANADERIAS,NOTAS_METODOLOGICAS}.md` — números actualizados.
- `CLAUDE.md` — sección "Estudios de rubro".

Regenerado: `outputs/panaderias/` (estudio nuevo, nada publicado dependía de las cifras
anteriores).

**No tocado a propósito:** `outputs/casas_pastas/`. El build corregido se corrió a una
carpeta aparte; regenerar lo oficial desalinea el informe y el PDF ya entregados, que
citan 10 casas. Es decisión de Diego.

## Estado de verificación

- `python -m unittest discover tests` → 85 tests OK.
- `python -m scripts.shared.fuentes_locales.f02` → los ocho archivos con filas y rubro.
- Los dos builds corren de punta a punta.

## Lo que sigue

`docs/estudios_de_rubro/ACCIONES_PARA_DIEGO.md`. Lo urgente de ahí: el archivo F02
llamado `2025` no trae habilitaciones de 2025 (sus disposiciones son 2015-2018), así que
el proyecto no tiene ningún dato posterior a 2024, y el archivo 2026 está configurado pero
no descargado.
