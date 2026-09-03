# Matriz ampliada de decisiones humanas — pipeline híbrido v1

Estado: EXPERIMENTAL / NO OFICIAL. Fecha de corte: 2026-07-10.
Amplía `docs/polos_gastro/experimentos/pipeline_hibrido_tipo_territorial_v1/MATRIZ_DECISIONES_POST_PROTOTIPO.md`.
Evidencia verificada en `REVISION_CRITICA_PROTOTIPOS_HIBRIDOS.md` (misma carpeta).

Las recomendaciones técnicas de este documento **no son vinculantes** y ninguna decisión
queda tomada por este documento. "Cobertura" siempre refiere a puntos del universo
experimental (F01/F02 + Places sanitizado); Places es fuente externa auxiliar, no padrón.

## Índice de decisiones

| ID | Zona | Pregunta | Prioridad | Bloquea |
| --- | --- | --- | --- | --- |
| DH-01 | San Telmo | ¿Un núcleo, dos núcleos, o núcleo + eje Defensa contextual? | ALTA | mapa principal |
| DH-02 | Corrientes | ¿Corredor único, subtramos narrativos o geometrías separadas? | ALTA | mapa principal |
| DH-03 | Corrientes/Microcentro | ¿Dónde termina el polo Corrientes frente a Microcentro? | MEDIA | escalado de Microcentro |
| DH-04 | Belgrano | ¿Se aprueba el protocolo de repetición y el contenedor de contraste? | ALTA | escalado (tipo multinuclear) |
| DH-05 | Belgrano | Nombres y jerarquía de núcleos | MEDIA (diferida) | mapa principal |
| DH-06 | Puerto Madero | ¿Qué soporte territorial y qué segmentación para el frente? | ALTA | escalado (tipo frente) |
| DH-07 | Costanera Norte | ¿Anexo exploratorio o exclusión? ¿En qué forma? | BAJA | nada (si queda en anexo) |
| DH-08 | Todas | Relación del pipeline híbrido con Fase 25 | ALTA | informe nuevo |
| DH-09 | Todas | Tratamiento de los puntos fuera de representación | ALTA | informe nuevo |
| DH-10 | Todas | Qué versión va al mapa principal del eventual informe | MEDIA | informe nuevo |
| DH-11 | Todas | Etiquetado humano de la muestra de deduplicación | MEDIA | informe nuevo |
| DH-12 | Corredores/frentes | Estatus del ancho de buffer (convención vs. medición) | BAJA | nada |

---

## DH-01 — San Telmo: jerarquía territorial

- **Zona:** San Telmo.
- **Pregunta:** ¿la representación final es un núcleo compacto único, dos núcleos, o un
  núcleo compacto principal más el eje Defensa como elemento contextual?
- **Por qué no puede resolverla el algoritmo:** el resultado depende del umbral de KDE
  elegido (a umbral 0,5 con bw 80/100 hay 2 componentes; el consenso multi-bandwidth da
  1). Elegir umbral es elegir respuesta; además "qué papel juega la calle Defensa en la
  identidad del polo" es una pregunta editorial e institucional, no estadística.
- **Opciones reales:**
  - a) Núcleo compacto único (ST_N01 tal como está).
  - b) Dos núcleos (aceptar la partición que sugieren los umbrales altos de KDE).
  - c) Núcleo compacto principal + eje Defensa como elemento contextual (línea de
    referencia, sin polígono propio).
- **Evidencia a favor / en contra:**
  - a) A favor: consenso robusto entre bandwidths; membresía media 0,92; mezcla de
    fuentes mejor que el promedio (39,6 % Places). En contra: oculta la bimodalidad que
    aparece a umbral 0,5.
  - b) A favor: 2 componentes reproducibles en bw 80 y 100 a umbral 0,5. En contra: la
    separación desaparece a bw 140 y a umbrales menores; robustez por bloques 0,57 con
    p10 negativo no sostiene una partición fina; ningún dato actual dice qué "es" cada
    subnúcleo.
  - c) A favor: comunica la estructura (núcleo + eje comercial reconocible) sin fabricar
    un segundo polígono; el eje Defensa existe en el callejero local. En contra: en el
    prototipo no se construyó soporte vial para San Telmo, así que hoy el eje sería un
    agregado gráfico sin métrica de respaldo propia.
