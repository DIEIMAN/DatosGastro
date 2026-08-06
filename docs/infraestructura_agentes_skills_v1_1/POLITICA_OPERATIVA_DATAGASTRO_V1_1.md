# Política operativa DataGastro / DGDGAS — V1.1

**ID:** `POLITICA_OPERATIVA_DATAGASTRO`  
**Versión:** 1.1  
**Fecha:** 2026-07-11  
**Precedencia de este documento:** ver §0 (no reordenar ad hoc en prompts).

Referenciar: *“Aplicar `POLITICA_OPERATIVA_DATAGASTRO` v1.1”*.  
El detalle de procedimientos vive en skills; los guardrails largos en `docs/skills_claude/`.

---

## 0. Precedencia (orden fijo)

1. **Guardrails y seguridad** (`docs/skills_claude/01_datagastro_guardrails.md` y equivalentes).  
2. **Autorización humana explícita** para excepciones *permitidas* (commit, push, API autorizada, promoción, escritura en Drive, tocar pipeline).  
   - La autorización **no** habilita inventar datos ni vulnerar privacidad.  
3. **Esta política operativa** (V1.1).  
4. **Definición del agente** (rol, rutas, prohibiciones).  
5. **Skill** invocada.  
6. **Tarea puntual** / prompt de sesión.

Ante conflicto: gana el nivel más alto de la lista.

---

## 1. Protección de datos

1. No inventar datos, métricas, URLs, fuentes, fechas ni resultados.  
2. No modificar datos fuente (CSV/XLSX/PDF originales, crudos).  
3. No exponer ni versionar secretos (`.env`, API keys, credenciales).  
4. No scrapear ni llamar APIs de plataformas privadas sin autorización explícita y presupuesto.  
5. No ejecutar Google Places ni descargas no autorizadas.

---

## 2. Superficies protegidas (genérico)

1. Toda superficie **cerrada, oficial, baseline o de solo lectura** se declara en un **registro por subproyecto** (YAML), no en el núcleo de esta política con nombres de fase sueltos.  
2. Registro tipico: `docs/<subproyecto>/PROTECTED_SURFACES.yaml` (ver plantilla en `docs/infraestructura_agentes_skills_v1_1/registros/PROTECTED_SURFACES_TEMPLATE.yaml`).  
3. Campos mínimos: `ruta_o_patron`, `tipo`, `motivo`, `nivel_proteccion`, `puede_leer`, `puede_copiar`, `puede_modificar`, `requiere_autorizacion`, `hash_opcional`, `responsable`.  
4. Niveles sugeridos: `fuente` | `pipeline` | `baseline_cerrada` | `entregable_oficial` | `experimental_cerrado` | `interno_sensible`.  
5. Regla operativa:  
   - `puede_modificar: false` → no editar in-place; abrir **línea paralela**.  
   - Si `requiere_autorizacion: true` → solo con pedido explícito de Diego (o responsable).  
6. Pipeline público F01–F05 y `src/build_*`, `data/processed`, `data/analytics`, `dashboard/`, `notebooks/` requieren permiso para modificar.

---

## 3. Líneas experimentales

1. Etiquetar **EXPERIMENTAL / NO OFICIAL** hasta decisión humana.  
2. Estructura: `docs/.../<paquete>/`, `outputs/.../<paquete>/`, `scripts/.../<paquete>/`.  
3. Separar capa **analítica** y de **presentación**.  
4. Geometrías/buffers/clusters no son límites institucionales salvo decisión firmada.

---

## 4. Git

1. No `git add .`.  
2. No staging masivo de outputs/secretos/crudos.  
3. No commit ni push sin autorización humana explícita (§0.2).  
4. Reportar archivos creados/modificados y si se tocaron fuentes.

---

## 5. Privacidad

1. Publicables = agregados y redacción prudente.  
2. Prohibido en publicables: emails, teléfonos, CUIT/DNI, nombres no institucionales, `place_id`, montos individuales, links privados Drive/Docs, API keys.  
3. Escaneo automático no reemplaza revisión humana.  
4. Crudos → rutas ignoradas por Git.

---

## 6. Google Drive

| Acción | Regla |
| --- | --- |
| Lectura / hashear / copiar *desde* Drive *hacia* local | Permitida |
| Borrar en Drive | **Prohibido** (no borrar directamente en Drive) |
| Escribir / crear / renombrar / mover en Drive | Solo con **autorización humana explícita** |
| Limpiar copias internas locales no fuente ni pipeline | Permitido con plan de limpieza + confirmación si es destructivo |
| Alterar fuentes públicas originales (locales o en Drive) | **Prohibido** |

Rutas típicas de solo lectura por defecto: `G:\My Drive`, `G:\.shortcut-targets-by-id`.

---

## 7. Rutas (portabilidad)

| Contexto | Convención |
| --- | --- |
| Manifests y metadata | Rutas **relativas al repositorio** |
| Handoffs | Relativas canónicas; absoluta **opcional** |
| Respuestas de sesión al usuario | Absoluta local permitida |
| Interior de ZIP de revisión | **Nunca** rutas absolutas de máquina |

---

## 8. Trazabilidad y manifests

1. Cierre de paquete con:  
   - `MANIFEST_CONTENIDO.csv` — todos los archivos del pack **excepto** el propio manifest;  
   - `CHECKSUMS_SHA256.txt` — hashes de manifest, metadata, ZIP y (si aplica) QA_FINAL;  
   - `metadata_*.json`.  
