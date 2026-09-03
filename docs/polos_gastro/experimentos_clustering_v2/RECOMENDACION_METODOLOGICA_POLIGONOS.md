# Recomendación metodológica — Polígonos exploratorios PolosGastro (v2)

**Fecha:** 2026-07-07 · **Carácter:** recomendación interna de trabajo, sujeta a decisión
humana. Nada de lo aquí descripto define límites oficiales.

## 1. ¿Conviene seguir con DBSCAN global?

**Sí, pero solo como diagnóstico exploratorio, no como capa de representación.** Sus dos
aportes probados: detectar concentraciones emergentes (subnúcleos de Palermo, San Telmo,
Villa Crespo) y delatar sedes mal geocodificadas (clusters con etiquetas de polos lejanos).
Sus límites son estructurales con este insumo: ruido 29–57 %, zonas enteras sin cluster y
sensibilidad fuerte a eps. Si se mantiene, usar la candidata **inclusiva (650/4)** como
referencia y la equilibrada (400/3) para comparar entre tandas.

## 2. ¿Conviene usar polígonos asistidos por subzona?

**Sí, como la salida de referencia técnica para revisión del informe.** Cubre las 14 zonas,
hereda la semántica editorial existente (no inventa zonas) y expone la calidad de cada grupo
(confianza por n, apartados excluidos, `extension_a_revisar`). Condición: los 3 polígonos
marcados dispersos (Chacarita, Caseros/Barracas, Costanera Norte) **no** se usan sin
depuración manual previa de sus puntos.

## 3. ¿Universo semilla de 106 o sumar otro universo?

Para esta línea de trabajo (contrastar delimitaciones editoriales), el universo semilla es el
correcto: es el que el informe conoce y cita. Pero está en su techo: ~7 puntos por polo no
alcanzan para densidad ni para corredores. Sumar puntos al universo semilla implicaría nueva
curaduría editorial (decisión humana, no técnica). La alternativa de más volumen es un
universo distinto en corrida separada (ver §4).

## 4. ¿Qué pasaría con el universo público F01–F05 (10.847 ubicaciones)?

Con ~100 veces más puntos, DBSCAN operaría en su régimen natural: eps menores (100–250 m),
min_samples mayores (10–30), ruido esperable mucho más bajo y capacidad real de detectar
corredores y subnúcleos. Sería el experimento técnicamente más sólido. Tres salvedades:

- **Qué mide:** oferta registrada/habilitaciones, no "locales activos" (guardrail 5). Las
  concentraciones resultantes serían de *registro administrativo*, con su propia lectura.
- **Cobertura y sesgo territorial:** la densidad de registro no es homogénea por comuna;
  habría que leer los clusters contra ese sesgo (ver skill de geodatos).
- **Es otra corrida:** input, parámetros, outputs y documentación propios, sin tocar el
  pipeline (los archivos de `data/processed/` se leen, no se regeneran).

## 5. Riesgos de mezclar universo semilla con F01–F05

**No mezclar automáticamente.** Riesgos concretos:
1. **Doble conteo:** un mismo local puede estar en ambos universos con coordenadas
   ligeramente distintas → densidad artificial.
2. **Sesgos incompatibles:** el semilla sobremuestrea polos editoriales; F01–F05 muestrea
   registro administrativo. Un cluster mixto no tendría interpretación limpia.
3. **Confusión de universos (guardrail 3):** los outputs dejarían de ser trazables a una
   fuente y una semántica; exactamente lo que la metodología de fuentes prohíbe.
4. **Riesgo comunicacional:** una capa mixta se leería como "el mapa de la gastronomía
   porteña", que ninguno de los dos universos respalda.
El único cruce legítimo es **a posteriori y visual**: superponer capas generadas por
separado, cada una con su etiqueta de fuente.

## 6. ¿Qué salida es más defendible para un informe institucional?

**La poligonización asistida por subzona**, con este encuadre: "áreas estimadas de
concentración construidas a partir de los locales semilla del informe, agrupados por las
zonas editoriales ya definidas; capa auxiliar que no constituye límites oficiales y requiere
revisión territorial". Es defendible porque cada polígono es trazable (zona → puntos → hull),
lleva atributos de calidad y no introduce zonas nuevas sin decisión humana. El DBSCAN, si se
muestra, va como anexo diagnóstico con su ruido explícito.

## 7. Qué revisar manualmente antes de usar en mapas

1. Los **10 puntos apartados** excluidos (lista en el QA v2): confirmar sede correcta o
   corregir la geolocalización en la revisión de Fase 11.
2. Los **3 polígonos `extension_a_revisar`**: decidir punto por punto qué locales definen
   realmente la zona (Chacarita es el caso más deformado).
3. **Abasto** (1 punto, confianza baja): decidir si se representa como buffer puntual o se
   absorbe visualmente en Corrientes, como ya sugiere su estatus editorial.
4. **Corredores** (Corrientes, Caseros/Barracas): validar si el hull convexo es aceptable o
   si conviene una cápsula sobre el eje vial (mejora propuesta, no implementada).
5. Cotejar los polígonos asistidos contra las **subzonas editoriales V4** antes de cualquier
   uso gráfico (superposición visual, sin modificar la capa editorial).

## Recomendación sintética

- **Informe actual:** referencia técnica = poligonización asistida por subzona (con
  depuración manual de los 3 grupos dispersos y de los 10 apartados).
- **DBSCAN:** se mantiene como diagnóstico exploratorio (candidata inclusiva 650/4).
- **Etapa futura:** experimento separado con F01–F05, sin mezcla automática con el universo
  semilla; cruce solo visual y documentado.
