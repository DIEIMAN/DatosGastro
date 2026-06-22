# DataGastro — Diagnóstico territorial gastronómico

## Casas de pastas en la Ciudad de Buenos Aires

**Padrón candidato depurado y lectura territorial del rubro**

_Análisis y desarrollo: Diego Aleman_

Este informe integra registro oficial, fuentes abiertas, señales operativas y revisión manual para aproximar un universo operativo probable de casas de pastas en CABA. El resultado no constituye un censo definitivo ni reemplaza al registro oficial: funciona como base analítica para orientar validaciones y decisiones territoriales.

> Tras una revisión manual de los casos dudosos, el padrón candidato depurado queda conformado por **254** establecimientos posibles, combinando el registro administrativo oficial (AGC / F02), el relevamiento abierto auxiliar (OpenStreetMap) y una señal operativa no oficial (Google Places). No es un padrón oficial ni un censo definitivo: es una base analítica para validación territorial.

## Indicadores

- **254** candidatos únicos · **173** independientes / de barrio · **81** en cadenas · **53** multifuente · **252** georreferenciados.

_252 de los 254 candidatos cuentan con coordenadas suficientes para su ubicación puntual; los 2 restantes integran el conteo general pero no se grafican._

## 1. ¿Qué universo permite ver el cruce de fuentes?

254 candidatos únicos. No es un padrón oficial ni un censo definitivo: es una base analítica para validación territorial.

## 2. ¿Por qué el registro oficial no alcanza?

| Fuente | Naturaleza | Candidatos | Qué puede / no puede afirmar |
|---|---|---|---|
| AGC / F02 | Registro administrativo **oficial** | 11 | Habilitaciones; **no implica local activo** |
| OpenStreetMap | **Abierta auxiliar** | 145 | Cobertura territorial; **no oficial** |
| Google Places | **Operativa no oficial** | 150 | Visibilidad comercial; **no gubernamental** |
| Padrón depurado | **Padrón candidato** | 254 | Unión deduplicada + revisión manual |

_Los conteos corresponden al padrón integrado ya consolidado; no representan resultados brutos de búsqueda._

## 3. ¿Dónde se concentran?

- **Comunas (cantidad):** 13 (33), 14 (30), 12 (24), 5 (23), 6 (23).
- **Barrios (cantidad):** Palermo (30), Caballito (23), Belgrano (22), Recoleta (21), Villa Urquiza (19).

## 4. ¿Qué cambia con la densidad por km²?

- **Densidad comuna (cand./km²):** 5 (3.45), 6 (3.36), 2 (3.26), 13 (2.22), 14 (1.88).
- **Densidad barrio (cand./km²):** Almagro (4.20), Colegiales (3.49), Villa Urquiza (3.49), Caballito (3.36), Recoleta (3.26). No es densidad por habitante; el ranking difiere del de cantidad absoluta.

## 5. ¿Qué barrios son polos?

Palermo (30), Caballito (23), Belgrano (22) encabezan el ranking. Mapas de zoom para Palermo, Caballito, Belgrano.

## 6. ¿Cadenas o casas de barrio?

> En el universo candidato predominan las casas independientes y de escala barrial (173 de 254; 81 en cadenas).

## 7. Principales cadenas (control de cobertura)

LA JUVENIL (28), MULTIPASTA (7), CAPRIZZI (4), MASTER PASTAS / PASTAS MASTER (2), MILENA PASTAS ARTESANALES (2), PASTAS MAZZEO (2), RAVIOLON (2).

## 8. Núcleo de mayor respaldo cruzado

- 53 candidatos multifuente (Google + OSM): base más sólida. Combinaciones: solo OSM 92 · solo Google 90 · Google+OSM 53 · solo AGC 11 · recall complementario (búsqueda adicional de cobertura) 7 · documental 1. Aparecer en más de una fuente aumenta la probabilidad de existencia, pero no la confirma: no reemplaza la validación.

## 9. ¿Qué aportó la revisión manual?

La revisión manual permitió depurar los casos dudosos detectados por el cruce de fuentes.

- Se confirmaron 27 candidatos y se excluyeron 15 casos (restaurantes, locales cerrados, registros genéricos o rubros no incluidos).
- Los confirmados se incorporan como candidatos validados en revisión manual.
- Una búsqueda complementaria de cobertura permitió detectar 7 candidatos adicionales, incorporados solo tras revisión y trazabilidad.
- El detalle por caso queda en el anexo metodológico interno.

## 10. ¿Qué aporta esta metodología?

Un método replicable (registro oficial + fuentes abiertas + señal operativa + revisión manual) para otros rubros: pizzerías, heladerías artesanales, cafeterías de especialidad, panaderías, parrillas, casas de empanadas.

## Casos con respaldo documental

Además del análisis territorial, se identificaron establecimientos con fuentes sobre trayectoria, origen familiar o antigüedad. No es un ranking histórico exhaustivo, sino ejemplos verificables dentro del rubro.

- **Pastas Amelia** — Boedo · 1948 — fábrica artesanal vinculada a la familia Palazzo (fusilis al fierrito).
- **La Hispano Americana** — San Telmo · más de medio siglo — casa de pastas asociada a inmigrantes gallegos y continuidad familiar.
- **La Juvenil** — Colegiales · 1959 — marca familiar con varias generaciones y expansión territorial.
- **Pastas Bayo** — Belgrano · 1978 — casa de pastas familiar con permanencia en la misma dirección.

_Se incluyen por contar con fuentes documentales identificables (prensa nacional y sitios oficiales); no agotan la historia del rubro ni prueban por sí solos cuál es la casa de pastas más antigua de la Ciudad. Detalle de fuentes en anexo metodológico interno._

## ¿Para qué sirve este diagnóstico?

Dimensionar el universo operativo probable por comuna y barrio; identificar polos territoriales; distinguir cadenas de casas independientes; señalar el núcleo de mayor respaldo cruzado como base más sólida. Es una base analítica candidata, no oficial: orienta el trabajo territorial y no reemplaza al registro oficial.

## Limitaciones

- Sigue siendo padrón candidato; no reemplaza al registro oficial; no implica local activo confirmado por fuente oficial. Google/OSM no son fuentes oficiales. Puede haber locales cerrados o faltantes. La densidad se expresa por superficie; una etapa posterior puede incorporar población para estimar cobertura relativa por habitante. La revisión manual de escritorio mejora la depuración, pero no reemplaza la verificación territorial final si el informe se usa públicamente.
