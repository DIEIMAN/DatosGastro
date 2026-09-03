# Arquitectura del informe de evolución metodológica

Estado: PROPUESTA EDITORIAL EXPERIMENTAL — **no es el informe final**. Fecha: 2026-07-11.
Es la tercera pieza del programa de informes (tras la Fase 25 pulida y el informe
híbrido). Documenta cómo se pasó de 106 referencias a un pipeline reproducible por tipo
territorial.

## 1. Audiencia

Primaria: equipo técnico DGDGAS y quien herede el proyecto (continuidad institucional).
Secundaria: revisores externos (auditorías tipo GPT-5.6, pares de otras direcciones) y
la propia jefatura cuando pregunte "¿cómo saben esto?". No es una pieza política; es la
pieza que respalda a las políticas.

## 2. Extensión y forma

25–35 páginas. Tono: metodológico narrativo, sobrio, primera persona institucional
("el equipo"). Cada capítulo cierra con "qué aprendimos" en 2–3 líneas. Los números
canónicos se congelan en un `kpis_lock.json` propio antes de redactar (validación con
`scripts/qa/validate_kpis.py`).

## 3. Relato central (los dieciséis hitos)

El informe cuenta una historia en cuatro actos, que absorbe los dieciséis hitos
requeridos:

**Acto I — La lectura editorial (caps. 1–3)**

1. **Punto de partida:** 106 referencias geolocalizadas y una lectura editorial de 22
   polos/ejes; qué preguntas institucionales la motivaron.
2. **Fase 25:** la pieza institucional de 11 páginas; sus virtudes (prudencia, marca,
   legibilidad) y su naturaleza (lectura, no medición).
3. **Limitaciones de las 106 semillas:** cobertura mínima, sesgo hacia lo reconocido,
   imposibilidad de derivar densidades o límites; por qué "semilla" no es "padrón".

**Acto II — La evidencia (caps. 4–6)**

4. **Construcción de F01/F02:** universo público de 9.739 entidades; qué mide cada
   fuente y qué no (habilitaciones/registros ≠ locales activos — guardrail permanente).
5. **Incorporación de Places:** consultas controladas y almacenadas (379 en el piloto
   de microzonas; 3.221 señales dentro de las 13 macrozonas estudiadas); estatus de
   fuente externa auxiliar E, nunca padrón; sanitización aplicada (sin `place_id` en
   entregables).
6. **Deduplicación:** apareo F01/F02↔Places; la muestra de 200 casos y por qué el
   etiquetado humano (DH-11) condiciona la confianza en las mezclas de fuentes.

**Acto III — El aprendizaje algorítmico (caps. 7–11)**

7. **DBSCAN:** por qué un único epsilon para toda la Ciudad falla con densidades
   heterogéneas; el diagnóstico de ruido (experimentos clustering v1/v2).
