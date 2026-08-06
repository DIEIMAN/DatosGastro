# Auditoría de reglas y skills · qué falta y qué está roto

**6 de agosto de 2026** · Lectura completa de `AGENTS.md`, `CLAUDE.md`, `agent_skills/`, la
política V1.1, el ciclo operativo y las skills V1.

---

## El resultado en una línea

La infraestructura de **privacidad y seguridad está bien cubierta**. La de **método
experimental casi no existe**: de las nueve prácticas que hicieron funcionar la etapa de esta
semana, **seis no están escritas en ninguna parte**.

Dicho de otro modo: el método bueno de este proyecto vive en las conversaciones, no en el
repositorio. Si mañana entra otra persona u otro agente, no lo hereda.

---

## 1 · Lo que sí está, y está bien

Cinco capas con precedencia declarada, nueve guardrails de Prioridad 0, un registro de 35
superficies protegidas, y un ciclo operativo con estados canónicos —`PREPARACIÓN → LISTO PARA
AUTORIZACIÓN → EJECUCIÓN → REVISIÓN → CORRECCIÓN → DECISIÓN → CERRADO`— movidos sólo por gates
verificables.

Tres reglas particularmente buenas y que conviene no perder:

- **El QA del productor no cuenta como auditoría.** Prohibida la auto-aprobación.
- **La regla de dos errores**: a la tercera falla se reconstruye desde el último input congelado.
- **Verificar contra el disco**: distinguir «verificado directamente» de «según el reporte de X»,
  y ante insumo dudoso parar y reportar la ruta exacta. Es la regla que evitó el desastre cuando
  la documentación decía una cosa y el disco otra.

Y nueve skills vivas con paridad verificada en tres espejos.

## 2 · Los seis huecos

| práctica | estado | consecuencia |
|---|---|---|
| Declarar la lectura del resultado **antes** de correr | **no existe** | el veredicto se elige después de ver el número |
| **Control aleatorio** en toda ablación | **no existe** | tres de cinco filas se leyeron al revés hasta agregarlo |
| Prohibir **mover un umbral** para rescatar un caso | **no existe** | el mapa confirma lo que ya creíamos |
| **Curva de sensibilidad** obligatoria ante parámetro elegido a mano | **no existe** | la elección del parámetro es la mitad del resultado, sin decirlo |
| **Número estimado de llamadas** antes de pedir autorización | parcial | la autorización existe, el número no |
| **Licencia y redistribución** por fuente | parcial | hay procedencia, no hay derechos: la base no sabe qué puede publicar |

Y uno más, de redacción, que es el que más rápido se rompe:

- **«No encontramos» contra «no existe»** — existe la taxonomía, no existe la prohibición del
  salto. Y la política V1.1 **eliminó** la sección de la V1 donde vivía «preferir no encontrado /
  no verificable». Es una regresión normativa, no un olvido.

## 3 · Seis cosas rotas o desactualizadas

1. **`agent_skills/README.md` dice que `.agents/` no tiene contenido útil**, y el mismo archivo
   dos líneas después lista sus nueve réplicas. `.codex/` sí está vacío.
2. **Las skills V1 citan secciones de la política V1**, pero `AGENTS.md` las manda usar bajo la
   V1.1, cuya numeración cambió. Las referencias cruzadas apuntan a secciones equivocadas:
   V1 §6 Trazabilidad es V1.1 §8; V1 §8 QA es V1.1 §10.
3. **`docs/infraestructura_agentes_skills_v1_1/skills/` está vacío**, aunque el reporte de
   paridad lo declara como una capa.
4. **La evaluación de julio quedó vieja**: anticipaba ausencias que el reporte de paridad de tres
   días después desmiente.
5. **Dos taxonomías de roles sin mapeo entre sí**: el ciclo operativo reparte por herramienta
   (Codex, Claude, Grok, Diego) y el catálogo define cuatro agentes funcionales. Ningún documento
   dice qué agente funcional corre en qué herramienta.
6. **Tres agentes definidos y nunca activados**, entre ellos el `auditor_metodologico` — que es
   justamente el rol al que el catálogo le asigna la responsabilidad de las sensibilidades y las
   ablaciones. La responsabilidad existe; el rol no corre.

## 4 · Lo que propongo

**Una skill nueva: `datagastro-metodo-experimental`.** Está escrita y va adjunta. Cubre los seis
huecos con **ocho reglas** —R8 se sumó el 2026-08-06, después de que un campo leído con la clave
equivocada costara 37 requests—, y cada regla lleva el caso concreto de este proyecto que la
originó, que es lo que hace que se recuerden. Cierra con **siete preguntas** de control antes de
reportar cualquier resultado.

No reemplaza a `datagastro-guardrails`: ésa dice **qué no hacer**, ésta dice **cómo hacer**.

**Cuatro arreglos chicos**, por orden de costo:

1. Corregir las referencias cruzadas de las skills V1 a la numeración V1.1. Es mecánico y hoy
   manda a leer secciones equivocadas.
2. Restituir en la V1.1 la sección de incertidumbre que se perdió de la V1, y sumarle la
   prohibición del salto de «no encontramos» a «no existe».
3. Arreglar la contradicción del README de `agent_skills/` y borrar o poblar la carpeta vacía.
4. Escribir el mapeo entre las dos taxonomías de roles, o abandonar una. Dos vocabularios para lo
   mismo es cómo se pierde una regla.

**Y una decisión que no es mía:** el `auditor_metodologico` está definido y nunca se activó. En
esta etapa ese rol lo vengo haciendo yo desde afuera del repositorio. Conviene decidir si se
activa adentro o si se declara que vive afuera — hoy figura como pendiente y no lo es.

---

## 5 · Lo que no tocaría

La capa de privacidad y superficies protegidas está bien y es la que más caro sale romper. Los
nueve guardrails de Prioridad 0 tampoco: son cortos, memorables y se cumplen.

El problema no es que sobre regulación. Es que **la parte del método que produce resultados
defendibles nunca se escribió**, porque se fue inventando sobre la marcha — y funcionó, pero sólo
mientras estuviéramos nosotros acá.
