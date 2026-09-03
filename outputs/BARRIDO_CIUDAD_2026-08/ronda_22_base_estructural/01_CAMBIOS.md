# Cambios de R22

## Qué cambió

| objeto | campo | valor_anterior | valor_nuevo | accion_r22 |
|---|---|---|---|---|
| Bar Olimpo | nombre | Café Olimpo | Bar Olimpo (alias Café Olimpo) | ACTUALIZAR |
| Bar Olimpo | barrio/comuna | Villa Luro en anexo; Monte Castro en capa R11 | Monte Castro; Comuna 10 | CONFIRMAR |
| OLIMPO | identidad | Registro histórico GCBA-only en Arregui 5794 | Entidad separada; no Bar Notable canónico; no fusionar con H028 | NO_FUSIONAR_NO_INCORPORAR |
| La Esquina de Aníbal Troilo | reconocimiento_normativo | Bar Notable en capa R11 | Excluido de la candidata canónica vigente | EXCLUIR_PRESERVANDO_HISTORIA |
| Bar Iberia | reconocimiento_normativo | Alta de ronda 5 interpretada como posible residual | Bar Notable canónico, orden 10/90 | CONSERVAR |
| El Sol de Galicia | registro/dirección/categoría | Sin fila en R11; base local a Luis Viale 2881 | Luis Viale 2867; churrería/pastelería; referente de trayectoria; no Bar Notable | INCORPORAR |

- Se creó una ontología explícita de sistemas y piezas; no se parsea semántica desde `R09+R19+Z43`.
- Se registró en la tabla de relaciones la continuidad Chacagiales–Villa Ortúzar (732 → 795; 69/69), explícitamente sin fusión.
- Se reparó R12 con `make_valid`; R08 quedó geométricamente idéntica al pasar por el mismo procedimiento.
- Se recalcularon conteos, comuna/barrio y asignaciones de referentes sobre la geometría candidata.

## Qué no cambió

- Atlas V2, ronda 21 y segunda pasada experimental por manzanas: sin modificaciones.
- Unión territorial, criterio de admisión, número de features (39) y variante Warnes: sin reapertura.
- Villa Ortúzar no se fusionó. Overture-only no se eliminó.
- Cero llamadas Places/API. Sin PDF, commit, push, staging ni `git add`.
