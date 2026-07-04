# Decisiones humanas post Tanda 1 — Google Places (PolosGastro, Fase 11)

Fecha: 2026-07-02. Documento interno. Registra decisiones de criterio (no automáticas) surgidas de
la corrida real de Tanda 1. Insumo para el Borrador 4 como **decisiones humanas pendientes**, no
como descartes.

## Principio general

La capa Google Places es una **fuente auxiliar de geolocalización y de vigencia operativa**. No
reescribe el universo semilla ni elimina locales por sí sola. Un `CLOSED_PERMANENTLY` de Google es
una **señal a validar**, no una baja automática.

**Tanda 1 no elimina ningún local de la semilla.**

## Casos

### Osaka (LG006)

- Google devolvió **"Osaka" correcto** (japanese_restaurant), **no** el sustituto erróneo "Osaki"
  de la Tanda 1 anterior.
- `business_status = CLOSED_PERMANENTLY`.
- **Decisión**: mantener en la semilla como **referencia con vigencia no confirmada / no mapeable
  hasta validar**. No mostrar como local activo en mapa público hasta verificar vigencia por otra
  vía.

### Aldo's (LG008)

- Google devolvió **"Aldos Restaurante" correcto** (restaurant), **no** el sustituto erróneo
  "Artemisia".
- `business_status = CLOSED_PERMANENTLY`.
- **Decisión**: igual que Osaka — mantener en semilla como **referencia con vigencia no confirmada /
  no mapeable hasta validar**.

### Oporto (LG010)

- Google devolvió **"Oporto Almacén"** (gastronómico), **no** "Somos OP" (la aseguradora de la
  Tanda 1 anterior). Operativo.
- Pero la dirección cae en **Colegiales** (11 de Septiembre 4152), no en Palermo Soho/Hollywood.
- **Decisión**: mantener en semilla en **revisión de zona/sucursal**. Confirmar si corresponde a la
  referencia de Palermo o a otra sede antes de mapear en el polo.

## Qué NO se hace

- No se borra Osaka, Aldo's ni Oporto de la semilla.
- No se reescribe el universo semilla con el resultado automático de Google.
- No se marca ninguno como baja: quedan como decisiones humanas para el Borrador 4.

## Sustitutos erróneos: confirmado que no reaparecen

Las queries corregidas de Fase 11 evitaron los 3 falsos matches de la Tanda 1 anterior: **Osaki,
Artemisia y Somos OP no reaparecieron**. Ver `QA_REPILOTO_TANDA1_REAL_GOOGLE_PLACES.md`.
