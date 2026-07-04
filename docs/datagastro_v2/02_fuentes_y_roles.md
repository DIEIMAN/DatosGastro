# DataGastro V2 — Fuentes y roles metodológicos

> Catálogo de fuentes para V2 y el **rol** de cada una. Mantiene la separación de universos de
> V1 (públicas F0x, internas I0x, externas/privadas E0x). Ninguna fuente es "la verdad": cada
> una aporta una señal con un rol distinto.

## 1. Clasificación de universos (heredada de V1)

```text
F01–F05   públicas oficiales / relevamiento público trazable
I01–I99   internas (datos propios, no públicos)
E01–E99   externas / privadas (terceros: Google, OSM, prensa, plataformas)
```

Regla permanente: **no mezclar universos** como uno solo sin declarar la fuente por fila.

## 2. Catálogo de fuentes V2

| Código | Fuente | Universo | Naturaleza | Rol en V2 | Oficial |
|---|---|---|---|---|---|
| F02 | AGC / habilitaciones | Pública | Registro administrativo | **Ancla oficial** (rubros, dirección, comuna) | Sí |
| F0x | BA Data / GCBA datasets | Pública | Datos oficiales abiertos | Anclas oficiales temáticas (Bares Notables, mercados, ferias) | Sí |
| F0x | Ente de Turismo | Pública | Oferta gastronómica curada | Curaduría oficial de oferta (sesgo turístico) | Sí |
| F03 | Ferias y mercados | Pública | Padrón/espacios | Espacios y puestos (grano mixto, ver V1) | Sí |
| F04 | Eventos gastronómicos | Pública | Relevamiento manual trazable | Eventos/ediciones datadas | Parcial |
| E01 | Google Places API | Externa | Señal operativa no oficial | **Cobertura amplia** + detección de actividad/cadenas | No |
| E02 | OpenStreetMap | Externa | Fuente abierta auxiliar | Cobertura auxiliar, geometría, tags de rubro | No |
| E03 | Fuentes documentales web | Externa | Documental | Casos históricos, rubros emblemáticos, contexto | No |
| E04 | Perplexity / búsqueda asistida | Externa | **Localizador** de fuentes | Encuentra documentales; **no** es fuente final | No |
| I01 | Revisión manual | Interna | Validación humana trazable | Decide A/B/C, corrige clasificación | — |
| I02 | Validación territorial posterior | Interna | Trabajo de campo (futuro) | Confirma existencia/actividad real | — |

## 3. Rol metodológico por fuente

### F02 — AGC / habilitaciones (ancla oficial)
- **Aporta:** registro administrativo oficial, rubro declarado, dirección, comuna.
- **Límite:** mide **habilitaciones**, no locales activos. Puede ser **angosto** (rubros que no
  capturan la realidad del comercio especializado). No usar como prueba de actividad.
- **Rol:** ancla de legitimidad. Cuando un candidato coincide con AGC, sube su confianza
  "oficial", pero no se afirma que esté activo.

### BA Data / GCBA (anclas temáticas)
- **Aporta:** datasets oficiales puntuales (Bares Notables, mercados, ferias, comercios).
- **Rol:** anclas oficiales por tema; ideales para `historico_emblematico` y
  `ferias_mercados_eventos`.

### Ente de Turismo (curaduría oficial)
- **Aporta:** oferta gastronómica seleccionada institucionalmente.
- **Límite:** **sesgo turístico** (sobre-representa zonas y rubros "vistosos").
- **Rol:** curaduría, no universo. Útil para emblemáticos y consumo en local.

### Google Places API (señal operativa no oficial)
- **Aporta:** la **cobertura más amplia** de actividad comercial, nombres, coordenadas,
  `businessStatus`, `types`, y señal de **cadenas** (repetición de nombre/marca).
- **Límite:** no oficial; etiqueta gruesa (`restaurant`/`store`); riesgo de confundir producción
  con consumo; datos sensibles (place_id, dirección, teléfono).
- **Rol:** motor de cobertura y detección de actividad/cadenas. Plan detallado en
  `04_plan_integracion_google_places.md`.

### OpenStreetMap (fuente abierta auxiliar)
- **Aporta:** tags de rubro (`amenity`, `shop`, `craft`), geometría, cobertura colaborativa.
- **Límite:** completitud desigual; calidad variable por zona.
- **Rol:** auxiliar y de contraste. Plan en `05_plan_integracion_osm.md`.

### Documentales web (contexto y memoria)
- **Aporta:** notas periodísticas, sitios oficiales, historia barrial, rubros emblemáticos.
- **Rol:** sostener `historico_emblematico` y enriquecer fichas. **Nunca** fuente única de
  existencia sin un ancla (oficial u operativa).

### Perplexity / búsqueda asistida (localizador)
- **Aporta:** acelera el hallazgo de fuentes documentales y oficiales.
- **Límite:** puede alucinar; **no** es fuente final.
- **Rol:** localizador. Toda afirmación que provenga de aquí debe quedar respaldada por una URL
  documental verificable (título, medio, fecha). Detalle en `07_...md`.

### Revisión y validación interna
- `I01` decide casos B (dudosos) y corrige clasificación.
- `I02` (futuro) confirma en territorio. Es lo que convierte "candidato" en "confirmado".

## 4. Cómo se combinan las fuentes

```text
Cobertura amplia        Google Places (E01) + OSM (E02)
Legitimidad oficial     AGC (F02) + BA Data + Ente Turismo
Memoria / emblemático   Documentales (E03) localizados con Perplexity (E04)
Decisión final          Revisión manual (I01) → Validación territorial (I02)
```

Principio: **multifuente sube confianza** (ver `03_niveles_de_confianza.md`). Una entidad
detectada por Google + AGC + OSM es más confiable que una detectada por una sola, pero la
detección única **no se descarta** — sólo queda en confianza menor / revisión.

## 5. Lo que ninguna fuente autoriza a decir

- Que el universo está **completo**.
- Que un registro es un **local activo confirmado** (sólo F02 + actividad observable + I02 lo
  acercan, nunca lo garantizan al 100%).
- Mezclar conteos de fuentes distintas como un total único sin nota metodológica.
