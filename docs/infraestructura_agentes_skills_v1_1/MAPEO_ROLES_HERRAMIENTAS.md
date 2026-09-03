# Mapeo de roles · quién es qué

**Por qué existe.** Hoy conviven dos vocabularios de roles sin traducción entre sí:

- `CICLO_OPERATIVO_UNA_PASADA.md` reparte por **herramienta**: Codex, Claude/Fable, Grok,
  ChatGPT, Diego.
- `CATALOGO_AGENTES_SKILLS.json` define cuatro **agentes funcionales**: `investigador_documental`,
  `cartografo_territorial`, `integrador_tecnico_editorial`, `auditor_qa`.

Ningún documento decía qué agente funcional corre en qué herramienta. Dos vocabularios para lo
mismo es cómo se pierde una regla.

---

## El mapeo

| agente funcional | dónde corre hoy | qué hace en la práctica |
|---|---|---|
| `integrador_tecnico_editorial` | **Claude Code, adentro del repositorio** | escribe y corre código, genera productos, produce QA, mantiene los generadores y los sellados |
| `investigador_documental` | **Claude en Cowork, afuera del repositorio** | busca fuentes en la web, verifica URL y licencias, lee el repositorio para reconstruir método |
| `auditor_qa` / `auditor_metodologico` | **Claude en Cowork, afuera del repositorio** | revisa lo que produce el integrador antes de que se adopte; escribe las bandas de lectura y los criterios antes de correr |
| `cartografo_territorial` | **Claude Code**, con criterios acordados afuera | clustering, envolventes, particiones y uniones |
| decisión humana | **Diego** | autoriza presupuesto, adopta o rechaza, define alcance y decide lo institucional |

---

## Las dos reglas que se desprenden, y son las que importan

**1 · El auditor no corre en la misma herramienta que el productor.**

La política ya prohíbe la auto-aprobación —el QA del productor es parte de la producción y no
cuenta como auditoría—. Lo que faltaba decir es **cómo se cumple en la práctica**: hoy se cumple
porque el que produce está adentro del repositorio y el que audita está afuera, y no comparten
contexto ni archivos de trabajo.

Esa separación no es un accidente de infraestructura: es el mecanismo. Si algún día las dos
tareas corren en la misma sesión, la auditoría deja de ser independiente aunque el prompt diga
que lo es.

**2 · La red y el disco están repartidos, y conviene saberlo antes de asignar una tarea.**

| capacidad | adentro del repo | afuera, en Cowork |
|---|---|---|
| correr código sobre los datos | **sí** | no |
| leer y escribir archivos del repositorio | **sí** | lectura, y escritura por puente |
| llamar APIs pagas | **sí**, con autorización | no |
| buscar en la web y verificar fuentes | no | **sí** |
| leer PDF y documentos externos | limitado | **sí** |

Regla práctica: **lo que necesita datos va adentro; lo que necesita red o criterio va afuera.**
Pedirle a una sesión algo que su lado no puede hacer es la causa más común de una vuelta perdida.

---

## El `auditor_metodologico`

Está definido en el catálogo y figura como **no activado**. En la práctica ese rol se viene
ejerciendo desde afuera del repositorio, sin estar declarado.

Queda **pendiente de decisión de Diego**: se activa adentro como agente propio, o se declara
formalmente que vive afuera y se le asigna el alcance que hoy ya tiene —escribir las bandas de
lectura antes de correr, exigir controles aleatorios y curvas de sensibilidad, y revisar la
redacción de los resultados negativos—.

Mientras no se decida, el rol existe y no figura, que es la peor de las dos opciones.