- **Cobertura de puntos:** a) 177/320 (55,3 %); b) no medida por opción (requiere
  recorte del consenso; estimable localmente sin datos nuevos); c) igual que a) más los
  puntos a ≤N m del eje que se decidan mostrar como contexto.
- **Impacto metodológico:** bajo — no cambia el pipeline, solo la salida.
- **Impacto visual:** alto — define la pieza central del mapa de San Telmo.
- **Impacto narrativo:** alto — "casco histórico con corazón gastronómico" (a/c) vs.
  "dos polos internos" (b).
- **Riesgo de falsa precisión:** máximo en b) (bordes de dos polígonos poco robustos);
  mínimo en c) si el eje se dibuja explícitamente como contexto.
- **Recomendación técnica (no vinculante):** opción c) — núcleo compacto principal +
  eje Defensa contextual — **condicionada a** construir primero el soporte vial de
  Defensa con la misma técnica de "eje respaldado" usada en Corrientes (corrida local,
  sin datos nuevos), para que el eje no sea decorativo. Si el respaldo del eje resulta
  débil, degradar a opción a).
- **Decisión preliminar sugerida:** c) condicionada; a) como fallback.
- **Quién decide:** Diego, con revisión cartográfica del eje respaldado; la prueba
  técnica adicional (soporte de Defensa) es previa a la firma.
- **Bloquea:** mapa principal de San Telmo. No bloquea el escalado del patrón núcleo.
- **Prioridad:** ALTA.

## DH-02 — Corrientes: forma de comunicación del corredor

- **Zona:** Avenida Corrientes.
- **Pregunta:** ¿corredor continuo único, corredor continuo con subtramos narrativos,
  varios corredores geométricamente separados, o corredor principal + contexto fuera
  del buffer?
- **Por qué no puede resolverla el algoritmo:** el perfil longitudinal no tiene huecos
  (0 bins vacíos), así que ningún criterio de densidad corta el corredor por sí solo;
  cualquier partición en tramos sería una elección de comunicación, no un hallazgo.
- **Opciones reales:**
  - a) Corredor geométrico continuo único (unificar las 5 componentes en la
    representación).
  - b) Corredor geométrico continuo con subtramos **solo como etiquetas narrativas**
    (p. ej. apoyados en los picos de los bins 3, 8 y 17–18 y el valle 400–800 m).
  - c) Varios corredores geométricamente separados (publicar las 5 componentes como
    piezas).
  - d) Corredor principal + puntos/contexto fuera del buffer (los 880 puntos del
    universo que quedan fuera, como capa de contexto).
- **Evidencia a favor / en contra:**
  - a/b) A favor: perfil continuo (105–525 pts/km, sin huecos); el eje es un objeto
    urbano real; robustez 0,65 con p10 aceptable. En contra de a): pierde la variación
    interna documentada.
  - b) A favor adicional: los picos y valles existen en el perfil; no requiere tocar la
    geometría. En contra: los nombres de los subtramos (p. ej. "tramo teatros") no
    están respaldados por los datos y deben validarse editorialmente.
  - c) En contra: las 5 componentes son un artefacto del filtro de respaldo por
    segmento (gate de puntos a 150 m), no cinco corredores reales; publicarlas
    fragmenta sin evidencia.
  - d) A favor: honesto con el hecho de que el corredor cubre 29,9 % del universo. En
    contra: el mapa se carga; requiere resolver antes DH-09.
- **Cobertura:** a/b) 375/1.255 (29,9 %); c) igual repartida en piezas; d) 100 % (con
  dos jerarquías visuales distintas).
- **Impacto metodológico:** nulo en a/b/d; c) contradice el diseño del soporte.
- **Impacto visual:** b) es el más legible; d) el más completo y el más cargado.
- **Impacto narrativo:** b) permite contar "un corredor con momentos distintos"; a)
  cuenta menos; c) cuenta algo que no es.
- **Riesgo de falsa precisión:** alto en c); medio en b) si las etiquetas de subtramo se
  publican como límites; bajo en a) y en b) con etiquetas claramente narrativas.
