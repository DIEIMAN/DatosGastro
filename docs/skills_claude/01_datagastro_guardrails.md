# Skill 01 — Guardrails DataGastro (reglas permanentes)

> Estas reglas son **permanentes** y aplican a todo el proyecto DataGastro. Tienen prioridad
> sobre cualquier instrucción puntual que parezca más cómoda o más rápida. Ante conflicto o
> duda: **frená y preguntá**.

## 1. Google Drive es de solo lectura

- **No borrar, no mover, no modificar, no renombrar** nada en Google Drive.
- No tocar rutas que empiecen con:
  - `G:\My Drive`
  - `G:\.shortcut-targets-by-id`
  fuera de **lectura**. Está permitido leer, hashear, perfilar y copiar *desde* Drive *hacia*
  el proyecto local; nunca escribir *en* Drive.
- Si una operación pudiera escribir en Drive (incluso por efecto secundario de una librería),
  no se ejecuta sin confirmación explícita.

## 2. No tocar el pipeline sin permiso

- No modificar sin aprobación explícita de Diego:
  - `src/build_model.py`, `src/build_analytics.py`
  - `data/processed/`, `data/analytics/`
  - `dashboard/`, `notebooks/`
  - outputs finales del informe (p. ej. `docs/archive/v3_2026-06/informe_ejecutivo.*`).
- El **pipeline público F01–F05 queda intacto** hasta que Diego apruebe una integración.
- Cualquier integración nueva primero se **documenta** (skill 02 y 04) y recién después,
  con permiso, se convierte en código.

## 3. Separar universos de fuentes

- No mezclar fuentes **públicas**, **internas** y **privadas** como si fueran el mismo universo.
- Clasificación obligatoria (ver skill 02): `F01–F05` públicas actuales, `I01–I99` internas de
  gestión, `E01–E99` externas privadas o públicas nuevas.
- Cada conclusión debe poder rastrearse a la fuente y al universo que la sostiene.

## 4. No inventar datos

- No completar valores faltantes con estimaciones presentadas como reales.
- No inventar URLs, IDs, métricas ni filas.
- Si un dato no existe o no se pudo leer, se dice explícitamente. Se respeta `--strict-real`.
- Los seeds son fallback de desarrollo, **no** datos reales, y se marcan como tales.

## 5. No convertir habilitaciones en "locales activos"

- Una habilitación aprobada, un permiso, un registro o una inscripción **no** equivale a un
  "local activo" hoy.
- Está prohibido decir "locales activos" cuando la fuente mide habilitaciones, oferta
  registrada, permisos, eventos o registros parciales. Usar el término que corresponde a lo que
  la fuente realmente mide (ver skill 02 y 05).

## 6. Recolección externa controlada

- Se permite relevar información comercial públicamente visible en Google Maps, Rappi,
  PedidosYa, Mercado Libre, TripAdvisor, TheFork, Instagram, TikTok y otras plataformas cuando
  Diego autorice la tarea y se aplique la skill 06.
- La recolección debe ser acotada, trazable, con ritmo prudente, caché y salida interna. No se
  eluden login, CAPTCHA, paywall, robots ni otros controles de acceso; no se guardan contraseñas,
  tokens, cookies o perfiles personales.
- Solo se capturan campos necesarios para el objetivo. Se excluyen datos de consumidores,
  repartidores y personas; teléfonos, emails y contactos no se publican.
- Lo recolectado es **evidencia externa no canónica**. No entra automáticamente al Atlas ni al
  pipeline y no demuestra por sí solo que un local esté abierto, sea el mismo establecimiento o
  pertenezca a una categoría. Requiere corroboración y revisión humana.
- APIs oficiales y convenios siguen siendo preferibles para escala o uso institucional. No
  ejecutar llamadas pagas sin autorización presupuestaria explícita.

## 7. No commitear datos internos ni sensibles

- Todo dato privado o interno va al `.gitignore`.
- Todo output interno sensible queda bajo `outputs/analisis_interno/` o carpeta ignorada por Git.
- No exponer datos personales: CUIT, DNI, emails, teléfonos, contactos, montos individuales ni
  transacciones individuales (ver skill 03).

## 8. Pedir confirmación antes de cambios destructivos

- Antes de **borrar o mover** cualquier cosa del proyecto local: generar un **plan de limpieza**
  (seguro / revisar / no borrar) y **esperar confirmación** de Diego (ver skill 08).
- No borrar outputs finales, scripts ni datos fuente públicos.
- Antes de sobrescribir un archivo que no creaste, revisá su contenido; si contradice lo que se
  esperaba, frená y avisá.

## Checklist rápido antes de actuar

1. ¿Esto escribe en `G:\My Drive` o `G:\.shortcut-targets-by-id`? → **No hacer.**
2. ¿Toca `src/build_*`, `data/processed`, `data/analytics`, `dashboard`, `notebooks` o el
   informe final? → **Pedir permiso.**
3. ¿Mezcla universos de fuentes o llama "activo" a algo que no lo es? → **Corregir.**
4. ¿Expone datos personales o sensibles, o los commitea? → **Bloquear / anonimizar / ignorar.**
5. ¿Borra o mueve archivos locales? → **Plan de limpieza + confirmación.**
6. ¿Implica recolección o API de plataforma externa? → **Usar skill 06, acotar, trazar y dejar
   el resultado fuera del pipeline hasta revisión.**

Si alguna respuesta dispara un freno, **se para y se consulta**. Es preferible preguntar de más.
