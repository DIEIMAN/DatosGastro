# Fase 5 — Auditoría de estado: información y mapas (PolosGastro)

Fecha: 2026-06-30.
Alcance revisado: `PolosGastro/`, `docs/polos_gastro/`, `outputs/polos_gastro/`,
`scripts/polos_gastro/`. **Material de trabajo, no informe final.** No se modificó ningún
dato fuente, output anterior, PDF ni XLSX. Sin commit/push/staging.

Esta auditoría vuelve al **foco principal** del proyecto (información útil + documentación de
polos débiles + mapas territoriales claros + base para informe serio) y **deja explícitamente
como material experimental/interno los mapas conceptuales y gráficos de barras** que no
convencen visualmente. Ver `FASE_5_CRITERIO_USO_VISUALES.md`.

---

## 1. Qué insumos existen

### Datos (`outputs/polos_gastro/`)
- **Universo defendible** — `universo_informe_polos_gastro.csv` (32 polos: grupo, evidencia,
  decisión, riesgo). **Fuente principal de clasificación.**
- **Delimitación textual** — `base_delimitacion_preliminar_polos_gastro.csv` (familia, barrios
  asociados, comunas probables, nivel de precisión, fuente de delimitación). **Insumo clave
  para mapas territoriales** (da barrio/comuna por polo).
- **Matriz de validación** — `matriz_validacion_polos_gastro.csv` (conteo de fuentes por polo:
  alta/media/baja/requiere_revision; flags de tipo de fuente). Derivada de Fase 2.
- **Fuentes externas** — `fuentes_externas_polos_gastro.csv` (92 fuentes, incl. CM001–CM012
  manuales). Trazabilidad fuente→polo.
- **Bases de visuales** — `base_cartografica_visual_polos_gastro.csv`,
  `base_mapa_conceptual_polos_gastro.csv`, `fuentes_por_familia_territorial.csv`.
- **Semilla / históricos** — `polos_gastronomicos_base_candidata.csv`,
  `locales_destacados_por_polo_seed.csv`, `nombres_publicos_polos_gastro.csv`,
  `perplexity_*`, `resumen_*`. (No tocar; son base histórica.)
- **Experimentos Google Places** — `experimentos_google_places/*.csv` (piloto, 10 locales).
- **Revisión manual** — `revision_manual_pre_borrador.csv` (paquete de revisión de Diego).

### Cartografía oficial (`PolosGastro/cartografia/`)
- `barrios_caba.geojson` (48 barrios, Buenos Aires Data) y `comunas_caba.geojson` (15 comunas).
  **Disponibles y validados.** Son la base para los mapas territoriales reales.

### Documentación (`docs/polos_gastro/`)
- README, esqueleto y plan de ensamblado del informe.
- Auditorías previas (Fase 2, mapa conceptual Fase 3B, visual, integral, QA de consistencia).
- 32 fichas en `fichas_polos/`.
- `fuentes_externas/` (estado de fuentes, búsquedas pendientes, Perplexity 1 y 2, ChatGPT).
- `google_places/` (roadmap, diseño, reporte piloto).
- `cartografia/` (fuentes cartográficas, librerías, USIG, reporte Fase 4A).
- `REVISION_MANUAL_DIEGO_PRE_BORRADOR.md`.

### Scripts (`scripts/polos_gastro/`)
- `inventariar_polos_gastro.py`, `generar_validacion_documental_fase2.py`,
  `definir_universo_informe_polos_gastro.py`, `fase3a_urls_y_delimitacion_textual.py`,
  `generar_mapa_conceptual_polos_gastro.py`, `cartografia/generar_visuales_polos_gastro_fase4a.py`,
  `google_places/places_piloto_locales.py`, experimento USIG aislado.

---

## 2. Qué polos están clasificados

**32 polos** clasificados por grupo. Distribución vigente:

| Grupo | Cantidad | Polos |
| --- | --- | --- |
| Núcleo principal | 6 | Palermo Soho, Palermo Hollywood, Las Cañitas, Puerto Madero, San Telmo, Recoleta |
| Zona relevante | 5 | Chacarita, Barrio Chino, Microcentro/Centro, Monserrat, Retiro |
| Emergente / candidato | 9 | Villa Crespo, Caballito, Costanera Norte, Av. Corrientes, Devoto, DoHo/Donado-Holmberg, Villa Urquiza, Paternal, Colegiales |
| Anexo | 8 | Belgrano R, Av. Caseros/Barracas, Abasto, Nuevo Bajo en Retiro, García del Río, Flores, Floresta, Parque Patricios |
| No incluir por ahora | 4 | Bajo Belgrano, Av. Boedo, Federico Lacroze, Villa Pueyrredón/Av. San Martín |

