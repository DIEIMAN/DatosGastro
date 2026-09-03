# Resumen metodologico - Google Places microzonas ampliacion completa v1

Estado: EXPERIMENTAL / no oficial. No define limites oficiales ni acredita locales activos.
Google Places se usa como senal auxiliar no oficial de oferta visible.

## Alcance

- Piloto: 379 consultas.
- Tanda A criticas: 351 consultas.
- Tanda B consolidacion: 260 consultas.
- Refinamiento puntual Chacarita: 18 consultas sobre `MZ_CHACARITA_C044` y `MZ_CHACARITA_C075`.

Consultas nuevas reales desde la autorizacion USD 15: 278.
Costo maximo adicional estimado: USD 9,73.
Margen remanente: 147 consultas / USD 5,27.

## Integracion

Fuentes separadas:

- F01+F02: oferta registrada / habilitaciones historicas.
- Google Places piloto.
- Google Places Tanda A.
- Google Places Tanda B.
- Google Places refinamiento Chacarita.

Reglas principales:

- contencion estricta por macrozona;
- deduplicacion por `place_id` entre tandas en tabla interna;
- deduplicacion contra F01+F02 por 15 m, o 40 m con nombre compatible;
- salidas sanitizadas sin `place_id`;
- tablas internas bajo `interno/`, ignorado por Git.

## Resultados

- Universo completo sanitizado: 6.461 puntos.
- F01+F02 en macrozonas: 3.240 puntos.
- Google Places nuevos incorporados: 3.221 puntos.
- Poligonos experimentales generados: 163.
- Mapas PNG generados: 11.

Puntos Google Places nuevos por zona:

- belgrano: 393
- caballito: 404
- caseros_barracas: 40
- chacarita: 213
- corrientes_microcentro: 661
- costanera_norte: 67
- palermo_soho_hollywood: 448
- puerto_madero: 209
- recoleta: 363
- san_telmo: 149
- villa_crespo: 274

## Saturacion

Celdas saturadas finales registradas:

- Tanda A: 2, ambas en Chacarita.
- Tanda B: 58: Recoleta 29, Villa Crespo 19, Caballito 10.

El refinamiento Chacarita 3x3 devolvio 35 puntos unicos, pero no agrego puntos nuevos
incorporables al universo completo luego de contencion y deduplicacion.

No se refinaron las 58 celdas de Tanda B: el refinamiento 2x2 completo requiere 232
consultas y excede el margen remanente de 165 consultas posterior a Tanda B. Un
refinamiento parcial seria metodologicamente sesgado si no se define antes un criterio
territorial de priorizacion.

## QA

- Errores API: 0 en Tanda B y 0 en refinamiento Chacarita.
- QA privacidad por celda: sin API keys, emails, CUIT/DNI, telefonos ni links privados.
- QA visual automatizado: los 11 mapas PNG existen, pesan mas de 10 KB y no son imagenes
  en blanco.
- No se guardo raw JSON de Google Places.

## Limitaciones

- Google Places mide oferta visible en la plataforma; no confirma habilitacion ni apertura
  actual.
- Recoleta, Villa Crespo y Caballito muestran saturacion relevante; conviene tratar esos
  resultados como densos pero potencialmente subcapturados en las celdas saturadas.
- La capa de poligonos es experimental y requiere revision humana antes de uso ejecutivo.