- **Recomendación técnica (no vinculante):** b) corredor geométrico continuo con
  subtramos solo como etiquetas o lectura narrativa, **sin partir la geometría**;
  combinable con d) según lo que se decida en DH-09.
- **Decisión preliminar sugerida:** b) (+ capa de contexto si DH-09 lo habilita).
- **Quién decide:** Diego (forma) + equipo DGDGAS (etiquetas narrativas de subtramos).
- **Bloquea:** mapa principal de Corrientes.
- **Prioridad:** ALTA.

## DH-03 — Corrientes: frontera con Microcentro y Centro

- **Zona:** Avenida Corrientes / Microcentro y Centro.
- **Pregunta:** ¿qué tratamiento recibe la zona de contacto? El contenedor de
  Microcentro se definió como "San Nicolás menos el corredor Corrientes" y la
  validación previa (V2-3) registró que el cluster más grande de la macrozona
  Corrientes cae en San Nicolás.
- **Por qué no puede resolverla el algoritmo:** es una decisión de arquitectura
  editorial (a qué polo se atribuye la oferta de la zona de contacto); cualquier
  asignación automática depende del recorte de contenedores que justamente está en
  discusión.
- **Opciones reales:** a) mantener el recorte actual (Corrientes absorbe la franja del
  corredor; Microcentro lo restante); b) redefinir la frontera al escalar Microcentro,
  con regla explícita de asignación; c) tratar la zona de contacto como solape
  declarado en el informe.
- **Evidencia:** a favor de a): el recorte ya eliminó un solape del 49,2 % y dejó 0
  entidades duplicadas (observaciones de MZ_MICROCENTRO_Y_CENTRO); a favor de b): el
  semiancho de 350 m de Corrientes fue una decisión de contenedor, no un hallazgo; en
  contra de c): dos polos contando la misma oferta reabre el problema que Cal-2/3 cerró.
- **Cobertura:** no aplica directamente; afecta a qué universo pertenecen ~cientos de
  puntos de la franja (406 entidades se reasignaron en la corrección previa).
- **Impactos:** metodológico medio (define universos de dos zonas); visual medio;
  narrativo medio ("dónde empieza el centro").
- **Riesgo de falsa precisión:** medio — cualquier línea divisoria será convencional;
  el riesgo es presentarla como límite real.
- **Recomendación técnica (no vinculante):** a) mantener el recorte actual hasta que
  Microcentro entre al escalado; decidir b) recién con el corredor de Microcentro
  construido.
- **Decisión preliminar sugerida:** a) statu quo documentado.
- **Quién decide:** Diego + revisión cartográfica (al escalar Microcentro).
- **Bloquea:** escalado de Microcentro; no bloquea el mapa de Corrientes.
- **Prioridad:** MEDIA.

## DH-04 — Belgrano: protocolo de repetición y contenedor de contraste

- **Zona:** Belgrano.
- **Pregunta:** ¿se aprueba repetir el prototipo según
  `ESPECIFICACION_REPETICION_BELGRANO.md`, incluyendo probar como contraste el barrio
  oficial completo además del contenedor de corredores de 250 m?
- **Por qué no puede resolverla el algoritmo:** el algoritmo no puede decidir contra qué
  contenedor validarse; la elección de contenedor es editorial y es la principal
  sospechosa de la robustez 0,39 (32,7 % de puntos a ≤100 m del borde; 53 entidades
  conocidas fuera de toda macrozona; encoger 100 m duplica el ruido).
- **Opciones reales:** a) aprobar el protocolo completo (incluye contenedor de
  contraste); b) aprobarlo sin cambio de contenedor; c) posponer Belgrano.
- **Evidencia:** a favor de a): toda la sección Belgrano de la revisión crítica; en
  contra de b): si el contenedor corta estructura, repetir dentro del mismo contenedor
  puede repetir el artefacto; en contra de c): Belgrano bloquea el tipo multinuclear
  completo (4 zonas más).
- **Cobertura:** hoy 21,5 %; objetivo del protocolo: núcleos estables con cobertura y
  estabilidad reportadas por núcleo.
- **Impactos:** metodológico alto (define el generador del tipo multinuclear); visual y
  narrativo diferidos a DH-05.
