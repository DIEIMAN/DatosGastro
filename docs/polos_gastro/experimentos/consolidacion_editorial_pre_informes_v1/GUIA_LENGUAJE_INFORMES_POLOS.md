# Guía de lenguaje político/institucional — Informes de Polos Gastronómicos

Estado: PROPUESTA EDITORIAL EXPERIMENTAL. Fecha: 2026-07-11.
Aplica a: Fase 25 pulida, informe híbrido (variantes A y B) e informe metodológico.
Respeta el REGISTRO (DEC-01…DEC-09) y los guardrails permanentes (no convertir
habilitaciones en "locales activos"; no inventar métricas; separar universos de fuentes).

## Principio general

La incertidumbre se comunica **eligiendo bien el sustantivo**, no apilando adjetivos de
duda. "Área de referencia" ya dice que no es un límite; no necesita "aproximada",
"preliminar" y "no oficial" encima. Cada pieza declara su alcance **una vez** (línea
estándar + nota metodológica) y después afirma con vocabulario calibrado.

## Tabla de reemplazos

| Expresión problemática | Mapa político | Informe ejecutivo | Anexo metodológico |
| --- | --- | --- | --- |
| "zona aproximada" / "APROX." | (sin tag; la convención se declara una vez) | "área de referencia" | "aproximación de lectura territorial (convención declarada)" |
| "polígono candidato" | — (no se muestra nada candidato) | "zona en estudio" / "zona en observación" | "polígono candidato (pendiente de decisión editorial DEC/DH)" |
| "ruido" | — | "oferta dispersa fuera de las zonas de concentración" | "puntos no asignados (taxonomía DEC-08, categorías 1–6)" |
| "dependencia de Places" | — | "zonas cuya evidencia proviene principalmente de fuentes externas, en corroboración" | "participación de fuente E (Places) en el universo de la zona: X %" |
| "buffer" | — (franja dibujada, sin nombre) | "franja de representación del corredor" | "buffer de 60/90/120 m (convención cartográfica orientativa, DEC-09)" |
| "cluster" | — | "concentración" / "núcleo gastronómico" | "cluster (HDBSCAN)" |
| "KMeans" | — | — (método descartado; no se menciona) | "subdivisión KMeans (abandonada; ver informe metodológico cap. 9)" |
| "HDBSCAN" | — | "métodos de detección de concentraciones" | "HDBSCAN (parámetros en anexo)" |
| "universo semilla" | — | "relevamiento inicial de referencias" | "universo semilla (106 referencias geolocalizadas)" |
| "baja confianza" | — | "lectura exploratoria" / "requiere mayor corroboración" | "estabilidad por bloques X; dependencia de fuente Y %" |
| "no oficial" | (la línea estándar de alcance lo cubre) | "referencia de trabajo institucional" | "sin estatus normativo; no constituye delimitación oficial" |
| "evidencia media/alta/baja" | — | "zona consolidada / en observación / exploratoria" | "clasificación de evidencia (criterios en tabla)" |
| "candidato a polo" | — | "zona con potencial de consolidación" | "candidata (checklist de revisión pendiente)" |
| "universo experimental" | — | "base de evidencia ampliada" | "universo experimental F01/F02 + E sanitizado" |
| "puntos fuera de representación" | (símbolo menor de contexto, sin texto) | "oferta gastronómica de contexto" | "no asignados por categoría (DEC-08)" |
| "macroárea / macrozona" | "zona" | "zona (con sectores internos)" | "macrozona (contenedor de análisis)" |
| "hito colectivo / hito de lectura" | "referencia" (o el nombre propio) | "hito" | "hito de lectura territorial" |
| "banda de docks" | "frente de los diques" | "frente gastronómico de los diques" | "frente (soporte vial: ejes inventariados)" |
| "señal exploratoria" | "lectura exploratoria" | "lectura exploratoria" | "señal sin polígono (KDE + puntos)" |
| "preliminar / borrador" | — (no aparece en piezas entregables) | "primera lectura" / "lectura inicial" | "versión de trabajo (fase interna)" |

Regla de lectura de la tabla: "—" significa que la expresión (y su concepto) **no debe
aparecer** en ese registro; si el concepto es imprescindible, se resuelve gráficamente o
se traslada al registro siguiente.

## Lenguaje para mapa político (láminas)

- Solo nombres propios de lugar + tres categorías visuales: zona consolidada, eje
  /corredor, lectura exploratoria.
- Sin tags técnicos bajo las etiquetas; sin porcentajes; sin fuentes.
- Leyendas de una palabra por ítem ("zona", "corredor", "sector", "referencia").
- La única frase permitida de alcance: la línea estándar (abajo).

## Lenguaje para informe ejecutivo (cuerpo)

- Verbos de hallazgo: "se concentra", "se consolida", "se observa", "gana relevancia",
  "merece seguimiento".
- Sustantivos calibrados: "polo consolidado", "eje gastronómico", "área de referencia",
  "sector", "zona en observación", "lectura exploratoria".
- Cifras: solo conteos redondeados y comparaciones simples; nunca parámetros ni
  decimales de métricas internas.
- Honestidad concentrada: una línea de alcance en el resumen + nota metodológica final.
- Prohibido: nombres de algoritmos, de plataformas externas, "ruido", "candidato",
  "semilla", "aproximado" como adjetivo repetido, "no oficial" fuera de la línea
  estándar, siglas internas (F01, DH, KDE) y numeración de fases internas ("Fase 25").

## Lenguaje para anexo metodológico

- Todos los términos técnicos permitidos, **siempre con su primera aparición
  explicada** en una frase llana.
- Los métodos descartados se nombran junto con la razón del descarte (transparencia).
- Las convenciones se declaran como tales, con su ID de decisión (DEC-09).
- La fuente externa se nombra con su clasificación (E), su peso por zona y la
  advertencia de error de apareo mientras DH-11 esté pendiente.

## Lenguaje que debe evitarse en todos los registros

- "Locales activos" cuando la fuente mide habilitaciones, registros u oferta relevada
  (guardrail permanente).
- "Ranking", "los mejores", "top" — la pieza no ordena preferencias.
- "Delimitación oficial", "límites del polo" en afirmativo — nada tiene estatus
  normativo.
- "Datos de Google" a secas — la fuente externa es auxiliar y sanitizada; en piezas
  públicas no se nombra la plataforma.
- Promesas de fecha o de resultado de pruebas pendientes ("cuando se confirme X, el
  polo será…").
- Lenguaje de IA o de proceso interno ("el modelo detectó", "el algoritmo decidió") —
  las decisiones son institucionales.

## Línea estándar de alcance (única autorizada, dos apariciones máximo por pieza)

> "Las áreas y ejes representados son referencias de lectura territorial elaboradas por
> la DGDGAS; no constituyen límites oficiales ni un registro de establecimientos."

## Nota estándar de franjas (DEC-09, para mapas con corredores/frentes)

> "Las franjas que acompañan a los ejes son convenciones de representación cartográfica,
> de carácter orientativo."
