# Mercados gastronómicos CABA — Fuentes posibles

> Catálogo de fuentes para el informe de **mercados gastronómicos**. Machine-readable:
> `outputs/mercados_caba/sanitized/fuentes_mercados_candidatas.csv`. **No** se descargó ni
> consultó ninguna fuente externa en esta etapa. De cada fuente se retiene **solo** lo que tenga
> foco gastronómico/alimentario; el resto se descarta o se marca fuera de alcance.

## 1. Fuentes locales ya disponibles (públicas, solo lectura)

| Código | Fuente | Qué aporta | Estado |
|---|---|---|---|
| `F03_mercados` | Ferias y Mercados — mercados (GCBA BA Data) | 6 CAM + Mercado Comunitario; filtrar por foco alimentario/gastronómico | en repo (`data/raw/`) |
| `F03_ferias` | Ferias y Mercados — ferias (GCBA BA Data) | 30 ferias; quedarse solo con ferias gastronómicas / de productores de alimentos (excluir pulgas, antigüedades, manualidades) | en repo |
| `F03_espacios_proc` | `fact_espacio_feria_mercado` (procesado V1) | espacios reales (grano mixto); filtrar foco gastronómico | en repo (no regenerar) |

> Estas son la **ancla oficial** de partida. Cubren mercados públicos/ferias con foco
> alimentario; **no** cubren los mercados gastronómicos privados ni food halls, que se relevan
> con fuentes externas.

## 2. Fuentes oficiales a relevar (descarga/relevamiento futuro, con aprobación)

| Código | Fuente | Rol |
|---|---|---|
| `BA_DATA` | Buenos Aires Data (catálogo) | identificar dataset directo de mercados gastronómicos / food halls / productores |
| `TURISMO_BA` | Ente de Turismo / Turismo BA | mercados gastronómicos con perfil turístico (sesgo turístico) |
| `BA_CAPITAL_GASTRO` | BA Capital Gastronómica | contexto de política pública |
| `SITIO_GCBA` | buenosaires.gob.ar | fichas oficiales por mercado |
| `SITIOS_MERCADOS` | sitios/redes oficiales de cada mercado | horarios y oferta autodeclarados |

URLs: **no se inventan**. Se relevan con su ficha de fuente (título, URL, fecha) antes de usar.

## 3. Fuentes externas auxiliares (plan, no ejecución)

| Código | Fuente | Rol | Plan |
|---|---|---|---|
| `OSM` | OpenStreetMap | cobertura y geometría | `08_plan_osm_mercados.md` |
| `GOOGLE_PLACES` | Google Places API | cobertura amplia y actividad | `07_plan_google_places_mercados.md` |
| `PRENSA` | notas periodísticas | casos y contexto | priorizar autoría/fecha |
| `PERPLEXITY` | búsqueda asistida | **localizar** fuentes, no fuente final | `06_prompt_perplexity_mercados.md` |

## 4. Fuentes internas (solo metadata/agregados, sin PII)

| Código | Fuente | Señal detectada | Uso |
|---|---|---|---|
| `I_DGDGAS` | Fuentes internas DGDGAS | "PATIO Y MERCADOS" (categoría de eventos), "BUENOS AIRES MARKET" (organizador) | contexto de eventos/activaciones en mercados |
| `INVENTARIO_DRIVE` | Inventarios de Drive copiados | referencias tipo "Mercados Madrid" | detección de documentos, solo metadata |

**Reglas de privacidad:** de las fuentes internas se usan **solo conteos/metadata agregada**. No
se publican contactos, teléfonos, mails, referentes, CUIT, nombres de personas ni links privados
de Drive. El material crudo interno queda en `outputs/mercados_caba/internal/` (gitignored).

## 5. Jerarquía de confianza entre fuentes (heredada de DataGastro)

```text
1. GCBA / BA Data con recurso directo
2. Boletín Oficial / normativa
3. Web oficial GCBA / Turismo BA
4. Sitios oficiales de cada mercado
5. OSM (auxiliar) / Google Places (operativa no oficial)
6. Prensa con autoría y fecha
7. Perplexity / web: solo localizador, nunca fuente final
```

Ante conflicto, gana la fuente más alta. Las externas/operativas se marcan para validación.