- **Riesgo de falsa precisión:** el protocolo lo reduce (categorías de estabilidad por
  núcleo en lugar de hulls firmes).
- **Recomendación técnica (no vinculante):** a).
- **Decisión preliminar sugerida:** a).
- **Quién decide:** Diego (aprobación de corrida local; no implica consultas externas).
- **Bloquea:** escalado del tipo multinuclear.
- **Prioridad:** ALTA.

## DH-05 — Belgrano: nombres y jerarquía (diferida)

- **Zona:** Belgrano.
- **Pregunta:** ¿qué nombres y jerarquía reciben los núcleos estables que sobrevivan a
  la repetición? ¿Barrio Chino, Cabildo/Juramento, Bajo Belgrano y Libertador/Barrancas
  emergen sin imponerlos?
- **Por qué no puede resolverla el algoritmo:** nombrar es atribuir identidad
  institucional; además la correspondencia núcleo↔topónimo debe testearse post hoc
  (protocolo BEL-R14), nunca usarse como insumo.
- **Opciones reales:** a) nombrar solo núcleos con estabilidad ALTA cuya
  correspondencia post hoc con un área conocida sea unívoca; b) publicar núcleos con
  códigos (BEL_Nxx) y sin nombres; c) trabajar con las cuatro subzonas conocidas como
  hipótesis editorial explícita (no algorítmica).
- **Evidencia:** hoy no hay núcleos reproducibles que nombrar (ARI entre métodos 0,07);
  cualquier decisión ahora sería prematura. La opción c) es legítima solo si se declara
  editorial.
- **Cobertura:** pendiente de la repetición.
- **Impactos:** narrativo alto (los nombres son lo que la jefatura retiene); visual
  medio; metodológico bajo.
- **Riesgo de falsa precisión:** alto si se nombra antes de tener estabilidad por
  núcleo.
- **Recomendación técnica (no vinculante):** posponer hasta después de la repetición;
  entonces aplicar a) con el test de correspondencia post hoc.
- **Decisión preliminar sugerida:** ninguna ahora (deliberadamente).
- **Quién decide:** Diego + equipo DGDGAS (nombres); prueba técnica adicional previa
  (repetición).
- **Bloquea:** mapa principal de Belgrano.
- **Prioridad:** MEDIA (alta después de la repetición).

## DH-06 — Puerto Madero: soporte territorial y segmentación

- **Zona:** Puerto Madero.
- **Pregunta:** ¿frente único sobre Alicia Moreau de Justo, frentes sobre ambos lados de
  los diques, segmentos norte/centro/sur, varios frentes cortos, o frente + puntos de
  contexto?
- **Por qué no puede resolverla el algoritmo:** las opciones dependen de qué ejes se
  admiten como soporte (decisión de diseño) y de cuánta cobertura se exige a cambio de
  cuánta banda (criterio editorial). El algoritmo solo puede medir cada opción.
- **Opciones reales** (todas con soporte verificado en
  `inventario_ejes_viales_puerto_madero.csv`; no se inventó ningún eje):
  - a) Frente único AMJ (statu quo del prototipo).
  - b) Frente doble: AMJ (oeste) + eje este de los diques (Juana Manso 3.876 m, y/o
    Pierina Dealessi 2.873 m / Olga Cossettini 1.650 m según respaldo por tramo).
  - c) Segmentos norte/centro/sur del mejor frente (derivados del perfil, no
    impuestos).
  - d) Varios frentes cortos (solo componentes respaldadas de longitud razonable).
  - e) Frente(s) + puntos de contexto para lo no asignado.
- **Evidencia a favor / en contra:**
  - a) A favor: robustez 0,86 con colas sanas. En contra: cubre 102/294 (34,7 %) y el
    soporte quedó en 18 componentes; el inventario confirma ejes paralelos del lado
    este que el prototipo ignoró.
  - b) A favor: los ejes existen y la mayor parte de la oferta no asignada está del
    lado este de los diques (192 puntos fuera del frente oeste); es la hipótesis
    natural del barrio (ambos márgenes de los diques). En contra: aún sin medir; riesgo
    de banda doble que se lea como "todo el barrio".
  - c) A favor: el perfil muestra variación (bin 750–1.000 m: 46 puntos) — pero ese
    tramo es 87 % Places, lo que desaconseja afirmar segmentos sobre esa base. En
    contra: nombres N/C/S no emergen de los datos.
  - d/e) A favor: honestidad con la fragmentación real y con los no asignados. En
    contra: d) fragmenta la lectura; e) depende de DH-09.
