# Componentes — DGDGAS Informes v1

Catálogo de componentes reutilizables del sistema. Cada componente se describe
con: **propósito**, **tokens que usa**, **contenido esperado** y **reglas**.
Los esqueletos de implementación están en
`scripts/shared/reporting_dgdgas/report_components_dgdgas.py`.

Convención de lectura del esquema visual (ASCII):

```
┌───────────────┐   borde        → border.subtle / border.strong
│ ▍ Título      │   barra ▍       → color de acento del componente
│   texto…      │   fondo         → surface.*
└───────────────┘
```

---

## 1. Portada institucional

**Propósito:** primera página. La Dirección debe ser más visible que el nombre
interno del proyecto.

**Tokens:** fondo `brand.primary`; texto `text.on_brand`; kicker en
`brand.secondary`/`#c9d6e4`; tabla de datos generales sobre `surface.page`.

```
┌──────────────────────────────────────────┐
│ DGDGAS – Dirección General de Gastronomía │  kicker (brand)
│                                           │
│  Título del informe                       │  display 26
│  Subtítulo / bajada                       │  h2
│                                           │
│  Descripción breve (2–4 líneas)           │  body
│                                           │
│  ┌───────────────────────────────────┐    │
│  │ Evento / Alcance   ……………           │    │  ficha de datos generales
│  │ Lugar              ……………           │    │
│  │ Fechas             ……………           │    │
│  │ Presenta           DGDGAS – …      │    │
│  └───────────────────────────────────┘    │
└──────────────────────────────────────────┘
```

**Reglas:** sin logos de terceros no autorizados; sin rutas ni versiones
internas; «Presenta: DGDGAS – Dirección General de Gastronomía».

---

## 2. Índice

**Propósito:** navegación con números de página. Secciones numeradas;
subsecciones indentadas.

**Tokens:** títulos `text.primary`; números de página `text.secondary`;
regla `border.subtle`.

```
Índice
1    Datos generales del relevamiento .............. 3
1.1    Ficha del relevamiento ...................... 3
1.2    Respuestas por día y franja ................. 3
2    Preguntas del formulario ...................... 4
…
```

**Reglas:** las páginas deben ser reales; las subsecciones llevan `sub: true`.

---

## 3. Ficha de relevamiento

**Propósito:** resumen estructurado del origen del dato (modalidad, universo,
fechas, volumen).

**Tokens:** `surface.card`, borde `border.subtle`, título `brand.primary`.

```
┌ 1.1 Ficha del relevamiento ────────────────┐
│ Modalidad   Encuesta en formulario digital  │
│ Universo    Respuestas obtenidas            │
│ Período     …                               │
│ Volumen     … respuestas                    │
└─────────────────────────────────────────────┘
```

**Reglas:** describir la naturaleza del dato sin convertir registros o
habilitaciones en «locales activos».

---

## 4. Caja «Pregunta analizada»

**Propósito:** mostrar la pregunta **antes** del resultado (encuestas).

**Tokens:** fondo `surface.card`; acento `brand.secondary`.

```
┌ ▍ Pregunta analizada ───────────────────────┐
│ ¿Cómo te enteraste del evento?              │
│ Tipo: multi-respuesta                       │
│ Qué permite observar: canales de llegada.   │
└─────────────────────────────────────────────┘
```

**Reglas:** indicar tipo (cerrada / abierta / multi-respuesta / consentimiento)
y qué permite observar.

---

## 5. Caja «Lectura de resultados»

**Propósito:** interpretación descriptiva y prudente del resultado.

**Tokens:** fondo `surface.note`; acento `brand.primary`.

```
┌ ▍ Lectura de resultados ────────────────────┐
│ Instagram fue el canal más mencionado (…).  │
│ La suma puede superar 100 % (multi-respuesta).│
└─────────────────────────────────────────────┘
```

**Reglas:** tono descriptivo; recomendaciones en potencial; sin bases/universo
dentro de la caja (van en el epígrafe del gráfico).

---

## 6. Caja «Nota metodológica breve»

**Propósito:** aclaración corta en el cuerpo. Lo extenso va a anexo.

**Tokens:** fondo `surface.card`; acento `text.muted`; radio `sm`.

```
┌ Nota metodológica ──────────────────────────┐
│ Resultados agregados sobre las respuestas   │
│ obtenidas. Muestra acotada.                 │
└─────────────────────────────────────────────┘
```

---

## 7. Tabla institucional

**Propósito:** presentar datos tabulares legibles en A4.

**Tokens:** encabezado `border.strong` + `text.on_brand`; filas alternas
`surface.zebra`; bordes `border.subtle`.

```
┌───────────────┬──────────┬──────────┐
│ Categoría     │ Menciones│ % base   │  ← encabezado
├───────────────┼──────────┼──────────┤
│ Instagram     │      120 │    48 %  │
│ Recomendación │       75 │    30 %  │  ← fila alterna
└───────────────┴──────────┴──────────┘
```

**Reglas:** números a la derecha; sin columnas técnicas en informes ejecutivos.

---

## 8. Tabla de polos

**Propósito:** variante de tabla institucional para listados de polos con
estado, prioridad y decisión sugerida.

