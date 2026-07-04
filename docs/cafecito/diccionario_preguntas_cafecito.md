# Diccionario de preguntas — Formulario Cafecito

**Evento:** Cafecito BA en tu barrio — La Glorieta de Barrancas de Belgrano, CABA.
**Fechas:** sábado 27 y domingo 28 de junio de 2026 (10–18:30 h / 10–18 h).
**Relevamiento:** encuesta al público realizada por el equipo de Gastronomía (BA Capital Gastronómica).
**Respuestas recibidas:** 79.

Fuente del diccionario: `Cafesito/Formulario cafecito.pdf` (preguntas + justificación) y la
estructura real del `Cafesito/Formulario Cafecito (Respuestas).xlsx`.

> **Nota de privacidad:** las columnas marcadas como **SENSIBLE** no se publican en tablas,
> gráficos ni en el informe. Se usan solo para conteos agregados o se excluyen por completo.

---

| # | Columna (xlsx) | Pregunta | Objetivo (según PDF) | Tipo de variable | Cómo se analiza | Limitaciones |
|---|---|---|---|---|---|---|
| A | Marca temporal | (metadato del formulario) | Registrar momento de carga | Fecha/hora individual — **SENSIBLE** | No se publica; a lo sumo rango de fechas agregado | Identifica a la persona por momento exacto; no aporta al perfil |
| B | Dirección de correo electrónico | Correo electrónico | Identificador único + base de contactos (con consentimiento) | Texto — **SENSIBLE (dato personal)** | **Excluida** de todo output. Solo se cuenta cuántos respondieron | Dato personal directo; nunca se expone |
| C | ¿Aceptás recibir información…? | Consentimiento de contacto | Saber quién acepta recibir novedades | Cerrada binaria (Sí/No) | Distribución de % que acepta | Mide intención declarada, no comportamiento |
| D | ¿Cuál es tu rango de edad? | Rango etario | Orientar comunicación por edad | Cerrada ordinal (6 tramos) | Distribución por tramo | Tramos amplios; muestra chica |
| E | ¿Con qué género te identificás? | Género | Composición del público | Cerrada nominal (Mujer/Varón/No binario) | Distribución | Categorías limitadas; N bajo en algunas |
| F | ¿Dónde vivís actualmente? | Procedencia (nivel macro) | Alcance territorial | Cerrada nominal (CABA/GBA/PBA/Otra) | Distribución | No distingue barrio fino |
| G | Indicanos tu barrio o localidad | Procedencia (nivel fino) | Detalle territorial | Texto libre — **SENSIBLE (potencialmente identificable)** | Solo agregado por barrio si N≥umbral; **no se listan respuestas individuales** | Texto libre, tipeos, baja cardinalidad por barrio |
| H | ¿Es la primera vez…? | Primera asistencia | Público nuevo vs recurrente | Cerrada (Sí/No/No seguro) | Distribución | Autodeclarado; sin verificación |
| I | ¿Con quién viniste? | Composición del grupo | Dinámica de asistencia | Cerrada nominal | Distribución | Categorías fijas |
| J | ¿Cómo te enteraste? | Canal de difusión | Efectividad de canales | Cerrada **multi-respuesta** | Desagregar por coma y contar por canal | Multi-select infla totales; reportar sobre N respuestas |
| K | ¿Qué fue lo que más te interesó? | Atractivo principal | Qué funciona del evento | Semi-cerrada (7 opciones, 1 por persona) | Distribución | Opciones acotadas; algunas con N muy bajo |
| L | ¿Qué tipo de eventos te interesaría a futuro? | Demanda futura | Insumo de programación | **Multi-respuesta** abierta (categorías + texto libre) | Desagregar por coma; agrupar categorías; cola libre como cualitativo | Multi-select + texto libre; categorías heterogéneas |

---

## Clasificación rápida

- **Cerradas (analizables por distribución):** C, D, E, F, H, I, K.
- **Cerradas multi-respuesta (desagregar):** J, L.
- **Texto libre / cualitativo:** G (sensible, solo agregado), cola de L.
- **Sensibles (no publicar):** A (timestamp), B (correo), G (barrio fino).

## Decisiones metodológicas

- El correo (B) se **excluye** por completo de los outputs; solo se reporta cuántas respuestas
  lo traían, como control de completitud.
- El barrio fino (G) **no se lista**; si se usa, se agrega y se omiten categorías con muy pocos
  casos para no volver identificable a nadie.
- En J y L (multi-respuesta) los porcentajes se calculan **sobre el total de respondentes**, por lo
  que **suman más de 100 %** (cada persona puede elegir varias opciones). Se aclara en cada gráfico.
- No se imputan respuestas faltantes. Solo se normalizan mayúsculas/acentos/espacios obvios.
