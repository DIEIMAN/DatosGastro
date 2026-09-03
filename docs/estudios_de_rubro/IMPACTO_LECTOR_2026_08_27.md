# Qué cambia al arreglar el lector de F02 — 2026-08-27

## Lo que estaba mal

Cada estudio de rubro copiaba el lector del anterior. El heredado abría los ocho archivos
de F02 con delimitador coma y codificación única. Como los siete archivos 2015-2024 usan
`;`, caían en una sola columna: no fallaban, devolvían cero filas. El estudio quedaba
midiendo el archivo 2025 y publicaba un piso sin que nada avisara.

Al corregir el delimitador aparece el segundo error, más silencioso: forzar latin-1 sobre
archivos que son UTF-8 rompe los acentos justo en la nomenclatura moderna
(`ELABORACIÓN DE PRODUCTOS DE PANADERÍA`), y la normalización de texto convierte el rubro
en `elaboraci n de productos de panader a`, que ningún patrón reconoce.

## Efecto medido

Filas de F02 con rubro de pan o pasta, por archivo, leyendo bien contra leyendo mal:

| archivo | lectura equivocada | lectura correcta |
|---|---|---|
| 2015_2018 | 546 | 1.529 |
| 2019 | 53 | 254 |
| 2020 | 19 | 158 |
| 2021 | 33 | 362 |
| 2022 | 18 | 226 |
| 2023 | 4 | 22 |
| 2024 | 107 | 107 |
| 2025 | 394 | 1.765 |

En los estudios ya construidos, con el mismo clasificador y el mismo alcance:

| estudio | antes | después |
|---|---|---|
| Panaderías, universo A (núcleo) | 569 | 1.176 |
| Panaderías, A + B | 646 | 1.647 |
| Casas de pastas, universo A | 10 | 159 |
| Casas de pastas, A + B | 11 | 161 |

Las 10 casas de pastas eran el síntoma: el estudio veía un solo archivo.

La serie por año lo muestra igual de claro. Antes, el núcleo de panaderías tenía 2021 y
2023 en cero y 2020 en 3; ahora 2020 da 53, 2021 da 132 y 2023 da 8 (ese último por una
razón distinta, ver abajo). No eran años sin panaderías: eran años sin leer.

## Estado de cada salida

- **Panaderías** (`outputs/panaderias/`): regenerado con el lector corregido. Es un estudio
  nuevo, no había nada publicado contra los números viejos.
- **Casas de pastas** (`outputs/casas_pastas/`): **sin tocar**. El build corregido se corrió
  a una carpeta aparte para medir el efecto. Regenerar lo oficial deja el informe y el PDF
  ya entregados desalineados con sus propios datos, así que esa es una decisión de Diego,
  no del arreglo. Cuando se decida:
  `.venv/Scripts/python.exe scripts/casas_pastas/build_casas_pastas.py`
  y después rehacer el informe y el PDF, que citan 10 casas.

## Dos cosas de la fuente que conviene saber (no son del lector)

1. **El archivo llamado `2025` no trae habilitaciones de 2025.** Es un padrón con otro
   esquema (`razon_social`, `rubro`, `domicilio`) y sus disposiciones son de 2015-2018:
   de las 1.765 filas de rubro pan, 255 son 2015, 1.112 de 2016, 180 de 2017 y 56 de 2018.
   O sea: el proyecto **no tiene todavía ninguna habilitación posterior a 2024**.
2. **El archivo `2023` está subrepresentado en origen**: 5.063 filas contra 12.938 de 2020,
   31.829 de 2021 y 26.430 de 2022. La caída de 2023 en cualquier serie por año es de la
   fuente, no del rubro, y hay que decirlo cada vez que se publique la serie.

## Lo que quedó en el repo

- `scripts/shared/fuentes_locales/` — lector único de F01 y F02, con detección de dialecto
  por archivo, reparación de doble codificación y bloqueo de columnas personales.
- `tests/test_fuentes_locales.py` — 10 pruebas; falla si un archivo vuelve a quedar en una
  sola columna o si aparece una columna personal.
- `python -m scripts.shared.fuentes_locales.f02` — perfil por archivo; sale con código 1 si
  algún archivo queda en cero filas o sin rubro.
- `--out DIR` en los dos builders, para correr sin pisar entregables publicados.
- `COMO_ABRIR_UN_RUBRO_NUEVO.md` — la receta para el próximo rubro.

## Otros lectores de F02 que quedan en el repo

Revisé los demás consumidores. Ninguno cambia una cifra publicada, así que no los toqué:

- `scripts/barrido_ciudad/probar_smp_lotes.py` lee 2015-2024 con `;` (bien) y latin-1 (mal
  para siete archivos), pero sólo usa sección, manzana, parcela y partida, que son
  alfanuméricos sin acentos: el error no le llega al resultado. Si alguna vez se le agrega
  una columna de texto, tiene que pasar al módulo compartido.
- `scripts/barrido_ciudad/detectar_lotes_permisos.py` lee sólo el archivo 2025, con su
  esquema correcto.
- `scripts/polos_gastro/build_capa_objetiva_fase8_fuerte.py` fija `sep=";"` para los ocho
  archivos, incluido el 2025 que va por coma, pero es sólo para inventariar columnas y esa
  fuente está marcada `usada_en_fase = NO`.
