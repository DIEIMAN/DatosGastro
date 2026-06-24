# Mercados gastronómicos de la Ciudad de Buenos Aires — Visión y objetivo

> Etapa de **diseño y preparación**. No se ejecutaron requests, no se usaron API keys, no se
> descargó nada, no se inventaron datos. No se modificó DataGastro V1 ni V2 (solo lectura de
> fuentes locales) ni casas de pastas.

> **Corrección de alcance (2026-06-23):** el informe trata exclusivamente sobre **mercados
> gastronómicos** de CABA (food halls, mercados de productores/alimentos, ferias gastronómicas,
> mercados barriales con foco alimentario, mercados turísticos gastronómicos, etc.). **No** es un
> relevamiento de mercados en general. Se excluyen mercados de pulgas, antigüedades, ropa,
> artesanías sin eje gastronómico, shoppings, galerías comerciales, supermercados y mayoristas
> sin experiencia gastronómica.

## 1. Objetivo

Investigar, ordenar y producir una **primera versión de informe ejecutivo** sobre los **mercados
gastronómicos** de CABA —públicos, privados o mixtos—, combinando fuentes públicas, fuentes
internas disponibles y la metodología DataGastro (padrón candidato, niveles de confianza,
separación de fuentes, lenguaje prudente).

No es un censo ni un padrón oficial: es un **relevamiento candidato** sujeto a validación.

## 2. Pregunta central

```text
¿Qué mercados gastronómicos existen en CABA, qué tipo de gestión tienen, qué oferta poseen,
qué horarios manejan, a qué público apuntan y qué rol cumplen en el ecosistema gastronómico
de la Ciudad?
```

Preguntas derivadas: ¿cuáles son públicos, privados o mixtos?; ¿qué oferta gastronómica y
alimentaria tienen?; ¿qué horarios y días manejan?; ¿qué público objetivo atienden (barrial /
turístico)?; ¿qué rol cumplen en el ecosistema gastronómico y en políticas/circuitos públicos?;
¿qué información falta validar?

## 3. Alcance (qué entra)

Espacios donde la **gastronomía, los alimentos, las bebidas o la experiencia gastronómica son el
eje principal**:

- mercados gastronómicos públicos, privados o mixtos;
- food halls;
- mercados de productores / de alimentos;
- ferias gastronómicas relevantes;
- mercados barriales con foco alimentario/gastronómico;
- mercados turísticos con identidad gastronómica;
- espacios tipo mercado donde la comida/bebida/productos alimentarios son centrales.

Ver tipología en `01_taxonomia_mercados.md`.

### Criterio de inclusión (al menos uno)

```text
la gastronomía es el eje principal del espacio
hay puestos gastronómicos o alimentarios como componente central
funciona como mercado de comida, productores, alimentos o bebidas
tiene relevancia turística o barrial asociada a la oferta gastronómica
forma parte de políticas, eventos o circuitos gastronómicos
es un mercado tradicional con oferta alimentaria significativa
```

## 4. Fuera de alcance (qué NO entra)

Se **excluye** o se marca `fuera_de_alcance_no_gastronomico`:

```text
mercados de pulgas
mercados de antigüedades
ferias de ropa
ferias de artesanías sin eje gastronómico
galerías comerciales sin foco gastronómico
shoppings
supermercados comunes
mayoristas sin experiencia gastronómica
ferias barriales genéricas si no tienen foco alimentario/gastronómico relevante
espacios comerciales donde la gastronomía sea accesoria y no central
```

### Criterio de exclusión

```text
la comida es secundaria
la categoría principal es ropa, antigüedades, artesanías, diseño, decoración o pulgas
es solo un shopping o galería comercial
es solo un supermercado o almacén individual
es un restaurante individual fuera de un mercado
es una feria general sin foco alimentario claro
```

**Regla:** no excluir automáticamente un espacio dudoso. Si el peso de lo gastronómico no está
claro, se marca `dudoso_pendiente_revision` y se justifica; recién se descarta como
`fuera_de_alcance_no_gastronomico` con evidencia de que la gastronomía es accesoria o inexistente.

## 5. Principios metodológicos (heredados de DataGastro)

- **No inventar.** Campo sin dato confiable → `pendiente`.
- **Separar fuentes.** Oficiales (GCBA/BA Data), externas (OSM/Google/prensa), internas (DGDGAS).
  No mezclar como un universo único sin declarar la fuente.
- **Nivel de confianza explícito** por ficha (ver `03_metodologia_y_niveles_confianza.md`).
- **Privacidad.** Sin teléfonos, emails, referentes, CUIT ni links privados de Drive. Material
  interno/crudo en carpetas gitignored; solo se publican agregados sanitizados.
- **Habilitación/registro ≠ actividad confirmada.** El estado operativo se valida aparte.

## 6. Estado de partida (lo que ya hay localmente)

De fuentes locales **públicas** (V1 / F03, solo lectura) se detectan candidatos con foco
alimentario: 6 Centros de Abastecimiento Municipal + Mercado Comunitario Primera Junta, todos
marcados `revisar_foco_gastronomico` (son mercados de abasto; falta verificar si tienen oferta
gastronómica/de comida o son solo abastecimiento). El **Mercado de las Pulgas** quedó marcado
`fuera_de_alcance_no_gastronomico` (eje antigüedades/usados). Los mercados gastronómicos
emblemáticos (food halls, mercados de productores) **no** están en datos locales: se relevan con
fuentes externas (Turismo BA, sitios oficiales, OSM, Google, prensa) en etapas siguientes. No se
anticipan nombres sin fuente. Ver `outputs/mercados_caba/sanitized/mercados_candidatos_iniciales.csv`.

## 7. Entregable final

Un informe ejecutivo institucional (estructura en `09_estructura_informe_final.md`) con mapa,
tipología gastronómica, gestión, oferta, horarios, público, potencial turístico/político y
brechas de información, acotado a mercados gastronómicos.

## 8. Qué NO hace esta etapa

- No completa el universo de mercados gastronómicos.
- No ejecuta Google Places, OSM/Overpass ni Perplexity.
- No descarga fuentes nuevas.
- No expone datos sensibles ni versiona crudos internos.
