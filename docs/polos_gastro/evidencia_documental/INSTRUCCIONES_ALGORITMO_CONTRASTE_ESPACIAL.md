# Instrucciones para el algoritmo / contraste espacial

**Ámbito:** Belgrano, Recoleta, Costanera Norte  
**Insumos documentales:** este directorio (`docs/polos_gastro/evidencia_documental/`)  
**Fecha:** 2026-07-11

Estas reglas rigen cualquier pipeline de clustering, densidades, polígonos o emparejamiento con geometrías técnicas. Leelas **antes** de correr o interpretar resultados.

---

## 1. Principio rector

Los nombres y subzonas de este paquete son **post hoc**: interpretan y comunican resultados territoriales. **No** son etiquetas de entrenamiento ni variables supervisadas del clustering.

```text
documentación  →  interpreta resultados
geometría       →  se calcula sin forzar nombres
desacuerdo      →  se reporta, no se oculta
```

---

## 2. Qué NO debe hacer el algoritmo

1. **No** usar nombres documentales (`Barrio Chino`, `Junín–Vicente López`, `Distrito Joven`, etc.) como labels supervisados del clustering.
2. **No** forzar que un cluster coincida con un nombre de la matriz territorial.
3. **No** exigir certeza absoluta ni polígonos “oficiales” inventados.
4. **No** dibujar límites **solo** a partir de prensa o de un titular (“4 cuadras”, “corredor hasta Retiro”).
5. **No** modificar datos fuente, padrones administrativos ni capas crudas.
6. **No** fusionar Costanera Norte con Costanera Sur.
7. **No** fragmentar Recoleta en nueve polos.
8. **No** elevar un pin de plataforma externa a “establecimiento habilitado”.
9. **No** afirmar informalidad o ilegalidad de un local concreto.
10. **No** reabrir decisiones de trabajo ya cerradas (existencia de los tres polos; 4 componentes CN; máx. 2 subzonas Recoleta) salvo pedido explícito del responsable del proyecto.

---

## 3. Qué SÍ debe hacer

1. Calcular densidades / clusters / polígonos con reglas espaciales transparentes y parámetros documentados.
2. **Después** del cálculo, contrastar con `matriz_territorial_documental.csv` y la evidencia del polo.
3. Producir una **tabla de emparejamiento**:

| campo | valores esperados |
|---|---|
| polo | Belgrano / Recoleta / Costanera Norte |
| unidad_documental | nombre_autorizado de la matriz territorial |
| geometria_id | id técnico del polígono/cluster |
| estado_emparejamiento | `emparejado` \| `parcial` \| `sin_par` \| `desacuerdo` |
| evidencia_espacial | métrica breve (densidad, n puntos, contigüidad) |
| evidencia_documental | evidencia_id o fuente_id |
| accion_editorial | `mantener_nombre` \| `aclarar` \| `no_nombrar` \| `revisar_jerarquia` |

4. Señalar **desacuerdos** entre evidencia espacial y documental en un archivo de salida legible (CSV o MD).
5. Respetar jerarquías: polo general > centralidad/subzona/componente > eje/nodo/referencia.
6. En Costanera Norte, **mapear vacíos** como parte del resultado (no “rellenar” continuidad).
7. En Belgrano, probar si Barrio Chino–Barrancas–Pasaje es **un cuerpo** o **nodos contiguos** sin inventar cortes.
8. En Recoleta, probar **como máximo dos** subzonas de alta intensidad; el resto va a nodo/transición.

---

## 4. Uso permitido de la documentación

| Uso | Permitido |
|---|---|
| Interpretar clusters ya calculados | Sí |
| Elegir nombre público post hoc | Sí, desde `nombre_autorizado` |
| Priorizar zonas a inspeccionar visualmente | Sí |
| Explicar subregistro admin (CN carritos) | Sí, con lenguaje cauteloso |
| Feature de clustering / label supervisado | **No** |
| Única prueba de un polígono | **No** |
| Sustituir validación espacial | **No** |

---

