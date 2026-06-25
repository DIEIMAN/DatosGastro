# Especificación del informe V4 — Mercados gastronómicos (estilo DataGastro)

> Documento de diseño/framing para la V4. Alinea el informe de mercados gastronómicos con la
> familia DataGastro / informe de casas de pastas. **No cambia datos ni conteos.** Fecha: 2026-06-24.

## 1. Objetivo de la V4

Convertir el informe de mercados gastronómicos en una **pieza ejecutiva DataGastro**: clara,
visual y con framing de diagnóstico territorial, no en un documento metodológico largo. El número
y el contenido se mantienen; cambia la **presentación, el lenguaje y la estructura narrativa**.

## 2. Cambios respecto de V3

1. **Lenguaje de prudencia.** En el informe principal se reemplaza "activos confirmados" por
   **"activos identificados"** / "activos identificados en relevamiento documental". "Confirmado"
   se reserva para contexto interno o se aclara como "confirmado documentalmente". Motivo: no hubo
   validación territorial.
2. **Número principal:** se mantiene **13 mercados gastronómicos activos identificados** (no vuelve
   a 12).
3. **Activos vs. no activos.** Mercado Soho, Mercat Caballito y El Galpón se presentan como
   **"espacios gastronómicos relevantes no contabilizados como activos por señales de cierre o
   falta de actividad reciente"** (no como errores ni fuera de alcance). Mercado de los Carruajes:
   **cerrado documentado / antecedente relevante**.
4. **Tipología primaria única.** Cada mercado tiene **un solo `tipo_primario`**; las categorías
   suman exactamente **13**, sin doble conteo. "Itinerante" deja de ser tipo y pasa a **atributo**
   (`es_itinerante`); "productores" se refleja también como atributo (`perfil_productores`).
5. **Multifuente / respaldo documental.** Se agrega una lectura de respaldo por mercado (ver §9),
   con niveles de **respaldo documental** (no de confianza territorial).

## 3. Estructura final por páginas (narrativa)

```text
1.  Portada diseñada (banda oscura, título DataGastro, autoría)
2.  Resumen ejecutivo con KPI cards
3.  ¿Cómo se construyó el universo identificado?
4.  ¿Cuántos mercados gastronómicos activos hay y de qué tipo?
5.  ¿Dónde están?
6.  ¿Quién los gestiona?
7.  ¿Cuándo abren?
8.  ¿A quién apuntan?
9.  Casos patrimoniales y mercados con identidad histórica
10. ¿Qué espacios quedaron afuera y por qué?
11. ¿Qué decisión permite tomar este informe?
12. Referencias documentales visibles
13. Limitaciones y cuidado metodológico
14. Tabla final de mercados activos
15. Qué aporta la metodología DataGastro
```

Cada sección central sigue el patrón:

```text
Pregunta
Respuesta:
[Gráfico / mapa / tabla principal]
Cuidado metodológico:
```

## 4. Paleta visual

- **Azul tinta** (`#1f3b5b` / `#365f91`) como color base institucional.
- **Naranja** (`#e07b2e`) como color de acento (KPIs destacados, barras principales).
- Grises neutros para tablas y texto secundario. Fondo blanco.
- Banda oscura en portada y footer institucional ("DataGastro · Diego Aleman").

## 5. Estilo de gráficos

- Barras limpias, sin 3D, con valor numérico sobre cada barra.
- Una idea por gráfico; títulos en oración.
- No depender solo del color: incluir etiquetas y leyenda.
- Mapas: puntos por tipo con leyenda; ubicación **aproximada por barrio**.

## 6. KPIs (cards del resumen ejecutivo)

```text
13  mercados gastronómicos activos identificados
11  de sede fija  ·  2  itinerantes
13  multifuente (respaldo cruzado)
12  con respaldo documental alto
6   comunas con presencia
3   espacios relevantes no contabilizados (en revisión)
```

## 7. Regla de lenguaje prudente

- Usar: "activos identificados", "relevamiento documental", "padrón candidato", "respaldo
  documental", "señal operativa no oficial", "pendiente de validación territorial".
- Evitar como headline: "confirmados", "censo", "padrón oficial", "todos los mercados".

## 8. Regla de tipología primaria (sin doble conteo)

Un `tipo_primario` por mercado. Suma exacta = 13:

```text
mercado_historico ............ 3
mercado_barrial_alimentario .. 1
food_hall .................... 2
patio_gastronomico ........... 4
mercado_de_productores ....... 2
feria_gastronomica ........... 1
TOTAL ........................ 13
```

`es_itinerante` (atributo): 2 (Buenos Aires Market, Sabe la Tierra). `perfil_productores`
(atributo): 3 (Bonpland, Sabe la Tierra, Buenos Aires Market).

## 9. Regla de multifuente / respaldo documental

Tipos de fuente por mercado: `fuente_oficial_gcba_turismo`, `sitio_propio`,
`google_places_operational`, `documental_prensa`, `fuente_interna_sanitizada`. Se cuenta
`cantidad_tipos_fuente` y `es_multifuente` (≥2 tipos). Niveles:

```text
alto_documental  : 3+ tipos, incluyendo al menos una oficial/sitio propio o Google operativo
medio_documental : 2 tipos
basico_documental: 1 tipo
a_validar        : señales contradictorias o falta de estado actual (p. ej. casos en revisión)
```

**Aclaración:** es **respaldo documental**, no "confianza alta territorial". La validación en
terreno sigue pendiente.

## 10. Outputs a generar (base V4)

```text
outputs/mercados_caba/sanitized/mercados_gastronomicos_activos_v4.csv
outputs/mercados_caba/sanitized/mercados_gastronomicos_no_activos_v4.csv
outputs/mercados_caba/sanitized/indicadores_mercados_gastronomicos_v4.csv
outputs/mercados_caba/sanitized/respaldo_fuentes_mercados_v4.csv
outputs/mercados_caba/sanitized/tipologias_mercados_v4.csv
outputs/mercados_caba/sanitized/decisiones_que_permite_tomar_v4.csv
outputs/mercados_caba/sanitized/referencias_documentales_visibles_v4.csv
```

El informe V4 (markdown + PDF con diseño) y el pack entregable se generan en una etapa posterior,
a partir de esta base y esta especificación.
