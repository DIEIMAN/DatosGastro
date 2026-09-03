# Criterios de limpieza

## Texto

- Reparar mojibake comun con `ftfy` si esta instalado y con reemplazos controlados.
- Compactar espacios, tabs y saltos de linea.
- Preservar nombres propios cuando el origen ya trae capitalizacion util.
- Normalizar mayusculas/minusculas solo cuando el proceso lo requiere.
- Quitar tildes solo para matching tecnico, no para campos finales legibles.

## Barrios y comunas

- Usar catalogo CABA Ley 2650 incluido en `src/config.py`.
- Normalizar variantes como `San Cristobal`, `San Cristobal`, `Montserrat` y mayusculas.
- Derivar comuna desde barrio normalizado.
- Marcar `requiere_validacion = si` si el barrio no matchea o es ambiguo.
- Caso `Retiro/San Nicolas`: no se fuerza un barrio sin direccion suficiente; queda para validacion/geocodificacion.

## Ubicaciones

- `U00000` representa ubicacion no determinada o evento sin sede fija.
- La normalizacion offline no consulta internet.
- USIG queda preparado como criterio futuro, no como dependencia para correr el pipeline.

## Categorias gastronomicas

La taxonomia V2 evita categorias innecesarias y genera:

- `es_gastronomico`
- `categoria_gastronomica_inferida`
- `confianza_categoria`
- `motivo_categoria`

Cada clasificacion se basa en keywords trazables o queda como `Requiere validacion`.