> Esta clasificación **coincide** con la clasificación de referencia del prompt, con tres
> diferencias documentadas (ver §abajo). No se cambió nada en esta fase.

**Diferencias entre la clasificación de referencia del prompt y el universo real (documentadas, no
modificadas):**
- **Microcentro/Centro** y **Monserrat** y **Retiro** ya están en **zona relevante** (el prompt
  los listaba ahí también; coincide). El prompt listaba "Microcentro / Centro" y "Monserrat" y
  "Retiro" como relevantes → coincide.
- **García del Río** está en **anexo** (no en "no incluir"). Cambio del 2026-06-29 por fuente
  periodística del Bulevar García del Río (`requiere_revision_url`). El prompt lo listaba en
  anexo → coincide.
- **Federico Lacroze**, **Villa Pueyrredón/Av. San Martín**, **Bajo Belgrano**, **Av. Boedo**
  están en **no incluir** → coincide con el prompt.

  No hay contradicciones que requieran reclasificar. Todo el universo del prompt está alineado
  con `universo_informe_polos_gastro.csv`.

---

## 3. Qué fuentes tiene cada polo

Conteo desde `matriz_validacion_polos_gastro.csv` (alta/media/requiere_revision_url) cruzado con
`universo_informe_polos_gastro.csv`:

| Polo | Grupo | Fuentes alta | Fuentes media | Req. rev. URL | URL pendiente |
| --- | --- | :-: | :-: | :-: | :-: |
| Palermo Soho | núcleo | 2 | 0 | 0 | no |
| Palermo Hollywood | núcleo | 2 | 0 | 0 | no |
| Las Cañitas | núcleo | 2 | 0 | 0 | no |
| Puerto Madero | núcleo | 1 | 1 | 0 | no |
| San Telmo | núcleo | 2 | 0 | 0 | no |
| Recoleta | núcleo | 2 | 0 | 0 | no |
| Chacarita | relevante | 1 | 1 | 1 | no |
| Barrio Chino | relevante | 2 | 1 | 0 | no |
| Microcentro/Centro | relevante | 0 | 3 | 0 | no |
| Monserrat | relevante | 0 | 2 | 0 | no |
| Retiro | relevante | 1 | 1 | 0 | no |
| Villa Crespo | emergente | 0 | 3 | 0 | no |
| Caballito | emergente | 0 | 4 | 0 | no |
| Costanera Norte | emergente | 0 | 2 | 2 | no |
| Av. Corrientes | emergente | 0 | 1 | 2 | no |
| Devoto | emergente | 0 | 2 | 1 | no |
| DoHo/Donado-Holmberg | emergente | 1 | 0 | 2 | no |
| Villa Urquiza | emergente | 1 | 1 | 1 | no |
| Paternal | emergente | 0 | 1 | 2 | **sí (PX025A)** |
| Colegiales | emergente | 0 | 2 | 0 | no |
| Belgrano R | anexo | 0 | 1 | 1 | no |
| Av. Caseros/Barracas | anexo | 0 | 2 | 0 | no |
| Abasto | anexo | 0 | 2 | 1 | no |
| Nuevo Bajo en Retiro | anexo | 1 | 1 | 0 | no |
| García del Río | anexo | 0 | 1 | 1 | **sí (PX024B)** |
| Flores | anexo | 0 | 3 | 0 | no |
| Floresta | anexo | 0 | 2 | 0 | no |
| Parque Patricios | anexo | 0 | 3 | 0 | no |
| Bajo Belgrano | no incluir | 0 | 1 | 1 | no |
| Av. Boedo | no incluir | 0 | 0 | 2 | no |
| Federico Lacroze | no incluir | 0 | 0 | 2 | **sí (PX023A/B)** |
| Villa Pueyrredón | no incluir | 0 | 1 | 1 | no |

Detalle de fuentes principales por polo: `fuentes_externas_polos_gastro.csv` y cada ficha.

---

## 4. Qué polos están bien documentados

Criterio de `estado_documentacion` (reproducible): **fuerte** = ≥2 fuentes de confiabilidad alta;
**media** = 1 alta o ≥2 media; **débil** = poca evidencia media sin respaldo alto; **pendiente**
= URL pendiente sin fuente verificable o evidencia insuficiente.

**Documentación fuerte (5)** — listos para informe sin reservas mayores:
- Palermo Soho, Palermo Hollywood, San Telmo, Recoleta, Barrio Chino.

**Documentación media (sólida, presentables) (15)** — usables con redacción prudente:
- Las Cañitas, Puerto Madero, Chacarita, Microcentro/Centro, Monserrat, Retiro, Villa Crespo,
  Caballito, Costanera Norte, Devoto, DoHo/Donado-Holmberg, Villa Urquiza, Colegiales,
  Av. Caseros/Barracas, Abasto, Flores, Floresta, Parque Patricios, Nuevo Bajo en Retiro.

