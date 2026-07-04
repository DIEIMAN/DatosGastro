# QA auditoria Fase 10 semilla

Fecha: 2026-07-02. Auditoria corta de calidad previa a una eventual geolocalizacion. No es
Borrador 4, no es informe final, no es PDF/DOCX y no aplica diseno.

## 1. Archivos revisados

- `docs/polos_gastro/fase7/DOCUMENTO_SEMILLA_POLOS_Y_LOCALES.md`
- `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/universo_polos_semilla_fase10.csv`
- `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/locales_semilla_polos_fase10.csv`
- `docs/polos_gastro/fase10_reencuadre_y_locales/QA_FASE10_REENCUADRE_Y_LOCALES.md`

## 2. Archivos creados por esta auditoria

- `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/control_polos_semilla_fase10.csv`
- `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/control_locales_semilla_fase10.csv`
- `docs/polos_gastro/fase10_reencuadre_y_locales/AUDITORIA_CASOS_DELICADOS_FASE10.md`
- `docs/polos_gastro/fase10_reencuadre_y_locales/QA_AUDITORIA_FASE10_SEMILLA.md`

## 3. Resultado de control

| Indicador | Resultado |
| --- | ---: |
| Polos/ejes esperados del documento semilla | 22 |
| Polos/ejes encontrados en tabla Fase 10 | 22 |
| Polos faltantes | 0 |
| Menciones local-polo esperadas | 106 |
| Menciones local-polo encontradas | 106 |
| Locales faltantes | 0 |
| Filas con flags obligatorios correctos en locales semilla | 106 |

## 4. Faltantes

No se detectaron polos faltantes ni locales faltantes respecto del documento semilla.

Los polos sin locales explicitos no son faltantes: el documento semilla los registra con "Sin
locales destacados en el listado disponible". Deben pasar a busqueda complementaria antes de armar
una capa de puntos.

## 5. Duplicados y ambiguedades

Duplicados deliberados o referencias compartidas:

- Abasto y Avenida Corrientes comparten el mismo bloque de seis locales. Se conserva en ambos por
  trazabilidad semilla.
- Nino Gordo aparece asociado a Palermo, Villa Crespo como zona limite y Chacarita como Nino Gordo
  Burger House.
- La Fuerza aparece en Villa Crespo y Chacarita.
- Cafe Registrado aparece en Palermo y Avenida Caseros / Barracas.
- La Mar aparece en Palermo y Belgrano.
- Sottovoce aparece en Puerto Madero y Recoleta.
- Napoles / Napoles Caseros requiere diferenciar sedes.
- Hierbabuena aparece en San Telmo y Avenida Caseros / Barracas.
- Anafe / Anafe original requiere control de denominacion.

Hitos o espacios colectivos:

- Mercado de San Telmo.
- Patio de los Lecheros.
- El Mercado / Faena.

## 6. Preparacion para Google Places

La tabla esta lista como base semilla para una futura geolocalizacion, con estas condiciones:

- no ejecutar Google Places hasta tener autorizacion explicita;
- agregar una columna de query propuesta antes de llamar API;
- revisar manualmente nombres ambiguos y sucursales;
- mantener `place_id`, ratings, volumenes de resenas y raw como campos internos si se autoriza la
  fase;
- no usar Google Places como padron oficial ni para decidir existencia de polos;
- no publicar puntos sin revision manual.

## 7. Controles de alcance

| Control | Resultado |
| --- | --- |
| Se llamo Google Places | No |
| Se usaron API keys | No |
| Se imprimieron API keys | No |
| Se tocaron datos fuente | No |
| Se toco Borrador 2 | No |
| Se toco Borrador 3 | No |
| Se tocaron Cafecito, Mercados o Casas de Pastas | No |
| Se genero PDF | No |
| Se genero DOCX | No |
| Se generaron mapas | No |
| Hubo commit | No |
| Hubo push | No |
| Hubo staging / git add | No |

## 8. Control de privacidad y campos internos

Se revisaron los archivos de Fase 10 con patrones de API keys, emails, telefonos, CUIT, DNI y links
privados.

Resultado:

- API keys de Google: sin hallazgos.
- Emails: sin hallazgos.
- Telefonos: sin hallazgos.
- Links privados de Drive/Docs: sin hallazgos.
- CUIT/DNI: los hits del patron amplio corresponden a falsos positivos por la palabra "circuito" y
  por la propia linea de QA que declara "DNI: sin hallazgos".
- `place_id`: aparece solo como campo interno/no publicable en documentos metodologicos y esquema
  Google Places. No hay valores reales de `place_id`.

## 9. Proximos pasos recomendados

1. Revisar manualmente las ambiguedades de sucursales y nombres.
2. Crear, en una fase posterior autorizada, una tabla de queries Google Places sin ejecutar API.
3. Definir criterio para polos sin locales explicitos: busqueda complementaria documental primero,
   seleccion de referencias despues.
4. Definir tratamiento cartografico para Abasto/Corrientes y puntos compartidos.
5. Mantener esta capa como insumo interno hasta completar revision manual y QA de privacidad.