**Tokens:** igual que tabla institucional; celda de estado coloreada con
`content_states.*`.

```
┌──────────────┬──────────┬───────────┬──────────────────┐
│ Polo         │ Grupo    │ Estado    │ Decisión sugerida│
├──────────────┼──────────┼───────────┼──────────────────┤
│ …            │ Núcleo   │ ● Principal│ Mantener         │
│ …            │ Emergente│ ● Preliminar│ Revisar         │
└──────────────┴──────────┴───────────┴──────────────────┘
```

**Reglas:** destacar estado/prioridad con color sobrio, no alarmista.

---

## 9. Ficha de polo

**Propósito:** ficha individual de un polo territorial.

**Tokens:** `surface.card`; título `brand.primary`; chips de estado con
`content_states.*`.

```
┌ Nombre del polo ────────────────  ● Principal ┐
│ Referencia territorial: barrios/comunas       │
│ Descripción breve …                           │
│ Aspectos a considerar …                       │
└───────────────────────────────────────────────┘
```

**Reglas:** referencia territorial por barrio/comuna, no límites oficiales.

---

## 10. Página con mapa territorial

**Propósito:** lectura territorial de referencia (no cartografía oficial).

**Tokens:** tierra/agua/límites de `map.*`; puntos `brand.secondary`;
leyenda `surface.page` + `border.subtle`.

```
┌ Título del mapa ────────────────────────────┐
│  [ mapa sobrio: barrios/comunas + puntos ]  │
│  Leyenda: ● sedes   ▨ densidad              │
│  Nota de alcance: mapa de referencia; …     │  ← obligatoria si es conceptual
└─────────────────────────────────────────────┘
```

**Reglas:** nota de alcance obligatoria en mapas conceptuales/preliminares;
sin geometría de plataformas privadas.

---

## 11. Página con gráfico

**Propósito:** un resultado con gráfico legible.

**Tokens:** secuencia `chart.sequence`; grilla `chart.grid`.

```
┌ Título del resultado ───────────────────────┐
│ Pregunta analizada (caja)                   │
│  ▆▆▆▆▆▆▆ Instagram          48 %            │
│  ▆▆▆▆    Recomendación      30 %            │
│  Base: … · Fuente: …                        │  ← epígrafe
│ Lectura de resultados (caja)                │
└─────────────────────────────────────────────┘
```

**Reglas:** barras/tablas antes que circulares; título + base + fuente +
lectura breve. Pregunta antes del resultado en encuestas.

---

## 12. Página de síntesis

**Propósito:** principales resultados descriptos, en viñetas.

**Tokens:** viñetas `text.primary`; nota `text.secondary`.

```
┌ Síntesis de resultados observados ──────────┐
│ • Punto 1 …                                 │
│ • Punto 2 …                                 │
│ Nota: resultados agregados; muestra acotada.│
└─────────────────────────────────────────────┘
```

---

## 13. Página de aspectos a considerar

**Propósito:** líneas de trabajo tentativas, en potencial.

**Tokens:** igual que síntesis; encabezado `brand.primary`.

```
┌ Aspectos a considerar ──────────────────────┐
│ • Podría sostenerse …                        │
│ • Sería conveniente evaluar …               │
│ Nota: consideraciones tentativas.           │
└─────────────────────────────────────────────┘
```

**Reglas:** todo en potencial; sin conclusiones definitivas sobre muestra
acotada.

---

## 14. Página de anexo

**Propósito:** material complementario, fuera de los resultados principales.

**Tokens:** encabezado `text.muted`; etiqueta de estado `anexo`.

```
┌ Anexo: … ───────────────────────────  Anexo ┐
│ Material complementario. No forma parte de  │
│ los resultados principales.                 │
└─────────────────────────────────────────────┘
```

---

## 15. Bloque «Requiere validación»

**Propósito:** marcar datos pendientes de confirmar.

**Tokens:** fondo `surface.warn`; borde `border.strong`; acento
`status.pending`.

```
┌ ▍ Requiere validación ──────────────────────┐
│ Este dato es preliminar y debe confirmarse. │
└─────────────────────────────────────────────┘
```

**Reglas:** visible pero no alarmista; nunca presentar como consolidado.

---

## 16. Bloque «Estado de documentación»

**Propósito:** indicar la madurez del informe/sección (borrador, en revisión,
final).

**Tokens:** chip con `content_states.*` (preliminar / interno / histórico).

```
┌ Estado de documentación ────────────────────┐
│ ● Borrador   ○ En revisión   ○ Final         │
└─────────────────────────────────────────────┘
```

**Reglas:** en documentos públicos, remover marcas de estado interno antes de
publicar (ver QA).

---

## Índice de estados de contenido

Los chips de estado usan `content_states.*` de los tokens:

| Estado | Uso |
|--------|-----|
| Resultado principal | dato consolidado |
| Resultado secundario | dato de apoyo |
| Preliminar | aún no consolidado |
| Requiere validación | pendiente de confirmar |
| Anexo | material complementario |
| Advertencia metodológica | límite de lectura |
| Uso interno | no publicar |
| Referencia histórica | antecedente |
