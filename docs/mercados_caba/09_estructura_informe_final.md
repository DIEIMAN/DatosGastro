# Mercados gastronómicos CABA — Estructura del informe ejecutivo final

> Esqueleto del entregable sobre **mercados gastronómicos** de CABA. Tono institucional y prudente
> (skill `datagastro-informes`): separar hallazgos de límites, sin lenguaje de IA, agregados sin
> datos personales.

## Estructura

1. **Portada** — título ("Mercados gastronómicos de CABA"), fecha, autoría institucional, nota de
   alcance ("relevamiento candidato, no censo; solo mercados gastronómicos").
2. **Nota de alcance** — qué se entiende por mercado gastronómico (criterios de inclusión) y qué
   queda explícitamente fuera (pulgas, antigüedades, ropa, shoppings, supermercados, mayoristas
   sin experiencia gastronómica).
3. **Resumen ejecutivo** — qué se relevó, cuántos mercados gastronómicos candidatos por tipo,
   principales hallazgos y brechas, en orden de magnitud.
4. **Mapa de mercados gastronómicos de CABA** — distribución territorial (agregada por
   barrio/comuna); sin exponer direcciones individuales innecesarias.
5. **Tipología de mercados gastronómicos** — categorías de la taxonomía con conteos y ejemplos.
6. **Públicos vs privados vs mixtos** — distribución por gestión y lectura.
7. **Oferta gastronómica y alimentaria** — qué venden; comida preparada vs productos vs oferta
   accesoria; presencia de productores y de locales gastronómicos.
8. **Horarios y funcionamiento** — permanentes vs temporales; cobertura de días/horarios.
9. **Público objetivo** — barrial / turístico / mixto.
10. **Mercados gastronómicos con potencial turístico** — perfil turístico alto, con cautela y
    fuente.
11. **Mercados barriales / identidad gastronómica local** — rol identitario y de proximidad.
12. **Relación con políticas y circuitos gastronómicos** — vínculo con eventos, programas o
    circuitos (p. ej. BA Capital Gastronómica), como hipótesis a validar.
13. **Oportunidades de política pública** — desarrollo económico, turismo gastronómico, identidad
    barrial; hipótesis a validar, no conclusiones cerradas.
14. **Brechas de información** — qué falta validar (foco gastronómico, horarios, oferta, gestión,
    estado); porcentaje de campos `pendiente` y de candidatos `revisar_foco_gastronomico`.
15. **Anexo metodológico** — fuentes, niveles de confianza, taxonomía gastronómica, criterios de
    inclusión/exclusión, candidatos fuera de alcance, limitaciones, fecha de corte; declaración de
    privacidad.

## Reglas de redacción

- Cada cifra acompañada de fuente, fecha y limitación.
- Conteos **por nivel de confianza**, no como total plano.
- Distinguir **volumen** de **densidad**; declarar sesgos de cobertura (turístico, céntrico).
- Lenguaje: "relevamiento candidato", "universo probable", "registro oficial", "señal operativa
  no oficial", "validación posterior". Evitar "censo", "padrón oficial", "todos los mercados".

## Salidas asociadas

- Tablas/figuras desde `outputs/mercados_caba/sanitized/` (agregados, sin PII).
- Versión PDF/print: se genera a `outputs/mercados_caba/` (los `.pdf`/`.zip` quedan gitignored).
