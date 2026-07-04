# Fase 5 — Universo consolidado de polos (PolosGastro)

Fecha: 2026-06-30.
Tabla fuente: `outputs/polos_gastro/fase5/polos_gastro_universo_consolidado_fase5.csv` (32 polos).

Consolidación legible del universo, combinando `universo_informe_polos_gastro.csv`,
`base_delimitacion_preliminar_polos_gastro.csv` y `matriz_validacion_polos_gastro.csv`.
**No inventa datos.** Donde falta información queda `pendiente`. **No cambia la clasificación**
existente; solo la reúne y le agrega estado de documentación, recomendación de uso y prioridad
de revisión.

---

## 1. Cómo se construyó

- **`grupo_actual`** — copiado de `universo_informe_polos_gastro.csv` (sin cambios).
- **`estado_documentacion`** — derivado de la matriz de validación (reproducible):
  - **fuerte**: ≥2 fuentes de confiabilidad alta.
  - **media**: 1 fuente alta, o ≥2 fuentes media.
  - **débil**: evidencia media escasa sin respaldo alto.
  - **pendiente**: URL pendiente sin fuente verificable, o evidencia insuficiente.
- **`tipo_territorial`** — mapeado desde `tipo_area` (subpolo→polo puntual, avenida/circuito→
  corredor, zona_costera/central→zona, barrio→barrio).
- **`barrios_relacionados` / `comunas_relacionadas`** — de la base de delimitación.
- **`recomendacion_uso_informe`** — derivada de grupo + estado (núcleo→principal; relevante
  fuerte/media→principal; emergente→secundario; anexo→anexo; no incluir→afuera; pendiente→
  requiere revisión).
- **`prioridad_revision`** — alta si pendiente o URL pendiente; media si débil o emergente medio;
  baja en el resto.

---

## 2. Distribución resultante

**Por grupo (sin cambios respecto del universo vigente):**
núcleo 6 · zona relevante 5 · emergente/candidato 9 · anexo 8 · no incluir 4.

**Por estado de documentación:**
fuerte 6 · media 18 · débil 4 · pendiente 4.

**Por recomendación de uso en informe:**
incluir principal 11 · incluir secundario 9 · incluir anexo 8 · dejar afuera 4.

**Por prioridad de revisión:**
baja 17 · media 9 · alta 6.

---

## 3. Tabla consolidada (resumen)

| Polo | Grupo | Estado doc. | Tipo terr. | Barrios | Recom. uso | Prioridad |
| --- | --- | --- | --- | --- | --- | --- |
| Palermo Soho | núcleo principal | fuerte | polo puntual | Palermo | incluir principal | baja |
| Palermo Hollywood | núcleo principal | fuerte | polo puntual | Palermo | incluir principal | baja |
| Las Cañitas | núcleo principal | fuerte | polo puntual | Palermo | incluir principal | baja |
| Puerto Madero | núcleo principal | media | zona | Puerto Madero | incluir principal | baja |
| San Telmo | núcleo principal | fuerte | barrio | San Telmo | incluir principal | baja |
| Recoleta | núcleo principal | fuerte | barrio | Recoleta | incluir principal | baja |
| Chacarita | zona relevante | media | barrio | Chacarita | incluir principal | baja |
| Barrio Chino | zona relevante | fuerte | polo puntual | Belgrano | incluir principal | baja |
| Microcentro / Centro | zona relevante | media | zona | San Nicolás; Monserrat; Retiro | incluir principal | baja |
| Monserrat | zona relevante | media | barrio | Monserrat | incluir principal | baja |
| Retiro | zona relevante | media | barrio | Retiro | incluir principal | baja |
| Villa Crespo | emergente/candidato | media | barrio | Villa Crespo | incluir secundario | media |
| Caballito | emergente/candidato | media | barrio | Caballito | incluir secundario | media |
| Costanera Norte | emergente/candidato | media | zona | Recoleta; Palermo; Núñez/Belgrano | incluir secundario | media |
| Avenida Corrientes | emergente/candidato | débil | corredor | San Nicolás; Balvanera; Almagro | incluir secundario | media |
| Devoto | emergente/candidato | media | barrio | Villa Devoto | incluir secundario | media |
| DoHo / Donado-Holmberg | emergente/candidato | media | corredor | Villa Urquiza; borde Belgrano R | incluir secundario | media |
| Villa Urquiza | emergente/candidato | media | barrio | Villa Urquiza | incluir secundario | media |
| Paternal | emergente/candidato | débil | corredor | La Paternal | incluir secundario | **alta** |
| Colegiales | emergente/candidato | media | barrio | Colegiales | incluir secundario | media |
| Belgrano R | anexo | débil | barrio | Belgrano | incluir anexo | media |
| Avenida Caseros / Barracas | anexo | media | corredor | Barracas | incluir anexo | baja |
| Abasto | anexo | media | barrio | Balvanera | incluir anexo | baja |
| Nuevo Bajo en Retiro | anexo | media | polo puntual | Retiro | incluir anexo | baja |
| Parque Saavedra / García del Río | anexo | débil | barrio | Saavedra | incluir anexo | **alta** |
| Flores | anexo | media | barrio | Flores | incluir anexo | baja |
| Floresta | anexo | media | barrio | Floresta | incluir anexo | baja |
| Parque Patricios | anexo | media | barrio | Parque Patricios | incluir anexo | baja |
| Bajo Belgrano | no incluir | pendiente | polo puntual | Belgrano | dejar afuera | alta |
| Avenida Boedo | no incluir | pendiente | corredor | Boedo | dejar afuera | alta |
| Federico Lacroze | no incluir | pendiente | corredor | Belgrano/Colegiales | dejar afuera | alta |
| Villa Pueyrredón / Av. San Martín | no incluir | pendiente | corredor | Villa Pueyrredón | dejar afuera | alta |

Columnas completas (evidencia_resumen, fuentes_cantidad, fuentes_principales, observaciones) en
el CSV.

---

## 4. Lectura

- **Cuerpo principal del informe (11 polos)**: los 6 núcleos + 5 zonas relevantes. Todos con
  documentación **fuerte** o **media**. Base sólida.
- **Secundarios (9 emergentes)**: incluibles con redacción prudente. Dos requieren atención —
  **Av. Corrientes** (débil) y **Paternal** (débil + URL pendiente).
- **Anexo (8)**: mención cualitativa con advertencia. **García del Río** es el más flojo
  (URL pendiente).
- **Fuera (4)**: documentación pendiente; se mencionan, si acaso, como casos no incluidos.

> Prioridad de refuerzo: los 6 de prioridad **alta** (Paternal, García del Río, Bajo Belgrano,
> Av. Boedo, Federico Lacroze, Villa Pueyrredón). Detalle en `FASE_5_POLOS_A_DOCUMENTAR.md`.

> Recordatorio metodológico: el universo es **lectura defendible, no padrón**. Barrios/comunas son
> referencia territorial, no delimitación oficial de polos. Ninguna fuente de
> concentración/identidad se convierte en "locales activos".
