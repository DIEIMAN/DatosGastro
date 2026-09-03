# Ronda 22 — corrección de relaciones posterior a auditoría independiente

**Estado:** CORRECCION. No constituye promoción institucional.

## Resultado geométrico confirmado

- **190 de 190** pares `referente_id + polo_uid` únicos y reproducidos.
- **190 de 190** coinciden con R22 en interior/exterior; distancia máxima divergente informada: **0,000 m**.
- Posición: **138 interiores**, **51 exteriores** y **1 sobre el límite**.
- Los Galgos: interior de Avenida Corrientes, a **36,976 m** del borde.
- No se modificó ninguna geometría.

## Clasificación diagnóstica integrada

| clasificación | relaciones |
|---|---:|
| INTERIOR | 108 |
| INTERIOR_PROXIMO_AL_BORDE | 30 |
| CONTEXTUAL_DOCUMENTAL | 26 |
| ASIGNACION_DUDOSA | 17 |
| ENTORNO_CERCANO | 9 |
| ASIGNACION_INCORRECTA | 0 |

Las bandas de 50 y 200 m son diagnósticas y no institucionales. No se encontró ninguna asignación incorrecta.

## Bloqueante documental

Las **52 relaciones exteriores** conservan `asignacion_metodo = DOCUMENTO`, pero R22 no individualiza norma, medio, año o página. Estado de trazabilidad de asignación:

- `GEOMETRIA_REPRODUCIDA`: **138** relaciones interiores.
- `ANTECEDENTE_LOCAL_PARCIAL`: **3** altas de Monserrat con antecedente local, todavía sin cita pública completa vinculada a la relación.
- `SIN_FUENTE_INDIVIDUALIZADA`: **49** relaciones.

Las 52 se conservan; no se aceptan ni rechazan en bloque. Sólo las 138 interiores pueden aparecer en el panel territorial. Entorno y contexto van en prosa; las 17 dudosas quedan suspendidas hasta individualizar la fuente.

## Alertas editoriales corregibles

- 18 relaciones no territoriales estaban publicadas en paneles.
- Tres omakase interiores de Palermo no estaban listados.
- La diferencia `Devoto` / `Villa Devoto` impidió localizar tres relaciones durante la auditoría, aunque la ficha sí las contenía; se normaliza el vínculo por `polo_uid`.
- Mercado de San Telmo queda a 64,2 m del borde: se conserva como señal para una decisión territorial futura, sin alterar el polígono.

## Validez por CRS

R22 entrega 39/39 geometrías válidas en EPSG:4326. La auditoría externa informó R08, R12 y R21 inválidas al reproyectar a EPSG:5347; el entorno local reproduce R08 y R21, mientras R12 resulta válida. La diferencia se atribuye al motor geométrico. En ambos controles, reparar no altera ninguna de las 190 relaciones ni produce variación material de superficie.
