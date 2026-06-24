# Mercados gastronómicos CABA — Metodología y niveles de confianza

> Cómo se construye y se comunica el relevamiento candidato de **mercados gastronómicos**.

## 1. Unidad de análisis

**1 ficha = 1 mercado gastronómico o espacio tipo mercado con eje gastronómico** (ver campos en
`05_campos_objetivo.md`). Cada ficha lleva fuente(s), nivel de confianza y `estado_revision` del
foco gastronómico. El conjunto es un **relevamiento candidato**, no un padrón oficial ni un censo.

## 1.bis Filtro de alcance (primer paso de toda ficha)

Antes de clasificar, se aplica el criterio de inclusión/exclusión de `00_vision_y_objetivo.md`.
Si la gastronomía/los alimentos no son el eje, la ficha se marca `fuera_de_alcance_no_gastronomico`
o, si hay duda, `dudoso_pendiente_revision`. Nunca se descarta en silencio.

## 2. Flujo metodológico

```text
A. Anclas oficiales locales (F03 mercados/ferias)        -> candidatos base
B. Fuentes oficiales a relevar (BA Data, Turismo BA, GCBA) -> ampliar y enriquecer
C. Externas auxiliares (OSM, Google Places)              -> cobertura y actividad
D. Documental (sitios oficiales, prensa; Perplexity localiza) -> horarios/oferta/casos
E. Internas DGDGAS (metadata/agregados)                  -> eventos/activaciones, contexto
F. Revisión manual                                       -> tipología y desambiguación
G. Validación territorial posterior                      -> confirma estado y oferta
```

Cada transición es un gate de aprobación. Esta etapa deja A listo y B–G planificados.

## 3. Niveles de confianza por ficha

| Nivel | Significado | Condición típica |
|---|---|---|
| `alto` | concordancia multifuente o fuente oficial + verificación | oficial + sitio del mercado, u oficial + territorial |
| `medio` | una fuente sólida sin verificación cruzada | Turismo BA o sitio oficial únicos |
| `oficial_incompleto` | registro oficial sin oferta/horarios validados | F03 mercados (existe, pero faltan campos) |
| `bajo` | señal débil o ambigua | solo OSM/Google, o nombre ambiguo |
| `pendiente` | sin dato suficiente para clasificar | a relevar |

> Aparecer en más de una fuente independiente **sube** la confianza. Aparecer en una sola **no**
> descarta: queda en confianza menor / revisión.

## 4. Reglas de no-mezcla (heredadas)

- No sumar mercados públicos (F03) con privados (externos) como un total único sin nota.
- No interpretar puestos de feria como mercados.
- No mezclar universos oficial/externo/interno sin declarar la fuente por fila.
- No sumar candidatos `fuera_de_alcance` ni `dudoso_pendiente_revision` al total de mercados
  gastronómicos confirmados.
- Registro/habilitación ≠ actividad confirmada.

## 5. Comunicación prudente (lenguaje)

**Usar:** relevamiento candidato · universo probable · registro oficial · señal operativa no
oficial · fuente abierta auxiliar · validación posterior · orden de magnitud.

**No usar:** censo definitivo · padrón oficial · todos los mercados · locales activos
confirmados.

## 6. Privacidad

Material interno/crudo en `outputs/mercados_caba/internal/` y `raw/` (gitignored). Entregables
solo en `outputs/mercados_caba/sanitized/`, sin teléfonos, emails, referentes, CUIT, place_id ni
links privados de Drive. Validación automatizada en `src/mercados_caba/validate_mercados_setup.py`.
