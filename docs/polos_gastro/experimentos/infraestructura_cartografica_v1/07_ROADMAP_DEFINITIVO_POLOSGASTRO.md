# Roadmap definitivo de PolosGastro (Etapa Infra-7)

**Fecha:** 2026-07-08 · **Carácter:** propuesta de arquitectura, con todo lo aprendido en
las tres tandas de trabajo de este día (diseño → prototipo V1 → validación → esta
infraestructura). Nada de lo aquí descripto está implementado como flujo oficial; es la
síntesis para decidir hacia dónde construir a partir de ahora.

## 0. De dónde viene esto (una línea por hito)

1. **Tandas 1-2 (clustering exploratorio, cerradas):** DBSCAN sobre 106 puntos semilla.
   Conclusión: el algoritmo sirve como prueba de concepto; el cuello de botella es el
   dato, no el método.
2. **Diseño del pipeline definitivo** (`experimentos/diseno_pipeline_definitivo/`):
   HDBSCAN intra-macrozona + KDE de control, universo F01+F02, sin implementar.
3. **Prototipo V1** (`experimentos/pipeline_microzonas_v1/`, s01-s08): implementado y
   corrido. Universo real de 9.739 entidades, 83 clusters HDBSCAN en 11 macrozonas.
4. **Validación con 8 casos reales** (`.../validacion/`): confirma que el enfoque
   funciona, salvo casos puntuales — y la causa raíz de esos casos es **el contenedor de
   macrozona** (hull de semilla), no el detector.
5. **Esta etapa — infraestructura cartográfica v1** (`experimentos/
   infraestructura_cartografica_v1/`): inventario de referencias existentes, diseño de
   esquema, herramienta de edición, prueba real sobre Palermo Soho, versionado y QA.

La conclusión que atraviesa las cuatro últimas tandas es siempre la misma, confirmada con
evidencia distinta cada vez: **el algoritmo de clustering ya no es el problema; el
contorno editorial de entrada sí lo es.** Este roadmap organiza el trabajo alrededor de
esa conclusión.

## 1. Infraestructura permanente (los cimientos — cambian poco, se versionan)

### 1.1 Universo gastronómico
- **Qué es:** tabla de entidades resueltas desde F01+F02, deduplicación espacial+textual
  documentada (`REGLAS_UNIVERSO_V1.md`).
- **Versionado:** `universo_vYYYYMM`, snapshots inmutables, tabla de correspondencia
  hacia filas fuente.
- **Pendiente conocido:** revisar el mapeo del recurso F02-2025 (25.289 filas → 877
  direcciones, sin fecha); calibrar umbrales de deduplicación (40 m / 15 m / 30 m) contra
  un conjunto etiquetado a mano.

### 1.2 Capa editorial de macrozonas (lo nuevo de hoy)
- **Qué es:** `macrozonas_editorial_vN.geojson`, jerarquía polo→subzona, 16 atributos
  (`02_DISENO_CAPA_EDITORIAL.md`), construida sobre calles reales del callejero GCBA en
  vez de elipses o hulls de puntos.
- **Estado real:** 2 de 12 polos con contorno real construido (Palermo Soho y Hollywood,
  en `borrador`, pendiente de aprobación editorial). Los otros 10 no tienen todavía
  ninguna geometría propia — heredan como mucho una elipse aproximada (5 casos) o nada
  (5 casos), según el inventario (Infra-1).
- **Versionado:** snapshots `vN_YYYYMMDD` + `CHANGELOG.md` + diff automático
  (`comparar_versiones_editorial.py`).
- **QA:** gates duros + banderas (`qa_capa_editorial.py`), ya validado contra datos
  reales — encontró un problema genuino (jerarquía incompleta) en el primer intento.

### 1.3 Pipeline de clustering (HDBSCAN intra-macrozona)
- **No cambia el detector.** Cambia lo que recibe como contorno de entrada (capa
  editorial real en vez de hull de semilla) y necesita, además, una segunda pasada
  **condicionada a la forma del cluster** (compacto → leaf/epsilon chico; alargado → otro
  tratamiento) — la Etapa Infra-4 confirmó que el contorno real resuelve la mezcla de
  identidades pero NO el problema de núcleos sobredimensionados, que sigue necesitando
  esta mejora ya identificada en la validación (Etapa V2-7).

### 1.4 QA (tres capas independientes, no una sola)
1. QA del universo (perfil de fuentes, % duplicados, cobertura geográfica).
2. QA de la capa editorial (Infra-6, geometría y atributos).
3. QA de microzonas (gates del prototipo V1: superficie máx. 35 ha, densidad mínima,
   diámetro, contención, sensibilidad a parámetros).

### 1.5 Versionado (tres ejes citados juntos, nunca mezclados)
Cada corrida de microzonas debe registrar `universo_vX + editorial_vY + parametros_id`
en su propio log (ya es el hábito con `parametros_pipeline_v1.json`; se agrega
`version_capa_editorial`). Un informe que cite una fecha de corrida debe poder
reconstruirse exactamente con esos tres identificadores.

