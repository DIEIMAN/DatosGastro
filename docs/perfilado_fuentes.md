# Perfilado de fuentes

Generado: 2026-06-10

El perfilado corre sobre los CSV disponibles en `data/raw/`. Los archivos `raw_*` se tratan como seed/manuales salvo evidencia de dataset completo.

## raw_establecimientos_gastronomicos.csv

- Ruta: `C:\proyectos\Gastronomia\DataGastro\data\raw\raw_establecimientos_gastronomicos.csv`
- Tamano: 1169 bytes
- Encoding: utf-8
- Separador: ','
- Filas x columnas: 6 x 12
- Columnas: id_raw | id_fuente | nombre_original | categoria_original | direccion_original | barrio_original | comuna_original | fecha_extraccion | calidad_dato | requiere_validacion | motivo_validacion | observaciones_raw
- Duplicados: 0
- Campos geograficos: direccion_original | barrio_original | comuna_original
- Campos temporales: fecha_extraccion
- Posible mojibake en muestra: 0
- Tipo estimado: seed/manual
- Recomendacion: usar como seed/fallback

## raw_eventos_gastronomicos.csv

- Ruta: `C:\proyectos\Gastronomia\DataGastro\data\raw\raw_eventos_gastronomicos.csv`
- Tamano: 1599 bytes
- Encoding: utf-8
- Separador: ','
- Filas x columnas: 6 x 12
- Columnas: id_raw | id_fuente | nombre_evento_original | fecha_original | ubicacion_original | organizador_original | precio_original | fecha_extraccion | calidad_dato | requiere_validacion | motivo_validacion | observaciones_raw
- Duplicados: 0
- Campos geograficos: ubicacion_original
- Campos temporales: fecha_original | fecha_extraccion
- Posible mojibake en muestra: 0
- Tipo estimado: seed/manual
- Recomendacion: usar como seed/fallback

## raw_ferias_mercados.csv

- Ruta: `C:\proyectos\Gastronomia\DataGastro\data\raw\raw_ferias_mercados.csv`
- Tamano: 1582 bytes
- Encoding: utf-8
- Separador: ','
- Filas x columnas: 6 x 14
- Columnas: id_raw | id_fuente | nombre_original | tipo_original | direccion_original | barrio_original | comuna_original | dias_horarios_original | gestion_original | fecha_extraccion | calidad_dato | requiere_validacion | motivo_validacion | observaciones_raw
- Duplicados: 0
- Campos geograficos: direccion_original | barrio_original | comuna_original
- Campos temporales: fecha_extraccion
- Posible mojibake en muestra: 0
- Tipo estimado: seed/manual
- Recomendacion: usar como seed/fallback

## raw_fuentes_relevadas.csv

- Ruta: `C:\proyectos\Gastronomia\DataGastro\data\raw\raw_fuentes_relevadas.csv`
- Tamano: 4250 bytes
- Encoding: utf-8
- Separador: ','
- Filas x columnas: 16 x 9
- Columnas: id_fuente_raw | nombre_fuente | organismo | tipo_fuente | url | formato | calidad_estimada | fecha_consulta | observaciones
- Duplicados: 0
- Campos geograficos: No detectados
- Campos temporales: fecha_consulta
- Posible mojibake en muestra: 0
- Tipo estimado: seed/manual
- Recomendacion: usar como seed/fallback

## raw_habilitaciones_aprobadas.csv

- Ruta: `C:\proyectos\Gastronomia\DataGastro\data\raw\raw_habilitaciones_aprobadas.csv`
- Tamano: 221 bytes
- Encoding: ascii
- Separador: ','
- Filas x columnas: 0 x 14
- Columnas: id_raw | id_fuente | anio | fecha_habilitacion | rubro_original | direccion_original | superficie | es_gastronomico | categoria_gastronomica_inferida | fecha_extraccion | calidad_dato | requiere_validacion | motivo_validacion | observaciones_raw
- Duplicados: 0
- Campos geograficos: direccion_original
- Campos temporales: anio | fecha_habilitacion | fecha_extraccion
- Posible mojibake en muestra: 0
- Tipo estimado: seed/manual
- Recomendacion: usar como seed/fallback

## raw_normativa_gastronomica.csv

- Ruta: `C:\proyectos\Gastronomia\DataGastro\data\raw\raw_normativa_gastronomica.csv`
- Tamano: 431 bytes
- Encoding: utf-8
- Separador: ','
- Filas x columnas: 1 x 12
- Columnas: id_raw | id_fuente | nombre_norma_original | tipo_norma | tema | fecha_original | url_fuente | fecha_extraccion | calidad_dato | requiere_validacion | motivo_validacion | observaciones_raw
- Duplicados: 0
- Campos geograficos: No detectados
- Campos temporales: fecha_original | fecha_extraccion
- Posible mojibake en muestra: 0
- Tipo estimado: seed/manual
- Recomendacion: usar como seed/fallback

## raw_programas_politicas.csv

- Ruta: `C:\proyectos\Gastronomia\DataGastro\data\raw\raw_programas_politicas.csv`
- Tamano: 2081 bytes
- Encoding: utf-8
- Separador: ','
- Filas x columnas: 6 x 11
- Columnas: id_raw | id_fuente | nombre_original | organismo_original | estado_original | descripcion_original | fecha_extraccion | calidad_dato | requiere_validacion | motivo_validacion | observaciones_raw
- Duplicados: 0
- Campos geograficos: No detectados
- Campos temporales: fecha_extraccion
- Posible mojibake en muestra: 0
- Tipo estimado: seed/manual
- Recomendacion: usar como seed/fallback
