# Fuentes y metodo - geolocalizacion de cafeterias Cafecito

## Objetivo de la capa

Construir una base trazable de sedes publicas conocidas en CABA de marcas/cafeterias participantes o vinculadas a Cafecito, para leer la red territorial potencial de difusion fisica y digital.

El mapa muestra sedes públicas conocidas en CABA de marcas/cafeterías participantes o vinculadas al evento. No implica que todas esas sedes hayan participado físicamente en la edición relevada; se utiliza como aproximación a la red territorial potencial de difusión.

## Diferencia conceptual

- **Marca participante o vinculada:** marca/cafeteria mencionada como parte del universo Cafecito.
- **Sede conocida:** local publico de esa marca con direccion validada por fuente oficial, semioficial o directorio confiable.
- **Sede participante exacta:** local cuya participacion fisica en la edicion relevada esta confirmada. En esta capa no se afirma esa condicion salvo evidencia especifica; por defecto se marca `sucursal_participante_exacta_confirmada = no`.

## Fuentes usadas

- Directorio Rappi Mr. Green Coffee Paraguay 364: https://www.rappi.com.ar/
- Instagram Caoba Cafe BA: https://www.instagram.com/caoba.cafeba/
- Instagram Cura Te Alma: https://www.instagram.com/curatealma/
- Instagram oficial Al Diablo Coffee Roasters: https://www.instagram.com/aldiablo.coffeeroasters/
- Instagram oficial GOUT Gluten Free: https://www.instagram.com/goutglutenfree/
- Instagram oficial Juan Valdez Cafe Argentina: https://www.instagram.com/juanvaldezcafear/
- Instagram oficial Lobo Cafe: https://www.instagram.com/lobocafe.ba/
- Instagram oficial Malvon: https://www.instagram.com/malvonba/
- Instagram oficial Manteca: https://www.instagram.com/manteca_arg/
- Instagram oficial Mojo Cafeteria: https://www.instagram.com/mojocafeteria/
- Instagram oficial Mr. Green Coffee: https://www.instagram.com/mr.greencoffee/
- Instagram oficial Piccolina: https://www.instagram.com/piccolinacafe/
- Insumo preliminar Perplexity provisto por usuario
- Referencias publicas no CABA de Cura Te Alma (Rio Cuarto/Cordoba)
- Sitio oficial Cafe Registrado - nuestros locales: https://www.caferegistrado.com/nuestros-locales/
- Sitio oficial Jimena Fuster: https://jimenafuster.com.ar/
- Sitio oficial Le Ble - cafe/resto: https://www.leble.com.ar/cafe-resto.html
- Sitio oficial Malvon: https://www.malvon.ar/
- Tienda oficial Al Diablo Coffee Roasters: https://al-diablocoffeeroasters.mitiendanube.com/

## Criterios de inclusion en mapa

- Direccion publica validada o suficientemente trazable.
- Coordenadas USIG dentro de CABA.
- Barrio y comuna validados con geometria local de DataGastro.
- Nivel de confianza `alta` o `media`.
- Sin datos personales, telefonos ni identificadores de servicios externos.

## Casos excluidos o no usados en mapa

- `@lobocafe.ba` / Lobo Cafe / Puerto Madero direccion contradictoria: Direccion contradictoria o historica frente a fuente oficial actual 1330; no se usa en mapa. Geocodificacion USIG: DEALESSI, PIERINA 1130, CABA.
- `@goutglutenfree` / GOUT Gluten Free / Av. La Plata 24 dudosa: No se confirma como sede GOUT con evidencia suficiente; queda fuera del mapa. Geocodificacion USIG: LA PLATA AV. 24, CABA.
- `@caoba.cafeba` / Caoba Cafe BA / Pendiente: No se identifico direccion CABA publica confiable en esta validacion.
- `@curatealma` / Cura Te Alma / Sin sede CABA validada: Marca vinculada sin sede CABA publica validada; referencias disponibles apuntan fuera de CABA o venta/marca sin local mapeable.

## Casos pendientes

- `@lobocafe.ba` - Hay direccion dudosa o contradictoria; no se usa en mapa.
- `@goutglutenfree` - Hay direccion dudosa o contradictoria; no se usa en mapa.
- `@caoba.cafeba` - No se encontro direccion CABA publica confiable.
- `@curatealma` - No se encontro direccion CABA publica confiable.

## Limitaciones

- La base no prueba que cada sede haya participado fisicamente en la edicion relevada.
- La presencia de sedes por comuna no explica causalmente la procedencia del publico encuestado.
- Algunas marcas tienen multiples sucursales y pueden haber cambiado su red comercial.
- Las direcciones derivadas de directorios o fuentes no oficiales quedan en confianza media o pendiente.
- La geocodificacion USIG puede requerir revision manual si una direccion cambia de altura, calle o nombre comercial.

## Como leer correctamente el mapa

El mapa debe leerse como aproximacion a una red territorial potencial: lugares desde los cuales se podria reforzar difusion con QR, folleteria, historias, reposts o piezas por comuna. No debe leerse como mapa de asistencia, ventas, impacto ni participacion exacta de cada sucursal.

## Resumen operativo

- Marcas analizadas: 14.
- Sedes CABA geocodificadas con uso en mapa: 39.
- Sedes o marcas pendientes/no usadas en mapa: 4.
- Fecha de generacion: 2026-06-29.
