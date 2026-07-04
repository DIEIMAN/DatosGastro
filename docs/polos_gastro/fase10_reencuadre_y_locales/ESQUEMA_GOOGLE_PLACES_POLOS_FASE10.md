# Esquema Google Places para PolosGastro - Fase 10

Fecha de trabajo: 2026-07-02. Documento de diseno metodologico. En esta fase no se llamo a Google
Places, no se uso API key y no se genero raw.

## 1. Criterio general

Google Places puede usarse en una fase posterior como capa complementaria de puntos gastronomicos.
No es fuente oficial, no es padron, no reemplaza revision humana y no decide si un polo existe.

El uso permitido debe limitarse a geolocalizacion, contraste de nombres y enriquecimiento interno
de puntos, con revision manual antes de cualquier salida publica.

## 2. Orden recomendado

1. Geolocalizar primero los locales del documento semilla.
2. Revisar manualmente coincidencias, sucursales, duplicados y ambiguedades.
3. Sumar locales complementarios relevantes por polo solo con criterio documentado.
4. Separar campos internos de campos publicables.
5. Revisar manualmente antes de publicar fichas o mapas.

## 3. Lo que Google Places no debe hacer

- No debe decidir si un polo del universo semilla existe.
- No debe reemplazar fuentes publicas u oficiales.
- No debe usarse como padron oficial de locales.
- No debe publicarse como ranking.
- No debe publicar raw, `place_id`, ratings ni cantidades de resenas en informes publicos.
- No debe usarse para afirmar actividad actual sin advertencias y revision.

## 4. Esquema de tabla interna

La estructura propuesta queda documentada en:

- `outputs/polos_gastro/fase10_reencuadre_y_locales/tablas/schema_locales_google_places_fase10.csv`

Campos propuestos:

| Campo | Uso | Publicable por defecto |
| --- | --- | --- |
| polo | Polo semilla asociado. | Si |
| subzona | Subzona o recorte textual cuando corresponda. | Si |
| nombre_lugar | Nombre usado en la capa de trabajo. | Si, con revision |
| query_google_places | Query usada para buscar coincidencia. | No |
| google_place_id_interno | Identificador tecnico de Google Places. | No |
| lat | Latitud del punto. | Si, solo si fue revisada |
| lon | Longitud del punto. | Si, solo si fue revisada |
| direccion | Direccion devuelta o normalizada. | Revisar antes de publicar |
| categoria_google | Categoria de Google. | No por defecto |
| rating_interno | Rating de Google Places. | No |
| user_ratings_total_interno | Cantidad de resenas. | No |
| fuente_geolocalizacion | Fuente de coordenadas o match. | Si, en anexo metodologico |
| origen | documento_semilla o complementario. | Si |
| prioridad | obligatorio o complementario. | Si |
| confidence_match | Nivel de confianza interno. | No |
| requiere_revision_manual | Flag de control. | No |
| mostrar_en_mapa | Flag editorial. | Si, como resultado, no como campo tecnico |
| mostrar_en_ficha | Flag editorial. | Si, como resultado, no como campo tecnico |
| nota_publica | Nota autorizada para ficha o mapa. | Si |
| nota_interna | Observacion operativa. | No |

## 5. Campos internos

Los campos `google_place_id_interno`, `rating_interno`, `user_ratings_total_interno`,
`confidence_match`, `query_google_places` y `nota_interna` son internos. No deben aparecer en PDF,
DOCX, mapas publicos ni fichas publicas salvo decision institucional explicita.

El raw de Google Places debe quedar fuera de entregables publicos y con controles de privacidad,
credenciales y trazabilidad.

## 6. Criterio visual futuro

En mapas publicos, si se autorizan, usar puntos pequenos y nombres solo cuando corresponda. La capa
de puntos debe leerse como referencias gastronomicas del relevamiento, no como padron oficial ni
ranking de locales.

En fichas por polo, los locales destacados deben presentarse como referencias preliminares o
ejemplos documentados, no como seleccion oficial ni recomendacion comercial.

