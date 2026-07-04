# Estado de fuentes pendientes — post Perplexity 2

Fecha: 2026-06-29.

Síntesis tras incorporar la **Respuesta 2 de Perplexity**
(`perplexity_respuesta_2_busqueda_puntual_faltantes.md`). Esta ronda **no aportó fuentes nuevas
de validación**: confirma el universo vigente y refuerza criterios de prudencia.
Detalle normalizado: `outputs/polos_gastro/perplexity_respuesta_2_aportes_normalizados.csv`.

> **El universo del informe NO cambia.** Ningún polo sube de categoría por esta respuesta.

---

## 1. Fuentes fuertes confirmadas

Todas ya cargadas en la matriz; la respuesta 2 las ratifica como núcleo de validación:

- Turismo BA — **Polos gastronómicos** (oficial).
- Turismo BA — **Gastronomía en Buenos Aires** (oficial).
- Turismo BA — **Guía de Turismo de Reuniones** (oficial; Puerto Madero).
- **Buenos Aires Data — Oferta y Establecimientos gastronómicos** (datos abiertos; base de
  densidad/mapas, no define polos).
- **La Nación — "Casi el 60%…"** (periodística; concentración barrial, respaldo secundario).

Núcleo principal ratificado: **Palermo (Soho/Hollywood/Las Cañitas), Puerto Madero, San Telmo,
Recoleta**.

## 2. Fuentes repetidas

Toda la "tabla de fuentes" de la respuesta 2 repite URLs **ya presentes** en
`fuentes_externas_polos_gastro.csv`. No se duplican en la matriz principal.

## 3. Polos que siguen débiles (confirmado)

La respuesta 2 reconfirma debilidad de evidencia para:

- **Federico Lacroze / Libertador a Cabildo** — sin fuente verificable (URL pendiente PX023A/B).
- **Parque Saavedra / García del Río** — sin fuente (PX024B).
- **Paternal** — sin fuente específica de circuito (PX025A).
- **Costanera Norte** — sin fuente sólida en esta pasada.
- **Avenida Corrientes** — identidad cultural, no probado lo gastronómico.
- **DoHo / Donado-Holmberg** — sin fuente verificable nueva.
- **Avenida Boedo** — sin evidencia suficiente.
- **Abasto** — datos abiertos sí, respaldo narrativo no.
- **Villa Urquiza** — oferta sí, corredor consolidado no.
- **Devoto** — presencia sí, polo no.
- **Villa Pueyrredón / Av. San Martín** — solo base de oferta, sin corredor.

Estos 11 casos **se mantienen con prudencia** (su grupo actual en el universo se conserva).

## 4. Polos que NO deberían subir de categoría

Por esta respuesta, **ninguno**. Específicamente, no elevar:
Chacarita, Costanera Norte, Avenida Corrientes, DoHo, Villa Urquiza, Abasto, Devoto, Paternal,
Federico Lacroze, García del Río, Villa Pueyrredón, Avenida Caseros / Barracas, ni los subejes
de Belgrano (Barrio Chino sigue como subzona; Bajo Belgrano y Belgrano R no suben).

Los barrios de alta concentración (Caballito, Colegiales, Monserrat, Flores, Floresta, Parque
Patricios, Belgrano R) siguen como **relevantes/emergentes/anexo con prudencia**, no como polos
consolidados: la concentración de locales no equivale a polo.

## 5. Fuentes cartográficas confirmadas

- **Buenos Aires Data** (oferta gastronómica + capas de barrios/comunas) — base recomendada.
- **Portal Buenos Aires Data** (`data.buenosaires.gob.ar`) — ubicar capas barrios/comunas.
- Coincide con lo documentado en `cartografia/FUENTES_CARTOGRAFICAS_CABA.md`. No agrega capas
  nuevas; ratifica la elección.

## 6. Fuentes narrativas útiles (contexto, no validación de polos)

Dos referencias institucionales **no presentes** antes en la matriz, útiles solo para el relato
del informe (marcadas `aporta_evidencia_nueva = parcial` en el CSV):

- **Observatorio turístico de CABA — Tableros**:
  https://turismo.buenosaires.gob.ar/es/observatorio/tableros — tendencias, no geometría.
- **BA Capital Gastronómica / Desarrollo Gastronómico (GCBA)**:
  https://buenosaires.gob.ar/gcaba_historico/desarrolloeconomico/gastronomia — marco de política
  pública para introducción/contexto.

> Ambas son **contexto narrativo**, no delimitan polos. Verificar vigencia de las URLs antes de
> citarlas en el informe (no se confirmaron en esta fase).

## 7. Qué falta buscar manualmente

- Notas/mapas específicos de corredor para: Chacarita, DoHo, Costanera Norte, Corrientes, Boedo,
  Devoto, Paternal, Villa Urquiza, Parque Saavedra, Villa Pueyrredón.
- Belgrano desagregado (Barrio Chino, Bajo Belgrano, Belgrano R).
- Documentos de centros comerciales a cielo abierto, cámaras gastronómicas o material
  comunal/barrial que fije límites y evolución de corredores.
- (Continúa lo ya listado en `BUSQUEDAS_COMPLEMENTARIAS_PENDIENTES.md`.)

## 8. Qué NO vale la pena seguir buscando por ahora

- Más fuentes turísticas **genéricas** que solo nombran "polos" sin delimitar: ya saturado.
- Repetir consultas que devuelven la nota de La Nación 60% o las páginas de Turismo BA ya
  cargadas: no aportan evidencia nueva.
- Forzar validación de los 4 casos de URL pendiente con fuentes débiles: mejor dejarlos como
  pendientes declarados que inflarlos.

---

## Conclusión

La Respuesta 2 cierra la ronda de Perplexity con valor **metodológico**, no de nuevas fuentes.
El próximo salto de evidencia para los polos débiles ya **no** vendrá de Perplexity, sino de
**búsqueda manual dirigida** y, eventualmente, de **medición cuantitativa** (Buenos Aires Data
de oferta y/o el experimento Google Places — ver `google_places/`).
