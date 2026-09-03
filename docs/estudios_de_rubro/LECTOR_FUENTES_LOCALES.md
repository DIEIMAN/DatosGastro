# El lector compartido de F01 y F02

`scripts/shared/fuentes_locales/` es el único lugar del proyecto donde se decide cómo se
abre cada archivo crudo de las fuentes públicas locales. Todo estudio de rubro
(panaderías, casas de pastas, y los que vengan) lee por ahí.

Existe por un defecto concreto: cada estudio venía copiando el lector del anterior, y el
lector heredado entendía **un solo esquema** de F02. Los otros siete archivos no fallaban
—se leían como una sola columna y devolvían cero filas—, así que el estudio terminaba
midiendo un año y publicando un piso artificialmente bajo sin que nada avisara.

## Cómo es realmente F02

Ocho archivos, tres cosas que cambian entre ellos. Medido sobre `data/raw` el 2026-08-27:

| archivo | delimitador | codificación | esquema | rubro |
|---|---|---|---|---|
| 2015_2018 | `;` | utf-8 | legacy | `descripcion_rubro` |
| 2019 | `;` | utf-8 | legacy | `descripcion_rubro` |
| 2020 | `;` | utf-8 | legacy | `DescripcionRubro` + `DescripcionSubRubro` |
| 2021 | `;` | utf-8 | legacy | ídem, con columnas `Unnamed` de cola |
| 2022 | `;` | utf-8 (doble codificación adentro) | legacy | ídem |
| 2023 | `;` | utf-8 | legacy | ídem, `codigo_rubro` tipo `1.4.2` |
| 2024 | `;` | **cp1252** | legacy | ídem |
| 2025 | `,` | utf-8 | moderno | `rubro`, con `razon_social`; contenido histórico 2014-2020 |

Total local: 391.046 filas. El perfil se reproduce en cualquier momento con

```
.venv/Scripts/python.exe -m scripts.shared.fuentes_locales.f02
```

que además devuelve código de salida 1 si algún archivo quedó en cero filas o sin rubro
—que es exactamente el síntoma del lector roto.

El lector también contrasta el período declarado por el nombre del archivo con los años
detectados dentro de las disposiciones. Así, el recurso local rotulado 2025 queda marcado
como incoherente en vez de ser usado silenciosamente como información de 2025.

## Los dos errores que el módulo evita

1. **Delimitador único.** Leer los ocho con coma: los siete legacy caen en una sola
   columna y aportan cero. Es lo que hacía el lector de casas de pastas.
2. **Codificación única.** Leer todo lo legacy como latin-1: siete de los ocho archivos
   son UTF-8, y forzar latin-1 rompe los acentos justo en la nomenclatura moderna
   (`ELABORACIÓN DE PRODUCTOS DE PANADERÍA`). Como la normalización de texto descarta lo
   que no es `[a-z0-9 ]`, el rubro queda como `elaboraci n de productos de panader a` y el
   clasificador deja de reconocerlo. Sobre el crudo, la lectura equivocada pierde alrededor
   del 70 % de las filas con rubro de pan o pasta.

El archivo 2022 trae, además, UTF-8 releído como latin-1 y grabado así en origen. Se
repara al leer (`texto.reparar_mojibake`): pasa de 106 a 226 filas de rubro pan/pasta.

## Privacidad

El lector no expone `titulares`, `cuits`, `telefono`, `cod_postal_titular` ni `mail`: se
descartan en el parseo y no hay forma de pedirlos desde la API del módulo (guardrail 7).
Consecuencia metodológica: **las filas legacy vienen sin nombre de establecimiento** y se
identifican por partida matriz y domicilio. Sólo el archivo 2025 (esquema moderno) aporta
razón social.

## API

```python
from scripts.shared.fuentes_locales import iter_f02, iter_f01, normalizar

for reg in iter_f02():                 # los ocho archivos, cada uno con su dialecto
    reg.rubro_completo                 # rubro + subrubro, ya reparado
    reg.texto_clasificable             # rubro + nombre + descripción, sin datos personales
    reg.clave_habilitacion             # el LOCAL: solicitud+UF (legacy) o disposición (2025)
    reg.domicilio, reg.comuna, reg.id_registro, reg.anio_habilitacion
    reg.solicitud, reg.unidad_funcional, reg.partida_horizontal
    reg.esquema, reg.periodo, reg.archivo_origen
```

- `iter_f02(filtro=...)` aplica el filtro sobre el registro ya normalizado; conviene usarlo
  para no materializar 391.000 filas cuando el estudio quiere las de un rubro.
- `iter_f01()` da lo mismo para la oferta gastronómica, con `lat`/`lon` ya convertidos.
- `perfilar_f02()` devuelve el diagnóstico por archivo.

### Agrupar por local, no por inmueble

`id_registro` es la **partida matriz**, que identifica la parcela. Agrupar por ella fusiona
locales distintos de un mismo edificio: en el universo de panaderías, el 51 % de los
inmuebles aloja más de una habilitación. Lo que hay que usar es **`clave_habilitacion`**,
que resuelve la diferencia entre esquemas:

- en los siete archivos viejos es `solicitud` más la unidad funcional, si la trae;
- en el de 2025, que no publica la solicitud, es la `disposicion` (3.500 disposiciones
  sobre 2.947 partidas: contar por partida sub-cuenta también ahí);
- queda vacía en el 4,7 % de las filas modernas que no traen disposición, y ahí el estudio
  tiene que caer a partida + nombre.

Dos cosas que el lector normaliza y que un estudio no debería re-resolver:

- La unidad funcional viene como `0001`, como `1;1` (el mismo código repetido por parcela)
  y como `0002;0001` (un trámite sobre dos UF). Se normaliza a `1`, `1` y `1;2`.
- En las filas corridas de 2021 esa columna recibe texto de rubro (`BOTONERIA`, `churros`).
  Se descarta: sólo se aceptan valores numéricos.

Lo que el lector **no** resuelve, porque es decisión de cada estudio: dos habilitaciones
sucesivas del mismo local se cuentan dos veces, y el mismo trámite puede estar publicado en
un archivo viejo y en el de 2025 con claves de espacios distintos. Cómo se midió y se unió
lo segundo en panaderías está en `docs/panaderias/NOTAS_METODOLOGICAS.md`, sección
"Deduplicación".

`tests/test_fuentes_locales.py` es el control de regresión: verifica que ningún archivo
quede en una sola columna, que todos traigan rubro, que el año sea de cuatro dígitos, que
no salgan columnas personales y que la clave de habilitación se arme igual en los dos
esquemas.

## Recordatorio permanente

F02 son **habilitaciones / registros administrativos**, no locales activos (guardrail 5).
Ningún estudio de rubro puede presentar estas filas como "locales abiertos".
