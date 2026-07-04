# Google Places API — Roadmap para PolosGastro

Fecha: 2026-06-29.

Diseño de **cómo podría** usarse Google Places API en PolosGastro y futuros informes DataGastro.
**No se ejecuta nada en esta fase.** No hay API key. No se hicieron llamadas. Es planificación.

Guardrail aplicable (skill `datagastro-fuentes-externas`): **Google Places = solo plan/diseño de
piloto, sin llamar la API. No guardar credenciales. No scraping.** Las llamadas pagas requieren
autorización explícita de Diego.

---

## 1. Para qué podría servir

- **Validar existencia actual** de locales destacados (¿siguen operando?).
- Obtener **`place_id`** como identificador estable de cada local.
- **Detectar cierres o cambios de nombre** (`business_status`).
- **Enriquecer categorías** (tipos de Google: restaurant, bar, cafe…).
- **Validar coordenadas** de locales (solo si la política de uso/cache lo permite).
- **Comparar densidad de oferta** con fuentes oficiales (Buenos Aires Data) — como contraste, no
  como reemplazo.

## 2. Para qué NO debe usarse todavía

- **No** como fuente oficial única.
- **No** para definir polos por sí sola (Google Maps tiene sesgo comercial/popularidad).
- **No** para reemplazar Buenos Aires Data ni fuentes oficiales del GCBA.
- **No** para armar mapas estáticos que mezclen contenido Google sobre bases no-Google sin
  revisar antes los Términos de Servicio de Google Maps Platform.
- **No** para guardar datos restringidos sin una política de cache acorde a esos términos.

## 3. Riesgos

- **Costo / billing**: Places API es paga; cada request cuesta según endpoint y campos.
- **API key**: si se filtra, genera gasto y abuso. Nunca commitear ni imprimir.
- **Cuotas**: límites por proyecto; un loop mal hecho dispara costo.
- **Restricciones de cache**: Google limita qué campos se pueden almacenar y por cuánto tiempo
  (`place_id` es de los pocos almacenables de forma estable; otros campos tienen límites).
- **Términos de uso**: mezclar datos de Places con mapas de otros proveedores puede violarlos.
- **Trazabilidad**: hay que registrar fecha de consulta y query exacta de cada dato.
- **Sesgo comercial**: la presencia/popularidad en Google Maps no equivale a relevancia
  gastronómica institucional ni a "polo".

## 4. Diseño seguro

- API key **solo** por variable de entorno: **`GOOGLE_MAPS_API_KEY`**.
- **Nunca guardar** la key (ni en código, ni en CSV, ni en logs, ni en `.env` commiteado).
- **Nunca imprimir** la key (ni enmascarada).
- Usar **`.env.example`** (sin valor real) como plantilla; el `.env` real va a `.gitignore` y no
  se commitea.
- Usar **`FieldMask`** para pedir solo los campos necesarios (reduce costo y datos almacenados).
- **Limitar** la cantidad de requests (tope duro en el script; piloto ≤ 10 locales).
- **`dry_run` por defecto**: el script no llama a la API salvo flag explícito.
- **Cachear solo lo permitido** por los términos (en la práctica: `place_id` + metadatos
  mínimos con fecha; no responses crudas completas).
- Guardar **`place_id`** como identificador estable.
- **Documentar fecha de consulta** en cada fila.
- **Separar outputs experimentales** (`outputs/polos_gastro/experimentos_google_places/`) de los
  outputs públicos del informe.

## 5. Campos posibles a pedir en una prueba mínima (FieldMask)

- `id` / `place_id`
- `displayName` (nombre)
- `formattedAddress` (dirección formateada)
- `types` (categorías)
- `businessStatus` (estado de negocio, si disponible)
- `location` (lat/lng) — **solo si** la política de uso/cache está clara; en el piloto puede
  omitirse para no almacenar coordenadas innecesariamente.

> Cuantos menos campos en el FieldMask, menor costo y menor superficie de datos a custodiar.

## 6. Recomendación

- Empezar con **10 locales destacados del núcleo principal** (Palermo, Puerto Madero, San Telmo,
  Recoleta) — hay ~25 disponibles en `locales_destacados_por_polo_seed.csv`.
- **No ejecutar masivamente.** Nada de barrer los 100 locales.
- Dejarlo como **experimento aislado**, fuera del pipeline.
- **Antes de la primera llamada real**: confirmar con Diego (a) que hay API key con billing
  controlado, (b) revisión de los Términos de Google Maps Platform, (c) tope de gasto.

Diseño técnico detallado en `DISEÑO_EXPERIMENTO_GOOGLE_PLACES.md`.
Script piloto (dry-run por defecto) en `scripts/polos_gastro/google_places/`.