> Los núcleos y relevantes están todos en **fuerte** o **media**: el cuerpo del informe es
> defendible.

---

## 5. Qué polos necesitan más evidencia

**Débiles o pendientes (necesitan refuerzo antes de darles más peso):**

| Polo | Grupo | Problema principal |
| --- | --- | --- |
| Av. Corrientes | emergente | Solo 1 fuente media + 2 `requiere_revision_url` (clarín no abrió). Identidad cultural fuerte, evidencia gastronómica fina débil. |
| Paternal | emergente | URL pendiente (PX025A); solo contexto Distrito del Vino. Sin fuente específica del circuito. |
| García del Río | anexo | URL pendiente (PX024B); fuente periodística no verificable (clarín). |
| Federico Lacroze | no incluir | URLs pendientes (PX023A/B); sin fuente verificable. |
| Av. Boedo | no incluir | Solo fuentes culturales/históricas; sin corredor gastronómico documentado. |
| Bajo Belgrano | no incluir | Mención indirecta dentro de Belgrano; sin fuente propia. |
| Villa Pueyrredón | no incluir | Hito puntual (La Nueva Andaluza); sin corredor validado. |
| Belgrano R | anexo | Señal barrial, sin polo delimitado. |

Detalle y plan de refuerzo: `FASE_5_POLOS_A_DOCUMENTAR.md`.

---

## 6. Qué mapas sirven

**Sirven como base territorial real (Fase 4A):**
- `mapa_estatico_caba_polos_gastro_v1.png` — CABA con barrios oficiales, núcleo + relevantes +
  candidatos. Territorial real.
- `mapa_estatico_caba_polos_gastro_nucleo_v1.png` — versión limpia (núcleo + relevantes),
  candidata al cuerpo del informe.

**Insumo cartográfico disponible:** `barrios_caba.geojson` + `comunas_caba.geojson` +
`base_delimitacion_preliminar_polos_gastro.csv` (barrio/comuna por polo). Con esto se pueden
generar mapas territoriales nuevos y mejores (Fase 5, Tarea 6) sin inventar delimitaciones.

> **Decisión metodológica vigente:** barrios/comunas son **referencia territorial, no
> delimitación oficial de polos**. Sin polígonos de polos, sin coordenadas Google en mapas
> públicos, sin geocodificar locales.

---

## 7. Qué mapas/gráficos quedan descartados como material principal

Por decisión de Diego (2026-06-30), **se conservan pero pasan a material experimental/interno**
(no borrar, no usar como base principal del informe):

- **Mapas conceptuales tipo red/diagrama** — `mapa_conceptual_polos_gastro*.png` (v1 y v2,
  resumido y completo). No convencen visualmente; el completo además es denso.
- **Gráficos de barras** — `universo_polos_por_grupo*.png`, `precision_delimitacion_polos*.png`,
  `familias_territoriales_polos*.png` (v1 y v2). Decorativos / poco aportan lectura territorial.

Detalle del criterio (cuáles usar, cuáles dejar como interno): `FASE_5_CRITERIO_USO_VISUALES.md`.

> Excepción: si en Fase 5 se encuentra una forma **mucho mejor** de representar esa información
> (p. ej. una tabla limpia o un mapa que reemplace al gráfico), se podrá reconsiderar caso a caso.

---

## 8. Qué falta antes de armar un borrador de informe

1. **Reforzar polos débiles/pendientes** (§5) con las fuentes ya disponibles en el repo;
   listar búsquedas web sugeridas para los que no se puedan cerrar sin autorización.
   → `FASE_5_POLOS_A_DOCUMENTAR.md`.
2. **Consolidar el universo en una sola tabla legible** con estado de documentación y
   recomendación de uso. → `polos_gastro_universo_consolidado_fase5.csv`.
3. **Fichas por polo** homogéneas y actualizadas (formato corto, sin inventar).
   → `fase5/fichas_polos/`.
4. **Mapas territoriales útiles** (universo por grupo, núcleos, relevantes+emergentes, anexo,
   revisión) sobre cartografía oficial. → `fase5/mapas/`.
5. **Cerrar/asumir las 3 URLs pendientes** (Federico Lacroze, García del Río, Paternal) y las
   `requiere_revision_url` de clarín — ninguna bloquea, pero deben quedar como nota.
6. **Decidir Google Places**: mantener como validación experimental interna, **no** fuente
   pública principal (regla vigente).
7. Recién con lo anterior cerrado y revisado: redactar el **primer borrador en Markdown**
   (sin PDF) según `PLAN_ENSAMBLADO_INFORME_POLOS_GASTRO.md`.

> Esta fase (Fase 5) produce material de trabajo. **No genera PDF, ni mapa final oficial, ni
> outputs públicos definitivos.**
