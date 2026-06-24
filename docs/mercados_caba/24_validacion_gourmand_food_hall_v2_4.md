# Mercados gastronómicos CABA — Validación de Gourmand Food Hall (V2.4)

> Mini-etapa enfocada **únicamente** en Gourmand Food Hall (Patio Bullrich). No altera el resto
> del informe. Fecha: 2026-06-24. Sin exponer place_id, teléfonos, emails ni datos sensibles.

## 1. Objeto

Evaluar si **Gourmand Food Hall** (posible omitido de alta prioridad) debe sumarse al universo
**activo confirmado para conteo** o mantenerse como posible omitido pendiente.

## 2. Datos del espacio

- **Nombre:** Gourmand Food Hall.
- **Ubicación:** Patio Bullrich, Nivel 1 (Posadas 1245 / Av. del Libertador 750), Retiro (Comuna 1).
- **Tipo:** food hall (curado, con lógica de mercado).
- **Gestión:** privada.
- **Horarios:** Domingo a jueves 10–23; viernes y sábados 10–01.
- **Apertura:** diciembre 2016 (presentado como "el primer food hall de Argentina").

## 3. Fuentes revisadas

**Internas del proyecto (ya procesadas):**
- `google_places_posibles_omitidos_v2.csv` y `mercados_gastronomicos_posibles_omitidos_v2_2.csv`
  (detectado por Google, prioridad alta).
- Staging interno de Google (lectura local, sin exportar): **`OPERATIONAL`**, rating 4.2,
  **2.125 reseñas**, web presente. (No se exporta place_id ni dirección individual.)

**Búsqueda web acotada (solo Gourmand):**
- **Sitio oficial:** gourmandfoodhall.com.
- **Prensa:** El Cronista (2016), LA NACION, El Economista, Gastronomia.com Argentina, Revista
  Mercado, Lucullus.
- **Operación reciente:** Google Places, Yelp ("Updated May 2026"), Tripadvisor (2026).

## 4. Criterios de inclusión (los 5 se cumplen)

| # | Criterio | ¿Cumple? | Evidencia |
|---|---|---|---|
| 1 | Identidad propia tipo food hall | **Sí** | sitio e Instagram propios; "primer food hall de Argentina" |
| 2 | Operación actual verificable | **Sí** | Google `OPERATIONAL`, 2.125 reseñas; Yelp/Tripadvisor 2026 |
| 3 | Más de una propuesta/local | **Sí** | 10+ paradas (Oyster Bar, Bistró, Italian, Wine Bar, Birrería, etc.) |
| 4 | Fuente no vieja ni genérica | **Sí** | sitio oficial + prensa + actividad reciente multifuente |
| 5 | No es patio de comidas común | **Sí** | food hall curado con lógica de mercado ("comer, comprar y aprender") |

Matriz machine-readable: `validacion_gourmand_food_hall_v2_4.csv`.

## 5. Fuente: oficial vs. prensa

Tiene **sitio oficial propio** (C2) **y** respaldo de **prensa multifuente** (C3) **y** señal
operativa de Google (alta cantidad de reseñas). No depende de una sola mención.

## 6. Recomendación

**Sumar Gourmand Food Hall al universo activo confirmado** como `food_hall` privado activo. La
evidencia es **suficiente y documentada**. Detalle del ajuste de conteo en
`25_ajuste_conteo_gourmand_v2_4.md`.

## 7. Salvedad

Está **dentro de Patio Bullrich** (shopping), pero —igual que Mercat Caballito dentro de su
shopping— **tiene entidad propia de food hall** y no es un patio de comidas común; por eso entra en
alcance. Conserva su ficha y queda sujeto a futura validación territorial como el resto.

## 8. Privacidad

En las fuentes aparecían teléfono y email de reservas: **no se copiaron** a ningún output. Las URLs
registradas son públicas (sitio oficial y medios), sin place_id ni datos personales.