8. **HDBSCAN:** la mejora real (densidades variables, ruido explícito) y sus límites.
9. **El problema de KMeans:** subdividir clusters grandes por tamaño genera 91 de los
   163 polígonos y afecta 57 % de los puntos asignados; tiles sin fundamento
   territorial; por qué se abandonó ("KMeans resuelve el tamaño de las piezas, no el
   territorio").
10. **Los 163 polígonos técnicos:** la cartografía v4/v4.1/v4.2; qué mostró y por qué
    no podía cerrarse como delimitación institucional.
11. **La simplificación editorial:** 163 → 41 retenidos → 31 unidades; qué ganó en
    legibilidad y qué decisiones humanas quedaron incorporadas al código (nombres,
    fusiones, exclusiones); los 16 pares de solape y su corrección solo visual en v4.1.

**Acto IV — La síntesis híbrida (caps. 12–16)**

12. **La auditoría externa (GPT-5.6):** veredicto (mejora la evidencia; no cerrar la
    cartografía), hallazgos principales (dependencia Places por zona: 93 % Costanera,
    71 % Puerto Madero, >60 % en cuatro zonas más) y la recomendación
    PIPELINE_HIBRIDO_POR_TIPO_TERRITORIAL.
13. **El pipeline híbrido:** representaciones por tipo territorial (núcleo, corredor,
    red, frente, señal); los cinco prototipos v1 y sus métricas de robustez; las
    repeticiones (Belgrano, Puerto Madero) y el soporte de ejes viales.
14. **Las decisiones humanas:** el sistema DH-01…DH-12; qué preguntas no puede
    responder un algoritmo (identidad, nombres, fronteras editoriales, alcance) y cómo
    se documentó cada firma (REGISTRO DEC-01…DEC-09).
15. **El resultado final:** el estado con que se publican los informes (se completa
    tras la integración de resultados de Codex y las firmas pendientes).
16. **Reproducibilidad futura:** scripts, hashes de insumos, metadata por experimento,
    QA por paquete; qué haría falta para repetir todo el camino (o extenderlo a las
    ocho zonas restantes) sin las personas que lo hicieron.

## 4. Capítulos (síntesis)

Portada / resumen ejecutivo técnico (1 p.) / los cuatro actos (caps. 1–16, ~2 páginas
por capítulo promedio, con los actos II y III más densos) / conclusiones y estado de
decisiones / anexos.

## 5. Gráficos necesarios

1. Línea de tiempo del proyecto (106 semillas → Fase 25 → F01/F02 → Places → clustering
   → auditoría → híbrido → informes).
2. Embudo de datos: 9.739 entidades F01/F02 → 6.461 puntos en 13 macrozonas (3.240 +
   3.221) → puntos asignados a estructuras por zona.
3. Embudo de polígonos: 163 → 41 → 31 → estructuras híbridas por tipo.
4. Mapa comparativo por zona "antes/después": Fase 25 vs. v4.2 vs. híbrido (Corrientes
   y San Telmo como casos ejemplares; Belgrano como caso de repetición).
5. Barras de dependencia de fuente por zona (F01/F02 vs. Places).
6. Diagrama del pipeline híbrido (insumos → detección → estabilidad → decisión humana →
   representación).
7. Panel de robustez: bootstrap por bloques / ablación de fuentes / sensibilidad de
   bordes por zona.

## 6. Tablas necesarias

1. Fuentes del proyecto con clasificación F/I/E y qué mide cada una.
2. Métricas por zona: puntos, cobertura de la representación, estabilidad, % Places.
3. Comparativa de métodos (DBSCAN / HDBSCAN / HDBSCAN+KMeans / híbrido) con criterios:
   maneja densidad variable, produce tiles artificiales, requiere decisión humana.
4. Registro de decisiones (DEC-01…DEC-09 + DH abiertas) con fecha y carácter.
5. Inventario de artefactos reproducibles (scripts, geojson, csv, hashes).

## 7. Comparativas antes/después

Obligatorias: Corrientes (23 tiles KMeans vs. corredor único continuo), San Telmo
(8 microáreas vs. núcleo de consenso), Belgrano (hulls inestables vs. núcleos con
estabilidad reportada — tras repetición), cobertura global de evidencia (106 semillas
vs. 6.461 puntos). Cada comparativa lleva la misma estructura: qué se veía, qué se ve,
qué decisión humana medió.

## 8. Métricas a incluir

- Conteos canónicos: 106 / 22 / 9.739 / 6.461 (3.240 + 3.221) / 163 / 91 / 41 / 31 / 5
  prototipos / 379 consultas del piloto.
- Robustez por zona (bootstrap por bloques): San Telmo 0,92 de membresía media y
  consenso 1; Corrientes 0,65; Belgrano 0,39 (pre-repetición) y su valor post;
  Puerto Madero 0,86; Costanera 0,77.
- Dependencia de Places por zona (con la advertencia de error de apareo mientras DH-11
  no esté completa).
- Coberturas de representación por zona (con su lectura DEC-08: lo no cubierto no es
  ruido).

## 9. Tecnicismos: cuáles se explican y cuáles van a anexo

**Se explican en el cuerpo (una vez, en lenguaje llano):** clustering ("agrupar puntos
cercanos"), densidad variable, ruido técnico vs. oferta dispersa, buffer/franja como
convención, estabilidad/bootstrap ("¿el resultado sobrevive si le quitamos una parte de
los datos?"), deduplicación.

**Van a anexo:** parámetros exactos (epsilon, min_samples, bandwidths, umbrales KDE),
hashes de insumos, metadata JSON por experimento, tablas completas de estabilidad,
inventario de ejes viales, fe de erratas de la auditoría.

**No aparecen en ningún lugar:** claves, rutas privadas, `place_id`, datos personales,
conteos que expongan filas individuales sensibles.

## 10. Dependencias

Se redacta **al final** del programa (tercera pieza): necesita los resultados de Codex
integrados, las DH abiertas firmadas y los dos informes anteriores cerrados para contar
el "resultado final" (cap. 15) sin reescrituras. Todo el material de los actos I–III ya
existe y puede pre-redactarse en borrador cuando Diego lo habilite.