## 2. Proceso operativo (el ciclo de vida — se repite)

```
Actualización del universo          Recalcular microzonas         Revisión humana
(BA Data publica F01/F02 nuevo,  →  (correr pipeline con      →   (checklist ya          →  Publicación
 o se corrige mapeo F02-2025)        universo + editorial          diseñado: doc 01 §7,       (solo si
                                     vigentes)                     caso canónico Fitz          aprobado_editorial)
                                                                    Roy-Honduras)
```

- **Quién aprueba contornos y microzonas: Diego, siempre.** Ningún polígono con
  `estado_revision != aprobado_editorial` alimenta un informe institucional (gate B4 del
  QA lo recuerda automáticamente).
- **Quién construye:** el asistente (Claude/Codex) propone contornos asistidos por
  callejero + fichas, corre el pipeline, corre el QA — nunca aprueba nada por sí mismo.
- **Cadencia sugerida:** no continua. Se re-versiona el universo cuando BA Data publique
  (verificar, no asumir periodicidad) y la capa editorial cuando se digitalice o corrija
  un contorno — lo que ocurra primero, pero no más de una vez por trimestre para no
  generar fatiga de changelog sin cambios sustantivos que justifiquen revisión.

## 3. Desarrollo futuro (después de que 1 y 2 estén asentados)

- **Polos emergentes:** las 22 fichas PG014 en adelante (Devoto, Villa Urquiza, Flores,
  Retiro, Boedo, corredor DOHO, …) documentadas pero nunca incorporadas a ningún
  contenedor de clustering — coincide con el 53 % de entidades que el prototipo V1 dejó
  "fuera de macrozona". Mismo proceso: contorno editorial real antes de clusterizar,
  nunca clustering global sin contorno.
- **Google Places:** rol ya definido y no revisado por esta etapa — evidencia
  complementaria por muestreo dirigido (validación de vigencia, desempate de duplicados),
  nunca fuente principal ni censo. Presupuesto explícito por corrida.
- **Indicadores:** ponderar entidades por recencia de evidencia y por presencia en ambas
  fuentes (F01+F02) — únicos pesos disponibles hoy sin datos externos.
- **Dashboards:** `@usig-gcba/mapa-interactivo` + Leaflet (ya instalados) son candidatos
  para un visor institucional interactivo; **no** para generación batch de PDFs (necesita
  browser/DOM, ver Infra-3).
- **Análisis temporal:** clustering espacio-temporal (ST-DBSCAN) para detectar núcleos en
  crecimiento/decadencia — requiere historia de altas/bajas por entidad que hoy no existe
  de forma limpia; roadmap explícito, no v1 ni v2.

## 4. Qué NO es infraestructura permanente (para no confundir capas)

- El código del prototipo V1 (`s01`…`s08` de `pipeline_microzonas_v1/`) demostró el
  método; sus **aprendizajes y parámetros documentados** son permanentes, pero el código
  en sí es un prototipo — cuando la capa editorial esté completa, conviene reescribirlo
  como pipeline definitivo en vez de seguir parchándolo indefinidamente.
- Los kits de edición (Infra-3) y los scripts de esta carpeta
  (`infraestructura_cartografica_v1/`) son herramientas de trabajo puntuales, no parte de
  la arquitectura final — la arquitectura final es el **esquema** (Infra-2) y el
  **proceso** (§2 de este documento), no estos scripts específicos.
- `subzonas_editoriales_geometrias.geojson` (fase16, elipses) sigue siendo válido para los
  mapas oficiales existentes (Fase 25) hasta que se decida migrarlos; no se toca ni se
  reemplaza automáticamente.

## 5. Próximos 3 pasos concretos (orden, no todo a la vez)

1. **Diego revisa el polígono de Palermo Soho/Hollywood** (único caso construido esta
   sesión) — primer `aprobado_editorial` real, o correcciones concretas sobre un caso
   acotado antes de escalar.
2. **Definir el método para los 10 polos restantes**, sabiendo que solo 2 fichas tienen
   calles límite completas: probablemente el barrio administrativo (`barrios_caba.geojson`,
   ya real y preciso) como punto de partida para los casos "solo nombre de barrio", con
   ajuste editorial asistido en QGIS (kit de edición, Infra-3) para acotarlo a la zona
   gastronómica real dentro del barrio.
3. **Publicar `macrozonas_editorial_v1` completo y re-correr el pipeline**, decidiendo
   antes la estrategia de segunda pasada condicionada a forma (Etapa V2-7) — el contorno
   real por sí solo no alcanza para declarar el pipeline "definitivo" (Etapa Infra-4).

Estos tres pasos son trabajo de días, no de meses; el bloqueo real, como en la validación
anterior, es la decisión editorial humana, no la construcción técnica.
