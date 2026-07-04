# DataGastro V2 — Niveles de confianza

> Escala formal de confianza para el padrón candidato y reglas de promoción/degradación.
> Generaliza la clasificación A/B/C del piloto de casas de pastas a todo el ecosistema.

## 1. Filosofía

- La confianza es una propiedad **por entidad** y **por fuente**, no una verdad binaria.
- **Aparecer en más de una fuente independiente sube la confianza.**
- **Aparecer en una sola fuente NO descarta:** las casas independientes barriales suelen estar
  en una sola fuente y son **centrales** para V2.
- Ninguna confianza, ni la máxima, equivale a "local activo confirmado". Eso requiere
  validación territorial posterior (I02).

## 2. Escala de confianza (nivel de entidad)

| Nivel | Etiqueta | Significado | Condición típica |
|---|---|---|---|
| C5 | `multifuente_alto` | Evidencia concordante en ≥2 fuentes independientes | Google A + AGC, o AGC + OSM + documental |
| C4 | `oficial_estricto` | Sólo registro administrativo oficial | Sólo AGC/BA Data. Oficial, **no** implica activo |
| C4 | `operativo_probable` | Sólo señal operativa fuerte | Sólo Google A (nombre/tipo inequívoco) |
| C3 | `auxiliar_abierto` | Sólo fuente abierta auxiliar | Sólo OSM con tag claro |
| C2 | `documental` | Sostenido por documentales | Caso emblemático con ≥2 referencias, sin ancla operativa |
| C1 | `revision_manual` | Dudoso / señales mixtas | Google B, OSM ambiguo, rubro confuso |
| C0 | `pendiente_taxonomica` | Rubro no resuelto | No se pudo clasificar el rubro todavía |
| X | `descartado_conservado` | Fuera del rubro objetivo | Restaurante italiano en búsqueda de casas de pastas. Se **conserva** aparte |

> C4 tiene dos sabores (`oficial_estricto` y `operativo_probable`) porque provienen de
> universos distintos (oficial vs operativo) y **no** deben sumarse como uno solo.

## 3. Reglas de promoción

```text
P1  Dos fuentes independientes concordantes  → C5 multifuente_alto
P2  AGC confirma un C4 operativo_probable     → C5 (oficial + operativo)
P3  Documental confirma identidad/rubro de un C1 → sube a C2/C3 según ancla
P4  Revisión manual (I01) valida un C1        → C3/C4 con motivo registrado
P5  Validación territorial (I02) confirma     → marca confirmado_territorial = si (transversal)
```

`confirmado_territorial` es un **flag aparte**, no un nivel: cualquier nivel puede tener
validación de campo cuando exista I02.

## 4. Reglas de degradación / conservación

```text
D1  Señales mixtas (consumo vs producción no resueltas) → C1 revision_manual
D2  Sólo Perplexity/web sin URL verificable             → no entra; queda como pista a verificar
D3  businessStatus = CLOSED/CLOSED_TEMPORARILY (Google)  → flag posible_cierre, no se elimina
D4  Fuera del rubro objetivo                             → X descartado_conservado (no se borra)
```

Nada se **elimina**: lo descartado se conserva en una tabla aparte con su motivo, igual que en
el piloto V1 (`deduplicacion_fuentes.csv`).

## 5. Campos de confianza en el modelo

Por entidad (`dim_establecimiento_candidato`):

```text
nivel_confianza            C0..C5 / X
etiqueta_confianza         multifuente_alto | oficial_estricto | operativo_probable | ...
fuentes_detectan           lista de códigos (F02, E01, E02, ...)
cantidad_fuentes           entero
fuente_principal           código de la fuente de mayor peso
requiere_revision_manual   si | no
motivo_clasificacion       texto trazable
confirmado_territorial     si | no | pendiente
```

Por detección (`fact_deteccion_fuente`): confianza **local** de esa fuente (ej.: Google A/B/C,
OSM tag fuerte/débil) antes de integrar.

## 6. Cómo se comunica la confianza en salidas ejecutivas

- Los conteos se reportan **por nivel de confianza**, no como un total plano.
- Ejemplo de redacción institucional:
  > "El universo operativo probable de casas de pastas en la Comuna 5 asciende a N candidatos,
  > de los cuales M presentan evidencia multifuente (C5) y K provienen únicamente del registro
  > administrativo oficial (C4, sin validación de actividad)."
- Nunca: "hay N casas de pastas activas".

## 7. Relación con V1

La clasificación integrada del piloto (`A_integrado_multifuente`, `A_agc_oficial_estricto`,
`A_google_probable`, `A_osm_auxiliar`, `B_revision_manual`, `C_descartado`) es un **caso
particular** de esta escala. Tabla de equivalencia:

| V1 (piloto) | V2 (nivel) |
|---|---|
| A_integrado_multifuente | C5 multifuente_alto |
| A_agc_oficial_estricto | C4 oficial_estricto |
| A_google_probable | C4 operativo_probable |
| A_osm_auxiliar | C3 auxiliar_abierto |
| B_revision_manual | C1 revision_manual |
| C_descartado | X descartado_conservado |
