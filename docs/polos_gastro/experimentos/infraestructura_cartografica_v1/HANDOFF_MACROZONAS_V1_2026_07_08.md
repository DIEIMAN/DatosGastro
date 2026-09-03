# HANDOFF — macrozonas_v1_experimental (2026-07-08, cuarta tanda)

## Qué se pidió

Cuarta tanda del día. Con el esquema, la herramienta, el caso de prueba (Palermo Soho) y
el QA ya diseñados (Infra-1 a Infra-6), Diego pidió construir la **primera versión
operativa** de la capa: `macrozonas_v1_experimental.geojson` con las 12 macrozonas
principales (+ Soho/Hollywood como subzonas de calles reales), documentar método/fuente/
dudas sin ocultar incertidumbre, correr QA extendido, generar mapas, y probar el pipeline
en 2 casos comparando contra el prototipo anterior. Restricciones de siempre: todo en
`experimentos/`, sin Fase 25, sin commits.

## Qué se hizo (las 7 tareas, completas)

Scripts nuevos en `scripts/polos_gastro/experimentos/infraestructura_cartografica_v1/`:
`construir_macrozonas_v1.py`, `qa_macrozonas_v1.py`, `generar_mapas_macrozonas_v1.py`,
`probar_pipeline_macrozonas_v1.py`. Docs nuevos en
`docs/polos_gastro/experimentos/infraestructura_cartografica_v1/`:
`METODOLOGIA_MACROZONAS_V1.md`, `QA_MACROZONAS_V1.md`,
`COMPARACION_CONTENEDORES_ANTERIORES_VS_MACROZONAS_V1.md`, este handoff.

1. **Capa construida:** `outputs/.../macrozonas_v1_experimental.geojson`, 14 features
   (12 polos + Palermo Soho/Hollywood como subzonas). 2 alta confianza, 7 media, 5 baja.
2. **Metodología documentada** feature por feature: método, fuente, límites asumidos,
   dudas y qué revisar — sin excepciones, incluidas las macrozonas de baja confianza.
3. **QA corrido:** encontró y corrigió un gate duro real (autointersección en Caballito,
   causada por precisión numérica al reproyectar — no un error de datos) y documentó 6
   banderas, la más seria: **Avenida Corrientes y Microcentro se solapan 49,2 % (406
   entidades compartidas)** — pendiente de decisión editorial, no resuelto en esta tanda.
4. **Mapas generados:** general, con entidades, por nivel de confianza, y 14 mapas
   individuales (uno por macrozona, con callejero + entidades dentro/cerca-fuera).
5. **Pipeline probado en 2 casos:** Palermo Soho/Hollywood (reconfirma Infra-4) y Avenida
   Corrientes (nuevo). Hallazgo fuerte: el contenedor viejo de Corrientes dejaba fuera
   casi un tercio de la avenida real (territorio hacia San Nicolás); el corredor real lo
   incorpora y además **elimina el cluster sobredimensionado** que sí aparecía antes
   (0 de 10 clusters supera 35 ha, vs. 1 de 9 antes).

## Números clave para el reporte

- 14 features, 2 alta / 7 media / 5 baja confianza.
- Fuentes: callejero GCBA (2 subzonas Palermo + 2 corredores), `barrios_caba.geojson`
  (7 polos), semilla Fase 13 depurada (6 de esos 7, combinada con barrio), elipses de
  fase16 heredadas (1: Belgrano).
- Problemas encontrados: geometría inválida (corregida), 1 solapamiento operativo serio
  (Corrientes/Microcentro, 406 entidades), semillas mal geocodificadas confirmadas en 3
  polos (Chacarita, Costanera Norte, Caseros/Barracas).
- Macrozonas que más necesitan revisión humana, en orden: (1) Avenida Corrientes +
  Microcentro (resolver frontera compartida — bloqueante), (2) Costanera Norte
  (0,02 entidades/ha, la más floja de las 12), (3) Belgrano (aprobar o subdividir en
  Barrio Chino/Bajo Belgrano/Belgrano R), (4) Chacarita (revisar sedes mal geocodificadas
  en la Fase 13, no en esta capa).
- Prueba de pipeline: Avenida Corrientes pasó de 1 cluster sobredimensionado (contenedor
  viejo) a 0 (corredor real); Palermo Soho/Hollywood reconfirmó a Infra-4 (373/213
  entidades, separación limpia de identidades, pero sigue necesitando segunda pasada).

## Confirmación de restricciones

Sin commits, sin `git add`, sin push, sin tocar Fase 25 ni informes oficiales, sin
modificar datos fuente. Todo nuevo vive en `docs/`, `scripts/` y `outputs/` bajo
`polos_gastro/experimentos/infraestructura_cartografica_v1/`. Verificado con
`git status` antes de cerrar esta tanda.

## Pendiente (antes de aprobar esta capa)

1. **Resolver el solapamiento Avenida Corrientes / Microcentro y Centro** — decisión
   editorial de Diego, no resoluble por QA automático.
2. Revisar Costanera Norte, Belgrano, Chacarita (ver §"macrozonas que requieren revisión"
   arriba).
3. Aprobar (`estado_revision = aprobado_editorial`) al menos Palermo Soho/Hollywood antes
   de considerar una corrida completa del pipeline con esta capa.
4. Corregir en la cola de calidad de Fase 11/13 las sedes mal geocodificadas detectadas
   (Bar Chacabuco, Cantina Urondo, Bar Roma para Chacarita; Puerto Cristal para Costanera
   Norte).
