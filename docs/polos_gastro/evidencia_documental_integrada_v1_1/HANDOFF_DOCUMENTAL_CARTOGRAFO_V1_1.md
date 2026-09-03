# HANDOFF DOCUMENTAL → CARTÓGRAFO TERRITORIAL — V1.1

**De:** `investigador_documental` (skill `auditar_evidencia_documental`, V1.1/V1.1.1)
**Para:** agente `cartografo_territorial` / Codex (corrida espacial)
**Fecha:** 2026-07-11
**Ámbito:** Belgrano, Recoleta, Costanera Norte
**Estado:** evidencia documental integrada; **apta para contraste espacial: SÍ** (los tres polos)

---

## 1. Propósito

Entregar la evidencia documental depurada para que la próxima corrida espacial
(clustering, densidades, geometrías) se ejecute **sin supervisión documental** y el
contraste con nombres y componentes se haga **post hoc**. Este handoff no crea
geometrías ni mapas.

## 2. Decisiones humanas cerradas (no reabrir)

1. **Belgrano:** un único Polo Gastronómico Belgrano. Estructura interna a contrastar:
   centralidad principal (Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría), eje
   Cabildo–Juramento, subpolo Bajo Belgrano, sector secundario Belgrano R (subpolo solo
   con respaldo espacial). No son cuatro polígonos equivalentes.
2. **Recoleta:** un único Polo Gastronómico Recoleta; no nueve polos. Comparar: unidad
   con centralidades internas vs. unidad con máximo dos subzonas. Callao–9 de Julio y
   Bellas Artes = referencias/transiciones.
3. **Costanera Norte:** un único Polo Gastronómico Costanera Norte, **polo adoptado**
   de cuatro componentes discontinuos, **incluido `CN_C02`** (DEC-10). Vacíos
   estructurales se preservan y no se dibujan conectores artificiales (DEC-05). La
   delimitación es una definición territorial adoptada por el estudio, actualizable con
   nueva evidencia; no se presenta como límite administrativo oficial. La **cartografía
   debe estar preparada para el cuerpo principal del informe**; la debilidad de fuente
   (dependencia de Places) se documenta metodológicamente una sola vez.
4. **REC-R02 rechazada:** ~150 restaurantes = San Telmo. No usar para Recoleta.
5. Transversales: nombres comerciales no institucionales; nombres post hoc; el híbrido
   complementa Fase 25 (DEC-07); taxonomía de 6 categorías para no asignados (DEC-08);
   buffers como convención orientativa con nota estándar (DEC-09); nombres de núcleos de
   Belgrano diferidos (DH-05, tras DEC-04).

## 3. Estructuras territoriales a probar

### Belgrano

- Unidad macro defendible (sin hull gigante injustificado).
- Continuidad entre centralidades: ¿Barrio Chino–Barrancas–Pasaje es un cuerpo o nodos
  contiguos? ¿Cabildo–Juramento continúa el núcleo o es eje aparte?
- Subestructuras internas: separación (o no) de Bajo Belgrano; Belgrano R concentración
  vs. dispersión.
- **No forzar cuatro clusters iguales.** Nombrar solo después del análisis y del test de
  correspondencia post hoc (BEL-R14 / DEC-04).

### Recoleta

- Reducir los **9 núcleos técnicos** (HDBSCAN v2.1) a una lectura defendible.
- Comparar **unidad única vs. máximo dos subzonas**; reportar cuál sostiene mejor la
  evidencia espacial.
- Evitar: nueve polígonos independientes; y una gran envolvente que una vacíos sin
  respaldo.
- Callao–9 de Julio = transición salvo evidencia espacial contraria (si aparece, se
  reporta como desacuerdo; la promoción la decide Diego).

### Costanera Norte

- Mantener **cuatro componentes**, incluido `CN_C02`; sin conectores/bandas/buffers que
  sugieran continuidad.
- Preservar vacíos territoriales (Aeroparque, parques, clubes, predios, tramos sin
  frentes) como parte del resultado.
