# Decisión post re-piloto — Tanda 1 real (Google Places, Fase 11)

Fecha: 2026-07-02. Documento interno de decisión. Basado en la corrida real única
(ver `QA_REPILOTO_TANDA1_REAL_GOOGLE_PLACES.md`).

## Veredicto

**La corrida real fue técnicamente exitosa y el flujo sirve.** Se recomienda **preparar la Tanda 2
(otro bloque de 10)**, sin cambios estructurales, corrigiendo solo las 3 queries de los casos que
quedaron con reserva (Osaka, Aldo's, Oporto). No hay problemas de API, cuota, billing ni seguridad.

## Respuestas puntuales

**¿La corrida real fue técnicamente exitosa?**
Sí. 10 requests, 10 matches, 0 errores de API, 0 problemas de cuota/billing/permiso/endpoint. Hard
cap respetado. Key nunca expuesta. Outputs bien separados (interno / revisión visual / publicable).

**¿Cuántos matches son confiables?**
**3** de confianza alta y operativos, con nombre y zona coherentes: **Don Julio, La Cabrera, Gran
Dabbang**. Son los candidatos más firmes (aun así pasan por revisión antes de publicar).

**¿Cuántos quedan en revisión?**
**5** en `aceptar_con_revision` (confianza media, operativos): **Niño Gordo, Mishiguene, La Mar,
Cosi Mi Piace, Oporto**. Nombre correcto; falta confirmar sede/zona.

**¿Cuántos fueron rechazados / corregir_query?**
Ninguno rechazado de plano por rubro o por sustituto erróneo. **2** quedan con reserva fuerte por
**CLOSED_PERMANENTLY**: **Osaka** (`aceptar_con_revision`, cerrado) y **Aldo's** (`revisar_manual`,
cerrado). Ambos requieren verificar vigencia; probablemente **corregir_query** o marcar el local
como "sin vigencia confirmada".

**¿Sirve el flujo para mapa después de revisión humana?**
Sí. Los 10 traen lat/lon en el interno y en la revisión visual. Tras validar sede/zona/vigencia a
mano y marcar `aceptado_para_mapa=si`, el publicable se llena con esos puntos. El diseño prudente
(nada al mapa sin revisión) funcionó: 0 aceptados automáticos.

**¿Conviene ejecutar una segunda tanda de 10?**
Sí. Se cumple el criterio: hay 7+ resultados razonables (de hecho los 10 devolvieron el local
correcto, sin sustitutos erróneos) y ningún problema grave de API/seguridad.

**¿Conviene corregir queries antes?**
Solo las 3 con reserva:
- **Osaka**: confirmar si hay sede vigente (la devuelta está cerrada). Ajustar query o marcar sin
  vigencia.
- **Aldo's**: ídem (devuelta cerrada).
- **Oporto**: la devuelta ("Oporto Almacén") cae en **Colegiales**, no en Palermo Soho/Hollywood.
  Ajustar query con barrio o aceptar el reencuadre de zona con revisión.
El resto (7) no necesita corrección de query.

**¿Conviene reemplazar algún local de la muestra?**
No para la muestra de Tanda 1 (fue diseñada como prueba de estrés e hizo su trabajo). Para escalar,
Osaka y Aldo's podrían quedar como "vigencia no confirmada" en el padrón semilla, no como puntos de
mapa activos.

**¿Conviene escalar luego a los 106?**
Sí, pero **por tandas de 10** (respetando el cap por corrida) y **después de** cerrar la revisión
manual de esta Tanda 1 y correr Tanda 2. No lanzar los 106 de una: mantiene el gasto acotado y
permite validar el criterio de aceptación en cada bloque.

## Recomendación operativa

1. Revisión humana de los 10 de Tanda 1: confirmar sede/zona de los 5 en revisión, y vigencia de
   Osaka/Aldo's (cerrados) y zona de Oporto (Colegiales).
2. Preparar Tanda 2 (siguiente bloque de 10 desde Fase 11), con las 3 queries ajustadas si se
   decide reintentar Osaka/Aldo's/Oporto.
3. Recién con Tanda 1 y Tanda 2 validadas, planificar el escalado por tandas hacia los 106.

> Nada de esto ejecuta API por sí solo: la Tanda 2 requiere una nueva autorización explícita y el
> mismo doble flag `--execute --confirm-real-api`.
