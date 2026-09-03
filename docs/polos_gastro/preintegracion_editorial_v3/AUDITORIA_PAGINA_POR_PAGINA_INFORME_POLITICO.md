# Auditoría página por página — Informe político experimental (preintegración V3)

Estado: **PREINTEGRACIÓN / SIN RESULTADOS V3**. Fecha: 2026-07-11.
Rol: `integrador_tecnico_editorial` (infraestructura V1.1.1).

## Objeto auditado

- PDF: `outputs/polos_gastro/experimentos/fase25_politica_e_integracion_editorial_v1/INFORME_POLOS_GASTRO_FASE25_POLITICA_EXPERIMENTAL_V1.pdf` (10 páginas).
- Método: lectura de los 10 PNG de QA del paquete `REVISION_FASE25_POLITICA_EXPERIMENTAL/02_QA_PNG/`
  (inspección visual directa de páginas 3, 7 y 8, las más afectadas por las decisiones vigentes),
  contraste con `contenido_fase25_politica_experimental_v1.yaml` (textos verbatim),
  `QA_VISUAL_PAGINA_A_PAGINA_FASE25_POLITICA.md`, `MATRIZ_ASSETS_PENDIENTES_CODEX.csv`,
  `kpis_lock_preliminar.json` y `DECISIONES_Y_USOS_DOCUMENTALES.md` (línea V1.1, con DEC-10).
- **Nada del paquete auditado fue modificado.**

## Marco de decisiones aplicado

Belgrano: un único polo con centralidad principal (Barrio Chino–Belgrano C–Barrancas–Pasaje
Echeverría), eje interno Cabildo–Juramento, Bajo Belgrano diferenciado y Belgrano R secundario
condicional. Recoleta: un único polo, máximo dos subzonas, Callao–9 de Julio y Bellas Artes como
referencias. Costanera Norte: DEC-10 (polo adoptado, cuatro componentes con `CN_C02`, apto para
cuerpo y cartografía principal, vacíos preservados, Places explicado una vez en método).

## Tabla de auditoría

