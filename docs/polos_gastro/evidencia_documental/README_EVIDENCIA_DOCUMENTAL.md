# Evidencia documental — polos gastronómicos (Belgrano, Recoleta, Costanera Norte)

Paquete de handoff para integrar investigación documental verificable al repositorio de análisis territorial de polos gastronómicos de CABA.

**Fecha de consolidación:** 2026-07-11  
**Alcance:** tres polos prioritarios con definición de trabajo adoptada  
**Uso principal:** contraste con geometrías técnicas (Claude Code / Codex / pipeline espacial)

## Qué es y qué no es

| Es | No es |
|---|---|
| Documentación urbana y periodística trazable | Delimitación oficial municipal inmutable |
| Definiciones de trabajo defendibles y actualizables | Hipótesis eternamente abiertas sin decisión |
| Insumo para interpretar resultados espaciales | Etiqueta supervisada del clustering |
| Matriz de evidencia con URLs completas | Inventario de locales ni censo de oferta |

## Decisiones institucionales (cerradas)

1. **Belgrano:** polo general con centralidad principal Barrio Chino–Belgrano C–Barrancas–Pasaje Echeverría; eje Cabildo–Juramento; subpolo Bajo Belgrano; Belgrano R secundario o eventual subpolo según contraste espacial.
2. **Recoleta:** polo general; **no** nueve polos; **máximo dos** subzonas internas (centralidad patrimonial-comercial; corredor patrimonial-hotelero).
3. **Costanera Norte:** un solo polo multiparte; **cuatro componentes discontinuos** se incorporan; los vacíos son parte de la estructura; diferencias admin vs. territorial se explican metodológicamente.

## Archivos del paquete

| Archivo | Función |
|---|---|
| `HANDOFF_EVIDENCIA_DOCUMENTAL_CODEX_CLAUDE.md` | Handoff operativo completo para agentes |
| `belgrano_investigacion_documental.md` | Síntesis Belgrano + auditoría de fuentes |
| `recoleta_investigacion_documental.md` | Síntesis Recoleta + auditoría de fuentes |
| `costanera_norte_investigacion_documental.md` | Síntesis Costanera Norte multiparte |
| `matriz_evidencia_documental_polos.csv` | Filas de evidencia trazables |
| `bibliografia_verificada_polos.csv` | Fuentes con estado de acceso |
| `matriz_territorial_documental.csv` | Unidades territoriales y jerarquías |
| `textos_institucionales_documentales.md` | Textos políticos, metodológicos y cartográficos |
| `INSTRUCCIONES_ALGORITMO_CONTRASTE_ESPACIAL.md` | Reglas para clustering / geometrías |

## Cómo usarlo (orden recomendado)

1. Leer `HANDOFF_EVIDENCIA_DOCUMENTAL_CODEX_CLAUDE.md`.
2. Cargar CSVs de evidencia, bibliografía y matriz territorial.
3. Aplicar `INSTRUCCIONES_ALGORITMO_CONTRASTE_ESPACIAL.md` al contrastar geometrías.
4. Tomar textos de `textos_institucionales_documentales.md` solo tras contraste espacial (ajustar si hay desacuerdo documentado).
5. No modificar datos fuente ni inventar URLs.

## Universos de fuentes (DataGastro)

| Prefijo / tipo | Uso en este paquete |
|---|---|
| Públicas / institucionales (Turismo BA, BO CABA, GCBA) | Evidencia de marco y denominación |
| Periodísticas reconocidas | Delimitación orientativa, caracterización, historia |
| Divulgación gastronómica / lifestyle | Caracterización secundaria |
| Plataformas de localización / reseñas | Solo presencia o uso social auxiliar; no delimitación principal |

## Reglas editoriales mínimas

- Mantener URLs completas en texto plano.
- No inventar fuentes ni completar URLs por intuición.
- No usar nombres comerciales como nombres institucionales de subpolos.
- Separar **evidencia documental**, **decisión institucional** e **inferencia metodológica**.
- No debilitar repetidamente decisiones ya adoptadas.
- Marcar paywall, no verificado y contenido no coincidente.
- No dibujar límites solo a partir de prensa.

## Relación con el resto del proyecto

- Universo de polos y fases previas: `docs/polos_gastro/`.
- Outputs espaciales y experimentos: `outputs/polos_gastro/`.
- Este directorio **no** regenera el pipeline F01–F05 ni modifica `data/processed` o `data/analytics`.

## Mantenimiento

Al actualizar una fuente o una decisión territorial:

1. Actualizar la fila en `matriz_evidencia_documental_polos.csv` o `bibliografia_verificada_polos.csv`.
2. Ajustar la ficha del polo correspondiente.
3. Registrar el cambio en el handoff (sección “decisiones” o “contradicciones”).
4. No reescribir textos institucionales sin revisar el contraste espacial vigente.
