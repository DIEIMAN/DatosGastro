# DataGastro V2 — Fuentes documentales y Perplexity / búsqueda asistida

> **Plan, no ejecución.** Diseño de cómo se usarían las fuentes documentales web y los
> asistentes de búsqueda (Perplexity y similares). **Regla central:** son **localizadores** de
> fuentes documentales, **no** fuente final.

## 1. Para qué sirven (y para qué no)

**Sirven para:**
- localizar **fuentes documentales** (notas, sitios oficiales, archivos);
- encontrar **casos históricos** y **rubros emblemáticos** del ecosistema porteño;
- detectar **notas periodísticas** que sostienen una trayectoria;
- encontrar **sitios oficiales** de comercios, cámaras, asociaciones;
- enriquecer **fichas por rubro** y la capa `historico_emblematico`.

**No sirven para:**
- ser **fuente final** de existencia o de una métrica;
- afirmar que un local existe/está activo sin una URL verificable;
- generar listados "de memoria" del modelo (riesgo de alucinación).

## 2. Regla anti-alucinación (obligatoria)

```text
Toda afirmación derivada de Perplexity/búsqueda asistida DEBE quedar respaldada por una
referencia documental verificable. Sin URL comprobable, NO entra al padrón:
queda como "pista a verificar", nunca como dato.
```

Esto implementa el guardrail "no inventar datos/URLs/IDs/métricas".

## 3. Flujo de trabajo documental

```text
1. Pregunta acotada     ej.: "casas de pastas históricas de Boedo con cobertura periodística"
2. Localización         Perplexity/web devuelven candidatos de FUENTES (no de datos finales)
3. Verificación         se abre cada fuente; se confirma que existe y dice lo que se afirma
4. Registro             se anota la referencia con el esquema del §4
5. Vinculación          la referencia se asocia a una entidad o a un caso emblemático
6. Confianza            sostiene niveles C2 (documental) / sube C1 a C2-C3 (ver doc 03)
```

## 4. Esquema de registro de referencias

Cada referencia documental se guarda con:

```text
id_referencia
titulo
medio                 (diario, sitio oficial, revista, archivo)
url
fecha_publicacion     (o "s/f" si no consta)
fecha_consulta
autor                 (si consta)
afirmacion_sostenida  (qué afirma exactamente, en una frase)
entidad_o_caso        (a qué establecimiento/caso se asocia)
tipo_fuente           (prensa | oficial | institucional | blog | archivo)
confiabilidad         (alta | media | baja, con criterio)
cita_textual          (opcional, breve)
```

Estas referencias alimentan `fact_trayectoria_documental` del modelo de datos (doc 08).

## 5. Jerarquía de confiabilidad documental

```text
alta    sitio oficial GCBA/organismo, registro oficial, medio de referencia con autoría/fecha
media   prensa general, revista especializada, nota sin autoría clara
baja    blog, foro, red social (sólo como pista, nunca como prueba única)
```

Una entidad como **caso emblemático** requiere **≥2 referencias independientes** de
confiabilidad media o superior (regla del criterio de validación de la taxonomía).

## 6. Casos históricos y rubros emblemáticos

- Objetivo: que V2 no sea sólo "lo que Google ve hoy", sino que incorpore **memoria barrial**:
  bodegones, confiterías y casas de pastas tradicionales, bares notables, pizzerías históricas.
- Estos casos suelen estar **sub-representados** en señales operativas y **bien documentados**
  en prensa/archivo: ahí la capa documental aporta más valor.
- Se cruzan con BA Data (Bares Notables) cuando exista ancla oficial.

## 7. Privacidad

- Las referencias documentales son públicas; aun así, **no** se extraen ni publican datos
  personales (teléfonos, emails, nombres de personas físicas) que pudieran aparecer en las
  notas. Sólo nombre comercial, rubro, barrio y trayectoria.

## 8. Límites a declarar

- Cobertura documental **sesgada** hacia lo notable/turístico y lo céntrico.
- Antigüedad variable: una nota de hace años no prueba existencia actual.
- Por eso la capa documental **contextualiza y prioriza**, pero la existencia/actividad actual
  la confirma la validación territorial posterior (I02).
