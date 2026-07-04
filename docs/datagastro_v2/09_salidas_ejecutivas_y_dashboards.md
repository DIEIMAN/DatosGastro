# DataGastro V2 — Salidas ejecutivas y dashboards

> Propuesta de salidas. **No** se generan todavía. Todas las salidas respetan el vocabulario
> institucional y la regla de **no exponer filas individuales sensibles** en entregables.

## 1. Catálogo de salidas

| Salida | Descripción | Insumo | Nivel de exposición |
|---|---|---|---|
| Mapa general gastronómico | Distribución de todo el padrón candidato en CABA | dim_candidato + territorio | agregado / puntos sanitizados |
| Mapa por rubro | Una capa por subcategoría de la taxonomía | + dim_rubro | agregado |
| Ranking por comuna | Conteo de candidatos por comuna y nivel de confianza | + territorio | agregado |
| Ranking por barrio | Ídem por barrio | + territorio | agregado |
| Densidad territorial | Candidatos por km² (geometrías GCBA) | + area_km2 | agregado |
| Cadenas vs independientes | Proporción por rubro y zona | + dim_marca_cadena | agregado |
| Rubros con concentración territorial | Subcategorías que se aglomeran en pocas zonas | analytics | agregado |
| Rubros con baja cobertura por zona | Subcategorías ausentes/escasas por comuna | analytics | agregado |
| Fichas por rubro | Resumen por subcategoría (qué es, cuántos, dónde, límites) | dim_rubro + analytics | agregado |
| Informes ejecutivos por tema | Documento para jefatura (estilo V1) | varias | agregado |
| Casos históricos / emblemáticos | Fichas con trayectoria documental | fact_trayectoria_documental | público sin datos personales |
| Base para validación territorial | Lista priorizada para campo (uso interno) | dim_candidato | **interno / gitignored** |

## 2. Reglas de exposición (obligatorias)

```text
- Entregables externos: SÓLO agregados (conteos, densidades, proporciones). Nada de filas
  individuales con nombre comercial + dirección.
- No exponer place_id, API key, teléfonos, emails ni direcciones individuales.
- Los conteos se reportan POR NIVEL DE CONFIANZA, no como total plano.
- Toda cifra se acompaña de su fuente, fecha y limitaciones (estilo fichas de fuente V1).
- "Base para validación territorial" (con filas individuales) es uso INTERNO y vive gitignored.
```

## 3. Densidad vs volumen (regla de geodatos V1)

- Distinguir **volumen** (cuántos candidatos) de **densidad** (candidatos por km² o por
  habitante). Un conteo alto en una comuna grande no implica mayor densidad.
- Declarar el **sesgo de cobertura** de cada fuente: más señal donde Google/OSM/turismo miran
  más (centro), menos en periferia → no confundir "menos cobertura" con "menos oferta".

## 4. Lenguaje de las salidas

**Usar:** padrón candidato · universo operativo probable · registro administrativo oficial ·
señal operativa no oficial · fuente abierta auxiliar · validación territorial posterior ·
nivel de confianza · orden de magnitud.

**No usar:** censo definitivo · padrón oficial · locales activos confirmados · todos los
establecimientos.

**Plantilla de frase ejecutiva:**
> "En la Comuna X, el universo operativo probable de [subcategoría] asciende a N candidatos
> (orden de magnitud), de los cuales M presentan evidencia multifuente (C5) y K provienen
> únicamente del registro administrativo oficial (sin validación de actividad). Fuente:
> [fuentes], consulta [fecha]. Sujeto a validación territorial posterior."

## 5. Dashboard V2 (propuesta, no implementación)

- Construido en **carpeta nueva** (no toca el dashboard V1).
- Capas conmutables por subcategoría y por nivel de confianza.
- Filtros: comuna/barrio, cadena/independiente, histórico/emblemático, fuente.
- Cada vista muestra **nota metodológica** y fecha de corte.
- Sólo consume **agregados sanitizados**; nunca la tabla sensible directa.

## 6. Fichas por rubro (estructura sugerida)

```text
- Qué es / qué incluye / qué excluye (de la taxonomía)
- Universo operativo probable (conteo por nivel de confianza)
- Distribución territorial (top comunas/barrios, densidad)
- Cadenas vs independientes
- Casos emblemáticos (si aplica, con referencias documentales)
- Fuentes usadas + fecha + limitaciones
- Riesgo metodológico del rubro y criterio de validación
```

## 7. Informes ejecutivos (estilo V1)

- Tono sobrio, sin lenguaje de IA, **separando hallazgos de límites** (skill
  `datagastro-informes`).
- Estructura: resumen ejecutivo → hallazgos → límites/sesgos → fuentes → próximos pasos.
- Agregados sanitizados; sin filas individuales sensibles.