2. **Prohibida** la autorreferencia del manifest a sí mismo dentro de `MANIFEST_CONTENIDO.csv`.  
3. Insumos críticos y superficies del registro: hash pre/post cuando el paquete lo exija.  
4. Cada cifra: fuente, universo, fecha de corte.

---

## 9. Fuentes

1. Universos F / I / E no se suman como total único.  
2. Sustantivo = lo que mide la fuente.  
3. No “locales activos” sin base.  
4. Fuentes privadas u off-pipeline: declararlas.

---

## 10. QA

1. PDF: render + revisión página por página.  
2. `kpis_lock` → `scripts/qa/validate_kpis.py` cuando exista.  
3. Cierre: política + manifest correcto + privacidad + ZIP + `QA_FINAL`.  
4. El productor **no** aprueba en definitivo su entregable.

---

## 11. Decisiones humanas

1. Separar: **evidencia** | **inferencia técnica** | **decisión institucional**.  
2. Firmadas no se reabren por defecto.  
3. Contradicción → nota y escala; no auto-revert.  
4. Nombres e inclusión política = decisión humana.

---

## 12. Paralelo y carpetas exclusivas

1. Cada agente escribe solo en sus rutas de misión.  
2. No escribir en la carpeta de otro agente en curso.  
3. Consumir del otro solo entregables finales con QA.  
4. Usar `RUN_PLAN_MULTIAGENT.yaml` cuando haya ≥2 escritores.

---

## 13. Handoffs y entregas

1. Plantillas en el paquete de infraestructura.  
2. Marca publicable: **DGDGAS**. “DataGastro” solo docs internos.  
3. Estado del material declarado (experimental / mostrable / oficial).

---

## 14. Entorno

1. Windows: `.venv/Scripts/python.exe`.  
2. No instalar librerías sin autorización.  
3. No activar configs experimentales globales del IDE sin documentar.

---

## 15. Autorización humana (ejemplos)

Requiere pedido explícito: commit/push; modificar superficies protegidas; pipeline F01–F05; borrar/mover del repo; Places/APIs pagas; reabrir decisión firmada; promover a oficial; sobrescribir `AGENTS.md`/`CLAUDE.md`/settings/skills productivas; escritura en Drive.

---

## 16. Referencias

| Tema | Ruta |
| --- | --- |
| Guardrails | `docs/skills_claude/01_datagastro_guardrails.md` |
| Catálogo V1.1 | `docs/infraestructura_agentes_skills_v1_1/CATALOGO_AGENTES_SKILLS.json` |
| Plantilla protegidas | `docs/infraestructura_agentes_skills_v1_1/registros/PROTECTED_SURFACES_TEMPLATE.yaml` |
| Ejemplo Polos | `docs/polos_gastro/PROTECTED_SURFACES.yaml` |
| Infra V1 (histórica) | `docs/infraestructura_agentes_skills_v1/` (no sobrescribir) |
| Método experimental | `agent_skills/shared/datagastro_metodo_experimental.md` |
| Correspondencia de numeración V1 → V1.1 | `docs/infraestructura_agentes_skills_v1_1/CORRESPONDENCIA_SECCIONES_V1_V1_1.md` |
| Mapeo de roles | `docs/infraestructura_agentes_skills_v1_1/MAPEO_ROLES_HERRAMIENTAS.md` |

---

## 17. Incertidumbre y defensa de lo adoptado

> Esta sección restituye la que existía en la política V1 (§ *Incertidumbre y defensa de lo
> adoptado*) y que la V1.1 no reprodujo. Su ausencia era una regresión normativa, no una
> simplificación: es la sección donde vive la obligación de no convertir un límite del trabajo en
> una afirmación sobre el mundo.

**17.1 · Declarar la incertidumbre real.** Toda cifra publicada declara qué la limita: cobertura,
fecha de corte, método, y qué queda fuera de su universo. Una cifra sin límite declarado se lee
como más firme de lo que es.

**17.2 · Preferir «no encontrado» y «no verificable».** Cuando una búsqueda no da resultado, se
escribe que no se encontró, no que no existe. Vale para texto, tablas, mapas y títulos.

| se escribe | no se escribe |
| --- | --- |
| «con la cobertura disponible, no se identificaron X» | «no hay X» |
| «la última señal de actividad es de AAAA» | «está activo» |
| «no figura en las fuentes relevadas» | «no existe» |

**17.3 · La ausencia va con su cobertura al lado.** Si un resultado negativo puede explicarse por
cobertura floja de la fuente en esa zona o categoría, la medida de cobertura acompaña al
resultado en el mismo lugar, no en una nota al pie.

**17.4 · Defensa de lo adoptado.** Una decisión adoptada se defiende con el criterio con el que
se tomó, no con el resultado que produjo. Si el criterio no se puede reconstruir, la decisión no
está adoptada: está heredada.

**17.5 · Método experimental.** Las reglas operativas que hacen cumplible esta sección —bandas
declaradas antes de correr, control aleatorio en ablaciones, umbrales que no se mueven, curvas de
sensibilidad, presupuesto declarado antes de gastar y procedencia con licencia por fuente— están
en `agent_skills/shared/datagastro_metodo_experimental.md` y son de cumplimiento obligatorio para
cualquier corrida que produzca una cifra reportable.

---

**Fin política v1.1.**
