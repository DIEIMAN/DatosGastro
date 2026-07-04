# Decisión sobre la Tanda 2 — Google Places (PolosGastro, Fase 11)

Fecha: 2026-07-02. Documento interno de decisión. No se ejecutó API para producirlo.

## Veredicto

**NO avanzar a Tanda 2 con el esquema actual.** Rehacer el piloto (Tanda 1 corregida) antes de
seguir. La Tanda 1 **no es confiable como está**: usó el insumo equivocado, con queries pobres que
produjeron 3 matches erróneos, y el QA de Copilot documentó mal el resultado.

Motivo según criterio de decisión: hubo **encoding roto** (en documentación), **matches fuera de
lo esperado** (Somos OP, Artemisia, Osaki) y **contradicción entre "aceptado" y "revisión
manual"**. Cualquiera de los tres ya obliga a no avanzar hasta corregir.

## Respuestas puntuales

**¿Conviene avanzar a Tanda 2 ahora?**
No. Primero corregir queries y rehacer la muestra de Palermo.

**¿Hay que corregir queries antes?**
Sí. Las queries de la Tanda 1 metían el nombre completo del polo dentro del `textQuery`
(`"Osaka, Palermo (Soho, Hollywood y Las Cañitas), CABA, Argentina"`), lo que degrada el match.
Debe usarse la tabla preparada de Fase 11 (`locales_semilla_preparados_para_google_places.csv`),
que ya tiene `query_google_places_principal` + `query_google_places_alternativa` + hints de barrio.

**¿Hay que rehacer la Tanda 1?**
Sí, rehacer el piloto con la muestra corregida (mismo tope de 10, mismos locales de Palermo, pero
queries de Fase 11). No se pierde nada: se conservan los CSV actuales como evidencia auditada.

**¿Qué pasó con Artemisia?**
No es un local del universo semilla. Es el **resultado equivocado** que Google devolvió para la
query de **Aldo's (Palermo)** (LG008). El QA de Copilot lo listó por error como "LG008_ARTEMISIA",
confundiendo el nombre-Google con el nombre-semilla. Acción: descartar el match, corregir la query
de Aldo's.

**¿Qué pasó con Somos OP?**
No es un local del universo semilla. Es el resultado equivocado para la query de **Oporto** (LG010)
— y encima es una **aseguradora** (`insurance_agency`), no un restaurante. El QA lo listó como
"LG010_SOmos_OP". No es Osaka ni una variante de Oporto: es ruido de match. Acción: rechazar,
corregir query de Oporto y validar vigencia del local.

**¿Qué pasó con Ni�o Gordo?**
Nada en los datos: en los CSV el nombre figura correcto como **"Niño Gordo"** (LG003), con un match
sólido (Thames 1810, Palermo). El "Ni�o Gordo" / "Ni o Gordo" es **mojibake** de la consola y del QA
markdown de Copilot (salida sin UTF-8). Acción: corregir solo la documentación QA, regenerándola en
UTF-8.

**¿Cuántos matches quedan aceptados realmente?**
**Cero** aceptados para mapa. En el CSV sanitizado las 10 filas tienen `aceptado_para_mapa = no`.
El "Aceptados: 10" del QO de Copilot es engañoso: contó "matches devueltos", no "aceptados para
mapa".

**¿Cuántos quedan en revisión?**
De los 10, **7** son matches plausibles que quedan en `aceptar_con_revision` (Don Julio, La Cabrera,
Niño Gordo, Gran Dabbang, Mishiguene, La Mar, Cosi Mi Piace).

**¿Cuántos deberían corregirse?**
**3** requieren corrección de query / rechazo: Osaka (→ Osaki, `corregir_query`), Aldo's
(→ Artemisia, `corregir_query`), Oporto (→ Somos OP, `rechazar`). Ver
`auditoria_matches_tanda1.csv`.

**¿El criterio de `aceptado_para_mapa` está bien aplicado?**
El valor está bien (todo en `no`, prudente). Lo que está **mal es la narrativa del QA de Copilot**,
que reportó "10 aceptados" contradiciendo la propia tabla. El criterio del dato es correcto; la
documentación no.

**¿Los resultados tienen lat/lon suficientes para mapa?**
No. El script usa un FieldMask **sin** `location` a propósito, así que **no hay lat/lon**. Con esta
tanda **no se puede armar mapa**. Para mapear haría falta cambiar el FieldMask (decisión aparte, con
permiso, y respetando ToS de Google) o geocodificar por otra vía.

**¿Usar los resultados actuales o rehacer el piloto?**
**Rehacer** el piloto con la muestra corregida (queries de Fase 11). Conservar los 7 matches
plausibles como referencia, descartar los 3 erróneos, y no usar nada de esta tanda para el
informe hasta la nueva corrida validada.

## Plan mínimo antes de cualquier Tanda 2 (a aprobar por Diego)

1. Apuntar el script (o un wrapper) a `locales_semilla_preparados_para_google_places.csv` en lugar
   del seed del experimento.
2. Usar `query_google_places_principal` (y `_alternativa` como fallback) en vez de la query cruda.
3. Reconsultar los 10 de Palermo (cap 10 intacto) y comparar contra la Tanda 1.
4. Recién con la muestra de Palermo limpia, evaluar extender a otros polos del núcleo.
5. Decidir por separado si se habilita `location` (lat/lon) para mapas, con permiso y revisión ToS.

> Nada de esto se ejecutó en esta auditoría. Es un plan para decisión humana.
