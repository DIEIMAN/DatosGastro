# DataGastro V2 — Fuentes internas DGDGAS y conexión con la taxonomía

> Etapa 2.5. Evaluación de las fuentes internas candidatas detectadas en la carpeta DGDGAS y su
> cruce con la taxonomía V2. **Diseño, no integración.** No se construye padrón ni se exponen
> datos personales. Complementa `14_inventario_dgdgas_drive.md`.

## 1. Fuentes internas candidatas

Catálogo en `config/v2/fuentes_internas_v2.csv` y
`outputs/v2/sanitized/fuentes_internas_dgdgas_candidatas.csv`. Códigos `I10–I13` (rango de
**datasets internos concretos**, distinto de los roles `I01` revisión / `I02` validación
territorial / `I03` relevamientos genéricos usados en Etapa 2).

| Código | Fuente | Tipo | Sensibilidad | Uso recomendado |
|---|---|---|---|---|
| I10 | Base de datos DGDGAS (directorio de locales por rubro) | planilla por rubro | **alta (PII)** | fuente para catálogo interno (agregado, sin PII) |
| I11 | Recap de eventos propios | planilla de eventos | media | ancla de eventos (enriquecer F04) |
| I12 | Seguimiento ADE / foodtrucks | planilla de gestión | media | contexto (foodtrucks/eventos) |
| I13 | Documentos e informes maestros | docs (punteros Drive) | baja | fuente documental / contexto |

## 2. La fuente más valiosa: I10 (directorio por rubro)

- Es un **relevamiento interno de establecimientos gastronómicos ya clasificados por rubro**:
  exactamente lo que V2 busca como **ancla interna**, sobre todo donde lo oficial es débil.
- Tras **minimizar PII** (quitar `CELULAR`, `MAIL`, `REFERENTE`, `INSTAGRAM`, `CARGO`), lo
  aprovechable es `LOCAL` + `BARRIO` + `DIRECCIÓN` + rubro de la hoja → candidatos por rubro.
- **No** reemplaza a F01/F02: complementa y **valida** (cruce por nombre/dirección).
- Riesgo: contacto ≠ establecimiento vigente; sin fecha de actualización; rubros mezclados en
  hojas ("Café y dulce", "Pizza, empanadas y pasta") que hay que **desagregar**.

## 3. Cruce con la taxonomía V2

Detalle en `outputs/v2/sanitized/cobertura_dgdgas_por_rubro_v2.csv`.

### 3.1 Rubros que DGDGAS (I10) podría enriquecer
- **Cobertura interna alta:** `bares`, `bodegones`, `restaurantes`, `heladerias`, `parrillas`.
- **Cobertura interna media (requiere desagregar hoja):** `cafeterias`, `pastelerias`,
  `pizzerias`, `empanadas`.
- **Cobertura interna baja:** `confiterias`, `casas_de_pastas`, `productores_proveedores`.
- **Aporte destacado:** `bodegones` y `heladerias` — rubros con ancla **oficial débil** (ver
  `13_mapa_cobertura_por_rubro_v2.md`) donde el directorio interno suma cobertura real.

### 3.2 Rubros que SIGUEN dependiendo de Google/OSM (sin cobertura interna)
`cafeterias_de_especialidad`, `cervecerias`, `panaderias` (no hay hoja dedicada),
`chocolaterias`, `vinotecas`, `queserias`, `charcuterias`, `dieteticas_gourmet`,
`almacenes_gastronomicos`, `obradores`, `fabricas_de_pastas`, `tostadores_de_cafe`,
`mercados_gastronomicos`, `ferias_gastronomicas`. DGDGAS **no** mueve la aguja en estos.

### 3.3 Archivos para casos históricos / emblemáticos
- I13 (`Documento_Maestro_Ecosistema`, informes) → contexto y posibles casos emblemáticos,
  **una vez exportados sin datos privados**.

### 3.4 Archivos para eventos
- I11 (Recap eventos) y, como contexto, I12 (ADE/foodtrucks) → enriquecen F04.

### 3.5 Archivos para programas / políticas
- I13 (informes/documento maestro) → contexto institucional que se cruza con F05.

### 3.6 Archivos demasiado sensibles para uso directo
- I10 en su forma cruda (PII de contacto). Solo uso **agregado y minimizado**, con permiso.
- Punteros de Drive: no auditables localmente; requieren export oficial sin datos privados.

## 4. Hamburguesería y Foodtrucks → `pendiente_revision_taxonomica`

Las hojas `Hamburguesería` (131) y `Foodtrucks` (82) no tienen subcategoría estable en la
taxonomía V2. Se marcan `pendiente_revision_taxonomica` (no se excluyen): podrían integrarse
como subcategorías nuevas o mapearse (hamburguesería → restaurantes/takeaway; foodtrucks →
formato itinerante transversal) en una revisión taxonómica futura.

## 5. Recomendaciones (gates antes de integrar)

1. **Confirmar con DGDGAS** propietario, fecha de corte, grano de fila y reglas de actualización
   de I10/I11/I12.
2. **Pedir export sin PII** del directorio (I10) para análisis agregado.
3. **Desagregar hojas mixtas** ("Café y dulce", "Pizza, empanadas y pasta") a subcategorías V2.
4. **No integrar** hasta aprobar contrato interno y minimización de PII.
5. Mantener I10–I13 como **universo interno separado** (no mezclar con F0x ni E0x).

## 6. Estado

- Fuentes **inventariadas y evaluadas**, **no integradas**. `estado_revision =
  inventariado_no_integrado` (I13: `pendiente_revision`).
- Sin padrón, sin datos personales en entregables, sin tocar originales.
