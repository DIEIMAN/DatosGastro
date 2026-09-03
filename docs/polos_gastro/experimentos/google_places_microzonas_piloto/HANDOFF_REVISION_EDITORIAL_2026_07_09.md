# HANDOFF — revisión editorial del piloto de microzonas (2026-07-09, tanda 2)

Continúa a `HANDOFF_GOOGLE_PLACES_MICROZONAS_PILOTO.md` (ejecución del piloto). Esta
tanda consolidó la revisión metodológica/editorial **sin llamadas nuevas a la API, sin
tocar outputs base ni Fase 25, sin commits**.

## Qué se produjo en esta tanda (derivados nuevos)

- `scripts/.../revision_editorial_microzonas.py` — genera la tabla de revisión.
- `outputs/.../revision/tabla_revision_editorial_microzonas.csv` — 78 filas: entidades,
  % por fuente, superficie, densidad, KDE, confianza algorítmica, referencia urbana
  orientativa (aproximada, verificar en mapa), clasificación, problema y acción.
- `docs/.../RESUMEN_EJECUTIVO_REVISION_PILOTO.md` — 10 hallazgos (robustos vs. pendientes).

## Qué está validado

- **Método y contenedores:** polígonos chicos (0,9–12,1 ha), contención estricta,
  dedup entre fuentes, 92 % de microzonas mixtas F01+F02/Places.
- **Zonas aprobables casi en bloque:** San Telmo (8/8) y Palermo Soho/Hollywood (18/19
  entre APROBAR y APROBAR CON OBS; corredores Plaza Serrano, Honduras/Armenia, Fitz Roy).
- **Aporte de Places:** +76 % de puntos, menos ruido en 3 macrozonas, estructura nueva
  real en Belgrano (núcleo tipo Barrio Chino con 74 % Places).

## Qué NO está validado

- **Los cortes internos de los corredores densos:** 43 piezas "REVISAR CORTE"
  (Corrientes 23, Belgrano 14, Microcentro 6). La subdivisión KMeans acota tamaño pero
  produce límites geométricos; ninguna de esas piezas debe tratarse como subzona con
  identidad propia todavía.
- **3 microzonas "REVISAR UNIVERSO"** (≥70 % Places): posible oferta nueva no
  registrada o sesgo de prominencia; verificar antes de aprobar.
- **Las referencias urbanas de la tabla son aproximadas** (hitos con coordenadas de
  conocimiento general): orientan la lectura, no reemplazan verificación en mapa.

## Ajustes recomendados ANTES de escalar

1. Reemplazar la subdivisión KMeans por cortes editoriales manuales en Corrientes/
   Microcentro y Belgrano (por cruces/hitos), usando las piezas actuales como insumo.
2. Decidir las 3 microzonas Places-dependientes (aprobar/observar/descartar).
3. Fijar el bug de sklearn 1.9 (`cluster_selection_epsilon`): anclar versión o merge
   post-hoc a 50 m, para que Soho corra igual que el resto.
4. Definir cómo se versiona la revisión (la tabla CSV admite una columna de decisión
   DGDGAS análoga al checklist ✓/△/✗ de macrozonas).

## Si se autoriza ampliar a las macrozonas restantes

- **Alcance:** 7 macrozonas contenedoras sin piloto (Chacarita, Villa Crespo, Puerto
  Madero, Recoleta, Caballito, Costanera Norte, Caseros/Barracas). Palermo contextual
  no es contenedor y no se consulta.
- **Cómo estimar:** agregar esas macrozonas a `ZONAS_PILOTO` en
  `preparar_consultas_places_piloto.py` y correr el **dry-run** (sin key, sin costo):
  imprime celdas exactas y costo máximo. Orden de magnitud esperado: ~550–650 consultas
  (≈ USD 19–23 al mismo SKU), dominado por Puerto Madero (503 ha) y Caballito (347 ha).
- **Requiere:** autorización explícita de presupuesto de Diego ANTES de `--execute
  --confirm-real-api` (mismo protocolo de doble confirmación), y revisar si conviene
  excluir Costanera Norte/Caseros hasta resolver su estado en la revisión de macrozonas
  (hoy son "no aprobar todavía").
- Después: correr etapas 2–5 tal cual (universo → clusters → mapas → revisión).

## Restricciones confirmadas en esta tanda

Sin llamadas a la API. Sin commits/add/push. Outputs base intactos (solo se agregó
`revision/` y docs). Fase 25, informes oficiales y datos fuente intactos. Marca
EXPERIMENTAL en todos los derivados.