- **Cobertura:** a) 34,7 % medida; b–e) pendientes de la repetición (medibles
  localmente, sin datos nuevos).
- **Impactos:** metodológico alto (define el tipo "frente"); visual alto; narrativo
  alto ("el polo de los diques").
- **Riesgo de falsa precisión:** interpretar robustez 0,86 como cobertura suficiente
  (explícitamente advertido); publicar banda gigante para forzar cobertura.
- **Recomendación técnica (no vinculante):** ejecutar la repetición
  (`ESPECIFICACION_REPETICION_PUERTO_MADERO.md`) con b) como hipótesis principal y a)
  como línea de base; decidir entre b), b+c) o e) con las métricas en mano. No
  interpretar la robustez actual como validación del frente único.
- **Decisión preliminar sugerida:** ninguna geometría final ahora; aprobar la
  repetición.
- **Quién decide:** Diego (protocolo ya); Diego + revisión cartográfica (geometría
  final, post repetición).
- **Bloquea:** escalado del tipo frente; mapa principal de Puerto Madero.
- **Prioridad:** ALTA.

## DH-07 — Costanera Norte: inclusión y forma

- **Zona:** Costanera Norte.
- **Pregunta:** ¿anexo exploratorio o exclusión completa? Y si es anexo: ¿puntos + KDE,
  o cuatro marcadores de concentración?
- **Por qué no puede resolverla el algoritmo:** es una decisión de alcance del informe:
  con 5 registros F01/F02 sobre 72 puntos no hay medición pública que defender; incluir
  o excluir es política editorial.
- **Opciones reales:** a) anexo exploratorio con puntos + KDE; b) anexo con los 4
  marcadores; c) anexo con ambos; d) exclusión completa.
- **Evidencia:** a favor de anexo (a/b/c): las concentraciones son estables (0,77) y la
  zona tiene interés institucional evidente; a favor de puntos+KDE sobre marcadores:
  los marcadores puntuales sugieren "lugares" con una precisión que la fuente no
  respalda (CN_C03 es 100 % Places); a favor de d): pureza de fuentes — pero pierde la
  única lectura disponible de una zona que la jefatura probablemente pregunte.
- **Cobertura:** n/a (no hay polígono).
- **Impactos:** metodológico bajo; visual bajo (anexo); narrativo medio (gestiona la
  expectativa sobre Costanera).
- **Riesgo de falsa precisión:** bajo en a); medio en b) (los ×4 parecen "polos").
- **Recomendación técnica (no vinculante):** a) mantener como anexo exploratorio con
  puntos + KDE, **sin polígono y sin marcadores como símbolo principal**, con la
  advertencia de fuente en la propia lámina.
- **Decisión preliminar sugerida:** a).
- **Quién decide:** Diego.
- **Bloquea:** nada, si queda en anexo.
- **Prioridad:** BAJA.

## DH-08 — Todas: relación con Fase 25

- **Zona:** todas.
- **Pregunta:** ¿el pipeline híbrido reemplaza, complementa o queda subordinado a la
  lectura de Fase 25?
- **Por qué no puede resolverla el algoritmo:** Fase 25 es la versión institucional
  entregada a la oficina; su reemplazo es una decisión de gestión y de comunicación,
  no de métrica.
- **Opciones reales:** a) reemplazo; b) complemento (Fase 25 lectura general + híbrido
  como detalle territorial experimental); c) lectura general Fase 25 + detalle híbrido
  solo en zonas maduras; d) conservar Fase 25 como única versión oficial hasta validar
  la nueva.
- **Evidencia:** a favor de b/c: dos de cinco prototipos requieren repetición; los
  guardrails del experimento exigen no tocar Fase 25; el híbrido aún no tiene
  deduplicación etiquetada (DH-11) ni decisiones de mapa (DH-01/02/06). En contra de
  a): prematuro y contrario al QA del propio experimento. d) es b) sin el detalle
  experimental: pierde valor informativo sin ganar prudencia adicional.
