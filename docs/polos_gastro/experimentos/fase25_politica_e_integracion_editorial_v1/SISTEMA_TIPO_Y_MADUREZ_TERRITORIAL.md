# Sistema de clasificación territorial en dos dimensiones — Tipo y Madurez

Estado: DOCUMENTACIÓN EDITORIAL EXPERIMENTAL. Fecha: 2026-07-11.
Implementa DEC-14 (`REGISTRO_DECISIONES_EDITORIALES_V2.md`). Matriz operativa en
`MATRIZ_TIPO_MADUREZ.csv`.

## 1. Principio

Cada zona se describe siempre con **dos atributos independientes**:

1. **Tipo territorial** — *qué forma tiene* la estructura gastronómica en el territorio.
   Es una propiedad del lugar. No cambia porque mejore o empeore la evidencia.
2. **Madurez de evidencia** — *cuán sólida es la base* que respalda esa lectura.
   Es una propiedad del conocimiento disponible. Puede cambiar sin que cambie la forma.

Errores que este sistema previene:

- leer "corredor" como si fuera un grado de avance ("todavía es corredor, después será
  polo") — **un corredor consolidado no es un polo inmaduro; es otra forma**;
- leer "experimental" como si fuera una forma ("la zona experimental") — experimental
  describe la evidencia, no el territorio;
- ordenar los tipos como escalera de importancia (núcleo > corredor > señal) — no hay
  jerarquía entre tipos; sí la hay, y explícita, entre grados de madurez.

Regla de redacción: **tipo = sustantivo; madurez = calificativo declarado aparte**.
"Corrientes es un corredor (tipo) con lectura consolidada (madurez)" — nunca "Corrientes
es un corredor consolidado a medias".

## 2. Dimensión 1 — Tipo territorial

| Tipo | Definición | Ejemplo actual |
| --- | --- | --- |
| **Núcleo compacto** | Concentración continua y acotada alrededor de un centro reconocible | San Telmo |
| **Corredor** | Estructura lineal continua a lo largo de un eje vial | Corrientes |
| **Red multinuclear** | Varias concentraciones próximas que funcionan como sistema dentro de una zona | Belgrano (en estudio); Palermo (hipótesis de escalado) |
| **Frente gastronómico** | Estructura lineal apoyada en un borde urbano (costa, diques), con uno o dos márgenes | Puerto Madero (frente doble) |
| **Unidad multiparte discontinua** | Piezas separadas que comparten una identidad, con vacíos reales preservados | Costanera Norte |
| **Señal exploratoria** | Indicio de concentración sin estructura defendible todavía | Zonas del pliego de observación |

Notas:

- "Señal exploratoria" es el único tipo que admite ausencia de geometría: puede
  representarse solo con densidad difusa o con mención textual.
- Una zona puede cambiar de tipo si la evidencia muestra otra forma (Puerto Madero pasó
  de "banda" a "frente doble"); el cambio de tipo requiere decisión registrada.

## 3. Dimensión 2 — Madurez de evidencia

| Madurez | Criterio | Ejemplo actual |
| --- | --- | --- |
| **Consolidado** | Representación estable, decisión firmada, sin condiciones pendientes de fondo | Corrientes (corredor, DEC-01) |
| **Con observaciones** | Representación estable pero con condiciones declaradas (p. ej. dependencia alta de fuente externa, geometría de presentación pendiente) | Puerto Madero (DEC-11); San Telmo (DEC-10, robustez media) |
| **Experimental** | Estructura detectada y repetida, pendiente de firma, shortlist o nombres | Belgrano (DEC-12) |
| **Exploratorio** | Sin medición defendible; lectura de interés institucional | Costanera Norte (DEC-13); zonas en observación |

Reglas:

- Una zona **solo sube de madurez por decisión firmada** registrada (regla heredada de
  la arquitectura V1, ahora referida solo a esta dimensión).
- La madurez se asigna **por representación**, no por zona en abstracto: el núcleo de San
  Telmo puede estar "con observaciones" mientras su eje contextual es solo eso, contexto.

## 4. Etiquetas, símbolos y tratamiento visual

### 4.1 Etiquetas de tipo (aparecen en leyenda, no bajo cada rótulo)

| Tipo | Etiqueta pública | Etiqueta interna |
| --- | --- | --- |
| Núcleo compacto | "núcleo gastronómico" | NUC |
| Corredor | "corredor" | COR |
| Red multinuclear | "red de núcleos" | RED |
| Frente gastronómico | "frente" | FRE |
| Unidad multiparte discontinua | "identidad en tramos" | MUL |
| Señal exploratoria | "lectura exploratoria" | SEN |

### 4.2 Distintivo de madurez (discreto, uno por lámina)

| Madurez | Distintivo visual | Texto del distintivo | Etiqueta interna |
| --- | --- | --- | --- |
| Consolidado | Punto lleno junto al título de lámina, color institucional pleno (azul #1F3B57) | "lectura consolidada" | MAD-C |
| Con observaciones | Punto lleno verde institucional (#2F6E5B) | "lectura consolidada, con seguimiento" | MAD-O |
| Experimental | Punto contorneado (anillo) gris azulado (#5E6B78) | "lectura en consolidación" | MAD-E |
| Exploratorio | Punto punteado gris (#8A97A3) | "lectura exploratoria" | MAD-X |

El distintivo es **un solo elemento** (punto + dos/tres palabras) alineado al título de
la lámina. Nunca un sello, nunca una marca de agua, nunca texto largo.

### 4.3 Estilos de línea y relleno por tipo (mapas)

| Tipo | Contorno | Relleno | Prohibiciones |
| --- | --- | --- | --- |
| Núcleo compacto | Línea continua 1,9 pt | Pleno 18 % de opacidad | Sin isolíneas múltiples |
| Corredor | Banda continua sobre el eje (franja orientativa, nota DEC-09) | Franja 22 % | Sin cortes internos que se lean como fronteras (DEC-02) |
| Red multinuclear | Línea continua 1,6 pt por núcleo, **idéntica entre núcleos** | Pleno 14 % | Sin contenedor duro; sin jerarquía visual entre núcleos mientras no haya firma |
| Frente gastronómico | Banda(s) sobre el/los márgenes | Franja 22 % | Sin segmentación interna en pieza política (DEC-11) |
| Unidad multiparte | Contorno continuo fino por pieza, misma etiqueta compartida | Pleno 12 % | Sin conectores, bandas ni buffers entre piezas (DEC-05/13) |
| Señal exploratoria | Sin contorno | Densidad difusa (gradiente sin borde) | Sin polígono; sin marcador puntual que se lea como local |

### 4.4 Cómo se combinan (la madurez modula, el tipo define)

La madurez **no cambia la forma** del símbolo; modula su énfasis:

- Consolidado / con observaciones: colores de zona plenos de la paleta DGDGAS.
- Experimental: mismo símbolo del tipo con contorno en gris azulado (#5E6B78) y relleno
  reducido a la mitad de opacidad.
- Exploratorio: tratamiento difuso (sin bordes) cualquiera sea el tipo, más el rótulo
  "lectura exploratoria" en la propia lámina.

## 5. Textos y notas estándar

- **Presentación del sistema (una vez por pieza, "Cómo leer"):**
  > "Cada zona se describe por su forma en el territorio (núcleo, corredor, red, frente,
  > identidad en tramos) y, por separado, por el grado de consolidación de su lectura
  > (consolidada, con seguimiento, en consolidación, exploratoria). Una cosa es la forma
  > de una zona; otra, cuánto sabemos hoy sobre ella."
- **Nota para láminas experimentales:**
  > "La estructura que se muestra está en proceso de consolidación; su forma y sus
  > referencias pueden ajustarse en próximas actualizaciones."
- **Nota para láminas exploratorias:**
  > "Lectura exploratoria: identifica interés territorial, no una delimitación."
- **Prohibido en todas las piezas:** usar los términos de tipo como grados ("todavía es
  un corredor"), usar los grados como formas ("la zona experimental de Belgrano"),
  ordenar tipos por importancia, mostrar las etiquetas internas (NUC, MAD-E) fuera de
  documentos internos.

## 6. Asignación vigente (2026-07-11)

La asignación operativa por zona está en `MATRIZ_TIPO_MADUREZ.csv`. Resumen: Corrientes
= corredor / consolidado; San Telmo = núcleo compacto / con observaciones; Puerto Madero
= frente gastronómico / con observaciones; Belgrano = red multinuclear (hipótesis) /
experimental; Costanera Norte = unidad multiparte discontinua / exploratorio; Palermo
Soho, Recoleta y Caseros/Barracas = tipo por confirmar / experimental (escalado v2.1 en
curso); resto del pliego de observación = señal exploratoria / exploratorio.

Cambios a esta asignación: solo por decisión registrada en el REGISTRO (V2 o sucesor).
