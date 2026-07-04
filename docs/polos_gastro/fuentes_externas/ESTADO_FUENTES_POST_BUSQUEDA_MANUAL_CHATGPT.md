# Estado de evidencia — post búsqueda manual (ChatGPT)

Fecha: 2026-06-29.

Síntesis tras incorporar las fuentes manuales documentadas en
`FUENTES_COMPLEMENTARIAS_MANUALES_CHATGPT.md`. A diferencia de la ronda Perplexity 2, esta sí
trajo **fuentes nuevas verificadas** y produjo **un cambio de universo**.

---

## 1. Fuentes nuevas incorporadas (12)

Agregadas a `fuentes_externas_polos_gastro.csv` como `CM001`–`CM012` (total de fuentes:
80 → 92). No se duplicaron las 2 que ya existían (Costanera Norte oficial, Circuito Sin Pausa).

- **Oficiales verificadas (alta):** Patio Costanera Norte (Turismo) CM001, Patio Costanera Norte
  (GCBA) CM002, Calle Corrientes CM003, Las pizzerías de Corrientes CM004.
- **Periodísticas verificadas (media):** El Cronista – Chacarita CM007, Infobae – Chacalermo
  CM008, TimeOut – Chacarita CM009.
- **Pendientes de verificar URL (`requiere_revision_manual = si`):** Barrio Chino/GCBA CM005,
  Clarín – Chacarita/Newbery CM006, Clarín – Federico Lacroze (antigua) CM010, Clarín – Bulevar
  García del Río CM011, TimeOut – Paternal (genérica) CM012.

## 2. Fuentes que no abrieron

- **clarin.com** (CM006, CM010, CM011): WebFetch no accede a ese dominio. Quedan documentadas
  con `requiere_revision_url`. **No** se usaron para elevar polos por encima de anexo.
- **Barrio Chino/GCBA** (CM005) y **TimeOut Paternal** (CM012): no verificadas en esta pasada.

## 3. Polos que ganan evidencia

- **Chacarita** — respaldo periodístico múltiple verificado (Cronista, Infobae, TimeOut). Una
  fuente la llama "el polo gastronómico más interesante de la ciudad". Mejora la justificación.
- **Costanera Norte** — Patio Costanera Norte (Turismo + GCBA) verificados. Hito gastronómico
  oficial confirmado.
- **Avenida Corrientes** — Calle Corrientes + pizzerías (oficiales, verificadas). Confirma el
  eje cultural-gastronómico.
- **Parque Saavedra / García del Río** — señal periodística del Bulevar García del Río (no
  verificable, pero existe).

## 4. Polos que siguen débiles

- **Federico Lacroze** — única fuente nueva es antigua y no verificable. Sigue débil.
- **Paternal** — solo mención genérica en un ranking. Sigue débil (URL pendiente PX025A).
- **DoHo / Donado-Holmberg** y **Villa Urquiza** — sin evidencia nueva (Circuito Sin Pausa ya
  estaba). Sin cambio.
- **Barrio Chino** — refuerzo contextual (URL pendiente); sigue subzona de Belgrano.

## 5. Cambios recomendados en universo

| Polo | Recomendación | Aplicado |
| --- | --- | --- |
| García del Río | no_incluir → **anexo** (prudente) | **Sí** |
| Chacarita | mantener zona relevante (mejor justificada) | Sí (sin cambio de grupo) |
| Costanera Norte | mantener emergente (mejor justificada) | Sí (sin cambio de grupo) |
| Av. Corrientes | mantener emergente / eje cultural-gastronómico | Sí (sin cambio de grupo) |
| Federico Lacroze | mantener no_incluir | Sí (sin cambio) |
| Paternal | mantener emergente débil | Sí (sin cambio) |

## 6. Cambios efectivamente aplicados

- **Parque Saavedra / García del Río**: `grupo_informe` no_incluir_por_ahora → **anexo**;
  `estado_validacion` requiere_validacion → candidato_con_evidencia;
  `decision_para_informe` no_incluir_aun → mencionar_en_anexo;
  `nivel_evidencia` insuficiente → parcial_baja. Aplicado en `universo_informe_*.csv` y
  `base_delimitacion_*.csv`, con observación de fecha y motivo. Ficha actualizada.
- **Fuentes** CM001–CM012 agregadas a `fuentes_externas_polos_gastro.csv`.
- **Fichas** actualizadas (sección 17): Chacarita, Costanera Norte, Av. Corrientes, García del Río.

Distribución de grupos resultante (32): núcleo 6 · zona relevante 5 · emergente 9 · **anexo 8** ·
**no incluir 4** (antes anexo 7 / no incluir 5).

> `matriz_validacion_polos_gastro.csv` **no se modificó**: su `cantidad_fuentes_*` se deriva de
> la corrida Fase 2 y regenerarla cambiaría conteos internos sin necesidad para esta fase. El
> aporte de las nuevas fuentes queda trazado en `fuentes_externas_*.csv` y en las fichas.

## 7. Justificación de prudencia

- **Ningún polo subió a núcleo ni a relevante** por estas fuentes. La evidencia periodística
  refuerza identidad/emergencia, pero no es oficial-cartográfica.
- **García del Río** sube solo a **anexo** (no a candidato pleno) porque su fuente no pudo
  verificarse (clarin.com). Es el mínimo movimiento defendible: deja de estar "fuera" pero no
  se le da peso de candidato con evidencia verificada.
- Las fuentes de clarin.com quedan con `requiere_revision_url` para verificación manual antes de
  cualquier uso en informe.
- No se convirtió ninguna mención de concentración/identidad en "locales activos" ni en
  delimitación oficial.
