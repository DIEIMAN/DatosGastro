# DataGastro V2 — Plan de implementación por etapas

> Hoja de ruta. Cada etapa termina con una **revisión y aprobación de Diego** antes de pasar a
> la siguiente. Las etapas con requests/API key/presupuesto están **bloqueadas** hasta
> autorización explícita. F01–F05 permanece intacto.

## Etapa 0 — Diseño y aprobación (esta etapa)

- **Hace:** documentación V2 (`docs/datagastro_v2/`), taxonomía, modelo de datos, planes.
- **No hace:** ningún request, ninguna API key, ningún dato nuevo, ningún cambio al pipeline.
- **Entregable:** estos 11 documentos.
- **Salida:** aprobación de Diego del enfoque, la taxonomía y el modelo.

## Etapa 1 — Esqueleto técnico (sin datos externos)

- **Hace:**
  - crear estructura de carpetas V2 **nueva** (no toca `src/`, `data/processed`, dashboard V1):
    ```text
    src/v2/                 (módulos nuevos)
    data/v2/raw/            (gitignored)
    data/v2/processed/      (gitignored si tiene filas sensibles)
    data/v2/analytics/      (agregados versionables)
    outputs/v2_*/           (gitignored los brutos)
    config/v2/              (mapeos rubro↔término, tags OSM, marcas conocidas — no sensibles)
    ```
  - definir esquemas de tablas (doc 08) como contratos/CSV vacíos;
  - cargar la **taxonomía** (doc 01) como `dim_rubro_gastronomico`;
  - construir `dim_fuente`, `dim_territorio` (desde geometrías GCBA ya existentes);
  - actualizar `.gitignore` para las rutas sensibles V2.
- **No hace:** requests externos.
- **Salida:** modelo vacío validable + taxonomía cargada.

## Etapa 2 — Anclas oficiales (públicas, sin costo)

- **Hace:** poblar candidatos desde fuentes oficiales **ya disponibles** en V1 (AGC/F02,
  BA Data, F03/F04), **leyendo** las salidas públicas sin regenerarlas.
- **Construye:** primeras `fact_deteccion_fuente` de universo oficial → resolución a
  `dim_establecimiento_candidato` con niveles C4 `oficial_estricto`.
- **No hace:** Google/OSM todavía.
- **Salida:** padrón candidato base, sólo oficial, con conteos por comuna/rubro.

## Etapa 3 — OSM (auxiliar abierto, sin costo monetario)

- **Hace:** integrar OSM (doc 05) por Overpass/extracto; mapear tags → taxonomía; deduplicar
  contra el padrón oficial.
- **Requiere:** aprobación para ejecutar consultas Overpass (sin costo, pero es acceso externo).
- **Salida:** cobertura ampliada; primeras entidades multifuente (oficial + OSM → C5).

## Etapa 4 — Google Places (PILOTO topeado, con costo) — BLOQUEADA

- **Requiere (todo previo a ejecutar):**
  - aprobación explícita de Diego;
  - presupuesto confirmado contra pricing vigente de Google + crédito gratuito;
  - topes acordados (`--max-queries`, `--max-results`), modo dry-run por defecto;
  - API key sólo en variable de entorno de la sesión (nunca commiteada).
- **Hace:** piloto por subcategoría/zona (doc 04), reutilizando el clasificador del piloto V1;
  brutos a carpeta gitignored; deduplicación inter-fuente; detección de cadenas.
- **Salida:** cobertura operativa, casos B a revisión, conteos por nivel de confianza.

## Etapa 5 — Capa documental y emblemáticos (sin costo)

- **Hace:** usar Perplexity/web como **localizador** (doc 07) para casos históricos y rubros
  emblemáticos; registrar `fact_trayectoria_documental` con URLs verificables; cruzar con
  Bares Notables.
- **Salida:** capa `historico_emblematico` con respaldo documental.

## Etapa 6 — Revisión manual e integración (interna)

- **Hace:** resolver casos B/C1 (`fact_validacion_manual`); consolidar niveles de confianza;
  marcar cadenas vs independientes.
- **Salida:** padrón candidato integrado con confianza por entidad.

## Etapa 7 — Salidas ejecutivas y dashboard V2

- **Hace:** generar **agregados sanitizados** (doc 09): mapas por rubro, rankings, densidad,
  fichas por rubro, informe ejecutivo. Dashboard V2 en carpeta nueva.
- **Salida:** entregables sin filas individuales sensibles.

## Etapa 8 — Validación territorial posterior (futuro)

- **Hace:** trabajo de campo (I02) sobre la lista priorizada; marca `confirmado_territorial`.
- **Salida:** subconjunto verificado en terreno. Sólo aquí se acerca la noción de "actividad".

## Dependencias y gates

```text
E0 ─► E1 ─► E2 ─► E3 ─► E4(💰 bloqueada) ─► E5 ─► E6 ─► E7 ─► E8
                          ▲
            gate: aprobación + presupuesto + topes
```

- Cada flecha es un **gate de aprobación**.
- Las etapas sin costo (E2/E3/E5) pueden avanzar antes que la de Google (E4).
- Nada se commitea ni pushea sin autorización explícita.

## Checklist de guardrails por etapa

```text
[ ] No se tocó F01–F05 ni el dashboard V1 sin permiso.
[ ] Brutos sensibles en carpetas gitignored.
[ ] Sin API key en repo/logs/archivos.
[ ] Sin scraping de plataformas privadas.
[ ] Sin datos personales en entregables.
[ ] Universos separados (F/I/E) y declarados por fila.
[ ] Vocabulario institucional ("padrón candidato", no "censo").
[ ] Aprobación de Diego antes del siguiente gate.
```