- Contrastar cada geometría `CN_C01–CN_C04` con los 4 componentes documentales y
  clasificar: `EMPAREJADA` | `PARCIAL` | `SIN_CORRESPONDENCIA_DOCUMENTAL_DIRECTA`.
- **La falta de correspondencia perfecta no elimina el componente.**

## 4. Nombres

**Autorizados (post hoc, desde `matriz_territorial_documental.csv` de Grok):**
Polo Gastronómico Belgrano; Barrio Chino de Belgrano / entorno Belgrano C–Barrancas–
Pasaje Echeverría; Cabildo–Juramento (eje); Bajo Belgrano; Belgrano R ·
Polo Gastronómico Recoleta; centralidad patrimonial-comercial Junín–Vicente López;
corredor patrimonial-hotelero Alvear–Posadas ·
Polo Gastronómico Costanera Norte; corredor de concesiones ribereñas (Distrito Joven);
franja de puestos y carritos de parrilla; patio gastronómico de puestos en containers;
predios de eventos y usos mixtos Costa Salguero–Punta Carrasco.

**Alternativos (referencia interna):** Belgrano C; Barrancas de Belgrano; Pasaje
Echeverría; Vía Viva; entorno Sucre; Recoleta Urban Mall; Cementerio/Plaza Francia;
Patio Bullrich; Bellas Artes/Facultad de Derecho; Callao–9 de Julio; Distrito Joven
(marco legal); Sector 1; Aeroparque; Costa Salguero; Punta Carrasco.

