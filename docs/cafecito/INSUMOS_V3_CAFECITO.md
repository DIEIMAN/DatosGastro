# Insumos preflight V3 - Cafecito

Documento breve de apoyo para preparar la V3 del informe Cafecito. No genera el PDF final ni modifica datos fuente.

## 1. Base de cafeterías

Datos tomados de la base consolidada de sedes geocodificadas de Cafecito.

- Cantidad total de filas: 43
- Cantidad con usar_en_mapa = si: 39
- Cantidad con usar_en_mapa = no: 2
- Cantidad con usar_en_mapa = pendiente: 2
- Marcas pendientes o no usadas en mapa: 4
  - Lobo Cafe
  - GOUT Gluten Free
  - Caoba Cafe BA
  - Cura Te Alma
- Sedes no usadas: 2
  - Lobo Cafe / Pierina Dealessi 1130
  - GOUT Gluten Free / Av. La Plata 24
- Comunas con más sedes mapeables:
  - Comuna 14: 9
  - Comuna 13: 7
  - Comuna 1: 7
  - Comuna 15: 4
  - Comuna 6: 3
  - Comuna 2: 3
- Barrios con más sedes mapeables:
  - Palermo: 9
  - Belgrano: 5
  - Caballito: 3
  - Recoleta: 3
  - San Nicolas: 3

Validación breve:
- Coinciden los valores esperados para total de filas, usar_en_mapa = si, usar_en_mapa = no y usar_en_mapa = pendiente.
- Coincide el conjunto de comunas principales esperadas.
- Diferencia: la base consolidada registra 4 marcas pendientes o no usadas en mapa, no 2; los casos de mayor incertidumbre para la V3 son Caoba Cafe BA y Cura Te Alma, mientras que Lobo Cafe y GOUT Gluten Free quedan fuera del mapa por contradicción o falta de validación suficiente.

## 2. Lectura territorial sugerida

Las sedes mapeables muestran una red territorial potencial de difusión; no implican que todas esas sedes hayan participado físicamente. Comuna 14, Comuna 1 y Comuna 13 aparecen como nodos fuertes. La comparación con el público encuestado debe hacerse solo a nivel agregado y sin afirmar causalidad. La red puede servir para QR, cartelería, reposts e historias.

Frase textual a conservar:

“El mapa muestra sedes públicas conocidas en CABA de marcas/cafeterías participantes o vinculadas al evento. No implica que todas esas sedes hayan participado físicamente en la edición relevada; se utiliza como aproximación a la red territorial potencial de difusión.”

## 3. Problemas detectados en V2

Tomando como referencia el paquete V2 y la revisión de preflight, los puntos que conviene corregir para la V3 son:

- Portada demasiado cargada.
- Repetición entre portada y resumen ejecutivo.
- Contenido técnico interno en anexo o cierre que no debe aparecer en PDF público.
- Superposición visual en la página de perfil/procedencia.
- Mapa y ranking comunal duplican información.
- Tipo de plan repite dona y barras.
- Intereses futuros debe aclarar que son menciones multi-respuesta.
- Cruces interpretativos débiles o con formato poco claro.
- Demasiadas cajas en conclusiones y recomendaciones.
- Necesidad de condensar páginas con aire.

## 4. Cosas prohibidas en el PDF público

El PDF final no debe contener:

- Rutas de archivos.
- Nombres de scripts.
- Extensiones .py, .csv, .md, .pdf.
- Carpetas outputs/, scripts/, docs/, Cafesito/final/.
- Hashes.
- Git.
- Commit.
- Push.
- QA técnico.
- Pdfinfo.
- Place_id.
- API key.
- Referencias a V1, V2 o V3.

## 5. Recomendación de estructura V3

Propuesta compacta de 12 a 14 páginas:

1. Portada institucional.
2. Resumen ejecutivo.
3. Qué permite decidir el relevamiento.
4. Perfil de la muestra.
5. Lectura territorial del público.
6. Red territorial de cafeterías.
7. Público vs red de sedes.
8. Canales de llegada y oportunidad de locales adheridos.
9. Vínculo con eventos y fidelización.
10. Motivaciones e intereses futuros.
11. Conclusiones y recomendaciones.
12. Anexo metodológico y privacidad.

## 6. Checks rápidos

Verificación rápida sobre los insumos públicos revisados:

- No hay place_id en los outputs públicos revisados.
- No hay API keys en los outputs públicos revisados.
- No se detectan teléfonos personales en los outputs públicos revisados.
- No se detectan correos personales en los outputs públicos revisados.
- El público aparece agregado y no expuesto a nivel individual.
- Las cafeterías usadas en mapa corresponden a filas con usar_en_mapa = si.

## 7. Recomendación operativa para Claude

Antes de pedir la V3, conviene dejar claros estos puntos de corte:

- Mantener el tono institucional y público.
- Eliminar referencias técnicas y rutas internas.
- Compactar la narrativa para 12 a 14 páginas.
- Separar claramente red territorial potencial de participación física real.
- No incluir nombres de archivos ni extensiones en el PDF final.
