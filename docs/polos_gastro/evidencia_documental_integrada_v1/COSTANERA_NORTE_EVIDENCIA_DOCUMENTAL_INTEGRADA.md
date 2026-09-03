# Costanera Norte — evidencia documental integrada V1

**Polo:** Polo Gastronómico Costanera Norte (único, multiparte, discontinuo).
**Fecha:** 2026-07-11.
**IDs de evidencia:** CN-01…CN-16 (heredados de Grok) + CN-INF01/CN-INF02 + CN-DEC01/CN-DEC02.
**Estado:** integrado; listo para contraste espacial. Estatus editorial: exploratorio
(DEC-05/DEC-06: anexo, no lámina principal).

---

## 1. Decisión cerrada (no reabrir)

Un único **Polo Gastronómico Costanera Norte** con **cuatro componentes discontinuos**.
La discontinuidad forma parte de la lógica territorial del polo y puede responder a:
infraestructura, Aeroparque, parques, clubes, concesiones, predios recreativos y tramos
sin oferta gastronómica.

**`CN_C02` debe incluirse como cuarto componente** (decisión de Diego, 2026-07-11). El
diagnóstico v2.1 lo trataba como "contexto secundario" por depender 100 % de Places; la
decisión lo incorpora y traslada esa debilidad de fuente al apartado metodológico.

**Prohibido:** afirmar informalidad, ilegalidad o falta de habilitación de
establecimientos concretos sin evidencia oficial. **Permitido como hipótesis:**
subregistro administrativo; diferencias de categoría; puestos; carritos; concesiones;
oferta móvil o registrada bajo otro domicilio.

---

## 2. Síntesis documental integrada

Turismo BA documenta la identidad pública de la zona: **restaurantes clásicos y
carritos** frente al río (CN-01, ALTA). La **Ley 5.961/2018** crea el Distrito Joven –
Costanera Norte, autoriza concesiones de dominio público por hasta diez años y prevé la
integración paisajística con el Parque de la Memoria y el Parque Natural de Ciudad
Universitaria, además de obras de cabecera del Aeroparque (CN-04/05/06): ese marco legal
**explica los vacíos** como estructura, no como defecto del dato. La regularización de
carritos está documentada en 2013 (comodato, gas, canon; CN-07) y 2017 (bienes del GCBA
en comodato por cinco años; CN-08). La prensa de 2026 describe la transformación del
Sector 1 hacia salones y locales de concesión (CN-11/12). Completan la lectura el patio
oficial de containers en Av. Rafael Obligado 7010 (CN-02/03) y los predios Costa
Salguero–Punta Carrasco (CN-13/14).

Nota de linaje: el barrido de Perplexity (2026-06-29) no había encontrado evidencia
verificable para Costanera Norte; el paquete de Grok (2026-07-11) cerró ese vacío con
fuentes institucionales, legales y periodísticas. Este contraste queda como ejemplo de
por qué la ausencia de evidencia en una pasada no equivale a inexistencia del polo.

### Cuatro componentes documentales

| # | Denominación descriptiva (no comercial) | Respaldo | IDs |
|---|---|---|---|
| 1 | Corredor de concesiones ribereñas gastronómico-recreativas (Distrito Joven / Sector 1) | Alto | CN-04, CN-11, CN-12, CN-13 |
| 2 | Franja de puestos y carritos de parrilla | Alto histórico / medio actual | CN-01, CN-07, CN-08, CN-09, CN-10, CN-15 |
| 3 | Patio gastronómico de puestos en containers (Obligado 7010) | Alto oficial | CN-02, CN-03 |
| 4 | Predios de eventos y usos mixtos Costa Salguero–Punta Carrasco | Medio-alto pertenencia / medio oferta | CN-13, CN-14 |

### Cruce con el pipeline híbrido v2.1

- Universo técnico: **72 puntos**; 71 asignados a **cuatro componentes técnicos**:
  `CN_C01` (21), `CN_C02` (11), `CN_C03` (29), `CN_C04` (10); 1 registro quedó como ruido
  de borde (dependencia del contenedor).
- `CN_C02`: 0 registros F01/F02 y 100 % Places → por decisión de Diego se incluye como
  cuarto componente; su composición de fuente se explica en método (hipótesis
  tipológica: puestos, carritos, concesiones, oferta móvil o registrada bajo otro
  domicilio — sin afirmar ilegalidad).
- Dependencia global de Places 93,1 % (solo 5 registros F01/F02 sobre 72): fundamento del
  estatus exploratorio (DEC-06). La estabilidad geométrica es alta (bootstrap por
  bloques 0,77) pero no compensa la debilidad de fuente.
- El emparejamiento componente documental ↔ geometría técnica **no se presupone 1:1**:
  es la tarea de la próxima corrida (ver §5).

---

## 3. Subregistro administrativo — tratamiento

- **Hechos verificados:** carritos como bienes del GCBA en comodato (CN-08);
  regularización 2013 con canon y gas (CN-07); concesión de dominio público (Ley 5.961);
  patio de containers como tipología de predio (CN-02/03).
- **Hipótesis permitidas (metodológicas):** un puesto en comodato o permiso de vía
  pública puede no figurar en padrones de establecimientos fijos (CN-INF01); un
  componente con presencia en fuente externa y baja huella administrativa es compatible
  con tipologías puesto/carrito/evento u oferta registrada bajo otro domicilio (CN-INF02).
- **No publicable:** ilegalidad de un establecimiento concreto; censo actual exacto de
  carritos; equivalencia pin de plataforma = local habilitado.

---

## 4. Uso editorial

- **Publicable:** identidad pública (Turismo BA); marco legal del Distrito Joven;
  regularizaciones documentadas; estructura multiparte discontinua con vacíos
  estructurales; distinción con Costanera Sur.
- **Metodológico:** cuatro componentes documentales ≠ cuatro polígonos oficiales;
  composición de fuentes por componente (`CN_C02` 100 % Places); tipologías
  administrativas; estatus exploratorio declarado una vez (DEC-06).
- **Interno:** hipótesis de subregistro por componente concreto; cualquier conteo de
  puestos activos; nombres de concesionarios y marcas (solo anclas periodísticas).

---

## 5. Qué debe probar el cartógrafo (resumen; detalle en el handoff)

1. Mantener **cuatro componentes**, incluido `CN_C02`; sin conectores, bandas ni buffers
   que sugieran continuidad (DEC-05).
2. **Preservar los vacíos territoriales** (Aeroparque, parques, clubes, predios, tramos
   sin frentes) como parte del resultado.
3. Contrastar cada geometría `CN_C01–CN_C04` con los cuatro componentes documentales y
   clasificar la correspondencia como `EMPAREJADA`, `PARCIAL` o
   `SIN_CORRESPONDENCIA_DOCUMENTAL_DIRECTA`.
4. **La falta de correspondencia perfecta no elimina el componente** (ni el documental ni
   el técnico).
5. Mantener la separación con Costanera Sur.

---

## 6. Vacíos reales

- Emparejamiento formal geometrías ↔ fichas documentales (pendiente espacial; es la
  próxima corrida).
- Censo actual de puestos/carritos activos (no existe fuente oficial actualizada).
- Pliegos completos del BO por espacio del Sector 1 (la prensa resume; no sustituye
  expediente).
- Incorporación de fuentes públicas que reduzcan la dependencia de Places (condición de
  reapertura de DEC-05/06).