**Evitar:** Libertador gastronómico; Polo del Bajo; Polo Recoleta Norte; nueve "polos" de
Recoleta; marcas comerciales como nombres de unidad (Recoleta Urban Mall, Bellas Artes
Bar, Jano's, etc.); fusionar Costanera Norte con Sur; "150 restaurantes en Recoleta";
"locales activos" si la fuente mide otra cosa; "informal/ilegal" como etiqueta.
Si un cluster no empareja: nombre técnico (`cluster_03`, `componente_sin_nombre`).

## 5. Evidencia documental principal

- Matriz integrada: `MATRIZ_EVIDENCIA_DOCUMENTAL_INTEGRADA.csv` (54 filas: 42 evidencias
  BEL-E01–E14 / REC-R01–R12 / CN-01–16 + inferencias + decisiones).
- Bibliografía: `BIBLIOGRAFIA_DOCUMENTAL_VERIFICADA.csv` (33 fuentes deduplicadas, con
  estado de acceso y carácter; estados según auditoría Grok 2026-07-11).
- Anclas más fuertes: Turismo BA (REC-R01, CN-01, CN-02); Ley 5.961 (CN-04/05/06);
  La Nación 2023 y Clarín 2023 para Barrio Chino (BEL-E04/E07); Clarín 2026 para
  Sector 1 (CN-11/12).
- Advertencias: REC-R03/R04/R05/R12 son branded (Content LAB); REC-R06/R07/R11 son de
  2011; BEL-E10 es débil para Cabildo–Juramento.

## 6. Referencias espaciales (del pipeline híbrido v2.1 — solo lectura)

- Belgrano: repetición autorizada (DEC-04); shortlist previa `BEL_RV2_N02/N03/N05/N06`.
- Recoleta: 9 núcleos HDBSCAN; cobertura 78,23 %; robustez media 0,626; 47,33 % Places.
- Costanera: universo 72; `CN_C01` 21 / `CN_C02` 11 / `CN_C03` 29 / `CN_C04` 10; 1 punto
  ruido de borde; `CN_C02` 100 % Places; bootstrap por bloques 0,77.

## 7. Desacuerdos y vacíos a tener presentes

- T-INT-04: no emparejar "4 núcleos técnicos ↔ 4 referencias documentales" de Belgrano
  por el número; probar correspondencia real.
- Vacíos documentales: polígono de Bajo Belgrano; nodo Junín–Vicente López sin fuente
  independiente reciente; corredor Alvear–Posadas sin actualización post-2011;
  censo de carritos inexistente. Detalle: `CONTRADICCIONES_Y_VACIOS_DOCUMENTALES.md`.

## 8. Contraste post hoc — instrucciones

1. Calcular geometrías **sin** nombres ni fichas documentales como input.
2. Después, emparejar con la tabla estándar (campos de
   `INSTRUCCIONES_ALGORITMO_CONTRASTE_ESPACIAL.md` §3 del paquete Grok):
   `polo, unidad_documental, geometria_id, estado_emparejamiento, evidencia_espacial,
   evidencia_documental, accion_editorial`.
   Para Costanera usar los tres estados del §3 de este handoff.
3. Desacuerdos → completar la tabla del §6 de `CONTRADICCIONES_Y_VACIOS_DOCUMENTALES.md`;
   nunca borrar la decisión de trabajo.
4. Documentar parámetros (clustering, buffers, umbrales) y declarar los buffers como
   convención orientativa (DEC-09).

## 9. Qué NO debe entrar como restricción supervisada del algoritmo

- Nombres documentales (Barrio Chino, Junín–Vicente López, Distrito Joven, etc.) como
  labels o features.
- Cantidades esperadas de clusters (4 en Belgrano, 2 en Recoleta, 4 en Costanera) como
  parámetro forzado — son hipótesis a contrastar, no objetivos.
- Fichas documentales como semillas espaciales.
- La decisión "CN_C02 es componente" como razón para alterar el clustering: es una
  decisión de **presentación editorial**, no de cálculo.

## 10. Archivos de entrada para el cartógrafo

```text
docs/polos_gastro/evidencia_documental_integrada_v1_1/ (esta línea completa; V1 queda como antecedente)
docs/polos_gastro/evidencia_documental/                (paquete Grok original, solo lectura)
docs/polos_gastro/experimentos/pipeline_hibrido_integracion_v21/  (diagnósticos, solo lectura)
docs/polos_gastro/experimentos/consolidacion_editorial_pre_informes_v1/REGISTRO_DECISIONES_APROBADAS_DIEGO.md
docs/polos_gastro/PROTECTED_SURFACES.yaml              (verificar antes de escribir)
```

Datos espaciales: los universos de puntos y geometrías de las carpetas de Codex
(`pipeline_hibrido_repeticiones_v2/`, cerradas como baseline de lectura). Derivar en
línea paralela nueva; no editar in-place.

## 11. Outputs esperados del cartógrafo

1. `emparejamiento_documental_espacial.csv` (tabla del §8.2) para los tres polos.
2. Nota breve de desacuerdos (MD) + tabla §6 de contradicciones completada.
3. Parámetros del clustering/buffers/umbrales usados.
4. Geometrías de trabajo en carpeta experimental nueva (sin tocar baselines).
5. Confirmación de: datos fuente intactos; sin nombres como labels; Recoleta ≤2 subzonas
   nombradas; Costanera 4 componentes + vacíos; Belgrano sin fragmentación forzada.

## 12. Decisiones que requerirían volver a Diego

- Fusionar/eliminar un polo; promover Belgrano R; tercera subzona o promoción de
  Callao–9 de Julio en Recoleta; publicar cifra de oferta para Recoleta; nombrar
  núcleos de Belgrano (DH-05).
- Costanera Norte: **solo** si el análisis propone eliminar, fusionar o alterar los
  cuatro componentes (incluida la exclusión de `CN_C02`). **No** volver a Diego para
  confirmar nuevamente la existencia o la jerarquía del polo: está adoptado (DEC-10).
- Cualquier `desacuerdo` espacial-documental que implique cambiar una decisión cerrada.

## 13. Restricciones operativas de la corrida

Sin consultas a Google Places ni APIs pagas (0 autorizadas); sin scraping; sin datos
nuevos; sin tocar pipeline F01–F05, `data/processed/`, `data/analytics/`, PDFs oficiales
ni superficies protegidas; trabajo en carpetas experimentales nuevas; sin commit/push
salvo pedido de Diego.
