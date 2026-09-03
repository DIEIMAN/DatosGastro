# Auditoría del portal de datos abiertos — F02 y F01 (2026-08-27)

Consulta a la API CKAN de `data.buenosaires.gob.ar` para responder una sola pregunta: ¿hay
algo más actualizado que lo que tenemos en `data/raw`?

## Lo que hay en el dataset "Habilitaciones Aprobadas"

El dataset se modificó por última vez el 2026-08-12 y publica dieciocho recursos (CSV y
XLSX de cada período). Frente a nuestros archivos locales:

| archivo local | vs portal | última modificación del recurso |
|---|---|---|
| 2015_2018 | idéntico | 2024-11-26 |
| 2019 | idéntico | 2024-11-26 |
| 2020 | idéntico | 2024-11-26 |
| 2021 | idéntico | 2024-11-26 |
| 2022 | idéntico | 2024-11-26 |
| 2023 | idéntico | 2024-11-26 |
| 2024 | idéntico | 2025-01-13 |
| 2025 | difiere en 26 filas | 2026-08-03 |

Siete de los ocho archivos locales están al día byte a byte. Nada que rebajar.

## Hay un archivo 2026, y no sirve para lo que esperábamos

Existe `habilitaciones-aprobadas2026.csv` (recurso `1ee0b29d`, publicado el 2026-05-21).
Lo bajé y lo perfilé:

- 145.475 filas contra 145.457 del 2025: **es el mismo padrón**, con 18 filas de
  diferencia.
- Mismo esquema (`razon_social`, `rubro`, `domicilio`, `comuna`, `nropartidamatriz`,
  `disposicion`), pero **con delimitador `;` en vez de coma**: un noveno dialecto.
- Sus disposiciones van de 2014 a 2020 (43.539 de 2015, 58.132 de 2016, ninguna posterior
  a 2020).

O sea: los archivos llamados `2025` y `2026` no son habilitaciones de esos años. Son un
padrón acumulado congelado, republicado con otro formato y otra fecha de portada. El año
del nombre es el de la publicación, no el del dato.

**No lo incorporé a `data/raw` a propósito**: sumarlo duplicaría cada establecimiento del
padrón en todos los estudios de rubro. Queda documentado en `src/config.py` (entrada
`F02_2026`, con `download_url` deliberadamente en `None` para que `download_sources.py` no
lo baje solo).

## Conclusión

**El portal no aporta registros cuya fecha interna sea posterior a 2024.** Sí existen
recursos llamados 2025 y 2026, pero esos nombres corresponden a la publicación y no al
período del contenido. El techo temporal del proyecto no es un problema de descarga:
conseguir 2025-2026 exige pedir a AGC la serie correcta o la aclaración formal del alcance.

## F01, de paso

El dataset "Oferta y Establecimientos gastronómicos" figura modificado el 2026-07-22, pero
sus siete recursos son todos del 2019-08-05: la fecha del dataset se movió por metadatos,
no por dato nuevo. Nuestro archivo local corresponde al recurso
`establecimientos_gastronomicos.csv` y está al día.

El dataset publica además un segundo CSV con otro nombre, `oferta_gastronomica.csv`.
Lo bajé para descartar que fuera otro universo: es **byte a byte idéntico** al que ya
tenemos (438.717 bytes, 2.823 registros). Son el mismo archivo publicado dos veces.

## Otras fuentes miradas

- El portal no tiene ningún dataset que responda a la búsqueda "gastronom" fuera de F01.
- "Mapa de Oportunidades Comerciales (MOC)" publica aperturas, cierres, rubros y zonas,
  pero todos sus recursos son de 2019. Sirve como contexto histórico, no como actualidad.
