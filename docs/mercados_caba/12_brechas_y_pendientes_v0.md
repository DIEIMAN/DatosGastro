# Mercados gastronómicos CABA — Brechas y pendientes v0

> Qué falta validar tras el relevamiento v0 (2026-06-23) y cómo seguir, sin ejecutar integraciones
> pagas ni exponer datos sensibles.

## 1. Horarios pendientes

Falta horario confiable (fuente oficial o sitio del mercado) en, al menos:
Mercado de Belgrano, Mercado del Progreso, Mercado Bonpland, El Galpón, Smart Plaza Parque
Patricios, Patio Costanera Norte, Patio Rodrigo Bueno, Mercado San Nicolás, Buenos Aires Market y
Sabe la Tierra (itinerantes: horario por sede/fecha). En **San Telmo** las fuentes difieren
(~9–22) y quedó `pendiente_fuentes_difieren`.

## 2. Gestión pendiente

Confirmar gestión y modelo de concesión (público / privado / mixto) en: San Telmo, Belgrano,
Carruajes, Bonpland, Costanera Norte, San Nicolás (marcados `mixta` tentativa) y precisar si
Progreso es 100% privado. Validar con normativa, pliego de concesión o sitio oficial.

## 3. Oferta pendiente

- Detallar **oferta gastronómica vs alimentaria** y **cantidad/tipo de puestos** en los patios
  públicos (Smart Plaza, Costanera Norte, Rodrigo Bueno) y en Bonpland / El Galpón / San Nicolás.
- Confirmar **~191 puestos** del Mercado del Progreso (hoy C4, Wikipedia).
- Confirmar presencia de **productores** en Mercat Villa Crespo y Mercat Caballito (declarada en
  prensa, falta fuente oficial).

## 4. Candidatos a verificar (revisión de foco gastronómico)

- **4 CAM + Mercado Comunitario Primera Junta**: ¿tienen oferta gastronómica/de comida o son solo
  abasto? → confirmar para incluir como `mercado_barrial_alimentario` o dejar fuera.
- **Mercado M1 (Chacarita)**: confirmar naturaleza.
- **Barrio Chino**: definir si entra como unidad, como zona, o queda fuera.
- **Los Arcos del Rosedal / "Patio de los Arcos"**: desambiguar de Distrito Arcos (outlet) y
  decidir si es mercado/patio o conjunto de restaurantes.

## 5. Fuentes a pedir internamente (DGDGAS / GCBA)

- Listado/normativa oficial de **mercados y centros de abastecimiento municipales** (estado,
  dirección, concesión).
- Programa **BA Capital Gastronómica**: mercados y patios incluidos, eventos y circuitos.
- Material interno DGDGAS sobre **"PATIO Y MERCADOS"** y eventos en mercados (solo agregados, sin
  PII) — referenciado en `outputs/v2/sanitized/` (inventario y cobertura DGDGAS).
- Calendario oficial de **ferias gastronómicas y de productores** (BA Market, Sabe la Tierra,
  mercados itinerantes) con sedes en CABA.

## 6. Próximos pasos sugeridos

1. **Documental (sin costo):** completar fichas con sitios oficiales de cada mercado y normativa
   GCBA; cerrar horarios/gestión/puestos. Resolver los 8 pendientes de revisión.
2. **OSM (sin costo, con aprobación):** contrastar geometría y cobertura (`amenity=food_court`,
   `amenity=marketplace` con señal gastronómica) según `08_plan_osm_mercados.md`.
3. **Google Places (solo con aprobación + presupuesto + topes):** validar `businessStatus`
   (p. ej. confirmar cierres como Carruajes) y ampliar cobertura, según
   `07_plan_google_places_mercados.md`. **No** ejecutado en esta etapa.
4. **Validación territorial posterior:** confirmar estado, oferta y horarios en terreno (sube a
   confianza alta).
5. **Mantener separados** los universos (oficial / sitio del mercado / prensa) y no sumar
   pendientes ni fuera de alcance al total confirmado.

## 7. Límites declarados

Relevamiento candidato con fuentes públicas; sesgo hacia mercados **emblemáticos y turísticos**
(mejor documentados) frente a mercados barriales de abasto (peor cubiertos). Registro/listado
oficial ≠ operación confirmada. Cifras en orden de magnitud, sujetas a validación.