- **Cobertura:** n/a.
- **Impactos:** metodológico bajo; visual medio; narrativo ALTO (define qué ve la
  jefatura).
- **Riesgo de falsa precisión:** máximo en a) (promover geometrías experimentales a
  oficiales).
- **Recomendación técnica (no vinculante):** b) — complementar: Fase 25 como lectura
  general vigente y pipeline híbrido como detalle territorial experimental, rotulado
  como tal; revisar la relación recién cuando Belgrano y Puerto Madero tengan
  repetición aprobada.
- **Decisión preliminar sugerida:** b).
- **Quién decide:** Diego + equipo DGDGAS.
- **Bloquea:** informe nuevo (su arquitectura depende de esto).
- **Prioridad:** ALTA.

## DH-09 — Todas: puntos fuera de representación

- **Zona:** todas.
- **Pregunta:** ¿cómo se clasifican y comunican los puntos que quedan fuera de núcleos,
  corredores y frentes? (San Telmo 143; Corrientes 880; Belgrano ~547; Puerto Madero
  192; Costanera n/a.)
- **Por qué no puede resolverla el algoritmo:** "fuera de la representación" mezcla
  categorías que solo se separan con criterio humano y, en parte, con revisión caso a
  caso. Llamar "ruido" a todo lo no asignado sería falso: en Corrientes el 70 % del
  universo queda fuera del corredor y es mayormente oferta real a más de 1–2 cuadras
  del eje.
- **Taxonomía propuesta (a validar):**
  1. Ruido técnico (geocodificación dudosa, duplicados residuales).
  2. Contexto gastronómico disperso (oferta real fuera de la estructura).
  3. Continuidad territorial (puntos que "pegan" la estructura a la trama; p. ej.
     entre componentes del eje).
  4. Cola de revisión (candidatos a incorporación tras revisión humana).
  5. Dependencia del contenedor (puntos cortados por el borde; anillos externos ya
     almacenados: Belgrano 131 F01/F02 + 157 Places; Puerto Madero 42 + 46).
  6. Establecimientos aislados genuinos.
- **Opciones reales:** a) adoptar la taxonomía y mostrar categorías 2–3 como capa de
  contexto en mapas de detalle; b) mostrar solo la estructura y documentar el resto en
  anexo; c) caso por caso por zona.
- **Evidencia:** los anillos externos y las cifras de cobertura (arriba) están
  medidos; la clasificación 1 vs. 4 requiere el etiquetado de DH-11.
- **Impactos:** metodológico alto (define qué significa "cobertura"); visual alto;
  narrativo alto (evita que "polo" se lea como "todo lo demás no cuenta").
- **Riesgo de falsa precisión:** alto si se omiten los no asignados (la estructura
  parecería exhaustiva); medio si se muestran sin jerarquía visual clara.
- **Recomendación técnica (no vinculante):** a) — adoptar la taxonomía de 6 categorías;
  regla mínima: ningún mapa de detalle sin capa de contexto o nota de cobertura
  explícita ("la estructura representa X % de la evidencia").
- **Decisión preliminar sugerida:** a).
- **Quién decide:** Diego (taxonomía y regla); equipo DGDGAS (aplicación por zona).
- **Bloquea:** informe nuevo; interactúa con DH-02 d) y DH-06 e).
- **Prioridad:** ALTA.

## DH-10 — Todas: mapa principal del eventual informe

- **Zona:** todas.
- **Pregunta:** ¿qué versión ocupa el mapa principal del próximo informe: lectura
  general tipo Fase 25, síntesis de estructuras híbridas maduras, u otra?
- **Por qué no puede resolverla el algoritmo:** es la decisión editorial central del
  producto.
- **Opciones reales:** a) lectura general (Fase 25 o su heredera) como mapa principal y
  estructuras híbridas como láminas de detalle; b) mapa principal nuevo con las
  estructuras maduras (San Telmo, Corrientes) y las demás zonas en lectura general;
  c) posponer el informe hasta que las cinco zonas piloto estén decididas.
