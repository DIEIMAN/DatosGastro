# Propuesta: contenido editable para informes DataGastro

**Estado:** propuesta. No aplicar todavía a todos los proyectos.
**Origen:** piloto en el informe Cafecito (junio 2026).
**Alcance de esta propuesta:** documentar un estándar futuro. La aplicación a
otros proyectos (PolosGastro, MercadosGastro, CasasDePastas, DataGastro V2…)
queda fuera de scope hasta una decisión explícita.

---

## 1. Problema que resuelve

Hoy varios informes se generan con un único script Python donde conviven, en el
mismo archivo:

- el **contenido narrativo** (títulos, bajadas, notas, recomendaciones);
- los **datos calculados** (números que vienen de CSV/XLSX);
- el **layout** (posiciones, cajas, colores, tamaños);
- los **paths** y funciones auxiliares.

Eso hace que una corrección de redacción —que debería ser de un minuto— obligue a
editar código, con riesgo de romper el generador y sin que una persona no técnica
pueda intervenir.

---

## 2. Estándar propuesto

Separar cada informe en **capas con responsabilidades claras**:

```
docs/<proyecto>/contenido_editable_informe_<proyecto>.yaml   ← TEXTOS (editable)
scripts/<proyecto>/generar_informe_..._editable.py           ← GENERADOR (layout)
outputs/<proyecto>/*.csv  ·  *.png                           ← INSUMOS (datos/gráficos)
outputs/<proyecto>/INFORME_..._EDITABLE_TEST.pdf             ← VERSIÓN DE REVISIÓN
outputs/<proyecto>/INFORME_..._FINAL.pdf                     ← VERSIÓN FINAL (aprobada)
```

### 2.1 Contenido en YAML (o MD)

- Todo texto visible del PDF vive en un archivo editable, organizado **por página**.
- Los números se referencian con marcadores `{clave}` que el generador reemplaza
  desde los datos. **El YAML nunca contiene datos calculados "a mano".**
- El archivo lleva al inicio un comentario que explica qué se puede y qué no se
  puede tocar.

### 2.2 Generador separado

- El script de generación se ocupa **solo** del layout y de inyectar el contenido.
- **No mezcla** narrativa con diseño: los strings largos no van hardcodeados.
- Reutiliza (importa) las primitivas de dibujo y el cálculo de datos en lugar de
  duplicarlas, para que el editable y el final no diverjan.

### 2.3 CSV / PNG como insumos

- Datos (CSV) y gráficos (PNG/mapas) son **insumos** que el generador consume.
- Se generan en un paso de análisis reproducible, no se editan a mano.

### 2.4 QA público obligatorio

Antes de publicar, verificar que el PDF **no** contiene:

- rutas locales ni nombres de archivos;
- nombres de scripts ni extensiones (`.py`, `.csv`, `.xlsx`…);
- versiones internas visibles (V2, V3, V6…);
- hashes, IDs de servicios externos;
- datos personales (correos, teléfonos, CUIT/DNI, nombres, transacciones).

Y que **sí** contiene: marca DataGastro, advertencias metodológicas y la cantidad
de páginas esperada.

> Este QA puede automatizarse extrayendo el texto del PDF y corriendo una lista de
> patrones prohibidos (como se hizo en el piloto Cafecito).

### 2.5 Versión de revisión vs versión final

- La generación produce siempre una **versión de revisión** con sufijo
  `_EDITABLE_TEST` (o equivalente). Nunca pisa el final automáticamente.
- El paso "revisión → final" lo decide **una persona**, una sola vez, con los
  textos ya aprobados.

---

## 3. Reglas duras del estándar

1. **No mezclar contenido con layout.** Los textos en su archivo; el diseño en el
   script.
2. **No editar PDFs a mano.** Todo cambio nace en el YAML/MD o en los datos y se
   regenera.
3. **No meter rutas técnicas en PDFs públicos.** Ni paths, ni scripts, ni versiones
   internas.
4. **No inventar ni hardcodear datos** en la capa editable. Los números vienen de
   los insumos vía marcadores `{...}`.
5. **No sobrescribir el final sin aprobación.** La revisión vive en un archivo
   aparte.
6. **Reutilizar, no duplicar** el motor de cálculo y dibujo entre el generador
   final y el editable.

---

## 4. Compatibilidad con los guardrails DataGastro

Esta propuesta es coherente con los guardrails del proyecto:

- No toca el pipeline F01–F05 ni los datos fuente.
- Refuerza la **no exposición de datos sensibles** mediante el QA público.
- Mantiene la **separación de universos** y la prudencia metodológica (no convierte
  registros parciales en afirmaciones de "actividad").
- No requiere scraping ni servicios externos.

---

## 5. Próximos pasos sugeridos (no ejecutar aún)

1. Validar el piloto Cafecito con jefatura.
2. Definir una convención de nombres común para los archivos editables.
3. Extraer el QA público a una función/script reutilizable.
4. Recién entonces, evaluar caso por caso aplicarlo a otros informes, **sin**
   rehacer los informes ya aprobados.

---

## 6. Referencia: piloto Cafecito

Implementación de referencia (junio 2026):

- Contenido editable: `docs/cafecito/contenido_editable_informe_cafecito.yaml`
- Generador editable: `scripts/cafecito/generar_informe_datagastro_final_editable.py`
- Guía de edición: `docs/cafecito/COMO_EDITAR_INFORME_CAFECITO.md`

El piloto demostró equivalencia con el informe final (mismas 12 páginas, mismos
datos y gráficos, misma marca y advertencias) sin tocar el PDF final original.
