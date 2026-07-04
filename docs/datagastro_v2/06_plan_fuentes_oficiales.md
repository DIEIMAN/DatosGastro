# DataGastro V2 — Plan de fuentes oficiales

> **Plan, no ejecución.** Diseño de integración de las fuentes oficiales (públicas) en V2.
> Reutiliza lo ya construido en V1 (F01–F05) y lo amplía. **No** se descargan ni regeneran
> datos del pipeline público sin permiso explícito (F01–F05 queda intacto).

## 1. Fuentes oficiales objetivo

| Fuente | Qué aporta | Rol en V2 | Estado en V1 |
|---|---|---|---|
| AGC / habilitaciones (F02) | Registro administrativo, rubro, dirección, comuna | Ancla oficial de legitimidad | Integrado |
| BA Data / GCBA (datasets) | Bares Notables, mercados, ferias, comercios | Anclas temáticas oficiales | Parcial |
| Ente de Turismo | Oferta gastronómica curada | Curaduría oficial (sesgo turístico) | Roadmap |
| Ferias y mercados (F03) | Espacios y puestos | Espacios reales (grano mixto) | Integrado |
| Eventos gastronómicos (F04) | Ediciones datadas, trazables | Eventos / activaciones | Integrado |
| Programas / políticas (F05) | Normativa, programas, instrumentos | Contexto institucional | Integrado |

## 2. AGC / habilitaciones (F02) — ancla oficial

- **Naturaleza:** registro administrativo oficial. Mide **habilitaciones aprobadas/inferidas**,
  **no** locales activos únicos (regla permanente de V1; ver `diccionario_de_datos.md`).
- **Uso en V2:**
  - cruce con candidatos operativos (Google/OSM) para subir confianza a C5;
  - aporta rubro administrativo para resolver casos B (consumo vs producción);
  - filtro de cobertura: rubros AGC que la realidad comercial no captura ⇒ se documenta la
    brecha, no se fuerza.
- **Límite declarado:** "habilitación ≠ local activo". Nunca se reporta AGC como actividad.

## 3. BA Data / GCBA — anclas temáticas

Datasets oficiales puntuales a evaluar (catálogo abierto GCBA):

```text
- Bares Notables           → historico_emblematico (ancla oficial fuerte)
- Mercados / ferias         → ferias_mercados_eventos
- Comercios / locales        → cobertura por rubro donde exista
- Geometrías comuna/barrio  → territorio (ya en data/raw, GCBA)
```

Cada dataset entra con su **ficha de fuente** (metodología 02 de V1): URL, fecha de consulta,
licencia, grano, limitaciones, `apto_dashboard`.

## 4. Ente de Turismo — curaduría oficial

- **Aporta:** oferta gastronómica seleccionada institucionalmente (útil para emblemáticos y
  consumo en local).
- **Límite:** **sesgo turístico** — sobre-representa zonas y rubros "vistosos", sub-representa
  el comercio barrial. Se usa como **curaduría**, no como universo.
- **Integración:** preferir datos publicados/abiertos o convenio; documentar el sesgo en toda
  salida que la use.

## 5. Ferias, mercados y eventos (F03 / F04)

- **F03 (espacios):** grano mixto (mercado / feria especializada / feria agregada / puesto).
  Regla V1: los **puestos** no se cuentan como ferias; indicadores principales usan **espacios
  reales**. V2 lo mantiene.
- **F04 (eventos):** relevamiento manual trazable, fuente por fila, **no** universo completo de
  eventos. Alimenta `fact_evento_gastronomico` en V2 con la misma trazabilidad.

## 6. Reglas de no-mezcla (heredadas de V1)

```text
- No sumar F01 (oferta) + F02 (habilitaciones) como "establecimientos gastronómicos".
- No interpretar puestos F03 como ferias/mercados.
- No mezclar oficiales (F0x) con operativos (E01/E02) en un total único sin nota metodológica.
- Cada fila conserva su fuente; los agregados declaran qué universo cuentan.
```

## 7. Pipeline público intacto

- V2 **no** modifica `src/build_model.py`, `src/build_analytics.py`, `data/processed/`,
  `data/analytics/` ni el dashboard V1 sin permiso explícito de Diego.
- La integración oficial de V2 se construye en **módulos y carpetas nuevos** (ver
  `10_plan_de_implementacion_por_etapas.md`), leyendo de las salidas públicas existentes sin
  regenerarlas.

## 8. Fichas de fuente (obligatorio)

Toda fuente oficial nueva entra con ficha mínima (metodología 02 de V1):

```text
codigo, nombre, universo (F/I/E), naturaleza, url_fuente, fecha_consulta, licencia,
grano, cobertura, limitaciones, apto_dashboard, observaciones
```
