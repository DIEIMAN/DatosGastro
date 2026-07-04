# Resumen de locales semilla - Fase 10

Fecha de trabajo: 2026-07-02. Documento interno. La tabla de locales semilla no es padron, ranking,
guia comercial ni prueba de vigencia operativa.

## 1. Base usada

Se extrajeron las menciones de locales, bares, restaurantes, cafeterias, mercados e hitos
gastronomicos desde:

- `docs/polos_gastro/fase7/DOCUMENTO_SEMILLA_POLOS_Y_LOCALES.md`

La tabla generada queda en:

- `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/locales_semilla_polos_fase10.csv`

## 2. Total extraido

Se extrajeron **106 menciones local-polo** desde el documento semilla.

El conteo es por polo. Si una misma referencia aparece en mas de un polo, se conserva en ambos
porque la tabla prepara una capa de puntos por polo y debe respetar el origen semilla.

## 3. Cantidad por polo

| Polo | Locales semilla extraidos |
| --- | ---: |
| Palermo | 19 |
| Belgrano | 11 |
| Puerto Madero | 9 |
| Villa Crespo | 9 |
| Recoleta | 8 |
| San Telmo | 8 |
| Chacarita | 7 |
| Microcentro y Centro | 7 |
| Abasto | 6 |
| Avenida Corrientes | 6 |
| Costanera Norte | 6 |
| Avenida Caseros / Barracas | 5 |
| Caballito | 5 |
| Avenida Boedo | 0 |
| Corredor DoHo / Donado-Holmberg | 0 |
| Circuito gastronomico de Paternal | 0 |
| Devoto | 0 |
| Nuevo Bajo Retiro / Esmeralda y Paraguay | 0 |
| Parque Saavedra / Avenida Garcia del Rio | 0 |
| Villa Pueyrredon / Avenida San Martin | 0 |
| Villa Urquiza | 0 |
| Avenida Federico Lacroze, desde Libertador hasta Cabildo | 0 |

## 4. Polos con mas locales semilla

Los polos con mayor cantidad de menciones son Palermo, Belgrano, Puerto Madero y Villa Crespo. Esta
lectura no debe interpretarse como ranking de densidad, vigencia ni importancia. Solo refleja la
cantidad de referencias incluidas en el documento semilla.

## 5. Polos con pocos o ningun local explicito

Los polos sin locales explicitos requieren una busqueda complementaria prioritaria si se quiere
preparar fichas o una capa de puntos:

- Avenida Boedo.
- Devoto.
- Corredor DoHo / Donado-Holmberg.
- Villa Urquiza.
- Nuevo Bajo Retiro / Esmeralda y Paraguay.
- Avenida Federico Lacroze, desde Libertador hasta Cabildo.
- Parque Saavedra / Avenida Garcia del Rio.
- Circuito gastronomico de Paternal.
- Villa Pueyrredon / Avenida San Martin.

La ausencia de locales explicitos no implica descarte del polo. Indica que la informacion
complementaria esta pendiente.

## 6. Dudas de normalizacion

Requieren revision manual de nombre, sucursal o subzona:

- Aldo's Palermo.
- Francisca del Fuego / Distrito Arcos.
- Pa' Pastar.
- Cafe Registrado, por aparicion en mas de un polo.
- La Fuerza, por aparicion en Villa Crespo y Chacarita.
- Nino Gordo / Nino Gordo Burger House.
- La Mar, por aparicion en Palermo y Belgrano.
- Anafe / Anafe original.
- Sottovoce / Sottovoce Recoleta.
- Napoles / Napoles Caseros.
- El Mercado / Faena.
- La Parolaccia Casa Tua.
- Lo de Jesus, sucursal Costanera.
- Caseros 3039, porque el nombre puede confundirse con una direccion.
- Locales del listado Corrientes/Abasto, porque el mismo bloque aparece en ambos polos.

## 7. Proximos pasos de geolocalizacion

1. Preparar queries de geolocalizacion para cada local semilla, combinando nombre + polo + CABA.
2. Geolocalizar primero los 106 registros obligatorios del documento semilla.
3. Revisar manualmente coincidencias, sucursales, duplicados y casos con nombre ambiguo.
4. Marcar puntos publicables y no publicables por separado.
5. Mantener `place_id`, rating, cantidad de resenas y raw de Google Places como informacion interna
   si se autoriza una fase posterior.
6. No publicar mapas finales hasta tener revision manual y criterio visual aprobado.

