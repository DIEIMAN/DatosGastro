# Cómo editar el informe Cafecito (DataGastro)

Esta guía explica cómo **corregir los textos** del informe Cafecito sin tocar el
código que arma el PDF, y sin pisar el informe final que ya está aprobado.

La idea es simple: los textos viven en un archivo aparte. Vos editás ese archivo,
volvés a generar el PDF de prueba, lo revisás y recién después se decide pasarlo
a final.

---

## 1. Qué archivo editar para cambiar textos

Editá **solo** este archivo:

```
docs/cafecito/contenido_editable_informe_cafecito.yaml
```

Ahí están todos los textos visibles del informe, organizados por página:

- portada (título, subtítulo, bajada, advertencia);
- resumen ejecutivo (KPIs, "qué sabemos", recomendaciones…);
- perfil de la muestra;
- lectura territorial;
- red de cafeterías;
- público y red;
- canales de llegada;
- fidelización;
- motivaciones e intereses futuros;
- conclusiones y recomendaciones;
- anexo metodológico y privacidad;
- footer (pie de página) y la nota de la red territorial.

**Para cambiar un texto:** buscá la frase, editá lo que está **entre comillas**
o el ítem de la lista (las líneas que empiezan con `- `), guardá y listo.

Ejemplo. Si dice:

```yaml
    subtitulo: "Lectura de público, territorio y red de cafeterías vinculadas"
```

podés cambiarlo a:

```yaml
    subtitulo: "Lectura de público y red de cafeterías de la Ciudad"
```

---

## 2. Qué NO editar

Dentro del YAML, **no toques**:

- **Los nombres de las claves** (lo que está antes de los dos puntos `:`).
  Por ejemplo `subtitulo:`, `titulo:`, `que_sabemos:`. Si los cambiás, el
  generador no encuentra el texto y falla.
- **La indentación** (los espacios al principio de cada línea). El YAML usa los
  espacios para entender la estructura. No los borres ni agregues al azar.
- **Los marcadores entre llaves** como `{instagram}`, `{caba}`, `{contact_yes}`.
  Son **números calculados** automáticamente desde los datos. El generador los
  reemplaza por el número real (por ejemplo `{instagram}` → `45`). Si los borrás,
  el número desaparece del PDF. Podés moverlos dentro de la frase, pero conservá
  el nombre exacto entre llaves.

Y **fuera del YAML**, no edites a mano:

- el script `scripts/cafecito/generar_informe_datagastro_final_editable.py`;
- el generador final `scripts/cafecito/generar_informe_datagastro_final.py`;
- el PDF directamente (nunca se editan PDFs a mano);
- los datos fuente (XLSX, CSV).

---

## 3. Cómo regenerar el PDF

Desde la raíz del proyecto, en PowerShell:

```powershell
python scripts/cafecito/generar_informe_datagastro_final_editable.py
```

El script lee el YAML, usa los mismos datos y gráficos del informe final, y arma
un PDF nuevo de prueba. Al terminar imprime un resumen con la cantidad de páginas
y dónde quedó el archivo.

> Si Python no se encuentra, usar el del entorno del proyecto:
> ```powershell
> .venv\Scripts\python.exe scripts/cafecito/generar_informe_datagastro_final_editable.py
> ```

---

## 4. Dónde aparece el PDF generado

El PDF **de prueba** se guarda en dos lugares (mismo archivo):

```
outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_FINAL_EDITABLE_TEST.pdf
Cafesito/final/INFORME_CAFECITO_DATAGASTRO_FINAL_EDITABLE_TEST.pdf
```

El nombre lleva el sufijo `_EDITABLE_TEST` justamente para que **no se confunda**
con el informe final ni lo sobrescriba.

El informe final aprobado sigue intacto en:

```
outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_FINAL.pdf
Cafesito/final/INFORME_CAFECITO_DATAGASTRO_FINAL.pdf
```

