# Plan de integración editorial V3 — informe político experimental

Estado: **PLAN / NO EJECUTADO**. Fecha: 2026-07-11.
Rol: `integrador_tecnico_editorial` (V1.1.1). Complementa (no reemplaza) el
`PLAN_INTEGRACION_HANDOFF_CODEX_V21.md` de la línea Fase 25 política.

Alcance: integración futura de los resultados territoriales V3 de **Belgrano, Recoleta y
Costanera Norte**. Los pendientes v2.1 previos (Corrientes, San Telmo, Puerto Madero, Palermo)
siguen en su cola propia y no bloquean ni son bloqueados por V3.

## 1. Destino por página (objetivo: 9–10 páginas)

| Página actual | Destino V3 |
|---|---|
| 1 Portada | **Conservar** (solo metadato `pdf_subject` al regenerar). |
| 2 Síntesis | **Actualización menor**: párrafo 4 y encuadre (TO-01, TO-02); sumar Recoleta. |
| 3 Mapa general | **Rediseño de asset y leyenda**; caja Lectura reescrita (TO-03). Estructura de página se conserva. |
| 4 Palermo | **Conservar** (PEN-04 fuera de alcance V3). |
| 5 Corrientes | **Conservar** (cola v2.1 propia). |
| 6 San Telmo / Puerto Madero | **Conservar**; retirar frase "en elaboración" si el asset v2.1 llega en la misma regeneración (TO-13). |
| 7 Belgrano y zonas en observación | **Rediseño**: pasa a "Polo Gastronómico Belgrano" con jerarquía interna; Recoleta sale de la caja de observación (TO-04..06). |
| 8 Costanera Norte | **Rediseño mayor sin cambiar de posición**: textos DEC-10 (TO-07..10) + mapa multiparte en la mitad inferior hoy vacía. No requiere página extra. |
| 9 Próximos pasos | **Actualización menor** (TO-11, TO-12). |
| 10 Nota metodológica | **Actualización menor**: párrafo único de dependencia de fuentes de Costanera (TO-14). |

## 2. Dónde vive Recoleta (decisión editorial pendiente — la firma Diego)

Recoleta hoy no tiene página. Alternativas, en orden de preferencia del integrador:

- **Opción A (recomendada, mantiene 10 páginas):** la página 7 se convierte en "Belgrano" pleno
  y se inserta una página nueva "Polo Gastronómico Recoleta" tras ella; para compensar, la
  página 9 (próximos pasos) se compacta y se fusiona con la caja "Relación con la lectura
  general" dentro de la página 10, que hoy tiene aire. Total: 10 páginas.
- **Opción B:** Recoleta comparte página con las zonas en observación restantes (media página
  mapa + media página lectura). Riesgo: diluye el estatus de polo único recién decidido.
- **Opción C:** pasar a 11 páginas. Solo si Diego lo aprueba; no hay hoy razón editorial fuerte.

No se decide aquí: se registra para decisión humana antes de la regeneración.

## 3. Mapas esperados de Codex (detalle en el contrato de outputs)

1. **Mapa general V3** (página 3): tres polos nuevos integrados + Costanera multiparte.
2. **Mapa Belgrano V3** (página 7): jerarquía interna de hasta 4 niveles.
3. **Mapa Recoleta V3** (página nueva/sección): polo único, máximo 2 subzonas.
4. **Mapa Costanera Norte V3** (página 8): 4 componentes discontinuos, vacíos preservados.

Codex **no** diseña páginas ni compone el informe: entrega capas, imágenes según plantilla,
métricas y QA. La composición queda en el generador propio de la línea política.

## 4. Textos que pueden prepararse ahora (sin esperar la corrida)

- Los tres paneles de Costanera con lenguaje DEC-10: la existencia, el estatus ("delimitación
  adoptada"), los 4 componentes y la explicación de vacíos **ya están decididos**; solo las
  geometrías y métricas esperan la corrida.
- El párrafo metodológico único de dependencia de fuentes (TO-14), con el valor numérico en
  blanco hasta el handoff.
- Título y bajada de "Polo Gastronómico Belgrano" y de "Polo Gastronómico Recoleta".
- Párrafo 4 de la síntesis (TO-01) en versión sin cifras.
- Actualización de bullets de próximos pasos (TO-11/TO-12), sujeta a revisión final.

## 5. Textos que DEBEN esperar los resultados espaciales

- Jerarquía interna definitiva de Belgrano (qué se afirma de Cabildo–Juramento y Bajo Belgrano;
  si Belgrano R aparece siquiera rotulado): corrida V3 + test de correspondencia + DH-05.
- Arquitectura de Recoleta (unidad general vs. unidad + 2 subzonas) y cualquier descripción de
  subzonas: la comparación espacial no corrió.
- Toda métrica V3 (registros, coberturas, composición de fuentes, dimensiones de componentes).
- Cualquier descripción de forma/extensión de los componentes de Costanera más allá de "cuatro
  componentes discontinuos".

## 6. Cómo evitar inflar la cantidad de páginas

- Página 8 absorbe el mapa de Costanera en su mitad vacía (cero páginas nuevas).
- Recoleta se financia con la compactación de próximos pasos (Opción A).
- No crear páginas de anexo técnico: los hashes y versiones van al bloque de trazabilidad del
  KPI lock y al QA, no al PDF político.
- Las zonas en observación restantes (área central, Caseros–Barracas) se resuelven en una caja,
  no en página propia.

## 7. Secuencia de integración (cuando llegue el handoff V3)

1. Inventariar handoff (archivos, hashes, CRS, fechas) contra el contrato de outputs.
2. Validar alcance: sin puntos individuales, sin nombres comerciales, sin identificadores técnicos.
3. Gates por polo: Belgrano (jerarquía respaldada; DH-05), Recoleta (máx. 2 subzonas; sin cifra
   de oferta), Costanera (4 componentes con `CN_C02`; vacíos sin conectores).
4. Completar `PLANTILLA_KPI_LOCK_V3.csv` → nuevo `kpis_lock` de la línea V3 (el preliminar no se toca).
5. Reemplazar assets y textos en una **copia paralela** del generador/YAML (línea nueva; el
   paquete `fase25_politica_e_integracion_editorial_v1` queda intacto).
6. Regenerar PDF paralelo, QA visual página por página (`scripts/qa/pdf_check.py`), validación
   cruzada texto–mapa–chip–decisión–KPI, y revisión de Diego.

## 8. Decisiones que vuelven a Diego antes de regenerar

1. Arquitectura de páginas para Recoleta (Opción A/B/C, §2).
2. Cantidad de "zonas seleccionadas" del encuadre (TO-02).
3. Nombres públicos de núcleos de Belgrano (DH-05) y eventual promoción de Belgrano R.
4. Chip de estado para Costanera en el sistema tipo/madurez (TO-09).
5. Si la regeneración V3 integra también los assets v2.1 pendientes (Corrientes, San Telmo,
   Puerto Madero) o los deja para una pasada posterior.