- **Evidencia:** dependencias duras: DH-01, DH-02, DH-08; repeticiones de Belgrano y
  Puerto Madero pendientes; el plan de escalado del experimento ya lista qué bloquea el
  informe.
- **Impactos:** narrativo máximo; visual máximo.
- **Riesgo de falsa precisión:** medio en b) (mezcla de madureces distintas en una
  lámina) — mitigable con rotulado.
- **Recomendación técnica (no vinculante):** a) por ahora; reevaluar b) cuando DH-01 y
  DH-02 estén firmadas y las repeticiones corridas.
- **Decisión preliminar sugerida:** a).
- **Quién decide:** Diego + equipo DGDGAS.
- **Bloquea:** informe nuevo.
- **Prioridad:** MEDIA (se activa al planificar el informe).

## DH-11 — Todas: etiquetado humano de la deduplicación

- **Zona:** todas.
- **Pregunta:** ¿quién etiqueta la muestra estratificada de 200 casos de deduplicación
  (`interno_revision_deduplicacion/`, fuera de Git) y con qué criterio de corte?
- **Por qué no puede resolverla el algoritmo:** la muestra actual es clasificación
  automática; sin verdad manual no se puede calcular precisión/recall del apareo
  F01/F02↔Places, y ese número condiciona cuánta confianza darle a las mezclas de
  fuentes reportadas.
- **Opciones reales:** a) etiquetado interno (Diego/equipo) de los 200 casos con guía
  (`GUIA_REVISION_DEDUPLICACION.md`); b) muestreo menor (~50) para una cota rápida;
  c) posponer.
- **Evidencia:** el QA del experimento lo lista como bloqueante del informe; los
  porcentajes de Places por representación (39,6–61,8 %) heredan el error de apareo,
  hoy no cuantificado.
- **Impactos:** metodológico alto (calibra todas las mezclas de fuentes); narrativo
  bajo directo.
- **Riesgo de falsa precisión:** reportar mezclas con dos decimales sin cota de error
  de apareo.
- **Recomendación técnica (no vinculante):** b) primero (cota rápida con 50 casos),
  a) completo antes del informe.
- **Decisión preliminar sugerida:** b) → a).
- **Quién decide:** Diego (asignación de tiempo propio o del equipo).
- **Bloquea:** informe nuevo (no bloquea repeticiones).
- **Prioridad:** MEDIA.

## DH-12 — Corredores y frentes: estatus del ancho de buffer

- **Zona:** Corrientes, Puerto Madero y futuros corredores/frentes.
- **Pregunta:** ¿el buffer (60/90/120 m; 180 m en frentes) se declara convención de
  representación o se presenta como medición?
- **Por qué no puede resolverla el algoritmo:** los anchos derivan de terciles de
  densidad y de un umbral de asignación elegido; son razonables pero convencionales.
- **Opciones reales:** a) declararlos convención cartográfica explícita (nota en cada
  mapa); b) calibrarlos con un estudio ad hoc; c) no declarar nada.
- **Evidencia:** el QA del experimento ya los describe como orientativos; b) no tiene
  hoy fuente de calibración disponible.
- **Impactos:** metodológico bajo; visual bajo; narrativo bajo pero de higiene.
- **Riesgo de falsa precisión:** c) lo maximiza; a) lo elimina casi sin costo.
- **Recomendación técnica (no vinculante):** a).
- **Decisión preliminar sugerida:** a).
- **Quién decide:** equipo DGDGAS (redacción de la nota estándar).
- **Bloquea:** nada.
- **Prioridad:** BAJA.

---

## Resumen: qué ya tiene recomendación sólida y qué necesita pruebas

**Con evidencia suficiente para decidir ya (solo falta la firma humana):**
DH-02 (b), DH-03 (a), DH-04 (a), DH-07 (a), DH-08 (b), DH-09 (a), DH-12 (a).

**Necesitan prueba técnica local previa (sin datos nuevos, sin API):**
DH-01 (soporte del eje Defensa), DH-06 (repetición Puerto Madero), DH-05 (repetición
Belgrano), DH-11 (etiquetado humano).

**Se activan después:** DH-10 (al planificar el informe).