| página | elemento | estado | problema | insumo futuro requerido | acción propuesta |
|---|---|---|---|---|---|
| 1 | Portada (título, institución, fecha, marca de versión interna) | CONSERVAR | Ninguno. `pdf_subject` en metadatos referencia la matriz de assets v2.1; detalle menor. | Ninguno (actualizar `pdf_subject` al regenerar). | Conservar sin cambios de diseño. |
| 2 | Síntesis ejecutiva + caja "Cómo leer esta pieza" | ACTUALIZACIÓN MENOR | Párrafo 4 presenta Belgrano y Costanera como "señales de actividad en seguimiento" (obsoleto: ambos son polos por decisión). Encuadre dice "cinco zonas seleccionadas" (cifra a revisar si Recoleta y Costanera pasan al detalle). Recoleta ausente de la síntesis. | Confirmación de arquitectura V3 (cantidad de zonas en detalle). | Reescribir párrafo 4 y encuadre; sumar mención de Recoleta. Diseño de página se conserva. |
| 3 | Mapa general de polos y ejes (asset `global_mapa_fase25.png`) + caja Lectura | REDISEÑO (asset) | Costanera Norte dibujada como **eje/corredor rojo** (contradice DEC-10: polo multiparte). Recoleta como simple "área/barrio de lectura". Belgrano dentro de "macrozona con subzonas" sin estatus de polo. Leyenda de 4 categorías no admite "polo multiparte". Texto de Lectura dice "frente ribereño en observación". | Mapa general V3 de Codex con los tres polos nuevos y Costanera en 4 componentes discontinuos; leyenda rediseñada. | Reemplazar asset y leyenda; reescribir caja Lectura. Riesgo de diseño: los 4 componentes de Costanera se concentran junto al Aeroparque (esquina NE del lienzo) — riesgo de solapamiento de rótulos con Palermo/Belgrano. |
| 4 | Mapa Palermo (asset placeholder) + lectura territorial | CONSERVAR | Placeholder heredado ya saneado (sin tags APROX.). Reemplazo por capa de escalado Palermo Soho (PEN-04) es opcional y **fuera del alcance V3**. | Ninguno para V3 (PEN-04 queda en cola v2.1). | Conservar. No bloquear V3 por Palermo. |
| 5 | Mapa Corrientes–Abasto (placeholder) + lecturas | CONSERVAR | Placeholder pendiente de la capa de corredor v2.1 (DEC-01/DEC-20/PEN-03); pendiente previo, no lo introduce V3. Texto vigente y alineado con decisiones. | Corredor v2.1 (cola previa, independiente de V3). | Conservar; reemplazo de asset cuando llegue la capa, sin tocar texto. |
| 6 | Mapas San Telmo y Puerto Madero (2 placeholders) + lecturas | CONSERVAR / ACTUALIZACIÓN MENOR | Placeholders pendientes v2.1 (núcleo+Defensa; frente doble `PM_PRES_C`, no los ~80 segmentos analíticos). Frase "la representación cartográfica de detalle… se encuentra en elaboración" caduca al llegar el asset. | Capas presentación v2.1 San Telmo y Puerto Madero (cola previa). | Conservar diseño; al reemplazar assets, retirar la frase "en elaboración". |
| 7 | "Belgrano y zonas en observación": mapa Belgrano + caja "Zonas en observación" | REDISEÑO | Mapa muestra Barrio Chino, Bajo Belgrano y Belgrano R como **tres "ÁREA DE LECTURA" equivalentes**, sin jerarquía (contradice la estructura decidida: centralidad principal + eje interno + centralidad diferenciada + sector secundario condicional). Falta Cabildo–Juramento como eje interno. La caja mantiene a **Recoleta como "zona en observación"** (obsoleto: Recoleta es polo único). Título de página obsoleto. Espacio libre ~20 % al pie. | Mapa Belgrano V3 (jerarquía interna respaldada espacialmente; Belgrano R solo si el análisis lo sostiene); resultado de la comparación de arquitecturas de Recoleta. | Rediseñar página como "Polo Gastronómico Belgrano"; sacar a Recoleta de la caja de observación. Decidir dónde vive Recoleta (ver plan de integración). |
| 8 | Costanera Norte: página solo textual (3 paneles), sin mapa | REDISEÑO / REEMPLAZO DE TEXTOS | Contradice DEC-10 en cadena: "tres sectores principales" (son 4 componentes con `CN_C02`), chip "lectura exploratoria", panel completo "Qué significa lectura exploratoria" con "**no constituye un polo delimitado**" y "sin proponer todavía una delimitación" (expresiones expresamente vetadas por DEC-10). No hay mapa. **Mitad inferior de la página vacía**: espacio disponible para el mapa multiparte sin agregar páginas. | Mapa Costanera Norte V3 multiparte (4 componentes, vacíos preservados, sin conectores); métricas V3 por componente. | Reescribir los tres paneles con lenguaje DEC-10 ("delimitación adoptada", "polo identificado", "estructura multiparte", "actualizable con nueva evidencia"); insertar mapa en la mitad inferior. Panel "condiciones del territorio" es rescatable casi íntegro (explica vacíos, coherente con DEC-05). |
| 9 | Próximos pasos + caja "Relación con la lectura general" | ACTUALIZACIÓN MENOR | Ítem 2 promete "extender el análisis en detalle a … Recoleta" e ítem 3 "mantener el seguimiento del frente ribereño de la Costanera Norte y de las zonas en observación" — ambos quedan cumplidos/superados al integrar V3. | Confirmación de qué zonas quedan efectivamente pendientes tras V3. | Reformular bullets; el resto de la página se conserva. |
| 10 | Nota metodológica | ACTUALIZACIÓN MENOR | Falta el único lugar donde debe explicarse la dependencia de Places de Costanera (DEC-10: "una sola vez en método"). Falta el marco "delimitación adoptada, actualizable" para los tres polos nuevos. El texto vigente de alcance sigue siendo válido. | Valor v2.1/V3 de dependencia de fuente externa de Costanera confirmado en el handoff. | Agregar un párrafo de dependencia de fuentes (sin afirmar informalidad; hipótesis permitidas: subregistro administrativo, categorías, concesiones, oferta móvil). Conservar el resto. |

## Riesgos de diseño transversales al reemplazar mapas

1. **Leyenda del mapa general** (p. 3): las categorías actuales (área/barrio, macrozona,
   área de lectura, eje/corredor) no representan "polo multiparte discontinuo" ni
   "centralidad interna"; la leyenda debe rediseñarse sin crecer al punto de invadir el lienzo.
2. **Chips de estado de lectura** (páginas 4–8): el sistema tipo/madurez
   (`SISTEMA_TIPO_Y_MADUREZ_TERRITORIAL.md`) debe emitir estados nuevos coherentes para
   Belgrano, Recoleta y Costanera; "lectura exploratoria" ya no aplica a Costanera.
3. **Densidad de rótulos en Belgrano** (p. 7): pasar de 3 cajas a una jerarquía de 4 niveles
   exige tipografía diferenciada; riesgo de saturación en un lienzo que hoy ya usa rótulos grandes.
4. **Paginación**: Recoleta no tiene página propia hoy; ver alternativas en
   `PLAN_INTEGRACION_EDITORIAL_V3.md` para sostener 9–10 páginas.
5. **Consistencia texto–mapa–chip–KPI**: cada página modificada debe pasar el gate cruzado del
   `PLAN_INTEGRACION_HANDOFF_CODEX_V21.md` §Validación cruzada (texto, mapa, tipo, madurez,
   decisión y KPI coherentes).

## Resumen

- 10/10 páginas auditadas.
- Conservables sin cambios: 1, 4, 5 (3 páginas; la 6 casi íntegra).
- Actualización menor de texto: 2, 6, 9, 10 (4 páginas).
- Rediseño: 3 (asset + leyenda), 7 (estructura Belgrano + salida de Recoleta), 8 (textos DEC-10 + mapa nuevo) (3 páginas).
- Página nueva potencial: Recoleta (decisión editorial pendiente, ver plan).
