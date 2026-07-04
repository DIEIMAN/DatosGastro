# Decisión post Tanda 2 — Google Places (PolosGastro, Fase 11)

Fecha: 2026-07-02. Documento interno de decisión. Basado en la corrida real única de Tanda 2
(ver `QA_TANDA2_REAL_GOOGLE_PLACES.md`).

## Veredicto

**Tanda 2 técnicamente exitosa.** Se recomienda **avanzar a Tanda 3**, cerrando primero el bloque
Palermo/Las Cañitas y **luego** pasar a Puerto Madero / San Telmo. Sin problemas de API/seguridad.

## Respuestas puntuales

**¿La Tanda 2 fue técnicamente exitosa?**
Sí. 10 requests, 10 matches, 0 errores; sin problemas de cuota/billing/permiso/endpoint; hard cap
respetado; key no expuesta; outputs separados y sanitizados. Ningún resultado fuera de CABA, ningún
rubro no gastronómico, ningún sustituto erróneo.

**¿Cuántos matches son confiables?**
De confianza operativa y nombre coherente: **~6** (Café Registrado, Novecento, Kansas, SushiClub,
Campo Bravo, Niño Gordo) — todos operativos, en CABA, rubro gastronómico. Aún pasan por revisión de
sede antes de mapear (cadenas). Estrictamente "alta + operativo" no quedó ninguno (Las Pizarras es
alta pero cerrado temporalmente).

**¿Cuántos quedan en revisión?**
Los 10 requieren revisión manual (diseño prudente). Casos con reserva específica:
- **Cerrados (3)**: Las Pizarras Bistro (temp.), Francisca del Fuego (temp.), Morelia (permanente).
- **Sede/zona a confirmar**: Café Registrado, Novecento, Kansas, SushiClub (cadenas).

**¿Cuántos fueron rechazados / corregir_query?**
- **Pa' Pastar**: devolvió "Pastasole Argentina" (nombre distinto, confianza baja) →
  **corregir_query** o marcar sin match confiable (probable cierre/renombramiento).
- **Campo Bravo**: "CAMPOBRAVO" es variante de formato del mismo local; no es rechazo, solo revisar.
- Ninguno rechazado por rubro no gastronómico, fuera de CABA ni sustituto erróneo.

**¿Conviene ejecutar Tanda 3?**
**Sí.** Se cumple el criterio (7+ resultados razonables, sin problemas graves). El flujo es estable
a lo largo de dos tandas.

**¿Seguir por Palermo/Las Cañitas o pasar a Puerto Madero/San Telmo?**
El bloque **Palermo/Las Cañitas ya quedó cubierto** (LG001–LG019 entre Tanda 1 y 2, + zona límite).
Por lo tanto, **Tanda 3 debería pasar a Puerto Madero** (LG029–LG037, 9 locales) y completar con
San Telmo, ambos polos de documentación media del Borrador 3. Es el paso natural.

**¿Qué casos deben quedar como decisiones humanas?**
- **Cerrados** (Las Pizarras, Francisca del Fuego, Morelia): mantener en semilla como "vigencia no
  confirmada / no mapeable hasta validar" (mismo criterio que Osaka/Aldo's de Tanda 1;
  ver `DECISIONES_HUMANAS_POST_TANDA1.md`).
- **Pa' Pastar**: definir si se acepta "Pastasole" como reemplazo, se corrige la query o se marca
  sin match; **no** reescribir automáticamente el nombre semilla.
- **Niño Gordo (LG028)**: confirmar si existe una sede propia en Villa Crespo o si es duplicado de
  la sede Palermo (LG003, misma dirección Thames 1810).
- **Cadenas** (Café Registrado, Novecento, Kansas, SushiClub): validar que la sede devuelta es la de
  Las Cañitas/Palermo esperada.

## Recomendación operativa

1. Revisión humana de los 10 de Tanda 2 (cierres, cadenas, Pa' Pastar, Niño Gordo LG028).
2. Preparar **Tanda 3 = Puerto Madero** (muestra + queries desde Fase 11), con el mismo flujo y
   doble confirmación.
3. Continuar por tandas de 10 hacia el resto del universo; nunca lanzar los 106 de una.

> La Tanda 3 requiere nueva autorización explícita y el mismo `--execute --confirm-real-api`
> (con `--tanda tanda3` una vez preparada su muestra).
