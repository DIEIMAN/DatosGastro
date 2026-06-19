# Skill 07 — Informes ejecutivos

Cómo redactar informes para jefatura (Dirección / Subsecretaría) que sean creíbles, útiles y
metodológicamente honestos.

## 1. Tono

- **Institucional y sobrio.** Es un documento de gestión pública, no marketing.
- **Claro y directo.** Frases cortas. Una idea por frase.
- **Sin exagerar.** No vender hallazgos más fuertes de lo que la evidencia sostiene.
- **Sin lenguaje de IA.** Evitar muletillas tipo "En el siempre cambiante mundo de...", "Es
  importante destacar que...", "En conclusión, podemos afirmar que...", emojis decorativos,
  superlativos vacíos ("revolucionario", "potente", "increíble") y listas de relleno.

## 2. Estructura recomendada

1. **Resumen ejecutivo** (5–10 líneas): qué se hizo, qué se encontró, qué se recomienda.
2. **Hallazgos** (tablas y bullets): lo que los datos muestran, con la magnitud correcta.
3. **Límites y riesgos metodológicos**: separados de los hallazgos, explícitos.
4. **Próximos pasos**: accionables, con responsable sugerido y plazo.
5. **Anexo** (opcional): detalle técnico, fuentes, fechas de corte.

## 3. Separar hallazgos de límites (no mezclar)

| Hallazgo (lo que muestra el dato) | Límite (lo que el dato NO permite afirmar) |
| --- | --- |
| "Se documentaron N eventos en 2026" | "N representa todos los eventos del año" |
| "X habilitaciones aprobadas con coordenada" | "X locales activos hoy" |
| "Densidad de oferta registrada por comuna" | "Densidad de locales operando" |

Cada afirmación fuerte debe tener al lado su límite. Nunca presentar un agregado sin su
denominador y su fecha de corte.

## 4. Reglas de contenido

- **Priorizar tablas y bullets ejecutivos** sobre párrafos largos.
- **Marcar riesgos metodológicos** de forma visible (sección propia o etiqueta).
- Usar el **sustantivo correcto** según la fuente (skills 01, 02, 05): oferta registrada, oferta
  visible, habilitaciones aprobadas, permisos — **no** "locales activos" si la fuente no lo mide.
- **No exponer datos sensibles** (skill 03): nada de CUIT, DNI, montos individuales, contactos.
  Solo agregados con umbral mínimo.
- Declarar siempre **fuente, fecha de corte y universo** de cada número.
- Si un dato es incierto o parcial, decirlo. La credibilidad vale más que la contundencia.

## 5. Checklist antes de entregar un informe

1. ¿Cada número tiene fuente, fecha de corte y universo?
2. ¿Separé hallazgos de límites?
3. ¿Usé el sustantivo correcto (no "activos" si no aplica)?
4. ¿Hay próximos pasos accionables?
5. ¿Eliminé muletillas de IA y superlativos vacíos?
6. ¿No se filtró ningún dato personal o individual sensible?
7. ¿Las tablas se entienden sin leer el cuerpo?

## 6. Versiones interna vs. publicable

- **Versión interna**: puede citar más detalle de gestión, pero igual sin datos personales.
  Va a `outputs/analisis_interno/` (ignorada por Git).
- **Versión publicable**: solo agregados seguros, lista para compartir fuera del área.
- Cada informe interno debe declarar explícitamente **qué se puede publicar y qué no**.
