# Plantillas de página — DGDGAS Informes v1

Plantillas de página tipo que combinan componentes (ver
`COMPONENTES_INFORMES_DGDGAS.md`) en un layout A4 completo. Cada plantilla
indica su **estructura**, los **componentes** que usa y la **grilla** sugerida.

Referencia de grilla (coordenadas relativas, como en los generadores actuales):

- Margen izquierdo/derecho: `0.065` / `0.935`.
- Ancho útil: `0.87`.
- Encabezado de sección: banda superior con título (`h1`) y bajada (`h2`).
- Footer: banda inferior con regla + `DGDGAS - {proyecto} - {tipo}` + nº página.

---

## P0 · Portada

| | |
|-|-|
| Fondo | `brand.primary` (banda superior) + `surface.page` |
| Componentes | Portada institucional (#1) |
| Contenido | kicker · título · subtítulo · descripción · ficha de datos generales |

```
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  (banda brand)
  DGDGAS – Dirección General de Desarrollo Gastronómico
  TÍTULO DEL INFORME
  Subtítulo
────────────────────────────────
  Descripción breve
  ┌ Datos generales ─────────────┐
  │ Evento / Lugar / Fechas / …  │
  └──────────────────────────────┘
```

---

## P1 · Índice

| | |
|-|-|
| Componentes | Índice (#2) |
| Contenido | entradas con num · texto · página; subsecciones indentadas |

```
Índice
 Contenido del informe.
 1    ………………………………………  3
 1.1    ……………………………………  3
 2    ………………………………………  4
```

---

## P2 · Datos generales

| | |
|-|-|
| Componentes | Ficha de relevamiento (#3), tabla institucional (#7) opcional |
| Contenido | modalidad · universo · período · volumen · distribución |

```
1. Datos generales del relevamiento
   Marco, lugar, fechas y volumen.
 ┌ 1.1 Ficha del relevamiento ─────┐
 └──────────────────────────────────┘
 1.2 Distribución (tabla opcional)
```

---

## P3 · Preguntas / variables

| | |
|-|-|
| Componentes | Caja «Pregunta analizada» (#4) repetida; nota de pie |
| Contenido | listado de preguntas con tipo y qué observan |

```
2. Preguntas del formulario
 ┌ ▍ Pregunta analizada ──┐  (cerrada)
 ┌ ▍ Pregunta analizada ──┐  (abierta)
 ┌ ▍ Pregunta analizada ──┐  (multi-respuesta)
 Nota: campos operativos no analizados.
```

**Regla:** las preguntas se muestran antes que cualquier resultado.

---

## P4 · Resultado con gráfico

| | |
|-|-|
| Componentes | Caja «Pregunta analizada» (#4), gráfico (#11), caja «Lectura» (#5) |
| Contenido | pregunta → gráfico con base/fuente → lectura descriptiva |

```
6. Canales de llegada
 ┌ ▍ Pregunta analizada ──┐
   ▆▆▆▆▆▆ Instagram   48 %
   ▆▆▆▆   Recomendación 30 %
   Base: … · Fuente: …
 ┌ ▍ Lectura de resultados ──┐
 (Nota multi-respuesta si aplica)
```

---

## P5 · Resultado con mapa

| | |
|-|-|
| Componentes | Página con mapa territorial (#10), caja «Lectura» (#5) |
| Contenido | mapa sobrio de referencia + leyenda + nota de alcance |

```
Título del mapa
 [ mapa: barrios/comunas + puntos/densidad ]
 Leyenda breve
 Nota de alcance: referencia territorial, no límites oficiales.
```

---

## P6 · Ficha de polo

| | |
|-|-|
| Componentes | Ficha de polo (#9) |
| Contenido | nombre · referencia territorial · descripción · aspectos |

```
Nombre del polo                       ● Principal
 Referencia territorial: barrios/comunas
 Descripción …
 Aspectos a considerar …
```

---

## P7 · Tabla comparativa / de polos

| | |
|-|-|
| Componentes | Tabla de polos (#8) |
| Contenido | filas con estado, prioridad y decisión sugerida |

```
Polos a revisar
 ┌ Polo │ Grupo │ Estado │ Decisión ┐
 │  …   │   …   │  ●     │    …     │
 └──────────────────────────────────┘
```

---

## P8 · Síntesis

| | |
|-|-|
| Componentes | Página de síntesis (#12) |
| Contenido | viñetas de resultados + nota breve |

---

## P9 · Aspectos a considerar

| | |
|-|-|
| Componentes | Página de aspectos (#13) |
| Contenido | viñetas en potencial + nota tentativa |

---

## P10 · Anexo

| | |
|-|-|
| Componentes | Página de anexo (#14); bloques #15/#16 si aplica |
| Contenido | material complementario, referencias históricas |

---

## Orden de páginas sugerido (informe de encuesta)

```
P0 Portada
P1 Índice
P2 Datos generales
P3 Preguntas / variables
P4 Resultado con gráfico   (×N secciones)
P5 Resultado con mapa      (si hay territorio)
P8 Síntesis
P9 Aspectos a considerar
P10 Anexo
```

## Orden de páginas sugerido (informe territorial, tipo PolosGastro)

```
P0 Portada
P1 Índice
P2 Datos generales / metodología breve
P5 Resultado con mapa (universo, núcleos, emergentes)
P7 Tabla de polos
P6 Ficha de polo (×N destacados)
P8 Síntesis
P9 Aspectos a considerar
P10 Anexo (casos secundarios, polos a revisar)
```
