# Decisión post corrida ampliada — Google Places (PolosGastro, Fase 11)

DGDGAS — Dirección General de Desarrollo Gastronómico. Documento interno de decisión. Fecha: 2026-07-02.
Basado en la corrida ampliada (86) y el consolidado total (106). Ver
`QA_CORRIDA_AMPLIADA_GOOGLE_PLACES.md` y `ANEXO_CONSOLIDADO_VIGENCIA_Y_GEOLOCALIZACION.md`.

## Veredicto

**Ya alcanza para empezar el Borrador 4.** La capa Google Places sobre la semilla de Fase 11 está
**completa (106/106)**, sin errores ni incidentes de seguridad. El siguiente paso es **revisión
humana**, no más consultas de API.

## Respuestas puntuales

**¿Tenemos suficientes puntos para armar mapa de revisión?**
Sí. Hay **59 matches razonables o fuertes** (32 fuertes + 27 razonables), todos en CABA, con
lat/lon en el output de revisión visual. Alcanza para un **mapa de revisión interno** (no público).

**¿Cuántos podrían ser mapeables tras revisión humana?**
Hasta **59** (los razonables/fuertes), menos los que la revisión descarte por sede/duplicado. Un
piso conservador realista: **~45–50** puntos mapeables tras validar cadenas y duplicados.

**¿Cuántos quedan fuera por vigencia dudosa?**
**8** cerrados (permanentes: Osaka, Aldo's, Morelia, La Reina Kunti; temporales: Las Pizarras,
Francisca del Fuego, Alo's Café) — no mapear como activos hasta validar.

**¿Qué polos quedaron mejor cubiertos?**
Palermo (12 razonables/19), Recoleta (6/8), Microcentro y Centro (6/7), Villa Crespo (6/9), Belgrano
(6/11), Puerto Madero (5/9), Costanera Norte (5/6).

**¿Qué polos siguen débiles?**
**Abasto (0 razonables)** — sus 6 locales **duplican** los de Av. Corrientes. Chacarita (2/7),
Caballito (2/5), Avenida Caseros/Barracas (2/5), San Telmo (4/8). Débiles por cierres, duplicados o
confianza baja.

**¿Hace falta más Google Places o ya alcanza para Borrador 4?**
**Ya alcanza.** No se recomienda más consulta de Places: la cobertura es total y el cuello de
botella ahora es la validación humana, no el volumen de datos.

**¿Qué decisiones debe consultar Diego con Ale?**
1. **Abasto como subzona/anexo de Av. Corrientes** (respaldado objetivamente por los 6 duplicados).
2. Tratamiento de los **8 cerrados**: conservar en semilla como "vigencia no confirmada", fuera del
   mapa.
3. **11 duplicados**: cuál sede se mapea en cada nombre compartido.
4. **Hitos colectivos** (Mercado de San Telmo, Patio de los Lecheros, El Mercado/Faena): cómo se
   representan (punto de referencia vs local).
5. Casos de **query a corregir** (Pa' Pastar, Chila-categoría, Oporto-zona).
6. Si el **mapa de revisión interno** se arma ya con los ~59 razonables o se espera a cerrar la
   validación.

## Recomendación operativa

1. Cerrar la **revisión humana** (cerrados, duplicados, Abasto, hitos, confianza baja).
2. Armar **mapa de revisión interno** (no público) con los razonables validados.
3. Redactar el **Borrador 4** con la capa auxiliar y las decisiones humanas como anexo.
4. No ejecutar más Google Places salvo casos puntuales de corrección de query, con autorización.

> Nada de esto ejecuta API. Cualquier reconsulta puntual requiere autorización y el mismo doble
> flag `--execute --confirm-real-api`.