## 5. Decisiones de trabajo que el contraste debe respetar

### Belgrano

- Existe polo general.
- Centralidad principal documentada: Barrio Chino–Belgrano C–Barrancas–Pasaje.
- Cabildo–Juramento = eje (no subpolo cerrado por defecto).
- Bajo Belgrano = subpolo con aclaración.
- Belgrano R = secundario; subir jerarquía **solo** si el espacial lo respalda de forma clara.

### Recoleta

- Un solo polo.
- Máximo dos subzonas internas.
- No publicar “150 restaurantes” como dato de Recoleta desde Turismo BA.
- Callao–9 de Julio y Bellas Artes = no subzona formal por defecto.

### Costanera Norte

- Un solo polo.
- Cuatro componentes se incorporan (aunque el emparejamiento sea parcial).
- Vacíos estructurales se conservan en la narrativa y en el mapa.
- Diferencias admin vs. territorio se explican; no niegan el polo.

---

## 6. Criterios de emparejamiento (orientativos)

| estado | criterio |
|---|---|
| `emparejado` | Superposición espacial clara + respaldo documental de la misma unidad |
| `parcial` | Superposición incompleta, o unidad documental más amplia/estrecha que la geometría |
| `sin_par` | Geometría sin análogo documental, o ficha documental sin geometría |
| `desacuerdo` | Espacial y documental apuntan a estructuras incompatibles (p. ej. un solo cluster donde el doc espera dos, o continuidad donde se esperan vacíos) |

Ante `desacuerdo`: **no borrar** la decisión de trabajo del polo; documentar el hallazgo y proponer ajuste de **límites o jerarquía de subunidad**, no la eliminación del polo.

---

## 7. Nombres post hoc — protocolo

1. Partir de `nombre_autorizado` en `matriz_territorial_documental.csv`.
2. Si no hay emparejamiento, usar nombre genérico técnico (`cluster_03`, `componente_sin_nombre`) en capas de trabajo.
3. No inventar marcas (“Polo del Bajo”, “Recoleta Norte”).
4. No usar nombres comerciales de locales como nombre de unidad.
5. Registrar en observaciones la evidencia_id que justifica el nombre elegido.

---

## 8. Fuente externa auxiliar de localización

- Uso: **auxiliar** de presencia o densidad visible.
- No: prueba de habilitación, formalidad o tipología legal.
- En Costanera Norte: puede iluminar el componente de puestos/carritos subrepresentado en admin; reportar como **hipótesis tipológica**, no como ilegalidad.

---

## 9. Salidas mínimas esperadas del contraste

1. `emparejamiento_documental_espacial.csv` (o equivalente).
2. Nota breve de desacuerdos (MD).
3. Parámetros del clustering / buffer / umbrales usados.
4. Confirmación de que no se modificaron datos fuente.
5. (Opcional) ajuste de textos en `textos_institucionales_documentales.md` **solo** en frases de límites o nota cartográfica, con diff trazable.

---

## 10. Checklist pre-ejecución

- [ ] Leí `HANDOFF_EVIDENCIA_DOCUMENTAL_CODEX_CLAUDE.md`
- [ ] Cargué los tres CSV de este directorio
- [ ] Confirmé que el clustering no recibe labels documentales
- [ ] Separé capas: admin / pública / externa auxiliar / documental
- [ ] Definí métricas de emparejamiento antes de mirar nombres
- [ ] Preparé carpeta de salida sin sobrescribir fuentes

## 11. Checklist post-ejecución

- [ ] Tabla de emparejamiento completa para los tres polos
- [ ] Desacuerdos listados sin forzar nombres
- [ ] Costanera Norte: cuatro componentes + vacíos tratados
- [ ] Recoleta: ≤2 subzonas nombradas
- [ ] Belgrano: centralidad principal no fragmentada sin corte espacial
- [ ] Ninguna URL inventada; ningún “link” opaco
- [ ] Ninguna afirmación de ilegalidad individual
- [ ] Pipeline F01–F05 y datos crudos intactos
