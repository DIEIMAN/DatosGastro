# Decision gate — antes de Places (Expansión V4)

**Fecha:** 2026-07-12

## Semáforo general

| Tanda | ¿Lista para ejecutar Places? | Condición |
|---|---|---|
| 1 | **CONDICIONAL VERDE** | Áreas+cobertura+plan+contratos listos; **reutilizar primero**; brechas solo con autorización |
| 2 | AMARILLO | Requiere autorización de volumen nuevo y calibración tanda 1 |
| 3 | AMARILLO | Idem; varias zonas con evidencia débil |
| 4 | ROJO/AMARILLO | Complejidad de solape con polos adoptados; subunidades Centro |

## Tanda 1 — checklist de listo

- [x] Áreas válidas GeoJSON
- [x] Cobertura medida vs universo 6461
- [x] Plan incremental
- [x] Contrato de puntos
- [x] Reglas de deduplicación referenciadas
- [x] Superficies protegidas respetadas
- [x] Prompt Codex completo
- [ ] **Autorización humana explícita** para cualquier fila `CONSULTAR*`

## Por zona (Tanda 1)

| Zona | Places reutilizable | Nueva consulta | Notas |
|---|---|---|---|
| Z01 Villa Crespo | SI (macrozona previa) | PARCIAL bordes/ejes | Thames vs Palermo |
| Z02 Chacarita | SI + refino previo | PARCIAL Newbery/Dorrego | No Lacroze completa |
| Z03 Caballito | SI | PARCIAL por nodos | No fusionar nodos |
| Z04 Caseros | SI parcial | PARCIAL tramo | No Patricios |

## Evidencia documental post hoc

Suficiente para contraste en Crespo/Chacarita/Caseros/García del Río.  
Releer fuentes `INDEXADA_SNIPPET_O_TITULO` antes de **publicación**.

## Bloqueos

1. Falta autorización de API/presupuesto.
2. Caches internos sensibles no van a paquetes públicos.
3. C-S02 no consulta.
4. No adoptar sin decisión humana.
