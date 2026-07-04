# Auditoria de casos delicados - Fase 10

Fecha: 2026-07-02. Documento interno de control antes de una eventual geolocalizacion. No se llamo
a Google Places, no se usaron API keys y no se tocaron datos fuente.

## 1. Resultado general

La extraccion de Fase 10 esta completa respecto del documento semilla: los 22 polos/ejes esperados
estan presentes y las 106 menciones local-polo fueron incorporadas a la tabla de locales semilla.

La base esta lista como insumo para preparar queries de geolocalizacion, con una condicion: antes
de ejecutar Google Places debe hacerse una revision manual de nombres ambiguos, sucursales,
duplicados deliberados y tipos de punto colectivo.

## 2. Belgrano R

Belgrano R no aparece como fila independiente en el universo semilla porque el documento semilla lo
incluye dentro de la macroarea Belgrano, junto con Barrio Chino y Bajo Belgrano. La tabla de Fase 10
conserva correctamente `Belgrano` como unidad semilla y documenta la macroarea en sus notas.

Control: Belgrano R debe mantenerse visible en fichas o notas de Belgrano, aunque no tenga locales
explicitos propios diferenciados en el detalle. No corresponde borrarlo ni convertirlo en polo
nuevo sin decision metodologica posterior.

## 3. Abasto y Avenida Corrientes

Abasto y Avenida Corrientes estan presentes como dos polos/ejes separados. La tabla de locales
conserva el mismo bloque de seis referencias en ambos casos:

- Guerrin.
- Las Cuartetas.
- El Palacio de la Pizza.
- Pertutti.
- La Reina Kunti.
- Moulin Bleu.

Esto no es un error de extraccion: refleja que el documento semilla vincula ambos casos. La
recomendacion es mantener ambos ejes y resolver la lectura como casos vinculados, con nota cruzada,
sin fusionar ni borrar ninguno.

Para Google Places, el riesgo es duplicar puntos en un mapa si se publican ambas capas sin regla
editorial. La solucion recomendada es conservar ambos registros en la tabla interna y decidir luego
si el mapa muestra un punto compartido, un punto por eje o una nota de vinculacion.

## 4. Polos con pocos o ningun local semilla explicito

Los siguientes polos estan correctamente incluidos en el universo, pero no tienen locales explicitos
en el documento semilla:

- Avenida Boedo.
- Devoto.
- Corredor DoHo / Donado-Holmberg.
- Villa Urquiza.
- Nuevo Bajo Retiro / Esmeralda y Paraguay.
- Avenida Federico Lacroze, desde Libertador hasta Cabildo.
- Parque Saavedra / Avenida Garcia del Rio.
- Circuito gastronomico de Paternal.
- Villa Pueyrredon / Avenida San Martin.

Estos casos no deben tratarse como faltantes de la tabla de locales. Deben marcarse como polos con
informacion complementaria pendiente para una fase de busqueda documental y seleccion de referencias
gastronomicas. Para Google Places, no conviene consultar genericos de polo sin antes definir
criterios de seleccion, porque eso podria convertir una busqueda abierta en pseudo-padron.

## 5. Locales con nombres ambiguos, sucursales o marcas repetidas

Requieren control manual antes de geolocalizar:

| Local o marca | Polos afectados | Riesgo | Accion recomendada |
| --- | --- | --- | --- |
| La Fuerza | Villa Crespo; Chacarita | Sucursal o sede distinta. | Usar query con barrio y revisar match manual. |
| Nino Gordo | Palermo; Villa Crespo; Chacarita como Nino Gordo Burger House | Marca/nombre compartido y zona limite. | Separar sede, marca y nota territorial antes de mapa. |
| Cafe Registrado | Palermo; Avenida Caseros / Barracas | Sucursal no explicitada en todos los casos. | Confirmar sede por polo. |
| La Mar | Palermo; Belgrano | Puede referir a sede o referencia de zona. | Confirmar punto correcto antes de geolocalizar. |
| Sottovoce | Puerto Madero; Recoleta | Sucursales distintas. | Usar query con polo/barrio y revisar coincidencia. |
| La Continental | Microcentro y Centro | Cadena con varias sucursales. | Confirmar sucursal del area central. |
| SushiClub | Palermo | Cadena con posibles sucursales. | Confirmar sucursal Palermo. |
| Napoles | San Telmo; Avenida Caseros como Napoles Caseros | Posible sede diferenciada. | Confirmar si son puntos distintos. |
| Hierbabuena | San Telmo; Avenida Caseros / Barracas | Segunda sede en semilla. | Confirmar sede de Caseros. |
| Anafe | Chacarita; Belgrano como Anafe original | Nombre relacionado con origen/sucursal. | Revisar punto correcto y denominacion. |
| El Muelle | Costanera Norte | Nombre generico. | Usar query con Costanera Norte y revisar manualmente. |
| La Popular | Avenida Caseros / Barracas | Nombre generico. | Usar query con corredor o barrio y revisar manualmente. |
| El Foro | Microcentro y Centro | Nombre generico. | Usar query con area central y revisar manualmente. |

## 6. Hitos colectivos

Algunos registros no son locales individuales simples:

- Mercado de San Telmo.
- Patio de los Lecheros.
- El Mercado / Faena.

Pueden geolocalizarse como puntos de referencia, pero deben distinguirse de restaurantes o bares
individuales. En fichas, conviene tratarlos como hitos gastronomicos o espacios colectivos.

## 7. Conclusion operativa

La base semilla esta lista para una fase de preparacion de queries y geolocalizacion controlada,
pero no para ejecutar Google Places de forma directa sin revision previa. La proxima fase deberia
agregar una columna de query propuesta, normalizar sucursales y separar puntos colectivos,
duplicados deliberados y casos sin locales explicitos.

