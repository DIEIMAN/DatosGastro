# Herramientas reutilizables DataGastro — propuesta

Fecha: 2026-06-29.

**Propuesta documental.** No implementa nada todavía. No crea carpetas `shared/` ni toca otros
subproyectos (Cafecito, MercadosGastro, CasasDePastas, V2). Solo recoge aprendizajes de
PolosGastro y de los informes ya hechos para proponer estándares y módulos comunes a futuro.

> Cualquier implementación posterior fuera de PolosGastro requiere autorización de Diego.

---

## 1. Plantilla común de informes DataGastro

Un esqueleto único reutilizable (como `ESQUELETO_INFORME_POLOS_GASTRO.md`, pero genérico):
portada, resumen ejecutivo, definición operativa, hallazgos, visuales, limitaciones, próximos
pasos, anexos, trazabilidad de fuentes. Cada subproyecto lo instancia.

## 2. Estándar de portada, footer, numeración y marca DataGastro

- **Portada**: título, subtítulo, fecha de corte, área responsable, advertencia de alcance.
- **Footer**: fuente, fecha de corte y nº de página consistentes.
- **Numeración**: secciones numeradas estables.
- **Marca**: logo/identidad DataGastro, paleta común.

## 3. Estándar de QA público

Checklist antes de publicar cualquier entregable:
- sin rutas locales (`C:\…`, `G:\…`);
- sin nombres de scripts ni detalles de implementación;
- sin datos personales (CUIT, DNI, emails, teléfonos, transacciones);
- sin versiones/borradores internos;
- sin hashes ni metadatos internos en el PDF público;
- separar documento público de documento técnico interno.

## 4. Estándar de cartografía

- **Fuente cartográfica** citada (Buenos Aires Data, USIG…).
- **Atribución** obligatoria (p. ej. GOED/GCBA © OpenStreetMap ODbL).
- **Notas metodológicas** visibles.
- **Niveles de precisión** explícitos (alta/media/baja/sin delimitación).
- **Distinción** mapa conceptual vs. mapa final/cartográfico.
- Regla: nunca convertir delimitaciones textuales en polígonos oficiales, ni habilitaciones/
  oferta en "locales activos".

## 5. Estándar de fuentes

Tipología común (ya usada en PolosGastro):
- **semilla** (insumo inicial no validado);
- **oficial** (GCBA, organismos);
- **periodística**;
- **turística**;
- **comercial** (con cautela: sesgo);
- **datos abiertos** (Buenos Aires Data).

Cada fuente con: id, url, fecha de consulta, confiabilidad, evidencia que aporta, limitaciones,
uso recomendado.

## 6. Estándar de visuales

- **Paleta** DataGastro (núcleo `#275DAD`, relevante `#2A9D8F`, emergente `#E9B44C`,
  anexo `#7D8597`, fuera `#C44536`).
- **Legibilidad**: etiquetas no superpuestas, contraste suficiente.
- **Tamaño de etiquetas** mínimo legible.
- **Evitar saturación** (preferir barras agrupadas/heatmaps a apilados densos).
- **Versión interna vs. pública**: la de trabajo puede ser densa; la pública debe ser limpia.

## 7. Potenciales módulos futuros (solo propuesta)

| Módulo propuesto | Propósito |
| --- | --- |
| `scripts/shared/reporting/` | Plantillas y ensamblado de informes (portada, footer, numeración). |
| `scripts/shared/cartografia/` | Carga de barrios/comunas GeoJSON, base GCBA, simbología por precisión. |
| `scripts/shared/qa_publico/` | Checklist automatizable de QA público (rutas, datos personales, hashes). |
| `scripts/shared/fuentes_externas/` | Normalización de fuentes (id, tipo, confiabilidad, fecha de consulta), dedupe por URL, append a matriz. |
| `scripts/shared/qa_urls/` | Verificación de URLs (estado, accesibilidad, marca `requiere_revision_url`); manejo de dominios bloqueados (p. ej. paywalls). |
| `scripts/shared/mapas_estaticos/` | Mapas estáticos GeoPandas + matplotlib con paleta DataGastro y barrios/comunas oficiales. |
| `scripts/shared/google_places_exp/` | Cliente experimental de Places: dry_run, hard cap, FieldMask mínimo, secrets por entorno, sin responses crudas ni coordenadas. |
| `docs/datagastro_estandares/` | Documentación de los estándares 1–8 de este documento. |

> **Importante:** estas carpetas **no se crean ahora**. Son propuesta. Implementarlas implica
> tocar áreas fuera de PolosGastro y requiere autorización.

## 8. Política de contenido Google sobre mapas no-Google

- **No** superponer datos/tiles de Google Maps Platform sobre mapas de otros proveedores
  (USIG, OpenStreetMap, Buenos Aires Data) sin revisar los **Términos de Google Maps Platform**.
- Los datos de Google Places del piloto (place_id, nombre, dirección, tipos, business_status)
  son **experimentales**: no van a mapas del informe; las **coordenadas Google no se guardan**.
- Para cartografía del informe, usar fuentes oficiales (Buenos Aires Data, USIG/GCBA), no Google.

## 9. Estándar de secrets y `.env.example`

- API keys y secretos **solo** por variable de entorno o `.env` **local** (nunca commiteado).
- `.env` real en `.gitignore`; versionar solo `.env.example` **sin valores**.
- **Nunca** imprimir, loguear ni guardar una key (ni enmascarada). Reportar solo
  presencia/ausencia.
- Aceptar nombres alternativos de variable de forma documentada (p. ej.
  `GOOGLE_MAPS_API_KEY` → `GOOGLE_PLACES_API_KEY`).
- Parsers de `.env` simples y seguros si `python-dotenv` no está instalado.

## 10. Camino sugerido

1. Validar estos estándares con Diego.
2. Pilotearlos **dentro de PolosGastro** primero (sin carpetas shared).
3. Si funcionan, extraerlos a `scripts/shared/` y `docs/datagastro_estandares/` con autorización.
4. Migrar gradualmente los otros subproyectos, sin romper sus pipelines.