El generador editable **nunca** toca esos archivos.

---

## 5. Cómo crear una versión de revisión sin pisar el final

El flujo normal ya hace esto: el PDF que generás siempre se llama
`..._EDITABLE_TEST.pdf`. Ese es tu archivo de revisión. Trabajá sobre él las veces
que necesites: editás el YAML, regenerás, mirás, volvés a editar.

Si querés guardar una copia con fecha para mandar a revisar y conservar el
historial, copiala a mano (sin pisar nada):

```powershell
Copy-Item outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_FINAL_EDITABLE_TEST.pdf `
          outputs/cafecito/INFORME_CAFECITO_REVISION_2026-06-30.pdf
```

El paso de "convertir el test en el nuevo final" **no es automático**: lo decide
una persona, una vez aprobados los textos. No sobrescribas el final por tu cuenta.

---

## 6. Qué revisar antes de enviar

Abrí el PDF de prueba y verificá:

- [ ] El texto que cambiaste se ve bien y **entra en su caja** (si es muy largo,
      puede cortarse; acortá la frase).
- [ ] Los números siguen apareciendo donde tienen que aparecer (no quedó ningún
      `{algo}` sin reemplazar).
- [ ] Sigue diciendo **DataGastro** como marca.
- [ ] Siguen estando las **advertencias metodológicas** (muestra exploratoria,
      no representativa, datos agregados).
- [ ] **No** aparecen: rutas de archivos, nombres de scripts, versiones internas
      (V3, V6…), correos, teléfonos, ni datos personales.
- [ ] Sigue teniendo **12 páginas**.

---

## 7. Qué hacer si el cambio afecta datos o gráficos

El archivo editable es **solo para textos**. Si lo que querés cambiar es:

- un **número** (que viene de los datos),
- un **gráfico** o **mapa**,
- una **categoría** del análisis,

eso **no se toca en el YAML**. Esos valores se calculan desde el XLSX y los CSV.
En ese caso, frená y avisá a quien mantiene el pipeline de Cafecito: hay que
revisar los datos o el script de análisis, no el texto. No inventes ni edites
números a mano en el YAML para "forzar" un resultado: el marcador `{...}` los
sobrescribe en cada generación de todos modos.

---

## Resumen de un vistazo

| Quiero cambiar…                | ¿Dónde?                                          |
|--------------------------------|--------------------------------------------------|
| Un título / bajada / texto     | `contenido_editable_informe_cafecito.yaml`       |
| Una recomendación o nota       | mismo YAML                                        |
| El footer                      | mismo YAML (`footer:`)                           |
| Un número                      | No se edita: viene de los datos                  |
| Un gráfico o mapa              | No se edita acá: avisar al pipeline              |
| El diseño / colores / layout   | No se edita acá: avisar al pipeline              |

---

## Versión REVISIÓN 1 (informe de resultados de encuesta)

A partir de comentarios de una revisión, existe además una **versión revisada**
del informe, reorientada como **informe de resultados de encuesta**: pone el foco
en los datos duros, las preguntas del formulario, los porcentajes y la
descripción de resultados, con síntesis y recomendaciones en potencial. Cambia la
estructura (suma índice, datos generales con franjas horarias y una sección de
preguntas) y lleva la red de cafeterías a un anexo.

Esta versión es **independiente** del informe final y del editable test: tiene su
propio archivo de textos, su propio script y su propio PDF. No pisa a los otros.

### Qué archivo editar

Para corregir textos de la versión revisada, editá:

```text
docs/cafecito/contenido_editable_informe_cafecito_revision_1.yaml
```

Valen las mismas reglas de siempre: editá lo que está entre comillas y los ítems
de lista; **no toques** las claves, la indentación ni los marcadores `{...}`
(porcentajes y datos calculados).

> En esta versión los datos institucionales del evento (área que presenta, lugar,
> fechas, horarios) también están en el YAML, en las secciones `institucion` y
> `evento`. El área figura como **DGDGAS – Dirección General de Desarrollo Gastronómico**; si
> se confirma otra redacción oficial, se cambia ahí.

### Cómo regenerar el PDF de revisión

```powershell
python scripts/cafecito/generar_informe_datagastro_revision_1.py
```

Si Python no se encuentra, usar el del entorno:

```powershell
.venv\Scripts\python.exe scripts/cafecito/generar_informe_datagastro_revision_1.py
```

### Dónde aparece el PDF de revisión

```text
outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_REVISION_1.pdf
Cafesito/final/INFORME_CAFECITO_DATAGASTRO_REVISION_1.pdf
```

No sobrescribe el informe final (`..._FINAL.pdf`) ni el editable test
(`..._FINAL_EDITABLE_TEST.pdf`): son archivos distintos.

### Las versiones, de un vistazo

| Versión | Textos (YAML) | Script | PDF |
|---|---|---|---|
| Final (aprobado) | *(textos dentro del script)* | `generar_informe_datagastro_final.py` | `..._FINAL.pdf` |
| Editable test | `contenido_editable_informe_cafecito.yaml` | `generar_informe_datagastro_final_editable.py` | `..._FINAL_EDITABLE_TEST.pdf` |
| Revisión 1 | `contenido_editable_informe_cafecito_revision_1.yaml` | `generar_informe_datagastro_revision_1.py` | `..._REVISION_1.pdf` |
| Revisión 2 | `contenido_editable_informe_cafecito_revision_2.yaml` | `generar_informe_cafecito_revision_2.py` | `..._DGDGAS_REVISION_2.pdf` |

El paso de "revisión → nuevo final" no es automático: lo decide una persona una
vez aprobados los textos. No sobrescribas el final por tu cuenta.

---

## Versión REVISIÓN 2 (informe institucional DGDGAS)

La segunda revisión deja el informe **a nombre de DGDGAS** (ya no DataGastro) y
ajusta estructura y formato. Mantiene el enfoque de resultados de encuesta de la
revisión 1 y aplica:

- Marca **DGDGAS – Dirección General de Desarrollo Gastronómico** en todo el PDF público
  (portada, encabezados, footer, índice y notas). **No** dice "DataGastro".
- Portada limpia, sin información duplicada ni "Entrada libre y gratuita".
- **Índice con números de página** reales.
- Datos generales **sin** la nota de horario (se mantiene la tabla de franjas).
- **Preguntas del formulario en una sola página** compacta.
- Página de **perfil reordenada** (edad y género sin solapamientos).
- El **anexo** de red de cafeterías también dice DGDGAS, no DataGastro.

Esta versión es **independiente** del final, del editable test y de la revisión 1:
tiene su propio YAML, su propio script y su propio PDF. No pisa a los otros.

### Qué archivo editar

```text
docs/cafecito/contenido_editable_informe_cafecito_revision_2.yaml
```

Valen las mismas reglas: editá lo que está entre comillas y los ítems de lista;
**no toques** las claves, la indentación ni los marcadores `{...}`.

> Si cambia la cantidad de páginas, actualizá a mano los números de página en la
> sección `indice` del YAML (cada entrada tiene su `pagina`).

### Cómo regenerar el PDF de revisión 2

```powershell
python scripts/cafecito/generar_informe_cafecito_revision_2.py
```

Si Python no se encuentra, usar el del entorno:

```powershell
.venv\Scripts\python.exe scripts/cafecito/generar_informe_cafecito_revision_2.py
```

### Dónde aparece el PDF de revisión 2

```text
outputs/cafecito/INFORME_CAFECITO_DGDGAS_REVISION_2.pdf
Cafesito/final/INFORME_CAFECITO_DGDGAS_REVISION_2.pdf
```

No sobrescribe el final, el editable test ni la revisión 1: son archivos
distintos.
