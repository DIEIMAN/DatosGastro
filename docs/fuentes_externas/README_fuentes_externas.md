# DataGastro – Fuentes externas y privadas para ampliar el modelo

Fecha: 2026-06-19

## Lectura ejecutiva

La idea de sumar Google, Rappi, PedidosYa y Mercado Pago es buena, pero no conviene mezclar todo como si fueran “bases de datos públicas”. Hay tres tipos de fuente:

1. **APIs oficiales utilizables rápido**: Google Places/Places Aggregate, OpenStreetMap, Foursquare/Yelp/Tripadvisor según cobertura.
2. **Datos privados de altísimo valor, pero sólo por convenio**: Rappi, PedidosYa, Mercado Pago, adquirentes, bancos, POS y reservas.
3. **Fuentes no recomendadas para pipeline institucional**: scraping de Google Maps, Popular Times, Rappi o PedidosYa sin permiso.

La estrategia correcta es:  
**primero fortalecer el padrón oficial vivo + permisos de área gastronómica; después agregar Google/OSM como validación externa; y en paralelo abrir convenios de delivery/pagos para demanda real.**

## Prioridad recomendada

### 1. Antes de fuentes privadas: cerrar lo público/interno crítico
- **Padrón vivo AGC**: estado vigente/baja/cese de habilitaciones.
- **Permisos de área gastronómica**: mesas, sillas, superficie, permisos activos.
- **Eventos oficiales operativos**: calendario, ubicación, asistentes, expositores.

Esto evita decir erróneamente “44 mil locales activos”.

### 2. Primer piloto externo rápido
- **OpenStreetMap / Overpass** como fuente abierta.
- **Google Places o Places Aggregate** como fuente externa paga/controlada.
- Validación por 2 comunas: San Nicolás y Palermo.

### 3. Convenios de alto impacto
- **Rappi + PedidosYa**: comercios activos, pedidos, ticket, GMV, categorías, horarios, performance por zona.
- **Mercado Pago/adquirentes/bancos**: transacciones, monto agregado, ticket promedio, rubro/comuna/mes.
- **POS/reservas**: ocupación, ventas, horarios pico, no-shows, mesas.

## Campos mínimos a pedir a privados

No pedir datos personales. No pedir usuarios. No pedir tarjetas. No pedir CUIT nominal salvo que haya base legal clara.

Pedir una tabla mensual agregada con:

- mes
- comuna o barrio
- rubro/categoría gastronómica
- cantidad de comercios activos
- cantidad de pedidos/transacciones
- monto agregado o índice base 100
- ticket promedio agregado
- horarios/franjas de mayor actividad
- plataforma/fuente
- aclaración metodológica

Regla de privacidad: cada celda debería tener un umbral mínimo de comercios para evitar reidentificación.

## Archivos incluidos

- `matriz_fuentes_externas.xlsx`: matriz priorizada y accionable.
- `matriz_fuentes_externas.csv`: misma matriz en CSV.
- `acciones_diego.csv`: acciones concretas para destrabar datos.
- `campos_objetivo_integraciones.csv`: esquema de campos ideal para nuevas fuentes.
- `prompt_codex_fuentes_externas.md`: prompt para pedirle a Codex que cree los módulos F07/F08/F09.
- `plantilla_pedido_convenio_datos.md`: texto base para pedir datos a plataformas.
- `checklist_legal_y_metodologico.md`: lista de control antes de usar fuentes privadas.
