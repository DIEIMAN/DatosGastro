# Handoff documental → preflight espacial Claude (Expansión V4)

**Fecha:** 2026-07-12  
**De:** investigador_documental_externo  
**Para:** preflight espacial / metodológico V4 (Claude)  
**Complementa:** no reemplaza el preflight técnico.

## 1. Nombres normalizados (usar en áreas de consulta)

| ID | Análisis | Comunicación | Evitar sin glosa |
|---|---|---|---|
| Z01 | Villa Crespo | Villa Crespo | Chacacrespo |
| Z02 | Chacarita | Chacarita | Chacalermo |
| Z03 | Caballito (multinodo) | Caballito | "el polo de Caballito" único |
| Z04 | Boulevard Caseros (tramo Parque Lezama) | Boulevard Caseros | Polo Caseros = Barracas |
| Z05 | Familia Centro (subunidades) | Centro y Microcentro (desagregado) | Centro unitario |
| Z06 | Abasto (núcleo) | Abasto | Abasto = toda Corrientes |
| Z07 | Avenida Boedo | Boedo | polo Boedo (sin spatial) |
| Z08 | Villa Devoto (Plaza Arenales) | Villa Devoto | — |
| Z09 | Corredor Donado–Holmberg | Donado–Holmberg | DoHo institucional |
| Z10 | Villa Urquiza (multieje) | Villa Urquiza | Urquiza = DoHo |
| Z11 | Retiro — Esmeralda–Paraguay | Entorno Esmeralda y Paraguay | Nuevo Bajo oficial |
| Z12 | Federico Lacroze (por tramos) | tramos Lacroze | avenida completa |
| Z13 | García del Río (Saavedra) | Bulevar García del Río | Parque Saavedra = polo |
| Z14 | La Paternal | La Paternal | Distrito del Vino |
| Z15 | Villa Pueyrredón (exploratorio) | Villa Pueyrredón | Av. San Martín completa |

## 2. Zonas y subzonas

- **Caballito:** Goyena · Primera Junta/Mercado · Patio Lecheros · (Parque Rivadavia a testear).
- **Chacarita:** Newbery · Dorrego · (no Lacroze completa).
- **Centro:** ver `SUBUNIDADES_DOCUMENTALES_CENTRO_V4.csv` (C-S01…C-S08).
- **Urquiza/DoHo/García del Río:** tres IDs.

## 3. Calles y nodos documentados (anclas de AOI, no de polígono final)

Ver normalización CSV y expedientes. Priorizar anclas con fuente OFICIAL o PERIODISTICA leída.

## 4. Conflictos a reflejar en preflight

- Crespo–Palermo (Thames)
- Chacarita–Palermo (Chacalermo)
- Caseros: San Telmo vs Barracas; excluir Patricios
- Abasto vs Corrientes centro
- DoHo vs Urquiza vs García del Río
- Nuevo Bajo vs Microcentro
- Paternal borde Crespo

## 5. Fuentes clave

`outputs/.../FUENTES_DOCUMENTALES_EXPANSION_V4.csv` + `QA_...csv`  
Priorizar `uso_permitido` RESPALDO_PRINCIPAL / COMPLEMENTARIO con QA ABIERTA_Y_LEIDA.

## 6. Preguntas que deben entrar al diseño de AOI

1. ¿Un cluster, varios o ninguno?  
2. ¿Corredor lineal vs núcleo vs archipiélago?  
3. ¿Borde con vecinos de tanda?  
4. ¿La avenida completa tiene señal o solo un tramo?

## 7. Límites que NO deben imponerse

- Polígonos barriales administrativos como máscara de polo.
- Bbox único de "Centro".
- DoHo/Chacalermo/Nuevo Bajo como etiquetas de cluster sin decisión editorial.
- Lista semilla de locales como puntos de verdad.

## 8. Correr juntas / separar

| Juntas (misma tanda, IDs distintos) | Separar |
|---|---|
| Crespo + Chacarita (+ borde Palermo observación) | Caseros vs Patricios |
| DoHo + Urquiza + García del Río (comparación) | Abasto vs Corrientes centro |
| Subunidades Centro + Nuevo Bajo | Lacroze completa vs Chacarita |
| Paternal + borde Crespo | Pueyrredón vs Av. San Martín total |

## 9. Evidencia faltante

Ver `AGENDA_BUSQUEDA_OFICIAL_PENDIENTE_V4.md`.

## 10. Mensaje final a Claude

Este handoff aporta **priors documentales y conflictos de nombres**. El preflight define **cómo medir**. Si el spatial no encuentra estructura, la respuesta correcta es reportar ausencia — no estirar el mapa hasta la narrativa.
