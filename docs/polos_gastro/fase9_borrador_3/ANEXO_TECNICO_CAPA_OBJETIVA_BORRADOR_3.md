# Anexo tecnico - Capa objetiva de contexto (Borrador 3)

Fecha: 2026-07-01. Documento interno. Anexo tecnico, no cuerpo principal. No es ranking. No se uso
Google Places.

Este anexo incorpora la capa objetiva de la Fase 8 fuerte como contexto tecnico del Borrador 3. La
capa **no** delimita polos, **no** mide densidad real, **no** valida vigencia y **no** ordena polos
por importancia.

## 1. Metodologia resumida

- **Fuentes.** F01 oferta y establecimientos gastronomicos (2823 registros) y F02 habilitaciones
  gastronomicas historicas (44169 registros), ambas locales del pipeline y en solo lectura. Apoyo de
  la dimension de ubicacion para comuna. No hubo descargas nuevas.
- **Agregacion.** Oferta registrada por barrio y comuna (F01). Habilitaciones por comuna (F02). La
  lectura barrial de F02 no se usa porque 44099 registros quedan sin barrio util.
- **Indice de senal objetiva.** Indicador interno de 0 a 100. Por barrio, normaliza la oferta
  registrada F01 contra el maximo barrial observado. Por comuna, promedia dos senales normalizadas
  (F01 y F02). Expresa presencia relativa en las fuentes disponibles, nada mas.

## 2. Como leer la tabla interpretativa (no ranking)

La tabla del Borrador 3
(`outputs/polos_gastro/fase9_borrador_3/tablas/tabla_polos_para_informe_borrador_3.csv`) conserva el
orden del Borrador 2 y describe la senal de forma cualitativa. El nivel (alto / medio / bajo / no
calculable) se acompana siempre de la lectura prudente y de la limitacion territorial. No se ordena
por indice y no se publica el indice numerico de forma aislada.

## 3. Casos de senal alta

La senal objetiva **acompana** la lectura documental (no la valida por si sola):

| Caso | Estado documental | Lectura prudente | Limitacion territorial |
| --- | --- | --- | --- |
| Palermo Soho | fuerte | La senal acompana la lectura documental. | Palermo como barrio aproxima el area nucleo, no el subpolo. |
| Palermo Hollywood | fuerte | La senal acompana la lectura documental. | Palermo como barrio aproxima el area nucleo, no el subpolo. |
| Las Canitas | fuerte | La senal acompana la lectura documental. | Palermo como barrio aproxima el area nucleo, no el subpolo. |
| Recoleta | fuerte | La senal acompana la lectura documental. | Coincide con barrio de referencia, pero no mide vigencia. |

Advertencia: la senal alta del barrio Palermo **no** valida cada subpolo (Soho, Hollywood, Las
Canitas). Es una senal del barrio contenedor.

## 4. Casos de senal media

Senal intermedia con **alta cautela territorial**; el numero no debe citarse sin su limitacion:

| Caso | Estado documental | Limitacion territorial |
| --- | --- | --- |
| Microcentro / Centro | media | Area central multibarrial; el promedio no delimita Microcentro. |
| Abasto | media | Balvanera como barrio no separa Abasto de Corrientes. |

## 5. Casos no calculables

Corredores y areas sin delimitacion territorial previa. No se les asigna senal; se mantienen como no
calculables hasta contar con un recorte territorial (aunque sea textual):

| Caso | Tipo territorial | Limitacion territorial |
| --- | --- | --- |
| Costanera Norte | area costera | Corredor costero multibarrial; no asignar a un barrio unico. |
| Avenida Corrientes | corredor | Corredor cultural-gastronomico sin tramo operativo cerrado. |
| DoHo / Donado-Holmberg | corredor | Corredor entre Villa Urquiza y Belgrano R; requiere delimitacion fina. |
| Avenida Caseros / Barracas | corredor | Solapamiento San Telmo/Barracas; requiere recorte territorial. |
| Avenida Boedo | corredor | Sin delimitacion operativa; el barrio Boedo no valida el eje. |
| Federico Lacroze / Libertador a Cabildo | corredor | Sin delimitacion operativa ni evidencia suficiente. |
| Villa Pueyrredon / Av. San Martin | corredor | El barrio completo no valida Avenida San Martin. |

Los casos restantes del universo (San Telmo, Puerto Madero, Barrio Chino, Chacarita, Monserrat,
Retiro y varios emergentes/anexos) presentan senal **baja**: la fuente muestra presencia en el
barrio de referencia, pero no alcanza para validar subpolos, corredores o recortes finos.

## 6. Control de riesgo metodologico

El cuadrante "evidencia documental debil o pendiente + senal objetiva alta" quedo **vacio (sin
registros)**. No existe ningun caso debil o pendiente al que la senal objetiva empuje hacia arriba.
Se deja constancia porque es el cuadrante de mayor riesgo de conclusion indebida: una senal barrial
alta no convierte automaticamente un caso en polo.

## 7. Advertencias obligatorias

Toda cita de esta capa, en cualquier version futura, debe incluir:

- La capa es **contexto**, no ranking ni prueba de densidad.
- No mide locales activos ni vigencia operativa.
- La senal de un barrio **no** valida subpolos ni corredores.
- Los corredores no calculables se mantienen como no calculables.
- Las habilitaciones (F02) y la oferta registrada (F01) **no** son "locales activos".
- No se uso Google Places ni plataformas privadas.
- Los cambios de clasificacion requieren revision humana; no son automaticos.
